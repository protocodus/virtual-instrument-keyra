#include "keyra/Piano.h"
#include "keyra/Parameters.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <string>
#include <vector>

// Includes note events in the callback budget. Timing is diagnostic: shared
// development hosts cannot certify a Reason rack's real-time deadline.
namespace {
bool parityStream(const char* path) {
  std::ofstream out(path, std::ios::binary);
  if (!out) return false;
  std::array<float,257> left{}, right{};
  for (int rate : {44100,48000,88200,96000}) {
    keyra::Piano piano;
    if (!piano.prepare(rate)) return false;
    for (int i=0;i<120;++i) {
      if (i%9==0) piano.setParameter(keyra::ParamId::Instrument,(i/9)%4);
      if (i%7==0) piano.setParameter(keyra::ParamId::Material,(i/7)%3);
      if (i%5==0) piano.setParameter(keyra::ParamId::Tone,(i%17)/16.);
      if (i%11==0) piano.setParameter(keyra::ParamId::Dynamics,(i%13)/12.);
      if (i%3==0) piano.sustain((i%5)/4.);
      piano.noteOn(21+(i*7)%88,((i*11)%127+1)/127.,i%16,i);
      if (i%2==0) piano.noteOff(21+((i+82)*7)%88,(i+82)%16,i+82);
      piano.process(left.data(),right.data(),257);
      out.write(reinterpret_cast<const char*>(left.data()),sizeof(left));
      out.write(reinterpret_cast<const char*>(right.data()),sizeof(right));
    }
  }
  return bool(out);
}
}

int main(int argc,char** argv) {
  if (argc==3 && std::string(argv[1])=="--parity-stream")
    return parityStream(argv[2]) ? 0 : 1;
  if (argc!=1) {
    std::cerr<<"Usage: keyra_attack_performance [--parity-stream OUTPUT.f32]\n";
    return 1;
  }
  constexpr int iterations=400, warmup=20;
  constexpr unsigned block=64;
  std::cout<<std::setprecision(10)
           <<"{\n  \"schema_version\": 1,\n"
           <<"  \"scenario\": \"Simultaneous fresh note attacks and one 64-frame render; reset excluded from timing\",\n"
           <<"  \"timing_is_diagnostic_not_a_test_gate\": true,\n"
           <<"  \"iterations_per_case\": "<<iterations<<",\n"
           <<"  \"cases\": [\n";
  bool first=true;
  for (int rate : {48000,96000}) for (int notes : {10,32,64}) {
    keyra::Piano piano;
    if (!piano.prepare(rate)) return 1;
    std::array<float,block> left{},right{};
    std::vector<double> times(iterations);
    double checksum=0;
    const double deadlineUs=1.e6*block/rate;
    for (int pass=-warmup;pass<iterations;++pass) {
      piano.reset();
      const auto start=std::chrono::steady_clock::now();
      for (int i=0;i<notes;++i)
        piano.noteOn(notes==10 ? 40+(i*5)%43 : 21+i,.2+.6*(i%7)/6.,0,i);
      piano.process(left.data(),right.data(),block);
      const auto stop=std::chrono::steady_clock::now();
      if (pass>=0) times[pass]=std::chrono::duration<double,std::micro>(stop-start).count();
      for (unsigned frame=0;frame<block;++frame) {
        if (!std::isfinite(left[frame]) || !std::isfinite(right[frame])) return 1;
      }
      checksum+=left[60]+right[63];
    }
    std::sort(times.begin(),times.end());
    double mean=0; unsigned misses=0;
    for (double time : times) { mean+=time/times.size(); if(time>deadlineUs)++misses; }
    if (!first) std::cout<<",\n";
    first=false;
    std::cout<<"    {\"sample_rate\": "<<rate<<", \"notes\": "<<notes
             <<", \"frames\": "<<block<<", \"deadline_us\": "<<deadlineUs
             <<", \"mean_us\": "<<mean<<", \"median_us\": "<<times[times.size()/2]
             <<", \"p95_us\": "<<times[static_cast<std::size_t>(std::ceil(.95*times.size()))-1]
             <<", \"maximum_us\": "<<times.back()<<", \"deadline_exceedances\": "<<misses
             <<", \"output_checksum\": "<<checksum<<"}";
  }
  std::cout<<"\n  ]\n}\n";
}
