"""Changing metric coverage must not manufacture improvements or regressions."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Tools'))
import compare_benchmarks as comparison


def report(*rows):
    return {'cases': [{'gain_db': 10., **r} for r in rows]}


class BenchmarkComparisonTests(unittest.TestCase):
    def test_new_sustain_score_is_not_a_regression_in_existing_observation(self):
        baseline = report({'case': 'n80v1', 'note': 80, 'sustain_db': 2.},
                          {'case': 'n80v2', 'note': 80, 'sustain_db': None})
        candidate = report({'case': 'n80v2', 'note': 80, 'sustain_db': 12.},
                           {'case': 'n80v1', 'note': 80, 'sustain_db': 2.})
        split = {'n80v1': 'train', 'n80v2': 'train'}
        before = copy.deepcopy((baseline, candidate))
        result = comparison.paired_comparison(baseline, candidate, split)
        metric = result['summary']['train']['sustain_db']
        self.assertEqual(metric['delta'], 0.)
        self.assertEqual((metric['paired_n'], metric['candidate_only_n']), (1, 1))
        self.assertEqual(result['regressions'], [])
        self.assertEqual(result['availability_changes'], [
            {'case': 'n80v2', 'note': 80, 'role': 'train', 'metric': 'sustain_db',
             'baseline': None, 'candidate': 12., 'change': 'gained'}])
        self.assertEqual((baseline, candidate), before)

    def test_lost_and_absent_scores_cannot_hide_paired_regression(self):
        baseline = report({'case': 'a', 'note': 60, 'early_db': 1., 'sustain_db': 20.},
                          {'case': 'b', 'note': 60, 'early_db': 3.})
        candidate = report({'case': 'a', 'note': 60, 'early_db': 2., 'sustain_db': None},
                           {'case': 'b', 'note': 60, 'early_db': 4.})
        result = comparison.paired_comparison(baseline, candidate, {'a': 'dev', 'b': 'dev'})
        self.assertEqual(result['regressions'], [
            {'note': 60, 'role': 'dev', 'metric': 'early_db', 'paired_n': 2,
             'baseline': 2., 'candidate': 3., 'delta': 1.}])
        metric = result['summary']['dev']['sustain_db']
        self.assertIsNone(metric['delta'])
        self.assertEqual((metric['baseline_only_n'], metric['neither_n']), (1, 1))
        self.assertEqual(result['availability_changes'][0]['change'], 'lost')

    def test_one_baseline_gain_reference_exposes_global_loudness_change(self):
        baseline = report({'case': 'a', 'note': 60, 'gain_db': 9.},
                          {'case': 'b', 'note': 72, 'gain_db': 11.})
        candidate = report({'case': 'a', 'note': 60, 'gain_db': 15.},
                           {'case': 'b', 'note': 72, 'gain_db': 17.})
        result = comparison.paired_comparison(baseline, candidate, {'a': 'train', 'b': 'dev'})
        self.assertEqual(result['level_reference_db'], 10.)
        self.assertEqual(result['summary']['train']['level_db']['delta'], 4.)
        self.assertEqual(result['summary']['dev']['level_db']['delta'], 6.)

    def test_invalid_identity_or_nonfinite_measurements_fail_closed(self):
        baseline = report({'case': 'a', 'note': 60, 'early_db': 1.})
        bad = [report({'case': 'a', 'note': 61}),
               report({'case': 'b', 'note': 60}),
               report({'case': 'a', 'note': 60}, {'case': 'a', 'note': 60}),
               report({'case': 'a', 'note': 60, 'gain_db': float('inf')}),
               report({'case': 'a', 'note': 60, 'early_db': float('nan')})]
        for candidate in bad:
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                comparison.paired_comparison(baseline, candidate, {'a': 'train', 'b': 'train'})


if __name__ == '__main__':
    unittest.main()
