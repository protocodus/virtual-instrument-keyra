#!/usr/bin/env python3
"""Write the validation report that compares two benchmark_recordings.py runs.

Both runs must score the same cases. The report gives each run's means by role
and register and lists every note and role where the candidate is worse than
the baseline by more than the metric's tolerance, largest first, so no
regression hides inside an average.

  python3 Tools/compare_benchmarks.py out/bench/baseline out/bench/candidate \\
      --name "shipping 0.3.0" "candidate 0.4.0" \\
      --out Docs/validation/recording-benchmark-split-2026-10-27
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
UNITS = {'partial_db': 'dB', 'tuning_cents': 'cents', 'decay_db_s': 'dB/s', 'attack_db': 'dB', 'early_db': 'dB',
         'sustain_db': 'dB', 'noise_db': 'dB', 'ild_db': 'dB', 'icc': '', 'envelope_db': 'dB', 'rise_ms': 'ms',
         'level_db': 'dB'}
# Differences smaller than these are not listed as regressions.
TOLERANCE = {'partial_db': .5, 'tuning_cents': .5, 'decay_db_s': 1.0, 'attack_db': .5, 'early_db': .5,
             'sustain_db': .5, 'noise_db': .5, 'ild_db': .5, 'icc': .02, 'envelope_db': .5, 'rise_ms': 1.0,
             'level_db': .5}


def table(report, keys):
    lines = ['| cases | ' + ' | '.join(keys) + ' |', '|---' * (len(keys) + 1) + '|']
    for name, s in list(report['summary'].items()) + list(report['by_register'].items()):
        lines.append(f'| {name} ({s["cases"]}) | ' + ' | '.join(
            f'{s[k]["mean"]:.2f}' if s.get(k) else '-' for k in keys) + ' |')
    return lines


def cell_means(report, split):
    cells = {}
    for row in report['cases']:
        cells.setdefault((row['note'], split[row['case']]), []).append(row)
    return {key: {k: float(np.mean([r[k] for r in rows if r.get(k) is not None]))
                  for k in UNITS if any(r.get(k) is not None for r in rows)}
            for key, rows in cells.items()}


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('baseline', type=Path)
    p.add_argument('candidate', type=Path)
    p.add_argument('--name', nargs=2, default=['baseline', 'candidate'])
    p.add_argument('--out', type=Path, required=True, help='report path without extension')
    a = p.parse_args()
    base = json.loads((a.baseline / 'report.json').read_text())
    cand = json.loads((a.candidate / 'report.json').read_text())
    if sorted(r['case'] for r in base['cases']) != sorted(r['case'] for r in cand['cases']):
        raise SystemExit('the two runs scored different cases')
    split_path = ROOT / cand['split']
    split = json.loads(split_path.read_text())['cases']
    keys = list(UNITS)
    b, c = cell_means(base, split), cell_means(cand, split)
    regressions = []
    for key in sorted(c):
        for k in keys:
            if k in b[key] and k in c[key] and c[key][k] - b[key][k] > TOLERANCE[k]:
                regressions.append({'note': key[0], 'role': key[1], 'metric': k,
                                    'baseline': b[key][k], 'candidate': c[key][k]})
    regressions.sort(key=lambda r: -(r['candidate'] - r['baseline']) / TOLERANCE[r['metric']])
    sources = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
               for name in ('Tools/benchmark_recordings.py', 'Tools/piano_analysis.py')}
    data = {'baseline': {'name': a.name[0], 'renderer': base['renderer'],
                         'summary': base['summary'], 'by_register': base['by_register']},
            'candidate': {'name': a.name[1], 'renderer': cand['renderer'],
                          'summary': cand['summary'], 'by_register': cand['by_register']},
            'split': cand['split'], 'split_sha256': hashlib.sha256(split_path.read_bytes()).hexdigest(),
            'scorer_sha256': sources, 'tolerance': TOLERANCE, 'regressions': regressions}
    lines = [f'# Recording benchmark: {a.name[1]} against {a.name[0]}', '',
             f'Every train and dev note of `{cand["split"]}` scored by `Tools/benchmark_recordings.py` '
             '(metric definitions in its docstring; lower is better). Train recordings calibrated the '
             'candidate; dev recordings were never fitted. Means per role and register.', '',
             f'## {a.name[0]}', ''] + table(base, keys) + ['', f'## {a.name[1]}', ''] + table(cand, keys) + [
             '', '## Regressions', '',
             f'Every note and role where {a.name[1]} is worse than {a.name[0]} by more than the tolerance '
             '(' + ', '.join(f'{k} {v:g}' for k, v in TOLERANCE.items()) + '), largest first.', '']
    if regressions:
        lines += ['| note | role | metric | ' + a.name[0] + ' | ' + a.name[1] + ' |', '|---|---|---|---|---|']
        lines += [f'| {r["note"]} | {r["role"]} | {r["metric"]} | {r["baseline"]:.2f} | {r["candidate"]:.2f} |'
                  for r in regressions]
    else:
        lines.append('None.')
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.with_suffix('.json').write_text(json.dumps(data, indent=1) + '\n')
    a.out.with_suffix('.md').write_text('\n'.join(lines) + '\n')
    print(f'{len(regressions)} regressions; report at {a.out}.md')


if __name__ == '__main__':
    main()
