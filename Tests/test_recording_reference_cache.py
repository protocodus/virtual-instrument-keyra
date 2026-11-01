"""Recording benchmarks must never reuse another piano's acoustic reference."""
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'Tools'))
import benchmark_recordings as benchmark


class RecordingReferenceCacheTests(unittest.TestCase):
    def test_shared_case_names_keep_distinct_recordings(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cache = root / 'cache'
            for piano, contents in [('grand', b'grand recording'), ('upright', b'upright recording')]:
                (root / piano).mkdir()
                (root / piano / 'n60v1r1.wav').write_bytes(contents)
            def measure(path, note):
                return {'source': path.read_bytes().decode(), 'note': note, 'missing': None}
            with patch.object(benchmark, 'features', side_effect=measure) as measured:
                grand = benchmark.cached_reference('n60v1r1', 60, cache, root / 'grand')
                upright = benchmark.cached_reference('n60v1r1', 60, cache, root / 'upright')
                again = benchmark.cached_reference('n60v1r1', 60, cache, root / 'grand')
            self.assertNotEqual(grand['source'], upright['source'])
            self.assertEqual(grand, again)
            self.assertEqual(measured.call_count, 2)

    def test_content_and_pitch_invalidate_even_with_same_size_and_timestamp(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            wav = root / 'n60v1r1.wav'
            wav.write_bytes(b'first')
            stamp = wav.stat()
            def measure(path, note):
                return {'source': path.read_bytes().decode(), 'note': note}
            with patch.object(benchmark, 'features', side_effect=measure) as measured:
                first = benchmark.cached_reference('n60v1r1', 60, root / 'cache', root)
                wav.write_bytes(b'other')
                os.utime(wav, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))
                changed = benchmark.cached_reference('n60v1r1', 60, root / 'cache', root)
                retagged = benchmark.cached_reference('n60v1r1', 61, root / 'cache', root)
            self.assertNotEqual(first['source'], changed['source'])
            self.assertEqual(retagged['note'], 61)
            self.assertEqual(measured.call_count, 3)


if __name__ == '__main__':
    unittest.main()
