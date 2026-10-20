"""Single-operator pull coordinator over existing Weft components.

No model/provider launcher, scientific execution, automatic reconciliation or
hold release. Existing pilot catalogs are readable but cannot be adopted.
"""
from collections import Counter
from contextlib import contextmanager
from html import escape
import hashlib
import json
import os
from pathlib import Path
import socket
import sqlite3
from types import SimpleNamespace

from . import batches, handoff, qualification, screening
from .discovery import now, write_json
from .identity import digest
from .reading import validate_reading
from .reading_locations import presented_result

FLAGS = {'model_invoked': False, 'automatic_cloud_launch': False,
         'scientific_execution_allowed': False, 'claim_validated': False,
         'actor_identity_verified': False}
CONSTRAINTS = [
    {'id': 'browser-policy', 'state': 'unresolved',
     'reason': 'Loaded origin allow rule and observed browser denial disagree; effective policy source unknown.',
     'evidence': 'docs/LAUNCHER_ACCESS_DIAGNOSIS.md'},
    {'id': 'cli-route', 'state': 'unqualified',
     'reason': 'No verified named environment mapping; known app worker rejected by CLI.',
     'evidence': 'docs/LAUNCHER_ACCESS_DIAGNOSIS.md'},
    {'id': 'native-runtime', 'state': 'hold',
     'reason': 'Task admitted; required runtime-status capability absent; zero tests.',
     'evidence': 'docs/qualification/NATIVE_RUNTIME_HOLD.md'},
    {'id': 'B4', 'state': 'hold',
     'reason': 'Platform-interrupted source review; no retry, rerouting or replacement.',
     'evidence': 'docs/B3_CLOUD_B4_REVIEW.md'},
    {'id': 'Choi', 'state': 'closed', 'reason': 'Descriptive benchmark remains closed.'},
    {'id': 'M6', 'state': 'disabled', 'reason': 'No schedule or unattended operation.'},
]


def _has(store, name):
    return bool(store.db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (name,)).fetchone())


@contextmanager
def readonly(root):
    """Status/export cannot initialize, migrate or activate a catalog."""
    root = Path(root).resolve(strict=True)
    if json.loads((root / 'WEFT_STORE.json').read_text(encoding='utf-8')) != {
            'kind': 'weft-discovery', 'schema_version': 1}:
        raise ValueError('Unexpected discovery store marker')
    db = sqlite3.connect((root / 'catalog.sqlite').as_uri() + '?mode=ro', uri=True)
    db.row_factory = sqlite3.Row
    try:
        db.execute('PRAGMA query_only=ON')
        db.execute('BEGIN')
        yield SimpleNamespace(root=root, db=db)
    finally:
        db.close()


@contextmanager
def _exclusive(store):
    """Serializes coordinator calls; component locks remain authoritative within
    their operations. Cooperative local use only, never distributed fencing.
    """
    with (store.root / '.workflow.lock').open('a+b') as lock:
        lock.seek(0, 2)
        if lock.tell() == 0:
            lock.write(b'0'); lock.flush()
        lock.seek(0)
        try:
            if os.name == 'nt':
                import msvcrt
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise ValueError('Workflow busy; do not break its lock') from exc
        try:
            yield
        finally:
            lock.seek(0)
            if os.name == 'nt':
                msvcrt.locking(lock.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(lock, fcntl.LOCK_UN)


def _binding(store, bid):
    if not _has(store, 'workflow_binding'):
        raise ValueError('Unmanaged catalog: status/export only; existing pilots cannot be adopted')
    row = store.db.execute('SELECT * FROM workflow_binding').fetchone()
    if not row or row['batch_id'] != bid:
        raise ValueError('Batch is not owned by this workflow')
    binding = json.loads(row['binding_json'])
    if digest(binding) != row['binding_sha']:
        raise ValueError('Workflow binding changed')
    if binding['host'] != socket.gethostname() or binding['store'] != str(store.root):
        raise ValueError('Restored/moved catalog is inactive: operator reconciliation required')
    if store.db.execute('SELECT COUNT(*) FROM batches').fetchone()[0] != 1:
        raise ValueError('Workflow requires one dedicated batch catalog')
    batches.specification(store, bid)
    return row, binding


def initialize(store, bid, actor):
    if not isinstance(actor, str) or not actor.strip() or len(actor) > 200:
        raise ValueError('Explicit bounded actor label required')
    with _exclusive(store):
        if _has(store, 'workflow_binding') and store.db.execute('SELECT 1 FROM workflow_binding').fetchone():
            _, binding = _binding(store, bid)
            if actor != binding['actor']:
                raise ValueError('Workflow actor differs from its binding')
            return status(store, bid)
        # Opt in before the first search. Never turn a historical hold into work.
        batches.specification(store, bid)
        if (store.db.execute('SELECT COUNT(*) FROM batches').fetchone()[0] != 1
                or store.db.execute('SELECT 1 FROM runs LIMIT 1').fetchone()
                or store.db.execute('SELECT 1 FROM candidates LIMIT 1').fetchone()
                or store.db.execute("SELECT 1 FROM batch_windows WHERE status!='pending' OR attempts!=0").fetchone()
                or (_has(store, 'screening_handoffs') and store.db.execute('SELECT 1 FROM screening_handoffs').fetchone())):
            raise ValueError('Only a fresh, unstarted, dedicated batch can initialize a workflow')
        handoff.initialize(store)
        qualification.schema(store)
        store.db.executescript('''
          CREATE TABLE IF NOT EXISTS workflow_binding(
            singleton INTEGER PRIMARY KEY CHECK(singleton=1), batch_id TEXT NOT NULL,
            binding_json TEXT NOT NULL, binding_sha TEXT NOT NULL, hold_reason TEXT);
          CREATE TABLE IF NOT EXISTS workflow_returns(
            id TEXT PRIMARY KEY, stage TEXT NOT NULL, candidate_id TEXT NOT NULL,
            claim_id TEXT, response_json TEXT NOT NULL, response_sha TEXT NOT NULL,
            state TEXT NOT NULL, result_json TEXT);
          CREATE UNIQUE INDEX IF NOT EXISTS one_pending_workflow_return
            ON workflow_returns((1)) WHERE state!='complete';
        ''')
        binding = {'schema_version': 1, 'batch_id': bid, 'actor': actor,
                   'host': socket.gethostname(), 'store': str(store.root),
                   'mode': 'manual-pull', 'created': now(), **FLAGS}
        with store.db:
            store.db.execute('INSERT INTO workflow_binding VALUES(1,?,?,?,NULL)',
                             (bid, json.dumps(binding), digest(binding)))
            batches.event(store, bid, 'workflow-initialized', binding)
        return status(store, bid)


def create(store, context, profile_name, profile, streams, since, until, *, actor, **limits):
    # Check before batches.create so a rejected legacy adoption writes no batch.
    if store.db.execute('SELECT 1 FROM runs LIMIT 1').fetchone() or (
            _has(store, 'batches') and store.db.execute('SELECT 1 FROM batches LIMIT 1').fetchone()):
        raise ValueError('workflow-create requires a fresh store; use advance/status for an existing workflow')
    bid = batches.create(store, context, profile_name, profile, streams, since, until, **limits)
    return initialize(store, bid, actor)


def _pending(store):
    if not _has(store, 'workflow_returns'):
        return None
    return store.db.execute("SELECT * FROM workflow_returns WHERE state!='complete'").fetchone()


def _claims(store):
    if not _has(store, 'screening_handoffs'):
        return []
    return [dict(r) for r in store.db.execute(
        'SELECT id,batch_id,candidate_id,state,expires FROM screening_handoffs ORDER BY rowid')]


def _item_state(store, bid, item, used_reads, cap):
    """Derive stages from source records; never promote or rewrite a decision."""
    row = store.db.execute('SELECT * FROM batch_items WHERE batch_id=? AND candidate_id=?',
                           (bid, item['candidate_id'])).fetchone()
    state, reason = item['stage'], item['reason']
    if not item['disposition_current']:
        return 'hold', 'Candidate/disposition is stale'
    if state in {'held', 'deferred'}:
        return ('hold' if state == 'held' else 'deferred'), reason
    if row['packet_json']:
        try:
            screening.live_candidate(store, screening.stored_packet(row))
        except (ValueError, OSError, KeyError, TypeError) as exc:
            return 'hold', str(exc)
    if state in {'queued', 'awaiting_agent'}:
        return 'screening', reason
    if item['decision'] in {'hold', 'reject'}:
        return ('hold' if item['decision'] == 'hold' else 'rejected'), reason
    if item['decision'] != 'read_next':
        return 'hold', 'Unrecognized screening disposition'
    if not row['reading_json']:
        return ('deferred', 'Full-read attempt cap reached') if used_reads >= cap else ('material', None)
    read = json.loads(row['reading_json'])
    if read['status'] != 'prepared':
        return 'hold', read.get('reason', 'Material preparation held')
    try:
        directory = screening.check_reading_files(store, read)
        if not row['reading_result_json']:
            return 'reading', None
        assessment = json.loads(row['reading_result_json'])
        validate_reading(directory, assessment)
        if assessment['next_action'] == 'hold':
            return 'hold', 'Reading assessment requests hold'
    except (ValueError, OSError, KeyError, TypeError) as exc:
        return 'hold', str(exc)
    evidence = item['evidence_qualification']
    if not evidence or evidence['status'] == 'awaiting_review':
        return 'evidence', None
    if not evidence['current']:
        return 'hold', evidence.get('reason', 'Evidence is no longer current')
    return 'reviewed', 'Proposals recorded; scientific acceptance not assessed'


def status(store, bid):
    report = batches.status_report(store, bid)
    spec = batches.specification(store, bid)
    blockers = []
    try:
        row, binding = _binding(store, bid)
        if row['hold_reason']:
            blockers.append(row['hold_reason'])
    except ValueError as exc:
        binding = None
        blockers.append(str(exc))
    pending = _pending(store)
    if pending:
        blockers.append('Saved return requires explicit recovery: ' + pending['id'])
    claims = _claims(store)
    for claim in claims:
        claim['expired'] = handoff._time() >= claim['expires']
        claim['automatic_reassignment_allowed'] = False
        if claim['state'] != 'complete' and (claim['batch_id'] != bid or claim['expired'] or claim['state'] == 'return_pending'):
            blockers.append('Unresolved handoff: ' + claim['id'])
    used = store.db.execute('SELECT COUNT(*) FROM batch_items WHERE batch_id=? AND reading_json IS NOT NULL', (bid,)).fetchone()[0]
    for item in report['items']:
        item['workflow_stage'], item['workflow_reason'] = _item_state(store, bid, item, used, spec['max_full_reads'])
        evidence = item['evidence_qualification']
        if evidence and evidence.get('record_sha256'):
            record = store.db.execute('SELECT record_json FROM evidence_reviews WHERE record_sha=?',
                                      (evidence['record_sha256'],)).fetchone()
            assessment = json.loads(record[0])
            item['evidence_review'] = {key: assessment[key] for key in ('actor', 'prior_exposure', 'data', 'rq_compatibility', 'coverage', 'limitations')}
    for claim in claims:
        if claim['state'] != 'complete' and any(i['candidate_id'] == claim['candidate_id'] and i['workflow_stage'] == 'hold' for i in report['items']):
            blockers.append('Active handoff source/disposition is held: ' + claim['id'])
    stages = Counter(i['workflow_stage'] for i in report['items'])
    # A crash can leave all windows complete before batch_items are populated.
    missing = store.db.execute('''SELECT 1 FROM candidate_runs cr JOIN batch_windows w ON w.run_id=cr.run_id
        JOIN candidates c ON c.id=cr.candidate_id WHERE w.batch_id=? AND w.status='complete' AND c.current=1
        AND NOT EXISTS(SELECT 1 FROM batch_items bi WHERE bi.batch_id=w.batch_id AND bi.candidate_id=c.id) LIMIT 1''', (bid,)).fetchone()
    if blockers:
        state, action = 'hold', 'Inspect blockers; recover only a saved return, never redispatch'
    elif not report['discovery_complete']:
        unsafe = [w for w in report['windows'] if w['status'] not in {'pending', 'complete', 'split'}]
        budget_used = sum(w['attempts'] for w in report['windows']) >= spec['max_searches']
        state = 'hold' if unsafe or budget_used else 'ready'
        action = 'Inspect discovery windows; no automatic reconciliation' if state == 'hold' else 'advance --allow-network for bounded metadata retrieval'
    elif missing:
        state, action = 'ready', 'advance to finalize cached discovery items'
    elif any(stages[s] for s in ('screening', 'material', 'reading', 'evidence')):
        state, action = 'awaiting_review', 'advance to retrieve the next manual packet or material request'
    else:
        proposal_holds = any(i['evidence_qualification'] and any(
            i['evidence_qualification'].get(k) == 'hold' for k in ('data_proposal', 'rq_proposal')) for i in report['items'])
        state = 'complete_with_holds' if stages['hold'] or stages['deferred'] or proposal_holds else 'complete'
        action = 'Review/export the recorded outcomes; no scientific execution is authorized'
    return {**report, 'status': state, 'mode': 'manual-pull', 'binding': binding,
            'blockers': blockers, 'next_action': action, 'item_stages': dict(stages),
            'claims': claims, 'returns': [dict(r) for r in store.db.execute(
                'SELECT id,stage,candidate_id,state,response_sha FROM workflow_returns ORDER BY rowid')] if _has(store, 'workflow_returns') else [],
            'discovery_finalized': report['discovery_complete'] and not bool(missing),
            'all_evidence_reviews_recorded': bool(report['items']) and all(i['workflow_stage'] == 'reviewed' for i in report['items']),
            'constraints': CONSTRAINTS, 'constraint_evidence_date': '2026-10-13',
            'semantic_support_verified': False, 'independent_study_count': None, **FLAGS}


def _writable(store, bid):
    row, binding = _binding(store, bid)
    if row['hold_reason']:
        raise ValueError('Workflow held: ' + row['hold_reason'])
    # Preserve the original handoff restore guard as well as this binding.
    handoff._binding(store)
    return binding


def hold(store, bid, reason):
    if not isinstance(reason, str) or not reason.strip() or len(reason) > 2000:
        raise ValueError('Explicit bounded hold reason required')
    with _exclusive(store):
        row, _ = _binding(store, bid)
        if row['hold_reason'] and row['hold_reason'] != reason:
            raise ValueError('Existing hold retained; no implicit replacement or release')
        if not row['hold_reason']:
            with store.db:
                store.db.execute('UPDATE workflow_binding SET hold_reason=?', (reason,))
                batches.event(store, bid, 'workflow-held', {'reason': reason})
        return status(store, bid)


def advance(store, bid, *, allow_network=False, client=None, fetch=None):
    """One bounded transition/packet. Reopening never repeats uncertain IO."""
    with _exclusive(store):
        binding = _writable(store, bid)
        report = status(store, bid)
        if report['status'] == 'hold':
            return report
        if not report['discovery_complete']:
            if not allow_network:
                return {**report, 'status': 'needs_network'}
            batches.run(store, bid, client)
            return status(store, bid)
        if not report['discovery_finalized']:
            batches.run(store, bid)  # Completed windows only; no new IO.
            return status(store, bid)
        active = next((c for c in report['claims'] if c['state'] != 'complete'), None)
        if active:
            return {'stage': 'screening', **handoff.packet(store, active['id']), **FLAGS}
        if report['item_stages'].get('screening'):
            return {'stage': 'screening', **handoff.claim(store, bid, binding['actor']), **FLAGS}
        for item in report['items']:
            cid, stage = item['candidate_id'], item['workflow_stage']
            if stage == 'material':
                if not allow_network:
                    return {'status': 'needs_network', 'stage': stage, 'candidate_id': cid, **FLAGS}
                result = screening.read_packet(store, bid, cid, fetch=fetch)
                return {'stage': stage, 'candidate_id': cid, 'material': result, 'status': result['status'], **FLAGS}
            if stage == 'reading':
                row = store.db.execute('SELECT reading_json FROM batch_items WHERE batch_id=? AND candidate_id=?', (bid, cid)).fetchone()
                return {'status': 'awaiting_review', 'stage': stage, 'candidate_id': cid,
                        'material': presented_result(store, json.loads(row[0])), **FLAGS}
            if stage == 'evidence':
                return {'stage': stage, **qualification.issue(store, bid, cid), **FLAGS}
        return report


def _ingest(store, bid, return_id):
    row = store.db.execute('SELECT * FROM workflow_returns WHERE id=?', (return_id,)).fetchone()
    if not row:
        raise ValueError('Unknown saved workflow return')
    response = json.loads(row['response_json'])
    if (digest(response) != row['response_sha'] or row['candidate_id'] != response.get('candidate_id')
            or return_id != 'return-' + digest({'batch_id': bid, 'stage': row['stage'], 'response': response})):
        raise ValueError('Saved workflow response changed')
    if row['stage'] == 'screening':
        result = handoff.submit(store, row['claim_id'], response)
    elif row['stage'] == 'reading':
        result = screening.submit_reading(store, bid, response)
    elif row['stage'] == 'evidence':
        result = qualification.submit(store, bid, response)
    else:
        raise ValueError('Unknown saved return stage')
    if row['state'] != 'complete':
        with store.db:
            store.db.execute("UPDATE workflow_returns SET state='complete',result_json=? WHERE id=?", (json.dumps(result), return_id))
            batches.event(store, bid, 'workflow-return-complete', {'return_id': return_id})
    return {'status': 'complete', 'return_id': return_id, 'stage': row['stage'], 'result': result, **FLAGS}


def submit(store, bid, stage, response):
    if stage not in {'screening', 'reading', 'evidence'} or not isinstance(response, dict) or len(json.dumps(response).encode()) > 1_000_000:
        raise ValueError('Known stage and response object below 1 MB required')
    with _exclusive(store):
        binding = _writable(store, bid)
        if response.get('actor') != binding['actor']:
            raise ValueError('Response actor differs from workflow label')
        rid = 'return-' + digest({'batch_id': bid, 'stage': stage, 'response': response})
        if store.db.execute('SELECT 1 FROM workflow_returns WHERE id=?', (rid,)).fetchone():
            return _ingest(store, bid, rid)
        if _pending(store):
            raise ValueError('Unresolved saved return blocks new submission')
        report = status(store, bid)
        item = next((i for i in report['items'] if i['candidate_id'] == response.get('candidate_id')), None)
        if report['status'] == 'hold' or not item or item['workflow_stage'] != stage:
            raise ValueError('Submission does not match the current workflow stage')
        claim = None
        if stage == 'screening':
            claim = next((c for c in report['claims'] if c['candidate_id'] == item['candidate_id'] and c['state'] != 'complete'), None)
            if not claim:
                raise ValueError('Issue a screening handoff first')
        elif stage == 'evidence' and not item['evidence_qualification']:
            raise ValueError('Issue an evidence packet first')
        with store.db:
            store.db.execute('INSERT INTO workflow_returns VALUES(?,?,?,?,?,?,?,NULL)',
                             (rid, stage, item['candidate_id'], claim['id'] if claim else None,
                              json.dumps(response), digest(response), 'return_pending'))
            batches.event(store, bid, 'workflow-return-saved', {'return_id': rid, 'stage': stage})
        return _ingest(store, bid, rid)


def recover(store, bid, return_id):
    with _exclusive(store):
        _writable(store, bid)
        return _ingest(store, bid, return_id)


def export(store, bid, output):
    """Private, immutable snapshot; status is derived without source retrieval."""
    report = status(store, bid)
    snapshot = {'schema_version': 1, 'exported': now(), 'private': True, 'workflow': report}
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    write_json(output / 'status.json', snapshot)
    rows = []
    for i in report['items']:
        q = i['evidence_qualification'] or {}
        assessment = i.get('evidence_review', {})
        details = [i['workflow_reason']] if i['workflow_reason'] else []
        for key in ('data', 'rq_compatibility'):
            if assessment.get(key):
                details.append(key + ': ' + assessment[key]['reason'])
        for key in ('coverage_holds', 'data_holds', 'rq_holds'):
            if q.get(key):
                details.append(key + ': ' + ', '.join(q[key]))
        cells = [i['title'], i['paper_key'], i['rq_id'], i['workflow_stage'], i['decision'],
                 i['reading_status'], q.get('data_proposal'), q.get('rq_proposal'), '; '.join(details)]
        rows.append('<tr>' + ''.join('<td>' + escape(str(c if c is not None else 'Not assessed')) + '</td>' for c in cells) + '</tr>')
    headers = ['Paper', 'Source identity', 'RQ', 'Stage', 'Reading priority', 'Material', 'Data proposal', 'RQ proposal', 'Reason / limit']
    html = '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>Weft workflow status</title><style>
body{font:16px/1.5 system-ui,sans-serif;margin:2rem;color:#182833;background:#f6f8fa}
main{max-width:1500px;margin:auto}h1{margin-bottom:.3rem}table{border-collapse:collapse;width:100%;background:white}
td,th{border:1px solid #bbc8d1;padding:.65rem;text-align:left;vertical-align:top;overflow-wrap:anywhere}
th{background:#dfebf0}.scroll{overflow-x:auto}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:white;padding:1rem}
</style><main><h1>Weft workflow status</h1><p>Private local snapshot. Proposals only; no scientific acceptance or execution.</p>'''
    html += '<p><strong>' + escape(report['status']) + '</strong> · ' + escape(snapshot['exported']) + '</p>'
    html += '<p>Discovery complete: ' + str(report['discovery_complete']) + ' · All evidence reviews recorded: ' + str(report['all_evidence_reviews_recorded']) + '</p>'
    html += '<p>' + escape(report['next_action']) + '</p><div class="scroll"><table><thead><tr>'
    html += ''.join('<th>' + h + '</th>' for h in headers) + '</tr></thead><tbody>' + ''.join(rows) + '</tbody></table></div>'
    html += '<h2>Holds and launch constraints</h2><pre>' + escape(json.dumps({'blockers': report['blockers'], 'constraints': report['constraints']}, indent=2)) + '</pre>'
    html += '<details><summary>Complete status and recovery identifiers</summary><pre>' + escape(json.dumps(report, indent=2)) + '</pre></details></main></html>'
    with (output / 'index.html').open('x', encoding='utf-8', newline='\n') as handle:
        handle.write(html)
    files = {name: hashlib.sha256((output / name).read_bytes()).hexdigest() for name in ('status.json', 'index.html')}
    # Written last: absence means the export did not complete. Never overwrite it.
    write_json(output / 'manifest.json', {'schema_version': 1, 'files': files, 'private': True})
    return {'status': 'exported', 'directory': str(output), 'files': files, 'private': True, **FLAGS}
