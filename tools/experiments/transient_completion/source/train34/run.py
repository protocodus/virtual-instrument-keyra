#!/usr/bin/env python3
"""Frozen full TRAIN34 confirmation: reuse six exact outcomes, emit only28."""
from pathlib import Path
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import argparse,ctypes,hashlib,importlib.util,math,subprocess,time,traceback
import numpy as np
from scipy.io import wavfile

OUT=Path(__file__).resolve().parent;PARENT=OUT.parent;PILOT=PARENT/'pitch-scaled-v1';V1=PARENT/'v1'
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
base=module(V1/'run.py','confirmation_original_base');protect=module(PARENT/'lf-protected-v1/run.py','confirmation_fixedHP200')
ROOT=base.ROOT;read=base.read;rec=base.rec;sha=base.sha;write=base.write;verify=base.verify;now=base.now
REFERENCE=ROOT/'out/full-radiation-crossover/train34/reference-control.json'
HELPER=ROOT/'out/full-radiation-crossover/train34/measure_references.py'
HISTORY=ROOT/'out/full-radiation-crossover/train34/result.json'
RATE=48000;FRAMES=182400

def compile_filter():
    path=OUT/'filter.so';cmd=['g++','-std=c++17','-O3','-fno-builtin','-ffp-contract=off','-shared','-fPIC',str(OUT/'filter.cpp'),'-o',str(path)];subprocess.run(cmd,check=True)
    lib=ctypes.CDLL(str(path));function=lib.keyra_protect_counter;pointer=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS');function.argtypes=[pointer,pointer,pointer,ctypes.c_size_t,pointer];function.restype=ctypes.c_int
    def process(old,fast,chunks):
        old=np.ascontiguousarray(old,dtype=np.float64);fast=np.ascontiguousarray(fast,dtype=np.float64);output=np.empty((len(old),10));state=np.zeros(16);offset=0;block=0
        while offset<len(old):
            end=min(len(old),offset+chunks[block%len(chunks)])
            if function(old[offset:end],fast[offset:end],output[offset:end],end-offset,state):raise ValueError('NonfiniteHP200')
            offset=end;block+=1
        return output,state
    return process,{'command':cmd,'binary':rec(path)}

def freeze():
    if (OUT/'protocol.json').exists():raise ValueError('Already frozen')
    fixed={PILOT/'result.json':'a87a84561d99895e9903f258400c60594b323c357373b6c41f7f68f637597efd',REFERENCE:'e3ad140a8052c2e81acdc0a281a4e658a2df7f796029572d562634c8adf375fe',HELPER:'45b38bc157afdff800c1c2f9c6090d4c51225acb058f5057f214808d0a74e3b6',OUT/'filter.cpp':'8859dbbebac6e54fe1a5e4c93dfb420b1fc91f0ef51f204ae2ebb8c93d5616cd'}
    for path,h in fixed.items():
        if sha(path)!=h:raise ValueError('Fixedidentity'+str(path))
    prefix=(PILOT/'replay.cpp').read_bytes().split(b'\nint main(int argc,char** argv) {')[0]+b'\n'
    if (OUT/'pitch_helpers.h').read_bytes()!=prefix:raise ValueError('Pitchhelpers changed')
    pilot=read(PILOT/'result.json');old=read(PILOT/'protocol.json')
    if pilot['passes_all_original_gates'] is not True or len(pilot['cases'])!=6:raise ValueError('Pilot notqualified')
    refs={c['id']:c for c in read(REFERENCE)['cases']};bindings={c['id']:c for c in read(base.BINDING)['cases']};history={c['id']:c for c in read(HISTORY)['cases']};reused={c['id']:c for c in pilot['cases']}
    cases=[]
    for ident,reference in refs.items():
        b=bindings[ident];role='reused_exact_pilot' if ident in reused else 'new_confirmation'
        proof=reused[ident]['source_proof'] if ident in reused else history[ident]['source_proof']
        cases.append({'id':ident,'midi':b['midi'],'role':role,'trace':{'path':b['trace'],'sha256':b['expected_trace_sha256']},'force_proof':{'path':b['force_proof'],'sha256':b['expected_proof_sha256']},
          'baseline_audio':reference['baseline_audio'],'fixed_gain':reference['baseline']['fixed_gain'],'fixed_onset_frame':reference['baseline']['fixed_onset_frame'],'support':reference['support'],'source_proof':proof})
    if len(cases)!=34 or sum(c['role']=='new_confirmation' for c in cases)!=28:raise ValueError('TRAINinventory')
    inputs=[PILOT/'result.json',PILOT/'protocol.json',PILOT/'replay.cpp',PILOT/'mechanics_v2_prefix.h',PILOT/'renders/bound-and-gamma.json',REFERENCE,HELPER,HISTORY,base.BINDING,base.FEATURES,V1/'run.py',V1/'replay.cpp']+[Path(x['path']) for x in old['inputs']]
    p={'schema_version':1,'frozen_at_utc':now(),'scope':'One fullTRAIN34 confirmation of the SAME frozen pitch-scaled full-pressure gammafield+HP200. Six qualified pilot outcome objects reused exactly; only28 new force-driven observer outputs/scorings. Already observed TRAIN, not fresh holdouts.',
      'new28_pressure_opened':False,'sources':[rec(OUT/x) for x in ['replay.cpp','pitch_helpers.h','filter.cpp','run.py']],'inputs':[rec(x) for x in dict.fromkeys(inputs)],'cases':cases,
      'pitch_law':old['pitch_law'],'matrix_scope':old['matrix_scope'],'minimum_gamma':100,'body_gamma':100,'pitch_law_variants':1,'cutoff_hz':200,'cutoff_variants':1,'strength':1,'fit_runs':0,
      'same_model_geometry':{'original_model_sha256':'5c8c92f8a761b46a66f3823765f6348ab0c08b74457d7efc062f0941ab07faf8','calibration_sha256':'619d6bf4d3200a6b55007a1abcc0658e76a14124ce5f3abad9f5f4b94d8979f7','sample_rate':48000,'frames':182400,'string_modes':17778,'strings':230,'board_modes':475,'mechanical_level':0,'humanization':0,'repetition_controller':False},
      'helper_reuse':'scalePitch/stepPitch and all mechanical/bound helpers are included byte-for-byte from qualified pilot prefixes. Prepared all88gamma/coldbound JSON must be byteidentical to pilot BEFORE any new recorded input is opened.',
      'control_scope':'Six uniform100 prefix controls and six historicalrho1full3.8s controls are implementation qualification at collection time. NOT repeated for new28; no per-new-case prefix/rho1 parity claim. All28 get actual forceFNV, baselineHPpayload, finite/fault, energy/fullbound/quiescence/count/HPtail/chunk checks.',
      'physical_scope':'Only the virtual fullstate observer is advanced from saved contactF. Original source/raw pressure unchanged; captured Schurvalues used for inputauthentication only, never as observerdrive.',
      'reuse_six':'Append exactly the original six outcome JSONobjects without rescoring/mutation; assert equality after newbatch.',
      'complete_C8_support':'Use immutable helper45b38 and stored support. C8v4 only complete three late windows through2.5s and full-support envelope through2.80s; no padding/retiming/releveling.',
      'original_gates':old['original_gates'],'gate_arithmetic_sha256':old['gate_arithmetic_sha256'],'canonical_partition':[64],'alternate_partition':[1,3,17,64,129,7],
      'compile':['g++','-std=c++17','-O3','-DNDEBUG','-fno-builtin','-ffp-contract=off',str(OUT/'replay.cpp'),'-o',str(OUT/'replay')],
      'fixed_gains_onsets_masks':True,'gamma_or_corner_sweep':False,'new_reference_PCM_access':False,'new_nonlinear_contact_source_render':False,'adopted':False,'listening_exported':False,
      'log_policy':'Closedproducer.logindexed; liveouterrun.logexcluded.','limitations':['All34 already observedTRAIN, six exact pilot reuses.','Fullstate companion is an offline quality proof, not realtime architecture.','No measured propagation/part identification, runtime/default or host claim follows from numericguards.']}
    write(OUT/'protocol.json',p);write(OUT/'freeze.json',{'protocol':rec(OUT/'protocol.json'),'sources':p['sources'],'frozen_at_utc':p['frozen_at_utc']})

def execute():
    p=read(OUT/'protocol.json');f=read(OUT/'freeze.json');case_inputs=[x for c in p['cases'] for x in (c['trace'],c['force_proof'],c['baseline_audio'])];identities=[f['protocol'],*p['sources'],*p['inputs'],*case_inputs];verify(identities)
    if (OUT/'opening-started.json').exists():raise ValueError('Once-only confirmation already started')
    write(OUT/'opening-started.json',{'started_at_utc':now(),'protocol':rec(OUT/'protocol.json'),'new28_pressure_opened':False})
    start=time.monotonic();subprocess.run(p['compile'],check=True);process,filterbuild=compile_filter();filtertests=protect.synthetic(process);write(OUT/'filter-synthetic.json',filtertests)
    if not filtertests['pass']:raise ValueError('Filter synthetic')
    fresh=[c for c in p['cases'] if c['role']=='new_confirmation'];output=OUT/'renders';output.mkdir(exist_ok=False)
    for c in fresh:(output/c['id']).mkdir()
    tsv=OUT/'cases.tsv';tsv.write_text(''.join('\t'.join([c['id'],str(c['midi']),c['trace']['path'],str(c['fixed_onset_frame']),c['force_proof']['path']])+'\n' for c in fresh))
    cmd=[str(OUT/'replay'),str(tsv),str(output),str(PILOT/'renders/bound-and-gamma.json')];write(OUT/'producer-freeze.json',{'created_at_utc':now(),'protocol':rec(OUT/'protocol.json'),'binary':rec(OUT/'replay'),'case_tsv':rec(tsv),'command':cmd})
    with (OUT/'producer.log').open('x') as log:
        job=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        for line in job.stdout:log.write(line);log.flush();print(line,end='',flush=True)
        status=job.wait()
    if status:raise ValueError('New28producerexit'+str(status))
    cold=read(output/'bound-and-gamma.json');synthetic=read(output/'synthetic.json')
    if sha(output/'bound-and-gamma.json')!=sha(PILOT/'renders/bound-and-gamma.json'):raise ValueError('Preparedall88gammaboundchanged')
    if not synthetic['retired'] or not synthetic['wake_identity'] or synthetic['max_free_energy_ratio']>1 or synthetic['max_zero_force_pressure_over_bound']>1 or synthetic['faults']:raise ValueError('Syntheticwake/energy')
    metric,gate,gate_sha=base.tools();helper=module(HELPER,'confirmation_frozen_censored_helper')
    if gate_sha!=p['gate_arithmetic_sha256']:raise ValueError('Gatearithmeticchanged')
    refs={x['id']:x for x in read(REFERENCE)['cases']};rows={x['id']:x for x in read(base.FEATURES)['samples']};reused={x['id']:x for x in read(PILOT/'result.json')['cases']};outcomes=[]
    for c in p['cases']:
        ident=c['id']
        if c['role']=='reused_exact_pilot':outcomes.append(reused[ident]);print(ident,'REUSED exact pilot outcome',flush=True);continue
        d=output/ident;numeric=read(d/'numeric.json');guards={'force':numeric['force_contract_errors']==numeric['force_proof_mismatches']==0,'finite':numeric['nonfinite']==0,'faults':numeric['faults']==0,'scale_energy':numeric['max_positive_scale_energy']==0,
          'free_energy':numeric['max_free_energy_ratio']<=1,'full_bound':numeric['max_zero_force_pressure_over_bound']<=1,'retirement':numeric['retirements']>=1 and numeric['discarded_future_bound']<=1e-20,
          'counts':numeric['mode_count']==17778 and numeric['strings']==230 and numeric['board_modes']==475,'control_scope_honest':numeric['new_uniform_prefix_control_run'] is False and numeric['new_rho1_control_run'] is False}
        if not all(guards.values()):raise ValueError('Numericguard'+ident+str(guards))
        original=np.memmap(c['trace']['path'],dtype='<f8',mode='r',shape=(FRAMES,15));fast=np.memmap(d/'fast.f64le',dtype='<f8',mode='r',shape=(FRAMES,15));old=np.ascontiguousarray(original[:,:2]);counter=np.ascontiguousarray(fast[:,:2]);values,state=process(old,counter,p['canonical_partition']);alternate,other=process(old,counter,p['alternate_partition']);partitions=values.tobytes()==alternate.tobytes() and state.tobytes()==other.tobytes()
        baseline=values[:,2:4].astype('<f4');candidate=values[:,4:6].astype('<f4');sr,historical=wavfile.read(c['baseline_audio']['path']);exact=sr==RATE and historical.dtype==np.float32 and baseline.tobytes()==historical.astype('<f4').tobytes()
        if not partitions or not exact or not np.isfinite(candidate).all():raise ValueError('Filter/baselineguard'+ident)
        values.tofile(d/'filtered.f64le');wave=d/'candidate.wav';wavfile.write(wave,RATE,candidate)
        features=helper.observation_features(metric,candidate.astype(float),c['fixed_onset_frame'],c['fixed_gain'],refs[ident]['reference'],rows[ident],c['support']);scored=gate(refs[ident],features,ident,exact,{ident:c['source_proof']})
        onset=c['fixed_onset_frame'];tail=values[onset+12000:,6:8];sustain=baseline[onset+12000:onset+36000].astype(float);rms=float(np.sqrt(np.mean(tail*tail)));base_rms=float(np.sqrt(np.mean(sustain*sustain)))
        outcome={'id':ident,'candidate_audio':rec(wave),'candidate':features,**scored,'numeric':numeric,'numeric_guards':guards,'support':c['support'],'postprocessor':{'partition_bytes_exact':partitions,'baseline_HP_payload_exact':exact,'final_state':state.tolist()},
          'tail':{'HP_RMS_after250ms':rms,'HP_peak_after250ms':float(np.max(abs(tail))),'HP_relative_old_sustain_RMS_db':20*math.log10(max(rms,1e-300)/max(base_rms,1e-300))},'source_proof':c['source_proof'],'implementation_controls':'Genericfunctionsqualifiedbytheunchangedsixpilotprefix/historicalrho1controls; no new per-case uniform/rho1control claim.','adopted':False}
        outcomes.append(outcome);write(d/'result.json',outcome);print(ident,'PASS' if outcome['passes_all_case_gates'] else 'FAIL',outcome['gates'],flush=True)
    verify(identities)
    for ident,original in reused.items():
        if next(x for x in outcomes if x['id']==ident)!=original:raise ValueError('Reusedpilotoutcomemutated'+ident)
    result={'completed_at_utc':now(),'protocol':rec(OUT/'protocol.json'),'producer_freeze':rec(OUT/'producer-freeze.json'),'filter_build':filterbuild,'filter_synthetic':filtertests,'pitch_synthetic':synthetic,'cold_bound_gamma':cold,'cases':outcomes,
      'case_count':34,'new_cases':28,'exact_pilot_outcomes_reused':6,'cases_passing_all_original_gates':sum(c['passes_all_case_gates'] for c in outcomes),'passes_all_original_gates':all(c['passes_all_case_gates'] for c in outcomes),'wall_seconds':time.monotonic()-start,
      'minimum_gamma':100,'body_gamma':100,'pitch_law_variants':1,'cutoff_hz':200,'cutoff_variants':1,'fit_runs':0,'new_reference_PCM_access':False,'new_full_companion_force_replays':28,'new_rho1_replays':0,'new_uniform_prefix_replays':0,'adopted':False,'limitations':p['limitations']}
    write(OUT/'result.json',result);print('TRAIN34 CONFIRMATION',result['cases_passing_all_original_gates'],'/34 pass',flush=True)
    manifest={str(x.relative_to(OUT)):{'sha256':sha(x),'bytes':x.stat().st_size} for x in sorted(OUT.rglob('*')) if x.is_file() and x.name not in ('manifest.json','run.log') and '__pycache__' not in x.parts};write(OUT/'manifest.json',manifest)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['freeze','run']);args=parser.parse_args()
    if args.command=='freeze':freeze();return
    try:execute()
    except Exception as e:
        if not (OUT/'failure.json').exists():write(OUT/'failure.json',{'failed_at_utc':now(),'error_type':type(e).__name__,'error':str(e),'traceback':traceback.format_exc(),'silently_retried':False})
        raise
if __name__=='__main__':main()
