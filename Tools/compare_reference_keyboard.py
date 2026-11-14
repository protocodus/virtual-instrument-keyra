#!/usr/bin/env python3
"""Where a Keyra piano stands against reference pianos played key by key.

The references are bounces of one score: each of the 88 keys alone, held
3 s, 4 s apart from A0 at 0 s, at velocities 40, 80 and 120
(<dir>/v040/<sub>/<name>.wav and so on). They are the owner's renders of
other instruments, read from outside the checkout and never committed; they
are a comparison, not a measurement of a real piano, and nothing is fitted
to them here. Keyra plays each key the same way through its renderer.

Per key and velocity, measured as Tools/survey_keyboard.py measures them
where the two share a measure:

- level: dB, mean square 50 to 750 ms after the onset, less that piano's
  median over all keys at velocity 80 (so each piano's own gain drops out);
- bright: octaves, the power-weighted mean of log2(f / f1) from 0.7 f1 up
  over the same window;
- fall: dB/s the 50 ms envelope falls from 0.1 to 0.6 s;
- decay: dB/s, a Theil-Sen line through that envelope from 0.6 to 2.8 s;
- rise: ms, 10 to 90 % of the 5 ms envelope's peak in the first 150 ms;
- release: dB the level has fallen 150 to 350 ms after the key is let go,
  against its last 200 ms held;
- tuning: cents, the first partial against equal temperament, 0.3 to 2.8 s;
- stiff: the inharmonicity B fitted to the partials found, times 1e4.

Per register the table gives the references' median and their range, each
renderer's median, and how far that lies outside the references' range
(0 inside it). Three references are a small sample: their range is the
ground the comparison stands on, not a tolerance.

  python3 Tools/compare_reference_keyboard.py --references <dir> --sub "Bounce uprights" \\
      --renderer 2.13.1=old/keyra_render --renderer candidate=build-dsp/keyra_render \\
      --model upright [--jobs 4] [--json OUT]
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

VELOCITIES = (40, 80, 120)
MEASURES = ('level', 'bright', 'fall', 'decay', 'rise', 'release', 'tuning', 'stiff')
REGISTERS = (('A0-B1', 21, 35), ('C2-B2', 36, 47), ('C3-B3', 48, 59), ('C4-B4', 60, 71), ('C5-B5', 72, 83),
             ('C6-B6', 84, 95), ('C7-C8', 96, 108))
HELD, APART = 3.0, 4.0


def partials(mono, sr, f1):
    """The first partial (Hz) and B from the peaks near k f1 sqrt(1 + B k^2), 0.3 to 2.8 s."""
    seg = mono[int(.3 * sr):int(2.8 * sr)]
    n = 1 << 20
    X = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), n))
    hz = sr / n
    top = X[int(.7 * f1 / hz):].max()
    found, F, B = [], f1, 0.0
    for k in range(1, 41):
        guess = k * F * np.sqrt(1 + B * k * k)
        if guess > min(10000, .45 * sr):
            break
        lo, hi = int((guess - .3 * f1) / hz), int((guess + .3 * f1) / hz)
        i = lo + int(np.argmax(X[lo:hi]))
        if X[i] < top * 10 ** (-50 / 20):
            continue
        a, b, c = X[i - 1], X[i], X[i + 1]
        found.append((k, (i + .5 * (a - c) / (a - 2 * b + c)) * hz))
        if len(found) >= 4:
            ks, fs = np.array(found).T
            sol = np.linalg.lstsq(np.stack([np.ones_like(ks), ks * ks], 1), (fs / ks) ** 2, rcond=None)[0]
            if sol[0] > 0:
                F, B = np.sqrt(sol[0]), max(0, sol[1] / sol[0])
    first = next((f for k, f in found if k == 1), np.nan)
    return first, (B if len(found) >= 4 else np.nan)


def measure(x, sr, note):
    """One key's measures from its stereo take, which starts shortly before the blow."""
    x = signal.sosfiltfilt(signal.butter(2, 20, 'highpass', fs=sr, output='sos'), x, axis=0)
    s = pa.onset(x, sr)
    e = x[s + int(.05 * sr):s + int(.75 * sr)]
    f1 = pa.midi_hz(note)
    f, p = signal.welch(e.mean(axis=1), sr, nperseg=8192)
    k = f > .7 * f1
    power = np.mean(x * x, axis=1)
    env = ndimage.uniform_filter1d(power, int(.05 * sr))[s:]
    t = np.arange(len(env)) / sr
    db = lambda a, b: 10 * np.log10(np.mean(power[s + int(a * sr):s + int(b * sr)]) + 1e-30)
    sel = (t >= .6) & (t <= HELD - .2)
    decay = stats.theilslopes(10 * np.log10(env[sel][::480] + 1e-30), t[sel][::480])[0]
    env5 = np.sqrt(np.maximum(ndimage.uniform_filter1d(power, int(.005 * sr)), 0))[s:s + int(.15 * sr)]
    peak = env5.max()
    rise = (np.flatnonzero(env5 >= .9 * peak)[0] - np.flatnonzero(env5 >= .1 * peak)[0]) / sr * 1000
    first, stiff = partials(x[s:].mean(axis=1), sr, f1)
    return dict(note=note, level=db(.05, .75), bright=float(np.sum(p[k] * np.log2(f[k] / f1)) / np.sum(p[k])),
                fall=(db(.075, .125) - db(.575, .625)) / .5, decay=float(-decay), rise=rise,
                release=db(HELD - .2, HELD) - db(HELD + .15, HELD + .35),
                tuning=1200 * np.log2(first / f1), stiff=stiff * 1e4)


def reference(job):
    path, velocity = job
    sr, x = pa.load(path)
    rows = []
    for i, note in enumerate(range(21, 109)):
        a = int((i * APART - .1) * sr)
        take = x[max(0, a):a + int(APART * sr)]
        if a < 0:
            take = np.concatenate([np.zeros((-a, x.shape[1])), take])
        rows.append(dict(measure(take, sr, note), velocity=velocity))
    return rows


def rendered(job):
    renderer, model, note, velocity = job
    with tempfile.TemporaryDirectory() as tmp:
        events = os.path.join(tmp, 'events')
        with open(events, 'w') as f:
            f.write(f'0.1 on {note} {velocity}\n{.1 + HELD} off {note} 0\n')
        wav = os.path.join(tmp, 'render.wav')
        subprocess.run([renderer, '--events', events, '--output', wav, '--duration', str(APART), '--body', model],
                       check=True, stdout=subprocess.DEVNULL)
        sr, x = pa.load(wav)
    return dict(measure(x, sr, note), velocity=velocity)


def relative(rows):
    """Levels against the piano's own median at velocity 80."""
    middle = np.median([r['level'] for r in rows if r['velocity'] == 80])
    return [dict(r, level=r['level'] - middle) for r in rows]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--references', required=True, help='the folder holding v040, v080 and v120')
    ap.add_argument('--sub', default='', help='the subfolder of each velocity folder that holds the bounces')
    ap.add_argument('--renderer', action='append', required=True, help='NAME=PATH, once per renderer')
    ap.add_argument('--model', default='upright')
    ap.add_argument('--jobs', type=int, default=3)
    ap.add_argument('--json', help='write every key\'s measures here')
    a = ap.parse_args()
    names = sorted(p.stem for p in (Path(a.references) / 'v080' / a.sub).glob('*.wav'))
    if not names:
        sys.exit('no reference bounces found')
    with ProcessPoolExecutor(a.jobs) as ex:
        refs = {}
        for name in names:
            jobs = [(Path(a.references) / f'v{v:03d}' / a.sub / f'{name}.wav', v) for v in VELOCITIES]
            refs[name] = relative([r for rows in ex.map(reference, jobs) for r in rows])
        ours = {}
        for item in a.renderer:
            name, path = item.split('=', 1)
            jobs = [(path, a.model, n, v) for v in VELOCITIES for n in range(21, 109)]
            ours[name] = relative(list(ex.map(rendered, jobs, chunksize=4)))

    def median(rows, velocity, lo, hi, m):
        v = [r[m] for r in rows if r['velocity'] == velocity and lo <= r['note'] <= hi and np.isfinite(r[m])]
        return float(np.median(v)) if v else np.nan

    outside = {name: {m: [] for m in MEASURES} for name in ours}
    for m in MEASURES:
        print(f'\n{m}')
        print('| velocity | register | references (range) | ' + ' | '.join(f'{n} (outside)' for n in ours) + ' |')
        print('|---:|---|---:|' + '---:|' * len(ours))
        for v in VELOCITIES:
            for label, lo, hi in REGISTERS:
                r = [median(refs[n], v, lo, hi, m) for n in names]
                cells = []
                for name, rows in ours.items():
                    x = median(rows, v, lo, hi, m)
                    d = x - np.nanmax(r) if x > np.nanmax(r) else x - np.nanmin(r) if x < np.nanmin(r) else 0.
                    outside[name][m].append(d)
                    cells.append(f'{x:.2f} ({d:+.2f})')
                print(f'| {v} | {label} | {np.nanmedian(r):.2f} ({np.nanmin(r):.2f} to {np.nanmax(r):.2f}) | '
                      + ' | '.join(cells) + ' |')
    print('\nmean distance outside the references\' range, over registers and velocities')
    print('| renderer | ' + ' | '.join(MEASURES) + ' |')
    print('|---|' + '---:|' * len(MEASURES))
    for name in ours:
        print(f'| {name} | ' + ' | '.join(f'{np.nanmean(np.abs(outside[name][m])):.2f}' for m in MEASURES) + ' |')
    if a.json:
        with open(a.json, 'w') as f:
            json.dump(dict(references=refs, renderers=ours), f, indent=1)


if __name__ == '__main__':
    main()
