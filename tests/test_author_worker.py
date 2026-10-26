import contextlib
import io
import json
import unittest
from unittest.mock import patch

import test_evidence as baseline
import test_science_pipeline as pipeline
from weft import author_worker as worker, evidence as ev


class AuthorWorkerTests(unittest.TestCase):
    setUp = baseline.EvidenceTests.setUp
    file_ref = baseline.EvidenceTests.file_ref
    base_record = baseline.EvidenceTests.base_record
    put = baseline.EvidenceTests.put
    source = baseline.EvidenceTests.source
    case = baseline.EvidenceTests.case
    data = baseline.EvidenceTests.data
    plan = baseline.EvidenceTests.plan
    build = pipeline.SciencePipelineTests.build

    def request(self):
        return {'image': 'python@sha256:' + 'a'*64, 'image_id': 'sha256:' + 'b'*64,
                'argv': ['/usr/local/bin/python', '-I', '/code/adapter.py'],
                'environment': ['HOME=/tmp', 'PATH=/usr/local/bin:/usr/bin:/bin'],
                'pids': 32, 'nano_cpus': 1000000000, 'tmpfs_bytes': 128, 'output_bytes': 512}

    def prepared(self):
        self.build()
        return worker.prepare(self.ws, self.pkg, self.request())['preparation']

    def assignment(self):
        return {'job_id': 'd'*64, 'attempt_id': 1, 'container_id': 'e'*64,
                'staging_root': '/var/lib/weft/staged'}

    def test_package_inventory_without_execution_upload_or_ledger(self):
        with patch('subprocess.run', side_effect=AssertionError('No launch')):
            ref = self.prepared()
            obj = worker.load_preparation(self.ws, ref)
        self.assertEqual(obj['staging']['code'][0]['destination'], '/code/adapter.py')
        self.assertEqual(obj['staging']['inputs'][0]['destination'], '/inputs/counts.csv')
        self.assertNotIn('paper.txt', json.dumps(obj['staging']))
        self.assertNotIn('review.txt', json.dumps(obj['staging']))
        self.assertFalse((self.ws.root / 'control/jobs.sqlite').exists())
        for flag in (*ev.FLAGS, 'runtime_qualified', 'author_code_executed'):
            self.assertIs(obj[flag], False)

    def test_repeat_preparation_preserves_identical_bytes(self):
        ref = self.prepared()
        again = worker.prepare(self.ws, self.pkg, self.request())['preparation']
        self.assertEqual(ref, again)

    def test_source_or_code_drift_invalidates_prepared_worker(self):
        ref = self.prepared()
        (self.inputs / 'adapter.py').write_bytes(b'changed author bytes')
        with self.assertRaises(ValueError): worker.load_preparation(self.ws, ref)

    def test_worker_implementation_change_requires_new_preparation(self):
        ref = self.prepared()
        with patch.object(worker, 'implementation', return_value={'changed': '0'*64}):
            with self.assertRaises(ValueError): worker.load_preparation(self.ws, ref)

    def test_unapproved_environment_and_unfrozen_command_rejected(self):
        self.build()
        for delta in ({'environment': ['HTTPS_PROXY=SECRET']}, {'argv': ['python', '/tmp/unpinned.py']},
                      {'image': 'python:latest'}, {'extra': True}):
            with self.subTest(delta=delta), self.assertRaises(ValueError):
                worker.prepare(self.ws, self.pkg, {**self.request(), **delta})

    def test_scratch_and_output_must_fit_existing_contract(self):
        self.build()
        for delta in ({'output_bytes': 1048576}, {'output_bytes': True}, {'tmpfs_bytes': 1024},
                      {'output_bytes': 0}, {'pids': 0}):
            with self.subTest(delta=delta), self.assertRaises(ValueError):
                worker.prepare(self.ws, self.pkg, {**self.request(), **delta})

    def test_attempt_specific_layout_and_supplied_observations_stay_unqualified(self):
        ref = self.prepared(); assignment = self.assignment()
        plan = worker.observation_plan(self.ws, ref, assignment)
        other = worker.observation_plan(self.ws, ref, {**assignment, 'attempt_id': 2})
        self.assertNotEqual(plan['container_name'], other['container_name'])
        same = worker.observation_plan(self.ws, ref, {**assignment, 'container_id': 'f'*64})
        self.assertEqual(plan['container_name'], same['container_name'])
        self.assertEqual(plan['mounts'], same['mounts'])
        result = worker.inspect_supplied(self.ws, ref, assignment, {}, {})
        self.assertEqual(result['status'], 'hold')
        for key in ('assignment_authenticated', 'dispatch_authorized', 'runtime_qualified',
                    'output_quota_verified', 'watchdog_verified'):
            self.assertIs(result[key], False)

    def test_invalid_assignment_and_path_cannot_bind(self):
        ref = self.prepared()
        for delta in ({'attempt_id': True}, {'staging_root': '/'}, {'staging_root': '/a/../b'},
                      {'container_id': 'not-an-id'}, {'job_id': 'unbound'}):
            with self.subTest(delta=delta), self.assertRaises(ValueError):
                worker.observation_plan(self.ws, ref, {**self.assignment(), **delta})

    def test_cli_does_not_echo_secrets_from_invalid_request(self):
        self.build()
        (self.base/'pkg.json').write_bytes(ev.encoded(self.pkg))
        req = self.request(); req['environment'].append('AWS_SECRET_ACCESS_KEY=DO-NOT-ECHO')
        (self.base/'req.json').write_bytes(ev.encoded(req))
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            rc = worker.main(['--root', str(self.ws.root), '--package-reference', str(self.base/'pkg.json'),
                              '--request', str(self.base/'req.json')])
        self.assertEqual(rc, 1); self.assertNotIn('DO-NOT-ECHO', output.getvalue())


if __name__ == '__main__': unittest.main()
