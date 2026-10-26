#!/usr/bin/env python3
"""Reproduce presentation from fingerprint-matched raw inputs; no DSP render."""
from pathlib import Path
import argparse,hashlib,importlib.util,json,subprocess,sys
sys.dont_write_bytecode=True
import numpy as np
from scipy.io import wavfile

HERE=Path(__file__).resolve().parent
sha=lambda data:hashlib.sha256(data).hexdigest()
def pcm24(path):
    return subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-f','s24le','-acodec','pcm_s24le','-'])
def decode24(data):
    b=np.frombuffer(data,dtype=np.uint8).reshape(-1,3).astype(np.int32)
    x=b[:,0]+(b[:,1]<<8)+(b[:,2]<<16)
    return ((x^0x800000)-0x800000).reshape(-1,2).astype(np.float64)/(2**23)
def load_input(path,record):
    if record['encoding']=='float32-WAV':
        rate,x=wavfile.read(path)
        if rate!=48000 or x.dtype!=np.float32 or x.shape!=(record['frames'],2):raise ValueError('Unexpected float32 source: '+str(path))
        digest=sha(np.asarray(x,dtype='<f4').tobytes());x=x.astype(np.float64)
    elif record['encoding']=='PCM24-audio':
        stream=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','a:0','-show_entries','stream=sample_rate,channels','-of','json',str(path)],text=True))['streams'][0]
        if int(stream['sample_rate'])!=48000 or stream['channels']!=2:raise ValueError('Unexpected recording format: '+str(path))
        data=pcm24(path);digest=sha(data);x=decode24(data)
        if len(x)!=record['frames']:raise ValueError('Recording frame count mismatch')
    else:raise ValueError('Unknown source encoding')
    if digest!=record['pcm_sha256'] or not np.isfinite(x).all():raise ValueError('Source PCM fingerprint mismatch: '+str(path))
    return x
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inputs',required=True,type=Path,help='JSON map from manifest source IDs to local audio paths')
    parser.add_argument('--output',required=True,type=Path,help='New or empty output directory')
    parser.add_argument('--repository-root',type=Path,default=HERE.parents[1])
    args=parser.parse_args()
    manifest=json.loads((HERE/'manifest.json').read_text())
    source_map=json.loads(args.inputs.read_text());sources={}
    for ident,record in manifest['raw_inputs'].items():
        if ident not in source_map:raise ValueError('Missing source ID: '+ident)
        path=Path(source_map[ident]);path=path if path.is_absolute() else args.inputs.resolve().parent/path
        sources[ident]=load_input(path,record)
    args.output.mkdir(parents=True,exist_ok=True)
    if any(args.output.iterdir()):raise ValueError('Use a new or empty output directory')
    code=args.repository_root/manifest['presentation_code']['file']
    if sha(code.read_bytes())!=manifest['presentation_code']['sha256']:raise ValueError('Presentation code fingerprint mismatch')
    spec=importlib.util.spec_from_file_location('keyra_frozen_presentation',code)
    presentation=importlib.util.module_from_spec(spec);spec.loader.exec_module(presentation)
    recipe=manifest['music_recipe'];ir=presentation.room_ir();versions={}
    if sha(np.asarray(ir,dtype='<f8').tobytes())!=recipe['procedural_ir_float64_sha256']:raise ValueError('Procedural IR mismatch')
    for engine in ('old','new'):
        source=sources['music-'+engine]
        for kind in ('dry','room'):
            x=source.copy() if kind=='dry' else presentation.presentation(source,ir,recipe['room_wet'])
            x*=recipe['control_rms_gain_before_fade'][kind]
            n=recipe['end_fade_frames'];x[-n:]*=np.linspace(1,0,n)[:,None]
            x*=recipe['original_common_true_peak_gain']
            x*=recipe['extra_shared_safety_gain']
            versions[(engine,kind)]=x
    outputs={}
    for kind in ('dry','room'):
        outputs['old-then-new-'+kind+'.flac']=np.concatenate([versions[('old',kind)],np.zeros((24000,2)),versions[('new',kind)]])
    recipe=manifest['C6_recipe'];clips=[]
    for case in recipe['cases']:
        ident=case['id'];segments=[]
        for engine in ('real','old','new'):
            start=case['fixed_onset_frames'][engine];count=recipe['segment_frames']
            x=sources[ident+'-'+engine][start:start+count].copy()
            if len(x)!=count:raise ValueError('Insufficient actual excerpt support')
            x*=case['fixed_gains'][engine]
            n=recipe['end_fade_frames'];x[-n:]*=np.linspace(1,0,n)[:,None]
            x*=recipe['common_presentation_gain_all_six_segments'];segments.append(x)
        gap=np.zeros((recipe['within_group_gap_frames'],2))
        clips.append(np.concatenate([segments[0],gap,segments[1],gap,segments[2]]))
    outputs['C6-v4-v12-real-old-new.flac']=np.concatenate([clips[0],np.zeros((recipe['between_group_gap_frames'],2)),clips[1]])
    checks=[]
    for name,x in outputs.items():
        wav=args.output/(Path(name).stem+'.wav');flac=args.output/name
        wavfile.write(wav,48000,x.astype(np.float32))
        subprocess.run(['ffmpeg','-v','error','-y','-i',str(wav),'-c:a','flac','-sample_fmt','s32','-bits_per_raw_sample','24',str(flac)],check=True)
        decoded=pcm24(flac)
        if decoded!=pcm24(wav) or sha(decoded)!=manifest['files'][name]['pcm24_sha256']:raise ValueError('Reproduction PCM mismatch: '+name)
        q=decode24(decoded);peak=float(presentation.true_peak(q))
        if not np.isfinite(q).all() or len(q)!=manifest['files'][name]['frames'] or peak>10**(-2/20)+3e-7:raise ValueError('Output validation failed: '+name)
        checks.append({'file':name,'pcm24_sha256':sha(decoded),'frames':len(q),'true_peak_4x':peak,'staged_PCM24_identical':True})
    (args.output/'checks.json').write_text(json.dumps({'scope':'Presentation reproduction only; no DSP synthesis or model approval','checks':checks},indent=2)+'\n')
    print(json.dumps({'reproduced_files':len(checks),'decoded_PCM24_identical':True,'output':str(args.output)},indent=2))
if __name__=='__main__':main()
