#!/usr/bin/env python3
"""Fetch and score eight predeclared, unused pitches after freezing the model.

The manifest locks the model header and case list before any new recording is
downloaded or scored. These are fresh notes from the same piano/session, not
independent-piano validation. This tool does not fit any parameter.
"""
from __future__ import annotations
import argparse
import concurrent.futures
import csv
import importlib.util
import json
import math
from pathlib import Path
import subprocess

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('keyra_existing_evaluation',ROOT/'Tools/evaluate_recordings.py')
evaluation=importlib.util.module_from_spec(spec)
spec.loader.exec_module(evaluation)


def fetch(sample, directory):
    flac=directory/'audio'/(sample['id']+'.flac')
    wav=directory/'wav'/(sample['id']+'.wav')
    flac.parent.mkdir(parents=True,exist_ok=True);wav.parent.mkdir(parents=True,exist_ok=True)
    if not flac.exists():
        temporary=flac.with_suffix('.download')
        subprocess.run(['curl','-fsSL','--retry','2','--max-time','120',sample['source_url'],
                        '-o',str(temporary)],check=True)
        temporary.replace(flac)
    flac_hash=evaluation.sha(flac)
    if sample.get('flac_sha256',flac_hash)!=flac_hash:
        raise ValueError(f"Fresh FLAC hash mismatch: {sample['id']}")
    if not wav.exists():
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(flac),
                        '-c:a','pcm_s24le',str(wav)],check=True)
    pcm=evaluation.restore.decoded_pcm_identity(wav)
    if sample.get('decoded_pcm',pcm)!=pcm:
        raise ValueError(f"Fresh decoded PCM mismatch: {sample['id']}")
    return {**sample,'flac_sha256':flac_hash,'wav_sha256':evaluation.sha(wav),'decoded_pcm':pcm}


def summarize(rows):
    result={'cases':len(rows)}
    for key in evaluation.FIELDS:
        values=[r[key] for r in rows if r[key] is not None and math.isfinite(r[key])]
        result[key]={'mean':float(np.mean(values)),'median':float(np.median(values)),
                     'valid_cases':len(values)} if values else None
    return result


def render(renderer, sample, directory, events, legacy, resonance):
    target=directory/(sample['id']+'.wav')
    command=[str(renderer),'--events',str(events),'--output',str(target),
             '--sample-rate','48000','--duration','4.4','--gain','.7','--resonance',str(resonance)]
    if legacy:command.append('--legacy-attack')
    completed=subprocess.run(command,check=True,capture_output=True,text=True)
    return {'id':sample['id'],'command':command,'output_sha256':evaluation.sha(target),
            'renderer_stdout':completed.stdout.strip()}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest',type=Path,default=ROOT/'Docs/research/fresh-recording-holdout-2026-10-26.json')
    parser.add_argument('--renderer',type=Path,default=ROOT/'build/keyra_render')
    parser.add_argument('--work-dir',type=Path,default=ROOT/'build/fresh-recording-holdout')
    parser.add_argument('--output',type=Path,default=ROOT/'Docs/validation/recording-benchmark-fresh-2026-10-26.json')
    parser.add_argument('--fetch-only',action='store_true')
    parser.add_argument('--jobs',type=int,default=2)
    args=parser.parse_args()
    if args.jobs<1:parser.error('--jobs must be positive')
    manifest=json.loads(args.manifest.read_text())
    if not manifest['locked_before_downloading'] or not manifest['locked_before_scoring']:
        raise ValueError('Fresh recording list must have been locked before downloading and scoring')
    if manifest['model_header_sha256']!=evaluation.sha(ROOT/'Source/DSP/MeasuredModalData.h'):
        raise ValueError('The model changed after the fresh note list was locked; do not recycle this holdout')
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
        verified=list(pool.map(lambda s:fetch(s,args.work_dir),manifest['samples']))
    if args.fetch_only:
        manifest['samples']=verified
        args.manifest.write_text(json.dumps(manifest,indent=2,allow_nan=False)+'\n')
        print(f'Locked and verified {len(verified)} fresh recordings; no features extracted or scored')
        return
    if any('decoded_pcm' not in sample for sample in manifest['samples']):
        raise ValueError('Run --fetch-only to pin decoded PCM identities before evaluation')
    references={}
    events_dir=args.work_dir/'events';events_dir.mkdir(parents=True,exist_ok=True)
    for sample in manifest['samples']:
        reference=evaluation.metrics.extract_features(args.work_dir/'wav'/(sample['id']+'.wav'),sample['midi'])
        reference['split']='fresh_same_piano';references[sample['id']]=reference
        (events_dir/(sample['id']+'.events')).write_text(
            f"0.100000 on {sample['midi']} 61\n4.150000 off {sample['midi']} 0\n")
    report={'schema_version':1,'purpose':manifest['purpose'],'manifest_sha256':evaluation.sha(args.manifest),
            'model_header_sha256':manifest['model_header_sha256'],
            'renderer_sha256':evaluation.sha(args.renderer),
            'engine_sources':{str(p.relative_to(ROOT)):evaluation.sha(p)
                              for p in sorted((ROOT/'Source/DSP').glob('*')) if p.is_file()},
            'sample_rate':48000,'case_count':len(verified),'fitting_used_these_recordings':False,
            'analysis':evaluation.metrics.ANALYSIS,
            'parameters_common':{'gain':.7,'brightness':.5,'width':.75,'tuning':440,
                                 'mute':0,'sustain':0,'sostenuto':0,'soft':0},
            'variants':{}}
    for name,legacy,resonance in [('fixed_attack',True,0),('measured_attack',False,0),
                                ('product_default',False,.25)]:
        directory=args.work_dir/name;directory.mkdir(parents=True,exist_ok=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
            receipts=list(pool.map(lambda s:render(args.renderer,s,directory,
                events_dir/(s['id']+'.events'),legacy,resonance),manifest['samples']))
        rows=[]
        for sample in manifest['samples']:
            model=evaluation.metrics.extract_features(directory/(sample['id']+'.wav'),sample['midi'])
            row=evaluation.comparison(references[sample['id']],model);rows.append(row)
            print(f"{name} {sample['id']}: harmonic {row['harmonic_level_mae_db']:.3f}dB, attack {row['attack_rise10_90_error_ms']:.3f}ms",flush=True)
        report['variants'][name]={'resonance':resonance,'cases':rows,'summary':summarize(rows),
                                  'render_receipts':receipts}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    with args.output.with_suffix('.csv').open('w',newline='') as destination:
        writer=csv.DictWriter(destination,fieldnames=['variant','id','split',*evaluation.FIELDS],lineterminator='\n')
        writer.writeheader()
        for name,variant in report['variants'].items():
            for row in variant['cases']:
                writer.writerow({'variant':name,**{k:row[k] for k in ('id','split',*evaluation.FIELDS)}})
    lines=['# Fresh same-piano holdout — 26 October 2026','',
           'Eight pitches (D♯2–D♯5 and A2–A5, velocity layer 8) were declared and the model '
           'header frozen before any new recording was downloaded or scored. No fitting used '
           'these recordings. They come from the same piano and recording session as the '
           'training data, so they do not establish independent-piano generalization.','',
           '| Mean error; lower is better | Fixed 2 ms | Measured attack | Product default |',
           '|---|---:|---:|---:|']
    for key in evaluation.FIELDS:
        values=[]
        for name in ('fixed_attack','measured_attack','product_default'):
            value=report['variants'][name]['summary'][key]
            values.append(f"{value['mean']:.3f}" if value else '—')
        lines.append('| '+key+' | '+' | '.join(values)+' |')
    lines+=['','The attack comparison uses the exposed resonance control at zero; the product-default '
            'column uses 0.25. All other controls retain their defaults. Every per-case result is '
            'retained in the JSON and CSV, including regressions. These are native-engine '
            'measurements, without a DAW or Rack host in the path.','',
            'Further tuning after reading this report needs another new validation set. '
            'Recorded pedal/release conditions and physical hammer velocities remain unknown; '
            'these measurements do not validate pedal calibration or commercial readiness.','']
    args.output.with_suffix('.md').write_text('\n'.join(lines))
    print(args.output)


if __name__=='__main__':main()
