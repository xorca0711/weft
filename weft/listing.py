"""Owner-scoped primary reading list. Source citations do not certify meaning."""
import copy
import json
from pathlib import Path

from .identity import digest


INSTRUCTIONS = '''The primary list requires the frozen listing_policy in this packet.
Assess primary research, biological field/system/endpoint, and whether a biological
mechanism is central to the actual comparison. Explain the relationship being tested
(for example immune-niche crosstalk, metabolic rewiring or cell-fate transitions).
A shared keyword, a generic signaling claim or materials performance is insufficient.
Use a packet citation for every assessment; unknown is valid and cannot be read_next.
Do not treat a CNS journal, a claimed mechanism, or citation existence as validation.
Contrary/null findings are eligible on the same basis. Do not invent a positive result.
'''


def policy():
    value = json.loads((Path(__file__).resolve().parents[1] / 'configs/listing_policy.json').read_text(encoding='utf-8'))
    if value['id'] != 'core-biology-cns-v1' or value['clinical_exceptions']:
        raise ValueError('Listing policy change requires a reviewed new version')
    return value


def scoped_profile(profile, selected):
    """Query terms are a bounded prefilter, never a semantic relevance decision."""
    result = copy.deepcopy(profile)
    titles = selected['journals'] + selected['clinical_exceptions'] + list(selected['journal_aliases'])
    journals = '(' + ' OR '.join('JOURNAL:"' + title + '"' for title in titles) + ')'
    for stream, query in result['streams'].items():
        result['streams'][stream] = f"({query}) AND ({selected['field_query']}) AND ({selected['mechanism_query']}) AND {journals}"
    return result


def _title(value):
    return ' '.join((value or '').casefold().split())


def precheck(packet):
    selected = packet['listing_policy']
    if packet['paper_key'] in selected['excluded_papers']:
        return {'status': 'excluded', 'reason': selected['excluded_papers'][packet['paper_key']]}
    types = {p.casefold() for r in packet['records'] for p in r.get('publication_types', [])}
    if types & {'review', 'systematic review', 'meta-analysis', 'editorial', 'comment'}:
        return {'status': 'excluded', 'reason': 'Source identifies a non-primary-research publication type'}
    aliases = {_title(k): _title(v) for k, v in selected['journal_aliases'].items()}
    titles = {aliases.get(_title(r.get('journal')), _title(r.get('journal'))) for r in packet['records']}
    if not titles or '' in titles or len(titles) != 1:
        return {'status': 'hold', 'reason': 'Journal identity missing or inconsistent; no fuzzy family match'}
    if not titles <= {_title(t) for t in selected['journals'] + selected['clinical_exceptions']}:
        return {'status': 'excluded', 'reason': 'Journal outside the named primary-list allowlist'}
    return {'status': 'pending', 'reason': 'Journal matches; source-bound biological review still required'}


def template():
    return {name: {'value': 'unknown', 'reason': 'REQUIRED', 'citations': []} for name in
            ('article_type', 'field', 'study_focus', 'mechanism_centrality', 'biological_system', 'measured_endpoint', 'mechanism')}


def assess(packet, answer):
    if not isinstance(answer, dict) or set(answer) != set(template()):
        raise ValueError('Complete listing assessment required; unknown is valid')
    segments = {s['locator']: s for s in packet['segments']}
    choices = {'article_type': {'primary_research', 'review', 'other', 'unknown'},
               'field': set(packet['listing_policy']['fields']) | {'out_of_scope', 'unknown'},
               'study_focus': {'biological_mechanism', 'materials_performance', 'other', 'unknown'},
               'mechanism_centrality': {'central', 'incidental', 'unknown'}}
    for name, entry in answer.items():
        if not isinstance(entry, dict) or set(entry) != {'value', 'reason', 'citations'}:
            raise ValueError('Malformed listing assessment: ' + name)
        for key in ('value', 'reason'):
            if not isinstance(entry[key], str) or not entry[key].strip() or 'REQUIRED' in entry[key] or len(entry[key]) > 4000:
                raise ValueError('Missing or unbounded listing ' + name + ' ' + key)
        if name in choices and entry['value'] not in choices[name]:
            raise ValueError('Invalid listing ' + name)
        refs = entry['citations']
        if not isinstance(refs, list) or len(refs) > 20 or (entry['value'] != 'unknown' and not refs):
            raise ValueError('Known listing assessments need source citations')
        for ref in refs:
            if not isinstance(ref, dict) or set(ref) != {'locator', 'segment_sha256'}:
                raise ValueError('Malformed listing citation')
            segment = segments.get(ref['locator'])
            if not segment or not segment['text'] or segment['segment_sha256'] != ref['segment_sha256']:
                raise ValueError('Unresolved/empty/changed listing citation')
        if entry['value'] != 'unknown' and name != 'article_type' and not any(r['locator'].endswith('/abstractText') for r in refs):
            raise ValueError('Biological listing assessments require abstract evidence, not a title alone')
    initial = precheck(packet)
    if initial['status'] != 'pending':
        return initial
    values = {key: entry['value'] for key, entry in answer.items()}
    if (values['article_type'] in {'review', 'other'} or values['field'] == 'out_of_scope'
            or values['study_focus'] in {'materials_performance', 'other'}
            or values['mechanism_centrality'] == 'incidental'):
        return {'status': 'excluded', 'reason': 'Outside primary mechanism-focused biological research scope'}
    if 'unknown' in values.values():
        return {'status': 'hold', 'reason': 'Unresolved biological context, endpoint or central mechanism'}
    return {'status': 'eligible', 'reason': 'Source-cited screening supports reading interest only; semantic and causal validity unverified'}


def report(store, bid):
    from .batches import specification
    selected = specification(store, bid).get('listing_policy')
    rows = store.db.execute('''SELECT c.id,c.paper_key,c.status,c.current,c.proposal_json,
        bi.packet_json,bi.packet_sha,bi.result_json,bi.reason FROM batch_items bi JOIN candidates c ON c.id=bi.candidate_id
        WHERE bi.batch_id=? ORDER BY c.paper_key,c.rq_id''', (bid,)).fetchall()
    items = []
    for row in rows:
        gate = {'status': 'hold', 'reason': 'No source-bound assessment under the current listing policy'}
        if selected and row['paper_key'] in selected['excluded_papers']:
            gate = {'status': 'excluded', 'reason': selected['excluded_papers'][row['paper_key']]}
        elif selected and not row['packet_json'] and (row['reason'] or '').startswith('Primary-list '):
            reason = row['reason'].removeprefix('Primary-list ')
            state, detail = reason.split(': ', 1)
            gate = {'status': state if state in {'hold', 'excluded'} else 'hold', 'reason': detail}
        elif selected and row['packet_json']:
            packet = json.loads(row['packet_json'])
            if digest(packet) != row['packet_sha'] or packet.get('listing_policy') != selected:
                raise ValueError('Listing packet/policy changed')
            gate = precheck(packet)
            if row['result_json']:
                response = json.loads(row['result_json'])
                if response['packet_sha256'] != row['packet_sha']:
                    raise ValueError('Listing response differs from frozen packet')
                gate = assess(packet, response['listing_assessment'])
                if gate['status'] == 'eligible' and response['decision'] != 'read_next':
                    gate = {'status': 'hold', 'reason': 'Reading decision is not read_next'}
                if gate['status'] == 'eligible':
                    from .screening import live_candidate
                    try:
                        live_candidate(store, packet)
                        latest = store.db.execute('SELECT record_json FROM events WHERE candidate_id=? ORDER BY id DESC LIMIT 1', (row['id'],)).fetchone()
                        if not latest or json.loads(latest[0]).get('screening_response_sha256') != digest(response):
                            raise ValueError('Reading decision changed outside the screened response')
                    except ValueError as exc:
                        gate = {'status': 'hold', 'reason': str(exc)}
        if (not row['current'] or row['status'] != 'read_next'
                or json.loads(row['proposal_json'])['hold_reasons']):
            if gate['status'] == 'eligible':
                gate = {'status': 'hold', 'reason': 'Current candidate disposition/identity hold retained'}
        items.append({'candidate_id': row['id'], 'paper_key': row['paper_key'], **gate})
    return {'policy_id': selected['id'] if selected else None,
            'primary_list': [i for i in items if i['status'] == 'eligible'], 'audit': items,
            'scope': 'Reading recommendations; excluded records retained; no scientific acceptance',
            'claim_validated': False, 'scientific_execution_allowed': False}


def require_admission(store, cid):
    """The manual reader cannot bypass an existing scoped batch's screening."""
    standalone = False
    for row in store.db.execute('SELECT r.receipt_json FROM runs r JOIN candidate_runs cr ON cr.run_id=r.id WHERE cr.candidate_id=?', (cid,)):
        receipt = json.loads(row[0]) if row[0] else {}
        if receipt.get('listing_policy'):
            if digest(receipt['listing_policy']) != receipt.get('listing_policy_sha256'):
                raise ValueError('Standalone discovery listing-policy binding changed')
            standalone = True
    if not store.db.execute("SELECT 1 FROM sqlite_master WHERE name='batch_items'").fetchone():
        if standalone:
            raise ValueError('Source-screened primary-list admission required; use a scoped batch before reading')
        return
    rows = store.db.execute('SELECT b.id,b.spec_json FROM batches b JOIN batch_items bi ON bi.batch_id=b.id WHERE bi.candidate_id=?', (cid,)).fetchall()
    scoped = [r['id'] for r in rows if json.loads(r['spec_json']).get('listing_policy')]
    if (scoped or standalone) and not any(any(i['candidate_id'] == cid for i in report(store, bid)['primary_list']) for bid in scoped):
        raise ValueError('Source-screened primary-list admission required; manual read_next cannot bypass it')
