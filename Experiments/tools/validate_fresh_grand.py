#!/usr/bin/env python3
"""Evaluate the seven newly reserved grand cases after a candidate is frozen.

This never fits, changes the split, or overwrites the historical benchmark.
Run once model choices have been made from training data; later runs of these
same cases are regression checks, not fresh model-selection evidence.
"""
import argparse
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'References/GrandExpanded'
spec=importlib.util.spec_from_file_location('keyra_fresh_benchmark',ROOT/'Research/GrandPianoV2/tools/benchmark.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
spec=importlib.util.spec_from_file_location('keyra_pcm_verify',ROOT/'Research/GrandPianoV2/reference/fetch_reference.py')
verify=importlib.util.module_from_spec(spec);spec.loader.exec_module(verify)


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def summary(rows):
    return b.aggregate([{**row,'split':'heldout_velocity'} for row in rows])['heldout_velocity']


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--baseline-renderer',type=Path,default=ROOT/'out/five-anchor-baseline/keyra_render')
    p.add_argument('--candidate-renderer',type=Path,default=ROOT/'build/keyra_preview_render')
    p.add_argument('--freeze',type=Path,required=True,help='Training-selected candidate freeze manifest with renderer SHA256')
    p.add_argument('--evaluate-reserved',action='store_true',help='Explicitly open the previously reserved evaluation cases')
    p.add_argument('--output',type=Path,default=ROOT/'Validation/fresh-grand.json')
    a=p.parse_args()
    if not a.evaluate_reserved:p.error('Use --evaluate-reserved only after training-only candidate selection and freeze')
    frozen=json.loads(a.freeze.read_text())
    if frozen['renderer_sha256']!=sha(a.candidate_renderer):raise ValueError('Candidate renderer changed after freeze')
    if frozen['calibration_sha256']!=sha(ROOT/'src/LiveCalibration.h'):raise ValueError('Candidate calibration changed after freeze')
    split_path=DATA/'split.json';split=json.loads(split_path.read_text())
    if sha(split_path)!=frozen['split_sha256']:raise ValueError('Evaluation split differs from freeze')
    if not split['locked_before_new_downloads_and_feature_extraction']:raise ValueError('Split was not locked')
    manifest_path=DATA/'manifest.json';manifest=json.loads(manifest_path.read_text())
    if manifest['split_sha256']!=sha(split_path):raise ValueError('Manifest split mismatch')
    reserved=split['fresh_validation_ids']
    if set(reserved)&set(frozen['training_ids']):raise ValueError('Reserved evaluation case was used in fitting')
    reference_features=[];rows={'baseline':[],'candidate':[]};render_features={'baseline':[],'candidate':[]}
    commands=[]
    for name in reserved:
        item=next(row for row in manifest['samples'] if row['id']==name)
        path=DATA/item['wav_path'];verify.verify_wav(item,path)
        reference=b.extract_features(path,item['midi'])
        reference['split']='fresh_pitch' if name.startswith('A3v') else 'fresh_velocity'
        reference['path']=str(path.relative_to(ROOT));reference_features.append(reference)
        for label,executable in [('baseline',a.baseline_renderer),('candidate',a.candidate_renderer)]:
            folder=ROOT/'out/fresh-grand'/label;folder.mkdir(parents=True,exist_ok=True)
            output=folder/(name+'.wav')
            command=[str(executable.resolve()),'--output',str(output),'--rate','48000','--seconds','4.25',
                     '--note',str(item['midi']),'--velocity',str(item['midi_velocity']),
                     '--param','noise=0','--param','distance=0','--param','resonance=0','--param','mic=0']
            subprocess.run(command,check=True,stdout=subprocess.DEVNULL);commands.append(command)
            feature=b.extract_features(output,item['midi']);feature['path']=str(output.relative_to(ROOT))
            comparison=b.compare_features(reference,feature)
            rows[label].append(comparison);render_features[label].append(feature)
        print(name,*(f"{label}: harmonics={rows[label][-1]['harmonic_level_mae_db']:.2f}dB" for label in rows),flush=True)
    metric_keys=('harmonic_level_mae_db','log_band_mae_db','partial_decay_slope_mae_db_per_second','attack_rise10_90_error_ms','envelope_mae_db')
    deltas=[]
    for before,after in zip(rows['baseline'],rows['candidate']):
        deltas.append({'id':before['id'],'split':before['split'],'candidate_minus_baseline_error':
            {key:after[key]-before[key] if after[key] is not None and before[key] is not None else None for key in metric_keys}})
    result={'schema_version':1,'selection':'Candidate frozen from training-only choices before opening these seven reserved recordings.',
            'split_sha256':sha(split_path),'manifest_sha256':sha(manifest_path),'freeze':frozen,'freeze_sha256':sha(a.freeze),
            'baseline_renderer_sha256':sha(a.baseline_renderer),'candidate_renderer_sha256':sha(a.candidate_renderer),
            'analysis':b.ANALYSIS,'commands':commands,'references':reference_features,'models':render_features,'cases':rows,
            'all_fresh':{label:summary(value) for label,value in rows.items()},
            'fresh_pitch':{label:summary([r for r in value if r['split']=='fresh_pitch']) for label,value in rows.items()},
            'fresh_velocity':{label:summary([r for r in value if r['split']=='fresh_velocity']) for label,value in rows.items()},
            'regressions_and_improvements':deltas,
            'limits':'Seven cases from the same piano/microphone collection. Model velocities are upstream SFZ-bin proxies. One scalar RMS match does not validate dynamics or perceptual realism. No claim of acoustic parity; later reuse is regression testing.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result['all_fresh'],indent=2))


if __name__=='__main__':main()
