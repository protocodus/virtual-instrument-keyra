#!/usr/bin/env python3
"""Describe authenticated mechanism TRAIN recordings without fitting a default.

All powers use stereo power rather than mono summation. Short windows and tails
are censored to available source samples; there is no zero-padded time support.
FFT padding only interpolates the displayed spectrum, not frequency resolution.
"""
from __future__ import annotations
import hashlib
import io
import json
import math
from pathlib import Path
import re
import subprocess

import numpy as np
from scipy import signal, stats
from scipy.io import wavfile

from fetch_mechanism_references import PROJECT, ROOT, EXPECTED_TRAIN, git_blob, locked_inputs, pcm_helper, sha, source_pcm_digest, write

BANDS = np.asarray([20, 80, 200, 500, 1000, 2000, 4000, 8000, 12000, 19000, 24000], float)
WINDOWS = [(0, .005), (.005, .02), (.02, .05), (.05, .1), (.1, .25),
           (.25, .5), (.5, 1), (1, 2), (2, 4)]


def db(power, reference=1.):
    return float(10 * np.log10(max(float(power), 1.e-300) / max(float(reference), 1.e-300)))


def spectrum(x, rate):
    count = len(x)
    if count < 16:
        raise ValueError('Insufficient actual samples for a spectrum')
    window = signal.windows.hann(count, sym=False)
    nfft = 1 << int(math.ceil(math.log2(count * 4)))
    fft = np.fft.rfft(x * window[:, None], n=nfft, axis=0)
    channel = np.abs(fft) ** 2 / (nfft * np.sum(window ** 2))
    channel[1:-1] *= 2
    frequencies = np.fft.rfftfreq(nfft, 1 / rate)
    return frequencies, channel.mean(axis=1), channel


def stereo(x):
    powers = np.mean(x * x, axis=0)
    centered = x - np.mean(x, axis=0)
    denominator = np.sqrt(np.sum(centered[:, 0] ** 2) * np.sum(centered[:, 1] ** 2))
    return {'right_minus_left_db': db(powers[1], powers[0]),
            'correlation': float(np.sum(centered[:, 0] * centered[:, 1]) / denominator) if denominator > 0 else None,
            'channel_rms': np.sqrt(powers).tolist()}


def bands(x, rate, reference):
    f, p, _ = spectrum(x, rate)
    powers = [float(np.sum(p[(f >= lo) & (f < hi)])) for lo, hi in zip(BANDS[:-1], BANDS[1:])]
    return {'power': powers, 'relative_to_early_rms_db': [db(v, reference) for v in powers],
            'native_frequency_spacing_hz': rate / len(x), 'interpolated_bin_spacing_hz': float(f[1]),
            'low_band_resolution_warning': rate / len(x) > 20}


def current_presets():
    """Read the actual C++ preset values, without duplicating its switch logic."""
    out = PROJECT / 'out/mechanism-references'
    out.mkdir(parents=True, exist_ok=True)
    cpp, binary = out / 'preset_probe.cpp', out / 'preset_probe'
    cpp.write_text('''#include "keyra/physics/MechanismExciter.h"
#include <cstdio>
int main(){const char* names[]={"key_press","keybed","key_release","pedal"};
 for(unsigned i=0;i<4;++i){auto c=keyra::physics::mechanismPreset(static_cast<keyra::physics::MechanismKind>(i));
 std::printf("%s %.17g %.17g %.17g %.17g %.17g %.17g\\n",names[i],c.frequencyHz,c.lossPerSecond,
 c.modalMassKg,c.couplingResistanceKgPerSecond,c.triggerImpulseNs,c.directObservationGain);}}
''')
    flags = ['-O2', '-std=c++17', '-fno-exceptions', '-fno-rtti', '-fno-builtin', '-ffp-contract=off']
    subprocess.run(['g++', *flags, '-I' + str(PROJECT / 'include'), str(cpp), '-o', str(binary)], check=True)
    text = subprocess.check_output([str(binary)], text=True)
    header = PROJECT / 'include/keyra/physics/MechanismExciter.h'
    match = re.search(r'ratios\{\{([^}]+)\}\}', header.read_text())
    if not match:
        raise RuntimeError('Cannot identify the actual three-mode preset ratios')
    ratios = [float(x) for x in match[1].split(',')]
    presets = {}
    for line in text.splitlines():
        name, *values = line.split()
        row = dict(zip(('frequency_hz', 'loss_per_second', 'modal_mass_kg', 'coupling_resistance_kg_per_second',
                        'trigger_impulse_ns', 'direct_observation_gain'), map(float, values)))
        row['nominal_mode_frequencies_hz'] = [row['frequency_hz'] * r for r in ratios]
        row['nominal_free_amplitude_t60_seconds'] = math.log(1000) / row['loss_per_second']
        presets[name] = row
    return {'presets': presets, 'source_sha256': sha(header), 'probe_source_sha256': sha(cpp),
            'probe_binary_sha256': sha(binary), 'compiler': subprocess.check_output(['g++', '--version'], text=True).splitlines()[0],
            'flags': flags, 'interpretation': 'Authored free-source coefficients only. Body coupling, soundboard pressure and unstruck-string response are absent from these nominal frequencies/T60 values.'}


def describe(row, helper, presets):
    path = ROOT / row['wav_path']
    if row['role'] != 'train' or row['id'] not in EXPECTED_TRAIN:
        raise RuntimeError('Refuse a non-TRAIN reference')
    flac = ROOT / row['flac_path']
    if flac.stat().st_size != row['flac_bytes'] or git_blob(flac) != row['git_blob_sha1'] or sha(flac) != row['flac_sha256'] or helper.decoded_pcm_identity(path) != row['decoded_pcm']:
        raise RuntimeError('Reference bytes/PCM do not match acquisition pins')
    if source_pcm_digest(flac) != row['decoded_pcm']['sha256']:
        raise RuntimeError('WAV measurements are not the authenticated source PCM')
    wav_bytes = path.read_bytes()
    measured_wav_sha = hashlib.sha256(wav_bytes).hexdigest()
    rate, raw = wavfile.read(io.BytesIO(wav_bytes))
    if raw.dtype != np.int32 or raw.ndim != 2 or raw.shape[1] != 2 or np.any(raw & 255):
        raise RuntimeError('Expected exact stereo PCM24 decode')
    # Bind the array actually used for measurements, not a preceding file read.
    # An editor/replacement between verification and loading must not associate
    # changed samples with the previously authenticated identity.
    packed = np.ascontiguousarray(raw, dtype='<i4').reshape(-1).view(np.uint8).reshape(-1, 4)[:, 1:].tobytes()
    loaded_pcm = {'sha256': hashlib.sha256(packed).hexdigest(), 'encoding': 's24le-interleaved',
                  'sample_rate': int(rate), 'channels': int(raw.shape[1]), 'frames': int(len(raw)), 'pcm_bits': 24}
    if loaded_pcm != row['decoded_pcm']:
        raise RuntimeError('Loaded measurement array differs from authenticated source PCM')
    x = raw.astype(np.float64) / 2147483648.
    if not np.isfinite(x).all() or rate != 48000:
        raise RuntimeError('Invalid source audio')
    ms = rate // 1000
    power1 = np.asarray([np.mean(x[k:k + ms] ** 2) for k in range(0, min(len(x), rate), ms)])
    threshold = max(float(np.max(power1)) * 1.e-4, 1.e-14)
    crossings = np.flatnonzero(power1 >= threshold)
    onset = int(crossings[0] * ms) if len(crossings) else 0
    active = x[onset:]
    support = len(active) / rate
    early = active[:min(len(active), int(.25 * rate))]
    early_power = float(np.mean(early ** 2))
    frame = rate // 200
    envelope = []
    for start in range(0, len(active), frame):
        chunk = active[start:start + frame]
        if len(chunk) < 16:
            continue
        envelope.append({'time_seconds_after_onset': (start + .5 * len(chunk)) / rate,
                         'duration_seconds': len(chunk) / rate, 'power': float(np.mean(chunk ** 2)),
                         'relative_to_early_rms_db': db(np.mean(chunk ** 2), early_power)})
    ep = np.asarray([v['power'] for v in envelope])
    times = np.asarray([v['time_seconds_after_onset'] for v in envelope])
    peak_index = int(np.argmax(ep))
    tail = active[-min(int(.1 * rate), len(active)):]
    tail_power = float(np.mean(tail ** 2))
    # A recorded floor is unknown; this is a conservative trace support mask,
    # not an SNR estimate or an identified physical damping coefficient.
    usable = (np.arange(len(ep)) > peak_index) & (ep >= max(np.max(ep) * 1.e-4, tail_power * 4))
    decay = None
    if np.count_nonzero(usable) >= 6 and np.ptp(times[usable]) >= .03:
        t, y = times[usable], 10 * np.log10(np.maximum(ep[usable], 1.e-300))
        slope, intercept, low, high = stats.theilslopes(y, t)
        fit = intercept + slope * t
        denominator = np.sum((y - np.mean(y)) ** 2)
        decay = {'slope_db_per_second': float(slope), 'slope_interval_db_per_second': [float(low), float(high)],
                 'r_squared': float(1 - np.sum((y - fit) ** 2) / denominator) if denominator > 0 else None,
                 'fit_interval_seconds_after_onset': [float(t[0]), float(t[-1])], 'observations': len(t),
                 'extrapolated_t60_seconds': float(-60 / slope) if slope < 0 else None,
                 'interpretation': 'Broadband envelope descriptor of this edited recording, not intrinsic mechanism loss or a source/body separation.'}
    windows = []
    for start, end in WINDOWS:
        actual_end = min(end, support)
        i, j = round(start * rate), min(len(active), round(actual_end * rate))
        if j - i < 16:
            continue
        segment = active[i:j]
        windows.append({'requested_window_seconds': [start, end], 'actual_window_seconds': [i / rate, j / rate],
                        'right_censored': j / rate < end - 1.e-9, 'frames': len(segment),
                        'rms_relative_to_early_db': db(np.mean(segment ** 2), early_power),
                        'bands': bands(segment, rate, early_power), 'stereo': stereo(segment)})
    f, p, channels = spectrum(early, rate)
    logp = 10 * np.log10(np.maximum(p, 1.e-300))
    native_resolution = rate / len(early)
    peaks, properties = signal.find_peaks(logp, prominence=6, distance=max(1, round(20 / f[1])))
    selected = [i for i in np.argsort(p[peaks])[::-1] if 20 <= f[peaks[i]] <= 19000 and
                logp[peaks[i]] >= np.max(logp[(f >= 20) & (f <= 19000)]) - 35][:12]
    peak_rows = [{'frequency_hz': float(f[peaks[i]]), 'power_relative_to_strongest_fft_bin_db': float(logp[peaks[i]] - np.max(logp)),
                  'local_prominence_db': float(properties['prominences'][i]), 'native_frequency_spacing_hz': native_resolution,
                  'physical_identity': 'unassigned recording component'} for i in selected]
    sample_power = np.mean(active ** 2, axis=1)
    cumulative = np.cumsum(sample_power)
    energy_times = {str(percent): float(np.searchsorted(cumulative, cumulative[-1] * percent / 100) / rate)
                    for percent in (10, 50, 90, 99)}
    kind = 'key_release' if row['kind'] == 'key_release' else 'pedal' if row['kind'].startswith('pedal_') else None
    coverage = None
    if kind:
        modes = presets['presets'][kind]['nominal_mode_frequencies_hz']
        mask = np.zeros(len(f), bool)
        for frequency in modes:
            mask |= np.abs(f - frequency) <= max(native_resolution, .05 * frequency)
        valid = (f >= 20) & (f <= 19000)
        coverage = {'preset': kind, 'nominal_mode_frequencies_hz': modes,
                    'recorded_early_power_fraction_near_free_source_modes': float(np.sum(p[mask & valid]) / np.sum(p[valid])),
                    'half_bandwidth_rule': 'max(native FFT spacing,5% center frequency)',
                    'recorded_early_power_fraction_below_lowest_free_source_mode': float(np.sum(p[valid & (f < min(modes))]) / np.sum(p[valid])),
                    'interpretation': 'Descriptive free-source frequency coverage only; the connected body/string network can supply other frequencies and decay. This is not a whole-model error or fit objective.'}
    return {'id': row['id'], 'role': 'train', 'kind': row['kind'], 'family': row['family'], 'midi': row['midi'],
            'wav_sha256': measured_wav_sha, 'flac_sha256': row['flac_sha256'], 'decoded_pcm': loaded_pcm,
            'duration_seconds': len(x) / rate, 'observed_onset_seconds': onset / rate,
            'available_seconds_after_onset': support, 'early_gain_window_seconds': [0, len(early) / rate],
            'early_rms_dbfs': db(early_power), 'raw_peak_dbfs': db(np.max(x * x)),
            'early_spectral_bands': bands(early, rate, early_power), 'early_stereo': stereo(early),
            'early_spectral_power_fraction_below_20hz': float(np.sum(p[f < 20]) / np.sum(p)),
            'early_spectral_dc_bin_power_fraction': float(p[0] / np.sum(p)),
            'low_frequency_power_identity': 'Unassigned: may include event/body/room/background/editing contributions.',
            'prominent_early_recording_peaks': peak_rows,
            'peak_envelope_time_seconds': float(times[peak_index]), 'energy_percentile_times_seconds': energy_times,
            'tail_100ms_relative_to_early_rms_db': db(tail_power, early_power),
            'tail_100ms_may_contain_event_body_room_or_background': True,
            'right_censored_for_requested_four_second_support': support < 4,
            'full_support_5ms_envelope': envelope, 'analysis_windows': windows, 'broadband_decay': decay,
            'free_source_preset_coverage': coverage}


def plot(rows):
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except ImportError:
        return {'created': False, 'reason': 'Matplotlib unavailable; numeric evidence remains complete.'}
    plt.rcParams['svg.hashsalt'] = 'keyra-mechanism-train-v1'
    fig, axes = plt.subplots(2, 3, figsize=(13, 6), constrained_layout=True)
    groups = [('Key release', lambda r: r['kind'] == 'key_release'),
              ('Pedal action', lambda r: r['kind'].startswith('pedal_')),
              ('String release', lambda r: r['kind'] == 'string_release')]
    centers = np.sqrt(BANDS[:-1] * BANDS[1:])
    for col, (title, choose) in enumerate(groups):
        for row in filter(choose, rows):
            envelope = row['full_support_5ms_envelope']
            label = row['id'].replace('key-release-', '').replace('string-release-', '')
            axes[0, col].plot([v['time_seconds_after_onset'] for v in envelope],
                              [v['relative_to_early_rms_db'] for v in envelope], label=label, linewidth=1)
            axes[1, col].semilogx(centers, row['early_spectral_bands']['relative_to_early_rms_db'], marker='.', label=label)
        axes[0, col].set(title=title, xlabel='Seconds after detected onset', ylabel='5 ms RMS / early RMS, dB', ylim=(-80, 25))
        axes[1, col].set(xlabel='Band center, Hz', ylabel='Early band power / early RMS², dB', ylim=(-100, 5))
        for ax in axes[:, col]:
            ax.grid(alpha=.25)
            ax.legend(fontsize=8)
    fig.suptitle('TRAIN mechanism recordings: relative envelopes and stereo-power spectra\nDifferent library layers and unknown physical strengths; no physical source separation', fontsize=11)
    path = ROOT / 'figures/training-summary.svg'
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, metadata={'Date': None})
    plt.close(fig)
    return {'created': True, 'path': str(path.relative_to(PROJECT)), 'sha256': sha(path)}


def main():
    split, manifest = locked_inputs()
    if not manifest['initial_training_acquisition_verified']:
        raise RuntimeError('Acquire/authenticate TRAIN before feature extraction')
    input_paths = [Path(__file__), PROJECT / 'tools/fetch_mechanism_references.py',
                   ROOT / 'manifest.json', ROOT / 'split.json', ROOT / 'split-lock.json',
                   ROOT / 'upstream-inventory.json', PROJECT / 'include/keyra/physics/MechanismExciter.h']
    inputs = {str(p.relative_to(PROJECT)): sha(p) for p in input_paths}
    presets = current_presets()
    rows = [describe(row, pcm_helper(), presets) for row in manifest['samples'] if row['role'] == 'train']
    if {r['id'] for r in rows} != EXPECTED_TRAIN:
        raise RuntimeError('Incomplete training measurements')
    locked_inputs()
    if any(sha(PROJECT / n) != h for n, h in inputs.items()):
        raise RuntimeError('Analysis inputs changed during extraction')
    figure = plot(rows)
    document = {'schema_version': 1, 'split_sha256': sha(ROOT / 'split.json'), 'input_sha256': inputs,
                'training_ids': sorted(EXPECTED_TRAIN), 'reserved_evaluation_audio_opened': False,
                'numeric_floor_db': -3000, 'band_edges_hz': BANDS.tolist(),
                'onset_definition': 'First1ms stereo-power RMS block at least40dB below first-second envelope peak, with1e-7 amplitude floor; edited-file start is not a measured physical event time.',
                'window_policy': 'Use only actual available support; short windows are explicitly right-censored. Spectral zero padding interpolates bins and does not improve native resolution.',
                'decay_policy': 'Descriptive broadband Theil-Sen slope after peak, above40dB below peak and6dB above final100ms proxy; not a physical loss identification or calibrated background/SNR.',
                'samples': rows, 'current_authored_presets': presets, 'figure': figure,
                'fitted_or_adopted_default': False, 'runtime_waveforms_embedded': False,
                'limits': ['One edited source library and microphone chain; no calibrated contact force/velocity, mass, body-only trace or acoustic level.',
                           'Key-release noises do not isolate finger contact, keybed impact, hammer strike or hammer return.',
                           'String-release families mix according to source SFZ; measuring one file does not reconstruct the complete release performance.',
                           'Free-source preset coverage excludes existing reciprocal body/string paths and cannot establish total-model quality.',
                           'Eight same-library source files remain reserved/unopened; these are not independent instruments or calibrated repetition statistics.']}
    write(ROOT / 'train_features.json', document)
    receipt = {'schema_version': 1, 'training_files_measured': len(rows), 'training_ids': sorted(EXPECTED_TRAIN),
               'reserved_downloaded_decoded_or_analyzed': [], 'feature_sha256': sha(ROOT / 'train_features.json'),
               'manifest_sha256': sha(ROOT / 'manifest.json'), 'split_sha256': sha(ROOT / 'split.json'),
               'input_sha256': inputs, 'current_preset_source_sha256': presets['source_sha256'],
               'no_default_or_dsp_change': True, 'no_runtime_waveform_embedding': True,
               'all_windows_use_actual_support': True, 'figure': figure}
    write(ROOT / 'analysis-receipt.json', receipt)
    print(json.dumps({**receipt, 'input_sha256': 'See analysis-receipt.json'}, indent=2))


if __name__ == '__main__':
    main()
