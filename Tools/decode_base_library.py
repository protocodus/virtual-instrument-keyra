#!/usr/bin/env python3
"""Decode and verify the libraries the keyboard network's base learns from.

Besides the five pianos Keyra plays, the network that fits their keyboards
learns what pianos share from other sampled pianos (Tools/keyboard_measurements.py).
None of them is played or shipped: each is measured once into the partial
envelopes the network is fitted to, and its audio is then deleted. This reads
a copy of a library and decodes the note takes the base uses into the ignored
out/ tree, which never enters the repository or the instrument, to 32-bit
float WAV without gain, trim, resampling, denoising or EQ, and pins every
source file's SHA256 in Tools/corpus/<library>.json.

  python3 Tools/decode_base_library.py vcsl-steinway-b --library <VCSL_Keys folder> --pin  # pin new takes
  python3 Tools/decode_base_library.py vcsl-steinway-b --library <VCSL_Keys folder>        # decode, verify

Only the takes present in the folder are decoded, so that a large library can
come over in parts; each part's pins join the manifest's.

A library whose layers were normalised by its author (`normalised`) keeps each
take's tone and decay but not its level: the network leaves those takes'
levels free.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
import subprocess
from pathlib import Path

from decode_vcsl import regions

ROOT = Path(__file__).resolve().parents[1]
NAMES = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def scientific(name: str) -> int:
    """MIDI number of a scientific pitch name (A0 = 21, C4 = 60)."""
    m = re.fullmatch(r'([A-G])(#?)(-?\d)', name)
    return 12 * (int(m.group(3)) + 1) + NAMES[m.group(1)] + (m.group(2) == '#')


def sfz_notes(sfz, keep):
    """The attack regions an SFZ maps that `keep` selects, layered by their
    velocity ranges from the softest the pitch has, first round robin only."""
    notes = {}
    for r in regions(sfz):
        if r.get('trigger', 'attack') != 'attack' or 'pitch_keycenter' not in r or not keep(r):
            continue
        if r.get('seq_position', '1') != '1':
            continue
        notes.setdefault(int(r['pitch_keycenter']), []).append(r)
    items = []
    for midi, rs in sorted(notes.items()):
        for layer, r in enumerate(sorted(rs, key=lambda r: int(r.get('lovel', 0))), 1):
            items.append({'id': f'n{midi}v{layer}', 'kind': 'note', 'midi': midi, 'layer': layer, 'round_robin': 1,
                          'velocity': [int(r.get('lovel', 0)), int(r.get('hivel', 127))], 'source': r['sample']})
    return items


def bitklavier_notes(folder):
    """bitKlavier's note takes, <pitch>v<layer>.wav with layer 1 the softest:
    every A, C, D# and F# from A0 to C8 (MIDI 21 to 108 every three
    semitones) at sixteen layers, as its README lists them."""
    names = {v: k for k, v in NAMES.items()} | {1: 'C#', 3: 'D#', 6: 'F#', 8: 'G#', 10: 'A#'}
    return [{'id': f'n{midi}v{layer}', 'kind': 'note', 'midi': midi, 'layer': layer, 'round_robin': 1,
             'source': f'{names[midi % 12]}{midi // 12 - 1}v{layer}.wav'}
            for midi in range(21, 109, 3) for layer in range(1, 17)]


VCSL = {'author': 'Versilian Studios', 'license': 'CC0 1.0 (the Versilian Community Sample Library)',
        'pitch_names': 'MIDI numbers as the SFZ\'s pitch_keycenter gives them'}
LIBRARIES = {
    'vcsl-steinway-b': VCSL | {
        'title': 'VCSL Keys: Grand Piano, S Model B 1895', 'instrument': 'a Steinway Model B grand of 1895',
        'capture': 'one stereo close pair ("Close" in every file name), 44.1 kHz FLAC',
        'normalised': 'NORMALIZED.txt: "The sustain and non-sustain articulations for this instrument have been '
                      'normalized"',
        'takes': 'the pedal-up ("NoSus") takes, three layers per pitch, every whole tone from A#0 to G#7',
        'notes': lambda library: sfz_notes(library / 'Grand Piano, S Model B 1895.sfz',
                                           lambda r: '/NoSus/' in r['sample'])},
    'vcsl-knight': VCSL | {
        'title': 'VCSL Keys: Upright Piano, Knight', 'instrument': 'a Knight upright',
        'capture': 'one stereo pair in player position ("Player" in every file name), 44.1 kHz FLAC',
        'normalised': False,
        'takes': 'the sustained notes, two layers per pitch, every whole tone from A0 to C8',
        'notes': lambda library: sfz_notes(library / 'Upright Piano, Knight.sfz',
                                           lambda r: '/Sustains/' in r['sample'])},
    'vcsl-upright-y': VCSL | {
        'title': 'VCSL Keys: Upright Piano, Y', 'instrument': 'an upright, maker not given ("Y")',
        'capture': 'one stereo pair, 44.1 kHz FLAC',
        # Note.txt calls these "a cleaned, recut, and remastered version" and
        # says nothing of normalising; the layers measure 20 dB and more apart.
        'normalised': False,
        'takes': 'the sustained notes, up to three layers per pitch, first round robin',
        'notes': lambda library: sfz_notes(library / 'Upright Piano, Y.sfz',
                                           lambda r: '/Sustains/' in r['sample'])},
    'vcsl-kawai-legacy': VCSL | {
        'title': 'VCSL Keys: Grand Piano, K - Legacy',
        'instrument': 'the Kawai grand of "Grand Piano, K", Keyra\'s Hamamatsu grand: an earlier cut of its takes',
        'capture': 'the main pair ("Main" in every file name), 44.1 kHz FLAC',
        'normalised': 'Normal is Normalized.txt: "\'Normal\' has been normalized"',
        'capture_of': 'kawai',
        'takes': 'the sustained notes, up to four layers per pitch',
        'notes': lambda library: sfz_notes(library / 'Grand Piano, K - Legacy.sfz',
                                           lambda r: '/Sustains/' in r['sample'])},
    'bitklavier': {
        'title': 'bitKlavier Grand Piano Sample Library (House ORTF, 44.1 kHz/16-bit)',
        'author': 'Daniel Trueman, Princeton University', 'license': 'CC BY 4.0',
        'instrument': 'the Steinway D of Taplin Auditorium, Princeton University',
        'capture': 'House ORTF: a Schoeps CMC64 cardioid pair, 44.1 kHz/16-bit WAV',
        'normalised': False,
        'takes': 'every A, C, D# and F# from A0 to C8 at sixteen layers',
        'notes': bitklavier_notes},
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def decode(item, library: Path, out: Path, pins: dict):
    source = library / item['source']
    digest = sha256(source)
    if item['id'] in pins and pins[item['id']] != digest:
        raise RuntimeError(f'{item["id"]}: SHA256 differs from the pin')
    wav = out / (item['id'] + '.wav')
    if not wav.exists():
        wav.parent.mkdir(parents=True, exist_ok=True)
        part = wav.with_suffix('.part.wav')
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-nostdin', '-y', '-i', str(source),
                        '-c:a', 'pcm_f32le', str(part)], check=True)
        part.replace(wav)
    return item['id'], digest


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('name', choices=sorted(LIBRARIES))
    parser.add_argument('--library', type=Path, required=True, help='the library\'s folder')
    parser.add_argument('--pin', action='store_true', help='pin the takes not pinned yet from their files')
    parser.add_argument('--only', type=int, nargs='*', help='decode only these MIDI pitches')
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    spec = LIBRARIES[args.name]
    manifest = ROOT / f'Tools/corpus/{args.name}.json'
    out = ROOT / f'out/base/{args.name}/wav'
    stored = json.loads(manifest.read_text()) if manifest.exists() else {}
    pins = {f['id']: f['sha256'] for f in stored.get('files', []) if 'sha256' in f}
    items = spec['notes'](args.library)
    if set(pins) - {i['id'] for i in items}:
        raise SystemExit('the manifest pins takes the library does not map')
    # The takes copied over so far: a library comes over in parts.
    chosen = [i for i in items if (args.library / i['source']).exists() and (not args.only or i['midi'] in args.only)]
    if not args.pin and any(i['id'] not in pins for i in chosen):
        raise SystemExit('takes without a pin: run with --pin to pin them')
    with concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        digests = dict(pool.map(lambda i: decode(i, args.library, out, pins), chosen))
    if args.pin:
        pins |= digests
        manifest.write_text(json.dumps(
            {k: v for k, v in spec.items() if k != 'notes'}
            | {'decoding': 'ffmpeg to 32-bit float WAV, no gain, trim, resampling, denoising or EQ',
               'files': [item | ({'sha256': pins[item['id']]} if item['id'] in pins else {}) for item in items]},
            indent=1) + '\n')
    print(json.dumps({'decoded': len(digests), 'pinned': len(pins) or 'written'}))


if __name__ == '__main__':
    main()
