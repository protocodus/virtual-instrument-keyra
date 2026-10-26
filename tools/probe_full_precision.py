#!/usr/bin/env python3
"""Bounded precision experiment on the complete original working piano model.

Never modifies src/ or Research/. Floating-point candidates are experimental,
not claims of inaudibility or native plugin readiness. No recording is opened.
"""
from __future__ import annotations
import argparse
import difflib
import hashlib
import json
import math
import platform
import statistics
import subprocess
from pathlib import Path

import numpy as np
from scipy.io import wavfile

ROOT = Path(__file__).resolve().parents[1]
PINNED_SOURCE = '0de379e97ceb26851c92c19f41f065bc554346e916dc0b91bac5117a1c4267e2'

PHYSICS_TEMPLATE = r'''
// Generated experiment harness. Replace @SOURCE@ with an absolute source path.
// This does not change the reference renderer's own self-test or thresholds.
#define main keyra_precision_renderer_main
#include "@SOURCE@"
#undef main
#include <array>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <random>

namespace precision_probe {
using grand::Piano;

// Promote before every product, including squares, so the audit itself never
// accidentally uses float products when the tested state storage is float.
double energy(const Piano& piano) {
  double result=0;
  for(const auto& string:piano.strings) {
    const auto& m=string.m;
    for(size_t j=0;j<m.size();++j) {
      const double w=static_cast<double>(m.omega[j]);
      const double q=static_cast<double>(m.q[j]);
      const double p=static_cast<double>(m.p[j]);
      result+=.5*w*w*(q*q+p*p);
    }
  }
  for(const auto& m:piano.board) {
    const double w=static_cast<double>(m.w);
    const double q=static_cast<double>(m.q);
    const double p=static_cast<double>(m.p);
    result+=.5*w*w*(q*q+p*p);
  }
  for(const auto& k:piano.keys) if(k.hammerActive) {
    double displacement=0;
    for(int index:k.strings) {
      const auto& m=piano.strings[index].m;
      for(size_t j=0;j<m.size();++j)
        displacement+=static_cast<double>(m.hammer[j])*static_cast<double>(m.q[j]);
    }
    result+=.5*k.mass*k.hammerV*k.hammerV+
      Piano::potential(k.hammerX-displacement,k.K,k.power);
  }
  return result;
}

bool finiteStates(const Piano& piano) {
  for(const auto& string:piano.strings) {
    const auto& m=string.m;
    for(size_t j=0;j<m.size();++j)
      if(!std::isfinite(static_cast<double>(m.q[j]))||
         !std::isfinite(static_cast<double>(m.p[j])))return false;
    if(!std::isfinite(string.velocity)||!std::isfinite(string.force))return false;
    for(double value:string.cachedRadiation)if(!std::isfinite(value))return false;
  }
  for(const auto& m:piano.board)
    if(!std::isfinite(static_cast<double>(m.q))||
       !std::isfinite(static_cast<double>(m.p))||!std::isfinite(m.force))return false;
  for(const auto& k:piano.keys)
    if(!std::isfinite(k.hammerX)||!std::isfinite(k.hammerV)||
       !std::isfinite(k.age)||!std::isfinite(k.maxForce)||
       !std::isfinite(k.contactSeconds)||!std::isfinite(k.damperPosition))return false;
  return std::isfinite(piano.maxForce)&&std::isfinite(piano.contactTime)&&
    std::isfinite(piano.maxContactResidual);
}

void printNumber(double value) {
  if(std::isfinite(value))std::cout<<value;
  else std::cout<<"null";
}

struct FreeResult {
  double hz=0;
  bool pStart=false,finite=true;
  double maxDrift=0,finalRatio=1,rotationNormMinusOne=0;
};
}

int main() {
  using namespace grand;
  using namespace precision_probe;
  try {
    Options contactOptions;
    contactOptions.sampleRate=192000;
    contactOptions.bridge=0;
    contactOptions.hammerLoss=0;
    contactOptions.loss=0;
    contactOptions.damper=0;
    Piano contactPiano(contactOptions);
    contactPiano.noteOn(60,100);
    contactPiano.setDamping();
    const double contactInitial=precision_probe::energy(contactPiano);
    auto& key=contactPiano.keys[60-21];
    bool contactFinite=finiteStates(contactPiano)&&std::isfinite(contactInitial)&&contactInitial>0;
    bool contactNonnegative=contactInitial>=0;
    double contactMaxDrift=0,contactMin=contactInitial;
    unsigned contactSteps=0;
    // Match the original contact audit: retain hammer energy for the audit
    // sample immediately after the production backcheck deactivates it.
    for(unsigned i=0;i<2400;++i) {
      contactPiano.oscillators();
      const bool active=key.hammerActive;
      key.hammerActive=true;
      const double current=precision_probe::energy(contactPiano);
      contactFinite=contactFinite&&finiteStates(contactPiano)&&std::isfinite(current);
      contactNonnegative=contactNonnegative&&current>=0;
      if(std::isfinite(current)) {
        contactMaxDrift=std::max(contactMaxDrift,std::abs(current-contactInitial)/contactInitial);
        contactMin=std::min(contactMin,current);
      }
      key.hammerActive=active;
      contactSteps=i+1;
      if(!contactFinite||!active)break;
    }
    const bool contactPassed=contactFinite&&contactNonnegative&&
      contactMaxDrift<=5e-5&&contactPiano.maxContactResidual<1e-8;

    Options bridgeOptions;
    bridgeOptions.sampleRate=96000;
    bridgeOptions.loss=0;
    bridgeOptions.damper=0;
    bridgeOptions.hammerLoss=0;
    Piano bridgePiano(bridgeOptions);
    std::mt19937 random(812);
    std::normal_distribution<double> normal;
    for(auto& string:bridgePiano.strings)for(size_t j=0;j<string.m.size();++j)
      string.m.p[j]=normal(random)*1e-5/static_cast<double>(string.m.omega[j]);
    for(auto& mode:bridgePiano.board)mode.p=normal(random)*1e-5/static_cast<double>(mode.w);
    const double bridgeInitial=precision_probe::energy(bridgePiano);
    double bridgePrevious=bridgeInitial,bridgeMaxRise=0,bridgeMaxEnergyRatio=1;
    bool bridgeFinite=finiteStates(bridgePiano)&&std::isfinite(bridgeInitial)&&bridgeInitial>0;
    bool bridgeNonnegative=bridgeInitial>=0;
    for(unsigned i=0;i<200;++i) {
      bridgePiano.bridgeStep(bridgePiano.dt);
      const double current=precision_probe::energy(bridgePiano);
      bridgeFinite=bridgeFinite&&finiteStates(bridgePiano)&&std::isfinite(current);
      bridgeNonnegative=bridgeNonnegative&&current>=0;
      if(std::isfinite(current)) {
        bridgeMaxRise=std::max(bridgeMaxRise,(current-bridgePrevious)/bridgeInitial);
        bridgeMaxEnergyRatio=std::max(bridgeMaxEnergyRatio,current/bridgeInitial);
      }
      bridgePrevious=current;
      if(!bridgeFinite)break;
    }
    const double bridgeFinalRatio=bridgePrevious/bridgeInitial;
    const bool bridgePassed=bridgeFinite&&bridgeNonnegative&&
      bridgeMaxRise<=5e-7&&bridgeFinalRatio<=1+5e-6;

    constexpr int freeRate=48000,freeSteps=freeRate*10;
    std::array<FreeResult,6> freeResults{};
    size_t resultIndex=0;
    double freeMaxDrift=0,maxRotationExcess=-std::numeric_limits<double>::infinity();
    double maxAbsRotationError=0;
    bool freeFinite=true;
    for(double hz:{65.0,261.6,4186.0})for(bool pStart:{false,true}) {
      Modes mode;
      mode.add(hz,0,0,0,0,1.0/freeRate,1,0);
      const double w=static_cast<double>(mode.omega[0]);
      if(pStart)mode.p[0]=1/w;else mode.q[0]=1/w;
      auto modeEnergy=[&]() {
        const double q=static_cast<double>(mode.q[0]),p=static_cast<double>(mode.p[0]);
        return .5*w*w*(q*q+p*p);
      };
      FreeResult result;
      result.hz=hz;result.pStart=pStart;
      const double c=static_cast<double>(mode.c[0]),s=static_cast<double>(mode.s[0]);
      result.rotationNormMinusOne=c*c+s*s-1;
      maxRotationExcess=std::max(maxRotationExcess,result.rotationNormMinusOne);
      maxAbsRotationError=std::max(maxAbsRotationError,std::abs(result.rotationNormMinusOne));
      const double initial=modeEnergy();
      result.finite=std::isfinite(initial)&&initial>0;
      for(int i=0;i<freeSteps;++i) {
        mode.freeStep();mode.finishDamping();
        const double current=modeEnergy();
        result.finite=result.finite&&std::isfinite(static_cast<double>(mode.q[0]))&&
          std::isfinite(static_cast<double>(mode.p[0]))&&std::isfinite(current)&&current>=0;
        if(!result.finite)break;
        result.finalRatio=current/initial;
        result.maxDrift=std::max(result.maxDrift,std::abs(result.finalRatio-1));
      }
      freeFinite=freeFinite&&result.finite;
      freeMaxDrift=std::max(freeMaxDrift,result.maxDrift);
      freeResults[resultIndex++]=result;
    }
    const bool freePassed=freeFinite&&freeMaxDrift<=1e-3;
    const bool topologyPassed=contactPiano.keys.size()==88&&contactPiano.strings.size()==230&&
      contactPiano.modeCount()==17778&&contactPiano.board.size()==475&&
      bridgePiano.keys.size()==contactPiano.keys.size()&&
      bridgePiano.strings.size()==contactPiano.strings.size()&&
      bridgePiano.modeCount()==contactPiano.modeCount()&&
      bridgePiano.board.size()==contactPiano.board.size();
    const bool passed=topologyPassed&&contactPassed&&bridgePassed&&freePassed;
    std::cout<<std::boolalpha<<std::setprecision(17);
    std::cout<<"{\"passed\":"<<passed<<",\"topology\":{\"passed\":"<<topologyPassed
      <<",\"keys\":"<<contactPiano.keys.size()<<",\"strings\":"<<contactPiano.strings.size()
      <<",\"string_modes\":"<<contactPiano.modeCount()<<",\"board_modes\":"<<contactPiano.board.size()
      <<",\"unison_ports\":"<<contactPiano.unisonPorts.size()
      <<",\"unison_groups\":"<<contactPiano.unisonGroups.size()<<"}"
      <<",\"contact\":{\"passed\":"<<contactPassed<<",\"finite_states\":"<<contactFinite
      <<",\"nonnegative_energy\":"<<contactNonnegative<<",\"steps\":"<<contactSteps
      <<",\"initial_energy_J\":";
    printNumber(contactInitial);
    std::cout<<",\"max_relative_energy_error\":";printNumber(contactMaxDrift);
    std::cout<<",\"minimum_energy_ratio\":";printNumber(contactMin/contactInitial);
    std::cout<<",\"max_relative_residual\":";printNumber(contactPiano.maxContactResidual);
    std::cout<<",\"energy_error_tolerance\":5e-5,\"residual_tolerance\":1e-8}"
      <<",\"bridge\":{\"passed\":"<<bridgePassed<<",\"finite_states\":"<<bridgeFinite
      <<",\"nonnegative_energy\":"<<bridgeNonnegative<<",\"steps\":200"
      <<",\"initial_energy_J\":";printNumber(bridgeInitial);
    std::cout<<",\"max_relative_step_energy_increase\":";printNumber(bridgeMaxRise);
    std::cout<<",\"max_energy_ratio\":";printNumber(bridgeMaxEnergyRatio);
    std::cout<<",\"final_energy_ratio\":";printNumber(bridgeFinalRatio);
    std::cout<<",\"step_increase_tolerance\":5e-7,\"final_increase_tolerance\":5e-6}"
      <<",\"free_oscillator\":{\"passed\":"<<freePassed<<",\"finite_states\":"<<freeFinite
      <<",\"sample_rate\":"<<freeRate<<",\"duration_seconds\":10,\"steps_per_case\":"<<freeSteps
      <<",\"max_relative_energy_drift\":";printNumber(freeMaxDrift);
    std::cout<<",\"max_rotation_norm_excess\":";printNumber(maxRotationExcess);
    std::cout<<",\"max_abs_rotation_norm_error\":";printNumber(maxAbsRotationError);
    std::cout<<",\"energy_drift_tolerance\":1e-3,\"cases\":[";
    for(size_t i=0;i<freeResults.size();++i) {
      if(i)std::cout<<',';
      const auto& result=freeResults[i];
      std::cout<<"{\"frequency_hz\":"<<result.hz<<",\"start\":\""<<(result.pStart?"p":"q")
        <<"\",\"finite_states\":"<<result.finite<<",\"max_relative_energy_drift\":";
      printNumber(result.maxDrift);
      std::cout<<",\"final_energy_ratio\":";printNumber(result.finalRatio);
      std::cout<<",\"rotation_norm_minus_one\":";printNumber(result.rotationNormMinusOne);
      std::cout<<'}';
    }
    std::cout<<"]}}\n";
    // Diagnostics remain consumable for rejected profiles; inspect `passed`.
    return 0;
  }catch(const std::exception& error) {
    // Constant JSON avoids invalid output if an exception message has quotes.
    std::cerr<<"precision physics probe: "<<error.what()<<'\n';
    std::cout<<"{\"passed\":false,\"exception\":true}\n";
    return 1;
  }
}
'''


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def replace(source, old, new):
    if source.count(old) != 1:
        raise ValueError('Source transform must match exactly once: ' + old[:80])
    return source.replace(old, new, 1)


def precision(source, coefficients=False):
    begin = source.index('struct Modes {')
    end = source.index('\nstruct String {', begin)
    modes = source[begin:end]
    modes = replace(modes,
        'std::vector<double> q,p,c,s,omega,hammer,b,forceQ,forceP,loss,damper,damp;',
        'std::vector<float> q,p;\n  std::vector<double> c,s,omega,hammer,b,forceQ,forceP,loss,damper,damp;')
    modes = modes.replace('double *__restrict yq=', 'float *__restrict yq=')
    modes = modes.replace('double *__restrict yp=', 'float *__restrict yp=')
    if coefficients:
        modes = modes.replace('std::vector<double>', 'std::vector<float>')
        modes = modes.replace('const double *__restrict', 'const float *__restrict')
        # Float oscillator kernels; nonlinear contact and all scalar sums stay double.
        modes = modes.replace('double v=yp[i]*yd[i],y=yq[i];', 'float v=yp[i]*yd[i],y=yq[i];')
        modes = modes.replace('double rotated=yc[i]*v-ys[i]*y;', 'float rotated=yc[i]*v-ys[i]*y;')
    # Explicit double products in energy and reductions, including state-only profile.
    for old, new in [
        ('omega[i]*omega[i]*(q[i]*q[i]+p[i]*p[i])', 'double(omega[i])*omega[i]*(double(q[i])*q[i]+double(p[i])*p[i])'),
        ('y+=hammer[i]*q[i]', 'y+=double(hammer[i])*q[i]'),
        ('v+=portOmega[i]*p[i]', 'v+=double(portOmega[i])*p[i]'),
        ('l+=radQL[i]*q[i]+radPL[i]*yp[i]', 'l+=double(radQL[i])*q[i]+double(radPL[i])*yp[i]'),
        ('r+=radQR[i]*q[i]+radPR[i]*yp[i]', 'r+=double(radQR[i])*q[i]+double(radPR[i])*yp[i]'),
        ('l+=radQL[i]*q[i]+radPL[i]*p[i]', 'l+=double(radQL[i])*q[i]+double(radPL[i])*p[i]'),
        ('r+=radQR[i]*q[i]+radPR[i]*p[i]', 'r+=double(radQR[i])*q[i]+double(radPR[i])*p[i]')]:
        modes = modes.replace(old, new)
    source = source[:begin] + modes + source[end:]
    source = replace(source, 'double q=0,p=0,w=0,c=0,s=0,damp=1,sigma=0,force=0;',
                     'float q=0,p=0;\n  double w=0,c=0,s=0,damp=1,sigma=0,force=0;')
    source = source.replace('std::array<double*,3> velocityState', 'std::array<float*,3> velocityState')
    source = source.replace('std::array<double*,3> velocity{}', 'std::array<float*,3> velocity{}')
    source = source.replace('double *__restrict p0=velocity[0]', 'float *__restrict p0=velocity[0]')
    if coefficients:
        source = replace(source, 'double coefficient=0;\n  std::array<float*,3> velocityState',
                         'float coefficient=0;\n  std::array<float*,3> velocityState')
        source = replace(source, 'std::array<double,3> omega{},inverseOmega{};',
                         'std::array<float,3> omega{},inverseOmega{};')
        source = replace(source, 'std::array<std::vector<double>,3> omega,inverse;',
                         'std::array<std::vector<float>,3> omega,inverse;')
        source = replace(source, 'std::vector<double> coefficient;', 'std::vector<float> coefficient;')
        for prefix in ('w0=omega[0]', 'r0=inverse[0]', 'c=coefficient.data()'):
            source = source.replace('const double *__restrict ' + prefix,
                                    'const float *__restrict ' + prefix)
        source = source.replace('double sum=w0[i]*p0[i]', 'double sum=double(w0[i])*p0[i]')
        source = source.replace('sum+=w1[i]*p1[i]', 'sum+=double(w1[i])*p1[i]')
        source = source.replace('sum+=w2[i]*p2[i]', 'sum+=double(w2[i])*p2[i]')
        source = source.replace('double sum=u.omega[0]*', 'double sum=double(u.omega[0])*')
        source = source.replace('sum+=u.omega[1]*', 'sum+=double(u.omega[1])*')
        source = source.replace('sum+=u.omega[2]*', 'sum+=double(u.omega[2])*')
        source = source.replace('opt.bridge*m.b[j]*H[ch]', 'opt.bridge*double(m.b[j])*H[ch]')
        source = source.replace('st.compliance+=st.m.b[j]*st.m.b[j]', 'st.compliance+=double(st.m.b[j])*st.m.b[j]')
        source = source.replace('k.contactCompliance+=st.m.hammer[j]*st.m.forceQ[j]',
                                'k.contactCompliance+=double(st.m.hammer[j])*st.m.forceQ[j]')
    source = source.replace('double l=m.baseQL[j]*m.q[j]+m.basePL[j]*m.p[j],r=m.baseQR[j]*m.q[j]+m.basePR[j]*m.p[j]',
                            'double l=double(m.baseQL[j])*m.q[j]+double(m.basePL[j])*m.p[j],r=double(m.baseQR[j])*m.q[j]+double(m.basePR[j])*m.p[j]')
    return source


def timing(source):
    source = replace(source, '#include <chrono>', '#include <chrono>\n#include <ctime>')
    source = replace(source, 'auto start=std::chrono::steady_clock::now();size_t next=0;',
                     'auto cpuStart=std::clock();auto start=std::chrono::steady_clock::now();size_t next=0;')
    source = replace(source,
        'double wall=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();',
        'double wall=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();double processCpu=double(std::clock()-cpuStart)/CLOCKS_PER_SEC;')
    return replace(source, '<<p.energy()<<"}";', '<<p.energy()<<",\\\"process_cpu_seconds\\\":"<<processCpu<<"}";')


def hot_precision(source):
    """True float hot kernels, double nonlinear/contact/junction solves.

    The conservative coefficient bias is deliberate added numerical loss; its
    ten-second drift must be reported rather than called a free accuracy gain.
    """
    source=precision(source,True)
    begin=source.index('struct Modes {');end=source.index('\nstruct String {',begin)
    modes=source[begin:end]
    modes=replace(modes,
        'q.push_back(0);p.push_back(0);c.push_back(std::cos(phase));s.push_back(std::sin(phase));omega.push_back(w);',
        '''q.push_back(0);p.push_back(0);
    float cf=static_cast<float>(std::cos(phase)),sf=static_cast<float>(std::sin(phase));
    // A rounded float rotation must not inject energy. Bias only the larger
    // component toward zero; the resulting loss is measured by the probe.
    while(double(cf)*cf+double(sf)*sf>1.0){
      if(std::abs(cf)>=std::abs(sf))cf=std::nextafter(cf,0.0f);
      else sf=std::nextafter(sf,0.0f);
    }
    c.push_back(cf);s.push_back(sf);omega.push_back(w);''')
    modes=modes.replace('double y=0;for(size_t i=0;i<size();++i)y+=double(hammer[i])*q[i]',
                        'float y=0;for(size_t i=0;i<size();++i)y+=hammer[i]*q[i]')
    modes=modes.replace('double v=0;for(size_t i=0;i<size();++i)v+=double(portOmega[i])*p[i]',
                        'float v=0;for(size_t i=0;i<size();++i)v+=portOmega[i]*p[i]')
    modes=replace(modes,'void force(double f){',
                  'void force(double f){\n    const float forceValue=static_cast<float>(f);')
    modes=modes.replace('fq[i]*f','fq[i]*forceValue').replace('fp[i]*f','fp[i]*forceValue')
    modes=replace(modes,'void portImpulse(double impulse){',
                  'void portImpulse(double impulse){\n    const float impulseValue=static_cast<float>(impulse);')
    modes=replace(modes,'std::array<double,2> portImpulseRadiation(double impulse){',
                  'std::array<double,2> portImpulseRadiation(double impulse){\n    const float impulseValue=static_cast<float>(impulse);')
    modes=modes.replace('bi[i]*impulse','bi[i]*impulseValue')
    modes=modes.replace('double l=0,r=0;', 'float l=0,r=0;')
    for field in ('radQL','radPL','radQR','radPR'):
        modes=modes.replace(f'double({field}[i])',f'{field}[i]')
    source=source[:begin]+modes+source[end:]
    begin=source.index('struct UnisonGroup {');end=source.index('\nclass Piano {',begin)
    group=source[begin:end]
    group=group.replace('double sum=double(w0[i])*p0[i]', 'float sum=w0[i]*p0[i]')
    group=group.replace('sum+=double(w1[i])*p1[i]', 'sum+=w1[i]*p1[i]')
    group=group.replace('sum+=double(w2[i])*p2[i]', 'sum+=w2[i]*p2[i]')
    group=group.replace('double impulse=c[i]*sum;', 'float impulse=c[i]*sum;')
    return source[:begin]+group+source[end:]


def hot_experiment(args,source,folder):
    """One targeted follow-up, keeping the completed mixed-profile evidence."""
    original_report=folder/'report.json'
    previous=json.loads(original_report.read_text())
    assert previous['source_sha256']==PINNED_SOURCE
    assert previous['flags']==['-O3','-DNDEBUG','-std=c++17','-ffp-contract=off']
    baseline=folder/'baseline'
    assert sha(baseline)==previous['variants']['baseline']['binary_sha256']
    flags=previous['flags'];label='hot_f32_biased';candidate=hot_precision(source)
    snapshot=folder/f'{label}.cpp';snapshot.write_text(candidate)
    compiled=folder/f'{label}.timed.cpp';compiled.write_text(timing(candidate))
    binary=folder/label
    run([args.compiler,*flags,str(compiled),'-o',binary],folder/f'{label}-compile')
    (folder/f'{label}.patch').write_text(''.join(difflib.unified_diff(source.splitlines(True),candidate.splitlines(True),fromfile='baseline.cpp',tofile=label+'.cpp')))
    template=folder/'physics-template.cpp.in'
    physics=folder/f'{label}-physics.cpp';physics.write_text(template.read_text().replace('@SOURCE@',snapshot.name))
    physics_binary=folder/f'{label}-physics'
    run([args.compiler,*flags,str(physics),'-o',physics_binary],folder/f'{label}-physics-compile')
    physical=json.loads(run([physics_binary],folder/f'{label}-physics-run'))
    physical['free_oscillator']['maximum_extra_energy_loss_db_over10s']=max(
        max(0.,-10*math.log10(row['final_energy_ratio'])) for row in physical['free_oscillator']['cases'])
    physical['free_oscillator']['energy_growth_within5e_6']=all(
        row['final_energy_ratio']<=1+5e-6 for row in physical['free_oscillator']['cases'])
    result={'schema_version':1,'profile':label,'source_sha256':PINNED_SOURCE,
        'calibration_sha256':sha(folder/'calibration.h'),'tool_sha256':sha(Path(__file__)),
        'baseline_report_sha256':sha(original_report),'flags':flags,
        'compiler':subprocess.check_output([args.compiler,'--version'],text=True).splitlines()[0],
        'description':'Float state/coefficient/free/force/port/unison/radiation hot kernels and per-string reductions. Force/impulse cast once per string. Double contact, hammer and 3x3 bridge solve. Rounded rotation norm biased <=1; added numerical loss is intentional and measured.',
        'candidate_source_sha256':sha(snapshot),'candidate_compiled_source_sha256':sha(compiled),
        'candidate_binary_sha256':sha(binary),'baseline_binary_sha256':sha(baseline),
        'precision_physics':physical,'cases':{},'limits':'No global fast math, no removed mode or physical operator, no audibility conclusion from null/energy alone. Short shared-host timing experiment, not a plugin deadline guarantee.'}
    fresh_audio={}
    for case,note in [('C4hard',60),('music_prefix',None)]:
        old=previous['cases'][case];events=folder/(case+'.events' if case!='music_prefix' else 'music-prefix.events')
        rate,duration=old['sample_rate'],old['duration_seconds'];row={}
        for version,executable in [('baseline',baseline),(label,binary)]:
            output=folder/f'hot-comparison-{version}-{case}.wav'
            command=[executable,'--events',events,'--output',output,'--sample-rate',str(rate),'--duration',str(duration)]
            metrics=json.loads(run(command,folder/f'hot-comparison-{version}-{case}'))
            assert (metrics['string_count'],metrics['string_modes'],metrics['board_modes'],metrics['nonfinite_samples'])==(230,17778,475,0)
            sr,x=load(output);assert sr==rate;fresh_audio[version,case]=x
            row[version]={'metrics':metrics,'audio_sha256':sha(output),'file':str(output)}
            print('hot render',case,version,metrics['process_cpu_seconds'],flush=True)
        row['speedup']=row['baseline']['metrics']['process_cpu_seconds']/row[label]['metrics']['process_cpu_seconds']
        row['difference']=compare(fresh_audio['baseline',case],fresh_audio[label,case],rate,note)
        result['cases'][case]=row
    result['initial_speedup_geomean']=float(np.exp(np.mean(np.log([x['speedup'] for x in result['cases'].values()]))))
    result['broadened']=False
    result['initial_decision']='Broaden only after root review of a clear speed win; this file contains the bounded C4/music screen.'
    segments={version:np.concatenate([fresh_audio[version,'C4hard'],np.zeros((9600,2)),fresh_audio[version,'music_prefix']]) for version in ('baseline',label)}
    gains={version:.08/np.sqrt(np.mean(x*x)) for version,x in segments.items()}
    common=10**(-2/20)/max(np.max(abs(x*gains[version])) for version,x in segments.items())
    result['listening_exports']={}
    for version,x in segments.items():
        path=folder/f'listening-hot-screen-{version}.wav';wavfile.write(path,48000,(x*gains[version]*common).astype(np.float32))
        result['listening_exports'][version]={'file':str(path),'sha256':sha(path),'whole_file_rms_gain':float(gains[version]),'shared_peak_gain':float(common),
            'segments':['C4 hard note/release','first1s original nocturne'],'music_start_seconds':1.4,'limits':'Labeled dry48k screen; complete-file RMS matched, not a blind listening result.'}
    result['canonical_source_unchanged']=sha(ROOT/'src/full_reference/grand.cpp')==PINNED_SOURCE
    path=folder/'hot-report.json';path.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'report':str(path),'screen_speedup':result['initial_speedup_geomean'],'cases':{k:v['speedup'] for k,v in result['cases'].items()}},indent=2))


def broaden_hot(args,folder):
    screen=folder/'hot-report.json';result=json.loads(screen.read_text())
    previous=json.loads((folder/'report.json').read_text());label=result['profile']
    assert result['initial_speedup_geomean']>1.15,'Do not broaden a failed speed screen'
    assert result['source_sha256']==PINNED_SOURCE
    assert sha(folder/label)==result['candidate_binary_sha256']
    assert sha(folder/'baseline')==result['baseline_binary_sha256']
    result['screen_report_sha256']=sha(screen)
    result['broaden_tool_sha256']=sha(Path(__file__))
    result['additional_paired_cases']={};audio={}
    cases=[('C2soft',36),('C6hard',84),('mixed192k',None),('C4hard',60),('music_prefix',None)]
    for case,note in cases:
        old=previous['cases'][case];rate,duration=old['sample_rate'],old['duration_seconds']
        filename='music-prefix.events' if case=='music_prefix' else 'mixed.events' if case=='mixed192k' else case+'.events'
        events=folder/filename;row={}
        # Reverse the candidate/baseline order from the initial screen.
        for version in (label,'baseline'):
            output=folder/f'hot-extended-{version}-{case}.wav'
            metrics=json.loads(run([folder/version,'--events',events,'--output',output,'--sample-rate',str(rate),'--duration',str(duration)],folder/f'hot-extended-{version}-{case}'))
            assert (metrics['string_count'],metrics['string_modes'],metrics['board_modes'],metrics['nonfinite_samples'])==(230,17778,475,0)
            sr,x=load(output);assert sr==rate;audio[version,case]=x
            row[version]={'metrics':metrics,'audio_sha256':sha(output),'file':str(output)}
            print('extended hot render',case,version,metrics['process_cpu_seconds'],flush=True)
        row['speedup']=row['baseline']['metrics']['process_cpu_seconds']/row[label]['metrics']['process_cpu_seconds']
        row['difference']=compare(audio['baseline',case],audio[label,case],rate,note)
        result['additional_paired_cases'][case]=row
    result['paired_cpu_summary']={}
    for case in ('C4hard','music_prefix'):
        rows=[result['cases'][case],result['additional_paired_cases'][case]]
        medians={version:statistics.median(row[version]['metrics']['process_cpu_seconds'] for row in rows) for version in ('baseline',label)}
        result['paired_cpu_summary'][case]={'pairs':2,'baseline_median_cpu_seconds':medians['baseline'],
            'candidate_median_cpu_seconds':medians[label],'speedup_ratio_of_medians':medians['baseline']/medians[label],
            'order':'Initial baseline then candidate; follow-up candidate then baseline.'}
    result['broadened']=True
    result['initial_decision']='Performance gain reproduced; candidate retained for listening and further long-tail/dynamics validation, not promoted to default.'
    segments={version:np.concatenate([piece for case in ('C2soft','C4hard','C6hard','music_prefix') for piece in (audio[version,case],np.zeros((9600,2)))]) for version in ('baseline',label)}
    gains={version:.08/np.sqrt(np.mean(x*x)) for version,x in segments.items()}
    common=10**(-2/20)/max(np.max(abs(x*gains[version])) for version,x in segments.items())
    result['full_listening_exports']={}
    for version,x in segments.items():
        path=folder/f'listening-full-hot-{version}.wav';wavfile.write(path,48000,(x*gains[version]*common).astype(np.float32))
        result['full_listening_exports'][version]={'file':str(path),'sha256':sha(path),'whole_file_rms_gain':float(gains[version]),'shared_peak_gain':float(common),
            'segments':['C2soft','C4hard','C6hard','music_prefix'],'segment_starts_seconds':[0,1.4,2.8,4.2],
            'limits':'Labeled dry48k excerpts, complete-file RMS matched. Shared sample-peak ceiling; no blind listening verdict.'}
    result['canonical_source_unchanged']=sha(ROOT/'src/full_reference/grand.cpp')==PINNED_SOURCE
    path=folder/'hot-broadened-report.json';path.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'report':str(path),'paired_cpu_summary':result['paired_cpu_summary'],'additional_speedups':{k:v['speedup'] for k,v in result['additional_paired_cases'].items()}},indent=2))


def audit_hot_free_rates(args,folder):
    """Cheap supplemental rate/maximum-energy audit; no additional audio render."""
    report=json.loads((folder/'hot-broadened-report.json').read_text())
    source=folder/(report['profile']+'.cpp')
    assert sha(source)==report['candidate_source_sha256']
    probe=folder/'hot-free-rates.cpp'
    text=r'''#define main keyra_precision_cli_main
#include "@SOURCE@"
#undef main
int main(){
  using namespace grand;
  std::cout<<std::setprecision(17)<<"{\"rates\":[";
  bool firstRate=true;
  for(int rate:{48000,192000}){
    if(!firstRate)std::cout<<',';firstRate=false;
    Options options;options.sampleRate=rate;Piano prepared(options);
    std::vector<double> floors;double maximumNorm=0,minimumNorm=2;
    for(auto& st:prepared.strings)for(size_t j=0;j<st.m.size();++j){
      double c=st.m.c[j],s=st.m.s[j],norm=c*c+s*s;
      maximumNorm=std::max(maximumNorm,norm);minimumNorm=std::min(minimumNorm,norm);
      floors.push_back(-.5*rate*std::log(norm));
    }
    std::sort(floors.begin(),floors.end());
    auto quantile=[&](double q){return floors[size_t(q*(floors.size()-1))];};
    std::cout<<"{\"sample_rate\":"<<rate<<",\"prepared_string_modes\":"<<prepared.modeCount()
      <<",\"rotation_norm_squared_min\":"<<minimumNorm<<",\"rotation_norm_squared_max\":"<<maximumNorm
      <<",\"rotation_only_amplitude_decay_sigma_per_second\":{\"median\":"<<quantile(.5)
      <<",\"p95\":"<<quantile(.95)<<",\"max\":"<<quantile(1)<<"},\"free_cases\":[";
    bool first=true;
    for(double hz:{65.,261.6,4186.})for(bool pStart:{false,true}){
      if(!first)std::cout<<',';first=false;
      Modes m;m.add(hz,0,0,0,0,1./rate,1,0);
      double w=m.omega[0];if(pStart)m.p[0]=1/w;else m.q[0]=1/w;
      auto energy=[&](){double q=m.q[0],p=m.p[0];return .5*w*w*(q*q+p*p);};
      double initial=energy(),minimum=1,maximum=1,final=1;bool finite=true;
      for(int i=0;i<rate*10;++i){
        m.freeStep();m.finishDamping();final=energy()/initial;
        finite=finite&&std::isfinite(final)&&final>=0;
        minimum=std::min(minimum,final);maximum=std::max(maximum,final);
      }
      std::cout<<"{\"frequency_hz\":"<<hz<<",\"start\":\""<<(pStart?"p":"q")
        <<"\",\"finite\":"<<(finite?"true":"false")<<",\"minimum_energy_ratio\":"<<minimum
        <<",\"maximum_energy_ratio\":"<<maximum<<",\"final_energy_ratio\":"<<final
        <<",\"extra_energy_loss_db_over10s\":"<<-10*std::log10(final)<<'}';
    }
    std::cout<<"]}";
  }
  std::cout<<"]}\n";
}
'''
    probe.write_text(text.replace('@SOURCE@',source.name));binary=folder/'hot-free-rates'
    run([args.compiler,*report['flags'],str(probe),'-o',binary],folder/'hot-free-rates-compile')
    result=json.loads(run([binary],folder/'hot-free-rates-run'))
    result.update({'candidate_source_sha256':sha(source),'probe_source_sha256':sha(probe),
        'probe_binary_sha256':sha(binary),'tool_sha256':sha(Path(__file__)),
        'broadened_report_sha256':sha(folder/'hot-broadened-report.json'),
        'limits':'Rotation-only loss and six lossless oscillator tests; full coupled long-pedal dynamics are not established. Norm<=1 is a coefficient property, not proof of floating-update passivity.',
        'future_compensation_not_applied':'For rotation radius R<=1, consider d_eff=min(1,d_original/R) at every damping update. This could offset some rotation loss for damped modes; zero-loss modes retain a numerical decay floor. Requires separate validation.'})
    for row in result['rates']:
        row['all_six_cases_finite']=all(case['finite'] for case in row['free_cases'])
        row['maximum_energy_ratio_over_all_steps']=max(case['maximum_energy_ratio'] for case in row['free_cases'])
        row['energy_growth_within5e_6']=row['maximum_energy_ratio_over_all_steps']<=1+5e-6
        row['maximum_extra_loss_db_over10s']=max(case['extra_energy_loss_db_over10s'] for case in row['free_cases'])
    path=folder/'hot-free-rates-report.json';path.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'report':str(path),'rate_summary':[{k:v for k,v in row.items() if k!='free_cases'} for row in result['rates']]},indent=2))


def run(command, log):
    call = subprocess.run([str(x) for x in command], text=True, capture_output=True)
    log.with_suffix('.stdout.txt').write_text(call.stdout)
    log.with_suffix('.stderr.txt').write_text(call.stderr)
    if call.returncode:
        raise RuntimeError(f'Command failed: {command[0]}; see {log}.stderr.txt')
    return call.stdout


def load(path):
    rate, data = wavfile.read(path)
    if data.dtype != np.float32 or data.ndim != 2 or data.shape[1] != 2 or not np.isfinite(data).all():
        raise ValueError('Expected finite float32 stereo WAV: ' + str(path))
    return rate, data.astype(np.float64)


def db_ratio(a, b):
    return float(10 * np.log10(max(float(a), 1e-30) / max(float(b), 1e-30)))


def stereo(x):
    power = np.mean(x*x, axis=0)
    return {'correlation': float(np.mean(x[:, 0]*x[:, 1])/max(np.sqrt(np.prod(power)), 1e-30)),
            'right_minus_left_db': db_ratio(power[1], power[0])}


def spectrum(x, rate):
    n = len(x); window = np.hanning(n)
    z = np.fft.rfft(x*window[:, None], axis=0)
    return np.fft.rfftfreq(n, 1/rate), np.sum(abs(z)**2, axis=1)


def pitch(x, rate, expected):
    # Same estimator on both versions; compares their dominant fundamental peak,
    # not a claim of physical tuning accuracy from this short excerpt.
    channel = int(np.argmax(np.mean(x*x, axis=0)))
    nfft = 1 << math.ceil(math.log2(rate*8))
    power = abs(np.fft.rfft(x[:, channel]*np.hanning(len(x)), n=nfft))**2
    freq = np.fft.rfftfreq(nfft, 1/rate)
    candidates = np.flatnonzero((freq >= expected*.97) & (freq <= expected*1.03))
    index = candidates[np.argmax(power[candidates])]
    v = np.log(np.maximum(power[index-1:index+2], 1e-30))
    offset = .5*(v[0]-v[2])/max(abs(v[0]-2*v[1]+v[2]), 1e-30)
    # The denominator is normally negative; preserve its sign explicitly.
    offset = .5*(v[0]-v[2])/(v[0]-2*v[1]+v[2]) if v[0]-2*v[1]+v[2] else 0
    return float((index+np.clip(offset, -.5, .5))*rate/nfft)


def compare(reference, candidate, rate, note=None):
    energy = np.mean(reference*reference); difference = candidate-reference
    gain = np.sqrt(energy/max(np.mean(candidate*candidate), 1e-30))
    result = {'finite': bool(np.isfinite(candidate).all()),
        'null_rms_db_relative_reference': db_ratio(np.mean(difference*difference), energy),
        'level_matched_null_rms_db': db_ratio(np.mean((candidate*gain-reference)**2), energy),
        'rms_change_db': db_ratio(np.mean(candidate*candidate), energy),
        'maximum_absolute_sample_difference': float(np.max(abs(difference))),
        'candidate_level_match_gain': float(gain), 'stereo_windows': {}}
    for name, a, b in [('early', .06, .26), ('sustain', .26, .56)]:
        aa=reference[int(a*rate):int(b*rate)];bb=candidate[int(a*rate):int(b*rate)]
        sa, sb = stereo(aa), stereo(bb)
        result['stereo_windows'][name]={'baseline':sa,'candidate':sb,
            'correlation_change':sb['correlation']-sa['correlation'],
            'balance_change_db':sb['right_minus_left_db']-sa['right_minus_left_db']}
    if note is not None:
        a, b = int(.16*rate), int(.56*rate)
        expected=440*2**((note-69)/12)
        pa,pb=pitch(reference[a:b],rate,expected),pitch(candidate[a:b],rate,expected)
        result['dominant_fundamental_peak']={'baseline_hz':pa,'candidate_hz':pb,'difference_cents':float(1200*np.log2(pb/pa)),
            'limits':'Relative dominant-peak estimator on a 0.4s window; unresolved unison beating and short-window bias remain.'}
        times=np.array([.21,.31,.41,.51]); slopes=[]
        for x in (reference,candidate):
            levels=[10*np.log10(max(np.mean(x[int((t-.05)*rate):int((t+.05)*rate)]**2),1e-30)) for t in times]
            slopes.append(float(np.polyfit(times,levels,1)[0]))
        result['held_note_decay_slope_db_per_second']={'baseline':slopes[0],'candidate':slopes[1],'change':slopes[1]-slopes[0],
            'limits':'Short whole-signal energy slope, not an independently fitted modal T60.'}
        result['attack_windows']={}
        for name, start, stop in [('first5ms',.01,.015),('5to20ms',.015,.03),('20to50ms',.03,.06)]:
            aa=reference[int(start*rate):int(stop*rate)];bb=candidate[int(start*rate):int(stop*rate)]
            row={'energy_change_db':db_ratio(np.mean(bb*bb),np.mean(aa*aa))}
            fa,sa=spectrum(aa,rate);fb,sb=spectrum(bb,rate)
            row['band_power_change_db']={f'{lo}-{hi}Hz':db_ratio(sb[(fb>=lo)&(fb<hi)].sum(),sa[(fa>=lo)&(fa<hi)].sum())
                for lo,hi in [(0,1000),(1000,4000),(4000,12000),(12000,20000)]}
            result['attack_windows'][name]=row
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'out/full-precision-optimization')
    parser.add_argument('--compiler',default='g++')
    parser.add_argument('--repeats',type=int,default=2)
    parser.add_argument('--physics-template',type=Path,help='Optional reviewed replacement; default physics probe is embedded in this tool')
    parser.add_argument('--hot-kernel-only',action='store_true',help='Run the targeted third-profile screen using an existing completed baseline report')
    parser.add_argument('--broaden-hot',action='store_true',help='After a >1.15x hot-kernel screen, add bass/treble/192k and reverse-order timing pairs')
    parser.add_argument('--audit-hot-free-rates',action='store_true',help='Supplement the retained hot candidate with cheap48k/192k free-energy and prepared-coefficient checks')
    args=parser.parse_args()
    if not 1<=args.repeats<=3:parser.error('Bounded repeats 1..3')
    source_path=ROOT/'src/full_reference/grand.cpp';calibration=ROOT/'src/full_reference/calibration.h'
    if sha(source_path)!=PINNED_SOURCE:raise ValueError('Working full solver changed; review and update the explicit input pin before a new experiment')
    source=source_path.read_text();folder=args.output_dir.resolve();folder.mkdir(parents=True,exist_ok=True)
    if args.audit_hot_free_rates:
        audit_hot_free_rates(args,folder)
        return
    if args.broaden_hot:
        broaden_hot(args,folder)
        return
    if args.hot_kernel_only:
        hot_experiment(args,source,folder)
        return
    (folder/'calibration.h').write_bytes(calibration.read_bytes())
    physics_template=folder/'physics-template.cpp.in'
    physics_template.write_text(args.physics_template.read_text() if args.physics_template else PHYSICS_TEMPLATE)
    variants={'baseline':source,'state_f32':precision(source),'modal_f32':precision(source,True)}
    flags=['-O3','-DNDEBUG','-std=c++17','-ffp-contract=off']
    result={'schema_version':1,'purpose':'Bounded precision tradeoff in the complete original working model; no surrogate, mode removal or recording fitting.',
        'source_sha256':sha(source_path),'calibration_sha256':sha(calibration),'tool_sha256':sha(Path(__file__)),
        'compiler':subprocess.check_output([args.compiler,'--version'],text=True).splitlines()[0],
        'flags':flags,'platform':platform.platform(),'variants':{},'cases':{},
        'precision_profiles':{'baseline':'All original double state/coefficients/arithmetic.',
            'state_f32':'String/board q,p states float. String coefficients, oscillator intermediates, scalar reductions, board coefficients, hammer/contact and bridge solve remain double.',
            'modal_f32':'Additionally all string-bank coefficients and cached unison factors float, float free-oscillator arithmetic. Reductions explicitly use double products/accumulators; board coefficients, hammer/contact and bridge solve remain double.'},
        'limits':'Local shared-host CPU and short synthesized-note comparisons only. No new recording, native plugin, blind listening or inaudibility claim. Numerical errors are measured, not automatically classified as audible/inaudible.'}
    for label,text in variants.items():
        snapshot=folder/f'{label}.cpp';snapshot.write_text(text)
        compiled=folder/f'{label}.timed.cpp';compiled.write_text(timing(text))
        binary=folder/label
        run([args.compiler,*flags,str(compiled),'-o',binary],folder/f'{label}-compile')
        (folder/f'{label}.patch').write_text(''.join(difflib.unified_diff(source.splitlines(True),text.splitlines(True),fromfile='baseline.cpp',tofile=label+'.cpp')))
        self_call=subprocess.run([str(binary),'--self-test'],text=True,capture_output=True)
        (folder/f'{label}-original-selftest.txt').write_text(self_call.stdout+self_call.stderr)
        result['variants'][label]={'source_sha256':sha(snapshot),'compiled_source_sha256':sha(compiled),'binary_sha256':sha(binary),
            'original_strict_self_test_exit_code':self_call.returncode,
            'original_strict_self_test':json.loads(self_call.stdout),'runs':[]}
        if physics_template.exists():
            physics=folder/f'{label}-physics.cpp';physics.write_text(physics_template.read_text().replace('@SOURCE@',snapshot.name))
            pbinary=folder/f'{label}-physics'
            run([args.compiler,*flags,str(physics),'-o',pbinary],folder/f'{label}-physics-compile')
            result['variants'][label]['precision_physics']=json.loads(run([pbinary],folder/f'{label}-physics-run'))
        print('compiled',label,flush=True)
    cases={}
    for name,note,velocity in [('C2soft',36,40),('C4hard',60,93),('C6hard',84,93)]:
        event=folder/f'{name}.events';event.write_text(f'.01 on {note} {velocity}\n.65 off {note} 0\n')
        cases[name]=(event,48000,1.2,note)
    score=ROOT/'Research/GrandPianoV2/scores/01_nocturne.events'
    music=folder/'music-prefix.events';music.write_text(''.join(line+'\n' for line in score.read_text().splitlines() if line and not line.startswith('#') and float(line.split()[0])<1))
    cases['music_prefix']=(music,48000,1.,None)
    mixed=folder/'mixed.events';mixed.write_text('0 pedal 0 1\n.01 on 36 40\n.025 on 60 93\n.04 on 84 127\n.075 off 60 0\n.09 on 60 61\n.12 pedal 0 .55\n.15 off 36 0\n.18 off 84 0\n.21 pedal 0 0\n.24 on 48 80\n.28 off 60 0\n.30 off 48 0\n')
    cases['mixed192k']=(mixed,192000,.35,None)
    audio={}
    # Interleave candidates within each case. Only the music workload repeats;
    # separate setup is excluded by each process's internal CPU clock.
    for case,(events,rate,duration,note) in cases.items():
        result['cases'][case]={'events_sha256':sha(events),'sample_rate':rate,'duration_seconds':duration,'variants':{}}
        repeats=args.repeats if case=='music_prefix' else 1
        for repeat in range(repeats):
            order=list(variants) if repeat%2==0 else list(reversed(variants))
            for label in order:
                output=folder/f'{label}-{case}-{repeat}.wav'
                command=[folder/label,'--events',events,'--output',output,'--sample-rate',str(rate),'--duration',str(duration)]
                metrics=json.loads(run(command,folder/f'{label}-{case}-{repeat}'))
                assert (metrics['string_count'],metrics['string_modes'],metrics['board_modes'],metrics['nonfinite_samples'])==(230,17778,475,0)
                result['variants'][label]['runs'].append({'case':case,'repeat':repeat,**metrics})
                if repeat==0:
                    sr,x=load(output);assert sr==rate
                    audio[label,case]=x
                    result['cases'][case]['variants'][label]={'metrics':metrics,'audio_sha256':sha(output),'audio_file':str(output)}
                print('rendered',case,label,repeat,metrics['process_cpu_seconds'],flush=True)
        for label in variants:
            if label=='baseline':continue
            result['cases'][case]['variants'][label]['difference']=compare(audio['baseline',case],audio[label,case],rate,note)
    for label,row in result['variants'].items():
        runs=[x['process_cpu_seconds'] for x in row['runs'] if x['case']=='music_prefix']
        row['music_prefix_median_process_cpu_seconds']=statistics.median(runs)
        row['music_prefix_cpu_seconds_per_audio_second']=statistics.median(runs)
    for label,row in result['variants'].items():
        row['music_prefix_speedup']=result['variants']['baseline']['music_prefix_median_process_cpu_seconds']/row['music_prefix_median_process_cpu_seconds']
    segments={label:np.concatenate([piece for case in ('C2soft','C4hard','C6hard','music_prefix') for piece in (audio[label,case],np.zeros((9600,2)))]) for label in variants}
    gains={label:.08/np.sqrt(np.mean(x*x)) for label,x in segments.items()}
    common=10**(-2/20)/max(np.max(abs(x*gains[label])) for label,x in segments.items())
    result['listening_exports']={}
    for label,x in segments.items():
        path=folder/f'listening-{label}.wav';wavfile.write(path,48000,(x*gains[label]*common).astype(np.float32))
        result['listening_exports'][label]={'file':str(path),'sha256':sha(path),'whole_file_rms_gain':float(gains[label]),'shared_peak_gain':float(common),
            'order':['C2 soft note/release','C4 hard note/release','C6 hard note/release','first1s original nocturne'],'gap_seconds':.2,
            'limits':'Dry same-rate48kHz source comparison, complete-file RMS matched; sample-peak ceiling only. These are not blind listening results.'}
    result['canonical_source_unchanged']=sha(source_path)==PINNED_SOURCE
    result['physics_template_sha256']=sha(physics_template)
    destination=folder/'report.json';destination.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'report':str(destination),'speedups':{k:v['music_prefix_speedup'] for k,v in result['variants'].items()}},indent=2))


if __name__=='__main__':
    main()
