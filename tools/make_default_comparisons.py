#!/usr/bin/env python3
"""Export real / five-anchor / expanded-default listening comparisons."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy.io import wavfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('keyra_comparison_benchmark',ROOT/'Research/GrandPianoV2/tools/benchmark.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)


def main():
    fresh=json.loads((ROOT/'Validation/fresh-grand.json').read_text())
    source=json.loads((ROOT/'References/GrandExpanded/manifest.json').read_text())
    destination=ROOT/'Audio';destination.mkdir(exist_ok=True)
    entries=[]
    for name in ('A3v8','D#4v8','A4v8'):
        item=next(row for row in source['samples'] if row['id']==name)
        paths=[ROOT/'References/GrandExpanded'/item['wav_path'],
               ROOT/'out/fresh-grand/baseline'/f'{name}.wav',
               ROOT/'out/fresh-grand/candidate'/f'{name}.wav']
        clips=[];gains=[]
        for path in paths:
            sr,x=b.load_audio(path)
            if sr!=48000 or x.shape[1]!=2:raise ValueError('Expected stereo48kHz audio')
            onset,_=b.onset_index(x,sr);x=x[onset:onset+192000]
            x=np.pad(x,((0,max(0,192000-len(x))),(0,0)))
            gain=.09/max(float(np.sqrt(np.mean(x[2400:36000]**2))),1e-20)
            x=x*gain;x[-4800:]*=np.linspace(1,0,4800)[:,None]
            clips.append(x);gains.append(gain)
        gap=np.zeros((24000,2))
        y=np.concatenate([clips[0],gap,clips[1],gap,clips[2]])
        common=min(1,10**(-2/20)/max(float(np.max(abs(y))),1e-20));y*=common
        stem='default-'+name.replace('#','sharp')+'-real-before-after'
        temporary=ROOT/'out'/f'{stem}.wav';wavfile.write(temporary,48000,y.astype(np.float32))
        target=destination/f'{stem}.mp3'
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(temporary),'-c:a','libmp3lame','-b:a','256k',str(target)],check=True)
        entries.append({'file':target.name,'case':name,'order':['real recording','five-anchor phase-aware model','expanded default'],
                        'segment_start_seconds':[0,4.5,9.0],'duration_seconds':13,
                        'early_rms_gains':gains,'common_peak_gain':common,
                        'reference_sha256':b.sha256(paths[0]),'audio_sha256':b.sha256(target),
                        'attribution':'Alexander Holm, Salamander Grand Piano V3, CC BY 3.0. Cropped/onset-aligned, gain matched, faded and concatenated; no EQ, room or limiter.',
                        'limits':'Labeled listening aid, not a blind test. Per-segment early RMS matching preserves the later decay but does not evaluate absolute dynamics.'})
    manifest={'schema_version':1,'fresh_report_sha256':b.sha256(ROOT/'Validation/fresh-grand.json'),
              'baseline_renderer_sha256':fresh['baseline_renderer_sha256'],
              'candidate_renderer_sha256':fresh['candidate_renderer_sha256'],
              'calibration_sha256':hashlib.sha256((ROOT/'src/LiveCalibration.h').read_bytes()).hexdigest(),'entries':entries}
    (destination/'default-comparisons.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(destination/'default-comparisons.json')


if __name__=='__main__':main()
