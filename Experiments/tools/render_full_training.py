#!/usr/bin/env python3
"""Render only the locked full-model training set, with verifiable resume.

The source/profile controls are immutable inputs for a render batch. This tool
does not decode or fit evaluation recordings. Full-model CLI stems use the same
conventions as the preserved study, with no added noise, room or effects.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


def write(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--renderer', type=Path, required=True)
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--calibration', type=Path)
    parser.add_argument('--reference', type=Path, default=ROOT/'References/GrandFullRange/combined_train_features.json')
    parser.add_argument('--split', type=Path, default=ROOT/'References/GrandFullRange/split.json')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--ids', nargs='+')
    parser.add_argument('--rate', type=int, default=48000)
    parser.add_argument('--duration', type=float, default=4.35)
    parser.add_argument('--jobs', type=int, default=3)
    parser.add_argument('--stems', action='store_true')
    parser.add_argument('--resume', action='store_true')
    args = parser.parse_args()
    if not 1 <= args.jobs <= 4 or args.rate not in (48000, 96000, 192000) or not 3.8 <= args.duration <= 10:
        parser.error('Use 1–4 jobs, 48/96/192 kHz and 3.8–10 seconds')
    fitter = module('keyra_full_training_guard', ROOT/'tools/fit_full_calibration.py')
    rows, _ = fitter.training_inputs(args.reference, args.split)
    if args.ids:
        requested = set(args.ids)
        if requested - {row['id'] for row in rows}:
            parser.error('Every requested ID must belong to the locked training set')
        rows = [row for row in rows if row['id'] in requested]
    folder = args.output.resolve()
    if not (ROOT/'out').resolve() in folder.parents:
        parser.error('Render batches must be under this repository out/ directory')
    folder.mkdir(parents=True, exist_ok=True)
    args.renderer = args.renderer.resolve()
    args.source = args.source.resolve()
    calibration = (args.calibration or args.source.parent/'calibration.h').resolve()
    identities = {'source_sha256': sha(args.source), 'calibration_sha256': sha(calibration),
                  'engine_sha256': sha(args.renderer), 'reference_features_sha256': sha(args.reference),
                  'split_sha256': sha(args.split), 'training_guard_sha256': sha(ROOT/'tools/fit_full_calibration.py')}
    config = {**identities, 'ids': sorted(row['id'] for row in rows), 'rate': args.rate,
              'duration_seconds': args.duration, 'stems': args.stems,
              'event_policy': '0.100s note on; 4.150s note off; pedal0; SFZ-bin velocity proxy'}
    inputs = folder/'render-inputs.json'
    if inputs.exists():
        if not args.resume or json.loads(inputs.read_text()) != config:
            raise ValueError('Existing batch inputs differ or --resume was not supplied; use a new output folder')
    else:
        write(inputs, config)

    def render(row):
        name = row['id']
        score = folder/(name+'.events')
        score.write_text(f"# Held note; recording acquisition pedal state is undocumented.\n"
                         f"0.100000 on {row['midi']} {row['midi_velocity']}\n4.150000 off {row['midi']} 0\n")
        audio = folder/(name+'.wav')
        sidecar = folder/(name+'.json')
        command = [str(args.renderer), '--events', str(score), '--output', str(audio),
                   '--sample-rate', str(args.rate), '--duration', str(args.duration)]
        if args.stems:
            command += ['--stem-prefix', str(folder/name)]
        outputs = [audio] + ([folder/f'{name}-{part}.wav' for part in ('primary','secondary','transient')]
                             if args.stems else [])
        expected = {**identities, 'score_sha256': sha(score), 'command': command}
        if args.resume and sidecar.exists():
            previous = json.loads(sidecar.read_text())
            if previous.get('inputs') == expected and all(path.exists() and
                    previous.get('output_sha256', {}).get(path.name) == sha(path) for path in outputs):
                print(name+': verified cached render', flush=True)
                return previous
        call = subprocess.run(command, check=True, text=True, capture_output=True)
        metrics = json.loads(call.stdout)
        if metrics['nonfinite_samples'] or metrics['string_count'] != 230 or metrics['board_modes'] != 475:
            raise ValueError(f'Invalid full-model render: {name}')
        record = {'id': name, 'inputs': expected, 'metrics': metrics,
                  'output_sha256': {path.name: sha(path) for path in outputs}}
        write(sidecar, record)
        print(f"{name}: {metrics['wall_seconds']:.2f}s shared-host render", flush=True)
        return record

    results, errors = [], []
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(render, row): row['id'] for row in rows}
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as error:
                errors.append({'id': futures[future], 'error': str(error)})
    if identities != {**identities, 'source_sha256': sha(args.source), 'calibration_sha256': sha(calibration),
                      'engine_sha256': sha(args.renderer), 'reference_features_sha256': sha(args.reference),
                      'split_sha256': sha(args.split), 'training_guard_sha256': sha(ROOT/'tools/fit_full_calibration.py')}:
        raise ValueError('Inputs changed during synthesis')
    report = {**config, 'source_path': str(args.source), 'engine_path': str(args.renderer),
              'tool_sha256': sha(Path(__file__)), 'renders': sorted(results, key=lambda row: row['id']),
              'errors': errors, 'complete': not errors,
              'limits': 'TRAIN-only synthesis. Parallel shared-host wall time is not realtime callback evidence. No recording waveform enters the synthesizer.'}
    write(folder/'render-manifest.json', report)
    if errors:
        raise RuntimeError(errors)
    print(folder/'render-manifest.json')


if __name__ == '__main__':
    main()
