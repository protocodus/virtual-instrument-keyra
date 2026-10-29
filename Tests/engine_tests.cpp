#include "DSP/KeyraEngine.h"
#include "DSP/MeasuredModalData.h"
#include "DSP/MeasuredUprightData.h"
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <complex>
#include <cstdlib>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <new>
#include <sstream>
#include <utility>
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
keyra::Parameters dryUpright(){auto p=dry();p.piano=keyra::Piano::upright;return p;}
// C4's own strings: the amplitude of its first four partials, in both
// channels, at a piano's measured pitch (the grand's unless given). They sit
// below F6, where the undamped strings its strike sets ringing begin; no
// damper reaches those, so a key-up leaves them sounding.
template<class Anchors> double c4Strings(const Audio& audio,const Anchors& anchors){
  constexpr double pi=3.14159265358979323846;
  const auto* a=&anchors[0];for(const auto& x:anchors)if(x.note==60)a=&x;
  const std::size_t frames=audio.size()/2;double sum=0;
  for(int n=1;n<=4;++n){
    const double frequency=n*a->f1*std::sqrt((1+a->B*n*n)/(1+a->B));
    const double c=std::cos(2*pi*frequency/48000),s=std::sin(2*pi*frequency/48000);
    for(int channel=0;channel<2;++channel){
      double phaseC=1,phaseS=0,re=0,im=0;
      for(std::size_t i=0;i<frames;++i){const double x=audio[2*i+channel]*(.5-.5*std::cos(2*pi*i/(frames-1)));
        re+=x*phaseC;im+=x*phaseS;const double nextC=phaseC*c-phaseS*s;phaseS=phaseS*c+phaseC*s;phaseC=nextC;}
      sum+=re*re+im*im;}
  }
  return std::sqrt(sum);
}
double c4Strings(const Audio& audio){return c4Strings(audio,keyra::measured::grand::anchors);}
// The engine's fundamental for a key (A4 = 440 Hz): its cents from equal
// temperament between the recorded pitches around it.
double keyPitch(int key){
  namespace m=keyra::measured::grand;
  int upper=1;while(upper<static_cast<int>(m::anchors.size())-1&&m::anchors[upper].note<key)++upper;
  const auto& a=m::anchors[upper-1];const auto& b=m::anchors[upper];
  auto cents=[](const keyra::measured::Anchor& x){return 1200*std::log2(x.f1/(440*std::pow(2.,(x.note-69)/12.)));};
  return 440*std::pow(2.,(key-69+(cents(a)+(cents(b)-cents(a))*(key-a.note)/(b.note-a.note))/100)/12.);
}
// The frequency of the undamped string `j` places above F6.
double haloHz(int j){return keyPitch(89+j)*std::pow(2.,keyra::measured::grand::haloStrings[j].cents/1200);}
double released(float sustain){keyra::Engine e;e.setParameters(dry());e.controlChange(64,static_cast<int>(sustain*127));e.noteOn(60,.7f);render(e,12000);e.noteOff(60);render(e,24000);return c4Strings(render(e,12000));}
double sostenuto(bool beforeNote){keyra::Engine e;e.setParameters(dry());if(beforeNote)e.controlChange(66,127);e.noteOn(60,.7f);render(e,12000);if(!beforeNote)e.controlChange(66,127);e.noteOff(60);render(e,24000);return c4Strings(render(e,12000));}
Audio sympatheticTail(float tuning,bool prepareAfterTuning){
  keyra::Engine wet,direct;auto wp=dry();wp.gain=.3f;wp.resonance=1;wp.sustain=1;
  if(prepareAfterTuning)wp.tuning=tuning;
  auto dp=wp;dp.resonance=0;wet.setParameters(wp);direct.setParameters(dp);
  if(prepareAfterTuning){wet.prepare(48000);direct.prepare(48000);}
  // Keep a very quiet second channel active so stopping the main note does
  // not clear the shared bank. Wet minus dry isolates its free radiation.
  wet.noteOn(21,.00001f,2);direct.noteOn(21,.00001f,2);
  wet.noteOn(69,.7f,1);direct.noteOn(69,.7f,1);render(wet,24000);render(direct,24000);
  if(!prepareAfterTuning){wp.tuning=tuning;dp.tuning=tuning;wet.setParameters(wp);direct.setParameters(dp);}
  wet.controlChange(120,0,1);direct.controlChange(120,0,1);
  auto tail=render(wet,38400),base=render(direct,38400);
  for(std::size_t i=0;i<tail.size();++i)tail[i]-=base[i];
  return tail;
}
double spectralPeak(const Audio& audio,double low,double high){
  constexpr double pi=3.14159265358979323846;
  const std::size_t frames=audio.size()/2;std::vector<double> signal(frames);
  for(std::size_t i=0;i<frames;++i)signal[i]=.5*(audio[2*i]+audio[2*i+1])*(.5-.5*std::cos(2*pi*i/(frames-1)));
  double peak=low,power=-1;
  for(double frequency=low;frequency<=high;frequency+=.25){
    const double c=std::cos(2*pi*frequency/48000),s=std::sin(2*pi*frequency/48000);
    double phaseC=1,phaseS=0,re=0,im=0;
    for(const double sample:signal){re+=sample*phaseC;im+=sample*phaseS;const double nextC=phaseC*c-phaseS*s;phaseS=phaseS*c+phaseC*s;phaseC=nextC;}
    const double candidate=re*re+im*im;if(candidate>power){power=candidate;peak=frequency;}
  }
  return peak;
}
// Each third-octave band's power over the whole render, both channels: band
// k is centred on 20 * 2^(k/3) Hz.
std::array<double,31> thirdOctaves(const Audio& audio){
  constexpr double pi=3.14159265358979323846;
  std::size_t n=1;while(n<audio.size()/2)n<<=1;
  std::array<double,31> bands{};
  for(int channel=0;channel<2;++channel){
    std::vector<std::complex<double>> a(n);
    for(std::size_t i=0;i<audio.size()/2;++i)a[i]=audio[2*i+static_cast<std::size_t>(channel)];
    for(std::size_t i=1,j=0;i<n;++i){std::size_t bit=n>>1;for(;j&bit;bit>>=1)j^=bit;j^=bit;if(i<j)std::swap(a[i],a[j]);}
    for(std::size_t length=2;length<=n;length<<=1){const auto w=std::polar(1.,-2*pi/static_cast<double>(length));
      for(std::size_t i=0;i<n;i+=length){std::complex<double> turn=1;
        for(std::size_t j=0;j<length/2;++j){const auto u=a[i+j],v=a[i+j+length/2]*turn;a[i+j]=u+v;a[i+j+length/2]=u-v;turn*=w;}}}
    for(std::size_t k=1;k<n/2;++k){
      const int band=static_cast<int>(std::floor(3*std::log2(static_cast<double>(k)*48000/static_cast<double>(n)/20)+.5));
      if(band>=0&&band<31)bands[static_cast<std::size_t>(band)]+=std::norm(a[k]);}
  }
  return bands;
}
// The right channel's level against the left's, in dB, at the strongest
// frequency between `low` and `high`.
double levelDifference(const Audio& audio,double low,double high){
  constexpr double pi=3.14159265358979323846;
  const std::size_t frames=audio.size()/2;std::vector<double> w(frames);
  for(std::size_t i=0;i<frames;++i)w[i]=.5-.5*std::cos(2*pi*i/(frames-1));
  double power=-1,difference=0;
  for(double frequency=low;frequency<=high;frequency+=.25){
    const double c=std::cos(2*pi*frequency/48000),s=std::sin(2*pi*frequency/48000);
    double phaseC=1,phaseS=0,lr=0,li=0,rr=0,ri=0;
    for(std::size_t i=0;i<frames;++i){const double l=w[i]*audio[2*i],r=w[i]*audio[2*i+1];
      lr+=l*phaseC;li+=l*phaseS;rr+=r*phaseC;ri+=r*phaseS;const double nextC=phaseC*c-phaseS*s;phaseS=phaseS*c+phaseC*s;phaseC=nextC;}
    const double left=lr*lr+li*li,right=rr*rr+ri*ri;
    if(left+right>power){power=left+right;difference=10*std::log10(right/left);}
  }
  return difference;
}
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
    // No two strikes of a key land alike: each plays at a player's spread
    // about its velocity, within a few dB. Steady strikes play the velocity
    // itself, and an engine from its start replays the same strikes.
    auto twice=[](bool steady){keyra::Engine e;e.setParameters(dry());e.setSteadyStrikesForMeasurement(steady);
      e.noteOn(60,.7f);const auto first=render(e,24000);e.controlChange(120,0);render(e,4800);
      e.noteOn(60,.7f);return std::make_pair(first,render(e,24000));};
    const auto played=twice(false),steady=twice(true);
    const double apart=20*std::log10(rms(played.second)/rms(played.first));
    std::cout<<"second_strike_against_first_db="<<apart<<'\n';
    check(played.first!=played.second&&std::abs(apart)<6,"no two strikes of a key land alike");
    check(steady.first==steady.second,"steady strikes play their velocity exactly");
    check(played==twice(false),"an engine from its start replays the same strikes");
  }
  {
    // Below full quality a strike leaves out only what no band of the note
    // hears (keepAudible). Over every third key at velocities 40, 80, 110 and
    // 127 these keys' bands changed the most, each piano's at each quality:
    // in 3 s of each, no third-octave band within 40 dB of the strongest
    // moves by more than 0.1 dB at balanced quality or 1 dB at light, and
    // light leaves something out.
    struct Key {keyra::Piano piano;int note;float velocity;};
    const std::array<Key,4> keys{{{keyra::Piano::grand,51,80/127.f},{keyra::Piano::grand,93,1},
                                  {keyra::Piano::upright,33,40/127.f},{keyra::Piano::upright,42,110/127.f}}};
    double worst[3]{};bool lighter=true;
    for(const auto& key:keys){
      std::array<Audio,3> audio;std::array<std::array<double,31>,3> bands;
      for(std::size_t q=0;q<3;++q){keyra::Engine e;keyra::Parameters p;p.piano=key.piano;p.quality=static_cast<keyra::Quality>(q);
        e.setParameters(p);e.noteOn(key.note,key.velocity);audio[q]=render(e,144000);bands[q]=thirdOctaves(audio[q]);}
      const double top=*std::max_element(bands[0].begin(),bands[0].end());
      for(std::size_t q=1;q<3;++q)for(std::size_t b=0;b<bands[0].size();++b)
        if(bands[0][b]>top*1e-4)worst[q]=std::max(worst[q],std::abs(10*std::log10(bands[q][b]/bands[0][b])));
      lighter=lighter&&audio[2]!=audio[0];
    }
    std::cout<<"quality_band_change_db balanced="<<worst[1]<<" light="<<worst[2]<<'\n';
    check(worst[1]<.1&&worst[2]<1,"below full quality no band the note is heard in changes");
    check(lighter,"light quality leaves out what no band hears");
  }
  {
    // One velocity response for both pianos: a velocity asks for a level under
    // the loudest layer, halfway between a straight line and smoothstep from
    // the higher of the two softest layers' levels, and plays where each
    // piano's measured layers reach it.
    namespace g=keyra::measured::grand;namespace u=keyra::measured::upright;
    auto level=[](const auto& v,const auto& l,int layers,double at){
      int i=0;while(i<layers-2&&at>v[i+1])++i;
      return l[i]+(l[i+1]-l[i])*(at-v[i])/(v[i+1]-v[i]);};
    const double floor=std::max(g::layerLevelDb[0],u::layerLevelDb[0]);
    double worst=0;float last[2]{};bool rising=true;
    for(int midi=1;midi<=127;++midi){
      const double x=(midi-1)/126.,wanted=floor*(1-.5*(x+x*x*(3-2*x)));
      const float at[2]{keyra::responseVelocity(keyra::Piano::grand,midi/127.f),
                        keyra::responseVelocity(keyra::Piano::upright,midi/127.f)};
      worst=std::max({worst,std::abs(level(g::layerVelocity,g::layerLevelDb,g::layers,at[0])-wanted),
                      std::abs(level(u::layerVelocity,u::layerLevelDb,u::layers,at[1])-wanted)});
      rising=rising&&at[0]>=last[0]&&at[1]>=last[1];last[0]=at[0];last[1]=at[1];
    }
    std::cout<<"velocity_response_worst_db="<<worst<<'\n';
    check(worst<.01,"both pianos play the shared velocity response's level at every velocity");
    check(rising,"a harder strike never plays a softer layer");
    check(last[0]==g::layerVelocity[g::layers-1]&&last[1]==u::layerVelocity[u::layers-1],
          "velocity 127 plays each piano's loudest layer");
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
    // The soft and sostenuto switches are silent; the sustain switch sounds
    // its pedal going down, as CC64 does, and nothing more.
    keyra::Engine e,pedal;e.noteOn(12,.5f,1);e.noteOn(13,.5f,1);
    check(rms(render(e,4800))==0,"soft and sostenuto keyswitches make no sound");
    e.noteOn(14,.5f,1);pedal.controlChange(64,127);
    const auto state=e.pedalState(1);
    check(state.soft==1&&state.sostenuto==1&&state.sustain==1,"keyswitch12/13/14 maps to soft/sostenuto/sustain below piano range");
    const auto sounded=render(e,4800);
    check(sounded==render(pedal,4800)&&rms(sounded)>0,"the sustain keyswitch sounds its pedal and creates no string voices");
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
    // The pedal is one, so another channel's sustain switch sounds it; it
    // adds that sound alone and holds nothing on channel 1.
    keyra::Engine a,b,pedal;a.setParameters(dry());b.setParameters(dry());pedal.setParameters(dry());
    a.noteOn(14,.7f,2);pedal.noteOn(14,.7f,2);
    a.noteOn(60,.7f,1);b.noteOn(60,.7f,1);render(a,12000);render(b,12000);render(pedal,12000);a.noteOff(60);b.noteOff(60);
    const auto x=render(a,24000),y=render(b,24000),z=render(pedal,24000);double error=0;
    for(std::size_t i=0;i<x.size();++i)error=std::max(error,std::abs(static_cast<double>(x[i])-y[i]-z[i]));
    check(error<1e-6,"another channel's sustain switch cannot hold channel1 voices");
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
    // The body's knock rings on at its own decay whatever damps the strings,
    // the same in all three engines: `c` releases the key where `a` takes
    // CC1, so the differences from `c` hold only the strings. CC1 damps the
    // undamped strings too, which `c` leaves ringing above C4's partials.
    keyra::Engine a,b,c;a.setParameters(dry());b.setParameters(dry());c.setParameters(dry());
    a.noteOn(60,.7f);b.noteOn(60,.7f);c.noteOn(60,.7f);render(a,12000);render(b,12000);render(c,12000);
    a.controlChange(1,127);c.noteOff(60);render(a,24000);render(b,24000);render(c,24000);
    auto damped=render(a,12000),held=render(b,12000);const auto released=render(c,12000);
    for(std::size_t i=0;i<released.size();++i){damped[i]-=released[i];held[i]-=released[i];}
    check(c4Strings(damped)<c4Strings(held)*.001,"CC1 physically damps held strings smoothly");
    a.controlChange(120,0);check(rms(render(a,512))==0,"all sound off clears owned voices and shared residue when last channel stops");
  }
  {
    keyra::Engine a,b;a.setParameters(dry());auto p=dry();p.soft=1;b.setParameters(p);a.noteOn(72,.7f);b.noteOn(72,.7f);
    check(rms(render(b,24000))<rms(render(a,24000)),"soft pedal changes hammer excitation");
    // Both pedals go down and are reset alike, so both sound the pedal once.
    keyra::Engine c,d;c.setParameters(dry());d.setParameters(dry());c.controlChange(64,127);c.controlChange(66,127);c.controlChange(1,127);c.pitchBend(2);c.controlChange(121,0);
    d.controlChange(64,127);d.controlChange(121,0);
    c.noteOn(60,.7f);d.noteOn(60,.7f);check(render(c,24000)==render(d,24000),"reset all controllers restores channel playing state");
  }
  {
    // The board's noise keeps to its measured spectrum: at the top recorded
    // pitch, at every layer, every band clear of its partials and no more
    // than 10 dB under either neighbour sounds within 6 dB of its measured
    // level against the 2.5 kHz band, and at least four bands are compared.
    // (A deeper step is beyond what third-octave bands can draw. Whether a
    // band clears it turns on densities 100 dB under the note's peak, so a
    // layer's count moves by a band or two between fits.)
    // Second-order bands leaked 10-34 dB into the quiet bands above.
    // The components beside the series are measured apart from the noise:
    // as the fit measures it, a band leaves out the frequencies within 1.5
    // main-lobe half-widths of them and counts where a quarter remains. With
    // a few frequencies left, one frame's reading swung by 4 dB, so a band is
    // read at every bin through four half-overlapping frames, against the
    // measured density's mean over the same frames as both stages of the
    // ring decay (frames were brought back to the strike at the band's one
    // decay, which no longer holds where a second, slower stage takes over).
    namespace m=keyra::measured::grand;
    constexpr double pi=3.14159265358979323846,sr=48000;constexpr int n=2048,reference=4;
    const int anchor=static_cast<int>(m::anchors.size())-1,bandCount=static_cast<int>(m::noiseBands.size());
    const auto& a=m::anchors[anchor];const auto* bands=&m::noise[anchor*bandCount];
    constexpr int frames=4,hop=n/2;
    std::vector<double> w(n);double w2=0;for(int i=0;i<n;++i){w[i]=.5-.5*std::cos(2*pi*i/n);w2+=w[i]*w[i];}
    auto edge=[&](int b,double side){return m::noiseBands[b].hz*std::pow(2.,side/6);};
    auto stiff=[&](int order,float cents){return order*a.f1*std::sqrt((1+a.B*order*order)/(1+a.B))*std::pow(2.,cents/1200);};
    std::vector<double> beside;
    for(int k=a.extraFirst;k<a.extraFirst+a.extraCount;++k)beside.push_back(stiff(m::extras[k].order,m::extras[k].cents));
    // The undamped strings stay in: leaving out every one would leave the
    // 2.5 kHz reference under a quarter of its bins. Their prompt parts put
    // some up to 25 dB over their aftersound in these first 100 ms, so a band
    // centred below the note's fundamental, where they lie and none of its
    // own partials can, is read as the fit reads it: each frame's and
    // channel's median bin over ln 2 (a noise bin's power is exponential),
    // which passes over their tones.
    int fewest=bandCount;double worst=0;
    for(int layer=0;layer<m::layers;++layer){
      // At the layer's own velocity, not a player's spread about it.
      keyra::Engine e(sr);e.setParameters(dry());e.setSteadyStrikesForMeasurement(true);e.noteOn(a.note,m::layerVelocity[layer]/127.f);
      Audio left(n+(frames-1)*hop),right(n+(frames-1)*hop);e.process(left.data(),right.data(),n+(frames-1)*hop);
      auto rendered=[&](int b){std::vector<double> bins[frames][2];int all=0;
        for(double f=edge(b,-1)+50;f<edge(b,1)-50;f+=sr/n,++all){
          bool clear=true;for(double hz:beside)clear=clear&&std::abs(f-hz)>3*sr/n;
          if(!clear)continue;
          for(int frame=0;frame<frames;++frame)
            for(int c=0;c<2;++c){const Audio& x=c?right:left;double re=0,im=0;
              for(int i=0;i<n;++i){const double y=x[frame*hop+i]*w[i];re+=y*std::cos(2*pi*f*i/sr);im+=y*std::sin(2*pi*f*i/sr);}
              bins[frame][c].push_back(re*re+im*im);}}
        const std::size_t points=bins[0][0].size();
        if(points==0||4*static_cast<int>(points)<all)return std::numeric_limits<double>::quiet_NaN();
        const bool below=m::noiseBands[b].hz<a.f1;double sum=0;
        for(auto& frame:bins)for(auto& p:frame){
          if(below){std::nth_element(p.begin(),p.begin()+points/2,p.end());sum+=p[points/2]/std::log(2.);}
          else{for(double x:p)sum+=x/points;}}
        return 10*std::log10(sum/frames);};
      // A band's measured density, both stages, its mean over the frames as
      // they decay, and both channels' share of it.
      auto measuredDb=[&](int b){const auto& x=bands[b];double sum=0;
        const double first=std::pow(10.,x.densityDb[layer]/10),second=std::pow(10.,x.slowDensityDb[layer]/10);
        for(int frame=0;frame<frames;++frame)for(int i=0;i<n;++i){const double t=(frame*hop+i)/sr;
          sum+=w[i]*w[i]*(first*std::exp(-2*x.rate*t)+second*std::exp(-2*x.slowRate*t));}
        return 10*std::log10(sum/(frames*w2))+10*std::log10(std::pow(10.,-x.balanceDb/20)+std::pow(10.,x.balanceDb/20));};
      const double offset=rendered(reference)-measuredDb(reference);
      int compared=0;
      for(int b=0;b<bandCount;++b){
        bool partial=false,step=false;
        for(int k=a.first;k<a.first+a.count;++k){const double hz=stiff(m::partials[k].order,m::partials[k].cents);
          partial=partial||(hz>edge(b,-1)-100&&hz<edge(b,1)+100);}
        for(int k:{b-1,b+1})if(k>=0&&k<bandCount)step=step||measuredDb(k)-measuredDb(b)>10;
        const double level=rendered(b);
        if(partial||step||b==reference||std::isnan(level))continue;
        const double error=level-measuredDb(b)-offset;++compared;
        check(std::abs(error)<6,"board noise band follows its measured density where no partial sounds");
        worst=std::max(worst,std::abs(error));
      }
      fewest=std::min(fewest,compared);
    }
    std::cout<<"noise_bands_compared_fewest="<<fewest<<" worst_error_db="<<worst<<'\n';
    check(fewest>=4,"board noise spectrum compared in at least four bands at every layer");
  }
  {
    // A pitch between two recorded ones places each partial between their
    // stereo positions. The microphones can hear like partials of C3 and F#3
    // half a turn apart; blended as vectors, those cancelled a channel and put
    // D#3's fundamental 12 dB further left than either.
    std::array<std::array<double,4>,3> difference{};
    for(int key=0;key<3;++key){
      const int note=48+3*key;keyra::Engine e;e.setParameters(dry());e.noteOn(note,.7f);
      auto audio=render(e,52800);audio.erase(audio.begin(),audio.begin()+4800);
      const double f=440*std::pow(2.,(note-69)/12.);
      for(int k=0;k<4;++k)difference[key][k]=levelDifference(audio,(k+1)*f*.97,(k+1)*f*1.03);
    }
    for(int k=0;k<4;++k){
      const double low=std::min(difference[0][k],difference[2][k]),high=std::max(difference[0][k],difference[2][k]);
      check(difference[1][k]>low-3&&difference[1][k]<high+3,"an interpolated pitch's partials sit between its recorded neighbours' stereo positions");
      std::cout<<"partial="<<k+1<<" c3_level_difference_db="<<difference[0][k]<<" d#3="<<difference[1][k]<<" f#3="<<difference[2][k]<<'\n';
    }
  }
  {
    // A key between two recorded pitches plays about as loud as they do. Its
    // partials' lanes, blended one by one, beat and cancel where neither
    // pitch's do, which put the grand's B4 4 dB under both its neighbours.
    // Every such key on both pianos, at one layer coordinate, 50-750 ms.
    double worst=0;
    const auto scan=[&](keyra::Piano piano,const auto& anchors){
      auto p=dry();p.piano=piano;
      const auto early=[&](int note){keyra::Engine e;e.setParameters(p);e.setSteadyStrikesForMeasurement(true);e.noteOn(note,.7f);
        auto audio=render(e,36000);audio.erase(audio.begin(),audio.begin()+4800);return 20*std::log10(rms(audio));};
      for(std::size_t i=1;i<anchors.size();++i){
        const int low=anchors[i-1].note,high=anchors[i].note;const double a=early(low),b=early(high);
        for(int note=low+1;note<high;++note){const double x=early(note);
          worst=std::max({worst,std::min(a,b)-x,x-std::max(a,b)});}
      }
    };
    scan(keyra::Piano::grand,keyra::measured::grand::anchors);scan(keyra::Piano::upright,keyra::measured::upright::anchors);
    std::cout<<"between_pitches_outside_neighbours_db="<<worst<<'\n';
    check(worst<3,"a key between two recorded pitches plays within 3 dB of their levels");
  }
  {
    // A damped key struck and let go leaves the undamped strings ringing,
    // whatever the Resonance control: each at its own pitch whichever key
    // struck it, heard through its own measured pickup. Taken: the string
    // each of two recorded pitches below F6 sets ringing loudest, half a
    // second after the dampers fall.
    namespace m=keyra::measured::grand;
    constexpr int strings=static_cast<int>(m::haloStrings.size());
    for(const int recorded:{60,81}){
      int index=0;while(m::anchors[index].note!=recorded)++index;
      const float* levels=&m::haloLevels[index*strings];
      int j=0;for(int k=1;k<strings;++k)if(levels[k]>levels[j])j=k;
      keyra::Engine e;e.setParameters(dry());e.noteOn(recorded,m::layerVelocity[m::layers-1]/127.f);
      render(e,14400);e.noteOff(recorded);render(e,24000);
      const auto tail=render(e,48000);const double hz=haloHz(j);
      const double peak=spectralPeak(tail,hz-20,hz+20);
      check(std::abs(peak-hz)<.5,"an undamped string rings on at its own pitch after the struck key is let go");
      const auto& string=m::haloStrings[j];
      const double measured=20*std::log10(std::hypot(string.rightRe,string.rightIm)/string.left),played=levelDifference(tail,hz-1,hz+1);
      check(std::abs(played-measured)<.5,"an undamped string sounds through its measured stereo pickup");
      std::cout<<"struck="<<recorded<<" undamped_key="<<89+j<<" string_hz="<<hz<<" peak_hz="<<peak
               <<" right_over_left_db="<<played<<" measured_db="<<measured<<'\n';
    }
  }
  {
    // A strike starts without a click: from 8 kHz up (a fourth-order
    // Butterworth high-pass) the 5 ms after contact hold no more power than
    // 20 to 40 ms later. Measured so from their onsets, the grand's
    // recordings of A1, F#2, C4, C6 and F#5 stay at or under 0 dB at every
    // layer tried; the rises' corners, unsmoothed, reached 14 dB.
    auto click=[](const Audio& audio,std::size_t contact){
      constexpr double pi=3.14159265358979323846;
      std::array<std::array<double,5>,2> sections{};
      for(int k=0;k<2;++k){const double q=k?1.3065629648763766:.5411961001461970,w=2*pi*8000/48000;
        const double alpha=std::sin(w)/(2*q),c=std::cos(w),a0=1+alpha;
        sections[static_cast<std::size_t>(k)]={(1+c)/2/a0,-(1+c)/a0,(1+c)/2/a0,-2*c/a0,(1-alpha)/a0};}
      std::vector<double> power(audio.size()/2);
      for(std::size_t channel=0;channel<2;++channel){std::array<double,4> z{};
        for(std::size_t i=0;i<power.size();++i){double x=audio[2*i+channel];
          for(std::size_t k=0;k<2;++k){const auto& s=sections[k];
            const double y=s[0]*x+z[2*k];z[2*k]=s[1]*x-s[3]*y+z[2*k+1];z[2*k+1]=s[2]*x-s[4]*y;x=y;}
          power[i]+=x*x;}}
      auto mean=[&](std::size_t from,std::size_t to){double sum=0;for(std::size_t i=from;i<to;++i)sum+=power[i];return sum/static_cast<double>(to-from);};
      return 10*std::log10(mean(contact,contact+240)/mean(contact+960,contact+1920));};
    for(const auto& piano:{dry(),dryUpright()})for(const int key:{33,42,60,84})for(const float velocity:{31.f,61.f,101.f}){
      keyra::Engine e;e.setParameters(piano);e.noteOn(key,velocity/127);
      const double db=click(render(e,2400),0);
      check(db<3,"a strike starts without a click");
      std::cout<<"model="<<(piano.piano==keyra::Piano::upright?"upright":"grand")<<" key="<<key<<" velocity="<<velocity
               <<" onset_over_30ms_above_8khz_db="<<db<<'\n';
    }
  }
  {
    // A key let go knocks the body. From F6 up no damper falls, so the strings
    // ring on alike and what the key-up adds is the knock alone: building up
    // rather than clicking, and 2 dB quieter for each second longer the key
    // was held.
    auto knock=[](double heldSeconds){
      keyra::Engine a,b;a.setParameters(dry());b.setParameters(dry());a.noteOn(100,.7f);b.noteOn(100,.7f);
      const int held=static_cast<int>(heldSeconds*48000);render(a,held);render(b,held);
      a.noteOff(100);auto x=render(a,24000);const auto y=render(b,24000);
      for(std::size_t i=0;i<x.size();++i)x[i]-=y[i];
      return x;};
    const auto early=knock(.5),late=knock(2);
    float peak=0,start=0;for(std::size_t i=0;i<early.size();++i){peak=std::max(peak,std::abs(early[i]));if(i<96)start=std::max(start,std::abs(early[i]));}
    check(peak>1e-5f,"a key let go knocks the body");
    check(start<peak*.1f,"a release knock builds up over the action's rise");
    const double ratio=rms(late)/rms(early);
    check(std::abs(20*std::log10(ratio)+3)<.05,"a release knock fades 2 dB for each second the key was held");
    std::cout<<"release_knock_peak_dbfs="<<20*std::log10(peak)<<" held_2s_against_0.5s_db="<<20*std::log10(ratio)<<'\n';
  }
  {
    // Under the pedal a damper stays off the strings, so letting its key go
    // sounds nothing: the same as holding it.
    keyra::Engine a,b;a.setParameters(dry());b.setParameters(dry());a.controlChange(64,127);b.controlChange(64,127);
    a.noteOn(60,.7f);b.noteOn(60,.7f);render(a,12000);render(b,12000);a.noteOff(60);
    check(render(a,24000)==render(b,24000),"a key let go under the pedal knocks nothing");
  }
  {
    // The pedal sounds at the ends of its travel, once each way: going down
    // past .92 and coming back below .08, never as it moves between them. A
    // reset of the controllers lifts it silently.
    keyra::Engine a,b,c;a.setParameters(dry());b.setParameters(dry());c.setParameters(dry());
    a.controlChange(64,64);a.controlChange(64,100);check(rms(render(a,4800))==0,"half pedalling sounds nothing");
    a.controlChange(64,127);b.controlChange(64,127);c.controlChange(64,127);
    a.controlChange(64,30);a.controlChange(64,120);c.controlChange(121,0);
    const auto down=render(a,9600);
    check(down==render(b,9600)&&rms(down)>0,"the pedal sounds once going down, not as it moves within its travel");
    check(render(c,9600)==down,"a reset of the controllers lifts the pedal silently");
    a.controlChange(64,0);b.controlChange(64,0);c.controlChange(64,0);
    const auto up=render(a,9600);
    check(up==render(b,9600)&&up!=render(c,9600),"the pedal sounds once coming up, and not when already lifted");
  }
  {
    // Switching pianos silences what sounds at once: the grand's strings,
    // body and noise would not belong to the upright. An engine switched so
    // then plays as one that started on the upright.
    keyra::Engine a,b;a.setParameters(dry());b.setParameters(dryUpright());
    a.noteOn(60,.7f);a.noteOn(100,.7f);render(a,12000);a.noteOff(60);a.noteOff(100);render(a,2400);
    a.setParameters(dryUpright());
    check(rms(render(a,4800))==0,"switching pianos silences what sounds");
    a.noteOn(60,.7f);b.noteOn(60,.7f);
    check(render(a,24000)==render(b,24000),"a switched engine plays the upright as one that started on it");
  }
  {
    // The upright sounds its own measured pitch, not the grand's: taken at
    // C7, where the two pianos' tunings lie several hertz apart.
    const auto c7=[](const auto& anchors){for(const auto& x:anchors)if(x.note==96)return x.f1;return 0.f;};
    const double hz=c7(keyra::measured::upright::anchors),grandHz=c7(keyra::measured::grand::anchors);
    check(std::abs(hz-grandHz)>4,"the pianos' C7s lie far enough apart to tell which plays");
    keyra::Engine e;e.setParameters(dryUpright());e.noteOn(96,.7f);
    auto audio=render(e,52800);audio.erase(audio.begin(),audio.begin()+9600);
    const double peak=spectralPeak(audio,hz-12,hz+12);
    check(std::abs(peak-hz)<2,"the upright sounds its own measured C7");
    std::cout<<"upright_c7_hz="<<hz<<" grand_c7_hz="<<grandHz<<" peak_hz="<<peak<<'\n';
  }
  {
    // An upright key let go sounds the hammer noise recorded with it at one
    // level, however long the key was held, as the library plays it; from F6
    // up no damper falls, so the key-up adds that noise alone. The library
    // has no pedal recordings, so the pedal sounds nothing.
    auto knock=[](double heldSeconds){
      keyra::Engine a,b;a.setParameters(dryUpright());b.setParameters(dryUpright());a.noteOn(100,.7f);b.noteOn(100,.7f);
      const int held=static_cast<int>(heldSeconds*48000);render(a,held);render(b,held);
      a.noteOff(100);auto x=render(a,24000);const auto y=render(b,24000);
      for(std::size_t i=0;i<x.size();++i)x[i]-=y[i];
      return x;};
    const auto early=knock(.5),late=knock(2);
    check(rms(early)>1e-6,"an upright key let go knocks the body");
    check(std::abs(20*std::log10(rms(late)/rms(early)))<.05,"an upright release knock does not fade with the time held");
    keyra::Engine e;e.setParameters(dryUpright());e.controlChange(64,127);render(e,4800);e.controlChange(64,0);
    check(rms(render(e,9600))==0,"the upright's pedal sounds nothing");
  }
  {
    // The upright's felt holds a share of each partial only loosely
    // (measured::Damper), so C4's strings still ring half a second after the
    // key-up, falling on, where the grand's felt has taken them. At middle C
    // the share is 13 dB under the partial and falls about 6 dB/s.
    const auto fall=[](const keyra::Parameters& p,const auto& anchors){
      keyra::Engine e;e.setParameters(p);e.noteOn(60,.7f);render(e,60000);
      const double before=c4Strings(render(e,12000),anchors);e.noteOff(60);render(e,24000);
      const double half=c4Strings(render(e,12000),anchors);render(e,36000);
      return std::array<double,3>{before,half,c4Strings(render(e,12000),anchors)};};
    const auto upright=fall(dryUpright(),keyra::measured::upright::anchors),grand=fall(dry(),keyra::measured::grand::anchors);
    check(upright[1]>upright[0]*.03,"the upright's felt leaves a share of a released C4 ringing");
    check(upright[2]<upright[1]*.7,"what the upright's felt leaves keeps falling");
    check(grand[1]<grand[0]*.01,"the grand's felt takes all of a released C4");
    std::cout<<"upright_released_c4_db="<<20*std::log10(upright[1]/upright[0])<<','<<20*std::log10(upright[2]/upright[0])
             <<" grand_released_c4_db="<<20*std::log10(grand[1]/grand[0])<<'\n';
  }
  for(const auto piano:{keyra::Piano::grand,keyra::Piano::upright})for(const double rate:{8000.,22050.,44100.,48000.,96000.,192000.}){
    keyra::Engine e(rate);auto p=dry();p.piano=piano;p.brightness=std::numeric_limits<float>::quiet_NaN();p.tuning=std::numeric_limits<float>::infinity();e.setParameters(p);
    for(int note:{21,60,108})e.noteOn(note,1);
    for(float bend:{-48.f,0.f,48.f}){e.pitchBend(bend);const auto a=render(e,4000);for(float x:a)check(std::isfinite(x)&&std::abs(x)<=1,"rate/bend/nonfinite parameter output finite and bounded");}
  }
  for(const float composite:{377.55f,508.54f}){
    keyra::Engine a,b;auto pa=dry(),pb=dry();pa.tuning=composite;pb.tuning=composite<400?400:480;a.setParameters(pa);b.setParameters(pb);
    a.noteOn(72,.7f);b.noteOn(72,.7f);check(render(a,12000)!=render(b,12000),"host master tuning composes beyond UI endpoints without internal clamping");
  }
  for(const float concert:{300.f,600.f})for(const bool prepared:{false,true}){
    const auto tail=sympatheticTail(concert,prepared);
    const double peak=spectralPeak(tail,concert*.94,concert*1.06);
    check(rms(tail)>1e-7,"concert-tuning change preserves audible sympathetic state");
    check(std::abs(peak-concert)<.75,prepared?"prepare retains the current concert tuning in sympathetic radiation":"live concert tuning moves the sympathetic bank with the piano");
    std::cout<<"sympathetic_concert_hz="<<concert<<" after_prepare="<<prepared<<" measured_peak_hz="<<peak<<'\n';
  }
  {
    keyra::Engine a,b;keyra::Parameters p;p.sustain=1;p.resonance=1;a.setParameters(p);b.setParameters(p);
    a.noteOn(69,.7f);b.noteOn(69,.7f);render(a,12000);render(b,12000);
    p.tuning=415;a.setParameters(p);p.tuning=440;a.setParameters(p);
    check(render(a,12000)==render(b,12000),"concert-tuning round trip preserves live modal and sympathetic q/p states exactly");
  }
  {
    keyra::Engine e;std::array<float,64> l{},r{};trap=true;
    e.noteOn(60,.8f);e.noteOn(72,.8f,2);e.noteOff(60);e.noteOn(12,.7f);e.noteOn(13,.7f);e.noteOn(14,.7f);e.noteOff(12);e.controlChange(64,80);e.controlChange(66,127);e.controlChange(67,64);e.pitchBend(.5f);auto p=dry();p.tuning=415;e.setParameters(p);
    const auto pedals=e.pedalState();(void)pedals;
    for(int i=0;i<40;++i)e.process(l.data(),r.data(),64);
    p.piano=keyra::Piano::upright;e.setParameters(p);e.noteOn(48,.8f);e.noteOff(48);
    for(int i=0;i<40;++i)e.process(l.data(),r.data(),64);
    e.reset();e.controlChange(120,0);trap=false;
    check(allocations==0,"all live event/render/reset APIs allocate zero bytes");
  }
  // A fortissimo chord meets the output stage's limiter, never the emergency
  // bound ahead of it (4, +12 dBFS): read 24 dB down, where the stage passes
  // it untouched, its peak at the default Output stays 3 dB under the bound.
  for(const auto piano:{keyra::Piano::grand,keyra::Piano::upright})for(int count:{3,6,10}){
    keyra::Engine e;keyra::Parameters p;p.piano=piano;p.gain/=16;e.setParameters(p);e.reset();
    for(int i=0;i<count;++i)e.noteOn(36+i*7,1);
    const auto audio=render(e,48000);float peak=0;for(float x:audio)peak=std::max(peak,std::abs(x));
    peak*=16;
    check(peak<4*std::pow(10.f,-3/20.f),"fortissimo chord has headroom before the emergency bound");
    std::cout<<"headroom_piano="<<(piano==keyra::Piano::upright?"upright":"grand")<<" notes="<<count<<" peak_dbfs_before_stage="<<20*std::log10(peak)<<'\n';
  }
  std::cout<<"engine_failures="<<failures<<" live_allocations="<<allocations<<'\n';return failures?1:0;
}
