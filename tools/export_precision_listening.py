#!/usr/bin/env python3
"""Publish the measured full-model precision comparison as lossless audio."""
import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy.io import wavfile

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    folder = ROOT / 'out/full-precision-optimization'
    report_path = folder / 'hot-broadened-report.json'
    report = json.loads(report_path.read_text())
    destination = ROOT / 'Audio/precision-comparison'
    destination.mkdir(parents=True, exist_ok=True)
    entries, audio = [], {}
    for profile, label in [('baseline', 'double-control'),
                           ('hot_f32_biased', 'float-candidate')]:
        entry = report['full_listening_exports'][profile]
        source = Path(entry['file'])
        if sha(source) != entry['sha256']:
            raise ValueError(f'Listening source hash mismatch: {source}')
        rate, samples = wavfile.read(source)
        if rate != 48000 or samples.dtype != np.float32 or samples.shape[1] != 2:
            raise ValueError('Expected 48 kHz stereo float masters')
        if not np.isfinite(samples).all() or np.max(np.abs(samples)) >= 1:
            raise ValueError('Nonfinite or excessive audio level')
        output = destination / f'{label}.flac'
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(source),
                        '-c:a', 'flac', '-sample_fmt', 's32',
                        '-bits_per_raw_sample', '24', str(output)], check=True)
        audio[label] = samples
        entries.append({'file': str(output.relative_to(ROOT / 'Audio')),
                        'sha256': sha(output), 'profile': profile,
                        'source_sha256': sha(source),
                        'duration_seconds': len(samples) / rate})
    sequence = np.concatenate([audio['double-control'], np.zeros((24000, 2), np.float32),
                               audio['float-candidate']])
    temporary = folder / 'double-then-float.wav'
    wavfile.write(temporary, 48000, sequence)
    output = destination / 'double-then-float.flac'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(temporary),
                    '-c:a', 'flac', '-sample_fmt', 's32',
                    '-bits_per_raw_sample', '24', str(output)], check=True)
    entries.append({'file': str(output.relative_to(ROOT / 'Audio')), 'sha256': sha(output),
                    'order': ['full double control', 'full float candidate'],
                    'segment_start_seconds': [0, len(audio['double-control']) / 48000 + .5]})
    manifest = {'schema_version': 1, 'report_sha256': sha(report_path),
                'export_tool_sha256': sha(Path(__file__)),
                'source_sha256': report['source_sha256'],
                'candidate_source_sha256': report['candidate_source_sha256'],
                'format': '24-bit FLAC, 48 kHz stereo; no lossy codec',
                'processing': 'Existing whole-file RMS matching and common sample-peak gain retained; no further gain, EQ or room.',
                'within_file_segments': report['full_listening_exports']['baseline']['segments'],
                'within_file_start_seconds': report['full_listening_exports']['baseline']['segment_starts_seconds'],
                'limits': 'Labeled short excerpts. Audibility, long-tail behavior and Reason realtime performance are unproven. Candidate adds measured numerical loss.',
                'entries': entries}
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(destination)


if __name__ == '__main__':
    main()
