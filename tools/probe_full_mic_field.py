#!/usr/bin/env python3
"""TRAIN32-only conditional test of a bounded four-parameter pickup field.

Only relative channel gain and differential delay vary affinely with keyboard
position. This is an empirical observation fit, not recovered mic geometry.
No synthesis, canonical source, dynamics or reference recording is modified.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil

import numpy as np
from scipy import optimize, signal
from scipy.io import wavfile

ROOT=Path(__file__).resolve().parents[1]
FEATURE=ROOT/'References/GrandFullRange/combined_train_features.json'
SPLIT=ROOT/'References/GrandFullRange/split.json'
ALLOWED={f'{p}v{v}' for p in ('A0','C1','A1','C2','D#2','A2','C3','D#3','C4','D#4','A4','C5','D#5','A5','C6','C7') for v in (4,12)}
MOMENTS=9
GATES={'relative_power_min':1e-4,'band_to_local_noise_min_db':10.,'coherence_squared_min':.5,
       'minimum_channel_power_fraction':.02,'maximum_frequency_hz':12000.,'minimum_frequency_hz':25.,
       'minimum_neighbor_spacing_times_window':4.,'moment_absolute_error_max':1e-7}


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def position(note):return (np.asarray(note)-21)/87.
def field(endpoints,notes):
    x=position(notes);return endpoints[0]*(1-x)+endpoints[1]*x
def fractional_weights(f,lo,hi):
    df=f[1]-f[0];return np.clip((np.minimum(f+df/2,hi)-np.maximum(f-df/2,lo))/df,0,1)


def spectrum(x,rate):
    n=len(x);w=signal.windows.hann(n,sym=False);nfft=1<<math.ceil(math.log2(n*2))
    z=np.fft.rfft(x*w[:,None],nfft,axis=0);f=np.fft.rfftfreq(nfft,1/rate)
    scale=2/(nfft*np.sum(w*w));pl=abs(z[:,0])**2*scale;pr=abs(z[:,1])**2*scale;c=z[:,0]*z[:,1].conj()*scale
    pl[[0,-1]]*=.5;pr[[0,-1]]*=.5;c[[0,-1]]*=.5
    return f,pl,pr,c


def band_data(spec,center,width,spacing,early_power):
    f,pl,pr,c=spec;weight=fractional_weights(f,center-width,center+width);valid=weight>0
    if not np.any(valid):return None
    left=float(np.dot(weight,pl));right=float(np.dot(weight,pr));cross=complex(np.dot(weight,c));total=left+right
    noise_weight=sum(fractional_weights(f,center+s*.5*spacing-.1*spacing,center+s*.5*spacing+.1*spacing) for s in (-1,1))
    noise=float(np.dot(noise_weight,pl+pr)/max(noise_weight.sum(),1e-30))
    signal_density=total/max(weight.sum(),1e-30)
    return {'pl':left,'pr':right,'cross':cross,'total':total,
        'relative_power':total/max(2*early_power,1e-30),
        'snr_db':float(10*np.log10(max(signal_density,1e-30)/max(noise,1e-30))),
        'coh':min(1.,abs(cross)**2/max(left*right,1e-60)),
        'channel_fraction':min(left,right)/max(total,1e-30),
        'frequencies':f[valid],'cross_bins':weight[valid]*c[valid]}


def normalize_weights(records):
    weights=np.array([min(row['raw_weight'],.2) for row in records],float)
    # Equal windows within each velocity, equal velocities within each pitch,
    # equal pitches overall. Weak/noisy bands never acquire inverse-power weight.
    for name in sorted({r['id'] for r in records}):
        indices=np.array([i for i,r in enumerate(records) if r['id']==name])
        for wi in sorted({records[i]['window'] for i in indices}):
            ix=np.array([i for i in indices if records[i]['window']==wi]);weights[ix]/=weights[ix].sum()
        weights[indices]/=weights[indices].sum()
    for note in sorted({r['midi'] for r in records}):
        ix=np.array([i for i,r in enumerate(records) if r['midi']==note]);weights[ix]/=weights[ix].sum()
    return weights/weights.sum()


def extract(rows,model_dir,fitter):
    manifest=json.loads((model_dir/'render-manifest.json').read_text())
    if manifest.get('complete') is not True or manifest.get('errors'):raise ValueError('Final render batch is incomplete')
    if manifest['reference_features_sha256']!=sha(FEATURE) or manifest['split_sha256']!=sha(SPLIT):raise ValueError('Render reference/split identity mismatch')
    engine=Path(manifest['engine_path']);source=Path(manifest['source_path']);header=source.parent/'calibration.h'
    if any(sha(path)!=manifest[key] for key,path in [('engine_sha256',engine),('source_sha256',source),('calibration_sha256',header)]):raise ValueError('Actual model source/header/binary mismatch')
    records=[];receipts=[];rejections={};audio={}
    for row in rows:
        name=row['id']
        if name not in ALLOWED:raise ValueError('Reference PCM request outside explicit TRAIN32 whitelist')
        reference=fitter.reference_audio(row,FEATURE)
        receipt=fitter.reference_audio_identity(row,reference)
        model=model_dir/(name+'.wav');sidecar=json.loads((model_dir/(name+'.json')).read_text())
        if sidecar['output_sha256'][model.name]!=sha(model):raise ValueError('Model WAV hash mismatch: '+name)
        for key in ('source_sha256','calibration_sha256','engine_sha256','reference_features_sha256','split_sha256'):
            if sidecar['inputs'][key]!=manifest[key]:raise ValueError('Per-render identity mismatch: '+name)
        sr,ref=fitter.benchmark.load_audio(reference);mr,mod=fitter.benchmark.load_audio(model)
        if sr!=mr or sr!=48000 or ref.shape[1]!=2 or mod.shape[1]!=2:raise ValueError('Expected native48k stereo')
        ro=int(round(row['onset_seconds']*sr));mo,_=fitter.benchmark.onset_index(mod,sr)
        ref=ref[ro:];mod=mod[mo:]
        windows=row.get('analysis_windows_seconds',[[.05,.25],[.25,.75],[.75,1.5],[1.5,3.5]])
        if min(len(ref),len(mod))<math.ceil(max(b for a,b in windows)*sr):raise ValueError('Insufficient recorded support; no padding allowed')
        re=float(np.mean(ref[int(.05*sr):int(.75*sr)]**2));me=float(np.mean(mod[int(.05*sr):int(.75*sr)]**2))
        receipt.update({'model_wave_path':str(model),'model_wave_sha256':sha(model),'model_sidecar_sha256':sha(model_dir/(name+'.json')),
            'reference_common_onset_seconds':ro/sr,'model_common_onset_seconds':mo/sr})
        receipts.append(receipt);audio[name]={'rate':sr,'reference':ref[:int(3.5*sr)],'model':mod[:int(3.5*sr)]}
        centers=np.array([p['frequency_hz'] for p in row['partials']])
        rejected={};accepted=0
        for wi,(lo,hi) in enumerate(windows):
            rs=spectrum(ref[int(lo*sr):int(hi*sr)],sr);ms=spectrum(mod[int(lo*sr):int(hi*sr)],sr)
            for i,partial in enumerate(row['partials']):
                center=partial['frequency_hz'];spacing=min(center-centers[i-1] if i else row['f1_hz'],centers[i+1]-center if i+1<len(centers) else row['f1_hz'])
                if center<GATES['minimum_frequency_hz'] or center>GATES['maximum_frequency_hz'] or spacing*(hi-lo)<GATES['minimum_neighbor_spacing_times_window']:
                    rejected['frequency_or_resolution']=rejected.get('frequency_or_resolution',0)+1;continue
                width=min(.3*spacing,max(2/(hi-lo),.003*center))
                r=band_data(rs,center,width,spacing,re);m=band_data(ms,center,width,spacing,me)
                reason=None
                if min(r['relative_power'],m['relative_power'])<GATES['relative_power_min']:reason='quiet'
                elif min(r['snr_db'],m['snr_db'])<GATES['band_to_local_noise_min_db']:reason='local_noise'
                elif min(r['coh'],m['coh'])<GATES['coherence_squared_min']:reason='low_band_coherence'
                elif min(r['channel_fraction'],m['channel_fraction'])<GATES['minimum_channel_power_fraction']:reason='weak_channel'
                if reason:rejected[reason]=rejected.get(reason,0)+1;continue
                df=m['frequencies']-center
                moments=np.array([np.sum(m['cross_bins']*(1j*2*np.pi*df*.001)**k/math.factorial(k))/m['total'] for k in range(MOMENTS)])
                records.append({'id':name,'midi':row['midi'],'layer':row['layer'],'n':partial['n'],'window':wi,'center_hz':center,'width_hz':width,
                    'raw_weight':r['relative_power'],'reference_pl':r['pl']/r['total'],'reference_pr':r['pr']/r['total'],'reference_cross':r['cross']/r['total'],
                    'model_pl':m['pl']/m['total'],'model_pr':m['pr']/m['total'],'model_cross':m['cross']/m['total'],'moments':moments,
                    'frequencies':m['frequencies'],'cross_bins':m['cross_bins']/m['total'],
                    'reference_band_coherence_squared':r['coh'],'model_band_coherence_squared':m['coh'],
                    'reference_snr_db':r['snr_db'],'model_snr_db':m['snr_db']})
                accepted+=1
        rejections[name]={'accepted':accepted,'rejected':rejected}
        print('extracted',name,accepted,flush=True)
    if {r['id'] for r in records}!=ALLOWED:raise ValueError('Every permitted case must retain some reliable observation')
    return records,receipts,rejections,audio,{'source':str(source),'source_sha256':sha(source),'header':str(header),'header_sha256':sha(header),
        'binary':str(engine),'binary_sha256':sha(engine),'manifest_sha256':sha(model_dir/'render-manifest.json')}


class Data:
    def __init__(self,records):
        self.records=records;self.notes=np.array([r['midi'] for r in records]);self.x=position(self.notes)
        self.center=np.array([r['center_hz'] for r in records]);self.weight=normalize_weights(records)
        self.pl=np.array([r['model_pl'] for r in records]);self.pr=np.array([r['model_pr'] for r in records])
        self.rl=np.array([r['reference_pl'] for r in records]);self.rr=np.array([r['reference_pr'] for r in records]);self.rc=np.array([r['reference_cross'] for r in records])
        self.mom=np.array([r['moments'] for r in records]);self.mc=self.mom[:,0]
    def prediction(self,gain,delay,exact=False):
        g=field(gain,self.notes);t=field(delay,self.notes)
        l=self.pl*10**(-g/20);r=self.pr*10**(g/20);total=l+r
        if exact:
            c=np.array([np.sum(row['cross_bins']*np.exp(1j*2*np.pi*row['frequencies']*.001*dt)) for row,dt in zip(self.records,t)])
        else:
            c=self.mom[:,-1].copy()
            for k in range(MOMENTS-2,-1,-1):c=c*t+self.mom[:,k]
            c*=np.exp(1j*2*np.pi*self.center*.001*t)
        return l/total,r/total,c/total,total
    def objective(self,gain,delay,mask):
        l,r,c,_=self.prediction(gain,delay)
        w=self.weight[mask];w=w/w.sum()
        error=(l-self.rl)**2+(r-self.rr)**2+2*abs(c-self.rc)**2
        return float(w@error[mask])


def fit(data,mask,with_delay,seed=20261026):
    x=data.x[mask];design=np.column_stack([1-x,x]);w=data.weight[mask];w=w/w.sum()
    target=10*np.log10(data.rr[mask]/data.rl[mask])-10*np.log10(data.pr[mask]/data.pl[mask])
    gain=optimize.lsq_linear(design*np.sqrt(w[:,None]),target*np.sqrt(w),bounds=(-6,6),tol=1e-12).x
    # Materialize ONLY retained-pitch arrays in the fitting closure. Target
    # observations never enter either gain regression or delay optimization.
    pl=data.pl[mask]*10**(-field(gain,data.notes[mask])/20)
    pr=data.pr[mask]*10**(field(gain,data.notes[mask])/20);total=pl+pr
    diagonal=(pl/total-data.rl[mask])**2+(pr/total-data.rr[mask])**2
    moments=data.mom[mask];center=data.center[mask];reference=data.rc[mask]
    def objective(value):
        t=value[0]*(1-x)+value[1]*x;c=moments[:,-1].copy()
        for k in range(MOMENTS-2,-1,-1):c=c*t+moments[:,k]
        c*=np.exp(1j*2*np.pi*center*.001*t);c/=total
        return float(w@(diagonal+2*abs(c-reference)**2))
    delay=np.zeros(2);minima=[]
    if with_delay:
        search=optimize.differential_evolution(objective,[(-2,2),(-2,2)],seed=seed,popsize=12,maxiter=65,tol=1e-7,polish=False,workers=1)
        starts=[np.zeros(2),search.x]
        for index in np.argsort(search.population_energies):
            value=search.population[index]
            if all(np.linalg.norm(value-s)>.05 for s in starts):starts.append(value)
            if len(starts)>=6:break
        for start in starts:
            polished=optimize.minimize(objective,start,method='L-BFGS-B',bounds=[(-2,2),(-2,2)],options={'ftol':1e-13,'gtol':1e-8,'maxiter':100})
            minima.append({'delay_endpoints_ms':polished.x.tolist(),'objective':float(polished.fun)})
        minima.sort(key=lambda row:row['objective']);delay=np.array(minima[0]['delay_endpoints_ms'])
    return {'gain_endpoints_db':gain.tolist(),'delay_endpoints_ms':delay.tolist(),'objective':objective(delay),
        'bound_hit':bool(np.max(abs(gain))>5.999 or np.max(abs(delay))>1.999),
        'delay_minima':minima}


def metrics(data,prediction,mask):
    l,r,c,power=prediction;w=data.weight[mask];w=w/w.sum()
    covariance=np.sqrt((l-data.rl)**2+(r-data.rr)**2+2*abs(c-data.rc)**2)
    balance=abs(10*np.log10(np.maximum(r,1e-30)/np.maximum(l,1e-30))-10*np.log10(data.rr/data.rl))
    phase=abs(np.angle(c*data.rc.conj()))*180/np.pi
    coherence=np.minimum(1,abs(c)**2/np.maximum(l*r,1e-30));refcoh=abs(data.rc)**2/(data.rl*data.rr)
    return {'observations':int(mask.sum()),'weighted_covariance_frobenius_error':float(w@covariance[mask]),
        'weighted_absolute_balance_error_db':float(w@balance[mask]),'weighted_absolute_cross_phase_error_degrees':float(w@phase[mask]),
        'weighted_absolute_band_coherence_squared_error':float(w@abs(coherence-refcoh)[mask]),
        'weighted_absolute_model_power_change_db':float(w@abs(10*np.log10(np.maximum(power,1e-30)))[mask])}


def self_check():
    rng=np.random.default_rng(443);records=[];truthg=np.array([1.1,-.8]);trutht=np.array([.24,-.13])
    for note in (24,36,48,60,72,84,96):
        for j,center in enumerate((85.,190.,430.,910.,1800.,3700.)):
            f=center+np.linspace(-6,6,17);z=rng.normal(size=(17,2))+1j*rng.normal(size=(17,2));z[:,1]=z[:,0]*(.7+.3j)+.08*z[:,1]
            pl=float(sum(abs(z[:,0])**2));pr=float(sum(abs(z[:,1])**2));cb=z[:,0]*z[:,1].conj();total=pl+pr
            g=float(field(truthg,note));t=float(field(trutht,note));l=pl*10**(-g/20);r=pr*10**(g/20);c=sum(cb*np.exp(1j*2*np.pi*f*.001*t));rt=l+r
            moment=np.array([sum(cb*(1j*2*np.pi*(f-center)*.001)**k/math.factorial(k))/total for k in range(MOMENTS)])
            records.append({'id':str(note),'midi':note,'window':0,'center_hz':center,'raw_weight':1.,'model_pl':pl/total,'model_pr':pr/total,'model_cross':sum(cb)/total,
                'reference_pl':l/rt,'reference_pr':r/rt,'reference_cross':c/rt,'moments':moment,'cross_bins':cb/total,'frequencies':f})
    data=Data(records);mask=np.ones(len(records),bool);fitted=fit(data,mask,True)
    gerr=float(np.max(abs(np.array(fitted['gain_endpoints_db'])-truthg)));terr=float(np.max(abs(np.array(fitted['delay_endpoints_ms'])-trutht)))
    maximum_moment_error=0
    for t in np.linspace(-2,2,9):
        approx=data.prediction([0,0],[t,t])[2];exact=data.prediction([0,0],[t,t],True)[2]
        maximum_moment_error=max(maximum_moment_error,float(np.max(abs(approx-exact))))
    z=np.array([1+.3j,.2-1.1j]);omega=2*np.pi*433.;common=np.exp(-1j*omega*.017)
    common_error=float(abs(z[0]*z[1].conj()-(z[0]*common)*(z[1]*common).conj()))
    train=data.notes!=60
    clean=fit(data,train,True,seed=91)
    poisoned=[]
    for row in records:
        row=dict(row)
        if row['midi']==60:
            row.update(reference_pl=.999,reference_pr=.001,reference_cross=.01j,model_pl=.001,model_pr=.999,
                center_hz=999999.,moments=np.full(MOMENTS,3+4j),raw_weight=1e20)
        poisoned.append(row)
    dirty=fit(Data(poisoned),train,True,seed=91)
    poison_error=max(float(np.max(abs(np.array(clean[key])-np.array(dirty[key])))) for key in ('gain_endpoints_db','delay_endpoints_ms'))
    endpoint_bounds=bool(np.max(abs(field([-6,6],np.arange(21,109))))<=6 and np.max(abs(field([-2,2],np.arange(21,109))))<=2)
    passed=gerr<1e-7 and terr<1e-5 and maximum_moment_error<1e-7 and common_error<1e-12 and poison_error<1e-12 and endpoint_bounds
    if not passed:raise AssertionError({'gain_error':gerr,'delay_error_ms':terr,'moment_error':maximum_moment_error})
    return {'passed':passed,'known_gain_endpoint_error_db':gerr,'known_delay_endpoint_error_ms':terr,
        'maximum_moment_vs_per_bin_error':maximum_moment_error,'common_channel_shift_cross_spectrum_error':common_error,
        'omitted_pitch_target_poison_parameter_difference':poison_error,'full_keyboard_endpoint_bounds_passed':endpoint_bounds,
        'phase_convention':'C=ZL*conj(ZR); positiveR-minus-L delay multiplies C by exp(+i2pi f tau).'}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--model-dir',type=Path,default=ROOT/'out/full-calibration/v4/final-renders')
    p.add_argument('--output-dir',type=Path,default=ROOT/'out/full-mic-study');args=p.parse_args();folder=args.output_dir.resolve()
    if (ROOT/'out').resolve() not in folder.parents:p.error('Research outputs must stay under out/')
    folder.mkdir(parents=True,exist_ok=True);checks=self_check()
    fitter=module('keyra_mic_pcm_guard',ROOT/'tools/fit_full_calibration.py');rows,notes=fitter.training_inputs(FEATURE,SPLIT)
    rows=[r for r in rows if r['midi']!=108]
    if {r['id'] for r in rows}!=ALLOWED or any(r.get('pitch_identity_ambiguous',False) for r in rows):raise ValueError('TRAIN32 whitelist or unambiguous pitch inventory mismatch')
    inputs={name:{'path':str(path),'sha256':sha(path)} for name,path in [('features',FEATURE),('split',SPLIT),('pcm_guard',ROOT/'tools/fit_full_calibration.py'),('analysis',Path(__file__))]}
    for name,item in inputs.items():shutil.copyfile(item['path'],folder/(name+Path(item['path']).suffix))
    records,receipts,rejections,audio,model_identity=extract(rows,args.model_dir,fitter);data=Data(records);allmask=np.ones(len(records),bool)
    baseline=data.prediction([0,0],[0,0],True)
    predictions={name:tuple(np.zeros(len(records),dtype=complex if k==2 else float) for k in range(4)) for name in ('gain_only','gain_delay')}
    folds=[]
    for note in sorted({r['midi'] for r in records}):
        train=data.notes!=note;test=~train;fold={'omitted_midi':int(note),'omitted_ids':sorted(r['id'] for r in rows if r['midi']==note),
            'baseline_omitted_pitch_metrics':metrics(data,baseline,test),'models':{}}
        for label,delay in [('gain_only',False),('gain_delay',True)]:
            fitted=fit(data,train,delay);pred=data.prediction(fitted['gain_endpoints_db'],fitted['delay_endpoints_ms'],True)
            for k in range(4):predictions[label][k][test]=pred[k][test]
            fold['models'][label]={**fitted,'omitted_pitch_metrics':metrics(data,pred,test)}
        folds.append(fold);print('fold',note,{k:v['omitted_pitch_metrics']['weighted_covariance_frobenius_error'] for k,v in fold['models'].items()},flush=True)
    x=np.clip((data.notes-64.5)/52,-.85,.85);pl=(1-.588*x)**2;pr=(1+.588*x)**2;tr=pl+pr
    pan=(pl/tr,pr/tr,np.sqrt(pl*pr)/tr,np.ones(len(records)))
    summary={'actual_full_model':metrics(data,baseline,allmask),'rank_one_keyboard_pan_diagnostic':metrics(data,pan,allmask),
        **{label:metrics(data,pred,allmask) for label,pred in predictions.items()}}
    fullfits={label:fit(data,allmask,delay) for label,delay in [('gain_only',False),('gain_delay',True)]}
    pre_gain_approximation_bound=max(float(np.sum(abs(row['cross_bins']))*math.exp(a)*a**MOMENTS/math.factorial(MOMENTS))
        for row in records for a in [2*np.pi*np.max(abs(row['frequencies']-row['center_hz']))*.002])
    # Trace normalization can amplify the cross-term approximation by at most
    # 10^(6/20), since each permitted power gain is at least10^(-6/20).
    approximation_bound=pre_gain_approximation_bound*10**(6/20)
    approximation_error=0
    for fitted in fullfits.values():
        a=data.prediction(fitted['gain_endpoints_db'],fitted['delay_endpoints_ms'])[2];b=data.prediction(fitted['gain_endpoints_db'],fitted['delay_endpoints_ms'],True)[2]
        approximation_error=max(approximation_error,float(np.max(abs(a-b))))
    if approximation_error>GATES['moment_absolute_error_max']:raise AssertionError('Fast delay objective approximation failed exact per-bin check')
    if approximation_bound>GATES['moment_absolute_error_max']:raise AssertionError('Fast delay objective Taylor remainder bound is too large')
    retained=[]
    base=summary['actual_full_model']
    for label in ('gain_only','gain_delay'):
        s=summary[label]
        wins=sum(f['models'][label]['omitted_pitch_metrics']['weighted_covariance_frobenius_error'] < metrics(data,baseline,data.notes==f['omitted_midi'])['weighted_covariance_frobenius_error'] for f in folds)
        s['pitch_covariance_wins_out_of16']=wins
        if s['weighted_covariance_frobenius_error']<.98*base['weighted_covariance_frobenius_error'] and s['weighted_absolute_balance_error_db']<base['weighted_absolute_balance_error_db']-.25 and wins>=10 and s['weighted_absolute_band_coherence_squared_error']<=base['weighted_absolute_band_coherence_squared_error']+.005:
            retained.append(label)
    report={'schema_version':1,'training_ids':sorted(ALLOWED),'excluded_ambiguous_C8_ids':['C8v4','C8v12'],'reserved_audio_or_features_used':False,
        'input_identities':inputs,'model_identity':model_identity,'reference_pcm_and_model_receipts':receipts,'known_signal_checks':checks,
        'gates':GATES,'rejections':rejections,'observations':len(records),'parameters':'RelativeR/Lgain in dB and R-minus-L differentialdelay in ms each affine between MIDI21/108, bounded at endpoints to±6dB/±2ms. No per-case gain/phase fit.',
        'estimator':'Single Hann complex band-integrated covariance; delay applied per frequency bin before integration. Band coherence is descriptive spectral concentration, not an independent-realization statistical coherence estimate.',
        'delay_optimizer':'Balance-first procedure: gain endpoints fit weightedR/LdB balance, then are fixed while delay minimizes bounded circular covariance. This is not a joint four-parameter covariance optimum. Differential-evolution seed20261026 plus zero/multiple local starts; no phase unwrapping.8th-order centered moments accelerate fitting; exact per-bin projections score every fold.',
        'validation_scope':'Conditional leave-one-pitch-out correction test: both velocities/all windows of target pitch excluded from gain/delay fitting. Target band masks/covariances are evaluation-only. Fixed full physical base was already calibrated on allTRAIN pitches; not end-to-end unseen-pitch validation.',
        'alignment':'Each file uses one sharedL/R onset index only. Neither independent channel onset nor ref/model carrier phase enters the phase target.',
        'weighting':'Equal pitch totals; equal velocity totals and available-window totals within each pitch, with capped reference partial-power weights inside a window.',
        'summary':summary,'folds':folds,'full_training_fits':fullfits,'maximum_moment_vs_exact_projection_error':approximation_error,
        'maximum_moment_taylor_remainder_bound_over_full_delay_box':approximation_bound,
        'pre_gain_moment_taylor_remainder_bound':pre_gain_approximation_bound,
        'window_and_velocity_slices':{group:{str(value):{'actual_full_model':metrics(data,baseline,np.array([r[group]==value for r in records])),
            **{label:metrics(data,pred,np.array([r[group]==value for r in records])) for label,pred in predictions.items()}}
            for value in sorted({r[group] for r in records})} for group in ('window','layer')},
        'delay_fit_diagnostics':{'fold_bound_hits':sum(f['models']['gain_delay']['bound_hit'] for f in folds),
            'full_training_bound_hit':fullfits['gain_delay']['bound_hit'],
            'fold_delay_endpoint_ranges_ms':np.column_stack([np.min([f['models']['gain_delay']['delay_endpoints_ms'] for f in folds],axis=0),np.max([f['models']['gain_delay']['delay_endpoints_ms'] for f in folds],axis=0)]).tolist()},
        'retained_research_candidates':retained,'decision':'Retain bounded research observation candidate for listening only.' if retained else 'Reject the tested balance-first gain/delay procedure: no tested candidate meets the predefined conditionalCV covariance/balance/coherence gates. This does not exhaust possible affine-field objectives.',
        'retention_gate':'At least2% covariance improvement and0.25dB balance improvement; at least10/16 pitch covariance wins; no >.005 mean band-coherence-error regression. Training research gate, not a perceptual or production acceptance score.',
        'limits':'Known capture usesAKGC414AB roughly12cm above strings; spacing/orientation/room unknown. Effective observation fit is not recovered microphone geometry. Source dynamics, amplitudes and recordings remain unchanged; gain changes projected stereo power and that change is reported. No new default or full-field microphone claim.'}
    # Preserve exact per-bin inputs for independent scoring without reopening PCM.
    lengths=np.array([len(r['frequencies']) for r in records]);offsets=np.r_[0,np.cumsum(lengths)]
    np.savez_compressed(folder/'observations.npz',notes=data.notes,ids=np.array([r['id'] for r in records]),
        layers=np.array([r['layer'] for r in records]),windows=np.array([r['window'] for r in records]),
        partials=np.array([r['n'] for r in records]),centers=data.center,widths=np.array([r['width_hz'] for r in records]),
        weights=data.weight,reference_l=data.rl,reference_r=data.rr,reference_c=data.rc,model_l=data.pl,model_r=data.pr,
        moments=data.mom,bin_offsets=offsets,bin_frequencies=np.concatenate([r['frequencies'] for r in records]),
        model_cross_bins=np.concatenate([r['cross_bins'] for r in records]))
    save(folder/'measurements.json',[{**{k:r[k] for k in ('id','midi','layer','n','window','center_hz','width_hz','raw_weight',
        'reference_pl','reference_pr','model_pl','model_pr','reference_snr_db','model_snr_db','reference_band_coherence_squared','model_band_coherence_squared')},
        'reference_cross':[r['reference_cross'].real,r['reference_cross'].imag],
        'model_cross':[r['model_cross'].real,r['model_cross'].imag]} for r in records])
    for key,destination in [('source','model-source.cpp'),('header','model-calibration.h')]:shutil.copyfile(model_identity[key],folder/destination)
    shutil.copyfile(args.model_dir/'render-manifest.json',folder/'model-render-manifest.json')
    report['artifact_sha256']={name:sha(folder/name) for name in ('observations.npz','measurements.json','model-source.cpp','model-calibration.h','model-render-manifest.json')}
    save(folder/'report.json',report)
    print(json.dumps({'report':str(folder/'report.json'),'summary':summary,'retained':retained},indent=2))

if __name__=='__main__':main()
