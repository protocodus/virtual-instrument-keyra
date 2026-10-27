#!/usr/bin/env python3
"""Fetch, decode and verify the Salamander Grand Piano V3 recordings Keyra is
measured against.

Every file comes from one pinned commit of the sfzinstruments SFZ/FLAC
distribution (Alexander Holm, CC BY 3.0, a Yamaha C5 recorded with two AKG C414
in AB about 12 cm above the strings, 48 kHz/24-bit stereo). FLACs are decoded
to PCM24 WAV without gain, trim, resampling or any other change. The audio is
fetched into the ignored out/ tree and never enters the repository or the
instrument; Tools/corpus/salamander-v3.json pins every file's SHA256.

  python3 Tools/fetch_salamander.py            # fetch what is missing, verify all
  python3 Tools/fetch_salamander.py --pin      # (re)write the pins from the files
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import subprocess
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'Tools/corpus/salamander-v3.json'
COMMIT = '3382bf9496bba2486f5ab0de55a264d1dfc38404'
BASE = f'https://raw.githubusercontent.com/sfzinstruments/SalamanderGrandPiano/{COMMIT}/Samples/'
# Sampled every minor third from A0 (the SFZ's Data/region.txt).
PITCHES = ['A0', 'C1', 'D#1', 'F#1', 'A1', 'C2', 'D#2', 'F#2', 'A2', 'C3', 'D#3', 'F#3',
           'A3', 'C4', 'D#4', 'F#4', 'A4', 'C5', 'D#5', 'F#5', 'A5', 'C6', 'D#6', 'F#6',
           'A6', 'C7', 'D#7', 'F#7', 'A7', 'C8']
# String-resonance release layers exist up to D#6 (Data/str_res.txt).
DAMPED = PITCHES[:PITCHES.index('D#6')+1]


def midi(name: str) -> int:
    letter, sharp, octave = name[0], name[1:2] == '#', int(name[-1])
    return 12*(octave+1) + {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}[letter] + sharp


def inventory():
    """Every recording the SFZ maps: notes, release noises, damper resonances, pedal."""
    items = [{'id': f'{p}v{v}', 'kind': 'note', 'midi': midi(p), 'layer': v}
             for p in PITCHES for v in range(1, 17)]
    items += [{'id': f'rel{k}', 'kind': 'key-release', 'midi': 20+k} for k in range(1, 89)]
    items += [{'id': f'harm{size}{p}', 'kind': 'damper-resonance', 'midi': midi(p),
               'layer': 'loud' if size == 'L' else 'soft'} for size in 'LS' for p in DAMPED]
    items += [{'id': f'pedal{edge}{n}', 'kind': 'sustain-pedal', 'edge': 'down' if edge == 'D' else 'up'}
              for edge in 'DU' for n in (1, 2)]
    return items


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def fetch(item, out: Path, pins: dict):
    flac = out/'flac'/(item['id']+'.flac')
    wav = out/'wav'/(item['id']+'.wav')
    if not flac.exists():
        flac.parent.mkdir(parents=True, exist_ok=True)
        part = flac.with_suffix('.part')
        url = BASE + urllib.parse.quote(item['id']+'.flac')
        subprocess.run(['curl', '-fsSL', '--retry', '4', '--max-time', '300', url, '-o', str(part)], check=True)
        part.replace(flac)
    digest = sha256(flac)
    if item['id'] in pins and pins[item['id']] != digest:
        raise RuntimeError(f'{item["id"]}: FLAC SHA256 differs from the pin')
    if not wav.exists():
        wav.parent.mkdir(parents=True, exist_ok=True)
        part = wav.with_suffix('.part.wav')
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(flac),
                        '-c:a', 'pcm_s24le', str(part)], check=True)
        part.replace(wav)
    return item['id'], digest


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out', type=Path, default=ROOT/'out/salamander')
    parser.add_argument('--jobs', type=int, default=8)
    parser.add_argument('--pin', action='store_true', help='write the SHA256 pins from the fetched files')
    parser.add_argument('--kind', action='append', help='restrict to note, key-release, damper-resonance or sustain-pedal')
    args = parser.parse_args()
    stored = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    pins = {} if args.pin else {f['id']: f['flac_sha256'] for f in stored.get('files', [])}
    items = [i for i in inventory() if not args.kind or i['kind'] in args.kind]
    with concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        digests = dict(pool.map(lambda i: fetch(i, args.out, pins), items))
    if args.pin:
        files = [dict(item, flac_sha256=digests[item['id']]) for item in inventory() if item['id'] in digests]
        MANIFEST.write_text(json.dumps({
            'title': 'Salamander Grand Piano V3', 'author': 'Alexander Holm',
            'instrument': 'Yamaha C5 grand', 'license': 'CC BY 3.0',
            'license_url': 'https://creativecommons.org/licenses/by/3.0/',
            'capture': 'two AKG C414 in AB about 12 cm above the strings, 48 kHz/24-bit stereo',
            'distribution': 'https://github.com/sfzinstruments/SalamanderGrandPiano', 'commit': COMMIT,
            'velocity_layers': 'SFZ bins 1-26, 27-34, 35-36, 37-43, 44-46, 47-50, 51-56, 57-64, '
                               '65-72, 73-80, 81-88, 89-96, 97-104, 105-112, 113-120, 121-127',
            'decoding': 'ffmpeg to PCM24 WAV, no gain, trim, resampling, denoising or EQ',
            'files': files}, indent=1)+'\n')
    print(json.dumps({'verified': len(digests), 'pinned': len(pins) or 'written'}))


if __name__ == '__main__':
    main()
