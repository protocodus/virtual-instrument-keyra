#!/usr/bin/env python3
"""Reproduce real-recording evaluation of the live Keyra signal path.

The 10 training cases, 12 in-range held-out cases and two edge cases remain
locked by Experiments/Research/GrandPianoV2/benchmark/split.json. This tool never fits a
parameter. It renders the measured-attack engine and its fixed-2ms ablation,
then evaluates the same four windows with the preserved phase-insensitive
measurements. Missing model partials receive a noise-floor penalty rather
than silently disappearing from the harmonic average.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import csv
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import subprocess

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'Experiments/Research/GrandPianoV2'
FIELDS = ('log_band_mae_db', 'harmonic_level_mae_db', 'envelope_mae_db',
          'partial_decay_slope_mae_db_per_second', 'absolute_f1_error_cents',
          'partial_tuning_mae_cents', 'attack_rise10_90_error_ms')


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


metrics = module('keyra_reference_metrics', RESEARCH/'tools/benchmark.py')
restore = module('keyra_reference_restore', RESEARCH/'reference/fetch_reference.py')


def sha(path):
    digest = hashlib.sha256()
    with path.open('rb') as source:
        for chunk in iter(lambda: source.read(1024*1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def verify_references(samples):
    manifest = json.loads((RESEARCH/'reference/manifest.json').read_text())
    entries = {item['id']:item for item in manifest['samples']}
    verified = []
    for sample in samples:
        item = entries[sample['id']]
        flac, wav = RESEARCH/item['flac_path'], RESEARCH/item['wav_path']
        if sha(flac) != item['flac_sha256']:
            raise ValueError(f'Reference FLAC hash mismatch: {flac}')
        verified.append(restore.verify_wav(item, wav))
    return {'source_commit':manifest['commit'], 'samples':len(verified),
            'all_flac_hashes_match':True, 'all_decoded_pcm_matches':True,
            'all_wav_container_hashes_match':all(v['container_matches'] for v in verified)}


def comparison(reference, model):
    row = metrics.compare_features(reference, model)
    gain = reference['early_rms']/max(model['early_rms'], 1e-20)
    early_power = reference['early_rms']**2
    lookup = {p['n']:p for p in model['partials']}
    errors, missing = [], []
    for partial in reference['partials']:
        reference_power = np.asarray(partial['powers'])/early_power
        model_partial = lookup.get(partial['n'])
        if model_partial is None:
            model_power = np.zeros(len(reference_power))
            missing.append(partial['n'])
        else:
            model_power = np.asarray(model_partial['powers'])*gain*gain/early_power
        mask = reference_power > 1e-5
        errors.extend(abs(10*np.log10(np.maximum(reference_power[mask],1e-7))
                          -10*np.log10(np.maximum(model_power[mask],1e-7))))
    row['harmonic_level_mae_db'] = float(np.mean(errors)) if errors else None
    row['missing_reference_partials'] = missing
    return row


def summarize(rows):
    result = metrics.aggregate(rows)
    heldout = [row for row in rows if row['split'] in ('heldout_pitch','heldout_velocity')]
    result['heldout_all'] = {'cases':len(heldout)}
    for key in FIELDS:
        values = [r[key] for r in heldout if r[key] is not None and math.isfinite(r[key])]
        result['heldout_all'][key] = {'mean':float(np.mean(values)),
            'median':float(np.median(values)), 'valid_cases':len(values)} if values else None
    return result


def render(renderer, sample, directory, rate, legacy, resonance):
    target = directory/(sample['id']+'.wav')
    command = [str(renderer), '--events', str(RESEARCH/'benchmark/events'/(sample['id']+'.events')),
               '--output',str(target),'--sample-rate',str(rate),'--duration','4.4',
               '--gain','.7','--resonance',str(resonance)]
    if legacy:
        command.append('--legacy-attack')
    completed = subprocess.run(command,check=True,capture_output=True,text=True)
    return {'id':sample['id'],'command':command,'output_sha256':sha(target),
            'renderer_stdout':completed.stdout.strip()}


def write_markdown(report, path):
    labels = {'log_band_mae_db':'Broad spectral bands (dB)',
              'harmonic_level_mae_db':'Harmonic levels (dB)',
              'envelope_mae_db':'Amplitude envelope (dB)',
              'partial_decay_slope_mae_db_per_second':'Partial decay (dB/s)',
              'absolute_f1_error_cents':'Fundamental pitch (cents)',
              'attack_rise10_90_error_ms':'Attack rise (ms)'}
    lines = ['# Keyra live-engine recording benchmark', '',
             'These errors measure agreement with one recorded piano and microphone setup. '
             'They do not measure perceptual realism or demonstrate commercial readiness.', '',
             f"The source FLACs and decoded PCM were verified for all {report['reference_verification']['samples']} cases. "
             'Ten notes/velocities train the numerical model, twelve in-range cases are held out, '
             'and two extreme notes measure extrapolation separately.', '',
             'The original twelve held-out cases stayed excluded from all numerical fitting, '
             'but their results were inspected before the train-only choir correction. These '
             'are now development-validation results. The separately locked eight-note fresh '
             'report supplies the first score after the final model coefficients were frozen.', '',
             'The measured attack and fixed 2 ms attack use identical events, rate and engine '
             'parameters. The attack coefficients come only from the ten training recordings. '
             'The preserved offline v2 renderer is a different, much more expensive model; its '
             'metrics are shown as historical context. In the attack comparison, the exposed '
             'resonance control is zero to measure the fitted modal source. The product-default '
             'column uses resonance 0.25; all other controls retain their defaults. '
             'This is a native-engine measurement, with no DAW or Rack host in the path.', '']
    for split,title in [('heldout_all','Twelve development holdout cases'),('train','Ten training cases'),
                        ('edge_extrapolation','Two edge cases')]:
        lines += [f'## {title}', '',
                  '| Mean error; lower is better | Offline v2 | Fixed 2 ms | Measured attack | Product default |',
                  '|---|---:|---:|---:|---:|']
        for key,label in labels.items():
            values=[]
            for variant in ('preserved_v2','fixed_attack','measured_attack','product_default'):
                value=report['variants'].get(variant,{}).get('summary',{}).get(split,{}).get(key)
                values.append(f"{value['mean']:.3f}" if value else '—')
            lines.append('| '+label+' | '+' | '.join(values)+' |')
        lines.append('')
    lines += ['## Limits', '',
              '- Recorded pedal positions, release events and physical hammer speeds are unknown. '
              'Pedal behavior requires new synchronized captures and host playing tests.',
              '- Modal phases, the recording room, detailed contact mechanics and complete '
              'mechanical noises are not identified by this fit. Positive prompt/late decay '
              'components are a compact empirical model.',
              '- One early scalar gain is removed for scoring; later windows keep that gain. '
              'Stereo channels combine in power. Missing prominent model partials receive a penalty.',
              '- The two edge cases are not part of the twelve-case held-out mean. '
              'Per-case regressions and all metric values remain in the matching JSON and CSV.', '']
    path.write_text('\n'.join(lines))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--renderer',type=Path,default=ROOT/'build/keyra_render')
    parser.add_argument('--audio-dir',type=Path,default=ROOT/'build/recording-benchmark')
    parser.add_argument('--output',type=Path,default=ROOT/'Docs/validation/recording-benchmark-2026-10-26.json')
    parser.add_argument('--sample-rate',type=int,default=48000)
    parser.add_argument('--jobs',type=int,default=2)
    parser.add_argument('--skip-render',action='store_true')
    parser.add_argument('--case',action='append',default=[])
    parser.add_argument('--training-only',action='store_true')
    parser.add_argument('--variant',action='append',choices=('fixed_attack','measured_attack','product_default'))
    parser.add_argument('--self-test',action='store_true')
    args=parser.parse_args()
    if args.self_test:
        print(json.dumps(metrics.measurement_self_test(),indent=2));return
    if args.jobs<1 or args.sample_rate not in (44100,48000,88200,96000,176400,192000):
        parser.error('Use a positive job count and a supported audio sample rate')
    split_path = RESEARCH/'benchmark/split.json'
    split=json.loads(split_path.read_text())
    samples=split['samples']
    if args.training_only:
        samples=[s for s in samples if s['split']=='train']
    if args.case:
        if set(args.case)-{s['id'] for s in samples}:
            parser.error('Unknown case ID')
        samples=[s for s in samples if s['id'] in args.case]
    verification=verify_references(samples)
    reference_path=RESEARCH/'benchmark/reference_features.json'
    references={r['id']:r for r in json.loads(reference_path.read_text())['samples']}
    fit_path=ROOT/'Docs/research/realtime-modal-fit-2026-10-26.json'
    fitting=json.loads(fit_path.read_text())
    expected_training={s['id'] for s in split['samples'] if s['split']=='train'}
    if (set(fitting['training_ids'])!=expected_training
        or fitting['heldout_measurements_used'] is not False
        or fitting['generated_header_sha256']!=sha(ROOT/'Source/DSP/MeasuredModalData.h')
        or fitting['fitter_source_sha256']!=sha(ROOT/'Tools/fit_realtime_modal.py')):
        raise ValueError('Current calibration provenance does not match TRAIN10 fit and generated header')
    report={'schema_version':1,'analysis':metrics.ANALYSIS,
            'harmonic_missing_partial_policy':'Zero model power; same reference -50 dB mask and -70 dB floor as observed partials.',
            'split_sha256':sha(split_path),'reference_features_sha256':sha(reference_path),
            'reference_verification':verification,'renderer_sha256':sha(args.renderer),
            'sample_rate':args.sample_rate,'duration_seconds':4.4,'case_count':len(samples),
            'parameters_common':{'gain':.7,'brightness':.5,'width':.75,'tuning':440,
                          'mute':0,'sustain':0,'sostenuto':0,'soft':0},
            'fitting_used_heldouts':False,
            'fit_metadata_sha256':sha(fit_path),
            'validation_status':'Development validation: same holdout reused after train-only model correction; fresh unseen captures needed.',
            'engine_sources':{str(p.relative_to(ROOT)):sha(p) for p in sorted((ROOT/'Source/DSP').glob('*')) if p.is_file()},
            'variants':{}}
    history_path=RESEARCH/'benchmark/candidate_report_features.json'
    historical={r['id']:r for r in json.loads(history_path.read_text())['samples']}
    rows=[comparison(references[s['id']],historical[s['id']]) for s in samples]
    report['variants']['preserved_v2']={'feature_source_sha256':sha(history_path),
        'historical_renderer_sample_rate':192000,'cases':rows,'summary':summarize(rows)}
    for variant,legacy,resonance in [('fixed_attack',True,0),('measured_attack',False,0),
                                    ('product_default',False,.25)]:
        if args.variant and variant not in args.variant:
            continue
        directory=args.audio_dir/variant;directory.mkdir(parents=True,exist_ok=True)
        if not args.skip_render:
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.jobs) as pool:
                receipt=list(pool.map(lambda s:render(args.renderer,s,directory,args.sample_rate,legacy,resonance),samples))
        else:
            receipt=[{'id':s['id'],'output_sha256':sha(directory/(s['id']+'.wav'))} for s in samples]
        models,rows=[],[]
        for sample in samples:
            feature=metrics.extract_features(directory/(sample['id']+'.wav'),sample['midi'])
            models.append(feature);row=comparison(references[sample['id']],feature);rows.append(row)
            print(f"{variant} {sample['id']}: harmonic {row['harmonic_level_mae_db']:.3f}dB, attack {row['attack_rise10_90_error_ms']:.3f}ms",flush=True)
        feature_path=directory/'features.json'
        feature_path.write_text(json.dumps({'samples':models},indent=2,allow_nan=False)+'\n')
        report['variants'][variant]={'resonance':resonance,'render_receipts':receipt,
                                    'cases':rows,'summary':summarize(rows)}
    if 'fixed_attack' in report['variants'] and 'measured_attack' in report['variants']:
        baseline={r['id']:r for r in report['variants']['fixed_attack']['cases']}
        report['attack_iteration_regressions']=[{'id':r['id'],'split':r['split'],
            **{key:r[key]-baseline[r['id']][key] for key in FIELDS if r[key] is not None and baseline[r['id']][key] is not None}}
            for r in report['variants']['measured_attack']['cases']]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    with args.output.with_suffix('.csv').open('w',newline='') as destination:
        writer=csv.DictWriter(destination,fieldnames=['variant','id','split',*FIELDS],lineterminator='\n')
        writer.writeheader()
        for name,variant in report['variants'].items():
            for row in variant['cases']:
                writer.writerow({'variant':name,**{k:row[k] for k in ('id','split',*FIELDS)}})
    write_markdown(report,args.output.with_suffix('.md'))
    print(args.output)


if __name__=='__main__':
    main()
