#pragma once
#include "PhysicalPiano.h"
#include "physics/Action.h"
#include "physics/Acoustics.h"
#include "physics/Materials.h"

namespace keyra {
// A connected research path, separate from the calibrated live preview. Every
// configuration change is setup-only and clears state. MIDI is a proxy for a
// prescribed finger trajectory; no recording of a finger is played back.
struct PhysicalInstrumentConfig {
  double sampleRate=48000;
  physics::materials::SoundboardWood soundboard=physics::materials::SoundboardWood::SitkaSpruce;
  physics::materials::KeyWoodChoice keyWood=physics::materials::KeyWoodChoice::SitkaSpruce;
  physics::ActionConfig action{};
  physics::AcousticConfig acoustic{};
  double resonance=.3;
  bool bridgeCoupling=true;
  bool acousticCoupling=true;
  // Authored fixed geometry converts sourced wood/PMMA densities into key
  // inertia. It is an experiment, not measured geometry of either recording.
  bool deriveKeyMassFromMaterials=true;
  double keyStickVolumeM3=7.e-5;
  double keyStickInertiaFactor=.55;
  double keytopVolumeM3=2.4e-6;
  double nonWoodEffectiveKeyMassKg=.030;
};
struct PhysicalInstrumentMetrics {
  double maximumContactResidual=0;
  double maximumContactEnergyResidual=0;
  double maximumAcousticBalanceResidual=0;
  double maximumAcousticReactionResidual=0;
  double contactDissipation=0;
  double acousticDissipation=0;
  uint64_t frames=0,contactFrames=0,invalidContacts=0;
};
class PhysicalInstrument {
public:
  PhysicalInstrument();
  bool prepare(const PhysicalInstrumentConfig&) noexcept;
  void reset() noexcept;
  void noteOn(int note,double velocity) noexcept;
  void noteOff(int note) noexcept;
  void sustain(double value) noexcept;
  void allSoundOff() noexcept;
  void process(float* left,float* right,uint32_t frames) noexcept;
  double energy() const noexcept;
  const PhysicalInstrumentConfig& configuration() const noexcept { return configuration_; }
  PhysicalInstrumentMetrics metrics() const noexcept { return metrics_; }
  // Explicit module access supports isolated experiments and benchmark fixtures.
  // Callers serialize access and must not interrupt an open frame protocol.
  PhysicalPiano& mechanics() noexcept { return mechanics_; }
  const PhysicalPiano& mechanics() const noexcept { return mechanics_; }
  physics::Action& action() noexcept { return action_; }
  const physics::Action& action() const noexcept { return action_; }
  physics::AcousticLoad& acoustics() noexcept { return acoustics_; }
  const physics::AcousticLoad& acoustics() const noexcept { return acoustics_; }
private:
  PhysicalPiano mechanics_;
  physics::Action action_;
  physics::AcousticLoad acoustics_;
  PhysicalInstrumentConfig configuration_{};
  PhysicalInstrumentMetrics metrics_{};
};
} // namespace keyra
