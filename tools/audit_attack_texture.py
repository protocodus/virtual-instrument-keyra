#!/usr/bin/env python3
"""TRAIN26-only default-grand attack/struck-texture diagnostics, without fitting.

Keeps the shared onset and one .05-.75s gain; adds short-time spectrum, crest,
harmonic/residual and observed phase diagnostics. Very short windows cannot
resolve bass partials or classify their apparent low-frequency content.
"""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

import numpy as np
from scipy import signal

ROOT=Path(__file__).resolve().parents[1]
FEATURES=ROOT/'References/GrandExpanded/train_features.json'
SPLIT=ROOT/'References/GrandExpanded/split.json'
WINDOWS=[(0.,.005),(.005,.020),(.020,.050),(.050,.100)]
BANDS=[(0.,31.25),(31.25,250.),(250.,1000.),(1000.,4000.),(4000.,12000.),(12000.,19000.)]


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def load_benchmark():
    path=ROOT/'Research/GrandPianoV2/tools/benchmark.py'
    spec=importlib.util.spec_from_file_location('keyra_attack_texture_benchmark',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def band_weights(frequency,lo,hi):
    df=frequency[1]-frequency[0]
    return np.clip((np.minimum(frequency+df/2,hi)-np.maximum(frequency-df/2,lo))/df,0.,1.)


def harmonic_centers(reference,sample_rate):
    if not reference.get('B_identifiable',True): return []
    ns=np.arange(1,321,dtype=float)
    hz=reference['f1_hz']*ns*np.sqrt((1+reference['B']*ns*ns)/(1+reference['B']))
    return hz[hz<min(19000.,sample_rate*.44)]


def spectrum_metrics(benchmark,section,sr,reference):
    frequency,power=benchmark.spectrum(section,sr)
    total=float(np.sum(power));duration=len(section)/sr
    band_power=[benchmark.integrated_power(frequency,power,lo,min(hi,sr*.5)) for lo,hi in BANDS]
    centroid_mask=(frequency>=250)&(frequency<=min(19000.,sr*.44))
    selected=power[centroid_mask]
    centroid=float(np.dot(frequency[centroid_mask],selected)/max(np.sum(selected),1e-30))
    floor=max(float(np.max(selected))*1e-12,1e-30)
    flatness=float(np.exp(np.mean(np.log(np.maximum(selected,floor))))/max(np.mean(selected),floor))
    harmonic=None
    if reference.get('B_identifiable',True):
        weight=np.zeros_like(frequency)
        groups={name:np.zeros_like(frequency) for name in ('calibrated_orders','unmeasured_orders_to64','orders_above64')}
        counts={name:0 for name in groups}
        for order,center in enumerate(harmonic_centers(reference,sr),1):
            width=min(.38*reference['f1_hz'],max(3/duration,.004*center))
            partial_weight=band_weights(frequency,center-width,center+width)
            weight=np.maximum(weight,partial_weight)
            name=('calibrated_orders' if order<=len(reference['partials']) else
                  'unmeasured_orders_to64' if order<=64 else 'orders_above64')
            groups[name]=np.maximum(groups[name],partial_weight);counts[name]+=1
        measured=float(np.dot(weight,power))
        harmonic={'power':measured,'fraction':measured/max(total,1e-30),
                  'residual_power':max(0.,total-measured),'residual_fraction':max(0.,1-measured/max(total,1e-30)),
                  'harmonic_fraction_by_band':[float(np.dot(weight*band_weights(frequency,lo,min(hi,sr*.5)),power))/max(band,1e-30)
                                               for (lo,hi),band in zip(BANDS,band_power)],
                  'order_group_power_by_band':{name:[float(np.dot(group*band_weights(frequency,lo,min(hi,sr*.5)),power))
                                                     for lo,hi in BANDS] for name,group in groups.items()},
                  'order_group_counts':counts,
                  'partial_bands_resolved':3/duration<=.38*reference['f1_hz'],
                  'fundamental_periods_in_window':duration*reference['f1_hz'],
                  'note':'Residual includes finite-window leakage, detuned unisons, noise, other body/string components and partial-model errors; it is not uniquely hammer noise.'}
    return {'hertz_resolution':1/duration,'hann_total_power':total,'band_power':band_power,
            'centroid_250_19000_hz':centroid,'flatness_250_19000':flatness,
            'harmonic':harmonic,
            'low_frequency_interpretation_resolved':duration>=.1}


def waveform_metrics(section,reference_early_rms):
    power=float(np.mean(section*section));peak=float(np.max(np.abs(section)))
    channel_rms=np.sqrt(np.mean(section*section,axis=0))
    channel_peak=np.max(np.abs(section),axis=0)
    return {'rectangular_power':power,'peak':peak,
            'crest_db':20*math.log10(max(peak,1e-30)/max(math.sqrt(power),1e-30)),
            'mean_channel_crest_db':float(np.mean(20*np.log10(np.maximum(channel_peak,1e-30)/np.maximum(channel_rms,1e-30)))),
            'peak_over_steady_rms_db':20*math.log10(max(peak,1e-30)/max(reference_early_rms,1e-30)),
            'power_over_steady_rms_db':10*math.log10(max(power,1e-30)/max(reference_early_rms**2,1e-30))}


def observed_phase(section,sr,reference):
    # Direct demodulation at known frequencies avoids an FFT-bin phase offset.
    # Use reference prominence/weights for both signals. This describes an
    # observed composite, not a unique mechanical or microphone phase model.
    chosen=[part for part in reference['partials'] if part['relative_db'][0]>-35 and part['frequency_hz']<sr*.44]
    if not chosen: return None
    frequencies=np.array([part['frequency_hz'] for part in chosen])
    weights=np.sqrt(np.array([part['powers'][0] for part in chosen]))
    times=np.arange(len(section))/sr
    window=signal.windows.hann(len(section),sym=False)
    demodulator=np.exp(-2j*np.pi*frequencies[:,None]*times[None,:])
    coefficients=demodulator@(section*window[:,None])
    delays=np.linspace(-.005,.005,1001)
    corrected=np.exp(2j*np.pi*frequencies[:,None]*delays[None,:])
    channels=[]
    for channel in range(section.shape[1]):
        phase=np.angle(coefficients[:,channel])
        phasor=weights*np.exp(1j*phase)
        concentration=np.abs(phasor@corrected)/max(float(np.sum(weights)),1e-30)
        at=int(np.argmax(concentration))
        channels.append({'phase_concentration_at_onset':float(abs(np.sum(phasor))/max(np.sum(weights),1e-30)),
                         'phase_concentration_after_common_delay':float(concentration[at]),
                         'common_delay_ms':float(1000*delays[at]),
                         'phase_radians':phase.tolist()})
    return {'partial_count':len(chosen),'limited_by_fewer_than_four_partials':len(chosen)<4,
            'partial_orders':[part['n'] for part in chosen],
            'channels':channels,
            'note':'Amplitude-weighted circular concentration of composite partial phases; common delay search only removes an onset/propagation offset. Radiation phase, unisons and nonstationarity remain confounds.'}


def statistics(values):
    values=np.asarray([v for v in values if v is not None and np.isfinite(v)],dtype=float)
    return {'count':int(len(values)),'mean':float(np.mean(values)),'median':float(np.median(values)),
            'p10':float(np.quantile(values,.1)),'p90':float(np.quantile(values,.9))} if len(values) else None


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--renders',type=Path,default=ROOT/'out/expanded-grand-candidate/training/expanded')
    parser.add_argument('--output',type=Path,default=ROOT/'Validation/attack-texture-audit.json')
    args=parser.parse_args()
    benchmark=load_benchmark()
    split=json.loads(SPLIT.read_text());data=json.loads(FEATURES.read_text())
    expected=set(split['training_ids']);rows=data['samples']
    if len(expected)!=26 or {row['id'] for row in rows}!=expected or not all(row['split']=='train' for row in rows):
        raise ValueError('Locked TRAIN26 mismatch')
    if any(name.startswith('A3v') for name in expected): raise ValueError('Reserved A3 must not enter training diagnostics')
    cases=[]
    for reference in sorted(rows,key=lambda row:(row['midi'],row['layer'])):
        name=reference['id']
        original=ROOT/'References/GrandExpanded/recordings'/f'{name}.wav'
        if not original.exists():original=ROOT/'Research/GrandPianoV2/reference/wav'/f'{name}.wav'
        rendered=args.renders/f'{name}.wav'
        sr,full=benchmark.load_audio(original);msr,mfull=benchmark.load_audio(rendered)
        if sr!=msr or sr!=48000:raise ValueError('Audit requires native matching 48kHz recordings/renders')
        onset,_=benchmark.onset_index(full,sr);monset,_=benchmark.onset_index(mfull,sr)
        actual=full[onset:];model=mfull[monset:]
        model_rms=float(np.sqrt(np.mean(model[int(.05*sr):int(.75*sr)]**2)))
        gain=reference['early_rms']/max(model_rms,1e-30)
        model=model*gain
        case={'id':name,'split':'train','midi':reference['midi'],'layer':reference['layer'],
              'reference_sha256':sha(original),'render_sha256':sha(rendered),
              'reference_onset_seconds':onset/sr,'render_onset_seconds':monset/sr,
              'fixed_model_gain_db':20*math.log10(gain),'windows':[],'aggregate_windows':[]}
        for lo,hi in WINDOWS+[(0.,.1),(0.,.25)]:
            a=actual[int(lo*sr):int(hi*sr)];z=model[int(lo*sr):int(hi*sr)]
            ref={**spectrum_metrics(benchmark,a,sr,reference),**waveform_metrics(a,reference['early_rms'])}
            mod={**spectrum_metrics(benchmark,z,sr,reference),**waveform_metrics(z,reference['early_rms'])}
            errors=[]
            for r,m in zip(ref['band_power'],mod['band_power']):
                errors.append(10*math.log10(max(m,1e-30)/max(r,1e-30)) if r/reference['early_rms']**2>1e-6 else None)
            window={'seconds_after_onset':[lo,hi],'reference':ref,'model':mod,
                    'model_minus_reference':{'rectangular_power_db':10*math.log10(max(mod['rectangular_power'],1e-30)/max(ref['rectangular_power'],1e-30)),
                                            'band_power_db':errors,
                                            'centroid_hz':mod['centroid_250_19000_hz']-ref['centroid_250_19000_hz'],
                                            'flatness_db':10*math.log10(max(mod['flatness_250_19000'],1e-30)/max(ref['flatness_250_19000'],1e-30)),
                                            'crest_db':mod['mean_channel_crest_db']-ref['mean_channel_crest_db']}}
            if lo==0 and hi in (.1,.25):
                window['reference_observed_phase']=observed_phase(a,sr,reference)
                window['model_observed_phase']=observed_phase(z,sr,reference)
                case['aggregate_windows'].append(window)
            else:case['windows'].append(window)
        cases.append(case)
        early=case['windows'][0]['model_minus_reference']
        aggregate=case['aggregate_windows'][0]
        print(f"{name}: 0–5ms power delta {early['rectangular_power_db']:+.2f}dB, 0–100ms centroid delta {aggregate['model_minus_reference']['centroid_hz']:+.0f}Hz, crest delta {aggregate['model_minus_reference']['crest_db']:+.2f}dB",flush=True)
    summary=[]
    for index,(lo,hi) in enumerate(WINDOWS):
        summary.append({'seconds_after_onset':[lo,hi],
                        'model_minus_reference_power_db':statistics([case['windows'][index]['model_minus_reference']['rectangular_power_db'] for case in cases]),
                        'model_minus_reference_band_power_db':[statistics([case['windows'][index]['model_minus_reference']['band_power_db'][band] for case in cases]) for band in range(len(BANDS))],
                        'centroid_delta_hz':statistics([case['windows'][index]['model_minus_reference']['centroid_hz'] for case in cases]),
                        'flatness_delta_db':statistics([case['windows'][index]['model_minus_reference']['flatness_db'] for case in cases]),
                        'crest_delta_db':statistics([case['windows'][index]['model_minus_reference']['crest_db'] for case in cases])})
    aggregate_summary=[]
    for index,seconds in enumerate((.1,.25)):
        windows=[case['aggregate_windows'][index] for case in cases]
        resolved=[window for window in windows if window['reference']['harmonic'] and window['reference']['harmonic']['partial_bands_resolved']]
        prominent_upper=[window for window,case in zip(windows,cases)
                         if window['reference']['harmonic'] and window['reference']['harmonic']['partial_bands_resolved']
                         and window['reference']['band_power'][4]/next(row['early_rms']**2 for row in rows if row['id']==case['id'])>1e-5]
        aggregate_summary.append({'seconds_after_onset':[0,seconds],
                                  'reference_resolved_harmonic_fraction':statistics([window['reference']['harmonic']['fraction'] for window in resolved]),
                                  'model_resolved_harmonic_fraction':statistics([window['model']['harmonic']['fraction'] for window in resolved]),
                                  'reference_prominent_4_12khz_harmonic_fraction':statistics([window['reference']['harmonic']['harmonic_fraction_by_band'][4] for window in prominent_upper]),
                                  'model_prominent_4_12khz_harmonic_fraction':statistics([window['model']['harmonic']['harmonic_fraction_by_band'][4] for window in prominent_upper]),
                                  'reference_phase_concentration_after_common_delay':statistics([channel['phase_concentration_after_common_delay'] for window in windows
                                       if window['reference_observed_phase'] and not window['reference_observed_phase']['limited_by_fewer_than_four_partials'] for channel in window['reference_observed_phase']['channels']]),
                                  'model_phase_concentration_after_common_delay':statistics([channel['phase_concentration_after_common_delay'] for window in windows
                                       if window['model_observed_phase'] and not window['model_observed_phase']['limited_by_fewer_than_four_partials'] for channel in window['model_observed_phase']['channels']])})
    report={'schema_version':1,'training_ids':sorted(expected),'heldout_cases_used':False,
            'source_features_sha256':sha(FEATURES),'locked_split_sha256':sha(SPLIT),
            'analysis_source_sha256':sha(Path(__file__)),'engine_sha256':sha(ROOT/'src/Piano.cpp'),
            'calibration_sha256':sha(ROOT/'src/LiveCalibration.h'),
            'render_directory':str(args.renders.relative_to(ROOT)) if args.renders.is_relative_to(ROOT) else str(args.renders),
            'band_edges_hz':BANDS,'configuration':'Frozen expanded default-grand training renders: close AB, default tone/dynamics/width, no authored room/resonance/mechanical noise.',
            'method':'Preserved onset detector, one .05–.75s RMS gain held fixed. Hann stereo-power spectra for short windows; full stiff-string harmonic sequence to19kHz for residual masks, split into calibration-covered orders, unmeasured orders<=64 and orders above the engine cap; separate direct complex demodulation phase concentration over100/250ms.',
            'summary':summary,'aggregate_summary':aggregate_summary,'cases':cases,
            'recommended_next_mechanism':'Evaluate causal nonlinear hammer/contact drive and complex loaded-board radiation phase, preserving the original physical solver mechanisms. A shared scalar onset ramp and all-positive modal starts do not reproduce the observed attack spectrum/phase structure. Do not fill residual bands with arbitrary white noise. Keep steady-state calibration fixed for an isolated physical attack/radiation comparison.',
            'limits':'Training diagnostics, no fit or default change.5/15/30/50ms spectra have limited resolution; unresolved harmonic fractions cannot identify broadband hammer noise. The first5ms can include detector/recording lead-in uncertainty. Low-frequency content in very short windows is not uniquely recording noise. Higher-order stiff-string locations extrapolate measured f1/B and are not independently identified peaks. Residual power also contains window leakage, unisons and imperfect pitch/dispersion estimates. Observed phase concentration does not uniquely recover hammer/microphone phase. No A3 or velocity-reserved recording is read.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')


if __name__=='__main__':main()
