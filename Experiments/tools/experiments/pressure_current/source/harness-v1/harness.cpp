#include "keyra/FullInstrument.h"
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <string>
#include <vector>
#if KEYRA_FUSION_CORRECTNESS
#include "ObserverCapture.h"
extern "C" bool keyra_pressure_snapshot(const keyra::FullInstrument*,const char*);
#endif
extern "C" bool keyra_fusion_prepare_report(const keyra::FullInstrument*,const char*);

struct Event {unsigned frame;char kind;int note;double value;};
using Clock=std::chrono::steady_clock;
uint64_t threadNow(){timespec t{};clock_gettime(CLOCK_THREAD_CPUTIME_ID,&t);return uint64_t(t.tv_sec)*1000000000u+uint64_t(t.tv_nsec);}
double elapsed(Clock::time_point t){return std::chrono::duration<double>(Clock::now()-t).count();}
bool dispatch(keyra::FullInstrument& p,const Event& e){
  if(e.kind=='p')return p.sustain(e.value);
  if(e.kind=='+')return p.noteOn(e.note,e.value);
  if(e.kind=='r'){p.reset();return true;}
  return p.noteOff(e.note);
}
std::array<std::vector<Event>,3> budgetScores(){
  std::vector<Event> music{{0,'p',0,1},{0,'+',36,.5},{0,'+',60,.73},{0,'+',67,.64},
    {1024,'-',60,0},{2048,'+',64,.69},{8192,'-',36,0},{10240,'+',72,.63},
    {16384,'p',0,.4},{24576,'p',0,0},{25600,'-',64,0},{25600,'-',67,0},{25600,'-',72,0}};
  std::vector<Event> repeats{{0,'p',0,1},{0,'+',60,.7},{256,'+',60,.7},{512,'+',60,.7},
    {768,'+',60,.7},{1024,'+',60,.7},{2048,'-',60,0},{3072,'+',60,.7},
    {4096,'-',60,0},{5120,'+',60,.7},{6144,'-',60,0},{8192,'+',60,.7},
    {10240,'-',60,0},{12288,'p',0,.5},{14336,'+',60,.7},{16384,'-',60,0},
    {18432,'+',60,.7},{20480,'-',60,0},{24576,'p',0,0}};
  std::vector<Event> dense{{0,'p',0,1}};
  for(int note=21;note<=108;++note)dense.push_back({0,'+',note,.7});
  for(int note=21;note<=108;++note)dense.push_back({512,'-',note,0});
  dense.push_back({8192,'p',0,0});return {{music,repeats,dense}};
}
std::vector<Event> correctnessScore(unsigned c,unsigned rate){
  if(c==3)return {{unsigned(std::llround(.03*rate))+7,'+',48,.73},
    {unsigned(std::llround(.07*rate))+11,'+',48,.61},
    {unsigned(std::llround(.10*rate))+3,'-',48,0},
    {unsigned(std::llround(.15*rate))+5,'p',0,.6},
    {unsigned(std::llround(.20*rate)),'r',0,0},
    {unsigned(std::llround(.24*rate))+13,'+',84,.57},
    {unsigned(std::llround(.30*rate))+17,'-',84,0}};
  auto events=budgetScores()[c];
  for(size_t i=0;i<events.size();++i){
    events[i].frame=unsigned(std::llround(events[i].frame*double(rate)/48000));
    if(events[i].kind!='p')events[i].frame+=1+unsigned(i%5)*3;
  }
  std::stable_sort(events.begin(),events.end(),[](const auto& a,const auto& b){return a.frame<b.frame;});return events;
}
bool writeAudio(const std::string& path,const std::vector<float>& l,const std::vector<float>& r){
  FILE* f=std::fopen(path.c_str(),"wb");if(!f)return false;
  bool ok=std::fwrite(l.data(),sizeof(float),l.size(),f)==l.size()&&std::fwrite(r.data(),sizeof(float),r.size(),f)==r.size();
  return std::fclose(f)==0&&ok;
}
double percentile(std::vector<double> x,double p){std::sort(x.begin(),x.end());return x[size_t(std::ceil(p*(x.size()-1)))];}
void array(const char* key,const std::vector<double>& a){std::printf(",\"%s\":[",key);for(size_t i=0;i<a.size();++i){if(i)std::printf(",");std::printf("%.17g",a[i]);}std::printf("]");}
int main(int argc,char** argv){
  if(argc!=3)return 2;const unsigned rate=unsigned(std::strtoul(argv[1],nullptr,10));const std::string dir=argv[2];
  if(rate!=44100&&rate!=48000&&rate!=88200&&rate!=96000)return 2;
  const std::array<const char*,4> names{{"music","repeats-pedal","dense-88-tail","silent-reset"}};
  std::printf("{\"sample_rate\":%u,\"cases\":[",rate);
  const unsigned cases=KEYRA_FUSION_CORRECTNESS?4:3;
  for(unsigned c=0;c<cases;++c){
    keyra::FullInstrument p;keyra::FullInstrumentConfig config;config.sampleRate=rate;config.seed=0x4b657972u;
    const auto prepareStart=Clock::now();if(!p.prepare(config))return 3;const double prepareWall=elapsed(prepareStart);
    if(!keyra_fusion_prepare_report(&p,(dir+"/"+names[c]+".prepare.json").c_str()))return 4;
    const std::array<unsigned,3> budgetFrames{{30720,30720,15360}};
    const unsigned frames=KEYRA_FUSION_CORRECTNESS?unsigned(std::llround(rate*(c<2?.64:.4))):budgetFrames[c];
    const auto events=KEYRA_FUSION_CORRECTNESS?correctnessScore(c,rate):budgetScores()[c];
    std::vector<float> left(frames),right(frames);std::vector<double> cpus,walls;std::vector<unsigned> dispatches;
    cpus.reserve((frames+63)/64);walls.reserve((frames+63)/64);dispatches.reserve((frames+63)/64);
    size_t next=0;unsigned position=0;std::vector<unsigned> checkpoints{64,512,4096,8192,frames};
    if(c==3){unsigned reset=unsigned(std::llround(.20*rate));checkpoints={64,4096,reset,reset+64,frames};}
    size_t check=0;unsigned dispatched=0;
#if KEYRA_FUSION_CORRECTNESS
    keyra_fusion_capture::reset();
    while(true){
      while(next<events.size()&&events[next].frame==position){if(!dispatch(p,events[next++]))return 5;++dispatched;}
      if(check<checkpoints.size()&&position==checkpoints[check]){
        const auto path=dir+"/"+names[c]+"-"+std::to_string(position)+".state";
        if(!keyra_pressure_snapshot(&p,path.c_str()))return 6;++check;
      }
      if(position==frames)break;
      unsigned end=std::min(frames,(position/64+1)*64);
      if(next<events.size())end=std::min(end,events[next].frame);
      if(check<checkpoints.size())end=std::min(end,checkpoints[check]);
      if(end<=position||!p.process(left.data()+position,right.data()+position,end-position))return 7;position=end;
    }
    if(keyra_fusion_capture::overflow||keyra_fusion_capture::cursor!=frames||check!=5)return 8;
    FILE* raw=std::fopen((dir+"/"+names[c]+".f64le-pressure").c_str(),"wb");if(!raw)return 9;
    if(std::fwrite(keyra_fusion_capture::pressure.data(),sizeof(double),2*frames,raw)!=2*frames||std::fclose(raw))return 9;
#else
    for(position=0;position<frames;position+=64){
      const auto wall0=Clock::now();const auto cpu0=threadNow();unsigned count=0;
      while(next<events.size()&&events[next].frame==position){if(!dispatch(p,events[next++]))return 5;++count;}
      if(!p.process(left.data()+position,right.data()+position,64))return 7;
      const double cpu=double(threadNow()-cpu0)*1e-9,wall=elapsed(wall0);
      cpus.push_back(cpu);walls.push_back(wall);dispatches.push_back(count);dispatched+=count;
    }
#endif
    const auto d=p.diagnostics();
    if(next!=events.size()||d.faultFlags||d.unsafeLaunches||d.nonfiniteOutputFaults||d.stringCount!=230||d.stringModes!=17778||d.boardModes!=475)return 10;
    for(unsigned i=0;i<frames;++i)if(!std::isfinite(left[i])||!std::isfinite(right[i]))return 11;
    if(!writeAudio(dir+"/"+names[c]+".f32le-planar",left,right))return 12;
    if(c)std::printf(",");
    std::printf("{\"name\":\"%s\",\"frames\":%u,\"audio_seconds\":%.17g,\"prepare_wall_seconds_excluded\":%.17g,\"events_dispatched\":%u,\"faults\":%u,\"unsafe_launches\":%llu,\"requests\":%llu,\"launches\":%llu,\"deferred\":%llu,\"coalesced\":%llu,\"cancelled\":%llu,\"expired\":%llu,\"events\":[",names[c],frames,frames/double(rate),prepareWall,dispatched,d.faultFlags,(unsigned long long)d.unsafeLaunches,(unsigned long long)d.requests,(unsigned long long)d.launches,(unsigned long long)d.deferred,(unsigned long long)d.coalesced,(unsigned long long)d.cancelled,(unsigned long long)d.expired);
    for(size_t i=0;i<events.size();++i){if(i)std::printf(",");const auto& e=events[i];std::printf("{\"frame\":%u,\"kind\":\"%c\",\"note\":%d,\"value\":%.17g}",e.frame,e.kind,e.note,e.value);}std::printf("]");
#if KEYRA_FUSION_CORRECTNESS
    std::printf(",\"physical_state_checkpoints\":[");for(size_t i=0;i<checkpoints.size();++i){if(i)std::printf(",");std::printf("%u",checkpoints[i]);}std::printf("]");
#else
    double cpuSum=0;for(double value:cpus)cpuSum+=value;
    const double deadline=64./rate;unsigned misses=0;for(double value:walls)if(value>deadline)++misses;
    std::printf(",\"callback_cpu_seconds\":%.17g,\"cpu_seconds_per_audio_second\":%.17g,\"wall_deadline_misses\":%u,\"callback_cpu_p50\":%.17g,\"callback_cpu_p95\":%.17g,\"callback_cpu_max\":%.17g,\"callback_wall_p50\":%.17g,\"callback_wall_p95\":%.17g,\"callback_wall_max\":%.17g",cpuSum,cpuSum/(frames/double(rate)),misses,percentile(cpus,.50),percentile(cpus,.95),*std::max_element(cpus.begin(),cpus.end()),percentile(walls,.50),percentile(walls,.95),*std::max_element(walls.begin(),walls.end()));
    array("callback_thread_cpu_seconds",cpus);array("callback_wall_seconds",walls);
    std::printf(",\"events_per_callback\":[");for(size_t i=0;i<dispatches.size();++i){if(i)std::printf(",");std::printf("%u",dispatches[i]);}std::printf("]");
#endif
    std::printf("}");
  }
  std::printf("]}\n");return 0;
}
