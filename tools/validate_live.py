#!/usr/bin/env python3
"""Render every frozen grand case and report recording agreement and regressions.

Run only after fitting is frozen. This does not tune the model or overwrite the
preserved reference reports. The same feature extraction/gain rules are reused.
"""
import argparse
import hashlib
import importlib.util
import json
import platform
import subprocess
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('keyra_benchmark', ROOT/'Research/GrandPianoV2/tools/benchmark.py')
benchmark = importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--renderer', type=Path, default=ROOT/'build/keyra_preview_render')
    p.add_argument('--output', type=Path, default=ROOT/'Validation/live-grand.json')
    p.add_argument('--upright', action='store_true')
    a = p.parse_args()
    source = ROOT/('References/Upright/reference_features.json' if a.upright else 'Research/GrandPianoV2/benchmark/reference_features.json')
    references = json.loads(source.read_text())['samples']
    renders = ROOT/'out'/('upright' if a.upright else 'grand')
    renders.mkdir(parents=True, exist_ok=True)
    features, rows, timings = [], [], []
    for reference in references:
        path = renders/(reference['id']+'.wav')
        report = path.with_suffix('.json')
        # Solo recording comparison bypasses authored room and mechanical noise;
        # all notes share output gain and width. No per-note amplitude is fitted.
        command = [str(a.renderer.resolve()), '--output', str(path), '--rate', '48000',
                   '--seconds', '4.25', '--note', str(reference['midi']), '--velocity', str(reference['midi_velocity']),
                   '--param', f'instrument={2 if a.upright else 0}', '--param', 'noise=0', '--param', 'distance=0',
                   '--param', 'resonance=0', '--param', 'mic=0', '--report', str(report)]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL)
        with tempfile.TemporaryDirectory(prefix='keyra-live-analysis-') as temporary:
            midi = reference['midi']
            scientific = ('C','C#','D','D#','E','F','F#','G','G#','A','A#','B')[midi%12]+str(midi//12-1)
            alias = Path(temporary)/f"{scientific}v{reference['layer']}.wav"
            alias.symlink_to(path.resolve())
            model = benchmark.extract_features(alias, midi)
        model['path'] = str(path.relative_to(ROOT))
        model['id'] = reference['id']
        comparison = benchmark.compare_features(reference, model)
        features.append(model); rows.append(comparison); timings.append(json.loads(report.read_text()))
        print(f"{reference['id']} {reference['split']}: harmonics={comparison['harmonic_level_mae_db']:.2f}dB attack={comparison['attack_rise10_90_error_ms']:.2f}ms", flush=True)
    summary = benchmark.aggregate(rows)
    selected = [r for r in rows if r['split'].startswith('heldout')]
    heldout = benchmark.aggregate([{**r, 'split':'heldout_velocity'} for r in selected])['heldout_velocity']
    prior = None
    if not a.upright:
        old = json.loads((ROOT/'Research/GrandPianoV2/benchmark/candidate_report.json').read_text())['cases']
        prior = []
        for row in rows:
            baseline = next(x for x in old if x['id']==row['id'])
            keys = ('harmonic_level_mae_db','log_band_mae_db','partial_decay_slope_mae_db_per_second','attack_rise10_90_error_ms','envelope_mae_db')
            prior.append({'id':row['id'], 'split':row['split'],
                          'live_minus_preserved_error':{key:row[key]-baseline[key] if row[key] is not None and baseline[key] is not None else None for key in keys}})
    result = {'schema_version':1, 'reference_features':str(source.relative_to(ROOT)), 'reference_sha256':sha(source),
              'engine_sha256':sha(ROOT/'src/Piano.cpp'), 'calibration_sha256':sha(ROOT/'src/LiveCalibration.h'),
              'upright_calibration_sha256':sha(ROOT/'src/UprightCalibration.h') if (ROOT/'src/UprightCalibration.h').exists() else None,
              'renderer_sha256':sha(a.renderer), 'machine':platform.platform(), 'analysis':benchmark.ANALYSIS,
              'configuration':'48kHz, default tone/dynamics/gain, close AB, zero noise/distance/resonance',
              'limits':'Offline feature agreement is not a blind listening test. New modal surrogate differs from preserved nonlinear solver. Instrument/material/microphone alternatives require independent validation. Corpus velocity values are model input proxies.',
              'cases':rows, 'summary':summary, 'all_heldout':heldout, 'live_minus_preserved':prior,
              'render_wall_seconds_per_audio_second':{'mean':float(np.mean([t['wall_seconds_per_audio_second'] for t in timings])),
                                                      'maximum':max(t['wall_seconds_per_audio_second'] for t in timings)},
              'features':features}
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'all_heldout':heldout,'render_cost':result['render_wall_seconds_per_audio_second']},indent=2))


if __name__ == '__main__': main()
