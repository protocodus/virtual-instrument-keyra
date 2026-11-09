#!/usr/bin/env python3
"""Measure how loud each piano's undamped strings ring in their own keys'
strikes, on the train takes of its locked split (fit_realtime_modal.MODELS),
and write it into Source/DSP/MeasuredHaloOwn.h.

The strings from F6 up have no dampers, and the engine plays each as one tone
at its pitch (fit_realtime_modal.halo_pitches: the strongest peak near the
key's pitch in the other keys' strikes) that every strike sets ringing but
its own key's, whose partials play it. Where none of the key's own
components sits near that pitch they do not: from F7 up the tone is the
second partial of the string an octave below, undamped too, which a strike
sets ringing through the bridge, and below F7 a string of the key's own
unison tuned further off than its partials' lanes reach. The grand's F#7
strikes hold that tone 8.6 Hz under the fundamental from -2 to +2 dB against
it from 1 to 2 s, its A7 strikes 28 Hz under from -15 to -5 dB, and read as
below, 0.4.23's renders held 30 to 43 dB less than the recordings there at
F#7 and 59 to 64 dB less at A7.

Each train take of an undamped recorded pitch whose own series leaves the
string's pitch apart, no lane of any of its partials within RESOLVED of it
(the halo fit's window resolves no nearer component, and the engine takes
the string as played wherever one is), is read as the halo fit reads a
string: its tone through the HALO_TIMES windows (halo_tone). In the key's
own strike a window hears it clear where it stands HALO_CLEAR over the
median from 4 to 20 Hz either side, leaving out what lies within RESOLVED
of the key's own components, and HALO_CLEAR over what those components
alone read there through the same window: each lane of the key's fitted
series within NEAR of the string, at the take's layer and falling at its
own rate, its powers summed. The second test is the one that matters next
to a fundamental: on the Hamamatsu grand's C7 the tone 5 Hz from the
fundamental read as loud in the recording as in the engine's render, the
fundamental's first sidelobe in both, and nowhere over it.

As the halo fit has it (fit_realtime_modal.halo_data), brought back to
contact at the string's rate, a layer's level is the mean over its clear
windows if two or more; otherwise the take only bounds it, at the 1 s
window's tone, where that stands HALO_CLEAR over the key's own components
(where it does not, what is there is theirs and bounds nothing). A recorded
pitch the series fit leaves uncalibrated (fit_realtime_modal.UNCALIBRATED)
has no fitted series to tell its own components from the string, so each of
its layers only bounds it, at the 1 s window's tone. The grand's C8 is one:
its strikes hold a tone at the string's pitch 140 Hz and more from their
strongest components, 39 to 46 dB under the take, and holding A7's level
there instead played it 11 to 20 dB over them. The string grows with the
strike at the halo fit's slope, or at its pitch's own where SLOPED layers or
more ring it clear: the grand's F#7 at 1.09 dB per dB and its A7 at 1.85,
where the halo fit's 1.48 held their softest layers' strings 4.9 dB too
quiet at F#7 and 8.3 dB too loud at A7. Its level at the pitch's loudest
layer, and its own slope, are fitted over the layers, the hidden ones as
bounds (a censored fit with one spread), and where fewer than two layers
ring clear it is HALO_HIDDEN under their median bound, never over the
tightest, a layer that rings clear bounding it at its level: the Hamburg
grand's F7 rings clear only at its softest layer, 18 dB under where the
loud layers' bounds alone put it. A pitch whose takes neither ring the
string clear nor bound it has its own components playing what is there,
and so has every pitch that leaves the string no room.

Between the recorded pitches each key takes the levels of the pitches
around it, interpolated by key where both have one and held from the one
that does otherwise; a key between two pitches whose own components play
their strings has none, as has a key past such a pitch at the ends. The
engine then plays a key's own string only where its own series, as it
builds it, leaves the string's pitch apart (KeyraEngine.cpp, strike()).

The dev takes of the measured pitches score the fitted levels: scored,
never fitted.

  python3 Tools/fit_halo_own.py           # measure every piano, write the header and the receipt
  python3 Tools/fit_halo_own.py --check   # the receipt is current and the header is the one it gives
"""
from __future__ import annotations

import argparse
import json
import math
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import numpy as np
from scipy import optimize, stats

import fit_halo_beats as beats
import fit_realtime_modal as fit
import import_modal_measurements as imm
import piano_analysis as pa

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / 'Source/DSP/MeasuredHaloOwn.h'
RECEIPT = ROOT / 'Docs/research/halo-own-2026-11-05.json'
PIANOS = beats.PIANOS
RESOLVED = 4.0    # Hz: the 0.5 s Hann window's main lobe, where halo_tone's floor begins
NEAR = 40.0       # Hz: the key's own components whose leakage is read at the string
SILENT = -200.0   # dB: no own string
SLOPED = 3        # layers ringing the string clear, the fewest that time its own slope
SLOPES = (0.0, 3.0)  # dB per dB: that slope's bounds, the halo fits' 1.2 to 2.0 well inside
DB = 20 / math.log(10)
TAU = np.linspace(-.25, .25, 4001)   # s: the halo fit's 0.5 s window
WINDOW = np.hanning(len(TAU))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def stiff(anchor, order, cents):
    return order * anchor['f1'] * math.sqrt((1 + anchor['B'] * order * order) / (1 + anchor['B'])) * 2 ** (cents / 1200)


def components(anchor, hz):
    """The lanes of the anchor's partials and extras within NEAR of `hz`, as
    (frequency, rate, levels by layer), and how far the nearest partial's
    lane lies from it."""
    near, nearest = [], math.inf
    for kind in ('partials', 'extras'):
        for p in anchor[kind]:
            base = stiff(anchor, p['order'], p['cents'])
            for lane in p['lanes']:
                f = base + lane['offset_hz']
                if kind == 'partials':
                    nearest = min(nearest, abs(f - hz))
                if abs(f - hz) < NEAR:
                    near.append((f, lane['rate'], list(lane['level_db'])))
    return near, nearest


def leakage(near, velocity, grid, hz, centre):
    """What the components alone read at `hz` through the 0.5 s Hann window
    centred `centre` s after contact (dB): the largest within 1 Hz of their
    summed powers, each falling at its own rate from its level at the take's
    velocity."""
    g = hz + np.arange(-1, 1.0001, .25)
    power = np.zeros_like(g)
    for f, rate, levels in near:
        shape = WINDOW * np.exp(-rate * TAU)
        response = np.abs(np.exp(-2j * np.pi * np.outer(g - f, TAU)) @ shape) / np.sum(WINDOW)
        power += (10 ** (np.interp(velocity, grid, levels) / 20) * math.exp(-rate * centre) * response) ** 2
    return 10 * math.log10(np.max(power) + 1e-30)


def take(args):
    """One take's string: per HALO_TIMES window the tone brought back to
    contact (dB), whether it rings clear, and whether it stands over the
    key's own components."""
    path, velocity, hz, rate, near, grid = args
    sr, x = pa.load(path)
    start = pa.onset(x, sr)
    delay = pa.contact_delay(x, sr, start)
    spectra = fit.halo_spectra({'layers': [{'start': start, 'delay': delay}], 'cases': [path.stem]}, 0,
                               [(c, .5) for c in fit.HALO_TIMES], path.parent)
    rows = []
    for centre, (f, z) in zip(fit.HALO_TIMES, spectra):
        if z is None:
            rows.append(None)
            continue
        tone = fit.halo_tone(f, z, hz)[0]
        d = np.abs(f - hz)
        power = np.mean(np.abs(z) ** 2, axis=1)
        apart = np.all(np.abs(f[:, None] - np.array([c[0] for c in near] or [math.inf])[None, :]) > RESOLVED, axis=1)
        floor = 10 * math.log10(np.median(power[(d >= 4) & (d <= 20) & apart]) + 1e-30)
        over = tone - leakage(near, velocity, grid, hz, centre) >= fit.HALO_CLEAR
        rows.append({'back': tone + DB * rate * centre, 'over': bool(over), 'clear': bool(over and tone - floor >= fit.HALO_CLEAR)})
    return rows


def layer(rows, fitted=True):
    """A layer's level (clear in two windows or more) or bound (dB, at
    contact), as halo_data reads them; only a bound where the key has no
    fitted series."""
    clear = [r['back'] for r in rows if r and r['clear']]
    if fitted and len(clear) >= 2:
        return {'level': float(np.mean(clear)), 'clear_windows': len(clear)}
    first = rows[0]
    return {'bound': float(first['back']) if first and (first['over'] or not fitted) else None,
            'clear_windows': len(clear)}


def loudest(xs, layers, slope):
    """The string's level at the pitch's loudest layer, the slope (dB per dB
    of the layers' level `xs`) it grows at and its kind: fitted to the layers
    that ring clear with the others as bounds, the slope with it where SLOPED
    or more ring and the halo fit's `slope` otherwise; HALO_HIDDEN under the
    bounds where fewer than two ring (one that rings bounding it at its
    level), or none where nothing bounds it."""
    levels = np.array([L.get('level', np.nan) for L in layers])
    bounds = np.array([np.nan if L.get('bound') is None else L['bound'] for L in layers])
    rang, bounded = np.isfinite(levels), np.isfinite(bounds)
    if rang.sum() >= 2:
        own = bool(rang.sum() >= SLOPED)
        def loss(p):
            s, spread = p[2] if own else slope, math.exp(p[1])
            return -(np.sum(stats.norm.logpdf(levels[rang] - s * xs[rang], p[0], spread))
                     + np.sum(stats.norm.logcdf((bounds[bounded] - s * xs[bounded] - p[0]) / spread)))
        fitted = optimize.minimize(loss, [float(np.mean(levels[rang] - slope * xs[rang])), math.log(3)] + [slope] * own,
                                   method='L-BFGS-B', bounds=[(-200, 40), (math.log(.5), math.log(20))] + [SLOPES] * own)
        return float(fitted.x[0]), float(fitted.x[2]) if own else slope, 'clear'
    caps = np.concatenate([bounds[bounded] - slope * xs[bounded], levels[rang] - slope * xs[rang]])
    if len(caps):
        return float(min(np.median(caps) - fit.HALO_HIDDEN, np.min(caps))), slope, 'under'
    return None, slope, 'played'


def by_key(pitches):
    """Each undamped key's level (dB at the loudest layer) from the recorded
    pitches' (None where the key's own components play the string)."""
    notes = sorted(pitches)
    out = []
    for key in fit.UNDAMPED:
        lo = max([n for n in notes if n <= key], default=notes[0])
        hi = min([n for n in notes if n >= key], default=notes[-1])
        a, b = pitches[lo], pitches[hi]
        if a is None or b is None or lo == hi:
            level = a if b is None else b if a is None else a
        else:
            level = a + (b - a) * (key - lo) / (hi - lo)
        out.append(SILENT if level is None else level)
    return out


def measure_piano(name, pool):
    model = fit.MODELS[name]
    inputs = dict(header=rel(model['header']), header_sha256=fit.sha256(model['header']),
                  split=rel(model['split']), split_sha256=fit.sha256(model['split']),
                  corpus=rel(model['corpus']), corpus_sha256=fit.sha256(model['corpus']))
    table = imm.load(model['header'])
    grid, layer_level = np.array(table['grid'], float), np.array(table['layer_level'], float)
    pitches = beats.halo_pitches(table)
    rates = dict(zip(table['halo']['keys'], table['halo']['rates']))
    anchors = {a['note']: a for a in table['anchors'] if a['note'] in fit.UNDAMPED}
    roles = json.loads(model['split'].read_text())['cases']
    corpus = {f['id']: f for f in json.loads(model['corpus'].read_text())['files']}
    strings = fit.string_pitches({a['note']: a['f1'] for a in table['anchors']})
    takes = {}
    for case, role in sorted(roles.items()):
        if role in ('train', 'dev') and corpus[case]['kind'] == 'note':
            takes.setdefault(corpus[case]['midi'], []).append((case, fit.layer_velocity(corpus[case]), role))
    uncalibrated = [note for note in fit.UNDAMPED if note in model['uncalibrated'] and note in takes]
    measured = {}
    for note in sorted(set(anchors) | set(uncalibrated)):
        anchor = anchors.get(note)
        hz = pitches[note]
        near, nearest = components(anchor, hz) if anchor else ([], None)
        slope = table['halo']['slope'] + table['halo']['rise'] * math.log2(max(1.0, hz / (anchor['f1'] if anchor else strings[note])))
        record = {'hz': hz, 'nearest_lane_hz': nearest, 'slope': slope}
        if anchor and nearest <= RESOLVED:
            measured[note] = record | {'kind': 'played', 'level': None}
            continue
        cases = sorted(takes[note], key=lambda c: (c[2] != 'train', c[1]))
        reads = pool.map(take, [(model['wav'] / f'{case}.wav', v, hz, rates[note], near, grid) for case, v, _ in cases])
        layers = [{'case': case, 'role': role, 'velocity': v, 'x': float(np.interp(v, grid, layer_level))} | layer(rows, bool(anchor))
                  for (case, v, role), rows in zip(cases, reads)]
        fitted = [L for L in layers if L['role'] == 'train']
        level, grows, kind = loudest(np.array([L['x'] for L in fitted]), fitted, slope)
        if level is not None:
            for L in layers:
                L['predicted'] = level + grows * L['x']
        measured[note] = record | {'kind': kind, 'level': level, 'own_slope': grows, 'layers': layers}
    levels = by_key({note: m['level'] for note, m in measured.items()})
    # How much faster than the halo fit's each key's own string grows, taken
    # between the pitches as the levels are; none where nothing plays it.
    shifts = [0.0 if v == SILENT else v for v in
              by_key({note: m['own_slope'] - m['slope'] if m['level'] is not None else None for note, m in measured.items()})]
    print(f'{name}:', flush=True)
    for note, m in measured.items():
        lane = 'no fitted series' if m['nearest_lane_hz'] is None else f'nearest lane {m["nearest_lane_hz"]:.2f} Hz'
        line = f'  {note}: {m["hz"]:.2f} Hz, {lane}, {m["kind"]}'
        if m['level'] is not None:
            line += f', {m["level"]:+.1f} dB at the loudest layer, {m["own_slope"]:.2f} dB per dB'
        for L in m.get('layers', []):
            if L['role'] == 'dev' and 'predicted' in L and ('level' in L or L.get('bound') is not None):
                read = f'{L["level"]:+.1f}' if 'level' in L else f'under {L["bound"]:+.1f}'
                line += f'; dev {L["case"]} {read} against {L["predicted"]:+.1f}'
        print(line, flush=True)
    print('  by key: ' + ' '.join(f'{k}:{v:.1f}' for k, v in zip(fit.UNDAMPED, levels) if v > SILENT), flush=True)
    return inputs | dict(pitches={str(k): v for k, v in measured.items()}, levels=levels, slope_shifts=shifts)


def header_text(receipt):
    lines = [
        '// Generated by Tools/fit_halo_own.py from the train takes of each piano\'s',
        f'// split ({rel(RECEIPT)}); regenerate, never edit.',
        '// Fitted numbers only: no recorded waveform.',
        '#pragma once',
        '',
        '#include <array>',
        '',
        'namespace keyra { namespace measured {',
        '// A component of a struck key\'s own series this near (Hz) one of its',
        '// undamped strings plays it.',
        f'constexpr float haloOwnResolvedHz={fit.number(RESOLVED)};',
        '// Where a key\'s own series leaves its undamped string\'s pitch apart, the',
        '// level (dB) its strike sets that string ringing at, at its loudest layer',
        '// and at contact, as the halo fit reads a string (haloLevels); -200 where',
        '// its own components play the string. One per key from F6 up.',
        '// haloOwnSlopeDb: how much faster than every undamped string (dB per dB',
        '// of the strike\'s layer level) the key\'s own string grows with the',
        f'// strike, where its recorded pitch rings it clear in {SLOPED} layers or more.',
    ]
    for name in PIANOS:
        levels = receipt['pianos'][name]['levels']
        lines.append(f'namespace {name} {{')
        lines.append(f'constexpr std::array<float,{len(fit.UNDAMPED)}> haloOwnDb{{{{'
                     + ','.join(fit.number(v) for v in levels) + '}};')
        lines.append(f'constexpr std::array<float,{len(fit.UNDAMPED)}> haloOwnSlopeDb{{{{'
                     + ','.join(fit.number(v) for v in receipt['pianos'][name]['slope_shifts']) + '}};')
        lines.append('}')
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
            raise SystemExit(f'{rel(RECEIPT)} predates the current {", ".join(sorted(stale))}: run Tools/fit_halo_own.py')
        if HEADER.read_text() != header_text(receipt):
            raise SystemExit(f'{rel(HEADER)} differs from {rel(RECEIPT)}: run Tools/fit_halo_own.py')
        print(f'{rel(HEADER)} matches {rel(RECEIPT)}')
        return
    with ProcessPoolExecutor(args.jobs) as pool:
        pianos = {name: measure_piano(name, pool) for name in PIANOS}
    receipt = dict(tool=rel(Path(__file__)), tool_sha256=fit.sha256(Path(__file__)),
                   protocol=dict(resolved_hz=RESOLVED, near_hz=NEAR, halo_times=list(fit.HALO_TIMES),
                                 halo_clear_db=fit.HALO_CLEAR, halo_hidden_db=fit.HALO_HIDDEN,
                                 sloped_layers=SLOPED, slope_bounds=list(SLOPES)),
                   pianos=pianos)
    RECEIPT.write_text(json.dumps(receipt, indent=1) + '\n')
    HEADER.write_text(header_text(receipt))
    print(f'wrote {rel(HEADER)} and {rel(RECEIPT)}')


if __name__ == '__main__':
    main()
