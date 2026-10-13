import copy
import json
from pathlib import Path
import unittest

from weft.coverage import audit_profiles, validate_profile_binding
from weft.identity import digest


def context():
    questions = [{"rq_id": q, "title": q + " fixture", "context_sha256": digest(q)} for q in ("A0", "A1", "A2")]
    return {"ravel_commit": "a" * 40, "questions": questions, "catalog_sha256": digest(questions)}


def configuration():
    return {"schema_version": 1, "profiles": {"fixture": {"rq_ids": ["A0"], "date_field": "FIRST_IDATE",
        "rationale": "Synthetic coverage test", "streams": {"broad": "synthetic-query"}}}}


class CoverageTests(unittest.TestCase):
    def test_reports_configured_rqs_without_semantic_claim(self):
        report = audit_profiles(configuration(), context())
        self.assertEqual(report["question_count"], 3)
        self.assertEqual(report["configured_question_count"], 1)
        self.assertEqual(report["unconfigured_question_ids"], ["A1", "A2"])
        self.assertFalse(report["recall_measured"])
        self.assertFalse(report["scientific_execution_allowed"])
        self.assertEqual(report["profiles"][0]["missing_complementary_streams"], ["adjacent_context", "rq_contrary"])

    def test_historical_profile_does_not_become_current_index_coverage(self):
        value = configuration()
        value["profiles"]["fixture"]["date_field"] = "FIRST_PDATE"
        report = audit_profiles(value, context())
        self.assertEqual(report["questions"][0]["profiles"], ["fixture"])
        self.assertEqual(report["questions"][0]["first_index_profiles"], [])

    def test_unknown_or_duplicate_rq_reference_is_rejected(self):
        for ids in (["A99"], ["A0", "A0"]):
            value = configuration()
            value["profiles"]["fixture"]["rq_ids"] = ids
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                audit_profiles(value, context())

    def test_missing_broad_and_invalid_query_are_rejected(self):
        for streams in ({"priority_journals": "fixture"}, {"broad": " "}, {"broad": "x" * 6001}):
            value = configuration()
            value["profiles"]["fixture"]["streams"] = streams
            with self.subTest(streams=list(streams)), self.assertRaises(ValueError):
                audit_profiles(value, context())

    def test_reused_query_does_not_inflate_rq_count(self):
        value = configuration()
        value["profiles"]["second"] = copy.deepcopy(value["profiles"]["fixture"])
        report = audit_profiles(value, context())
        self.assertEqual(report["configured_question_count"], 1)
        self.assertEqual(len(report["identical_query_reuse"]), 1)

    def test_context_tampering_rejected(self):
        value = context()
        value["questions"][0]["title"] = "Changed"
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            audit_profiles(configuration(), value)

    def test_inputs_unchanged(self):
        settings, catalog = configuration(), context()
        before = copy.deepcopy((settings, catalog))
        self.assertEqual(audit_profiles(settings, catalog), audit_profiles(settings, catalog))
        self.assertEqual((settings, catalog), before)

    def draft(self):
        value = configuration()["profiles"]["fixture"]
        value.update(qualification_status="draft-unqueried", source_commit="a" * 40,
                     source_context_sha256=context()["questions"][0]["context_sha256"])
        return value

    def test_draft_binding_accepts_exact_full_or_selected_catalog(self):
        value = self.draft()
        validate_profile_binding(value, context())
        selected = context()
        selected["questions"] = selected["questions"][:1]
        selected["catalog_sha256"] = digest(selected["questions"])
        validate_profile_binding(value, selected)
        report = audit_profiles({"schema_version": 1, "profiles": {"draft": value}}, context())
        self.assertEqual(report["draft_profile_count"], 1)
        self.assertEqual(report["profiles"][0]["qualification_status"], "draft-unqueried")

    def test_draft_binding_rejects_revision_or_context_drift(self):
        for field, replacement in (("source_commit", "b" * 40), ("source_context_sha256", "b" * 64),
                                   ("rq_ids", ["A1"]), ("rq_ids", ["A0", "A1"])):
            value = self.draft()
            value[field] = replacement
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_profile_binding(value, context())

    def test_draft_cannot_drop_status_to_bypass_binding(self):
        value = self.draft()
        del value["qualification_status"]
        with self.assertRaises(ValueError):
            validate_profile_binding(value, context())

    def test_legacy_profiles_retain_original_behavior_and_unknown_qualification(self):
        validate_profile_binding(configuration()["profiles"]["fixture"], context())
        report = audit_profiles(configuration(), context())
        self.assertEqual(report["draft_profile_count"], 0)
        self.assertEqual(report["profiles"][0]["qualification_status"], "legacy-unspecified")

    def test_repository_drafts_cover_each_remaining_rq_with_explicit_limits(self):
        root = Path(__file__).resolve().parents[1]
        value = json.loads((root / "configs/search_profiles.json").read_text(encoding="utf-8"))
        lock = json.loads((root / "integration/ravel.lock.json").read_text(encoding="utf-8"))
        drafts = [p for p in value["profiles"].values() if p.get("qualification_status") == "draft-unqueried"]
        self.assertEqual(len(drafts), 30)
        self.assertEqual({p["rq_ids"][0] for p in drafts}, {"A" + str(i) for i in range(2, 32)})
        for profile in drafts:
            with self.subTest(rq=profile["rq_ids"]):
                self.assertEqual(profile["date_field"], "FIRST_IDATE")
                self.assertEqual(profile["source_commit"], lock["commit"])
                self.assertEqual(set(profile["streams"]), {"broad", "rq_contrary", "adjacent_context"})
                self.assertTrue(all(isinstance(q, str) and 0 < len(q) <= 6000 for q in profile["streams"].values()))
                self.assertRegex(profile["source_context_sha256"], r"^[0-9a-f]{64}$")
                self.assertRegex(profile["source_section_sha256"], r"^[0-9a-f]{64}$")
                self.assertTrue(profile["source_excerpt"].startswith("**"))
                self.assertTrue(profile["interpretation_limits"])
                self.assertIn("explicit-profile-selection-only", profile["activation_scope"])
