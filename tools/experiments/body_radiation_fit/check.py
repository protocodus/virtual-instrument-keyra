#!/usr/bin/env python3
"""Verify archived six-weight fit identities and stored decisions; stdlib only.

No PCM decode, synthesis, numerical Gram extraction, optimizer or feature scorer.
NPZ moment files are hashed and their safe numeric headers inspected only.
"""
from pathlib import Path
import argparse,ast,collections,hashlib,importlib.util,io,json,math,struct,sys,zipfile

PACKAGE=Path(__file__).resolve().parent
ROOT=PACKAGE.parents[2]
OLD='/workspace/virtual-instrument-keyra/out/full-body-fit'
spec=importlib.util.spec_from_file_location('body_basis_archive_reader',ROOT/'tools/experiments/body_radiation_basis/check.py')
reader=importlib.util.module_from_spec(spec);spec.loader.exec_module(reader)
require=reader.require
digest=reader.digest

def close(a,b):return math.isclose(a,b,rel_tol=128*sys.float_info.epsilon,abs_tol=128*sys.float_info.epsilon)
def mean(x):return sum(x)/len(x)
def power_db(x,y,floor):return 10*math.log10(max(x,floor)/max(y,floor))

def original_gates(old,candidate,ident,proof):
    base=old['baseline'];floor=old['reference']['sustain_power']*1e-10
    first=max(0.,base['early'][0]['broad_signed_error_db'])-max(0.,candidate['early'][0]['broad_signed_error_db'])
    ring=max(0.,base['early'][1]['ring_signed_error_db'])-max(0.,candidate['early'][1]['ring_signed_error_db'])
    harmonic=candidate['late_harmonic_MAE_db']-base['late_harmonic_MAE_db']
    envelope=candidate['late_envelope']['MAE_db']-base['late_envelope']['MAE_db']
    drift=20*math.log10(candidate['sustain_RMS']/base['sustain_RMS'])
    early=[c['five_band_MAE_db']-b['five_band_MAE_db'] for c,b in zip(candidate['early'],base['early'])]
    LR=candidate['stereo']['sustain']['LR_db']-base['stereo']['sustain']['LR_db']
    mono=power_db(candidate['stereo']['sustain']['mono_power'],base['stereo']['sustain']['mono_power'],floor)
    gates={'baseline_payload_exact_to_cached_control':True,
           'mechanical_state_force_bit_parity':proof['mechanical_state_bit_parity'] and proof['force_bit_parity'],
           'no_new_faults':proof['new_faults']==0,'late_harmonic_MAE':harmonic<=.75,
           'late_envelope_MAE':envelope<=.75,'late_RMS_drift':abs(drift)<=.5,
           'stereo_LR_shift':abs(LR)<=.5,'mono_energy_shift':abs(mono)<=.75}
    if ident.startswith('C3'):gates.update(C3_first5_excess_reduction=first>=3.,C3_ring5_20_excess_reduction=ring>=3.)
    else:gates['each_early_window_band_MAE']=max(early)<=1.
    return gates,{'first5_positive_excess_reduction_db':first,'ring5_20_positive_excess_reduction_db':ring,
                  'late_harmonic_MAE_db':harmonic,'late_envelope_MAE_db':envelope,'late_RMS_db':drift}

def check_forecasts(case,alpha):
    direct=case['final_double_gram_forecast'];rounded=case['final_float32_gram_forecast']
    require(direct['test_alpha']==rounded['alpha']==alpha,'Same fitted alpha in every forecast')
    require(direct['pass'] is True and rounded['pass'] is True,'Stored final forecast failed')
    for check in list(direct['coherent_feature_checks'].values())+list(rounded['checks'].values()):
        require(check['pass'] is True and check['maximum_error_over_bound']<=1,'Forecast bound failed')
    for check in direct['psd']:
        require(check['pass'] is True and check['negative_eigenvalue_over_bound']<=1,'PSD bound failed')

def inspect_npz(data):
    arrays=0
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        for name in archive.namelist():
            require(name.endswith('.npy') and '/' not in name,'Unexpected NPZ member')
            value=archive.read(name);require(value[:6]==b'\x93NUMPY','NPY magic')
            version=tuple(value[6:8])
            if version==(1,0):size=struct.unpack('<H',value[8:10])[0];offset=10
            elif version==(2,0):size=struct.unpack('<I',value[8:12])[0];offset=12
            else:raise ValueError('Unsupported NPY version')
            header=ast.literal_eval(value[offset:offset+size].decode('latin1').strip())
            require(header['descr'] in ('<f8','<i8','|b1'),'NPZ must be numeric, never object/pickle')
            require(header['fortran_order'] is False,'Unexpected NPZ layout')
            shape=header['shape'];require(isinstance(shape,tuple) and all(isinstance(n,int) and 0<=n<10000 for n in shape),'Unexpected moment dimensions')
            count=math.prod(shape);width=1 if header['descr']=='|b1' else 8
            require(len(value)==offset+size+count*width,'NPY data size')
            arrays+=1
    return arrays

def verify(index):
    a=reader.Archive(index)
    p=a.role('v2_protocol');frozen=a.role('v2_freeze');result=a.role('v2_result')
    fit=a.role('v2_fit_result');grams=a.role('v2_gram_receipt');manifest=a.role('v2_manifest')
    reference=a.role('reference_control');refs={c['id']:c for c in reference['cases']}
    validation=a.role('validation');summary=a.role('v2_summary')
    basis=a.role('basis_result');require(basis['pass'] is True and basis['count']==34,'Prior body reconstruction')
    require(frozen['protocol']==result['protocol']==index['roles']['v2_protocol'],'Protocol binding')
    require(frozen['sources']==p['sources'],'Source freeze binding')
    for item in p['sources']+p['inputs']:a.identity(item['path'],item['sha256'])
    require(result['fit_result']==index['roles']['v2_fit_result'] and result['gram_receipt']==index['roles']['v2_gram_receipt'],'Outcome bindings')
    require(p['optimizer']['method']=='L-BFGS-B' and p['optimizer']['start_theta_dB']==[0.]*6,'One fixed start')
    require(p['optimizer']['bounds_alpha']==[.025,40.] and p['optimizer']['restarts_or_sweeps'] is False,'Frozen bounds/no sweep')
    require(len(p['cases'])==34 and sum(c['fit'] for c in p['cases'])==32,'Fit/apply inventory')
    require({c['id'] for c in p['cases'] if not c['fit']}=={'C8v4','C8v12'},'Only calibration selection excludes C8')
    for case in p['cases']:
        old=refs[case['id']]
        require(case['fit'] is (not case['id'].startswith('C8')),'Shared rule')
        require(case['fixed_old_gain']==old['baseline']['fixed_gain'] and case['fixed_old_onset_frame']==old['baseline']['fixed_onset_frame'] and case['support']==old['support'],'Fixed gain/onset/support')
        a.identity(case['basis']['path'],case['basis']['sha256'],182400*14*8)
    require(fit['success'] is True and fit['iterations']==13 and fit['evaluations']==14==len(fit['trace']),'Converged one solve')
    require(fit['same_alpha_all34'] is True and fit['fit_count']==32 and fit['excluded_fit_cases']==['C8v4','C8v12'],'Shared coefficients and fit scope')
    require(fit['initial_is_old_final_sound'] is False,'Alpha1 is raw body, not old final sound')
    require(all(close(alpha,10**(theta/20)) and .025<=alpha<=40 for alpha,theta in zip(fit['alpha'],fit['theta_dB'])),'Coefficient transform/bounds')
    require([t['evaluation'] for t in fit['trace']]==list(range(14)) and fit['trace'][0]['theta_dB']==[0.]*6,'Full optimizer trace')
    for t in fit['trace']:require(reader.finite_tree(t),'Finite optimizer trace')
    require(fit['trace'][-1]['theta_dB']==fit['theta_dB'] and close(fit['trace'][-1]['objective'],fit['final_objective']['total']),'Final trace binding')
    final=fit['final_objective'];theta=fit['theta_dB']
    require(close(final['prior'],.01*mean([v*v for v in theta])) and close(final['smooth'],.02*mean([(b-c)**2 for b,c in zip(theta[1:],theta[:-1])])),'Fixed regularizers')
    require(close(final['total'],mean(final['family_losses'])+final['prior']+final['smooth']),'Objective components')
    require(result['case_count']==34 and len(result['cases'])==34 and {c['id'] for c in result['cases']}==set(refs),'All outcomes present')
    failures=collections.Counter()
    for case in result['cases']:
        ident=case['id'];old=refs[ident];features=case['candidate']
        require(case['used_in_fit'] is (not ident.startswith('C8')),'Fit role in output')
        require(features['fixed_gain']==old['baseline']['fixed_gain'] and features['fixed_onset_frame']==old['baseline']['fixed_onset_frame'],'No final gain or retiming')
        require([w['window_seconds'] for w in features['late_harmonics']]==old['support']['late_windows_seconds'],'Complete actual late support')
        require(features['late_envelope']['times_seconds']==old['reference']['late_envelope']['times_seconds'] and features['late_envelope']['included']==old['reference']['late_envelope']['included'],'Fixed envelope masks')
        gates,changes=original_gates(old,features,ident,case['source_proof'])
        require(gates==case['gates'] and all(gates.values()) is case['passes_all_case_gates'],'Stored original gate arithmetic')
        for key,value in changes.items():require(close(value,case['changes'][key]),'Stored change '+key)
        for key,value in gates.items():
            if not value:failures[key]+=1
        check_forecasts(case,fit['alpha'])
        stored=a.resolve(OLD+'/v2/case-results/'+ident+'.json',manifest['case-results/'+ident+'.json']['sha256'])
        require(reader.json_data(stored)==case,'Individual case/full result equality')
    expected={'late_harmonic_MAE':24,'late_RMS_drift':34,'mono_energy_shift':31,'each_early_window_band_MAE':22,'stereo_LR_shift':25,'C3_ring5_20_excess_reduction':2,'late_envelope_MAE':17}
    require(dict(failures)==expected==summary['failed_gate_counts']==validation['failed_gate_counts'],'Failure categories')
    require(len(result['failed_case_ids'])==34 and result['passes_all_preservation_gates'] is False and result['passed'] is False,'Global failure retained')
    require(result['optimizer_converged'] is True and result['final_forecast_checks_pass'] is True,'Numerical success scoped correctly')
    require(result['reference_PCM_opened'] is False and result['physical_synthesis_runs']==0 and result['adopted'] is False,'No synthesis/acquisition/adoption')
    require(len(grams['all34_direct_parity'])==34 and all(c['pass'] is True for c in grams['all34_direct_parity']),'All prefit numerical checks')
    total_gram_bytes=0;arrays=0
    for item in grams['files']:
        data=a.resolve(item['path'],item['sha256']);total_gram_bytes+=len(data);arrays+=inspect_npz(data)
    require(len(grams['files'])==index['gram_files']==34 and total_gram_bytes==index['gram_bytes']==4814760,'All compact moments included')
    completion=a.role('v2_completion_receipt');log=completion['final_run_log'];data=a.resolve(log['path'],log['sha256'])
    prefix=completion['original_run_log_prefix'];tail=data[prefix['bytes']:]
    require(digest(data[:prefix['bytes']])==prefix['sha256']==manifest['run.log']['sha256'],'Original log prefix retained')
    require(digest(tail)==completion['appended_suffix']['sha256'] and len(tail)==completion['appended_suffix']['bytes'],'Final appended journal identity')
    require(reader.json_data(tail)=={k:v for k,v in result.items() if k not in ['cases','limits']},'Appended summary equals result')
    for relative,row in manifest.items():a.identity(OLD+'/v2/'+relative,row['sha256'],row['bytes'])
    failed=a.role('v1_failure');require(failed['error']=='Actual coherent featureparity failed: C6v4' and failed['silently_retried'] is False,'Initial numeric failure preserved')
    require(index['v1_stopped_before_optimizer'] is True and index['optimizer_runs']==1,'No prior optimizer retry')
    review=a.role('audit_v2_post_run_review');addendum=a.role('audit_v2_completion_review_addendum')
    require(review['preservation_pass_count']==0 and review['case_count']==34 and review['all34_exact_original_gate_arithmetic_rechecked'] is True,'Independent postreview')
    require(review['preservation_failed_gate_counts']==dict(failures),'Independent review failure counts')
    require(validation['adopted'] is False and validation['runtime_or_default_changes'] is False,'Validation default status')
    require(reader.finite_tree(result) and reader.finite_tree(fit),'Finite stored outputs')
    return {'published_records_verified':a.checked,'compact_gram_files':34,'compact_gram_arrays':arrays,'compact_gram_bytes':total_gram_bytes,'stored_original_gate_cases_verified':34,'preservation_pass_count':0,'preservation_fail_count':34,'failed_gate_counts':dict(failures),'optimizer_runs':1,'audio_decoded':False,'optimizer_or_DSP_run':False,'adopted':False,'verification_passed':True}

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path)
    args=parser.parse_args();result=verify(reader.json_data((PACKAGE/'index.json').read_bytes()))
    if args.output:
        require(not args.output.exists(),'New output path required');args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
