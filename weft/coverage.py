"""Read-only query configuration coverage; never a measurement of literature recall."""
from __future__ import annotations

import re

from .identity import digest


def validate_profile_binding(profile: dict, context: dict) -> None:
    """Reject stale source-bound drafts without imposing a new approval system.

    Historical profiles without qualification/source-binding fields retain their
    original behaviour. A draft is executable only by explicit profile selection
    and binds one exact question packet; passing this check does not qualify its
    search performance, scientific interpretation or live dispatch.
    """
    fields = {"qualification_status", "source_commit", "source_context_sha256"}
    if not isinstance(profile, dict):
        raise ValueError("Profile must be an object")
    if not fields.intersection(profile):
        return
    if (profile.get("qualification_status") != "draft-unqueried"
            or not isinstance(context, dict) or not isinstance(context.get("questions"), list)
            or digest(context["questions"]) != context.get("catalog_sha256")
            or not isinstance(profile.get("rq_ids"), list) or len(profile["rq_ids"]) != 1
            or not isinstance(profile["rq_ids"][0], str)
            or not re.fullmatch(r"[0-9a-f]{40}", str(profile.get("source_commit", "")))
            or profile["source_commit"] != context.get("ravel_commit")):
        raise ValueError("Draft profile must bind one exact current Ravel context and source revision")
    matches = [q for q in context["questions"]
               if isinstance(q, dict) and q.get("rq_id") == profile["rq_ids"][0]]
    if (len(matches) != 1
            or not re.fullmatch(r"[0-9a-f]{64}", str(profile.get("source_context_sha256", "")))
            or profile["source_context_sha256"] != matches[0].get("context_sha256")):
        raise ValueError("Draft query source context is stale or absent; review and rebind explicitly")


def audit_profiles(configuration: dict, context: dict) -> dict:
    """Validate profile references against a caller-supplied pinned RQ catalog.

    Use the complete ``build_context(repo, lock)`` result for portfolio auditing.
    This inspects query configuration only: no retrieval, semantic judgment,
    scientific eligibility or automatic expansion of a question is performed.
    """
    if (not isinstance(configuration, dict) or type(configuration.get("schema_version")) is not int
            or configuration["schema_version"] != 1 or not isinstance(configuration.get("profiles"), dict)
            or not configuration["profiles"]):
        raise ValueError("Expected schema-1 nonempty search profiles")
    if not isinstance(context, dict) or not isinstance(context.get("questions"), list) or not context["questions"]:
        raise ValueError("A pinned nonempty RQ context is required")
    if digest(context["questions"]) != context.get("catalog_sha256"):
        raise ValueError("RQ context hash mismatch")
    if not isinstance(context.get("ravel_commit"), str) or not re.fullmatch(r"[0-9a-f]{40}", context["ravel_commit"]):
        raise ValueError("Full Ravel source revision required")
    questions = {}
    for question in context["questions"]:
        if (not isinstance(question, dict) or not isinstance(question.get("rq_id"), str)
                or not re.fullmatch(r"A\d+", question["rq_id"]) or question["rq_id"] in questions
                or not isinstance(question.get("title"), str) or not question["title"]
                or not re.fullmatch(r"[0-9a-f]{64}", str(question.get("context_sha256", "")))):
            raise ValueError("Malformed or duplicate RQ context entry")
        questions[question["rq_id"]] = question
    assignments = {qid: [] for qid in questions}
    profiles, query_uses = [], {}
    for name, profile in sorted(configuration["profiles"].items()):
        if (not isinstance(name, str) or not name.strip() or not isinstance(profile, dict)
                or not isinstance(profile.get("rq_ids"), list) or not profile["rq_ids"]
                or any(not isinstance(qid, str) for qid in profile["rq_ids"])
                or len(set(profile["rq_ids"])) != len(profile["rq_ids"])
                or not set(profile["rq_ids"]).issubset(questions)
                or profile.get("date_field") not in {"FIRST_IDATE", "FIRST_PDATE"}
                or not isinstance(profile.get("rationale"), str) or not profile["rationale"].strip()
                or not isinstance(profile.get("streams"), dict) or "broad" not in profile["streams"]):
            raise ValueError("Profile requires registered RQs, rationale, date field and broad stream")
        validate_profile_binding(profile, context)
        for stream, query in profile["streams"].items():
            if (not isinstance(stream, str) or not stream.strip() or not isinstance(query, str)
                    or not query.strip() or len(query) > 6000):
                raise ValueError("Each stream requires a bounded nonempty query")
            query_uses.setdefault(digest(query), []).append({"profile": name, "stream": stream})
        for qid in profile["rq_ids"]:
            assignments[qid].append(name)
        profiles.append({"profile": name, "rq_ids": profile["rq_ids"],
                         "qualification_status": profile.get("qualification_status", "legacy-unspecified"),
                         "date_field": profile["date_field"], "streams": sorted(profile["streams"]),
                         "missing_complementary_streams": sorted({"rq_contrary", "adjacent_context"} - profile["streams"].keys()),
                         "configuration_sha256": digest(profile),
                         "retrieval_and_semantic_qualification": "not-assessed-by-this-audit"})
    rows = [{"rq_id": qid, "title": questions[qid]["title"], "profiles": assignments[qid],
             "status": "configured" if assignments[qid] else "no-profile",
             "first_index_profiles": [name for name in assignments[qid]
                                      if configuration["profiles"][name]["date_field"] == "FIRST_IDATE"]}
            for qid in sorted(questions, key=lambda value: int(value[1:]))]
    return {"schema_version": 1, "scope": "configuration-coverage-only",
            "ravel_commit": context["ravel_commit"], "context_sha256": context["catalog_sha256"],
            "configuration_sha256": digest(configuration), "questions": rows, "profiles": profiles,
            "question_count": len(rows), "configured_question_count": sum(bool(row["profiles"]) for row in rows),
            "draft_profile_count": sum(p["qualification_status"] == "draft-unqueried" for p in profiles),
            "unconfigured_question_ids": [row["rq_id"] for row in rows if not row["profiles"]],
            "identical_query_reuse": [sorted(uses, key=lambda x: (x["profile"], x["stream"]))
                                      for _, uses in sorted(query_uses.items()) if len(uses) > 1],
            "recall_measured": False, "scientific_execution_allowed": False,
            "limitations": ["The supplied catalog defines the audit denominator; supply all RQs for portfolio coverage.",
                            "Configured queries do not establish search recall, appropriate framing or completed retrieval.",
                            "Missing complementary streams nominate review, not automatically generated biological terms."]}
