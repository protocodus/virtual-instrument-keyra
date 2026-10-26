#!/usr/bin/env python3
"""Extract only locked full-range TRAIN recordings, preserving censored tails.

The C8 soft source is shorter than the frozen 3.5-second late window. Its final
window/envelope are explicitly truncated, never zero-padded or extrapolated.
Fresh evaluation recordings have no extraction mode in this tool.
"""
from __future__ import annotations
import importlib.util
import json
import math
from pathlib import Path

import numpy as np
from scipy import ndimage

from fetch_full_range_grand import PROJECT, ROOT, locked_inputs, load_pcm_helper, sha


def load_benchmark():
    path = PROJECT / 'Research/GrandPianoV2/tools/benchmark.py'
    spec = importlib.util.spec_from_file_location('keyra_full_range_benchmark', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def censored_features(path, midi, benchmark, analysis_windows_seconds=None,
                      envelope_times_seconds=None, max_analysis_seconds=None):
    """Frozen formulas on short-note support, or exact explicitly paired windows.

    Explicit comparison windows must be fully supported by the counterpart.
    Only default recording windows are clipped to an actual short source.
    """
    path = Path(path)
    stem, _, layer = benchmark.identity(path)
    sr, full = benchmark.load_audio(path)
    onset, onset_detail = benchmark.onset_index(full, sr)
    maximum = 4. if max_analysis_seconds is None else min(4., float(max_analysis_seconds))
    x = full[onset:min(len(full), onset + int(math.ceil(maximum * sr - 1e-8)))]
    available = len(x) / sr
    if available < 1.6:
        raise RuntimeError(f'Too little source support for comparable early windows: {path}')
    requested = benchmark.WINDOWS if analysis_windows_seconds is None else analysis_windows_seconds
    if any(not np.isfinite([lo, hi]).all() or lo < 0 or hi <= lo for lo, hi in requested):
        raise RuntimeError('Invalid comparison windows')
    if analysis_windows_seconds is not None and any(hi > available + 1e-9 for _, hi in requested):
        raise RuntimeError('Counterpart does not fully support the requested reference windows')
    windows = [(float(lo), min(float(hi), available)) for lo, hi in requested if available > lo + .01]
    if len(windows) != len(requested):
        raise RuntimeError('Source does not support every requested comparison window')
    pitch = benchmark.fit_pitch(x, sr, midi)
    f1, B = pitch['f1_hz'], pitch['B']
    count = max(3, min(48, int(16000 / f1))) if pitch['B_identifiable'] else 1
    ns = np.arange(1, count + 1)
    frequencies = benchmark.partial_frequencies(f1, B, ns)
    keep = frequencies < min(17000, sr * .44)
    ns, frequencies = ns[keep], frequencies[keep]
    early = x[int(.05 * sr):int(.75 * sr)]
    early_power = max(float(np.mean(early * early)), 1e-24)
    partial_power, band_power, rms_windows = [], [], []
    for lo, hi in windows:
        section = x[int(lo * sr):int(hi * sr)]
        f, power = benchmark.spectrum(section, sr)
        partial_power.append([
            benchmark.integrated_power(f, power,
                center - min(.38 * f1, max(3 / (hi - lo), .004 * center)),
                center + min(.38 * f1, max(3 / (hi - lo), .004 * center)))
            for center in frequencies])
        band_power.append([benchmark.integrated_power(f, power, a, b)
                           for a, b in zip(benchmark.BAND_EDGES[:-1], benchmark.BAND_EDGES[1:])])
        rms_windows.append(float(np.sqrt(np.mean(section * section))))
    partial_power = np.asarray(partial_power)
    decays = benchmark.decay_features(x, sr, frequencies, f1)
    envelope_power = ndimage.uniform_filter1d(np.mean(x * x, axis=1), max(3, int(.005 * sr)), mode='nearest')
    envelope = np.sqrt(np.maximum(envelope_power, 0))
    attack_limit = min(len(envelope), int(.15 * sr))
    peak = float(np.max(envelope[:attack_limit]))
    crossings = {}
    for fraction in (.1, .5, .9):
        indices = np.flatnonzero(envelope[:attack_limit] >= fraction * peak)
        crossings[f't{int(fraction * 100)}_seconds'] = float(indices[0] / sr) if len(indices) else None
    times = (np.arange(.02, min(3.5, (len(x) - 1) / sr) + 1e-9, .02)
             if envelope_times_seconds is None else np.asarray(envelope_times_seconds, dtype=float))
    if not np.isfinite(times).all() or np.any(times < 0) or np.any(times > (len(x) - 1) / sr + 1e-9):
        raise RuntimeError('Requested envelope times exceed actual source support')
    envelope_samples = np.interp(times * sr, np.arange(len(envelope)), envelope)
    return {'id': stem, 'path': str(path.resolve()), 'sha256': sha(path),
            'midi': midi, 'layer': layer, 'midi_velocity': benchmark.MIDI_VELOCITIES[layer],
            'split': 'train', 'sample_rate': sr, 'duration_seconds': len(full) / sr,
            'channels': full.shape[1], 'onset_seconds': onset / sr, 'onset_details': onset_detail,
            **pitch, 'early_rms': float(np.sqrt(early_power)), 'window_rms': rms_windows,
            'analysis_windows_seconds': windows, 'available_seconds_after_onset': available,
            'right_censored': True,
            'censoring': 'Last analysis window and envelope stop at actual source end. No padding or extrapolation; decay fits use only observed STFT frames.',
            'attack': dict(crossings, rise10_90_seconds=crossings['t90_seconds'] - crossings['t10_seconds'],
                           definition='5ms RMS envelope rise within first150ms; not hammer contact duration'),
            'band_edges_hz': benchmark.BAND_EDGES.tolist(), 'band_power': band_power,
            'envelope_times_seconds': times.tolist(), 'envelope_rms': envelope_samples.tolist(),
            'partials': [{'n': int(n), 'frequency_hz': float(hz),
                          'powers': partial_power[:, j].tolist(),
                          'relative_db': (10 * np.log10(np.maximum(partial_power[:, j], 1e-30) / early_power)).tolist(),
                          'decay': decays[j]} for j, (n, hz) in enumerate(zip(ns, frequencies))]}


def quality_diagnostic(path, row, benchmark):
    sr, full = benchmark.load_audio(path)
    onset = round(row['onset_seconds'] * sr)
    aligned = full[onset:]
    early = aligned[int(.05 * sr):int(.75 * sr)]
    f, power = benchmark.spectrum(early, sr)
    early_power = max(float(np.mean(early * early)), 1e-30)
    bands = {'subsonic_0_20': (0, 20), 'low_20_31_25': (20, 31.25),
             'low_31_25_62_5': (31.25, 62.5), 'mains_proxy_48_52': (48, 52)}
    band_db = {name: float(10 * np.log10(max(benchmark.integrated_power(f, power, a, b), 1e-30) / early_power))
               for name, (a, b) in bands.items()}
    center = row['f1_hz']
    width = min(.25 * center, max(3., .004 * center))
    peak = benchmark.integrated_power(f, power, center - width, center + width)
    background = (benchmark.integrated_power(f, power, center - 3 * width, center - 2 * width)
                  + benchmark.integrated_power(f, power, center + 2 * width, center + 3 * width))
    prominence = float(10 * np.log10(max(peak, 1e-30) / max(background, 1e-30)))
    last = full[-min(len(full), sr // 2):]
    tail_power = max(float(np.mean(last * last)), 1e-30)
    return {'id': row['id'], 'role': 'train', 'source_duration_seconds': len(full) / sr,
            'available_seconds_after_onset': len(aligned) / sr,
            'sample_peak_dbfs': float(20 * np.log10(max(float(np.max(np.abs(full))), 1e-30))),
            'samples_at_or_above_full_scale': int(np.count_nonzero(np.abs(full) >= 1)),
            'pitch_confidence': row['confidence'], 'B_identifiable': row['B_identifiable'],
            'fit_partial_count': row['fit_partial_count'], 'reported_partial_count': len(row['partials']),
            'early_low_band_db_relative_early_power': band_db,
            'fundamental_band_to_two_neighbor_bands_db': prominence,
            'early_power_over_last_half_second_db': float(10 * np.log10(early_power / tail_power)),
            'late_window_power_relative_early_db': float(20 * np.log10(max(row['window_rms'][-1], 1e-30) / row['early_rms'])),
            'flags': {'right_censored': row.get('right_censored', False),
                      'fundamental_below_frozen_broadband_floor': row['f1_hz'] < 31.25,
                      'limited_or_unidentified_pitch_fit': row['confidence'] != 'good',
                      'upper_register_few_partials': row['midi'] >= 96 and row['fit_partial_count'] < 4,
                      'mains_proxy_overlaps_possible_partial': any(abs(p['frequency_hz'] - 50) < 10 for p in row['partials'])},
            'limits': 'Neighbor-band prominence and edited-file tail power are diagnostics, not measured SNR/noise floor. The48–52Hz proxy may include actual piano energy. Source recording/editing/pedal conditions are unknown.'}


def main():
    split, manifest = locked_inputs()
    if not manifest['initial_training_acquisition_verified']:
        raise RuntimeError('Acquire and authenticate the training corpus first')
    for name in split['reserved_fresh_evaluation_ids']:
        if (ROOT / f'recordings/{name}.wav').exists():
            raise RuntimeError(f'Unexpected decoded fresh evaluation recording: {name}')
    original_path = PROJECT / manifest['original_reference_features']
    expanded_path = PROJECT / manifest['expanded_train_features']
    if sha(original_path) != manifest['original_reference_features_sha256'] or sha(expanded_path) != manifest['expanded_train_features_sha256']:
        raise RuntimeError('Frozen existing training measurements changed')
    benchmark, pcm_helper = load_benchmark(), load_pcm_helper()
    original = {r['id']: r for r in json.loads(original_path.read_text())['samples'] if r['split'] == 'train'}
    expanded = {r['id']: r for r in json.loads(expanded_path.read_text())['samples']}
    metadata = {r['id']: r for r in manifest['samples']}
    rows, diagnostics = [], []
    for name in split['training_ids']:
        item = metadata[name]
        if item['role'] != 'train' or item['layer'] not in (4, 12):
            raise RuntimeError(f'Refuse evaluation feature extraction: {name}')
        path = ROOT / item['wav_path']
        if pcm_helper.decoded_pcm_identity(path) != item['decoded_pcm']:
            raise RuntimeError(f'Training PCM changed: {name}')
        if name in original:
            row = dict(original[name])
            row['feature_provenance'] = 'Frozen original TRAIN10 numeric measurements reused unchanged.'
        else:
            sr, audio = benchmark.load_audio(path)
            onset, _ = benchmark.onset_index(audio, sr)
            if (len(audio) - onset) / sr < 3.5:
                row = censored_features(path, item['midi'], benchmark)
            else:
                row = benchmark.extract_features(path, item['midi'])
            row['frozen_extractor_default_split'] = row['split']
            row['split'] = 'train'
            row['path'] = str(path.relative_to(PROJECT))
            row['feature_provenance'] = 'New locked TRAIN acquisition; frozen formulas with explicit available-support handling for right-censored source.'
        row['full_range_role'] = 'train'
        row['midi_velocity'] = item['midi_velocity']
        row['analysis_windows_seconds'] = row.get('analysis_windows_seconds', benchmark.WINDOWS)
        row['right_censored'] = row.get('right_censored', False)
        rows.append(row)
        diagnostics.append(quality_diagnostic(path, row, benchmark))
        print(f'{name}: TRAIN, f1={row["f1_hz"]:.5f} Hz, {row["confidence"]}, censored={row["right_censored"]}', flush=True)
    by_id = dict(expanded)
    for row in rows:
        if row['id'] not in by_id:
            by_id[row['id']] = row
    if set(by_id) != set(split['combined_training_ids']) or len(rows) != 18:
        raise RuntimeError('Combined training inventory mismatch')
    common = {'schema_version': 1, 'analysis': benchmark.ANALYSIS,
              'source_commit': split['source_commit'], 'split_sha256': sha(ROOT / 'split.json'),
              'manifest_sha256': sha(ROOT / 'manifest.json'),
              'extractor_sha256': sha(Path(__file__)),
              'frozen_benchmark_sha256': sha(PROJECT / 'Research/GrandPianoV2/tools/benchmark.py'),
              'fresh_reserved_recordings_opened': False,
              'right_censoring_policy': 'Respect per-row analysis_windows_seconds/envelope support; never pad missing recorded tails. Fixed broadband edges remain31.25Hz upward; separate QC includes20–31.25Hz.'}
    (ROOT / 'train_features.json').write_text(json.dumps(dict(common, samples=rows), indent=2, allow_nan=False) + '\n')
    combined = [by_id[name] for name in split['combined_training_ids']]
    (ROOT / 'combined_train_features.json').write_text(json.dumps(dict(common,
        expanded_training_features_sha256=sha(expanded_path), samples=combined), indent=2, allow_nan=False) + '\n')
    qc = {'schema_version': 1, 'scope': 'Locked TRAIN18 only; no evaluation audio used.',
          'split_sha256': sha(ROOT / 'split.json'), 'train_features_sha256': sha(ROOT / 'train_features.json'),
          'samples': diagnostics}
    (ROOT / 'training-quality.json').write_text(json.dumps(qc, indent=2, allow_nan=False) + '\n')


if __name__ == '__main__':
    main()
