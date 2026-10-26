#!/usr/bin/env python3
"""Report frozen baseline/candidate metrics without redefining or refitting them.

Requires Matplotlib only for the two PNG figures. Inputs must contain the same
complete case set and identical analysis settings. Every regression is retained.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SPLITS = ['train', 'heldout_velocity', 'heldout_pitch', 'edge_extrapolation']
LABELS = {'train': 'Training', 'heldout_velocity': 'Held-out velocity',
          'heldout_pitch': 'Held-out pitch', 'edge_extrapolation': 'Keyboard edges'}
METRICS = [
    ('log_band_mae_db', 'Log-frequency band error', 'dB'),
    ('harmonic_level_mae_db', 'Partial-level error', 'dB'),
    ('envelope_mae_db', 'Amplitude-envelope error', 'dB'),
    ('partial_decay_slope_mae_db_per_second', 'Partial decay-rate error', 'dB/s'),
    ('absolute_f1_error_cents', 'Fundamental tuning error', 'cents'),
    ('attack_rise10_90_error_ms', 'Attack-rise error', 'ms'),
]
# The auxiliary tuning metric remains in the complete tables even though the
# compact overview plot shows six main quantities.
ALL_METRICS = METRICS + [('partial_tuning_mae_cents', 'Partial tuning error', 'cents')]


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def compare_reports(baseline_path, candidate_path):
    baseline = json.loads(Path(baseline_path).read_text())
    candidate = json.loads(Path(candidate_path).read_text())
    if baseline['analysis'] != candidate['analysis']:
        raise ValueError('Analysis definitions differ; regenerate both with the same frozen benchmark')
    old = {r['id']: r for r in baseline['cases']}
    new = {r['id']: r for r in candidate['cases']}
    if set(old) != set(new):
        raise ValueError(f'Case-set mismatch: baseline-only={sorted(set(old)-set(new))}; candidate-only={sorted(set(new)-set(old))}')
    if len(old) != 24:
        raise ValueError(f'This locked benchmark expects all 24 cases, found {len(old)}')
    cases, regressions, unpaired = [], [], []
    for id_ in sorted(old, key=lambda s: (SPLITS.index(old[s]['split']), old[s]['midi'], old[s]['layer'])):
        a, b = old[id_], new[id_]
        if a['split'] != b['split'] or a['reference_sha256'] != b['reference_sha256']:
            raise ValueError(f'Reference or split changed for {id_}')
        row = {'id': id_, 'split': a['split'], 'midi': a['midi'], 'layer': a['layer'], 'metrics': {}}
        for key, label, units in ALL_METRICS:
            before, after = a.get(key), b.get(key)
            if before is None or after is None:
                row['metrics'][key] = {'baseline': before, 'candidate': after, 'change': None, 'status': 'not_comparable'}
                unpaired.append({'id': id_, 'split': a['split'], 'metric': key, 'baseline': before, 'candidate': after})
                continue
            delta = float(after-before)
            state = 'regressed' if delta > 1e-9 else 'improved' if delta < -1e-9 else 'tied'
            row['metrics'][key] = {'baseline': before, 'candidate': after, 'change': delta,
                                    'error_reduction_percent': 100*(before-after)/before if before > 1e-12 else None,
                                    'status': state}
            if state == 'regressed':
                regressions.append({'id': id_, 'split': a['split'], 'metric': key, 'label': label,
                                    'units': units, 'baseline': before, 'candidate': after, 'increase': delta})
        cases.append(row)
    summary = {}
    for split in SPLITS:
        selected = [c for c in cases if c['split'] == split]
        group = {'cases': len(selected), 'metrics': {}}
        for key, label, units in ALL_METRICS:
            pairs = [c['metrics'][key] for c in selected if c['metrics'][key]['change'] is not None]
            before = float(np.mean([p['baseline'] for p in pairs])) if pairs else None
            after = float(np.mean([p['candidate'] for p in pairs])) if pairs else None
            group['metrics'][key] = {'label': label, 'units': units, 'baseline_mean': before,
                'candidate_mean': after, 'change': after-before if pairs else None,
                'error_reduction_percent': 100*(before-after)/before if pairs and before > 1e-12 else None,
                'improved_cases': sum(p['status'] == 'improved' for p in pairs),
                'regressed_cases': sum(p['status'] == 'regressed' for p in pairs),
                'tied_cases': sum(p['status'] == 'tied' for p in pairs), 'valid_cases': len(pairs)}
        summary[split] = group
    return {'schema_version': 1, 'baseline_report_sha256': file_hash(baseline_path),
            'candidate_report_sha256': file_hash(candidate_path),
            'benchmark_implementation_sha256': file_hash(ROOT/'tools/benchmark.py'),
            'metric_definitions_unchanged': True, 'analysis': baseline['analysis'],
            'summary': summary, 'cases': cases, 'regressions': regressions,
            'not_comparable': unpaired,
            'interpretation': 'Errors measure agreement with one acoustic piano recording set; percentages are error reductions, not percentages of realism.'}


def plots(report, destination):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                         'axes.spines.top': False, 'axes.spines.right': False,
                         'axes.labelcolor': '#303642', 'text.color': '#202733',
                         'xtick.color': '#394250', 'ytick.color': '#394250',
                         'savefig.facecolor': '#fbfcfe', 'figure.facecolor': '#fbfcfe'})
    fig, axes = plt.subplots(2, 3, figsize=(12.8, 8.2))
    x = np.arange(len(SPLITS))
    short_labels = ['Train\n(n=10)', 'Velocity\n(n=8)', 'Pitch\n(n=4)', 'Edges\n(n=2)']
    for ax, (key, title, units) in zip(axes.reshape(-1), METRICS):
        old = [report['summary'][s]['metrics'][key]['baseline_mean'] for s in SPLITS]
        new = [report['summary'][s]['metrics'][key]['candidate_mean'] for s in SPLITS]
        old_plot = [np.nan if v is None else v for v in old]
        new_plot = [np.nan if v is None else v for v in new]
        first = ax.bar(x-.19, old_plot, width=.36, color='#9ba7b5', label='Original POC')
        second = ax.bar(x+.19, new_plot, width=.36, color='#197b70', label='Calibrated model')
        ax.set_title(title, loc='left', fontweight='bold', pad=12)
        ax.set_ylabel(units)
        ax.set_xticks(x, short_labels)
        ax.set_axisbelow(True); ax.grid(axis='y', color='#e3e7ee', linewidth=.7)
        top = max([v for v in old+new if v is not None] or [1])
        ax.set_ylim(0, top*1.23+1e-8)
        for bars in (first, second):
            ax.bar_label(bars, labels=[f'{b.get_height():.1f}' for b in bars], fontsize=8, padding=3)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper right', frameon=False, ncol=2, bbox_to_anchor=(.985, .975))
    fig.suptitle('Acoustic-piano benchmark — mean errors by locked split', x=.065, ha='left', fontweight='bold', y=.98)
    fig.text(.065, .935, 'Lower is better. The reference is an acoustic Yamaha C5 recording set; edges are extrapolation cases.', fontsize=9)
    fig.text(.065, .025, 'One fixed early-energy gain per pair; stereo power features; no per-window normalization. These are recording-agreement metrics, not perceptual realism scores.', fontsize=8)
    fig.tight_layout(rect=(.02, .05, .99, .91), h_pad=3, w_pad=2)
    fig.savefig(destination/'summary.png', dpi=180)
    plt.close(fig)

    selected = [c for c in report['cases'] if c['split'] in ('heldout_velocity', 'heldout_pitch')]
    fig, axes = plt.subplots(1, 2, figsize=(12, 7.4), sharey=True)
    for ax, key, title in zip(axes, ['log_band_mae_db', 'envelope_mae_db'], ['Log-frequency band error', 'Amplitude-envelope error']):
        reductions = [-c['metrics'][key]['change'] for c in selected]
        colors = ['#197b70' if r >= 0 else '#c45a4c' for r in reductions]
        yy = np.arange(len(selected))
        ax.barh(yy, reductions, color=colors, height=.65)
        ax.axvline(0, color='#687382', linewidth=1)
        ax.set_yticks(yy, [f'{c["id"]}  ·  {"pitch" if c["split"] == "heldout_pitch" else "velocity"}' for c in selected])
        ax.set_title(title, loc='left', fontweight='bold', pad=10)
        ax.set_xlabel('Error reduction (dB); negative values are regressions')
        ax.set_axisbelow(True); ax.grid(axis='x', color='#e3e7ee', linewidth=.7)
        extent = max(max(abs(r) for r in reductions)*1.2, 1)
        ax.set_xlim(-extent, extent)
        for i, value in enumerate(reductions):
            ax.text(value+(.15 if value >= 0 else -.15), i, f'{value:+.2f}', ha='left' if value >= 0 else 'right', va='center', fontsize=8)
    axes[0].invert_yaxis()
    fig.suptitle('Every held-out case — improvements and regressions', x=.055, ha='left', y=.97, fontweight='bold')
    fig.tight_layout(rect=(.02, .03, .99, .93), w_pad=2)
    fig.savefig(destination/'heldout_cases.png', dpi=180)
    plt.close(fig)


def write_tables(report, destination):
    with (destination/'all_case_metrics.csv').open('w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'split', 'metric', 'units', 'baseline', 'candidate', 'change', 'status'])
        for case in report['cases']:
            for key, _, units in ALL_METRICS:
                pair = case['metrics'][key]
                writer.writerow([case['id'], case['split'], key, units, pair['baseline'], pair['candidate'], pair['change'], pair['status']])
    with (destination/'regressions.csv').open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'split', 'metric', 'label', 'units', 'baseline', 'candidate', 'increase'])
        writer.writeheader(); writer.writerows(report['regressions'])


def markdown(report, destination):
    lines = ['# Acoustic-piano benchmark: original and calibrated models', '',
        'The comparison uses 24 acoustic Yamaha C5 sample recordings and the same frozen analysis for both model versions. Ten recordings supplied parameter fitting; fourteen did not. These measurements quantify agreement with this recording setup. They do not establish acoustic indistinguishability or a percentage of realism.', '',
        '![Mean errors by split](summary.png)', '',
        '## Mean errors by split', '',
        '| Split | Cases | Band error (dB) | Partial levels (dB) | Envelope (dB) | Decay rate (dB/s) | Fundamental (cents) | Attack (ms) |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for split in SPLITS:
        group = report['summary'][split]
        values = []
        for key, _, _ in METRICS:
            item = group['metrics'][key]
            values.append('n/a' if item['baseline_mean'] is None else f"{item['baseline_mean']:.2f} → {item['candidate_mean']:.2f}")
        lines.append('| '+LABELS[split]+' | '+str(group['cases'])+' | '+' | '.join(values)+' |')
    lines += ['', 'Each cell shows original → calibrated. Lower is better. Means use only comparable case pairs; metric-specific counts are preserved in comparison.json.', '',
        '## Held-out cases', '', '![Every held-out case](heldout_cases.png)', '',
        '## All regressions', '',
        'Every case/metric increase above numerical tolerance is listed below, including training and edge cases. No regressing case was omitted from the aggregate.', '',
        '| Case | Split | Metric | Original | Calibrated | Increase |',
        '|---|---|---|---:|---:|---:|']
    for row in report['regressions']:
        lines.append(f"| {row['id']} | {LABELS[row['split']]} | {row['label']} ({row['units']}) | {row['baseline']:.3f} | {row['candidate']:.3f} | +{row['increase']:.3f} |")
    if not report['regressions']: lines.append('| None | | | | | |')
    lines += ['', 'Complete machine-readable results: [all cases](all_case_metrics.csv), [regressions](regressions.csv), [comparison and input hashes](comparison.json).', '',
        '## Measurement scope', '',
        '- Onsets are detected independently; stereo channels are combined in power, avoiding mono cancellation.',
        '- A single gain from 0.05–0.75 seconds aligns each pair. That gain remains fixed through all later windows. Absolute microphone gain is therefore excluded; velocity amplitude ratios need a separate analysis.',
        '- Band and partial-power measurements use 0.05–0.25, 0.25–0.75, 0.75–1.5 and 1.5–3.5 second windows. Pitch and decay use the frozen benchmark definitions.',
        '- The 10 training cases are C2–C6 at layers 4 and 12. Velocity holdouts are their layer-8 recordings plus C3/C4/C5 layer 6. Pitch holdouts are F#2–F#5 layer 8. C1/C7 layer 8 are separate extrapolation cases.',
        '- The library does not establish measured hammer speed, acquisition pedal state, microphone transfer or editing history. Its MIDI layer mapping is not a measured physical velocity.',
        '- C7 has too few reliable partials to identify inharmonicity; higher-partial analysis is excluded there. Recorded beating, room response and noise also affect measured decay.',
        '- The held-out recordings were excluded from parameter fitting. Their earlier baseline measurements were inspected, so this is not a blind evaluation.',
        '- Training gains are expected after calibration. The small held-out sets are a limited generalization check, not proof across other pianos or recording setups.', '',
        'Reference provenance and license: [reference manifest](../../reference/manifest.json). Model equations and limitations: [model notes](../../MODEL.md).', '']
    (destination/'report.md').write_text('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, default=ROOT/'benchmark/baseline_report.json')
    parser.add_argument('--candidate', type=Path, default=ROOT/'benchmark/candidate_report.json')
    parser.add_argument('--output-dir', type=Path, default=ROOT/'benchmark/report')
    parser.add_argument('--no-plots', action='store_true')
    args = parser.parse_args()
    report = compare_reports(args.baseline, args.candidate)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir/'comparison.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    write_tables(report, args.output_dir)
    if not args.no_plots: plots(report, args.output_dir)
    markdown(report, args.output_dir)
    print(json.dumps({'cases': len(report['cases']), 'regressions': len(report['regressions']),
                      'not_comparable': len(report['not_comparable']), 'report': str(args.output_dir/'report.md')}, indent=2))


if __name__ == '__main__': main()
