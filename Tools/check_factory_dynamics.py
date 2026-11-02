"""Check a KeyraLevels factory CSV against the measured 0.4.10 exceptions.

Every (piano, microphone, chord, round, velocity interval) is independent.
An improvement cannot offset a regression elsewhere. For a nominally positive
row the floor is zero. For an existing negative row it is the measured step.
Both allow 0.001 dB of cross-build/reporting variation. This numerical allowance
is not an audibility threshold or the stricter gate for a new DSP experiment.

--csv checks an existing audit without rendering. --renderer runs one fresh
factory audit, saves its actual CSV under --output, then checks that same file.
"""
import argparse
import csv
import json
import math
from pathlib import Path
import subprocess
import sys
import tempfile


REFERENCE = Path(__file__).resolve().parents[1] / 'Tests/Fixtures/dynamics/factory-0.4.10.json'
TOLERANCE_DB = 0.001
COLUMNS = ('panel', 'drive', 'output_gain', 'piano', 'mic', 'round', 'shape', 'midi_notes',
           'velocity_low', 'velocity_high', 'vu_low', 'vu_high', 'step_db')


def reference_rows():
    ref = json.loads(REFERENCE.read_text(encoding='utf-8'))
    if ref['version'] != 1 or ref['sample_rate_hz'] != 48000 or ref['output_gain'] != .7:
        raise ValueError('unsupported factory dynamics reference')
    if (ref['exception_fields'] != ['mic', 'round', 'shape', 'velocity_low', 'step_db']
            or len(ref['pianos']) != 6 or len(set(ref['pianos'])) != 6):
        raise ValueError('invalid factory dynamics reference dimensions')
    expected = {}
    for panel, spec in ref['panels'].items():
        for piano in ref['pianos']:
            for mic in range(2):
                for rnd in range(1, spec['rounds'] + 1):
                    for shape, notes in enumerate(spec['chords']):
                        for low, high in zip(spec['velocities'], spec['velocities'][1:]):
                            key = (panel, piano, mic, rnd, shape, low)
                            expected[key] = (high, ' '.join(map(str, notes)))
    exceptions = {}
    for panel, pianos in ref['negative_steps'].items():
        for piano, rows in pianos.items():
            for mic, rnd, shape, low, step in rows:
                key = (panel, piano, mic, rnd, shape, low)
                if key not in expected or key in exceptions or not math.isfinite(step) or step >= 0:
                    raise ValueError(f'invalid baseline exception {key}: {step}')
                exceptions[key] = step
    return expected, exceptions


def check(stream):
    expected, exceptions = reference_rows()
    reader = csv.DictReader(stream, strict=True)
    if tuple(reader.fieldnames or ()) != COLUMNS:
        raise ValueError('invalid factory audit CSV header')
    seen = set()
    regressions = []
    for r in reader:
        if None in r or None in r.values():
            raise ValueError(f'incomplete or extra CSV fields at line {reader.line_num}')
        key = (r['panel'], r['piano'], int(r['mic']), int(r['round']), int(r['shape']), int(r['velocity_low']))
        if key not in expected or (int(r['velocity_high']), r['midi_notes']) != expected[key]:
            raise ValueError(f'unexpected audit support at {key}, notes {r["midi_notes"]}, high {r["velocity_high"]}')
        if key in seen:
            raise ValueError(f'duplicate audit row {key}')
        seen.add(key)
        gain, low, high, step = (float(r[field]) for field in ('output_gain', 'vu_low', 'vu_high', 'step_db'))
        if not all(map(math.isfinite, (gain, low, high, step))):
            raise ValueError(f'nonfinite audit value at {key}')
        if r['drive'] != 'factory' or gain != .7:
            raise ValueError(f'incorrect drive or output gain at {key}: {r["drive"]}, {gain}')
        # KeyraLevels clamps mean square to 1e-30 before its +12 dB VU offset.
        if min(low, high) <= -288:
            raise ValueError(f'silent meter reading at {key}')
        # The three columns are independently printed to nine decimals.
        if abs(high - low - step) > 1.6e-9:
            raise ValueError(f'inconsistent paired readings at {key}: {low}, {high}, {step}')
        baseline = exceptions.get(key, 0.)
        if step < baseline - TOLERANCE_DB:
            regressions.append(f'{key}: {step:+.6f} dB, baseline floor {baseline:+.6f} dB')
    missing = expected.keys() - seen
    if missing:
        raise ValueError(f'{len(missing)} missing audit rows, first {min(missing)}')
    if regressions:
        raise ValueError(f'{len(regressions)} factory dynamics regressions:\n' + '\n'.join(regressions))
    return len(seen)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--csv', type=Path)
    source.add_argument('--renderer', type=Path)
    parser.add_argument('--output', type=Path, help='CSV to retain from a fresh render')
    parser.add_argument('--jobs', type=int, default=4)
    args = parser.parse_args()
    if bool(args.renderer) != bool(args.output) or args.jobs < 1:
        parser.error('--renderer and --output must be used together, and --jobs must be positive')
    path = args.csv or args.output
    if args.renderer and path.resolve() in (args.renderer.resolve(), REFERENCE.resolve()):
        parser.error('--output must be separate from the renderer and reference fixture')
    try:
        if args.renderer:
            # Leave the previous complete capture intact if the renderer fails.
            with tempfile.TemporaryDirectory(dir=path.parent) as temporary:
                capture = Path(temporary) / 'factory.csv'
                with capture.open('w', encoding='utf-8', newline='') as out:
                    subprocess.run([str(args.renderer.resolve()), '--audit-dynamics', '--jobs', str(args.jobs)],
                                   stdout=out, check=True)
                capture.replace(path)
        with path.open(encoding='utf-8', newline='') as stream:
            count = check(stream)
    except (OSError, csv.Error, ValueError, subprocess.CalledProcessError) as error:
        print(f'Factory dynamics check failed: {error}', file=sys.stderr)
        return 1
    print(f'Factory dynamics passed on {count} paired rows against 0.4.10 (tolerance {TOLERANCE_DB} dB).')
    return 0


if __name__ == '__main__':
    sys.exit(main())
