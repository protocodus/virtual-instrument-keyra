#include "keyra/PhysicalInstrument.h"
#include <algorithm>
#include <cmath>

namespace keyra {
namespace {
double absolute(double x) noexcept { return x<0?-x:x; }
bool range(double x,double a,double b) noexcept { return std::isfinite(x)&&x>=a&&x<=b; }
}
PhysicalInstrument::PhysicalInstrument() { (void)prepare(PhysicalInstrumentConfig{}); }
bool PhysicalInstrument::prepare(const PhysicalInstrumentConfig& c) noexcept {
  if(!range(c.sampleRate,8000,384000)||!range(c.resonance,0,1)||
     static_cast<unsigned>(c.soundboard)>1||static_cast<unsigned>(c.keyWood)>1||
     !range(c.keyStickVolumeM3,1.e-6,.001)||!range(c.keyStickInertiaFactor,.01,1)||
     !range(c.keytopVolumeM3,0,.0001)||!range(c.nonWoodEffectiveKeyMassKg,0,.5))return false;
  auto actionConfig=c.action;
  if(c.deriveKeyMassFromMaterials) {
    actionConfig.keyMass=c.nonWoodEffectiveKeyMassKg+
      physics::materials::keyWood(c.keyWood).densityKgM3()*c.keyStickVolumeM3*c.keyStickInertiaFactor+
      physics::materials::acrylicKeyTop.densityKgM3*c.keytopVolumeM3;
  }
  // Validate every configuration before touching the running network.
  physics::Action actionCheck;
  physics::AcousticLoad acousticCheck;
  auto acousticConfig=c.acoustic;acousticConfig.sampleRate=c.sampleRate;
  if(!actionCheck.configure(actionConfig)||!acousticCheck.prepare(acousticConfig))return false;
  (void)mechanics_.prepare(c.sampleRate);
  (void)mechanics_.setSoundboardMaterial(static_cast<int>(c.soundboard));
  mechanics_.setResonance(c.resonance);mechanics_.setCouplingEnabled(c.bridgeCoupling);
  (void)action_.prepare(c.sampleRate);(void)action_.configure(actionConfig);
  (void)acoustics_.prepare(acousticConfig);acoustics_.setCouplingEnabled(c.acousticCoupling);
  configuration_=c;reset();return true;
}
void PhysicalInstrument::reset() noexcept {
  mechanics_.reset();action_.reset();acoustics_.reset();metrics_={};
}
void PhysicalInstrument::noteOn(int note,double velocity) noexcept {
  if(note<21||note>108||!std::isfinite(velocity))return;
  if(velocity<=0){noteOff(note);return;}
  // The key action supplies hammer work; do not also inject a synthetic
  // instantaneous strike into the strings.
  action_.press(note,velocity);mechanics_.setKeyDown(note,true);
}
void PhysicalInstrument::noteOff(int note) noexcept {
  action_.release(note);mechanics_.noteOff(note);
}
void PhysicalInstrument::sustain(double value) noexcept { mechanics_.sustain(value); }
void PhysicalInstrument::allSoundOff() noexcept { reset(); }
double PhysicalInstrument::energy() const noexcept {
  double result=mechanics_.energy()+action_.energy()+acoustics_.energy();
  if(action_.configuration().hammerContactEnabled)
    for(int note=21;note<=108;++note)
      result+=physics::contactPotential(action_.state(note).hammerPosition-
        mechanics_.keyDisplacement(note),action_.configuration().hammerContact);
  return result;
}
void PhysicalInstrument::process(float* left,float* right,uint32_t frames) noexcept {
  if(!left||!right)return;
  for(uint32_t i=0;i<frames;++i) {
    action_.beginFrame();mechanics_.beginFrame();
    for(int note=21;note<=108;++note) {
      if(!action_.active(note))continue;
      const physics::ContactPort port{mechanics_.keyPreviousDisplacement(note),
        mechanics_.keyDisplacement(note),mechanics_.contactCompliance(note)};
      const auto contact=action_.solveStringContact(note,port);
      if(!contact.valid){++metrics_.invalidContacts;continue;}
      metrics_.maximumContactResidual=std::max(metrics_.maximumContactResidual,absolute(contact.residual));
      if(contact.force>0) {
        const double before=mechanics_.keyEnergy(note);
        const double displacementBefore=mechanics_.keyPreviousDisplacement(note);
        (void)mechanics_.applyContactForce(note,contact.force);
        const double displacementAfter=mechanics_.keyDisplacement(note);
        const double work=contact.force*(displacementAfter-displacementBefore);
        metrics_.maximumContactEnergyResidual=std::max(metrics_.maximumContactEnergyResidual,
          absolute((mechanics_.keyEnergy(note)-before)-work));
        metrics_.contactDissipation+=contact.dissipatedEnergy;++metrics_.contactFrames;
      }
    }
    action_.endFrame();mechanics_.finishFrame();
    const auto load=acoustics_.step({mechanics_.boardVelocity(0),mechanics_.boardInverseMass(0)});
    if(load.valid) {
      const double mechanicalWork=mechanics_.boardImpulse(0,load.boardImpulse);
      metrics_.maximumAcousticReactionResidual=std::max(metrics_.maximumAcousticReactionResidual,
        absolute(mechanicalWork-load.boardWork));
      metrics_.maximumAcousticBalanceResidual=std::max(metrics_.maximumAcousticBalanceResidual,
        absolute(load.balanceResidual));
      metrics_.acousticDissipation+=load.couplingDissipation+load.radiationDissipation+
        load.playerDissipation+load.internalDissipation+load.numericalDissipation;
    }
    // The radiation observation is separate from mechanical energy. Both the
    // board reaction and cavity motion are connected even when this diagnostic
    // output proxy omits a far-field microphone/room observation.
    mechanics_.observe(left[i],right[i]);++metrics_.frames;
  }
}
} // namespace keyra
