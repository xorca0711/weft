"""Frozen numerical checks, issue-linked critique, private view and dry handoff.

Checks validate supplied measurements and metadata. They cannot authenticate a
scientist, validate source semantics or infer biological independence/causation.
"""
from __future__ import annotations

import base64
import hashlib
import html
import math

from . import evidence as ev


def number(value, *, nonnegative=False):
    try:
        finite = type(value) in (int, float) and math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite or (nonnegative and value < 0):
        raise ValueError('Finite numeric value required')


def numerical_plan(workspace, record):
    ev.keys(record, ev.COMMON | {'article_id', 'case_id', 'contract', 'checks', 'limitations'})
    contract = workspace.bound_record(record['contract'], 'analysis-contract', case=record)
    workspace.validate(contract)
    case = workspace.bound_record(contract['case'], 'case-revision', case=record)
    source = workspace.bound_record(case['source_manifest'], 'source-manifest', case=record)
    data = workspace.bound_record(contract['feasibility'], 'data-feasibility', case=record)
    available_units = {u['unit_id'] for u in data['units'] if u['unit_id'] is not None}
    outputs = {o['path'] for o in contract['outputs'] if o['role'] == 'qc'}
    resources = {r['resource_id']: r for r in source['resources']}
    if not isinstance(record['checks'], list) or not 1 <= len(record['checks']) <= 256:
        raise ValueError('Bounded pre-specified numerical checks required')
    ids, measured = set(), set()
    for check in record['checks']:
        ev.keys(check, {'id', 'output', 'metric', 'quantity', 'expected', 'absolute_tolerance',
                        'relative_tolerance', 'arithmetic_tolerance', 'denominator', 'units',
                        'reference', 'interval_required', 'sensitivity_labels'})
        ev.text(check['id']); ev.text(check['metric'])
        pair = (check['output'], check['metric'])
        if check['id'] in ids or pair in measured or check['output'] not in outputs:
            raise ValueError('Duplicate check or unplanned QC output')
        ids.add(check['id']); measured.add(pair)
        if check['quantity'] not in {'scalar', 'proportion'}: raise ValueError('Unsupported quantity')
        number(check['arithmetic_tolerance'], nonnegative=True)
        if type(check['denominator']) is not int or not 1 <= check['denominator'] <= 2**63 - 1:
            raise ValueError('Explicit positive denominator required')
        ev.string_list(check['units'], nonempty=True)
        if not set(check['units']).issubset(available_units): raise ValueError('Invented biological unit')
        if type(check['interval_required']) is not bool: raise ValueError('Explicit interval requirement required')
        ev.string_list(check['sensitivity_labels'])
        if check['expected'] is None:
            if any(check[k] is not None for k in ('absolute_tolerance', 'relative_tolerance', 'reference')):
                raise ValueError('No target means no invented comparison tolerance/reference')
        else:
            number(check['expected'])
            for key in ('absolute_tolerance', 'relative_tolerance'): number(check[key], nonnegative=True)
            ev.keys(check['reference'], {'resource_id', 'locator', 'file_sha256'})
            cite = check['reference']; ev.text(cite['locator'])
            resource = resources.get(cite['resource_id'])
            if not resource or resource['file'] is None or cite['file_sha256'] != resource['file']['sha256']:
                raise ValueError('Numerical target lacks retained source binding')
    ev.string_list(record['limitations'], nonempty=True)
    if not set(contract['plan']['interpretation_limits']).issubset(record['limitations']):
        raise ValueError('Numerical plan drops interpretation limits')
    return {'status': 'checks-frozen', 'reference_semantics_authenticated': False, **ev.FLAGS}


def _binding(workspace, record):
    from .science_adapter import verified_receipt, load_package
    receipt = verified_receipt(workspace, record['receipt'])
    pkg, contract, plan = load_package(workspace, receipt['package'])
    if any(record[k] != contract[k] for k in ('workspace_id', 'article_id', 'case_id')):
        raise ValueError('Review case/workspace mismatch')
    return receipt, pkg, contract, plan


def validate(workspace, record):
    if record['kind'] == 'numerical-plan': return numerical_plan(workspace, record)
    if record['kind'] == 'scientific-review':
        ev.keys(record, ev.COMMON | {'article_id', 'case_id', 'receipt', 'issues', 'responses', 'interpretation'})
        receipt, _, _, plan = _binding(workspace, record)
        allowed = {canonical_ref(o['file']) for o in receipt['outputs']}
        check_ids = {c['id'] for c in plan['checks']}
        if not isinstance(record['issues'], list) or len(record['issues']) > 256: raise ValueError('Bounded issues required')
        ids = set()
        for issue in record['issues']:
            ev.keys(issue, {'id', 'check_id', 'severity', 'comment', 'evidence'})
            ev.text(issue['id']); ev.text(issue['comment'])
            if issue['id'] in ids or issue['severity'] not in {'blocking', 'limitation', 'note'}:
                raise ValueError('Duplicate issue or unknown severity')
            ids.add(issue['id'])
            if issue['check_id'] is not None and issue['check_id'] not in check_ids:
                raise ValueError('Issue links an unknown frozen check')
            if not isinstance(issue['evidence'], list): raise ValueError('Evidence references required')
            for ref in issue['evidence']:
                if canonical_ref(ref) not in allowed: raise ValueError('Issue evidence is not a returned output')
                workspace.file(ref)
        if not isinstance(record['responses'], list) or len(record['responses']) > 256:
            raise ValueError('Bounded issue responses required')
        for response in record['responses']:
            ev.keys(response, {'issue_id', 'response', 'evidence'})
            if response['issue_id'] not in ids: raise ValueError('Response has no retained issue')
            ev.text(response['response'])
            if not isinstance(response['evidence'], list): raise ValueError('Response evidence required')
            for ref in response['evidence']: workspace.file(ref)
        ev.text(record['interpretation'])
        return {'status': 'critique-recorded', 'issue_count': len(ids),
                'scientific_acceptance': False, 'identity_authenticated': False, **ev.FLAGS}
    if record['kind'] == 'owner-disposition':
        ev.keys(record, ev.COMMON | {'article_id', 'case_id', 'receipt', 'review',
                                    'disposition', 'rationale', 'decision_evidence'})
        _binding(workspace, record)
        review = workspace.bound_record(record['review'], 'scientific-review', case=record)
        workspace.validate(review)
        if review['receipt'] != record['receipt']: raise ValueError('Disposition reviews another return')
        if record['actor']['kind'] != 'human': raise ValueError('Owner disposition requires supplied human evidence')
        if record['disposition'] not in {'reading-only', 'infeasible', 'deferred', 'no-further-analysis',
                                         'review-requested', 'next-comparison-proposed', 'export-proposed'}:
            raise ValueError('Unknown disposition; canonical acceptance is not supported')
        ev.text(record['rationale']); workspace.file(record['decision_evidence'])
        return {'status': 'disposition-recorded', 'identity_authenticated': False,
                'supplied_decision_requires_owner_verification': True, **ev.FLAGS}
    raise ValueError('Unsupported scientific record')


def canonical_ref(ref):
    return ev.encoded(ref)


def qc(workspace, receipt_ref):
    from .science_adapter import verified_receipt, load_package
    receipt = verified_receipt(workspace, receipt_ref)
    pkg, contract, plan = load_package(workspace, receipt['package'])
    if receipt['outcome'] != 'fixture_completed':
        return {'status': 'hold', 'outcome': receipt['outcome'], 'receipt': receipt_ref,
                'checks': [], 'error': receipt['error'], 'scientific_validity_established': False, **ev.FLAGS}
    outputs = {o['path']: o['file'] for o in receipt['outputs']}
    tables, checks = {}, []
    for name in {c['output'] for c in plan['checks']}:
        table = workspace.file(outputs[name], parse=True)
        ev.keys(table, {'schema_version', 'metrics'})
        if table['schema_version'] != 'weft-measurements-v1' or not isinstance(table['metrics'], list):
            raise ValueError('Versioned numerical measurements required')
        if len(table['metrics']) > 256: raise ValueError('Too many metrics')
        rows = {}
        for row in table['metrics']:
            ev.keys(row, {'id', 'value', 'numerator', 'denominator', 'unit_ids', 'interval', 'sensitivity'})
            ev.text(row['id']); number(row['value'])
            if row['id'] in rows: raise ValueError('Duplicate metric')
            if type(row['denominator']) is not int or not 1 <= row['denominator'] <= 2**63 - 1: raise ValueError('Invalid denominator')
            ev.string_list(row['unit_ids'], nonempty=True)
            if row['numerator'] is not None: number(row['numerator'], nonnegative=True)
            if row['interval'] is not None:
                if not isinstance(row['interval'], list) or len(row['interval']) != 2: raise ValueError('Interval pair required')
                for value in row['interval']: number(value)
                if row['interval'][0] > row['interval'][1]: raise ValueError('Reversed uncertainty interval')
            if not isinstance(row['sensitivity'], list) or len(row['sensitivity']) > 256: raise ValueError('Bounded sensitivity data required')
            labels = set()
            for item in row['sensitivity']:
                ev.keys(item, {'label', 'value'}); ev.text(item['label']); number(item['value'])
                if item['label'] in labels: raise ValueError('Duplicate sensitivity label')
                labels.add(item['label'])
            rows[row['id']] = row
        if set(rows) != {c['metric'] for c in plan['checks'] if c['output'] == name}:
            raise ValueError('Missing or unplanned measurements; retain as an unresolved return')
        tables[name] = rows
    for check in plan['checks']:
        row = tables[check['output']][check['metric']]
        issues = []
        if row['denominator'] != check['denominator']: issues.append('denominator-mismatch')
        if set(row['unit_ids']) != set(check['units']): issues.append('biological-unit-mismatch')
        if check['quantity'] == 'proportion':
            numerator = row['numerator']
            if (type(numerator) is not int or not 0 <= numerator <= row['denominator']
                    or not 0 <= row['value'] <= 1
                    or abs(row['value'] - numerator / row['denominator']) > check['arithmetic_tolerance']):
                issues.append('proportion-arithmetic-mismatch')
        elif row['numerator'] is not None:
            issues.append('scalar-has-unplanned-numerator')
        if check['interval_required'] and row['interval'] is None: issues.append('uncertainty-missing')
        if {x['label'] for x in row['sensitivity']} != set(check['sensitivity_labels']):
            issues.append('sensitivity-inventory-mismatch')
        delta = tolerance = None
        if check['expected'] is not None:
            delta = row['value'] - check['expected']
            tolerance = check['absolute_tolerance'] + check['relative_tolerance'] * abs(check['expected'])
            number(delta); number(tolerance, nonnegative=True)
            if abs(delta) > tolerance: issues.append('reference-discrepancy')
        checks.append({'id': check['id'], 'metric': check['metric'], 'output': outputs[check['output']],
                       'observed': row, 'expected': check['expected'], 'reference': check['reference'],
                       'delta': delta, 'tolerance': tolerance, 'issues': issues})
    return {'status': 'qc-issues' if any(c['issues'] for c in checks) else 'qc-consistent',
            'exposure': pkg['exposure'], 'receipt': receipt_ref, 'checks': checks,
            'interpretation_limits': plan['limitations'], 'scientific_review_pending': True,
            'scientific_validity_established': False, **ev.FLAGS}


def _context(workspace, receipt_ref, review_ref=None, disposition_ref=None):
    from .science_adapter import verified_receipt, load_package
    receipt = verified_receipt(workspace, receipt_ref)
    pkg, contract, plan = load_package(workspace, receipt['package'])
    case = workspace.bound_record(contract['case'], 'case-revision')
    review = disposition = None
    if review_ref:
        review = workspace.bound_record(review_ref, 'scientific-review', case=case)
        workspace.validate(review)
        if review['receipt'] != receipt_ref: raise ValueError('Review refers to another receipt')
    if disposition_ref:
        disposition = workspace.bound_record(disposition_ref, 'owner-disposition', case=case)
        workspace.validate(disposition)
        if disposition['receipt'] != receipt_ref or disposition['review'] != review_ref:
            raise ValueError('Disposition binding differs from view')
    return receipt, pkg, contract, case, review, disposition


def view(workspace, receipt_ref, review_ref=None, disposition_ref=None):
    from .science_adapter import _save, _writable
    from .workflow import _exclusive
    _writable(workspace)
    receipt, pkg, contract, case, review, disposition = _context(workspace, receipt_ref, review_ref, disposition_ref)
    report = qc(workspace, receipt_ref)
    esc = lambda x: html.escape(str(x), quote=True)
    pieces = ['<!doctype html><html lang="en"><meta charset="utf-8">',
              '<meta http-equiv="Content-Security-Policy" content="default-src &#39;none&#39;; img-src data:; style-src &#39;unsafe-inline&#39;; base-uri &#39;none&#39;; form-action &#39;none&#39;">',
              '<title>Weft evidence review</title><style>body{max-width:1000px;margin:32px auto;padding:0 24px;font:16px system-ui;line-height:1.5;color:#183047;background:#f4f7fa}section{background:white;padding:24px;margin:20px 0;border-radius:8px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccd5dd;text-align:left;padding:8px}pre{white-space:pre-wrap;overflow-wrap:anywhere}img{max-width:100%}.hold{color:#8b3215}svg{max-width:100%;height:auto}a{color:#174f89}</style>',
              '<h1>Evidence review</h1><p class="hold">Synthetic fixture replay. No author code executed. No scientific acceptance.</p>',
              '<nav><a href="#question">Question</a> · <a href="#measurements">Measurements</a> · <a href="#figures">Figures</a> · <a href="#critique">Critique</a> · <a href="#decision">Decision</a> · <a href="#lineage">Lineage</a></nav>',
              '<section id="question"><h2>' + esc(case['question']) + '</h2><p>' + esc(contract['plan']['comparison']) + '</p><p>Endpoint: ' + esc(contract['plan']['endpoint']) + '</p><p>Exposure: ' + esc(case['exposure']['mode']) + '</p><p>Method: ' + esc(contract['plan']['methods']) + '</p><p>Uncertainty plan: ' + esc(contract['plan']['uncertainty']) + '</p></section>',
              '<section id="measurements"><h2>Numerical checks</h2><p>' + esc(report['status']) + '</p>']
    for index, check in enumerate(report['checks']):
        row = check['observed']
        pieces += ['<article id="check-' + str(index) + '"><h3>' + esc(check['id']) + '</h3>',
                   '<table><tr><th>Observed</th><th>Reference</th><th>Difference / tolerance</th><th>Denominator / units</th></tr><tr><td>' + esc(row['value']) + '</td><td>' + esc(check['expected']) + '</td><td>' + esc(check['delta']) + ' / ' + esc(check['tolerance']) + '</td><td>' + esc(row['denominator']) + ' / ' + esc(', '.join(row['unit_ids'])) + '</td></tr></table>',
                   '<p>Interval: ' + esc(row['interval']) + '; sensitivity: ' + esc(row['sensitivity']) + '</p>',
                   '<p class="hold">' + esc(', '.join(check['issues']) or 'No mechanical discrepancy under supplied checks') + '</p>']
        # Trusted generated graphic from verified numeric data; no author SVG/HTML.
        values = [('Observed', row['value'])]
        if check['expected'] is not None: values.append(('Reference', check['expected']))
        scale = max(abs(value) for _, value in values) or 1
        pieces.append('<svg viewBox="0 0 640 105" role="img" aria-label="Observed and reference quantities"><line x1="350" y1="0" x2="350" y2="100" stroke="#60798b"/>')
        for i, (label, value) in enumerate(values):
            width = abs(value / scale) * 240
            x = 350 if value >= 0 else 350 - width
            pieces.append(f'<text x="5" y="{25+i*45}">{esc(label)} {esc(value)}</text><rect x="{x:.3f}" y="{8+i*45}" width="{width:.3f}" height="25" fill="{["#167b84", "#b67625"][i]}"/>')
        pieces.append('</svg></article>')
    pieces.append('</section><section id="figures"><h2>Returned figures and files</h2>')
    for output in receipt['outputs']:
        ref = output['file']
        pieces.append('<p>' + esc(output['path']) + ' · SHA-256 ' + esc(ref['sha256']) + '</p>')
        if any(o['path'] == output['path'] and o['role'] == 'figure' for o in contract['outputs']):
            raw = ev.read_raw(workspace.file(ref))
            if len(raw) != ref['bytes'] or hashlib.sha256(raw).hexdigest() != ref['sha256']:
                raise ValueError('Figure changed between verification and rendering')
            mime = 'image/png' if raw.startswith(b'\x89PNG\r\n\x1a\n') else ('image/jpeg' if raw.startswith(b'\xff\xd8\xff') else None)
            if mime: pieces.append('<img alt="Verified returned figure" src="data:' + mime + ';base64,' + base64.b64encode(raw).decode('ascii') + '">')
            else: pieces.append('<p>Figure retained; active/unsupported formats are not embedded.</p>')
    pieces.append('</section><section id="critique"><h2>Interpretation and critique</h2>')
    pieces.append('<pre>' + esc('\n'.join(contract['plan']['interpretation_limits'])) + '</pre>')
    pieces.append('<pre>' + esc(ev.encoded(review).decode() if review else 'No scientific critique supplied. Numerical consistency is not scientific review.') + '</pre>')
    pieces.append('</section><section id="decision"><h2>Owner disposition</h2><pre>' + esc(ev.encoded(disposition).decode() if disposition else 'No owner disposition recorded. Review the outputs, limitations and unresolved issues.') + '</pre></section>')
    pieces.append('<section id="lineage"><h2>Immutable lineage</h2><pre>' + esc(ev.encoded({'receipt': receipt_ref, 'package': receipt['package'], 'contract': pkg['contract'], 'numerical_plan': pkg['numerical_plan'], 'closure': pkg['closure']}).decode()) + '</pre></section></html>')
    raw = ''.join(pieces).encode('utf-8')
    if len(raw) > ev.MAX_RECORD: raise ValueError('View exceeds 1 MiB; reduce embedded figures')
    with _exclusive(workspace):
        ref = _save(workspace, 'views/' + hashlib.sha256(raw).hexdigest() + '.html', raw)
    return {'status': 'private-view-created', 'view': ref, **ev.FLAGS}


def dry_export(workspace, receipt_ref, review_ref, proposed_use):
    """Allowlisted private metadata package. Never writes to Ravel or embeds sources."""
    from .science_adapter import _save, _writable
    from .workflow import _exclusive
    _writable(workspace); ev.text(proposed_use)
    receipt, pkg, contract, case, review, _ = _context(workspace, receipt_ref, review_ref)
    if review is None: raise ValueError('A retained critique is required for a handoff proposal')
    report = qc(workspace, receipt_ref)
    # Hashes bind lineage without leaking external roots, file names or full texts.
    obj = {'schema_version': 'weft-scientific-handoff-v1', 'kind': 'private-dry-proposal',
           'article_id': case['article_id'], 'case_id': case['case_id'], 'question': case['question'],
           'proposed_use': proposed_use, 'exposure': pkg['exposure'], 'outcome': receipt['outcome'],
           'qc_status': report['status'], 'interpretation_limits': contract['plan']['interpretation_limits'],
           'critique': {'interpretation': review['interpretation'],
                       'issues': [{k: issue[k] for k in ('id', 'check_id', 'severity', 'comment')} for issue in review['issues']],
                       'responses': [{k: response[k] for k in ('issue_id', 'response')} for response in review['responses']]},
           'lineage_sha256': {'package': receipt['package']['sha256'], 'receipt': receipt_ref['sha256'],
                             'review': review_ref['sha256'], 'contract': pkg['contract']['sha256'],
                             'numerical_plan': pkg['numerical_plan']['sha256'],
                             'inputs_and_sources': sorted({r['sha256'] for r in pkg['closure']})},
           'measurements': [{k: c[k] for k in ('id', 'metric', 'expected', 'delta', 'tolerance', 'issues')}
                            | {'value': c['observed']['value'], 'denominator': c['observed']['denominator'],
                               'unit_count': len(c['observed']['unit_ids']), 'interval': c['observed']['interval']}
                            for c in report['checks']],
           'integration_status': 'not-requested', 'owner_disposition': 'not-transferred',
           'ravel_write_performed': False, 'scientific_validity_established': False, **ev.FLAGS}
    raw = ev.encoded(obj)
    with _exclusive(workspace):
        ref = _save(workspace, 'exports/' + hashlib.sha256(raw).hexdigest() + '.json', raw)
    return {'status': 'dry-export-created', 'export': ref,
            'review_required_before_any_transfer': True, **ev.FLAGS}


def verify_export(path, expected_sha256):
    ev.sha(expected_sha256)
    raw = ev.read_raw(path)
    if hashlib.sha256(raw).hexdigest() != expected_sha256: raise ValueError('Export hash mismatch')
    obj = ev.decode(raw)
    ev.keys(obj, {'schema_version', 'kind', 'article_id', 'case_id', 'question', 'proposed_use',
                  'exposure', 'outcome', 'qc_status', 'interpretation_limits', 'critique',
                  'lineage_sha256', 'measurements', 'integration_status', 'owner_disposition',
                  'ravel_write_performed', 'scientific_validity_established', *ev.FLAGS})
    if (obj['schema_version'] != 'weft-scientific-handoff-v1' or obj['kind'] != 'private-dry-proposal'
            or obj['integration_status'] != 'not-requested' or obj['owner_disposition'] != 'not-transferred'
            or any(obj[key] is not False for key in ('ravel_write_performed', 'scientific_validity_established', *ev.FLAGS))):
        raise ValueError('Export authority mismatch')
    return {'status': 'dry-export-verified', 'sha256': expected_sha256,
            'verification_scope': 'exact bytes and proposal authority only; not scientific review', **ev.FLAGS}
