#!/usr/bin/env python3
"""Fetch and verify the opening of the MAESTRO performances Keyra's phrases are
measured against.

MAESTRO v3.0.0 (Hawthorne et al., ICLR 2019; CC BY-NC-SA 4.0) holds concert
performances from the International Piano-e-Competition on Yamaha Disklavier
grands: each a stereo recording with the keys, their velocities and the three
pedals as the piano's own MIDI, aligned to about 3 ms. The pianos, halls and
microphones are none of Keyra's and differ from year to year.

The archive is 108 GB, so each performance is read out of the published zip by
range request and only its first 60 s is kept: the PCM as it stands, in a WAV
header of that length, and the whole MIDI. Three performances a year: ordered
by the SHA-1 of the audio's file name, the first two of MAESTRO's train split
by different composers are train here and the first of its validation split
is dev. Its test split is left unopened. The audio is fetched into the ignored
out/ tree and never enters the repository or the instrument;
Tools/corpus/maestro-v3.json pins every file's SHA256.

  python3 Tools/fetch_maestro.py            # fetch what is missing, verify all
  python3 Tools/fetch_maestro.py --pin      # (re)write the pins from the files
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import struct
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'Tools/corpus/maestro-v3.json'
BASE = 'https://storage.googleapis.com/magentadata/datasets/maestro/v3.0.0/maestro-v3.0.0'
SECONDS = 60


class Remote(io.RawIOBase):
    """The published zip, read by range request."""

    def __init__(self, url, block=1 << 22):
        self.url, self.block, self.position, self.blocks = url, block, 0, {}
        with urllib.request.urlopen(urllib.request.Request(url, method='HEAD')) as reply:
            self.size = int(reply.headers['Content-Length'])

    def seekable(self):
        return True

    def readable(self):
        return True

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        self.position = offset + (0, self.position, self.size)[whence]
        return self.position

    def read(self, count=-1):
        count = self.size - self.position if count < 0 else count
        out = b''
        while count > 0 and self.position < self.size:
            index, offset = divmod(self.position, self.block)
            if index not in self.blocks:
                first = index * self.block
                request = urllib.request.Request(self.url, headers={
                    'Range': f'bytes={first}-{min(self.size, first+self.block)-1}'})
                with urllib.request.urlopen(request) as reply:
                    self.blocks = {index: reply.read()}
            part = self.blocks[index][offset:offset+count]
            out += part
            self.position += len(part)
            count -= len(part)
        return out


def selection():
    """Per year two train performances and one dev, as the head of this file has them."""
    with urllib.request.urlopen(BASE + '.csv') as reply:
        rows = list(csv.DictReader(io.TextIOWrapper(reply, 'utf-8')))
    rows.sort(key=lambda row: hashlib.sha1(row['audio_filename'].encode()).hexdigest())
    chosen = []
    for year in sorted({row['year'] for row in rows}):
        train = [row for row in rows if row['year'] == year and row['split'] == 'train']
        second = next(row for row in train if row['canonical_composer'] != train[0]['canonical_composer'])
        dev = next(row for row in rows if row['year'] == year and row['split'] == 'validation')
        chosen += [(row, role) for row, role in ((train[0], 'train'), (second, 'train'), (dev, 'dev'))]
    return [{'id': f'{row["year"]}-{hashlib.sha1(row["audio_filename"].encode()).hexdigest()[:8]}',
             'role': role, 'year': int(row['year']), 'composer': row['canonical_composer'],
             'title': row['canonical_title'], 'audio': row['audio_filename'], 'midi': row['midi_filename']}
            for row, role in chosen]


def opening(member):
    """The first SECONDS of a PCM WAV read forward, as a WAV of that length."""
    riff = member.read(12)
    if riff[:4] != b'RIFF' or riff[8:] != b'WAVE':
        raise RuntimeError('not a WAV')
    while True:
        name, size = struct.unpack('<4sI', member.read(8))
        if name == b'data':
            break
        chunk = member.read(size + (size & 1))
        if name == b'fmt ':
            form = chunk[:16]
    code, channels, rate, _, frame, _ = struct.unpack('<HHIIHH', form)
    if code != 1:
        raise RuntimeError('not PCM')
    data = member.read(min(size, SECONDS*rate*frame))
    return (b'RIFF' + struct.pack('<I', 36+len(data)) + b'WAVEfmt ' + struct.pack('<I', 16) + form
            + b'data' + struct.pack('<I', len(data)) + data)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--out', type=Path, default=ROOT/'out/maestro')
    parser.add_argument('--pin', action='store_true', help='write the SHA256 pins from the fetched files')
    args = parser.parse_args()
    items = selection() if args.pin else json.loads(MANIFEST.read_text())['files']
    args.out.mkdir(parents=True, exist_ok=True)
    archive = None
    for item in items:
        for kind, suffix in (('audio', '.wav'), ('midi', '.midi')):
            path = args.out/(item['id']+suffix)
            if not path.exists():
                archive = archive or zipfile.ZipFile(Remote(BASE + '.zip'))
                with archive.open('maestro-v3.0.0/' + item[kind]) as member:
                    part = path.with_name(path.name + '.part')
                    part.write_bytes(opening(member) if kind == 'audio' else member.read())
                    part.replace(path)
            digest = sha256(path)
            if args.pin:
                item[kind+'_sha256'] = digest
            elif item[kind+'_sha256'] != digest:
                raise RuntimeError(f'{path.name}: SHA256 differs from the pin')
    if args.pin:
        MANIFEST.write_text(json.dumps({
            'title': 'MAESTRO v3.0.0', 'author': 'Hawthorne et al., ICLR 2019',
            'instrument': 'Yamaha Disklavier concert grands, International Piano-e-Competition',
            'license': 'CC BY-NC-SA 4.0',
            'license_url': 'https://creativecommons.org/licenses/by-nc-sa/4.0/',
            'distribution': 'https://magenta.tensorflow.org/datasets/maestro', 'archive': BASE + '.zip',
            'excerpt': f'the first {SECONDS} s of each recording, PCM unchanged; the whole MIDI',
            'files': items}, indent=1, ensure_ascii=False)+'\n')
    print(json.dumps({'verified': 2*len(items), 'pinned': 'written' if args.pin else 2*len(items)}))


if __name__ == '__main__':
    main()
