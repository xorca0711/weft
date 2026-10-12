import copy
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from weft import intake, qualification
from weft.__main__ import main
import test_qualification


class IntakeTests(unittest.TestCase):
    setUp = test_qualification.QualificationTests.setUp
    create = test_qualification.QualificationTests.create
    run_batch = test_qualification.QualificationTests.run_batch
    response = test_qualification.QualificationTests.response
    screen = test_qualification.QualificationTests.screen
    prepared = test_qualification.QualificationTests.prepared
    citation = test_qualification.QualificationTests.citation
    descriptive = test_qualification.QualificationTests.descriptive

    def reviewed(self):
        bid, cid, packet, record = self.prepared()
        record = self.descriptive(packet, record)
        qualification.submit(self.store, bid, record)
        return bid, cid, record

    def test_only_scope_ready_can_stage_and_neither_scope_is_approved(self):
        bid, cid, _ = self.reviewed()
        with self.assertRaisesRegex(ValueError, 'scope-specific'):
            intake.prepare(self.store, bid, cid, 'rq_review')
        staged = intake.prepare(self.store, bid, cid, 'data_review')
        self.assertEqual(staged['members'], 5)
        self.assertFalse(staged['publication_authorized'])
        verified = intake.verify(self.store, bid, cid, 'data_review', staged['directory'], staged['manifest_sha256'])
        self.assertEqual(verified['status'], 'verified_private_proposal')
        summary = json.loads((Path(staged['directory']) / 'summary.json').read_text())
        self.assertEqual(summary['rq_proposal'], 'hold')
        self.assertFalse(summary['claim_validated'])
        with self.assertRaises(FileExistsError):
            intake.prepare(self.store, bid, cid, 'data_review')

    def test_unreviewed_and_coverage_hold_cannot_stage(self):
        bid, cid, _, record = self.prepared()
        with self.assertRaises(ValueError):
            intake.prepare(self.store, bid, cid, 'data_review')
        qualification.submit(self.store, bid, record)
        with self.assertRaises(ValueError):
            intake.prepare(self.store, bid, cid, 'data_review')
        self.assertFalse((self.store.root / 'intake-staging').exists())

    def test_tampered_members_and_wrong_anchor_rejected(self):
        bid, cid, _ = self.reviewed()
        staged = intake.prepare(self.store, bid, cid, 'data_review')
        folder = Path(staged['directory'])
        verify = lambda: intake.verify(self.store, bid, cid, 'data_review', folder, staged['manifest_sha256'])
        with self.assertRaisesRegex(ValueError, 'anchor'):
            intake.verify(self.store, bid, cid, 'data_review', folder, '0' * 64)
        extra = folder / 'unreviewed-source.xml'
        extra.write_text('not allowed')
        with self.assertRaisesRegex(ValueError, 'members'):
            verify()
        extra.unlink()
        (folder / 'summary.json').write_text('{}')
        with self.assertRaisesRegex(ValueError, 'Changed intake member'):
            verify()

    def test_new_review_invalidates_old_package(self):
        bid, cid, record = self.reviewed()
        staged = intake.prepare(self.store, bid, cid, 'data_review')
        prior = qualification.summary(self.store, bid, cid)['record_sha256']
        changed = copy.deepcopy(record)
        changed.update(previous_record_sha256=prior, amendment_reason='Fixture amendment')
        changed['limitations'].append('Additional fixture limit')
        qualification.submit(self.store, bid, changed)
        with self.assertRaisesRegex(ValueError, 'current proposal'):
            intake.verify(self.store, bid, cid, 'data_review', staged['directory'], staged['manifest_sha256'])

    def test_stale_source_prevents_verification(self):
        bid, cid, _ = self.reviewed()
        staged = intake.prepare(self.store, bid, cid, 'data_review')
        with self.store.db:
            self.store.db.execute("UPDATE candidates SET evidence_sha='changed'")
        with self.assertRaisesRegex(ValueError, 'scope-specific'):
            intake.verify(self.store, bid, cid, 'data_review', staged['directory'], staged['manifest_sha256'])

    def test_no_raw_text_or_arbitrary_paths_copied_and_cli_verifies(self):
        bid, cid, _ = self.reviewed()
        staged = intake.prepare(self.store, bid, cid, 'data_review')
        folder = Path(staged['directory'])
        self.assertEqual({p.name for p in folder.iterdir()}, {'review.json', 'summary.json', 'provenance.json', 'README.md', 'manifest.json'})
        manifest = json.loads((folder / 'manifest.json').read_text())
        self.assertTrue(manifest['proposed_ravel_path'].startswith('weft_intake/paper-'))
        self.assertFalse(manifest['automatic_integration_allowed'])
        with self.assertRaisesRegex(ValueError, 'staging path'):
            intake.verify(self.store, bid, cid, 'data_review', self.store.root, staged['manifest_sha256'])
        with patch('sys.stdout', new_callable=io.StringIO) as output:
            self.assertEqual(main(['intake-verify', '--store', str(self.store.root), '--batch', bid,
                                  '--candidate', cid, '--scope', 'data_review', '--directory', str(folder),
                                  '--manifest-sha256', staged['manifest_sha256']]), 0)
            self.assertEqual(json.loads(output.getvalue())['members'], 5)
