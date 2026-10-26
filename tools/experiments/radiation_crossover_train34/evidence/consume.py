#!/usr/bin/env python3
"""Once-only consumer of the frozen full-TRAIN34 compatibility confirmation.

The producer owns28 new fixed400Hz WAVs. This consumer never renders or
reprocesses audio. Six prior outcomes are reused exactly, without rescoring.
"""
from pathlib import Path
from datetime import datetime, timezone
import argparse
import hashlib
import importlib.util
import json
import math
import numpy as np

OUT = Path(__file__).resolve().parent
REFERENCE_SOURCE_SHA = '45b38bc157afdff800c1c2f9c6090d4c51225acb058f5057f214808d0a74e3b6'
REFERENCE_SHA = 'e3ad140a8052c2e81acdc0a281a4e658a2df7f796029572d562634c8adf375fe'


def now(): return datetime.now(timezone.utc).isoformat()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p): return json.loads(Path(p).read_text())
def record(p): return {'path': str(Path(p).resolve()), 'sha256': sha(p)}


def write(path, value):
    path = Path(path).resolve()
    if OUT not in path.parents or path.exists(): raise ValueError('Private new output required: '+str(path))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def load_reference_module():
    path = OUT/'measure_references.py'
    if sha(path) != REFERENCE_SOURCE_SHA: raise ValueError('Frozen reference metric source changed')
    spec = importlib.util.spec_from_file_location('train34_reference_metrics', path)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


def dependencies():
    helper = load_reference_module()
    metric, operator, original_protocol, training = helper.dependencies()
    if sha(OUT/'reference-control.json') != REFERENCE_SHA: raise ValueError('Reference/control report changed')
    references = read(OUT/'reference-control.json')
    helper.verify(references['inputs'])
    cases = {r['id']: r for r in references['cases']}
    if set(cases) != {r['id'] for r in training}: raise ValueError('Full TRAIN inventory mismatch')
    originals = {r['id']: r for r in read(helper.OLD_REFERENCE)['cases']}
    for ident in helper.OLD_IDS:
        for key, value in originals[ident].items():
            if cases[ident][key] != value: raise ValueError('Existing six reference features changed: '+ident)
    return helper, metric, operator, original_protocol, training, cases


def locked():
    helper, metric, operator, original_protocol, training, references = dependencies()
    freeze = read(OUT/'protocol-freeze.json'); protocol = read(OUT/'protocol.json')
    if freeze['consumer_source'] != record(__file__) or freeze['protocol'] != record(OUT/'protocol.json'):
        raise ValueError('Consumer/protocol source freeze changed')
    if protocol['reference_control'] != record(OUT/'reference-control.json') or protocol['reference_source'] != record(OUT/'measure_references.py'):
        raise ValueError('Protocol omits exact reference measurements')
    if protocol['fixed400_operator'] != record(helper.OPERATOR) or protocol['existing_six_result'] != record(helper.OLD_RESULT):
        raise ValueError('Fixed operator/existing outcomes changed')
    if protocol['original_preservation_gates'] != original_protocol['gates']:
        raise ValueError('Preservation thresholds changed')
    if [c['id'] for c in protocol['cases']] != [r['id'] for r in training]:
        raise ValueError('Protocol case order/inventory differs')
    for case in protocol['cases']:
        old = references[case['id']]
        if (case['fixed_old_gain'], case['fixed_old_onset_frame'], case['support']) != (old['baseline']['fixed_gain'], old['baseline']['fixed_onset_frame'], old['support']):
            raise ValueError('Per-case gain/onset/support differs: '+case['id'])
    helper.verify(protocol['inputs'])
    return helper, metric, operator, protocol, training, references


def proof_rows(helper, entry):
    proof = entry['parity_proof']
    helper.verify([proof['state_rows'], proof['force_rows']])
    state = np.frombuffer(Path(proof['state_rows']['path']).read_bytes(), dtype='<u8')
    force = np.frombuffer(Path(proof['force_rows']['path']).read_bytes(), dtype='<u8')
    checkpoints = np.r_[np.arange(0, helper.FRAMES, 256), helper.FRAMES-1].astype(np.uint64)
    if state.size != len(checkpoints)*3 or force.size != helper.FRAMES*3:
        raise ValueError('Incomplete source state/force proof rows: '+entry['id'])
    state = state.reshape((-1, 3)); force = force.reshape((-1, 3))
    if not np.array_equal(state[:, 0], checkpoints) or not np.array_equal(force[:, 0], np.arange(helper.FRAMES, dtype=np.uint64)):
        raise ValueError('Source proof frame schedule differs: '+entry['id'])
    state_equal = bool(np.array_equal(state[:, 1], state[:, 2]))
    force_equal = bool(np.array_equal(force[:, 1], force[:, 2]))
    if entry['mechanical_state_bit_parity'] is not state_equal or entry['force_bit_parity'] is not force_equal:
        raise ValueError('Declared source proof differs from actual stored rows: '+entry['id'])
    return {'mechanical_state_bit_parity': state_equal, 'force_bit_parity': force_equal,
            'new_faults': entry['new_faults'], 'state_checkpoints': len(checkpoints), 'force_frames': helper.FRAMES,
            'scope': 'One physical trajectory: read-only observer pre/post hashes. Sampled stated fields and every-frame contact88/Schur3 force bytes; not every internal state or an independent mechanical rerender. FNV has no cryptographic collision guarantee.'}


def producer_evidence(helper, protocol, capture):
    expected_protocol = record(OUT/'protocol.json')
    if capture['protocol'] != expected_protocol: raise ValueError('Capture does not bind final TRAIN34 protocol')
    helper.verify([capture['producer_receipt']]); producer = read(capture['producer_receipt']['path'])
    plan_record = protocol['producer_contract']['producer_plan']
    helper.verify([plan_record]); plan = read(plan_record['path'])
    if producer['protocol'] != expected_protocol or producer['producer_plan'] != plan_record:
        raise ValueError('Producer lacks exact protocol/plan binding')
    freeze_record = producer['candidate_freeze']; helper.verify([freeze_record]); freeze = read(freeze_record['path'])
    if freeze['protocol'] != expected_protocol or freeze['producer_plan'] != plan_record:
        raise ValueError('Producer freeze omits protocol/plan')
    for key in ('source_inputs', 'binary', 'configuration'):
        if producer[key] != plan[key] or freeze[key] != plan[key]: raise ValueError('Producer deviates from frozen plan: '+key)
    if producer['configuration'] != protocol['producer_contract']['configuration']:
        raise ValueError('Producer configuration deviates from protocol')
    helper.verify([producer['binary'], *producer['source_inputs']])
    hashes = {r['sha256'] for r in producer['source_inputs']}
    for key in ('prepared_model_sha256', 'calibration_sha256', 'observer_header_sha256'):
        if protocol['producer_contract'][key] not in hashes: raise ValueError('Missing fixed producer source: '+key)
    if producer['fixed400_operator'] != protocol['fixed400_operator'] or freeze['fixed400_operator'] != protocol['fixed400_operator']:
        raise ValueError('Producer operator deviates')
    times = [protocol['frozen_at_utc'], freeze['frozen_at_utc'], producer['render_started_at_utc']]
    if [datetime.fromisoformat(t) for t in times] != sorted(datetime.fromisoformat(t) for t in times):
        raise ValueError('Protocol/source/render chronology differs')
    ids = [r['id'] for r in protocol['cases'] if r['role'] == 'new_confirmation']
    if [r['id'] for r in capture['cases']] != ids or [r['id'] for r in producer['cases']] != ids:
        raise ValueError('Producer new28 inventory/order differs')
    cases = {r['id']: r for r in protocol['cases']}; evidence = {}
    for entry, declaration in zip(capture['cases'], producer['cases']):
        if entry != declaration: raise ValueError('Capture/producer case evidence differs: '+entry['id'])
        expected = cases[entry['id']]
        if (entry['midi'], entry['velocity'], entry['frames']) != (expected['midi'], expected['midi_velocity'], helper.FRAMES):
            raise ValueError('Producer MIDI/velocity/frame request differs')
        for role in ('baseline', 'causal', 'candidate'):
            if Path(entry[role]['path']).resolve() != Path(expected['expected_output_paths'][role]).resolve():
                raise ValueError('Producer output path differs from predeclared inventory: '+entry['id']+'/'+role)
        if type(entry['new_faults']) is not int or entry['new_faults'] < 0: raise ValueError('Invalid fault declaration')
        diagnostics = entry['diagnostics']
        faults = [diagnostics['original_fault_flags'], diagnostics['new_observer_faults']]
        if any(type(value) is not int or value < 0 for value in faults) or entry['new_faults'] != (faults[0] | faults[1]):
            raise ValueError('Fault guard must include physical/API and observer flags: '+entry['id'])
        post = entry['postprocessor_contract']
        if post['fixed400_operator'] != protocol['fixed400_operator'] or post['canonical_partition'] != [64] or post['alternate_partitions'] != [1, 3, 17, 64, 129, 7]:
            raise ValueError('Postprocessor contract differs')
        if post['partitions_byte_identical'] is not True or post['finite_output_and_final_state'] is not True:
            raise ValueError('Postprocessor numerical proof failed')
        helper.verify([entry['baseline'], entry['causal'], entry['candidate']])
        evidence[entry['id']] = proof_rows(helper, entry)
    return evidence, [capture['producer_receipt'], plan_record, freeze_record, producer['binary'], *producer['source_inputs']]


def evaluate(capture_path):
    helper, metric, operator, protocol, training, references = locked()
    if (OUT/'candidate-opening-started.json').exists(): raise ValueError('Once-only confirmation already started; no silent rerun/rescore')
    write(OUT/'candidate-opening-started.json', {'started_at_utc': now(), 'protocol_freeze': record(OUT/'protocol-freeze.json'),
          'capture_path': str(Path(capture_path).resolve()), 'new_candidate_PCM_opened': False})
    capture = read(capture_path); capture_identity = record(capture_path)
    evidence, producer_records = producer_evidence(helper, protocol, capture)
    original_outcomes = {r['id']: r for r in read(helper.OLD_RESULT)['cases']}
    entries = {r['id']: r for r in capture['cases']}; rows = {r['id']: r for r in training}
    gate, gate_sha = operator.gate_function(metric, Path(helper.METRIC).read_text())
    results = []
    for case in protocol['cases']:
        ident = case['id']
        if case['role'] == 'reused_frozen_six':
            result = original_outcomes[ident]
            if result != case['reused_outcome']: raise ValueError('Existing six outcome changed')
        else:
            entry = entries[ident]; old = references[ident]
            try:
                candidate = helper.read_float_snapshot(entry['candidate'])
                baseline = helper.read_float_snapshot(entry['baseline'])
                cached = helper.read_float_snapshot(old['baseline_audio'])
                baseline_exact = baseline.tobytes() == cached.tobytes()
                features = helper.observation_features(metric, candidate.astype(np.float64), case['fixed_old_onset_frame'],
                           case['fixed_old_gain'], old['reference'], rows[ident], case['support'])
                scored = gate(old, features, ident, baseline_exact, evidence)
                result = {'id': ident, 'baseline_audio': entry['baseline'], 'causal_audio': entry['causal'], 'candidate_audio': entry['candidate'],
                          'candidate': features, **scored, 'source_proof': evidence[ident], 'support': case['support'],
                          'per_band_signed_error_change_db': [[n-b for n, b in zip(new['band_signed_errors_db'], base['band_signed_errors_db'])]
                                                            for new, base in zip(features['early'], old['baseline']['early'])],
                          'unassigned_component_scope': 'Reference-fixed diagnostics only; no added/tuned gate or physical assignment.'}
            except (ValueError, FloatingPointError) as error:
                result = {'id': ident, 'passes_all_case_gates': False, 'invalid_case': True,
                          'error_type': type(error).__name__, 'error': str(error), 'not_dropped_or_retried': True}
            write(OUT/'case-results'/(ident+'.json'), result)
        results.append(result)
        print(ident, 'PASS' if result['passes_all_case_gates'] else 'FAIL', 'reused' if case['role'] == 'reused_frozen_six' else 'new', flush=True)
    helper.verify([capture_identity, *producer_records]); locked()
    for entry in capture['cases']:
        helper.verify([entry['baseline'], entry['causal'], entry['candidate'], entry['parity_proof']['state_rows'], entry['parity_proof']['force_rows']])
    for ident in helper.OLD_IDS:
        if next(r for r in results if r['id'] == ident) != original_outcomes[ident]: raise ValueError('Reused outcome mutated')
    write(OUT/'result.json', {'schema_version': 1, 'completed_at_utc': now(), 'protocol': record(OUT/'protocol.json'),
          'protocol_freeze': record(OUT/'protocol-freeze.json'), 'reference_control': record(OUT/'reference-control.json'),
          'consumer_source': record(__file__), 'capture': capture_identity, 'verified_producer_inputs': producer_records,
          'original_gate_arithmetic_sha256': gate_sha, 'reused_frozen_six': list(helper.OLD_IDS), 'new_cases_scored_once': 28,
          'cases': results, 'passes_all_preservation_gates': all(r['passes_all_case_gates'] for r in results),
          'failed_case_ids': [r['id'] for r in results if not r['passes_all_case_gates']], 'source_DSP_renders_by_consumer': 0,
          'gain_onset_gate_or_operator_changes': False, 'fit_or_acquisition': False, 'reserved_or_historical_evaluation_used': False,
          'limits': ['All34 are already observed TRAIN, never independent holdouts.', 'Six original outcomes copied exactly without reprocessing/rescoring.',
                     'Relative preservation guards allow small regressions and do not prove recording parity or audibility.',
                     'Original reference prominence masks remain; every weak H1 band is retained separately.',
                     'C8 near4434Hz remains unassigned and potentially missing; its diagnostic does not relax any guard.',
                     'C8v4 uses only three complete late windows and full-support envelope samples, without padding or shifted alignment.',
                     'No realtime/SDK/Reason host proof or automatic default/runtime integration.'], 'adopted': False, 'published': False})


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--check-source', action='store_true'); parser.add_argument('--evaluate', type=Path)
    args = parser.parse_args()
    if args.check_source:
        helper, metric, operator, _, training, references = dependencies()
        gate, gate_sha = operator.gate_function(metric, Path(helper.METRIC).read_text())
        print(json.dumps({'passed': True, 'source': record(__file__), 'reference_control': record(OUT/'reference-control.json'),
                          'TRAIN_cases': len(training), 'exact_existing_reference_reuse': len(helper.OLD_IDS),
                          'exact_original_gate_arithmetic_sha256': gate_sha, 'new_candidate_PCM_opened': False}, indent=2))
    elif args.evaluate:
        try: evaluate(args.evaluate)
        except Exception as error:
            write(OUT/'consumer-failure.json', {'failed_at_utc': now(), 'error_type': type(error).__name__, 'error': str(error), 'no_silent_restart': True})
            raise
    else: raise SystemExit('Choose --check-source or --evaluate CAPTURE')


if __name__ == '__main__': main()
