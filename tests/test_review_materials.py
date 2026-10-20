"""Synthetic multi-source review and transferred-bundle recovery boundaries."""
import copy
import hashlib
import io
import json
import shutil
import unittest
from unittest.mock import patch

from weft import quality_review as q
from weft.__main__ import main
from tests import test_quality_review as legacy


class ReviewMaterialsTests(unittest.TestCase):
    save = legacy.QualityReviewTests.save
    response = legacy.QualityReviewTests.response

    def setUp(self):
        legacy.QualityReviewTests.setUp(self)
        self.packet['schema_version'] = 2
        case = self.packet['cases'][0]
        case['materials'] = []
        case['access_attempts'] = []
        self.add_material('paper', 'pdf', b'%PDF-1.4\nSynthetic fixture, not a real paper.', 'full_text')
        self.add_material('text', 'txt', b'Synthetic methods\nPooled measurements, not independent animals.',
                          'derived_text', ['paper'])
        self.add_material('owner', 'json', b'{"decision":"keep", "scope":"reading only"}', 'authority')
        self.add_material('receipt', 'json', b'{"observation":"retained PDF bytes; synthetic fixture"}', 'access_receipt')
        case['access_attempts'] = [{'attempt_id': 'attempt-1', 'route': 'institutional_browser',
            'source_url': 'https://example.org/fixture', 'observed_at': '2026-10-20T00:00:00Z',
            'outcome': 'retrieved', 'http_status': None, 'material_ids': ['paper'],
            'receipt_locator': '/materials/receipt/content/observation', 'notes': 'Synthetic retained bytes.'}]
        case['findings'][0]['locators'] = ['/materials/text/content/1']
        self.save()

    def add_material(self, mid, fmt, body, role, parents=None):
        name = 'materials/' + mid + '.' + fmt
        target = self.root / name
        target.parent.mkdir(exist_ok=True)
        target.write_bytes(body)
        item = {'material_id': mid, 'path': name, 'sha256': hashlib.sha256(body).hexdigest(),
            'bytes': len(body), 'format': fmt, 'role': role, 'paper_key': self.packet['cases'][0]['paper_key'],
            'origin': 'https://example.org/fixture', 'version': 'Synthetic v1',
            'coverage': 'Synthetic fixture; no actual article review.',
            'inspection': {'status': 'not_reviewed', 'actor': None, 'scope': 'Not inspected'},
            'derived_from': parents or []}
        self.packet['cases'][0]['materials'].append(item)
        return item

    def export(self, response=None):
        self.save()
        output = self.root / 'export'
        q.export(self.path, output, response)
        return output

    def rewrite_manifest_hash(self, output, name):
        manifest = json.loads((output / 'manifest.json').read_text())
        manifest['files'][name] = hashlib.sha256((output / name).read_bytes()).hexdigest()
        (output / 'manifest.json').write_text(json.dumps(manifest))

    def test_reading_keep_does_not_create_other_authority(self):
        packet, sources = q.load(self.path)
        response = self.response()
        response['cases'][0]['judgments']['reading'].update(label='read_next', reason='Synthetic human keep',
            locators=['/materials/owner/content/decision'])
        report = q.adjudicate(packet, sources, response)
        self.assertEqual((report['recorded_labels'], report['missing_labels'], report['unresolved_findings']), (1, 2, 1))
        self.assertEqual(report['independent_reference_records'], 0)
        self.assertIsNone(report['quality_metrics'])
        for flag in q.FLAGS: self.assertIs(report[flag], False)
        summary = report['material_review']['case-1']
        self.assertFalse(summary['automatic_cloud_access_qualified'])
        self.assertFalse(summary['institutional_permission_failure_inferred'])

    def test_multiple_sources_survive_transfer_without_resuming(self):
        output = self.export()
        transfer = self.root / 'transfer'
        shutil.copytree(output, transfer)
        report = q.verify(transfer)
        self.assertTrue(report['integrity_verified'])
        self.assertFalse(report['resume_performed'])
        self.assertFalse(report['automatic_cloud_launch'])
        self.assertEqual((transfer / 'materials/paper.pdf').read_bytes(), (self.root / 'materials/paper.pdf').read_bytes())
        html = (transfer / 'index.html').read_text(encoding='utf-8')
        self.assertIn('institutional_browser: retrieved', html)

    def test_metadata_200_and_failed_routes_do_not_establish_fulltext_access(self):
        attempt = self.packet['cases'][0]['access_attempts'][0]
        attempt.update(route='publisher_api', outcome='metadata_only', http_status=200, material_ids=[])
        self.save()
        packet, sources = q.load(self.path)
        summary = q.adjudicate(packet, sources)['material_review']['case-1']
        self.assertEqual(summary['access_attempts'][0]['outcome'], 'metadata_only')
        self.assertFalse(summary['access_failure_is_relevance_rejection'])
        attempt['outcome'] = 'retrieved'; self.save()
        with self.assertRaisesRegex(ValueError, 'retained bytes'): q.load(self.path)

    def test_receipt_must_resolve_to_bound_receipt_not_generic_text(self):
        attempt = self.packet['cases'][0]['access_attempts'][0]
        for locator in ('/materials/text/content/0', '/materials/receipt/content/missing'):
            attempt['receipt_locator'] = locator; self.save()
            with self.subTest(locator=locator), self.assertRaises(ValueError): q.load(self.path)

    def test_binary_bytes_cannot_be_cited_as_parsed_text(self):
        case = self.packet['cases'][0]
        case['findings'][0]['locators'] = ['/materials/paper/content/0']; self.save()
        with self.assertRaisesRegex(ValueError, 'scalar'): q.load(self.path)
        case['findings'][0]['locators'] = ['/materials/paper/inspection/scope']; self.save()
        q.load(self.path)  # An explicit inspection attestation, not PDF entailment.

    def test_captions_cannot_be_promoted_to_pixel_inspection(self):
        self.packet['cases'][0]['materials'][1]['inspection'].update(
            status='text_and_selected_pixels', actor='fixture-critic')
        self.save()
        with self.assertRaisesRegex(ValueError, 'pixel'): q.load(self.path)

    def test_derivation_and_paper_binding_are_required(self):
        original = copy.deepcopy(self.packet)
        for changes in ({'derived_from': ['absent']}, {'derived_from': ['owner']},
                        {'derived_from': []}, {'paper_key': 'doi:10.9999/other'}, {'format': 'pdf'}):
            self.packet = copy.deepcopy(original)
            self.packet['cases'][0]['materials'][1].update(changes); self.save()
            with self.subTest(changes=changes), self.assertRaises(ValueError): q.load(self.path)

    def test_material_hash_signature_and_unsafe_paths_rejected(self):
        original = copy.deepcopy(self.packet)
        for changes in ({'sha256': '0' * 64}, {'bytes': 1}, {'format': 'png'},
                        {'path': '../source.json'}, {'path': 'report.json'}, {'path': 'materials/NUL.txt'}):
            self.packet = copy.deepcopy(original)
            self.packet['cases'][0]['materials'][0].update(changes); self.save()
            with self.subTest(changes=changes), self.assertRaises((ValueError, OSError)): q.load(self.path)

    def test_file_directory_and_case_aliases_rejected_before_export(self):
        for path in ('source.json/child.pdf', 'SOURCE.json'):
            self.packet['cases'][0]['materials'][0]['path'] = path; self.save()
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'collide|alias'): q.load(self.path)

    def test_tampered_material_and_incomplete_transfer_fail(self):
        output = self.export()
        paper = output / 'materials/paper.pdf'
        body = paper.read_bytes(); paper.write_bytes(body + b'changed')
        with self.assertRaisesRegex(ValueError, 'changed'): q.verify(output)
        paper.write_bytes(body)
        (output / 'manifest.json').unlink()
        with self.assertRaises((ValueError, OSError)): q.verify(output)

    def test_report_and_blank_template_are_recomputed_after_manifest_edit(self):
        output = self.export()
        for name in ('report.json', 'human-response-template.json'):
            original = (output / name).read_bytes()
            value = json.loads(original)
            value['independent_reference'] = True
            (output / name).write_text(json.dumps(value))
            self.rewrite_manifest_hash(output, name)
            with self.subTest(name=name), self.assertRaises(ValueError): q.verify(output)
            (output / name).write_bytes(original)
            self.rewrite_manifest_hash(output, name)

    def test_unlisted_files_and_linked_sources_are_rejected(self):
        output = self.export()
        extra = output / 'extra.txt'; extra.write_text('unlisted')
        with self.assertRaisesRegex(ValueError, 'unlisted'): q.verify(output)
        extra.unlink()
        # Windows machines may not grant symlink privileges; directory links still
        # have explicit rejection in the shared _local_file and verify paths.
        link = output / 'linked'
        try: link.symlink_to(self.root, target_is_directory=True)
        except OSError: return
        try:
            with self.assertRaisesRegex(ValueError, 'linked'): q.verify(output)
        finally: link.unlink()

    def test_cli_verification_is_offline_and_side_effect_free(self):
        output = self.export()
        digest = hashlib.sha256((output / 'manifest.json').read_bytes()).hexdigest()
        with patch('urllib.request.urlopen', side_effect=AssertionError('No retrieval allowed')), patch('sys.stdout', new_callable=io.StringIO) as stdout:
            self.assertEqual(main(['quality-review-verify', '--directory', str(output), '--expected-manifest-sha256', digest]), 0)
        report = json.loads(stdout.getvalue())
        self.assertTrue(report['integrity_verified'])
        self.assertTrue(report['manifest_matches_expected'])
        self.assertFalse(report['model_invoked'])
        with self.assertRaisesRegex(ValueError, 'separately retained hash'):
            q.verify(output, '0' * 64)

    def test_legacy_export_can_be_verified(self):
        legacy.QualityReviewTests.setUp(self)
        output = self.export()
        self.assertEqual(q.verify(output)['schema_version'], 1)

    def test_oversized_response_cannot_leave_completed_unverifiable_export(self):
        first = self.packet['cases'][0]
        first['findings'] = [{**first['findings'][0], 'finding_id': 'finding-' + str(i)} for i in range(20)]
        self.packet['cases'] = [{**copy.deepcopy(first), 'case_id': 'case-' + str(i)} for i in range(6)]
        self.save()
        response = self.response()
        for case in response['cases']:
            for finding in case['findings']:
                finding['reason'] = 'x' * 10_000
        output = self.root / 'too-large'
        with self.assertRaisesRegex(ValueError, 'JSON exceeds'):
            q.export(self.path, output, response)
        self.assertFalse(output.exists())
