"""Offline bridge from scientific packages to a proposed isolated worker.

No daemon, subprocess, network, ledger mutation or author-code execution. This
prepares/revalidates a private transport inventory; it never grants dispatch.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath

from . import evidence as ev, science_adapter as adapter, author_isolation as isolation
from .workflow import _exclusive

VERSION = 'weft-author-worker-preparation-v1'


def implementation():
    return {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest()
            for name in ('author_worker.py', 'author_isolation.py')}


def _inventory(refs, destination):
    result, names = [], []
    for ref in refs:
        ev.relative(ref['path'])
        path = PurePosixPath(ref['path'].casefold())
        if any(path == other or path.is_relative_to(other) or other.is_relative_to(path)
               for other in names):
            raise ValueError('Worker file destinations collide')
        names.append(path)
        result.append({'file': ref, 'destination': destination + '/' + ref['path']})
    return sorted(result, key=lambda item: item['destination'])


def _build(workspace, package_ref, request):
    pkg, contract, _ = adapter.load_package(workspace, package_ref)
    ev.keys(request, {'image', 'image_id', 'argv', 'environment', 'pids',
                      'nano_cpus', 'tmpfs_bytes', 'output_bytes'})
    # Validate shared isolation fields without claiming a real container exists.
    isolation.plan({'schema_version': isolation.VERSION, 'container_id': '0' * 64,
                    'container_name': 'weft-author-validation-only',
                    'mounts': {x: '/validation' + x for x in ('/code', '/inputs', '/outputs')},
                    'memory_bytes': contract['limits']['memory_bytes'],
                    **{key: value for key, value in request.items() if key != 'output_bytes'}})
    if (type(request['output_bytes']) is not int or request['output_bytes'] < 1
            or request['output_bytes'] + request['tmpfs_bytes'] > contract['limits']['disk_bytes']):
        raise ValueError('Output plus scratch quota must fit the frozen disk budget')
    if request['tmpfs_bytes'] >= contract['limits']['memory_bytes']:
        raise ValueError('Scratch must leave memory for the author process')
    data = workspace.bound_record(contract['feasibility'], 'data-feasibility', case=contract)
    code = _inventory(contract['code_files'], '/code')
    inputs = _inventory([item['file'] for item in data['files']], '/inputs')
    staged_bytes = sum(item['file']['bytes'] for item in (*code, *inputs))
    if staged_bytes + request['output_bytes'] + request['tmpfs_bytes'] > contract['limits']['disk_bytes']:
        raise ValueError('Frozen staging plus proposed output/scratch exceeds disk budget')
    if not any(item['destination'] in request['argv'] for item in code):
        raise ValueError('Command must explicitly reference a frozen code file')
    return {'schema_version': VERSION, 'kind': 'prepared-author-worker',
            'workspace_id': workspace.binding['workspace_id'], 'package': package_ref,
            'request': request, 'implementation': implementation(), 'exposure': pkg['exposure'],
            'staging': {'code': code, 'inputs': inputs},
            'outputs': contract['outputs'], 'limits': contract['limits'],
            'required_live_controls': ['current-runtime-and-policy-provenance',
                'authenticated-shared-ledger-attempt', 'verified-readonly-staging',
                'kernel-output-quota', 'independent-watchdog-before-author-start',
                'preauthor-isolation-observation', 'termination-and-private-output-recovery'],
            'runtime_qualified': False, 'author_code_executed': False, **ev.FLAGS}


def prepare(workspace, package_ref, request):
    """Save a content-addressed proposal; no file upload, staging copy or lease."""
    adapter._writable(workspace)
    with _exclusive(workspace):
        obj = _build(workspace, package_ref, request)
        raw = ev.encoded(obj)
        ref = adapter._save(workspace, 'worker-preparations/' + hashlib.sha256(raw).hexdigest() + '.json', raw)
    return {'status': 'prepared-live-dispatch-held', 'preparation': ref,
            'runtime_qualified': False, **ev.FLAGS}


def load_preparation(workspace, ref):
    obj = workspace.file(ref, parse=True)
    if (ref['root'] != 'workspace'
            or ref['path'] != 'worker-preparations/' + ref['sha256'] + '.json'):
        raise ValueError('Worker preparation must use its content address')
    if obj != _build(workspace, obj['package'], obj['request']):
        raise ValueError('Worker preparation, controls or implementation drift')
    return obj


def observation_plan(workspace, ref, assignment):
    """Bind supplied worker identities for offline comparison, not admission.

    The future trusted dispatcher must authenticate these against the shared
    ledger and actual daemon. Caller-supplied identities do not prove ownership.
    """
    obj = load_preparation(workspace, ref)
    ev.keys(assignment, {'job_id', 'attempt_id', 'container_id', 'staging_root'})
    ev.sha(assignment['job_id']); ev.sha(assignment['container_id'])
    if type(assignment['attempt_id']) is not int or not 1 <= assignment['attempt_id'] <= 2**63 - 1:
        raise ValueError('Positive bounded attempt ID required')
    root = PurePosixPath(assignment['staging_root'])
    if (not root.is_absolute() or root.as_posix() != assignment['staging_root']
            or '..' in root.parts or root == PurePosixPath('/')):
        raise ValueError('Separate normalized Linux staging root required')
    identity = hashlib.sha256(ev.encoded({'preparation': ref,
        'assignment': {key: value for key, value in assignment.items() if key != 'container_id'}})).hexdigest()
    return isolation.plan({'schema_version': isolation.VERSION,
        'container_id': assignment['container_id'], 'container_name': 'weft-author-' + identity,
        'mounts': {target: str(root / identity / target[1:]) for target in ('/code', '/inputs', '/outputs')},
        'memory_bytes': obj['limits']['memory_bytes'],
        **{key: value for key, value in obj['request'].items() if key != 'output_bytes'}})


def inspect_supplied(workspace, ref, assignment, container, probe):
    result = isolation.audit(observation_plan(workspace, ref, assignment), container, probe)
    return {**result, 'preparation': ref, 'assignment_authenticated': False,
            'output_quota_verified': False, 'watchdog_verified': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--package-reference', required=True)
    parser.add_argument('--request', required=True)
    args = parser.parse_args(argv)
    try:
        result = prepare(ev.Workspace(args.root),
                         ev.decode(ev.read_raw(Path(args.package_reference))),
                         ev.decode(ev.read_raw(Path(args.request))))
        print(json.dumps(result, sort_keys=True))
        return 0
    except (ValueError, OSError, KeyError, TypeError):
        # Do not echo request values; malformed requests may contain credentials.
        print(json.dumps({'status': 'invalid-worker-preparation', **ev.FLAGS}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
