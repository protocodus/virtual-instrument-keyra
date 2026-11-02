"""Check the factory dynamics regression policy with synthetic meter readings."""
import csv
import io
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Tools'))
import check_factory_dynamics as dynamics


class FactoryDynamics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        expected, exceptions = dynamics.reference_rows()
        cls.rows = {}
        for key, (high_velocity, notes) in expected.items():
            panel, piano, mic, rnd, shape, low_velocity = key
            step = exceptions.get(key, .25)
            cls.rows[key] = dict(zip(dynamics.COLUMNS, (panel, 'factory', .7, piano, mic, rnd, shape, notes,
                                                       low_velocity, high_velocity, -10., -10. + step, step)))

    def check(self, change=None, remove=None, extra=None):
        stream = io.StringIO(newline='')
        writer = csv.DictWriter(stream, dynamics.COLUMNS)
        writer.writeheader()
        for key, row in self.rows.items():
            if key != remove:
                writer.writerow(dict(row, **(change or {}).get(key, {})))
        if extra:
            writer.writerow(extra)
        stream.seek(0)
        return dynamics.check(stream)

    def test_accepted_exceptions_and_improvements(self):
        expected, exceptions = dynamics.reference_rows()
        self.assertEqual(len(expected), 2544)
        self.assertEqual(len(exceptions), 406)
        key = ('original', 'Belmont Grand', 0, 5, 1, 110)
        self.assertAlmostEqual(exceptions[key], -.561, places=2)
        self.assertEqual(self.check(change={key: {'step_db': .1, 'vu_high': -9.9}}), 2544)

    def test_rejected_indicator_from_independent_chords(self):
        # Measured in the rejected short-release, peak-first trial: this
        # five-note Hamamatsu Tube chord turned down where stock increased.
        key = ('independent', 'Hamamatsu Grand', 1, 5, 0, 101)
        step = -.057344033
        self.assertNotIn(key, dynamics.reference_rows()[1])
        with self.assertRaisesRegex(ValueError, '1 factory dynamics regression'):
            self.check(change={key: {'vu_high': -10 + step, 'step_db': step}})

    def test_old_reversal_is_a_floor_independent_of_other_improvements(self):
        exceptions = dynamics.reference_rows()[1]
        key = ('original', 'Belmont Grand', 0, 5, 1, 110)
        other = ('expanded', 'Kakegawa Grand', 0, 1, 0, 112)
        small = exceptions[key] - .0005
        self.assertEqual(self.check(change={key: {'step_db': small, 'vu_high': -10 + small}}), 2544)
        worse = exceptions[key] - .002
        with self.assertRaisesRegex(ValueError, '1 factory dynamics regression'):
            self.check(change={key: {'step_db': worse, 'vu_high': -10 + worse},
                               other: {'step_db': 1.25, 'vu_high': -8.75}})

    def test_support_and_invalid_measurements(self):
        key = ('original', 'Kakegawa Grand', 0, 1, 0, 110)
        for message, options in (
                ('missing audit rows', {'remove': key}),
                ('duplicate audit row', {'extra': self.rows[key]}),
                ('unexpected audit support', {'change': {key: {'midi_notes': '59 63 67'}}}),
                ('unexpected audit support', {'change': {key: {'velocity_high': 126}}}),
                ('incorrect drive', {'change': {key: {'drive': 'low', 'output_gain': .07}}}),
                ('nonfinite audit value', {'change': {key: {'vu_high': 'nan'}}}),
                ('silent meter reading', {'change': {key: {'vu_low': -288, 'vu_high': -288, 'step_db': 0}}}),
                ('inconsistent paired readings', {'change': {key: {'step_db': 10}}})):
            with self.subTest(message=message), self.assertRaisesRegex(ValueError, message):
                self.check(**options)


if __name__ == '__main__':
    unittest.main()
