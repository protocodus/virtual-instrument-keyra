#include "KeyraEngine.h"
#include "MeasuredModalData.h"
#include "MeasuredUprightData.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <limits>

namespace keyra {
namespace {
constexpr double pi=3.14159265358979323846;
// Controls, damping and retuning take effect every `chunk` samples; each
// partial's exact double-precision state is carried from chunk to chunk and
// the float lanes only ever run one chunk from it.
constexpr int maxVoices=128, maxPartials=128, chunk=32, sineSize=4096;
constexpr int lanes=4; // a partial's measured lanes, one per vector lane
namespace grand=measured::grand;
namespace upright=measured::upright;
// F6, the lowest key without a damper, and the undamped strings from it up.
constexpr int firstHalo=89,halo=static_cast<int>(grand::haloStrings.size());
static_assert(firstHalo+halo-1==108,"the undamped strings run to the top key");
static_assert(upright::haloStrings.size()==grand::haloStrings.size(),"both pianos leave the same keys undamped");
float bounded(float x,float lo=0,float hi=1) noexcept {
  return x!=x?lo:x<lo?lo:x>hi?hi:x;
}
int channelIndex(int channel) noexcept {return channel>=1&&channel<=16?channel-1:-1;}
int switchIndex(int note) noexcept {return note>=12&&note<=14?note-12:-1;}
float pedalLevel(float panel,float midi,std::uint16_t heldSwitches) noexcept {
  return heldSwitches?1.f:std::max(panel,midi);
}
// The gain at velocity v (0..1) under an SFZ amp_veltrack of `tracking`, as
// sfizz's Region::velocityCurve computes it.
double trackingGain(double tracking,double v) noexcept {return 1-tracking+tracking*v*v;}
// A piano: its fitted data (MeasuredTypes.h), where its lanes start in the
// engine's caches, how its library mixes the action's noises against the
// notes, and the scale of its levels. Tables over the recorded pitches hold
// a row per pitch; one without pedal recordings has no pedal knocks.
struct Model {
  int layers;const float* layerVelocity;
  const measured::Anchor* anchors;int anchorCount;
  const measured::Partial* partials;const measured::Extra* extras;int partialFirst,extraFirst;
  const measured::HaloString* haloStrings;const float* haloLevels;float haloSlopeDb;
  const measured::BodyMode* bodyModes;int bodyModeCount;float bodyRise;const measured::Knock* knocks;
  const measured::ActionKnock *releaseKnocks,*pedalDown,*pedalUp;float actionRise;
  double releaseDb,releaseTracking,noteTracking,releaseFadeDbPerSecond,pedalDownDb,pedalUpDb;
  const measured::NoiseBand* noiseBands;const measured::Noise* noise;
  double outputScale;
};
constexpr Model models[]{
  {grand::layers,grand::layerVelocity.data(),grand::anchors.data(),static_cast<int>(grand::anchors.size()),
   grand::partials.data(),grand::extras.data(),0,0,
   grand::haloStrings.data(),grand::haloLevels.data(),grand::haloSlopeDb,
   grand::bodyModes.data(),static_cast<int>(grand::bodyModes.size()),grand::bodyRise,grand::knocks.data(),
   grand::releaseKnocks.data(),grand::pedalDown.data(),grand::pedalUp.data(),grand::actionRise,
   // The action's noises against the notes, as the library's own SFZ mixes
   // them (Salamander Grand Piano V3, kinwie's SFZ v2 mapping, Data/hammer.txt
   // and Data/pedal.txt): a key let go at -37 dB with 82 % velocity tracking,
   // 2 dB quieter for each second since its strike (rt_decay); the sustain
   // pedal at -20 dB going down and -19 dB coming up. The notes track velocity
   // at 73 % there (CC99's default) but play at the recordings' own levels
   // here, so a release takes the ratio of the two trackings. The noise files
   // were gained up as a set, so this balance is the library's mixing choice,
   // not a measurement (Docs/research/release-recordings-2026-10-27.md).
   -37,.82,.73,2,-20,-19,
   grand::noiseBands.data(),grand::noise.data(),
   // The measured levels are the recordings' own. This scale keeps the
   // median note as loud as version 0.3.0's (Tools/benchmark_recordings.py,
   // median gain 17.6 dB to the recordings).
   .21},
  {upright::layers,upright::layerVelocity.data(),upright::anchors.data(),static_cast<int>(upright::anchors.size()),
   upright::partials.data(),upright::extras.data(),
   static_cast<int>(grand::partials.size()),static_cast<int>(grand::extras.size()),
   upright::haloStrings.data(),upright::haloLevels.data(),upright::haloSlopeDb,
   upright::bodyModes.data(),static_cast<int>(upright::bodyModes.size()),upright::bodyRise,upright::knocks.data(),
   upright::releaseKnocks.data(),nullptr,nullptr,upright::actionRise,
   // The library's Stereo Ribbon preset plays every recording at its own
   // level (ampVelTrack 0) and a key let go as the hammer noise recorded
   // with that key, at its group's volume of 0.2 (-14 dB) whatever the
   // velocity and however long the key was held. It has no pedal recordings.
   -13.9794,0,0,0,0,0,
   upright::noiseBands.data(),upright::noise.data(),
   // The recordings' levels are their own. This scale makes the median note
   // at velocity 127 as loud as the grand's (each key A0-C8 held, both
   // channels' RMS from 50 to 750 ms after the strike, as the benchmark sets
   // a case's gain), so both pianos' fortissimo leaves the output the same
   // headroom. Below it the upright keeps the wider span its recordings
   // have: at velocity 85 its median note is 6 dB under the grand's.
   .502},
};
constexpr int partialCaches=static_cast<int>(grand::partials.size()+upright::partials.size()),
              extraCaches=static_cast<int>(grand::extras.size()+upright::extras.size());
// The SFZ sounds the pedal at CC64 127 and 0. Here it sounds within .08 of
// either end of its travel, the margin within which the dampers already
// clear the strings (the contact in boundary()), so that a pedal which
// never quite reaches an end still sounds and half-pedalling between does not.
constexpr float pedalClear=.92f,pedalRest=.08f;
#if (defined(__clang__) || defined(__GNUC__)) && !defined(KEYRA_FORCE_SCALAR)
// Explicit 128-bit lanes also survive the freestanding Rack compiler, whose
// ordinary loops do not auto-vectorize. One vector holds a partial's lanes.
using V4=float __attribute__((vector_size(16)));
float lane(const V4& v,int i) noexcept {return v[i];}
void setLane(V4& v,int i,float x) noexcept {v[i]=x;}
V4 splat(float x) noexcept {return V4{x,x,x,x};}
#else
struct V4 {float v[4];};
V4 operator+(V4 a,V4 b) noexcept {return {{a.v[0]+b.v[0],a.v[1]+b.v[1],a.v[2]+b.v[2],a.v[3]+b.v[3]}};}
V4 operator-(V4 a,V4 b) noexcept {return {{a.v[0]-b.v[0],a.v[1]-b.v[1],a.v[2]-b.v[2],a.v[3]-b.v[3]}};}
V4 operator*(V4 a,V4 b) noexcept {return {{a.v[0]*b.v[0],a.v[1]*b.v[1],a.v[2]*b.v[2],a.v[3]*b.v[3]}};}
V4& operator+=(V4& a,V4 b) noexcept {a=a+b;return a;}
float lane(const V4& v,int i) noexcept {return v.v[i];}
void setLane(V4& v,int i,float x) noexcept {v.v[i]=x;}
V4 splat(float x) noexcept {return {{x,x,x,x}};}
#endif
double mix(double a,double b,double t) noexcept {return a+(b-a)*t;}
struct Complex {double re=0,im=0;};
Complex operator*(Complex a,Complex b) noexcept {return {a.re*b.re-a.im*b.im,a.re*b.im+a.im*b.re};}
Complex power(Complex base,int exponent) noexcept {
  Complex result{1,0};
  while(exponent>0){if(exponent&1)result=result*base;base=base*base;exponent>>=1;}
  return result;
}
// One partial: four complex lanes, each a damped rotation at its own rate and
// frequency, under one rise 1 - d, d = e^(-t/rise), that starts them from
// zero. Each microphone hears the real part of a complex weighted sum.
struct alignas(16) Partial {
  V4 re{},im{},c{},s{};
  V4 leftRe{},leftIm{},rightRe{},rightIm{};
  Complex exact[lanes]{};          // state at the next chunk boundary
  Complex natural[lanes]{};        // undamped per-sample rotation
  Complex step[lanes]{},leap[lanes]{}; // damped rotation per sample and per chunk
  double decay[lanes]{},hz[lanes]{};
  float baseLeftRe[lanes]{},baseLeftIm[lanes]{},baseRightRe[lanes]{},baseRightIm[lanes]{};
  double energyWeight[lanes]{};
  double frequency=0,damperScale=0,tintScale=0;
  double riseExact=0,riseStep=0,riseLeap=0; // d at the next chunk boundary, per sample and per chunk
  float riseRemaining=0,riseDecay=0;        // d's float copy, run one chunk from riseExact
  float tint=1,audibility=1,targetAudibility=1;
  bool rising=false;
};
// Four of the body's modes, which every strike knocks: damped rotations at
// fixed frequencies, each heard through its own pickup. As with a partial's
// lanes, the float state runs one chunk from the exact state.
struct alignas(16) BodyBank {
  V4 re{},im{},c{},s{},left{},rightRe{},rightIm{};
  Complex exact[lanes]{},step[lanes]{},leap[lanes]{};
};
constexpr int bodyModes=static_cast<int>(std::max(grand::bodyModes.size(),upright::bodyModes.size())),
              bodyBanks=(bodyModes+lanes-1)/lanes;
using Body=std::array<BodyBank,bodyBanks>;
void knock(BodyBank& bank,int j,Complex g,int ahead) noexcept {
  setLane(bank.re,j,lane(bank.re,j)+static_cast<float>(g.re));
  setLane(bank.im,j,lane(bank.im,j)+static_cast<float>(g.im));
  const Complex z=g*power(bank.step[j],ahead);
  bank.exact[j]={bank.exact[j].re+z.re,bank.exact[j].im+z.im};
}
// At a chunk boundary: the float lanes restart from the exact state, which
// advances one chunk. Below -150 dB the bank falls silent.
bool advance(Body& body) noexcept {
  double energy=0;
  for(auto& bank:body)for(int j=0;j<lanes;++j){const Complex z=bank.exact[j];
    setLane(bank.re,j,static_cast<float>(z.re));setLane(bank.im,j,static_cast<float>(z.im));
    energy+=z.re*z.re+z.im*z.im;bank.exact[j]=z*bank.leap[j];}
  if(energy>=1e-15)return true;
  for(auto& bank:body){bank.re=bank.im=V4{};for(auto& z:bank.exact)z={};}
  return false;
}
// Above the body modes the board's ring is noise in third-octave bands. A
// strike's burst holds, per band, its left and right amplitude at the next
// chunk boundary and its decay per chunk.
constexpr int noiseBands=static_cast<int>(grand::noiseBands.size()),maxBursts=32;
static_assert(upright::noiseBands.size()==grand::noiseBands.size(),"both pianos' noise has the same bands");
struct Burst {
  double left[noiseBands]{},right[noiseBands]{},step[noiseBands]{};
  std::uint64_t serial=0;
  bool active=false;
};
// One band: a band-pass of `noiseSections` sections (b1 = 0, b2 = -b0) on
// each of two independent noise sources, mixed for the measured left/right
// coherence, under gains that ramp across each chunk to the bursts' sum at
// its end.
constexpr int noiseSections=3;
struct NoiseBand {
  double b0[noiseSections]{},a1[noiseSections]{},a2[noiseSections]{},scale=0,c=1,s=0;
  double x1[noiseSections][2]{},x2[noiseSections][2]{},y1[noiseSections][2]{},y2[noiseSections][2]{};
  double left=0,right=0,leftStep=0,rightStep=0,leftEnd=0,rightEnd=0;
};
struct Voice {
  std::array<Partial,maxPartials> partials{};
  int count=0,note=60,channel=0;
  std::uint64_t serial=0;
  double damper=0,contact=0,appliedContact=-1,appliedMute=-1;
  bool active=false,retune=false;
};
struct Channel {
  std::array<std::uint16_t,88> presses{};
  std::array<bool,88> captured{};
  // Each key's latest strike, which sets the noise of its release.
  std::array<float,88> velocity{};
  std::array<std::uint64_t,88> struck{};
  // Momentary C0/C#0/D0 switches have independent ownership from CC/panel.
  std::array<std::uint16_t,3> keySwitches{};
  float sustain=0,sostenuto=0,soft=0,mute=0,bend=0;
  double smoothedMute=0;
  bool sostDown=false;
};
struct Resonator {double q=0,p=0,c=1,s=0,decay=1;};
// A strike's data, interpolated between the two recorded pitches around it.
// `ratio` and `angle` are its pickup's right-over-left level (natural log)
// and phase difference.
struct LaneData {double rate=0,offset=0,level=0,ratio=0,angle=0;Complex phase{1,0},left{},right{};};
struct PartialData {int order=0;double cents=0,rise=0;LaneData lane[lanes]{};};
// What every strike would otherwise recompute of a measured lane: its log
// rate, its pickup's ratio and angle (see LaneData) and its layers' phases
// as unit vectors.
struct LaneCache {double logRate=0,ratio=0,angle=0;std::array<Complex,measured::maxLayers> phase{};};
LaneCache cacheLane(const measured::Lane& m,int layers) noexcept {
  LaneCache c;c.logRate=std::log(m.rate);
  const double right=std::max(1e-6,std::hypot(static_cast<double>(m.rightRe),static_cast<double>(m.rightIm)));
  c.ratio=std::log(right/std::max(1e-6,static_cast<double>(m.left)));
  c.angle=std::atan2(static_cast<double>(m.rightIm),static_cast<double>(m.rightRe));
  for(int i=0;i<layers;++i)c.phase[i]={std::cos(m.phase[i]),std::sin(m.phase[i])};
  return c;
}

double levelAt(const Model& model,const std::array<float,measured::maxLayers>& db,double velocity) noexcept {
  // Piecewise linear in dB between the recorded layers, continued with the
  // end segments' slopes (never rising toward softer playing).
  const float* v=model.layerVelocity;
  const int last=model.layers-1;
  if(velocity<=v[0])return db[0]-std::max(0.f,(db[1]-db[0])/(v[1]-v[0]))*(v[0]-velocity);
  if(velocity>=v[last])return db[last]+std::max(0.f,(db[last]-db[last-1])/(v[last]-v[last-1]))*(velocity-v[last]);
  int i=0;while(velocity>v[i+1])++i;
  return mix(db[i],db[i+1],(velocity-v[i])/(v[i+1]-v[i]));
}
double onsetRiseAt(const Model& model,const measured::Anchor& anchor,double velocity) noexcept {
  // Log-linear between the recorded layers, held beyond them.
  const float* v=model.layerVelocity;const auto& r=anchor.onsetRise;
  const int last=model.layers-1;
  if(velocity<=v[0])return std::log(r[0]);
  if(velocity>=v[last])return std::log(r[last]);
  int i=0;while(velocity>v[i+1])++i;
  return mix(std::log(r[i]),std::log(r[i+1]),(velocity-v[i])/(v[i+1]-v[i]));
}
Complex unit(Complex z,Complex fallback) noexcept {
  const double norm=std::sqrt(z.re*z.re+z.im*z.im);
  return norm>1e-6?Complex{z.re/norm,z.im/norm}:fallback;
}
Complex phaseAt(const Model& model,const LaneCache& lane,double velocity) noexcept {
  // A lane's phase against the partial's strongest lane, held beyond the
  // recorded layers and interpolated on the unit circle between them.
  const float* v=model.layerVelocity;const auto& ph=lane.phase;
  const int last=model.layers-1;
  if(velocity<=v[0])return ph[0];
  if(velocity>=v[last])return ph[last];
  int i=0;while(velocity>v[i+1])++i;
  const double t=(velocity-v[i])/(v[i+1]-v[i]);
  const Complex a=ph[i],b=ph[i+1];
  return unit({mix(a.re,b.re,t),mix(a.im,b.im,t)},t<.5?a:b);
}
LaneData laneAt(const Model& model,const measured::Lane& m,const LaneCache& c,double velocity) noexcept {
  LaneData l;l.rate=c.logRate;l.offset=m.offsetHz;l.level=levelAt(model,m.levelDb,velocity);l.phase=phaseAt(model,c,velocity);
  l.ratio=c.ratio;l.angle=c.angle;l.left={m.left,0};l.right={m.rightRe,m.rightIm};
  return l;
}
PartialData single(const Model& model,const measured::Partial& p,const std::array<LaneCache,lanes>& c,double velocity) noexcept {
  PartialData d;d.order=p.order;d.cents=p.cents;
  d.rise=std::log(p.riseSeconds)+p.riseSlope*(velocity-64)/64;
  for(int j=0;j<lanes;++j)d.lane[j]=laneAt(model,p.lanes[j],c[j],velocity);
  return d;
}
LaneData blendLane(const LaneData& x,const LaneData& y,double t) noexcept {
  LaneData l;
  l.rate=mix(x.rate,y.rate,t);l.offset=mix(x.offset,y.offset,t);l.level=mix(x.level,y.level,t);
  // Phases come from the nearer anchor: each is one measured pattern of
  // the strike's arrival across the partials, and a blend of two is neither.
  l.phase=t<.5?x.phase:y.phase;
  // The pickup shape (left real, unit mean channel power) is blended as its
  // channels' level difference in dB and their phase difference along the
  // shorter arc. The microphones hear the board about 3.4 ms apart, so like
  // partials of two recorded pitches can arrive half a turn apart in phase;
  // blended as vectors they cancelled a channel, putting D#3's fundamental
  // 12 dB further left than either C3 or F#3 has it.
  const double g=std::exp(mix(x.ratio,y.ratio,t));
  const double phase=x.angle+t*std::remainder(y.angle-x.angle,2*pi);
  const double left=std::sqrt(2/(1+g*g));
  l.left={left,0};l.right={left*g*std::cos(phase),left*g*std::sin(phase)};
  return l;
}
PartialData blend(const PartialData& a,const PartialData& b,double t) noexcept {
  PartialData d;d.order=a.order;d.cents=mix(a.cents,b.cents,t);
  d.rise=mix(a.rise,b.rise,t);
  // Lanes are stored fastest first, so like roles meet.
  for(int j=0;j<lanes;++j)d.lane[j]=blendLane(a.lane[j],b.lane[j],t);
  return d;
}
// The recorded pitch above a key, or the last one; the one below is upper - 1.
int upperAnchor(const Model& model,int note) noexcept {
  int upper=1;while(upper<model.anchorCount-1&&model.anchors[upper].note<note)++upper;
  return upper;
}
// The fundamental (Hz at A4 = 440 Hz) the engine gives a key: its cents from
// equal temperament between the recorded pitches around it, continued from
// the last two beyond them.
double keyPitch(const Model& model,int note) noexcept {
  const int upper=upperAnchor(model,note);
  const auto& a=model.anchors[upper-1];const auto& b=model.anchors[upper];
  auto cents=[](const measured::Anchor& x){return 1200*std::log2(x.f1/(440*std::pow(2.,(x.note-69)/12.)));};
  return 440*std::pow(2.,(note-69+mix(cents(a),cents(b),static_cast<double>(note-a.note)/(b.note-a.note))/100)/12.);
}
// A key's stiffness B, between the recorded pitches around it like its pitch.
double keyStiffness(const Model& model,int note) noexcept {
  const int upper=upperAnchor(model,note);
  const auto& a=model.anchors[upper-1];const auto& b=model.anchors[upper];
  return std::exp(mix(std::log(a.B),std::log(b.B),static_cast<double>(note-a.note)/(b.note-a.note)));
}
}

struct Engine::Impl {
  std::array<Voice,maxVoices> voices{};
  // The piano that plays.
  const Model* model=&models[0];
  // Every piano's measured lanes' caches (see LaneCache), filled at construction.
  std::array<std::array<LaneCache,lanes>,partialCaches> partialLanes{};
  std::array<LaneCache,extraCaches> extraLanes{};
  // Each undamped string's frequency (Hz at A4 = 440 Hz).
  std::array<double,halo> haloHz{};
  std::array<Channel,16> channels{};
  std::array<Resonator,88> sympathetic{};
  std::array<double,88> openness{};
  std::array<double,sineSize+1> sine{};
  std::array<V4,chunk> mixLeft{},mixRight{};
  // The body rings in `ring`. `onset` holds the same modes decaying faster by
  // the measured body rise; each strike adds its knock to the one and takes
  // it from the other, so their sum starts from zero. The action's knocks
  // (keys let go, the sustain pedal) build up more slowly, by the action's
  // rise in `actionOnset`.
  Body ring{},onset{},actionOnset{};
  bool ringing=false,rising=false,actionRising=false;
  std::array<Burst,maxBursts> bursts{};
  std::array<NoiseBand,noiseBands> noise{};
  std::array<double,chunk> noiseLeft{},noiseRight{};
  std::uint32_t seed=1;
  bool hissing=false;
  Parameters parameters{};
  double sampleRate=48000,gain=.7,width=.75,mute=0;
  double smooth=0,controlSmooth=0,highpassCoefficient=0,highpassL=0,highpassR=0,previousL=0,previousR=0;
  float previousBrightness=.5f;
  std::uint64_t serial=0,frame=0;
  std::uint64_t clock=0; // samples processed since reset, asleep or not
  bool legacyAttack=false;
  bool sleeping=true;
  bool pedalHeld=false;  // the sustain pedal's dampers off the strings

  Complex rotation(double frequency) const noexcept {
    double phase=frequency/sampleRate;
    phase=std::max(-.45,std::min(.45,phase));
    const bool negative=phase<0;
    const double position=std::abs(phase)*sineSize;
    const int index=static_cast<int>(position);
    const double fraction=position-index;
    double s=mix(sine[index],sine[index+1],fraction);
    const int ci=(index+sineSize/4)%sineSize;
    double c=mix(sine[ci],sine[ci+1],fraction);
    // Linear wavetable interpolation slightly shrinks the unit circle. Exact
    // normalization here prevents artificial long-tail decay or energy growth.
    const double inverse=1/std::sqrt(c*c+s*s);
    c*=inverse;s*=inverse;
    return {c,negative?-s:s};
  }
  double tuningRatio(int ch) const noexcept {return parameters.tuning/440.*std::pow(2.,channels[ch].bend/12.);}
  void tunePartial(Partial& partial,double ratio) noexcept {
    for(int j=0;j<lanes;++j){const Complex r=rotation(partial.hz[j]*ratio);
      partial.natural[j]={r.re*partial.decay[j],r.im*partial.decay[j]};}
    partial.targetAudibility=partial.frequency*ratio<sampleRate*.45?1.f:0.f;
  }
  void capture(int ch) noexcept {
    auto& state=channels[ch];
    const bool down=pedalLevel(parameters.sostenuto,state.sostenuto,state.keySwitches[1])>=.5f;
    if(down&&!state.sostDown)
      for(int n=0;n<88;++n)state.captured[n]=state.presses[n]>0;
    if(!down)state.captured.fill(false);
    state.sostDown=down;
  }
  // Frequencies follow tuning and bends from the next chunk boundary, so the
  // exact state is never advanced with a rotation that was not used.
  void retune(int ch) noexcept {for(auto& voice:voices)if(voice.active&&voice.channel==ch)voice.retune=true;}
  void placeHalo() noexcept {
    for(int j=0;j<halo;++j)haloHz[j]=keyPitch(*model,firstHalo+j)*std::pow(2.,model->haloStrings[j].cents/1200);
  }
  // What sounds is the other piano's strings, body and noise, so a switch
  // silences it, as all sound off does. Held keys and pedals keep their state.
  void choose(const Model& next) noexcept {
    model=&next;
    for(auto& voice:voices)voice.active=false;
    for(auto& r:sympathetic){r.q=0;r.p=0;}
    silenceBody();silenceNoise();
    highpassL=highpassR=previousL=previousR=0;
    placeHalo();retuneSympathetic();prepareBody();prepareNoise();
  }
  void retuneSympathetic() noexcept {
    // The shared open-string bank follows concert tuning, independently of
    // channel pitch bends. Rebuild coefficients without resetting its q/p.
    // The undamped strings ring at their measured frequencies and rates.
    for(int i=0;i<88;++i){auto& mode=sympathetic[i];
      const int j=i+21-firstHalo;
      const double frequency=j<0?parameters.tuning*std::pow(2.,(i+21-69)/12.):haloHz[j]*parameters.tuning/440;
      const Complex r=rotation(frequency);mode.c=r.re;mode.s=r.im;
      mode.decay=std::exp(-(j<0?.7+.001*frequency:model->haloStrings[j].rate)/sampleRate);
    }
  }
  void prepareBody() noexcept {
    // Each bank's decay per sample beyond the ring's.
    const double settle[3]={1,std::exp(-1/(model->bodyRise*sampleRate)),std::exp(-1/(model->actionRise*sampleRate))};
    for(int m=0;m<bodyBanks*lanes;++m){
      const int k=m/lanes,j=m%lanes;
      const bool real=m<model->bodyModeCount;const auto& mode=model->bodyModes[real?m:0];
      const double d=real?std::exp(-mode.rate/sampleRate):0,w=2*pi*mode.hz/sampleRate;
      const Complex step{d*std::cos(w),d*std::sin(w)};
      BodyBank* banks[3]={&ring[k],&onset[k],&actionOnset[k]};
      for(int b=0;b<3;++b){auto* bank=banks[b];
        const Complex s=b==0?step:Complex{step.re*settle[b],step.im*settle[b]};
        bank->step[j]=s;bank->leap[j]=power(s,chunk);
        setLane(bank->c,j,static_cast<float>(s.re));setLane(bank->s,j,static_cast<float>(s.im));
        setLane(bank->left,j,real?mode.left:0.f);
        setLane(bank->rightRe,j,real?mode.rightRe:0.f);setLane(bank->rightIm,j,real?mode.rightIm:0.f);
      }
    }
  }
  // The power response at w (rad/sample) of one section, b0 (1 - z^-2) over
  // 1 + a1 z^-1 + a2 z^-2.
  static double sectionPower(double b0,double a1,double a2,double w) noexcept {
    const double re=1+a1*std::cos(w)+a2*std::cos(2*w),im=a1*std::sin(w)+a2*std::sin(2*w);
    return b0*b0*(2-2*std::cos(2*w))/(re*re+im*im);
  }
  void prepareNoise() noexcept {
    // Sixth-order Butterworth third-octave band-passes, the IEC 61260 kind,
    // with unit gain at their centres. Second-order band-passes fall only
    // 6 dB per octave: above the treble's fundamentals, where the measured
    // noise falls about 20 dB per octave, their skirts stood 25-50 dB over the
    // measured densities from 6 to 16 kHz. A band's scale turns a noise
    // density (1/Hz) into the gain on its uniform source (variance 1/3),
    // shared with the neighbouring bands' skirts.
    for(auto& band:noise)band.scale=0;
    auto warp=[this](double f){const double x=pi*f/sampleRate;return 2*sampleRate*std::sin(x)/std::cos(x);};
    for(int b=0;b<noiseBands;++b){
      const double hz=model->noiseBands[b].hz;
      if(hz*std::pow(2.,1/6.)>.45*sampleRate)continue;
      auto& band=noise[b];
      // Each pole of the low-pass prototype maps to one pole pair of the band,
      // whose edges, a sixth of an octave either side, are prewarped for the
      // bilinear transform; every section has one zero at DC and one at Nyquist.
      const double lo=warp(hz*std::pow(2.,-1/6.)),hi=warp(hz*std::pow(2.,1/6.));
      const double centre=std::sqrt(lo*hi),width=hi-lo,w=2*pi*hz/sampleRate;
      for(int j=0;j<noiseSections;++j){
        const double angle=pi*(2*j+noiseSections+1)/(2*noiseSections);
        const Complex q{std::cos(angle)*width/2,std::sin(angle)*width/2};
        const Complex d{q.re*q.re-q.im*q.im-centre*centre,2*q.re*q.im};
        const double m=std::sqrt(d.re*d.re+d.im*d.im);
        const Complex r{std::sqrt((m+d.re)/2),(d.im<0?-1:1)*std::sqrt((m-d.re)/2)};
        Complex pole{q.re+r.re,q.im+r.im};
        if(pole.im<0)pole={q.re-r.re,q.im-r.im};
        const double nr=2*sampleRate+pole.re,dr=2*sampleRate-pole.re,dd=dr*dr+pole.im*pole.im;
        const Complex z{(nr*dr-pole.im*pole.im)/dd,(pole.im*dr+nr*pole.im)/dd};
        band.a1[j]=-2*z.re;band.a2[j]=z.re*z.re+z.im*z.im;
        band.b0[j]=1/std::sqrt(sectionPower(1,band.a1[j],band.a2[j],w));
      }
      const double theta=std::acos(bounded(model->noiseBands[b].coherence))/2;
      band.c=std::cos(theta);band.s=std::sin(theta);band.scale=1;
    }
    for(int b=0;b<noiseBands;++b){auto& band=noise[b];if(band.scale==0)continue;
      const double w=2*pi*model->noiseBands[b].hz/sampleRate;double overlap=0;
      for(const auto& other:noise)if(other.scale!=0){double power=1;
        for(int j=0;j<noiseSections;++j)power*=sectionPower(other.b0[j],other.a1[j],other.a2[j],w);
        overlap+=power;}
      band.scale=std::sqrt(3*sampleRate/2/overlap);
    }
  }
  void silenceNoise() noexcept {
    for(auto& burst:bursts)burst.active=false;
    for(auto& band:noise){
      for(int j=0;j<noiseSections;++j)for(int k=0;k<2;++k)band.x1[j][k]=band.x2[j][k]=band.y1[j][k]=band.y2[j][k]=0;
      band.left=band.right=band.leftStep=band.rightStep=band.leftEnd=band.rightEnd=0;
    }
    seed=1;hissing=false;
  }
  Burst& claimBurst() noexcept {
    Burst* chosen=&bursts[0];
    for(auto& burst:bursts){if(!burst.active)return burst;if(burst.serial<chosen->serial)chosen=&burst;}
    return *chosen;
  }
  // At a chunk boundary: each band ramps from where the last chunk ended to
  // the bursts' sum at this chunk's end; below -180 dB a burst ends.
  void advanceNoise() noexcept {
    double target[2][noiseBands]{};bool any=false;
    for(auto& burst:bursts)if(burst.active){double energy=0;
      for(int b=0;b<noiseBands;++b){
        burst.left[b]*=burst.step[b];burst.right[b]*=burst.step[b];
        target[0][b]+=burst.left[b];target[1][b]+=burst.right[b];
        energy+=burst.left[b]*burst.left[b]+burst.right[b]*burst.right[b];}
      burst.active=energy>=1e-18;any=any||burst.active;}
    for(int b=0;b<noiseBands;++b){auto& band=noise[b];
      band.left=band.leftEnd;band.right=band.rightEnd;
      band.leftEnd=target[0][b];band.rightEnd=target[1][b];
      band.leftStep=(band.leftEnd-band.left)/chunk;band.rightStep=(band.rightEnd-band.right)/chunk;
      any=any||band.left>0||band.right>0;}
    hissing=any;
  }
  void hiss(int frames) noexcept {
    for(int i=0;i<frames;++i){
      double source[2];
      for(double& x:source){seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;
        x=(static_cast<double>(seed)-2147483648.)*(1./2147483648.);}
      double l=0,r=0;
      for(auto& band:noise)if(band.scale!=0){
        double y[2];
        for(int k=0;k<2;++k){y[k]=source[k];
          for(int j=0;j<noiseSections;++j){
            const double x=y[k];
            y[k]=band.b0[j]*(x-band.x2[j][k])-band.a1[j]*band.y1[j][k]-band.a2[j]*band.y2[j][k];
            band.x2[j][k]=band.x1[j][k];band.x1[j][k]=x;band.y2[j][k]=band.y1[j][k];band.y1[j][k]=y[k];}}
        const double mid=band.c*y[0],side=band.s*y[1];
        l+=band.left*(mid+side);r+=band.right*(mid-side);
        band.left+=band.leftStep;band.right+=band.rightStep;
      }
      noiseLeft[i]=l;noiseRight[i]=r;
    }
  }
  void silenceBody() noexcept {
    Body* bodies[3]={&ring,&onset,&actionOnset};
    for(auto* body:bodies)for(auto& bank:*body){bank.re=bank.im=V4{};for(auto& z:bank.exact)z={};}
    ringing=rising=actionRising=false;
  }
  double dampingFactor(const Voice& voice,const Partial& partial) const noexcept {
    const double m=channels[voice.channel].smoothedMute;
    return 1/(1+voice.contact*partial.damperScale+180*m*m/sampleRate*(.5+partial.frequency*.00015));
  }
  static void setRotation(Partial& partial,double damping) noexcept {
    for(int j=0;j<lanes;++j){
      partial.step[j]={partial.natural[j].re*damping,partial.natural[j].im*damping};
      partial.leap[j]=power(partial.step[j],chunk);
      setLane(partial.c,j,static_cast<float>(partial.step[j].re));setLane(partial.s,j,static_cast<float>(partial.step[j].im));
    }
  }
  void updateWeights(Partial& partial) noexcept {
    const float g=partial.tint*partial.audibility;
    for(int j=0;j<lanes;++j){
      setLane(partial.leftRe,j,partial.baseLeftRe[j]*g);setLane(partial.leftIm,j,partial.baseLeftIm[j]*g);
      setLane(partial.rightRe,j,partial.baseRightRe[j]*g);setLane(partial.rightIm,j,partial.baseRightIm[j]*g);
    }
  }
  // Called at every chunk boundary: pedals and dampers, then each partial's
  // float lanes restart from its exact state and the exact state advances one
  // chunk with this chunk's rotation.
  void boundary() noexcept {
    mute+=controlSmooth*(parameters.mute-mute);
    for(auto& channel:channels)
      channel.smoothedMute+=controlSmooth*(std::max(parameters.mute,channel.mute)-channel.smoothedMute);
    if(ringing)ringing=advance(ring);
    if(rising)rising=advance(onset);
    if(actionRising)actionRising=advance(actionOnset);
    if(hissing)advanceNoise();
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
      voice.contact=voice.note>=89?0:std::pow(std::max(0.,(voice.damper-.08)/.92),2.5);
      const bool damping=voice.contact!=voice.appliedContact||channel.smoothedMute!=voice.appliedMute;
      voice.appliedContact=voice.contact;voice.appliedMute=channel.smoothedMute;
      const double ratio=voice.retune?tuningRatio(voice.channel):0;
      double energy=0;
      for(int k=0;k<voice.count;){auto& partial=voice.partials[k];
        if(voice.retune)tunePartial(partial,ratio);
        bool weights=tintChanged;
        if(tintChanged)partial.tint=static_cast<float>(std::pow(2.,(parameters.brightness-.5)*partial.tintScale));
        if(partial.audibility!=partial.targetAudibility){
          const float step=static_cast<float>(controlSmooth)*(partial.targetAudibility-partial.audibility);
          partial.audibility=std::abs(step)<1e-6f?partial.targetAudibility:partial.audibility+step;weights=true;}
        if(weights)updateWeights(partial);
        if(partial.rising){
          // Below -140 dB the rise is complete and the partial runs unscaled.
          partial.riseRemaining=static_cast<float>(partial.riseExact);
          partial.rising=partial.riseExact>1e-7;
          partial.riseExact*=partial.riseLeap;
        }
        double e=0;
        for(int j=0;j<lanes;++j){const Complex z=partial.exact[j];
          setLane(partial.re,j,static_cast<float>(z.re));setLane(partial.im,j,static_cast<float>(z.im));
          e+=(z.re*z.re+z.im*z.im)*partial.energyWeight[j];}
        e*=partial.audibility*partial.audibility*partial.tint*partial.tint;
        if(e<1e-15&&partial.targetAudibility==partial.audibility){partial=voice.partials[--voice.count];continue;}
        energy+=e;
        if(damping||voice.retune)setRotation(partial,dampingFactor(voice,partial));
        for(int j=0;j<lanes;++j)partial.exact[j]=partial.exact[j]*partial.leap[j];
        ++k;
      }
      voice.retune=false;
      if(voice.count==0||energy<1e-15)voice.active=false;
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
    voice.count=0;voice.serial=++serial;voice.damper=0;voice.contact=0;voice.retune=false;
    voice.appliedContact=0;voice.appliedMute=channel.smoothedMute;
    const double soft=pedalLevel(parameters.soft,channel.soft,channel.keySwitches[0]);
    // MIDI velocity is a recording-layer coordinate, not measured hammer speed.
    const double v=127*bounded(velocity);
    channel.velocity[note-21]=bounded(velocity);channel.struck[note-21]=clock;
    const Model& m=*model;
    const int upper=upperAnchor(m,note);
    const auto& a=m.anchors[upper-1];const auto& b=m.anchors[upper];
    // Keys beyond the last recorded pitch keep its partials but follow the
    // stretch and stiffness trend of the last two.
    const double reach=static_cast<double>(note-a.note)/(b.note-a.note),t=std::max(0.,std::min(1.,reach));
    const double f1=keyPitch(m,note),B=keyStiffness(m,note);
    const double highest=std::min(17000.,sampleRate*.43);
    // No partial rises faster than its recorded pitch's onset builds up.
    const double shortestRise=std::exp(mix(onsetRiseAt(m,a,v),onsetRiseAt(m,b,v),t));
    const double ratio=tuningRatio(ch);
    const double softGain=1-.28*soft;
    // Samples until the next chunk boundary: the exact state is kept there.
    const int ahead=static_cast<int>((chunk-(frame%chunk))%chunk);
    // The body's knock: levels between the two pitches like the partials',
    // phases from the nearer one.
    const auto* ka=m.knocks+(upper-1)*m.bodyModeCount;const auto* kb=ka+m.bodyModeCount;
    for(int k=0;k<m.bodyModeCount;++k){const auto& x=ka[k];const auto& y=kb[k];
      const double level=mix(x.levelDb,y.levelDb,t)+mix(x.slopeDb,y.slopeDb,t)*(v-64)/64;
      const double amplitude=std::pow(10.,level/20)*softGain,phase=t<.5?x.phase:y.phase;
      const Complex g{amplitude*std::cos(phase),amplitude*std::sin(phase)};
      knock(ring[k/lanes],k%lanes,g,ahead);knock(onset[k/lanes],k%lanes,{-g.re,-g.im},ahead);
    }
    ringing=rising=true;
    // The undamped strings: the strike sets every one ringing but its own
    // key's, which its partials play, at the level the two pitches around
    // the key set it (dB between them), softened and tinted like a
    // component of its order. They ring on in the shared bank whatever
    // damps the strings. The recordings do not fix their phases, so each
    // key gives each string a fixed one.
    for(int j=0;j<halo;++j){const int key=firstHalo+j;
      if(key==note||haloHz[j]*parameters.tuning/440>highest)continue;
      const double order=std::max(1.,haloHz[j]/f1);
      const double level=mix(m.haloLevels[(upper-1)*halo+j],m.haloLevels[upper*halo+j],t)+m.haloSlopeDb*(v-64)/64;
      const double amplitude=std::pow(10.,level/20)*softGain*std::exp(-soft*.115*(order-1))
                             *std::pow(2.,(parameters.brightness-.5)*std::min(4.,std::log2(order)));
      const double phase=2*pi*std::fmod(.6180339887498949*(note*halo+key),1.);
      auto& mode=sympathetic[key-21];mode.q+=amplitude*std::cos(phase);mode.p+=amplitude*std::sin(phase);
    }
    // The board's noise: each band's density between the pitches like the
    // partials' levels, tinted and softened like a partial of its order.
    auto& burst=claimBurst();
    const auto* na=m.noise+(upper-1)*noiseBands;const auto* nb=na+noiseBands;
    for(int k=0;k<noiseBands;++k){const auto& x=na[k];const auto& y=nb[k];
      const double density=mix(levelAt(m,x.densityDb,v),levelAt(m,y.densityDb,v),t);
      const double order=std::max(1.,m.noiseBands[k].hz/f1);
      const double amplitude=std::pow(10.,density/20)*noise[k].scale*softGain*std::exp(-soft*.115*(order-1))
                             *std::pow(2.,(parameters.brightness-.5)*std::min(4.,std::log2(order)));
      const double balance=mix(x.balanceDb,y.balanceDb,t);
      burst.left[k]=amplitude*std::pow(10.,-balance/40);burst.right[k]=amplitude*std::pow(10.,balance/40);
      burst.step[k]=std::exp(-std::exp(mix(std::log(x.rate),std::log(y.rate),t))*chunk/sampleRate);
    }
    burst.active=true;burst.serial=serial;hissing=true;
    int i=a.first,j=b.first;const int ia=a.first+a.count,jb=b.first+b.count;
    while((i<ia||j<jb)&&voice.count<maxPartials){
      PartialData d;double weight=1;
      const int oa=i<ia?m.partials[i].order:1<<30,ob=j<jb?m.partials[j].order:1<<30;
      const auto* cache=&partialLanes[m.partialFirst];
      if(oa==ob){d=blend(single(m,m.partials[i],cache[i],v),single(m,m.partials[j],cache[j],v),t);++i;++j;}
      else if(oa<ob){d=single(m,m.partials[i],cache[i],v);++i;weight=1-t;}
      else{d=single(m,m.partials[j],cache[j],v);++j;weight=t;}
      if(weight<=0)continue;
      const int order=d.order;
      const double frequency=order*f1*std::sqrt((1+B*order*order)/(1+B))*std::pow(2.,d.cents/1200);
      if(frequency>highest)break;
      // Una corda reduces high-frequency excitation progressively and moves
      // energy from the prompt lane to the slowest one, as the unstruck
      // string is driven only through the bridge.
      const double felt=std::exp(-soft*.115*(order-1))*softGain*weight;
      const double laneSoft[lanes]={1-.28*soft,1,1,1+.08*soft};
      auto& partial=voice.partials[voice.count];
      partial.frequency=frequency;
      // Felt loss once the damper lands: about 500 dB/s on a released C4.
      // Measured C4-C5 terminations on a Yamaha C7 fall 220-470 dB/s after a
      // quick key release (Taguti et al., Acoust. Sci. & Tech. 23(5), 2002,
      // Table 6). The Salamander release recordings cannot set it
      // (Docs/research/release-recordings-2026-10-27.md).
      partial.damperScale=(24+1.4*std::sqrt(frequency)+.001*frequency)/sampleRate;
      partial.tintScale=std::min(4.,std::log2(static_cast<double>(order)));
      partial.tint=static_cast<float>(std::pow(2.,(parameters.brightness-.5)*partial.tintScale));
      double peak=0;
      for(int k=0;k<lanes;++k){const auto& l=d.lane[k];
        const double amplitude=std::pow(10.,l.level/20)*felt*laneSoft[k];
        peak+=amplitude;
        partial.decay[k]=std::exp(-std::exp(l.rate)/sampleRate);
        partial.hz[k]=frequency+l.offset;
        const Complex g{l.phase.re*amplitude,l.phase.im*amplitude},wl=g*l.left,wr=g*l.right;
        partial.baseLeftRe[k]=static_cast<float>(wl.re);partial.baseLeftIm[k]=static_cast<float>(wl.im);
        partial.baseRightRe[k]=static_cast<float>(wr.re);partial.baseRightIm[k]=static_cast<float>(wr.im);
      }
      if(peak<1e-7)continue;
      launch(voice,partial,legacyAttack?.002:std::max(std::exp(d.rise),shortestRise),ahead,ratio);
      ++voice.count;
    }
    // Single components (one measured lane each) share a slot four at a time,
    // one to a lane, in order of frequency; the slot's damping and tint follow
    // its members. Each starts at contact, under the pitch's onset rise.
    int filled=0;double hzSum=0,orderSum=0,peak=0;
    const auto add=[&](double frequency,double order,const LaneData& l){
      auto& slot=voice.partials[voice.count];const int k=filled++;
      const double amplitude=std::pow(10.,l.level/20)*softGain*std::exp(-soft*.115*(order-1));
      const Complex g{l.phase.re*amplitude,l.phase.im*amplitude},wl=g*l.left,wr=g*l.right;
      slot.decay[k]=std::exp(-std::exp(l.rate)/sampleRate);slot.hz[k]=frequency+l.offset;
      slot.baseLeftRe[k]=static_cast<float>(wl.re);slot.baseLeftIm[k]=static_cast<float>(wl.im);
      slot.baseRightRe[k]=static_cast<float>(wr.re);slot.baseRightIm[k]=static_cast<float>(wr.im);
      hzSum+=frequency;orderSum+=order;peak+=amplitude;
    };
    const auto close=[&](bool damped){
      auto& slot=voice.partials[voice.count];
      for(int k=filled;k<lanes;++k){
        slot.decay[k]=0;slot.hz[k]=hzSum/filled;
        slot.baseLeftRe[k]=slot.baseLeftIm[k]=slot.baseRightRe[k]=slot.baseRightIm[k]=0;}
      slot.frequency=hzSum/filled;
      slot.damperScale=damped?(24+1.4*std::sqrt(slot.frequency)+.001*slot.frequency)/sampleRate:0;
      slot.tintScale=std::min(4.,std::log2(orderSum/filled));
      slot.tint=static_cast<float>(std::pow(2.,(parameters.brightness-.5)*slot.tintScale));
      if(peak>=1e-7){
        launch(voice,slot,legacyAttack?.002:shortestRise,ahead,ratio);
        ++voice.count;}
      filled=0;hzSum=orderSum=peak=0;
    };
    // The components beside the series pair with nothing at the other pitch,
    // so each anchor's are cross-faded in power.
    const double share[2]={std::sqrt(1-t),std::sqrt(t)};
    const auto place=[&](const measured::Extra& e){
      const double n=e.order;return n*f1*std::sqrt((1+B*n*n)/(1+B))*std::pow(2.,e.cents/1200);};
    int ea=a.extraFirst,eb=b.extraFirst;
    const int enda=a.extraFirst+a.extraCount,endb=b.extraFirst+b.extraCount;
    while((ea<enda||eb<endb)&&voice.count<maxPartials){
      const bool first=eb>=endb||(ea<enda&&place(m.extras[ea])<=place(m.extras[eb]));
      const int k=first?ea++:eb++;const auto& e=m.extras[k];
      const double weight=share[first?0:1],frequency=place(e);
      if(weight<=0||frequency>highest)continue;
      LaneData l=laneAt(m,e.lane,extraLanes[m.extraFirst+k],v);l.level+=20*std::log10(weight);
      add(frequency,e.order,l);
      if(filled==lanes)close(true);
    }
    if(filled>0&&voice.count<maxPartials)close(true);
    if(voice.count==0)voice.active=false;
  }
  // A partial's rise, tuning, weights and state from its strike, `ahead`
  // samples before the next chunk boundary.
  void launch(const Voice& voice,Partial& partial,double rise,int ahead,double ratio) noexcept {
    partial.riseStep=std::exp(-1/(rise*sampleRate));
    partial.riseLeap=std::pow(partial.riseStep,chunk);
    partial.riseExact=std::pow(partial.riseStep,ahead);
    partial.riseRemaining=1;partial.riseDecay=static_cast<float>(partial.riseStep);
    partial.rising=true;
    for(int k=0;k<lanes;++k)
      partial.energyWeight[k]=static_cast<double>(partial.baseLeftRe[k])*partial.baseLeftRe[k]+static_cast<double>(partial.baseLeftIm[k])*partial.baseLeftIm[k]
                             +static_cast<double>(partial.baseRightRe[k])*partial.baseRightRe[k]+static_cast<double>(partial.baseRightIm[k])*partial.baseRightIm[k];
    tunePartial(partial,ratio);
    partial.audibility=partial.targetAudibility;
    updateWeights(partial);
    setRotation(partial,dampingFactor(voice,partial));
    for(int k=0;k<lanes;++k){
      setLane(partial.re,k,1.f);setLane(partial.im,k,0.f);
      partial.exact[k]=power(partial.step[k],ahead);
    }
  }
  // A knock of the action on the body between two recorded pitches' (levels
  // mixed, phases from the nearer), building up under the action's rise.
  void actionKnock(const measured::ActionKnock* x,const measured::ActionKnock* y,double t,double gainDb) noexcept {
    sleeping=false;
    const int ahead=static_cast<int>((chunk-(frame%chunk))%chunk);
    for(int m=0;m<model->bodyModeCount;++m){
      const double amplitude=std::pow(10.,(mix(x[m].levelDb,y[m].levelDb,t)+gainDb)/20),phase=t<.5?x[m].phase:y[m].phase;
      const Complex g{amplitude*std::cos(phase),amplitude*std::sin(phase)};
      knock(ring[m/lanes],m%lanes,g,ahead);knock(actionOnset[m/lanes],m%lanes,{-g.re,-g.im},ahead);
    }
    ringing=actionRising=true;
  }
  // A key let go: its damper falls back onto the strings unless a pedal holds
  // it off them, and the key returns. From F6 up there is no damper to fall,
  // so the key sounds alone; the recordings of those keys are that sound.
  void release(int note,int ch) noexcept {
    const auto& channel=channels[ch];const int key=note-21;
    if(note<89&&(channel.captured[key]||pedalLevel(parameters.sustain,channel.sustain,channel.keySwitches[2])>=pedalClear))return;
    const double v=channel.velocity[key],held=static_cast<double>(clock-channel.struck[key])/sampleRate;
    const Model& m=*model;
    const int upper=upperAnchor(m,note);
    const auto& a=m.anchors[upper-1];const auto& b=m.anchors[upper];
    const double t=std::max(0.,std::min(1.,static_cast<double>(note-a.note)/(b.note-a.note)));
    const auto* x=m.releaseKnocks+(upper-1)*m.bodyModeCount;
    actionKnock(x,x+m.bodyModeCount,t,
                m.releaseDb+20*std::log10(trackingGain(m.releaseTracking,v)/trackingGain(m.noteTracking,v))-m.releaseFadeDbPerSecond*held);
  }
  // After anything that moves the sustain pedal: at an end of its travel it
  // sounds, unless `audible` is false for a reset.
  void pedalEdge(bool audible=true) noexcept {
    float level=0;
    for(const auto& c:channels)level=std::max(level,pedalLevel(parameters.sustain,c.sustain,c.keySwitches[2]));
    const bool held=level>=pedalClear||(pedalHeld&&level>pedalRest);
    if(audible&&held!=pedalHeld&&model->pedalDown){
      const auto* k=held?model->pedalDown:model->pedalUp;actionKnock(k,k,0,held?model->pedalDownDb:model->pedalUpDb);}
    pedalHeld=held;
  }
  void ringBody(Body& body,int frames) noexcept {
    for(auto& bank:body){
      V4 re=bank.re,im=bank.im;
      const V4 c=bank.c,s=bank.s,l=bank.left,rr=bank.rightRe,ri=bank.rightIm;
      for(int i=0;i<frames;++i){
        mixLeft[i]+=l*re;mixRight[i]+=rr*re-ri*im;
        const V4 next=re*c-im*s;im=re*s+im*c;re=next;
      }
      bank.re=re;bank.im=im;
    }
  }
  void render(float* left,float* right,int frames) noexcept {
    const V4 zero{};
    for(int i=0;i<frames;++i){mixLeft[i]=zero;mixRight[i]=zero;}
    for(auto& voice:voices)if(voice.active)
      for(int k=0;k<voice.count;++k){auto& partial=voice.partials[k];
        V4 re=partial.re,im=partial.im;
        const V4 c=partial.c,s=partial.s,lr=partial.leftRe,li=partial.leftIm,rr=partial.rightRe,ri=partial.rightIm;
        if(partial.rising){
          float d=partial.riseRemaining;const float decay=partial.riseDecay;
          for(int i=0;i<frames;++i){
            const V4 g=splat(1-d);d*=decay;
            mixLeft[i]+=(lr*re-li*im)*g;mixRight[i]+=(rr*re-ri*im)*g;
            const V4 next=re*c-im*s;im=re*s+im*c;re=next;
          }
          partial.riseRemaining=d;
        }else
          for(int i=0;i<frames;++i){
            mixLeft[i]+=lr*re-li*im;mixRight[i]+=rr*re-ri*im;
            const V4 next=re*c-im*s;im=re*s+im*c;re=next;
          }
        partial.re=re;partial.im=im;
      }
    if(ringing)ringBody(ring,frames);
    if(rising)ringBody(onset,frames);
    if(actionRising)ringBody(actionOnset,frames);
    const bool noisy=hissing;
    if(noisy)hiss(frames);
    for(int i=0;i<frames;++i){
      gain+=smooth*(parameters.gain-gain);width+=smooth*(parameters.width-width);
      const V4 l4=mixLeft[i],r4=mixRight[i];
      double l=static_cast<double>(lane(l4,0))+lane(l4,1)+lane(l4,2)+lane(l4,3);
      double r=static_cast<double>(lane(r4,0))+lane(r4,1)+lane(r4,2)+lane(r4,3);
      if(noisy){l+=noiseLeft[i];r+=noiseRight[i];}
      // The undamped strings ring from their strikes alone (strike()),
      // heard through their measured pickups like the partials, whatever
      // the Resonance control.
      for(int j=0;j<halo;++j){auto& mode=sympathetic[firstHalo-21+j];const auto& string=model->haloStrings[j];
        const double d=mode.decay/(1+180*mute*mute/sampleRate);
        const double q=mode.q,im=mode.p;
        mode.q=d*(mode.c*q+mode.s*im);mode.p=d*(mode.c*im-mode.s*q);
        if(mode.q<1e-30&&mode.q>-1e-30)mode.q=0;
        if(mode.p<1e-30&&mode.p>-1e-30)mode.p=0;
        // The bank turns the other way to the partials' lanes.
        l+=string.left*mode.q;r+=string.rightRe*mode.q+string.rightIm*mode.p;
      }
      // The pickup's own image at the default width; narrower towards mono.
      const double mid=(l+r)*.5,side=(l-r)*.5*width/.75;
      double outL=mid+side,outR=mid-side;
      // Feed-forward bridge-to-open-string radiation. The reduced core does not
      // claim the reference solver's reciprocal 475-mode soundboard network.
      // No feedback reaches the driven voices, so this response cannot run away.
      double responseL=0,responseR=0;
      for(int note=0;note<firstHalo-21;++note){
        const double openness=this->openness[note];
        auto& mode=sympathetic[note];
        const double d=mode.decay/(1+(1-openness)*60/sampleRate+180*mute*mute/sampleRate);
        const double q=mode.q,im=mode.p;
        mode.q=d*(mode.c*q+mode.s*im);mode.p=d*(mode.c*im-mode.s*q)+(1-mode.decay)*mid*openness;
        if(mode.q<1e-30&&mode.q>-1e-30)mode.q=0;
        if(mode.p<1e-30&&mode.p>-1e-30)mode.p=0;
        const double pan=(note-43.5)/80.*width;
        responseL+=mode.q*(1-pan);responseR+=mode.q*(1+pan);
      }
      outL+=responseL*parameters.resonance*.35;outR+=responseR*parameters.resonance*.35;
      // DC blocker and bounded, memoryless emergency ceiling. Typical single
      // notes remain linear; extreme 128-strike stacks cannot emit NaN/Inf.
      const double hpL=outL-previousL+highpassCoefficient*highpassL,hpR=outR-previousR+highpassCoefficient*highpassR;
      previousL=outL;previousR=outR;highpassL=hpL;highpassR=hpR;
      const double yL=hpL*gain*model->outputScale,yR=hpR*gain*model->outputScale;
      left[i]=static_cast<float>(yL>1?1:yL< -1?-1:yL);
      right[i]=static_cast<float>(yR>1?1:yR< -1?-1:yR);
    }
  }
};

Engine::Engine(double sampleRate):impl(new Impl){
  auto& p=*impl;
  for(const auto& m:models){
    for(int i=0;i<m.anchors[m.anchorCount-1].first+m.anchors[m.anchorCount-1].count;++i)
      for(int j=0;j<lanes;++j)p.partialLanes[m.partialFirst+i][j]=cacheLane(m.partials[i].lanes[j],m.layers);
    for(int i=0;i<m.anchors[m.anchorCount-1].extraFirst+m.anchors[m.anchorCount-1].extraCount;++i)
      p.extraLanes[m.extraFirst+i]=cacheLane(m.extras[i].lane,m.layers);
  }
  p.placeHalo();
  prepare(sampleRate);
}
Engine::~Engine()=default;
void Engine::prepare(double sampleRate){
  auto& p=*impl;p.sampleRate=sampleRate==sampleRate?std::max(8000.,std::min(192000.,sampleRate)):48000.;
  for(int i=0;i<=sineSize;++i)p.sine[i]=std::sin(2*pi*i/sineSize);
  p.smooth=1-std::exp(-1/(.012*p.sampleRate));p.controlSmooth=1-std::exp(-chunk/(.018*p.sampleRate));
  p.highpassCoefficient=std::exp(-2*pi*10/p.sampleRate);
  p.retuneSympathetic();
  p.prepareBody();
  p.prepareNoise();
  reset();
}
void Engine::reset() noexcept {
  auto& p=*impl;for(auto& voice:p.voices){voice.active=false;voice.count=0;}
  for(auto& channel:p.channels)channel=Channel{};
  for(auto& resonator:p.sympathetic){resonator.q=0;resonator.p=0;}
  p.silenceBody();p.silenceNoise();
  p.serial=0;p.frame=0;p.clock=0;p.gain=p.parameters.gain;p.width=p.parameters.width;p.mute=p.parameters.mute;
  p.previousBrightness=p.parameters.brightness;
  p.sleeping=true;
  p.highpassL=p.highpassR=p.previousL=p.previousR=0;
  for(int ch=0;ch<16;++ch)p.capture(ch);
  p.pedalHeld=false;p.pedalEdge(false);
}
void Engine::setParameters(const Parameters& input) noexcept {
  auto& p=*impl;const float oldTune=p.parameters.tuning;
  p.parameters.gain=bounded(input.gain,0,2);p.parameters.brightness=bounded(input.brightness);
  p.parameters.resonance=bounded(input.resonance);p.parameters.width=bounded(input.width);
  // Wrappers combine their 400..480 Hz user range with host master tuning.
  p.parameters.tuning=bounded(input.tuning,300,600);p.parameters.mute=bounded(input.mute);
  p.parameters.sustain=bounded(input.sustain);p.parameters.sostenuto=bounded(input.sostenuto);
  p.parameters.soft=bounded(input.soft);
  const Model& chosen=models[input.piano==Piano::upright?1:0];
  if(p.model!=&chosen)p.choose(chosen);
  for(int ch=0;ch<16;++ch){p.capture(ch);if(oldTune!=p.parameters.tuning)p.retune(ch);}
  if(oldTune!=p.parameters.tuning)p.retuneSympathetic();
  p.pedalEdge();
}
void Engine::noteOn(int note,float velocity,int channel) noexcept {
  const int ch=channelIndex(channel);if(ch<0)return;
  if(!(velocity>0)){noteOff(note,channel);return;}
  const int sw=switchIndex(note);
  if(sw>=0){
    auto& count=impl->channels[ch].keySwitches[sw];
    if(count<std::numeric_limits<std::uint16_t>::max())++count;
    if(sw==1)impl->capture(ch);
    if(sw==2)impl->pedalEdge();
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
    if(sw==2)impl->pedalEdge();
    return;
  }
  if(note<21||note>108)return;
  auto& count=impl->channels[ch].presses[note-21];
  if(count>0&&--count==0)impl->release(note,ch);
}
void Engine::controlChange(int cc,int value,int channel) noexcept {
  const int ch=channelIndex(channel);if(ch<0)return;
  auto& p=*impl;auto& state=p.channels[ch];const float amount=bounded(value/127.f);
  if(cc==1)state.mute=amount;
  else if(cc==64){state.sustain=amount;p.pedalEdge();}
  else if(cc==66){state.sostenuto=amount;p.capture(ch);}
  else if(cc==67)state.soft=amount;
  else if(cc==123){state.presses.fill(0);state.keySwitches.fill(0);p.capture(ch);p.pedalEdge(false);}
  else if(cc==120){
    state.presses.fill(0);state.keySwitches.fill(0);state.captured.fill(false);p.capture(ch);p.pedalEdge(false);
    for(auto& voice:p.voices)if(voice.channel==ch)voice.active=false;
    bool any=false;for(const auto& voice:p.voices)any=any||voice.active;
    if(!any){for(auto& r:p.sympathetic){r.q=0;r.p=0;}p.silenceBody();p.silenceNoise();p.highpassL=p.highpassR=p.previousL=p.previousR=0;}
  }else if(cc==121){
    state.sustain=state.sostenuto=state.soft=state.mute=state.bend=0;
    // Resetting MIDI CC sources is not a new edge on a held panel/switch.
    p.capture(ch);p.pedalEdge(false);
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
  p.clock+=static_cast<std::uint64_t>(frames);
  if(p.sleeping){
    std::fill_n(left,frames,0.f);std::fill_n(right,frames,0.f);
    p.gain=p.parameters.gain;p.width=p.parameters.width;
    p.mute=p.parameters.mute;
    for(auto& channel:p.channels)channel.smoothedMute=std::max(p.parameters.mute,channel.mute);
    return;
  }
  int done=0;
  while(done<frames){
    if(p.frame%chunk==0)p.boundary();
    const int n=std::min(frames-done,static_cast<int>(chunk-p.frame%chunk));
    p.render(left+done,right+done,n);
    done+=n;p.frame+=static_cast<std::uint64_t>(n);
  }
  bool any=p.ringing||p.rising||p.actionRising||p.hissing;
  for(const auto& voice:p.voices)any=any||voice.active;
  if(!any){
    double residue=std::abs(p.highpassL)+std::abs(p.highpassR);
    for(const auto& r:p.sympathetic)residue+=std::abs(r.q)+std::abs(r.p);
    if(residue<1e-14){
      // Chunks restart with the next strike, so a silent engine's output
      // does not depend on how long it has been silent.
      p.sleeping=true;p.frame=0;p.highpassL=p.highpassR=p.previousL=p.previousR=0;
      for(auto& r:p.sympathetic){r.q=0;r.p=0;}
      p.silenceNoise();
    }
  }
}
}
