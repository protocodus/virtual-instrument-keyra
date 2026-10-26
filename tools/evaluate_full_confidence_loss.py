#!/usr/bin/env python3
"""Resume the frozen confidence-loss historical batch and score all regressions.

The numerical candidate and historical protocol were frozen before this recovery
runner was written. This runner does not fit parameters, acquire recordings or
claim fresh validation. It preserves and authenticates completed predictions.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'out/full-confidence-loss/historical'
sys.path.insert(0, str(ROOT/'tools'))
import evaluate_full_candidate as evaluation
import probe_full_inverse_loss as loss


def read(path): return json.loads(Path(path).read_text())
def write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def record(path): return {'path':str(Path(path).resolve()), 'sha256':sha(path)}
def now(): return datetime.now(timezone.utc).isoformat()
def verify(records):
    for row in records:
        if sha(row['path']) != row['sha256']:
            raise ValueError('Frozen input changed: '+row['path'])
def locked():
    protocol=read(OUT/'freeze.json')
    verify(protocol['inputs']); verify([protocol['candidate_freeze']])
    candidate=read(protocol['candidate_freeze']['path'])
    verify([candidate[k] for k in ('profile','source','header','binary','protocol','training_report','train_predictions')])
    if protocol['fresh_cases'] or not protocol['all_references_previously_observed']:
        raise ValueError('Runner supports the frozen historical-only batch')
    return protocol,candidate


def predictions():
    protocol,candidate=locked()
    recovery=OUT/'recovery-runner.json'
    receipt={'runner':record(__file__), 'protocol':record(OUT/'freeze.json'),
             'candidate_freeze':protocol['candidate_freeze'],
             'scope':'Recovery runner written after the frozen protocol and partial predictions; no protocol/candidate change.',
             'completed_before_recovery':[record(p) for p in sorted((OUT/'predictions').glob('*.json'))]}
    if recovery.exists():
        old=read(recovery)
        verify([old['runner'],old['protocol'],old['candidate_freeze']]);verify(old['completed_before_recovery'])
    else:write(recovery,{**receipt,'started_at_utc':now()})
    def one(row):
        folder=OUT/'predictions'; folder.mkdir(exist_ok=True)
        events=folder/(row['id']+'.events');audio=folder/(row['id']+'.wav');sidecar=folder/(row['id']+'.json')
        text=(f"# Frozen historical prediction; recording acquisition pedal unknown.\n"
              f"0.100000 on {row['midi']} {row['midi_velocity']}\n4.150000 off {row['midi']} 0\n")
        if events.exists() and events.read_text()!=text:raise ValueError('Frozen event changed')
        if not events.exists():events.write_text(text)
        command=[candidate['binary']['path'],'--events',str(events),'--output',str(audio),
                 '--sample-rate','48000','--duration','3.8']
        if sidecar.exists():
            old=read(sidecar);verify([old['events'],*old['outputs'],old['candidate_freeze']])
            if old['command']!=command or old['id']!=row['id']:raise ValueError('Cached prediction differs')
            return old
        if audio.exists():raise ValueError('Unreceipted prediction must be inspected: '+str(audio))
        call=subprocess.run(command,check=True,capture_output=True,text=True)
        metrics=json.loads(call.stdout)
        if metrics['nonfinite_samples'] or metrics['string_count']!=230 or metrics['board_modes']!=475:
            raise ValueError('Invalid full prediction')
        result={'id':row['id'],'variant':'confidence_loss','role':'historical_observed',
                'candidate_freeze':protocol['candidate_freeze'],'command':command,
                'events':record(events),'outputs':[record(audio)],'metrics':metrics}
        write(sidecar,result); print(row['id']+' prediction complete',flush=True)
        return result
    with ThreadPoolExecutor(max_workers=protocol['protocol']['maximum_concurrent_renders']) as pool:
        rows=list(pool.map(one,protocol['cases']))
    locked()
    write(OUT/'predictions.json',{'completed_at_utc':now(),'freeze':record(OUT/'freeze.json'),
          'recovery_runner':record(recovery),'renders':rows,
          'all_references_previously_observed':True,'fresh_validation':False})


def restricted(value, ids):
    return {k:[r for r in value[k] if r['id'] in ids] for k in ('comparison','attack_texture')}


def comparison(base,candidate,ids):
    a,b=restricted(base,ids),restricted(candidate,ids)
    report=evaluation.compare_report(a,b)
    aa,bb=loss.attack_by_case(a),loss.attack_by_case(b)
    report['attack_5_100ms_case_mean_mae_db']={
        'baseline_mean':float(np.mean([aa[i] for i in ids])),
        'candidate_mean':float(np.mean([bb[i] for i in ids])),
        'mean_change':float(np.mean([bb[i]-aa[i] for i in ids])),
        'cases':[{'id':i,'baseline':aa[i],'candidate':bb[i],'change':bb[i]-aa[i]} for i in ids]}
    return report


def score():
    protocol,candidate=locked();predictions_receipt=read(OUT/'predictions.json')
    verify([predictions_receipt['freeze'],predictions_receipt['recovery_runner']])
    if (OUT/'results.json').exists():raise ValueError('Historical score already exists; use verify')
    cached=evaluation.read(ROOT/'out/full-calibration/v4/evaluation/results.json')
    refs={r['id']:r for r in read(ROOT/'out/full-calibration/v4/evaluation/reference-features.json')['samples']}
    predicted={r['id']:r for r in predictions_receipt['renders']}
    expected={r['id'] for r in protocol['cases']}
    if set(predicted)!=expected:raise ValueError('Historical prediction inventory differs')
    opening=OUT/'scoring-started.json'
    if opening.exists():raise ValueError('Interrupted historical scoring; inspect before restarting')
    write(opening,{'started_at_utc':now(),'freeze':record(OUT/'freeze.json'),
                   'predictions':record(OUT/'predictions.json'),'runner':record(__file__)})
    models=[];comparisons=[];attacks=[];components=[]
    for row in protocol['cases']:
        ref=refs[row['id']];pred=predicted[row['id']]
        verify([row['reference']['wav'],row['reference']['flac'],pred['events'],*pred['outputs']])
        if ref['sha256']!=row['reference']['wav']['sha256']:
            raise ValueError('Reference feature/audio receipt differs')
        model,comp,attack,component=evaluation.measure_pair(ref,Path(pred['outputs'][0]['path']))
        models.append(model);comparisons.append(comp);attacks.append(attack);components+=component
        print(row['id']+' historical comparison scored',flush=True)
    result_variant={'comparison':comparisons,'attack_texture':attacks,
                    'unassigned_component_comparison':components,
                    'spurious_model_band_diagnostic':{
                       'case_count_with_flags':sum(bool(r['spurious_prominent_model_bands']) for r in comparisons),
                       'flagged_window_band_pairs':sum(len(r['spurious_prominent_model_bands']) for r in comparisons)}}
    groups={'all_historical':[r['id'] for r in protocol['cases']],**protocol['groups']}
    variants={'original_control':cached['variants']['control'],'v4':cached['variants']['candidate']}
    summaries={name:{group:comparison(base,result_variant,ids) for group,ids in groups.items()}
               for name,base in variants.items()}
    report={'schema_version':1,'scored_at_utc':now(),'freeze':record(OUT/'freeze.json'),
            'candidate_freeze':protocol['candidate_freeze'],'predictions':record(OUT/'predictions.json'),
            'runner':record(__file__),'scoring_started':record(opening),
            'reference_features':record(ROOT/'out/full-calibration/v4/evaluation/reference-features.json'),
            'cached_baselines':record(ROOT/'out/full-calibration/v4/evaluation/results.json'),
            'all_references_previously_observed':True,'fresh_cases':[],
            'comparison_to_baselines':summaries,'variant':result_variant,
            'default_promoted':False,'evaluation_used_for_fitting':False,
            'interpretation':'Frozen historical regression after ALL-TRAIN fit. Every regression retained; no fresh or independent validation.',
            'limits':['One piano and recording chain with unknown hammer speed, pedal and room.',
                      'Recording-agreement metrics are not perceptual scores or a realtime benchmark.',
                      'The unassigned C8 component remains explicit and is not generated by this loss adjustment.']}
    locked();write(OUT/'model-features.json',{'samples':models});write(OUT/'results.json',report)
    write(ROOT/'Validation/full-confidence-loss-historical.json',report)
    for name in variants:
        summary=summaries[name]['all_historical']
        print(name, json.dumps({k:{j:v for j,v in summary[k].items() if j!='cases'} for k in
                               ('harmonic_level_mae_db','envelope_mae_db','attack_5_100ms_case_mean_mae_db')}),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=('predictions','score','verify'))
    args=parser.parse_args()
    if args.stage=='predictions':predictions()
    elif args.stage=='score':score()
    else:
        locked()
        for p in ('predictions.json','results.json'):
            if (OUT/p).exists():
                d=read(OUT/p)
                if 'renders' in d:
                    for row in d['renders']:verify([row['events'],*row['outputs'],row['candidate_freeze']])
                else:verify([d[k] for k in ('freeze','candidate_freeze','predictions','runner','scoring_started','reference_features','cached_baselines')])
        print('Frozen protocol, candidate and available predictions/results verified')


if __name__=='__main__':main()
