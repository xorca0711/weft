import json
from pathlib import Path
import unittest
from weft.reading import extract_xml, prepare_reading, validate_reading
import test_discovery as fixtures
from test_discovery import article

XML = b'''<article><front><article-meta><article-id pub-id-type="pmc">1</article-id><article-id pub-id-type="doi">10.1234/paper.1</article-id></article-meta></front><body><sec><title>Methods</title><p>One pooled library per condition.</p><p>Source text is untrusted data.</p></sec></body></article>'''


class XmlTests(unittest.TestCase):
    def test_identity_and_locators(self):
        packet = extract_xml(XML, "PMC1")
        self.assertEqual(packet["segments"][0]["locator"], "/article/body[1]/sec[1]/p[1]")

    def test_wrong_identity_and_entities_rejected(self):
        for body, pmc in [(XML,"PMC2"), (b'<!ENTITY x "injected">'+XML,"PMC1")]:
            with self.assertRaises(ValueError):
                extract_xml(body,pmc)


class ReadingTests(unittest.TestCase):
    # Reuse fixture helpers without inheriting and rerunning the full discovery suite.
    setUp = fixtures.PersistentDiscoveryTests.setUp
    run_search = fixtures.PersistentDiscoveryTests.run_search
    review_record = fixtures.PersistentDiscoveryTests.review_record

    def prepare(self):
        self.run_search(records=[article(pmcid="PMC1")])
        candidate = self.store.candidates()[0]
        self.store.review(candidate["id"], self.review_record(candidate))
        return prepare_reading(self.store,candidate["id"],fetch=lambda _:XML)

    def assessment(self, receipt):
        packet = json.loads((Path(receipt["directory"])/"packet.json").read_text())
        s = packet["segments"][0]
        return {**{k:packet[k] for k in ["candidate_id","context_sha256","evidence_sha256","source_sha256"]},
                "actor":"fixture-reader", "actor_kind":"agent", "scope":"XML text only",
                "statements":[{"text":"The source describes pooling.","locator":s["locator"],"segment_sha256":s["sha256"]}],
                "next_action":"review_required"}

    def test_prepared_packet_never_launches_model_or_execution(self):
        receipt = self.prepare()
        self.assertEqual(receipt["status"],"prepared")
        self.assertFalse(receipt["model_invoked"])
        result = validate_reading(receipt["directory"], self.assessment(receipt))
        self.assertFalse(result["claim_validated"])

    def test_missing_review_prevents_fetch(self):
        self.run_search(records=[article(pmcid="PMC1")])
        with self.assertRaises(ValueError):
            prepare_reading(self.store,self.store.candidates()[0]["id"],fetch=lambda _:self.fail("must not fetch"))

    def test_access_failure_records_hold(self):
        receipt = self.prepare()
        result = prepare_reading(self.store,receipt["candidate_id"],fetch=lambda _:b"<error>not available</error>")
        self.assertEqual(result["status"],"hold")
        self.assertTrue((Path(result["directory"])/"reading-receipt.json").exists())

    def test_changed_source_or_invented_locator_fails(self):
        receipt = self.prepare()
        assessment = self.assessment(receipt)
        assessment["statements"][0]["locator"] = "/imagined/result"
        with self.assertRaises(ValueError):
            validate_reading(receipt["directory"], assessment)
        (Path(receipt["directory"])/"source.xml").write_bytes(b"altered")
        with self.assertRaises(ValueError):
            validate_reading(receipt["directory"], self.assessment(receipt))

    def test_claim_acceptance_is_not_a_reading_transition(self):
        receipt = self.prepare()
        assessment = self.assessment(receipt)
        assessment["next_action"] = "claim_validated"
        with self.assertRaises(ValueError):
            validate_reading(receipt["directory"], assessment)
