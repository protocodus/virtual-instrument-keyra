#!/usr/bin/env python3
"""Frozen six-TRAIN causal-observer pilot metrics; no fitting or retiming.

The protocol predates this implementation. Before any candidate file is opened,
this tool pins its own implementation and the completed reference/control score.
A candidate uses the baseline onset and baseline-derived sustain gain unchanged.
"""
from __future__ import annotations
import argparse
from datetime import datetime,timezone
import hashlib
import json
import math
from pathlib import Path
import sys

import numpy as np
from scipy import ndimage
from scipy.io import wavfile

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import fit_full_calibration as fit

OUT=ROOT/'out/full-causal-radiation-metrics/v1'
PROTOCOL_SHA='5ec7ace5cffb6655fb017430d328dc784762beb9ff5460eb5c63a07e606b96fa'
IDS=('C3v4','C3v12','C4v4','C4v12','C6v4','C6v12')
EARLY=((0.,.005),(.005,.020),(.020,.050),(.050,.100))
BANDS=((31.25,250.),(250.,1000.),(1000.,4000.),(4000.,12000.),(12000.,19000.))
LATE=((.25,.75),(.75,1.5),(1.5,2.5),(2.5,3.5))
RATE=48000


def now():return datetime.now(timezone.utc).isoformat()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def read_snapshot(path):
    path=Path(path).resolve();data=path.read_bytes()
    return json.loads(data),{'path':str(path),'sha256':hashlib.sha256(data).hexdigest()}
def record(path):return {'path':str(Path(path).resolve()),'sha256':sha(path)}
def write(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def verify(records):
    for row in records:
        if sha(row['path'])!=row['sha256']:raise ValueError('Frozen input changed:'+row['path'])
def locked():
    path=OUT/'protocol.json'
    if sha(path)!=PROTOCOL_SHA or sha(ROOT/'Validation/full-causal-radiation-pilot-protocol.json')!=PROTOCOL_SHA:
        raise ValueError('Frozen protocol changed')
    protocol=read(path);verify(protocol['inputs'])
    if tuple(row['id'] for row in protocol['cases'])!=IDS:raise ValueError('TRAIN pilot inventory changed')
    rows,_=fit.training_inputs(fit.DEFAULT_REFERENCE,fit.DEFAULT_SPLIT)
    refs={row['id']:row for row in rows}
    if not set(IDS)<=set(refs):raise ValueError('A non-TRAIN case entered the pilot')
    return protocol,refs

def load_float(path):
    sr,x=wavfile.read(path)
    if sr!=RATE or x.dtype.kind!='f' or x.dtype.itemsize!=4 or x.ndim!=2 or x.shape[1]!=2:
        raise ValueError('Expected float32 stereo48k capture:'+str(path))
    if len(x)!=182400 or not np.isfinite(x).all():raise ValueError('Invalid pilot capture length/finiteness')
    return x,np.asarray(x,dtype='<f4').tobytes()

def aligned(x,onset):
    value=x[onset:]
    if len(value)<round(3.5*RATE)+1:raise ValueError('Insufficient actual3.5s post-onset support; no padding allowed')
    return value

def section(x,a,b):
    value=x[round(a*RATE):round(b*RATE)]
    if len(value)!=round((b-a)*RATE):raise ValueError('Window outside actual support')
    return value

def mean_square(x):return float(np.mean(np.asarray(x,dtype=np.float64)**2))
def power_db(value,reference,floor):return float(10*np.log10(max(value,floor)/max(reference,floor)))
def band_powers(x,bands):
    f,p=fit.benchmark.spectrum(x,RATE)
    return [fit.benchmark.integrated_power(f,p,a,b) for a,b in bands]

def onset_detail(x,model_event_frame=4800):
    onset,detail=fit.benchmark.onset_index(x,RATE)
    return {'frame':onset,'seconds':onset/RATE,'known_model_event_frame':model_event_frame,
        'ms_after_actual_model_event':None if model_event_frame is None else (onset-model_event_frame)/48.,'detector':detail}

def observation_features(x,onset,gain,reference_features,reference_row):
    value=aligned(np.asarray(x,dtype=np.float64),onset)*gain
    ref_power=reference_features['sustain_power']
    floor=ref_power*1e-10
    early=[]
    for index,(a,b) in enumerate(EARLY):
        chunk=section(value,a,b);powers=band_powers(chunk,BANDS)
        ref=reference_features['early'][index]
        errors=[power_db(p,q,floor) for p,q in zip(powers,ref['band_power'])]
        f,p=fit.benchmark.spectrum(chunk,RATE);mask=(f>=250)&(f<19000)
        centroid=float(f[mask]@p[mask]/max(float(np.sum(p[mask])),1e-30))
        broad=mean_square(chunk)
        extra=band_powers(chunk,((740.,810.),(4000.,8000.)))
        early.append({'window_seconds':[a,b],'broad_power':broad,'broad_signed_error_db':power_db(broad,ref['broad_power'],floor),
            'band_power':powers,'band_signed_errors_db':errors,'five_band_MAE_db':float(np.mean(np.abs(errors))),
            'ring_740_810_power':extra[0],'ring_signed_error_db':power_db(extra[0],ref['ring_740_810_power'],floor),
            'bright_4000_8000_power':extra[1],'bright_signed_error_db':power_db(extra[1],ref['bright_4000_8000_power'],floor),
            'centroid_250_19000_hz':centroid})
    partial_errors=[];partials=[]
    for index,(a,b) in enumerate(LATE):
        chunk=section(value,a,b)
        centers=reference_features['late_harmonics'][index]['partials']
        f,p=fit.benchmark.spectrum(chunk,RATE);observed=[]
        for center in centers:
            width=min(.38*reference_row['f1_hz'],max(3/(b-a),.004*center['frequency_hz']))
            power=fit.benchmark.integrated_power(f,p,center['frequency_hz']-width,center['frequency_hz']+width)
            error=power_db(power,center['power'],floor)
            observed.append({'n':center['n'],'frequency_hz':center['frequency_hz'],'power':power,
                'reference_power':center['power'],'included':center['included'],'signed_error_db':error})
            if center['included']:partial_errors.append(abs(error))
        partials.append({'window_seconds':[a,b],'partials':observed})
    env=np.sqrt(np.maximum(ndimage.uniform_filter1d(np.mean(value*value,axis=1),240,mode='nearest'),0))
    times=np.asarray(reference_features['late_envelope']['times_seconds'])
    env_values=np.interp(times*RATE,np.arange(len(env)),env)
    ref_values=np.asarray(reference_features['late_envelope']['rms'])
    mask=np.asarray(reference_features['late_envelope']['included'],dtype=bool)
    amplitude_floor=math.sqrt(ref_power)*1e-5
    envelope_errors=20*np.log10(np.maximum(env_values,amplitude_floor)/np.maximum(ref_values,amplitude_floor))
    if not partial_errors or not np.any(mask):raise ValueError('Missing fixed reference late metric support')
    sustain=section(value,.25,.75)
    stereo={}
    for name,(a,b) in [('sustain',(.25,.75)),('whole_note',(0.,3.5)),*[(f'early_{i}',window) for i,window in enumerate(EARLY)]]:
        chunk=section(value,a,b);left=mean_square(chunk[:,0]);right=mean_square(chunk[:,1]);mono=mean_square(np.mean(chunk,axis=1))
        stereo[name]={'window_seconds':[a,b],'left_power':left,'right_power':right,'mono_power':mono,
            'LR_db':power_db(left,right,floor)}
    return {'fixed_onset_frame':onset,'fixed_gain':gain,'detected_onset_diagnostic':onset_detail(x),
        'early':early,'late_harmonics':partials,'late_harmonic_MAE_db':float(np.mean(partial_errors)),
        'late_envelope':{'times_seconds':times.tolist(),'rms':env_values.tolist(),'reference_rms':ref_values.tolist(),
            'included':mask.tolist(),'signed_errors_db':envelope_errors.tolist(),'MAE_db':float(np.mean(abs(envelope_errors[mask])))},
        'sustain_RMS':math.sqrt(mean_square(sustain)),'stereo':stereo}

def reference_features(x,onset,row):
    value=aligned(np.asarray(x,dtype=np.float64),onset)
    sustain=mean_square(section(value,.25,.75));early=[];harmonics=[]
    for a,b in EARLY:
        chunk=section(value,a,b);powers=band_powers(chunk,BANDS);extra=band_powers(chunk,((740.,810.),(4000.,8000.)))
        early.append({'window_seconds':[a,b],'broad_power':mean_square(chunk),'band_power':powers,
            'ring_740_810_power':extra[0],'bright_4000_8000_power':extra[1]})
    for a,b in LATE:
        f,p=fit.benchmark.spectrum(section(value,a,b),RATE);partials=[]
        for part in row['partials']:
            center=part['frequency_hz']
            if center>=17000:continue
            width=min(.38*row['f1_hz'],max(3/(b-a),.004*center))
            power=fit.benchmark.integrated_power(f,p,center-width,center+width)
            partials.append({'n':part['n'],'frequency_hz':center,'power':power,'included':power/sustain>1e-5})
        harmonics.append({'window_seconds':[a,b],'partials':partials})
    env=np.sqrt(np.maximum(ndimage.uniform_filter1d(np.mean(value*value,axis=1),240,mode='nearest'),0))
    times=np.arange(.26,3.5001,.02);samples=np.interp(times*RATE,np.arange(len(env)),env)
    mask=samples/math.sqrt(sustain)>10**(-50/20)
    return {'onset_frame':onset,'onset_diagnostic':onset_detail(x,None),'sustain_power':sustain,'early':early,
        'late_harmonics':harmonics,'late_envelope':{'times_seconds':times.tolist(),'rms':samples.tolist(),'included':mask.tolist()}}


def references():
    protocol,rows=locked();target=OUT/'reference-control.json'
    if target.exists():raise ValueError('Reference/control study already complete; use verify')
    results=[]
    for case in protocol['cases']:
        ident=case['id'];refpath=Path(case['reference_audio']['path']);basepath=Path(case['cached_control_audio']['path'])
        verify([case['reference_audio'],case['cached_control_audio']])
        sr,ref=fit.benchmark.load_audio(refpath);raw,_=load_float(basepath);base=raw.astype(np.float64)
        if sr!=RATE:raise ValueError('Reference sample rate changed')
        ro,_=fit.benchmark.onset_index(ref,RATE);bo,_=fit.benchmark.onset_index(base,RATE)
        if ro!=round(rows[ident]['onset_seconds']*RATE):raise ValueError('Reference onset disagrees with frozen TRAIN measurement')
        rf=reference_features(ref,ro,rows[ident])
        gain=math.sqrt(rf['sustain_power']/mean_square(section(aligned(base,bo),.25,.75)))
        baseline=observation_features(base,bo,gain,rf,rows[ident])
        results.append({'id':ident,'reference_audio':case['reference_audio'],'baseline_audio':case['cached_control_audio'],
            'reference':rf,'baseline':baseline,'gain_db':20*math.log10(gain)})
        print(ident+' reference/control analysed',flush=True)
    locked();write(target,{'completed_at_utc':now(),'protocol':record(OUT/'protocol.json'),'tool':record(__file__),
        'candidate_audio_opened':False,'cases':results,'fit_or_acquisition':False})
    for row in results:
        if row['id'].startswith('C3'):
            first=row['baseline']['early'][0]['broad_signed_error_db'];ring=row['baseline']['early'][1]['ring_signed_error_db']
            print(row['id'],'gain',10**(row['gain_db']/20),'first5 signed dB',first,'ring5–20 signed dB',ring,flush=True)


def producer_evidence(producer,protocol,capture):
    """Cross-check the bound producer, never infer physical parity from audio."""
    if producer.get('protocol',{}).get('sha256')!=PROTOCOL_SHA:
        raise ValueError('Producer receipt does not bind the frozen protocol')
    verify([producer['protocol']])
    records=list(producer.get('source_inputs',[]))
    if not records:raise ValueError('Producer source identities missing')
    verify(records)
    hashes={row['sha256'] for row in records}
    for key in ('calibration_sha256','prepared_model_sha256','frozen_facade_sha256'):
        if protocol['producer_contract'][key] not in hashes:
            raise ValueError('Producer omitted exact frozen source/profile identity:'+key)
    expected={'sample_rate':48000,'frames':182400,'note_on_frame':4800,'pedal_initial':0,
        'humanization':0,'mechanical_level':0,'repetition_controller':False,'gain_db':0,'stereo_width':1}
    actual=producer.get('configuration',{})
    for key,value in expected.items():
        if key not in actual or actual[key]!=value:
            raise ValueError('Producer control differs from frozen protocol:'+key)
    if actual['repetition_controller'] is not False:
        raise ValueError('Producer repetition bypass must be explicit')
    freeze_record=producer['candidate_freeze'];verify([freeze_record])
    frozen,frozen_identity=read_snapshot(freeze_record['path'])
    if frozen_identity['sha256']!=freeze_record['sha256']:
        raise ValueError('Prototype freeze changed during read')
    if frozen.get('protocol',{}).get('sha256')!=PROTOCOL_SHA:
        raise ValueError('Prototype freeze predates or omits the pilot protocol binding')
    verify([frozen['protocol'],frozen['binary'],frozen['math_validation']])
    frozen_sources=frozen.get('source_inputs',[])
    if not frozen_sources or not isinstance(frozen.get('readout_method'),str) or not frozen['readout_method']:
        raise ValueError('Final prototype source/readout provenance missing')
    verify(frozen_sources)
    math_report,_=read_snapshot(frozen['math_validation']['path'])
    if math_report.get('passed') is not True:
        raise ValueError('Final prototype math validation not passed')
    if producer.get('binary')!=frozen['binary']:
        raise ValueError('Rendered binary differs from frozen final prototype')
    protocol_time=datetime.fromisoformat(protocol['frozen_at_utc'])
    prototype_time=datetime.fromisoformat(frozen['frozen_at_utc'])
    render_time=datetime.fromisoformat(producer['render_started_at_utc'])
    if not protocol_time<=prototype_time<=render_time:
        raise ValueError('Protocol/prototype/audio-batch chronology differs')
    proof=producer.get('cases',[])
    if len(proof)!=6 or {row['id'] for row in proof}!=set(IDS):
        raise ValueError('Producer case proof inventory differs')
    by_id={row['id']:row for row in proof}
    protocol_cases={row['id']:row for row in protocol['cases']}
    for entry in capture['cases']:
        ident=entry['id'];row=by_id[ident];requested=protocol_cases[ident]
        if (row.get('midi'),row.get('velocity'),row.get('frames'))!=(requested['midi'],requested['midi_velocity'],182400):
            raise ValueError('Producer case event/frame request differs:'+ident)
        for role in ('baseline','candidate'):
            if row.get(role)!=entry.get(role):
                raise ValueError('Capture/producer audio binding differs:'+ident+'/'+role)
        for key in ('mechanical_state_bit_parity','force_bit_parity'):
            if type(row.get(key)) is not bool:raise ValueError('Missing producer proof:'+key)
        if type(row.get('new_faults')) is not int or row['new_faults']<0:
            raise ValueError('Missing producer numeric-fault counter')
        declared=row['mechanical_state_bit_parity'] and row['force_bit_parity']
        if entry.get('mechanical_state_force_bit_parity') is not declared or entry.get('new_faults')!=row['new_faults']:
            raise ValueError('Capture guard claims differ from bound producer proof')
    return by_id,[producer['protocol'],*records,freeze_record,frozen['binary'],frozen['math_validation'],*frozen_sources]


def evaluate(capture_path):
    protocol,rows=locked();reference_path=OUT/'reference-control.json';control=read(reference_path)
    verify([control['protocol'],control['tool']])
    if (OUT/'candidate-result.json').exists() or (OUT/'candidate-opening-started.json').exists():
        raise ValueError('Candidate evaluation already started; inspect it rather than silently restarting')
    # This receipt is intentionally written before opening the capture manifest,
    # producer evidence or a single candidate output byte.
    write(OUT/'analysis-code-freeze.json',{'frozen_at_utc':now(),'protocol':record(OUT/'protocol.json'),
        'reference_control':record(reference_path),'metric_tool':record(__file__),
        'candidate_capture_manifest_path':str(capture_path.resolve()),'candidate_bytes_opened':False})
    write(OUT/'candidate-opening-started.json',{'started_at_utc':now(),'code_freeze':record(OUT/'analysis-code-freeze.json')})
    capture,capture_identity=read_snapshot(capture_path)
    if capture.get('protocol_sha256')!=PROTOCOL_SHA:raise ValueError('Producer did not bind the frozen pilot protocol')
    verify([capture['producer_receipt']]);producer,producer_identity=read_snapshot(capture['producer_receipt']['path'])
    if producer_identity['sha256']!=capture['producer_receipt']['sha256']:
        raise ValueError('Producer receipt changed during read')
    cases=capture['cases']
    if len(cases)!=6 or {r['id'] for r in cases}!=set(IDS):raise ValueError('Candidate pilot inventory differs')
    proof,producer_records=producer_evidence(producer,protocol,capture)
    baseline_rows={r['id']:r for r in control['cases']};results=[]
    for entry in cases:
        ident=entry['id'];old=baseline_rows[ident];verify([entry['baseline'],entry['candidate']])
        braw,bbytes=load_float(entry['baseline']['path']);craw,_=load_float(entry['candidate']['path'])
        cached,cached_bytes=load_float(old['baseline_audio']['path'])
        baseline_exact=bbytes==cached_bytes
        gain=old['baseline']['fixed_gain'];onset=old['baseline']['fixed_onset_frame']
        candidate=observation_features(craw.astype(np.float64),onset,gain,old['reference'],rows[ident])
        base=old['baseline'];floor=old['reference']['sustain_power']*1e-10
        first_b=max(0.,base['early'][0]['broad_signed_error_db']);first_c=max(0.,candidate['early'][0]['broad_signed_error_db'])
        ring_b=max(0.,base['early'][1]['ring_signed_error_db']);ring_c=max(0.,candidate['early'][1]['ring_signed_error_db'])
        harmonic=candidate['late_harmonic_MAE_db']-base['late_harmonic_MAE_db']
        envelope=candidate['late_envelope']['MAE_db']-base['late_envelope']['MAE_db']
        drift=20*math.log10(candidate['sustain_RMS']/base['sustain_RMS'])
        window_changes=[c['five_band_MAE_db']-b['five_band_MAE_db'] for c,b in zip(candidate['early'],base['early'])]
        shifts={}
        for name in base['stereo']:
            b,c=base['stereo'][name],candidate['stereo'][name]
            shifts[name]={'LR_db':c['LR_db']-b['LR_db'],'mono_energy_db':power_db(c['mono_power'],b['mono_power'],floor)}
        gates={
            'baseline_payload_exact_to_cached_control':baseline_exact,
            'mechanical_state_force_bit_parity':proof[ident]['mechanical_state_bit_parity'] and proof[ident]['force_bit_parity'],
            'no_new_faults':proof[ident]['new_faults']==0,
            'late_harmonic_MAE':harmonic<=.75,'late_envelope_MAE':envelope<=.75,
            'late_RMS_drift':abs(drift)<=.5,'stereo_LR_shift':abs(shifts['sustain']['LR_db'])<=.5,
            'mono_energy_shift':abs(shifts['sustain']['mono_energy_db'])<=.75}
        if ident.startswith('C3'):
            gates.update(C3_first5_excess_reduction=first_b-first_c>=3.,C3_ring5_20_excess_reduction=ring_b-ring_c>=3.)
        else:gates['each_early_window_band_MAE']=max(window_changes)<=1.
        optional=None
        if entry.get('stems'):
            parts=[]
            for name in ('primary','secondary','transient'):
                verify([entry['stems'][name]]);part,_=load_float(entry['stems'][name]['path']);parts.append(part.astype(np.float64))
            reconstruction=float(np.max(np.abs(sum(parts)-braw)))
            if reconstruction>1e-5:raise ValueError('Optional intact stems do not reconstruct baseline')
            t_half=parts[0]+parts[1]+.5*parts[2]
            optional={'scope':'Observational diagnostic only; not the causal candidate and not a promotion decision.',
                'stem_reconstruction_maximum_abs_error':reconstruction,
                'metrics':observation_features(t_half,onset,gain,old['reference'],rows[ident])}
        result={'id':ident,'baseline_audio':entry['baseline'],'candidate_audio':entry['candidate'],
            'producer_guard_fields':{'mechanical_state_force_bit_parity':entry.get('mechanical_state_force_bit_parity'),'new_faults':entry.get('new_faults')},
            'candidate':candidate,'changes':{'first5_positive_excess_reduction_db':first_b-first_c,
                'ring5_20_positive_excess_reduction_db':ring_b-ring_c,
                'late_harmonic_MAE_db':harmonic,'late_envelope_MAE_db':envelope,'late_RMS_db':drift,
                'early_window_band_MAE_db':window_changes,'stereo':shifts},
            'gates':gates,'passes_all_case_gates':all(gates.values()),'optional_T_half_control':optional}
        results.append(result);print(ident,'PASS' if result['passes_all_case_gates'] else 'FAIL',gates,flush=True)
    locked()
    verify([capture_identity,producer_identity,*producer_records])
    for entry in cases:verify([entry['baseline'],entry['candidate']])
    result={'schema_version':1,'completed_at_utc':now(),'protocol':record(OUT/'protocol.json'),
        'code_freeze':record(OUT/'analysis-code-freeze.json'),'candidate_opening':record(OUT/'candidate-opening-started.json'),
        'reference_control':record(reference_path),'capture_manifest':capture_identity,
        'producer_receipt':producer_identity,'verified_producer_inputs':producer_records,'metric_tool':record(__file__),'cases':results,
        'passes_all_pilot_gates':all(r['passes_all_case_gates'] for r in results),
        'default_promoted':False,'fit_or_acquisition':False,
        'decision':'Root decides whether fullTRAIN34 confirmation/new listening is justified; this pilot never promotes a model.',
        'limits':['Signed errors retained: positive-excess reduction can also reward excessive attenuation.',
            '15ms Hann ENBW is about100Hz;740–810Hz is leakage-weighted local power,not a uniquely isolated partial.',
            'No candidate-specific gain/onset trim; unchanged onset detector is diagnostic only.',
            'Early power/texture agreement does not establish perceived click removal or real hammer latency.',
            'Mechanical state/force parity is supplied by the bound producer proof,not inferred from audio.',
            'TRAIN-only onepiano/capturechain; no historical evaluation or independent generalization.']}
    write(OUT/'candidate-result.json',result);write(ROOT/'Validation/full-causal-radiation-pilot.json',result)
    print('ALL PILOT GATES:',result['passes_all_pilot_gates'],flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=('references','candidate','verify'))
    parser.add_argument('--capture',type=Path)
    args=parser.parse_args()
    if args.stage=='references':references()
    elif args.stage=='candidate':
        if args.capture is None:parser.error('--capture required')
        evaluate(args.capture)
    else:
        locked()
        p=OUT/'reference-control.json'
        if p.exists():
            d=read(p);verify([d['protocol'],d['tool']])
        p=OUT/'candidate-result.json'
        if p.exists():
            d=read(p);verify([d[k] for k in ('protocol','code_freeze','candidate_opening','reference_control','capture_manifest','producer_receipt','metric_tool')])
            for row in d['cases']:verify([row['baseline_audio'],row['candidate_audio']])
        print('Frozen protocol,source inputs and available measurements verified')


if __name__=='__main__':main()
