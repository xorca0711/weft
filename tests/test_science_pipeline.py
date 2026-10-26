import copy
import hashlib
import json
from pathlib import Path
import shutil
import unittest
from unittest.mock import patch

import test_evidence as baseline
from weft import evidence as ev, science_adapter as adapter, science_review as review
from weft.jobs import JobError, validate_packet


class SciencePipelineTests(unittest.TestCase):
    setUp = baseline.EvidenceTests.setUp
    file_ref = baseline.EvidenceTests.file_ref
    base_record = baseline.EvidenceTests.base_record
    put = baseline.EvidenceTests.put
    source = baseline.EvidenceTests.source
    case = baseline.EvidenceTests.case
    data = baseline.EvidenceTests.data
    plan = baseline.EvidenceTests.plan
    prepare = baseline.EvidenceTests.prepare

    def build(self, *, exposure='synthetic-fixture', attempts=1):
        sr = self.put(self.source())
        case = self.case(sr); case['exposure']['mode'] = exposure
        cr = self.put(case); dr = self.put(self.data(cr))
        contract = self.plan(cr, dr)
        contract['outputs'] = [{'path': 'outputs/metrics.json', 'role': 'qc', 'description': 'Synthetic measurements'}]
        contract['limits'].update(disk_bytes=1_048_576, wall_seconds=30, max_attempts=attempts)
        self.contract = self.put(contract)
        self.checks = {**self.base_record('numerical-plan'), 'case_id': self.cid, 'contract': self.contract,
            'checks': [{'id': 'mean-check', 'output': 'outputs/metrics.json', 'metric': 'mean',
                        'quantity': 'scalar', 'expected': 11, 'absolute_tolerance': 0,
                        'relative_tolerance': 0, 'arithmetic_tolerance': 0,
                        'denominator': 2, 'units': ['s1', 's2'],
                        'reference': {'resource_id': 'paper', 'locator': 'Synthetic test target, not a published claim',
                                      'file_sha256': self.file_ref('sources', 'paper.txt')['sha256']},
                        'interval_required': False, 'sensitivity_labels': ['leave-one-out']}],
            'limitations': ['Synthetic description only']}
        self.plan_ref = self.put(self.checks)
        self.pkg = adapter.package(self.ws, self.contract, self.plan_ref)['package']
        return self.pkg

    def begin(self, replay):
        result = replay.begin(self.pkg)
        self.claim = {k: result[k] for k in ('job_id', 'attempt_id', 'lease_token', 'expires')}
        return self.claim

    def measurement(self):
        return {'schema_version': 'weft-measurements-v1', 'metrics': [
            {'id': 'mean', 'value': 11, 'numerator': None, 'denominator': 2,
             'unit_ids': ['s1', 's2'], 'interval': None,
             'sensitivity': [{'label': 'leave-one-out', 'value': 10}]}]}

    def delivery(self, *, outcome='completed', measurements=None):
        directory = self.base / ('return-' + str(self.claim['attempt_id']))
        directory.mkdir(); (directory / 'outputs').mkdir()
        files = []
        if outcome == 'completed':
            raw = ev.encoded(measurements or self.measurement())
            (directory / 'outputs/metrics.json').write_bytes(raw)
            files.append({'path': 'outputs/metrics.json', 'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()})
        manifest = {'schema_version': adapter.VERSION, 'kind': 'synthetic-fixture-return',
                    'job_id': self.claim['job_id'], 'attempt_id': self.claim['attempt_id'],
                    'package_sha256': self.pkg['sha256'], 'outcome': outcome, 'files': files,
                    'error': None if outcome == 'completed' else 'Controlled ' + outcome + ' fixture'}
        raw = ev.encoded(manifest); (directory / 'return.json').write_bytes(raw)
        return directory, hashlib.sha256(raw).hexdigest()

    def finish(self, measurements=None):
        self.build()
        with adapter.open_replay(self.ws) as replay:
            self.begin(replay); directory, expected = self.delivery(measurements=measurements)
            self.receipt = replay.receive(self.claim, directory, expected)['receipt']
        return self.receipt

    def critique(self, receipt):
        return {**self.base_record('scientific-review'), 'case_id': self.cid, 'receipt': receipt,
                'issues': [{'id': 'scope', 'check_id': 'mean-check', 'severity': 'limitation',
                            'comment': 'Fixture only <script>alert(1)</script>', 'evidence': []}],
                'responses': [{'issue_id': 'scope', 'response': 'Retain unresolved scope', 'evidence': []}],
                'interpretation': 'Synthetic values; no biological result'}

    def test_end_to_end_qc_view_and_dry_export_no_code_execution(self):
        with patch('subprocess.run', side_effect=AssertionError('No process launch')):
            receipt = self.finish()
            report = review.qc(self.ws, receipt)
            self.assertEqual(report['status'], 'qc-consistent')
            self.assertFalse(report['scientific_validity_established'])
            rr = self.put(self.critique(receipt))
            result = review.view(self.ws, receipt, rr)
            page = self.ws.file(result['view']).read_text(encoding='utf-8')
            self.assertIn('&lt;script&gt;', page); self.assertNotIn('<script>', page)
            self.assertIn('No owner disposition recorded', page)
            self.assertIn('Observed 11', page)
            export = review.dry_export(self.ws, receipt, rr, 'Review only')['export']
            self.assertEqual(review.verify_export(self.ws.file(export), export['sha256'])['status'], 'dry-export-verified')
            raw = self.ws.file(export).read_text()
            for private in ('private-bindings', 'lease_token', 'counts.csv', str(self.inputs)):
                self.assertNotIn(private, raw)
            self.assertEqual((self.protected / 'historical.txt').read_bytes(), b'PRESERVE')

    def test_changed_source_invalidates_package_without_dispatch(self):
        self.build()
        source = self.source(); old = ev.reference(self.ws.root, ev.record_path(source))
        source.update(revision=2, previous=old, amendment_reason='Correct fixture source')
        self.put(source)
        with adapter.open_replay(self.ws) as replay:
            with self.assertRaises(ValueError): replay.begin(self.pkg)
            self.assertEqual(replay.ledger.db.execute('SELECT COUNT(*) FROM attempts').fetchone()[0], 0)

    def test_package_pin_and_code_tamper_hold(self):
        self.build()
        with patch.object(adapter, 'implementation', return_value={}):
            with self.assertRaises(ValueError): adapter.load_package(self.ws, self.pkg)
        (self.inputs / 'adapter.py').write_text('different')
        with self.assertRaises(ValueError): adapter.load_package(self.ws, self.pkg)

    def test_real_exposure_can_prepare_but_never_replay(self):
        self.build(exposure='exposed-exploration')
        with adapter.open_replay(self.ws) as replay:
            with self.assertRaises(ValueError): replay.begin(self.pkg)
        result = adapter.readiness(self.ws, self.contract)
        self.assertEqual(result['status'], 'hold'); self.assertFalse(result['runtime_qualified'])

    def test_double_begin_and_legacy_execution_api_rejected(self):
        self.build()
        with adapter.open_replay(self.ws) as replay:
            self.begin(replay)
            with self.assertRaises(JobError): replay.begin(self.pkg)
            with self.assertRaises(JobError): validate_packet(replay.ledger.status(self.claim['job_id'])['packet'])
            with self.assertRaises(JobError): replay.ledger.claim(self.claim['job_id'], inputs_root=self.inputs,
                current_context_sha256='a' * 64, current_policy_sha256='b' * 64)
            with self.assertRaises(JobError): replay.ledger.reconcile(self.claim['attempt_id'], self.claim['lease_token'],
                outcome='cancelled', receipt_ref='a' * 64)
            with self.assertRaises(JobError): replay.ledger.bind_executor(self.claim, {})

    def test_shared_slot_unknown_synthetic_attempt_blocks_replay(self):
        self.build()
        with adapter.open_replay(self.ws, clock=lambda: 10) as replay:
            packet = {'schema_version': 1, 'kind': 'synthetic-qualification',
                      **{k: 'a' * 64 for k in ('paper_version_sha256', 'context_sha256', 'policy_sha256', 'contract_sha256', 'executor_sha256')},
                      'inputs': [{k: v for k, v in self.file_ref('inputs', 'counts.csv').items() if k != 'root'}],
                      'max_attempts': 1, 'lease_seconds': 1}
            job = replay.ledger.submit(packet)
            replay.ledger.claim(job, inputs_root=self.inputs, current_context_sha256='a' * 64, current_policy_sha256='a' * 64)
            replay.ledger.clock = lambda: 12; self.assertEqual(replay.ledger.expire(), 1)
            with self.assertRaises(JobError): replay.begin(self.pkg)

    def test_unknown_cancellation_restart_and_duplicate_return(self):
        self.build()
        with adapter.open_replay(self.ws, clock=lambda: 10) as replay:
            self.begin(replay); replay.ledger.cancel(self.claim['job_id'])
            self.assertEqual(replay.ledger.status(self.claim['job_id'])['state'], 'cancel_requested')
            replay.ledger.clock = lambda: 41; replay.ledger.expire()
            with self.assertRaises(JobError): replay.begin(self.pkg)
        directory, expected = self.delivery(outcome='cancelled')
        with adapter.open_replay(self.ws, clock=lambda: 42) as replay:
            result = replay.receive(self.claim, directory, expected)
            self.assertEqual(result['status'], 'fixture_cancelled')
            self.assertTrue(replay.receive(self.claim, directory, expected)['idempotent'])
            with self.assertRaises(JobError): replay.begin(self.pkg)

    def test_failed_attempt_retained_and_bounded_retry_uses_fresh_directory(self):
        self.build(attempts=2)
        with adapter.open_replay(self.ws) as replay:
            self.begin(replay); first = self.claim.copy()
            directory, expected = self.delivery(outcome='failed')
            receipt = replay.receive(self.claim, directory, expected)['receipt']
            self.assertEqual(review.qc(self.ws, receipt)['status'], 'hold')
            self.begin(replay)
            self.assertNotEqual(first['attempt_id'], self.claim['attempt_id'])
            self.assertTrue(self.ws.file(receipt).is_file())

    def test_interrupted_ledger_application_recovers_exact_retained_return(self):
        self.build()
        with adapter.open_replay(self.ws) as replay:
            self.begin(replay); directory, expected = self.delivery()
            with patch.object(replay.ledger, '_event', side_effect=RuntimeError('Interrupted after receipt saved')):
                with self.assertRaises(RuntimeError): replay.receive(self.claim, directory, expected)
            self.assertEqual(replay.ledger.status(self.claim['job_id'])['state'], 'running')
            receipt = ev.reference(self.ws.root, adapter.FixtureReplay._prefix(self.claim) + '/receipt.json')
        with adapter.open_replay(self.ws) as replay:
            result = replay.recover(self.claim, receipt)
            self.assertEqual(result['status'], 'fixture_completed')
            self.assertTrue(replay.recover(self.claim, receipt)['idempotent'])

    def test_interrupted_file_copy_can_resume_but_not_replace(self):
        self.build()
        with adapter.open_replay(self.ws) as replay:
            self.begin(replay); directory, expected = self.delivery()
            original = adapter._save
            def interrupted(workspace, name, raw):
                if name.endswith('return.json'): raise OSError('Interrupted transfer')
                return original(workspace, name, raw)
            with patch.object(adapter, '_save', side_effect=interrupted):
                with self.assertRaises(OSError): replay.receive(self.claim, directory, expected)
            self.assertEqual(replay.receive(self.claim, directory, expected)['status'], 'fixture_completed')

    def test_return_digest_and_missing_output_do_not_release_attempt(self):
        self.build()
        with adapter.open_replay(self.ws) as replay:
            self.begin(replay); directory, expected = self.delivery()
            with self.assertRaises(ValueError): replay.receive(self.claim, directory, '0' * 64)
            manifest = ev.decode((directory / 'return.json').read_bytes()); manifest['files'] = []
            raw = ev.encoded(manifest); (directory / 'return.json').write_bytes(raw)
            with self.assertRaises(ValueError): replay.receive(self.claim, directory, hashlib.sha256(raw).hexdigest())
            self.assertEqual(replay.ledger.status(self.claim['job_id'])['state'], 'running')

    def test_receipt_output_tamper_rejected(self):
        receipt = self.finish()
        record = self.ws.file(receipt, parse=True)
        self.ws.file(record['outputs'][0]['file']).write_text('tampered')
        with self.assertRaises(ValueError): review.qc(self.ws, receipt)

    def test_discrepancies_retained_without_scientific_acceptance(self):
        data = self.measurement(); row = data['metrics'][0]
        row.update(value=-3, denominator=3, unit_ids=['invented'], sensitivity=[])
        receipt = self.finish(data)
        report = review.qc(self.ws, receipt)
        self.assertEqual(report['status'], 'qc-issues')
        self.assertEqual(set(report['checks'][0]['issues']), {'reference-discrepancy', 'denominator-mismatch',
                         'biological-unit-mismatch', 'sensitivity-inventory-mismatch'})
        self.assertFalse(report['canonical_acceptance'])

    def test_invalid_numeric_rows_and_duplicate_metrics_fail_closed(self):
        self.build()
        with adapter.open_replay(self.ws) as replay:
            self.begin(replay)
            data = self.measurement(); data['metrics'].append(copy.deepcopy(data['metrics'][0]))
            directory, expected = self.delivery(measurements=data)
            receipt = replay.receive(self.claim, directory, expected)['receipt']
            with self.assertRaises(ValueError): review.qc(self.ws, receipt)
        for value in (float('nan'), float('inf'), True, '11'):
            with self.assertRaises(ValueError): review.number(value)

    def test_plan_cannot_invent_units_or_drop_limits(self):
        self.build()
        for mutate in (lambda x: x['checks'][0].update(units=['unknown']),
                       lambda x: x.update(limitations=['Dropped']),
                       lambda x: x['checks'][0].update(expected=None),
                       lambda x: x['checks'][0].update(absolute_tolerance=-1)):
            record = copy.deepcopy(self.checks); mutate(record)
            with self.assertRaises(ValueError): self.ws.validate(record)

    def test_new_numerical_plan_cannot_rescore_old_attempt(self):
        self.finish()
        revised = copy.deepcopy(self.checks)
        revised.update(revision=2, previous=self.plan_ref, amendment_reason='Different target, requires new prospective package')
        revised['checks'][0]['expected'] = 5; self.put(revised)
        with self.assertRaises(ValueError): review.qc(self.ws, self.receipt)

    def test_owner_disposition_never_inferred_and_cannot_accept_canonical_result(self):
        receipt = self.finish(); rr = self.put(self.critique(receipt))
        obj = {**self.base_record('owner-disposition'), 'case_id': self.cid, 'receipt': receipt,
               'review': rr, 'disposition': 'deferred', 'rationale': 'Synthetic supplied owner-response fixture',
               'decision_evidence': self.file_ref('sources', 'review.txt')}
        with self.assertRaises(ValueError): self.put(obj)
        obj['actor']['kind'] = 'human'
        ref = self.put(obj); self.assertIsNotNone(ref)
        obj['disposition'] = 'accepted'
        with self.assertRaises(ValueError): self.ws.validate(obj)

    def test_copy_inactive_and_hardlinked_ledger_not_opened(self):
        self.build(); copied = self.base / 'copy'; shutil.copytree(self.ws.root, copied)
        with self.assertRaises(ValueError):
            with adapter.open_replay(ev.Workspace(copied)): pass
        ledger = self.ws.root / 'control/jobs.sqlite'; ledger.parent.mkdir()
        try: ledger.hardlink_to(self.protected / 'historical.txt')
        except OSError: self.skipTest('Hard links unavailable')
        with self.assertRaises(ValueError):
            with adapter.open_replay(self.ws): pass
        self.assertEqual((self.protected / 'historical.txt').read_bytes(), b'PRESERVE')

    def test_review_cross_case_and_unbound_issue_rejected(self):
        receipt = self.finish(); obj = self.critique(receipt)
        obj['issues'][0]['check_id'] = 'fabricated'
        with self.assertRaises(ValueError): self.put(obj)
        obj = self.critique(receipt); obj['case_id'] = 'wc-' + 'c' * 32
        with self.assertRaises(ValueError): self.put(obj)

    def test_cli_complete_controlled_flow(self):
        import contextlib
        import io
        from weft.__main__ import main
        self.build()
        path = self.base / 'package-ref.json'; path.write_bytes(ev.encoded(self.pkg))
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            self.assertEqual(main(['evidence-fixture-begin', '--root', str(self.ws.root), '--package-reference', str(path)]), 0)
        result = json.loads(stream.getvalue())
        self.claim = {k: result[k] for k in ('job_id', 'attempt_id', 'lease_token', 'expires')}
        directory, expected = self.delivery()
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(['evidence-fixture-return', '--root', str(self.ws.root), '--checkpoint',
                str(self.ws.root / result['checkpoint']), '--directory', str(directory), '--expected-manifest-sha256', expected]), 0)
        state = self.ws.status()
        self.assertEqual(state['attempts'][0]['state'], 'fixture_completed')
        self.assertNotIn('lease_token', json.dumps(state))

    def test_proportion_arithmetic_and_required_uncertainty(self):
        self.build()
        revised = copy.deepcopy(self.checks)
        revised.update(revision=2, previous=self.plan_ref, amendment_reason='Proportion fixture')
        revised['checks'][0].update(quantity='proportion', expected=0.5, interval_required=True)
        self.plan_ref = self.put(revised)
        self.pkg = adapter.package(self.ws, self.contract, self.plan_ref)['package']
        with adapter.open_replay(self.ws) as replay:
            self.begin(replay)
            data = self.measurement(); data['metrics'][0].update(value=0.5, numerator=0)
            directory, expected = self.delivery(measurements=data)
            receipt = replay.receive(self.claim, directory, expected)['receipt']
        issues = review.qc(self.ws, receipt)['checks'][0]['issues']
        self.assertEqual(set(issues), {'proportion-arithmetic-mismatch', 'uncertainty-missing'})

    def test_shared_slot_unknown_replay_blocks_synthetic_claim(self):
        self.build()
        with adapter.open_replay(self.ws, clock=lambda: 10) as replay:
            self.begin(replay)
            packet = {'schema_version': 1, 'kind': 'synthetic-qualification',
                      **{k: 'a' * 64 for k in ('paper_version_sha256', 'context_sha256', 'policy_sha256', 'contract_sha256', 'executor_sha256')},
                      'inputs': [{k: v for k, v in self.file_ref('inputs', 'counts.csv').items() if k != 'root'}],
                      'max_attempts': 1, 'lease_seconds': 1}
            job = replay.ledger.submit(packet)
            replay.ledger.clock = lambda: 41; replay.ledger.expire()
            with self.assertRaises(JobError): replay.ledger.claim(job, inputs_root=self.inputs,
                current_context_sha256='a' * 64, current_policy_sha256='a' * 64)

    def test_partial_or_aliased_attempt_root_is_not_reused(self):
        self.build()
        with adapter.open_replay(self.ws) as replay:
            from weft.identity import digest
            job = digest(replay._packet(self.pkg))
            root = self.ws.root / f'runs/{job}/attempt-000001'
            root.mkdir(parents=True); (root / 'partial').write_bytes(b'PRESERVE')
            with self.assertRaises(FileExistsError): replay.begin(self.pkg)
            self.assertEqual((root / 'partial').read_bytes(), b'PRESERVE')
            self.assertEqual(replay.ledger.db.execute('SELECT COUNT(*) FROM attempts').fetchone()[0], 0)
