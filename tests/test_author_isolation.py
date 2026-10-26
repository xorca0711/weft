import contextlib
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from weft.author_isolation import VERSION, audit, main


class AuthorIsolationTests(unittest.TestCase):
    def setUp(self):
        self.plan = {'schema_version': VERSION, 'container_id': 'a'*64, 'container_name': 'weft-author-fixture',
            'image': 'python@sha256:' + 'b'*64, 'image_id': 'sha256:' + 'c'*64,
            'argv': ['python', '-I', '/code/main.py'], 'environment': ['HOME=/tmp', 'PATH=/usr/local/bin:/usr/bin:/bin'],
            'mounts': {'/code': '/stage/code', '/inputs': '/stage/inputs', '/outputs': '/stage/outputs'},
            'memory_bytes': 268435456, 'pids': 32, 'nano_cpus': 1000000000, 'tmpfs_bytes': 16777216}
        self.info = {'Id': self.plan['container_id'], 'Name': '/' + self.plan['container_name'], 'Image': self.plan['image_id'],
            'Config': {'Image': self.plan['image'], 'Cmd': self.plan['argv'], 'Entrypoint': None,
                       'User': '65534:65534', 'Labels': {'weft.author': self.plan['container_name']}, 'Env': self.plan['environment']},
            'HostConfig': {'NetworkMode': 'none', 'Privileged': False, 'ReadonlyRootfs': True,
                'CapDrop': ['ALL'], 'CapAdd': None, 'SecurityOpt': ['no-new-privileges:true'],
                'PidMode': '', 'IpcMode': 'private', 'UTSMode': '', 'CgroupnsMode': 'private',
                'Devices': [], 'DeviceRequests': None, 'VolumesFrom': None, 'Links': None,
                'RestartPolicy': {'Name': 'no', 'MaximumRetryCount': 0},
                'Memory': 268435456, 'MemorySwap': 268435456, 'PidsLimit': 32, 'NanoCpus': 1000000000,
                'Tmpfs': {'/tmp': 'rw,noexec,nosuid,nodev,size=16777216,mode=1777'}},
            'Mounts': [{'Source': source, 'Destination': target, 'Type': 'bind', 'Propagation': 'rprivate', 'RW': target == '/outputs'}
                       for target, source in self.plan['mounts'].items()]}
        self.probe = {'uid': 65534, 'gid': 65534, 'interfaces': ['lo'], 'cap_eff': '0000000000000000',
            'no_new_privileges': True, 'seccomp_mode': 2, 'memory_max': 268435456, 'swap_max': 0,
            'pids_max': 32, 'cpu_max': [100000, 100000],
            **{k: True for k in ('code_write_denied', 'input_write_denied', 'root_write_denied',
                                 'output_write_succeeded', 'host_socket_absent', 'host_canary_absent')}}

    def test_consistency_never_qualifies_or_executes(self):
        with patch('subprocess.run', side_effect=AssertionError('No launch')):
            result = audit(self.plan, self.info, self.probe)
        self.assertEqual(result['status'], 'supplied-controls-consistent')
        for key in ('runtime_qualified', 'dispatch_authorized', 'canonical_acceptance', 'observations_authenticated'):
            self.assertFalse(result[key])
        self.assertEqual(len(result['remaining_live_evidence']), 6)

    def test_host_control_drift_holds(self):
        drift = {'NetworkMode': 'host', 'Privileged': True, 'ReadonlyRootfs': False, 'CapDrop': [],
                 'CapAdd': ['SYS_ADMIN'], 'SecurityOpt': ['seccomp=unconfined'], 'PidMode': 'host',
                 'IpcMode': 'host', 'UTSMode': 'host', 'CgroupnsMode': 'host', 'Devices': ['/dev/sda'],
                 'DeviceRequests': ['gpu'], 'VolumesFrom': ['other'], 'Links': ['other'],
                 'RestartPolicy': {'Name': 'always', 'MaximumRetryCount': 0}, 'Memory': 0,
                 'MemorySwap': -1, 'PidsLimit': -1, 'NanoCpus': 0, 'Tmpfs': {}}
        for key, value in drift.items():
            with self.subTest(key=key):
                info = copy.deepcopy(self.info); info['HostConfig'][key] = value
                self.assertEqual(audit(self.plan, info, self.probe)['status'], 'hold')

    def test_credentials_and_proxy_inheritance_rejected_without_echo(self):
        for name in ('OPENAI_API_KEY', 'HTTPS_PROXY', 'DOCKER_HOST', 'AWS_SECRET_ACCESS_KEY'):
            info = copy.deepcopy(self.info); info['Config']['Env'].append(name + '=DO-NOT-ECHO')
            result = audit(self.plan, info, self.probe)
            self.assertIn('environment-allowlist', result['issues'])
            self.assertNotIn('DO-NOT-ECHO', json.dumps(result))
        planned = copy.deepcopy(self.plan); planned['environment'].append('OPENAI_API_KEY=value')
        with self.assertRaises(ValueError): audit(planned, self.info, self.probe)

    def test_socket_mount_extra_mount_and_writable_inputs_rejected(self):
        variants = []
        info = copy.deepcopy(self.info); info['Mounts'].append({'Destination': '/var/run/docker.sock'}); variants.append(info)
        info = copy.deepcopy(self.info); info['Mounts'][0]['RW'] = True; variants.append(info)
        info = copy.deepcopy(self.info); info['Mounts'][1]['Source'] = '/private/research'; variants.append(info)
        info = copy.deepcopy(self.info); info['Mounts'][2]['Propagation'] = 'shared'; variants.append(info)
        info = copy.deepcopy(self.info); info['Mounts'].append(copy.deepcopy(info['Mounts'][0])); variants.append(info)
        for info in variants: self.assertEqual(audit(self.plan, info, self.probe)['status'], 'hold')

    def test_probe_absence_or_failure_holds(self):
        for key in self.probe:
            probe = copy.deepcopy(self.probe); del probe[key]
            with self.subTest(key=key): self.assertEqual(audit(self.plan, self.info, probe)['status'], 'hold')

    def test_code_image_and_attempt_bindings_required(self):
        for key in ('Id', 'Name', 'Image'):
            info = copy.deepcopy(self.info); info[key] = 'changed'
            self.assertEqual(audit(self.plan, info, self.probe)['status'], 'hold')
        for key in ('Cmd', 'Entrypoint', 'Image', 'User', 'Labels'):
            info = copy.deepcopy(self.info); info['Config'][key] = 'changed' if key != 'Labels' else {}
            self.assertEqual(audit(self.plan, info, self.probe)['status'], 'hold')

    def test_supplied_plan_rejects_paths_and_unbounded_resources(self):
        for target in ('/', '/stage', '/stage/code', '/stage/../escape'):
            planned = copy.deepcopy(self.plan); planned['mounts']['/outputs'] = target
            with self.assertRaises(ValueError): audit(planned, self.info, self.probe)
        for value in (0, -1, True, float('inf')):
            planned = copy.deepcopy(self.plan); planned['memory_bytes'] = value
            with self.assertRaises(ValueError): audit(planned, self.info, self.probe)

    def test_cli_hash_binding_and_no_sensitive_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = {}
            for key, data in (('plan', self.plan), ('inspect', self.info), ('probe', self.probe)):
                paths[key] = Path(tmp)/f'{key}.json'; paths[key].write_text(json.dumps(data))
            args = [v for key, path in paths.items() for v in ('--'+key, str(path))]
            expected = hashlib.sha256(paths['plan'].read_bytes()).hexdigest()
            with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(main(args + ['--expected-plan-sha256', expected]), 0)
            with contextlib.redirect_stdout(io.StringIO()): self.assertEqual(main(args + ['--expected-plan-sha256', '0'*64]), 1)

    def test_no_observations_holds(self):
        self.assertEqual(audit(self.plan, {}, {})['status'], 'hold')

    def test_image_healthcheck_cannot_bypass_frozen_command(self):
        for value in ({'Test': ['CMD-SHELL', 'unreviewed-command']}, {}, 'malformed'):
            info = copy.deepcopy(self.info); info['Config']['Healthcheck'] = value
            self.assertIn('unreviewed-healthcheck', audit(self.plan, info, self.probe)['issues'])
        info = copy.deepcopy(self.info); info['Config']['Healthcheck'] = {'Test': ['NONE']}
        self.assertEqual(audit(self.plan, info, self.probe)['status'], 'supplied-controls-consistent')

    def test_malformed_observations_cannot_report_consistency(self):
        for key, value in (('Env', [None]), ('Labels', 'untrusted')):
            info = copy.deepcopy(self.info); info['Config'][key] = value
            self.assertEqual(audit(self.plan, info, self.probe)['status'], 'hold')
        info = copy.deepcopy(self.info); info['HostConfig']['SecurityOpt'] = [None]
        self.assertEqual(audit(self.plan, info, self.probe)['status'], 'hold')
        with self.assertRaises(ValueError): audit(self.plan, {'Config': 'untrusted'}, self.probe)


if __name__ == '__main__': unittest.main()
