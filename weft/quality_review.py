"""Private critic-to-human development review, separate from independent B5 scoring.

No model invocation, source retrieval, store mutation or reference-label conversion.
Human adjudication assisted by a critic is deliberately not an independent reference.
"""
from html import escape
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import quote, urlsplit

from . import evaluation as e
from .discovery import now, write_json
from .materials import _local_file

MODE = 'ai_assisted_adjudication'
CATEGORIES = {'citation_support', 'biological_unit', 'controls', 'endpoint', 'data_access',
              'lineage', 'rq_fit', 'missing_material'}
FLAGS = {**e.FLAGS, 'independent_reference': False, 'blind_to_agent': False,
         'semantic_support_verified': False}
RESERVED = {'packet.json', 'human-response-template.json', 'report.json', 'human-response.json',
            'review.md', 'index.html', 'manifest.json'}


def pointer(document, locator):
    """Resolve an exact JSON pointer in the retained metadata, never execute text."""
    if not isinstance(locator, str) or not locator.startswith('/'):
        raise ValueError('Exact source JSON pointer required')
    value = document
    try:
        for part in locator[1:].split('/'):
            part = part.replace('~1', '/').replace('~0', '~')
            if isinstance(value, list):
                if not part.isdecimal() or str(int(part)) != part:
                    raise ValueError('Canonical nonnegative array index required')
                value = value[int(part)]
            elif isinstance(value, dict):
                value = value[part]
            else:
                raise ValueError('Source locator traverses a scalar')
    except (KeyError, IndexError) as exc:
        raise ValueError('Source locator does not exist') from exc
    if value is None or value == '' or value == [] or value == {}:
        raise ValueError('Source locator is empty')
    return value


def load(packet_path):
    path = Path(packet_path)
    if not path.is_file() or path.is_symlink() or path.stat().st_size > 1_000_000:
        raise ValueError('Regular review packet below 1 MB required')
    packet = json.loads(path.read_text(encoding='utf-8'))
    e._keys(packet, {'schema_version', 'review_id', 'created_at', 'kind', 'mode', 'scope',
                     'sampling', 'critic', 'cases'}, 'quality packet')
    if (type(packet['schema_version']) is not int or packet['schema_version'] != 1
            or not isinstance(packet['kind'], str) or packet['kind'] not in {'synthetic', 'development'} or packet['mode'] != MODE):
        raise ValueError('Only explicit synthetic/development assisted review is supported')
    e._text(packet['review_id'], 'review ID'); e._text(packet['scope'], 'scope')
    e._time(packet['created_at'], 'packet creation')
    e._keys(packet['sampling'], {'universe_locator', 'universe_sha256', 'selection_method', 'coverage_limits'}, 'sampling')
    for key, value in packet['sampling'].items():
        (e._sha if key.endswith('sha256') else e._text)(value, key)
    e._keys(packet['critic'], {'actor', 'actor_kind', 'prior_exposure', 'limits'}, 'critic')
    if packet['critic']['actor_kind'] != 'agent' or packet['critic']['prior_exposure'] != 'exposed':
        raise ValueError('Explicit exposed AI critic required; never a human reference')
    e._text(packet['critic']['actor'], 'critic actor'); e._text(packet['critic']['limits'], 'critic limits')
    if not isinstance(packet['cases'], list) or not 1 <= len(packet['cases']) <= 25:
        raise ValueError('One to 25 explicit review cases required')
    sources, seen, paths = {}, set(), {}
    for case in packet['cases']:
        e._keys(case, {'case_id', 'paper_key', 'rq_context', 'historical_decisions', 'source', 'findings', 'human_questions'}, 'case')
        for key in ('case_id', 'paper_key', 'rq_context', 'historical_decisions'):
            e._text(case[key], key)
        if case['case_id'] in seen:
            raise ValueError('Duplicate case ID')
        seen.add(case['case_id'])
        source = case['source']
        e._keys(source, {'path', 'sha256', 'url', 'scope', 'accessed_at'}, 'source')
        e._sha(source['sha256'], 'source hash'); e._text(source['scope'], 'source scope')
        e._time(source['accessed_at'], 'source access')
        e._text(source['url'], 'source URL')
        url = urlsplit(source['url'])
        if url.scheme != 'https' or not url.hostname or url.username or url.password:
            raise ValueError('Explicit public HTTPS source URL required')
        if not isinstance(source['path'], str):
            raise ValueError('Portable relative source path required')
        parts = source['path'].split('/')
        devices = {'con', 'prn', 'aux', 'nul'} | {p + str(n) for p in ('com', 'lpt') for n in range(1, 10)}
        if any(not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9 ._#-]*', p) or p != p.rstrip(' .')
               or p.split('.')[0].casefold() in devices for p in parts):
            raise ValueError('Canonical portable source path components required')
        if parts[0].casefold() in RESERVED:
            raise ValueError('Source path collides with a reserved export filename')
        alias = source['path'].casefold()
        if alias in paths and paths[alias] != source['path']:
            raise ValueError('Source path aliases another case on case-insensitive filesystems')
        paths[alias] = source['path']
        local = _local_file(path.resolve().parent, source['path'])
        with local.open('rb') as handle:
            body = handle.read(1_000_001)
        if len(body) > 1_000_000 or hashlib.sha256(body).hexdigest() != source['sha256']:
            raise ValueError('Source snapshot changed or exceeds 1 MB')
        document = json.loads(body)
        records = pointer(document, '/resultList/result')
        if (not isinstance(records, list) or len(records) != 1 or not isinstance(records[0], dict)
                or not isinstance(records[0].get('doi'), str) or 'doi:' + records[0]['doi'].lower() != case['paper_key']):
            raise ValueError('One exact DOI metadata record required per case')
        sources[case['case_id']] = (body, document)
        if not isinstance(case['findings'], list) or not 1 <= len(case['findings']) <= 20:
            raise ValueError('Bounded explicit critic findings required')
        findings = set()
        for finding in case['findings']:
            e._keys(finding, {'finding_id', 'category', 'assessment', 'statement', 'locators'}, 'finding')
            e._text(finding['finding_id'], 'finding ID'); e._text(finding['statement'], 'finding statement')
            e._text(finding['category'], 'finding category'); e._text(finding['assessment'], 'finding assessment')
            if finding['finding_id'] in findings:
                raise ValueError('Duplicate finding ID within case')
            findings.add(finding['finding_id'])
            if finding['category'] not in CATEGORIES or finding['assessment'] not in {'supported', 'concern', 'not_assessed'}:
                raise ValueError('Unknown critic finding category/assessment')
            if not isinstance(finding['locators'], list) or not finding['locators']:
                raise ValueError('Source locators required, including for scope limitations')
            for locator in finding['locators']:
                pointer(document, locator)
        if not isinstance(case['human_questions'], list) or not case['human_questions']:
            raise ValueError('Human review questions required')
        for question in case['human_questions']:
            e._text(question, 'human question')
    return packet, sources


def template(packet):
    return {'schema_version': 1, 'review_id': packet['review_id'], 'packet_sha256': e.fingerprint(packet),
            'mode': MODE, 'actor': None, 'actor_kind': 'human', 'created_at': None,
            'independent_reference': False, 'blind_to_agent': False, 'prior_exposure': 'exposed',
            'cases': [{'case_id': c['case_id'], 'judgments': {d: {'label': None,
                'reason': 'Awaiting your judgment; uncertainty may remain', 'locators': []} for d in e.LABELS},
                'findings': [{'finding_id': f['finding_id'], 'decision': None,
                             'reason': 'Awaiting your review'} for f in c['findings']]} for c in packet['cases']]}


def adjudicate(packet, sources, response=None):
    result = {'schema_version': 1, 'review_id': packet['review_id'], 'packet_sha256': e.fingerprint(packet),
              'mode': MODE, 'kind': packet['kind'], 'case_count': len(packet['cases']),
              'unique_papers': len({c['paper_key'] for c in packet['cases']}), 'independent_study_count': None,
              'independent_reference_records': 0, 'quality_metrics': None,
              'model_invocation_scope': 'This exporter only; the supplied critique is AI-authored.',
              'limits': ['Critic statements are proposals; locator integrity does not establish semantic support.',
                         'AI-assisted human decisions are not independent reference labels.',
                         'No live candidate, hold, threshold, or scientific authority changes.'], **FLAGS}
    if response is None:
        return {**result, 'status': 'awaiting_human_adjudication', 'recorded_labels': 0,
                'missing_labels': 3 * len(packet['cases']), 'unresolved_findings': sum(len(c['findings']) for c in packet['cases'])}
    expected = template(packet)
    e._keys(response, expected, 'human adjudication')
    for key in ('schema_version', 'review_id', 'packet_sha256', 'mode', 'actor_kind', 'independent_reference', 'blind_to_agent', 'prior_exposure'):
        if type(response[key]) is not type(expected[key]) or response[key] != expected[key]:
            raise ValueError('Adjudication identity/mode differs: ' + key)
    e._text(response['actor'], 'human actor')
    if response['actor'] == packet['critic']['actor']:
        raise ValueError('Critic cannot impersonate the human adjudicator')
    if e._time(response['created_at'], 'adjudication creation') < e._time(packet['created_at'], 'packet creation'):
        raise ValueError('Adjudication predates this packet')
    if not isinstance(response['cases'], list) or len(response['cases']) != len(packet['cases']):
        raise ValueError('Every case must remain represented, including unresolved ones')
    cases = {c['case_id']: c for c in packet['cases']}; seen = set()
    labels = unresolved = disagreements = 0
    for answer in response['cases']:
        e._keys(answer, {'case_id', 'judgments', 'findings'}, 'case adjudication')
        cid = answer['case_id']
        e._text(cid, 'adjudicated case ID')
        if cid not in cases or cid in seen:
            raise ValueError('Unknown or duplicate adjudicated case')
        seen.add(cid); case = cases[cid]; document = sources[cid][1]
        e._keys(answer['judgments'], e.LABELS, 'separate human judgments')
        for dimension, judgment in answer['judgments'].items():
            e._keys(judgment, {'label', 'reason', 'locators'}, 'human judgment')
            if judgment['label'] is not None and judgment['label'] not in e.LABELS[dimension]:
                raise ValueError('Unknown judgment label')
            e._text(judgment['reason'], 'judgment or missingness reason')
            if not isinstance(judgment['locators'], list) or (judgment['label'] is not None and not judgment['locators']):
                raise ValueError('Known human judgments need source locators')
            for locator in judgment['locators']:
                pointer(document, locator)
            labels += judgment['label'] is not None
        expected_ids = {f['finding_id'] for f in case['findings']}; actual_ids = set()
        if not isinstance(answer['findings'], list):
            raise ValueError('Finding adjudications required')
        for finding in answer['findings']:
            e._keys(finding, {'finding_id', 'decision', 'reason'}, 'human finding')
            e._text(finding['finding_id'], 'adjudicated finding ID')
            if finding['finding_id'] not in expected_ids or finding['finding_id'] in actual_ids:
                raise ValueError('Unknown or duplicate finding adjudication')
            actual_ids.add(finding['finding_id'])
            if finding['decision'] not in (None, 'agree', 'disagree', 'uncertain'):
                raise ValueError('Unknown finding disposition')
            e._text(finding['reason'], 'finding reason')
            unresolved += finding['decision'] in (None, 'uncertain')
            disagreements += finding['decision'] == 'disagree'
        if actual_ids != expected_ids:
            raise ValueError('All critic findings must remain represented')
    missing = 3 * len(cases) - labels
    return {**result, 'status': 'recorded_with_unresolved' if missing or unresolved else 'adjudication_recorded',
            'response_sha256': e.fingerprint(response), 'recorded_labels': labels, 'missing_labels': missing,
            'unresolved_findings': unresolved, 'human_disagreements_with_critic': disagreements}


def export(packet_path, output, response=None):
    packet, sources = load(packet_path)
    report = adjudicate(packet, sources, response)
    root = Path(output).resolve(); root.mkdir(parents=True, exist_ok=False)
    write_json(root / 'packet.json', packet)
    write_json(root / 'human-response-template.json', template(packet))
    write_json(root / 'report.json', report)
    if response is not None:
        write_json(root / 'human-response.json', response)
    text = ['# Weft: critic-to-human review', '', packet['scope'], '',
            '**AI-assisted development adjudication. Independent scientific-quality evaluation remains pending.**', '',
            'Read the evidence and record your own reasons. You may disagree or leave uncertainty unresolved.', '',
            'The blank response template records separate reading, data-use and RQ judgments; no answer is preselected.', '']
    html = ['<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
            '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; base-uri \'none\'">',
            '<title>Weft human adjudication</title><style>body{font:16px/1.6 system-ui;margin:2rem auto;padding:0 1rem;max-width:960px;color:#182a38}section{border-top:1px solid #ccd6df;margin-top:2rem}pre{white-space:pre-wrap;overflow-wrap:anywhere}a{color:#076490}</style>',
            '<h1>Weft: critic-to-human review</h1><p>AI-assisted, exposed development review. Independent scientific-quality evaluation remains pending.</p>',
            '<p>' + escape(packet['scope']) + '</p><p>No human answers are preselected. You may disagree or retain uncertainty.</p>']
    files = {}
    answers = {c['case_id']: c for c in response['cases']} if response else {}
    for case in packet['cases']:
        name = case['source']['path']; body = sources[case['case_id']][0]
        target = root / name; target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            with target.open('xb') as handle: handle.write(body)
        files[name] = hashlib.sha256(target.read_bytes()).hexdigest()
        if files[name] != case['source']['sha256']:
            raise ValueError('Exported source differs on readback')
        text += [f'## {case["case_id"]}: {case["paper_key"]}', '', case['rq_context'], '',
                 'Historical decisions: ' + case['historical_decisions'], '',
                 f'Source: {case["source"]["url"]}', 'Reviewed scope: ' + case['source']['scope'], '']
        html += ['<section><h2>' + escape(case['case_id'] + ': ' + case['paper_key']) + '</h2>',
                 '<p>' + escape(case['rq_context']) + '</p><p>Historical decisions: ' + escape(case['historical_decisions']) + '</p>',
                 '<p><a href="' + escape(case['source']['url'], quote=True) + '">Primary source</a> · <a href="' + quote(name, safe='/') + '">Retained metadata</a></p>',
                 '<p>Reviewed scope: ' + escape(case['source']['scope']) + '</p>']
        answer = answers.get(case['case_id'])
        human_findings = {f['finding_id']: f for f in answer['findings']} if answer else {}
        for finding in case['findings']:
            line = finding['finding_id'] + ' · ' + finding['category'] + ' · ' + finding['assessment'] + ': ' + finding['statement']
            text += [line, 'Source locators: ' + ', '.join(finding['locators']), '']
            html += ['<h3>' + escape(finding['finding_id'] + ' · ' + finding['category']) + '</h3><p><strong>' + escape(finding['assessment']) + '</strong>: ' + escape(finding['statement']) + '</p>',
                     '<p>Source locators: ' + escape(', '.join(finding['locators'])) + '</p>']
            if finding['finding_id'] in human_findings:
                human = human_findings[finding['finding_id']]
                line = 'Human adjudication: ' + (human['decision'] or 'unresolved') + ' — ' + human['reason']
                text += [line, '']; html += ['<p><strong>' + escape(line) + '</strong></p>']
        if answer:
            text += ['### Recorded human judgments', '', 'Actor: ' + response['actor'], '']
            html += ['<h3>Recorded human judgments</h3><p>Actor: ' + escape(response['actor']) + '</p>']
            for dimension, judgment in answer['judgments'].items():
                line = dimension + ': ' + (judgment['label'] or 'unresolved') + ' — ' + judgment['reason']
                locator_text = 'Source locators: ' + ', '.join(judgment['locators'])
                text += [line, locator_text, '']; html += ['<p>' + escape(line) + '<br>' + escape(locator_text) + '</p>']
        text += ['### Your decisions', ''] + ['- ' + q for q in case['human_questions']] + ['']
        html += ['<h3>Your decisions</h3><ul>' + ''.join('<li>' + escape(q) + '</li>' for q in case['human_questions']) + '</ul></section>']
    html += ['<h2>Accounting</h2><pre>' + escape(json.dumps(report, indent=2)) + '</pre>']
    (root / 'review.md').write_text('\n'.join(text), encoding='utf-8')
    (root / 'index.html').write_text('\n'.join(html), encoding='utf-8')
    for path in root.iterdir():
        if path.is_file(): files[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
    write_json(root / 'manifest.json', {'schema_version': 1, 'private': True, 'exported_at': now(), 'files': files,
                                      'packet_sha256': e.fingerprint(packet)})
    return {**report, 'directory': str(root), 'private': True}
