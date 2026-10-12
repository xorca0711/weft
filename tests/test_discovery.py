import copy
from datetime import date
import io
import json
from pathlib import Path
import tempfile
import unittest
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit

from weft.europe_pmc import EuropePMC, SourceError, date_window
from weft.identity import deduplicate, digest, doi_key
from weft.discovery import Store, discover, stream_key, verify_run


def article(identifier="1", **extra):
    return {"source": "MED", "id": identifier, "pmid": identifier,
            "doi": f"10.1234/paper.{identifier}", "title": "An observed phenotype", **extra}


def page(records, total=None, cursor=None):
    result = {"version": "fixture", "hitCount": len(records) if total is None else total,
              "resultList": {"result": records}}
    if cursor:
        result["nextCursorMark"] = cursor
    return json.dumps(result).encode()


def context(tag="original"):
    questions = [{"rq_id": "A0", "title": "A0. Example", "context_sha256": digest(tag)}]
    return {"ravel_commit": "a" * 40, "questions": questions, "catalog_sha256": digest(questions)}


class TransportTests(unittest.TestCase):
    def test_pagination_preserves_query_and_cursor(self):
        requests, receipts = [], []
        def fetch(url):
            params = parse_qs(urlsplit(url).query)
            requests.append(params)
            return page([article("1")], 2, "next token+/") if len(requests) == 1 else page([article("2")], 2)
        result = EuropePMC(fetch=fetch).search('AT2 AND "cell fate"', lambda m, b: receipts.append(m), page_size=1)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(requests[1]["cursorMark"], ["next token+/"])
        self.assertEqual(requests[0]["query"], ['AT2 AND "cell fate"'])
        self.assertEqual(len(receipts), 2)

    def test_retry_and_backoff_are_bounded(self):
        calls, sleeps = [], []
        def fetch(url):
            calls.append(url)
            if len(calls) == 1:
                raise HTTPError(url, 429, "limited", {"Retry-After": "9999"}, io.BytesIO())
            return page([])
        result = EuropePMC(fetch=fetch, sleep=sleeps.append).search("AT2", lambda *a: None)
        self.assertEqual(result["status"], "complete")
        self.assertEqual(sleeps, [20])

    def test_nonretryable_error_is_not_zero_hits(self):
        def fetch(url):
            raise HTTPError(url, 400, "bad query", {}, io.BytesIO())
        with self.assertRaises(SourceError):
            EuropePMC(fetch=fetch).search("AT2", lambda *a: None)

    def test_retry_exhaustion_preserves_attempt_count(self):
        def fetch(url):
            raise HTTPError(url, 503, "unavailable", {}, io.BytesIO())
        with self.assertRaises(SourceError) as raised:
            EuropePMC(fetch=fetch, sleep=lambda _: None).search("AT2", lambda *a: None)
        self.assertEqual(len(raised.exception.attempts), 3)

    def test_malformed_page_is_recorded(self):
        receipts = []
        with self.assertRaises(SourceError):
            EuropePMC(fetch=lambda _: b'{"error":"failure"}').search("AT2", lambda m,b: receipts.append(m))
        self.assertTrue(receipts[0]["malformed"])

    def test_truncation_is_explicit(self):
        result = EuropePMC(fetch=lambda _: page([article()], 20, "next")).search(
            "AT2", lambda *a: None, max_records=1)
        self.assertEqual(result["status"], "truncated")

    def test_missing_continuation_fails(self):
        with self.assertRaises(SourceError):
            EuropePMC(fetch=lambda _: page([article()], 3)).search("AT2", lambda *a: None)

    def test_repeated_cursor_fails(self):
        with self.assertRaises(SourceError):
            EuropePMC(fetch=lambda _: page([article()], 9, "same")).search("AT2", lambda *a: None, page_size=1)

    def test_index_changes_prevent_complete_status(self):
        pages = iter([page([article("1")], 3, "next"), page([article("2")], 2)])
        result = EuropePMC(fetch=lambda _: next(pages)).search("AT2", lambda *a: None, page_size=1)
        self.assertEqual(result["status"], "unstable")

    def test_duplicate_page_record_not_silent_success(self):
        pages = iter([page([article()], 2, "next"), page([article()], 2)])
        result = EuropePMC(fetch=lambda _: next(pages)).search("AT2", lambda *a: None, page_size=1)
        self.assertEqual(result["status"], "unstable")

    def test_date_window_handles_late_indexing(self):
        value = date_window("AT2", "FIRST_IDATE", "2026-10-01", "2026-10-11")
        self.assertIn("FIRST_IDATE", value)
        self.assertNotIn("FIRST_PDATE", value)
        with self.assertRaises(SourceError):
            date_window("AT2", "FIRST_IDATE", "2026-10-11", "2026-10-01")


class IdentityTests(unittest.TestCase):
    def test_doi_normalization_preserves_meaningful_punctuation(self):
        self.assertEqual(doi_key("https://doi.org/10.1234/ABC(1)"), "10.1234/abc(1)")
        self.assertEqual(doi_key(" DOI:10.1234/AbC "), "10.1234/abc")
        self.assertIsNone(doi_key("not-a-doi"))

    def test_cross_provider_duplicate_merges(self):
        a = article(pmcid="PMC1")
        b = {**a, "source": "PMC", "id": "PMC1"}
        result = deduplicate([a, a, b])
        self.assertEqual(result["resolved_work_count"], 1)
        self.assertEqual(result["observations"], 3)
        self.assertIsNone(result["independent_study_count"])

    def test_preprint_journal_are_not_collapsed_by_title(self):
        a, b = article("1"), article("2")
        result = deduplicate([a, b])
        self.assertEqual(result["resolved_work_count"], 2)
        self.assertEqual(len(result["possible_versions_by_title"]), 1)

    def test_conflicting_identifiers_hold_instead_of_false_merge(self):
        result = deduplicate([article("1"), article("2", doi="10.1234/paper.1")])
        self.assertEqual(result["resolved_work_count"], 0)
        self.assertEqual(len(result["identity_conflicts"]), 1)

    def test_comment_is_not_a_retraction(self):
        raw = article(commentCorrectionList={"commentCorrection":[{"type":"Comment in","source":"MED","id":"2"}]})
        self.assertFalse(deduplicate([raw])["groups"][0]["records"][0]["integrity_flags"])
        raw["commentCorrectionList"]["commentCorrection"][0]["type"] = "Retraction in"
        self.assertTrue(deduplicate([raw])["groups"][0]["records"][0]["integrity_flags"])

    def test_provider_version_links_are_retained(self):
        raw = article(versionList={"version":[{"source":"PPR","id":"PPR1"}]})
        record = deduplicate([raw])["groups"][0]["records"][0]
        self.assertEqual(record["provider_versions"], raw["versionList"])


class PersistentDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = Store(Path(self.temp.name)/"store")
        self.addCleanup(self.store.db.close)
        self.ctx = context()

    def run_search(self, records=None, **kwargs):
        records = [article()] if records is None else records
        defaults = {"since":"2026-10-01", "until":"2026-10-11",
                    "client":EuropePMC(fetch=lambda _: page(records))}
        defaults.update(kwargs)
        return discover(self.store, self.ctx, "AT2", **defaults)

    def test_success_receipt_and_repeat_dedup(self):
        first, second = self.run_search(), self.run_search()
        self.assertEqual(first["candidate_ids"], second["candidate_ids"])
        self.assertEqual(len(self.store.candidates()), 1)
        self.assertEqual(self.store.candidates()[0]["status"], "pending_review")
        self.assertTrue(verify_run(self.store, first["run_id"])["ok"])

    def test_failure_and_truncation_do_not_advance_watermark(self):
        fail = self.run_search(client=EuropePMC(fetch=lambda _: b'invalid'))
        self.assertEqual(fail["status"], "error")
        limited = self.run_search(client=EuropePMC(fetch=lambda _: page([article()],10,"next")), max_records=1)
        self.assertEqual(limited["status"], "truncated")
        self.assertIsNone(self.store.watermark(stream_key("AT2", "FIRST_IDATE", self.ctx)))

    def test_incremental_window_overlaps_and_never_regresses(self):
        self.run_search()
        receipt = self.run_search(since=None, until="2026-10-12")
        self.assertEqual(receipt["since"], "2026-10-04")
        self.run_search(since="2026-01-01",until="2026-01-02")
        self.assertEqual(self.store.watermark(stream_key("AT2","FIRST_IDATE",self.ctx)), "2026-10-12")

    def test_initial_since_required(self):
        with self.assertRaises(ValueError):
            self.run_search(since=None)

    def test_zero_results_is_success_but_error_is_not(self):
        result = self.run_search(records=[])
        self.assertEqual((result["status"], result["retrieved_records"]), ("complete",0))

    def review_record(self, candidate):
        return {"decision":"read_next","actor":"fixture-reader","actor_kind":"agent",
                "reason":"Read the primary methods before interpreting this match",
                "evidence_refs":["metadata:title"], "context_sha256":candidate["context_sha"],
                "evidence_sha256":candidate["evidence_sha"]}

    def test_read_next_never_validates_claim_or_executes(self):
        self.run_search()
        candidate = self.store.candidates()[0]
        result = self.store.review(candidate["id"], self.review_record(candidate))
        self.assertFalse(result["claim_validated"])
        self.assertFalse(result["scientific_execution_allowed"])
        self.assertFalse(result["actor_identity_verified"])

    def test_review_bound_to_snapshots_and_cannot_accept_claim(self):
        self.run_search()
        candidate = self.store.candidates()[0]
        record = self.review_record(candidate)
        record["context_sha256"] = "wrong"
        with self.assertRaises(ValueError):
            self.store.review(candidate["id"],record)
        record = self.review_record(candidate)
        record["decision"] = "claim_validated"
        with self.assertRaises(ValueError):
            self.store.review(candidate["id"],record)

    def test_context_change_invalidates_prior_review(self):
        self.run_search()
        old = self.store.candidates()[0]
        self.store.review(old["id"],self.review_record(old))
        self.ctx = context("changed")
        self.run_search()
        previous = next(c for c in self.store.candidates() if c["id"] == old["id"])
        self.assertEqual(previous["status"],"stale")
        with self.assertRaises(ValueError):
            self.store.review(old["id"],self.review_record(old))

    def test_source_change_and_reappearance_requires_review(self):
        self.run_search()
        old = self.store.candidates()[0]
        self.store.review(old["id"],self.review_record(old))
        self.run_search(records=[article(title="Corrected title")])
        self.run_search()
        active = [c for c in self.store.candidates() if c["current"]]
        self.assertEqual(len(active),1)
        self.assertEqual(active[0]["status"],"pending_review")

    def test_integrity_flag_blocks_read_next(self):
        self.run_search(records=[article(pubTypeList={"pubType":["Retracted Publication"]})])
        candidate = self.store.candidates()[0]
        self.assertEqual(candidate["status"],"held")
        with self.assertRaises(ValueError):
            self.store.review(candidate["id"],self.review_record(candidate))

    def test_raw_response_tamper_is_detected(self):
        result = self.run_search()
        path = self.store.root/result["run_id"]/"page-0001.json"
        path.write_text("altered",encoding="utf-8")
        with self.assertRaises(ValueError):
            verify_run(self.store,result["run_id"])

    def test_deduplication_tamper_is_detected(self):
        result = self.run_search()
        path = self.store.root/result["run_id"]/"deduplication.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["independent_study_count"] = 99
        path.write_text(json.dumps(data),encoding="utf-8")
        with self.assertRaises(ValueError):
            verify_run(self.store,result["run_id"])

    def test_existing_nonstore_is_preserved(self):
        other = Path(self.temp.name)/"other"
        other.mkdir()
        (other/"keep.txt").write_text("keep",encoding="utf-8")
        with self.assertRaises(ValueError):
            Store(other)
        self.assertEqual((other/"keep.txt").read_text(),"keep")

    def test_context_change_invalidates_even_without_new_hits(self):
        self.run_search()
        self.ctx = context("changed")
        self.run_search(records=[])
        self.assertEqual(self.store.candidates()[0]["status"], "stale")

    def test_identifier_change_between_runs_holds_both(self):
        self.run_search()
        self.run_search(records=[article(doi="10.1234/revised")])
        self.assertEqual(len(self.store.candidates()), 2)
        self.assertTrue(all(c["status"] == "held" for c in self.store.candidates()))
        for c in self.store.candidates():
            with self.assertRaises(ValueError):
                self.store.review(c["id"], self.review_record(c))

    def test_null_optional_metadata_is_supported(self):
        receipt = self.run_search(records=[article(commentCorrectionList=None, pubTypeList=None, abstractText=None)])
        self.assertEqual(receipt["status"], "complete")

    def test_explicit_window_cannot_skip_unsearched_gap(self):
        self.run_search()
        receipt = self.run_search(since="2026-10-20", until="2026-10-21")
        self.assertFalse(receipt["watermark_advanced"])
        self.assertIn("window-gap-watermark-not-advanced", receipt["warnings"])
        self.assertEqual(self.store.watermark(stream_key("AT2", "FIRST_IDATE", self.ctx)), "2026-10-11")


if __name__ == "__main__":
    unittest.main()
