"""Synthetic result intake: never dispatch, manufacture authority or resume."""
import copy
import hashlib
import io
import json
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch

from weft import cloud_return as cr, launches
from weft.__main__ import main
from tests import test_launches as legacy


class CloudReturnTests(unittest.TestCase):
    def setUp(self):
        legacy.LaunchTests.setUp(self)
        self.journal.prepare(self.spec, self.prompt)
        self.journal.begin(self.spec, self.prompt)
        self.journal.acknowledge(self.spec['operation_key'], legacy.LaunchTests.receipt(self))
        evidence = self.journal.evidence(self.spec['operation_key'])
        self.contract_path = self.root / 'contract.json'
        self.contract = {'schema_version': 1, 'kind': 'synthetic-return-contract',
            'operation_key': self.spec['operation_key'], 'spec_sha256': evidence['spec_sha256'],
            'frozen_at': '2026-10-20T00:00:00Z', 'expected_tests': ['fixture-' + str(i) for i in range(12)]}
        self.directory = self.root / 'return'
        (self.directory / 'artifacts').mkdir(parents=True)
        self.observation = {'schema_version': 1, 'kind': 'synthetic-runtime-observation',
            'operation_key': self.spec['operation_key'], 'task_id': 'synthetic-task-1',
            'state': 'completed', 'execution_started': True,
            'bindings': {k: self.spec[k] for k in cr.BINDINGS},
            'runtime_capability': 'present', 'policy_enforcement': 'enforced',
            'notes': 'Synthetic fixture assertions only; no real cloud observation.'}
        self.report = {'schema_version': 1, 'kind': 'synthetic-fixture-report', 'cases': [
            {'test_id': name, 'outcome': 'passed', 'reason': 'Synthetic expected result'} for name in self.contract['expected_tests']]}
        self.manifest = {'schema_version': 1, 'kind': 'synthetic-qualification-return',
            'operation_key': self.spec['operation_key'], 'spec_sha256': evidence['spec_sha256'],
            'task_id': 'synthetic-task-1', 'contract_sha256': None,
            'acknowledgement_sha256': evidence['receipt_sha256'], 'returned_at': '2026-10-20T01:00:00Z',
            'files': {}, 'observation_path': 'artifacts/observation.json',
            'test_report_path': 'artifacts/tests.json', 'log_path': 'artifacts/tests.log'}
        self.log = b'Synthetic fixture execution log. No provider was called.\n'
        self.save()

    def write(self, path, value):
        path.write_text(json.dumps(value, indent=2), encoding='utf-8')

    def digest(self, path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def save(self):
        self.write(self.contract_path, self.contract)
        self.contract_sha = self.digest(self.contract_path)
        self.write(self.directory / self.manifest['observation_path'], self.observation)
        self.write(self.directory / self.manifest['test_report_path'], self.report)
        (self.directory / self.manifest['log_path']).write_bytes(self.log)
        self.manifest['contract_sha256'] = self.contract_sha
        self.manifest['files'] = {p.relative_to(self.directory).as_posix():
            {'sha256': self.digest(p), 'bytes': p.stat().st_size}
            for p in (self.directory / 'artifacts').rglob('*') if p.is_file()}
        self.write_manifest()

    def write_manifest(self):
        self.write(self.directory / 'manifest.json', self.manifest)
        self.manifest_sha = self.digest(self.directory / 'manifest.json')

    def verify(self, journal=None, directory=None):
        return cr.verify(journal or self.path, self.spec['operation_key'], self.contract_path,
                         self.contract_sha, directory or self.directory, self.manifest_sha)

    def test_consistent_return_does_not_qualify_runtime_or_change_journal(self):
        before = self.digest(self.path)
        report = self.verify()
        self.assertEqual(report['status'], 'consistent_synthetic_return')
        self.assertEqual(report['reported_outcomes'], {'passed': 12})
        self.assertEqual(report['hold_reasons'], [])
        for flag in cr.FLAGS: self.assertIs(report[flag], False)
        self.assertEqual(report['journal_state'], 'acknowledged')
        self.assertEqual(self.digest(self.path), before)
        self.assertEqual(self.verify(), report)

    def test_completed_turn_with_no_runtime_and_zero_fixtures_stays_held(self):
        self.observation.update(execution_started=False, runtime_capability='absent', policy_enforcement='unknown',
            bindings={key: None for key in cr.BINDINGS})
        self.report['cases'] = []; self.log = b''; self.save()
        report = self.verify()
        self.assertEqual(report['status'], 'hold')
        self.assertEqual(len(report['missing_test_ids']), 12)
        self.assertFalse(report['permission_failure_inferred'])
        self.assertFalse(report['runtime_qualified'])

    def test_unknown_acknowledgement_cannot_be_reconstructed_from_return(self):
        other = self.root / 'uncertain.sqlite'; launches.initialize(other)
        with launches.LaunchJournal(other) as journal:
            journal.prepare(self.spec, self.prompt); journal.begin(self.spec, self.prompt)
        before = self.digest(other)
        with self.assertRaisesRegex(ValueError, 'Acknowledged task required'): self.verify(journal=other)
        self.assertEqual(self.digest(other), before)

    def test_wrong_task_receipt_contract_or_operation_rejected(self):
        original = copy.deepcopy(self.manifest)
        for key, value in [('task_id', 'other-task'), ('acknowledgement_sha256', 'a' * 64),
                           ('contract_sha256', 'a' * 64), ('spec_sha256', 'a' * 64),
                           ('operation_key', 'other-operation')]:
            self.manifest = {**copy.deepcopy(original), key: value}; self.write_manifest()
            with self.subTest(key=key), self.assertRaisesRegex(ValueError, 'bind'): self.verify()

    def test_changed_source_policy_prompt_environment_or_account_stays_held(self):
        original = dict(self.observation['bindings'])
        for key in cr.BINDINGS:
            self.observation['bindings'] = {**original, key: 'f' * (40 if key == 'source_revision' else 64)}
            self.save(); report = self.verify()
            with self.subTest(key=key):
                self.assertEqual(report['status'], 'hold')
                self.assertEqual(report['runtime_binding_comparison'][key], 'mismatch')

    def test_cancelled_failed_running_and_unknown_never_become_completion(self):
        for state in ('held', 'cancelled', 'failed', 'running', 'unknown'):
            self.observation['state'] = state; self.save()
            with self.subTest(state=state): self.assertEqual(self.verify()['status'], 'hold')

    def test_missing_failed_errored_or_skipped_fixtures_cannot_pass(self):
        original = copy.deepcopy(self.report['cases'])
        for outcome in ('failed', 'error', 'skipped', None):
            self.report['cases'] = copy.deepcopy(original)
            if outcome is None: self.report['cases'].pop()
            else: self.report['cases'][0]['outcome'] = outcome
            self.save()
            with self.subTest(outcome=outcome): self.assertEqual(self.verify()['status'], 'hold')

    def test_duplicate_unknown_and_nonexecution_test_results_rejected(self):
        original = copy.deepcopy(self.report['cases'])
        for test_id in ('unknown', original[1]['test_id']):
            self.report['cases'] = copy.deepcopy(original); self.report['cases'][0]['test_id'] = test_id
            self.save()
            with self.subTest(test_id=test_id), self.assertRaisesRegex(ValueError, 'Unknown or duplicate'): self.verify()
        self.report['cases'] = original; self.observation['execution_started'] = False; self.save()
        with self.assertRaisesRegex(ValueError, 'contradict'): self.verify()

    def test_empty_execution_log_stays_held(self):
        self.log = b''; self.save()
        self.assertIn('Execution reported without a retained nonempty log', self.verify()['hold_reasons'])

    def test_tampering_and_partial_transfer_fail_without_journal_write(self):
        before = self.digest(self.path)
        copied = self.root / 'copied'; shutil.copytree(self.directory, copied)
        log = copied / 'artifacts/tests.log'; body = log.read_bytes(); log.write_bytes(body.replace(b'fixture', b'changed'))
        with self.assertRaisesRegex(ValueError, 'changed'): self.verify(directory=copied)
        log.write_bytes(body)
        (copied / 'manifest.json').unlink()
        with self.assertRaises((ValueError, OSError)): self.verify(directory=copied)
        self.assertEqual(self.digest(self.path), before)

    def test_json_replaced_after_inventory_cannot_change_verified_verdict(self):
        original = cr._files
        for name in ('observation_path', 'test_report_path'):
            self.save()
            def replace_after_check(root, manifest):
                original(root, manifest)
                path = root / manifest[name]
                value = json.loads(path.read_text())
                if name == 'observation_path': value['state'] = 'failed'
                else: value['cases'][0]['outcome'] = 'failed'
                self.write(path, value)
            with self.subTest(name=name), patch.object(cr, '_files', side_effect=replace_after_check):
                with self.assertRaisesRegex(ValueError, 'retained hash'): self.verify()

    def test_unlisted_missing_and_traversing_files_are_rejected(self):
        extra = self.directory / 'extra.txt'; extra.write_text('Unlisted')
        with self.assertRaisesRegex(ValueError, 'Unlisted'): self.verify()
        extra.unlink()
        self.manifest['files']['../escape.txt'] = {'sha256': 'a' * 64, 'bytes': 1}; self.write_manifest()
        with self.assertRaisesRegex(ValueError, 'portable'): self.verify()

    def test_external_hashes_and_contract_chronology_are_required(self):
        self.contract_sha = None
        with self.assertRaisesRegex(ValueError, 'SHA-256'): self.verify()
        self.save(); self.manifest_sha = None
        with self.assertRaisesRegex(ValueError, 'SHA-256'): self.verify()
        self.save()
        self.contract_sha = 'f' * 64
        with self.assertRaisesRegex(ValueError, 'retained hash'): self.verify()
        self.save(); self.manifest_sha = 'f' * 64
        with self.assertRaisesRegex(ValueError, 'retained hash'): self.verify()
        self.contract['frozen_at'] = '2026-10-21T00:00:00Z'; self.save()
        with self.assertRaisesRegex(ValueError, 'predates'): self.verify()

    def test_malformed_contract_and_observation_fail_closed(self):
        original = copy.deepcopy(self.contract)
        for expected in ([], ['duplicate', 'duplicate'], [False]):
            self.contract = {**copy.deepcopy(original), 'expected_tests': expected}; self.save()
            with self.subTest(expected=expected), self.assertRaises(ValueError): self.verify()
        self.contract = original
        self.observation['execution_started'] = 1; self.save()
        with self.assertRaisesRegex(ValueError, 'execution-start'): self.verify()

    def test_readonly_snapshot_and_restored_journal_do_not_activate_restore(self):
        copied = self.root / 'inactive.sqlite'; shutil.copyfile(self.path, copied)
        before = self.digest(copied)
        report = self.verify(journal=copied)
        self.assertFalse(report['active_journal_binding'])
        self.assertFalse(report['resume_performed'])
        self.assertEqual(self.digest(copied), before)
        with launches.LaunchJournal(self.path, read_only=True) as journal:
            self.assertEqual(journal.evidence(self.spec['operation_key'])['specification'], self.spec)
            with self.assertRaisesRegex(ValueError, 'Read-only'): journal.begin(self.spec, self.prompt)

    def test_cli_is_offline_and_returns_distinct_hold_status(self):
        args = ['launch-result-verify', '--journal', str(self.path), '--operation', self.spec['operation_key'],
                '--contract', str(self.contract_path), '--contract-sha256', self.contract_sha,
                '--directory', str(self.directory), '--manifest-sha256', self.manifest_sha]
        with patch('urllib.request.urlopen', side_effect=AssertionError('No provider or network')), patch('sys.stdout', new_callable=io.StringIO) as stdout:
            self.assertEqual(main(args), 0)
        self.assertFalse(json.loads(stdout.getvalue())['provider_called'])
        self.observation['state'] = 'held'; self.save()
        args[-1] = self.manifest_sha
        with patch('sys.stdout', new_callable=io.StringIO): self.assertEqual(main(args), 2)
