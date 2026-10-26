#!/usr/bin/env python3
"""Restore and verify immutable, CC0 upright evaluation WAVs; never modify audio."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parent


def check(data, item):
    blob = hashlib.sha1((f'blob {len(data)}\0').encode() + data).hexdigest()
    if (len(data) != item['bytes'] or blob != item['git_blob_sha1'] or
            hashlib.sha256(data).hexdigest() != item['wav_sha256']):
        raise RuntimeError(f"Pinned source mismatch: {item['id']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'manifest.json').read_text())

    def restore(item):
        path = ROOT / item['local_path']
        if path.exists():
            check(path.read_bytes(), item)
        else:
            if args.verify_only:
                raise RuntimeError(f'Missing {path}')
            with urllib.request.urlopen(item['source_url'], timeout=90) as response:
                data = response.read()
            check(data, item)
            path.parent.mkdir(parents=True, exist_ok=True)
            temporary = path.with_suffix('.download')
            temporary.write_bytes(data)
            temporary.replace(path)
        return item['id']

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        done = list(pool.map(restore, manifest['samples']))
    print(json.dumps({'verified': True, 'source_commit': manifest['source_commit'],
                      'samples': len(done), 'ids': done}, indent=2))


if __name__ == '__main__':
    main()
