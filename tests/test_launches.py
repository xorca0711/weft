from contextlib import closing
import hashlib
import io
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
from unittest.mock import patch

from weft import launches
from weft.__main__ import main


class LaunchTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.path = self.root / 'launches.sqlite'
        launches.initialize(self.path)
        self.journal = launches.LaunchJournal(self.path)
        self.addCleanup(self.journal.db.close)
        self.prompt = b'Synthetic fixture only. Do not launch anything.\n'
        self.spec = {'schema_version': 1, 'kind': 'synthetic-qualification',
                     'operation_key': 'fixture-occurrence-1', 'repository': 'fixture/weft',
                     'source_revision': 'a' * 40, 'prompt_sha256': hashlib.sha256(self.prompt).hexdigest(),
                     'environment_sha256': 'b' * 64, 'policy_sha256': 'c' * 64,
                     'account_scope_sha256': 'd' * 64, 'max_submissions': 1}

    def prepare(self):
        return self.journal.prepare(self.spec, self.prompt)

    def receipt(self):
        return {'operation_key': self.spec['operation_key'],
                'spec_sha256': self.journal.status(self.spec['operation_key'])['spec_sha256'],
                'task_id': 'synthetic-task-1', 'observation_sha256': 'e' * 64}

    def test_prepare_is_idempotent_but_key_cannot_be_rebound(self):
        first = self.prepare()
        self.assertEqual(self.prepare(), first)
        changed = {**self.spec, 'source_revision': 'f' * 40}
        with self.assertRaisesRegex(ValueError, 'different launch intent'):
            self.journal.prepare(changed, self.prompt)
        self.assertEqual(self.journal.db.execute('SELECT COUNT(*) FROM launch_events').fetchone()[0], 1)
        self.assertFalse(first['dispatch_authorized'])

    def test_strict_synthetic_scope_and_exact_prompt(self):
        for changes in [{'kind': 'science'}, {'max_submissions': 2}, {'max_submissions': True},
                        {'schema_version': True}, {'extra': 'unreviewed'}, {'policy_sha256': 'unknown'}]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.journal.prepare({**self.spec, **changes}, self.prompt)
        for prompt in [b'', self.prompt + b'changed', b'x' * 100001]:
            with self.assertRaises(ValueError):
                self.journal.prepare(self.spec, prompt)

    def test_changed_current_environment_or_account_cannot_begin(self):
        self.prepare()
        for field in ['environment_sha256', 'policy_sha256', 'account_scope_sha256', 'source_revision']:
            changed = {**self.spec, field: 'f' * len(self.spec[field])}
            with self.assertRaisesRegex(ValueError, 'differs'):
                self.journal.begin(changed, self.prompt)
        self.assertEqual(self.journal.status(self.spec['operation_key'])['state'], 'prepared')

    def test_lost_begin_output_and_reopen_never_resubmit(self):
        self.prepare()
        self.journal.begin(self.spec, self.prompt)
        with launches.LaunchJournal(self.path) as reopened:
            self.assertEqual(reopened.status(self.spec['operation_key'])['state'], 'awaiting_ack')
            with self.assertRaisesRegex(ValueError, 'never resubmit'):
                reopened.begin(self.spec, self.prompt)
            self.assertFalse(reopened.status(self.spec['operation_key'])['provider_called'])

    def test_uncertainty_blocks_other_occurrence_and_race_is_serialized(self):
        self.prepare()
        other = {**self.spec, 'operation_key': 'fixture-occurrence-2'}
        self.journal.prepare(other, self.prompt)
        barrier = threading.Barrier(2)
        results = []
        def begin(spec):
            with launches.LaunchJournal(self.path) as journal:
                barrier.wait(timeout=5)
                try:
                    results.append(journal.begin(spec, self.prompt)['state'])
                except ValueError as exc:
                    results.append(str(exc))
        threads = [threading.Thread(target=begin, args=(s,)) for s in [self.spec, other]]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)
            self.assertFalse(thread.is_alive())
        self.assertEqual(results.count('awaiting_ack'), 1)
        self.assertTrue(any('Another uncertain' in r for r in results))

    def test_exact_acknowledgement_replay_and_conflict(self):
        self.prepare()
        receipt = self.receipt()
        with self.assertRaisesRegex(ValueError, 'begun submission'):
            self.journal.acknowledge(self.spec['operation_key'], receipt)
        self.journal.begin(self.spec, self.prompt)
        acknowledged = self.journal.acknowledge(self.spec['operation_key'], receipt)
        self.assertEqual(self.journal.acknowledge(self.spec['operation_key'], receipt), acknowledged)
        with self.assertRaisesRegex(ValueError, 'Conflicting'):
            self.journal.acknowledge(self.spec['operation_key'], {**receipt, 'task_id': 'different-task'})
        with self.assertRaisesRegex(ValueError, 'never resubmit'):
            self.journal.begin(self.spec, self.prompt)
        self.assertEqual(self.journal.db.execute("SELECT COUNT(*) FROM launch_events WHERE action='acknowledgement-recorded'").fetchone()[0], 1)

    def test_bad_acknowledgement_keeps_hold(self):
        self.prepare()
        self.journal.begin(self.spec, self.prompt)
        for changes in [{'operation_key': 'wrong'}, {'spec_sha256': 'f' * 64},
                        {'task_id': ''}, {'observation_sha256': 'unknown'}, {'extra': True}]:
            with self.assertRaises(ValueError):
                self.journal.acknowledge(self.spec['operation_key'], {**self.receipt(), **changes})
        self.assertEqual(self.journal.status(self.spec['operation_key'])['state'], 'awaiting_ack')

    def test_restore_is_observable_but_inactive(self):
        self.prepare()
        self.journal.begin(self.spec, self.prompt)
        copy_path = self.root / 'restored.sqlite'
        with closing(sqlite3.connect(copy_path)) as destination:
            self.journal.db.backup(destination)
        before = copy_path.read_bytes()
        with launches.LaunchJournal(copy_path) as restored:
            self.assertFalse(restored.status(self.spec['operation_key'])['active_binding'])
            with self.assertRaisesRegex(ValueError, 'inactive'):
                restored.acknowledge(self.spec['operation_key'], self.receipt())
        self.assertEqual(before, copy_path.read_bytes())
        with patch.object(launches.socket, 'gethostname', return_value='other-host'):
            with self.assertRaisesRegex(ValueError, 'inactive'):
                self.journal.begin(self.spec, self.prompt)

    def test_existing_unrelated_or_partial_database_is_preserved(self):
        unrelated = self.root / 'unrelated.sqlite'
        with closing(sqlite3.connect(unrelated)) as db, db:
            db.execute('CREATE TABLE other(value TEXT)')
            db.execute("INSERT INTO other VALUES('preserve')")
        before = unrelated.read_bytes()
        with self.assertRaises(FileExistsError):
            launches.initialize(unrelated)
        with self.assertRaises(sqlite3.OperationalError):
            launches.LaunchJournal(unrelated)
        self.assertEqual(before, unrelated.read_bytes())
        partial = self.root / 'partial.sqlite'
        partial.touch()
        with self.assertRaises(FileExistsError):
            launches.initialize(partial)

    def test_saved_spec_and_receipt_tampering_are_detected(self):
        self.prepare()
        self.journal.begin(self.spec, self.prompt)
        self.journal.acknowledge(self.spec['operation_key'], self.receipt())
        self.journal.db.execute("UPDATE launch_intents SET receipt_json='{}'")
        with self.assertRaisesRegex(ValueError, 'acknowledgement changed'):
            self.journal.status(self.spec['operation_key'])
        self.journal.db.execute("UPDATE launch_intents SET spec_json='{}'")
        with self.assertRaisesRegex(ValueError, 'specification changed'):
            self.journal.status(self.spec['operation_key'])

    def test_interrupted_transaction_does_not_emit_a_begin_result(self):
        self.prepare()
        with patch.object(self.journal, '_event', side_effect=RuntimeError('synthetic interruption')):
            with self.assertRaises(RuntimeError):
                self.journal.begin(self.spec, self.prompt)
        self.assertEqual(self.journal.status(self.spec['operation_key'])['state'], 'prepared')
        self.assertEqual(self.journal.db.execute('SELECT COUNT(*) FROM launch_events').fetchone()[0], 1)

    def test_cli_records_without_dispatch(self):
        spec = self.root / 'spec.json'
        spec.write_text(json.dumps(self.spec), encoding='utf-8')
        prompt = self.root / 'prompt.txt'
        prompt.write_bytes(self.prompt)
        args = ['--journal', str(self.path), '--spec', str(spec), '--prompt', str(prompt)]
        for command in ['launch-prepare', 'launch-begin']:
            with patch('sys.stdout', new_callable=io.StringIO) as output:
                self.assertEqual(main([command, *args]), 0)
                self.assertFalse(json.loads(output.getvalue())['provider_called'])
        with patch('sys.stderr', new_callable=io.StringIO):
            self.assertEqual(main(['launch-begin', *args]), 1)
