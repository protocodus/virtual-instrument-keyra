#!/usr/bin/env python3
"""Single full-pressure fast-companion followup; same gamma100, no fit."""
from pathlib import Path
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import argparse,hashlib,importlib.util,json,math,subprocess,time,traceback
import numpy as np
from scipy.io import wavfile

OUT=Path(__file__).resolve().parent;V1=OUT.parent/'v1'
spec=importlib.util.spec_from_file_location('frozen_transient_v1',V1/'run.py');base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
ROOT=base.ROOT;sha=base.sha;read=base.read;rec=base.rec;write=base.write;verify=base.verify;now=base.now
RATE=48000;FRAMES=182400

def freeze():
    if (OUT/'protocol.json').exists():raise ValueError('Already frozen')
    if sha(V1/'result.json')!='d408e83dc6ab713c8da6e242b0cc76a5714d6fc6d181b57720f64f21c534b998':raise ValueError('Original pilot changed')
    old=read(V1/'protocol.json');result=read(V1/'result.json');outcomes={c['id']:c for c in result['cases']}
    if not all(all(c['numeric_guards'].values()) for c in result['cases']):raise ValueError('v1 numeric baseline not qualified')
    inputs=[V1/'result.json',V1/'protocol.json',V1/'freeze.json',V1/'manifest.json',V1/'replay.cpp',V1/'run.py']+[Path(x['path']) for x in old['inputs']]
    cases=[]
    for c in old['cases']:
        ident=c['id'];d=V1/'renders'/ident;o=outcomes[ident]
        cases.append({**c,'v1_observer':rec(d/'observer.f64le'),'v1_numeric':rec(d/'numeric.json'),'v1_baseline_payload':rec(d/'baseline.f32le'),
          'v1_retirement_frame':o['numeric']['retirement_frame'],'v1_discarded_bound':o['numeric']['discarded_pressure_bound'],
          'v1_control':{'rawOld_bitexact':o['numeric_guards']['rho1_raw_bitexact'],'rawBoard_bitexact':o['numeric_guards']['rho1_board_bitexact'],'HP_payload_exact':o['numeric_guards']['baseline_HP_payload'],
           'scope':'Inherited full rho1 mechanical force-replay control from v1; not repeated here. Same private v1 dynamics helpers are included verbatim and C_rad replay is checked until its former quiescence.'}})
    sources=[rec(OUT/'replay.cpp'),rec(OUT/'run.py')]
    p={'schema_version':1,'frozen_at_utc':now(),'scope':'One full-PRESSURE fast contact-companion followup, same gamma100 as rejected C_rad-only v1. No fit/gamma sweep/reference PCM/core/listening/default changes.',
       'new_fullpressure_candidate_opened':False,'sources':sources,'inputs':[rec(p) for p in dict.fromkeys(inputs)],'cases':cases,
       'rate':RATE,'frames':FRAMES,'gamma_per_second':100,'rho':math.exp(-100/48000),
       'operator':'candidateRaw=recordedRawOld-full(fast); full(fast)=its own board pressure plus per-string C_rad cached readout in original summation order. All old captured mechanics/forces untouched. Full body RADIATION observation is now modified by the counterterm.',
       'dynamics':'Include frozen v1 replay.cpp helpers byte-for-byte. Scale only old fast string+board coordinates by rho BEFORE free update, unmodified solved contact F injection, own unison+own Schur. No original Schur drive; captured bridge fields are proof-only.',
       'full_future_bound':{'K_dynamic':'sqrt(sum_string[(radQ/omega)^2+(radP/omega)^2]+sum_board[mic^2*(omega^2+4sigma^2)]) perchannel',
         'S_force':'Energy-normalized prebridge p coefficients: string_i,j= -alpha_i*(portOmega_j/omega_j) in its group; board_m=beta_g*port_mg. alpha_i=r_i/(1+dt*r_i*compliance_i/2); beta_g=sumalpha_i.',
         'M':'I+dt/2*diag(beta)*boardGram; Dmic_ch,g=-sum_board mic_ch*port_g',
         'K_force':'norm2(Dmic_ch * inverse(M) * S_force), evaluated exactly by its explicit string/board coefficient norm.',
         'K':'K_dynamic+K_force perchannel. Physical free rotation/unison/bridge are passive nominally; use factor2 numerical margin.',
         'quiescence':'When F==0 and 2*max(K)*sqrt(2E_PREstep)<=1e-20, clear only companion coordinates/cache/old force BEFORE next update; previous output was already retained. HP states never clear, any later nonzero F wakes from zero. Current input force feedthrough is never erased after output.',
         'numerical_qualification':'Record M and inverse Frobenius norms, all observed zero-F full-pressure/bound ratios, free energy ratios, finite/fault guards, and later-force synthetic wake identity. Bound is a conservative model/numerical engineering bound, not a new measured piano part.'},
       'controls':{'v1_reuse':True,'C_rad_before_v1_retirement':'All double C_rad samples must be bitidentical to v1 before its retirement frame.',
         'C_rad_after_v1_retirement':'Magnitude must remain <= v1 discarded pressure bound; no source/dynamics difference is hidden at the below1e-20 tail.',
         'HP_baseline':'HP24(rawOld) float32 payload must match both historical baseline WAV and v1 payload.',
         'force':'Full91force FNV bothbefore/after archived proof rows, frameindices, selectedcontactF finite/nonnegative/precontactzero/after40mszero.',
         'force_log':'Store separate full/Crad/board/force-only-board pressures and ownSchur3 recovered from boardGram^-1*(-sum port*modalForce). Recovered values are diagnostics, not original driving inputs.'},
       'original_gates':old['unchanged_original_gates'],'gate_arithmetic_sha256':old['gate_arithmetic_sha256'],
       'unchanged':{'gamma':True,'fixed_old_gains_onsets':True,'reference_masks':True,'six_training_witnesses':True},
       'trace_columns':['fast_fullL','fast_fullR','fast_CradL','fast_CradR','fast_boardL','fast_boardR','fast_board_forceL','fast_board_forceR','baselineHPL','baselineHPR','candidateHPL','candidateHPR','fast_fullHPL','fast_fullHPR','energyPost','energyPre','futureZeroFBound','contactF','candidateRawL','candidateRawR','recoveredOwnSchur0','recoveredOwnSchur1','recoveredOwnSchur2'],
       'compile':['g++','-std=c++17','-O3','-DNDEBUG','-fno-builtin','-ffp-contract=off',str(OUT/'replay.cpp'),'-o',str(OUT/'replay')],
       'log_policy':'Closed producer.log is indexed. Live outer run.log excluded intentionally.',
       'adopted':False,'fit_runs':0,'new_nonlinear_contact_source_renders':0,'full_companion_force_replays':6,'rho1_control_replays_repeated':0}
    write(OUT/'protocol.json',p);write(OUT/'freeze.json',{'frozen_at_utc':p['frozen_at_utc'],'protocol':rec(OUT/'protocol.json'),'sources':sources})

def execute():
    p=read(OUT/'protocol.json');frozen=read(OUT/'freeze.json')
    case_inputs=[item for c in p['cases'] for item in (c['trace'],c['force_proof'],c['baseline_audio'],c['v1_observer'],c['v1_numeric'],c['v1_baseline_payload'])]
    identities=[frozen['protocol'],*p['sources'],*p['inputs'],*case_inputs]
    verify(identities)
    if (OUT/'opening-started.json').exists():raise ValueError('Once-only fullpressure run already started')
    write(OUT/'opening-started.json',{'started_at_utc':now(),'freeze':rec(OUT/'freeze.json'),'new_pressure_opened':False})
    start=time.monotonic();subprocess.run(p['compile'],check=True)
    output=OUT/'renders';output.mkdir(exist_ok=False)
    for c in p['cases']:(output/c['id']).mkdir()
    tsv=OUT/'cases.tsv';tsv.write_text(''.join('\t'.join([c['id'],str(c['midi']),c['trace']['path'],str(c['fixed_onset_frame']),c['force_proof']['path'],c['v1_observer']['path'],str(c['v1_retirement_frame']),repr(c['v1_discarded_bound'])])+'\n' for c in p['cases']))
    command=[str(OUT/'replay'),str(tsv),str(output)]
    write(OUT/'producer-freeze.json',{'protocol':rec(OUT/'protocol.json'),'binary':rec(OUT/'replay'),'case_tsv':rec(tsv),'command':command,'created_at_utc':now()})
    with (OUT/'producer.log').open('x') as log:
        process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        for line in process.stdout:log.write(line);log.flush();print(line,end='',flush=True)
        code=process.wait()
    if code:raise ValueError('Producer exit '+str(code))
    synthetic=read(output/'synthetic.json');bound=read(output/'bound.json')
    if not synthetic['retired'] or not synthetic['wake_identity'] or synthetic['max_free_energy_ratio']>1 or synthetic['max_zero_force_pressure_over_bound']>1 or synthetic['faults']:raise ValueError('Synthetic fullbound/wake failed')
    metric,gate,gate_sha=base.tools()
    if gate_sha!=p['gate_arithmetic_sha256']:raise ValueError('Changed gate')
    refs={x['id']:x for x in read(base.REF)['cases']};rows={x['id']:x for x in read(base.FEATURES)['samples']};outcomes=[]
    for c in p['cases']:
        ident=c['id'];d=output/ident;numeric=read(d/'numeric.json');sr,historical=wavfile.read(c['baseline_audio']['path'])
        baseline=np.fromfile(d/'baseline.f32le',dtype='<f4').reshape((FRAMES,2));candidate=np.fromfile(d/'candidate.f32le',dtype='<f4').reshape((FRAMES,2))
        baseline_exact=sr==RATE and historical.dtype==np.float32 and baseline.tobytes()==historical.astype('<f4').tobytes() and baseline.tobytes()==Path(c['v1_baseline_payload']['path']).read_bytes()
        numeric_guards={'baseline_HP_exact':baseline_exact,'C_rad_prefix_exact':numeric['rad_nonidentical_samples_before_v1_retirement']==0,'C_rad_after_v1_bound':numeric['rad_post_v1_bound_errors']==0,
          'force':numeric['force_contract_errors']==numeric['force_proof_mismatches']==0,'finite':numeric['nonfinite']==0 and bool(np.isfinite(candidate).all()),'faults':numeric['faults']==0,
          'scale_energy':numeric['max_positive_scale_energy']==0,'free_energy':numeric['max_free_energy_ratio']<=1,'full_pressure_bound':numeric['max_zero_force_pressure_over_bound']<=1,
          'retirement':numeric['retirements']>=1 and numeric['discarded_future_pressure_bound']<=1e-20,'counts':numeric['mode_count']==17778 and numeric['strings']==230 and numeric['board_modes']==475}
        if not all(numeric_guards.values()):raise ValueError('Numerical guard '+ident+str(numeric_guards))
        wave=d/'candidate.wav';wavfile.write(wave,RATE,candidate)
        features=metric.observation_features(candidate.astype(float),c['fixed_onset_frame'],c['fixed_gain'],refs[ident]['reference'],rows[ident]);scored=gate(refs[ident],features,ident,baseline_exact,{ident:c['source_proof']})
        observer=np.memmap(d/'observer.f64le',dtype='<f8',mode='r',shape=(FRAMES,23));onset=c['fixed_onset_frame'];tail=np.asarray(observer[onset+12000:,12:14]);sustain=baseline[onset+12000:onset+36000].astype(float)
        rms=float(np.sqrt(np.mean(tail*tail)));base_rms=float(np.sqrt(np.mean(sustain*sustain)))
        outcome={'id':ident,'candidate_audio':rec(wave),'candidate':features,**scored,'numeric':numeric,'numeric_guards':numeric_guards,'v1_control':c['v1_control'],'source_proof':c['source_proof'],
          'fast_tail':{'HP_RMS_after_250ms':rms,'HP_peak_after_250ms':float(np.max(abs(tail))),'HP_relative_old_sustain_RMS_db':20*math.log10(max(rms,1e-300)/max(base_rms,1e-300)),
            'late_float32_different_samples':int(np.count_nonzero(candidate[onset+12000:].view('<u4')!=baseline[onset+12000:].view('<u4')))},'adopted':False}
        outcomes.append(outcome);write(d/'result.json',outcome);print(ident,'PASS' if outcome['passes_all_case_gates'] else 'FAIL',outcome['gates'],flush=True)
    verify(identities)
    result={'completed_at_utc':now(),'protocol':rec(OUT/'protocol.json'),'producer_freeze':rec(OUT/'producer-freeze.json'),'bound':bound,'synthetic':synthetic,'cases':outcomes,
      'cases_passing_all_original_gates':sum(c['passes_all_case_gates'] for c in outcomes),'passes_all_original_gates':all(c['passes_all_case_gates'] for c in outcomes),'case_count':6,'wall_seconds':time.monotonic()-start,
      'gamma_per_second':100,'gamma_variants':1,'fit_runs':0,'new_reference_PCM_access':False,'new_nonlinear_contact_source_renders':0,'full_companion_force_replays':6,'rho1_replays_repeated':0,'adopted':False,
      'scope':'Original captured mechanics unchanged. This FULLpressure observation counterterm modifies board radiation as well as empirical string radiation. It is a full-state offline proof, not realtime architecture or an identified piano part.'}
    write(OUT/'result.json',result);print('FULLPRESSURE PILOT',result['cases_passing_all_original_gates'],'/6 pass',flush=True)
    manifest={str(f.relative_to(OUT)):{'sha256':sha(f),'bytes':f.stat().st_size} for f in sorted(OUT.rglob('*')) if f.is_file() and f.name not in ('manifest.json','run.log') and '__pycache__' not in f.parts};write(OUT/'manifest.json',manifest)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['freeze','run']);args=parser.parse_args()
    if args.command=='freeze':freeze();return
    try:execute()
    except Exception as e:
        if not (OUT/'failure.json').exists():write(OUT/'failure.json',{'failed_at_utc':now(),'error_type':type(e).__name__,'error':str(e),'traceback':traceback.format_exc(),'silently_retried':False})
        raise
if __name__=='__main__':main()
