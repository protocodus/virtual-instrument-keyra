#include "keyra/physics/WaveguideString.h"
#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <limits>
#include <new>

namespace {
using String=keyra::physics::WaveguideString;
bool track=false;
unsigned allocations=0;
void require(bool condition,const char* message){
  if(!condition){std::fprintf(stderr,"FAIL waveguide string: %s\n",message);std::exit(1);}
}
unsigned randomState=0x1738abcdu;
double randomUnit(){randomState^=randomState<<13;randomState^=randomState>>17;randomState^=randomState<<5;return double(randomState)/4294967295.;}
String::Config integerConfig(){
  String::Config c;c.impedance=3.7;c.left.delaySamples=16;
  c.toBridge.delaySamples=c.fromBridge.delaySamples=56;return c;
}
void integerEnergyAndReaction(){
  String string;const auto config=integerConfig();require(string.prepare(config),"integer prepare");
  const double force=4;
  const auto strike=string.step(force);
  require(strike.valid&&strike.contactVelocity==force/(2*config.impedance),"force junction compliance");
  require(std::abs(string.energy()-String::stepSeconds*force*strike.contactVelocity)<1.e-18,"first force work");
  const double energy=string.energy();
  for(unsigned i=1;i<=384000;++i){
    const auto result=string.step();
    if(i==56)require(std::abs(result.bridgeForce+force)<1.e-14,"bridge reaction time/sign");
    if(i%128==0)require(std::abs(string.energy()-energy)<1.e-16,"lossless integer rail drift");
  }
  std::printf("waveguide integer 8 s energy drift %.12g J\n",string.energy()-energy);
}
void allpassAndLossLedger(){
  double maxResidual=0;
  for(unsigned trial=0;trial<32;++trial){
    String string;auto c=integerConfig();c.impedance=.1+randomUnit()*20;
    c.left.delaySamples=1+unsigned(randomUnit()*120);c.toBridge.delaySamples=1+unsigned(randomUnit()*120);
    c.left.allpassCount=4;c.toBridge.allpassCount=7;
    for(unsigned j=0;j<c.left.allpassCount;++j)c.left.allpass[j]=1.98*randomUnit()-.99;
    for(unsigned j=0;j<c.toBridge.allpassCount;++j)c.toBridge.allpass[j]=1.98*randomUnit()-.99;
    if(trial%2){c.left.lossMix=.5*randomUnit();c.toBridge.lossMix=.5*randomUnit();
      c.left.lossGain=.9+.1*randomUnit();c.toBridge.lossGain=.9+.1*randomUnit();}
    c.fromBridge=c.toBridge;require(string.prepare(c),"allpass prepare");
    for(unsigned i=0;i<20000;++i){
      const double contact=i<500?(randomUnit()-.5)*20:0;
      const double bridge=i<500?(randomUnit()-.5)*.01:0;
      const auto result=string.step(contact,bridge);
      require(result.valid&&result.dissipated>=0,"negative loss");
      if(i%97==0){const double residual=std::abs(string.balanceResidual());maxResidual=std::max(maxResidual,residual);
        require(residual<3.e-13*(1+std::abs(string.accumulatedWork())),"allpass/FIR work balance");}
    }
    require(string.energy()<=string.accumulatedWork()+2.e-13,"unforced energy grew");
  }
  std::printf("waveguide allpass/FIR random-port maximum balance residual %.12g J\n",maxResidual);
}
void shelfAndReadOnlyPorts(){
  double maximumResidual=0,maximumPrediction=0;
  for(unsigned trial=0;trial<36;++trial){
    String observed,untouched;auto c=integerConfig();c.impedance=.25+20*randomUnit();
    c.left.delaySamples=1+unsigned(70*randomUnit());
    c.toBridge.delaySamples=1+unsigned(100*randomUnit());
    c.left.allpassCount=3;c.toBridge.allpassCount=4;
    for(unsigned j=0;j<c.left.allpassCount;++j)c.left.allpass[j]=1.9*randomUnit()-.95;
    for(unsigned j=0;j<c.toBridge.allpassCount;++j)c.toBridge.allpass[j]=1.9*randomUnit()-.95;
    c.left.lossMix=.5*randomUnit();c.toBridge.lossMix=.5*randomUnit();
    c.left.dcPreservingLoss=c.toBridge.dcPreservingLoss=true;
    c.left.lossGain=trial%3==0?0:(trial%3==1?1:.1+.8*randomUnit());
    c.toBridge.lossGain=trial%3==1?0:(trial%3==2?1:.1+.8*randomUnit());
    const double poles[]={0,.1,.97,.9997};
    c.left.dcLossPole=poles[trial%4];c.toBridge.dcLossPole=poles[(trial+1)%4];
    c.fromBridge=c.toBridge;
    require(observed.prepare(c)&&untouched.prepare(c),"shelf prepare");
    for(const auto* path:{&c.left,&c.toBridge}){
      require(std::abs(String::transfer(*path,{1,0})-std::complex<double>(1,0))<2.e-14,
              "shelf lost unity DC transmission");
      for(unsigned j=0;j<=128;++j){
        const double angle=3.14159265358979323846*j/128;
        require(std::abs(String::transfer(*path,std::polar(1.,angle)))<=1+1.e-13,
                "shelf transfer is active");
      }
    }
    for(unsigned frame=0;frame<12000;++frame){
      const double f=frame<600?(randomUnit()-.5)*12:0;
      const double bridge=frame<600?(randomUnit()-.5)*.02:0;
      const double oldEnergy=observed.energy(),oldWork=observed.accumulatedWork(),oldLoss=observed.accumulatedLoss();
      const auto p=observed.ports(),again=observed.ports();
      require(p.valid&&p.contactVelocityFree==again.contactVelocityFree&&
              p.bridgeIncomingVelocity==again.bridgeIncomingVelocity&&
              p.contactForceMobility==again.contactForceMobility,"ports changed on repeated read");
      require(observed.energy()==oldEnergy&&observed.accumulatedWork()==oldWork&&
              observed.accumulatedLoss()==oldLoss,"ports changed energy/work ledger");
      const auto a=observed.step(f,bridge),b=untouched.step(f,bridge);
      require(a.valid&&b.valid&&a.contactVelocity==b.contactVelocity&&a.bridgeForce==b.bridgeForce&&
              a.dissipated==b.dissipated&&a.portWork==b.portWork,"ports changed later output");
      const double prediction=std::max(std::abs(a.contactVelocity-(p.contactVelocityFree+p.contactForceMobility*f)),
          std::abs(a.bridgeForce-c.impedance*(bridge-2*p.bridgeIncomingVelocity)));
      maximumPrediction=std::max(maximumPrediction,prediction);
      require(prediction<2.e-14*(1+std::abs(f)),"ports did not predict advanced junction");
      require(a.dissipated>=0,"negative shelf dissipation");
      if(frame%97==0){
        const double residual=std::abs(observed.balanceResidual());maximumResidual=std::max(maximumResidual,residual);
        require(residual<5.e-13*(1+std::abs(observed.accumulatedWork())),"shelf stored energy/work balance");
      }
    }
    allocations=0;track=true;
    for(unsigned frame=0;frame<1000;++frame){(void)observed.ports();(void)observed.step(frame==0?1.:0.);}
    track=false;require(allocations==0,"shelf/ports allocated");
  }
  std::printf("waveguide DC shelf random-port maximum balance residual %.12g J, prediction %.12g\n",
              maximumResidual,maximumPrediction);
}
void shelfStaticCompliance(){
  String preserving,scalar;auto c=integerConfig();c.impedance=2;
  c.left.delaySamples=9;c.toBridge.delaySamples=31;
  c.left.lossGain=c.toBridge.lossGain=.97;
  c.left.dcPreservingLoss=c.toBridge.dcPreservingLoss=true;
  c.left.dcLossPole=c.toBridge.dcLossPole=.99;c.fromBridge=c.toBridge;
  require(preserving.prepare(c),"DC compliance prepare");
  c.left.dcPreservingLoss=c.toBridge.dcPreservingLoss=false;c.fromBridge=c.toBridge;
  require(scalar.prepare(c),"scalar creep positive control prepare");
  double firstDisplacement=0,lastVelocity=0,scalarLastVelocity=0;
  for(unsigned frame=0;frame<150000;++frame){
    const auto a=preserving.step(1),b=scalar.step(1);
    if(frame==119999)firstDisplacement=preserving.contactDisplacement();
    if(frame>=120000){lastVelocity=std::max(lastVelocity,std::abs(a.contactVelocity));scalarLastVelocity+=b.contactVelocity/30000;}
  }
  require(lastVelocity<1.e-8,"DC-preserving path has steady contact mobility");
  require(std::abs(preserving.contactDisplacement()-firstDisplacement)<1.e-9,"DC-preserving displacement creeps");
  require(scalarLastVelocity>1.e-3,"scalar-loss creep positive control failed");
  require(std::abs(preserving.balanceResidual())<1.e-11,"DC storage balance");
  std::printf("waveguide DC compliance max final velocity %.12g m/s, scalar control %.12g m/s\n",lastVelocity,scalarLastVelocity);
}
void shelfTransferConsistency(){
  auto c=integerConfig();c.left.delaySamples=7;c.toBridge.delaySamples=13;
  c.left.allpassCount=c.toBridge.allpassCount=2;
  c.left.allpass[0]=-.4;c.left.allpass[1]=.7;
  c.toBridge.allpass[0]=-.2;c.toBridge.allpass[1]=.3;
  c.left.lossGain=.67;c.toBridge.lossGain=.83;
  c.left.lossMix=.17;c.toBridge.lossMix=.31;
  c.left.dcLossPole=.97;c.toBridge.dcLossPole=.9997;
  c.left.dcPreservingLoss=c.toBridge.dcPreservingLoss=true;c.fromBridge=c.toBridge;
  double maximum=0;
  for(double angle:{.013,.22,1.7}){
    String force,bridge;require(force.prepare(c)&&bridge.prepare(c),"shelf transfer prepare");
    const auto z=std::polar(std::exp(.002),angle),zi=1./z;
    const auto p=String::transfer(c.left,z),q=String::transfer(c.toBridge,z),r=q;
    const auto denominator=1.-p*q*r;
    const std::complex<double> expected[]={
      (1.-p)*(1.-q*r)/(2*c.impedance*denominator),
      -q*(1.-p)/denominator,r*(1.-p)/denominator,
      c.impedance*(1.+p*q*r)/denominator};
    std::complex<double> measured[4]{},weight=1;
    for(unsigned frame=0;frame<16000;++frame){
      const auto a=force.step(frame==0?1.:0.,0),b=bridge.step(0,frame==0?1.:0.);
      measured[0]+=weight*a.contactVelocity;measured[1]+=weight*a.bridgeForce;
      measured[2]+=weight*b.contactVelocity;measured[3]+=weight*b.bridgeForce;weight*=zi;
    }
    for(unsigned i=0;i<4;++i){const double error=std::abs(measured[i]-expected[i])/(1+std::abs(expected[i]));
      maximum=std::max(maximum,error);require(error<1.e-10,"shelf transfer helper disagrees with state recurrence");}
  }
  std::printf("waveguide shelf state/transfer maximum scaled error %.12g\n",maximum);
}
void repetitionAndValidation(){
  String twice,first,second;auto c=integerConfig();
  require(twice.prepare(c)&&first.prepare(c)&&second.prepare(c),"repetition prepare");
  double maximum=0;
  for(unsigned frame=0;frame<1500;++frame){
    const double f1=frame==0?3.:0.,f2=frame==77?-1.:0.;
    const auto a=twice.step(f1+f2),b=first.step(f1),d=second.step(f2);
    maximum=std::max(maximum,std::abs(a.bridgeForce-b.bridgeForce-d.bridgeForce));
    require(std::abs(a.contactVelocity-b.contactVelocity-d.contactVelocity)<1.e-14,"repeat cleared vibration");
  }
  require(maximum<1.e-13,"repeated force did not superpose persistent vibration");
  const double before=twice.energy();
  auto invalid=c;invalid.left.allpassCount=1;invalid.left.allpass[0]=1;
  require(!twice.prepare(invalid)&&twice.energy()==before,"unstable allpass changed state");
  invalid=c;invalid.fromBridge.delaySamples+=1;
  require(!twice.prepare(invalid)&&twice.energy()==before,"nonreciprocal path accepted");
  invalid=c;invalid.left.dcPreservingLoss=true;invalid.left.dcLossPole=1;
  require(!twice.prepare(invalid)&&twice.energy()==before,"nondecaying shelf pole accepted");
  invalid.left.dcLossPole=std::numeric_limits<double>::quiet_NaN();
  require(!twice.prepare(invalid)&&twice.energy()==before,"NaN shelf pole accepted");
  require(!twice.step(std::numeric_limits<double>::quiet_NaN()).valid&&twice.energy()==before,"NaN force changed state");
  allocations=0;track=true;
  for(unsigned i=0;i<10000;++i)(void)twice.step(i==500?1.:0.);
  track=false;require(allocations==0,"step allocated");
}
}
void* operator new(std::size_t bytes){if(track)++allocations;if(void* p=std::malloc(bytes))return p;throw std::bad_alloc();}
void* operator new[](std::size_t bytes){return ::operator new(bytes);}
void operator delete(void* p) noexcept {std::free(p);}
void operator delete[](void* p) noexcept {std::free(p);}
#if __cplusplus >= 201402L
void operator delete(void* p,std::size_t) noexcept {std::free(p);}
void operator delete[](void* p,std::size_t) noexcept {std::free(p);}
#endif
int main(){integerEnergyAndReaction();allpassAndLossLedger();shelfAndReadOnlyPorts();shelfStaticCompliance();shelfTransferConsistency();repetitionAndValidation();
  std::puts("PASS waveguide string: integer scattering, allpass/FIR/shelf ledger, readonly ports, DC compliance, persistence, validation, allocation");}
