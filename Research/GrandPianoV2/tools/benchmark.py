#!/usr/bin/env python3
"""Phase-insensitive, onset-aligned measurements of isolated acoustic piano notes.

The metrics measure recording agreement, not perceptual realism. One scalar
early-energy gain is removed per comparison; it is held fixed for every later
window. Stereo channels are combined in power, never as cancelling waveforms.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import tempfile

import numpy as np
from scipy import ndimage, optimize, signal, stats
from scipy.io import wavfile

ROOT = Path(__file__).resolve().parents[1]
WINDOWS = [(0.05, 0.25), (0.25, 0.75), (0.75, 1.5), (1.5, 3.5)]
BAND_EDGES = 31.25 * 2.0 ** (np.arange(20) / 2.0)
MIDI_VELOCITIES = {4: 40, 6: 49, 8: 61, 12: 93}
ANALYSIS = {
    "windows_seconds_after_onset": WINDOWS,
    "early_gain_window_seconds": [0.05, 0.75],
    "maximum_analysis_seconds": 4.0,
    "channel_combination": "mean stereo power; no mono waveform summation",
    "onset": "first 1ms RMS envelope crossing a noise-aware threshold near -45dB of the first-second peak",
    "pitch": "joint stiff-string fit to dominant partial peaks; normalized f1 convention",
    "partial_levels": "Hann-window power integrated around each fitted partial, with bandwidth covering window leakage and unison splitting",
    "decay": "Theil-Sen regression of partial-band dB power from 0.25 to 3.5 seconds; not a physical loss identification in isolation",
    "gain": "one scalar from 0.05–0.75s RMS, applied unchanged to all windows",
    "limits": "one piano/recording setup; microphone, room, library editing, unknown physical hammer velocities and acquisition pedal state are confounds; metrics are not perceptual scores",
}


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()


def identity(path):
    stem = Path(path).stem
    m = re.fullmatch(r'([A-G])([#b]?)(-?\d+)v(\d+)', stem)
    if not m: raise ValueError(f'Cannot infer note/layer from {stem}; use a reference-style filename')
    note, accidental, octave, layer = m.groups()
    semitone = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}[note]
    semitone += {'': 0, '#': 1, 'b': -1}[accidental]
    midi = 12*(int(octave)+1)+semitone
    return stem, midi, int(layer)


def split_for(stem):
    _, midi, layer = identity(stem)
    if midi in (24, 96): return 'edge_extrapolation'
    if '#' in stem: return 'heldout_pitch'
    if layer in (6, 8): return 'heldout_velocity'
    if layer in (4, 12): return 'train'
    return 'other'


def write_split(path=None):
    samples = []
    for octave in range(2, 7):
        samples += [f'C{octave}v{layer}' for layer in (4, 8, 12)]
    samples += [f'F#{octave}v8' for octave in range(2, 6)]
    samples += [f'C{octave}v6' for octave in range(3, 6)]
    samples += ['C1v8', 'C7v8']
    result = {'schema_version': 1, 'locked_before_fitting': True,
              'rule': 'Only C2–C6 at layers4/12 are fitting data. All layer8/layer6 cases, F# pitches and edge notes are excluded from parameter fitting.',
              'physical_velocity_caveat': 'MIDI velocities are SFZ-bin midpoints, not measured physical hammer speeds.',
              'samples': [{'id': s, 'midi': identity(s)[1], 'layer': identity(s)[2],
                           'midi_velocity': MIDI_VELOCITIES[identity(s)[2]], 'split': split_for(s)} for s in samples]}
    target = path or ROOT/'benchmark/split.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(result, indent=2)+'\n')
    return result


def load_audio(path):
    sr, x = wavfile.read(path)
    if x.dtype.kind in 'iu':
        if x.dtype.kind == 'u': x = (x.astype(np.float64)-128)/128
        else: x = x.astype(np.float64)/(2.0**(x.dtype.itemsize*8-1))
    else: x = x.astype(np.float64)
    if x.ndim == 1: x = x[:, None]
    if x.ndim != 2 or len(x) < 32 or not np.isfinite(x).all():
        raise ValueError(f'Invalid or nonfinite WAV: {path}')
    return int(sr), x


def onset_index(x, sr):
    power = np.mean(x*x, axis=1)
    env = ndimage.uniform_filter1d(power, max(3, int(.001*sr)), mode='constant')
    peak = float(np.max(env[:min(len(env), int(1.5*sr))]))
    if peak <= 1e-22: raise ValueError('No audible onset in the first 1.5 seconds')
    noise = float(np.median(env[:max(1, int(.008*sr))]))
    # If the edited file begins at the attack, its first samples cannot be used
    # as a noise estimate. Bound this nuisance threshold rather than shifting
    # onset far into a rising note.
    threshold = max(peak*10**(-45/10), min(noise*25, peak*1e-4))
    indices = np.flatnonzero(env > threshold)
    index = max(0, int(indices[0])-int(.0005*sr))
    return index, {'threshold_power': threshold, 'initial_noise_power': noise,
                   'first_peak_power': peak, 'threshold_relative_db': 10*math.log10(threshold/peak)}


def spectrum(x, sr):
    n = len(x)
    if n < 16: return np.array([0.]), np.array([0.])
    w = signal.windows.hann(n, sym=False)
    nfft = 1 << int(math.ceil(math.log2(n*2)))
    z = np.fft.rfft(x*w[:, None], n=nfft, axis=0)
    # Sum over these discrete one-sided powers approximately equals the
    # window-weighted mean-square amplitude, independent of zero-padding.
    p = np.mean(abs(z)**2, axis=1)*2/(nfft*np.sum(w*w))
    p[0] *= .5
    if nfft % 2 == 0: p[-1] *= .5
    return np.fft.rfftfreq(nfft, 1/sr), p


def partial_frequencies(f1, B, n):
    n = np.asarray(n, dtype=float)
    return f1*n*np.sqrt((1+B*n*n)/(1+B))


def fit_pitch(x, sr, midi):
    nominal = 440*2**((midi-69)/12)
    start, stop = int(.06*sr), min(len(x), int(2.6*sr))
    f, p = spectrum(x[start:stop], sr)
    df = f[1]-f[0]
    peaks, _ = signal.find_peaks(p, distance=max(1, int(.4/df)))
    peaks = peaks[(f[peaks] > nominal*.9) & (f[peaks] < min(15000, sr*.44))]
    frequency, amplitude = [], []
    for k in peaks:
        a, b, c = np.log(np.maximum(p[k-1:k+2], 1e-40))
        offset = .5*(a-c)/(a-2*b+c) if abs(a-2*b+c) > 1e-15 else 0.
        frequency.append(f[k]+float(np.clip(offset, -.5, .5))*df)
        amplitude.append(p[k])
    frequency, amplitude = np.asarray(frequency), np.asarray(amplitude)
    fundamental_candidates = np.flatnonzero(abs(np.log2(frequency/nominal)) < 60/1200)
    if not len(fundamental_candidates):
        return {'f1_hz': nominal, 'B': 1e-4, 'B_identifiable': False, 'confidence': 'fallback', 'rms_residual_cents': None,
                'measured_partial_peaks': [], 'fit_partial_count': 0}
    base = float(frequency[fundamental_candidates[np.argmax(amplitude[fundamental_candidates])]])
    ns = np.arange(1, min(11, int(14000/base))+1)
    if len(ns) < 3: ns = np.arange(1, max(3, int(18000/base))+1)

    def select(f1, B):
        predicted = partial_frequencies(f1, B, ns)
        selected, keep, strengths = [], [], []
        for n, target in zip(ns, predicted):
            candidates = np.flatnonzero(abs(frequency-target) < max(2.0, .007*target))
            if not len(candidates): continue
            # A weak noise peak does not beat an actual partial solely because
            # it is closer to the current prediction.
            score = np.log(np.maximum(amplitude[candidates], 1e-40))-0.5*((frequency[candidates]-target)/max(1.0, .0025*target))**2
            chosen = candidates[np.argmax(score)]
            selected.append(frequency[chosen]); keep.append(n); strengths.append(amplitude[chosen])
        return np.asarray(keep), np.asarray(selected), np.asarray(strengths)

    best = None
    for B in np.r_[0., np.geomspace(1e-7, .035, 130)]:
        n, observed, strength = select(base, B)
        if len(n) < 3: continue
        strongest = max(float(np.max(strength)), 1e-30)
        good = strength > strongest*1e-5
        n, observed, strength = n[good], observed[good], strength[good]
        if len(n) < 3: continue
        residual = 1200*np.log2(observed/partial_frequencies(base, B, n))
        objective = float(np.mean(np.minimum(abs(residual), 40)))+3*(len(ns)-len(n))
        if best is None or objective < best[0]: best = (objective, base, float(B), n, observed, strength)
    if best is None:
        return {'f1_hz': base, 'B': 1e-4, 'B_identifiable': False, 'confidence': 'fallback', 'rms_residual_cents': None,
                'measured_partial_peaks': [], 'fit_partial_count': 0}
    _, f1, B, n, observed, strength = best
    for _ in range(4):
        weights = np.clip((strength/max(strength))**.15, .2, 1)
        def residual(theta):
            return weights*1200*np.log2(partial_frequencies(theta[0], theta[1], n)/observed)
        fit = optimize.least_squares(residual, [f1, max(B, 1e-8)],
                bounds=([nominal*2**(-70/1200), 0], [nominal*2**(70/1200), .05]),
                loss='soft_l1', f_scale=1., x_scale=[nominal, .001], max_nfev=100)
        f1, B = map(float, fit.x)
        new_n, new_observed, new_strength = select(f1, B)
        if len(new_n) < 3: break
        good = new_strength > max(new_strength)*1e-5
        if good.sum() < 3: break
        n, observed, strength = new_n[good], new_observed[good], new_strength[good]
    errors = 1200*np.log2(observed/partial_frequencies(f1, B, n))
    rms = float(np.sqrt(np.mean(errors*errors)))
    return {'f1_hz': f1, 'B': B, 'B_identifiable': True, 'confidence': 'good' if rms < 4 and len(n) >= 4 else 'limited',
            'rms_residual_cents': rms, 'fit_partial_count': len(n),
            'measured_partial_peaks': [{'n': int(i), 'hz': float(hz), 'residual_cents': float(e),
                'relative_peak_db': float(10*np.log10(a/max(strength)))} for i, hz, e, a in zip(n, observed, errors, strength)]}


def integrated_power(f, p, lo, hi):
    if len(f) < 2: return 0.
    df = f[1]-f[0]
    # Fractional boundary bins prevent shifts relative to the FFT grid from
    # changing the measured power merely by including/excluding an entire bin.
    weights = np.clip((np.minimum(f+df/2, hi)-np.maximum(f-df/2, lo))/df, 0, 1)
    return float(np.dot(weights, p))


def decay_features(x, sr, frequencies, f1):
    seconds = min(.4, max(.16, 8/f1))
    nperseg = min(len(x), int(seconds*sr))
    hop = max(1, int(.04*sr))
    nfft = 1 << int(math.ceil(math.log2(nperseg*2)))
    powers = None
    for channel in range(x.shape[1]):
        f, t, z = signal.stft(x[:, channel], fs=sr, window='hann', nperseg=nperseg,
                              noverlap=nperseg-hop, nfft=nfft, boundary=None, padded=False)
        powers = abs(z)**2 if powers is None else powers+abs(z)**2
    powers /= x.shape[1]
    results = []
    for center in frequencies:
        width = min(.38*f1, max(3/seconds, .004*center))
        trace = np.sum(powers[(f > center-width) & (f < center+width)], axis=0)
        floor = max(float(np.max(trace))*1e-6, 1e-24)
        db = 10*np.log10(np.maximum(trace, floor))
        def fit_range(lo, hi):
            mask = (t >= lo) & (t <= hi) & (trace > floor*4)
            if mask.sum() < 5: return None
            slope, intercept, _, _ = stats.theilslopes(db[mask], t[mask])
            pred = intercept+slope*t[mask]
            residual = db[mask]-pred
            variance = float(np.sum((db[mask]-np.mean(db[mask]))**2))
            r2 = 1-float(np.sum(residual*residual))/max(variance, 1e-20)
            return {'slope_db_per_second': float(slope), 'amplitude_sigma_per_second': float(-slope/(20/math.log(10))),
                    'extrapolated_t60_seconds': float(-60/slope) if slope < -.01 else None,
                    'r_squared': r2, 'frames': int(mask.sum())}
        results.append({'overall': fit_range(.25, 3.5), 'early': fit_range(.2, 1.0), 'late': fit_range(1.0, 3.5)})
    return results


def extract_features(path, midi=None):
    path = Path(path)
    stem, inferred, layer = identity(path)
    midi = inferred if midi is None else midi
    sr, full = load_audio(path)
    onset, onset_detail = onset_index(full, sr)
    x = full[onset:min(len(full), onset+int(4*sr))]
    if len(x) < int(3.5*sr):
        raise ValueError(f'Need at least 3.5 seconds after onset for the fixed benchmark windows: {path}')
    pitch = fit_pitch(x, sr, midi)
    f1, B = pitch['f1_hz'], pitch['B']
    # With too few reliable peaks the placeholder B is not a measurement.
    # Restrict harmonic/decay analysis to the observed fundamental instead of
    # inventing higher partial locations from that fallback.
    count = max(3, min(48, int(16000/f1))) if pitch['B_identifiable'] else 1
    ns = np.arange(1, count+1)
    frequencies = partial_frequencies(f1, B, ns)
    keep = frequencies < min(17000, sr*.44)
    ns, frequencies = ns[keep], frequencies[keep]
    early = x[int(.05*sr):int(.75*sr)]
    early_power = max(float(np.mean(early*early)), 1e-24)
    partial_power, band_power, rms_windows = [], [], []
    for lo, hi in WINDOWS:
        section = x[int(lo*sr):int(hi*sr)]
        f, p = spectrum(section, sr)
        partial_power.append([integrated_power(f, p, center-min(.38*f1, max(3/(hi-lo), .004*center)),
                     center+min(.38*f1, max(3/(hi-lo), .004*center))) for center in frequencies])
        band_power.append([integrated_power(f, p, a, b) for a, b in zip(BAND_EDGES[:-1], BAND_EDGES[1:])])
        rms_windows.append(float(np.sqrt(np.mean(section*section))))
    partial_power = np.asarray(partial_power)
    decays = decay_features(x, sr, frequencies, f1)
    envelope_power = ndimage.uniform_filter1d(np.mean(x*x, axis=1), max(3, int(.005*sr)), mode='nearest')
    envelope = np.sqrt(np.maximum(envelope_power, 0))
    attack_limit = min(len(envelope), int(.15*sr))
    peak = float(np.max(envelope[:attack_limit]))
    crossings = {}
    for fraction in (.1, .5, .9):
        at = np.flatnonzero(envelope[:attack_limit] >= fraction*peak)
        crossings[f't{int(fraction*100)}_seconds'] = float(at[0]/sr) if len(at) else None
    times = np.arange(.02, 3.501, .02)
    envelope_samples = np.interp(times*sr, np.arange(len(envelope)), envelope)
    return {'id': stem, 'path': str(path.resolve()), 'sha256': sha256(path), 'midi': int(midi),
            'layer': layer, 'midi_velocity': MIDI_VELOCITIES.get(layer), 'split': split_for(stem),
            'sample_rate': sr, 'duration_seconds': len(full)/sr, 'channels': full.shape[1],
            'onset_seconds': onset/sr, 'onset_details': onset_detail,
            **pitch, 'early_rms': float(np.sqrt(early_power)), 'window_rms': rms_windows,
            'attack': dict(crossings, rise10_90_seconds=crossings['t90_seconds']-crossings['t10_seconds'],
                           definition='5ms RMS envelope rise within first150ms; not hammer contact duration'),
            'band_edges_hz': BAND_EDGES.tolist(), 'band_power': band_power,
            'envelope_times_seconds': times.tolist(), 'envelope_rms': envelope_samples.tolist(),
            'partials': [{'n': int(n), 'frequency_hz': float(hz),
                         'powers': partial_power[:, j].tolist(),
                         'relative_db': (10*np.log10(np.maximum(partial_power[:, j], 1e-30)/early_power)).tolist(),
                         'decay': decays[j]} for j, (n, hz) in enumerate(zip(ns, frequencies))]}


def compare_features(reference, model):
    gain = reference['early_rms']/max(model['early_rms'], 1e-20)
    early_power = reference['early_rms']**2
    ref_band = np.asarray(reference['band_power'])/early_power
    mod_band = np.asarray(model['band_power'])*gain*gain/early_power
    ref_db = 10*np.log10(np.maximum(ref_band, 1e-7))
    mod_db = 10*np.log10(np.maximum(mod_band, 1e-7))
    # Fixed reference-derived mask; weak recorded noise is not treated as an
    # exact target. Missing prominent reference energy remains penalized.
    mask = ref_db > -50
    band_error = abs(ref_db-mod_db)
    partial_errors, tuning_errors, decay_errors = [], [], []
    model_partial = {p['n']: p for p in model['partials']}
    for rp in reference['partials']:
        mp = model_partial.get(rp['n'])
        if not mp: continue
        rr = np.asarray(rp['powers'])/early_power
        mm = np.asarray(mp['powers'])*gain*gain/early_power
        valid = rr > 1e-5
        if np.any(valid):
            partial_errors.extend(abs(10*np.log10(np.maximum(rr[valid], 1e-7))-10*np.log10(np.maximum(mm[valid], 1e-7))).tolist())
            if rp['n'] <= 10: tuning_errors.append(abs(1200*math.log2(mp['frequency_hz']/rp['frequency_hz'])))
        rdec, mdec = rp['decay']['overall'], mp['decay']['overall']
        if rdec and mdec and rdec['r_squared'] > .25 and rp['relative_db'][1] > -45:
            decay_errors.append(abs(rdec['slope_db_per_second']-mdec['slope_db_per_second']))
    er = np.asarray(reference['envelope_rms'])/reference['early_rms']
    em = np.asarray(model['envelope_rms'])/model['early_rms']
    mask_env = er > 10**(-50/20)
    envelope_error = abs(20*np.log10(np.maximum(er, 1e-4))-20*np.log10(np.maximum(em, 1e-4)))
    per_window = [float(np.mean(row[m])) if np.any(m) else None for row, m in zip(band_error, mask)]
    return {'id': reference['id'], 'split': reference['split'], 'midi': reference['midi'],
            'layer': reference['layer'], 'early_gain_db': 20*math.log10(gain),
            'f1_error_cents': float(1200*math.log2(model['f1_hz']/reference['f1_hz'])),
            'absolute_f1_error_cents': float(abs(1200*math.log2(model['f1_hz']/reference['f1_hz']))),
            'reference_f1_hz': reference['f1_hz'], 'model_f1_hz': model['f1_hz'],
            'reference_B': reference['B'] if reference.get('B_identifiable', True) else None,
            'model_B': model['B'] if model.get('B_identifiable', True) else None,
            'pitch_fit_confidence': {'reference': reference['confidence'], 'model': model['confidence']},
            'log_band_mae_db': float(np.mean(band_error[mask])) if np.any(mask) else None,
            'log_band_mae_by_window_db': per_window,
            'harmonic_level_mae_db': float(np.mean(partial_errors)) if partial_errors else None,
            'partial_tuning_mae_cents': float(np.mean(tuning_errors)) if tuning_errors else None,
            'partial_decay_slope_mae_db_per_second': float(np.mean(decay_errors)) if decay_errors else None,
            'partial_decay_pairs': len(decay_errors),
            'envelope_mae_db': float(np.mean(envelope_error[mask_env])),
            'attack_rise10_90_error_ms': 1000*abs(reference['attack']['rise10_90_seconds']-model['attack']['rise10_90_seconds']),
            'reference_sha256': reference['sha256'], 'model_sha256': model['sha256']}


def aggregate(rows):
    keys = ['log_band_mae_db', 'harmonic_level_mae_db', 'envelope_mae_db',
            'partial_decay_slope_mae_db_per_second', 'absolute_f1_error_cents',
            'partial_tuning_mae_cents', 'attack_rise10_90_error_ms']
    report = {}
    for split in ['train', 'heldout_velocity', 'heldout_pitch', 'edge_extrapolation', 'all_non_edge']:
        selected = [r for r in rows if r['split'] == split or (split == 'all_non_edge' and r['split'] != 'edge_extrapolation')]
        report[split] = {'cases': len(selected)}
        for key in keys:
            values = [r[key] for r in selected if r.get(key) is not None and np.isfinite(r[key])]
            report[split][key] = {'mean': float(np.mean(values)), 'median': float(np.median(values)), 'valid_cases': len(values)} if values else None
    return report


def measurement_self_test():
    """Known modal signal checks extraction, stereo power and gain invariance."""
    sr = 48000
    t = np.arange(int(4.3*sr))/sr-.06
    positive = np.maximum(t, 0)
    f1, B = 261.6255653, .0003
    y = np.zeros(len(t))
    for n in range(1, 13):
        hz = float(partial_frequencies(f1, B, n))
        y += .07/n*np.exp(-(.3+.04*n)*positive)*np.sin(2*np.pi*hz*positive+.17*n)
    y *= (t >= 0)*(1-np.exp(-positive/.002))
    # Opposite channels would vanish under a mono-sum implementation.
    stereo = np.stack([y, -y], axis=1)
    with tempfile.TemporaryDirectory(prefix='piano-benchmark-test-') as temp:
        original = Path(temp)/'original'; original.mkdir()
        scaled = Path(temp)/'scaled'; scaled.mkdir()
        wavfile.write(original/'C4v8.wav', sr, stereo.astype(np.float32))
        wavfile.write(scaled/'C4v8.wav', sr, (stereo*.125).astype(np.float32))
        ref = extract_features(original/'C4v8.wav')
        other = extract_features(scaled/'C4v8.wav')
        pair = compare_features(ref, other)
    cents = abs(1200*math.log2(ref['f1_hz']/f1))
    b_error = abs(ref['B']/B-1)
    measured_slope = ref['partials'][0]['decay']['overall']['slope_db_per_second']
    expected_slope = -20/math.log(10)*.34
    result = {'passed': cents < .3 and b_error < .01 and ref['early_rms'] > .01
                       and abs(measured_slope-expected_slope) < .12
                       and pair['log_band_mae_db'] < .001 and pair['envelope_mae_db'] < .001,
              'known_f1_error_cents': cents, 'known_B_relative_error': b_error,
              'known_fundamental_decay_error_db_per_second': abs(measured_slope-expected_slope),
              'opposite_polarity_stereo_early_rms': ref['early_rms'],
              'gain_invariance_log_band_mae_db': pair['log_band_mae_db'],
              'gain_invariance_envelope_mae_db': pair['envelope_mae_db'],
              'expected_gain_db': -20*math.log10(.125), 'recovered_gain_db': pair['early_gain_db']}
    if not result['passed']: raise AssertionError(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('self-test')
    extract = sub.add_parser('extract')
    extract.add_argument('--input-dir', type=Path, default=ROOT/'reference/wav')
    extract.add_argument('--output', type=Path, default=ROOT/'benchmark/reference_features.json')
    compare = sub.add_parser('compare')
    compare.add_argument('--reference', type=Path, default=ROOT/'benchmark/reference_features.json')
    compare.add_argument('--model-dir', type=Path, required=True)
    compare.add_argument('--output', type=Path, required=True)
    compare.add_argument('--feature-output', type=Path)
    compare.add_argument('--allow-missing', action='store_true')
    args = parser.parse_args()
    if args.command == 'self-test':
        print(json.dumps(measurement_self_test(), indent=2)); return
    write_split()
    if args.command == 'extract':
        samples = []
        for path in sorted(args.input_dir.glob('*.wav')):
            feature = extract_features(path)
            samples.append(feature)
            print(f"{feature['id']}: f1={feature['f1_hz']:.3f}Hz B={feature['B']:.6g} ({feature['confidence']})", flush=True)
        report = {'schema_version': 1, 'analysis': ANALYSIS, 'samples': samples}
    else:
        references = json.loads(args.reference.read_text())['samples']
        models, rows, missing = [], [], []
        for reference in references:
            path = args.model_dir/(reference['id']+'.wav')
            if not path.exists():
                if args.allow_missing: missing.append(reference['id']); continue
                raise FileNotFoundError(path)
            model = extract_features(path, reference['midi'])
            models.append(model)
            comparison = compare_features(reference, model)
            rows.append(comparison)
            print(f"{model['id']}: bands={comparison['log_band_mae_db']:.2f}dB envelope={comparison['envelope_mae_db']:.2f}dB", flush=True)
        report = {'schema_version': 1, 'analysis': ANALYSIS, 'reference_features_sha256': sha256(args.reference),
                  'model_dir': str(args.model_dir.resolve()), 'cases': rows, 'summary': aggregate(rows), 'missing': missing}
        feature_output = args.feature_output or args.output.with_name(args.output.stem+'_features.json')
        feature_output.parent.mkdir(parents=True, exist_ok=True)
        feature_output.write_text(json.dumps({'schema_version': 1, 'analysis': ANALYSIS, 'samples': models}, indent=2)+'\n')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')


if __name__ == '__main__': main()
