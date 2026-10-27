#!/usr/bin/env python3
"""One frozen contact-only transient-companion pilot; no reference PCM access."""
from pathlib import Path
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import argparse,datetime,hashlib,importlib.util,json,math,subprocess,sys,time,traceback
import numpy as np
from scipy.io import wavfile

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
IDS=('C3v4','C3v12','C4v4','C4v12','C6v4','C6v12')
OLD=ROOT/'out/full-causal-radiation/v1'
REF=ROOT/'out/full-causal-radiation-metrics/v1/reference-control.json'
BINDING=ROOT/'out/full-body-basis/v1/input-bindings.json'
METRIC=ROOT/'tools/probe_full_causal_radiation_metrics.py'
GATE=ROOT/'out/full-radiation-crossover/v1/postprocess.py'
FEATURES=ROOT/'References/GrandFullRange/combined_train_features.json'
MODEL=ROOT/'tools/experiments/causal_radiation_pilot/producer/original_core/src/full_instrument/PreparedModel.h'
CAL=MODEL.with_name('PreparedCalibration.h')
RATE=48000;FRAMES=182400

def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def rec(p):return {'path':str(Path(p).resolve()),'sha256':sha(p)}
def write(p,v):
    p=Path(p)
    if p.exists():raise ValueError('Refuse overwriting '+str(p))
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
def verify(rows):
    for r in rows:
        if sha(r['path'])!=r['sha256']:raise ValueError('Changed frozen input '+r['path'])
def module(p,name):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def tools():
    metric=module(METRIC,'transient_original_metric')
    operator=module(GATE,'transient_original_gate')
    gate,gate_sha=operator.gate_function(metric,METRIC.read_text())
    return metric,gate,gate_sha

def freeze():
    if (OUT/'protocol.json').exists():raise ValueError('Already frozen')
    expected={MODEL:'5c8c92f8a761b46a66f3823765f6348ab0c08b74457d7efc062f0941ab07faf8',
              CAL:'619d6bf4d3200a6b55007a1abcc0658e76a14124ce5f3abad9f5f4b94d8979f7',
              REF:'4675d46574d65063d63ce9266ef4caa3d30c4880e4fac6fbabd11e6ff9747faf',
              METRIC:'14fc804b80f3742ee6c95cc3908c498459a77e61c90a1bdfe4b6c23c8580c1cd',
              GATE:'636dc354c5eb475757bbf8f0a1195d7b40782dd5a72969af0127beaccdb51a3e',
              OLD/'producer-receipt.json':'c18f0a3fbcec5fb85a21e1b33b95863aacb4a64b064bddd5e93056f8ae8d60ae'}
    for path,h in expected.items():
        if sha(path)!=h:raise ValueError('Historical source identity '+str(path))
    refs={x['id']:x for x in read(REF)['cases']}
    bindings={x['id']:x for x in read(BINDING)['cases']}
    producer=read(OLD/'producer-receipt.json');source_cases={x['id']:x for x in producer['cases']}
    metric,_,gate_sha=tools()
    sources=[rec(OUT/'replay.cpp'),rec(OUT/'run.py')]
    dependencies=[MODEL,CAL,REF,BINDING,METRIC,GATE,FEATURES,
                  ROOT/'tools/fit_full_calibration.py',ROOT/'Research/GrandPianoV2/tools/benchmark.py',
                  ROOT/'Research/GrandPianoV2/tools/radiation_fit.py',ROOT/'Research/GrandPianoV2/tools/fit_calibration.py',
                  OLD/'producer-receipt.json',ROOT/'out/full-causal-radiation-metrics/v1/protocol.json']
    cases=[]
    for ident in IDS:
        old=refs[ident];binding=bindings[ident];source=source_cases[ident]
        cases.append({'id':ident,'midi':binding['midi'],
          'trace':{'path':binding['trace'],'sha256':binding['expected_trace_sha256']},
          'force_proof':{'path':binding['force_proof'],'sha256':binding['expected_proof_sha256']},
          'baseline_audio':old['baseline_audio'],
          'fixed_gain':old['baseline']['fixed_gain'],'fixed_onset_frame':old['baseline']['fixed_onset_frame'],
          'source_proof':{**{key:source[key] for key in ['mechanical_state_bit_parity','force_bit_parity','new_faults']},
           'scope':'Inherited original capture collection-time proof. No new original physical trajectory is rendered; the computed companion cannot feed back into that saved trajectory.'}})
    p={'schema_version':1,'frozen_at_utc':now(),'scope':'One gamma100 contact-only full-state transient observer pilot on six already observed TRAIN cases. No fitting, new reference PCM, physical source changes, listening export or runtime adoption.',
       'candidate_or_force_pressure_opened':False,'sources':sources,'inputs':[rec(x) for x in dependencies],
       'cases':cases,'ids':list(IDS),'rate':RATE,'frames':FRAMES,'note_on_frame':4800,
       'model':{'strings':230,'string_modes':17778,'board_modes':475,'legacy_calibration_anchors':5,'humanization':0,'mechanical_level':0,'repetition_controller':False,'sample_rate':48000},
       'operator':{'gamma_per_second':100,'rho':math.exp(-100/48000),'recurrence':'Scale ALL old companion string+board q/p by rho BEFORE free update. Inject unchanged solved contact F at old freeStep/force/finishDamp location; then own unison and own full bridge Schur. No recorded bridge force drives the companion.',
         'output':'candidateRaw=recordedRawOld-C_rad*fastStringState; actual physical board pressure remains in recordedRawOld. HP24 from frame0, gain/width unchanged; output float32.',
         'first_markov':'Nominal real arithmetic companion Afast=rho*A, B unchanged gives h_new[n]=(1-rho^n)h_rad[n] for contact path. Float implementation/retirement are approximate; no exact linearity or new physical-part claim.',
         'free_poles':'Original physical state and its slow-pole readout remain. Extra fast observer poles/contact-driven history decay; no static radiation coefficient is changed.',
         'quiescence':{'fast_only':True,'rho1_control_gated':False,'threshold_raw_pressure':1e-20,'condition':'F==0 and 2*max_ch||C_rad S^-1||2*sqrt(2E_allFastStringsAndBoard)<=1e-20',
           'clear':'ONLY companion coordinates, cached radiation and bridge force; never HP state or captured source. Skip until a subsequent nonzero actual contact F. Controlled below-threshold approximation, not a MIDI/note-age gate.'}},
       'controls':{'rho1':'Manual force replay of full old model with rho1, own bridge/board, no nonlinear hammer solve. Require ALL rawOld and rawBoard float64 samples bitidentical to capture.',
         'baseline_HP':'HP24(recordedRawOld) float32 payload must exactly equal the historical baseline WAV payload.',
         'force':'Selected F must be finite/nonnegative, zero before4800 and from6720 onward; full88contact+3capturedbridge FNV compare both archived proof rows every frame. Captured bridge fields are proof-only, never drive either model.',
         'synthetic_wake':'One fixed C4 contact force impulse, wait for energy-bound retirement,64 quiet frames, later identical impulse; companion coordinates/output must match a fresh held instance at wake. No capture/reference input.'},
       'numerical_guards':{'finite':True,'faults':0,'positive_rho_scale_energy_increase':0,'maximum_free_energy_ratio':1,'max_actual_pressure_over_dual_bound':1,'mode_counts_unchanged':True,'force_and_replay_parity':True,'baseline_HP_payload':True,
         'tail':'Measure raw and HP counterterm after fixed old onset+.25s; final scores use explicit output and original gates. No new acoustic tail exception.'},
       'unchanged_original_gates':read(ROOT/'out/full-causal-radiation-metrics/v1/protocol.json')['gates'],
       'gate_arithmetic_sha256':gate_sha,'reference_access':'Existing derived reference/control JSON only. Never call historical locked/dependencies functions which recursively read reference audio.',
       'fit_or_gamma_sweep':False,'listening_candidate_exported':False,'adopted':False,
       'output_trace_columns':['rho1_rawL','rho1_rawR','fast_radL','fast_radR','baseline_HPL','baseline_HPR','candidate_HPL','candidate_HPR','fast_HPL','fast_HPR','fastEnergy','cumulativeRhoLoss','dualPressureBound','actualContactForce','candidateRawL','candidateRawR'],
       'log_policy':'producer.log is closed before manifest. run.log is a live outer stdout transcript and intentionally excluded from the numeric artifact manifest.',
       'compile':['g++','-std=c++17','-O3','-DNDEBUG','-fno-builtin','-ffp-contract=off',str(OUT/'replay.cpp'),'-o',str(OUT/'replay')]}
    write(OUT/'protocol.json',p);write(OUT/'freeze.json',{'frozen_at_utc':p['frozen_at_utc'],'protocol':rec(OUT/'protocol.json'),'sources':sources})

def execute():
    p=read(OUT/'protocol.json');frozen=read(OUT/'freeze.json')
    verify([frozen['protocol'],*p['sources'],*p['inputs'],*[item for c in p['cases'] for item in [c['trace'],c['force_proof'],c['baseline_audio']]]])
    if (OUT/'opening-started.json').exists():raise ValueError('Once-only pilot already started')
    write(OUT/'opening-started.json',{'started_at_utc':now(),'freeze':rec(OUT/'freeze.json'),'pressure_inputs_decoded_before_marker':False})
    started=time.monotonic();subprocess.run(p['compile'],check=True)
    root=OUT/'renders';root.mkdir(exist_ok=False)
    for c in p['cases']:(root/c['id']).mkdir()
    tsv=OUT/'cases.tsv';tsv.write_text(''.join('\t'.join([c['id'],str(c['midi']),c['trace']['path'],str(c['fixed_onset_frame']),c['force_proof']['path']])+'\n' for c in p['cases']))
    command=[str(OUT/'replay'),str(tsv),str(root)]
    write(OUT/'producer-freeze.json',{'created_at_utc':now(),'protocol':rec(OUT/'protocol.json'),'binary':rec(OUT/'replay'),'case_tsv':rec(tsv),'command':command})
    with (OUT/'producer.log').open('x') as log:
        process=subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        for line in process.stdout:log.write(line);log.flush();print(line,end='',flush=True)
        code=process.wait()
    if code:raise ValueError('Producer failed with exit '+str(code))
    synthetic=read(root/'synthetic.json')
    if not synthetic['retired'] or not synthetic['wake_coordinate_identity'] or synthetic['max_scale_energy_increase']>0 or synthetic['max_free_energy_ratio']>1 or synthetic['max_pressure_over_bound']>1 or synthetic['control_faults'] or synthetic['companion_faults']:raise ValueError('Synthetic wake/energy guard')
    metric,gate,gate_sha=tools()
    if gate_sha!=p['gate_arithmetic_sha256']:raise ValueError('Gate arithmetic changed')
    refs={x['id']:x for x in read(REF)['cases']};rows={x['id']:x for x in read(FEATURES)['samples']}
    outcomes=[]
    for c in p['cases']:
        ident=c['id'];d=root/ident;numeric=read(d/'numeric.json')
        sr,historical=wavfile.read(c['baseline_audio']['path'])
        if sr!=RATE or historical.dtype!=np.float32 or historical.shape!=(FRAMES,2):raise ValueError('Historical synthetic baseline format')
        baseline=np.fromfile(d/'baseline.f32le',dtype='<f4').reshape((FRAMES,2))
        candidate=np.fromfile(d/'candidate.f32le',dtype='<f4').reshape((FRAMES,2))
        observer=np.memmap(d/'observer.f64le',mode='r',dtype='<f8',shape=(FRAMES,16))
        baseline_exact=baseline.tobytes()==historical.astype('<f4').tobytes()
        numeric_guards={'rho1_raw_bitexact':numeric['control_nonidentical_samples']==0 and numeric['control_max_error']==0,
          'rho1_board_bitexact':numeric['board_nonidentical_samples']==0 and numeric['board_max_error']==0,
          'baseline_HP_payload':baseline_exact,'force_contract':numeric['force_contract_errors']==0 and numeric['force_proof_mismatches']==0,
          'finite':numeric['nonfinite']==0 and bool(np.isfinite(candidate).all()),'faults':numeric['control_faults']==numeric['companion_faults']==0,
          'rho_energy':numeric['max_positive_scale_energy']==0,'free_energy_contracts':numeric['max_free_energy_ratio']<=1,'dual_pressure_bound':numeric['max_pressure_over_bound']<=1,
          'counts':numeric['mode_count']==17778 and numeric['board_modes']==475 and numeric['string_count']==230,
          'retirement_bound':numeric['retirements']>=1 and numeric['discarded_pressure_bound']<=1e-20}
        if not all(numeric_guards.values()):raise ValueError('Numeric guard failed '+ident+': '+str(numeric_guards))
        wave=d/'candidate.wav';wavfile.write(wave,RATE,candidate)
        features=metric.observation_features(candidate.astype(np.float64),c['fixed_onset_frame'],c['fixed_gain'],refs[ident]['reference'],rows[ident])
        proof=dict(c['source_proof']);proof['new_faults']|=numeric['companion_faults']|numeric['nonfinite']
        scored=gate(refs[ident],features,ident,baseline_exact,{ident:proof})
        onset=c['fixed_onset_frame'];tail=np.asarray(observer[onset+12000:,8:10]);base_sustain=baseline[onset+12000:onset+36000].astype(float)
        tail_rms=float(np.sqrt(np.mean(tail*tail)));base_rms=float(np.sqrt(np.mean(base_sustain*base_sustain)))
        row={'id':ident,'candidate_audio':rec(wave),'candidate':features,**scored,'numeric':numeric,'numeric_guards':numeric_guards,
             'fast_tail':{'from_old_onset_seconds':.25,'HP_RMS':tail_rms,'HP_peak':float(np.max(abs(tail))),'relative_to_old_sustain_RMS_db':20*math.log10(max(tail_rms,1e-300)/max(base_rms,1e-300)),
               'late_candidate_baseline_float32_different_samples':int(np.count_nonzero(candidate[onset+12000:].view('<u4')!=baseline[onset+12000:].view('<u4')))},
             'source_proof':proof,'source_proof_scope':'Inherited old intact-source collection-time state/force parity, plus this contact-history FNV/rho1 force replay. Companion is intentionally a separate observer; no original source/state was rerendered or modified.',
             'no_new_reference_PCM':True,'adopted':False}
        outcomes.append(row);write(d/'result.json',row)
        print(ident,'PASS' if row['passes_all_case_gates'] else 'FAIL',row['gates'],flush=True)
    verify([frozen['protocol'],*p['sources'],*p['inputs'],*[item for c in p['cases'] for item in [c['trace'],c['force_proof'],c['baseline_audio']]]])
    result={'completed_at_utc':now(),'protocol':rec(OUT/'protocol.json'),'producer_freeze':rec(OUT/'producer-freeze.json'),'synthetic':synthetic,'cases':outcomes,
      'cases_passing_all_original_gates':sum(c['passes_all_case_gates'] for c in outcomes),'case_count':6,
      'passes_all_original_gates':all(c['passes_all_case_gates'] for c in outcomes),'wall_seconds':time.monotonic()-started,
      'original_physical_trajectory_renders':0,'full_companion_and_rho1_replay_instances':2,'new_reference_PCM_access':False,'gamma_variants':1,'fit_runs':0,'adopted':False,
      'limitations':['Six already observed TRAIN witnesses, not new validation.','Original poles/readout and captured physical forces retained; companion has no physical feedback or identified-part meaning.','Full additional17778string+475board observer is an offline quality proof, not a realtime architecture.','Float arithmetic and below1e-20 quiescence are explicit approximations.','A passed pilot would require full-range and musical/listening checks before any runtime change.']}
    write(OUT/'result.json',result)
    print('PILOT',result['cases_passing_all_original_gates'],'/6 original preservation cases pass',flush=True)
    manifest={str(f.relative_to(OUT)):{'sha256':sha(f),'bytes':f.stat().st_size} for f in sorted(OUT.rglob('*')) if f.is_file() and f.name not in ('manifest.json','run.log') and '__pycache__' not in f.parts}
    write(OUT/'manifest.json',manifest)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['freeze','run']);a=parser.parse_args()
    if a.command=='freeze':freeze();return
    try:execute()
    except Exception as e:
        if not (OUT/'failure.json').exists():write(OUT/'failure.json',{'failed_at_utc':now(),'error_type':type(e).__name__,'error':str(e),'traceback':traceback.format_exc(),'silently_retried':False})
        raise
if __name__=='__main__':main()
