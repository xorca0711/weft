"""Versioned nomination order and bibliography accounting, never relevance labels.

Stream membership describes the query that retrieved a record. It does not
establish that a paper is contrary, relevant, independent or analysis-ready.
"""
from collections import Counter, defaultdict
import json

from .identity import digest

POLICY = {'id': 'paper-stream-v1', 'stream_order': ['rq_contrary', 'adjacent_context', 'broad'],
          'paper_rounds': True, 'rq_tie_break': 'fewest links nominated, then rq_id',
          'paper_tie_break': 'paper_key', 'scope': 'query coverage and paper diversity only'}


def policy(name):
    if name != POLICY['id']:
        raise ValueError('Unknown selection policy')
    return json.loads(json.dumps(POLICY))


def _inputs(store, bid):
    rows = store.db.execute('''SELECT c.id,c.paper_key,c.rq_id,c.context_sha,c.evidence_sha,c.proposal_json
        FROM batch_items bi JOIN candidates c ON c.id=bi.candidate_id WHERE bi.batch_id=?
        ORDER BY c.paper_key,c.rq_id,c.id''', (bid,)).fetchall()
    items = []
    for row in rows:
        sources = [dict(r) for r in store.db.execute('''SELECT DISTINCT w.stream,w.run_id FROM batch_windows w
            JOIN candidate_runs cr ON cr.run_id=w.run_id WHERE w.batch_id=? AND cr.candidate_id=?
            AND w.status='complete' ORDER BY w.stream,w.run_id''', (bid, row['id']))]
        proposal = json.loads(row['proposal_json'])
        items.append({'candidate_id': row['id'], 'paper_key': row['paper_key'], 'rq_id': row['rq_id'],
                      'context_sha256': row['context_sha'], 'evidence_sha256': row['evidence_sha'],
                      'sources': sources, 'streams': sorted({r['stream'] for r in sources}),
                      'hold_reasons': proposal['hold_reasons']})
    return items


def _ordered(items):
    groups = defaultdict(list)
    held = []
    for item in items:
        if item['hold_reasons']:
            held.append({**item, 'reason': 'Existing identity/integrity hold retained'})
        else:
            groups[item['paper_key']].append(item)
    ordered, rq_counts = [], Counter()
    # Each round admits at most one link per paper. Stream rotation restarts each
    # round; shared stream membership never duplicates a paper within the round.
    while groups:
        available = set(groups)
        while available:
            progressed = False
            for stream in POLICY['stream_order']:
                choices = [key for key in sorted(available) if any(stream in i['streams'] for i in groups[key])]
                if not choices:
                    continue
                key = choices[0]
                item = min((i for i in groups[key] if stream in i['streams']),
                           key=lambda i: (rq_counts[i['rq_id']], i['rq_id'], i['candidate_id']))
                ordered.append({**item, 'reason': 'Paper round; query stream ' + stream})
                rq_counts[item['rq_id']] += 1
                groups[key].remove(item)
                if not groups[key]:
                    del groups[key]
                available.remove(key)
                progressed = True
            if not progressed:
                raise ValueError('Candidate lacks a supported completed query stream')
    return [{**item, 'rank': n + 1} for n, item in enumerate(ordered + held)]


def _build(store, bid):
    from .batches import specification
    spec = specification(store, bid)
    configured = spec.get('selection_policy')
    if configured != policy(configured.get('id') if isinstance(configured, dict) else None):
        raise ValueError('Frozen selection policy differs from its supported version')
    windows = store.db.execute('SELECT status FROM batch_windows WHERE batch_id=?', (bid,)).fetchall()
    if not windows or any(w[0] not in {'complete', 'split'} for w in windows):
        raise ValueError('Complete discovery required for selection')
    items = _inputs(store, bid)
    return {'schema_version': 1, 'batch_id': bid, 'policy': configured,
            'input_sha256': digest(items), 'baseline_order': [i['candidate_id'] for i in items],
            'items': _ordered(items), 'scientific_execution_allowed': False,
            'relevance_validated': False, 'independent_study_count': None}


def plan(store, bid):
    built = _build(store, bid)
    exists = store.db.execute("SELECT 1 FROM sqlite_master WHERE name='batch_selections'").fetchone()
    row = store.db.execute('SELECT * FROM batch_selections WHERE batch_id=?', (bid,)).fetchone() if exists else None
    if not row:
        return {**built, 'status': 'preview', 'plan_sha256': digest(built)}
    saved = json.loads(row['plan_json'])
    if digest(saved) != row['plan_sha'] or saved != built:
        raise ValueError('Selection inputs or frozen plan changed; no implicit reranking')
    return {**saved, 'status': 'frozen', 'plan_sha256': row['plan_sha']}


def freeze(store, bid):
    """Caller owns the existing batch lock; no nested lock or historical rewrite."""
    from .batches import event
    result = plan(store, bid)
    if result['status'] == 'frozen':
        return result
    store.db.execute('''CREATE TABLE IF NOT EXISTS batch_selections(
        batch_id TEXT PRIMARY KEY REFERENCES batches(id), plan_json TEXT NOT NULL, plan_sha TEXT NOT NULL)''')
    saved = {k: v for k, v in result.items() if k not in {'status', 'plan_sha256'}}
    with store.db:
        store.db.execute('INSERT INTO batch_selections VALUES(?,?,?)', (bid, json.dumps(saved), result['plan_sha256']))
        event(store, bid, 'selection-frozen', {'plan_sha256': result['plan_sha256'], 'policy': POLICY['id']})
    return {**result, 'status': 'frozen'}


def _account(items):
    return {'links': len(items), 'unique_papers': len({i['paper_key'] for i in items}),
            'rq_links': dict(sorted(Counter(i['rq_id'] for i in items).items())),
            'query_stream_links': dict(sorted(Counter(s for i in items for s in i['streams']).items())),
            'paper_keys': sorted({i['paper_key'] for i in items})}


def report(store, bid, *, reference=None, include_plan=False):
    from .batches import specification
    spec = specification(store, bid)
    if not spec.get('selection_policy'):
        return {'status': 'legacy', 'policy': spec['selection'], 'relevance_validated': False}
    if any(r[0] not in {'complete', 'split'} for r in store.db.execute('SELECT status FROM batch_windows WHERE batch_id=?', (bid,))):
        return {'status': 'not_ready', 'policy': spec['selection_policy'], 'relevance_validated': False}
    frozen = plan(store, bid)
    items = frozen['items']; by_id = {i['candidate_id']: i for i in items}
    cap = spec['max_screenings']
    nominal = [i for i in items if not i['hold_reasons']][:cap]
    baseline = [by_id[c] for c in frozen['baseline_order'] if not by_id[c]['hold_reasons']][:cap]
    actual_ids = {r[0] for r in store.db.execute('SELECT candidate_id FROM batch_items WHERE batch_id=? AND packet_json IS NOT NULL', (bid,))}
    actual = [i for i in items if i['candidate_id'] in actual_ids]
    result = {'status': frozen['status'], 'policy': frozen['policy'], 'plan_sha256': frozen['plan_sha256'],
              'screening_cap': cap, 'universe': _account(items), 'nominal_policy': _account(nominal),
              'nominal_baseline': _account(baseline), 'actual_issued': _account(actual),
              'held_links': [i['candidate_id'] for i in items if i['hold_reasons']],
              'scope': 'Nominal budget comparison excludes known integrity holds; actual validated issuance is separate.',
              'relevance_validated': False, 'independent_study_count': None, 'scientific_execution_allowed': False}
    if include_plan:
        result['plan'] = frozen
    if reference is not None:
        if (not isinstance(reference, dict) or set(reference) != {'schema_version', 'provenance', 'prior_exposure', 'paper_keys'}
                or type(reference['schema_version']) is not int or reference['schema_version'] != 1
                or any(not isinstance(reference[k], str) or not reference[k].strip() for k in ('provenance', 'prior_exposure'))
                or not isinstance(reference['paper_keys'], list) or not 1 <= len(reference['paper_keys']) <= 10000
                or any(not isinstance(k, str) or not k.strip() or len(k) > 1000 for k in reference['paper_keys'])
                or len(set(reference['paper_keys'])) != len(reference['paper_keys'])):
            raise ValueError('Bounded unique reference paper keys, provenance and prior exposure required')
        keys = set(reference['paper_keys'])
        accounting = {}
        for name in ('universe', 'nominal_policy', 'nominal_baseline', 'actual_issued'):
            found = keys & set(result[name]['paper_keys'])
            accounting[name] = {'matched': len(found), 'reference_denominator': len(keys),
                                'missing_from_this_set': sorted(keys - found)}
        result['reference_audit'] = {'reference_sha256': digest(reference), 'provenance': reference['provenance'],
            'prior_exposure': reference['prior_exposure'], 'accounting': accounting,
            'interpretation': 'Coverage of the supplied bibliography only; not population recall, relevance accuracy or independent evaluation.',
            'reference_independence_verified': False}
    return result
