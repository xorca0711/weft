import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from weft.transfer_parts import split_file, reassemble, TransferError, MAX_PART


class TransferPartsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.data = bytes(range(251)) * 5
        self.source = self.root / 'source.bin'
        self.source.write_bytes(self.data)
        self.sha = hashlib.sha256(self.data).hexdigest()

    def split(self, **kw):
        return split_file(self.source, self.root/'parts', expected_sha256=self.sha, **kw)

    def restore(self, result, **kw):
        args = dict(expected_manifest_sha256=result['manifest_sha256'], expected_artifact_sha256=self.sha)
        args.update(kw)
        return reassemble(self.root/'parts', self.root/'restored', **args)

    def test_roundtrip_uneven_parts_and_anchors(self):
        result = self.split(part_bytes=400)
        self.assertEqual(result['parts'], 4)
        restored = self.restore(result)
        self.assertEqual((self.root/'restored/payload.bin').read_bytes(), self.data)
        self.assertFalse(restored['activation_permitted'])
        self.assertFalse(restored['transport_verified'])

    def test_exact_provider_bound_crossed(self):
        self.data = b'x' * (MAX_PART+7)
        self.source.write_bytes(self.data)
        self.sha = hashlib.sha256(self.data).hexdigest()
        result = self.split()
        self.assertEqual(result['parts'], 2)
        self.restore(result)

    def test_corrupted_part_retains_failure_without_verified_marker(self):
        result = self.split(part_bytes=400)
        (self.root/'parts/part-0001.bin').write_bytes(b'X'*400)
        with self.assertRaises(TransferError): self.restore(result)
        self.assertFalse((self.root/'restored/verified.json').exists())

    def test_unexpected_part_rejected(self):
        result = self.split(part_bytes=400)
        (self.root/'parts/unexpected').write_bytes(b'x')
        with self.assertRaises(TransferError): self.restore(result)
        self.assertFalse((self.root/'restored').exists())

    def test_external_anchors_required(self):
        result = self.split()
        with self.assertRaises(TransferError): self.restore(result, expected_manifest_sha256='0'*64)
        with self.assertRaises(TransferError): self.restore(result, expected_artifact_sha256='0'*64)

    def test_traversal_manifest_rejected_even_with_hash(self):
        result = self.split(part_bytes=400)
        path = self.root/'parts/manifest.json'
        manifest = json.loads(path.read_bytes())
        manifest['parts'][0]['name'] = '../source.bin'
        raw = json.dumps(manifest, sort_keys=True, separators=(',', ':')).encode()
        path.write_bytes(raw)
        result['manifest_sha256'] = hashlib.sha256(raw).hexdigest()
        with self.assertRaises(TransferError): self.restore(result)

    def test_changed_source_and_existing_destination_preserved(self):
        self.source.write_bytes(b'different')
        with self.assertRaises(TransferError): self.split()
        self.assertFalse((self.root/'parts/manifest.json').exists())
        with self.assertRaises(FileExistsError): self.split()

    def test_limits(self):
        for n in [0, -1, True, MAX_PART+1]:
            with self.assertRaises(TransferError): self.split(part_bytes=n)
        with self.assertRaises(TransferError): self.split(part_bytes=1)


if __name__ == '__main__':
    unittest.main()
