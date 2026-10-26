#!/usr/bin/env python3
"""Fit numeric modal envelopes from an explicitly locked training subset.

No waveform is embedded. Four Hann-power windows constrain positive, bounded
two-stage amplitude decays; these are empirical radiation envelopes, not an
identification of hammer mechanics or wood species.
"""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ROOT / 'Research/GrandPianoV2/benchmark/reference_features.json'
EXPANDED_FEATURES = ROOT / 'References/GrandExpanded/train_features.json'
EXPANDED_SPLIT = ROOT / 'References/GrandExpanded/split.json'
WINDOWS = [(0.05, .25), (.25, .75), (.75, 1.5), (1.5, 3.5)]
TIMES = np.array([np.linspace(a, b, 96, endpoint=False)+(b-a)/192 for a, b in WINDOWS])
WEIGHTS = np.sin(np.pi*(np.arange(96)+.5)/96)**4
WEIGHTS /= WEIGHTS.sum()


def training_contract(source, split_path=None):
    """Reject partial pairs, duplicate IDs, or fit/validation contamination."""
    rows = source['samples']
    selected = [sample for sample in rows if sample['split'] == 'train']
    ids = [sample['id'] for sample in selected]
    if len(ids) != len(set(ids)): raise ValueError('Duplicate training ID')
    lock = None
    if split_path is None:
        expected = {f'C{o}v{v}' for o in range(2, 7) for v in (4, 12)}
    else:
        lock = json.loads(split_path.read_text())
        if not lock.get('locked_before_new_downloads_and_feature_extraction'):
            raise ValueError('Expanded split must be locked before extraction')
        locked_ids = lock['training_ids']
        expected = set(locked_ids)
        if len(expected) != len(locked_ids): raise ValueError('Duplicate locked training ID')
        locked_rows = {row['id']: row for row in lock['samples']}
        if len(locked_rows)!=len(lock['samples']): raise ValueError('Duplicate split ID')
        roles = {name:row['role'] for name,row in locked_rows.items()}
        if any(roles.get(name) != 'train' for name in expected):
            raise ValueError('A locked training ID has a validation role')
        if len(rows) != len(selected):
            raise ValueError('Expanded fitting input must contain training features only')
        for row in selected:
            metadata = locked_rows.get(row['id'])
            if metadata is None or any(row[field]!=metadata[field] for field in ('midi','layer','midi_velocity')):
                raise ValueError('Feature identity differs from the locked split')
    if set(ids) != expected: raise ValueError('Training split changed')
    pairs = {}
    for row in selected:
        note,layer = row['midi'],row['layer']
        if not isinstance(note,int) or not 21<=note<=108 or layer not in (4,12):
            raise ValueError('Anchors require MIDI21..108 and source layers4/12')
        if row['midi_velocity'] != {4:40,12:93}[layer]:
            raise ValueError('Unexpected training velocity proxy')
        if layer in pairs.setdefault(note,{}): raise ValueError('Duplicate anchor velocity')
        pairs[note][layer] = row
    if len(pairs)<2 or any(set(pair)!={4,12} for pair in pairs.values()):
        raise ValueError('Each anchor requires exactly soft/loud training cases')
    if lock and lock.get('anchor_midis') != sorted(pairs):
        raise ValueError('Anchor list differs from the locked split')
    return selected,expected,pairs,lock


def fit_partial(partial,detune_cents=0.):
    powers = np.maximum(partial['powers'], 1e-18)
    # The live grand starts the fast/late oscillators in phase but detunes the
    # late branch by .23 cents. Its cycle-averaged power therefore contains a
    # difference-frequency cosine, rather than a permanently coherent sum.
    detuned_cosine = np.cos(2*np.pi*partial['frequency_hz']*(2**(detune_cents/1200)-1)*TIMES)
    dec = partial['decay']
    def rate(kind, fallback):
        fit = dec.get(kind)
        return np.clip(fit['amplitude_sigma_per_second'], .04, 20.) if fit and fit['r_squared'] > .3 else fallback
    slow = rate('late', rate('overall', .7))
    fast = max(slow+.2, rate('early', slow+2.))
    peak = np.sqrt(2*powers[0])*np.exp(min(fast*.15, 2.))
    def prediction(theta):
        amp, mix, late, extra = np.exp(theta[0]), theta[1], np.exp(theta[2]), np.exp(theta[3])
        if detune_cents:
            fast,slow=amp*mix,amp*(1-mix)
            power=fast*fast*np.exp(-2*(late+extra)*TIMES)+slow*slow*np.exp(-2*late*TIMES)+2*fast*slow*np.exp(-(2*late+extra)*TIMES)*detuned_cosine
            return .5*(power @ WEIGHTS)
        envelope = amp*(mix*np.exp(-(late+extra)*TIMES)+(1-mix)*np.exp(-late*TIMES))
        return .5*(envelope*envelope @ WEIGHTS)
    def residual(theta):
        # Weak rate priors discourage extreme solutions when beating makes the
        # four powers non-monotonic; no held-out feature enters this fit.
        return np.r_[10*np.log10(np.maximum(prediction(theta), 1e-24)/powers),
                     .12*(theta[2]-np.log(slow)), .12*(theta[3]-np.log(max(.1, fast-slow))) ]
    best = None
    for mix in (.2, .7, .95):
        fit = least_squares(residual, [np.log(max(peak, 1e-7)), mix, np.log(slow), np.log(max(.1, fast-slow))],
                            bounds=([np.log(1e-9), 0, np.log(.03), np.log(.05)],
                                    [np.log(4), 1, np.log(20), np.log(40)]), max_nfev=100)
        if best is None or np.sum(fit.fun**2) < np.sum(best.fun**2): best = fit
    amp, mix, late, extra = np.exp(best.x[0]), best.x[1], np.exp(best.x[2]), np.exp(best.x[3])
    return float(amp*mix), float(amp*(1-mix)), float(late+extra), float(late)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--header', type=Path)
    parser.add_argument('--report', type=Path)
    parser.add_argument('--features', type=Path, help='Training feature export (default: locked expanded grand); custom data requires --split')
    parser.add_argument('--split', type=Path, help='Immutable expanded split manifest')
    parser.add_argument('--upright', action='store_true', help='Use the separate locked CC0 upright training subset')
    parser.add_argument('--legacy-coherent', action='store_true', help='Reproduce the original coherent two-stage grand calibration')
    args = parser.parse_args()
    if args.upright and (args.features or args.split):
        parser.error('The independent upright uses its existing locked training subset')
    if args.features and not args.split and args.features.resolve() not in (FEATURES.resolve(),EXPANDED_FEATURES.resolve()):
        parser.error('Alternative training features require --split')
    feature_path = args.features or (ROOT/'References/Upright/train_features.json' if args.upright else
                                    FEATURES if args.legacy_coherent else EXPANDED_FEATURES)
    if not args.upright and args.split is None and feature_path.resolve()==EXPANDED_FEATURES.resolve():
        args.split=EXPANDED_SPLIT
    args.header = args.header or ROOT/('src/UprightCalibration.h' if args.upright else 'src/LiveCalibration.h')
    args.report = args.report or ROOT/('Validation/upright-calibration.json' if args.upright else 'Validation/live-calibration.json')
    source = json.loads(feature_path.read_text())
    # Keep the independent upright calibration unchanged. The grand's fit now
    # agrees with its existing default observation model; no attack, voicing or
    # microphone parameter is changed by this correction.
    detune_cents=0. if args.upright or args.legacy_coherent else .23
    selected,expected,pairs,lock = training_contract(source,args.split)
    fitted = {}
    for sample in selected:
        sample_detune = .04 if detune_cents and sample['midi']<32 else detune_cents
        modes = [fit_partial(p,sample_detune) for p in sample['partials']]
        modes += [(1e-8, 1e-8, 12., 4.)]*(64-len(modes))
        fitted[sample['id']] = {'modes': modes[:64], 'attack': float(np.clip(sample['attack']['rise10_90_seconds'], .001, .075))}
    priors = []
    for sample in selected:
        if sample.get('B_identifiable', True): continue
        other = next((s for s in selected if s['midi']==sample['midi'] and s.get('B_identifiable', True)), None)
        if other is None: raise ValueError(f"No reliable training pitch/spectrum for {sample['id']}")
        # A pitch-analysis fallback is not a measurement of missing harmonics.
        # Borrow the other training velocity's shape and retain measured RMS.
        scale = sample['early_rms']/other['early_rms']
        fitted[sample['id']]['modes'] = [(a*scale,b*scale,c,d) for a,b,c,d in fitted[other['id']]['modes']]
        priors.append({'case':sample['id'],'borrowed_training_spectrum':other['id'], 'level_scale':scale,
                       'reason':'Pitch/inharmonicity unidentifiable; missing partials use same-note training shape, not analysis fallback values.'})
    lines = ['// Generated by tools/fit_live_calibration.py; numeric TRAIN10 features only.',
             '#pragma once', '#include <array>', 'namespace keyra::calibration {',
             'struct Anchor { int note; double f1,B;',
             'std::array<double,64> amplitudeSoft,amplitudeHard,decaySoft,decayHard;',
             'double attackSoft,attackHard;',
             'std::array<double,64> amplitudeLateSoft,amplitudeLateHard,decayLateSoft,decayLateHard; };',
             'inline constexpr std::array<Anchor,'+str(len(pairs))+'> anchors={{']
    if lock:
        lines[0] = '// Generated by tools/fit_live_calibration.py; locked numeric training features only.'
    if detune_cents:
        lines.insert(1,'// Default grand: in-phase fast/late branches, late branch detuned by .23 cents.')
    if args.upright:
        lines = ['// Generated from locked CC0 upright training features; velocities are proxies.',
                 '#pragma once', '#include "LiveCalibration.h"', 'namespace keyra::upright_calibration {',
                 'inline constexpr std::array<keyra::calibration::Anchor,5> anchors={{']
    def array(values): return '{'+','.join(f'{v:.10g}' for v in values)+'}'
    for note in sorted(pairs):
        a,b = pairs[note][4],pairs[note][12]
        low, high = fitted[a['id']], fitted[b['id']]
        reliable = [s for s in (a,b) if s.get('B_identifiable',True)]
        f1 = np.exp(np.mean([np.log(s['f1_hz']) for s in reliable]))
        dispersion = np.exp(np.mean([np.log(max(s['B'],1e-7)) for s in reliable]))
        lines.append('{'+f"{note},{f1:.12g},{dispersion:.12g},")
        lines.append(',\n'.join(array([m[idx] for m in f['modes']]) for idx in (0,2) for f in (low, high))+',')
        lines.append(f"{low['attack']:.10g},{high['attack']:.10g},")
        lines.append(',\n'.join(array([m[idx] for m in f['modes']]) for idx in (1,3) for f in (low, high))+'},')
    lines += ['}};', '}', '']
    args.header.parent.mkdir(parents=True, exist_ok=True)
    args.header.write_text('\n'.join(lines))
    try: feature_source = str(feature_path.relative_to(ROOT))
    except ValueError: feature_source = str(feature_path)
    report = {'schema_version': 1, 'training_ids': sorted(expected),
              'anchor_midis':sorted(pairs),
              'feature_source': feature_source,
              'feature_sha256': hashlib.sha256(feature_path.read_bytes()).hexdigest(),
              'method': 'Positive two-stage amplitude decays fitted to four Hann-squared weighted power windows, weak rate priors; absolute recorded velocity levels retained.',
              'model_provenance':{
                  'observation_model':'detuned two-stage modal branches' if detune_cents else 'legacy coherent two-stage modal branches',
                  'source_sample_rates_hz':sorted({sample['sample_rate'] for sample in selected}),
                  'first_branch_frequency':'Measured partial frequency_hz from the locked training feature row.',
                  'first_branch_decay':'late + extra, positive bounded amplitude decay per second.',
                  'late_branch_detune_cents':detune_cents,
                  'late_branch_frequency_ratio':2**(detune_cents/1200),
                  'late_branch_decay':'late, positive bounded amplitude decay per second.',
                  'initial_relative_phase_radians':0,
                  'power_model':'0.5 * (F^2 exp(-2 sf t) + L^2 exp(-2 sl t) + 2 F L exp(-(sf+sl)t) cos(2 pi (f_late-f_fast)t))' if detune_cents else '0.5 * (F exp(-sf t) + L exp(-sl t))^2',
                  'integration':'Carrier-cycle averaged power, weighted by the unchanged four Hann-squared windows using 96 quadrature points per window.',
                  'live_model_scope':'Default grand notes >=32 use .23-cent late detuning; lower notes use .04 cents. Fitted anchor range MIDI'+str(min(pairs))+'..'+str(max(pairs))+'. Outside the measured range and other voicings remain authored extrapolations.' if detune_cents else 'Coherent baseline retained for reproducibility; upright fitting defaults unchanged.',
                  'why_no_low_frequency_fit':'Only the struck note partial-band powers are fitting targets. Sub-fundamental/subsonic/mains energy has unresolved body, room and acquisition confounds; no hum or low-frequency noise is synthesized to fit it.',
                  'heldout_cases_used':False,
              },
              'fitter_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'limits': ('One edited Yamaha upright corpus with ordinal velocity proxies and unknown mic geometry.' if args.upright else 'One Yamaha C5 / close AB pair.')+' Held-out features excluded. Modal reduction is distinct from the preserved mechanical solver. Upper partials beyond measured bands use negligible authored floors.',
              'header_sha256': hashlib.sha256(args.header.read_bytes()).hexdigest(),
              'confidence_priors':priors,
              'fits': fitted}
    if args.split:
        report['locked_split_source'] = str(args.split)
        report['locked_split_sha256'] = hashlib.sha256(args.split.read_bytes()).hexdigest()
        report['locked_before_extraction'] = True
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    print(f'Fitted {len(selected)} training cases; wrote {args.header}')


if __name__ == '__main__': main()
