#include "keyra/Piano.h"
#include "keyra/Parameters.h"
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
struct Event { double time; std::string type; int note; double value; };
void u16(std::ostream& out, uint16_t n) { out.put(char(n)); out.put(char(n>>8)); }
void u32(std::ostream& out, uint32_t n) { u16(out,uint16_t(n)); u16(out,uint16_t(n>>16)); }
void wav(const std::string& path, const std::vector<float>& samples, uint32_t rate) {
  if(samples.size()>((uint64_t(1)<<32)-44)/4) throw std::runtime_error("WAV exceeds RIFF limit");
  std::ofstream out(path,std::ios::binary); if(!out) throw std::runtime_error("Cannot open WAV output");
  const auto bytes=uint32_t(samples.size()*4);
  out.write("RIFF",4); u32(out,36+bytes); out.write("WAVEfmt ",8); u32(out,16);
  u16(out,3); u16(out,2); u32(out,rate); u32(out,rate*8); u16(out,8); u16(out,32);
  out.write("data",4); u32(out,bytes);
  for(float sample:samples) { uint32_t bits; std::memcpy(&bits,&sample,4); u32(out,bits); }
  if(!out) throw std::runtime_error("Failed to write WAV");
}
double number(const std::string& text) {
  size_t used=0; double value=std::stod(text,&used);
  if(used!=text.size() || !std::isfinite(value)) throw std::runtime_error("Invalid number: "+text);
  return value;
}
keyra::ParamId parameter(const std::string& name) {
  const std::array<const char*,10> names={"instrument","material","mic","tone","dynamics","resonance","noise","distance","width","gain"};
  for(size_t i=0;i<names.size();++i) if(name==names[i]) return static_cast<keyra::ParamId>(i);
  throw std::runtime_error("Unknown parameter: "+name);
}
}
int main(int argc,char** argv) {
  try {
    uint32_t rate=48000; double seconds=4.5; int note=60; double velocity=61.;
    std::string output,eventsPath,reportPath;
    std::vector<std::pair<keyra::ParamId,double>> params;
    for(int i=1;i<argc;++i) {
      std::string arg=argv[i];
      if(arg=="--help") {
        std::cout<<"Keyra live modal renderer\n--output FILE.wav [--rate 48000] [--seconds 4.5]\n"
                   "[--note 60 --velocity 61] [--events FILE.events] [--report FILE.json]\n"
                   "[--param instrument=0] [--param material=0] [--param mic=0]\n"
                   "[--param tone=.5] [--param dynamics=.5] [--param resonance=.3]\n"
                   "[--param noise=.1] [--param distance=.15] [--param width=.7] [--param gain=-6]\n"
                   "Float WAV preserves dynamics; no normalization or limiter is applied.\n"; return 0;
      }
      if(i+1>=argc) throw std::runtime_error("Missing value for "+arg);
      std::string value=argv[++i];
      if(arg=="--output") output=value;
      else if(arg=="--events") eventsPath=value;
      else if(arg=="--report") reportPath=value;
      else if(arg=="--rate") { double n=number(value); if(n!=std::floor(n)||n<22050||n>192000) throw std::runtime_error("Rate must be 22050..192000"); rate=uint32_t(n); }
      else if(arg=="--seconds") seconds=number(value);
      else if(arg=="--note") { double n=number(value); if(n!=std::floor(n)||n<21||n>108) throw std::runtime_error("Note must be 21..108"); note=int(n); }
      else if(arg=="--velocity") velocity=number(value);
      else if(arg=="--param") { auto eq=value.find('='); if(eq==std::string::npos) throw std::runtime_error("Expected name=value"); params.emplace_back(parameter(value.substr(0,eq)),number(value.substr(eq+1))); }
      else throw std::runtime_error("Unknown argument: "+arg);
    }
    if(output.empty()||seconds<=0||seconds>600||velocity<=0||velocity>127) throw std::runtime_error("Specify output, duration in (0,600], velocity in (0,127]");
    std::vector<Event> events;
    if(eventsPath.empty()) events={{.05,"on",note,velocity}};
    else {
      std::ifstream in(eventsPath); if(!in) throw std::runtime_error("Cannot read events");
      std::string line;
      while(std::getline(in,line)) {
        if(line.empty()||line[0]=='#') continue;
        std::istringstream row(line); Event e{};
        if(!(row>>e.time>>e.type>>e.note>>e.value)||!std::isfinite(e.time)||!std::isfinite(e.value)||e.time<0) throw std::runtime_error("Invalid event line");
        if(e.type!="on"&&e.type!="off"&&e.type!="pedal") throw std::runtime_error("Invalid event type");
        if(e.type=="on"&&(e.value<=0||e.value>127)) throw std::runtime_error("Invalid event velocity");
        if(e.type=="pedal"&&(e.value<0||e.value>1)) throw std::runtime_error("Invalid pedal position");
        if(e.type!="pedal"&&(e.note<21||e.note>108)) throw std::runtime_error("Invalid event note");
        events.push_back(e);
      }
      std::stable_sort(events.begin(),events.end(),[](const Event&a,const Event&b){return a.time<b.time;});
    }
    keyra::Piano piano; piano.prepare(rate);
    for(auto item:params) piano.setParameter(item.first,item.second);
    const auto frames=uint64_t(std::ceil(seconds*rate));
    std::vector<float> result(size_t(frames)*2);
    std::array<float,64> left{},right{};
    size_t event=0; uint64_t cursor=0; double peak=0,power=0;
    const auto start=std::chrono::steady_clock::now();
    while(cursor<frames) {
      while(event<events.size()&&uint64_t(std::llround(events[event].time*rate))<=cursor) {
        const auto& e=events[event++];
        if(e.type=="on") piano.noteOn(e.note,e.value/127.);
        else if(e.type=="off") piano.noteOff(e.note);
        else piano.sustain(e.value);
      }
      uint64_t stop=std::min(cursor+64,frames);
      if(event<events.size()) stop=std::min(stop,uint64_t(std::llround(events[event].time*rate)));
      if(stop==cursor) continue;
      auto count=uint32_t(stop-cursor); piano.process(left.data(),right.data(),count);
      for(uint32_t i=0;i<count;++i) {
        if(!std::isfinite(left[i])||!std::isfinite(right[i])) throw std::runtime_error("Nonfinite engine output");
        result[2*(cursor+i)]=left[i]; result[2*(cursor+i)+1]=right[i];
        peak=std::max({peak,std::abs(double(left[i])),std::abs(double(right[i]))});
        power+=double(left[i])*left[i]+double(right[i])*right[i];
      }
      cursor=stop;
    }
    const double wall=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
    wav(output,result,rate);
    std::ostringstream report;
    report<<"{\n  \"sample_rate\": "<<rate<<",\n  \"frames\": "<<frames<<",\n  \"peak\": "<<peak
          <<",\n  \"rms\": "<<std::sqrt(power/(2*frames))<<",\n  \"wall_seconds\": "<<wall
          <<",\n  \"wall_seconds_per_audio_second\": "<<wall/(double(frames)/rate)<<",\n  \"parameters\": [";
    for(size_t i=0;i<10;++i) report<<(i?", ":"")<<piano.parameter(static_cast<keyra::ParamId>(i));
    report<<"]\n}\n";
    if(!reportPath.empty()) { std::ofstream out(reportPath); out<<report.str(); if(!out) throw std::runtime_error("Cannot write report"); }
    std::cout<<report.str();
  } catch(const std::exception& e) { std::cerr<<"keyra_preview_render: "<<e.what()<<'\n'; return 1; }
}
