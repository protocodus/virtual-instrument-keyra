#!/usr/bin/env python3
"""One separately registered confidence-prior fit on all locked TRAIN34.

Keeps the negative global-loss study immutable. Supported anchors receive the
already selected0.6 common-unison-excess correction; weak/ambiguous anchors keep
the original prior. Every coupled prediction is rendered again. No evaluation
data or pedal-condition result is used to construct the confidence mask.
"""
from __future__ import annotations
import argparse
import copy
from datetime import datetime,timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
REFERENCE=ROOT/'References/GrandFullRange/combined_train_features.json'
SPLIT=ROOT/'References/GrandFullRange/split.json'
BASE=ROOT/'out/full-calibration/v4/radiation'
BASE_RENDERS=ROOT/'out/full-calibration/v4/final-renders'
BASE_SCORE=ROOT/'out/full-calibration/v4/final-score'
CONTROL_RENDERS=ROOT/'out/full-calibration/v3/control-renders'
CONTROL_SCORE=ROOT/'out/full-calibration/v4/control-score'
POLICY={'supported_excess_scale':.6,'prior_excess_scale':1.,
        'minimum_distinct_early_decay_partial_orders':4,'prominence_relative_db':-45.,
        'minimum_early_decay_r_squared':.15,'maximum_early_decay_slope_db_per_second':-.3,
        'both_layers_require_good_identifiable_pitch_with_at_least_four_fitted_peaks':True,
        'any_pitch_identity_ambiguity_retains_prior':True,
        'missing_pitch_fields_retain_prior':True,
        'partial_support_is_union_across_both_layers':'Same gates as the existing mechanics fitter; a clear order in either layer can constrain a shared physical loss.'}
FLAGS=['-O3','-DNDEBUG','-std=c++17','-ffp-contract=off']


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text())
def write(path,value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def record(path):return {'path':str(Path(path).resolve()),'sha256':sha(path)}
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path);value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
def verify(records):
    for row in records:
        if sha(row['path'])!=row['sha256']:raise ValueError('Frozen input changed: '+row['path'])
def run_command(cmd,log):
    with Path(log).open('w') as stream:
        subprocess.run(list(map(str,cmd)),cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True)
    print(Path(log).relative_to(ROOT),flush=True)


def support_mask(rows):
    result=[]
    for midi in sorted({r['midi'] for r in rows}):
        pair=[r for r in rows if r['midi']==midi]
        if {r['layer'] for r in pair}!={4,12}:raise ValueError('Incomplete TRAIN velocity pair')
        details=[];orders=set();pitch_ok=True
        for row in pair:
            missing=[k for k in ('B_identifiable','confidence','fit_partial_count') if k not in row]
            good=(not missing and row['B_identifiable'] is True and row['confidence']=='good'
                  and row['fit_partial_count']>=4 and not row.get('pitch_identity_ambiguous',False))
            accepted=[]
            for partial in row['partials']:
                decay=partial['decay'].get('early')
                if (partial['relative_db'][0]>=POLICY['prominence_relative_db'] and decay
                    and decay['r_squared']>=POLICY['minimum_early_decay_r_squared']
                    and decay['slope_db_per_second']<POLICY['maximum_early_decay_slope_db_per_second']):
                    accepted.append(partial['n'])
            orders.update(accepted);pitch_ok=pitch_ok and good
            details.append({'id':row['id'],'layer':row['layer'],'pitch_ok':good,
                'B_identifiable':row.get('B_identifiable'),'confidence':row.get('confidence'),
                'fit_partial_count':row.get('fit_partial_count'),
                'pitch_identity_ambiguous':row.get('pitch_identity_ambiguous',False),
                'missing_fields':missing,'accepted_early_decay_orders':accepted})
        supported=pitch_ok and len(orders)>=POLICY['minimum_distinct_early_decay_partial_orders']
        result.append({'midi':midi,'supported':supported,'excess_scale':.6 if supported else 1.,
            'distinct_accepted_early_decay_orders':sorted(orders),'layer_evidence':details,
            'decision':'Apply selected correction' if supported else 'Retain prior because existing TRAIN support is limited/ambiguous'})
    return result


def verify_old_control(ids,rows):
    """Authenticate the older guard's cached TRAIN predictions explicitly.

    Its renderer predates the current diagnostic-only fitter revision. Do not
    rewrite that historical receipt or require its guard hash to equal today's.
    Current locked IDs, exact MIDI events, producer and measurement hashes are
    checked instead, separately from new render validation.
    """
    manifest=read(CONTROL_RENDERS/'render-manifest.json')
    cases={r['id']:r for r in manifest['renders']};models={r['id']:r for r in read(CONTROL_SCORE/'model-features.json')['samples']}
    scores={r['id']:r for r in read(CONTROL_SCORE/'score.json')['comparison']};refs={r['id']:r for r in rows}
    producer={'source_sha256':Path(manifest['source_path']),
              'calibration_sha256':Path(manifest['source_path']).parent/'calibration.h',
              'engine_sha256':Path(manifest['engine_path']),
              'reference_features_sha256':REFERENCE,'split_sha256':SPLIT}
    for key,path in producer.items():
        if manifest[key]!=sha(path):raise ValueError('Historical control producer changed')
    for ident in ids:
        row=cases[ident];wav=CONTROL_RENDERS/(ident+'.wav');events=CONTROL_RENDERS/(ident+'.events')
        if row['output_sha256'][wav.name]!=sha(wav) or models[ident]['sha256']!=sha(wav) or scores[ident]['model_sha256']!=sha(wav):
            raise ValueError('Historical control prediction/measurement mismatch')
        if row['inputs']['score_sha256']!=sha(events):raise ValueError('Historical control event receipt mismatch')
        parsed=[line.split() for line in events.read_text().splitlines() if line and not line.startswith('#')]
        expected=[['0.100000','on',str(refs[ident]['midi']),str(refs[ident]['midi_velocity'])],['4.150000','off',str(refs[ident]['midi']),'0']]
        if parsed!=expected:raise ValueError('Historical control event is not the locked TRAIN request')
        for key in producer:
            if row['inputs'][key]!=manifest[key]:raise ValueError('Historical control row producer mismatch')
    return {'manifest':record(CONTROL_RENDERS/'render-manifest.json'),
        'producer':{k:record(v) for k,v in producer.items()},
        'historical_training_guard_sha256':manifest['training_guard_sha256'],
        'scope':'Cached original-calibration control authenticated against current TRAIN IDs/events and actual producer/output/measurement identities; no new acoustic score or render.'}


def freeze(out,fitter,loss):
    rows,notes=fitter.training_inputs(REFERENCE,SPLIT);ids=[r['id'] for r in rows]
    base=read(BASE/'calibration.json');fitter.validate_profile(base)
    if [k['midi'] for k in base['keys']]!=notes:raise ValueError('Anchor inventory mismatch')
    mask=support_mask(rows);by_note={r['midi']:r for r in mask};candidate=copy.deepcopy(base)
    for old,new in zip(base['keys'],candidate['keys']):
        scale=by_note[old['midi']]['excess_scale'];late=np.asarray(old['sigma_late'])
        if scale!=1:
            new['sigma_prompt']=(late+scale*np.maximum(0,np.asarray(old['sigma_prompt'])-late)).tolist()
        elif new['sigma_prompt']!=old['sigma_prompt']:
            raise AssertionError('Unsupported-anchor prior changed')
        if {k:v for k,v in old.items() if k!='sigma_prompt'}!={k:v for k,v in new.items() if k!='sigma_prompt'}:
            raise AssertionError('Non-prompt field changed')
    fitter.validate_profile(candidate)
    candidate['confidence_prior_phase2']={'policy':POLICY,'mask':mask,
        'base_profile':record(BASE/'calibration.json'),
        'global_loss_study':record(ROOT/'Validation/full-inverse-loss.json'),
        'scope':'New ALL-TRAIN fit after failed global-study confirmation; no independent or fresh validation claim.',
        'evaluation_or_pedal_results_used_for_numeric_fit':False,'default_promoted':False}
    profile=out/'calibration.json';solver=out/'solver';solver.mkdir(exist_ok=True)
    if profile.exists() and read(profile)!=candidate:raise ValueError('Existing candidate differs')
    write(profile,candidate);fitter.generate_header(candidate,solver/'calibration.h')
    shutil.copyfile(BASE/'float-solver/grand.cpp',solver/'grand.cpp')
    refs=[]
    for row in rows:
        path=fitter.reference_audio(row,REFERENCE);refs.append(fitter.reference_audio_identity(row,path))
    inputs=[Path(__file__),ROOT/'tools/probe_full_inverse_loss.py',ROOT/'tools/fit_full_calibration.py',
        ROOT/'tools/render_full_training.py',REFERENCE,SPLIT,BASE/'calibration.json',
        BASE/'float-solver/grand.cpp',BASE/'float-solver/calibration.h',BASE/'float-solver/render',
        ROOT/'Validation/full-inverse-loss.json',ROOT/'out/full-inverse-loss-refinement/report.json',
        BASE_RENDERS/'render-manifest.json',BASE_SCORE/'score.json',BASE_SCORE/'model-features.json',
        CONTROL_SCORE/'score.json',CONTROL_SCORE/'model-features.json',profile,solver/'grand.cpp',solver/'calibration.h']
    config={'schema_version':1,'all_training_ids':ids,'support_policy':POLICY,'mask':mask,
        'selection_limits':loss.LIMITS,'compiler':subprocess.check_output(['g++','--version'],text=True).splitlines()[0],
        'flags':FLAGS,'rate':48000,'duration_seconds':3.8,'maximum_concurrent_renders':2,
        'inputs':[record(p) for p in inputs],'reference_identities':refs,
        'v4_baseline':loss.verify_render(BASE_RENDERS,ids),'original_control':verify_old_control(ids,rows),
        'fit_scope':'ALL TRAIN34, including mask/regularization design. No held-out confirmation or fresh validation claim.',
        'evaluation_data_used':False,'pedal_diagnostic_used':False,'canonical_model_changed':False}
    target=out/'freeze.json'
    if target.exists():
        old=read(target);old.pop('frozen_at_utc',None)
        if old!=config:raise ValueError('Frozen phase2 inputs/protocol differ')
    else:write(target,{**config,'frozen_at_utc':datetime.now(timezone.utc).isoformat()})
    verify(config['inputs']);return rows


def predict(out):
    frozen=read(out/'freeze.json');verify(frozen['inputs']);solver=out/'solver';binary=solver/'render'
    if not binary.exists():
        run_command(['g++',*FLAGS,solver/'grand.cpp','-o',binary],out/'compile.log')
        write(out/'build.json',{'source':record(solver/'grand.cpp'),'header':record(solver/'calibration.h'),
            'binary':record(binary),'flags':FLAGS,'compiler':frozen['compiler']})
    else:verify([read(out/'build.json')[k] for k in ('source','header','binary')])
    renders=out/'renders';cmd=[sys.executable,ROOT/'tools/render_full_training.py',
        '--renderer',binary,'--source',solver/'grand.cpp','--calibration',solver/'calibration.h',
        '--duration','3.8','--jobs','2','--output',renders]
    if (renders/'render-inputs.json').exists():cmd.append('--resume')
    run_command(cmd,out/'render.log');verify(frozen['inputs'])
    if not (out/'score/score.json').exists():
        run_command([sys.executable,ROOT/'tools/fit_full_calibration.py','score',
            '--renders',renders,'--output',out/'score'],out/'score.log')
    verify(frozen['inputs'])


def summarize(out,loss):
    frozen=read(out/'freeze.json');verify(frozen['inputs']);ids=frozen['all_training_ids']
    binding=loss.verify_render(out/'renders',ids);new=read(out/'score/score.json')
    vs_v4=loss.comparison(read(BASE_SCORE/'score.json'),new,ids)
    vs_original=loss.comparison(read(CONTROL_SCORE/'score.json'),new,ids)
    result={'schema_version':1,'freeze':record(out/'freeze.json'),'profile':record(out/'calibration.json'),
        'header':record(out/'solver/calibration.h'),'build':record(out/'build.json'),
        'predictions':binding,'score':record(out/'score/score.json'),'mask':frozen['mask'],
        'all_training_vs_v4':vs_v4,'all_training_vs_original_control':vs_original,
        'passes_all_training_gates_vs_v4':vs_v4['passes_all_gates'],'default_promoted':False,
        'scope':frozen['fit_scope'],'evaluation_data_used_for_fit':False,
        'unassigned_component_comparison':new['unassigned_component_comparison'],
        'attack_aggregation':'Unweighted mean of per-case prominent5–100ms band MAEs above250Hz.',
        'limits':['All34 recordings influenced this fitting phase; no independent generalization claim.',
            'Confidence is a conservative regularization rule, not a unique physical loss identification.',
            'The C8 missing component is not generated by this adjustment.',
            'No canonical/source/default change. A passing TRAIN fit still requires frozen historical regression tests and listening.']}
    write(out/'report.json',result)
    if result['passes_all_training_gates_vs_v4']:
        # The candidate and TRAIN predictions are frozen before any later
        # historical-reference feature access or prediction is dispatched.
        target=out/'candidate-freeze.json'
        receipt={'scope':'Candidate frozen after ALL-TRAIN fitting; later tests are historical/observed, never fresh.',
            'profile':record(out/'calibration.json'),'source':record(out/'solver/grand.cpp'),
            'header':record(out/'solver/calibration.h'),'binary':record(out/'solver/render'),
            'protocol':record(out/'freeze.json'),'training_report':record(out/'report.json'),
            'train_predictions':record(out/'renders/render-manifest.json'),
            'historical_predictions_dispatched':False,'default_promoted':False}
        if target.exists():
            old=read(target);old.pop('frozen_at_utc',None)
            if old!=receipt:raise ValueError('Frozen candidate changed')
        else:write(target,{**receipt,'frozen_at_utc':datetime.now(timezone.utc).isoformat()})
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=('freeze','run','report'))
    parser.add_argument('--output',type=Path,default=ROOT/'out/full-confidence-loss')
    parser.add_argument('--report',type=Path,default=ROOT/'Validation/full-confidence-loss.json')
    args=parser.parse_args();out=args.output.resolve();report=args.report.resolve()
    if not (ROOT/'out').resolve() in out.parents:parser.error('Output must be under out/')
    if not any(p.resolve() in report.parents for p in (ROOT/'out',ROOT/'Validation')):parser.error('Report must be under out/ or Validation/')
    out.mkdir(parents=True,exist_ok=True)
    fitter=load('confidence_loss_fitter',ROOT/'tools/fit_full_calibration.py')
    loss=load('confidence_loss_quality',ROOT/'tools/probe_full_inverse_loss.py')
    freeze(out,fitter,loss)
    if args.stage=='run':predict(out)
    if args.stage in ('run','report'):
        result=summarize(out,loss);shutil.copyfile(out/'report.json',report)
        print('All-TRAIN gates passed:',result['passes_all_training_gates_vs_v4'],flush=True)
        print(report,flush=True)


if __name__=='__main__':main()
