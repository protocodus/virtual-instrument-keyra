#!/usr/bin/env python3
"""Export the frozen repetition probe, retaining its one shared gain."""
import hashlib
import json
from pathlib import Path
import struct
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decoded(path, format):
    return subprocess.run(
        ['ffmpeg', '-v', 'error', '-i', str(path), '-f', format, '-'],
        check=True, stdout=subprocess.PIPE).stdout


def main():
    folder = ROOT / 'out/strike-repetition/v3'
    frozen_path = folder / 'frozen-manifest.json'
    frozen = json.loads(frozen_path.read_text())
    receipt_path = folder / 'producer-receipt.json'
    if sha(receipt_path) != frozen['producer_receipt_sha256']:
        raise ValueError('Frozen probe producer receipt changed')
    for relative, expected in frozen['source_sha256'].items():
        if sha(ROOT / relative) != expected:
            raise ValueError(f'Frozen strike input changed: {relative}')
    document = frozen['documentation_at_render']
    if sha(ROOT / document['snapshot']) != document['sha256']:
        raise ValueError('Frozen producer-time documentation snapshot changed')
    updated_document = frozen['documentation_after_render']
    if sha(ROOT / updated_document['snapshot']) != updated_document['sha256']:
        raise ValueError('Frozen post-render documentation snapshot changed')
    for name, expected in frozen['binary_sha256'].items():
        if sha(folder / name) != expected:
            raise ValueError(f'Frozen producer/test binary changed: {name}')
    report_path = folder / 'repetitions.json'
    if sha(report_path) != frozen['report_sha256']:
        raise ValueError('Frozen repetition report changed')
    report = json.loads(report_path.read_text())
    expected_names = {'legacy-reset', 'recovery-control', 'varied-recovery',
                      'varied-with-mechanisms'}
    if {v['name'] for v in report['versions']} != expected_names:
        raise ValueError('Unexpected repetition comparison inventory')
    if report['sample_rate'] != 48000 or report['seconds'] != .6:
        raise ValueError('Unexpected frozen audio dimensions')
    for version in report['versions']:
        name = Path(version['audio']).name
        source = folder / name
        entry = frozen['audio'][name]
        if sha(source) != entry['sha256']:
            raise ValueError(f'Frozen repetition audio changed: {name}')
        if entry['same_shared_gain'] != report['shared_export_gain']:
            raise ValueError(f'Inconsistent shared gain: {name}')

    destination = ROOT / 'Audio/strike-repetition'
    destination.mkdir(parents=True, exist_ok=True)
    entries = []
    for version in report['versions']:
        source = folder / Path(version['audio']).name
        output = destination / source.with_suffix('.flac').name
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(source),
                        '-c:a', 'flac', '-sample_fmt', 's32',
                        '-bits_per_raw_sample', '24', str(output)], check=True)
        # FLAC must reproduce precisely the source's 24-bit PCM conversion.
        source_pcm24 = decoded(source, 's24le')
        output_pcm24 = decoded(output, 's24le')
        if output_pcm24 != source_pcm24:
            raise ValueError(f'FLAC PCM differs from source conversion: {output}')
        before = decoded(source, 'f32le')
        after = decoded(output, 'f32le')
        expected_bytes = 28800 * 2 * 4
        if len(before) != expected_bytes or len(after) != expected_bytes:
            raise ValueError(f'Unexpected frame/channel count: {output}')
        quantization_error = max(abs(a[0] - b[0]) for a, b in zip(
            struct.iter_unpack('<f', before), struct.iter_unpack('<f', after)))
        if quantization_error > 2 ** -23:
            raise ValueError(f'Unexpected level/conversion difference: {output}')
        entries.append({
            'name': version['name'],
            'file': str(output.relative_to(ROOT / 'Audio')),
            'sha256': sha(output), 'source_sha256': sha(source),
            'decoded_pcm24_sha256': hashlib.sha256(output_pcm24).hexdigest(),
            'source_to_flac_maximum_quantization_error': quantization_error,
            'requests': version['requests'], 'launches': version['launches'],
            'coalesced': version['coalesced'], 'cancelled': version['cancelled'],
            'legacy_active_resets': version['legacy_active_resets'],
            'launch_events': version['launch_events']})
    manifest = {
        'schema_version': 1,
        'probe_version': 3,
        'supersedes': 'Version 2 could leave short explicit release/repress requests unready. Version 3 schedules finite authored key lift while preserving hammer/string state. Previous source snapshots, producer binaries, reports, audio and hashes are preserved under out/strike-repetition/v1 and v2.',
        'producer_manifest_sha256': sha(frozen_path),
        'producer_receipt_sha256': frozen['producer_receipt_sha256'],
        'documentation_at_render': frozen['documentation_at_render'],
        'documentation_after_render': frozen['documentation_after_render'],
        'producer_report_sha256': sha(report_path),
        'source_sha256': frozen['source_sha256'],
        'producer_binary_sha256': frozen['binary_sha256']['probe'],
        'export_tool_sha256': sha(Path(__file__)),
        'format': '24-bit FLAC, 48 kHz stereo, 28800 frames per file',
        'conversion': 'Lossless FLAC of 24-bit PCM converted from frozen float WAV; no additional gain, EQ, fades or room.',
        'same_input_events': True,
        'key_midi': 60, 'requested_velocity': 80, 'seed': report['seed'],
        'shared_export_gain_already_in_source': report['shared_export_gain'],
        'events': report['events'],
        'event_legend': {'n': 'note-on, MIDI key 60', 'o': 'note-off, MIDI key 60',
                         'p': 'normalized sustain position'},
        'interpretation': 'Same requested events; state-dependent admitted launch times/counts can differ. Mechanism coupling affects the network and is not solely an observation-layer addition.',
        'limits': frozen['limits'], 'entries': entries}
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(destination)


if __name__ == '__main__':
    main()
