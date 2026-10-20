import copy
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from weft import batches, materials, qualification as q, review_view, screening, workflow as w
from weft.__main__ import main
from weft.identity import digest
import test_batches
import test_reading
import test_qualification
import test_workflow


class MaterialsTests(unittest.TestCase):
    setUp = test_workflow.WorkflowTests.setUp
    create = test_workflow.WorkflowTests.create
    response = test_workflow.WorkflowTests.response
    start = test_workflow.WorkflowTests.start
    packet = test_workflow.WorkflowTests.packet
    through_screening = test_workflow.WorkflowTests.through_screening
    through_material = test_workflow.WorkflowTests.through_material
    through_reading = test_workflow.WorkflowTests.through_reading

    def two_links(self, **limits):
        self.ctx['questions'].append({'rq_id': 'A1', 'title': 'Second synthetic RQ', 'context_sha256': digest('A1')})
        self.ctx['catalog_sha256'] = digest(self.ctx['questions'])
        bid = self.start(**limits)
        cids = []
        for _ in range(2):
            issued, response = self.packet(bid, 'screening')
            cids.append(response['candidate_id'])
            w.submit(self.store, bid, 'screening', response)
        return bid, cids

    def material_manifest(self):
        bid = self.through_reading(); issued, record = self.packet(bid, 'evidence')
        folder = Path(self.temp.name) / 'intake'; folder.mkdir()
        path = folder / 'figure.png'
        path.write_bytes(b'\x89PNG\r\n\x1a\nsynthetic signature fixture; not a rendered figure')
        item = {'resource_id': issued['packet']['resources'][0]['resource_id'], 'path': path.name,
                'bytes': path.stat().st_size, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'origin': 'Synthetic Figure 1 fixture'}
        manifest = {'schema_version': 1, 'batch_id': bid, 'candidate_id': issued['packet']['candidate_id'],
                    'packet_sha256': issued['packet_sha256'], 'artifacts': [item]}
        manifest_path = folder / 'manifest.json'; manifest_path.write_text(json.dumps(manifest))
        return bid, manifest['candidate_id'], issued, record, manifest_path, manifest

    def test_xml_reuse_preserves_separate_rq_packets_and_assessments(self):
        bid, cids = self.two_links()
        first = screening.read_packet(self.store, bid, cids[0], fetch=lambda _: test_reading.XML)
        self.assertEqual(materials.reusable(self.store, bid, cids[1]), cids[0])
        with patch('weft.reading.EuropePMC.request', side_effect=AssertionError('Cached reuse must not retrieve')):
            second = screening.read_packet(self.store, bid, cids[1], reuse_candidate=cids[0])
        p1 = json.loads((Path(first['resolved_directory']) / 'packet.json').read_text())
        p2 = json.loads((Path(second['resolved_directory']) / 'packet.json').read_text())
        self.assertEqual(p1['source_sha256'], p2['source_sha256'])
        self.assertNotEqual(p1['context_sha256'], p2['context_sha256'])
        self.assertNotEqual(first['packet_sha256'], second['packet_sha256'])
        self.assertEqual(second['transport_attempts'], [])
        self.assertFalse(second['source_acquisition']['assessment_reused'])
        self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM batch_items WHERE reading_result_json IS NOT NULL').fetchone()[0], 0)

    def test_workflow_reuses_material_without_network_permission_but_keeps_read_hold(self):
        bid, cids = self.two_links()
        w.advance(self.store, bid, allow_network=True, fetch=lambda _: test_reading.XML)
        _, response = self.packet(bid, 'reading'); response['next_action'] = 'hold'
        w.submit(self.store, bid, 'reading', response)
        with patch('weft.reading.EuropePMC.request', side_effect=AssertionError('No refetch')):
            result = w.advance(self.store, bid)
        self.assertEqual(result['material']['source_acquisition']['kind'], 'cached_xml')
        self.assertEqual(w.status(self.store, bid)['item_stages'], {'hold': 1, 'reading': 1})

    def test_changed_cached_bytes_hold_target_without_network_fallback(self):
        bid, cids = self.two_links()
        first = screening.read_packet(self.store, bid, cids[0], fetch=lambda _: test_reading.XML)
        (Path(first['resolved_directory']) / 'source.xml').write_bytes(b'changed')
        with patch('weft.reading.EuropePMC.request', side_effect=AssertionError('No fallback')):
            result = screening.read_packet(self.store, bid, cids[1], reuse_candidate=cids[0])
        self.assertEqual(result['status'], 'hold')
        self.assertIn('changed', result['reason'].lower())

    def test_reuse_rejects_foreign_snapshot(self):
        bid, cids = self.two_links()
        screening.read_packet(self.store, bid, cids[0], fetch=lambda _: test_reading.XML)
        with self.store.db:
            self.store.db.execute('UPDATE candidates SET evidence_sha=? WHERE id=?', ('0' * 64, cids[1]))
        with self.assertRaises(ValueError):
            screening.read_packet(self.store, bid, cids[1], reuse_candidate=cids[0])

    def test_cached_source_change_after_validation_is_held(self):
        bid, cids = self.two_links()
        screening.read_packet(self.store, bid, cids[0], fetch=lambda _: test_reading.XML)
        check = materials.check_files
        def changed(*args):
            directory = check(*args)
            (directory / 'source.xml').write_bytes(test_reading.XML.replace(b'pooled', b'changed'))
            return directory
        with patch.object(materials, 'check_files', side_effect=changed), patch('weft.reading.EuropePMC.request', side_effect=AssertionError('No fallback')):
            result = screening.read_packet(self.store, bid, cids[1], reuse_candidate=cids[0])
        self.assertEqual(result['status'], 'hold')
        self.assertIn('changed during reuse', result['reason'])

    def test_cached_reuse_obeys_reading_cap(self):
        bid, cids = self.two_links(max_full_reads=1)
        screening.read_packet(self.store, bid, cids[0], fetch=lambda _: test_reading.XML)
        with self.assertRaisesRegex(ValueError, 'cap'):
            screening.read_packet(self.store, bid, cids[1], reuse_candidate=cids[0])

    def test_demo_has_no_live_transport_and_preserves_output(self):
        from weft.demo import run
        output = Path(self.temp.name) / 'demo'
        with patch('urllib.request.urlopen', side_effect=AssertionError('No network')):
            result = run(output)
        self.assertEqual(result['fixture_transport_calls'], {'metadata': 3, 'xml': 3})
        self.assertEqual(result['reading_packets'], 4)
        self.assertEqual(result['cached_xml_reuses'], 1)
        self.assertEqual(result['selected_papers'], 3)
        self.assertTrue((output / 'review' / 'manifest.json').exists())
        with self.assertRaises(FileExistsError):
            run(output)

    def test_manifest_retry_does_not_imply_inspection(self):
        bid, cid, issued, record, path, manifest = self.material_manifest()
        first = w.import_materials(self.store, bid, cid, path)
        second = w.import_materials(self.store, bid, cid, path)
        self.assertEqual(first['artifacts'][0]['artifact_id'], second['artifacts'][0]['artifact_id'])
        self.assertEqual(second['artifacts'][0]['status'], 'already_recorded')
        with w.readonly(self.store.root) as readonly:
            inv = materials.inventory(readonly, bid, cid)
        self.assertEqual(inv['resources'][0]['coverage']['status'], 'not_inspected')
        self.assertEqual(inv['resources'][0]['attachments'][0]['status'], 'verified_bytes')
        self.assertFalse(first['inspection_attested'])

    def test_bad_manifest_entries_fail_before_any_attachment(self):
        bid, cid, issued, record, path, manifest = self.material_manifest()
        for changes in [{'path': '../outside.png'}, {'sha256': '0' * 64}, {'bytes': True}, {'resource_id': 'invented'}]:
            bad = copy.deepcopy(manifest)
            bad['artifacts'].append({**bad['artifacts'][0], **changes})
            path.write_text(json.dumps(bad))
            with self.subTest(changes=changes), self.assertRaises((ValueError, OSError)):
                w.import_materials(self.store, bid, cid, path)
            self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM evidence_artifacts').fetchone()[0], 0)

    def test_file_change_between_preflight_and_attach_is_rejected(self):
        bid, cid, issued, record, path, manifest = self.material_manifest()
        original = q.attach
        def changed(*args, **kwargs):
            (path.parent / 'figure.png').write_bytes(b'\x89PNG\r\n\x1a\nchanged')
            return original(*args, **kwargs)
        with patch.object(q, 'attach', side_effect=changed), self.assertRaises(ValueError):
            w.import_materials(self.store, bid, cid, path)
        self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM evidence_artifacts').fetchone()[0], 0)

    def test_partial_intake_ack_loss_recovers_exact_attachment(self):
        bid, cid, issued, record, path, manifest = self.material_manifest()
        original = q.attach
        def lost(*args, **kwargs):
            original(*args, **kwargs)
            raise KeyboardInterrupt()
        with patch.object(q, 'attach', side_effect=lost), self.assertRaises(KeyboardInterrupt):
            w.import_materials(self.store, bid, cid, path)
        recovered = w.import_materials(self.store, bid, cid, path)
        self.assertEqual(recovered['artifacts'][0]['status'], 'already_recorded')
        self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM evidence_artifacts').fetchone()[0], 1)

    def test_explicit_workflow_hold_blocks_material_intake(self):
        bid, cid, issued, record, path, manifest = self.material_manifest()
        w.hold(self.store, bid, 'Preserve review hold')
        with self.assertRaisesRegex(ValueError, 'held'):
            w.import_materials(self.store, bid, cid, path)

    def test_review_bundle_source_anchors_escaping_and_opt_in_copies(self):
        bid, cid, issued, record, path, manifest = self.material_manifest()
        result = w.import_materials(self.store, bid, cid, path)
        record['data']['reason'] = '<script>untrusted source instruction</script>'
        record['data']['citations'] = [{'locator': issued['packet']['segments'][0]['locator'], 'segment_sha256': issued['packet']['segments'][0]['sha256']}]
        w.submit(self.store, bid, 'evidence', record)
        root = Path(self.temp.name)
        with w.readonly(self.store.root) as readonly:
            review_view.export(readonly, bid, cid, root / 'without-assets')
            exported = review_view.export(readonly, bid, cid, root / 'with-assets', include_materials=True)
        self.assertFalse((root / 'without-assets' / 'assets').exists())
        html = (root / 'with-assets' / 'index.html').read_text(encoding='utf-8')
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)
        class Links(HTMLParser):
            def __init__(self):
                super().__init__(); self.ids = set(); self.links = []
            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if 'id' in attrs: self.ids.add(attrs['id'])
                if 'href' in attrs: self.links.append(attrs['href'])
        parser = Links(); parser.feed(html)
        for link in parser.links:
            if link.startswith('#'):
                self.assertIn(link[1:], parser.ids)
            else:
                self.assertTrue(link.startswith('assets/'))
        for name, sha in exported['files'].items():
            self.assertEqual(hashlib.sha256((root / 'with-assets' / name).read_bytes()).hexdigest(), sha)
        self.assertIn('not_inspected', html)
        self.assertTrue((root / 'with-assets' / 'manifest.json').exists())

    def test_changed_asset_is_visible_and_cannot_be_copied(self):
        bid, cid, issued, record, path, manifest = self.material_manifest()
        w.import_materials(self.store, bid, cid, path)
        next(self.store.root.glob('evidence-*/source.bin')).write_bytes(b'tampered')
        inv = materials.inventory(self.store, bid, cid)
        self.assertEqual(inv['resources'][0]['attachments'][0]['status'], 'hold')
        visible = Path(self.temp.name) / 'hold-view'
        review_view.export(self.store, bid, cid, visible)
        self.assertIn(inv['resources'][0]['attachments'][0]['reason'], (visible / 'index.html').read_text(encoding='utf-8'))
        output = Path(self.temp.name) / 'incomplete'
        with self.assertRaises(ValueError):
            review_view.export(self.store, bid, cid, output, include_materials=True)
        self.assertFalse((output / 'manifest.json').exists())

    def test_cli_intake_inventory_and_review_export(self):
        bid, cid, issued, record, path, manifest = self.material_manifest()
        common = ['--store', str(self.store.root), '--batch', bid, '--candidate', cid]
        with patch('sys.stdout', new_callable=io.StringIO):
            self.assertEqual(main(['workflow-import-materials', *common, '--manifest', str(path)]), 0)
            self.assertEqual(main(['workflow-materials', *common]), 0)
            self.assertEqual(main(['workflow-review-export', *common, '--output', str(Path(self.temp.name) / 'cli-view')]), 0)


if __name__ == '__main__':
    unittest.main()
