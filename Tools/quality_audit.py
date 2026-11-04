#!/usr/bin/env python3
"""Reproducible public-engine quality observations, with no reference recordings.

Prepare against a source snapshot before running any candidate. The full grid is
exhaustive only over the declared six pianos, 88 keys and 127 integer velocities
at one fixed setting/history/rate. Other continuous controls and event histories
are sampled. Numerical contracts are separated from acoustic outlier rankings:
real pianos need not have identical spectra, stereo, or finite-window decay.

Example (snapshot contains Source/DSP):
  python3 Tools/quality_audit.py prepare --snapshot PATH --out OUT
  python3 OUT/quality_audit.py grid --out OUT --jobs 2
  python3 OUT/quality_audit.py scenes --out OUT --jobs 2
  python3 OUT/quality_audit.py analyze --out OUT
No parameter, reference corpus, or production source is modified.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import csv
from datetime import datetime, timezone
import hashlib
import itertools
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import numpy as np

MODELS = ('grand', 'upright', 'kawai', 'hamburg', 'newyork')
WINDOWS = ((0., .05), (.05, .3), (.3, .75), (.75, 1.5), (1.5, 2.))
DEFAULTS = dict(gain=.07, brightness=.5, resonance=.25, width=.75,
                tuning=440., mechanics=.175, mute=0., sustain=0.,
                sostenuto=0., soft=0., mic=0., stiffness=0., unisons=0., ring=0.)
CEILING = float(np.float32(.84139514)) * (1+1e-6)
POLICY = {
    'hard_contracts': ['all output samples finite',
                       'absolute output <= existing OutputStage ceiling * (1+1e-6)',
                       'selected reset/repeat waveforms byte identical',
                       'every primary-grid note has nonzero output'],
    'diagnostic_only': ['every negative adjacent-velocity RMS step (no tolerance hides it)',
                        'adjacent-pitch steps and local curvature in all reported windows',
                        'spectral balance, stereo, attack rise, derivative and release outliers'],
    'interpretation': 'An outlier is a reproducible listening/structural witness, not proof of a defect. '
                      'No universal level, timbre, stereo, or finite-window monotonicity target is imposed.',
    'comparison': 'Identical frozen controls/operators; no per-case gain, phase, frequency or time fitting. '
                  'Report all paired deltas, including regressions; changes require separate musical/source evidence.',
}


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def utc():
    return datetime.now(timezone.utc).isoformat()


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, np.ndarray):
        return clean(value.tolist())
    if isinstance(value, (float, np.floating)):
        return float(value) if math.isfinite(value) else None
    if isinstance(value, np.integer):
        return int(value)
    return value


def write_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(clean(value), indent=2, allow_nan=False)+'\n')
    temporary.replace(path)


def case(ident, model, note=60, velocity=80, rate=48000, quality=0,
         duration=2., parameters=None, events=None, windows=None, repeat=False,
         family='controls', comparison=None):
    return dict(id=ident, model=model, note=note, velocity=velocity, rate=rate,
                quality=quality, duration=duration, parameters=parameters or {},
                windows=windows or list(WINDOWS), repeat=bool(repeat), family=family,
                comparison=comparison,
                events=events if events is not None else
                [[0., 'on', str(note), velocity, 1], [1.5, 'off', str(note), 0, 1]])


def scene_plan():
    """Predeclared coverage; histories are deterministic, never called RNG seeds."""
    plan = []
    long_windows = [(0, .05), (.05, .3), (.3, 1.5), (1.5, 4), (4, 8), (8, 16)]
    for model in range(6):
        # Long bass/tail coverage at the primary rate; release, hold and pedal-up.
        for note, velocity, history in itertools.product((21, 33, 60, 84, 108), (16, 64, 112),
                                                         ('held', 'released', 'pedal')):
            events = [[0, 'on', str(note), velocity, 1]]
            if history != 'held':
                if history == 'pedal':
                    events.insert(0, [0, 'cc', '64', 127, 1])
                    events.append([8, 'cc', '64', 0, 1])
                events.append([4, 'off', str(note), 0, 1])
            plan.append(case(f'long_{model}_{note}_{velocity}_{history}', model, note, velocity,
                             duration=16, windows=long_windows, events=events, family='long'))
        # Every legal quality mode, three supported host rates and MIDI channels.
        for rate, quality, note in itertools.product((44100, 48000, 96000), range(3), (21, 60, 108)):
            plan.append(case(f'mode_{model}_{rate}_{quality}_{note}', model, note, 80,
                             rate, quality, repeat=note == 60, family='modes'))
        # Native prepare() limits, treated as numerical/stability coverage rather
        # than musically equivalent spectra (8k Nyquist removes high partials).
        for rate, quality, note in itertools.product((8000,192000),range(3),(21,60,108)):
            plan.append(case(f'rate_bound_{model}_{rate}_{quality}_{note}',model,note,80,
                             rate,quality,family='rate_bounds'))
        for channel in range(1, 17):
            plan.append(case(f'channel_{model}_{channel}', model, events=[
                [0, 'on', '60', 80, channel], [1.5, 'off', '60', 0, channel]], family='channels'))
        # Parameter endpoints act on held notes and release; all remain raw engine units.
        bounds = dict(gain=(0., 2.), brightness=(0., 1.), resonance=(0., 1.), width=(0., 1.),
                      tuning=(300., 600.), mechanics=(0., 2.), mute=(0., 1.), sustain=(0., 1.),
                      sostenuto=(0., 1.), soft=(0., 1.), mic=(0., 1.),
                      stiffness=(-1., 1.), unisons=(-1., 1.), ring=(-1., 1.))
        for name, (low, high) in bounds.items():
            for level, value in (('low', low), ('high', high)):
                # Sostenuto must be caught after note-on for meaningful activation.
                pars = {name: value} if name != 'sostenuto' else {}
                events = [[0, 'on', '60', 100, 1], [.9, 'off', '60', 0, 1]]
                if name == 'sostenuto':
                    events.insert(1, [.25, 'p', name, value, 1])
                plan.append(case(f'endpoint_{model}_{name}_{level}', model, velocity=100,
                                 parameters=pars, events=events, comparison=f'endpoint_{model}_{name}',
                                 family='endpoints'))
            for direction, start, stop in (('up', low, high), ('down', high, low)):
                plan.append(case(f'live_{model}_{name}_{direction}', model, velocity=100,
                    duration=3, parameters={name: start}, windows=[(0,.05),(.05,.3),(.3,.75),
                    (.75,1.5),(1.5,2),(2,3)], events=[[0,'on','60',100,1],
                    [.371,'p',name,stop,1],[1.2,'on','67',80,1],[1.7,'off','60',0,1],
                    [2.,'p',name,start,1],[2.3,'off','67',0,1]], family='live'))
        # Complete 2^4 low/high interaction corners for selected coupled public controls.
        for bits in itertools.product((0,1), repeat=4):
            pars = dict(zip(('mic','mechanics','resonance','soft'), bits))
            pars['mechanics'] *= 2
            plan.append(case(f'corner_{model}_{"".join(map(str,bits))}',model,
                             velocity=120, parameters=pars, family='corners'))
        # All six choices for each build part separately, each relative to this piano.
        for part, donor in itertools.product(('strings','hammers','soundboard','action'),range(6)):
            pars = {part+str(i+1): float(i==donor) for i in range(6)}
            plan.append(case(f'build_{model}_{part}_{donor}', model, parameters=pars, family='build'))
        # Explicit state histories, with later deterministic RNG draws/repeated strikes.
        histories = {
            'repetition': [[i*.12, 'on' if j==0 else 'off', '60', 90 if j==0 else 0, 1]
                           for i in range(10) for j in (0,1)],
            'repedal': [[0,'cc','64',127,1],[0,'on','36',100,1],[.4,'off','36',0,1],
                        [.7,'cc','64',0,1],[.74,'cc','64',127,1],[1.5,'cc','64',0,1]],
            'sostenuto': [[0,'on','48',100,1],[.2,'cc','66',127,1],[.3,'on','60',80,1],
                          [.6,'off','48',0,1],[.6,'off','60',0,1],[1.5,'cc','66',0,1]],
            'cc120': [[0,'on','36',110,1],[.5,'cc','120',0,1],[.75,'on','60',80,1]],
            'cc123': [[0,'cc','64',127,1],[0,'on','48',100,1],[.5,'cc','123',0,1],[1.5,'cc','64',0,1]],
            'reset': [[0,'on','36',110,1],[.5,'reset','0',0,1],[.75,'on','60',80,1]],
            'bend': [[0,'on','60',80,1],[.4,'bend','0',2,1],[1.,'bend','0',-2,1],[1.5,'off','60',0,1]],
            'soft_key': [[0,'on','12',127,1],[0,'on','60',100,1],[1.,'off','12',0,1],[1.5,'off','60',0,1]],
            'sustain_key': [[0,'on','14',127,1],[0,'on','48',100,1],[.6,'off','48',0,1],[1.5,'off','14',0,1]],
            'sostenuto_key': [[0,'on','48',100,1],[.2,'on','13',127,1],[.6,'off','48',0,1],[1.5,'off','13',0,1]],
            'half_pedal': [[0,'cc','64',64,1],[0,'on','48',100,1],[.6,'off','48',0,1],[1.5,'cc','64',0,1]],
            'cc121': [[0,'cc','64',127,1],[0,'cc','67',127,1],[0,'on','48',100,1],
                      [.6,'off','48',0,1],[1.,'cc','121',0,1],[1.2,'on','60',80,1]],
            'modwheel': [[0,'on','60',80,1],[.4,'cc','1',127,1],[1.,'cc','1',0,1],[1.5,'off','60',0,1]],
        }
        # The repeated strike is held 65ms rather than paired on/off at one sample.
        histories['repetition'] = [event for i in range(10) for event in
            [[i*.12,'on','60',90,1],[i*.12+.065,'off','60',0,1]]]
        for name, events in histories.items():
            plan.append(case(f'history_{model}_{name}', model, events=events,
                             repeat=True, family='history'))
    # All 6^4 categorical BUILD combinations, bounded C4/80 scene, not continuous mix coverage.
    for choices in itertools.product(range(6), repeat=4):
        pars = {part+str(i+1):float(i==donor)
                for part,donor in zip(('strings','hammers','soundboard','action'),choices)
                for i in range(6)}
        plan.append(case('build_all_'+''.join(map(str,choices)),0,
                         parameters=pars,family='build_cartesian'))
    assert len({c['id'] for c in plan}) == len(plan)
    return plan


def case_text(cases):
    out = ['# quality-audit v1; times are latency-compensated output/event times']
    for c in cases:
        out.append('case {id} {model} {note} {velocity} {rate} {quality} {duration:.17g} {r}'.format(
            **c, r=int(c['repeat'])))
        for name, value in c['parameters'].items():
            out.append(f'p {name} {value:.17g}')
        for begin, end in c['windows']:
            out.append(f'w {begin:.17g} {end:.17g}')
        for t, kind, a, b, channel in c['events']:
            out.append(f'e {t:.17g} {kind} {a} {b:.17g} {channel}')
        out.append('end')
    return '\n'.join(out)+'\n'


def protocol():
    plan = scene_plan()
    return dict(version=1, models=MODELS, defaults=DEFAULTS, quality='full',
        grid=dict(notes=[21,108], velocities=[1,127], cases=6*88*127, rate=48000,
                  duration=2., release=1.5, windows=WINDOWS),
        initial_state='setParameters then reset, normal playing response, RNG reset value 1; '
                      'same first strike draw per grid cell; no invented independent seeds',
        timing='Note-on at frame0, output latency discarded exactly once. No extra2ms shift. '
               'This reset-initialized probe differs intentionally from Tools/render.cpp initialization.',
        spectrum='Real symmetric Hann-window power; radix2 zero padding only refines bin grid. '
                 'One-sided stereo-mean energy with Parseval normalization. Relative bands use '
                 'equal-tempered nominal f0 at current initial tuning, not inferred pitch.',
        rise='Causal5ms power average;10/90% amplitude thresholds of maximum in first150ms; '
             'diagnostic only, window-edge flag retained; not fitted hammer contact duration.',
        availability='Zero-energy denominators are unavailable (null), never floor-filled. '
                     'Very quiet late-window ratios can be unstable; raw powers retained.',
        policy=POLICY, scene_count=len(plan),
        scene_families={name:sum(c['family']==name for c in plan) for name in sorted({c['family'] for c in plan})},
        limits='Discrete grid only at one rate/quality/controls/history. Long, live, quality/rate, '
               'categorical build and MIDI coverage are separate finite panels. No source audio, '
               'TRAIN/DEV/SEALED fitting or piano-identity homogenization.')


def prepare(args):
    out, snapshot = args.out.resolve(), args.snapshot.resolve()
    out.mkdir(parents=True, exist_ok=True)
    if (out/'harness-freeze.json').exists():
        raise RuntimeError('Already frozen; use a new output directory')
    root = Path(__file__).resolve().parent
    for name in ('quality_audit.py','quality_probe.cpp'):
        target = out/name
        if (root/name).resolve()!=target:
            shutil.copyfile(root/name,target)
    source = {str(p.relative_to(snapshot)):sha(p) for p in sorted((snapshot/'Source/DSP').glob('*')) if p.is_file()}
    if not source or 'Source/DSP/KeyraEngine.cpp' not in source:
        raise RuntimeError('Expected frozen Source/DSP tree')
    plan = scene_plan()
    write_json(out/'protocol.json',protocol()); write_json(out/'scene-plan.json',plan)
    specs = out/'scene-specs'; specs.mkdir(exist_ok=True)
    for model in range(6):
        selected = [c for c in plan if c['model']==model]
        (specs/f'{MODELS[model]}.txt').write_text(case_text(selected))
    command = [os.environ.get('CXX','c++'),'-std=c++17','-O3','-DNDEBUG','-Wall','-Wextra','-pedantic',
               '-I',str(snapshot/'Source'),str(out/'quality_probe.cpp'),
               str(snapshot/'Source/DSP/KeyraEngine.cpp'),'-o',str(out/'quality_probe')]
    started=time.monotonic(); build=subprocess.run(command,capture_output=True,text=True)
    (out/'build.log').write_text(build.stdout+build.stderr)
    if build.returncode:
        raise RuntimeError('Probe build failed; see build.log')
    pins = {str(p.relative_to(out)):sha(p) for p in [out/'quality_audit.py',out/'quality_probe.cpp',
             out/'quality_probe',out/'protocol.json',out/'scene-plan.json',*sorted(specs.glob('*.txt'))]}
    write_json(out/'harness-freeze.json',dict(frozen_utc=utc(),source_snapshot=str(snapshot),
               source_sha256=source,pins=pins,build_command=command,build_seconds=time.monotonic()-started,
               compiler=subprocess.check_output([command[0],'--version'],text=True).splitlines()[0]))
    print('FROZEN',out/'harness-freeze.json',sha(out/'harness-freeze.json'),flush=True)


def verify(out):
    frozen=json.loads((out/'harness-freeze.json').read_text())
    for rel, digest in frozen['pins'].items():
        if sha(out/rel)!=digest:
            raise RuntimeError('Frozen harness input changed: '+rel)
    for rel,digest in frozen['source_sha256'].items():
        if sha(Path(frozen['source_snapshot'])/rel)!=digest:
            raise RuntimeError('Frozen engine input changed: '+rel)
    return frozen


def run_task(out, name, command, expected):
    receipt=out/(name+'.receipt.json')
    if receipt.exists():
        old=json.loads(receipt.read_text())
        if old['command']!=command or old['freeze_sha256']!=sha(out/'harness-freeze.json'):
            raise RuntimeError('Resume identity differs: '+name)
        if sha(Path(old['csv']))!=old['csv_sha256']:
            raise RuntimeError('Completed result changed: '+name)
        if old.get('returncode')!=0 or old.get('cases')!=expected or old.get('expected_cases')!=expected:
            raise RuntimeError('Prior task failed or is incomplete; preserve its receipt and use a new run directory: '+name)
        return old
    csv_path=Path(command[3]); csv_path.parent.mkdir(parents=True,exist_ok=True)
    t=time.monotonic()
    with (out/(name+'.log')).open('w') as log:
        result=subprocess.run(command,stdout=log,stderr=log)
    with csv_path.open() as f:
        count=sum(1 for _ in f)-1
    verify(out)
    data=dict(command=command,returncode=result.returncode,elapsed_seconds=time.monotonic()-t,
              cases=count,expected_cases=expected,csv=str(csv_path),csv_sha256=sha(csv_path),
              freeze_sha256=sha(out/'harness-freeze.json'),finished_utc=utc())
    write_json(receipt,data)
    print(name,'cases',count,'seconds',round(data['elapsed_seconds'],2),'returncode',result.returncode,flush=True)
    if result.returncode or count!=expected:
        raise RuntimeError('Numerical contract or coverage failure: '+name)
    return data


def run(args):
    out=args.out.resolve();verify(out)
    tasks=[]
    for model in range(6):
        if args.model is not None and model!=args.model:
            continue
        name=f'{args.action}-{MODELS[model]}'
        if args.action=='grid':
            low,high=(args.pilot_note,args.pilot_note) if args.pilot_note is not None else (21,108)
            if args.pilot_note is not None:
                name+=f'-pilot{low}'
            cmd=[str(out/'quality_probe'),'--grid',str(model),str(out/'results'/(name+'.csv')),
                 str(low),str(high),'1','127','2','1.5']
            count=(high-low+1)*127
        else:
            cmd=[str(out/'quality_probe'),'--cases',str(out/'scene-specs'/f'{MODELS[model]}.txt'),
                 str(out/'results'/(name+'.csv'))]
            count=sum(c['model']==model for c in json.loads((out/'scene-plan.json').read_text()))
        tasks.append((name,cmd,count))
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures=[pool.submit(run_task,out,*t) for t in tasks]
        results=[future.result() for future in as_completed(futures)]
    suffix=f'-pilot{args.pilot_note}' if args.action=='grid' and args.pilot_note is not None else ''
    write_json(out/(args.action+suffix+'-manifest.json'),dict(results=results,
               freeze_sha256=sha(out/'harness-freeze.json'),finished_utc=utc()))


def db(power):
    power=np.asarray(power,dtype=float)
    with np.errstate(divide='ignore',invalid='ignore'):
        return np.where(power>0,10*np.log10(power),np.nan)


def divide(numerator,denominator):
    with np.errstate(divide='ignore',invalid='ignore'):
        return np.where(np.asarray(denominator)>0,np.asarray(numerator)/denominator,np.nan)


def load_csv(path):
    with Path(path).open(newline='') as f:
        reader=csv.reader(f); names=next(reader); rows=list(reader)
    if any(len(r)!=len(names) for r in rows):
        raise RuntimeError('Malformed CSV column count: '+str(path))
    text={name:[r[i] for r in rows] for i,name in enumerate(names) if name in ('case_id','hash_fnv1a64')}
    columns={name:np.array([float(r[i]) for r in rows]) for i,name in enumerate(names)
             if name not in text}
    return text,columns


def metrics(columns):
    result={name:columns[name] for name in ('model','note','velocity','rate','quality','whole_bad','whole_peak','repeat_equal')}
    result['rise_ms']=np.where((columns['rise10_frame']>=0)&(columns['rise90_frame']>=0),
        1000*(columns['rise90_frame']-columns['rise10_frame'])/columns['rate'],np.nan)
    for w in range(6):
        get=lambda name:columns[f'w{w}_{name}']
        prefix=f'w{w}_';total=get('ll')+get('rr'); power=divide(total,2*get('n'))
        result[prefix+'rms_db']=db(power)
        result[prefix+'ild_db']=db(get('ll'))-db(get('rr'))
        mid=np.maximum(0,total+2*get('lr'));side=np.maximum(0,total-2*get('lr'))
        result[prefix+'side_mid_db']=db(side)-db(mid)
        result[prefix+'correlation']=divide(get('lr'),np.sqrt(get('ll')*get('rr')))
        result[prefix+'centroid_f0']=divide(get('spectral_hz_power'),get('spectral_power')*columns['f0'])
        result[prefix+'high4k_fraction']=divide(get('above4000'),get('spectral_power'))
        result[prefix+'band500_1000_fraction']=divide(get('band500_1000'),get('spectral_power'))
        result[prefix+'crest_db']=db(get('peak')**2)-db(power)
        result[prefix+'maxjump_relative_rms']=divide(get('jump'),np.sqrt(power))
        result[prefix+'jump_frame']=get('jump_frame')
        result[prefix+'stereo_power']=power
    return result


def rank_differences(values, rows, axis, limit=12):
    """Signed transitions; adjacent integer keys/velocities only, no smoothing."""
    order=np.lexsort((rows['velocity'],rows['note'],rows['model']))
    values=values[order]; model=rows['model'][order];note=rows['note'][order];velocity=rows['velocity'][order]
    lookup={(int(m),int(n),int(v)):i for i,(m,n,v) in enumerate(zip(model,note,velocity))}
    pairs=[]
    for key,i in lookup.items():
        target=(key[0],key[1]+(axis=='note'),key[2]+(axis=='velocity'))
        j=lookup.get(target)
        if j is not None and np.isfinite(values[i]) and np.isfinite(values[j]):
            pairs.append((float(values[j]-values[i]),key,target))
    ranked=sorted(pairs,key=lambda x:abs(x[0]),reverse=True)
    neg=sorted((p for p in pairs if p[0]<0),key=lambda x:x[0])
    return dict(available_pairs=len(pairs),negative_count=len(neg),
                negative_larger_than_0_1_metric_units=sum(p[0]<-.1 for p in pairs),
                largest_absolute=ranked[:limit],most_negative=neg[:limit])


def summarize(text,cols):
    m=metrics(cols); n=len(text['case_id']); peaks=cols['whole_peak']
    hard=dict(finite=bool(np.all(cols['whole_bad']==0)),output_ceiling=bool(np.all(peaks<=CEILING)),
              repeats=bool(np.all(cols['repeat_equal']!=0)))
    primary=np.array([x.startswith('g_') for x in text['case_id']])
    hard['primary_nonzero']=bool(np.all(peaks[primary]>0))
    diagnostics={}
    for w in range(5):
        for name in ('rms_db','ild_db','side_mid_db','centroid_f0','high4k_fraction','band500_1000_fraction'):
            metric=f'w{w}_{name}'
            diagnostics[metric]={axis:rank_differences(m[metric][primary],
                {k:v[primary] for k,v in m.items()},axis) for axis in ('velocity','note')}
            # Curvature isolates isolated keys from smooth register trends, not piano voicing truth.
            if name=='rms_db':
                lookup={(int(a),int(b),int(c)):float(v) for a,b,c,v in zip(m['model'][primary],m['note'][primary],m['velocity'][primary],m[metric][primary])}
                curvature=[]
                for (model,note,velocity),v in lookup.items():
                    a=lookup.get((model,note-1,velocity));b=lookup.get((model,note+1,velocity))
                    if a is not None and b is not None and all(map(math.isfinite,(a,b,v))):
                        curvature.append((v-(a+b)/2,(model,note,velocity)))
                diagnostics[metric]['pitch_curvature']=sorted(curvature,key=lambda x:abs(x[0]),reverse=True)[:12]
    registers={}
    # Same absolute output gain, native note/velocity coordinates. These summarize
    # character and calibration coverage; they do not force pianos to a shared EQ.
    for model,name in enumerate(MODELS):
        registers[name]={}
        for label,lo,hi in (('bass',21,47),('middle',48,71),('upper',72,95),('top',96,108)):
            curves=[]
            for velocity in range(1,128):
                mask=primary&(m['model']==model)&(m['note']>=lo)&(m['note']<=hi)&(m['velocity']==velocity)
                if not np.any(mask):continue
                row=dict(velocity=velocity,notes=int(np.sum(mask)),metrics={})
                for field in ('w0_rms_db','w1_rms_db','w2_rms_db','w3_rms_db','w4_rms_db',
                              'w1_centroid_f0','w1_high4k_fraction','w1_side_mid_db','w1_ild_db','rise_ms'):
                    finite=m[field][mask];finite=finite[np.isfinite(finite)]
                    row['metrics'][field]=dict(available=len(finite),quantiles=np.quantile(finite,[.1,.5,.9]) if len(finite) else [])
                curves.append(row)
            registers[name][label]=dict(note_range=[lo,hi],velocity_curves=curves)
    return dict(cases=n,hard_contracts=hard,hard_pass=all(hard.values()),maximum_peak=float(np.max(peaks)),
                policy=POLICY,diagnostics=diagnostics,registers=registers),m


def analyze(args):
    out=args.out.resolve();verify(out)
    files=sorted((out/'results').glob('*.csv'))
    if not files:
        raise RuntimeError('No results')
    # Pilot data is separate, never counted twice in the main grid.
    files=[p for p in files if '-pilot' not in p.name]
    text={'case_id':[],'hash_fnv1a64':[]}; columns={};pins={}
    for path in files:
        receipt=json.loads((out/(path.stem+'.receipt.json')).read_text())
        if (Path(receipt['csv']).resolve()!=path.resolve() or receipt['csv_sha256']!=sha(path)
                or receipt['freeze_sha256']!=sha(out/'harness-freeze.json')):
            raise RuntimeError('CSV does not match completed native receipt: '+str(path))
        t,c=load_csv(path);pins[str(path.relative_to(out))]=sha(path)
        if len(t['case_id'])!=receipt['cases']:
            raise RuntimeError('CSV row count differs from receipt: '+str(path))
        for k,v in t.items():text[k].extend(v)
        for k,v in c.items():columns.setdefault(k,[]).append(v)
    columns={k:np.concatenate(v) for k,v in columns.items()}
    if len(set(text['case_id']))!=len(text['case_id']):
        raise RuntimeError('Duplicate observations')
    summary,m=summarize(text,columns)
    plan=json.loads((out/'scene-plan.json').read_text()); lookup={v:i for i,v in enumerate(text['case_id'])}
    activation=[]
    for c in plan:
        if c['comparison'] and c['id'].endswith('_low'):
            other=c['id'][:-4]+'_high'
            if c['id'] in lookup and other in lookup:
                i,j=lookup[c['id']],lookup[other]
                activation.append(dict(low=c['id'],high=other,exact_output_different=text['hash_fnv1a64'][i]!=text['hash_fnv1a64'][j],
                    low_silent=bool(m['whole_peak'][i]==0),high_silent=bool(m['whole_peak'][j]==0),
                    window_rms_delta_db=[m[f'w{w}_rms_db'][j]-m[f'w{w}_rms_db'][i] for w in range(5)],
                    caveat='Different output proves this sampled context activates the control; unchanged output may be context-dependent.'))
    summary.update(finished_utc=utc(),freeze_sha256=sha(out/'harness-freeze.json'),csv_sha256=pins,
                   analysis_source=str(Path(__file__).resolve()),analysis_source_sha256=sha(__file__),
                   expected_grid_cases=67056,observed_grid_cases=sum(s.startswith('g_') for s in text['case_id']),
                   expected_scene_cases=len(plan),observed_scene_cases=sum(not s.startswith('g_') for s in text['case_id']),
                   control_activation=activation)
    gain_zero=[lookup[c['id']] for c in plan if c['id'] in lookup and c['id'].endswith('_gain_low')]
    summary['hard_contracts']['sampled_gain_zero_silent']=bool(np.all(m['whole_peak'][gain_zero]==0))
    summary['hard_contracts']['complete_declared_coverage']=(summary['observed_grid_cases']==67056
                                                           and summary['observed_scene_cases']==len(plan))
    summary['hard_pass']=all(summary['hard_contracts'].values())
    np.savez_compressed(out/'metrics.npz',case_id=np.array(text['case_id']),hash_fnv1a64=np.array(text['hash_fnv1a64']),**m)
    summary['metrics_sha256']=sha(out/'metrics.npz');write_json(out/'summary.json',summary)
    lines=['# Public-engine quality observations','',f"Cases: {summary['cases']}; grid {summary['observed_grid_cases']}/67056; scenes {summary['observed_scene_cases']}/{len(plan)}.",
           f"Numerical contracts: {summary['hard_contracts']}. Peak {summary['maximum_peak']:.9g}.",'',
           'Acoustic rankings are diagnostic witnesses; natural piano differences are retained. No recording or held-out source was used.','']
    for w in range(5):
        d=summary['diagnostics'][f'w{w}_rms_db']
        lines.append(f"Window {WINDOWS[w]}: worst velocity drops {d['velocity']['most_negative'][:3]}; pitch curvature {d['pitch_curvature'][:3]}.")
    (out/'report.md').write_text('\n'.join(lines)+'\n')
    print(out/'summary.json',summary['hard_pass'],flush=True)
    if not summary['hard_pass']:
        raise RuntimeError('Observed numerical contract failure; retained all results')


def compare(args):
    a,b=args.baseline.resolve(),args.candidate.resolve()
    fa,fb=verify(a),verify(b)
    if fa['pins']['quality_probe.cpp']!=fb['pins']['quality_probe.cpp']:
        raise RuntimeError('Comparison observation operators differ')
    if (a/'protocol.json').read_bytes()!=(b/'protocol.json').read_bytes():
        raise RuntimeError('Comparison protocols differ')
    x,y=np.load(a/'metrics.npz'),np.load(b/'metrics.npz')
    if set(x.files)!=set(y.files) or set(x['case_id'])!=set(y['case_id']):
        raise RuntimeError('Comparison coverage differs')
    ix=np.argsort(x['case_id']);iy=np.argsort(y['case_id']);ids=x['case_id'][ix]
    result=dict(baseline=str(a),candidate=str(b),cases=len(ids),
                baseline_metrics_sha256=sha(a/'metrics.npz'),candidate_metrics_sha256=sha(b/'metrics.npz'),
                exact_waveform_hash_count=int(np.sum(x['hash_fnv1a64'][ix]==y['hash_fnv1a64'][iy])),
                diagnostic_only='Signed paired changes are not automatically improvements or regressions in piano character.',metrics={})
    for name in x.files:
        if name in ('case_id','hash_fnv1a64'):continue
        old,new=x[name][ix],y[name][iy];common=np.isfinite(old)&np.isfinite(new);delta=new-old
        order=np.argsort(np.where(common,np.abs(delta),-1))[::-1][:20]
        result['metrics'][name]=dict(common=int(common.sum()),availability_changes=int(np.sum(np.isfinite(old)!=np.isfinite(new))),
            changed=int(np.sum(common&(delta!=0))),median_delta=float(np.median(delta[common])) if np.any(common) else None,
            largest=[dict(case=str(ids[i]),baseline=old[i],candidate=new[i],delta=delta[i]) for i in order if common[i]])
    write_json(args.output,result);print(args.output)


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='action',required=True)
    q=sub.add_parser('prepare');q.add_argument('--snapshot',type=Path,required=True);q.add_argument('--out',type=Path,required=True)
    for name in ('grid','scenes'):
        q=sub.add_parser(name);q.add_argument('--out',type=Path,required=True);q.add_argument('--jobs',type=int,choices=(1,2),default=2)
        q.add_argument('--model',type=int,choices=range(6));q.add_argument('--pilot-note',type=int,choices=range(21,109))
    q=sub.add_parser('analyze');q.add_argument('--out',type=Path,required=True)
    q=sub.add_parser('compare');q.add_argument('--baseline',type=Path,required=True);q.add_argument('--candidate',type=Path,required=True);q.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    if args.action=='prepare':prepare(args)
    elif args.action in ('grid','scenes'):run(args)
    elif args.action=='analyze':analyze(args)
    else:compare(args)


if __name__=='__main__':
    main()
