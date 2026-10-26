#!/usr/bin/env python3
"""Frozen historical regression for a passing ALL-TRAIN confidence-loss fit.

All sixteen references were observed in the earlier v4 study. This evaluator
does not download or acquire audio, identify materials, select a new fit, or
promote a default. Stages are freeze -> predictions -> score -> verify.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / 'out/full-confidence-loss'
OUT = CANDIDATE / 'historical'
PREVIOUS = ROOT / 'out/full-calibration/v4/evaluation'
REPORT = ROOT / 'Validation/full-confidence-loss-historical.json'
GROUPS = {
    'historical_extremes_previously_observed': ['A0v8', 'C8v8'],
    'historical_full_range': [f'C{o}v8' for o in range(1, 8)],
    'historical_interpolation': ['A3v4', 'A3v8', 'A3v12', 'D#3v8',
                                 'D#4v8', 'A4v8', 'D#5v8'],
}
IDS = [ident for group in GROUPS.values() for ident in group]
METRICS = ('harmonic_level_mae_db', 'envelope_mae_db', 'log_band_mae_db',
           'absolute_f1_error_cents', 'partial_tuning_mae_cents',
           'partial_decay_slope_mae_db_per_second', 'attack_rise10_90_error_ms')


def now():
    return datetime.now(timezone.utc).isoformat()


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def record(path):
    path = Path(path).resolve()
    return {'path': str(path), 'sha256': sha(path)}


def verify(records):
    for row in records:
        if sha(row['path']) != row['sha256']:
            raise ValueError('Frozen input changed: ' + row['path'])


def write_once(path, value):
    """A failed/interrupted stage may resume only with identical receipts."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if read(path) != value:
            raise ValueError('Refuse to replace an existing receipt: ' + str(path))
        return
    with path.open('x') as stream:
        stream.write(json.dumps(value, indent=2, allow_nan=False) + '\n')


def finite_full(metrics):
    if (metrics['nonfinite_samples'] != 0 or metrics['string_count'] != 230
            or metrics['board_modes'] != 475 or metrics['sample_rate'] != 48000
            or metrics['duration_seconds'] != 3.8):
        raise ValueError('Invalid full-model prediction')


def candidate_lock():
    """Check this before any prior evaluation receipt/feature/audio access."""
    frozen = read(CANDIDATE / 'candidate-freeze.json')
    expected = {'profile': CANDIDATE / 'calibration.json',
                'source': CANDIDATE / 'solver/grand.cpp',
                'header': CANDIDATE / 'solver/calibration.h',
                'binary': CANDIDATE / 'solver/render',
                'protocol': CANDIDATE / 'freeze.json',
                'training_report': CANDIDATE / 'report.json',
                'train_predictions': CANDIDATE / 'renders/render-manifest.json'}
    for key, path in expected.items():
        if Path(frozen[key]['path']).resolve() != path.resolve():
            raise ValueError('Unexpected frozen candidate path: ' + key)
        verify([frozen[key]])
    training = read(expected['training_report'])
    comparison = training['all_training_vs_v4']
    if (training.get('passes_all_training_gates_vs_v4') is not True
            or comparison.get('passes_all_gates') is not True
            or not comparison.get('gates')
            or not all(value is True for value in comparison['gates'].values())
            or training.get('evaluation_data_used_for_fit') is not False
            or training.get('default_promoted') is not False
            or frozen.get('default_promoted') is not False):
        raise ValueError('A passing unpromoted TRAIN-only frozen candidate is required')
    protocol = read(expected['protocol'])
    verify(protocol['inputs'])
    split = read(ROOT / 'References/GrandFullRange/split.json')
    if (set(protocol['all_training_ids']) != set(split['combined_training_ids'])
            or len(protocol['all_training_ids']) != 34
            or set(IDS) & set(protocol['all_training_ids'])):
        raise ValueError('Locked TRAIN/historical inventories disagree')
    for key in ('profile', 'header'):
        if training[key] != frozen[key]:
            raise ValueError('TRAIN report/candidate binding differs: ' + key)
    verify([training['freeze'], training['build'], training['score']])
    if training['freeze'] != frozen['protocol']:
        raise ValueError('TRAIN protocol binding differs')
    if training['predictions']['manifest'] != frozen['train_predictions']:
        raise ValueError('TRAIN prediction binding differs')
    build = read(training['build']['path'])
    for key in ('source', 'header', 'binary'):
        if build[key] != frozen[key]:
            raise ValueError('Candidate build binding differs: ' + key)
    return frozen


def event_text(row):
    return ('# Frozen historical prediction; recording acquisition pedal unknown.\n'
            f"0.100000 on {row['midi']} {row['midi_velocity']}\n"
            f"4.150000 off {row['midi']} 0\n")


def check_events(path, row):
    parsed = [line.split() for line in Path(path).read_text().splitlines()
              if line.strip() and not line.lstrip().startswith('#')]
    try:
        actual = [(float(v[0]), v[1], int(v[2]), float(v[3])) for v in parsed]
    except (ValueError, IndexError) as error:
        raise ValueError('Invalid MIDI event file: ' + str(path)) from error
    expected = [(.1, 'on', row['midi'], float(row['midi_velocity'])),
                (4.15, 'off', row['midi'], 0.)]
    if actual != expected or any(len(v) != 4 for v in parsed):
        raise ValueError('Historical held-note event policy differs: ' + str(path))


def previous_bindings():
    """Authenticate cached controls and observed reference identities only."""
    old = read(PREVIOUS / 'freeze.json')
    acquired = read(PREVIOUS / 'acquisition.json')
    predictions = read(PREVIOUS / 'predictions.json')
    results = read(PREVIOUS / 'results.json')
    verify(old['inputs'])
    verify([old['training_result'], acquired['freeze'], acquired['predictions'],
            acquired['opening'], results['freeze'], results['acquisition'],
            results['predictions'], predictions['freeze']])
    opening = read(PREVIOUS / 'reference-opening-started.json')
    if (acquired['freeze'] != record(PREVIOUS / 'freeze.json')
            or results['freeze'] != acquired['freeze']
            or predictions['freeze'] != acquired['freeze']
            or opening['freeze'] != acquired['freeze']
            or opening['predictions'] != record(PREVIOUS / 'predictions.json')
            or acquired['predictions'] != record(PREVIOUS / 'predictions.json')
            or results['acquisition'] != record(PREVIOUS / 'acquisition.json')
            or results['predictions'] != record(PREVIOUS / 'predictions.json')):
        raise ValueError('Historical chronology receipt bindings disagree')
    cases = {row['id']: row for row in old['cases']}
    sources = {row['id']: row for row in acquired['samples']}
    if (len(cases) != 16 or set(cases) != set(IDS)
            or len(sources) != 16 or set(sources) != set(IDS)
            or len(predictions['renders']) != 32):
        raise ValueError('Historical inventory changed')
    inputs = [record(PREVIOUS / name) for name in
              ('freeze.json', 'training-result.json', 'acquisition.json',
               'reference-opening-started.json', 'predictions.json', 'results.json',
               'reference-features.json', 'control-model-features.json',
               'candidate-model-features.json')]
    for source in sources.values():
        verify([source['wav'], source['flac']])
        if not source.get('git_blob_verified') or not source.get('decoded_pcm'):
            raise ValueError('Missing authenticated historical PCM/source receipt')
        inputs += [source['wav'], source['flac']]
    labels = ('control', 'candidate')
    for label in labels:
        producer = old['producers'][label]
        for key in ('source', 'header', 'binary'):
            inputs.append(record(producer[key]))
        models = {row['id']: row for row in
                  read(PREVIOUS / (label + '-model-features.json'))['samples']}
        comparisons = {row['id']: row for row in results['variants'][label]['comparison']}
        if set(models) != set(IDS) or set(comparisons) != set(IDS):
            raise ValueError('Cached historical measurements incomplete')
        selected = [row for row in predictions['renders'] if row['variant'] == label]
        if len(selected) != 16 or {row['id'] for row in selected} != set(IDS):
            raise ValueError('Cached historical predictions incomplete')
        for prediction in selected:
            row = cases[prediction['id']]
            command = prediction['command']
            if len(prediction['outputs']) != 1 or len(command) != 9:
                raise ValueError('Unexpected cached full-output inventory/command')
            wav = Path(prediction['outputs'][0]['path'])
            events = Path(command[command.index('--events') + 1])
            expected = [producer['binary'], '--events', str(events), '--output',
                        str(wav), '--sample-rate', '48000', '--duration', '3.8']
            if command != expected or sha(events) != prediction['event_sha256']:
                raise ValueError('Cached prediction producer/event mismatch')
            check_events(events, row)
            verify(prediction['outputs']); finite_full(prediction['metrics'])
            if (models[row['id']]['sha256'] != sha(wav)
                    or comparisons[row['id']]['model_sha256'] != sha(wav)
                    or comparisons[row['id']]['reference_sha256'] != sources[row['id']]['wav']['sha256']):
                raise ValueError('Cached measurement/audio identity differs')
            inputs += [record(events), *prediction['outputs']]
    # Never mutate the legacy fresh/held-out roles in their original receipts.
    rows = []
    for ident in IDS:
        source = cases[ident]
        rows.append({'id': ident, 'midi': source['midi'],
                     'midi_velocity': source['midi_velocity'],
                     'role': 'historical_observed', 'previous_role': source['role'],
                     'group': next(k for k, names in GROUPS.items() if ident in names),
                     'reference': sources[ident]})
    return rows, inputs


def freeze():
    candidate = candidate_lock()
    if (OUT / 'freeze.json').exists():
        raise ValueError('Historical protocol already frozen; use later stages')
    rows, inputs = previous_bindings()
    code = [Path(__file__), ROOT / 'tools/evaluate_full_candidate.py',
            ROOT / 'tools/fit_full_calibration.py',
            ROOT / 'tools/extract_full_range_grand.py', ROOT / 'tools/full_range_pitch.py',
            ROOT / 'tools/fetch_full_range_grand.py',
            ROOT / 'Research/GrandPianoV2/tools/benchmark.py',
            ROOT / 'Research/GrandPianoV2/tools/fit_calibration.py',
            ROOT / 'Research/GrandPianoV2/tools/radiation_fit.py',
            ROOT / 'Research/GrandPianoV2/reference/fetch_reference.py']
    inputs += [record(path) for path in code]
    inputs += [record(CANDIDATE / 'candidate-freeze.json'), *candidate_records(candidate)]
    unique = {row['path']: row for row in inputs}
    verify(unique.values())
    result = {'schema_version': 1, 'frozen_at_utc': now(),
              'candidate_freeze': record(CANDIDATE / 'candidate-freeze.json'),
              'inputs': list(unique.values()), 'cases': rows,
              'groups': GROUPS, 'fresh_cases': [], 'all_references_previously_observed': True,
              'protocol': {'sample_rate': 48000, 'duration_seconds': 3.8,
                           'note_on_seconds': .1, 'note_off_seconds': 4.15, 'pedal': 0,
                           'maximum_concurrent_renders': 2,
                           'new_predictions': 16, 'cached_predictions': 32,
                           'velocity': 'Unchanged pinned SFZ-bin MIDI midpoint.',
                           'features': 'Reuse observed reference features and frozen legacy formulas; preserve reference censoring/window/envelope support.',
                           'components': 'Unchanged reference-fixed component centers/windows, including ambiguous C8; no model-peak substitution.',
                           'gain': 'One early0.05–0.75s RMS scalar per case, fixed across note.',
                           'attack': 'Equal mean of case MAEs over valid5–100ms reference-prominent bands above250Hz; retain0–5ms/sub250Hz diagnostics.'},
              'interpretation': 'Historical regression after ALL-TRAIN fitting. Both formerly fresh extremes were observed previously. No fresh, independent instrument/mic, perceptual or realtime claim.',
              'selection': 'No fitting or default promotion; retain every case/regression versus original control and frozen v4.',
              'historical_references_used_for_this_fit': False,
              'new_acquisition_or_download': False, 'default_promoted': False}
    candidate_lock(); write_once(OUT / 'freeze.json', result)
    print(str(OUT / 'freeze.json'), sha(OUT / 'freeze.json'), flush=True)


def candidate_records(candidate):
    return [candidate[key] for key in ('profile', 'source', 'header', 'binary',
                                      'protocol', 'training_report', 'train_predictions')]


def locked():
    candidate_lock()
    frozen = read(OUT / 'freeze.json')
    verify([frozen['candidate_freeze'], *frozen['inputs']])
    if ([r['id'] for r in frozen['cases']] != IDS or frozen['groups'] != GROUPS
            or frozen['fresh_cases'] or not frozen['all_references_previously_observed']):
        raise ValueError('Historical protocol inventory/roles changed')
    return frozen


def predictions(jobs):
    frozen = locked(); candidate = read(frozen['candidate_freeze']['path'])
    if (OUT / 'score-started.json').exists():
        raise ValueError('Prediction stage closed after historical scoring started')
    folder = OUT / 'predictions'; folder.mkdir(parents=True, exist_ok=True)

    def one(row):
        events = folder / (row['id'] + '.events'); wav = folder / (row['id'] + '.wav')
        text = event_text(row)
        if events.exists() and events.read_text() != text:
            raise ValueError('Cached event file changed')
        if not events.exists():
            with events.open('x') as stream: stream.write(text)
        command = [candidate['binary']['path'], '--events', str(events), '--output',
                   str(wav), '--sample-rate', '48000', '--duration', '3.8']
        sidecar = folder / (row['id'] + '.json')
        if sidecar.exists():
            cached = read(sidecar); verify(cached['outputs'])
            if (cached['command'] != command or cached['events'] != record(events)
                    or cached['candidate_freeze'] != frozen['candidate_freeze']):
                raise ValueError('Cached historical prediction binding differs')
            finite_full(cached['metrics']); return cached
        if wav.exists():
            raise ValueError('Unreceipted output exists; inspect interrupted render: ' + str(wav))
        call = subprocess.run(command, check=True, text=True, capture_output=True)
        metrics = json.loads(call.stdout); finite_full(metrics)
        result = {'id': row['id'], 'variant': 'confidence_loss', 'role': 'historical_observed',
                  'candidate_freeze': frozen['candidate_freeze'], 'command': command,
                  'events': record(events), 'outputs': [record(wav)], 'metrics': metrics}
        write_once(sidecar, result); print(row['id'] + ' historical prediction complete', flush=True)
        return result

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        results = list(pool.map(one, frozen['cases']))
    locked()
    receipt = {'freeze': record(OUT / 'freeze.json'), 'new_predictions': 16,
               'historical_observed_only': True, 'renders': sorted(results, key=lambda r: r['id'])}
    write_once(OUT / 'predictions.json', receipt)


def prediction_lock(frozen):
    receipt = read(OUT / 'predictions.json')
    verify([receipt['freeze']])
    if receipt['freeze'] != record(OUT / 'freeze.json'):
        raise ValueError('Prediction/protocol binding differs')
    rows = {row['id']: row for row in frozen['cases']}
    predictions = receipt['renders']
    if len(predictions) != 16 or {r['id'] for r in predictions} != set(IDS):
        raise ValueError('All sixteen historical predictions are required')
    for row in predictions:
        verify([row['events'], *row['outputs']]); check_events(row['events']['path'], rows[row['id']])
        events = OUT / 'predictions' / (row['id'] + '.events')
        wav = OUT / 'predictions' / (row['id'] + '.wav')
        candidate = read(frozen['candidate_freeze']['path'])
        expected_command = [candidate['binary']['path'], '--events', str(events),
                            '--output', str(wav), '--sample-rate', '48000', '--duration', '3.8']
        if (row['candidate_freeze'] != frozen['candidate_freeze']
                or row['events'] != record(events) or row['outputs'] != [record(wav)]
                or row['command'] != expected_command or row['variant'] != 'confidence_loss'
                or row['role'] != 'historical_observed'):
            raise ValueError('Prediction candidate binding differs')
        if read(events.with_suffix('.json')) != row:
            raise ValueError('Prediction receipt/sidecar differs')
        finite_full(row['metrics'])
    return receipt


def helper():
    """Lazy import only after model/protocol/prediction checks have passed."""
    sys.dont_write_bytecode = True
    path = ROOT / 'tools/evaluate_full_candidate.py'
    spec = importlib.util.spec_from_file_location('historical_full_loss_measurement', path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def mean(values):
    valid = [float(v) for v in values if v is not None and math.isfinite(v)]
    return sum(valid) / len(valid) if valid else None


def attack_cases(variant):
    return {row['id']: mean(abs(value) for window in row['differences']
             if .005 <= window['window_seconds'][0] < .1
             for j, value in enumerate(window['band_error_db'])
             if j > 0 and window['reference_prominent_band_mask'][j])
            for row in variant['attack_texture']}


def compare(a, b, ids):
    left = {r['id']: r for r in a['comparison']}; right = {r['id']: r for r in b['comparison']}
    aa, ba = attack_cases(a), attack_cases(b)
    cases = []
    for ident in ids:
        values = {}
        for key in (*METRICS, 'attack_band_mae_db'):
            x = aa[ident] if key == 'attack_band_mae_db' else left[ident].get(key)
            y = ba[ident] if key == 'attack_band_mae_db' else right[ident].get(key)
            values[key] = {'baseline': x, 'candidate': y,
                           'change': y-x if x is not None and y is not None else None}
        cases.append({'id': ident, **values,
                      'spurious_baseline': len(left[ident]['spurious_prominent_model_bands']),
                      'spurious_candidate': len(right[ident]['spurious_prominent_model_bands'])})
    aggregates = {}
    for key in (*METRICS, 'attack_band_mae_db'):
        valid = [r[key] for r in cases if r[key]['change'] is not None]
        aggregates[key] = {'baseline_mean': mean(r['baseline'] for r in valid),
                           'candidate_mean': mean(r['candidate'] for r in valid),
                           'mean_change': mean(r['change'] for r in valid),
                           'worst_case_regression': max((r['change'] for r in valid), default=None),
                           'valid_cases': len(valid),
                           'improved_cases': sum(r['change'] < 0 for r in valid)}
    return {'cases': cases, 'aggregate': aggregates,
            'harmonic_or_envelope_regressions_above2db': [
                {'id': r['id'], 'metric': key, 'change': r[key]['change']}
                for r in cases for key in ('harmonic_level_mae_db', 'envelope_mae_db')
                if r[key]['change'] is not None and r[key]['change'] > 2.]}


def historical_variant(variant):
    """Retain numeric cached evidence while naming its now-observed role."""
    groups = {ident: group for group, ids in GROUPS.items() for ident in ids}
    return {**variant, 'comparison': [
        {**row, 'previous_split': row['split'], 'split': groups[row['id']],
         'role': 'historical_observed'} for row in variant['comparison']]}


def score():
    frozen = locked(); predictions = prediction_lock(frozen)
    if (OUT / 'results.json').exists():
        raise ValueError('Historical scoring already completed; use verify')
    started = OUT / 'score-started.json'
    if not started.exists():
        write_once(started, {'started_at_utc': now(), 'freeze': record(OUT / 'freeze.json'),
                            'predictions': record(OUT / 'predictions.json'),
                            'all_references_previously_observed': True})
    else:
        verify([read(started)['freeze'], read(started)['predictions']])
    measurement = helper(); pcm = measurement.acquisition.load_pcm_helper()
    refs = read(PREVIOUS / 'reference-features.json')['samples']
    if len(refs) != 16 or {r['id'] for r in refs} != set(IDS):
        raise ValueError('Observed reference feature inventory differs')
    old = read(PREVIOUS / 'results.json'); byid = {r['id']: r for r in frozen['cases']}
    predictions_by_id = {r['id']: r for r in predictions['renders']}
    models, comparisons, attacks, components, identities = [], [], [], [], []
    for original in refs:
        row = byid[original['id']]; source = row['reference']; verify([source['wav'], source['flac']])
        if original['sha256'] != source['wav']['sha256']:
            raise ValueError('Observed feature/reference container identity differs')
        identity = pcm.decoded_pcm_identity(Path(source['wav']['path']))
        if identity != source['decoded_pcm']:
            raise ValueError('Observed reference PCM identity differs')
        ref = dict(original, path=source['wav']['path'], split=row['group'],
                   role='historical_observed', previous_role=row['previous_role'])
        prediction = predictions_by_id[ref['id']]
        model, comparison, attack, component = measurement.measure_pair(
            ref, Path(prediction['outputs'][0]['path']))
        models.append(model); comparisons.append(comparison); attacks.append(attack); components += component
        identities.append({'id': ref['id'], 'wav': source['wav'], 'decoded_pcm': identity,
                           'preserved_analysis_windows_seconds': ref.get('analysis_windows_seconds'),
                           'preserved_component_frequencies_hz': [r['frequency_hz'] for r in ref.get('unassigned_components', [])]})
        print(ref['id'] + ' historical comparison scored', flush=True)
    variant = {'comparison': comparisons, 'attack_texture': attacks,
               'unassigned_component_comparison': components,
               'spurious_model_band_diagnostic': {
                   'case_count_with_flags': sum(bool(r['spurious_prominent_model_bands']) for r in comparisons),
                   'flagged_window_band_pairs': sum(len(r['spurious_prominent_model_bands']) for r in comparisons)}}
    baselines = {'original_control': historical_variant(old['variants']['control']),
                 'v4': historical_variant(old['variants']['candidate'])}
    comparison_groups = {group: {label: compare(v, variant, ids) for label, v in baselines.items()}
                         for group, ids in {'all_historical': IDS, **GROUPS}.items()}
    locked(); prediction_lock(frozen)
    write_once(OUT / 'model-features.json', {'samples': models, 'freeze': record(OUT / 'freeze.json'),
                                           'predictions': record(OUT / 'predictions.json')})
    result = {'schema_version': 1, 'scored_at_utc': now(), 'freeze': record(OUT / 'freeze.json'),
              'candidate_freeze': frozen['candidate_freeze'],
              'predictions': record(OUT / 'predictions.json'), 'score_started': record(started),
              'model_features': record(OUT / 'model-features.json'),
              'previous_evaluation': record(PREVIOUS / 'results.json'),
              'observed_reference_features': record(PREVIOUS / 'reference-features.json'),
              'reference_identities': identities, 'groups': GROUPS,
              'comparison_groups': comparison_groups,
              'candidate': variant, 'cached_baseline_variants': baselines,
              'source_quality_reused': [
                  {**row, 'previous_role': row.get('role'), 'role': 'historical_observed'}
                  for row in old['source_quality']],
              'fresh_cases': [], 'all_references_previously_observed': True,
              'historical_results_used_for_fit_or_parameter_selection': False,
              'default_promoted': False, 'canonical_model_changed': False,
              'interpretation': 'Regression on sixteen previously observed cases of one recording setup after ALL-TRAIN fitting; no fresh or independent generalization claim.',
              'limits': ['Every case and regression retained. Metrics are not perceptual scores.',
                         'Unknown hammer speed, pedal, room and editing remain confounds.',
                         'C8 reference ambiguity and missing fixed-band components remain explicit.',
                         'No realtime, Reason SDK/host or production-readiness claim.']}
    write_once(OUT / 'results.json', result); write_once(REPORT, result)


def verify_all():
    frozen = locked()
    if (OUT / 'predictions.json').exists(): prediction_lock(frozen)
    if (OUT / 'results.json').exists():
        result = read(OUT / 'results.json')
        verify([result[key] for key in ('freeze', 'candidate_freeze', 'predictions',
                                      'score_started', 'model_features', 'previous_evaluation',
                                      'observed_reference_features')])
        if result != read(REPORT):
            raise ValueError('Historical result copies differ')
    print('Frozen candidate/protocol and available prediction/score receipts match', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('freeze', 'predictions', 'score', 'verify'))
    parser.add_argument('--jobs', type=int, default=2)
    args = parser.parse_args()
    if not 1 <= args.jobs <= 2: parser.error('Use1–2 concurrent renders')
    if args.stage == 'freeze': freeze()
    elif args.stage == 'predictions': predictions(args.jobs)
    elif args.stage == 'score': score()
    else: verify_all()


if __name__ == '__main__':
    main()
