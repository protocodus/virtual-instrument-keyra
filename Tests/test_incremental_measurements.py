"""Contract checks use public numeric fixtures; no decoding or optimizer call.

The separate integration fixture runs original exporter/residual operators on
the declared private TRAIN inputs and compares both frozen candidate headers.
"""
from pathlib import Path
import argparse
import copy
import gzip
import hashlib
import importlib.util
import json
import pickle
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / 'Tools'))
import update_modal_measurements as u
parser = argparse.ArgumentParser(add_help=False)
parser.add_argument('--operator-dir', type=Path, default=HERE / 'Tools')
parser.add_argument('--archive', type=Path, default=HERE / 'Tests/Fixtures/measurements/hamburg-accepted.json.gz')
CONFIG, remaining = parser.parse_known_args()
sys.argv = [sys.argv[0]] + remaining

class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # A portable validation fixture. Source/cache bytes deliberately cannot
        # be decoded/unpickled: unit checks must stop before observation access.
        # Only the public accepted numeric archive and current exporter are real.
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        root = Path(cls.temp.name)
        ref = lambda p: {'path': str(p.absolute()), 'sha256': u.digest(p)}
        archive = u.read_archive(CONFIG.archive)
        anchor = archive['measurements']['anchors'][0]
        rows, files, roles = [], [], {'not-training': 'dev'}
        # Hamburg's recipe: a 24-bit original cropped 20 ms before its preset
        # start into a 32-bit analysis WAV.
        for i, velocity in enumerate(anchor['velocities']):
            case = f'fixture-layer-{i}'
            p, original = root / (case + '.wav'), root / (case + '-original.wav')
            p.write_bytes(('must not decode ' + case).encode())
            original.write_bytes(('must not decode original ' + case).encode())
            rows.append({'id': case, 'velocity': velocity, 'wav': ref(p),
                         'provenance': {'kind': 'hamburg-preset-crop-v1', 'historical_cache_pin': u.digest(original),
                                        'original': ref(original), 'decoder': ref(CONFIG.operator_dir/'decode_hamburg.py'),
                                        'sample_rate': 48000, 'channels': 2, 'source_bits': 24,
                                        'analysis_bits': 32, 'frame_span': [40, 1000]}})
            files.append({'id': case, 'kind': 'note', 'midi': anchor['note'], 'start': 1000,
                          'wav_sha256': u.digest(original), 'source': original.name})
            roles[case] = 'train'
        (root/'corpus.json').write_bytes(u.json_bytes({'files': files}))
        (root/'split.json').write_bytes(u.json_bytes({'cases': roles}))
        for key in ['corpus', 'split']:
            archive['provenance'][key + '_sha256'] = u.digest(root/(key+'.json'))
        (root/'archive.json.gz').write_bytes(gzip.compress(u.json_bytes(u.encode(archive)), mtime=0))
        for name in ['old.pkl', 'new.pkl', 'selection.json']:
            (root/name).write_bytes(('must not open ' + name).encode())
        cls.fixture = {'schema': u.MANIFEST, 'model': archive['model'],
                       'accepted': ref(root/'archive.json.gz'),
                       'fitter': ref(CONFIG.operator_dir/'fit_realtime_modal.py'),
                       'analysis': ref(CONFIG.operator_dir/'piano_analysis.py'),
                       'baseline_analysis': ref(CONFIG.operator_dir/'piano_analysis.py'),
                       'corpus': ref(root/'corpus.json'), 'split': ref(root/'split.json'),
                       'targets': [{'note': anchor['note'], 'orders': [anchor['partials'][0]['order']],
                                    'conditioning': 'accepted-clock-floor-carrier', 'noise_policy': 'accepted',
                                    'analysis_options': {}, 'sources': rows,
                                    'baseline_cache': ref(root/'old.pkl'), 'candidate_cache': ref(root/'new.pkl'),
                                    'selection_receipt': ref(root/'selection.json')}]}

    def altered(self, change):
        value = copy.deepcopy(self.fixture)
        change(value)
        tmp = tempfile.TemporaryDirectory()
        path = Path(tmp.name) / 'manifest.json'
        path.write_bytes(u.json_bytes(value))
        self.addCleanup(tmp.cleanup)
        return path

    def rejects(self, change, message):
        path = self.altered(change)
        with patch.object(pickle, 'load', side_effect=AssertionError('pickle opened before preflight')):
            with self.assertRaisesRegex(u.InvalidInput, message):
                u.preflight(path)

    def test_no_target_exact_without_audio_or_cache(self):
        actual = u.operators
        def guarded(paths):
            fit, pa = actual(paths)
            pa.load = lambda *a, **k: self.fail('no-target decoded audio')
            return fit, pa
        manifest = self.altered(lambda m: m.update(targets=[]))
        with patch.object(u, 'operators', guarded), patch.object(pickle, 'load', side_effect=AssertionError('no-target opened cache')):
            content, receipt = u.generate(manifest)
        expected = u.read_archive(self.fixture['accepted']['path'])['provenance']['header_sha256']
        self.assertEqual(receipt['output_sha256'], expected)
        self.assertEqual(receipt['targets'], [])

    def test_wrong_model(self):
        self.rejects(lambda m: m.update(model='upright'), 'wrong model')

    def test_json_manifest_uses_utf8_under_non_utf8_default_locale(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / 'Žluťoučký klavír'
            root.mkdir()
            source = root / 'měření.bin'
            source.write_bytes(b'synthetic pinned input, no audio')
            value = {'source': {'path': str(source), 'sha256': u.digest(source)},
                     'attribution': 'Müller – Žižkov'}
            manifest = root / 'manifest.json'
            manifest.write_bytes(u.json_bytes(value))
            self.assertIn('Žižkov'.encode('utf-8'), manifest.read_bytes())
            original_read = Path.read_text
            def locale_read(path, encoding=None, errors=None):
                # Model a Windows non-UTF8 text locale without changing the
                # process locale or relying on installed system locales.
                return original_read(path, encoding=encoding or 'cp1252', errors=errors)
            with patch.object(Path, 'read_text', locale_read):
                loaded = u.read_json(manifest)
            self.assertEqual(loaded, value)
            pins = {}
            self.assertEqual(u.pinned(loaded['source'], root, pins), source)
            self.assertEqual(pins, {str(source): u.digest(source)})

    def test_maintainable_numeric_importer_roundtrip(self):
        manifest = self.altered(lambda m: m.update(targets=[]))
        content, receipt = u.generate(manifest)
        with tempfile.TemporaryDirectory() as directory:
            header = Path(directory)/'accepted.h'
            header.write_text(content)
            importer = u.module('test_numeric_importer', HERE/'Tools/import_modal_measurements.py')
            _, _, paths, _, _ = u.preflight(manifest)
            fit, _ = u.operators(paths)
            result = fit.header(fit.MODELS[self.fixture['model']], **importer.load(header))
            self.assertEqual(result, content)

    def test_wrong_source_hash(self):
        self.rejects(lambda m: m['targets'][0]['sources'][0]['wav'].update(sha256='0'*64), 'input hash mismatch')

    def test_wrong_cache_hash(self):
        self.rejects(lambda m: m['targets'][0]['candidate_cache'].update(sha256='0'*64), 'input hash mismatch')

    def test_nontrain_source_rejected_before_pickle(self):
        roles = u.read_json(self.fixture['split']['path'])['cases']
        case = next(k for k, v in roles.items() if v != 'train')
        self.rejects(lambda m: m['targets'][0]['sources'][0].update(id=case), 'non-TRAIN')

    def test_duplicate_note(self):
        self.rejects(lambda m: m['targets'].append(copy.deepcopy(m['targets'][0])), 'duplicate target')

    def test_duplicate_order(self):
        self.rejects(lambda m: m['targets'][0]['orders'].append(m['targets'][0]['orders'][0]), 'duplicate target order')

    def test_new_order_not_supported(self):
        self.rejects(lambda m: m['targets'][0].update(orders=[999]), 'membership changes unsupported')

    def test_conditioning_explicit(self):
        self.rejects(lambda m: m['targets'][0].update(conditioning='new-clock'), 'unsupported conditioning')

    def test_source_coordinates_exact(self):
        self.rejects(lambda m: m['targets'][0]['sources'][0].update(velocity=-1), 'source coordinates')

    def test_nonfinite_archive(self):
        with self.assertRaisesRegex(u.InvalidInput, 'nonfinite'):
            u.encode({'x': complex(float('nan'), 0)})

    def test_numeric_codec_preserves_complex_and_negative_zero(self):
        import math
        value = {'x': complex(-0., 2.), 'y': [-0., .012345678901234567]}
        decoded = u.decode(json.loads(u.json_bytes(u.encode(value))))
        self.assertEqual(value, decoded)
        self.assertEqual(math.copysign(1, decoded['x'].real), -1)
        self.assertEqual(math.copysign(1, decoded['y'][0]), -1)

    def test_archive_format_not_pickle(self):
        p = Path(self.fixture['accepted']['path'])
        value = json.loads(gzip.decompress(p.read_bytes()))
        self.assertEqual(value['schema'], u.SCHEMA)
        self.assertNotIn('residual', json.dumps(value))
        self.assertNotIn('amplitudes', json.dumps(value))

    def test_existing_output_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / 'header.h'
            p.write_bytes(b'accepted')
            with self.assertRaisesRegex(u.InvalidInput, 'refusing to overwrite'):
                u.publish(p, b'changed')
            self.assertEqual(p.read_bytes(), b'accepted')
            with self.assertRaisesRegex(u.InvalidInput, 'differs'):
                u.publish(p, b'changed', check=True)
            self.assertEqual(p.read_bytes(), b'accepted')

    def caches(self):
        import numpy as np
        t = copy.deepcopy(self.fixture['targets'][0])
        selected = {'theta': np.zeros(10), 'amplitudes': [np.ones((2, 4), complex) for q in t['sources']]}
        old = {'note': t['note'], 'cases': [q['id'] for q in t['sources']],
               'orders': t['orders'].copy(), 'freqs': np.array([440.]), 'sr': 48000,
               'fits': [selected], 'layers': [{'velocity': q['velocity'], 'residual': np.zeros((2, 2), np.float32)} for q in t['sources']]}
        analysis = Path(self.fixture['baseline_analysis']['path'])
        h = hashlib.sha256(analysis.read_bytes())
        for q in t['sources']:
            h.update(f"{q['id']}:{q['velocity']}:{q['provenance']['historical_cache_pin']}\n".encode())
        old['cache_key'] = h.hexdigest()
        new = copy.deepcopy(old)
        new['diagnostic_parent_cache_sha256'] = t['baseline_cache']['sha256']
        new['cache_key'] = ['explicit derived fixture', old['cache_key']]
        paths = {'baseline_cache': Path(t['baseline_cache']['path'])}
        return t, paths, [], old, new, analysis

    def test_changed_carrier_rejected(self):
        args = self.caches()
        args[4]['freqs'][0] += 1
        with self.assertRaisesRegex(u.InvalidInput, 'carrier/order/observation'):
            u.validate_caches(*args)

    def test_historical_cache_options_not_relabelled(self):
        args = self.caches()
        args[0]['analysis_options']['min_layers'] = 1
        with self.assertRaisesRegex(u.InvalidInput, 'stale original analysis options'):
            u.validate_caches(*args)

    def test_invalid_options_rejected_before_pcm_or_pickle(self):
        manifest = self.altered(lambda m: m['targets'][0].update(analysis_options={'min_layers': 99}))
        with (patch.object(u.source_provenance, 'verify', side_effect=AssertionError('PCM decoded')),
              patch.object(pickle, 'load', side_effect=AssertionError('cache opened'))):
            with self.assertRaisesRegex(u.InvalidInput, 'nondefault analysis options'):
                u.generate(manifest)

    def test_selected_nonfinite_fit_rejected_before_audio(self):
        args = self.caches()
        args[4]['fits'][0]['theta'][0] = float('nan')
        with self.assertRaisesRegex(u.InvalidInput, 'invalid selected pole'):
            u.validate_caches(*args)

    def test_declared_finite_fit_passes_cache_contract(self):
        args = self.caches()
        args[4]['fits'][0]['amplitudes'][0][0, 0] += .1
        u.validate_caches(*args)

    def test_multiple_target_receipts_do_not_include_or_mutate_source_records(self):
        """Exercise the real collector with synthetic caches and stub operators."""
        import numpy as np
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            partial = {'order': 1, 'rise_seconds': .001, 'rise_slope': 0., 'lanes': [1.]}
            accepted = {
                'anchors': [{'note': note, 'f1': 440., 'velocities': [64],
                             'onset_rise': [.001], 'partials': [copy.deepcopy(partial)]}
                            for note in [72, 81]],
                'noise': {'anchors': [{'level': 0.}, {'level': 0.}]},
                'halo': {'keys': [], 'cents': []}}
            formatter = lambda model, **values: json.dumps(values, sort_keys=True)
            archive = {'measurements': accepted,
                       'clocks': [{'note': note, 'layer_shift_ms': [0.]} for note in [72, 81]],
                       'provenance': {'header_sha256': hashlib.sha256(formatter({}, **accepted).encode()).hexdigest()}}
            archive_path = root / 'accepted.json'
            archive_path.write_bytes(u.json_bytes(archive))
            targets = []
            for note in [72, 81]:
                cache = root / f'{note}.pkl'
                cache.write_bytes(pickle.dumps({'note': note}))
                target = {'note': note, 'orders': [1], 'analysis_options': {}, 'noise_policy': 'accepted'}
                sources = [{'kind': 'hamburg-preset-crop-v1', 'case': f'n{note}v1r1'}]
                targets.append((target, {'baseline_cache': cache, 'candidate_cache': cache},
                                [root / f'n{note}v1r1.wav'], sources))
            original_sources = copy.deepcopy([row[3] for row in targets])
            pins = {str(archive_path): u.digest(archive_path)}
            paths = {'accepted': archive_path, 'baseline_analysis': archive_path}
            fit = SimpleNamespace(MODELS={'fixture': {}}, analysis_options=lambda model: {},
                                  header=formatter, number=lambda value: str(value), string_pitches=lambda values: {})
            def conditioned(new, *args):
                changed = copy.deepcopy(partial)
                changed['lanes'] = [float(new['note'])]
                return {'partials': [changed], 'onset_rise': np.array([.001])}, [{'synthetic_clock': 0.}]
            with (patch.object(u, 'preflight', return_value=({'model': 'fixture'}, archive, paths, targets, pins)),
                  patch.object(u, 'operators', return_value=(fit, object())),
                  patch.object(u, 'validate_caches'), patch.object(u, 'residual_proof', return_value=[]),
                  patch.object(u, 'fixed_clock_anchor', side_effect=conditioned),
                  patch.object(u.source_provenance, 'verify', side_effect=lambda row: dict(row, verified=True)),
                  patch.object(u.source_provenance, 'runtime', return_value={})):
                first_content, first = u.generate(root / 'manifest.json')
                second_content, second = u.generate(root / 'manifest.json')
            self.assertEqual([row['note'] for row in first['targets']], [72, 81])
            self.assertEqual([row['orders'] for row in first['targets']], [[1], [1]])
            self.assertEqual([row['case'] for row in first['source_proofs']], ['n72v1r1', 'n81v1r1'])
            self.assertEqual([row[3] for row in targets], original_sources)
            self.assertEqual(first_content, second_content)
            self.assertEqual(first, second)

if __name__ == '__main__':
    unittest.main(verbosity=2)
