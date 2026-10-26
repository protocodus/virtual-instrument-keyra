#!/usr/bin/env python3
"""Independent, TRAIN10-only frequency/decay estimates from acoustic recordings.

No holdout waveform is read. Fits are observations of a microphone recording,
not isolated measurements of tension, material loss, bridge mobility or SPL.
"""
from pathlib import Path
import argparse,hashlib,json,math
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,find_peaks,resample_poly,sosfiltfilt
from scipy.optimize import least_squares
ROOT=Path(__file__).resolve().parents[1]


def spectrum(x,fs,start,end,nfft=2**20):
    z=x[int(start*fs):int(end*fs)]
    z=z-np.mean(z,axis=0)
    power=np.mean(abs(np.fft.rfft(z*np.hanning(len(z))[:,None],n=nfft,axis=0))**2,axis=1)
    return np.fft.rfftfreq(nfft,1/fs),power


def interpolate_peak(i,p,df):
    y=np.log(np.maximum(p[i-1:i+2],1e-300))
    delta=.5*(y[0]-y[2])/(y[0]-2*y[1]+y[2])
    return (i+np.clip(delta,-.5,.5))*df


def fit_model(partials):
    n=np.array([r['partial'] for r in partials],float)
    freq=np.array([r['frequency_hz'] for r in partials])
    fguess=np.median(freq[:3]/n[:3])
    def cents(q):return 1200*np.log2(freq/(n*q[0]*np.sqrt((1+q[1]*n*n)/(1+q[1]))))
    fit=least_squares(cents,[fguess,.0003],bounds=([fguess*.97,0],[fguess*1.03,.02]),loss='soft_l1',f_scale=1.5,
                      xtol=1e-13,ftol=1e-13,gtol=1e-13,max_nfev=500)
    f1,B=map(float,fit.x);A=f1*f1/(1+B);C=A*B
    for r,error in zip(partials,fit.fun):r['fit_error_cents']=float(error)
    return {'fundamental_hz':f1,'engine_B':B,'normalized_B':C/(A+C),'linear_A_hz2':A,'linear_C_hz2':C,
            'rms_partial_error_cents':float(np.sqrt(np.mean(fit.fun**2))),
            'max_partial_error_cents':float(np.max(abs(fit.fun))),'partials_used':len(partials)}


def estimate_partials(x,fs,note,onset):
    f,p=spectrum(x,fs,onset+.1,min(onset+2.1,len(x)/fs-.02));df=f[1]-f[0]
    peaks,_=find_peaks(p);reference=440*2**((note-69)/12)
    ids=peaks[(f[peaks]>reference*.96)&(f[peaks]<reference*1.04)]
    dominant=f[ids[np.argmax(p[ids])]]
    def get(n,center,halfwidth):
        ids=peaks[(f[peaks]>center-halfwidth)&(f[peaks]<center+halfwidth)]
        if not len(ids):return None
        i=int(ids[np.argmax(p[ids])]);relative=float(10*np.log10(p[i]/np.max(p)))
        neighborhood=p[(f>center-.35*dominant)&(f<center+.35*dominant)]
        snr=float(10*np.log10(p[i]/max(float(np.median(neighborhood)),1e-300)))
        if relative< -60 or snr<18:return None
        return {'partial':n,'frequency_hz':float(interpolate_peak(i,p,df)),
                'relative_spectral_peak_db':relative,'local_peak_to_median_db':snr}
    partials=[]
    for n in range(1,9):
        row=get(n,n*dominant+.2*dominant,.4*dominant)
        if row:partials.append(row)
    fit=fit_model(partials)
    initial_error=fit['rms_partial_error_cents'];candidate_count=len(partials)
    outliers=[r for r in partials if abs(r['fit_error_cents'])>4]
    retained=[r for r in partials if abs(r['fit_error_cents'])<=4]
    if outliers and len(retained)>=4:
        fit=fit_model(retained)
        fit['excluded_inconsistent_partials']=outliers
        partials=retained
    else:
        fit['excluded_inconsistent_partials']=[]
    fit['all_candidate_count']=candidate_count
    fit['initial_all_candidate_rms_error_cents']=initial_error
    fit['dominant_fundamental_peak_hz']=float(interpolate_peak(int(ids[np.argmax(p[ids])]),p,df))
    fit['dominant_fundamental_vs_ET_cents']=float(1200*np.log2(fit['dominant_fundamental_peak_hz']/reference))
    fit['fit_fundamental_vs_ET_cents']=float(1200*np.log2(fit['fundamental_hz']/reference))
    return fit,partials


def decay_fit(t,envelope,lo,hi,noise):
    mask=(t>=lo)&(t<=hi)&(envelope>max(4*noise,1e-11))
    if np.count_nonzero(mask)<30:return {'valid':False,'reason':'insufficient samples above late-file noise estimate'}
    times=t[mask];db=20*np.log10(np.maximum(envelope[mask],1e-30))
    m,b=np.polyfit(times,db,1);pred=m*times+b
    r2=1-float(np.sum((db-pred)**2))/max(float(np.sum((db-np.mean(db))**2)),1e-30)
    return {'valid':bool(m<0),'amplitude_slope_db_per_second':float(m),'sigma_per_second':float(-m*math.log(10)/20),
            'extrapolated_T60_seconds':float(-60/m) if m<0 else None,'r_squared':r2,'extrapolated_onset_amplitude_dbfs':float(b),
            'accepted_time_seconds':[float(times[0]),float(times[-1])],
            'median_snr_db':float(20*np.log10(np.median(envelope[mask])/max(noise,1e-30)))}


def partial_decay(x,fs,freq,onset,fund):
    # Heterodyne each channel, anti-alias/downsample the complex amplitude, then
    # low-pass at a bandwidth that covers the unresolved unison cluster.
    time=np.arange(len(x))/fs
    demod=x*np.exp(-2j*np.pi*freq*time)[:,None]
    down=128;env_fs=fs/down
    slow=resample_poly(demod,1,down,axis=0,window=('kaiser',10))
    bandwidth=min(.15*fund,max(4,.005*freq))
    slow=sosfiltfilt(butter(4,bandwidth,fs=env_fs,output='sos'),slow,axis=0)
    envelope=2*np.sqrt(np.mean(abs(slow)**2,axis=1))
    t=np.arange(len(envelope))/env_fs-onset
    noise=float(np.median(envelope[t>max(t[-1]-.75,.8*t[-1])]))
    return {'bandwidth_hz':bandwidth,'late_file_envelope_floor':noise,
            'early':decay_fit(t,envelope,.2,.8,noise),
            'late':decay_fit(t,envelope,1,3,noise)}


def unison_observation(x,fs,fit,onset):
    end=min(len(x)/fs-.1,onset+8)
    start=onset+.25
    f,p=spectrum(x,fs,start,end,nfft=2**21);df=f[1]-f[0]
    frequency=fit['fundamental_hz'];width=frequency*(2**(20/1200)-1)
    region=(f>frequency-width)&(f<frequency+width)
    # Resolution derives from window length, not the zero-padded FFT spacing.
    resolution=1.5/(end-start)
    peaks,_=find_peaks(p,distance=max(1,int(resolution/df)))
    ids=peaks[region[peaks]]
    if not len(ids):return {'resolved':False,'reason':'no fundamental peak'}
    maximum=float(np.max(p[ids]));ids=ids[p[ids]>maximum*10**(-18/10)]
    ids=ids[np.argsort(p[ids])[-4:][::-1]]
    observations=[{'frequency_hz':float(interpolate_peak(int(i),p,df)),
                   'relative_peak_db':float(10*np.log10(p[i]/maximum))}for i in ids]
    frequencies=sorted(row['frequency_hz']for row in observations)
    return {'resolved_multiple_components':bool(len(frequencies)>1),'hann_resolution_hz':resolution,
            'analysis_window_seconds_after_onset':[.25,end-onset],
            'peaks':observations,'candidate_beat_rates_hz':[float(b-a)for a,b in zip(frequencies,frequencies[1:])],
            'interpretation':'Multiple components can include unison strings, polarization splitting, leakage or recording artifacts. No individual-string identification is asserted.'}



def estimator_sanity_checks():
    # Opposite stereo polarity deliberately defeats arithmetic waveform mixing;
    # the estimator must retain the correct partial frequencies through power.
    results=[];fs=48000;t=np.arange(int(2.4*fs))/fs
    for midi,f1,B in [(36,65.1,.00013),(60,261.4,.00029),(84,1050.2,.0026)]:
        y=np.zeros(len(t))
        for n in range(1,9):
            f=n*f1*math.sqrt((1+B*n*n)/(1+B))
            y+=np.sin(2*np.pi*f*t+.17*n)*np.exp(-.8*t)/n**1.3
        x=np.stack([y,-y],axis=1)
        fit,_=estimate_partials(x,fs,midi,0)
        error=abs(1200*math.log2(fit['fundamental_hz']/f1))
        relativeB=abs(fit['engine_B']/B-1)
        passed=error<.05 and relativeB<.02
        if not passed:raise AssertionError((midi,error,relativeB))
        results.append({'midi_note':midi,'known_fundamental_hz':f1,'known_engine_B':B,
                        'recovered_fundamental_error_cents':error,'relative_B_error':relativeB,
                        'opposite_stereo_polarity':True,'passed':passed})
    return results


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,default=ROOT/'benchmark/independent_physics.json')
    args=parser.parse_args()
    manifest=json.loads((ROOT/'reference/manifest.json').read_text())
    selected=[r for r in manifest['samples'] if r['midi_note'] in (36,48,60,72,84) and r['layer'] in (4,12)]
    assert len(selected)==10 and all(r['id'].startswith('C')for r in selected)
    rows=[]
    for item in selected:
        fs,raw=wavfile.read(ROOT/item['wav_path']);x=raw.astype(np.float64)/(2**31);onset=item['observed_onset_seconds']
        fit,partials=estimate_partials(x,fs,item['midi_note'],onset)
        for p in partials:p['decay']=partial_decay(x,fs,p['frequency_hz'],onset,fit['fundamental_hz'])
        unison=unison_observation(x,fs,fit,onset)
        result={'id':item['id'],'midi_note':item['midi_note'],'layer':item['layer'],
                'source_wav_sha256':hashlib.sha256((ROOT/item['wav_path']).read_bytes()).hexdigest(),
                'onset_seconds':onset,'fit':fit,'partials':partials,'unison_observation':unison}
        rows.append(result)
        early=[p['decay']['early']['extrapolated_T60_seconds']for p in partials if p['decay']['early']['valid']]
        late=[p['decay']['late']['extrapolated_T60_seconds']for p in partials if p['decay']['late']['valid']]
        print(item['id'],f"f1={fit['fundamental_hz']:.5f} B={fit['engine_B']:.7g} error={fit['rms_partial_error_cents']:.2f}cent",
              f"medianT60early={np.median(early):.2f}s late={np.median(late):.2f}s",flush=True)
    anchors=[]
    for midi in [36,48,60,72,84]:
        selected_rows=[r for r in rows if r['midi_note']==midi]
        f1=float(np.median([r['fit']['fundamental_hz']for r in selected_rows]))
        entry={'midi_note':midi,'fundamental_hz_median':f1,
               'stretch_cents_vs_ET':float(1200*np.log2(f1/(440*2**((midi-69)/12)))),
               'engine_B_median':float(np.median([r['fit']['engine_B']for r in selected_rows])),
               'source_ids':[r['id']for r in selected_rows]}
        for stage in ['early','late']:
            fits=[p['decay'][stage]for r in selected_rows for p in r['partials']
                  if p['decay'][stage]['valid'] and p['decay'][stage]['r_squared']>.5]
            entry[stage+'_median_T60_seconds']=float(np.median([f['extrapolated_T60_seconds']for f in fits])) if fits else None
            entry[stage+'_median_sigma_per_second']=float(np.median([f['sigma_per_second']for f in fits])) if fits else None
            entry[stage+'_reliable_partial_fit_count']=len(fits)
        ratios=[p['decay']['late']['extrapolated_onset_amplitude_dbfs']-p['decay']['early']['extrapolated_onset_amplitude_dbfs']
                for r in selected_rows for p in r['partials']
                if p['decay']['early']['valid'] and p['decay']['late']['valid']
                and p['decay']['early']['r_squared']>.5 and p['decay']['late']['r_squared']>.5]
        entry['late_to_early_extrapolated_onset_amplitude_db_median']=float(np.median(ratios)) if ratios else None
        anchors.append(entry)
    report={'scope':'TRAIN10 ONLY: C2,C3,C4,C5,C6 × layers4,12. No holdout waveform read.',
            'pitch_anchors':anchors,'algorithm_sanity_checks':estimator_sanity_checks(),
            'method':{'frequency':'Stereo power sum; Hann window0.1..2.1s after observed onset; interpolated high-resolution FFT peaks; dominant peaks in each broad harmonic band; require>=18dB local prominence and>=-60dB global relative peak, then exclude initialfit residuals>4c ifatleast4partials remain.','model':'f_n=n f1 sqrt((1+B n²)/(1+B)); A=f1²/(1+B),C=A B. engine_B=C/A; normalized_B=C/(A+C).','decay':'Per-channel complex heterodyne,polyphase down128,zero-phase4th-order lowpass spanning unison cluster,combined channel power. OLS amplitude-dB slopes in0.2..0.8s and1..3s,excluding estimates<12dB over late-file floor. ExtrapolatedT60 is not measured decay-to-silence.','unison':'Long-window power spectrum around fundamental,peaks separated by Hann resolution; candidatebeat rates are observations,not identified physical strings.'},
            'limitations':['Microphone and soundboard radiation affect amplitude estimates.','Unison interference makes short-window decay non-exponential; inspect slopes/R² bypartial.','A stiff-string law cannot exactly explain every recorded partial,especially wound-bass and unresolved polarization components.','No absoluteSPL or physicalhammerforce inference.','Recorded pedalstate andnoteofftimeunknown.'],
            'samples':rows}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    temporary=args.out.with_suffix('.json.tmp');temporary.write_text(json.dumps(report,indent=2)+'\n');temporary.replace(args.out)

if __name__=='__main__':main()
