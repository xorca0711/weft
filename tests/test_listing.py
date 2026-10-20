import copy
import io
import json
import unittest
from unittest.mock import patch

from weft import batches, listing, reading, screening, workflow
from weft.__main__ import main
from weft.discovery import Store
from weft.discovery import discover
from weft.europe_pmc import EuropePMC
from weft.identity import digest
import test_batches
import test_discovery as fixtures


class ListingTests(unittest.TestCase):
    setUp = fixtures.PersistentDiscoveryTests.setUp
    create = test_batches.BatchTests.create
    run_batch = test_batches.BatchTests.run_batch
    response = test_batches.BatchTests.response

    def prepared(self, *, journal='Nature Communications', doi=None, legacy=False, pubtypes=None):
        bid = self.create(listing_policy=None if legacy else listing.policy())
        workflow.initialize(self.store, bid, 'synthetic-agent')
        record = fixtures.article(pmcid='PMC1', abstractText='Synthetic primary research: immune signals alter epithelial fate; perturbations test the relationship.',
                                  journalInfo={'journal': {'title': journal}})
        if doi: record['doi'] = doi
        if pubtypes: record['pubTypeList'] = {'pubType': pubtypes}
        self.run_batch(bid, [record])
        return bid

    def answered(self, bid):
        issued = screening.next_packet(self.store, bid)
        answer = self.response(issued)
        values = {'article_type': 'primary_research', 'field': 'immunology', 'study_focus': 'biological_mechanism',
                  'mechanism_centrality': 'central', 'biological_system': 'Synthetic pulmonary epithelium and immune cells',
                  'measured_endpoint': 'Synthetic lineage-resolved epithelial state', 'mechanism': 'Synthetic immune-to-epithelial fate regulation'}
        for name, value in values.items():
            answer['listing_assessment'][name] = {'value': value, 'reason': 'Synthetic source explicitly tests this comparison',
                                                 'citations': copy.deepcopy(answer['citations'])}
        return issued, answer

    def test_query_is_frozen_and_original_profile_preserved(self):
        original = copy.deepcopy(test_batches.PROFILE)
        bid = self.prepared()
        spec = batches.specification(self.store, bid)
        self.assertEqual(test_batches.PROFILE, original)
        self.assertEqual(spec['listing_policy'], listing.policy())
        self.assertIn('JOURNAL:"Cell Stem Cell"', spec['profile']['streams']['broad'])
        self.assertIn('TITLE_ABS:', spec['profile']['streams']['broad'])
        self.assertEqual(spec['listing_policy']['clinical_exceptions'], [])

    def test_admission_and_recovery_preserve_contrary_findings(self):
        bid = self.prepared(); issued, answer = self.answered(bid)
        answer['relation'] = 'contrary'
        screening.submit(self.store, bid, answer)
        with Store(self.store.root) as reopened:
            report = listing.report(reopened, bid)
            self.assertEqual(len(report['primary_list']), 1)
            self.assertFalse(report['claim_validated'])
            self.assertEqual(screening.submit(reopened, bid, answer)['status'], 'already_recorded')
            self.assertEqual(workflow.status(reopened, bid)['paper_listing'], report)

    def test_unknown_does_not_pass_and_hold_is_recordable(self):
        bid = self.prepared(); issued, answer = self.answered(bid)
        answer['listing_assessment']['mechanism']['value'] = 'unknown'
        with self.assertRaisesRegex(ValueError, 'Primary-list gate: hold'):
            screening.submit(self.store, bid, answer)
        answer['decision'] = 'hold'
        screening.submit(self.store, bid, answer)
        self.assertEqual(listing.report(self.store, bid)['primary_list'], [])

    def test_materials_keyword_only_and_nonprimary_cannot_pass(self):
        bid = self.prepared(); issued, original = self.answered(bid)
        for field, value in [('field', 'out_of_scope'), ('study_focus', 'materials_performance'),
                             ('mechanism_centrality', 'incidental'), ('article_type', 'review')]:
            answer = copy.deepcopy(original); answer['listing_assessment'][field]['value'] = value
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'Primary-list gate: excluded'):
                screening.submit(self.store, bid, answer)
        self.assertEqual(listing.report(self.store, bid)['primary_list'], [])

    def test_title_only_or_tampered_citation_cannot_pass(self):
        bid = self.prepared(); issued, original = self.answered(bid)
        answer = copy.deepcopy(original)
        answer['listing_assessment']['mechanism']['citations'] = [{k: issued['packet']['segments'][0][k] for k in ('locator', 'segment_sha256')}]
        with self.assertRaisesRegex(ValueError, 'abstract evidence'):
            screening.submit(self.store, bid, answer)
        answer = copy.deepcopy(original)
        answer['listing_assessment']['field']['citations'][0]['segment_sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'changed listing citation'):
            screening.submit(self.store, bid, answer)

    def test_journal_family_and_clinical_journal_are_not_implicit_admission(self):
        bid = self.prepared(journal='Nature Materials')
        result = screening.next_packet(self.store, bid)
        self.assertEqual(result['status'], 'no-packet')
        self.assertEqual(listing.report(self.store, bid)['primary_list'], [])
        self.assertEqual(listing.report(self.store, bid)['audit'][0]['status'], 'excluded')
        for title in ('Scientific Reports', 'The Lancet', 'Nature Fake', ''):
            packet = {'listing_policy': listing.policy(), 'paper_key': 'doi:10.9999/synthetic', 'records': [{'journal': title}]}
            self.assertIn(listing.precheck(packet)['status'], {'excluded', 'hold'})

    def test_source_review_type_cannot_be_overridden(self):
        bid = self.prepared(pubtypes=['Review', 'Journal Article'])
        self.assertEqual(screening.next_packet(self.store, bid)['status'], 'no-packet')

    def test_verified_exact_science_alias_is_accepted_without_family_expansion(self):
        bid = self.prepared(journal='Science (New York, N.Y.)')
        issued, answer = self.answered(bid)
        screening.submit(self.store, bid, answer)
        self.assertEqual(len(listing.report(self.store, bid)['primary_list']), 1)

    def test_owner_excluded_tooth_cannot_reenter_even_with_core_journal(self):
        bid = self.prepared(doi='10.1002/adma.75042')
        self.assertEqual(screening.next_packet(self.store, bid)['status'], 'no-packet')
        audit = listing.report(self.store, bid)['audit']
        self.assertEqual(audit[0]['status'], 'excluded')
        self.assertIn('Owner strictly rejected', audit[0]['reason'])

    def test_manual_read_next_cannot_bypass_scoped_assessment(self):
        bid = self.prepared(); issued = screening.next_packet(self.store, bid)
        cid = issued['packet']['candidate_id']
        with self.store.db:
            self.store.db.execute("UPDATE candidates SET status='read_next' WHERE id=?", (cid,))
        with self.assertRaisesRegex(ValueError, 'admission required'):
            reading.prepare_reading(self.store, cid, fetch=lambda _: self.fail('No fetch before admission'))

    def test_standalone_scoped_discovery_cannot_bypass_admission(self):
        receipt = discover(self.store, self.ctx, 'Synthetic constrained query', since='2026-10-01', until='2026-10-02',
                           listing_policy=listing.policy(), client=EuropePMC(fetch=lambda _: fixtures.page([fixtures.article(pmcid='PMC1')])) )
        self.assertEqual(receipt['listing_policy_sha256'], digest(listing.policy()))
        cid = receipt['candidate_ids'][0]
        with self.store.db:
            self.store.db.execute("UPDATE candidates SET status='read_next' WHERE id=?", (cid,))
        with self.assertRaisesRegex(ValueError, 'admission required'):
            reading.prepare_reading(self.store, cid, fetch=lambda _: self.fail('No fetch before admission'))

    def test_new_hold_or_changed_response_removes_recommendation(self):
        bid = self.prepared(); issued, answer = self.answered(bid)
        screening.submit(self.store, bid, answer)
        with self.store.db:
            self.store.db.execute("UPDATE candidates SET status='held' WHERE id=?", (answer['candidate_id'],))
        self.assertEqual(listing.report(self.store, bid)['primary_list'], [])

    def test_legacy_batch_is_not_retroactively_promoted_or_modified(self):
        bid = self.prepared(legacy=True)
        before = batches.specification(self.store, bid)
        issued = screening.next_packet(self.store, bid)
        self.assertNotIn('listing_assessment', issued['response_template'])
        screening.submit(self.store, bid, self.response(issued))
        self.assertEqual(listing.report(self.store, bid)['primary_list'], [])
        self.assertEqual(batches.specification(self.store, bid), before)

    def test_cli_and_export_separate_primary_list_from_audit(self):
        bid = self.prepared(); issued, answer = self.answered(bid)
        screening.submit(self.store, bid, answer)
        with patch('sys.stdout', new_callable=io.StringIO) as stdout:
            self.assertEqual(main(['paper-list', '--store', str(self.store.root), '--batch', bid]), 0)
        self.assertEqual(len(json.loads(stdout.getvalue())['primary_list']), 1)
        output = self.store.root.parent / 'listing-export'
        workflow.export(self.store, bid, output)
        html = (output / 'index.html').read_text(encoding='utf-8')
        self.assertIn('Primary reading list', html); self.assertIn('Complete audit queue', html)


if __name__ == '__main__':
    unittest.main()
