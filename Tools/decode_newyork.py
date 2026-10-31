#!/usr/bin/env python3
"""Decode and verify the Decent Sampler "Steinway Grand" recordings.

The library (a Steinway grand, Jon Meyer, jonmeyermusic.com; the author is
inferred from its image caption and archive name) states no licence. Its
preset maps 12 pitches every seven semitones from MIDI 24 to 101, at four
velocity layers and two round robins, with one release take per pitch; there
are no pedal takes. Files are 48 kHz/24-bit stereo. This reads a copy of the
library and writes into the ignored out/ tree, which never enters the
repository or the instrument, without gain, resampling, denoising or EQ.

Each take is cut once, at the preset's own start point less CUT_MARGIN. Files
hold about 0.75 s of pre-roll before that point, and in some of them
unrelated sounds up to -39 dBFS (G0 Dyn1 RR2) that the analysis's onset would
take for the strike. The preset's volume trims are not applied: the fit reads
the recorded levels.

  python3 Tools/decode_steinway.py --library <Steinway Grand  (DS) folder>        # decode, verify
  python3 Tools/decode_steinway.py --library <Steinway Grand  (DS) folder> --pin  # (re)write the pins
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

import numpy as np
from scipy.io import wavfile

ROOT = Path(__file__).resolve().parents[1]
PRESET = 'Steinway Grand.dspreset'
MANIFEST = ROOT / 'Tools/corpus/newyork-grand.json'
CUT_MARGIN = .02


def inventory(library: Path):
    """Every sample the preset maps. A note's root comes from its release
    take's pitch name, not from its rootNote: the preset gives F6 Dyn1 RR2
    rootNote 37 where its zone and every other F6 take say 101."""
    text = (library / PRESET).read_text(encoding='utf-8')
    samples = [dict(re.findall(r'(\w+)="([^"]*)"', s)) for s in re.findall(r'<sample\b[^>]*>', text)]
    items = []
    for s in samples:
        release = re.search(r'Steinway_Release_(.+)\.wav$', s['path'])
        common = {'midi': int(s['hiNote']), 'keys': [int(s['loNote']), int(s['hiNote'])],
                  'velocity': [int(s['loVel']), int(s['hiVel'])], 'source': s['path'], 'start': int(s['start'])}
        if release:
            items.append({'id': f'rel{common["midi"]}', 'kind': 'key-release'} | common)
            continue
        layer, take = map(int, re.search(r'_Dyn(\d)_RR(\d)\.wav$', s['path']).groups())
        items.append({'id': f'n{common["midi"]}v{layer}r{take}', 'kind': 'note', 'layer': layer,
                      'round_robin': take} | common)
    return sorted(items, key=lambda i: (i['kind'] != 'note', i['midi'], i.get('layer', 0), i.get('round_robin', 0)))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=ROOT / 'out/newyork/wav')
    parser.add_argument('--pin', action='store_true')
    args = parser.parse_args()
    stored = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    pins = {} if args.pin else {f['id']: f['wav_sha256'] for f in stored.get('files', [])}
    items = inventory(args.library)
    if not args.pin and {i['id'] for i in items} != set(pins):
        raise SystemExit('the preset maps other recordings than the manifest pins')
    args.out.mkdir(parents=True, exist_ok=True)
    for item in items:
        path = args.library / item['source']
        item['wav_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        if item['id'] in pins and pins[item['id']] != item['wav_sha256']:
            raise SystemExit(f'{item["id"]}: SHA256 differs from the pin')
        rate, x = wavfile.read(path)
        if rate != 48000 or x.dtype != np.int32 or x.ndim != 2:
            raise SystemExit(f'{item["id"]}: expected 48 kHz 24-bit stereo')
        target = args.out / f'{item["id"]}.wav'
        if not target.exists():
            part = target.with_suffix('.part.wav')
            wavfile.write(part, rate, x[max(0, item['start'] - round(CUT_MARGIN * rate)):])
            part.replace(target)
    if args.pin:
        MANIFEST.write_text(json.dumps({
            'title': 'Steinway Grand (Decent Sampler)',
            'author': 'Jon Meyer (inferred: the library\'s image caption JONMEYERMUSIC.COM and its archive name)',
            'instrument': 'a Steinway & Sons grand piano; model and size are not given',
            'license': 'none stated in the library; the project owner asked for the fit on 31 October 2026',
            'capture': 'one stereo perspective, 48 kHz/24-bit stereo WAV',
            'pitch_names': 'the library names middle C (MIDI 60) C3; ids carry MIDI numbers',
            'velocity_layers': 'four, by the preset: 1-60, 61-98, 99-117, 118-127; two round robins each',
            'mixing': 'the preset trims samples by -6 to +9 dB, which the fit does not apply',
            'decoding': f'cut at the preset\'s start point less {CUT_MARGIN} s, no gain, resampling, denoising or EQ',
            'files': items}, indent=1) + '\n')
    print(json.dumps({'decoded': len(items), 'pinned': len(pins) or 'written'}))


if __name__ == '__main__':
    main()
