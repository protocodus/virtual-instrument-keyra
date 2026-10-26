#!/usr/bin/env python3
"""Compare one fixed training note at 96/192 kHz without changing the benchmark.

Render commands, input hashes and the one-case scope are preserved in the JSON.
The two temporary WAVs belong in build/, which is excluded from the delivery.
"""
from __future__ import annotations
import json
from pathlib import Path
import tempfile

import numpy as np

from benchmark import ANALYSIS, compare_features, extract_features, load_audio, sha256

ROOT = Path(__file__).resolve().parents[1]
METRICS = [
    'log_band_mae_db', 'harmonic_level_mae_db', 'envelope_mae_db',
    'partial_decay_slope_mae_db_per_second', 'absolute_f1_error_cents',
    'partial_tuning_mae_cents', 'attack_rise10_90_error_ms',
]


def row(path, field):
    data = json.loads((ROOT / path).read_text())
    return next(x for x in data[field] if x['id'] == 'C4v12')


def extract_named(path):
    # Keep the frozen extractor's strict reference-style filename convention.
    with tempfile.TemporaryDirectory(prefix='grand-rate-check-') as directory:
        alias = Path(directory) / 'C4v12.wav'
        alias.symlink_to(path)
        return extract_features(alias)


def main():
    frozen = row('benchmark/candidate_report_features.json', 'samples')
    ref = row('benchmark/reference_features.json', 'samples')
    manifest = json.loads((ROOT / 'benchmark/candidate/render-manifest.json').read_text())
    original = next(r for r in manifest['renders'] if r['id'] == 'C4v12')
    provenance = json.loads((ROOT / 'build/grand.provenance.json').read_text())
    paths = {
        'source': ROOT / 'src/grand.cpp',
        'calibration_header': ROOT / 'src/calibration.h',
        'current_binary': ROOT / 'build/grand',
        'benchmark_binary': ROOT / 'build/grand_candidate',
        'current_binary_provenance': ROOT / 'build/grand.provenance.json',
        'score': ROOT / 'benchmark/events/C4v12.events',
        'benchmark_extractor': ROOT / 'tools/benchmark.py',
        'check_script': Path(__file__).resolve(),
        'reference_features': ROOT / 'benchmark/reference_features.json',
        'candidate_features': ROOT / 'benchmark/candidate_report_features.json',
        'candidate_manifest': ROOT / 'benchmark/candidate/render-manifest.json',
        'reference_audio': ROOT / 'reference/wav/C4v12.wav',
        'frozen_96k_audio': ROOT / 'benchmark/candidate/C4v12.wav',
        'current_96k_audio': ROOT / 'build/C4v12-96k-ratecheck.wav',
        'current_192k_audio': ROOT / 'build/C4v12-192k.wav',
    }
    inputs = {key: {'path': str(path.relative_to(ROOT)), 'sha256': sha256(path)}
              for key, path in paths.items()}
    assert inputs['source']['sha256'] == provenance['solver_source_sha256'] == manifest['source_sha256']
    assert inputs['calibration_header']['sha256'] == provenance['calibration_sha256'] == manifest['calibration_sha256']
    assert inputs['current_binary']['sha256'] == provenance['binary_sha256']
    assert inputs['benchmark_binary']['sha256'] == manifest['engine_sha256']
    assert inputs['score']['sha256'] == original['score_sha256']
    assert inputs['frozen_96k_audio']['sha256'] == frozen['sha256'] == original['audio_sha256']
    assert inputs['reference_audio']['sha256'] == ref['sha256']
    f96 = extract_named(paths['current_96k_audio'])
    f192 = extract_named(paths['current_192k_audio'])
    assert f96['sample_rate'] == 96000 and f192['sample_rate'] == 192000
    assert f96['duration_seconds'] == f192['duration_seconds'] == frozen['duration_seconds'] == 4.35
    comparisons = {
        'frozen_96k_vs_recording': compare_features(ref, frozen),
        'current_96k_vs_recording': compare_features(ref, f96),
        'current_192k_vs_recording': compare_features(ref, f192),
        'current_192k_vs_current_96k': compare_features(f96, f192),
        'current_96k_vs_frozen_96k': compare_features(frozen, f96),
    }
    _, old_audio = load_audio(paths['frozen_96k_audio'])
    _, new_audio = load_audio(paths['current_96k_audio'])
    assert old_audio.shape == new_audio.shape
    build_difference = float(np.sqrt(np.mean((old_audio-new_audio)**2)/max(np.mean(old_audio**2), 1e-30)))
    feature_keys = ['sample_rate', 'onset_seconds', 'f1_hz', 'B', 'confidence',
                    'rms_residual_cents', 'early_rms', 'window_rms', 'attack']
    render_metadata = {str(rate): json.loads((ROOT / f'validation/C4v12-{rate}k-render.json').read_text())
                       for rate in (96, 192)}
    result = {
        'schema_version': 1,
        'case': {'id': 'C4v12', 'midi': 60, 'velocity': 93, 'split': 'train', 'duration_seconds': 4.35},
        'scope': 'One-case sample-rate sensitivity check at C4, velocity 93. This is not formal numerical convergence, a keyboard-wide guarantee, or validation of polyphonic/pedal behavior. No parameters were refitted.',
        'analysis': ANALYSIS,
        'inputs': inputs,
        'source_and_calibration_match_frozen_benchmark': True,
        'same_binary_used_for_current_96k_and_192k': True,
        'current_and_benchmark_binaries_identical': inputs['current_binary']['sha256'] == inputs['benchmark_binary']['sha256'],
        'current_96k_vs_frozen_96k_raw_relative_rms_difference': build_difference,
        'render_commands': [
            'build/grand --events benchmark/events/C4v12.events --output build/C4v12-96k-ratecheck.wav --sample-rate 96000 --duration 4.35 --metrics validation/C4v12-96k-render.json',
            'build/grand --events benchmark/events/C4v12.events --output build/C4v12-192k.wav --sample-rate 192000 --duration 4.35 --metrics validation/C4v12-192k-render.json',
        ],
        'render_metrics': render_metadata,
        'features': {label: {key: feature[key] for key in feature_keys}
                     for label, feature in [('reference', ref), ('frozen_96k', frozen), ('current_96k', f96), ('current_192k', f192)]},
        'comparisons': comparisons,
        'recording_error_change_192k_minus_frozen_96k': {
            key: comparisons['current_192k_vs_recording'][key] - comparisons['frozen_96k_vs_recording'][key]
            for key in METRICS
        },
        'interpretation': 'The direct rate comparison uses the frozen onset, stereo power, masks and one early gain definition. Differences include finite-step integration, sample-rate-dependent observation and extraction resolution. No waveform or window-specific alignment/gain was fitted.',
        'delivery_note': 'Raw rate-check WAVs are retained only under build/ and excluded from the final package.',
    }
    out = ROOT / 'validation/rate-convergence.json'
    out.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'output': str(out), 'direct_rate_metrics': comparisons['current_192k_vs_current_96k'],
                      'recording_error_change': result['recording_error_change_192k_minus_frozen_96k'],
                      'build_relative_rms_difference': build_difference}, indent=2))


if __name__ == '__main__':
    main()
