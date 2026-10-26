#!/usr/bin/env python3
"""Verify stored fixed-400 Hz research evidence with the standard library.

No recording/capture is opened, no filter is run, and no audio is scored.
The six passes are post-hoc TRAIN reuse, not default or listening qualification.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import textwrap

PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parents[2]
IDS=('C3v4','C3v12','C4v4','C4v12','C6v4','C6v12')
GATE_BLOCK_SHA='3e79de5cc8cff0470711fe6b54bed880e753ed34aa7060941fb07031cd216f40'


def require(value,message):
    if not value:raise ValueError(message)


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())


def arithmetic_equal(a,b,path=''):
    """Stored arithmetic roundoff only; no acceptance threshold is relaxed."""
    require(type(a) is type(b),'Stored schema/type differs: '+path)
    if isinstance(a,dict):
        require(a.keys()==b.keys(),'Stored keys differ: '+path)
        for key in a:arithmetic_equal(a[key],b[key],path+'/'+key)
    elif isinstance(a,list):
        require(len(a)==len(b),'Stored length differs: '+path)
        for i,(x,y) in enumerate(zip(a,b)):arithmetic_equal(x,y,path+'/'+str(i))
    elif isinstance(a,float):
        require(math.isfinite(a) and math.isfinite(b),'Nonfinite stored number')
        require(math.isclose(a,b,rel_tol=16*sys.float_info.epsilon,abs_tol=16*sys.float_info.epsilon),'Stored dB arithmetic differs: '+path)
    else:require(a==b,'Stored value differs: '+path)


def original_gate_function(source):
    # Reuse exactly the SHA-bound original predicates and thresholds. This
    # operates on archived numeric features, not PCM or new feature estimates.
    start="        base=old['baseline'];floor=old['reference']['sustain_power']*1e-10\n"
    end='        optional=None\n'
    require(source.count(start)==1,'Original gate block start is not unique')
    begin=source.index(start);finish=source.index(end,begin)
    block=textwrap.dedent(source[begin:finish])
    require(hashlib.sha256(block.encode()).hexdigest()==GATE_BLOCK_SHA,'Original gate arithmetic changed')
    tail="return {'changes':{'first5_positive_excess_reduction_db':first_b-first_c,'ring5_20_positive_excess_reduction_db':ring_b-ring_c,'late_harmonic_MAE_db':harmonic,'late_envelope_MAE_db':envelope,'late_RMS_db':drift,'early_window_band_MAE_db':window_changes,'stereo':shifts},'gates':gates,'passes_all_case_gates':all(gates.values())}\n"
    body='def stored_gates(old,candidate,ident,baseline_exact,proof):\n'+textwrap.indent(block+tail,'    ')
    def power_db(p,q,floor):return 10*math.log10(max(p,floor)/max(q,floor))
    namespace={'math':math,'power_db':power_db}
    exec(compile(body,'sha-bound-original-stored-gates','exec'),namespace)
    return namespace['stored_gates']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,help='Write a NEW evidence-review receipt; existing files are refused.')
    args=parser.parse_args()
    require(args.output is None or not args.output.exists(),'Preserve prior receipts; output exists')
    index_path=PACKAGE/'index.json';index=read(index_path);index_sha=sha(index_path)
    published=[];mapping={}
    for row in index['published_artifacts']:
        path=ROOT/row['package_path'];require(sha(path)==row['sha256'],'Published input changed: '+str(path))
        published.append((path,row['sha256']))
        for old in row.get('archived_paths',[]):mapping[(old,row['sha256'])]=path
    def bound(record):
        path=mapping.get((record['path'],record['sha256']))
        require(path is not None,'Archived metadata/source dependency not published: '+record['path'])
        return path
    def load(record):return read(bound(record))
    upstream=read(ROOT/index['upstream_source_index']['path'])
    require(sha(ROOT/index['upstream_source_index']['path'])==index['upstream_source_index']['sha256'],'Original public source index changed')
    for row in upstream['files']:
        path=ROOT/row['package_path'];require(sha(path)==row['sha256'],'Original source archive changed: '+str(path))
        published.append((path,row['sha256']))

    result=read(ROOT/'Validation/full-radiation-crossover.json')
    protocol=load(result['protocol']);freeze=load(result['freeze']);opening=load(result['opening'])
    control=load(result['reference_control']);old_result=load(protocol['original_causal_pilot_result'])
    old_protocol=load(protocol['original_protocol']);producer=load(protocol['upstream_producer'])
    capture=load(protocol['upstream_capture'])
    source=bound(freeze['postprocessor_source']);metric_source=bound(result['original_metric_tool'])
    require(sha(source)=='636dc354c5eb475757bbf8f0a1195d7b40782dd5a72969af0127beaccdb51a3e','Frozen crossover source changed')
    require(sha(metric_source)=='14fc804b80f3742ee6c95cc3908c498459a77e61c90a1bdfe4b6c23c8580c1cd','Frozen metric changed')
    require(protocol['unchanged_original_gates']==old_protocol['gates'],'Original thresholds changed')
    require(protocol['unchanged_original_analysis']==old_protocol['analysis'],'Original analysis changed')
    require(protocol['prior_causal_pilot_results_observed'] is True,'Post-hoc role lost')
    require(protocol['cutoff_hz']==400. and protocol['sample_rate']==48000,'Fixed filter changed')
    require(protocol['processing']['frames_each']==182400,'Capture frame count changed')
    require(protocol['processing']['cutoff_variants']==1 and protocol['processing']['tuning_sweep'] is False,'Single fixed variant scope changed')
    require(result['default_promoted'] is False and result['recording_fit_or_acquisition'] is False,'Scope changed')
    require(result['full_DSP_renders']==0 and result['candidate_cutoff_variants']==1,'Run scope changed')
    require(result['gain_or_onset_changes'] is False and result['gate_changes'] is False and result['rescore_after_failure'] is False,'Frozen scoring controls changed')
    require(tuple(c['id'] for c in result['cases'])==IDS,'Six-case inventory changed')
    require(tuple(c['id'] for c in protocol['cases'])==IDS,'Protocol inventory changed')
    require(old_result['passes_all_pilot_gates'] is False and sum(c['passes_all_case_gates'] for c in old_result['cases'])==4,'Original failed pilot changed')
    times=[protocol['frozen_at_utc'],freeze['frozen_at_utc'],opening['started_at_utc'],result['completed_at_utc']]
    values=[datetime.fromisoformat(t) for t in times]
    require(values==sorted(values) and len(set(values))==4,'Archived protocol/source/opening/result chronology differs')
    require(freeze['protocol']==result['protocol'],'Freeze protocol binding differs')
    require(opening['freeze']==result['freeze'],'Opening freeze binding differs')
    proofs={c['id']:c for c in producer['cases']};olds={c['id']:c for c in control['cases']}
    prior={c['id']:c for c in old_result['cases']};requested={c['id']:c for c in protocol['cases']}
    capture_cases={c['id']:c for c in capture['cases']}
    gate=original_gate_function(metric_source.read_text())
    for case in result['cases']:
        ident=case['id'];old=olds[ident];request=requested[ident];proof=proofs[ident]
        for new_role,old_role in [('old_audio','baseline'),('causal_audio','candidate')]:
            actual={k:case[new_role][k] for k in ('path','sha256')}
            require(actual==request[new_role]==proof[old_role]==capture_cases[ident][old_role],'Source-pair descriptor differs: '+ident)
        require(case['candidate']['fixed_gain']==old['baseline']['fixed_gain']==request['fixed_old_gain'],'Old gain changed')
        require(case['candidate']['fixed_onset_frame']==old['baseline']['fixed_onset_frame']==request['fixed_old_onset_frame'],'Old onset changed')
        require(case['postprocessor_contract']['partitions_byte_identical'] is True,'Partition claim failed')
        require(case['postprocessor_contract']['finite_output_and_final_state'] is True,'Finite-output claim failed')
        lineage=case['upstream_state_force_lineage']
        require(lineage['producer_case']==ident and all(lineage[k]==proof[k] for k in ('mechanical_state_bit_parity','force_bit_parity','new_faults')),'Inherited physical proof claim differs')
        expected=gate(old,case['candidate'],ident,True,proofs)
        arithmetic_equal(expected['changes'],case['changes'],ident+'/changes')
        require(expected['gates']==case['gates'] and all(case['gates'].values()),'Stored original gates differ: '+ident)
        require(expected['passes_all_case_gates'] is case['passes_all_case_gates'] is True,'Case decision differs')
        require(proof['baseline_float32_payload_identical_to_cached_control'] is True,'Original payload guard failed')
    require(result['passes_all_unchanged_pilot_gates'] is True,'Six-case numerical result changed')
    margins=read(ROOT/'Validation/full-radiation-crossover-margins.json')
    require(margins['result']['sha256']==sha(ROOT/'Validation/full-radiation-crossover.json'),'Margins result binding differs')
    bycase={c['id']:c for c in result['cases']}
    limits=old_protocol['gates']
    require(tuple(c['id'] for c in margins['minimum_gate_margins'])==IDS,'Margin inventory changed')
    for table in margins['minimum_gate_margins']:
        ident=table['id'];case=bycase[ident];d=case['changes']
        values={
            'late_harmonic_MAE_db':limits['each_pilot_maximum_late_harmonic_MAE_worsening_db']-d['late_harmonic_MAE_db'],
            'late_envelope_MAE_db':limits['each_pilot_maximum_late_envelope_MAE_worsening_db']-d['late_envelope_MAE_db'],
            'late_RMS_drift_db':limits['each_pilot_maximum_absolute_late_RMS_drift_db']-abs(d['late_RMS_db']),
            'stereo_LR_shift_db':limits['each_pilot_maximum_absolute_stereo_LR_shift_db']-abs(d['stereo']['sustain']['LR_db']),
            'mono_energy_shift_db':limits['each_pilot_maximum_absolute_mono_energy_shift_db']-abs(d['stereo']['sustain']['mono_energy_db'])}
        if ident.startswith('C3'):
            values['C3_first5_excess_reduction_db']=d['first5_positive_excess_reduction_db']-limits['C3_each_layer_minimum_first5_positive_excess_reduction_db']
            values['C3_ring5_20_excess_reduction_db']=d['ring5_20_positive_excess_reduction_db']-limits['C3_each_layer_minimum_ring5_20_positive_excess_reduction_db']
        else:values['each_early_window_band_MAE_db']=limits['C4_C6_each_early_window_maximum_band_MAE_worsening_db']-max(d['early_window_band_MAE_db'])
        arithmetic_equal(values,table['gate_margins_db'],ident+'/margins')
        arithmetic_equal(min(values.values()),table['minimum_numeric_margin_db'],ident+'/minimum_margin')
        require(min(values,key=values.get)==table['limiting_numeric_gate'],'Limiting gate changed')
        require(table['boolean_gate_requirements']=={k:case['gates'][k] for k in ('baseline_payload_exact_to_cached_control','mechanical_state_force_bit_parity','no_new_faults')},'Margin proof metadata differs')
        for role,features in [('old',olds[ident]['baseline']),('crossover',case['candidate'])]:
            require([e['window_seconds'] for e in features['early']]==old_protocol['analysis']['early_windows_seconds'],'Four early windows differ')
            for i,early in enumerate(features['early']):
                require(len(early['band_signed_errors_db'])==5,'Five-band inventory differs')
                arithmetic_equal(sum(abs(x) for x in early['band_signed_errors_db'])/5,early['five_band_MAE_db'],ident+'/'+role+'/five_band_mean')
    c6=[]
    require(tuple(c['id'] for c in margins['C6_signed_LF_analysis'])==('C6v4','C6v12'),'C6 diagnostic inventory changed')
    for table in margins['C6_signed_LF_analysis']:
        ident=table['id'];case=bycase[ident]
        require([w['window_seconds'] for w in table['windows']]==old_protocol['analysis']['early_windows_seconds'],'C6 four-window inventory differs')
        for i,window in enumerate(table['windows']):
            for label,features in [('old',olds[ident]['baseline']),('causal',prior[ident]['candidate']),('crossover',case['candidate'])]:
                early=features['early'][i]
                require(window['window_seconds']==early['window_seconds'],'C6 window changed')
                require(window['all_five_band_signed_errors_db'][label]==early['band_signed_errors_db'],'C6 signed bands changed')
                require(window['LF_31_25_to_250_Hz_signed_error_db'][label]==early['band_signed_errors_db'][0],'C6 LF error changed')
                require(window['five_band_MAE_db'][label]==early['five_band_MAE_db'],'C6 MAE changed')
            old_lf=window['LF_31_25_to_250_Hz_signed_error_db']['old'];new_lf=window['LF_31_25_to_250_Hz_signed_error_db']['crossover']
            arithmetic_equal(abs(new_lf)-abs(old_lf),window['LF_absolute_error_worsening_crossover_minus_old_db'],ident+'/LF')
            arithmetic_equal(new_lf-old_lf,window['LF_signed_error_change_crossover_minus_old_db'],ident+'/LF_signed_change')
            arithmetic_equal(window['five_band_MAE_db']['crossover']-window['five_band_MAE_db']['old'],window['crossover_five_band_MAE_worsening_db'],ident+'/MAE_change')
        for field,worst,where in [('crossover_five_band_MAE_worsening_db','worst_five_band_MAE_worsening_db','worst_five_band_MAE_window'),
                                  ('LF_absolute_error_worsening_crossover_minus_old_db','worst_LF_absolute_error_worsening_db','worst_LF_absolute_error_worsening_window')]:
            window=max(table['windows'],key=lambda w:w[field])
            arithmetic_equal(window[field],table[worst],ident+'/'+worst)
            require(window['window_seconds']==table[where],'C6 worst-window label changed')
        c6.append({'id':ident,'first5_LF_absolute_error_worsening_db':table['windows'][0]['LF_absolute_error_worsening_crossover_minus_old_db'],
            'worst_five_band_MAE_worsening_db':max(case['changes']['early_window_band_MAE_db']),
            'LF_signed_errors_20_to_50_and_50_to_100_ms_db':[w['LF_31_25_to_250_Hz_signed_error_db']['crossover'] for w in table['windows'][2:]]})
    require(len(c6)==2 and all(c['first5_LF_absolute_error_worsening_db']>1 for c in c6),'Individual LF regression caveat lost')
    for name in ('independent-review.json','independent-result-review.json'):
        review=read(PACKAGE/'evidence'/name);require(review['passed'] is True,'Independent review failed')
    stored=read(PACKAGE/'evidence/independent-result-review.json')
    require(stored['result_sha256']==sha(ROOT/'Validation/full-radiation-crossover.json') and stored['default_or_publication_approved'] is False,'Independent result scope differs')
    presentation=read(ROOT/'Audio/full-radiation-crossover/manifest.json')
    for key in ('source','protocol','result','freeze','review'):
        row=presentation['crossover'][key]
        require(sha(ROOT/row['file'])==row['sha256'],'Presentation crossover binding changed: '+key)
    for key,row in presentation['reused_source_evidence'].items():
        if 'file' in row:require(sha(ROOT/row['file'])==row['sha256'],'Presentation upstream binding changed: '+key)
    require(presentation['crossover']['posthoc_TRAIN_reuse'] is True and presentation['crossover']['broader34_validated'] is False,'Presentation role differs')
    require(presentation['crossover']['original_unfiltered_causal_pilot_still_failed'] is True,'Presentation rewrote original failure')
    require(presentation['default_changed'] is False and presentation['production_source_changed'] is False and presentation['subjective_improvement_claim'] is False,'Presentation scope changed')
    require(presentation['checks']['listener_verdict'] is None,'Listener qualification claimed')
    environment=read(ROOT/'Audio/full-radiation-crossover/environment-receipt.json')
    observations={r['OPENBLAS_NUM_THREADS']:r for r in environment['observations']}
    historical_IR=read(ROOT/'Audio/full-radiation-pilot/manifest.json')['music_recipe']['procedural_ir_float64_sha256']
    require(observations[1]['float64_IR_sha256']==historical_IR=='38dd2ac037e8fb2cb47f3ec561c37eab0478cef092b7ded9b617b92d6458b374','Historical room environment binding differs')
    require(observations[8]['float64_IR_sha256']=='b033d343963462d49247dade80a831015e5a3c04534160fc2f303d55d7806657','Thread-mismatch observation changed')
    require(presentation['environment']['required_before_numpy_import']=={'OPENBLAS_NUM_THREADS':'1'},'Replay thread pin changed')
    require(presentation['environment']['first_attempt_preserved'] is True and presentation['environment']['IR_or_gain_source_changed'] is False,'Retry scope changed')
    reproduction=read(ROOT/'Audio/full-radiation-crossover/evidence/presentation-reproduction.json')
    require(all(reproduction[k] is True for k in ('passed','PCM24_exact','old_segment_PCM24_exact','gap_exact_zero','finite')),'Recorded presentation reproduction failed')
    require(reproduction['flac_sha256']==presentation['audio']['sha256'] and reproduction['pcm24_sha256']==presentation['audio']['pcm24_sha256'],'Presentation fingerprints differ')
    for path,expected in published:require(sha(path)==expected,'Published input changed during review: '+str(path))
    require(sha(index_path)==index_sha,'Index changed during review')
    report={'schema_version':1,'reviewed_at_utc':datetime.now(timezone.utc).isoformat(),'passed':True,
        'scope':'Published hashes, archived source/protocol/reviews and stored original-gate arithmetic only. No PCM, filtering, synthesis or new scoring.',
        'index_sha256':index_sha,'verifier_sha256':sha(__file__),'python':platform.python_version(),
        'six_posthoc_TRAIN_cases_pass_unchanged_gates':True,'original_failed_pilot_passes':False,
        'source_archive_files_reused_without_copy':len(upstream['files']),'captured_audio_files_not_opened':len(index['unbundled_audio']),
        'presentation_metadata_and_environment_bindings_consistent':True,'comparison_audio_opened_or_reproduced_by_this_verifier':False,
        'C6_caveats':c6,'default_changed':False,'broader_TRAIN34_listening_or_host_qualification':False,
        'limits':['Stored arithmetic review is not independent PCM feature verification or acoustic realism validation.',
            'Presentation hashes and environment/reproduction receipts are checked as metadata; this verifier does not open the comparison audio or regenerate the room IR.',
            'Relative five-band means can pass while an individual band regresses and large inherited signed deficits remain.',
            'Finite-width physical parity evidence is inherited from source pairs, not a new instrument-state run.',
            'This package preserves archived chronology; publication and later review cannot recreate first-use chronology.']}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
