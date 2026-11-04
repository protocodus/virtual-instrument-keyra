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
        expected, floors = dynamics.reference_rows()
        cls.rows = {}
        for key, (high_velocity, notes, _) in expected.items():
            panel, piano, mic, rnd, shape, low_velocity = key
            step = floors[key]
            cls.rows[key] = dict(zip(dynamics.COLUMNS, (panel, 'factory', .7, piano, mic, rnd, shape, notes,
                                                       low_velocity, high_velocity, -80., -80. + step, step)))

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

    def test_floor_and_improvements(self):
        expected, floors = dynamics.reference_rows()
        self.assertEqual(len(expected), 2120)
        original = [value for key, value in floors.items() if key[0] == 'original']
        self.assertEqual(len(original), 400)
        self.assertGreater(min(original), 0.)
        key = ('original', 'New York Grand', 0, 5, 1, 110)
        improved = floors[key] + .35
        self.assertEqual(self.check(change={key: {'step_db': improved, 'vu_high': -80 + improved}}), 2120)

    def test_positive_step_losing_contrast_is_a_regression(self):
        # A harder chord can still play louder while losing most of B's dynamics.
        key = ('independent', 'Hamamatsu Grand', 1, 5, 0, 101)
        floor = dynamics.reference_rows()[1][key]
        self.assertGreater(floor, .1)
        with self.assertRaisesRegex(ValueError, '1 factory dynamics regression'):
            self.check(change={key: {'vu_high': -79.99, 'step_db': .01}})

    def test_each_fine_reversal_has_its_own_floor(self):
        floors = dynamics.reference_rows()[1]
        key = min((k for k in floors if k[0] == 'expanded'), key=floors.get)
        self.assertLess(floors[key], 0.)
        slight = floors[key] - .0005
        self.assertEqual(self.check(change={key: {'step_db': slight, 'vu_high': -80 + slight}}), 2120)
        worse = floors[key] - .002
        other = ('expanded', 'Kakegawa Grand', 0, 1, 0, 112)
        improved = floors[other] + .25
        with self.assertRaisesRegex(ValueError, '1 factory dynamics regression'):
            self.check(change={key: {'step_db': worse, 'vu_high': -80 + worse},
                               other: {'step_db': improved, 'vu_high': -80 + improved}})

    def test_absolute_level_upper_bound_uses_the_matching_mic(self):
        expected, floors = dynamics.reference_rows()
        key = ('original', 'New York Grand', 1, 5, 1, 110)
        maximum = expected[key][2] + .01
        step = floors[key]
        with self.assertRaisesRegex(ValueError, 'exceeds B limit'):
            self.check(change={key: {'vu_low': maximum - step, 'vu_high': maximum}})

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
