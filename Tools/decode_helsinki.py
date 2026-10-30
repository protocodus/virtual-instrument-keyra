#!/usr/bin/env python3
"""Decode and verify the Helsinki 1967 Tube-Ribbon Edition recordings Keyra's
upright is measured against.

The library is Mikko Patama's (2026, a Decent Sampler instrument). Its
author permits fitting numeric data from its recordings provided the
recordings themselves are not distributed, so this reads a copy of the
library's .dsbundle and decodes into the ignored out/ tree, which never enters
the repository or the instrument. The Stereo Ribbon preset's sample map names
every recording: a Blumlein pair of ribbon microphones in player position,
48 kHz/24-bit stereo FLAC, decoded to PCM24 WAV without gain, trim, resampling
or any other change. Tools/corpus/helsinki-1967.json pins every file's SHA256.
With --tube, the same for the Mono Tube preset's recordings, the same strikes
taken by the library's other microphone (Tools/fit_mic.py), into out/helsinki/tube
and pinned by Tools/corpus/helsinki-1967-tube.json.

  python3 Tools/decode_helsinki.py --library <path>.dsbundle [--tube]          # decode what is missing, verify all
  python3 Tools/decode_helsinki.py --library <path>.dsbundle [--tube] --pin    # (re)write the pins from the files
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Each microphone's preset, pins, folder under out/helsinki and what its
# manifest says of it. The tube's placement is the library's product page's.
MICROPHONES = {
    'ribbon': {'preset': 'Helsinki 1967 Stereo Ribbon.dspreset', 'manifest': ROOT / 'Tools/corpus/helsinki-1967.json',
               'folder': 'wav',
               'capture': 'the Stereo Ribbon preset: a stereo ribbon microphone (Blumlein pair) in player position '
                          'close to the hammers, 48 kHz/24-bit stereo FLAC',
               'played': 'notes, release takes and hammer noises', 'released': 'release takes and hammer noises',
               'release_decay': 3},
    'tube': {'preset': 'Helsinki 1967 Mono Tube.dspreset', 'manifest': ROOT / 'Tools/corpus/helsinki-1967-tube.json',
             'folder': 'tube',
             'capture': 'the Mono Tube preset: a tube condenser microphone (a modified CV-12, cardioid) at shin height '
                        'from the left, aimed at the string crossover, further from the hammers; the same strikes as '
                        'the Stereo Ribbon preset\'s, by the same ids; 48 kHz/24-bit FLAC, its one channel on both sides',
             'played': 'notes and release takes', 'released': 'release takes', 'release_decay': 6},
}
# The preset's velocity ranges, layer 1..5. E7 and G7 (MIDI 100, 103) have
# four layers, the fourth over 100-127; B3 (MIDI 59) has only the fifth, which
# A#3's zone plays. The library names middle C C3, an octave under scientific
# pitch, which Keyra uses.
LAYERS = [(0, 30), (31, 70), (71, 99), (100, 115), (116, 127)]
KINDS = {'Sustain': 'note', 'Release': 'key-release', 'Hammer': 'release-hammer'}


def inventory(library: Path, preset: str):
    """Every recording the preset maps: notes, release takes and the hammer
    noises the ribbon's plays on key release."""
    items = []
    for group in ET.parse(library / preset).getroot().iter('group'):
        kind = KINDS[group.get('name')]
        for sample in group.iter('sample'):
            root = int(sample.get('rootNote'))
            item = {'kind': kind, 'midi': root, 'keys': [int(sample.get('loNote')), int(sample.get('hiNote'))]}
            if kind == 'note':
                velocity = (int(sample.get('loVel')), int(sample.get('hiVel')))
                layer = next(k for k, (lo, hi) in enumerate(LAYERS, 1) if lo == velocity[0])
                # A layer with one take plays it always, without a position.
                rr = int(sample.get('seqPosition', 1))
                item = {'id': f'n{root}v{layer}r{rr}'} | item | {'layer': layer, 'velocity': list(velocity),
                                                                 'round_robin': rr}
            else:
                item = {'id': f'{"rel" if kind == "key-release" else "hammer"}{root}'} | item
            items.append(item | {'source': sample.get('path')})
    return items


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def decode(item, library: Path, out: Path, pins: dict):
    flac = library / item['source']
    wav = out / (item['id'] + '.wav')
    digest = sha256(flac)
    if item['id'] in pins and pins[item['id']] != digest:
        raise RuntimeError(f'{item["id"]}: FLAC SHA256 differs from the pin')
    if not wav.exists():
        wav.parent.mkdir(parents=True, exist_ok=True)
        part = wav.with_suffix('.part.wav')
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-y', '-i', str(flac),
                        '-c:a', 'pcm_s24le', str(part)], check=True)
        part.replace(wav)
    return item['id'], digest


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--library', type=Path, required=True, help='the library\'s .dsbundle folder')
    parser.add_argument('--out', type=Path, default=ROOT / 'out/helsinki')
    parser.add_argument('--jobs', type=int, default=8)
    parser.add_argument('--pin', action='store_true', help='write the SHA256 pins from the library\'s files')
    parser.add_argument('--tube', action='store_true', help='the Mono Tube preset\'s recordings, not the ribbon\'s')
    args = parser.parse_args()
    mic = MICROPHONES['tube' if args.tube else 'ribbon']
    stored = json.loads(mic['manifest'].read_text()) if mic['manifest'].exists() else {}
    pins = {} if args.pin else {f['id']: f['flac_sha256'] for f in stored.get('files', [])}
    items = inventory(args.library, mic['preset'])
    if not args.pin and {i['id'] for i in items} != set(pins):
        raise SystemExit('the preset maps other recordings than the manifest pins')
    out = args.out / mic['folder']
    with concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        digests = dict(pool.map(lambda i: decode(i, args.library, out, pins), items))
    if args.pin:
        mic['manifest'].write_text(json.dumps({
            'title': 'Helsinki 1967 Tube-Ribbon Edition', 'author': 'Mikko Patama',
            'instrument': 'an upright piano with worn hammers (the library does not name its make), in a '
                          'rehearsal space treated to sound dry',
            'license': 'the author permits fitting numeric data from the recordings provided the recordings '
                       'are not distributed (as the project owner relayed it, 28 October 2026)',
            'capture': mic['capture'],
            'pitch_names': 'the library names middle C (MIDI 60) C3, an octave under the scientific pitch used '
                           'here; files are named by MIDI number',
            'velocity_layers': 'Decent Sampler ranges 0-30, 31-70, 71-99, 100-115, 116-127; E7 and G7 (MIDI 100, '
                               '103) 0-30, 31-70, 71-99, 100-127; B3 (MIDI 59) only 116-127',
            'mixing': f'the preset plays {mic["played"]} at their recorded levels '
                      f'(ampVelTrack 0); {mic["released"]} sound on key release at group volume 0.2, '
                      f'release takes {mic["release_decay"]} dB quieter for each second the key was held '
                      '(releaseTriggerDecay)',
            'decoding': 'ffmpeg to PCM24 WAV, no gain, trim, resampling, denoising or EQ',
            'files': [item | {'flac_sha256': digests[item['id']]} for item in items]}, indent=1) + '\n')
    print(json.dumps({'verified': len(digests), 'pinned': len(pins) or 'written'}))


if __name__ == '__main__':
    main()
