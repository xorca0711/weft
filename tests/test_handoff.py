import copy
import io
import json
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch

from weft import batches, handoff, screening
from weft.__main__ import main
from weft.discovery import Store
import test_batches


class HandoffTests(unittest.TestCase):
    setUp = test_batches.BatchTests.setUp
    create = test_batches.BatchTests.create
    run_batch = test_batches.BatchTests.run_batch
    response = test_batches.BatchTests.response

    def prepared(self):
        bid = self.create()
        self.run_batch(bid)
        handoff.initialize(self.store)
        result = handoff.claim(self.store, bid, 'fixture-agent')
        return bid, result, self.response(copy.deepcopy(result['issued']))

    def test_explicit_binding_and_invalid_bounds(self):
        bid = self.create()
        self.run_batch(bid)
        with self.assertRaisesRegex(ValueError, 'handoff-init'):
            handoff.claim(self.store, bid, 'fixture')
        first = handoff.initialize(self.store)
        self.assertEqual(handoff.initialize(self.store)['binding'], first['binding'])
        for limit in [0, 3601, True]:
            with self.assertRaises(ValueError):
                handoff.claim(self.store, bid, 'fixture', lease_seconds=limit)

    def test_single_claim_persists_after_reopen_and_lost_stdout(self):
        bid, claimed, _ = self.prepared()
        with Store(self.store.root) as reopened:
            report = handoff.status(reopened)
            self.assertEqual(report['claims'][0]['id'], claimed['claim_id'])
            self.assertEqual(handoff.packet(reopened, claimed['claim_id'])['issued'], claimed['issued'])
            with self.assertRaisesRegex(ValueError, 'Unresolved handoff'):
                handoff.claim(reopened, bid, 'another-worker')
        self.assertFalse(claimed['model_invoked'])

    def test_advisory_lock_prevents_parallel_claim(self):
        bid, _, _ = self.prepared()
        with batches.exclusive(self.store, name='.handoff.lock'):
            with self.assertRaisesRegex(ValueError, 'busy'):
                handoff.claim(self.store, bid, 'parallel')

    def test_exact_response_replay_only_and_no_duplicate_events(self):
        bid, claim, response = self.prepared()
        handoff.submit(self.store, claim['claim_id'], response)
        self.assertEqual(handoff.submit(self.store, claim['claim_id'], response)['screening']['status'], 'already_recorded')
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM batch_events WHERE action='handoff-complete'").fetchone()[0], 1)
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM events WHERE action='reading-triage'").fetchone()[0], 1)
        with self.assertRaisesRegex(ValueError, 'Different response'):
            handoff.submit(self.store, claim['claim_id'], {**response, 'reason': 'Edited'})
        self.assertEqual(handoff.claim(self.store, bid, 'fixture-agent')['status'], 'no-packet')

    def test_crash_after_saved_intent_recovers_without_agent_replay(self):
        _, claim, response = self.prepared()
        with patch.object(screening, 'submit', side_effect=RuntimeError('simulated interruption')):
            with self.assertRaises(RuntimeError):
                handoff.submit(self.store, claim['claim_id'], response)
        self.assertEqual(handoff.status(self.store)['claims'][0]['state'], 'return_pending')
        with patch.object(handoff, '_time', return_value=claim['expires'] + 1):
            recovered = handoff.recover(self.store, claim['claim_id'])
        self.assertEqual(recovered['status'], 'complete')
        self.assertFalse(recovered['model_invoked'])

    def test_crash_after_ingestion_before_ack_recovers_exact_replay(self):
        _, claim, response = self.prepared()
        original = batches.event

        def interrupted(store, bid, action, record):
            if action == 'handoff-complete':
                raise RuntimeError('acknowledgement lost')
            return original(store, bid, action, record)

        with patch.object(batches, 'event', side_effect=interrupted):
            with self.assertRaises(RuntimeError):
                handoff.submit(self.store, claim['claim_id'], response)
        self.assertEqual(handoff.recover(self.store, claim['claim_id'])['screening']['status'], 'already_recorded')
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM events WHERE action='reading-triage'").fetchone()[0], 1)

    def test_expired_claim_is_held_without_reassignment(self):
        bid, claim, response = self.prepared()
        with patch.object(handoff, '_time', return_value=claim['expires']):
            with self.assertRaisesRegex(ValueError, 'Expired'):
                handoff.submit(self.store, claim['claim_id'], response)
            self.assertTrue(handoff.status(self.store)['claims'][0]['expired'])
            with self.assertRaisesRegex(ValueError, 'Unresolved'):
                handoff.claim(self.store, bid, 'replacement')
        with self.assertRaisesRegex(ValueError, 'No saved response'):
            handoff.recover(self.store, claim['claim_id'])

    def test_invalid_citation_intent_stays_held_and_blocks_replacement(self):
        bid, claim, response = self.prepared()
        response['citations'][0]['locator'] = '/fabricated'
        with self.assertRaisesRegex(ValueError, 'citation'):
            handoff.submit(self.store, claim['claim_id'], response)
        self.assertEqual(handoff.status(self.store)['claims'][0]['state'], 'return_pending')
        with self.assertRaisesRegex(ValueError, 'Unresolved'):
            handoff.claim(self.store, bid, 'replacement')
        with self.assertRaisesRegex(ValueError, 'citation'):
            handoff.recover(self.store, claim['claim_id'])

    def test_wrong_actor_and_candidate_cannot_change_intent(self):
        _, claim, response = self.prepared()
        for changes in [{'actor': 'other'}, {'candidate_id': 'other'}, {'packet_sha256': 'bad'}]:
            with self.assertRaisesRegex(ValueError, 'does not match'):
                handoff.submit(self.store, claim['claim_id'], {**response, **changes})
        self.assertIsNone(handoff.status(self.store)['claims'][0]['response_sha'])

    def test_changed_source_and_saved_response_fail_closed(self):
        _, claim, response = self.prepared()
        with patch.object(screening, 'submit', side_effect=RuntimeError('interrupted')):
            with self.assertRaises(RuntimeError):
                handoff.submit(self.store, claim['claim_id'], response)
        with self.store.db:
            self.store.db.execute("UPDATE candidates SET evidence_sha='changed'")
        with self.assertRaises(ValueError):
            handoff.recover(self.store, claim['claim_id'])
        with self.store.db:
            self.store.db.execute("UPDATE screening_handoffs SET response_json='{}'")
        with self.assertRaisesRegex(ValueError, 'Saved response changed'):
            handoff.recover(self.store, claim['claim_id'])

    def test_restored_copy_and_host_change_cannot_activate(self):
        self.prepared()
        clone = Path(self.temp.name) / 'read-only-restore'
        shutil.copytree(self.store.root, clone)
        with Store(clone) as restored:
            with self.assertRaisesRegex(ValueError, 'inactive'):
                handoff.initialize(restored)
        with patch.object(handoff.socket, 'gethostname', return_value='another-host'):
            with self.assertRaisesRegex(ValueError, 'inactive'):
                handoff.status(self.store)

    def test_cli_claim_to_submission(self):
        bid = self.create()
        self.run_batch(bid)
        common = ['--store', str(self.store.root)]
        with patch('sys.stdout', new_callable=io.StringIO):
            self.assertEqual(main(['handoff-init', *common]), 0)
        with patch('sys.stdout', new_callable=io.StringIO) as output:
            self.assertEqual(main(['handoff-claim', *common, '--batch', bid, '--actor', 'fixture-agent']), 0)
            issued = json.loads(output.getvalue())
        response_path = Path(self.temp.name) / 'response.json'
        response_path.write_text(json.dumps(self.response(issued['issued'])), encoding='utf-8')
        with patch('sys.stdout', new_callable=io.StringIO) as output:
            self.assertEqual(main(['handoff-submit', *common, '--claim', issued['claim_id'], '--assessment', str(response_path)]), 0)
            self.assertFalse(json.loads(output.getvalue())['scientific_execution_allowed'])
