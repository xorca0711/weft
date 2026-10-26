import unittest
from unittest.mock import patch

import test_author_worker as fixtures
from weft import author_attempts as attempts, science_adapter as adapter
from weft.jobs import JobError


class AuthorAttemptTests(unittest.TestCase):
    setUp = fixtures.AuthorWorkerTests.setUp
    file_ref = fixtures.AuthorWorkerTests.file_ref
    base_record = fixtures.AuthorWorkerTests.base_record
    put = fixtures.AuthorWorkerTests.put
    source = fixtures.AuthorWorkerTests.source
    case = fixtures.AuthorWorkerTests.case
    data = fixtures.AuthorWorkerTests.data
    plan = fixtures.AuthorWorkerTests.plan
    build = fixtures.AuthorWorkerTests.build
    request = fixtures.AuthorWorkerTests.request
    prepared = fixtures.AuthorWorkerTests.prepared

    def test_reservation_checkpoint_restart_and_pristine_abandon(self):
        ref = self.prepared()
        with patch('subprocess.run', side_effect=AssertionError('No execution')):
            with attempts.open_attempts(self.ws, clock=lambda: 10) as ctl:
                claim = ctl.reserve(ref)
                self.assertFalse(ctl.status(claim)['dispatch_authorized'])
            with attempts.open_attempts(self.ws, clock=lambda: 11) as ctl:
                self.assertEqual(ctl.status(claim)['state'], 'running')
                self.assertNotIn('lease_token', ctl.status(claim))
                ctl.abandon_unstarted(claim)
                self.assertEqual(ctl.status(claim)['state'], 'preparation_abandoned')
                with self.assertRaises(JobError): ctl.reserve(ref)

    def test_shared_slot_blocks_fixture_and_duplicate_reservation(self):
        ref = self.prepared()
        with attempts.open_attempts(self.ws) as ctl:
            ctl.reserve(ref)
            with self.assertRaises(JobError): ctl.reserve(ref)
            replay = adapter.FixtureReplay(self.ws, ctl.ledger)
            with self.assertRaises(JobError): replay.begin(self.pkg)

    def test_fixture_reservation_blocks_author(self):
        ref = self.prepared()
        with adapter.open_replay(self.ws) as replay:
            replay.begin(self.pkg)
            with self.assertRaises(JobError): attempts.AuthorAttempts(self.ws, replay.ledger).reserve(ref)

    def test_supplied_success_retains_slot_and_rejects_legacy_release(self):
        ref = self.prepared()
        with attempts.open_attempts(self.ws) as ctl:
            claim = ctl.reserve(ref)
            ctl.observe(claim, {'outcome': 'success', 'all_processes_dead': True})
            self.assertEqual(ctl.status(claim)['state'], 'unknown')
            with self.assertRaises(JobError): ctl.abandon_unstarted(claim)
            with self.assertRaises(JobError): ctl.ledger.reconcile(claim['attempt_id'], claim['lease_token'],
                outcome='cancelled', receipt_ref='0'*64)
            with self.assertRaises(JobError): ctl.ledger.bind_executor(claim, {'job_id': claim['job_id'],
                'attempt_id': claim['attempt_id']})

    def test_expiry_and_cancel_never_prove_termination(self):
        ref = self.prepared(); now = [10]
        with attempts.open_attempts(self.ws, clock=lambda: now[0]) as ctl:
            claim = ctl.reserve(ref); ctl.ledger.cancel(claim['job_id'])
            with self.assertRaises(JobError): ctl.abandon_unstarted(claim)
            now[0] = 41; self.assertEqual(ctl.ledger.expire(), 1)
            self.assertEqual(ctl.status(claim)['state'], 'unknown')

    def test_bad_token_and_checkpoint_change_rejected(self):
        ref = self.prepared()
        with attempts.open_attempts(self.ws) as ctl:
            claim = ctl.reserve(ref)
            with self.assertRaises(JobError): ctl.status({**claim, 'lease_token': 'forged'})
            path = self.ws.root / ctl._prefix(claim) / 'checkpoint.json'
            path.write_text('{}')
            with self.assertRaises(JobError): ctl.abandon_unstarted(claim)

    def test_failed_checkpoint_rolls_back_db_but_never_reuses_orphan(self):
        ref = self.prepared()
        with attempts.open_attempts(self.ws) as ctl:
            with patch.object(attempts.ev, 'write_new', side_effect=OSError('disk full')):
                with self.assertRaises(OSError): ctl.reserve(ref)
            self.assertEqual(ctl.ledger.db.execute('SELECT COUNT(*) FROM attempts').fetchone()[0], 0)
            with self.assertRaises(FileExistsError): ctl.reserve(ref)

    def test_recovery_available_after_input_drift_without_new_admission(self):
        ref = self.prepared()
        with attempts.open_attempts(self.ws) as ctl:
            claim = ctl.reserve(ref)
            (self.inputs/'counts.csv').write_bytes(b'changed')
            ctl.abandon_unstarted(claim)
            with self.assertRaises(ValueError): ctl.reserve(ref)


if __name__ == '__main__': unittest.main()
