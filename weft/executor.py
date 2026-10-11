"""Trusted local Docker adapter for one built-in SYNTHETIC fixture only.

No author commands, network, scientific input, remote dispatch or Drive SDK.
Uncertain daemon/process outcomes reserve the ledger slot for explicit recovery.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid

from .artifacts import encoded, decode, make_bundle, sha, verify_bundle, write_archive
from .identity import digest
from .jobs import JobError, verify_files

IMAGE = 'python@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1'
IMAGE_ID = 'sha256:df18428df8a0f9189c84e7424d214b4c50092af1f9dca5842a00c41c39bda316'
FIXTURE = b'synthetic fixture'
WORKER = '''import hashlib,json,pathlib,sys,time,subprocess,os
mode=sys.argv[1]
assert os.getuid()==65534
security=pathlib.Path('/proc/self/status').read_text()
assert 'CapEff:\t0000000000000000' in security and 'NoNewPrivs:\t1' in security
data=pathlib.Path('/inputs/fixture.txt').read_bytes()
assert data==b'synthetic fixture'
assert hashlib.sha256(data).hexdigest()==sys.argv[2]
assert {k:pathlib.Path('/sys/fs/cgroup/'+k).read_text().strip() for k in ['memory.max','memory.swap.max','pids.max','cpu.max']}=={'memory.max':'268435456','memory.swap.max':'0','pids.max':'32','cpu.max':'100000 100000'}
assert pathlib.Path('/sys/class/net').joinpath('lo').exists()
time.sleep(.8)
if mode=='failure':sys.exit(23)
if mode=='cancel':
 child="import subprocess,sys; p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)']); p.wait()"
 p=subprocess.Popen([sys.executable,'-c',child]);p.wait()
else:
 print(json.dumps({'kind':'synthetic-qualification','input_sha256':hashlib.sha256(data).hexdigest(),'values':[x*x for x in range(8)]},sort_keys=True,separators=(',',':')),flush=True)
'''


def code_sha256():
    """Bind worker plus all adapter/receipt/ledger implementation bytes."""
    root = Path(__file__).parent
    return digest({name: sha((root / name).read_bytes()) for name in
                   ('executor.py', 'artifacts.py', 'jobs.py', 'identity.py', 'validation.py')})


def executor_sha256(mode='success', wall_seconds=10):
    check_options(mode, wall_seconds)
    return digest({'code': code_sha256(), 'worker': sha(WORKER.encode()),
                   'image': IMAGE, 'image_id': IMAGE_ID, 'mode': mode, 'wall_seconds': wall_seconds})


def check_options(mode, wall_seconds):
    if mode not in {'success', 'failure', 'cancel'} or type(wall_seconds) is not int or not 1 <= wall_seconds <= 10:
        raise JobError('Only built-in bounded synthetic fixtures are accepted')


def expected_result():
    return {'kind': 'synthetic-qualification', 'input_sha256': sha(FIXTURE),
            'values': [x*x for x in range(8)]}


class DockerExecutor:
    def _docker(self, args, timeout=3):
        env = os.environ.copy()
        for key in ('DOCKER_HOST', 'DOCKER_CONTEXT', 'DOCKER_TLS', 'DOCKER_TLS_VERIFY', 'DOCKER_CERT_PATH'):
            env.pop(key, None)
        deadline = getattr(self, '_deadline', None)
        if deadline is not None:
            timeout = min(timeout, max(.001, deadline - time.monotonic()))
        p = subprocess.run(['docker', '--host=unix:///var/run/docker.sock', *args],
                           env=env, capture_output=True, timeout=timeout)
        if p.returncode:
            raise JobError('Docker operation failed: ' + args[0])
        if len(p.stdout) > 1048576 or len(p.stderr) > 1048576:
            raise JobError('Docker response exceeds synthetic bound')
        return p.stdout

    def _save_state(self, ledger, claim, root, state):
        (root / 'run-state.json').write_bytes(encoded(state))
        ledger._save_executor_state(claim, state)

    def _inspect(self, name):
        return json.loads(self._docker(['inspect', name]))[0]

    def _processes(self, name):
        rows = self._docker(['top', name, '-eo', 'pid']).decode().splitlines()[1:]
        if not 1 <= len(rows) <= 32:
            raise JobError('Missing/excess process observation')
        result = []
        for row in rows:
            pid = int(row.strip())
            text = Path('/proc', str(pid), 'stat').read_text()
            # PID reuse identity: kernel start time after the process-name field.
            result.append({'pid': pid, 'start': text.rsplit(')', 1)[1].split()[19]})
        return result

    def _absent(self, processes):
        if not processes:
            return False
        for process in processes:
            path = Path('/proc', str(process['pid']), 'stat')
            if path.exists():
                fields = path.read_text().rsplit(')', 1)[1].split()
                if fields[19] == process['start']:
                    return False  # even a zombie prevents a positive disappearance claim
        return True

    def _check_container(self, info, identity, stage):
        h = info['HostConfig']
        mounts = info['Mounts']
        if (info['Image'] != IMAGE_ID or info['Id'] != identity['container_id'] or info['Name'] != '/' + identity['container_name']
                or info['Config']['Image'] != IMAGE or info['Config']['User'] != '65534:65534'
                or info['Config']['Cmd'] != ['python', '-I', '-u', '-c', WORKER, identity['mode'], sha(FIXTURE)]
                or info['Config'].get('Entrypoint') is not None
                or info['Config']['Labels'].get('weft.executor') != identity['container_name']
                or h['NetworkMode'] != 'none' or h['Privileged'] or not h['ReadonlyRootfs']
                or h['Memory'] != 268435456 or h['MemorySwap'] != 268435456
                or h['PidsLimit'] != 32 or h['NanoCpus'] != 1000000000
                or h['CapDrop'] != ['ALL'] or h['CapAdd']
                or 'no-new-privileges:true' not in h['SecurityOpt']
                or h['Tmpfs'] != {'/tmp': 'rw,noexec,nosuid,nodev,size=16m,mode=1777'}
                or len(mounts) != 1 or mounts[0]['Destination'] != '/inputs'
                or mounts[0]['Source'] != str(stage) or mounts[0]['RW']):
            raise JobError('Container identity/control drift')

    def _observation(self, info, identity, processes, timed_out, cancel_requested):
        s = info['State']
        if s['Status'] != 'exited' or s['Running'] or s['Pid'] != 0 or s['Error'] or not self._absent(processes):
            raise JobError('Process termination is not independently demonstrated')
        return {'container_id': identity['container_id'], 'status': s['Status'],
                'running': s['Running'], 'pid': s['Pid'], 'exit_code': s['ExitCode'],
                'oom_killed': s['OOMKilled'], 'processes_absent': True, 'timed_out': timed_out, 'cancel_requested': cancel_requested}

    def execute(self, ledger, claim, *, inputs_root, run_root, mode='success', wall_seconds=10):
        check_options(mode, wall_seconds)
        packet = ledger.status(claim['job_id'])['packet']
        records = [{'path': 'fixture.txt', 'bytes': len(FIXTURE), 'sha256': sha(FIXTURE)}]
        if packet['inputs'] != records or packet['executor_sha256'] != executor_sha256(mode, wall_seconds):
            raise JobError('Executor/code/input identity mismatch')
        verify_files(inputs_root, records)
        root = Path(run_root).absolute()
        if any(p.is_symlink() for p in [root, *root.parents]):
            raise JobError('Symlink run path rejected')
        root.mkdir(mode=0o755)  # unique, fresh; never overwrite evidence
        stage = root / 'inputs'
        stage.mkdir(mode=0o755)
        (stage / 'fixture.txt').write_bytes(FIXTURE)
        (stage / 'fixture.txt').chmod(0o444)
        verify_files(stage, records)
        stage.chmod(0o555)
        name = 'weft-synthetic-' + uuid.uuid4().hex
        identity = {'job_id': claim['job_id'], 'attempt_id': claim['attempt_id'],
                    'packet_sha256': digest(packet), 'inputs_sha256': digest(records),
                    'code_sha256': code_sha256(), 'worker_sha256': sha(WORKER.encode()),
                    'executor_sha256': packet['executor_sha256'], 'image': IMAGE, 'image_id': IMAGE_ID,
                    'container_name': name, 'mode': mode, 'wall_seconds': wall_seconds}
        ledger.bind_executor(claim, identity)
        state = {'processes': [], 'timed_out': False, 'cancel_requested': False, 'stage': str(stage)}
        self._save_state(ledger, claim, root, state)
        try:
            actual_image = self._docker(['image', 'inspect', IMAGE, '--format', '{{.Id}}']).decode().strip()
            if actual_image != IMAGE_ID:
                raise JobError('Pinned platform image ID mismatch')
            cid = self._docker(['create', '--name', name, '--pull', 'never', '--label', 'weft.executor='+name,
                '--network', 'none', '--cpus', '1', '--memory', '256m', '--memory-swap', '256m',
                '--pids-limit', '32', '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges:true',
                '--user', '65534:65534', '--read-only', '--tmpfs', '/tmp:rw,noexec,nosuid,nodev,size=16m,mode=1777',
                '--mount', 'type=bind,src='+str(stage)+',dst=/inputs,readonly',
                IMAGE, 'python', '-I', '-u', '-c', WORKER, mode, sha(FIXTURE)]).decode().strip()
            ledger._attach_container(claim, cid)
            identity = {**identity, 'container_id': cid}
            self._check_container(self._inspect(name), identity, stage)
            # Deadline covers start/observation/wait, not just the client wait call.
            deadline = time.monotonic() + wall_seconds
            self._deadline = deadline
            self._docker(['start', cid], timeout=min(3, wall_seconds))
            state['processes'] = self._processes(cid)
            self._save_state(ledger, claim, root, state)
            while True:
                if ledger.status(claim['job_id'])['state'] == 'cancel_requested':
                    state['cancel_requested'] = True
                    raise subprocess.TimeoutExpired('coordinator-cancel-request', wall_seconds)
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    raise subprocess.TimeoutExpired('external-wall-deadline', wall_seconds)
                info = self._inspect(cid)
                if not info['State']['Running']:
                    break
                try:
                    sampled = self._processes(cid)
                except (JobError, FileNotFoundError):
                    # Exit between inspect/top/proc reads is normal, but only a
                    # second terminal observation can settle it using prior PIDs.
                    if not self._inspect(cid)['State']['Running']:
                        break
                    raise
                for p in sampled:
                    if p not in state['processes']:
                        state['processes'].append(p)
                self._save_state(ledger, claim, root, state)
                time.sleep(min(.05, remaining))
        except subprocess.TimeoutExpired:
            self._deadline = None
            state['timed_out'] = not state['cancel_requested']
            self._save_state(ledger, claim, root, state)
            try:
                binding = ledger.executor_binding(claim)
                if not binding['container_id']:
                    raise JobError('Create/start outcome uncertain')
                self._docker(['kill', binding['container_id']])
                self._docker(['wait', binding['container_id']])
            except (JobError, subprocess.TimeoutExpired, OSError):
                ledger._executor_unknown(claim, 'Timeout; termination unverified')
                return {'outcome': 'held_unknown', 'run_root': str(root)}
        except (JobError, OSError, ValueError, KeyError) as exc:
            self._deadline = None
            ledger._executor_unknown(claim, type(exc).__name__ + '; Docker/process observation uncertain')
            return {'outcome': 'held_unknown', 'run_root': str(root)}
        self._deadline = None
        return self.recover(ledger, claim, run_root=root)

    def recover(self, ledger, claim, *, run_root):
        """Reobserve the bound container after expiry/restart. Never trust a report hash."""
        root = Path(run_root).absolute()
        try:
            b = ledger.executor_binding(claim)
            identity = {**b['identity'], 'container_id': b['container_id']}
            if b['terminal_sha256']:
                return {'outcome': ledger.status(claim['job_id'])['state'],
                        'terminal_sha256': b['terminal_sha256'], 'already_terminal': True}
            if (identity['code_sha256'] != code_sha256() or identity['image'] != IMAGE
                    or identity['worker_sha256'] != sha(WORKER.encode())):
                raise JobError('Recovery code/image drift')
            packet = ledger.status(claim['job_id'])['packet']
            if digest(packet) != identity['packet_sha256'] or digest(packet['inputs']) != identity['inputs_sha256']:
                raise JobError('Recovery packet/input drift')
            verify_files(root / 'inputs', packet['inputs'])
            state = decode((root / 'run-state.json').read_bytes())
            if state != b['run_state']:
                raise JobError('Process evidence drift')
            if state['stage'] != str(root / 'inputs'):
                raise JobError('Recovery stage drift')
            info = self._inspect(identity['container_id'])
            self._check_container(info, identity, root / 'inputs')
            observation = self._observation(info, identity, state['processes'], state['timed_out'], state['cancel_requested'])
            outcome = 'cancelled' if state['timed_out'] or state['cancel_requested'] else ('local_verified' if observation['exit_code'] == 0 and not observation['oom_killed'] else 'failed')
            result = None
            if outcome == 'local_verified':
                result = json.loads(self._docker(['logs', identity['container_id']]))
                if result != expected_result():
                    raise JobError('Deterministic output mismatch')
            files = make_bundle(identity, outcome, observation, result)
            terminal_hash = sha(files['terminal.json'])
            verify_bundle(files, identity=identity, terminal_sha256=terminal_hash)
            # Frozen receipts are exclusive; reconcile a preexisting identical bundle after a crash.
            bundle = root / 'bundle'
            if bundle.exists():
                existing = {p.name: p.read_bytes() for p in bundle.iterdir() if p.is_file() and not p.is_symlink()}
                if existing != files or len(list(bundle.iterdir())) != len(files):
                    raise JobError('Existing receipt drift')
            else:
                bundle.mkdir()
                for name, data in files.items():
                    (bundle / name).write_bytes(data)
            archive = root / 'synthetic-evidence.zip'
            if not archive.exists():
                write_archive(archive, files)
            else:
                from .artifacts import restore_archive
                # Verify bytes and identity without trusting the filename; fresh verification directory.
                restore_archive(archive, root / ('verify-'+uuid.uuid4().hex), identity=identity,
                                terminal_sha256=terminal_hash, archive_sha256=sha(archive.read_bytes()))
            ledger._record_executor(claim, files, terminal_hash)
            # Only a verified terminal container may be removed; unknown containers remain for recovery.
            cleanup = True
            try:
                self._docker(['rm', identity['container_id']])
            except (JobError, OSError, subprocess.TimeoutExpired):
                cleanup = False  # terminal proof remains valid; cleanup is separate
            return {'outcome': outcome, 'terminal_sha256': terminal_hash,
                    'archive_sha256': sha(archive.read_bytes()), 'archive': str(archive),
                    'identity': identity, 'cleanup': cleanup, 'external_export_verified': False}
        except (JobError, OSError, ValueError, KeyError, subprocess.TimeoutExpired, TypeError):
            # A lost container, missing process snapshot, drift, or daemon error is never a release.
            ledger._executor_unknown(claim, 'Recovery observation/content verification incomplete')
            return {'outcome': 'held_unknown', 'run_root': str(root)}
