#include "keyra/PhysicalPiano.h"
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
struct Event {double time;std::string type;int note;double value;};
double number(const std::string& s) {size_t used=0;const double x=std::stod(s,&used);if(used!=s.size()||!std::isfinite(x))throw std::runtime_error("Invalid number");return x;}
void u16(std::ostream& o,uint16_t x){o.put(char(x));o.put(char(x>>8));}
void u32(std::ostream& o,uint32_t x){u16(o,uint16_t(x));u16(o,uint16_t(x>>16));}
void wav(const std::string& path,const std::vector<float>& x,uint32_t rate){
  if(x.size()>((uint64_t(1)<<32)-44)/4)throw std::runtime_error("RIFF limit");
  std::ofstream o(path,std::ios::binary);if(!o)throw std::runtime_error("Cannot open output");
  const auto bytes=uint32_t(x.size()*4);o.write("RIFF",4);u32(o,36+bytes);o.write("WAVEfmt ",8);u32(o,16);
  u16(o,3);u16(o,2);u32(o,rate);u32(o,rate*8);u16(o,8);u16(o,32);o.write("data",4);u32(o,bytes);
  for(float value:x){uint32_t bits;std::memcpy(&bits,&value,4);u32(o,bits);}if(!o)throw std::runtime_error("WAV write failed");
}
}
int main(int argc,char** argv){
  try {
    double seconds=4.25,rate=48000,velocity=61,resonance=.5;int note=60;
    bool nonlinear=true,referenceBoard=true,complex=true;
    std::string eventsPath,output,reportPath,stemPrefix;
    for(int i=1;i<argc;++i){std::string arg=argv[i];
      if(arg=="--help") {std::cout<<"Experimental physical note renderer; not the released/default plugin.\n"
        "--output FILE.wav [--events FILE.events] [--note 60 --velocity 61]\n"
        "--rate 48000 --seconds 4.25 --resonance 0.5 --nonlinear 1 --reference-board 1 --complex 1\n"
        "--report FILE.json [--stem-prefix PATH]\nAll options take separate values. Native pressure-proxy float WAV is unnormalized.\n";return 0;}
      if(i+1>=argc)throw std::runtime_error("Missing option value");
      const std::string value=argv[++i];
      if(arg=="--output")output=value;else if(arg=="--events")eventsPath=value;else if(arg=="--report")reportPath=value;
      else if(arg=="--stem-prefix")stemPrefix=value;else if(arg=="--seconds")seconds=number(value);else if(arg=="--rate")rate=number(value);
      else if(arg=="--velocity")velocity=number(value);else if(arg=="--resonance")resonance=number(value);
      else if(arg=="--note"){const double n=number(value);if(n!=std::floor(n)||n<21||n>108)throw std::runtime_error("Note21..108");note=int(n);}
      else if(arg=="--nonlinear")nonlinear=number(value)!=0;else if(arg=="--reference-board")referenceBoard=number(value)!=0;
      else if(arg=="--complex")complex=number(value)!=0;else throw std::runtime_error("Unknown option");
    }
    if(output.empty()||seconds<=0||seconds>60||rate!=std::floor(rate)||rate<48000||rate>192000||velocity<=0||velocity>127||resonance<0||resonance>1)
      throw std::runtime_error("Invalid render configuration");
    std::vector<Event> events;
    if(eventsPath.empty())events.push_back({.05,"on",note,velocity});
    else {std::ifstream in(eventsPath);if(!in)throw std::runtime_error("Cannot read events");std::string line;
      while(std::getline(in,line)){if(line.empty()||line[0]=='#')continue;std::istringstream row(line);Event e{};
        if(!(row>>e.time>>e.type>>e.note>>e.value)||!std::isfinite(e.time)||!std::isfinite(e.value)||e.time<0||e.time>600)throw std::runtime_error("Invalid event");
        if(e.type!="on"&&e.type!="off"&&e.type!="pedal")throw std::runtime_error("Invalid event kind");
        if(e.type!="pedal"&&(e.note<21||e.note>108))throw std::runtime_error("Invalid event note");
        if((e.type=="on"&&(e.value<0||e.value>127))||(e.type=="pedal"&&(e.value<0||e.value>1)))throw std::runtime_error("Invalid event value");
        events.push_back(e);}
      std::stable_sort(events.begin(),events.end(),[](const auto&a,const auto&b){return a.time<b.time;});}
    keyra::PhysicalPiano piano;if(!piano.prepare(rate))throw std::runtime_error("Unsupported rate");
    piano.setReferenceSoundboardEnabled(referenceBoard);piano.setResonance(resonance);
    piano.setNonlinearHammerEnabled(nonlinear);piano.setComplexRadiationEnabled(complex);piano.reset();
    const auto frames=uint64_t(std::ceil(seconds*rate));std::vector<float> audio(frames*2);
    std::array<std::vector<float>,3> stems;if(!stemPrefix.empty())for(auto& stem:stems)stem.resize(frames*2);
    std::array<std::array<double,2>,4> previous{},hp{};const double pole=std::exp(-2*3.14159265358979323846*24/rate);
    size_t next=0;double peak=0,power=0;const auto start=std::chrono::steady_clock::now();
    for(uint64_t frame=0;frame<frames;++frame){
      while(next<events.size()&&uint64_t(std::llround(events[next].time*rate))<=frame){const auto& e=events[next++];
        if(e.type=="on")piano.noteOn(e.note,e.value/127.);else if(e.type=="off")piano.noteOff(e.note);else piano.sustain(e.value);}
      piano.beginFrame();piano.finishFrame();const auto s=piano.observeStems();
      const std::array<std::array<double,2>,3> parts={s.primary,s.secondary,s.board};
      for(unsigned channel=0;channel<2;++channel){const double x=s.primary[channel]+s.secondary[channel]+s.board[channel];
        hp[0][channel]=pole*(hp[0][channel]+x-previous[0][channel]);previous[0][channel]=x;
        const double y=hp[0][channel];if(!std::isfinite(y))throw std::runtime_error("Nonfinite physical output");
        audio[2*frame+channel]=float(y);peak=std::max(peak,std::abs(y));power+=y*y;
        if(!stemPrefix.empty())for(unsigned part=0;part<3;++part){const double v=parts[part][channel];
          hp[part+1][channel]=pole*(hp[part+1][channel]+v-previous[part+1][channel]);previous[part+1][channel]=v;
          stems[part][2*frame+channel]=float(hp[part+1][channel]);}}
    }
    const double wall=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
    wav(output,audio,uint32_t(rate));if(!stemPrefix.empty()){const char* names[]={"-primary.wav","-secondary.wav","-board.wav"};for(unsigned i=0;i<3;++i)wav(stemPrefix+names[i],stems[i],uint32_t(rate));}
    const auto contact=piano.contactMetrics();std::ostringstream report;
    report<<"{\n\"experimental_physical_candidate\":true,\n\"sample_rate\":"<<rate<<",\n\"seconds\":"<<seconds<<",\n\"wall_seconds\":"<<wall
      <<",\n\"wall_seconds_per_audio_second\":"<<wall/seconds<<",\n\"mode_count\":"<<piano.modeCount()<<",\n\"board_mode_count\":"<<piano.boardModeCount()
      <<",\n\"resonance\":"<<resonance<<",\n\"nonlinear_hammer\":"<<(nonlinear?"true":"false")
      <<",\n\"reference_board\":"<<(referenceBoard?"true":"false")<<",\n\"complex_radiation\":"<<(complex?"true":"false")<<",\n\"peak\":"<<peak
      <<",\n\"rms\":"<<std::sqrt(power/(2*frames))<<",\n\"contact_frames\":"<<contact.contactFrames<<",\n\"invalid_contacts\":"<<contact.invalidContacts
      <<",\n\"maximum_contact_energy_residual_j\":"<<contact.maximumEnergyResidual<<",\n\"final_energy_j\":"<<piano.energy()<<"\n}\n";
    if(!reportPath.empty()){std::ofstream f(reportPath);f<<report.str();if(!f)throw std::runtime_error("Cannot write report");}
    std::cout<<report.str();
  }catch(const std::exception& e){std::cerr<<"keyra_physical_render: "<<e.what()<<'\n';return 1;}
}
