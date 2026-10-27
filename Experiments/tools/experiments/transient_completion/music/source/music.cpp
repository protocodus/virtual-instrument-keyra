
#include "keyra/FullInstrument.h"
#include <algorithm>
#include <cmath>
#include <cstdio>
#include <ctime>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
extern "C" void causal_capture_begin(unsigned,int);extern "C" bool causal_capture_write(const char*);
extern "C" bool causal_capture_coefficients_match(const char*,const char*);
extern "C" uint64_t causal_capture_mismatches();extern "C" uint64_t causal_capture_faults();
struct Event{uint64_t frame;std::string kind;int note;double value;};
int main(int argc,char**argv){if(argc!=4)return 2;const std::string dir=argv[1];std::ifstream input(argv[2]);if(!input)return 3;
 std::vector<Event> events;std::string line;while(std::getline(input,line)){const auto c=line.find('#');if(c!=std::string::npos)line.resize(c);std::istringstream row(line);double time;Event e;if(!(row>>time>>e.kind>>e.note>>e.value))continue;e.frame=uint64_t(std::llround(time*48000.));events.push_back(e);}
 std::stable_sort(events.begin(),events.end(),[](const auto&a,const auto&b){return a.frame<b.frame;});constexpr unsigned frames=432000;causal_capture_begin(frames,48);
 keyra::FullInstrumentConfig config;config.sampleRate=48000;config.seed=123456;config.repetitionController=false;config.parameters.humanization=0;config.parameters.mechanicalLevel=0;config.parameters.gainDb=0;config.parameters.stereoWidth=1;
 keyra::FullInstrument piano;if(!piano.prepare(config))return 4;if(!causal_capture_coefficients_match(argv[3],dir.c_str()))return 11;std::vector<float>l(frames),r(frames);unsigned cursor=0;size_t next=0;const auto cpuStart=std::clock();
 while(cursor<frames){while(next<events.size()&&events[next].frame==cursor){const auto&e=events[next++];bool ok=false;if(e.kind=="on")ok=piano.noteOn(e.note,e.value/127.);else if(e.kind=="off")ok=piano.noteOff(e.note);else if(e.kind=="pedal")ok=piano.sustain(e.value);if(!ok)return 5;}
  unsigned end=std::min(frames,cursor+64);if(next<events.size())end=unsigned(std::min(uint64_t(end),events[next].frame));if(end<=cursor||!piano.process(l.data()+cursor,r.data()+cursor,end-cursor))return 6;cursor=end;}
 const double cpu=double(std::clock()-cpuStart)/CLOCKS_PER_SEC;FILE*f=std::fopen((dir+"/baseline.f32le").c_str(),"wb");if(!f)return 7;for(unsigned i=0;i<frames;++i){const float pair[2]={l[i],r[i]};if(!std::isfinite(pair[0])||!std::isfinite(pair[1])||std::fwrite(pair,sizeof(float),2,f)!=2)return 8;}std::fclose(f);
 if(!causal_capture_write(dir.c_str()))return 9;const auto d=piano.diagnostics();const auto mismatches=causal_capture_mismatches(),faults=causal_capture_faults();
 std::printf("{\"sample_rate\":48000,\"frames\":432000,\"seed\":123456,\"events_applied\":%zu,\"requests\":%llu,\"launches\":%llu,\"original_fault_flags\":%u,\"parity_mismatches\":%llu,\"new_observer_faults\":%llu,\"process_cpu_seconds_diagnostic\":%.17g}\n",next,(unsigned long long)d.requests,(unsigned long long)d.launches,d.faultFlags,(unsigned long long)mismatches,(unsigned long long)faults,cpu);
 return d.faultFlags||d.requests!=11||d.launches!=11||mismatches||faults?10:0;}
