#!/usr/bin/env python3
"""Fit the tube microphone's perspective, Keyra's Mic control, from the
Helsinki 1967 recordings into Source/DSP/MeasuredMicData.h.

The library took every strike with two microphones at once: the Blumlein
ribbon pair in player position close to the hammers, which Keyra's upright is
fitted from, and a mono tube condenser at shin height from the left, further
from the hammers (Tools/corpus/helsinki-1967-tube.json). On each strike the
two onsets sit a median 0.26 ms apart, and where a note's two round robins
differ in level the two microphones show the same difference (correlation
0.98, against -0.10 with the tube's differences shuffled across notes), so
the tube's take is the ribbon's strike heard from elsewhere and the
difference between them is the microphone and its place, not the playing.

Protocol: on each note take of the split's train role
(Tools/corpus/split-helsinki-2026-10-28.json), from 50 ms to 1 s after the
onset (where the ribbon pair's mid, (L+R)/2, first reaches 2 % of its peak
envelope), per third-octave band from 39 Hz to 8 kHz, the tube's power over
the mid's, kept where each microphone stands 15 dB over its own floor (its
quietest half second before the take's last tenth). The response is each
band's median over the takes that keep it, at least 10. The dev takes'
medians (at least 5 per band) score it and are never fitted; the sealed
takes and the repeats are not read. Over 1 to 3 s the ratio moves a median
-0.3 dB from the first second's, and register and velocity move it little
against the bands' spread, so one steady response describes the tube: no
room the ribbon does not also hear, and no change with the note.

The response is realized as a low and a high shelf and SECTIONS peaking
sections (the RBJ cookbook's, which the engine designs at its own rate), the
peaking sections inside the measured bands and the shelves holding the level
of the bands at either end beyond them, least squares on
the band medians in dB, each band weighted by the root of its takes, with a
free gain: the recordings' levels are each microphone's preamp's, so the
engine sets the tube's level by its own calibration on Reason's meter
(Tools/KeyraLevels.cpp) and takes only the shape.

  python3 Tools/decode_helsinki.py --library <path> [--tube]  # both microphones' takes
  python3 Tools/fit_mic.py                                    # regenerate the header and provenance
  python3 Tools/fit_mic.py --check                            # verify both reproduce exactly
  python3 Tools/fit_mic.py --sections                         # dev error by section count
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path

# One BLAS thread per worker, so the floating-point results are the same on
# any machine.
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import numpy as np
import scipy.io.wavfile as wavfile
import scipy.optimize as optimize

ROOT = Path(__file__).resolve().parents[1]
RIBBON = ROOT / 'Tools/corpus/helsinki-1967.json'
TUBE = ROOT / 'Tools/corpus/helsinki-1967-tube.json'
SPLIT = ROOT / 'Tools/corpus/split-helsinki-2026-10-28.json'
WAV = {'ribbon': ROOT / 'out/helsinki/wav', 'tube': ROOT / 'out/helsinki/tube'}
HEADER = ROOT / 'Source/DSP/MeasuredMicData.h'
METADATA = ROOT / 'Docs/research/mic-tube-fit-2026-10-30.json'

RATE = 48000
CENTRES = 1000 * 2.0 ** (np.arange(-14, 10) / 3)  # 39.4 Hz .. 7.94 kHz
EDGES = np.c_[CENTRES * 2 ** (-1 / 6), CENTRES * 2 ** (1 / 6)]
WINDOW = (.05, 1.)
FRAME, HOP = 4096, 4800
OVER_FLOOR_DB = 15
MIN_TRAIN, MIN_DEV = 10, 5
# The fewest peaking sections whose dev error is within 0.1 dB of the best of
# two to eight (--sections): 1.83, 1.67, 1.73, 1.51, 1.54, 1.56 and 1.52 dB.
SECTIONS = 5


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> np.ndarray:
    rate, x = wavfile.read(path)
    if rate != RATE:
        raise SystemExit(f'{path}: {rate} Hz, not {RATE}')
    x = x.astype(np.float64) / 2 ** 31
    return x if x.ndim == 2 else x[:, None]


def band_power(frames: np.ndarray) -> np.ndarray:
    """Each Hann-windowed frame's power per band."""
    spectrum = np.abs(np.fft.rfft(frames * np.hanning(FRAME), axis=-1)) ** 2
    f = np.fft.rfftfreq(FRAME, 1 / RATE)
    member = np.stack([(f >= lo) & (f < hi) for lo, hi in EDGES], 1).astype(np.float64)
    return spectrum @ member


def measure(take: dict) -> dict:
    """One take's tube-over-mid ratio per band (NaN where either microphone
    is within OVER_FLOOR_DB of its floor)."""
    ribbon, tube = load(WAV['ribbon'] / f'{take["id"]}.wav'), load(WAV['tube'] / f'{take["id"]}.wav')[:, 0]
    n = min(len(ribbon), len(tube))
    mid, tube = ribbon[:n].mean(1), tube[:n]
    envelope = np.convolve(np.abs(mid), np.ones(48) / 48, 'same')
    onset = int(np.argmax(envelope > .02 * envelope.max()))
    start, stop = onset + int(WINDOW[0] * RATE), min(n, onset + int(WINDOW[1] * RATE))
    windows = np.lib.stride_tricks.sliding_window_view

    def body(x):
        return band_power(windows(x[start:stop], FRAME)[::FRAME // 2]).mean(0)

    def floor(x):
        frames = band_power(windows(x[:int(.9 * n)], FRAME)[::HOP])
        half_second = windows(frames, 5, axis=0).mean(-1)
        return half_second.min(0)

    pm, pt = body(mid), body(tube)
    kept = (pm > floor(mid) * 10 ** (OVER_FLOOR_DB / 10)) & (pt > floor(tube) * 10 ** (OVER_FLOOR_DB / 10))
    return {'id': take['id'], 'midi': take['midi'], 'layer': take['layer'],
            'ratio_db': np.where(kept, 10 * np.log10(np.maximum(pt, 1e-300) / np.maximum(pm, 1e-300)), np.nan)}


def medians(rows: list, least: int):
    ratio = np.array([r['ratio_db'] for r in rows])
    count = np.isfinite(ratio).sum(0)
    median = np.array([np.median(ratio[np.isfinite(ratio[:, i]), i]) if count[i] >= least else np.nan
                       for i in range(len(CENTRES))])
    return median, count


def coefficients(kind: str, hz: float, q: float, gain_db: float, rate: float = RATE):
    """The RBJ cookbook's peaking, low-shelf or high-shelf biquad, normalised
    (b, a), as KeyraEngine.cpp designs it."""
    a_ = 10 ** (gain_db / 40)
    w = 2 * np.pi * hz / rate
    cos, sin = np.cos(w), np.sin(w)
    alpha = sin / (2 * q)
    root = 2 * np.sqrt(a_) * alpha
    if kind == 'peak':
        b = [1 + alpha * a_, -2 * cos, 1 - alpha * a_]
        a = [1 + alpha / a_, -2 * cos, 1 - alpha / a_]
    elif kind == 'low':
        b = [a_ * ((a_ + 1) - (a_ - 1) * cos + root), 2 * a_ * ((a_ - 1) - (a_ + 1) * cos),
             a_ * ((a_ + 1) - (a_ - 1) * cos - root)]
        a = [(a_ + 1) + (a_ - 1) * cos + root, -2 * ((a_ - 1) + (a_ + 1) * cos), (a_ + 1) + (a_ - 1) * cos - root]
    else:
        b = [a_ * ((a_ + 1) + (a_ - 1) * cos + root), -2 * a_ * ((a_ - 1) + (a_ + 1) * cos),
             a_ * ((a_ + 1) + (a_ - 1) * cos - root)]
        a = [(a_ + 1) - (a_ - 1) * cos + root, 2 * ((a_ - 1) - (a_ + 1) * cos), (a_ + 1) - (a_ - 1) * cos - root]
    return np.array(b) / a[0], np.array(a) / a[0]


# Each band's response is the mean power gain over 64 frequencies spread
# evenly in log frequency across it, as the takes' band power sums the
# partials wherever they fall.
def grid(centres: np.ndarray) -> np.ndarray:
    return np.exp(np.linspace(np.log(centres * 2 ** (-1 / 6)), np.log(centres * 2 ** (1 / 6)), 64, axis=1))


GRID = grid(CENTRES)


def band_response_db(sections: list, frequencies: np.ndarray = GRID) -> np.ndarray:
    z = np.exp(-1j * 2 * np.pi * frequencies / RATE)
    power = np.ones_like(frequencies)
    for kind, hz, q, gain in sections:
        b, a = coefficients(kind, hz, q, gain)
        power *= np.abs((b[0] + b[1] * z + b[2] * z * z) / (a[0] + a[1] * z + a[2] * z * z)) ** 2
    return 10 * np.log10(power.mean(1))


def unpack(p: np.ndarray, peaks: int):
    shelf = 1 / np.sqrt(2)
    sections = [('low', float(np.exp(p[1])), shelf, float(p[2])), ('high', float(np.exp(p[3])), shelf, float(p[4]))]
    for k in range(peaks):
        sections.append(('peak', float(np.exp(p[5 + 3 * k])), float(np.exp(p[6 + 3 * k])), float(p[7 + 3 * k])))
    return float(p[0]), sections


def fit(target: np.ndarray, count: np.ndarray, peaks: int):
    """Greedy then joint least squares: each peaking section starts at the
    band the sections before it miss most, then all move together. The
    peaking sections stay inside the measured bands; the shelves set the
    level beyond them."""
    use = np.isfinite(target)
    weight = np.sqrt(count[use])
    # Beyond the measured bands the response holds the level of the band at
    # either end, two bands on at that band's weight: no partial there
    # stands clear of the floor in both microphones, so the recordings
    # say nothing of it.
    first, last = np.flatnonzero(use)[[0, -1]]
    beyond = CENTRES[[first, first, last, last]] * 2.0 ** (np.array([-2, -1, 1, 2]) / 3)
    beyond_grid = grid(beyond)
    held = target[[first, first, last, last]]
    held_weight = np.sqrt(count[[first, first, last, last]])
    low = [-40, np.log(20), -15, np.log(1000), -15]
    high = [40, np.log(300), 15, np.log(12000), 15]
    inside = (np.log(CENTRES[first]), np.log(CENTRES[last]))
    p = np.array([np.median(target[use]), np.log(60), 0., np.log(4000), 0.])
    for k in range(peaks + 1):
        bounds = (low + [inside[0], np.log(.3), -15] * k, high + [inside[1], np.log(8), 15] * k)

        def residual(x):
            gain, sections = unpack(x, k)
            return np.r_[weight * (gain + band_response_db(sections)[use] - target[use]),
                         held_weight * (gain + band_response_db(sections, beyond_grid) - held)]
        p = optimize.least_squares(residual, np.clip(p, *bounds), bounds=bounds, x_scale='jac', max_nfev=4000).x
        if k == peaks:
            break
        gain, sections = unpack(p, k)
        miss = np.where(use, target - gain - band_response_db(sections), 0)
        worst = int(np.argmax(np.abs(miss) * np.sqrt(count)))
        p = np.r_[p, np.log(CENTRES[worst]), np.log(1.4), miss[worst]]
    return unpack(p, peaks)


def error(gain, sections, median):
    use = np.isfinite(median)
    return float(np.mean(np.abs(gain + band_response_db(sections)[use] - median[use])))


def takes(role: str):
    split = json.loads(SPLIT.read_text())['cases']
    tube = {f['id'] for f in json.loads(TUBE.read_text())['files']}
    return [f for f in json.loads(RIBBON.read_text())['files']
            if f['kind'] == 'note' and split[f['id']] == role and f['id'] in tube]


def generate(jobs: int):
    with concurrent.futures.ProcessPoolExecutor(jobs) as pool:
        train = list(pool.map(measure, takes('train')))
        dev = list(pool.map(measure, takes('dev')))
    target, count = medians(train, MIN_TRAIN)
    dev_median, dev_count = medians(dev, MIN_DEV)
    gain, sections = fit(target, count, SECTIONS)
    response = gain + band_response_db(sections)
    flat = np.nanmedian(target)
    use = np.isfinite(dev_median)
    lines = [
        '// Generated by Tools/fit_mic.py from the Helsinki 1967 Tube-Ribbon Edition',
        '// (Mikko Patama): the tube microphone\'s perspective over the ribbon pair\'s',
        '// mid on the same strikes, fitted on the split\'s train takes and scored on',
        f'// its dev takes ({len(train)} and {len(dev)} note takes, Docs/research/{METADATA.name}).',
        '// Only the response\'s shape is the tube\'s: its level is the engine\'s',
        '// calibration (KeyraEngine.cpp, tubeScale). Do not edit by hand.',
        '#pragma once',
        '',
        'namespace keyra::measured {',
        '',
        '// An RBJ cookbook biquad the engine designs at its own rate.',
        'enum class MicShape {peak,lowShelf,highShelf};',
        'struct MicSection {MicShape shape;double hz,q,gainDb;};',
        f'inline constexpr int tubeSections={len(sections)};',
        'inline constexpr MicSection tube[tubeSections]{',
    ]
    for kind, hz, q, g in sections:
        shape = {'peak': 'peak', 'low': 'lowShelf', 'high': 'highShelf'}[kind]
        lines.append(f'  {{MicShape::{shape},{hz:.2f},{q:.4f},{g:.3f}}},')
    lines += ['};', '', '} // namespace keyra::measured', '']
    content = '\n'.join(lines)
    metadata = {
        'schema': 1,
        'corpus': {'ribbon': str(RIBBON.relative_to(ROOT)), 'ribbon_sha256': sha256(RIBBON),
                   'tube': str(TUBE.relative_to(ROOT)), 'tube_sha256': sha256(TUBE),
                   'split': str(SPLIT.relative_to(ROOT)), 'split_sha256': sha256(SPLIT)},
        'fitter_source_sha256': sha256(Path(__file__)),
        'protocol': {'window_s': list(WINDOW), 'frame': FRAME, 'over_floor_db': OVER_FLOOR_DB,
                     'least_train_takes': MIN_TRAIN, 'least_dev_takes': MIN_DEV, 'sections': SECTIONS},
        'train_takes': [r['id'] for r in train], 'dev_takes': [r['id'] for r in dev],
        'band_hz': [round(float(c), 1) for c in CENTRES],
        'train_median_db': [None if not np.isfinite(x) else round(float(x), 2) for x in target],
        'train_takes_kept': [int(c) for c in count],
        'dev_median_db': [None if not np.isfinite(x) else round(float(x), 2) for x in dev_median],
        'dev_takes_kept': [int(c) for c in dev_count],
        'fitted_db': [round(float(x), 2) for x in response],
        'fitted_gain_db': round(gain, 2),
        'sections': [{'kind': kind, 'hz': round(hz, 2), 'q': round(q, 4), 'gain_db': round(g, 3)}
                     for kind, hz, q, g in sections],
        'train_mean_abs_error_db': round(error(gain, sections, target), 3),
        'dev_mean_abs_error_db': round(error(gain, sections, dev_median), 3),
        'dev_mean_abs_error_flat_db': round(float(np.mean(np.abs(flat - dev_median[use]))), 3),
        'dev_mean_abs_error_train_medians_db': round(float(np.nanmean(np.abs(target - dev_median))), 3),
        'generated_header_sha256': hashlib.sha256(content.encode()).hexdigest(),
    }
    return content, metadata, (train, dev, target, count, dev_median)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--jobs', type=int, default=os.cpu_count() or 1)
    parser.add_argument('--check', action='store_true', help='verify the header and provenance reproduce')
    parser.add_argument('--sections', action='store_true', help='print train and dev error by section count')
    args = parser.parse_args()
    content, metadata, (train, dev, target, count, dev_median) = generate(args.jobs)
    if args.sections:
        for peaks in range(2, 9):
            gain, sections = fit(target, count, peaks)
            print(f'{peaks} peaks: train {error(gain, sections, target):.3f} dB, '
                  f'dev {error(gain, sections, dev_median):.3f} dB')
        return
    if args.check:
        if HEADER.read_text() != content:
            raise SystemExit('Measured mic header differs from the regenerated fit')
        if json.loads(METADATA.read_text()) != metadata:
            raise SystemExit('Measured mic provenance differs from the regenerated fit')
        print('measured mic header and provenance reproduce exactly')
        return
    HEADER.write_text(content)
    METADATA.write_text(json.dumps(metadata, indent=2, allow_nan=False) + '\n')
    print(f'{len(train)} train and {len(dev)} dev takes; train error {metadata["train_mean_abs_error_db"]} dB, '
          f'dev {metadata["dev_mean_abs_error_db"]} dB (flat {metadata["dev_mean_abs_error_flat_db"]} dB, '
          f'the train medians themselves {metadata["dev_mean_abs_error_train_medians_db"]} dB)')


if __name__ == '__main__':
    main()
