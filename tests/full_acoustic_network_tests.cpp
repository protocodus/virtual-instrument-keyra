#include "../tools/full_acoustic_network_support.h"
#include <cstdio>
#include <cstdlib>
#include <limits>
#include <new>
#if defined(KEYRA_ACOUSTIC_RT_WRAP)
#include <cstdarg>
#include <fcntl.h>
#include <pthread.h>
#include <unistd.h>
#endif

namespace {
namespace probe=keyra::full_acoustic_probe;
namespace body=keyra::mechanism_probe;
bool trackRealtime=false;
unsigned allocations=0,locks=0,ioCalls=0;
double maximumBalance=0,maximumReaction=0,maximumPassiveIncrease=0;
double cavityToStrings=0,cavityToSources=0,boardToAir=0,mechanismsToAir=0;
void require(bool value,const char* reason) {
  if (!value) { std::fprintf(stderr,"FAIL full acoustic network: %s\n",reason); std::exit(1); }
}
bool near(double a,double b,double tolerance=2.e-12) {
  return std::abs(a-b)<=tolerance*(1+std::abs(a)+std::abs(b));
}
bool sameMechanicalState(const probe::Piano& a,const probe::Piano& b) {
  for (unsigned i=0;i<a.strike.model.board.size();++i) {
    const auto& x=a.strike.model.board[i]; const auto& y=b.strike.model.board[i];
    if (x.q!=y.q||x.p!=y.p||x.force!=y.force) return false;
  }
  for (unsigned i=0;i<a.strike.model.strings.size();++i) {
    const auto& x=a.strike.model.strings[i].m; const auto& y=b.strike.model.strings[i].m;
    if (x.q!=y.q||x.p!=y.p) return false;
  }
  for (unsigned i=0;i<4;++i)
    if (a.strike.mechanisms[i].energy()!=b.strike.mechanisms[i].energy()||
        a.strike.mechanisms[i].velocity()!=b.strike.mechanisms[i].velocity()) return false;
  for (unsigned i=0;i<88;++i) {
    const auto& x=a.strike.model.keys[i]; const auto& y=b.strike.model.keys[i];
    if (x.hammerX!=y.hammerX||x.hammerV!=y.hammerV||x.hammerActive!=y.hammerActive||x.down!=y.down) return false;
    const auto& u=a.strike.controller.state(i+21); const auto& v=b.strike.controller.state(i+21);
    if (u.launches!=v.launches||u.returnDepth!=v.returnDepth||u.recovery!=v.recovery||u.pending!=v.pending) return false;
  }
  return a.strike.model.pedal==b.strike.model.pedal;
}
bool sameAirState(const probe::Piano& a,const probe::Piano& b) {
  for (unsigned i=0;i<a.config().loadCount;++i)
    if (a.acoustic[i].energy()!=b.acoustic[i].energy()||
        a.acoustic[i].volumeVelocity()!=b.acoustic[i].volumeVelocity()||
        a.acoustic[i].cavityPressure()!=b.acoustic[i].cavityPressure()) return false;
  return true;
}
void record(const probe::Frame& frame) {
  require(frame.valid,"nonfinite full frame");
  maximumBalance=std::max(maximumBalance,frame.junction.maximumBalanceResidual);
  maximumReaction=std::max(maximumReaction,frame.junction.maximumReactionResidual);
  require(frame.junction.maximumBalanceResidual<1.e-12&&frame.junction.maximumReactionResidual<1.e-12,
          "full network junction balance");
}

void sequentialAndObserver() {
  grand::Piano model(body::options()),manual(body::options());
  std::array<keyra::physics::AcousticLoad,probe::maximumLoads> loads,independent;
  for (unsigned i=0;i<2;++i) {
    auto c=loads[i].config(); c.lidPosition=i?.9:.1;
    require(loads[i].prepare(c)&&independent[i].prepare(c),"two load prepare");
    loads[i].applyPressureImpulse(i?.013:.021); independent[i].applyPressureImpulse(i?.013:.021);
  }
  body::bodyImpulse(model,0,.003); body::bodyImpulse(manual,0,.003);
  std::vector<double> originalP,originalForce;
  for (unsigned i=0;i<model.board.size();++i) {
    // Deliberately nonzero bridge force: a correction must preserve it.
    model.board[i].force=manual.board[i].force=.001*(i+1);
    originalP.push_back(model.board[i].p); originalForce.push_back(model.board[i].force);
  }
  const double energyBefore=body::boardEnergy(model);
  const auto result=probe::couple(model,loads,2,0);
  double sumImpulse=0,work=0;
  for (unsigned i=0;i<2;++i) {
    const auto p=body::bodyPort(manual,0);
    const auto s=independent[i].step({p.velocity,p.inverseMass});
    body::bodyImpulse(manual,0,s.boardImpulse);
    require(result.loads[i].boardImpulse==s.boardImpulse,"adapter diverges from explicit sequential junction");
    require(result.ports[i].velocity==p.velocity,"load read stale board velocity");
    sumImpulse+=s.boardImpulse; work+=s.boardWork;
  }
  require(result.appliedImpulses==2&&result.valid,"two loads did not both react");
  require(near(result.ports[1].velocity,result.ports[0].velocity+
    result.ports[0].inverseMass*result.loads[0].boardImpulse,1.e-15),"second load missed first reaction");
  require(std::abs(result.ports[1].velocity-result.ports[0].velocity)>1.e-12,"stale velocity fixture too weak");
  require(near(body::boardEnergy(model)-energyBefore,work,1.e-15),"board impulse applied other than exactly once");
  std::array<double,2> expectedCorrection{};
  for (unsigned i=0;i<model.board.size();++i) {
    const auto& z=model.board[i];
    require(z.p==manual.board[i].p&&z.force==originalForce[i],"reaction changed original bridge force or state");
    const double delta=-2*z.sigma*z.w*(z.p-originalP[i])+z.port[0]*sumImpulse/model.dt;
    for (unsigned ch=0;ch<2;++ch) expectedCorrection[ch]+=delta*z.mic[ch];
  }
  for (unsigned ch=0;ch<2;++ch)
    require(near(result.pressureProxyCorrection[ch],expectedCorrection[ch],2.e-11),
            "observer missed or doubled external J/dt");
  require(result.maximumReactionResidual<1.e-15&&result.maximumBalanceResidual<1.e-14,"sequential work mismatch");
}

void passiveFullTransfer() {
  probe::Config config; config.loadCount=2; config.acoustic[1].lidPosition=.2;
  probe::Piano piano(config); body::openDampers(piano.strike.model);
  const double supplied=piano.applyPressureImpulse(0,.03)+piano.applyPressureImpulse(1,-.01);
  double previous=supplied;
  for (unsigned frame=0;frame<4800;++frame) {
    record(piano.step(frame));
    if ((frame&31u)==0) {
      const double total=piano.energy();
      maximumPassiveIncrease=std::max(maximumPassiveIncrease,total-previous);
      require(total<=previous+1.e-12,"unforced connected air/body/string network created energy");
      previous=total;
      cavityToStrings=std::max(cavityToStrings,body::stringEnergy(piano.strike.model));
      for (const auto& source:piano.strike.mechanisms) cavityToSources=std::max(cavityToSources,source.energy());
    }
  }
  require(cavityToStrings>1.e-14&&cavityToSources>1.e-14,"cavity reaction did not reach unstruck strings and sources");
  require(piano.strike.ledger.launches==0,"reverse path secretly launched hammer");

  probe::Piano boardDriven;
  body::bodyImpulse(boardDriven.strike.model,0,.003);
  probe::Piano mechanismDriven;
  mechanismDriven.strike.mechanisms[1].trigger(.7); mechanismDriven.strike.mechanisms[3].trigger(.6);
  for (unsigned frame=0;frame<2400;++frame) {
    record(boardDriven.step(frame)); record(mechanismDriven.step(frame));
    boardToAir=std::max(boardToAir,boardDriven.acousticEnergy());
    mechanismsToAir=std::max(mechanismsToAir,mechanismDriven.acousticEnergy());
  }
  require(boardToAir>1.e-14&&mechanismsToAir>1.e-14,"board/mechanism did not drive cavity");
}

void events(probe::Piano& piano,unsigned frame) {
  if (frame==0) piano.noteOn(60,75);
  if (frame==800) piano.sustain(1);
  if (frame==1200) piano.noteOff(60);
  if (frame==1800) piano.noteOn(60,75);
  if (frame==2400) piano.noteOff(60);
  if (frame==3000) { piano.noteOn(48,60); piano.noteOn(67,80); }
  if (frame==3600) { piano.noteOff(48); piano.noteOff(67); piano.sustain(0); }
}

void ablationsAndPartition() {
  probe::Config config; config.airEnabled=false;
  probe::Piano off(config);
  keyra::strike_probe::Piano exact;
  exact.enableMechanisms(true);
  off.noteOn(60,75); exact.noteOn(60,75);
  for (unsigned frame=0;frame<1000;++frame)
    require(off.step(frame).combined==exact.step(frame),"air-off changed preserved strike/mechanism baseline");

  config=probe::Config{}; config.airCoupling=false;
  probe::Piano disconnected(config); disconnected.applyPressureImpulse(0,.03);
  for (unsigned frame=0;frame<600;++frame) {
    const auto result=disconnected.step(frame);
    require(result.combined[0]==0&&result.combined[1]==0&&result.junction.appliedImpulses==0,
            "uncoupled unobserved air reached mechanical network");
  }
  require(body::stringEnergy(disconnected.strike.model)==0,"coupling ablation reached unstruck strings");
  require(disconnected.acousticEnergy()>0,"coupling ablation removed acoustic source state");

  probe::Piano observed,muted,partitioned,different([]{probe::Config c; c.seed=12345; return c;}());
  observed.setDirectAirGain(.2);
  constexpr unsigned frames=4096;
  std::vector<std::array<double,2>> expected(frames);
  bool observedDifference=false,seedDifference=false;
  // All objects and buffers are prepared. Include actual MIDI/partial-restrike
  // event handling in the instrumented callback region, not only quiet steps.
  trackRealtime=true;
  for (unsigned frame=0;frame<frames;++frame) {
    events(observed,frame); events(muted,frame); events(different,frame);
    const auto a=observed.step(frame),b=muted.step(frame),c=different.step(frame);
    record(a); record(b); record(c); expected[frame]=b.combined;
    observedDifference=observedDifference||a.combined!=b.combined;
    seedDifference=seedDifference||c.combined!=b.combined;
  }
  unsigned position=0,blockIndex=0;
  constexpr std::array<unsigned,7> blocks{{1,17,64,3,128,11,257}};
  while (position<frames) {
    const unsigned end=std::min(frames,position+blocks[blockIndex++%blocks.size()]);
    for (;position<end;++position) {
      events(partitioned,position);
      require(partitioned.step(position).combined==expected[position],"block partition changed absolute-frame evolution");
    }
  }
  trackRealtime=false;
  require(observedDifference&&seedDifference,"observation/seed control had no effect");
  require(sameMechanicalState(observed,muted)&&sameAirState(observed,muted),"observation-only gain changed physical state");
  require(sameMechanicalState(partitioned,muted)&&sameAirState(partitioned,muted),"partition changed internal state");
  require(allocations==0&&locks==0&&ioCalls==0,"prepared frame/event path allocated, locked or performed I/O");
  require(muted.acousticEnergy()>0,"source-off cavity failed to receive struck-piano energy");
  require(!muted.setDirectAirGain(std::numeric_limits<double>::infinity()),"invalid observation gain accepted");
}

void finiteGeometryAndValidation() {
  for (int rate:{44100,48000,96000}) {
    probe::Config c; c.sampleRate=rate; c.acoustic[0].lidPosition=rate==44100?0:rate==48000?.5:1;
    c.acoustic[0].player.presence=1; c.acoustic[0].player.distanceM=rate==44100?0:rate==48000?.6:3;
    probe::Piano piano(c); piano.noteOn(21,100); piano.noteOn(108,100);
    for (unsigned frame=0;frame<1200;++frame) record(piano.step(frame));
    const double mechanical=piano.strike.model.energy();
    auto geometry=piano.acoustic[0].config(); geometry.lidPosition=.3;
    require(piano.acoustic[0].prepare(geometry)&&piano.acousticEnergy()==0&&
            piano.strike.model.energy()==mechanical,"outside-process geometry reset altered mechanical state");
  }
  for (unsigned badCase=0;badCase<4;++badCase) {
    probe::Config c;
    if (badCase==0) c.sampleRate=0;
    if (badCase==1) c.loadCount=3;
    if (badCase==2) c.boardGroup=3;
    if (badCase==3) c.acoustic[0].cavityVolumeM3=-1;
    bool rejected=false;
    try { probe::Piano invalid(c); } catch (const std::exception&) { rejected=true; }
    require(rejected,"invalid adapter setup accepted");
  }
}

void auditHooks() {
  // Positive controls keep zero counts from being a vacuous audit. These
  // deliberate calls are outside any piano process/event callback.
  trackRealtime=true;
  void* p=::operator new(7);
  ::operator delete(p);
#if defined(KEYRA_ACOUSTIC_RT_WRAP)
  pthread_mutex_t mutex=PTHREAD_MUTEX_INITIALIZER;
  pthread_mutex_lock(&mutex); pthread_mutex_unlock(&mutex);
  (void)::write(-1,"x",1);
#endif
  trackRealtime=false;
  require(allocations==1,"allocation hook positive control failed");
#if defined(KEYRA_ACOUSTIC_RT_WRAP)
  require(locks==2&&ioCalls==1,"lock/I/O hook positive controls failed");
#endif
  allocations=locks=ioCalls=0;
}
}

void* operator new(std::size_t size) {
  if (trackRealtime) ++allocations;
  if (void* p=std::malloc(size?size:1)) return p;
  std::abort();
}
void* operator new[](std::size_t size) { return ::operator new(size); }
void operator delete(void* p) noexcept { std::free(p); }
void operator delete[](void* p) noexcept { std::free(p); }
void operator delete(void* p,std::size_t) noexcept { std::free(p); }
void operator delete[](void* p,std::size_t) noexcept { std::free(p); }

// GNU/ELF linker wrappers audit calls from the compiled callback translation
// units. This is a focused process-path check, not a whole SDK/host guarantee.
#if defined(KEYRA_ACOUSTIC_RT_WRAP)
extern "C" {
int __real_pthread_mutex_lock(pthread_mutex_t*);
int __real_pthread_mutex_unlock(pthread_mutex_t*);
ssize_t __real_read(int,void*,size_t);
ssize_t __real_write(int,const void*,size_t);
int __real_open(const char*,int,...);
FILE* __real_fopen(const char*,const char*);
size_t __real_fread(void*,size_t,size_t,FILE*);
size_t __real_fwrite(const void*,size_t,size_t,FILE*);
int __wrap_pthread_mutex_lock(pthread_mutex_t* p) { if(trackRealtime)++locks; return __real_pthread_mutex_lock(p); }
int __wrap_pthread_mutex_unlock(pthread_mutex_t* p) { if(trackRealtime)++locks; return __real_pthread_mutex_unlock(p); }
ssize_t __wrap_read(int fd,void* p,size_t n) { if(trackRealtime)++ioCalls; return __real_read(fd,p,n); }
ssize_t __wrap_write(int fd,const void* p,size_t n) { if(trackRealtime)++ioCalls; return __real_write(fd,p,n); }
int __wrap_open(const char* p,int flags,...) {
  if(trackRealtime)++ioCalls;
  if(flags&O_CREAT) { va_list args; va_start(args,flags); const int mode=va_arg(args,int); va_end(args); return __real_open(p,flags,mode); }
  return __real_open(p,flags);
}
FILE* __wrap_fopen(const char* p,const char* mode) { if(trackRealtime)++ioCalls; return __real_fopen(p,mode); }
size_t __wrap_fread(void* p,size_t a,size_t b,FILE* f) { if(trackRealtime)++ioCalls; return __real_fread(p,a,b,f); }
size_t __wrap_fwrite(const void* p,size_t a,size_t b,FILE* f) { if(trackRealtime)++ioCalls; return __real_fwrite(p,a,b,f); }
}
#endif

int main() {
  auditHooks();
  sequentialAndObserver(); passiveFullTransfer(); ablationsAndPartition(); finiteGeometryAndValidation();
  std::printf("{\"schema_version\":1,\"passed\":true,\"maximum_acoustic_balance_residual_j\":%.17g,"
    "\"maximum_actual_reaction_work_residual_j\":%.17g,\"maximum_unforced_energy_increase_j\":%.17g,"
    "\"cavity_to_unstruck_strings_maximum_j\":%.17g,\"cavity_to_mechanisms_maximum_j\":%.17g,"
    "\"board_to_cavity_maximum_j\":%.17g,\"mechanisms_to_cavity_maximum_j\":%.17g,"
    "\"callback_allocations\":%u,\"wrapped_callback_mutex_calls\":%u,\"wrapped_callback_io_calls\":%u,"
    "\"wrapped_io_and_locks_enabled\":%s,\"scope\":\"Full original solver plus action, mechanisms and reciprocal air research adapter; no host or SDK claim.\"}\n",
    maximumBalance,maximumReaction,maximumPassiveIncrease,cavityToStrings,cavityToSources,boardToAir,mechanismsToAir,
    allocations,locks,ioCalls,
#if defined(KEYRA_ACOUSTIC_RT_WRAP)
    "true"
#else
    "false"
#endif
  );
}
