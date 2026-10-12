"""Local bounded splitting/reassembly; transport and scientific authority are separate."""
import hashlib
import json
from pathlib import Path
import re
import stat

MAX_PART = 16 * 1024 * 1024
MAX_PARTS = 256
MAX_BYTES = MAX_PART * MAX_PARTS
MAX_MANIFEST = 128 * 1024


class TransferError(ValueError):
    pass


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _anchor(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise TransferError('Expected external SHA-256 anchor')


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode()


def _regular(path, limit):
    info = path.lstat()
    if not stat.S_ISREG(info.st_mode) or not 0 < info.st_size <= limit:
        raise TransferError('Not a bounded regular file')
    return info.st_size


def split_file(source, destination, *, expected_sha256, part_bytes=MAX_PART):
    """Create a fresh directory; incomplete failures retain parts but no manifest."""
    _anchor(expected_sha256)
    if type(part_bytes) is not int or not 1 <= part_bytes <= MAX_PART:
        raise TransferError('Invalid part size')
    source, destination = Path(source), Path(destination)
    size = _regular(source, MAX_BYTES)
    if (size + part_bytes - 1) // part_bytes > MAX_PARTS:
        raise TransferError('Too many parts')
    destination.mkdir(mode=0o700)
    digest, total, parts = hashlib.sha256(), 0, []
    with source.open('rb') as stream:
        while data := stream.read(part_bytes):
            if len(parts) >= MAX_PARTS or total + len(data) > size:
                raise TransferError('Source grew beyond bound')
            name = f'part-{len(parts):04d}.bin'
            with (destination / name).open('xb') as output:
                output.write(data)
            digest.update(data)
            total += len(data)
            parts.append({'name': name, 'bytes': len(data), 'sha256': _hash(data)})
    if total != size or digest.hexdigest() != expected_sha256:
        raise TransferError('Source content changed or external hash mismatch')
    manifest = {'schema_version': 1, 'artifact_bytes': total,
                'artifact_sha256': expected_sha256, 'part_bytes': part_bytes, 'parts': parts}
    raw = _canonical(manifest)
    with (destination / 'manifest.json').open('xb') as output:
        output.write(raw)
    return {'manifest_sha256': _hash(raw), 'artifact_sha256': expected_sha256,
            'artifact_bytes': total, 'parts': len(parts)}


def reassemble(source, destination, *, expected_manifest_sha256, expected_artifact_sha256):
    """Require external anchors and a fresh output directory. Never extract/execute."""
    _anchor(expected_manifest_sha256)
    _anchor(expected_artifact_sha256)
    source, destination = Path(source), Path(destination)
    if source.is_symlink() or not source.is_dir():
        raise TransferError('Expected a regular parts directory')
    _regular(source / 'manifest.json', MAX_MANIFEST)
    raw = (source / 'manifest.json').read_bytes()
    if _hash(raw) != expected_manifest_sha256:
        raise TransferError('Manifest anchor mismatch')
    try:
        m = json.loads(raw)
        if _canonical(m) != raw or set(m) != {'schema_version', 'artifact_bytes', 'artifact_sha256', 'part_bytes', 'parts'}:
            raise ValueError('Noncanonical or unexpected manifest')
        if type(m['schema_version']) is not int or m['schema_version'] != 1:
            raise ValueError('Version')
        if m['artifact_sha256'] != expected_artifact_sha256:
            raise ValueError('Artifact anchor')
        if type(m['artifact_bytes']) is not int or not 0 < m['artifact_bytes'] <= MAX_BYTES:
            raise ValueError('Artifact bound')
        if type(m['part_bytes']) is not int or not 1 <= m['part_bytes'] <= MAX_PART:
            raise ValueError('Part bound')
        if not isinstance(m['parts'], list) or not 1 <= len(m['parts']) <= MAX_PARTS:
            raise ValueError('Parts')
        if len(m['parts']) != (m['artifact_bytes'] + m['part_bytes'] - 1) // m['part_bytes']:
            raise ValueError('Part count')
        for i, part in enumerate(m['parts']):
            if set(part) != {'name', 'bytes', 'sha256'} or part['name'] != f'part-{i:04d}.bin':
                raise ValueError('Part name/order')
            expected_size = min(m['part_bytes'], m['artifact_bytes'] - i * m['part_bytes'])
            if type(part['bytes']) is not int or part['bytes'] != expected_size:
                raise ValueError('Part length')
            _anchor(part['sha256'])
        if {p.name for p in source.iterdir()} != {'manifest.json', *(p['name'] for p in m['parts'])}:
            raise ValueError('Missing or unexpected files')
    except (ValueError, TypeError, KeyError, UnicodeError) as exc:
        raise TransferError('Invalid transfer manifest') from exc
    destination.mkdir(mode=0o700)
    digest = hashlib.sha256()
    with (destination / 'payload.bin').open('xb') as output:
        for part in m['parts']:
            path = source / part['name']
            if _regular(path, MAX_PART) != part['bytes']:
                raise TransferError('Part size mismatch')
            with path.open('rb') as stream:
                data = stream.read(part['bytes'] + 1)
            if len(data) != part['bytes'] or _hash(data) != part['sha256']:
                raise TransferError('Part content mismatch')
            output.write(data)
            digest.update(data)
    if digest.hexdigest() != expected_artifact_sha256:
        raise TransferError('Reconstructed artifact hash mismatch')
    result = {'status': 'VERIFIED_LOCAL_BYTES', 'artifact_bytes': m['artifact_bytes'],
              'artifact_sha256': expected_artifact_sha256, 'manifest_sha256': expected_manifest_sha256,
              'parts': len(m['parts']), 'transport_verified': False, 'activation_permitted': False}
    with (destination / 'verified.json').open('xb') as output:
        output.write(_canonical(result))
    return result
