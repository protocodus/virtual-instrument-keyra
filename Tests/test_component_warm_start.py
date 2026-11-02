"""Synthetic fitting contracts, without recordings or recording-derived fixtures.

The two resolved components exercise the additional starting point. This is not
a synthetic reproduction of Belmont C5's original local minimum; its measured
before/after evidence remains in the dated calibration record.
"""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Tools'))
import piano_analysis as analysis


def synthetic_layers(two_components):
    sample_rate, fundamental = 48000, 500.
    length = analysis.window_length(fundamental, sample_rate)
    grid, profile = analysis.window_profile(
        fundamental, sample_rate, min(.002, length / sample_rate / 24), length)
    times = np.r_[np.arange(0, .5, .0015), np.arange(.5, 5, .02)]
    response = analysis._WindowedExponentials(times, grid, profile)
    poles = (np.array([-.7 + 2j * np.pi * .7, -.7 - 2j * np.pi * .7])
             if two_components else np.array([-.7 + 2j * np.pi * .3]))
    basis, _ = response(np.r_[poles, poles - 500])
    envelope = basis[:, :len(poles)] - basis[:, len(poles):]
    layers = []
    for velocity, amplitude in [(25, .03), (77, .1), (116, .3)]:
        measured = ((envelope * amplitude).T if two_components else np.vstack([
            envelope[:, 0] * amplitude,
            envelope[:, 0] * amplitude * (.7 + .2j)]))
        layers.append({
            'times': times, 'z': measured,
            'power_db': 10 * np.log10(np.maximum(np.mean(abs(measured)**2, axis=0), 1e-30)),
            'floor_db': -140., 'velocity': velocity})
    return layers, dict(f1=fundamental, sr=sample_rate, n=2, hz=1000)


class ComponentWarmStart(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = []
        for two_components in [False, True]:
            layers, arguments = synthetic_layers(two_components)
            disabled_trace, enabled_trace = {}, {}
            # These interior fixtures do not reach the original wider-bound
            # retry. Default/disabled must therefore never request spectrum
            # seeds. Comparing separate nonlinear fits byte-for-byte is an
            # invalid contract: the unchanged original fitter also permutes
            # indistinguishable lanes on NumPy 1.26/SciPy 1.14. Test the opt-in
            # boundary and same-run winner identity, without a loose tolerance.
            with patch.object(analysis, '_component_offsets',
                              side_effect=AssertionError('disabled extra search')):
                baseline = analysis.fit_partial_layers(layers, **arguments)
                disabled = analysis.fit_partial_layers(
                    layers, **arguments, component_warm_start=False,
                    diagnostics=disabled_trace)
            enabled = analysis.fit_partial_layers(
                layers, **arguments, component_warm_start=True,
                diagnostics=enabled_trace)
            cls.cases.append((baseline, disabled, enabled, disabled_trace,
                              enabled_trace['component_warm_start']))

    def test_disabled_default_does_not_run_extra_search(self):
        for baseline, disabled, _, trace, _ in self.cases:
            self.assertIsNotNone(baseline)
            self.assertIsNotNone(disabled)
            self.assertEqual(trace, {})

    def test_unresolved_pair_does_not_change_fit(self):
        _, _, enabled, _, trace = self.cases[0]
        self.assertLess(len(trace['measured_offsets']), 2)
        self.assertIn('skipped', trace)
        self.assertEqual(trace['selected'], 'baseline')
        np.testing.assert_array_equal(enabled['theta'], trace['baseline_theta'])

    def test_original_objective_selects_and_reports(self):
        trace = self.cases[1][-1]
        self.assertGreaterEqual(len(trace['measured_offsets']), 2)
        self.assertTrue(np.isfinite(trace['baseline_cost']))
        self.assertTrue(np.isfinite(trace['candidate_cost']))
        self.assertEqual(trace['selected'], 'component_warm_start'
                         if trace['candidate_cost'] < trace['baseline_cost'] else 'baseline')
        self.assertGreater(trace['nfev'], 0)
        self.assertIn('message', trace)

    def test_bounds_and_finite_result(self):
        for _, _, fit, _, trace in self.cases:
            theta = fit['theta']
            self.assertTrue(np.all(np.isfinite(theta)))
            self.assertTrue(np.all(theta[:4] >= np.log(analysis.SLOWEST_RATE)))
            self.assertTrue(np.all(theta[:4] <= np.log(500)))
            self.assertTrue(np.all(abs(theta[4:8]) <= trace['span']))
            self.assertGreaterEqual(theta[8], np.log(2e-4))
            self.assertLessEqual(theta[8], np.log(.5))
            self.assertLessEqual(abs(theta[9]), 3)
            for amplitudes in fit['amplitudes']:
                self.assertTrue(np.all(np.isfinite(amplitudes)))


if __name__ == '__main__':
    unittest.main()
