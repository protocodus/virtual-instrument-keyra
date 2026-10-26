#include "keyra/PhysicalInstrument.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <limits>
#include <stdexcept>

namespace {
void require(bool condition,const char* message) { if(!condition)throw std::runtime_error(message); }
struct Witness {
  double energy=0,stringEnergy=0,boardEnergy=0,airEnergy=0,peak=0;
  keyra::PhysicalInstrumentMetrics metrics{};
};
Witness play(keyra::PhysicalInstrument& instrument,unsigned block=64) {
  std::array<float,257> left{},right{};
  instrument.sustain(1);instrument.noteOn(60,.8);
  Witness result;
  for(unsigned cursor=0;cursor<14400;) {
    const auto count=std::min(block,14400-cursor);
    instrument.process(left.data(),right.data(),count);cursor+=count;
    for(unsigned i=0;i<count;++i) {
      require(std::isfinite(left[i])&&std::isfinite(right[i]),"nonfinite connected output");
      result.energy+=double(left[i])*left[i]+double(right[i])*right[i];
      result.peak=std::max({result.peak,std::abs(double(left[i])),std::abs(double(right[i]))});
    }
    result.stringEnergy=std::max(result.stringEnergy,instrument.mechanics().keyEnergy(60));
    result.boardEnergy=std::max(result.boardEnergy,instrument.mechanics().boardEnergy());
    result.airEnergy=std::max(result.airEnergy,instrument.acoustics().energy());
  }
  result.metrics=instrument.metrics();return result;
}
}
int main() {
  try {
    keyra::PhysicalInstrument instrument;
    keyra::PhysicalInstrumentConfig config;
    config.acoustic.player.presence=1;
    require(instrument.prepare(config),"valid connected config rejected");
    const auto witness=play(instrument);
    require(witness.energy>1.e-10&&witness.stringEnergy>1.e-9,"action failed to excite strings");
    require(witness.boardEnergy>1.e-15&&witness.airEnergy>1.e-22,"wood/air path was not activated");
    require(witness.metrics.contactFrames>0&&witness.metrics.invalidContacts==0,"hammer contact was not solved");
    require(witness.metrics.maximumContactEnergyResidual<1.e-9,"contact work failed to cancel");
    require(witness.metrics.maximumAcousticBalanceResidual<1.e-9&&
            witness.metrics.maximumAcousticReactionResidual<1.e-9,"air/wood reaction energy mismatch");
    require(std::isfinite(instrument.energy())&&instrument.energy()>=0,"invalid system energy");

    keyra::PhysicalInstrument singleSample;
    require(singleSample.prepare(config),"single-frame config");
    const auto reference=play(singleSample,1);
    require(std::abs(reference.energy-witness.energy)<1.e-11,"block partition changed connected output");

    const double previousEnergy=instrument.energy();
    auto invalid=config;invalid.acoustic.cavityVolumeM3=-1;
    require(!instrument.prepare(invalid)&&instrument.energy()==previousEnergy,
            "invalid acoustic config changed mechanical state");
    invalid=config;invalid.sampleRate=std::numeric_limits<double>::quiet_NaN();
    require(!instrument.prepare(invalid)&&instrument.energy()==previousEnergy,"invalid sample rate changed state");
    auto basswood=config;basswood.keyWood=keyra::physics::materials::KeyWoodChoice::AmericanBasswood;
    keyra::PhysicalInstrument materialVariant;require(materialVariant.prepare(basswood),"key wood setup");
    require(materialVariant.action().configuration().keyMass!=instrument.action().configuration().keyMass,
            "sourced key density did not alter effective inertia");
    instrument.allSoundOff();
    require(instrument.energy()==0,"connected reset retained stored energy");
    std::cout<<"Connected finger/key/keybed/hammer/string/wood/air tests passed; "
             <<"contact frames="<<witness.metrics.contactFrames<<", peak="<<witness.peak<<'\n';
  } catch(const std::exception& error) { std::cerr<<error.what()<<'\n';return 1; }
}
