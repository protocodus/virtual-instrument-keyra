#pragma once
// Research adapter only: the preserved full solver and calibration remain
// untouched. The action/mechanism adapter is the same one used by its probes.
#include "strike_repetition_support.h"
#include "keyra/physics/Acoustics.h"

namespace keyra::full_acoustic_probe {
constexpr unsigned maximumLoads=2;

struct Config {
  int sampleRate=48000;
  uint32_t seed=0x4b657972u;
  double variation=.65;
  bool mechanismsEnabled=true,airEnabled=true,airCoupling=true;
  unsigned loadCount=1,boardGroup=0;
  std::array<physics::AcousticConfig,maximumLoads> acoustic{};
  // Authored diagnostic scales, not a physical pressure/microphone calibration.
  double originalPressureGain=1,mechanicalImpulseLevel=1,directAirGain=0;
};

struct JunctionFrame {
  std::array<physics::AcousticStep,maximumLoads> loads{};
  std::array<physics::AcousticMechanicalPort,maximumLoads> ports{};
  std::array<double,maximumLoads> actualBoardWork{};
  std::array<double,3> addedForce{};
  std::array<double,2> pressureProxyCorrection{};
  double maximumReactionResidual=0,maximumBalanceResidual=0;
  double cavityPressurePa=0;
  unsigned appliedImpulses=0;
  bool valid=true;
};

// Compose after the complete original string/board/mechanism step. Every load
// reads the port AFTER the previous load's impulse. Reusing stale velocity
// would break both work accounting and passivity with two loads.
inline JunctionFrame couple(grand::Piano& model,
    std::array<physics::AcousticLoad,maximumLoads>& acoustic,unsigned count,unsigned group) noexcept {
  JunctionFrame out;
  if (count>maximumLoads||group>=3) { out.valid=false; return out; }
  const auto before=mechanism_probe::boardObservation(model);
  for (unsigned i=0;i<count;++i) {
    const auto port=mechanism_probe::bodyPort(model,group);
    out.ports[i]={port.velocity,port.inverseMass};
    auto& result=out.loads[i]=acoustic[i].step(out.ports[i]);
    out.valid=out.valid&&result.valid;
    out.maximumBalanceResidual=std::max(out.maximumBalanceResidual,std::abs(result.balanceResidual));
    if (result.boardImpulse!=0) {
      const double actual=out.actualBoardWork[i]=mechanism_probe::bodyImpulse(model,group,result.boardImpulse);
      out.maximumReactionResidual=std::max(out.maximumReactionResidual,std::abs(actual-result.boardWork));
      // J/dt is a frame-average EXTERNAL force, added once to observation.
      // The original bridge's z.force is never overwritten or applied again.
      out.addedForce[group]+=result.boardImpulse/model.dt;
      ++out.appliedImpulses;
    }
    out.cavityPressurePa+=result.cavityPressure;
  }
  if (out.appliedImpulses) {
    const auto after=mechanism_probe::boardObservation(model,out.addedForce);
    for (unsigned ch=0;ch<2;++ch) out.pressureProxyCorrection[ch]=after[ch]-before[ch];
  }
  return out;
}

struct Frame {
  std::array<double,2> combined{},originalAndMechanisms{},mechanismDirect{},
    acousticReaction{},directAir{};
  JunctionFrame junction{};
  bool valid=true;
};

class Piano {
public:
  strike_probe::Piano strike;
  std::array<physics::AcousticLoad,maximumLoads> acoustic{};

  explicit Piano(const Config& config=Config{})
      :strike(checkedRate(config),config.variation,config.seed),config_(config) {
    for (unsigned i=0;i<config_.loadCount;++i) {
      auto c=config_.acoustic[i]; c.sampleRate=config_.sampleRate;
      if (!acoustic[i].prepare(c)) throw std::runtime_error("Invalid full-network acoustic configuration");
      acoustic[i].setCouplingEnabled(config_.airCoupling);
    }
    strike.enableMechanisms(config_.mechanismsEnabled);
    for (unsigned i=0;i<4;++i) {
      auto c=physics::mechanismPreset(static_cast<physics::MechanismKind>(i),config_.sampleRate);
      c.triggerImpulseNs*=config_.mechanicalImpulseLevel;
      if (!strike.mechanisms[i].prepare(c)) throw std::runtime_error("Invalid diagnostic mechanism scale");
    }
  }
  bool noteOn(int note,double velocity) { return strike.noteOn(note,velocity); }
  void noteOff(int note) noexcept { strike.noteOff(note); }
  void sustain(double value) noexcept { strike.sustain(value); }
  const Config& config() const noexcept { return config_; }
  bool setDirectAirGain(double gain) noexcept {
    if (!std::isfinite(gain)||std::abs(gain)>1.e6) return false;
    config_.directAirGain=gain; return true;
  }
  double applyPressureImpulse(unsigned load,double impulse) noexcept {
    return config_.airEnabled&&load<config_.loadCount?acoustic[load].applyPressureImpulse(impulse):0;
  }
  double acousticEnergy() const noexcept {
    double e=0; if (config_.airEnabled) for (unsigned i=0;i<config_.loadCount;++i) e+=acoustic[i].energy();
    return e;
  }
  double energy() const {
    double e=strike.model.energy()+acousticEnergy();
    for (const auto& source:strike.mechanisms) e+=source.energy();
    return e;
  }
  Frame step(uint64_t frame) {
    Frame out;
    out.originalAndMechanisms=strike.step(frame);
    for (const auto& source:strike.mechanisms) {
      const double value=source.directObservation();
      out.mechanismDirect[0]+=value; out.mechanismDirect[1]+=value;
    }
    if (config_.airEnabled) out.junction=couple(strike.model,acoustic,config_.loadCount,config_.boardGroup);
    out.valid=out.junction.valid;
    for (unsigned ch=0;ch<2;++ch) {
      out.acousticReaction[ch]=out.junction.pressureProxyCorrection[ch];
      // Keep disabled-air baseline exact: no unnecessary subtract/add roundtrip.
      if (out.junction.appliedImpulses) out.originalAndMechanisms[ch]+=out.acousticReaction[ch];
      out.directAir[ch]=config_.directAirGain*out.junction.cavityPressurePa;
      out.combined[ch]=config_.originalPressureGain*out.originalAndMechanisms[ch];
      if (out.directAir[ch]!=0) out.combined[ch]+=out.directAir[ch];
      out.valid=out.valid&&std::isfinite(out.combined[ch]);
    }
    return out;
  }

private:
  Config config_;
  static int checkedRate(const Config& c) {
    if (c.sampleRate<44100||c.sampleRate>384000||c.loadCount>maximumLoads||c.boardGroup>=3||
        !std::isfinite(c.variation)||c.variation<0||c.variation>1||
        !std::isfinite(c.originalPressureGain)||std::abs(c.originalPressureGain)>1.e6||
        !std::isfinite(c.mechanicalImpulseLevel)||c.mechanicalImpulseLevel<0||c.mechanicalImpulseLevel>10||
        !std::isfinite(c.directAirGain)||std::abs(c.directAirGain)>1.e6)
      throw std::runtime_error("Invalid full acoustic research adapter setup");
    return c.sampleRate;
  }
};
} // namespace keyra::full_acoustic_probe
