"""Private static review bundle: source locators, coverage and separate proposals."""
from html import escape
import hashlib
import json
from pathlib import Path

from . import materials, qualification
from .discovery import now, write_json
from .identity import digest


def _text(value):
    return escape(str(value if value is not None else 'Unknown'))


def _table(headers, rows):
    return '<div class="scroll"><table><thead><tr>' + ''.join('<th>' + _text(h) + '</th>' for h in headers) + '</tr></thead><tbody>' + ''.join(
        '<tr>' + ''.join('<td>' + cell + '</td>' for cell in row) + '</tr>' for row in rows) + '</tbody></table></div>'


def export(store, bid, cid, output, *, include_materials=False):
    dossier = materials.inventory(store, bid, cid)
    dossier['exported'] = now()
    dossier['copied_materials'] = include_materials
    root = Path(output).resolve()
    root.mkdir(parents=True, exist_ok=False)
    files = {}
    # Source assets are never copied implicitly. Every copied object is checked
    # again after readback; the manifest is written only after all copies succeed.
    if include_materials:
        for resource in dossier['resources']:
            for asset in resource['attachments']:
                if asset['status'] != 'verified_bytes':
                    raise ValueError('Held attachment cannot be included in a review bundle')
                relative = 'assets/' + asset['sha256'] + '.' + asset['format']
                target = root / relative
                target.parent.mkdir(exist_ok=True)
                body = qualification._blob_path(store, asset['sha256']).read_bytes()
                if len(body) != asset['bytes'] or hashlib.sha256(body).hexdigest() != asset['sha256']:
                    raise ValueError('Material changed while exporting')
                if not target.exists():
                    with target.open('xb') as handle:
                        handle.write(body)
                files[relative] = hashlib.sha256(target.read_bytes()).hexdigest()
                if files[relative] != asset['sha256']:
                    raise ValueError('Exported material readback differs')
                asset['export_path'] = relative
    packet = dossier['packet']
    sections = {s['locator']: ('source-' + digest(s['locator']), s) for s in packet['segments']}

    def citations(refs):
        return '<br>'.join('<a href="#' + sections[r['locator']][0] + '">' + _text(r['locator']) + '</a>' for r in refs)

    content = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>Weft evidence review</title><style>
body{font:16px/1.55 system-ui,sans-serif;color:#172a36;background:#f6f8fa;margin:2rem}
main{max-width:1200px;margin:auto}table{border-collapse:collapse;width:100%;background:white}th,td{border:1px solid #bfccd5;padding:.6rem;text-align:left;vertical-align:top}
th{background:#dfebf0}pre,td,p{overflow-wrap:anywhere}pre{white-space:pre-wrap;background:white;padding:1rem}
.scroll{overflow-x:auto}a{color:#075c8e}section{margin:2rem 0}h1{margin-bottom:.2rem}
</style><main><h1>Weft evidence review</h1>
<p>Private source bundle. Attached bytes, inspection assertions and scientific support are separate.</p>
<nav><a href="#proposals">Proposals</a> · <a href="#coverage">Materials</a> · <a href="#source">Source text</a> · <a href="#provenance">Provenance</a></nav>'''
    content += '<p>Paper: ' + _text(packet['paper_key']) + ' · RQ: ' + _text(packet['rq_context']['rq_id']) + '</p>'
    summary = dossier['summary'] or {}
    content += '<p>Review state: <strong>' + _text(summary.get('status')) + '</strong> · Current: ' + _text(summary.get('current')) + '</p>'
    record = dossier['assessment']
    content += '<section id="proposals"><h2>Separate proposals</h2>'
    if record:
        data, rq = record['data'], record['rq_compatibility']
        content += _table(['Decision', 'Proposal', 'Reason'], [
            ['Data use', _text(data['recommendation']), _text(data['reason'])],
            ['RQ compatibility', _text(rq['recommendation']), _text(rq['reason'])]])
        content += _table(['Data-use field', 'Recorded value'], [[_text(k.replace('_', ' ')), _text(data[k])] for k in (
            'purpose', 'comparison', 'measured_endpoint', 'biological_unit', 'inference', 'independent_units', 'controls', 'access')])
        content += '<p>Data-use citations: ' + citations(data['citations']) + '</p>'
        content += _table(['Dataset', 'Files', 'Unit mapping', 'Cohort / source relationship', 'Citations'], [
            [_text(d['accession']), _text(', '.join(d['file_identifiers'])), _text(d['unit_mapping']),
             _text(str(d['cohort']) + ' / ' + d['source_relationship']), citations(d['citations'])] for d in data['datasets']])
        content += _table(['RQ dimension', 'Match', 'Source / target', 'Citations'], [
            [_text(k), _text(v['status']), _text(v['source_description'] + ' / ' + v['target_description']), citations(v['citations'])]
            for k, v in rq['dimensions'].items()])
        content += '<p>Limitations: ' + _text('; '.join(record['limitations'])) + '</p>'
        content += '<p>Actor: ' + _text(record['actor']) + ' · Prior exposure: ' + _text(record['prior_exposure']) + '</p>'
    else:
        content += '<p>No current validated proposal record. Missing values remain unknown.</p>'
    content += '<pre>' + _text(json.dumps(summary, indent=2)) + '</pre></section>'
    content += '<section id="coverage"><h2>Material coverage</h2><p>Source references are shown as text; no external URL is fetched or embedded. Opening a file does not record inspection.</p>'
    for resource in dossier['resources']:
        content += '<h3>' + _text(resource['label']) + ' (' + _text(resource['kind']) + ')</h3><p>' + _text(resource['locator']) + '</p>'
        content += '<p>Caption: ' + _text(resource['caption']) + '</p><p>Source references: ' + _text('; '.join(resource['hrefs'])) + '</p>'
        coverage = resource['coverage']
        content += '<p>Recorded coverage: <strong>' + _text(coverage['status']) + '</strong> — ' + _text(coverage['inspection_note']) + '</p>'
        rows = []
        for asset in resource['attachments']:
            link = '<a href="' + _text(asset['export_path']) + '" rel="noopener">Open supplied material</a>' if asset.get('export_path') else 'Not copied'
            rows.append([_text(asset['artifact_id']), _text(asset['status']), _text(asset.get('reason', '')), _text(asset.get('origin')), link])
        content += _table(['Artifact ID', 'Byte verification', 'Hold reason', 'Declared origin', 'Local material'], rows)
    content += '</section><section id="source"><h2>Source text and reading assertions</h2>'
    for statement in dossier['reading_assessment']['statements']:
        content += '<p>' + _text(statement['text']) + ' — ' + citations([statement]) + '</p>'
    for locator, (anchor, segment) in sections.items():
        content += '<details id="' + anchor + '" open><summary>' + _text(locator) + '</summary><p>' + _text(segment['text']) + '</p><p>SHA-256: ' + _text(segment['sha256']) + '</p></details>'
    provenance = {k: dossier[k] for k in ('batch_id', 'candidate_id', 'packet_sha256', 'source_acquisition', 'exported')}
    provenance['source_sha256'] = packet['source_sha256']
    content += '</section><section id="provenance"><h2>Provenance and scope</h2><pre>' + _text(json.dumps(provenance, indent=2)) + '</pre><p>No claim acceptance, study-independence count or scientific execution is authorized.</p></section></main></html>'
    write_json(root / 'review.json', dossier)
    with (root / 'index.html').open('x', encoding='utf-8', newline='\n') as handle:
        handle.write(content)
    for name in ('review.json', 'index.html'):
        files[name] = hashlib.sha256((root / name).read_bytes()).hexdigest()
    write_json(root / 'manifest.json', {'schema_version': 1, 'private': True, 'files': files})
    return {'status': 'exported', 'directory': str(root), 'files': files, 'private': True,
            'inspection_attested': False, 'scientific_execution_allowed': False, 'claim_validated': False}
