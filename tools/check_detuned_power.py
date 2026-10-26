#!/usr/bin/env python3
"""Check fitted modal power against independently sampled two-sine signals.

The production fitter's residual is evaluated at known amplitudes/decays with
its numerical optimizer stubbed out. No parameters are fitted. The reference
power comes from the preserved FFT/Hann estimator applied to time-domain sines.
"""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT=Path(__file__).resolve().parents[1]


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    loaded=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def evaluated_prediction(fitter,frequency,powers,fast,late,fast_decay,late_decay,detune_cents):
    # Expose the actual fit residual at a known physical signal, rather than
    # copying the power formula into the test. least_squares never optimizes.
    known=np.array([math.log(fast+late),fast/(fast+late),
                    math.log(late_decay),math.log(fast_decay-late_decay)])
    captured=[]
    def evaluate(residual,initial,**kwargs):
        values=residual(known)
        captured.append(values[:4].copy())
        return SimpleNamespace(x=known,fun=values)
    original=fitter.least_squares
    fitter.least_squares=evaluate
    try:
        decay={name:{'amplitude_sigma_per_second':value,'r_squared':1.}
               for name,value in [('early',fast_decay),('late',late_decay),('overall',late_decay)]}
        fitter.fit_partial({'frequency_hz':frequency,'powers':list(powers),'decay':decay},detune_cents)
    finally:
        fitter.least_squares=original
    if len(captured)!=3 or any(not np.array_equal(captured[0],row) for row in captured[1:]):
        raise AssertionError('Known-state residual evaluation was inconsistent')
    return np.asarray(powers)*10**(captured[0]/10)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    fit_path=ROOT/'tools/fit_live_calibration.py'
    benchmark_path=ROOT/'Research/GrandPianoV2/tools/benchmark.py'
    fitter=module('keyra_phase_power_fitter',fit_path)
    benchmark=module('keyra_phase_power_benchmark',benchmark_path)
    profiles=[('prompt',.12,.025,4.,.5),('shared_late',.07,.06,.5,.25),
              ('treble',.15,.03,4.8,1.7)]
    detune_cents=.23
    cases=[]
    maximum_band_error=0.; maximum_total_error=0.; maximum_legacy_error=0.
    for rate in (44100,48000,96000):
        times=np.arange(int(3.6*rate),dtype=np.float64)/rate
        for frequency in (65.,261.,1050.):
            for name,fast,late,fast_decay,late_decay in profiles:
                late_frequency=frequency*2**(detune_cents/1200)
                # Independent time-domain generation includes both carriers;
                # it does not use the analytical difference-frequency formula.
                wave=(fast*np.exp(-fast_decay*times)*np.sin(2*np.pi*frequency*times)
                      +late*np.exp(-late_decay*times)*np.sin(2*np.pi*late_frequency*times))
                # Opposed channels retain power and also guard the preserved
                # estimator's stereo-power convention against a mono sum.
                stereo=np.column_stack((wave,-wave))
                band_powers=[]; total_powers=[]
                for lo,hi in benchmark.WINDOWS:
                    f,power=benchmark.spectrum(stereo[int(lo*rate):int(hi*rate)],rate)
                    width=min(.38*frequency,max(3/(hi-lo),.004*frequency))
                    band_powers.append(benchmark.integrated_power(f,power,frequency-width,frequency+width))
                    total_powers.append(float(np.sum(power)))
                predicted=evaluated_prediction(fitter,frequency,band_powers,fast,late,fast_decay,late_decay,detune_cents)
                legacy=evaluated_prediction(fitter,frequency,band_powers,fast,late,fast_decay,late_decay,0.)
                band_errors=10*np.log10(predicted/np.asarray(band_powers))
                total_errors=10*np.log10(predicted/np.asarray(total_powers))
                legacy_errors=10*np.log10(legacy/np.asarray(band_powers))
                maximum_band_error=max(maximum_band_error,float(np.max(np.abs(band_errors))))
                maximum_total_error=max(maximum_total_error,float(np.max(np.abs(total_errors))))
                maximum_legacy_error=max(maximum_legacy_error,float(np.max(np.abs(legacy_errors))))
                cases.append({'sample_rate':rate,'frequency_hz':frequency,'profile':name,
                              'fast_amplitude':fast,'late_amplitude':late,
                              'fast_decay_per_second':fast_decay,'late_decay_per_second':late_decay,
                              'sampled_hann_band_power':band_powers,'sampled_hann_total_power':total_powers,
                              'production_model_power':predicted.tolist(),
                              'model_minus_sampled_band_db':band_errors.tolist(),
                              'model_minus_sampled_total_db':total_errors.tolist(),
                              'legacy_coherent_minus_sampled_band_db':legacy_errors.tolist()})
    # Finite spectral bands lose a small amount of leakage; the analytical
    # model also averages carrier cycles and uses 96-point Hann quadrature.
    passed=(maximum_band_error<.02 and maximum_total_error<.02 and maximum_legacy_error>.5)
    result={'schema_version':1,'passed':passed,'fitting_performed':False,
            'fit_source_sha256':sha(fit_path),'estimator_sha256':sha(benchmark_path),
            'detune_cents':detune_cents,'initial_relative_phase_radians':0,
            'case_count':len(cases),'windows_per_case':len(benchmark.WINDOWS),
            'maximum_absolute_band_error_db':maximum_band_error,
            'maximum_absolute_total_error_db':maximum_total_error,
            'maximum_legacy_coherent_band_error_db':maximum_legacy_error,
            'acceptance':{'maximum_absolute_error_db':.02,'minimum_legacy_counterexample_error_db':.5},
            'limits':'Known two-sine signals only, zero initial relative phase, .23-cent detuning, 65/261/1050Hz, 44.1/48/96kHz and the specified positive decay profiles. Checks carrier-averaged/Hann power, not recorded-piano realism, phase identification or the complete engine signal path.',
            'cases':cases}
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({key:value for key,value in result.items() if key!='cases'},indent=2))
    if not passed: raise SystemExit(1)


if __name__=='__main__':main()
