#!/usr/bin/env python3
"""Measure the strike's knock under 400 Hz on the train takes of each piano's
locked split (fit_realtime_modal.MODELS) and write Source/DSP/MeasuredLowKnock.h.

The hammer's blow reaches the board through the bridge, and the board and
case answer it with a knock that falls faster than the body's modes ring.
fit_realtime_modal measures that knock from 400 Hz up (its KNOCK_BANDS) and
fits the body's modes from 20 ms after contact (BODY_SKIP), so under 400 Hz
nothing played it: aligned at the strike, the train notes from C6 up stood a
median 1 to 12 dB under their recordings from 160 to 315 Hz over their first
30 ms on every piano, at 0.4.27's engine (Docs/research/low-knock-2026-11-09.md).

Each take is aligned at its strike, the first 1 ms frame within 20 dB of its
loudest up to 0.2 s after its onset, and so is its render through the engine
without this knock (--no-low-knock) at its layer's velocity, scaled to the
recording as benchmark_recordings scores it (its early RMS). In each band of
BANDS whose upper edge lies a third of an octave or more under the take's
fundamental, where no partial sounds, both pass through the engine's band
filter (three pole pairs, prepareNoise in KeyraEngine.cpp), in 5 ms frames
from the strike to 0.5 s after it: benchmark_recordings' attack window (to
0.1 s) and its early window (on to 0.5 s), which the fit weighs alike. The
knock is the engine's band noise under an envelope A e^(-rt) (1 - e^(-t/rise))
from contact, as the engine plays it: its source through the band's filters,
stationary from the start (prepareNoiseStates), under the envelope, and
through the filters again to measure it, its expected power per frame worked
out exactly through the filters' joint state (knock_shapes); and with it what
the engine's room returns of it, which hears the knock as it hears the
strike's noise (room_echo). The fit compares, in dB, the recording's power
with the render's plus the knock's, each held up to 30 dB under the
recording's loudest frame, so a knock that would raise the frames the render
already fills, or those the recording leaves quiet, is fitted away.

- The shape: per piano and band, the decay rate of RATES and the rise of
  RISES that fit its takes best together, each take at its own best level:
  the board's damping at a frequency does not follow the key that drives it.
- The level: per pitch and band, under that shape, its density at contact
  (dB re 1/Hz in the recording's scale, as fit_realtime_modal measures the
  knock) as the line in the level its layers play at (layerLevelDb in the
  pitch's header) that fits its takes best, a slope of SLOPES, where at least
  LEVEL_TAKES takes clear the band. A pitch with fewer holds -200 dB there,
  which a key plays only as far as it lies towards a pitch that measures it.
- The balance and coherence: per piano and band, the right channel's power
  over the left's in what the recordings hold beyond their renders, and the
  magnitude of the channels' correlation as analytic signals (as
  fit_realtime_modal measures the knock's), through the frames of the first
  0.1 s where the recording stands 3 dB over its render, over every take.
  They come first: how much of the knock the room hears, its mid, follows
  from them.

  python3 Tools/fit_low_knock.py --renderer build/keyra_render   # measure, write the header and the receipt
  python3 Tools/fit_low_knock.py --check                         # the receipt is current and the header the one it gives
"""
from __future__ import annotations

import argparse
import functools
import json
import math
import os
import re
import subprocess
import tempfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')

import numpy as np
from scipy import linalg, ndimage, signal

import benchmark_recordings as br
import fit_realtime_modal as fit
import fit_room as fr
import piano_analysis as pa

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / 'Source/DSP/MeasuredLowKnock.h'
RECEIPT = ROOT / 'Docs/research/low-knock-2026-11-09.json'
ENGINE = ROOT / 'Source/DSP/KeyraEngine.cpp'
ROOM = ROOT / 'Source/DSP/MeasuredRoom.h'
PIANOS = ('grand', 'upright', 'kawai', 'hamburg', 'newyork')
# Third-octave bands under fit_realtime_modal's lowest knock band (400 Hz).
BANDS = [1000.0 * 2 ** (k / 3) for k in range(-9, -4)]  # 125 to 315 Hz
CLEARANCE = 2 ** (-1 / 3)  # a band's upper edge under the fundamental by this ratio at least
HOP, ATTACK, SPAN = .005, .1, .5  # s: the frames' length, and the ends of benchmark_recordings' attack and early windows
FLOOR = 10 ** (-30 / 10)  # the level, under the recording's loudest frame, that both sides are held at
KNOCK_OVER = 10 ** (3 / 10)  # the frames the balance and coherence come from: the recording 3 dB over the render
RATES = np.geomspace(20., 2000., 31)  # dB/s
RISES = np.array([.0005, .001, .002, .003, .005, .007, .01, .014, .02, .028, .04])  # s
OFFSETS = np.arange(-40., 10.01, .5)  # dB about the density whose knock alone meets a take's loudest frame
SLOPES = np.arange(0., 2.001, .05)  # dB per dB of layer level
LINE_SPAN = np.arange(-12., 12.01, .25)  # dB about the line through the takes' own best levels
LEVEL_TAKES = 3
RENDER_SECONDS = 1.2  # band_frames reads twice SPAN past the strike
DB_PER_NEPER = 20 / math.log(10)


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def header_array(text, name):
    return [float(v) for v in re.search(name + r'\{\{([^}]*)\}\}', text).group(1).replace('f', '').split(',')]


def layer_level(velocity, grid, levels):
    """The level (dB) a velocity's layer plays at, as levelAt in KeyraEngine.cpp."""
    return float(np.interp(velocity, grid, levels))


def strike(x, sr):
    """The first 1 ms frame within 20 dB of the loudest up to 0.2 s after the onset."""
    start = pa.onset(x, sr)
    power = ndimage.uniform_filter1d(np.mean(x * x, axis=1), int(.001 * sr), mode='constant')
    head = power[:start + int(.2 * sr)]
    return int(np.flatnonzero(head >= head.max() * .01)[0])


def early_rms(x, sr, at):
    """The level benchmark_recordings.features matches a render to its recording by."""
    xh = signal.sosfiltfilt(signal.butter(2, 20, 'highpass', fs=sr, output='sos'), x, axis=0)
    early = xh[at + int(.05 * sr):at + int(.75 * sr)]
    return float(np.sqrt(np.mean(early * early)))


def band_filter(f, sr):
    """The engine's noise band: three pole pairs a sixth of an octave either side, prewarped."""
    return signal.butter(3, [f * 2 ** (-1 / 6), f * 2 ** (1 / 6)], 'bandpass', fs=sr, output='sos')


def cascade(sos):
    """A cascade of biquads as one state-space system (A, B, C, D), each section in transposed direct form II."""
    A = B = C = None
    D = 1.
    for b0, b1, b2, _, a1, a2 in sos:
        a, b, c = np.array([[-a1, 1.], [-a2, 0.]]), np.array([b1 - a1 * b0, b2 - a2 * b0]), np.array([1., 0.])
        if A is None:
            A, B, C, D = a, b, c, b0
        else:
            n = len(B)
            A = np.block([[A, np.zeros((n, 2))], [np.outer(b, C), a]])
            B, C, D = np.concatenate([B, b * D]), np.concatenate([b0 * C, c]), b0 * D
    return A, B, C, D


@functools.lru_cache(maxsize=None)
def knock_shapes(f, sr):
    """Per shape (RATES by RISES, rate-major) and per sample from contact, the expected power through the
    band's filter of the engine's knock of unit density (1/Hz): its source (variance sr/2, as the engine
    scales a band's) through the band's filters, stationary from the start, under the envelope, and
    through the filters again. The covariance of the two filters' joint state runs forward exactly."""
    A, B, C, D = cascade(band_filter(f, sr))
    m = len(B)
    t = np.arange(int(round((SPAN + 2 * HOP) * sr))) / sr
    decay, rise = np.repeat(RATES / DB_PER_NEPER, len(RISES)), np.tile(RISES, len(RATES))
    env = np.exp(-decay[:, None] * t) * (1 - np.exp(-t / rise[:, None]))
    count, var = len(env), sr / 2
    P = np.zeros((count, 2 * m, 2 * m))
    P[:, :m, :m] = linalg.solve_discrete_lyapunov(A, var * np.outer(B, B))
    F = np.zeros((count, 2 * m, 2 * m))
    F[:, :m, :m] = F[:, m:, m:] = A
    coupling, through = np.outer(B, C), np.broadcast_to(C, (count, m))
    source = np.broadcast_to(B, (count, m))
    out = np.empty(env.shape)
    for i in range(env.shape[1]):
        e = env[:, i]
        H = np.concatenate([e[:, None] * (D * C)[None], through], axis=1)
        out[:, i] = np.einsum('si,sij,sj->s', H, P, H) + var * (e * D * D) ** 2
        F[:, m:, :m] = e[:, None, None] * coupling
        G = np.concatenate([source, e[:, None] * (B * D)[None]], axis=1)
        P = F @ P @ F.transpose(0, 2, 1) + var * G[:, :, None] * G[:, None, :]
    return out


def room_echo(shapes, room, f, sr):
    """Per shape and sample, the expected power through the band that the engine's room returns of a knock
    whose own power is `shapes` at its input (playRoom in KeyraEngine.cpp): its sixteen lines, fed alike at
    the room's gain over 4, hold the input's energy and give it back, spread among them by the Hadamard
    mixing, at their mean length's share per sample, losing it at the shelf's rate at the band
    (fit_room.shelf_rate) from the shortest line's delay on. Against the engine's own echo of a knock (the
    difference of renders with the room on and off) this incoherent model agreed within 1.1 dB over 0.1 to
    1.4 s in every band, on the Hamburg grand's D#6."""
    low, high, crossover, gain = room
    lengths = np.array(fr.line_lengths(sr))
    a = 10 ** (-float(fr.shelf_rate(f, low, high, crossover, sr)) / (10 * sr))
    first = int(lengths.min())
    drive = np.zeros_like(shapes)
    drive[:, first:] = shapes[:, :-first] * a ** first * (gain * .25) ** 2 / lengths.mean()
    return signal.lfilter([1.], [1., -a], drive, axis=1)


def room_of(model):
    """The room a measured piano's build plays (MeasuredRoom.h): its low and high rates (dB/s), crossover (Hz) and gain."""
    found = re.search(r'namespace ' + model + r' \{ constexpr Room room\{([^}]*)\}', ROOM.read_text())
    return tuple(float(v) for v in found.group(1).replace('f', '').split(','))


def frame_weights():
    """Per frame, its share of its window's weight: the attack window and the early window weigh alike, as
    benchmark_recordings scores them in attack_db and early_db."""
    frames, attack = int(round(SPAN / HOP)), int(round(ATTACK / HOP))
    return np.where(np.arange(frames) < attack, 1 / attack, 1 / (frames - attack))


WEIGHTS = frame_weights()


def shape_frames(shapes, start, sr):
    """The shapes' mean power per frame of a take whose strike lies `start` samples after its contact."""
    hop, frames = int(round(HOP * sr)), int(round(SPAN / HOP))
    at = start + np.arange(hop * frames)
    taken = np.where(at[None, :] >= 0, shapes[:, np.clip(at, 0, None)], 0.)
    return taken.reshape(len(shapes), frames, hop).mean(axis=2)


def band_frames(x, sr, at, f, analytic=False):
    """Per frame from the strike the band's mean power per channel and, `analytic`, the sums of the
    channels' analytic signals' product (left times right's conjugate) and of their squared magnitudes."""
    y = signal.sosfilt(band_filter(f, sr), x, axis=0)
    hop, frames = int(round(HOP * sr)), int(round(SPAN / HOP))
    if at + hop * frames + hop * frames > len(y):
        return None, None
    power = np.mean(y[at:at + hop * frames].reshape(frames, hop, 2) ** 2, axis=1)
    if not analytic:
        return power, None
    lo = max(at - hop * frames, 0)
    z = signal.hilbert(y[lo:at + 2 * hop * frames], axis=0)[at - lo:at - lo + hop * frames].reshape(frames, hop, 2)
    sums = np.stack([np.sum(z[:, :, 0] * np.conj(z[:, :, 1]), axis=1),
                     np.sum(np.abs(z[:, :, 0]) ** 2, axis=1), np.sum(np.abs(z[:, :, 1]) ** 2, axis=1)], axis=1)
    return power, sums


def render(renderer, model, note, velocity, tmp):
    events = Path(tmp) / 'note.events'
    events.write_text(f'{br.LEAD} on {note} {velocity}\n')
    out = Path(tmp) / 'render.wav'
    subprocess.run([renderer, '--events', str(events), '--output', str(out), '--duration', str(RENDER_SECONDS),
                    '--no-low-knock'] + br.MEASURE + (['--model', model] if model != 'grand' else []),
                   check=True, stdout=subprocess.DEVNULL)
    return pa.load(out)


def measure_take(job):
    """A take's frames in each band its fundamental clears: the recording's power per frame and
    channel, the render's scaled to it, and the recording's analytic sums (band_frames); and how
    far the render's strike lies after its contact (samples), where its knock would start."""
    model, case, note, velocity, renderer = job
    sr, x = pa.load(fit.MODELS[model]['wav'] / f'{case}.wav')
    with tempfile.TemporaryDirectory(prefix='fit-low-knock-') as tmp:
        sr2, y = render(renderer, model, note, velocity, tmp)
    kx, ky = strike(x, sr), strike(y, sr2)
    gain = (early_rms(x, sr, kx) / max(early_rms(y, sr2, ky), 1e-20)) ** 2
    f1 = pa.midi_hz(note)
    bands = {}
    for j, f in enumerate(BANDS):
        if f * 2 ** (1 / 6) > CLEARANCE * f1:
            continue
        rec, sums = band_frames(x, sr, kx, f, analytic=True)
        eng, _ = band_frames(y, sr2, ky, f)
        if rec is not None and eng is not None:
            bands[j] = dict(rec=rec, eng=gain * eng, sums=sums)
    return dict(case=case, note=note, velocity=velocity, sr=sr2, start=ky - int(round(br.LEAD * sr2)), bands=bands)


def errors(p, q, s, density):
    """Weighted squared dB error (frame_weights) of the recording's frames `p` against the render's `q` plus
    knocks of the shapes' frames `s` at the densities `density`, each held up to FLOOR under the recording's
    loudest frame: a knock raising a frame the recording leaves under that counts for what it adds above it.
    Any leading axes broadcast."""
    floor = FLOOR * p.max()
    model = np.maximum(q + density[..., None] * s, floor)
    return np.sum(WEIGHTS * (10 * np.log10(model) - 10 * np.log10(np.maximum(p, floor))) ** 2, axis=-1)


def measure_piano(model, renderer, pool):
    m = fit.MODELS[model]
    text = m['header'].read_text()
    grid, levels = header_array(text, 'layerVelocity'), header_array(text, 'layerLevelDb')
    anchors = fit.train_anchors(m)
    jobs = [(model, case, note, velocity, renderer) for note, layers in anchors.items()
            if BANDS[0] * 2 ** (1 / 6) <= CLEARANCE * pa.midi_hz(note) for case, velocity, _ in layers]
    takes = list(pool.map(measure_take, jobs, chunksize=2))
    rates, rises = np.repeat(RATES, len(RISES)), np.tile(RISES, len(RATES))
    attack = int(round(ATTACK / HOP))
    bands, lines = [], {note: [None] * len(BANDS) for note in anchors}
    for j, f in enumerate(BANDS):
        mine = [t for t in takes if j in t['bands']]
        excess, sums = np.zeros(2), np.zeros(3, complex)
        for t in mine:
            e = t['bands'][j]
            e['p'], e['q'] = e['rec'].mean(axis=1), e['eng'].mean(axis=1)
            held = e['p'] >= KNOCK_OVER * e['q']
            held[attack:] = False
            excess += np.maximum(e['rec'] - e['eng'], 0)[held].sum(axis=0)
            sums += e['sums'][held].sum(axis=0)
        bands.append(dict(hz=f, takes=len(mine), mine=mine,
                          balance_db=float(10 * math.log10(excess[1] / excess[0])) if excess.min() > 0 else 0.,
                          coherence=float(abs(sums[0]) / math.sqrt(sums[1].real * sums[2].real)) if sums[1].real * sums[2].real > 0 else None))
    for j, band in enumerate(bands):
        if band['coherence'] is None:
            known = [k for k, b in enumerate(bands) if b['coherence'] is not None]
            band['coherence'] = bands[min(known, key=lambda k: abs(k - j))]['coherence'] if known else 1.
    room = room_of(model)
    for j, (f, band) in enumerate(zip(BANDS, bands)):
        mine = band.pop('mine')
        # The room hears the mid of the knock's channels: its power over theirs follows from their
        # balance and coherence as the engine plays them (min(1, coherence), the header's).
        tilt = 10 ** (band['balance_db'] / 20)
        heard = .5 * (1 + 2 * min(1., band['coherence']) / (tilt + 1 / tilt))
        shapes = {}
        for sr in {t['sr'] for t in mine}:
            own = knock_shapes(f, sr)
            shapes[sr] = own + heard * room_echo(own, room, f, sr)
        for t in mine:
            e = t['bands'][j]
            e['s'] = shape_frames(shapes[t['sr']], t['start'], t['sr'])
            e['d0'] = e['p'].max() / e['s'].max(axis=1)
        total = sum(errors(e['p'], e['q'], e['s'][:, None, :], e['d0'][:, None] * 10 ** (OFFSETS / 10)).min(axis=1)
                    for e in (t['bands'][j] for t in mine))
        best = int(np.argmin(total))
        fitted = []
        for note in anchors:
            own = [t for t in mine if t['note'] == note]
            if len(own) < LEVEL_TAKES:
                continue
            x = np.array([layer_level(t['velocity'], grid, levels) for t in own])
            es = [t['bands'][j] for t in own]
            s = [e['s'][best] for e in es]
            # Each take's own best level starts the line, which the grid then fits to them together.
            own_db = np.array([10 * math.log10(e['d0'][best]) + OFFSETS[int(np.argmin(
                errors(e['p'], e['q'], si, e['d0'][best] * 10 ** (OFFSETS / 10))))] for e, si in zip(es, s)])
            level0 = np.polyfit(x, own_db, 1)[1]
            line = level0 + LINE_SPAN[:, None, None] + SLOPES[None, :, None] * x[None, None, :]  # (levels, slopes, takes)
            error = sum(errors(e['p'], e['q'], si, 10 ** (line[:, :, k] / 10)) for k, (e, si) in enumerate(zip(es, s)))
            i, k = np.unravel_index(int(np.argmin(error)), error.shape)
            without = sum(errors(e['p'], e['q'], si, np.zeros(())) for e, si in zip(es, s))
            weight = len(es) * WEIGHTS.sum()
            lines[note][j] = dict(takes=len(own), level_db=float(level0 + LINE_SPAN[i]), slope_db=float(SLOPES[k]),
                                  rms_db_without=float(math.sqrt(without / weight)),
                                  rms_db=float(math.sqrt(error[i, k] / weight)),
                                  at_edge=bool(i in (0, len(LINE_SPAN) - 1) or k in (0, len(SLOPES) - 1)))
            fitted.append(note)
        band.update(pitches=fitted, rate_db_s=float(rates[best]), rise_s=float(rises[best]),
                    rate_at_edge=bool(rates[best] in (RATES[0], RATES[-1])),
                    rise_at_edge=bool(rises[best] in (RISES[0], RISES[-1])), room_heard=heard)
    return dict(header=rel(m['header']), header_sha256=fit.sha256(m['header']),
                split=rel(m['split']), split_sha256=fit.sha256(m['split']),
                corpus=rel(m['corpus']), corpus_sha256=fit.sha256(m['corpus']),
                takes=len(takes), bands=bands,
                anchors=[dict(note=note, bands=lines[note]) for note in anchors])


def number(x):
    return f'{x:.7g}f' if '.' in f'{x:.7g}' or 'e' in f'{x:.7g}' else f'{x:.7g}.f'


def header_text(receipt):
    lines = ['// Generated by Tools/fit_low_knock.py from the train takes of each piano\'s',
             '// locked split (Docs/research/low-knock-2026-11-09.md); regenerate, never edit.',
             '// Fitted numbers only: no recorded waveform or impulse response.',
             '#pragma once',
             '#include <array>',
             '',
             'namespace keyra { namespace measured {',
             '// The strike\'s knock under the noise bands\' lowest (400 Hz). Per',
             '// third-octave band: its centre (Hz), its left/right coherence, its decay',
             '// rate (1/s) and rise (s), and its right-over-left level difference (dB).',
             '// Per recorded pitch and band: its density at contact (dB re 1/Hz) at the',
             '// loudest layer and its slope per dB of the level the strike\'s layer plays',
             '// at (-200 dB where the pitch does not measure it).',
             'struct LowKnockBand { float hz, coherence, rate, rise, balanceDb; };',
             'struct LowKnock { float levelDb, slopeDb; };',
             f'constexpr int lowKnockBandCount={len(BANDS)};']
    for name in PIANOS:
        m = receipt['pianos'][name]
        lines += [f'namespace {name} {{',
                  f'constexpr std::array<LowKnockBand,{len(BANDS)}> lowKnockBands{{{{'
                  + ','.join('{' + ','.join(number(v) for v in (b['hz'], min(1., b['coherence']), b['rate_db_s'] / DB_PER_NEPER,
                                                                 b['rise_s'], b['balance_db'])) + '}' for b in m['bands']) + '}};',
                  f'constexpr std::array<LowKnock,{len(m["anchors"])}*{len(BANDS)}> lowKnock{{{{']
        for row in m['anchors']:
            cells = ['{' + number(b['level_db']) + ',' + number(b['slope_db']) + '}' if b else '{-200.f,0.f}' for b in row['bands']]
            lines.append(f'  // MIDI {row["note"]}')
            lines.append('  ' + ','.join(cells) + ',')
        lines += ['}};', f'}} // namespace {name}']
    lines += ['}} // namespace keyra::measured', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--renderer', type=Path, help='keyra_render built from the engine to measure against')
    parser.add_argument('--jobs', type=int, default=3)
    parser.add_argument('--check', action='store_true', help='check the receipt against the tool, its inputs and the header, and exit')
    args = parser.parse_args()
    if args.check:
        receipt = json.loads(RECEIPT.read_text())
        stale = {rel(Path(__file__))} if receipt['tool_sha256'] != fit.sha256(Path(__file__)) else set()
        stale |= {receipt['room']} if receipt['room_sha256'] != fit.sha256(ROOT / receipt['room']) else set()
        for measured in receipt['pianos'].values():
            stale |= {measured[k] for k in ('header', 'split', 'corpus') if measured[f'{k}_sha256'] != fit.sha256(ROOT / measured[k])}
        if stale:
            raise SystemExit('the receipt is stale for ' + ', '.join(sorted(stale)) + ': run Tools/fit_low_knock.py --renderer <keyra_render>')
        if HEADER.read_text() != header_text(receipt):
            raise SystemExit(f'{rel(HEADER)} differs from the one {rel(RECEIPT)} gives: run Tools/fit_low_knock.py --renderer <keyra_render>')
        print('the low knock receipt and header are current')
        return
    if args.renderer is None:
        parser.error('--renderer is required to measure')
    with ProcessPoolExecutor(args.jobs) as pool:
        pianos = {name: measure_piano(name, str(args.renderer.resolve()), pool) for name in PIANOS}
    receipt = dict(tool=rel(Path(__file__)), tool_sha256=fit.sha256(Path(__file__)),
                   engine=rel(ENGINE), engine_sha256=fit.sha256(ENGINE), room=rel(ROOM), room_sha256=fit.sha256(ROOM),
                   bands=BANDS, pianos=pianos)
    RECEIPT.write_text(json.dumps(receipt, indent=1) + '\n')
    HEADER.write_text(header_text(receipt))
    print(f'wrote {rel(HEADER)} and {rel(RECEIPT)}')


if __name__ == '__main__':
    main()
