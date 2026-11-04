#!/usr/bin/env python3
"""Measure recorded pitches into what the keyboard network is fitted to.

The network that fits a piano's whole keyboard is trained on the misfit
today's fitter minimises at each recorded pitch: each partial's complex
envelope in each channel, weighed frame by frame as
piano_analysis.fit_partial_layers weighs it. This measures every recorded
pitch the way piano_analysis.analyse_anchor does up to that fit (onsets, the
partial series, envelopes, floors and contact delays, with the same code) and
keeps, for every layer and partial, the frames the fit weighs, the envelope
there and the weights, so that the fit's objective can be evaluated for any
lanes without the audio. Nothing is fitted here, and no audio is kept.

  python3 Tools/keyboard_measurements.py --piano kawai     # a Keyra piano's train pitches
  python3 Tools/keyboard_measurements.py --piano kawai --check   # re-evaluate today's fit on them
  python3 Tools/keyboard_measurements.py --library bitklavier   # a base library's notes (decode_base_library.py)

--check evaluates the shipping fit's lanes (the fitter's anchor caches) on the
stored measurements and compares each partial's relative error with the one
the fitter recorded: they agree when the stored frames and weights are the
fit's own.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import math
import os
import pickle
import sys
from pathlib import Path

# One BLAS thread per worker: the pool already fills every core.
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import numpy as np  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fit_realtime_modal as fit  # noqa: E402
import piano_analysis as pa  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'out/keyboard'
# fit_partial_layers' default `beat`: each frame is weighed by the envelope's
# largest value within this many seconds of it.
BEAT = .3


def cache_key(cases, options) -> str:
    h = hashlib.sha256(Path(pa.__file__).read_bytes())
    h.update(Path(__file__).read_bytes())
    for case, velocity, pin in cases:
        h.update(f'{case}:{velocity}:{pin}\n'.encode())
    for name, value in sorted(options.items()):
        h.update(f'{name}:{value}\n'.encode())
    return h.hexdigest()


def measure_anchor(paths, note, velocities, horizon_max=16.0, min_layers=3):
    """One recorded pitch's layers, measured as analyse_anchor measures them,
    and each partial's frames as fit_partial_layers weighs them."""
    layers = []
    for path, velocity in zip(paths, velocities):
        sr, x = pa.load(path)
        start = pa.onset(x, sr)
        f1, B, found = pa.partials(x, sr, note, start)
        duration = (len(x) - start) / sr
        horizon = min(horizon_max, duration - max(1.0, .25 * duration) if duration > 8 else duration - 1.0)
        seg = x[start + int(.05 * sr):start + int(.75 * sr)]
        layers.append({'path': str(path), 'x': x, 'sr': sr, 'start': start, 'f1': f1, 'B': B, 'found': found,
                       'velocity': velocity, 'horizon': horizon, 'duration': duration,
                       'end': pa.recorded_end(x, sr, start) - start,
                       'early_rms_db': float(10 * np.log10(np.mean(seg ** 2) + 1e-30))})
    sr = layers[0]['sr']
    by_order = {}
    for L in layers:
        for q in L['found']:
            by_order.setdefault(q['n'], []).append(q['hz'])
    orders = sorted(n for n, hz in by_order.items() if len(hz) >= min(min_layers, len(layers)))
    freqs = np.array([float(np.median(by_order[n])) for n in orders])
    f1 = float(np.median([L['f1'] for L in layers]))
    length = pa.window_length(f1, sr)
    hop = float(np.clip(length / sr / 8, .0005, .005))
    series = [[None] * len(layers) for _ in orders]
    out_layers = []
    for i, L in enumerate(layers):
        L['horizon'] = min(L['horizon'], L['end'] / sr - length / sr / 2)
        times = np.r_[np.arange(0, min(.5, L['horizon']), hop), np.arange(.5, L['horizon'], .02)]
        t, z = pa.envelopes(L['x'], sr, freqs, f1, L['start'], None, times=times)
        power_db = 10 * np.log10(np.maximum(np.mean(np.abs(z) ** 2, axis=1), 1e-30))
        floor = pa.envelope_floor(t, power_db)
        delay = pa.contact_delay(L['x'], sr, L['start'])
        t = t - delay
        for k in range(len(orders)):
            sel = pa._layer_frames(t, power_db[k], floor[k])
            if sel is None:
                continue
            tt = t[sel]
            amp = 10 ** (power_db[k][sel] / 20)
            local = np.array([amp[np.abs(tt - s) <= BEAT].max() for s in tt])
            w = 1 / (local + 10 ** (floor[k] / 20)) / math.sqrt(len(sel))
            series[k][i] = {'t': tt, 'z': z[k][:, sel].astype(np.complex64), 'w': w.astype(np.float32),
                            'floor_db': float(floor[k]), 'peak': float(amp.max())}
        out_layers.append({key: L[key] for key in ('path', 'start', 'f1', 'B', 'velocity', 'horizon', 'duration',
                                                   'end', 'early_rms_db')}
                          | {'delay': delay, 'channels': int(L['x'].shape[1])})
    return {'note': int(note), 'sr': sr, 'f1': f1, 'length': int(length), 'orders': orders, 'freqs': freqs,
            'layers': out_layers, 'series': series}


def measure_one(target, paths, note, velocities, cases, options):
    key = cache_key(cases, options)
    if target.exists():
        with target.open('rb') as f:
            if pickle.load(f).get('cache_key') == key:
                return note, 'cached'
    result = measure_anchor(paths, note, velocities, **options)
    result['cache_key'] = key
    result['cases'] = [case for case, _, _ in cases]
    target.parent.mkdir(parents=True, exist_ok=True)
    part = target.with_suffix('.part')
    with part.open('wb') as f:
        pickle.dump(result, f, protocol=pickle.HIGHEST_PROTOCOL)
    part.replace(target)
    return note, 'measured'


def piano_jobs(name):
    """A Keyra piano's train pitches with their train layers, as its fitter
    calibrates them (fit_realtime_modal.train_anchors)."""
    model = fit.MODELS[name]
    options = fit.analysis_options(model)
    for note, layers in fit.train_anchors(model).items():
        yield (OUT / name / f'{note}.pkl', [model['wav'] / f'{case}.wav' for case, _, _ in layers], note,
               [velocity for _, velocity, _ in layers], layers, options)


def library_jobs(name):
    """Every recorded pitch of a base library with its layers, decoded by
    decode_base_library.py. A second capture of a Keyra piano keeps out the
    pitches that piano's split holds back (dev or sealed), so that no held-out
    recording of the piano is learned through the other microphones."""
    corpus = json.loads((ROOT / f'Tools/corpus/{name}.json').read_text())
    wav = ROOT / f'out/base/{name}/wav'
    held = set()
    if 'capture_of' in corpus:
        model = fit.MODELS[corpus['capture_of']]
        files = {f['id']: f for f in json.loads(model['corpus'].read_text())['files']}
        held = {files[case]['midi'] for case, role in json.loads(model['split'].read_text())['cases'].items()
                if role != 'train' and files[case]['kind'] == 'note'}
    pitches = {}
    for item in corpus['files']:
        if item['kind'] == 'note' and item['midi'] not in held and (wav / f'{item["id"]}.wav').exists():
            # A layer's velocity is its range's midpoint where the library maps
            # one, else its place among the library's layers.
            velocity = fit.layer_velocity(item) if 'velocity' in item else round((item['layer'] - .5) * 127 / 16)
            pitches.setdefault(item['midi'], []).append((item['id'], velocity, item['sha256']))
    for note, layers in sorted(pitches.items()):
        layers.sort(key=lambda layer: layer[1])
        yield (OUT / name / f'{note}.pkl', [wav / f'{case}.wav' for case, _, _ in layers], note,
               [velocity for _, velocity, _ in layers], layers, {})


def run(jobs, workers):
    jobs = sorted(jobs, key=lambda j: j[2])  # the bass, with the most partials, first
    with concurrent.futures.ProcessPoolExecutor(workers) as pool:
        for future in concurrent.futures.as_completed([pool.submit(measure_one, *j) for j in jobs]):
            note, state = future.result()
            print(f'pitch {note}: {state}', flush=True)


def relative_errors(theta, amplitudes, layer_series, f1, sr, length, lanes=pa.LANES):
    """Each layer's relative misfit of one partial's lanes, as
    fit_partial_layers reports it: the weighted envelope's residual power
    over its power, the amplitude penalty left out."""
    grid, profile = pa.window_profile(f1, sr, min(.002, length / sr / 24), length)
    out = []
    for s_, a in zip(layer_series, amplitudes):
        if s_ is None or a is None:
            out.append(None)
            continue
        response = pa._WindowedExponentials(s_['t'].astype(float), grid, profile)
        s, rho = pa.lane_complex_rates(theta, s_['velocity'], lanes)
        Bm, _ = response(np.r_[s, s - rho])
        X = (Bm[:, :lanes] - Bm[:, lanes:]) * s_['w'][:, None]
        zw = (s_['z'] * s_['w']).T
        r = X @ a.T - zw
        out.append(float(np.vdot(r, r).real / max(np.vdot(zw, zw).real, 1e-30)))
    return out


def check(name):
    """Today's fit evaluated on the stored measurements, against the errors
    the fitter recorded for it."""
    model = fit.MODELS[name]
    worst, count = 0.0, 0
    for note, layers in fit.train_anchors(model).items():
        with (OUT / name / f'{note}.pkl').open('rb') as f:
            m = pickle.load(f)
        with (model['cache'] / f'{note}.pkl').open('rb') as f:
            c = pickle.load(f)
        if list(c['orders']) != list(m['orders']):
            raise SystemExit(f'{name} {note}: the partial orders differ from the fitter\'s')
        for k, fitted in enumerate(c['fits']):
            if fitted is None:
                continue
            per_layer = [None if s_ is None else s_ | {'velocity': L['velocity']}
                         for s_, L in zip(m['series'][k], m['layers'])]
            errors = relative_errors(fitted['theta'], fitted['amplitudes'], per_layer, m['f1'], m['sr'], m['length'])
            for mine, theirs in zip(errors, fitted['relative_error']):
                if (mine is None) != (theirs is None):
                    raise SystemExit(f'{name} {note} order {m["orders"][k]}: a layer is weighed in one only')
                if mine is not None:
                    worst = max(worst, abs(mine - theirs) / max(theirs, 1e-6))
                    count += 1
    print(f'{name}: {count} layer series; worst relative difference of the fit\'s error {worst:.2e}')
    return worst


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    which = parser.add_mutually_exclusive_group(required=True)
    which.add_argument('--piano', choices=sorted(fit.MODELS))
    which.add_argument('--library', help='a base library decoded by decode_base_library.py')
    parser.add_argument('--jobs', type=int, default=os.cpu_count() or 4)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if args.check:
        if not args.piano:
            raise SystemExit('--check compares a Keyra piano with its fitter\'s caches')
        raise SystemExit(0 if check(args.piano) < 1e-3 else 1)
    run(piano_jobs(args.piano) if args.piano else library_jobs(args.library), args.jobs)


if __name__ == '__main__':
    main()
