"""Deterministic scaffold checks and read-only verification of pinned Git blobs."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
from urllib.parse import unquote, urlsplit


class ValidationError(ValueError):
    pass


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def safe_relative(path: str) -> bool:
    return (isinstance(path, str) and bool(path) and "\\" not in path
            and ":" not in path and not PurePosixPath(path).is_absolute()
            and all(part not in ("", ".", "..") for part in path.split("/")))


def validate_manifest(lock: dict) -> None:
    if lock.get("schema_version") != 1:
        raise ValidationError("Unsupported Ravel lock schema")
    if not re.fullmatch(r"[0-9a-f]{40}", lock.get("commit", "")):
        raise ValidationError("Ravel commit must be a full lowercase Git SHA")
    if lock.get("repository") != "https://github.com/xorca0711/ravel.git":
        raise ValidationError("Unexpected Ravel repository identity")
    ids = lock.get("question_ids", [])
    if (not ids or len(ids) != len(set(ids))
            or any(not re.fullmatch(r"A\d+", q) for q in ids)):
        raise ValidationError("Missing, duplicate or malformed Ravel question IDs")
    entries = lock.get("files", [])
    if not entries:
        raise ValidationError("No pinned Ravel files")
    seen = set()
    for entry in entries:
        path = entry.get("path")
        if not safe_relative(path) or path in seen:
            raise ValidationError(f"Unsafe or duplicate source path: {path}")
        seen.add(path)
        if not re.fullmatch(r"[0-9a-f]{64}", entry.get("sha256", "")):
            raise ValidationError(f"Invalid SHA-256: {path}")
    if "analysis/research/registry.json" not in seen:
        raise ValidationError("Ravel registry must be pinned")


def validate_project(root: Path) -> dict:
    required = ["README.md", "AGENTS.md", "AI_CONTEXT.md", "PROGRESS.md",
                "DEVELOPMENT.md", "docs/IMPLEMENTATION_PLAN.md", "docs/GATES.md",
                "docs/AGENT_WORKFLOW.md", "docs/RAVEL_CONNECTION.md",
                "docs/PILOT_CHOI_2020.md", "docs/EVALUATION.md"]
    for rel in required:
        if not (root / rel).is_file():
            raise ValidationError(f"Missing required file: {rel}")
    project = read_json(root / "configs/project.json")
    policy = read_json(root / "configs/policy.json")
    pilot = read_json(root / "configs/pilot.json")
    sources = read_json(root / "configs/sources.json")
    for config in (project, policy, pilot, sources):
        if config.get("schema_version") != 1:
            raise ValidationError("Unsupported configuration schema")
    # Activation requires implementing and reviewing the runtime first.
    for flag in ("enabled", "automations_enabled", "scientific_execution_enabled",
                 "automatic_merge_enabled", "canonical_rq_registration_enabled"):
        if policy.get(flag) is not False:
            raise ValidationError(f"Unimplemented capability cannot be activated: {flag}")
    if sources.get("enabled") is not False:
        raise ValidationError("Live source adapter is not implemented")
    if policy.get("journal_priority_is_eligibility") is not False:
        raise ValidationError("Journal priority must not become scientific eligibility")
    if not sources.get("broad_search_required"):
        raise ValidationError("Broad search stream is required")
    limits = policy.get("limits", {})
    expected = {"records_per_search", "full_reads_per_batch", "active_scientific_jobs",
                "scientific_wall_hours", "new_download_gib", "model_usd_per_job",
                "model_usd_per_month"}
    if set(limits) != expected or any(type(v) not in (int, float) or v <= 0 for v in limits.values()):
        raise ValidationError("Explicit positive operational limits are required")
    if project.get("pilot_id") != pilot.get("pilot_id"):
        raise ValidationError("Pilot identity drift")
    if (pilot.get("status") != "planned-not-run"
            or pilot.get("exposure") != "historical-outcomes-known"
            or pilot.get("population_inference_allowed") is not False
            or pilot.get("historical_scripts_may_run_in_place") is not False):
        raise ValidationError("Pilot status, exposure or inference boundary drift")
    if not safe_relative(project.get("ravel_lock")):
        raise ValidationError("Unsafe Ravel lock path")
    lock = read_json(root / project["ravel_lock"])
    validate_manifest(lock)
    if set(pilot.get("ravel_question_ids", [])) != set(lock["question_ids"]):
        raise ValidationError("Pilot question IDs differ from the connection lock")
    checked_links = 0
    for path in [root / n for n in required] + [root / "docs/SOURCES.md"]:
        content = path.read_text(encoding="utf-8")
        for link in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", content):
            target = urlsplit(link)
            if target.scheme or not target.path:
                continue
            resolved = (path.parent / unquote(target.path)).resolve()
            if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                raise ValidationError(f"Missing/escaping local link in {path.name}: {link}")
            checked_links += 1
    if "```mermaid" not in (root / "README.md").read_text(encoding="utf-8"):
        raise ValidationError("README workflow diagram is missing")
    return {"ok": True, "scope": "offline-scaffold-only", "local_links": checked_links,
            "pinned_files": len(lock["files"]), "scientific_execution_enabled": False}


def git_read(repo: Path, *args: str) -> bytes:
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_NO_REPLACE_OBJECTS="1")
    result = subprocess.run(["git", "--no-optional-locks", "-C", str(repo), *args],
                            capture_output=True, timeout=60, env=env)
    if result.returncode:
        raise ValidationError("Git read failed: " + result.stderr.decode("utf-8", "replace").strip())
    return result.stdout


def verify_ravel(repo: Path, lock: dict) -> dict:
    validate_manifest(lock)
    commit = lock["commit"]
    resolved = git_read(repo, "rev-parse", "--verify", commit + "^{commit}").decode().strip()
    if resolved != commit:
        raise ValidationError("Resolved Ravel commit differs from lock")
    registry = None
    for entry in lock["files"]:
        blob = git_read(repo, "show", f"{commit}:{entry['path']}")
        if hashlib.sha256(blob).hexdigest() != entry["sha256"]:
            raise ValidationError("Pinned source hash mismatch: " + entry["path"])
        if entry["path"] == "analysis/research/registry.json":
            registry = json.loads(blob)
    actual_ids = {q["id"] for q in registry["questions"]}
    missing = set(lock["question_ids"]) - actual_ids
    if missing:
        raise ValidationError("Question IDs absent from pinned registry: " + ", ".join(sorted(missing)))
    return {"ok": True, "scope": "committed-source-identity-only", "ravel_commit": commit,
            "verified_files": len(lock["files"]), "question_ids": lock["question_ids"],
            "working_tree_read": False, "scientific_execution": False}
