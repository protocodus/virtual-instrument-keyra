#!/usr/bin/env python3
"""Decode and verify the VCSL recordings Keyra's Kawai grand is measured
against.

The Versilian Community Sample Library (VCSL Keys, Versilian Studios) is
CC0. Its "Grand Piano, K" (the library list's "Grand Piano, Kawai", sampled
for VSCO 2 Pro) is a stereo pair in player position, 44.1 kHz/16-bit FLAC.
This reads a copy of the library and decodes into the ignored out/ tree, which
never enters the repository or the instrument, without gain, trim or
resampling. The library's SFZ maps every recording; Tools/corpus/vcsl-kawai.json
pins every file's SHA256.

  python3 Tools/decode_vcsl.py --library <VCSL_Keys folder>          # decode what is missing, verify all
  python3 Tools/decode_vcsl.py --library <VCSL_Keys folder> --pin    # (re)write the pins from the files
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SFZ = 'Grand Piano, K.sfz'
MANIFEST = ROOT / 'Tools/corpus/vcsl-kawai.json'
# A key let go plays the release take the SFZ maps to that key at this
# velocity: the middle of its velocity ranges, a typical touch.
RELEASE_VELOCITY = 80
# The library maps its lowest takes ("A#-1", pitch_keycenter 22) to A#0, but
# every one sounds A0: the strongest peak beside A#0's third partial sits 109
# to 112 cents under it in all three layers, 9 to 12 cents under A0's, as
# C1's sit 12 to 13 cents under C1's (0.1 to 2.1 s after the onset). They are
# taken as A0's, and so is the release take the SFZ plays for their keys.
RECORDED_PITCH = {22: 21}


def regions(sfz: Path):
    """The SFZ's regions with what their <global> and <group> set; commented
    regions are left out."""
    text = re.sub(r'//[^\n]*', '', sfz.read_text(encoding='utf-8', errors='replace'))
    scopes, out, current = {'global': {}, 'group': {}}, [], None
    for part in re.split(r'(<\w+>)', text):
        header = re.fullmatch(r'<(\w+)>', part.strip())
        if header:
            name = header.group(1)
            if name in scopes:
                if name == 'global':
                    scopes['group'] = {}
                scopes[name] = current = {}
            else:
                current = {}
                out.append((dict(scopes['global']) | dict(scopes['group']), current))
            continue
        if current is None:
            continue
        for line in part.split('\n'):
            found = list(re.finditer(r'(\w+)=', line))
            for i, m in enumerate(found):
                end = found[i + 1].start() if i + 1 < len(found) else len(line)
                current[m.group(1)] = line[m.end():end].strip()
    return [inherited | own for inherited, own in out]


def inventory(library: Path):
    """Every note the SFZ plays, layer by layer, and for each recorded pitch
    the release take its key plays when let go at RELEASE_VELOCITY. Keys the
    SFZ gives no release (from F6 up, the undamped keys, where its top group rings on) take the
    nearest lower pitch's, marked as carried."""
    rs = regions(library / SFZ)
    notes, releases = {}, []
    for r in rs:
        centre = int(r['pitch_keycenter'])
        item = {'midi': RECORDED_PITCH.get(centre, centre), 'keys': [int(r['lokey']), int(r['hikey'])],
                'velocity': [int(r.get('lovel', 0)), int(r.get('hivel', 127))], 'source': r['sample']}
        (releases if r.get('trigger') == 'release' else notes.setdefault(item['midi'], [])).append(item)
    items = []
    for midi, layers in sorted(notes.items()):
        for layer, item in enumerate(sorted(layers, key=lambda i: i['velocity'][0]), 1):
            items.append({'id': f'n{midi}v{layer}', 'kind': 'note'} | item | {'layer': layer, 'round_robin': 1})
    for midi in sorted(notes):
        heard = [r for r in releases if r['keys'][0] <= midi <= r['keys'][1]
                 and r['velocity'][0] <= RELEASE_VELOCITY <= r['velocity'][1]]
        carried = None
        if not heard:
            carried = max(r['midi'] for r in releases if r['midi'] < midi)
            heard = [r for r in releases if r['midi'] == carried
                     and r['velocity'][0] <= RELEASE_VELOCITY <= r['velocity'][1]]
        release = heard[0]
        items.append({'id': f'rel{midi}', 'kind': 'key-release', 'midi': midi, 'keys': release['keys'],
                      'velocity': release['velocity'], 'source': release['source']}
                     | ({'carried_from': carried} if carried else {}))
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
                        '-c:a', 'pcm_s16le', str(part)], check=True)
        part.replace(wav)
    return item['id'], digest


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--library', type=Path, required=True, help='the VCSL_Keys folder')
    parser.add_argument('--out', type=Path, default=ROOT / 'out/vcsl/kawai')
    parser.add_argument('--jobs', type=int, default=8)
    parser.add_argument('--pin', action='store_true', help='write the SHA256 pins from the library\'s files')
    args = parser.parse_args()
    stored = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    pins = {} if args.pin else {f['id']: f['flac_sha256'] for f in stored.get('files', [])}
    items = inventory(args.library)
    if not args.pin and {i['id'] for i in items} != set(pins):
        raise SystemExit('the SFZ maps other recordings than the manifest pins')
    with concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        digests = dict(pool.map(lambda i: decode(i, args.library, args.out, pins), items))
    if args.pin:
        MANIFEST.write_text(json.dumps({
            'title': 'VCSL Keys: Grand Piano, K', 'author': 'Versilian Studios (sampled for VSCO 2 Pro)',
            'instrument': 'a Kawai grand piano: VCSL names it "Grand Piano, K", Versilian\'s library list '
                          '"Grand Piano, Kawai"; model and size are not given',
            'license': 'CC0 1.0 (the Versilian Community Sample Library)',
            'capture': 'a stereo pair in player position ("Player" in every file name), 44.1 kHz/16-bit '
                       'stereo FLAC',
            'pitch_names': 'the library names middle C (MIDI 60) C3, an octave under the scientific pitch used '
                           'here; ids carry MIDI numbers, as the SFZ\'s pitch_keycenter gives them, except the '
                           'takes it names A#-1 and centres on A#0 (22), which sound A0 (21): see RECORDED_PITCH '
                           'in Tools/decode_vcsl.py',
            'velocity_layers': 'up to four per pitch, by the SFZ\'s lovel/hivel (0-54, 55-83, 84-106, 107-127 '
                               'where all four play); a layer is numbered from the softest the pitch has',
            'mixing': 'the SFZ (amp_veltrack 88) raises each region by its own volume opcode: the recordings '
                      'keep their dynamics, about 33 dB from the softest layer to the loudest at the median',
            'releases': f'rel<midi>: the release take the SFZ plays when that key is let go at velocity '
                        f'{RELEASE_VELOCITY}; from F6 up, the undamped keys, the SFZ maps none, so those keys carry the nearest '
                        'lower pitch\'s (carried_from)',
            'decoding': 'ffmpeg to PCM16 WAV, no gain, trim, resampling, denoising or EQ',
            'files': [item | {'flac_sha256': digests[item['id']]} for item in items]}, indent=1) + '\n')
    print(json.dumps({'verified': len(digests), 'pinned': len(pins) or 'written'}))


if __name__ == '__main__':
    main()
