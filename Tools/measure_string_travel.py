#!/usr/bin/env python3
"""Measure when a low note's sound comes in, band by band, in the recordings
and in the engine's renders: the evidence for strikeTravel in KeyraEngine.cpp
(Docs/research/string-travel-2026-11-09.md).

Each train and dev take from A0 to B3 of a piano's locked split
(fit_realtime_modal.MODELS), and its render at its layer's velocity as
benchmark_recordings renders it (LEAD, MEASURE), are read from their
benchmark onset (piano_analysis.onset). In each of three bands, 20 to 400 Hz,
400 Hz to 2 kHz and over 2 kHz, through the same causal fourth-order
Butterworth filter on recording and render, a band comes in where the 1 ms
running mean of the channels' power first stands within 20 dB of its highest
over the first 150 ms. A band whose sound starts before the onset comes in at
it. Per register, the table gives the median over the takes of the band under
400 Hz less the band over 2 kHz, in ms, for the recordings and for each
renderer, and the time the strike's wave takes to run seven eighths of the
string to the bridge, (7/8) / (2 f), at the median take's pitch. Sealed takes
are never read, and nothing is fitted.

  python3 -B Tools/measure_string_travel.py --renderer 0.4.28=old/keyra_render \\
      --renderer 0.4.29=build/keyra_render [--model grand] [--jobs 3]
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
from scipy import ndimage, signal

import benchmark_recordings as br
import fit_realtime_modal as fit
import piano_analysis as pa

BANDS = (('lo', 20, 400), ('mid', 400, 2000), ('hi', 2000, None))
REGISTERS = ((21, 26, 'A0–C♯1'), (27, 32, 'D♯1–G♯1'), (33, 38, 'A1–D2'),
             (39, 44, 'D♯2–G♯2'), (45, 50, 'A2–D3'), (51, 59, 'D♯3–B3'))
NAMES = {'grand': 'Kakegawa grand', 'upright': 'upright', 'kawai': 'Hamamatsu grand',
         'hamburg': 'Hamburg grand', 'newyork': 'New York grand'}


def arrivals(x: np.ndarray, sr: int) -> dict[str, float]:
    """Seconds after the onset at which each band comes in."""
    start = pa.onset(x, sr)
    out = {}
    for name, low, high in BANDS:
        sos = signal.butter(4, [low, high] if high else low, 'bandpass' if high else 'highpass',
                            fs=sr, output='sos')
        y = signal.sosfilt(sos, x, axis=0)
        power = ndimage.uniform_filter1d(np.mean(y * y, axis=1), max(2, int(.001 * sr)), mode='constant')
        half = int(.0005 * sr)
        power = np.concatenate([power[half:], np.zeros(half)])
        window = power[start:start + int(.15 * sr)]
        out[name] = int(np.flatnonzero(window >= .01 * window.max())[0]) / sr
    return out


def measure(job):
    case, note, velocity, renderers, extra, wav_dir = job
    sr, x = pa.load(Path(wav_dir) / f'{case}.wav')
    row = {'case': case, 'note': note, 'recording': arrivals(x, sr)}
    with tempfile.TemporaryDirectory(prefix='keyra-travel-') as tmp:
        events = Path(tmp) / 'note.events'
        events.write_text(f'{br.LEAD} on {note} {velocity}\n')
        for label, renderer in renderers:
            wav = Path(tmp) / 'render.wav'
            subprocess.run([renderer, '--events', str(events), '--output', str(wav), '--duration', '1']
                           + br.MEASURE + extra, check=True, stdout=subprocess.DEVNULL)
            rate, y = pa.load(wav)
            row[label] = arrivals(y, rate)
    return row


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--renderer', action='append', required=True, metavar='LABEL=PATH')
    parser.add_argument('--model', action='append', choices=list(NAMES))
    parser.add_argument('--jobs', type=int, default=3)
    args = parser.parse_args()
    renderers = [tuple(r.split('=', 1)) for r in args.renderer]
    labels = [label for label, _ in renderers]
    print('| piano | keys | takes | recording | ' + ' | '.join(labels) + ' | the wave |')
    print('|---|---|---|---|' + '---|' * len(labels) + '---|')
    for model in args.model or list(NAMES):
        m = fit.MODELS[model]
        roles = json.loads(m['split'].read_text())['cases']
        items = {i['id']: i for i in json.loads(m['corpus'].read_text())['files']}
        extra = ['--model', model] if model != 'grand' else []
        jobs = [(case, items[case]['midi'], fit.layer_velocity(items[case]), renderers, extra, str(m['wav']))
                for case, role in roles.items()
                if role in ('train', 'dev') and items[case]['kind'] == 'note' and items[case]['midi'] <= 59]
        with ProcessPoolExecutor(args.jobs) as pool:
            rows = list(pool.map(measure, jobs, chunksize=2))
        first = True
        for low, high, name in REGISTERS:
            group = [r for r in rows if low <= r['note'] <= high]
            if not group:
                continue
            lag = lambda side: f"{1000 * np.median([r[side]['lo'] - r[side]['hi'] for r in group]):.1f}"
            wave = 1000 * np.median([(7 / 8) / (2 * 440 * 2 ** ((r['note'] - 69) / 12)) for r in group])
            cells = [NAMES[model] if first else '', name, str(len(group)), lag('recording')] + [lag(l) for l in labels]
            print('| ' + ' | '.join(cells) + f' | {wave:.1f} |', flush=True)
            first = False
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
