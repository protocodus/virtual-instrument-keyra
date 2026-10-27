#!/usr/bin/env python3
"""Fetch the locked C1–C8/A0 grand corpus; never decode fresh evaluation audio.

Default acquisition covers TRAIN18 and the seven already observed regression
cases. --include-reserved-bytes optionally downloads only the authenticated FLAC
bytes of A0v8/C8v8. There is deliberately no reserved-audio decode option.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT / 'References/GrandFullRange'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha(path):
    data = path.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def load_pcm_helper():
    path = PROJECT / 'Research/GrandPianoV2/reference/fetch_reference.py'
    spec = importlib.util.spec_from_file_location('keyra_full_range_pcm', path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    return helper


def locked_inputs():
    split_path, manifest_path = ROOT / 'split.json', ROOT / 'manifest.json'
    split = json.loads(split_path.read_text())
    manifest = json.loads(manifest_path.read_text())
    lock = json.loads((ROOT / 'split-lock.json').read_text())
    if sha(split_path) != lock['split_sha256'] or sha(split_path) != manifest['split_sha256']:
        raise RuntimeError('Locked full-range split changed')
    if sha(ROOT / 'split-lock.json') != manifest['split_lock_sha256']:
        raise RuntimeError('Full-range split receipt changed')
    if set(split['reserved_fresh_evaluation_ids']) != {'A0v8', 'C8v8'}:
        raise RuntimeError('Reserved extreme-note roles changed')
    if len(split['training_ids']) != 18 or len(split['combined_training_ids']) != 34:
        raise RuntimeError('Locked training inventory changed')
    roles = {row['id']: row['role'] for row in split['samples']}
    if {row['id']: row['role'] for row in manifest['samples']} != roles:
        raise RuntimeError('Manifest roles differ from the locked split')
    for name, expected in manifest['upstream_text_files'].items():
        if sha(ROOT / name) != expected:
            raise RuntimeError(f'Pinned license/source text changed: {name}')
    return split, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--acquire', action='store_true', help='Initial SHA/PCM pinning after Git-blob authentication')
    parser.add_argument('--verify-only', action='store_true')
    parser.add_argument('--training-only', action='store_true', help='Skip the seven known regression cases')
    parser.add_argument('--include-reserved-bytes', action='store_true', help='FLAC bytes/hash only; never decode the two fresh cases')
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 8 or args.acquire and args.verify_only:
        parser.error('Use 1–8 jobs and choose acquisition or verification')
    split, manifest = locked_inputs()
    helper = load_pcm_helper()
    samples = [row for row in manifest['samples']
               if row['role'] == 'train' or row['role'] == 'historical_evaluation' and not args.training_only
               or row['role'] == 'reserved_fresh_evaluation' and args.include_reserved_bytes]
    if not args.acquire and any(row.get('flac_sha256') is None or
                               row['role'] != 'reserved_fresh_evaluation' and row.get('decoded_pcm') is None
                               for row in samples):
        raise RuntimeError('Initial acquisition is unpinned; use --acquire to authenticate and pin it')

    def get(item):
        flac, wav = ROOT / item['flac_path'], ROOT / item['wav_path']
        fresh = item['role'] == 'reserved_fresh_evaluation'
        if fresh and wav.exists():
            raise RuntimeError(f'Unexpected decoded fresh evaluation file: {wav}')
        if not flac.exists():
            if args.verify_only:
                raise RuntimeError(f'Missing {flac}')
            flac.parent.mkdir(parents=True, exist_ok=True)
            reuse = PROJECT / item.get('reuse_flac_path', '__no_reuse__')
            temporary = flac.with_suffix('.download')
            if reuse.is_file():
                shutil.copy2(reuse, temporary)
            else:
                subprocess.run(['curl', '-fsSL', '--retry', '2', '--max-time', '120',
                                item['source_url'], '-o', str(temporary)], check=True)
            if temporary.stat().st_size != item['flac_bytes'] or git_blob_sha(temporary) != item['git_blob_sha1']:
                temporary.unlink()
                raise RuntimeError(f'Pinned Git blob mismatch: {item["id"]}')
            temporary.replace(flac)
        if flac.stat().st_size != item['flac_bytes'] or git_blob_sha(flac) != item['git_blob_sha1']:
            raise RuntimeError(f'Pinned FLAC identity mismatch: {item["id"]}')
        digest = sha(flac)
        if item.get('flac_sha256') and item['flac_sha256'] != digest:
            raise RuntimeError(f'Pinned FLAC SHA256 mismatch: {item["id"]}')
        result = dict(item, flac_sha256=digest)
        if fresh:
            return result
        if not wav.exists():
            if args.verify_only:
                raise RuntimeError(f'Missing {wav}')
            wav.parent.mkdir(parents=True, exist_ok=True)
            reuse = PROJECT / item.get('reuse_wav_path', '__no_reuse__')
            if reuse.is_file():
                shutil.copy2(reuse, wav)
            else:
                subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(flac),
                                '-c:a', 'pcm_s24le', str(wav)], check=True)
        pcm = helper.decoded_pcm_identity(wav)
        if (pcm['sample_rate'], pcm['channels'], pcm['pcm_bits']) != (48000, 2, 24):
            raise RuntimeError(f'Unexpected source format: {item["id"]}')
        if item.get('decoded_pcm') and pcm != item['decoded_pcm']:
            raise RuntimeError(f'Pinned decoded PCM mismatch: {item["id"]}')
        result.update(wav_sha256=sha(wav), decoded_pcm=pcm,
                      duration_seconds=pcm['frames'] / pcm['sample_rate'])
        return result

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        verified = list(pool.map(get, samples))
    if args.acquire:
        by_id = {row['id']: row for row in verified}
        manifest['samples'] = [by_id.get(row['id'], row) for row in manifest['samples']]
        manifest['initial_training_acquisition_verified'] = all(
            row.get('decoded_pcm') is not None for row in manifest['samples'] if row['role'] == 'train')
        (ROOT / 'manifest.json').write_text(json.dumps(manifest, indent=2, allow_nan=False) + '\n')
    receipt = {'verified': True, 'split_sha256': sha(ROOT / 'split.json'),
               'source_commit': manifest['source_commit'],
               'verified_cases': len(verified),
               'training_cases': sum(row['role'] == 'train' for row in verified),
               'historical_cases': sum(row['role'] == 'historical_evaluation' for row in verified),
               'fresh_reserved_downloaded_bytes_only': [row['id'] for row in verified if row['role'] == 'reserved_fresh_evaluation'],
               'fresh_reserved_decoded': False, 'features_extracted': False,
               'manifest_sha256': sha(ROOT / 'manifest.json')}
    (ROOT / 'verification.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
