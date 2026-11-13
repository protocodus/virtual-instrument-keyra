#!/usr/bin/env python3
"""How alike a microphone pair's two channels are, octave by octave, in the
Salamander grand and in a renderer: the evidence for the phase a pair hears
each soundboard mode in (PianoModel.cpp, designBoard).

Protocol. Every sampled pitch of the Salamander from A0 to C8 (30, a minor
third apart) at layers 7, 9, 11, 13 and 15 (velocities 54, 69, 85, 101 and
117 for the renderer, struck from silence, 1.6 s at gain .07, each pair
alone). The note begins where its power, averaged over 1 ms, first stands
within 45 dB of its highest; the measure is taken from 0.05 to 0.85 s after
that under a Hann window.

In each octave (88-177, 177-354, 354-707, 707-1414 and 1414-2828 Hz) the two
channels' likeness is the real part of their cross-spectrum summed over the
octave, over the root of the product of their energies there: 1 when they
move together, -1 when one is the other inverted, 0 when a mono sum neither
gains nor loses. An octave counts for a note where it holds more than -40 dB
of the note's energy above 20 Hz. The table gives the mean over the notes
that count and its standard error, then the same likeness over everything
above 20 Hz, c: a mono sum of such a note holds 10 log10((1 + c) / 2) dB of
the two channels' mean energy, 0 when they are the same and -3 when they are
unrelated.

The recording is one spaced pair close over the strings, so it stands beside
the renderer's close pair; the other pairs have no recording beside them
here. Nothing is fitted to a note.

  python3 -B Tools/measure_pair_image.py --renderer build-dsp/keyra_render \\
      [--salamander out/salamander/wav] [--jobs 4] [-- --body upright ...]
"""
from __future__ import annotations

import argparse
import subprocess
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
from scipy.io import wavfile

ROOT = Path(__file__).resolve().parents[1]
PITCHES = [f'{p}{o}' for o in range(8) for p in ('C', 'D#', 'F#', 'A')][3:] + ['C8']
LAYER_VELOCITY = [14, 31, 36, 40, 45, 49, 54, 61, 69, 77, 85, 93, 101, 109, 117, 124]
LAYERS = [7, 9, 11, 13, 15]
BANDS = [(88, 177), (177, 354), (354, 707), (707, 1414), (1414, 2828)]
PAIRS = [('close', '1,0,0,0'), ('xy', '0,1,0,0'), ('live', '0,0,1,0'), ('distant', '0,0,0,1')]


def midi(name):
    return 12 * (int(name[-1]) + 1) + {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}[name[0]] + (name[1:2] == '#')


def load(path):
    sr, x = wavfile.read(str(path))
    return sr, x.astype(np.float64) / (2.0 ** (8 * x.dtype.itemsize - 1) if x.dtype.kind == 'i' else 1)


def likeness(sr, x):
    power = np.mean(x * x, axis=1)
    k = max(3, int(.001 * sr))
    env = np.convolve(power, np.ones(k) / k, mode='same')
    start = int(np.flatnonzero(env > np.max(env[:int(1.5 * sr)]) * 10 ** -4.5)[0])
    seg = x[start + int(.05 * sr):start + int(.85 * sr)]
    spectrum = np.fft.rfft(seg * np.hanning(len(seg))[:, None], axis=0)
    f = np.fft.rfftfreq(len(seg), 1 / sr)
    left, right = spectrum[:, 0], spectrum[:, 1]

    def over(mask):
        el, er = np.sum(np.abs(left[mask]) ** 2), np.sum(np.abs(right[mask]) ** 2)
        return float(np.real(np.sum(left[mask] * np.conj(right[mask]))) / np.sqrt(el * er)), el + er

    whole, energy = over(f >= 20)
    octaves = []
    for lo, hi in BANDS:
        alike, held = over((f >= lo) & (f < hi))
        octaves.append(alike if held > 1e-4 * energy else np.nan)
    return octaves + [whole]


def recorded(args):
    corpus, pitch, layer = args
    return likeness(*load(Path(corpus) / f'{pitch}v{layer}.wav'))


def rendered(args):
    renderer, extra, mics, pitch, layer = args
    with tempfile.TemporaryDirectory(prefix='keyra-image-') as tmp:
        events, wav = Path(tmp) / 'note.events', Path(tmp) / 'note.wav'
        events.write_text(f'0.05 on {midi(pitch)} {LAYER_VELOCITY[layer - 1]}\n')
        subprocess.run([renderer, '--events', str(events), '--output', str(wav), '--duration', '1.6', '--gain', '.07',
                        '--mics', mics] + extra, check=True, stdout=subprocess.DEVNULL)
        return likeness(*load(wav))


def row(label, notes):
    notes = np.array(notes)
    cells = []
    for i in range(len(BANDS)):
        held = notes[:, i][~np.isnan(notes[:, i])]
        cells.append(f'{held.mean():6.2f} +-{held.std() / np.sqrt(len(held)):5.2f}')
    return f'{label:18s}' + '  '.join(cells) + f'  {notes[:, -1].mean():8.2f}'


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('--renderer', required=True)
    p.add_argument('--salamander', default=str(ROOT / 'out/salamander/wav'))
    p.add_argument('--jobs', type=int, default=4)
    p.add_argument('renderer_args', nargs=argparse.REMAINDER, help='after --: extra keyra_render options')
    a = p.parse_args()
    extra = [x for x in a.renderer_args if x != '--']
    notes = [(pitch, layer) for pitch in PITCHES for layer in LAYERS]
    print(f'{"":18s}' + '  '.join(f'{f"{lo}-{hi} Hz":>13s}' for lo, hi in BANDS) + '     whole')
    with ProcessPoolExecutor(a.jobs) as pool:
        print(row('recording', list(pool.map(recorded, [(a.salamander, *n) for n in notes]))), flush=True)
        for name, mics in PAIRS:
            print(row(name, list(pool.map(rendered, [(a.renderer, extra, mics, *n) for n in notes]))), flush=True)


if __name__ == '__main__':
    main()
