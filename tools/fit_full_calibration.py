#!/usr/bin/env python3
"""TRAIN-only calibration tools for the original coupled full piano solver.

Writes candidate profiles/headers and reports outside Research and src. Never
changes the solver, the canonical calibration, or the locked recording split.
The original nonlinear hammer, reciprocal bridge, complex radiation phase and
complete modal topology must be retained by the candidate renderer.
"""
from __future__ import annotations
import argparse
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys

import numpy as np
from scipy import optimize, signal

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT/'Research/GrandPianoV2'
PARTIALS = 64
DEFAULT_REFERENCE = ROOT/'References/GrandFullRange/combined_train_features.json'
DEFAULT_SPLIT = ROOT/'References/GrandFullRange/split.json'
DEFAULT_BASE = RESEARCH/'benchmark/calibration.json'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# Reuse the frozen estimators and original smooth positive radiation field fit.
# This changes only imported module memory; no Research file is written.
sys.path.insert(0, str(RESEARCH/'tools'))
benchmark = load_module('keyra_full_fit_benchmark', RESEARCH/'tools/benchmark.py')
original = load_module('keyra_full_fit_radiation', RESEARCH/'tools/radiation_fit.py')
mechanics_helper = load_module('keyra_full_fit_mechanics', RESEARCH/'tools/fit_calibration.py')


def safe_output(path):
    path = Path(path).resolve()
    for protected in (ROOT/'Research', ROOT/'src', ROOT/'References'):
        if path == protected or protected in path.parents:
            raise ValueError(f'Refuse to write a canonical/source/reference path: {path}')
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path, value):
    safe_output(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def read_json(path):
    return json.loads(Path(path).read_text())


def input_record(path):
    return {'path': str(Path(path).resolve()), 'sha256': sha(path)}


def training_inputs(reference_path, split_path):
    document = read_json(reference_path)
    split = read_json(split_path)
    expected = set(split.get('combined_training_ids', split.get('training_ids', [])))
    rows = document['samples']
    if any(document.get(k) is True for k in ('fresh_reserved_recordings_opened','fresh_evaluation_audio_opened','reserved_recordings_opened_for_feature_extraction')):
        raise ValueError('Refuse a training export that opened reserved evaluation audio')
    ids = [r['id'] for r in rows]
    if not expected or len(ids) != len(set(ids)) or set(ids) != expected:
        raise ValueError('Feature inventory must equal the locked training inventory')
    for row in rows:
        _, inferred, layer = benchmark.identity(row['id']+'.wav')
        if row.get('split') != 'train' or layer not in (4, 12) or row['layer'] != layer or row['midi'] != inferred:
            raise ValueError(f'Refuse non-training or inconsistent reference row: {row["id"]}')
        if row.get('role', 'train') != 'train' or row.get('expanded_role', 'train') != 'train' or row.get('full_range_role','train')!='train':
            raise ValueError(f'Refuse reserved reference row: {row["id"]}')
    forbidden = set(split.get('reserved_fresh_evaluation_ids', [])) | set(split.get('fresh_validation_ids', []))
    if set(ids) & forbidden:
        raise ValueError('Reserved evaluation row entered training')
    if document.get('split_sha256') and document['split_sha256'] != sha(split_path):
        raise ValueError('Feature document and locked split hash disagree')
    notes = sorted({int(r['midi']) for r in rows})
    if len(notes) < 2 or any({r['layer'] for r in rows if r['midi'] == n} != {4, 12} for n in notes):
        raise ValueError('Every anchor requires exactly the two locked training layers4/12')
    return sorted(rows, key=lambda r: (r['midi'], r['layer'])), notes


def provenance(reference, split, more=()):
    paths = [Path(__file__), Path(reference), Path(split), RESEARCH/'tools/fit_calibration.py',
             RESEARCH/'tools/radiation_fit.py', RESEARCH/'tools/benchmark.py',
             RESEARCH/'reference/manifest.json',RESEARCH/'reference/fetch_reference.py',
             ROOT/'References/GrandFullRange/manifest.json',ROOT/'tools/extract_full_range_grand.py',
             ROOT/'tools/full_range_pitch.py',ROOT/'tools/fetch_full_range_grand.py',*map(Path, more)]
    return {'inputs': [input_record(p) for p in dict.fromkeys(paths)],
            'heldout_measurements_used': False,
            'fresh_evaluation_audio_opened': False,
            'interpretation': 'Effective parameters of a coupled instrument and recording chain, not unique material or hammer identification.'}


def verify_inputs(record):
    for item in record['inputs']:
        if sha(item['path']) != item['sha256']:
            raise RuntimeError(f'Input changed during operation: {item["path"]}')


def validate_profile(profile):
    keys = profile['keys']
    notes = [k['midi'] for k in keys]
    if len(keys) < 2 or notes != sorted(set(notes)) or min(notes) < 21 or max(notes) > 108:
        raise ValueError('Profile anchors must be unique, sorted, and in the88-key range')
    for k in keys:
        for field in ('f1_hz', 'B', 'hardness', 'velocity_exponent', 'detune_scale'):
            if not np.isfinite(k[field]) or k[field] <= 0:
                raise ValueError(f'Nonpositive/nonfinite{field} at MIDI{k["midi"]}')
        for field in ('sigma_late', 'sigma_prompt', 'radiation_db', 'radiation_after_db'):
            values = np.asarray(k[field], float)
            if values.shape != (PARTIALS,) or not np.isfinite(values).all():
                raise ValueError(f'Invalid{field} at MIDI{k["midi"]}')
            if field.startswith('sigma') and np.any(values <= 0):
                raise ValueError('Mechanical losses must remain positive')
        if np.any(np.asarray(k['sigma_prompt']) < np.asarray(k['sigma_late'])):
            raise ValueError('Prompt loss must be at least intrinsic late loss')


def generate_header(profile, path):
    validate_profile(profile)
    def number(x): return format(float(x), '.17g')
    def array(xs): return '{'+','.join(map(number, xs))+'}'
    rows = []
    for k in profile['keys']:
        values = [str(k['midi'])]+[number(k[f]) for f in ('f1_hz','B','hardness','velocity_exponent','detune_scale')]
        values += [array(k[f]) for f in ('sigma_late','sigma_prompt','radiation_db','radiation_after_db')]
        rows.append('{'+','.join(values)+'}')
    content = '''// Generated by tools/fit_full_calibration.py; locked TRAIN only.
// Variable anchors require the candidate Cal integration in docs/FULL_CALIBRATION.md.
#pragma once
#include <array>
namespace piano_calibration {
constexpr int partials=64;
struct Anchor {int note;double f1,B,hardness,velocityExponent,detuneScale;
 std::array<double,partials> late,prompt,radiationDb,radiationAfterDb;};
constexpr bool radiationEnabled='''+str(bool(profile.get('radiation_enabled'))).lower()+''';
constexpr std::array<Anchor,'''+str(len(rows))+'''> anchors={{
'''+',\n'.join(rows)+'''\n}};
} // namespace piano_calibration
'''
    safe_output(path).write_text(content)


def prior_at(profile, note):
    keys = profile['keys']
    notes = np.array([k['midi'] for k in keys])
    result = {'midi': note}
    for field in ('hardness', 'velocity_exponent', 'detune_scale'):
        # Physical positive priors have endpoint extension. The measured new
        # anchors, not an extrapolated regression, provide range evidence.
        result[field] = float(np.exp(np.interp(note, notes, np.log([k[field] for k in keys]))))
    j=max(0,min(len(keys)-2,int(np.searchsorted(notes,note,side='right'))-1))
    t=(note-notes[j])/float(notes[j+1]-notes[j])
    result['B']=float(np.clip(np.exp((1-t)*np.log(keys[j]['B'])+t*np.log(keys[j+1]['B'])),2e-5,.025))
    if note<notes[0]:result['B']=float(keys[0]['B']*2**((notes[0]-note)/18.))
    cents = [1200*math.log2(k['f1_hz']/(440*2**((k['midi']-69)/12))) for k in keys]
    result['f1_hz'] = 440*2**((note-69+float(np.clip((1-t)*cents[j]+t*cents[j+1],-25,30))/100)/12)
    for field in ('sigma_late', 'sigma_prompt', 'radiation_db', 'radiation_after_db'):
        source = np.array([k.get(field,k['radiation_db']) for k in keys])
        log = field.startswith('sigma')
        if log: source = np.log(source)
        values = np.array([np.interp(note, notes, source[:,n]) for n in range(PARTIALS)])
        result[field] = ((np.exp(values)*2**(max(0,note-notes[-1])/24.)) if log else values).tolist()
    return result


def fit_mechanics(rows, base):
    keys, diagnostics = [], []
    for note in sorted({r['midi'] for r in rows}):
        rr = [r for r in rows if r['midi'] == note]
        key = prior_at(base, note)
        # Limited/fallback f1/B fits must not turn a placeholder into measured
        # stiffness. In particular C8 often has too few prominent upper peaks.
        pitch = [r for r in rr if r.get('confidence') == 'good' and r.get('B_identifiable',False)
                 and r.get('fit_partial_count',0) >= 4 and r.get('rms_residual_cents',1e9) < 4]
        if pitch:
            key['f1_hz'] = float(np.median([r['f1_hz'] for r in pitch]))
            key['B'] = float(np.clip(np.median([r['B'] for r in pitch]), 2e-5, .025))
        else:
            # A measured dominant fundamental can still constrain tuning when
            # B cannot be identified. Only an observed first peak is accepted.
            fundamentals = [p['hz'] for r in rr for p in r.get('measured_partial_peaks',[]) if p['n']==1]
            nominal=440*2**((note-69)/12)
            # The frozen estimator returns a detected fundamental even when
            # there are too few upper peaks for B. Its no-peak placeholder is
            # exactly nominal: never count that placeholder as a measurement.
            fundamentals += [r['f1_hz'] for r in rr if not r.get('B_identifiable',False)
                and abs(1200*math.log2(r['f1_hz']/nominal))>1e-6]
            if fundamentals: key['f1_hz'] = float(np.median(fundamentals))
        cents = 1200*math.log2(key['f1_hz']/(440*2**((note-69)/12)))
        key['f1_hz'] = 440*2**((note-69+np.clip(cents,-70.,70.)/100)/12)
        detail = {'midi':note, 'training_ids':[r['id'] for r in rr], 'good_pitch_fits':len(pitch),
                  'B_source':'measured' if pitch else 'inherited positive prior',
                  'pitch_identity_ambiguous':any(r.get('pitch_identity_ambiguous',False) for r in rr),
                  'frequency_interpretation':'Candidate carrier/key-family frequency; no unassigned dominant component is forced into f1.',
                  'unassigned_components_hz':[c['frequency_hz'] for r in rr for c in r.get('unassigned_components',[])],
                  'unclipped_tuning_cents':cents, 'tuning_clipped_to_engine_bounds':bool(cents < -70 or cents > 70),
                  'accepted_loss_observations':{}, 'observed_partial_orders':sorted({p['n'] for r in rr for p in r['partials']})}
        losses = {}
        for stage, field, upper in (('late','sigma_late',14.), ('early','sigma_prompt',18.)):
            values, weights, accepted = [], [], 0
            for n in range(1,PARTIALS+1):
                observed, quality = [], []
                for r in rr:
                    p = next((p for p in r['partials'] if p['n'] == n),None)
                    if p is None or p['relative_db'][0] < -45: continue
                    d = p['decay'].get(stage)
                    if not d or d['slope_db_per_second'] >= -.3 or d['r_squared'] < .15: continue
                    # A late trace that has reached a persistent floor does not
                    # identify physical loss: require useful power in both late
                    # windows and no flattening to an essentially fixed floor.
                    if stage == 'late' and min(p['relative_db'][2:]) < -45: continue
                    observed.append(float(np.clip(d['amplitude_sigma_per_second'],.06,15.)))
                    quality.append(float(np.clip(d['r_squared'],0.,1.)))
                values.append(float(np.average(observed,weights=quality)) if observed else key[field][n-1])
                weights.append(sum(quality)); accepted += len(observed)
            # Original positive log-loss smoothing, but use the inherited full
            # field where new recordings do not identify a partial, not an
            # arbitrary extra high-frequency branch or noise component.
            prior = np.log(np.asarray(key[field]))
            fitted = np.exp(mechanics_helper.regularized(np.log(values),weights,prior,.65))
            losses[field] = np.clip(fitted,.08 if stage=='late' else .12,upper)
            detail['accepted_loss_observations'][stage] = accepted
        key['sigma_late'] = losses['sigma_late'].tolist()
        key['sigma_prompt'] = np.clip(np.maximum(losses['sigma_prompt'],losses['sigma_late']*1.1),.12,18.).tolist()
        keys.append(key); diagnostics.append(detail)
    return keys, diagnostics



def gram_windows(stems_dir,item,reference):
    """The original stereo Hann Gram estimator on each reference's support.

    In particular C8v4's short final window never sees an invented silent tail
    or a longer model tail. Cross terms retain the actual mechanical/radiation
    phases of all three rendered components.
    """
    arrays,files=[],[]
    sr=None
    for component in ('primary','secondary','transient'):
        path=Path(stems_dir)/(item['id']+'-'+component+'.wav')
        rate,x=benchmark.load_audio(path)
        if sr is not None and (rate!=sr or x.shape!=arrays[0].shape):raise ValueError('Stem shape/rate mismatch')
        sr=rate;arrays.append(x);files.append({'component':component,**input_record(path)})
    windows=reference.get('analysis_windows_seconds',benchmark.WINDOWS)
    if item.get('analysis_windows_seconds',windows)!=windows:raise ValueError('Reference/model power windows disagree')
    onset=int(round(item['onset_seconds']*sr))
    stop=int(round(max(hi for _,hi in windows)*sr))
    x=np.stack(arrays,axis=-1)[onset:onset+stop]
    if len(x)<stop:raise ValueError('Stem shorter than reference comparison support')
    model_wave=Path(stems_dir)/(item['id']+'.wav')
    if not model_wave.is_file():raise ValueError('Full render must accompany its stems')
    full_sr,total=benchmark.load_audio(model_wave)
    if full_sr!=sr or total.shape!=arrays[0].shape:raise ValueError('Full render/stem shape mismatch')
    if sha(model_wave)!=item['sha256']:raise ValueError('Model feature audio hash does not match the full stem render')
    reconstruction=float(np.sqrt(np.mean((sum(arrays)-total)**2))/max(np.sqrt(np.mean(total*total)),1e-20))
    if reconstruction>.005:raise ValueError('Stem sum does not reconstruct the measured full model')
    grams={int(p['n']):[] for p in item['partials']}
    for lo,hi in windows:
        section=x[int(lo*sr):int(hi*sr)];count=len(section)
        window=signal.windows.hann(count,sym=False)
        nfft=1<<int(math.ceil(math.log2(count*2)))
        z=np.fft.rfft(section*window[:,None,None],n=nfft,axis=0)
        matrix=np.einsum('fci,fcj->fij',z,z.conjugate()).real/x.shape[1]
        matrix*=2/(nfft*np.sum(window*window));matrix[0]*=.5;matrix[-1]*=.5
        f=np.fft.rfftfreq(nfft,1/sr);df=f[1]-f[0]
        for partial in item['partials']:
            center=partial['frequency_hz'];width=min(.38*item['f1_hz'],max(3/(hi-lo),.004*center))
            weights=np.clip((np.minimum(f+df/2,center+width)-np.maximum(f-df/2,center-width))/df,0,1)
            valid=weights>0
            grams[int(partial['n'])].append(np.einsum('f,fij->ij',weights[valid],matrix[valid]))
    return {n:np.asarray(g) for n,g in grams.items()},{'id':item['id'],'files':files,
        'full_render':input_record(model_wave),'sum_reconstruction_relative_rms_error':reconstruction,'analysis_windows_seconds':windows}


def fit_radiation(rows, models, basis_rows, stems_dir, profile_keys=None, quality_rows=()):
    notes = sorted({r['midi'] for r in rows})
    original.NOTES = notes
    model_map = {r['id']:r for r in models}
    if set(model_map) != {r['id'] for r in rows}:
        raise ValueError('Model feature inventory must equal TRAIN reference inventory')
    basis = original._basis_index(basis_rows)
    global_gain_db = float(np.median([20*math.log10(r['early_rms']/model_map[r['id']]['early_rms']) for r in rows]))
    global_gain = 10**(global_gain_db/20)
    gram_data, stem_records = {}, []
    for ref in rows:
        item = model_map[ref['id']]
        gram_data[item['id']], record = gram_windows(stems_dir,item,ref)
        stem_records.append(record)
    quality={(r['id'],r['partial'],r['window_index']):r for r in quality_rows}
    excluded=[]
    observations = []
    lower, upper = np.log(original.GAIN_LIMITS)
    for note in notes:
        rr = [r for r in rows if r['midi']==note]
        for n in range(1,PARTIALS+1):
            base = [original._basis_value(basis,note,n,pol) for pol in (0,1)]
            if not all(x is not None and x>1e-8 for x in base): continue
            target, matrices, weights = [], [], []
            for ref in rr:
                rp = next((p for p in ref['partials'] if p['n']==n),None)
                mp = next((p for p in model_map[ref['id']]['partials'] if p['n']==n),None)
                if rp is None or mp is None: continue
                for j, gram in enumerate(gram_data[ref['id']][n]):
                    q=quality.get((ref['id'],n,j))
                    if q is not None and not q['accepted_for_radiation_fit']:
                        excluded.append(q)
                        continue
                    relative = rp['powers'][j]/ref['early_rms']**2
                    if relative<1e-5: continue
                    model_power = max(float(gram[0,0]+gram[1,1]),1e-24)
                    if model_power/model_map[ref['id']]['early_rms']**2<1e-7: continue
                    target.append(rp['powers'][j]/global_gain**2)
                    matrices.append(gram)
                    weights.append(float(np.clip((10*math.log10(relative)+50)/30,.1,1))*[1.,1.,.8,.6][j])
            if len(target)<3: continue
            target, matrices, weights = map(np.asarray,(target,matrices,weights))
            def prediction(theta):
                g = np.r_[np.exp(theta),1.]
                return np.maximum(np.einsum('i,nij,j->n',g,matrices,g),1e-24)
            def residual(theta,regularize=True):
                value = np.sqrt(weights)*10*np.log10(prediction(theta)/target)
                if regularize:
                    db = theta*20/math.log(10)
                    value = np.r_[value,.04*db[0],.08*db[1]]
                return value
            estimate = float(np.clip(np.sqrt(np.median(target/prediction(np.zeros(2)))),.05,20.))
            candidates = [optimize.least_squares(residual,np.log([estimate,min(39.,estimate*s)]),
                          bounds=([lower,lower],[upper,upper]),loss='soft_l1',f_scale=3.,max_nfev=160) for s in (1.,8.,24.)]
            fitted = min(candidates,key=lambda result:result.cost)
            gains = np.exp(fitted.x)
            jacobian = fitted.jac[:len(target)]
            singular = np.linalg.svd(jacobian,compute_uv=False)
            condition = float(singular[-1]/max(singular[0],1e-20))
            relative_weights = np.clip(np.linalg.norm(jacobian,axis=0)/20,0,1)
            relative_weights[1] *= min(1.,condition/.025)
            error = float(np.sqrt(np.mean(residual(fitted.x,False)**2)))
            relative_weights *= 1/(1+(error/8)**2)
            for pol in (0,1):
                neighborhood = [original._basis_value(basis,note,j,pol) for j in range(max(1,n-3),n+4)]
                neighborhood = [x for x in neighborhood if x is not None and x>0]
                relative_weights[pol] *= min(1.,base[pol]/max(float(np.median(neighborhood))*.18,1e-20))
            row = basis[note,n,0]
            observations.append({'midi':note,'n':n,'frequency_hz':float(row['frequency_hz']),
                'base_H':base,'gains':gains.tolist(),'gains_db':(20*np.log10(gains)).tolist(),
                'target_db':(20*np.log10(np.asarray(base)*gains)).tolist(),'weights':relative_weights.tolist(),
                'jacobian_singular_ratio':condition,'valid_power_observations':len(target),
                'fit_weighted_rmse_db':error,
                'baseline_weighted_rmse_db':float(np.sqrt(np.mean(residual(np.zeros(2),False)**2))),
                'bound_hit':bool(np.any(gains<.026) or np.any(gains>39.9)),
                '_matrices':matrices,'_targets':target,'_timeweights':weights})
    if not observations: raise ValueError('No identifiable TRAIN radiation observations')
    grid = np.linspace(math.log2(min(30.,.9*min(r['f1_hz'] for r in rows))),math.log2(20000),32)
    grids, priors, offsets = [], [], []
    for pol in (0,1):
        coefficients, prior, offset = original._smooth_targets(observations,basis,grid,pol)
        grids.append(coefficients);priors.append(prior);offsets.append(offset)
    grids, joint = original._joint_refinement(observations,grids,priors,offsets,grid)
    keys = []
    for k,note in enumerate(notes):
        ref = next(r for r in rows if r['midi']==note)
        tuning = next((r for r in profile_keys if r['midi']==note),ref) if profile_keys is not None else ref
        orders = np.arange(1,PARTIALS+1)
        frequencies = tuning['f1_hz']*orders*np.sqrt((1+tuning['B']*orders*orders)/(1+tuning['B']))
        fields = [np.interp(np.log2(frequencies),grid,curve[k]).tolist() for curve in grids]
        keys.append({'midi':note,'radiation_db':fields[0],'radiation_after_db':fields[1]})
    for o in observations:
        k = notes.index(o['midi'])
        db = np.array([np.interp(math.log2(o['frequency_hz']),grid,curve[k]) for curve in grids])
        gain = np.clip(10**(db/20)/o['base_H'],*original.GAIN_LIMITS)
        g = np.r_[gain,1.]
        prediction = np.maximum(np.einsum('i,nij,j->n',g,o['_matrices'],g),1e-24)
        error = np.sqrt(o['_timeweights'])*10*np.log10(prediction/o['_targets'])
        o['regularized_gains'] = gain.tolist()
        o['regularized_weighted_rmse_db'] = float(np.sqrt(np.mean(error*error)))
        for field in ('_matrices','_targets','_timeweights'):del o[field]
    return {'keys':keys,'global_reference_gain_db':global_gain_db,
            'training_ids':sorted(r['id'] for r in rows),'heldout_measurements_used':False,
            'method':'Original bounded positive two-polarization joint Gram-power fit with variable TRAIN anchors; complex radiation phase retained.',
            'frequency_grid_hz':(2**grid).tolist(),'grid_primary_db':grids[0].tolist(),
            'grid_secondary_db':grids[1].tolist(),'secondary_prior_offset_db':offsets[1],
            'stem_sources':stem_records,'joint_refinement':joint,'observations':observations,
            'excluded_ambiguous_fundamental_observations':excluded,
            'edge_fundamental_window_quality':list(quality_rows),
            'unassigned_components_not_fitted':[{'id':r['id'],**c} for r in rows for c in r.get('unassigned_components',[])],
            'unassigned_component_limit':'Current primary/secondary observation magnitudes cannot generate a distinct missing4434Hz component. It is separately measured and excluded from this fit; no forcedretune, extra pole, or broad power compensation is introduced.',
            'quality_gate':'Only individual edge H1 windows below6dB versus same-window equal-width neighboring bands are excluded; all full-envelope metrics remain reported.',
            'fit_diagnostics':{'partial_fits':len(observations),'bound_hits':sum(o['bound_hit'] for o in observations),
                **{name:float(np.median([o[field] for o in observations])) for name,field in (
                   ('median_raw_rmse_db','fit_weighted_rmse_db'),('median_regularized_rmse_db','regularized_weighted_rmse_db'),
                   ('median_before_rmse_db','baseline_weighted_rmse_db'))}}}


def reference_audio(row, feature_path):
    # Historical numeric measurements include an obsolete absolute path. Resolve
    # only this explicitly authorized TRAIN basename, never enumerate audio.
    candidates = [Path(row['path']),ROOT/row['path'],Path(feature_path).parent/'recordings'/(row['id']+'.wav'),
                  ROOT/'References/GrandFullRange/recordings'/(row['id']+'.wav'),
                  ROOT/'References/GrandExpanded/recordings'/(row['id']+'.wav'),
                  RESEARCH/'reference/wav'/(row['id']+'.wav')]
    for path in candidates:
        if path.is_file() and sha(path)==row['sha256']:return path
    # Rebuilt WAV containers can differ while the authenticated PCM is exact.
    # Require the original feature->historical manifest link, the same source
    # FLAC identity, both manifests' identical PCM receipt, and actual decoded
    # PCM equality. A basename match alone never authorizes this fallback.
    old_manifest=read_json(RESEARCH/'reference/manifest.json')
    manifest=read_json(ROOT/'References/GrandFullRange/manifest.json')
    old=next((r for r in old_manifest['samples'] if r['id']==row['id']),None)
    current=next((r for r in manifest['samples'] if r['id']==row['id']),None)
    if (old is not None and current is not None and row.get('split')=='train' and row.get('layer') in (4,12)
        and current.get('role')=='train' and old.get('wav_sha256')==row['sha256']
        and old.get('flac_sha256')==current.get('flac_sha256') and old.get('decoded_pcm')==current.get('decoded_pcm')):
        path=ROOT/'References/GrandFullRange'/current['wav_path']
        if path.is_file() and sha(path)==current['wav_sha256']:
            pcm=load_module('keyra_full_fit_pcm',RESEARCH/'reference/fetch_reference.py')
            if pcm.decoded_pcm_identity(path)==old['decoded_pcm']:return path
    raise ValueError(f'No hash/decoded-PCM-matching TRAIN audio found for {row["id"]}')


def reference_audio_identity(row,path):
    """Receipt for reference_audio's historical-container/actual-PCM link."""
    actual=sha(path)
    receipt={'id':row['id'],'historical_feature_wave_sha256':row['sha256'],
             'actual_wave_path':str(Path(path).resolve()),'actual_wave_sha256':actual,
             'container_hash_matches_feature':actual==row['sha256']}
    if actual!=row['sha256']:
        pcm=load_module('keyra_full_fit_pcm_receipt',RESEARCH/'reference/fetch_reference.py')
        receipt['decoded_pcm']=pcm.decoded_pcm_identity(Path(path))
        receipt['identity_basis']='Historical manifest links feature WAV hash to the same FLAC and decoded PCM as authenticated current TRAIN manifest; actual decoded PCM checked.'
    else:receipt['identity_basis']='Exact feature WAV container SHA256.'
    return receipt



def edge_window_quality(rows,feature_path):
    result,sources=[],[]
    for row in rows:
        if not (row['f1_hz']<31.25 or row['midi']>=96):continue
        path=reference_audio(row,feature_path);sources.append(input_record(path))
        sr,x=benchmark.load_audio(path);x=x[int(round(row['onset_seconds']*sr)):]
        for j,(lo,hi) in enumerate(row.get('analysis_windows_seconds',benchmark.WINDOWS)):
            f,p=benchmark.spectrum(x[int(lo*sr):int(hi*sr)],sr)
            center=row['f1_hz'];width=min(.38*center,max(3/(hi-lo),.004*center))
            power=benchmark.integrated_power(f,p,center-width,center+width)
            adjacent=(benchmark.integrated_power(f,p,center-3*width,center-2*width)
                      +benchmark.integrated_power(f,p,center+2*width,center+3*width))
            prominence=10*math.log10(max(power,1e-30)/max(adjacent,1e-30))
            result.append({'id':row['id'],'partial':1,'window_index':j,'window_seconds':[lo,hi],
                'band_hz':[center-width,center+width],'band_to_equal_width_neighbor_bands_db':prominence,
                'accepted_for_radiation_fit':bool(prominence>=6.),
                'reason':'Require6dB prominence over same-window neighboring bands for an ambiguous edge fundamental; not a measured SNR/noise floor.'})
    return result,sources


def attack_measurement(x, sr, early_rms):
    onset,_ = benchmark.onset_index(x,sr)
    x = x[onset:]
    if len(x)<int(.75*sr):raise ValueError('Need at least0.75s after onset for the fixed gain')
    result = []
    for lo,hi in ((.0,.005),(.005,.020),(.020,.050),(.050,.100)):
        section = x[int(lo*sr):int(hi*sr)]
        f,p = benchmark.spectrum(section,sr)
        bands = [benchmark.integrated_power(f,p,a,b)/early_rms**2 for a,b in ((31.25,250),(250,1000),(1000,4000),(4000,12000),(12000,19000))]
        active = (f>=250)&(f<min(19000,sr*.44))
        centroid = float(f[active]@p[active]/max(np.sum(p[active]),1e-30))
        rms = float(np.sqrt(np.mean(section*section)))
        crest = 20*math.log10(max(float(np.max(abs(section))),1e-30)/max(rms,1e-30))
        result.append({'window_seconds':[lo,hi],'normalized_band_power':bands,
                       'centroid_250_19000_hz':centroid,'crest_db':crest,
                       'power_over_steady_rms_db':20*math.log10(max(rms,1e-30)/early_rms)})
    return result


def emit_profile(profile, output):
    validate_profile(profile)
    out = Path(output)
    write_json(out/'calibration.json',profile)
    generate_header(profile,out/'calibration.h')




def joint_stiffness_proposal(rows,profile,note):
    key=next((k for k in profile['keys'] if k['midi']==note),None)
    if key is None:raise ValueError('No proposed anchor')
    observed=[(r['id'],p) for r in rows if r['midi']==note for p in r.get('measured_partial_peaks',[])]
    if len(observed)<6 or len({p['n'] for _,p in observed})<3:raise ValueError('Joint proposal requires three observed partial orders at both velocities')
    if any(r.get('confidence')=='good' for r in rows if r['midi']==note):raise ValueError('This uncertain proposal is only for limited high-register pitch fits')
    orders=np.array([p['n'] for _,p in observed],float)
    frequencies=np.array([p['hz'] for _,p in observed],float)
    weights=np.clip(10**(np.array([p['relative_peak_db'] for _,p in observed])*.015),.2,1.)
    # Fundamental is directly observed and remains fixed. The one B parameter
    # is shared by both training strikes. Robust loss exposes inconsistent
    # upper peaks rather than silently identifying separate string materials.
    def residual(value):
        predicted=key['f1_hz']*orders*np.sqrt((1+value[0]*orders*orders)/(1+value[0]))
        return weights*1200*np.log2(predicted/frequencies)
    fit=optimize.least_squares(residual,[min(key['B'],.01)],bounds=([2e-5],[.025]),
          loss='soft_l1',f_scale=3.,xtol=1e-12,ftol=1e-12,gtol=1e-12,max_nfev=200)
    proposed=float(fit.x[0]);predicted=key['f1_hz']*orders*np.sqrt((1+proposed*orders*orders)/(1+proposed))
    errors=1200*np.log2(predicted/frequencies)
    return {'midi':note,'prior_B':key['B'],'proposed_B':proposed,'fundamental_hz_fixed':key['f1_hz'],
        'individual_limited_B_fits':[{'id':r['id'],'B':r['B']} for r in rows if r['midi']==note],
        'method':'One shared bounded B; fixed observed fundamental; robust joint cents fit over both TRAIN velocities; relative peak weights clipped0.2–1.',
        'B_identified_as_unique_physical_material':False,'converged':bool(fit.success),
        'peak_residuals':[{'id':name,'n':p['n'],'observed_hz':p['hz'],'predicted_hz':float(hz),'residual_cents':float(error),'weight':float(weight)}
                          for (name,p),hz,error,weight in zip(observed,predicted,errors,weights)],
        'rms_residual_cents':float(np.sqrt(np.mean(errors*errors))),
        'limits':'Only three partials per strike; upper peaks disagree across layers and may be weak/nonharmonic. This is one TRAIN proposal for actual-render comparison, not an accepted measurement or a default.'}


def build_candidate(source):
    text=Path(source).read_text()
    replacements=[(
      'double cents=std::clamp(lerp(centsA,centsB,cal.t),-25.0,30.0);',
      'double cents=std::clamp(lerp(centsA,centsB,cal.t),-70.0,70.0);',
      'Allow directly observed TRAIN tuning within the frozen pitch extractor search bounds.'),(
      'explicit Cal(int note){lo=std::clamp((note-36)/12,0,3);hi=lo+1;t=(note-piano_calibration::anchors[lo].note)/12.0;}',
      'explicit Cal(int note){lo=0;hi=1;while(hi+1<(int)piano_calibration::anchors.size()&&note>=piano_calibration::anchors[hi].note){++lo;++hi;}t=(note-piano_calibration::anchors[lo].note)/(double)(piano_calibration::anchors[hi].note-piano_calibration::anchors[lo].note);}',
      'Use the sorted measured anchor notes and actual semitone distances.'),(
      'if(n<36)k.B=piano_calibration::anchors[0].B*std::pow(2.0,(36-n)/18.0);',
      'if(n<piano_calibration::anchors.front().note)k.B=piano_calibration::anchors.front().B*std::pow(2.0,(piano_calibration::anchors.front().note-n)/18.0);',
      'Apply bass stiffness extrapolation only outside measured anchors.'),(
      'if(n>84)late*=std::pow(2.0,(n-84)/24.0);',
      'if(n>piano_calibration::anchors.back().note)late*=std::pow(2.0,(n-piano_calibration::anchors.back().note)/24.0);',
      'Apply treble intrinsic-loss extrapolation only outside measured anchors.'),(
      'if(n>84){late*=std::pow(2.0,(n-84)/24.0);fast*=std::pow(2.0,(n-84)/24.0);}',
      'if(n>piano_calibration::anchors.back().note){late*=std::pow(2.0,(n-piano_calibration::anchors.back().note)/24.0);fast*=std::pow(2.0,(n-piano_calibration::anchors.back().note)/24.0);}',
      'Apply treble common-unison loss extrapolation only outside measured anchors.')]
    records=[]
    for before,after,reason in replacements:
        if text.count(before)!=1:raise ValueError('Candidate integration expects exactly one original site: '+before)
        text=text.replace(before,after)
        records.append({'before':before,'after':after,'reason':reason})
    return text,records



def validate_render_manifest(manifest_path,rows,reference_path,split_path,profile_header,stems_dir):
    """Bind the selected complete batch to actual immutable inputs and WAVs."""
    manifest=read_json(manifest_path)
    if manifest.get('complete') is not True or manifest.get('errors') or manifest.get('stems') is not True:
        raise ValueError('Radiation requires a complete error-free stem batch')
    expected_ids={r['id'] for r in rows}
    records=manifest.get('renders',[])
    if len(records)!=len(expected_ids) or {r['id'] for r in records}!=expected_ids:
        raise ValueError('Stem manifest must contain each locked TRAIN ID exactly once')
    expected={'calibration_sha256':sha(profile_header),'reference_features_sha256':sha(reference_path),
              'split_sha256':sha(split_path),'training_guard_sha256':sha(Path(__file__))}
    source=Path(manifest.get('source_path',''));engine=Path(manifest.get('engine_path',''))
    if not source.is_file() or not engine.is_file():raise ValueError('Manifest source and binary paths must exist')
    expected.update(source_sha256=sha(source),engine_sha256=sha(engine))
    if sha(source.parent/'calibration.h')!=expected['calibration_sha256']:
        raise ValueError('Actual solver header differs from the selected analytic profile header')
    if any(manifest.get(k)!=v for k,v in expected.items()):raise ValueError('Stem manifest input/source/binary/profile/split/guard hashes differ from actual files')
    checked=[input_record(source),input_record(engine),input_record(profile_header),input_record(source.parent/'calibration.h')]
    reference_map={r['id']:r for r in rows}
    for record in records:
        if any(record.get('inputs',{}).get(k)!=v for k,v in expected.items()):
            raise ValueError('Per-render input identities disagree with the batch: '+record['id'])
        name=record['id'];paths=[Path(stems_dir)/(name+suffix+'.wav') for suffix in ('','-primary','-secondary','-transient')]
        if set(record.get('output_sha256',{}))!={p.name for p in paths}:
            raise ValueError('Per-render output inventory must contain full plus exactly three stems: '+name)
        for path in paths:
            if not path.is_file() or sha(path)!=record['output_sha256'][path.name]:
                raise ValueError('Actual full/stem WAV does not match manifest: '+str(path))
            checked.append(input_record(path))
        events=Path(stems_dir)/(name+'.events')
        if not events.is_file() or sha(events)!=record['inputs'].get('score_sha256'):
            raise ValueError('Actual event file does not match manifest: '+name)
        lines=[line.split() for line in events.read_text().splitlines() if line.strip() and not line.lstrip().startswith('#')]
        reference=reference_map[name]
        expected_events=[(0.1,'on',reference['midi'],reference['midi_velocity']),(4.15,'off',reference['midi'],0)]
        try:actual=[(float(v[0]),v[1],int(v[2]),float(v[3])) for v in lines if len(v)==4]
        except (ValueError,IndexError) as error:raise ValueError('Invalid training event file: '+name) from error
        if len(actual)!=len(lines) or actual!=expected_events:raise ValueError('Rendered controls do not match the locked held-note policy: '+name)
        checked.append(input_record(events))
        metrics=record.get('metrics',{})
        if metrics.get('nonfinite_samples')!=0 or metrics.get('string_count')!=230 or metrics.get('board_modes')!=475:
            raise ValueError('Render metrics violate finite/full-physics requirements: '+name)
    return {'manifest':input_record(manifest_path),'rendered_training_ids':sorted(expected_ids),
            'validated_full_and_stem_wavs':len(records)*4,'validated_event_files':len(records),
            'all_inputs_and_outputs_match_actual_files':True},checked


def spurious_model_bands(reference,model):
    """Diagnostic only; keep the preserved reference-masked metrics unchanged."""
    observed=np.asarray(reference['band_power'])/reference['early_rms']**2
    predicted=np.asarray(model['band_power'])/model['early_rms']**2
    observed_db=10*np.log10(np.maximum(observed,1e-30));predicted_db=10*np.log10(np.maximum(predicted,1e-30))
    selected=np.argwhere((predicted_db>-30.)&(observed_db<-50.))
    windows=reference.get('analysis_windows_seconds',benchmark.WINDOWS)
    edges=reference['band_edges_hz']
    return [{'window_index':int(j),'window_seconds':windows[j],'band_index':int(k),
             'band_hz':[edges[k],edges[k+1]],'reference_relative_db':float(observed_db[j,k]),
             'model_relative_db':float(predicted_db[j,k]),'model_minus_reference_db':float(predicted_db[j,k]-observed_db[j,k])}
            for j,k in selected]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference',type=Path,default=DEFAULT_REFERENCE)
    parser.add_argument('--split',type=Path,default=DEFAULT_SPLIT)
    sub = parser.add_subparsers(dest='stage',required=True)
    p = sub.add_parser('mechanics',help='Measured positive tuning/loss candidate; inherited strike/radiation priors')
    p.add_argument('--base-profile',type=Path,default=DEFAULT_BASE);p.add_argument('--output',type=Path,required=True)
    p = sub.add_parser('radiation',help='Original joint2-polarization fit from actual full-model stems')
    p.add_argument('--profile',type=Path,required=True);p.add_argument('--model-features',type=Path,required=True)
    p.add_argument('--basis',type=Path,required=True);p.add_argument('--stems-dir',type=Path,required=True)
    p.add_argument('--quality-report',type=Path,default=ROOT/'References/GrandFullRange/training-quality.json')
    p.add_argument('--exclude-ambiguous-anchors',action='store_true',help='Explicitly exclude every anchor with ambiguous pitch identity; preserve its prior observation fields unchanged')
    p.add_argument('--render-manifest',type=Path,required=True,help='Full renderer provenance with calibration_sha256 and all TRAIN render IDs')
    p.add_argument('--output',type=Path,required=True)
    p = sub.add_parser('analytic',help='Disable only fitted observation magnitudes for the final Gram-basis render')
    p.add_argument('--profile',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p = sub.add_parser('build',help='Create a candidate-only solver/header with variable-anchor interpolation')
    p.add_argument('--profile',type=Path,required=True)
    p.add_argument('--source',type=Path,default=ROOT/'src/full_reference/grand.cpp')
    p.add_argument('--output',type=Path,required=True)
    p = sub.add_parser('stiffness-proposal',help='One uncertain joint-peak stiffness candidate for a limited high-register anchor')
    p.add_argument('--profile',type=Path,required=True);p.add_argument('--midi',type=int,default=108)
    p.add_argument('--output',type=Path,required=True)
    p = sub.add_parser('strike-bank',help='Bounded physical hammer probes; no waveform/envelope replacement')
    p.add_argument('--profile',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p = sub.add_parser('score',help='TRAIN comparison including measured0–100ms struck texture')
    p.add_argument('--renders',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--ids',nargs='+',help='Optional complete velocity pairs selected strictly from locked TRAIN IDs')
    p = sub.add_parser('header',help='Reproduce a candidate header from its JSON profile')
    p.add_argument('--profile',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    rows,notes = training_inputs(args.reference,args.split)
    if args.stage=='score' and args.ids:
        wanted=set(args.ids)
        if not wanted.issubset({r['id'] for r in rows}):raise ValueError('Score IDs must be locked TRAIN cases')
        rows=[r for r in rows if r['id'] in wanted];notes=sorted({r['midi'] for r in rows})
        if any({r['layer'] for r in rows if r['midi']==n}!={4,12} for n in notes):raise ValueError('Score subsets require complete TRAIN velocity pairs')
    if args.stage=='header':
        profile = read_json(args.profile)
        if set(profile['training_ids']) != {r['id'] for r in rows}:raise ValueError('Profile TRAIN IDs mismatch')
        generate_header(profile,args.output);print(args.output);return
    more = [getattr(args,'base_profile',None),getattr(args,'profile',None),getattr(args,'model_features',None),getattr(args,'basis',None),getattr(args,'source',None),getattr(args,'render_manifest',None),getattr(args,'quality_report',None)]
    evidence = provenance(args.reference,args.split,[p for p in more if p is not None])
    if args.stage=='mechanics':
        base = read_json(args.base_profile)
        keys,diagnostics = fit_mechanics(rows,base)
        profile = {'version':3,'model':'original coupled full solver','training_ids':sorted(r['id'] for r in rows),
                   'radiation_enabled':bool(base.get('radiation_enabled')),'keys':keys,'provenance':evidence,
                   'calibrated_tuning_bounds_cents':[-70.,70.],
                   'mechanics_diagnostics':diagnostics,
                   'fit_stage':'measured positive mechanics, inherited strike and radiation; candidate not validated',
                   'notes':'late/prompt remain positive; prompt-late acts through passive common-unison ports; no sampled pressure/IR embedded.'}
        verify_inputs(evidence);emit_profile(profile,args.output)
        print(json.dumps({'anchors':notes,'training_cases':len(rows),'output':str(args.output),'stage':profile['fit_stage']},indent=2))
    elif args.stage=='analytic':
        profile=read_json(args.profile)
        if set(profile['training_ids'])!={r['id'] for r in rows}:raise ValueError('Profile TRAIN IDs mismatch')
        profile.update(radiation_enabled=False,provenance=evidence,fit_stage='analytic complex radiation basis; physical mechanics/hammer unchanged')
        verify_inputs(evidence);emit_profile(profile,args.output);print(args.output/'calibration.h')
    elif args.stage=='build':
        profile=read_json(args.profile)
        if [k['midi'] for k in profile['keys']]!=notes or set(profile['training_ids'])!={r['id'] for r in rows}:
            raise ValueError('Profile anchors/TRAIN inventory mismatch')
        candidate,transform=build_candidate(args.source)
        verify_inputs(evidence);generate_header(profile,args.output/'calibration.h')
        safe_output(args.output/'grand.cpp').write_text(candidate)
        write_json(args.output/'candidate-source.json',{'provenance':evidence,'transforms':transform,
            'source_sha256':sha(args.output/'grand.cpp'),'calibration_sha256':sha(args.output/'calibration.h'),
            'expected_topology':{'keys':88,'strings':230,'board_modes':475},
            'status':'candidate only; compile, physical self-test, full TRAIN render/score, freeze then separate evaluation required'})
        print(args.output/'grand.cpp')
    elif args.stage=='radiation':
        profile = read_json(args.profile)
        if profile.get('radiation_enabled'):raise ValueError('Fit radiation from an analytic-observation profile/stem render; run the analytic stage first')
        if [k['midi'] for k in profile['keys']]!=notes or set(profile['training_ids'])!={r['id'] for r in rows}:
            raise ValueError('Profile anchors/TRAIN inventory mismatch')
        header=args.profile.parent/'calibration.h'
        receipt,checked=validate_render_manifest(args.render_manifest,rows,args.reference,args.split,header,args.stems_dir)
        evidence['inputs']+=checked
        excluded_notes={r['midi'] for r in rows if r.get('pitch_identity_ambiguous',False)} if args.exclude_ambiguous_anchors else set()
        fit_rows=[r for r in rows if r['midi'] not in excluded_notes]
        if len({r['midi'] for r in fit_rows})<2:raise ValueError('Too few unambiguous anchors for joint radiation fit')
        all_models=read_json(args.model_features)['samples']
        if len(all_models)!=len(rows) or {r['id'] for r in all_models}!={r['id'] for r in rows}:raise ValueError('Scored model features must contain every rendered TRAIN case')
        fit_ids={r['id'] for r in fit_rows}
        fit_models=[r for r in all_models if r['id'] in fit_ids]
        quality=read_json(args.quality_report)
        if quality['split_sha256']!=sha(args.split) or any(r.get('role')!='train' or r['id'] not in profile['training_ids'] for r in quality['samples']):
            raise ValueError('Quality report must contain TRAIN-only diagnostics from the locked split')
        window_quality,audio_sources=edge_window_quality(fit_rows,args.reference)
        evidence['inputs']+=audio_sources
        report = fit_radiation(fit_rows,fit_models,read_json(args.basis),args.stems_dir,profile['keys'],window_quality)
        fitted_keys={k['midi']:k for k in report['keys']}
        preserved={}
        for key in profile['keys']:
            if key['midi'] in fitted_keys:key.update(fitted_keys[key['midi']])
            else:preserved[str(key['midi'])]={field:list(key[field]) for field in ('radiation_db','radiation_after_db')}
        report.update(render_manifest_validation=receipt,rendered_training_ids=sorted(r['id'] for r in rows),
            fit_training_ids=sorted(fit_ids),excluded_anchor_midis=sorted(excluded_notes),
            explicit_exclude_ambiguous_anchors=bool(args.exclude_ambiguous_anchors),preserved_prior_observation_fields=preserved,
            unassigned_components_not_fitted=[{'id':r['id'],**c} for r in rows for c in r.get('unassigned_components',[])],
            fit_scope='All TRAIN cases rendered/scored; only explicitly unambiguous anchors fitted when exclusion flag is set. Excluded observation fields remain exactly the supplied prior.')
        profile['radiation_fit_scope']={k:report[k] for k in ('rendered_training_ids','fit_training_ids','excluded_anchor_midis','explicit_exclude_ambiguous_anchors')}
        profile.update(radiation_enabled=True,provenance=evidence,fit_stage='joint positive full-model radiation candidate; not evaluated')
        report['provenance']=evidence
        verify_inputs(evidence);emit_profile(profile,args.output);write_json(args.output/'radiation-fit.json',report)
        print(json.dumps(report['fit_diagnostics'],indent=2))
    elif args.stage=='stiffness-proposal':
        profile=read_json(args.profile);validate_profile(profile)
        if [k['midi'] for k in profile['keys']]!=notes or set(profile['training_ids'])!={r['id'] for r in rows}:
            raise ValueError('Profile anchors/TRAIN inventory mismatch')
        proposal=joint_stiffness_proposal(rows,profile,args.midi)
        key=next(k for k in profile['keys'] if k['midi']==args.midi)
        key['B']=proposal['proposed_B']
        profile.update(provenance=evidence,fit_stage='uncertain joint high-register stiffness proposal; requires TRAIN render comparison')
        profile['stiffness_proposal']=proposal
        verify_inputs(evidence);emit_profile(profile,args.output)
        write_json(args.output/'stiffness-proposal.json',proposal)
        print(json.dumps(proposal,indent=2))
    elif args.stage=='strike-bank':
        base = read_json(args.profile);validate_profile(base)
        if [k['midi'] for k in base['keys']]!=notes or set(base['training_ids'])!={r['id'] for r in rows}:
            raise ValueError('Profile anchors/TRAIN inventory mismatch')
        # One control at a time exposes identifiability and costs5 rendersets,
        # rather than a broad optimizer confounding hammer and radiation gains.
        probes = [('baseline',1.,0.),('softer',.8,0.),('harder',1.25,0.),('velocity-down',1.,-.08),('velocity-up',1.,.08)]
        records = []
        for name,hardness,velocity in probes:
            candidate = copy.deepcopy(base)
            for key in candidate['keys']:
                key['hardness'] = float(np.clip(key['hardness']*hardness,.25,4.))
                key['velocity_exponent'] = float(np.clip(key['velocity_exponent']+velocity,.45,1.8))
            candidate.update(provenance=evidence,fit_stage=f'physical strike probe{name}; unselected')
            out = args.output/name
            emit_profile(candidate,out)
            records.append({'name':name,'profile':str((out/'calibration.json').resolve()),'profile_sha256':sha(out/'calibration.json'),
                            'hardness_scale':hardness,'velocity_exponent_offset':velocity})
        verify_inputs(evidence)
        write_json(args.output/'strike-bank.json',{'provenance':evidence,'training_ids':base['training_ids'],'candidates':records,
                   'selection':'Render actual nonlinear solver; compare attack texture, velocity contrasts, body/passivity, then freeze. No scalar RMS-rise-only selection.'})
        print(args.output/'strike-bank.json')
    else:
        comparisons,models,attacks,sources,identities,components = [],[],[],[],[],[]
        for ref in rows:
            original_path = reference_audio(ref,args.reference)
            identities.append(reference_audio_identity(ref,original_path))
            model_path = args.renders/(ref['id']+'.wav')
            if ref.get('right_censored'):
                sys.path.insert(0,str(ROOT/'tools'))
                extractor=load_module('keyra_full_fit_censored',ROOT/'tools/extract_full_range_grand.py')
                model=extractor.censored_features(model_path.resolve(),ref['midi'],benchmark,
                    analysis_windows_seconds=ref['analysis_windows_seconds'],
                    envelope_times_seconds=ref['envelope_times_seconds'],
                    max_analysis_seconds=ref['available_seconds_after_onset'])
            else:model = benchmark.extract_features(model_path,ref['midi'])
            model['split']='train'
            if model['layer'] != ref['layer']:raise ValueError('Model layer mismatch')
            models.append(model)
            comparison=benchmark.compare_features(ref,model)
            model_peaks={p['n']:p for p in model.get('measured_partial_peaks',[])}
            comparison['spurious_prominent_model_bands']=spurious_model_bands(ref,model)
            comparison['observed_peak_tuning']=[{'n':p['n'],'reference_hz':p['hz'],'model_hz':model_peaks[p['n']]['hz'],
                'error_cents':1200*math.log2(model_peaks[p['n']]['hz']/p['hz']),
                'reference_relative_peak_db':p['relative_peak_db']} for p in ref.get('measured_partial_peaks',[]) if p['n'] in model_peaks]
            comparisons.append(comparison)
            sr,x=benchmark.load_audio(original_path);msr,mx=benchmark.load_audio(model_path)
            if ref.get('unassigned_components'):
                sys.path.insert(0,str(ROOT/'tools'))
                extractor=load_module('keyra_full_fit_components',ROOT/'tools/extract_full_range_grand.py')
                monset,_=benchmark.onset_index(mx,msr)
                support=ref.get('available_seconds_after_onset',4.)
                aligned=mx[monset:monset+int(math.ceil(min(4.,support)*msr-1e-8))]
                model['unassigned_components']=[extractor.component_features(aligned,msr,c['frequency_hz'],
                    c['analysis_windows_seconds'],model['early_rms']**2,ref['f1_hz'],benchmark) for c in ref['unassigned_components']]
                gain=ref['early_rms']/model['early_rms']
                for rc,mc in zip(ref['unassigned_components'],model['unassigned_components']):
                    target=np.asarray(rc['powers']);predicted=np.asarray(mc['powers'])*gain*gain
                    errors=10*np.log10(np.maximum(predicted,1e-30)/np.maximum(target,1e-30))
                    components.append({'id':ref['id'],'frequency_hz_fixed_to_reference':rc['frequency_hz'],
                        'physical_identity':'unassigned/unknown','analysis_windows_seconds':rc['analysis_windows_seconds'],
                        'reference':rc,'model':mc,'fixed_early_gain_power_error_db':errors.tolist(),
                        'reference_prominent_window_mask':(np.asarray(rc['relative_db'])>-50).tolist(),
                        'included_in_radiation_fit':False,'forced_into_string_f1':False})
            reference_attack=attack_measurement(x,sr,ref['early_rms'])
            model_attack=attack_measurement(mx,msr,model['early_rms'])
            differences=[]
            for r,m in zip(reference_attack,model_attack):
                target=np.asarray(r['normalized_band_power']);predicted=np.asarray(m['normalized_band_power'])
                valid=target>1e-5
                # First5ms and sub250Hz remain reported diagnostics; short
                # bass windows cannot distinguish noise from unresolved modes.
                bands=10*np.log10(np.maximum(predicted,1e-12)/np.maximum(target,1e-12))
                differences.append({'window_seconds':r['window_seconds'],'band_error_db':bands.tolist(),
                    'reference_prominent_band_mask':valid.tolist(),'centroid_log2_ratio':math.log2(max(m['centroid_250_19000_hz'],1)/max(r['centroid_250_19000_hz'],1)),
                    'crest_error_db':m['crest_db']-r['crest_db'],
                    'power_over_steady_rms_error_db':m['power_over_steady_rms_db']-r['power_over_steady_rms_db']})
            attacks.append({'id':ref['id'],'midi':ref['midi'],'layer':ref['layer'],'reference':reference_attack,'model':model_attack,'differences':differences})
            sources += [input_record(original_path),input_record(model_path)]
            print(ref['id']+': TRAIN score',flush=True)
        velocity=[]
        for note in notes:
            pair=[r for r in rows if r['midi']==note];modelpair=[r for r in models if r['midi']==note]
            contrast=lambda items:20*math.log10(next(r['early_rms'] for r in items if r['layer']==12)/next(r['early_rms'] for r in items if r['layer']==4))
            velocity.append({'midi':note,'reference_early_rms_contrast_db':contrast(pair),'model_early_rms_contrast_db':contrast(modelpair),
                             'error_db':contrast(modelpair)-contrast(pair)})
        evidence['audio_sources']=sources
        for item in sources:
            if sha(item['path'])!=item['sha256']:raise RuntimeError('Audio changed during measurement')
        verify_inputs(evidence)
        write_json(args.output/'model-features.json',{'samples':models,'provenance':evidence})
        write_json(args.output/'score.json',{'provenance':evidence,'training_ids':sorted(r['id'] for r in rows),
            'analysis':benchmark.ANALYSIS,'comparison':comparisons,'aggregate':benchmark.aggregate(comparisons)['train'],
            'attack_windows_seconds':[[0,.005],[.005,.020],[.020,.050],[.050,.100]],
            'attack_band_edges_hz':[31.25,250,1000,4000,12000,19000],
            'attack_texture':attacks,'velocity_contrasts':velocity,'reference_audio_identities':identities,
            'unassigned_component_comparison':components,
            'unassigned_component_limit':'Measured at fixed reference bands even when model lacks a local peak; not fitted or assigned to string/material/body identity.',
            'spurious_model_band_diagnostic':{'model_threshold_relative_db':-30.,'reference_threshold_relative_db':-50.,
                'case_count_with_flags':sum(bool(c['spurious_prominent_model_bands']) for c in comparisons),
                'flagged_window_band_pairs':sum(len(c['spurious_prominent_model_bands']) for c in comparisons),
                'changes_preserved_primary_metrics':False},
            'selection_limits':'No single automatic perceptual score. Compare0–5ms and sub250Hz only as onset/leakage diagnostics; preserve full envelope/body metrics, velocity contrast and acoustic regression cases.'})
        print(args.output/'score.json')


if __name__=='__main__':main()
