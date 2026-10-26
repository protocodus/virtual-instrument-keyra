#!/usr/bin/env python3
"""Separate TRAIN-only sensitivity study for unknown reference pedal condition.

This is not a pedal-state identification, a loss-bank selection or a proposal
to hold the live instrument's pedal down. It compares the same frozen full
model at three prospective pedal conditions and never changes its profile.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
REFERENCE=ROOT/'References/GrandFullRange/combined_train_features.json'
SPLIT=ROOT/'References/GrandFullRange/split.json'
BASE=ROOT/'out/full-calibration/v4/radiation/float-solver'
BASE_RENDERS=ROOT/'out/full-calibration/v4/final-renders'
BASE_SCORE=ROOT/'out/full-calibration/v4/final-score'
IDS=[note+f'v{layer}' for note in ('A0','C4','D#4') for layer in (4,12)]
LEVELS=(.5,1.)
METRICS=('envelope_mae_db','harmonic_level_mae_db','log_band_mae_db',
         'partial_decay_slope_mae_db_per_second','partial_tuning_mae_cents',
         'attack_rise10_90_error_ms')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def record(path):return {'path':str(Path(path).resolve()),'sha256':sha(path)}
def module():
    spec=importlib.util.spec_from_file_location('pedal_condition_training_guard',ROOT/'tools/fit_full_calibration.py')
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
def verify(records):
    for row in records:
        if sha(row['path'])!=row['sha256']:raise ValueError('Frozen input changed: '+row['path'])
def condition_name(level):return 'pedal-half' if level==.5 else 'pedal-down'
def mean(values):
    xs=[float(v) for v in values if v is not None and math.isfinite(v)]
    return sum(xs)/len(xs) if xs else None


def freeze(out,fitter):
    rows,_=fitter.training_inputs(REFERENCE,SPLIT);refs={r['id']:r for r in rows}
    if not set(IDS)<=set(refs):raise ValueError('Condition pilot left locked TRAIN')
    inputs=[Path(__file__),ROOT/'tools/fit_full_calibration.py',REFERENCE,SPLIT,
            BASE/'grand.cpp',BASE/'calibration.h',BASE/'render',
            BASE_RENDERS/'render-manifest.json',BASE_SCORE/'score.json',BASE_SCORE/'model-features.json']
    identities=[]
    for ident in IDS:
        path=fitter.reference_audio(refs[ident],REFERENCE);inputs.append(path)
        identities.append(fitter.reference_audio_identity(refs[ident],path))
    original=read(BASE_RENDERS/'render-manifest.json');cached={r['id']:r for r in original['renders']}
    for field,path in (('source_sha256',BASE/'grand.cpp'),('calibration_sha256',BASE/'calibration.h'),
                       ('engine_sha256',BASE/'render'),('reference_features_sha256',REFERENCE),
                       ('split_sha256',SPLIT),('training_guard_sha256',ROOT/'tools/fit_full_calibration.py')):
        if original[field]!=sha(path):raise ValueError('Cached zero-pedal producer mismatch')
    cached_models={r['id']:r for r in read(BASE_SCORE/'model-features.json')['samples']}
    cached_scores={r['id']:r for r in read(BASE_SCORE/'score.json')['comparison']}
    for ident in IDS:
        if cached[ident]['output_sha256'][ident+'.wav']!=sha(BASE_RENDERS/(ident+'.wav')):
            raise ValueError('Cached zero-pedal output mismatch')
        if cached[ident]['inputs']['score_sha256']!=sha(BASE_RENDERS/(ident+'.events')):
            raise ValueError('Cached zero-pedal event mismatch')
        if cached_models[ident]['sha256']!=sha(BASE_RENDERS/(ident+'.wav')) or cached_scores[ident]['model_sha256']!=sha(BASE_RENDERS/(ident+'.wav')):
            raise ValueError('Cached zero-pedal feature mismatch')
        inputs.extend((BASE_RENDERS/(ident+'.wav'),BASE_RENDERS/(ident+'.events')))
    config={'schema_version':1,'ids':IDS,'pedal_conditions':[0.,.5,1.],
            'sample_rate':48000,'duration_seconds':3.8,'note_on_seconds':.1,'note_off_seconds':4.15,
            'pedal_event_seconds':0.,'profile_changed':False,'maximum_concurrent_renders':2,
            'inputs':[record(p) for p in inputs],'reference_identities':identities,
            'selection':'None; report condition sensitivity, do not identify acquisition state or select a default.',
            'evaluation_audio_or_features_read':False,
            'limitations':['Unknown recording pedal/room/editing conditions confound agreement.',
                'The original full renderer includes passive damper/sympathetic response, but no separate pedal-noise adapter in this experiment.',
                'Any changed hammer interaction follows the existing coupled model; no waveform/noise source is added.']}
    target=out/'freeze.json'
    if target.exists():
        old=read(target);old.pop('frozen_at_utc',None)
        if old!=config:raise ValueError('Existing condition protocol changed')
    else:write(target,{**config,'frozen_at_utc':datetime.now(timezone.utc).isoformat()})
    verify(config['inputs']);return refs


def render_condition(out,level,refs):
    name=condition_name(level);folder=out/name;folder.mkdir(parents=True,exist_ok=True)
    freeze_record=read(out/'freeze.json');verify(freeze_record['inputs'])
    producer={'source_sha256':sha(BASE/'grand.cpp'),'calibration_sha256':sha(BASE/'calibration.h'),
        'engine_sha256':sha(BASE/'render'),'reference_features_sha256':sha(REFERENCE),
        'split_sha256':sha(SPLIT),'training_guard_sha256':sha(ROOT/'tools/fit_full_calibration.py')}
    def one(ident):
        ref=refs[ident];events=folder/(ident+'.events');audio=folder/(ident+'.wav');sidecar=folder/(ident+'.json')
        events.write_text(f'# Prospective capture-condition sensitivity; not identified recording state.\n'
            f'0.000000 pedal 0 {level:.6f}\n0.100000 on {ref["midi"]} {ref["midi_velocity"]}\n4.150000 off {ref["midi"]} 0\n')
        cmd=[str(BASE/'render'),'--events',str(events),'--output',str(audio),
             '--sample-rate','48000','--duration','3.8']
        inputs={**producer,'score_sha256':sha(events),'command':cmd}
        if sidecar.exists():
            old=read(sidecar)
            if old['inputs']!=inputs or old['output_sha256'][audio.name]!=sha(audio):
                raise ValueError('Cached condition prediction changed: '+ident)
            return old
        call=subprocess.run(cmd,text=True,capture_output=True,check=True)
        metrics=json.loads(call.stdout)
        if metrics['nonfinite_samples'] or metrics['string_count']!=230 or metrics['board_modes']!=475:
            raise ValueError('Invalid condition render')
        result={'id':ident,'inputs':inputs,'metrics':metrics,'output_sha256':{audio.name:sha(audio)}}
        write(sidecar,result);return result
    results=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        for task in as_completed([pool.submit(one,ident) for ident in IDS]):
            result=task.result();results.append(result);print(name,result['id'],'rendered',flush=True)
    verify(freeze_record['inputs'])
    write(folder/'render-manifest.json',{**producer,'ids':sorted(IDS),'rate':48000,
        'duration_seconds':3.8,'pedal_position':level,'stems':False,
        'event_policy':f'0s pedal{level}; .1s on; 4.15s off; frozen SFZ-bin velocity proxy',
        'source_path':str(BASE/'grand.cpp'),'engine_path':str(BASE/'render'),
        'renders':sorted(results,key=lambda r:r['id']),'errors':[],'complete':True,
        'limits':'TRAIN-only condition sensitivity, not acquisition-state identification.'})
    score=folder/'score'
    if not (score/'score.json').exists():
        with (folder/'score.log').open('w') as log:
            subprocess.run([sys.executable,str(ROOT/'tools/fit_full_calibration.py'),'score',
                '--renders',str(folder),'--output',str(score),'--ids',*IDS],
                cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    print(name,'scored',flush=True)


def attack_rows(score):
    return {r['id']:mean(abs(v) for w in r['differences'] if .005<=w['window_seconds'][0]<.1
        for j,v in enumerate(w['band_error_db']) if j>0 and w['reference_prominent_band_mask'][j]) for r in score['attack_texture']}


def stereo(path,benchmark):
    rate,x=benchmark.load_audio(path);start,_=benchmark.onset_index(x,rate);x=x[start:]
    result=[]
    for a,b in ((.05,.25),(.25,.75),(.75,1.5),(1.5,3.5)):
        y=np.asarray(x[int(a*rate):int(b*rate)],float)
        if y.ndim!=2 or y.shape[1]!=2:raise ValueError('Stereo source required')
        power=np.mean(y*y,axis=0);cor=float(np.corrcoef(y.T)[0,1])
        result.append({'window_seconds':[a,b],'correlation':cor,
            'right_minus_left_db':float(10*np.log10(max(power[1],1e-30)/max(power[0],1e-30)))})
    return result


def summarize(out,refs,fitter):
    frozen=read(out/'freeze.json');verify(frozen['inputs'])
    baseline=read(BASE_SCORE/'score.json');base={r['id']:r for r in baseline['comparison']}
    ba=attack_rows(baseline);bv={r['midi']:r for r in baseline['velocity_contrasts']}
    conditions=[]
    for level in LEVELS:
        folder=out/condition_name(level);score=read(folder/'score/score.json')
        rows={r['id']:r for r in score['comparison']};attack=attack_rows(score);cases=[]
        for ident in IDS:
            values={k:{'pedal_zero':base[ident][k],'condition':rows[ident][k],
                       'change':rows[ident][k]-base[ident][k]} for k in METRICS}
            values['attack_band_mae_db']={'pedal_zero':ba[ident],'condition':attack[ident],
                                        'change':attack[ident]-ba[ident]}
            cases.append({'id':ident,**values,
                'spurious_zero':len(base[ident]['spurious_prominent_model_bands']),
                'spurious_condition':len(rows[ident]['spurious_prominent_model_bands']),
                'stereo':{'reference':stereo(fitter.reference_audio(refs[ident],REFERENCE),fitter.benchmark),
                          'pedal_zero':stereo(BASE_RENDERS/(ident+'.wav'),fitter.benchmark),
                          'condition':stereo(folder/(ident+'.wav'),fitter.benchmark)}})
        velocity=[{'midi':r['midi'],'reference_contrast_db':r['reference_early_rms_contrast_db'],
                   'pedal_zero_error_db':bv[r['midi']]['error_db'],'condition_error_db':r['error_db']} for r in score['velocity_contrasts']]
        conditions.append({'pedal_position':level,'cases':cases,
            'aggregate':{k:{'pedal_zero_mean':mean(r[k]['pedal_zero'] for r in cases),
                            'condition_mean':mean(r[k]['condition'] for r in cases),
                            'mean_change':mean(r[k]['change'] for r in cases),
                            'worst_case_regression':max(r[k]['change'] for r in cases)} for k in (*METRICS,'attack_band_mae_db')},
            'velocity_contrasts':velocity,'score':record(folder/'score/score.json'),
            'predictions':record(folder/'render-manifest.json')})
    verify(frozen['inputs'])
    result={'schema_version':1,'freeze':record(out/'freeze.json'),'ids':IDS,'conditions':conditions,
        'default_or_profile_changed':False,'acquisition_pedal_state_identified':False,
        'evaluation_data_used':False,'loss_bank_selection_informed_by_this_study':False,
        'interpretation':'Sensitivity of the same coupled instrument to a documented prospective condition. Agreement cannot identify source pedal state amid room/body/editing/velocity uncertainty.',
        'limits':frozen['limitations']}
    write(out/'report.json',result);return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=('freeze','run','report'))
    parser.add_argument('--output',type=Path,default=ROOT/'out/full-pedal-condition')
    parser.add_argument('--report',type=Path,default=ROOT/'Validation/full-pedal-condition.json')
    args=parser.parse_args();out=args.output.resolve();report=args.report.resolve()
    if not (ROOT/'out').resolve() in out.parents:parser.error('Output must be under out/')
    if not any(p.resolve() in report.parents for p in (ROOT/'out',ROOT/'Validation')):parser.error('Report must be under out/ or Validation/')
    out.mkdir(parents=True,exist_ok=True);fitter=module();refs=freeze(out,fitter)
    if args.stage=='run':
        for level in LEVELS:render_condition(out,level,refs)
    if args.stage in ('report','run'):
        summarize(out,refs,fitter);shutil.copyfile(out/'report.json',report);print(report,flush=True)


if __name__=='__main__':main()
