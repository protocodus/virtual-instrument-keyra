#!/usr/bin/env python3
"""Set a Keyra renderer's playing of concert performances beside their
recordings: MAESTRO's Disklavier grands, each performance's own keys,
velocities and pedals played through the renderer.

The pianos, halls and microphones are none of Keyra's, so nothing here scores
a level or a balance. What is read is how the recording MOVES against the
render within one performance.

Protocol. The render plays the opening 60 s of the performance's MIDI (notes,
sustain, sostenuto and soft pedals as continuous values) on the given piano at
its default controls, as the plug-in plays (--vary). Recording and render are
each cut in 64 ms Hann frames every 16 ms; a frame's level is the mean of the
two channels' power in the octave bands from 62.5 Hz to 8 kHz and in the whole
of that range, in dB. MAESTRO's alignment of MIDI and audio (about 3 ms) is
taken as it stands. A frame counts where the
render stands within 50 dB of its loudest frame and the recording 10 dB over
its floor (its level before the first note where that is 0.3 s or longer, else
its first percentile). The difference is the recording's level less the
render's, less the median of that over the performance's counted frames, band
by band: 0 is the performance's own average, positive is the recording louder
there than the render makes it.

Reported, each as the median over a performance's frames and then the median
(and quartiles) over performances:

  movement   the median absolute difference: how far the two part ways.
  sustain    the difference by the time since the last key went down, with
             the sustain pedal up (at most 0.2) and that key still held, with
             the pedal down (at least 0.8), and down less up. The hall rings
             in both, so only down less up is the piano's.
  velocity   the difference in the 0.2 s after a key that had 0.2 s to itself
             with the soft pedal up, by its velocity, and the line through
             them in dB per 10 steps: positive is the recorded piano growing
             more with velocity.
  density    the difference by the keys that went down in the last second.
  soft       the difference with the soft pedal down (at least 0.8) less up
             (at most 0.2), in the 0.2 s after a key, by band: the mean over
             the velocity ranges that hold 15 frames of each, so that soft
             playing under the pedal is set beside as soft playing without.
             With --without-soft the render leaves the soft pedal out, and
             this is the recorded pianos' una corda against none.
  release    the difference after the last key and the pedal came up with
             nothing held: the hall's ring as much as the dampers'.

Train and dev are the corpus's roles (Tools/fetch_maestro.py). Only numbers
are tracked; the recordings stay in the ignored out/ tree.

  python3 Tools/fetch_maestro.py
  python3 Tools/benchmark_phrases.py --renderer build-dsp/keyra_render --model grand
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import struct
import subprocess
import tempfile
from pathlib import Path

import numpy as np

from piano_analysis import load

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'Tools/corpus/maestro-v3.json'
SECONDS = 60
FRAME, HOP = .064, .016
EDGES = [62.5, 125, 250, 500, 1000, 2000, 4000, 8000]
BANDS = [f'{int(low)}-{int(high)}' for low, high in zip(EDGES, EDGES[1:])] + ['whole']
SINCE = [0, .05, .2, .5, 1, 2, 4]
VELOCITY = [1, 40, 55, 70, 85, 128]
DENSITY = [1, 2, 4, 8, 1000]
RELEASE = [0, .1, .3, 1]


def events(path, seconds):
    """A MIDI file's notes and controllers before seconds: (time, kind, number, value)."""
    data = Path(path).read_bytes()
    tracks, division = struct.unpack('>HH', data[10:14])
    if data[:4] != b'MThd' or division >= 0x8000:
        raise ValueError(f'{path}: not a MIDI file in ticks per beat')
    position, raw = 14, []

    def length():
        nonlocal position
        value = 0
        while True:
            byte = data[position]
            position += 1
            value = value << 7 | byte & 127
            if byte < 128:
                return value

    for _ in range(tracks):
        end = position + 8 + struct.unpack('>I', data[position+4:position+8])[0]
        position += 8
        tick = status = 0
        while position < end:
            tick += length()
            if data[position] >= 128:
                status = data[position]
                position += 1
            if status == 0xff:
                kind = data[position]
                position += 1
                size = length()
                if kind == 0x51:
                    raw.append((tick, 'tempo', int.from_bytes(data[position:position+size], 'big'), 0))
                position += size
            elif status in (0xf0, 0xf7):
                position += length()
            else:
                size = 1 if status >> 4 in (0xc, 0xd) else 2
                number, value = data[position], data[position+1] if size == 2 else 0
                position += size
                kind = {8: 'off', 9: 'on' if value else 'off', 0xb: 'cc'}.get(status >> 4)
                if kind:
                    raw.append((tick, kind, number, value))
    out, tempo, last, time = [], 500000, 0, 0.
    for tick, kind, number, value in sorted(raw, key=lambda event: event[0]):
        time += (tick-last)*tempo/division/1e6
        last = tick
        if kind == 'tempo':
            tempo = number
        elif time < seconds:
            out.append((time, kind, number, value))
    return out


PEDALS = {64: 'pedal 0', 66: 'sostenuto', 67: 'soft'}


def render(renderer, model, item, folder, soft):
    played = events(item['midi_path'], SECONDS)
    lines = [f'{time:.6f} {kind} {number} {value}' if kind != 'cc' else f'{time:.6f} {PEDALS[number]} {value/127:.6f}'
             for time, kind, number, value in played if kind != 'cc' or number in PEDALS and (soft or number != 67)]
    score, wav = folder/(item['id']+'.events'), folder/(item['id']+'.wav')
    score.write_text('\n'.join(lines)+'\n')
    subprocess.run([str(renderer), '--events', str(score), '--output', str(wav), '--duration', str(SECONDS),
                    '--body', model, '--vary'], check=True, stdout=subprocess.DEVNULL)
    return played, wav


def levels(path):
    """Per frame and band the level in dB."""
    rate, x = load(path)
    size, hop = round(FRAME*rate), HOP*rate
    starts = np.round(hop*np.arange(int((len(x) - size)//hop))).astype(int)
    frames = x[starts[:, None] + np.arange(size)] * np.hanning(size)[None, :, None]
    power = (np.abs(np.fft.rfft(frames, axis=1))**2).mean(axis=2) / rate
    hz = np.fft.rfftfreq(size, 1/rate)
    bands = [power[:, (hz >= low) & (hz < high)].sum(axis=1) for low, high in zip(EDGES, EDGES[1:])]
    bands.append(np.sum(bands, axis=0))
    return 10*np.log10(np.array(bands).T + 1e-30)


def state(played, times):
    """What the performance is doing at each frame's centre."""
    ons = np.array([time for time, kind, *_ in played if kind == 'on'])
    # When each key came up again: the next off of its number.
    offs, waiting = [], {}
    for time, kind, number, _ in played:
        if kind == 'on':
            waiting[number] = len(offs)
            offs.append(np.inf)
        elif kind == 'off' and number in waiting:
            offs[waiting.pop(number)] = time
    offs = np.array(offs)
    velocities = np.array([value for _, kind, _, value in played if kind == 'on'])
    last = np.searchsorted(ons, times, 'right') - 1
    since = np.where(last >= 0, times - ons[np.maximum(last, 0)], np.inf)
    # A key with 0.2 s to itself: none other from 0.2 s before it to the frame.
    alone = (last >= 0) & (np.searchsorted(ons, times, 'right') - np.searchsorted(ons, ons[np.maximum(last, 0)] - .2) == 1)
    density = np.searchsorted(ons, times, 'right') - np.searchsorted(ons, times - 1)

    def controller(number):
        changes = [(time, value/127) for time, kind, n, value in played if kind == 'cc' and n == number]
        if not changes:
            return np.zeros(len(times))
        at, values = map(np.array, zip(*changes))
        index = np.searchsorted(at, times, 'right') - 1
        return np.where(index >= 0, values[np.maximum(index, 0)], 0)

    # Since everything came up: no key held, the sustain pedal up (at most 0.2).
    edges, held = [], 0
    for time, kind, number, value in played:
        if kind in ('on', 'off'):
            held += 1 if kind == 'on' else -1
            edges.append((time, held))
    free_at, free = np.array([e[0] for e in edges]), np.array([e[1] <= 0 for e in edges])
    index = np.searchsorted(free_at, times, 'right') - 1
    sustain = controller(64)
    quiet = (index >= 0) & free[np.maximum(index, 0)] & (sustain <= .2)
    released = np.full(len(times), np.inf)
    start = None
    for i, q in enumerate(quiet):
        start = (times[i] if start is None else start) if q else None
        if q:
            released[i] = times[i] - start
    return {'since': since, 'held': (last >= 0) & (times < offs[np.maximum(last, 0)]), 'velocity': velocities[np.maximum(last, 0)], 'alone': alone, 'density': density,
            'sustain': sustain, 'soft': controller(67), 'released': released, 'first': ons[0] if len(ons) else 0.}


def binned(values, keys, edges, mask):
    """The median of values where mask holds, by the bin of keys; None under 10 frames."""
    out = []
    for low, high in zip(edges, edges[1:]):
        chosen = values[mask & (keys >= low) & (keys < high)]
        out.append(float(np.median(chosen)) if len(chosen) >= 10 else None)
    return out


def measure(item, played, wav):
    recording, rendered = levels(item['audio_path']), levels(wav)
    count = min(len(recording), len(rendered))
    recording, rendered = recording[:count], rendered[:count]
    times = FRAME/2 + HOP*np.arange(count)
    s = state(played, times)
    before = times + FRAME/2 < s['first']
    floor = np.median(recording[before], axis=0) if before.sum()*HOP >= .3 else np.percentile(recording, 1, axis=0)
    counted = (rendered >= rendered.max(axis=0) - 50) & (recording >= floor + 10)
    difference = recording - rendered
    difference = difference - np.array([np.median(column[use]) if use.any() else 0.
                                        for column, use in zip(difference.T, counted.T)])
    whole, use = difference[:, -1], counted[:, -1]
    up, down = s['sustain'] <= .2, s['sustain'] >= .8
    played_on = np.isfinite(s['since'])
    strike = use & s['alone'] & (s['since'] < .2) & (s['soft'] <= .2)
    row = {'id': item['id'], 'role': item['role'],
           'movement': [float(np.median(np.abs(column[use_]))) if use_.any() else None
                        for column, use_ in zip(difference.T, counted.T)],
           'sustain_up': binned(whole, s['since'], SINCE, use & up & s['held']),
           'sustain_down': binned(whole, s['since'], SINCE, use & down & played_on),
           'velocity': binned(whole, s['velocity'], VELOCITY, strike),
           'density': binned(whole, s['density'], DENSITY, use & played_on),
           'release': binned(whole, s['released'], RELEASE, use)}
    row['velocity_slope'] = float(np.polyfit(s['velocity'][strike], whole[strike], 1)[0]*10) if strike.sum() >= 50 else None
    after = played_on & (s['since'] < .2)
    row['soft'] = []
    for column, use_ in zip(difference.T, counted.T):
        pairs = []
        for low, high in zip(VELOCITY, VELOCITY[1:]):
            at = use_ & after & (s['velocity'] >= low) & (s['velocity'] < high)
            on, off = column[at & (s['soft'] >= .8)], column[at & (s['soft'] <= .2)]
            if min(len(on), len(off)) >= 15:
                pairs.append(np.median(on) - np.median(off))
        row['soft'].append(float(np.mean(pairs)) if pairs else None)
    return row


def across(rows, key, index=None):
    """Over performances the median and quartiles of one reported number."""
    values = [row[key] if index is None else row[key][index] for row in rows]
    values = [value for value in values if value is not None]
    if len(values) < 3:
        return None
    return [float(q) for q in np.percentile(values, [50, 25, 75])] + [len(values)]


def show(cell):
    return '      -      ' if cell is None else f'{cell[0]:+5.1f} ({cell[1]:+.1f},{cell[2]:+.1f})'.rjust(19)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--renderer', type=Path, required=True)
    parser.add_argument('--model', default='concert')
    parser.add_argument('--corpus', type=Path, default=ROOT/'out/maestro')
    parser.add_argument('--without-soft', action='store_true', help='leave the soft pedal out of the render')
    parser.add_argument('--jobs', type=int, default=4)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    items = [dict(item, audio_path=args.corpus/(item['id']+'.wav'), midi_path=args.corpus/(item['id']+'.midi'))
             for item in json.loads(MANIFEST.read_text())['files']]
    with tempfile.TemporaryDirectory() as folder, concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        rows = list(pool.map(lambda item: measure(
            item, *render(args.renderer, args.model, item, Path(folder), not args.without_soft)), items))
    if args.out:
        args.out.write_text(json.dumps({'model': args.model, 'soft': not args.without_soft, 'bands': BANDS, 'since': SINCE, 'velocity': VELOCITY,
                                        'density': DENSITY, 'release': RELEASE, 'performances': rows}, indent=1)+'\n')
    spans = lambda edges, unit='': [f'{low:g}-{high:g}{unit}' for low, high in zip(edges, edges[1:])]
    for role in ('train', 'dev'):
        chosen = [row for row in rows if row['role'] == role]
        print(f'\n{args.model}, {role}: {len(chosen)} performances; dB, median (quartiles) over performances')
        print('movement by band')
        for index, band in enumerate(BANDS):
            print(f'  {band:>10} {show(across(chosen, "movement", index))}')
        print('sustain: s since a key, pedal up | down | down less up')
        for index, span in enumerate(spans(SINCE)):
            both = [dict(row, pair=[None if None in (row['sustain_down'][index], row['sustain_up'][index])
                                    else row['sustain_down'][index] - row['sustain_up'][index]]) for row in chosen]
            print(f'  {span:>10} {show(across(chosen, "sustain_up", index))} |{show(across(chosen, "sustain_down", index))}'
                  f' |{show(across(both, "pair", 0))}')
        print('velocity of a key alone, soft pedal up, first 0.2 s')
        for index, span in enumerate(spans(VELOCITY)):
            print(f'  {span:>10} {show(across(chosen, "velocity", index))}')
        print(f'  per 10 steps {show(across(chosen, "velocity_slope"))}')
        print('keys in the last second')
        for index, span in enumerate(spans(DENSITY)):
            print(f'  {span:>10} {show(across(chosen, "density", index))}')
        print('soft pedal down less up, first 0.2 s after a key, by band')
        for index, band in enumerate(BANDS):
            print(f'  {band:>10} {show(across(chosen, "soft", index))}')
        print('s since everything came up')
        for index, span in enumerate(spans(RELEASE)):
            print(f'  {span:>10} {show(across(chosen, "release", index))}')


if __name__ == '__main__':
    main()
