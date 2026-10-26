"""Read-only audit of supplied Docker/probe evidence for a planned author worker.

This never starts a container, invokes author code or grants execution authority.
Consistent supplied observations are not authenticated runtime qualification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

from .evidence import decode, keys, read_raw, sha, text

VERSION = 'weft-author-isolation-v1'
ENV_KEYS = {'PATH', 'LANG', 'LC_ALL', 'PYTHONHASHSEED', 'PYTHONUNBUFFERED',
            'PYTHONDONTWRITEBYTECODE', 'OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
            'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS', 'MPLCONFIGDIR', 'HOME'}


def plan(value):
    keys(value, {'schema_version', 'container_id', 'container_name', 'image', 'image_id',
                 'argv', 'environment', 'mounts', 'memory_bytes', 'pids', 'nano_cpus', 'tmpfs_bytes'})
    if value['schema_version'] != VERSION: raise ValueError('Unsupported isolation plan')
    sha(value['container_id'])
    if not isinstance(value['container_name'], str) or not re.fullmatch(r'weft-author-[a-z0-9-]{1,64}', value['container_name']):
        raise ValueError('Bound planned container name required')
    if not isinstance(value['image'], str) or not re.fullmatch(r'[A-Za-z0-9./_-]+@sha256:[0-9a-f]{64}', value['image']):
        raise ValueError('Digest-pinned image required')
    if not isinstance(value['image_id'], str) or not re.fullmatch(r'sha256:[0-9a-f]{64}', value['image_id']):
        raise ValueError('Pinned platform image ID required')
    if not isinstance(value['argv'], list) or not 1 <= len(value['argv']) <= 64: raise ValueError('Frozen argument vector required')
    for argument in value['argv']: text(argument)
    if not isinstance(value['environment'], list): raise ValueError('Explicit environment allowlist required')
    names = set()
    for entry in value['environment']:
        text(entry)
        name, sep, content = entry.partition('=')
        if not sep or name not in ENV_KEYS or name in names or '\n' in content:
            raise ValueError('Unapproved or duplicate environment variable')
        if name == 'HOME' and content != '/tmp': raise ValueError('Author HOME must use isolated scratch')
        names.add(name)
    keys(value['mounts'], {'/code', '/inputs', '/outputs'})
    paths = []
    for source in value['mounts'].values():
        text(source)
        path = PurePosixPath(source)
        if not path.is_absolute() or path.as_posix() != source or '..' in path.parts or source == '/':
            raise ValueError('Absolute normalized Linux staging paths required')
        if any(path == p or path.is_relative_to(p) or p.is_relative_to(path) for p in paths):
            raise ValueError('Separate code/input/output staging paths required')
        paths.append(path)
    for key in ('memory_bytes', 'pids', 'nano_cpus', 'tmpfs_bytes'):
        if type(value[key]) is not int or not 1 <= value[key] <= 2**63 - 1: raise ValueError('Explicit finite resource bound required')
    return value


def audit(expected, container, probe):
    """Audit only supplied configuration and trusted pre-author probe observations.

    The trusted worker must collect these independently of author output. This
    function cannot establish their origin or freshness and cannot release a job.
    """
    expected = plan(expected)
    issues = []
    if not isinstance(container, dict) or not isinstance(probe, dict): raise ValueError('Observation objects required')
    config = container.get('Config') or {}
    host = container.get('HostConfig') or {}
    if not isinstance(config, dict) or not isinstance(host, dict): raise ValueError('Malformed container observation')
    def require(ok, reason):
        if not ok: issues.append(reason)
    require(container.get('Id') == expected['container_id'], 'container-identity')
    require(container.get('Name') == '/' + expected['container_name'], 'container-name')
    require(container.get('Image') == expected['image_id'] and config.get('Image') == expected['image'], 'image-identity')
    require(config.get('Cmd') == expected['argv'] and config.get('Entrypoint') is None, 'command-identity')
    healthcheck = config.get('Healthcheck')
    require(healthcheck is None or (isinstance(healthcheck, dict)
            and healthcheck.get('Test') == ['NONE']), 'unreviewed-healthcheck')
    labels = config.get('Labels') or {}
    require(isinstance(labels, dict) and labels.get('weft.author') == expected['container_name'], 'job-label')
    require(config.get('User') == '65534:65534' and probe.get('uid') == 65534 and probe.get('gid') == 65534, 'nonroot-identity')
    env = config.get('Env')
    require(isinstance(env, list) and all(isinstance(x, str) for x in env) and len(env) == len(expected['environment'])
            and sorted(env) == sorted(expected['environment']), 'environment-allowlist')
    require(host.get('NetworkMode') == 'none' and probe.get('interfaces') == ['lo'], 'network-isolation')
    require(host.get('Privileged') is False and host.get('ReadonlyRootfs') is True, 'root-filesystem-or-privilege')
    require(host.get('CapDrop') == ['ALL'] and not host.get('CapAdd') and probe.get('cap_eff') == '0000000000000000', 'capability-isolation')
    security = host.get('SecurityOpt')
    require(isinstance(security, list) and all(isinstance(x, str) for x in security) and 'no-new-privileges:true' in security
            and not any('unconfined' in x for x in security) and probe.get('no_new_privileges') is True
            and probe.get('seccomp_mode') == 2, 'privilege-and-syscall-controls')
    require(host.get('PidMode') in ('', 'private') and host.get('IpcMode') == 'private'
            and host.get('UTSMode') in ('', 'private') and host.get('CgroupnsMode') == 'private', 'namespace-isolation')
    require(host.get('Devices') == [] and host.get('DeviceRequests') in (None, [])
            and not host.get('VolumesFrom') and not host.get('Links'), 'host-device-or-container-access')
    require(host.get('RestartPolicy') == {'Name': 'no', 'MaximumRetryCount': 0}, 'automatic-restart-disabled')
    require(host.get('Memory') == expected['memory_bytes'] and host.get('MemorySwap') == expected['memory_bytes']
            and probe.get('memory_max') == expected['memory_bytes'] and probe.get('swap_max') == 0, 'memory-and-swap-limit')
    require(host.get('PidsLimit') == expected['pids'] and probe.get('pids_max') == expected['pids'], 'pid-limit')
    require(host.get('NanoCpus') == expected['nano_cpus'], 'cpu-configuration')
    cpu = probe.get('cpu_max')
    require(isinstance(cpu, list) and len(cpu) == 2 and all(type(n) is int and n > 0 for n in cpu)
            and cpu[0] * 1_000_000_000 == expected['nano_cpus'] * cpu[1], 'cpu-enforcement')
    require(host.get('Tmpfs') == {'/tmp': f"rw,noexec,nosuid,nodev,size={expected['tmpfs_bytes']},mode=1777"}, 'bounded-scratch')
    mounts = container.get('Mounts')
    allowed = expected['mounts']
    actual = {}
    if isinstance(mounts, list):
        for mount in mounts:
            if not isinstance(mount, dict): issues.append('malformed-mount'); continue
            target = mount.get('Destination')
            if target not in allowed or target in actual:
                issues.append('unexpected-or-duplicate-mount'); continue
            actual[target] = mount
            require(mount.get('Source') == allowed[target] and mount.get('Type') == 'bind'
                    and mount.get('Propagation') == 'rprivate' and mount.get('RW') is (target == '/outputs'), 'mount-boundary:' + target)
    require(set(actual) == set(allowed), 'mount-inventory')
    # Behavioral probes run before author code; supplied booleans alone aren't proof.
    for key in ('code_write_denied', 'input_write_denied', 'root_write_denied',
                'output_write_succeeded', 'host_socket_absent', 'host_canary_absent'):
        require(probe.get(key) is True, 'probe:' + key)
    return {'schema_version': VERSION,
            'status': 'hold' if issues else 'supplied-controls-consistent', 'issues': sorted(set(issues)),
            'runtime_qualified': False, 'dispatch_authorized': False, 'canonical_acceptance': False,
            'observations_authenticated': False,
            'remaining_live_evidence': ['Current supported runtime identity and enforced policy',
                'Trusted before-author observation provenance and fresh job bindings',
                'Bounded output-volume quota with exhaustion test',
                'Watchdog deadline surviving coordinator disconnect',
                'Cancellation and descendant termination observed outside author process',
                'Immutable output recovery and independent expected-hash verification']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('plan', 'inspect', 'probe'): parser.add_argument('--' + name, required=True, type=Path)
    parser.add_argument('--expected-plan-sha256', required=True)
    args = parser.parse_args(argv)
    try:
        sha(args.expected_plan_sha256)
        raw = {key: read_raw(getattr(args, key)) for key in ('plan', 'inspect', 'probe')}
        hashes = {key: hashlib.sha256(value).hexdigest() for key, value in raw.items()}
        if hashes['plan'] != args.expected_plan_sha256: raise ValueError('Separately retained plan hash mismatch')
        result = audit(*(decode(raw[key]) for key in ('plan', 'inspect', 'probe')))
        result['source_sha256'] = hashes
    except (ValueError, TypeError, KeyError, OSError):
        # Never echo unexpected environment values or Docker content into logs.
        print(json.dumps({'status': 'hold', 'error': 'Invalid or mismatched isolation evidence'}))
        return 1
    print(json.dumps(result, indent=2))
    return 2 if result['status'] == 'hold' else 0


if __name__ == '__main__':
    raise SystemExit(main())
