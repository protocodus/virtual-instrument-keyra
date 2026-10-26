#!/usr/bin/env python3
"""Fit a smooth, positive two-polarization radiation observation from TRAIN10.

This identifies effective observation weights, not unique soundboard physics.
No held-out waveform or measurement is used. Mechanical states are untouched.
"""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy import ndimage, optimize, signal

from benchmark import WINDOWS, load_audio, sha256

ROOT = Path(__file__).resolve().parents[1]
NOTES = [36, 48, 60, 72, 84]
PARTIALS = 64
GAIN_LIMITS = (.025, 40.)


def _load(value, member=None):
    if isinstance(value, (str, Path)):
        value = json.loads(Path(value).read_text())
    if member and isinstance(value, dict): return value[member]
    return value


def _basis_index(rows):
    result = {}
    for row in rows:
        pol = row.get('polarization', row.get('pol', 0))
        if isinstance(pol, str): pol = 1 if pol in ('secondary', 'horizontal', '1') else 0
        result[int(row['midi']), int(row['n']), int(pol)] = row
    return result


def _basis_value(basis, note, n, pol):
    row = basis.get((note, n, pol)) or basis.get((note, n, 0))
    return float(row['H_magnitude']) if row else None


def _gram_windows(stems_dir, item):
    arrays = []
    paths = []
    sr = None
    for component in ('primary', 'secondary', 'transient'):
        path = Path(stems_dir)/(item['id']+'-'+component+'.wav')
        rate, x = load_audio(path)
        if sr is not None and (rate != sr or x.shape != arrays[0].shape):
            raise ValueError(f'Stem shape/rate mismatch for {item["id"]}')
        sr = rate
        arrays.append(x)
        paths.append({'component': component, 'path': str(path.resolve()), 'sha256': sha256(path)})
    onset = int(round(item['onset_seconds']*sr))
    x = np.stack(arrays, axis=-1)[onset:onset+int(4*sr)]
    if len(x) < 3.5*sr: raise ValueError('Stem shorter than fixed analysis windows')
    # The main render accompanies its stems; do not follow a historical
    # absolute path from an imported measurement file.
    model_wave = Path(stems_dir)/(item['id']+'.wav')
    reconstruction = None
    if model_wave.exists():
        full_sr, total = load_audio(model_wave)
        if full_sr == sr and total.shape == arrays[0].shape:
            reconstructed = sum(arrays)
            reconstruction = float(np.sqrt(np.mean((reconstructed-total)**2))/max(np.sqrt(np.mean(total*total)), 1e-20))
            if reconstruction > .005:
                raise ValueError(f'Stems do not reconstruct measured model for {item["id"]}: {reconstruction:.6g}')
    grams = {int(p['n']): [] for p in item['partials']}
    for lo, hi in WINDOWS:
        section = x[int(lo*sr):int(hi*sr)]
        count = len(section)
        window = signal.windows.hann(count, sym=False)
        nfft = 1 << int(math.ceil(math.log2(count*2)))
        z = np.fft.rfft(section*window[:, None, None], n=nfft, axis=0)
        matrix = np.einsum('fci,fcj->fij', z, z.conjugate()).real/x.shape[1]
        matrix *= 2/(nfft*np.sum(window*window))
        matrix[0] *= .5
        matrix[-1] *= .5
        f = np.fft.rfftfreq(nfft, 1/sr)
        df = f[1]-f[0]
        for partial in item['partials']:
            center = partial['frequency_hz']
            width = min(.38*item['f1_hz'], max(3/(hi-lo), .004*center))
            weights = np.clip((np.minimum(f+df/2, center+width)-np.maximum(f-df/2, center-width))/df, 0, 1)
            valid = weights > 0
            gram = np.einsum('f,fij->ij', weights[valid], matrix[valid])
            grams[int(partial['n'])].append(gram)
    return {n: np.asarray(g) for n, g in grams.items()}, {
        'id': item['id'], 'files': paths, 'sum_reconstruction_relative_rms_error': reconstruction}


def _row(log_frequency, grid, note_index):
    p = float(np.clip(log_frequency, grid[0], grid[-1]))
    left = min(len(grid)-2, max(0, int(np.searchsorted(grid, p)-1)))
    fraction = (p-grid[left])/(grid[left+1]-grid[left])
    row = np.zeros(len(NOTES)*len(grid))
    row[note_index*len(grid)+left] = 1-fraction
    row[note_index*len(grid)+left+1] = fraction
    return row


def _smooth_targets(observations, basis, grid, component):
    width = len(grid)
    size = len(NOTES)*width
    prior = np.zeros((len(NOTES), width))
    for k, note in enumerate(NOTES):
        rows = sorted((v for key, v in basis.items() if key[0] == note and key[2] == component), key=lambda z: z['frequency_hz'])
        if not rows:
            rows = sorted((v for key, v in basis.items() if key[0] == note and key[2] == 0), key=lambda z: z['frequency_hz'])
        frequencies = np.log2([r['frequency_hz'] for r in rows])
        levels = 20*np.log10(np.maximum([r['H_magnitude'] for r in rows], 1e-8))
        prior[k] = ndimage.gaussian_filter1d(np.interp(grid, frequencies, levels), 1.15, mode='nearest')
    if component:
        # Ambiguous weak secondary modes borrow one common polarization offset
        # from the identifiable TRAIN10 modes, not an independently chosen gain.
        identified = [o for o in observations if o['weights'][1] > .12]
        offset = float(np.median([o['gains_db'][1] for o in identified])) if identified else 0.
        offset = float(np.clip(offset, 0, 26))
        prior += offset
    else: offset = 0.
    A, y = [], []
    for o in observations:
        weight = o['weights'][component]
        if weight <= 0: continue
        A.append(_row(math.log2(o['frequency_hz']), grid, NOTES.index(o['midi']))*math.sqrt(weight))
        y.append(o['target_db'][component]*math.sqrt(weight))
    # Weak absolute prior closes unobserved high modes. Second differences in
    # log frequency remove narrow compensation spikes, and adjacent registers
    # share a slowly varying observation curve at a common absolute frequency.
    for i in range(size):
        row = np.zeros(size); row[i] = math.sqrt(.025)
        A.append(row); y.append(prior.reshape(-1)[i]*math.sqrt(.025))
    for key in range(len(NOTES)):
        for f in range(1, width-1):
            row = np.zeros(size)
            row[key*width+f-1:key*width+f+2] = np.array([1, -2, 1])*math.sqrt(1.8)
            A.append(row); y.append(0.)
    for key in range(len(NOTES)-1):
        for f in range(width):
            row = np.zeros(size)
            row[key*width+f] = math.sqrt(.12)
            row[(key+1)*width+f] = -math.sqrt(.12)
            A.append(row); y.append(0.)
    coefficients = np.linalg.lstsq(np.asarray(A), np.asarray(y), rcond=None)[0].reshape(len(NOTES), width)
    # Absolute smooth-target bounds avoid using deep analytic nodes or a
    # vanishing excitation as an excuse for arbitrarily large output gains.
    unshifted_prior = prior-offset
    coefficients = np.clip(coefficients, unshifted_prior-24, unshifted_prior+(36 if component else 24))
    return coefficients, prior, offset


def _joint_refinement(observations, grids, priors, offsets, grid):
    """Fit the smooth fields to powers jointly so V/H regularization respects
    their interference and cannot silently destroy the independently fitted sum.
    """
    width = len(grid)
    one = len(NOTES)*width
    size = 2*one
    R, rhs = [], []
    for component in (0, 1):
        for j in range(one):
            row = np.zeros(size); row[component*one+j] = math.sqrt(.008)
            R.append(row); rhs.append(priors[component].reshape(-1)[j]*math.sqrt(.008))
        for key in range(len(NOTES)):
            for f in range(1, width-1):
                row = np.zeros(size)
                first = component*one+key*width+f-1
                row[first:first+3] = np.array([1., -2., 1.])*math.sqrt(.8)
                R.append(row); rhs.append(0.)
        for key in range(len(NOTES)-1):
            for f in range(width):
                row = np.zeros(size)
                row[component*one+key*width+f] = math.sqrt(.05)
                row[component*one+(key+1)*width+f] = -math.sqrt(.05)
                R.append(row); rhs.append(0.)
    R, rhs = np.asarray(R), np.asarray(rhs)
    for o in observations:
        o['_basis'] = _row(math.log2(o['frequency_hz']), grid, NOTES.index(o['midi']))
    def objective(theta):
        penalty = R@theta-rhs
        value = .5*float(penalty@penalty)
        gradient = R.T@penalty
        for o in observations:
            basis = o['_basis']
            db = np.array([basis@theta[:one], basis@theta[one:]])
            raw_gain = 10**(db/20)/o['base_H']
            v, h = np.clip(raw_gain, *GAIN_LIMITS)
            gram = o['_matrices']
            g = np.array([v, h, 1.])
            power = np.maximum(np.einsum('i,nij,j->n', g, gram, g), 1e-24)
            root_w = np.sqrt(o['_timeweights'])
            residual = root_w*10*np.log10(power/o['_targets'])
            robust = np.sqrt(1+(residual/3)**2)
            value += float(np.sum(9*(robust-1)))
            influence = residual/robust
            if GAIN_LIMITS[0] < raw_gain[0] < GAIN_LIMITS[1]:
                derivative = root_w*v*(v*gram[:, 0, 0]+h*gram[:, 0, 1]+gram[:, 0, 2])/power
                gradient[:one] += float(influence@derivative)*basis
            if GAIN_LIMITS[0] < raw_gain[1] < GAIN_LIMITS[1]:
                derivative = root_w*h*(h*gram[:, 1, 1]+v*gram[:, 0, 1]+gram[:, 1, 2])/power
                gradient[one:] += float(influence@derivative)*basis
        return value, gradient
    bounds = []
    for component in (0, 1):
        base = (priors[component]-offsets[component]).reshape(-1)
        bounds += list(zip(base-24, base+(36 if component else 24)))
    initial = np.concatenate([g.reshape(-1) for g in grids])
    before, _ = objective(initial)
    fit = optimize.minimize(objective, initial, jac=True, method='L-BFGS-B', bounds=bounds,
                            options={'maxiter': 350, 'ftol': 1e-10, 'gtol': 1e-5, 'maxls': 30})
    for o in observations: del o['_basis']
    fields = [fit.x[:one].reshape(len(NOTES), width), fit.x[one:].reshape(len(NOTES), width)]
    return fields, {'method': 'analytic-gradient joint log-band-power refinement with smoothness priors',
                    'initial_objective': before, 'final_objective': float(fit.fun),
                    'iterations': int(fit.nit), 'converged': bool(fit.success), 'message': str(fit.message)}


def fit_radiation(reference_features, model_features, basis_rows, stems_dir):
    references = _load(reference_features, 'samples')
    models = _load(model_features, 'samples')
    references = [r for r in references if r['split'] == 'train']
    model_map = {m['id']: m for m in models}
    expected = {f'C{o}v{v}' for o in range(2, 7) for v in (4, 12)}
    if {r['id'] for r in references} != expected:
        raise ValueError('Radiation fit requires precisely the locked TRAIN10 reference cases')
    if not expected.issubset(model_map): raise ValueError('Missing TRAIN10 mechanics measurements')
    references = sorted(references, key=lambda r: (r['midi'], r['layer']))
    basis = _basis_index(_load(basis_rows))
    global_gain_db = float(np.median([20*math.log10(r['early_rms']/model_map[r['id']]['early_rms']) for r in references]))
    global_gain = 10**(global_gain_db/20)
    gram_data, stem_records = {}, []
    for reference in references:
        item = model_map[reference['id']]
        gram_data[item['id']], record = _gram_windows(stems_dir, item)
        stem_records.append(record)
    observations = []
    lower, upper = np.log(GAIN_LIMITS)
    for note in NOTES:
        rr = [r for r in references if r['midi'] == note]
        for n in range(1, PARTIALS+1):
            base = [_basis_value(basis, note, n, pol) for pol in (0, 1)]
            if not all(x is not None and x > 1e-8 for x in base): continue
            target, matrices, weights = [], [], []
            for ref in rr:
                rp = next((p for p in ref['partials'] if p['n'] == n), None)
                mp = next((p for p in model_map[ref['id']]['partials'] if p['n'] == n), None)
                if rp is None or mp is None: continue
                for j, gram in enumerate(gram_data[ref['id']][n]):
                    relative = rp['powers'][j]/ref['early_rms']**2
                    if relative < 1e-5: continue
                    model_component_power = max(float(gram[0, 0]+gram[1, 1]), 1e-24)
                    if model_component_power/model_map[ref['id']]['early_rms']**2 < 1e-7: continue
                    target.append(rp['powers'][j]/global_gain**2)
                    matrices.append(gram)
                    snr = float(np.clip((10*math.log10(relative)+50)/30, .1, 1))
                    weights.append(snr*[1., 1., .8, .6][j])
            if len(target) < 3: continue
            target, matrices, weights = np.asarray(target), np.asarray(matrices), np.asarray(weights)
            def prediction(theta):
                g = np.r_[np.exp(theta), 1.]
                return np.maximum(np.einsum('i,nij,j->n', g, matrices, g), 1e-24)
            def residual(theta, regularize=True):
                residuals = np.sqrt(weights)*10*np.log10(prediction(theta)/target)
                if regularize:
                    db = theta*20/math.log(10)
                    residuals = np.r_[residuals, .04*db[0], .08*db[1]]
                return residuals
            original = prediction(np.zeros(2))
            estimate = float(np.clip(np.sqrt(np.median(target/original)), .05, 20))
            candidates = []
            for secondary in (1., 8., 24.):
                start = np.log([estimate, min(39., estimate*secondary)])
                candidates.append(optimize.least_squares(residual, start, bounds=([lower, lower], [upper, upper]),
                    loss='soft_l1', f_scale=3., max_nfev=160))
            fit = min(candidates, key=lambda result: result.cost)
            gains = np.exp(fit.x)
            jacobian = fit.jac[:len(target)]
            singular = np.linalg.svd(jacobian, compute_uv=False)
            condition = float(singular[-1]/max(singular[0], 1e-20))
            leverage = np.linalg.norm(jacobian, axis=0)
            relative_weights = np.clip(leverage/20, 0, 1)
            relative_weights[1] *= min(1., condition/.025)
            fitted_error = float(np.sqrt(np.mean(residual(fit.x, False)**2)))
            relative_weights *= 1/(1+(fitted_error/8)**2)
            # Deep H nodes give noisy inversions; their absolute target is
            # supplied mostly by the smooth neighboring response.
            for pol in (0, 1):
                neighborhood = [_basis_value(basis, note, j, pol) for j in range(max(1, n-3), n+4)]
                neighborhood = [x for x in neighborhood if x is not None and x > 0]
                typical = float(np.median(neighborhood))
                relative_weights[pol] *= min(1., base[pol]/max(typical*.18, 1e-20))
            row = basis.get((note, n, 0))
            observations.append({'midi': note, 'n': n, 'frequency_hz': float(row['frequency_hz']),
                'base_H': base, 'gains': gains.tolist(), 'gains_db': (20*np.log10(gains)).tolist(),
                'target_db': (20*np.log10(np.asarray(base)*gains)).tolist(),
                'weights': relative_weights.tolist(), 'jacobian_singular_ratio': condition,
                'valid_power_observations': len(target), 'fit_weighted_rmse_db': fitted_error,
                'baseline_weighted_rmse_db': float(np.sqrt(np.mean(residual(np.zeros(2), False)**2))),
                'bound_hit': bool(np.any(gains < .026) or np.any(gains > 39.9)),
                '_matrices': matrices, '_targets': target, '_timeweights': weights})
    if not observations: raise ValueError('No identifiable TRAIN10 radiation observations')
    grid = np.linspace(math.log2(30), math.log2(20000), 32)
    grids, priors, offsets = [], [], []
    for pol in (0, 1):
        coefficients, prior, offset = _smooth_targets(observations, basis, grid, pol)
        grids.append(coefficients); priors.append(prior); offsets.append(offset)
    grids, joint_report = _joint_refinement(observations, grids, priors, offsets, grid)
    keys = []
    for k, note in enumerate(NOTES):
        ref = next(r for r in references if r['midi'] == note)
        orders = np.arange(1, PARTIALS+1)
        frequencies = ref['f1_hz']*orders*np.sqrt((1+ref['B']*orders*orders)/(1+ref['B']))
        fields = [np.interp(np.log2(frequencies), grid, curve[k]).tolist() for curve in grids]
        keys.append({'midi': note, 'radiation_db': fields[0], 'radiation_secondary_db': fields[1]})
    for o in observations:
        k = NOTES.index(o['midi'])
        target_db = np.array([np.interp(math.log2(o['frequency_hz']), grid, curve[k]) for curve in grids])
        gain = np.clip(10**(target_db/20)/o['base_H'], *GAIN_LIMITS)
        g = np.r_[gain, 1.]
        prediction = np.maximum(np.einsum('i,nij,j->n', g, o['_matrices'], g), 1e-24)
        errors = np.sqrt(o['_timeweights'])*10*np.log10(prediction/o['_targets'])
        o['regularized_gains'] = gain.tolist()
        o['regularized_weighted_rmse_db'] = float(np.sqrt(np.mean(errors*errors)))
        for field in ('_matrices', '_targets', '_timeweights'): del o[field]
    return {'schema_version': 1, 'training_ids': sorted(expected), 'keys': keys,
        'global_reference_gain_db': global_gain_db,
        'method': 'positive bounded two-polarization observation fit to stereo band-power/crosspower over four fixed windows and two training velocities, followed by log-frequency/register regularization',
        'interpretation': 'effective anisotropic radiation/observation identification; not unique physical soundboard parameters; mechanical state and contact remain unchanged',
        'heldout_measurements_used': False, 'gain_limits': list(GAIN_LIMITS),
        'absolute_target_units': '20 log10(|H|), not a correction dB',
        'frequency_grid_hz': (2**grid).tolist(),
        'grid_primary_db': grids[0].tolist(), 'grid_secondary_db': grids[1].tolist(),
        'secondary_prior_offset_db': offsets[1], 'stem_sources': stem_records,
        'joint_refinement': joint_report,
        'observations': observations,
        'fit_diagnostics': {'partial_fits': len(observations),
            'bound_hits': sum(o['bound_hit'] for o in observations),
            'median_raw_rmse_db': float(np.median([o['fit_weighted_rmse_db'] for o in observations])),
            'median_regularized_rmse_db': float(np.median([o['regularized_weighted_rmse_db'] for o in observations])),
            'median_before_rmse_db': float(np.median([o['baseline_weighted_rmse_db'] for o in observations]))}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference', type=Path, default=ROOT/'benchmark/reference_features.json')
    parser.add_argument('--model-features', type=Path, default=ROOT/'benchmark/mechanics_report_features.json')
    parser.add_argument('--basis', type=Path, default=ROOT/'benchmark/radiation-basis.json')
    parser.add_argument('--stems-dir', type=Path, default=ROOT/'benchmark/mechanics_stems')
    parser.add_argument('--output', type=Path, default=ROOT/'benchmark/radiation_fit.json')
    args = parser.parse_args()
    report = fit_radiation(args.reference, args.model_features, args.basis, args.stems_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(json.dumps(report['fit_diagnostics'], indent=2))


if __name__ == '__main__': main()
