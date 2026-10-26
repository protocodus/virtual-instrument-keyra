#pragma once
// Research-only bridge to a frozen full solver; no canonical source is edited.
// An absolute quoted KEYRA_LOCAL_RESONANCE_SOLVER can select a frozen V3 source.
#ifndef KEYRA_LOCAL_RESONANCE_SOLVER
#define KEYRA_LOCAL_RESONANCE_SOLVER "../src/full_reference/grand.cpp"
#endif
#define main keyra_local_resonance_original_cli_main
#include KEYRA_LOCAL_RESONANCE_SOLVER
#undef main
#include "keyra/physics/LocalResonance.h"

namespace keyra::local_resonance_probe {
inline grand::Options options(int rate=48000) {
  grand::Options o; o.sampleRate=rate; return o;
}
inline double boardEnergy(const grand::Piano& piano) {
  double e=0; for (const auto& z:piano.board) e+=.5*z.w*z.w*(z.q*z.q+z.p*z.p); return e;
}
inline double stringEnergy(const grand::Piano& piano) {
  double e=0; for (const auto& s:piano.strings) e+=s.m.energy(); return e;
}
inline std::array<double,2> boardObservation(const grand::Piano& piano) {
  std::array<double,2> out{};
  for (const auto& z:piano.board) {
    const double a=-z.w*z.w*z.q-2*z.sigma*z.w*z.p+z.force;
    for (unsigned ch=0;ch<2;++ch) out[ch]+=a*z.mic[ch];
  }
  return out;
}
inline std::array<double,2> recomputeObservation(const grand::Piano& piano) {
  auto out=boardObservation(piano);
  if (piano.opt.calibrated&&piano_calibration::radiationEnabled)
    for (const auto& string:piano.strings) {
      const auto radiation=string.m.radiation();
      for (unsigned ch=0;ch<2;++ch) out[ch]+=radiation[ch];
    }
  return out;
}

struct ImpulseResult {
  double work=0;
  std::array<double,2> radiationCorrection{};
};

// With N speaking strings use equal w=1/sqrt(N): u=sum(w*u_s),
// G=sum(w*w*G_s). The conjugate impulse is w*J on every participating string.
// Thus deltaE=J*u+.5*G*J*J, including unequal/detuned string modal banks.
template<class Piano> class SpeakingKeyPort {
public:
  explicit SpeakingKeyPort(Piano& piano,int note):piano_(piano),note_(note) {
    if (note<21||note>108) throw std::runtime_error("Invalid local-resonance key");
    const auto& indices=piano.keys[note-21].strings;
    if (indices.empty()||indices.size()>3) throw std::runtime_error("Unsupported speaking-string choir");
    count_=unsigned(indices.size()); weight_=1/std::sqrt(double(count_));
    for (unsigned i=0;i<count_;++i) {
      indices_[i]=indices[i];
      inverseMass_+=weight_*weight_*piano.strings[indices_[i]].compliance;
    }
  }
  physics::SpeakingStringPort snapshot() const noexcept {
    double velocity=0;
    for (unsigned i=0;i<count_;++i)
      velocity+=weight_*piano_.strings[indices_[i]].m.portVelocity();
    return {velocity,inverseMass_};
  }
  ImpulseResult applyImpulse(double impulse) noexcept {
    ImpulseResult result;
    const bool radiating=piano_.opt.calibrated&&piano_calibration::radiationEnabled;
    for (unsigned i=0;i<count_;++i) {
      auto& m=piano_.strings[indices_[i]].m;
      const double individual=weight_*impulse;
      for (size_t j=0;j<m.size();++j) {
        const double old=m.p[j];
        m.p[j]+=m.portInverse[j]*individual;
        const double actualDelta=m.p[j]-old;
        const double dv=m.omega[j]*actualDelta;
        result.work+=m.omega[j]*old*dv+.5*dv*dv;
        if (radiating) {
          result.radiationCorrection[0]+=m.radPL[j]*actualDelta;
          result.radiationCorrection[1]+=m.radPR[j]*actualDelta;
        }
      }
    }
    return result;
  }
  double energy() const noexcept {
    double e=0; for (unsigned i=0;i<count_;++i) e+=piano_.strings[indices_[i]].m.energy(); return e;
  }
  unsigned stringCount() const noexcept { return count_; }
  double weight() const noexcept { return weight_; }
  int note() const noexcept { return note_; }
private:
  Piano& piano_;
  int note_=108;
  std::array<int,3> indices_{};
  unsigned count_=0;
  double weight_=0,inverseMass_=0;
};

struct Frame {
  std::array<double,2> network{},body{},strings{},auxiliaryDirect{},combined{};
  double auxiliaryEnergy=0,speakingImpulse=0,workResidual=0,balanceResidual=0;
  bool valid=true;
};

template<class Piano> Frame step(Piano& piano,SpeakingKeyPort<Piano>& key,
                                physics::LocalResonance& auxiliary,uint64_t frame) {
  Frame out;
  out.network=piano.step(frame);
  out.body=boardObservation(piano);
  const auto reaction=auxiliary.step(key.snapshot());
  out.valid=reaction.valid;
  out.speakingImpulse=reaction.speakingImpulse;
  out.balanceResidual=reaction.balanceResidual;
  if (reaction.speakingImpulse!=0) {
    const auto actual=key.applyImpulse(reaction.speakingImpulse);
    out.workResidual=actual.work-reaction.speakingWork;
    // The original step already observed its string p states. Correct only
    // their changed radiation coordinates; do not add another board transfer.
    for (unsigned ch=0;ch<2;++ch) out.network[ch]+=actual.radiationCorrection[ch];
  }
  out.auxiliaryEnergy=auxiliary.energy();
  const double direct=auxiliary.directObservation();
  for (unsigned ch=0;ch<2;++ch) {
    out.strings[ch]=out.network[ch]-out.body[ch];
    out.auxiliaryDirect[ch]=direct;
    out.combined[ch]=direct!=0?out.network[ch]+direct:out.network[ch];
    out.valid=out.valid&&std::isfinite(out.combined[ch]);
  }
  return out;
}
} // namespace keyra::local_resonance_probe
