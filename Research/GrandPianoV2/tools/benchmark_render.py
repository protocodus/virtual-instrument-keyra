#!/usr/bin/env python3
"""Render exactly the locked reference pitches and SFZ-bin representative velocities."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import subprocess

ROOT=Path(__file__).resolve().parents[1]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--engine',type=Path,required=True)
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--label',required=True)
    ap.add_argument('--rate',type=int,default=96000)
    ap.add_argument('--jobs',type=int,default=6)
    ap.add_argument('--ids',nargs='*')
    ap.add_argument('--stems',action='store_true')
    args=ap.parse_args()
    engine=args.engine.resolve(); source=args.source.resolve()
    data=json.loads((ROOT/'reference/manifest.json').read_text())['samples']
    if args.ids:data=[x for x in data if x['id'] in args.ids]
    out=ROOT/'benchmark'/args.label; out.mkdir(parents=True,exist_ok=True)
    events=ROOT/'benchmark/events';events.mkdir(exist_ok=True)
    source_hash=sha(source);engine_hash=sha(engine)
    calibration=source.parent/'calibration.h'
    calibration_hash=sha(calibration) if calibration.exists() else None
    def render(item):
        name=item['id']; score=events/(name+'.events')
        score.write_text(f"# Matched held note; recording pedal state undocumented.\n0.100000 on {item['midi_note']} {item['model_velocity']}\n4.150000 off {item['midi_note']} 0\n")
        command=[str(engine),'--events',str(score),'--output',str(out/(name+'.wav')),'--sample-rate',str(args.rate),'--duration','4.35','--metrics',str(out/(name+'.json'))]
        if args.stems:command+=['--stem-prefix',str(out/name)]
        proc=subprocess.run(command,capture_output=True,text=True)
        if proc.returncode:raise RuntimeError(f'{name}: {proc.stderr}')
        meta=json.loads(proc.stdout);meta.update(id=name,source_sha256=source_hash,calibration_sha256=calibration_hash,engine_sha256=engine_hash,score_sha256=sha(score),audio_sha256=sha(out/(name+'.wav')))
        (out/(name+'.json')).write_text(json.dumps(meta,indent=2)+'\n')
        print(f"{args.label}: {name}, {meta['wall_seconds']:.1f}s wall",flush=True)
        return meta
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:report=list(pool.map(render,data))
    assert sha(source)==source_hash and sha(engine)==engine_hash,'Source or engine changed during benchmark'
    assert not calibration_hash or sha(calibration)==calibration_hash,'Calibration changed during benchmark'
    (out/'render-manifest.json').write_text(json.dumps({'label':args.label,'source_sha256':source_hash,'calibration_sha256':calibration_hash,'engine_sha256':engine_hash,'solver_rate':args.rate,'held_note_duration':4.05,'pedal':0,'renders':report},indent=2)+'\n')
if __name__=='__main__':main()
