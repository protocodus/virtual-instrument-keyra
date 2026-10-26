#!/usr/bin/env python3
"""TRAIN-only causal attack-timing diagnostic; no fitting or default changes."""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
from scipy import ndimage
from scipy.io import wavfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import fit_full_calibration as fit

OUT=ROOT/'out/full-attack-timing'
IDS=('A0v4','A0v12','C1v4','C1v12','C2v4','C2v12','C4v4','C4v12')
VARIANTS={
 'v4':'Unmodified frozen V4; short render must match cached full-render prefix.',
 'hardness-prior':'Only A0 hammer K divided by0.8, restoring pre-strike-bank hardness1.0.',
 'analytic-observation':'Zero all additive modal radiation corrections; actual board pressure and mechanics retained.',
 'zero-H-phase-correction':'Set additive correction H phase to0 while preserving its magnitude and transformer sign per mode/channel; actual board pressure retained.',
 'no-sub250-correction':'Zero additive corrections below250Hz; actual board pressure and all other corrections retained.'}
FOLDERS={
 'original':ROOT/'out/full-calibration/v3/control-renders',
 'analytic':ROOT/'out/full-calibration/v4/analytic-renders',
 'v4':ROOT/'out/full-calibration/v4/final-renders',
 'confidence':ROOT/'out/full-confidence-loss/renders'}
SCORES={
 'original':ROOT/'out/full-calibration/v4/control-score',
 'analytic':ROOT/'out/full-calibration/v4/analytic-score',
 'v4':ROOT/'out/full-calibration/v4/final-score',
 'confidence':ROOT/'out/full-confidence-loss/score'}
PRODUCERS={
 'original':ROOT/'out/full-calibration/v3/control-f32',
 'analytic':ROOT/'out/full-calibration/v4/analytic/float-solver',
 'v4':ROOT/'out/full-calibration/v4/radiation/float-solver',
 'confidence':ROOT/'out/full-confidence-loss/solver'}
FLAGS=['-O3','-DNDEBUG','-std=c++17','-ffp-contract=off']


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def record(path):return {'path':str(Path(path).resolve()),'sha256':sha(path)}
def now():return datetime.now(timezone.utc).isoformat()
def verify(rows):
    for r in rows:
        if sha(r['path'])!=r['sha256']:raise ValueError('Frozen input changed:'+r['path'])
def locked():
    d=read(OUT/'freeze.json');verify(d['inputs']);return d


def freeze():
    if (OUT/'freeze.json').exists():locked();return
    OUT.mkdir(parents=True,exist_ok=True)
    rows,_=fit.training_inputs(fit.DEFAULT_REFERENCE,fit.DEFAULT_SPLIT)
    by_id={r['id']:r for r in rows}
    if not set(IDS)<=by_id.keys():raise ValueError('Diagnostic contains non-TRAIN cases')
    paths=[Path(__file__),ROOT/'tools/probe_full_attack_timing.cpp',ROOT/'tools/fit_full_calibration.py',
        ROOT/'Research/GrandPianoV2/tools/benchmark.py',fit.DEFAULT_REFERENCE,fit.DEFAULT_SPLIT,
        ROOT/'out/full-calibration/v4/analytic/calibration.json',
        ROOT/'out/full-calibration/v4/radiation/calibration.json',
        ROOT/'out/full-confidence-loss/calibration.json']
    refs=[]
    for ident in IDS:
        row=by_id[ident];p=fit.reference_audio(row,fit.DEFAULT_REFERENCE)
        identity=fit.reference_audio_identity(row,p)
        refs.append({'id':ident,'audio':record(p),'identity':identity})
        paths.append(Path(p))
    for label,folder in FOLDERS.items():
        for name in ('render-manifest.json',):paths.append(folder/name)
        for file in ('grand.cpp','calibration.h','render'):paths.append(PRODUCERS[label]/file)
        for name in ('model-features.json','score.json'):paths.append(SCORES[label]/name)
        for ident in IDS:
            receipt=read(folder/(ident+'.json'));wav=folder/(ident+'.wav')
            if receipt['output_sha256'][wav.name]!=sha(wav):raise ValueError('Cached prediction changed')
            if receipt['inputs']['source_sha256']!=sha(PRODUCERS[label]/'grand.cpp') or receipt['inputs']['calibration_sha256']!=sha(PRODUCERS[label]/'calibration.h') or receipt['inputs']['engine_sha256']!=sha(PRODUCERS[label]/'render'):
                raise ValueError('Cached producer mismatch')
            paths.extend((folder/(ident+'.json'),folder/(ident+'.events'),wav))
            for suffix in ('-primary.wav','-secondary.wav','-transient.wav'):
                stem=folder/(ident+suffix)
                if stem.name in receipt['output_sha256']:
                    if sha(stem)!=receipt['output_sha256'][stem.name]:raise ValueError('Cached stem changed')
                    paths.append(stem)
    source=OUT/'source';source.mkdir(exist_ok=True)
    for name in ('grand.cpp','calibration.h'):
        shutil.copyfile(PRODUCERS['v4']/name,source/name);paths.append(source/name)
    config={'schema_version':1,'frozen_at_utc':now(),'training_ids':list(IDS),
        'new_synthesis_training_ids':['A0v4','A0v12'],'variants':VARIANTS,
        'render_protocol':{'sample_rate':48000,'frames':16800,'seconds':.35,'note_on_frame':4800,
            'note_off':'None within render','pedal':0,'maximum_concurrent_renders':2,
            'maximum_new_short_renders':10,'maximum_new_audio_seconds':3.5,
            'gain':'No synthesis normalization; compare using fixed early-RMS gain from frozen V4 full render, never refit ablation gain.'},
        'diagnostics':{'official':'Unmodified onset_index and centered5ms RMS crossings relative to first150ms maximum.',
            'threshold_sensitivity':[.75,.80,.85,.90,.95],
            'smoothing_ms':[1,2,5,10],
            'fixed_event_axis':'Also show pressure peak times and force on true100ms event axis.',
            'texture':'Retain first5/5–20/20–50/50–100ms band powers and centroid above250Hz.',
            'force':'Infer sample force from exact hammer velocity change,mass/dt; no other hammer-velocity update exists in frozen source.',
            'mechanics':'FNV1a state checkpoints and force traces; observation changes must preserve mechanics.'},
        'compiler':subprocess.check_output(['g++','--version'],text=True).splitlines()[0],
        'flags':FLAGS,'references':refs,'inputs':[record(p) for p in dict.fromkeys(paths)],
        'historical_audio_or_features_used':False,'numeric_fit':False,'default_promoted':False,
        'interpretation':'Authored causal observation/hardness ablations on TRAIN only; none is a proposed preset or perceptual latency estimate.'}
    write(OUT/'freeze.json',config)


def render():
    d=locked();binary=OUT/'probe';build=OUT/'build.json'
    if build.exists():verify([read(build)['binary']])
    else:
        command=['g++',*FLAGS,'-I',str(OUT/'source'),str(ROOT/'tools/probe_full_attack_timing.cpp'),'-o',str(binary)]
        call=subprocess.run(command,capture_output=True,text=True)
        (OUT/'compile.log').write_text(call.stdout+call.stderr)
        if call.returncode:raise RuntimeError('Compile failed')
        write(build,{'binary':record(binary),'command':command,'driver':record(ROOT/'tools/probe_full_attack_timing.cpp'),
            'source':record(OUT/'source/grand.cpp'),'header':record(OUT/'source/calibration.h')})
    folder=OUT/'renders';folder.mkdir(exist_ok=True)
    def one(pair):
        variant,(ident,velocity)=pair;prefix=folder/(variant+'-'+ident);receipt=Path(str(prefix)+'-receipt.json')
        if receipt.exists():
            old=read(receipt);verify(old['outputs']);verify([old['binary'],old['freeze']]);return old
        if Path(str(prefix)+'.wav').exists():raise ValueError('Unreceipted output must be inspected')
        command=[str(binary),variant,str(velocity),str(prefix)]
        subprocess.run(command,check=True,capture_output=True,text=True)
        outputs=[record(str(prefix)+suffix) for suffix in ('.wav','-primary.wav','-secondary.wav','-transient.wav','-trace.csv','.json')]
        result={'variant':variant,'id':ident,'command':command,'binary':record(binary),'freeze':record(OUT/'freeze.json'),
            'outputs':outputs,'metrics':read(str(prefix)+'.json')}
        write(receipt,result);print(variant+' '+ident+' complete',flush=True);return result
    pairs=[(variant,item) for variant in VARIANTS for item in (('A0v4',40),('A0v12',93))]
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(one,pairs))
    locked();write(OUT/'renders.json',{'completed_at_utc':now(),'freeze':record(OUT/'freeze.json'),
        'build':record(build),'renders':results})


def envelope_diagnostics(x,sr,onset=None):
    if onset is None:onset,detail=fit.benchmark.onset_index(x,sr)
    else:_,detail=fit.benchmark.onset_index(x,sr)
    aligned=x[onset:];power=np.mean(aligned*aligned,axis=1);limit=min(len(aligned),round(.15*sr))
    results={}
    for ms in (1,2,5,10):
        env=np.sqrt(np.maximum(ndimage.uniform_filter1d(power,max(3,round(ms*.001*sr)),mode='nearest'),0))
        peak=float(np.max(env[:limit]));index=int(np.argmax(env[:limit]));cross={}
        for threshold in (.10,.50,.75,.80,.85,.90,.95):
            indices=np.flatnonzero(env[:limit]>=threshold*peak);cross[str(threshold)]=float(indices[0]/sr)
        first20=float(np.max(env[:round(.020*sr)]));first25=float(np.max(env[:round(.025*sr)]))
        results[str(ms)]={'crossings_seconds':cross,'rise10_90_seconds':cross['0.9']-cross['0.1'],
            'peak_seconds':index/sr,'peak_rms':peak,'first20ms_peak_fraction':first20/peak,
            'first25ms_peak_fraction':first25/peak,
            'first20ms_peak_to90pct_amplitude_db':20*np.log10(.9*peak/max(first20,1e-30))}
    energy=np.cumsum(power[:limit]);energy_cross={}
    for fraction in (.1,.5,.9):energy_cross[str(fraction)]=float(np.searchsorted(energy,fraction*energy[-1])/sr)
    return {'onset_frame':onset,'onset_seconds':onset/sr,'onset_details':detail,
        'smoothing_ms':results,'first150ms_energy_crossings_seconds':energy_cross}


def texture(x,sr,onset,gain):
    result=[];aligned=x[onset:]*gain
    for lo,hi in ((0,.005),(.005,.020),(.020,.050),(.050,.100)):
        section=aligned[round(lo*sr):round(hi*sr)]
        f,p=fit.benchmark.spectrum(section,sr)
        bands=[fit.benchmark.integrated_power(f,p,a,b) for a,b in ((31.25,250),(250,1000),(1000,4000),(4000,12000),(12000,19000))]
        mask=(f>=250)&(f<19000)
        result.append({'window_seconds':[lo,hi],'band_power':bands,
            'centroid_250_19000_hz':float(f[mask]@p[mask]/max(float(np.sum(p[mask])),1e-30)),
            'rms':float(np.sqrt(np.mean(section*section)))})
    return result


def measure(path,gain,reference):
    sr,x=fit.benchmark.load_audio(path);onset,_=fit.benchmark.onset_index(x,sr)
    diagnostics=envelope_diagnostics(x,sr,onset)
    actual=texture(x,sr,onset,gain)
    for m,r in zip(actual,reference):
        m['band_error_db']=(10*np.log10(np.maximum(m['band_power'],1e-30)/np.maximum(r['band_power'],1e-30))).tolist()
        m['reference_prominent_mask']=(np.asarray(r['band_power'])/max(sum(r['band_power']),1e-30)>1e-5).tolist()
        m['centroid_log2_ratio']=float(np.log2(max(m['centroid_250_19000_hz'],1)/max(r['centroid_250_19000_hz'],1)))
    return {'audio':record(path),'fixed_gain':gain,'envelope':diagnostics,'texture':actual}


def analyze():
    d=locked();batch=read(OUT/'renders.json');verify([batch['freeze'],batch['build']])
    for r in batch['renders']:verify(r['outputs'])
    rows,_=fit.training_inputs(fit.DEFAULT_REFERENCE,fit.DEFAULT_SPLIT);refs={r['id']:r for r in rows}
    scores={name:read(folder/'score.json') for name,folder in SCORES.items()}
    cached={};references={};arrays={}
    for ident in IDS:
        reference_path=next(Path(r['audio']['path']) for r in d['references'] if r['id']==ident)
        sr,x=fit.benchmark.load_audio(reference_path);onset,_=fit.benchmark.onset_index(x,sr)
        reftexture=texture(x,sr,onset,1.)
        references[ident]={'audio':record(reference_path),'envelope':envelope_diagnostics(x,sr,onset),'texture':reftexture}
        arrays[(ident,'real')]=(x,onset)
        cached[ident]={}
        for label,folder in FOLDERS.items():
            comp=next(r for r in scores[label]['comparison'] if r['id']==ident)
            path=folder/(ident+'.wav')
            if sha(path)!=comp['model_sha256']:raise ValueError('Cached scored identity differs')
            cached[ident][label]=measure(path,10**(comp['early_gain_db']/20),reftexture)
            _,xx=fit.benchmark.load_audio(path);oo=cached[ident][label]['envelope']['onset_frame'];arrays[(ident,label)]=(xx,oo)
    new=[];mechanical=[]
    for row in batch['renders']:
        ident,variant=row['id'],row['variant'];prefix=OUT/'renders'/(variant+'-'+ident)
        comp=next(r for r in scores['v4']['comparison'] if r['id']==ident)
        measured=measure(str(prefix)+'.wav',10**(comp['early_gain_db']/20),references[ident]['texture'])
        sr,x=fit.benchmark.load_audio(str(prefix)+'.wav');array_onset=measured['envelope']['onset_frame']
        arrays[(ident,variant+'-short')]=(x,array_onset)
        baseline=next(r for r in batch['renders'] if r['id']==ident and r['variant']=='v4')
        force=np.loadtxt(str(prefix)+'-trace.csv',delimiter=',',skiprows=1)
        baseline_force=np.loadtxt(OUT/'renders'/('v4-'+ident+'-trace.csv'),delimiter=',',skiprows=1)
        state_exact=row['metrics']['mechanical_hash_checkpoints']==baseline['metrics']['mechanical_hash_checkpoints']
        force_exact=np.array_equal(force,baseline_force)
        mechanical.append({'id':ident,'variant':variant,'mechanical_checkpoints_exact_to_v4':state_exact,
            'force_hammer_trace_exact_to_v4':force_exact,'max_force_trace_difference_N':float(np.max(np.abs(force[:,1]-baseline_force[:,1]))),
            'metrics':row['metrics']})
        if variant not in ('v4','hardness-prior') and (not state_exact or not force_exact):raise ValueError('Observation ablation changed mechanics')
        if variant=='v4':
            _,long=fit.benchmark.load_audio(FOLDERS['v4']/(ident+'.wav'))
            if not np.array_equal(x,long[:len(x)]):raise ValueError('Short V4 output differs from frozen prefix')
        if variant=='analytic-observation':
            _,long=fit.benchmark.load_audio(FOLDERS['analytic']/(ident+'.wav'))
            if not np.array_equal(x,long[:len(x)]):raise ValueError('Zero correction differs from frozen analytic prefix')
        stems=[]
        for suffix in ('-primary.wav','-secondary.wav','-transient.wav'):
            _,part=fit.benchmark.load_audio(str(prefix)+suffix);stems.append(part)
        reconstruction=float(np.max(np.abs(sum(stems)-x)))
        cross=[]
        for lo,hi in ((0,.005),(.005,.020),(.020,.050),(.050,.100),(.100,.150)):
            ss=[s[array_onset+round(lo*sr):array_onset+round(hi*sr)] for s in stems]
            powers=[float(np.mean(s*s)) for s in ss]
            pairs=[float(2*np.mean(ss[a]*ss[b])) for a,b in ((0,1),(0,2),(1,2))]
            cross.append({'window_seconds':[lo,hi],'stem_mean_square':powers,'twice_pair_cross_terms':pairs,
                'sum_coherent_power':sum(powers)+sum(pairs),'incoherent_stem_power':sum(powers)})
        new.append({'id':ident,'variant':variant,**measured,'metrics':row['metrics'],
            'stem_reconstruction_maximum_abs_error':reconstruction,'stem_coherent_power':cross})
    analytic_profile=read(ROOT/'out/full-calibration/v4/analytic/calibration.json')
    final_profile=read(ROOT/'out/full-calibration/v4/radiation/calibration.json')
    physical_exact=all({k:v for k,v in a.items() if k not in ('radiation_db','radiation_after_db')}==
                       {k:v for k,v in b.items() if k not in ('radiation_db','radiation_after_db')}
                       for a,b in zip(analytic_profile['keys'],final_profile['keys']))
    mechanics_fields=('max_hammer_force_N','accumulated_contact_seconds','contact_solves','contact_max_relative_residual','final_mechanical_energy_J')
    old_mechanics=[]
    for ident in IDS:
        a=read(FOLDERS['analytic']/(ident+'.json'))['metrics'];b=read(FOLDERS['v4']/(ident+'.json'))['metrics']
        old_mechanics.append({'id':ident,'all_fields_exact':all(a[k]==b[k] for k in mechanics_fields),
            'fields':{k:{'analytic':a[k],'v4':b[k]} for k in mechanics_fields}})
    result={'schema_version':1,'analyzed_at_utc':now(),'freeze':record(OUT/'freeze.json'),'batch':record(OUT/'renders.json'),
        'references':references,'cached':cached,'new':new,'mechanical_checks':mechanical,
        'existing_analytic_vs_v4_mechanics':old_mechanics,'existing_analytic_vs_v4_physical_key_fields_exact':physical_exact,
        'reference_roles':'Locked TRAIN only; historical audio/features were never opened by this diagnostic.',
        'metric_interpretation':'RMS-envelope relative crossings measure output peak structure, not hammer-contact duration or perceived latency.',
        'numeric_fit':False,'default_promoted':False}
    locked();write(OUT/'report.json',result);write(ROOT/'Validation/full-attack-timing.json',result)
    plot(result,arrays)
    for row in new:
        env=row['envelope']['smoothing_ms']['5']
        print(row['id'],row['variant'],'rise_ms',round(env['rise10_90_seconds']*1000,3),
            't50_ms',round(env['crossings_seconds']['0.5']*1000,3),'first20fraction',round(env['first20ms_peak_fraction'],5),flush=True)


def plot(report,arrays):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,3,figsize=(14,7),constrained_layout=True)
    for row,ident in enumerate(('A0v4','A0v12')):
        for label in ('real','original','analytic','v4','confidence'):
            x,onset=arrays[(ident,label)];power=np.mean(x[onset:]*x[onset:],axis=1)
            env=np.sqrt(np.maximum(ndimage.uniform_filter1d(power,240,mode='nearest'),0))[:7200]
            axes[row,0].plot(np.arange(len(env))/48,env/max(env),label=label,alpha=.85)
        for variant in VARIANTS:
            x,onset=arrays[(ident,variant+'-short')];power=np.mean(x[onset:]*x[onset:],axis=1)
            env=np.sqrt(np.maximum(ndimage.uniform_filter1d(power,240,mode='nearest'),0))[:7200]
            axes[row,1].plot(np.arange(len(env))/48,env/max(env),label=variant,alpha=.85)
        for variant in ('v4','hardness-prior'):
            trace=np.loadtxt(OUT/'renders'/(variant+'-'+ident+'-trace.csv'),delimiter=',',skiprows=1)
            axes[row,2].plot((trace[:,0]-4800)/48,trace[:,1],label=variant)
        axes[row,0].set_title(ident+' cached:5ms RMS /150ms peak');axes[row,1].set_title(ident+' authored diagnostic ablations')
        axes[row,2].set_title(ident+' hammer contact force');axes[row,2].set_xlim(-.5,8)
        for col in (0,1):axes[row,col].axhline(.9,color='gray',linestyle='--',linewidth=.7);axes[row,col].set_xlim(0,150)
        for col in range(3):axes[row,col].set_xlabel('ms after detected onset' if col<2 else 'ms after actual MIDI event');axes[row,col].grid(alpha=.15)
        axes[row,0].set_ylabel('normalized output RMS');axes[row,2].set_ylabel('N')
    for ax in axes[0]:ax.legend(fontsize=7)
    fig.suptitle('TRAIN-only attack diagnostic: relative output crossings are not hammer latency')
    for suffix in ('.svg','.png'):fig.savefig(ROOT/'Validation'/('full-attack-timing'+suffix),dpi=150)
    plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('stage',choices=('freeze','render','analyze','run','verify'))
    args=parser.parse_args()
    if args.stage in ('freeze','run'):freeze()
    if args.stage in ('render','run'):render()
    if args.stage in ('analyze','run'):analyze()
    if args.stage=='verify':
        locked()
        if (OUT/'renders.json').exists():
            d=read(OUT/'renders.json');verify([d['freeze'],d['build']])
            for row in d['renders']:verify(row['outputs'])
        if (OUT/'report.json').exists():
            d=read(OUT/'report.json');verify([d['freeze'],d['batch']])
        print('TRAIN-only frozen sources and available outputs verified')


if __name__=='__main__':main()
