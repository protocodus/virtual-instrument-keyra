// Keyra's levels on Reason's channel meter, the scale the portfolio's newer
// instruments are calibrated on (Aculele's Tools/ReasonMeter.h): the RMS over
// a sliding 300 ms window of the louder channel, read 12 dB up, so 0 VU is
// -12 dBFS RMS (Reason's VU offset as its users report it; the manual gives
// no default).
//
//   KeyraLevels --report [--jobs N]   every piano's and factory preset's
//                                     readings, each piano's correction and
//                                     how even its keys are
//   KeyraLevels --check [--jobs N]    the audio-tier test Keyra.Levels
//   KeyraLevels --write-keys Source/DSP/KeyVoicing.h [--jobs N]
//                                     the scale's voicing, below
//
// Playing is at 48 kHz in 256-sample blocks, through the plug-in's velocity
// response and strike variation, each event alone in a 1.5 s slot and held
// 0.8 s without pedal, with the output stage's latency compensated:
//  - typical playing: single notes every fourth semitone from A0 to A7 and
//    eight chords, four around middle C and four for two hands, at
//    velocities 70, 90 and 110. Its reading is the median over events of
//    each event's highest reading.
//  - the loudest chords: the same chords at velocity 127, five rounds of
//    them, read as the highest of their readings and the output's sample
//    peak, and against five rounds at velocity 110.
//  - the loudest single notes: the same single notes at velocity 127,
//    against them at 110.
//
// A piano's calibration reads its default sound 20 dB down, below the output
// stage, and adds the 20 dB back; the factor --report prints brings it to
// targetVu at the default Output (KeyraEngine.cpp's pascalScale). A preset
// has no level of its own: its microphone pairs' levels set how loud it
// plays, and the check holds each within presetWindowDb of the target. The
// stereo output has a separate -1.5 dBFS sample ceiling.
//
// The scale's voicing. A board answers each key's partials in its own way, so
// through the microphones a key comes out several dB over or under its
// neighbours (2.1.0: 2.2 dB between neighbours on average and up to 8 dB,
// where the Salamander grand's keys, recorded every minor third, lie within
// 1.5 dB of the curve through them). A technician voices that even by ear;
// here it is measured, through the model below the engine at its default
// controls: each key alone at keyVelocity, the second after the blow, as each
// pair of each piano hears its strings (the key's sound less what the blow
// alone knocks out of the frame, which no voicing reaches). The mean square
// over both channels is the key's level in a pair; the mean product of two
// pairs' signals says how they add in a mix, where pairs meet as waves. The
// even scale of a pair is the curve through its keys' levels: the median of
// five, then a line fitted about each key with weights falling off over
// keySpread keys. --write-keys writes KeyVoicing.h: each key's levels and
// products against the close pair's even scale, and each pair's even scale
// against it, from which the model's mix pulls each key onto the even scale
// of the pairs that are up. Each pair's scale keeps its own course through
// the keys at the close pair's level without the room, on average over the
// keys: the model balances its pairs on the board's modes alone, and what
// the bridge radiates beside them adds 0.2 dB to the concert grand's close
// pair and up to 1.3 dB to the others (2.10.0), which took the distant pair
// 2.6 dB over the close one in Keyra.Engine's chord. After any change to the model's sound, write it
// again: --check plays every key, voiced, through each pair alone and
// through two mixes (keyMixes), and fails when a key is more than keyWindowDb
// off the curve through its neighbours. With the table fresh (2.10.0) the
// furthest key is 1.1 dB off, the concert grand's C8 through the close pair,
// where the knock is a good part of a key's sound; the others lie within
// 1.0 dB. A stale table leaves keys 3 dB and more off.
#include "DSP/KeyraEngine.h"
#include "DSP/KeyraPresets.h"
#include "DSP/KeyVoicing.h"
#include "DSP/OutputStage.h"

#include <algorithm>
#include <array>
#include <atomic>
#include <charconv>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <functional>
#include <string>
#include <thread>
#include <utility>
#include <vector>

namespace {
constexpr double rate=48000,slotSeconds=1.5,holdSeconds=.8,vuOffsetDb=12,targetVu=-9,belowDb=20,presetWindowDb=2;
constexpr int block=256;
struct Event {std::vector<int> notes;int velocity;};
const std::vector<std::vector<int>> chords{
  {60,64,67},{60,65,69},{59,62,67},{57,60,64},
  {48,55,64,67,72},{41,53,57,60,65},{43,55,59,62,67},{45,52,57,60,64}};
constexpr int singles=22,velocities[]{70,90,110};
std::vector<Event> singleNotes(int velocity){
  std::vector<Event> events;
  for(int i=0;i<singles;++i)events.push_back({{21+4*i},velocity});
  return events;
}
std::vector<Event> typicalPlaying(){
  std::vector<Event> events;
  for(int velocity:velocities){
    for(auto& note:singleNotes(velocity))events.push_back(std::move(note));
    for(const auto& chord:chords)events.push_back({chord,velocity});
  }
  return events;
}
// The chords at one velocity, five rounds of them: every strike lands at its
// own spread (touchSpreadDb), and through the output stage's limiter the
// loudest chords differ little, so one round's draws could decide the
// step's sign.
constexpr int rounds=5;
std::vector<Event> chordRounds(int velocity){
  std::vector<Event> events;
  for(int round=0;round<rounds;++round)for(const auto& chord:chords)events.push_back({chord,velocity});
  return events;
}

struct Reading {std::vector<double> events;double peakDbfs=-300;bool finite=true;};
// Each event's highest reading on the meter, and the output's sample peak.
Reading play(const keyra::Parameters& parameters,const std::vector<Event>& events){
  const auto slot=static_cast<long long>(slotSeconds*rate),hold=static_cast<long long>(holdSeconds*rate);
  keyra::Engine engine(rate);engine.setParameters(parameters);
  // Starts the smoothed Output at its setting rather than the default's.
  engine.reset();
  const long long latency=engine.outputLatencySamples(),total=slot*static_cast<long long>(events.size());
  const long long length=total+latency;
  std::vector<float> left(static_cast<std::size_t>(length)),right(left.size());
  for(long long done=0;done<length;){
    // Events land on their exact frame: blocks end at the next one.
    long long next=std::min(length,done+block);
    const auto index=static_cast<std::size_t>(done/slot);
    if(index<events.size()){
      const long long at=static_cast<long long>(index)*slot,off=at+hold;
      if(done==at)for(int note:events[index].notes)engine.noteOn(note,events[index].velocity/127.f);
      if(done==off)for(int note:events[index].notes)engine.noteOff(note);
      next=std::min(next,done<off?off:at+slot);
    }
    engine.process(left.data()+done,right.data()+done,static_cast<int>(next-done));
    done=next;
  }
  Reading result;
  const auto window=static_cast<long long>(.3*rate);
  double sumLeft=0,sumRight=0,peak=0,highest=-300;
  for(long long i=0;i<total;++i){
    const auto at=static_cast<std::size_t>(i+latency);
    if(!std::isfinite(left[at])||!std::isfinite(right[at]))result.finite=false;
    sumLeft+=static_cast<double>(left[at])*left[at];sumRight+=static_cast<double>(right[at])*right[at];
    if(i>=window){
      const auto gone=at-static_cast<std::size_t>(window);
      sumLeft-=static_cast<double>(left[gone])*left[gone];sumRight-=static_cast<double>(right[gone])*right[gone];
    }
    const double meanSquare=std::max(std::max(sumLeft,sumRight)/static_cast<double>(window),1e-30);
    highest=std::max(highest,10*std::log10(meanSquare)+vuOffsetDb);
    peak=std::max({peak,static_cast<double>(std::abs(left[at])),static_cast<double>(std::abs(right[at]))});
    if((i+1)%slot==0){result.events.push_back(highest);highest=-300;}
  }
  result.peakDbfs=20*std::log10(std::max(peak,1e-15));
  return result;
}
double median(std::vector<double> x){
  std::sort(x.begin(),x.end());const auto n=x.size();
  return n%2?x[n/2]:.5*(x[n/2-1]+x[n/2]);
}
void parallel(std::size_t count,int jobs,const std::function<void(std::size_t)>& work){
  std::atomic<std::size_t> next{0};std::vector<std::thread> threads;
  for(int j=0;j<jobs;++j)threads.emplace_back([&]{for(std::size_t i=next++;i<count;i=next++)work(i);});
  for(auto& thread:threads)thread.join();
}

constexpr double keySeconds=1,keySkipSeconds=.02,keyWindowDb=2,keySpread=4;
constexpr float keyVelocity=.5f;
constexpr int keys=keyra::model::keyCount,pairs=keyra::model::micCount,bodies=keyra::model::bodyCount;
const char* const pairNames[pairs]{"close","xy","live","distant"};
constexpr float keyMixes[][pairs]{{1,0,0,0},{0,1,0,0},{0,0,1,0},{0,0,0,1},{.7f,.7f,.3f,0},{.4f,.4f,.7f,.4f}};
constexpr int keyMixCount=static_cast<int>(sizeof(keyMixes)/sizeof(keyMixes[0]));
using KeyLevels=std::array<double,keys>;
// A key alone through a mix of the pairs, left then right; `pull` as
// Piano::pullKey takes it, and the room as the controls give it unless `dry`.
std::vector<float> keySound(keyra::model::Piano& piano,int body,const float* mix,int key,float pull,bool dry=false){
  keyra::model::Controls controls;controls.body=static_cast<keyra::model::Body>(body);
  std::copy(mix,mix+pairs,controls.mic);
  if(dry)controls.room=0;
  const int skip=static_cast<int>(keySkipSeconds*rate),frames=skip+static_cast<int>(keySeconds*rate);
  std::vector<float> left(static_cast<std::size_t>(frames)),right(left.size());
  piano.reset();piano.setControls(controls);piano.pullKey(key,pull);
  piano.holdDamper(key,true);piano.strike(key,keyVelocity);
  for(int done=0;done<frames;done+=block)piano.process(left.data()+done,right.data()+done,std::min(block,frames-done));
  piano.pullKey(key,-1);
  left.erase(left.begin(),left.begin()+skip);
  left.insert(left.end(),right.begin()+skip,right.end());
  return left;
}
double meanProduct(const std::vector<float>& a,const std::vector<float>& b){
  double sum=0;
  for(std::size_t i=0;i<a.size();++i)sum+=static_cast<double>(a[i])*b[i];
  return sum/static_cast<double>(a.size());
}
double decibels(double power){return 10*std::log10(std::max(power,1e-30));}
KeyLevels evenScale(const KeyLevels& level){
  KeyLevels calm{},curve{};
  for(int k=0;k<keys;++k){
    std::vector<double> near;
    for(int j=std::max(0,k-2);j<=std::min(keys-1,k+2);++j)near.push_back(level[static_cast<std::size_t>(j)]);
    calm[static_cast<std::size_t>(k)]=median(near);
  }
  for(int k=0;k<keys;++k){
    double s=0,sx=0,sxx=0,sy=0,sxy=0;
    for(int j=0;j<keys;++j){
      const double x=j-k,w=std::exp(-x*x/(2*keySpread*keySpread)),y=calm[static_cast<std::size_t>(j)];
      s+=w;sx+=w*x;sxx+=w*x*x;sy+=w*y;sxy+=w*x*y;
    }
    curve[static_cast<std::size_t>(k)]=(sxx*sy-sx*sxy)/(s*sxx-sx*sx);
  }
  return curve;
}
// How far the furthest key is off the curve through the keys, and the mean
// step from a key to the next.
struct Evenness {double furthest=0,step=0;int key=0;};
Evenness evenness(const KeyLevels& level){
  const KeyLevels even=evenScale(level);
  Evenness result;
  for(int k=0;k<keys;++k){
    const auto at=static_cast<std::size_t>(k);
    if(std::abs(level[at]-even[at])>std::abs(result.furthest)){result.furthest=level[at]-even[at];result.key=k;}
    if(k)result.step+=std::abs(level[at]-level[at-1])/(keys-1);
  }
  return result;
}
// A piano's table: every key's pair products (close-close, close-xy, ...
// distant-distant) and each pair's even scale, both against the close pair's
// even scale; and how even its unvoiced keys were through each pair.
constexpr int products=pairs*(pairs+1)/2;
struct Voicing {
  std::array<std::array<double,products>,keys> heard{};
  std::array<std::array<double,pairs>,keys> even{};
  Evenness unvoiced[pairs];
};
Voicing voice(int body){
  keyra::model::Piano piano;piano.prepare(rate);
  Voicing voicing;
  std::array<KeyLevels,pairs> level{},dry{};
  for(int key=0;key<keys;++key){
    std::vector<float> strings[pairs];
    for(int pair=0;pair<pairs;++pair){
      const auto heard=[&](bool withoutRoom){
        auto sound=keySound(piano,body,keyMixes[pair],key,1,withoutRoom);
        const auto knock=keySound(piano,body,keyMixes[pair],key,0,withoutRoom);
        for(std::size_t i=0;i<knock.size();++i)sound[i]-=knock[i];
        return sound;};
      strings[pair]=heard(false);
      const auto alone=heard(true);
      dry[static_cast<std::size_t>(pair)][static_cast<std::size_t>(key)]=decibels(meanProduct(alone,alone));
    }
    std::size_t at=0;
    for(int a=0;a<pairs;++a)for(int b=a;b<pairs;++b)voicing.heard[static_cast<std::size_t>(key)][at++]=meanProduct(strings[a],strings[b]);
    for(int pair=0;pair<pairs;++pair)
      level[static_cast<std::size_t>(pair)][static_cast<std::size_t>(key)]=decibels(meanProduct(strings[pair],strings[pair]));
  }
  std::array<KeyLevels,pairs> even{};
  for(int pair=0;pair<pairs;++pair){
    even[static_cast<std::size_t>(pair)]=evenScale(level[static_cast<std::size_t>(pair)]);
    voicing.unvoiced[pair]=evenness(level[static_cast<std::size_t>(pair)]);
  }
  // Each pair keeps its own scale through the keys, at the close pair's
  // level on average: voiced onto it, a key gives the pair what the scale
  // says, of which the share without the room is what the key gave it dry.
  // The room comes on top, as the pair sends to it.
  double offset[pairs]{};
  for(std::size_t pair=0;pair<pairs;++pair)for(std::size_t key=0;key<keys;++key)
    offset[pair]+=(even[pair][key]+dry[pair][key]-level[pair][key]-even[0][key]-dry[0][key]+level[0][key])/keys;
  for(std::size_t key=0;key<keys;++key){
    const double close=std::pow(10.,even[0][key]/10);
    for(double& product:voicing.heard[key])product/=close;
    for(std::size_t pair=0;pair<pairs;++pair)voicing.even[key][pair]=std::pow(10.,(even[pair][key]-even[0][key]-offset[pair])/10);
  }
  return voicing;
}
int writeKeys(const char* path,int jobs){
  std::vector<Voicing> all(bodies);
  parallel(all.size(),jobs,[&](std::size_t body){all[body]=voice(static_cast<int>(body));});
  std::FILE* file=std::fopen(path,"w");
  if(!file){std::fprintf(stderr,"Cannot write %s\n",path);return 1;}
  std::fprintf(file,"// Written by KeyraLevels --write-keys (Tools/KeyraLevels.cpp, which says what\n"
                    "// is measured); never edit by hand.\n#pragma once\nnamespace keyra { namespace model {\n"
                    "// [body][key]: what the key's strings give the pairs close, xy, live and\n"
                    "// distant, alone and two together (close-close, close-xy, close-live,\n"
                    "// close-distant, xy-xy, ... distant-distant), against the close pair's even\n"
                    "// scale at the key.\n"
                    "constexpr float keyHeard[%d][%d][%d]{\n",bodies,keys,products);
  for(std::size_t body=0;body<all.size();++body){
    std::fprintf(file,"  { // %s\n",keyra::bodyNames[body]);
    for(const auto& key:all[body].heard){
      std::fprintf(file,"    {");
      for(double product:key)std::fprintf(file,"%.4g,",product);
      std::fprintf(file,"},\n");
    }
    std::fprintf(file,"  },\n");
  }
  std::fprintf(file,"};\n// [body][key]: each pair's even scale against the close pair's, at the close\n"
                    "// pair's level without the room on average over the keys.\n"
                    "constexpr float keyEven[%d][%d][%d]{\n",bodies,keys,pairs);
  for(std::size_t body=0;body<all.size();++body){
    std::fprintf(file,"  { // %s\n",keyra::bodyNames[body]);
    for(const auto& key:all[body].even){
      std::fprintf(file,"    {");
      for(double scale:key)std::fprintf(file,"%.4g,",scale);
      std::fprintf(file,"},\n");
    }
    std::fprintf(file,"  },\n");
    for(int pair=0;pair<pairs;++pair){
      const Evenness& e=all[body].unvoiced[pair];
      std::printf("%-14s %-8s unvoiced: furthest key (MIDI %d) %+.2f dB off the even scale, %.2f dB from key to key\n",
                  keyra::bodyNames[body],pairNames[pair],e.key+21,e.furthest,e.step);
    }
  }
  std::fprintf(file,"};\n}}\n");
  return std::fclose(file)==0?0:1;
}
// Every key of every piano, voiced, through each of keyMixes.
std::vector<Evenness> voicedScales(int jobs){
  std::vector<Evenness> all(static_cast<std::size_t>(bodies*keyMixCount));
  parallel(all.size(),jobs,[&](std::size_t task){
    const int body=static_cast<int>(task)/keyMixCount,mix=static_cast<int>(task)%keyMixCount;
    keyra::model::Piano piano;piano.prepare(rate);
    KeyLevels level{};
    for(int key=0;key<keys;++key){
      const auto sound=keySound(piano,body,keyMixes[mix],key,-1);
      level[static_cast<std::size_t>(key)]=decibels(meanProduct(sound,sound));
    }
    all[task]=evenness(level);
  });
  return all;
}

int run(int jobs,bool check){
  const auto& presets=keyra::factoryPresets;
  constexpr std::size_t pianos=keyra::model::bodyCount;
  const auto typicalEvents=typicalPlaying(),loudestEvents=chordRounds(127),strongEvents=chordRounds(110);
  const auto loudestNotes=singleNotes(127),strongNotes=singleNotes(110);
  // Each piano's default sound below the output stage, then each factory
  // program's typical playing, fortissimo and strong chords and singles.
  constexpr std::size_t perPreset=5;
  const std::size_t count=pianos+perPreset*presets.size();
  std::vector<Reading> readings(count);
  parallel(count,jobs,[&](std::size_t task){
    if(task<pianos){
      keyra::Parameters parameters;parameters.body=static_cast<keyra::model::Body>(task);
      parameters.gain*=static_cast<float>(std::pow(10.,-belowDb/20));
      readings[task]=play(parameters,typicalEvents);
      return;
    }
    const std::size_t preset=(task-pianos)/perPreset,kind=(task-pianos)%perPreset;
    const auto parameters=keyra::withPreset(keyra::Parameters{},presets[preset]);
    const std::vector<Event>* events[perPreset]{&typicalEvents,&loudestEvents,&strongEvents,&loudestNotes,&strongNotes};
    readings[task]=play(parameters,*events[kind]);
  });

  int failures=0;
  const auto expect=[&failures](bool ok,const char* what,const char* message,double value){
    if(ok)return;
    std::printf("FAIL %s: %s (%.2f)\n",what,message,value);++failures;
  };
  if(std::any_of(readings.begin(),readings.end(),[](const Reading& r){return !r.finite;})){
    std::fprintf(stderr,"Nonfinite samples in factory level capture\n");
    return 1;
  }
  const double peakCeilingDbfs = 20 * std::log10(protocodus::OutputStage<2>::kCeiling) + .00001;
  for(std::size_t piano=0;piano<pianos;++piano){
    const double reading=median(readings[piano].events)+belowDb;
    std::printf("%-14s default sound %6.2f VU; pascalScale x%.5f (%+.2f dB) for %.0f VU\n",keyra::bodyNames[piano],
                reading,std::pow(10.,(targetVu-reading)/20),targetVu-reading,targetVu);
    expect(std::abs(reading-targetVu)<=.5,keyra::bodyNames[piano],"its default sound is not at the target",reading);
  }
  // The median step from velocity 110 to 127, event by event, and the least.
  const auto stepOf=[](const Reading& loudest,const Reading& strong){
    std::vector<double> steps;
    for(std::size_t k=0;k<loudest.events.size();++k)steps.push_back(loudest.events[k]-strong.events[k]);
    return std::make_pair(median(steps),*std::min_element(steps.begin(),steps.end()));
  };
  for(std::size_t preset=0;preset<presets.size();++preset){
    const Reading* r=&readings[pianos+perPreset*preset];
    const auto& typical=r[0];const auto& loudest=r[1];const auto& strong=r[2];
    const double reading=median(typical.events);
    const double loud=*std::max_element(loudest.events.begin(),loudest.events.end());
    const auto [step,least]=stepOf(loudest,strong);
    const double noteStep=stepOf(r[3],r[4]).first;
    const double peak=std::max({typical.peakDbfs,loudest.peakDbfs,strong.peakDbfs,r[3].peakDbfs,r[4].peakDbfs});
    std::printf("%-18s typical %6.2f VU  loudest chords %6.2f VU  velocity 110 to 127 %+.2f dB (least %+.2f), "
                "single notes %+.2f dB  peak %6.2f dBFS\n",presets[preset].name,reading,loud,step,least,noteStep,peak);
    const char* name=presets[preset].name;
    expect(std::abs(reading-targetVu)<=presetWindowDb,name,"typical playing is not near the target",reading);
    expect(noteStep>0,name,"the single notes at velocity 127 are no louder than at 110",noteStep);
    expect(step>0,name,"the chords at velocity 127 are no louder than at 110",step);
    expect(peak<=peakCeilingDbfs,name,"a sample passes the ceiling",peak);
  }
  const auto scales=voicedScales(jobs);
  for(int body=0;body<bodies;++body)for(int mix=0;mix<keyMixCount;++mix){
    const Evenness& e=scales[static_cast<std::size_t>(body*keyMixCount+mix)];
    char what[96];
    std::snprintf(what,sizeof(what),"%s, pairs %g %g %g %g",keyra::bodyNames[static_cast<std::size_t>(body)],
                  keyMixes[mix][0],keyMixes[mix][1],keyMixes[mix][2],keyMixes[mix][3]);
    std::printf("%-36s furthest key (MIDI %d) %+.2f dB off the even scale, %.2f dB from key to key\n",what,e.key+21,e.furthest,e.step);
    expect(std::abs(e.furthest)<=keyWindowDb,what,"a key is off the even scale; write KeyVoicing.h again (--write-keys)",e.furthest);
  }
  if(!check)return 0;
  if(failures==0)std::printf("Keyra levels: all checks passed\n");
  return failures==0?0:1;
}
}

int main(int argc,char** argv){
  int jobs=static_cast<int>(std::max(1u,std::thread::hardware_concurrency()));
  const bool check=argc>=2&&!std::strcmp(argv[1],"--check");
  const bool write=argc>=3&&!std::strcmp(argv[1],"--write-keys");
  bool known=check||write||(argc>=2&&!std::strcmp(argv[1],"--report"));
  for(int i=write?3:2;known&&i<argc;++i){
    if(!std::strcmp(argv[i],"--jobs")&&i+1<argc){
      const char* start=argv[++i];
      const char* end=start+std::strlen(start);
      const auto parsed=std::from_chars(start,end,jobs);
      known=parsed.ec==std::errc{}&&parsed.ptr==end;
      jobs=std::max(1,jobs);
    }
    else known=false;
  }
  if(!known){
    std::fprintf(stderr,"usage: KeyraLevels (--report | --check | --write-keys Source/DSP/KeyVoicing.h) [--jobs N]\n");
    return 2;
  }
  return write?writeKeys(argv[2],jobs):run(jobs,check);
}
