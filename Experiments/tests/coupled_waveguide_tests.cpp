#include "../tools/coupled_waveguide_support.h"
#include <cstdio>
#include <cstdlib>
#include <limits>
#include <new>

namespace {
using Network=keyra::physics::CoupledWaveguide;
#ifdef KEYRA_WAVEGUIDE_TEST_PROFILE_DIR
std::string profileDirectory=KEYRA_WAVEGUIDE_TEST_PROFILE_DIR;
#else
std::string profileDirectory;
#endif
bool track=false;
unsigned allocations=0;
void require(bool value,const char* message) {
  if(!value){std::fprintf(stderr,"FAIL coupled waveguide: %s\n",message);std::exit(1);}
}
std::string profile(int note) {
  return profileDirectory+(note==36?"/C2-s32.cfg":"/C4-s32.cfg");
}
Network::Config config(int note,bool loss) {
  return keyra::waveguide_probe::pianoConfig(note,profile(note),loss,true);
}
void coupledBalance() {
  for(int note:{36,60})for(bool loss:{false,true}) {
    Network network;require(network.prepare(config(note,loss)),"prepare full board");
    require(network.noteOn(.7),"initial strike request");
    double maxBalance=0,maxEnergy=0,minimumLoss=0,tailReference=0,maximumUnforcedGrowth=0;
    for(unsigned i=0;i<48000;++i) {
      const auto frame=network.step();require(frame.valid,"finite step");
      require(std::isfinite(frame.pressure[0])&&std::isfinite(frame.pressure[1]),"finite observer");
      minimumLoss=std::min(minimumLoss,frame.pathLoss+frame.boardLoss+frame.contactLoss);
      if(i%64==0) {
        const double e=network.energy();maxEnergy=std::max(maxEnergy,e);
        maxBalance=std::max(maxBalance,std::abs(network.balanceResidual()));
        if(i>4000)maximumUnforcedGrowth=std::max(maximumUnforcedGrowth,e-tailReference);
        tailReference=e;
      }
    }
    const auto& l=network.ledger();
    const double tolerance=2.e-10*(1+l.launchWork);
    require(l.contactFaults==0&&l.bridgeFaults==0,"solver fault");
    require(l.launches==1,"one admitted launch");
    require(l.maximumInteractionResidual<tolerance,"contact/bridge work cancellation");
    require(maxBalance<tolerance,"global energy ledger");
    require(minimumLoss>=-1.e-16,"negative passive loss");
    require(maxEnergy<=l.launchWork+tolerance,"unforced energy exceeds input");
    require(maximumUnforcedGrowth<tolerance,"unforced energy grows after release");
    std::printf("balance note %d loss %d max_global %.12g max_step %.12g launch %.12g final %.12g growth %.12g\n",
      note,int(loss),maxBalance,l.maximumInteractionResidual,l.launchWork,network.energy(),maximumUnforcedGrowth);
  }
}
void externalPortsAndObservation() {
  auto c=config(60,true);Network observed,muted,uncoupled;
  require(observed.prepare(c),"observed prepare");c.observation=false;
  require(muted.prepare(c),"muted prepare");c.coupling=false;
  require(uncoupled.prepare(c),"uncoupled prepare");
  double maxBalance=0,maxBoard=0,maxString=0,maxOffString=0;
  for(unsigned i=0;i<12000;++i) {
    Network::Input input;
    if(i<100){input.boardForce={{.01,-.004,.003}};}
    const auto a=observed.step(input),b=muted.step(input),d=uncoupled.step(input);
    require(a.valid&&b.valid&&d.valid,"external board port");
    require(b.pressure[0]==0&&b.pressure[1]==0,"observer isolation");
    require(observed.energy()==muted.energy()&&observed.contactDisplacement()==muted.contactDisplacement(),"observer changed mechanics");
    if(i%64==0){maxBalance=std::max(maxBalance,std::abs(observed.balanceResidual()));
      maxBoard=std::max(maxBoard,observed.boardEnergy());maxString=std::max(maxString,observed.stringEnergy());
      maxOffString=std::max(maxOffString,uncoupled.stringEnergy());}
  }
  require(maxBalance<1.e-15,"external-force work ledger");
  require(maxBoard>0&&maxString>0,"board failed to drive strings reciprocally");
  require(maxOffString==0,"coupling switch leaked force into strings");
  std::printf("external board excitation max_balance %.12g board %.12g string %.12g isolated_string %.12g\n",maxBalance,maxBoard,maxString,maxOffString);
}
void persistentRepetition() {
  Network repeated,single;
  auto c=config(60,true);c.humanization=.65;c.seed=123456;
  require(repeated.prepare(c)&&single.prepare(c),"repeat prepare");
  require(repeated.noteOn(.7)&&single.noteOn(.7),"first requests");
  double energyBefore=0,energyAfter=0;
  for(unsigned i=0;i<24000;++i) {
    // A touching off/on pair requires finite key lift. It must not reset a
    // contacting hammer or discard existing rails/filter/board state.
    if(i==4800||i==9600) {
      repeated.noteOff();energyBefore=repeated.stringEnergy()+repeated.boardEnergy();
      require(repeated.noteOn(.7),"touching repeat request");
      energyAfter=repeated.stringEnergy()+repeated.boardEnergy();
      require(energyBefore==energyAfter&&energyBefore>0,"note event reset resonating state");
    }
    const auto a=repeated.step(),b=single.step();require(a.valid&&b.valid,"repeat step");
    if(i==4800)require(repeated.ledger().launches==1,"zero-gap repeat bypassed finite lift");
  }
  require(repeated.ledger().launches==3,"touching repetitions not admitted");
  require(repeated.ledger().contactFaults==0,"repeat contact fault");
  require(std::abs(repeated.balanceResidual())<1.e-9,"repeat energy ledger");
  require(repeated.energy()!=single.energy(),"additional strikes had no impact");
  require(repeated.strikeState().pendingVelocityFactor!=1&&repeated.strikeState().pendingHardnessFactor!=1,
    "humanization did not reach excitation");
  std::printf("persistent repetition launches %llu partial %llu last_string_energy %.12g global_residual %.12g\n",
    (unsigned long long)repeated.ledger().launches,(unsigned long long)repeated.ledger().partialLaunches,energyAfter,repeated.balanceResidual());
}
void validationAndRealtime() {
  Network n;auto c=config(60,true);require(n.prepare(c),"validation prepare");
  auto invalid=c;invalid.board[0].sigma=-1;
  require(!n.prepare(invalid)&&n.prepared(),"invalid prepare changed valid instance");
  require(n.noteOn(.7),"runtime request");
  for(unsigned i=0;i<100;++i)require(n.step().valid,"runtime warmup");
  const double e=n.energy();Network::Input input;input.stringForce[0]=std::numeric_limits<double>::quiet_NaN();
  require(!n.step(input).valid&&n.energy()==e,"invalid input changed state");
  allocations=0;track=true;
  for(unsigned i=0;i<10000;++i) {
    if(i==2000){n.noteOff();(void)n.noteOn(.7);}
    (void)n.step();
  }
  track=false;require(allocations==0,"runtime allocated");
  n.reset();require(n.energy()==0&&n.ledger().launches==0,"reset did not clear state");
}
void passiveDamperAndPedal() {
  for(int note:{36,60}) {
    std::array<double,3> finalEnergy{},tailIntegral{},damperLoss{};
    for(unsigned level=0;level<3;++level) {
      auto c=config(note,true);c.damperEnabled=true;Network n;require(n.prepare(c),"damper prepare");
      const double pedal=.5*level;require(n.setPedal(pedal)&&n.noteOn(.7),"pedal strike");
      double maximumBalance=0,maximumSolve=0,previousEnergy=n.energy();
      for(unsigned i=0;i<48000;++i) {
        if(i==4800) {
          const double before=n.energy();n.noteOff();
          require(n.energy()==before,"key release erased energy");
          require(n.damperTargetClosure()==1-pedal,"pedal sign convention");
        }
        const auto frame=n.step();require(frame.valid,"damper finite step");
        require(frame.damperLoss>=0,"damper returned energy");
        require(n.damperClosure()>=0&&n.damperClosure()<=1,"unbounded damper control");
        maximumSolve=std::max(maximumSolve,frame.damperSolveResidual);
        for(unsigned s=0;s<c.stringCount;++s) {
          require(frame.damperResistance[s]>=0,"negative damper resistance");
          require(frame.damperForce[s]*frame.contactVelocity[s]<=1.e-14,"active damper force");
        }
        if(i%64==0) {
          const double e=n.energy();maximumBalance=std::max(maximumBalance,std::abs(n.balanceResidual()));
          require(e<=previousEnergy+1.e-12,"variable damper increased unforced energy");previousEnergy=e;
          if(i>=9600)tailIntegral[level]+=e*64*Network::h;
        }
      }
      finalEnergy[level]=n.energy();damperLoss[level]=n.ledger().damperLoss;
      require(maximumBalance<1.e-10,"damper global work ledger");
      require(maximumSolve<1.e-12,"damper implicit port solve");
      require(n.ledger().contactFaults==0&&n.ledger().bridgeFaults==0,"damper solver fault");
      std::printf("damper note %d pedal %.1f tail_integral %.12g final %.12g loss %.12g max_balance %.12g solve %.12g\n",
        note,pedal,tailIntegral[level],finalEnergy[level],damperLoss[level],maximumBalance,maximumSolve);
    }
    require(tailIntegral[0]<tailIntegral[1]&&tailIntegral[1]<tailIntegral[2],"half pedal did not interpolate tail loss");
    require(finalEnergy[0]<finalEnergy[1]&&finalEnergy[1]<finalEnergy[2],"pedal did not hold strings");
    require(damperLoss[0]>damperLoss[1]&&damperLoss[1]>damperLoss[2],"pedal did not change dissipated work");
  }
}
void damperControlsAndRepetition() {
  auto c=config(60,true);c.damperEnabled=true;Network n;require(n.prepare(c)&&n.noteOn(.7),"dynamic damper prepare");
  double maximumBalance=0;unsigned event=0;
  for(unsigned i=0;i<24000;++i) {
    if(i==960||i==4800||i==6720) {
      const double e=n.energy();n.noteOff();require(n.energy()==e,"damper release reset state");
    }
    if(i==1440||i==5280) {
      const double e=n.stringEnergy()+n.boardEnergy();require(n.noteOn(.7),"damper restrike request");
      require(n.stringEnergy()+n.boardEnergy()==e&&e>0,"damper restrike erased vibration");
    }
    if(i==7200||i==9600||i==12000||i==14400) {
      const double e=n.energy(),loss=n.ledger().damperLoss;
      const double pedals[]={1,.5,0,.75};require(n.setPedal(pedals[event++]),"dynamic pedal");
      require(n.energy()==e&&n.ledger().damperLoss==loss,"pedal event reset energy or ledger");
    }
    if(i==10000||i==13000) {
      const double e=n.energy(),loss=n.ledger().damperLoss;
      n.setDamperEnabled(i==13000);
      require(n.energy()==e&&n.ledger().damperLoss==loss,"bypass reset energy or ledger");
    }
    const auto frame=n.step();require(frame.valid&&frame.damperLoss>=0,"dynamic damper step");
    if(i%64==0)maximumBalance=std::max(maximumBalance,std::abs(n.balanceResidual()));
  }
  require(n.ledger().launches==3&&n.ledger().partialLaunches>=1,"damper broke safe partial restrikes");
  require(maximumBalance<1.e-10,"dynamic damper work ledger");
  const double e=n.energy(),pedal=n.pedal();
  require(!n.setPedal(std::numeric_limits<double>::quiet_NaN())&&n.pedal()==pedal&&n.energy()==e,"NaN pedal changed state");
  std::printf("dynamic damper launches %llu partial %llu loss %.12g max_balance %.12g\n",
    (unsigned long long)n.ledger().launches,(unsigned long long)n.ledger().partialLaunches,n.ledger().damperLoss,maximumBalance);

  Network legacy,zero;auto d=config(60,true);require(legacy.prepare(d),"legacy load bypass");
  d.damperEnabled=true;d.damperStrength=0;require(zero.prepare(d),"zero load prepare");
  require(legacy.noteOn(.7)&&zero.noteOn(.7),"zero load strike");
  for(unsigned i=0;i<12000;++i) {
    if(i==2400){legacy.noteOff();zero.noteOff();}
    if(i==4800){(void)legacy.setPedal(1);(void)zero.setPedal(1);}
    const auto a=legacy.step(),b=zero.step();
    require(a.valid&&b.valid&&a.pressure==b.pressure&&legacy.energy()==zero.energy(),"zero load changed old mechanical output");
    require(b.damperLoss==0,"zero resistance dissipated energy");
  }
  allocations=0;track=true;
  for(unsigned i=0;i<10000;++i){if(i%1000==0)(void)n.setPedal(double(i%3000)/3000);(void)n.step();}
  track=false;require(allocations==0,"damper control allocated");
}
void damperExternalWork() {
  auto c=config(60,true);c.damperEnabled=true;Network n;require(n.prepare(c),"damper external prepare");
  double maximumBalance=0,maximumForceWorkResidual=0;unsigned control=0;
  for(unsigned i=0;i<20000;++i) {
    if(i%2000==0){const double p[]={0,.5,1,.25,.75};require(n.setPedal(p[control++%5]),"external pedal control");}
    Network::Input input;
    if(i<1000) {
      input.stringForce={{.1*std::sin(.013*i),-.05*std::cos(.021*i),.03*std::sin(.033*i)}};
      input.boardForce={{.001*std::sin(.017*i),.002*std::cos(.011*i),0}};
    }
    const auto frame=n.step(input);require(frame.valid&&frame.damperLoss>=0,"external damper frame");
    double forceWork=0;for(unsigned s=0;s<c.stringCount;++s)forceWork-=Network::h*frame.damperForce[s]*frame.contactVelocity[s];
    maximumForceWorkResidual=std::max(maximumForceWorkResidual,std::abs(forceWork-frame.damperLoss));
    if(i%64==0)maximumBalance=std::max(maximumBalance,std::abs(n.balanceResidual()));
  }
  require(maximumBalance<1.e-13&&maximumForceWorkResidual<1.e-16,"external damper work did not balance");
  require(n.ledger().damperLoss>0&&n.ledger().launches==0,"external damper source isolation");
  std::printf("damper external force max_balance %.12g max_force_work_residual %.12g damper_loss %.12g\n",
    maximumBalance,maximumForceWorkResidual,n.ledger().damperLoss);
}
}
void* operator new(std::size_t n){if(track)++allocations;if(void* p=std::malloc(n))return p;throw std::bad_alloc();}
void* operator new[](std::size_t n){return ::operator new(n);}
void operator delete(void* p) noexcept {std::free(p);}
void operator delete[](void* p) noexcept {std::free(p);}
void operator delete(void* p,std::size_t) noexcept {std::free(p);}
void operator delete[](void* p,std::size_t) noexcept {std::free(p);}
int main(int argc,char** argv){
  if(argc==2)profileDirectory=argv[1];
  if(profileDirectory.empty()){std::fprintf(stderr,"Supply the tests/data/coupled-waveguide profile directory as argv[1] or compile KEYRA_WAVEGUIDE_TEST_PROFILE_DIR\n");return 1;}
  coupledBalance();externalPortsAndObservation();persistentRepetition();validationAndRealtime();
  passiveDamperAndPedal();damperControlsAndRepetition();damperExternalWork();
  std::puts("PASS coupled waveguide: original full board, passive contact/damper, reciprocal ports, persistent repetition, pedal/isolation, allocation");}
