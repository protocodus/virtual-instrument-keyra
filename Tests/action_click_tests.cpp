// The click of the action above the body modes (Tools/fit_action_noise.py,
// MeasuredActionNoise.h; actionClick in KeyraEngine.cpp). A key let go and
// the grand's pedal coming up play, beside their knocks, a burst in each
// noise band their table sounds: on a recorded pitch exactly its row (each
// band's density against the others', its balance and its decay, building
// up under the action's rise), between two recorded pitches their rows mixed
// in dB as the knock's modes are, a band silent at one fading in power
// towards it. The Kawai, whose takes are let go from sounding notes, plays
// none; nor do the pedal going down, a key whose damper the pedal holds and
// Mechanics at 0. A release's click is invariant to the host's blocks.
#include <cmath>
#include <iostream>
#include <vector>
#include "DSP/KeyraEngine.cpp"

namespace keyra {
struct ActionClickTestObserver {
  static Engine::Impl& state(Engine& engine) noexcept {return *engine.impl;}
};
}

namespace {
int failures=0;
void check(bool condition,const char* message){if(!condition){std::cerr<<"FAIL: "<<message<<'\n';++failures;}}
std::vector<float> render(keyra::Engine& engine,int frames,int block=256){
  std::vector<float> out;std::vector<float> l(static_cast<std::size_t>(block)),r(static_cast<std::size_t>(block));
  for(int done=0;done<frames;done+=block){const int n=std::min(block,frames-done);
    engine.process(l.data(),r.data(),n);
    for(int i=0;i<n;++i){out.push_back(l[static_cast<std::size_t>(i)]);out.push_back(r[static_cast<std::size_t>(i)]);}}
  return out;
}
keyra::Parameters build(keyra::Piano piano){keyra::Parameters p;p.build=keyra::measuredBuild(piano);p.resonance=0;return p;}
const keyra::Model& model(keyra::Piano piano){return keyra::models[static_cast<int>(piano)];}
bool sounds(const keyra::measured::ActionNoise& n){return n.densityDb>-180;}
// The burst a click claimed: a strike's never rises.
template<class Impl> const keyra::Burst* click(const Impl& impl){
  for(const auto& burst:impl.bursts)if(burst.active)
    for(int k=0;k<keyra::noiseBands;++k)if(burst.riseLeft[k]!=0||burst.riseRight[k]!=0)return &burst;
  return nullptr;
}
// Whether `burst` plays the rows a and b of a click table mixed at t: per
// band its level against the first band both rows sound (so that the knock's
// gain, which every band shares, drops out), its right over its left, its
// decay, and its rise starting at its level and falling the faster by the
// action's rise; nothing where neither sounds.
template<class Impl> bool plays(const Impl& impl,const keyra::Burst& burst,const keyra::measured::ActionNoise* a,
                                const keyra::measured::ActionNoise* b,double t){
  const auto close=[](double x,double y){return std::abs(x-y)<=1e-9*std::max(std::abs(x),std::abs(y));};
  int reference=-1;double referenceLevel=0;bool ok=true;
  for(int k=0;k<keyra::noiseBands;++k){
    if(impl.noise[k].scale==0)continue;
    const bool hasA=sounds(a[k]),hasB=sounds(b[k]);
    if(!hasA&&!hasB){ok=ok&&burst.knockLeft[k]==0&&burst.knockRight[k]==0;continue;}
    // In double, as the engine mixes them: float differences round.
    const auto between=[&](double x,double y){return hasA&&hasB?x+(y-x)*t:hasA?x:y;};
    const double db=between(a[k].densityDb,b[k].densityDb),weight=hasA&&hasB?1:hasA?1-t:t;
    const double rate=std::exp(between(std::log(a[k].rate),std::log(b[k].rate)));
    const double tilt=between(a[k].balanceDb,b[k].balanceDb);
    // The band's mean level over its two channels, in the band's scale.
    const double level=std::sqrt(weight)*std::pow(10.,db/20)*impl.noise[k].scale;
    const double mean=std::sqrt(burst.knockLeft[k]*burst.knockRight[k]);
    if(reference<0&&hasA&&hasB){reference=k;referenceLevel=mean/level;}
    else if(reference>=0)ok=ok&&close(mean/level,referenceLevel);
    ok=ok&&close(burst.knockRight[k]/burst.knockLeft[k],std::pow(10.,tilt/20))
         &&burst.riseLeft[k]==burst.knockLeft[k]&&burst.riseRight[k]==burst.knockRight[k]
         &&close(burst.knockStep[k],std::exp(-rate*keyra::chunk/impl.sampleRate))
         &&close(burst.riseStep[k],std::exp(-(rate+1/impl.actionRise)*keyra::chunk/impl.sampleRate));
  }
  return ok&&reference>=0;
}
}

int main(){
  using keyra::Piano;
  {
    // On a recorded pitch a key let go plays its row exactly, the knock with it.
    const auto& grand=model(Piano::grand);
    const int note=grand.anchors[grand.anchorCount/2].note,upper=keyra::upperAnchor(grand,note);
    const auto* row=grand.releaseNoise+(grand.anchors[upper].note==note?upper:upper-1)*keyra::noiseBands;
    keyra::Engine engine(48000);engine.setParameters(build(Piano::grand));
    auto& impl=keyra::ActionClickTestObserver::state(engine);
    engine.noteOn(note,.7f);render(engine,12000);
    check(click(impl)==nullptr,"a strike plays no click");
    engine.noteOff(note);
    const keyra::Burst* burst=click(impl);
    check(burst&&plays(impl,*burst,row,row,0),"a recorded pitch let go plays its click's row");
    std::cout<<"grand_click_note="<<note<<'\n';
  }
  {
    // Between two recorded pitches the rows mix in dB, by where the key lies
    // between them; a band one of them leaves silent fades towards it in power.
    for(const Piano piano:{Piano::grand,Piano::hamburg}){
      const auto& m=model(piano);
      int upper=-1;
      for(int i=1;i<m.anchorCount&&upper<0;++i){
        if(m.anchors[i].note-m.anchors[i-1].note<2)continue;
        const auto* a=m.releaseNoise+(i-1)*keyra::noiseBands;const auto* b=a+keyra::noiseBands;
        bool partly=false;for(int k=0;k<keyra::noiseBands;++k)partly=partly||sounds(a[k])!=sounds(b[k]);
        if(piano==Piano::grand||partly)upper=i;
      }
      check(upper>0,"a piano has two recorded pitches to play a click between");
      if(upper<0)continue;
      const int lo=m.anchors[upper-1].note,hi=m.anchors[upper].note,note=lo+(hi-lo)/2;
      const double t=static_cast<double>(note-lo)/(hi-lo);
      const auto* a=m.releaseNoise+(upper-1)*keyra::noiseBands;
      keyra::Engine engine(48000);engine.setParameters(build(piano));
      auto& impl=keyra::ActionClickTestObserver::state(engine);
      engine.noteOn(note,.7f);render(engine,12000);engine.noteOff(note);
      const keyra::Burst* burst=click(impl);
      check(burst&&plays(impl,*burst,a,a+keyra::noiseBands,t),
            piano==Piano::grand?"a key between two recorded pitches mixes their clicks in dB"
                               :"a band one recorded pitch leaves silent fades towards it in power");
      std::cout<<"between_piano="<<static_cast<int>(piano)<<" note="<<note<<" t="<<t<<'\n';
    }
  }
  {
    // The Kawai's keys are let go from sounding notes: no click, the knock
    // alone, which the same release at Mechanics 0 lacks (the control
    // scales what the action sets ringing, not what already rings).
    keyra::Engine engine(48000),quiet(48000);engine.setParameters(build(Piano::kawai));quiet.setParameters(build(Piano::kawai));
    auto& impl=keyra::ActionClickTestObserver::state(engine);
    engine.noteOn(60,.7f);quiet.noteOn(60,.7f);render(engine,12000);render(quiet,12000);
    auto silent=build(Piano::kawai);silent.mechanics=0;quiet.setParameters(silent);
    engine.noteOff(60);quiet.noteOff(60);
    check(click(impl)==nullptr&&render(engine,4800)!=render(quiet,4800),"the Kawai's key let go knocks without a click");
  }
  {
    // The pedal clicks coming up, as its pedalU take, and not going down; a
    // key whose damper it holds clicks nothing; Mechanics at 0 clicks nothing.
    const auto& grand=model(Piano::grand);
    keyra::Engine engine(48000);engine.setParameters(build(Piano::grand));
    auto& impl=keyra::ActionClickTestObserver::state(engine);
    engine.controlChange(64,127);
    check(click(impl)==nullptr,"the pedal going down plays no click");
    render(engine,24000);
    engine.noteOn(60,.7f);render(engine,12000);engine.noteOff(60);
    check(click(impl)==nullptr,"a key let go under the pedal plays no click");
    render(engine,96000);
    engine.controlChange(64,0);
    const keyra::Burst* burst=click(impl);
    check(burst&&plays(impl,*burst,grand.pedalUpNoise,grand.pedalUpNoise,0),"the pedal coming up plays its click");
    auto silent=build(Piano::grand);silent.mechanics=0;
    keyra::Engine quiet(48000);quiet.setParameters(silent);
    auto& still=keyra::ActionClickTestObserver::state(quiet);
    quiet.noteOn(60,.7f);render(quiet,12000);quiet.noteOff(60);quiet.controlChange(64,127);render(quiet,4800);
    quiet.controlChange(64,0);
    check(click(still)==nullptr,"at Mechanics 0 nothing clicks");
  }
  {
    // The click starts and falls at chunk boundaries, so the host's blocks do
    // not change it: keys let go between and on recorded pitches, the pedal
    // coming up.
    keyra::Engine a(48000),b(48000);
    for(auto* engine:{&a,&b}){engine->setParameters(build(Piano::hamburg));engine->noteOn(52,.8f);engine->noteOn(73,.6f);}
    auto outA=render(a,9600,17),outB=render(b,9600,256);
    a.noteOff(52);b.noteOff(52);
    auto midA=render(a,4801,19),midB=render(b,4801,128);
    a.noteOff(73);b.noteOff(73);a.controlChange(64,127);b.controlChange(64,127);
    auto tailA=render(a,9600,23),tailB=render(b,9600,64);
    a.controlChange(64,0);b.controlChange(64,0);
    auto endA=render(a,24000,31),endB=render(b,24000,512);
    check(outA==outB&&midA==midB&&tailA==tailB&&endA==endB,"the click is invariant to audio block partitioning");
  }
  std::cout<<"action_click_failures="<<failures<<'\n';
  return failures?1:0;
}
