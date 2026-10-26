#include "keyra/Piano.h"
#include "LiveCalibration.h"
#include "UprightCalibration.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <limits>

namespace keyra {
namespace {
constexpr double pi=3.14159265358979323846;
// One outgoing fade per primary voice permits replacing a complete 64-note
// chord at one event boundary without truncating its old waveform.
constexpr unsigned tailCount=64;
constexpr unsigned boardCount=12;
constexpr unsigned roomCapacity=32768;
constexpr unsigned micCapacity=8192;
// The Rack Extension toolchain uses -fno-builtin. Arithmetic magnitude avoids
// a libm call for every denormal check in the sample/mode loops.
template<class T> T magnitude(T value) noexcept {return value<0?-value:value;}
double mix(double a,double b,double t) noexcept {return a+(b-a)*t;}
double logmix(double a,double b,double t) noexcept {
  return std::exp(mix(std::log(std::max(a,1.e-12)),std::log(std::max(b,1.e-12)),t));
}
// Average exponential power over the benchmark's .05–.75 second early window.
double meanDecay(double rate) noexcept {
  const double e=std::exp(-.05*rate),e2=e*e,e4=e2*e2,e8=e4*e4;
  return (e-e8*e4*e2*e)/(.7*rate);
}
double branchEnergy(double fast,double late,double sf,double sl) noexcept {
  return .5*(fast*fast*meanDecay(2*sf)+late*late*meanDecay(2*sl)+2*fast*late*meanDecay(sf+sl));
}
bool matches(int note,int channel,int32_t id,int vn,int vc,int32_t vi) noexcept {
  return (note<0||note==vn)&&(channel<0||channel==vc)&&(id<0||id==vi);
}
float randomBipolar(uint32_t& state) noexcept {
  state^=state<<13;state^=state>>17;state^=state<<5;
  return static_cast<float>(static_cast<int32_t>(state))*(1.f/2147483648.f);
}
struct ModalState {
  float fastR=0,fastI=0,lateR=0,lateI=0;
  float fastC=0,fastS=0,lateC=0,lateS=0;
};
struct Voice {
  std::array<ModalState,64> modes{};
  int count=0,note=60,channel=0;
  int32_t id=-1;
  uint64_t serial=0,frames=0;
  bool active=false,down=false;
  float position=0,attack=0,attackStep=1;
  float damping=1,dampingTarget=1,damperEnvelope=1;
  float fade=1,fadeStep=0,last=0;
  float noiseEnvelope=0,noiseFilter=0,noiseDecay=.999f;
  uint32_t random=1;
};
struct BoardState {float r=0,i=0,c=0,s=0;};
struct NoteBasis {
  double f1=440,B=.0003,attackSoft=.01,attackHard=.01;
  std::array<double,64> ampSoft{},ampHard{},lateAmpSoft{},lateAmpHard{};
  std::array<double,64> decaySoft{},decayHard{},lateDecaySoft{},lateDecayHard{};
  std::array<double,64> energySoft{},energyHard{};
};
} // namespace

struct Piano::Impl {
  double sampleRate=48000;
  std::array<double,10> values{};
  std::array<float,10> smooth{};
  std::array<float,6> micWeight{};
  std::array<float,3> materialWeight{};
  std::array<float,16> pedal{};
  std::array<Voice,maxVoices> voices{};
  std::array<Voice,tailCount> tails{};
  std::array<std::array<NoteBasis,88>,2> basis{};
  std::array<std::array<BoardState,boardCount>,3> boards{};
  std::array<std::array<float,roomCapacity>,4> room{};
  std::array<unsigned,4> roomLength{},roomIndex{};
  std::array<float,4> roomLow{};
  std::array<float,micCapacity> micMain{},micSide{};
  unsigned micIndex=0;
  uint64_t serial=0;
  float smoothing=.001f,damperSmoothing=.001f;
  float lowL=0,lowR=0,shelfCoeff=.15f;
  float dcXL=0,dcXR=0,dcYL=0,dcYR=0,dcPole=.999f;
  float overflowTail=0,overflowSide=0,overflowDecay=.999f;
  float noiseReleaseDecay=.999f;

  Impl() {
    for(unsigned i=0;i<values.size();++i)values[i]=kParameters[i].defaultValue;
  }

  void buildBasis() {
    for(unsigned family=0;family<2;++family){
      const auto& anchors=family?upright_calibration::anchors:calibration::anchors;
      for(int note=21;note<=108;++note){
        auto& b=basis[family][note-21];
        int lo=std::clamp((note-36)/12,0,3),hi=lo+1;
        const auto& a=anchors[lo];const auto& z=anchors[hi];
        double t=(note-a.note)/static_cast<double>(z.note-a.note);
        double u=std::clamp(t,0.,1.);
        double centsA=1200*std::log2(a.f1/(440*std::pow(2.,(a.note-69)/12.)));
        double centsZ=1200*std::log2(z.f1/(440*std::pow(2.,(z.note-69)/12.)));
        double cents=std::clamp(mix(centsA,centsZ,t),-40.,40.);
        b.f1=440*std::pow(2.,(note-69+cents/100.)/12.);
        b.B=std::clamp(logmix(a.B,z.B,t),.00001,.04);
        // Below the measured C2 the wound bass scale is a bounded extrapolation.
        if(note<36)b.B=std::clamp(a.B*std::pow(2.,(36-note)/24.),.00001,.04);
        b.attackSoft=std::clamp(mix(a.attackSoft,z.attackSoft,u),.001,.09);
        b.attackHard=std::clamp(mix(a.attackHard,z.attackHard,u),.001,.09);
        for(unsigned j=0;j<64;++j){
          b.ampSoft[j]=logmix(a.amplitudeSoft[j],z.amplitudeSoft[j],u);
          b.ampHard[j]=logmix(a.amplitudeHard[j],z.amplitudeHard[j],u);
          b.lateAmpSoft[j]=logmix(a.amplitudeLateSoft[j],z.amplitudeLateSoft[j],u);
          b.lateAmpHard[j]=logmix(a.amplitudeLateHard[j],z.amplitudeLateHard[j],u);
          b.decaySoft[j]=logmix(a.decaySoft[j],z.decaySoft[j],u);
          b.decayHard[j]=logmix(a.decayHard[j],z.decayHard[j],u);
          b.lateDecaySoft[j]=logmix(a.decayLateSoft[j],z.decayLateSoft[j],u);
          b.lateDecayHard[j]=logmix(a.decayLateHard[j],z.decayLateHard[j],u);
          b.energySoft[j]=branchEnergy(b.ampSoft[j],b.lateAmpSoft[j],b.decaySoft[j],b.lateDecaySoft[j]);
          b.energyHard[j]=branchEnergy(b.ampHard[j],b.lateAmpHard[j],b.decayHard[j],b.lateDecayHard[j]);
        }
      }
    }
  }

  void buildEffects() noexcept {
    constexpr double frequencies[boardCount]={97,139,197,269,367,491,659,877,1171,1567,2089,2791};
    constexpr double scales[3]={1.,.935,1.075};
    constexpr double losses[3]={1.,1.32,.82};
    for(unsigned wood=0;wood<3;++wood)for(unsigned j=0;j<boardCount;++j){
      auto& b=boards[wood][j];double hz=frequencies[j]*scales[wood];
      double damping=std::exp(-(1.8+.002*hz)*losses[wood]/sampleRate);
      if(hz>=sampleRate*.43)damping=0;
      b.c=static_cast<float>(damping*std::cos(2*pi*hz/sampleRate));
      b.s=static_cast<float>(damping*std::sin(2*pi*hz/sampleRate));
    }
    constexpr double seconds[4]={.0297,.0371,.0411,.0437};
    for(unsigned j=0;j<4;++j)roomLength[j]=std::clamp(static_cast<unsigned>(seconds[j]*sampleRate),1u,roomCapacity-1);
    smoothing=static_cast<float>(1-std::exp(-1/(.020*sampleRate)));
    damperSmoothing=static_cast<float>(1-std::exp(-1/(.008*sampleRate)));
    shelfCoeff=static_cast<float>(1-std::exp(-2*pi*2200/sampleRate));
    dcPole=static_cast<float>(std::exp(-2*pi*7/sampleRate));
    noiseReleaseDecay=static_cast<float>(std::exp(-1/(.012*sampleRate)));
    overflowDecay=static_cast<float>(std::exp(-1/(.001*sampleRate)));
  }

  void reset() noexcept {
    for(auto& v:voices)v.active=false;
    for(auto& v:tails)v.active=false;
    pedal.fill(0);serial=0;
    for(unsigned i=0;i<values.size();++i)smooth[i]=static_cast<float>(values[i]);
    smooth[9]=static_cast<float>(std::pow(10.,values[9]/20.));
    micWeight.fill(0);micWeight[static_cast<unsigned>(values[2])]=1;
    materialWeight.fill(0);materialWeight[static_cast<unsigned>(values[1])]=1;
    for(auto& material:boards)for(auto& b:material)b.r=b.i=0;
    for(auto& line:room)line.fill(0);
    roomIndex.fill(0);roomLow.fill(0);
    micMain.fill(0);micSide.fill(0);micIndex=0;
    lowL=lowR=dcXL=dcXR=dcYL=dcYR=overflowTail=overflowSide=0;
  }

  void updateDamper(Voice& v) noexcept {
    if(v.down||v.note>=89){v.dampingTarget=1;return;}
    // Full lifting at .85 leaves room for controllable partial damping. Energy
    // already lost is not recreated when the player catches a note by repedal.
    double contact=std::clamp((.85-pedal[v.channel])/.85,0.,1.);
    double rate=(28.+.45*(v.note-21))*contact*contact;
    v.dampingTarget=static_cast<float>(std::exp(-rate/sampleRate));
  }

  void retireToTail(const Voice& old) noexcept {
    if(!old.active)return;
    auto* tail=&tails[0];
    for(auto& t:tails){
      if(!t.active){tail=&t;break;}
      if(magnitude(t.last)<magnitude(tail->last))tail=&t;
    }
    // Pathological bursts exceeding a whole chord within four milliseconds
    // retain the replaced fade's current value in a short continuity ramp.
    if(tail->active){overflowTail+=tail->last;overflowSide+=tail->last*tail->position;}
    *tail=old;
    tail->fade=1;
    tail->fadeStep=static_cast<float>(1/(.004*sampleRate));
    tail->down=false;
  }

  float tickVoice(Voice& v) noexcept {
    if(!v.active)return 0;
    float sample=0;
    for(int j=0;j<v.count;++j){
      auto& m=v.modes[j];
      sample+=m.fastR+m.lateR;
      const float fr=m.fastR,lr=m.lateR;
      m.fastR=m.fastC*fr+m.fastS*m.fastI;
      m.fastI=m.fastC*m.fastI-m.fastS*fr;
      m.lateR=m.lateC*lr+m.lateS*m.lateI;
      m.lateI=m.lateC*m.lateI-m.lateS*lr;
    }
    v.attack+=(1-v.attack)*v.attackStep;
    v.damping+=(v.dampingTarget-v.damping)*damperSmoothing;
    v.damperEnvelope*=v.damping;
    float noise=0;
    if(v.noiseEnvelope>1.e-8f){
      float white=randomBipolar(v.random);
      v.noiseFilter+=(white-v.noiseFilter)*.28f;
      noise=v.noiseFilter*v.noiseEnvelope;
      v.noiseEnvelope*=v.noiseDecay;
    }
    sample=(sample*v.attack*v.damperEnvelope+noise*smooth[6])*v.fade;
    v.last=sample;
    v.fade=std::max(0.f,v.fade-v.fadeStep);
    ++v.frames;
    if(v.fade<=0||v.damperEnvelope<1.e-7f||v.frames>static_cast<uint64_t>(sampleRate*45))v.active=false;
    else if((v.frames&1023u)==0){
      double e=0;int live=0;
      for(int j=0;j<v.count;++j){
        auto m=v.modes[j];
        // A fast component may become subnormal long before its companion
        // aftersound or the rest of the voice. Flush pairs independently, and
        // remove dead modes, without changing host floating-point flags.
        if(magnitude(m.fastR)+magnitude(m.fastI)<1.e-20f)m.fastR=m.fastI=0;
        if(magnitude(m.lateR)+magnitude(m.lateI)<1.e-20f)m.lateR=m.lateI=0;
        e+=m.fastR*m.fastR+m.fastI*m.fastI+m.lateR*m.lateR+m.lateI*m.lateI;
        if(m.fastR!=0||m.fastI!=0||m.lateR!=0||m.lateI!=0)v.modes[live++]=m;
      }
      v.count=live;
      if(e*v.damperEnvelope*v.damperEnvelope<1.e-13&&v.noiseEnvelope<1.e-7)v.active=false;
    }
    return sample;
  }

  float readMic(const std::array<float,micCapacity>& ring,double seconds) const noexcept {
    double delay=std::clamp(seconds*sampleRate,0.,static_cast<double>(micCapacity-2));
    unsigned whole=static_cast<unsigned>(delay);float fraction=static_cast<float>(delay-whole);
    auto a=(micIndex+micCapacity-whole)%micCapacity;
    auto b=(a+micCapacity-1)%micCapacity;
    return ring[a]+fraction*(ring[b]-ring[a]);
  }

  void tick(float& left,float& right) noexcept {
    for(unsigned i=3;i<9;++i)smooth[i]+=(static_cast<float>(values[i])-smooth[i])*smoothing;
    smooth[9]+=(gainTarget-smooth[9])*smoothing;
    unsigned mic=static_cast<unsigned>(values[2]),wood=static_cast<unsigned>(values[1]);
    for(unsigned j=0;j<6;++j)micWeight[j]+=((j==mic?1.f:0.f)-micWeight[j])*smoothing;
    for(unsigned j=0;j<3;++j)materialWeight[j]+=((j==wood?1.f:0.f)-materialWeight[j])*smoothing;
    float main=0,side=0;
    for(auto& v:voices)if(v.active){float s=tickVoice(v);main+=s;side+=s*v.position;}
    for(auto& v:tails)if(v.active){float s=tickVoice(v);main+=s;side+=s*v.position;}
    main+=overflowTail;side+=overflowSide;
    overflowTail*=overflowDecay;overflowSide*=overflowDecay;
    if(magnitude(overflowTail)<1.e-20f)overflowTail=0;
    if(magnitude(overflowSide)<1.e-20f)overflowSide=0;
    float boardMain=0,boardSide=0;
    for(unsigned w=0;w<3;++w){float a=0,b=0;
      for(unsigned j=0;j<boardCount;++j){
        auto& m=boards[w][j];float old=m.r;
        // Bounded feed-forward observation resonances. They never feed energy
        // back into the calibrated string oscillators.
        m.r=m.c*m.r+m.s*m.i;
        m.i=m.c*m.i-m.s*old+main*.00012f;
        a+=m.r;b+=(j&1?m.r:-m.r);
        if(magnitude(m.r)+magnitude(m.i)<1.e-20f)m.r=m.i=0;
      }
      boardMain+=a*materialWeight[w];boardSide+=b*materialWeight[w];
    }
    main+=boardMain*smooth[5]*.35f;
    side+=boardSide*smooth[5]*.25f;
    micMain[micIndex]=main;micSide[micIndex]=side;
    float l=0,r=0;
    // Authored observations of close spaced, coincident, near-coincident,
    // decoded mid/side, mono and distant spaced pickup. These are not measured
    // capsule emulations or recovered microphone transfer functions.
    float closeSide=side*.42f;
    l+=(main-closeSide)*micWeight[0];r+=(main+closeSide)*micWeight[0];
    l+=(main*.94f-side*.30f)*micWeight[1];r+=(main*.94f+side*.30f)*micWeight[1];
    l+=(main*.87f-readMic(micSide,.00025)*.55f)*micWeight[2];
    r+=(readMic(micMain,.00018)*.87f+side*.55f)*micWeight[2];
    float mid=main*.90f,figure=side-readMic(micSide,.00010)*.40f;
    l+=(mid-figure*.70f)*micWeight[3];r+=(mid+figure*.70f)*micWeight[3];
    l+=main*micWeight[4];r+=main*micWeight[4];
    l+=(readMic(micMain,.0027)*.68f-readMic(micSide,.0034)*.55f)*micWeight[5];
    r+=(readMic(micMain,.0038)*.68f+readMic(micSide,.0021)*.55f)*micWeight[5];
    micIndex=(micIndex+1)%micCapacity;
    float roomL=0,roomR=0;
    for(unsigned j=0;j<4;++j){
      float delayed=room[j][roomIndex[j]];
      roomLow[j]+=(delayed-roomLow[j])*.24f;
      if(magnitude(roomLow[j])<1.e-20f)roomLow[j]=0;
      room[j][roomIndex[j]]=main*.11f+roomLow[j]*.69f;
      roomIndex[j]=(roomIndex[j]+1)%roomLength[j];
      roomL+=delayed*(j&1?.65f:1.f);roomR+=delayed*(j&1?1.f:.65f);
    }
    float distance=smooth[7];
    float wet=distance*.45f+micWeight[5]*.22f;
    l=l*(1-distance*.42f)+roomL*wet;
    r=r*(1-distance*.42f)+roomR*wet;
    // A live shelf complements the attack-latched hammer spectral voicing.
    lowL+=(l-lowL)*shelfCoeff;lowR+=(r-lowR)*shelfCoeff;
    float shelf=smooth[3]*2;
    l=lowL+(l-lowL)*shelf;r=lowR+(r-lowR)*shelf;
    float center=(l+r)*.5f,difference=(r-l)*smooth[8];
    l=(center-difference)*smooth[9];r=(center+difference)*smooth[9];
    // DC rejection and a finite headroom ceiling protect hosts from pathological
    // stacked unison chords without clipping normal single-note calibration.
    float yl=l-dcXL+dcPole*dcYL,yr=r-dcXR+dcPole*dcYR;
    dcXL=l;dcXR=r;dcYL=yl;dcYR=yr;
    if(magnitude(lowL)<1.e-20f)lowL=0;
    if(magnitude(lowR)<1.e-20f)lowR=0;
    if(magnitude(dcYL)<1.e-20f)dcYL=0;
    if(magnitude(dcYR)<1.e-20f)dcYR=0;
    left=std::clamp(yl,-16.f,16.f);right=std::clamp(yr,-16.f,16.f);
  }
  float gainTarget=.501187f;
};

Piano::Piano():impl_(std::make_unique<Impl>()){(void)prepare(48000);}
Piano::~Piano()=default;
bool Piano::prepare(double rate) noexcept {
  if(!std::isfinite(rate)||rate<8000||rate>384000)return false;
  impl_->sampleRate=rate;impl_->buildBasis();impl_->buildEffects();reset();
  return true;
}
void Piano::reset() noexcept {impl_->reset();impl_->gainTarget=impl_->smooth[9];}
void Piano::setParameter(ParamId id,double value) noexcept {
  auto i=static_cast<unsigned>(id);
  if(i>=kParameters.size()||!std::isfinite(value))return;
  const auto& p=kParameters[i];value=std::clamp(value,p.min,p.max);
  if(p.stepped)value=std::round(value);
  impl_->values[i]=value;
  if(id==ParamId::Gain)impl_->gainTarget=static_cast<float>(std::pow(10.,value/20.));
}
double Piano::parameter(ParamId id) const noexcept {
  auto i=static_cast<unsigned>(id);return i<kParameters.size()?impl_->values[i]:0;
}
void Piano::noteOn(int note,double velocity,int channel,int32_t noteId) noexcept {
  if(note<21||note>108||channel<0||channel>=16||noteId< -1||!std::isfinite(velocity))return;
  if(velocity<=0){noteOff(note,channel,noteId);return;}
  auto& p=*impl_;Voice* voice=nullptr;
  for(auto& v:p.voices)if(!v.active){voice=&v;break;}
  if(!voice){
    voice=&p.voices[0];
    for(auto& v:p.voices){
      // Released voices are preferred; then compare attenuated current level,
      // using age to break ties deterministically.
      double score=(v.down?1000.:0.)+magnitude(v.last)*100+v.damperEnvelope;
      double best=(voice->down?1000.:0.)+magnitude(voice->last)*100+voice->damperEnvelope;
      if(score<best||(score==best&&v.serial<voice->serial))voice=&v;
    }
    p.retireToTail(*voice);
  }
  auto& v=*voice;v=Voice{};
  v.active=true;v.down=true;v.note=note;v.channel=channel;v.id=noteId;
  v.serial=++p.serial;v.random=0x9e3779b9u^static_cast<uint32_t>(v.serial*7919+note*101+channel*17);
  const int instrument=static_cast<int>(p.values[0]),material=static_cast<int>(p.values[1]);
  const auto& b=p.basis[instrument>=2?1:0][note-21];
  double dynamics=std::pow(2.,(p.values[4]-.5)*1.4);
  double speed=std::pow(std::clamp(velocity,.001,1.),dynamics);
  constexpr double softVelocity=40./127.,hardVelocity=93./127.;
  double u=std::clamp(std::log(speed/softVelocity)/std::log(hardVelocity/softVelocity),0.,1.);
  // Branch weights can trade places between measured velocities. Extrapolating
  // each component's log amplitude made near-zero components explode at soft
  // strikes. Extrapolate the complete note using one bounded scalar instead.
  double velocityGain=speed<softVelocity?std::pow(speed/softVelocity,1.5):
                      speed>hardVelocity?speed/hardVelocity:1.;
  double spectral=p.values[3]-.5;
  double attack=std::clamp(mix(b.attackSoft,b.attackHard,std::clamp(u,0.,1.)),.001,.09);
  double decayScale=1,dispersion=1,soften=0,detune=.23;
  if(instrument==1){decayScale=1.12+.1*std::max(0.,(52-note)/31.);dispersion=1.22;detune=.42;}
  if(instrument==2){detune=.65;}
  if(instrument==3){decayScale=1.20;dispersion=1.03;soften=.65;attack*=1.35;detune=.47;}
  if(material==1){decayScale*=1.14;dispersion*=.985;soften+=.10;}
  if(material==2){decayScale*=.94;dispersion*=1.025;soften-=.04;}
  double B=std::clamp(b.B*dispersion,.00001,.045);
  // Bounded authored geometry beyond each family's measured pitches/dynamics.
  if(note<36)decayScale*=std::pow(2.,(36-note)/72.);
  if(note>84)decayScale*=std::pow(2.,(note-84)/20.);
  v.attackStep=static_cast<float>(1-std::exp(-2.197224577/(attack*p.sampleRate)));
  v.position=static_cast<float>(std::clamp((note-64.5)/52.,-.85,.85));
  // The maximum is deliberately audible; the default 10% retains a restrained
  // action/hammer transient rather than adding a persistent noise floor.
  v.noiseEnvelope=static_cast<float>(.075*speed);
  v.noiseDecay=static_cast<float>(std::exp(-1/(.006*p.sampleRate)));
  double softEnergy=0,hardEnergy=0,currentEnergy=0;
  for(unsigned j=0;j<64;++j){
    double partial=j+1.;double hz=b.f1*partial*std::sqrt((1+B*partial*partial)/(1+B));
    if(hz>=p.sampleRate*.44||hz>19000)break;
    double shade=std::exp(std::clamp((spectral*.70-soften)*std::log1p(partial*.7),-5.,2.));
    if(material)shade*=std::exp(.12*std::sin(std::log(std::max(hz,20.))*2.7+material*1.7));
    double fast=mix(b.ampSoft[j],b.ampHard[j],u);
    double late=mix(b.lateAmpSoft[j],b.lateAmpHard[j],u);
    double sigma=std::clamp(logmix(b.decaySoft[j],b.decayHard[j],std::clamp(u,0.,1.))*decayScale,.03,100.);
    double lateSigma=std::clamp(logmix(b.lateDecaySoft[j],b.lateDecayHard[j],std::clamp(u,0.,1.))*decayScale,.03,40.);
    softEnergy+=b.energySoft[j];hardEnergy+=b.energyHard[j];
    currentEnergy+=branchEnergy(fast,late,sigma,lateSigma);
    double phase=2*pi*hz/p.sampleRate;
    // The second polarization/aftersound is a lightly detuned branch. Keep the
    // lowest wound single strings closer than multi-string choirs.
    double latePhase=phase*std::pow(2.,(note<32?.04:detune)/1200.);
    double damping=std::exp(-sigma/p.sampleRate),lateDamping=std::exp(-lateSigma/p.sampleRate);
    auto& m=v.modes[v.count++];
    m.fastI=static_cast<float>(fast*shade);m.lateI=static_cast<float>(late*shade);
    m.fastC=static_cast<float>(damping*std::cos(phase));m.fastS=static_cast<float>(damping*std::sin(phase));
    m.lateC=static_cast<float>(lateDamping*std::cos(latePhase));m.lateS=static_cast<float>(lateDamping*std::sin(latePhase));
  }
  // Preserve the measured note's overall dynamic trend while interpolating its
  // changing two-stage envelopes. This scalar is shared across every partial;
  // it does not normalize away spectral differences or velocity response.
  double desiredEnergy=logmix(std::max(softEnergy,1.e-20),std::max(hardEnergy,1.e-20),u);
  double normalization=std::sqrt(desiredEnergy/std::max(currentEnergy,1.e-20))*velocityGain;
  normalization=std::min(normalization,32.);
  for(int j=0;j<v.count;++j){v.modes[j].fastI*=static_cast<float>(normalization);v.modes[j].lateI*=static_cast<float>(normalization);}
}
void Piano::noteOff(int note,int channel,int32_t noteId) noexcept {
  if(note< -1||channel< -1||noteId< -1)return;
  auto& p=*impl_;
  for(auto& v:p.voices)if(v.active&&matches(note,channel,noteId,v.note,v.channel,v.id)){
    v.down=false;p.updateDamper(v);
    v.noiseEnvelope=std::max(v.noiseEnvelope,.006f);v.noiseDecay=p.noiseReleaseDecay;
  }
}
void Piano::noteChoke(int note,int channel,int32_t noteId) noexcept {
  if(note< -1||channel< -1||noteId< -1)return;
  for(auto& v:impl_->voices)if(v.active&&matches(note,channel,noteId,v.note,v.channel,v.id)){
    impl_->retireToTail(v);v.active=false;
  }
}
bool Piano::noteActive(int note,int channel,int32_t noteId) const noexcept {
  if(note< -1||channel< -1||noteId< -1)return false;
  for(const auto& v:impl_->voices)if(v.active&&matches(note,channel,noteId,v.note,v.channel,v.id))return true;
  return false;
}
void Piano::sustain(double position,int channel) noexcept {
  if(channel<0||channel>=16||!std::isfinite(position))return;
  auto& p=*impl_;p.pedal[channel]=static_cast<float>(std::clamp(position,0.,1.));
  for(auto& v:p.voices)if(v.active&&v.channel==channel)p.updateDamper(v);
}
void Piano::allNotesOff(int channel) noexcept {noteOff(-1,channel,-1);}
void Piano::allSoundOff(int channel) noexcept {
  auto& p=*impl_;
  if(channel== -1){p.reset();return;}
  if(channel< -1)return;
  if(channel>=16)return;
  for(auto& v:p.voices)if(v.channel==channel)v.active=false;
  for(auto& v:p.tails)if(v.channel==channel)v.active=false;
  p.pedal[channel]=0;
}
void Piano::process(float* left,float* right,uint32_t frames) noexcept {
  if(!left||!right)return;
  for(uint32_t i=0;i<frames;++i)impl_->tick(left[i],right[i]);
}
std::size_t Piano::activeVoices() const noexcept {
  std::size_t count=0;for(const auto& v:impl_->voices)if(v.active)++count;return count;
}
} // namespace keyra
