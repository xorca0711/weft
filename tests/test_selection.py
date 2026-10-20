import copy
import io
import json
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from weft import batches, screening, selection, workflow
from weft.__main__ import main
from weft.europe_pmc import EuropePMC
from weft.identity import digest
import test_batches
import test_discovery as fixtures


class SelectionTests(unittest.TestCase):
    setUp = fixtures.PersistentDiscoveryTests.setUp

    def prepared(self, *, cap=3, integrity=False):
        self.ctx['questions'] = [{'rq_id': rq, 'title': rq + '. Synthetic question', 'context_sha256': digest(rq)} for rq in ('A0', 'A1', 'A2')]
        self.ctx['catalog_sha256'] = digest(self.ctx['questions'])
        bid = batches.create(self.store, self.ctx, 'fixture', test_batches.PROFILE,
            ['broad', 'rq_contrary', 'adjacent_context'], '2026-10-01', '2026-10-02',
            max_records=10, max_searches=3, max_screenings=cap, selection_policy='paper-stream-v1')
        workflow.initialize(self.store, bid, 'fixture-agent')
        records = [fixtures.article(str(i), abstractText='Synthetic source') for i in (1, 2, 3)]
        if integrity:
            records[2]['pubTypeList'] = {'pubType': ['Retracted Publication']}
        def fetch(url):
            query = parse_qs(urlsplit(url).query)['query'][0]
            return fixtures.page([records[2]] if 'failure' in query else [records[1]] if 'organoid' in query else records)
        batches.run(self.store, bid, EuropePMC(fetch=fetch))
        return bid

    def test_distinct_papers_stream_rotation_and_rq_fairness(self):
        bid = self.prepared()
        report = selection.report(self.store, bid, include_plan=True)
        first = report['plan']['items'][:3]
        self.assertEqual([i['paper_key'] for i in first], ['doi:10.1234/paper.3', 'doi:10.1234/paper.2', 'doi:10.1234/paper.1'])
        self.assertEqual([i['rq_id'] for i in first], ['A0', 'A1', 'A2'])
        self.assertEqual(report['nominal_baseline']['unique_papers'], 1)
        self.assertEqual(report['nominal_policy']['unique_papers'], 3)
        issued = screening.next_packet(self.store, bid)
        self.assertEqual(issued['packet']['candidate_id'], first[0]['candidate_id'])
        self.assertEqual(selection.report(self.store, bid)['actual_issued']['links'], 1)
        self.assertFalse(report['relevance_validated'])
        self.assertIsNone(report['independent_study_count'])

    def test_plan_is_frozen_before_issue_and_stable_after_dispositions(self):
        bid = self.prepared(); first = selection.plan(self.store, bid)
        issued = screening.next_packet(self.store, bid)
        response = test_batches.BatchTests.response(self, issued, 'reject')
        screening.submit(self.store, bid, response)
        with workflow.readonly(self.store.root) as reopened:
            self.assertEqual(first, selection.plan(reopened, bid))
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM batch_events WHERE action='selection-frozen'").fetchone()[0], 1)

    def test_changed_provenance_does_not_rerank_or_submit(self):
        bid = self.prepared()
        with self.store.db:
            self.store.db.execute("UPDATE batch_windows SET stream='unexpected' WHERE stream='rq_contrary'")
        with self.assertRaisesRegex(ValueError, 'no implicit reranking'):
            selection.plan(self.store, bid)
        with patch.object(screening, 'next_packet', side_effect=AssertionError('No altered plan issuance')):
            self.assertEqual(workflow.advance(self.store, bid)['status'], 'hold')

    def test_known_integrity_holds_retained_and_never_nominated(self):
        bid = self.prepared(integrity=True)
        report = selection.report(self.store, bid, include_plan=True)
        self.assertEqual(len(report['held_links']), 3)
        self.assertNotIn('doi:10.1234/paper.3', report['nominal_policy']['paper_keys'])
        self.assertEqual(len(report['plan']['items']), 9)
        self.assertEqual(len({i['candidate_id'] for i in report['plan']['items']}), 9)

    def test_reference_audit_has_explicit_denominator_and_missing_papers(self):
        bid = self.prepared()
        reference = {'schema_version': 1, 'provenance': 'Synthetic independent-reference format fixture',
                     'prior_exposure': 'All generated outcomes exposed',
                     'paper_keys': ['doi:10.1234/paper.2', 'doi:10.1234/paper.9']}
        audit = selection.report(self.store, bid, reference=reference)['reference_audit']
        self.assertEqual(audit['accounting']['universe']['matched'], 1)
        self.assertEqual(audit['accounting']['universe']['reference_denominator'], 2)
        self.assertEqual(audit['accounting']['nominal_baseline']['matched'], 0)
        self.assertEqual(audit['accounting']['nominal_policy']['matched'], 1)
        self.assertEqual(audit['accounting']['universe']['missing_from_this_set'], ['doi:10.1234/paper.9'])
        self.assertFalse(audit['reference_independence_verified'])
        bad = copy.deepcopy(reference); bad['paper_keys'] *= 2
        with self.assertRaises(ValueError):
            selection.report(self.store, bid, reference=bad)

    def test_order_handles_overlap_missing_streams_and_every_link_once(self):
        for count in range(1, 12):
            items = [{'candidate_id': str(i), 'paper_key': str(i // 3), 'rq_id': str(i % 3),
                      'streams': ['broad'], 'hold_reasons': []} for i in range(count)]
            result = selection._ordered(items)
            self.assertEqual({i['candidate_id'] for i in result}, {i['candidate_id'] for i in items})
            first = result[:len({i['paper_key'] for i in items})]
            self.assertEqual(len(first), len({i['paper_key'] for i in first}))

    def test_legacy_spec_and_cli_default_are_preserved(self):
        bid = test_batches.BatchTests.create(self)
        self.assertNotIn('selection_policy', batches.specification(self.store, bid))
        self.assertEqual(selection.report(self.store, bid)['status'], 'legacy')
        with patch('weft.__main__.build_context', return_value=self.ctx), patch('weft.__main__.coverage.validate_profile_binding'), patch('weft.__main__.batches.create', return_value=bid) as create, patch('weft.__main__.batches.run', return_value={}), patch('sys.stdout', new_callable=io.StringIO):
            self.assertEqual(main(['batch-discover', '--repo', '.', '--profile', 'alveolar-transitions', '--since', '2026-10-01', '--until', '2026-10-02', '--store', str(self.store.root)]), 0)
        self.assertIsNone(create.call_args.kwargs['selection_policy'])

    def test_cli_report_is_readonly(self):
        bid = self.prepared()
        before = self.store.db.total_changes
        with patch('sys.stdout', new_callable=io.StringIO) as out:
            self.assertEqual(main(['selection-report', '--store', str(self.store.root), '--batch', bid, '--include-plan']), 0)
        self.assertEqual(json.loads(out.getvalue())['status'], 'frozen')
        self.assertEqual(before, self.store.db.total_changes)


if __name__ == '__main__':
    unittest.main()
