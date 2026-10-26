#!/usr/bin/env python3
"""Plot the existing C4v8 recording and model WAVs with a common power scale.

This is a visual diagnostic; it neither modifies frozen metrics nor fits data.
"""
from __future__ import annotations
import json
import math
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

from benchmark import load_audio, sha256

ROOT = Path(__file__).resolve().parents[1]
CASE = 'C4v8'
RATE, WINDOW, HOP, NFFT = 48000, 4096, 512, 8192
DURATION, FMIN, FMAX, DYNAMIC_RANGE_DB = 3.5, 80, 12000, 80
SOURCES = [
    ('Recorded Yamaha C5', 'benchmark/reference_features.json', '#313947'),
    ('Original POC', 'benchmark/baseline_report_features.json', '#8593a6'),
    ('Calibrated model', 'benchmark/candidate_report_features.json', '#147e75'),
]


def main():
    out = ROOT / 'benchmark/report'
    out.mkdir(parents=True, exist_ok=True)
    rows = []
    for label, source, color in SOURCES:
        path = ROOT / source
        feature = next(r for r in json.loads(path.read_text())['samples'] if r['id'] == CASE)
        # Resolve regenerated audio in this checkout, not the historical
        # absolute machine path retained in the frozen feature record.
        folder = 'reference/wav' if source.endswith('/reference_features.json') else ('benchmark/baseline' if 'baseline' in source else 'benchmark/candidate')
        audio = ROOT / folder / (CASE + '.wav')
        assert sha256(audio) == feature['sha256'], f'Stale feature input: {audio}'
        rows.append(dict(label=label, feature=feature, audio=audio, feature_path=path, color=color))
    reference_rms = rows[0]['feature']['early_rms']
    for row in rows:
        f = row['feature']
        rate, audio = load_audio(row['audio'])
        assert rate == f['sample_rate']
        gain = reference_rms / f['early_rms']
        # Preserve actual pre-onset samples for the centered first STFT window.
        # Only the file boundary is zero-padded, consistently for all inputs.
        stop = min(len(audio), int(math.ceil((f['onset_seconds'] + DURATION + .15) * rate)))
        audio = audio[:stop] * gain
        divisor = math.gcd(RATE, rate)
        if rate != RATE:
            audio = signal.resample_poly(audio, RATE // divisor, rate // divisor, axis=0)
        pad = WINDOW // 2
        padded = np.pad(audio, ((pad, pad), (0, 0)))
        frequency, time, channel_psd = signal.spectrogram(
            padded, fs=RATE, window='hann', nperseg=WINDOW,
            noverlap=WINDOW-HOP, nfft=NFFT, detrend=False,
            scaling='density', mode='psd', axis=0)
        # spectrogram returns frequency × channels × time for samples × channels.
        power = np.mean(channel_psd, axis=1)
        time = time - pad / RATE - f['onset_seconds']
        valid_f = (frequency >= FMIN) & (frequency <= FMAX)
        valid_t = (time >= -HOP/RATE) & (time <= DURATION + HOP/RATE)
        db = 10 * np.log10(np.maximum(power[np.ix_(valid_f, valid_t)] / reference_rms**2, 1e-15))
        envelope = np.asarray(f['envelope_rms']) * gain / reference_rms
        row.update(gain=gain, frequency=frequency[valid_f], time=time[valid_t], db=db,
                   envelope_db=20*np.log10(np.maximum(envelope, 1e-8)))
    # One global color limit, never an independently normalized panel.
    vmax = float(5 * math.ceil(max(float(np.max(r['db'])) for r in rows)/5))
    vmin = vmax - DYNAMIC_RANGE_DB
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11, 'axes.titlesize': 13,
                         'axes.labelcolor': '#313947', 'xtick.color': '#313947', 'ytick.color': '#313947',
                         'figure.facecolor': '#fafbfe', 'savefig.facecolor': '#fafbfe'})
    fig = plt.figure(figsize=(13.5, 10))
    grid = fig.add_gridspec(4, 2, width_ratios=[1, .025], height_ratios=[1, 1, 1, .85],
                           left=.095, right=.92, top=.87, bottom=.15, hspace=.24, wspace=.035)
    axes = []
    for i, row in enumerate(rows):
        ax = fig.add_subplot(grid[i, 0], sharex=axes[0] if axes else None)
        axes.append(ax)
        mesh = ax.pcolormesh(row['time'], row['frequency'], row['db'], shading='auto',
                             cmap='magma', vmin=vmin, vmax=vmax, rasterized=True)
        ax.set_yscale('log')
        ax.set_ylim(FMIN, FMAX)
        ax.set_yticks([125, 250, 500, 1000, 2000, 4000, 8000], ['125', '250', '500', '1k', '2k', '4k', '8k'])
        ax.minorticks_off()
        ax.set_ylabel('Frequency (Hz)')
        ax.set_title(row['label'], loc='left', pad=6, fontweight='bold')
        ax.tick_params(axis='x', labelbottom=False)
    cbar = fig.colorbar(mesh, cax=fig.add_subplot(grid[:3, 1]))
    cbar.set_label('Stereo power density (dB / Hz relative to recorded early RMS²)', labelpad=10)
    env_ax = fig.add_subplot(grid[3, 0], sharex=axes[0])
    for row in rows:
        env_ax.plot(row['feature']['envelope_times_seconds'], row['envelope_db'],
                    color=row['color'], label=row['label'], lw=1.7,
                    linestyle='--' if row['label'] == 'Original POC' else '-')
    env_ax.set_ylabel('RMS level (dB)')
    env_ax.set_xlabel('Time after detected onset (seconds)')
    env_ax.set_title('Amplitude envelope · same fixed gains as the spectrograms', loc='left', pad=6, fontsize=12)
    env_ax.set_xlim(0, DURATION)
    env_ax.grid(alpha=.18)
    env_ax.legend(loc='lower left', ncols=3, fontsize=10, frameon=False)
    all_env = np.concatenate([r['envelope_db'] for r in rows])
    env_ax.set_ylim(5*math.floor(float(all_env.min())/5)-8, 5*math.ceil(float(all_env.max())/5)+2)
    fig.suptitle('C4 at held-out velocity · recording and two physical-model versions',
                 x=.095, ha='left', y=.968, fontsize=17, fontweight='bold')
    fig.text(.095, .928, 'Identical time, log-frequency and color scales; only the frozen 0.05–0.75 s RMS gain is applied.',
             color='#313947', fontsize=11)
    fig.text(.095, .035,
             '85.3 ms Hann windows · 10.7 ms hop · stereo power · envelope: saved 5 ms RMS measurements\n'
             'Visual diagnostic of one Yamaha C5 recording setup. Held out from fitting; not a blind listening test.',
             color='#505967', fontsize=10, linespacing=1.55)
    output = out / f'{CASE}-spectrogram.png'
    fig.savefig(output, dpi=180)
    plt.close(fig)
    metadata = {
        'schema_version': 1, 'case': CASE, 'split': 'heldout_velocity',
        'purpose': 'Visual diagnostic only. No model fitting or metric changes.',
        'parameters': {
            'analysis_sample_rate': RATE, 'resampling': 'scipy.signal.resample_poly default polyphase antialias filter',
            'window': 'Hann', 'window_samples': WINDOW, 'window_seconds': WINDOW/RATE,
            'hop_samples': HOP, 'hop_seconds': HOP/RATE, 'fft_samples': NFFT,
            'spectrum': 'One-sided PSD; arithmetic mean of channel powers; no mono waveform summation',
            'detrend': False, 'time_seconds': [0, DURATION], 'frequency_hz': [FMIN, FMAX],
            'frequency_axis': 'log', 'color_db_per_hz': [vmin, vmax],
            'color_reference': 'Recorded early RMS squared; one global maximum rounded up to 5 dB and 80 dB common range',
            'alignment': 'Frozen detected onset from each feature file; actual pre-onset samples retained; file boundaries zero-padded',
            'gain': 'One frozen 0.05–0.75 s early RMS scalar per model, fixed across all times, frequencies and envelope',
            'envelope': 'Frozen feature-file 5 ms stereo-power RMS envelope sampled every 20 ms; same model gains',
        },
        'inputs': [{
            'label': r['label'], 'audio_path': str(r['audio'].relative_to(ROOT)),
            'audio_sha256': r['feature']['sha256'],
            'feature_path': str(r['feature_path'].relative_to(ROOT)),
            'feature_sha256': sha256(r['feature_path']), 'onset_seconds': r['feature']['onset_seconds'],
            'gain_linear': r['gain'], 'gain_db': 20*math.log10(r['gain']),
        } for r in rows],
        'script_sha256': sha256(Path(__file__)), 'image_sha256': sha256(output),
    }
    sidecar = output.with_suffix('.json')
    sidecar.write_text(json.dumps(metadata, indent=2) + '\n')
    print(json.dumps({'figure': str(output), 'parameters': str(sidecar), 'color_range_db': [vmin, vmax],
                      'gains_db': {r['label']: 20*math.log10(r['gain']) for r in rows}}, indent=2))


if __name__ == '__main__':
    main()
