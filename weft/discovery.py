"""Persistent discovery receipts and a conservative paper-to-RQ review buffer."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import uuid

from .europe_pmc import EuropePMC, SourceError, date_window
from .identity import deduplicate, digest, provider_relations


def now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value):
    # Every run owns new paths; fail instead of overwriting prior artifacts.
    with Path(path).open("x", encoding="utf-8", newline="\n") as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


class Store:
    def __init__(self, root):
        self.root = Path(root).resolve()
        if ".git" in self.root.parts:
            raise ValueError("A discovery store cannot live in Git internals")
        self.root.mkdir(parents=True, exist_ok=True)
        marker = self.root / "WEFT_STORE.json"
        if not marker.exists():
            if any(self.root.iterdir()):
                raise ValueError("Existing nonempty directory is not a Weft discovery store")
            write_json(marker, {"kind": "weft-discovery", "schema_version": 1})
        elif json.loads(marker.read_text(encoding="utf-8")) != {"kind": "weft-discovery", "schema_version": 1}:
            raise ValueError("Unexpected discovery store marker")
        self.db = sqlite3.connect(self.root / "catalog.sqlite", timeout=30)
        self.db.row_factory = sqlite3.Row
        self.db.executescript("""
            PRAGMA foreign_keys=ON;
            CREATE TABLE IF NOT EXISTS runs(
                id TEXT PRIMARY KEY, created TEXT NOT NULL, finished TEXT, stream_key TEXT NOT NULL,
                status TEXT NOT NULL, since_date TEXT NOT NULL, until_date TEXT NOT NULL,
                query TEXT NOT NULL, directory TEXT NOT NULL, receipt_json TEXT);
            CREATE TABLE IF NOT EXISTS observations(
                run_id TEXT NOT NULL REFERENCES runs(id), provider_id TEXT NOT NULL,
                raw_sha TEXT NOT NULL, raw_json TEXT NOT NULL,
                UNIQUE(run_id, provider_id, raw_sha));
            CREATE TABLE IF NOT EXISTS watermarks(
                stream_key TEXT PRIMARY KEY, until_date TEXT NOT NULL, run_id TEXT NOT NULL REFERENCES runs(id));
            CREATE TABLE IF NOT EXISTS candidates(
                id TEXT PRIMARY KEY, paper_key TEXT NOT NULL, rq_id TEXT NOT NULL,
                context_sha TEXT NOT NULL, evidence_sha TEXT NOT NULL, status TEXT NOT NULL,
                current INTEGER NOT NULL, proposal_json TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS candidate_runs(
                candidate_id TEXT NOT NULL REFERENCES candidates(id), run_id TEXT NOT NULL REFERENCES runs(id),
                UNIQUE(candidate_id, run_id));
            CREATE TABLE IF NOT EXISTS events(
                id INTEGER PRIMARY KEY, candidate_id TEXT NOT NULL REFERENCES candidates(id),
                created TEXT NOT NULL, action TEXT NOT NULL, record_json TEXT NOT NULL);
        """)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.db.close()

    def watermark(self, key):
        row = self.db.execute("SELECT until_date FROM watermarks WHERE stream_key=?", (key,)).fetchone()
        return row[0] if row else None

    def candidates(self):
        return [dict(row) for row in self.db.execute(
            "SELECT id,paper_key,rq_id,status,current,context_sha,evidence_sha FROM candidates ORDER BY paper_key,rq_id,id")]

    def queue(self, groups, context, run_id):
        current_q = {q["rq_id"]: q for q in context["questions"]}
        ids = []
        with self.db:
            # Refresh invalidates all old context links for these RQs, even on a zero-hit run.
            for qid, question in current_q.items():
                stale = self.db.execute(
                    "SELECT id FROM candidates WHERE rq_id=? AND current=1 AND context_sha<>?",
                    (qid, question["context_sha256"])).fetchall()
                for row in stale:
                    self.db.execute("UPDATE candidates SET current=0,status='stale' WHERE id=?", (row[0],))
                    self.db.execute("INSERT INTO events(candidate_id,created,action,record_json) VALUES(?,?,?,?)",
                                    (row[0], now(), "context-invalidated", json.dumps({"run_id": run_id})))
            for group in groups:
                for qid, question in current_q.items():
                    identity = [group["paper_key"], qid, question["context_sha256"], group["evidence_sha256"]]
                    candidate_id = digest(identity)
                    # Previously reviewed links cannot carry across changed sources or RQ context.
                    old_rows = self.db.execute(
                        "SELECT id FROM candidates WHERE paper_key=? AND rq_id=? AND current=1 AND id<>?",
                        (group["paper_key"], qid, candidate_id)).fetchall()
                    for row in old_rows:
                        self.db.execute("UPDATE candidates SET current=0,status='stale' WHERE id=?", (row[0],))
                        self.db.execute("INSERT INTO events(candidate_id,created,action,record_json) VALUES(?,?,?,?)",
                                        (row[0], now(), "invalidated", json.dumps({"replacement": candidate_id})))
                    reasons = []
                    if group["identity_status"] != "resolved":
                        reasons.append("identity-conflict")
                    if any(r["integrity_flags"] for r in group["records"]):
                        reasons.append("provider-integrity-flag")
                    if any(r["identity_warning"] for r in group["records"]):
                        reasons.append("identity-warning")
                    # A provider can revise strong identifiers between separate searches.
                    # Do not silently transfer a reading decision to a different paper key.
                    peers = self.db.execute(
                        "SELECT id,proposal_json FROM candidates WHERE rq_id=? AND current=1 AND paper_key<>?",
                        (qid, group["paper_key"])).fetchall()
                    for peer in peers:
                        proposal_old = json.loads(peer["proposal_json"])
                        if set(proposal_old["identifiers"]) & set(group["identifiers"]):
                            reasons.append("cross-run-identity-change")
                            proposal_old["hold_reasons"] = sorted(set(proposal_old["hold_reasons"] + ["cross-run-identity-change"]))
                            self.db.execute("UPDATE candidates SET status='held',proposal_json=? WHERE id=?",
                                            (json.dumps(proposal_old), peer["id"]))
                            self.db.execute("INSERT INTO events(candidate_id,created,action,record_json) VALUES(?,?,?,?)",
                                            (peer["id"], now(), "identity-held", json.dumps({"run_id": run_id})))
                    reasons = sorted(set(reasons))
                    status = "held" if reasons else "pending_review"
                    proposal = {"paper_key": group["paper_key"], "identifiers": group["identifiers"],
                                "titles": sorted({r["title"] for r in group["records"]}),
                                "rq_id": qid, "rq_title": question["title"],
                                "basis": "retrieved by an RQ-associated query; relevance is not yet established",
                                "source_scope": "metadata-retrieval-only", "hold_reasons": reasons,
                                "claim_proposals": [], "supports_rq": None,
                                "study_independence": "not-assessed", "scientific_execution_allowed": False}
                    existing = self.db.execute("SELECT current,proposal_json FROM candidates WHERE id=?", (candidate_id,)).fetchone()
                    if existing:
                        # Preserve attributable cross-record observations on exact
                        # replay, even when this record carries its own hold flag.
                        retained = json.loads(existing["proposal_json"])
                        if "provider_relations" in retained:
                            proposal["provider_relations"] = retained["provider_relations"]
                        if "provider-related-integrity-flag" in retained["hold_reasons"]:
                            reasons = sorted(set(reasons + ["provider-related-integrity-flag"]))
                            proposal["hold_reasons"] = reasons
                            status = "held"
                    self.db.execute("INSERT OR IGNORE INTO candidates VALUES(?,?,?,?,?,?,?,?)",
                                    (candidate_id, group["paper_key"], qid, question["context_sha256"],
                                     group["evidence_sha256"], status, 1, json.dumps(proposal)))
                    if existing and not existing[0]:
                        self.db.execute("UPDATE candidates SET current=1,status=? WHERE id=?", (status, candidate_id))
                        self.db.execute("INSERT INTO events(candidate_id,created,action,record_json) VALUES(?,?,?,?)",
                                        (candidate_id, now(), "reopened-for-review", json.dumps({"run_id": run_id})))
                    if existing and reasons:
                        self.db.execute("UPDATE candidates SET status='held',proposal_json=? WHERE id=?",
                                        (json.dumps(proposal), candidate_id))
                    self.db.execute("INSERT OR IGNORE INTO candidate_runs VALUES(?,?)", (candidate_id, run_id))
                    ids.append(candidate_id)
            self._reconcile_relations(run_id)
        return ids

    def _reconcile_relations(self, run_id):
        """Join explicit metadata links, not publication identities or scientific claims.

        Retained observations make a notice effective whether it precedes or follows
        the original's discovery. An absent notice on a later response is not an
        authenticated withdrawal, so it cannot silently clear the integrity hold.
        The caller owns the transaction; no separate schema or historical rewrite.
        """
        candidates = self.db.execute("SELECT * FROM candidates WHERE current=1").fetchall()
        by_identifier = {}
        for row in candidates:
            for identifier in json.loads(row["proposal_json"])["identifiers"]:
                by_identifier.setdefault(identifier, set()).add(row["id"])
        related = {row["id"]: {} for row in candidates}
        seen = set()
        for observation in self.db.execute("SELECT rowid,* FROM observations ORDER BY rowid"):
            for relation in provider_relations(json.loads(observation["raw_json"])):
                key = digest([observation["raw_sha"], relation["relation_sha256"]])
                if key in seen:
                    continue
                seen.add(key)
                evidence = {"evidence_sha256": key, "source_run": observation["run_id"],
                            "raw_sha256": observation["raw_sha"], "relation": relation}
                identifiers = relation["source_identifiers"] + relation["target_identifiers"]
                affected = set().union(*(by_identifier.get(i, set()) for i in identifiers))
                for candidate_id in affected:
                    related[candidate_id][key] = evidence
        for row in candidates:
            evidence = sorted(related[row["id"]].values(), key=lambda r: r["evidence_sha256"])
            if not evidence:
                continue
            proposal = json.loads(row["proposal_json"])
            concerns = any(e["relation"]["integrity_review_required"] for e in evidence)
            reasons = set(proposal["hold_reasons"])
            if concerns:
                reasons.add("provider-related-integrity-flag")
            status = "held" if concerns else row["status"]
            if (proposal.get("provider_relations") == evidence and
                    proposal["hold_reasons"] == sorted(reasons) and row["status"] == status):
                continue
            proposal["provider_relations"] = evidence
            proposal["hold_reasons"] = sorted(reasons)
            self.db.execute("UPDATE candidates SET status=?,proposal_json=? WHERE id=?",
                            (status, json.dumps(proposal), row["id"]))
            self.db.execute("INSERT INTO events(candidate_id,created,action,record_json) VALUES(?,?,?,?)",
                (row["id"], now(), "provider-relation-held" if concerns else "provider-relation-observed",
                 json.dumps({"run_id": run_id, "previous_status": row["status"],
                             "relation_evidence": [e["evidence_sha256"] for e in evidence],
                             "scope": "metadata integrity review; prior decisions retained; no scientific determination"})))

    def review(self, candidate_id, record):
        if record.get("decision") not in {"read_next", "hold", "reject"}:
            raise ValueError("Only reading-priority decisions are implemented; no claim validation or acceptance")
        if record.get("actor_kind") not in {"human", "agent"} or not record.get("actor"):
            raise ValueError("An explicit self-reported review actor is required")
        if not record.get("reason") or not isinstance(record.get("evidence_refs"), list) or not record["evidence_refs"]:
            raise ValueError("Review reason and evidence references are required")
        with self.db:
            row = self.db.execute("SELECT * FROM candidates WHERE id=?", (candidate_id,)).fetchone()
            if not row or not row["current"]:
                raise ValueError("Missing or stale candidate")
            if record.get("context_sha256") != row["context_sha"] or record.get("evidence_sha256") != row["evidence_sha"]:
                raise ValueError("Review does not bind the current RQ and paper metadata snapshots")
            if record["decision"] == "read_next" and json.loads(row["proposal_json"])["hold_reasons"]:
                raise ValueError("Held identity/integrity flags require resolution through refreshed source evidence")
            status = {"read_next": "read_next", "hold": "held", "reject": "rejected"}[record["decision"]]
            self.db.execute("INSERT INTO events(candidate_id,created,action,record_json) VALUES(?,?,?,?)",
                            (candidate_id, now(), "reading-triage", json.dumps(record)))
            self.db.execute("UPDATE candidates SET status=? WHERE id=?", (status, candidate_id))
        return {"candidate_id": candidate_id, "status": status, "claim_validated": False,
                "actor_identity_verified": False, "scientific_execution_allowed": False}


def stream_key(query, field, context):
    return digest({"query": query, "date_field": field, "rq_context": context["catalog_sha256"],
                   "provider": "EuropePMC", "result_type": "core", "schema_version": 1})


def discover(store, context, query, *, since, until, date_field="FIRST_IDATE",
             max_records=200, page_size=100, overlap_days=7, client=None):
    key = stream_key(query, date_field, context)
    previous = store.watermark(key)
    if type(overlap_days) is not int or not 0 <= overlap_days <= 90:
        raise ValueError("Overlap must be between zero and 90 days")
    if since is None:
        if previous is None:
            raise ValueError("Initial discovery needs an explicit --since date")
        since = (date.fromisoformat(previous) - timedelta(days=overlap_days)).isoformat()
    full_query = date_window(query, date_field, since, until)
    run_id = "search-" + uuid.uuid4().hex
    directory = store.root / run_id
    directory.mkdir()
    with store.db:
        store.db.execute("INSERT INTO runs VALUES(?,?,?,?,?,?,?,?,?,?)",
                         (run_id, now(), None, key, "running", since, until, full_query, run_id, None))
    write_json(directory / "rq-context.json", context)
    pages = []

    def on_page(meta, body):
        filename = f"page-{meta['page']:04d}.json"
        with (directory / filename).open("xb") as handle:
            handle.write(body)
        page = {**meta, "file": filename, "sha256": hashlib.sha256(body).hexdigest(), "bytes": len(body)}
        write_json(directory / f"page-{meta['page']:04d}.receipt.json", page)
        pages.append(page)
        if not meta.get("malformed"):
            data = json.loads(body)["resultList"]["result"]
            with store.db:
                for raw in data:
                    store.db.execute("INSERT OR IGNORE INTO observations VALUES(?,?,?,?)",
                                     (run_id, f"epmc:{raw['source']}:{raw['id']}", digest(raw), json.dumps(raw)))

    receipt = {"schema_version": 1, "run_id": run_id, "created_at": now(), "provider": "EuropePMC",
               "query": full_query, "base_query": query, "date_field": date_field,
               "since": since, "until": until, "context_sha256": context["catalog_sha256"],
               "ravel_commit": context["ravel_commit"], "previous_watermark": previous,
               "max_records": max_records, "page_size": page_size, "pages": pages,
               "scientific_execution": False, "watermark_advanced": False}
    try:
        result = (client or EuropePMC()).search(full_query, on_page, page_size=page_size, max_records=max_records)
        grouped = deduplicate(result["records"])
        write_json(directory / "deduplication.json", grouped)
        candidate_ids = store.queue(grouped["groups"], context, run_id)
        receipt.update({"status": result["status"], "hit_count": result["hit_count"],
                        "retrieved_records": len(result["records"]), "warnings": result["warnings"],
                        "resolved_work_count": grouped["resolved_work_count"],
                        "identity_conflicts": len(grouped["identity_conflicts"]),
                        "possible_version_groups": len(grouped["possible_versions_by_title"]),
                        "candidate_ids": candidate_ids, "next_cursor": result["next_cursor"],
                        "deduplication_sha256": digest(grouped)})
    except Exception as exc:
        receipt.update({"status": "error", "error_type": type(exc).__name__, "error": str(exc),
                        "transport_attempts": getattr(exc, "attempts", [])})
    # The DB receipt and watermark commit together; failure/truncation never advances a cutoff.
    receipt["finished_at"] = now()
    with store.db:
        store.db.execute("BEGIN IMMEDIATE")
        current_cutoff = store.watermark(key)
        next_date = max(until, current_cutoff) if current_cutoff else until
        covers_gap = current_cutoff is None or date.fromisoformat(since) <= date.fromisoformat(current_cutoff) + timedelta(days=1)
        if receipt["status"] == "complete" and not covers_gap:
            receipt["warnings"].append("window-gap-watermark-not-advanced")
        if receipt["status"] == "complete" and covers_gap:
            receipt["watermark_advanced"] = current_cutoff is None or next_date > current_cutoff
        write_json(directory / "receipt.json", receipt)
        if receipt["status"] == "complete" and covers_gap:
            store.db.execute("INSERT INTO watermarks VALUES(?,?,?) ON CONFLICT(stream_key) DO UPDATE SET until_date=excluded.until_date,run_id=excluded.run_id WHERE excluded.until_date > watermarks.until_date",
                             (key, next_date, run_id))
        store.db.execute("UPDATE runs SET status=?,finished=?,receipt_json=? WHERE id=?",
                         (receipt["status"], receipt["finished_at"], json.dumps(receipt), run_id))
    return receipt


def verify_run(store, run_id):
    row = store.db.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
    if not row or not row["receipt_json"]:
        raise ValueError("Run is missing or interrupted; repeat its saved window as a new attempt")
    receipt = json.loads(row["receipt_json"])
    directory = store.root / row["directory"]
    for page in receipt["pages"]:
        body = (directory / page["file"]).read_bytes()
        if hashlib.sha256(body).hexdigest() != page["sha256"]:
            raise ValueError("Raw page was changed after retrieval")
    if json.loads((directory / "receipt.json").read_text(encoding="utf-8")) != receipt:
        raise ValueError("Database and file receipts differ")
    context = json.loads((directory / "rq-context.json").read_text(encoding="utf-8"))
    if digest(context["questions"]) != receipt["context_sha256"]:
        raise ValueError("RQ context artifact changed")
    if receipt.get("deduplication_sha256"):
        grouped = json.loads((directory / "deduplication.json").read_text(encoding="utf-8"))
        if digest(grouped) != receipt["deduplication_sha256"]:
            raise ValueError("Deduplication artifact changed")
    return {"ok": True, "run_id": run_id, "status": receipt["status"],
            "verified_pages": len(receipt["pages"]), "scientific_validation": False}
