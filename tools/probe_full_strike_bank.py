#!/usr/bin/env python3
"""One bounded physical strike bank on frozen corrected TRAIN34 only.

Five uncapped full-model/hot-float builds,1s isolated renders,actual onsets,
shared recording-defined harmonic bands and conservative register selection.
"""
from __future__ import annotations
import argparse,copy,hashlib,json,math,subprocess,sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
import numpy as np
import fit_full_calibration as fitter
import probe_full_precision as precision
ROOT=Path(__file__).resolve().parents[1]
FROZEN_FITTER='355ac867415c62aba90717ecef6cbb77da839a798150c3664bf67247128f3356'
FROZEN_PROFILE='f8a3a3fe3833693b917b7462c8bc95652213f2486905941dae3cbc40990387d9'
FROZEN_TRAIN34='249e5b1b623aea2cc008d4523016a700c83b74ffc0fe9f10b54929f678ad0bc7'
WINDOWS=((0.,.005),(.005,.020),(.020,.050),(.050,.100))
BAND_EDGES=[31.25,250.,1000.,4000.,12000.,19000.]

BANK_ORDER = ('baseline', 'softer', 'harder', 'velocity-down', 'velocity-up')
LAYERS = ('4', '12')
OFFSETS = (-.001, 0., .001)
RULES = {
    'version': 1,
    'bank_order': list(BANK_ORDER),
    'onset_offsets_seconds': list(OFFSETS),
    'minimum_shared_reliable_bands': 3,
    'minimum_attack_improvement_db': .25,
    'minimum_attack_improvement_fraction': .05,
    'maximum_per_layer_attack_regression_db': .25,
    'maximum_per_layer_body_regression_db': .25,
    'maximum_contrast_regression_db': .25,
    'excluded_anchor_midis': [108],
    'quality_weights': {'attack': .5, 'body': .3, 'contrast': .2},
    'baseline_parameter_penalty_db': .05,
    'neighbor_parameter_jump_penalty_db_per_octave': .10,
    'parameter_units': {'log_hardness_ratio': math.log(1.25), 'velocity_exponent_delta': .08},
    'tie_tolerance_db': 1e-12,
    'interpretation': 'Prespecified engineering margins and regularization, not confidence intervals or an audibility claim.',
    'required_validation': 'Rerender and compare the selected combined profile before promotion.',
}


def _by_note(mapping, note, default=None):
    return mapping.get(note, mapping.get(str(note), default))


def _number(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError('Nonfinite metric or parameter')
    return result


def _layers(value):
    result = {layer: _number(value[layer]) for layer in LAYERS}
    if any(item < 0 for item in result.values()):
        raise ValueError('Attack/body losses must be nonnegative dB errors')
    return result


def _measure(record):
    """Validate all three offsets; missing evidence cannot create a win."""
    if not isinstance(record, dict) or record.get('eligible') is not True:
        return None, 'upstream measurement is absent or ineligible'
    try:
        attack = _layers(record['attack_by_layer'])
        body = _layers(record['body_by_layer'])
        contrast = abs(_number(record['contrast']))
        offsets = {}
        for key, values in record['attack_by_offset'].items():
            offset = _number(key)
            if offset in offsets:
                raise ValueError('Duplicate onset offset')
            offsets[offset] = _layers(values)
        if set(offsets) != set(OFFSETS):
            raise ValueError('Require exactly the three frozen onset offsets')
        if any(abs(attack[layer] - offsets[0.][layer]) > 1e-8 for layer in LAYERS):
            raise ValueError('Central attack metrics disagree')
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        return None, 'invalid metric evidence: ' + str(error)
    return {'attack': attack, 'body': body, 'contrast': contrast, 'offsets': offsets}, None


def _profile_keys(profile):
    result = {}
    for key in profile['keys']:
        note = int(key['midi'])
        if note in result or not 21 <= note <= 108:
            raise ValueError('Duplicate or out-of-range profile anchor')
        hardness = _number(key['hardness'])
        exponent = _number(key['velocity_exponent'])
        if hardness <= 0:
            raise ValueError('Hardness must be positive')
        result[note] = (hardness, exponent)
    return result


def select_strike_banks(metrics_by_note, profiles, shared_support_counts):
    """Return labels, gate reasons, local costs and the fixed rule definitions.

    metrics_by_note[note][bank] contains attack_by_layer/body_by_layer {'4','12'},
    contrast (absolute or signed error in hard-minus-soft harmonic-power dB),
    eligible bool, and attack_by_offset {'-0.001','0.0','0.001'} with both layers.
    profiles[bank]['keys'] supplies actual emitted parameters after clipping.
    shared_support_counts[note] is the reference-only reliable-band intersection
    across both velocities, frozen identically for every bank.
    """
    if set(profiles) != set(BANK_ORDER):
        raise ValueError('Require exactly the five frozen strike-bank profiles')
    keys = {bank: _profile_keys(profiles[bank]) for bank in BANK_ORDER}
    notes = sorted(keys['baseline'])
    if not notes or any(set(value) != set(notes) for value in keys.values()):
        raise ValueError('Bank profile anchor inventories must agree')
    if any(int(note) not in notes for note in metrics_by_note):
        raise ValueError('Metrics contain an anchor absent from the profiles')
    costs, parameters = {}, {}
    for note in notes:
        records = _by_note(metrics_by_note, note, {})
        base, base_error = _measure(records.get('baseline'))
        support = _by_note(shared_support_counts, note, 0)
        try:
            support_valid = _number(support) >= 3 and int(support) == float(support)
        except (ValueError, TypeError, OverflowError):
            support_valid = False
        base_hardness, base_exponent = keys['baseline'][note]
        parameters[note], costs[note] = {}, {}
        for bank in BANK_ORDER:
            hardness, exponent = keys[bank][note]
            delta = (math.log(hardness / base_hardness) / math.log(1.25),
                     (exponent - base_exponent) / .08)
            parameters[note][bank] = delta
            entry = {'eligible': bank == 'baseline', 'reasons': [],
                     'actual_normalized_parameter_delta': list(delta), 'local_cost_db': 0. if bank == 'baseline' else None}
            costs[note][bank] = entry
            if bank == 'baseline':
                entry['reasons'] = ['baseline is always an available control']
                continue
            if note == 108:
                entry['reasons'].append('C8 is excluded from selection at both velocities')
            if not support_valid:
                entry['reasons'].append('fewer than three shared reliable reference bands')
            if base is None:
                entry['reasons'].append('baseline evidence unavailable: ' + str(base_error))
            candidate, error = _measure(records.get(bank))
            if candidate is None:
                entry['reasons'].append(str(error))
            if entry['reasons']:
                continue
            attack_deltas, gains = {}, {}
            for offset in OFFSETS:
                old = base['offsets'][offset]
                new = candidate['offsets'][offset]
                old_mean, new_mean = sum(old.values()) / 2, sum(new.values()) / 2
                improvement = old_mean - new_mean
                required = max(.25, .05 * old_mean)
                attack_deltas[str(offset)] = new_mean - old_mean
                gains[str(offset)] = {'improvement_db': improvement, 'required_db': required}
                if improvement < required - 1e-12:
                    entry['reasons'].append(f'attack improvement below frozen margin at {offset:+.3f}s')
                if any(new[layer] > old[layer] + .25 + 1e-12 for layer in LAYERS):
                    entry['reasons'].append(f'per-layer attack regression exceeds .25dB at {offset:+.3f}s')
            if any(candidate['body'][layer] > base['body'][layer] + .25 + 1e-12 for layer in LAYERS):
                entry['reasons'].append('per-layer body regression exceeds .25dB')
            if candidate['contrast'] > base['contrast'] + .25 + 1e-12:
                entry['reasons'].append('harmonic velocity-contrast regression exceeds .25dB')
            if abs(delta[0]) + abs(delta[1]) <= 1e-12:
                entry['reasons'].append('emitted anchor parameters equal baseline after clipping')
            attack_delta = max(attack_deltas.values())
            body_delta = sum(candidate['body'][layer] - base['body'][layer] for layer in LAYERS) / 2
            contrast_delta = candidate['contrast'] - base['contrast']
            prior = .05 * sum(value * value for value in delta)
            entry.update({'attack_improvement_by_offset': gains,
                          'quality_delta_db': {'attack_worst_offset': attack_delta, 'body_mean': body_delta,
                                               'contrast_absolute_error': contrast_delta},
                          'baseline_parameter_penalty_db': prior})
            if not entry['reasons']:
                entry['eligible'] = True
                entry['local_cost_db'] = .5 * attack_delta + .3 * body_delta + .2 * contrast_delta + prior
                entry['reasons'] = ['clear attack improvement at every onset offset; all layer/body/dynamics guards pass']
    # Dynamic programming uses only individually eligible clear wins plus the
    # baseline. Regularization can reject a win, never manufacture eligibility.
    states = {'baseline': (0., ())}
    for index, note in enumerate(notes):
        next_states = {}
        previous_note = notes[index - 1] if index else None
        for bank in BANK_ORDER:
            if not costs[note][bank]['eligible']:
                continue
            choices = []
            for previous_bank, (previous_cost, path) in states.items():
                jump = 0.
                if previous_note is not None:
                    gap_octaves = (note - previous_note) / 12.
                    jump = .10 * sum((a - b) ** 2 for a, b in zip(
                        parameters[note][bank], parameters[previous_note][previous_bank])) / gap_octaves
                choices.append((previous_cost + costs[note][bank]['local_cost_db'] + jump,
                                path + (BANK_ORDER.index(bank),)))
            best = choices[0]
            for choice in choices[1:]:
                if choice[0] < best[0] - 1e-12 or (abs(choice[0] - best[0]) <= 1e-12 and choice[1] < best[1]):
                    best = choice
            next_states[bank] = best
        states = next_states
    best = None
    for value in states.values():
        if best is None or value[0] < best[0] - 1e-12 or (abs(value[0] - best[0]) <= 1e-12 and value[1] < best[1]):
            best = value
    chosen = {str(note): BANK_ORDER[rank] for note, rank in zip(notes, best[1])}
    reasons, transitions = {}, []
    for index, note in enumerate(notes):
        bank = chosen[str(note)]
        if bank != 'baseline':
            reasons[str(note)] = ['eligible clear win retained after baseline and register-smoothness penalties']
        elif note == 108:
            reasons[str(note)] = ['C8 anchor forced to baseline; neither velocity contributes to selection']
        elif any(costs[note][label]['eligible'] for label in BANK_ORDER[1:]):
            reasons[str(note)] = ['baseline preferred after baseline and register-smoothness penalties']
        else:
            reasons[str(note)] = ['baseline retained; no candidate passed every frozen eligibility gate']
        if index:
            previous = notes[index - 1]
            old = parameters[previous][chosen[str(previous)]]
            new = parameters[note][bank]
            penalty = .10 * sum((a - b) ** 2 for a, b in zip(old, new)) / ((note - previous) / 12.)
            transitions.append({'from_midi': previous, 'to_midi': note, 'penalty_db': penalty})
    return {'chosen_labels': chosen, 'reasons': reasons,
            'candidate_costs': {str(note): value for note, value in costs.items()},
            'objective_cost_db': best[0], 'selected_neighbor_penalties': transitions,
            'rule_definitions': copy.deepcopy(RULES),
            'validation_status': 'Proposed combined profile only; actual combined renders have not been validated.'}


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def db(value):return 10*np.log10(np.maximum(value,1e-30))
def run(command,log,allow_failure=False):
    p=subprocess.run([str(x) for x in command],capture_output=True,text=True,timeout=180)
    Path(str(log)+'.stdout.txt').write_text(p.stdout);Path(str(log)+'.stderr.txt').write_text(p.stderr)
    if p.returncode and not allow_failure:raise RuntimeError(f'Command failed: {command[0]}; see {log}')
    return p

def analyze(x,sr,centers,fundamental,offset=0.):
    onset,detail=fitter.benchmark.onset_index(x,sr)
    begin=onset+int(round(offset*sr));aligned=x[begin:]
    if begin<0 or len(aligned)<int(.75*sr):raise ValueError('Insufficient actual post-onset support')
    def spec(a,b):return fitter.benchmark.spectrum(aligned[int(a*sr):int(b*sr)],sr)
    f,p=spec(.05,.75);widths=np.minimum(.38*fundamental,np.maximum(3/.7,.004*np.asarray(centers)))
    power=np.array([fitter.benchmark.integrated_power(f,p,c-w,c+w) for c,w in zip(centers,widths)])
    neighbor=np.array([(fitter.benchmark.integrated_power(f,p,c-3*w,c-2*w)+fitter.benchmark.integrated_power(f,p,c+2*w,c+3*w))/2 for c,w in zip(centers,widths)])
    attack=[]
    for a,b in WINDOWS:
        fa,pa=spec(a,b);section=aligned[int(a*sr):int(b*sr)]
        bands=np.array([fitter.benchmark.integrated_power(fa,pa,lo,hi) for lo,hi in zip(BAND_EDGES[:-1],BAND_EDGES[1:])])
        attack.append({'window_seconds':[a,b],'band_power':bands.tolist(),'rms':float(np.sqrt(np.mean(section*section))),
                       'crest_db':float(20*np.log10(max(np.max(abs(section)),1e-30)/max(np.sqrt(np.mean(section*section)),1e-30)))})
    return {'onset_seconds':onset/sr,'onset_details':detail,'relative_onset_perturbation_seconds':offset,
            'harmonic_power':power.tolist(),'harmonic_neighbor_prominence_db':(db(power)-db(neighbor)).tolist(),
            'early_rms':float(np.sqrt(np.mean(aligned[int(.05*sr):int(.75*sr)]**2))),'attack':attack}


def normalized_losses(ref,model,mask):
    rp=np.array(ref['harmonic_power']);mp=np.array(model['harmonic_power']);denr=float(rp[mask].sum());denm=float(mp[mask].sum())
    if not np.any(mask) or min(denr,denm)<=1e-28:return None
    body=float(np.median(np.abs(db(mp[mask]/denm)-db(rp[mask]/denr))))
    losses=[];windows=[]
    for index,(rr,mm) in enumerate(zip(ref['attack'],model['attack'])):
        r=np.array(rr['band_power'])/denr;m=np.array(mm['band_power'])/denm
        # The fixed recording mask is shared by every strike bank. 0-5ms and
        # sub250Hz are diagnostics, not short-window parameter evidence.
        accepted=(np.array(BAND_EDGES[:-1])>=250)&(db(r)>=-45)
        error=db(m)-db(r);loss=float(np.median(abs(error[accepted]))) if np.any(accepted) else None
        windows.append({'window_seconds':rr['window_seconds'],'reference_prominent_selection_mask':accepted.tolist(),
                        'band_error_db':error.tolist(),'loss_db':loss,'ranked':index>0})
        if index>0 and loss is not None:losses.append(loss)
    if len(losses)!=3:return None
    return {'attack_loss_db':float(np.mean(losses)),'body_shape_loss_db':body,'attack_windows':windows,
            'harmonic_shape_error_db':(db(mp[mask]/denm)-db(rp[mask]/denr)).tolist(),
            'normalization':'Sum of frozen reliable fixed harmonic bands in0.05–0.75s; broadband RMS is diagnostic only.'}


def build_and_render(args,rows,profiles,guard,evidence):
    base_source,transforms=fitter.build_candidate(args.source)
    full_float=precision.hot_precision(base_source)
    if 'int cap=pol==0?320:48;' not in full_float:raise ValueError('Refuse a capped source')
    records={};flags=['-O3','-DNDEBUG','-std=c++17','-ffp-contract=off']
    for bank in BANK_ORDER:
        folder=args.output/bank;folder.mkdir(parents=True,exist_ok=True)
        source=folder/'grand.cpp';source.write_text(full_float);header=folder/'calibration.h';fitter.generate_header(profiles[bank],header)
        binary=folder/'render';run([args.compiler,*flags,source,'-o',binary],folder/'compile')
        raw=run([binary,'--self-test'],folder/'physical-self-test',True);physical=json.loads(raw.stdout)
        eligible=(physical['conservative_contact_relative_energy_error']<=5e-5 and physical['bridge_max_relative_energy_increase']<=5e-7
                  and physical['bridge_energy_remaining_ratio']<=1+5e-6 and physical['contact_max_relative_residual']<1e-8)
        records[bank]={'source_sha256':digest(source),'calibration_sha256':digest(header),'engine_sha256':digest(binary),
                       'profile_sha256':digest(args.output/'profiles'/bank/'calibration.json'),'physical_self_test_original':physical,
                       'float_physics_eligible':eligible,'flags':flags,'renders':[]}
        if bank=='baseline' and not eligible:raise ValueError('Baseline float mechanical audit failed')
    def job(row,bank):
        folder=args.output/bank/'renders';folder.mkdir(parents=True,exist_ok=True)
        events=folder/(row['id']+'.events');events.write_text(f"0.100000 on {row['midi']} {row['midi_velocity']}\n")
        wav=folder/(row['id']+'.wav');sidecar=folder/(row['id']+'.json')
        identity={k:records[bank][k] for k in ('source_sha256','calibration_sha256','engine_sha256','profile_sha256')}
        inputs={**identity,**guard,'events_sha256':digest(events),'duration_seconds':1.,'sample_rate':48000,
                'note_on_seconds':.1,'id':row['id'],'render_spec_version':1}
        if args.resume and sidecar.exists():
            old=json.loads(sidecar.read_text())
            if old['inputs']==inputs and wav.is_file() and digest(wav)==old['audio_sha256']:return bank,old
            raise ValueError('Resume identity mismatch: '+str(sidecar))
        if sidecar.exists() and not args.resume:raise ValueError('Use --resume for existing batch')
        p=run([args.output/bank/'render','--events',events,'--output',wav,'--sample-rate','48000','--duration','1.0'],folder/row['id'])
        metrics=json.loads(p.stdout)
        if (metrics['string_count'],metrics['board_modes'],metrics['nonfinite_samples'])!=(230,475,0) or not np.isfinite(metrics['final_mechanical_energy_J']) or metrics['final_mechanical_energy_J']<0 or metrics['contact_max_relative_residual']>=1e-8:
            raise ValueError('Invalid mechanical render: '+row['id'])
        receipt={'id':row['id'],'inputs':inputs,'metrics':metrics,'audio_file':str(wav),'audio_sha256':digest(wav),'driver_sha256':evidence['tool_sha256']}
        write(sidecar,receipt);return bank,receipt
    tasks=[(row,bank) for row in rows for bank in BANK_ORDER]
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures=[pool.submit(job,*task) for task in tasks]
        for count,future in enumerate(as_completed(futures),1):
            bank,receipt=future.result();records[bank]['renders'].append(receipt)
            if count%10==0 or count==len(tasks):print('rendered',count,'/',len(tasks),flush=True)
    for bank in records:records[bank]['renders'].sort(key=lambda r:r['id'])
    return records,transforms


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--profile',type=Path,default=ROOT/'out/full-calibration/v3/mechanics/calibration.json')
    p.add_argument('--profile-sha',default=FROZEN_PROFILE)
    p.add_argument('--reference',type=Path,default=ROOT/'References/GrandFullRange/combined_train_features.json')
    p.add_argument('--split',type=Path,default=ROOT/'References/GrandFullRange/split.json')
    p.add_argument('--source',type=Path,default=ROOT/'src/full_reference/grand.cpp')
    p.add_argument('--output',type=Path,default=ROOT/'out/full-strike-bank')
    p.add_argument('--compiler',default='g++');p.add_argument('--jobs',type=int,default=3);p.add_argument('--resume',action='store_true')
    args=p.parse_args();args.output=args.output.resolve()
    if not 1<=args.jobs<=4 or not (ROOT/'out').resolve() in args.output.parents:p.error('Use1–4 jobs and an out/ destination')
    if digest(ROOT/'tools/fit_full_calibration.py')!=FROZEN_FITTER or digest(args.profile)!=args.profile_sha or digest(args.reference)!=FROZEN_TRAIN34:
        p.error('Frozen fitter/profile/TRAIN34 identity mismatch; wait for a reviewed freeze')
    args.output.mkdir(parents=True,exist_ok=True)
    rows,notes=fitter.training_inputs(args.reference,args.split)
    if len(rows)!=34 or len(notes)!=17:raise ValueError('Require exact locked TRAIN34')
    base=json.loads(args.profile.read_text());fitter.validate_profile(base)
    if set(base['training_ids'])!={r['id'] for r in rows}:raise ValueError('Profile TRAIN IDs mismatch')
    evidence={'tool_sha256':digest(Path(__file__)),'fitter_sha256':FROZEN_FITTER,'profile_sha256':digest(args.profile),
              'reference_sha256':digest(args.reference),'split_sha256':digest(args.split),'source_sha256':digest(args.source),
              'precision_transform_sha256':digest(ROOT/'tools/probe_full_precision.py'),
              'compiler':subprocess.check_output([args.compiler,'--version'],text=True).splitlines()[0],
              'fresh_evaluation_audio_opened':False,'heldout_measurements_used':False}
    profiles_dir=args.output/'profiles'
    run([sys.executable,ROOT/'tools/fit_full_calibration.py','--reference',args.reference,'--split',args.split,
         'strike-bank','--profile',args.profile,'--output',profiles_dir],args.output/'generate-bank')
    profiles={bank:json.loads((profiles_dir/bank/'calibration.json').read_text()) for bank in BANK_ORDER}
    receipts={};references={};centers_by_note={};centers_orders={}
    for note in notes:
        rr=[r for r in rows if r['midi']==note]
        # Only observed reference partials are shared across velocity layers;
        # model-fitted centers and unidentified fallback B never set bands.
        observed=[]
        for row in rr:
            mapping={int(q['n']):float(q['hz']) for q in row.get('measured_partial_peaks',[])}
            if not mapping:mapping={int(q['n']):float(q['frequency_hz']) for q in row['partials']}
            observed.append(mapping)
        orders=sorted(set(observed[0])&set(observed[1]));centers_orders[note]=orders
        centers_by_note[note]=[float(np.median([q[n] for q in observed])) for n in orders]
    for row in rows:
        path=fitter.reference_audio(row,args.reference);receipt=fitter.reference_audio_identity(row,path);receipts[row['id']]=receipt
        rate,x=fitter.benchmark.load_audio(path)
        centers=centers_by_note[row['midi']];fundamental=float(np.median([r['f1_hz'] for r in rows if r['midi']==row['midi']]))
        references[row['id']]=analyze(x,rate,centers,fundamental)
        references[row['id']]['stored_onset_seconds']=row['onset_seconds']
    write(args.output/'reference-identities.json',receipts);write(args.output/'reference-short-features.json',references)
    guard={k:evidence[k] for k in ('fitter_sha256','reference_sha256','split_sha256')}
    records,transforms=build_and_render(args,rows,profiles,guard,evidence)
    write(args.output/'render-bank.json',{'provenance':evidence,'banks':records,'build_transforms':transforms})
    model_features={bank:{} for bank in BANK_ORDER}
    for bank in BANK_ORDER:
        for row in rows:
            path=args.output/bank/'renders'/(row['id']+'.wav');rate,x=fitter.benchmark.load_audio(path)
            if rate!=48000 or len(x)!=48000:raise ValueError('Invalid short render support')
            centers=centers_by_note[row['midi']];fundamental=float(np.median([r['f1_hz'] for r in rows if r['midi']==row['midi']]))
            model_features[bank][row['id']]={str(offset):analyze(x,rate,centers,fundamental,offset) for offset in OFFSETS}
            model_features[bank][row['id']]['0.0']['event_to_onset_latency_seconds']=model_features[bank][row['id']]['0.0']['onset_seconds']-.1
        write(args.output/bank/'short-features.json',model_features[bank])
    metrics={};details={};support={};missing=[]
    for note in notes:
        rr=sorted([r for r in rows if r['midi']==note],key=lambda r:r['layer']);ref=[references[r['id']] for r in rr]
        rp=np.array([q['harmonic_power'] for q in ref]);prom=np.array([q['harmonic_neighbor_prominence_db'] for q in ref])
        bp=np.array([model_features['baseline'][r['id']]['0.0']['harmonic_power'] for r in rr]);bprom=np.array([model_features['baseline'][r['id']]['0.0']['harmonic_neighbor_prominence_db'] for r in rr])
        refmask=np.all((db(rp)-db(np.maximum(rp.max(axis=1,keepdims=True),1e-30))>=-40)&(prom>=6),axis=0) if rp.size else np.zeros(0,bool)
        basemask=np.all((db(bp)-db(np.maximum(bp.max(axis=1,keepdims=True),1e-30))>=-50)&(bprom>=3),axis=0) if bp.size else np.zeros(0,bool)
        mask=refmask&basemask;support[note]=int(mask.sum());metrics[note]={}
        details[str(note)]={'orders':centers_orders[note],'fixed_reference_centers_hz':centers_by_note[note],
                            'reference_reliable_mask':refmask.tolist(),'baseline_supported_mask':basemask.tolist(),'selection_mask':mask.tolist(),
                            'support':support[note],'candidates':{}}
        if note==108:
            missing=[{'id':r['id'],'carrier_f1_hz':r['f1_hz'],'unassigned_components':r.get('unassigned_components',[]),
                      'selection':'Entire C8 anchor excluded; missing4434Hz physical component is not a strike-parameter target.'} for r in rr]
        refcontrast=db(rp[1])-db(rp[0]) if rp.size else np.zeros(0)
        for bank in BANK_ORDER:
            attack={str(offset):{} for offset in OFFSETS};body={};loss_details={};eligible=support[note]>=3 and note!=108 and records[bank]['float_physics_eligible']
            for row,rf in zip(rr,ref):
                layer=str(row['layer']);loss_details[layer]={}
                for offset in OFFSETS:
                    loss=normalized_losses(rf,model_features[bank][row['id']][str(offset)],mask)
                    if loss is None:eligible=False;continue
                    attack[str(offset)][layer]=loss['attack_loss_db'];loss_details[layer][str(offset)]=loss
                    if offset==0:body[layer]=loss['body_shape_loss_db']
            mp=np.array([model_features[bank][r['id']]['0.0']['harmonic_power'] for r in rr])
            contrast_error=(db(mp[1])-db(mp[0])-refcontrast)[mask] if mp.size else np.zeros(0)
            contrast=float(np.median(abs(contrast_error))) if len(contrast_error) else None
            metrics[note][bank]={'eligible':eligible,'attack_by_layer':attack['0.0'],'attack_by_offset':attack,
                                  'body_by_layer':body,'contrast':contrast}
            details[str(note)]['candidates'][bank]={'metrics':metrics[note][bank],'window_losses':loss_details,
                'raw_harmonic_hard_minus_soft_error_db':contrast_error.tolist(),'contrast_removed_per_layer_gain':False}
    selection=select_strike_banks(metrics,profiles,support)
    proposed=copy.deepcopy(base)
    for key in proposed['keys']:
        bank=selection['chosen_labels'][str(key['midi'])];selected=next(k for k in profiles[bank]['keys'] if k['midi']==key['midi'])
        key['hardness']=selected['hardness'];key['velocity_exponent']=selected['velocity_exponent']
    proposed.update(fit_stage='TRAIN34 short physical strike-bank proposal; combined long renders/radiation/evaluation still required',
                    strike_bank_proposal={'selection_labels':selection['chosen_labels'],'provenance':evidence,'combined_render_validated':False})
    fitter.emit_profile(proposed,args.output/'proposed-profile')
    report={'schema_version':1,'provenance':evidence,'training_ids':[r['id'] for r in rows],'duration_seconds':1.,'note_on_seconds':.1,
            'fixed_windows':{'attack_seconds':WINDOWS,'body_seconds':[.05,.75],'attack_band_edges_hz':BAND_EDGES},
            'reference_audio_identities':receipts,'bank_artifacts':records,'measurements':details,'selection':selection,
            'unassigned_missing_physics':missing,'proposed_profile':{'path':str(args.output/'proposed-profile/calibration.json'),
                'sha256':digest(args.output/'proposed-profile/calibration.json'),'header_sha256':digest(args.output/'proposed-profile/calibration.h')},
            'limits':'One5-bank short TRAIN-only batch. Effective strike parameters remain confounded with unrefitted observation. Fixed reliable harmonic bands, balanced velocities and onset sensitivity guard selection; no scalar rise-only fit. Proposal requires combined long34 rendering, joint radiation, freeze and separate locked evaluation. No canonical or Research edits.'}
    # Reauthenticate exactly these TRAIN files and all frozen fitting inputs.
    for row in rows:
        actual=fitter.reference_audio(row,args.reference)
        if fitter.reference_audio_identity(row,actual)!=receipts[row['id']]:raise ValueError('TRAIN PCM identity changed')
    if digest(ROOT/'tools/fit_full_calibration.py')!=FROZEN_FITTER or digest(args.profile)!=args.profile_sha or digest(args.reference)!=FROZEN_TRAIN34:
        raise ValueError('Fitting inputs changed during batch')
    write(args.output/'report.json',report)
    print(json.dumps({'report':str(args.output/'report.json'),'chosen_labels':selection['chosen_labels'],'proposal':report['proposed_profile']},indent=2))


if __name__=='__main__':main()
