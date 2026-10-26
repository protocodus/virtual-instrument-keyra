#include "keyra/physics/Acoustics.h"
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <initializer_list>
#include <limits>
#include <new>

namespace {
bool trackAllocation = false;
unsigned allocationCount = 0;
void require(bool condition, const char* message) {
  if (!condition) { std::fprintf(stderr, "FAIL acoustics: %s\n", message); std::exit(1); }
}
bool near(double a, double b, double relative = 2.e-11) {
  return std::abs(a - b) <= relative * (1 + std::abs(a) + std::abs(b));
}
uint32_t seed = 0x12345678u;
double randomUnit() {
  seed ^= seed << 13; seed ^= seed >> 17; seed ^= seed << 5;
  return static_cast<double>(seed) / 4294967295.;
}
using namespace keyra::physics;
AcousticConfig lossless() {
  AcousticConfig config;
  config.lidRadiation = 0;
  config.internalLossPerSecond = 0;
  config.player.presence = 0;
  return config;
}

void airAndGeometry() {
  AcousticLoad load;
  const auto& p = load.properties();
  require(near(p.densityKgPerM3, 101325 / (287.05 * 293.15)), "dry-air density equation");
  require(near(p.speedOfSoundMps, std::sqrt(1.4 * 287.05 * 293.15)), "dry-air wave speed equation");
  require(p.speedOfSoundMps > 343 && p.speedOfSoundMps < 344, "room-temperature wave speed");
  require(p.lowKaApproximation, "default aperture leaves low-ka model domain");
  AcousticConfig config;
  double lastFrequency = 0;
  for (double opening : {0., .5, 1.}) {
    config.lidPosition = opening;
    require(load.prepare(config), "lid geometry prepare");
    require(load.properties().frequencyHz > lastFrequency, "aperture inertance does not respond to lid position");
    require(load.properties().radiationResistancePaSecondsPerM3 > 0, "nonpositive radiation resistance");
    lastFrequency = load.properties().frequencyHz;
  }
  config = AcousticConfig{}; config.air.temperatureC = 0;
  require(load.prepare(config), "cold-air prepare");
  const double coldFrequency = load.properties().frequencyHz;
  const double coldDensity = load.properties().densityKgPerM3;
  config.air.temperatureC = 40;
  require(load.prepare(config), "warm-air prepare");
  require(load.properties().frequencyHz > coldFrequency &&
          load.properties().densityKgPerM3 < coldDensity,
          "air temperature has no physical frequency/density effect");
}

void isolatedConservation() {
  AcousticLoad load;
  auto config = lossless();
  config.couplingResistancePaSecondsPerM3 = 0;
  require(load.prepare(config), "lossless prepare");
  const double work = load.applyPressureImpulse(.2);
  require(near(work, load.energy()), "pressure impulse external-work identity");
  const double initial = load.energy();
  for (unsigned i = 0; i < 480000; ++i) {
    const auto result = load.step({0, 1});
    require(result.valid && std::abs(result.balanceResidual) < 1.e-14,
            "isolated cavity energy balance");
    require(result.boardImpulse == 0, "disabled coupling reacted on board");
  }
  require(std::abs(load.energy() / initial - 1) < 1.e-9, "lossless cavity accumulated energy drift");
}

void reciprocalEnergy() {
  AcousticLoad load;
  auto config = lossless();
  for (unsigned iteration = 0; iteration < 3000; ++iteration) {
    config.sampleRate = iteration % 3 == 0 ? 8000 : iteration % 3 == 1 ? 48000 : 192000;
    config.couplingResistancePaSecondsPerM3 = std::pow(10., randomUnit() * 7);
    require(load.prepare(config), "random passive config");
    (void)load.applyPressureImpulse((randomUnit() - .5) * .02);
    const AcousticMechanicalPort port{(randomUnit() - .5) * 2, randomUnit() * 50};
    const auto result = load.step(port);
    const double scale = 1 + result.cavityEnergyBefore + std::abs(result.boardWork);
    require(result.valid, "nonfinite reciprocal load step");
    require(result.couplingDissipation >= 0, "junction created negative dissipation");
    require(std::abs(result.balanceResidual) < 2.e-12 * scale, "midpoint energy identity");
    require(result.cavityEnergyAfter + result.boardWork <= result.cavityEnergyBefore + 2.e-12 * scale,
            "combined cavity and board energy increased");
    require(near(result.boardWork, port.velocity * result.boardImpulse +
                 .5 * port.inverseMass * result.boardImpulse * result.boardImpulse),
            "mechanical reaction-work identity");
  }

  config = lossless();
  config.couplingResistancePaSecondsPerM3 = 3000;
  require(load.prepare(config), "coupled oscillator config");
  const double inverseMass = 2.3, rootInverseMass = std::sqrt(inverseMass);
  const double c = std::cos(2 * 3.14159265358979323846 * 157 / config.sampleRate / 2);
  const double s = std::sin(2 * 3.14159265358979323846 * 157 / config.sampleRate / 2);
  double x = 0, velocity = .2;
  double oldEnergy = .5 * velocity * velocity;
  bool transferred = false;
  for (unsigned i = 0; i < 48000; ++i) {
    const double old = x; x = c * x + s * velocity; velocity = c * velocity - s * old;
    const auto step = load.step({rootInverseMass * velocity, inverseMass});
    velocity += rootInverseMass * step.boardImpulse;
    const double oldAgain = x; x = c * x + s * velocity; velocity = c * velocity - s * oldAgain;
    const double now = .5 * (x * x + velocity * velocity) + load.energy();
    require(now <= oldEnergy + 1.e-13, "integrated mechanical/acoustic system is active");
    transferred = transferred || load.energy() > 1.e-10;
    oldEnergy = now;
  }
  require(transferred, "board did not excite cavity");
}

void lidAndBodyLoads() {
  AcousticConfig config = lossless();
  config.couplingResistancePaSecondsPerM3 = 0;
  AcousticLoad noLoss, lid, nearBody, farBody;
  require(noLoss.prepare(config), "dry load config");
  config.lidRadiation = 1;
  require(lid.prepare(config), "radiating load config");
  config.lidRadiation = 0; config.player.presence = 1; config.player.distanceM = .2;
  require(nearBody.prepare(config), "near body config");
  config.player.distanceM = 3;
  require(farBody.prepare(config), "far body config");
  for (AcousticLoad* load : {&noLoss, &lid, &nearBody, &farBody})
    (void)load->applyPressureImpulse(.1);
  double radiation = 0, body = 0;
  for (unsigned i = 0; i < 24000; ++i) {
    (void)noLoss.step({0, 1});
    radiation += lid.step({0, 1}).radiationDissipation;
    body += nearBody.step({0, 1}).playerDissipation;
    (void)farBody.step({0, 1});
  }
  require(radiation > 0 && lid.energy() < .9 * noLoss.energy(), "lid radiation has no energetic effect");
  require(body > 0 && nearBody.energy() < .9 * farBody.energy(), "player distance/presence has no energetic effect");
  const double old = nearBody.energy();
  require(nearBody.setLidRadiation(.5) && nearBody.setPlayerPresence(.4) && nearBody.setPlayerDistance(.8),
          "live passive load setters");
  require(nearBody.energy() == old, "load setter injected instantaneous energy");
}

void validationAndRealtime() {
  AcousticLoad load, control;
  (void)load.applyPressureImpulse(.1); (void)control.applyPressureImpulse(.1);
  const double old = load.energy();
  auto config = load.config(); config.cavityVolumeM3 = -1;
  require(!load.prepare(config) && load.energy() == old, "invalid prepare changed playing state");
  require(!load.setLidRadiation(2) && !load.setPlayerPresence(-1) &&
          !load.setPlayerDistance(std::numeric_limits<double>::quiet_NaN()), "invalid controls accepted");
  const auto bad = load.step({std::numeric_limits<double>::infinity(), 1});
  require(!bad.valid && bad.boardImpulse == 0 && load.energy() == old, "invalid port changed state");
  require(load.applyPressureImpulse(std::numeric_limits<double>::quiet_NaN()) == 0 && load.energy() == old,
          "invalid external impulse changed state");
  for (unsigned i = 0; i < 1000; ++i) {
    const auto a = load.step({.1, 2}), b = control.step({.1, 2});
    require(a.boardImpulse == b.boardImpulse && a.cavityEnergyAfter == b.cavityEnergyAfter,
            "invalid operations broke independent state parity");
  }
  for (double rate : {8000., 44100., 48000., 88200., 96000., 192000., 384000.}) {
    config = AcousticConfig{}; config.sampleRate = rate;
    require(load.prepare(config), "supported sample rate rejected");
    (void)load.applyPressureImpulse(.01);
    const unsigned before = allocationCount;
    trackAllocation = true;
    for (unsigned i = 0; i < 4096; ++i) {
      const auto step = load.step({0, 3});
      require(step.valid, "supported rate produced nonfinite output");
    }
    trackAllocation = false;
    require(allocationCount == before, "acoustic callback allocated");
  }
}
}

void* operator new(std::size_t size) {
  if (trackAllocation) ++allocationCount;
  if (void* memory = std::malloc(size ? size : 1)) return memory;
  std::abort();
}
void* operator new[](std::size_t size) { return ::operator new(size); }
void operator delete(void* memory) noexcept { std::free(memory); }
void operator delete[](void* memory) noexcept { std::free(memory); }
void operator delete(void* memory, std::size_t) noexcept { std::free(memory); }
void operator delete[](void* memory, std::size_t) noexcept { std::free(memory); }

int main() {
  airAndGeometry();
  isolatedConservation();
  reciprocalEnergy();
  lidAndBodyLoads();
  validationAndRealtime();
  std::puts("PASS acoustics: air/geometry, isolated energy, reciprocal coupling, lid/body losses, validation and allocation checks");
}
