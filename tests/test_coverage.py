import copy
import unittest

from weft.coverage import audit_profiles
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
