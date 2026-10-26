#include "keyra/FullInstrument.h"
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <ctime>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#ifndef KEYRA_RENDER_PRESSURE_SIMD
#define KEYRA_RENDER_PRESSURE_SIMD 0
#endif

namespace {
struct Event { uint64_t frame=0; std::string type; int note=0; double value=0; };
double number(const std::string& text) {
  size_t used=0; const double value=std::stod(text,&used);
  if(used!=text.size()||!std::isfinite(value)) throw std::runtime_error("Invalid number: "+text);
  return value;
}
uint64_t integer(const std::string& text,uint64_t minimum,uint64_t maximum) {
  const double value=number(text);
  if(value<std::ldexp(1.,64)&&value>=double(minimum)&&value<=double(maximum)&&value==std::floor(value))
    return static_cast<uint64_t>(value);
  throw std::runtime_error("Integer outside supported range: "+text);
}
uint64_t frameAt(double seconds,uint32_t rate) {
  const double value=seconds*rate;
  if(seconds<0||!std::isfinite(value)||value>=double(std::numeric_limits<int64_t>::max()))
    throw std::runtime_error("Event timestamp outside supported range");
  return static_cast<uint64_t>(std::llround(value));
}
void u16(std::ostream& out,uint16_t value) { out.put(char(value));out.put(char(value>>8)); }
void u32(std::ostream& out,uint32_t value) { u16(out,uint16_t(value));u16(out,uint16_t(value>>16)); }
void wav(const std::string& path,const std::vector<float>& audio,uint32_t rate) {
  if(audio.size()>(uint64_t(UINT32_MAX)-36)/4) throw std::runtime_error("WAV exceeds RIFF limit");
  std::ofstream out(path,std::ios::binary);if(!out) throw std::runtime_error("Cannot open WAV output");
  const auto bytes=static_cast<uint32_t>(audio.size()*4);
  out.write("RIFF",4);u32(out,36+bytes);out.write("WAVEfmt ",8);u32(out,16);
  u16(out,3);u16(out,2);u32(out,rate);u32(out,rate*8);u16(out,8);u16(out,32);
  out.write("data",4);u32(out,bytes);
  for(float sample:audio) { uint32_t bits;std::memcpy(&bits,&sample,4);u32(out,bits); }
  if(!out) throw std::runtime_error("Failed to write WAV");
}
void parameter(keyra::FullInstrumentParameters& p,const std::string& text) {
  const auto eq=text.find('=');if(eq==std::string::npos) throw std::runtime_error("Expected name=value");
  const auto name=text.substr(0,eq);const double value=number(text.substr(eq+1));
  if(name=="dynamics")p.dynamics=value;
  else if(name=="humanization")p.humanization=value;
  else if(name=="mechanicalLevel")p.mechanicalLevel=value;
  else if(name=="width")p.stereoWidth=value;
  else if(name=="gain")p.gainDb=value;
  else throw std::runtime_error("Unknown full-model parameter: "+name);
}
std::vector<Event> readEvents(const std::string& path,uint32_t rate) {
  std::ifstream in(path);if(!in)throw std::runtime_error("Cannot open event score");
  std::vector<Event> result;std::string line;unsigned lineNumber=0;
  while(std::getline(in,line)) {
    ++lineNumber;const auto comment=line.find('#');if(comment!=std::string::npos)line.resize(comment);
    std::istringstream row(line);row>>std::ws;if(row.eof())continue;
    double time=0;Event event;std::string extra;
    if(!(row>>time>>event.type>>event.note>>event.value)||row>>extra||!std::isfinite(time)||!std::isfinite(event.value))
      throw std::runtime_error("Invalid score line "+std::to_string(lineNumber));
    event.frame=frameAt(time,rate);
    if(event.type=="on"||event.type=="off") {
      if(event.note<21||event.note>108||event.value<0||event.value>127)
        throw std::runtime_error("Invalid note/velocity on score line "+std::to_string(lineNumber));
    } else if(event.type=="pedal") {
      if(event.value<0||event.value>1)throw std::runtime_error("Pedal position must be within 0..1");
    } else throw std::runtime_error("Unknown score event: "+event.type);
    result.push_back(event);
  }
  if(in.bad())throw std::runtime_error("Failed while reading event score");
  std::stable_sort(result.begin(),result.end(),[](const Event& a,const Event& b){return a.frame<b.frame;});
  return result;
}
}

int main(int argc,char** argv) {
  try {
    keyra::FullInstrumentConfig config;
    uint32_t block=64;double seconds=4.5,velocity=61.;int note=60;
    std::string output,score,reportPath;
    for(int i=1;i<argc;++i) {
      const std::string arg=argv[i];
      if(arg=="--help") {
        std::cout<<"Keyra full physical renderer (offline; no realtime claim)\n"
          "--output FILE.wav [--rate 48000 --seconds 4.5 --block 64 --seed UINT32]\n"
          "[--note 60 --velocity 61] [--events FILE.events --report FILE.json]\n"
          "[--param dynamics=.5 --param humanization=.65 --param mechanicalLevel=.025]\n"
          "[--param width=1 --param gain=0]\n"
          "[--mechanism-body 1 --mechanism-direct 1 --repetition 1]\n"
          "Score: seconds on/off MIDI velocity(0..127), or seconds pedal 0 position(0..1).\n"
          "Note-on velocity zero releases. Same-frame events preserve file order.\n"
          "One physical keyboard/global pedal; no recorded audio, room, limiter or normalization.\n";
        return 0;
      }
      if(i+1>=argc)throw std::runtime_error("Missing value for "+arg);
      const std::string value=argv[++i];
      if(arg=="--output")output=value;
      else if(arg=="--events")score=value;
      else if(arg=="--report")reportPath=value;
      else if(arg=="--rate")config.sampleRate=double(integer(value,44100,96000));
      else if(arg=="--seconds")seconds=number(value);
      else if(arg=="--block")block=static_cast<uint32_t>(integer(value,1,4096));
      else if(arg=="--seed")config.seed=static_cast<uint32_t>(integer(value,0,UINT32_MAX));
      else if(arg=="--note")note=static_cast<int>(integer(value,21,108));
      else if(arg=="--velocity")velocity=number(value);
      else if(arg=="--param")parameter(config.parameters,value);
      else if(arg=="--mechanism-body")config.mechanismBodyCoupling=integer(value,0,1)!=0;
      else if(arg=="--mechanism-direct")config.mechanismObservation=integer(value,0,1)!=0;
      else if(arg=="--repetition")config.repetitionController=integer(value,0,1)!=0;
      else throw std::runtime_error("Unknown argument: "+arg);
    }
    if(output.empty()||seconds<=0||seconds>600||velocity<0||velocity>127)
      throw std::runtime_error("Specify output, duration in (0,600], velocity in [0,127]");
    const auto rate=static_cast<uint32_t>(config.sampleRate);
    const auto total=static_cast<uint64_t>(std::ceil(seconds*rate));
    auto events=score.empty()?std::vector<Event>{{frameAt(.05,rate),"on",note,velocity}}:readEvents(score,rate);
    keyra::FullInstrument piano;if(!piano.prepare(config))throw std::runtime_error("Invalid full-model configuration");
    std::vector<float> audio(static_cast<size_t>(total)*2),left(block),right(block);
    size_t next=0;uint64_t cursor=0,rejected=0;double peak=0,power=0;
    const auto start=std::chrono::steady_clock::now();const auto cpu=std::clock();
    while(cursor<total) {
      while(next<events.size()&&events[next].frame<=cursor) {
        const auto& event=events[next++];bool accepted=false;
        if(event.type=="on")accepted=piano.noteOn(event.note,event.value/127.);
        else if(event.type=="off")accepted=piano.noteOff(event.note);
        else accepted=piano.sustain(event.value);
        if(!accepted)++rejected;
      }
      uint64_t stop=std::min(cursor+block,total);
      if(next<events.size())stop=std::min(stop,events[next].frame);
      if(stop<=cursor)throw std::runtime_error("Score dispatcher made no progress");
      const auto count=static_cast<uint32_t>(stop-cursor);
      if(!piano.process(left.data(),right.data(),count))throw std::runtime_error("Full-model block rejected");
      for(uint32_t i=0;i<count;++i) {
        if(!std::isfinite(left[i])||!std::isfinite(right[i]))throw std::runtime_error("Nonfinite output");
        audio[2*(cursor+i)]=left[i];audio[2*(cursor+i)+1]=right[i];
        peak=std::max({peak,std::abs(double(left[i])),std::abs(double(right[i]))});
        power+=double(left[i])*left[i]+double(right[i])*right[i];
      }
      cursor=stop;
    }
    const double processCpu=double(std::clock()-cpu)/CLOCKS_PER_SEC;
    const double wall=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
    wav(output,audio,rate);const auto d=piano.diagnostics();const auto p=piano.parameters();
    std::ostringstream report;report<<std::setprecision(17)<<"{\n"
      "  \"engine\": \"FullInstrument, original control calibration\",\n"
      "  \"sample_rate\": "<<rate<<",\n  \"frames\": "<<total<<",\n  \"block_frames\": "<<block<<",\n  \"seed\": "<<config.seed
      <<",\n  \"pressure_simd\": "<<(KEYRA_RENDER_PRESSURE_SIMD?"true":"false")
      <<",\n  \"peak\": "<<peak<<",\n  \"rms\": "<<std::sqrt(power/(2*total))
      <<",\n  \"render_wall_seconds\": "<<wall<<",\n  \"render_process_cpu_seconds\": "<<processCpu
      <<",\n  \"events_applied\": "<<next<<",\n  \"events_after_render\": "<<events.size()-next
      <<",\n  \"events_rejected\": "<<rejected<<",\n  \"requests\": "<<d.requests<<",\n  \"launches\": "<<d.launches
      <<",\n  \"deferred_requests\": "<<d.deferred<<",\n  \"coalesced\": "<<d.coalesced
      <<",\n  \"cancelled\": "<<d.cancelled<<",\n  \"expired\": "<<d.expired
      <<",\n  \"fault_flags\": "<<d.faultFlags<<",\n  \"unsafe_launches\": "<<d.unsafeLaunches
      <<",\n  \"topology\": {\"strings\": "<<d.stringCount<<", \"string_modes\": "<<d.stringModes<<", \"board_modes\": "<<d.boardModes<<"},\n"
      "  \"parameters\": {\"dynamics\": "<<p.dynamics<<", \"humanization\": "<<p.humanization
      <<", \"mechanicalLevel\": "<<p.mechanicalLevel<<", \"width\": "<<p.stereoWidth<<", \"gain_db\": "<<p.gainDb<<"},\n"
      "  \"isolation\": {\"mechanism_body_coupling\": "<<(config.mechanismBodyCoupling?"true":"false")
      <<", \"direct_mechanism_observation\": "<<(config.mechanismObservation?"true":"false")
      <<", \"repetition_controller\": "<<(config.repetitionController?"true":"false")<<"},\n"
      "  \"limits\": \"Offline render includes event dispatch and collection; timing is not callback qualification. No automatic gain or room.\"\n}\n";
    if(!reportPath.empty()) { std::ofstream file(reportPath);file<<report.str();if(!file)throw std::runtime_error("Cannot write report"); }
    std::cout<<report.str();
    if(d.faultFlags)return 2;
  } catch(const std::exception& error) {std::cerr<<"keyra_full_render: "<<error.what()<<'\n';return 1;}
}
