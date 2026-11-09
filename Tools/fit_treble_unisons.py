#!/usr/bin/env python3
"""Measure the treble's strings that each recorded pitch's series leaves out,
on the train takes of each piano's locked split (fit_realtime_modal.MODELS),
and write those of the pianos that play them (PLAYED) into
Source/DSP/MeasuredTrebleUnisons.h.

From C6 up a key's unison strings lie 2 to 7 cents apart, 4 to 12 Hz at its
fundamental. The series fit follows each partial through a window of six
periods of the fundamental, at least 4 ms, whose main lobe holds the whole
unison, and its lanes reach about 3 cents from the partial
(piano_analysis.lane_span), or 10 where one settles at that bound; what they
leave goes into them by the energy gains (fit_realtime_modal.energy_gains).
So the fitted treble beats less than its recordings and sounds from one
place: over 50 ms to 1.5 s the grand's recorded F#7 and A7 keep 0.47 to 0.81
of their coherence between channels, where 0.4.25's renders keep 0.91 to 0.99.

Each train take of a recorded pitch from C6 up (LOWEST) is read through a
1.45 s Hann window from 50 ms after contact (SPAN), within the unison reach
of each of its first ORDERS partials (lane_span at UNISON_REACH): the peaks
standing PROMINENCE over their surroundings and within DEPTH of the
strongest there. A component is a peak half the layers or more, and at
least three, hold within TOL of one another. It is the series' within
RESOLVE of the partial's own frequency; a component beside the series' (the
fit's extras), the key's own undamped string's where the engine plays that
(MeasuredHaloOwn.h), or that string's where it lies within HALO_UNISON of
another key's undamped string; and a lane's where one of the partial's lanes
lies within RESOLVE of it and falls no faster than twice its rate. Nothing
plays the others: the key's own strings tuned past its lanes, and from F7 up
the second partial of the undamped string an octave down, which the strike
sets ringing through the bridge.

Each is measured as the analysis measures a component beside the series
(piano_analysis.analyse_anchor): through its own Blackman-Harris window,
whose main lobe ends where the nearest other component begins, on the
recording itself, fitted with two lanes across the layers (one where the fit
does not time two apart), its frames weighed against the envelope within
BEAT of them as a partial's are, and carried into the engine's frame and the
header's layers as the fit carries a component beside the series
(fit_realtime_modal.anchor_data and on_grid). The engine plays them as those,
starting in phase with the partial at contact, as the hammer sets every
string of a unison off together, and takes their power over 50 to 750 ms
out of the partial's lanes, which the energy gains matched to the whole
unison (KeyraEngine.cpp, strike()).

  python3 Tools/fit_treble_unisons.py           # measure every piano, write the header and the receipt
  python3 Tools/fit_treble_unisons.py --check   # the receipt is current and the header is the one it gives
"""
from __future__ import annotations

import argparse
import json
import math
import os
import pickle
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import numpy as np
from scipy import signal

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fit_halo_beats as beats
import fit_halo_own as own
import fit_realtime_modal as fit
import import_modal_measurements as imm
import piano_analysis as pa

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / 'Source/DSP/MeasuredTrebleUnisons.h'
RECEIPT = ROOT / 'Docs/research/treble-unisons-2026-11-06.json'
PIANOS = beats.PIANOS
LOWEST = 84            # MIDI: C6
ORDERS = 2             # partials searched
SPAN = (.05, 1.5)      # s after contact: the long window
RESOLVE = 1.5          # Hz: that window's main lobe (2 / 1.45 s), the nearest two components it parts
PROMINENCE = 10.0      # dB over a peak's surroundings
DEPTH = 20.0           # dB under the strongest peak within the reach, the deepest counted
TOL = .6               # Hz: one component's peak from layer to layer
PAD = 1 << 21          # FFT length
SILENT = -110.0        # dB: a lane no louder at any layer is left out, as the fit leaves out such a component
BEAT = .3              # s: each frame weighed against the envelope this near it, as the partials' are
# The pianos whose header plays their strings. Scored by benchmark_recordings
# against 0.4.25, each measure's mean change from C6 up in compare_benchmarks'
# tolerance and summed, level aside, the grand's train and dev takes come
# closer with them by 1.01 and 1.04, the upright's by 0.37 and 2.25 and New
# York's by 1.15 and 0.06; the Hamamatsu's and the Hamburg's train takes stand
# further, +0.43 and +1.74, and none of their dev takes changes. Those two are
# measured and not played (Docs/research/treble-unisons-2026-11-06.md).
PLAYED = ['grand', 'upright', 'newyork']


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def contact(L, sr):
    return L['start'] + int(round(L['delay'] * sr))


def peaks(x, sr, at, hz, reach):
    """The peaks of one take within `reach` of `hz` through the SPAN window
    from sample `at`: (offset Hz, dB under the strongest there, right over
    left)."""
    seg = x[at + int(SPAN[0] * sr):at + int(SPAN[1] * sr)]
    S = np.fft.rfft(seg * np.hanning(len(seg))[:, None], PAD, axis=0)
    f = np.fft.rfftfreq(PAD, 1 / sr)
    sel = np.flatnonzero(np.abs(f - hz) < reach)
    db = 10 * np.log10(np.sum(np.abs(S[sel]) ** 2, axis=1) + 1e-30)
    k, _ = signal.find_peaks(db, prominence=PROMINENCE)
    k = k[db[k] >= db.max() - DEPTH]
    return [(float(f[sel[q]] - hz), float(db[q] - db.max()), complex(S[sel[q], 1] / (S[sel[q], 0] + 1e-30))) for q in k]


def components(hits, layers):
    """The peaks (offset, dB, ratio, layer) that at least half the layers, and
    three, hold within TOL of one another, strongest first; of two within
    RESOLVE, which the window does not part, the stronger."""
    hits = sorted(hits, key=lambda h: h[0])
    groups, current = [], []
    for h in hits:
        if current and h[0] - current[-1][0] > TOL:
            groups.append(current)
            current = []
        current.append(h)
    if current:
        groups.append(current)
    need = max(3, math.ceil(layers / 2))
    found = []
    for g in groups:
        held = sorted({h[3] for h in g})
        if len(held) < need:
            continue
        ratio = np.median([h[2] for h in g])
        found.append({'offset_hz': float(np.median([h[0] for h in g])), 'db': float(np.median([h[1] for h in g])),
                      'layers': len(held), 'ild_db': float(20 * math.log10(max(abs(ratio), 1e-6))),
                      'phase_deg': float(np.degrees(np.angle(ratio)))})
    kept = []
    for c in sorted(found, key=lambda c: -c['db']):
        if all(abs(c['offset_hz'] - k['offset_hz']) > RESOLVE for k in kept):
            kept.append(c)
    return kept


def owner(c, hz, note, beside, own_hz, halo_hz):
    """What plays the component at `hz` already, apart from the partial's
    lanes, or None."""
    if abs(c['offset_hz']) <= RESOLVE:
        return 'series'
    f = hz + c['offset_hz']
    if any(abs(f - e) <= RESOLVE for e in beside):
        return 'beside'
    if own_hz is not None and abs(f - own_hz) <= RESOLVE:
        return 'own string'
    for key, h in halo_hz.items():
        if key != note and abs(1200 * math.log2(f / h)) <= fit.HALO_UNISON:
            return f'string {key}'
    return None


def measure(x, L, sr, f1, hz, window):
    """One take's envelope at `hz` through its own window of `window`
    samples, as analyse_anchor measures a component beside the series."""
    step = max(window / sr / 8, .02)
    t, z = pa.envelopes(x, sr, [hz], f1, L['start'], None, times=np.arange(0, L['horizon'], step), length=window)
    power_db = 10 * np.log10(np.maximum(np.mean(np.abs(z[0]) ** 2, axis=0), 1e-30))
    floor = float(pa.envelope_floor(t, power_db[None])[0])
    return {'times': t - L['delay'], 'z': z[0], 'power_db': power_db, 'floor_db': floor, 'velocity': L['velocity']}


def anchor(args):
    """One recorded pitch's strings beside its series, in the header's frame
    on its own layers, and what the search found at each partial."""
    name, note = args
    model = fit.MODELS[name]
    table = imm.load(model['header'])
    halo_hz = beats.halo_pitches(table)
    receipt = json.loads(own.RECEIPT.read_text())['pianos'][name]
    own_hz = dict(zip(fit.UNDAMPED, [halo_hz[k] if level > own.SILENT else None
                                     for k, level in zip(fit.UNDAMPED, receipt['levels'])]))
    with (model['cache'] / f'{note}.pkl').open('rb') as f:
        result = pickle.load(f)
    a = next(a for a in table['anchors'] if a['note'] == note)
    sr, f1 = result['sr'], result['f1']
    takes = [pa.load(L['path'])[1] for L in result['layers']]
    beside = [own.stiff(a, e['order'], e['cents']) + e['lanes'][0]['offset_hz'] for e in a['extras']]
    searched, new = [], []
    for k, (n, hz) in enumerate(zip(result['orders'], result['freqs'])):
        p = next((p for p in a['partials'] if p['order'] == n), None)
        if n > ORDERS or p is None or hz > .45 * sr:
            continue
        reach = pa.lane_span(n, hz, pa.UNISON_REACH)
        hits = [h + (i,) for i, (L, x) in enumerate(zip(result['layers'], takes))
                if contact(L, sr) + int(SPAN[1] * sr) <= len(x) for h in peaks(x, sr, contact(L, sr), hz, reach)]
        found = components(hits, len(result['layers']))
        for c in found:
            c['owner'] = owner(c, hz, note, beside, own_hz.get(note), halo_hz)
        others = [hz + c['offset_hz'] for c in found] + list(result['freqs']) + beside \
            + [h for h in halo_hz.values() if abs(h - hz) < 2 * reach]
        for c in found:
            if c['owner']:
                continue
            f = hz + c['offset_hz']
            gap = max(RESOLVE, min(abs(o - f) for o in others if abs(o - f) > 1e-9))
            window = max(pa.window_length(f1, sr), 2 * round(2 * sr / gap))
            measured = [measure(x, L, sr, f1, f, window) for L, x in zip(result['layers'], takes)]
            # Two lanes, as the analysis fits a component where an undamped
            # string may ring: the strings' quick early fall and their slow
            # ringing on. Fitted with one, F#7's strings beside its series
            # fell at 4 to 7 per second, where through their own windows
            # they fell at 2 to 4 after the first half second.
            # Two lanes are one where the fit gives them the same rate and
            # pitch (the grand's F#7, its nearest string), and a lane left at
            # the slowest rate the fit allows was not timed (pa.SLOWEST_RATE):
            # the New York's G#7 left one there at -76 dB in its loudest
            # layer, which would have rung on for half an hour.
            lane = None
            for count in (2, 1):
                lane = pa.fit_partial_layers(measured, f1, sr, max(1, int(round(f / f1))), f, lanes=count,
                                             beat=BEAT, length=window, rise=False)
                if lane is not None:
                    rates, offsets = np.exp(lane['theta'][:count]), lane['theta'][count:2 * count]
                    apart = count == 1 or abs(math.log(rates[0] / rates[1])) > .01 or abs(offsets[0] - offsets[1]) > .01
                    if np.all(np.abs(offsets) <= RESOLVE) and np.all(rates > 1.001 * pa.SLOWEST_RATE) and apart:
                        break
                lane = None
            if lane is None:
                c['owner'] = 'no fit at its pitch'
                continue
            count = (len(lane['theta']) - 2) // 2
            rates = np.exp(lane['theta'][:count])
            near = [L for L in p['lanes'] if abs(L['offset_hz'] - c['offset_hz']) <= RESOLVE and L['rate'] <= 2 * rates.min()]
            if near:
                c['owner'] = 'lane'
                continue
            c.update(rates=rates.tolist(), window_s=window / sr)
            new.append((c, f, lane, [float(m['power_db'].max()) for m in measured], [m['floor_db'] for m in measured]))
        searched.append({'order': int(n), 'hz': float(hz), 'reach_hz': float(reach), 'components': found})
    data = None
    if new:
        # Carried into the header's frame by the fit itself, as its own
        # components beside the series.
        mod = dict(result, extra_freqs=np.array([f for _, f, *_ in new]), extra_halo=np.zeros(len(new), bool),
                   extra_fits=[lane for _, _, lane, *_ in new], ring_fits=[None] * len(new),
                   layers=[dict(L, extra_peak_db=np.array([c[3][i] for c in new]),
                                extra_floor_db=np.array([c[4][i] for c in new]))
                           for i, L in enumerate(result['layers'])])
        data = fit.anchor_data(mod, halo_hz, model['wav'])
    return note, searched, data


def on_grid(model, data, grid, layer_level):
    """The components carried onto the header's layers as on_grid carries an
    anchor's components beside the series."""
    v = list(data['velocities'])
    top = float(layer_level[-1] - layer_level[-2]) if model.get('carried_top') else None
    for e in data['extras']:
        for lane in e['lanes']:
            if v != list(grid):
                def at(db, g):
                    if top is not None and g > v[-1]:
                        return float(db[-1]) + top * (g - v[-1]) / (grid[-1] - v[-1])
                    return fit.level_at(v, db, g)
                lane['level_db'] = np.array([at(lane['level_db'], g) for g in grid])
                lane['phase'] = np.array([fit.phase_at(v, lane['phase'], g) for g in grid])
    return data['extras']


def measure_piano(name, pool):
    model = fit.MODELS[name]
    inputs = dict(header=rel(model['header']), header_sha256=fit.sha256(model['header']),
                  split=rel(model['split']), split_sha256=fit.sha256(model['split']),
                  corpus=rel(model['corpus']), corpus_sha256=fit.sha256(model['corpus']),
                  halo_own=rel(own.RECEIPT), halo_own_sha256=fit.sha256(own.RECEIPT))
    table = imm.load(model['header'])
    grid, layer_level = np.array(table['grid'], float), np.array(table['layer_level'], float)
    anchors = fit.train_anchors(model)
    notes = [note for note in anchors if note >= LOWEST]
    keys = {}
    for note in notes:
        with (model['cache'] / f'{note}.pkl').open('rb') as f:
            key = pickle.load(f).get('cache_key')
        if key != fit.cache_key(anchors[note], fit.analysis_options(model)):
            raise SystemExit(f'{name} {note}: its analysis was made from other inputs: run fit_realtime_modal.py --analyse')
        keys[str(note)] = key
    pitches = {}
    for note, searched, data in pool.map(anchor, [(name, note) for note in notes]):
        extras = on_grid(model, data, grid, layer_level) if data else []
        pitches[str(note)] = {'searched': searched, 'unisons': [
            {'order': e['order'], 'cents': e['cents'], 'error': e['error'],
             'lanes': [{k: (v.tolist() if isinstance(v, np.ndarray) else v) for k, v in L.items() if k != 'right'}
                       | {'right': [L['right'].real, L['right'].imag]}
                       for L in e['lanes'] if max(L['level_db']) >= SILENT]} for e in extras]}
    print(f'{name}:', flush=True)
    for note, m in pitches.items():
        for s in m['searched']:
            line = ', '.join(f'{c["offset_hz"]:+.2f} Hz {c["db"]:+.1f} dB {c["owner"] or "unplayed"}' for c in s['components'])
            print(f'  {note} n{s["order"]} at {s["hz"]:.2f} Hz: {line}', flush=True)
        for u in m['unisons']:
            print(f'    plays n{u["order"]} {u["cents"]:+.2f} cents: ' + ', '.join(
                f'{L["offset_hz"]:+.2f} Hz {L["rate"]:.2f}/s {max(L["level_db"]):+.1f} dB' for L in u['lanes']), flush=True)
    return inputs | dict(analysis_cache_keys=keys, pitches=pitches)


def header_text(receipt):
    lines = [
        '// Generated by Tools/fit_treble_unisons.py from the train takes of each',
        f'// piano\'s split ({rel(RECEIPT)}); regenerate, never edit.',
        '// Fitted numbers only: no recorded waveform.',
        '#pragma once',
        '',
        '#include <array>',
        '#include "MeasuredTypes.h"',
        '',
        'namespace keyra { namespace measured {',
        '// A recorded pitch\'s strings beside its series that it plays nowhere',
        '// else: its unison strings tuned past its lanes, and the undamped string',
        '// an octave down at its second partial; first and count in unisons.',
        'struct UnisonAnchor { int note, first, count; };',
    ]
    for name in PIANOS:
        pitches = receipt['pianos'][name]['pitches'] if name in receipt['played'] else {}
        rows, extras = [], []
        for note, m in pitches.items():
            if m['unisons']:
                lanes = sum(len(u['lanes']) for u in m['unisons'])
                rows.append(f'{{{note},{sum(len(u["lanes"]) for _, u in extras)},{lanes}}}')
                extras += [(note, u) for u in m['unisons']]
        lines.append(f'namespace {name} {{')
        if not rows:
            lines += ['constexpr std::array<UnisonAnchor,0> unisonAnchors{};',
                      'constexpr std::array<Extra,0> unisons{};', '}']
            continue
        lines.append(f'constexpr std::array<UnisonAnchor,{len(rows)}> unisonAnchors{{{{' + ','.join(rows) + '}};')
        lines.append(f'constexpr std::array<Extra,{sum(len(u["lanes"]) for _, u in extras)}> unisons{{{{')
        last = None
        for note, u in extras:
            if note != last:
                lines.append(f'  // MIDI {note}')
                last = note
            for L in u['lanes']:
                lines.append(f'  {{{u["order"]},{fit.number(u["cents"])},{{'
                             + ','.join(fit.number(v) for v in (L['rate'], L['offset_hz'], L['left'], *L['right']))
                             + ',{{' + ','.join(fit.number(v) for v in L['level_db']) + '}}'
                             + ',{{' + ','.join(fit.number(v) for v in L['phase']) + '}}}},')
        lines += ['}};', '}']
    lines += ['}}', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--check', action='store_true', help='check the receipt against the tool, its inputs and the header, and exit')
    parser.add_argument('--jobs', type=int, default=2, help='recorded pitches measured at once')
    parser.add_argument('--pianos', nargs='+', choices=PIANOS, default=PIANOS, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.check:
        receipt = json.loads(RECEIPT.read_text())
        stale = {rel(Path(__file__))} if receipt['tool_sha256'] != fit.sha256(Path(__file__)) else set()
        for measured in receipt['pianos'].values():
            stale |= {measured[k] for k in ('header', 'split', 'corpus', 'halo_own')
                      if measured[f'{k}_sha256'] != fit.sha256(ROOT / measured[k])}
        if stale:
            raise SystemExit(f'{rel(RECEIPT)} predates the current {", ".join(sorted(stale))}: run Tools/fit_treble_unisons.py')
        if HEADER.read_text() != header_text(receipt):
            raise SystemExit(f'{rel(HEADER)} differs from {rel(RECEIPT)}: run Tools/fit_treble_unisons.py')
        print(f'{rel(HEADER)} matches {rel(RECEIPT)}')
        return
    with ProcessPoolExecutor(args.jobs) as pool:
        pianos = {name: measure_piano(name, pool) for name in args.pianos}
    receipt = dict(tool=rel(Path(__file__)), tool_sha256=fit.sha256(Path(__file__)),
                   protocol=dict(lowest=LOWEST, orders=ORDERS, span_s=list(SPAN), resolve_hz=RESOLVE,
                                 prominence_db=PROMINENCE, depth_db=DEPTH, tolerance_hz=TOL,
                                 unison_reach=pa.UNISON_REACH, halo_unison_cents=fit.HALO_UNISON),
                   played=PLAYED, pianos=pianos)
    if args.pianos != PIANOS:
        print(json.dumps(receipt, indent=1)[:2000])
        return
    RECEIPT.write_text(json.dumps(receipt, indent=1) + '\n')
    HEADER.write_text(header_text(receipt))
    print(f'wrote {rel(HEADER)} and {rel(RECEIPT)}')


if __name__ == '__main__':
    main()
