#!/usr/bin/env python3
"""Reproduce the ten mechanism-reference guard checks with synthetic audio only.

The corpus manifest, lock, inventory and source/license text are read as metadata.
No real recording is opened or decoded. All PCM24/FLAC audio is generated inside
a temporary directory under out/, which is removed even after a failed check.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import wave

import numpy as np

import analyze_mechanism_references as analysis
import fetch_mechanism_references as acquisition


PROJECT = Path(__file__).resolve().parents[1]
METADATA_ROOT = PROJECT / 'References/Mechanisms'
TEXT_METADATA = {
    'upstream/README.md',
    'upstream/LICENSE-CC-BY-3.0.txt',
    'upstream/Salamander-Grand-Piano-V3.sfz',
    'upstream/hammer.txt',
    'upstream/pedal.txt',
    'upstream/str_res.txt',
}


@contextmanager
def substitute(owner, attribute, value):
    """Restore module paths and shared SciPy functions even on assertion failure."""
    previous = getattr(owner, attribute)
    setattr(owner, attribute, value)
    try:
        yield
    finally:
        setattr(owner, attribute, previous)


def expect_runtime_error(operation, message_fragment):
    try:
        operation()
    except RuntimeError as error:
        if message_fragment not in str(error):
            raise AssertionError(f'Unexpected rejection: {error}') from error
    else:
        raise AssertionError(f'Missing rejection: {message_fragment}')


def write_pcm24(path, samples):
    values = np.clip(np.rint(samples * 2**23), -2**23, 2**23 - 1)
    integers = values.astype('<i4').reshape(-1)
    packed = integers.view(np.uint8).reshape(-1, 4)[:, :3].copy().tobytes()
    with wave.open(str(path), 'wb') as output:
        output.setnchannels(2)
        output.setsampwidth(3)
        output.setframerate(48000)
        output.writeframes(packed)


def encode_synthetic_flac(wav, flac):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(wav), str(flac)],
                   check=True)


def run_checks():
    input_paths = [Path(__file__), PROJECT / 'tools/analyze_mechanism_references.py',
                   PROJECT / 'tools/fetch_mechanism_references.py',
                   PROJECT / 'Research/GrandPianoV2/reference/fetch_reference.py']
    input_paths += [METADATA_ROOT / name for name in
                    ('manifest.json', 'split.json', 'split-lock.json',
                     'upstream-inventory.json')]
    # Verify the metadata allowlist before the acquisition guard reads its texts.
    manifest = json.loads((METADATA_ROOT / 'manifest.json').read_text())
    if set(manifest['upstream_text_files']) != TEXT_METADATA:
        raise RuntimeError('Unexpected source metadata path; no audio was opened')
    input_paths += [METADATA_ROOT / name for name in sorted(TEXT_METADATA)]
    inputs = {str(path.relative_to(PROJECT)): acquisition.sha(path)
              for path in input_paths}
    checks = {}

    random = np.random.default_rng(54321)
    for count in (17, 240, 1613, 12000):
        samples = random.normal(size=(count, 2))
        window = np.hanning(count + 1)[:-1]
        _, powers, _ = analysis.spectrum(samples, 48000)
        expected = np.sum((samples * window[:, None])**2) / (2 * np.sum(window**2))
        assert abs(float(np.sum(powers)) - float(expected)) < 1.e-12
    checks['stereo_power_parseval_even_odd_lengths'] = True

    time = np.arange(4800) / 48000
    tone = np.sin(2 * np.pi * 1000 * time)
    opposite = np.stack([tone, -tone], axis=1)
    _, powers, _ = analysis.spectrum(opposite, 48000)
    _, in_phase, _ = analysis.spectrum(np.stack([tone, tone], axis=1), 48000)
    assert np.array_equal(powers, in_phase)
    assert abs(analysis.stereo(opposite)['correlation'] + 1) < 1.e-15
    checks['opposite_channel_phase_preserves_power'] = True

    _, manifest = acquisition.locked_inputs()
    checks['current_locked_metadata_valid'] = True

    output_root = PROJECT / 'out'
    output_root.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='mechanism-guard-', dir=output_root) as folder:
        temporary = Path(folder)
        (temporary / 'recordings').mkdir()
        count = 1613
        time = np.arange(count) / 48000
        tone = .12 * np.exp(-30 * time) * np.sin(2 * np.pi * 1000 * time)
        wav = temporary / 'recordings/synthetic.wav'
        other = temporary / 'recordings/other.wav'
        flac = temporary / 'recordings/synthetic.flac'
        write_pcm24(wav, np.stack([tone, -tone], axis=1))
        write_pcm24(other, np.stack([tone * .4, tone * .4], axis=1))
        original_bytes = wav.read_bytes()
        encode_synthetic_flac(wav, flac)
        helper = acquisition.pcm_helper()
        row = {
            'id': 'key-release-A0', 'role': 'train', 'kind': 'key_release',
            'family': 'synthetic_fixture', 'midi': 21,
            'wav_path': 'recordings/synthetic.wav',
            'flac_path': 'recordings/synthetic.flac',
            'flac_bytes': flac.stat().st_size,
            'git_blob_sha1': acquisition.git_blob(flac),
            'flac_sha256': acquisition.sha(flac),
            'decoded_pcm': helper.decoded_pcm_identity(wav),
        }
        # Only satisfy the descriptor's bookkeeping argument. These synthetic
        # centers are not read from, or a check of, the piano's preset voicing.
        presets = {'presets': {'key_release': {
            'nominal_mode_frequencies_hz': [500., 1000., 1800.],
        }}}
        with substitute(analysis, 'ROOT', temporary):
            description = analysis.describe(row, helper, presets)
            windows = description['analysis_windows']
            assert len(windows) == 3 and windows[-1]['right_censored']
            assert sum(window['frames'] for window in windows) == count
            assert windows[-1]['actual_window_seconds'][1] == count / 48000
            checks['synthetic_short_window_censoring_without_padding'] = True

            expect_runtime_error(
                lambda: analysis.describe(dict(row, role='reserved_fresh_evaluation',
                                               id='key-release-C1'), helper, presets),
                'non-TRAIN')
            checks['reserved_describe_rejected_before_audio_access'] = True

            wrong = temporary / 'recordings/wrong.flac'
            encode_synthetic_flac(other, wrong)
            mismatched = dict(row, flac_path='recordings/wrong.flac',
                              flac_bytes=wrong.stat().st_size,
                              git_blob_sha1=acquisition.git_blob(wrong),
                              flac_sha256=acquisition.sha(wrong))
            expect_runtime_error(lambda: analysis.describe(mismatched, helper, presets),
                                 'authenticated source PCM')
            checks['valid_flac_with_wrong_source_pcm_rejected'] = True

            original_source_digest = analysis.source_pcm_digest

            def replace_after_preflight(path):
                digest = original_source_digest(path)
                wav.write_bytes(other.read_bytes())
                return digest

            try:
                with substitute(analysis, 'source_pcm_digest', replace_after_preflight):
                    expect_runtime_error(lambda: analysis.describe(row, helper, presets),
                                         'Loaded measurement array differs')
            finally:
                wav.write_bytes(original_bytes)
            checks['post_preflight_wav_replacement_now_rejected'] = True

            original_read = analysis.wavfile.read
            snapshot_reads = 0

            def replace_after_snapshot(source):
                nonlocal snapshot_reads
                if isinstance(source, io.BytesIO):
                    snapshot_reads += 1
                    wav.write_bytes(other.read_bytes())
                return original_read(source)

            try:
                with substitute(analysis.wavfile, 'read', replace_after_snapshot):
                    stable = analysis.describe(row, helper, presets)
            finally:
                wav.write_bytes(original_bytes)
            assert snapshot_reads == 1
            assert stable['early_stereo']['correlation'] < -.999
            assert stable['wav_sha256'] == hashlib.sha256(original_bytes).hexdigest()
            assert stable['decoded_pcm'] == row['decoded_pcm']
            checks['replacement_after_snapshot_cannot_change_measurement'] = True

            def replace_loaded_array(source):
                return original_read(other) if isinstance(source, io.BytesIO) else original_read(source)

            with substitute(analysis.wavfile, 'read', replace_loaded_array):
                expect_runtime_error(lambda: analysis.describe(row, helper, presets),
                                     'Loaded measurement array differs')
            checks['changed_loaded_array_now_rejected'] = True

        # This guard only needs metadata and an empty placeholder. No corpus
        # recording is copied to the temporary directory or opened here.
        for name in ('split.json', 'split-lock.json', 'manifest.json',
                     'upstream-inventory.json', *sorted(TEXT_METADATA)):
            target = temporary / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((METADATA_ROOT / name).read_bytes())
        reserved = next(item for item in manifest['samples']
                        if item['role'] == 'reserved_fresh_evaluation')
        (temporary / reserved['flac_path']).touch()
        with substitute(acquisition, 'ROOT', temporary):
            expect_runtime_error(acquisition.locked_inputs, 'unexpectedly present')
        checks['reserved_file_presence_guard_metadata_only'] = True

    if any(acquisition.sha(PROJECT / name) != digest for name, digest in inputs.items()):
        raise RuntimeError('Review inputs changed while checking')
    assert len(checks) == 10
    return {
        'schema_version': 1, 'passed': all(checks.values()), 'checks': checks,
        'input_sha256': inputs, 'source_tool': str(Path(__file__).relative_to(PROJECT)),
        'synthetic_sample_rate': 48000, 'synthetic_short_fixture_frames': 1613,
        'real_audio_opened': False, 'reserved_audio_opened': False,
        'corpus_metadata_only': True, 'temporary_audio_removed': True,
        'scope': 'Ten existing synthetic and metadata checks; no DSP or recording fit.',
        'formula_limits': 'Hann-weighted stereo power is not unweighted event energy. '
                          'Free-source bookkeeping does not assess the connected piano network.',
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=PROJECT / 'out/mechanism-reference-guard-check.json')
    arguments = parser.parse_args()
    output = arguments.output.resolve()
    if output.suffix != '.json' or not any(parent in output.parents
            for parent in (PROJECT / 'out', PROJECT / 'Validation')):
        parser.error('Write the JSON receipt under this project\'s out/ or Validation/')
    report = run_checks()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    print(json.dumps({'passed': report['passed'], 'checks': report['checks'],
                      'report': str(output)}, indent=2))


if __name__ == '__main__':
    main()
