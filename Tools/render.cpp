#include "DSP/KeyraEngine.h"
#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

namespace {
struct Event { double time;std::string type;int note;float value;int channel=1; };
void u16(std::ofstream& f,std::uint16_t v){char b[2]={static_cast<char>(v),static_cast<char>(v>>8)};f.write(b,2);}
void u32(std::ofstream& f,std::uint32_t v){char b[4]={static_cast<char>(v),static_cast<char>(v>>8),static_cast<char>(v>>16),static_cast<char>(v>>24)};f.write(b,4);}
}
int main(int argc,char** argv){try {
  std::string eventsPath,outputPath,metricsPath;int rate=48000;double duration=5;bool legacy=false,vary=false;
  keyra::Parameters parameters;
  for(int i=1;i<argc;++i){const std::string option=argv[i];
    auto value=[&](){if(++i>=argc)throw std::runtime_error("missing argument after "+option);return std::string(argv[i]);};
    if(option=="--help"){
      std::cout<<"keyra_render --events score.events --output render.wav [--sample-rate 48000] [--duration 5] [--metrics result.json] [--gain .7] [--brightness .5] [--resonance .25] [--mute 0] [--sustain 0] [--soft 0] [--sostenuto 0] [--model grand|upright] [--build strings,hammers,soundboard,action[,stiffness,unisons,ring]] [--quality full|balanced|light] [--legacy-attack] [--vary]\n"
      <<"Events: seconds on note[0..127] velocity[0..127] [channel]; seconds off note 0 [channel]; seconds pedal value[0..1] (or preserved seconds pedal 0 value); seconds cc controller value[0..127] [channel]; seconds bend semitones [channel]. Keys12/13/14 hold soft/sostenuto/sustain. Use cc for channel-specific pedal events.\n";return 0;
    }else if(option=="--events")eventsPath=value();else if(option=="--output")outputPath=value();
    else if(option=="--metrics")metricsPath=value();else if(option=="--sample-rate")rate=std::stoi(value());
    else if(option=="--duration")duration=std::stod(value());else if(option=="--legacy-attack")legacy=true;
    else if(option=="--vary")vary=true;
    else if(option=="--gain")parameters.gain=std::stof(value());else if(option=="--brightness")parameters.brightness=std::stof(value());
    else if(option=="--resonance")parameters.resonance=std::stof(value());else if(option=="--mute")parameters.mute=std::stof(value());
    else if(option=="--sustain")parameters.sustain=std::stof(value());else if(option=="--soft")parameters.soft=std::stof(value());
    else if(option=="--sostenuto")parameters.sostenuto=std::stof(value());
    else if(option=="--model"){const auto piano=value();
      if(piano!="grand"&&piano!="upright")throw std::runtime_error("unknown model "+piano);
      parameters.build=keyra::measuredBuild(piano=="upright"?keyra::Piano::upright:keyra::Piano::grand);}
    else if(option=="--build"){
      // strings,hammers,soundboard,action[,stiffness,unisons,ring]
      std::istringstream in(value());float* fields[]{&parameters.build.strings,&parameters.build.hammers,
        &parameters.build.soundboard,&parameters.build.action,&parameters.build.stiffness,&parameters.build.unisons,
        &parameters.build.ring};
      std::size_t n=0;for(std::string field;std::getline(in,field,',');++n){
        if(n==std::size(fields))throw std::runtime_error("--build takes at most seven values");
        *fields[n]=std::stof(field);}
      if(n<4)throw std::runtime_error("--build takes the four parts, then optionally the three modifiers");}
    else if(option=="--quality"){const auto quality=value();
      if(quality!="full"&&quality!="balanced"&&quality!="light")throw std::runtime_error("unknown quality "+quality);
      parameters.quality=quality=="light"?keyra::Quality::light:quality=="balanced"?keyra::Quality::balanced:keyra::Quality::full;}
    else throw std::runtime_error("unknown option "+option);
  }
  if(outputPath.empty()||rate<8000||rate>192000||!std::isfinite(duration)||duration<=0||duration>600)throw std::runtime_error("invalid output/rate/duration");
  std::vector<Event> events;
  if(!eventsPath.empty()){
    std::ifstream file(eventsPath);if(!file)throw std::runtime_error("cannot open "+eventsPath);
    std::string line;while(std::getline(file,line)){
      const auto comment=line.find('#');if(comment!=std::string::npos)line.resize(comment);
      std::istringstream in(line);in>>std::ws;if(in.peek()==std::char_traits<char>::eof())continue;
      Event e{};if(!(in>>e.time>>e.type)||!std::isfinite(e.time)||e.time<0||e.time>600)throw std::runtime_error("invalid event: "+line);
      std::vector<double> fields;double field;
      while(in>>field){if(!std::isfinite(field))throw std::runtime_error("nonfinite event: "+line);fields.push_back(field);}
      if(!in.eof())throw std::runtime_error("invalid event number: "+line);
      auto channelField=[&](double x){if(x<1||x>16||std::floor(x)!=x)throw std::runtime_error("invalid channel: "+line);e.channel=static_cast<int>(x);};
      if(e.type=="pedal"||e.type=="soft"||e.type=="sostenuto"||e.type=="mute"){
        e.note=0;if(fields.empty()||fields.size()>3)throw std::runtime_error("invalid controller event: "+line);
        if(e.type=="pedal"&&fields.size()>=2&&fields[0]==0&&fields[1]>=0&&fields[1]<=1){
          e.value=static_cast<float>(fields[1]);if(fields.size()==3)channelField(fields[2]);
        }else{
          if(fields.size()>2)throw std::runtime_error("invalid controller event: "+line);
          e.value=static_cast<float>(fields[0]);if(fields.size()==2)channelField(fields[1]);
        }
        if(e.value<0||e.value>1)throw std::runtime_error("controller out of range: "+line);
      }else if(e.type=="bend"){
        if(fields.empty()||fields.size()>2||fields[0]<-48||fields[0]>48)throw std::runtime_error("invalid bend: "+line);
        e.value=static_cast<float>(fields[0]);if(fields.size()==2)channelField(fields[1]);
      }else if(e.type=="on"||e.type=="off"||e.type=="cc"){
        if(fields.empty()||fields.size()>3||(e.type!="off"&&fields.size()<2))throw std::runtime_error("invalid event: "+line);
        const double minimum=0,maximum=127;
        if(fields[0]<minimum||fields[0]>maximum||std::floor(fields[0])!=fields[0])throw std::runtime_error("note/CC out of range: "+line);
        e.note=static_cast<int>(fields[0]);e.value=fields.size()>1?static_cast<float>(fields[1]):0;
        if(e.value<0||e.value>127)throw std::runtime_error("event value out of range: "+line);
        if(fields.size()==3)channelField(fields[2]);
      }else throw std::runtime_error("unknown event: "+line);
      if(!std::isfinite(e.value)||e.channel<1||e.channel>16)throw std::runtime_error("invalid event value/channel: "+line);
      events.push_back(e);
    }
  }else{events.push_back({0,"on",60,80,1});events.push_back({1,"off",60,0,1});}
  std::stable_sort(events.begin(),events.end(),[](const Event&a,const Event&b){return a.time<b.time;});
  keyra::Engine engine(rate);engine.setParameters(parameters);engine.setLegacyAttackForComparison(legacy);
  // Measurements play each strike at exactly the recorded layers' velocity it is
  // given; --vary plays them as the plug-in does, through the shared velocity
  // response and each a little harder or softer.
  engine.setSteadyStrikesForMeasurement(!vary);
  const auto frames=static_cast<std::uint64_t>(std::llround(duration*rate));
  if(frames*8>0xffffffffu-36u)throw std::runtime_error("WAV too large");
  std::ofstream out(outputPath,std::ios::binary);if(!out)throw std::runtime_error("cannot write "+outputPath);
  out.write("RIFF",4);u32(out,static_cast<std::uint32_t>(36+frames*8));out.write("WAVEfmt ",8);u32(out,16);u16(out,3);u16(out,2);
  u32(out,rate);u32(out,rate*8);u16(out,8);u16(out,32);out.write("data",4);u32(out,static_cast<std::uint32_t>(frames*8));
  std::array<float,256> l{},r{};std::array<float,512> interleaved{};std::size_t next=0;std::uint64_t frame=0;
  double squares=0,peak=0;const auto start=std::chrono::steady_clock::now();
  // As a host compensates the output stage's look-ahead: its first frames are
  // dropped, so a strike at t sounds at t in the file.
  const auto latency=static_cast<std::uint64_t>(engine.outputLatencySamples());
  while(frame<frames+latency){
    while(next<events.size()&&std::llround(events[next].time*rate)<=static_cast<std::int64_t>(frame)){
      const auto&e=events[next++];if(e.type=="on")engine.noteOn(e.note,e.value/127,e.channel);
      else if(e.type=="off")engine.noteOff(e.note,e.channel);else if(e.type=="cc")engine.controlChange(e.note,static_cast<int>(e.value),e.channel);
      else if(e.type=="bend")engine.pitchBend(e.value,e.channel);
      else{const int cc=e.type=="pedal"?64:e.type=="soft"?67:e.type=="sostenuto"?66:1;engine.controlChange(cc,static_cast<int>(std::lround(e.value*127)),e.channel);}
    }
    int count=static_cast<int>(std::min<std::uint64_t>(256,frames+latency-frame));
    if(next<events.size())count=std::min(count,static_cast<int>(std::max<std::int64_t>(1,std::llround(events[next].time*rate)-static_cast<std::int64_t>(frame))));
    engine.process(l.data(),r.data(),count);
    int kept=0;
    for(int i=0;i<count;++i){if(frame+static_cast<std::uint64_t>(i)<latency)continue;
      interleaved[2*kept]=l[i];interleaved[2*kept+1]=r[i];++kept;squares+=static_cast<double>(l[i])*l[i]+static_cast<double>(r[i])*r[i];peak=std::max({peak,std::abs(static_cast<double>(l[i])),std::abs(static_cast<double>(r[i]))});}
    out.write(reinterpret_cast<const char*>(interleaved.data()),kept*8);frame+=count;
  }
  const double elapsed=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  std::ostringstream json;json<<std::setprecision(10)<<"{\"sample_rate\":"<<rate<<",\"frames\":"<<frames<<",\"duration_seconds\":"<<duration<<",\"wall_seconds\":"<<elapsed<<",\"realtime_factor\":"<<elapsed/duration<<",\"peak\":"<<peak<<",\"rms\":"<<std::sqrt(squares/(2*frames))<<",\"legacy_attack\":"<<(legacy?"true":"false")<<"}";
  if(!metricsPath.empty()){std::ofstream metrics(metricsPath);metrics<<json.str()<<'\n';}
  std::cout<<json.str()<<'\n';return 0;
}catch(const std::exception& error){std::cerr<<error.what()<<'\n';return 1;}}
