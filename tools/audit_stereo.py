#!/usr/bin/env python3
"""Report default close-AB stereo mismatch on training notes without fitting it."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('keyra_stereo_benchmark',ROOT/'Research/GrandPianoV2/tools/benchmark.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)


def metrics(path):
    sr,x=b.load_audio(path);onset,_=b.onset_index(x,sr);x=x[onset:]
    if x.shape[1]!=2:raise ValueError('Stereo recordings required')
    rows=[]
    for lo,hi in b.WINDOWS:
        y=x[int(lo*sr):int(hi*sr)]
        power=np.mean(y*y,axis=0);cross=float(np.mean(y[:,0]*y[:,1]))
        mid=.5*(y[:,0]+y[:,1]);side=.5*(y[:,0]-y[:,1])
        # Sample correlation includes any interchannel phase difference; it is
        # not treated as a universal microphone quality score.
        rows.append({'seconds_after_onset':[lo,hi],
                     'left_right_correlation':cross/max(float(np.sqrt(power[0]*power[1])),1e-30),
                     'right_minus_left_power_db':float(10*np.log10(max(power[1],1e-30)/max(power[0],1e-30))),
                     'side_minus_mid_power_db':float(10*np.log10(max(np.mean(side*side),1e-30)/max(np.mean(mid*mid),1e-30)))})
    return rows


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--model-dir',type=Path,default=ROOT/'out/grand')
    p.add_argument('--output',type=Path,default=ROOT/'Validation/default-stereo-audit.json')
    a=p.parse_args()
    source=ROOT/'Research/GrandPianoV2/benchmark/reference_features.json'
    samples=[s for s in json.loads(source.read_text())['samples'] if s['split']=='train']
    rows=[]
    for item in samples:
        reference=ROOT/'Research/GrandPianoV2/reference/wav'/f"{item['id']}.wav"
        model=a.model_dir/f"{item['id']}.wav"
        rows.append({'id':item['id'],'split':'train','reference_sha256':b.sha256(reference),
                     'model_sha256':b.sha256(model),'reference':metrics(reference),'model':metrics(model)})
    result={'schema_version':1,'heldout_cases_used':False,'cases':rows,
            'engine_sha256':hashlib.sha256((ROOT/'src/Piano.cpp').read_bytes()).hexdigest(),
            'limits':'Training diagnostics only. Correlation is not realism or mono-compatibility quality. Microphone geometry, phase, noise and acoustic radiation are not separately identifiable from these observations. No model parameter is fit or changed.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(a.output)


if __name__=='__main__':main()
