// Keyra's levels on Reason's channel meter, the scale the portfolio's newer
// instruments are calibrated on (Aculele's Tools/ReasonMeter.h): the RMS over
// a sliding 300 ms window of the louder channel, read 12 dB up, so 0 VU is
// -12 dBFS RMS (Reason's VU offset as its users report it; the manual gives
// no default).
//
//   KeyraLevels --report [--jobs N]   every factory preset's readings and each
//                                     piano's outputScale correction
//   KeyraLevels --check [--jobs N]    the audio-tier test Keyra.Levels
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
//
// A piano's calibration reads its default sound 20 dB down, below the output
// stage, and adds the 20 dB back; the factor --report prints brings it to
// targetVu at the default Output (KeyraEngine.cpp's outputScale). The same
// reading at Mic 1, the tube alone, gives the factor that brings it to its
// pair's (KeyraEngine.cpp's tubeScale). --check fails unless each piano's
// default sound reads targetVu within half a decibel at Mic 0 and at Mic 1
// (the Kawai's down to 1.05 dB under there, below), where its loudest chords
// also stay out of the red and play louder than at
// 110; every preset without felt reads within 2 dB of it; the loudest
// chords of every preset stay out of the red, under 0 VU, with no sample over
// the stage's ceiling; and the chords still play louder at velocity 127 than
// at 110 through the guard, by their median difference: each strike's own
// spread (touchSpreadDb) can turn one chord over. The felt presets read lower and are not
// held to the target: the felt stops each note within a fraction of a second,
// so the meter's 300 ms holds less of it, while its attack peaks as high as
// the others' and raising them would press every hard note into the limiter.
// When an engine change moves a reading, re-pin outputScale and tubeScale
// rather than move these bounds.
#include "DSP/KeyraEngine.h"
#include "DSP/KeyraPresets.h"
#include "DSP/OutputStage.h"

#include <algorithm>
#include <atomic>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <functional>
#include <thread>
#include <vector>

namespace {
constexpr double rate=48000,slotSeconds=1.5,holdSeconds=.8,vuOffsetDb=12,targetVu=-9,belowDb=20;
constexpr int block=256;
struct Event {std::vector<int> notes;int velocity;};
const std::vector<std::vector<int>> chords{
  {60,64,67},{60,65,69},{59,62,67},{57,60,64},
  {48,55,64,67,72},{41,53,57,60,65},{43,55,59,62,67},{45,52,57,60,64}};
constexpr int singles=22,velocities[]{70,90,110};
std::vector<Event> typicalPlaying(){
  std::vector<Event> events;
  for(int velocity:velocities){
    for(int i=0;i<singles;++i)events.push_back({{21+4*i},velocity});
    for(const auto& chord:chords)events.push_back({chord,velocity});
  }
  return events;
}
// The chords at one velocity, five rounds of them: every strike lands at its
// own spread (touchSpreadDb), and through the guard the uprights' chords at
// 127 and 110 differ by about a tenth of a decibel, so one round's draws
// decided the step's sign (the shipping upright read +0.08 dB over one round
// and -0.04 dB over five).
constexpr int rounds=5;
std::vector<Event> chordRounds(int velocity){
  std::vector<Event> events;
  for(int round=0;round<rounds;++round)for(const auto& chord:chords)events.push_back({chord,velocity});
  return events;
}

struct Reading {std::vector<double> events;double peakDbfs=-300;};
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

int run(int jobs,bool check){
  const auto& presets=keyra::factoryPresets;
  constexpr std::size_t pianos=keyra::pianoCount;
  const char* const pianoNames[pianos]{"grand","upright","kawai"};
  const auto typicalEvents=typicalPlaying(),loudestEvents=chordRounds(127),strongEvents=chordRounds(110);
  // Tasks: each piano's default sound below the stage, at Mic 0 and at 1,
  // and its loudest chords and the same chords at 110 at Mic 1 as heard;
  // then each preset's typical playing, loudest chords and the same chords
  // at 110 as heard.
  const std::size_t calibrations=4*pianos,count=calibrations+3*presets.size();
  std::vector<Reading> readings(count);
  parallel(count,jobs,[&](std::size_t task){
    if(task<calibrations){
      const std::size_t kind=task/pianos;
      keyra::Parameters parameters;parameters.build=keyra::measuredBuild(static_cast<keyra::Piano>(task%pianos));
      parameters.mic=kind==0?0.f:1.f;
      if(kind<2)parameters.gain*=static_cast<float>(std::pow(10.,-belowDb/20));
      readings[task]=play(parameters,kind<2?typicalEvents:kind==2?loudestEvents:strongEvents);
      return;
    }
    const std::size_t preset=(task-calibrations)/3,kind=(task-calibrations)%3;
    const auto parameters=keyra::withPreset(keyra::Parameters{},presets[preset]);
    readings[task]=play(parameters,kind==0?typicalEvents:kind==1?loudestEvents:strongEvents);
  });

  int failures=0;
  const auto expect=[&failures](bool ok,const char* what,const char* message,double value){
    if(ok)return;
    std::printf("FAIL %s: %s (%.2f)\n",what,message,value);++failures;
  };
  for(std::size_t piano=0;piano<pianos;++piano){
    const double reading=median(readings[piano].events)+belowDb,tube=median(readings[pianos+piano].events)+belowDb;
    const auto& loudest=readings[2*pianos+piano];const auto& strong=readings[3*pianos+piano];
    const double loud=*std::max_element(loudest.events.begin(),loudest.events.end());
    std::vector<double> steps;
    for(std::size_t chord=0;chord<loudest.events.size();++chord)steps.push_back(loudest.events[chord]-strong.events[chord]);
    const double step=median(steps);
    std::printf("%-8s default sound %6.2f VU; outputScale x%.5f (%+.2f dB) for %.0f VU\n",pianoNames[piano],
                reading,std::pow(10.,(targetVu-reading)/20),targetVu-reading,targetVu);
    std::printf("%-8s at Mic 1 %6.2f VU; tubeScale x%.5f (%+.2f dB) for Mic 0's  loudest chords %6.2f VU  "
                "velocity 110 to 127 %+.2f dB  peak %6.2f dBFS\n",
                pianoNames[piano],tube,std::pow(10.,(reading-tube)/20),reading-tube,loud,step,loudest.peakDbfs);
    expect(std::abs(reading-targetVu)<=.5,pianoNames[piano],"its default sound is not at the target",reading);
    // The Kawai's tube may read up to 1.05 dB under the target: within 0.5,
    // its loudest chords at Mic 1 reach the red (+0.07 VU at -9.73), and the
    // owner chose a quieter tube over evening out its loud A2 recordings
    // (KeyraEngine.cpp's tubeScale, Docs/decisions.md, 2026-10-31).
    const double tubeBelow=static_cast<keyra::Piano>(piano)==keyra::Piano::kawai?1.05:.5;
    expect(tube-targetVu<=.5&&targetVu-tube<=tubeBelow,pianoNames[piano],"its sound at Mic 1 is not at the target",tube);
    expect(loud<0,pianoNames[piano],"the loudest chords at Mic 1 reach the red",loud);
    expect(step>0,pianoNames[piano],"the chords at velocity 127 are no louder than at 110 at Mic 1",step);
    expect(std::max(loudest.peakDbfs,strong.peakDbfs)<=20*std::log10(protocodus::OutputStage<2>::kCeiling)+.01,
           pianoNames[piano],"a sample at Mic 1 passes the ceiling",std::max(loudest.peakDbfs,strong.peakDbfs));
  }
  for(std::size_t preset=0;preset<presets.size();++preset){
    const auto& typical=readings[calibrations+3*preset];const auto& loudest=readings[calibrations+3*preset+1];
    const auto& strong=readings[calibrations+3*preset+2];
    const double reading=median(typical.events);
    const double loud=*std::max_element(loudest.events.begin(),loudest.events.end());
    std::vector<double> steps;
    for(std::size_t chord=0;chord<loudest.events.size();++chord)steps.push_back(loudest.events[chord]-strong.events[chord]);
    const double step=median(steps),least=*std::min_element(steps.begin(),steps.end());
    const double peak=std::max({typical.peakDbfs,loudest.peakDbfs,strong.peakDbfs});
    std::printf("%-18s typical %6.2f VU  loudest chords %6.2f VU  velocity 110 to 127 %+.2f dB (least %+.2f)  peak %6.2f dBFS\n",
                presets[preset].name,reading,loud,step,least,peak);
    const char* name=presets[preset].name;
    if(presets[preset].mute==0)expect(std::abs(reading-targetVu)<=2,name,"typical playing is not near the target",reading);
    expect(loud<0,name,"the loudest chords reach the red",loud);
    expect(step>0,name,"the chords at velocity 127 are no louder than at 110",step);
    expect(peak<=20*std::log10(protocodus::OutputStage<2>::kCeiling)+.01,name,"a sample passes the ceiling",peak);
  }
  if(!check)return 0;
  if(failures==0)std::printf("Keyra levels: all checks passed\n");
  return failures==0?0:1;
}
}

int main(int argc,char** argv){
  int jobs=static_cast<int>(std::max(1u,std::thread::hardware_concurrency()));
  bool check=false,known=argc>=2;
  if(known)check=!std::strcmp(argv[1],"--check"),known=check||!std::strcmp(argv[1],"--report");
  for(int i=2;known&&i<argc;++i){
    if(!std::strcmp(argv[i],"--jobs")&&i+1<argc)jobs=std::max(1,std::atoi(argv[++i]));
    else known=false;
  }
  if(!known){std::fprintf(stderr,"usage: KeyraLevels --report | --check [--jobs N]\n");return 2;}
  return run(jobs,check);
}
