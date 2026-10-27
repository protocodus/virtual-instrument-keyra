#pragma once
#include "shadow/PreparedModel.h"
#include "ShadowMechanics.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstring>
#include <iomanip>
#include <memory>
#include <sstream>
#include <string>

namespace pitch_music {
using Forces=std::array<double,88>;
using Branches=std::array<unsigned char,88>;
enum class MemoryLaw { PitchOnly, PitchAndModalFrequency };
struct FrameResult { Stereo fast{},unity{};bool valid=true;bool coordinateMatch=true; };

// No contact solve, note/pedal event or damping update belongs to this shadow.
// The primary's branch mask is captured inside oscillators(), before freeStep.
inline bool advanceAll(pitch_shadow::Piano& p,const Forces& forces,const Branches& branches) {
  for(int index=0;index<88;++index){auto& key=p.keys[index];
    if(!std::isfinite(forces[index])||forces[index]<0||(!branches[index]&&forces[index]!=0))return false;
    if(branches[index]){
      for(int si:key.strings)p.strings[si].m.freeStep();
      for(int si:key.strings)p.strings[si].m.force(forces[index]);
      for(int si:key.strings)p.strings[si].m.finishDamping();
    }else for(int si:key.strings)p.strings[si].m.freeDampedStep();
  }
  for(auto& z:p.board){double v=z.p*z.damp,y=z.q;z.q=z.c*y+z.s*v;z.p=(z.c*v-z.s*y)*z.damp;}
  p.groupedUnisonStep();p.bridgeStep(p.dt,true);return p.faultFlags==0;
}

template<class Primary> bool mirrorDamping(pitch_shadow::Piano& shadow,const Primary& primary) {
  if(shadow.strings.size()!=primary.strings.size())return false;
  for(size_t i=0;i<shadow.strings.size();++i){auto& to=shadow.strings[i].m;const auto& from=primary.strings[i].m;
    if(to.damp.size()!=from.damp.size())return false;
    std::copy(from.damp.begin(),from.damp.end(),to.damp.begin());
  }
  return true;
}
template<class Primary> bool coordinatesMatch(const pitch_shadow::Piano& shadow,const Primary& primary) {
  if(shadow.strings.size()!=primary.strings.size()||shadow.board.size()!=primary.board.size())return false;
  for(size_t i=0;i<shadow.strings.size();++i){const auto& a=shadow.strings[i].m;const auto& b=primary.strings[i].m;
    if(a.q.size()!=b.q.size()||std::memcmp(a.q.data(),b.q.data(),a.q.size()*sizeof(float))||
       std::memcmp(a.p.data(),b.p.data(),a.p.size()*sizeof(float))||
       std::memcmp(a.damp.data(),b.damp.data(),a.damp.size()*sizeof(float)))return false;
  }
  for(size_t i=0;i<shadow.board.size();++i){const auto& a=shadow.board[i];const auto& b=primary.board[i];
    if(std::memcmp(&a.q,&b.q,sizeof(float))||std::memcmp(&a.p,&b.p,sizeof(float))||
       std::memcmp(&a.force,&b.force,sizeof(double)))return false;
  }
  return true;
}

class Companion {
  std::unique_ptr<pitch_shadow::Piano> fast_,unity_;
  std::vector<std::vector<double>> rhos_;
  std::vector<double> bodyRhos_;
  MemoryLaw law_=MemoryLaw::PitchOnly;
  double maxGamma_=0;
  std::array<double,88> gammas_{};
  double bodyRho_=0,K_=0;Stereo KLR_{};
  bool active_=false;
public:
  Stats stats{};
  uint64_t unitySteps=0,coordinateFailures=0,pressureFailures=0,inputFailures=0;
  template<class Primary> bool prepare(const Primary& source,MemoryLaw law) {
    law_=law;
    pitch_shadow::Options options;options.sampleRate=48000;
    fast_.reset(new pitch_shadow::Piano(options));unity_.reset(new pitch_shadow::Piano(options));
    if(fast_->modeCount()!=17778||fast_->strings.size()!=230||fast_->board.size()!=475||
       source.modeCount()!=17778||source.strings.size()!=230||source.board.size()!=475)return false;
    const auto bound=fullBound(*fast_);KLR_=bound.combined;K_=std::max(KLR_[0],KLR_[1]);
    const double reference=fast_->keys[48-21].f0;bodyRho_=std::exp(-100./48000);
    if(!std::isfinite(K_)||K_<=0||!std::isfinite(reference)||reference<=0)return false;
    for(int i=0;i<88;++i){
      if(fast_->keys[i].f0!=source.keys[i].f0)return false;
      gammas_[i]=100*std::max(1.,fast_->keys[i].f0/reference);
    }
    rhos_.clear();rhos_.reserve(fast_->strings.size());maxGamma_=100;
    for(const auto& st:fast_->strings){std::vector<double> field;field.reserve(st.m.size());
      for(size_t j=0;j<st.m.size();++j){const double hz=double(st.m.omega[j])/(2*pitch_shadow::pi);
        if(!std::isfinite(hz)||hz<=0)return false;
        const double gamma=law_==MemoryLaw::PitchAndModalFrequency?
          std::max(gammas_[st.note-21],100*hz/1000):gammas_[st.note-21];
        const double rho=std::exp(-gamma/48000);
        if(!std::isfinite(rho)||rho<=0||rho>bodyRho_)return false;
        maxGamma_=std::max(maxGamma_,gamma);field.push_back(rho);}
      rhos_.push_back(std::move(field));}
    bodyRhos_.clear();bodyRhos_.reserve(fast_->board.size());
    for(const auto& z:fast_->board){const double hz=z.w/(2*pitch_shadow::pi);
      if(!std::isfinite(hz)||hz<=0)return false;
      const double gamma=law_==MemoryLaw::PitchAndModalFrequency?100*std::max(1.,hz/1000):100.;
      const double rho=std::exp(-gamma/48000);
      if(!std::isfinite(rho)||rho<=0||rho>bodyRho_)return false;
      maxGamma_=std::max(maxGamma_,gamma);bodyRhos_.push_back(rho);}
    reset();return true;
  }
  void reset() noexcept {
    if(fast_)fast_->resetState();if(unity_)unity_->resetState();
    active_=false;stats={};unitySteps=coordinateFailures=pressureFailures=inputFailures=0;
  }
  template<class Primary> FrameResult step(const Primary& source,const Forces& forces,
      const Branches& branches,const Stereo& rawPrimary,uint64_t frame,bool checkpoint) {
    FrameResult out;
    if(!fast_||!unity_||!mirrorDamping(*fast_,source)||!mirrorDamping(*unity_,source)){
      ++inputFailures;out.valid=false;return out;
    }
    bool anyForce=false;
    for(size_t i=0;i<88;++i){if(!std::isfinite(forces[i])||forces[i]<0||(!branches[i]&&forces[i]!=0)){
      ++inputFailures;out.valid=false;return out;}anyForce=anyForce||forces[i]!=0;}
    // rho=1 qualification never retires or resets at events/block boundaries.
    if(!advanceAll(*unity_,forces,branches)){out.valid=false;return out;}++unitySteps;
    out.unity=full(*unity_);
    for(int ch=0;ch<2;++ch)if(std::memcmp(&out.unity[ch],&rawPrimary[ch],sizeof(double)))++pressureFailures;
    if(checkpoint){out.coordinateMatch=coordinatesMatch(*unity_,source);if(!out.coordinateMatch)++coordinateFailures;}
    if(!active_&&!anyForce){++stats.skipped;out.valid=pressureFailures==0&&coordinateFailures==0;return out;}
    const double pre=energy(*fast_),future=2*K_*std::sqrt(2*pre);
    if(!active_&&anyForce){active_=true;++stats.wakes;}
    if(!anyForce&&future<=1e-20){++stats.retirements;stats.retirementFrame=frame;
      stats.retiredEnergy=pre;stats.discardedBound=future;clearCoordinates(*fast_);active_=false;++stats.skipped;
    }else{
      const double prior=scaleField(*fast_,rhos_,bodyRhos_,stats);
      if(!advanceAll(*fast_,forces,branches)){out.valid=false;return out;}++stats.fastSteps;
      const double E=energy(*fast_);out.fast=full(*fast_);
      if(!anyForce&&prior>0)stats.maxFreeEnergyRatio=std::max(stats.maxFreeEnergyRatio,E/prior);
      if(!anyForce&&future>0)for(double y:out.fast)stats.maxZeroForcePressureOverBound=std::max(stats.maxZeroForcePressureOverBound,std::abs(y)/future);
    }
    for(double v:out.fast)if(!std::isfinite(v))++stats.nonfinite;
    out.valid=pressureFailures==0&&coordinateFailures==0&&inputFailures==0&&
      stats.maxPositiveScaleEnergy<=0&&stats.maxFreeEnergyRatio<=1&&stats.maxZeroForcePressureOverBound<=1&&
      stats.nonfinite==0&&fast_->faultFlags==0&&unity_->faultFlags==0;
    return out;
  }
  // Exact native-f64 field layout: all string modes in original order, then
  // all board modes. Captured for independent comparison to the frozen pilot.
  std::vector<double> preparedRhos() const {
    std::vector<double> out;out.reserve(17778+475);
    for(const auto& field:rhos_)out.insert(out.end(),field.begin(),field.end());
    out.insert(out.end(),bodyRhos_.begin(),bodyRhos_.end());return out;
  }
  std::string report() const {
    std::ostringstream s;s<<std::setprecision(17)<<"{\"unity_steps\":"<<unitySteps<<
      ",\"unity_raw_nonidentical_samples\":"<<pressureFailures<<",\"unity_coordinate_mismatch_checkpoints\":"<<coordinateFailures<<
      ",\"input_errors\":"<<inputFailures<<",\"fast_steps\":"<<stats.fastSteps<<",\"fast_skipped\":"<<stats.skipped<<
      ",\"wakes\":"<<stats.wakes<<",\"retirements\":"<<stats.retirements<<",\"discarded_future_pressure_bound\":"<<stats.discardedBound<<
      ",\"max_positive_scale_energy\":"<<stats.maxPositiveScaleEnergy<<",\"max_free_energy_ratio\":"<<stats.maxFreeEnergyRatio<<
      ",\"max_zero_input_pressure_over_bound\":"<<stats.maxZeroForcePressureOverBound<<",\"fast_faults\":"<<(fast_?fast_->faultFlags:0)<<
      ",\"unity_faults\":"<<(unity_?unity_->faultFlags:0)<<",\"body_gamma_min\":100,\"gamma_by_key\":[";
    for(int i=0;i<88;++i){if(i)s<<',';s<<gammas_[i];}s<<"],\"memory_law\":\""<<(law_==MemoryLaw::PitchAndModalFrequency?"pitch-and-modal-frequency":"pitch-only")<<"\",\"max_gamma\":"<<maxGamma_<<",\"K_LR\":["<<KLR_[0]<<','<<KLR_[1]<<"]}";return s.str();
  }
};
} // namespace pitch_music
