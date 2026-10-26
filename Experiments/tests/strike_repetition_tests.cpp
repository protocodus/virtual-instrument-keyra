#include "../tools/strike_repetition_support.h"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <new>

namespace {
namespace probe=keyra::strike_probe;
using keyra::physics::StrikeController;
using keyra::physics::StrikeConfig;
bool trackAllocation=false;
unsigned allocations=0;
void require(bool value,const char* reason) {
  if (!value) { std::fprintf(stderr,"FAIL strike repetition: %s\n",reason); std::exit(1); }
}
std::vector<double> stringState(const grand::Piano& model) {
  std::vector<double> state;
  for (const auto& string:model.strings) {
    state.insert(state.end(),string.m.q.begin(),string.m.q.end());
    state.insert(state.end(),string.m.p.begin(),string.m.p.end());
  }
  return state;
}
void advance(probe::Piano& piano,uint64_t& frame,unsigned count) {
  for (unsigned i=0;i<count;++i) {
    const auto x=piano.step(frame++);
    require(std::isfinite(x[0])&&std::isfinite(x[1]),"nonfinite full output");
  }
}

void independentVariationAndBounds() {
  bool rejected=false;
  try { probe::Piano invalid(0); } catch (const std::exception&) { rejected=true; }
  require(rejected,"invalid full-model sample rate reached construction");
  StrikeController a,b;
  StrikeConfig c; c.seed=123456; c.variation=1;
  require(a.prepare(c)&&b.prepare(c),"controller prepare");
  double previousVelocity=0,previousHardness=0;
  for (unsigned press=0;press<32;++press) {
    require(a.request(60,.7)&&b.request(60,.7),"request");
    const auto x=a.poll(60,{false,-.012,0},false),y=b.poll(60,{false,-.012,0},false);
    require(x.valid&&y.valid,"ready independent launch");
    require(x.velocityFactor==y.velocityFactor&&x.hardnessFactor==y.hardnessFactor,
            "same seed/input is not reproducible");
    require(std::abs(x.velocityFactor-1)<=c.velocityVariation&&
            std::abs(x.hardnessFactor-1)<=c.hardnessVariation,"variation exceeds configured bound");
    if (press) require(x.velocityFactor!=previousVelocity||x.hardnessFactor!=previousHardness,
                       "successive ready excitation repeated exactly");
    previousVelocity=x.velocityFactor; previousHardness=x.hardnessFactor;
    a.release(60); b.release(60);
    for (unsigned i=0;i<8000;++i) {
      (void)a.poll(60,{false,-.012,0}); (void)b.poll(60,{false,-.012,0});
    }
  }
  StrikeController isolated;
  require(isolated.prepare(c),"isolated seed prepare");
  require(isolated.request(60,.7),"isolated request");
  const auto first=isolated.poll(60,{false,-.012,0},false);
  StrikeController differentOrder;
  require(differentOrder.prepare(c),"independent key prepare");
  differentOrder.request(48,.4); differentOrder.poll(48,{false,0,0},false);
  differentOrder.request(60,.7);
  const auto same=differentOrder.poll(60,{false,-.012,0},false);
  require(first.velocityFactor==same.velocityFactor&&first.hardnessFactor==same.hardnessFactor,
          "another key perturbed per-key variation sequence");
  const auto before=a.state(60).requests;
  require(!a.request(10,.5)&&!a.request(60,std::numeric_limits<double>::quiet_NaN()),"invalid request accepted");
  c.sampleRate=0;
  require(!a.prepare(c)&&a.state(60).requests==before,"invalid setup changed state");
}

void queuedAndPartialRecovery() {
  StrikeController c; StrikeConfig config; config.variation=0;
  require(c.prepare(config),"zero variation prepare");
  c.request(60,.8);
  require(!c.poll(60,{false,.0001,0},false).valid,"initial controller bypassed existing compression");
  auto launch=c.poll(60,{false,0,0},false);
  require(launch.valid&&launch.velocityFactor==1&&launch.hardnessFactor==1,"zero variation control");
  c.request(60,.5); c.request(60,.7);
  require(!c.poll(60,{true,.0003,1},false).valid,"launched in contact/inbound");
  require(c.statistics().coalesced==1&&c.statistics().deferred==2,"pending diagnostics wrong");
  c.release(60);
  require(!c.state(60).pending&&c.statistics().cancelled==1,"release did not cancel pending strike");
  for (unsigned i=0;i<250;++i) (void)c.poll(60,{true,-.002,-1});
  for (unsigned i=0;i<80;++i) (void)c.poll(60,{false,-.002,0});
  c.request(60,.8);
  const auto partial=c.poll(60,{false,-.002,0},false);
  require(partial.valid&&partial.preserveSeparatedPosition&&partial.recoveryVelocityFactor<.99,
          "partial return was treated as fresh hammer");
  c.release(60);
  for (unsigned i=0;i<5000;++i) (void)c.poll(60,{false,-.012,0});
  c.request(60,.8);
  const auto full=c.poll(60,{false,-.012,0},false);
  require(full.valid&&!full.preserveSeparatedPosition&&
          full.recoveryVelocityFactor>partial.recoveryVelocityFactor,"full recovery does not restore strike");

  // Timeout is bounded even when a pathological observation never separates.
  c.request(60,.8);
  for (unsigned i=0;i<7000;++i) (void)c.poll(60,{true,.0001,.1});
  require(!c.state(60).pending&&c.statistics().expired==1,"pending slot never expired");
  c.request(60,.8);
  require(!c.request(60,0)&&!c.state(60).pending&&!c.state(60).down,
          "zero-velocity note-on did not act as release");

  StrikeController retired; retired.request(60,.8);
  require(retired.poll(60,{false,0,0},false).valid,"retirement fixture initial launch");
  retired.release(60);
  (void)retired.poll(60,{true,.0002,.1});
  (void)retired.poll(60,{false,.0002,.1});
  require(retired.statistics().retiredBeforeSeparation==1&&retired.state(60).returnDepth<0,
          "timeout return proxy teleported from compression");
  for (unsigned i=0;i<9000;++i) (void)retired.poll(60,{false,-retired.state(60).returnDepth,0});
  require(retired.state(60).recovery==1&&retired.state(60).returnVelocity==0,
          "retired near-string hammer never recovered or stopped");
  retired.request(60,.8);
  require(retired.poll(60,{false,-.012,0},false).valid,"retired key remained permanently unready");
}

void finiteLiftRepetition() {
  // Touching MIDI notes are common after quantization. A short explicit off
  // must defer the next press for a real lift, rather than freeze its initial
  // lift forever while the newly requested down-state drives it toward zero.
  for (unsigned gap:{0u,1u,48u,240u}) {
    StrikeController c; StrikeConfig config; config.variation=0;
    require(c.prepare(config)&&c.request(60,.7),"touching-note setup");
    require(c.poll(60,{false,-.012,0},false).valid,"touching first launch");
    std::array<unsigned,3> launches{{0,0,0}}; unsigned count=1;
    const auto record=[&](const keyra::physics::StrikeLaunch& launch,unsigned frame) {
      if (!launch.valid) return;
      require(count<launches.size(),"touching notes created an extra launch");
      require(launch.keyLift>=config.minimumKeyLift&&
              launch.recoveryVelocityFactor<1,"touching repeat bypassed partial action");
      launches[count++]=frame;
    };
    for (unsigned frame=1;frame<11000;++frame) {
      if (gap&&(frame==4800-gap||frame==9600-gap)) c.release(60);
      if (frame==4800||frame==9600) {
        if (!gap) c.release(60);
        require(c.request(60,.7),"touching repeat request rejected");
        const auto event=c.poll(60,{false,-.012,0},false);
        if (gap<193) require(!event.valid,"short release skipped finite lift");
        record(event,frame);
      }
      record(c.poll(60,{false,-.012,0}),frame);
    }
    require(count==3&&c.statistics().launches==3&&
            c.statistics().cancelled==0&&c.statistics().expired==0,
            "touching notes did not all rearm");
    for (unsigned i=1;i<launches.size();++i) {
      const unsigned requested=4800*i;
      require(launches[i]>=requested&&launches[i]<=requested+241,
              "touching-note finite lift exceeded five milliseconds");
      if (!gap) require(launches[i]>=requested+190,
                         "zero-gap repeat received an instantaneous lift");
      if (gap==240) require(launches[i]==requested,
                            "sufficient explicit lift gained a new delay");
    }
  }

  const auto preparePending=[](StrikeController& c) {
    c.request(60,.7);
    require(c.poll(60,{false,-.012,0},false).valid,"lift policy initial launch");
    for (unsigned i=0;i<4800;++i) (void)c.poll(60,{false,-.012,0});
    c.release(60); c.request(60,.6);
    require(!c.poll(60,{false,-.012,0},false).valid,"lift policy initially bypassed gate");
  };
  StrikeController cancelled; preparePending(cancelled);
  for (unsigned i=0;i<48;++i)
    require(!cancelled.poll(60,{false,-.012,0}).valid,"short lift admitted early");
  require(cancelled.state(60).pending&&cancelled.state(60).pendingLift<.2,
          "cancellation fixture missed pending lift");
  cancelled.release(60);
  for (unsigned i=0;i<7000;++i)
    require(!cancelled.poll(60,{false,-.012,0}).valid,"cancelled lift made a ghost launch");
  require(cancelled.statistics().launches==1&&cancelled.statistics().cancelled==1,
          "cancellation during lift was not retained");

  StrikeController coalesced; preparePending(coalesced);
  for (unsigned i=0;i<40;++i) (void)coalesced.poll(60,{false,-.012,0});
  coalesced.request(60,.8);coalesced.request(60,.9);
  for (unsigned i=0;i<400;++i)
    require(!coalesced.poll(60,{true,-.002,-1}).valid,
            "lift completion reset an active hammer");
  const auto partial=coalesced.poll(60,{false,-.002,0});
  require(partial.valid&&partial.velocity==.9&&partial.requestId==4&&
          partial.preserveSeparatedPosition&&partial.recoveryVelocityFactor<.8,
          "coalesced lift ignored partial hammer recovery or latest request");
  require(coalesced.statistics().launches==2&&coalesced.statistics().coalesced==2,
          "lift completion created an extra queued strike");
}

void virginHammerRestAndVibratingNetwork() {
  // A virgin key must be ready at either phase of an already vibrating string.
  // The old adapter left its inactive hammer at x=0, so a negative string
  // displacement incorrectly looked like positive compression and deferred it.
  for (double sign:{-1.,1.}) {
    probe::Piano piano(48000,0);
    auto& key=piano.model.keys[39];
    auto& modes=piano.model.strings[key.strings.front()].m;
    const auto it=std::find_if(modes.hammer.begin(),modes.hammer.end(),
                             [](double h){return std::abs(h)>1.e-8;});
    require(it!=modes.hammer.end(),"virgin phase fixture has no hammer mode");
    const auto mode=size_t(it-modes.hammer.begin());
    modes.q[mode]=sign*1.e-6/modes.hammer[mode];
    piano.model.board.front().q=1.e-8;
    const auto prior=stringState(piano.model);
    require(piano.noteOn(60,80),"virgin first launch incorrectly gated by vibrating string phase");
    require(piano.controller.statistics().launches==1&&
            piano.controller.statistics().deferred==0,
            "virgin first launch was not immediate");
    require(stringState(piano.model)==prior,"virgin launch cleared existing string vibration");
    require(piano.lastLaunch[39].recovery==1&&
            !piano.lastLaunch[39].preserveSeparatedPosition,
            "virgin first launch treated as partial recovery");
  }

  probe::Piano piano(48000,0);
  for (unsigned i=0;i<88;++i) {
    const auto& key=piano.model.keys[i];
    require(!key.hammerActive&&key.hammerV==0&&
            key.hammerX==-piano.controller.config().restDepth,
            "unused hammer not at authored inactive rest geometry");
    require(!piano.controller.requiresTick(int(i)+21),
            "virgin rest fixture unexpectedly needs controller ticking");
  }
  // Real coupling path: pedal motion drives the board and unstruck strings
  // before the first note; none of those hammers has been ticked or launched.
  piano.enableMechanisms(true); piano.sustain(1);
  uint64_t frame=0; advance(piano,frame,480);
  require(keyra::mechanism_probe::boardEnergy(piano.model)>0&&
          keyra::mechanism_probe::stringEnergy(piano.model)>0,
          "pedal fixture did not excite body and unstruck strings");
  require(piano.noteOn(60,80)&&piano.controller.statistics().launches==1&&
          piano.controller.statistics().deferred==0,
          "preexisting body vibration falsely deferred virgin first launch");
}

void originalPhaseAndContactGate() {
  probe::Piano piano(48000,0);
  piano.sustain(1);
  const double before=piano.model.energy();
  require(piano.noteOn(60,93),"initial strike not launched");
  require(std::abs(piano.model.energy()-before-piano.ledger.coreLaunchWork)<1.e-14,
          "initial external launch work mismatch");
  uint64_t frame=0; advance(piano,frame,24);
  auto& hammer=piano.model.keys[39];
  require(hammer.hammerActive,"fixture missed active hammer");
  const auto state=stringState(piano.model);
  const double x=hammer.hammerX,v=hammer.hammerV,K=hammer.K;
  require(!piano.noteOn(60,61),"active hammer was immediately relaunched");
  require(hammer.hammerX==x&&hammer.hammerV==v&&hammer.K==K,"contact retrigger teleported hammer or changed felt");
  require(stringState(piano.model)==state,"noteOn reset resonating strings");
  require(piano.controller.state(60).pending,"active strike was not queued");
  piano.noteOff(60);
  require(!piano.controller.state(60).pending,"noteOff left ghost strike");
  advance(piano,frame,6000);
  require(piano.keyEnergy(60)>0,"sustain fixture lost all string history");
  const auto ringing=stringState(piano.model);
  const double energyBefore=piano.model.energy(),workBefore=piano.ledger.coreLaunchWork;
  require(piano.noteOn(60,61),"recovered hammer did not launch");
  require(stringState(piano.model)==ringing,"ready restrike cleared existing vibration");
  require(std::abs((piano.model.energy()-energyBefore)-(piano.ledger.coreLaunchWork-workBefore))<1.e-12,
          "restrike external core-work identity");
  require(piano.ledger.maximumInitialCompression<=0,"launch inserted contact potential");
  require(piano.ledger.retiredCoreHammerEnergy>=0,"negative retirement energy");
  require(!piano.noteOn(60,0)&&!piano.model.keys[39].down&&!piano.controller.state(60).down,
          "full adapter zero-velocity note-on launched a hammer");
  // Exercise the original safety timeout while the new stroke is still near
  // contact. The retirement is recorded, then finite-speed proxy return must
  // recover the key without an active-hammer reset.
  hammer.age=.040;
  advance(piano,frame,1);
  require(!hammer.hammerActive,"forced legacy retirement fixture failed");
  const double retiredX=hammer.hammerX;
  advance(piano,frame,1);
  require(piano.controller.statistics().retiredBeforeSeparation>0&&
          std::abs(hammer.hammerX-retiredX)<.0001,"retirement fallback did not retain finite return motion");
  advance(piano,frame,9000);
  require(piano.controller.state(60).recovery==1&&hammer.hammerV==0,
          "full adapter timeout left key permanently unready");
}

void readyAudioVariation() {
  probe::Piano piano(48000,1,2468);
  std::array<std::array<double,2>,384> prior{},current{};
  uint64_t frame=0;
  for (unsigned press=0;press<3;++press) {
    // Explicit fixture-only clearing isolates excitation variation from the
    // otherwise persistent string/board phases. Controller/RNG are not reset.
    for (auto& string:piano.model.strings) {
      std::fill(string.m.q.begin(),string.m.q.end(),0);
      std::fill(string.m.p.begin(),string.m.p.end(),0);
    }
    for (auto& mode:piano.model.board) mode.q=mode.p=mode.force=0;
    require(piano.noteOn(60,80),"ready audio strike not ready");
    for (auto& x:current) x=piano.step(frame++);
    if (press) require(std::memcmp(prior.data(),current.data(),sizeof(current))!=0,
                       "ready isolated same-velocity audio repeated exactly");
    prior=current; piano.noteOff(60); advance(piano,frame,6000);
  }
}

void rapidSequencesAndNoAllocation() {
  for (unsigned spacing:{240u,960u,3840u}) {
    probe::Piano piano(48000,.65,123);
    piano.sustain(1);
    const unsigned frames=spacing*5+2400;
    trackAllocation=true;
    for (unsigned frame=0;frame<frames;++frame) {
      if (frame%spacing==0&&frame/spacing<5) piano.noteOn(60,80);
      if (frame%spacing==spacing/2) piano.noteOff(60);
      if (frame==frames/2) piano.sustain(.4);
      const auto sample=piano.step(frame);
      require(std::isfinite(sample[0])&&std::isfinite(sample[1]),"rapid sequence became nonfinite");
    }
    trackAllocation=false;
    const auto& statistics=piano.controller.statistics();
    require(statistics.requests==5&&statistics.launches>0&&statistics.launches<=statistics.requests,
            "rapid repetition request accounting");
    require(piano.model.energy()>=0&&std::isfinite(piano.model.energy()),"rapid negative/invalid energy");
    require(allocations==0,"event/frame path allocated");
    std::printf("spacing %.1f ms: requests %llu launches %llu cancelled %llu partial %llu\n",
      spacing/48.,static_cast<unsigned long long>(statistics.requests),
      static_cast<unsigned long long>(statistics.launches),static_cast<unsigned long long>(statistics.cancelled),
      static_cast<unsigned long long>(piano.ledger.partialLaunches));
  }
}

void seedAndPartitionReproducibility() {
  probe::Piano a(48000,.65,555),b(48000,.65,555);
  std::array<std::array<double,2>,4800> reference{};
  const auto event=[](probe::Piano& piano,unsigned frame) {
    if (frame==0||frame==960||frame==3840) piano.noteOn(60,75);
    if (frame==480||frame==1440) piano.noteOff(60);
  };
  for (unsigned frame=0;frame<reference.size();++frame) {
    event(a,frame); reference[frame]=a.step(frame);
  }
  uint64_t frame=0;
  constexpr std::array<unsigned,5> partitions{{1,31,64,17,127}};
  unsigned part=0;
  while (frame<4800) {
    const auto end=std::min<uint64_t>(4800,frame+partitions[part++%partitions.size()]);
    for (;frame<end;++frame) {
      event(b,unsigned(frame));
      require(reference[frame]==b.step(frame),"seed/sample-timestamp reproduction changed with partitions");
    }
  }
  require(a.controller.statistics().launches==b.controller.statistics().launches,"reproduction launch mismatch");
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
  independentVariationAndBounds(); queuedAndPartialRecovery(); finiteLiftRepetition();
  virginHammerRestAndVibratingNetwork();
  originalPhaseAndContactGate();
  readyAudioVariation(); rapidSequencesAndNoAllocation(); seedAndPartitionReproducibility();
  std::puts("PASS strike repetition: eight groups");
}
