"""Synthetic assisted-review contracts; no fabricated real human references."""
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from weft import evaluation, quality_review as q
from weft.__main__ import main


class QualityReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        body = json.dumps({'resultList': {'result': [{'doi': '10.9999/fixture', 'abstractText': 'Synthetic pooled-library description.'}]}}).encode()
        (self.root / 'source.json').write_bytes(body)
        self.packet = {'schema_version': 1, 'review_id': 'synthetic-assisted-v1', 'created_at': '2026-10-20T00:00:00Z',
            'kind': 'synthetic', 'mode': q.MODE, 'scope': 'Synthetic fixture only',
            'sampling': {'universe_locator': 'fixture:universe', 'universe_sha256': 'a' * 64,
                         'selection_method': 'All one synthetic case', 'coverage_limits': 'No actual papers'},
            'critic': {'actor': 'synthetic-critic', 'actor_kind': 'agent', 'prior_exposure': 'exposed', 'limits': 'Generated fixture'},
            'cases': [{'case_id': 'case-1', 'paper_key': 'doi:10.9999/fixture', 'rq_context': 'Synthetic RQ',
                       'historical_decisions': 'Synthetic historical hold; never redated',
                       'source': {'path': 'source.json', 'sha256': hashlib.sha256(body).hexdigest(),
                                  'url': 'https://example.org/fixture', 'scope': 'Synthetic metadata only', 'accessed_at': '2026-10-20T00:00:00Z'},
                       'findings': [{'finding_id': 'unit', 'category': 'biological_unit', 'assessment': 'concern',
                                     'statement': 'A pooled library is not an independent-animal count.',
                                     'locators': ['/resultList/result/0/abstractText']}],
                       'human_questions': ['Does this source establish the biological unit?']} ]}
        self.path = self.root / 'input.json'; self.save()

    def save(self):
        self.path.write_text(json.dumps(self.packet), encoding='utf-8')

    def response(self):
        response = q.template(self.packet)
        response.update(actor='synthetic-human-fixture', created_at='2026-10-20T01:00:00Z')
        return response

    def test_blank_template_never_claims_human_review_or_independence(self):
        packet, sources = q.load(self.path)
        response = q.template(packet)
        self.assertIsNone(response['actor']); self.assertIsNone(response['created_at'])
        self.assertTrue(all(j['label'] is None for j in response['cases'][0]['judgments'].values()))
        result = q.adjudicate(packet, sources)
        self.assertEqual(result['missing_labels'], 3)
        self.assertEqual(result['independent_reference_records'], 0)
        self.assertIsNone(result['quality_metrics'])
        for flag in q.FLAGS: self.assertIs(result[flag], False)
        with self.assertRaises(ValueError): q.adjudicate(packet, sources, response)

    def test_missing_disputed_and_uncertain_answers_remain_visible(self):
        packet, sources = q.load(self.path); response = self.response()
        answer = response['cases'][0]
        answer['judgments']['reading'].update(label='hold', reason='Synthetic unresolved unit', locators=['/resultList/result/0/abstractText'])
        answer['findings'][0].update(decision='disagree', reason='Synthetic disagreement with critic')
        result = q.adjudicate(packet, sources, response)
        self.assertEqual(result['status'], 'recorded_with_unresolved')
        self.assertEqual(result['recorded_labels'], 1); self.assertEqual(result['missing_labels'], 2)
        self.assertEqual(result['human_disagreements_with_critic'], 1)
        answer['findings'][0]['decision'] = 'uncertain'
        self.assertEqual(q.adjudicate(packet, sources, response)['unresolved_findings'], 1)

    def test_assisted_identity_and_mode_cannot_be_upgraded(self):
        packet, sources = q.load(self.path)
        changes = [{'independent_reference': True}, {'blind_to_agent': True}, {'actor_kind': 'agent'},
                   {'actor': 'synthetic-critic'}, {'prior_exposure': 'none'}, {'schema_version': True},
                   {'packet_sha256': 'b' * 64}, {'created_at': '2026-10-19T00:00:00Z'}]
        for change in changes:
            with self.subTest(change=change), self.assertRaises(ValueError):
                q.adjudicate(packet, sources, {**self.response(), **change})

    def test_duplicate_or_dropped_cases_and_findings_fail(self):
        packet, sources = q.load(self.path)
        for scope in ('cases', 'findings'):
            response = self.response()
            if scope == 'cases': response['cases'] = []
            else: response['cases'][0]['findings'] = []
            with self.subTest(scope=scope), self.assertRaises(ValueError): q.adjudicate(packet, sources, response)
        response = self.response(); response['cases'][0]['findings'] *= 2
        with self.assertRaises(ValueError): q.adjudicate(packet, sources, response)

    def test_source_tamper_wrong_identity_and_invalid_locators_fail(self):
        original = copy.deepcopy(self.packet)
        patches = [('sha256', '0' * 64), ('path', '../source.json'), ('url', 'javascript:alert(1)')]
        for key, value in patches:
            self.packet = copy.deepcopy(original); self.packet['cases'][0]['source'][key] = value; self.save()
            with self.subTest(key=key), self.assertRaises((ValueError, OSError)): q.load(self.path)
        self.packet = copy.deepcopy(original); self.packet['cases'][0]['paper_key'] = 'doi:10.9999/foreign'; self.save()
        with self.assertRaisesRegex(ValueError, 'DOI'): q.load(self.path)
        self.packet = copy.deepcopy(original); self.packet['cases'][0]['findings'][0]['locators'] = ['/missing']; self.save()
        with self.assertRaisesRegex(ValueError, 'locator'): q.load(self.path)

    def test_human_citations_are_resolved_not_just_strings(self):
        packet, sources = q.load(self.path); response = self.response()
        response['cases'][0]['judgments']['data'].update(label='hold', locators=['/does-not-exist'])
        with self.assertRaisesRegex(ValueError, 'locator'): q.adjudicate(packet, sources, response)
        with self.assertRaises(ValueError): q.pointer(sources['case-1'][1], '/resultList/result/-1')

    def test_private_export_is_immutable_escaped_and_hash_bound(self):
        self.packet['cases'][0]['findings'][0]['statement'] = '<script>untrusted instruction</script>'; self.save()
        output = self.root / 'review'
        result = q.export(self.path, output)
        self.assertFalse(result['release_qualified'])
        html = (output / 'index.html').read_text(encoding='utf-8')
        self.assertNotIn('<script>', html); self.assertIn('&lt;script&gt;', html)
        manifest = json.loads((output / 'manifest.json').read_text())
        for name, sha in manifest['files'].items():
            self.assertEqual(hashlib.sha256((output / name).read_bytes()).hexdigest(), sha)
        with self.assertRaises(FileExistsError): q.export(self.path, output)

    def test_partial_export_has_no_completion_manifest(self):
        original = q.write_json
        def interrupt(path, value):
            if path.name == 'report.json': raise KeyboardInterrupt()
            return original(path, value)
        output = self.root / 'interrupted'
        with patch.object(q, 'write_json', side_effect=interrupt), self.assertRaises(KeyboardInterrupt):
            q.export(self.path, output)
        self.assertFalse((output / 'manifest.json').exists())

    def test_nested_source_paths_survive_transfer_and_cannot_overwrite_outputs(self):
        (self.root / 'metadata').mkdir()
        (self.root / 'metadata' / 'lung #1.json').write_bytes((self.root / 'source.json').read_bytes())
        self.packet['cases'][0]['source']['path'] = 'metadata/lung #1.json'; self.save()
        output = self.root / 'portable'
        q.export(self.path, output)
        restored, _ = q.load(output / 'packet.json')
        self.assertEqual(restored, self.packet)
        self.assertIn('metadata/lung%20%231.json', (output / 'index.html').read_text(encoding='utf-8'))
        (self.root / 'report.json').write_bytes((self.root / 'source.json').read_bytes())
        self.packet['cases'][0]['source']['path'] = 'report.json'; self.save()
        with self.assertRaisesRegex(ValueError, 'reserved'): q.export(self.path, self.root / 'collision')
        self.assertFalse((self.root / 'collision').exists())

    def test_rendered_human_correction_is_not_hidden_behind_critic(self):
        response = self.response()
        response['cases'][0]['findings'][0].update(decision='disagree', reason='Human correction <retain both records>')
        response['cases'][0]['judgments']['reading'].update(label='hold', reason='Human missing-evidence reason', locators=['/resultList/result/0/abstractText'])
        output = self.root / 'adjudicated'
        q.export(self.path, output, response)
        html = (output / 'index.html').read_text(encoding='utf-8')
        self.assertIn('Human adjudication: disagree', html)
        self.assertIn('Human correction &lt;retain both records&gt;', html)
        self.assertIn('reading: hold', html)
        self.assertIn('A pooled library is not an independent-animal count.', html)
        self.assertIn('data: unresolved', html)

    def test_windows_reserved_case_and_filename_aliases_are_rejected(self):
        body = (self.root / 'source.json').read_bytes()
        for name in ('INDEX.HTML', 'REVIEW.MD', 'MANIFEST.JSON'):
            (self.root / name).write_bytes(body)
            self.packet['cases'][0]['source']['path'] = name; self.save()
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'reserved'):
                q.export(self.path, self.root / 'unsafe')
            self.assertFalse((self.root / 'unsafe').exists())
        for name in ('source.json.', 'source.json ', 'aux.json', 'index~1.htm', 'folder./source.json'):
            self.packet['cases'][0]['source']['path'] = name; self.save()
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'portable'):
                q.load(self.path)

    def test_cli_prepares_review_without_network_or_store(self):
        with patch('weft.europe_pmc.urlopen', side_effect=AssertionError('No network')), patch('sys.stdout', new_callable=io.StringIO) as out:
            code = main(['quality-review-export', '--packet', str(self.path), '--output', str(self.root / 'cli')])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(out.getvalue())['status'], 'awaiting_human_adjudication')

    def test_wrong_json_types_fail_as_validation_errors(self):
        original = copy.deepcopy(self.packet)
        for field in ('category', 'assessment'):
            self.packet = copy.deepcopy(original)
            self.packet['cases'][0]['findings'][0][field] = []
            self.save()
            with self.subTest(field=field), self.assertRaises(ValueError): q.load(self.path)
        self.packet = copy.deepcopy(original); self.packet['kind'] = []; self.save()
        with self.assertRaises(ValueError): q.load(self.path)
        self.packet = original; self.save(); packet, sources = q.load(self.path)
        response = self.response(); response['cases'][0]['case_id'] = []
        with self.assertRaises(ValueError): q.adjudicate(packet, sources, response)


if __name__ == '__main__': unittest.main()
