"""Ledger-only manual checkpoints. Restore never activates or reconciles jobs."""
from contextlib import contextmanager
import datetime
import hashlib
import io
import os
from pathlib import Path
import re
import sqlite3
import stat
import tempfile
import time
import uuid
import zipfile

from .artifacts import decode, encoded, sha, write_archive
from .jobs import JobError

MAX_DB_BYTES = 32 * 1048576
MANIFEST_BYTES = 16384
RECONCILIATION = 'REQUIRES_OPERATOR_RECONCILIATION'


class CheckpointError(JobError):
    pass


def _hash(value):
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def _identity(value):
    return isinstance(value, str) and re.fullmatch('[A-Za-z0-9_.:-]{1,128}', value) is not None


def _bounds(max_bytes, max_seconds):
    if (type(max_bytes) is not int or not 4096 <= max_bytes <= MAX_DB_BYTES
            or type(max_seconds) not in (int, float) or not 0 < max_seconds <= 10):
        raise CheckpointError('Invalid checkpoint size/time bound')
    return time.monotonic() + max_seconds


def _deadline(deadline):
    if time.monotonic() >= deadline:
        raise CheckpointError('Checkpoint time bound exceeded')


def _path(path):
    path = Path(path).absolute()
    if any(p.is_symlink() for p in [path, *path.parents]):
        raise CheckpointError('Symlink checkpoint path rejected')
    return path


def _private_file(path, data):
    # Parent directory is private before the file exists; O_EXCL avoids overwrites.
    with path.open('xb') as stream:
        if os.name == 'posix':
            os.fchmod(stream.fileno(), 0o600)
        stream.write(data)
        stream.flush()
        os.fsync(stream.fileno())


@contextmanager
def _readonly(path, deadline, *, immutable=False):
    uri = _path(path).as_uri() + '?mode=ro' + ('&immutable=1' if immutable else '')
    db = sqlite3.connect(uri, uri=True, timeout=.05)
    try:
        db.execute('PRAGMA query_only=ON')
        db.execute('PRAGMA trusted_schema=OFF')
        db.set_progress_handler(lambda: int(time.monotonic() >= deadline), 1000)
        yield db
        _deadline(deadline)
    finally:
        db.close()


def schema_sha256(db):
    """Trusted handoff schema anchor: exact non-internal SQLite schema objects."""
    rows = db.execute("SELECT type,name,tbl_name,sql FROM sqlite_schema "
                      "WHERE name NOT LIKE 'sqlite_%' ORDER BY type,name").fetchall()
    if not rows or len(encoded(rows)) > MANIFEST_BYTES:
        raise CheckpointError('Missing/oversized expected ledger schema')
    return sha(encoded(rows))


def _check_db(path, deadline, expected_schema_sha256):
    with _readonly(path, deadline, immutable=True) as db:
        if db.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
            raise CheckpointError('SQLite integrity check failed')
        if schema_sha256(db) != expected_schema_sha256:
            raise CheckpointError('Expected SQLite schema mismatch')


def inspect_schema(source, *, max_seconds=5):
    """Read-only helper for operator schema selection; not an authority decision."""
    deadline = _bounds(MAX_DB_BYTES, max_seconds)
    try:
        with _readonly(source, deadline) as db:
            return schema_sha256(db)
    except sqlite3.Error as exc:
        raise CheckpointError('SQLite schema inspection failed') from exc


def _reference(reference):
    return (isinstance(reference, dict) and (
        (set(reference) == {'stage'} and _identity(reference['stage'])) or
        (set(reference) == {'job_id', 'attempt_id'} and _hash(reference['job_id'])
         and type(reference['attempt_id']) is int and reference['attempt_id'] > 0)))


def _metadata(ledger_identity, reference, phase, parent, source_revision, schema):
    if (not _identity(ledger_identity) or not _reference(reference)
            or not isinstance(phase,str) or phase not in {'before-dispatch', 'after-run'}
            or (parent is not None and not _hash(parent))
            or not isinstance(source_revision, str) or not re.fullmatch('[0-9a-f]{40}', source_revision)
            or not _hash(schema)):
        raise CheckpointError('Invalid manual checkpoint identity/reference/phase/anchors')


def create_checkpoint(source, staging, *, ledger_identity, reference, phase,
                      source_revision, expected_schema_sha256,
                      parent_checkpoint_sha256=None, max_bytes=8*1048576, max_seconds=5):
    """Bounded consistent backup API snapshot; no live-ledger SQL writes or activation."""
    deadline = _bounds(max_bytes, max_seconds)
    _metadata(ledger_identity, reference, phase, parent_checkpoint_sha256,
              source_revision, expected_schema_sha256)
    source, staging = _path(source), _path(staging)
    if not source.is_file() or not stat.S_ISREG(source.stat().st_mode):
        raise CheckpointError('Source must be an existing regular SQLite ledger')
    staging.mkdir(mode=0o700)  # fresh private staging; incomplete failures remain visible
    database = staging / 'ledger.sqlite'
    _private_file(database, b'')
    try:
        with _readonly(source, deadline) as src:
            page_size = src.execute('PRAGMA page_size').fetchone()[0]
            if src.execute('PRAGMA page_count').fetchone()[0] * page_size > max_bytes:
                raise CheckpointError('Source ledger size bound exceeded')
            dst = sqlite3.connect(database, timeout=.05)
            try:
                dst.set_progress_handler(lambda: int(time.monotonic() >= deadline), 1000)
                def progress(status, remaining, total):
                    _deadline(deadline)
                    if total * page_size > max_bytes:
                        raise CheckpointError('Backup expansion bound exceeded')
                src.backup(dst, pages=16, progress=progress, sleep=.01)
                # Portable standalone snapshot: no WAL/SHM/journal members are exported.
                dst.execute('PRAGMA journal_mode=DELETE')
            finally:
                dst.close()
        if set(p.name for p in staging.iterdir()) != {'ledger.sqlite'}:
            raise CheckpointError('Backup left unexpected SQLite sidecars')
        _check_db(database, deadline, expected_schema_sha256)
        if not 0 < database.stat().st_size <= max_bytes:
            raise CheckpointError('Backup file size bound exceeded')
        data = database.read_bytes()
        manifest = {'schema_version': 1, 'ledger_identity': ledger_identity,
                    'checkpoint_id': uuid.uuid4().hex, 'reference': reference, 'phase': phase,
                    'parent_checkpoint_sha256': parent_checkpoint_sha256,
                    'source_revision': source_revision,
                    'timestamp_utc': datetime.datetime.now(datetime.timezone.utc).isoformat().replace('+00:00','Z'),
                    'sqlite_schema_sha256': expected_schema_sha256,
                    'files': [{'path':'ledger.sqlite','bytes':len(data),'sha256':sha(data)}]}
        manifest_data = encoded(manifest)
        if len(manifest_data) > MANIFEST_BYTES:
            raise CheckpointError('Checkpoint manifest size bound exceeded')
        _private_file(staging / 'checkpoint-manifest.json', manifest_data)
        archive = staging / 'checkpoint.zip'
        write_archive(archive, {'ledger.sqlite':data,'checkpoint-manifest.json':manifest_data})
        if os.name == 'posix': archive.chmod(0o600)
        _deadline(deadline)
        return {'status':'LOCAL_CHECKPOINT_VERIFIED','archive':str(archive),
                'archive_sha256':sha(archive.read_bytes()),'manifest':manifest,
                'upload_verified':False,'retention_qualified':False}
    except sqlite3.Error as exc:
        raise CheckpointError('SQLite backup/integrity operation failed or timed out') from exc


def restore_checkpoint(archive, destination, *, expected_archive_sha256, ledger_identity,
                       expected_schema_sha256, max_bytes=8*1048576, max_seconds=5):
    """Verify the trusted handoff anchors; restore privately and require reconciliation."""
    deadline = _bounds(max_bytes, max_seconds)
    if not _hash(expected_archive_sha256) or not _identity(ledger_identity) or not _hash(expected_schema_sha256):
        raise CheckpointError('Trusted manual archive/ledger/schema anchors are required')
    archive, destination = _path(archive), _path(destination)
    if destination.exists():
        raise FileExistsError('Checkpoint destination must be fresh')
    if not archive.is_file() or archive.stat().st_size > max_bytes + MANIFEST_BYTES + 4096:
        raise CheckpointError('Checkpoint archive size bound exceeded')
    raw = archive.read_bytes()
    if sha(raw) != expected_archive_sha256:
        raise CheckpointError('Trusted checkpoint archive hash mismatch')
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            entries = z.infolist()
            if len(entries) != 2 or {i.filename for i in entries} != {'ledger.sqlite','checkpoint-manifest.json'}:
                raise CheckpointError('Duplicate/missing/unexpected checkpoint members')
            for i in entries:
                mode = i.external_attr >> 16
                cap = max_bytes if i.filename == 'ledger.sqlite' else MANIFEST_BYTES
                if (i.is_dir() or stat.S_IFMT(mode) not in {0,stat.S_IFREG}
                        or i.flag_bits & 1 or not 0 < i.file_size <= cap
                        or i.compress_type not in {zipfile.ZIP_STORED,zipfile.ZIP_DEFLATED}):
                    raise CheckpointError('Unsafe/encrypted/oversized checkpoint member')
            files = {i.filename:z.read(i) for i in entries}  # full CRC check before destination writes
        _deadline(deadline)
        manifest = decode(files['checkpoint-manifest.json'])
        required = {'schema_version','ledger_identity','checkpoint_id','reference','phase',
                    'parent_checkpoint_sha256','source_revision','timestamp_utc','sqlite_schema_sha256','files'}
        if not isinstance(manifest, dict) or set(manifest) != required or type(manifest['schema_version']) is not int or manifest['schema_version'] != 1:
            raise CheckpointError('Invalid checkpoint manifest schema')
        _metadata(manifest['ledger_identity'],manifest['reference'],manifest['phase'],
                  manifest['parent_checkpoint_sha256'],manifest['source_revision'],manifest['sqlite_schema_sha256'])
        if (manifest['ledger_identity'] != ledger_identity
                or manifest['sqlite_schema_sha256'] != expected_schema_sha256
                or not isinstance(manifest['checkpoint_id'],str) or not re.fullmatch('[0-9a-f]{32}',manifest['checkpoint_id'])
                or not isinstance(manifest['timestamp_utc'],str) or not manifest['timestamp_utc'].endswith('Z')
                or datetime.datetime.fromisoformat(manifest['timestamp_utc']).utcoffset() != datetime.timedelta(0)):
            raise CheckpointError('Checkpoint identity/schema/timestamp drift')
        data = files['ledger.sqlite']
        expected_files = [{'path':'ledger.sqlite','bytes':len(data),'sha256':sha(data)}]
        if encoded(manifest['files']) != encoded(expected_files):
            raise CheckpointError('Checkpoint SQLite bytes/hash drift')
        # Validate SQLite corruption/schema in private scratch BEFORE creating the destination.
        with tempfile.TemporaryDirectory(prefix='weft-checkpoint-verify-') as scratch:
            test_database = Path(scratch) / 'ledger.sqlite'
            _private_file(test_database, data)
            _check_db(test_database, deadline, expected_schema_sha256)
        destination.mkdir(mode=0o700)
        _private_file(destination / 'ledger.sqlite', data)
        _private_file(destination / 'checkpoint-manifest.json', files['checkpoint-manifest.json'])
        _check_db(destination / 'ledger.sqlite', deadline, expected_schema_sha256)
        return {'status':RECONCILIATION,'directory':str(destination),
                'archive_sha256':expected_archive_sha256,'manifest':manifest,
                'database_opened_read_only':True,'activation_permitted':False,
                'upload_verified':False,'retention_qualified':False}
    except (sqlite3.Error, zipfile.BadZipFile, RuntimeError, ValueError, TypeError, KeyError) as exc:
        raise CheckpointError('Checkpoint corruption/schema/format verification failed') from exc
