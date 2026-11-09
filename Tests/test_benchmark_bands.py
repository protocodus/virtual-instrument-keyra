"""The recording benchmark scores a third-octave band only where both spectra have bins."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Tools'))
import benchmark_recordings as benchmark
import piano_analysis as pa


class BenchmarkBandTests(unittest.TestCase):
    def empty(self, sr):
        return [round(float(f), 1) for f, has in zip(pa.THIRD_OCTAVE, benchmark.band_members(sr).any(axis=0)) if not has]

    def test_the_window_misses_low_bands_by_rate(self):
        # 40 ms windows padded to 4096 bins: 10.8 Hz apart at 44.1 kHz, 11.7 Hz at 48 kHz.
        self.assertEqual(self.empty(44100), [24.8])
        self.assertEqual(self.empty(48000), [19.7, 31.2])

    def test_a_band_neither_rate_misses_is_scored(self):
        both = benchmark.band_members(44100).any(axis=0) & benchmark.band_members(48000).any(axis=0)
        self.assertTrue(both[pa.THIRD_OCTAVE > 35].all())


if __name__ == '__main__':
    unittest.main()
