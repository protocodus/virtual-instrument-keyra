#!/usr/bin/env python3
"""Write the validation report that compares two benchmark_recordings.py runs.

Both runs must score the same cases. The report gives each run's means by role
and register, plus paired means using only cases measurable in both runs.
Availability changes are listed separately: a newly measurable sustain must
not be mistaken for a regression in a previously scored take. The legacy
independent-sample regression list remains in the output for traceability.

  python3 Tools/compare_benchmarks.py out/bench/baseline out/bench/candidate \\
      --name "shipping 0.3.0" "candidate 0.4.0" \\
      --out Docs/validation/recording-benchmark-split-2026-10-27
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics

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


def paired_comparison(base, cand, split):
    """Compare identical observations, exposing gained/lost metric coverage.

    Kawai n80v2 made sustain measurable after the censored-frame trial. Means
    over independently filtered layers then reported a +4.93 dB note change
    even though that take had no baseline sustain score. Keep missing values
    missing and compare each metric on its common case set. Both level errors
    use the baseline's full-case median gain, so recentering the candidate
    cannot hide a changed loudness response.
    """
    def indexed(report):
        rows = {r['case']: r for r in report['cases']}
        if len(rows) != len(report['cases']):
            raise ValueError('duplicate benchmark case')
        return rows

    b, c = indexed(base), indexed(cand)
    if b.keys() != c.keys():
        raise ValueError('the two runs scored different cases')
    if not b:
        raise ValueError('empty benchmark')
    for case in b:
        if b[case]['note'] != c[case]['note'] or case not in split:
            raise ValueError(f'case identity or split mismatch: {case}')
        if not all(math.isfinite(r['gain_db']) for r in (b[case], c[case])):
            raise ValueError(f'non-finite gain: {case}')
    pin = statistics.median(r['gain_db'] for r in b.values())

    def value(row, metric):
        v = abs(row['gain_db'] - pin) if metric == 'level_db' else row.get(metric)
        if v is not None and not math.isfinite(v):
            raise ValueError(f'non-finite {metric}: {row["case"]}')
        return v

    roles, notes, availability = {}, {}, []
    for case in sorted(b):
        role, note = split[case], b[case]['note']
        roles.setdefault(role, []).append(case)
        notes.setdefault((note, role), []).append(case)
        for metric in UNITS:
            bv, cv = value(b[case], metric), value(c[case], metric)
            if (bv is None) != (cv is None):
                availability.append({'case': case, 'note': note, 'role': role,
                                     'metric': metric, 'baseline': bv, 'candidate': cv,
                                     'change': 'gained' if bv is None else 'lost'})

    def summarise(cases):
        result = {'cases': len(cases)}
        for metric in UNITS:
            pairs = [(value(b[k], metric), value(c[k], metric)) for k in cases]
            shared = [(bv, cv) for bv, cv in pairs if bv is not None and cv is not None]
            bm = statistics.mean(v[0] for v in shared) if shared else None
            cm = statistics.mean(v[1] for v in shared) if shared else None
            result[metric] = {'paired_n': len(shared),
                              'baseline_only_n': sum(bv is not None and cv is None for bv, cv in pairs),
                              'candidate_only_n': sum(bv is None and cv is not None for bv, cv in pairs),
                              'neither_n': sum(bv is None and cv is None for bv, cv in pairs),
                              'baseline': bm, 'candidate': cm,
                              'delta': cm - bm if shared else None}
        return result

    by_note = [{'note': note, 'role': role, **summarise(cases)}
               for (note, role), cases in sorted(notes.items())]
    regressions = []
    for row in by_note:
        for metric, tolerance in TOLERANCE.items():
            s = row[metric]
            if s['delta'] is not None and s['delta'] > tolerance:
                regressions.append({'note': row['note'], 'role': row['role'], 'metric': metric,
                                    **{k: s[k] for k in ('paired_n', 'baseline', 'candidate', 'delta')}})
    regressions.sort(key=lambda r: -r['delta'] / TOLERANCE[r['metric']])
    return {'level_reference_db': pin, 'summary': {r: summarise(v) for r, v in sorted(roles.items())},
            'by_note': by_note, 'regressions': regressions, 'availability_changes': availability}


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
    if base['split'] != cand['split']:
        raise SystemExit('the two runs used different splits')
    paired = paired_comparison(base, cand, split)
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
            'scorer_sha256': sources, 'tolerance': TOLERANCE, 'regressions': regressions,
            'comparison_schema': 2, 'paired': paired,
            'comparator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'input_sha256': {name: hashlib.sha256((directory / 'report.json').read_bytes()).hexdigest()
                             for name, directory in [('baseline', a.baseline), ('candidate', a.candidate)]}}
    lines = [f'# Recording benchmark: {a.name[1]} against {a.name[0]}', '',
             f'Every train and dev note of `{cand["split"]}` scored by `Tools/benchmark_recordings.py` '
             '(metric definitions in its docstring; lower is better). Train recordings calibrated the '
             'candidate; dev recordings were never fitted. The first tables retain each run\'s '
             'independently filtered means; use the paired section for changes on the same observations.', '',
             f'## {a.name[0]}', ''] + table(base, keys) + ['', f'## {a.name[1]}', ''] + table(cand, keys) + [
             '', '## Independent-sample regressions (legacy)', '',
             f'Every note and role where {a.name[1]} is worse than {a.name[0]} by more than the tolerance '
             '(' + ', '.join(f'{k} {v:g}' for k, v in TOLERANCE.items()) + '), largest first.', '']
    if regressions:
        lines += ['| note | role | metric | ' + a.name[0] + ' | ' + a.name[1] + ' |', '|---|---|---|---|---|']
        lines += [f'| {r["note"]} | {r["role"]} | {r["metric"]} | {r["baseline"]:.2f} | {r["candidate"]:.2f} |'
                  for r in regressions]
    else:
        lines.append('None.')
    lines += ['', '## Paired changes', '',
              'Only observations measurable in both runs contribute to each metric. Both level errors '
              f'use the baseline full-case median gain ({paired["level_reference_db"]:.4f} dB). '
              'Lower errors are better; no metric tolerance changed.', '',
              '| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |',
              '|---|---|---:|---:|---:|---:|---:|---:|---:|']
    for role, summary in paired['summary'].items():
        for metric in keys:
            s = summary[metric]
            numbers = ' | '.join('-' if s[k] is None else f'{s[k]:.4f}'
                                 for k in ('baseline', 'candidate', 'delta'))
            lines.append(f'| {role} | {metric} | {s["paired_n"]} | {numbers} | '
                         f'{s["baseline_only_n"]} | {s["candidate_only_n"]} | {s["neither_n"]} |')
    lines += ['', '### Paired note regressions', '']
    if paired['regressions']:
        lines += ['| note | role | metric | paired n | baseline | candidate | change |',
                  '|---|---|---|---:|---:|---:|---:|']
        for r in paired['regressions']:
            lines.append(f'| {r["note"]} | {r["role"]} | {r["metric"]} | {r["paired_n"]} | '
                         f'{r["baseline"]:.4f} | {r["candidate"]:.4f} | {r["delta"]:.4f} |')
    else:
        lines.append('None.')
    lines += ['', '### Metric availability changes', '',
              'Gaining or losing a score is not an error delta. Every changed observation is listed; '
              'lost coverage is not silently treated as improvement.', '']
    if paired['availability_changes']:
        lines += ['| case | note | role | metric | change | baseline | candidate |',
                  '|---|---|---|---|---|---:|---:|']
        for r in paired['availability_changes']:
            values = ' | '.join('-' if r[k] is None else f'{r[k]:.4f}' for k in ('baseline', 'candidate'))
            lines.append(f'| {r["case"]} | {r["note"]} | {r["role"]} | {r["metric"]} | {r["change"]} | {values} |')
    else:
        lines.append('None.')
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.with_suffix('.json').write_text(json.dumps(data, indent=1) + '\n')
    a.out.with_suffix('.md').write_text('\n'.join(lines) + '\n')
    print(f'{len(paired["regressions"])} paired regressions; '
          f'{len(paired["availability_changes"])} availability changes; '
          f'{len(regressions)} legacy independent-sample regressions; report at {a.out}.md')


if __name__ == '__main__':
    main()
