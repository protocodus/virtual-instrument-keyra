#include "../tools/local_resonance_support.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <new>

namespace {
using namespace keyra::physics;
namespace probe=keyra::local_resonance_probe;
bool trackAllocation=false;
unsigned allocations=0;
void require(bool good,const char* message) {
  if (!good) { std::fprintf(stderr,"FAIL local resonance: %s\n",message); std::exit(1); }
}
uint32_t state=0x19c3abcdu;
double uniform() {
  state^=state<<13;state^=state>>17;state^=state<<5;return double(state)/4294967295.;
}
void clearNetwork(grand::Piano& piano) {
  for (auto& string:piano.strings) {
    std::fill(string.m.q.begin(),string.m.q.end(),0);
    std::fill(string.m.p.begin(),string.m.p.end(),0);
    string.force=string.velocity=0;
  }
  for (auto& b:piano.board) b.q=b.p=b.force=0;
  for (auto& key:piano.keys) key.hammerActive=false;
}
void seedSpeakingKey(grand::Piano& piano,int note,double velocity) {
  const auto i=piano.keys[note-21].strings.front();
  piano.strings[i].m.p[0]=velocity/piano.strings[i].m.omega[0];
}

void passiveCouplerAndValidation() {
  double maximum=0;
  for (unsigned i=0;i<3000;++i) {
    LocalResonance auxiliary;
    auto config=auxiliary.config();
    config.sampleRate=i%3==0?44100:i%3==1?48000:192000;
    config.lossPerSecond=uniform()*100;
    config.couplingResistance=std::pow(10.,uniform()*6-3);
    require(auxiliary.prepare(config),"random config rejected");
    double speakingVelocity=(uniform()-.5)*2;
    const double G=.01+uniform()*100;
    for (unsigned frame=0;frame<20;++frame) {
      const double oldVelocity=speakingVelocity;
      const auto r=auxiliary.step({oldVelocity,G});
      speakingVelocity+=G*r.speakingImpulse;
      const double actualWork=r.speakingImpulse*oldVelocity+.5*G*r.speakingImpulse*r.speakingImpulse;
      maximum=std::max(maximum,std::abs(r.balanceResidual));
      require(r.valid&&r.couplingDissipation>=0&&r.internalDissipation>=0,"active or invalid local mode");
      require(std::abs(actualWork-r.speakingWork)<1.e-13,"speaking work identity");
      require(std::abs(r.balanceResidual)<1.e-12,"local energy balance");
      require(r.energyAfter+r.speakingWork<=r.energyBefore+1.e-12,"unforced local coupler created energy");
    }
  }
  LocalResonance auxiliary;
  require(auxiliary.energy()==0,"new auxiliary has independent initial energy");
  for (unsigned i=0;i<1000;++i) require(auxiliary.step({0,1}).energyAfter==0,"silent strings excited auxiliary");
  (void)auxiliary.step({1,2});
  const double before=auxiliary.energy();
  auto invalid=auxiliary.config();invalid.frequencyHz=std::numeric_limits<double>::infinity();
  require(!auxiliary.prepare(invalid)&&auxiliary.energy()==before,"invalid config changed state");
  const auto bad=auxiliary.step({std::numeric_limits<double>::quiet_NaN(),1});
  require(!bad.valid&&auxiliary.energy()==before&&bad.speakingImpulse==0,"invalid port changed state");
  std::printf("local reciprocal maximum balance residual %.12g J\n",maximum);
}

void reverseAndObserverIsolation() {
  LocalResonance auxiliary,muted;
  muted.setObservationEnabled(false);
  bool returned=false;
  for (unsigned frame=0;frame<300;++frame) {
    // All auxiliary energy originates in one speaking-port velocity impulse.
    const SpeakingStringPort port{frame==0?1.:0.,2};
    const auto a=auxiliary.step(port),b=muted.step(port);
    require(a.speakingImpulse==b.speakingImpulse&&auxiliary.energy()==muted.energy(),
            "observer mute changed reciprocal mechanics");
    require(muted.directObservation()==0,"observer mute audible");
    returned=returned||(frame>0&&a.speakingWork>0);
  }
  require(returned,"charged auxiliary did not return energy to speaking port");
  auto config=auxiliary.config();config.lossPerSecond=0;
  require(auxiliary.prepare(config),"conservative config");
  (void)auxiliary.step({1,1});auxiliary.setCouplingEnabled(false);
  const double initial=auxiliary.energy();
  for(unsigned i=0;i<96000;++i)(void)auxiliary.step({0,1});
  require(std::abs(auxiliary.energy()/initial-1)<2.e-10,"isolated conservative oscillator drift");
}

void fullKeyTransferAndField() {
  grand::Piano piano(probe::options());
  probe::SpeakingKeyPort<grand::Piano> key(piano,108);
  require(key.stringCount()==3,"C8 choir topology unexpected");
  require(std::abs(key.weight()-1/std::sqrt(3.))<1.e-15,"power-conjugate choir weight");
  seedSpeakingKey(piano,108,.1);
  const auto port=key.snapshot();
  const double before=key.energy();
  const auto actual=key.applyImpulse(.001);
  const double expected=.001*port.velocity+.5*port.inverseMass*.001*.001;
  require(std::abs(actual.work-expected)<1.e-14&&std::abs(key.energy()-before-expected)<1.e-14,
          "aggregate speaking-port impulse not power conjugate");
  clearNetwork(piano);seedSpeakingKey(piano,108,.1);
  LocalResonance auxiliary;
  double previous=piano.energy(),maximumEnergy=0,maximumWork=0,maximumField=0;
  for (unsigned frame=0;frame<2400;++frame) {
    const auto r=probe::step(piano,key,auxiliary,frame);
    require(r.valid,"full local network nonfinite");
    maximumEnergy=std::max(maximumEnergy,auxiliary.energy());
    maximumWork=std::max(maximumWork,std::abs(r.workResidual));
    if ((frame&31u)==0) {
      const double total=piano.energy()+auxiliary.energy();
      require(total<=previous+1.e-12,"unforced speaking/auxiliary network gained energy");previous=total;
      const auto recomputed=probe::recomputeObservation(piano);
      for (unsigned ch=0;ch<2;++ch) maximumField=std::max(maximumField,std::abs(recomputed[ch]-r.network[ch]));
    }
  }
  require(maximumEnergy>1.e-15,"speaking strings did not excite local mode");
  require(maximumWork<1.e-12&&maximumField<1.e-10,"post-coupling observation or work correction failed");
  const double persistent=auxiliary.energy();
  piano.noteOn(108,93);
  require(auxiliary.energy()==persistent,"key restrike reset auxiliary state");
  clearNetwork(piano);
  double returned=0;
  for (unsigned frame=2400;frame<2880;++frame) {
    require(probe::step(piano,key,auxiliary,frame).valid,"reverse full network nonfinite");
    returned=std::max(returned,key.energy());
  }
  require(returned>1.e-20,"stored local mode did not re-excite speaking strings");
  std::printf("C8 local energy max %.12g J; return key energy %.12g J; field correction error %.12g\n",
              maximumEnergy,returned,maximumField);
}

void ablationsAndRealtime() {
  grand::Piano reference(probe::options()),off(probe::options()),isolated(probe::options());
  probe::SpeakingKeyPort<grand::Piano> keyOff(off,108),keyIsolated(isolated,108);
  LocalResonance disabled,uncoupled;
  disabled.setEnabled(false);uncoupled.setCouplingEnabled(false);
  reference.noteOn(108,40);off.noteOn(108,40);isolated.noteOn(108,40);
  trackAllocation=true;
  for(unsigned frame=0;frame<2400;++frame) {
    const auto a=reference.step(frame);
    const auto b=probe::step(off,keyOff,disabled,frame);
    const auto c=probe::step(isolated,keyIsolated,uncoupled,frame);
    require(std::memcmp(a.data(),b.combined.data(),sizeof(a))==0,"disabled module changed original output bytes");
    require(std::memcmp(a.data(),c.combined.data(),sizeof(a))==0,"uncoupled zero-state auxiliary changed original output");
    require(uncoupled.energy()==0,"uncoupled zero-state auxiliary gained energy");
  }
  trackAllocation=false;
  require(allocations==0,"local realtime path allocated");
}
}

void* operator new(std::size_t n) {
  if(trackAllocation)++allocations;
  if(void* p=std::malloc(n))return p;throw std::bad_alloc();
}
void* operator new[](std::size_t n){return ::operator new(n);}
void operator delete(void* p)noexcept{std::free(p);}
void operator delete[](void* p)noexcept{std::free(p);}
void operator delete(void* p,std::size_t)noexcept{std::free(p);}
void operator delete[](void* p,std::size_t)noexcept{std::free(p);}
int main(){
  passiveCouplerAndValidation();reverseAndObserverIsolation();fullKeyTransferAndField();ablationsAndRealtime();
  std::puts("PASS local resonance: four test groups");
}
