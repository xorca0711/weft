"""Portable reading references and explicit reconciliation of legacy absolute paths."""
import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re

from .batches import event, exclusive, specification
from .identity import digest

SCOPE = 'discovery-store-relative-v1'
READING_NAME = re.compile(r'reading-[0-9a-f]{32}')


def store_directory(store, relative):
    """Only an immediate generated reading directory can be referenced."""
    if not isinstance(relative, str) or not READING_NAME.fullmatch(relative):
        raise ValueError('Expected one store-relative reading directory name')
    root = store.root.resolve()
    directory = root / relative
    if directory.is_symlink() or getattr(directory, 'is_junction', lambda: False)():
        raise ValueError('Linked reading directory rejected')
    resolved = directory.resolve(strict=True)
    if resolved.parent != root or not resolved.is_dir():
        raise ValueError('Reading directory outside the store')
    return resolved


def resolve_directory(store, read):
    if read.get('directory_scope') == SCOPE:
        return store_directory(store, read['directory'])
    if 'directory_scope' in read:
        raise ValueError('Unknown reading directory scope')
    # Legacy receipts remain usable in the original store. Never interpret a
    # foreign absolute path as relative or guess its basename after a move.
    raw = read.get('directory')
    if not isinstance(raw, str) or not Path(raw).is_absolute():
        raise ValueError('Legacy reading path needs explicit batch-relocate-reading')
    path = Path(raw)
    if path.parent != store.root or '..' in path.parts:
        raise ValueError('Legacy reading path outside current store; use batch-relocate-reading')
    return store_directory(store, path.name)


def check_files(store, read):
    directory = resolve_directory(store, read)
    for name in ['reading-receipt.json'] + (['packet.json', 'source.xml'] if read['status'] == 'prepared' else []):
        path = directory / name
        if path.is_symlink() or not path.is_file() or path.resolve().parent != directory:
            raise ValueError('Missing or linked reading evidence file')
    receipt = json.loads((directory / 'reading-receipt.json').read_text(encoding='utf-8'))
    # The wrapper may add interface/path fields, but cannot revise the receipt.
    if any(read.get(key) != value for key, value in receipt.items()):
        raise ValueError('Reading result differs from its original receipt')
    if read['status'] == 'prepared':
        packet = json.loads((directory / 'packet.json').read_text(encoding='utf-8'))
        if digest(packet) != receipt['packet_sha256']:
            raise ValueError('Reading packet changed')
        if any(packet[key] != receipt[key] for key in ['candidate_id', 'context_sha256', 'evidence_sha256', 'source_sha256']):
            raise ValueError('Reading packet differs from receipt identity')
        if hashlib.sha256((directory / 'source.xml').read_bytes()).hexdigest() != packet['source_sha256']:
            raise ValueError('Reading source changed')
    return directory


def portable_result(store, result):
    """Remove host-specific addressing from new persisted batch results."""
    if 'directory' not in result:
        return dict(result)
    directory = check_files(store, result)
    return {**result, 'directory': directory.name, 'directory_scope': SCOPE}


def presented_result(store, result):
    """Resolve a display/CLI path at read time; it is never stored in SQLite."""
    if 'directory' not in result:
        return dict(result)
    directory = check_files(store, result)
    return {**result, 'resolved_directory': str(directory)}


def legacy_relative(raw, source_root):
    if not isinstance(raw, str) or not isinstance(source_root, str):
        raise ValueError('Explicit source root and legacy path required')
    flavor = PureWindowsPath if PureWindowsPath(source_root).drive else PurePosixPath
    root, path = flavor(source_root), flavor(raw)
    if not root.is_absolute() or not path.is_absolute() or '..' in root.parts or '..' in path.parts:
        raise ValueError('Absolute source root/path without traversal required')
    if flavor is PurePosixPath and ('\\' in raw or ':' in raw or '\\' in source_root or ':' in source_root):
        raise ValueError('Mixed path syntax rejected')
    try:
        relative = path.relative_to(root)
    except ValueError as exc:
        raise ValueError('Legacy path does not belong to the explicit source root') from exc
    if len(relative.parts) != 1 or not READING_NAME.fullmatch(relative.name):
        raise ValueError('Legacy reading must be one immediate store child')
    return relative.name


def relocate_readings(store, batch_id, source_root):
    """Atomic, verified addressing amendment; retain original paths in private events.

    Run only on the designated restored store after quiescing its source writer.
    No source artifact, packet, assessment or scientific decision is rewritten.
    """
    with exclusive(store), store.db:
        store.db.execute('BEGIN IMMEDIATE')
        specification(store, batch_id)
        changes = []
        rows = store.db.execute('SELECT * FROM batch_items WHERE batch_id=? AND reading_json IS NOT NULL', (batch_id,)).fetchall()
        for row in rows:
            old = json.loads(row['reading_json'])
            if 'directory' not in old:
                continue
            if old.get('directory_scope') == SCOPE:
                check_files(store, old)
                continue
            if 'directory_scope' in old:
                raise ValueError('Unknown directory scope; no implicit migration')
            relative = legacy_relative(old['directory'], source_root)
            new = {**old, 'directory': relative, 'directory_scope': SCOPE}
            check_files(store, new)
            packet = json.loads(row['packet_json'])
            if digest(packet) != row['packet_sha']:
                raise ValueError('Stored screening packet changed')
            for key in ['candidate_id', 'context_sha256', 'evidence_sha256']:
                if new.get(key) != packet[key]:
                    raise ValueError('Reading identity differs from its screening packet')
            changes.append((row['candidate_id'], old, new))
        for cid, old, new in changes:
            store.db.execute('UPDATE batch_items SET reading_json=? WHERE batch_id=? AND candidate_id=?',
                             (json.dumps(new), batch_id, cid))
            event(store, batch_id, 'reading-path-relocated', {
                'candidate_id': cid, 'source_root': source_root, 'previous_result': old,
                'previous_result_sha256': digest(old), 'replacement_result_sha256': digest(new),
                'scope': 'addressing only; original artifacts and decisions preserved'})
    return {'status': 'relocated' if changes else 'already_portable', 'batch_id': batch_id,
            'changed_readings': len(changes), 'scientific_execution_allowed': False,
            'source_writer_fencing': 'operator responsibility; not a distributed lock'}
