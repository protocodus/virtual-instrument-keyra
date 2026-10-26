#!/usr/bin/env python3
"""Bounded cached-potential safeguarded-Newton experiment for full piano contact.

Preserves the discrete-gradient/Hunt-Crossley law and complete float model.
Changes only generated out/ source copies. No recording or feature is read.
"""
from __future__ import annotations
import argparse
import difflib
import hashlib
import json
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'out/full-calibration/v2/mechanics/float-solver/grand.cpp'
SOURCE_SHA='8d6abcd41d89a32b54366106c54ebb62a9b52de21dc21402a7c179c55af88e56'
CAL_SHA='45935c2fbe67e1916ba1bf6eeb22f676f04639e70f5aa1e53e3bd5196c01a529'

FAST_SOLVER=r'''
struct FastContactResult {
  double force=0,residual=0;
  unsigned newtonIterations=0,bisectionIterations=0,evaluations=0;
  bool valid=true;
};
struct ContactProbeStats {
  uint64_t calls=0,evaluations=0,newton=0,bisections=0,failures=0;
  unsigned maximumNewton=0,maximumBisections=0;
};
inline ContactProbeStats contactProbeStats;
// Same convex contact potential; cache its old-compression value once.
inline FastContactResult fastContact(double a,double free,double A,double dt,double K,double power,double loss){
  FastContactResult result;
  if(!std::isfinite(a)||!std::isfinite(free)||!std::isfinite(A)||!std::isfinite(dt)||
     !std::isfinite(K)||!std::isfinite(power)||!std::isfinite(loss)||A<0||dt<=0||K<0||power<1||power>5||loss<0){
    result.valid=false;return result;
  }
  if(K==0||(a<=0&&free<=0))return result;
  const double va=a>0?K*std::pow(a,power+1)/(power+1):0;
  const double chi=loss/dt;
  struct Evaluation {double residual,tangent,target;};
  auto evaluate=[&](double f){
    ++result.evaluations;
    const double b=free-A*f,d=b-a,h=std::max(0.0,1+chi*d);
    if(h==0||(a<=0&&b<=0))return Evaluation{f,1,0};
    double g=0,gb=0;
    if(b<=0){const double distance=a-b;g=va/distance;gb=g/distance;}
    else if(a<=0){
      const double vb=K*std::pow(b,power+1)/(power+1),prime=(power+1)*vb/b;
      g=vb/d;gb=(prime-g)/d;
    }else{
      const double t=d/a;
      if(std::abs(t)<1e-2){
        // Integral/binomial series evaluates the same DG law without subtracting
        // nearby potentials. Terms through t^6 suffice for power1..5 here.
        const double base=(power+1)*va/a;
        double coefficient=1,value=1,derivative=0,term=1;
        for(int k=1;k<=6;++k){
          coefficient*=(power-k+1)/(k+1);
          derivative+=k*coefficient*term;term*=t;value+=coefficient*term;
        }
        g=base*value;gb=base*derivative/a;
      }else{
        const double vb=K*std::pow(b,power+1)/(power+1),prime=(power+1)*vb/b;
        g=(vb-va)/d;gb=(prime-g)/d;
      }
    }
    const double target=g*h;
    return Evaluation{f-target,1+A*(h*gb+chi*g),target};
  };
  auto zero=evaluate(0);
  if(!std::isfinite(zero.target)||zero.target<0||!std::isfinite(va)){
    result.valid=false;return result;
  }
  if(zero.target==0)return result;
  if(A==0){result.force=zero.target;result.residual=0;return result;}
  // The target decreases with force, so its value at zero brackets the root.
  double low=0,high=zero.target;
  double f=zero.target/zero.tangent;
  if(!(f>low&&f<high)||!std::isfinite(f))f=.5*(low+high);
  double best=f,bestResidual=std::numeric_limits<double>::infinity();
  bool solved=false;
  auto remember=[&](double value,const Evaluation& e){
    if(std::isfinite(e.residual)&&std::abs(e.residual)<std::abs(bestResidual)){
      best=value;bestResidual=e.residual;
    }
  };
  for(unsigned i=0;i<10;++i){
    auto e=evaluate(f);++result.newtonIterations;remember(f,e);
    if(std::abs(e.residual)<=2e-14*(1+f)){solved=true;break;}
    if(e.residual>0)high=f;else low=f;
    double next=f-e.residual/e.tangent;
    if(!std::isfinite(e.tangent)||e.tangent<1||!std::isfinite(next)||!(next>low&&next<high))next=.5*(low+high);
    f=next;
  }
  if(!solved)for(unsigned i=0;i<56;++i){
    f=.5*(low+high);auto e=evaluate(f);++result.bisectionIterations;remember(f,e);
    if(std::abs(e.residual)<=2e-14*(1+f)){solved=true;break;}
    if(e.residual>0)high=f;else low=f;
  }
  result.force=best;result.residual=bestResidual;
  result.valid=std::isfinite(best)&&best>=0&&std::isfinite(bestResidual)&&
    std::abs(bestResidual)<=1e-10*(1+best);
  return result;
}
'''

MATH_TEMPLATE=r'''
// Standalone scalar experiment: no rendering, recordings, or repository edits.
#define main keyra_contact_original_main
#include "@BASELINE@"
#undef main
#include "fast-contact.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <random>
#include <string>
#include <vector>

namespace contact_math_probe {
using LD=long double;
struct Case {
  const char* kind="";
  bool outsidePhysical=false;
  int note=60,rate=48000;
  double a=0,free=0,A=0,K=0,power=2.5,loss=.12;
};

// Independent long-double discrete gradient. The positive-positive branch is
// symmetric in its endpoints and uses expm1/log1p, without subtracting nearly
// equal powers. Crossing branches use direct positive expressions.
LD dg(LD a,LD b,LD K,LD power) {
  if(K==0||(a<=0&&b<=0))return 0;
  if(a<=0) return K*powl(b,power)*b/((power+1)*(b-a));
  if(b<=0) return K*powl(a,power)*a/((power+1)*(a-b));
  const LD high=std::max(a,b),low=std::min(a,b);
  if(high==low)return K*powl(high,power);
  const LD t=(low-high)/high;
  const LD divided=t<=-1 ? 1/(power+1) :
    expm1l((power+1)*log1pl(t))/((power+1)*t);
  return K*powl(high,power)*divided;
}
LD target(const Case& c,LD force) {
  const LD a=c.a,b=LD(c.free)-LD(c.A)*force;
  const LD hc=std::max(LD(0),1+LD(c.loss)*(b-a)/LD(1.0/c.rate));
  return dg(a,b,c.K,c.power)*hc;
}
LD reference(const Case& c) {
  const LD initial=target(c,0);
  if(initial==0||c.A==0)return initial;
  LD low=0,high=initial;
  for(unsigned i=0;i<100;++i) {
    const LD middle=.5L*(low+high);
    if(middle==low||middle==high)break;
    if(middle-target(c,middle)>0)high=middle;else low=middle;
  }
  return .5L*(low+high);
}

void number(double value) {
  if(std::isfinite(value))std::cout<<value;else std::cout<<"null";
}
struct Record {
  Case c{};
  double referenceForce=0,fastForce=0,originalForce=0;
  double fastNormalizedError=0,originalNormalizedError=0,fastPureRelativeError=0;
  double fastReferenceResidual=0,fastReportedResidual=0;
  double dissipation=0,expectedDissipation=0,workLawDefect=0;
  double normalizedWorkDefect=0,normalizedNegativeDissipation=0;
  unsigned newton=0,bisection=0,evaluations=0;
  bool fastValid=false,originalFinite=false;
};
void printRecord(const Record& r) {
  std::cout<<"{\"kind\":\""<<r.c.kind<<"\",\"outside_physical_ranges\":"<<r.c.outsidePhysical
    <<",\"note\":"<<r.c.note<<",\"rate\":"<<r.c.rate<<",\"a\":";number(r.c.a);
  std::cout<<",\"free\":";number(r.c.free);
  std::cout<<",\"A\":";number(r.c.A);
  std::cout<<",\"K\":";number(r.c.K);
  std::cout<<",\"power\":";number(r.c.power);
  std::cout<<",\"loss\":";number(r.c.loss);
  std::cout<<",\"reference_force\":";number(r.referenceForce);
  std::cout<<",\"fast_force\":";number(r.fastForce);
  std::cout<<",\"original_force\":";number(r.originalForce);
  std::cout<<",\"fast_normalized_force_error\":";number(r.fastNormalizedError);
  std::cout<<",\"original_normalized_force_error\":";number(r.originalNormalizedError);
  std::cout<<",\"fast_pure_relative_force_error\":";number(r.fastPureRelativeError);
  std::cout<<",\"fast_reference_residual_normalized\":";number(r.fastReferenceResidual);
  std::cout<<",\"fast_reported_residual\":";number(r.fastReportedResidual);
  std::cout<<",\"dissipation_J\":";number(r.dissipation);
  std::cout<<",\"expected_dissipation_J\":";number(r.expectedDissipation);
  std::cout<<",\"scalar_work_law_defect_J\":";number(r.workLawDefect);
  std::cout<<",\"normalized_work_law_defect\":";number(r.normalizedWorkDefect);
  std::cout<<",\"normalized_negative_dissipation\":";number(r.normalizedNegativeDissipation);
  std::cout<<",\"newton_iterations\":"<<r.newton<<",\"bisection_iterations\":"<<r.bisection
    <<",\"evaluations\":"<<r.evaluations<<",\"fast_valid\":"<<r.fastValid
    <<",\"original_finite\":"<<r.originalFinite<<'}';
}
}

int main() {
  using namespace grand;
  using namespace contact_math_probe;
  try {
    Options options;options.sampleRate=48000;
    Piano baseline(options);
    const auto originalKeys=baseline.keys;
    std::vector<Case> cases;cases.reserve(8000);
    auto make=[&](const char* kind,int note,int rate,double a,double free,double loss,
                  bool outside=false) {
      const auto& key=originalKeys[note-21];
      const double ratio=48000.0/rate;
      return Case{kind,outside,note,rate,a,free,key.contactCompliance*ratio*ratio,
        key.K,key.power,loss};
    };
    std::mt19937_64 random(0x4b657972614347ULL);
    std::uniform_real_distribution<double> unit(0,1);
    constexpr std::array<int,4> rates{{48000,96000,192000,384000}};
    constexpr std::array<double,4> losses{{0,.12,1,10}};
    // Exactly 5000 seeded physical-key cases. Compression is within +/-2mm;
    // free motion is within +/-8m/s. Loss0/1/10 exercise allowed option extremes.
    for(unsigned i=0;i<5000;++i) {
      const int note=21+int(random()%88),rate=rates[random()%rates.size()];
      double a=(2*unit(random)-1)*.002;
      if(i%7==0)a=(2*unit(random)-1)*powl(10.0,-10+7*unit(random));
      const double velocity=(2*unit(random)-1)*8;
      const double free=a+velocity/rate;
      cases.push_back(make("physical_random",note,rate,a,free,losses[random()%losses.size()]));
    }
    // Prescribe the desired post-contact endpoint, then derive its free endpoint
    // independently in long double. The double input rounding remains present.
    auto endpoint=[&](const char* kind,int note,int rate,double a,double b,double loss,
                      bool outside=false) {
      Case c=make(kind,note,rate,a,b,loss,outside);
      const LD hc=std::max(LD(0),1+LD(loss)*(LD(b)-LD(a))/LD(1.0/rate));
      const LD force=dg(a,b,c.K,c.power)*hc;
      c.free=double(LD(b)+LD(c.A)*force);
      cases.push_back(c);
    };
    const std::array<double,15> factors{{-1000,-10,-2,-1.01,-1,-.99,-.1,0,.1,.99,1,1.01,2,10,1000}};
    for(int note:{21,60,108})for(int rate:{48000,192000,384000})
      for(double a:{1e-8,1e-6,1e-4,.001})for(double loss:{0.,.12}) {
        const double cutoff=1e-10*std::max(1e-5,std::abs(a));
        for(double factor:factors)
          endpoint("near_equal_cutoff",note,rate,a,a+factor*cutoff,loss);
        for(double relative:{-1e-3,-1e-4,-1e-6,-1e-8,1e-8,1e-6,1e-4,1e-3})
          endpoint("near_equal_series",note,rate,a,a*(1+relative),loss);
      }
    for(int note:{21,60,108})for(int rate:rates)for(double loss:losses) {
      endpoint("loading_crossing",note,rate,-1e-6,1e-6,loss);
      endpoint("unloading_crossing",note,rate,1e-6,-1e-6,loss);
      endpoint("zero_old_endpoint",note,rate,0,1e-6,loss);
      endpoint("zero_new_endpoint",note,rate,1e-6,0,loss);
      cases.push_back(make("both_negative",note,rate,-1e-4,-2e-4,loss));
      cases.push_back(make("both_zero",note,rate,0,0,loss));
      Case noA=make("zero_compliance",note,rate,.001,.00101,loss,true);noA.A=0;cases.push_back(noA);
      Case noK=make("zero_stiffness",note,rate,.001,.00101,loss,true);noK.K=0;cases.push_back(noK);
      if(loss>0) {
        const double a=.001,clamp=a-1.0/(rate*loss);
        endpoint("hc_clamp_below",note,rate,a,std::nextafter(clamp,-INFINITY),loss,true);
        endpoint("hc_clamp_at",note,rate,a,clamp,loss,true);
        endpoint("hc_clamp_above",note,rate,a,std::nextafter(clamp,INFINITY),loss,true);
      }
    }
    // Explicitly outside the observed physical-key K/p/A ranges, while retaining
    // finite nonnegative parameters and a well-defined mathematical root.
    for(double power:{1.,2.,5.})for(double K:{1e6,1e12,1e18})
      for(double A:{0.,1e-12,1e-6})for(double loss:{0.,.12,10.}) {
        Case c=make("outside_physical_stress",60,48000,.001,.0011,loss,true);
        c.power=power;c.K=K;c.A=A;cases.push_back(c);
      }

    double maxFastError=0,maxOriginalError=0,maxPureError=0,maxResidual=0;
    double maxNegativeDissipation=0,maxWorkDefect=0,maxConservativeWorkDefect=0;
    double maxPhysicalFastError=0,maxPhysicalOriginalError=0,maxPhysicalResidual=0;
    double maxPhysicalNegativeDissipation=0,maxPhysicalWorkDefect=0;
    double maxNormalizedWorkDefect=0,maxNormalizedNegativeDissipation=0;
    double sumNewton=0,sumBisection=0,sumEvaluations=0;
    unsigned maxNewton=0,maxBisection=0,maxEvaluations=0;
    size_t invalidFast=0,originalExceptions=0,failedFast=0,outside=0,failedOutside=0,failedAccuracy=0;
    size_t originalAboveTolerance=0,pureCount=0,negativeDissipationCount=0;
    size_t failedNormalizedForce=0,failedPureForce=0,failedWork=0,failedPhysicalWork=0;
    Record worstFast{},worstOriginal{},worstPure{},worstWork{};
    Record worstPhysicalFast{},worstPhysicalOriginal{},firstInvalid{},worstResidual{};
    bool finite=true,physicalFinite=true;
    for(size_t index=0;index<cases.size();++index) {
      const Case& c=cases[index];
      const LD referenceForce=reference(c);
      const double ref=double(referenceForce);
      const auto fast=fastContact(c.a,c.free,c.A,1.0/c.rate,c.K,c.power,c.loss);
      Record r;r.c=c;r.referenceForce=ref;r.fastForce=fast.force;
      r.fastReportedResidual=fast.residual;r.fastValid=fast.valid;
      r.newton=fast.newtonIterations;r.bisection=fast.bisectionIterations;r.evaluations=fast.evaluations;
      baseline.dt=1.0/c.rate;baseline.opt.hammerLoss=c.loss;
      auto& key=baseline.keys[0];key.K=c.K;key.power=c.power;key.contactCompliance=c.A;
      key.hammerV=(c.free-c.a)*c.rate;
      try{r.originalForce=baseline.contact(key,c.a,c.free);r.originalFinite=std::isfinite(r.originalForce);}
      catch(...){++originalExceptions;r.originalForce=std::numeric_limits<double>::quiet_NaN();}
      r.fastNormalizedError=double(fabsl(LD(fast.force)-referenceForce)/(1+fabsl(referenceForce)));
      r.originalNormalizedError=r.originalFinite ?
        double(fabsl(LD(r.originalForce)-referenceForce)/(1+fabsl(referenceForce))) : INFINITY;
      r.fastPureRelativeError=ref>1e-3 ? double(fabsl(LD(fast.force)-referenceForce)/fabsl(referenceForce)) : 0;
      const LD residual=LD(fast.force)-target(c,fast.force);
      r.fastReferenceResidual=double(fabsl(residual)/(1+fabsl(LD(fast.force))));
      const LD b=LD(c.free)-LD(c.A)*LD(fast.force),d=b-LD(c.a);
      const LD elastic=dg(c.a,b,c.K,c.power);
      const LD hc=std::max(LD(0),1+LD(c.loss)*d/LD(1.0/c.rate));
      r.dissipation=double((LD(fast.force)-elastic)*d);
      r.expectedDissipation=double((elastic*hc-elastic)*d);
      r.workLawDefect=double(fabsl((LD(fast.force)-elastic*hc)*d));
      const LD va=c.a>0 ? LD(c.K)*powl(LD(c.a),LD(c.power)+1)/(LD(c.power)+1) : 0;
      const LD vb=b>0 ? LD(c.K)*powl(b,LD(c.power)+1)/(LD(c.power)+1) : 0;
      const LD workScale=1+fabsl(LD(fast.force)*d)+fabsl(va)+fabsl(vb);
      r.normalizedWorkDefect=double(LD(r.workLawDefect)/workScale);
      r.normalizedNegativeDissipation=double(std::max(LD(0),-LD(r.dissipation))/workScale);
      const bool caseFinite=std::isfinite(ref)&&std::isfinite(fast.force)&&std::isfinite(fast.residual)&&
        std::isfinite(r.fastNormalizedError)&&std::isfinite(r.fastReferenceResidual)&&
        std::isfinite(r.dissipation)&&std::isfinite(r.workLawDefect)&&
        std::isfinite(r.normalizedWorkDefect)&&std::isfinite(r.normalizedNegativeDissipation);
      finite=finite&&caseFinite;
      if(!c.outsidePhysical)physicalFinite=physicalFinite&&caseFinite;
      if(!fast.valid){if(invalidFast==0)firstInvalid=r;++invalidFast;}
      const bool normalizedForcePassed=caseFinite&&fast.force>=0&&r.fastNormalizedError<=1e-10;
      const bool pureForcePassed=caseFinite&&(ref<=1e-3||r.fastPureRelativeError<=1e-10);
      if(!normalizedForcePassed)++failedNormalizedForce;
      if(!pureForcePassed)++failedPureForce;
      const bool accuracyPassed=normalizedForcePassed&&pureForcePassed;
      if(!accuracyPassed)++failedAccuracy;
      const bool workPassed=caseFinite&&r.normalizedWorkDefect<=1e-10&&r.normalizedNegativeDissipation<=1e-10;
      if(!workPassed){++failedWork;if(!c.outsidePhysical)++failedPhysicalWork;}
      maxNormalizedWorkDefect=std::max(maxNormalizedWorkDefect,r.normalizedWorkDefect);
      maxNormalizedNegativeDissipation=std::max(maxNormalizedNegativeDissipation,r.normalizedNegativeDissipation);
      const bool casePassed=accuracyPassed&&workPassed&&fast.valid;
      if(!casePassed)++failedFast;
      if(c.outsidePhysical){++outside;if(!casePassed)++failedOutside;}
      else{
        if(r.fastNormalizedError>=maxPhysicalFastError){maxPhysicalFastError=r.fastNormalizedError;worstPhysicalFast=r;}
        if(r.originalNormalizedError>=maxPhysicalOriginalError){maxPhysicalOriginalError=r.originalNormalizedError;worstPhysicalOriginal=r;}
        maxPhysicalResidual=std::max(maxPhysicalResidual,r.fastReferenceResidual);
        maxPhysicalWorkDefect=std::max(maxPhysicalWorkDefect,r.workLawDefect);
        maxPhysicalNegativeDissipation=std::max(maxPhysicalNegativeDissipation,-r.dissipation);
      }
      if(r.originalNormalizedError>1e-10)++originalAboveTolerance;
      if(r.fastNormalizedError>=maxFastError||index==0){maxFastError=r.fastNormalizedError;worstFast=r;}
      if(r.originalNormalizedError>=maxOriginalError||index==0){maxOriginalError=r.originalNormalizedError;worstOriginal=r;}
      if(ref>1e-3){++pureCount;if(r.fastPureRelativeError>=maxPureError){maxPureError=r.fastPureRelativeError;worstPure=r;}}
      if(r.fastReferenceResidual>=maxResidual){maxResidual=r.fastReferenceResidual;worstResidual=r;}
      if(r.workLawDefect>=maxWorkDefect){maxWorkDefect=r.workLawDefect;worstWork=r;}
      if(c.loss==0)maxConservativeWorkDefect=std::max(maxConservativeWorkDefect,std::abs(r.dissipation));
      if(r.dissipation<0){++negativeDissipationCount;maxNegativeDissipation=std::max(maxNegativeDissipation,-r.dissipation);}
      sumNewton+=r.newton;sumBisection+=r.bisection;sumEvaluations+=r.evaluations;
      maxNewton=std::max(maxNewton,r.newton);maxBisection=std::max(maxBisection,r.bisection);maxEvaluations=std::max(maxEvaluations,r.evaluations);
    }
    double minK=INFINITY,maxK=0,minP=INFINITY,maxP=0,minA=INFINITY,maxA=0;
    for(const auto& key:originalKeys){minK=std::min(minK,key.K);maxK=std::max(maxK,key.K);minP=std::min(minP,key.power);maxP=std::max(maxP,key.power);minA=std::min(minA,key.contactCompliance);maxA=std::max(maxA,key.contactCompliance);}
    std::cout<<std::boolalpha<<std::setprecision(17);
    std::cout<<"{\"passed\":"<<(finite&&failedFast==0)<<",\"finite\":"<<finite
      <<",\"physical_passed\":"<<(physicalFinite&&failedFast==failedOutside)
      <<",\"all_case_force_accuracy_passed\":"<<(finite&&failedAccuracy==0)
      <<",\"all_case_force_accuracy_failure_count\":"<<failedAccuracy
      <<",\"normalized_force_accuracy_passed\":"<<(finite&&failedNormalizedForce==0)
      <<",\"pure_relative_force_accuracy_passed\":"<<(finite&&failedPureForce==0)
      <<",\"normalized_force_failure_count\":"<<failedNormalizedForce
      <<",\"pure_relative_force_failure_count\":"<<failedPureForce
      <<",\"scalar_work_dissipation_passed\":"<<(finite&&failedWork==0)
      <<",\"physical_scalar_work_dissipation_passed\":"<<(physicalFinite&&failedPhysicalWork==0)
      <<",\"scalar_work_dissipation_failure_count\":"<<failedWork
      <<",\"scalar_work_normalization\":\"1+abs(F*(b-a))+abs(V(a))+abs(V(b))\""
      <<",\"scalar_work_and_negative_dissipation_tolerance\":1e-10"
      <<",\"case_count\":"<<cases.size()<<",\"seeded_physical_random_cases\":5000"
      <<",\"outside_physical_ranges_count\":"<<outside<<",\"outside_physical_failed_count\":"<<failedOutside
      <<",\"failed_fast_count\":"<<failedFast<<",\"fast_invalid_count\":"<<invalidFast
      <<",\"original_exception_count\":"<<originalExceptions
      <<",\"original_above_force_tolerance_count\":"<<originalAboveTolerance
      <<",\"force_error_tolerance\":1e-10,\"force_error_definition\":\"abs(F-Fref)/(1+abs(Fref))\""
      <<",\"reference\":\"long-double stable DG +100 bisections; all scalar inputs, including double dt, promoted exactly to long double\""
      <<",\"physical_case_limits\":\"Actual48k key K/p/A; A scaled by(48000/rate)^2, not rebuilt at new rates. Random compression+/-2mm, free velocity+/-8m/s. Allowed loss0,.12,1,10. Targeted A0/K0/clamp and broad K/p/A stress are flagged outside_physical_ranges.\""
      <<",\"physical_key_ranges_48k\":{\"K_min\":"<<minK<<",\"K_max\":"<<maxK
      <<",\"power_min\":"<<minP<<",\"power_max\":"<<maxP<<",\"A_min\":"<<minA<<",\"A_max\":"<<maxA<<'}'
      <<",\"max_fast_normalized_force_error\":";number(maxFastError);
    std::cout<<",\"max_original_normalized_force_error\":";number(maxOriginalError);
    std::cout<<",\"physical_max_fast_normalized_force_error\":";number(maxPhysicalFastError);
    std::cout<<",\"physical_max_original_normalized_force_error\":";number(maxPhysicalOriginalError);
    std::cout<<",\"physical_max_fast_reference_residual_normalized\":";number(maxPhysicalResidual);
    std::cout<<",\"physical_max_scalar_work_law_defect_J\":";number(maxPhysicalWorkDefect);
    std::cout<<",\"physical_max_negative_dissipation_J\":";number(maxPhysicalNegativeDissipation);
    std::cout<<",\"max_fast_pure_relative_force_error_above1e_3N\":";number(maxPureError);
    std::cout<<",\"pure_relative_case_count\":"<<pureCount<<",\"max_fast_reference_residual_normalized\":";number(maxResidual);
    std::cout<<",\"max_scalar_work_law_defect_J\":";number(maxWorkDefect);
    std::cout<<",\"max_conservative_work_defect_J\":";number(maxConservativeWorkDefect);
    std::cout<<",\"max_normalized_scalar_work_law_defect\":";number(maxNormalizedWorkDefect);
    std::cout<<",\"max_normalized_negative_dissipation\":";number(maxNormalizedNegativeDissipation);
    std::cout<<",\"max_negative_dissipation_J\":";number(maxNegativeDissipation);
    std::cout<<",\"negative_dissipation_count_including_roundoff\":"<<negativeDissipationCount
      <<",\"iterations\":{\"mean_newton\":"<<sumNewton/cases.size()<<",\"max_newton\":"<<maxNewton
      <<",\"mean_bisection\":"<<sumBisection/cases.size()<<",\"max_bisection\":"<<maxBisection
      <<",\"mean_evaluations\":"<<sumEvaluations/cases.size()<<",\"max_evaluations\":"<<maxEvaluations<<'}'
      <<",\"worst_fast_force\":";printRecord(worstFast);
    std::cout<<",\"worst_original_force\":";printRecord(worstOriginal);
    std::cout<<",\"worst_physical_fast_force\":";printRecord(worstPhysicalFast);
    std::cout<<",\"worst_physical_original_force\":";printRecord(worstPhysicalOriginal);
    std::cout<<",\"worst_fast_reference_residual\":";printRecord(worstResidual);
    std::cout<<",\"first_invalid_fast_case\":";if(invalidFast)printRecord(firstInvalid);else std::cout<<"null";
    std::cout<<",\"worst_fast_pure_relative_force\":";printRecord(worstPure);
    std::cout<<",\"worst_work_law_defect\":";printRecord(worstWork);
    std::cout<<"}\n";
    return 0;
  }catch(const std::exception& error) {
    std::cerr<<"contact scalar probe: "<<error.what()<<'\n';
    std::cout<<"{\"passed\":false,\"exception\":true}\n";
    return 1;
  }
}
'''

RENDER_HARNESS=r'''#define main keyra_contact_original_cli
#include "@SOURCE@"
#undef main
#include <ctime>
int main(int argc,char**argv){try{
  if(argc==2&&std::string(argv[1])=="--physical-self-test")return grand::selfTest();
  if(argc!=5)throw std::runtime_error("events prefix duration rate");
  auto events=grand::readEvents(argv[1]);std::string prefix=argv[2];double duration=std::stod(argv[3]);int rate=std::stoi(argv[4]);
  grand::Options options;options.sampleRate=rate;grand::Piano piano(options);
  const size_t frames=size_t(std::llround(duration*rate)),block=64;
  std::vector<float> audio(frames*2);std::vector<double> precise(frames*2);
  double pole=std::exp(-2*grand::pi*24/rate),hp[2]{},previous[2]{};size_t event=0;bool finite=true;
  struct Window {double start,end,cpu;uint64_t calls,evaluations,newton,bisections;};std::vector<Window> windows;
  double total=0;
  for(size_t first=0;first<frames;first+=block){
    size_t last=std::min(frames,first+block);auto old=grand::contactProbeStats;auto start=std::clock();
    for(size_t frame=first;frame<last;++frame){
      while(event<events.size()&&size_t(std::llround(events[event].time*rate))<=frame){const auto& e=events[event++];if(e.kind=="on"&&e.value>0)piano.noteOn(e.note,e.value);else if(e.kind=="off"||e.kind=="on")piano.noteOff(e.note);else piano.pedalTarget=e.value;}
      auto value=piano.step(frame);
      for(int ch=0;ch<2;++ch){hp[ch]=pole*(hp[ch]+value[ch]-previous[ch]);previous[ch]=value[ch];finite=finite&&std::isfinite(hp[ch]);precise[frame*2+ch]=hp[ch];audio[frame*2+ch]=float(hp[ch]);}
    }
    double cpu=double(std::clock()-start)/CLOCKS_PER_SEC;total+=cpu;auto now=grand::contactProbeStats;
    windows.push_back({double(first)/rate,double(last)/rate,cpu,now.calls-old.calls,now.evaluations-old.evaluations,now.newton-old.newton,now.bisections-old.bisections});
  }
  grand::wav(prefix+".wav",audio,rate);std::ofstream raw(prefix+".f64",std::ios::binary);raw.write(reinterpret_cast<const char*>(precise.data()),precise.size()*sizeof(double));raw.close();
  auto stats=grand::contactProbeStats;
  std::cout<<std::setprecision(17)<<std::boolalpha<<"{\"sample_rate\":"<<rate<<",\"duration_seconds\":"<<duration<<",\"finite\":"<<finite<<",\"strings\":"<<piano.strings.size()<<",\"string_modes\":"<<piano.modeCount()<<",\"board_modes\":"<<piano.board.size()<<",\"process_cpu_seconds\":"<<total
    <<",\"contact_calls\":"<<stats.calls<<",\"contact_evaluations\":"<<stats.evaluations<<",\"newton_iterations\":"<<stats.newton<<",\"bisection_iterations\":"<<stats.bisections<<",\"maximum_newton_iterations\":"<<stats.maximumNewton<<",\"maximum_bisection_iterations\":"<<stats.maximumBisections<<",\"contact_failures\":"<<stats.failures<<",\"maximum_scaled_contact_residual\":"<<piano.maxContactResidual<<",\"final_mechanical_energy_J\":"<<piano.energy()<<",\"windows\":[";
  bool first=true;for(const auto& w:windows){if(!first)std::cout<<',';first=false;std::cout<<"{\"start_seconds\":"<<w.start<<",\"end_seconds\":"<<w.end<<",\"cpu_seconds\":"<<w.cpu<<",\"contact_calls\":"<<w.calls<<",\"evaluations\":"<<w.evaluations<<",\"newton\":"<<w.newton<<",\"bisections\":"<<w.bisections<<'}';}
  std::cout<<"]}\n";return finite&&stats.failures==0?0:2;
}catch(const std::exception& e){std::cerr<<e.what()<<'\n';return 1;}}
'''

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')
def run(command,log):
    c=subprocess.run([str(x) for x in command],text=True,capture_output=True)
    log.with_suffix('.stdout.txt').write_text(c.stdout);log.with_suffix('.stderr.txt').write_text(c.stderr)
    if c.returncode:raise RuntimeError(f'Command failed; see {log}.stderr.txt')
    return c.stdout
def replace(source,old,new):
    if source.count(old)!=1:raise ValueError('Pinned source transform mismatch: '+old[:80])
    return source.replace(old,new,1)

def transform(source,fast):
    source=replace(source,'namespace grand {','namespace grand {\n'+FAST_SOLVER)
    if fast:
        first=source.index('  double contact(Key &k,double delta0,double freeDelta){')
        last=source.index('\n  void oscillators(){',first)
        method=r'''  double contact(Key &k,double delta0,double freeDelta){
    if(delta0<=0&&freeDelta<=0)return 0;
    auto result=fastContact(delta0,freeDelta,k.contactCompliance,dt,k.K,k.power,opt.hammerLoss);
    ++contactProbeStats.calls;contactProbeStats.evaluations+=result.evaluations;
    contactProbeStats.newton+=result.newtonIterations;contactProbeStats.bisections+=result.bisectionIterations;
    contactProbeStats.maximumNewton=std::max(contactProbeStats.maximumNewton,result.newtonIterations);
    contactProbeStats.maximumBisections=std::max(contactProbeStats.maximumBisections,result.bisectionIterations);
    if(!result.valid)++contactProbeStats.failures;
    maxContactResidual=std::max(maxContactResidual,std::abs(result.residual)/(1+result.force));++forceSolves;
    return result.force;
  }'''
        return source[:first]+method+source[last:]
    source=replace(source,'for(int j=0;j<32&&residual(hi)<0;++j)hi*=2;',
                   'for(int j=0;j<32&&residual(hi)<0;++j){hi*=2;++contactProbeStats.evaluations;}')
    source=replace(source,'double f=.5*(lo+hi);maxContactResidual=',
                   'contactProbeStats.evaluations+=45;contactProbeStats.bisections+=42;++contactProbeStats.calls;contactProbeStats.maximumBisections=42;\n    double f=.5*(lo+hi);maxContactResidual=')
    return source

def difference(folder,case,repeat):
    a=np.fromfile(folder/f'baseline-{case}-{repeat}.f64',dtype=np.float64).reshape(-1,2)
    b=np.fromfile(folder/f'newton-{case}-{repeat}.f64',dtype=np.float64).reshape(-1,2)
    d=b-a;power=float(np.mean(a*a));error=float(np.mean(d*d))
    return {'maximum_absolute_pressure_difference':float(np.max(abs(d))),
        'null_rms_db_relative_baseline':None if error==0 else float(10*np.log10(error/max(power,1e-300))),
        'precise_samples_identical':bool(np.array_equal(a,b)),
        'rms_change_db':float(10*np.log10(max(np.mean(b*b),1e-300)/max(power,1e-300)))}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',type=Path,default=ROOT/'out/full-contact-optimization')
    p.add_argument('--compiler',default='g++');p.add_argument('--render',action='store_true',help='After isolated checks pass and heavy batches finish, run bounded music/dense timing')
    p.add_argument('--math-template',type=Path,help='Optional reviewed replacement; the default independent scalar harness is embedded')
    args=p.parse_args();folder=args.output_dir.resolve();folder.mkdir(parents=True,exist_ok=True)
    if (ROOT/'out').resolve() not in folder.parents:p.error('Study outputs must stay under this repository out/ directory')
    assert sha(SOURCE)==SOURCE_SHA and sha(SOURCE.parent/'calibration.h')==CAL_SHA
    flags=['-O3','-DNDEBUG','-std=c++17','-ffp-contract=off']
    if not args.render:
        shutil.copyfile(SOURCE,folder/'original.cpp');shutil.copyfile(SOURCE.parent/'calibration.h',folder/'calibration.h')
        (folder/'math-tool-input.py').write_bytes(Path(__file__).read_bytes())
        (folder/'fast-contact.h').write_text('namespace grand {\n'+FAST_SOLVER+'\n}\n')
        for label,fast in [('baseline',False),('newton',True)]:
            text=transform(SOURCE.read_text(),fast);path=folder/f'{label}.cpp';path.write_text(text)
            (folder/f'{label}.patch').write_text(''.join(difflib.unified_diff(SOURCE.read_text().splitlines(True),text.splitlines(True),fromfile='pinned/original.cpp',tofile=label+'.cpp')))
        template=args.math_template.read_text() if args.math_template else MATH_TEMPLATE;(folder/'math-template.cpp.in').write_text(template)
        math_source=folder/'math.cpp';math_source.write_text(template.replace('@BASELINE@','original.cpp'))
        binary=folder/'math';run([args.compiler,*flags,math_source,'-o',binary],folder/'math-compile')
        result=json.loads(run([binary],folder/'math-run'))
        report={'schema_version':1,'source_sha256':SOURCE_SHA,'calibration_sha256':CAL_SHA,'tool_sha256':sha(Path(__file__)),
            'compiler':subprocess.check_output([args.compiler,'--version'],text=True).splitlines()[0],'flags':flags,'platform':platform.platform(),
            'isolated_math':result,'fast_helper_sha256':sha(folder/'fast-contact.h'),'math_template_sha256':sha(folder/'math-template.cpp.in'),
            'math_binary_sha256':sha(binary),'source_profiles':{label:sha(folder/f'{label}.cpp') for label in ('baseline','newton')},
            'limits':'Same contact potential/discrete-gradient/Hunt-Crossley law. Near-equal algebra is evaluated with a stable series, not a promise of original42-step quotient bit equivalence. No recording or evaluation feature read. Full-model timing is a later separately authorized stage.'}
        save(folder/'math-report.json',report);print(json.dumps({'report':str(folder/'math-report.json'),'isolated_math':result},indent=2))
        return
    report=json.loads((folder/'math-report.json').read_text())
    scalar=report['isolated_math']
    physical_work_ok=(scalar['physical_max_scalar_work_law_defect_J']<=5e-12 and scalar['physical_max_negative_dissipation_J']<=5e-12)
    if not(scalar['finite'] and scalar['physical_passed'] and scalar['all_case_force_accuracy_passed'] and
           scalar['pure_relative_force_accuracy_passed'] and scalar['scalar_work_dissipation_passed'] and physical_work_ok):
        raise ValueError('Isolated physical force/work checks did not pass; no full-model rendering allowed')
    assert sha(folder/'fast-contact.h')==report['fast_helper_sha256']
    (folder/'render-tool-input.py').write_bytes(Path(__file__).read_bytes())
    physics={}
    for label in ('baseline','newton'):
        assert sha(folder/f'{label}.cpp')==report['source_profiles'][label]
        harness=folder/f'{label}-render.cpp';harness.write_text(RENDER_HARNESS.replace('@SOURCE@',label+'.cpp'))
        run([args.compiler,*flags,harness,'-o',folder/label],folder/f'{label}-render-compile')
        call=subprocess.run([str(folder/label),'--physical-self-test'],text=True,capture_output=True)
        (folder/f'{label}-physical-selftest.stdout.txt').write_text(call.stdout)
        (folder/f'{label}-physical-selftest.stderr.txt').write_text(call.stderr)
        raw=json.loads(call.stdout)
        tolerant=(raw['conservative_contact_relative_energy_error']<=5e-5 and
            raw['bridge_max_relative_energy_increase']<=5e-7 and raw['bridge_energy_remaining_ratio']<=1+5e-6 and
            raw['contact_max_relative_residual']<=1e-8)
        physics[label]={'original_strict_exit_code':call.returncode,'original_strict_result':raw,
            'experimental_float_tolerance_passed':tolerant,
            'declared_tolerances':{'contact_relative_energy':5e-5,'bridge_step_relative_energy_rise':5e-7,'bridge_final_relative_energy_rise':5e-6,'contact_residual':1e-8}}
        if not tolerant:raise ValueError('Full-model component energy checks failed: '+label)
    music=folder/'music.events';score=ROOT/'Research/GrandPianoV2/scores/01_nocturne.events'
    music.write_text(''.join(line+'\n' for line in score.read_text().splitlines() if line and not line.startswith('#') and float(line.split()[0])<1))
    dense=folder/'dense.events';dense.write_text(''.join(f'.001 on {n} 93\n' for n in range(21,109)))
    result={'schema_version':1,'math_report_sha256':sha(folder/'math-report.json'),'source_sha256':SOURCE_SHA,'calibration_sha256':CAL_SHA,
        'render_tool_sha256':sha(Path(__file__)),'flags':flags,'component_energy_checks':physics,
        'compiled_variants':{label:{'source_sha256':sha(folder/f'{label}.cpp'),'harness_sha256':sha(folder/f'{label}-render.cpp'),
            'binary_sha256':sha(folder/label)} for label in ('baseline','newton')},
        'math_gate':'Physical-range validity, all-case force accuracy and physical scalar work/negative dissipation <=5e-12J. Six deliberately unsupported extreme-stiffness failures remain visible in the linked math report.',
        'cases':{},'limits':'Two sequential reversed-order pairs per case, shared host.64-sample CPU windows include instrumentation and output storage, exclude construction/I/O. Dense88-key simultaneous strike is a stress case, not a musical polyphony guarantee.'}
    for case,events,duration in [('music',music,1.),('dense88',dense,.05)]:
        result['cases'][case]={'events_sha256':sha(events),'sample_rate':48000,'duration_seconds':duration,'variants':{k:[] for k in ('baseline','newton')}}
        for repeat in range(2):
            for label in (('baseline','newton') if repeat==0 else ('newton','baseline')):
                prefix=folder/f'{label}-{case}-{repeat}';metrics=json.loads(run([folder/label,events,prefix,duration,48000],folder/f'{label}-{case}-{repeat}-run'))
                assert metrics['finite'] and metrics['contact_failures']==0 and metrics['strings']==230 and metrics['board_modes']==475
                metrics['audio_sha256']=sha(str(prefix)+'.wav');metrics['precise_pressure_sha256']=sha(str(prefix)+'.f64')
                result['cases'][case]['variants'][label].append(metrics)
                print('rendered',case,label,repeat,metrics['process_cpu_seconds'],flush=True)
        row=result['cases'][case];summaries={}
        for label,runs in row['variants'].items():
            peak=[max(w['cpu_seconds']/(w['end_seconds']-w['start_seconds']) for w in r['windows']) for r in runs]
            summaries[label]={'median_cpu_seconds':statistics.median(r['process_cpu_seconds'] for r in runs),
                'peak64_sample_cpu_seconds_per_audio_second':peak,'contact_calls':runs[0]['contact_calls'],
                'peak_contact_active_window_cpu_seconds_per_audio_second':[
                    max((w['cpu_seconds']/(w['end_seconds']-w['start_seconds']) for w in r['windows'] if w['contact_calls']),default=0) for r in runs],
                'evaluations_per_contact':runs[0]['contact_evaluations']/max(1,runs[0]['contact_calls']),
                'maximum_newton_iterations':max(r['maximum_newton_iterations'] for r in runs),
                'maximum_bisection_iterations':max(r['maximum_bisection_iterations'] for r in runs)}
        row['summaries']=summaries;row['mean_speedup']=summaries['baseline']['median_cpu_seconds']/summaries['newton']['median_cpu_seconds']
        row['differences']=[difference(folder,case,r) for r in range(2)]
    result['pinned_inputs_unchanged']=sha(SOURCE)==SOURCE_SHA and sha(SOURCE.parent/'calibration.h')==CAL_SHA
    save(folder/'render-report.json',result);print(json.dumps({'report':str(folder/'render-report.json'),'case_summary':{k:{'speedup':v['mean_speedup'],'summaries':v['summaries'],'differences':v['differences']} for k,v in result['cases'].items()}},indent=2))

if __name__=='__main__':main()
