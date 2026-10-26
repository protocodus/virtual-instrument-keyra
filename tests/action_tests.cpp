#include "keyra/physics/Action.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <new>
#include <stdexcept>

namespace {
bool allocationTrap=false;
unsigned allocationCount=0;
}
void* operator new(std::size_t n) {
  if(allocationTrap)++allocationCount;
  if(void* result=std::malloc(n?n:1))return result;
  throw std::bad_alloc();
}
void* operator new[](std::size_t n){return ::operator new(n);}
#if defined(__GNUC__) || defined(__clang__)
__attribute__((noinline))
#endif
void freeAllocation(void* p) noexcept {std::free(p);}
void operator delete(void* p) noexcept {freeAllocation(p);}
void operator delete[](void* p) noexcept {freeAllocation(p);}
void operator delete(void* p,std::size_t) noexcept {freeAllocation(p);}
void operator delete[](void* p,std::size_t) noexcept {freeAllocation(p);}

namespace {
using namespace keyra::physics;
constexpr double pi=3.14159265358979323846;
void require(bool condition,const char* message){if(!condition)throw std::runtime_error(message);}
double square(double value){return value*value;}
double loss(const ActionLedger& ledger) {
  return ledger.viscousDissipation+ledger.catchDissipation+ledger.contactDissipation+
         ledger.fingerDissipation+ledger.keybedDissipation;
}

void freeMassContact() {
  for(double rate:{8000.,44100.,48000.,96000.,192000.,384000.})for(double dissipation:{0.,.12}) {
    const double dt=1/rate,mh=.008,ms=.04;
    ContactLaw law{8.e8,2.5,dissipation};
    double yh=-.0001,ys=0,vh=3,vs=0;
    double prior=.5*mh*vh*vh;
    const double initial=prior;
    double accumulated=0,maxForce=0;
    for(unsigned i=0;i<unsigned(.012*rate);++i) {
      const double old=yh-ys;
      const auto result=solveContact(old,old+dt*(vh-vs),.5*dt*dt*(1/mh+1/ms),dt,law);
      require(result.valid&&result.force>=0&&result.iterations<=56,"invalid or adhesive free-mass contact");
      require(std::abs(result.residual)/(1+result.force)<1.e-10,"contact root did not converge");
      yh+=dt*vh-.5*dt*dt*result.force/mh;
      ys+=dt*vs+.5*dt*dt*result.force/ms;
      vh-=dt*result.force/mh;vs+=dt*result.force/ms;
      const double energy=.5*mh*vh*vh+.5*ms*vs*vs+contactPotential(yh-ys,law);
      accumulated+=result.dissipatedEnergy;maxForce=std::max(maxForce,result.force);
      require(energy<=prior+2.e-11,"contact created unforced mechanical energy");
      require(std::abs(energy+accumulated-initial)<2.e-10,"contact force work does not balance potential and dissipation");
      prior=energy;
    }
    require(maxForce>1,"free-mass contact witness was not activated");
    if(dissipation==0)require(std::abs(prior-initial)<2.e-10,"conservative contact lost energy");
    else require(accumulated>1.e-5,"dissipative contact did not dissipate");
  }
}

void oscillatorContact() {
  for(double rate:{44100.,48000.,96000.}) {
    const double dt=1/rate,mh=.008,ms=.05,w=2*pi*261.625565;
    const double c=std::cos(w*dt),s=std::sin(w*dt);
    const double forceQ=2*square(std::sin(.5*w*dt))/(ms*w*w),forceV=s/(ms*w);
    ContactLaw law{1.e9,2.5,0};
    double hammer=-.00005,hv=2,q=0,v=0;
    const double initial=.5*mh*hv*hv;
    double maxWorkDefect=0,maxTotalDefect=0;
    for(unsigned i=0;i<unsigned(.02*rate);++i) {
      const double oldHammer=hammer,oldQ=q;
      const double freeQ=c*q+s*v/w,freeV=c*v-s*w*q;
      const double oldOsc=.5*ms*(v*v+w*w*q*q);
      auto result=solveContact(oldHammer-oldQ,oldHammer+dt*hv-freeQ,
                               .5*dt*dt/mh+forceQ,dt,law);
      require(result.valid,"harmonic contact solver failed");
      hammer=oldHammer+dt*hv-.5*dt*dt*result.force/mh;hv-=dt*result.force/mh;
      q=freeQ+forceQ*result.force;v=freeV+forceV*result.force;
      const double energyOsc=.5*ms*(v*v+w*w*q*q);
      maxWorkDefect=std::max(maxWorkDefect,std::abs(energyOsc-oldOsc-result.force*(q-oldQ)));
      maxTotalDefect=std::max(maxTotalDefect,std::abs(.5*mh*hv*hv+energyOsc+contactPotential(hammer-q,law)-initial));
    }
    require(maxWorkDefect<2.e-12,"constant-force harmonic port violates force/displacement work");
    require(maxTotalDefect<2.e-10,"hammer/string harmonic exchange is not conservative");
  }
}

void actionCycle() {
  for(double rate:{44100.,48000.,96000.}) {
    Action action;require(action.prepare(rate),"action prepare failed");action.press(60,.8);
    std::array<bool,6> stages{};double maxBudget=0,maxBed=0,maxHammer=0,maxKey=0;
    double previous=0;bool unforced=false;
    for(unsigned i=0;i<unsigned(rate);++i) {
      if(i==unsigned(rate*.25))action.release(60);
      action.beginFrame();
      const auto contact=action.solveStringContact(60,{0,0,0});
      require(contact.valid,"rigid string contact failed");action.endFrame();
      const auto state=action.state(60);const auto& ledger=action.ledger();
      stages[unsigned(state.stage)]=true;
      maxBed=std::max(maxBed,state.keybedForce);maxHammer=std::max(maxHammer,state.hammerForce);
      maxKey=std::max(maxKey,state.keyPosition);
      require(state.fingerForce>=0&&state.keybedForce>=0&&state.hammerForce>=0,"action contact became adhesive");
      require(std::isfinite(state.keyPosition)&&std::isfinite(state.hammerPosition),"nonfinite action state");
      const double potential=contactPotential(state.hammerPosition,action.configuration().hammerContact);
      const double energy=action.energy()+potential;
      const double defect=energy+loss(ledger)-ledger.fingerWork;
      maxBudget=std::max(maxBudget,std::abs(defect));
      if(unforced)require(energy<=previous+2.e-11,"released action created energy");
      unforced=i>unsigned(.28*rate)&&state.fingerPosition==0;previous=energy;
    }
    require(maxBudget<1.e-8,"full action finger-work ledger did not close");
    require(maxBed>1&&maxHammer>1,"keybed/hammer witness did not activate");
    require(maxKey>.0095&&maxKey<.0115,"key travel is not bounded by the mechanical bed");
    for(bool visited:stages)require(visited,"action cycle omitted a driven/flight/contact/backcheck/release/rest stage");
    require(!action.active(60),"released action failed to settle to rest");
    require(action.ledger().maximumContactResidual<1.e-10,"full action contact residual excessive");
  }
}

double keyAfterHold(Action& action,bool* hit=nullptr) {
  action.press(60,.8);double maxBed=0,maxTravel=0;
  for(unsigned i=0;i<6000;++i) {
    action.beginFrame();auto r=action.solveStringContact(60,{0,0,0});
    require(r.valid,"isolation contact failure");action.endFrame();
    maxBed=std::max(maxBed,action.state(60).keybedForce);
    maxTravel=std::max(maxTravel,action.state(60).keyPosition);
  }
  if(hit)*hit=maxBed>1;
  return maxTravel;
}
void isolationAndRetrigger() {
  Action noFinger;auto config=noFinger.configuration();config.fingerEnabled=false;
  require(noFinger.configure(config),"finger ablation configure failed");keyAfterHold(noFinger);
  require(noFinger.energy()<1.e-18&&noFinger.state(60).fingerForce==0,"disabled finger still excites action");
  Action normal,noBed;config=noBed.configuration();config.keybedEnabled=false;
  require(noBed.configure(config),"bed ablation configure failed");bool bedWitness=false;
  const double heldNormal=keyAfterHold(normal,&bedWitness),heldNoBed=keyAfterHold(noBed);
  require(bedWitness&&noBed.state(60).keybedForce==0,"bed ablation witness invalid");
  require(heldNoBed>heldNormal+.0002,"removing the bed did not change held key travel");
  Action noJack;config=noJack.configuration();config.jackEnabled=false;
  require(noJack.configure(config),"jack ablation configure failed");keyAfterHold(noJack);
  require(noJack.energy(60).hammerKinetic+noJack.energy(60).hammerReturn<1.e-18,"disabled jack drove the hammer");
  const auto before=normal.state(60);normal.press(60,.3);const auto after=normal.state(60);
  require(before.keyPosition==after.keyPosition&&before.hammerPosition==after.hammerPosition&&
          before.keyVelocity==after.keyVelocity&&before.hammerVelocity==after.hammerVelocity,
          "repeated MIDI press teleported or reset the physical key/hammer");
}

void contractAndMalformed() {
  Action action;action.press(60,.7);action.beginFrame();
  const auto first=action.solveStringContact(60,{0,0,0});
  require(first.valid&&!action.solveStringContact(60,{0,0,0}).valid,"duplicate contact application accepted");
  const auto once=action.state(60);action.beginFrame();
  require(action.state(60).keyPosition==once.keyPosition,"duplicate begin advanced physical time");
  action.endFrame();action.endFrame();
  const auto before=action.state(60);const double energy=action.energy();
  require(!action.prepare(0)&&!action.prepare(std::numeric_limits<double>::quiet_NaN()),"invalid action sample rate accepted");
  auto config=action.configuration();config.hammerMass=-1;require(!action.configure(config),"negative hammer mass accepted");
  action.press(-1,.9);action.release(109);action.press(60,std::numeric_limits<double>::infinity());
  action.setFingerTarget(60,0,std::numeric_limits<double>::quiet_NaN());
  require(action.energy()==energy&&action.state(60).keyPosition==before.keyPosition,"invalid input mutated action");
  const ContactLaw law{};
  require(!solveContact(0,0,-1,1./48000,law).valid,"negative port compliance accepted");
  require(!solveContact(0,0,1,0,law).valid,"zero contact step accepted");
  require(solveContact(-.1,-.2,1,1./48000,law).force==0,"separated contact exerts force");
}

void allocations() {
  Action action;action.prepare(48000);
  allocationCount=0;allocationTrap=true;
  action.press(60,.8);
  for(unsigned i=0;i<4000;++i) {
    if(i==2000)action.release(60);
    action.beginFrame();(void)action.solveStringContact(60,{0,0,0});action.endFrame();
  }
  allocationTrap=false;
  require(allocationCount==0,"real-time action allocated C++ memory");
}
}
int main() {
  const std::array<std::pair<const char*,void(*)()>,6> tests{{
    {"free-mass nonlinear contact energy",freeMassContact},
    {"harmonic string contact work",oscillatorContact},
    {"finger/key/bed/escapement/hammer/release ledger",actionCycle},
    {"module isolation and state-preserving repetition",isolationAndRetrigger},
    {"frame contract and malformed inputs",contractAndMalformed},
    {"real-time C++ allocation trap",allocations}
  }};
  unsigned passed=0;
  for(const auto& test:tests)try{test.second();++passed;std::cout<<"PASS "<<test.first<<'\n';}
  catch(const std::exception& e){allocationTrap=false;std::cerr<<"FAIL "<<test.first<<": "<<e.what()<<'\n';}
  std::cout<<passed<<'/'<<tests.size()<<" action test groups passed\n";
  return passed==tests.size()?0:1;
}
