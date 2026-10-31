#!/usr/bin/env python3
"""Decode and verify the Pianobook "Grandpa's Piano" recordings.

The library (a 1933 Steinway Model L, David Hawkins, README 2024-06-19) states
no licence. Its preset maps five velocity layers on pitches every five
semitones, seven unpitched key-noise takes and pedal noises, 44.1 kHz stereo,
mostly 16-bit. This reads a copy of the library and writes WAV into the
ignored out/ tree, which never enters the repository or the instrument,
without gain, trim, resampling, denoising or EQ.

The preset's line 147 is not well-formed XML (no space before an attribute),
so it is read by pattern. The five files it leaves unmapped are left out,
FF_94_CellNoise and FF_99_CellNoise among them.

The preset's levels are not applied. Its group volumes (FF 0.35, F 0.45, M 0.6,
P and PP 1) step down with velocity, and its pan runs -24 to +24 with pitch.
The layers were not brought to one level: from PP to FF the 50-750 ms RMS
rises 19 to 45 dB at each pitch, in order. But the FF takes peak within 2.4 dB
of full scale at every pitch, so they were likely normalised take by take,
and between neighbouring pitches their levels say little.

The seven key-noise takes play on any key. A pitch's rel<midi> is one of them
in turn, by the pitch's place in the list (carried_from names the take).

  python3 Tools/decode_detroit.py --library <Grandpas Piano (DS) folder>        # decode, verify
  python3 Tools/decode_detroit.py --library <Grandpas Piano (DS) folder> --pin  # (re)write the pins
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRESET = 'GrandpasPiano.dspreset'
MANIFEST = ROOT / 'Tools/corpus/detroit-grand.json'
LAYERS = {'PP': 1, 'P': 2, 'M': 3, 'F': 4, 'FF': 5}


def inventory(library: Path):
    text = re.sub(r'<!--.*?-->', '', (library / PRESET).read_text(encoding='utf-8'), flags=re.S)
    samples = [dict(re.findall(r'(\w+)="([^"]*)"', s)) for s in re.findall(r'<sample\b[^>]*>', text)]
    items, noises = [], []
    for s in samples:
        name = re.search(r'Steinway_(PP|P|M|FF|F)_\d+', s['path'])
        if name:
            root = int(s['rootNote'])
            items.append({'id': f'n{root}v{LAYERS[name[1]]}', 'kind': 'note', 'midi': root, 'layer': LAYERS[name[1]],
                          'round_robin': 1, 'keys': [int(s['loNote']), int(s['hiNote'])],
                          'velocity': [int(s['loVel']), int(s['hiVel'])], 'source': s['path']})
        elif 'RT_' in s['path']:
            noises.append(s['path'])
        elif 'Pedal_Down' in s['path'] or 'Pedal_Up' in s['path']:
            items.append({'id': 'pedalD1' if 'Down' in s['path'] else 'pedalU1', 'kind': 'pedal', 'source': s['path']})
    pitches = sorted({i['midi'] for i in items if i['kind'] == 'note'})
    for n, midi in enumerate(pitches):
        source = noises[n % len(noises)]
        items.append({'id': f'rel{midi}', 'kind': 'key-release', 'midi': midi, 'source': source,
                      'carried_from': Path(source).stem})
    return sorted(items, key=lambda i: (i['kind'], i.get('midi', 0), i.get('layer', 0)))


def depth(path: Path) -> str:
    probe = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries',
                            'stream=sample_fmt,bits_per_sample', '-of', 'csv=p=0', str(path)],
                           capture_output=True, text=True, check=True).stdout
    return 'pcm_s24le' if '24' in probe else 'pcm_s16le'


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--library', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=ROOT / 'out/detroit/wav')
    parser.add_argument('--pin', action='store_true')
    args = parser.parse_args()
    stored = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    pins = {} if args.pin else {f['id']: f['aif_sha256'] for f in stored.get('files', [])}
    items = inventory(args.library)
    if not args.pin and {i['id'] for i in items} != set(pins):
        raise SystemExit('the preset maps other recordings than the manifest pins')
    args.out.mkdir(parents=True, exist_ok=True)
    for item in items:
        path = args.library / item['source']
        item['aif_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        if item['id'] in pins and pins[item['id']] != item['aif_sha256']:
            raise SystemExit(f'{item["id"]}: SHA256 differs from the pin')
        target = args.out / f'{item["id"]}.wav'
        if not target.exists():
            part = target.with_suffix('.part.wav')
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-y', '-i', str(path),
                            '-map_metadata', '-1', '-c:a', depth(path), str(part)], check=True)
            part.replace(target)
    if args.pin:
        MANIFEST.write_text(json.dumps({
            'title': 'Grandpa\'s Piano (Decent Sampler, Pianobook)', 'author': 'David Hawkins',
            'instrument': 'a 1933 Steinway Model L grand piano, per the library\'s README',
            'license': 'none stated in the library',
            'capture': 'one stereo perspective, 44.1 kHz stereo AIFF, 16-bit but for six 24-bit takes',
            'velocity_layers': 'PP 0-25, P 26-45, M 46-75, F 76-105, FF 106-127',
            'mixing': 'the preset\'s group volumes and pan are not applied; see Tools/decode_detroit.py',
            'decoding': 'ffmpeg to PCM WAV at the source depth, no gain, trim, resampling, denoising or EQ',
            'files': items}, indent=1) + '\n')
    print(json.dumps({'decoded': len(items), 'pinned': len(pins) or 'written'}))


if __name__ == '__main__':
    main()
