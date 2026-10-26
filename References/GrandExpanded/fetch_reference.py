#!/usr/bin/env python3
"""Fetch/verify the pre-locked expanded grand split without extracting features.

The new files are authenticated against Git blob identities from the pinned
upstream commit. First acquisition then pins SHA256 and decoded PCM identities.
Reserved recordings are only format/hash verified; their sound is not analyzed.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_blob_sha(path):
    data = path.read_bytes()
    return hashlib.sha1(b'blob ' + str(len(data)).encode('ascii') + b'\0' + data).hexdigest()


def load_pcm_helper():
    spec = importlib.util.spec_from_file_location(
        'keyra_pinned_pcm', PROJECT/'Research/GrandPianoV2/reference/fetch_reference.py')
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    return helper


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-only', action='store_true')
    parser.add_argument('--acquire', action='store_true', help='Pin initial SHA256/PCM only after Git blob authentication')
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    if args.jobs < 1 or (args.verify_only and args.acquire):
        parser.error('Use positive jobs and choose verification or initial acquisition')
    manifest_path = ROOT/'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    if sha(ROOT/'split.json') != manifest['split_sha256']:
        raise RuntimeError('Locked split changed')
    helper = load_pcm_helper()

    def get(item):
        flac = ROOT/item['flac_path']
        wav = ROOT/item['wav_path']
        if not flac.exists():
            if args.verify_only:
                raise RuntimeError(f'Missing {flac}')
            flac.parent.mkdir(parents=True, exist_ok=True)
            temporary = flac.with_suffix('.download')
            subprocess.run(['curl', '-fsSL', '--retry', '2', '--max-time', '120',
                            item['source_url'], '-o', str(temporary)], check=True)
            if temporary.stat().st_size != item['flac_bytes'] or git_blob_sha(temporary) != item['git_blob_sha1']:
                temporary.unlink()
                raise RuntimeError(f'Pinned Git blob mismatch: {item["id"]}')
            temporary.replace(flac)
        if flac.stat().st_size != item['flac_bytes'] or git_blob_sha(flac) != item['git_blob_sha1']:
            raise RuntimeError(f'Pinned FLAC identity mismatch: {item["id"]}')
        flac_sha = sha(flac)
        if item.get('flac_sha256') is not None and flac_sha != item['flac_sha256']:
            raise RuntimeError(f'FLAC SHA256 mismatch: {item["id"]}')
        if not wav.exists():
            if args.verify_only:
                raise RuntimeError(f'Missing {wav}')
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(flac),
                            '-c:a', 'pcm_s24le', str(wav)], check=True)
        pcm = helper.decoded_pcm_identity(wav)
        if pcm['sample_rate'] != 48000 or pcm['channels'] != 2 or pcm['pcm_bits'] != 24:
            raise RuntimeError(f'Unexpected source PCM format: {item["id"]}')
        if item.get('decoded_pcm') is not None and pcm != item['decoded_pcm']:
            raise RuntimeError(f'Decoded PCM mismatch: {item["id"]}')
        if not args.acquire and (item.get('flac_sha256') is None or item.get('decoded_pcm') is None):
            raise RuntimeError('Unpinned acquisition metadata; run initial --acquire after reviewing the split')
        updated = dict(item, flac_sha256=flac_sha, wav_sha256=sha(wav), decoded_pcm=pcm)
        return updated

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        verified = list(pool.map(get, manifest['samples']))
    if args.acquire:
        manifest['samples'] = verified
        manifest['initial_acquisition_verified'] = True
        manifest_path.write_text(json.dumps(manifest, indent=2, allow_nan=False)+'\n')
    print(json.dumps({'verified': True, 'source_commit': manifest['source_commit'],
                      'samples': len(verified), 'features_extracted_by_this_command': False,
                      'git_blob_matches': True, 'pcm_matches': True,
                      'manifest_sha256': sha(manifest_path)}, indent=2))


if __name__ == '__main__':
    main()
