#include "../tools/mechanism_network_support.h"
#include <cstdio>
#include <cstdlib>
#include <limits>
#include <new>

namespace {
using namespace keyra::physics;
namespace probe=keyra::mechanism_probe;
bool trackAllocation=false;
unsigned allocations=0;
void require(bool yes,const char* text) {
  if (!yes) { std::fprintf(stderr,"FAIL mechanism network: %s\n",text); std::exit(1); }
}
bool near(double a,double b,double tolerance=2.e-12) {
  return std::abs(a-b)<=tolerance*(1+std::abs(a)+std::abs(b));
}
uint32_t randomState=0x1234abcdu;
double uniform() {
  randomState^=randomState<<13; randomState^=randomState>>17; randomState^=randomState<<5;
  return double(randomState)/4294967295.;
}

void isolatedAndReciprocal() {
  MechanismExciter source;
  auto config=mechanismPreset(MechanismKind::Keybed); config.lossPerSecond=0;
  require(source.prepare(config),"lossless source prepare");
  source.setCouplingEnabled(false);
  const double work=source.trigger(.7),initial=source.energy();
  require(near(work,initial),"trigger external-work identity");
  for (unsigned i=0;i<48000;++i) {
    const auto result=source.step({0,1});
    require(result.valid&&std::abs(result.balanceResidual)<1.e-16,"lossless source balance");
  }
  require(std::abs(source.energy()/initial-1)<2.e-10,"lossless source accumulated drift");

  double maximumResidual=0;
  for (unsigned i=0;i<3000;++i) {
    config.sampleRate=i%3==0?8000:i%3==1?48000:192000;
    config.lossPerSecond=uniform()*1000;
    config.couplingResistanceKgPerSecond=std::pow(10.,-3+uniform()*7);
    require(source.prepare(config),"random reciprocal prepare");
    source.setCouplingEnabled(true);
    (void)source.trigger(uniform());
    const MechanismBodyPort body{(uniform()-.5)*2,uniform()*100};
    const auto result=source.step(body);
    maximumResidual=std::max(maximumResidual,std::abs(result.balanceResidual));
    require(result.valid&&result.couplingDissipation>=0&&result.internalDissipation>=0,
            "negative or invalid source dissipation");
    require(std::abs(result.balanceResidual)<1.e-12,"reciprocal source/body work ledger");
    require(near(result.bodyWork,result.bodyImpulse*body.velocity+
                 .5*body.inverseMass*result.bodyImpulse*result.bodyImpulse),"body impulse work identity");
    require(result.sourceEnergyAfter+result.bodyWork<=result.sourceEnergyBefore+1.e-12,
            "source/body junction created mechanical energy");
  }
  std::printf("isolated/reciprocal maximum ledger residual %.12g J\n",maximumResidual);
}

void validationAndAblations() {
  MechanismExciter observed,muted;
  (void)observed.trigger(.8); (void)muted.trigger(.8); muted.setObservationEnabled(false);
  for (unsigned i=0;i<1200;++i) {
    const auto a=observed.step({.02,3}),b=muted.step({.02,3});
    require(a.bodyImpulse==b.bodyImpulse&&observed.energy()==muted.energy(),
            "observation-only mute changed mechanical state");
    require(muted.directObservation()==0,"muted observation audible");
  }
  auto bad=observed.config(); bad.modalMassKg=-1;
  const double before=observed.energy();
  require(!observed.prepare(bad)&&observed.energy()==before,"invalid setup changed state");
  const auto result=observed.step({std::numeric_limits<double>::infinity(),1});
  require(!result.valid&&observed.energy()==before&&result.bodyImpulse==0,
          "invalid port changed source state");
  observed.setEnabled(false);
  require(observed.energy()==0&&observed.ledger().retiredEnergy>=before,
          "disabled source failed to retire stored energy");
  require(observed.trigger(1)==0&&observed.step({1,3}).bodyImpulse==0,
          "disabled source excited network");

  MechanismExciter tail;
  tail.setCouplingEnabled(false); (void)tail.trigger(1);
  trackAllocation=true;
  for (unsigned i=0;i<480000;++i) (void)tail.step({0,0});
  trackAllocation=false;
  require(allocations==0,"source realtime path allocated");
  require(tail.energy()==0&&tail.ledger().retiredEnergy>0,"silent tail not retired before subnormals");
}

void fullNetworkTransfer() {
  grand::Piano piano(probe::options()); probe::openDampers(piano);
  std::array<MechanismExciter,4> sources;
  probe::prepare(sources,48000);
  // A keybed and a pedal impulse enter the same physical board that is coupled
  // to all unstruck strings; no noteOn or string initial condition is used.
  const double external=sources[1].trigger(.7)+sources[3].trigger(.6);
  MechanismExciter isolated;
  require(isolated.prepare(mechanismPreset(MechanismKind::Keybed)),"isolated keybed setup");
  isolated.setCouplingEnabled(false); (void)isolated.trigger(.7);
  double maximumBoard=0,maximumStrings=0,maximumResidual=0,maximumReaction=0,tailDifference=0;
  double previous=external;
  for (unsigned frame=0;frame<4800;++frame) {
    const auto result=probe::step(piano,sources,frame);
    (void)isolated.step({0,0});
    tailDifference=std::max(tailDifference,std::abs(sources[1].directObservation()-isolated.directObservation()));
    require(result.valid,"full mechanism network nonfinite");
    maximumResidual=std::max(maximumResidual,result.maximumSourceBalanceResidual);
    maximumReaction=std::max(maximumReaction,result.maximumReactionWorkResidual);
    if ((frame&31u)==0) {
      maximumBoard=std::max(maximumBoard,probe::boardEnergy(piano));
      maximumStrings=std::max(maximumStrings,probe::stringEnergy(piano));
      double total=piano.energy(); for (const auto& s:sources) total+=s.energy();
      require(total<=previous+1.e-12,"unforced full mechanism network created energy");
      previous=total;
    }
  }
  require(maximumBoard>1.e-12&&maximumStrings>1.e-14,"mechanism failed to excite body/unstruck strings");
  require(maximumReaction<1.e-12&&maximumResidual<1.e-12,"full board reaction-work mismatch");
  require(tailDifference>1.e-10,"body coupling did not alter mechanism tail");
  std::printf("source->body max %.12g J; unstruck strings max %.12g J; reaction residual %.12g J\n",
              maximumBoard,maximumStrings,maximumReaction);

  grand::Piano reverse(probe::options()); probe::openDampers(reverse);
  std::array<MechanismExciter,4> receiving; probe::prepare(receiving,48000);
  (void)probe::bodyImpulse(reverse,1,.003);
  double received=0;
  for (unsigned frame=0;frame<1200;++frame) {
    require(probe::step(reverse,receiving,frame).valid,"reverse coupling nonfinite");
    received=std::max(received,receiving[1].energy());
  }
  require(received>1.e-12,"body motion failed to react back on source");
}

void disabledExactAndCouplingAblation() {
  grand::Piano reference(probe::options()),disabled(probe::options()),uncoupled(probe::options());
  std::array<MechanismExciter,4> off,isolated;
  probe::prepare(off,48000,false); probe::prepare(isolated,48000,true,false);
  reference.noteOn(60,61); disabled.noteOn(60,61);
  (void)isolated[1].trigger(.8);
  double direct=0;
  trackAllocation=true;
  for (unsigned frame=0;frame<2400;++frame) {
    const auto a=reference.step(frame);
    const auto b=probe::step(disabled,off,frame);
    const auto alone=probe::step(uncoupled,isolated,frame);
    require(a==b.combined&&a==b.network,"disabled source changed original output");
    require(alone.network[0]==0&&alone.network[1]==0,"coupling-off mechanism reached network");
    direct=std::max(direct,std::abs(alone.direct[0]));
  }
  trackAllocation=false;
  require(allocations==0,"integrated frame path allocated");
  require(probe::boardEnergy(uncoupled)==0&&probe::stringEnergy(uncoupled)==0&&direct>0,
          "isolated source/network ablation inconsistent");
}
}

void* operator new(std::size_t n) {
  if (trackAllocation) ++allocations;
  if (void* p=std::malloc(n)) return p;
  throw std::bad_alloc();
}
void* operator new[](std::size_t n) { return ::operator new(n); }
void operator delete(void* p) noexcept { std::free(p); }
void operator delete[](void* p) noexcept { std::free(p); }
void operator delete(void* p,std::size_t) noexcept { std::free(p); }
void operator delete[](void* p,std::size_t) noexcept { std::free(p); }

int main() {
  isolatedAndReciprocal(); validationAndAblations(); fullNetworkTransfer();
  disabledExactAndCouplingAblation();
  std::puts("PASS mechanism network: four test groups");
}
