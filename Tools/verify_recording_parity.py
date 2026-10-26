#!/usr/bin/env python3
"""Replay frozen recording-benchmark commands through a candidate renderer.

This closes the link between frozen tone scores and subsequent controller/UI
changes. Every saved live-render WAV must match exactly; no metric is refitted,
no reference audio is opened, and the benchmark reports remain immutable.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_REPORT = 'recording-benchmark-2026-10-26.json'
FRESH_REPORT = 'recording-benchmark-fresh-2026-10-26.json'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def event_input(root, report_name, identity, temporary):
    """Resolve a score from checkout data, never a historical workspace path."""
    if not identity or Path(identity).name != identity or '\\' in identity:
        raise ValueError(f'Invalid recording case ID: {identity!r}')
    if report_name == ORIGINAL_REPORT:
        path = root/'Research/GrandPianoV2/benchmark/events'/(identity+'.events')
        if not path.is_file():
            raise ValueError(f'Missing tracked recording score: {path}')
        return path
    if report_name != FRESH_REPORT:
        raise ValueError(f'Unknown recording report: {report_name}')
    manifest_path = root/'Docs/research/fresh-recording-holdout-2026-10-26.json'
    manifest = json.loads(manifest_path.read_text())
    if not manifest.get('locked_before_downloading') or not manifest.get('locked_before_scoring'):
        raise ValueError('Fresh recording cases must be locked before downloading and scoring')
    matches = [sample for sample in manifest['samples'] if sample['id'] == identity]
    if len(matches) != 1:
        raise ValueError(f'Fresh recording case is missing or duplicated: {identity}')
    sample = matches[0]
    note, velocity = sample['midi'], sample['midi_velocity']
    if type(note) is not int or type(velocity) is not int or not 0 <= note <= 127 or not 1 <= velocity <= 127:
        raise ValueError(f'Invalid note/velocity in fresh recording case: {identity}')
    directory = temporary/'fresh-events'
    directory.mkdir(parents=True, exist_ok=True)
    path = directory/(identity+'.events')
    # Same event chronology as evaluate_fresh_recordings.py. Reconstructing
    # this MIDI-only input needs neither ignored build files nor reference audio.
    path.write_text(f'0.100000 on {note} {velocity}\n4.150000 off {note} 0\n')
    return path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--renderer', type=Path, default=ROOT/'build/keyra_render')
    parser.add_argument('--output', type=Path,
                        default=ROOT/'Docs/validation/final-recording-parity-2026-10-26.json')
    args = parser.parse_args()
    renderer = args.renderer.resolve()
    result = {
        'scope': 'Exact WAV parity against frozen live recording benchmarks; no refitting',
        'renderer_sha256': sha(renderer),
        'engine_sha256': sha(ROOT/'Source/DSP/KeyraEngine.cpp'),
        'engine_header_sha256': sha(ROOT/'Source/DSP/KeyraEngine.h'),
        'measured_data_sha256': sha(ROOT/'Source/DSP/MeasuredModalData.h'),
        'reports': [],
    }
    failed = []
    with tempfile.TemporaryDirectory(prefix='keyra-recording-parity-') as temporary:
        output = Path(temporary)/'case.wav'
        for name in (ORIGINAL_REPORT, FRESH_REPORT):
            path = ROOT/'Docs/validation'/name
            report = json.loads(path.read_text())
            cases = []
            for variant, data in report['variants'].items():
                for receipt in data.get('render_receipts', []):
                    command = list(receipt['command'])
                    command[0] = str(renderer)
                    command[command.index('--events')+1] = str(
                        event_input(ROOT, name, receipt['id'], Path(temporary)))
                    command[command.index('--output')+1] = str(output)
                    subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
                    actual = sha(output)
                    identical = actual == receipt['output_sha256']
                    cases.append({'id': receipt['id'], 'variant': variant,
                                  'sha256': actual, 'identical': identical})
                    if not identical:
                        failed.append(f'{name}:{variant}:{receipt["id"]}')
            result['reports'].append({'path': name, 'sha256': sha(path), 'cases': cases})
    result['all_identical'] = not failed
    result['case_count'] = sum(len(r['cases']) for r in result['reports'])
    result['mismatches'] = failed
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({'cases': result['case_count'], 'mismatches': failed}))
    return int(bool(failed))


if __name__ == '__main__':
    raise SystemExit(main())
