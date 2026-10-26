#!/usr/bin/env python3
"""Audit the default grand against TRAIN10 without fitting recording noise.

Retains the existing full-envelope comparison. Adds separate harmonic,
sub-fundamental, subsonic and mains-band diagnostics; none replaces that metric
or classifies the origin of low-frequency energy. No held-out case is rendered.
"""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess

import numpy as np
from scipy import signal

ROOT=Path(__file__).resolve().parents[1]
REFERENCE=ROOT/'Research/GrandPianoV2'
TRAIN_IDS={f'C{o}v{v}' for o in range(2,7) for v in (4,12)}


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    loaded=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def ratio(numerator,denominator): return float(numerator/max(denominator,1e-30))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--renderer',type=Path,default=ROOT/'build/keyra_preview_render')
    parser.add_argument('--scratch-dir',type=Path,default=ROOT/'out/train-audit')
    parser.add_argument('--output',type=Path,default=ROOT/'Validation/default-training-audit.json')
    args=parser.parse_args()
    benchmark=module('keyra_training_benchmark',REFERENCE/'tools/benchmark.py')
    fetch=module('keyra_reference_verification',REFERENCE/'reference/fetch_reference.py')
    source=REFERENCE/'benchmark/reference_features.json'
    rows=[row for row in json.loads(source.read_text())['samples'] if row['split']=='train']
    if {row['id'] for row in rows}!=TRAIN_IDS: raise ValueError('Locked TRAIN10 changed')
    manifest_path=REFERENCE/'reference/manifest.json'
    manifest=json.loads(manifest_path.read_text())
    args.scratch_dir.mkdir(parents=True,exist_ok=True)
    cases=[]
    for reference in rows:
        name=reference['id']
        reference_path=REFERENCE/'reference/wav'/f'{name}.wav'
        pin=next(item for item in manifest['samples'] if item['id']==name)
        verification=fetch.verify_wav(pin,reference_path)
        sr,full=benchmark.load_audio(reference_path)
        onset,_=benchmark.onset_index(full,sr)
        audio=full[onset:]
        path=args.scratch_dir/f'{name}.wav'
        command=[str(args.renderer.resolve()),'--output',str(path),'--rate','48000',
                 '--seconds','4.25','--note',str(reference['midi']),'--velocity',str(reference['midi_velocity']),
                 '--param','instrument=0','--param','noise=0','--param','distance=0','--param','resonance=0','--param','mic=0']
        subprocess.run(command,check=True,stdout=subprocess.DEVNULL)
        model=benchmark.extract_features(path,reference['midi'])
        comparison=benchmark.compare_features(reference,model)
        model_partials={partial['n']:partial for partial in model['partials']}
        windows=[]
        for index,(lo,hi) in enumerate(benchmark.WINDOWS):
            frequencies,power=benchmark.spectrum(audio[int(lo*sr):int(hi*sr)],sr)
            total=float(power.sum())
            harmonic=float(sum(partial['powers'][index] for partial in reference['partials']))
            subfundamental=benchmark.integrated_power(frequencies,power,0,.8*reference['f1_hz'])
            subsonic=benchmark.integrated_power(frequencies,power,0,31.25)
            mains=benchmark.integrated_power(frequencies,power,48,52)
            model_harmonic=sum(model_partials[partial['n']]['powers'][index]
                               for partial in reference['partials'] if partial['n'] in model_partials)
            gain=reference['early_rms']/max(model['early_rms'],1e-20)
            peaks,_=signal.find_peaks(power)
            peaks=peaks[(frequencies[peaks]>5)&(frequencies[peaks]<.8*reference['f1_hz'])]
            peaks=sorted(peaks,key=lambda at:power[at],reverse=True)[:8]
            windows.append({'seconds_after_onset':[lo,hi],'total_hann_power':total,
                            'harmonic_power':harmonic,'harmonic_fraction':ratio(harmonic,total),
                            'subfundamental_power':subfundamental,'subfundamental_fraction':ratio(subfundamental,total),
                            'sub_31_25_hz_power':subsonic,'sub_31_25_hz_fraction':ratio(subsonic,total),
                            '48_52_hz_power':mains,'48_52_hz_fraction':ratio(mains,total),
                            'model_minus_reference_harmonic_power_db':10*math.log10(max(model_harmonic*gain*gain,1e-30)/max(harmonic,1e-30)),
                            'subfundamental_peak_frequencies_hz':[float(frequencies[at]) for at in peaks]})
        last_start=max(0,len(audio)-2*sr)
        f,p=benchmark.spectrum(audio[last_start:],sr)
        tail={'seconds_after_onset':[last_start/sr,len(audio)/sr],
              'sub_31_25_hz_fraction':ratio(benchmark.integrated_power(f,p,0,31.25),p.sum()),
              '48_52_hz_fraction':ratio(benchmark.integrated_power(f,p,48,52),p.sum()),
              'note':'Final library fades/editing may attenuate both piano and background; this is not an independently measured noise floor.'}
        case={'id':name,'split':'train','midi':reference['midi'],'midi_velocity':reference['midi_velocity'],
              'reference_pcm_verified':verification['decoded_pcm_matches'],
              'reference_container_sha256':sha(reference_path),'model_sha256':sha(path),
              'existing_full_comparison':comparison,'windows':windows,'final_two_seconds':tail,
              'pre_onset_duration_seconds':onset/sr,
              'pre_onset_sufficient_for_50_hz_identification':onset>=int(.1*sr),
              'interpretation_limit':'Subfundamental energy can include body/room response or acquisition noise. Spectra and velocity scaling do not prove its cause; do not synthesize hum or subsonic noise to improve a score.'}
        cases.append(case)
        print(f"{name}: full-envelope error {comparison['envelope_mae_db']:.2f}dB; late harmonic power {100*windows[-1]['harmonic_fraction']:.1f}%",flush=True)
    velocity_scaling=[]
    for octave in range(2,7):
        soft=next(case for case in cases if case['id']==f'C{octave}v4')
        hard=next(case for case in cases if case['id']==f'C{octave}v12')
        a,z=soft['windows'][-1],hard['windows'][-1]
        velocity_scaling.append({'midi':soft['midi'],'late_harmonic_hard_minus_soft_db':10*math.log10(ratio(z['harmonic_power'],a['harmonic_power'])),
                                  'late_subfundamental_hard_minus_soft_db':10*math.log10(ratio(z['subfundamental_power'],a['subfundamental_power'])),
                                  'late_subsonic_hard_minus_soft_db':10*math.log10(ratio(z['sub_31_25_hz_power'],a['sub_31_25_hz_power'])),
                                  'late_50_hz_hard_minus_soft_db':10*math.log10(ratio(z['48_52_hz_power'],a['48_52_hz_power']))})
    result={'schema_version':1,'training_ids':sorted(TRAIN_IDS),'heldout_cases_used':False,
            'reference_features_sha256':sha(source),'reference_manifest_sha256':sha(manifest_path),
            'engine_sha256':sha(ROOT/'src/Piano.cpp'),'calibration_sha256':sha(ROOT/'src/LiveCalibration.h'),
            'renderer_sha256':sha(args.renderer),
            'configuration':'Default grand, tone/dynamics defaults, close AB, no authored mechanical noise/room/resonance; output gain -6dB.',
            'analysis':{'existing_full_envelope_metric':'Unchanged preserved benchmark, fixed early RMS gain.',
                        'harmonic_power':'Sum of existing fitted-partial integration bands; not a new realism score.',
                        'subfundamental':'0 to0.8 times measured fundamental, separately reported.',
                        'power_windows':'Hann-squared weighted power, mean stereo power, no mono cancellation.'},
            'cases':cases,'late_velocity_scaling':velocity_scaling,
            'limits':'Training diagnostics only. Retains complete full-envelope error. Below-fundamental/subsonic/mains evidence cannot uniquely identify room/body response or recording contamination. Does not normalize, filter, alter, denoise or fit the recordings.'}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')


if __name__=='__main__':main()
