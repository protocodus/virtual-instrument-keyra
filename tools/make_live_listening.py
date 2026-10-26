#!/usr/bin/env python3
"""Export reproducible listening aids; never used to fit numeric parameters."""
import argparse
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

import numpy as np
from scipy import signal
from scipy.io import wavfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('keyra_benchmark',ROOT/'Research/GrandPianoV2/tools/benchmark.py')
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)


def encode(path, data, rate=48000):
    temporary = ROOT/'out'/path.with_suffix('.wav').name
    wavfile.write(temporary,rate,data.astype(np.float32))
    subprocess.run(['ffmpeg','-v','error','-y','-i',str(temporary),'-c:a','libmp3lame','-b:a','256k',str(path)],check=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--renderer',type=Path,default=ROOT/'build/keyra_preview_render')
    a=p.parse_args()
    destination=ROOT/'Audio';destination.mkdir(exist_ok=True)
    (ROOT/'out').mkdir(exist_ok=True)
    names=['concert-grand','studio-grand','upright','felt-upright']
    songs=[]
    for instrument,name in enumerate(names):
        raw=ROOT/'out'/f'{name}.wav'
        subprocess.run([str(a.renderer.resolve()),'--output',str(raw),'--events',str(ROOT/'Research/GrandPianoV2/scores/01_nocturne.events'),
                        '--seconds','37.75','--param',f'instrument={instrument}'],check=True,stdout=subprocess.DEVNULL)
        sr,x=b.load_audio(raw); songs.append((name,x))
    common_gain=10**(-2/20)/max(np.max(np.abs(x)) for _,x in songs)
    entries=[]
    for name,x in songs:
        x=x*common_gain;x[-7200:]*=np.linspace(1,0,7200)[:,None]
        path=destination/f'{name}.mp3';encode(path,x)
        entries.append({'file':path.name,'kind':'original performance','gain':float(common_gain),
                        'seconds':37.75,'score':'Research/GrandPianoV2/scores/01_nocturne.events',
                        'mp3_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    for family,case in [('grand','C4v8'),('upright','G3v8')]:
        if family=='grand':
            reference=ROOT/'Research/GrandPianoV2/reference/wav'/f'{case}.wav'
            attribution='Alexander Holm, Salamander Grand Piano V3, CC BY 3.0. Aligned, gain matched, cropped, faded and concatenated for comparison.'
        else:
            manifest=json.loads((ROOT/'References/Upright/manifest.json').read_text())
            item=next(s for s in manifest['samples'] if s['feature_id']==case)
            reference=ROOT/'References/Upright'/item['local_path']
            attribution='VCSL Yamaha upright, CC0 1.0. Aligned, gain matched, cropped, faded and concatenated for comparison.'
        clips=[]
        for path in (reference,ROOT/'out'/family/f'{case}.wav'):
            sr,x=b.load_audio(path);onset,_=b.onset_index(x,sr);x=x[onset:onset+int(4*sr)]
            if x.shape[1]==1:x=np.repeat(x,2,axis=1)
            if sr!=48000:
                import math
                gcd=math.gcd(sr,48000);x=signal.resample_poly(x,48000//gcd,sr//gcd)
            x=x[:192000];x=np.pad(x,((0,max(0,192000-len(x))),(0,0)))
            energy=np.sqrt(np.mean(x[2400:36000]**2));x*=.09/max(energy,1e-12)
            x[-4800:]*=np.linspace(1,0,4800)[:,None];clips.append(x)
        comparison=np.concatenate([clips[0],np.zeros((24000,2)),clips[1]])
        comparison*=min(1,10**(-2/20)/max(np.max(abs(comparison)),1e-12))
        path=destination/f'{family}-{case}-real-live.mp3';encode(path,comparison)
        entries.append({'file':path.name,'kind':'held-out recording comparison','order':['real recording','live modal model'],
                        'segment_start_seconds':[0,4.5],'seconds':8.5,'attribution':attribution,
                        'reference_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),
                        'limits':'One early RMS gain per segment, held fixed through decay. Labeled listening aid, not a blind test or dynamics validation.',
                        'mp3_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    (destination/'manifest.json').write_text(json.dumps({'schema_version':1,'engine_sha256':hashlib.sha256((ROOT/'src/Piano.cpp').read_bytes()).hexdigest(),
                                                        'entries':entries},indent=2)+'\n')
    print(destination)


if __name__=='__main__':main()
