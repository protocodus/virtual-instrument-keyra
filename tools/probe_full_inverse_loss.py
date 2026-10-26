#!/usr/bin/env python3
"""TRAIN-only full-network loss response experiment; never edits a live model.

The two positive controls are calibrated late loss and common-unison excess
(prompt minus late). Changing late also changes the existing bridge port and
its loaded radiation transfer; this is intentionally an actual-network probe,
not an identification of an isolated material damping coefficient.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT/'References/GrandFullRange/combined_train_features.json'
SPLIT = ROOT/'References/GrandFullRange/split.json'
BASE = ROOT/'out/full-calibration/v4/radiation'
BASE_RENDERS = ROOT/'out/full-calibration/v4/final-renders'
BASE_SCORE = ROOT/'out/full-calibration/v4/final-score'
PILOT = [note+f'v{layer}' for note in ('A0','C2','C4','D#4','C6') for layer in (4,12)]
BANKS = [('late-down',.7,1.), ('late-up',1.3,1.),
         ('excess-down',1.,.5), ('both-down',.7,.5)]
REFINEMENT = False
FIELDS = ('envelope_mae_db','harmonic_level_mae_db','log_band_mae_db',
          'partial_decay_slope_mae_db_per_second','absolute_f1_error_cents',
          'partial_tuning_mae_cents','attack_rise10_90_error_ms')
LIMITS = {
    'minimum_mean_envelope_improvement_db': .25,
    'maximum_case_envelope_regression_db': .75,
    'maximum_mean_harmonic_regression_db': .25,
    'maximum_case_harmonic_regression_db': 1.,
    'maximum_mean_attack_band_regression_db': .25,
    'maximum_case_attack_band_regression_db': 1.,
    'maximum_mean_decay_regression_db_per_second': .25,
    'maximum_case_decay_regression_db_per_second': 1.,
    'maximum_mean_rise_regression_ms': 1.,
    'maximum_case_rise_regression_ms': 3.,
    'maximum_mean_tuning_regression_cents': .05,
    'maximum_case_tuning_regression_cents': .25,
    'maximum_mean_velocity_contrast_regression_db': .5,
    'maximum_case_velocity_contrast_regression_db': 1.,
    'spurious_band_count_may_increase': False,
}


def sha(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path): return json.loads(Path(path).read_text())
def write(path, value):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def module():
    spec=importlib.util.spec_from_file_location('inverse_loss_training_guard',ROOT/'tools/fit_full_calibration.py')
    value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
def record(path): return {'path':str(Path(path).resolve()),'sha256':sha(path)}
def check_records(records):
    for item in records:
        if sha(item['path'])!=item['sha256']:raise ValueError('Frozen input changed: '+item['path'])
def command(cmd, log):
    log=Path(log);log.parent.mkdir(parents=True,exist_ok=True)
    with log.open('w') as stream:
        subprocess.run(list(map(str,cmd)),cwd=ROOT,stdout=stream,stderr=subprocess.STDOUT,check=True)
    print(log.relative_to(ROOT),flush=True)


def verify_render(folder, ids):
    """Authenticate producer, event and float output identities, not filenames."""
    folder=Path(folder);manifest=read(folder/'render-manifest.json')
    if not manifest['complete'] or manifest['errors']:raise ValueError('Incomplete batch')
    if not set(ids)<=set(manifest['ids']):raise ValueError('Missing requested TRAIN predictions')
    paths={'source_sha256':Path(manifest['source_path']),
           'engine_sha256':Path(manifest['engine_path']),
           'calibration_sha256':Path(manifest['source_path']).parent/'calibration.h',
           'reference_features_sha256':REFERENCE,'split_sha256':SPLIT,
           'training_guard_sha256':ROOT/'tools/fit_full_calibration.py'}
    for key,path in paths.items():
        if manifest[key]!=sha(path):raise ValueError('Producer mismatch: '+str(path))
    rows={r['id']:r for r in manifest['renders']}
    evidence=[]
    for ident in ids:
        row=rows[ident]
        for key in paths:
            if row['inputs'][key]!=manifest[key]:raise ValueError('Row producer mismatch')
        metrics=row['metrics']
        if metrics['nonfinite_samples'] or metrics['string_count']!=230 or metrics['board_modes']!=475:
            raise ValueError('Invalid full-model topology/output')
        if sha(folder/(ident+'.events'))!=row['inputs']['score_sha256']:
            raise ValueError('Event mismatch: '+ident)
        for name,want in row['output_sha256'].items():
            if sha(folder/name)!=want:raise ValueError('WAV mismatch: '+name)
        evidence.append({'id':ident,'events':record(folder/(ident+'.events')),
                         'audio':record(folder/(ident+'.wav')),'metrics':metrics})
    return {'manifest':record(folder/'render-manifest.json'),'producer':paths_as_records(paths),
            'cases':evidence}


def paths_as_records(paths):return {key:record(path) for key,path in paths.items()}


def prepare(out, fitter):
    rows,notes=fitter.training_inputs(REFERENCE,SPLIT)
    byid={r['id']:r for r in rows}
    if not set(PILOT)<=set(byid):raise ValueError('Pilot inventory left locked TRAIN')
    profile=read(BASE/'calibration.json');fitter.validate_profile(profile)
    if set(profile['training_ids'])!=set(byid):raise ValueError('Base TRAIN mismatch')
    cached_models={r['id']:r for r in read(BASE_SCORE/'model-features.json')['samples']}
    cached_scores={r['id']:r for r in read(BASE_SCORE/'score.json')['comparison']}
    for ident in PILOT:
        actual=sha(BASE_RENDERS/(ident+'.wav'))
        if cached_models[ident]['sha256']!=actual or cached_scores[ident]['model_sha256']!=actual:
            raise ValueError('Cached measurement does not describe actual prediction: '+ident)
    inputs=[Path(__file__),ROOT/'tools/fit_full_calibration.py',ROOT/'tools/render_full_training.py',
            REFERENCE,SPLIT,BASE/'calibration.json',BASE/'float-solver/grand.cpp',
            BASE/'float-solver/calibration.h',BASE/'float-solver/render',
            BASE_RENDERS/'render-manifest.json',BASE_SCORE/'score.json',BASE_SCORE/'model-features.json']
    if REFINEMENT:inputs.append(ROOT/'out/full-inverse-loss/report.json')
    refs=[]
    for ident in PILOT:
        path=fitter.reference_audio(byid[ident],REFERENCE)
        refs.append(fitter.reference_audio_identity(byid[ident],path));inputs.append(path)
    config={'schema_version':1,'pilot_ids':PILOT,'complete_training_ids':sorted(byid),
            'banks':[{'name':name,'late_scale':late,'prompt_minus_late_scale':extra} for name,late,extra in BANKS],
            'selection_limits':LIMITS,'inputs':[record(p) for p in inputs],
            'reference_identities':refs,'baseline':verify_render(BASE_RENDERS,PILOT),
            'evaluation_data_used':False,'new_recordings_read':False,
            'scope':'Conditional TRAIN pilot on a base profile already fitted to TRAIN34; not fresh validation.'}
    if REFINEMENT:
        config['prospective_extension']={'initial_pilot':record(ROOT/'out/full-inverse-loss/report.json'),
            'change':'One additional global excess scale0.6 between the initial0.5 probe and baseline1.0; every gate unchanged.',
            'reason':'Initial0.5 bank passed all but one frozen gate; interpolate a smaller perturbation using TRAIN only.',
            'pedal_condition_results_used':False}
    target=out/'freeze.json'
    if target.exists():
        if read(target)!=config:raise ValueError('Existing freeze differs; use a new output directory')
    else:write(target,config)
    for name,late_scale,excess_scale in BANKS:
        candidate=copy.deepcopy(profile)
        for old,new in zip(profile['keys'],candidate['keys']):
            late=np.asarray(old['sigma_late']);excess=np.maximum(0,np.asarray(old['sigma_prompt'])-late)
            new['sigma_late']=(late*late_scale).tolist()
            new['sigma_prompt']=(late*late_scale+excess*excess_scale).tolist()
            if {k:v for k,v in old.items() if k not in ('sigma_late','sigma_prompt')}!={k:v for k,v in new.items() if k not in ('sigma_late','sigma_prompt')}:
                raise AssertionError('Non-loss field changed')
        fitter.validate_profile(candidate)
        candidate['inverse_loss_probe']={'name':name,'late_scale':late_scale,
            'prompt_minus_late_scale':excess_scale,'base_profile':record(BASE/'calibration.json'),
            'frozen_pilot':record(target),'selected':False,'evaluation_used':False}
        folder=out/name;folder.mkdir(exist_ok=True)
        profile_path=folder/'calibration.json'
        if profile_path.exists() and read(profile_path)!=candidate:raise ValueError('Candidate profile changed')
        write(profile_path,candidate)
        solver=folder/'solver';solver.mkdir(exist_ok=True)
        shutil.copyfile(BASE/'float-solver/grand.cpp',solver/'grand.cpp')
        fitter.generate_header(candidate,solver/'calibration.h')
        # All source/calibration changes are private output files. Inputs stay frozen.
    check_records(config['inputs'])
    return config


def build_and_measure(out, ids):
    frozen=read(out/'freeze.json');check_records(frozen['inputs'])
    for name,_,_ in BANKS:
        folder=out/name;solver=folder/'solver';binary=solver/'render'
        if not binary.exists():
            flags=['-O3','-DNDEBUG','-std=c++17','-ffp-contract=off']
            command(['g++',*flags,solver/'grand.cpp','-o',binary],folder/'compile.log')
            write(folder/'build.json',{'compiler':subprocess.check_output(['g++','--version'],text=True).splitlines()[0],
                'flags':flags,'source':record(solver/'grand.cpp'),'header':record(solver/'calibration.h'),
                'binary':record(binary),'profile':record(folder/'calibration.json')})
        else:
            build=read(folder/'build.json')
            check_records([build[k] for k in ('source','header','binary','profile')])
        stage='pilot' if set(ids)==set(PILOT) else 'all-training'
        renders=folder/stage/'renders';score=folder/stage/'score'
        cmd=[sys.executable,ROOT/'tools/render_full_training.py','--renderer',binary,
             '--source',solver/'grand.cpp','--calibration',solver/'calibration.h',
             '--duration','3.8','--jobs','2','--output',renders,'--ids',*ids]
        if (renders/'render-inputs.json').exists():cmd.append('--resume')
        command(cmd,folder/stage/'render.log')
        binding=verify_render(renders,ids)
        if not (score/'score.json').exists():
            command([sys.executable,ROOT/'tools/fit_full_calibration.py','score',
                     '--renders',renders,'--output',score,'--ids',*ids],folder/stage/'score.log')
        check_records(frozen['inputs'])
        write(folder/stage/'binding.json',binding)


def mean(xs):
    values=[float(x) for x in xs if x is not None and math.isfinite(x)]
    return float(np.mean(values)) if values else None


def attack_by_case(score):
    return {r['id']:mean(abs(value) for w in r['differences'] if .005<=w['window_seconds'][0]<.1
            for j,value in enumerate(w['band_error_db']) if j>0 and w['reference_prominent_band_mask'][j])
            for r in score['attack_texture']}


def diagnostic_features(refs, models, ids):
    result=[];models={r['id']:r for r in models['samples']};refs={r['id']:r for r in refs}
    for ident in ids:
        ref,model=refs[ident],models[ident];gain=ref['early_rms']/model['early_rms']
        times=np.asarray(ref['envelope_times_seconds']);mtimes=np.asarray(model['envelope_times_seconds'])
        values=np.interp(times,mtimes,model['envelope_rms'])*gain
        signed=20*np.log10(np.maximum(values,1e-20)/np.maximum(ref['envelope_rms'],1e-20))
        slopes=[]
        for p in ref['partials']:
            q=next((q for q in model['partials'] if q['n']==p['n']),None)
            if q is None or p['relative_db'][0]<-40 or min(p['relative_db'][2:])<-45:continue
            a,b=p['decay'].get('late'),q['decay'].get('late')
            if a and b and a['r_squared']>.15 and a['slope_db_per_second']<-.3:
                slopes.append({'n':p['n'],'model_minus_reference_db_per_second':b['slope_db_per_second']-a['slope_db_per_second']})
        result.append({'id':ident,'signed_envelope_db_after_.75s':mean(signed[times>=.75]),
            'last_envelope_error_db':float(signed[-1]),'reliable_late_partial_pairs':slopes,
            'median_late_slope_signed_error_db_per_second':float(np.median([p['model_minus_reference_db_per_second'] for p in slopes])) if slopes else None,
            'interpretation':'Negative envelope means too little normalized power; negative slope error means faster measured partial-band decay. These need not agree.'})
    return result


def comparison(base, candidate, ids):
    b={r['id']:r for r in base['comparison']};c={r['id']:r for r in candidate['comparison']}
    ba,ca=attack_by_case(base),attack_by_case(candidate)
    cases=[]
    for ident in ids:
        values={field:{'baseline':b[ident][field],'candidate':c[ident][field],
                       'change':c[ident][field]-b[ident][field] if b[ident][field] is not None and c[ident][field] is not None else None} for field in FIELDS}
        values['attack_band_mae_db']={'baseline':ba[ident],'candidate':ca[ident],'change':ca[ident]-ba[ident]}
        cases.append({'id':ident,**values,'spurious_baseline':len(b[ident]['spurious_prominent_model_bands']),
                      'spurious_candidate':len(c[ident]['spurious_prominent_model_bands'])})
    metrics={field:{'baseline_mean':mean(r[field]['baseline'] for r in cases),
                    'candidate_mean':mean(r[field]['candidate'] for r in cases),
                    'mean_change':mean(r[field]['change'] for r in cases),
                    'worst_case_regression':max(r[field]['change'] for r in cases if r[field]['change'] is not None)}
                    for field in (*FIELDS,'attack_band_mae_db')}
    midis={r['midi'] for r in candidate['comparison'] if r['id'] in ids}
    bv={r['midi']:r for r in base['velocity_contrasts']};cv={r['midi']:r for r in candidate['velocity_contrasts']}
    velocity=[{'midi':n,'baseline_absolute_error_db':abs(bv[n]['error_db']),
               'candidate_absolute_error_db':abs(cv[n]['error_db']),
               'change':abs(cv[n]['error_db'])-abs(bv[n]['error_db'])} for n in sorted(midis)]
    spurious={'baseline':sum(r['spurious_baseline'] for r in cases),'candidate':sum(r['spurious_candidate'] for r in cases)}
    gates={
        'mean_envelope':metrics['envelope_mae_db']['mean_change']<=-LIMITS['minimum_mean_envelope_improvement_db'],
        'case_envelope':metrics['envelope_mae_db']['worst_case_regression']<=LIMITS['maximum_case_envelope_regression_db'],
        'mean_harmonic':metrics['harmonic_level_mae_db']['mean_change']<=LIMITS['maximum_mean_harmonic_regression_db'],
        'case_harmonic':metrics['harmonic_level_mae_db']['worst_case_regression']<=LIMITS['maximum_case_harmonic_regression_db'],
        'mean_attack_band':metrics['attack_band_mae_db']['mean_change']<=LIMITS['maximum_mean_attack_band_regression_db'],
        'case_attack_band':metrics['attack_band_mae_db']['worst_case_regression']<=LIMITS['maximum_case_attack_band_regression_db'],
        'mean_decay':metrics['partial_decay_slope_mae_db_per_second']['mean_change']<=LIMITS['maximum_mean_decay_regression_db_per_second'],
        'case_decay':metrics['partial_decay_slope_mae_db_per_second']['worst_case_regression']<=LIMITS['maximum_case_decay_regression_db_per_second'],
        'mean_rise':metrics['attack_rise10_90_error_ms']['mean_change']<=LIMITS['maximum_mean_rise_regression_ms'],
        'case_rise':metrics['attack_rise10_90_error_ms']['worst_case_regression']<=LIMITS['maximum_case_rise_regression_ms'],
        'mean_tuning':metrics['partial_tuning_mae_cents']['mean_change']<=LIMITS['maximum_mean_tuning_regression_cents'],
        'case_tuning':metrics['partial_tuning_mae_cents']['worst_case_regression']<=LIMITS['maximum_case_tuning_regression_cents'],
        'mean_velocity':mean(r['change'] for r in velocity)<=LIMITS['maximum_mean_velocity_contrast_regression_db'],
        'case_velocity':max(r['change'] for r in velocity)<=LIMITS['maximum_case_velocity_contrast_regression_db'],
        'spurious':spurious['candidate']<=spurious['baseline']}
    return {'cases':cases,'metrics':metrics,'velocity_contrasts':velocity,'spurious':spurious,
            'gates':gates,'passes_all_gates':all(gates.values())}


def report(out, fitter):
    frozen=read(out/'freeze.json');check_records(frozen['inputs'])
    refs,_=fitter.training_inputs(REFERENCE,SPLIT)
    base=read(BASE_SCORE/'score.json');base_models=read(BASE_SCORE/'model-features.json')
    banks=[]
    for name,late,extra in BANKS:
        folder=out/name/'pilot';verify_render(folder/'renders',PILOT)
        score=read(folder/'score/score.json');models=read(folder/'score/model-features.json')
        result=comparison(base,score,PILOT)
        banks.append({'name':name,'late_scale':late,'prompt_minus_late_scale':extra,
            **result,'diagnostics':diagnostic_features(refs,models,PILOT),
            'profile':record(out/name/'calibration.json'),'score':record(folder/'score/score.json'),
            'predictions':record(folder/'renders/render-manifest.json')})
    passing=[r for r in banks if r['passes_all_gates']]
    selected=min(passing,key=lambda r:r['metrics']['envelope_mae_db']['mean_change'])['name'] if passing else None
    result={'schema_version':1,'freeze':record(out/'freeze.json'),'pilot_ids':PILOT,
        'baseline_diagnostics':diagnostic_features(refs,base_models,PILOT),
        'banks':banks,'selected_for_remaining_training':selected,'promoted':False,
        'evaluation_data_used_for_selection_or_fit':False,'canonical_model_changed':False,
        'interpretation':'Positive full-network response experiment. Late scaling changes intrinsic losses and bridge port strength; common-unison excess scaling changes choir dissipation. Recording partial slopes are not uniquely isolated losses.',
        'limits':['All data are previously fitted TRAIN; this is not independent generalization.',
                  'Radiation target arrays and analytic loaded-board H phase remain unchanged. Late scaling changes bridge-transformer/output amplitude and actual coupled-state evolution; H depends on unchanged board/frequencies/fixed resistances, not that transformer.',
                  'No recording waveform enters the synthesizer. No ambiguity/body/room/background power is relabeled as a material property.',
                  'No evaluation audio or feature file is read. Main-note recording velocity proxies and acquisition conditions remain uncertain.']}
    write(out/'report.json',result)
    return result


def validate_selected(out, fitter):
    summary=read(out/'report.json');name=summary['selected_for_remaining_training']
    if name is None:return summary
    rows,_=fitter.training_inputs(REFERENCE,SPLIT);ids=[r['id'] for r in rows]
    # Avoid compiling/rerendering unselected banks: validation is not a new search.
    folder=out/name;solver=folder/'solver';renders=folder/'all-training/renders';score=folder/'all-training/score'
    remaining=[ident for ident in ids if ident not in PILOT]
    cmd=[sys.executable,ROOT/'tools/render_full_training.py','--renderer',solver/'render',
         '--source',solver/'grand.cpp','--calibration',solver/'calibration.h',
         '--duration','3.8','--jobs','2','--output',renders,'--ids',*remaining]
    if (renders/'render-inputs.json').exists():cmd.append('--resume')
    command(cmd,folder/'all-training/render.log')
    # Reuse the ten authenticated pilot predictions without claiming a new run.
    manifest=read(renders/'render-manifest.json')
    write(renders/'remaining-render-manifest.json',manifest)
    pilot_folder=folder/'pilot/renders';verify_render(pilot_folder,PILOT)
    pilot=read(pilot_folder/'render-manifest.json')
    if any(manifest[k]!=pilot[k] for k in ('source_sha256','calibration_sha256','engine_sha256',
        'reference_features_sha256','split_sha256','training_guard_sha256','rate','duration_seconds','event_policy')):
        raise ValueError('Pilot and confirmation producer/configuration mismatch')
    reused=[]
    for row in pilot['renders']:
        for suffix in ('.wav','.events','.json'):
            shutil.copyfile(pilot_folder/(row['id']+suffix),renders/(row['id']+suffix))
        reused.append({**row,'reused_prediction_receipt':record(pilot_folder/(row['id']+'.json'))})
    manifest.update(ids=sorted(ids),renders=sorted(manifest['renders']+reused,key=lambda r:r['id']),
        prediction_reuse={'pilot_manifest':record(pilot_folder/'render-manifest.json'),
            'reused_ids':PILOT,'newly_rendered_ids':remaining,'no_pilot_rerender':True})
    write(renders/'render-manifest.json',manifest)
    binding=verify_render(renders,ids)
    if not (score/'score.json').exists():
        command([sys.executable,ROOT/'tools/fit_full_calibration.py','score','--renders',renders,'--output',score],folder/'all-training/score.log')
    base=read(BASE_SCORE/'score.json');candidate=read(score/'score.json')
    summary['training_confirmation']={'all_training':comparison(base,candidate,ids),
        'remaining_training':comparison(base,candidate,remaining),'binding':binding,
        'unassigned_component_comparison':candidate['unassigned_component_comparison'],
        'scope':'Conditional transfer to previously fitted TRAIN cases, not a fresh evaluation; no further setting chosen from this confirmation.'}
    check_records(read(out/'freeze.json')['inputs']);write(out/'report.json',summary);return summary


def main():
    global BANKS,REFINEMENT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=('prepare','pilot','report','validate-selected','run'))
    parser.add_argument('--output',type=Path,default=ROOT/'out/full-inverse-loss')
    parser.add_argument('--report',type=Path,default=ROOT/'Validation/full-inverse-loss.json')
    parser.add_argument('--refine-excess',action='store_true',help='One separately registered TRAIN-selected excess0.6 refinement; use a new output folder')
    args=parser.parse_args();out=args.output.resolve()
    if args.refine_excess:
        BANKS=[('excess-refined',1.,.6)];REFINEMENT=True
    if not (ROOT/'out').resolve() in out.parents:parser.error('Private experiment output must be under out/')
    report_path=args.report.resolve()
    if not any(folder.resolve() in report_path.parents for folder in (ROOT/'out',ROOT/'Validation')):
        parser.error('Report must be under out/ or Validation/')
    out.mkdir(parents=True,exist_ok=True);fitter=module()
    if args.stage in ('prepare','run'):prepare(out,fitter)
    if args.stage in ('pilot','run'):build_and_measure(out,PILOT)
    if args.stage in ('report','run'):report(out,fitter)
    if args.stage in ('validate-selected','run'):validate_selected(out,fitter)
    if (out/'report.json').exists():
        shutil.copyfile(out/'report.json',args.report)
        data=read(out/'report.json')
        print('Selected:',data['selected_for_remaining_training'],flush=True)
    print(out,flush=True)


if __name__=='__main__':main()
