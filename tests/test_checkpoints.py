import copy
import json
import os
from pathlib import Path
import sqlite3
import stat
import tempfile
import unittest
from unittest.mock import patch
import warnings
import zipfile

from weft.artifacts import encoded, sha, write_archive
from weft.checkpoints import (CheckpointError, create_checkpoint, restore_checkpoint,
                              inspect_schema, RECONCILIATION)


class CheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.source=self.root/'live.sqlite'
        self.db=sqlite3.connect(self.source);self.addCleanup(self.db.close)
        self.db.execute('PRAGMA journal_mode=WAL');self.db.execute('PRAGMA wal_autocheckpoint=0')
        self.db.execute('CREATE TABLE state(id INTEGER PRIMARY KEY, stage TEXT NOT NULL)')
        self.db.execute("INSERT INTO state VALUES(1,'held_unknown')");self.db.commit()
        self.schema=inspect_schema(self.source)
        self.kw={'ledger_identity':'manual-synthetic-ledger-v1','reference':{'stage':'P001-fixture'},
            'phase':'before-dispatch','source_revision':'c8ab57024b355314a3a84c8400093a173aa9f3f1',
            'expected_schema_sha256':self.schema}

    def checkpoint(self,**kw):
        return create_checkpoint(self.source,self.root/'staging',**{**self.kw,**kw})

    def restore(self,r,**kw):
        return restore_checkpoint(r['archive'],self.root/'restored',
            **{'expected_archive_sha256':r['archive_sha256'],'ledger_identity':self.kw['ledger_identity'],
               'expected_schema_sha256':self.schema,**kw})

    def test_wal_consistent_committed_snapshot_source_unchanged(self):
        wal=Path(str(self.source)+'-wal')
        before=(self.source.read_bytes(),wal.read_bytes())
        self.db.execute("INSERT INTO state VALUES(2,'uncommitted')")
        r=self.checkpoint()
        self.assertEqual((self.source.read_bytes(),wal.read_bytes()),before)
        self.assertEqual(self.db.execute('SELECT count(*) FROM state').fetchone()[0],2)
        restored=self.restore(r)
        with sqlite3.connect(Path(restored['directory']).joinpath('ledger.sqlite').as_uri()+'?mode=ro',uri=True) as d:
            self.assertEqual(d.execute('SELECT * FROM state').fetchall(),[(1,'held_unknown')])
            with self.assertRaises(sqlite3.OperationalError):d.execute("DELETE FROM state")
        self.assertEqual(restored['status'],RECONCILIATION)
        self.assertFalse(restored['activation_permitted']);self.assertFalse(restored['upload_verified'])

    def test_restore_never_instantiates_active_ledger_or_executes_jobs(self):
        r=self.checkpoint()
        with patch('weft.jobs.JobLedger',side_effect=AssertionError('must not activate')):
            out=self.restore(r)
        self.assertEqual(out['status'],RECONCILIATION)
        self.assertEqual(set(p.name for p in Path(out['directory']).iterdir()),{'ledger.sqlite','checkpoint-manifest.json'})

    def test_exact_members_unique_id_parent_job_attempt_and_phase(self):
        r=self.checkpoint(reference={'job_id':'a'*64,'attempt_id':2},phase='after-run',parent_checkpoint_sha256='b'*64)
        m=r['manifest'];self.assertEqual(m['reference']['attempt_id'],2)
        self.assertEqual(m['parent_checkpoint_sha256'],'b'*64)
        with zipfile.ZipFile(r['archive']) as z:self.assertEqual(set(z.namelist()),{'ledger.sqlite','checkpoint-manifest.json'})
        other=create_checkpoint(self.source,self.root/'another',**self.kw)
        self.assertNotEqual(other['manifest']['checkpoint_id'],m['checkpoint_id'])

    def test_wrong_external_identity_hash_and_schema_rejected_before_destination(self):
        r=self.checkpoint()
        for change in ({'ledger_identity':'different'},{'expected_archive_sha256':'0'*64},{'expected_schema_sha256':'0'*64}):
            with self.assertRaises(CheckpointError):self.restore(r,**change)
            self.assertFalse((self.root/'restored').exists())

    def test_fresh_staging_and_destination_required(self):
        r=self.checkpoint();self.restore(r)
        with self.assertRaises(FileExistsError):self.restore(r)
        with self.assertRaises(FileExistsError):self.checkpoint()

    def test_size_and_time_limits(self):
        with self.assertRaises(CheckpointError):self.checkpoint(max_bytes=4096)
        self.assertFalse((self.root/'staging/checkpoint.zip').exists())
        for seconds in (0,11,float('nan')):
            with self.assertRaises(CheckpointError):create_checkpoint(self.source,self.root/'bad',**self.kw,max_seconds=seconds)
        # An expired deadline prevents backup completion; source remains untouched.
        with patch('weft.checkpoints.time.monotonic',side_effect=[100,101,101,101,101,101,101,101]):
            with self.assertRaises(CheckpointError):create_checkpoint(self.source,self.root/'timed',**self.kw,max_seconds=.001)

    def test_bad_metadata_rejected(self):
        for change in ({'phase':'complete'},{'reference':{'command':'run'}},{'reference':{'job_id':'a'*64,'attempt_id':True}},
                       {'source_revision':'moving-main'},{'parent_checkpoint_sha256':'bad'}):
            with self.assertRaises(CheckpointError):self.checkpoint(**change)

    def read_members(self,r):
        with zipfile.ZipFile(r['archive']) as z:return {n:z.read(n) for n in z.namelist()}

    def reject_members(self,members,name='bad.zip'):
        path=self.root/name;write_archive(path,members)
        r={'archive':str(path),'archive_sha256':sha(path.read_bytes())}
        with self.assertRaises(CheckpointError):self.restore(r)
        self.assertFalse((self.root/'restored').exists())

    def test_missing_unexpected_traversal_and_token_capsule_names(self):
        r=self.checkpoint();members=self.read_members(r)
        for i,name in enumerate(['../ledger.sqlite','/ledger.sqlite','private/claim.json','.weft-recovery/claim.json','extra']):
            self.reject_members({**members,name:b'not permitted'},str(i)+'.zip')
        self.reject_members({'checkpoint-manifest.json':members['checkpoint-manifest.json']},'missing.zip')

    def test_duplicate_symlink_special_and_encrypted_members(self):
        r=self.checkpoint();members=self.read_members(r)
        for kind in ['duplicate','symlink','special','encrypted']:
            path=self.root/(kind+'.zip')
            with zipfile.ZipFile(path,'w') as z:
                for name,data in members.items():
                    i=zipfile.ZipInfo(name);i.create_system=3
                    i.external_attr=(stat.S_IFLNK if kind=='symlink' else stat.S_IFIFO if kind=='special' else stat.S_IFREG)<<16
                    z.writestr(i,data)
                if kind=='duplicate':
                    with warnings.catch_warnings():warnings.simplefilter('ignore');z.writestr('ledger.sqlite',b'bad')
            if kind=='encrypted':
                data=bytearray(path.read_bytes());offset=data.index(b'PK\x01\x02');data[offset+8]|=1;path.write_bytes(data)
            with self.assertRaises(CheckpointError):self.restore({'archive':str(path),'archive_sha256':sha(path.read_bytes())})
            self.assertFalse((self.root/'restored').exists())

    def test_crc_and_sqlite_corruption_before_destination(self):
        r=self.checkpoint();members=self.read_members(r)
        self.reject_members({**members,'ledger.sqlite':b'corrupted'},'hashdrift.zip')
        m=json.loads(members['checkpoint-manifest.json']);m['files']=[{'path':'ledger.sqlite','bytes':9,'sha256':sha(b'corrupted')}]
        self.reject_members({'ledger.sqlite':b'corrupted','checkpoint-manifest.json':encoded(m)},'databasebad.zip')
        path=self.root/'crc.zip';write_archive(path,members)
        data=bytearray(path.read_bytes())
        with zipfile.ZipFile(path) as z:
            i=z.getinfo('ledger.sqlite');offset=i.header_offset+30+len(i.filename.encode())+len(i.extra)
        data[offset]^=1;path.write_bytes(data)
        with self.assertRaises(CheckpointError):self.restore({'archive':str(path),'archive_sha256':sha(data)})

    def test_malformed_manifest_and_expansion_excess(self):
        r=self.checkpoint();members=self.read_members(r)
        self.reject_members({**members,'checkpoint-manifest.json':b'{"x":1,"x":2}'},'duplicate-json.zip')
        m=json.loads(members['checkpoint-manifest.json']);m['schema_version']=True
        self.reject_members({**members,'checkpoint-manifest.json':encoded(m)},'wrong-schema.zip')
        path=self.root/'expansion.zip'
        with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED) as z:
            z.writestr('ledger.sqlite',b'x'*(1048576+1));z.writestr('checkpoint-manifest.json',members['checkpoint-manifest.json'])
        with self.assertRaises(CheckpointError):self.restore({'archive':str(path),'archive_sha256':sha(path.read_bytes())},max_bytes=1048576)

    @unittest.skipUnless(os.name=='posix','POSIX private directory/file permissions')
    def test_private_permissions_and_symlink_rejection(self):
        r=self.checkpoint();out=self.restore(r)
        directory=Path(out['directory'])
        self.assertEqual(stat.S_IMODE(directory.stat().st_mode),0o700)
        for p in directory.iterdir():self.assertEqual(stat.S_IMODE(p.stat().st_mode),0o600)
        (self.root/'link').symlink_to(self.source)
        with self.assertRaises(CheckpointError):create_checkpoint(self.root/'link',self.root/'bad',**self.kw)


if __name__=='__main__':unittest.main()
