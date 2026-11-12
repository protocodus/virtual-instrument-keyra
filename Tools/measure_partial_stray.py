#!/usr/bin/env python3
"""How far a note's partials stray from the ideal stiff string, and how they
beat, in the Salamander grand and in a renderer: the evidence for the wound
strings' stray in PianoModel.cpp (KeyData::stray).

Protocol. Every third key from A0 to C6, layers 8 and 13 (velocities 61 and
101 for the renderer, struck from silence, 8.5 s at gain .07), the two
channels' mean.

Stray. From 0.3 to 3 s, a Hann-windowed spectrum zero-padded to 2^20
points. The partials are found one by one from the first: each is the
spectrum's peak within 0.3 f0 of where the stiff-string law n F sqrt(1 + B n^2),
fitted to the partials already found (from the fourth on), puts it,
refined by a parabola through the peak's three bins, and kept when it
stands within 40 dB of the spectrum's peak; the search stops at 5 kHz or the
30th partial. F and B are then fitted to the kept partials in cents, and the
note's stray is the rms of their residuals, cents.

Beats, on the kept partials below 3 kHz twice over: those within 20 dB of
the loudest, which carry the note, and all of them. From 0.3 to 8 s, each
is shifted to 0 Hz, low-passed at 6 Hz (4th-order Butterworth, both ways),
and its level in dB, from 0.1 s in to 0.1 s before the end, is read every
5 ms. A cubic in time
takes out the decay; the rms of what is left is the partial's swing, dB,
and the peak of its spectrum from 0.15 to 6 Hz its swing rate. A unison whose
strings stand one ratio apart at every partial beats at a rate in proportion
to the partial's frequency, so each partial's rate lies on the line through
its neighbours'. The note's irregularity is the median, over the partials
between two others, of how far its rate lies off that line, over the median
rate; its swing the median swing.

Per register, the tables give the median over notes and layers. Nothing is
fitted to a note.

  python3 -B Tools/measure_partial_stray.py --renderer build-dsp/keyra_render \\
      [--salamander out/salamander/wav] [--jobs 4]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import numpy as np
import soundfile as sf
from scipy.optimize import least_squares
from scipy.signal import butter, sosfiltfilt

ROOT = Path(__file__).resolve().parent.parent
NOTES = range(21, 85, 3)
LAYERS = {8: 61, 13: 101}
REGISTERS = (('A0-B2', 21, 47), ('C3-B4', 48, 71), ('C5-C6', 72, 84))
NAMES = 'A A# B C C# D D# E F F# G G#'.split()


def name(note):
    return f'{NAMES[(note - 21) % 12]}{(note - 12) // 12}'


def partials(x, sr, note, top=30, within=40):
    seg = x[int(.3 * sr):int(3 * sr)]
    size = 1 << 20
    spectrum = np.abs(np.fft.rfft(seg * np.hanning(len(seg)), size))
    hertz = np.fft.rfftfreq(size, 1 / sr)
    f0 = 440 * 2 ** ((note - 69) / 12)
    loudest = spectrum.max()
    found, F, B = [], f0, 0.
    for n in range(1, top + 1):
        if len(found) >= 4:
            q = np.array(found)
            fit = least_squares(lambda p: q[:, 0] * p[0] * np.sqrt(1 + max(p[1], 0) * q[:, 0] ** 2) - q[:, 1], [F, 1e-4])
            F, B = fit.x[0], max(fit.x[1], 0)
        want = n * F * np.sqrt(1 + B * n * n)
        if want > 5000:
            break
        lo, hi = np.searchsorted(hertz, [want - .3 * f0, want + .3 * f0])
        i = lo + int(np.argmax(spectrum[lo:hi]))
        if 20 * np.log10(spectrum[i] / loudest) < -within:
            continue
        a, b, c = np.log(spectrum[i - 1:i + 2])
        found.append((n, hertz[i] + .5 * (a - c) / (a - 2 * b + c) * (hertz[1] - hertz[0]), 20 * np.log10(spectrum[i] / loudest)))
    return np.array(found)


def stray(q, note):
    f0 = 440 * 2 ** ((note - 69) / 12)
    fit = least_squares(lambda p: 1200 * np.log2(q[:, 0] * p[0] * np.sqrt(1 + p[1] * q[:, 0] ** 2) / q[:, 1]), [f0, 1e-4])
    return float(np.sqrt(np.mean(fit.fun ** 2)))


def beats(x, sr, q, within):
    q = q[(q[:, 1] < 3000) & (q[:, 2] >= -within)]
    seg = x[int(.3 * sr):int(min(8, len(x) / sr - .2) * sr)]
    t = np.arange(len(seg)) / sr
    sos = butter(4, 6, fs=sr, output='sos')
    keep = slice(int(.1 * sr), len(seg) - int(.1 * sr), int(.005 * sr))
    swing, rate = [], []
    for f in q[:, 1]:
        z = seg * np.exp(-2j * np.pi * f * t)
        level = 20 * np.log10(np.abs(sosfiltfilt(sos, z.real) + 1j * sosfiltfilt(sos, z.imag))[keep] + 1e-12)
        tt = t[keep]
        r = level - np.polyval(np.polyfit(tt, level, 3), tt)
        spectrum = np.abs(np.fft.rfft(r * np.hanning(len(r)), 8 * len(r)))
        hertz = np.fft.rfftfreq(8 * len(r), tt[1] - tt[0])
        band = (hertz >= .15) & (hertz <= 6)
        swing.append(r.std())
        rate.append(hertz[band][np.argmax(spectrum[band])])
    rate = np.array(rate)
    off = np.abs(rate[1:-1] - (rate[:-2] + rate[2:]) / 2)
    return float(np.median(off) / np.median(rate)) if len(rate) > 3 else np.nan, float(np.median(swing))


def analyse(path, note):
    x, sr = sf.read(path)
    x = x.mean(axis=1) if x.ndim > 1 else x
    q = partials(x, sr, note)
    return (stray(q, note),) + beats(x, sr, q, 20) + beats(x, sr, q, 40)


def measure(job):
    source, note, layer = job
    if source != 'render':
        return analyse(os.path.join(source, f'{name(note)}v{layer}.wav'), note)
    with tempfile.TemporaryDirectory() as tmp:
        events = os.path.join(tmp, 'events')
        with open(events, 'w') as f:
            f.write(f'0.05 on {note} {LAYERS[layer]}\n')
        wav = os.path.join(tmp, 'render.wav')
        subprocess.run([measure.renderer, '--events', events, '--output', wav, '--duration', '8.5', '--gain', '.07'],
                       check=True, stdout=subprocess.DEVNULL)
        return analyse(wav, note)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('--renderer', required=True)
    ap.add_argument('--salamander', default=str(ROOT / 'out/salamander/wav'))
    ap.add_argument('--jobs', type=int, default=4)
    a = ap.parse_args()
    measure.renderer = a.renderer
    jobs = [(n, layer) for n in NOTES for layer in LAYERS]
    rows = {}
    with ProcessPoolExecutor(a.jobs, initializer=setattr, initargs=(measure, 'renderer', a.renderer)) as ex:
        for source, label in ((a.salamander, 'Salamander'), ('render', 'render')):
            rows[label] = list(zip(jobs, ex.map(measure, [(source, n, layer) for n, layer in jobs])))
    for column, title in enumerate(('stray, cents', 'beat irregularity, partials within 20 dB', 'beat swing within 20 dB, dB',
                                    'beat irregularity, all partials', 'beat swing of all partials, dB')):
        print(f'\n{title}\n\n| source | ' + ' | '.join(r[0] for r in REGISTERS) + ' |')
        print('|---|' + '---:|' * len(REGISTERS))
        for label, values in rows.items():
            # A note with fewer than four partials to compare has no irregularity.
            cells = [[v[column] for (n, _), v in values if lo <= n <= hi and np.isfinite(v[column])] for _, lo, hi in REGISTERS]
            print(f'| {label} | ' + ' | '.join(f'{np.median(c):.2f}' if c else '-' for c in cells) + ' |')


if __name__ == '__main__':
    main()
