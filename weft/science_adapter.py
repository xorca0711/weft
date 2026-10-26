"""Pinned scientific packages and controlled replay, never an author-code runner.

Fixture replays use JobLedger's jobs/attempts/events and its single execution slot.
No subprocess, network, provider call or supplied code is executed by this module.
Receipts establish local byte consistency, not process termination or science.
"""
from __future__ import annotations

from contextlib import closing, contextmanager
import hashlib
from pathlib import Path
import secrets
import sqlite3

from . import evidence as ev
from .identity import digest
from .jobs import JobLedger, JobError, canonical
from .workflow import _exclusive

VERSION = 'weft-science-adapter-v1'
KIND = 'scientific-fixture-replay'
MAX_OUTPUT = 1_048_576
MAX_TOTAL = 8_388_608


def implementation():
    root = Path(__file__).resolve().parent
    return {name: hashlib.sha256((root / name).read_bytes()).hexdigest()
            for name in ('evidence.py', 'scientific.py', 'science_adapter.py',
                         'science_review.py', 'jobs.py')}


def _writable(workspace):
    if not workspace.active: raise ValueError('Restored workspace is inactive for writes')
    workspace._isolation()
    path = ev.contained(workspace.root, '.workflow.lock')
    if path.exists() and (not path.is_file() or path.stat().st_nlink != 1):
        raise ValueError('Aliased workflow lock rejected')


def _save(workspace, name, raw):
    if len(raw) > ev.MAX_RECORD: raise ValueError('Retained artifact exceeds 1 MiB')
    path = ev.contained(workspace.root, name)
    if path.exists():
        if ev.read_raw(path) != raw: raise ValueError('Immutable artifact differs; retain and investigate')
    else:
        ev.write_new(path, raw)
    return ev.reference(workspace.root, name)


def package(workspace, contract_ref, plan_ref):
    """Freeze an execution-neutral manifest; every dependency is verified at use."""
    _writable(workspace)
    with _exclusive(workspace):
        contract = workspace.bound_record(contract_ref, 'analysis-contract')
        workspace.validate(contract)
        plan = workspace.bound_record(plan_ref, 'numerical-plan', case=contract)
        workspace.validate(plan)
        if plan['contract'] != contract_ref: raise ValueError('Numerical plan uses another contract')
        data = workspace.bound_record(contract['feasibility'], 'data-feasibility', case=contract)
        case = workspace.bound_record(contract['case'], 'case-revision', case=contract)
        source = workspace.bound_record(case['source_manifest'], 'source-manifest', case=case)
        refs = [contract_ref, plan_ref, contract['case'], contract['feasibility'],
                case['source_manifest'], contract['environment'], contract['design_review'],
                *contract['code_files'], *(f['file'] for f in data['files']),
                *(r['file'] for r in source['resources'] if r['file'])]
        closure = sorted({canonical(r): r for r in refs}.values(), key=canonical)
        for ref in closure: workspace.file(ref)
        obj = {'schema_version': VERSION, 'kind': 'prepared-scientific-package',
               'workspace_id': workspace.binding['workspace_id'], 'contract': contract_ref,
               'numerical_plan': plan_ref, 'closure': closure, 'implementation': implementation(),
               'exposure': case['exposure']['mode'], 'author_code_executed': False, **ev.FLAGS}
        raw = ev.encoded(obj)
        ref = _save(workspace, 'packages/' + hashlib.sha256(raw).hexdigest() + '.json', raw)
    return {'status': 'prepared', 'package': ref, 'live_dispatch': 'hold', **ev.FLAGS}


def load_package(workspace, ref):
    obj = workspace.file(ref, parse=True)
    ev.keys(obj, {'schema_version', 'kind', 'workspace_id', 'contract', 'numerical_plan',
                  'closure', 'implementation', 'exposure', 'author_code_executed', *ev.FLAGS})
    if (obj['schema_version'] != VERSION or obj['kind'] != 'prepared-scientific-package'
            or obj['workspace_id'] != workspace.binding['workspace_id']
            or obj['implementation'] != implementation()
            or obj['author_code_executed'] is not False
            or any(obj[key] is not False for key in ev.FLAGS)):
        raise ValueError('Package identity, implementation or authority drift')
    if ref['root'] != 'workspace' or ref['path'] != 'packages/' + ref['sha256'] + '.json':
        raise ValueError('Package must be retained at its content address')
    contract = workspace.bound_record(obj['contract'], 'analysis-contract')
    plan = workspace.bound_record(obj['numerical_plan'], 'numerical-plan', case=contract)
    workspace.validate(contract); workspace.validate(plan)
    if plan['contract'] != obj['contract']: raise ValueError('Mismatched package plan')
    case = workspace.bound_record(contract['case'], 'case-revision', case=contract)
    data = workspace.bound_record(contract['feasibility'], 'data-feasibility', case=contract)
    source = workspace.bound_record(case['source_manifest'], 'source-manifest', case=case)
    expected = [obj['contract'], obj['numerical_plan'], contract['case'], contract['feasibility'],
                case['source_manifest'], contract['environment'], contract['design_review'],
                *contract['code_files'], *(f['file'] for f in data['files']),
                *(r['file'] for r in source['resources'] if r['file'])]
    if obj['closure'] != sorted({canonical(r): r for r in expected}.values(), key=canonical):
        raise ValueError('Incomplete package dependency closure')
    for item in obj['closure']: workspace.file(item)
    if obj['exposure'] != case['exposure']['mode']: raise ValueError('Exposure drift')
    return obj, contract, plan


def _ledger_path(workspace):
    _writable(workspace)
    name = 'control/jobs.sqlite'
    for suffix in ('', '-journal', '-wal', '-shm'):
        path = ev.contained(workspace.root, name + suffix)
        if path.exists() and (not path.is_file() or path.stat().st_nlink != 1):
            raise ValueError('Aliased ledger rejected')
    return ev.contained(workspace.root, name)


@contextmanager
def open_replay(workspace, **kwargs):
    """One host/path-bound workspace database, shared with synthetic JobLedger jobs."""
    with JobLedger(_ledger_path(workspace), **kwargs) as ledger:
        yield FixtureReplay(workspace, ledger)


class FixtureReplay:
    def __init__(self, workspace, ledger):
        if ledger.path.absolute() != _ledger_path(workspace):
            raise ValueError('Use the authoritative workspace control/jobs.sqlite ledger')
        self.workspace, self.ledger = workspace, ledger

    def _packet(self, ref):
        pkg, contract, _ = load_package(self.workspace, ref)
        if pkg['exposure'] != 'synthetic-fixture':
            raise ValueError('Only explicitly synthetic cases can use controlled replay')
        if contract['limits']['max_attempts'] > 3:
            raise ValueError('Controlled replay has a maximum of three attempts')
        return {'schema_version': VERSION, 'kind': KIND, 'package': ref,
                'workspace_id': self.workspace.binding['workspace_id'],
                'max_attempts': contract['limits']['max_attempts'],
                'lease_seconds': min(contract['limits']['wall_seconds'], 300), **ev.FLAGS}

    def begin(self, ref):
        _writable(self.workspace)
        packet = self._packet(ref)
        job = digest(packet)
        ledger = self.ledger
        with _exclusive(self.workspace), ledger._transaction():
            # Repeat freshness checks inside the workspace lock.
            if packet != self._packet(ref): raise ValueError('Package changed during admission')
            at = ledger._now()
            found = ledger.db.execute('SELECT state FROM jobs WHERE id=?', (job,)).fetchone()
            if found and found['state'] not in {'fixture_failed', 'fixture_cancelled'}:
                raise JobError('Replay already reserved or complete; recover, never redispatch')
            if ledger.db.execute("SELECT 1 FROM attempts WHERE state IN ('running','unknown','cancel_requested')").fetchone():
                raise JobError('Active or unresolved attempt reserves the execution slot')
            count = ledger.db.execute('SELECT COUNT(*) FROM attempts WHERE job_id=?', (job,)).fetchone()[0]
            if count >= packet['max_attempts']: raise JobError('Attempt budget exhausted')
            if not found:
                ledger.db.execute('INSERT INTO jobs(id,packet) VALUES(?,?)', (job, canonical(packet)))
                ledger._event(job, 'fixture-submitted', {'package': ref, **ev.FLAGS}, at)
            token = secrets.token_hex(24)
            cur = ledger.db.execute('INSERT INTO attempts(job_id,token_hash,started,expires,state) VALUES(?,?,?,?,?)',
                                    (job, digest(token), at, at + packet['lease_seconds'], 'running'))
            claim = {'job_id': job, 'attempt_id': cur.lastrowid, 'lease_token': token,
                     'expires': at + packet['lease_seconds']}
            ledger.db.execute("UPDATE jobs SET state='running' WHERE id=?", (job,))
            ledger._event(job, 'fixture-reserved-no-process', {'attempt_id': cur.lastrowid}, at)
            # If the process dies before commit, retained checkpoint is an orphan:
            # exclusive directory creation prevents silent reuse of its attempt ID.
            root = ev.contained(self.workspace.root, self._prefix(claim))
            root.mkdir(parents=True, exist_ok=False)
            ev.write_new(root / 'checkpoint.json', ev.encoded(claim))
        return {**claim, 'status': 'fixture-reserved', 'checkpoint': self._prefix(claim) + '/checkpoint.json',
                'author_code_executed': False, **ev.FLAGS}

    @staticmethod
    def _prefix(claim):
        ev.sha(claim['job_id'])
        if type(claim['attempt_id']) is not int or claim['attempt_id'] < 1: raise ValueError('Invalid attempt')
        return f"runs/{claim['job_id']}/attempt-{claim['attempt_id']:06d}"

    def _bound(self, claim):
        ev.keys(claim, {'job_id', 'attempt_id', 'lease_token', 'expires'})
        row = self.ledger._attempt(claim)
        packet = self.ledger.status(claim['job_id'])['packet']
        if packet.get('kind') != KIND or packet != self._packet(packet['package']):
            raise ValueError('Not a matching fixture replay')
        checkpoint = ev.decode(ev.read_raw(ev.contained(self.workspace.root, self._prefix(claim) + '/checkpoint.json')))
        if checkpoint != claim: raise ValueError('Checkpoint identity drift')
        return row, packet

    def receive(self, claim, directory, expected_manifest_sha256):
        """Save a complete return before applying it; retries resume exact bytes.

        expected_manifest_sha256 must come from a separately retained delivery
        record. Matching it detects corruption; it is not worker authentication.
        """
        _writable(self.workspace); ev.sha(expected_manifest_sha256)
        with _exclusive(self.workspace):
            _, packet = self._bound(claim)
            pkg, contract, _ = load_package(self.workspace, packet['package'])
            directory = ev.unlinked(directory).resolve(strict=True)
            raw = ev.read_raw(directory / 'return.json')
            if hashlib.sha256(raw).hexdigest() != expected_manifest_sha256:
                raise ValueError('Separately retained return hash mismatch')
            ret = ev.decode(raw)
            ev.keys(ret, {'schema_version', 'kind', 'job_id', 'attempt_id', 'package_sha256',
                          'outcome', 'files', 'error'})
            if (ret['schema_version'] != VERSION or ret['kind'] != 'synthetic-fixture-return'
                    or ret['job_id'] != claim['job_id'] or ret['attempt_id'] != claim['attempt_id']
                    or ret['package_sha256'] != packet['package']['sha256']
                    or ret['outcome'] not in {'completed', 'failed', 'cancelled'}):
                raise ValueError('Return identity/outcome mismatch')
            if ret['outcome'] == 'completed':
                if ret['error'] is not None: raise ValueError('Completed fixture has an error')
            else: ev.text(ret['error'])
            expected = {o['path'] for o in contract['outputs']}
            if not isinstance(ret['files'], list) or len(ret['files']) > len(expected):
                raise ValueError('Bounded return inventory required')
            names, content, total = set(), {}, 0
            for item in ret['files']:
                ev.keys(item, {'path', 'sha256', 'bytes'})
                ev.relative(item['path']); ev.sha(item['sha256'])
                if (item['path'] not in expected or item['path'].casefold() in names
                        or type(item['bytes']) is not int or not 0 <= item['bytes'] <= MAX_OUTPUT):
                    raise ValueError('Unplanned, duplicate or oversized output')
                names.add(item['path'].casefold()); total += item['bytes']
                if total > min(MAX_TOTAL, contract['limits']['disk_bytes']):
                    raise ValueError('Return exceeds frozen disk/replay bound')
                payload = ev.read_raw(ev.contained(directory, item['path']))
                if len(payload) != item['bytes'] or hashlib.sha256(payload).hexdigest() != item['sha256']:
                    raise ValueError('Output identity drift')
                content[item['path']] = payload
            if ret['outcome'] == 'completed' and set(content) != expected:
                raise ValueError('Completed return missing planned outputs')
            prefix = self._prefix(claim)
            # On interruption, a repeated delivery can only fill missing exact files.
            for name, payload in content.items(): _save(self.workspace, prefix + '/' + name, payload)
            manifest = _save(self.workspace, prefix + '/return.json', raw)
            receipt = {'schema_version': VERSION, 'kind': 'fixture-receipt',
                       'job_id': claim['job_id'], 'attempt_id': claim['attempt_id'],
                       'package': packet['package'], 'return_manifest': manifest,
                       'outcome': 'fixture_' + ret['outcome'],
                       'outputs': [{'path': name, 'file': ev.reference(self.workspace.root, prefix + '/' + name)}
                                   for name in sorted(content)],
                       'error': ret['error'], 'scientific_validity_established': False,
                       'author_code_executed': False, **ev.FLAGS}
            receipt_ref = _save(self.workspace, prefix + '/receipt.json', ev.encoded(receipt))
        return self.recover(claim, receipt_ref)

    def recover(self, claim, receipt_ref):
        _writable(self.workspace)
        with _exclusive(self.workspace), self.ledger._transaction():
            row, packet = self._bound(claim)
            receipt = verified_receipt(self.workspace, receipt_ref)
            if (receipt['job_id'] != claim['job_id'] or receipt['attempt_id'] != claim['attempt_id']
                    or receipt['package'] != packet['package']):
                raise ValueError('Recovery receipt belongs to another attempt')
            previous = self.ledger.db.execute("SELECT evidence FROM events WHERE job_id=? AND action='fixture-return-verified'",
                                              (claim['job_id'],)).fetchall()
            for event in previous:
                value = ev.decode(event['evidence'].encode())
                if value['attempt_id'] == claim['attempt_id']:
                    if value['receipt'] != receipt_ref: raise ValueError('Terminal receipt differs')
                    return {'status': receipt['outcome'], 'receipt': receipt_ref, 'idempotent': True, **ev.FLAGS}
            if row['state'] not in {'running', 'unknown', 'cancel_requested'}:
                raise JobError('Terminal fixture cannot be rewritten')
            at = self.ledger._now()
            self.ledger.db.execute('UPDATE attempts SET state=? WHERE id=?', (receipt['outcome'], row['id']))
            self.ledger.db.execute('UPDATE jobs SET state=? WHERE id=?', (receipt['outcome'], claim['job_id']))
            self.ledger._event(claim['job_id'], 'fixture-return-verified',
                               {'attempt_id': row['id'], 'receipt': receipt_ref,
                                'process_termination_claimed': False}, at)
        return {'status': receipt['outcome'], 'receipt': receipt_ref, 'idempotent': False, **ev.FLAGS}


def verified_receipt(workspace, ref):
    receipt = workspace.file(ref, parse=True)
    ev.keys(receipt, {'schema_version', 'kind', 'job_id', 'attempt_id', 'package',
                      'return_manifest', 'outcome', 'outputs', 'error',
                      'scientific_validity_established', 'author_code_executed', *ev.FLAGS})
    prefix = FixtureReplay._prefix(receipt)
    if (ref['root'] != 'workspace' or ref['path'] != prefix + '/receipt.json'
            or receipt['schema_version'] != VERSION or receipt['kind'] != 'fixture-receipt'
            or receipt['author_code_executed'] is not False
            or receipt['scientific_validity_established'] is not False
            or any(receipt[key] is not False for key in ev.FLAGS)):
        raise ValueError('Invalid retained fixture receipt')
    pkg, contract, _ = load_package(workspace, receipt['package'])
    if pkg['exposure'] != 'synthetic-fixture': raise ValueError('Nonfixture return unsupported')
    manifest = workspace.file(receipt['return_manifest'], parse=True)
    ev.keys(manifest, {'schema_version', 'kind', 'job_id', 'attempt_id', 'package_sha256',
                       'outcome', 'files', 'error'})
    if (receipt['return_manifest']['root'] != 'workspace'
            or receipt['return_manifest']['path'] != prefix + '/return.json'
            or manifest['schema_version'] != VERSION or manifest['kind'] != 'synthetic-fixture-return'
            or manifest['job_id'] != receipt['job_id'] or manifest['attempt_id'] != receipt['attempt_id']
            or manifest['package_sha256'] != receipt['package']['sha256']
            or manifest['outcome'] not in {'completed', 'failed', 'cancelled'}
            or receipt['outcome'] != 'fixture_' + manifest['outcome']
            or receipt['error'] != manifest['error']):
        raise ValueError('Receipt/return identity mismatch')
    expected = {o['path'] for o in contract['outputs']}
    actual = set()
    inventory = []
    total = 0
    for output in receipt['outputs']:
        ev.keys(output, {'path', 'file'})
        name, item = output['path'], output['file']
        if name not in expected or name in actual or item['root'] != 'workspace' or item['path'] != prefix + '/' + name:
            raise ValueError('Receipt output escapes attempt or plan')
        workspace.file(item)
        if item['bytes'] > MAX_OUTPUT: raise ValueError('Oversized replay output')
        total += item['bytes']; actual.add(name)
        inventory.append({'path': name, 'sha256': item['sha256'], 'bytes': item['bytes']})
    if total > min(MAX_TOTAL, contract['limits']['disk_bytes']): raise ValueError('Oversized return')
    if sorted(inventory, key=lambda x: x['path']) != sorted(manifest['files'], key=lambda x: x['path']):
        raise ValueError('Receipt output inventory differs from return')
    if manifest['outcome'] == 'completed' and (actual != expected or receipt['error'] is not None):
        raise ValueError('Incomplete completed fixture')
    if manifest['outcome'] != 'completed': ev.text(receipt['error'])
    return receipt


def readiness(workspace, contract_ref):
    from .scientific import preflight
    result = preflight(workspace, contract_ref)
    return {**result, 'remaining_jobs': {
        'W04': 'Qualify author-code isolation on a permitted worker',
        'W05': 'Bind actual worker observations and checkpoint returns to this ledger',
        'W08': 'Fresh real case, approved design, qualified execution and owner disposition',
        'W10': 'Supported evidence for the existing held occurrence and exact prompt binding',
        'W11': 'Remote writer fencing, cancellation, usage and PC-independent qualification',
        'W12': 'Separate optional scope/cadence/limits/activation after W11'},
        'recurrence_enabled': False, 'runtime_qualified': False}


def attempt_status(workspace):
    """Read-only operational inventory, including incomplete returns, without tokens."""
    path = ev.contained(workspace.root, 'control/jobs.sqlite')
    if not path.exists(): return []
    if not path.is_file() or path.stat().st_nlink != 1: raise ValueError('Aliased ledger rejected')
    with closing(sqlite3.connect(path.as_uri() + '?mode=ro', uri=True)) as db:
        db.row_factory = sqlite3.Row
        rows = db.execute('SELECT a.id,a.job_id,a.state,a.expires FROM attempts a ORDER BY a.id').fetchall()
    result = []
    for row in rows:
        item = dict(row)
        prefix = FixtureReplay._prefix({'job_id': row['job_id'], 'attempt_id': row['id']})
        name = prefix + '/receipt.json'
        item['receipt'] = ev.reference(workspace.root, name) if ev.contained(workspace.root, name).exists() else None
        item['checkpoint'] = prefix + '/checkpoint.json' if ev.contained(workspace.root, prefix + '/checkpoint.json').exists() else None
        result.append(item)
    return result
