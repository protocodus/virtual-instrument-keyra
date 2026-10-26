#!/usr/bin/env python3
"""Check root-built full-model renderers against the immutable original.

Five short mixed-event cases compare float WAV/stem bytes and every deterministic
CLI metric. Separate identically compiled probes also compare canonical runtime
state, including double modal coordinates; they do not certify the root binaries'
internal state or Reason performance. No research or production source is edited.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import struct
import subprocess

from profile_reference import cpu_clock


ROOT = Path(__file__).resolve().parents[1]
TIMING_METRICS = {'wall_seconds', 'realtime_factor', 'process_cpu_seconds'}
FLAGS = ['-O3', '-DNDEBUG', '-std=c++17', '-ffp-contract=off']
SCALAR_FLAGS = ['-fno-builtin', '-fno-tree-vectorize']
EVENTS = [
    (0, 'pedal', 0, 1), (.01, 'on', 36, 40), (.025, 'on', 60, 93),
    (.04, 'on', 84, 127), (.075, 'off', 60, 0), (.09, 'on', 60, 61),
    (.12, 'pedal', 0, .55), (.15, 'off', 36, 0), (.18, 'off', 84, 0),
    (.21, 'pedal', 0, 0), (.24, 'on', 48, 80), (.28, 'off', 60, 0),
    (.3, 'off', 48, 0),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def strict_json(text: str):
    def reject(value):
        raise ValueError('Non-finite JSON value: ' + value)
    return json.loads(text, parse_constant=reject)


def deterministic(metrics: dict) -> dict:
    return {key: value for key, value in metrics.items() if key not in TIMING_METRICS}


def changed_metrics(left: dict, right: dict) -> list[str]:
    a, b = deterministic(left), deterministic(right)
    return sorted(key for key in a.keys() | b.keys() if key not in a or key not in b or a[key] != b[key])


def command_json(command: list[str], log_prefix: Path) -> dict:
    call = subprocess.run(command, text=True, capture_output=True, timeout=120)
    log_prefix.with_suffix('.stdout.json').write_text(call.stdout)
    log_prefix.with_suffix('.stderr.txt').write_text(call.stderr)
    if call.returncode:
        raise RuntimeError(f'Command exited {call.returncode}: {command!r}; see {log_prefix}.stderr.txt')
    result = strict_json(call.stdout)
    if not isinstance(result, dict):
        raise ValueError(f'Expected JSON object from {command[0]}')
    return result


def wav_info(path: Path, rate: int, duration: float) -> dict:
    data = path.read_bytes()
    frames = int(math.ceil(duration * rate))
    if len(data) != 44 + frames * 8:
        raise ValueError(f'Unexpected stereo WAV size: {path}')
    if (data[:4] != b'RIFF' or data[8:16] != b'WAVEfmt ' or data[36:40] != b'data'
            or struct.unpack_from('<HHI', data, 20) != (3, 2, rate)
            or struct.unpack_from('<H', data, 34)[0] != 32):
        raise ValueError(f'Expected float32 stereo WAV at {rate} Hz: {path}')
    return {'path': str(path), 'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}


def same_file(left: dict, right: dict) -> bool:
    # Read bytes too: equality is the criterion, hashes are report provenance.
    return Path(left['path']).read_bytes() == Path(right['path']).read_bytes()


def render(binary: Path, label: str, folder: Path, case: str, rate: int,
           arguments: list[str], duration: float, events: Path, state: bool) -> dict:
    prefix = folder / f'{case}-{label}'
    output = prefix.with_suffix('.wav')
    args = list(arguments)
    if case == '96k_stems':
        args += ['--stem-prefix', str(prefix)]
    metrics = command_json([str(binary), '--events', str(events), '--output', str(output),
                            '--sample-rate', str(rate), '--duration', str(duration), *args], prefix)
    if (metrics.get('nonfinite_samples') != 0 or metrics.get('sample_rate') != rate
            or metrics.get('duration_seconds') != float(f'{duration:.12g}') or metrics.get('string_count') != 230
            or metrics.get('board_modes') != 475 or metrics.get('string_modes', 0) <= 0):
        raise ValueError(f'Invalid full-model render metrics: {prefix}')
    files = {'audio': wav_info(output, rate, duration)}
    if case == '96k_stems':
        for stem in ('primary', 'secondary', 'transient'):
            files[stem] = wav_info(Path(str(prefix) + '-' + stem + '.wav'), rate, duration)
    if state:
        snapshot = Path(str(output) + '.state')
        if not snapshot.is_file() or not snapshot.stat().st_size:
            raise ValueError(f'Missing canonical runtime-state snapshot: {snapshot}')
        files['state'] = {'path': str(snapshot), 'bytes': snapshot.stat().st_size, 'sha256': sha(snapshot)}
    return {'metrics': metrics, 'files': files}


def compare_pair(rows: dict) -> dict:
    baseline, optimized = rows['baseline'], rows['optimized']
    changed = [name for name in baseline['files']
               if not same_file(baseline['files'][name], optimized['files'][name])]
    metrics = changed_metrics(baseline['metrics'], optimized['metrics'])
    return {'all_bytes_identical': not changed, 'changed_files': changed,
            'deterministic_metrics_identical': not metrics, 'changed_metrics': metrics,
            'variants': rows}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True, help='Root-built keyra_reference executable')
    parser.add_argument('--optimized', type=Path, required=True, help='Root-built keyra_full_reference executable')
    parser.add_argument('--duration', type=float, default=.35, help='Seconds per case, bounded to .1–2 (events scale with duration)')
    parser.add_argument('--sample-rate', type=int, default=48000)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'out/full-reference-parity')
    parser.add_argument('--report', type=Path, default=ROOT / 'Validation/full-reference-parity.json')
    parser.add_argument('--baseline-source', type=Path, default=ROOT / 'Research/GrandPianoV2/src/grand.cpp')
    parser.add_argument('--optimized-source', type=Path, default=ROOT / 'src/full_reference/grand.cpp')
    parser.add_argument('--compiler', default='g++', help='C++ compiler for separate runtime-state probes')
    parser.add_argument('--skip-state-probes', action='store_true', help='Run root-built CLI checks only; report state proof as skipped')
    parser.add_argument('--scalar-state-probes', action='store_true', help='Also run all state cases with GNU scalar/no-builtin flags')
    args = parser.parse_args()
    if not .1 <= args.duration <= 2 or not 48000 <= args.sample_rate <= 384000:
        parser.error('duration must be .1–2 seconds and sample rate must be 48000–384000')
    if args.skip_state_probes and args.scalar_state_probes:
        parser.error('--scalar-state-probes cannot be combined with --skip-state-probes')
    for key in ('baseline', 'optimized', 'baseline_source', 'optimized_source', 'output_dir', 'report'):
        setattr(args, key, getattr(args, key).resolve())
    return args


def check(args, result: dict):
    args.output_dir.mkdir(parents=True, exist_ok=True)
    events = args.output_dir / 'mixed.events'
    events.write_text(''.join(f'{time * args.duration / .35:.12f} {kind} {note} {value}\n'
                              for time, kind, note, value in EVENTS))
    result.update({'schema_version': 1, 'platform': platform.platform(), 'duration_seconds': args.duration,
                   'tool_sha256': sha(Path(__file__)), 'events_path': str(events), 'events_sha256': sha(events),
                   'ignored_timing_metrics': sorted(TIMING_METRICS), 'root_build': {}, 'state_probes': {},
                   'failures': [], 'limits': 'Finite mixed-event regression coverage, not perceptual realism or Reason-host certification. Root-built CLI output/metrics are tested directly. Double-state proof uses separately instrumented source copies, not the internal state of those root-built binaries. Scalar probes approximate GNU host restrictions; they are not Jukebox SDK builds.'})
    binaries = {'baseline': args.baseline, 'optimized': args.optimized}
    sources = {'baseline': args.baseline_source, 'optimized': args.optimized_source}
    result['root_build']['executables'] = {label: {'path': str(path), 'sha256': sha(path)}
                                          for label, path in binaries.items()}
    self_tests = {label: command_json([str(binary), '--self-test'], args.output_dir / f'self-test-{label}')
                  for label, binary in binaries.items()}
    result['root_build']['physical_self_tests'] = self_tests
    if any(row.get('passed') is not True for row in self_tests.values()) or self_tests['baseline'] != self_tests['optimized']:
        result['failures'].append({'configuration': 'root_build', 'case': 'physical_self_test'})
    cases = [('mixed', args.sample_rate, []), ('96k_stems', 96000, []),
             ('no_sympathetic', args.sample_rate, ['--no-sympathetic']),
             ('bridge_zero', args.sample_rate, ['--bridge', '0']),
             ('uncalibrated', args.sample_rate, ['--uncalibrated'])]
    result['root_build']['cases'] = {}
    for case, rate, arguments in cases:
        rows = {label: render(binary, label, args.output_dir, case, rate, arguments, args.duration, events, False)
                for label, binary in binaries.items()}
        pair = compare_pair(rows)
        result['root_build']['cases'][case] = pair
        if not pair['all_bytes_identical'] or not pair['deterministic_metrics_identical']:
            result['failures'].append({'configuration': 'root_build', 'case': case,
                                       'changed_files': pair['changed_files'], 'changed_metrics': pair['changed_metrics']})
    if args.skip_state_probes:
        result['state_probes']['status'] = 'explicitly_skipped'
    else:
        result['compiler'] = subprocess.check_output([args.compiler, '--version'], text=True, timeout=30).splitlines()[0]
        result['state_probe_transform_sha256'] = sha(ROOT / 'tools/profile_reference.py')
        configurations = [('native', FLAGS)]
        if args.scalar_state_probes:
            configurations.append(('scalar_no_builtin', FLAGS + SCALAR_FLAGS))
        for configuration, flags in configurations:
            folder = args.output_dir / configuration
            folder.mkdir(parents=True, exist_ok=True)
            probes, metadata = {}, {}
            for label, source in sources.items():
                compiled = folder / f'{label}.instrumented.cpp'
                compiled.write_text(cpu_clock(source.read_text()))
                binary = folder / label
                call = subprocess.run([args.compiler, *flags, '-I' + str(source.parent), str(compiled), '-o', str(binary)],
                                      text=True, capture_output=True, timeout=120)
                (folder / f'{label}.compile.stdout.txt').write_text(call.stdout)
                (folder / f'{label}.compile.stderr.txt').write_text(call.stderr)
                if call.returncode:
                    raise RuntimeError(f'{configuration}/{label} probe compilation failed; see {folder}/{label}.compile.stderr.txt')
                probes[label] = binary
                metadata[label] = {'source_path': str(source), 'source_sha256': sha(source),
                                   'calibration_sha256': sha(source.parent / 'calibration.h'),
                                   'instrumented_source_sha256': sha(compiled), 'binary_sha256': sha(binary)}
            probe_result = {'flags': flags, 'variants': metadata, 'cases': {}}
            result['state_probes'][configuration] = probe_result
            for case, rate, arguments in cases:
                rows = {label: render(binary, label, folder, case, rate, arguments, args.duration, events, True)
                        for label, binary in probes.items()}
                pair = compare_pair(rows)
                probe_result['cases'][case] = pair
                if not pair['all_bytes_identical'] or not pair['deterministic_metrics_identical']:
                    result['failures'].append({'configuration': configuration, 'case': case,
                                               'changed_files': pair['changed_files'], 'changed_metrics': pair['changed_metrics']})
                # Tie source probes to the actual root-built executable outputs.
                pair['root_build_output_identical'] = {}
                for label, row in rows.items():
                    root_row = result['root_build']['cases'][case]['variants'][label]
                    identical = all(same_file(info, row['files'][name]) for name, info in root_row['files'].items())
                    metrics_identical = not changed_metrics(root_row['metrics'], row['metrics'])
                    pair['root_build_output_identical'][label] = identical and metrics_identical
                    if not identical or not metrics_identical:
                        result['failures'].append({'configuration': configuration, 'case': case,
                                                   'variant': label, 'root_build_output_or_metrics_differ': True})
    result['passed'] = not result['failures']
    result['root_build_audio_and_metrics_identical'] = not any(row['configuration'] == 'root_build' for row in result['failures'])
    result['canonical_double_state_identical'] = None if args.skip_state_probes else all(
        'state' not in case['changed_files'] for configuration in result['state_probes'].values()
        for case in configuration['cases'].values())


def main():
    args = parse_args()
    result = {'passed': False}
    try:
        check(args, result)
    except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as error:
        result['passed'] = False
        result['error'] = str(error)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({key: result.get(key) for key in ('passed', 'root_build_audio_and_metrics_identical',
                     'canonical_double_state_identical', 'failures', 'error')} | {'report': str(args.report)}, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
