#!/usr/bin/env python3
"""Private fixed-400Hz TRAIN34 confirmation: references first, candidates once.

No fitting, acquisition, canonical output, retiming or automatic promotion.
The six existing outcomes are copied exactly. New references/cached controls
are measured and frozen before the separately owned producer may start.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import io
import json
import math
import sys
import numpy as np
from scipy import ndimage
from scipy.io import wavfile

ROOT = Path('/workspace/virtual-instrument-keyra')
OUT = Path(__file__).resolve().parent
RATE = 48000
FRAMES = 182400
METRIC = ROOT/'tools/probe_full_causal_radiation_metrics.py'
METRIC_SHA = '14fc804b80f3742ee6c95cc3908c498459a77e61c90a1bdfe4b6c23c8580c1cd'
OPERATOR = ROOT/'out/full-radiation-crossover/v1/postprocess.py'
OPERATOR_SHA = '636dc354c5eb475757bbf8f0a1195d7b40782dd5a72969af0127beaccdb51a3e'
OLD_RESULT = ROOT/'out/full-radiation-crossover/v1/result.json'
OLD_RESULT_SHA = 'e807196b36d7f9cca224630cfc7b9de64bd06c2b5ec73e9f48ff7001ae2b32ec'
OLD_REFERENCE = ROOT/'out/full-causal-radiation-metrics/v1/reference-control.json'
OLD_REFERENCE_SHA = '4675d46574d65063d63ce9266ef4caa3d30c4880e4fac6fbabd11e6ff9747faf'
FEATURES = ROOT/'References/GrandFullRange/combined_train_features.json'
SPLIT = ROOT/'References/GrandFullRange/split.json'
CACHE = ROOT/'out/full-calibration/v3/control-renders'
OLD_IDS = ('C3v4', 'C3v12', 'C4v4', 'C4v12', 'C6v4', 'C6v12')
EARLY = ((0., .005), (.005, .020), (.020, .050), (.050, .100))
LATE = ((.25, .75), (.75, 1.5), (1.5, 2.5), (2.5, 3.5))
BANDS = ((31.25, 250.), (250., 1000.), (1000., 4000.), (4000., 12000.), (12000., 19000.))


def now(): return datetime.now(timezone.utc).isoformat()
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text())
def record(path): return {'path': str(Path(path).resolve()), 'sha256': sha(path)}


def write(path, value):
    path = Path(path).resolve()
    if OUT not in path.parents or path.exists():
        raise ValueError('Private write must be new and inside this experiment: '+str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def verify(records):
    for row in records:
        if sha(row['path']) != row['sha256']:
            raise ValueError('Frozen input changed: '+row['path'])


def module(path, name, expected):
    if sha(path) != expected: raise ValueError('Source SHA differs: '+str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def dependencies():
    metric = module(METRIC, 'train34_original_metric', METRIC_SHA)
    operator = module(OPERATOR, 'train34_fixed400_operator', OPERATOR_SHA)
    if sha(OLD_RESULT) != OLD_RESULT_SHA or sha(OLD_REFERENCE) != OLD_REFERENCE_SHA:
        raise ValueError('Existing six frozen results/reference changed')
    original_protocol, _ = metric.locked()
    rows, notes = metric.fit.training_inputs(FEATURES, SPLIT)
    if len(rows) != 34 or len(notes) != 17:
        raise ValueError('Expected exactly17 anchors x layers4/12')
    return metric, operator, original_protocol, rows


def read_float_snapshot(identity):
    data = Path(identity['path']).read_bytes()
    if hashlib.sha256(data).hexdigest() != identity['sha256']:
        raise ValueError('Audio SHA changed: '+identity['path'])
    sr, value = wavfile.read(io.BytesIO(data))
    if sr != RATE or value.dtype.kind != 'f' or value.dtype.itemsize != 4 or value.shape != (FRAMES, 2) or not np.isfinite(value).all():
        raise ValueError('Expected finite float32 stereo48k182400-frame source: '+identity['path'])
    return value


def support(reference, onset, ident):
    frames = len(reference)-onset
    late = [list(window) for window in LATE if round(window[1]*RATE) <= frames]
    omitted = [list(window) for window in LATE if list(window) not in late]
    if (ident == 'C8v4' and omitted != [[2.5, 3.5]]) or (ident != 'C8v4' and omitted):
        raise ValueError('Unexpected right censoring, stop before producer: '+ident)
    times = np.arange(.26, 3.5001, .02)
    # A240-sample centered smoother requires real samples on both sides.
    times = times[np.ceil(times*RATE).astype(int)+120 < frames]
    if not len(times): raise ValueError('No complete envelope support')
    whole_frames = min(round(3.5*RATE), frames)
    return {'reference_frames_after_onset': frames, 'late_windows_seconds': late,
            'omitted_incomplete_late_windows_seconds': omitted,
            'late_envelope_times_seconds': times.tolist(),
            'whole_note_stereo_frames': whole_frames,
            'right_censored': bool(omitted),
            'policy': 'Only complete requested spectral windows; no clipped substitute, padding, extrapolation or retiming. Envelope samples require full5ms smoothing support.'}


def reference_features(metric, full, onset, row, valid):
    value = np.asarray(full, dtype=np.float64)[onset:]
    section = metric.section
    sustain = metric.mean_square(section(value, .25, .75))
    early, harmonics = [], []
    for a, b in EARLY:
        chunk = section(value, a, b)
        powers = metric.band_powers(chunk, BANDS)
        extra = metric.band_powers(chunk, ((740., 810.), (4000., 8000.)))
        early.append({'window_seconds': [a, b], 'broad_power': metric.mean_square(chunk),
                      'band_power': powers, 'ring_740_810_power': extra[0], 'bright_4000_8000_power': extra[1]})
    for a, b in valid['late_windows_seconds']:
        f, power = metric.fit.benchmark.spectrum(section(value, a, b), RATE)
        partials = []
        for part in row['partials']:
            center = part['frequency_hz']
            if center >= 17000: continue
            width = min(.38*row['f1_hz'], max(3/(b-a), .004*center))
            energy = metric.fit.benchmark.integrated_power(f, power, center-width, center+width)
            partials.append({'n': part['n'], 'frequency_hz': center, 'power': energy, 'included': energy/sustain > 1e-5})
        harmonics.append({'window_seconds': [a, b], 'partials': partials})
    env = np.sqrt(np.maximum(ndimage.uniform_filter1d(np.mean(value*value, axis=1), 240, mode='nearest'), 0))
    times = np.asarray(valid['late_envelope_times_seconds'])
    samples = np.interp(times*RATE, np.arange(len(env)), env)
    mask = samples/math.sqrt(sustain) > 10**(-50/20)
    components = []
    for component in row.get('unassigned_components', []):
        center = component['frequency_hz']
        powers = []
        for a, b in valid['late_windows_seconds']:
            width = min(.38*row['f1_hz'], max(3/(b-a), .004*center))
            f, power = metric.fit.benchmark.spectrum(section(value, a, b), RATE)
            powers.append(metric.fit.benchmark.integrated_power(f, power, center-width, center+width))
        components.append({'frequency_hz': center, 'physical_identity': 'unassigned',
                           'window_seconds': valid['late_windows_seconds'], 'powers': powers,
                           'scope': 'Reference-fixed observed component, not H1 or identified piano part; diagnostic only, no added gate.'})
    return {'onset_frame': onset, 'onset_diagnostic': metric.onset_detail(full, None),
            'sustain_power': sustain, 'early': early, 'late_harmonics': harmonics,
            'late_envelope': {'times_seconds': times.tolist(), 'rms': samples.tolist(), 'included': mask.tolist()},
            'unassigned_components': components}


def observation_features(metric, full, onset, gain, reference, row, valid):
    # Same arithmetic as the original scorer, with explicit complete-window
    # support for the short C8v4 reference. The existing six never use this.
    value = np.asarray(full, dtype=np.float64)[onset:]*gain
    if len(value) < valid['whole_note_stereo_frames']:
        raise ValueError('Model lacks frozen reference support; no padding')
    ref_power = reference['sustain_power']; floor = ref_power*1e-10
    early, partials, partial_errors = [], [], []
    for index, (a, b) in enumerate(EARLY):
        chunk = metric.section(value, a, b); powers = metric.band_powers(chunk, BANDS)
        ref = reference['early'][index]
        errors = [metric.power_db(p, q, floor) for p, q in zip(powers, ref['band_power'])]
        f, power = metric.fit.benchmark.spectrum(chunk, RATE); mask = (f >= 250) & (f < 19000)
        centroid = float(f[mask]@power[mask]/max(float(np.sum(power[mask])), 1e-30))
        broad = metric.mean_square(chunk)
        extra = metric.band_powers(chunk, ((740., 810.), (4000., 8000.)))
        early.append({'window_seconds': [a, b], 'broad_power': broad, 'broad_signed_error_db': metric.power_db(broad, ref['broad_power'], floor),
                      'band_power': powers, 'band_signed_errors_db': errors, 'five_band_MAE_db': float(np.mean(np.abs(errors))),
                      'ring_740_810_power': extra[0], 'ring_signed_error_db': metric.power_db(extra[0], ref['ring_740_810_power'], floor),
                      'bright_4000_8000_power': extra[1], 'bright_signed_error_db': metric.power_db(extra[1], ref['bright_4000_8000_power'], floor),
                      'centroid_250_19000_hz': centroid})
    for index, (a, b) in enumerate(valid['late_windows_seconds']):
        f, power = metric.fit.benchmark.spectrum(metric.section(value, a, b), RATE); observed = []
        for center in reference['late_harmonics'][index]['partials']:
            width = min(.38*row['f1_hz'], max(3/(b-a), .004*center['frequency_hz']))
            energy = metric.fit.benchmark.integrated_power(f, power, center['frequency_hz']-width, center['frequency_hz']+width)
            error = metric.power_db(energy, center['power'], floor)
            observed.append({'n': center['n'], 'frequency_hz': center['frequency_hz'], 'power': energy,
                             'reference_power': center['power'], 'included': center['included'], 'signed_error_db': error})
            if center['included']: partial_errors.append(abs(error))
        partials.append({'window_seconds': [a, b], 'partials': observed})
    env = np.sqrt(np.maximum(ndimage.uniform_filter1d(np.mean(value*value, axis=1), 240, mode='nearest'), 0))
    times = np.asarray(reference['late_envelope']['times_seconds'])
    env_values = np.interp(times*RATE, np.arange(len(env)), env)
    ref_values = np.asarray(reference['late_envelope']['rms'])
    mask = np.asarray(reference['late_envelope']['included'], dtype=bool)
    amplitude_floor = math.sqrt(ref_power)*1e-5
    envelope_errors = 20*np.log10(np.maximum(env_values, amplitude_floor)/np.maximum(ref_values, amplitude_floor))
    if not partial_errors or not np.any(mask): raise ValueError('Missing fixed reference late support')
    stereo = {}
    windows = [('sustain', (.25, .75)), ('whole_note', (0., valid['whole_note_stereo_frames']/RATE)),
               *[(f'early_{i}', window) for i, window in enumerate(EARLY)]]
    for name, (a, b) in windows:
        chunk = metric.section(value, a, b)
        left = metric.mean_square(chunk[:, 0]); right = metric.mean_square(chunk[:, 1]); mono = metric.mean_square(np.mean(chunk, axis=1))
        stereo[name] = {'window_seconds': [a, b], 'left_power': left, 'right_power': right, 'mono_power': mono, 'LR_db': metric.power_db(left, right, floor)}
    components = []
    for component in reference.get('unassigned_components', []):
        center = component['frequency_hz']; entries = []
        for i, (a, b) in enumerate(valid['late_windows_seconds']):
            width = min(.38*row['f1_hz'], max(3/(b-a), .004*center))
            f, power = metric.fit.benchmark.spectrum(metric.section(value, a, b), RATE)
            energy = metric.fit.benchmark.integrated_power(f, power, center-width, center+width)
            entries.append({'window_seconds': [a, b], 'power': energy, 'reference_power': component['powers'][i],
                            'signed_error_db': metric.power_db(energy, component['powers'][i], floor)})
        components.append({'frequency_hz': center, 'physical_identity': 'unassigned', 'windows': entries, 'gate': False})
    return {'fixed_onset_frame': onset, 'fixed_gain': gain, 'detected_onset_diagnostic': metric.onset_detail(full),
            'early': early, 'late_harmonics': partials, 'late_harmonic_MAE_db': float(np.mean(partial_errors)),
            'late_envelope': {'times_seconds': times.tolist(), 'rms': env_values.tolist(), 'reference_rms': ref_values.tolist(),
                              'included': mask.tolist(), 'signed_errors_db': envelope_errors.tolist(), 'MAE_db': float(np.mean(abs(envelope_errors[mask])))},
            'sustain_RMS': math.sqrt(metric.mean_square(metric.section(value, .25, .75))), 'stereo': stereo,
            'unassigned_components': components,
            'weak_H1_bands': [{'window_seconds': p['window_seconds'], **part} for p in partials for part in p['partials'] if part['n'] == 1 and not part['included']]}


def references():
    metric, operator, original_protocol, rows = dependencies()
    if (OUT/'reference-opening-started.json').exists(): raise ValueError('Reference phase already started; no silent rerun')
    inputs = [record(p) for p in [__file__, METRIC, OPERATOR, OLD_RESULT, OLD_REFERENCE, FEATURES, SPLIT,
              ROOT/'tools/fit_full_calibration.py', ROOT/'Research/GrandPianoV2/tools/benchmark.py',
              ROOT/'References/GrandFullRange/manifest.json', ROOT/'Research/GrandPianoV2/reference/manifest.json',
              ROOT/'Research/GrandPianoV2/reference/fetch_reference.py', CACHE/'render-inputs.json', CACHE/'render-manifest.json']]
    write(OUT/'measurement-code-freeze.json', {'frozen_at_utc': now(), 'source': record(__file__), 'inputs': inputs,
          'candidate_audio_opened': False, 'scope': 'Reference/cached OLD controls only. No new producer start before final protocol freeze.'})
    write(OUT/'reference-opening-started.json', {'started_at_utc': now(), 'code_freeze': record(OUT/'measurement-code-freeze.json')})
    originals = {x['id']: x for x in read(OLD_REFERENCE)['cases']}; results = []; audio_inputs = []
    for row in rows:
        ident = row['id']; path = metric.fit.reference_audio(row, FEATURES)
        identity = metric.fit.reference_audio_identity(row, path)
        reference_audio = record(path); cached = record(CACHE/(ident+'.wav'))
        cache_metadata = [record(CACHE/(ident+suffix)) for suffix in ('.events', '.json')]
        audio_inputs += [reference_audio, cached, *cache_metadata]
        sr, full = metric.fit.benchmark.load_audio(path)
        if sr != RATE or not np.isfinite(full).all(): raise ValueError('Invalid reference')
        ro, _ = metric.fit.benchmark.onset_index(full, RATE)
        if ro != round(row['onset_seconds']*RATE): raise ValueError('Frozen TRAIN onset disagrees: '+ident)
        valid = support(full, ro, ident)
        if ident in OLD_IDS:
            old = originals[ident]
            if old['reference_audio'] != reference_audio or old['baseline_audio'] != cached: raise ValueError('Existing six input identity changed')
            result = dict(old)
            result.update(reference_identity=identity, support=valid, cached_control_metadata=cache_metadata, feature_measurement_reused_exactly=True)
        else:
            raw = read_float_snapshot(cached); base = raw.astype(np.float64)
            bo, _ = metric.fit.benchmark.onset_index(base, RATE)
            rf = reference_features(metric, full, ro, row, valid)
            gain = math.sqrt(rf['sustain_power']/metric.mean_square(metric.section(base[bo:], .25, .75)))
            baseline = observation_features(metric, base, bo, gain, rf, row, valid)
            result = {'id': ident, 'reference_audio': reference_audio, 'reference_identity': identity,
                      'baseline_audio': cached, 'cached_control_metadata': cache_metadata, 'support': valid,
                      'reference': rf, 'baseline': baseline, 'gain_db': 20*math.log10(gain), 'feature_measurement_reused_exactly': False}
        results.append(result)
        print(ident, 'reused' if ident in OLD_IDS else 'reference/control measured', flush=True)
    verify(inputs+audio_inputs); dependencies()
    write(OUT/'reference-control.json', {'completed_at_utc': now(), 'source': record(__file__), 'measurement_freeze': record(OUT/'measurement-code-freeze.json'),
          'inputs': inputs+audio_inputs, 'cases': results, 'candidate_audio_opened': False, 'fit_or_acquisition': False,
          'scope': 'All34 are already observed TRAIN. Fixed OLD gains/onsets precede new candidate outputs. Six existing reference/baseline features reused exactly.'})


def selftest():
    metric, operator, _, _ = dependencies()
    checks = operator.selftests()
    fake = np.zeros((round(2.8080833333333333*RATE)+132, 2))
    valid = support(fake, 132, 'C8v4')
    assert valid['late_windows_seconds'] == [[.25, .75], [.75, 1.5], [1.5, 2.5]]
    assert valid['omitted_incomplete_late_windows_seconds'] == [[2.5, 3.5]]
    assert abs(valid['late_envelope_times_seconds'][-1]-2.8) < 1e-12
    assert valid['whole_note_stereo_frames'] == len(fake)-132
    rng = np.random.default_rng(34400)
    synthetic = rng.normal(size=(round(3.8*RATE), 2))
    synthetic[:4800] = 0
    row = {'f1_hz': 130., 'partials': [{'n': n, 'frequency_hz': 130.*n} for n in range(1, 8)]}
    full_support = support(synthetic, 4800, 'synthetic')
    original_reference = metric.reference_features(synthetic, 4800, row)
    adapted_reference = reference_features(metric, synthetic, 4800, row, full_support)
    assert all(adapted_reference[k] == v for k, v in original_reference.items())
    original_observation = metric.observation_features(synthetic, 4800, .7, original_reference, row)
    adapted_observation = observation_features(metric, synthetic, 4800, .7, adapted_reference, row, full_support)
    assert all(adapted_observation[k] == v for k, v in original_observation.items())
    return {'passed': True, 'operator': checks, 'C8v4_complete_window_censoring': valid,
            'synthetic_full_support_original_reference_features_exact': True,
            'synthetic_full_support_original_observation_features_exact': True,
            'scope': 'Synthetic only; no reference or candidate PCM opened.'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--references', action='store_true')
    parser.add_argument('--selftest', action='store_true')
    args = parser.parse_args()
    if args.selftest: print(json.dumps(selftest(), indent=2))
    elif args.references: references()
    else: raise SystemExit('Choose --references or --selftest')


if __name__ == '__main__': main()
