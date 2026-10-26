import copy
import unittest

from weft import r01_analysis as r01


class R01AnalysisTests(unittest.TestCase):
    def profiles(self):
        first = {'sample': 'GSM9136218', 'population': 'qLSC', 'representation': 'reported',
                 'recipe_sha256': 'a'*64, 'membership_sha256': 'b'*64, 'cell_count': 123,
                 'genes': ['G1', 'G2', 'G3'], 'values': [1, 2, 3]}
        second = {**copy.deepcopy(first), 'sample': 'GSM9136222', 'membership_sha256': 'c'*64,
                  'cell_count': 456, 'values': [3, 2, 1]}
        return first, second

    def test_analytic_values_constant_and_large_magnitude(self):
        self.assertAlmostEqual(r01.pearson([1,2,3], [3,2,1]), -1)
        self.assertAlmostEqual(r01.pearson([1,2,3], [2,4,6]), 1)
        self.assertAlmostEqual(r01.pearson([1,2,3], [1,0,1]), 0)
        self.assertAlmostEqual(r01.pearson([-1e308,0,1e308], [-1,0,1]), 1)
        self.assertIsNone(r01.pearson([2,2], [1,2]))

    def test_pool_denominators_never_become_replication_or_reproduction_pass(self):
        result = r01.compare(*self.profiles())
        self.assertEqual([p['cell_count'] for p in result['pools']], [123,456])
        self.assertEqual(result['gene_count'], 3)
        self.assertFalse(result['biological_replicates_established'])
        self.assertIsNone(result['biological_confidence_interval'])
        self.assertEqual(result['published_reproduction_verdict'], 'not-assessed')

    def test_mismatched_features_recipe_and_nonfinite_values_rejected(self):
        for delta in ({'genes': ['G2','G1','G3']}, {'values': [1,float('nan'),3]},
                      {'recipe_sha256': 'd'*64}, {'genes': ['G1','G1','G3']},
                      {'cell_count': True}, {'sample': 'invented-donor'}):
            left, right = self.profiles()
            with self.subTest(delta=delta), self.assertRaises(ValueError): r01.compare(left, {**right, **delta})

    def test_fixed_membership_processing_sensitivity(self):
        left, right = self.profiles()
        alternate = [{**copy.deepcopy(p), 'representation': 'unintegrated', 'recipe_sha256': 'd'*64}
                     for p in (left, right)]
        alternate[1]['values'] = [1,2,3]
        result = r01.sensitivity(left, right, *alternate)
        self.assertAlmostEqual(result['delta_r'], 2)
        self.assertFalse(result['selection_bias_resolved'])
        alternate[1]['cell_count'] -= 1
        with self.assertRaises(ValueError): r01.sensitivity(left, right, *alternate)

    def test_constant_profile_retains_unavailable_sensitivity(self):
        left, right = self.profiles(); right['values'] = [1,1,1]
        other = [{**p, 'representation': 'unintegrated'} for p in (left, right)]
        self.assertIsNone(r01.sensitivity(left, right, *other)['delta_r'])


if __name__ == '__main__': unittest.main()
