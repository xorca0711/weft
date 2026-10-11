"""Single-writer synthetic-job ledger. No scientific execution or remote dispatch."""
from __future__ import annotations

from contextlib import contextmanager
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import secrets
import sqlite3
import time

from .identity import digest
from .validation import safe_relative


class JobError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def validate_packet(packet):
    required = {"schema_version", "kind", "paper_version_sha256", "context_sha256",
                "policy_sha256", "contract_sha256", "executor_sha256", "inputs",
                "max_attempts", "lease_seconds"}
    if not isinstance(packet, dict) or set(packet) != required:
        raise JobError("Exact versioned job packet required")
    if type(packet["schema_version"]) is not int or packet["schema_version"] != 1:
        raise JobError("Unsupported packet schema")
    if packet["kind"] != "synthetic-qualification":
        raise JobError("Only synthetic qualification is implemented; science remains held")
    for key in required:
        if key.endswith("sha256") and (not isinstance(packet[key], str) or not re.fullmatch(r"[0-9a-f]{64}", packet[key])):
            raise JobError("Invalid identity hash: " + key)
    for key, cap in (("max_attempts", 3), ("lease_seconds", 300)):
        if type(packet[key]) is not int or not 1 <= packet[key] <= cap:
            raise JobError("Invalid synthetic bound: " + key)
    if not isinstance(packet["inputs"], list) or not 1 <= len(packet["inputs"]) <= 32:
        raise JobError("Nonempty immutable input inventory required")
    names = set()
    for item in packet["inputs"]:
        if not isinstance(item, dict) or set(item) != {"path", "sha256", "bytes"}:
            raise JobError("Invalid input record")
        if (not safe_relative(item["path"]) or item["path"] in names
                or PurePosixPath(item["path"]).as_posix() != item["path"]):
            raise JobError("Unsafe/duplicate input path")
        names.add(item["path"])
        if not isinstance(item["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", item["sha256"]):
            raise JobError("Invalid input hash")
        if type(item["bytes"]) is not int or not 0 <= item["bytes"] <= 1048576:
            raise JobError("Synthetic inputs are bounded at 1 MiB each")
    if sum(item["bytes"] for item in packet["inputs"]) > 1048576:
        raise JobError("Synthetic input total exceeds 1 MiB")
    # Ignore manifest ordering, never identity or parameter changes.
    return {**packet, "inputs": sorted(packet["inputs"], key=lambda x: x["path"])}


def verify_files(root, records):
    root = Path(root).resolve(strict=True)
    for item in records:
        if not safe_relative(item["path"]):
            raise JobError("Unsafe artifact path")
        path = root / item["path"]
        if any(p.is_symlink() for p in [path, *path.parents] if p != root and root in p.parents):
            raise JobError("Symlink artifact rejected")
        resolved = path.resolve(strict=True)
        if not resolved.is_relative_to(root) or not resolved.is_file():
            raise JobError("Artifact escapes root or is not a regular file")
        if resolved.stat().st_size != item["bytes"]:
            raise JobError("Artifact size drift: " + item["path"])
        with resolved.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual != item["sha256"]:
            raise JobError("Artifact hash drift: " + item["path"])


class JobLedger:
    """Transactional materialized status plus append-only transition events.

    This coordinates cooperating clients of ONE SQLite database. It is not a
    distributed lock service, a sandbox, a usage meter or a scientific gate.
    """
    def __init__(self, path, *, clock=time.time):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.clock = clock
        self.db = sqlite3.connect(self.path, timeout=15, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            PRAGMA foreign_keys=ON;
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY, packet TEXT NOT NULL,
                state TEXT NOT NULL DEFAULT 'queued');
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT NOT NULL REFERENCES jobs(id), token_hash TEXT NOT NULL,
                started REAL NOT NULL, expires REAL NOT NULL, state TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT, job_id TEXT NOT NULL,
                at REAL NOT NULL, action TEXT NOT NULL, evidence TEXT NOT NULL);
            CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON events
                BEGIN SELECT RAISE(ABORT, 'Events are append-only'); END;
            CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON events
                BEGIN SELECT RAISE(ABORT, 'Events are append-only'); END;
            CREATE TRIGGER IF NOT EXISTS packet_no_update BEFORE UPDATE OF packet ON jobs
                BEGIN SELECT RAISE(ABORT, 'Packets are immutable'); END;
        """)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.db.close()

    def _now(self):
        value = float(self.clock())
        if not math.isfinite(value):
            raise JobError("Invalid clock")
        previous = self.db.execute("SELECT MAX(at) FROM events").fetchone()[0]
        if previous is not None and value < previous:
            raise JobError("Clock moved backwards; reconcile before dispatch")
        return value

    @contextmanager
    def _transaction(self):
        self.db.execute("BEGIN IMMEDIATE")
        try:
            yield
        except BaseException:
            self.db.rollback()
            raise
        else:
            self.db.commit()

    def _event(self, job, action, evidence, at):
        self.db.execute("INSERT INTO events(job_id,at,action,evidence) VALUES(?,?,?,?)",
                        (job, at, action, canonical(evidence)))

    def submit(self, packet):
        packet = validate_packet(packet)
        key = digest(packet)
        with self._transaction():
            at = self._now()
            found = self.db.execute("SELECT id FROM jobs WHERE id=?", (key,)).fetchone()
            if not found:
                self.db.execute("INSERT INTO jobs(id,packet) VALUES(?,?)", (key, canonical(packet)))
                self._event(key, "submitted", {"packet_sha256": key}, at)
        return key

    def status(self, job):
        row = self.db.execute("SELECT id,state,packet FROM jobs WHERE id=?", (job,)).fetchone()
        if row is None:
            raise JobError("Unknown job")
        return {"id": row["id"], "state": row["state"], "packet": json.loads(row["packet"])}

    def claim(self, job, *, inputs_root, current_context_sha256, current_policy_sha256):
        with self._transaction():
            at = self._now()
            current = self.status(job)
            packet = current["packet"]
            if current["state"] not in {"queued", "failed", "cancelled"}:
                raise JobError("Job is not dispatchable")
            if (packet["context_sha256"] != current_context_sha256
                    or packet["policy_sha256"] != current_policy_sha256):
                raise JobError("Stale context or policy requires a new packet")
            verify_files(inputs_root, packet["inputs"])
            # Unknown/cancel-requested attempts continue to reserve the only slot.
            if self.db.execute("SELECT 1 FROM attempts WHERE state IN ('running','unknown','cancel_requested')").fetchone():
                raise JobError("Active or unresolved attempt reserves the execution slot")
            count = self.db.execute("SELECT COUNT(*) FROM attempts WHERE job_id=?", (job,)).fetchone()[0]
            if count >= packet["max_attempts"]:
                raise JobError("Attempt budget exhausted")
            token = secrets.token_hex(24)
            cur = self.db.execute("INSERT INTO attempts(job_id,token_hash,started,expires,state) VALUES(?,?,?,?,?)",
                                  (job, digest(token), at, at + packet["lease_seconds"], "running"))
            self.db.execute("UPDATE jobs SET state='running' WHERE id=?", (job,))
            self._event(job, "claimed", {"attempt_id": cur.lastrowid}, at)
            return {"job_id": job, "attempt_id": cur.lastrowid, "lease_token": token,
                    "expires": at + packet["lease_seconds"]}

    def expire(self):
        with self._transaction():
            at = self._now()
            rows = self.db.execute("SELECT id,job_id FROM attempts WHERE state IN ('running','cancel_requested') AND expires<=?", (at,)).fetchall()
            for row in rows:
                self.db.execute("UPDATE attempts SET state='unknown' WHERE id=?", (row["id"],))
                self.db.execute("UPDATE jobs SET state='held_unknown' WHERE id=?", (row["job_id"],))
                self._event(row["job_id"], "lease-expired-outcome-unknown", {"attempt_id": row["id"]}, at)
            return len(rows)

    def cancel(self, job):
        with self._transaction():
            at = self._now()
            state = self.status(job)["state"]
            if state == "queued":
                self.db.execute("UPDATE jobs SET state='cancelled' WHERE id=?", (job,))
            elif state == "running":
                self.db.execute("UPDATE jobs SET state='cancel_requested' WHERE id=?", (job,))
                self.db.execute("UPDATE attempts SET state='cancel_requested' WHERE job_id=? AND state='running'", (job,))
            else:
                raise JobError("No cancellable queued or running job")
            self._event(job, "cancel-requested", {"previous_state": state}, at)
        # No termination claim: a worker receipt must reconcile the process.

    def reconcile(self, attempt_id, token, *, outcome, receipt_ref):
        if outcome not in {"failed", "cancelled"}:
            raise JobError("Success needs verified artifacts; completion is not implemented")
        if not re.fullmatch(r"[0-9a-f]{64}", str(receipt_ref)):
            raise JobError("A content-addressed terminal receipt is required")
        with self._transaction():
            at = self._now()
            row = self.db.execute("SELECT * FROM attempts WHERE id=?", (attempt_id,)).fetchone()
            if row is None or not secrets.compare_digest(row["token_hash"], digest(token)):
                raise JobError("Attempt identity/lease mismatch")
            if row["state"] not in {"running", "unknown", "cancel_requested"}:
                raise JobError("Terminal attempt cannot be rewritten")
            self.db.execute("UPDATE attempts SET state=? WHERE id=?", (outcome, attempt_id))
            self.db.execute("UPDATE jobs SET state=? WHERE id=?", (outcome, row["job_id"]))
            self._event(row["job_id"], "terminal-report", {"attempt_id": attempt_id,
                "outcome": outcome, "receipt_sha256": receipt_ref,
                "process_termination_independently_verified": False}, at)
        # Cooperative synthetic API only: receipt reference is not authentication
        # or proof of actual termination. Never use this API to dispatch science.
