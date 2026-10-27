#!/usr/bin/env python3
"""Bounded float pressure-reduction SIMD experiment on copied full API sources.

Only observer summation order may change. No global fast math, FMA, OpenMP
runtime, port-velocity reassociation, mechanical update or mode cut is allowed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import re
import shutil
import subprocess

import numpy as np
from scipy import signal

ROOT=Path(__file__).resolve().parents[1]
BUDGET=ROOT/'tools/probe_full_backend_budget.py'
spec=importlib.util.spec_from_file_location('keyra_budget_harness',BUDGET)
budget=importlib.util.module_from_spec(spec);spec.loader.exec_module(budget)
INPUTS=[*budget.INPUTS,'tools/probe_full_backend_budget.py']

OBSERVER_HEADER=r'''
#pragma once
#include <array>
namespace keyra_simd {
inline std::array<double,61440> pressure{};
}
'''

SNAPSHOT=r'''

// Copied-header access exposure is for this serialized diagnostic only. It
// changes no storage/layout; no output observer/filter values enter this file.
extern "C" bool keyra_simd_snapshot(const keyra::FullInstrument* piano,const char* path) {
  const auto& impl=*piano->impl_;const auto& model=*impl.model;
  FILE* file=std::fopen(path,"wb");if(!file)return false;bool ok=true;
  auto scalar=[&](const auto& x){ok=ok&&std::fwrite(&x,sizeof(x),1,file)==1;};
  auto vector=[&](const auto& x){ok=ok&&std::fwrite(x.data(),sizeof(x[0]),x.size(),file)==x.size();};
  const uint32_t version=1;scalar(version);scalar(impl.frame);
  scalar(model.dt);scalar(model.pedal);scalar(model.pedalTarget);
  scalar(model.maxForce);scalar(model.contactTime);scalar(model.maxContactResidual);
  scalar(model.forceSolves);scalar(model.faultFlags);scalar(model.bridgeFaults);scalar(model.contactFaults);
  for(const auto& string:model.strings){
    vector(string.m.q);vector(string.m.p);vector(string.m.damp);
    scalar(string.velocity);scalar(string.force);
  }
  for(const auto& key:model.keys){
    scalar(key.hammerX);scalar(key.hammerV);scalar(key.age);scalar(key.K);
    scalar(key.maxForce);scalar(key.contactSeconds);scalar(key.down);scalar(key.hammerActive);
    scalar(key.everStruck);scalar(key.damperPosition);scalar(key.cachedContact);scalar(key.cachedLoss);
  }
  for(const auto& z:model.board){scalar(z.q);scalar(z.p);scalar(z.force);}
  for(const auto& mechanism:impl.mechanisms){
    for(const auto& mode:mechanism.modes_){scalar(mode.x);scalar(mode.v);}
  }
  for(int note=21;note<=108;++note){
    const auto& s=impl.controller.state(note);
    scalar(s.down);scalar(s.pending);scalar(s.hasLaunched);scalar(s.lastActive);scalar(s.releasedSinceLaunch);
    scalar(s.recovery);scalar(s.returnDepth);scalar(s.keyLift);scalar(s.returnVelocity);
    scalar(s.elapsedSinceLaunch);scalar(s.pendingAge);scalar(s.pendingVelocity);scalar(s.pendingLift);
    scalar(s.pendingVelocityFactor);scalar(s.pendingHardnessFactor);
    scalar(s.correlatedVelocity);scalar(s.correlatedHardness);scalar(s.random);
    scalar(s.requests);scalar(s.launches);scalar(s.pendingId);
  }
  const auto& s=impl.controller.statistics();
  scalar(s.requests);scalar(s.launches);scalar(s.deferred);scalar(s.coalesced);scalar(s.cancelled);scalar(s.expired);
  scalar(s.retiredBeforeSeparation);scalar(s.invalidObservations);
  if(std::fclose(file)!=0)ok=false;
  return ok;
}
'''


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def once(s,a,b):
    if s.count(a)!=1:raise ValueError('Non-unique source target: '+a[:80])
    return s.replace(a,b,1)


def simd_model(s,kind='pragma'):
    if kind in ('pointer','pointer-control'):
        start=s.index('  std::array<double,2> portImpulseRadiation(double impulse){')
        end=s.index('\n\n};',start)
        replacement='''  std::array<double,2> portImpulseRadiation(double impulse){
    const float impulseValue=static_cast<float>(impulse);
    const size_t count=size();
    float *__restrict yp=p.data();
    const float *__restrict bi=portInverse.data(),*__restrict yq=q.data();
    const float *__restrict ql=radQL.data(),*__restrict pl=radPL.data();
    const float *__restrict qr=radQR.data(),*__restrict pr=radPR.data();
    float l=0,r=0;
    #pragma omp simd reduction(+:l,r) simdlen(4)
    for(size_t i=0;i<count;++i){
      yp[i]+=bi[i]*impulseValue;
      l+=ql[i]*yq[i]+pl[i]*yp[i];
      r+=qr[i]*yq[i]+pr[i]*yp[i];
    }
    return {l,r};
  }
  std::array<double,2> radiation()const{
    const size_t count=size();
    const float *__restrict yp=p.data(),*__restrict yq=q.data();
    const float *__restrict ql=radQL.data(),*__restrict pl=radPL.data();
    const float *__restrict qr=radQR.data(),*__restrict pr=radPR.data();
    float l=0,r=0;
    #pragma omp simd reduction(+:l,r) simdlen(4)
    for(size_t i=0;i<count;++i){
      l+=ql[i]*yq[i]+pl[i]*yp[i];
      r+=qr[i]*yq[i]+pr[i]*yp[i];
    }
    return {l,r};
  }'''
        if kind=='pointer-control':
            replacement=replacement.replace('    #pragma omp simd reduction(+:l,r) simdlen(4)\n','')
        return s[:start]+replacement+s[end:]
    s=once(s,'    for(size_t i=0;i<size();++i){\n      yp[i]+=bi[i]*impulseValue;\n      l+=',
             '    #pragma omp simd reduction(+:l,r)\n    for(size_t i=0;i<size();++i){\n      yp[i]+=bi[i]*impulseValue;\n      l+=')
    s=once(s,'    float l=0,r=0;\n    for(size_t i=0;i<size();++i){l+=radQL[i]*q[i]+radPL[i]*p[i];r+=radQR[i]*q[i]+radPR[i]*p[i];}',
             '    float l=0,r=0;\n    #pragma omp simd reduction(+:l,r)\n    for(size_t i=0;i<size();++i){l+=radQL[i]*q[i]+radPL[i]*p[i];r+=radQR[i]*q[i]+radPR[i]*p[i];}')
    return s


def instrument_api(api):
    api=once(api,'#include "PreparedModel.h"','#include "PreparedModel.h"\n#include "ObserverCapture.h"\n#include <cstdio>')
    api=once(api,'    auto x=impl_->step();','    auto x=impl_->step();\n    keyra_simd::pressure[2*impl_->frame]=x[0];keyra_simd::pressure[2*impl_->frame+1]=x[1];')
    return api+SNAPSHOT


def harness_source():
    s=budget.HARNESS
    s=once(s,'#include "keyra/FullInstrument.h"','#include "keyra/FullInstrument.h"\n#include "ObserverCapture.h"\nextern "C" bool keyra_simd_snapshot(const keyra::FullInstrument*,const char*);')
    s=once(s,'const auto cpuStart=std::clock();','')
    s=once(s,'      if(wall>64./48000.)++misses;',
             '      if(wall>64./48000.)++misses;\n'
             '      const unsigned end=start+64;\n'
             '      if(end==64||end==512||end==4096||end==8192||end==frames){\n'
             '        const auto statePath=directory+"/"+names[c]+"-"+std::to_string(end)+".mechanical";\n'
             '        if(!keyra_simd_snapshot(&piano,statePath.c_str()))return 9;\n'
             '      }')
    s=once(s,'    const double processCpu=double(std::clock()-cpuStart)/CLOCKS_PER_SEC,totalWall=seconds(wallStart,Clock::now());',
             '    double processCpu=0;for(double t:cpus)processCpu+=t;const double totalWall=seconds(wallStart,Clock::now());')
    s=once(s,'    std::fclose(audio);',
             '    std::fclose(audio);\n'
             '    FILE* pressure=std::fopen((directory+"/"+names[c]+".f64le-pressure").c_str(),"wb");if(!pressure)return 10;\n'
             '    if(std::fwrite(keyra_simd::pressure.data(),sizeof(double),2*frames,pressure)!=2*frames)return 11;\n'
             '    std::fclose(pressure);')
    return s


def difference(a,b,sr=48000):
    # A float32 output's quantized samples remain unchanged; promote the
    # analysis arithmetic so sub-micro-dB changes are not rounded away.
    a=np.asarray(a,dtype=np.float64);b=np.asarray(b,dtype=np.float64)
    def db(x):return 10*np.log10(max(float(x),1.e-300))
    power=float(np.mean(a*a));delta=b-a
    rms_ratio=np.sqrt(power/max(float(np.mean(b*b)),1.e-300))
    result={'reference_rms':float(np.sqrt(power)),
            'exactly_equal':bool(np.array_equal(a,b)),
            'null_metric_floor_db':-3000,
            'null_rms_db_relative_reference':db(np.mean(delta*delta)/max(power,1.e-300)),
            'level_matched_null_rms_db':db(np.mean((b*rms_ratio-a)**2)/max(power,1.e-300)),
            'rms_change_db':db(np.mean(b*b)/max(power,1.e-300)),
            'maximum_absolute_sample_difference':float(np.max(np.abs(delta))),
            'finite':bool(np.isfinite(a).all() and np.isfinite(b).all()),
            'stereo_windows':{},'spectral_bands':[]}
    for name,lo,hi in (('attack',0,.1),('sustain',.1,len(a)/sr)):
        start,end=int(lo*sr),min(len(a),int(hi*sr))
        if end-start<2:continue
        stats=[]
        for x in (a[start:end],b[start:end]):
            corr=float(np.corrcoef(x.T)[0,1]);balance=db(np.mean(x[:,1]**2)/max(float(np.mean(x[:,0]**2)),1.e-300))
            stats.append({'correlation':corr,'right_minus_left_db':balance})
        result['stereo_windows'][name]={'baseline':stats[0],'candidate':stats[1],
            'correlation_change':stats[1]['correlation']-stats[0]['correlation'],
            'balance_change_db':stats[1]['right_minus_left_db']-stats[0]['right_minus_left_db']}
    nperseg=min(4096,len(a))
    f,pa=signal.welch(a,sr,axis=0,nperseg=nperseg,noverlap=nperseg//2)
    _,pb=signal.welch(b,sr,axis=0,nperseg=nperseg,noverlap=nperseg//2)
    pa=np.mean(pa,axis=1);pb=np.mean(pb,axis=1)
    for lo,hi in ((0,250),(250,1000),(1000,4000),(4000,12000),(12000,20000)):
        mask=(f>=lo)&(f<hi);p=float(np.sum(pa[mask]));q=float(np.sum(pb[mask]))
        result['spectral_bands'].append({'band_hz':[lo,hi],'baseline_power':p,'candidate_power':q,'candidate_minus_baseline_db':db(q/max(p,1.e-300))})
    return result


def summarize(row):
    deadline=64/48000
    for name in ('thread_cpu','wall'):
        values=np.asarray(row['callback_'+name+'_seconds'])
        row[name+'_summary']={'p50_ms':float(np.percentile(values,50)*1000),
            'p95_ms':float(np.percentile(values,95)*1000),'max_ms':float(values.max()*1000),
            'p95_deadline_multiple':float(np.percentile(values,95)/deadline),
            'deadline_misses':int(np.count_nonzero(values>deadline)),'callbacks':len(values)}
    row['callback_cpu_seconds_per_audio_second']=row['process_cpu_seconds']/row['audio_seconds']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'out/full-radiation-simd')
    parser.add_argument('--report',type=Path,default=ROOT/'Validation/full-radiation-simd.json')
    parser.add_argument('--candidate',choices=('pragma','pointer','pointer-control'),default='pragma')
    args=parser.parse_args();out=args.output.resolve()
    if out.exists() and any(out.iterdir()):parser.error('Use a new empty output directory')
    out.mkdir(parents=True,exist_ok=True)
    input_hashes={name:sha(ROOT/name) for name in INPUTS}
    def verify():
        for name,value in input_hashes.items():
            if sha(ROOT/name)!=value:raise RuntimeError('Source changed during experiment: '+name)
    flags=['-O3','-DNDEBUG','-std=c++17','-Wall','-Wextra','-Wpedantic',
           '-ffp-contract=off','-fno-exceptions','-fno-rtti','-fno-builtin','-fopenmp-simd']
    api=instrument_api((ROOT/INPUTS[0]).read_text());model=(ROOT/INPUTS[1]).read_text()
    harness=harness_source()
    result={'schema_version':1,'purpose':__doc__,'compiler':subprocess.check_output(['g++','--version'],text=True).splitlines()[0],
            'platform':platform.platform(),'input_sha256':input_hashes,'tool_sha256':sha(__file__),'flags':flags,
            'candidate_kind':args.candidate,
            'allowed_difference':'Only float pressure reduction summation order in Modes::portImpulseRadiation/radiation; all updates/port/contact/bridge arithmetic keep their original expressions and order.',
            'timing_scope':'Three paired trials AB,BA,AB using the existing actual-API three-case schedules. Callback thread CPU includes event dispatch, process and identical raw-pressure capture; excludes checkpoint serialization/prepare/audio writes. Snapshot copies expose private members solely for diagnostic access; layout is unchanged.',
            'snapshot_scope':'At frames64,512,4096,8192,andfinal for each case: all string q/p/damp, string velocity/force, board q/p/force, hammer position/velocity/age/hardness/contact/damper state, pedal, solver counters, all controller states/RNG/recovery and mechanical source x/v. No struct padding is serialized. Observer caches, output high-pass/filter state and pressure are intentionally excluded.',
            'variants':{},'runs':[],'comparisons':{},'limits':'Shared Linux GCC host only; OpenMP SIMD compiler support in SDK is untested. No global fast math/FMA/OpenMP runtime, auditory/inaudibility claim, scalar fallback replacement or canonical adoption.'}
    for label in ('baseline','simd'):
        verify();folder=out/label;folder.mkdir();include=folder/'include'
        for name in INPUTS[3:-1]:
            target=include/Path(name).relative_to('include');target.parent.mkdir(parents=True,exist_ok=True)
            text=(ROOT/name).read_text()
            if name.endswith(('FullInstrument.h','MechanismExciter.h')):
                text=once(text,'private:','public: // diagnostic copied-header access only')
            target.write_text(text)
        (folder/'FullInstrument.cpp').write_text(api)
        (folder/'PreparedModel.h').write_text(simd_model(model,args.candidate) if label=='simd' else model)
        shutil.copyfile(ROOT/INPUTS[2],folder/'PreparedCalibration.h')
        (folder/'ObserverCapture.h').write_text(OBSERVER_HEADER)
        (folder/'harness.cpp').write_text(harness)
        subprocess.run(['g++',*flags,'-I'+str(include),'-I'+str(folder),
            '-fopt-info-vec-all='+str(folder/'api-vectorization.txt'),'-c',str(folder/'FullInstrument.cpp'),'-o',str(folder/'api.o')],check=True)
        subprocess.run(['g++',*flags,'-I'+str(include),'-I'+str(folder),'-c',str(folder/'harness.cpp'),'-o',str(folder/'harness.o')],check=True)
        subprocess.run(['g++',*flags,str(folder/'api.o'),str(folder/'harness.o'),'-o',str(folder/'probe')],check=True)
        linked=subprocess.check_output(['ldd',str(folder/'probe')],text=True)
        if re.search(r'lib(gomp|omp)',linked):raise RuntimeError('Unexpected OpenMP runtime linkage')
        result['variants'][label]={'binary_sha256':sha(folder/'probe'),'dynamic_dependencies':linked,
            'compiled_source_sha256':{name:sha(folder/name) for name in ('FullInstrument.cpp','PreparedModel.h','PreparedCalibration.h','ObserverCapture.h','harness.cpp')},
            'vectorization_report':{'path':str(folder/'api-vectorization.txt'),'sha256':sha(folder/'api-vectorization.txt')}}
        print(label+': compiled',flush=True)
    for trial,order in enumerate((('baseline','simd'),('simd','baseline'),('baseline','simd'))):
        for label in order:
            verify();folder=out/label;run=out/f'trial{trial}'/label;run.mkdir(parents=True)
            call=subprocess.run([str(folder/'probe'),str(run)],text=True,capture_output=True)
            (run/'stdout.json').write_text(call.stdout);(run/'stderr.txt').write_text(call.stderr)
            if call.returncode:raise RuntimeError(f'{label} trial{trial} failed exit{call.returncode}: {call.stderr}')
            data=json.loads(call.stdout)
            for row in data['cases']:summarize(row)
            result['runs'].append({'trial':trial,'variant':label,'trace':{'path':str(run/'stdout.json'),'sha256':sha(run/'stdout.json')},
                'cases':[{k:v for k,v in row.items() if k not in ('callback_wall_seconds','callback_thread_cpu_seconds','events_per_block','events')} for row in data['cases']]})
            print(f'trial{trial} {label}: '+', '.join(r['name']+'='+format(r['callback_cpu_seconds_per_audio_second'],'.3f') for r in data['cases']),flush=True)
            verify()
    for name in ('music','repeats-pedal','dense-88-tail'):
        checkpoints=[];all_states=True
        for trial in range(3):
            baseline=out/f'trial{trial}/baseline';candidate=out/f'trial{trial}/simd'
            for path in sorted(baseline.glob(name+'-*.mechanical')):
                other=candidate/path.name;equal=path.read_bytes()==other.read_bytes();all_states=all_states and equal
                checkpoints.append({'trial':trial,'checkpoint':path.name,'bytes':path.stat().st_size,
                    'baseline_sha256':sha(path),'candidate_sha256':sha(other),'byte_identical':equal})
                if not equal:raise RuntimeError('Mechanical state changed: '+str(path))
        a=np.fromfile(out/'trial0/baseline'/(name+'.f64le-pressure'),dtype='<f8').reshape(-1,2)
        b=np.fromfile(out/'trial0/simd'/(name+'.f64le-pressure'),dtype='<f8').reshape(-1,2)
        audio_a=np.fromfile(out/'trial0/baseline'/(name+'.f32le-planar'),dtype='<f4').reshape(2,-1).T
        audio_b=np.fromfile(out/'trial0/simd'/(name+'.f32le-planar'),dtype='<f4').reshape(2,-1).T
        times={}
        for label in ('baseline','simd'):
            times[label]=[next(c for c in r['cases'] if c['name']==name)['callback_cpu_seconds_per_audio_second'] for r in result['runs'] if r['variant']==label]
        result['comparisons'][name]={'mechanical_checkpoints':checkpoints,'all_mechanical_snapshots_byte_identical':all_states,
            'pre_highpass_float64_pressure':difference(a,b),'api_float32_output':difference(audio_a,audio_b),
            'baseline_cpu_per_audio':times['baseline'],'candidate_cpu_per_audio':times['simd'],
            'paired_speedup':[x/y for x,y in zip(times['baseline'],times['simd'])],
            'median_cpu_reduction_fraction':1-float(np.median(times['simd'])/np.median(times['baseline']))}
        for trial in (1,2):
            for label in ('baseline','simd'):
                for suffix in ('.f64le-pressure','.f32le-planar'):
                    p=out/f'trial{trial}'/label/(name+suffix);q=out/'trial0'/label/(name+suffix)
                    if p.read_bytes()!=q.read_bytes():raise RuntimeError('Repeated-run sound not deterministic: '+str(p))
    verify();result['all_mechanical_snapshots_byte_identical']=True;result['inputs_unchanged']=True
    result['decision']='Pending explicit measured-gain review; this report never adopts a candidate.'
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    (out/'report.json').write_text(args.report.read_text())
    shutil.copyfile(__file__,out/'probe-tool-input.py')
    shutil.copyfile(BUDGET,out/'budget-harness-input.py')
    print(args.report,flush=True)


if __name__=='__main__':main()
