#pragma once
// Research-only adapter. The exact full solver is included once without its CLI
// entry point, following the preserved independent physics-probe convention.
// This is not the public plugin API and never modifies the canonical source.
#define main keyra_mechanism_probe_original_cli_main
#include "../src/full_reference/grand.cpp"
#undef main
#include "keyra/physics/MechanismExciter.h"

namespace keyra::mechanism_probe {
using physics::MechanismBodyPort;
using physics::MechanismExciter;
using physics::MechanismKind;
constexpr std::array<unsigned,4> bodyGroups{{1,1,1,0}};
constexpr std::array<const char*,4> names{{"key-press","keybed","key-release","pedal"}};

inline grand::Options options(int rate=48000) {
  grand::Options o; o.sampleRate=rate; return o;
}
inline void openDampers(grand::Piano& piano) {
  piano.pedal=piano.pedalTarget=1;
  for (auto& key:piano.keys) key.damperPosition=0;
  piano.setDamping();
}
inline MechanismBodyPort bodyPort(const grand::Piano& piano,unsigned group) {
  MechanismBodyPort port;
  for (const auto& z:piano.board) {
    port.velocity+=z.port[group]*z.w*z.p;
    port.inverseMass+=z.port[group]*z.port[group];
  }
  return port;
}
inline double bodyImpulse(grand::Piano& piano,unsigned group,double impulse) {
  double work=0;
  for (auto& z:piano.board) {
    const double dv=z.port[group]*impulse;
    work+=z.w*z.p*dv+.5*dv*dv;
    z.p+=dv/z.w;
  }
  return work;
}
inline double boardEnergy(const grand::Piano& piano) {
  double e=0;
  for (const auto& z:piano.board) e+=.5*z.w*z.w*(z.q*z.q+z.p*z.p);
  return e;
}
inline double stringEnergy(const grand::Piano& piano) {
  double e=0; for (const auto& s:piano.strings) e+=s.m.energy(); return e;
}
inline std::array<double,2> boardObservation(const grand::Piano& piano,
                                          const std::array<double,3>& additionalForce={}) {
  std::array<double,2> out{};
  for (const auto& z:piano.board) {
    double force=z.force;
    for (unsigned g=0;g<3;++g) force+=z.port[g]*additionalForce[g];
    const double acc=-z.w*z.w*z.q-2*z.sigma*z.w*z.p+force;
    for (unsigned ch=0;ch<2;++ch) out[ch]+=acc*z.mic[ch];
  }
  return out;
}

struct Frame {
  std::array<double,2> network{},body{},strings{},direct{},combined{};
  std::array<double,4> individualDirect{};
  double maximumReactionWorkResidual=0,maximumSourceBalanceResidual=0;
  bool valid=true;
};

// Advance the exact original network, then couple each mechanism sequentially
// through a passive midpoint port. Board reaction affects all following frames.
// Its frame-average external force J/dt is observed exactly once, without
// overwriting the original bridge's z.force. This is a first-order composition.
inline Frame step(grand::Piano& piano,std::array<MechanismExciter,4>& sources,uint64_t frame) {
  Frame out;
  out.network=piano.step(frame);
  const auto originalBody=boardObservation(piano);
  std::array<double,3> force{};
  bool applied=false;
  for (unsigned i=0;i<4;++i) {
    auto& source=sources[i];
    const auto result=source.step(bodyPort(piano,bodyGroups[i]));
    out.valid=out.valid&&result.valid;
    out.maximumSourceBalanceResidual=std::max(out.maximumSourceBalanceResidual,std::abs(result.balanceResidual));
    if (result.bodyImpulse!=0) {
      const double actualWork=bodyImpulse(piano,bodyGroups[i],result.bodyImpulse);
      out.maximumReactionWorkResidual=std::max(out.maximumReactionWorkResidual,std::abs(actualWork-result.bodyWork));
      force[bodyGroups[i]]+=result.bodyImpulse/piano.dt;
      applied=true;
    }
    out.individualDirect[i]=source.directObservation();
    out.direct[0]+=out.individualDirect[i]; out.direct[1]+=out.individualDirect[i];
  }
  out.body=applied?boardObservation(piano,force):originalBody;
  for (unsigned ch=0;ch<2;++ch) {
    out.strings[ch]=out.network[ch]-originalBody[ch];
    // Preserve the exact original output path for a completely disabled source
    // set, rather than introducing an unnecessary subtract/add round trip.
    if (applied) out.network[ch]+=out.body[ch]-originalBody[ch];
    out.combined[ch]=out.direct[ch]!=0?out.network[ch]+out.direct[ch]:out.network[ch];
    out.valid=out.valid&&std::isfinite(out.combined[ch]);
  }
  return out;
}

inline void prepare(std::array<MechanismExciter,4>& sources,double sampleRate,
                    bool enabled=true,bool coupling=true) {
  for (unsigned i=0;i<4;++i) {
    if (!sources[i].prepare(physics::mechanismPreset(static_cast<MechanismKind>(i),sampleRate)))
      throw std::runtime_error("Invalid mechanism configuration");
    sources[i].setEnabled(enabled); sources[i].setCouplingEnabled(coupling);
  }
}
} // namespace keyra::mechanism_probe
