#include "KeyraEngine.h"
#include "MeasuredModalData.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <limits>

namespace keyra {
namespace {
constexpr double pi=3.14159265358979323846;
constexpr int maxVoices=128, maxModes=192, sineSize=4096;
float bounded(float x,float lo=0,float hi=1) noexcept {
  return x!=x?lo:x<lo?lo:x>hi?hi:x;
}
int channelIndex(int channel) noexcept {return channel>=1&&channel<=16?channel-1:-1;}
int switchIndex(int note) noexcept {return note>=12&&note<=14?note-12:-1;}
float pedalLevel(float panel,float midi,std::uint16_t heldSwitches) noexcept {
  return heldSwitches?1.f:std::max(panel,midi);
}
#if (defined(__clang__) || defined(__GNUC__)) && !defined(KEYRA_FORCE_SCALAR)
// Explicit 128-bit lanes also survive the freestanding Rack compiler, whose
// ordinary loops do not auto-vectorize. Each lane keeps its original operation
// order: prompt and late envelopes remain independent oscillators.
using Pair=double __attribute__((vector_size(16)));
#else
struct Pair {double v[2];double& operator[](int i){return v[i];}double operator[](int i)const{return v[i];}};
Pair operator+(Pair a,Pair b) noexcept {return {{a[0]+b[0],a[1]+b[1]}};}
Pair operator-(Pair a,Pair b) noexcept {return {{a[0]-b[0],a[1]-b[1]}};}
Pair operator*(Pair a,Pair b) noexcept {return {{a[0]*b[0],a[1]*b[1]}};}
Pair operator*(Pair a,double b) noexcept {return {{a[0]*b,a[1]*b}};}
#endif
double mix(double a,double b,double t) noexcept {return a+(b-a)*t;}
double logMix(double a,double b,double t) noexcept {
  return std::exp(mix(std::log(std::max(a,1e-12)),std::log(std::max(b,1e-12)),t));
}
struct Mode {
  Pair q{},p{},decay{};
  double c=1,s=0;
  float pan=0,tint=1,audibility=1,targetAudibility=1;
};
// Geometry and unmodified decay are read only at control/event rate. Keeping
// them off the oscillator stride reduces bandwidth without deleting modes.
struct ModeSetup {
  Pair naturalDecay{};
  double frequency=0,damperScale=0,tintScale=0;
};
struct Voice {
  std::array<Mode,maxModes> modes{};
  std::array<ModeSetup,maxModes> setup{};
  int count=0,note=60,channel=0;
  std::uint64_t serial=0;
  double attack=0,attackDecay=0,damper=0;
  double extraDecay=1;
  bool active=false;
};
struct Channel {
  std::array<std::uint16_t,88> presses{};
  std::array<bool,88> captured{};
  // Momentary C0/C#0/D0 switches have independent ownership from CC/panel.
  std::array<std::uint16_t,3> keySwitches{};
  float sustain=0,sostenuto=0,soft=0,mute=0,bend=0;
  double smoothedMute=0;
  bool sostDown=false;
};
struct Resonator {double q=0,p=0,c=1,s=0,decay=1;};
}

struct Engine::Impl {
  std::array<Voice,maxVoices> voices{};
  std::array<Channel,16> channels{};
  std::array<Resonator,88> sympathetic{};
  std::array<double,88> openness{};
  std::array<double,sineSize+1> sine{};
  Parameters parameters{};
  double sampleRate=48000,gain=.7,width=.75,mute=0;
  double smooth=0,controlSmooth=0,highpassCoefficient=0,highpassL=0,highpassR=0,previousL=0,previousR=0;
  float previousBrightness=.5f;
  std::uint64_t serial=0,frame=0;
  bool legacyAttack=false;
  bool sleeping=true;

  void rotation(double frequency,double& c,double& s) const noexcept {
    double phase=frequency/sampleRate;
    phase=std::max(0.,std::min(.45,phase));
    const double position=phase*sineSize;
    const int index=static_cast<int>(position);
    const double fraction=position-index;
    s=mix(sine[index],sine[index+1],fraction);
    const int ci=(index+sineSize/4)%sineSize;
    c=mix(sine[ci],sine[ci+1],fraction);
    // Linear wavetable interpolation slightly shrinks the unit circle. Exact
    // normalization here prevents artificial long-tail decay or energy growth.
    const double inverse=1/std::sqrt(c*c+s*s);
    c*=inverse;s*=inverse;
  }
  void capture(int ch) noexcept {
    auto& state=channels[ch];
    const bool down=pedalLevel(parameters.sostenuto,state.sostenuto,state.keySwitches[1])>=.5f;
    if(down&&!state.sostDown)
      for(int n=0;n<88;++n)state.captured[n]=state.presses[n]>0;
    if(!down)state.captured.fill(false);
    state.sostDown=down;
  }
  void retune(int ch) noexcept {
    const double ratio=parameters.tuning/440.*std::pow(2.,channels[ch].bend/12.);
    for(auto& voice:voices)if(voice.active&&voice.channel==ch)
      for(int j=0;j<voice.count;++j){auto& mode=voice.modes[j];
        const double frequency=voice.setup[j].frequency*ratio;
        mode.targetAudibility=frequency<sampleRate*.45?1.f:0.f;
        rotation(frequency,mode.c,mode.s);
      }
  }
  void control() noexcept {
    mute+=controlSmooth*(parameters.mute-mute);
    for(auto& channel:channels)
      channel.smoothedMute+=controlSmooth*(std::max(parameters.mute,channel.mute)-channel.smoothedMute);
    const bool tintChanged=previousBrightness!=parameters.brightness;
    previousBrightness=parameters.brightness;
    for(int note=0;note<88;++note){
      bool open=note>=68;double sustain=parameters.sustain;
      for(const auto& channel:channels){sustain=std::max(sustain,static_cast<double>(pedalLevel(parameters.sustain,channel.sustain,channel.keySwitches[2])));open=open||channel.presses[note]>0||channel.captured[note];}
      openness[note]=open?1:sustain*sustain;
    }
    for(auto& voice:voices)if(voice.active){
      const auto& channel=channels[voice.channel];
      const int key=voice.note-21;
      const bool open=channel.presses[key]>0||channel.captured[key];
      const double sustain=pedalLevel(parameters.sustain,channel.sustain,channel.keySwitches[2]);
      const double target=open?0:1-sustain;
      voice.damper+=controlSmooth*(target-voice.damper);
      // Continuous felt contact, including partial engagement and re-pedaling.
      // The undamped top twenty keys do not acquire a fictitious key damper.
      const double contact=voice.note>=89?0:std::pow(std::max(0.,(voice.damper-.08)/.92),2.5);
      voice.extraDecay=contact;
      for(int j=0;j<voice.count;++j){auto& mode=voice.modes[j];const auto& setup=voice.setup[j];
        if(tintChanged)mode.tint=static_cast<float>(std::pow(2.,(parameters.brightness-.5)*setup.tintScale));
        const double d=1/(1+contact*setup.damperScale+180*channel.smoothedMute*channel.smoothedMute/sampleRate*(.5+setup.frequency*.00015));
        mode.decay=setup.naturalDecay*d;
      }
    }
  }
  void strike(int note,float velocity,int ch) noexcept {
    sleeping=false;
    auto& channel=channels[ch];
    if(channel.presses[note-21]<std::numeric_limits<std::uint16_t>::max())++channel.presses[note-21];
    Voice* chosen=nullptr;
    for(auto& voice:voices)if(!voice.active){chosen=&voice;break;}
    if(!chosen){
      // Prefer released tails, then the oldest strike. Fixed storage bounds
      // CPU and memory under pathological repeated-note streams.
      for(auto& voice:voices)
        if(!chosen||((channels[voice.channel].presses[voice.note-21]==0)
                    &&channels[chosen->channel].presses[chosen->note-21]>0)
           ||((channels[voice.channel].presses[voice.note-21]>0)==
              (channels[chosen->channel].presses[chosen->note-21]>0)
              &&voice.serial<chosen->serial))chosen=&voice;
    }
    auto& voice=*chosen;voice.active=true;voice.note=note;voice.channel=ch;
    voice.count=0;voice.serial=++serial;voice.attack=0;voice.damper=0;
    const double soft=pedalLevel(parameters.soft,channel.soft,channel.keySwitches[0]);
    const double position=std::max(0.,std::min(4.,(note-36)/12.));
    const int lower=std::min(3,static_cast<int>(position)),upper=lower+1;
    const double pitchMix=position-lower;
    const double v=bounded(velocity);
    // MIDI velocity is a recording-layer coordinate, not measured hammer speed.
    const double velocityMix=std::max(0.,std::min(1.,(127*v-40)/53.));
    const auto& a=measured::anchors[2*lower];const auto& b=measured::anchors[2*upper];
    const auto& ah=measured::anchors[2*lower+1];const auto& bh=measured::anchors[2*upper+1];
    auto scalar=[&](float measured::Anchor::*member){return mix(mix(a.*member,ah.*member,velocityMix),mix(b.*member,bh.*member,velocityMix),pitchMix);};
    // Interpolate tuning offsets rather than absolute Hz between pitch anchors.
    const double ca=mix(1200*std::log2(a.f1/(440*std::pow(2.,(a.note-69)/12.))),1200*std::log2(ah.f1/(440*std::pow(2.,(ah.note-69)/12.))),velocityMix);
    const double cb=mix(1200*std::log2(b.f1/(440*std::pow(2.,(b.note-69)/12.))),1200*std::log2(bh.f1/(440*std::pow(2.,(bh.note-69)/12.))),velocityMix);
    const double f1=440*std::pow(2.,(note-69+mix(ca,cb,pitchMix)/100)/12.);
    double B=logMix(mix(a.B,ah.B,velocityMix),mix(b.B,bh.B,velocityMix),pitchMix);
    if(note<36)B*=std::pow(2.,(36-note)/18.);
    if(note>84)B*=std::pow(2.,(note-84)/8.);
    const double tau=legacyAttack?.002:scalar(&measured::Anchor::attackSeconds);
    voice.attackDecay=std::exp(-1/(sampleRate*tau));
    const double outsideVelocity=127*v<40?std::pow(std::max(.001,127*v/40),1.4):127*v>93?std::pow(127*v/93,1.1):1;
    const double softGain=1-.28*soft;
    const int unisons=note<=31?1:note<=43?2:3;
    const double normalization=1/std::sqrt(static_cast<double>(unisons));
    const double tuning=parameters.tuning/440.*std::pow(2.,channel.bend/12.);
    for(int order=1;order<=measured::partials;++order){
      const double frequency=order*f1*std::sqrt((1+B*order*order)/(1+B));
      if(frequency>std::min(17000.,sampleRate*.43))break;
      const auto& ma=a.modes[order-1];const auto& mb=b.modes[order-1];
      const auto& mha=ah.modes[order-1];const auto& mhb=bh.modes[order-1];
      auto field=[&](float measured::Partial::*member){return logMix(logMix(ma.*member,mha.*member,velocityMix),logMix(mb.*member,mhb.*member,velocityMix),pitchMix);};
      const double pAmp=field(&measured::Partial::promptAmplitude)*outsideVelocity*softGain;
      const double lAmp=field(&measured::Partial::lateAmplitude)*outsideVelocity*softGain;
      if(pAmp+lAmp<1e-9)continue;
      const double ps=field(&measured::Partial::promptSigma);
      const double ls=field(&measured::Partial::lateSigma);
      // Una corda reduces high-frequency excitation progressively and changes
      // the choir balance. Existing tails retain their original strike timbre.
      const double felt=std::exp(-soft*.115*(order-1));
      for(int u=0;u<unisons;++u){
        auto& setup=voice.setup[voice.count];auto& mode=voice.modes[voice.count++];
        double detune=unisons==1?0:unisons==2?(u==0?-.38:.43):(u==0?-.60:u==1?.12:.73);
        detune*=.7+.45*(note-21)/87.;
        setup.frequency=frequency*std::pow(2.,detune/1200.);
        rotation(setup.frequency*tuning,mode.c,mode.s);
        mode.targetAudibility=mode.audibility=setup.frequency*tuning<sampleRate*.45?1.f:0.f;
        const double phase=.41*order+.79*u;
        // Deterministic authored phase, never extracted recording phase.
        const double choir=(u==0?1-.28*soft:1+.08*soft)*normalization*felt;
        mode.q[0]=std::sin(phase)*pAmp*choir;mode.p[0]=std::cos(phase)*pAmp*choir;
        mode.q[1]=std::sin(phase)*lAmp*choir;mode.p[1]=std::cos(phase)*lAmp*choir;
        setup.naturalDecay[0]=std::exp(-ps/sampleRate);setup.naturalDecay[1]=std::exp(-ls/sampleRate);
        setup.damperScale=(24+1.4*std::sqrt(frequency)+.001*frequency)/sampleRate;
        setup.tintScale=std::min(4.,std::log2(static_cast<double>(order)));
        mode.tint=static_cast<float>(std::pow(2.,(parameters.brightness-.5)*setup.tintScale));
        mode.pan=static_cast<float>((note-64.5)/70.+(u-(unisons-1)*.5)*.12);
        const double d=1/(1+180*channel.smoothedMute*channel.smoothedMute/sampleRate*(.5+setup.frequency*.00015));
        mode.decay=setup.naturalDecay*d;
      }
    }
  }
};

Engine::Engine(double sampleRate):impl(new Impl){prepare(sampleRate);}
Engine::~Engine()=default;
void Engine::prepare(double sampleRate){
  auto& p=*impl;p.sampleRate=sampleRate==sampleRate?std::max(8000.,std::min(192000.,sampleRate)):48000.;
  for(int i=0;i<=sineSize;++i)p.sine[i]=std::sin(2*pi*i/sineSize);
  p.smooth=1-std::exp(-1/(.012*p.sampleRate));p.controlSmooth=1-std::exp(-32/(.018*p.sampleRate));
  p.highpassCoefficient=std::exp(-2*pi*10/p.sampleRate);
  for(int i=0;i<88;++i){auto& r=p.sympathetic[i];const double f=440*std::pow(2.,(i+21-69)/12.);
    p.rotation(f,r.c,r.s);r.decay=std::exp(-(.7+.001*f)/p.sampleRate);}
  reset();
}
void Engine::reset() noexcept {
  auto& p=*impl;for(auto& voice:p.voices){voice.active=false;voice.count=0;}
  for(auto& channel:p.channels)channel=Channel{};
  for(auto& resonator:p.sympathetic){resonator.q=0;resonator.p=0;}
  p.serial=0;p.frame=0;p.gain=p.parameters.gain;p.width=p.parameters.width;p.mute=p.parameters.mute;
  p.previousBrightness=p.parameters.brightness;
  p.sleeping=true;
  p.highpassL=p.highpassR=p.previousL=p.previousR=0;
  for(int ch=0;ch<16;++ch)p.capture(ch);
}
void Engine::setParameters(const Parameters& input) noexcept {
  auto& p=*impl;const float oldTune=p.parameters.tuning;
  p.parameters.gain=bounded(input.gain,0,2);p.parameters.brightness=bounded(input.brightness);
  p.parameters.resonance=bounded(input.resonance);p.parameters.width=bounded(input.width);
  // Wrappers combine their 400..480 Hz user range with host master tuning.
  p.parameters.tuning=bounded(input.tuning,300,600);p.parameters.mute=bounded(input.mute);
  p.parameters.sustain=bounded(input.sustain);p.parameters.sostenuto=bounded(input.sostenuto);
  p.parameters.soft=bounded(input.soft);
  for(int ch=0;ch<16;++ch){p.capture(ch);if(oldTune!=p.parameters.tuning)p.retune(ch);}
}
void Engine::noteOn(int note,float velocity,int channel) noexcept {
  const int ch=channelIndex(channel);if(ch<0)return;
  if(!(velocity>0)){noteOff(note,channel);return;}
  const int sw=switchIndex(note);
  if(sw>=0){
    auto& count=impl->channels[ch].keySwitches[sw];
    if(count<std::numeric_limits<std::uint16_t>::max())++count;
    if(sw==1)impl->capture(ch);
    return;
  }
  if(note<21||note>108)return;
  impl->strike(note,bounded(velocity),ch);
}
void Engine::noteOff(int note,int channel) noexcept {
  const int ch=channelIndex(channel);if(ch<0)return;
  const int sw=switchIndex(note);
  if(sw>=0){
    auto& count=impl->channels[ch].keySwitches[sw];if(count>0)--count;
    if(sw==1)impl->capture(ch);
    return;
  }
  if(note<21||note>108)return;
  auto& count=impl->channels[ch].presses[note-21];if(count>0)--count;
}
void Engine::controlChange(int cc,int value,int channel) noexcept {
  const int ch=channelIndex(channel);if(ch<0)return;
  auto& p=*impl;auto& state=p.channels[ch];const float amount=bounded(value/127.f);
  if(cc==1)state.mute=amount;
  else if(cc==64)state.sustain=amount;
  else if(cc==66){state.sostenuto=amount;p.capture(ch);}
  else if(cc==67)state.soft=amount;
  else if(cc==123){state.presses.fill(0);state.keySwitches.fill(0);p.capture(ch);}
  else if(cc==120){
    state.presses.fill(0);state.keySwitches.fill(0);state.captured.fill(false);p.capture(ch);
    for(auto& voice:p.voices)if(voice.channel==ch)voice.active=false;
    bool any=false;for(const auto& voice:p.voices)any=any||voice.active;
    if(!any){for(auto& r:p.sympathetic){r.q=0;r.p=0;}p.highpassL=p.highpassR=p.previousL=p.previousR=0;}
  }else if(cc==121){
    state.sustain=state.sostenuto=state.soft=state.mute=state.bend=0;
    // Resetting MIDI CC sources is not a new edge on a held panel/switch.
    p.capture(ch);
    p.retune(ch);
  }
}
void Engine::pitchBend(float semitones,int channel) noexcept {
  const int ch=channelIndex(channel);if(ch<0)return;
  impl->channels[ch].bend=bounded(semitones,-48,48);impl->retune(ch);
}
PedalState Engine::pedalState(int channel) const noexcept {
  PedalState state;
  if(channel<0||channel>16)return state;
  const int first=channel==0?0:channel-1,last=channel==0?16:channel;
  const auto& p=*impl;
  for(int ch=first;ch<last;++ch){const auto& c=p.channels[ch];
    state.sustain=std::max(state.sustain,pedalLevel(p.parameters.sustain,c.sustain,c.keySwitches[2]));
    state.sostenuto=std::max(state.sostenuto,pedalLevel(p.parameters.sostenuto,c.sostenuto,c.keySwitches[1]));
    state.soft=std::max(state.soft,pedalLevel(p.parameters.soft,c.soft,c.keySwitches[0]));
  }
  return state;
}
void Engine::setLegacyAttackForComparison(bool enabled) noexcept {impl->legacyAttack=enabled;}
void Engine::process(float* left,float* right,int frames) noexcept {
  if(!left||!right||frames<=0)return;
  auto& p=*impl;
  if(p.sleeping){
    std::fill_n(left,frames,0.f);std::fill_n(right,frames,0.f);
    p.gain=p.parameters.gain;p.width=p.parameters.width;
    p.mute=p.parameters.mute;
    for(auto& channel:p.channels)channel.smoothedMute=std::max(p.parameters.mute,channel.mute);
    return;
  }
  for(int sample=0;sample<frames;++sample,++p.frame){
    if((p.frame&31u)==0)p.control();
    p.gain+=p.smooth*(p.parameters.gain-p.gain);p.width+=p.smooth*(p.parameters.width-p.width);
    double l=0,r=0;
    for(auto& voice:p.voices)if(voice.active){
      voice.attack=1-(1-voice.attack)*voice.attackDecay;
      double vl=0,vr=0,energy=0;
      const bool measureEnergy=(p.frame&63u)==0;
      for(int j=0;j<voice.count;++j){auto& mode=voice.modes[j];
        // Backward Euler is strictly dissipative for every controller setting.
        const Pair q=mode.q,im=mode.p,decay=mode.decay;
        mode.q=(q*mode.c+im*mode.s)*decay;
        mode.p=(im*mode.c-q*mode.s)*decay;
        if(mode.audibility!=mode.targetAudibility)
          mode.audibility+=static_cast<float>(p.smooth)*(mode.targetAudibility-mode.audibility);
        const double out=(mode.q[0]+mode.q[1])*mode.tint*mode.audibility;
        const double pan=mode.pan*p.width;
        vl+=out*(1-pan);vr+=out*(1+pan);
        if(measureEnergy)energy+=mode.q[0]*mode.q[0]+mode.p[0]*mode.p[0]+mode.q[1]*mode.q[1]+mode.p[1]*mode.p[1];
      }
      l+=vl*voice.attack;r+=vr*voice.attack;
      if(measureEnergy&&energy<1e-17&&voice.attack>.9)voice.active=false;
    }
    // Feed-forward bridge-to-open-string radiation. The reduced core does not
    // claim the reference solver's reciprocal 475-mode soundboard network.
    // No feedback reaches the driven voices, so this response cannot run away.
    const double drive=(l+r)*.5;
    double responseL=0,responseR=0;
    for(int note=0;note<88;++note){
      const double openness=p.openness[note];
      auto& mode=p.sympathetic[note];
      const double d=mode.decay/(1+(1-openness)*60/p.sampleRate+180*p.mute*p.mute/p.sampleRate);
      const double q=mode.q,im=mode.p;
      mode.q=d*(mode.c*q+mode.s*im);mode.p=d*(mode.c*im-mode.s*q)+(1-mode.decay)*drive*openness;
      if(mode.q<1e-30&&mode.q>-1e-30)mode.q=0;
      if(mode.p<1e-30&&mode.p>-1e-30)mode.p=0;
      const double pan=(note-43.5)/80.*p.width;
      responseL+=mode.q*(1-pan);responseR+=mode.q*(1+pan);
    }
    l+=responseL*p.parameters.resonance*.35;r+=responseR*p.parameters.resonance*.35;
    // DC blocker and bounded, memoryless emergency ceiling. Typical single
    // notes remain linear; extreme 128-strike stacks cannot emit NaN/Inf.
    const double hpL=l-p.previousL+p.highpassCoefficient*p.highpassL,hpR=r-p.previousR+p.highpassCoefficient*p.highpassR;
    p.previousL=l;p.previousR=r;p.highpassL=hpL;p.highpassR=hpR;
    const double outL=hpL*p.gain*.18,outR=hpR*p.gain*.18;
    left[sample]=static_cast<float>(outL>1?1:outL< -1?-1:outL);
    right[sample]=static_cast<float>(outR>1?1:outR< -1?-1:outR);
  }
  bool any=false;
  for(const auto& voice:p.voices)any=any||voice.active;
  if(!any){
    double residue=std::abs(p.highpassL)+std::abs(p.highpassR);
    for(const auto& r:p.sympathetic)residue+=std::abs(r.q)+std::abs(r.p);
    if(residue<1e-14){
      p.sleeping=true;p.highpassL=p.highpassR=p.previousL=p.previousR=0;
      for(auto& r:p.sympathetic){r.q=0;r.p=0;}
    }
  }
}
}
