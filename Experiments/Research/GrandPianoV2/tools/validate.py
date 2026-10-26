#!/usr/bin/env python3
"""Reproducible mechanical contracts and score checks for the actual piano POC.

Needs a C++17 compiler. Optional --audio inspects final 48kHz WAVs with scipy/numpy.
No perceptual realism or equivalence to a commercial piano is asserted.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def source_provenance():
    files = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
             for name in ('src/grand.cpp', 'src/calibration.h')}
    composite = hashlib.sha256(json.dumps(files, sort_keys=True,
                                          separators=(',', ':')).encode('utf-8')).hexdigest()
    return {'solver_source_sha256': files['src/grand.cpp'],
            'calibration_sha256': files['src/calibration.h'],
            'model_source_sha256': composite}


def run_json(command):
    r = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"Command failed: {command}\n{r.stdout}\n{r.stderr}")
    return json.loads(r.stdout)


def check_scores():
    reports=[]
    for path in sorted((ROOT/'scores').glob('*.events')):
        active=set(); count=0; last=-1
        for line in path.read_text().splitlines():
            if not line or line.startswith('#'): continue
            t, kind, n, val=line.split(); t=float(t); n=int(n); val=float(val)
            assert t>=last>=-1, path
            last=t
            if kind=='on':
                assert n not in active and 21<=n<=108 and 0<val<=127, (path,line)
                active.add(n); count+=1
            elif kind=='off':
                assert n in active, (path,line)
                active.remove(n)
            else:
                assert kind=='pedal' and 0<=val<=1, (path,line)
        assert not active, (path,active)
        reports.append({'score':path.name,'onsets':count,'last_event_seconds':last})
    assert len(reports)>=5
    return reports


def inspect_audio():
    import numpy as np
    from scipy.io import wavfile
    results=[]
    for path in sorted((ROOT/'renders').glob('*.wav')):
        fs,x=wavfile.read(path)
        if x.dtype.kind in 'iu': x=x.astype(np.float64)/(2**(x.dtype.itemsize*8-1))
        else: x=x.astype(np.float64)
        assert fs==48000 and x.ndim==2 and x.shape[1]==2, path
        assert np.isfinite(x).all() and np.any(x), path
        peak=float(np.max(np.abs(x)))
        assert peak<1, path
        results.append({'file':path.name,'sample_rate':fs,'duration_seconds':len(x)/fs,
                        'sample_peak_dbfs':float(20*np.log10(peak)),
                        'rms_dbfs':float(10*np.log10(np.mean(x*x))),
                        'finite':True})
    assert results, 'No final WAV files found'
    return results


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audio',action='store_true')
    parser.add_argument('--compiler',default='clang++')
    args=parser.parse_args()
    (ROOT/'build').mkdir(exist_ok=True)
    (ROOT/'validation').mkdir(exist_ok=True)
    # Build independently from current source so evidence cannot silently refer
    # to an older engine binary after an implementation change.
    sources=source_provenance()
    subprocess.run([args.compiler,'-std=c++17','-O3','-Wall','-Wextra',
                    'validation/physics_probe.cpp','-o','build/physics_probe'],cwd=ROOT,check=True)
    subprocess.run([args.compiler,'-std=c++17','-O3','-Wall','-Wextra',
                    'src/grand.cpp','-o','build/grand_validation'],cwd=ROOT,check=True)
    if source_provenance()!=sources:
        raise RuntimeError('Model source or calibration changed during compilation; rerun validation')
    report={'source_sha256':sources['solver_source_sha256'], **sources,
            'engine_self_test':run_json(['build/grand_validation','--self-test']),
            'mechanical_contracts':run_json(['build/physics_probe']),
            'scores':check_scores(),
            'scope':'Numerical and behavioral contracts. Recording agreement is evaluated separately in benchmark/candidate_report.json; no blind listening evaluation.'}
    if args.audio: report['audio']=inspect_audio()
    if source_provenance()!=sources:
        raise RuntimeError('Model source or calibration changed during validation; rerun validation')
    report['passed']=report['engine_self_test']['passed'] and report['mechanical_contracts']['passed']
    target=ROOT/'validation'/'report.json'; target.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__': main()
