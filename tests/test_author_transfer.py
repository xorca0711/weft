import hashlib
import os
import shutil
import unittest
from unittest.mock import patch

import test_author_worker as fixtures
from weft import author_transfer as transfer, author_worker as worker, evidence as ev


class AuthorTransferTests(unittest.TestCase):
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

    def limits(self, total=512):
        return {'max_files': 4, 'max_entries': 16, 'max_file_bytes': total, 'max_total_bytes': total}

    def delivery(self):
        self.ref = self.prepared()
        directory = self.base / 'return'; (directory / 'outputs').mkdir(parents=True)
        (directory / 'outputs/metrics.json').write_bytes(b'{"value": 42}')
        self.files = [{k: v for k, v in ev.reference(directory, 'outputs/metrics.json').items() if k != 'root'}]
        self.identity = {'job_id': 'a'*64, 'attempt_id': 1, 'container_id': 'b'*64}
        return directory

    def collect(self, directory):
        return transfer.collect(self.ws, self.ref, self.identity, directory, self.base/'collected',
                                self.files, self.limits())

    def test_stage_only_frozen_bytes_and_idempotent_resume(self):
        ref = self.prepared()
        with patch('subprocess.run', side_effect=AssertionError('Must not execute')):
            result = transfer.stage(self.ws, ref, self.base/'stage', self.limits())
        self.assertEqual({x['path'] for x in result['files']}, {'code/adapter.py', 'inputs/counts.csv'})
        self.assertFalse(result['readonly_mount_verified'])
        self.assertEqual(transfer.stage(self.ws, ref, self.base/'stage', self.limits()), result)

    def test_frozen_input_growth_rejected_before_unbounded_digest(self):
        ref = self.file_ref('inputs', 'counts.csv')
        (self.inputs/'counts.csv').write_bytes(b'x' * 2048)
        with patch('hashlib.file_digest', side_effect=AssertionError('Unbounded hash forbidden')):
            with self.assertRaises(ValueError): self.ws.file(ref)

    def test_staging_and_output_share_the_frozen_disk_budget(self):
        (self.inputs/'counts.csv').write_bytes(b'x' * 900000)
        self.build()
        with self.assertRaises(ValueError):
            worker.prepare(self.ws, self.pkg, {**self.request(), 'output_bytes': 200000})

    def test_stage_rejects_protected_root_extras_and_partial_copy(self):
        ref = self.prepared()
        for root in (self.ws.root/'stage', self.inputs/'stage', self.protected/'stage'):
            with self.subTest(root=root), self.assertRaises(ValueError):
                transfer.stage(self.ws, ref, root, self.limits())
        root = self.base/'stage'
        transfer.stage(self.ws, ref, root, self.limits())
        (root/'code/adapter.py').write_bytes(b'partial')
        with self.assertRaises(ValueError): transfer.stage(self.ws, ref, root, self.limits())
        self.assertEqual((root/'code/adapter.py').read_bytes(), b'partial')

    def test_collection_restore_and_duplicate_keep_authority_false(self):
        directory = self.delivery(); ref = self.collect(directory)
        self.assertEqual(self.collect(directory), ref)
        shutil.copytree(self.base/'collected', self.base/'restore')
        obj = transfer.verify(self.base/'restore', ref['sha256'])
        self.assertEqual(obj['missing_outputs'], [])
        for flag in (*ev.FLAGS, 'termination_verified', 'identity_authenticated'):
            self.assertIs(obj[flag], False)
        (self.base/'restore/outputs/metrics.json').write_bytes(b'changed')
        with self.assertRaises(ValueError): transfer.verify(self.base/'restore', ref['sha256'])

    def test_failed_return_can_retain_missing_outputs_without_success_claim(self):
        directory = self.delivery()
        (directory/'outputs/metrics.json').unlink(); (directory/'outputs').rmdir()
        self.files = []
        ref = self.collect(directory)
        self.assertEqual(transfer.verify(self.base/'collected', ref['sha256'])['missing_outputs'],
                         ['outputs/metrics.json'])

    def test_extra_file_empty_directory_and_count_bound_rejected(self):
        directory = self.delivery()
        (directory/'unexpected').mkdir()
        with self.assertRaises(ValueError): self.collect(directory)
        (directory/'unexpected').rmdir(); (directory/'secret').write_bytes(b'private')
        with self.assertRaises(ValueError): self.collect(directory)
        with self.assertRaises(ValueError): transfer.exact_tree(directory, self.files,
            {'max_files': 1, 'max_entries': 1, 'max_file_bytes': 512, 'max_total_bytes': 512})

    def test_wrong_hash_over_budget_or_unplanned_output_rejected(self):
        directory = self.delivery()
        original = self.files[0].copy()
        for delta in ({'sha256': '0'*64}, {'bytes': 1024}, {'path': 'outputs/secret.txt'}):
            self.files = [{**original, **delta}]
            with self.subTest(delta=delta), self.assertRaises(ValueError): self.collect(directory)

    def test_portable_path_aliases_and_prefix_collisions_rejected(self):
        item = {'path': 'a', 'sha256': '0'*64, 'bytes': 1}
        for path in ('../secret', 'A', 'a/b', 'NUL.txt', 'x.', 'x:secret', '/root'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                transfer.inventory([item, {**item, 'path': path}], self.limits())

    def test_hardlinks_are_never_copied(self):
        directory = self.delivery()
        os.link(directory/'outputs/metrics.json', self.base/'alias')
        with self.assertRaises(ValueError): self.collect(directory)

    def test_stream_larger_than_structured_record_bound(self):
        source = self.base/'large'; source.write_bytes(b'x' * (ev.MAX_RECORD * 2 + 7))
        item = {'path': 'large', 'bytes': source.stat().st_size,
                'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}
        target = self.base/'copied'; target.mkdir()
        transfer._copy(source, target, item)
        self.assertEqual(ev.reference(target, 'large')['sha256'], item['sha256'])
        self.assertGreater(item['bytes'], ev.MAX_RECORD)

    def test_corrupt_manifest_and_extra_restore_file_rejected(self):
        directory = self.delivery(); ref = self.collect(directory)
        with self.assertRaises(ValueError): transfer.verify(self.base/'collected', '0'*64)
        (self.base/'collected/extra').write_bytes(b'extra')
        with self.assertRaises(ValueError): transfer.verify(self.base/'collected', ref['sha256'])


if __name__ == '__main__': unittest.main()
