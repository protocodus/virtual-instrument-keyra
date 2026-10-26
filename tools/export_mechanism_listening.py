#!/usr/bin/env python3
"""Export verified mechanism/network stems with their shared gains intact."""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    folder = ROOT / 'out/mechanism-network'
    frozen_path = folder / 'frozen-manifest.json'
    frozen = json.loads(frozen_path.read_text())
    for relative, expected in frozen['source_sha256'].items():
        if sha(ROOT / relative) != expected:
            raise ValueError(f'Frozen mechanism input changed: {relative}')
    probe = ROOT / frozen['probe_commands'][0][0]
    if sha(probe) != frozen['binary_sha256']['probe']:
        raise ValueError('Frozen probe binary changed')
    destination = ROOT / 'Audio/mechanism-network'
    destination.mkdir(parents=True, exist_ok=True)
    entries = []
    for bundle, data in frozen['bundles'].items():
        report_path = folder / f'{bundle}.json'
        if sha(report_path) != data['report_sha256']:
            raise ValueError(f'Frozen report changed: {bundle}')
        for filename, audio in data['audio'].items():
            selected = ('-intact-' in filename or '-coupling-off-combined.' in filename
                        or '-coupling-off-direct.' in filename or '-coupling-off-network.' in filename
                        or '-source-off-combined.' in filename or '-delta.' in filename)
            if not selected:
                continue
            source = folder / filename
            if sha(source) != audio['sha256']:
                raise ValueError(f'Frozen mechanism audio changed: {filename}')
            output = destination / source.with_suffix('.flac').name
            subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(source),
                            '-c:a', 'flac', '-sample_fmt', 's32',
                            '-bits_per_raw_sample', '24', str(output)], check=True)
            entries.append({'file': str(output.relative_to(ROOT / 'Audio')),
                            'sha256': sha(output), 'source_sha256': audio['sha256'],
                            'bundle': bundle, 'shared_export_gain': data['shared_gain'],
                            'rms_before_flac_quantization': audio['rms'],
                            'peak_before_flac_quantization': audio['peak']})
    manifest = {'schema_version': 1, 'producer_manifest_sha256': sha(frozen_path),
                'source_sha256': frozen['source_sha256'],
                'export_tool_sha256': sha(Path(__file__)),
                'format': '24-bit FLAC, 48 kHz stereo; no extra gain, EQ or room',
                'bundles': {'isolated': 'Mechanism triggers with all strings initially unstruck.',
                            'with-notes': 'Same mechanism events with a short piano note sequence.'},
                'levels': 'One existing gain per bundle is retained for every stem and ablation. Direct/string stems can be quiet. Effective levels are authored pressure proxies.',
                'limits': frozen['limits'], 'entries': entries}
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(destination)


if __name__ == '__main__':
    main()
