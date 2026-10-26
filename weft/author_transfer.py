"""Bounded, inert local transport for a future isolated worker.

Call only on trusted, quiescent directories. This is not a filesystem sandbox or
proof that a worker has stopped. No extraction, imports, subprocesses or network.
Incomplete destinations are preserved; they never become verified deliveries.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path, PurePosixPath
import stat

from . import evidence as ev, author_worker as worker

VERSION = 'weft-author-transfer-v1'
CHUNK = 1024 * 1024


def budget(value):
    ev.keys(value, {'max_files', 'max_entries', 'max_file_bytes', 'max_total_bytes'})
    for key, limit in value.items():
        if type(limit) is not int or not 1 <= limit <= 2**63 - 1:
            raise ValueError('Positive bounded transfer limits required')
    if value['max_files'] > 10000 or value['max_entries'] > 100000:
        raise ValueError('Transfer inventory exceeds record bounds')
    if value['max_files'] > value['max_entries']:
        raise ValueError('Entries must cover files')
    return value


def inventory(files, limits):
    budget(limits)
    if not isinstance(files, list) or len(files) > limits['max_files']:
        raise ValueError('File count bound exceeded')
    names, total = [], 0
    for item in files:
        ev.keys(item, {'path', 'sha256', 'bytes'})
        ev.relative(item['path']); ev.sha(item['sha256'])
        if type(item['bytes']) is not int or not 0 <= item['bytes'] <= limits['max_file_bytes']:
            raise ValueError('File byte bound exceeded')
        name = PurePosixPath(item['path'].casefold())
        if any(name == p or name.is_relative_to(p) or p.is_relative_to(name) for p in names):
            raise ValueError('File destination collision')
        names.append(name); total += item['bytes']
    if total > limits['max_total_bytes']:
        raise ValueError('Total byte bound exceeded')
    return files


def _signature(s):
    # Windows Python 3.12 path/descriptor ctime can report different creation vs
    # change timestamps. Identity, size, mtime and exact bytes remain mandatory.
    return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_nlink,
            s.st_ctime_ns if os.name != 'nt' else None)


def _stream(path, expected, destination=None):
    """Hash exactly the copied bytes with bounded reads and identity rechecks."""
    path = ev.unlinked(path)
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1 or before.st_size != expected['bytes']:
        raise ValueError('Expected unlinked regular file/size required')
    flags = (os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_NONBLOCK', 0)
             | getattr(os, 'O_BINARY', 0))
    descriptor = os.open(path, flags)
    with os.fdopen(descriptor, 'rb') as source:
        if _signature(os.fstat(source.fileno())) != _signature(before):
            raise ValueError('File replaced before transfer')
        digest, count = hashlib.sha256(), 0
        while True:
            data = source.read(min(CHUNK, expected['bytes'] - count + 1))
            if not data: break
            count += len(data)
            if count > expected['bytes']: raise ValueError('File grew during transfer')
            digest.update(data)
            if destination is not None: destination.write(data)
        if (_signature(os.fstat(source.fileno())) != _signature(before)
                or _signature(ev.unlinked(path).lstat()) != _signature(before)):
            raise ValueError('File changed during transfer')
    if count != expected['bytes'] or digest.hexdigest() != expected['sha256']:
        raise ValueError('Transferred bytes/hash mismatch')


def _copy(source, root, item):
    target = ev.contained(root, item['path'])
    if target.exists():
        # A complete previous copy is resumable, a partial copy is retained/held.
        _stream(target, item)
        _stream(source, item)
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    ev.unlinked(target.parent)
    with target.open('xb') as out:
        _stream(source, item, out)
        out.flush(); os.fsync(out.fileno())


def exact_tree(root, files, limits, *, metadata=()):
    """Reject extras, empty extraneous directories, aliases and special files."""
    inventory(files, limits)
    root = ev.unlinked(root).resolve(strict=True)
    expected = {item['path'] for item in files} | set(metadata)
    directories = {str(p) for name in expected for p in PurePosixPath(name).parents if str(p) != '.'}
    pending, seen, count = [root], set(), 0
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                count += 1
                if count > limits['max_entries']: raise ValueError('Directory entry bound exceeded')
                path = ev.unlinked(Path(entry.path))
                name = path.relative_to(root).as_posix()
                ev.relative(name)
                s = path.lstat()
                if stat.S_ISDIR(s.st_mode):
                    if name not in directories: raise ValueError('Unexpected directory')
                    pending.append(path)
                elif stat.S_ISREG(s.st_mode) and s.st_nlink == 1:
                    if name not in expected: raise ValueError('Unexpected file')
                    seen.add(name)
                else:
                    raise ValueError('Linked or special transfer entry')
    if seen != expected: raise ValueError('Incomplete transfer tree')


def _separate(workspace, destination):
    root = ev.unlinked(destination).absolute()
    for old in (workspace.root, Path(workspace.binding['inputs']), Path(workspace.binding['sources']),
                *(Path(p) for p in workspace.binding['protected_roots'])):
        if root.is_relative_to(old) or old.is_relative_to(root):
            raise ValueError('Transfer destination must be separate from registered roots')
    root.mkdir(parents=True, exist_ok=True)
    return root


def stage(workspace, preparation_ref, destination, limits):
    """Copy frozen code/data as inert bytes. This does not mount or execute them."""
    prepared = worker.load_preparation(workspace, preparation_ref)
    items = [item for group in prepared['staging'].values() for item in group]
    files = [{'path': item['destination'].lstrip('/'), 'sha256': item['file']['sha256'],
              'bytes': item['file']['bytes']} for item in items]
    inventory(files, limits)
    if sum(x['bytes'] for x in files) > prepared['limits']['disk_bytes']:
        raise ValueError('Staging exceeds frozen disk budget')
    root = _separate(workspace, destination)
    for original, item in zip(items, files):
        _copy(workspace.file(original['file']), root, item)
    exact_tree(root, files, limits)
    return {'schema_version': VERSION, 'kind': 'staged-inert-bytes', 'preparation': preparation_ref,
            'files': files, 'limits': limits, 'readonly_mount_verified': False,
            'runtime_qualified': False, **ev.FLAGS}


def collect(workspace, preparation_ref, identity, directory, destination, files, limits):
    """Quarantine an allowlisted supplied inventory, without terminal admission."""
    prepared = worker.load_preparation(workspace, preparation_ref)
    ev.keys(identity, {'job_id', 'attempt_id', 'container_id'})
    ev.sha(identity['job_id']); ev.sha(identity['container_id'])
    if type(identity['attempt_id']) is not int or not 1 <= identity['attempt_id'] <= 2**63 - 1:
        raise ValueError('Invalid attempt ID')
    inventory(files, limits)
    allowed = {item['path'] for item in prepared['outputs']}
    if not {x['path'] for x in files} <= allowed:
        raise ValueError('Output outside frozen contract')
    if limits['max_total_bytes'] > prepared['request']['output_bytes']:
        raise ValueError('Collector exceeds proposed output quota')
    source = ev.unlinked(directory).resolve(strict=True)
    root = _separate(workspace, destination)
    if root.is_relative_to(source) or source.is_relative_to(root):
        raise ValueError('Return source and destination overlap')
    exact_tree(source, files, limits)
    obj = {'schema_version': VERSION, 'kind': 'quarantined-author-return',
           'preparation': preparation_ref, 'identity': identity, 'files': files, 'limits': limits,
           'missing_outputs': sorted(allowed - {x['path'] for x in files}),
           'termination_verified': False, 'identity_authenticated': False, **ev.FLAGS}
    raw = ev.encoded(obj)
    if len(raw) > ev.MAX_RECORD: raise ValueError('Transfer manifest too large')
    for item in files: _copy(ev.contained(source, item['path']), root, item)
    manifest = root / 'transfer.json'
    if manifest.exists():
        if ev.read_raw(manifest) != raw: raise ValueError('Return manifest cannot be replaced')
    else: ev.write_new(manifest, raw)
    verify(root, hashlib.sha256(raw).hexdigest())
    return ev.reference(root, 'transfer.json')


def verify(directory, expected_sha256):
    """Independent exact-byte restore check; hashes do not authenticate a worker."""
    ev.sha(expected_sha256)
    root = ev.unlinked(directory).resolve(strict=True)
    raw = ev.read_raw(root / 'transfer.json')
    if hashlib.sha256(raw).hexdigest() != expected_sha256: raise ValueError('Manifest hash mismatch')
    obj = ev.decode(raw)
    ev.keys(obj, {'schema_version', 'kind', 'preparation', 'identity', 'files', 'limits',
                  'missing_outputs', 'termination_verified', 'identity_authenticated', *ev.FLAGS})
    if (obj['schema_version'] != VERSION or obj['kind'] != 'quarantined-author-return'
            or any(obj[k] is not False for k in (*ev.FLAGS, 'termination_verified', 'identity_authenticated'))):
        raise ValueError('Transfer cannot establish live authority')
    exact_tree(root, obj['files'], obj['limits'], metadata=('transfer.json',))
    for item in obj['files']: _stream(ev.contained(root, item['path']), item)
    return obj
