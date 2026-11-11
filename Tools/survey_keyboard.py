#!/usr/bin/env python3
"""Survey every key of a piano for jumps from one key to the next: the
evidence for the key level and balance smoothing in initCalibrations()
(KeyraEngine.cpp, Docs/research/key-balance-smoothing-2026-11-10.md).

Each of the 88 keys is struck alone from silence at velocities 40, 80 and
120 (one render each, 4 s, gain .07, a 20 Hz high-pass). Per key: its level
(dB, both channels' mean square 50 to 750 ms after the onset), its balance
(dB, right over left over the same window), its brightness (octaves, the
power-weighted mean of log2(f/f1) over that window, from 0.7 f1 up), its
decay (dB/s, a Theil-Sen line through the 50 ms mean-square envelope from
0.5 to 3 s) and its rise (ms, 10 to 90 % of the 5 ms envelope's peak in the
first 150 ms). A key's jump in a measure is its value less the median of
its up to six neighbours within three keys (decay and rise as log ratios).
Per renderer, velocity and measure the table gives the jumps' rms and the
largest. No recording is read and nothing is fitted.

  python3 -B Tools/survey_keyboard.py --renderer 0.4.31=old/keyra_render \\
      --renderer 0.4.32=build/keyra_render [--model parlor] [--jobs 3] [--json OUT]
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
from scipy import ndimage, signal, stats

import piano_analysis as pa

MODELS = ('concert', 'parlor', 'baby', 'upright')
VELOCITIES = (40, 80, 120)
MEASURES = ('level', 'balance', 'bright', 'decay', 'rise')


def measure(job):
    renderer, model, note, velocity = job
    with tempfile.TemporaryDirectory() as tmp:
        events = os.path.join(tmp, 'events')
        with open(events, 'w') as f:
            f.write(f'0.1 on {note} {velocity}\n')
        wav = os.path.join(tmp, 'render.wav')
        subprocess.run([renderer, '--events', events, '--output', wav, '--duration', '4', '--gain', '.07',
                        '--body', model], check=True, stdout=subprocess.DEVNULL)
        sr, x = pa.load(wav)
    x = signal.sosfiltfilt(signal.butter(2, 20, 'highpass', fs=sr, output='sos'), x, axis=0)
    s = pa.onset(x, sr)
    e = x[s + int(.05 * sr):s + int(.75 * sr)]
    f1 = pa.midi_hz(note)
    f, p = signal.welch(e.mean(axis=1), sr, nperseg=8192)
    k = f > .7 * f1
    power = np.mean(x * x, axis=1)
    env = ndimage.uniform_filter1d(power, int(.05 * sr))[s:]
    t = np.arange(len(env)) / sr
    sel = (t >= .5) & (t <= 3.)
    decay = stats.theilslopes(10 * np.log10(env[sel][::480] + 1e-30), t[sel][::480])[0]
    # The filter's rounding can leave a mean square a hair under 0.
    env5 = np.sqrt(np.maximum(ndimage.uniform_filter1d(power, int(.005 * sr)), 0))[s:s + int(.15 * sr)]
    peak = env5.max()
    rise = (np.flatnonzero(env5 >= .9 * peak)[0] - np.flatnonzero(env5 >= .1 * peak)[0]) / sr * 1000
    return dict(note=note, velocity=velocity, level=10 * np.log10(np.mean(e * e) + 1e-30),
                balance=10 * np.log10(np.mean(e[:, 1] ** 2) / np.mean(e[:, 0] ** 2)),
                bright=float(np.sum(p[k] * np.log2(f[k] / f1)) / np.sum(p[k])), decay=float(decay), rise=rise)


def jumps(rows, velocity, key):
    v = np.array([r[key] for r in sorted(rows, key=lambda r: r['note']) if r['velocity'] == velocity], float)
    if key in ('decay', 'rise'):
        v = np.log(np.maximum(np.abs(v), 1e-3))
    return np.array([v[i] - np.median([v[j] for j in range(max(0, i - 3), min(len(v), i + 4)) if j != i])
                     for i in range(len(v))])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--renderer', action='append', required=True, help='NAME=PATH, once per renderer')
    ap.add_argument('--model', action='append', choices=MODELS)
    ap.add_argument('--jobs', type=int, default=3)
    ap.add_argument('--json', help='write every key\'s measures here')
    a = ap.parse_args()
    renderers = [r.split('=', 1) for r in a.renderer]
    out = {}
    with ProcessPoolExecutor(a.jobs) as ex:
        for model in a.model or MODELS:
            for name, path in renderers:
                jobs = [(path, model, n, v) for v in VELOCITIES for n in range(21, 109)]
                out.setdefault(model, {})[name] = list(ex.map(measure, jobs, chunksize=4))
    print('| piano | velocity | renderer | ' + ' | '.join(f'{m} rms / max' for m in MEASURES) + ' |')
    print('|---|---:|---|' + '---:|' * len(MEASURES))
    for model, by in out.items():
        for v in VELOCITIES:
            for name, rows in by.items():
                cells = []
                for m in MEASURES:
                    d = jumps(rows, v, m)
                    cells.append(f'{np.sqrt(np.mean(d * d)):.2f} / {np.max(np.abs(d)):.1f}')
                print(f'| {model} | {v} | {name} | ' + ' | '.join(cells) + ' |')
    if a.json:
        with open(a.json, 'w') as f:
            json.dump(out, f, indent=1)


if __name__ == '__main__':
    main()
