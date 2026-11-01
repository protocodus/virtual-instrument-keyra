#!/usr/bin/env python3
"""Import the Yamaha C3 acoustic reference without altering its PCM samples.

Protocol: read the original DecentSampler ZIP and its declared sample regions,
retain native stereo PCM24/48 kHz, and apply no gain, trim, filtering or resampling.
DecentSampler's `end` is inclusive (the documented default is file length minus
one), so a region contains end-start+1 frames. Repeated mappings of one region
become aliases of a single file. SHA256 pins cover the ZIP, preset, monolith,
individual PCM regions and emitted WAVs. Exact PCM duplicates cannot cross roles.
The ZIP is read forward without materializing the monolith. By default only
metadata is generated/verified. Decode selected cases on demand into a bounded
cache; all regions are still hashed, even when their WAVs are not retained.

The split is chosen from pitch numbers alone, before acoustic analysis: every
fifth recorded pitch starting with the third goes to dev; all other pitches go
to train. All velocities, declared sequence positions, pedals and releases of
one root pitch stay together. No sealed set or new user-facing piano is created.
The capture's hammer velocity, microphone blend, processing and absolute gain
are uncalibrated. MIDI velocity bins describe preset playback, not strike force.

Only numeric metadata is tracked; source and output audio remain in ignored
out/yamaha-c3. This tool does not grant permission to redistribute the recordings.

  python3 Tools/decode_yamaha_c3.py --library /path/YamahaC3.dslibrary --pin
  python3 Tools/decode_yamaha_c3.py --library /path/YamahaC3.dslibrary
  python3 Tools/decode_yamaha_c3.py --library /path/YamahaC3.dslibrary --cases n60v1r1pup n60v1r1pdown

Sources: https://www.pianobook.co.uk/packs/yamaha-c3/
https://decentsampler-developers-guide.readthedocs.io/en/latest/the-groups-element.html
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
from pathlib import Path
import tempfile
import wave
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'out/yamaha-c3'
MANIFEST = ROOT / 'Tools/corpus/yamaha-c3.json'
SPLIT = ROOT / 'Tools/corpus/split-yamaha-c3-2026-11-01.json'
PRESET_MEMBER = 'YamahaC3/Yamaha_C3.dspreset'
MONOLITH_MEMBER = 'YamahaC3/samples/Monolith.wav'
LAYER_RANGES = {(1, 95): 1, (96, 109): 2, (110, 127): 3}
FORMAT_URL = 'https://decentsampler-developers-guide.readthedocs.io/en/latest/the-groups-element.html'


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1 << 20), b''):
            digest.update(block)
    return digest.hexdigest()


class ForwardHashReader:
    """Hash every source byte, including RIFF metadata skipped by wave.open."""
    def __init__(self, source):
        self.source = source
        self.position = 0
        self.consumed = 0
        self.digest = hashlib.sha256()

    def read(self, size=-1):
        if self.position < self.consumed:
            raise ValueError('source regions must be read in ascending, non-overlapping order')
        while self.consumed < self.position:
            skipped = self.source.read(min(1 << 20, self.position - self.consumed))
            if not skipped:
                raise ValueError('unexpected end of monolith')
            self.digest.update(skipped)
            self.consumed += len(skipped)
        data = self.source.read(size)
        self.digest.update(data)
        self.position += len(data)
        self.consumed += len(data)
        return data

    def tell(self):
        return self.position

    def seek(self, offset, whence=0):
        target = offset + (self.position if whence == 1 else 0)
        if whence not in (0, 1) or target < 0:
            raise ValueError('unsupported monolith seek')
        # wave.readframes first seeks to the data origin and then the requested
        # frame. Defer physical movement until read(), after both logical seeks.
        self.position = target
        return self.position

    def finish(self):
        self.position = self.consumed
        while self.read(1 << 20):
            pass
        return self.digest.hexdigest()


def inventory(preset: bytes) -> list[dict]:
    """Preserve every XML mapping, collapsing only identical source coordinates."""
    root = ET.fromstring(preset)
    regions = {}
    for group_index, group in enumerate(root.iter('group')):
        trigger = group.get('trigger', 'attack')
        if trigger not in ('attack', 'release'):
            raise ValueError(f'unsupported trigger: {trigger}')
        cc64 = [int(group.get('loCC64', 0)), int(group.get('hiCC64', 127))]
        if cc64 not in ([0, 63], [64, 127], [0, 127]):
            raise ValueError(f'unexpected pedal gating: {cc64}')
        pedal = 'ungated' if cc64 == [0, 127] else ('up' if cc64[0] == 0 else 'down')
        for sample_index, sample in enumerate(group.findall('sample')):
            attrs = dict(sample.attrib)
            if attrs['path'] != 'samples/Monolith.wav':
                raise ValueError(f'unexpected source path: {attrs["path"]}')
            midi = int(attrs['rootNote'])
            velocity = [int(attrs['loVel']), int(attrs['hiVel'])]
            layer = LAYER_RANGES.get(tuple(velocity)) if trigger == 'attack' else None
            if trigger == 'attack' and layer is None:
                raise ValueError(f'unexpected velocity bin: {velocity}')
            start, end = int(attrs['start']), int(attrs['end'])
            if not 0 <= start <= end:
                raise ValueError(f'invalid inclusive region: {start}..{end}')
            position = int(attrs.get('seqPosition', 1))
            item = {
                'kind': 'note' if trigger == 'attack' else 'key-release',
                'midi': midi, 'keys': [int(attrs['loNote']), int(attrs['hiNote'])],
                'velocity': velocity, 'layer': layer, 'pedal': pedal, 'cc64': cc64,
                'source': MONOLITH_MEMBER, 'start_frame': start, 'end_frame_inclusive': end,
                'frames': end - start + 1,
            }
            key = (item['source'], start, end)
            alias = {'mapping_id': f'g{group_index}s{sample_index}',
                     'group': dict(group.attrib), 'sample': attrs}
            if key in regions:
                previous = regions[key]
                if any(previous[field] != value for field, value in item.items()):
                    raise ValueError(f'one source region has inconsistent metadata: {key}')
                previous['mappings'].append(alias)
                previous['sequence_positions'].append(position)
            else:
                regions[key] = item | {'sequence_positions': [position], 'mappings': [alias]}

    items = []
    for item in regions.values():
        item['sequence_positions'] = sorted(set(item['sequence_positions']))
        if item['kind'] == 'note':
            identifier = (f'n{item["midi"]}v{item["layer"]}'
                          f'r{min(item["sequence_positions"])}p{item["pedal"]}')
        else:
            identifier = f'rel{item["midi"]}'
        items.append({'id': identifier} | item)
    if len({item['id'] for item in items}) != len(items):
        raise ValueError('distinct source regions produced the same file id')
    return sorted(items, key=lambda item: (item['midi'], item['kind'], item['layer'] or 0,
                                         item['pedal'], item['sequence_positions'][0]))


def pitch_roles(items: list[dict]) -> dict[int, str]:
    """Split metadata only: each fifth pitch, with a fixed offset, is development."""
    return {pitch: 'dev' if index % 5 == 2 else 'train'
            for index, pitch in enumerate(sorted({item['midi'] for item in items}))}


def read_region(reader: wave.Wave_read, start: int, end: int) -> bytes:
    # Official sample-attribute docs give end's default as file length minus 1.
    # Keep that inclusive final frame; no onset trimming or sampler interpolation.
    if not 0 <= start <= end < reader.getnframes():
        raise ValueError(f'region [{start}, {end}] is outside {reader.getnframes()} frames')
    reader.setpos(start)
    pcm = reader.readframes(end - start + 1)
    expected = (end - start + 1) * reader.getnchannels() * reader.getsampwidth()
    if len(pcm) != expected:
        raise ValueError('truncated PCM region')
    return pcm


def write_or_verify_wav(path: Path, pcm: bytes, params: wave._wave_params) -> str:
    if path.exists():
        with wave.open(str(path), 'rb') as reader:
            actual = reader.getparams()
            if (actual.nchannels, actual.sampwidth, actual.framerate, actual.comptype) != (
                    params.nchannels, params.sampwidth, params.framerate, params.comptype):
                raise ValueError(f'{path.name}: output WAV format differs from source')
            if actual.nframes * actual.nchannels * actual.sampwidth != len(pcm):
                raise ValueError(f'{path.name}: output frame count differs from source region')
            if reader.readframes(actual.nframes) != pcm:
                raise ValueError(f'{path.name}: output PCM differs from source region')
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=path.parent, suffix='.part.wav', delete=False) as pending:
                temporary = Path(pending.name)
                with wave.open(pending, 'wb') as writer:
                    writer.setnchannels(params.nchannels)
                    writer.setsampwidth(params.sampwidth)
                    writer.setframerate(params.framerate)
                    writer.writeframes(pcm)
            temporary.replace(path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
    return sha256(path)


def wav_sha256(pcm: bytes, params: wave._wave_params) -> str:
    """Pin the deterministic output container without storing its waveform."""
    buffer = io.BytesIO()
    with wave.open(buffer, 'wb') as writer:
        writer.setnchannels(params.nchannels)
        writer.setsampwidth(params.sampwidth)
        writer.setframerate(params.framerate)
        writer.writeframes(pcm)
    return hashlib.sha256(buffer.getbuffer()).hexdigest()


def assert_no_duplicate_leakage(items: list[dict], roles: dict[int, str]) -> None:
    by_pcm = defaultdict(set)
    for item in items:
        by_pcm[item['pcm_sha256']].add(roles[item['midi']])
    if any(len(role_set) > 1 for role_set in by_pcm.values()):
        raise ValueError('identical PCM appears in both train and dev; refusing to publish split')


def build_split(items: list[dict], roles: dict[int, str]) -> dict:
    assert_no_duplicate_leakage(items, roles)
    canonical = {}
    duplicates = {}
    for item in sorted(items, key=lambda entry: entry['id']):
        identity = canonical.setdefault(item['pcm_sha256'], item['id'])
        if identity != item['id']:
            duplicates[item['id']] = identity
    return {
        'name': 'yamaha-c3-2026-11-01', 'corpus': 'yamaha-c3.json',
        'written_before': 'acoustic feature extraction, model fitting or listening-based selection',
        'rules': [
            'Sort the recorded root MIDI pitches; index % 5 == 2 is dev, all others train.',
            'All velocities, pedal states, sequence positions and releases of one root pitch share its role.',
            'Repeated XML mappings of the same source region are aliases, never additional observations.',
            'Exact PCM SHA256 duplicates must not cross roles; importing fails if they do.',
            'duplicate_cases identifies additional equal-PCM regions; exclude these from observation counts and fitting weights.',
            'This is a development corpus with no sealed evaluation set.',
            'Playback velocity bins are uncalibrated; they are not measured hammer velocities.',
        ],
        'pitches': {role: [pitch for pitch, value in roles.items() if value == role]
                    for role in ('train', 'dev')},
        'cases': {item['id']: roles[item['midi']] for item in items},
        'duplicate_cases': duplicates,
    }


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, suffix='.part.json', mode='w',
                                         encoding='utf-8', delete=False) as pending:
            temporary = Path(pending.name)
            pending.write(json.dumps(value, indent=2) + '\n')
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--library', type=Path, required=True, help='original YamahaC3.dslibrary ZIP')
    parser.add_argument('--pin', action='store_true', help='write numeric manifest and deterministic split')
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument('--cases', nargs='+', help='retain only these canonical case WAVs')
    selection.add_argument('--role', choices=('train', 'dev'), help='retain all WAVs in this split role')
    selection.add_argument('--all', action='store_true', help='retain all case WAVs (requires a larger cache limit)')
    parser.add_argument('--cache-limit-mib', type=int, default=256,
                        help='maximum retained WAV cache size; default 256 MiB, never auto-deletes files')
    args = parser.parse_args()
    stored = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else None
    if not args.pin and stored is None:
        raise SystemExit('no manifest; run once with --pin to create the numeric source pins')
    archive_hash = sha256(args.library)
    if not args.pin and archive_hash != stored['archive']['sha256']:
        raise SystemExit('source library SHA256 differs from the pinned archive')

    with zipfile.ZipFile(args.library) as archive:
        preset = archive.read(PRESET_MEMBER)
        items = inventory(preset)
        if len(items) != 354 or sum(len(item['mappings']) for item in items) != 570:
            raise SystemExit('unexpected Yamaha C3 inventory: expected 570 mappings / 354 unique regions')
        if sorted({item['midi'] for item in items}) != list(range(21, 109, 3)):
            raise SystemExit('unexpected Yamaha C3 recorded pitches')
        roles = pitch_roles(items)
        requested = set(args.cases or [])
        unknown = requested - {item['id'] for item in items}
        if unknown:
            raise SystemExit(f'unknown case ids: {sorted(unknown)}')
        selected = {item['id'] for item in items if args.all or item['id'] in requested
                    or roles[item['midi']] == args.role}
        cached_files = {path.stem: path.stat().st_size for path in (OUT / 'wav').glob('*.wav')}
        projected = sum(cached_files.values()) + sum(item['frames'] * 6 + 44 for item in items
                                                    if item['id'] in selected and item['id'] not in cached_files)
        if args.cache_limit_mib <= 0 or projected > args.cache_limit_mib * (1 << 20):
            raise SystemExit(f'WAV cache would use {projected / (1 << 20):.1f} MiB; select fewer cases '
                             f'or explicitly raise --cache-limit-mib (currently {args.cache_limit_mib}).')
        with archive.open(MONOLITH_MEMBER) as source:
            hashed = ForwardHashReader(source)
            with wave.open(hashed, 'rb') as reader:
                params = reader.getparams()
                if (params.nchannels, params.sampwidth, params.framerate, params.comptype) != (2, 3, 48000, 'NONE'):
                    raise SystemExit(f'unexpected monolith PCM format: {params}')
                for item in sorted(items, key=lambda entry: entry['start_frame']):
                    pcm = read_region(reader, item['start_frame'], item['end_frame_inclusive'])
                    item['pcm_sha256'] = hashlib.sha256(pcm).hexdigest()
                    item['wav_sha256'] = wav_sha256(pcm, params)
                    path = OUT / 'wav' / (item['id'] + '.wav')
                    if item['id'] in selected or path.exists():
                        if write_or_verify_wav(path, pcm, params) != item['wav_sha256']:
                            raise ValueError(f'{item["id"]}: emitted WAV hash differs from native encoding')
            monolith_hash = hashed.finish()

    split = build_split(items, roles)
    for item in items:
        if item['id'] in split['duplicate_cases']:
            item['duplicate_pcm_of'] = split['duplicate_cases'][item['id']]
    counts = Counter(split['cases'].values())
    observation_counts = Counter(roles[item['midi']] for item in items if 'duplicate_pcm_of' not in item)
    manifest = {
        'title': 'Yamaha C3', 'author': 'wesleywilson29',
        'origin': 'https://www.pianobook.co.uk/packs/yamaha-c3/',
        'purpose': 'Acoustic reference for common piano behavior; not a user-facing Keyra instrument.',
        'capture': 'The creator describes a Yamaha C3 in a converted garage, with condenser microphones '
                   'near the piano holes, towels/foam treatment and an additional microphone underneath. '
                   'The monolith groups are labelled MIC1; their exact microphone blend is unknown.',
        'calibration_unknown': ['absolute recording gain', 'hammer velocity or strike force',
                                'microphone blend and precise positions', 'signal processing',
                                'timing of pedal motion within recordings'],
        'rights': 'No audio is redistributed. No licence file was found in the source archive; '
                  'the public download and these numeric pins do not grant redistribution rights.',
        'format': {'sample_rate': params.framerate, 'channels': params.nchannels,
                   'pcm_bits': params.sampwidth * 8, 'processing': 'none'},
        'archive': {'filename': args.library.name, 'sha256': archive_hash},
        'preset': {'member': PRESET_MEMBER, 'sha256': hashlib.sha256(preset).hexdigest()},
        'monolith': {'member': MONOLITH_MEMBER, 'sha256': monolith_hash, 'frames': params.nframes},
        'region_convention': {'start': 'zero-based inclusive frame', 'end': 'zero-based inclusive frame',
                              'frames': 'end - start + 1', 'source': FORMAT_URL},
        'mapping_count': sum(len(item['mappings']) for item in items),
        'unique_region_count': len(items), 'unique_pcm_count': len({item['pcm_sha256'] for item in items}),
        'velocity_bins': [{'layer': layer, 'range': list(bounds)} for bounds, layer in LAYER_RANGES.items()],
        'pedal': {'up': [0, 63], 'down': [64, 127],
                  'release': 'The release group is ungated by CC64; recorded pedal state is unknown.',
                  'interpretation': 'Preset endpoint selection only; no measured half-pedal trajectory.'},
        'sequence': 'Preserve declared seqPosition labels. No seqMode is specified by the source preset; '
                    'these labels do not establish playback sequencing or independent performances.',
        'deduplication': 'Identical monolith coordinates become one file with all XML mappings as aliases. '
                         'Equal PCM at different coordinates is retained for traceability but marked duplicate_pcm_of; '
                         'exclude these aliases from observation counts and fitting weights. '
                         'PCM SHA256 identity is audited separately against cross-role leakage.',
        'split': SPLIT.name, 'role_counts': dict(sorted(counts.items())),
        'unique_observation_role_counts': dict(sorted(observation_counts.items())),
        'files': items,
    }
    if args.pin:
        write_json(MANIFEST, manifest)
        write_json(SPLIT, split)
    else:
        if manifest != stored:
            raise SystemExit('source metadata or decoded file hashes differ from pinned manifest')
        if not SPLIT.exists() or split != json.loads(SPLIT.read_text()):
            raise SystemExit('split differs from deterministic whole-pitch policy')
    print(f'{"Pinned" if args.pin else "Verified"} {manifest["mapping_count"]} mappings -> '
          f'{len(items)} regions / {manifest["unique_pcm_count"]} unique PCM recordings; '
          f'{counts["train"]} train, {counts["dev"]} dev; native stereo PCM24 at 48000 Hz.')
    print(f'Audio: {OUT.relative_to(ROOT)} (ignored); numeric metadata: {MANIFEST.relative_to(ROOT)}')
    print(f'Retained WAV cache: {projected / (1 << 20):.1f} MiB; {len(selected)} selected cases.')


if __name__ == '__main__':
    main()
