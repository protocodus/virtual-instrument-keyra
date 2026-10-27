#include "keyra/FullInstrument.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <limits>
#include <new>

#ifndef KEYRA_EXPECT_FULL_STRING_MODES
#define KEYRA_EXPECT_FULL_STRING_MODES 17778
#endif

namespace {
bool trackAllocations=false;
uint64_t allocations=0;
void require(bool condition,const char* reason) {
  if (!condition) {
    std::fprintf(stderr,"FAIL full instrument: %s\n",reason);
    std::exit(1);
  }
}
void* allocate(std::size_t size) {
  if (trackAllocations) ++allocations;
  if (void* p=std::malloc(size?size:1)) return p;
  std::abort();
}
using Instrument=keyra::FullInstrument;
using Config=keyra::FullInstrumentConfig;
constexpr unsigned count=4096;
struct Audio {
  std::array<float,count> left{},right{};
};
void same(const Audio& a,const Audio& b,const char* reason) {
  require(std::memcmp(a.left.data(),b.left.data(),sizeof(a.left))==0&&
          std::memcmp(a.right.data(),b.right.data(),sizeof(a.right))==0,reason);
}
double energy(const Audio& a,unsigned n=count) {
  double sum=0;
  for (unsigned i=0;i<n;++i) {
    require(std::isfinite(a.left[i])&&std::isfinite(a.right[i]),"nonfinite output");
    sum+=double(a.left[i])*a.left[i]+double(a.right[i])*a.right[i];
  }
  return sum;
}
void healthy(const Instrument& piano) {
  const auto d=piano.diagnostics();
  require(d.faultFlags==0&&d.bridgeFaults==0&&d.contactFaults==0&&
          d.nonfiniteOutputFaults==0&&d.unsafeLaunches==0,"normal input raised a solver fault");
}

// Event times straddle the original 64-frame damper/pedal clock. Each render
// receives identical events at identical absolute frames, with different block
// boundaries between them.
void score(Instrument& piano,Audio& audio,bool fragmented) {
  constexpr std::array<unsigned,8> times{{0,17,63,64,129,511,1025,2050}};
  constexpr std::array<unsigned,5> blocks{{1,3,17,64,257}};
  unsigned cursor=0,event=0,partition=0;
  while (cursor<count) {
    if (event<times.size()&&cursor==times[event]) {
      switch (event++) {
        case 0: require(piano.noteOn(60,.73),"score first note"); break;
        case 1: require(piano.noteOn(48,.42),"score second note"); break;
        case 2: require(piano.sustain(.8),"score pedal down"); break;
        case 3: require(piano.noteOff(60),"score release"); break;
        case 4: require(piano.noteOn(72,.61),"score treble"); break;
        case 5: require(piano.noteOff(48),"score bass release"); break;
        case 6: require(piano.sustain(.15),"score half pedal"); break;
        case 7: require(piano.noteOff(72),"score treble release"); break;
      }
    }
    const unsigned end=event<times.size()?times[event]:count;
    const unsigned requested=fragmented?blocks[partition++%blocks.size()]:count;
    const unsigned n=std::min(requested,end-cursor);
    require(n>0,"score made no progress");
    require(piano.process(audio.left.data()+cursor,audio.right.data()+cursor,n),"score render rejected");
    cursor+=n;
  }
}

void validation(Instrument& piano) {
  require(!piano.prepared(),"default instrument unexpectedly prepared");
  require(piano.process(nullptr,nullptr,0),"zero frame render rejected");
  require(!piano.noteOn(60,.7)&&!piano.sustain(1),"unprepared events accepted");
  for (double rate:{0.,44099.,96001.,48000.5,std::numeric_limits<double>::quiet_NaN(),
                   std::numeric_limits<double>::infinity()})
    require(!piano.prepare(rate)&&!piano.prepared(),"invalid initial sample rate accepted");
  Config config;
  require(piano.prepare(config)&&piano.prepared(),"valid full preparation failed");
  const auto initial=piano.diagnostics();
  require(initial.stringCount==230&&initial.stringModes==KEYRA_EXPECT_FULL_STRING_MODES&&initial.boardModes==475,
          "complete selected modal topology not retained");
  require(initial.frames==0&&initial.launches==0,"prepare did not clear runtime state");
  require(piano.noteOn(60,.7),"valid note rejected");
  Audio audio;
  require(piano.process(audio.left.data(),audio.right.data(),73),"validation render");
  const auto before=piano.diagnostics();
  config.sampleRate=std::numeric_limits<double>::quiet_NaN();
  require(!piano.prepare(config)&&piano.prepared()&&piano.diagnostics().frames==before.frames,
          "invalid reprepare replaced the running instance");
  const double nan=std::numeric_limits<double>::quiet_NaN();
  require(!piano.noteOn(20,.5)&&!piano.noteOn(109,.5)&&!piano.noteOn(60,-.01)&&
          !piano.noteOn(60,1.01)&&!piano.noteOn(60,nan)&&!piano.noteOff(0)&&
          !piano.sustain(-.1)&&!piano.sustain(1.1)&&!piano.sustain(nan),"invalid event accepted");
  require(!piano.process(nullptr,audio.right.data(),1)&&
          !piano.process(audio.left.data(),nullptr,1)&&
          !piano.process(audio.left.data(),audio.left.data(),1)&&
          piano.diagnostics().frames==before.frames,"invalid buffers advanced the frame clock");
  auto controls=piano.parameters();
  controls.humanization=nan;
  require(!piano.setParameters(controls),"nonfinite control accepted");
  controls=piano.parameters(); controls.dynamics=1.01;
  require(!piano.setParameters(controls),"out of range normalized control accepted");
  controls=piano.parameters(); controls.gainDb=12.01;
  require(!piano.setParameters(controls),"out of range gain accepted");
  controls=piano.parameters(); controls.stereoWidth=2.01;
  require(!piano.setParameters(controls),"out of range width accepted");
  require(piano.noteOn(60,0),"velocity zero was not accepted as release");
  piano.reset();
  const auto cleared=piano.diagnostics();
  require(cleared.frames==0&&cleared.requests==0&&cleared.launches==0&&
          cleared.rejectedInputs==0&&cleared.pedal==0&&cleared.pedalTarget==0,
          "reset retained counters, pedal or frame clock");
  require(piano.process(audio.left.data(),audio.right.data(),count),"reset silence render");
  require(energy(audio)==0,"reset left audible or resonating state");
}

void partitionResetAndIndependence(Instrument& a,Instrument& b) {
  Config config; config.seed=2468;
  // Exercise the connected mechanism path as well as per-key random state.
  config.parameters.mechanicalLevel=.06;
  require(a.prepare(config)&&b.prepare(config),"partition setup failed");
  Audio first,second,resetReplay;
  score(a,first,false);
  score(b,second,true);
  same(first,second,"partition or another instance changed audio");
  require(energy(first)>0,"score produced no sound");
  require(a.diagnostics().frames==count&&b.diagnostics().frames==count,
          "absolute frame count changed with block size");
  require(a.diagnostics().requests==3&&a.diagnostics().launches==3,
          "score requests or launches missing");
  healthy(a); healthy(b);
  a.allSoundOff();
  require(a.diagnostics().frames==0&&a.diagnostics().requests==0,"allSoundOff did not fully reset");
  score(a,resetReplay,true);
  same(first,resetReplay,"reset changed seed, filters, controllers or prepared pointers");
  Audio continuationA,continuationB;
  require(a.process(continuationA.left.data(),continuationA.right.data(),512)&&
          b.process(continuationB.left.data(),continuationB.right.data(),512),"continuation render");
  same(continuationA,continuationB,"reset or rendering another instance mutated shared state");
  const auto surviving=b.diagnostics();
  a.reset();
  require(b.diagnostics().frames==surviving.frames&&b.diagnostics().requests==surviving.requests,
          "one instance reset changed another instance");
}

void activeHammerAndRepetition(Instrument& a,Instrument& b) {
  Config config; config.parameters.humanization=0;
  // Queued key motion legitimately triggers texture; silence that independent
  // source to isolate the active-hammer and persistent-string contract.
  config.parameters.mechanicalLevel=0;
  require(a.prepare(config)&&b.prepare(config),"repetition setup");
  require(a.noteOn(60,.8)&&b.noteOn(60,.8),"initial repetition launch");
  Audio first,second;
  require(a.process(first.left.data(),first.right.data(),24)&&
          b.process(second.left.data(),second.right.data(),24),"contact prefix render");
  require(a.diagnostics().activeHammers==1,"fixture missed active hammer");
  require(b.noteOn(60,.2),"active repeat was not queued");
  require(a.noteOff(60)&&b.noteOff(60),"pending cancellation release");
  require(a.process(first.left.data(),first.right.data(),512)&&
          b.process(second.left.data(),second.right.data(),512),"contact cancellation render");
  same(first,second,"queued request changed active hammer or reset ringing strings");
  require(b.diagnostics().requests==2&&b.diagnostics().launches==1&&
          b.diagnostics().cancelled==1,"pending cancellation diagnostics incorrect");
  a.reset();
  require(a.sustain(1)&&a.noteOn(60,.7),"rapid repetition fixture");
  for (unsigned i=0;i<12;++i) require(a.noteOn(60,.4+.02*i),"rapid repeat request rejected");
  auto d=a.diagnostics();
  require(d.requests==13&&d.launches==1&&d.coalesced==11&&d.deferred>=12,
          "rapid repeat queue is not bounded/coalesced");
  require(a.process(first.left.data(),first.right.data(),count),"rapid repetition render");
  d=a.diagnostics();
  require(d.launches==2&&d.expired==0&&d.activeHammers<=1,
          "coalesced repeat failed to launch after hammer recovery");
  require(energy(first)>0,"queued repeat and ringing state produced no audio");
  require(d.pedal>.99&&d.pedalTarget==1,"global pedal did not persist across blocks");
  require(a.sustain(0),"pedal release rejected");
  const double before=d.pedal;
  require(a.process(first.left.data(),first.right.data(),512),"pedal return render");
  require(a.diagnostics().pedal<before&&a.diagnostics().pedalTarget==0,"pedal did not return globally");
  require(energy(first,512)>0,"restrike/pedal release lost all ringing state");
  healthy(a); healthy(b);
}

void touchingNotesAndPartition(Instrument& a,Instrument& b) {
  Config config;config.seed=8675309;config.parameters.mechanicalLevel=0;
  require(a.prepare(config)&&b.prepare(config),"touching API setup");
  constexpr unsigned length=12000;
  struct RepeatedAudio {std::array<float,length> left{},right{};} first,second;
  const auto play=[](Instrument& piano,RepeatedAudio& audio,bool fragmented) {
    constexpr std::array<unsigned,3> times{{0,4800,9600}};
    constexpr std::array<unsigned,5> blocks{{1,3,17,64,257}};
    require(piano.sustain(1),"touching API sustain");
    unsigned cursor=0,event=0,partition=0;
    while (cursor<length) {
      if (event<times.size()&&cursor==times[event]) {
        if (event) require(piano.noteOff(60),"touching API release");
        const auto before=piano.diagnostics();
        require(piano.noteOn(60,.7),"touching API press");
        if (event) require(piano.diagnostics().launches==before.launches,
                            "touching API press skipped finite lift");
        ++event;
      }
      const unsigned end=event<times.size()?times[event]:length;
      const unsigned requested=fragmented?blocks[partition++%blocks.size()]:length;
      const unsigned n=std::min(requested,end-cursor);
      require(n&&piano.process(audio.left.data()+cursor,audio.right.data()+cursor,n),
              "touching API render rejected");
      cursor+=n;
    }
    const auto d=piano.diagnostics();
    require(d.requests==3&&d.launches==3&&d.cancelled==0&&d.expired==0&&
            d.frames==length,"touching MIDI notes failed to rearm");
    healthy(piano);
  };
  play(a,first,false);play(b,second,true);
  require(std::memcmp(first.left.data(),second.left.data(),sizeof(first.left))==0&&
          std::memcmp(first.right.data(),second.right.data(),sizeof(first.right))==0,
          "finite-lift repetition changed with seed or block partition");
  double sum=0;
  for (unsigned i=0;i<length;++i) {
    require(std::isfinite(first.left[i])&&std::isfinite(first.right[i]),
            "touching API output became nonfinite");
    sum+=double(first.left[i])*first.left[i]+double(first.right[i])*first.right[i];
  }
  require(sum>0,"touching API score silent");
}

void virginHammerOnMovingBody(Instrument& piano) {
  Config config;config.parameters.mechanicalLevel=.2;
  config.mechanismBodyCoupling=true;config.mechanismObservation=false;
  require(piano.prepare(config),"moving body initial hammer setup");
  Audio audio;
  for (unsigned pass=0;pass<2;++pass) {
    if (pass) piano.reset();
    // A pedal source sets the board and attached strings moving before C4's
    // first request. At this phase the old hammerX=0 falsely implied contact.
    require(piano.sustain(1)&&piano.process(audio.left.data(),audio.right.data(),480),
            "moving body prefix render");
    require(energy(audio,480)>0,"initial hammer fixture has no body motion");
    require(piano.diagnostics().launches==0,"body fixture unexpectedly struck a key");
    require(piano.noteOn(60,.7),"initial strike on moving body rejected");
    const auto d=piano.diagnostics();
    require(d.requests==1&&d.launches==1&&d.deferred==0,
            "virgin hammer was phase-gated by existing body/string motion");
    healthy(piano);
  }
}

void noRuntimeAllocation(Instrument& piano) {
  Config config; config.parameters.mechanicalLevel=.05;
  require(piano.prepare(config),"allocation fixture preparation");
  Audio audio;
  allocations=0; trackAllocations=true;
  require(piano.sustain(.7),"allocation pedal event");
  for (int note=21;note<=108;++note) require(piano.noteOn(note,.05),"allocation note event");
  require(piano.process(audio.left.data(),audio.right.data(),64),"allocation render");
  healthy(piano);
  for (int note=21;note<=108;++note) require(piano.noteOff(note),"allocation release");
  auto parameters=piano.parameters(); parameters.humanization=.2; parameters.gainDb=-3;
  require(piano.setParameters(parameters),"allocation parameters");
  (void)piano.diagnostics();
  piano.reset(); piano.allSoundOff();
  require(piano.process(audio.left.data(),audio.right.data(),64),"allocation reset render");
  trackAllocations=false;
  require(allocations==0,"events, render, controls, diagnostics or reset allocated");
  healthy(piano);
}

void supportedRateEndpoints(Instrument& piano) {
  Audio audio;
  for (double rate:{44100.,96000.}) {
    require(piano.prepare(rate),"supported sample-rate endpoint rejected");
    require(piano.noteOn(60,.5)&&piano.process(audio.left.data(),audio.right.data(),256),
            "supported sample-rate endpoint could not render");
    require(energy(audio,256)>0,"supported sample-rate endpoint silent");
    healthy(piano);
  }
}

void independentMechanismPaths(Instrument& piano) {
  Config config; config.parameters.mechanicalLevel=.2;
  Audio audio;
  const auto playPedal=[&]() {
    require(piano.prepare(config)&&piano.sustain(1),"mechanism path setup");
    require(piano.process(audio.left.data(),audio.right.data(),256),"mechanism path render");
    healthy(piano);
    return energy(audio,256);
  };
  // With initially motionless strings, this event excites only the pedal
  // source. Its direct observer and physical board reaction can be isolated.
  config.mechanismBodyCoupling=false; config.mechanismObservation=false;
  require(playPedal()==0,"disabled mechanism paths leaked audio");
  config.mechanismObservation=true;
  require(playPedal()>0,"direct mechanism observation is disconnected");
  require(std::memcmp(audio.left.data(),audio.right.data(),256*sizeof(float))==0,
          "uncoupled direct pedal source unexpectedly changed stereo body state");
  config.mechanismBodyCoupling=true; config.mechanismObservation=false;
  require(playPedal()>0,"mechanism body reaction is disconnected");
  require(std::memcmp(audio.left.data(),audio.right.data(),256*sizeof(float))!=0,
          "body-only mechanism path did not reach the two board observers");
  config.parameters.mechanicalLevel=0;
  require(playPedal()==0,"zero mechanical level retained pedal excitation");
}

void mechanismReprepareAndReset(Instrument& reused) {
  // Reusing prepared coefficient storage must match an entirely fresh cache,
  // including after a sample-rate change and disabled/re-enabled mechanisms.
  for (double rate:{48000.,96000.,48000.}) {
    Config config;config.sampleRate=rate;config.seed=123321;
    config.parameters.mechanicalLevel=.2;config.mechanismObservation=false;
    Instrument fresh;
    require(reused.prepare(config)&&fresh.prepare(config),"mechanism reprepare setup");
    Audio first,second;
    const auto render=[&](unsigned frames) {
      first={};second={};
      require(reused.process(first.left.data(),first.right.data(),frames)&&
              fresh.process(second.left.data(),second.right.data(),frames),"mechanism reprepare render");
      same(first,second,"reprepared body coefficients differ from a fresh instrument");
    };
    require(reused.sustain(.8)&&fresh.sustain(.8),"mechanism reprepare trigger");
    render(512);require(energy(first,512)>0,"reprepared body path silent");
    const auto before=reused.diagnostics();
    auto invalid=config;invalid.parameters.mechanicalLevel=std::numeric_limits<double>::quiet_NaN();
    require(!reused.prepare(invalid)&&reused.diagnostics().frames==before.frames,
            "invalid reprepare changed running body state");
    render(256);
    auto controls=reused.parameters();controls.mechanicalLevel=0;
    require(reused.setParameters(controls)&&fresh.setParameters(controls),"disable mechanism controls");
    render(128);
    reused.reset();fresh.reset();controls.mechanicalLevel=.2;
    require(reused.setParameters(controls)&&fresh.setParameters(controls),"reenable mechanism controls");
    render(256);require(energy(first,256)==0,"reset retained mechanism impulse or coefficient state");
    require(reused.sustain(.5)&&fresh.sustain(.5),"reset mechanism retrigger");
    render(512);require(energy(first,512)>0,"reset disconnected mechanism reaction");
    healthy(reused);healthy(fresh);
  }
}
} // namespace

void* operator new(std::size_t n) { return allocate(n); }
void* operator new[](std::size_t n) { return allocate(n); }
// Cover nothrow construction too: the core uses it for setup allocations.
// A sanitizer's nothrow-new interceptor otherwise allocates with a different
// family than the malloc/free pair used by these tracking replacements.
void* operator new(std::size_t n,const std::nothrow_t&) noexcept { return allocate(n); }
void* operator new[](std::size_t n,const std::nothrow_t&) noexcept { return allocate(n); }
void operator delete(void* p) noexcept { std::free(p); }
void operator delete[](void* p) noexcept { std::free(p); }
void operator delete(void* p,std::size_t) noexcept { std::free(p); }
void operator delete[](void* p,std::size_t) noexcept { std::free(p); }
void operator delete(void* p,const std::nothrow_t&) noexcept { std::free(p); }
void operator delete[](void* p,const std::nothrow_t&) noexcept { std::free(p); }

int main() {
  Instrument a,b;
  validation(a);
  partitionResetAndIndependence(a,b);
  activeHammerAndRepetition(a,b);
  touchingNotesAndPartition(a,b);
  virginHammerOnMovingBody(a);
  noRuntimeAllocation(a);
  supportedRateEndpoints(a);
  independentMechanismPaths(a);
  mechanismReprepareAndReset(a);
  std::puts("Full physical block API: topology, validation, partition, reset, repetition, pedal, independence and allocation checks passed");
}
