#!/usr/bin/env python3
"""Authenticate the locked mechanism TRAIN corpus; never open reserved audio.

The initial --acquire run pins SHA256 and decoded PCM only after the immutable
Git blob and byte count match. Normal runs enforce those pins. Evaluation needs
a separate frozen-candidate protocol, not a switch on this acquisition tool.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
from urllib.parse import quote

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT / 'References/Mechanisms'
COMMIT = '3382bf9496bba2486f5ab0de55a264d1dfc38404'
EXPECTED_TRAIN = {'key-release-A0', 'key-release-C4', 'key-release-C8',
                  'pedal-D1', 'pedal-U1', 'string-release-S-C2',
                  'string-release-L-C4', 'string-release-V3-C6'}
EXPECTED_RESERVED = {'key-release-C1', 'key-release-C3', 'key-release-C6',
                     'pedal-D2', 'pedal-U2', 'string-release-S-C4',
                     'string-release-L-C6', 'string-release-V3-C2'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def git_blob(path):
    data = Path(path).read_bytes()
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def pcm_helper():
    path = PROJECT / 'Research/GrandPianoV2/reference/fetch_reference.py'
    spec = importlib.util.spec_from_file_location('keyra_mechanism_pcm', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_pcm_digest(flac):
    """Bind an existing WAV to actual source samples, not only manifest fields."""
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(flac),
                                   '-map', '0:a:0', '-c:a', 'pcm_s24le', '-f', 's24le', '-'])
    return hashlib.sha256(raw).hexdigest()


def locked_inputs():
    split = json.loads((ROOT / 'split.json').read_text())
    lock = json.loads((ROOT / 'split-lock.json').read_text())
    inventory = json.loads((ROOT / 'upstream-inventory.json').read_text())
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    if set(split['training_ids']) != EXPECTED_TRAIN or set(split['reserved_fresh_evaluation_ids']) != EXPECTED_RESERVED:
        raise RuntimeError('Locked mechanism roles changed')
    if sha(ROOT / 'split.json') != lock['split_sha256'] or sha(ROOT / 'upstream-inventory.json') != lock['inventory_sha256']:
        raise RuntimeError('Locked mechanism split or inventory changed')
    for field, name in (('split_sha256', 'split.json'), ('split_lock_sha256', 'split-lock.json'),
                        ('inventory_sha256', 'upstream-inventory.json')):
        if manifest[field] != sha(ROOT / name):
            raise RuntimeError(f'Manifest binding changed: {name}')
    if any(x.get('source_commit') != COMMIT for x in (split, inventory, manifest)):
        raise RuntimeError('Pinned source commit changed')
    by_id = {x['id']: x for x in split['samples']}
    if len(by_id) != 16 or len(manifest['samples']) != 16:
        raise RuntimeError('Mechanism inventory must contain 16 unique cases')
    by_path = {x['path']: x for x in inventory['mechanism_audio_metadata_only']}
    blobs = []
    for row in manifest['samples']:
        locked = by_id.get(row['id'])
        if locked is None or any(row.get(k) != v for k, v in locked.items()):
            raise RuntimeError('Manifest role or sample identity differs from split')
        entry = by_path.get(row['source_path'])
        if entry is None or row['source_path'] != 'Samples/' + row['source_sample'] or any(
                row[k] != entry[v] for k, v in (('git_blob_sha1', 'git_blob_sha1'), ('flac_bytes', 'bytes'))):
            raise RuntimeError('Manifest Git identity differs from pinned inventory')
        if row['flac_path'] != 'recordings/' + row['source_sample'] or row['wav_path'] != (
                'recordings/' + Path(row['source_sample']).with_suffix('.wav').name):
            raise RuntimeError('Unexpected local recording path')
        expected_url = f'https://raw.githubusercontent.com/sfzinstruments/SalamanderGrandPiano/{COMMIT}/' + row['source_path']
        if row['source_url'] != expected_url:
            raise RuntimeError('Unexpected source URL')
        blobs.append(row['git_blob_sha1'])
        if row['role'] == 'reserved_fresh_evaluation':
            reserved_paths = [ROOT / row[k] for k in ('flac_path', 'wav_path')]
            reserved_paths += [reserved_paths[0].with_suffix('.download'), reserved_paths[1].with_suffix('.decode.wav')]
            if any(p.exists() for p in reserved_paths):
                raise RuntimeError(f'Reserved mechanism audio unexpectedly present: {row["id"]}')
            if row.get('flac_sha256') or row.get('decoded_pcm'):
                raise RuntimeError('Reserved audio was pinned through the TRAIN manifest')
    if len(set(blobs)) != 16:
        raise RuntimeError('Audio blob crosses TRAIN/evaluation boundaries')
    for name, digest in manifest['upstream_text_files'].items():
        if sha(ROOT / name) != digest:
            raise RuntimeError(f'Pinned source/license text changed: {name}')
    return split, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--acquire', action='store_true', help='Initial pins after Git authentication')
    parser.add_argument('--verify-only', action='store_true')
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 8 or args.acquire and args.verify_only:
        parser.error('Choose acquisition or verification and 1–8 jobs')
    split, manifest = locked_inputs()
    tool_digest = sha(Path(__file__))
    started = datetime.datetime.now(datetime.timezone.utc).isoformat()
    initial_manifest_sha = sha(ROOT / 'manifest.json')
    immutable = {n: sha(ROOT / n) for n in ('split.json', 'split-lock.json', 'upstream-inventory.json')}
    helper = pcm_helper()
    rows = [x for x in manifest['samples'] if x['role'] == 'train']
    if not args.acquire and any(not x.get('flac_sha256') or not x.get('decoded_pcm') for x in rows):
        raise RuntimeError('Initial TRAIN acquisition requires --acquire')

    def get(row):
        flac, wav = ROOT / row['flac_path'], ROOT / row['wav_path']
        if not flac.exists():
            if args.verify_only:
                raise RuntimeError(f'Missing {flac}')
            flac.parent.mkdir(parents=True, exist_ok=True)
            temporary = flac.with_suffix('.download')
            subprocess.run(['curl', '-fsSL', '--retry', '2', '--max-time', '120',
                            quote(row['source_url'], safe=':/'), '-o', str(temporary)], check=True)
            if temporary.stat().st_size != row['flac_bytes'] or git_blob(temporary) != row['git_blob_sha1']:
                temporary.unlink()
                raise RuntimeError(f'Pinned Git blob mismatch: {row["id"]}')
            temporary.replace(flac)
        if flac.stat().st_size != row['flac_bytes'] or git_blob(flac) != row['git_blob_sha1']:
            raise RuntimeError(f'Pinned Git blob mismatch: {row["id"]}')
        digest = sha(flac)
        if row.get('flac_sha256') and row['flac_sha256'] != digest:
            raise RuntimeError(f'Pinned SHA256 mismatch: {row["id"]}')
        stream = json.loads(subprocess.check_output([
            'ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries',
            'stream=sample_rate,channels,bits_per_raw_sample,sample_fmt',
            '-of', 'json', str(flac)], text=True))['streams'][0]
        source_format = {'sample_rate': int(stream['sample_rate']), 'channels': int(stream['channels']),
                         'bits_per_raw_sample': int(stream['bits_per_raw_sample']),
                         'sample_fmt': stream['sample_fmt']}
        if tuple(source_format[k] for k in ('sample_rate', 'channels', 'bits_per_raw_sample')) != (48000, 2, 24):
            raise RuntimeError(f'Unexpected original FLAC format: {row["id"]}')
        if row.get('source_format') and row['source_format'] != source_format:
            raise RuntimeError(f'Pinned original format changed: {row["id"]}')
        if not wav.exists():
            if args.verify_only:
                raise RuntimeError(f'Missing {wav}')
            temporary = wav.with_suffix('.decode.wav')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(flac),
                            '-c:a', 'pcm_s24le', str(temporary)], check=True)
            temporary.replace(wav)
        pcm = helper.decoded_pcm_identity(wav)
        if (pcm['sample_rate'], pcm['channels'], pcm['pcm_bits']) != (48000, 2, 24):
            raise RuntimeError(f'Unexpected recording format: {row["id"]}')
        if row.get('decoded_pcm') and row['decoded_pcm'] != pcm:
            raise RuntimeError(f'Decoded PCM mismatch: {row["id"]}')
        source_pcm = source_pcm_digest(flac)
        if pcm['sha256'] != source_pcm:
            raise RuntimeError(f'WAV samples do not match authenticated FLAC: {row["id"]}')
        return dict(row, flac_sha256=digest, wav_sha256=sha(wav), decoded_pcm=pcm,
                    source_format=source_format, source_decoded_pcm_sha256=source_pcm,
                    duration_seconds=pcm['frames'] / pcm['sample_rate'])

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        verified = list(pool.map(get, rows))
    if sha(ROOT / 'manifest.json') != initial_manifest_sha or sha(Path(__file__)) != tool_digest or any(sha(ROOT / n) != h for n, h in immutable.items()):
        raise RuntimeError('Acquisition inputs changed while downloading')
    if args.acquire:
        by_id = {x['id']: x for x in verified}
        manifest['samples'] = [by_id.get(x['id'], x) for x in manifest['samples']]
        manifest['initial_training_acquisition_verified'] = True
        write(ROOT / 'manifest.json', manifest)
    locked_inputs()
    receipt = {'schema_version': 1, 'verified': True, 'training_files': len(verified),
               'started_at_utc': started, 'verified_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'training_ids': sorted(x['id'] for x in verified),
               'reserved_files_downloaded': [], 'reserved_files_decoded_or_analyzed': [],
               'manifest_sha256': sha(ROOT / 'manifest.json'), **immutable,
               'source_flac_and_wav_decoded_pcm_match': True,
               'tool_sha256': sha(Path(__file__)), 'features_extracted': False}
    write(ROOT / 'verification.json', receipt)
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
