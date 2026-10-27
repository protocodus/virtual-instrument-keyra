#!/usr/bin/env python3
"""Read-only post-run audit; no model rendering, fitting, or reference PCM."""
from pathlib import Path
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import datetime, hashlib, importlib.util, json, math, time
import numpy as np
from scipy.io import wavfile

ROOT=Path('/workspace/virtual-instrument-keyra')
OUT=Path(__file__).resolve().parent
TRAIN=ROOT/'out/full-transient-completion/modal-train34'
PILOT=TRAIN.parent/'modal-scaled-v1'
def read(p): return json.loads(Path(p).read_text())
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(4*1024*1024), b''): h.update(chunk)
    return h.hexdigest()
def module(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def identity(p): return {'path':str(p),'sha256':digest(p)}

start=time.monotonic();result=read(TRAIN/'result.json');p=read(TRAIN/'protocol.json');pilot=read(PILOT/'result.json');pp=read(PILOT/'protocol.json')
assert len(result['cases'])==34 and len({x['id'] for x in result['cases']})==34
assert {x['id'] for x in result['cases']}=={x['id'] for x in p['cases']}
checked={};manifest_count=0
def verify_record(r):
    path=Path(r['path']);expected=r['sha256']
    if path not in checked: checked[path]=digest(path)
    assert checked[path]==expected, str(path)
def collect(obj):
    if isinstance(obj,dict):
        if isinstance(obj.get('path'),str) and isinstance(obj.get('sha256'),str):verify_record(obj)
        for value in obj.values():collect(value)
    elif isinstance(obj,list):
        for value in obj:collect(value)
for d in (TRAIN,PILOT):
    for n in ('protocol.json','freeze.json','producer-freeze.json','result.json'):
        collect(read(d/n))
    for name,r in read(d/'manifest.json').items():
        path=d/name;verify_record({'path':str(path),'sha256':r['sha256']});assert path.stat().st_size==r['bytes'];manifest_count+=1
assert (TRAIN/'modal_helpers.h').read_bytes()==(PILOT/'replay.cpp').read_bytes().split(b'\nint main(int argc,char** argv) {')[0]+b'\n'
assert (TRAIN/'filter.cpp').read_bytes()==(PILOT/'filter.cpp').read_bytes()
assert digest(TRAIN/'renders/bound-and-gamma.json')==digest(PILOT/'renders/bound-and-gamma.json')
metric_path=ROOT/'tools/probe_full_causal_radiation_metrics.py'
assert digest(metric_path)=='14fc804b80f3742ee6c95cc3908c498459a77e61c90a1bdfe4b6c23c8580c1cd'
metric=module(metric_path,'audit_metric')
operator=module(ROOT/'out/full-radiation-crossover/v1/postprocess.py','audit_operator')
gate,gate_sha=operator.gate_function(metric,metric_path.read_text())
assert gate_sha==p['gate_arithmetic_sha256']==pp['gate_arithmetic_sha256']
helper_path=ROOT/'out/full-radiation-crossover/train34/measure_references.py'
assert digest(helper_path)=='45b38bc157afdff800c1c2f9c6090d4c51225acb058f5057f214808d0a74e3b6'
helper=module(helper_path,'audit_complete_window_helper')
refs={x['id']:x for x in read(ROOT/'out/full-radiation-crossover/train34/reference-control.json')['cases']}
rows={x['id']:x for x in read(ROOT/'References/GrandFullRange/combined_train_features.json')['samples']}
cases={x['id']:x for x in p['cases']};six={x['id']:x for x in pilot['cases']}
audit_rows=[];failures=[];numeric_pass=0;feature_exact=0
for c in result['cases']:
    ident=c['id'];spec=cases[ident];ref=refs[ident]
    if ident in six:assert c==six[ident]
    assert spec['fixed_gain']==ref['baseline']['fixed_gain'] and spec['fixed_onset_frame']==ref['baseline']['fixed_onset_frame']
    sr,x=wavfile.read(c['candidate_audio']['path']);assert sr==48000 and x.dtype==np.float32 and x.shape==(182400,2) and np.isfinite(x).all()
    if ident in six:
        features=metric.observation_features(x.astype(float),spec['fixed_onset_frame'],spec['fixed_gain'],ref['reference'],rows[ident])
    else:
        features=helper.observation_features(metric,x.astype(float),spec['fixed_onset_frame'],spec['fixed_gain'],ref['reference'],rows[ident],spec['support'])
    assert features==c['candidate'], 'Feature rescore differs '+ident
    feature_exact+=1
    computed=gate(ref,features,ident,True,{ident:c['source_proof']})
    for k in ('changes','gates','passes_all_case_gates'):assert computed[k]==c[k], 'Gate rescore differs '+ident
    # Reconstruct numerical predicates independently from actual logged values.
    n=c['numeric']
    numerical=(n['force_contract_errors']==0 and n['force_proof_mismatches']==0 and n['nonfinite']==0 and n['faults']==0 and n['max_positive_scale_energy']==0 and n['max_free_energy_ratio']<=1 and n['max_zero_force_pressure_over_bound']<=1 and n['retirements']>=1 and n['discarded_future_bound']<=1e-20 and n['mode_count']==17778 and n['strings']==230 and n['board_modes']==475)
    if ident in six:
        numerical=numerical and n['uniform_full_pressure_nonidentical_samples']==0 and n['uniform_full_pressure_max_error']==0 and n['uniform_control_faults']==0
    else:
        numerical=numerical and n['new_uniform_prefix_control_run'] is False and n['new_rho1_control_run'] is False
    assert numerical and all(c['numeric_guards'].values())
    numeric_pass+=1
    assert c['postprocessor']['partition_bytes_exact'] and c['postprocessor']['baseline_HP_payload_exact']
    support=spec['support'];assert c.get('support',support)==support
    expected_late=[[.25,.75],[.75,1.5],[1.5,2.5]]+([] if ident=='C8v4' else [[2.5,3.5]])
    assert support['late_windows_seconds']==expected_late
    assert bool(support['right_censored'])==(ident=='C8v4')
    if ident=='C8v4':
        assert support['omitted_incomplete_late_windows_seconds']==[[2.5,3.5]]
        assert max(support['late_envelope_times_seconds'])<2.801
    assert [h['window_seconds'] for h in features['late_harmonics']]==expected_late
    bad=[k for k,v in computed['gates'].items() if not v]
    record={'id':ident,'passes_all_case_gates':not bad,'failed_gates':bad,'late_harmonic_MAE_delta_db':computed['changes']['late_harmonic_MAE_db'],'late_envelope_MAE_delta_db':computed['changes']['late_envelope_MAE_db'],'late_RMS_drift_db':computed['changes']['late_RMS_db'],'sustain_LR_shift_db':computed['changes']['stereo']['sustain']['LR_db'],'sustain_mono_shift_db':computed['changes']['stereo']['sustain']['mono_energy_db'],'max_early_band_MAE_delta_db':max(computed['changes']['early_window_band_MAE_db'])}
    audit_rows.append(record)
    if bad:failures.append(record)
assert len(failures)==1 and failures[0]['id']=='C8v12' and failures[0]['failed_gates']==['each_early_window_band_MAE']
assert sum(c['passes_all_case_gates'] for c in result['cases'])==33==result['cases_passing_all_original_gates'] and result['passes_all_original_gates'] is False
for c in result['cases']:
    assert all(c['gates'][k] for k in ('late_harmonic_MAE','late_envelope_MAE','late_RMS_drift','stereo_LR_shift','mono_energy_shift'))
c=next(x for x in result['cases'] if x['id']=='C8v12');base=refs['C8v12']['baseline'];cand=c['candidate']
receipt={'schema_version':1,'reviewed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer':'Independent /root/transient_audit, read-only modal post-run','decision':'Numerical/evidence audit passes; acoustic global candidate FAIL,33/34. No adoption authorized.',
 'inputs':{'result':identity(TRAIN/'result.json'),'protocol':identity(TRAIN/'protocol.json'),'manifest':identity(TRAIN/'manifest.json'),'pilot_result':identity(PILOT/'result.json'),'metric':identity(metric_path),'complete_window_helper':identity(helper_path),'audit_source':identity(Path(__file__))},
 'checks':{'unique_path_hashes_verified':len(checked),'manifest_entries_verified':manifest_count,'all34_float32_features_recomputed_exact':feature_exact,'all34_original_gate_changes_and_flags_recomputed_exact':True,'numerical_guards_independently_reconstructed':numeric_pass,'six_pilot_outcome_objects_reused_verbatim':6,'source_helper_prefix_exact':True,'filter_source_exact':True,'all88_and_modal_prepared_gamma_and_bound_JSON_exact':True,'actual_canonical_alternate_filter_partition_checks_recorded_pass_all34':True,'C8v4_right_censoring_complete_windows_only':True,'all_late_and_sustain_stereo_guards_pass_all34':True,'new_model_renders':0,'new_reference_PCM_access':False},
 'case_count':34,'passes_all_original_gates':False,'pass_count':33,'failures':failures,'C8v12_detail':{'window_seconds':[.005,.020],'baseline_five_band_MAE_db':base['early'][1]['five_band_MAE_db'],'candidate_five_band_MAE_db':cand['early'][1]['five_band_MAE_db'],'delta_db':c['changes']['early_window_band_MAE_db'][1],'maximum_allowed_delta_db':1.,'baseline_signed_band_errors_db':base['early'][1]['band_signed_errors_db'],'candidate_signed_band_errors_db':cand['early'][1]['band_signed_errors_db'],'whole_note_stereo_diagnostics_not_gated':c['changes']['stereo']['whole_note']},
 'cases':audit_rows,'wall_seconds':time.monotonic()-start,
 'scope_and_limits':['Already observed34TRAIN cases, six retained exact outcomes plus28 confirmation outputs; not fresh evaluation.','All modal-family features and gates were rescored from emittedfloat32candidate WAVs against frozen derived reference JSON, fixed gains/onsets/masks. No reference recordings decoded.','State/force parity is inherited original collection-time read-only sampled-state/FNV evidence. No source rerender here; FNV does not prove cryptographic collision freedom or every internal-state byte.','The source observer preserves original physical trajectory and uses contact forces only; solved Schur fields authenticate the capture and do not drive the companion.','Separate full17778string/475board copy is an offline quality experiment, not an efficient realtime implementation, measured piano part, or production plugin qualification.','48kHz frozen5-anchor source, humanization/mechanisms0 and repetition controller bypass. Does not qualify current API/mechanical/default integration, other rates, Realtime/Reason/Recon/U45, unseen pianos or hearing.','Original exact gate block constrains sustain L/R and mono. Whole-note and early stereo changes are diagnostics and can be larger. Positive-excess reduction can reward overattenuation; signed errors remain.','Uniformall100 prefix controls exist only for sixpilot cases; no additionalrho1 or per-new28 uniform control is claimed. Original fullrho1 controls were inherited from earlier studies.']}
dest=OUT/'independent-current-review.json'
if dest.exists():raise RuntimeError('Audit receipt already exists')
dest.write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
print(json.dumps({'receipt':identity(dest),'decision':receipt['decision'],'checks':receipt['checks'],'C8v12_detail':receipt['C8v12_detail'],'wall_seconds':receipt['wall_seconds']},indent=2))
