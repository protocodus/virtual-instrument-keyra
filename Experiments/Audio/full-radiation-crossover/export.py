#!/usr/bin/env python3
"""Reproduce one frozen compatibility presentation from authenticated raw WAVs.

This runs the archived observation crossover and presentation, not piano DSP.
"""
from pathlib import Path
import argparse
import hashlib
import importlib.util
import io
import json
import os
import subprocess
import sys

# Set before NumPy/SciPy import: the historical procedural IR uses BLAS norms.
os.environ['OPENBLAS_NUM_THREADS'] = '1'
sys.dont_write_bytecode = True
import numpy as np
import scipy
from scipy.io import wavfile

PACKAGE = Path(__file__).resolve().parent
sha = lambda data: hashlib.sha256(data).hexdigest()


def module(name, path, digest):
    if sha(path.read_bytes()) != digest:
        raise ValueError('Source fingerprint mismatch: ' + str(path))
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


def pcm24(path):
    return subprocess.check_output(['ffmpeg', '-v', 'error', '-i', str(path),
                                    '-f', 's24le', '-acodec', 'pcm_s24le', '-'])


def decoded24(data):
    b = np.frombuffer(data, dtype=np.uint8).reshape(-1, 3).astype(np.int32)
    q = b[:, 0]+(b[:, 1] << 8)+(b[:, 2] << 16)
    return (((q ^ 0x800000)-0x800000).reshape(-1, 2).astype(np.float64))/2**23


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs', type=Path, required=True,
                        help='JSON object mapping the two manifest source IDs to raw WAV paths')
    parser.add_argument('--output', type=Path, required=True,
                        help='New or empty output directory; files are never overwritten')
    parser.add_argument('--repository-root', type=Path, default=PACKAGE.parents[1])
    args = parser.parse_args()
    manifest = json.loads((PACKAGE/'manifest.json').read_text())
    expected_exporter = next(x['sha256'] for x in manifest['package_files'] if x['file'] == 'export.py')
    if sha(Path(__file__).read_bytes()) != expected_exporter:
        raise ValueError('Exporter fingerprint mismatch')
    if args.output.exists() and any(args.output.iterdir()):
        raise ValueError('Output directory must be empty')
    args.output.mkdir(parents=True, exist_ok=True)
    source_paths = json.loads(args.inputs.read_text())
    audio = {}
    for row in manifest['raw_sources']:
        path = Path(source_paths[row['id']])
        data = path.read_bytes()
        if sha(data) != row['sha256']:
            raise ValueError('Raw source fingerprint mismatch: ' + row['id'])
        rate, value = wavfile.read(io.BytesIO(data))
        if rate != 48000 or value.dtype != np.float32 or value.shape != (432000, 2) or not np.isfinite(value).all():
            raise ValueError('Invalid raw source format: ' + row['id'])
        if sha(value.astype('<f4').tobytes()) != row['float32_payload_sha256']:
            raise ValueError('Raw source sample fingerprint mismatch: ' + row['id'])
        audio[row['id']] = value
    crossover_source = manifest['crossover']['source']
    crossover = module('frozen_400hz_presentation_crossover',
        args.repository_root/crossover_source['file'], crossover_source['sha256'])
    recipe = manifest['music_recipe']
    if crossover.RATE != 48000 or crossover.CUTOFF != 400.0 or list(crossover.coefficients()) != manifest['crossover']['coefficients_a_b']:
        raise ValueError('Frozen coefficient mismatch')
    compatibility, state = crossover.process(audio['music-old-raw'], audio['music-causal-raw'], [64])
    compatibility32 = compatibility.astype('<f4')
    if sha(compatibility32.tobytes()) != manifest['compatibility_raw_float32_payload_sha256']:
        raise ValueError('Compatibility sample fingerprint mismatch')
    if state.tolist() != manifest['compatibility_final_LP_state']:
        raise ValueError('Compatibility final filter state mismatch')
    presentation_source = manifest['presentation_code']
    presentation = module('historical_fixed_room_presentation',
        args.repository_root/presentation_source['file'], presentation_source['sha256'])
    impulse = presentation.room_ir()
    if sha(impulse.astype('<f8').tobytes()) != recipe['procedural_ir_float64_sha256']:
        raise ValueError('Historical procedural IR mismatch; use the documented numerical environment')
    versions = []
    for source in (audio['music-old-raw'], compatibility32):
        x = presentation.presentation(source.astype(np.float64), impulse, recipe['room_wet']).copy()
        x *= recipe['rms_gain_before_fade']
        x[-recipe['fade_frames']:] *= np.linspace(1, 0, recipe['fade_frames'])[:, None]
        x *= recipe['original_common_true_peak_gain']
        x *= recipe['fixed_prior_shared_extra_safety_gain']
        if not np.isfinite(x).all() or np.max(abs(x)) >= 1 or presentation.true_peak(x) > 10**(-2/20)+3.e-7:
            raise ValueError('Fixed recipe unsafe; do not change gains or normalize')
        versions.append(x)
    joined = np.concatenate([versions[0], np.zeros((24000, 2)), versions[1]])
    wav = args.output/'old-then-compatibility-room.wav'
    flac = args.output/'old-then-compatibility-room.flac'
    wavfile.write(wav, 48000, joined.astype(np.float32))
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(wav), '-c:a', 'flac',
                    '-sample_fmt', 's32', '-bits_per_raw_sample', '24', str(flac)], check=True)
    data = pcm24(flac)
    if data != pcm24(wav) or sha(data) != manifest['audio']['pcm24_sha256']:
        raise ValueError('Presentation PCM24 reproduction mismatch')
    if sha(data[:432000*6]) != manifest['audio']['old_segment_pcm24_sha256'] or data[432000*6:456000*6] != bytes(24000*6):
        raise ValueError('Old-segment identity or silent-gap mismatch')
    q = decoded24(data)
    if not np.isfinite(q).all() or len(q) != 888000 or presentation.true_peak(q) > 10**(-2/20)+3.e-7:
        raise ValueError('Emitted PCM24 safety or duration check failed')
    checks = {'scope': 'Exact fixed presentation reproduction only; no piano DSP render or metric rescore.',
        'passed': True, 'PCM24_exact': True, 'old_segment_PCM24_exact': True,
        'gap_exact_zero': True, 'finite': True, 'frames': len(q), 'sample_rate': 48000,
        'channels': 2, 'bits': 24, 'true_peak_4x': float(presentation.true_peak(q)),
        'flac_sha256': sha(flac.read_bytes()), 'pcm24_sha256': sha(data),
        'OPENBLAS_NUM_THREADS': os.environ['OPENBLAS_NUM_THREADS'],
        'numpy': np.__version__, 'scipy': scipy.__version__}
    (args.output/'checks.json').write_text(json.dumps(checks, indent=2)+'\n')
    print(json.dumps(checks, indent=2))


if __name__ == '__main__':
    main()
