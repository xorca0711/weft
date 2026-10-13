"""Offline submission-intent journal. No provider calls or dispatch authority.

Cooperating callers share one database. An uncertain submission never retries;
only an externally observed acknowledgement can reconcile it. Fingerprints and
receipts are operator-supplied evidence, not authenticated provider attestations.
"""
import hashlib
import json
from pathlib import Path
import re
import socket
import sqlite3


FLAGS = {'provider_called': False, 'dispatch_authorized': False,
         'scientific_execution_allowed': False}


def _encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def _hash(raw):
    return hashlib.sha256(raw).hexdigest()


def _text(value, limit=256):
    return isinstance(value, str) and 0 < len(value) <= limit and value.strip() == value and not any(ord(c) < 32 for c in value)


def _spec(spec, prompt):
    fields = {'schema_version', 'kind', 'operation_key', 'repository', 'source_revision',
              'prompt_sha256', 'environment_sha256', 'policy_sha256', 'account_scope_sha256',
              'max_submissions'}
    if not isinstance(spec, dict) or set(spec) != fields:
        raise ValueError('Exact versioned launch specification required')
    if (type(spec['schema_version']) is not int or spec['schema_version'] != 1
            or spec['kind'] != 'synthetic-qualification'
            or type(spec['max_submissions']) is not int or spec['max_submissions'] != 1):
        raise ValueError('Only one synthetic submission is supported')
    if not _text(spec['operation_key'], 128) or not _text(spec['repository']):
        raise ValueError('Bounded operation and repository identities required')
    for key in fields:
        length = 40 if key == 'source_revision' else 64 if key.endswith('_sha256') else None
        if length and (not isinstance(spec[key], str) or not re.fullmatch('[0-9a-f]{' + str(length) + '}', spec[key])):
            raise ValueError('Invalid fingerprint: ' + key)
    if not isinstance(prompt, bytes) or not 0 < len(prompt) <= 100_000 or _hash(prompt) != spec['prompt_sha256']:
        raise ValueError('Exact bounded prompt bytes required')
    return _encode(spec)


class LaunchJournal:
    def __init__(self, path):
        self.path = Path(path).absolute()
        if any(p.is_symlink() or p.is_junction() for p in [self.path, *self.path.parents]):
            raise ValueError('Launch journal must not traverse links/junctions')
        self.path = self.path.resolve(strict=True)
        self.db = sqlite3.connect(self.path.as_uri() + '?mode=rw', uri=True, timeout=15,
                                  isolation_level=None)
        self.db.row_factory = sqlite3.Row
        try:
            row = self.db.execute('SELECT * FROM launch_journal_identity').fetchall()
            if len(row) != 1 or row[0]['schema_version'] != 1:
                raise ValueError('Not a version-1 launch journal')
            self.binding = dict(row[0])
        except Exception:
            self.db.close()
            raise

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.db.close()

    def _active(self):
        return self.binding['host'] == socket.gethostname() and self.binding['path'] == str(self.path)

    def _begin(self):
        if not self._active():
            raise ValueError('Restored or moved journal is inactive; reconciliation required')
        self.db.execute('BEGIN IMMEDIATE')

    def _row(self, key):
        row = self.db.execute('SELECT * FROM launch_intents WHERE operation_key=?', (key,)).fetchone()
        if not row:
            raise ValueError('Unknown launch operation')
        if _hash(row['spec_json'].encode()) != row['spec_sha256'] or json.loads(row['spec_json'])['operation_key'] != key:
            raise ValueError('Saved launch specification changed')
        if row['receipt_json'] is not None and _hash(row['receipt_json'].encode()) != row['receipt_sha256']:
            raise ValueError('Saved acknowledgement changed')
        return row

    def _event(self, key, action, sha):
        self.db.execute('INSERT INTO launch_events(operation_key,action,evidence_sha256) VALUES(?,?,?)', (key, action, sha))

    def prepare(self, spec, prompt):
        encoded = _spec(spec, prompt)
        key = spec['operation_key']
        with self.db:
            self._begin()
            existing = self.db.execute('SELECT 1 FROM launch_intents WHERE operation_key=?', (key,)).fetchone()
            if existing:
                if self._row(key)['spec_json'] != encoded:
                    raise ValueError('Operation key already binds different launch intent')
            else:
                sha = _hash(encoded.encode())
                self.db.execute('INSERT INTO launch_intents VALUES(?,?,?,\'prepared\',NULL,NULL)', (key, encoded, sha))
                self._event(key, 'prepared', sha)
        return self.status(key)

    def begin(self, spec, prompt):
        encoded = _spec(spec, prompt)
        key = spec['operation_key']
        with self.db:
            self._begin()
            row = self._row(key)
            if row['spec_json'] != encoded:
                raise ValueError('Current source/prompt/account/environment/policy differs from saved intent')
            if row['state'] != 'prepared':
                raise ValueError('Submission already begun; reconcile acknowledgement, never resubmit')
            if self.db.execute("SELECT 1 FROM launch_intents WHERE state='awaiting_ack'").fetchone():
                raise ValueError('Another uncertain submission blocks launch progression')
            self.db.execute("UPDATE launch_intents SET state='awaiting_ack' WHERE operation_key=?", (key,))
            self._event(key, 'submission-intent-committed', row['spec_sha256'])
        return self.status(key)

    def acknowledge(self, key, receipt):
        fields = {'operation_key', 'spec_sha256', 'task_id', 'observation_sha256'}
        if not isinstance(receipt, dict) or set(receipt) != fields or receipt['operation_key'] != key or not _text(receipt['task_id']):
            raise ValueError('Exact scoped task acknowledgement required')
        for field in ('spec_sha256', 'observation_sha256'):
            if not isinstance(receipt[field], str) or not re.fullmatch('[0-9a-f]{64}', receipt[field]):
                raise ValueError('Invalid acknowledgement fingerprint')
        encoded = _encode(receipt)
        with self.db:
            self._begin()
            row = self._row(key)
            if row['spec_sha256'] != receipt['spec_sha256'] or row['state'] == 'prepared':
                raise ValueError('Acknowledgement does not bind a begun submission')
            if row['receipt_json'] is not None:
                if row['receipt_json'] != encoded:
                    raise ValueError('Conflicting task acknowledgement; preserve prior evidence')
            else:
                sha = _hash(encoded.encode())
                self.db.execute("UPDATE launch_intents SET state='acknowledged',receipt_json=?,receipt_sha256=? WHERE operation_key=?", (encoded, sha, key))
                self._event(key, 'acknowledgement-recorded', sha)
        return self.status(key)

    def status(self, key):
        row = self._row(key)
        return {'operation_key': key, 'state': row['state'], 'active_binding': self._active(),
                'spec_sha256': row['spec_sha256'], 'receipt_sha256': row['receipt_sha256'],
                'acknowledgement': json.loads(row['receipt_json']) if row['receipt_json'] else None,
                'resubmission_allowed': False, **FLAGS}


def initialize(path):
    path = Path(path).absolute()
    if any(p.is_symlink() or p.is_junction() for p in [path, *path.parents]):
        raise ValueError('Launch journal must not traverse links/junctions')
    path.parent.mkdir(parents=True, exist_ok=True)
    # Never open an existing scientific ledger, catalog or partial initialization.
    with path.open('xb'):
        pass
    db = sqlite3.connect(path)
    try:
        db.executescript('''
          CREATE TABLE launch_journal_identity(schema_version INTEGER, host TEXT, path TEXT);
          CREATE TABLE launch_intents(operation_key TEXT PRIMARY KEY, spec_json TEXT NOT NULL,
            spec_sha256 TEXT NOT NULL, state TEXT NOT NULL CHECK(state IN ('prepared','awaiting_ack','acknowledged')),
            receipt_json TEXT, receipt_sha256 TEXT);
          CREATE UNIQUE INDEX one_uncertain_launch ON launch_intents((1)) WHERE state='awaiting_ack';
          CREATE TABLE launch_events(sequence INTEGER PRIMARY KEY, operation_key TEXT NOT NULL,
            action TEXT NOT NULL, evidence_sha256 TEXT NOT NULL);
        ''')
        with db:
            db.execute('INSERT INTO launch_journal_identity VALUES(1,?,?)', (socket.gethostname(), str(path.resolve())))
    finally:
        db.close()
    return {'status': 'initialized', **FLAGS}
