import copy
import io
import json
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
import zipfile

from weft.artifacts import (encoded, make_bundle, sha, verify_bundle, write_archive, restore_archive, MAX_MEMBER)
from weft.executor import DockerExecutor, FIXTURE, IMAGE, IMAGE_ID, WORKER, executor_sha256, expected_result
from weft.jobs import JobError, JobLedger


class FakeDocker(DockerExecutor):
    """Daemon fixture; production always uses the documented local Docker socket."""
    def __init__(self, mode='success', absent=True, uncertain=False):
        self.mode, self.absent, self.uncertain = mode, absent, uncertain
        self.started = False
        self.killed = False
        self.commands = []

    def _docker(self, args, timeout=3):
        self.commands.append(args)
        if args[0] == 'image': return IMAGE_ID.encode()
        if args[0] == 'create':
            self.name = args[args.index('--name')+1]
            self.stage = args[args.index('--mount')+1].split('src=')[1].split(',')[0]
            for flag in ('--pull', '--network', '--cpus', '--memory', '--memory-swap', '--pids-limit',
                         '--cap-drop', '--security-opt', '--user', '--read-only', '--tmpfs'):
                assert flag in args
            assert IMAGE in args and '--privileged' not in args
            return b'1'*64
        if args[0] == 'start': self.started = True
        if args[0] == 'kill': self.killed = True
        if args[0] == 'logs': return encoded(expected_result())
        return b''

    def _inspect(self, name):
        if self.started and self.uncertain:
            raise JobError('daemon unavailable')
        if self.started and self.mode == 'cancel' and not self.killed:
            raise subprocess.TimeoutExpired('wait', 1)
        exit_code = 137 if self.killed else (23 if self.mode == 'failure' else 0)
        return {'Image':IMAGE_ID,'Id':'1'*64,'Name':'/'+self.name,
            'Config':{'Image':IMAGE,'User':'65534:65534','Entrypoint':None,
                      'Cmd':['python','-I','-u','-c',WORKER,self.mode,sha(FIXTURE)],
                      'Labels':{'weft.executor':self.name}},
            'Mounts':[{'Source':self.stage,'Destination':'/inputs','RW':False}],
            'HostConfig':{'NetworkMode':'none','Privileged':False,'ReadonlyRootfs':True,
                'Memory':268435456,'MemorySwap':268435456,'PidsLimit':32,'NanoCpus':1000000000,
                'CapDrop':['ALL'],'CapAdd':None,'SecurityOpt':['no-new-privileges:true'],
                'Tmpfs':{'/tmp':'rw,noexec,nosuid,nodev,size=16m,mode=1777'}},
            'State':{'Status':'exited','Running':False,'Pid':0,'Error':'','ExitCode':exit_code,'OOMKilled':False}}

    def _processes(self, name):
        return [{'pid':123,'start':'100'}]

    def _absent(self, processes):
        return self.absent and bool(processes)


class ExecutorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.inputs=self.root/'inputs';self.inputs.mkdir()
        (self.inputs/'fixture.txt').write_bytes(FIXTURE)
        self.clock=[100.]
        self.ledger=JobLedger(self.root/'ledger.sqlite',clock=lambda:self.clock[0])
        self.addCleanup(self.ledger.db.close)

    def claim(self, mode='success'):
        packet={'schema_version':1,'kind':'synthetic-qualification',
            'paper_version_sha256':'a'*64,'context_sha256':'b'*64,'policy_sha256':'c'*64,
            'contract_sha256':'d'*64,'executor_sha256':executor_sha256(mode,3),
            'max_attempts':2,'lease_seconds':30,
            'inputs':[{'path':'fixture.txt','bytes':len(FIXTURE),'sha256':sha(FIXTURE)}]}
        key=self.ledger.submit(packet)
        return self.ledger.claim(key,inputs_root=self.inputs,current_context_sha256='b'*64,current_policy_sha256='c'*64)

    def run_fixture(self, mode='success', **kw):
        claim=self.claim(mode);executor=FakeDocker(mode,**kw)
        result=executor.execute(self.ledger,claim,inputs_root=self.inputs,run_root=self.root/'run',mode=mode,wall_seconds=3)
        return claim,executor,result

    def test_success_local_only_and_content_verified(self):
        claim,e,r=self.run_fixture()
        self.assertEqual(r['outcome'],'local_verified');self.assertFalse(r['external_export_verified'])
        self.assertEqual(self.ledger.status(claim['job_id'])['state'],'local_verified')
        self.assertNotEqual(self.ledger.status(claim['job_id'])['state'],'complete')
        restored=restore_archive(r['archive'],self.root/'restored',identity=r['identity'],
            terminal_sha256=r['terminal_sha256'],archive_sha256=r['archive_sha256'])
        self.assertEqual(restored['outcome'],'local_verified')
        self.assertEqual(json.loads((self.root/'restored/result.json').read_bytes()),expected_result())

    def test_failure_and_cancel_have_no_success_outputs(self):
        for mode,outcome in [('failure','failed'),('cancel','cancelled')]:
            with self.subTest(mode=mode):
                claim=self.claim(mode);e=FakeDocker(mode)
                r=e.execute(self.ledger,claim,inputs_root=self.inputs,run_root=self.root/mode,mode=mode,wall_seconds=3)
                self.assertEqual(r['outcome'],outcome)
                self.assertFalse((self.root/mode/'bundle/result.json').exists())
                self.assertEqual(self.ledger.status(claim['job_id'])['state'],outcome)

    def test_unknown_reserves_slot_and_legacy_reconcile_rejected(self):
        claim,e,r=self.run_fixture(uncertain=True)
        self.assertEqual(r['outcome'],'held_unknown')
        self.assertFalse(any(c[0]=='rm' for c in e.commands))
        with self.assertRaisesRegex(JobError,'legacy'):
            self.ledger.reconcile(claim['attempt_id'],claim['lease_token'],outcome='failed',receipt_ref='f'*64)
        with self.assertRaisesRegex(JobError,'reserves'):
            self.claim('failure')

    def test_process_presence_is_unknown(self):
        claim,e,r=self.run_fixture(absent=False)
        self.assertEqual(r['outcome'],'held_unknown')
        self.assertIsNone(self.ledger.executor_binding(claim)['terminal_sha256'])

    def test_expiry_restart_and_recovery_requires_new_observation(self):
        claim,e,r=self.run_fixture(uncertain=True)
        self.clock[0]=131;self.ledger.expire()
        with JobLedger(self.root/'ledger.sqlite',clock=lambda:132) as reopened:
            self.assertEqual(reopened.status(claim['job_id'])['state'],'held_unknown')
            e.uncertain=False
            recovered=e.recover(reopened,claim,run_root=self.root/'run')
            self.assertEqual(recovered['outcome'],'local_verified')
            self.assertTrue(e.recover(reopened,claim,run_root=self.root/'run')['already_terminal'])

    def test_expired_unbound_attempt_cannot_start(self):
        claim=self.claim();self.clock[0]=131;self.ledger.expire()
        e=FakeDocker()
        with self.assertRaisesRegex(JobError,'Expired'):
            e.execute(self.ledger,claim,inputs_root=self.inputs,run_root=self.root/'run',wall_seconds=3)
        self.assertEqual(e.commands,[])

    def test_lease_and_attempt_identity_rejected(self):
        claim=self.claim()
        for change in ({'lease_token':'wrong'},{'job_id':'f'*64},{'attempt_id':999}):
            with self.assertRaises(JobError):
                self.ledger._attempt({**claim,**change})

    def test_code_input_identity_and_arbitrary_worker_rejected(self):
        claim=self.claim();e=FakeDocker()
        with self.assertRaises(JobError):
            e.execute(self.ledger,claim,inputs_root=self.inputs,run_root=self.root/'bad',mode='failure',wall_seconds=3)
        (self.inputs/'fixture.txt').write_bytes(b'wrong')
        with self.assertRaises(JobError):
            e.execute(self.ledger,claim,inputs_root=self.inputs,run_root=self.root/'bad',wall_seconds=3)
        with self.assertRaises(JobError):executor_sha256('shell',3)
        self.assertEqual(e.commands,[])

    def test_process_snapshot_tampering_cannot_release(self):
        claim,e,r=self.run_fixture(uncertain=True)
        state=self.root/'run/run-state.json';value=json.loads(state.read_bytes())
        value['processes']=[{'pid':99999999,'start':'fake'}];state.write_bytes(encoded(value))
        e.uncertain=False
        self.assertEqual(e.recover(self.ledger,claim,run_root=self.root/'run')['outcome'],'held_unknown')

    def test_exit_during_process_sample_is_reobserved(self):
        class Exiting(FakeDocker):
            def __init__(self):super().__init__();self.inspections=0;self.samples=0
            def _inspect(self,name):
                info=super()._inspect(name)
                if self.started:
                    self.inspections+=1
                    if self.inspections==1:info['State']['Running']=True
                return info
            def _processes(self,name):
                self.samples+=1
                if self.samples>1:raise JobError('exited during top')
                return super()._processes(name)
        claim=self.claim();r=Exiting().execute(self.ledger,claim,inputs_root=self.inputs,
            run_root=self.root/'race',wall_seconds=3)
        self.assertEqual(r['outcome'],'local_verified')

    def test_recovery_code_drift_is_unknown(self):
        from unittest.mock import patch
        claim,e,r=self.run_fixture(uncertain=True);e.uncertain=False
        with patch('weft.executor.code_sha256',return_value='f'*64):
            self.assertEqual(e.recover(self.ledger,claim,run_root=self.root/'run')['outcome'],'held_unknown')

    def test_cancel_request_is_observed_without_releasing_early(self):
        claim=self.claim('cancel')
        ledger=self.ledger
        class Requested(FakeDocker):
            def _processes(self,name):
                ledger.cancel(claim['job_id'])
                return super()._processes(name)
        r=Requested('cancel').execute(ledger,claim,inputs_root=self.inputs,
            run_root=self.root/'request',mode='cancel',wall_seconds=3)
        self.assertEqual(r['outcome'],'cancelled')
        o=json.loads((self.root/'request/bundle/terminal.json').read_bytes())['observation']
        self.assertTrue(o['cancel_requested']);self.assertFalse(o['timed_out'])

    def test_container_control_drift_is_unknown(self):
        class Drift(FakeDocker):
            def _inspect(self,name):
                x=super()._inspect(name);x['HostConfig']['PidsLimit']=0;return x
        claim=self.claim();e=Drift()
        self.assertEqual(e.execute(self.ledger,claim,inputs_root=self.inputs,run_root=self.root/'run',wall_seconds=3)['outcome'],'held_unknown')


class ArtifactTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        self.identity={'job_id':'a'*64,'attempt_id':1,'container_id':'b'*64,'code_sha256':'c'*64,'inputs_sha256':'d'*64}
        self.o={'container_id':'b'*64,'status':'exited','running':False,'pid':0,'exit_code':0,
                'oom_killed':False,'processes_absent':True,'timed_out':False,'cancel_requested':False}
        self.files=make_bundle(self.identity,'local_verified',self.o,expected_result());self.anchor=sha(self.files['terminal.json'])

    def verify(self, files=None, identity=None):
        return verify_bundle(files or self.files,identity=identity or self.identity,terminal_sha256=self.anchor)

    def test_tampered_receipts_outputs_missing_and_unexpected(self):
        for name in self.files:
            files=dict(self.files);files[name]+=b' '
            with self.assertRaises(JobError):self.verify(files)
            files=dict(self.files);files.pop(name)
            with self.assertRaises(JobError):self.verify(files)
        with self.assertRaises(JobError):self.verify({**self.files,'evil.py':b'x'})

    def test_wrong_attempt_container_code_input_job_identity(self):
        for key in self.identity:
            identity={**self.identity,key:999 if key=='attempt_id' else 'f'*64}
            with self.assertRaises(JobError):self.verify(identity=identity)

    def test_canonical_duplicate_json_and_false_terminal(self):
        for change in ({'running':True},{'processes_absent':False},{'exit_code':23},{'timed_out':True}):
            files=make_bundle(self.identity,'local_verified',{**self.o,**change},expected_result())
            with self.assertRaises(JobError):verify_bundle(files,identity=self.identity,terminal_sha256=sha(files['terminal.json']))
        files=dict(self.files);files['terminal.json']=b'{"schema_version":1,"schema_version":1}'
        with self.assertRaises(JobError):verify_bundle(files,identity=self.identity,terminal_sha256=sha(files['terminal.json']))

    def test_deterministic_archive_and_restore(self):
        a=self.root/'a.zip';b=self.root/'b.zip';write_archive(a,self.files);write_archive(b,self.files)
        self.assertEqual(a.read_bytes(),b.read_bytes())
        restore_archive(a,self.root/'restored',identity=self.identity,terminal_sha256=self.anchor,archive_sha256=sha(a.read_bytes()))
        with self.assertRaises(FileExistsError):
            restore_archive(a,self.root/'restored',identity=self.identity,terminal_sha256=self.anchor,archive_sha256=sha(a.read_bytes()))

    def test_archive_tampering_and_identity_anchor(self):
        a=self.root/'a.zip';write_archive(a,self.files)
        with self.assertRaises(JobError):restore_archive(a,self.root/'x',identity=self.identity,terminal_sha256='0'*64,archive_sha256=sha(a.read_bytes()))
        raw=a.read_bytes();a.write_bytes(raw+b'tampered')
        with self.assertRaises(JobError):restore_archive(a,self.root/'x',identity=self.identity,terminal_sha256=self.anchor,archive_sha256=sha(raw))

    def test_bounded_member_paths_symlinks_duplicates_and_expansion(self):
        cases=[('../terminal.json',b'x',None),('/terminal.json',b'x',None),('unexpected',b'x',None),
            ('terminal.json',b'x',stat.S_IFLNK|0o777),('terminal.json',b'x'*(MAX_MEMBER+1),None)]
        for index,(name,data,mode) in enumerate(cases):
            a=self.root/(str(index)+'.zip')
            with zipfile.ZipFile(a,'w',compression=zipfile.ZIP_DEFLATED) as z:
                i=zipfile.ZipInfo(name)
                if mode:i.create_system=3;i.external_attr=mode<<16
                z.writestr(i,data)
            with self.assertRaises(JobError):restore_archive(a,self.root/('r'+str(index)),identity=self.identity,terminal_sha256=self.anchor,archive_sha256=sha(a.read_bytes()))
        a=self.root/'duplicate.zip'
        with zipfile.ZipFile(a,'w') as z:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter('ignore');z.writestr('terminal.json',b'x');z.writestr('terminal.json',b'x')
        with self.assertRaises(JobError):restore_archive(a,self.root/'rdup',identity=self.identity,terminal_sha256=self.anchor,archive_sha256=sha(a.read_bytes()))

    def test_zip_crc_checked_even_with_matching_archive_hash(self):
        a=self.root/'crc.zip';write_archive(a,self.files)
        raw=bytearray(a.read_bytes())
        with zipfile.ZipFile(a) as z:
            i=z.getinfo('result.json');offset=i.header_offset+30+len(i.filename.encode())+len(i.extra)
        raw[offset] ^= 1;a.write_bytes(raw)
        with self.assertRaisesRegex(JobError,'ZIP/CRC'):
            restore_archive(a,self.root/'crc-restore',identity=self.identity,
                            terminal_sha256=self.anchor,archive_sha256=sha(raw))

    def test_json_boolean_cannot_alias_integer_schema_or_identity(self):
        identity={**self.identity,'attempt_id':True}
        files=make_bundle(identity,'local_verified',self.o,expected_result())
        with self.assertRaises(JobError):
            verify_bundle(files,identity=self.identity,terminal_sha256=sha(files['terminal.json']))
        files=dict(self.files);m=json.loads(files['output-manifest.json']);m['schema_version']=True
        files['output-manifest.json']=encoded(m)
        t=json.loads(files['terminal.json']);t['output_manifest_sha256']=sha(files['output-manifest.json'])
        files['terminal.json']=encoded(t)
        with self.assertRaises(JobError):
            verify_bundle(files,identity=self.identity,terminal_sha256=sha(files['terminal.json']))

    def test_destination_symlink_rejected(self):
        a=self.root/'a.zip';write_archive(a,self.files);(self.root/'link').symlink_to(self.root,target_is_directory=True)
        with self.assertRaises(JobError):restore_archive(a,self.root/'link/new',identity=self.identity,terminal_sha256=self.anchor,archive_sha256=sha(a.read_bytes()))


if __name__=='__main__':unittest.main()
