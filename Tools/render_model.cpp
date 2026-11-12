// Renders an event score through the physical piano (Source/DSP/PianoModel.h)
// to a 32-bit float WAV in pascals times --scale. The score is keyra_render's:
// "seconds on note velocity", "seconds off note", "seconds pedal 0..1",
// "seconds soft 0..1".
#include "DSP/PianoModel.h"
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
#include <algorithm>

namespace {
struct Event {double time;std::string type;int note;float value;};
void u16(std::ofstream& f,std::uint16_t v){char b[2]={static_cast<char>(v),static_cast<char>(v>>8)};f.write(b,2);}
void u32(std::ofstream& f,std::uint32_t v){char b[4]={static_cast<char>(v),static_cast<char>(v>>8),static_cast<char>(v>>16),static_cast<char>(v>>24)};f.write(b,4);}
}
int main(int argc,char** argv){try{
  using namespace keyra::model;
  std::string eventsPath,outputPath;int rate=48000;double duration=5,scale=.25;int block=256;
  Controls controls;bool report=false;
  for(int i=1;i<argc;++i){const std::string option=argv[i];
    auto value=[&](){if(++i>=argc)throw std::runtime_error("missing argument after "+option);return std::string(argv[i]);};
    if(option=="--events")eventsPath=value();else if(option=="--output")outputPath=value();
    else if(option=="--sample-rate")rate=std::stoi(value());else if(option=="--duration")duration=std::stod(value());
    else if(option=="--scale")scale=std::stod(value());else if(option=="--block")block=std::stoi(value());
    else if(option=="--body"){const auto b=value();controls.body=b=="concert"?Body::concertGrand:b=="parlor"?Body::parlorGrand:b=="baby"?Body::babyGrand:b=="upright"?Body::upright:b=="studio"?Body::studioGrand:throw std::runtime_error("unknown body "+b);}
    else if(option=="--hammer")controls.hammer=std::stof(value());else if(option=="--age")controls.age=std::stof(value());
    else if(option=="--detune")controls.detune=std::stof(value());else if(option=="--stretch")controls.stretch=std::stof(value());
    else if(option=="--dynamics")controls.dynamics=std::stof(value());else if(option=="--lid")controls.lid=std::stof(value());
    else if(option=="--soundboard")controls.soundboard=std::stof(value());else if(option=="--sympathetic")controls.sympathetic=std::stof(value());
    else if(option=="--duplex")controls.duplex=std::stof(value());else if(option=="--room")controls.room=std::stof(value());
    else if(option=="--tuning")controls.tuning=std::stof(value());else if(option=="--felt")controls.felt=std::stof(value());
    else if(option=="--mics"){std::istringstream in(value());std::string field;int m=0;
      while(std::getline(in,field,',')&&m<micCount)controls.mic[m++]=std::stof(field);}
    else if(option=="--report")report=true;
    else throw std::runtime_error("unknown option "+option);
  }
  Piano piano;piano.prepare(rate);piano.setControls(controls);
  if(report){
    std::cout<<"key strings partials hertz length tension B stretchCents hammerGrams\n";
    for(int k=0;k<keyCount;++k){const auto r=piano.report(controls.body,k);
      std::cout<<k<<' '<<r.strings<<' '<<r.partials<<' '<<r.hertz<<' '<<r.length<<' '<<r.tension<<' '<<r.inharmonicity<<' '<<r.stretchCents<<' '<<r.hammerMass*1e3<<'\n';}
    return 0;
  }
  if(outputPath.empty())throw std::runtime_error("--output is required");
  std::vector<Event> events;
  if(!eventsPath.empty()){std::ifstream file(eventsPath);if(!file)throw std::runtime_error("cannot open "+eventsPath);
    std::string line;while(std::getline(file,line)){
      const auto comment=line.find('#');if(comment!=std::string::npos)line.resize(comment);
      std::istringstream in(line);Event e{};double a=0,b=0;
      if(!(in>>e.time>>e.type))continue;
      in>>a;if(in>>b){}
      if(e.type=="pedal"||e.type=="soft"){e.value=static_cast<float>(e.type=="pedal"&&a==0&&b>0?b:a);}
      else{e.note=static_cast<int>(a);e.value=static_cast<float>(b);}
      events.push_back(e);}
  }else{events.push_back({0,"on",60,90});events.push_back({2,"off",60,0});}
  std::stable_sort(events.begin(),events.end(),[](const Event&a,const Event&b){return a.time<b.time;});
  const auto frames=static_cast<std::uint64_t>(std::llround(duration*rate));
  std::ofstream out(outputPath,std::ios::binary);if(!out)throw std::runtime_error("cannot write "+outputPath);
  out.write("RIFF",4);u32(out,static_cast<std::uint32_t>(36+frames*8));out.write("WAVEfmt ",8);u32(out,16);u16(out,3);u16(out,2);
  u32(out,rate);u32(out,rate*8);u16(out,8);u16(out,32);out.write("data",4);u32(out,static_cast<std::uint32_t>(frames*8));
  std::vector<float> l(block),r(block),both(2*block);
  std::size_t next=0;std::uint64_t frame=0;float soft=0;double peak=0;
  const auto start=std::chrono::steady_clock::now();
  while(frame<frames){
    while(next<events.size()&&std::llround(events[next].time*rate)<=static_cast<std::int64_t>(frame)){const Event& e=events[next++];
      if(e.type=="on"&&e.value>0){piano.holdDamper(e.note-21,true);piano.strike(e.note-21,e.value/127,soft);}
      else if(e.type=="off"||e.type=="on")piano.holdDamper(e.note-21,false);
      else if(e.type=="pedal")piano.setPedal(e.value);
      else if(e.type=="soft")soft=e.value;
      else if(e.type=="knock")piano.knockBridge(e.note-21,e.value);
    }
    std::uint64_t n=std::min<std::uint64_t>(block,frames-frame);
    if(next<events.size())n=std::min<std::uint64_t>(n,std::max<std::int64_t>(1,std::llround(events[next].time*rate)-static_cast<std::int64_t>(frame)));
    piano.process(l.data(),r.data(),static_cast<int>(n));
    for(std::uint64_t i=0;i<n;++i){both[2*i]=static_cast<float>(l[i]*scale);both[2*i+1]=static_cast<float>(r[i]*scale);
      peak=std::max(peak,static_cast<double>(std::max(std::abs(both[2*i]),std::abs(both[2*i+1]))));}
    out.write(reinterpret_cast<const char*>(both.data()),static_cast<std::streamsize>(n*8));
    frame+=n;
  }
  const double seconds=std::chrono::duration<double>(std::chrono::steady_clock::now()-start).count();
  std::cerr<<"peak "<<20*std::log10(std::max(peak,1e-12))<<" dBFS, "<<100*seconds/duration<<" % of real time\n";
  return 0;
}catch(const std::exception& e){std::cerr<<"render_model: "<<e.what()<<'\n';return 1;}}
