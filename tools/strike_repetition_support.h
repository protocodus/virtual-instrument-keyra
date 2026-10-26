#pragma once
// Research-only full-model action adapter. No canonical source is modified.
#include "mechanism_network_support.h"
#include "keyra/physics/StrikeController.h"

namespace keyra::strike_probe {
struct LaunchLedger {
  double coreLaunchWork=0,retiredCoreHammerEnergy=0,replacedInactiveKinematicEnergy=0;
  double maximumInitialCompression=0;
  uint64_t launches=0,partialLaunches=0;
};

class Piano {
public:
  grand::Piano model;
  physics::StrikeController controller;
  LaunchLedger ledger{};
  std::array<physics::StrikeLaunch,88> lastLaunch{};
  std::array<physics::MechanismExciter,4> mechanisms{};
  bool mechanismsEnabled=false;

  explicit Piano(int rate=48000,double variation=.65,uint32_t seed=0x4b657972u)
    :model(checkedOptions(rate)) {
    physics::StrikeConfig config; config.sampleRate=rate; config.variation=variation; config.seed=seed;
    if (!controller.prepare(config)) throw std::runtime_error("Invalid strike setup");
    for (unsigned i=0;i<88;++i) {
      auto& key=model.keys[i];
      baseHardness_[i]=key.K;
      // Pristine strings are at zero displacement. Match the controller's
      // authored rest geometry before body motion excites unstruck strings;
      // virgin keys need no return tick and must not sit on the contact plane.
      key.hammerX=-config.restDepth;
      key.hammerV=0;
    }
    mechanism_probe::prepare(mechanisms,rate,false);
  }
  void enableMechanisms(bool value) noexcept {
    mechanismsEnabled=value; for (auto& source:mechanisms) source.setEnabled(value);
  }
  bool noteOn(int note,double velocity) {
    if (velocity==0) { noteOff(note); return false; }
    if (!controller.request(note,velocity/127.)) return false;
    auto& k=model.keys[note-21];
    // Key motion lifts the damper immediately, even if the hammer must wait.
    k.down=true; k.damperPosition=0; k.cachedContact=0; k.cachedLoss=model.opt.loss;
    for (int index:k.strings) { auto& m=model.strings[index].m;
      for (size_t i=0;i<m.size();++i) m.damp[i]=std::exp(-model.opt.loss*m.loss[i]*model.dt);
    }
    if (mechanismsEnabled) mechanisms[0].trigger(.95*std::min(velocity/127.,1.)*
      controller.state(note).pendingVelocityFactor);
    const auto launch=controller.poll(note,observation(note,true),false);
    return launch.valid?apply(note,launch):false;
  }
  void noteOff(int note) noexcept {
    if (note<21||note>108) return;
    const bool wasDown=controller.state(note).down;
    controller.release(note); model.noteOff(note);
    if (mechanismsEnabled&&wasDown) mechanisms[2].trigger(.4);
  }
  void sustain(double value) noexcept {
    if (!std::isfinite(value)) return;
    value=std::clamp(value,0.,1.);
    if (mechanismsEnabled) mechanisms[3].trigger(std::abs(value-model.pedalTarget));
    model.pedalTarget=value;
  }
  std::array<double,2> step(uint64_t frame) {
    for (int note=21;note<=108;++note) if (controller.requiresTick(note)) {
      auto& k=model.keys[note-21];
      const auto h=observation(note,k.hammerActive||controller.state(note).pending);
      const auto launch=controller.poll(note,h);
      if (launch.valid) (void)apply(note,launch);
      else if (!k.hammerActive&&controller.state(note).hasLaunched) {
        // Backchecked/returning geometry is an authored proxy outside the
        // original solver's active-hammer energy. It never drives strings.
        const auto& state=controller.state(note);
        k.hammerX=contactPlane_[note-21]-state.returnDepth;
        k.hammerV=-state.returnVelocity;
      }
      activeBefore_[note-21]=k.hammerActive;
    }
    const auto result=mechanismsEnabled?mechanism_probe::step(model,mechanisms,frame).combined:model.step(frame);
    for (int note=21;note<=108;++note) if (activeBefore_[note-21]&&!model.keys[note-21].hammerActive) {
      const auto& k=model.keys[note-21];
      const auto h=observation(note,true);
      ledger.retiredCoreHammerEnergy+=.5*k.mass*k.hammerV*k.hammerV+
        grand::Piano::potential(h.compression,k.K,k.power);
      activeBefore_[note-21]=false;
    }
    return result;
  }
  double keyEnergy(int note) const {
    if (note<21||note>108) return 0;
    double e=0; for (int index:model.keys[note-21].strings) e+=model.strings[index].m.energy(); return e;
  }

private:
  std::array<double,88> baseHardness_{},contactPlane_{};
  std::array<bool,88> activeBefore_{};
  static grand::Options checkedOptions(int rate) {
    if (rate<44100||rate>384000) throw std::runtime_error("Unsupported full strike-probe rate");
    return mechanism_probe::options(rate);
  }
  physics::HammerObservation observation(int note,bool refresh) {
    auto& k=model.keys[note-21];
    if (refresh) { double y=0; for (int index:k.strings) y+=model.strings[index].m.displacement(); contactPlane_[note-21]=y; }
    return {k.hammerActive,k.hammerX-contactPlane_[note-21],k.hammerV};
  }
  bool apply(int note,const physics::StrikeLaunch& launch) {
    auto& k=model.keys[note-21];
    if (k.hammerActive) throw std::runtime_error("Unsafe active-hammer strike");
    const double oldX=k.hammerX,oldV=k.hammerV;
    const double compression=observation(note,true).compression;
    if (controller.state(note).launches>1&&compression>-controller.config().separationMargin)
      throw std::runtime_error("Unsafe near-string strike");
    ledger.replacedInactiveKinematicEnergy+=.5*k.mass*oldV*oldV;
    k.K=baseHardness_[note-21]*launch.hardnessFactor;
    model.noteOn(note,launch.velocity*127.);
    if (launch.preserveSeparatedPosition) { k.hammerX=oldX; ++ledger.partialLaunches; }
    k.hammerV*=launch.velocityFactor*launch.recoveryVelocityFactor;
    ledger.coreLaunchWork+=.5*k.mass*k.hammerV*k.hammerV;
    lastLaunch[note-21]=launch;
    ledger.maximumInitialCompression=std::max(ledger.maximumInitialCompression,
      k.hammerX-contactPlane_[note-21]);
    ++ledger.launches;
    if (mechanismsEnabled) mechanisms[1].trigger(.95*launch.velocity*
      launch.recoveryVelocityFactor*launch.hardnessFactor);
    return true;
  }
};
} // namespace keyra::strike_probe
