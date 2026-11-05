#!/usr/bin/env python3
"""The keyboard network's partials at every key between two recorded pitches
of the Keyra pianos it plays, written as Source/DSP/MeasuredNetworkKeys.h for
KeyraEngine.cpp to play there in place of blending the two pitches' fits.

The engine plays a key between two recorded pitches by blending their fitted
partials (KeyraEngine.cpp series() and blend()) unless this table holds the
key. This writes, for every such key of the pianos named, what the keyboard
network (Tools/keyboard_network.py) gives it instead, in the engine's own
partial format (MeasuredTypes.h), so that the engine plays the network there
and the fits at the recorded pitches. A key's partials are the orders either
recorded pitch around it holds, up to the engine's highest partial, and each
takes from the network, at the key, the order and each layer's level:

- its lanes' decays, offsets, pickups and levels per layer. The network's
  level input is each layer's level under the loudest, layerLevelDb, the
  same median the network's own layer levels are measured as;
- none of its lanes that decays faster than every lane of the two fits
  around the key at the order: such a lane is silent, and goes last. The
  fitter measures a partial through six periods of its fundamental (82 ms
  at the Hamburg's D2), which smears a lane that falls within a few
  milliseconds over every frame its start reaches, and the network, unlike
  the fitter, pays nothing for a lane's amplitude. So it puts a burst on
  the upper partials that the fits do not hold: from 4 kHz up the
  Hamburg's network decays its fastest lanes at 150 to 410/s where the
  fits' fastest median 9 to 25/s, and from 8 kHz up its recorded pitches
  took 9 to 50 dB more power in their first 50 ms from the network than
  from their fits. Played so, its keys between clicked: from 8 kHz up, the
  5 ms after contact stood up to 46 dB over 20 to 40 ms later (the measure
  of Tests/engine_tests.cpp, which fails 13 dB), where today's engine
  stands at most 6.5 dB on every key, and with those lanes silent at most
  3.5 dB. Kept at the fits' fastest decay instead, the lanes' energy put
  the Hamburg's dev takes further off the recordings than today's engine
  (12.74 against 11.04 dB);
- its levels in the fits' units: the network's times its recording term for
  the piano's library, over the fits' channel gains against the same
  measurements (keyboard_network.py `baseline`);
- and those levels moved by the network's error at the two recorded pitches
  around the key: each partial's power in each channel over the window the
  layers' levels are measured over moves by what the fit at each pitch holds
  over the network's there, written as the keys between the two are (the
  same lanes silent), blended between the two in dB. The first run's
  network stands 13.0 dB rms off the Hamburg's fits at their own pitches,
  per partial, layer and channel, and the engine trims every key towards
  its neighbours' level (initCalibrations), so keys between at the
  network's own level move the recorded pitches too: so written, the
  Hamburg's train takes' level error (Tools/benchmark_recordings.py
  level_db) went from 0.70 to 2.95 dB and its dev takes' from 1.84 to 6.01,
  where moved they stand at 0.69 and 2.21;
- not its tuning or its rise: a partial's cents and rise are the engine's
  between the two pitches (blend()), so that the keys play in tune and
  strike as they do today. The network rises the upper partials ever slower
  with their order, to 0.15 to 0.4 s, where the fits at the same recorded
  pitches have them rise within 22 ms (the grand's C3 and F#3 to their 40th
  partials, velocity 64); and played, a partial stays on the engine's
  per-partial path while it rises, about 16 of its rises: the grand's D#3
  took 2.3 times as long to render;
- not its phases as they stand: the network learns each channel's power,
  which no common turn of a partial's lanes, nor of its right channel,
  changes. Its right channel is turned to the lag the engine moves between
  the two pitches' along the shorter arc (blend(), windowChannels), and its
  lanes together to the nearer pitch's partial at each layer (windowCross),
  so that a strike arrives across the partials as the recorded pitch's does.

Its defaults write the table that ships (WEIGHTS and SHIPPED below):

    python3 -I Tools/write_network_tables.py
    python3 -I Tools/write_network_tables.py --check   # is the header what it writes?
    python3 -I Tools/write_network_tables.py --weights out/network/full --pianos grand hamburg --output <file>
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
import fit_realtime_modal as fit  # noqa: E402
import keyboard_network as kn  # noqa: E402
import piano_analysis as pa  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / 'Source/DSP/MeasuredNetworkKeys.h'
WEIGHTS = ROOT / 'Docs/research/keyboard-network-2026-11-04'   # the run whose tables ship
BASELINE = WEIGHTS / 'baseline.json'
PIANOS = ['grand', 'upright', 'kawai', 'hamburg', 'newyork']   # KeyraEngine.h Piano, in its order
# The pianos that play the network between their recorded pitches: those whose
# dev takes it brought closer to their recordings both in the engine
# (keyboard_network.py engine, the level error) and on most measures of
# Tools/benchmark_recordings.py (Docs/decisions.md, 2026-11-05). With the first
# run's tables the Hamburg's dev takes stand 9.38 dB off in the engine where
# blending leaves them 11.04, and the benchmark has them closer on 7 of its 12
# measures. The grand's stand 7.73 against 7.79, but the benchmark has them
# further off on 6 measures and closer on 5, 8 measures past a tolerance;
# the upright's, the Kawai's and New York's stand further off than blending
# (9.94 against 9.56, 11.13 against 10.56 and 12.36 against 11.65). The second
# run's tables leave the Hamburg's 10.12 off and the others' 7.80, 9.86, 12.44
# and 12.13.
SHIPPED = ['hamburg']
FROM, TO = .05, .75   # KeyraEngine.cpp windowPower: the window the layers' levels are measured over


def load_net(path, names):
    """Exported weights (keyboard_network.export) as the Net they came from."""
    with np.load(path) as f:
        meta = json.loads(str(f['meta']))
        state = {k: torch.from_numpy(f[k]) for k in f.files if k != 'meta'}
    if state['gain'].shape[0] != len(names):
        raise SystemExit(f'{path}: {state["gain"].shape[0]} libraries, the settings give {len(names)}')
    net = kn.Net(meta['pianos'], state['breaks'].tolist(), names, meta['level_slots'], meta['arch'])
    net.load_state_dict(state)
    return net.eval(), meta


# --- the engine's window integrals (KeyraEngine.cpp) ------------------------
# A partial at one layer: its lanes' complex amplitudes (level and phase),
# decay rates (1/s), offsets (Hz) and pickups (left, right).

def at(p, i):
    return {'amp': 10 ** (p['level'][i] / 20) * np.exp(1j * p['phase'][i]), 'rate': p['rate'],
            'offset': p['offset'], 'pickup': (p['left'], p['right'])}


def pairs(x, y):
    """The window's integral of e^(-(r_j + r_k) t) e^(2 pi i (d_j - d_k) t), lane j of x and k of y."""
    c = x['rate'][:, None] + y['rate'][None, :] - 2j * math.pi * (x['offset'][:, None] - y['offset'][None, :])
    return (np.exp(-c * FROM) - np.exp(-c * TO)) / c


def inner(x, y, cx, cy):
    """Channel cx of x times the conjugate of channel cy of y, over the window."""
    u, v = x['amp'] * x['pickup'][cx], y['amp'] * y['pickup'][cy]
    return complex(np.sum(u[:, None] * np.conj(v)[None, :] * pairs(x, y)))


def power(x, c):
    """windowPower in one channel (0 left, 1 right)."""
    return inner(x, x, c, c).real


def channels(x):
    """windowChannels: how far the right channel lags the left, as an angle."""
    return inner(x, x, 0, 1)


def cross(x, y):
    """windowCross: the two partials' inner product, both channels."""
    return inner(x, y, 0, 0) + inner(x, y, 1, 1)


# --- the partials ------------------------------------------------------------

def of_table(p):
    """A fitted partial (import_modal_measurements) as the arrays above use."""
    lanes = p['lanes']
    return {'rate': np.array([L['rate'] for L in lanes], float), 'offset': np.array([L['offset_hz'] for L in lanes], float),
            'left': np.array([L['left'] for L in lanes], complex), 'right': np.array([L['right'] for L in lanes]),
            'level': np.array([L['level_db'] for L in lanes], float).T, 'phase': np.array([L['phase'] for L in lanes], float).T}


@torch.no_grad()
def network(net, piano, library, note, orders, table, gain, f1, B, cents):
    """The network's partials at a key, of `orders`, in the fits' units: one
    dict per order, its levels and phases per layer of the table's grid."""
    grid, levels = np.asarray(table['grid'], float), np.asarray(table['layer_level'], float)
    n, m = len(orders), len(grid)
    order = np.repeat(np.asarray(orders, float), m)
    out = net(torch.full((n * m,), piano, dtype=torch.long), torch.full((n * m,), float(note)),
              torch.from_numpy(order), torch.from_numpy(np.tile(levels, n)))
    hz = pa.stiff(f1, B, order) * 2 ** (np.repeat(cents, m) / 1200)
    record = net.recording(torch.full((n * m,), library, dtype=torch.long), torch.from_numpy(hz)).numpy() / gain
    partials = []
    for k in range(n):
        r = k * m   # the string trunk's figures do not depend on the layer: the first row's stand for all
        theta, lag = out['theta'][r].numpy(), out['lag'][r].numpy()
        left = math.sqrt(2) * np.cos(theta) * record[r, 0]
        right = math.sqrt(2) * np.sin(theta) * lag * record[r, 1]
        share = (np.abs(left) ** 2 + np.abs(right) ** 2) / 2   # back to unit mean channel power
        partials.append({'rate': np.exp(out['log_rate'][r].numpy()), 'offset': out['offset'][r].numpy(),
                         'left': (left / np.sqrt(share)).astype(complex), 'right': right / np.sqrt(share),
                         'level': out['level_db'][r:r + m].numpy() + 10 * np.log10(share)[None, :],
                         'phase': np.angle(out['phase'][r:r + m].numpy())})
    return partials


def fastest(q):
    """A fitted partial's fastest decay rate (1/s)."""
    return max(L['rate'] for L in q['lanes'])


def bound(p, rate):
    """Silence p's lanes that decay faster than `rate` and put them last, so
    that the soft pedal's ranks, which the engine gives a key's lanes in
    their order (fastest first, softBiasAtRank), fall on the lanes that
    sound; how many it silenced."""
    faster = p['rate'] > rate
    p['level'][:, faster] = -200.0
    order = np.r_[np.flatnonzero(~faster), np.flatnonzero(faster)]
    for k in ('rate', 'offset', 'left', 'right'):
        p[k] = p[k][order]
    p['level'], p['phase'] = p['level'][:, order], p['phase'][:, order]
    return int(faster.sum())


def align(p, a, b, t):
    """Turn p's right channel to the lag between a's and b's (either may be
    None), one turn for every layer as its pickups are one, then its lanes
    at each layer to the nearer one's partial."""
    layers = p['level'].shape[0]
    turns = 0j
    for i in range(layers):
        if a is not None and b is not None:
            start, end = np.angle(channels(at(a, i))), np.angle(channels(at(b, i)))
            target = start + t * math.remainder(end - start, 2 * math.pi)
        else:
            target = np.angle(channels(at(a if a is not None else b, i)))
        turns += np.exp(1j * (np.angle(channels(at(p, i))) - target))
    p['right'] = p['right'] * np.exp(1j * np.angle(turns))
    near = a if (t < .5 and a is not None) or b is None else b   # blendLane's nearer anchor, t < .5
    for i in range(layers):
        p['phase'][i] = np.angle(np.exp(1j * (p['phase'][i] + np.angle(cross(at(near, i), at(p, i))))))


def channel_powers(p):
    return np.array([[power(at(p, i), c) for c in (0, 1)] for i in range(p['level'].shape[0])])


def move_power(p, shift):
    """Move p's power in each channel by `shift` (dB, layers x 2): its
    balance by the layers' mean, as its pickups are one for every layer,
    then each layer's level to the total."""
    target = channel_powers(p) * 10 ** (shift / 10)
    right = p['right'] * 10 ** (np.mean(shift[:, 1] - shift[:, 0]) / 20)
    share = (np.abs(p['left']) ** 2 + np.abs(right) ** 2) / 2
    p['left'], p['right'] = p['left'] / np.sqrt(share), right / np.sqrt(share)
    p['level'] = p['level'] + 10 * np.log10(share)[None, :]
    p['level'] = p['level'] + 10 * np.log10(target.sum(1) / channel_powers(p).sum(1))[:, None]


def key_tuning(a, b, t):
    """The engine's f1 and B between two recorded pitches (keyPitch and
    keyStiffness below C7, which is all the recording term needs)."""
    def cents(x):
        return 1200 * math.log2(x['f1'] / (440 * 2 ** ((x['note'] - 69) / 12)))
    note = a['note'] + t * (b['note'] - a['note'])
    f1 = 440 * 2 ** ((note - 69 + (cents(a) + t * (cents(b) - cents(a))) / 100) / 12)
    return f1, math.exp(math.log(a['B']) + t * (math.log(b['B']) - math.log(a['B'])))


def piano_keys(name, net, piano, library, gain, log):
    """Every key strictly between two of the piano's recorded pitches: its
    partials, as (order, cents, rise seconds, rise slope, partial dict),
    lowest order first."""
    table = kn.header_of(name)
    anchors = table['anchors']
    by_order = [{p['order']: p for p in x['partials']} for x in anchors]

    def held_over(x, held, limit):
        """What the fit at a recorded pitch holds over the network there,
        written as the keys beside it are, per order, layer and channel (dB)."""
        orders = sorted(held)
        ours = network(net, piano, library, x['note'], orders, table, gain, x['f1'], x['B'],
                       [held[o]['cents'] for o in orders])
        for o, q in zip(orders, ours):
            bound(q, limit[o])
        return {o: 10 * np.log10(channel_powers(of_table(held[o])) / channel_powers(q)) for o, q in zip(orders, ours)}

    keys, silenced, moved = {}, 0, []
    for lower in range(len(anchors) - 1):
        a, b = anchors[lower], anchors[lower + 1]
        pair = by_order[lower], by_order[lower + 1]
        # The fastest decay either fit holds at each order, which no lane of
        # the keys between them exceeds.
        limit = {o: max(fastest(held[o]) for held in pair if o in held) for o in set(pair[0]) | set(pair[1])}
        residual = [held_over(x, held, limit) for x, held in zip((a, b), pair)]
        moved += [np.ravel(list(r.values())) for r in residual]
        for note in range(a['note'] + 1, b['note']):
            t = (note - a['note']) / (b['note'] - a['note'])
            f1, B = key_tuning(a, b, t)
            orders, cents, rises = [], [], []
            for o in sorted(set(by_order[lower]) | set(by_order[lower + 1])):
                pa_, pb_ = by_order[lower].get(o), by_order[lower + 1].get(o)
                if pa_ and pb_:   # blend(): cents and the log rise mixed, the rise's slope with it
                    c = pa_['cents'] + t * (pb_['cents'] - pa_['cents'])
                    rise = (math.exp(math.log(pa_['rise_seconds']) + t * (math.log(pb_['rise_seconds'])
                                                                         - math.log(pa_['rise_seconds']))),
                            pa_['rise_slope'] + t * (pb_['rise_slope'] - pa_['rise_slope']))
                else:
                    q = pa_ or pb_
                    c, rise = q['cents'], (q['rise_seconds'], q['rise_slope'])
                if pa.stiff(f1, B, o) * 2 ** (c / 1200) > kn.TOP_HZ:   # the engine plays none above it
                    continue
                orders.append(o)
                cents.append(c)
                rises.append(rise)
            ours = network(net, piano, library, note, orders, table, gain, f1, B, cents)
            for o, p in zip(orders, ours):
                pa_, pb_ = by_order[lower].get(o), by_order[lower + 1].get(o)
                silenced += bound(p, limit[o])
                ra, rb = residual[0].get(o), residual[1].get(o)
                move_power(p, ra + t * (rb - ra) if ra is not None and rb is not None
                           else ra if ra is not None else rb)
                align(p, of_table(pa_) if pa_ else None, of_table(pb_) if pb_ else None, t)
            keys[note] = [(o, c, r[0], r[1], p) for o, c, r, p in zip(orders, cents, rises, ours)]
    moved = np.concatenate(moved)
    log(f'{name}: the fits over the network at their own pitches, per partial, layer and channel: '
        f'{np.mean(moved):+.2f} dB mean, {np.sqrt(np.mean(moved ** 2)):.2f} dB rms')
    log(f'{name}: {len(keys)} keys between its {len(anchors)} recorded pitches, '
        f'{sum(len(v) for v in keys.values())} partials, {silenced} lanes silent')
    return keys


def lane_text(p, j):
    return ('{' + ','.join(fit.number(x) for x in (p['rate'][j], p['offset'][j], p['left'][j].real,
                                                   p['right'][j].real, p['right'][j].imag))
            + ',{{' + ','.join(fit.number(x) for x in p['level'][:, j])
            + '}},{{' + ','.join(fit.number(x) for x in p['phase'][:, j]) + '}}}')


def header(written, sources):
    made = ('from the keyboard network\'s weights '
            + ', '.join(f'{path} (sha256 {digest[:16]})' for path, digest in sources)
            + '; anchored at the recorded pitches') if sources else \
        'with no piano\'s network: every key plays as the fits give it'
    lines = fit.wrap(f'Generated by Tools/write_network_tables.py {made}; regenerate, never edit.')
    lines += fit.wrap('Each Keyra piano\'s keys between two recorded pitches, which KeyraEngine.cpp plays '
                      'from these partials in place of blending the two pitches\' fits. Fitted numbers '
                      'only: no recorded waveform or impulse response.')
    lines += ['#pragma once', '#include "MeasuredTypes.h"', '',
              'namespace keyra { namespace measured { namespace network {']
    for name in PIANOS:
        keys = written.get(name, {})
        lines.append(f'namespace {name} {{')
        first, rows = 0, []
        for note in range(21, 109):
            count = len(keys.get(note, []))
            rows.append(f'{{{first if count else 0},{count}}}')
            first += count
        lines.append('constexpr std::array<NetworkKey,88> keys{{' + ','.join(rows) + '}};')
        if not first:
            lines += ['constexpr std::array<Partial,0> partials{};', f'}} // namespace {name}']
            continue
        lines.append(f'constexpr std::array<Partial,{first}> partials{{{{')
        for note in sorted(keys):
            lines.append(f'  // MIDI {note}')
            for order, cents, rise, slope, p in keys[note]:
                lines.append(f'  {{{order},' + ','.join(fit.number(x) for x in (cents, rise, slope))
                             + ',{{' + ','.join(lane_text(p, j) for j in range(4)) + '}}},')
        lines += ['}};', f'}} // namespace {name}']
    lines += ['}}} // namespace keyra::measured::network', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--weights', default=str(WEIGHTS), help='a keyboard network run folder holding <setting>-<piano>.npz')
    parser.add_argument('--setting', default='character', choices=['character', 'smooth'])
    parser.add_argument('--pianos', nargs='*', default=SHIPPED, choices=PIANOS,
                        help='pianos to write; the rest, or all with none named, blend their recorded pitches')
    parser.add_argument('--baseline', default=str(BASELINE), help='the fits\' channel gains (keyboard_network.py baseline)')
    parser.add_argument('--output', default=str(HEADER))
    parser.add_argument('--check', action='store_true', help='fail unless the output is what this writes')
    args = parser.parse_args()
    torch.set_num_threads(1)   # one thread sums alike from run to run
    weights = Path(args.weights)
    config = kn.load_config()
    alone = json.loads((weights / 'run.json').read_text()).get('alone', False)
    names = [n for n, i in config['libraries'].items() if i.get('keyra') or not alone]
    baseline = json.loads(Path(args.baseline).read_text())
    written, sources = {}, []
    for name in args.pianos:
        path = weights / f'{args.setting}-{name}.npz'
        net, meta = load_net(path, names)
        gain = 10 ** (np.asarray(baseline[name]['gain_db']) / 20)
        written[name] = piano_keys(name, net, meta['pianos'].index(name), names.index(name), gain, print)
        shown = path.resolve().relative_to(ROOT) if path.resolve().is_relative_to(ROOT) else path
        sources.append((str(shown), hashlib.sha256(path.read_bytes()).hexdigest()))
    text = header(written, sources)
    output = Path(args.output)
    if args.check:
        if not output.exists() or output.read_text() != text:
            raise SystemExit(f'{output} is not what Tools/write_network_tables.py writes: regenerate it')
        print(f'{output} is current')
        return
    output.write_text(text)
    print(f'wrote {output} ({len(text) / 1e6:.1f} MB)')


if __name__ == '__main__':
    main()
