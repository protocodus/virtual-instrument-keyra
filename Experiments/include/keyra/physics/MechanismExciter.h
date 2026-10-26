#pragma once
#include <array>
#include <cmath>
#include <cstdint>

namespace keyra::physics {

// Authored, inexpensive mechanical texture sources. These are effective modal
// proxies, not measured action geometries, felt properties or recorded noises.
enum class MechanismKind : unsigned { KeyPress, Keybed, KeyRelease, Pedal };

struct MechanismConfig {
  double sampleRate = 48000;
  double modalMassKg = .024;
  double frequencyHz = 1450;
  double lossPerSecond = 300;
  double couplingResistanceKgPerSecond = 2;
  double triggerImpulseNs = .0025;
  double directObservationGain = .03;
};

inline MechanismConfig mechanismPreset(MechanismKind kind, double sampleRate = 48000) noexcept {
  MechanismConfig c;
  c.sampleRate = sampleRate;
  switch (kind) {
    case MechanismKind::KeyPress:
      c.modalMassKg=.016; c.frequencyHz=800; c.lossPerSecond=400;
      c.couplingResistanceKgPerSecond=1.2; c.triggerImpulseNs=.0015; break;
    case MechanismKind::Keybed: break;
    case MechanismKind::KeyRelease:
      c.modalMassKg=.011; c.frequencyHz=1800; c.lossPerSecond=650;
      c.couplingResistanceKgPerSecond=.9; c.triggerImpulseNs=.0007; break;
    case MechanismKind::Pedal:
      c.modalMassKg=.15; c.frequencyHz=135; c.lossPerSecond=35;
      c.couplingResistanceKgPerSecond=5; c.triggerImpulseNs=.006; break;
  }
  return c;
}

struct MechanismBodyPort {
  double velocity = 0;
  double inverseMass = 0;
};

struct MechanismStep {
  bool valid = true;
  double sourceEnergyBefore = 0, sourceEnergyAfter = 0;
  double bodyImpulse = 0, bodyWork = 0;
  double internalDissipation = 0, couplingDissipation = 0;
  double retirementDissipation = 0;
  double balanceResidual = 0;
};

struct MechanismLedger {
  double externalWork = 0, retiredEnergy = 0;
  double internalDissipation = 0, couplingDissipation = 0, bodyWork = 0;
  double maximumBalanceResidual = 0;
  uint64_t triggers = 0, frames = 0, invalidFrames = 0;
};

// A three-mode source with a reciprocal viscous body port. State is x=omega*q
// and v=qdot, with unit modal mass; port b converts to physical velocity.
// E=.5 sum(x*x+v*v), G=sum(b*b). The body receives +J, the source receives -J.
// No allocations, locks, I/O, exceptions or random floor in the render path.
class MechanismExciter {
public:
  MechanismExciter() noexcept { (void)prepare(MechanismConfig{}); }

  bool prepare(const MechanismConfig& c) noexcept {
    if (!finite(c.sampleRate) || c.sampleRate<8000 || c.sampleRate>384000 ||
        !finite(c.modalMassKg) || c.modalMassKg<1.e-5 || c.modalMassKg>10 ||
        !finite(c.frequencyHz) || c.frequencyHz<=0 || c.frequencyHz*1.81>=c.sampleRate*.45 ||
        !finite(c.lossPerSecond) || c.lossPerSecond<0 || c.lossPerSecond>100000 ||
        !finite(c.couplingResistanceKgPerSecond) || c.couplingResistanceKgPerSecond<0 || c.couplingResistanceKgPerSecond>1.e6 ||
        !finite(c.triggerImpulseNs) || c.triggerImpulseNs<0 || c.triggerImpulseNs>100 ||
        !finite(c.directObservationGain) || std::abs(c.directObservationGain)>1000) return false;
    config_=c;
    constexpr std::array<double,3> ratios{{.67,1,1.81}}, shapes{{.8,.5,.3}};
    constexpr double pi=3.14159265358979323846;
    inverseMass_=0;
    for (unsigned i=0;i<3;++i) {
      auto& m=modes_[i]; m={};
      const double angle=2*pi*c.frequencyHz*ratios[i]/c.sampleRate;
      m.c=std::cos(angle); m.s=std::sin(angle);
      m.damp=std::exp(-c.lossPerSecond/c.sampleRate);
      m.port=shapes[i]/std::sqrt(c.modalMassKg);
      inverseMass_+=m.port*m.port;
    }
    reset();
    return true;
  }

  void reset() noexcept {
    for (auto& m:modes_) m.x=m.v=0;
    ledger_={};
  }
  const MechanismConfig& config() const noexcept { return config_; }
  const MechanismLedger& ledger() const noexcept { return ledger_; }
  double energy() const noexcept {
    double e=0; for (const auto& m:modes_) e+=.5*(m.x*m.x+m.v*m.v); return e;
  }
  double velocity() const noexcept {
    double v=0; for (const auto& m:modes_) v+=m.port*m.v; return v;
  }
  double inverseMass() const noexcept { return inverseMass_; }
  bool enabled() const noexcept { return enabled_; }
  bool couplingEnabled() const noexcept { return coupling_; }
  void setCouplingEnabled(bool value) noexcept { coupling_=value; }
  void setObservationEnabled(bool value) noexcept { observation_=value; }
  void setEnabled(bool value) noexcept {
    if (enabled_ && !value) {
      ledger_.retiredEnergy+=energy();
      for (auto& m:modes_) m.x=m.v=0;
    }
    enabled_=value;
  }
  double directObservation() const noexcept {
    return enabled_ && observation_ ? config_.directObservationGain*velocity() : 0;
  }
  // Return the actual external work, which can have either sign on a restrike.
  // A zero-strength event is a no-op. Disabled modules cannot receive a trigger.
  double trigger(double strength) noexcept {
    if (!enabled_ || !finite(strength) || strength<=0) return 0;
    if (strength>1) strength=1;
    const double work=impulse(config_.triggerImpulseNs*strength);
    ledger_.externalWork+=work; ++ledger_.triggers;
    return work;
  }

  MechanismStep step(MechanismBodyPort body) noexcept {
    MechanismStep result;
    result.sourceEnergyBefore=result.sourceEnergyAfter=energy();
    if (!enabled_) return result;
    if (!finite(body.velocity) || std::abs(body.velocity)>1.e6 ||
        !finite(body.inverseMass) || body.inverseMass<0 || body.inverseMass>1.e12) {
      result.valid=false; ++ledger_.invalidFrames; return result;
    }
    for (auto& m:modes_) {
      const double before=m.v;
      const double damped=before*m.damp;
      result.internalDissipation+=.5*(before*before-damped*damped);
      const double x=m.x, v=m.v=damped;
      m.x=m.c*x+m.s*v;
      const double rotated=m.c*v-m.s*x;
      m.v=rotated*m.damp;
      result.internalDissipation+=.5*(rotated*rotated-m.v*m.v);
    }
    if (coupling_ && config_.couplingResistanceKgPerSecond>0) {
      const double relative=velocity()-body.velocity;
      const double hR=config_.couplingResistanceKgPerSecond/config_.sampleRate;
      const double totalInverseMass=inverseMass_+body.inverseMass;
      result.bodyImpulse=hR*relative/(1+.5*hR*totalInverseMass);
      (void)impulse(-result.bodyImpulse);
      const double midpointRelative=relative-.5*totalInverseMass*result.bodyImpulse;
      result.couplingDissipation=hR*midpointRelative*midpointRelative;
      result.bodyWork=result.bodyImpulse*body.velocity+
        .5*body.inverseMass*result.bodyImpulse*result.bodyImpulse;
    }
    // Explicitly retire energies far below any audio representation instead of
    // allowing decayed source states to enter costly subnormal arithmetic.
    for (auto& m:modes_) if (std::abs(m.x)<1.e-24 && std::abs(m.v)<1.e-24) {
      result.retirementDissipation+=.5*(m.x*m.x+m.v*m.v); m.x=m.v=0;
    }
    result.sourceEnergyAfter=energy();
    result.balanceResidual=result.sourceEnergyAfter-result.sourceEnergyBefore+
      result.bodyWork+result.internalDissipation+result.couplingDissipation+result.retirementDissipation;
    ledger_.internalDissipation+=result.internalDissipation;
    ledger_.couplingDissipation+=result.couplingDissipation;
    ledger_.bodyWork+=result.bodyWork;
    ledger_.retiredEnergy+=result.retirementDissipation;
    if (std::abs(result.balanceResidual)>ledger_.maximumBalanceResidual)
      ledger_.maximumBalanceResidual=std::abs(result.balanceResidual);
    ++ledger_.frames;
    return result;
  }

private:
  struct Mode { double x=0,v=0,c=1,s=0,damp=1,port=0; };
  MechanismConfig config_{};
  std::array<Mode,3> modes_{};
  MechanismLedger ledger_{};
  double inverseMass_=0;
  bool enabled_=true,coupling_=true,observation_=true;
  static bool finite(double value) noexcept { return std::isfinite(value); }
  double impulse(double value) noexcept {
    double work=0;
    for (auto& m:modes_) {
      const double d=m.port*value;
      work+=m.v*d+.5*d*d; m.v+=d;
    }
    return work;
  }
};

} // namespace keyra::physics
