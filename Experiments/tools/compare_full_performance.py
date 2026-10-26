#!/usr/bin/env python3
"""Fair musical listening comparison of full control and connected full core.

Uses the authenticated renderer snapshot from full-renderer validation. It does
not rebuild the evolving API or read acoustic evaluation recordings.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess

import numpy as np
from scipy.io import wavfile

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'out/full-performance'
AUDIO=ROOT/'Audio/full-performance'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render',action='store_true',help='Render the two nine-second full-model versions')
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True);AUDIO.mkdir(parents=True,exist_ok=True)
    proof_path=OUT/'renderer-validation.json'
    if not proof_path.exists():
        shutil.copyfile(ROOT/'Validation/full-renderer.json',proof_path)
    proof=json.loads(proof_path.read_text())
    producer=ROOT/'out/full-render-validation/keyra_full_render'
    source_root=Path(proof['source_snapshot'])
    if sha(producer)!=proof['binary_sha256']:
        raise ValueError('Renderer snapshot mismatch')
    for name,expected in proof['source_sha256'].items():
        if sha(source_root/name)!=expected:
            raise ValueError('Renderer source snapshot mismatch: '+name)
    if proof['source_sha256']['src/full_instrument/PreparedCalibration.h']!='619d6bf4d3200a6b55007a1abcc0658e76a14124ce5f3abad9f5f4b94d8979f7':
        raise ValueError('Expected the original control calibration')
    renderer=OUT/'renderer-snapshot'
    if not renderer.exists():
        shutil.copy2(producer,renderer)
    if sha(renderer)!=proof['binary_sha256']:
        raise ValueError('Listening renderer identity changed')
    score=ROOT/'out/quality-baseline/passage.events'
    source_score=ROOT/'Research/GrandPianoV2/scores/01_nocturne.events'
    # The exact prepared passage is shared with the earlier quality comparison.
    # Its final held note and pedal remain held during the three-second tail.
    if not score.is_file() or not source_score.is_file():
        raise FileNotFoundError('Run the existing quality-baseline preparation first')
    expected=[line.strip() for line in source_score.read_text().splitlines()
              if line.strip() and not line.lstrip().startswith('#') and float(line.split()[0])<6]
    actual=[line.strip() for line in score.read_text().splitlines()
            if line.strip() and not line.lstrip().startswith('#')]
    if actual!=expected:
        raise ValueError('Prepared passage is not the original first-six-second event prefix')
    config={
        'renderer_sha256':sha(renderer),'score_sha256':sha(score),
        'renderer_validation_sha256':sha(proof_path),'seed':123456,'rate':48000,'seconds':9,
        'variants':{
            'control':['--param','humanization=0','--param','mechanicalLevel=0','--repetition','0'],
            'connected':['--param','humanization=.65','--param','mechanicalLevel=.025','--repetition','1']}}
    guard=OUT/'synthesis-inputs.json'
    if guard.exists() and json.loads(guard.read_text())!=config:
        raise ValueError('Use a new listening folder when inputs change')
    guard.write_text(json.dumps(config,indent=2)+'\n')
    renders={}
    for name,extra in config['variants'].items():
        audio=OUT/(name+'.wav');report=OUT/(name+'.json');receipt=OUT/(name+'-synthesis.json')
        command=[str(renderer),'--events',str(score),'--rate','48000','--seconds','9',
                 '--seed','123456','--param','gain=0','--output',str(audio),'--report',str(report),*extra]
        if args.render:
            subprocess.run(command,check=True,capture_output=True,text=True)
            if sha(renderer)!=config['renderer_sha256'] or sha(score)!=config['score_sha256']:
                raise ValueError('Synthesis input changed during render')
            receipt.write_text(json.dumps({'command':command,'inputs':config,
                'wav_sha256':sha(audio),'report_sha256':sha(report)},indent=2)+'\n')
        if not receipt.is_file():
            raise FileNotFoundError('Use --render to produce the full-model audio')
        record=json.loads(receipt.read_text())
        if record['inputs']!=config or record['wav_sha256']!=sha(audio) or record['report_sha256']!=sha(report):
            raise ValueError('Synthesis receipt mismatch: '+name)
        diagnostics=json.loads(report.read_text())
        if diagnostics['fault_flags'] or diagnostics['unsafe_launches'] or diagnostics['events_rejected'] or diagnostics['requests']!=diagnostics['launches']:
            raise ValueError('Fault or missing launch in musical comparison: '+name)
        if diagnostics['sample_rate']!=48000 or diagnostics['frames']!=432000 or diagnostics['seed']!=123456 or diagnostics['pressure_simd']:
            raise ValueError('Unexpected musical renderer configuration')
        rate,x=wavfile.read(audio)
        if rate!=48000 or x.shape!=(432000,2) or x.dtype!=np.float32 or not np.isfinite(x).all():
            raise ValueError('Unexpected musical audio format')
        renders[name]=x.astype(np.float64)
    spec=importlib.util.spec_from_file_location('keyra_shared_presentation',ROOT/'Research/GrandPianoV2/tools/render.py')
    presentation=importlib.util.module_from_spec(spec);spec.loader.exec_module(presentation)
    impulse=presentation.room_ir();versions={};trims={}
    for name,x in renders.items():
        for kind,y in [('dry',x),('room',presentation.presentation(x,impulse,.16))]:
            y=y.copy();gain=.08/max(float(np.sqrt(np.mean(y*y))),1.e-30)
            y*=gain;y[-7200:]*=np.linspace(1,0,7200)[:,None]
            versions[(name,kind)]=y;trims[name+'-'+kind]=gain
    common=10**(-2/20)/max(presentation.true_peak(x) for x in versions.values())
    entries=[]
    def export(name,x,metadata):
        temporary=OUT/(name+'.wav');target=AUDIO/(name+'.flac')
        wavfile.write(temporary,48000,x.astype(np.float32))
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(temporary),'-c:a','flac','-sample_fmt','s32','-bits_per_raw_sample','24',str(target)],check=True)
        pcm=['-f','s24le','-acodec','pcm_s24le','-']
        decoded=subprocess.check_output(['ffmpeg','-v','error','-i',str(target),*pcm])
        expected=subprocess.check_output(['ffmpeg','-v','error','-i',str(temporary),*pcm])
        if decoded!=expected:
            raise ValueError('FLAC PCM conversion mismatch')
        entries.append({'file':target.name,'sha256':sha(target),'pcm24_sha256':hashlib.sha256(decoded).hexdigest(),**metadata})
    for (name,kind),x in versions.items():
        versions[(name,kind)]=x*common
        export(name+'-'+kind,x*common,{'engine':name,'presentation':kind,'duration_seconds':9,
               'rms_gain_before_fade':trims[name+'-'+kind]})
    for kind in ('dry','room'):
        x=np.concatenate([versions[('control',kind)],np.zeros((24000,2)),versions[('connected',kind)]])
        export('control-then-connected-'+kind,x,{'order':['control','connected'],'segment_start_seconds':[0,9.5],
               'presentation':kind,'duration_seconds':18.5})
    manifest={'schema_version':1,'purpose':'Compare original full physical control and connected stateful full instrument; not acoustic parity or listener approval.',
        'synthesis_inputs':config,'source_snapshot':str(source_root),'renderer_validation':proof,
        'performance':'First six seconds of Window at Dusk original algorithmic nocturne performance, then three seconds of held/tail behavior; no added release events.',
        'score_path':str(score),'score_sha256':sha(score),
        'source_score_sha256':sha(source_score),
        'recordings_used':False,'runtime_samples_used':False,
        'presentation_code_sha256':sha(ROOT/'Research/GrandPianoV2/tools/render.py'),
        'exporter_sha256':sha(Path(__file__)),'output_rate':48000,'pcm_bits':24,
        'gain_policy':'Each full nine-second engine/presentation matches .08 stereo RMS before identical150ms ending fade; one common true-peak gain across all versions.',
        'common_true_peak_gain':common,'room':'Same procedural IR and wet=.16; dry versions have no added room.',
        'limits':'Snapshot uses original control calibration/hot float and legacy contact; separate contact/pressure experiments are excluded. Return timing, variation and mechanical levels are authored. No blind preference or realtime/Reason claim.',
        'entries':entries}
    (AUDIO/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(AUDIO)


if __name__=='__main__':
    main()
