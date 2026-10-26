#pragma once
#include <cmath>
#include <cstdint>

namespace keyra::physics {

// One effective key-local mode. Its physical identity is intentionally open:
// these numbers are not a measured duplex geometry, wire mass or material.
struct LocalResonanceConfig {
  double sampleRate = 48000;
  double frequencyHz = 4433.86;
  // A 50 dB/s free amplitude-loss prior gives sigma=50*ln(10)/20.
  double lossPerSecond = 5.756462732485114;
  double couplingResistance = .5;
  // Optional separate direct radiation proxy; it never enters the mechanics.
  double directObservationGain = 1;
};

struct SpeakingStringPort {
  double velocity = 0;
  double inverseMass = 0;
};

struct LocalResonanceStep {
  bool valid = true;
  double energyBefore = 0, energyAfter = 0;
  // Apply once to the same power-conjugate speaking-string port supplied.
  double speakingImpulse = 0, speakingWork = 0;
  double internalDissipation = 0, couplingDissipation = 0;
  double retirementDissipation = 0, balanceResidual = 0;
};

struct LocalResonanceLedger {
  double internalDissipation = 0, couplingDissipation = 0;
  double speakingWork = 0, retiredEnergy = 0;
  double maximumBalanceResidual = 0;
  uint64_t frames = 0, invalidFrames = 0;
};

// Unit-mass energy coordinates x=omega*q, v=qdot; E=.5*(x*x+v*v).
// There is no independent MIDI/impulse exciter. All energy enters from the
// speaking-string port. State persists across key retriggers and releases.
class LocalResonance {
public:
  LocalResonance() noexcept { (void)prepare(LocalResonanceConfig{}); }
  bool prepare(const LocalResonanceConfig& c) noexcept {
    if (!finite(c.sampleRate) || c.sampleRate<8000 || c.sampleRate>384000 ||
        !finite(c.frequencyHz) || c.frequencyHz<=0 || c.frequencyHz>=c.sampleRate*.45 ||
        !finite(c.lossPerSecond) || c.lossPerSecond<0 || c.lossPerSecond>1.e5 ||
        !finite(c.couplingResistance) || c.couplingResistance<0 || c.couplingResistance>1.e6 ||
        !finite(c.directObservationGain) || std::abs(c.directObservationGain)>1.e6) return false;
    config_=c;
    constexpr double pi=3.14159265358979323846;
    const double angle=2*pi*c.frequencyHz/c.sampleRate;
    cosine_=std::cos(angle); sine_=std::sin(angle);
    damping_=std::exp(-c.lossPerSecond/c.sampleRate);
    reset(); return true;
  }
  void reset() noexcept { x_=v_=0; ledger_={}; }
  const LocalResonanceConfig& config() const noexcept { return config_; }
  const LocalResonanceLedger& ledger() const noexcept { return ledger_; }
  double energy() const noexcept { return .5*(x_*x_+v_*v_); }
  double displacementCoordinate() const noexcept { return x_; }
  double velocity() const noexcept { return v_; }
  double directObservation() const noexcept {
    return enabled_&&observation_?config_.directObservationGain*v_:0;
  }
  bool enabled() const noexcept { return enabled_; }
  void setObservationEnabled(bool enabled) noexcept { observation_=enabled; }
  void setCouplingEnabled(bool enabled) noexcept { coupling_=enabled; }
  void setEnabled(bool enabled) noexcept {
    if (enabled_&&!enabled) { ledger_.retiredEnergy+=energy(); x_=v_=0; }
    enabled_=enabled;
  }

  LocalResonanceStep step(SpeakingStringPort speaking) noexcept {
    LocalResonanceStep result;
    result.energyBefore=result.energyAfter=energy();
    if (!enabled_) return result;
    if (!finite(speaking.velocity)||std::abs(speaking.velocity)>1.e6 ||
        !finite(speaking.inverseMass)||speaking.inverseMass<0||speaking.inverseMass>1.e12) {
      result.valid=false; ++ledger_.invalidFrames; return result;
    }
    const double before=v_,damped=before*damping_;
    result.internalDissipation=.5*(before*before-damped*damped);
    const double oldX=x_,rotated=cosine_*damped-sine_*oldX;
    x_=cosine_*oldX+sine_*damped; v_=rotated*damping_;
    result.internalDissipation+=.5*(rotated*rotated-v_*v_);
    if (coupling_&&config_.couplingResistance>0) {
      const double hR=config_.couplingResistance/config_.sampleRate;
      const double relative=speaking.velocity-v_;
      const double denominator=1+.5*hR*(speaking.inverseMass+1);
      const double toAuxiliary=hR*relative/denominator;
      v_+=toAuxiliary;
      result.speakingImpulse=-toAuxiliary;
      result.speakingWork=result.speakingImpulse*speaking.velocity+
        .5*speaking.inverseMass*result.speakingImpulse*result.speakingImpulse;
      const double midpointRelative=relative/denominator;
      result.couplingDissipation=hR*midpointRelative*midpointRelative;
    }
    if (std::abs(x_)<1.e-24&&std::abs(v_)<1.e-24) {
      result.retirementDissipation=energy(); x_=v_=0;
    }
    result.energyAfter=energy();
    result.balanceResidual=result.energyAfter-result.energyBefore+result.speakingWork+
      result.internalDissipation+result.couplingDissipation+result.retirementDissipation;
    ledger_.internalDissipation+=result.internalDissipation;
    ledger_.couplingDissipation+=result.couplingDissipation;
    ledger_.speakingWork+=result.speakingWork;
    ledger_.retiredEnergy+=result.retirementDissipation;
    if (std::abs(result.balanceResidual)>ledger_.maximumBalanceResidual)
      ledger_.maximumBalanceResidual=std::abs(result.balanceResidual);
    ++ledger_.frames;
    return result;
  }

private:
  LocalResonanceConfig config_{};
  LocalResonanceLedger ledger_{};
  double x_=0,v_=0,cosine_=1,sine_=0,damping_=1;
  bool enabled_=true,coupling_=true,observation_=true;
  static bool finite(double value) noexcept { return std::isfinite(value); }
};

} // namespace keyra::physics
