#!/usr/bin/env python3
"""Export a labeled physical-kernel audition against the frozen quality target.

No fitting or automatic quality decision. Render input with keyra_physical_render
first; this script reuses the original passage and its original procedural room.
"""
import argparse
import json
import subprocess

import numpy as np
from scipy.io import wavfile

from compare_quality_baseline import ROOT, load, r, sha, verify_reference_receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render-candidate', action='store_true',
                        help='Render the frozen candidate and capture input/output provenance')
    args = parser.parse_args()
    folder = ROOT / 'out/physical-candidate'
    folder.mkdir(parents=True, exist_ok=True)
    destination = ROOT / 'Audio/physical-candidate'
    destination.mkdir(parents=True, exist_ok=True)
    baseline = ROOT / 'out/quality-baseline'
    original_path = baseline / 'original-192k.wav'
    candidate_path = folder / 'passage-48k.wav'
    reduced_path = baseline / 'reduced-48k.wav'
    sources = ['tools/render_physical.cpp', 'src/PhysicalPiano.cpp',
               'include/keyra/PhysicalPiano.h', 'include/keyra/physics/ModalBank.h',
               'include/keyra/physics/Bridge.h', 'include/keyra/physics/Action.h',
               'include/keyra/physics/Materials.h', 'include/keyra/AnchorLookup.h',
               'src/physics/Action.cpp', 'src/LiveCalibration.h']
    inputs = sources + ['build/keyra_physical_render', 'out/quality-baseline/passage.events']
    receipt_path = ROOT / 'Validation/physical-candidate-freeze.json'
    if args.render_candidate:
        before = {path: sha(ROOT / path) for path in inputs}
        command = [str(ROOT / 'build/keyra_physical_render'), '--events',
                   str(baseline / 'passage.events'), '--output', str(candidate_path),
                   '--rate', '48000', '--seconds', '9', '--resonance', '0.5',
                   '--report', str(folder / 'passage-48k.json'),
                   '--stem-prefix', str(folder / 'passage')]
        subprocess.run(command, check=True)
        if before != {path: sha(ROOT / path) for path in inputs}:
            raise ValueError('Physical inputs changed during synthesis')
        outputs = [candidate_path, folder / 'passage-48k.json'] + [
            folder / f'passage-{name}.wav' for name in ('primary', 'secondary', 'board')]
        receipt = {'schema_version': 1, 'command': command,
                   'receipt_method': 'Inputs hashed before/after successful renderer execution.',
                   'sha256': {**before, **{str(path.relative_to(ROOT)): sha(path)
                                           for path in outputs}}}
        receipt_path.write_text(json.dumps(receipt, indent=2) + '\n')
    receipt = json.loads(receipt_path.read_text())
    for path, expected in receipt['sha256'].items():
        if sha(ROOT / path) != expected:
            raise ValueError(f'Physical synthesis receipt mismatch: {path}')
    reference_receipt = verify_reference_receipt()
    reduced_receipt = json.loads((ROOT / 'Validation/quality-baseline-comparison.json').read_text())
    if sha(reduced_path) != reduced_receipt['reduced_raw_sha256']:
        raise ValueError('Reduced renderer comparison is stale')
    original = r.downsample(original_path)
    candidate_rate, candidate = load(candidate_path)
    reduced_rate, reduced = load(reduced_path)
    if candidate_rate != 48000 or reduced_rate != 48000:
        raise ValueError('Expected 48 kHz candidate and live preview')
    if original.shape != candidate.shape or original.shape != reduced.shape:
        raise ValueError('Expected the same nine-second event passage')

    stems = [load(folder / f'passage-{name}.wav')[1]
             for name in ('primary', 'secondary', 'board')]
    stem_error = float(np.max(np.abs(sum(stems) - candidate)))
    if stem_error > 3e-6 * np.sqrt(np.mean(candidate * candidate)):
        raise ValueError('Physical stems do not reconstruct the same simulation')

    versions, trims = {}, {}
    impulse = r.room_ir()
    for name, data in [('original', original), ('physical', candidate), ('reduced', reduced)]:
        for kind, y in [('dry', data), ('room', r.presentation(data, impulse, .16))]:
            gain = .08 / max(float(np.sqrt(np.mean(y * y))), 1e-20)
            y = y.copy() * gain
            y[-7200:] *= np.linspace(1, 0, 7200)[:, None]
            versions[(name, kind)] = y
            trims[f'{name}-{kind}'] = gain
    common = 10 ** (-2 / 20) / max(r.true_peak(y) for y in versions.values())
    entries, metrics = [], {}

    def export(name, data):
        temporary = folder / f'{name}-export.wav'
        path = destination / f'{name}.mp3'
        wavfile.write(temporary, 48000, data.astype(np.float32))
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(temporary),
                        '-c:a', 'libmp3lame', '-b:a', '320k', str(path)], check=True)
        return {'file': str(path.relative_to(ROOT / 'Audio')), 'sha256': sha(path),
                'duration_seconds': len(data) / 48000}

    for (name, kind), data in versions.items():
        data *= common
        entry = export(f'{name}-{kind}', data)
        entry.update(engine=name, presentation=kind,
                     whole_file_rms_gain_before_fade=trims[f'{name}-{kind}'],
                     common_true_peak_gain=common)
        entries.append(entry)
        powers = np.mean(data * data, axis=0)
        metrics[f'{name}-{kind}'] = {
            'rms': float(np.sqrt(np.mean(data * data))),
            'left_right_correlation': float(np.mean(data[:, 0] * data[:, 1]) /
                                            max(np.sqrt(powers[0] * powers[1]), 1e-30)),
            'right_minus_left_power_db': float(10 * np.log10(max(powers[1], 1e-30) /
                                                            max(powers[0], 1e-30)))}
    gap = np.zeros((24000, 2))
    sequence = np.concatenate([versions[('original', 'dry')], gap,
                               versions[('physical', 'dry')], gap,
                               versions[('reduced', 'dry')]])
    entry = export('original-physical-reduced-dry', sequence)
    entry.update(order=['preserved full physical original', 'experimental physical candidate',
                        'reduced live preview'], segment_start_seconds=[0, 9.5, 19])
    entries.append(entry)
    sources += ['tools/compare_physical_candidate.py', 'tools/compare_quality_baseline.py']
    report = {
        'schema_version': 1,
        'purpose': 'Audition restored nonlinear excitation, two mechanical polarizations and '
                   'full reference board; no quality or real-time promotion.',
        'events_sha256': sha(baseline / 'passage.events'),
        'physical_synthesis_receipt': receipt,
        'reference_synthesis_receipt': reference_receipt,
        'reduced_parameters': reduced_receipt['reduced_parameters'],
        'source_hashes': {path: sha(ROOT / path) for path in sources},
        'binary_sha256': sha(ROOT / 'build/keyra_physical_render'),
        'raw_hashes': {'original': sha(original_path), 'physical': sha(candidate_path),
                       'reduced': sha(reduced_path)},
        'physical_render': json.loads((folder / 'passage-48k.json').read_text()),
        'physical_stem_maximum_absolute_reconstruction_error': stem_error,
        'physical_stem_rms': {name: float(np.sqrt(np.mean(data * data)))
                              for name, data in zip(('primary', 'secondary', 'board'), stems)},
        'gain_policy': 'Each complete engine/presentation matches .08 stereo RMS before '
                       'the same 150 ms end fade; one common true-peak gain for all six.',
        'room': 'Identical preserved room_ir and presentation(), wet=.16; dry has no added room.',
        'limits': ['Original synthesis 192 kHz, candidate/live 48 kHz; exports all 48 kHz.',
                   'Original/candidate native output high-pass 24 Hz, live DC reject 7 Hz.',
                   'Candidate is an aggregate choir reduction, with empirical loss/observation '
                   'priors and authored hammer; it does not restore all original string modes.',
                   'Timing includes shared-host contention; not a Rack/real-time qualification.',
                   'No recordings fitted here; no listener preference or parity inferred.'],
        'metrics': metrics, 'entries': entries}
    text = json.dumps(report, indent=2) + '\n'
    (destination / 'manifest.json').write_text(text)
    (ROOT / 'Validation/physical-candidate-comparison.json').write_text(text)
    print(destination)


if __name__ == '__main__':
    main()
