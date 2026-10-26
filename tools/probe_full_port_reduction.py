#!/usr/bin/env python3
"""One mechanical port-velocity reduction experiment, on copied full API sources.

The baseline enables guarded pressure SIMD. Only the candidate's float bridge
port sum reassociates. Independent double-energy audits precede sound/timing.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import shutil
import subprocess

import numpy as np
from scipy import signal

ROOT=Path(__file__).resolve().parents[1]


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    item=importlib.util.module_from_spec(spec);spec.loader.exec_module(item);return item


rad=module('keyra_port_radiation_tools',ROOT/'tools/probe_full_radiation_simd.py')
budget=rad.budget
INPUTS=[*budget.INPUTS,'src/full_instrument/generate_prepared_model.py',
        'src/full_instrument/prepared_model_provenance.json',
        'tools/probe_full_backend_budget.py','tools/probe_full_radiation_simd.py']

ENERGY=r'''
#pragma once
#include <cmath>
namespace keyra_port {
// The audit promotes before every multiply, including mode squares and the
// physical hammer-displacement sum. It does not call float energy/reductions.
inline double energy(const grand::Piano& model){
  double total=0;
  for(const auto& string:model.strings){const auto& m=string.m;
    for(size_t j=0;j<m.size();++j){
      const double w=double(m.omega[j]),q=double(m.q[j]),p=double(m.p[j]);
      total+=.5*w*w*(q*q+p*p);
    }
  }
  for(const auto& z:model.board){const double q=double(z.q),p=double(z.p);total+=.5*z.w*z.w*(q*q+p*p);}
  for(const auto& key:model.keys)if(key.hammerActive){
    double y=0;for(int i:key.strings){const auto& m=model.strings[i].m;
      for(size_t j=0;j<m.size();++j)y+=double(m.hammer[j])*double(m.q[j]);}
    const double x=key.hammerX-y;
    total+=.5*key.mass*key.hammerV*key.hammerV+(x>0?key.K*std::pow(x,key.power+1)/(key.power+1):0);
  }
  return total;
}
inline double portVelocity(const grand::Modes& m){
  double v=0;for(size_t j=0;j<m.size();++j)v+=double(m.b[j])*double(m.omega[j])*double(m.p[j]);return v;
}
inline std::array<double,3> boardVelocity(const grand::Piano& model){
  std::array<double,3> v{};for(const auto& z:model.board)for(unsigned g=0;g<3;++g)v[g]+=z.port[g]*z.w*double(z.p);return v;
}
}
'''

BRIDGE_PROFILE=r'''
#pragma once
#include <array>
#include <cstdint>
#include <ctime>
namespace keyra_port_profile {
inline std::array<uint64_t,4> elapsed{};
inline uint64_t now(){timespec t{};clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t);return uint64_t(t.tv_sec)*1000000000u+t.tv_nsec;}
inline void add(unsigned stage,uint64_t begin){elapsed[stage]+=now()-begin;}
}
'''

METRICS=r'''

extern "C" void keyra_port_metrics(const keyra::FullInstrument* piano,double* out){
  const auto& model=*piano->impl_->model;
  out[0]=keyra_port::energy(model);out[1]=model.maxContactResidual;
  out[2]=model.maxForce;out[3]=double(model.forceSolves);
#ifdef KEYRA_PORT_PROFILE
  for(unsigned i=0;i<4;++i)out[4+i]=keyra_port_profile::elapsed[i]*1.e-9;
#else
  for(unsigned i=0;i<4;++i)out[4+i]=0;
#endif
}
extern "C" void keyra_port_reset_profile(){
#ifdef KEYRA_PORT_PROFILE
  keyra_port_profile::elapsed={};
#endif
}
'''

PHYSICS=r'''
#include "PreparedModel.h"
#include "EnergyProbe.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <random>
#include <vector>

using grand::Piano;using grand::Options;
bool healthy(const Piano& p){return p.faultFlags==0&&std::isfinite(keyra_port::energy(p));}
void initialize(Piano& p,std::mt19937& random,double amplitude,bool cancel){
  p.resetState();std::normal_distribution<double> normal;
  for(auto& string:p.strings){auto& m=string.m;double sum=0,best=0;size_t pivot=0;
    for(size_t j=0;j<m.size();++j){
      m.p[j]=float(amplitude*normal(random)/double(m.omega[j]));
      const double coefficient=double(m.b[j])*double(m.omega[j]);sum+=coefficient*double(m.p[j]);
      if(std::abs(coefficient)>best){best=std::abs(coefficient);pivot=j;}
    }
    if(cancel&&best>0){const double coefficient=double(m.b[pivot])*double(m.omega[pivot]);m.p[pivot]=float(double(m.p[pivot])-sum/coefficient);}
  }
  for(auto& z:p.board)z.p=cancel?0:float(amplitude*normal(random)/z.w);
}
int main(){
  bool all=true,first=true;std::printf("{\"energy_arithmetic\":\"double promotion before every product; independent physical port sums\",\"bridge_stress\":[");
  for(int rate:{48000,96000}){
    Options o;o.sampleRate=rate;o.loss=0;o.damper=0;o.hammerLoss=0;Piano p(o);
    for(double resistance:{.01,1.,100.})for(double amplitude:{1.e-7,1.e-4,1.e-1})for(bool cancel:{false,true}){
      std::mt19937 random(812);p.opt.bridge=resistance;initialize(p,random,amplitude,cancel);
      const double initial=keyra_port::energy(p);double previous=initial,maxRatio=1,maxRise=0,maxLedger=0,maxPortError=0;
      unsigned positiveSteps=0;bool finite=healthy(p)&&initial>0;
      for(unsigned step=0;step<500;++step){
        std::vector<double> before(p.strings.size());const auto boardBefore=keyra_port::boardVelocity(p);
        for(size_t i=0;i<p.strings.size();++i){const auto& m=p.strings[i].m;before[i]=keyra_port::portVelocity(m);
          double scale=0;for(size_t j=0;j<m.size();++j)scale+=std::abs(double(m.b[j])*double(m.omega[j])*double(m.p[j]));
          maxPortError=std::max(maxPortError,std::abs(m.portVelocity()-before[i])/std::max(scale,1.e-300));}
        p.bridgeStep(p.dt,false);const auto boardAfter=keyra_port::boardVelocity(p);double dissipation=0;
        for(size_t i=0;i<p.strings.size();++i){const auto& string=p.strings[i];
          const double relative=.5*(before[i]+keyra_port::portVelocity(string.m)-boardBefore[string.group]-boardAfter[string.group]);
          dissipation+=p.dt*string.resistance*resistance*relative*relative;}
        const double e=keyra_port::energy(p);finite=finite&&healthy(p)&&e>=0;
        const double rise=(e-previous)/initial;if(rise>0)++positiveSteps;
        maxRise=std::max(maxRise,rise);maxRatio=std::max(maxRatio,e/initial);
        maxLedger=std::max(maxLedger,std::abs(e-previous+dissipation)/initial);previous=e;
      }
      const bool pass=finite&&maxRise<=5.e-7&&maxRatio<=1+5.e-6;all=all&&pass;
      if(!first)std::printf(",");first=false;
      std::printf("{\"rate\":%d,\"bridge_scale\":%.17g,\"amplitude\":%.17g,\"cancelling_ports\":%s,\"steps\":500,\"initial_J\":%.17g,\"final_ratio\":%.17g,\"max_energy_ratio\":%.17g,\"max_step_rise_relative_initial\":%.17g,\"positive_steps\":%u,\"max_physical_work_ledger_residual_relative_initial\":%.17g,\"max_port_sum_error_over_sum_abs_products\":%.17g,\"finite\":%s,\"passed\":%s}",rate,resistance,amplitude,cancel?"true":"false",initial,previous/initial,maxRatio,maxRise,positiveSteps,maxLedger,maxPortError,finite?"true":"false",pass?"true":"false");
    }
  }
  std::printf("],\"isolated_contact\":[");first=true;
  for(int rate:{48000,96000}){
    Options o;o.sampleRate=rate;o.bridge=0;o.loss=0;o.damper=0;o.hammerLoss=0;Piano p(o);
    for(int note:{21,36,60,84,108})for(double velocity:{40.,127.}){
      p.resetState();p.noteOn(note,velocity);const double initial=keyra_port::energy(p);double maxDrift=0;bool finite=true;
      auto& key=p.keys[note-21];unsigned steps=0;
      for(unsigned i=0;i<unsigned(rate*.05);++i){p.oscillators();const bool active=key.hammerActive;key.hammerActive=true;
        const double e=keyra_port::energy(p);finite=finite&&healthy(p)&&e>=0;maxDrift=std::max(maxDrift,std::abs(e-initial)/initial);
        key.hammerActive=active;steps=i+1;if(!active)break;}
      const bool pass=finite&&maxDrift<=5.e-5&&p.maxContactResidual<1.e-8;all=all&&pass;
      if(!first)std::printf(",");first=false;
      std::printf("{\"rate\":%d,\"note\":%d,\"velocity\":%.17g,\"steps\":%u,\"max_relative_energy_drift\":%.17g,\"max_contact_residual\":%.17g,\"fault_flags\":%u,\"finite\":%s,\"passed\":%s}",rate,note,velocity,steps,maxDrift,p.maxContactResidual,p.faultFlags,finite?"true":"false",pass?"true":"false");
    }
  }
  std::printf("],\"free_oscillators\":[");first=true;
  for(int rate:{48000,96000})for(double hz:{27.5,65.,261.6,4186.,12500.})for(bool pStart:{false,true}){
    grand::Modes m;m.add(hz,0,0,0,0,1./rate,1,0);const double w=double(m.omega[0]);
    if(pStart)m.p[0]=float(1/w);else m.q[0]=float(1/w);
    auto energy=[&](){const double q=double(m.q[0]),p=double(m.p[0]);return .5*w*w*(q*q+p*p);};
    const double initial=energy();double maximum=1,final=1;bool finite=true;
    for(unsigned i=0;i<unsigned(rate*10);++i){m.freeDampedStep();final=energy()/initial;finite=finite&&std::isfinite(final)&&final>=0;maximum=std::max(maximum,final);}
    const bool pass=finite&&maximum<=1+5.e-6;all=all&&pass;
    if(!first)std::printf(",");first=false;
    std::printf("{\"rate\":%d,\"hz\":%.17g,\"p_start\":%s,\"seconds\":10,\"max_energy_ratio\":%.17g,\"final_ratio\":%.17g,\"finite\":%s,\"passed\":%s}",rate,hz,pStart?"true":"false",maximum,final,finite?"true":"false",pass?"true":"false");
  }
  std::printf("],\"coupled_unforced_decay\":[");first=true;
  for(int rate:{48000,96000}){
    Options o;o.sampleRate=rate;o.loss=0;o.damper=0;o.hammerLoss=0;Piano p(o);std::mt19937 random(391);initialize(p,random,1.e-5,false);
    const double initial=keyra_port::energy(p);double maximum=1,previous=initial,maxRise=0;bool finite=true;
    std::vector<double> trace;trace.push_back(1);std::vector<unsigned> traceFrames{0};
    for(unsigned frame=0;frame<unsigned(rate*8);++frame){const auto out=p.step(frame);finite=finite&&std::isfinite(out[0])&&std::isfinite(out[1]);
      if((frame+1)%64==0){const double e=keyra_port::energy(p);finite=finite&&healthy(p)&&e>=0;
        maximum=std::max(maximum,e/initial);maxRise=std::max(maxRise,(e-previous)/initial);previous=e;
        if((frame+1)*10/unsigned(rate)>trace.size()-1){trace.push_back(e/initial);traceFrames.push_back(frame+1);}}
    }
    const bool pass=finite&&maximum<=1+1.e-4;all=all&&pass;
    if(!first)std::printf(",");first=false;
    std::printf("{\"rate\":%d,\"seconds\":8,\"initial_J\":%.17g,\"max_energy_ratio\":%.17g,\"max_64frame_energy_rise_relative_initial\":%.17g,\"final_ratio\":%.17g,\"fault_flags\":%u,\"finite\":%s,\"passed\":%s,\"coarse_energy_ratio_trace\":[",rate,initial,maximum,maxRise,previous/initial,p.faultFlags,finite?"true":"false",pass?"true":"false");
    bool firstValue=true;for(double e:trace){if(!firstValue)std::printf(",");firstValue=false;std::printf("%.17g",e);}
    std::printf("],\"trace_frames\":[");firstValue=true;for(unsigned f:traceFrames){if(!firstValue)std::printf(",");firstValue=false;std::printf("%u",f);}std::printf("]}");
  }
  std::printf("],\"passed\":%s}\n",all?"true":"false");return all?0:9;
}
'''


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def once(s,a,b):return rad.once(s,a,b)


def candidate_model(s):
    return once(s,'    float v=0;for(size_t i=0;i<size();++i)v+=portOmega[i]*p[i];return v;',
        '#if defined(KEYRA_FULL_PORT_SIMD) && KEYRA_FULL_PORT_SIMD && (defined(__GNUC__) || defined(__clang__))\n'
        '    const size_t count=size();\n'
        '    const float *__restrict bw=portOmega.data(),*__restrict velocity=p.data();\n'
        '    float v=0;\n'
        '    #pragma omp simd reduction(+:v) simdlen(4)\n'
        '    for(size_t i=0;i<count;++i)v+=bw[i]*velocity[i];\n'
        '    return v;\n'
        '#else\n'
        '    float v=0;for(size_t i=0;i<size();++i)v+=portOmega[i]*p[i];return v;\n'
        '#endif')


def profiled_model(s):
    s=once(s,'#include "PreparedCalibration.h"','#include "PreparedCalibration.h"\n#include "BridgeProfile.h"')
    s=once(s,'    Vec3 boardV{},sum{},beta{};','    auto phaseStart=keyra_port_profile::now();\n    Vec3 boardV{},sum{},beta{};')
    s=once(s,'    Mat3 mat{};for(int g=0;g<3;++g)',
        '    keyra_port_profile::add(0,phaseStart);phaseStart=keyra_port_profile::now();\n    Mat3 mat{};for(int g=0;g<3;++g)')
    s=once(s,'    for(auto &st:strings){\n      auto &k=keys[st.note-21];\n      if(!opt.sympathetic&&!k.everStruck){\n        if(cacheRadiation)',
        '    keyra_port_profile::add(1,phaseStart);phaseStart=keyra_port_profile::now();\n    for(auto &st:strings){\n      auto &k=keys[st.note-21];\n      if(!opt.sympathetic&&!k.everStruck){\n        if(cacheRadiation)')
    s=once(s,'    for(auto &z:board){double force=0;for(int g=0;g<3;++g)',
        '    keyra_port_profile::add(2,phaseStart);phaseStart=keyra_port_profile::now();\n    for(auto &z:board){double force=0;for(int g=0;g<3;++g)')
    s=once(s,'z.p+=step*force/z.w;}\n  }\n  std::array<double,2> step',
        'z.p+=step*force/z.w;}\n    keyra_port_profile::add(3,phaseStart);\n  }\n  std::array<double,2> step')
    return s


def api_source(s):
    s=rad.instrument_api(s)
    s=once(s,'#include "PreparedModel.h"','#include "PreparedModel.h"\n#include "EnergyProbe.h"')
    return s+METRICS


def harness_source():
    s=rad.harness_source()
    s=once(s,'extern "C" bool keyra_simd_snapshot(const keyra::FullInstrument*,const char*);',
        'extern "C" bool keyra_simd_snapshot(const keyra::FullInstrument*,const char*);\n'
        'extern "C" void keyra_port_metrics(const keyra::FullInstrument*,double*);\n'
        'extern "C" void keyra_port_reset_profile();')
    s=once(s,'  if(argc!=2)return 2;','  if(argc!=3)return 2;\n  const unsigned rate=unsigned(std::strtoul(argv[2],nullptr,10));if(rate!=48000&&rate!=96000)return 2;')
    s=once(s,'  const std::array<std::vector<Event>,3> scores', '  std::array<std::vector<Event>,3> scores')
    s=once(s,'  const std::array<unsigned,3> lengths', '  std::array<unsigned,3> lengths')
    s=once(s,'  std::printf("{\\\"cases\\\":[");',
        '  for(auto& score:scores)for(auto& e:score)e.frame*=rate/48000;\n'
        '  for(auto& frames:lengths)frames*=rate/48000;\n'
        '  std::printf("{\\\"cases\\\":[");')
    s=s.replace('config.sampleRate=48000','config.sampleRate=rate')
    s=s.replace('64./48000.','64./rate').replace('frames/48000.','frames/double(rate)')
    s=once(s,'    const auto wallStart=Clock::now();','    keyra_port_reset_profile();\n    const auto wallStart=Clock::now();')
    s=once(s,'    const auto diagnostics=piano.diagnostics();',
        '    const auto diagnostics=piano.diagnostics();\n'
        '    double metrics[8]{};keyra_port_metrics(&piano,metrics);\n'
        '    std::fprintf(stderr,"PORT_METRICS {\\\"name\\\":\\\"%s\\\",\\\"rate\\\":%u,\\\"true_energy_J\\\":%.17g,\\\"max_contact_residual\\\":%.17g,\\\"max_force_N\\\":%.17g,\\\"force_solves\\\":%.17g,\\\"bridge_stage_seconds\\\":[%.17g,%.17g,%.17g,%.17g]}\\n",names[c],rate,metrics[0],metrics[1],metrics[2],metrics[3],metrics[4],metrics[5],metrics[6],metrics[7]);')
    s=once(s,'\\\"sample_rate\\\":48000,\\\"block_frames\\\":64','\\\"sample_rate\\\":%u,\\\"block_frames\\\":64')
    s=once(s,'      names[c],frames,frames/double(rate),','      names[c],rate,frames,frames/double(rate),')
    return s


def peak_changes(a,b,rate):
    # Track baseline-resolved peaks; chord/dense peaks are not unique strings.
    n=len(a);fft_length=8*n;window=np.hanning(n);freq=np.fft.rfftfreq(fft_length,1/rate)
    spectra=[np.mean(np.abs(np.fft.rfft(x*window[:,None],n=fft_length,axis=0))**2,axis=1) for x in (a,b)]
    peaks,_=signal.find_peaks(spectra[0]);peaks=peaks[(freq[peaks]>30)&(freq[peaks]<16000)]
    peaks=sorted(peaks,key=lambda i:spectra[0][i],reverse=True)[:20]
    candidate_peaks,_=signal.find_peaks(spectra[1])
    def refine(power,i):
        y=np.log(np.maximum(power[i-1:i+2],1.e-300));denominator=y[0]-2*y[1]+y[2]
        shift=.5*(y[0]-y[2])/denominator if abs(denominator)>1.e-15 else 0
        return (i+np.clip(shift,-.5,.5))*rate/fft_length
    result=[]
    for i in peaks:
        matches=candidate_peaks[np.abs(candidate_peaks-i)<=2]
        if not len(matches):
            result.append({'baseline_hz':float(refine(spectra[0],i)),'matched':False});continue
        # Match a local maximum to its nearest candidate maximum. Taking the
        # largest bin in a ±2-bin window can select a different stronger peak
        # even for identical inputs, falsely reporting a tuning change.
        j=int(matches[np.argmin(np.abs(matches-i))])
        fa,fb=refine(spectra[0],i),refine(spectra[1],j)
        result.append({'baseline_hz':float(fa),'candidate_hz':float(fb),'matched':True,
            'baseline_relative_peak_db':float(10*np.log10(spectra[0][i]/max(float(spectra[0].max()),1.e-300))),
            'change_cents':float(1200*np.log2(fb/fa))})
    return result


def peak_selfchecks():
    rate=48000;t=np.arange(30720)/rate
    y=np.sin(2*np.pi*261.63*t);reference=np.column_stack((y,.8*y))
    identity=peak_changes(reference,reference,rate)
    error=max(abs(p['change_cents']) for p in identity if p.get('matched'))
    z=np.sin(2*np.pi*261.63*2**(1/1200)*t);shifted=np.column_stack((z,.8*z))
    known=peak_changes(reference,shifted,rate)[0]['change_cents']
    passed=error<1.e-9 and abs(known-1)<.01
    if not passed:raise RuntimeError('Peak-analysis identity/known-tone selfcheck failed')
    return {'identity_max_abs_cents':error,'known_plus1cent_strongest_peak_change_cents':known,
            'known_shift_tolerance_cents':.01,'passed':True}


def attack(a,b,rate):
    results=[]
    for x in (a,b):
        x=np.asarray(x,dtype=np.float64);width=max(1,int(.005*rate))
        env=np.sqrt(np.convolve(np.mean(x*x,axis=1),np.ones(width)/width,mode='full')[:len(x)])
        env=env[:int(.15*rate)];peak=max(float(env.max()),1.e-300)
        crossings=[int(np.argmax(env>=peak*t))/rate for t in (.1,.9)]
        results.append({'rise10_90_ms':1000*(crossings[1]-crossings[0]),'rms_envelope_peak':peak})
    return {'baseline':results[0],'candidate':results[1],
        'rise_error_ms':results[1]['rise10_90_ms']-results[0]['rise10_90_ms'],
        'definition':'Causal5ms stereo RMS,10–90% of first150ms peak; input-event aligned, not measured hammer-contact time.'}


def read_run(folder,rate):
    d=json.loads((folder/'stdout.json').read_text())
    metrics={json.loads(line[len('PORT_METRICS '):])['name']:json.loads(line[len('PORT_METRICS '):])
        for line in (folder/'stderr.txt').read_text().splitlines() if line.startswith('PORT_METRICS ')}
    for row in d['cases']:
        rad.summarize(row);row['physical_metrics']=metrics[row['name']]
        deadline=64/rate
        for kind in ('thread_cpu','wall'):
            values=np.asarray(row['callback_'+kind+'_seconds'])
            row[kind+'_summary']['p95_deadline_multiple']=float(np.percentile(values,95)/deadline)
            row[kind+'_summary']['deadline_misses']=int(np.count_nonzero(values>deadline))
        if metrics[row['name']]['max_contact_residual']>1.e-8:raise RuntimeError('Contact residual gate failed')
    return d


def main():
    global rad,budget,INPUTS
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'out/full-port-reduction')
    parser.add_argument('--report',type=Path,default=ROOT/'Validation/full-port-reduction.json')
    parser.add_argument('--prepare-only',action='store_true')
    parser.add_argument('--run-prepared',action='store_true')
    parser.add_argument('--physics-only',action='store_true')
    parser.add_argument('--reuse-physics',action='store_true')
    parser.add_argument('--input-root',type=Path,default=ROOT,
        help='Repository-layout input root; a frozen input-snapshot reproduces an older measured basis')
    args=parser.parse_args();out=args.output.resolve()
    source_root=args.input_root.resolve()
    if source_root!=ROOT:
        rad=module('keyra_port_frozen_radiation',source_root/'tools/probe_full_radiation_simd.py');budget=rad.budget
        INPUTS=[*budget.INPUTS,'src/full_instrument/generate_prepared_model.py',
            'src/full_instrument/prepared_model_provenance.json',
            'tools/probe_full_backend_budget.py','tools/probe_full_radiation_simd.py']
    analysis_checks=peak_selfchecks()
    flags=['-O3','-DNDEBUG','-std=c++17','-Wall','-Wextra','-Wpedantic','-ffp-contract=off',
        '-fno-exceptions','-fno-rtti','-fno-builtin','-fopenmp-simd','-DKEYRA_FULL_PRESSURE_SIMD=1']
    if args.run_prepared:
        config=json.loads((out/'input-manifest.json').read_text())
        if config['tool_sha256']!=sha(__file__):raise RuntimeError('Tool changed after preparation')
    else:
        if out.exists() and any(out.iterdir()):parser.error('Use a new empty output directory')
        out.mkdir(parents=True,exist_ok=True)
        config={'inputs':{name:sha(source_root/name) for name in INPUTS},'input_root':str(source_root),'tool_sha256':sha(__file__),
            'compiler':subprocess.check_output(['g++','--version'],text=True).splitlines()[0],
            'flags':flags,'pressure_baseline':'Live guarded pressure SIMD explicitly enabled; current zero-gap controller.',
            'port_macro':{'baseline':0,'candidate':1,'profile':0}}
        (out/'input-manifest.json').write_text(json.dumps(config,indent=2)+'\n')
    def verify():
        for name,value in config['inputs'].items():
            if sha(source_root/name)!=value:raise RuntimeError('Input changed: '+name)
    verify()
    if not args.run_prepared:
        api=(source_root/budget.INPUTS[0]).read_text();model=(source_root/budget.INPUTS[1]).read_text()
        if '#if defined(KEYRA_FULL_PRESSURE_SIMD)' not in model:raise RuntimeError('Expected guarded live pressure integration')
        for label in ('baseline','candidate','profile'):
            folder=out/label;folder.mkdir();include=folder/'include'
            for name in budget.INPUTS[3:]:
                target=include/Path(name).relative_to('include');target.parent.mkdir(parents=True,exist_ok=True)
                text=(source_root/name).read_text()
                if name.endswith(('FullInstrument.h','MechanismExciter.h')):text=once(text,'private:','public: // copied diagnostic access')
                target.write_text(text)
            prepared=candidate_model(model) if label=='candidate' else profiled_model(model) if label=='profile' else model
            (folder/'PreparedModel.h').write_text(prepared)
            (folder/'FullInstrument.cpp').write_text(api_source(api))
            (folder/'harness.cpp').write_text(harness_source())
            (folder/'EnergyProbe.h').write_text(ENERGY);(folder/'BridgeProfile.h').write_text(BRIDGE_PROFILE)
            (folder/'ObserverCapture.h').write_text(rad.OBSERVER_HEADER.replace('61440','122880'))
            shutil.copyfile(source_root/budget.INPUTS[2],folder/'PreparedCalibration.h')
            extra=['-DKEYRA_FULL_PORT_SIMD='+('1' if label=='candidate' else '0')]
            if label=='profile':extra+=['-DKEYRA_PORT_PROFILE=1']
            subprocess.run(['g++',*flags,*extra,'-I'+str(include),'-I'+str(folder),
                '-fopt-info-vec-all='+str(folder/'vectorization.txt'),'-c',str(folder/'FullInstrument.cpp'),'-o',str(folder/'api.o')],check=True)
            subprocess.run(['g++',*flags,*extra,'-I'+str(include),'-I'+str(folder),str(folder/'api.o'),str(folder/'harness.cpp'),'-o',str(folder/'probe')],check=True)
            linked=subprocess.check_output(['ldd',str(folder/'probe')],text=True)
            if 'libgomp' in linked or 'libomp' in linked:raise RuntimeError('OpenMP runtime linked')
            (folder/'dynamic-dependencies.txt').write_text(linked)
            if label!='profile':
                (folder/'physics.cpp').write_text(PHYSICS)
                subprocess.run(['g++',*flags,*extra,'-I'+str(include),'-I'+str(folder),str(folder/'physics.cpp'),'-o',str(folder/'physics')],check=True)
            print(label+': prepared',flush=True);verify()
        shutil.copyfile(__file__,out/'probe-tool-input.py')
    if args.prepare_only:
        print('Prepared only; no physics/timing run.',flush=True);return
    result={'schema_version':1,'purpose':__doc__,'platform':platform.platform(),'input_manifest':config,
        'analysis_selfchecks':analysis_checks,
        'thresholds':{'bridge_max_step_rise_relative_initial':5.e-7,'bridge_max_growth_relative_initial':5.e-6,
            'isolated_contact_energy_relative_error':5.e-5,'contact_residual':1.e-8,
            'free_max_growth_relative_initial':5.e-6,'coupled8s_max_growth_relative_initial':1.e-4},
        'limits':'Mechanical reduction order intentionally changes; no byte-parity conservation or inaudibility claim. Independent double energy measures empirical near-passivity of an already approximate float core. No SDK/Reason/multithread qualification; no global fastmath,FMA,OpenMP runtime/worker or canonical adoption.',
        'physics':{},'runs':[],'comparison':{},'bridge_profile':{}}
    if args.reuse_physics:
        receipt=json.loads((out/'physics-report.json').read_text())
        if receipt['input_manifest_sha256']!=sha(out/'input-manifest.json'):raise RuntimeError('Physics input identity mismatch')
        for label,value in receipt['physics_binary_sha256'].items():
            if sha(out/label/'physics')!=value:raise RuntimeError('Physics binary changed')
        result['physics']=receipt['physics']
    else:
        for label in ('baseline','candidate'):
            verify();folder=out/label
            call=subprocess.run([str(folder/'physics')],text=True,capture_output=True)
            (folder/'physics.json').write_text(call.stdout);(folder/'physics-stderr.txt').write_text(call.stderr)
            if call.returncode:raise RuntimeError(f'{label} physics failed; inspect retained output')
            data=json.loads(call.stdout)
            if not data['passed']:raise RuntimeError(label+' failed independent physics gates')
            result['physics'][label]=data;print(label+': physical audits pass',flush=True);verify()
        receipt={'input_manifest_sha256':sha(out/'input-manifest.json'),'physics':result['physics'],
            'physics_binary_sha256':{label:sha(out/label/'physics') for label in ('baseline','candidate')}}
        (out/'physics-report.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
    if args.physics_only:
        print('Physical checks complete; paired timing intentionally deferred.',flush=True);return
    for rate in (48000,96000):
        for trial,order in enumerate((('baseline','candidate'),('candidate','baseline'),('baseline','candidate'))):
            for label in order:
                verify();folder=out/f'rate{rate}'/f'trial{trial}'/label;folder.mkdir(parents=True)
                call=subprocess.run([str(out/label/'probe'),str(folder),str(rate)],text=True,capture_output=True)
                (folder/'stdout.json').write_text(call.stdout);(folder/'stderr.txt').write_text(call.stderr)
                if call.returncode:raise RuntimeError(f'{label} benchmark failed exit{call.returncode}')
                data=read_run(folder,rate)
                result['runs'].append({'rate':rate,'trial':trial,'variant':label,'trace_path':str(folder/'stdout.json'),
                    'trace_sha256':sha(folder/'stdout.json'),'cases':[{k:v for k,v in row.items() if k not in ('events','events_per_block','callback_wall_seconds','callback_thread_cpu_seconds')} for row in data['cases']]})
                print(f'{rate} trial{trial} {label}: '+', '.join(r['name']+'='+format(r['callback_cpu_seconds_per_audio_second'],'.3f') for r in data['cases']),flush=True);verify()
        result['comparison'][str(rate)]={}
        for name in ('music','repeats-pedal','dense-88-tail'):
            folders={label:out/f'rate{rate}'/'trial0'/label for label in ('baseline','candidate')}
            a=np.fromfile(folders['baseline']/(name+'.f64le-pressure'),dtype='<f8').reshape(-1,2)
            b=np.fromfile(folders['candidate']/(name+'.f64le-pressure'),dtype='<f8').reshape(-1,2)
            aa=np.fromfile(folders['baseline']/(name+'.f32le-planar'),dtype='<f4').reshape(2,-1).T
            bb=np.fromfile(folders['candidate']/(name+'.f32le-planar'),dtype='<f4').reshape(2,-1).T
            times={label:[next(c for c in run['cases'] if c['name']==name)['callback_cpu_seconds_per_audio_second']
                for run in result['runs'] if run['rate']==rate and run['variant']==label] for label in ('baseline','candidate')}
            result['comparison'][str(rate)][name]={'pre_highpass_pressure':rad.difference(a,b,rate),
                'float32_output':rad.difference(aa,bb,rate),'attack':attack(a,b,rate),'tracked_resolved_peaks':peak_changes(a,b,rate),
                'peak_tracking_limit':'Baseline-resolved spectrum peaks; chord/dense peaks are not uniquely assigned fundamentals.',
                'cpu_per_audio':times,'paired_speedups':[x/y for x,y in zip(times['baseline'],times['candidate'])],
                'median_cpu_reduction_fraction':1-float(np.median(times['candidate'])/np.median(times['baseline']))}
    folder=out/'bridge-profile-run';folder.mkdir()
    call=subprocess.run([str(out/'profile/probe'),str(folder),'48000'],text=True,capture_output=True)
    (folder/'stdout.json').write_text(call.stdout);(folder/'stderr.txt').write_text(call.stderr)
    if call.returncode:raise RuntimeError('Bridge profile failed')
    prof=read_run(folder,48000)
    for row in prof['cases']:
        name=row['name'];times=row['physical_metrics']['bridge_stage_seconds'];total=sum(times)
        reference=out/'rate48000/trial0/baseline'/(name+'.f32le-planar');audio=folder/(name+'.f32le-planar')
        result['bridge_profile'][name]={'stages':{label:{'thread_cpu_seconds':value,'fraction_of_bridge':value/total}
            for label,value in zip(('board_and_port_force_assembly','junction_solve','impulse_fused_pressure','board_update'),times)},
            'audio_byte_identical_to_control':reference.read_bytes()==audio.read_bytes(),
            'callback_cpu_seconds_per_audio_second':row['callback_cpu_seconds_per_audio_second']}
    verify();result['inputs_unchanged']=True;result['decision']='Pending measured usefulness/stability review; no canonical adoption.'
    args.report.parent.mkdir(parents=True,exist_ok=True);args.report.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    (out/'report.json').write_text(args.report.read_text());print(args.report,flush=True)


if __name__=='__main__':main()
