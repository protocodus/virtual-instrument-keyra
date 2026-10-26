#!/usr/bin/env python3
"""Fit a compact, sample-free modal field from the immutable ten training notes.

The four fixed analysis windows constrain nonnegative prompt/late amplitude
components. Decay priors regularize this underdetermined decomposition; they
are not a claim to identify a unique mechanical piano. Held-out recordings are
never opened by this fitting tool. No recorded audio or phase enters the header.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path

import numpy as np
import scipy
from scipy import optimize

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / 'Experiments/Research/GrandPianoV2'
MODULE = RESEARCH / 'tools/benchmark.py'
spec = importlib.util.spec_from_file_location('keyra_recording_metrics', MODULE)
metrics = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metrics)
PARTIALS = 64


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fit_partial(powers, prompt_prior, late_prior, attack, note, order, frequency):
    """Hann-power quadrature including the engine's exact detuned choir.

    The common audio-frequency carrier averages to 1/2; cross-unison beating
    remains explicit at its difference frequencies, including stereo gains.
    No recorded phase is measured or fitted.
    """
    powers = np.maximum(np.asarray(powers, float), 1e-24)
    times, weights = [], []
    for lo, hi in metrics.WINDOWS:
        t = lo + (np.arange(96) + .5) / 96 * (hi-lo)
        w = np.sin(np.pi*(t-lo)/(hi-lo))**4
        times.append(t)
        weights.append(w/w.sum())
    times, weights = np.asarray(times), np.asarray(weights)
    envelope = 1 - np.exp(-times/attack)
    unisons = 1 if note<=31 else 2 if note<=43 else 3
    detunes = [0] if unisons==1 else [-.38,.43] if unisons==2 else [-.60,.12,.73]
    left = np.zeros_like(times,dtype=complex)
    right = np.zeros_like(times,dtype=complex)
    for u,detune in enumerate(detunes):
        detune *= .7+.45*(note-21)/87
        relative_hz = frequency*(2**(detune/1200)-1)
        phase = .41*order+.79*u
        pan = ((note-64.5)/70+(u-(unisons-1)*.5)*.12)*.75
        phasor = np.exp(1j*(2*np.pi*relative_hz*times+phase))/np.sqrt(unisons)
        left += (1-pan)*phasor
        right += (1+pan)*phasor
    choir_power = .25*(abs(left)**2+abs(right)**2)
    late_prior = float(np.clip(late_prior, .04, 14))
    prompt_prior = float(np.clip(max(prompt_prior, late_prior*1.1), .05, 24))
    # A positive difference maintains promptSigma >= lateSigma. Four power
    # observations cannot uniquely identify four rates/amplitudes: small
    # regularizers keep the fit near robust training-only slope estimates.
    def decode(x):
        amplitude = np.exp(x[0])
        mix = 1/(1+np.exp(-x[1]))
        late = np.exp(x[2])
        prompt = late + np.exp(x[3])
        return amplitude*mix, amplitude*(1-mix), prompt, late
    def residual(x):
        ap, al, sp, sl = decode(x)
        signal = (ap*np.exp(-sp*times)+al*np.exp(-sl*times))*envelope
        prediction = np.sum(weights*choir_power*signal*signal, axis=1)
        data = np.log(np.maximum(prediction, 1e-30)/powers)
        prior = [.12*np.log(sl/late_prior), .12*np.log(sp/prompt_prior), .025*x[1]]
        return np.r_[data, prior]
    amplitude = np.sqrt(2*powers[0])*np.exp(late_prior*.12)
    initial = [np.log(max(amplitude, 1e-12)), 0., np.log(late_prior), np.log(prompt_prior-late_prior)]
    fit = optimize.least_squares(residual, initial,
        bounds=([-30,-6,np.log(.02),np.log(.01)], [3,6,np.log(18),np.log(35)]), max_nfev=100)
    ap, al, sp, sl = decode(fit.x)
    return [float(ap),float(al),float(sp),float(sl)], float(np.mean(np.abs(residual(fit.x)[:4]))*10/np.log(10))


def generate():
    split = json.loads((RESEARCH/'benchmark/split.json').read_text())
    features = json.loads((RESEARCH/'benchmark/reference_features.json').read_text())
    training = [s for s in split['samples'] if s['split']=='train']
    expected = {f'C{o}v{v}' for o in range(2,7) for v in (4,12)}
    assert len(training)==10 and {s['id'] for s in training}==expected
    lookup = {s['id']:s for s in features['samples']}
    mechanical = json.loads((RESEARCH/'benchmark/calibration.json').read_text())
    priors = {k['midi']:k for k in mechanical['keys']}
    rows, errors, sources = [], [], []
    for sample in sorted(training, key=lambda s:(s['midi'],s['midi_velocity'])):
        f = lookup[sample['id']]
        path = RESEARCH/'reference/wav'/(sample['id']+'.wav')
        sr, full = metrics.load_audio(path)
        onset, _ = metrics.onset_index(full, sr)
        x = full[onset:onset+int(4*sr)]
        # Use the frozen pitch estimate, and extend the same fixed-window
        # measurement from 48 to 64 partials for the low register only.
        frequencies = metrics.partial_frequencies(f['f1_hz'], f['B'], np.arange(1,65))
        powers = np.zeros((4,PARTIALS))
        for j,(lo,hi) in enumerate(metrics.WINDOWS):
            hz, power = metrics.spectrum(x[int(lo*sr):int(hi*sr)],sr)
            for k,center in enumerate(frequencies):
                width = min(.38*f['f1_hz'], max(3/(hi-lo), .004*center))
                if center < min(17000,sr*.44):
                    powers[j,k] = metrics.integrated_power(hz,power,center-width,center+width)
        attack = float(np.clip(f['attack']['rise10_90_seconds']/np.log(9), .001, .1))
        modes=[]
        for k in range(PARTIALS):
            if frequencies[k] >= min(17000,sr*.44) or max(powers[:,k]) < f['early_rms']**2*1e-7:
                modes.append([0.,0.,1.,.5]); continue
            p = priors[sample['midi']]
            mode,error = fit_partial(powers[:,k],p['sigma_prompt'][k],p['sigma_late'][k],attack,
                                     sample['midi'],k+1,frequencies[k])
            modes.append(mode); errors.append(error)
        rows.append({'id':sample['id'],'note':sample['midi'],'velocity':sample['midi_velocity'],
                     'f1':f['f1_hz'],'B':f['B'],'attackSeconds':attack,'modes':modes})
        sources.append({'id':sample['id'],'wav_sha256':digest(path)})
    return rows, {'schema_version':1,'training_ids':[r['id'] for r in rows],
        'heldout_measurements_used':False,'sample_free':True,
        'reference_features_sha256':digest(RESEARCH/'benchmark/reference_features.json'),
        'split_sha256':digest(RESEARCH/'benchmark/split.json'),'metric_source_sha256':digest(MODULE),
        'calibration_prior_sha256':digest(RESEARCH/'benchmark/calibration.json'),
        'fitter_source_sha256':digest(Path(__file__)),
        'tool_versions':{'numpy':np.__version__,'scipy':scipy.__version__},
        'recordings':sources,'partial_count':PARTIALS,
        'amplitude_model':'Exact authored detuned-unison stereo difference-frequency power times (Ap*exp(-sp*t)+Al*exp(-sl*t))^2*(1-exp(-t/attackSeconds))^2; Hann-power quadrature',
        'choir_model':{'phase':'.41*order+.79*unison','normalization':'1/sqrt(unisons)',
                       'pan':'((note-64.5)/70+(u-(unisons-1)/2)*.12)*.75',
                       'detune_cents':'[-.38,.43] or [-.60,.12,.73], times .7+.45*(note-21)/87'},
        'identification_limit':'Positive prompt/late decomposition regularized by measured training slopes; not a unique mechanical identification.',
        'training_window_power_mean_absolute_error_db':float(np.mean(errors))}


def header(rows):
    def f(x):
        value=f'{float(x):.9g}'
        return value+('f' if '.' in value or 'e' in value else '.0f')
    lines=['// Generated by Tools/fit_realtime_modal.py; TRAIN10 only, no waveform/IR/phase.',
           '// This is a reduced empirical radiation model, not the preserved physical solver.',
           '#pragma once','#include <array>','namespace keyra { namespace measured {',
           'constexpr int partials=64;',
           'struct Partial { float promptAmplitude, lateAmplitude, promptSigma, lateSigma; };',
           'struct Anchor { int note; int velocity; float f1,B,attackSeconds; std::array<Partial,64> modes; };',
           'constexpr std::array<Anchor,10> anchors={{']
    for row in rows:
        lines.append('  {'+str(row['note'])+','+str(row['velocity'])+','+','.join(f(row[k]) for k in ('f1','B','attackSeconds'))+',{{')
        lines.extend('    {'+','.join(map(f,mode))+'},' for mode in row['modes'])
        lines.append('  }}},')
    lines.extend(['}};','}} // namespace keyra::measured',''])
    return '\n'.join(lines)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true')
    parser.add_argument('--header',type=Path,default=ROOT/'Source/DSP/MeasuredModalData.h')
    parser.add_argument('--metadata',type=Path,default=ROOT/'Docs/research/realtime-modal-fit-2026-10-26.json')
    args=parser.parse_args()
    rows,metadata=generate(); content=header(rows)
    metadata['generated_header_sha256']=hashlib.sha256(content.encode()).hexdigest()
    if args.check:
        if args.header.read_text()!=content:
            raise SystemExit('Measured modal header differs from regenerated TRAIN10 fit')
        stored=json.loads(args.metadata.read_text())
        if stored!=metadata:
            raise SystemExit('Measured modal metadata differs from regenerated provenance and fit')
        print('TRAIN10 modal header reproduces exactly');return
    args.header.parent.mkdir(parents=True,exist_ok=True)
    args.header.write_text(content)
    args.metadata.parent.mkdir(parents=True,exist_ok=True)
    args.metadata.write_text(json.dumps(metadata,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:metadata[k] for k in ('training_ids','heldout_measurements_used','training_window_power_mean_absolute_error_db')},indent=2))
if __name__=='__main__':main()
