#!/usr/bin/env python3
"""Review the failed six-TRAIN pilot without synthesis or changing its receipts.

The default check uses published JSON/source only (Python standard library).
--verify-captures additionally requires the archived, hash-bound input bundle.
--recompute also needs NumPy/SciPy and repeats the frozen numerical observations.
No mode fits, renders, retimes, rewrites archived JSON, or promotes a model.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import struct

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT/'tools/experiments/causal_radiation_pilot'
ARCHIVE_ROOT = Path('/workspace/virtual-instrument-keyra')
IDS = ('C3v4','C3v12','C4v4','C4v12','C6v4','C6v12')


def require(condition, message):
    if not condition: raise ValueError(message)


def read(path): return json.loads(Path(path).read_text())
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def close(a, b, label):
    # Receipt arithmetic only; acceptance thresholds below remain exact.
    require(math.isclose(a,b,rel_tol=2e-14,abs_tol=1e-12), 'Stored arithmetic differs: '+label)


def check_arithmetic(protocol, control, pilot):
    require(tuple(c['id'] for c in protocol['cases'])==IDS, 'Protocol inventory changed')
    require(all(c['role']=='train' for c in protocol['cases']), 'Non-TRAIN protocol case')
    require(tuple(c['id'] for c in pilot['cases'])==IDS, 'Result inventory changed')
    require(pilot['default_promoted'] is False and pilot['fit_or_acquisition'] is False, 'Pilot scope changed')
    thresholds=protocol['gates']; expected=[]
    old={c['id']:c for c in control['cases']}
    for case in pilot['cases']:
        ident=case['id']; b=old[ident]['baseline']; c=case['candidate']; d=case['changes']
        first=max(0.,b['early'][0]['broad_signed_error_db'])-max(0.,c['early'][0]['broad_signed_error_db'])
        ring=max(0.,b['early'][1]['ring_signed_error_db'])-max(0.,c['early'][1]['ring_signed_error_db'])
        harmonic=c['late_harmonic_MAE_db']-b['late_harmonic_MAE_db']
        envelope=c['late_envelope']['MAE_db']-b['late_envelope']['MAE_db']
        drift=20*math.log10(c['sustain_RMS']/b['sustain_RMS'])
        changes=[cc['five_band_MAE_db']-bb['five_band_MAE_db'] for bb,cc in zip(b['early'],c['early'])]
        lr=c['stereo']['sustain']['LR_db']-b['stereo']['sustain']['LR_db']
        mono=10*math.log10(c['stereo']['sustain']['mono_power']/b['stereo']['sustain']['mono_power'])
        for key,value in [('first5_positive_excess_reduction_db',first),('ring5_20_positive_excess_reduction_db',ring),
                          ('late_harmonic_MAE_db',harmonic),('late_envelope_MAE_db',envelope),('late_RMS_db',drift)]:
            close(value,d[key],ident+'/'+key)
        for i,value in enumerate(changes): close(value,d['early_window_band_MAE_db'][i],ident+'/early'+str(i))
        close(lr,d['stereo']['sustain']['LR_db'],ident+'/LR')
        close(mono,d['stereo']['sustain']['mono_energy_db'],ident+'/mono')
        require(c['fixed_gain']==b['fixed_gain'] and c['fixed_onset_frame']==b['fixed_onset_frame'], 'Candidate gain/trim changed')
        guards=case['producer_guard_fields']
        gates={'baseline_payload_exact_to_cached_control':case['gates']['baseline_payload_exact_to_cached_control'],
            'mechanical_state_force_bit_parity':guards['mechanical_state_force_bit_parity'],
            'no_new_faults':guards['new_faults']==0,
            'late_harmonic_MAE':harmonic<=thresholds['each_pilot_maximum_late_harmonic_MAE_worsening_db'],
            'late_envelope_MAE':envelope<=thresholds['each_pilot_maximum_late_envelope_MAE_worsening_db'],
            'late_RMS_drift':abs(drift)<=thresholds['each_pilot_maximum_absolute_late_RMS_drift_db'],
            'stereo_LR_shift':abs(lr)<=thresholds['each_pilot_maximum_absolute_stereo_LR_shift_db'],
            'mono_energy_shift':abs(mono)<=thresholds['each_pilot_maximum_absolute_mono_energy_shift_db']}
        if ident.startswith('C3'):
            gates['C3_first5_excess_reduction']=first>=thresholds['C3_each_layer_minimum_first5_positive_excess_reduction_db']
            gates['C3_ring5_20_excess_reduction']=ring>=thresholds['C3_each_layer_minimum_ring5_20_positive_excess_reduction_db']
        else:
            gates['each_early_window_band_MAE']=max(changes)<=thresholds['C4_C6_each_early_window_maximum_band_MAE_worsening_db']
        require(gates==case['gates'], 'Stored gates differ: '+ident)
        passed=all(gates.values()); require(passed is case['passes_all_case_gates'], 'Case decision differs')
        failed=[k for k,v in gates.items() if not v]
        require(failed==(['each_early_window_band_MAE'] if ident.startswith('C6') else []), 'Failure scope changed: '+ident)
        expected.append({'id':ident,'passed':passed,'failed_gates':failed})
    require(sum(c['passed'] for c in expected)==4 and pilot['passes_all_pilot_gates'] is False, 'Frozen global FAIL changed')
    return expected


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify-captures',action='store_true',help='Hash all external input artifacts and inspect state/force rows.')
    parser.add_argument('--recompute',action='store_true',help='Recompute numerical features from exact captured PCM; implies --verify-captures.')
    parser.add_argument('--capture-root',type=Path,help='Root containing archived repository-relative inputs; defaults to this checkout.')
    parser.add_argument('--output',type=Path,help='Write a NEW review receipt. Existing files are refused.')
    args=parser.parse_args()
    require(args.output is None or not args.output.exists(), 'Preserve prior receipts; output already exists')
    index_path=PACKAGE/'review-index.json'; index=read(index_path)
    mapping={}; published=[]
    for item in index['published_artifacts']:
        path=ROOT/item['package_path']; require(sha(path)==item['sha256'], 'Published artifact changed: '+str(path))
        published.append((path,item['sha256']))
        for archived in item.get('archived_paths',[]): mapping[(archived,item['sha256'])]=path
    producer_index_path=ROOT/index['producer_index']['path']
    require(sha(producer_index_path)==index['producer_index']['sha256'], 'Producer source index changed')
    for item in read(producer_index_path)['files']:
        path=ROOT/item['package_path']; require(sha(path)==item['sha256'], 'Frozen producer source changed: '+str(path))
        published.append((path,item['sha256']))
        mapping[(item['original_path'],item['sha256'])]=path
    external_keys={(r['path'],r['sha256']) for r in index['external_input_artifacts']}

    def resolve(record, external=False):
        key=(record['path'],record['sha256'])
        if key in mapping: return mapping[key]
        require(key in external_keys, 'Artifact not declared in published/external inventory: '+record['path'])
        require(external, 'Artifact not published: '+record['path'])
        relative=Path(record['path']).relative_to(ARCHIVE_ROOT)
        path=(args.capture_root or ROOT)/relative
        require(sha(path)==record['sha256'], 'External artifact changed: '+str(path))
        return path

    def load_record(record): return read(resolve(record))

    protocol=read(ROOT/'Validation/full-causal-radiation-pilot-protocol.json')
    pilot=read(ROOT/'Validation/full-causal-radiation-pilot.json')
    control=load_record(pilot['reference_control'])
    cases=check_arithmetic(protocol,control,pilot)
    capture=load_record(pilot['capture_manifest']); producer=load_record(pilot['producer_receipt'])
    original=load_record(capture['metadata_schema_adapter']['original_capture'])
    require(original['cases']==producer['cases'], 'Original capture differs from bound producer')
    for old,new in zip(original['cases'],capture['cases']):
        without_alias={k:v for k,v in new.items() if k!='mechanical_state_force_bit_parity'}
        require(without_alias==old, 'Adapter changed more than its alias')
        require(new['mechanical_state_force_bit_parity'] is (old['mechanical_state_bit_parity'] and old['force_bit_parity']), 'Alias differs')
    freeze=load_record(producer['candidate_freeze']); math_report=load_record(freeze['math_validation'])
    require(math_report['passed'] is True and freeze['binary']==producer['binary'], 'Prototype math/binary binding differs')
    for record in [*protocol['inputs'],*producer['source_inputs'],*freeze['source_inputs']]:
        key=(record['path'],record['sha256'])
        require(key in mapping or key in external_keys, 'Frozen input absent from inventory: '+record['path'])
        if key in mapping: resolve(record)
    times=[protocol['frozen_at_utc'],freeze['frozen_at_utc'],producer['render_started_at_utc']]
    require([datetime.fromisoformat(t) for t in times]==sorted(datetime.fromisoformat(t) for t in times), 'Protocol/prototype/render chronology differs')
    code=load_record(pilot['code_freeze']); opening=load_record(pilot['candidate_opening'])
    require(datetime.fromisoformat(code['frozen_at_utc'])<datetime.fromisoformat(opening['started_at_utc'])<datetime.fromisoformat(pilot['completed_at_utc']), 'Analysis chronology differs')
    fixture=read(ROOT/'Validation/full-causal-radiation-metric-checks.json')
    replay=read(ROOT/'Validation/full-causal-radiation-metric-replay.json')
    require(fixture['passed'] is True and replay['passed'] is True, 'Metric fixture/replay failed')
    require(len(fixture['producer_capture_guards_rejected'])==9 and fixture['producer_capture_guards_rejected']==replay['producer_capture_guards_rejected'], 'Nine negative guards changed')
    require(replay['replay_comparison']['absolute_power_bound']==0. and replay['replay_comparison']['exact_structure_and_nonfloats'] is True, 'Replay comparator changed')
    diag=read(ROOT/'Validation/full-causal-radiation-C6-diagnostic.json')
    require(diag['original_frozen_pilot_passes_all_gates'] is False and diag['frozen_gates_rescored_or_changed'] is False, 'Diagnostic changed the frozen result')
    require(all(c['true_SNR_db'] is None for c in diag['C6_cases']), 'Unmeasured SNR claimed')
    require([c['passes_numerical_diagnostic_gates'] for c in diag['T_half_posthoc_diagnostic_gate_application']]==[True,True,True,True,False,False], 'T*.5 failure changed')
    external_count=0
    if args.verify_captures or args.recompute:
        for record in index['external_input_artifacts']:
            resolve(record,external=True);external_count+=1
        for c in producer['cases']:
            proof=c['parity_proof']
            for kind,count in [('state_rows',714),('force_rows',182400)]:
                data=resolve(proof[kind],external=True).read_bytes()
                require(len(data)==count*24, 'Physical proof row count changed')
                rows=list(struct.iter_unpack('<QQQ',data))
                require(all(before==after for _,before,after in rows), 'Physical hash mismatch')
                require(rows[0][0]==0 and rows[-1][0]==182399, 'Physical proof frame coverage differs')
    numerical=[]; environment={'python':platform.python_version()}
    if args.recompute:
        # Import only after CLI parsing and explicit numerical-replay request.
        import numpy as np
        import scipy
        import probe_full_causal_radiation_metrics as metrics
        from check_causal_radiation_metrics import numeric_identity
        environment.update(numpy=np.__version__,scipy=scipy.__version__)
        required={
            'tools/probe_full_causal_radiation_metrics.py':'14fc804b80f3742ee6c95cc3908c498459a77e61c90a1bdfe4b6c23c8580c1cd',
            'tools/fit_full_calibration.py':'c070b3a9f8f68b1e9aa18c8958d703225e5506ade5943ee1cd5ec0a3e1678550',
            'Research/GrandPianoV2/tools/benchmark.py':'f64c0be9d6ae365bb8dcaa1d36d30a6e531f0778082722f0a58a1a27484e1cda',
            'References/GrandFullRange/combined_train_features.json':'249e5b1b623aea2cc008d4523016a700c83b74ffc0fe9f10b54929f678ad0bc7',
            'References/GrandFullRange/split.json':'a00135a26fb0e9a95e1245d1f29d55c57da332d42510f1efb9adcbca36fd0428'}
        for path,expected in required.items():
            require(mapping.get((str(ARCHIVE_ROOT/path),expected))==(ROOT/path), 'Required metric dependency missing or remapped: '+path)
            require(sha(ROOT/path)==expected, 'Required metric dependency changed: '+path)
        for module in (metrics,metrics.fit,metrics.fit.benchmark,metrics.fit.original,metrics.fit.mechanics_helper):
            path=Path(module.__file__).resolve()
            require(any(path==p and sha(path)==expected for p,expected in published), 'Loaded unpinned metric import: '+str(path))
        training,_=metrics.fit.training_inputs(metrics.fit.DEFAULT_REFERENCE,metrics.fit.DEFAULT_SPLIT)
        training={r['id']:r for r in training}
        controls={r['id']:r for r in control['cases']}
        protocol_cases={r['id']:r for r in protocol['cases']}
        for case in pilot['cases']:
            ident=case['id'];old=controls[ident];pr=protocol_cases[ident]
            rr=resolve(pr['reference_audio'],external=True);sr,ref=metrics.fit.benchmark.load_audio(rr)
            require(sr==48000, 'Reference sample rate changed')
            ro,_=metrics.fit.benchmark.onset_index(ref,sr)
            rf=metrics.reference_features(ref,ro,training[ident])
            witnesses=numeric_identity(rf,old['reference'],ident+'/reference')
            base,bbytes=metrics.load_float(resolve(case['baseline_audio'],external=True))
            _,cached=metrics.load_float(resolve(pr['cached_control_audio'],external=True))
            require(bbytes==cached, 'Baseline PCM is not exact cached control')
            new,_=metrics.load_float(resolve(case['candidate_audio'],external=True))
            for role,raw,stored in [('baseline',base,old['baseline']),('candidate',new,case['candidate'])]:
                value=metrics.observation_features(raw.astype(np.float64),old['baseline']['fixed_onset_frame'],old['baseline']['fixed_gain'],old['reference'],training[ident])
                witnesses+=numeric_identity(value,stored,ident+'/'+role)
            numerical.append({'id':ident,'baseline_float32_payload_exact':True,'floating_roundoff_cells':len(witnesses),
                'numeric_roundoff_witness':witnesses,
                'maximum_absolute_roundoff':max((w['absolute_difference'] for w in witnesses),default=0.),
                'maximum_ULP_distance':max((w['ULP_distance'] for w in witnesses),default=0)})
    for path,expected in published:
        require(sha(path)==expected, 'Published input changed during review: '+str(path))
    require(sha(producer_index_path)==index['producer_index']['sha256'], 'Producer source index changed during review')
    if args.verify_captures or args.recompute:
        for record in index['external_input_artifacts']: resolve(record,external=True)
    report={'schema_version':1,'reviewed_at_utc':datetime.now(timezone.utc).isoformat(),
        'passed':True,'scope':'Published evidence consistency'+('; captured inputs and frozen numerical replay' if args.recompute else '; captured input hashes' if args.verify_captures else ' only; no external audio opened'),
        'review_index_sha256':sha(index_path),'review_tool_sha256':sha(__file__),
        'pilot_passes_all_gates':False,'case_results':cases,'external_artifacts_verified':external_count,
        'external_artifacts_unverified':len(index['external_input_artifacts'])-external_count,
        'environment':environment,'numerical_replay':numerical,'new_synthesis_fit_acquisition_or_default_change':False,
        'limits':['A review/replay pass preserves the failed pilot; it does not establish sound fidelity, physical correctness or fresh generalization.',
            'Supplemental source-path/music files are hash-pinned metadata; this command does not independently replay those separate diagnoses or listening exports.',
            'Physical parity uses finite-width source-produced state/force hashes plus exact baseline PCM, not a collision-free proof.',
            'Original chronology is archived evidence; a later replay cannot recreate first-use chronology.']}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    summary={k:v for k,v in report.items() if k not in ('numerical_replay','limits')}
    summary['numerical_replay']=[{k:v for k,v in case.items() if k!='numeric_roundoff_witness'} for case in numerical]
    summary['full_receipt_output']=None if args.output is None else str(args.output)
    print(json.dumps(summary,indent=2))


if __name__=='__main__':main()
