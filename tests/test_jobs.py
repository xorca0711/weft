import copy
import hashlib
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest

from weft.jobs import JobError, JobLedger, validate_packet


class JobTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.data = self.root / "input"
        self.data.mkdir()
        (self.data / "fixture.txt").write_bytes(b"synthetic fixture")
        self.clock = [100.0]
        self.path = self.root / "jobs.sqlite"
        self.packet = {"schema_version": 1, "kind": "synthetic-qualification",
            "paper_version_sha256": "a"*64, "context_sha256": "b"*64,
            "policy_sha256": "c"*64, "contract_sha256": "d"*64,
            "executor_sha256": "e"*64, "max_attempts": 2, "lease_seconds": 30,
            "inputs": [{"path": "fixture.txt", "bytes": 17,
                        "sha256": hashlib.sha256(b"synthetic fixture").hexdigest()}]}
        self.ledger = JobLedger(self.path, clock=lambda: self.clock[0])
        self.addCleanup(self.ledger.db.close)
        self.key = self.ledger.submit(self.packet)

    def claim(self, ledger=None, key=None, **kwargs):
        return (ledger or self.ledger).claim(key or self.key, inputs_root=self.data,
            current_context_sha256=kwargs.get("context", "b"*64),
            current_policy_sha256=kwargs.get("policy", "c"*64))

    def terminal(self, attempt, outcome="failed", **kwargs):
        self.ledger.reconcile(attempt["attempt_id"], kwargs.get("token", attempt["lease_token"]),
                              outcome=outcome, receipt_ref="f"*64)

    def test_scientific_packet_and_shell_fields_rejected(self):
        for change in ({"kind": "scientific"}, {"command": ["python", "science.py"]}):
            with self.assertRaises(JobError):
                self.ledger.submit({**self.packet, **change})

    def test_repeat_submit_does_not_duplicate_or_reset_state(self):
        self.claim()
        self.assertEqual(self.ledger.submit(copy.deepcopy(self.packet)), self.key)
        self.assertEqual(self.ledger.status(self.key)["state"], "running")
        self.assertEqual(self.ledger.db.execute("SELECT COUNT(*) FROM events WHERE action='submitted'").fetchone()[0], 1)

    def test_scientific_identity_or_parameter_change_creates_new_job(self):
        for change in ({"context_sha256": "9"*64}, {"contract_sha256": "8"*64}, {"max_attempts": 3}):
            self.assertNotEqual(self.ledger.submit({**self.packet, **change}), self.key)

    def test_invalid_hash_bounds_and_path_rejected(self):
        for change in ({"lease_seconds": True}, {"max_attempts": 4}, {"context_sha256": "bad"}):
            with self.assertRaises(JobError):
                self.ledger.submit({**self.packet, **change})
        for name in ("../fixture.txt", "/fixture.txt", "x//y", "x:/file"):
            packet = copy.deepcopy(self.packet)
            packet["inputs"][0]["path"] = name
            with self.assertRaises(JobError):
                validate_packet(packet)

    def test_changed_input_blocks_dispatch_without_consuming_attempt(self):
        (self.data / "fixture.txt").write_bytes(b"changed fixture!!")
        with self.assertRaisesRegex(JobError, "hash drift"):
            self.claim()
        self.assertEqual(self.ledger.db.execute("SELECT COUNT(*) FROM attempts").fetchone()[0], 0)

    def test_stale_context_and_policy_block(self):
        for change in ({"context": "a"*64}, {"policy": "d"*64}):
            with self.assertRaisesRegex(JobError, "Stale"):
                self.claim(**change)

    def test_two_clients_cannot_claim_same_slot(self):
        other = self.ledger.submit({**self.packet, "contract_sha256": "7"*64})
        barrier = threading.Barrier(2)
        outcomes = []
        def run(key):
            with JobLedger(self.path, clock=lambda: 100.0) as ledger:
                barrier.wait(timeout=5)
                try:
                    self.claim(ledger=ledger, key=key)
                    outcomes.append("claimed")
                except JobError:
                    outcomes.append("held")
        threads = [threading.Thread(target=run, args=(key,)) for key in (self.key, other)]
        for thread in threads: thread.start()
        for thread in threads: thread.join(timeout=10)
        self.assertEqual(sorted(outcomes), ["claimed", "held"])

    def test_expiry_reserves_slot_and_survives_reopen(self):
        attempt = self.claim()
        self.clock[0] = 130
        self.assertEqual(self.ledger.expire(), 1)
        self.assertEqual(self.ledger.status(self.key)["state"], "held_unknown")
        other = self.ledger.submit({**self.packet, "executor_sha256": "2"*64})
        with JobLedger(self.path, clock=lambda: 131) as reopened:
            with self.assertRaisesRegex(JobError, "unresolved"):
                self.claim(ledger=reopened, key=other)
        self.clock[0] = 132
        self.terminal(attempt)
        self.claim(key=other)

    def test_cancel_request_does_not_release_running_slot(self):
        attempt = self.claim()
        self.ledger.cancel(self.key)
        self.assertEqual(self.ledger.status(self.key)["state"], "cancel_requested")
        other = self.ledger.submit({**self.packet, "executor_sha256": "2"*64})
        with self.assertRaises(JobError): self.claim(key=other)
        self.terminal(attempt, "cancelled")
        self.claim(key=other)

    def test_wrong_lease_or_success_cannot_release_attempt(self):
        attempt = self.claim()
        with self.assertRaises(JobError): self.terminal(attempt, token="wrong")
        with self.assertRaises(JobError): self.terminal(attempt, "complete")
        self.assertEqual(self.ledger.status(self.key)["state"], "running")

    def test_attempt_budget_and_terminal_immutability(self):
        for _ in range(2):
            attempt = self.claim()
            self.terminal(attempt)
            with self.assertRaises(JobError): self.terminal(attempt)
        with self.assertRaisesRegex(JobError, "budget"):
            self.claim()
        self.assertEqual(self.ledger.db.execute("SELECT COUNT(*) FROM attempts").fetchone()[0], 2)

    def test_event_history_and_packet_are_immutable(self):
        for sql in ("UPDATE events SET action='fake'", "DELETE FROM events", "UPDATE jobs SET packet='{}'"):
            with self.assertRaises(sqlite3.IntegrityError): self.ledger.db.execute(sql)

    def test_clock_rollback_holds_dispatch(self):
        self.clock[0] = 99
        with self.assertRaisesRegex(JobError, "backwards"): self.claim()

    def test_queued_cancel_does_not_claim_process_termination(self):
        self.ledger.cancel(self.key)
        self.assertEqual(self.ledger.status(self.key)["state"], "cancelled")
        self.assertEqual(self.ledger.db.execute("SELECT COUNT(*) FROM attempts").fetchone()[0], 0)


if __name__ == "__main__":
    unittest.main()
