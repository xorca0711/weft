"""Versioned RQ discovery context, never an editable copy of Ravel's authority."""
from __future__ import annotations
import hashlib
import json
import re
from urllib.parse import unquote
from .identity import digest
from .validation import ValidationError, git_read, safe_relative, verify_ravel


def build_context(repo, lock, rq_ids=None):
    verify_ravel(repo, lock)
    commit = lock["commit"]
    registry = json.loads(git_read(repo, "show", commit + ":analysis/research/registry.json"))
    questions = {q["id"]: q for q in registry["questions"]}
    requested = list(questions) if rq_ids is None else list(dict.fromkeys(rq_ids))
    if not requested:
        raise ValidationError("At least one registered RQ is required")
    if set(requested) - questions.keys():
        raise ValidationError("Requested question is absent from the pinned Ravel registry")
    guides = {q["question"]: q for q in registry.get("question_guides", [])}
    packets, blobs = [], {}
    for qid in requested:
        question = questions[qid]
        path = unquote(question["card"].split("#", 1)[0])
        if not safe_relative(path):
            raise ValidationError("Unsafe registry card path")
        if path not in blobs:
            blobs[path] = git_read(repo, "show", f"{commit}:{path}")
        blob = blobs[path]
        text = blob.decode("utf-8")
        match = re.search(rf"^### {re.escape(qid)}[. :].*?(?=^### A\d+[. :]|\Z)", text, re.M | re.S)
        if not match:
            raise ValidationError(f"Canonical section could not be resolved for {qid}")
        section = match.group().strip()
        title = section.splitlines()[0].removeprefix("### ")
        # A discovery packet is deliberately not a full scientific review.
        packet = {"rq_id": qid, "title": title, "canonical_section": section,
                  "section_sha256": hashlib.sha256(section.encode()).hexdigest(),
                  "card": question["card"], "card_blob_sha256": hashlib.sha256(blob).hexdigest(),
                  "dossier": question["dossier"], "evidence_locators": question.get("evidence", []),
                  "guide": guides.get(qid), "ravel_commit": commit,
                  "scope": "discovery-context; current results and amendments still require reading"}
        packet["context_sha256"] = digest(packet)
        packets.append(packet)
    return {"schema_version": 1, "repository": lock["repository"], "ravel_commit": commit,
            "questions": packets, "catalog_sha256": digest(packets)}
