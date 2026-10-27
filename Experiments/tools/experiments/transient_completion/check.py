#!/usr/bin/env python3
"""Verify archived transient-completion identities and stored decisions.

Standard library only: no PCM decoding, feature extraction, model synthesis,
compilation or execution of the archived experiment sources.
"""
from pathlib import Path
import argparse
import collections
import hashlib
import importlib.util
import json
import math
import sys
import textwrap

PACKAGE = Path(__file__).resolve().parent
ROOT = PACKAGE.parents[2]
spec = importlib.util.spec_from_file_location(
    'transient_archive_reader', ROOT/'tools/experiments/body_radiation_basis/check.py')
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
require = reader.require
PILOT = {f'{note}v{layer}' for note in ('C3', 'C4', 'C6') for layer in (4, 12)}
METRIC_SHA = '14fc804b80f3742ee6c95cc3908c498459a77e61c90a1bdfe4b6c23c8580c1cd'
GATE_SHA = '3e79de5cc8cff0470711fe6b54bed880e753ed34aa7060941fb07031cd216f40'
FILTER_SHA = '8859dbbebac6e54fe1a5e4c93dfb420b1fc91f0ef51f204ae2ebb8c93d5616cd'
MODEL_SHA = '5c8c92f8a761b46a66f3823765f6348ab0c08b74457d7efc062f0941ab07faf8'
CALIBRATION_SHA = '619d6bf4d3200a6b55007a1abcc0658e76a14124ce5f3abad9f5f4b94d8979f7'


def close(a, b):
    return math.isclose(a, b, rel_tol=128*sys.float_info.epsilon,
                        abs_tol=128*sys.float_info.epsilon)


def same_values(actual, expected, label):
    if isinstance(expected, dict):
        require(isinstance(actual, dict) and actual.keys() == expected.keys(), label)
        for key, value in expected.items(): same_values(actual[key], value, label+'.'+key)
    elif isinstance(expected, list):
        require(isinstance(actual, list) and len(actual) == len(expected), label)
        for i, value in enumerate(expected): same_values(actual[i], value, label+f'[{i}]')
    elif isinstance(expected, float):
        require(close(actual, expected), label)
    else:
        require(actual == expected, label)


def identities(archive, value):
    if isinstance(value, dict):
        if isinstance(value.get('path'), str) and isinstance(value.get('sha256'), str):
            archive.identity(value['path'], value['sha256'])
        for child in value.values(): identities(archive, child)
    elif isinstance(value, list):
        for child in value: identities(archive, child)


def source_bytes(archive, protocol, name):
    records = [r for r in protocol['sources'] if Path(r['path']).name == name]
    require(len(records) == 1, 'Unique frozen source '+name)
    record = records[0]
    return archive.resolve(record['path'], record['sha256'])


def original_gates(old, candidate, ident, proof):
    """Independent arithmetic equivalent to the SHA-bound original gate block."""
    base = old['baseline']; floor = old['reference']['sustain_power']*1e-10
    power_db = lambda x, y: 10*math.log10(max(x, floor)/max(y, floor))
    first = max(0., base['early'][0]['broad_signed_error_db']) - max(0., candidate['early'][0]['broad_signed_error_db'])
    ring = max(0., base['early'][1]['ring_signed_error_db']) - max(0., candidate['early'][1]['ring_signed_error_db'])
    harmonic = candidate['late_harmonic_MAE_db']-base['late_harmonic_MAE_db']
    envelope = candidate['late_envelope']['MAE_db']-base['late_envelope']['MAE_db']
    drift = 20*math.log10(candidate['sustain_RMS']/base['sustain_RMS'])
    early = [c['five_band_MAE_db']-b['five_band_MAE_db'] for c, b in zip(candidate['early'], base['early'])]
    shifts = {name: {'LR_db': candidate['stereo'][name]['LR_db']-value['LR_db'],
                     'mono_energy_db': power_db(candidate['stereo'][name]['mono_power'], value['mono_power'])}
              for name, value in base['stereo'].items()}
    gates = {'baseline_payload_exact_to_cached_control': True,
             'mechanical_state_force_bit_parity': proof['mechanical_state_bit_parity'] and proof['force_bit_parity'],
             'no_new_faults': proof['new_faults'] == 0,
             'late_harmonic_MAE': harmonic <= .75, 'late_envelope_MAE': envelope <= .75,
             'late_RMS_drift': abs(drift) <= .5,
             'stereo_LR_shift': abs(shifts['sustain']['LR_db']) <= .5,
             'mono_energy_shift': abs(shifts['sustain']['mono_energy_db']) <= .75}
    if ident.startswith('C3'):
        gates.update(C3_first5_excess_reduction=first >= 3., C3_ring5_20_excess_reduction=ring >= 3.)
    else:
        gates['each_early_window_band_MAE'] = max(early) <= 1.
    changes = {'first5_positive_excess_reduction_db': first,
               'ring5_20_positive_excess_reduction_db': ring,
               'late_harmonic_MAE_db': harmonic, 'late_envelope_MAE_db': envelope,
               'late_RMS_db': drift, 'early_window_band_MAE_db': early, 'stereo': shifts}
    return gates, changes


def numerical(case, variant):
    n = case['numeric']; stored = case['numeric_guards']
    require(reader.finite_tree(n) and n['frames'] == 182400, 'Finite numeric trace and frame count')
    require(n['mode_count'] == 17778 and n['board_modes'] == 475
            and n.get('strings', n.get('string_count')) == 230, 'Original full mode counts')
    require(n['force_contract_errors'] == n['force_proof_mismatches'] == n['nonfinite'] == 0,
            'Finite authenticated force trace')
    require(n['max_positive_scale_energy'] == 0 and n['max_free_energy_ratio'] <= 1,
            'Recorded paired scaling/free energy contraction')
    require(n['retirements'] >= 1, 'Companion retirement recorded')
    if variant == 'v1':
        require(n['control_nonidentical_samples'] == n['board_nonidentical_samples'] == 0
                and n['control_max_error'] == n['board_max_error'] == 0, 'Full rho1 replay parity')
        require(n['control_faults'] == n['companion_faults'] == 0, 'No source/control companion faults')
        require(n['max_pressure_over_bound'] <= 1 and n['discarded_pressure_bound'] <= 1e-20,
                'Crad bound/retirement')
        require(stored['baseline_HP_payload'] is True, 'Recorded baseline HP payload equality')
    else:
        require(n['faults'] == 0 and n['max_zero_force_pressure_over_bound'] <= 1,
                'Full pressure bound/no faults')
        bound = n.get('discarded_future_bound', n.get('discarded_future_pressure_bound'))
        require(bound <= 1e-20, 'Full pressure retirement bound')
        if variant == 'v2':
            require(n['rad_nonidentical_samples_before_v1_retirement'] == 0
                    and n['rad_post_v1_bound_errors'] == 0, 'Crad prefix and discarded-bound compatibility')
            require(stored['baseline_HP_exact'] is True, 'Recorded baseline HP payload equality')
            require(all(case['v1_control'][k] is True for k in ('rawOld_bitexact', 'rawBoard_bitexact', 'HP_payload_exact')),
                    'Inherited rho1 compatibility scope')
        elif 'uniform_control_prefix_frames' in n:
            require(n['uniform_control_prefix_frames'] > 12000
                    and n['uniform_full_pressure_nonidentical_samples'] == 0
                    and n['uniform_full_pressure_max_error'] == n['uniform_control_faults'] == 0,
                    'Same scaler with uniform100 prefix control')
        else:
            require(n['new_uniform_prefix_control_run'] is False and n['new_rho1_control_run'] is False,
                    'New confirmation cases do not claim new implementation controls')
    require(all(value is True for value in stored.values()), 'All recorded numeric guards pass')


def filter_checks(value):
    k = math.tan(math.pi*200/48000); pole = (1-k)/(1+k); b = 1/(1+k)
    require(value['cutoff_hz'] == 200 and close(value['pole'], pole) and close(value['b'], b), 'Fixed HP200 coefficients')
    require(value['stable'] is True and 0 < value['pole'] < 1
            and value['algebraic_DC_gain'] == 0 and abs(value['algebraic_Nyquist_gain']-1) < 1e-14,
            'HP200 DC/Nyquist/stability')
    require(value['measured_DC_tail_max'] < 1e-12 and value['measured_Nyquist_tail_max_error'] < 1e-12,
            'Recorded synthetic filter tails')
    require(all(value[k] is True for k in ('chunk_output_bitidentity', 'chunk_state_bitidentity',
                                         'zero_counter_baseline_identity', 'pass')), 'Synthetic filter decisions')


def observer_checks(value):
    require(value['retired'] is True and value.get('wake_identity', value.get('wake_coordinate_identity')) is True,
            'Synthetic retire/later-force wake')
    require(value['max_free_energy_ratio'] <= 1, 'Synthetic free energy')
    bound = value.get('discarded_future_bound', value.get('discarded_future_pressure_bound', value.get('discarded_pressure_bound')))
    require(bound <= 1e-20, 'Synthetic retirement bound')
    require(value.get('max_zero_force_pressure_over_bound', value.get('max_pressure_over_bound')) <= 1,
            'Synthetic pressure bound')
    for key in ('faults', 'control_faults', 'companion_faults', 'max_scale_energy_increase'):
        if key in value: require(value[key] == 0, 'Synthetic '+key)


def gamma_fields(value):
    require(len(value['key_fields']) == 88 and [k['note'] for k in value['key_fields']] == list(range(21, 109)),
            'All88 prepared key fields')
    reference = value['f0_reference_C3']; require(reference > 0, 'Positive prepared C3 frequency')
    require(all(v > 0 for v in value['K_LR']) and len(value['K_LR']) == 2, 'Finite positive pressure norms')
    require(value['M_frobenius'] > 0 and value['M_inverse_frobenius'] > 0, 'Cold bridge bounds')
    keys = {k['note']: k for k in value['key_fields']}
    for key in keys.values():
        gamma = 100*max(1., key['f0']/reference)
        require(close(key.get('pitch_gamma', key.get('gamma')), gamma), 'Global key pitch law')
        if 'rho' in key: require(close(key['rho'], math.exp(-gamma/48000)), 'Paired key rho')
    if 'string_fields' not in value:
        require(value['body_gamma'] == 100, 'Fixed gamma100 board')
        return
    require(value['minimum_gamma'] == 100 and value['modal_corner_hz'] == 1000, 'One modal law')
    strings = value['string_fields']; board = value['board_fields']
    require(len(strings) == 230 and sum(len(s['modes']) for s in strings) == 17778 and len(board) == 475,
            'All prepared string/board modal fields')
    for i, string in enumerate(strings):
        require(string['index'] == i and string['note'] in keys, 'Prepared string identity')
        for j, mode in enumerate(string['modes']):
            gamma = 100*max(1., keys[string['note']]['f0']/reference, mode['frequency_hz']/1000)
            require(mode['index'] == j and mode['frequency_hz'] > 0 and close(mode['gamma'], gamma)
                    and close(mode['rho'], math.exp(-gamma/48000)), 'Global per-mode string law')
    for i, mode in enumerate(board):
        gamma = 100*max(1., mode['frequency_hz']/1000)
        require(mode['index'] == i and mode['frequency_hz'] > 0 and close(mode['gamma'], gamma)
                and close(mode['rho'], math.exp(-gamma/48000)), 'Global board modal law')


def verify(index):
    archive = reader.Archive(index)
    archive.by_hash(MODEL_SHA); archive.by_hash(CALIBRATION_SHA)
    metric = archive.by_hash(METRIC_SHA).decode()
    start = "        base=old['baseline'];floor=old['reference']['sustain_power']*1e-10\n"
    end = '        optional=None\n'
    require(metric.count(start) == 1, 'Unique original gate block')
    begin = metric.index(start); finish = metric.index(end, begin)
    require(hashlib.sha256(textwrap.dedent(metric[begin:finish]).encode()).hexdigest() == GATE_SHA,
            'Exact original gate arithmetic SHA')
    pilot_refs = {c['id']: c for c in archive.role('reference_control_pilot')['cases']}
    full_refs = {c['id']: c for c in archive.role('reference_control_train34')['cases']}
    variants = index['variants']; completed = {}; protocols = {}; summaries = []; total_cases = 0; numeric_cases = 0
    required = {'v1', 'v2', 'lf_protected_v1', 'pitch_scaled_v1', 'train34', 'modal_scaled_v1'}
    prefixes = {v.get('role_prefix', v['id'].replace('-', '_')) for v in variants}
    require(required <= prefixes, 'All completed predecessor variants retained')
    for variant in variants:
        prefix = variant.get('role_prefix', variant['id'].replace('-', '_'))
        role = lambda suffix: archive.role(prefix+'_'+suffix)
        p = role('protocol'); frozen = role('freeze'); result = role('result'); manifest = role('manifest')
        require(frozen['protocol'] == result['protocol'] == index['roles'][prefix+'_protocol'], 'Frozen protocol/result binding')
        require(frozen['sources'] == p['sources'] and p['gate_arithmetic_sha256'] == GATE_SHA, 'Frozen source/gate identities')
        identities(archive, p); identities(archive, frozen); identities(archive, result)
        for source in p['sources']: archive.resolve(source['path'], source['sha256'])
        if any(Path(s['path']).name == 'filter.cpp' for s in p['sources']):
            require(reader.digest(source_bytes(archive, p, 'filter.cpp')) == FILTER_SHA, 'Unchanged shared HP200 source')
        if any(Path(s['path']).name == 'mechanics_v2_prefix.h' for s in p['sources']):
            full = source_bytes(archive, protocols['v2'], 'replay.cpp')
            require(source_bytes(archive, p, 'mechanics_v2_prefix.h')
                    == full.split(b'\nint main(int argc,char** argv) {')[0]+b'\n', 'Exact full-pressure mechanics prefix')
        if any(Path(s['path']).name == 'pitch_helpers.h' for s in p['sources']):
            full = source_bytes(archive, protocols['pitch_scaled_v1'], 'replay.cpp')
            require(source_bytes(archive, p, 'pitch_helpers.h')
                    == full.split(b'\nint main(int argc,char** argv) {')[0]+b'\n', 'Exact pitch companion helper prefix')
        if any(Path(s['path']).name == 'modal_helpers.h' for s in p['sources']):
            full = source_bytes(archive, protocols['modal_scaled_v1'], 'replay.cpp')
            require(source_bytes(archive, p, 'modal_helpers.h')
                    == full.split(b'\nint main(int argc,char** argv) {')[0]+b'\n', 'Exact modal companion helper prefix')
        for relative, record in manifest.items():
            archive.identity(variant['archived_root']+'/'+relative, record['sha256'], record['bytes'])
        require(p['adopted'] is False and result['adopted'] is False and result['fit_runs'] == 0,
                'No runtime adoption or fitting')
        require(result['new_reference_PCM_access'] is False, 'No new reference PCM in experiment')
        for synthetic in ('filter_synthetic', 'pitch_synthetic', 'synthetic'):
            if synthetic in result:
                value = result[synthetic]
                (filter_checks if 'cutoff_hz' in value else observer_checks)(value)
        if 'cold_bound_gamma' in result: gamma_fields(result['cold_bound_gamma'])
        cases = result['cases']; expected = variant['expected_cases']
        require(len(cases) == result['case_count'] == expected and len({c['id'] for c in cases}) == expected,
                'Complete unique outcome inventory')
        specs = {c['id']: c for c in p['cases']}; require(set(specs) == {c['id'] for c in cases}, 'Protocol/outcome inventory')
        refs = full_refs if expected == 34 else pilot_refs
        require(set(specs) == (set(full_refs) if expected == 34 else PILOT), 'All expectedTRAIN identities')
        failures = collections.Counter(); passing = 0
        for case in cases:
            ident = case['id']; old = refs[ident]; features = case['candidate']; source = specs[ident]
            require(features['fixed_gain'] == source['fixed_gain'] == old['baseline']['fixed_gain']
                    and features['fixed_onset_frame'] == source['fixed_onset_frame'] == old['baseline']['fixed_onset_frame'],
                    'Fixed old gain/onset')
            require(features['late_envelope']['times_seconds'] == old['reference']['late_envelope']['times_seconds']
                    and features['late_envelope']['included'] == old['reference']['late_envelope']['included'],
                    'Frozen reference envelope times/masks')
            require(case['source_proof'] == source['source_proof'], 'Inherited source proof unchanged')
            gates, changes = original_gates(old, features, ident, case['source_proof'])
            require(gates == case['gates'] and all(gates.values()) is case['passes_all_case_gates'], 'Stored original gates')
            same_values(case['changes'], changes, prefix+'.'+ident+'.changes')
            if 'numeric' in case:
                numerical(case, prefix); numeric_cases += 1
            else:
                require(prefix == 'lf_protected_v1', 'Unexpected missing numeric trace')
                original = next(c for c in completed['v2']['cases'] if c['id'] == ident)
                stored = reader.json_data(archive.resolve(source['full_numeric']['path'], source['full_numeric']['sha256']))
                require(stored == original['numeric'] and all(source['full_numerical_proof'].values()),
                        'HP200 source has retained full-pressure numerical proof')
            if 'postprocessor' in case:
                post = case['postprocessor']
                require(post.get('partition_bytes_exact', post.get('partitions_byte_identical')) is True
                        and post['baseline_HP_payload_exact'] is True, 'Recorded partition/baseline payload proof')
                if 'finite' in post: require(post['finite'] is True, 'Finite recorded postprocessor')
            if expected == 34:
                support = source['support']
                require(support == old['support'] and case.get('support', support) == support, 'Frozen complete support')
                require([h['window_seconds'] for h in features['late_harmonics']] == support['late_windows_seconds'],
                        'Actual complete late windows')
                if ident == 'C8v4':
                    require(support['right_censored'] is True and support['late_windows_seconds'] == [[.25, .75], [.75, 1.5], [1.5, 2.5]]
                            and support['omitted_incomplete_late_windows_seconds'] == [[2.5, 3.5]]
                            and max(support['late_envelope_times_seconds']) < 2.801, 'Short C8v4 remains right censored')
            outcome_path = str(Path(case['candidate_audio']['path']).with_name('result.json'))
            outcome_sha = next((r['sha256'] for relative, r in manifest.items()
                                if variant['archived_root']+'/'+relative == outcome_path), None)
            if outcome_sha:
                require(reader.json_data(archive.resolve(outcome_path, outcome_sha)) == case, 'Per-case/full outcome equality')
            require(case['adopted'] is False and reader.finite_tree(case), 'Finite evidence/no adoption')
            for name, passed in gates.items():
                if not passed: failures[name] += 1
            passing += int(all(gates.values()))
        require(passing == result['cases_passing_all_original_gates'] == variant['expected_pass_count'], 'Stored pass count')
        require(result['passes_all_original_gates'] is (passing == expected), 'Global acoustic decision')
        if expected == 34:
            default_reuse = 'modal_scaled_v1' if 'modal' in prefix else 'pitch_scaled_v1'
            reuse = variant.get('reuses_variant', default_reuse).replace('-', '_')
            require(reuse in completed, 'Pilot precedes confirmation')
            pilot_cases = {c['id']: c for c in completed[reuse]['cases']}
            require(set(variant.get('reused_case_ids', PILOT)) == PILOT, 'Exactly six pilot reuse identities')
            require(all(c == pilot_cases[c['id']] for c in cases if c['id'] in PILOT), 'Six exact outcome objects reused')
            require(result['exact_pilot_outcomes_reused'] == 6 and result['new_cases'] == 28
                    and result['new_rho1_replays'] == result['new_uniform_prefix_replays'] == 0, 'Honest confirmation control scope')
            require(result['cold_bound_gamma'] == completed[reuse]['cold_bound_gamma'], 'Prepared all-mode law/bound unchanged')
        completed[prefix] = result; protocols[prefix] = p; total_cases += expected
        summaries.append({'variant': prefix, 'cases': expected, 'preservation_pass_count': passing,
                          'preservation_fail_count': expected-passing, 'failed_gate_counts': dict(failures)})
    return {'verification_passed': True, 'published_records_verified': archive.checked,
            'stored_original_gate_cases_verified': total_cases, 'numeric_case_predicates_checked': numeric_cases,
            'variants': summaries, 'audio_decoded': False, 'DSP_or_feature_extraction_run': False,
            'adopted': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = verify(reader.json_data((PACKAGE/'index.json').read_bytes()))
    if args.output:
        require(not args.output.exists(), 'New output path required')
        args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__': main()
