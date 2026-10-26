#!/usr/bin/env python3
"""TRAIN10-only attack-ramp diagnostic; never changes a header or live default.

An RMS rise measured from a recording is not the exponential ramp parameter
that produces that rise through a modal piano. This tool fits that parameter
through the actual onset/envelope metric and reports other transient witnesses.
It does not identify physical hammer contact or optimize a perceptual score.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

import numpy as np
from scipy import ndimage, signal

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location('keyra_attack_benchmark', ROOT/'Research/GrandPianoV2/tools/benchmark.py')
benchmark = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(benchmark)


def modal_waveform(modes, f1, dispersion, midi, sample_rate=48000, seconds=.9):
    """Analytic dry/default source at an exact training velocity anchor.

    Fast and late branches have the same initial phase, with the engine's
    authored late-branch detuning. Overall note gain is deliberately omitted:
    onset/rise and the subsequent common-RMS comparisons are gain invariant.
    """
    time = np.arange(int(math.ceil(seconds*sample_rate)))/sample_rate
    output = np.zeros_like(time)
    late_ratio = 2**((.04 if midi<32 else .23)/1200)
    for partial, (fast, late, sigma, late_sigma) in enumerate(modes,1):
        hz = f1*partial*np.sqrt((1+dispersion*partial*partial)/(1+dispersion))
        if hz>=sample_rate*.44 or hz>19000: break
        output += fast*np.exp(-sigma*time)*np.sin(2*np.pi*hz*time)
        output += late*np.exp(-late_sigma*time)*np.sin(2*np.pi*hz*late_ratio*time)
    return time,output


def ramped_waveform(time, base, parameter, sample_rate=48000):
    ramp = -np.expm1(-2.197224577*(time+1/sample_rate)/parameter)
    # The live recurrence updates the ramp before observing the current modes.
    y = signal.lfilter([1.,-1.],[1.,-np.exp(-2*np.pi*7/sample_rate)],base*ramp)
    return np.r_[np.zeros(int(.05*sample_rate)),y]


def transient_features(full, sample_rate):
    x=np.asarray(full,dtype=np.float64)
    if x.ndim==1:x=x[:,None]
    onset,_=benchmark.onset_index(x,sample_rate)
    x=x[onset:]
    power=np.mean(x*x,axis=1)
    envelope=np.sqrt(np.maximum(ndimage.uniform_filter1d(power,max(3,int(.005*sample_rate)),mode='nearest'),0))
    attack=envelope[:int(.15*sample_rate)]
    peak=float(np.max(attack));crossings=[]
    for fraction in (.1,.9):
        crossings.append(int(np.flatnonzero(attack>=fraction*peak)[0]))
    early_rms=float(np.sqrt(np.mean(power[int(.05*sample_rate):int(.75*sample_rate)])))
    bands=[]
    for length in (.02,.05):
        frequency,spectrum=benchmark.spectrum(x[:int(length*sample_rate)],sample_rate)
        bands.append([benchmark.integrated_power(frequency,spectrum,lo,hi) for lo,hi in zip((31.25,250,1000,4000,12000),(250,1000,4000,12000,22000))])
    return {'rise_seconds':(crossings[1]-crossings[0])/sample_rate,
            't10_seconds':crossings[0]/sample_rate,'t90_seconds':crossings[1]/sample_rate,
            'onset_seconds':onset/sample_rate,'peak_time_seconds':int(np.argmax(attack))/sample_rate,
            'early_rms':early_rms,
            'early_energy':[float(np.mean(power[:int(length*sample_rate)])) for length in (.02,.05)],
            'early_bands':bands,
            'envelope_150ms':envelope[:int(.15*sample_rate)].tolist()}


def rise_metric(time,base,parameter,sample_rate=48000):
    # Restrict work to the onset and first150ms; peak-normalized rise needs no
    # later spectral/decay extraction or recording samples during the search.
    full=ramped_waveform(time,base,parameter,sample_rate)
    onset,_=benchmark.onset_index(full[:,None],sample_rate)
    power=full[onset:]*full[onset:]
    envelope=np.sqrt(np.maximum(ndimage.uniform_filter1d(power,max(3,int(.005*sample_rate)),mode='nearest'),0))[:int(.15*sample_rate)]
    peak=float(np.max(envelope));a=np.flatnonzero(envelope>=.1*peak)[0];b=np.flatnonzero(envelope>=.9*peak)[0]
    return float((b-a)/sample_rate)


def fit_parameter(time,base,target,initial,sample_rate=48000,maximum=.2):
    grid=np.unique(np.r_[np.geomspace(.001,maximum,201),initial])
    values=np.array([rise_metric(time,base,p,sample_rate) for p in grid])
    def select(parameters,rises):
        errors=np.abs(rises-target)
        # Prefer the least departure from the old ramp when the sampled metric
        # has an equivalent plateau; do not introduce gratuitous slow ramps.
        order=np.lexsort((np.abs(np.log(parameters/initial)),errors))
        return int(order[0])
    best=select(grid,values)
    lo,hi=grid[max(0,best-1)],grid[min(len(grid)-1,best+1)]
    refinement=np.linspace(lo,hi,121)
    refined=np.array([rise_metric(time,base,p,sample_rate) for p in refinement])
    parameters=np.r_[grid,refinement];rises=np.r_[values,refined]
    best=select(parameters,rises)
    return float(parameters[best]),{'target_rise_seconds':target,'predicted_rise_seconds':float(rises[best]),
            'absolute_error_seconds':float(abs(rises[best]-target)),
            'search_bounds_seconds':[.001,maximum],
            'requires_above_live_90ms_limit':bool(parameters[best]>.09),
            'at_search_bound':bool(parameters[best]<=.0010001 or parameters[best]>=maximum*.9999)}


def compare_transient(reference,model):
    gain=reference['early_rms']/max(model['early_rms'],1e-20)
    result={'rise_error_ms':1000*abs(model['rise_seconds']-reference['rise_seconds']),
            'first20ms_energy_error_db':10*np.log10(max(model['early_energy'][0]*gain*gain,1e-30)/max(reference['early_energy'][0],1e-30)),
            'first50ms_energy_error_db':10*np.log10(max(model['early_energy'][1]*gain*gain,1e-30)/max(reference['early_energy'][1],1e-30)),
            'peak_time_error_ms':1000*(model['peak_time_seconds']-reference['peak_time_seconds'])}
    for index,name in enumerate(('first20ms_band_mae_db','first50ms_band_mae_db')):
        r=np.array(reference['early_bands'][index])/reference['early_rms']**2
        m=np.array(model['early_bands'][index])/model['early_rms']**2
        mask=r>1e-5
        result[name]=float(np.mean(np.abs(10*np.log10(np.maximum(r[mask],1e-8))-10*np.log10(np.maximum(m[mask],1e-8)))))
    r=np.array(reference['envelope_150ms'])/reference['early_rms'];m=np.array(model['envelope_150ms'])/model['early_rms']
    n=min(len(r),len(m));mask=r[:n]>.01
    result['first150ms_envelope_mae_db']=float(np.mean(np.abs(20*np.log10(np.maximum(r[:n][mask],1e-5))-20*np.log10(np.maximum(m[:n][mask],1e-5)))))
    return {k:float(v) for k,v in result.items()}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--calibration',type=Path,default=ROOT/'Validation/live-calibration.json')
    p.add_argument('--features',type=Path,default=ROOT/'Research/GrandPianoV2/benchmark/reference_features.json')
    p.add_argument('--recordings',type=Path,default=ROOT/'Research/GrandPianoV2/reference/wav')
    p.add_argument('--native-baseline',type=Path,default=ROOT/'out/grand')
    p.add_argument('--output',type=Path,default=Path('/tmp/keyra-attack-proposal.json'))
    p.add_argument('--maximum',type=float,default=.2)
    a=p.parse_args()
    if not (.09<=a.maximum<=.3):p.error('--maximum must be between .09 and .3 seconds')
    all_features=json.loads(a.features.read_text())['samples']
    training=[s for s in all_features if s['split']=='train']
    expected={f'C{o}v{v}' for o in range(2,7) for v in (4,12)}
    if {s['id'] for s in training}!=expected:raise ValueError('TRAIN10 split changed')
    calibration=json.loads(a.calibration.read_text())
    if not expected.issubset(calibration['training_ids']):raise ValueError('Calibration omits required C training anchors')
    cases=[]
    for reference in training:
        same=[s for s in training if s['midi']==reference['midi'] and s.get('B_identifiable',True)]
        f1=float(np.exp(np.mean([np.log(s['f1_hz']) for s in same])))
        dispersion=float(np.exp(np.mean([np.log(s['B']) for s in same])))
        source=calibration['fits'][reference['id']]
        time,base=modal_waveform(source['modes'],f1,dispersion,reference['midi'])
        parameter,diagnostic=fit_parameter(time,base,reference['attack']['rise10_90_seconds'],source['attack'],maximum=a.maximum)
        sample_rate,recorded=benchmark.load_audio(a.recordings/(reference['id']+'.wav'))
        real=transient_features(recorded,sample_rate)
        before=transient_features(ramped_waveform(time,base,source['attack']),48000)
        after=transient_features(ramped_waveform(time,base,parameter),48000)
        native_path=a.native_baseline/(reference['id']+'.wav')
        native=None
        if native_path.exists():
            rate,x=benchmark.load_audio(native_path);native=transient_features(x,rate)
        row={'id':reference['id'],'midi':reference['midi'],'velocity':reference['midi_velocity'],
             'old_parameter_seconds':source['attack'],'candidate_parameter_seconds':parameter,
             'fit':diagnostic,'reference':{k:v for k,v in real.items() if k not in ('early_bands','envelope_150ms')},
             'analytic_baseline':compare_transient(real,before),'analytic_candidate':compare_transient(real,after),
             'analytic_vs_native_baseline_rise_error_ms':1000*abs(before['rise_seconds']-native['rise_seconds']) if native else None}
        cases.append(row)
        print(reference['id'],f"old={source['attack']*1000:.2f}ms candidate={parameter*1000:.2f}ms rise={after['rise_seconds']*1000:.2f}/{reference['attack']['rise10_90_seconds']*1000:.2f}ms",flush=True)
    report={'schema_version':1,'training_ids':sorted(expected),'all_calibration_training_ids':calibration['training_ids'],'cases':cases,
            'calibration_sha256':hashlib.sha256(a.calibration.read_bytes()).hexdigest(),
            'feature_sha256':hashlib.sha256(a.features.read_bytes()).hexdigest(),
            'method':'Analytic modal source plus live exponential ramp and7Hz DC rejection; same onset and5ms RMS/first150ms10-90 metric. Scalar rise fit only; transient witnesses are held apart from optimization.',
            'limits':'Candidate only, no default change. RMS rise is not hammer contact duration. First20/50ms energy and spectral errors can reveal smearing concealed by a scalar rise fit. Native float recurrence verification required after any candidate header is generated.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(a.output)


if __name__=='__main__':main()
