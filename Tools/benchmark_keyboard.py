#!/usr/bin/env python3
"""Measure whole-keyboard consistency, without opening any reference audio.

Protocol v1: a fresh keyra_render process per model/note/velocity, 48 kHz,
full quality, gain 0.07, one channel-1 note-on at 0.05 s, held for 1.6 s.
All exposed controls are fixed below; unexposed width/tuning use the engine's
defaults (0.75/440 Hz). --vary selects the normal shared velocity response
and strike variation. The fresh engine starts its touch RNG at 1, so every
case gets the same first strike draw. This is intentionally different from
benchmark_recordings.py's exact recorded-layer measurement mode. It does
not measure repeated strikes, releases, pedals, chords or long decays.

RMS/peak use both channels without level normalization. Windows relative to
note-on are early [0,0.1), middle [0.1,0.5), late [0.8,1.6) seconds.
Hann-windowed one-sided power spectra use each window's actual length (no
padding); frequency/f0 uses nominal equal-tempered A440, not estimated pitch.
Spectral energy fractions and centroid/f0 compare spectral balance, but low
notes have few cycles in the early window and upper bands can exceed Nyquist.
Side=(L-R)/2 and mid=(L+R)/2; side fraction is S/(S+M) in power. Stereo RMS
equals sqrt(M+S). Ratios and decibels with zero denominators are JSON null.

The rise diagnostic uses a causal 5 ms stereo RMS and its maximum in the
fixed first 150 ms. First crossings of 10% and 90% of that maximum define
the rise; the peak time and window-edge flag expose censoring. This is an
envelope diagnostic, not a hammer-contact estimate: cycles, interference,
and later maxima can move it. Silence is marked explicitly.

Adjacent differences and departure from the two-neighbour mean are signed
diagnostics. Largest absolute values are ranked, with no acoustic pass/fail
threshold and no assumption that a piano's natural irregularities are bad.
Coverage comes only from corpus/split metadata: measured_anchor means a train
pitch used by the fit, interpolated lies between the outer train anchors,
edge lies outside. An anchor label does not mean velocity 32/80/120 was
recorded. No sealed recordings or their feature caches are opened.

The output stage remains in the shipping signal path. Gain is 20 dB below
the renderer default. Each case is rendered again at half gain and checked
for floating-point proportionality, to catch output compression/limiting.
The first case is also repeated exactly to check deterministic rendering.
WAVs exist only in temporary directories. Numeric rows are checkpointed to
<out>.cases.jsonl, and --resume reuses them only for the identical protocol,
renderer, source declaration, and tool/corpus hashes.

Examples:
  python3 Tools/benchmark_keyboard.py --self-check
  python3 Tools/benchmark_keyboard.py --renderer out/realism/baseline/keyra_render \
      --source-revision ba3ee99 --out out/realism/keyboard/baseline.json --jobs 2
  python3 Tools/benchmark_keyboard.py --compare baseline.json candidate.json --out comparison.json
"""
from __future__ import annotations

import argparse
import concurrent.futures
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import tempfile
import time

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
import numpy as np
from scipy.io import wavfile

ROOT = Path(__file__).resolve().parents[1]
MODELS = ('grand', 'upright', 'kawai', 'hamburg', 'newyork', 'belmont')
WINDOWS = {'early': (0., .1), 'middle': (.1, .5), 'late': (.8, 1.6)}
PROTOCOL = {
    'version': 1, 'sample_rate': 48000, 'onset_seconds': .05,
    'held_seconds': 1.6, 'gain': .07, 'quality': 'full',
    'velocity_response': 'normal_playing_vary_fresh_engine_first_draw',
    'controls': {'brightness': .5, 'resonance': .25, 'mute': 0, 'sustain': 0,
                 'soft': 0, 'sostenuto': 0, 'mic': 0, 'mechanics': 1},
    'unexposed_engine_defaults': {'width': .75, 'tuning_hz': 440},
    'windows_seconds': WINDOWS, 'rise_rms_seconds': .005, 'rise_window_seconds': .15,
    'spectral_f0': 'nominal_A440_equal_temperament',
    'relative_band_edges': [0, .5, 2, 4, 8, 16, 'Nyquist'],
    'absolute_highpass_hz': [4000, 8000],
    'linearity_check': 'every_case_half_gain; 8 float32 eps relative max error',
    'interpretation': 'diagnostic_only_no_acoustic_pass_fail_thresholds',
}
RANK_METRICS = ['held_peak_dbfs', 'rise_ms'] + [
    f'{w}_{m}' for w in WINDOWS for m in
    ('rms_dbfs', 'centroid_f0', 'above_8f0_fraction', 'above_4000hz_fraction', 'side_fraction')]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def db(amplitude):
    return 20 * math.log10(amplitude) if amplitude > 0 else None


def ratio(numerator, denominator):
    return numerator / denominator if denominator > 0 else None


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


def spectrum_metrics(segment, rate, f0):
    n = len(segment)
    window = np.hanning(n)
    power = np.mean(abs(np.fft.rfft(segment * window[:, None], axis=0)) ** 2, axis=1)
    power[1:-1 if n % 2 == 0 else None] *= 2
    power /= n * np.sum(window * window)
    frequencies = np.fft.rfftfreq(n, 1 / rate)
    total = float(power.sum())
    centroid = ratio(float(power @ frequencies), total)
    result = {'centroid_hz': centroid, 'centroid_f0': centroid / f0 if centroid is not None else None}
    edges = [0, .5, 2, 4, 8, 16, float('inf')]
    for lo, hi in zip(edges, edges[1:]):
        name = f'band_{lo:g}_{hi:g}f0_fraction'
        result[name] = ratio(float(power[(frequencies >= lo * f0) & (frequencies < hi * f0)].sum()), total)
    for cutoff, name in ((8 * f0, '8f0'), (4000, '4000hz'), (8000, '8000hz')):
        result[f'above_{name}_fraction'] = ratio(float(power[frequencies >= cutoff].sum()), total)
    result['nyquist_f0'] = .5 * rate / f0
    return result


def window_metrics(segment, rate, f0):
    mid = .5 * (segment[:, 0] + segment[:, 1])
    side = .5 * (segment[:, 0] - segment[:, 1])
    mid_power, side_power = float(np.mean(mid ** 2)), float(np.mean(side ** 2))
    rms = math.sqrt(mid_power + side_power)
    sm_ratio = ratio(side_power, mid_power)
    result = {'rms': rms, 'rms_dbfs': db(rms), 'peak': float(np.max(abs(segment))),
              'side_fraction': ratio(side_power, mid_power + side_power),
              'side_mid_power_ratio': sm_ratio,
              'side_mid_db': 10 * math.log10(sm_ratio) if sm_ratio and sm_ratio > 0 else None}
    result.update(spectrum_metrics(segment, rate, f0))
    return result


def rise_metrics(audio, rate, onset):
    width = round(PROTOCOL['rise_rms_seconds'] * rate)
    start = round(onset * rate)
    stop = start + round(PROTOCOL['rise_window_seconds'] * rate)
    power = np.mean(audio ** 2, axis=1)
    cumulative = np.r_[0., np.cumsum(power)]
    ends = np.arange(start, stop) + 1
    smooth = (cumulative[ends] - cumulative[np.maximum(0, ends - width)]) / width
    maximum_index = int(np.argmax(smooth))
    maximum = float(smooth[maximum_index])
    if maximum <= 0:
        return {'rise_ms': None, 'rise_t10_ms': None, 'rise_t90_ms': None,
                'rise_peak_ms': None, 'rise_peak_at_window_end': False, 'rise_status': 'silent'}
    t10 = int(np.flatnonzero(smooth >= .01 * maximum)[0])
    t90 = int(np.flatnonzero(smooth >= .81 * maximum)[0])
    return {'rise_ms': 1000 * (t90 - t10) / rate, 'rise_t10_ms': 1000 * t10 / rate,
            'rise_t90_ms': 1000 * t90 / rate, 'rise_peak_ms': 1000 * maximum_index / rate,
            'rise_peak_at_window_end': maximum_index == len(smooth) - 1, 'rise_status': 'measured'}


def analyse(audio, rate, note):
    if audio.ndim != 2 or audio.shape[1] != 2 or not np.all(np.isfinite(audio)):
        raise ValueError('expected finite stereo audio')
    audio = audio.astype(np.float64)
    onset = PROTOCOL['onset_seconds']
    expected = round((onset + PROTOCOL['held_seconds']) * rate)
    if rate != PROTOCOL['sample_rate'] or len(audio) != expected:
        raise ValueError(f'unexpected audio shape/rate: {audio.shape}, {rate}')
    f0 = 440 * 2 ** ((note - 69) / 12)
    held = audio[round(onset * rate):]
    peak = float(np.max(abs(held)))
    metrics = {'held_peak': peak, 'held_peak_dbfs': db(peak), 'nominal_f0_hz': f0}
    metrics.update(rise_metrics(audio, rate, onset))
    for name, (lo, hi) in WINDOWS.items():
        segment = audio[round((onset + lo) * rate):round((onset + hi) * rate)]
        metrics.update({f'{name}_{key}': value for key, value in window_metrics(segment, rate, f0).items()})
    return metrics


def render(renderer, model, note, velocity, gain):
    with tempfile.TemporaryDirectory(prefix='keyra-keyboard-') as directory:
        directory = Path(directory)
        events, output = directory / 'note.events', directory / 'note.wav'
        events.write_text(f"{PROTOCOL['onset_seconds']} on {note} {velocity} 1\n")
        command = [str(renderer), '--events', str(events), '--output', str(output),
                   '--sample-rate', str(PROTOCOL['sample_rate']), '--duration', '1.65',
                   '--model', model, '--quality', PROTOCOL['quality'], '--gain', str(gain), '--vary']
        for name, value in PROTOCOL['controls'].items():
            command.extend([f'--{name}', str(value)])
        process = subprocess.run(command, check=True, capture_output=True, text=True)
        rate, audio = wavfile.read(output)
        return rate, audio, json.loads(process.stdout)


def run_case(job):
    renderer, model, note, velocity, coverage = job
    rate, audio, render_metrics = render(renderer, model, note, velocity, PROTOCOL['gain'])
    metrics = analyse(audio, rate, note)
    half_rate, half, _ = render(renderer, model, note, velocity, PROTOCOL['gain'] / 2)
    if half_rate != rate or half.shape != audio.shape:
        raise ValueError('gain-halving render changed audio shape/rate')
    error = float(np.max(abs(audio.astype(float) - 2 * half.astype(float))))
    scale = float(np.max(abs(audio)))
    relative = error / scale if scale else error
    # Eight float32 eps is a numerical identity allowance, not an acoustic
    # acceptance threshold. Output gain is linear before the guard/limiter.
    if relative > 8 * np.finfo(np.float32).eps:
        raise ValueError(f'{model}/{note}/{velocity}: output is not proportional at half gain ({relative:g})')
    return {'model': model, 'note': note, 'velocity': velocity, 'coverage': coverage,
            'metrics': metrics, 'audio_sha256': hashlib.sha256(audio.tobytes()).hexdigest(),
            'gain_halving_max_relative_error': relative,
            'renderer_wall_seconds': render_metrics['wall_seconds']}


def read_source(path, revision):
    if revision:
        return subprocess.check_output(['git', 'show', f'{revision}:{path}'], cwd=ROOT)
    return (ROOT / path).read_bytes()


def source_provenance(revision):
    resolved = subprocess.check_output(['git', 'rev-parse', revision or 'HEAD'], cwd=ROOT, text=True).strip()
    if revision:
        paths = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', resolved,
                                         '--', 'Source/DSP', 'Tools/render.cpp', 'CMakeLists.txt'], cwd=ROOT, text=True).splitlines()
    else:
        paths = sorted(str(p.relative_to(ROOT)) for p in (ROOT / 'Source/DSP').rglob('*') if p.is_file())
        paths += ['Tools/render.cpp', 'CMakeLists.txt']
    hashes = {path: hashlib.sha256(read_source(path, revision)).hexdigest() for path in paths}
    return {'mode': 'declared_revision' if revision else 'working_tree_snapshot',
            'git_head_or_declared_revision': resolved, 'files_sha256': hashes,
            'caveat': 'Source declaration is caller supplied; binary identity is independently hashed.'}


def coverage_metadata(models, notes):
    # Import only in the parent process; this helper reads JSON, never audio.
    import fit_realtime_modal as fit
    result, provenance = {}, {}
    for name in models:
        config = fit.MODELS[name]
        anchors = sorted(fit.train_anchors(config))
        corpus = json.loads(config['corpus'].read_text())
        roles = json.loads(config['split'].read_text())['cases']
        recorded = {}
        for item in corpus['files']:
            if item['kind'] == 'note':
                recorded.setdefault(item['midi'], set()).add(roles.get(item['id'], 'unassigned'))
        result[name] = {}
        for note in notes:
            lower = max((n for n in anchors if n <= note), default=None)
            upper = min((n for n in anchors if n >= note), default=None)
            role = 'measured_anchor' if note in anchors else 'interpolated' if lower is not None and upper is not None else 'edge'
            result[name][note] = {'role': role, 'lower_anchor': lower, 'upper_anchor': upper,
                                  'anchor_gap_semitones': upper - lower if upper is not None and lower is not None else None,
                                  'recorded_pitch_roles': sorted(recorded.get(note, [])),
                                  'excluded_anchor_reason': config['uncalibrated'].get(note)}
        provenance[name] = {'anchors': anchors, 'corpus': str(config['corpus'].relative_to(ROOT)),
                            'corpus_sha256': sha(config['corpus']), 'split': str(config['split'].relative_to(ROOT)),
                            'split_sha256': sha(config['split']),
                            'note_coverage': dict(Counter(row['role'] for row in result[name].values()))}
    return result, provenance


def diagnostic_rows(rows):
    indexed = {(r['model'], r['velocity'], r['note']): r for r in rows}
    adjacent, departures = [], []
    for (model, velocity, note), row in sorted(indexed.items()):
        after = indexed.get((model, velocity, note + 1))
        before = indexed.get((model, velocity, note - 1))
        if after:
            values = {m: after['metrics'][m] - row['metrics'][m] for m in RANK_METRICS
                      if row['metrics'][m] is not None and after['metrics'][m] is not None}
            adjacent.append({'model': model, 'velocity': velocity, 'from_note': note, 'to_note': note + 1,
                             'roles': [row['coverage']['role'], after['coverage']['role']], 'delta': values})
        if before and after:
            values = {m: row['metrics'][m] - .5 * (before['metrics'][m] + after['metrics'][m]) for m in RANK_METRICS
                      if all(r['metrics'][m] is not None for r in (before, row, after))}
            departures.append({'model': model, 'velocity': velocity, 'note': note,
                               'role': row['coverage']['role'], 'departure': values})
    return adjacent, departures


def rankings(rows, value_key):
    return {metric: sorted([
        {**{k: v for k, v in row.items() if k != value_key}, 'value': row[value_key][metric]}
        for row in rows if metric in row[value_key]], key=lambda r: abs(r['value']), reverse=True)[:12]
        for metric in RANK_METRICS}


def summaries(rows):
    result = {}
    for model in sorted({r['model'] for r in rows}):
        selected = [r for r in rows if r['model'] == model]
        result[model] = {'cases': len(selected),
                         'case_coverage': dict(Counter(r['coverage']['role'] for r in selected)),
                         'silent_rises': sum(r['metrics']['rise_status'] == 'silent' for r in selected),
                         'rise_peaks_at_window_end': sum(r['metrics']['rise_peak_at_window_end'] for r in selected),
                         'max_gain_halving_relative_error': max(r['gain_halving_max_relative_error'] for r in selected),
                         'metrics': {}}
        for metric in RANK_METRICS:
            values = [r['metrics'][metric] for r in selected if r['metrics'][metric] is not None]
            result[model]['metrics'][metric] = {'count': len(values), 'min': min(values) if values else None,
                                               'median': float(np.median(values)) if values else None,
                                               'max': max(values) if values else None}
    return result


def compare(baseline_path, candidate_path, output):
    baseline, candidate = [json.loads(Path(p).read_text()) for p in (baseline_path, candidate_path)]
    for field in ('protocol', 'coverage', 'grid'):
        if baseline[field] != candidate[field]:
            raise ValueError(f'cannot pair sweeps: {field} differs')
    if baseline['provenance']['tool_sha256'] != candidate['provenance']['tool_sha256']:
        raise ValueError('cannot pair sweeps produced by different analysis tool versions')
    key = lambda r: (r['model'], r['velocity'], r['note'])
    base = {key(r): r for r in baseline['cases']}
    current = {key(r): r for r in candidate['cases']}
    if set(base) != set(current) or len(base) != len(baseline['cases']) or len(current) != len(candidate['cases']):
        raise ValueError('case sets differ or contain duplicates')
    changes = []
    for case in sorted(base):
        a, b = base[case], current[case]
        changes.append({'model': case[0], 'velocity': case[1], 'note': case[2], 'role': a['coverage']['role'],
                        'audio_identical': a['audio_sha256'] == b['audio_sha256'],
                        'metric_availability_changes': [m for m in RANK_METRICS
                                                        if (a['metrics'][m] is None) != (b['metrics'][m] is None)],
                        'rise_status': [a['metrics']['rise_status'], b['metrics']['rise_status']],
                        'delta': {m: b['metrics'][m] - a['metrics'][m] for m in RANK_METRICS
                                  if a['metrics'][m] is not None and b['metrics'][m] is not None}})
    paired_diagnostics = {}
    for field, index_fields, value_key in (('adjacent', ('model', 'velocity', 'from_note'), 'delta'),
                                          ('departures', ('model', 'velocity', 'note'), 'departure')):
        bmap = {tuple(r[k] for k in index_fields): r for r in baseline[field]}
        paired = []
        for row in candidate[field]:
            old = bmap[tuple(row[k] for k in index_fields)]
            paired.append({**{k: row[k] for k in index_fields}, 'delta': {
                m: abs(row[value_key][m]) - abs(old[value_key][m])
                for m in RANK_METRICS if m in row[value_key] and m in old[value_key]}})
        paired_diagnostics[field] = {'absolute_magnitude_change': paired,
                                     'largest_absolute_magnitude_changes': rankings(paired, 'delta')}
    result = {'baseline': str(Path(baseline_path).resolve()), 'baseline_sha256': sha(baseline_path),
              'candidate': str(Path(candidate_path).resolve()), 'candidate_sha256': sha(candidate_path),
              'case_count': len(changes), 'identical_audio_cases': sum(r['audio_identical'] for r in changes),
              'cases_with_metric_availability_changes': sum(bool(r['metric_availability_changes']) for r in changes),
              'interpretation': 'Signed candidate-minus-baseline. Smaller adjacent/departure magnitude is not inherently better.',
              'case_changes': changes, 'largest_case_changes': rankings(changes, 'delta'),
              'diagnostic_changes': paired_diagnostics}
    write_json(output, result)
    print(json.dumps({'comparison': str(output), 'cases': len(changes), 'identical_audio_cases': result['identical_audio_cases']}))


def self_check():
    rate = PROTOCOL['sample_rate']
    n = round((PROTOCOL['held_seconds'] + PROTOCOL['onset_seconds']) * rate)
    audio = np.zeros((n, 2))
    start = round(PROTOCOL['onset_seconds'] * rate)
    t = np.arange(n - start) / rate
    audio[start:] = (.01 * np.sin(2 * np.pi * 440 * t))[:, None]
    measured = analyse(audio, rate, 69)
    doubled = analyse(audio * 2, rate, 69)
    def require(condition, reason):
        if not condition:
            raise AssertionError(reason)
    require(abs(measured['middle_rms'] - .01 / math.sqrt(2)) < 1e-12, 'sine RMS')
    require(abs(doubled['middle_rms_dbfs'] - measured['middle_rms_dbfs'] - 20 * math.log10(2)) < 1e-12, 'gain in dB')
    require(measured['middle_side_fraction'] == 0, 'mono side power')
    require(abs(measured['middle_centroid_f0'] - 1) < 1e-7, 'centroid normalization')
    require(abs(measured['middle_band_0.5_2f0_fraction'] - 1) < 1e-8, 'relative energy band')
    audio[:, 1] *= -1
    require(analyse(audio, rate, 69)['middle_side_fraction'] == 1, 'opposite channels side power')
    silence = analyse(np.zeros_like(audio), rate, 69)
    require(silence['rise_status'] == 'silent' and silence['early_rms_dbfs'] is None, 'silence without NaN')
    # Linear RMS envelope: verify the diagnostic, including its causal smoothing,
    # against a direct convolution independently of the cumulative-sum path.
    ramp = np.zeros_like(audio)
    ramp[start:, :] = np.minimum(t / .1, 1)[:, None]
    rise = rise_metrics(ramp, rate, PROTOCOL['onset_seconds'])
    direct = np.sqrt(np.convolve(np.mean(ramp ** 2, axis=1), np.ones(240) / 240, mode='full')[:n])[start:start + 7200]
    a = int(np.flatnonzero(direct >= .1 * direct.max())[0])
    b = int(np.flatnonzero(direct >= .9 * direct.max())[0])
    require(abs(rise['rise_ms'] - 1000 * (b - a) / rate) < 1e-12, 'rise diagnostic')
    rows = [{'model': 'grand', 'velocity': 80, 'note': note, 'coverage': {'role': 'interpolated'},
             'metrics': {m: float(note) for m in RANK_METRICS}} for note in (59, 60, 61)]
    adjacent, departures = diagnostic_rows(rows)
    require(all(v == 1 for row in adjacent for v in row['delta'].values()), 'adjacent differences')
    require(all(v == 0 for v in departures[0]['departure'].values()), 'linear-trend departures')
    print('self-check: RMS, gain, relative spectrum, stereo, silence, causal rise, adjacent differences passed')


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--renderer', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--models', nargs='+', choices=MODELS, default=list(MODELS))
    parser.add_argument('--notes', nargs='+', type=int, default=list(range(21, 109)))
    parser.add_argument('--velocities', nargs='+', type=int, default=[32, 80, 120])
    parser.add_argument('--jobs', type=int, default=2)
    parser.add_argument('--source-revision', help='Caller declaration of the source used to build this renderer; omitted means current files.')
    parser.add_argument('--resume', action='store_true')
    parser.add_argument('--compare', nargs=2, metavar=('BASELINE', 'CANDIDATE'))
    parser.add_argument('--self-check', action='store_true')
    args = parser.parse_args()
    if args.self_check:
        self_check()
        return
    if args.compare:
        if not args.out:
            parser.error('--compare requires --out')
        compare(*args.compare, args.out)
        return
    if not args.renderer or not args.out or args.jobs < 1:
        parser.error('--renderer, --out and positive --jobs are required')
    if any(n < 21 or n > 108 for n in args.notes) or any(v < 1 or v > 127 for v in args.velocities):
        parser.error('notes must be 21..108; velocities must be 1..127')
    models, notes, velocities = sorted(set(args.models)), sorted(set(args.notes)), sorted(set(args.velocities))
    renderer = args.renderer.resolve()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    coverage, coverage_provenance = coverage_metadata(models, notes)
    provenance = {'renderer': str(renderer), 'renderer_sha256': sha(renderer),
                  'tool_sha256': sha(__file__), 'coverage_helper_sha256': sha(ROOT / 'Tools/fit_realtime_modal.py'),
                  'source': source_provenance(args.source_revision)}
    declaration = {'protocol': PROTOCOL, 'provenance': provenance, 'coverage': coverage_provenance,
                   'grid': {'models': models, 'notes': notes, 'velocities': velocities}}
    journal = Path(str(args.out) + '.cases.jsonl')
    receipt = Path(str(args.out) + '.receipt.json')
    rows = []
    if args.resume and receipt.exists():
        if json.loads(receipt.read_text()) != json.loads(json.dumps(declaration)):
            raise ValueError('resume declaration differs from existing receipt')
        if journal.exists():
            rows = [json.loads(line) for line in journal.read_text().splitlines() if line]
    elif journal.exists() or receipt.exists() or args.out.exists():
        raise ValueError('output already exists; choose a new path or use --resume')
    else:
        write_json(receipt, declaration)
    keys = {(r['model'], r['note'], r['velocity']) for r in rows}
    if len(keys) != len(rows):
        raise ValueError('duplicate checkpoint cases')
    jobs = [(str(renderer), m, n, v, coverage[m][n]) for m in models for v in velocities for n in notes
            if (m, n, v) not in keys]
    expected = len(models) * len(notes) * len(velocities)
    started = time.monotonic()
    with journal.open('a') as stream, concurrent.futures.ProcessPoolExecutor(max_workers=args.jobs) as pool:
        futures = [pool.submit(run_case, job) for job in jobs]
        for future in concurrent.futures.as_completed(futures):
            row = future.result()
            rows.append(row)
            stream.write(json.dumps(row, separators=(',', ':'), allow_nan=False) + '\n')
            stream.flush()
            if len(rows) % 48 == 0 or len(rows) == expected:
                print(f'{len(rows)}/{expected} cases; {time.monotonic() - started:.1f}s this run', flush=True)
    rows.sort(key=lambda r: (r['model'], r['velocity'], r['note']))
    first = rows[0]
    _, repeat, _ = render(renderer, first['model'], first['note'], first['velocity'], PROTOCOL['gain'])
    repeat_hash = hashlib.sha256(repeat.tobytes()).hexdigest()
    if repeat_hash != first['audio_sha256']:
        raise ValueError('fresh engine render is not deterministic')
    if sha(renderer) != provenance['renderer_sha256'] or sha(__file__) != provenance['tool_sha256']:
        raise ValueError('renderer or analysis tool changed during sweep')
    adjacent, departures = diagnostic_rows(rows)
    report = {**declaration, 'created_utc': datetime.now(timezone.utc).isoformat(),
              'case_count': len(rows), 'complete': len(rows) == expected,
              'fresh_engine_repeat': {'model': first['model'], 'note': first['note'], 'velocity': first['velocity'],
                                      'audio_sha256': repeat_hash, 'identical': True},
              'summary': summaries(rows), 'cases': rows, 'adjacent': adjacent, 'departures': departures,
              'largest_adjacent_changes': rankings(adjacent, 'delta'),
              'largest_local_departures': rankings(departures, 'departure')}
    write_json(args.out, report)
    print(json.dumps({'report': str(args.out.resolve()), 'cases': len(rows),
                      'complete': report['complete'], 'seconds_this_run': round(time.monotonic() - started, 2)}))


if __name__ == '__main__':
    main()
