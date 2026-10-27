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
