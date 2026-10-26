#!/usr/bin/env python3
"""One frozen full-model evaluation, separate from the TRAIN-only fitter.

Stages deliberately separate model/protocol freezing, prediction synthesis,
first reference decode, and scoring. No stage changes a model or calibration.
"""
from __future__ import annotations
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import importlib.util
import json
import math
from pathlib import Path
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'out/full-calibration/v4/evaluation'
VALIDATION = ROOT/'Validation'
sys.path.insert(0, str(ROOT/'tools'))
import fetch_full_range_grand as acquisition
import extract_full_range_grand as extractor
import fit_full_calibration as fitting
sha = acquisition.sha
benchmark = fitting.benchmark


def now(): return datetime.now(timezone.utc).isoformat()
def read(path): return json.loads(Path(path).read_text())
def write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
def record(path):
    path = Path(path).resolve()
    return {'path': str(path), 'sha256': sha(path)}
def verify(records):
    for item in records:
        if sha(Path(item['path'])) != item['sha256']:
            raise RuntimeError('Frozen input changed: '+item['path'])


def inventory():
    split, manifest = acquisition.locked_inputs()
    rows = [dict(row, source_manifest='References/GrandFullRange/manifest.json',
                 source_root=str(acquisition.ROOT)) for row in manifest['samples']
            if row['role'] != 'train']
    extra = read(ROOT/'References/GrandExpanded/manifest.json')
    wanted = {'A3v4','A3v8','A3v12','D#3v8','D#4v8','A4v8','D#5v8'}
    for item in extra['samples']:
        if item['id'] in wanted:
            rows.append(dict(item, role='historical_evaluation',
                             source_manifest='References/GrandExpanded/manifest.json',
                             source_root=str(ROOT/'References/GrandExpanded')))
    if len(rows) != 16 or len({r['id'] for r in rows}) != 16:
        raise RuntimeError('Expected two fresh and fourteen historical evaluation cases')
    if set(r['id'] for r in rows)&set(split['combined_training_ids']):
        raise RuntimeError('TRAIN case entered evaluation inventory')
    return rows


def attack_error(rows):
    values = [abs(v) for row in rows for window in row['differences']
              if window['window_seconds'][0] >= .005
              for index,v in enumerate(window['band_error_db'])
              if index > 0 and window['reference_prominent_band_mask'][index]]
    return float(np.mean(values)) if values else None


def compare_report(control, candidate):
    a = {r['id']:r for r in control['comparison']}
    b = {r['id']:r for r in candidate['comparison']}
    fields = ('harmonic_level_mae_db','envelope_mae_db','log_band_mae_db',
              'absolute_f1_error_cents','partial_tuning_mae_cents',
              'partial_decay_slope_mae_db_per_second','attack_rise10_90_error_ms')
    result = {}
    for field in fields:
        changes = [{'id':name,'control':a[name][field],'candidate':b[name][field],
                    'candidate_minus_control':b[name][field]-a[name][field]}
                   for name in a if a[name].get(field) is not None and b[name].get(field) is not None]
        result[field] = {'control_mean':float(np.mean([x['control'] for x in changes])) if changes else None,
                         'candidate_mean':float(np.mean([x['candidate'] for x in changes])) if changes else None,
                         'improved_cases':sum(x['candidate_minus_control']<0 for x in changes),
                         'valid_cases':len(changes),
                         'cases':sorted(changes,key=lambda x:x['candidate_minus_control'])}
    result['attack_5_100ms_prominent_bands_above250Hz_mae_db'] = {
        'control':attack_error(control['attack_texture']), 'candidate':attack_error(candidate['attack_texture'])}
    result['harmonic_or_envelope_regressions_above2db'] = [
        {'id':name,'metric':field,'candidate_minus_control':b[name][field]-a[name][field]}
        for name in a for field in ('harmonic_level_mae_db','envelope_mae_db')
        if a[name].get(field) is not None and b[name].get(field) is not None and b[name][field]-a[name][field]>2]
    return result


def freeze():
    destination = OUT/'freeze.json'
    if destination.exists() or (OUT/'reference-opening-started.json').exists():
        raise RuntimeError('Evaluation already frozen; receipt is never overwritten')
    rows = inventory()
    fresh = [r for r in rows if r['role']=='reserved_fresh_evaluation']
    for row in fresh:
        for path in (Path(row['source_root'])/row['wav_path'], OUT/'recordings'/(row['id']+'.wav')):
            if path.exists(): raise RuntimeError('Fresh audio already decoded before freeze: '+str(path))
    batch = {'control':ROOT/'out/full-calibration/v3/control-renders/render-manifest.json',
             'candidate':ROOT/'out/full-calibration/v4/final-renders/render-manifest.json'}
    producers = {}
    inputs = [record(Path(__file__)),record(ROOT/'tools/fit_full_calibration.py'),
              record(ROOT/'tools/extract_full_range_grand.py'),record(ROOT/'tools/full_range_pitch.py'),
              record(ROOT/'Research/GrandPianoV2/tools/benchmark.py'),
              record(ROOT/'Research/GrandPianoV2/reference/fetch_reference.py'),
              record(ROOT/'tools/fetch_full_range_grand.py'),record(ROOT/'References/GrandFullRange/split.json'),
              record(ROOT/'References/GrandFullRange/manifest.json'),record(ROOT/'References/GrandExpanded/manifest.json'),
              record(ROOT/'out/full-calibration/v4/radiation/calibration.json'),
              record(ROOT/'out/full-calibration/v4/radiation/radiation-fit.json')]
    for label,path in batch.items():
        receipt = read(path)
        if not receipt['complete'] or len(receipt['renders'])!=34: raise RuntimeError('Incomplete TRAIN batch')
        source=Path(receipt['source_path']); binary=Path(receipt['engine_path']); header=source.parent/'calibration.h'
        for p,key in ((source,'source_sha256'),(binary,'engine_sha256'),(header,'calibration_sha256')):
            if sha(p)!=receipt[key]: raise RuntimeError('TRAIN producer changed: '+str(p))
            inputs.append(record(p))
        producers[label] = {'source':str(source),'binary':str(binary),'header':str(header),
                            'training_manifest':record(path)}
        inputs.append(record(path))
    control=read(ROOT/'out/full-calibration/v4/control-score/score.json')
    candidate=read(ROOT/'out/full-calibration/v4/final-score/score.json')
    training = {'scope':'Locked TRAIN34; no evaluation data used in selection.',
                'selection':'Retain as research candidate for evaluation; not a default promotion.',
                'comparison':compare_report(control,candidate),
                'sources':[record(ROOT/'out/full-calibration/v4/control-score/score.json'),
                           record(ROOT/'out/full-calibration/v4/analytic-score/score.json'),
                           record(ROOT/'out/full-calibration/v4/final-score/score.json')],
                'optimizer':'Joint radiation optimizer reached 350-iteration cap; converged=false.',
                'limits':'C8 unassigned4434Hz component missing; train gains are not perceptual parity.'}
    inputs += training['sources']
    write(OUT/'training-result.json',training)
    receipt = {'schema_version':1,'frozen_at_utc':now(),'inputs':inputs,'producers':producers,
        'cases':rows,'fresh_ids':['A0v8','C8v8'],'fresh_reference_decoded_at_freeze':False,
        'prediction_protocol':{'sample_rate':48000,'duration_seconds':3.8,
           'note_on_seconds':.1,'note_off_seconds':4.15,'pedal':0,
           'velocity':'Pinned SFZ-bin midpoint; not measured hammer velocity.',
           'all_predictions_before_first_fresh_decode':True,
           'features':'Frozen benchmark and censored edge helper; counterpart uses reference window/envelope support.',
           'gain':'One per-case early0.05–0.75s RMS scalar; fixed throughout each note.',
           'attack':'Report0–5ms/sub250Hz diagnostics; primary texture5–100ms strong bands above250Hz.',
           'components':'Reference-fixed unassigned component bands, including C8 near4434Hz; never move to model peaks.',
           'comparison_groups':['fresh two extremes','historical full-range seven','historical interpolation seven']},
        'predictions_from_training':{
           'A0v8':'Expect harmonic error at least2dB and envelope at least1dB below control.',
           'C8v8':'Expect substantial remaining error and missing4434Hz component; no complete fit expected.',
           'historical':'Expect lower mean harmonic/envelope/5–100ms attack error; individual regressions remain possible.'},
        'acceptance_limits':{'promotion_authorized':False,
           'research_generalization':'Lower mean harmonic/envelope and5–100ms attack errors on historical group; fresh cases shown individually.',
           'severe_regression_reporting':'Every case retained; flag harmonic/envelope regression above2dB.',
           'C8':'Failure to reproduce observed4434Hz component remains explicit regardless of aggregate gains.',
           'realtime_or_perceptual_claim':'None; these are recording-agreement metrics on one piano/recording chain.'},
        'training_result':record(OUT/'training-result.json')}
    verify(inputs)
    write(destination,receipt)
    write(VALIDATION/'full-calibration-v4-training.json',training)
    write(VALIDATION/'full-calibration-v4-freeze.json',receipt)
    print(str(destination),sha(destination),flush=True)


def locked():
    frozen=read(OUT/'freeze.json')
    verify(frozen['inputs']); verify([frozen['training_result']])
    if sha(OUT/'freeze.json')!=sha(VALIDATION/'full-calibration-v4-freeze.json'):
        raise RuntimeError('Frozen receipt copies differ')
    return frozen


def predictions(jobs):
    frozen=locked()
    if (OUT/'reference-opening-started.json').exists(): raise RuntimeError('Prediction stage closed after reference opening')
    def one(label,producer,row):
        folder=OUT/'predictions'/label;folder.mkdir(parents=True,exist_ok=True)
        events=folder/(row['id']+'.events'); audio=folder/(row['id']+'.wav')
        events.write_text(f"# Frozen held-note prediction; acquisition pedal unknown.\n0.100000 on {row['midi']} {row['midi_velocity']}\n4.150000 off {row['midi']} 0\n")
        command=[producer['binary'],'--events',str(events),'--output',str(audio),
                 '--sample-rate','48000','--duration','3.8']
        sidecar=folder/(row['id']+'.json')
        if sidecar.exists():
            previous=read(sidecar);verify(previous['outputs'])
            if previous['command']!=command or previous['event_sha256']!=sha(events):raise RuntimeError('Cached prediction differs')
            return previous
        call=subprocess.run(command,check=True,text=True,capture_output=True)
        metrics=json.loads(call.stdout)
        if metrics['nonfinite_samples'] or metrics['string_count']!=230 or metrics['board_modes']!=475:
            raise RuntimeError('Invalid full prediction')
        result={'id':row['id'],'variant':label,'command':command,'event_sha256':sha(events),
                'outputs':[record(audio)],'metrics':metrics}
        write(sidecar,result);print(label+' '+row['id']+' prediction complete',flush=True)
        return result
    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futures=[pool.submit(one,label,producer,row) for label,producer in frozen['producers'].items() for row in frozen['cases']]
        results=[future.result() for future in as_completed(futures)]
    locked()
    write(OUT/'predictions.json',{'completed_at_utc':now(),'freeze':record(OUT/'freeze.json'),
        'all_predictions_before_first_fresh_decode':True,'renders':sorted(results,key=lambda x:(x['variant'],x['id']))})


def acquire():
    frozen=locked(); predictions_receipt=read(OUT/'predictions.json')
    if len(predictions_receipt['renders'])!=32:raise RuntimeError('All predictions required before decoding')
    for item in predictions_receipt['renders']:verify(item['outputs'])
    destination=OUT/'acquisition.json'
    if destination.exists(): raise RuntimeError('First acquisition receipt already exists; use score or verify, never reopen as fresh')
    helper=acquisition.load_pcm_helper();results=[]
    # Write before any external bytes are opened; a crash cannot silently restart
    # and claim that a later freeze preceded first access.
    opening=OUT/'reference-opening-started.json'
    if opening.exists():raise RuntimeError('Reference opening already started; inspect the interrupted run')
    write(opening,{'started_at_utc':now(),'freeze':record(OUT/'freeze.json'),
                   'predictions':record(OUT/'predictions.json')})
    for row in frozen['cases']:
        fresh=row['role']=='reserved_fresh_evaluation'
        root=Path(row['source_root'])
        flac=(OUT/'downloads'/(row['id']+'.flac')) if fresh else root/row['flac_path']
        wav=(OUT/'recordings'/(row['id']+'.wav')) if fresh else root/row['wav_path']
        if not flac.exists():
            if not fresh:raise RuntimeError('Missing historical source '+str(flac))
            flac.parent.mkdir(parents=True,exist_ok=True)
            subprocess.run(['curl','-fsSL','--retry','2','--max-time','120',row['source_url'],'-o',str(flac)],check=True)
        if flac.stat().st_size!=row['flac_bytes'] or acquisition.git_blob_sha(flac)!=row['git_blob_sha1']:
            raise RuntimeError('Pinned Gitblob mismatch '+row['id'])
        if row.get('flac_sha256') and sha(flac)!=row['flac_sha256']:raise RuntimeError('Pinned FLAC SHA mismatch')
        if fresh:
            if wav.exists():raise RuntimeError('Fresh decode unexpectedly present '+row['id'])
            wav.parent.mkdir(parents=True,exist_ok=True)
            subprocess.run(['ffmpeg','-v','error','-y','-i',str(flac),'-c:a','pcm_s24le',str(wav)],check=True)
        pcm=helper.decoded_pcm_identity(wav)
        if (pcm['sample_rate'],pcm['channels'],pcm['pcm_bits'])!=(48000,2,24):raise RuntimeError('Unexpected PCM format')
        if row.get('decoded_pcm') and pcm!=row['decoded_pcm']:raise RuntimeError('Historical PCM mismatch')
        results.append({'id':row['id'],'role':row['role'],'flac':record(flac),'wav':record(wav),
                        'decoded_pcm':pcm,'git_blob_verified':True,'decoded_at_utc':now() if fresh else None})
        print(row['id']+' authenticated '+('first decode' if fresh else 'historical PCM'),flush=True)
    locked()
    receipt={'completed_at_utc':now(),'freeze':record(OUT/'freeze.json'),'predictions':record(OUT/'predictions.json'),
        'opening':record(opening),'samples':results,'license':{'title':'Salamander Grand Piano V3','author':'Alexander Holm',
        'url':'https://creativecommons.org/licenses/by/3.0/','source_commit':'3382bf9496bba2486f5ab0de55a264d1dfc38404',
        'modifications':'Lossless PCM24 WAV decode only. No gain/trim/retune/resample/denoise/EQ/padding.'}}
    write(destination,receipt)
    write(VALIDATION/'full-calibration-v4-acquisition.json',receipt)


def measure_pair(ref,model_path):
    if ref.get('analysis_windows_seconds'):
        model=extractor.censored_features(model_path,ref['midi'],benchmark,
            analysis_windows_seconds=ref['analysis_windows_seconds'],envelope_times_seconds=ref['envelope_times_seconds'],
            max_analysis_seconds=ref['available_seconds_after_onset'],component_frequencies_hz=[])
    else:model=benchmark.extract_features(model_path,ref['midi'])
    model['split']=ref['split']
    comparison=benchmark.compare_features(ref,model)
    comparison['spurious_prominent_model_bands']=fitting.spurious_model_bands(ref,model)
    sr,x=benchmark.load_audio(ref['path']);msr,mx=benchmark.load_audio(model_path)
    rattack=fitting.attack_measurement(x,sr,ref['early_rms']);mattack=fitting.attack_measurement(mx,msr,model['early_rms'])
    differences=[]
    for r,m in zip(rattack,mattack):
        rp=np.asarray(r['normalized_band_power']);mp=np.asarray(m['normalized_band_power'])
        differences.append({'window_seconds':r['window_seconds'],
            'band_error_db':(10*np.log10(np.maximum(mp,1e-12)/np.maximum(rp,1e-12))).tolist(),
            'reference_prominent_band_mask':(rp>1e-5).tolist(),
            'centroid_log2_ratio':math.log2(max(m['centroid_250_19000_hz'],1)/max(r['centroid_250_19000_hz'],1)),
            'crest_error_db':m['crest_db']-r['crest_db'],
            'power_over_steady_rms_error_db':m['power_over_steady_rms_db']-r['power_over_steady_rms_db']})
    components=[]
    if ref.get('unassigned_components'):
        onset,_=benchmark.onset_index(mx,msr)
        aligned=mx[onset:onset+int(math.ceil(min(4.,ref['available_seconds_after_onset'])*msr-1e-8))]
        gain=ref['early_rms']/model['early_rms']
        for rc in ref['unassigned_components']:
            mc=extractor.component_features(aligned,msr,rc['frequency_hz'],rc['analysis_windows_seconds'],model['early_rms']**2,ref['f1_hz'],benchmark)
            error=10*np.log10(np.maximum(np.asarray(mc['powers'])*gain*gain,1e-30)/np.maximum(rc['powers'],1e-30))
            components.append({'id':ref['id'],'frequency_hz_fixed_to_reference':rc['frequency_hz'],
                'reference':rc,'model':mc,'fixed_early_gain_power_error_db':error.tolist(),
                'reference_prominent_window_mask':(np.asarray(rc['relative_db'])>-50).tolist(),
                'physical_identity':'unassigned/unknown','used_in_fitting':False})
    return model,comparison,{'id':ref['id'],'reference':rattack,'model':mattack,'differences':differences},components


def score():
    frozen=locked();acquired=read(OUT/'acquisition.json'); verify([acquired['predictions']])
    if (OUT/'results.json').exists():raise RuntimeError('Evaluation already scored; do not repeat as fresh')
    sources={r['id']:r for r in acquired['samples']};references=[];qc=[]
    for row in frozen['cases']:
        source=sources[row['id']];verify([source['wav'],source['flac']]);path=Path(source['wav']['path'])
        # Use the same frozen censored estimator for the three extreme registers;
        # ordinary notes use the immutable legacy formulas.
        ref=(extractor.censored_features(path,row['midi'],benchmark) if row['midi'] in extractor.EDGE_MIDIS
             else benchmark.extract_features(path,row['midi']))
        ref.update(split='fresh_extremes' if row['role']=='reserved_fresh_evaluation' else
            'historical_full_range' if row['source_manifest'].endswith('GrandFullRange/manifest.json') else 'historical_interpolation',
            role=row['role'])
        references.append(ref)
        diagnostics=extractor.quality_diagnostic(path,ref,benchmark);diagnostics['role']=row['role'];qc.append(diagnostics)
    variants={}
    prediction_receipt=read(OUT/'predictions.json')
    for label in frozen['producers']:
        models=[];comparisons=[];attacks=[];components=[]
        for ref in references:
            prediction=next(p for p in prediction_receipt['renders'] if p['id']==ref['id'] and p['variant']==label)
            verify(prediction['outputs'])
            model,comparison,attack,component=measure_pair(ref,Path(prediction['outputs'][0]['path']))
            models.append(model);comparisons.append(comparison);attacks.append(attack);components+=component
            print(label+' '+ref['id']+' evaluation scored',flush=True)
        aggregate={}
        for group in ('fresh_extremes','historical_full_range','historical_interpolation'):
            selected=[dict(row,split='train') for row in comparisons if row['split']==group]
            aggregate[group]=benchmark.aggregate(selected)['train']
        variants[label]={'comparison':comparisons,'aggregate':aggregate,
                         'attack_texture':attacks,'unassigned_component_comparison':components,
                         'spurious_model_band_diagnostic':{
                             'case_count_with_flags':sum(bool(r['spurious_prominent_model_bands']) for r in comparisons),
                             'flagged_window_band_pairs':sum(len(r['spurious_prominent_model_bands']) for r in comparisons)}}
        write(OUT/(label+'-model-features.json'),{'samples':models})
    groups={}
    for group in ('fresh_extremes','historical_full_range','historical_interpolation'):
        restricted={label:{'comparison':[r for r in v['comparison'] if r['split']==group],
                           'attack_texture':[a for a in v['attack_texture'] if any(r['id']==a['id'] and r['split']==group for r in v['comparison'])]}
                    for label,v in variants.items()}
        groups[group]=compare_report(restricted['control'],restricted['candidate'])
    results={'schema_version':1,'scored_at_utc':now(),'freeze':record(OUT/'freeze.json'),
        'acquisition':record(OUT/'acquisition.json'),'predictions':record(OUT/'predictions.json'),
        'fresh_scope':'Only two extreme notes on the same piano/recording chain; no new instrument or mic generalization.',
        'comparison_groups':groups,'variants':variants,'source_quality':qc,
        'promotion':'Not promoted. Review every regression and listening; C8 component remains an explicit failure if absent.',
        'optimizer':'TRAIN joint radiation optimizer reached 350-iteration cap, converged=false.',
        'limits':'Recording-agreement metrics, not perceptual scores; unknown hammer speed/pedal/room/editing; no realtime Reason claim.',
        'evaluation_used_for_fitting':False,'canonical_sources_changed':False}
    locked()
    write(OUT/'reference-features.json',{'samples':references,'acquisition':record(OUT/'acquisition.json')})
    write(OUT/'results.json',results);write(VALIDATION/'full-calibration-v4-evaluation.json',results)
    print(json.dumps({group:{k:v for k,v in report.items() if k=='attack_5_100ms_prominent_bands_above250Hz_mae_db' or k in ('harmonic_level_mae_db','envelope_mae_db')}
                      for group,report in groups.items()},indent=2),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=('freeze','predictions','acquire','score','verify'))
    parser.add_argument('--jobs',type=int,default=3)
    args=parser.parse_args()
    if not 1<=args.jobs<=4:parser.error('Use1–4 jobs')
    OUT.mkdir(parents=True,exist_ok=True)
    if args.stage=='freeze':freeze()
    elif args.stage=='predictions':predictions(args.jobs)
    elif args.stage=='acquire':acquire()
    elif args.stage=='score':score()
    else:locked();print('Frozen inputs match')


if __name__=='__main__':main()
