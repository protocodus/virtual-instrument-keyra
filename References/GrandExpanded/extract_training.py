#!/usr/bin/env python3
"""Extract only the locked expanded training set; never read reserved test audio."""
from __future__ import annotations
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    split_path = ROOT/'split.json'
    manifest_path = ROOT/'manifest.json'
    split = json.loads(split_path.read_text())
    manifest = json.loads(manifest_path.read_text())
    if sha(split_path) != manifest['split_sha256']:
        raise RuntimeError('Locked split changed')
    expected = set(split['training_ids'])
    fresh = set(split['fresh_validation_ids'])
    if len(expected) != 26 or len(fresh) != 7 or expected.intersection(fresh):
        raise RuntimeError('Expanded train/reserved roles changed')
    old_path = PROJECT/'Research/GrandPianoV2/benchmark/reference_features.json'
    if sha(old_path) != manifest['original_reference_features_sha256']:
        raise RuntimeError('Frozen original features changed')
    old_features = json.loads(old_path.read_text())
    spec = importlib.util.spec_from_file_location('keyra_grand_benchmark',
             PROJECT/'Research/GrandPianoV2/tools/benchmark.py')
    benchmark = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(benchmark)
    pcm_spec = importlib.util.spec_from_file_location('keyra_grand_pcm',
               PROJECT/'Research/GrandPianoV2/reference/fetch_reference.py')
    pcm_helper = importlib.util.module_from_spec(pcm_spec)
    pcm_spec.loader.exec_module(pcm_helper)
    rows = []
    originals = {row['id']: row for row in old_features['samples'] if row['split'] == 'train'}
    files = {row['id']: row for row in manifest['samples']}
    locked = {row['id']: row for row in split['samples']}
    for name in split['training_ids']:
        if name in originals:
            # Reuse the exact frozen numerical measurements. Provenance of the
            # original ten cases stays distinct from the new acquisitions.
            row = dict(originals[name])
            row['feature_provenance'] = 'Frozen original TRAIN10 reference features; numeric measurements unchanged.'
        else:
            item = files[name]
            if item['role'] != 'train':
                raise RuntimeError(f'Refuse feature extraction of reserved recording: {name}')
            path = ROOT/item['wav_path']
            pcm = pcm_helper.decoded_pcm_identity(path)
            if pcm != item['decoded_pcm']:
                raise RuntimeError(f'Decoded training PCM mismatch: {name}')
            row = benchmark.extract_features(path, locked[name]['midi'])
            row['path'] = str(path.relative_to(PROJECT))
            row['split'] = 'train'
            row['midi_velocity'] = locked[name]['midi_velocity']
            row['feature_provenance'] = 'New locked training acquisition; unchanged benchmark extraction.'
        row['expanded_role'] = 'train'
        rows.append(row)
        print(f'{name}: training only', flush=True)
    if {row['id'] for row in rows} != expected:
        raise RuntimeError('Training export inventory mismatch')
    result = {'schema_version': 1, 'analysis': benchmark.ANALYSIS,
              'source_commit': split['source_commit'], 'split_sha256': sha(split_path),
              'manifest_sha256': sha(manifest_path), 'original_features_sha256': sha(old_path),
              'reserved_recordings_opened_for_feature_extraction': False,
              'samples': rows}
    (ROOT/'train_features.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(ROOT/'train_features.json')


if __name__ == '__main__':
    main()
