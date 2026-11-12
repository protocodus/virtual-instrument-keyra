// The engine's contracts as a front end meets them: the keys, pedals and
// controllers, the action's noises beside the strings, every control's
// effect, and the real-time rules. The model's own physics are in
// piano_model_tests.cpp.
//
// Two settings take the engine's two sources apart: `strings()` plays with
// Mechanics at 0, so only the model sounds, and `action()` with every
// microphone pair at 0, so only the action does.
#include "DSP/KeyraEngine.h"
#include "DSP/KeyraPresets.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <limits>
#include <memory>
#include <new>
#include <thread>
#include <vector>

namespace {
bool trap=false;std::size_t allocations=0;int failures=0;
void check(bool condition,const char* message){if(!condition){std::cerr<<"FAIL: "<<message<<'\n';++failures;}}
constexpr double pi=3.14159265358979323846;
using Audio=std::vector<float>;
struct Take {
  Audio audio;double rate=48000;
  std::size_t at(double seconds) const {return std::min(audio.size()/2,static_cast<std::size_t>(std::lround(seconds*rate)));}
  // RMS level of both channels over a span, dB re full scale.
  double db(double from,double to) const {
    double sum=0;const std::size_t a=at(from),b=at(to);
    for(std::size_t i=2*a;i<2*b;++i)sum+=static_cast<double>(audio[i])*audio[i];
    return 10*std::log10(sum/std::max<std::size_t>(1,2*(b-a))+1e-30);
  }
  double peak(double from,double to) const {
    double top=0;for(std::size_t i=2*at(from);i<2*at(to);++i)top=std::max(top,std::abs(static_cast<double>(audio[i])));
    return top;
  }
  // The level of one frequency in the mid channel over a span (Hann window), dB.
  double tone(double hz,double from,double to) const {
    const std::size_t a=at(from),n=at(to)-a;double re=0,im=0;
    for(std::size_t i=0;i<n;++i){
      const double x=.5*(audio[2*(a+i)]+audio[2*(a+i)+1])*(.5-.5*std::cos(2*pi*i/(n-1))),w=2*pi*hz*i/rate;
      re+=x*std::cos(w);im+=x*std::sin(w);}
    return 20*std::log10(4*std::hypot(re,im)/n+1e-15);
  }
  // The strongest frequency within `cents` of `hz`, to a tenth of a cent.
  double pitch(double hz,double from,double to,double cents=70) const {
    double best=hz,top=-400;
    for(double step:{5.,.5,.1}){const double centre=best,span=step==5.?cents:step*10;
      for(double c=-span;c<=span;c+=step){const double f=centre*std::pow(2.,c/1200),level=tone(f,from,to);
        if(level>top){top=level;best=f;}}}
    return best;
  }
  // The share of a span's power above `hz`, dB: both channels through a
  // fourth-order Butterworth high-pass (two state-variable sections).
  double above(double hz,double from,double to) const {
    const double g=std::tan(pi*hz/rate);double high=0,all=0;
    for(int ch=0;ch<2;++ch){double state[2][2]{};
      for(std::size_t i=at(from);i<at(to);++i){double x=audio[2*i+ch];all+=x*x;
        for(int stage=0;stage<2;++stage){const double r=stage?.765367:1.847759;double* s=state[stage];
          const double hp=(x-(r+g)*s[0]-s[1])/(1+r*g+g*g),bp=g*hp+s[0],lp=g*bp+s[1];
          s[0]=g*hp+bp;s[1]=g*bp+lp;x=hp;}
        high+=x*x;}}
    return 10*std::log10((high+1e-30)/(all+1e-30));
  }
  // How alike the channels are over a span, -1 to 1.
  double correlation(double from,double to) const {
    double ll=0,rr=0,lr=0;
    for(std::size_t i=at(from);i<at(to);++i){const double l=audio[2*i],r=audio[2*i+1];ll+=l*l;rr+=r*r;lr+=l*r;}
    return lr/std::sqrt(ll*rr+1e-30);
  }
  bool safe() const {return std::all_of(audio.begin(),audio.end(),[](float x){return std::isfinite(x)&&x>=-1&&x<=1;});}
};
void render(keyra::Engine& engine,Take& take,double seconds,int block=127){
  std::array<float,512> l{},r{};
  int left=static_cast<int>(std::lround(seconds*take.rate));
  while(left>0){const int n=std::min(block,left);engine.process(l.data(),r.data(),n);
    for(int i=0;i<n;++i){take.audio.push_back(l[static_cast<std::size_t>(i)]);take.audio.push_back(r[static_cast<std::size_t>(i)]);}
    left-=n;}
}
// Strikes at exactly the velocity given, on an engine started afresh with
// these controls: constructing one designs every piano, so the tests share it.
struct Bench {
  keyra::Engine engine{48000};
  Take take;
  Bench(){engine.setSteadyStrikesForMeasurement(true);}
  void start(const keyra::Parameters& parameters){engine.setParameters(parameters);engine.reset();take=Take{};}
  void run(double seconds){render(engine,take,seconds);}
  double now() const {return take.audio.size()/2/take.rate;}
};
keyra::Parameters strings(){keyra::Parameters p;p.mechanics=0;return p;}
keyra::Parameters action(){keyra::Parameters p;p.mechanics=1;for(float& level:p.mic)level=0;return p;}
double hertz(int note,double a4=440){return a4*std::pow(2.,(note-69)/12.);}
double cents(double f,double reference){return 1200*std::log2(f/reference);}
}
void* operator new(std::size_t size){if(trap)++allocations;if(void* p=std::malloc(size))return p;throw std::bad_alloc();}
void* operator new[](std::size_t size){return ::operator new(size);}
void operator delete(void* p) noexcept {std::free(p);}void operator delete[](void* p) noexcept {std::free(p);}
void operator delete(void* p,std::size_t) noexcept {std::free(p);}void operator delete[](void* p,std::size_t) noexcept {std::free(p);}

int main(){
  auto bench=std::make_unique<Bench>();auto& b=*bench;auto& e=b.engine;
  {
    check(keyra::Parameters{}.mechanics==keyra::defaultMechanicsGain,
          "a new instrument uses the chosen Mechanics gain");
    check(keyra::legacyMechanicsGain==1.f&&keyra::maximumMechanicsGain==2.f,
          "legacy Mechanics gains retain their physical range");
    check(keyra::mechanicsGainFromPosition(0)==0&&keyra::mechanicsGainFromPosition(1)==2
          &&keyra::mechanicsPositionFromGain(0)==0&&keyra::mechanicsPositionFromGain(2)==1,
          "Mechanics display endpoints preserve the gain endpoints");
    check(keyra::mechanicsGainFromPosition(.4)==.175f
          &&keyra::mechanicsGainFromPosition(keyra::defaultMechanicsPosition)==keyra::defaultMechanicsGain
          &&keyra::mechanicsPositionFromGain(keyra::defaultMechanicsGain)==keyra::defaultMechanicsPosition,
          "forty percent knob travel selects the exact chosen gain");
    const float nan=std::numeric_limits<float>::quiet_NaN(),inf=std::numeric_limits<float>::infinity();
    check(keyra::mechanicsGainFromPosition(-1)==0&&keyra::mechanicsGainFromPosition(inf)==2
          &&keyra::mechanicsGainFromPosition(nan)==0&&keyra::mechanicsPositionFromGain(-1)==0
          &&keyra::mechanicsPositionFromGain(inf)==1&&keyra::mechanicsPositionFromGain(nan)==0,
          "Mechanics display conversions bound invalid input");
    bool monotone=true;float previousGain=-1,previousPosition=-1,maxGainError=0,maxPositionError=0;
    for(int i=0;i<=16384;++i){
      const float position=static_cast<float>(i)/16384,gain=2*position;
      const float displayed=keyra::mechanicsPositionFromGain(gain),played=keyra::mechanicsGainFromPosition(position);
      monotone=monotone&&played>previousGain&&displayed>previousPosition;
      maxGainError=std::max(maxGainError,std::abs(keyra::mechanicsGainFromPosition(displayed)-gain));
      maxPositionError=std::max(maxPositionError,std::abs(keyra::mechanicsPositionFromGain(played)-position));
      previousGain=played;previousPosition=displayed;
    }
    // Two float-domain conversions and the intervening power function: a
    // small multiple of float epsilon, independent of any audio tolerance.
    constexpr float epsilon=std::numeric_limits<float>::epsilon();
    check(monotone&&maxGainError<=8*epsilon*keyra::maximumMechanicsGain&&maxPositionError<=8*epsilon,
          "Mechanics display taper is monotone and round-trips in the float domain");
  }
  {
    // Silence, the host's blocks, and starting over.
    const auto score=[](keyra::Engine& engine,Take& take,int block){
      // A top key with them: its blow knocks on the capo bar, and each key's hammer is caught.
      render(engine,take,.05,block);engine.noteOn(60,.7f);engine.noteOn(36,.9f,2);engine.noteOn(98,.8f);render(engine,take,.2,block);
      engine.controlChange(64,127);engine.noteOff(60);render(engine,take,.15,block);
      engine.controlChange(64,0);engine.noteOff(36,2);render(engine,take,.2,block);
    };
    b.start(keyra::Parameters{});b.run(.1);
    check(b.take.peak(0,.1)==0,"a fresh engine is exactly silent");
    Take byOne,byMany,again,other;
    b.start(keyra::Parameters{});score(e,byOne,1);
    b.start(keyra::Parameters{});score(e,byMany,512);
    check(byOne.audio==byMany.audio,"the output does not depend on the host's blocks");
    b.start(keyra::Parameters{});score(e,again,127);
    auto fresh=std::make_unique<keyra::Engine>(48000);fresh->setSteadyStrikesForMeasurement(true);
    score(*fresh,other,127);
    check(again.audio==other.audio,"a reset engine plays as a fresh one");
    check(byOne.db(.05,.25)>-40,"the score sounds");
    // Let go, a short note falls silent, exactly, and the engine sleeps.
    b.start(keyra::Parameters{});e.noteOn(60,.7f);b.run(.3);e.noteOff(60);b.run(40);
    std::size_t last=0;for(std::size_t i=0;i<b.take.audio.size();++i)if(b.take.audio[i]!=0)last=i;
    std::cout<<"a staccato C4 is silent after "<<last/2/48000.<<" s\n";
    check(last/2<b.take.at(39),"a note let go falls exactly silent");
  }
  {
    // No two strikes land alike, unless a measurement asks for steady ones.
    // Under the pedal a key let go is silent, so only its landing sounds.
    const auto spread=[&](bool steady){
      e.setSteadyStrikesForMeasurement(steady);b.start(action());e.controlChange(64,127);b.run(1.5);
      double low=1e9,high=-1e9;
      for(int k=0;k<8;++k){const double t=b.now();e.noteOn(60,.6f);b.run(.25);e.noteOff(60);b.run(.75);
        const double level=b.take.db(t,t+.25);low=std::min(low,level);high=std::max(high,level);}
      e.setSteadyStrikesForMeasurement(true);
      return high-low;
    };
    const double varied=spread(false),steady=spread(true);
    std::cout<<"eight landings of one key spread "<<varied<<" dB, steady "<<steady<<" dB\n";
    check(varied>.5&&varied<8,"strikes of one key vary as a player's do");
    check(steady<.05,"steady strikes land alike");
  }
  {
    // A key belongs to every channel that holds it; its damper falls when
    // the last lets go.
    b.start(strings());e.noteOn(60,.7f,1);b.run(1);const double down=b.take.db(.8,1.0);
    b.start(strings());e.noteOn(60,.7f,1);e.noteOn(60,.7f,2);b.run(.5);
    e.noteOff(60,1);b.run(.5);const double held=b.take.db(.8,1.0);
    e.noteOff(60,2);b.run(.5);const double damped=b.take.db(1.3,1.5);
    std::cout<<"C4 held by a second channel "<<held<<" dB (one strike kept down "<<down<<" dB), let go "<<damped<<" dB\n";
    // The second channel's strike lands on the first's, so it is no quieter
    // than one strike kept down.
    check(held>down-1,"a key another channel holds keeps ringing");
    check(damped<held-30,"the damper falls when the last channel lets go");
    e.noteOff(60,2);e.noteOff(60,7);b.run(.05);
    check(b.take.safe(),"a key let go twice stays let go");
    // From F6 up there are no dampers.
    b.start(strings());e.noteOn(96,.7f);b.run(.3);e.noteOff(96);b.run(.5);
    Take open=b.take;
    b.start(strings());e.noteOn(96,.7f);b.run(.8);
    check(std::abs(open.db(.6,.8)-b.take.db(.6,.8))<1,"a key without a damper rings on when it is let go");
  }
  {
    // The sustain pedal is continuous, and catches what still rings.
    const auto after=[&](int pedal){
      b.start(strings());e.controlChange(64,pedal);e.noteOn(60,.7f);b.run(.4);e.noteOff(60);b.run(.6);
      return b.take.db(.8,1.0);
    };
    // The dampers lift between a fifth and seven tenths of the way down
    // (PianoModel.cpp, damperGoal; KeyraEngine.cpp, pedalLift), so that is
    // where the pedal works by degrees.
    const int travel[]{0,26,45,64,76,86,95,127};double level[8];bool rising=true;int between=0;
    std::cout<<"C4 let go, by the pedal's travel:";
    for(int k=0;k<8;++k){level[k]=after(travel[k]);std::cout<<' '<<travel[k]<<": "<<level[k]<<" dB";
      rising=rising&&(k==0||level[k]>=level[k-1]-.5);}
    std::cout<<'\n';
    const double up=level[0],down=level[7];
    for(int k=1;k<7;++k)between+=level[k]>up+3&&level[k]<down-3;
    check(down>up+30,"the sustain pedal holds a note let go");
    // Short of the lift the key's own damper is on, and the travel has begun
    // to loosen every other string's, which answer a little.
    check(level[1]<up+3&&std::abs(level[6]-down)<1,"the pedal's ends leave the dampers on and off the strings");
    check(rising&&between>=2,"between its ends the pedal damps by degrees");
    b.start(strings());e.controlChange(64,127);e.noteOn(48,.8f);b.run(.4);e.noteOff(48);b.run(.4);
    const double before=b.take.db(.6,.8);
    e.controlChange(64,0);b.run(.06);e.controlChange(64,127);b.run(.6);
    const double caught=b.take.db(1.0,1.2),later=b.take.db(1.26,1.46);
    std::cout<<"repedalled C3: before "<<before<<" dB, caught "<<caught<<" dB, then "<<later<<" dB\n";
    check(caught<before-3&&caught>before-40,"a quick change of pedal catches some of the ring");
    // Under the grazing pedal C3 itself falls 11 dB/s, 2.9 dB between these
    // windows, so a limit of 3 dB stood 0.1 dB from the pedal's own decay
    // and 2.7.0's 3.1 dB crossed it.
    check(later>caught-4,"what the pedal caught rings on");
    // The full pedal's felt still grazes the strings, as the owner chose
    // (KeyraEngine.cpp, pedalLift): a chord let go under it is 60 dB down
    // after 9.6 s on the concert grand, where clear of the strings it took
    // 17.4 s.
    b.start(strings());e.controlChange(64,127);
    for(int n:{48,60,72,84})e.noteOn(n,80/127.f);
    b.run(.5);for(int n:{48,60,72,84})e.noteOff(n);b.run(12);
    const double let=b.take.db(.55,.65),early=b.take.db(7.45,7.55),late=b.take.db(12.3,12.4);
    std::cout<<"a chord let go under the full pedal: "<<early-let<<" dB after 7 s, "<<late-let<<" dB after 12 s\n";
    check(early>let-60&&late<let-60,"a chord under the full pedal falls 60 dB in 7 to 12 s");
  }
  {
    // The sostenuto holds the dampers of the keys that are down as it goes
    // down, and no others.
    b.start(strings());e.noteOn(60,.7f);b.run(.3);e.controlChange(66,127);e.noteOff(60);
    e.noteOn(67,.7f);b.run(.3);e.noteOff(67);b.run(.5);
    const double c4=b.take.tone(b.take.pitch(hertz(60),.8,1.1),.8,1.1),g4=b.take.tone(b.take.pitch(hertz(67),.8,1.1),.8,1.1);
    std::cout<<"sostenuto: C4 "<<c4<<" dB, G4 struck after it "<<g4<<" dB\n";
    check(c4>g4+25,"the sostenuto holds the keys down at its rising edge only");
    e.controlChange(66,0);b.run(.5);
    check(b.take.db(1.4,1.6)<c4-25,"the sostenuto lets its dampers fall");
    b.start(strings());e.controlChange(66,127);e.noteOn(60,.7f);b.run(.3);e.noteOff(60);b.run(.5);
    check(b.take.db(.6,.8)<b.take.db(.1,.3)-30,"a sostenuto pressed before the key holds nothing");
  }
  {
    // C0, C#0 and D0 are the soft, sostenuto and sustain pedals while held,
    // on their own channel's count, and the engine reports the pedals.
    b.start(strings());
    e.noteOn(14,1,3);check(e.pedalState(3).sustain==1&&e.pedalState(0).sustain==1&&e.pedalState(1).sustain==0,"D0 is the sustain pedal on its channel");
    e.noteOn(14,1,3);e.noteOff(14,3);check(e.pedalState(3).sustain==1,"a switch held twice stays down until both let go");
    e.noteOff(14,3);check(e.pedalState(0).sustain==0,"D0 let go lifts the pedal");
    e.noteOn(13,1);check(e.pedalState(1).sostenuto==1,"C#0 is the sostenuto");e.noteOff(13);
    e.noteOn(12,1);check(e.pedalState(1).soft==1,"C0 is the soft pedal");e.noteOff(12);
    e.controlChange(64,64,5);e.controlChange(67,127,5);
    check(std::abs(e.pedalState(5).sustain-64/127.f)<1e-6f&&e.pedalState(5).soft==1&&e.pedalState(4).sustain==0,"the pedals are reported per channel");
    keyra::Parameters panel=strings();panel.sustain=.3f;panel.sostenuto=1;e.setParameters(panel);
    check(e.pedalState(4).sustain==.3f&&std::abs(e.pedalState(5).sustain-64/127.f)<1e-6f&&e.pedalState(9).sostenuto==1,"the panel's pedals reach every channel");
    check(e.pedalState(17).sustain==0&&e.pedalState(-1).sustain==0,"a channel that does not exist reports no pedal");
    b.run(.1);check(b.take.peak(0,.1)==0,"the switches play no note");
    b.start(strings());e.noteOn(14,1);e.noteOn(60,.7f);b.run(.3);e.noteOff(60);b.run(.5);const double held=b.take.db(.6,.8);
    e.noteOff(14);b.run(.5);
    check(held>b.take.db(.1,.3)-15&&b.take.db(1.1,1.3)<held-30,"D0 holds the dampers as the pedal does");
  }
  {
    // The soft pedal: a grand's shifts the hammers off a string, an
    // upright's halves the blow.
    for(const auto body:{keyra::model::Body::concertGrand,keyra::model::Body::upright}){
      auto p=strings();p.body=body;
      b.start(p);e.noteOn(60,.7f);b.run(.5);const double loud=b.take.db(.02,.4),bright=b.take.above(2000,.02,.4);
      b.start(p);e.controlChange(67,127);e.noteOn(60,.7f);b.run(.5);
      std::cout<<keyra::bodyNames[static_cast<int>(body)]<<" soft pedal: "<<b.take.db(.02,.4)-loud<<" dB, above 2 kHz "<<b.take.above(2000,.02,.4)-bright<<" dB more\n";
      check(b.take.db(.02,.4)<loud-1.5&&b.take.db(.02,.4)>loud-15,"the soft pedal plays softer");
      check(b.take.above(2000,.02,.4)<bright-.5,"the soft pedal plays darker");
    }
  }
  {
    // The mod wheel lays felt on the sounding strings, held keys' too,
    // smoothly, and lifts it again.
    const auto held=[&](int wheel){
      b.start(strings());e.noteOn(48,.8f);b.run(.5);e.controlChange(1,wheel);b.run(.7);
      return b.take.db(1.0,1.2);
    };
    const double open=held(0),some=held(40),full=held(127);
    std::cout<<"held C3 under the wheel: 0 "<<open<<" dB, 40 "<<some<<" dB, 127 "<<full<<" dB\n";
    check(full<open-25,"the wheel damps a held key");
    check(some<open-2&&some>full+5,"the wheel damps by degrees");
    // The felt comes down over the dampers' travel, not at once.
    double step=0;for(std::size_t i=b.take.at(.5);i<b.take.at(.6);++i)step=std::max(step,std::abs(static_cast<double>(b.take.audio[2*i])-b.take.audio[2*i-2]));
    double before=0;for(std::size_t i=b.take.at(.4);i<b.take.at(.5);++i)before=std::max(before,std::abs(static_cast<double>(b.take.audio[2*i])-b.take.audio[2*i-2]));
    check(step<=1.5*before,"the wheel's felt lands without a click");
    auto p=strings();p.mute=1;b.start(p);e.noteOn(48,.8f);b.run(.5);
    Take muted=b.take;
    b.start(strings());e.noteOn(48,.8f);b.run(.5);
    check(muted.db(.3,.5)<b.take.db(.3,.5)-20,"Felt mute damps as the wheel does");
  }
  {
    // All sound off, reset all controllers, all notes off.
    b.start(keyra::Parameters{});e.controlChange(64,127);e.noteOn(48,.9f);e.noteOn(60,.9f,2);b.run(.3);
    e.controlChange(120,0);const double t=b.now();b.run(.2);
    check(b.take.peak(t,t+.2)==0,"all sound off silences every channel's strings at once");
    b.start(strings());e.controlChange(64,127);e.controlChange(1,90);e.pitchBend(2);e.noteOn(60,.7f);b.run(.2);e.noteOff(60);
    e.controlChange(121,0);
    check(e.pedalState(1).sustain==0,"reset all controllers lifts the pedals");
    b.run(.6);check(b.take.db(.6,.8)<b.take.db(.05,.2)-30,"reset all controllers lets a pedalled note fall");
    b.start(strings());e.noteOn(60,.7f);e.noteOn(64,.7f);b.run(.3);e.controlChange(123,0);b.run(.5);
    check(b.take.db(.6,.8)<b.take.db(.1,.3)-30,"all notes off lets every key go");
    // Against the key let go under the pedal, not the key kept down: the
    // pedal holds the dampers a little less clear of the strings than a key
    // does (pedalLift), which takes 1.0 dB by then on its own, the whole of
    // the 1 dB this check allowed when it compared with the key kept down.
    b.start(strings());e.controlChange(64,127);e.noteOn(60,.7f);b.run(.3);e.noteOff(60);b.run(.5);const double pedalled=b.take.db(.6,.8);
    b.start(strings());e.controlChange(64,127);e.noteOn(60,.7f);b.run(.3);e.controlChange(123,0);b.run(.5);
    std::cout<<"C4 let go under the pedal "<<pedalled<<" dB, by all notes off "<<b.take.db(.6,.8)<<" dB\n";
    check(std::abs(b.take.db(.6,.8)-pedalled)<.1,"all notes off leaves the pedal down");
  }
  {
    // The action beside the strings: every key lands and returns, louder with
    // Mechanics, and not at all at 0.
    auto none=action();none.mechanics=0;
    b.start(none);e.noteOn(60,.8f);b.run(.3);e.noteOff(60);e.controlChange(64,127);b.run(.3);e.controlChange(64,0);b.run(.3);
    check(b.take.peak(0,.9)==0,"at Mechanics 0 the action is silent");
    // Read 20 dB down, where the output stage passes it untouched.
    const auto play=[&](float mechanics,keyra::model::Body body,int note){
      auto p=action();p.mechanics=mechanics;p.gain=.07f;p.body=body;p.room=0;
      b.start(p);e.noteOn(note,.8f);b.run(.5);e.noteOff(note);b.run(.5);
    };
    for(const auto body:{keyra::model::Body::concertGrand,keyra::model::Body::upright}){
      play(1,body,60);const double landing=b.take.db(0,.3),back=b.take.db(.5,.8);
      play(2,body,60);
      std::cout<<keyra::bodyNames[static_cast<int>(body)]<<" action at C4: landing "<<landing<<" dB, return "<<back<<" dB\n";
      check(landing>-110&&back>-110,"a key lands and returns");
      check(std::abs(b.take.db(0,.3)-landing-6.02)<.1&&std::abs(b.take.db(.5,.8)-back-6.02)<.5,"Mechanics is the action's amplitude");
    }
    // Every grand plays the measured grand's action, the upright its own.
    play(1,keyra::model::Body::concertGrand,60);Take concert=b.take;
    play(1,keyra::model::Body::babyGrand,60);check(concert.audio==b.take.audio,"the grands share one action");
    play(1,keyra::model::Body::upright,60);check(concert.audio!=b.take.audio,"the upright has its own action");
    // A soft strike's return is quieter than a hard one's: by the recorded
    // releases' own tracking on steady strikes, and as a player's strikes
    // land, no louder against its note than a mezzo forte's is (the mean of
    // eight, since no two land alike).
    const auto back=[&](float velocity,bool steady){
      e.setSteadyStrikesForMeasurement(steady);
      auto p=action();p.gain=.07f;p.room=0;b.start(p);double power=0;
      for(int k=0;k<(steady?1:8);++k){const double t=b.now();e.noteOn(60,velocity);b.run(.5);e.noteOff(60);b.run(.4);
        power+=std::pow(10.,b.take.db(t+.5,t+.8)/10)/(steady?1:8);}
      e.setSteadyStrikesForMeasurement(true);
      return 10*std::log10(power);};
    const double soft=back(.2f,true),middle=back(.63f,true),hard=back(1.f,true);
    const double softPlayed=back(.2f,false),middlePlayed=back(.63f,false);
    std::cout<<"C4's return after velocity 25 "<<soft<<" dB, 80 "<<middle<<" dB, 127 "<<hard<<" dB; as played, 25 "
             <<softPlayed<<" dB, 80 "<<middlePlayed<<" dB\n";
    check(soft<middle-1&&middle<=hard+.5,"a key's return follows its strike");
    check(softPlayed<middlePlayed-6,"a soft strike's return stays under its note");
    // A key held for long returns more quietly (the grand's 2 dB a second).
    {auto p=action();p.gain=.07f;p.room=0;b.start(p);e.noteOn(60,.63f);b.run(3.5);e.noteOff(60);b.run(.4);
     check(std::abs(middle-b.take.db(3.5,3.8)-6)<1.5,"the grand's return fades 2 dB for each second held");}
    // The sustain pedal knocks once at each end of its travel on the grand.
    {auto p=action();p.gain=.07f;b.start(p);b.run(.1);
     for(int v=0;v<=110;v+=10){e.controlChange(64,v);b.run(.02);}
     check(b.take.peak(0,b.now())==0,"the pedal is silent short of its end");
     const double down=b.now();e.controlChange(64,120);b.run(.5);
     check(b.take.db(down,down+.3)>-110,"the pedal knocks as it reaches the bottom");
     const double wobble=b.now();for(int k=0;k<10;++k){e.controlChange(64,k%2?110:30);b.run(.05);}b.run(1.5);
     check(b.take.db(wobble+1.5,wobble+2)<b.take.db(down,down+.3)-40,"half-pedalling knocks no more");
     const double up=b.now();e.controlChange(64,5);b.run(.5);
     check(b.take.db(up,up+.3)>-110,"the pedal knocks as it comes back up");
     p.body=keyra::model::Body::upright;b.start(p);e.controlChange(64,127);b.run(.3);e.controlChange(64,0);b.run(.3);
     check(b.take.peak(0,.6)==0,"the upright has no pedal recording, and plays none");}
    // Under the pedal a key let go does not sound; from F6 up it always does.
    {auto p=action();p.gain=.07f;b.start(p);e.controlChange(64,127);b.run(1.5);
     e.noteOn(60,.7f);b.run(.6);const double t=b.now();e.noteOff(60);b.run(.3);
     const double under=b.take.db(t,t+.3);
     e.noteOn(96,.7f);b.run(.6);const double u=b.now();e.noteOff(96);b.run(.3);
     check(b.take.db(u,u+.3)>under+20,"only a key without a damper returns aloud under the pedal");}
    // The action's room follows Room.
    {auto p=action();p.gain=.07f;p.room=0;b.start(p);e.noteOn(60,.8f);b.run(.6);const double dry=b.take.db(.3,.6);
     p.room=1;b.start(p);e.noteOn(60,.8f);b.run(.6);
     std::cout<<"the landing's tail without the room "<<dry<<" dB, with it "<<b.take.db(.3,.6)<<" dB\n";
     check(b.take.db(.3,.6)>dry+6,"the action sounds in its room");}
  }
  {
    // Tuning, the bend and the stretch.
    const auto a4=[&](float tuning,float bend){
      auto p=strings();p.tuning=tuning;b.start(p);e.pitchBend(bend);e.noteOn(69,.6f);b.run(1.2);
      return b.take.pitch(tuning*std::pow(2.,bend/12.),.2,1.2);
    };
    const double at440=a4(440,0),at432=a4(432,0),bent=a4(440,2);
    std::cout<<"A4 plays "<<at440<<" Hz, tuned to 432 "<<at432<<" Hz, bent two semitones "<<bent<<" Hz\n";
    check(std::abs(cents(at440,440))<2,"A4 is in tune");
    check(std::abs(cents(at432,432))<2,"Tuning moves A4");
    check(std::abs(cents(bent,440)-200)<3,"the bend moves the strings");
    const auto key=[&](int note,float stretch){
      auto p=strings();p.stretch=stretch;p.detune=0;b.start(p);e.noteOn(note,.6f);b.run(1.2);
      // The strike's own sound: in the treble the aftersound, which the
      // bridge does not move, takes over within half a second, a few cents
      // under it (PianoModel.cpp, tune).
      return cents(b.take.pitch(hertz(note),.03,.5,120),hertz(note));
    };
    const double c7[3]{key(96,0),key(96,1),key(96,2)},a1[3]{key(33,0),key(33,1),key(33,2)};
    std::cout<<"C7 at stretch 0, 1, 2: "<<c7[0]<<", "<<c7[1]<<", "<<c7[2]<<" cents; A1: "<<a1[0]<<", "<<a1[1]<<", "<<a1[2]<<" cents\n";
    check(std::abs(c7[0])<3&&std::abs(a1[0])<3,"without stretch the keys are in equal temperament");
    check(c7[1]>c7[0]+3&&c7[2]>c7[1]+3,"the stretch sharpens the treble");
    check(a1[1]<a1[0]-1&&a1[2]<a1[1]-1,"the stretch flattens the bass");
    // A change of tuning reaches what sounds.
    {auto p=strings();b.start(p);e.noteOn(69,.6f);b.run(.5);p.tuning=452;e.setParameters(p);b.run(1.2);
     check(std::abs(cents(b.take.pitch(452,.7,1.7),452))<3,"Tuning retunes sounding strings");}
  }
  {
    // Each control of the piano does what it says.
    const auto note=[&](const keyra::Parameters& p,int key,float velocity,double seconds){
      b.start(p);e.noteOn(key,velocity);b.run(seconds);return b.take;};
    {auto p=strings();p.hammer=-1;const Take soft=note(p,60,.7f,.5);p.hammer=1;const Take hard=note(p,60,.7f,.5);
     std::cout<<"Hammer -1 to 1: above 2 kHz "<<soft.above(2000,.02,.4)<<" to "<<hard.above(2000,.02,.4)<<" dB\n";
     check(hard.above(2000,.02,.4)>soft.above(2000,.02,.4)+6,"harder hammers play brighter");}
    {auto p=strings();const Take fresh=note(p,48,.8f,3);p.age=1;const Take old=note(p,48,.8f,3);
     const double f=fresh.above(1500,2,3)-fresh.above(1500,.05,.3),o=old.above(1500,2,3)-old.above(1500,.05,.3);
     std::cout<<"String age: C3's share above 1.5 kHz falls "<<-f<<" dB over 2.5 s new, "<<-o<<" dB old\n";
     check(o<f-3,"old strings lose their upper partials sooner");}
    {auto p=strings();p.detune=0;const Take pure=note(p,60,.6f,3);p.detune=1;const Take wide=note(p,60,.6f,3);
     // A unison's beat: how far its 50 ms levels stray from a straight fall.
     const auto wobble=[](const Take& t){double sx=0,sy=0,sxx=0,sxy=0;const int n=50;std::array<double,50> y{};
       for(int i=0;i<n;++i){y[i]=t.db(.4+.05*i,.45+.05*i);sx+=i;sy+=y[i];sxx+=i*i;sxy+=i*y[i];}
       const double slope=(n*sxy-sx*sy)/(n*sxx-sx*sx),mean=(sy-slope*sx)/n;double sum=0;
       for(int i=0;i<n;++i){const double d=y[i]-mean-slope*i;sum+=d*d;}
       return std::sqrt(sum/n);};
     std::cout<<"Detune 0 to 1: C4's level wobbles "<<wobble(pure)<<" to "<<wobble(wide)<<" dB\n";
     check(wobble(wide)>wobble(pure)+.5,"detuned unisons beat");}
    {const auto span=[&](float dynamics){auto p=strings();p.dynamics=dynamics;
       return note(p,60,1,.4).db(.02,.4)-note(p,60,.2f,.4).db(.02,.4);};
     const double narrow=span(0),wide=span(1);
     std::cout<<"Dynamics 0 to 1: velocity 25 to 127 spans "<<narrow<<" to "<<wide<<" dB\n";
     check(narrow>4&&wide>narrow+10,"Dynamics widens the span between soft and hard playing");}
    {auto p=strings();const Take open=note(p,72,.8f,.5);p.lid=0;const Take shut=note(p,72,.8f,.5);
     std::cout<<"Lid open to shut: above 2 kHz "<<open.above(2000,.02,.4)<<" to "<<shut.above(2000,.02,.4)<<" dB\n";
     check(shut.above(2000,.02,.4)<open.above(2000,.02,.4)-2,"a closed lid is darker");}
    {// A staccato note leaves the board ringing.
     const auto ring=[&](float soundboard){auto p=strings();p.soundboard=soundboard;p.sympathetic=0;p.duplex=0;p.room=0;
       b.start(p);e.noteOn(48,.9f);b.run(.15);e.noteOff(48);b.run(.5);return b.take.db(.35,.55)-b.take.db(.02,.15);};
     const double dead=ring(0),lively=ring(1);
     std::cout<<"Soundboard 0 to 1: the ring after a staccato C3 "<<dead<<" to "<<lively<<" dB\n";
     check(lively>dead+3,"a livelier soundboard rings longer");}
    {// Under the pedal the open strings answer a struck one.
     const auto wash=[&](float sympathetic){auto p=strings();p.sympathetic=sympathetic;p.duplex=0;p.room=0;
       b.start(p);e.controlChange(64,127);e.noteOn(60,.9f);b.run(1.5);return b.take;};
     auto p=strings();p.sympathetic=0;p.duplex=0;p.room=0;
     b.start(p);e.noteOn(60,.9f);b.run(1.5);const Take alone=b.take;
     const Take dry=wash(0),wet=wash(1);
     // The fundamentals of the octave below C4, which only sympathy rings.
     const auto others=[&](const Take& t){double sum=0;for(int n=36;n<48;++n)sum+=std::pow(10.,t.tone(hertz(n),.5,1.5)/10);return 10*std::log10(sum);};
     std::cout<<"Sympathetic 0 to 1 under the pedal: the octave below rings "<<others(dry)<<" to "<<others(wet)<<" dB (no pedal "<<others(alone)<<")\n";
     check(others(wet)>others(dry)+6,"Sympathetic sets how the open strings answer");}
    {auto p=strings();p.duplex=0;p.sympathetic=0;const Take plain=note(p,84,.9f,.8);p.duplex=1;const Take ringing=note(p,84,.9f,.8);
     check(plain.audio!=ringing.audio,"Duplex changes the treble");
     p.body=keyra::model::Body::upright;p.duplex=0;const Take a=note(p,84,.9f,.4);p.duplex=1;
     check(a.audio==note(p,84,.9f,.4).audio,"the upright has no duplex scale");}
    {// The microphone pairs: each alone sounds, about as loud as the close
     // pair, and further off hears more room and a later sound.
     Take pair[keyra::model::micCount];double dry[keyra::model::micCount];
     for(int m=0;m<keyra::model::micCount;++m){auto p=strings();for(int k=0;k<keyra::model::micCount;++k)p.mic[k]=k==m?1.f:0.f;
       b.start(p);for(int n:{48,60,64,67})e.noteOn(n,.7f);b.run(.6);for(int n:{48,60,64,67})e.noteOff(n);b.run(.6);pair[m]=b.take;
       p.room=0;b.start(p);for(int n:{48,60,64,67})e.noteOn(n,.7f);b.run(.6);dry[m]=b.take.db(0,.6);}
     for(int m=0;m<keyra::model::micCount;++m){
       std::cout<<keyra::micNames[m]<<": "<<pair[m].db(0,.6)<<" dB (without the room "<<dry[m]<<" dB), tail "<<pair[m].db(.8,1.2)-pair[m].db(0,.6)<<" dB, channels alike "<<pair[m].correlation(0,.6)<<'\n';
       check(std::abs(dry[m]-dry[0])<2,"each pair hears the piano as loud as the close pair does");
       for(int k=0;k<m;++k)check(pair[m].audio!=pair[k].audio,"each pair hears its own sound");}
     check(pair[keyra::model::micDistant].db(.8,1.2)-pair[keyra::model::micDistant].db(0,.6)
           >pair[keyra::model::micClose].db(.8,1.2)-pair[keyra::model::micClose].db(0,.6)+6,"the distant pair hears more of the room");
     auto p=strings();for(float& level:p.mic)level=0;b.start(p);e.noteOn(60,.8f);b.run(.3);
     check(b.take.peak(0,.3)==0,"with every pair down the strings are unheard");
     p.mic[keyra::model::micLive]=1;p.room=0;
     b.start(p);e.noteOn(60,.8f);b.run(.2);e.noteOff(60);b.run(.5);const double without=b.take.db(.5,.7);
     p.room=1;b.start(p);e.noteOn(60,.8f);b.run(.2);e.noteOff(60);b.run(.5);
     std::cout<<"Room 0 to 1 at the live pair: the tail "<<without<<" to "<<b.take.db(.5,.7)<<" dB\n";
     check(b.take.db(.5,.7)>without+6,"Room is the room's reverberation");}
    {auto p=strings();p.width=0;const Take mono=note(p,55,.8f,.3);
     bool same=true;for(std::size_t i=0;i<mono.audio.size();i+=2)same=same&&mono.audio[i]==mono.audio[i+1];
     check(same,"at Width 0 the channels are one");
     p.width=1;const Take wide=note(p,55,.8f,.3);p.width=.75f;const Take pairs=note(p,55,.8f,.3);
     check(wide.correlation(0,.3)<pairs.correlation(0,.3),"Width widens the image");}
    {auto p=strings();const Take bare=note(p,60,.8f,.5);p.felt=1;const Take felted=note(p,60,.8f,.5);
     std::cout<<"Practice felt: "<<felted.db(.02,.4)-bare.db(.02,.4)<<" dB, above 1 kHz "<<felted.above(1000,.02,.4)-bare.above(1000,.02,.4)<<" dB more\n";
     check(felted.db(.02,.4)<bare.db(.02,.4)-3&&felted.above(1000,.02,.4)<bare.above(1000,.02,.4)-10,"the practice felt plays softer and darker");}
    {auto p=strings();p.gain=.35f;const Take half=note(p,60,.5f,.3);p.gain=.7f;
     check(std::abs(note(p,60,.5f,.3).db(.02,.3)-half.db(.02,.3)-6.02)<.5,"Output is the level");}
    // The four pianos are four instruments.
    {Take body[keyra::model::bodyCount];
     for(int k=0;k<keyra::model::bodyCount;++k){auto p=strings();p.body=static_cast<keyra::model::Body>(k);body[k]=note(p,36,.8f,.5);
       check(body[k].db(.02,.5)>-40&&body[k].safe(),"every piano plays");
       for(int j=0;j<k;++j)check(body[k].audio!=body[j].audio,"each piano is its own");}}
    // Every factory preset plays, and no two alike.
    {std::vector<Take> preset;
     for(const auto& x:keyra::factoryPresets){auto p=keyra::withPreset(strings(),x);p.mechanics=0;preset.push_back(note(p,60,.7f,.3));
       check(preset.back().db(.02,.3)>-45&&preset.back().safe(),"every preset plays");
       for(std::size_t j=0;j+1<preset.size();++j)check(preset.back().audio!=preset[j].audio,"no two presets are alike");}}
  }
  {
    // A piano changed while it sounds: the strings of the old one stop, and
    // the new one plays.
    auto p=strings();b.start(p);e.controlChange(64,127);e.noteOn(48,.9f);b.run(.3);
    p.body=keyra::model::Body::upright;e.setParameters(p);b.run(.3);e.noteOn(60,.7f);b.run(.3);
    check(b.take.safe()&&b.take.db(.6,.9)>-45,"a piano changed while it sounds plays on");
    const double changed=b.take.db(.6,.9);
    b.start(p);e.controlChange(64,127);b.run(.6);e.noteOn(60,.7f);b.run(.3);
    check(std::abs(changed-b.take.db(.6,.9))<1,"the new piano plays as itself");
  }
  {
    // Sample rates: the same piano at each.
    double level48=0;
    for(const double rate:{48000.,44100.,88200.,96000.,192000.,22050.}){
      auto engine=std::make_unique<keyra::Engine>(rate);engine->setSteadyStrikesForMeasurement(true);engine->setParameters(strings());
      Take take;take.rate=rate;engine->noteOn(69,.7f);render(*engine,take,1.2);
      const double level=take.db(.02,.5),f=take.pitch(440,.2,1.2);
      if(rate==48000)level48=level;
      std::cout<<rate<<" Hz: A4 "<<f<<" Hz, "<<level<<" dB, latency "<<engine->outputLatencySamples()<<" samples\n";
      check(std::abs(cents(f,440))<2,"A4 is in tune at every sample rate");
      check(std::abs(level-level48)<1.5,"the level is the same at every sample rate");
      check(take.safe(),"every sample rate plays safely");
    }
    for(const double rate:{0.,-1.,1e9,std::numeric_limits<double>::quiet_NaN()}){
      auto engine=std::make_unique<keyra::Engine>(rate);Take take;engine->noteOn(60,.8f);render(*engine,take,.1);
      check(take.safe()&&take.peak(0,.1)>0,"a nonsense sample rate is bounded to one that plays");
    }
  }
  {
    // What is not a key, a channel or a number is ignored or bounded.
    b.start(keyra::Parameters{});
    for(int n:{-5,0,11,15,20,109,127,4000}){e.noteOn(n,.8f);e.noteOff(n);}
    for(int ch:{0,17,-3,99}){e.noteOn(60,.8f,ch);e.controlChange(64,127,ch);e.pitchBend(3,ch);}
    b.run(.1);check(b.take.peak(0,.1)==0,"notes off the keyboard and channels that do not exist play nothing");
    const float nan=std::numeric_limits<float>::quiet_NaN(),inf=std::numeric_limits<float>::infinity();
    keyra::Parameters wild;
    float* fields[]{&wild.gain,&wild.hammer,&wild.age,&wild.detune,&wild.stretch,&wild.dynamics,&wild.lid,&wild.soundboard,&wild.sympathetic,
                    &wild.duplex,&wild.mic[0],&wild.mic[3],&wild.room,&wild.width,&wild.tuning,&wild.felt,&wild.mute,&wild.sustain,
                    &wild.sostenuto,&wild.soft,&wild.mechanics};
    for(const float value:{nan,inf,-inf,1e30f,-1e30f}){
      for(float* field:fields)*field=value;
      wild.body=static_cast<keyra::model::Body>(value>0?99:-7);
      b.start(wild);e.noteOn(60,nan);e.noteOn(48,inf);e.noteOn(64,2.f);e.pitchBend(nan);e.pitchBend(inf);e.controlChange(64,9999);e.controlChange(1,-4);
      b.run(.2);e.noteOff(48);b.run(.1);
      check(b.take.safe(),"controls that are not numbers are bounded");
    }
    std::array<float,4> left{{1,2,3,4}},right{{5,6,7,8}};
    e.process(left.data(),right.data(),0);e.process(left.data(),right.data(),-1);
    e.process(nullptr,right.data(),4);e.process(left.data(),nullptr,4);
    check(left[0]==1&&right[3]==8,"an invalid render span leaves its memory alone");
  }
  {
    // The loudest playing stays under full scale at any Output, and typical
    // playing is not squeezed by the output stage.
    for(const float gain:{.7f,2.f}){
      keyra::Parameters p;p.gain=gain;b.start(p);e.controlChange(64,127);
      for(int round=0;round<3;++round){for(int n:{24,31,36,43,48,55,60,64,67,72,76,84})e.noteOn(n,1);b.run(.5);for(int n:{24,31,36,43,48,55,60,64,67,72,76,84})e.noteOff(n);}
      std::cout<<"twelve keys at 127 under the pedal, Output "<<gain<<": peak "<<20*std::log10(b.take.peak(0,1.5))<<" dBFS\n";
      check(b.take.safe()&&b.take.peak(0,1.5)<=1,"the loudest playing stays under full scale");
    }
  }
  {
    // Pianos designed at the same moment on several threads, as a host
    // loading a session's instances does, are the piano designed alone.
    const auto chord=[](keyra::Engine& engine){
      engine.setSteadyStrikesForMeasurement(true);engine.setParameters(strings());engine.reset();
      Take take;for(int n:{36,60,64,91})engine.noteOn(n,.7f);render(engine,take,.5);return take.audio;
    };
    // The much-played engine of the checks above is that piano again after a
    // reset, its last pitch bend included.
    e.pitchBend(1.5f);b.run(.1);
    const auto alone=chord(e);
    constexpr int instances=4;
    std::vector<float> together[instances];
    std::vector<std::thread> threads;
    for(auto& audio:together)threads.emplace_back([&audio,&chord]{keyra::Engine engine(48000);audio=chord(engine);});
    for(auto& thread:threads)thread.join();
    bool same=true;for(const auto& audio:together)same=same&&audio==alone;
    check(same,"pianos designed together on several threads are the piano designed alone");
  }
  {
    // Nothing a host calls on the audio thread allocates.
    keyra::Parameters p;e.setParameters(p);e.reset();
    std::array<float,256> l{},r{};
    trap=true;
    e.noteOn(60,.8f);e.noteOn(14,1);e.process(l.data(),r.data(),256);
    p.body=keyra::model::Body::upright;p.hammer=.5f;p.mic[2]=1;p.tuning=443;p.soundboard=.9f;e.setParameters(p);
    e.controlChange(64,127);e.controlChange(66,127);e.controlChange(67,90);e.controlChange(1,30);e.pitchBend(1.5f);
    e.noteOn(36,1,4);e.process(l.data(),r.data(),256);e.noteOff(60);e.noteOff(14);e.process(l.data(),r.data(),100);
    (void)e.pedalState();(void)e.outputLatencySamples();
    e.controlChange(123,0);e.controlChange(121,0);e.controlChange(120,0);e.reset();e.process(l.data(),r.data(),64);
    trap=false;
    check(allocations==0,"events, controls, rendering and reset allocate nothing");
  }
  std::cout<<"engine_failures="<<failures<<" live_allocations="<<allocations<<'\n';
  return failures?1:0;
}
