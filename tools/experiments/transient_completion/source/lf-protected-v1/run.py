#!/usr/bin/env python3
"""One post-hoc TRAIN followup: fixed HP200-protected gamma100 counterterm."""
from pathlib import Path
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import argparse,ctypes,importlib.util,json,math,subprocess,time,traceback
import numpy as np
from scipy.io import wavfile

OUT=Path(__file__).resolve().parent;PARENT=OUT.parent;V1=PARENT/'v1';V2=PARENT/'v2'
spec=importlib.util.spec_from_file_location('frozen_transient_base',V1/'run.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
ROOT=base.ROOT;sha=base.sha;read=base.read;rec=base.rec;write=base.write;verify=base.verify;now=base.now
RATE=48000;FRAMES=182400;CANONICAL=[64];ALTERNATE=[1,3,17,64,129,7]

def compile_filter():
    destination=OUT/'filter.so'
    command=['g++','-std=c++17','-O3','-fno-builtin','-ffp-contract=off','-shared','-fPIC',str(OUT/'filter.cpp'),'-o',str(destination)]
    subprocess.run(command,check=True);library=ctypes.CDLL(str(destination));function=library.keyra_protect_counter
    pointer=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS');function.argtypes=[pointer,pointer,pointer,ctypes.c_size_t,pointer];function.restype=ctypes.c_int
    def process(old,fast,chunks):
        old=np.ascontiguousarray(old,dtype=np.float64);fast=np.ascontiguousarray(fast,dtype=np.float64)
        if old.shape!=fast.shape or old.ndim!=2 or old.shape[1]!=2:raise ValueError('Stereo shape')
        output=np.empty((len(old),10),dtype=np.float64);state=np.zeros(16);offset=0;block=0
        while offset<len(old):
            stop=min(len(old),offset+chunks[block%len(chunks)])
            if function(old[offset:stop],fast[offset:stop],output[offset:stop],stop-offset,state):raise ValueError('Nonfinite filter')
            offset=stop;block+=1
        return output,state
    return process,{'command':command,'binary':rec(destination)}

def synthetic(process):
    k=math.tan(math.pi*200/RATE);a=(1-k)/(1+k);b=1/(1+k)
    n=np.arange(8192);old=np.column_stack((np.sin(n*.123),np.cos(n*.071)))
    signal=np.column_stack((np.where(n%101<50,1.,-.5),np.sin(n*.283)))
    one,s1=process(old,signal,CANONICAL);two,s2=process(old,signal,ALTERNATE)
    dc,_=process(np.zeros_like(old),np.ones_like(old),CANONICAL)
    nyquist=np.repeat(((-1.)**n)[:,None],2,axis=1);ny,_=process(np.zeros_like(old),nyquist,CANONICAL)
    zero,_=process(old,np.zeros_like(old),CANONICAL)
    result={'cutoff_hz':200,'pole':a,'b':b,'stable':0<a<1,'algebraic_DC_gain':0.,'algebraic_Nyquist_gain':2*b/(1+a),
      'measured_DC_tail_max':float(np.max(abs(dc[-1024:,:2]))),'measured_Nyquist_tail_max_error':float(np.max(abs(ny[-1024:,:2]-nyquist[-1024:]))),
      'chunk_output_bitidentity':one.tobytes()==two.tobytes(),'chunk_state_bitidentity':s1.tobytes()==s2.tobytes(),
      'zero_counter_baseline_identity':zero[:,2:4].tobytes()==zero[:,4:6].tobytes()}
    result['pass']=bool(result['stable'] and abs(result['algebraic_Nyquist_gain']-1)<1e-14 and result['measured_DC_tail_max']<1e-12 and result['measured_Nyquist_tail_max_error']<1e-12 and result['chunk_output_bitidentity'] and result['chunk_state_bitidentity'] and result['zero_counter_baseline_identity'])
    return result

def freeze():
    if (OUT/'protocol.json').exists():raise ValueError('Already frozen')
    if sha(V2/'result.json')!='7bbdd9f7f664e770040641c6faed8955176d89b79ec13c88c648ad5081bac4f6':raise ValueError('Full counterterm pilot changed')
    old=read(V2/'protocol.json');result=read(V2/'result.json');outcomes={c['id']:c for c in result['cases']}
    if not all(all(c['numeric_guards'].values()) for c in result['cases']):raise ValueError('v2 numerical source invalid')
    cases=[]
    for c in old['cases']:
        ident=c['id'];d=V2/'renders'/ident
        cases.append({**c,'full_observer':rec(d/'observer.f64le'),'full_numeric':rec(d/'numeric.json'),
          'full_numerical_proof':{'all_guards_pass':True,'C_rad_prefix_matches_v1':outcomes[ident]['numeric_guards']['C_rad_prefix_exact'],'counterterm_pressure_is_full':True}})
    inputs=[V1/'run.py',V1/'protocol.json',V1/'result.json',V2/'run.py',V2/'replay.cpp',V2/'protocol.json',V2/'result.json',V2/'manifest.json']+[Path(x['path']) for x in old['inputs']]
    p={'schema_version':1,'frozen_at_utc':now(),'scope':'One fixed200Hz LF-protected FULLgamma100 pressurecounterterm. Post-hoc TRAIN engineering based on previously observed31–250Hz preservation errors and C3 ring budget, not new validation or identified physical-part evidence.',
       'new_candidate_pressure_opened':False,'sources':[rec(OUT/'filter.cpp'),rec(OUT/'run.py')],'inputs':[rec(x) for x in dict.fromkeys(inputs)],'cases':cases,
       'rate':RATE,'frames':FRAMES,'gamma_per_second':100,'cutoff_hz':200,'cutoff_variants':1,'gamma_variants':1,'strength_variants':1,'strength':1,
       'operator':'h200[n]=a*h200[n-1]+b*(fullFastRaw[n]-fullFastRaw[n-1]); rawCandidate=rawOld-h200; originalHP24 from frame0, thenfloat32. a=(1-tan(pi200/fs))/(1+tan(...)), b=1/(1+tan(...)). Identical LRfilter, zero initialstate.',
       'canonical_partition':CANONICAL,'alternate_partition':ALTERNATE,'controls':'SyntheticDCzero/Nyquistunity/stablepole/chunkoutput+finalstatebitidentity/zerocounterbaselineidentity beforecandidate; everyactualcase bothpartitions byteequal; reconstructedoldHP24f32equalsoldbaselinepayload.',
       'source_scope':'Reuse v2 full counterterm and original rawOld, authenticated sourceforces and numerical proofs. No full network replay or new nonlinear contact solve. Physical source mechanics unchanged; only this observation differs.',
       'original_gates':old['original_gates'],'gate_arithmetic_sha256':old['gate_arithmetic_sha256'],'fixed_gains_onsets_masks':True,
       'no_tuning_sweep':True,'fit_runs':0,'new_reference_PCM_access':False,'listening_exported':False,'adopted':False,
       'trace_columns':['HP200_counterL','HP200_counterR','baselineHP24L','baselineHP24R','candidateHP24L','candidateHP24R','counterHP24L','counterHP24R','candidateRawL','candidateRawR'],
       'log_policy':'Live outerrun.log excluded from manifest; no process writer retains other outputfiles aftermanifest.',
       'limitations':['All six are previously observed TRAIN.','A six-case pass only motivates a separately frozen full-range confirmation and listening; no runtime/default promotion.','Fixed200Hz selection is posthoc engineering, not measured wood/air/microphone physics.','The fullstate upstream counterterm remains an offline quality proof requiring a cheaper realization.']}
    write(OUT/'protocol.json',p);write(OUT/'freeze.json',{'protocol':rec(OUT/'protocol.json'),'sources':p['sources'],'frozen_at_utc':p['frozen_at_utc']})

def execute():
    p=read(OUT/'protocol.json');frozen=read(OUT/'freeze.json');case_inputs=[x for c in p['cases'] for x in [c['trace'],c['force_proof'],c['baseline_audio'],c['full_observer'],c['full_numeric'],c['v1_baseline_payload']]]
    identities=[frozen['protocol'],*p['sources'],*p['inputs'],*case_inputs];verify(identities)
    if (OUT/'opening-started.json').exists():raise ValueError('Once-only fixedcorner run already started')
    write(OUT/'opening-started.json',{'started_at_utc':now(),'protocol':rec(OUT/'protocol.json'),'new_candidate_pressure_opened':False})
    tick=time.monotonic();process,compiler=compile_filter();checks=synthetic(process);write(OUT/'synthetic.json',checks)
    if not checks['pass']:raise ValueError('Synthetic filter checks failed')
    metric,gate,gate_sha=base.tools()
    if gate_sha!=p['gate_arithmetic_sha256']:raise ValueError('Original gates changed')
    refs={x['id']:x for x in read(base.REF)['cases']};rows={x['id']:x for x in read(base.FEATURES)['samples']};outcomes=[]
    for c in p['cases']:
        ident=c['id'];original=np.memmap(c['trace']['path'],mode='r',dtype='<f8',shape=(FRAMES,15));full=np.memmap(c['full_observer']['path'],mode='r',dtype='<f8',shape=(FRAMES,23))
        old=np.ascontiguousarray(original[:,:2]);counter=np.ascontiguousarray(full[:,:2]);value,state=process(old,counter,CANONICAL);alternate,otherstate=process(old,counter,ALTERNATE)
        partitions=value.tobytes()==alternate.tobytes() and state.tobytes()==otherstate.tobytes()
        if not partitions:raise ValueError('Actual partitions differ '+ident)
        baseline=value[:,2:4].astype('<f4');candidate=value[:,4:6].astype('<f4');sr,history=wavfile.read(c['baseline_audio']['path'])
        baseline_exact=sr==RATE and history.dtype==np.float32 and baseline.tobytes()==history.astype('<f4').tobytes() and baseline.tobytes()==Path(c['v1_baseline_payload']['path']).read_bytes()
        if not baseline_exact or not np.isfinite(candidate).all():raise ValueError('Baseline/finiteness '+ident)
        d=OUT/'renders'/ident;d.mkdir(parents=True,exist_ok=False);value.astype('<f8').tofile(d/'observer.f64le');wavfile.write(d/'candidate.wav',RATE,candidate)
        features=metric.observation_features(candidate.astype(float),c['fixed_onset_frame'],c['fixed_gain'],refs[ident]['reference'],rows[ident]);scored=gate(refs[ident],features,ident,baseline_exact,{ident:c['source_proof']})
        onset=c['fixed_onset_frame'];tail=value[onset+12000:,6:8];sustain=baseline[onset+12000:onset+36000].astype(float);rms=float(np.sqrt(np.mean(tail*tail)));base_rms=float(np.sqrt(np.mean(sustain*sustain)))
        outcome={'id':ident,'candidate_audio':rec(d/'candidate.wav'),'candidate':features,**scored,'postprocessor':{'partitions_byte_identical':partitions,'finite':True,'baseline_HP_payload_exact':baseline_exact,'final_state':state.tolist(),'sample_peak':float(np.max(abs(candidate)))},
         'tail':{'HP_RMS_after250ms':rms,'HP_peak_after250ms':float(np.max(abs(tail))),'HP_relative_old_sustain_RMS_db':20*math.log10(max(rms,1e-300)/max(base_rms,1e-300))},'source_proof':c['source_proof'],'source_scope':p['source_scope'],'adopted':False}
        outcomes.append(outcome);write(d/'result.json',outcome);print(ident,'PASS' if outcome['passes_all_case_gates'] else 'FAIL',outcome['gates'],flush=True)
    verify(identities)
    r={'completed_at_utc':now(),'protocol':rec(OUT/'protocol.json'),'compiler':compiler,'synthetic':checks,'cases':outcomes,'case_count':6,'cases_passing_all_original_gates':sum(c['passes_all_case_gates'] for c in outcomes),'passes_all_original_gates':all(c['passes_all_case_gates'] for c in outcomes),'wall_seconds':time.monotonic()-tick,'gamma_per_second':100,'cutoff_hz':200,'cutoff_variants':1,'gamma_variants':1,'fit_runs':0,'full_network_replays':0,'new_reference_PCM_access':False,'adopted':False,'limitations':p['limitations']}
    write(OUT/'result.json',r);print('FIXED HP200 PILOT',r['cases_passing_all_original_gates'],'/6 pass',flush=True)
    manifest={str(f.relative_to(OUT)):{'sha256':sha(f),'bytes':f.stat().st_size} for f in sorted(OUT.rglob('*')) if f.is_file() and f.name not in ('manifest.json','run.log') and '__pycache__' not in f.parts};write(OUT/'manifest.json',manifest)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['freeze','run']);args=parser.parse_args()
    if args.command=='freeze':freeze();return
    try:execute()
    except Exception as e:
        if not (OUT/'failure.json').exists():write(OUT/'failure.json',{'failed_at_utc':now(),'error_type':type(e).__name__,'error':str(e),'traceback':traceback.format_exc(),'silently_retried':False})
        raise
if __name__=='__main__':main()
