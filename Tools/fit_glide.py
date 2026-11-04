#!/usr/bin/env python3
"""Measure each piano's pitch glide on the train takes of its locked split
(fit_realtime_modal.MODELS) and write it into Source/DSP/MeasuredGlide.h.

A string's mean tension rises with the square of its slope, so a struck
string plays sharp and settles as it decays (tension modulation: T. Tolonen,
V. Valimaki and M. Karjalainen, IEEE Trans. Speech Audio Process. 8(3),
300-310, 2000). For partials of displacement a(n) the tension grows by
EA pi^2 / (8 L^2) sum n^2 a(n)^2 and every frequency by half that share of
the tension; a partial's energy is mu L pi^2 f1^2 n^2 a(n)^2, so the glide
is in proportion to the string's whole energy. The engine plays it as
cents(t) = K 2^(s (key - 60) / 12) P(t), P(t) its key's partials' power,
both channels' squared amplitudes summed, in the recordings' units (1 at
full scale), and the key held between the lowest and the highest pitch
measured: output power falls with the string's energy at each partial's
own rate, so P stands for it where the board radiates the partials alike.

Each take, from its onset (piano_analysis.onset), at the frequencies of the
table's measured partials (piano_analysis.envelopes, every 5 ms):
- the glide: each of the first ten partials' frequency from its phase's
  slope, both channels summed, fitted with weights |z| over 0.05 to 0.35 s
  and over 0.6 to 1.1 s; the early's cents over the late's, the median over
  the partials. A take whose recording ends before 1.1 s and half a window
  (piano_analysis.recorded_end) is left out;
- the drop: P's mean over the first window less its mean over the second,
  P the table's (MeasuredModalData.h) at the take's layer: each lane's level
  and decay, both channels, over the partials and the extras, as the engine
  plays them. In the bass, measured at the partials' frequencies, the takes
  hold a half to a third of it (upright C1, New York C1 and A#1), where a
  partial's lanes beat against each other: the lanes' powers add as the
  string's modes' energies do.

A piano's takes give glide = a(pitch) + K 2^(s (key - 60) / 12) drop: an
offset per pitch takes what does not grow with the strike (the unison's
beating moves a partial's phase as it decays at every layer), and K and s
are the law, s profiled over a grid. The partials are drawn 2000 times
within each take (seeded by the piano): a take's error e is its median's
spread over the draws, and it weighs as 1 / (e^2 + tau^2), tau the takes'
scatter beyond their errors, set so that the weighted residuals' mean
square is 1. The null shuffles the drops among each pitch's takes 2000
times, so that no take's glide goes with its own strike. The takes show a
glide where the lowest 0.1 % of K refitted on the draws stays above zero
and the law lowers chi^2 by more than the highest 0.1 % of the null's.
Elsewhere K is 0.

  python3 Tools/fit_glide.py           # measure every piano, write the header and the receipt
  python3 Tools/fit_glide.py --check   # the receipt is current and the header is the one it gives
"""
from __future__ import annotations

import argparse
import json
import os
import zlib
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import numpy as np

import fit_realtime_modal as fit
import import_modal_measurements as imm
import piano_analysis as pa

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / 'Source/DSP/MeasuredGlide.h'
RECEIPT = ROOT / 'Docs/research/pitch-glide-2026-11-04.json'
PIANOS = ('grand', 'upright', 'kawai', 'hamburg', 'newyork')
EARLY, LATE, HOP = (.05, .35), (.6, 1.1), .005
GLIDING = 10  # the first partials whose frequencies give the glide
MIN_PARTIALS = 5  # a take with fewer measured there is left out
SLOPES = np.round(np.arange(-3., 1.0001, .05), 2)  # s, per octave
DRAWS, CONFIDENCE = 2000, .999


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def frequencies(anchor, sr):
    hz = np.array([pa.stiff(anchor['f1'], anchor['B'], p['order']) * 2 ** (p['cents'] / 1200) for p in anchor['partials']])
    return hz[hz < .45 * sr]


def slope(t, z, window):
    k = (t >= window[0] - 1e-9) & (t <= window[1] + 1e-9) & (np.abs(z) > 0)
    if k.sum() < 4:
        return None
    return np.polyfit(t[k], np.unwrap(np.angle(z[k])), 1, w=np.sqrt(np.abs(z[k])))[0]


def measure_take(path, anchor):
    """The take's glide at each of its first partials (cents, early over
    late), or None."""
    sr, x = pa.load(path)
    start = pa.onset(x, sr)
    if pa.recorded_end(x, sr, start) - start < (LATE[1] + .5 * pa.window_length(anchor['f1'], sr) / sr) * sr:
        return None
    hz = frequencies(anchor, sr)[:GLIDING]
    times = np.concatenate([np.arange(EARLY[0], EARLY[1] + 1e-9, HOP), np.arange(LATE[0], LATE[1] + 1e-9, HOP)])
    t, z = pa.envelopes(x, sr, hz, anchor['f1'], start, None, times=times)
    glides = []
    for f, series in zip(hz, z.sum(axis=1)):
        a, b = slope(t, series, EARLY), slope(t, series, LATE)
        if a is None or b is None:
            continue
        fa, fb = f + a / (2 * np.pi), f + b / (2 * np.pi)
        if fa > 0 and fb > 0:
            glides.append(float(1200 * np.log2(fa / fb)))
    return glides if len(glides) >= MIN_PARTIALS else None


def table_drop(anchor, layer):
    """The table's power at a layer, its mean over the early window less its
    mean over the late: each lane's 10^(level / 10) (left^2 + |right|^2) as
    it decays, over the partials and the extras."""
    def mean(rate, window):
        a, b = window
        return (np.exp(-2 * rate * a) - np.exp(-2 * rate * b)) / (2 * rate * (b - a))
    return float(sum(10 ** (lane['level_db'][layer] / 10) * (lane['left'] ** 2 + abs(lane['right']) ** 2)
                     * (mean(lane['rate'], EARLY) - mean(lane['rate'], LATE))
                     for p in anchor['partials'] + anchor['extras'] for lane in p['lanes']))


def take_job(args):
    path, anchor = args
    return measure_take(path, anchor)


def design(notes, x):
    """An offset per pitch and the law's column x."""
    columns = sorted(set(notes))
    X = np.zeros((len(x), len(columns) + 1))
    X[np.arange(len(x)), [columns.index(n) for n in notes]] = 1
    X[:, -1] = x
    return X


def chi2(X, y, w):
    beta = np.linalg.lstsq(X * w[:, None], y * w, rcond=None)[0]
    return float(np.sum(((y - X @ beta) * w) ** 2)), beta


def law_fit(notes, y, w, drop):
    """The law's chi^2, s and K, s profiled over SLOPES."""
    keys = (np.asarray(notes) - 60) / 12
    best = None
    for s in SLOPES:
        c, beta = chi2(design(notes, 2 ** (s * keys) * drop), y, w)
        if best is None or c < best[0]:
            best = (c, float(s), float(beta[-1]))
    return best


def scatter(notes, y, e, drop):
    """tau: the takes' scatter beyond their errors, so that the weighted
    residuals' mean square at the law's best slope is 1 (0 where the errors
    hold it)."""
    dof = len(y) - len(set(notes)) - 2
    tau = 0.
    for _ in range(4):
        s = law_fit(notes, y, 1 / np.sqrt(e ** 2 + tau ** 2), drop)[1]
        keys = 2 ** (s * (np.asarray(notes) - 60) / 12) * drop
        at = lambda t: chi2(design(notes, keys), y, 1 / np.sqrt(e ** 2 + t ** 2))[0]
        if at(0.) <= dof:
            return 0.
        lo, hi = 0., float(np.max(np.abs(y))) + 1
        for _ in range(50):
            mid = .5 * (lo + hi)
            lo, hi = (mid, hi) if at(mid) > dof else (lo, mid)
        tau = .5 * (lo + hi)
    return tau


def measure_piano(name, pool):
    model = fit.MODELS[name]
    table = imm.load(model['header'])
    anchors = {a['note']: a for a in table['anchors']}
    grid = np.array(table['grid'])
    train = fit.train_anchors(model)
    jobs = [(note, case, velocity, pin) for note, layers in train.items() if note in anchors for case, velocity, pin in layers]
    results = list(pool.map(take_job, [(model['wav'] / f'{case}.wav', anchors[note]) for note, case, _, _ in jobs]))
    takes, rows = [], []
    for (note, case, velocity, pin), result in zip(jobs, results):
        take = dict(note=note, case=case, velocity=velocity, pin=pin)
        if result is None:
            take['skipped'] = 'too short or too few partials'
        else:
            take.update(glide=float(np.median(result)), drop=table_drop(anchors[note], int(np.argmin(np.abs(grid - velocity)))), partials=result)
            rows.append(take)
        takes.append(take)
    rng = np.random.default_rng(zlib.crc32(name.encode()))
    # Each take's median over its partials drawn with replacement: its error
    # is their spread, and the law refitted on each draw gives K's.
    draws = np.array([[np.median(np.asarray(r['partials'])[rng.integers(0, len(r['partials']), len(r['partials']))]) for r in rows]
                      for _ in range(DRAWS)])
    notes = [r['note'] for r in rows]
    y = np.array([r['glide'] for r in rows])
    e = draws.std(axis=0)
    drop = np.array([r['drop'] for r in rows])
    tau = scatter(notes, y, e, drop)
    w = 1 / np.sqrt(e ** 2 + tau ** 2)
    for r, error in zip(rows, e):
        r['error'] = float(error)
    plain = chi2(design(notes, np.zeros(len(y)))[:, :-1], y, w)[0]
    law, s, K = law_fit(notes, y, w, drop)
    low, high = (float(v) for v in np.quantile([law_fit(notes, d, w, drop)[2] for d in draws], [1 - CONFIDENCE, CONFIDENCE]))
    # The null: the drops shuffled among each pitch's takes, so that no
    # take's glide goes with its own strike.
    groups = {}
    for i, n in enumerate(notes):
        groups.setdefault(n, []).append(i)
    null = []
    for _ in range(DRAWS):
        shuffled = drop.copy()
        for index in groups.values():
            shuffled[index] = rng.permutation(drop[index])
        null.append(plain - law_fit(notes, y, w, shuffled)[0])
    null_high = float(np.quantile(null, CONFIDENCE))
    found = low > 0 and plain - law > null_high
    loudest = {}
    for r in rows:
        if r['note'] not in loudest or r['velocity'] > loudest[r['note']]['velocity']:
            loudest[r['note']] = r
    print(f'{name}: {len(rows)} of {len(takes)} takes, K {K:.4g} ({low:.4g} to {high:.4g}) cents per unit power at C4, '
          f'x{2 ** s:.3g} per octave, tau {tau:.3f} cents; the law gains chi^2 {plain - law:.1f}, the shuffled drops '
          f'{null_high:.1f} at the {100 * CONFIDENCE:g} %: {"a glide" if found else "none"}', flush=True)
    for note, r in sorted(loudest.items()):
        print(f'  {note}: loudest take v{r["velocity"]} {r["glide"]:+.2f} cents (law {K * 2 ** (s * (note - 60) / 12) * r["drop"]:+.2f})', flush=True)
    return dict(header=rel(model['header']), header_sha256=fit.sha256(model['header']),
                split=rel(model['split']), split_sha256=fit.sha256(model['split']),
                corpus=rel(model['corpus']), corpus_sha256=fit.sha256(model['corpus']),
                K=K, per_octave=s, tau=tau, K_low=low, K_high=high, chi2_gain=plain - law, null_gain=null_high,
                found=found, cents=K if found else 0., low=min(notes), high=max(notes), takes=takes)


def header_text(receipt):
    lines = [
        '// Generated by Tools/fit_glide.py from the train takes of each piano\'s',
        f'// split ({rel(RECEIPT)}); regenerate, never edit.',
        '// Fitted numbers only: no recorded waveform.',
        '#pragma once',
        '',
        'namespace keyra { namespace measured {',
        '// A piano\'s pitch glide: a key plays sharp by cents 2^(perOctave',
        '// (key - 60) / 12) P, P its partials\' power, both channels\' squared',
        '// amplitudes summed, in the recordings\' units (1 at full scale), the',
        '// key held between the lowest and the highest pitch measured. 0 where',
        '// the takes show none.',
        'struct Glide { float cents; float perOctave; int low; int high; };',
    ]
    for name in PIANOS:
        m = receipt['pianos'][name]
        lines.append(f'namespace {name} {{ constexpr Glide glide{{{fit.number(m["cents"])},{fit.number(m["per_octave"] if m["found"] else 0.)},'
                     f'{m["low"]},{m["high"]}}}; }}')
    lines += ['}}', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true', help='check the receipt against the tool, its inputs and the header, and exit')
    parser.add_argument('--jobs', type=int, default=2, help='takes measured at once')
    args = parser.parse_args()
    if args.check:
        receipt = json.loads(RECEIPT.read_text())
        stale = {rel(Path(__file__))} if receipt['tool_sha256'] != fit.sha256(Path(__file__)) else set()
        for measured in receipt['pianos'].values():
            stale |= {measured[k] for k in ('header', 'split', 'corpus') if measured[f'{k}_sha256'] != fit.sha256(ROOT / measured[k])}
        if stale:
            raise SystemExit(f'{rel(RECEIPT)} predates the current {", ".join(sorted(stale))}: run Tools/fit_glide.py')
        if HEADER.read_text() != header_text(receipt):
            raise SystemExit(f'{rel(HEADER)} differs from {rel(RECEIPT)}: run Tools/fit_glide.py')
        print(f'{rel(HEADER)} matches {rel(RECEIPT)}')
        return
    with ProcessPoolExecutor(args.jobs) as pool:
        pianos = {name: measure_piano(name, pool) for name in PIANOS}
    receipt = dict(tool=rel(Path(__file__)), tool_sha256=fit.sha256(Path(__file__)),
                   protocol=dict(early_seconds=list(EARLY), late_seconds=list(LATE), hop_seconds=HOP, gliding=GLIDING,
                                 min_partials=MIN_PARTIALS, slopes=[float(SLOPES[0]), float(SLOPES[-1]), .05],
                                 draws=DRAWS, confidence=CONFIDENCE),
                   pianos=pianos)
    RECEIPT.write_text(json.dumps(receipt, indent=1) + '\n')
    HEADER.write_text(header_text(receipt))
    print(f'wrote {rel(HEADER)} and {rel(RECEIPT)}')


if __name__ == '__main__':
    main()
