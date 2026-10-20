import copy
import hashlib
import io
import json
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch

from weft import batches, handoff, qualification, screening, workflow as w
from weft.__main__ import main
from weft.discovery import Store
from weft.europe_pmc import EuropePMC
import test_batches
import test_discovery as fixtures
import test_qualification
import test_reading


class WorkflowTests(unittest.TestCase):
    setUp = test_batches.BatchTests.setUp
    create = test_batches.BatchTests.create
    response = test_batches.BatchTests.response
    citation = test_qualification.QualificationTests.citation
    descriptive = test_qualification.QualificationTests.descriptive

    def start(self, records=None, **limits):
        bid = self.create(**limits)
        w.initialize(self.store, bid, 'fixture-agent')
        records = [fixtures.article(pmcid='PMC1', abstractText='One pooled library per condition.')] if records is None else records
        self.client = EuropePMC(fetch=lambda _: fixtures.page(records))
        w.advance(self.store, bid, allow_network=True, client=self.client)
        return bid

    def packet(self, bid, stage):
        issued = w.advance(self.store, bid)
        self.assertEqual(issued['stage'], stage)
        if stage == 'screening':
            return issued, self.response(copy.deepcopy(issued['issued']))
        if stage == 'reading':
            read = issued['material']
            assessment = test_reading.ReadingTests.assessment(self, {**read, 'directory': read['resolved_directory']})
            assessment['actor'] = 'fixture-agent'
            return issued, assessment
        record = copy.deepcopy(issued['response_template'])
        record.update(actor='fixture-agent', prior_exposure='Synthetic development fixture')
        return issued, record

    def through_screening(self):
        bid = self.start()
        _, response = self.packet(bid, 'screening')
        w.submit(self.store, bid, 'screening', response)
        return bid

    def through_material(self):
        bid = self.through_screening()
        w.advance(self.store, bid, allow_network=True, fetch=lambda _: test_qualification.XML)
        return bid

    def through_reading(self):
        bid = self.through_material()
        _, response = self.packet(bid, 'reading')
        w.submit(self.store, bid, 'reading', response)
        return bid

    def test_end_to_end_separate_proposals_and_repeat_without_io(self):
        bid = self.through_reading()
        issued, record = self.packet(bid, 'evidence')
        record = self.descriptive(issued, record)
        result = w.submit(self.store, bid, 'evidence', record)
        self.assertEqual(result['result']['data_proposal'], 'review_required')
        self.assertEqual(result['result']['rq_proposal'], 'hold')
        with patch.object(batches, 'run', side_effect=AssertionError('No rediscovery')), patch.object(screening, 'read_packet', side_effect=AssertionError('No refetch')):
            with Store(self.store.root) as reopened:
                report = w.advance(reopened, bid, allow_network=True)
                replay = w.submit(reopened, bid, 'evidence', record)
        self.assertEqual(report['status'], 'complete_with_holds')
        self.assertTrue(report['all_evidence_reviews_recorded'])
        self.assertTrue(report['discovery_complete'])
        self.assertIsNone(report['independent_study_count'])
        self.assertFalse(report['automatic_cloud_launch'])
        self.assertFalse(report['scientific_execution_allowed'])
        self.assertEqual(result['return_id'], replay['return_id'])
        self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM evidence_reviews').fetchone()[0], 1)

    def test_network_is_explicit_and_discovery_is_not_review_completion(self):
        bid = self.create(); w.initialize(self.store, bid, 'fixture-agent')
        with patch.object(batches, 'run', side_effect=AssertionError('No implicit retrieval')):
            self.assertEqual(w.advance(self.store, bid)['status'], 'needs_network')
        w.advance(self.store, bid, allow_network=True, client=EuropePMC(fetch=lambda _: fixtures.page([
            fixtures.article(pmcid='PMC1', abstractText='Fixture')])) )
        report = w.status(self.store, bid)
        self.assertTrue(report['discovery_complete'])
        self.assertFalse(report['all_evidence_reviews_recorded'])
        self.assertEqual(report['item_stages'], {'screening': 1})
        _, response = self.packet(bid, 'screening')
        w.submit(self.store, bid, 'screening', response)
        with patch.object(screening, 'read_packet', side_effect=AssertionError('No implicit XML')):
            self.assertEqual(w.advance(self.store, bid)['status'], 'needs_network')

    def test_discovery_crash_stays_held_and_attempt_not_repeated(self):
        bid = self.create(); w.initialize(self.store, bid, 'fixture-agent')
        with patch.object(batches, 'discover', side_effect=KeyboardInterrupt), self.assertRaises(KeyboardInterrupt):
            w.advance(self.store, bid, allow_network=True)
        with patch.object(batches, 'run', side_effect=AssertionError('No retry')):
            result = w.advance(self.store, bid, allow_network=True)
        self.assertEqual(result['status'], 'hold')
        self.assertEqual(result['windows'][0]['status'], 'running')
        self.assertEqual(result['windows'][0]['attempts'], 1)

    def test_finalize_cached_discovery_after_interrupted_item_population(self):
        bid = self.start()
        # Models a completed window committed before INSERT batch_items.
        with self.store.db:
            self.store.db.execute('DELETE FROM batch_items')
        self.assertFalse(w.status(self.store, bid)['discovery_finalized'])
        with patch.object(batches, 'discover', side_effect=AssertionError('No search replay')):
            result = w.advance(self.store, bid)
        self.assertTrue(result['discovery_finalized'])
        self.assertEqual(result['candidate_links'], 1)

    def test_material_crash_reservation_is_never_retried(self):
        bid = self.through_screening()
        with patch.object(screening, 'prepare_reading', side_effect=KeyboardInterrupt), self.assertRaises(KeyboardInterrupt):
            w.advance(self.store, bid, allow_network=True)
        with patch.object(screening, 'read_packet', side_effect=AssertionError('No material retry')):
            report = w.advance(self.store, bid, allow_network=True)
        self.assertEqual(report['status'], 'complete_with_holds')
        self.assertEqual(report['items'][0]['workflow_reason'], 'reading-started-outcome-unknown')

    def test_lost_packet_output_reopens_same_handoff_and_expiry_blocks(self):
        bid = self.start(); first, _ = self.packet(bid, 'screening')
        with Store(self.store.root) as reopened:
            second = w.advance(reopened, bid)
        self.assertEqual(first['claim_id'], second['claim_id'])
        self.assertEqual(first['issued'], second['issued'])
        self.assertFalse(second['redispatch_allowed'])
        with patch.object(handoff, '_time', return_value=first['expires'] + 1):
            report = w.advance(self.store, bid)
        self.assertEqual(report['status'], 'hold')
        self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM screening_handoffs').fetchone()[0], 1)

    def assert_return_recovery(self, stage, bid):
        _, response = self.packet(bid, stage)
        with patch.object(w, '_ingest', side_effect=KeyboardInterrupt), self.assertRaises(KeyboardInterrupt):
            w.submit(self.store, bid, stage, response)
        report = w.status(self.store, bid)
        rid = report['returns'][-1]['id']
        self.assertEqual(report['status'], 'hold')
        with patch.object(batches, 'run', side_effect=AssertionError('No retrieval')):
            with Store(self.store.root) as reopened:
                self.assertEqual(w.recover(reopened, bid, rid)['status'], 'complete')
        self.assertEqual(w.submit(self.store, bid, stage, response)['return_id'], rid)

    def test_saved_screening_return_recovers_after_process_reopen(self):
        self.assert_return_recovery('screening', self.start())

    def test_saved_reading_return_recovers_after_process_reopen(self):
        self.assert_return_recovery('reading', self.through_material())

    def test_saved_evidence_return_recovers_after_process_reopen(self):
        self.assert_return_recovery('evidence', self.through_reading())

    def test_all_stage_commits_survive_ack_loss_without_duplicate_events(self):
        bid = self.start()
        for stage, module, method, event in [('screening', handoff, 'submit', 'reading-triage'),
                                             ('reading', screening, 'submit_reading', 'reading-assessment-recorded'),
                                             ('evidence', qualification, 'submit', 'evidence-proposal-recorded')]:
            with self.subTest(stage=stage):
                if stage == 'reading':
                    w.advance(self.store, bid, allow_network=True, fetch=lambda _: test_qualification.XML)
                _, response = self.packet(bid, stage)
                original = getattr(module, method)
                def lose_ack(*args, **kwargs):
                    original(*args, **kwargs)
                    raise KeyboardInterrupt()
                with patch.object(module, method, side_effect=lose_ack), self.assertRaises(KeyboardInterrupt):
                    w.submit(self.store, bid, stage, response)
                rid = w.status(self.store, bid)['returns'][-1]['id']
                w.recover(self.store, bid, rid)
                table = 'events' if stage == 'screening' else 'batch_events'
                self.assertEqual(self.store.db.execute(f'SELECT COUNT(*) FROM {table} WHERE action=?', (event,)).fetchone()[0], 1)

    def test_invalid_return_is_preserved_and_cannot_be_replaced(self):
        bid = self.through_material(); _, response = self.packet(bid, 'reading')
        response['statements'][0]['segment_sha256'] = '0' * 64
        with self.assertRaises(ValueError):
            w.submit(self.store, bid, 'reading', response)
        report = w.status(self.store, bid)
        rid = report['returns'][-1]['id']
        with self.assertRaises(ValueError):
            w.recover(self.store, bid, rid)
        response['statements'][0]['text'] = 'Correction must not overwrite saved intent'
        with self.assertRaisesRegex(ValueError, 'Unresolved saved return'):
            w.submit(self.store, bid, 'reading', response)
        self.assertEqual(w.advance(self.store, bid)['status'], 'hold')

    def test_reading_hold_does_not_issue_b3_packet(self):
        bid = self.through_material(); _, response = self.packet(bid, 'reading')
        response['next_action'] = 'hold'
        w.submit(self.store, bid, 'reading', response)
        with patch.object(qualification, 'issue', side_effect=AssertionError('Hold is terminal')):
            report = w.advance(self.store, bid)
        self.assertEqual(report['status'], 'complete_with_holds')
        self.assertFalse(report['all_evidence_reviews_recorded'])
        self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM evidence_packets').fetchone()[0], 0)

    def test_screening_reject_and_cap_remain_visible(self):
        bid = self.start(records=[fixtures.article('1', abstractText='One'), fixtures.article('2', abstractText='Two')], max_screenings=1)
        issued, response = self.packet(bid, 'screening')
        response['decision'] = 'reject'
        w.submit(self.store, bid, 'screening', response)
        w.advance(self.store, bid)  # Existing selector records cap deferral.
        report = w.status(self.store, bid)
        self.assertEqual(report['item_stages'], {'rejected': 1, 'deferred': 1})
        self.assertEqual(report['status'], 'complete_with_holds')

    def test_stale_source_and_changed_xml_are_visible_holds(self):
        bid = self.through_material()
        issued, _ = self.packet(bid, 'reading')
        (Path(issued['material']['resolved_directory']) / 'source.xml').write_bytes(b'changed')
        self.assertEqual(w.status(self.store, bid)['item_stages'], {'hold': 1})
        with self.store.db:
            self.store.db.execute('UPDATE candidates SET current=0')
        self.assertIn('stale', w.status(self.store, bid)['items'][0]['workflow_reason'])

    def test_explicit_hold_cannot_be_cleared_or_resumed(self):
        bid = self.start()
        w.hold(self.store, bid, 'Operator: preserve this interrupted review')
        with self.assertRaisesRegex(ValueError, 'held'):
            w.advance(self.store, bid, allow_network=True)
        with self.assertRaisesRegex(ValueError, 'retained'):
            w.hold(self.store, bid, 'Try again')
        self.assertEqual(w.status(self.store, bid)['status'], 'hold')

    def test_material_cap_is_visible_without_attempting_another_read(self):
        bid = self.start(records=[fixtures.article('1', pmcid='PMC1', abstractText='One'),
                                  fixtures.article('2', pmcid='PMC2', abstractText='Two')], max_full_reads=1)
        for _ in range(2):
            _, response = self.packet(bid, 'screening')
            w.submit(self.store, bid, 'screening', response)
        w.advance(self.store, bid, allow_network=True, fetch=lambda _: test_qualification.XML)
        _, response = self.packet(bid, 'reading')
        response['next_action'] = 'hold'
        w.submit(self.store, bid, 'reading', response)
        with patch.object(screening, 'read_packet', side_effect=AssertionError('Cap must be retained')):
            report = w.advance(self.store, bid, allow_network=True)
        self.assertEqual(report['item_stages'], {'hold': 1, 'deferred': 1})
        self.assertEqual(report['status'], 'complete_with_holds')

    def test_evidence_packet_reopen_and_readonly_review_export(self):
        bid = self.through_reading(); first, record = self.packet(bid, 'evidence')
        with Store(self.store.root) as reopened:
            second = w.advance(reopened, bid)
        self.assertEqual(first, second)
        w.submit(self.store, bid, 'evidence', record)
        with w.readonly(self.store.root) as readonly:
            report = w.status(readonly, bid)
        self.assertEqual(report['items'][0]['evidence_review']['data']['recommendation'], 'hold')
        self.assertEqual(report['items'][0]['evidence_review']['actor'], 'fixture-agent')

    def test_stale_active_handoff_is_not_presented_again(self):
        bid = self.start(); self.packet(bid, 'screening')
        with self.store.db:
            self.store.db.execute('UPDATE candidates SET current=0')
        with patch.object(handoff, 'packet', side_effect=AssertionError('No stale packet')):
            report = w.advance(self.store, bid)
        self.assertEqual(report['status'], 'hold')

    def test_empty_result_is_complete_without_implying_evidence_review(self):
        bid = self.start(records=[])
        report = w.advance(self.store, bid)
        self.assertEqual(report['status'], 'complete')
        self.assertTrue(report['discovery_complete'])
        self.assertFalse(report['all_evidence_reviews_recorded'])
        self.assertFalse(report['claim_validated'])

    def test_coordinator_lock_refuses_overlapping_mutation(self):
        bid = self.start()
        with w._exclusive(self.store), self.assertRaisesRegex(ValueError, 'busy'):
            w.advance(self.store, bid)

    def test_cli_create_freezes_without_network_and_refuses_second_catalog_batch(self):
        config = json.loads((Path(__file__).resolve().parents[1] / 'configs/search_profiles.json').read_text())
        profile_name, profile = next(iter(config['profiles'].items()))
        ctx = fixtures.context()
        ctx['questions'] = [{**ctx['questions'][0], 'rq_id': rq} for rq in profile['rq_ids']]
        from weft.identity import digest
        ctx['catalog_sha256'] = digest(ctx['questions'])
        args = ['workflow-create', '--repo', str(Path(self.temp.name)), '--store', str(self.store.root),
                '--profile', profile_name, '--actor', 'fixture-agent', '--streams', 'broad',
                '--since', '2026-10-01', '--until', '2026-10-02']
        with patch('weft.__main__.build_context', return_value=ctx), patch.object(batches, 'run', side_effect=AssertionError('No search during creation')):
            with patch('sys.stdout', new_callable=io.StringIO) as out:
                self.assertEqual(main(args), 0)
            report = json.loads(out.getvalue())
            self.assertEqual(report['status'], 'ready')
            with patch('sys.stderr', new_callable=io.StringIO):
                self.assertEqual(main(args), 1)
        self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM batches').fetchone()[0], 1)

    def test_legacy_catalog_not_adopted_and_can_be_viewed_without_writes(self):
        bid = self.create()
        test_batches.BatchTests.run_batch(self, bid)
        before = self.store.db.total_changes
        with self.assertRaisesRegex(ValueError, 'fresh'):
            w.initialize(self.store, bid, 'fixture-agent')
        self.assertEqual(before, self.store.db.total_changes)
        with w.readonly(self.store.root) as readonly:
            report = w.status(readonly, bid)
            self.assertEqual(report['status'], 'hold')
            self.assertIn('Unmanaged', report['blockers'][0])
        self.assertFalse(w._has(self.store, 'workflow_binding'))

    def test_restored_catalog_inactive_but_exportable(self):
        bid = self.through_material()
        target = Path(self.temp.name) / 'restored'
        shutil.copytree(self.store.root, target)
        before = hashlib.sha256((target / 'catalog.sqlite').read_bytes()).hexdigest()
        with w.readonly(target) as restored:
            report = w.status(restored, bid)
            self.assertIn('inactive', report['blockers'][0])
            result = w.export(restored, bid, Path(self.temp.name) / 'restored-view')
        with patch('sys.stderr', new_callable=io.StringIO):
            self.assertEqual(main(['workflow-advance', '--store', str(target), '--batch', bid]), 1)
        self.assertEqual(before, hashlib.sha256((target / 'catalog.sqlite').read_bytes()).hexdigest())
        self.assertEqual(result['status'], 'exported')

    def test_private_export_escapes_source_and_manifest_is_last(self):
        bid = self.start(records=[fixtures.article(title='<script>alert(1)</script>', abstractText='Fixture')])
        target = Path(self.temp.name) / 'export'
        before = self.store.db.total_changes
        with w.readonly(self.store.root) as readonly:
            w.export(readonly, bid, target)
        self.assertEqual(before, self.store.db.total_changes)
        html = (target / 'index.html').read_text(encoding='utf-8')
        self.assertNotIn('<script>', html)
        self.assertIn('&lt;script&gt;', html)
        self.assertIn("default-src 'none'", html)
        manifest = json.loads((target / 'manifest.json').read_text())
        for name, sha in manifest['files'].items():
            self.assertEqual(hashlib.sha256((target / name).read_bytes()).hexdigest(), sha)
        self.assertTrue(json.loads((target / 'status.json').read_text())['private'])
        with self.assertRaises(FileExistsError):
            w.export(self.store, bid, target)

    def test_cli_status_missing_store_does_not_create_and_valid_status_is_read_only(self):
        missing = Path(self.temp.name) / 'absent'
        with patch('sys.stderr', new_callable=io.StringIO):
            self.assertEqual(main(['workflow-status', '--store', str(missing), '--batch', 'missing']), 1)
        self.assertFalse(missing.exists())
        bid = self.start()
        before = hashlib.sha256((self.store.root / 'catalog.sqlite').read_bytes()).hexdigest()
        with patch('sys.stdout', new_callable=io.StringIO) as out:
            self.assertEqual(main(['workflow-status', '--store', str(self.store.root), '--batch', bid]), 0)
        self.assertFalse(json.loads(out.getvalue())['automatic_cloud_launch'])
        self.assertEqual(before, hashlib.sha256((self.store.root / 'catalog.sqlite').read_bytes()).hexdigest())


if __name__ == '__main__':
    unittest.main()
