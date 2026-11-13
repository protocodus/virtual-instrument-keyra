#!/usr/bin/env python3
"""Which octaves the recorded grand's tuner tuned in the bass.

The stretch a tuner leaves follows from the strings' stiffness and from which
partials the octaves were heard on. This reads each Salamander pitch's first
partial and stiffness B as the benchmark measured them (the median of the
pitch's sixteen layers in out/bench/reference-cache, written by
Tools/benchmark_recordings.py), carries B in log over the keys between the
sampled pitches, tunes A4 where the recording's stands and the octave A3-A4
4:2, and chains each rule's octaves down from there on the recording's own
partials, n f sqrt(1 + B n^2). Printed for A0 to A2, rule against recording in
cents: the rms, the mean and each pitch. The last rule is PianoModel.cpp's.

  python3 Tools/measure_tuner_octaves.py [--cache out/bench/reference-cache]
"""
import argparse
import re
from pathlib import Path

import numpy as np

SEMITONE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def key_of(name):
    return 12 * (int(name[-1]) + 1) + SEMITONE[name[0]] + (name[1:2] == '#') - 21


def nominal(key):
    return 440 * 2 ** ((key - 48) / 12)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--cache', type=Path, default=Path(__file__).resolve().parents[1] / 'out/bench/reference-cache')
    args = ap.parse_args()
    read = {}
    for path in sorted(args.cache.glob('*.npz')):
        m = re.match(r'([A-G]#?\d)v\d+-', path.name)
        if m:
            z = np.load(path, allow_pickle=True)
            read.setdefault(key_of(m.group(1)), []).append((float(z['f1']), float(z['B'])))
    if 48 not in read or 36 not in read:
        raise SystemExit(f'no A3 and A4 in {args.cache}: run Tools/benchmark_recordings.py first')
    keys = sorted(read)
    stretch = {k: 1200 * np.log2(np.median([f for f, _ in read[k]]) / nominal(k)) for k in keys}
    B = np.exp(np.interp(np.arange(88), keys, [np.log(np.median([b for _, b in read[k]])) for k in keys]))

    def partial(key, n):
        return n * np.sqrt(1 + B[key] * n * n)

    def tuned(octave_type):
        """octave_type(key): the lower note's partial the octave is heard on, 4 for 4:2; fractions blend."""
        pitch = np.zeros(88)
        pitch[48] = nominal(48) * 2 ** (stretch[48] / 1200) / partial(48, 1)
        pitch[36] = pitch[48] * partial(48, 2) / partial(36, 4)
        # The octave A3-A4 in equal steps between its ends, as the model's.
        for i in range(37, 48):
            pitch[i] = pitch[36] * (pitch[48] / pitch[36]) ** ((i - 36) / 12)
        for i in range(35, -1, -1):
            n = octave_type(i)
            lower = 2 * int(n // 2)
            a = pitch[i + 12] * partial(i + 12, lower // 2) / partial(i, lower)
            b = pitch[i + 12] * partial(i + 12, lower // 2 + 1) / partial(i, lower + 2)
            pitch[i] = a * (b / a) ** ((n - lower) / 2)
        return {k: 1200 * np.log2(pitch[k] * partial(k, 1) / nominal(k)) for k in range(49)}

    bass = [k for k in keys if k <= 24]
    print('rule                         rms   mean  ' + ' '.join(f'{k:5d}' for k in bass) + '   (key, A0 = 0)')
    for name, rule in (('4:2', lambda i: 4), ('6:3 (through 2.12.0)', lambda i: 6), ('8:4', lambda i: 8), ('10:5', lambda i: 10),
                       ('4:2 at A3, 6:3 A2, 8:4 A1', lambda i: min(8., 4 + (36 - i) / 6))):
        s = tuned(rule)
        d = np.array([s[k] - stretch[k] for k in bass])
        print(f'{name:27s} {np.sqrt(np.mean(d * d)):5.2f} {np.mean(d):+6.2f}  ' + ' '.join(f'{x:+5.1f}' for x in d))


if __name__ == '__main__':
    main()
