#!/usr/bin/env python3
"""Confidence audit for newly acquired TRAIN extremes, without forced pitch IDs.

The preserved estimator's narrow prior remains a candidate, not ground truth.
We inspect a wider nominal +/-200-cent region and harmonic-family support.
Strong out-of-prior components are reported separately: dominance alone does
not prove fundamental identity or justify retuning all modeled strings.
"""
from __future__ import annotations
import math

import numpy as np
from scipy import signal

EDGE_MIDIS = {21, 24, 96, 108}
WINDOWS = ((.005, .05), (.05, .25), (.25, .75), (.06, 2.6))


def _peaks(x, sr, lo, hi, benchmark):
    hi = min(hi, len(x) / sr)
    f, power = benchmark.spectrum(x[int(lo * sr):int(hi * sr)], sr)
    indices, _ = signal.find_peaks(power)
    peaks = []
    if len(f) < 3:
        return f, power, peaks, hi
    df = f[1] - f[0]
    for index in indices:
        if index == 0 or index >= len(power) - 1:
            continue
        a, b, c = np.log(np.maximum(power[index - 1:index + 2], 1e-40))
        offset = .5 * (a - c) / (a - 2 * b + c) if abs(a - 2 * b + c) > 1e-15 else 0.
        peaks.append({'hz': float(f[index] + np.clip(offset, -.5, .5) * df),
                      'power': float(power[index])})
    return f, power, peaks, hi


def fit_edge_pitch(x, sr, midi, benchmark):
    """Keep plausible key-family estimates, exposing out-of-prior ambiguity.

    A three-peak numerical fit is not called identifiable when its supporting
    peaks are below -35 dB of the strongest relevant recorded peak. No wider
    component automatically replaces f1: sparse extreme-register spectra and
    source-library tuning metadata can leave physical pitch identity ambiguous.
    """
    frozen = benchmark.fit_pitch(x, sr, midi)
    if midi not in EDGE_MIDIS:
        return frozen, None
    nominal = 440 * 2 ** ((midi - 69) / 12)
    broad_lo, broad_hi = nominal * 2 ** (-200 / 1200), nominal * 2 ** (200 / 1200)
    records, spectra = [], []
    for lo, hi in WINDOWS:
        f, power, peaks, stop = _peaks(x, sr, lo, hi, benchmark)
        near = sorted((p for p in peaks if broad_lo <= p['hz'] <= broad_hi),
                      key=lambda p: p['power'], reverse=True)
        relevant = [p for p in peaks if nominal * .8 <= p['hz'] < min(20000, sr * .44)]
        maximum = max((p['power'] for p in relevant), default=1e-30)
        records.append({'window_seconds': [lo, stop],
                        'fft_bin_width_hz': float(f[1] - f[0]) if len(f) > 1 else None,
                        'window_inverse_duration_hz': 1 / (stop - lo),
                        'nominal_search_half_width_cents': 200,
                        'strongest_near_nominal': [dict(p, relative_to_relevant_peak_db=float(
                            10 * np.log10(max(p['power'], 1e-30) / max(maximum, 1e-30)))) for p in near[:8]]})
        spectra.append((f, power, peaks))
    # The .25-.75s observation limits short-attack FFT bias. It does not prove
    # a stationary physical frequency; earlier/later windows remain visible.
    f, power, peaks = spectra[2]
    near = sorted((p for p in peaks if broad_lo <= p['hz'] <= broad_hi),
                  key=lambda p: p['power'], reverse=True)
    if not near:
        result = dict(frozen, pitch_identity_ambiguous=True, confidence='ambiguous')
        return result, {'midi': midi, 'nominal_hz': nominal, 'windows': records,
                        'decision': 'No reliable dominant component in the wide neighborhood; retain candidate with ambiguity.'}
    dominant = near[0]
    width = min(.25 * frozen['f1_hz'], max(4., .004 * frozen['f1_hz']))
    candidate_power = benchmark.integrated_power(f, power, frozen['f1_hz'] - width, frozen['f1_hz'] + width)
    dominant_power = benchmark.integrated_power(f, power, dominant['hz'] - width, dominant['hz'] + width)
    separation = 1200 * math.log2(dominant['hz'] / frozen['f1_hz'])
    ratio = 10 * math.log10(max(dominant_power, 1e-30) / max(candidate_power, 1e-30))

    long_f, long_power, long_peaks = spectra[3]
    relevant_maximum = max((p['power'] for p in long_peaks
                           if nominal * .8 <= p['hz'] < min(20000, sr * .44)), default=1e-30)
    df = long_f[1] - long_f[0] if len(long_f) > 1 else 1.
    support = []
    for n in range(1, min(11, int(19000 / frozen['f1_hz'])) + 1):
        target = float(benchmark.partial_frequencies(frozen['f1_hz'], frozen['B'], [n])[0])
        candidates = [p for p in long_peaks if abs(p['hz'] - target) <= max(2 * df, .007 * target)]
        if not candidates:
            continue
        selected = max(candidates, key=lambda p: p['power'])
        level = 10 * math.log10(max(selected['power'], 1e-30) / max(relevant_maximum, 1e-30))
        support.append({'n': n, 'predicted_hz': target, 'observed_hz': selected['hz'],
                        'relative_peak_db': level, 'strong_support': level >= -35})
    strong = [p for p in support if p['strong_support']]
    identifiable = bool(frozen['B_identifiable'] and len(strong) >= 3)
    ambiguous = bool(len(strong) < 3 and abs(separation) > 6 and ratio > 12)
    track = [r['strongest_near_nominal'][0]['hz'] for r in records if r['strongest_near_nominal']]
    spread = 1200 * math.log2(max(track) / min(track)) if track else None
    result = dict(frozen)
    if not identifiable:
        result.update(B=1e-4, B_identifiable=False, fit_partial_count=0,
                      measured_partial_peaks=[], rms_residual_cents=None)
    if ambiguous:
        result['confidence'] = 'ambiguous'
    result.update(pitch_identity_ambiguous=ambiguous,
                  pitch_measurement_basis=('Weak candidate key-family frequency; physical identity unresolved.' if ambiguous
                                           else 'Frozen key-family estimate checked against a wide component/family audit.'),
                  nominal_key_frequency_hz=nominal,
                  observed_dominant_component_hz=dominant['hz'],
                  dominant_component_window_seconds=[.25, min(.75, len(x) / sr)],
                  dominant_component_separation_from_f1_cents=separation,
                  dominant_component_window_frequency_spread_cents=spread,
                  dominant_to_candidate_band_power_db=ratio)
    diagnostic = {'midi': midi, 'nominal_key_frequency_hz': nominal,
                  'preserved_candidate_f1_hz': frozen['f1_hz'],
                  'previous_candidate_B': frozen['B'],
                  'previous_B_identifiable': frozen['B_identifiable'],
                  'observed_dominant_component_hz': dominant['hz'],
                  'dominant_separation_from_candidate_cents': separation,
                  'dominant_to_candidate_band_power_db': ratio,
                  'strong_family_support_threshold_db': -35,
                  'strong_candidate_family_peaks': len(strong),
                  'candidate_family_support': support,
                  'B_identifiable_after_audit': identifiable,
                  'pitch_identity_ambiguous': ambiguous, 'windows': records,
                  'dominant_component_window_frequency_spread_cents': spread,
                  'window_peak_variation_exceeds_5_cents': spread is not None and spread > 5,
                  'decision': ('Retain weak candidate f1 and report dominant separately; reject noise-derived B. Do not retune the entire key to the strongest component.'
                               if ambiguous else 'Candidate family/dominant agreement checked; retain candidate f1 and any adequately supported B.'),
                  'limits': 'The wide scan exposes missed components, not their physical origin. Window resolution/nonstationarity/unison or noise can shift peaks. No physical chirp, mislabeling, string identity or stretch cause is asserted.'}
    return result, diagnostic
