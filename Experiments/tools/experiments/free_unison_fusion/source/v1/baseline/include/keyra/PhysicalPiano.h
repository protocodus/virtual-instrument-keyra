#pragma once
#include <cstdint>
#include <cstddef>
#include <memory>
#include <array>
#include "physics/Action.h"

namespace keyra {
// Separate mechanical research candidate; not a replacement for Piano's live
// calibrated surrogate. No allocations, locks or exceptions after construction.
class PhysicalPiano {
public:
  static constexpr std::size_t keyCount=88,partialsPerKey=32,
    modeCapacityPerKey=2*partialsPerKey,boardModeCapacity=512;
  struct Metrics {double maximumPositiveBridgeEnergyChange=0,maximumBridgeBalanceResidual=0,bridgeDissipatedEnergy=0;};
  struct ContactMetrics {
    double maximumForceResidual=0,maximumEnergyResidual=0;
    double dissipatedEnergy=0,retiredHammerEnergy=0,launchedEnergy=0;
    uint64_t contactFrames=0,invalidContacts=0;
  };
  struct RadiationStems {
    std::array<double,2> primary{},secondary{},board{};
  };
  struct QuadratureStems {RadiationStems displacement{},velocity{};};
  PhysicalPiano();~PhysicalPiano();
  PhysicalPiano(const PhysicalPiano&)=delete;PhysicalPiano& operator=(const PhysicalPiano&)=delete;
  bool prepare(double sampleRate) noexcept;
  // Setup-only material change: rebuilds coefficients and clears state. It is
  // not an audio-thread automation method. 0=Sitka spruce, 1=Norway spruce.
  bool setSoundboardMaterial(int material) noexcept;
  int soundboardMaterial() const noexcept;
  double boardModeFrequency(std::size_t mode) const noexcept;
  std::size_t boardModeCount() const noexcept;
  // Setup-only exact authored board selector/ports/mics from the preserved v2
  // reference, with acceleration observation. Rebuilds and clears all state.
  void setReferenceSoundboardEnabled(bool enabled) noexcept;
  bool referenceSoundboardEnabled() const noexcept;
  void reset() noexcept;
  void noteOn(int note,double velocity) noexcept;
  void noteOff(int note) noexcept;
  void setKeyDown(int note,bool down) noexcept;
  void sustain(double position) noexcept;
  void setResonance(double normalized) noexcept;
  void setCouplingEnabled(bool enabled) noexcept;
  // Optional at-string hammer launch for an isolated physical-note audition.
  // Off by default: external Action integration must own excitation instead.
  void setNonlinearHammerEnabled(bool enabled) noexcept;
  // Setup-only contact-law change clears all state; not an automation method.
  bool setHammerContactLaw(const physics::ContactLaw&) noexcept;
  // Diagnostic loss ablation; dampers and bridge remain independently active.
  void setMechanicalLossEnabled(bool enabled) noexcept;
  // Observation-only controls are diagnostic ablations, never force changes.
  void setRadiationEnabled(bool enabled) noexcept;
  void setComplexRadiationEnabled(bool enabled) noexcept;
  void process(float* left,float* right,uint32_t frames) noexcept;
  // Frame protocol for an external mechanical action: free motion first,
  // exact constant-force contact second, finish losses/bridge/observation last.
  void beginFrame() noexcept;
  void finishFrame() noexcept;
  void observe(float& left,float& right) const noexcept;
  RadiationStems observeStems() const noexcept;
  // Positive-reference-weight x/v bases for offline observation fitting, from
  // the same complete mechanical simulation. They do not change any state.
  QuadratureStems observeQuadratureStems() const noexcept;
  void endFrame(float& left,float& right) noexcept;
  double keyPreviousDisplacement(int note) const noexcept;
  double keyDisplacement(int note) const noexcept;
  double keyVelocity(int note) const noexcept;
  double keyInverseMass(int note) const noexcept;
  double contactCompliance(int note) const noexcept;
  double keyImpulse(int note,double impulse) noexcept;
  double applyContactForce(int note,double force) noexcept;
  double boardDisplacement(unsigned port) const noexcept;
  double boardVelocity(unsigned port) const noexcept;
  double boardInverseMass(unsigned port) const noexcept;
  double boardImpulse(unsigned port,double impulse) noexcept;
  double keyEnergy(int note) const noexcept;
  double boardEnergy() const noexcept;
  // Includes active hammer kinetic energy and hammer/string contact potential.
  double hammerEnergy() const noexcept;
  ContactMetrics contactMetrics() const noexcept;
  double energy() const noexcept;
  Metrics metrics() const noexcept;
  std::size_t modeCount() const noexcept;
private:
  struct Impl;std::unique_ptr<Impl> impl_;
};
} // namespace keyra
