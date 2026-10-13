"""Cooperative, single-catalog screening handoffs. No worker or model launcher.

An expired or uncertain handoff is never reassigned. Recovery ingests only its
saved response through the existing screening validator. Host/path binding is
an accidental-restore guard, not distributed fencing or actor authentication.
"""
from datetime import datetime, timezone
import json
import socket
import uuid

from . import batches, screening
from .identity import digest


FLAGS = {'model_invoked': False, 'scientific_execution_allowed': False,
         'actor_identity_verified': False}


def _schema(store):
    batches.schema(store)
    store.db.executescript('''
      CREATE TABLE IF NOT EXISTS handoff_binding(
        singleton INTEGER PRIMARY KEY CHECK(singleton=1), identity_json TEXT NOT NULL);
      CREATE TABLE IF NOT EXISTS screening_handoffs(
        id TEXT PRIMARY KEY, batch_id TEXT NOT NULL, candidate_id TEXT NOT NULL,
        actor TEXT NOT NULL, state TEXT NOT NULL, issued_json TEXT NOT NULL,
        packet_sha TEXT NOT NULL, expires REAL NOT NULL,
        response_json TEXT, response_sha TEXT, result_json TEXT);
      CREATE UNIQUE INDEX IF NOT EXISTS one_open_screening_handoff
        ON screening_handoffs((1)) WHERE state != 'complete';
    ''')


def _time():
    return datetime.now(timezone.utc).timestamp()


def initialize(store):
    with batches.exclusive(store, name='.handoff.lock'):
        _schema(store)
        if store.db.execute('SELECT 1 FROM handoff_binding').fetchone():
            return {'status': 'already_bound', 'binding': _binding(store), **FLAGS}
        identity = {'schema_version': 1, 'id': uuid.uuid4().hex,
                    'host': socket.gethostname(), 'store': str(store.root)}
        with store.db:
            store.db.execute('INSERT INTO handoff_binding VALUES(1,?)', (json.dumps(identity),))
        return {'status': 'bound', 'binding': identity, **FLAGS}


def _binding(store):
    _schema(store)
    row = store.db.execute('SELECT identity_json FROM handoff_binding').fetchone()
    if not row:
        raise ValueError('Explicit handoff-init required for this catalog')
    identity = json.loads(row[0])
    if identity['host'] != socket.gethostname() or identity['store'] != str(store.root):
        raise ValueError('Restored/moved catalog is inactive: operator reconciliation required')
    return identity


def _row(store, claim_id):
    row = store.db.execute('SELECT * FROM screening_handoffs WHERE id=?', (claim_id,)).fetchone()
    if not row:
        raise ValueError('Unknown handoff')
    issued = json.loads(row['issued_json'])
    if digest(issued['packet']) != row['packet_sha'] or issued['packet_sha256'] != row['packet_sha']:
        raise ValueError('Saved handoff packet changed')
    if (issued['packet']['batch_id'], issued['packet']['candidate_id']) != (row['batch_id'], row['candidate_id']):
        raise ValueError('Saved handoff identity changed')
    return row, issued


def claim(store, batch_id, actor, *, lease_seconds=1800):
    if not isinstance(actor, str) or not actor.strip() or len(actor) > 200:
        raise ValueError('Explicit bounded actor label required')
    if type(lease_seconds) is not int or not 60 <= lease_seconds <= 3600:
        raise ValueError('Lease must be 60..3600 seconds; expiry never reassigns work')
    with batches.exclusive(store, name='.handoff.lock'):
        _binding(store)
        active = store.db.execute("SELECT id FROM screening_handoffs WHERE state!='complete'").fetchone()
        if active:
            raise ValueError('Unresolved handoff blocks another claim: ' + active[0])
        issued = screening.next_packet(store, batch_id)
        if issued['status'] != 'awaiting_agent':
            return issued
        cid = issued['packet']['candidate_id']
        claim_id = uuid.uuid4().hex
        expires = _time() + lease_seconds
        # Commit before returning a packet. A lost stdout is recoverable by status/packet.
        with store.db:
            store.db.execute('INSERT INTO screening_handoffs VALUES(?,?,?,?,?,?,?,?,NULL,NULL,NULL)',
                             (claim_id, batch_id, cid, actor, 'claimed', json.dumps(issued),
                              issued['packet_sha256'], expires))
            batches.event(store, batch_id, 'handoff-claimed', {'claim_id': claim_id,
                          'candidate_id': cid, 'actor': actor, 'expires': expires})
        return {'status': 'claimed', 'claim_id': claim_id, 'expires': expires,
                'issued': issued, **FLAGS}


def status(store):
    with batches.exclusive(store, name='.handoff.lock'):
        identity = _binding(store)
        rows = store.db.execute('SELECT id,batch_id,candidate_id,actor,state,expires,response_sha FROM screening_handoffs ORDER BY rowid').fetchall()
        claims = [dict(r) for r in rows]
        for item in claims:
            item['expired'] = _time() >= item['expires']
            item['automatic_reassignment_allowed'] = False
        return {'status': 'bound', 'binding': identity, 'claims': claims, **FLAGS}


def packet(store, claim_id):
    """Recover lost handoff output; this does not authorize a second worker."""
    with batches.exclusive(store, name='.handoff.lock'):
        _binding(store)
        row, issued = _row(store, claim_id)
        return {'status': row['state'], 'claim_id': claim_id, 'issued': issued,
                'expired': _time() >= row['expires'], 'redispatch_allowed': False, **FLAGS}


def _ingest(store, claim_id):
    row, _ = _row(store, claim_id)
    if row['response_json'] is None:
        raise ValueError('No saved response; held for operator reconciliation, never redispatch')
    response = json.loads(row['response_json'])
    if digest(response) != row['response_sha']:
        raise ValueError('Saved response changed')
    if (response.get('batch_id'), response.get('candidate_id'), response.get('packet_sha256'), response.get('actor')) != (
            row['batch_id'], row['candidate_id'], row['packet_sha'], row['actor']):
        raise ValueError('Saved response identity changed')
    # Existing validator checks live source, context, stage, citations and exact replay.
    result = screening.submit(store, row['batch_id'], response)
    if row['state'] != 'complete':
        with store.db:
            store.db.execute("UPDATE screening_handoffs SET state='complete',result_json=? WHERE id=?",
                             (json.dumps(result), claim_id))
            batches.event(store, row['batch_id'], 'handoff-complete',
                          {'claim_id': claim_id, 'response_sha256': row['response_sha']})
    return {'status': 'complete', 'claim_id': claim_id, 'screening': result, **FLAGS}


def submit(store, claim_id, response):
    if not isinstance(response, dict) or len(json.dumps(response).encode()) > 1_000_000:
        raise ValueError('Response must be an object below 1 MB')
    with batches.exclusive(store, name='.handoff.lock'):
        _binding(store)
        row, _ = _row(store, claim_id)
        if (response.get('batch_id'), response.get('candidate_id'), response.get('packet_sha256'), response.get('actor')) != (
                row['batch_id'], row['candidate_id'], row['packet_sha'], row['actor']):
            raise ValueError('Response does not match handoff/actor label')
        if row['response_sha']:
            if row['response_sha'] != digest(response):
                raise ValueError('Different response: preserve saved intent for explicit review')
        else:
            if _time() >= row['expires']:
                raise ValueError('Expired handoff held; no new response or reassignment')
            with store.db:
                store.db.execute("UPDATE screening_handoffs SET state='return_pending',response_json=?,response_sha=? WHERE id=?",
                                 (json.dumps(response), digest(response), claim_id))
                batches.event(store, row['batch_id'], 'handoff-return-saved',
                              {'claim_id': claim_id, 'response_sha256': digest(response)})
        # If validation or acknowledgement fails, intent stays pending and blocks another claim.
        return _ingest(store, claim_id)


def recover(store, claim_id):
    """Only finish ingestion of saved bytes; no search, reading or model replay."""
    with batches.exclusive(store, name='.handoff.lock'):
        _binding(store)
        return _ingest(store, claim_id)
