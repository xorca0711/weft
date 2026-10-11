import json
from pathlib import Path
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from test_executor import FakeDocker
from weft.artifacts import encoded, sha
from weft.executor import executor_sha256, FIXTURE
from weft.jobs import JobError, JobLedger
from weft.recovery import load_capsule, SOURCE_FILES


@unittest.skipUnless(os.name == "posix", "Executor recovery requires POSIX ownership and permission controls")
class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.inputs=self.root/'inputs';self.inputs.mkdir()
        (self.inputs/'fixture.txt').write_bytes(FIXTURE)
        self.ledger=JobLedger(self.root/'ledger.sqlite',clock=lambda:100.)
        self.addCleanup(self.ledger.db.close)
        packet={'schema_version':1,'kind':'synthetic-qualification',
            'paper_version_sha256':'a'*64,'context_sha256':'b'*64,'policy_sha256':'c'*64,
            'contract_sha256':'d'*64,'executor_sha256':executor_sha256('success',3),
            'max_attempts':1,'lease_seconds':30,
            'inputs':[{'path':'fixture.txt','bytes':len(FIXTURE),'sha256':sha(FIXTURE)}]}
        self.job=self.ledger.submit(packet)
        self.claim=self.ledger.claim(self.job,inputs_root=self.inputs,
            current_context_sha256='b'*64,current_policy_sha256='c'*64)
        self.run=self.root/'run'

    def launch(self,uncertain=True):
        self.docker=FakeDocker(uncertain=uncertain)
        return self.docker.execute(self.ledger,self.claim,inputs_root=self.inputs,run_root=self.run,wall_seconds=3)

    def test_capsule_modes_complete_source_and_no_secret_export(self):
        r=self.launch(uncertain=False)
        claim,m,source=load_capsule(self.run)
        self.assertEqual(claim,self.claim)
        self.assertEqual(set(m['sources']),set(SOURCE_FILES))
        capsule=self.run/'.weft-recovery'
        for p in [capsule,*capsule.rglob('*')]:
            self.assertEqual(stat.S_IMODE(p.stat().st_mode),0o700 if p.is_dir() else 0o600)
        with zipfile.ZipFile(r['archive']) as z:
            self.assertFalse(any('recovery' in n or 'claim' in n for n in z.namelist()))
            self.assertNotIn(self.claim['lease_token'].encode(),b''.join(z.read(n) for n in z.namelist()))
        self.assertNotIn(self.claim['lease_token'],json.dumps(r))

    def test_persistence_failure_before_docker_calls(self):
        with patch('weft.recovery.os.fsync',side_effect=OSError('disk full')):
            r=self.launch()
        self.assertEqual(r['outcome'],'held_unknown')
        self.assertEqual(self.docker.commands,[])
        self.assertEqual(self.ledger.status(self.job)['state'],'held_unknown')
        with self.assertRaises(JobError):load_capsule(self.run)
        with self.assertRaisesRegex(JobError,'legacy'):
            self.ledger.reconcile(self.claim['attempt_id'],self.claim['lease_token'],outcome='failed',receipt_ref='f'*64)

    def test_claim_tampering_cannot_authenticate(self):
        self.launch();p=self.run/'.weft-recovery/claim.json'
        value=json.loads(p.read_bytes());value['lease_token']='0'*48;p.write_bytes(encoded(value))
        with self.assertRaises(JobError):load_capsule(self.run)
        self.assertEqual(self.ledger.status(self.job)['state'],'held_unknown')

    def test_source_tampering_even_with_updated_manifest_rejected(self):
        self.launch();c=self.run/'.weft-recovery'
        p=c/'source/weft/executor.py';p.write_bytes(p.read_bytes()+b'\n# changed\n')
        m=json.loads((c/'manifest.json').read_bytes());m['sources']['executor.py']=sha(p.read_bytes())
        (c/'manifest.json').write_bytes(encoded(m))
        with self.assertRaises(JobError):load_capsule(self.run)

    def test_missing_and_unexpected_material_rejected(self):
        self.launch();c=self.run/'.weft-recovery';p=c/'source/weft/identity.py'
        data=p.read_bytes();p.unlink()
        with self.assertRaises(JobError):load_capsule(self.run)
        p.write_bytes(data);p.chmod(0o600)
        (c/'extra').write_bytes(b'x')
        with self.assertRaises(JobError):load_capsule(self.run)

    def test_symlinks_and_permissive_secret_file_rejected(self):
        self.launch();c=self.run/'.weft-recovery';p=c/'claim.json'
        p.chmod(0o644)
        with self.assertRaises(JobError):load_capsule(self.run)
        p.chmod(0o600);other=self.root/'secret';p.rename(other);p.symlink_to(other)
        with self.assertRaises(JobError):load_capsule(self.run)
        with self.assertRaises(JobError):load_capsule(self.root/'absent')

    def test_exclusive_capsule_prevents_overwrite_and_docker(self):
        self.run.mkdir();(self.run/'.weft-recovery').mkdir(mode=0o700)
        # Fresh run requirement independently rejects an existing directory.
        with self.assertRaises(FileExistsError):self.launch()
        self.assertEqual(self.docker.commands,[])

    def test_separate_process_loads_claim_and_exact_saved_package(self):
        self.launch()
        info=self.docker._inspect(self.docker.name) if not self.docker.uncertain else None
        self.docker.uncertain=False;info=self.docker._inspect(self.docker.name)
        observations=self.root/'fake-observation.json';observations.write_text(json.dumps(info))
        script='''import sys,json,subprocess
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,sys.argv[1])
from weft.recovery import recover_from_capsule
import weft.executor
weft.executor.code_sha256=lambda:'0'*64 # current module cannot satisfy the old binding
info=json.loads(Path(sys.argv[3]).read_text())
def docker(args,**kw):
 op=args[2]
 if op=='inspect':out=json.dumps([info]).encode()
 elif op=='logs':
  from weft.executor import expected_result
  out=json.dumps(expected_result()).encode()
 elif op=='rm':out=b''
 else:raise AssertionError(op)
 return subprocess.CompletedProcess(args,0,out,b'')
with patch('subprocess.run',side_effect=docker):r=recover_from_capsule(sys.argv[2])
assert r['outcome']=='local_verified'
print(json.dumps({'outcome':r['outcome'],'code_sha256':r['identity']['code_sha256']}))
'''
        repo=str(Path(__file__).resolve().parents[1])
        p=subprocess.run([sys.executable,'-I','-B','-c',script,repo,str(self.run),str(observations)],
            capture_output=True,text=True,timeout=10)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertEqual(json.loads(p.stdout)['outcome'],'local_verified')
        self.assertNotIn(self.claim['lease_token'],p.stdout+p.stderr)
        self.assertEqual(self.ledger.status(self.job)['state'],'local_verified')
        load_capsule(self.run) # importing snapshots must not add __pycache__ material


if __name__=='__main__':unittest.main()
