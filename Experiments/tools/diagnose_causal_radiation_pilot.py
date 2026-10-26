#!/usr/bin/env python3
"""Post-hoc diagnostics of the failed frozen pilot; no rescore or new synthesis.

Uses fixed pilot gains/onsets and existing captures. Fine bands, carrier-relative
levels and coherent differences diagnose the C6 failure; they cannot change the
frozen acceptance result. Optional T*.5 was preregistered as a mixture, while its
application to all acceptance gates here is explicitly post-hoc diagnostic only.
"""
from __future__ import annotations
from datetime import datetime,timezone
import hashlib,json,math
from pathlib import Path
import numpy as np
from scipy import signal
import probe_full_causal_radiation_metrics as metrics

ROOT=metrics.ROOT
WINDOWS=((.005,.020),(.020,.050),(.050,.100))
BANDS=((31.25,250.),(250.,500.),(500.,1000.),(1000.,2000.),(2000.,4000.),(4000.,8000.),(8000.,12000.),(12000.,19000.))


def db(power):return float(10*np.log10(max(float(power),1e-30)))
def transform(x):
    n=len(x);window=signal.windows.hann(n,sym=False);nfft=1<<int(math.ceil(math.log2(n*2)))
    z=np.fft.rfft(x*window[:,None],n=nfft,axis=0)
    weights=np.full(len(z),2/(nfft*np.sum(window*window)));weights[0]*=.5;weights[-1]*=.5
    return np.fft.rfftfreq(nfft,1/metrics.RATE),z,weights

def integrate(f,p,a,b):
    step=f[1]-f[0]
    weights=np.clip((np.minimum(f+step/2,b)-np.maximum(f-step/2,a))/step,0,1)
    return np.sum(p*weights)

def spectra(ref,old,new):
    f,zr,w=transform(ref);_,zo,_=transform(old);_,zn,_=transform(new)
    zd=zn-zo
    return f,{'reference':np.mean(abs(zr)**2,axis=1)*w,'baseline':np.mean(abs(zo)**2,axis=1)*w,
        'candidate':np.mean(abs(zn)**2,axis=1)*w,'difference':np.mean(abs(zd)**2,axis=1)*w,
        'old_new_cross':np.mean(zo*zn.conjugate(),axis=1)*w,
        'old_difference_cross':np.mean(zo*zd.conjugate(),axis=1)*w}

def gates_for_T(base,candidate,ident,ref_power):
    change={'first5_excess_reduction_db':max(0.,base['early'][0]['broad_signed_error_db'])-max(0.,candidate['early'][0]['broad_signed_error_db']),
        'ring5_20_excess_reduction_db':max(0.,base['early'][1]['ring_signed_error_db'])-max(0.,candidate['early'][1]['ring_signed_error_db']),
        'late_harmonic_MAE_db':candidate['late_harmonic_MAE_db']-base['late_harmonic_MAE_db'],
        'late_envelope_MAE_db':candidate['late_envelope']['MAE_db']-base['late_envelope']['MAE_db'],
        'late_RMS_db':20*math.log10(candidate['sustain_RMS']/base['sustain_RMS']),
        'early_window_MAE_db':[c['five_band_MAE_db']-b['five_band_MAE_db'] for c,b in zip(candidate['early'],base['early'])],
        'stereo_LR_db':candidate['stereo']['sustain']['LR_db']-base['stereo']['sustain']['LR_db'],
        'mono_energy_db':metrics.power_db(candidate['stereo']['sustain']['mono_power'],base['stereo']['sustain']['mono_power'],ref_power*1e-10)}
    gates={'same_physical_run_observational_mixture':True,
        'late_harmonic':change['late_harmonic_MAE_db']<=.75,'late_envelope':change['late_envelope_MAE_db']<=.75,
        'late_RMS':abs(change['late_RMS_db'])<=.5,'stereo_LR':abs(change['stereo_LR_db'])<=.5,'mono_energy':abs(change['mono_energy_db'])<=.75}
    if ident.startswith('C3'):
        gates['C3_first5']=change['first5_excess_reduction_db']>=3
        gates['C3_ring5_20']=change['ring5_20_excess_reduction_db']>=3
    else:gates['each_early_window_MAE']=max(change['early_window_MAE_db'])<=1
    return {'changes':change,'gates':gates,'passes_numerical_diagnostic_gates':all(gates.values()),
        'scope':'Post-hoc gate application to preregistered T*.5 mixture; not another production candidate or a changed frozen result.'}


def main():
    protocol,rows=metrics.locked();pilot_path=ROOT/'Validation/full-causal-radiation-pilot.json';pilot=metrics.read(pilot_path)
    refs=metrics.read(pilot['reference_control']['path']);oldcases={c['id']:c for c in refs['cases']}
    metrics.verify([pilot[k] for k in ('protocol','code_freeze','candidate_opening','reference_control','capture_manifest','producer_receipt','metric_tool')])
    metric_hash=metrics.sha(Path(metrics.__file__))
    if metric_hash!='14fc804b80f3742ee6c95cc3908c498459a77e61c90a1bdfe4b6c23c8580c1cd':raise ValueError('Frozen metric class changed')
    predefine={'frozen_at_utc':datetime.now(timezone.utc).isoformat(),'diagnostic_only':True,'pilot':metrics.record(pilot_path),
        'tool':metrics.record(__file__),'windows_seconds':WINDOWS,'fine_bands_hz':BANDS,
        'gain_alignment':'Exactly old pilot gain/onsets; no candidate retiming or trim.',
        'carrier':'Frozen reference H1,fixed center; width uses existing3/windowduration rule.',
        'tonal_prominence':'H1-band power / mean of equal-width left/right adjacent bands. Local contrast proxy, not source-separated SNR.',
        'noise_rule':'Reference pre-onset−35..−5ms if at least5ms actual support; otherwise SNR unavailable. No tail-floor inference.',
        'coherent_difference':'Candidate−baseline pressure; Enew=Eold+Edifference+2ReCross(old,difference), Hann-band units.',
        'T_half':'Mixture preregistered; applying complete gate table is post-hoc diagnostic only; original globalFAIL unchanged.'}
    folder=metrics.OUT/'posthoc-C6';folder.mkdir(exist_ok=True)
    p=folder/'protocol.json'
    if p.exists():raise ValueError('Post-hoc diagnostic already exists')
    metrics.write(p,predefine)
    results=[];T=[];closure=[];inputs=[]
    for case in pilot['cases']:
        ident=case['id'];old=oldcases[ident]
        optional=case.get('optional_T_half_control')
        if optional:T.append({'id':ident,**gates_for_T(old['baseline'],optional['metrics'],ident,old['reference']['sustain_power'])})
        if not ident.startswith('C6'):continue
        reference_path=Path(old['reference_audio']['path']);metrics.verify([old['reference_audio'],case['baseline_audio'],case['candidate_audio']])
        _,ref=metrics.fit.benchmark.load_audio(reference_path);base,_=metrics.load_float(case['baseline_audio']['path']);new,_=metrics.load_float(case['candidate_audio']['path'])
        gain=old['baseline']['fixed_gain'];ro=old['reference']['onset_frame'];bo=old['baseline']['fixed_onset_frame']
        f1=rows[ident]['f1_hz'];r=metrics.aligned(ref,ro);b=metrics.aligned(base.astype(np.float64),bo)*gain;c=metrics.aligned(new.astype(np.float64),bo)*gain
        pre_stop=ro-240;pre_start=max(0,pre_stop-1440)
        noise={'available':pre_stop-pre_start>=240,'actual_reference_onset_ms':ro/48.,
            'reason':'No≥5ms noise segment before a5ms onset safetygap in this edited recording.'}
        if noise['available']:raise ValueError('Unexpected available noise segment; inspect before using an SNR estimate')
        windows=[]
        for a,z in WINDOWS:
            rr=metrics.section(r,a,z);bb=metrics.section(b,a,z);cc=metrics.section(c,a,z)
            f,s=spectra(rr,bb,cc);width=min(.38*f1,max(3/(z-a),.004*f1))
            h1={name:float(integrate(f,power,f1-width,f1+width).real) for name,power in s.items() if name in ('reference','baseline','candidate')}
            prominence={}
            for name in h1:
                neighbors=[float(integrate(f,s[name],f1-3*width,f1-width).real),float(integrate(f,s[name],f1+width,f1+3*width).real)]
                prominence[name]=db(h1[name]/max(sum(neighbors)*.5,1e-30))
            bands=[]
            for lo,hi in BANDS:
                powers={name:integrate(f,value,lo,hi) for name,value in s.items()}
                er,eo,en,ed=(float(powers[name].real) for name in ('reference','baseline','candidate','difference'))
                cross=float(powers['old_difference_cross'].real)
                defect=abs(en-(eo+ed+2*cross));normal=max(er,eo,en,ed,1e-30)
                if defect>normal*1e-10:raise ValueError('Coherent pressure-power identity failed')
                closure.append(defect/normal)
                floor=old['reference']['sustain_power']*1e-10
                bands.append({'band_hz':[lo,hi],'reference_dBFS':db(er),'baseline_reference_equivalent_dBFS':db(eo),'candidate_reference_equivalent_dBFS':db(en),
                    'baseline_minus_reference_db':metrics.power_db(eo,er,floor),'candidate_minus_reference_db':metrics.power_db(en,er,floor),
                    'reference_relative_H1_db':db(er/max(h1['reference'],1e-30)),
                    'reference_relative_sustain_db':db(er/old['reference']['sustain_power']),
                    'reference_above_minus50dB_sustain':er/old['reference']['sustain_power']>1e-5,
                    'candidate_minus_baseline_db':metrics.power_db(en,eo,floor),'difference_reference_equivalent_dBFS':db(ed),
                    'old_new_real_correlation':float(powers['old_new_cross'].real)/max(math.sqrt(eo*en),1e-30),
                    'difference_power_over_old':ed/max(eo,1e-30),'twice_old_difference_cross_over_old':2*cross/max(eo,1e-30),
                    'coherent_identity_relative_defect':defect/normal})
            bmono=metrics.mean_square(np.mean(bb,axis=1));cmono=metrics.mean_square(np.mean(cc,axis=1))
            windows.append({'window_seconds':[a,z],'H1_center_hz':f1,'H1_half_width_hz':width,
                'H1_power_dBFS':{name:db(value) for name,value in h1.items()},'H1_adjacent_band_prominence_db':prominence,
                'broad_mono_candidate_minus_baseline_db':10*math.log10(cmono/bmono),
                'fine_bands':bands})
        results.append({'id':ident,'midi':rows[ident]['midi'],'frozen_reference_f1_hz':f1,
            'source_reference_onset_frame':ro,'source_model_fixed_onset_frame':bo,'fixed_model_gain':gain,
            'noise_SNR':noise,'true_SNR_db':None,'windows':windows})
        inputs += [old['reference_audio'],case['baseline_audio'],case['candidate_audio']]
    metrics.verify(inputs)
    report={'schema_version':1,'completed_at_utc':datetime.now(timezone.utc).isoformat(),'pilot':metrics.record(pilot_path),
        'diagnostic_protocol':metrics.record(p),'tool':metrics.record(__file__),'frozen_metric_tool':metrics.record(Path(metrics.__file__)),
        'C6_cases':results,'T_half_posthoc_diagnostic_gate_application':T,
        'coherent_pressure_power_maximum_relative_closure_error':max(closure),
        'inputs':inputs,'original_frozen_pilot_passes_all_gates':pilot['passes_all_pilot_gates'],
        'frozen_gates_rescored_or_changed':False,'default_promoted':False,'new_synthesis_fit_or_acquisition':False,
        'limits':['Absolute model levels are reference-equivalent dBFS after the pre-existing fixed gain; they are not calibrated acoustic SPL.',
            'H1 prominence is adjacent-band contrast, not measured noise SNR; edited references provide no usable separate pre-onset noise here.',
            'Fine-band estimates are leakage-weighted finite-window powers.500–1000Hz includes H1 leakage below the1050Hz carrier,especially in15ms windows.',
            'Coherent differences describe observed pressure power; mechanical state/force remains unchanged.',
            'This post-hoc diagnosis cannot turn the failed frozen pilot into a pass or assign the real low-frequency component to a particular physical source.']}
    metrics.write(folder/'report.json',report);metrics.write(ROOT/'Validation/full-causal-radiation-C6-diagnostic.json',report)
    for case in results:
        print(case['id'],'f1',case['frozen_reference_f1_hz'])
        for window in case['windows']:
            print(window['window_seconds'],'monoShift',window['broad_mono_candidate_minus_baseline_db'],
                'errorsold→new',[(row['band_hz'],round(row['baseline_minus_reference_db'],3),round(row['candidate_minus_reference_db'],3)) for row in window['fine_bands']])
    print('T*.5 numerical diagnostic gates',[(row['id'],row['passes_numerical_diagnostic_gates']) for row in T])


if __name__=='__main__':main()
