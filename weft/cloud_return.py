"""Offline return-evidence consistency, never provider authentication or dispatch.

The contract and manifest hashes must be retained separately by the operator.
Observation fields are attestations; matching them does not qualify a runtime.
Existing journals, including inactive restore copies, are opened read-only.
"""
from collections import Counter
import hashlib
import json
import os
from pathlib import Path

from . import evaluation as e, launches
from .materials import _local_file
from .review_materials import portable
from .qualification import MAX_ARTIFACT, MAX_TOTAL

FLAGS = {**launches.FLAGS, 'provider_authenticated': False, 'runtime_qualified': False,
         'remote_continuity_qualified': False, 'resubmission_allowed': False,
         'resume_performed': False, 'journal_modified': False}
BINDINGS = ('source_revision', 'prompt_sha256', 'environment_sha256',
            'policy_sha256', 'account_scope_sha256')


def _root(path):
    path = Path(path).absolute()
    if any(p.is_symlink() or p.is_junction() for p in [path, *path.parents]):
        raise ValueError('Return evidence cannot traverse links or junctions')
    return path.resolve(strict=True)


def _json(path, expected=None):
    path = _root(path)
    if not path.is_file() or path.stat().st_size > 1_000_000:
        raise ValueError('Regular evidence JSON below 1 MB required')
    with path.open('rb') as handle:
        body = handle.read(1_000_001)
    if len(body) > 1_000_000:
        raise ValueError('Evidence JSON exceeds 1 MB')
    if expected is not None:
        e._sha(expected, 'separately retained hash')
        if hashlib.sha256(body).hexdigest() != expected:
            raise ValueError('Evidence differs from separately retained hash')
    value = json.loads(body)
    e.fingerprint(value)
    return value


def _version(value, fields, kind, where):
    e._keys(value, {'schema_version', 'kind'} | set(fields), where)
    if type(value['schema_version']) is not int or value['schema_version'] != 1 or value['kind'] != kind:
        raise ValueError('Unsupported ' + where)


def _files(root, manifest):
    files = manifest['files']
    if not isinstance(files, dict) or not 3 <= len(files) <= 64:
        raise ValueError('Three to 64 return files required')
    paths, total = {}, 0
    for name, entry in files.items():
        portable(name, paths)
        e._keys(entry, {'sha256', 'bytes'}, 'returned file')
        e._sha(entry['sha256'], 'returned file hash')
        size = entry['bytes']
        if type(size) is not int or not 0 <= size <= MAX_ARTIFACT:
            raise ValueError('Returned file exceeds bounded size')
        total += size
        if total > MAX_TOTAL:
            raise ValueError('Return files exceed total size limit')
        path = _local_file(root, name)
        if path.stat().st_size != size:
            raise ValueError('Returned file size changed: ' + name)
        with path.open('rb') as handle:
            body = handle.read(size + 1)
            if len(body) != size or hashlib.sha256(body).hexdigest() != entry['sha256']:
                raise ValueError('Returned file hash changed: ' + name)
    selected = [manifest[k] for k in ('observation_path', 'test_report_path', 'log_path')]
    if any(not isinstance(name, str) or name not in files for name in selected) or len(set(selected)) != 3:
        raise ValueError('Distinct retained observation, test report and log required')
    actual, directories = set(), 0
    for parent, dirs, names in os.walk(root, followlinks=False):
        directories += len(dirs)
        if directories > 128:
            raise ValueError('Return directory inventory exceeds bound')
        for name in dirs:
            path = Path(parent) / name
            if path.is_symlink() or path.is_junction():
                raise ValueError('Linked return directory rejected')
        for name in names:
            relative = (Path(parent) / name).relative_to(root).as_posix()
            _local_file(root, relative)
            actual.add(relative)
            if len(actual) > 65:
                raise ValueError('Unbounded return inventory')
    if actual != set(files) | {'manifest.json'}:
        raise ValueError('Unlisted or missing return files')


def verify(journal_path, operation, contract_path, contract_sha256, directory, manifest_sha256):
    """Check a normalized synthetic return against a prior acknowledged intent."""
    e._sha(contract_sha256, 'separately retained contract hash')
    e._sha(manifest_sha256, 'separately retained return manifest hash')
    contract = _json(contract_path, contract_sha256)
    _version(contract, {'operation_key', 'spec_sha256', 'frozen_at', 'expected_tests'},
             'synthetic-return-contract', 'return contract')
    e._sha(contract['spec_sha256'], 'contract specification hash')
    frozen = e._time(contract['frozen_at'], 'return contract freeze')
    expected = contract['expected_tests']
    if (not isinstance(expected, list) or not 1 <= len(expected) <= 1000 or
            any(not launches._text(item, 128) for item in expected) or len(set(expected)) != len(expected)):
        raise ValueError('Distinct bounded expected fixture IDs required')
    with launches.LaunchJournal(journal_path, read_only=True) as journal:
        evidence = journal.evidence(operation)
    if contract['operation_key'] != operation or contract['spec_sha256'] != evidence['spec_sha256']:
        raise ValueError('Contract does not bind this launch intent')
    if evidence['state'] != 'acknowledged':
        raise ValueError('Acknowledged task required; unresolved submission stays held without retry')

    root = _root(directory)
    manifest = _json(_local_file(root, 'manifest.json'), manifest_sha256)
    _version(manifest, {'operation_key', 'spec_sha256', 'task_id', 'contract_sha256',
                       'acknowledgement_sha256', 'returned_at', 'files',
                       'observation_path', 'test_report_path', 'log_path'},
             'synthetic-qualification-return', 'return manifest')
    if (manifest['operation_key'] != operation or manifest['spec_sha256'] != evidence['spec_sha256'] or
            manifest['task_id'] != evidence['acknowledgement']['task_id'] or
            manifest['acknowledgement_sha256'] != evidence['receipt_sha256'] or
            manifest['contract_sha256'] != contract_sha256):
        raise ValueError('Return does not bind the acknowledged task, receipt and frozen contract')
    if e._time(manifest['returned_at'], 'return observation') < frozen:
        raise ValueError('Return predates the declared contract freeze')
    _files(root, manifest)
    observation = _json(_local_file(root, manifest['observation_path']),
                        manifest['files'][manifest['observation_path']]['sha256'])
    _version(observation, {'operation_key', 'task_id', 'state', 'execution_started',
                          'bindings', 'runtime_capability', 'policy_enforcement', 'notes'},
             'synthetic-runtime-observation', 'runtime observation')
    if observation['operation_key'] != operation or observation['task_id'] != manifest['task_id']:
        raise ValueError('Runtime observation names another task or occurrence')
    e._text(observation['state'], 'observed state')
    if observation['state'] not in {'completed', 'held', 'failed', 'cancelled', 'running', 'unknown'}:
        raise ValueError('Unsupported observed task state')
    if type(observation['execution_started']) is not bool:
        raise ValueError('Explicit execution-start observation required')
    e._text(observation['runtime_capability'], 'runtime capability')
    e._text(observation['policy_enforcement'], 'policy enforcement')
    if (observation['runtime_capability'] not in {'present', 'absent', 'unknown'} or
            observation['policy_enforcement'] not in {'enforced', 'not_enforced', 'unknown'}):
        raise ValueError('Explicit observed or unknown runtime capability/policy required')
    e._text(observation['notes'], 'observation notes and scope')
    e._keys(observation['bindings'], BINDINGS, 'runtime bindings')
    matches = {}
    for key in BINDINGS:
        value = observation['bindings'][key]
        if value is not None:
            if key == 'source_revision':
                if not isinstance(value, str) or len(value) != 40 or any(c not in '0123456789abcdef' for c in value):
                    raise ValueError('Observed source revision must be a commit SHA or unknown')
            else:
                e._sha(value, key)
        matches[key] = 'unknown' if value is None else 'match' if value == evidence['specification'][key] else 'mismatch'

    report = _json(_local_file(root, manifest['test_report_path']),
                   manifest['files'][manifest['test_report_path']]['sha256'])
    _version(report, {'cases'}, 'synthetic-fixture-report', 'fixture report')
    if not isinstance(report['cases'], list) or len(report['cases']) > len(expected):
        raise ValueError('Bounded reported fixtures required')
    outcomes = {}
    for case in report['cases']:
        e._keys(case, {'test_id', 'outcome', 'reason'}, 'fixture outcome')
        if not launches._text(case['test_id'], 128) or case['test_id'] not in expected or case['test_id'] in outcomes:
            raise ValueError('Unknown or duplicate reported fixture')
        e._text(case['outcome'], 'fixture outcome'); e._text(case['reason'], 'fixture reason')
        if case['outcome'] not in {'passed', 'failed', 'error', 'skipped'}:
            raise ValueError('Invalid fixture outcome')
        outcomes[case['test_id']] = case['outcome']
    if not observation['execution_started'] and outcomes:
        raise ValueError('Fixture results contradict reported non-execution')
    counts = dict(Counter(outcomes.values()))
    missing = [item for item in expected if item not in outcomes]
    reasons = []
    if observation['state'] != 'completed': reasons.append('Reported task state: ' + observation['state'])
    if not observation['execution_started']: reasons.append('No execution reported')
    if observation['runtime_capability'] != 'present': reasons.append('Runtime capability not observed present')
    if observation['policy_enforcement'] != 'enforced': reasons.append('Current policy enforcement not observed')
    for key, value in matches.items():
        if value != 'match': reasons.append('Runtime binding ' + key + ': ' + value)
    if missing: reasons.append('Expected fixture results missing')
    if any(outcome != 'passed' for outcome in outcomes.values()): reasons.append('Failed, errored or skipped fixtures remain')
    if observation['execution_started'] and manifest['files'][manifest['log_path']]['bytes'] == 0:
        reasons.append('Execution reported without a retained nonempty log')
    return {'schema_version': 1, 'status': 'hold' if reasons else 'consistent_synthetic_return',
            'operation_key': operation, 'task_id': manifest['task_id'], 'spec_sha256': evidence['spec_sha256'],
            'manifest_sha256': manifest_sha256, 'contract_sha256': contract_sha256,
            'integrity_verified': True, 'verified_files': len(manifest['files']),
            'journal_state': evidence['state'], 'active_journal_binding': evidence['active_binding'],
            'reported_state': observation['state'], 'reported_execution_started': observation['execution_started'],
            'runtime_binding_comparison': matches, 'expected_tests': len(expected),
            'reported_outcomes': counts, 'missing_test_ids': missing, 'hold_reasons': reasons,
            'permission_failure_inferred': False,
            'limits': ['Normalized observations and timestamps are operator attestations, not authenticated provider receipts.',
                       'A consistent fixture report does not qualify the runtime, remote ownership, recovery or scientific work.',
                       'Acknowledgement remains unchanged; no slot is released and no retry, resume or schedule is authorized.'],
            **FLAGS}
