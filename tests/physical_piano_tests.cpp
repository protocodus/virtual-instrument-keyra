#include "keyra/PhysicalPiano.h"
#include "keyra/physics/ModalBank.h"
#include "keyra/physics/Bridge.h"
#include <array>
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <limits>

namespace {
void require(bool condition,const char* message){if(!condition){std::cerr<<"FAIL "<<message<<'\n';std::exit(1);}}
void bridgeIdentity(){
  std::array<keyra::physics::ModalBank<1>,88> strings{};
  keyra::physics::ModalBank<3> board;board.count=3;
  for(unsigned i=0;i<88;++i){strings[i].count=1;auto& m=strings[i].modes[0];m.v=std::sin(i*.31)*.1;m.x=std::cos(i*.7)*.02;m.port[0]=.2+i*.001;}
  for(unsigned i=0;i<3;++i){auto& m=board.modes[i];m.v=.02*(i+1);m.port={.4-.03*i,.2+.07*i,-.1+.04*i};}
  keyra::physics::PassiveBridge<88> bridge;
  require(bridge.configure(strings,board,1./8000,8),"bridge configuration");
  const auto energy=[&](){double e=board.energy();for(const auto& s:strings)e+=s.energy();return e;};
  double previous=energy();
  for(unsigned i=0;i<1024;++i){bridge.step(strings,board);const double current=energy();require(current<=previous+2.e-15,"midpoint bridge added mechanical energy");previous=current;}
  require(bridge.maximumPositiveEnergyChange<1.e-15,"bridge work positive");
  require(bridge.maximumBalanceResidual<1.e-14,"bridge discrete power identity residual");
  require(bridge.dissipatedEnergy>1.e-5,"bridge did not dissipate relative port motion");
}
void energyAndTransfer(){
  for(double rate:{8000.,44100.,48000.,96000.,192000.}){
    keyra::PhysicalPiano p;require(p.prepare(rate),"physical sample rate");p.sustain(1);p.setResonance(1);p.noteOn(60,.8);
    double previous=p.energy();require(previous>0,"strike adds mechanical energy");
    std::array<float,64> l{},r{};
    for(unsigned i=0;i<80;++i){p.process(l.data(),r.data(),64);const double current=p.energy();require(std::isfinite(current)&&current<=previous*(1+1.e-10)+1.e-15,"unforced physical model energy increased");previous=current;for(unsigned j=0;j<64;++j)require(std::isfinite(l[j])&&std::isfinite(r[j]),"nonfinite physical pressure");}
    require(p.boardEnergy()>1.e-15,"strings did not transfer energy to wood");
    require(p.keyEnergy(72)>1.e-20,"unstruck octave receiver did not gain mechanical energy");
    const auto metrics=p.metrics();require(metrics.maximumBridgeBalanceResidual<1.e-13,"coupled mechanical work balance");
    const double old=p.energy();require(!p.prepare(std::numeric_limits<double>::quiet_NaN()),"invalid sample rate accepted");require(p.energy()==old,"invalid sample rate changed physical state");
  }
  keyra::PhysicalPiano uncoupled;uncoupled.sustain(1);uncoupled.setCouplingEnabled(false);uncoupled.noteOn(60,.8);
  std::array<float,64> l{},r{};for(unsigned i=0;i<80;++i)uncoupled.process(l.data(),r.data(),64);
  require(uncoupled.keyEnergy(72)==0&&uncoupled.boardEnergy()==0,"disabled bridge still transfers energy");
}
void contactPorts(){
  keyra::PhysicalPiano p;p.setCouplingEnabled(false);p.sustain(1);p.setKeyDown(60,true);
  const double injected=p.keyImpulse(60,.0002);require(injected>0,"contact impulse adds energy");
  require(std::abs(injected-p.energy())<1.e-15,"impulse work does not match energy");
  const double oldQ=p.keyDisplacement(60);p.beginFrame();
  require(p.keyPreviousDisplacement(60)==oldQ,"old contact displacement not saved");
  const double freeQ=p.keyDisplacement(60),energy=p.energy(),compliance=p.contactCompliance(60),force=.4;
  require(compliance>0&&p.keyInverseMass(60)>0,"invalid mechanical contact compliance");
  const double work=p.applyContactForce(60,force),newQ=p.keyDisplacement(60);
  require(std::abs((newQ-freeQ)-force*compliance)<1.e-17,"constant-force displacement compliance");
  require(std::abs((p.energy()-energy)-work)<1.e-15,"constant-force work mismatch");
  require(std::abs(work-force*(newQ-oldQ))<1.e-13,"exact forced oscillator work identity");
  float l=0,r=0;p.endFrame(l,r);
  const double beforeQ=p.keyDisplacement(60);p.noteOn(60,.6);require(p.keyDisplacement(60)==beforeQ,"repeated strike reset persistent string position");
  const double G=p.boardInverseMass(1),v=p.boardVelocity(1),J=.0003;const double boardWork=p.boardImpulse(1,J);
  require(G>0&&std::abs(p.boardVelocity(1)-(v+G*J))<1.e-14,"wood port reciprocal impulse");
  require(std::abs(boardWork-(J*v+.5*J*J*G))<1.e-15,"wood impulse work identity");
}
void observationsAndPedal(){
  keyra::PhysicalPiano a,b;require(a.prepare(48000)&&b.prepare(48000),"prepare observation twins");a.sustain(1);b.sustain(1);a.noteOn(60,.7);b.noteOn(60,.7);b.setRadiationEnabled(false);
  std::array<float,64> l{},r{},bl{},br{};double audible=0;
  for(unsigned i=0;i<100;++i){a.process(l.data(),r.data(),64);b.process(bl.data(),br.data(),64);require(a.energy()==b.energy(),"radiation changed mechanical forces/energy");for(unsigned j=0;j<64;++j){require(bl[j]==0&&br[j]==0,"disabled radiation not silent");audible+=l[j]*l[j]+r[j]*r[j];}}
  require(audible>1.e-8,"mechanical candidate silent");
  keyra::PhysicalPiano closed,open;closed.setResonance(1);open.setResonance(1);open.sustain(1);closed.noteOn(60,.8);open.noteOn(60,.8);
  for(unsigned i=0;i<240;++i){closed.process(l.data(),r.data(),64);open.process(bl.data(),br.data(),64);}
  require(open.keyEnergy(72)>closed.keyEnergy(72)*1.2,"lifting unstruck dampers did not increase sympathetic receiver energy");
  a.reset();require(a.energy()==0,"reset left physical state");
}
void blockPartition(){
  keyra::PhysicalPiano a,b;a.sustain(1);b.sustain(1);a.noteOn(60,.7);b.noteOn(60,.7);
  std::array<float,1024> al{},ar{},bl{},br{};a.process(al.data(),ar.data(),1024);
  for(unsigned i=0;i<1024;++i)b.process(bl.data()+i,br.data()+i,1);
  require(al==bl&&ar==br&&a.energy()==b.energy(),"mechanical model depends on host block partition");
}
void materialMechanics(){
  keyra::PhysicalPiano p;const double sitka=p.boardModeFrequency(0),massSitka=p.boardInverseMass(0);
  require(p.setSoundboardMaterial(1)&&p.soundboardMaterial()==1,"Norway material setup");
  require(std::abs(p.boardModeFrequency(0)-sitka)>.1,"wood moduli did not affect structural modal frequency");
  require(std::abs(p.boardInverseMass(0)-massSitka)>.001,"wood density did not affect mechanical modal port mass");
  require(!p.setSoundboardMaterial(-1)&&p.soundboardMaterial()==1,"invalid material changed state");
  p.sustain(1);p.noteOn(60,.7);double before=p.energy();std::array<float,64> l{},r{};
  for(unsigned i=0;i<32;++i){p.process(l.data(),r.data(),64);require(p.energy()<=before+1.e-14,"alternate wood coupling added energy");before=p.energy();}
}
void nonlinearHammerEnergy(){
  for(double rate:{44100.,48000.,96000.})for(double dissipation:{0.,.08}){
    keyra::PhysicalPiano p;require(p.prepare(rate),"hammer rate setup");
    keyra::physics::ContactLaw law;law.dissipation=dissipation;
    require(p.setHammerContactLaw(law),"hammer contact law setup");p.setMechanicalLossEnabled(false);p.setCouplingEnabled(false);p.setNonlinearHammerEnabled(true);p.sustain(1);p.noteOn(60,.8);
    const double initial=p.energy();require(initial>0&&p.hammerEnergy()==initial&&p.keyEnergy(60)==0,"nonlinear note launch double-injected strings");
    double previous=initial;
    for(unsigned i=0;i<static_cast<unsigned>(rate*.018);++i){float l=0,r=0;p.process(&l,&r,1);const auto m=p.contactMetrics();const double stored=p.energy()+m.retiredHammerEnergy;
      require(std::isfinite(l)&&std::isfinite(r)&&stored<=previous+1.e-11,"unforced hammer/string contact added energy");
      require(std::abs(stored+m.dissipatedEnergy-initial)<1.e-9,"hammer/contact energy ledger does not balance");previous=stored;
    }
    const auto m=p.contactMetrics();require(m.invalidContacts==0&&m.contactFrames>0,"nonlinear hammer did not make valid contact");
    require(m.maximumEnergyResidual<1.e-11,"nonlinear hammer work/potential residual");require(m.maximumForceResidual<1.e-8,"nonlinear hammer force residual");
    if(dissipation>0)require(m.dissipatedEnergy>1.e-10,"dissipative contact lost no energy");
    else require(m.dissipatedEnergy<1.e-10,"conservative contact spuriously dissipated");
    require(p.keyEnergy(60)>0,"nonlinear hammer did not transfer energy to strings");
  }
}
void polarizationAndPhaseStems(){
  keyra::PhysicalPiano p;p.setNonlinearHammerEnabled(true);p.sustain(1);p.noteOn(60,.8);
  double primary=0,secondary=0,wood=0,quadrature=0;
  for(unsigned i=0;i<4096;++i){float l=0,r=0;p.process(&l,&r,1);const auto stems=p.observeStems();const auto bases=p.observeQuadratureStems();
    require(l==static_cast<float>(stems.primary[0]+stems.secondary[0]+stems.board[0])&&r==static_cast<float>(stems.primary[1]+stems.secondary[1]+stems.board[1]),"stems do not reconstruct shared mechanical observation");
    primary+=stems.primary[0]*stems.primary[0];secondary+=stems.secondary[0]*stems.secondary[0];wood+=stems.board[0]*stems.board[0];quadrature+=bases.velocity.primary[0]*bases.velocity.primary[0];
  }
  require(primary>1.e-12&&secondary>1.e-12&&wood>1.e-18&&quadrature>1.e-12,"physical polarization/wood/quadrature stem missing");
  const double before=p.energy();p.setComplexRadiationEnabled(false);require(p.energy()==before,"complex phase observation changed mechanics");
  p.setComplexRadiationEnabled(true);require(p.energy()==before,"restoring complex phase observation changed mechanics");
}
void fullReferenceBoard(){
  keyra::PhysicalPiano p;p.setReferenceSoundboardEnabled(true);
  require(p.referenceSoundboardEnabled()&&p.boardModeCount()==475,"full reference board lost original475 retained modes");
  require(p.boardModeFrequency(0)>75.3&&p.boardModeFrequency(0)<75.4,"full reference board lower pole differs");
  require(p.boardModeFrequency(474)>12992&&p.boardModeFrequency(474)<12993,"full reference board upper pole differs");
  p.setResonance(.5);p.setNonlinearHammerEnabled(true);p.sustain(1);p.noteOn(60,.8);
  double previous=p.energy();std::array<float,64> l{},r{};
  for(unsigned i=0;i<48;++i){p.process(l.data(),r.data(),64);require(p.energy()<=previous+1.e-10,"full board/nonlinear hammer added unforced energy");previous=p.energy();for(unsigned j=0;j<64;++j)require(std::isfinite(l[j])&&std::isfinite(r[j]),"nonfinite acceleration observation");}
  require(p.metrics().maximumBridgeBalanceResidual<1.e-12,"full board reciprocal work balance");
  const auto stems=p.observeStems();p.observe(l[0],r[0]);require(l[0]==static_cast<float>(stems.primary[0]+stems.secondary[0]+stems.board[0]),"full acceleration board stems do not reconstruct");
  keyra::physics::ModalBank<1> observer;observer.count=1;observer.accelerationObserver=true;auto& mode=observer.modes[0];
  mode.x=.002;mode.v=.01;mode.omega=10;mode.lossSigma=2;mode.observation={1,1};mode.port={.3,0,0};mode.inverseStep=48000;
  (void)observer.portImpulse({.001,0,0});(void)observer.portImpulse({.0002,0,0});
  const double force=.3*.0012*48000;const double expected=-10*.002-4*mode.v+force;
  require(std::abs(observer.radiation()[0]-expected)<1.e-13,"acceleration observer omitted accumulated bridge/reaction force");
  observer.freeStep();require(mode.appliedForce==0,"new frame retained stale board forcing");
}
}
int main(){bridgeIdentity();energyAndTransfer();contactPorts();observationsAndPedal();blockPartition();materialMechanics();nonlinearHammerEnergy();polarizationAndPhaseStems();fullReferenceBoard();std::cout<<"PASS physical bridge, passivity, sympathetic transfer, contact/work ports, radiation isolation, pedal, block invariance, structural wood, nonlinear hammer, complex stems and full reference board\n";}
