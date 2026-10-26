"""Verify frozen-score replay works in a relocated, clean source checkout."""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


TOOL = Path(__file__).resolve().parents[1]/'Tools/verify_recording_parity.py'
SPEC = importlib.util.spec_from_file_location('recording_parity', TOOL)
parity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(parity)


class RecordingParityPaths(unittest.TestCase):
    def test_clean_relocated_checkout_reconstructs_both_score_sources(self):
        with tempfile.TemporaryDirectory(prefix='keyra-relocated-checkout-') as temporary:
            root = Path(temporary)/'different checkout'
            original = root/'Research/GrandPianoV2/benchmark/events/C4v8.events'
            original.parent.mkdir(parents=True)
            original.write_text('0.100000 on 60 61\n4.150000 off 60 0\n')
            fresh_text = '0.100000 on 39 61\n4.150000 off 39 0\n'
            manifest = root/'Docs/research/fresh-recording-holdout-2026-10-26.json'
            manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({
                'locked_before_downloading': True, 'locked_before_scoring': True,
                'samples': [{'id': 'D#2v8', 'midi': 39, 'midi_velocity': 61}],
            }))
            for name in ('KeyraEngine.cpp', 'KeyraEngine.h', 'MeasuredModalData.h'):
                path = root/'Source/DSP'/name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text('fixture')
            reports = root/'Docs/validation'
            reports.mkdir(parents=True)
            for report, identity, text in (
                (parity.ORIGINAL_REPORT, 'C4v8', original.read_text()),
                (parity.FRESH_REPORT, 'D#2v8', fresh_text),
            ):
                stale = '/missing/original/workspace/build/fresh-recording-holdout/events/'
                receipt = {'id': identity,
                           'command': ['/obsolete/renderer', '--events', stale+identity+'.events',
                                       '--output', '/obsolete/output.wav'],
                           'output_sha256': hashlib.sha256(text.encode()).hexdigest()}
                (reports/report).write_text(json.dumps({
                    'variants': {'product_default': {'render_receipts': [receipt]}},
                }))
            renderer = root/'new-renderer'
            renderer.write_text('fixture')
            destination = root/'parity-result.json'
            observed = []

            def render(command, **_kwargs):
                events = Path(command[command.index('--events')+1])
                observed.append(events)
                Path(command[command.index('--output')+1]).write_bytes(events.read_text().encode())

            # No ignored build directory or original absolute event path exists.
            self.assertFalse((root/'build').exists())
            with mock.patch.object(parity, 'ROOT', root), \
                    mock.patch.object(sys, 'argv', ['verify_recording_parity.py',
                                                   '--renderer', str(renderer),
                                                   '--output', str(destination)]), \
                    mock.patch.object(parity.subprocess, 'run', side_effect=render):
                self.assertEqual(parity.main(), 0)
            result = json.loads(destination.read_text())
            self.assertEqual(result['case_count'], 2)
            self.assertTrue(result['all_identical'])
            self.assertEqual(observed[0], original)
            self.assertEqual(observed[1].name, 'D#2v8.events')
            self.assertNotIn('build', observed[1].parts)
            self.assertFalse((root/'build').exists())

    def test_unlocked_fresh_manifest_is_rejected(self):
        with tempfile.TemporaryDirectory(prefix='keyra-unlocked-manifest-') as temporary:
            root = Path(temporary)
            manifest = root/'Docs/research/fresh-recording-holdout-2026-10-26.json'
            manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({'locked_before_downloading': False,
                                            'locked_before_scoring': True, 'samples': []}))
            with self.assertRaisesRegex(ValueError, 'locked before'):
                parity.event_input(root, parity.FRESH_REPORT, 'D#2v8', root/'scores')


if __name__ == '__main__':
    unittest.main()
