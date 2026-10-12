import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from weft import batches, screening
from weft.discovery import Store
from weft.identity import digest
from weft.reading_locations import SCOPE, legacy_relative, relocate_readings, store_directory
import test_batches
import test_reading


class PortabilityTests(unittest.TestCase):
    setUp = test_batches.BatchTests.setUp
    create = test_batches.BatchTests.create
    run_batch = test_batches.BatchTests.run_batch
    response = test_batches.BatchTests.response
    screen = test_batches.BatchTests.screen

    def prepared(self):
        bid = self.create()
        self.run_batch(bid)
        issued, response = self.screen(bid)
        cid = issued['packet']['candidate_id']
        read = screening.read_packet(self.store, bid, cid, fetch=lambda _: test_reading.XML)
        assessment = test_reading.ReadingTests.assessment(self, {**read, 'directory': read['resolved_directory']})
        return bid, cid, read, assessment

    def copy_store(self, name='restored'):
        # No writer is active; checkpoint a closed SQLite file in this fixture.
        path = Path(self.temp.name) / name
        shutil.copytree(self.store.root, path)
        other = Store(path)
        self.addCleanup(other.db.close)
        return other

    def make_legacy(self, bid, cid, read, source_root):
        old = {k:v for k,v in read.items() if k not in {'directory_scope','resolved_directory'}}
        separator = '\\' if ':' in source_root else '/'
        old['directory'] = source_root.rstrip('/\\') + separator + read['directory']
        with self.store.db:
            self.store.db.execute('UPDATE batch_items SET reading_json=? WHERE batch_id=? AND candidate_id=?',
                                  (json.dumps(old),bid,cid))
        return old

    def test_new_result_persists_no_host_path(self):
        bid,cid,read,_ = self.prepared()
        self.assertEqual(read['directory_scope'],SCOPE)
        self.assertEqual(Path(read['resolved_directory']),self.store.root/read['directory'])
        stored=json.loads(self.store.db.execute('SELECT reading_json FROM batch_items').fetchone()[0])
        self.assertNotIn('resolved_directory',stored)
        self.assertEqual(stored['directory'],Path(read['resolved_directory']).name)

    def test_relocated_store_resumes_without_fetch_and_preserves_packet(self):
        bid,cid,read,assessment=self.prepared()
        other=self.copy_store()
        resumed=screening.read_packet(other,bid,cid,fetch=lambda _:self.fail('no fetch on restore'))
        self.assertEqual(resumed['directory'],read['directory'])
        self.assertNotEqual(resumed['resolved_directory'],read['resolved_directory'])
        self.assertEqual(screening.submit_reading(other,bid,assessment)['status'],'review_required')
        self.assertEqual(screening.submit_reading(other,bid,assessment)['status'],'already_recorded')
        self.assertIsNone(self.store.db.execute('SELECT reading_result_json FROM batch_items').fetchone()[0])

    def test_windows_legacy_mapping_is_explicit_and_auditable(self):
        bid,cid,read,assessment=self.prepared()
        root=r'X:\GitHub\weft\runs\original'
        old=self.make_legacy(bid,cid,read,root)
        other=self.copy_store()
        with self.assertRaises(ValueError):screening.read_packet(other,bid,cid)
        directory=other.root/read['directory']
        before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.iterdir()}
        self.assertEqual(relocate_readings(other,bid,root)['changed_readings'],1)
        self.assertEqual(relocate_readings(other,bid,root)['status'],'already_portable')
        self.assertEqual(screening.submit_reading(other,bid,assessment)['status'],'review_required')
        after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in directory.iterdir()}
        self.assertEqual(before,after)
        event=json.loads(other.db.execute("SELECT record_json FROM batch_events WHERE action='reading-path-relocated'").fetchone()[0])
        self.assertEqual(event['previous_result'],old)
        self.assertEqual(event['previous_result_sha256'],digest(old))
        self.assertEqual(json.loads(self.store.db.execute('SELECT reading_json FROM batch_items').fetchone()[0]),old)

    def test_posix_legacy_mapping_works_after_copy(self):
        bid,cid,read,_=self.prepared()
        root='/workspace/original-store'
        self.make_legacy(bid,cid,read,root)
        other=self.copy_store()
        self.assertEqual(relocate_readings(other,bid,root)['changed_readings'],1)
        self.assertEqual(screening.read_packet(other,bid,cid)['directory_scope'],SCOPE)

    def test_wrong_root_or_tamper_does_not_update_rows(self):
        bid,cid,read,_=self.prepared()
        root=r'X:\GitHub\weft\runs\original'
        old=self.make_legacy(bid,cid,read,root)
        other=self.copy_store()
        for changed_root in [r'X:\GitHub\weft\runs\other','original','/workspace/original']:
            with self.assertRaises(ValueError):relocate_readings(other,bid,changed_root)
        (other.root/read['directory']/'source.xml').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError,'source changed'):relocate_readings(other,bid,root)
        self.assertEqual(json.loads(other.db.execute('SELECT reading_json FROM batch_items').fetchone()[0]),old)
        self.assertEqual(other.db.execute("SELECT COUNT(*) FROM batch_events WHERE action='reading-path-relocated'").fetchone()[0],0)

    def test_cross_candidate_binding_rejected(self):
        bid,cid,read,_=self.prepared()
        root='/workspace/old'
        self.make_legacy(bid,cid,read,root)
        with self.store.db:
            packet=json.loads(self.store.db.execute('SELECT packet_json FROM batch_items').fetchone()[0])
            packet['candidate_id']='unrelated'
            self.store.db.execute('UPDATE batch_items SET packet_json=?,packet_sha=?',(json.dumps(packet),digest(packet)))
        with self.assertRaisesRegex(ValueError,'identity differs'):relocate_readings(self.store,bid,root)

    def test_path_traversal_mixed_flavors_and_prefix_collision_rejected(self):
        name='reading-'+'a'*32
        invalid=[('/workspace/store/../'+name,'/workspace/store'),
                 ('/workspace/store-extra/'+name,'/workspace/store'),
                 ('/workspace/store/nested/'+name,'/workspace/store'),
                 ('X:\\store\\..\\'+name,r'X:\store'),
                 ('X:\\store2\\'+name,r'X:\store'),
                 ('/workspace/store/'+name+':stream','/workspace/store'),
                 ('/workspace/store/'+name+'\\other','/workspace/store')]
        for raw,root in invalid:
            with self.subTest(raw=raw),self.assertRaises(ValueError):legacy_relative(raw,root)
        for raw in ['../'+name,'/'+name,'X:/'+name,name+'/child',name+' ',name+'.']:
            with self.subTest(raw=raw),self.assertRaises(ValueError):store_directory(self.store,raw)

    def test_linked_reading_artifact_rejected(self):
        bid,cid,read,_=self.prepared()
        directory=Path(read['resolved_directory'])
        target=directory/'source.xml'
        alternate=directory/'source-preserved.xml'
        target.rename(alternate)
        try:target.symlink_to(alternate)
        except OSError:
            alternate.rename(target)
            self.skipTest('Symlink creation unavailable on this host')
        with self.assertRaisesRegex(ValueError,'linked'):screening.read_packet(self.store,bid,cid)

    def test_unknown_scope_is_not_silently_rewritten(self):
        bid,cid,read,_=self.prepared()
        stored={k:v for k,v in read.items() if k!='resolved_directory'}
        stored['directory_scope']='unsupported-v99'
        with self.store.db:self.store.db.execute('UPDATE batch_items SET reading_json=?',(json.dumps(stored),))
        with self.assertRaisesRegex(ValueError,'Unknown'):relocate_readings(self.store,bid,str(self.store.root))

    def test_existing_assessment_and_budget_survive_relocation(self):
        bid,cid,read,assessment=self.prepared()
        screening.submit_reading(self.store,bid,assessment)
        self.make_legacy(bid,cid,read,'/workspace/old')
        other=self.copy_store()
        before=batches.status_report(other,bid)
        relocate_readings(other,bid,'/workspace/old')
        self.assertEqual(before,batches.status_report(other,bid))
        self.assertEqual(screening.submit_reading(other,bid,assessment)['status'],'already_recorded')
