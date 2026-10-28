#!/usr/bin/env python3
"""Measure how the upright library's second takes repeat its first.

The Helsinki 1967 library holds two takes of most notes at each layer, which
its preset alternates. Two strikes of a piano differ in the hammer's impact
noise, which is random from strike to strike, and their recorded partials
keep the strings' own pitches. Most of the library's pairs instead share the
impact noise, and nine in ten of those differ in pitch by under 0.15 cents:
the second take is the first played back a few samples later, a fraction of
a cent off. Such a take cannot hold out its first, so the split
(Tools/corpus/split-helsinki-2026-10-28.json) gives every second take the
role `repeat`, neither fitted nor scored.

For every note and layer with two takes, aligned on the lag (within
+-3000 samples) that best correlates their first 0.5 s:

  correlation  both channels' normalised correlation over that 0.5 s
  impact       the same over the first 30 ms, band-passed to 2-12 kHz
  cents        the second take's pitch against the first's, the median
               over partials 1-6, each the strongest peak near its harmonic
               from 0.2 to 2.2 s
  copy         correlation 0.9 or more and impact 0.8 or more

  python3 Tools/find_repeated_takes.py   # the measurements and a summary, as JSON
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import signal

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fit_realtime_modal as fit  # noqa: E402
import piano_analysis as pa  # noqa: E402

SEARCH = 3000


def align(x, y, sr):
    """The lag of y against x and their correlation over x's first 0.5 s."""
    n = int(.5 * sr)
    a, b = x[:n].ravel(), np.r_[np.zeros((SEARCH, 2)), y[:n + SEARCH]]
    best = (-2.0, 0)
    for lag in range(-SEARCH, SEARCH + 1):
        v = b[SEARCH + lag:SEARCH + lag + n].ravel()
        if len(v) == len(a):
            best = max(best, (float(a @ v / np.sqrt((a @ a) * (v @ v) + 1e-30)), lag))
    return best[1], best[0]


def impact(x, y, sr, lag):
    sos = signal.butter(6, [2000, 12000], 'bandpass', fs=sr, output='sos')
    n, pad = int(.03 * sr), SEARCH
    hx = signal.sosfiltfilt(sos, np.r_[np.zeros((pad, 2)), x[:n + pad]], axis=0)
    hy = signal.sosfiltfilt(sos, np.r_[np.zeros((pad, 2)), y[:n + 2 * pad]], axis=0)
    u, v = hx[pad:pad + n].ravel(), hy[pad + lag:pad + lag + n].ravel()
    return float(u @ v / np.sqrt((u @ u) * (v @ v) + 1e-30))


def cents(x, y, sr, lag, note):
    lo, hi = int(.2 * sr), int(2.2 * sr)
    if len(x) < hi or len(y) < hi + max(lag, 0):
        return None
    nfft = 1 << 22
    hz = np.fft.rfftfreq(nfft, 1 / sr)
    w = signal.windows.blackmanharris(hi - lo)
    sx = np.abs(np.fft.rfft(x[lo:hi, 0] * w, nfft))
    sy = np.abs(np.fft.rfft(y[lo + lag:hi + lag, 0] * w, nfft))
    f0, out = pa.midi_hz(note), []
    for k in range(1, 7):
        span = (hz > k * f0 * .97) & (hz < k * f0 * 1.05)
        px, py = hz[span][np.argmax(sx[span])], hz[span][np.argmax(sy[span])]
        out.append(1200 * np.log2(py / px))
    return float(np.median(out))


def main():
    argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter).parse_args()
    model = fit.MODELS['upright']
    takes = defaultdict(list)
    for item in json.loads(model['corpus'].read_text())['files']:
        if item['kind'] == 'note':
            takes[(item['midi'], item['layer'])].append(item)
    rows = []
    for (note, layer), pair in sorted(takes.items()):
        if len(pair) < 2:
            continue
        first, second = sorted(pair, key=lambda i: i['round_robin'])
        sr, x = pa.load(model['wav'] / f'{first["id"]}.wav')
        _, y = pa.load(model['wav'] / f'{second["id"]}.wav')
        lag, correlation = align(x, y, sr)
        row = {'take': second['id'], 'of': first['id'], 'lag': lag, 'correlation': round(correlation, 4),
               'impact': round(impact(x, y, sr, lag), 4), 'cents': cents(x, y, sr, lag, note)}
        row['copy'] = row['correlation'] >= .9 and row['impact'] >= .8
        rows.append(row)
    copies = [r for r in rows if r['copy']]
    summary = {'pairs': len(rows), 'copies': len(copies),
               'least_correlation': min(r['correlation'] for r in rows),
               'median_abs_cents_of_copies': float(np.median([abs(r['cents']) for r in copies if r['cents'] is not None]))}
    print(json.dumps({'summary': summary, 'pairs': rows}, indent=1))

if __name__ == '__main__':
    main()
