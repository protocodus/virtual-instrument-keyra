#!/usr/bin/env python3
"""Score the sound a Keyra renderer leaves between a pedalled note's partials
against the Yamaha C3's pedal-down takes: the open strings a strike sets
ringing under the pedal.

Protocol, one for the takes and the renders. From the onset (the first frame
whose peak over the channels passes 5 % of the greatest in the first 3 s), in
the windows 0.15-0.5, 0.5-1.5, 1.5-3 and 3-6 s, the Hann-windowed spectrum of
the mid channel gives per octave band (150-300, 300-600, 600-1200 and
1200-2400 Hz) the energy of the whole band and of what lies BETWEEN the key's
partials: the bins further than max(12 Hz, 3 %) + 0.8 % from every multiple
of the key's equal-tempered pitch. The whole note is the energy from 150 Hz to
6 kHz. Over 2.4 kHz the pedal-down takes do not clear the pedal-up takes.

A band that holds partials of the key (its top over 1.05 times the pitch) is
scored as its between energy in each window over the band's whole energy in
the first window; a band under the first partial as its between energy over
the whole note's in the first window. Both are ratios within one file, so
neither depends on its scale, and the fall from window to window is the
sound's own. The score is the render's ratio minus the takes', in dB,
wherever the pedal-down take stands 6 dB over the pedal-up take in that band
and window (under that the take's floor is what is measured). Takes of one
pitch, layer and pedal state share a median.

How the note itself holds up under the pedal is reported beside it, unscored:
the whole note's energy pedal down less pedal up in each later window, less
the same in the first, so that neither take's strike nor its scale counts.

The renderer plays each pitch alone on the given piano at its default
controls, with the pedal down from the start and without it, the key struck
at 0.5 s, at velocities 60, 100 and 120 for the preset's layers 1 to 3. Those are the
preset's playback bins; the capture's strike force is unknown. The pitches are
the corpus's damped keys from C1 to D#6 (under C1 a key's partials leave no
bins between them from 150 Hz), train and dev as the corpus's split has them.

Only numbers are tracked: Tools/corpus/yamaha-c3-pedal-wash.json holds the
takes' energies in dB, written with --library from a copy of the library
(NumPy alone, the monolith read forward; exact PCM duplicates left out).

  python3 Tools/benchmark_pedal_wash.py --renderer build-dsp/keyra_render --model parlor
  python3 Tools/benchmark_pedal_wash.py --library /path/YamahaC3.dslibrary
"""
from __future__ import annotations

import argparse
import json
import struct
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'Tools/corpus/yamaha-c3.json'
SPLIT = ROOT / 'Tools/corpus/split-yamaha-c3-2026-11-01.json'
TAKES = ROOT / 'Tools/corpus/yamaha-c3-pedal-wash.json'
SR = 48000
WINDOWS = ((.15, .5), (.5, 1.5), (1.5, 3.), (3., 6.))
BANDS = ((150, 300), (300, 600), (600, 1200), (1200, 2400))
NOTE = (150, 6000)
PITCHES = range(24, 88, 3)
VELOCITY = {1: 60, 2: 100, 3: 120}


def measure(x, midi):
    """A stereo take's energies in dB: per window the whole note, and per band
    the whole band and what lies between the key's partials."""
    m = x.mean(axis=1)
    peak = np.abs(x).max(axis=1)[:3 * SR]
    onset = int(np.argmax(peak > .05 * peak.max()))
    f0 = 440 * 2 ** ((midi - 69) / 12)
    out = {'note': [], 'band': [], 'between': []}
    db = lambda energy: None if energy <= 0 else round(10 * float(np.log10(energy)), 2)
    for a, b in WINDOWS:
        y = m[onset + int(a * SR):onset + int(b * SR)]
        if len(y) < int((b - a) * SR):
            raise SystemExit('a take ends inside a window')
        spectrum = np.abs(np.fft.rfft(y * np.hanning(len(y)))) ** 2 / len(y)
        hz = np.fft.rfftfreq(len(y), 1 / SR)
        order = np.maximum(1, np.round(hz / f0))
        near = np.abs(hz - order * f0) < np.maximum(12, .03 * hz) + .008 * order * f0
        out['note'].append(db(spectrum[(hz >= NOTE[0]) & (hz < NOTE[1])].sum()))
        out['band'].append([db(spectrum[(hz >= lo) & (hz < hi)].sum()) for lo, hi in BANDS])
        out['between'].append([db(spectrum[(hz >= lo) & (hz < hi) & ~near].sum()) for lo, hi in BANDS])
    return out


def measure_library(library):
    manifest = json.loads(MANIFEST.read_text())
    cases = sorted((c for c in manifest['files'] if c['kind'] == 'note' and not c.get('duplicate_pcm_of')),
                   key=lambda c: c['start_frame'])
    takes = {}
    with zipfile.ZipFile(library) as archive, archive.open(manifest['monolith']['member']) as stream:
        if stream.read(4) != b'RIFF' or stream.read(8)[4:] != b'WAVE':
            raise SystemExit('the monolith is not a WAV')
        while True:
            chunk, size = stream.read(4), struct.unpack('<I', stream.read(4))[0]
            if chunk == b'data':
                break
            stream.read(size + (size & 1))
        done = 0
        for case in cases:
            skip = case['start_frame'] * 6 - done
            while skip > 0:
                skip -= len(stream.read(min(skip, 1 << 24)))
            pcm = np.frombuffer(stream.read(case['frames'] * 6), np.uint8).reshape(-1, 3)
            done = (case['start_frame'] + case['frames']) * 6
            x = (pcm[:, 0].astype(np.int32) | (pcm[:, 1].astype(np.int32) << 8)
                 | (pcm[:, 2].astype(np.int8).astype(np.int32) << 16)) / 8388608.
            takes[case['id']] = {'midi': case['midi'], 'layer': case['layer'], 'pedal': case['pedal'],
                                 **measure(x.reshape(-1, 2), case['midi'])}
    TAKES.write_text(json.dumps({
        'corpus': MANIFEST.name, 'protocol': 'Tools/benchmark_pedal_wash.py', 'unit': 'dB re the file\'s scale',
        'windows_s': WINDOWS, 'bands_hz': BANDS, 'note_hz': NOTE, 'takes': takes}, separators=(',', ':')) + '\n')
    print(f'{len(takes)} takes measured into {TAKES.relative_to(ROOT)}')


def render(renderer, model):
    """The renderer's notes with and without the pedal, measured as the takes are."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import piano_analysis as pa  # SciPy; --library needs NumPy alone
    rendered = {}
    with tempfile.TemporaryDirectory() as tmp:
        for midi in PITCHES:
            for layer, velocity in VELOCITY.items():
                for pedal in ('down', 'up'):
                    events, wav = Path(tmp) / 'note.events', Path(tmp) / 'note.wav'
                    events.write_text(('0 pedal 1\n' if pedal == 'down' else '') + f'0.5 on {midi} {velocity}\n')
                    subprocess.run([renderer, '--events', str(events), '--output', str(wav), '--duration', '7',
                                    '--body', model], check=True, stdout=subprocess.DEVNULL)
                    rendered[midi, layer, pedal] = measure(pa.load(wav)[1], midi)
    return rendered


def takes():
    by = {}
    for take in json.loads(TAKES.read_text())['takes'].values():
        by.setdefault((take['midi'], take['layer'], take['pedal']), []).append(take)
    return by


def score(rendered):
    """Per pitch, layer, window and band the render's ratio minus the takes'."""
    by = takes()
    median = lambda takes, value: float(np.median([value(t) for t in takes]))
    roles = {pitch: role for role, pitches in json.loads(SPLIT.read_text())['pitches'].items() for pitch in pitches}
    rows = []
    for (midi, layer, pedal), ours in rendered.items():
        down, up = by.get((midi, layer, 'down')), by.get((midi, layer, 'up'))
        if pedal != 'down' or not down or not up:
            continue
        for b, (_, top) in enumerate(BANDS):
            holds = top > 1.05 * 440 * 2 ** ((midi - 69) / 12)
            whole = (lambda t: t['band'][0][b]) if holds else (lambda t: t['note'][0])
            if whole(ours) is None:
                continue
            for w in range(len(WINDOWS)):
                between = lambda t: t['between'][w][b]
                if any(between(t) is None for t in (*down, *up, ours)) or median(down, between) < median(up, between) + 6:
                    continue
                rows.append({'role': roles[midi], 'midi': midi, 'layer': layer, 'window': w, 'band': b, 'holds': holds,
                             'db': between(ours) - whole(ours) - (median(down, between) - median(down, whole))})
    return rows


def sustained(rendered):
    """Per pitch and layer the whole note under the pedal less without, in each
    later window against the first: the takes' and the render's."""
    by = takes()
    roles = {pitch: role for role, pitches in json.loads(SPLIT.read_text())['pitches'].items() for pitch in pitches}
    rows = []
    for midi, layer in sorted({key[:2] for key in rendered}):
        down, up = by.get((midi, layer, 'down')), by.get((midi, layer, 'up'))
        if not down or not up:
            continue
        note = lambda takes: np.median([t['note'] for t in takes], axis=0)
        gain = lambda down, up: (down - up)[1:] - (down - up)[0]
        rows.append({'role': roles[midi], 'midi': midi, 'layer': layer, 'takes': gain(note(down), note(up)).tolist(),
                     'render': gain(note([rendered[midi, layer, 'down']]), note([rendered[midi, layer, 'up']])).tolist()})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--renderer')
    mode.add_argument('--library', type=Path, help='original YamahaC3.dslibrary ZIP; rewrites the tracked energies')
    parser.add_argument('--model', default='concert')
    parser.add_argument('--out', type=Path, help='write every scored row here as JSON')
    args = parser.parse_args()
    if args.library:
        return measure_library(args.library)
    rendered = render(args.renderer, args.model)
    rows, notes = score(rendered), sustained(rendered)
    if args.out:
        args.out.write_text(json.dumps({'between': rows, 'held': notes}, indent=1) + '\n')
    line = lambda v: f'{np.median(v):+6.1f} (mean |dB| {np.mean(np.abs(v)):4.1f}, n={len(v):3d})' if v else '  none'
    print(f'{args.model}: render minus the Yamaha C3\'s takes, dB, median')
    for role in ('train', 'dev'):
        held = [r for r in rows if r['role'] == role and r['holds']]
        print(f'{role}: bands holding partials {line([r["db"] for r in held])}')
        for w, (a, b) in enumerate(WINDOWS):
            print(f'  {a:g}-{b:g} s {line([r["db"] for r in held if r["window"] == w])}')
        for name, low, high in (('C1-A2', 24, 45), ('C3-A4', 48, 69), ('C5-D#6', 72, 87)):
            print(f'  {name} {line([r["db"] for r in held if low <= r["midi"] <= high])}')
        for layer in VELOCITY:
            print(f'  layer {layer} {line([r["db"] for r in held if r["layer"] == layer])}')
        print(f'  bands under the first partial {line([r["db"] for r in rows if r["role"] == role and not r["holds"]])}')
    print('the whole note under the pedal less without, dB, median: ' + ', '.join(f'{a:g}-{b:g}' for a, b in WINDOWS[1:])
          + f' s against {WINDOWS[0][0]:g}-{WINDOWS[0][1]:g} s')
    for name, low, high in (('C1-A2', 24, 45), ('C3-A4', 48, 69), ('C5-D#6', 72, 87)):
        part = [r for r in notes if low <= r['midi'] <= high]
        both = (' '.join(f'{v:+5.1f}' for v in np.median([r[who] for r in part], axis=0)) for who in ('takes', 'render'))
        print(f'  {name}: the takes {next(both)}, {args.model} {next(both)} (n={len(part)})')
    for role in ('train', 'dev'):
        miss = np.array([np.subtract(r['render'], r['takes']) for r in notes if r['role'] == role])
        print(f'  {role}: render minus the takes ' + ' '.join(f'{v:+5.1f}' for v in np.median(miss, axis=0))
              + ', mean |dB| ' + ' '.join(f'{v:4.1f}' for v in np.mean(np.abs(miss), axis=0)) + f' (n={len(miss)})')


if __name__ == '__main__':
    main()
