"""Reproducible synthetic workflow demonstration. All source transports are fixtures."""
import base64
import hashlib
import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from . import workflow, selection, review_view
from .discovery import Store, write_json
from .europe_pmc import EuropePMC
from .identity import digest

PNG = base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aWQAAAABJRU5ErkJggg==')


def run(output):
    root = Path(output).resolve()
    root.mkdir(parents=True, exist_ok=False)
    questions = [{'rq_id': q, 'title': q + '. Synthetic demonstration only', 'context_sha256': digest(q)} for q in ('A0', 'A1', 'A2')]
    context = {'ravel_commit': 'a' * 40, 'questions': questions, 'catalog_sha256': digest(questions)}
    profile = {'date_field': 'FIRST_IDATE', 'streams': {'broad': 'SYNTHETIC_BROAD', 'rq_contrary': 'SYNTHETIC_CONTRARY', 'adjacent_context': 'SYNTHETIC_ADJACENT'}}
    records = [{'source': 'MED', 'id': str(9000000 + i), 'pmid': str(9000000 + i), 'pmcid': 'PMC' + str(9000000 + i),
                'doi': '10.9999/weft.synthetic.' + str(i), 'title': 'Synthetic paper ' + str(i) + ': pooled-library demonstration',
                'abstractText': 'Synthetic fixture: condition A versus B; one pooled RNA library per condition.'} for i in (1, 2, 3)]
    calls = {'metadata': 0, 'xml': 0}

    def metadata(url):
        calls['metadata'] += 1
        query = parse_qs(urlsplit(url).query)['query'][0]
        found = [records[2]] if 'CONTRARY' in query else [records[1]] if 'ADJACENT' in query else records
        return json.dumps({'version': 'synthetic', 'hitCount': len(found), 'resultList': {'result': found}}).encode()

    def xml(url):
        calls['xml'] += 1
        pmcid = url.split('/')[-2]
        record = next(r for r in records if r['pmcid'] == pmcid)
        return (f'<article><front><article-meta><article-id pub-id-type="pmc">{pmcid[3:]}</article-id>'
                f'<article-id pub-id-type="doi">{record["doi"]}</article-id></article-meta></front>'
                '<body><sec><title>Synthetic methods</title><p>Condition A versus B; one pooled RNA library per condition. '
                'Synthetic source only; no independent biological replication is established.</p>'
                '<fig id="f1"><label>Figure 1</label><caption><p>Synthetic placeholder; no scientific image.</p></caption>'
                '<graphic xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="figure.png"/></fig>'
                '<supplementary-material id="s1"><label>Supplement 1</label><caption><p>Unavailable synthetic supplement.</p></caption>'
                '</supplementary-material></sec></body></article>').encode()

    with Store(root / 'store') as store:
        initial = workflow.create(store, context, 'synthetic-demo', profile, list(profile['streams']),
                                  '2026-10-01', '2026-10-02', actor='synthetic-demo-agent',
                                  max_searches=3, max_records=10, max_screenings=4, max_full_reads=4)
        bid = initial['batch_id']
        client = EuropePMC(fetch=metadata)
        review_cid = None
        for _ in range(64):
            step = workflow.advance(store, bid, allow_network=True, client=client, fetch=xml)
            stage = step.get('stage')
            if stage == 'screening' and 'issued' in step:
                issued = step['issued']; record = issued['response_template']
                segment = issued['packet']['segments'][1]
                record.update(actor='synthetic-demo-agent', prior_exposure='Generated fixture; all outcomes exposed', decision='read_next',
                              relation='methodological', reason='Synthetic pooled-library description needs full-source review.', reopen_when='Synthetic fixture only',
                              citations=[{k: segment[k] for k in ('locator', 'segment_sha256')}])
                workflow.submit(store, bid, 'screening', record)
            elif stage == 'reading':
                packet = json.loads((Path(step['material']['resolved_directory']) / 'packet.json').read_text(encoding='utf-8'))
                segment = packet['segments'][0]
                record = {k: packet[k] for k in ('candidate_id', 'context_sha256', 'evidence_sha256', 'source_sha256')}
                record.update(actor='synthetic-demo-agent', actor_kind='agent', scope='Synthetic XML fixture only; pixels not inspected',
                              statements=[{'text': 'The synthetic source describes pooled libraries.', 'locator': segment['locator'], 'segment_sha256': segment['sha256']}], next_action='review_required')
                workflow.submit(store, bid, 'reading', record)
            elif stage == 'evidence':
                cid = step['packet']['candidate_id']; record = step['response_template']
                if review_cid is None:
                    review_cid = cid
                    folder = root / 'supplied-material'; folder.mkdir()
                    (folder / 'figure.png').write_bytes(PNG)
                    manifest = {'schema_version': 1, 'batch_id': bid, 'candidate_id': cid, 'packet_sha256': step['packet_sha256'],
                                'artifacts': [{'resource_id': step['packet']['resources'][0]['resource_id'], 'path': 'figure.png',
                                               'bytes': len(PNG), 'sha256': hashlib.sha256(PNG).hexdigest(), 'origin': 'Generated one-pixel synthetic fixture; not a scientific figure'}]}
                    write_json(folder / 'manifest.json', manifest)
                    workflow.import_materials(store, bid, cid, folder / 'manifest.json')
                segment = step['packet']['segments'][0]
                record.update(actor='synthetic-demo-agent', prior_exposure='Generated fixture; no independent review')
                record['data'].update(comparison='Condition A versus B', measured_endpoint='RNA abundance', biological_unit='Pooled library',
                    independent_units='pooled_only', citations=[{'locator': segment['locator'], 'segment_sha256': segment['sha256']}],
                    reason='Synthetic description only; dataset access and source materials remain unresolved.')
                workflow.submit(store, bid, 'evidence', record)
            elif step.get('status') in {'complete', 'complete_with_holds'}:
                break
            elif step.get('status') == 'hold':
                raise ValueError('Synthetic workflow unexpectedly held: ' + json.dumps(step.get('blockers')))
        else:
            raise ValueError('Synthetic demonstration exceeded its transition bound')
        with workflow.readonly(store.root) as readonly:
            workflow.export(readonly, bid, root / 'status')
            review_view.export(readonly, bid, review_cid, root / 'review', include_materials=True)
            reference = {'schema_version': 1, 'provenance': 'Generated synthetic comparison bibliography',
                         'prior_exposure': 'All fixtures exposed', 'paper_keys': ['doi:' + r['doi'] for r in records] + ['doi:10.9999/weft.synthetic.missing']}
            audit = selection.report(readonly, bid, reference=reference, include_plan=True)
            write_json(root / 'selection-audit.json', audit)
        result = {'status': 'complete', 'synthetic': True, 'directory': str(root), 'batch_id': bid,
                  'fixture_transport_calls': calls, 'selected_papers': audit['actual_issued']['unique_papers'],
                  'baseline_nominal_papers': audit['nominal_baseline']['unique_papers'],
                  'reading_packets': store.db.execute('SELECT COUNT(*) FROM batch_items WHERE reading_json IS NOT NULL').fetchone()[0],
                  'cached_xml_reuses': sum(json.loads(row[0]).get('source_acquisition', {}).get('kind') == 'cached_xml'
                                           for row in store.db.execute('SELECT reading_json FROM batch_items WHERE reading_json IS NOT NULL')),
                  'scientific_execution_allowed': False, 'claim_validated': False}
        write_json(root / 'demo.json', result)
    return result
