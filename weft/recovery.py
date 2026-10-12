"""Private prelaunch recovery material; never an ordinary artifact or public receipt.

Only previously ledger-bound source is loaded. No token appears in CLI arguments,
stdout, terminal manifests or ZIP outputs. POSIX ownership/modes are mandatory.
"""
import importlib
import importlib.util
import os
from pathlib import Path
import secrets
import sqlite3
import stat
import sys

from .artifacts import decode, encoded, sha
from .identity import digest
from .jobs import JobError

SOURCE_FILES = ('__init__.py', 'executor.py', 'artifacts.py', 'jobs.py',
                'identity.py', 'validation.py', 'recovery.py')
CAPSULE_NAME = '.weft-recovery'
MAX_FILE = 1048576


def _no_symlinks(path):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in [path, *path.parents]):
        raise JobError('Symlink recovery path rejected')
    return path


def _private(path, directory=False):
    s = path.lstat()
    expected = 0o700 if directory else 0o600
    kind = stat.S_ISDIR if directory else stat.S_ISREG
    if (not kind(s.st_mode) or stat.S_IMODE(s.st_mode) != expected
            or s.st_uid != os.getuid() or (not directory and s.st_nlink != 1)):
        raise JobError('Recovery ownership/type/permissions invalid')


def _read(path):
    _private(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        with os.fdopen(fd, 'rb') as stream:
            data = stream.read(MAX_FILE + 1)
        if len(data) > MAX_FILE:
            raise JobError('Recovery file bound exceeded')
        return data
    except BaseException:
        # fdopen owns the descriptor once constructed.
        raise


def _write(path, data):
    if len(data) > MAX_FILE:
        raise JobError('Recovery file bound exceeded')
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())
    _private(path)


def _sync_dir(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def write_capsule(ledger, claim, identity, run_root):
    """Exclusive, fsynced commit marker; failure must precede every Docker call."""
    if os.name != 'posix':
        raise JobError('Private recovery requires POSIX permissions')
    ledger._attempt(claim)  # authenticate before persisting the bearer lease
    root = _no_symlinks(run_root)
    capsule = root / CAPSULE_NAME
    capsule.mkdir(mode=0o700)
    (capsule / 'source').mkdir(mode=0o700)
    package = capsule / 'source' / 'weft'
    package.mkdir(mode=0o700)
    claim_bytes = encoded(claim)
    _write(capsule / 'claim.json', claim_bytes)
    source_root = Path(__file__).parent
    hashes = {}
    for name in SOURCE_FILES:
        original = source_root / name
        if original.is_symlink() or not original.is_file():
            raise JobError('Unsafe/missing adapter dependency')
        data = original.read_bytes()
        hashes[name] = sha(data)
        _write(package / name, data)
    if digest(hashes) != identity['code_sha256']:
        raise JobError('Source changed during capsule persistence')
    manifest = {'schema_version': 1, 'claim_sha256': sha(claim_bytes),
                'ledger_path': str(_no_symlinks(ledger.path)),
                'run_root': str(root), 'identity': identity, 'sources': hashes}
    manifest_bytes = encoded(manifest)
    _sync_dir(package)
    _sync_dir(capsule / 'source')
    _write(capsule / 'manifest.json', manifest_bytes)  # last: completeness marker
    _sync_dir(capsule)
    _sync_dir(root)
    ledger._attach_capsule(claim, sha(manifest_bytes))
    # Verify persisted bytes, restrictions and ledger anchor before launch.
    load_capsule(root, expected_claim=claim, expected_ledger=ledger.path)


def load_capsule(run_root, *, expected_claim=None, expected_ledger=None):
    """Authenticate hashes against the SAME ledger before loading any saved code."""
    if os.name != 'posix':
        raise JobError('Private recovery requires POSIX permissions')
    root = _no_symlinks(run_root)
    capsule = root / CAPSULE_NAME
    package = capsule / 'source' / 'weft'
    try:
        for p in (capsule, capsule / 'source', package):
            _private(p, directory=True)
        wanted = {'claim.json', 'manifest.json', 'source', 'source/weft',
                  *('source/weft/' + name for name in SOURCE_FILES)}
        if {p.relative_to(capsule).as_posix() for p in capsule.rglob('*')} != wanted:
            raise JobError('Incomplete/unexpected recovery capsule members')
        manifest_bytes = _read(capsule / 'manifest.json')
        m = decode(manifest_bytes)
        if (set(m) != {'schema_version', 'claim_sha256', 'ledger_path', 'run_root', 'identity', 'sources'}
                or type(m['schema_version']) is not int or m['schema_version'] != 1
                or m['run_root'] != str(root) or set(m['sources']) != set(SOURCE_FILES)):
            raise JobError('Recovery manifest schema/path drift')
        claim_bytes = _read(capsule / 'claim.json')
        if sha(claim_bytes) != m['claim_sha256']:
            raise JobError('Recovery claim content drift')
        claim = decode(claim_bytes)
        if (set(claim) != {'job_id', 'attempt_id', 'lease_token', 'expires'}
                or type(claim['attempt_id']) is not int or claim['attempt_id'] < 1
                or not isinstance(claim['lease_token'], str)):
            raise JobError('Invalid persisted claim')
        if expected_claim is not None and encoded(claim) != encoded(expected_claim):
            raise JobError('Persisted claim differs from authenticated caller')
        ledger_path = _no_symlinks(m['ledger_path'])
        if expected_ledger is not None and ledger_path != _no_symlinks(expected_ledger):
            raise JobError('Recovery ledger path drift')
        # Read-only lookup: do not create/migrate/modify a ledger named by unverified material.
        with sqlite3.connect(ledger_path.as_uri() + '?mode=ro', uri=True) as db:
            db.row_factory = sqlite3.Row
            row = db.execute('SELECT a.job_id,a.token_hash,a.expires,b.identity,b.capsule_sha256 '
                             'FROM attempts a JOIN executor_bindings b ON b.attempt_id=a.id '
                             'WHERE a.id=?', (claim['attempt_id'],)).fetchone()
            if (row is None or row['job_id'] != claim['job_id'] or row['expires'] != claim['expires']
                    or not secrets.compare_digest(row['token_hash'], digest(claim['lease_token']))
                    or row['capsule_sha256'] != sha(manifest_bytes)
                    or encoded(__import__('json').loads(row['identity'])) != encoded(m['identity'])):
                raise JobError('Recovery ledger/claim/identity authentication failed')
        hashes = {name: sha(_read(package / name)) for name in SOURCE_FILES}
        if hashes != m['sources'] or digest(hashes) != m['identity']['code_sha256']:
            raise JobError('Recovery source content drift')
        return claim, m, capsule / 'source'
    except (OSError, ValueError, TypeError, KeyError, sqlite3.Error) as exc:
        raise JobError('Recovery capsule missing/tampered/incomplete') from exc


def recover_from_capsule(run_root):
    """A restarted process imports only content-verified, self-contained saved code."""
    claim, m, source = load_capsule(run_root)
    name = '_weft_recovery_' + m['identity']['code_sha256']
    spec = importlib.util.spec_from_file_location(name, source / 'weft' / '__init__.py',
        submodule_search_locations=[str(source / 'weft')])
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        sys.modules[name] = module
        spec.loader.exec_module(module)
        jobs = importlib.import_module(name + '.jobs')
        executor = importlib.import_module(name + '.executor')
        with jobs.JobLedger(m['ledger_path']) as ledger:
            return executor.DockerExecutor().recover(ledger, claim, run_root=run_root)
    finally:
        sys.dont_write_bytecode = previous


if __name__ == '__main__':
    import json
    try:
        result = recover_from_capsule(sys.argv[1])
    except (JobError, OSError, IndexError):
        result = {'outcome': 'held_unknown', 'reason': 'Recovery capsule verification failed'}
    print(json.dumps(result, sort_keys=True))  # never print the claim or manifest
    sys.exit(0 if result['outcome'] in {'local_verified', 'failed', 'cancelled'} else 1)
