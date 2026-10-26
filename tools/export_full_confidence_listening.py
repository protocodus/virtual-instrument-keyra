#!/usr/bin/env python3
"""Export five frozen TRAIN/historical comparisons without fitting or synthesis."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np
from scipy.io import wavfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import evaluate_full_confidence_loss as historical
import fit_full_calibration as fitting

CASES=('A3v8','C4v12','A0v8','C2v8','C8v8')
RATE=48000
MAX_SECONDS=3.5
GAP_SECONDS=.25
FADE_SECONDS=.020


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def record(path):return {'path':str(Path(path).resolve()),'sha256':sha(path)}
def decode(path,fmt):
    return subprocess.run(['ffmpeg','-v','error','-i',str(path),'-f',fmt,'-'],
                          check=True,stdout=subprocess.PIPE).stdout


def main():
    protocol,candidate=historical.locked()
    inputs={}
    def guard(path,expected):
        path=Path(path).resolve()
        if sha(path)!=expected:raise ValueError('Frozen input changed: '+str(path))
        if path in inputs and inputs[path]!=expected:raise ValueError('Conflicting identity')
        inputs[path]=expected;return path
    def guarded(row):return guard(row['path'],row['sha256'])
    for row in protocol['inputs']:guarded(row)
    guarded(protocol['candidate_freeze'])
    for key in ('source','header','profile','binary','protocol','training_report','train_predictions'):
        guarded(candidate[key])
    # Follow the nested TRAIN freeze as well: the historical freeze pins its
    # receipt, while these records authenticate each TRAIN score/producer.
    training_protocol=read(candidate['protocol']['path'])
    for row in training_protocol['inputs']:guarded(row)
    historical_path=ROOT/'out/full-confidence-loss/historical/results.json'
    hist=read(historical_path)
    for key in ('freeze','candidate_freeze','predictions','runner','scoring_started','reference_features','cached_baselines'):
        guarded(hist[key])
    # The result itself was produced from the above pinned receipts; retain its
    # actual identity in this export in addition to every selected audio hash.
    guard(historical_path,sha(historical_path))
    hist_refs={r['id']:r for r in read(hist['reference_features']['path'])['samples']}
    hist_cases={r['id']:r for r in protocol['cases']}
    original_history=read(hist['cached_baselines']['path'])
    history_predictions=read(ROOT/'out/full-calibration/v4/evaluation/predictions.json')
    current_predictions=read(hist['predictions']['path'])
    train_rows,_=fitting.training_inputs(fitting.DEFAULT_REFERENCE,fitting.DEFAULT_SPLIT)
    train_refs={r['id']:r for r in train_rows}
    confidence_train=read(ROOT/'out/full-confidence-loss/report.json')
    guarded(confidence_train['score'])
    train_scores={name:read(path) for name,path in {
        'original':ROOT/'out/full-calibration/v4/control-score/score.json',
        'v4':ROOT/'out/full-calibration/v4/final-score/score.json',
        'confidence':ROOT/'out/full-confidence-loss/score/score.json'}.items()}
    # Pin every original/V4 producer from the historical protocol, and the
    # confidence candidate through its candidate-freeze receipt.
    frozen_v4=read(ROOT/'out/full-calibration/v4/evaluation/freeze.json')
    producers={}
    for name,label in (('original','control'),('v4','candidate')):
        prod=frozen_v4['producers'][label]
        producers[name]={k:record(prod[k]) for k in ('source','header','binary')}
        for row in producers[name].values():guarded(row)
    producers['v4']['profile']=record(ROOT/'out/full-calibration/v4/radiation/calibration.json')
    guarded(producers['v4']['profile'])
    producers['confidence']={k:candidate[k] for k in ('source','header','binary','profile')}
    prepared=[]
    fade_frames=round(RATE*FADE_SECONDS)
    fade=.5+.5*np.cos(np.linspace(0.,np.pi,fade_frames))
    for ident in CASES:
        is_historical=ident in hist_cases
        if is_historical:
            row=hist_cases[ident];ref=hist_refs[ident]
            reference_identity=row['reference'];reference_path=guarded(reference_identity['wav'])
            guarded(reference_identity['flac'])
            comp_sets={'original':original_history['variants']['control'],
                       'v4':original_history['variants']['candidate'],
                       'confidence':hist['variant']}
            paths={name:Path(next(p for p in history_predictions['renders'] if p['id']==ident and p['variant']==label)['outputs'][0]['path'])
                   for name,label in (('original','control'),('v4','candidate'))}
            prediction=next(p for p in current_predictions['renders'] if p['id']==ident)
            paths['confidence']=Path(prediction['outputs'][0]['path'])
            split='historical_observed'
        else:
            if ident not in train_refs:raise ValueError('Case outside locked inventories')
            ref=train_refs[ident]
            reference_path=Path(fitting.reference_audio(ref,fitting.DEFAULT_REFERENCE)).resolve()
            reference_identity=fitting.reference_audio_identity(ref,reference_path)
            guard(reference_path,reference_identity['actual_wave_sha256'])
            comp_sets=train_scores
            paths={'original':ROOT/'out/full-calibration/v3/control-renders'/(ident+'.wav'),
                   'v4':ROOT/'out/full-calibration/v4/final-renders'/(ident+'.wav'),
                   'confidence':ROOT/'out/full-confidence-loss/renders'/(ident+'.wav')}
            split='train'
            # The score and manifest are frozen by the TRAIN/candidate receipts;
            # retain the selected prediction's complete source binding as well.
            entry=next(r for r in confidence_train['predictions']['cases'] if r['id']==ident)
            guarded(entry['audio']);guarded(entry['events'])
        tracks=[];sections=[]
        for name in ('real','original','v4','confidence'):
            comparison=None;gain_db=0.
            if name=='real':path=reference_path
            else:
                comparison=next(r for r in comp_sets[name]['comparison'] if r['id']==ident)
                path=guard(paths[name],comparison['model_sha256'])
                gain_db=comparison['early_gain_db']
                if comparison['reference_sha256']!=ref['sha256']:
                    raise ValueError('Comparison uses different reference features')
            sr,x=fitting.benchmark.load_audio(path)
            if sr!=RATE or x.ndim!=2 or x.shape[1]!=2 or not np.isfinite(x).all():
                raise ValueError('Expected finite stereo48k audio')
            onset,onset_detail=fitting.benchmark.onset_index(x,sr)
            if name=='real' and onset!=round(ref['onset_seconds']*sr):
                raise ValueError('Reference onset differs from frozen features')
            sections.append(x[onset:].copy()*10**(gain_db/20))
            tracks.append({'role':name,'input':str(Path(path).relative_to(ROOT)),
                'input_sha256':sha(path),'input_frames':len(x),'source_onset_frame':onset,
                'available_frames_after_onset':len(x)-onset,'onset_measurement':onset_detail,
                'early_gain_db_from_frozen_score':gain_db,
                'early_gain_linear':10**(gain_db/20),
                'producer':None if name=='real' else producers[name],
                'scored_comparison':comparison})
        frames=min(round(MAX_SECONDS*RATE),*(len(x) for x in sections))
        if frames<=fade_frames:raise ValueError('Insufficient shared support')
        cropped=[]
        for x in sections:
            y=x[:frames].copy();y[-fade_frames:]*=fade[:,None];cropped.append(y)
        prepared.append((ident,split,reference_identity,cropped,tracks,frames))
    peak=max(float(np.max(np.abs(x))) for _,_,_,sections,_,_ in prepared for x in sections)
    common_gain=.8/peak
    folder=ROOT/'Audio/full-confidence-loss';folder.mkdir(parents=True,exist_ok=True)
    work=ROOT/'out/full-confidence-loss/listening';work.mkdir(parents=True,exist_ok=True)
    gap=np.zeros((round(RATE*GAP_SECONDS),2));entries=[]
    for ident,split,reference_identity,sections,tracks,frames in prepared:
        sequence=[]
        for i,x in enumerate(sections):
            if i:sequence.append(gap)
            sequence.append(x)
        audio=np.concatenate(sequence)*common_gain
        if not np.isfinite(audio).all() or np.max(np.abs(audio))>.800001:raise ValueError('Invalid comparison')
        prefix=ident+'-real-original-v4-confidence'
        wave=work/(prefix+'.wav');flac=folder/(prefix+'.flac')
        wavfile.write(wave,RATE,audio.astype(np.float32))
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(wave),'-c:a','flac',
                        '-sample_fmt','s32','-bits_per_raw_sample','24',str(flac)],check=True)
        pcm=decode(wave,'s24le')
        if decode(flac,'s24le')!=pcm:raise ValueError('Lossless PCM24 verification failed')
        decoded=np.frombuffer(decode(flac,'f32le'),dtype='<f4').reshape(-1,2)
        error=float(np.max(np.abs(decoded-audio.astype(np.float32))))
        if decoded.shape!=audio.shape or error>2**-23:raise ValueError('Unexpected PCM quantization')
        for i,track in enumerate(tracks):
            track['output_start_frame']=i*(frames+len(gap))
            track['output_start_seconds']=track['output_start_frame']/RATE
            track['output_frames']=frames
        entries.append({'id':ident,'split':split,'reference_identity':reference_identity,
            'file':flac.name,'sha256':sha(flac),'processed_float_wave_sha256':sha(wave),
            'decoded_pcm24_sha256':hashlib.sha256(pcm).hexdigest(),
            'maximum_float_to_pcm24_error':error,'frames':len(audio),'seconds_per_section':frames/RATE,
            'duration_seconds':len(audio)/RATE,'tracks':tracks})
    for path,expected in inputs.items():guard(path,expected)
    historical.locked()
    manifest={'schema_version':1,'exporter':record(__file__),
        'candidate_freeze':protocol['candidate_freeze'],'historical_result':record(historical_path),
        'training_result':record(ROOT/'out/full-confidence-loss/report.json'),
        'order':['real recording','original full control','v4 full candidate','confidence-prior full candidate'],
        'format':'24-bit FLAC,48kHz stereo','maximum_seconds_per_section':MAX_SECONDS,
        'support':'Common actual post-onset support within each case, capped3.5s; no zero padding.',
        'gap_seconds':GAP_SECONDS,'alignment':'Frozen benchmark onset per source; no time stretch, pitch shift or phase alignment.',
        'levels':{'model_gain':'Exact early_gain_db from the frozen score for that model/reference; real0dB before common gain.',
                  'one_shared_peak_gain_across_all_twenty_sections':common_gain,
                  'peak_before_common_gain':peak,'target_sample_peak':.8,'independent_peak_normalization':False},
        'fade':{'where':'Last20ms of every section','shape':'Half cosine1to0','frames':fade_frames,'attack_fade':False},
        'no_synthesis_or_fitting_run':True,'new_reference_acquisition':False,
        'all_historical_audio_previously_observed':True,'fresh_validation':False,'default_promoted':False,
        'attribution':{'recordings':'Salamander Grand Piano V3 by Alexander Holm',
            'source':'https://github.com/sfzinstruments/SalamanderGrandPiano/tree/3382bf9496bba2486f5ab0de55a264d1dfc38404',
            'original_distribution':'https://archive.org/details/SalamanderGrandPianoV3',
            'license':'Creative Commons Attribution3.0 Unported','license_url':'https://creativecommons.org/licenses/by/3.0/',
            'modifications':'Onset-trimmed,cropped to common support up to3.5s,final20ms faded,one shared gain,concatenated with model comparisons and0.25s silence,converted toPCM24FLAC. No resampling,EQ,denoising or added room.'},
        'limits':['C4v12 is TRAIN; A3v8,A0v8,C2v8,C8v8 are previously-observed historical cases.',
            'Recording-agreement metrics are not perceptual parity or independent generalization.',
            'A0v8 rise-time regression,C2v8 envelope regression and the unresolved C8 component remain audible review targets.',
            'Acquisition room/recording chain remain in real recordings; no room added to any section.',
            'MIDI velocities are SFZ-bin proxies,not measured recording hammer speeds.',
            'Single held-note renders do not include the separate repetition/mechanism/acoustic research adapters.',
            'No realtime or Reason host qualification.'],
        'inputs':[{'path':str(path.relative_to(ROOT)),'sha256':expected} for path,expected in sorted(inputs.items())],
        'entries':entries}
    (folder/'manifest.json').write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n')
    print(folder)


if __name__=='__main__':main()
