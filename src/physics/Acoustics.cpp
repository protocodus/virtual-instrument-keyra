#include "keyra/physics/Acoustics.h"
#include <cmath>

namespace keyra::physics {
namespace {
constexpr double pi = 3.14159265358979323846;
constexpr double dryAirGasConstant = 287.05; // J/(kg K), ideal dry-air mixture
constexpr double dryAirGamma = 1.4;
bool finite(double value) noexcept {
#if defined(__GNUC__) || defined(__clang__)
  return __builtin_isfinite(value);
#else
  return std::isfinite(value);
#endif
}
bool between(double value, double lo, double hi) noexcept {
  return finite(value) && value >= lo && value <= hi;
}
double magnitude(double value) noexcept { return value < 0 ? -value : value; }
double damp(double& velocity, double multiplier) noexcept {
  const double old = velocity;
  velocity *= multiplier;
  return .5 * (old * old - velocity * velocity);
}
void rotate(double& x, double& velocity, double c, double s) noexcept {
  const double old = x;
  x = c * old + s * velocity;
  velocity = c * velocity - s * old;
}
}

AcousticLoad::AcousticLoad() noexcept { (void)prepare(config_); }

bool AcousticLoad::prepare(const AcousticConfig& candidate) noexcept {
  if (!between(candidate.sampleRate, 8000, 384000) ||
      !between(candidate.air.temperatureC, -20, 50) ||
      !between(candidate.air.pressurePa, 30000, 120000) ||
      !between(candidate.cavityVolumeM3, .001, 20) ||
      !between(candidate.openingAreaClosedM2, .00001, 2) ||
      !between(candidate.openingAreaOpenM2, candidate.openingAreaClosedM2, 2) ||
      !between(candidate.neckLengthM, .001, 2) ||
      !between(candidate.lidPosition, 0, 1) ||
      !between(candidate.boardAreaM2, .0001, 2) ||
      !between(candidate.couplingResistancePaSecondsPerM3, 0, 1.e9) ||
      !between(candidate.internalLossPerSecond, 0, 1.e5) ||
      !between(candidate.lidRadiation, 0, 1) ||
      !between(candidate.player.presence, 0, 1) ||
      !between(candidate.player.distanceM, 0, 20) ||
      !between(candidate.player.maximumLossPerSecond, 0, 1.e5)) return false;

  AcousticProperties next{};
  const double kelvin = candidate.air.temperatureC + 273.15;
  next.densityKgPerM3 = candidate.air.pressurePa / (dryAirGasConstant * kelvin);
  next.speedOfSoundMps = std::sqrt(dryAirGamma * dryAirGasConstant * kelvin);
  next.apertureAreaM2 = candidate.openingAreaClosedM2 + candidate.lidPosition *
      (candidate.openingAreaOpenM2 - candidate.openingAreaClosedM2);
  next.apertureRadiusM = std::sqrt(next.apertureAreaM2 / pi);
  // The two aperture ends use an authored 1.7*r correction. This is a common
  // ideal neck approximation, not measured piano lid/cabinet geometry.
  const double effectiveLength = candidate.neckLengthM + 1.7 * next.apertureRadiusM;
  next.acousticInertanceKgPerM4 = next.densityKgPerM3 * effectiveLength / next.apertureAreaM2;
  next.acousticComplianceM5PerN = candidate.cavityVolumeM3 /
      (next.densityKgPerM3 * next.speedOfSoundMps * next.speedOfSoundMps);
  const double omega = 1 / std::sqrt(next.acousticInertanceKgPerM4 * next.acousticComplianceM5PerN);
  next.frequencyHz = omega / (2 * pi);
  if (!finite(omega) || next.frequencyHz >= .44 * candidate.sampleRate) return false;
  next.apertureKa = omega * next.apertureRadiusM / next.speedOfSoundMps;
  next.lowKaApproximation = next.apertureKa <= .5;
  // Leading low-ka radiation resistance of a baffled circular aperture/piston
  // in volume-flow coordinates. Positive at every allowed parameter value;
  // frequency accuracy is only asserted as a low-ka approximation.
  next.radiationResistancePaSecondsPerM3 = next.densityKgPerM3 * next.speedOfSoundMps /
      next.apertureAreaM2 * .5 * next.apertureKa * next.apertureKa;

  config_ = candidate;
  properties_ = next;
  dt_ = 1 / candidate.sampleRate;
  halfCos_ = std::cos(.5 * omega * dt_);
  halfSin_ = std::sin(.5 * omega * dt_);
  inverseSqrtMass_ = 1 / std::sqrt(next.acousticInertanceKgPerM4);
  inverseSqrtCompliance_ = 1 / std::sqrt(next.acousticComplianceM5PerN);
  couplingEnabled_ = true;
  updateLosses();
  reset();
  return true;
}

void AcousticLoad::reset() noexcept { x_ = v_ = 0; }

void AcousticLoad::updateLosses() noexcept {
  internalHalf_ = std::exp(-config_.internalLossPerSecond * dt_);
  radiationHalf_ = std::exp(-.5 * properties_.radiationResistancePaSecondsPerM3 *
      config_.lidRadiation * dt_ / properties_.acousticInertanceKgPerM4);
  // The proximity law and maximum damping are deliberately authored. They
  // parameterize a positive load, not a measured human impedance or tissue law.
  const double relativeDistance = config_.player.distanceM / .5;
  const double playerLoss = config_.player.maximumLossPerSecond * config_.player.presence /
      (1 + relativeDistance * relativeDistance);
  playerHalf_ = std::exp(-playerLoss * dt_);
}

bool AcousticLoad::setLidRadiation(double multiplier) noexcept {
  if (!between(multiplier, 0, 1)) return false;
  config_.lidRadiation = multiplier;
  updateLosses();
  return true;
}
bool AcousticLoad::setPlayerPresence(double presence) noexcept {
  if (!between(presence, 0, 1)) return false;
  config_.player.presence = presence;
  updateLosses();
  return true;
}
bool AcousticLoad::setPlayerDistance(double distanceM) noexcept {
  if (!between(distanceM, 0, 20)) return false;
  config_.player.distanceM = distanceM;
  updateLosses();
  return true;
}
void AcousticLoad::setCouplingEnabled(bool enabled) noexcept { couplingEnabled_ = enabled; }

AcousticStep AcousticLoad::step(AcousticMechanicalPort port) noexcept {
  AcousticStep result{};
  result.cavityEnergyBefore = result.cavityEnergyAfter = energy();
  if (!finite(port.velocity) || !between(port.inverseMass, 0, 1.e12)) return result;

  result.internalDissipation += damp(v_, internalHalf_);
  result.radiationDissipation += damp(v_, radiationHalf_);
  result.playerDissipation += damp(v_, playerHalf_);
  rotate(x_, v_, halfCos_, halfSin_);

  if (couplingEnabled_ && config_.couplingResistancePaSecondsPerM3 > 0) {
    const double area = config_.boardAreaM2;
    const double relative = area * port.velocity - inverseSqrtMass_ * v_;
    const double gram = area * area * port.inverseMass + inverseSqrtMass_ * inverseSqrtMass_;
    const double hR = dt_ * config_.couplingResistancePaSecondsPerM3;
    const double midpointRelative = relative / (1 + .5 * hR * gram);
    const double pressureImpulse = hR * midpointRelative;
    result.boardImpulse = -area * pressureImpulse;
    v_ += inverseSqrtMass_ * pressureImpulse;
    result.couplingDissipation = hR * midpointRelative * midpointRelative;
    result.boardWork = port.velocity * result.boardImpulse +
        .5 * port.inverseMass * result.boardImpulse * result.boardImpulse;
  }

  rotate(x_, v_, halfCos_, halfSin_);
  result.playerDissipation += damp(v_, playerHalf_);
  result.radiationDissipation += damp(v_, radiationHalf_);
  result.internalDissipation += damp(v_, internalHalf_);
  if (magnitude(x_) + magnitude(v_) < 1.e-24) {
    result.numericalDissipation = energy();
    x_ = v_ = 0;
  }
  result.cavityEnergyAfter = energy();
  result.balanceResidual = result.cavityEnergyAfter - result.cavityEnergyBefore +
      result.boardWork + result.couplingDissipation + result.radiationDissipation +
      result.playerDissipation + result.internalDissipation + result.numericalDissipation;
  result.volumeVelocity = volumeVelocity();
  result.cavityPressure = cavityPressure();
  result.valid = finite(result.cavityEnergyAfter) && finite(result.boardImpulse) &&
      finite(result.balanceResidual);
  return result;
}

double AcousticLoad::applyPressureImpulse(double impulse) noexcept {
  if (!between(impulse, -1.e6, 1.e6)) return 0;
  const double old = v_;
  const double delta = impulse * inverseSqrtMass_;
  v_ += delta;
  return old * delta + .5 * delta * delta;
}
double AcousticLoad::energy() const noexcept { return .5 * (x_ * x_ + v_ * v_); }
double AcousticLoad::volumeVelocity() const noexcept { return inverseSqrtMass_ * v_; }
double AcousticLoad::cavityPressure() const noexcept { return inverseSqrtCompliance_ * x_; }

} // namespace keyra::physics
