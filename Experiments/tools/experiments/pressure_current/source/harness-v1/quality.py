"""Frozen-recipe numerical pressure/output comparison; no audio alignment or fit.

Engineering error limits are not audibility or recording-realism thresholds.
Inputs are compared at their original scale, delay, onset and sample support.
Only selftest() manufactures data; this module reads no files or recordings.
"""
import os
for _name in ('OPENBLAS_NUM_THREADS', 'OMP_NUM_THREADS', 'MKL_NUM_THREADS'):
    os.environ[_name] = '1'
import json
import math
import numpy as np

CONSTANTS = {
    'sample_rates': (44100, 48000, 88200, 96000),
    'maximum_null_rms_db': -110.,
    'maximum_absolute_error_factor': 1.e-4,
    'maximum_LR_shift_db': .001,
    'maximum_correlation_shift': 1.e-5,
    'maximum_mono_shift_db': .001,
    'maximum_band_shift_db': .01,
    'relative_power_floor': 1.e-10,
    'window_edges_seconds': (.05, .20),
    'band_edges_hz': (0., 31.25, 250., 1000., 4000., 12000., 19000.),
    'absolute_error_reference': 'old peak in the same window',
    'baseline_wholly_zero_requires_candidate_wholly_zero': True,
}
FFT_NORMALIZATION = (
    'symmetric np.hanning(N); mean channel |rfft(x*w)|^2/(N*sum(w^2)); '
    'one-sided interior bins doubled, DC and even-N Nyquist counted once. '
    'Sum equals Hann-squared-weighted mean stereo power. No detrending.'
)
RECIPE = {**CONSTANTS, 'FFT_normalization': FFT_NORMALIZATION,
          'FFT_gated_at_all_declared_rates': True,
          'correlation': 'mean-removed Pearson, with baseline-variance mask',
          'adjustments': 'none: no level matching, onset, delay, detrending or alignment'}


def _ratio_db(numerator, denominator):
    if denominator <= 0:
        return None, 'both_zero' if numerator == 0 else 'old_zero'
    if numerator <= 0:
        return None, 'new_zero'
    return 10.*(math.log10(numerator)-math.log10(denominator)), 'defined'


def _power(x):
    return float(np.mean(x*x)) if x.size else 0.


def _stereo(x):
    channel = np.mean(x*x, axis=0) if len(x) else np.zeros(2)
    centered = x-np.mean(x, axis=0) if len(x) else x
    variance = np.mean(centered*centered, axis=0) if len(x) else np.zeros(2)
    lr, lr_status = _ratio_db(float(channel[0]), float(channel[1]))
    if lr is None:
        lr_status = ('both_channels_zero' if not np.any(channel)
                     else 'left_channel_zero' if channel[0] == 0 else 'right_channel_zero')
    correlation = None
    if variance[0] > 0 and variance[1] > 0:
        covariance = float(np.mean(centered[:, 0]*centered[:, 1]))
        correlation = float(np.clip(covariance/math.sqrt(float(variance[0]*variance[1])), -1., 1.))
    return {
        'channel_power': channel.tolist(), 'variance': variance.tolist(),
        'mono_power': _power(np.mean(x, axis=1)) if len(x) else 0.,
        'LR_db': lr, 'LR_status': lr_status,
        'correlation': correlation,
        'correlation_status': 'defined' if correlation is not None else 'zero_variance',
    }


def _window(old, new, whole_old_power, name, start, end, rate):
    a, b = old[start:end], new[start:end]
    error = b-a
    old_power, new_power, error_power = _power(a), _power(b), _power(error)
    old_peak = float(np.max(np.abs(a))) if len(a) else 0.
    error_peak = float(np.max(np.abs(error))) if len(error) else 0.
    old_stereo, new_stereo = _stereo(a), _stereo(b)
    floor = old_power*CONSTANTS['relative_power_floor']
    masks = {
        'relative_null': old_power > 0 and old_power >= whole_old_power*CONSTANTS['relative_power_floor'],
        'LR': old_power > 0 and all(p > 0 and p >= floor for p in old_stereo['channel_power']),
        'correlation': old_power > 0 and all(p > 0 and p >= floor for p in old_stereo['variance']),
        'mono': old_stereo['mono_power'] > 0 and old_stereo['mono_power'] >= floor,
    }
    null_db, null_status = _ratio_db(error_power, old_power)
    if error_power == 0:
        null_status = 'exact_zero_error' if old_power > 0 else 'both_zero'
    lr_shift = (new_stereo['LR_db']-old_stereo['LR_db']
                if old_stereo['LR_db'] is not None and new_stereo['LR_db'] is not None else None)
    correlation_shift = (new_stereo['correlation']-old_stereo['correlation']
                         if old_stereo['correlation'] is not None and new_stereo['correlation'] is not None else None)
    mono_shift, mono_status = _ratio_db(new_stereo['mono_power'], old_stereo['mono_power'])
    absolute_limit = CONSTANTS['maximum_absolute_error_factor']*(1.+old_peak)
    gates = {
        'absolute_error': error_peak <= absolute_limit,
        'relative_null': not masks['relative_null'] or error_power <= old_power*10.**(CONSTANTS['maximum_null_rms_db']/10.),
        'LR': not masks['LR'] or lr_shift is not None and abs(lr_shift) <= CONSTANTS['maximum_LR_shift_db'],
        'correlation': not masks['correlation'] or correlation_shift is not None and abs(correlation_shift) <= CONSTANTS['maximum_correlation_shift'],
        'mono': not masks['mono'] or mono_shift is not None and abs(mono_shift) <= CONSTANTS['maximum_mono_shift_db'],
    }
    return {
        'name': name, 'start_frame': start, 'end_frame': end, 'frames': end-start,
        'seconds': [start/rate, end/rate], 'empty': start == end,
        'old_power': old_power, 'new_power': new_power, 'error_power': error_power,
        'old_rms': math.sqrt(old_power), 'new_rms': math.sqrt(new_power),
        'error_rms': math.sqrt(error_power), 'null_rms_db': null_db, 'null_rms_status': null_status,
        'old_peak': old_peak, 'maximum_absolute_error': error_peak, 'absolute_error_limit': absolute_limit,
        'old_stereo': old_stereo, 'new_stereo': new_stereo,
        'LR_shift_db': lr_shift, 'correlation_shift': correlation_shift,
        'mono_shift_db': mono_shift, 'mono_shift_status': mono_status,
        'baseline_window_power_floor': floor, 'masks': masks, 'gates': gates,
        'pass': all(gates.values()),
    }


def _spectrum(old, new, rate):
    n = len(old); window = np.hanning(n)
    denominator = n*float(np.sum(window*window))
    weights = np.ones(n//2+1)
    weights[1:-1 if n % 2 == 0 else None] = 2.
    def powers(x):
        transformed = np.fft.rfft(x*window[:, None], axis=0)
        return np.mean(transformed.real**2+transformed.imag**2, axis=1)*weights/denominator
    a, b, error = powers(old), powers(new), powers(new-old)
    total = float(np.sum(a)); threshold = total*CONSTANTS['relative_power_floor']
    frequencies = np.fft.rfftfreq(n, 1./rate)
    edges = (*CONSTANTS['band_edges_hz'], rate/2.)
    bands = []
    for index, (lo, hi) in enumerate(zip(edges[:-1], edges[1:])):
        # rfft ends at Nyquist by definition. Taking all remaining bins avoids
        # losing its endpoint to the roundoff in rfftfreq's Hz representation.
        support = (frequencies >= lo) if index == len(edges)-2 else ((frequencies >= lo) & (frequencies < hi))
        old_power = float(np.sum(a[support])); new_power = float(np.sum(b[support]))
        error_power = float(np.sum(error[support]))
        shift, status = _ratio_db(new_power, old_power)
        null, null_status = _ratio_db(error_power, old_power)
        if error_power == 0 and old_power > 0: null_status = 'exact_zero_error'
        mask = total > 0 and old_power >= threshold
        passed = not mask or shift is not None and abs(shift) <= CONSTANTS['maximum_band_shift_db']
        bands.append({
            'index': index, 'hz': [lo, hi], 'upper_inclusive': index == len(edges)-2,
            'bins': int(np.count_nonzero(support)), 'old_power': old_power, 'new_power': new_power,
            'error_power': error_power, 'error_rms': math.sqrt(error_power),
            'signed_power_change': new_power-old_power, 'absolute_power_change': abs(new_power-old_power),
            'shift_db': shift, 'shift_status': status, 'null_rms_db': null, 'null_rms_status': null_status,
            'baseline_power_mask': mask, 'gate_applied': mask, 'pass': passed,
        })
    return {'normalization': FFT_NORMALIZATION, 'old_total_power': total,
            'new_total_power': float(np.sum(b)), 'error_total_power': float(np.sum(error)),
            'baseline_power_floor': threshold, 'bands': bands,
            'pass': all(row['pass'] for row in bands)}


def compare(a, b, rate):
    """Compare equal Nx2 raw-f64 or emitted-f32 payloads with no adjustment.

    All seven FFT bands are evaluated at all four rates. Weak/empty/zero-power
    observations remain in the report; undefined dB/correlation is None with a
    status. An active strong-baseline gate rejects new zero power/variance.
    Empty fixed windows contain no samples and therefore apply no relative gate.
    """
    if isinstance(rate, bool) or rate not in CONSTANTS['sample_rates']:
        raise ValueError('Expected one of the four declared sample rates')
    old_array, new_array = np.asarray(a), np.asarray(b)
    if np.iscomplexobj(old_array) or np.iscomplexobj(new_array):
        raise ValueError('Audio inputs must be real')
    old, new = np.asarray(old_array, dtype=np.float64), np.asarray(new_array, dtype=np.float64)
    if old.shape != new.shape or old.ndim != 2 or old.shape[1] != 2 or len(old) < 3:
        raise ValueError('Expected equal Nx2 arrays with at least three frames')
    finite = bool(np.isfinite(old).all() and np.isfinite(new).all())
    if not finite:
        return {'metrics': {'sample_rate': int(rate), 'frames': len(old), 'status': 'nonfinite_input'},
                'gates': {'finite_samples': False}, 'pass': False}
    try:
        with np.errstate(over='raise', invalid='raise', divide='raise'):
            whole_power = _power(old); n = len(old)
            first, second = [min(n, int(round(t*rate))) for t in CONSTANTS['window_edges_seconds']]
            ranges = (('whole', 0, n), ('0_to_50ms', 0, first),
                      ('50_to_200ms', first, second), ('200ms_to_end', second, n))
            windows = [_window(old, new, whole_power, name, start, end, rate) for name, start, end in ranges]
            spectrum = _spectrum(old, new, rate)
    except (FloatingPointError, OverflowError):
        return {'metrics': {'sample_rate': int(rate), 'frames': len(old), 'status': 'derived_numeric_overflow'},
                'gates': {'finite_samples': True, 'finite_metrics': False}, 'pass': False}
    silent = bool(not np.any(old)); silent_exact = not silent or bool(not np.any(new))
    gates = {'finite_samples': True, 'silent_baseline_exact': silent_exact,
             'window_comparisons': all(row['pass'] for row in windows), 'all_spectral_bands': spectrum['pass']}
    return {'metrics': {'sample_rate': int(rate), 'frames': len(old), 'baseline_wholly_zero': silent,
                        'windows': windows, 'spectrum': spectrum,
                        'limits_scope': 'Numerical engineering guards; no audibility or recording-realism claim.'},
            'gates': gates, 'pass': all(gates.values())}


def selftest():
    """Small manufactured checks only; no files, recordings or model inputs."""
    rate = 48000; n = 16384; t = np.arange(n, dtype=np.float64)/rate
    tones = (55., 220., 550., 1500., 6500., 14500., 21000.)
    left = sum(.05/(i+1)*np.sin(2*np.pi*f*t+.17*i) for i, f in enumerate(tones))+.015
    right = sum(.04/(i+1)*np.sin(2*np.pi*f*t+.37+.23*i) for i, f in enumerate(tones))-.009
    source = np.column_stack((left, right))
    identity = compare(source, source.copy(), rate)
    amplitude = compare(source, source*1.002, rate)
    stereo = source.copy(); stereo[:, 1] *= 1.0005
    changed_stereo = compare(source, stereo, rate)
    zero = np.zeros_like(source); silent_identity = compare(zero, zero, rate)
    tiny = zero.copy(); tiny[0, 0] = 1.e-20
    silent_changed = compare(zero, tiny, rate)
    constant = np.column_stack((np.ones(n)*.125, np.ones(n)*.25))
    constant_identity = compare(constant, constant, rate)
    w = np.hanning(n)
    expected = float(np.sum(np.mean(source*source, axis=1)*w*w)/np.sum(w*w))
    checks = {
        'identity_pass': identity['pass'],
        'amplitude_rejected_by_relative_null': not amplitude['metrics']['windows'][0]['gates']['relative_null'],
        'amplitude_rejected_by_band_shift': not amplitude['gates']['all_spectral_bands'],
        'stereo_perturbation_rejected_by_LR': not changed_stereo['metrics']['windows'][0]['gates']['LR'],
        'exact_silence_pass': silent_identity['pass'],
        'nonzero_silence_candidate_rejected': not silent_changed['gates']['silent_baseline_exact'],
        'zero_variance_identity_pass': constant_identity['pass'],
        'hann_parseval_normalization': math.isclose(identity['metrics']['spectrum']['old_total_power'], expected, rel_tol=1.e-13),
        'all_seven_bands_retained': len(identity['metrics']['spectrum']['bands']) == 7,
        'all_four_windows_retained': len(identity['metrics']['windows']) == 4,
    }
    checks['all_rfft_bins_covered_all_rates_even_odd'] = all(
        sum(row['bins'] for row in _spectrum(source[:length], source[:length], sample_rate)['bands']) == length//2+1
        for sample_rate in CONSTANTS['sample_rates'] for length in (n, n-1))
    result = {'manufactured_only': True, 'recording_or_model_inputs': False,
              'constants': CONSTANTS, 'FFT_normalization': FFT_NORMALIZATION,
              'checks': checks, 'pass': all(checks.values())}
    json.dumps(result, allow_nan=False)
    return result


if __name__ == '__main__':
    print(json.dumps(selftest(), indent=2, allow_nan=False))
