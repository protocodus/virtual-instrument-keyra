#!/usr/bin/env python3
"""Extract the unchanged grand benchmark measurements with explicit source mapping.

Source velocity layers are ordinal. Analysis layer/velocity proxies are inputs
for comparing models, not documented upstream velocity bins or hammer speeds.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--train-only', action='store_true')
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location(
        'keyra_grand_benchmark', PROJECT / 'Research/GrandPianoV2/tools/benchmark.py')
    benchmark = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(benchmark)
    manifest = json.loads((ROOT / 'manifest.json').read_text())
    records = []
    selected = [r for r in manifest['samples'] if not args.train_only or r['split'] == 'train']
    with tempfile.TemporaryDirectory(prefix='keyra-upright-analysis-') as temp:
        for item in selected:
            source = ROOT / item['local_path']
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            if digest != item['wav_sha256']:
                raise RuntimeError(f"Reference hash mismatch: {item['id']}")
            # Alias only the filename convention. The WAV bytes, duration,
            # onset, levels and channels are never edited or normalized.
            alias = Path(temp) / (item['scientific_pitch'] + 'v' +
                                  str(item['analysis_layer_proxy']) + '.wav')
            alias.symlink_to(source.resolve())
            row = benchmark.extract_features(alias, midi=item['midi'])
            alias.unlink()
            row.update(id=item['feature_id'], path=item['local_path'],
                       split=item['split'], reference_id=item['id'],
                       source_layer=item['source_layer'],
                       source_round_robin=item['source_round_robin'],
                       source_note_label=item['source_note_label'],
                       midi_velocity=item['render_velocity_proxy'],
                       velocity_is_proxy=True,
                       velocity_provenance=manifest['proxy_caveat'])
            records.append(row)
            print(f"{row['id']}: {row['split']}")
    result = {'schema_version': 1, 'analysis': benchmark.ANALYSIS,
              'benchmark_script': 'Research/GrandPianoV2/tools/benchmark.py',
              'benchmark_script_sha256': hashlib.sha256(Path(spec.origin).read_bytes()).hexdigest(),
              'source_manifest': 'manifest.json', 'source_commit': manifest['source_commit'],
              'velocity_caveat': manifest['proxy_caveat'], 'samples': records}
    destination = ROOT / ('train_features.json' if args.train_only else 'reference_features.json')
    destination.write_text(json.dumps(result, indent=2) + '\n')
    print(destination)


if __name__ == '__main__':
    main()
