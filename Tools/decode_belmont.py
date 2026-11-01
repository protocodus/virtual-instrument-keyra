#!/usr/bin/env python3
"""Decode and verify the Pianobook "Mom's 1974 Baby Grand" recordings.

The library (a 1974 Wm. Knabe & Co. baby grand, The Imperfect Drummer, Brian
Peat, README 13 July 2025, Decent Sampler 1.5) states no licence. Its preset
maps 30 pitches every three semitones from MIDI 21 to 108 at three velocity
layers, each with and without the sustain pedal, one key-release take per
pitch (played with the pedal up only) and five pedal-down and five pedal-up
noises. Files are 48 kHz/24-bit stereo, recorded by one pair of sE 8s at the
hammers. The library ships as a .dslibrary, a stored zip of the preset and
its WAVs; this reads the extracted folder its README describes, or the
.dslibrary itself, and writes into the ignored out/ tree, which never enters
the repository or the instrument, without trim, resampling, denoising or EQ:
every preset start point is 0.

Only the pedal-up notes are decoded. The pedal-down notes are the same
pitches with every damper off, and no fit here reads a held note's free
strings from them yet.

Each file is pinned by its samples' SHA256 (pcm_sha256: the interleaved
frames as little-endian int32, as scipy reads 24-bit WAV and ffmpeg -f s32le
writes them), so that a lossless copy of the library verifies as the
original does. wav_sha256 is the decoded WAV's, the file the fit reads, so
that a change of gain invalidates the fit's cached analyses.

Every note take is peak-normalised by layer: at 26 of the 30 pitches the
Soft takes peak at -11.9 +-0.1 dBFS, Med at -9.9 and Hard at -7.9, from A0 to
C8, so the recordings keep neither the steps between the layers nor the
piano's level from key to key. The decoder sets both, and says so in the
manifest; neither is a measurement of the piano.

- The layers' steps are the library's own playback curve (the owner's
  choice, 2026-11-01). Its groups set no ampVelTrack, so Decent Sampler
  scales each note by velocity/127 ("a velocity of 127 yields a gain 1.0, a
  velocity of 63 a gain of 0.5", the developer guide's <group> attributes).
  Each layer takes that gain at the velocity the fit plays it at, the
  midpoint of its range, against the Hard layer's (LAYER_GAIN_DB): Soft
  -13.33 dB, Med -3.56 dB.
- Key to key, every take is gained to a smooth trend over the keyboard (the
  owner asked for a smooth response, 2026-11-01). Normalising to one peak
  left each pitch's 50-750 ms level, the benchmark's measure, scattered about
  its neighbours' by a median 1.1 to 1.5 dB and up to 5.5 dB per layer, and
  played that way the keys jumped by up to 4.3 dB from one to the next. Per
  layer, the trend is a robust local line (smooth_trend) through the train
  pitches' first takes, so the dev pitches keep out of it; it keeps the
  treble's fall, which the takes' decays carry.

The key releases and pedal noises are not normalised (their peaks scatter
from -19 to -47 dBFS) and keep their levels. Nothing else of the preset's mix
is applied.

  python3 Tools/decode_belmont.py --library <Moms 1974 Baby Grand folder or .dslibrary>        # decode, verify
  python3 Tools/decode_belmont.py --library <Moms 1974 Baby Grand folder or .dslibrary> --pin  # (re)write the pins
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import zipfile
from pathlib import Path

import sys

import numpy as np
from scipy.io import wavfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
import piano_analysis as pa  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PRESET = 'Moms_1974_Baby_Grand_1.5.dspreset'
MANIFEST = ROOT / 'Tools/corpus/belmont-grand.json'
SPLIT = ROOT / 'Tools/corpus/split-belmont-2026-11-01.json'
LAYERS = {'Soft': 1, 'Med': 2, 'Hard': 3}
# Decent Sampler's velocity gain, velocity/127, at each layer's rounded
# velocity midpoint (25, 77, 116), against the Hard layer's.
VELOCITY = {1: 25, 2: 77, 3: 116}
LAYER_GAIN_DB = {layer: 20 * np.log10(v / VELOCITY[3]) for layer, v in VELOCITY.items()}
# The trend's half-width in semitones: three recorded pitches on each side.
TREND_SPAN = 10


def early_db(x, rate) -> float:
    """A take's level as the benchmark sets its gain: both channels' RMS
    from 50 to 750 ms after its onset, in dB."""
    at = pa.onset(x.astype(np.float64) / 2 ** 31, rate)
    part = x[at + round(.05 * rate):at + round(.75 * rate)].astype(np.float64) / 2 ** 31
    return float(10 * np.log10(np.mean(part ** 2)))


def smooth_trend(notes, levels, at):
    """Levels (dB) at the notes `at` on a local line through (notes,
    levels): tricube weights over TREND_SPAN semitones, then two passes of
    bisquare weights on the residuals, so one take far off its neighbours
    does not bend the line (LOWESS, Cleveland, JASA 74(368), 1979)."""
    notes, levels = np.asarray(notes, float), np.asarray(levels, float)
    robust = np.ones(len(notes))

    def fit(n):
        w = np.clip(1 - (np.abs(notes - n) / TREND_SPAN) ** 3, 0, None) ** 3 * robust
        A = np.stack([np.ones(len(notes)), notes - n], axis=1) * np.sqrt(w)[:, None]
        return float(np.linalg.lstsq(A, levels * np.sqrt(w), rcond=None)[0][0])
    for _ in range(2):
        residual = levels - np.array([fit(n) for n in notes])
        scale = 6 * np.median(np.abs(residual))
        robust = np.clip(1 - (residual / scale) ** 2, 0, None) ** 2 if scale > 0 else np.ones(len(notes))
    return np.array([fit(n) for n in at])


class Library:
    """The library's files by name, from its folder or its .dslibrary zip."""

    def __init__(self, path: Path):
        self.zip = zipfile.ZipFile(path) if path.is_file() else None
        if self.zip:
            self.names = {Path(n).name: n for n in self.zip.namelist()
                          if not n.startswith('__MACOSX/') and not n.endswith('/')}
        else:
            inner = next(path.glob('**/' + PRESET), None)
            if inner is None:
                raise SystemExit(f'{PRESET} not found under {path}')
            self.folder = inner.parent

    def read(self, name: str) -> bytes:
        return self.zip.read(self.names[name]) if self.zip else (self.folder / name).read_bytes()


def inventory(library: Library):
    """Every pedal-up note, key release and pedal noise the preset maps. A
    note's take is its RR number (one Hard take, played in every round-robin
    position, is take 1); the preset's own pitch, rootNote, gives its MIDI
    number (it names A0 A-1, so middle C is C3)."""
    text = library.read(PRESET).decode('utf-8')
    samples = [dict(re.findall(r'(\w+)="([^"]*)"', s)) for s in re.findall(r'<sample\b[^>]*>', text)]
    items, seen = [], set()
    for s in samples:
        if s['path'] in seen:
            continue
        seen.add(s['path'])
        common = {'source': s['path']}
        note = re.fullmatch(r'sE8s Ped Up (Soft|Med|Hard) \S+?(?: RR(\d))?\.wav', s['path'])
        pedal = re.fullmatch(r'sE 8 Pedal (Down|Up) (\d)\.wav', s['path'])
        if note:
            midi, layer, take = int(s['rootNote']), LAYERS[note[1]], int(note[2] or 1)
            items.append({'id': f'n{midi}v{layer}r{take}', 'kind': 'note', 'midi': midi, 'layer': layer,
                          'round_robin': take, 'keys': [int(s['loNote']), int(s['hiNote'])],
                          'velocity': [int(s['loVel']), int(s['hiVel'])]} | common)
        elif s['path'].startswith('sE 8 Ped Up RT '):
            items.append({'id': f'rel{s["rootNote"]}', 'kind': 'key-release', 'midi': int(s['rootNote'])} | common)
        elif pedal:
            items.append({'id': f'pedal{pedal[1][0]}{pedal[2]}', 'kind': 'sustain-pedal', 'edge': pedal[1].lower()}
                         | common)
    return sorted(items, key=lambda i: (i['kind'], i.get('midi', 0), i.get('layer', 0), i.get('round_robin', 0),
                                        i['id']))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=ROOT / 'out/belmont/wav')
    parser.add_argument('--pin', action='store_true')
    args = parser.parse_args()
    stored = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    pins = {} if args.pin else {f['id']: f for f in stored.get('files', [])}
    library = Library(args.library)
    items = inventory(library)
    if not args.pin and {i['id'] for i in items} != set(pins):
        raise SystemExit('the preset maps other recordings than the manifest pins')
    args.out.mkdir(parents=True, exist_ok=True)
    audio = {}
    for item in items:
        data = library.read(item['source'])
        rate, x = wavfile.read(io.BytesIO(data))
        if rate != 48000 or x.dtype != np.int32 or x.ndim != 2:
            raise SystemExit(f'{item["id"]}: expected 48 kHz 24-bit stereo')
        item['pcm_sha256'] = hashlib.sha256(x.astype('<i4').tobytes()).hexdigest()
        if item['id'] in pins and pins[item['id']]['pcm_sha256'] != item['pcm_sha256']:
            raise SystemExit(f'{item["id"]}: samples differ from the pin')
        if item['kind'] == 'note':
            item['recorded_db'] = round(early_db(x, rate), 3)
    roles = json.loads(SPLIT.read_text())['cases']
    for layer in LAYERS.values():
        notes = [i for i in items if i['kind'] == 'note' and i['layer'] == layer]
        fitted = [i for i in notes if roles[i['id']] == 'train']
        trend = smooth_trend([i['midi'] for i in fitted], [i['recorded_db'] for i in fitted],
                             [i['midi'] for i in notes])
        for item, level in zip(notes, trend):
            item['gain_db'] = round(float(LAYER_GAIN_DB[layer] + level - item['recorded_db']), 3)
    for item in items:
        target = args.out / f'{item["id"]}.wav'
        if not target.exists():
            rate, x = wavfile.read(io.BytesIO(library.read(item['source'])))
            if item['kind'] == 'note':
                x = np.round(x * 10 ** (item['gain_db'] / 20) / 256).astype(np.int32) * 256
            part = target.with_suffix('.part.wav')
            wavfile.write(part, rate, x)
            part.replace(target)
        item['wav_sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
        if item['id'] in pins and pins[item['id']].get('wav_sha256') != item['wav_sha256']:
            raise SystemExit(f'{item["id"]}: the decoded WAV differs from the pin; remove {args.out} to decode again')
    if args.pin:
        MANIFEST.write_text(json.dumps({
            'title': 'Mom\'s 1974 Baby Grand (Decent Sampler 1.5, Pianobook)',
            'author': 'The Imperfect Drummer (Brian Peat), pianobook.co.uk/profile/imperfectdrummer',
            'instrument': 'a 1974 Wm. Knabe & Co. baby grand piano, reconditioned with its felts sanded, '
                          'per the library\'s README',
            'license': 'none stated in the library',
            'capture': 'one pair of sE 8 cardioids in X/Y at the hammers, lid fully open, 48 kHz/24-bit stereo WAV',
            'pitch_names': 'the library names A0 (MIDI 21) A-1 and middle C C3; ids carry MIDI numbers',
            'velocity_layers': 'three, by the preset: Soft 1-48, Med 49-104, Hard 105-127; Soft and Med have '
                               'one to three round robins, Hard one take played in all three positions',
            'levels': 'every note take is peak-normalised by layer (Soft -11.9, Med -9.9, Hard -7.9 dBFS); '
                      'the decoder gives each layer Decent Sampler\'s velocity gain v/127 at its velocity midpoint '
                      'against Hard\'s (Soft -13.33 dB, Med -3.56 dB) and each take a smooth trend over the '
                      'keyboard: gain_db per take, from its recorded_db (50-750 ms RMS); see Tools/decode_belmont.py',
            'mixing': 'the preset plays the notes at its Key Vol default 0.3, the key releases and pedal noises '
                      'at 0.1 with each sample at +6 dB, and a reverb; the fit applies none of them',
            'processing': 'the README says the takes were cleaned of clicky keys and buzzes and may be '
                          'processed and cleaned too much',
            'decoding': 'pedal-up notes at the gains above, key releases and pedal noises as recorded; '
                        'no trim, resampling, denoising or EQ',
            'files': items}, indent=1) + '\n')
    print(json.dumps({'decoded': len(items), 'pinned': len(pins) or 'written'}))


if __name__ == '__main__':
    main()
