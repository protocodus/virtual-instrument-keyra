#include "DSP/KeyraEngine.h"
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <new>
#include <sstream>
#include <string>
#include <vector>

namespace {bool trap=false;std::size_t allocations=0;int failures=0;
#ifdef __VERSION__
constexpr const char* compilerVersion=__VERSION__;
#else
constexpr const char* compilerVersion="native compiler";
#endif
void check(bool condition,const char* message){if(!condition){std::cerr<<"FAIL: "<<message<<'\n';++failures;}}
using Audio=std::vector<float>;
Audio render(keyra::Engine& engine,int frames,int block=127){
  Audio audio(static_cast<std::size_t>(frames)*2);std::array<float,512> l{},r{};
  int done=0;while(done<frames){const int n=std::min(block,frames-done);engine.process(l.data(),r.data(),n);
    for(int i=0;i<n;++i){audio[2*(done+i)]=l[i];audio[2*(done+i)+1]=r[i];}done+=n;}
  return audio;
}
double rms(const Audio& audio){double sum=0;for(float x:audio)sum+=static_cast<double>(x)*x;return std::sqrt(sum/std::max<std::size_t>(1,audio.size()));}
keyra::Parameters dry(){keyra::Parameters p;p.resonance=0;return p;}
double released(float sustain){keyra::Engine e;e.setParameters(dry());e.controlChange(64,static_cast<int>(sustain*127));e.noteOn(60,.7f);render(e,12000);e.noteOff(60);render(e,24000);return rms(render(e,12000));}
double sostenuto(bool beforeNote){keyra::Engine e;e.setParameters(dry());if(beforeNote)e.controlChange(66,127);e.noteOn(60,.7f);render(e,12000);if(!beforeNote)e.controlChange(66,127);e.noteOff(60);render(e,24000);return rms(render(e,12000));}
std::string timing(int count){
  std::array<double,3> onset{},cpu{},wall{};
  for(int run=0;run<3;++run){keyra::Engine e;e.setParameters(dry());
    const auto onsetStart=std::clock();for(int i=0;i<count;++i)e.noteOn(36+i%60,.6f,1+i/88);
    onset[run]=static_cast<double>(std::clock()-onsetStart)/CLOCKS_PER_SEC;
    const auto start=std::chrono::steady_clock::now();const auto cpuStart=std::clock();render(e,48000,256);
    cpu[run]=static_cast<double>(std::clock()-cpuStart)/CLOCKS_PER_SEC;
    wall[run]=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  }
  std::sort(onset.begin(),onset.end());std::sort(cpu.begin(),cpu.end());std::sort(wall.begin(),wall.end());
  std::ostringstream json;json<<std::setprecision(9)<<"{\"notes\":"<<count<<",\"sample_rate\":48000,\"duration_seconds\":1,\"block_size\":256,\"runs\":3,\"median_onset_process_cpu_ms\":"<<onset[1]*1000<<",\"median_process_cpu_realtime_factor\":"<<cpu[1]<<",\"median_wall_realtime_factor\":"<<wall[1]<<"}";return json.str();
}
}
void* operator new(std::size_t size){if(trap)++allocations;if(void* p=std::malloc(size))return p;throw std::bad_alloc();}
void* operator new[](std::size_t size){return ::operator new(size);}
void operator delete(void* p) noexcept {std::free(p);}void operator delete[](void* p) noexcept {std::free(p);}
void operator delete(void* p,std::size_t) noexcept {std::free(p);}void operator delete[](void* p,std::size_t) noexcept {std::free(p);}

int main(int argc,char** argv){
  if(argc>1){
    std::ostringstream json;json<<"{\"scope\":\"development machine native DSP only; not Reason host performance\",\"compiler\":\""<<compilerVersion<<"\",\"clock\":\"process CPU median; wall also reported for contention\",\"cases\":[";
    json<<timing(12)<<','<<timing(32)<<','<<timing(128)<<"]}\n";
    if(argc>2){std::ofstream out(argv[2]);out<<json.str();}
    std::cout<<json.str();return 0;
  }
  {
    keyra::Engine a,b;a.setParameters(dry());b.setParameters(dry());
    check(rms(render(a,5000))==0,"fresh engine exact silence");
    a.noteOn(60,.7f);b.noteOn(60,.7f);
    check(render(a,24000,1)==render(b,24000,512),"block segmentation invariance");
    a.reset();b.reset();a.noteOn(60,.7f);b.noteOn(60,.7f);
    check(render(a,24000)==render(b,24000),"reset deterministic");
  }
  {
    keyra::Engine a,b;a.setParameters(dry());b.setParameters(dry());a.noteOn(60,.7f,1);b.noteOn(60,.7f,1);
    render(a,12000);render(b,12000);a.noteOff(60,2);a.controlChange(1,127,2);
    check(render(a,24000)==render(b,24000),"foreign channel noteOff and mute preserve channel1 exactly");
    a.noteOn(60,.7f,1);b.noteOn(60,.7f,1);a.noteOff(60,1);
    check(render(a,24000)==render(b,24000),"repeated positive note ownership counts balanced");
    a.noteOff(60,1);b.noteOff(60,1);b.noteOff(60,1);
    check(render(a,24000)==render(b,24000),"final paired release owns all same-key strike tails");
  }
  const double down=released(0),half=released(.5f),up=released(1);
  check(down<half&&half<up,"continuous half pedal orders released tail energy");
  check(up>down*100,"sustain preserves released strings");
  check(sostenuto(false)>sostenuto(true)*100,"sostenuto rising edge captures only already held keys");
  {
    keyra::Engine e;e.noteOn(12,.5f,1);e.noteOn(13,.5f,1);e.noteOn(14,.5f,1);
    const auto state=e.pedalState(1);
    check(state.soft==1&&state.sostenuto==1&&state.sustain==1,"keyswitch12/13/14 maps to soft/sostenuto/sustain below piano range");
    check(rms(render(e,4800))==0,"keyswitches create no audible string voices");
    check(e.pedalState(2).soft==0&&e.pedalState(2).sustain==0&&e.pedalState(2).sostenuto==0,"keyswitch ownership is channel local");
    check(e.pedalState().soft==1&&e.pedalState().sustain==1,"aggregate pedal query publishes keyswitch activity");
    e.noteOff(12,2);check(e.pedalState(1).soft==1,"foreign channel keyswitch release preserves owner");
    e.noteOn(12,.5f);e.noteOff(12);check(e.pedalState(1).soft==1,"repeated keyswitch presses require balanced releases");
    e.noteOn(12,0);check(e.pedalState(1).soft==0,"velocity-zero keyswitch note releases its final press");
    e.reset();check(e.pedalState().soft==0&&e.pedalState().sostenuto==0&&e.pedalState().sustain==0,"reset clears all momentary keyswitch ownership");
  }
  for(const int sw:{12,13,14}){
    keyra::Engine e;const int cc=sw==12?67:sw==13?66:64;
    auto level=[&](){const auto s=e.pedalState(1);return sw==12?s.soft:sw==13?s.sostenuto:s.sustain;};
    e.controlChange(cc,64);e.noteOn(sw,.8f);check(level()==1,"keyswitch composes with independent physical CC source");
    e.noteOff(sw);check(level()==64/127.f,"releasing switch preserves physical CC pedal position");
    auto p=dry();if(sw==12)p.soft=.8f;else if(sw==13)p.sostenuto=.8f;else p.sustain=.8f;e.setParameters(p);
    e.noteOn(sw,.8f);e.controlChange(cc,0);check(level()==1,"releasing physical CC preserves held switch source");
    e.noteOff(sw);check(level()==.8f,"releasing switch preserves panel pedal position");
    e.setParameters(dry());check(level()==0,"effective pedal releases once all independent sources release");
    e.noteOn(sw,.8f);e.controlChange(121,0);check(level()==1,"CC121 preserves held keyswitch ownership");
    e.controlChange(cc,64);e.controlChange(123,0);check(level()==64/127.f,"CC123 clears key-held switch but preserves CC source");
    e.noteOn(sw,.8f);e.controlChange(120,0);check(level()==64/127.f,"CC120 clears transient switch ownership without resetting CC source");
  }
  {
    keyra::Engine a,b;a.setParameters(dry());b.setParameters(dry());a.noteOn(14,.7f,2);
    a.noteOn(60,.7f,1);b.noteOn(60,.7f,1);render(a,12000);render(b,12000);a.noteOff(60);b.noteOff(60);
    check(render(a,24000)==render(b,24000),"another channel's sustain switch cannot hold channel1 voices");
  }
  {
    keyra::Engine a,b;a.setParameters(dry());b.setParameters(dry());a.noteOn(60,.7f);b.noteOn(60,.7f);
    a.noteOn(13,.7f);b.controlChange(66,127);a.noteOn(72,.6f);b.noteOn(72,.6f);a.noteOn(13,.7f);
    a.controlChange(121,0);a.noteOff(60);b.noteOff(60);a.noteOff(72);b.noteOff(72);
    check(render(a,24000)==render(b,24000),"repeated sostenuto switch and CC121 do not capture later notes");
    a.noteOff(13);check(a.pedalState().sostenuto==1,"sostenuto switch remains latched until last matching release");
    a.noteOff(13);b.controlChange(66,0);check(render(a,12000)==render(b,12000),"final sostenuto switch release damps its original captured notes");
  }
  {
    keyra::Engine a,b;a.setParameters(dry());b.setParameters(dry());a.noteOn(60,.7f);b.noteOn(60,.7f);
    render(a,12000);render(b,12000);a.noteOff(60);b.noteOff(60);render(a,960);render(b,960);
    a.controlChange(64,127);render(a,18000);render(b,18000);
    check(rms(render(a,12000))>rms(render(b,12000))*10,"re-pedaling catches a still vibrating released string");
  }
  {
    keyra::Engine a,b;auto p=dry();p.sostenuto=1;a.setParameters(p);b.setParameters(p);
    a.noteOn(60,.7f);b.noteOn(60,.7f);render(a,12000);render(b,12000);a.controlChange(121,0);
    a.noteOff(60);b.noteOff(60);check(render(a,24000)==render(b,24000),"CC121 never creates an edge on an unchanged panel sostenuto pedal");
  }
  {
    keyra::Engine a,b;a.setParameters(dry());b.setParameters(dry());
    a.noteOn(60,.7f);b.noteOn(60,.7f);render(a,12000);render(b,12000);
    a.controlChange(1,127);render(a,24000);render(b,24000);
    check(rms(render(a,12000))<rms(render(b,12000))*.001,"CC1 physically damps held strings smoothly");
    a.controlChange(120,0);check(rms(render(a,512))==0,"all sound off clears owned voices and shared residue when last channel stops");
  }
  {
    keyra::Engine a,b;a.setParameters(dry());auto p=dry();p.soft=1;b.setParameters(p);a.noteOn(72,.7f);b.noteOn(72,.7f);
    check(rms(render(b,24000))<rms(render(a,24000)),"soft pedal changes hammer excitation");
    keyra::Engine c,d;c.setParameters(dry());d.setParameters(dry());c.controlChange(64,127);c.controlChange(66,127);c.controlChange(1,127);c.pitchBend(2);c.controlChange(121,0);
    c.noteOn(60,.7f);d.noteOn(60,.7f);check(render(c,24000)==render(d,24000),"reset all controllers restores channel playing state");
  }
  for(const double rate:{8000.,22050.,44100.,48000.,96000.,192000.}){
    keyra::Engine e(rate);auto p=dry();p.brightness=std::numeric_limits<float>::quiet_NaN();p.tuning=std::numeric_limits<float>::infinity();e.setParameters(p);
    for(int note:{21,60,108})e.noteOn(note,1);
    for(float bend:{-48.f,0.f,48.f}){e.pitchBend(bend);const auto a=render(e,4000);for(float x:a)check(std::isfinite(x)&&std::abs(x)<=1,"rate/bend/nonfinite parameter output finite and bounded");}
  }
  for(const float composite:{377.55f,508.54f}){
    keyra::Engine a,b;auto pa=dry(),pb=dry();pa.tuning=composite;pb.tuning=composite<400?400:480;a.setParameters(pa);b.setParameters(pb);
    a.noteOn(72,.7f);b.noteOn(72,.7f);check(render(a,12000)!=render(b,12000),"host master tuning composes beyond UI endpoints without internal clamping");
  }
  {
    keyra::Engine e;std::array<float,64> l{},r{};trap=true;
    e.noteOn(60,.8f);e.noteOn(72,.8f,2);e.noteOff(60);e.noteOn(12,.7f);e.noteOn(13,.7f);e.noteOn(14,.7f);e.noteOff(12);e.controlChange(64,80);e.controlChange(66,127);e.controlChange(67,64);e.pitchBend(.5f);e.setParameters(dry());
    const auto pedals=e.pedalState();(void)pedals;
    for(int i=0;i<40;++i)e.process(l.data(),r.data(),64);
    e.reset();e.controlChange(120,0);trap=false;
    check(allocations==0,"all live event/render/reset APIs allocate zero bytes");
  }
  for(int count:{3,6,10}){
    keyra::Engine e;for(int i=0;i<count;++i)e.noteOn(36+i*7,1);
    const auto audio=render(e,48000);float peak=0;for(float x:audio)peak=std::max(peak,std::abs(x));
    check(peak<.9f,"fortissimo chord has headroom before emergency hard ceiling");
    std::cout<<"headroom_notes="<<count<<" peak_dbfs="<<20*std::log10(peak)<<'\n';
  }
  std::cout<<"engine_failures="<<failures<<" live_allocations="<<allocations<<'\n';return failures?1:0;
}
