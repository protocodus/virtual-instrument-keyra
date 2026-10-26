#!/usr/bin/env python3
"""Export three labeled, RMS-matched real / first live / refit live comparisons.

These are sighted evidence previews, not blind listening decisions. The source
recordings are Alexander Holm's Salamander Grand Piano V3 under CC BY 3.0.
No preview audio is loaded by the instrument.
"""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess

import numpy as np
from scipy.io import wavfile

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('keyra_comparison_evaluation',ROOT/'Tools/evaluate_recordings.py')
evaluation=importlib.util.module_from_spec(spec);spec.loader.exec_module(evaluation)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--initial-renderer',type=Path,default=ROOT/'build/recording-iteration-01/keyra_render')
    parser.add_argument('--final-renderer',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'Docs/audio/recording-comparisons/2026-10-26')
    args=parser.parse_args()
    args.output_dir.mkdir(parents=True,exist_ok=True)
    working=ROOT/'build/recording-comparison-previews';working.mkdir(parents=True,exist_ok=True)
    records=[];pending=[]
    for case in ('C4v8','F#3v8','C6v8'):
        paths=[evaluation.RESEARCH/'reference/wav'/(case+'.wav')]
        receipts=[]
        for name,renderer in [('initial_live',args.initial_renderer),('refit_live',args.final_renderer)]:
            path=working/(case+'-'+name+'.wav')
            command=[str(renderer),'--events',str(evaluation.RESEARCH/'benchmark/events'/(case+'.events')),
                     '--output',str(path),'--sample-rate','48000','--duration','4.4',
                     '--resonance','0','--gain','.7']
            subprocess.run(command,check=True,capture_output=True,text=True)
            paths.append(path)
            receipts.append({'variant':name,'renderer_sha256':evaluation.sha(renderer),'command':command})
        sections=[];details=[]
        for label,path in zip(('real_recording','initial_live','refit_live'),paths):
            rate,full=evaluation.metrics.load_audio(path)
            if rate!=48000:raise ValueError('Preview sources must be 48 kHz')
            onset,_=evaluation.metrics.onset_index(full,rate)
            begin=max(0,onset-int(.05*rate));section=full[begin:begin+int(3.45*rate)].copy()
            # Identical short output fades remove edit discontinuities only.
            fade=int(.01*rate)
            section[:fade]*=np.linspace(0,1,fade)[:,None]
            section[-fade:]*=np.linspace(1,0,fade)[:,None]
            rms=float(np.sqrt(np.mean(section*section)))
            sections.append(section/rms)
            details.append({'variant':label,'source_sha256':evaluation.sha(path),
                            'start_frame':begin,'frames':len(section),'source_rms':rms})
        pending.append((case,sections,details,receipts))
    # One common target for all nine segments. A decaying upper-register note
    # can have enough crest factor that -23 dBFS whole-clip RMS would clip.
    max_unit_peak=max(float(np.max(abs(s))) for _,sections,_,_ in pending for s in sections)
    target=min(10**(-23/20),.95/max_unit_peak)
    target_db=float(20*np.log10(target))
    for case,sections,details,receipts in pending:
        sections=[section*target for section in sections]
        for detail in details:
            detail['gain_db']=float(20*np.log10(target/detail['source_rms']))
            detail['rms_dbfs']=target_db
        gap=np.zeros((int(.45*48000),2))
        joined=np.concatenate([sections[0],gap,sections[1],gap,sections[2]])
        slug=case.replace('#','sharp')+'-real-initial-refit'
        wav=working/(slug+'.wav');mp3=args.output_dir/(slug+'.mp3')
        wavfile.write(wav,48000,joined.astype(np.float32))
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(wav),
                        '-c:a','libmp3lame','-b:a','192k',str(mp3)],check=True)
        records.append({'id':case,'file':mp3.name,'sha256':evaluation.sha(mp3),
                        'segments':details,'renderer_receipts':receipts})
    manifest={'schema_version':1,'sequence':['real_recording','initial_live','refit_live'],
              'level_matching':f'Each 3.45-second stereo segment independently matched to {target_db:.3f} dBFS whole-segment RMS after identical 10ms edit fades; 450ms silent gaps. Common target lowered from -23 dBFS if needed to prevent clipping.',
              'reference_attribution':'Salamander Grand Piano V3 by Alexander Holm, CC BY 3.0; upstream commit 3382bf9496bba2486f5ab0de55a264d1dfc38404.',
              'limits':'Sighted comparisons of the same recorded piano. Both model variants use the reduced live engine, not the preserved physical solver; resonance=0. Preview processing is not used in scoring or runtime synthesis.',
              'cases':records}
    (args.output_dir/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (args.output_dir/'README.md').write_text(
        '# Recording comparisons — 26 October 2026\n\n'
        'Each file plays **real acoustic recording → initial live model → refit live model**. '
        'The two model variants use the reduced live engine; neither is the preserved offline physical solver. '
        'C4 demonstrates the central register, F♯3 exposes pitch interpolation, and C6 exposes remaining upper-register decay gaps.\n\n'
        f'Each segment is independently matched to **{target_db:.3f} dBFS whole-segment stereo RMS**, after identical 10 ms edit fades. '
        'The common target was lowered from −23 dBFS to preserve the upper-register attack peaks without clipping. '
        'The segments last 3.45 seconds, separated by 450 ms silence. Resonance is zero; the other controls use their defaults. '
        'The manifest records the exact trims, source hashes, renderer hashes and commands. These are sighted comparison clips.\n\n'
        'Reference audio: **Salamander Grand Piano V3 by Alexander Holm**, licensed under '
        '[CC BY 3.0](https://creativecommons.org/licenses/by/3.0/), from '
        '[the pinned upstream distribution](https://github.com/sfzinstruments/SalamanderGrandPiano/tree/3382bf9496bba2486f5ab0de55a264d1dfc38404). '
        'The recording excerpts were trimmed, given short edit fades, level-matched and MP3 encoded. '
        'No endorsement is implied. The instrument does not load these recordings.\n')
    print(args.output_dir)


if __name__=='__main__':main()
