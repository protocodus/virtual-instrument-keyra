#!/usr/bin/env python3
"""Measure each piano's phantom partials on the train takes of its locked
split (fit_realtime_modal.MODELS) and write them into
Source/DSP/MeasuredPhantoms.h.

A string's tension grows with the square of its displacement, so a struck
string also sounds lines at the sums f(m) + f(n) of its partials'
frequencies, just under the series (phantom partials: H. A. Conklin, JASA
105(1), 536-545, 1999), and at their differences f(n) - f(m); the piano's
wooden parts make both as well (T. R. Moore, L. M. Neldner and E. Rokni,
JASA 144(3), 1564, 2018). The engine plays them as gain x^2 added to each
channel, x a key's partials in that channel, its constant taken out: a line
of gain a(m) a(n) at f(m) + f(n) and at f(n) - f(m), and of gain a(m)^2/2 at
2 f(m), for partials of amplitudes a(m) and a(n).

Each take, both channels' power summed:
- the window: 0.05 to 1.05 s after the onset (piano_analysis.onset), Nuttall's
  4-term window with a continuous first derivative, whose side lobes lie
  93 dB under a partial; zero at its ends, so that beside a partial decaying
  fast its skirt keeps falling, where Blackman-Harris's settles on its ends'
  6e-5 (70 dB under a partial decaying at 30/s: 52 Hz away against 327 Hz);
  zero-padded four times (0.25 Hz bins);
- the prediction: x^2 of the take itself in the same window, its mean taken
  out: what the engine's square makes of these partials at gain 1, with
  their own decay and beating, so that neither biases the fit below;
- what else rings: the lanes of the series' measured partials and extra
  components, the series beyond its measured orders, the undamped strings
  from F6 up (their first four partials, at the pitches the engine gives
  them) and the body's modes clear of the partials. Each skirts the bins
  around it as a lane at its rate decays through the window, from its peak
  in the take, shared among a partial's lanes by their levels at the take's
  layer, decayed to and through the window;
- the lines: every sum f(m) + f(n) and difference f(n) - f(m) of two of the
  series' partials from 200 Hz to 8 kHz, at the measured series (its
  stiffness and each partial's cents); lines within 3 Hz of each other share
  one window, from 1.5 Hz under the lowest to 1.5 Hz over the highest, kept
  where no lane lies within 4.5 Hz of it, beyond a steady one's main lobe
  (4 Hz);
- the fit: from 8 Hz under a window to 8 Hz over it, on the bins 4.5 Hz or
  more from every lane where the skirts put under a tenth of what the line
  would at gain 0.01, and with 2 Hz of them each side, the take's spectrum
  is a quadratic floor plus gain^2 times the prediction's, with its
  standard error from the fit's residual;
- the null: the same fit with the take's spectrum moved 11 to 17 Hz to one
  side of the line (alternately), as clear, where the prediction peaks at
  under a tenth of its peak in the line's window: what the fit finds where
  no line is.

A recorded pitch's gain^2 is the windows' over all its takes, weighted by
their inverse variance, so that the clearest lines decide it. The windows
are drawn 2000 times (seeded by the pitch); the takes show phantom partials
where the lowest 0.1 % of the draws stays above zero while the null's
lowest and highest 0.1 % hold zero between them, over 30 windows or more.
Between two pitches that show them, one that doesn't takes the gain
interpolated between them, or the most its own takes allow where that is
less (fill); elsewhere the gain is 0.

The lines' gain depends on where they lie: at the grand's F#3, C4 and F#4,
those from 1.6 to 3.2 kHz read 8 to 10 dB over those from 3.2 to 6.4 kHz and
6 to 8.5 dB over the pitch's pooled gain, while the null beside them reads
15 to 30 dB under them. One gain per pitch plays the lines from 1.6 to
3.2 kHz that much too soft, and those from 3.2 to 6.4 kHz 1 to 3 dB too loud
(Docs/research/phantom-partials-2026-11-04.md).

  python3 Tools/fit_phantoms.py           # measure every piano, write the header and the receipt
  python3 Tools/fit_phantoms.py --check   # the receipt is current and the header is the one it gives
"""
from __future__ import annotations

import argparse
import functools
import json
import os
from pathlib import Path

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import numpy as np

import fit_realtime_modal as fit
import import_modal_measurements as imm
import piano_analysis as pa

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / 'Source/DSP/MeasuredPhantoms.h'
RECEIPT = ROOT / 'Docs/research/phantom-partials-2026-11-04.json'
PIANOS = ('grand', 'upright', 'kawai', 'hamburg', 'newyork')
START, LENGTH, PAD = .05, 1., 4
LOW_HZ, TOP_HZ = 200., 8000.
HALF_HZ = 1.5  # a line's window either side of its sum
JOIN_HZ = 3.  # sums this close share a window
CLEAR_HZ = 4.5  # no lane this close outside a window
REACH = 8.  # the floor's span either side of a window
SUPPORT = 2.  # of clear bins the floor needs each side
NULL_GAPS = (11., 13., 15., 17.)  # the null's distance from the line
NULL_SHARE = .1
DRAWS, CONFIDENCE = 2000, .999
MIN_WINDOWS = 30  # a pitch with fewer over its takes is not measured
# Nuttall's 4-term window with a continuous first derivative: zero at its
# ends, so that beside a fast-decaying partial its skirt keeps falling where
# Blackman-Harris's settles on its ends' 6e-5 (70 dB under a partial decaying
# at 30/s: 52 Hz away against 327 Hz).
NUTTALL = (0.355768, 0.487396, 0.144232, 0.012604)
SHAPE_RATE = 4096  # Hz: the lanes' skirts are sampled at this rate
SHAPE_FLOOR = 1e-16  # a skirt under this share of its peak is left out
GAIN_REF = .01  # the smallest gain the fit must still read
SKIRT_SHARE = .1  # of the line at GAIN_REF the partials' skirts may put in a bin


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def key_pitch(anchors, note, field='f1'):
    """A key's fundamental, or with field='B' its stiffness, between the
    recorded pitches around it as the engine gives it (keyPitch): its cents
    from equal temperament, or log B, along the keys, continued from the last
    two beyond them."""
    upper = 1
    while upper < len(anchors) - 1 and anchors[upper]['note'] < note:
        upper += 1
    a, b = anchors[upper - 1], anchors[upper]
    t = (note - a['note']) / (b['note'] - a['note'])
    if field == 'B':
        return float(np.exp(np.log(a['B']) + t * (np.log(b['B']) - np.log(a['B']))))
    cents = [1200 * np.log2(x['f1'] / (440 * 2 ** ((x['note'] - 69) / 12))) for x in (a, b)]
    return 440 * 2 ** ((note - 69 + (cents[0] + t * (cents[1] - cents[0])) / 100) / 12)


def nuttall(n):
    x = np.arange(n) / n
    return sum((-1) ** k * c * np.cos(2 * np.pi * k * x) for k, c in enumerate(NUTTALL))


@functools.lru_cache(maxsize=None)
def skirt(rate):
    """A lane decaying at `rate` (1/s) through the window: its power beside
    its frequency against its peak's, in the takes' bins from 0 Hz until it
    falls under SHAPE_FLOOR, and its peak's amplitude against a steady lane's
    that starts the window as loud."""
    n = int(SHAPE_RATE * LENGTH)
    w = nuttall(n)
    decayed = w * np.exp(-rate * np.arange(n) / SHAPE_RATE)
    power = np.abs(np.fft.rfft(decayed, n=PAD * n)) ** 2
    power /= power[0]
    return power[:np.flatnonzero(power > SHAPE_FLOOR)[-1] + 1], float(np.sum(decayed) / np.sum(w))


def ringing(anchor, anchors, table, top):
    """What rings besides the lines up to `top`: the frequencies a window
    must stay clear of, and the groups whose skirts a take's floor holds, as
    (Hz, lanes), each lane (Hz, rate 1/s, level dB per layer or None, pickup
    power). The measured partials and extras with their lanes; the series
    beyond the measured orders, decaying as the highest measured partial's
    fastest lane; the undamped strings from F6 up, which every strike sets
    ringing, with their first four partials; the body's modes clear of the
    partials."""
    groups = []
    for p in anchor['partials'] + anchor['extras']:
        hz = float(pa.stiff(anchor['f1'], anchor['B'], p['order'])) * 2 ** (p['cents'] / 1200)
        lanes = [(hz + lane['offset_hz'], lane['rate'], lane['level_db'],
                  lane['left'] ** 2 + abs(lane['right']) ** 2) for lane in p['lanes']]
        groups.append((hz, lanes))
    measured = {p['order'] for p in anchor['partials']}
    highest = max(anchor['partials'], key=lambda p: p['order'])
    fastest = max(lane['rate'] for lane in highest['lanes'])
    for order, hz in enumerate(series_hz(anchor, top), 1):
        if order not in measured:
            groups.append((hz, [(hz, fastest, None, 1.)]))
    halo = table['halo']
    for key, cents, rate in zip(halo['keys'], halo['cents'], halo['rates']):
        f1 = key_pitch(anchors, key) * 2 ** (cents / 1200)
        for hz in pa.stiff(f1, key_pitch(anchors, key, 'B'), np.arange(1, 5)):
            groups.append((float(hz), [(float(hz), rate, None, 1.)]))
    lanes = np.sort([lane[0] for _, group in groups for lane in group])
    body = table['body']
    for hz, rate in zip(body['hz'], body['rates']):
        i = np.searchsorted(lanes, hz)
        if np.min(np.abs(lanes[max(i - 1, 0):i + 1] - hz)) > CLEAR_HZ:
            groups.append((float(hz), [(float(hz), rate, None, 1.)]))
    groups = [g for g in groups if g[0] <= top]
    blocked = np.sort([lane[0] for _, group in groups for lane in group])
    return blocked, groups


def skirt_floor(groups, taken, df, layer):
    """The power the ringing groups' skirts put in each bin of a take's
    spectrum: each group's peak in the take (its highest bin within HALF_HZ),
    shared among its lanes as their levels at the take's layer, decayed to and
    through the window, give it."""
    floor = np.zeros_like(taken)
    near = int(round(HALF_HZ / df))
    for hz, lanes in groups:
        k = int(round(hz / df))
        if k - near < 0 or k + near >= len(taken):
            continue
        peak = taken[k - near:k + near + 1].max()
        power = np.array([1. if level is None else
                          10 ** (level[layer] / 10) * pickup * (skirt(rate)[1] * np.exp(-rate * START)) ** 2
                          for _, rate, level, pickup in lanes])
        for (lane_hz, rate, _, _), share in zip(lanes, power / power.sum()):
            shape = skirt(rate)[0]
            span = (len(shape) - 1) * df
            bins = np.arange(max(int(np.ceil((lane_hz - span) / df)), 0), min(int((lane_hz + span) / df), len(taken) - 1) + 1)
            floor[bins] += peak * share * np.interp(np.abs(bins * df - lane_hz) / df, np.arange(len(shape)), shape)
    return floor


def series_hz(anchor, top):
    """The series' partials up to `top`, at the measured cents where measured."""
    cents = {p['order']: p['cents'] for p in anchor['partials']}
    orders = np.arange(1, int(top / anchor['f1']) + 1)
    hz = pa.stiff(anchor['f1'], anchor['B'], orders) * 2 ** (np.array([cents.get(int(o), 0.) for o in orders]) / 1200)
    return hz[hz <= top]


def line_windows(anchor, blocked):
    """The line windows (lo, hi Hz) over the series' sums and differences,
    clear of `blocked`."""
    hz = series_hz(anchor, TOP_HZ)
    lines = np.concatenate([(hz[:, None] + hz[None, :])[np.triu_indices(len(hz))],
                            (hz[None, :] - hz[:, None])[np.triu_indices(len(hz), 1)]])
    lines = np.sort(lines[(lines >= LOW_HZ) & (lines <= TOP_HZ)])
    if not len(lines):
        return np.zeros((0, 2))
    breaks = np.flatnonzero(np.diff(lines) > JOIN_HZ) + 1
    groups = np.split(lines, breaks)
    windows = np.array([(g[0] - HALF_HZ, g[-1] + HALF_HZ) for g in groups])
    return windows[clear(windows, blocked)]


def clear(windows, blocked):
    """Which windows have no blocked frequency within CLEAR_HZ outside them."""
    lo, hi = windows[:, 0] - CLEAR_HZ, windows[:, 1] + CLEAR_HZ
    return np.searchsorted(blocked, lo, 'left') == np.searchsorted(blocked, hi, 'right')


def take_spectra(path):
    """A take's power spectrum and its prediction's, channels summed, and the
    bin width; None where the take ends inside the window."""
    sr, x = pa.load(path)
    on = pa.onset(x, sr)
    start, n = on + int(START * sr), int(LENGTH * sr)
    if start + n > pa.recorded_end(x, sr, on):
        return None
    square = x[start:start + n] ** 2
    square -= square.mean(axis=0)
    w = nuttall(n)[:, None]

    def power(y):
        return np.sum(np.abs(np.fft.rfft(y * w, n=PAD * n, axis=0)) ** 2, axis=1)

    return sr / (PAD * n), power(x[start:start + n]), power(square)


def regress(df, taken, predicted, floor, lo, hi, blocked, shift=0.):
    """gain^2 and its standard error at one window: the take's spectrum from
    REACH under the window lo-hi to REACH over it, moved by `shift`,
    regressed on the prediction's over the window's own bins beside a
    quadratic floor, on the bins clear of every blocked lane and where the
    partials' skirts put under SKIRT_SHARE of the line at GAIN_REF; None
    without SUPPORT each side."""
    move = int(round(shift / df))
    k = np.arange(int(np.ceil((lo - REACH) / df)), int(np.floor((hi + REACH) / df)) + 1)
    if k[0] + move < 1 or k[-1] + move >= len(taken):
        return None
    hz = (k + move) * df
    inside = (hz >= lo + shift) & (hz <= hi + shift)
    line = np.max(predicted[k[inside]])
    i = np.clip(np.searchsorted(blocked, hz), 1, len(blocked) - 1)
    ok = np.minimum(np.abs(hz - blocked[i - 1]), np.abs(hz - blocked[i])) > CLEAR_HZ
    ok &= floor[k + move] < SKIRT_SHARE * GAIN_REF ** 2 * line
    if not ok[inside].all() or min(np.sum(ok & (hz < lo + shift)), np.sum(ok & (hz > hi + shift))) * df < SUPPORT:
        return None
    if shift and np.max(predicted[k[inside] + move]) > NULL_SHARE * line:
        return None
    template, y = predicted[k[ok]], taken[k[ok] + move]
    if line <= 0 or np.max(y) <= 0:
        return None
    # Each column at unit peak keeps the normal equations well conditioned.
    tscale, yscale = np.max(template), np.max(y)
    u = (k[ok] * df - (lo + hi) / 2) / REACH
    X = np.stack([np.ones_like(u), u, u * u, template / tscale], axis=1)
    beta, *_ = np.linalg.lstsq(X, y / yscale, rcond=None)
    residual = y / yscale - X @ beta
    variance = residual @ residual / max(len(y) - 4, 1) * np.linalg.inv(X.T @ X)[3, 3]
    return beta[3] * yscale / tscale, np.sqrt(variance) * yscale / tscale


def measure_take(path, windows, blocked, groups, layer):
    """Each window's gain^2 and its standard error on one take, at its line
    and at the null's place beside it."""
    spectra = take_spectra(path)
    if spectra is None:
        return None
    df, taken, predicted = spectra
    floor = skirt_floor(groups, taken, df, layer)
    rows = []
    for j, (lo, hi) in enumerate(windows):
        line = regress(df, taken, predicted, floor, lo, hi, blocked)
        if line is None:
            continue
        for side in ((1, -1) if j % 2 else (-1, 1)):
            null = next((r for r in (regress(df, taken, predicted, floor, lo, hi, blocked, side * gap)
                                     for gap in NULL_GAPS) if r is not None), None)
            if null is not None:
                rows.append((*line, *null))
                break
    return np.array(rows).reshape(-1, 4)


def pooled(rows):
    """gain^2 over windows (rows of gain^2 and its error) weighted by their
    inverse variance, so that the clearest lines decide it."""
    weights = rows[..., 1] ** -2.
    return np.sum(rows[..., 0] * weights, axis=-1) / np.sum(weights, axis=-1)


def estimate(rows, rng):
    """gain^2 at the lines and beside them over the windows, with the lowest
    and highest 0.1 % of each over the windows drawn DRAWS times; None under
    MIN_WINDOWS windows."""
    if len(rows) < MIN_WINDOWS:
        return None
    drawn = rows[np.concatenate([rng.integers(0, len(rows), (100, len(rows))) for _ in range(DRAWS // 100)])]
    out = {}
    for name, columns in (('line', slice(0, 2)), ('null', slice(2, 4))):
        values = pooled(drawn[..., columns])
        out.update({name: float(pooled(rows[:, columns])), f'{name}_low': float(np.quantile(values, 1 - CONFIDENCE)),
                    f'{name}_high': float(np.quantile(values, CONFIDENCE))})
    return out


def fill(outputs):
    """Between two pitches that show phantom partials, one that doesn't takes
    the gain interpolated between them, as the engine gives the keys between
    recorded pitches, or the most its own takes allow where that is less: a
    pitch too clouded to show them is not taken to have none."""
    found = [i for i, o in enumerate(outputs) if o['found']]
    for i, o in enumerate(outputs):
        if o['found'] or not found or not found[0] < i < found[-1]:
            continue
        a = outputs[max(j for j in found if j < i)]
        b = outputs[min(j for j in found if j > i)]
        gain = a['gain'] + (o['note'] - a['note']) / (b['note'] - a['note']) * (b['gain'] - a['gain'])
        if 'line_high' in o:
            gain = min(gain, float(np.sqrt(max(o['line_high'], 0.))))
        o.update(gain=gain, filled=True)


def measure_piano(name):
    model = fit.MODELS[name]
    train = fit.train_anchors(model)
    table = imm.load(model['header'])
    grid = np.array(table['grid'])
    outputs = []
    for anchor in table['anchors']:
        note = anchor['note']
        blocked, groups = ringing(anchor, table['anchors'], table, TOP_HZ + 100)
        windows = line_windows(anchor, blocked)
        takes, measured = [], []
        for case, velocity, pin in train[note]:
            take = dict(case=case, velocity=velocity, pin=pin)
            rows = measure_take(model['wav'] / f'{case}.wav', windows, blocked, groups,
                                int(np.argmin(np.abs(grid - velocity))))
            if rows is None:
                take['skipped'] = 'ends inside the window'
            else:
                measured.append(rows)
                take['windows'] = len(rows)
                if len(rows):
                    take.update(line=float(pooled(rows[:, :2])), null=float(pooled(rows[:, 2:])))
            takes.append(take)
        rows = np.concatenate(measured) if measured else np.zeros((0, 4))
        result = estimate(rows, np.random.default_rng(note))
        # Found where the lines stand clear of zero and the fit finds nothing
        # beside them.
        found = result is not None and result['line_low'] > 0 and result['null_low'] < 0 < result['null_high']
        outputs.append(dict(note=note, windows=len(rows), **(result or {}), found=found,
                            gain=float(np.sqrt(result['line'])) if found else 0., takes=takes))
    fill(outputs)
    for o in outputs:
        detail = (f'gain^2 {o["line"]:.3g} ({o["line_low"]:.3g} to {o["line_high"]:.3g}), beside the lines '
                  f'{o["null"]:.3g} ({o["null_low"]:.3g} to {o["null_high"]:.3g})' if 'line' in o else 'too few')
        print(f'{name} {o["note"]}: {o["windows"]} windows, {detail}: gain {o["gain"]:.4g}'
              f'{" (between its neighbours)" if o.get("filled") else ""}', flush=True)
    return dict(header=rel(model['header']), header_sha256=fit.sha256(model['header']),
                split=rel(model['split']), split_sha256=fit.sha256(model['split']),
                corpus=rel(model['corpus']), corpus_sha256=fit.sha256(model['corpus']),
                outputs=outputs)


def header_text(receipt):
    lines = [
        '// Generated by Tools/fit_phantoms.py from the train takes of each piano\'s',
        f'// split ({rel(RECEIPT)}); regenerate, never edit.',
        '// Fitted numbers only: no recorded waveform.',
        '#pragma once',
        '#include <array>',
        '',
        'namespace keyra { namespace measured {',
        '// A recorded pitch\'s phantom partials, the lines its strings sound at the',
        '// sums f(m) + f(n) and differences f(n) - f(m) of their partials\'',
        '// frequencies: the engine adds gain x^2 to each channel, x the key\'s',
        '// partials there in the recordings\' units (1 at full scale), its',
        '// constant taken out: a line of gain a(m) a(n) at f(m) + f(n) and at',
        '// f(n) - f(m). 0 where the takes show none.',
        'struct Phantom { int note; float gain; };',
    ]
    for name in PIANOS:
        rows = receipt['pianos'][name]['outputs']
        values = ','.join(f'{{{r["note"]},{fit.number(r["gain"])}}}' for r in rows)
        lines.append(f'namespace {name} {{ constexpr std::array<Phantom,{len(rows)}> phantoms{{{{{values}}}}}; }}')
    lines += ['}}', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true', help='check the receipt against the tool, its inputs and the header, and exit')
    args = parser.parse_args()
    if args.check:
        receipt = json.loads(RECEIPT.read_text())
        stale = {rel(Path(__file__))} if receipt['tool_sha256'] != fit.sha256(Path(__file__)) else set()
        for measured in receipt['pianos'].values():
            stale |= {measured[k] for k in ('header', 'split', 'corpus') if measured[f'{k}_sha256'] != fit.sha256(ROOT / measured[k])}
        if stale:
            raise SystemExit(f'{rel(RECEIPT)} predates the current {", ".join(sorted(stale))}: run Tools/fit_phantoms.py')
        if HEADER.read_text() != header_text(receipt):
            raise SystemExit(f'{rel(HEADER)} differs from {rel(RECEIPT)}: run Tools/fit_phantoms.py')
        for name in PIANOS:
            notes = [a['note'] for a in imm.load(fit.MODELS[name]['header'])['anchors']]
            if notes != [r['note'] for r in receipt['pianos'][name]['outputs']]:
                raise SystemExit(f'{name}: the receipt\'s pitches are not the header\'s anchors')
        print(f'{rel(HEADER)} matches {rel(RECEIPT)}')
        return
    receipt = dict(tool=rel(Path(__file__)), tool_sha256=fit.sha256(Path(__file__)),
                   protocol=dict(window_seconds=[START, START + LENGTH], window='nuttall', pad=PAD,
                                 band_hz=[LOW_HZ, TOP_HZ], half_hz=HALF_HZ, join_hz=JOIN_HZ, clear_hz=CLEAR_HZ, gain_ref=GAIN_REF, skirt_share=SKIRT_SHARE,
                                 reach_hz=REACH, support_hz=SUPPORT, null_gaps_hz=list(NULL_GAPS),
                                 null_share=NULL_SHARE, draws=DRAWS, confidence=CONFIDENCE),
                   pianos={name: measure_piano(name) for name in PIANOS})
    RECEIPT.write_text(json.dumps(receipt, indent=1) + '\n')
    HEADER.write_text(header_text(receipt))
    print(f'wrote {rel(HEADER)} and {rel(RECEIPT)}')


if __name__ == '__main__':
    main()
