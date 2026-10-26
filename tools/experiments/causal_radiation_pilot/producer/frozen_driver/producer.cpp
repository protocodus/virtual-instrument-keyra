
#include "keyra/FullInstrument.h"
#include <cstdio>
#include <cmath>
#include <cstdlib>
#include <string>
#include <vector>
extern "C" void causal_capture_begin(unsigned,int);
extern "C" bool causal_capture_write(const char*);
extern "C" uint64_t causal_capture_mismatches();extern "C" uint64_t causal_capture_faults();
int main(int argc,char**argv){if(argc!=4)return 2;const std::string dir=argv[1];const int note=std::atoi(argv[2]);const double velocity=std::strtod(argv[3],nullptr);constexpr unsigned frames=182400;
 causal_capture_begin(frames,note);keyra::FullInstrumentConfig config;config.sampleRate=48000;config.seed=123456;config.repetitionController=false;config.parameters.humanization=0;config.parameters.mechanicalLevel=0;config.parameters.gainDb=0;config.parameters.stereoWidth=1;
 keyra::FullInstrument piano;if(!piano.prepare(config))return 3;std::vector<float>l(frames),r(frames);
 for(unsigned first=0;first<frames;first+=64){if(first==4800&&!piano.noteOn(note,velocity/127.))return 4;if(!piano.process(l.data()+first,r.data()+first,64))return 5;}
 FILE*f=std::fopen((dir+"/baseline.f32le").c_str(),"wb");if(!f)return 6;for(unsigned i=0;i<frames;++i){const float x[2]={l[i],r[i]};if(!std::isfinite(x[0])||!std::isfinite(x[1])||std::fwrite(x,sizeof(float),2,f)!=2)return 7;}std::fclose(f);
 if(!causal_capture_write(dir.c_str()))return 8;const auto d=piano.diagnostics();const auto mismatch=causal_capture_mismatches(),fault=causal_capture_faults();
 std::printf("{\"frames\":182400,\"sample_rate\":48000,\"midi\":%d,\"velocity\":%.17g,\"note_on_frame\":4800,\"launches\":%llu,\"original_fault_flags\":%u,\"parity_mismatches\":%llu,\"new_observer_faults\":%llu}\n",note,velocity,(unsigned long long)d.launches,d.faultFlags,(unsigned long long)mismatch,(unsigned long long)fault);
 return d.faultFlags||d.launches!=1||d.unsafeLaunches||mismatch||fault?9:0;}
