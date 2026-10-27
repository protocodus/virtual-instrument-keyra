#pragma once
#include <cstdint>

namespace keyra::physics {

// Dry ideal-gas approximation. Humidity, temperature gradients and acoustic
// nonlinearity are outside this reduced candidate. Geometry is authored.
struct AcousticAir {
  double temperatureC = 20;
  double pressurePa = 101325;
};

struct PlayerBodyLoad {
  double presence = 0;
  double distanceM = .6;
  // Authored modal amplitude-loss budget, not measured human absorption data.
  double maximumLossPerSecond = 3;
};

struct AcousticConfig {
  double sampleRate = 48000;
  AcousticAir air{};
  double cavityVolumeM3 = .25;
  double openingAreaClosedM2 = .003;
  double openingAreaOpenM2 = .12;
  double neckLengthM = .015;
  // Sets aperture geometry/inertance at prepare. Changing geometry clears the
  // acoustic state; it must be done outside real-time processing.
  double lidPosition = .5;
  double boardAreaM2 = .03;
  double couplingResistancePaSecondsPerM3 = 1000;
  double internalLossPerSecond = 0;
  // Positive radiation-load multiplier. This can change live, unlike geometry.
  double lidRadiation = 1;
  PlayerBodyLoad player{};
};

// A generalized mechanical port. Applying impulse J changes its velocity by
// inverseMass*J and its mechanical energy by velocity*J+.5*inverseMass*J*J.
struct AcousticMechanicalPort {
  double velocity = 0;
  double inverseMass = 0;
};

struct AcousticStep {
  double boardImpulse = 0;
  double boardWork = 0;
  double cavityEnergyBefore = 0;
  double cavityEnergyAfter = 0;
  double couplingDissipation = 0;
  double radiationDissipation = 0;
  double playerDissipation = 0;
  double internalDissipation = 0;
  double numericalDissipation = 0;
  // Δ cavity energy + board work + every dissipated term. This is a numerical
  // residual, not a claim of agreement with a real room or player.
  double balanceResidual = 0;
  double volumeVelocity = 0;
  double cavityPressure = 0;
  bool valid = false;
};

struct AcousticProperties {
  double densityKgPerM3 = 0;
  double speedOfSoundMps = 0;
  double acousticComplianceM5PerN = 0;
  double acousticInertanceKgPerM4 = 0;
  double frequencyHz = 0;
  double apertureAreaM2 = 0;
  double apertureRadiusM = 0;
  double apertureKa = 0;
  double radiationResistancePaSecondsPerM3 = 0;
  bool lowKaApproximation = false;
};

// One explicitly reduced cavity/aperture mode coupled reciprocally to one
// mechanical board port. It is not a full air field, lid plate or human body
// simulation. Energy coordinates are x=omega*sqrt(M)*Q and v=sqrt(M)*Qdot,
// giving E=.5*(x*x+v*v) joules for volume displacement Q in m^3.
class AcousticLoad {
public:
  AcousticLoad() noexcept;
  // Invalid input leaves configuration and state unchanged. All expensive
  // coefficient work occurs here/setters; step has no allocation or libm calls.
  bool prepare(const AcousticConfig&) noexcept;
  void reset() noexcept;
  bool setLidRadiation(double multiplier) noexcept;
  bool setPlayerPresence(double presence) noexcept;
  bool setPlayerDistance(double distanceM) noexcept;
  void setCouplingEnabled(bool enabled) noexcept;
  // The caller must apply result.boardImpulse once, to the same port whose
  // velocity/inverseMass were supplied. This provides the reaction force.
  AcousticStep step(AcousticMechanicalPort) noexcept;
  // External pressure impulse in Pa*s; returns externally supplied work in J.
  double applyPressureImpulse(double pressureImpulse) noexcept;
  double energy() const noexcept;
  double volumeVelocity() const noexcept;
  double cavityPressure() const noexcept;
  const AcousticProperties& properties() const noexcept { return properties_; }
  const AcousticConfig& config() const noexcept { return config_; }

private:
  void updateLosses() noexcept;
  double x_ = 0, v_ = 0;
  double dt_ = 1.0 / 48000;
  double halfCos_ = 1, halfSin_ = 0;
  double inverseSqrtMass_ = 0, inverseSqrtCompliance_ = 0;
  double internalHalf_ = 1, radiationHalf_ = 1, playerHalf_ = 1;
  bool couplingEnabled_ = true;
  AcousticConfig config_{};
  AcousticProperties properties_{};
};

} // namespace keyra::physics
