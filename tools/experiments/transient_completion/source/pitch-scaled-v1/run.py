#!/usr/bin/env python3
"""One authored pitch-scaled companion family with unchanged fixed HP200."""
from pathlib import Path
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import argparse,ctypes,importlib.util,math,subprocess,time,traceback
import numpy as np
from scipy.io import wavfile

OUT=Path(__file__).resolve().parent;PARENT=OUT.parent;V1=PARENT/'v1';V2=PARENT/'v2';LF=PARENT/'lf-protected-v1'
def module(path,name):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
base=module(V1/'run.py','pitch_frozen_base');protect=module(LF/'run.py','pitch_frozen_HP200')
ROOT=base.ROOT;sha=base.sha;read=base.read;rec=base.rec;write=base.write;verify=base.verify;now=base.now
RATE=48000;FRAMES=182400

def compile_filter():
    destination=OUT/'filter.so';cmd=['g++','-std=c++17','-O3','-fno-builtin','-ffp-contract=off','-shared','-fPIC',str(OUT/'filter.cpp'),'-o',str(destination)]
    subprocess.run(cmd,check=True);library=ctypes.CDLL(str(destination));function=library.keyra_protect_counter
    pointer=np.ctypeslib.ndpointer(dtype=np.float64,flags='C_CONTIGUOUS');function.argtypes=[pointer,pointer,pointer,ctypes.c_size_t,pointer];function.restype=ctypes.c_int
    def process(old,fast,chunks):
        old=np.ascontiguousarray(old,dtype=np.float64);fast=np.ascontiguousarray(fast,dtype=np.float64);output=np.empty((len(old),10));state=np.zeros(16);offset=0;block=0
        while offset<len(old):
            stop=min(len(old),offset+chunks[block%len(chunks)])
            if function(old[offset:stop],fast[offset:stop],output[offset:stop],stop-offset,state):raise ValueError('Nonfinite fixedfilter')
            offset=stop;block+=1
        return output,state
    return process,{'command':cmd,'binary':rec(destination)}

def freeze():
    if (OUT/'protocol.json').exists():raise ValueError('Already frozen')
    expected_prefix=(V2/'replay.cpp').read_bytes().split(b'\nint main(int argc,char** argv) {')[0]+b'\n'
    if (OUT/'mechanics_v2_prefix.h').read_bytes()!=expected_prefix:raise ValueError('Mechanics prefix differs')
    if sha(OUT/'filter.cpp')!='8859dbbebac6e54fe1a5e4c93dfb420b1fc91f0ef51f204ae2ebb8c93d5616cd':raise ValueError('FixedHP200changed')
    if sha(LF/'result.json')!='217559fb70e03818784f6bcee702b45688ec270aef8d049249bb74f1470aff4b':raise ValueError('Priorposthocinputchanged')
    old=read(LF/'protocol.json');inputs=[LF/'protocol.json',LF/'result.json',LF/'run.py',V2/'replay.cpp',V2/'protocol.json',V2/'result.json',V1/'replay.cpp']+[Path(x['path']) for x in old['inputs']]
    sources=[rec(OUT/x) for x in ['replay.cpp','mechanics_v2_prefix.h','filter.cpp','run.py']]
    p={'schema_version':1,'frozen_at_utc':now(),'scope':'One posthoc authored smooth pitch-scaled memory family, no alternate law/parameter fitting. Not measured propagation or a newly identified piano mechanism. Six already observed TRAIN witnesses.',
      'new_pitch_candidate_opened':False,'sources':sources,'inputs':[rec(x) for x in dict.fromkeys(inputs)],'cases':old['cases'],'rate':RATE,'frames':FRAMES,
      'pitch_law':'For ALL88keys, gamma_key=100*max(1,f0_key/f0_C3) from SAME prepared five-anchor model; every string/choir line of that key gets exp(-gamma_key/fs) on BOTH prior q/p. Bodygamma100. No per-note exception and no per-event age gain.',
      'matrix_scope':'A_fast=A*D_rho nominally; D is nonuniform and does NOT commute with bridge coupling. Do NOT claim (1-rho^age)h_total identity. D contracts energy with minimumgamma100, leaving original physical poles/readout untouched while this observer fades.',
      'uniform_control':'The SAME new scaling routine with all-key gamma100 reproduces v2 full raw pressure BITEXACT through fixed old onset+.25s for all six. Includes inactive zero-state scan optimization, never repeats full3.8s rho1control.',
      'body_and_force':'Same full pressure readout, own unison/bridge, unmodified solved contact force only; no recorded bridge-force drive. Reuse v2 K_dynamic+||DmicM^-1S_force||2 PREstep zero-input bound and1e-20 companion-only retirement; HP memory untouched.',
      'minimum_gamma':100,'body_gamma':100,'pitch_law_variants':1,'cutoff_hz':200,'corner_variants':1,'strength':1,'fit_runs':0,
      'postprocessor':'Identical fixed HP200 code SHA8859…; rawCandidate=rawOld-HP200(fullFastPitch); originalHP24fromframe0 thenfloat32, same LR filter.',
      'canonical_partition':[64],'alternate_partition':[1,3,17,64,129,7],'synthetic':'Pitch-companion energybound/retire/later-force wake; unchanged HP200 DC/Nyquist/stability/zero-counter/partition tests beforeactualscoring.',
      'original_gates':old['original_gates'],'gate_arithmetic_sha256':old['gate_arithmetic_sha256'],'old_gains_onsets_masks_unchanged':True,
      'compile':['g++','-std=c++17','-O3','-DNDEBUG','-fno-builtin','-ffp-contract=off',str(OUT/'replay.cpp'),'-o',str(OUT/'replay')],
      'fast_trace_columns':['fastFullL','fastFullR','fastCradL','fastCradR','fastBoardL','fastBoardR','fastBoardForceL','fastBoardForceR','energyPost','energyPre','futureZeroFBound','contactF','recoveredOwnSchur0','recoveredOwnSchur1','recoveredOwnSchur2'],
      'log_policy':'Closedproducer.logindexed, liveouterrun.logexcluded.','adopted':False,'new_reference_PCM_access':False,'new_nonlinear_contact_source_render':False,'listening_exported':False,
      'limitations':['Posthoc TRAINengineering, not generalization or measured wave-travel identification.','Fullstate companion remains an offline proof requiring a cheaper realization.','Passed six-case metrics alone cannot promote runtime/default or prove audibility.']}
    write(OUT/'protocol.json',p);write(OUT/'freeze.json',{'protocol':rec(OUT/'protocol.json'),'sources':sources,'frozen_at_utc':p['frozen_at_utc']})

def execute():
    p=read(OUT/'protocol.json');f=read(OUT/'freeze.json');case_inputs=[item for c in p['cases'] for item in (c['trace'],c['force_proof'],c['baseline_audio'],c['full_observer'],c['v1_baseline_payload'])];identities=[f['protocol'],*p['sources'],*p['inputs'],*case_inputs];verify(identities)
    if (OUT/'opening-started.json').exists():raise ValueError('Once-only pitchfamily alreadystarted')
    write(OUT/'opening-started.json',{'started_at_utc':now(),'protocol':rec(OUT/'protocol.json'),'new_pitch_pressure_opened':False})
    start=time.monotonic();subprocess.run(p['compile'],check=True);process,filter_build=compile_filter();filter_tests=protect.synthetic(process);write(OUT/'filter-synthetic.json',filter_tests)
    if not filter_tests['pass']:raise ValueError('UnchangedHP200syntheticfailed')
    output=OUT/'renders';output.mkdir(exist_ok=False)
    for c in p['cases']:(output/c['id']).mkdir()
    tsv=OUT/'cases.tsv';tsv.write_text(''.join('\t'.join([c['id'],str(c['midi']),c['trace']['path'],str(c['fixed_onset_frame']),c['force_proof']['path'],c['full_observer']['path']])+'\n' for c in p['cases']))
    cmd=[str(OUT/'replay'),str(tsv),str(output)];write(OUT/'producer-freeze.json',{'created_at_utc':now(),'protocol':rec(OUT/'protocol.json'),'binary':rec(OUT/'replay'),'case_tsv':rec(tsv),'command':cmd})
    with (OUT/'producer.log').open('x') as log:
        job=subprocess.Popen(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        for line in job.stdout:log.write(line);log.flush();print(line,end='',flush=True)
        status=job.wait()
    if status:raise ValueError('Pitchproducerexit'+str(status))
    cold=read(output/'bound-and-gamma.json');synthetic=read(output/'synthetic.json')
    if not synthetic['retired'] or not synthetic['wake_identity'] or synthetic['max_free_energy_ratio']>1 or synthetic['max_zero_force_pressure_over_bound']>1 or synthetic['faults']:raise ValueError('Pitchsyntheticguard')
    metric,gate,gate_sha=base.tools()
    if gate_sha!=p['gate_arithmetic_sha256']:raise ValueError('Gatechanged')
    refs={x['id']:x for x in read(base.REF)['cases']};rows={x['id']:x for x in read(base.FEATURES)['samples']};outcomes=[]
    for c in p['cases']:
        ident=c['id'];d=output/ident;numeric=read(d/'numeric.json')
        guards={'uniform_prefix_bitexact':numeric['uniform_full_pressure_nonidentical_samples']==0 and numeric['uniform_full_pressure_max_error']==0,'uniform_faults':numeric['uniform_control_faults']==0,
          'force':numeric['force_contract_errors']==numeric['force_proof_mismatches']==0,'finite':numeric['nonfinite']==0,'faults':numeric['faults']==0,'scale_energy':numeric['max_positive_scale_energy']==0,
          'free_energy':numeric['max_free_energy_ratio']<=1,'full_bound':numeric['max_zero_force_pressure_over_bound']<=1,'retirement':numeric['retirements']>=1 and numeric['discarded_future_bound']<=1e-20,
          'counts':numeric['mode_count']==17778 and numeric['strings']==230 and numeric['board_modes']==475}
        if not all(guards.values()):raise ValueError('Pitchnumericguard'+ident+str(guards))
        original=np.memmap(c['trace']['path'],dtype='<f8',mode='r',shape=(FRAMES,15));fast=np.memmap(d/'fast.f64le',dtype='<f8',mode='r',shape=(FRAMES,15));old=np.ascontiguousarray(original[:,:2]);counter=np.ascontiguousarray(fast[:,:2])
        value,state=process(old,counter,p['canonical_partition']);alternative,other=process(old,counter,p['alternate_partition']);partitions=value.tobytes()==alternative.tobytes() and state.tobytes()==other.tobytes()
        baseline=value[:,2:4].astype('<f4');candidate=value[:,4:6].astype('<f4');sr,historical=wavfile.read(c['baseline_audio']['path']);exact=sr==RATE and historical.dtype==np.float32 and baseline.tobytes()==historical.astype('<f4').tobytes() and baseline.tobytes()==Path(c['v1_baseline_payload']['path']).read_bytes()
        if not partitions or not exact or not np.isfinite(candidate).all():raise ValueError('Pitchfilterguard'+ident)
        value.tofile(d/'filtered.f64le');wave=d/'candidate.wav';wavfile.write(wave,RATE,candidate)
        features=metric.observation_features(candidate.astype(float),c['fixed_onset_frame'],c['fixed_gain'],refs[ident]['reference'],rows[ident]);scored=gate(refs[ident],features,ident,exact,{ident:c['source_proof']})
        onset=c['fixed_onset_frame'];tail=value[onset+12000:,6:8];sustain=baseline[onset+12000:onset+36000].astype(float);rms=float(np.sqrt(np.mean(tail*tail)));base_rms=float(np.sqrt(np.mean(sustain*sustain)))
        outcome={'id':ident,'candidate_audio':rec(wave),'candidate':features,**scored,'numeric':numeric,'numeric_guards':guards,'postprocessor':{'partition_bytes_exact':partitions,'baseline_HP_payload_exact':exact,'final_state':state.tolist()},
          'tail':{'HP_RMS_after250ms':rms,'HP_peak_after250ms':float(np.max(abs(tail))),'HP_relative_old_sustain_RMS_db':20*math.log10(max(rms,1e-300)/max(base_rms,1e-300))},'source_proof':c['source_proof'],'adopted':False}
        outcomes.append(outcome);write(d/'result.json',outcome);print(ident,'PASS' if outcome['passes_all_case_gates'] else 'FAIL',outcome['gates'],flush=True)
    verify(identities)
    result={'completed_at_utc':now(),'protocol':rec(OUT/'protocol.json'),'producer_freeze':rec(OUT/'producer-freeze.json'),'filter_build':filter_build,'filter_synthetic':filter_tests,'pitch_synthetic':synthetic,'cold_bound_gamma':cold,'cases':outcomes,
      'case_count':6,'cases_passing_all_original_gates':sum(c['passes_all_case_gates'] for c in outcomes),'passes_all_original_gates':all(c['passes_all_case_gates'] for c in outcomes),'wall_seconds':time.monotonic()-start,
      'minimum_gamma':100,'body_gamma':100,'pitch_law_variants':1,'cutoff_hz':200,'cutoff_variants':1,'fit_runs':0,'new_reference_PCM_access':False,'full_companion_force_replays':6,'uniform_control_prefix_replays':6,'adopted':False,'limitations':p['limitations']}
    write(OUT/'result.json',result);print('PITCHMEMORY PILOT',result['cases_passing_all_original_gates'],'/6 pass',flush=True)
    manifest={str(x.relative_to(OUT)):{'sha256':sha(x),'bytes':x.stat().st_size} for x in sorted(OUT.rglob('*')) if x.is_file() and x.name not in ('manifest.json','run.log') and '__pycache__' not in x.parts};write(OUT/'manifest.json',manifest)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['freeze','run']);a=parser.parse_args()
    if a.command=='freeze':freeze();return
    try:execute()
    except Exception as e:
        if not (OUT/'failure.json').exists():write(OUT/'failure.json',{'failed_at_utc':now(),'error_type':type(e).__name__,'error':str(e),'traceback':traceback.format_exc(),'silently_retried':False})
        raise
if __name__=='__main__':main()
