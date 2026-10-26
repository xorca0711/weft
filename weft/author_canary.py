"""Trusted bounded canary payload for a separately authorized isolated campaign.

Default invocation prints a plan. --execute is for the qualified disposable
worker only. Allocation, write and spawn counts are capped. Wall time requires
the external watchdog, including stalled I/O. Payload output is never trusted
enforcement evidence.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time

MODES = ('success', 'failure', 'sleep', 'descendants', 'memory', 'pids', 'output', 'inodes')
CAMPAIGN = ('success', 'failure', 'timeout', 'cancellation', 'coordinator-loss',
            'memory-limit', 'pid-limit', 'output-byte-limit', 'output-inode-limit',
            'stale-identity', 'restart-recovery', 'independent-restore')


def plan(mode):
    if mode not in MODES: raise ValueError('Unknown canary')
    return {'kind': 'trusted-author-canary', 'mode': mode, 'watchdog_seconds': 20,
            'max_allocated_bytes': 64 * 1024 * 1024, 'max_children': 8,
            'max_written_bytes': 8 * 1024 * 1024, 'max_created_files': 256,
            'runtime_qualified': False, 'dispatch_authorized': False,
            'required_external_evidence': ['runtime-policy-and-identity', 'isolated-mounts',
                'kernel-byte-and-inode-quota', 'watchdog-before-start', 'outside-cgroup-termination',
                'private-receipt-and-restore']}


def execute(mode, output):
    spec = plan(mode)
    started = time.monotonic()
    children, memory = [], []
    count, error = 0, None
    try:
        if mode in {'success', 'output', 'inodes'}:
            root = Path(output)
            if root.is_symlink() or not root.is_dir(): raise ValueError('Existing canary output directory required')
            if mode == 'success':
                with (root/'canary.json').open('x') as stream: stream.write('{"trusted_fixture":true}\n')
                count = 1
            elif mode == 'output':
                with (root/'bounded-bytes.bin').open('xb') as stream:
                    for _ in range(spec['max_written_bytes'] // 65536):
                        stream.write(b'x' * 65536); stream.flush(); os.fsync(stream.fileno())
                        count += 65536
            else:
                for i in range(spec['max_created_files']):
                    with (root/f'inode-{i:03d}').open('xb'): pass
                    count += 1
        elif mode == 'memory':
            for _ in range(spec['max_allocated_bytes'] // (1024 * 1024)):
                memory.append(bytearray(b'x' * (1024 * 1024)))
                count += 1024 * 1024
            time.sleep(1)
        elif mode in {'pids', 'descendants'}:
            for _ in range(spec['max_children'] if mode == 'pids' else 1):
                children.append(subprocess.Popen([sys.executable, '-I', '-c', 'import time; time.sleep(20)'],
                    stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    close_fds=True))
                count += 1
            time.sleep(15 if mode == 'descendants' else 1)
        elif mode == 'sleep': time.sleep(15)
    except (OSError, MemoryError) as exc:
        # No paths, environment values or arbitrary exception text in probe output.
        error = {'type': type(exc).__name__, 'errno': getattr(exc, 'errno', None)}
    finally:
        for child in children:
            if child.poll() is None: child.kill()
        for child in children: child.wait(timeout=2)
    return {'mode': mode, 'operations': count, 'error': error,
            'elapsed_seconds': time.monotonic() - started,
            'payload_completed': True, 'enforcement_verified': False,
            'runtime_qualified': False, 'dispatch_authorized': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=MODES)
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--output', default='/outputs')
    args = parser.parse_args(argv)
    result = execute(args.mode, args.output) if args.execute else plan(args.mode)
    print(json.dumps(result, sort_keys=True))
    return 17 if args.execute and args.mode == 'failure' else 0


if __name__ == '__main__': raise SystemExit(main())
