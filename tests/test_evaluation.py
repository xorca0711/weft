"""Entirely synthetic B5 examples; fixture reviewers are not real reference labels."""
import copy
import unittest

from weft import evaluation as e


def plan_fixture():
    return {
        'schema_version': 1, 'evaluation_id': 'synthetic-evaluation-v1', 'kind': 'synthetic',
        'frozen_at': '2026-10-13T00:00:00Z',
        'owner_review': {'actor': 'synthetic-owner', 'locator': 'fixture:approval', 'record_sha256': 'a'*64},
        'sampling': {'universe_locator': 'fixture:universe', 'universe_sha256': 'b'*64,
                     'selection_method': 'All synthetic fixtures', 'coverage_limits': 'No actual papers'},
        'reference_reviewers': ['synthetic-reviewer'],
        'sample': [{'item_id': 'item-1', 'paper_key': 'fixture:paper-1', 'lineage_group': 'fixture:cohort-1',
                    'packet_sha256': 'c'*64, 'source_sha256': 'd'*64,
                    'source_version': 'synthetic-v1', 'source_locator': 'fixture:source',
                    'prior_exposure': {'agent': 'none', 'evaluator': 'none'},
                    'selection_probability': None,
                    'selection_probability_note': 'Purposive synthetic fixture; not estimable'}],
    }


def judgment_fixture(plan, reference=False, labels=('read_next','hold','not_suitable'), item_id='item-1', actor=None):
    item = next(x for x in plan['sample'] if x['item_id'] == item_id)
    return {'schema_version': 1, 'evaluation_id': plan['evaluation_id'], 'plan_sha256': e.fingerprint(plan),
            'item_id': item_id, 'packet_sha256': item['packet_sha256'],
            'actor': actor or ('synthetic-reviewer' if reference else 'synthetic-agent'),
            'actor_kind': 'human' if reference else 'agent', 'created_at': '2026-10-13T01:00:00Z',
            'independent_reference': reference, 'blind_to_agent': reference, 'prior_exposure': 'none',
            'judgments': {dimension: {'label': label, 'reason': 'Synthetic source-bound judgment' if label else 'Not assessed',
                                      'citations': [{'locator': 'fixture:paragraph-1', 'source_sha256': item['source_sha256']}] if label else []}
                          for dimension, label in zip(e.LABELS, labels)}}


class EvaluationTests(unittest.TestCase):
    def test_three_dimensions_remain_separate_and_never_qualify(self):
        plan=plan_fixture()
        agent=judgment_fixture(plan, labels=('read_next','review_required','hold'))
        reference=judgment_fixture(plan,True)
        result=e.evaluate(plan,[agent],[reference])
        self.assertEqual(result['metrics']['reading']['disagreement_rate'],0)
        self.assertEqual(result['metrics']['data']['disagreement_rate'],1)
        self.assertEqual(result['metrics']['data']['unsupported_positive_rate'],1)
        self.assertEqual(result['metrics']['rq']['disagreement_rate'],1)
        self.assertIsNone(result['metrics']['rq']['unsupported_positive_rate'])
        self.assertEqual(result['exposure_strata'].keys(),{'synthetic'})
        for flag in e.FLAGS:self.assertIs(result[flag],False)
        self.assertIsNone(result['independent_study_count'])

    def test_missing_records_and_labels_are_not_negative_or_perfect(self):
        plan=plan_fixture();agent=judgment_fixture(plan,labels=(None,'hold',None))
        result=e.evaluate(plan,[agent],[])
        for dimension in e.LABELS:
            self.assertEqual(result['metrics'][dimension]['sample_items'],1)
            self.assertEqual(result['metrics'][dimension]['missing_reference_labels'],1)
            self.assertEqual(result['metrics'][dimension]['paired_items'],0)
            self.assertIsNone(result['metrics'][dimension]['disagreement_rate'])
        self.assertEqual(result['missing_reference_records'],1)
        self.assertEqual(result['metrics']['reading']['missing_agent_labels'],1)
        self.assertEqual(e.evaluate(plan,[],[])['missing_prediction_records'],1)

    def test_reference_disagreement_and_missing_reviewer_stay_unresolved(self):
        plan=plan_fixture();plan['reference_reviewers'].append('second-reviewer')
        agent=judgment_fixture(plan)
        ref=judgment_fixture(plan,True)
        second=judgment_fixture(plan,True,labels=('reject','hold','not_suitable'),actor='second-reviewer')
        result=e.evaluate(plan,[agent],[ref,second])
        self.assertEqual(result['metrics']['reading']['reference_disagreements'],1)
        self.assertEqual(result['metrics']['reading']['paired_items'],0)
        self.assertEqual(result['metrics']['data']['concordant_holds'],1)
        incomplete=e.evaluate(plan,[agent],[ref])
        self.assertEqual(incomplete['metrics']['reading']['paired_items'],0)
        self.assertEqual(incomplete['metrics']['reading']['missing_reference_labels'],1)

    def test_exposed_and_unknown_material_do_not_enter_unseen_denominator(self):
        for exposure in ('exposed','unknown'):
            with self.subTest(exposure=exposure):
                plan=plan_fixture();plan['kind']='prospective'
                plan['sample'][0]['prior_exposure']['agent']=exposure
                result=e.evaluate(plan,[judgment_fixture(plan)],[judgment_fixture(plan,True)])
                self.assertNotIn('declared_unseen',result['exposure_strata'])
                self.assertIn(exposure,result['exposure_strata'])
        plan=plan_fixture();plan['kind']='prospective'
        agent=judgment_fixture(plan);reference=judgment_fixture(plan,True)
        reference['prior_exposure']='exposed'
        self.assertNotIn('declared_unseen',e.evaluate(plan,[agent],[reference])['exposure_strata'])
        reference['prior_exposure']='none'
        self.assertEqual(e.evaluate(plan,[agent],[reference])['exposure_strata']['declared_unseen']['reading']['paired_items'],1)

    def test_plan_rebinding_source_changes_and_pre_freeze_outcomes_fail(self):
        plan=plan_fixture();agent=judgment_fixture(plan)
        changes=[('plan_sha256','f'*64),('packet_sha256','f'*64),('created_at','2026-10-12T01:00:00Z'),('created_at','2026-10-13T01:00:00')]
        for key,value in changes:
            with self.subTest(key=key),self.assertRaises(ValueError):
                e.evaluate(plan,[{**agent,key:value}],[])
        changed=copy.deepcopy(agent)
        changed['judgments']['data']['citations'][0]['source_sha256']='e'*64
        with self.assertRaisesRegex(ValueError,'Citation source'):e.evaluate(plan,[changed],[])

    def test_unmatched_duplicate_and_invalid_records_fail_without_partial_scores(self):
        plan=plan_fixture();agent=judgment_fixture(plan);ref=judgment_fixture(plan,True)
        for predictions,references in [([agent,agent],[]),([{**agent,'item_id':'foreign'}],[]),([],[ref,ref])]:
            with self.assertRaises(ValueError):e.evaluate(plan,predictions,references)
        for label in ('accepted','claim_validated',[],True):
            invalid=copy.deepcopy(agent);invalid['judgments']['data']['label']=label
            with self.subTest(label=label),self.assertRaises(ValueError):e.evaluate(plan,[invalid],[])

    def test_reference_independence_is_required_but_not_authenticated(self):
        plan=plan_fixture();agent=judgment_fixture(plan);ref=judgment_fixture(plan,True)
        for patch in ({'actor_kind':'agent'},{'independent_reference':False},{'actor':'unlisted-reviewer'}):
            with self.assertRaisesRegex(ValueError,'independent named human'):
                e.evaluate(plan,[agent],[{**ref,**patch}])
        with self.assertRaisesRegex(ValueError,'identities overlap'):
            e.evaluate(plan,[{**agent,'actor':'synthetic-reviewer'}],[ref])
        result=e.evaluate(plan,[agent],[{**ref,'blind_to_agent':False}])
        self.assertEqual(result['unblinded_reference_records'],1)
        self.assertFalse(result['actor_identity_verified'])

    def test_unblinded_reference_never_enters_unseen_stratum(self):
        plan=plan_fixture(); plan['kind']='prospective'
        reference=judgment_fixture(plan,True); reference['blind_to_agent']=False
        result=e.evaluate(plan,[judgment_fixture(plan)],[reference])
        self.assertNotIn('declared_unseen',result['exposure_strata'])
        self.assertEqual(result['exposure_strata']['exposed']['reading']['paired_items'],1)

    def test_sample_and_probabilities_are_explicit_without_invented_denominators(self):
        for probability in (float('nan'),float('inf'),0,1.1,True,'unknown'):
            plan=plan_fixture();plan['sample'][0]['selection_probability']=probability
            with self.subTest(probability=probability),self.assertRaises(ValueError):e.validate_plan(plan)
        for patch in ({'sample':[]},{'owner_review':{}},{'reference_reviewers':[]},{'schema_version':True}):
            with self.assertRaises(ValueError):e.validate_plan({**plan_fixture(),**patch})
        plan=plan_fixture();plan['sample'].append(copy.deepcopy(plan['sample'][0]))
        with self.assertRaisesRegex(ValueError,'Duplicate sample'):e.validate_plan(plan)

    def test_null_label_needs_missingness_reason_and_known_label_citation(self):
        plan=plan_fixture();agent=judgment_fixture(plan)
        for judgment in ({'label':None,'reason':'','citations':[]},
                         {'label':'read_next','reason':'asserted','citations':[]}):
            changed=copy.deepcopy(agent);changed['judgments']['reading']=judgment
            with self.assertRaises(ValueError):e.evaluate(plan,[changed],[])

    def test_hashes_and_results_are_deterministic_inputs_unchanged(self):
        plan=plan_fixture();agent=judgment_fixture(plan);ref=judgment_fixture(plan,True)
        before=copy.deepcopy((plan,agent,ref));first=e.evaluate(plan,[agent],[ref])
        self.assertEqual(first,e.evaluate(plan,[agent],[ref]))
        self.assertEqual((plan,agent,ref),before)
        self.assertEqual(first['predictions_sha256'],e.fingerprint([agent]))
        with self.assertRaises(ValueError):e.fingerprint({'bad':float('nan')})


if __name__ == '__main__':
    unittest.main()
