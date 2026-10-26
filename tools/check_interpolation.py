#!/usr/bin/env python3
"""Training-only cross-validation of fitted modal envelope interpolation.

This evaluates the envelope parameterization, not the full audio engine. Each
interior C anchor is excluded and predicted from its two neighboring training C
anchors at the same velocity. No held-out recording enters model selection.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
WINDOWS = ((.05, .25), (.25, .75), (.75, 1.5), (1.5, 3.5))
QUADRATURE_POINTS = 512
TIMES = np.array([np.linspace(lo, hi, QUADRATURE_POINTS, endpoint=False)
                  + (hi-lo)/(2*QUADRATURE_POINTS) for lo, hi in WINDOWS])
WEIGHTS = np.sin(np.pi*(np.arange(QUADRATURE_POINTS)+.5)/QUADRATURE_POINTS)**4
WEIGHTS /= WEIGHTS.sum()
EXPECTED = {f'C{octave}v{layer}' for octave in range(2, 7) for layer in (4, 12)}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def interpolate(a: np.ndarray, b: np.ndarray, fraction: float, policy: str) -> np.ndarray:
    # Modal columns: fast amplitude, late amplitude, fast loss, late loss.
    result = np.exp((1-fraction)*np.log(np.maximum(a, 1e-12))
                    + fraction*np.log(np.maximum(b, 1e-12)))
    if policy == 'linear_amplitude_log_loss':
        result[:, :2] = (1-fraction)*a[:, :2]+fraction*b[:, :2]
    elif policy != 'legacy_log_amplitude_log_loss':
        raise ValueError(f'Unknown policy: {policy}')
    return result


def envelope(modes: np.ndarray, times: np.ndarray = TIMES) -> np.ndarray:
    return (modes[:, 0, None, None]*np.exp(-modes[:, 2, None, None]*times)
            + modes[:, 1, None, None]*np.exp(-modes[:, 3, None, None]*times))


def powers(modes: np.ndarray) -> np.ndarray:
    value = envelope(modes)
    return (.5*np.sum(value*value*WEIGHTS, axis=-1)).T


def synthetic_branch_swap() -> dict:
    """Equivalent one-pole envelopes can have opposite inactive branch labels.

    At onset both endpoints have unit amplitude. A component-wise geometric
    average nearly removes both branches. The replacement must retain the
    onset mixture and endpoint limits. Later envelope identity is deliberately
    not claimed: arbitrary rates of inactive branches remain a limitation.
    """
    a = np.array([[0., 1., 3., 1.]])
    b = np.array([[1., 0., 1., .2]])
    old = interpolate(a, b, .5, 'legacy_log_amplitude_log_loss')
    new = interpolate(a, b, .5, 'linear_amplitude_log_loss')
    for fraction in np.linspace(0, 1, 101):
        mixed = interpolate(a, b, float(fraction), 'linear_amplitude_log_loss')
        if (not np.isfinite(mixed).all() or np.any(mixed < 0)
                or abs(float(mixed[:, :2].sum())-1.) > 1e-12):
            raise AssertionError('Interpolation loses onset energy under branch relabeling')
    for fraction, endpoint in ((0., a), (1., b)):
        mixed = interpolate(a, b, fraction, 'linear_amplitude_log_loss')
        if not np.allclose(mixed, endpoint, atol=1e-14, rtol=1e-14):
            raise AssertionError('Interpolation changed its endpoint')
    return {'passed': True,
            'legacy_midpoint_onset_amplitude': float(old[:, :2].sum()),
            'selected_midpoint_onset_amplitude': float(new[:, :2].sum()),
            'endpoint_onset_amplitudes': [1., 1.],
            'limits': 'Onset mixture is preserved. This two-branch policy is not invariant to arbitrary unused loss parameters at later times.'}


def evaluate_family(name: str, feature_path: Path, fit_path: Path, header_path: Path) -> dict:
    # Read the split tag only before selecting training rows. The grand source
    # also contains evaluation cases, which are never used below.
    selected = [s for s in json.loads(feature_path.read_text())['samples']
                if s['split'] == 'train']
    features = {s['id']: s for s in selected}
    fitted = json.loads(fit_path.read_text())
    if not EXPECTED.issubset(features) or not EXPECTED.issubset(fitted['fits']):
        raise ValueError(f'{name}: the original ten C-anchor training cases are required')
    if sha(header_path) != fitted['header_sha256']:
        raise ValueError(f'{name}: fitted report does not match the compiled calibration header')
    fits = {key: np.asarray(value['modes'], dtype=float)
            for key, value in fitted['fits'].items()}
    if any(value.shape != (64, 4) or not np.isfinite(value).all()
           or np.any(value[:, :2] < 0) or np.any(value[:, 2:] <= 0)
           for value in fits.values()):
        raise ValueError(f'{name}: invalid fitted modes')

    rows = []
    errors = {'legacy_log_amplitude_log_loss': [], 'linear_amplitude_log_loss': []}
    for octave in (3, 4, 5):
        for layer in (4, 12):
            omitted = f'C{octave}v{layer}'
            low, high = f'C{octave-1}v{layer}', f'C{octave+1}v{layer}'
            a, b = fits[low], fits[high]
            target = features[omitted]
            reference = np.asarray([p['powers'] for p in target['partials']]).T
            mask = reference > target['early_rms']**2*1e-5
            row = {'excluded_training_case': omitted, 'predictor_training_cases': [low, high],
                   'prominent_partial_windows': int(mask.sum()), 'policies': {}}
            for policy in errors:
                prediction = powers(interpolate(a, b, .5, policy))[:, :reference.shape[1]]
                # Exactly one scalar level match for the whole note, held fixed
                # through all later windows. No partial-specific normalization.
                ref_early = .2*np.sum(reference[0])+.5*np.sum(reference[1])
                mod_early = .2*np.sum(prediction[0])+.5*np.sum(prediction[1])
                gain = float(ref_early/max(mod_early, 1e-30))
                delta = abs(10*np.log10(np.maximum(reference, 1e-30)
                                       / np.maximum(prediction*gain, 1e-30)))
                values = delta[mask]
                errors[policy].extend(values.tolist())
                row['policies'][policy] = {'mean_error_db': float(np.mean(values)),
                                          'median_error_db': float(np.median(values)),
                                          'single_power_gain_db': float(10*np.log10(gain))}
            rows.append(row)

    # Diagnose real adjacent-anchor gaps as well as the wider leave-one-pitch-out
    # folds. The witness is only about a component-label artifact, not a musical
    # definition of which envelope is desirable between different notes.
    times = np.r_[0., np.geomspace(.001, 4., 128)][None, :]
    worst = {}
    for policy in errors:
        witness = None
        for octave in (2, 3, 4, 5):
            for layer in (4, 12):
                low, high = f'C{octave}v{layer}', f'C{octave+1}v{layer}'
                a, b = fits[low], fits[high]
                ea, eb = envelope(a, times), envelope(b, times)
                prominent = np.maximum(ea, eb) > max(float(ea.max()), float(eb.max()))*1e-3
                for step in range(1, 12):
                    mixed = envelope(interpolate(a, b, step/12, policy), times)
                    ratio = 20*np.log10(np.maximum(mixed, 1e-30)
                                       / np.maximum(np.minimum(ea, eb), 1e-30))
                    valid = np.where(prominent, ratio, np.inf)
                    index = np.unravel_index(np.argmin(valid), valid.shape)
                    value = float(valid[index])
                    if witness is None or value < witness['relative_to_smaller_endpoint_db']:
                        witness = {'training_endpoints': [low, high], 'semitones_above_low': step,
                                   'partial': int(index[0]+1), 'seconds': float(times[0, index[2]]),
                                   'relative_to_smaller_endpoint_db': value}
        worst[policy] = witness
    return {'feature_source': str(feature_path.relative_to(ROOT)),
            'feature_sha256': sha(feature_path), 'fit_source': str(fit_path.relative_to(ROOT)),
            'fit_sha256': sha(fit_path), 'calibration_header': str(header_path.relative_to(ROOT)),
            'calibration_header_sha256': sha(header_path), 'training_ids': sorted(EXPECTED),
            'all_fitted_training_ids': sorted(fitted['fits']),
            'scope': 'C-anchor interpolation diagnostic; additional fitted pitches are not used in these leave-one-C-anchor-out folds.',
            'folds': rows, 'pooled_error_db': {policy: float(np.mean(values)) for policy, values in errors.items()},
            'adjacent_anchor_worst_below_both_endpoints': worst}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'Validation/interpolation-cv.json')
    args = parser.parse_args()
    report = {'schema_version': 1, 'analysis': 'Training-only leave-one-pitch-out modal envelope comparison',
              'engine_source_sha256': sha(ROOT/'src/Piano.cpp'), 'analysis_source_sha256': sha(Path(__file__)),
              'selected_policy': 'linear_amplitude_log_loss',
              'fold_rule': 'Predict C3/C4/C5 from adjacent C training pitches at identical source layer; the omitted training fit is not used in prediction.',
              'gain_rule': 'One note-wide power gain from summed partial power in the first two windows, duration weighted; fixed through later windows.',
              'windows_seconds': WINDOWS, 'hann_squared_quadrature_points': QUADRATURE_POINTS,
              'prominent_mask': 'Reference partial power greater than 1e-5 of reference early RMS squared.',
              'synthetic_branch_relabeling': synthetic_branch_swap(),
              'limits': 'This compares coherent positive envelopes analytically, not rendered audio; it excludes authored beating, attack, microphones and nonlinear mechanics. Cross-validation reuses training cases and is not a fresh recording held-out result. Linear component amplitudes remove zero-component collapse but do not make arbitrary fitted branch parameters uniquely physical or fully representation invariant.',
              'families': {}}
    for name, feature, fit, header in (
            ('grand', 'Research/GrandPianoV2/benchmark/reference_features.json', 'Validation/live-calibration.json', 'src/LiveCalibration.h'),
            ('upright', 'References/Upright/train_features.json', 'Validation/upright-calibration.json', 'src/UprightCalibration.h')):
        report['families'][name] = evaluate_family(name, ROOT/feature, ROOT/fit, ROOT/header)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'synthetic_check': report['synthetic_branch_relabeling']['passed'],
                      'pooled_error_db': {name: family['pooled_error_db']
                                          for name, family in report['families'].items()}}, indent=2))


if __name__ == '__main__':
    main()
