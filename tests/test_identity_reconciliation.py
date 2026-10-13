"""Synthetic regression cases for cross-record bibliographic integrity holds."""
import json
from pathlib import Path
import tempfile
import unittest

from weft.discovery import Store, discover, verify_run
from weft.europe_pmc import EuropePMC, SourceError
from weft.identity import deduplicate, digest, normalize


def article(identifier, **kwargs):
    return {"source": "MED", "id": identifier, "pmid": identifier,
            "doi": "10.1234/" + identifier, "title": "Shared fixture title", **kwargs}


def notice(target="1", kind="Retraction of"):
    return article("2", commentCorrectionList={"commentCorrection": [
        {"source": "MED", "id": target, "type": kind, "note": "Provider assertion only"}]})


class IdentifierRegressionTests(unittest.TestCase):
    def test_contradictory_self_identifier_is_a_conflict(self):
        result = deduplicate([article("1", pmid="2")])
        self.assertEqual(result["resolved_work_count"], 0)
        self.assertEqual(result["identity_conflicts"][0]["values"]["pmid"], ["1", "2"])
        self.assertIn("provider-pmid-conflict", result["groups"][0]["records"][0]["identity_warning"])

    def test_pmc_provider_identity_matches_explicit_pmcid(self):
        result = deduplicate([{"source": "PMC", "id": "PMC1", "title": "Fixture"},
                              article("1", pmcid="PMC1")])
        self.assertEqual(len(result["groups"]), 1)
        self.assertEqual(result["resolved_work_count"], 1)

    def test_explicit_relations_do_not_merge_notice_or_versions(self):
        original = article("1", versionList={"version": [{"source": "PPR", "id": "PPR1", "versionNumber": 1}]})
        preprint = {"source": "PPR", "id": "PPR1", "doi": "10.1234/preprint", "title": "Shared fixture title"}
        result = deduplicate([original, notice(), preprint])
        self.assertEqual(result["resolved_work_count"], 3)
        self.assertEqual(len(result["provider_relations"]), 2)
        self.assertIsNone(result["independent_study_count"])

    def test_provider_heuristic_note_is_retained_not_promoted(self):
        raw = notice(kind="Preprint in")
        raw["commentCorrectionList"]["commentCorrection"][0]["note"] = "Link created based on a title-first author match"
        relation = deduplicate([raw])["provider_relations"][0]
        self.assertIn("title-first author", relation["provider_assertion"]["note"])
        self.assertFalse(relation["integrity_review_required"])
        self.assertEqual(relation["reconciliation"], "target-not-in-result")

    def test_unresolved_relation_target_remains_explicit(self):
        raw = notice()
        del raw["commentCorrectionList"]["commentCorrection"][0]["id"]
        relation = deduplicate([raw])["provider_relations"][0]
        self.assertEqual(relation["target_identifiers"], [])
        self.assertEqual(relation["reconciliation"], "target-not-identified")
        self.assertTrue(relation["integrity_review_required"])

    def test_malformed_provider_id_is_rejected(self):
        for bad in ({}, [], True, ""):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                normalize(article("1", id=bad))

    def test_publication_erratum_nominates_integrity_review(self):
        self.assertTrue(normalize(article("1", pubTypeList={"pubType": ["Published Erratum"]}))["integrity_flags"])

    def test_relation_output_is_order_independent(self):
        raws = [article("1"), notice(), article("3")]
        self.assertEqual(deduplicate(raws), deduplicate(list(reversed(raws))))

    def test_conflict_output_is_order_independent(self):
        raws = [article("1", doi="10.1234/shared1"), article("2", doi="10.1234/shared1"),
                article("3", doi="10.1234/shared2"), article("4", doi="10.1234/shared2")]
        self.assertEqual(deduplicate(raws), deduplicate(list(reversed(raws))))

    def test_nested_optional_null_relation_lists_are_supported(self):
        result = deduplicate([article("1", commentCorrectionList={"commentCorrection": None}, versionList={"version": None})])
        self.assertEqual(result["provider_relations"], [])


class TransportIntegrityTests(unittest.TestCase):
    def test_zero_hit_count_with_nonempty_page_is_preserved_as_malformed(self):
        receipts = []
        body = json.dumps({"hitCount": 0, "resultList": {"result": [article("1")]}}).encode()
        with self.assertRaises(SourceError):
            EuropePMC(fetch=lambda _: body).search("fixture", lambda meta, raw: receipts.append((meta, raw)))
        self.assertEqual(receipts[0][1], body)
        self.assertTrue(receipts[0][0]["malformed"])

    def test_malformed_cursor_is_preserved_not_followed(self):
        for cursor in (True, {}, [], 3):
            receipts = []
            body = json.dumps({"hitCount": 2, "nextCursorMark": cursor, "resultList": {"result": [article("1")]}}).encode()
            with self.subTest(cursor=cursor), self.assertRaises(SourceError):
                EuropePMC(fetch=lambda _: body).search("fixture", lambda meta, raw: receipts.append(meta))
            self.assertTrue(receipts[0]["malformed"])

    def test_falling_hit_count_cannot_report_complete_after_overcount(self):
        pages = iter([json.dumps({"hitCount": 3, "nextCursorMark": "next", "resultList": {"result": [article("1"), article("2")]}}).encode(),
                      json.dumps({"hitCount": 2, "resultList": {"result": [article("3")]}}).encode()])
        result = EuropePMC(fetch=lambda _: next(pages)).search("fixture", lambda *args: None, page_size=2)
        self.assertEqual(result["status"], "unstable")
        self.assertIn("retrieved-record-count-exceeds-hit-count", result["warnings"])


class CorrectionBufferTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.store = Store(Path(temporary.name) / "store")
        self.addCleanup(self.store.db.close)
        questions = [{"rq_id": "A0", "title": "A0 fixture", "context_sha256": digest("context")}]
        self.context = {"ravel_commit": "a" * 40, "questions": questions, "catalog_sha256": digest(questions)}

    def search(self, records):
        body = json.dumps({"hitCount": len(records), "resultList": {"result": records}}).encode()
        receipt = discover(self.store, self.context, "fixture", since="2026-10-01", until="2026-10-13",
                           client=EuropePMC(fetch=lambda _: body))
        self.assertEqual(receipt["status"], "complete", receipt)
        return receipt

    def candidate(self, key="doi:10.1234/1"):
        return next(row for row in self.store.candidates() if row["paper_key"] == key and row["current"])

    def review(self, candidate):
        return {"decision": "read_next", "actor": "fixture-reader", "actor_kind": "human",
                "reason": "Synthetic initial reading decision", "evidence_refs": ["metadata:title"],
                "context_sha256": candidate["context_sha"], "evidence_sha256": candidate["evidence_sha"]}

    def test_later_notice_holds_prior_read_next_without_rewriting_decision(self):
        first = self.search([article("1")])
        original = self.candidate()
        review = self.review(original)
        self.store.review(original["id"], review)
        self.search([notice()])
        self.assertEqual(self.candidate()["status"], "held")
        events = self.store.db.execute("SELECT action,record_json FROM events WHERE candidate_id=? ORDER BY id", (original["id"],)).fetchall()
        self.assertEqual(events[0]["action"], "reading-triage")
        self.assertEqual(json.loads(events[0]["record_json"]), review)
        self.assertEqual(events[1]["action"], "provider-relation-held")
        self.assertEqual(json.loads(events[1]["record_json"])["previous_status"], "read_next")
        with self.assertRaisesRegex(ValueError, "Held identity/integrity"):
            self.store.review(original["id"], review)
        self.assertTrue(verify_run(self.store, first["run_id"])["ok"])

    def test_notice_before_original_and_same_batch_both_hold(self):
        self.search([notice()])
        self.search([article("1")])
        self.assertEqual(self.candidate()["status"], "held")
        self.assertEqual(len(self.store.candidates()), 2)

    def test_replay_is_idempotent_and_no_unflagged_snapshot_clears_hold(self):
        self.search([article("1"), notice()])
        count = self.store.db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        self.search([article("1"), notice()])
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM events").fetchone()[0], count)
        self.search([article("1")])
        self.assertEqual(self.candidate()["status"], "held")
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM events").fetchone()[0], count)

    def test_exact_identifier_only_not_shared_title(self):
        self.search([article("1"), article("3"), notice()])
        self.assertEqual(self.candidate()["status"], "held")
        self.assertEqual(self.candidate("doi:10.1234/3")["status"], "pending_review")

    def test_comment_relation_does_not_create_integrity_hold(self):
        self.search([article("1"), notice(kind="Comment on")])
        self.assertEqual(self.candidate()["status"], "pending_review")
        proposal = json.loads(self.store.db.execute("SELECT proposal_json FROM candidates WHERE id=?", (self.candidate()["id"],)).fetchone()[0])
        self.assertEqual(len(proposal["provider_relations"]), 1)

    def test_correction_across_rq_contexts_holds_all_original_links(self):
        self.search([article("1")])
        old = self.candidate()
        self.context["questions"] = [{"rq_id": "A1", "title": "A1 fixture", "context_sha256": digest("other")}]
        self.context["catalog_sha256"] = digest(self.context["questions"])
        self.search([notice()])
        retained = next(row for row in self.store.candidates() if row["id"] == old["id"])
        self.assertTrue(retained["current"])
        self.assertEqual(retained["status"], "held")

    def test_pending_packet_is_invalidated_by_later_relation(self):
        from weft.screening import candidate_event, live_candidate
        run = self.search([article("1")])
        candidate = self.candidate()
        packet = {"candidate_id": candidate["id"], "context_sha256": candidate["context_sha"],
                  "evidence_sha256": candidate["evidence_sha"], "source_run": run["run_id"]}
        before = candidate_event(self.store, candidate["id"])
        live_candidate(self.store, packet)
        self.search([notice()])
        self.assertGreater(candidate_event(self.store, candidate["id"]), before)
        with self.assertRaisesRegex(ValueError, "Identity/integrity hold"):
            live_candidate(self.store, packet)

    def test_prechange_store_observations_are_reconciled_without_schema_migration(self):
        self.search([article("1"), notice()])
        with self.store.db:
            self.store.db.execute("DELETE FROM events WHERE action LIKE 'provider-relation-%'")
            for row in self.store.db.execute("SELECT id,proposal_json FROM candidates").fetchall():
                proposal = json.loads(row["proposal_json"])
                proposal.pop("provider_relations", None)
                proposal["hold_reasons"] = [r for r in proposal["hold_reasons"] if r != "provider-related-integrity-flag"]
                self.store.db.execute("UPDATE candidates SET status=?,proposal_json=? WHERE id=?",
                    ("held" if proposal["hold_reasons"] else "pending_review", json.dumps(proposal), row["id"]))
        self.search([])
        self.assertEqual(self.candidate()["status"], "held")
