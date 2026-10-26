"""Shared-ledger author preparation lifecycle; there is deliberately no start API.

Reservations are preparation work, not runtime admission. Supplied worker/return
observations are quarantined and retain the global slot until a future qualified
backend can reconcile them. No JSON report or token proves process termination.
"""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
from pathlib import Path
import secrets

from . import evidence as ev, author_worker as worker, science_adapter as adapter
from .jobs import JobError, JobLedger, canonical
from .identity import digest
from .workflow import _exclusive

VERSION = 'weft-author-attempt-preparation-v1'
KIND = 'author-preparation'


@contextmanager
def open_attempts(workspace, **kwargs):
    with JobLedger(adapter._ledger_path(workspace), **kwargs) as ledger:
        yield AuthorAttempts(workspace, ledger)


class AuthorAttempts:
    def __init__(self, workspace, ledger):
        if ledger.path.absolute() != adapter._ledger_path(workspace):
            raise ValueError('Use the authoritative workspace ledger')
        self.workspace, self.ledger = workspace, ledger

    def _packet(self, ref):
        prepared = worker.load_preparation(self.workspace, ref)
        return {'schema_version': VERSION, 'kind': KIND, 'preparation': ref,
                'implementation_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'workspace_id': self.workspace.binding['workspace_id'],
                'max_attempts': prepared['limits']['max_attempts'],
                'lease_seconds': prepared['limits']['wall_seconds'], **ev.FLAGS}

    @staticmethod
    def _prefix(claim):
        ev.sha(claim['job_id'])
        if type(claim['attempt_id']) is not int or not 1 <= claim['attempt_id'] <= 2**63 - 1:
            raise ValueError('Invalid attempt')
        return f"author-attempts/{claim['job_id']}/attempt-{claim['attempt_id']:06d}"

    def reserve(self, preparation_ref):
        adapter._writable(self.workspace)
        with _exclusive(self.workspace), self.ledger._transaction():
            packet = self._packet(preparation_ref)
            job, ledger = digest(packet), self.ledger
            at = ledger._now()
            prior = ledger.db.execute('SELECT state FROM jobs WHERE id=?', (job,)).fetchone()
            if prior and prior['state'] != 'preparation_abandoned':
                raise JobError('Existing attempt must be recovered, not redispatched')
            if ledger.db.execute("SELECT 1 FROM attempts WHERE state IN ('running','unknown','cancel_requested')").fetchone():
                raise JobError('Active or unresolved attempt reserves the shared slot')
            count = ledger.db.execute('SELECT COUNT(*) FROM attempts WHERE job_id=?', (job,)).fetchone()[0]
            if count >= packet['max_attempts']: raise JobError('Attempt budget exhausted')
            if not prior:
                ledger.db.execute('INSERT INTO jobs(id,packet) VALUES(?,?)', (job, canonical(packet)))
            token = secrets.token_hex(24)
            cur = ledger.db.execute('INSERT INTO attempts(job_id,token_hash,started,expires,state) VALUES(?,?,?,?,?)',
                                    (job, digest(token), at, at + packet['lease_seconds'], 'running'))
            claim = {'job_id': job, 'attempt_id': cur.lastrowid, 'lease_token': token,
                     'expires': at + packet['lease_seconds']}
            path = ev.contained(self.workspace.root, self._prefix(claim))
            # A crash before DB commit leaves a held orphan, never an overwritten checkpoint.
            path.mkdir(parents=True, exist_ok=False)
            ev.write_new(path / 'checkpoint.json', ev.encoded({'claim': claim, 'packet': packet}))
            ledger.db.execute("UPDATE jobs SET state='running' WHERE id=?", (job,))
            ledger._event(job, 'author-preparation-reserved-no-dispatch', {'attempt_id': cur.lastrowid, **ev.FLAGS}, at)
        return claim

    def _bound(self, claim):
        ev.keys(claim, {'job_id', 'attempt_id', 'lease_token', 'expires'})
        row = self.ledger._attempt(claim)
        packet = self.ledger.status(claim['job_id'])['packet']
        if packet.get('kind') != KIND or digest(packet) != claim['job_id']:
            raise JobError('Not an author preparation attempt')
        checkpoint = ev.decode(ev.read_raw(ev.contained(self.workspace.root, self._prefix(claim) + '/checkpoint.json')))
        if checkpoint != {'claim': claim, 'packet': packet} or row['expires'] != claim['expires']:
            raise JobError('Checkpoint identity mismatch')
        # Recovery of frozen attempts must remain possible after dependencies change.
        return row, packet

    def observe(self, claim, observation):
        """Retain bounded supplied evidence; never use it to free a live slot."""
        raw = ev.encoded(observation)
        if len(raw) > ev.MAX_RECORD: raise ValueError('Observation too large')
        with _exclusive(self.workspace), self.ledger._transaction():
            row, _ = self._bound(claim)
            if row['state'] not in {'running', 'unknown', 'cancel_requested'}:
                raise JobError('Terminal preparation is immutable')
            at = self.ledger._now()
            ref = adapter._save(self.workspace, self._prefix(claim) + '/observations/' + hashlib.sha256(raw).hexdigest() + '.json', raw)
            self.ledger.db.execute("UPDATE attempts SET state='unknown' WHERE id=?", (row['id'],))
            self.ledger.db.execute("UPDATE jobs SET state='held_unknown' WHERE id=?", (row['job_id'],))
            self.ledger._event(row['job_id'], 'author-unverified-observation',
                               {'attempt_id': row['id'], 'observation': ref, **ev.FLAGS}, at)
        return {'status': 'held-unknown', 'observation': ref, **ev.FLAGS}

    def abandon_unstarted(self, claim):
        """Release only this implementation's preparation with no worker evidence.

        This cannot reconcile a launched worker. Unknown/cancelled/expired states
        and even orphaned observation files require qualified recovery instead.
        """
        with _exclusive(self.workspace), self.ledger._transaction():
            row, _ = self._bound(claim)
            at = self.ledger._now()
            path = ev.contained(self.workspace.root, self._prefix(claim))
            if (row['state'] != 'running' or row['expires'] <= at
                    or {p.name for p in path.iterdir()} != {'checkpoint.json'}):
                raise JobError('Only pristine, unexpired, unstarted preparation can be abandoned')
            self.ledger.db.execute("UPDATE attempts SET state='preparation_abandoned' WHERE id=?", (row['id'],))
            self.ledger.db.execute("UPDATE jobs SET state='preparation_abandoned' WHERE id=?", (row['job_id'],))
            self.ledger._event(row['job_id'], 'author-preparation-abandoned-no-dispatch', {'attempt_id': row['id']}, at)
        return {'status': 'preparation-abandoned', 'author_code_executed': False, **ev.FLAGS}

    def status(self, claim):
        row, packet = self._bound(claim)
        return {'job_id': row['job_id'], 'attempt_id': row['id'], 'state': row['state'],
                'preparation': packet['preparation'], 'live_backend_available': False, **ev.FLAGS}
