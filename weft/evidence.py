"""Private immutable evidence records. No execution, dispatch or acceptance API."""
from __future__ import annotations

from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import stat
import uuid

from .validation import safe_relative
from .workflow import _exclusive

VERSION = 'weft-evidence-v1'
MAX_RECORD = 1_048_576
FLAGS = {'dispatch_authorized': False, 'canonical_acceptance': False}
COMMON = {'schema_version', 'kind', 'workspace_id', 'revision', 'previous',
          'amendment_reason', 'created_at', 'actor', *FLAGS}
REF_KEYS = {'root', 'path', 'sha256', 'bytes'}
KINDS = {'source-manifest', 'case-revision', 'data-feasibility', 'analysis-contract',
         'numerical-plan', 'scientific-review', 'owner-disposition'}


def keys(value, expected):
    if not isinstance(value, dict) or set(value) != set(expected):
        raise ValueError('Exact evidence record fields required')


def text(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 8192:
        raise ValueError('Nonempty bounded text required')


def identifier(value, prefix):
    if not isinstance(value, str) or not re.fullmatch(prefix + '-[0-9a-f]{32}', value):
        raise ValueError('Invalid provisional identifier: ' + prefix)


def sha(value):
    if not isinstance(value, str) or not re.fullmatch('[0-9a-f]{64}', value):
        raise ValueError('SHA-256 required')


def encoded(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False, indent=2,
                       allow_nan=False) + '\n').encode('utf-8')


def decode(raw):
    if len(raw) > MAX_RECORD:
        raise ValueError('Evidence JSON exceeds 1 MiB')
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out:
                raise ValueError('Duplicate JSON key')
            out[key] = value
        return out
    def invalid(_):
        raise ValueError('Non-finite JSON number')
    return json.loads(raw.decode('utf-8'), object_pairs_hook=unique, parse_constant=invalid)


def unlinked(path):
    path = Path(path).absolute()
    for part in [*reversed(path.parents), path]:
        if part.exists() or part.is_symlink():
            s = part.lstat()
            if (part.is_symlink() or getattr(s, 'st_file_attributes', 0) &
                    getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0x400)):
                raise ValueError('Linked/reparse evidence path rejected')
    return path


def relative(value):
    if not safe_relative(value) or not re.fullmatch('[A-Za-z0-9._/-]+', value):
        raise ValueError('Portable relative path required')
    for part in value.split('/'):
        if part.endswith('.') or re.fullmatch(r'(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?', part):
            raise ValueError('Platform-ambiguous path rejected')


def contained(root, name):
    relative(name)
    root = unlinked(root).resolve(strict=True)
    path = unlinked(root / name)
    if not path.resolve().is_relative_to(root):
        raise ValueError('Evidence path escapes root')
    current = root
    for part in name.split('/'):
        if current.is_dir() and any(p.name.casefold() == part.casefold() and
                                   p.name != part for p in current.iterdir()):
            raise ValueError('Case-insensitive path collision')
        current = current / part
    return path


def read_raw(path):
    path = unlinked(path)
    with path.open('rb') as stream:
        s = os.fstat(stream.fileno())
        if not stat.S_ISREG(s.st_mode) or s.st_nlink != 1:
            raise ValueError('Unlinked regular record required')
        raw = stream.read(MAX_RECORD + 1)
    if len(raw) > MAX_RECORD:
        raise ValueError('Record exceeds 1 MiB')
    return raw


def write_new(path, raw):
    path = unlinked(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    unlinked(path.parent)
    with path.open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def reference(root, name, *, expected_bytes=None):
    path = contained(root, name)
    with path.open('rb') as stream:
        before = os.fstat(stream.fileno())
        if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
            raise ValueError('Unlinked regular input required')
        if expected_bytes is None:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        else:
            if before.st_size != expected_bytes:
                raise ValueError('Referenced file size changed before hashing')
            hasher, count = hashlib.sha256(), 0
            while True:
                chunk = stream.read(min(1_048_576, expected_bytes - count + 1))
                if not chunk: break
                count += len(chunk)
                if count > expected_bytes: raise ValueError('Referenced file grew while hashing')
                hasher.update(chunk)
            digest = hasher.hexdigest()
        after = os.fstat(stream.fileno())
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError('File changed while hashing')
    return {'root': 'workspace', 'path': name, 'sha256': digest, 'bytes': after.st_size}


def common(record):
    if not isinstance(record, dict):
        raise ValueError('Evidence object required')
    if record.get('schema_version') != VERSION or record.get('kind') not in KINDS:
        raise ValueError('Unsupported evidence record version/kind')
    identifier(record['workspace_id'], 'ww')
    if any(record[k] is not v for k, v in FLAGS.items()):
        raise ValueError('Evidence records cannot grant execution or acceptance')
    if type(record['revision']) is not int or not 1 <= record['revision'] <= 999999:
        raise ValueError('Invalid revision')
    text(record['created_at'])
    at = datetime.fromisoformat(record['created_at'].replace('Z', '+00:00'))
    if at.tzinfo is None or at.utcoffset() is None:
        raise ValueError('Timezone-aware timestamp required')
    keys(record['actor'], {'id', 'kind', 'identity_basis'})
    text(record['actor']['id'])
    if record['actor']['kind'] not in {'human', 'agent', 'fixture'} or record['actor']['identity_basis'] != 'self-reported':
        raise ValueError('Attribution is not authenticated identity')
    if record['revision'] == 1:
        if record['previous'] is not None or record['amendment_reason'] is not None:
            raise ValueError('Initial revision cannot replace a predecessor')
    else:
        keys(record['previous'], REF_KEYS)
        text(record['amendment_reason'])


def record_path(record):
    identifier(record['article_id'], 'wa')
    base = f"articles/{record['article_id']}"
    if record['kind'] == 'source-manifest':
        base += '/sources'
    else:
        identifier(record['case_id'], 'wc')
        base += f"/cases/{record['case_id']}/{record['kind']}"
    return f"{base}/v{record['revision']:06d}.json"


class Workspace:
    def __init__(self, root):
        self.root = unlinked(root).resolve(strict=True)
        self.binding = decode(read_raw(self.root / 'private-bindings.json'))
        keys(self.binding, {'schema_version', 'workspace_id', 'host', 'root', 'inputs', 'sources', 'protected_roots'})
        if self.binding['schema_version'] != VERSION:
            raise ValueError('Unsupported workspace binding')
        identifier(self.binding['workspace_id'], 'ww')
        self.active = (self.binding['host'] == socket.gethostname() and
                       self.binding['root'] == str(self.root))
        self.roots = {'workspace': self.root, **{k: Path(self.binding[k]) for k in ('inputs', 'sources')}}
        self._isolation()

    def _isolation(self):
        for path in [self.roots['inputs'], self.roots['sources'],
                     *map(Path, self.binding['protected_roots'])]:
            resolved = unlinked(path).resolve(strict=True)
            if self.root.is_relative_to(resolved) or resolved.is_relative_to(self.root):
                raise ValueError('Workspace overlaps an input or protected root')

    @classmethod
    def create(cls, root, *, inputs, sources, protected_roots):
        if not Path(root).is_absolute():
            raise ValueError('Evidence root must be explicitly absolute')
        root = unlinked(root)
        if not root.is_absolute() or root.exists() or not root.parent.is_dir():
            raise ValueError('Fresh root with existing parent required')
        if not protected_roots:
            raise ValueError('Explicit protected Ravel/historical roots required')
        protected = [str(unlinked(p).resolve(strict=True)) for p in protected_roots]
        locations = {k: str(unlinked(p).resolve(strict=True)) for k, p in [('inputs', inputs), ('sources', sources)]}
        if any(not Path(p).is_dir() for p in [*locations.values(), *protected]):
            raise ValueError('Registered roots must be directories')
        resolved = root.resolve()
        for other in [*locations.values(), *protected]:
            p = Path(other)
            if resolved.is_relative_to(p) or p.is_relative_to(resolved):
                raise ValueError('Workspace overlaps inputs or protected storage')
        root.mkdir(mode=0o700)
        binding = {'schema_version': VERSION, 'workspace_id': 'ww-' + uuid.uuid4().hex,
                   'host': socket.gethostname(), 'root': str(resolved), **locations,
                   'protected_roots': protected}
        write_new(root / 'private-bindings.json', encoded(binding))
        return cls(root)

    def file(self, ref, *, parse=False):
        keys(ref, REF_KEYS)
        if ref['root'] not in self.roots:
            raise ValueError('Unregistered input root')
        sha(ref['sha256'])
        if type(ref['bytes']) is not int or not 0 <= ref['bytes'] <= 2**63 - 1:
            raise ValueError('Invalid byte count')
        path = contained(self.roots[ref['root']], ref['path'])
        if parse:
            raw = read_raw(path)
            actual = {'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)}
        else:
            actual = reference(self.roots[ref['root']], ref['path'], expected_bytes=ref['bytes'])
        if any(actual[k] != ref[k] for k in ('sha256', 'bytes')):
            raise ValueError('Referenced file bytes changed')
        return decode(raw) if parse else path

    def bound_record(self, ref, kind, *, case=None, latest=True):
        obj = self.file(ref, parse=True)
        if (ref['root'] != 'workspace' or obj['kind'] != kind or
                obj['workspace_id'] != self.binding['workspace_id'] or
                ref['path'] != record_path(obj)):
            raise ValueError('Wrong evidence record identity/kind/path')
        if case and (obj['article_id'] != case['article_id'] or
                     (kind != 'source-manifest' and obj['case_id'] != case['case_id'])):
            raise ValueError('Evidence belongs to another article/case')
        if latest:
            sibling = self.root / ref['path']
            revisions = sorted(sibling.parent.glob('v[0-9][0-9][0-9][0-9][0-9][0-9].json'))
            if not revisions or revisions[-1] != sibling:
                raise ValueError('Stale dependent record; new revision required')
        return obj

    def validate(self, obj):
        common(obj)
        if obj['workspace_id'] != self.binding['workspace_id']:
            raise ValueError('Wrong workspace identity')
        record_path(obj)
        ancestor = obj
        while ancestor['revision'] > 1:
            previous = self.bound_record(ancestor['previous'], ancestor['kind'], case=ancestor, latest=False)
            common(previous)
            if previous['revision'] != ancestor['revision'] - 1:
                raise ValueError('Predecessor revision discontinuity')
            if obj['kind'] == 'case-revision' and previous['exposure']['mode'] != obj['exposure']['mode']:
                raise ValueError('Exposure history changed')
            ancestor = previous
        if obj['kind'] == 'source-manifest':
            keys(obj, COMMON | {'article_id', 'bibliography', 'origin', 'resources'})
            keys(obj['bibliography'], {'identifiers', 'title', 'integrity_status'})
            string_list(obj['bibliography']['identifiers'], nonempty=True)
            text(obj['bibliography']['title'])
            if obj['bibliography']['integrity_status'] not in {'unknown', 'concern-recorded', 'review-recorded', 'synthetic-fixture'}:
                raise ValueError('Invalid source integrity state')
            if obj['origin'] is not None:
                keys(obj['origin'], {'catalog_id', 'batch_id', 'candidate_id', 'packet_sha256'})
                for key in ('catalog_id', 'batch_id', 'candidate_id'): text(obj['origin'][key])
                sha(obj['origin']['packet_sha256'])
            if not isinstance(obj['resources'], list) or not 1 <= len(obj['resources']) <= 256:
                raise ValueError('Bounded source inventory required')
            ids = set()
            for item in obj['resources']:
                keys(item, {'resource_id', 'version', 'locator', 'access', 'inspection', 'file', 'limits'})
                for key in ('resource_id', 'version', 'locator', 'limits'): text(item[key])
                if item['resource_id'] in ids: raise ValueError('Duplicate source resource')
                ids.add(item['resource_id'])
                if item['inspection'] not in {'not-inspected', 'metadata-only', 'caption-only', 'inspected'}:
                    raise ValueError('Unknown inspection state')
                if item['access'] == 'retained': self.file(item['file'])
                elif item['access'] not in {'listed-only', 'unavailable'} or item['file'] is not None:
                    raise ValueError('Unsupported source access binding')
        elif obj['kind'] == 'case-revision':
            keys(obj, COMMON | {'article_id', 'case_id', 'source_manifest', 'purpose',
                               'analysis_mode', 'question', 'comparison', 'endpoint',
                               'inference_scope', 'exposure', 'holds'})
            self.bound_record(obj['source_manifest'], 'source-manifest', case=obj)
            if obj['purpose'] not in {'description', 'replication', 'prediction', 'perturbation-effect', 'exploration'}:
                raise ValueError('Unknown scientific purpose')
            if obj['analysis_mode'] not in {'reproduction', 'adapted-analysis', 'exploration'}:
                raise ValueError('Unknown analysis mode')
            text(obj['question'])
            for key in ('comparison', 'endpoint'):
                if obj[key] is not None: text(obj[key])
            if obj['inference_scope'] not in {'unresolved', 'descriptive', 'within-sample', 'replicated-population'}:
                raise ValueError('Unknown inference scope')
            keys(obj['exposure'], {'mode', 'note', 'evidence'})
            if obj['exposure']['mode'] not in {'synthetic-fixture', 'historical-replay', 'exposed-exploration', 'prospective-test'}:
                raise ValueError('Unknown exposure mode')
            text(obj['exposure']['note'])
            if not isinstance(obj['exposure']['evidence'], list): raise ValueError('Exposure references required')
            for ref in obj['exposure']['evidence']: self.file(ref)
            string_list(obj['holds'])
            if (obj['comparison'] is None or obj['endpoint'] is None or obj['inference_scope'] == 'unresolved') and not obj['holds']:
                raise ValueError('Missing design must remain held')
        else:
            from .scientific import validate
            return validate(self, obj)
        return {'status': 'recorded', **FLAGS}

    def put(self, raw):
        if not self.active: raise ValueError('Restored workspace is inactive for writes')
        lock = unlinked(self.root / '.workflow.lock')
        if lock.exists() and (not lock.is_file() or lock.stat().st_nlink != 1):
            raise ValueError('Aliased workflow lock rejected')
        with _exclusive(self):
            self._isolation()
            obj = decode(raw)
            result = self.validate(obj)
            name = record_path(obj)
            path = contained(self.root, name)
            if path.exists():
                if read_raw(path) != raw: raise ValueError('Immutable record already exists with different bytes')
                return {**result, 'record': reference(self.root, name), 'idempotent': True}
            existing = sorted(path.parent.glob('v[0-9][0-9][0-9][0-9][0-9][0-9].json')) if path.parent.exists() else []
            if [p.name for p in existing] != [f'v{i:06d}.json' for i in range(1, len(existing) + 1)]:
                raise ValueError('Existing revision sequence has a gap')
            if obj['revision'] != len(existing) + 1:
                raise ValueError('Revision gap or fork')
            if existing:
                expected = reference(self.root, existing[-1].relative_to(self.root).as_posix())
                if obj['previous'] != expected: raise ValueError('Wrong predecessor binding')
                previous = decode(read_raw(existing[-1]))
                if obj['kind'] == 'case-revision' and previous['exposure']['mode'] != obj['exposure']['mode']:
                    raise ValueError('Exposure cannot be erased by a new version')
            write_new(path, raw)
            return {**result, 'record': reference(self.root, name), 'idempotent': False}

    def status(self):
        from .science_adapter import attempt_status
        records = []
        for path in sorted(self.root.glob('articles/**/v[0-9][0-9][0-9][0-9][0-9][0-9].json')):
            raw = read_raw(path)
            obj = decode(raw)
            try:
                siblings = sorted(path.parent.glob('v[0-9][0-9][0-9][0-9][0-9][0-9].json'))
                result = self.validate(obj) if siblings[-1] == path else {'status': 'historical'}
                issue = None
            except (ValueError, KeyError, TypeError, OSError) as exc:
                result, issue = {'status': 'hold'}, str(exc)
            records.append({'path': path.relative_to(self.root).as_posix(), 'kind': obj.get('kind'),
                            'sha256': hashlib.sha256(raw).hexdigest(), 'assessment': result, 'issue': issue})
        attempts = attempt_status(self)
        held = any(r['issue'] or r['assessment']['status'] == 'held' for r in records)
        held = held or any(a['state'] in {'unknown', 'cancel_requested'} for a in attempts)
        return {'status': 'hold' if held else 'recorded',
                'workspace_id': self.binding['workspace_id'], 'writable_here': self.active,
                'records': records, 'attempts': attempts,
                'scientific_execution_implemented': False, **FLAGS}


def string_list(value, *, nonempty=False):
    if not isinstance(value, list) or (nonempty and not value):
        raise ValueError('List required')
    for item in value: text(item)
    if len(value) != len(set(value)): raise ValueError('Duplicate list member')
