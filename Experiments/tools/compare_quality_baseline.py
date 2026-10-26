#!/usr/bin/env python3
"""Compare the preserved physical quality baseline and reduced live renderer.

Same event passage, export rate, whole-file RMS matching, and procedural room
for both. The mechanical models intentionally differ; source hashes identify
them. This is a listening comparison, not a claim that note metrics choose one.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy.io import wavfile

ROOT=Path(__file__).resolve().parents[1]
REF=ROOT/'Research/GrandPianoV2'
spec=importlib.util.spec_from_file_location('keyra_reference_export',REF/'tools/render.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    sr,x=wavfile.read(path)
    if x.dtype!=np.float32 or x.ndim!=2 or x.shape[1]!=2:raise ValueError('Expected native stereo float32 WAV')
    return sr,x.astype(np.float64)


def reference_input_paths():
    return [REF/'src/grand.cpp', REF/'src/calibration.h', ROOT/'build/keyra_reference',
            ROOT/'out/quality-baseline/passage.events']


def verify_reference_receipt():
    receipt=json.loads((ROOT/'Validation/quality-baseline-reference.json').read_text())
    for relative,expected in receipt['sha256'].items():
        if sha(ROOT/relative)!=expected:raise ValueError(f'Reference receipt mismatch: {relative}')
    return receipt


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render-reference',action='store_true',help='Regenerate the expensive original and its synthesis receipt')
    args=parser.parse_args()
    folder=ROOT/'out/quality-baseline';destination=ROOT/'Audio/quality-baseline';destination.mkdir(parents=True,exist_ok=True)
    original=folder/'original-192k.wav';events=folder/'passage.events'
    reference_command=[str(ROOT/'build/keyra_reference'),'--events',str(events),'--output',str(original),
                       '--sample-rate','192000','--duration','9','--metrics',str(folder/'original-192k.json')]
    if args.render_reference:
        inputs={str(path.relative_to(ROOT)):sha(path) for path in reference_input_paths()}
        subprocess.run(reference_command,check=True)
        if inputs!={str(path.relative_to(ROOT)):sha(path) for path in reference_input_paths()}:
            raise ValueError('Reference inputs changed during synthesis')
        paths=reference_input_paths()+[original,folder/'original-192k.json']
        receipt={'schema_version':1,'command':reference_command,
                 'binary_path':'build/keyra_reference',
                 'receipt_method':'Inputs hashed before/after successful renderer execution.',
                 'sha256':{str(path.relative_to(ROOT)):sha(path) for path in paths}}
        (ROOT/'Validation/quality-baseline-reference.json').write_text(json.dumps(receipt,indent=2)+'\n')
    if not original.exists():raise FileNotFoundError('Use --render-reference; see docs/QUALITY_BASELINE.md')
    reference_receipt=verify_reference_receipt()
    live=folder/'reduced-48k.wav'
    command=[str(ROOT/'build/keyra_preview_render'),'--events',str(events),'--output',str(live),'--rate','48000','--seconds','9',
             '--param','distance=0','--report',str(folder/'reduced-48k.json')]
    subprocess.run(command,check=True,stdout=subprocess.DEVNULL)
    a=r.downsample(original)
    sr,b=load(live)
    if sr!=48000 or a.shape!=b.shape:raise ValueError('Different comparison formats/durations')
    impulse=r.room_ir();versions={};trims={};metrics={}
    for name,data in [('original',a),('reduced',b)]:
        for kind,y in [('dry',data),('room',r.presentation(data,impulse,.16))]:
            y=y.copy();gain=.08/max(float(np.sqrt(np.mean(y*y))),1e-20)
            y*=gain;y[-7200:]*=np.linspace(1,0,7200)[:,None]
            versions[(name,kind)]=y;trims[f'{name}-{kind}']=gain
    common=10**(-2/20)/max(r.true_peak(y) for y in versions.values())
    entries=[]
    for (name,kind),data in versions.items():
        data*=common;path=destination/f'{name}-{kind}.mp3';temporary=folder/f'{name}-{kind}-export.wav'
        wavfile.write(temporary,48000,data.astype(np.float32))
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(temporary),'-c:a','libmp3lame','-b:a','320k',str(path)],check=True)
        powers=np.mean(data*data,axis=0)
        metrics[f'{name}-{kind}']={'rms':float(np.sqrt(np.mean(data*data))),
            'left_right_correlation':float(np.mean(data[:,0]*data[:,1])/max(np.sqrt(powers[0]*powers[1]),1e-30)),
            'right_minus_left_power_db':float(10*np.log10(max(powers[1],1e-30)/max(powers[0],1e-30)))}
        entries.append({'file':str(path.relative_to(ROOT/'Audio')),'sha256':sha(path),'engine':name,'presentation':kind,
                        'duration_seconds':len(data)/48000,'whole_file_rms_gain_before_fade':trims[f'{name}-{kind}'],
                        'common_true_peak_gain':common})
    # A compact dry pair makes the algorithm comparison easy to repeat.
    gap=np.zeros((24000,2));triplet=np.concatenate([versions[('original','dry')],gap,versions[('reduced','dry')]])
    temporary=folder/'original-reduced-dry.wav';wavfile.write(temporary,48000,triplet.astype(np.float32))
    path=destination/'original-then-reduced-dry.mp3'
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(temporary),'-c:a','libmp3lame','-b:a','320k',str(path)],check=True)
    entries.append({'file':str(path.relative_to(ROOT/'Audio')),'sha256':sha(path),'order':['preserved physical original','reduced live model'],
                    'segment_start_seconds':[0,9.5],'duration_seconds':18.5,'presentation':'dry, whole-file RMS matched before end fade'})
    report={'schema_version':2,'purpose':'Restore the preserved full physical renderer as the quality baseline; compare full live preview with internal room bypassed.',
            'events_sha256':sha(events),'events_source':'First six seconds of the original nocturne score, followed by three seconds of held/tail behavior.',
            'reference_source_sha256':sha(REF/'src/grand.cpp'),'reference_calibration_sha256':sha(REF/'src/calibration.h'),
            'reference_binary_sha256':reference_receipt['sha256'][reference_receipt['binary_path']],
            'reference_raw_sha256':sha(original),
            'reference_receipt':reference_receipt,
            'reduced_source_sha256':sha(ROOT/'src/Piano.cpp'),'reduced_calibration_sha256':sha(ROOT/'src/LiveCalibration.h'),
            'reduced_binary_sha256':sha(ROOT/'build/keyra_preview_render'),'reduced_raw_sha256':sha(live),
            'reduced_command':command,'output_rate':48000,'reference_internal_rate':192000,'reduced_internal_rate':48000,
            'reduced_parameters':json.loads((folder/'reduced-48k.json').read_text())['parameters'],
            'reduced_setting_policy':'Default body/resonance .3 and mechanical noise .1 retained; only internal room/distance is zero for shared external room.',
            'gain_policy':'Each complete nine-second engine/presentation file matches .08 stereo RMS before the same150ms end fade; one final true-peak gain is shared across all files.',
            'room':'Identical preserved procedural room_ir and presentation(), wet=.16 for both room files; no added room for dry files.',
            'native_filter_difference':'Reference includes its24Hz output high-pass; reduced engine includes7Hz DC rejection. These native differences are retained, with no additional EQ.',
            'limits':'Labeled comparison, not a blind listening verdict. Different internal synthesis rates are documented; the same output rate and room prevent presentation being mistaken for a proof of engine parity.',
            'metrics':metrics,'entries':entries}
    (destination/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'Validation/quality-baseline-comparison.json').write_text(json.dumps(report,indent=2)+'\n')
    print(destination)


if __name__=='__main__':main()
