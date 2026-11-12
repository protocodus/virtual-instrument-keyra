#include "KeyraEngine.h"
#include "MeasuredModalData.h"
#include "MeasuredActionNoise.h"
#include "MeasuredRoom.h"
#include "MeasuredUprightData.h"
#include "ForteOutput.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <limits>
#include <type_traits>

namespace keyra {
namespace {
// The measured pianos whose actions play (MeasuredTypes.h).
enum class Piano {grand,upright};
constexpr int pianoCount=2;
using Mix=std::array<float,pianoCount>;
constexpr Mix only(Piano piano) noexcept {Mix mix{};mix[static_cast<std::size_t>(piano)]=1;return mix;}
struct Build {
  Mix soundboard=only(Piano::grand);
  Mix action=only(Piano::grand);
};
constexpr Build measuredBuild(Piano piano) noexcept {return {only(piano),only(piano)};}
struct ActionParameters {
  float gain=.7f, width=.75f;
  float mute=0.f, sustain=0.f, sostenuto=0.f, soft=0.f;
  float mechanics=defaultMechanicsGain;
  float room=1.f;
  Build build{};
};
constexpr double pi=3.14159265358979323846;
// The action's rings and noise bursts are advanced every `chunk` samples:
// each ring's exact double-precision state is carried from chunk to chunk
// and its float lanes only ever run one chunk from it.
constexpr int chunk=32;
constexpr int lanes=4; // body modes to a vector
namespace grand=measured::grand;
namespace upright=measured::upright;
// A key landing with its strike knocks the body as an impact through felt,
// whose force grows from zero slope (Hall, JASA 92(1), 1992; Stulov, JASA
// 97(4), 1995): its knock builds up under the body's measured rise smoothed
// by one more pole of this time, as every strike's did in 1.0.0, where a
// bare rise put a click over 8 kHz into it (Docs/decisions.md, 2026-10-29).
constexpr double contactSmoothing=1e-4;
static_assert(grand::bodyRise>2*contactSmoothing&&upright::bodyRise>2*contactSmoothing,
              "the body's rise is slower than the contact's smoothing");

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
// Performance balance, not another acoustic velocity law: below a nominal
// MIDI80 strike, a key's return is no louder than that reference return
// scaled by the requested strike level. This only attenuates; at/above the
// reference it preserves the recorded/sampler balance. If strike calibration
// adds a gain later, its reference-minus-current gain belongs in this bound,
// so boosting a quiet note cannot silently boost its action above the bound.
// Tracking ratios are positive for the engine's finite native coordinates.
double releaseBalanceCapDb(double requestedDb,double referenceDb,double trackingRatio,
                          double referenceTrackingRatio,double strikeCorrectionDb=0,
                          double referenceCorrectionDb=0) noexcept {
  if(requestedDb>=referenceDb)return 0;
  return std::min(0.,requestedDb-referenceDb+referenceCorrectionDb-strikeCorrectionDb
                    +20*std::log10(referenceTrackingRatio/trackingRatio));
}

// A measured piano's action (MeasuredTypes.h): the recorded pitches and
// layers its noises are levelled against, the body modes its knocks ring,
// the knocks and clicks themselves and how loud they play against the
// notes, the scale of its levels and how its soft pedal works (unaCorda: the
// hammers shift along the strings, as a grand's do, rather than move toward
// them). Tables over the recorded pitches hold a row per pitch; one without
// pedal recordings has no pedal knocks, and one whose release takes hold
// their strings has no clicks above the body modes (MeasuredActionNoise.h).
struct Model {
  int layers;const float *layerVelocity,*layerLevelDb;
  const measured::Anchor* anchors;int anchorCount;
  const measured::BodyMode* bodyModes;int bodyModeCount;float bodyRise;
  const measured::ActionKnock *releaseKnocks,*pedalDown,*pedalUp;float actionRise,actionDecay;
  const measured::ActionNoise *releaseNoise,*pedalUpNoise;
  double releaseDb,releaseTracking,noteTracking,releaseFadeDbPerSecond,pedalDownDb,pedalUpDb,keyDownDb;
  const measured::NoiseBand* noiseBands;
  double outputScale;
  bool unaCorda;
};
constexpr Model models[]{
  {grand::layers,grand::layerVelocity.data(),grand::layerLevelDb.data(),grand::anchors.data(),static_cast<int>(grand::anchors.size()),
   grand::bodyModes.data(),static_cast<int>(grand::bodyModes.size()),grand::bodyRise,
   grand::releaseKnocks.data(),grand::pedalDown.data(),grand::pedalUp.data(),grand::actionRise,grand::actionDecay,
   grand::releaseNoise.data(),grand::pedalUpNoise.data(),
   // The action's noises against the notes. The library's own SFZ
   // (Salamander Grand Piano V3, kinwie's SFZ v2 mapping, Data/hammer.txt and
   // Data/pedal.txt) mixes a key let go at -37 dB with 82 % velocity
   // tracking, 2 dB quieter for each second since its strike (rt_decay), and
   // the sustain pedal at -20 dB going down and -19 dB coming up. The notes
   // track velocity at 73 % there (CC99's default), so a release takes the
   // ratio of the two trackings. That balance is a mixing choice, not a
   // measurement (Docs/research/release-recordings-2026-10-27.md), and the
   // owner chose louder keys by ear (Docs/decisions.md, 2026-10-29). The
   // levels here are in the fit's scale, which its rise and decay set.
   -33.65,.82,.73,2,-20,-19,-41.92,
   grand::noiseBands.data(),
   // The scale of the measured grand's levels, as its notes played at -9 VU
   // in 1.0.0: the action's noises keep the level they had there.
   .8022,
   true},
  {upright::layers,upright::layerVelocity.data(),upright::layerLevelDb.data(),upright::anchors.data(),static_cast<int>(upright::anchors.size()),
   upright::bodyModes.data(),static_cast<int>(upright::bodyModes.size()),upright::bodyRise,
   upright::releaseKnocks.data(),nullptr,nullptr,upright::actionRise,upright::actionDecay,upright::releaseNoise.data(),nullptr,
   // The library's Stereo Ribbon preset plays a key let go as the hammer
   // noise recorded with that key at a fixed -14 dB, which played 50 to 72 dB
   // under the notes. Its keys play with the grand's velocity tracking and
   // without its fade, measured as the grand's: a key let go about 36 dB and
   // the key landing about 30 dB under a velocity-80 note of 1.0.0, as when
   // the owner chose them. It has no pedal recordings.
   5.65,.82,0,0,0,0,4.29,
   upright::noiseBands.data(),
   // As the grand's: the measured upright's scale in 1.0.0.
   2.2164,
   false},
};
static_assert(std::size(models)==pianoCount,"a model for every piano");
// The SFZ sounds the pedal at CC64 127 and 0. Here it sounds within .08 of
// either end of its travel, so that a pedal which never quite reaches an end
// still sounds and half-pedalling between does not.
constexpr float pedalClear=.92f,pedalRest=.08f;
// How far down the pedal goes on lifting the dampers, of the travel the
// piano's take (PianoModel.cpp, damperGoal(): clear of the strings at .75).
// The owner found a full pedal's ring too long and chose one whose felt still
// grazes the strings (Docs/decisions.md, 2026-10-30): a velocity-80 chord of
// C3, C4, C5 and C6 let go under it fell 60 dB in 9.5 s on 1.0.0's grand and
// 11.3 s on its upright. Stopped at .7 the concert grand took 9.6 s and the
// upright 10.4 s, where clear of the strings they took 17.4 and 20.5 s. With
// 2.7.0's bridge the grand's chord rang longer at .7 (-58 dB after 12 s
// where it stood at -64); at .695 it takes 11.1 s and the upright 9.2 to
// fall 60 dB under the level at letting go, in 0.1 s windows, where
// 2.6.0's took 10.7 and 10.2.
constexpr float pedalLift=.695f;
// How far a player's strikes of one key at one intended force spread, in
// level. Twelve of the upright library's second takes at train pitches, nine
// of them at its softest layer, are new strikes rather than copies of the
// first (find_repeated_takes.py). They differ from their first as a velocity
// change does, ten of them brighter where louder, by a median 1.04 dB in
// early level, so one strike spreads 1.085 dB about its key's level: the
// median absolute difference over 0.6745 and the square root of two. A spread
// in velocity units instead would follow each layer's level slope, which at
// the upright's loudest layers is twice the measured layers', and so double
// it there. Their pitches differ by a median 0.02 cents, so a strike keeps
// its tuning.
constexpr double touchSpreadDb=1.085;
// Nor do two knocks of the action sound alike. The Salamander grand's key
// returns, each key's recorded once, stand 1.5 dB from their neighbours' in
// level (1.6, 2.1, 3.4 and 3.8 dB in the bands from 50 Hz, 200 Hz, 800 Hz and
// 3.2 kHz up), and their waveforms correlate 0.56 at the best lag: an upper
// bound on what two returns of one key differ by. Each knock draws its level
// (knockSpreadDb), each body mode its own level and phase about the recorded
// ones, each band of the click its level, and the click its rise (a factor's
// logarithm). Two returns of C3, C4 or C6 then differ by 1.4 to 1.8, 1.5 to
// 1.8, 2.3 to 2.9 and 3.3 to 3.8 dB in those bands and 1.4 to 1.9 dB in
// all, and correlate 0.60 to 0.75. The recorded pedal's two takes correlate
// 0.52 going down and 0.36 coming up; these spreads leave the engine's at
// 0.89 and 0.62, more alike than the recorded.
constexpr double knockSpreadDb=1,modeSpreadDb=2,modeSpreadPhase=1,clickSpreadDb=3,clickSpreadRise=.3;
#if (defined(__clang__) || defined(__GNUC__)) && !defined(KEYRA_FORCE_SCALAR)
// Explicit 128-bit lanes also survive the freestanding Rack compiler, whose
// ordinary loops do not auto-vectorize. One vector holds four body modes.
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
// Between two pianos' values of a part at its build: exactly either at its
// ends, linear or in the log domain between them.
double pick(double a,double b,double t) noexcept {return t<=0?a:t>=1?b:mix(a,b,t);}
double pickLog(double a,double b,double t) noexcept {return t<=0?a:t>=1?b:std::exp(mix(std::log(a),std::log(b),t));}
// A part's shares of the pianos, by Piano, summing to 1.
using Shares=std::array<double,pianoCount>;
// A part's weights (0 to 1) as shares of their sum; a part with none plays
// the grand's.
Shares sharesOf(const Mix& mix) noexcept {
  Shares share{};double sum=0;
  for(int p=0;p<pianoCount;++p){share[p]=mix[p];sum+=share[p];}
  if(!(sum>0)){share.fill(0);share[0]=1;return share;}
  for(auto& x:share)x/=sum;
  return share;
}
// The built piano's value from each piano's, get(p), at a part's shares:
// mixed two at a time in the pianos' order, each next one at its share of
// the shares so far, so that two pianos mix as `two` mixes a pair and more
// as its weighted mean. A piano without a share is left out.
template<class Get,class Two> auto fold(const Shares& share,const Get& get,const Two& two) noexcept {
  std::decay_t<decltype(get(0))> value{};double total=0;
  for(int p=0;p<pianoCount;++p){if(!(share[p]>0))continue;
    if(total>0){total+=share[p];value=two(value,get(p),share[p]/total);}
    else{total=share[p];value=get(p);}}
  return value;
}
// A part's shares left to the pianos that have something.
template<class Has> Shares among(Shares share,const Has& has) noexcept {
  for(int p=0;p<pianoCount;++p)if(!has(p))share[p]=0;
  return share;
}
// A stereo pickup (left real; right complex; mean channel power 1).
struct Pickup {double left=1,rightRe=1,rightIm=0;};
// Between two pickups as blendLane blends a lane's: their channels' level
// difference in dB and phase difference along the shorter arc.
Pickup blendPickup(const Pickup& x,const Pickup& y,double t) noexcept {
  if(t<=0)return x;
  if(t>=1)return y;
  const auto ratio=[](const Pickup& p){return std::log(std::max(1e-6,std::hypot(p.rightRe,p.rightIm))/std::max(1e-6,p.left));};
  const double ax=std::atan2(x.rightIm,x.rightRe),ay=std::atan2(y.rightIm,y.rightRe);
  const double g=std::exp(mix(ratio(x),ratio(y),t)),phase=ax+t*std::remainder(ay-ax,2*pi),left=std::sqrt(2/(1+g*g));
  return {left,left*g*std::cos(phase),left*g*std::sin(phase)};
}
struct Complex {double re=0,im=0;};
Complex operator*(Complex a,Complex b) noexcept {return {a.re*b.re-a.im*b.im,a.re*b.im+a.im*b.re};}
Complex power(Complex base,int exponent) noexcept {
  Complex result{1,0};
  while(exponent>0){if(exponent&1)result=result*base;base=base*base;exponent>>=1;}
  return result;
}
// Four of the body's modes, which the action knocks: damped rotations at
// fixed frequencies, each heard through its own pickup (BodyPickup, shared by
// the body's banks of those modes). The float state runs one chunk from the
// exact state.
struct alignas(16) BodyBank {
  V4 re{},im{},c{},s{};
  Complex exact[lanes]{},step[lanes]{},leap[lanes]{};
};
struct alignas(16) BodyPickup {V4 left{},rightRe{},rightIm{};};
constexpr int bodyModes=static_cast<int>(std::max({grand::bodyModes.size(),upright::bodyModes.size()})),
              bodyBanks=(bodyModes+lanes-1)/lanes;
using Body=std::array<BodyBank,bodyBanks>;
void knock(BodyBank& bank,int j,Complex g,int ahead) noexcept {
  setLane(bank.re,j,lane(bank.re,j)+static_cast<float>(g.re));
  setLane(bank.im,j,lane(bank.im,j)+static_cast<float>(g.im));
  const Complex z=ahead==0?g:g*power(bank.step[j],ahead);
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
// Third-octave bands of noise, which the action's clicks sound above the
// body modes. A click's burst holds, per band, its left and right amplitude
// at the next chunk boundary and its decay per chunk, and the same again for
// its rise: a click builds up under the action's rise, as its amplitude less
// the rise's, which falls the faster by the rise's rate.
constexpr int noiseBands=static_cast<int>(grand::noiseBands.size()),maxBursts=32;
static_assert(upright::noiseBands.size()==grand::noiseBands.size(),
              "every piano's noise has the same bands");
// The noise filters are designed once from the grand's centres for every
// build, so every other piano's must be the same.
constexpr bool sameCentres(std::size_t b=0) noexcept {
  return b==grand::noiseBands.size()||(grand::noiseBands[b].hz==upright::noiseBands[b].hz&&sameCentres(b+1));
}
static_assert(sameCentres(),"every piano's noise bands share the grand's centres");
struct Burst {
  double knockLeft[noiseBands]{},knockRight[noiseBands]{},knockStep[noiseBands]{};
  double riseLeft[noiseBands]{},riseRight[noiseBands]{},riseStep[noiseBands]{};
  std::uint64_t serial=0;
  bool active=false;
};
// One band: a band-pass of `noiseSections` sections (b1 = 0, b2 = -b0) on
// each of two independent noise sources, mixed for the measured left/right
// coherence, under gains that ramp across each chunk to the bursts' sum at
// its end. A band whose gains stay under -180 dB through a chunk is left
// unfiltered for it.
constexpr int noiseSections=3;
struct NoiseBand {
  double b0[noiseSections]{},a1[noiseSections]{},a2[noiseSections]{},scale=0,c=1,s=0;
  // A live soundboard change rotates this unit mixing direction over 12 ms.
  // The filters and random sources keep their state. Rotating, rather than
  // independently fading c and s, preserves each band's marginal power.
  double targetC=1,targetS=0,mixStepC=1,mixStepS=0;
  int mixFrames=0;
  double x1[noiseSections][2]{},x2[noiseSections][2]{},y1[noiseSections][2]{},y2[noiseSections][2]{};
  double left=0,right=0,leftStep=0,rightStep=0,leftEnd=0,rightEnd=0;
  bool live=false;
};
// The room each piano's action was recorded in (MeasuredRoom.h), by Piano:
// the floor its recordings hold between the notes' partials, which decays at
// one rate per band whatever the note, uncorrelated between the microphones
// (Docs/research/room-2026-11-09.md). It hears the action's knocks and
// clicks only; the strings' room is the model's own (PianoModel.h).
constexpr measured::Room rooms[]{grand::room,upright::room};
static_assert(sizeof(rooms)/sizeof(rooms[0])==pianoCount,"a room for every piano");
// It plays as a feedback delay network (J.-M. Jot and A. Chaigne, "Digital
// delay networks for designing artificial reverberators", AES 90th
// Convention, 1991): 16 lines of these lengths, each the first prime at or
// above it in samples at the engine's rate, so that no two lines' echoes
// coincide; the 16-point Hadamard matrix mixes their outputs back into them;
// each line's loss is a first-order shelf that takes the room's decay over
// one pass; the input enters the lines with these signs and the left and
// right channels are two of the matrix's orthogonal outputs.
constexpr int roomLines=16;
constexpr double roomDelaySeconds[roomLines]{.0113,.0137,.0161,.0187,.0214,.0244,.0276,.0310,
                                             .0346,.0385,.0426,.0470,.0517,.0566,.0619,.0675};
constexpr double roomSign[roomLines]{1,-1,1,1,-1,1,-1,-1,1,1,-1,1,-1,1,1,-1};
// The lines' samples at the highest rate the engine runs at (prepare()),
// each with room for the primes above its length: no gap between primes
// under 20000 reaches 64.
constexpr int roomCapacity=[]{int n=0;for(double seconds:roomDelaySeconds)n+=static_cast<int>(seconds*192000)+64;return n;}();
// A line's loss: y = b0 x + b1 x[-1] - a1 y[-1].
struct RoomLoss {double b0=1,b1=0,a1=0;};
// The orthonormal 16-point Hadamard transform in place (Sylvester's order).
void hadamard(double* y) noexcept {
  for(int h=1;h<roomLines;h*=2)
    for(int i=0;i<roomLines;i+=2*h)
      for(int j=i;j<i+h;++j){const double a=y[j],b=y[j+h];y[j]=a+b;y[j+h]=a-b;}
  for(int j=0;j<roomLines;++j)y[j]*=.25;
}
struct Channel {
  std::array<std::uint16_t,88> presses{};
  std::array<bool,88> captured{};
  // Each key's latest strike, which sets the noise of its release: where it
  // played on each piano's layers (0..1).
  std::array<std::array<float,88>,pianoCount> velocity{};
  // Captured with the latest strike, including its touch draw. All models
  // are retained because the action build can change before the key returns.
  std::array<std::array<float,88>,pianoCount> releaseCapDb{};
  std::array<std::uint64_t,88> struck{};
  // Momentary C0/C#0/D0 switches have independent ownership from CC/panel.
  std::array<std::uint16_t,3> keySwitches{};
  float sustain=0,sostenuto=0,soft=0,mute=0,bend=0;
  bool sostDown=false;
};

double levelAt(const Model& model,const float* db,double velocity) noexcept {
  // Piecewise linear in dB between the recorded layers, continued with the
  // end segments' slopes (never rising toward softer playing).
  const float* v=model.layerVelocity;
  const int last=model.layers-1;
  if(velocity<=v[0])return db[0]-std::max(0.f,(db[1]-db[0])/(v[1]-v[0]))*(v[0]-velocity);
  if(velocity>=v[last])return db[last]+std::max(0.f,(db[last]-db[last-1])/(v[last]-v[last-1]))*(velocity-v[last]);
  int i=0;while(velocity>v[i+1])++i;
  return mix(db[i],db[i+1],(velocity-v[i])/(v[i+1]-v[i]));
}
// The action's noises follow the velocity response 1.0.0's notes had, the
// one the owner asked for between linear and an S-curve (2026-10-28). A MIDI
// velocity sets a level under the loudest layer, halfway between a straight
// line and smoothstep, and the action plays the layer coordinate where its
// piano's measured layers (layerLevelDb) reach it. Velocity 127 plays each
// piano's loudest layer and 1 the higher of the softest layers' levels, so
// neither plays beyond what it recorded.
constexpr double responseFloorDb=std::max({grand::layerLevelDb[0],upright::layerLevelDb[0]});
double responseDb(double midi) noexcept {
  const double x=(std::max(1.,std::min(127.,midi))-1)/126;
  return responseFloorDb*(1-.5*(x+x*x*(3-2*x)));
}
// The layer coordinate where the piano's measured layers reach a level:
// piecewise linear between them, continued with the end segments' slopes,
// within velocities 1 to 127.
double layerAt(const Model& model,double db) noexcept {
  const float *v=model.layerVelocity,*l=model.layerLevelDb;
  int i=0;while(i<model.layers-2&&db>l[i+1])++i;
  return std::max(1.,std::min(127.,v[i]+(v[i+1]-v[i])*(db-l[i])/(l[i+1]-l[i])));
}
// The recorded pitch above a key, or the last one; the one below is upper - 1.
int upperAnchor(const Model& model,int note) noexcept {
  int upper=1;while(upper<model.anchorCount-1&&model.anchors[upper].note<note)++upper;
  return upper;
}
constexpr int maxAnchors=32;
// One piano's knock of the action on the body: its two recorded pitches'
// knocks on its `count` modes (none for a piano without them), how far
// between them, and its level (dB, in the output's units); and their clicks
// above the modes, per noise band (none where it has no click to play).
struct ActionSide {const measured::ActionKnock *x=nullptr,*y=nullptr;double t=0,gainDb=0;int count=0;
                   const measured::ActionNoise *noiseX=nullptr,*noiseY=nullptr;};
}

struct Engine::Impl {
  std::array<std::array<double,maxAnchors>,pianoCount> actionAnchorGainDb{};
  std::array<measured::BodyMode,bodyModes> bodyMode{};
  int bodyModeCount=0;
  double bodyRise=0,actionRise=0,actionDecay=1;
  // What a knock on a ring puts into `onset` and `contactOnset`, as shares
  // of it, for the sum to build up as 1 - (rise e^(-t/rise) - s e^(-t/s)) /
  // (rise - s), rise the body's, s = contactSmoothing.
  double struckOnset=0,struckContact=0;
  std::array<double,noiseBands> coherence{};
  // Each part's shares of the pianos (setParameters), all the grand's until set.
  struct {Shares soundboard=sharesOf({}),action=sharesOf({});} share;
  std::array<Channel,16> channels{};
  std::array<double,chunk> dryLeft{},dryRight{};
  std::array<V4,chunk> mixLeft{},mixRight{};
  // The action's knocks (keys landing and let go, the sustain pedal) ring in
  // `actionRing`, each mode actionDecay times as fast as the measured board
  // rang, and build up by the action's rise, taken from them in
  // `actionOnset`, as they were measured. A key landing with its strike
  // builds up under the body's rise smoothed by contactSmoothing instead:
  // `onset` holds the board's modes decaying faster by the body's rise and
  // `contactOnset` faster by contactSmoothing, and the knock takes
  // struckOnset and struckContact of itself from them.
  Body onset{},contactOnset{},actionRing{},actionOnset{};
  bool rising=false,actionRinging=false;
  // The body modes' pickups as built (pickupTarget) and as heard (pickup).
  // A piano changed while the body sounds glides them to the new board's
  // over pickupGlide more samples, by pickupStep each sample: set at once,
  // they put a click over 8 kHz 4 dB stronger than the ring's.
  std::array<BodyPickup,bodyBanks> pickup{},pickupTarget{},pickupStep{};
  int pickupGlide=0;
  std::array<Burst,maxBursts> bursts{};
  std::array<NoiseBand,noiseBands> noise{};
  std::array<double,chunk> noiseLeft{},noiseRight{};
  std::uint32_t seed=1;
  bool hissing=false;
  // The room as built (assemble()) and its network at the engine's rate:
  // each line's length, start in `roomLine` and position, its loss as heard
  // and the target and step a piano changed while the room sounds glides it
  // by, and its loss's last input and output. Through a chunk, what the room
  // hears and its two outputs. A room whose lines and input have stayed
  // under 1e-12 for as long as its longest line falls silent and sleeps.
  measured::Room builtRoom{};
  double roomGain=0;
  std::array<int,roomLines> roomLength{},roomStart{},roomAt{};
  std::array<RoomLoss,roomLines> roomLoss{},roomLossTarget{},roomLossStep{};
  std::array<double,roomLines> roomTap{},roomOut{};
  std::array<float,roomCapacity> roomLine{};
  std::array<double,chunk> roomInput{},roomLeft{},roomRight{};
  int roomGlide=0,roomQuiet=0,roomLongest=0;
  bool roomSounding=false;
  ActionParameters parameters{};
  Parameters set{};
  model::Piano piano;
  // Pascals at the microphones to the output's units, for each piano: what
  // puts its typical playing at -9 VU on Reason's meter (Tools/KeyraLevels.cpp).
  static constexpr double pascalScale[model::bodyCount]{.1826,.1701,.1330,.1904};
  std::array<float,chunk> pianoLeft{},pianoRight{};
  double sampleRate=48000,gain=.7,width=.75;
  double smooth=0,highpassCoefficient=0,highpassL=0,highpassR=0,previousL=0,previousR=0;
  std::uint64_t serial=0,frame=0;
  std::uint64_t clock=0; // samples processed since reset, asleep or not
  bool steady=false;
  std::uint32_t touch=1; // the strikes' own draws, apart from the noise's; from 1 on reset
  std::uint32_t chance=1; // the action's knocks' own draws, apart from both; from 1 on reset
  bool sleeping=true;
  bool pedalHeld=false;  // the sustain pedal's dampers off the strings
  // The half-drive response keeps normal playing at the calibrated level.
  // A final stereo envelope protects restored peaks on hard chords.
  ForteOutput output;

  void capture(int ch) noexcept {
    auto& state=channels[ch];
    const bool down=pedalLevel(parameters.sostenuto,state.sostenuto,state.keySwitches[1])>=.5f;
    if(down&&!state.sostDown)
      for(int n=0;n<88;++n)state.captured[n]=state.presses[n]>0;
    if(!down)state.captured.fill(false);
    state.sostDown=down;
  }
  // The share of a part's build from the pianos that `has` something.
  template<class Has> double shareWith(const Shares& part,const Has& has) const noexcept {
    double sum=0;
    for(int p=0;p<pianoCount;++p)if(has(models[p]))sum+=part[p];
    return sum;
  }
  // The action's parts from the measured pianos' by the build's shares: the
  // body's modes (the pianos' lowest with lowest, those only some have from
  // those alone, fading with their share at a knock), the noise's coherence
  // and the room by the soundboard's, the action's rise and decay by the
  // action's. Their sample-rate coefficients follow (prepare()).
  void assemble() noexcept {
    const auto pickupOf=[](const auto& x){return Pickup{x.left,x.rightRe,x.rightIm};};
    bodyModeCount=0;
    for(int p=0;p<pianoCount;++p)if(share.soundboard[p]>0)bodyModeCount=std::max(bodyModeCount,models[p].bodyModeCount);
    for(int k=0;k<bodyModeCount;++k){
      const Shares w=among(share.soundboard,[&](int p){return models[p].bodyModeCount>k;});
      const auto at=[&](int p)->const measured::BodyMode&{return models[p].bodyModes[k];};
      int pianos=0,first=0;
      for(int p=pianoCount-1;p>=0;--p)if(w[p]>0){first=p;++pianos;}
      if(pianos==1){bodyMode[k]=at(first);continue;}
      auto& z=bodyMode[k];
      z.hz=static_cast<float>(fold(w,[&](int p){return static_cast<double>(at(p).hz);},pickLog));
      z.rate=static_cast<float>(fold(w,[&](int p){return static_cast<double>(at(p).rate);},pickLog));
      const Pickup p=fold(w,[&](int q){return pickupOf(at(q));},blendPickup);
      z.left=static_cast<float>(p.left);z.rightRe=static_cast<float>(p.rightRe);z.rightIm=static_cast<float>(p.rightIm);
    }
    bodyRise=fold(share.soundboard,[&](int p){return static_cast<double>(models[p].bodyRise);},pickLog);
    actionRise=fold(share.action,[&](int p){return static_cast<double>(models[p].actionRise);},pickLog);
    actionDecay=fold(share.action,[&](int p){return static_cast<double>(models[p].actionDecay);},pickLog);
    const auto room=[&](float measured::Room::* x){
      return static_cast<float>(fold(share.soundboard,[&](int p){return static_cast<double>(rooms[p].*x);},pickLog));};
    builtRoom={room(&measured::Room::lowRate),room(&measured::Room::highRate),room(&measured::Room::crossover),room(&measured::Room::gain)};
    struckOnset=-bodyRise/(bodyRise-contactSmoothing);struckContact=contactSmoothing/(bodyRise-contactSmoothing);
    for(int k=0;k<noiseBands;++k)
      coherence[k]=fold(share.soundboard,[&](int p){return static_cast<double>(models[p].noiseBands[k].coherence);},pick);
  }
  float sharedSustain(float panel) const noexcept {
    float sustain=panel;
    for(const auto& channel:channels)
      sustain=std::max(sustain,pedalLevel(panel,channel.sustain,channel.keySwitches[2]));
    return sustain;
  }
  void wake() noexcept {sleeping=false;}
  void prepareBody(bool glide=false) noexcept {
    // Each onset's decay per sample beyond its ring's: the body's rise, the
    // action's and the contact's smoothing.
    const double settle[3]={std::exp(-1/(bodyRise*sampleRate)),std::exp(-1/(actionRise*sampleRate)),
                            std::exp(-1/(contactSmoothing*sampleRate))};
    // A mode the build no longer has fades over 5 ms as its pickup glides
    // away, rather than stopping at once; none other ever sounds.
    const double gone=std::exp(-1/(.005*sampleRate));
    for(int m=0;m<bodyBanks*lanes;++m){
      const int k=m/lanes,j=m%lanes;
      const bool real=m<bodyModeCount;const auto& mode=bodyMode[real?m:0];
      const double d=real?std::exp(-mode.rate/sampleRate):gone,w=2*pi*mode.hz/sampleRate;
      const double a=real?std::exp(-mode.rate*actionDecay/sampleRate):gone;
      const Complex step{d*std::cos(w),d*std::sin(w)},actionStep{a*std::cos(w),a*std::sin(w)};
      BodyBank* banks[4]={&onset[k],&actionOnset[k],&contactOnset[k],&actionRing[k]};
      for(int b=0;b<4;++b){auto* bank=banks[b];
        const Complex& from=b==1?actionStep:step;
        const Complex s=b==3?actionStep:Complex{from.re*settle[b],from.im*settle[b]};
        bank->step[j]=s;bank->leap[j]=power(s,chunk);
        setLane(bank->c,j,static_cast<float>(s.re));setLane(bank->s,j,static_cast<float>(s.im));
      }
      auto& target=pickupTarget[k];
      setLane(target.left,j,real?mode.left:0.f);
      setLane(target.rightRe,j,real?mode.rightRe:0.f);setLane(target.rightIm,j,real?mode.rightIm:0.f);
    }
    pickupGlide=glide?static_cast<int>(std::lround(.01*sampleRate)):0;
    if(pickupGlide==0)pickup=pickupTarget;
    else{const V4 per=splat(1.f/static_cast<float>(pickupGlide));
      for(int k=0;k<bodyBanks;++k){const auto &from=pickup[k],&to=pickupTarget[k];
        pickupStep[k]={(to.left-from.left)*per,(to.rightRe-from.rightRe)*per,(to.rightIm-from.rightIm)*per};}}
  }
  // The power response at w (rad/sample) of one section, b0 (1 - z^-2) over
  // 1 + a1 z^-1 + a2 z^-2.
  static double sectionPower(double b0,double a1,double a2,double w) noexcept {
    const double re=1+a1*std::cos(w)+a2*std::cos(2*w),im=a1*std::sin(w)+a2*std::sin(2*w);
    return b0*b0*(2-2*std::cos(2*w))/(re*re+im*im);
  }
  static void snapNoiseMix(NoiseBand& band) noexcept {
    band.c=band.targetC;band.s=band.targetS;band.mixStepC=1;band.mixStepS=0;band.mixFrames=0;
  }
  void snapNoiseMixes() noexcept {for(auto& band:noise)snapNoiseMix(band);}
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
      auto& band=noise[b];
      const double theta=std::acos(bounded(static_cast<float>(coherence[b])))/2;
      const double targetC=std::cos(theta),targetS=std::sin(theta);
      const bool changed=targetC!=band.targetC||targetS!=band.targetS;
      band.targetC=targetC;band.targetS=targetS;
      if(sleeping||!hissing||!band.live)snapNoiseMix(band);
      else if(changed){
        // atan2 starts an interrupted change from the direction actually
        // heard. Trigonometry is confined to this control update; the audio
        // loop uses one precomputed unit rotation and snaps exactly at its
        // finite endpoint.
        band.mixFrames=std::max(1,static_cast<int>(std::lround(.012*sampleRate)));
        const double step=(theta-std::atan2(band.s,band.c))/band.mixFrames;
        band.mixStepC=std::cos(step);band.mixStepS=std::sin(step);
      }
      const double hz=grand::noiseBands[b].hz;
      if(hz*std::pow(2.,1/6.)>.45*sampleRate)continue;
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
      band.scale=1;
    }
    // The bands share their scales among themselves, as they were fitted.
    for(int b=0;b<noiseBands;++b){auto& band=noise[b];if(band.scale==0)continue;
      const double w=2*pi*grand::noiseBands[b].hz/sampleRate;double overlap=0;
      for(const auto& other:noise){if(other.scale==0)continue;
        double power=1;
        for(int j=0;j<noiseSections;++j)power*=sectionPower(other.b0[j],other.a1[j],other.a2[j],w);
        overlap+=power;}
      band.scale=std::sqrt(3*sampleRate/2/overlap);
    }
  }
  // A band's filters start from rest after a silence, so the first click
  // after one takes the filters' response time to reach its density, as the
  // clicks were fitted.
  void silenceNoise() noexcept {
    for(auto& burst:bursts)burst.active=false;
    for(auto& band:noise){
      for(int j=0;j<noiseSections;++j)for(int k=0;k<2;++k)band.x1[j][k]=band.x2[j][k]=band.y1[j][k]=band.y2[j][k]=0;
      band.left=band.right=band.leftStep=band.rightStep=band.leftEnd=band.rightEnd=0;band.live=false;
      snapNoiseMix(band);
    }
    seed=1;hissing=false;
  }
  Burst& claimBurst() noexcept {
    Burst* chosen=&bursts[0];
    for(auto& burst:bursts){if(!burst.active)return burst;if(burst.serial<chosen->serial)chosen=&burst;}
    return *chosen;
  }
  // At a chunk boundary: each band ramps from where the last chunk ended to
  // the bursts' sum at this chunk's end; below -180 dB a burst ends. A click
  // still rising lives by what it will sound, its rise counted with it.
  void advanceNoise() noexcept {
    double target[2][noiseBands]{};bool any=false;
    for(auto& burst:bursts)if(burst.active){double energy=0;
      for(int b=0;b<noiseBands;++b){
        burst.knockLeft[b]*=burst.knockStep[b];burst.knockRight[b]*=burst.knockStep[b];
        burst.riseLeft[b]*=burst.riseStep[b];burst.riseRight[b]*=burst.riseStep[b];
        if(burst.knockLeft[b]<1e-9&&burst.knockRight[b]<1e-9)
          burst.knockLeft[b]=burst.knockRight[b]=burst.riseLeft[b]=burst.riseRight[b]=0;
        const double kl=burst.knockLeft[b]-burst.riseLeft[b],kr=burst.knockRight[b]-burst.riseRight[b];
        target[0][b]+=std::abs(kl);target[1][b]+=std::abs(kr);
        energy+=kl*kl+kr*kr+burst.riseLeft[b]*burst.riseLeft[b]+burst.riseRight[b]*burst.riseRight[b];}
      burst.active=energy>=1e-18;any=any||burst.active;}
    for(int b=0;b<noiseBands;++b){auto& band=noise[b];
      band.left=band.leftEnd;band.right=band.rightEnd;
      band.leftEnd=target[0][b];band.rightEnd=target[1][b];
      band.leftStep=(band.leftEnd-band.left)/chunk;band.rightStep=(band.rightEnd-band.right)/chunk;
      band.live=band.scale!=0&&std::max(std::max(band.left,band.leftEnd),std::max(band.right,band.rightEnd))>=1e-9;
      if(!band.live)snapNoiseMix(band);
      any=any||band.left>0||band.right>0;}
    hissing=any;
  }
  void hiss(int frames) noexcept {
    for(int i=0;i<frames;++i){
      double source[2];
      for(double& x:source){seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;
        x=(static_cast<double>(seed)-2147483648.)*(1./2147483648.);}
      double l=0,r=0;
      for(auto& band:noise)if(band.live){
        if(band.mixFrames>0){
          if(--band.mixFrames==0)snapNoiseMix(band);
          else{const double c=band.c*band.mixStepC-band.s*band.mixStepS;
            band.s=band.s*band.mixStepC+band.c*band.mixStepS;band.c=c;}
        }
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
  // The room's lines at the engine's rate, end to end in `roomLine`.
  void prepareRoomLines() noexcept {
    const auto prime=[](int n){for(int k=2;k*k<=n;++k)if(n%k==0)return false;return n>1;};
    int start=0;roomLongest=0;
    for(int j=0;j<roomLines;++j){
      int n=static_cast<int>(std::lround(roomDelaySeconds[j]*sampleRate));
      while(!prime(n)||std::find(roomLength.begin(),roomLength.begin()+j,n)!=roomLength.begin()+j)++n;
      roomLength[j]=n;roomStart[j]=start;start+=n;roomLongest=std::max(roomLongest,n);
    }
  }
  // Each line's loss for the room: its gain over one pass of its length
  // takes the room's low rate at DC and its high rate at Nyquist, through a
  // bilinear one-pole shelf at the crossover. A room changed while it
  // sounds glides its losses there over 10 ms, as the board's pickups glide.
  void prepareRoom(bool glide=false) noexcept {
    const auto& room=builtRoom;
    const double w=std::tan(pi*std::min(static_cast<double>(room.crossover),.45*sampleRate)/sampleRate),a1=(w-1)/(w+1);
    for(int j=0;j<roomLines;++j){
      const double pass=roomLength[j]/sampleRate;
      const double low=std::pow(10.,-room.lowRate*pass/20),high=std::pow(10.,-room.highRate*pass/20);
      roomLossTarget[j]={.5*(low*(1+a1)+high*(1-a1)),.5*(low*(1+a1)-high*(1-a1)),a1};
    }
    roomGain=room.gain;
    roomGlide=glide&&roomSounding?static_cast<int>(std::lround(.01*sampleRate)):0;
    if(roomGlide==0){roomLoss=roomLossTarget;return;}
    for(int j=0;j<roomLines;++j){const auto &from=roomLoss[j],&to=roomLossTarget[j];
      roomLossStep[j]={(to.b0-from.b0)/roomGlide,(to.b1-from.b1)/roomGlide,(to.a1-from.a1)/roomGlide};}
  }
  void silenceRoom() noexcept {
    std::fill_n(roomLine.begin(),roomStart[roomLines-1]+roomLength[roomLines-1],0.f);
    roomTap.fill(0);roomOut.fill(0);roomAt.fill(0);
    roomQuiet=0;roomSounding=false;
    if(roomGlide>0){roomLoss=roomLossTarget;roomGlide=0;}
  }
  // The room through a chunk, from roomInput into roomLeft and roomRight.
  void playRoom(int frames) noexcept {
    const double in=roomGain*parameters.room*.25;
    for(int i=0;i<frames;++i){
      double y[roomLines],energy=0;
      for(int j=0;j<roomLines;++j){
        const double tap=roomLine[roomStart[j]+roomAt[j]];energy+=tap*tap;
        const auto& loss=roomLoss[j];
        y[j]=loss.b0*tap+loss.b1*roomTap[j]-loss.a1*roomOut[j];
        roomTap[j]=tap;roomOut[j]=y[j];
      }
      hadamard(y);
      roomLeft[i]=y[1];roomRight[i]=y[2];
      const double x=in*roomInput[i];
      for(int j=0;j<roomLines;++j){
        roomLine[roomStart[j]+roomAt[j]]=static_cast<float>(y[j]+roomSign[j]*x);
        if(++roomAt[j]==roomLength[j])roomAt[j]=0;
      }
      if(roomGlide>0){
        if(--roomGlide==0)roomLoss=roomLossTarget;
        else for(int j=0;j<roomLines;++j){auto& loss=roomLoss[j];const auto& step=roomLossStep[j];
          loss.b0+=step.b0;loss.b1+=step.b1;loss.a1+=step.a1;}
      }
      if(energy>=1e-24||x*x>=1e-24)roomQuiet=0;
      else if(++roomQuiet>roomLongest){
        silenceRoom();
        std::fill(roomLeft.begin()+i+1,roomLeft.begin()+frames,0.);std::fill(roomRight.begin()+i+1,roomRight.begin()+frames,0.);
        return;
      }
    }
  }
  void silenceBody() noexcept {
    Body* bodies[4]={&onset,&contactOnset,&actionRing,&actionOnset};
    for(auto* body:bodies)for(auto& bank:*body){bank.re=bank.im=V4{};for(auto& z:bank.exact)z={};}
    rising=actionRinging=false;
  }
  // Called at every chunk boundary: each ring's float lanes restart from its
  // exact state, which advances one chunk, and the noise's bursts advance.
  void boundary() noexcept {
    if(rising){const bool body=advance(onset),contact=advance(contactOnset);rising=body||contact;}
    if(actionRinging){const bool action=advance(actionRing),onset=advance(actionOnset);actionRinging=action||onset;}
    if(hissing)advanceNoise();
  }
  // A body mode's level (dB) and phase on the built piano at a part's shares
  // w, each piano's from get(p, level, phase) for its first counts[p] modes:
  // the powers of the pianos that have the mode mixed by their shares, and
  // the phase of the one with the largest; the mix fading with their share
  // of the build in power where not every piano has it. False where the
  // build plays the mode from none. The pianos' k-th modes are not one mode
  // of one board, and their strongest lie at different k: mixed in dB, a
  // soft top note's knock, nearly all body, sat 4 dB under both pianos at
  // the halfway build.
  template<class Get> static bool betweenPianos(const Shares& w,int k,const int (&counts)[pianoCount],const Get& get,double& level,double& phase) noexcept {
    double power=0,total=0,top=0;int pianos=0;
    for(int p=0;p<pianoCount;++p){if(!(k<counts[p]&&w[p]>0))continue;
      double l=0,ph=0;get(p,l,ph);
      if(pianos++){total+=w[p];power=mix(power,std::pow(10.,l/10),w[p]/total);}
      else{total=w[p];power=std::pow(10.,l/10);level=l;}
      if(w[p]>=top){top=w[p];phase=ph;}
    }
    if(!pianos)return false;
    level=pianos==1?level+10*std::log10(total):10*std::log10(power*total);
    return true;
  }
  // A key struck: the hammer is thrown at its strings (PianoModel.h) and the
  // key lands on the keybed.
  void strike(int note,float velocity,int ch) noexcept {
    wake();
    auto& channel=channels[ch];const int key=note-21;
    if(channel.presses[key]<std::numeric_limits<std::uint16_t>::max())++channel.presses[key];
    const double pedal=pedalLevel(parameters.soft,channel.soft,channel.keySwitches[0]);
    // An upright's soft pedal moves the hammers toward the strings: thrown
    // as hard by the key, a hammer that starts halfway there arrives
    // sqrt(1/2) as fast, and the key lands as softly.
    const double hammer=bounded(velocity)*std::sqrt(1-.5*pedal*shareWith(share.action,[](const Model& m){return !m.unaCorda;}));
    // No two strikes land alike: each moves the blow's level by a draw of
    // spread touchSpreadDb (four uniform draws summed, within 3.5 spreads).
    double draw=0;
    for(int k=0;k<4;++k){touch^=touch<<13;touch^=touch>>17;touch^=touch<<5;draw+=touch*(1./4294967296.)-.5;}
    const double touchDb=steady?0.:touchSpreadDb*std::sqrt(3.)*draw;
    const double requestedDb=responseDb(127*hammer)+touchDb;
    const double releaseReferenceDb=responseDb(127*double(80/127.f));
    // Every piano's, so that a key let go knocks as its strike played on
    // whichever action plays then.
    ActionSide keys[pianoCount];
    for(int p=0;p<pianoCount;++p){const Model& m=models[p];
      const double v=steady?std::max(1.,127.*hammer):layerAt(m,requestedDb);
      channel.velocity[p][key]=static_cast<float>(v/127);
      const double actual=channel.velocity[p][key];
      const double reference=static_cast<float>(layerAt(m,releaseReferenceDb)/127.);
      const double tracking=trackingGain(m.releaseTracking,actual)/trackingGain(m.noteTracking,actual);
      const double referenceTracking=trackingGain(m.releaseTracking,reference)/trackingGain(m.noteTracking,reference);
      channel.releaseCapDb[p][key]=static_cast<float>(steady?0:
        releaseBalanceCapDb(requestedDb,releaseReferenceDb,tracking,referenceTracking));
      const int upper=upperAnchor(m,note);const auto& a=m.anchors[upper-1];const auto& b=m.anchors[upper];
      const double t=std::max(0.,std::min(1.,static_cast<double>(note-a.note)/(b.note-a.note)));
      // The key landing on the keybed knocks the body's modes as its return
      // does, growing with the strike's layer, but as an impact.
      keys[p]={m.releaseKnocks+(upper-1)*m.bodyModeCount,m.releaseKnocks+upper*m.bodyModeCount,t,
               m.keyDownDb+levelAt(m,m.layerLevelDb,v)+20*std::log10(m.outputScale),m.bodyModeCount};
    }
    channel.struck[key]=clock;
    ++serial;
    actionKnock(keys,true);
    syncPiano();
    piano.strike(key,bounded(model::touched(velocity,static_cast<float>(touchDb),set.dynamics),1/127.f,1.f),
                 static_cast<float>(pedal),steady?0:touch);
  }
  // The dampers the keys and the sostenuto hold off their strings, the
  // sustain pedal's travel and the mod wheel's felt, as the channels stand.
  void syncPiano() noexcept {
    float wheel=0;
    for(const auto& channel:channels)wheel=std::max(wheel,channel.mute);
    if(wheel!=wheelMute){wheelMute=wheel;applyControls();}
    for(int key=0;key<88;++key){bool held=false;
      for(const auto& channel:channels)held=held||channel.presses[key]>0||channel.captured[key];
      piano.holdDamper(key,held);}
    piano.setPedal(std::min(pedalLift,sharedSustain(parameters.sustain)));
  }
  void applyControls() noexcept {
    model::Controls c;
    c.body=set.body;c.hammer=set.hammer;c.age=set.age;c.detune=set.detune;c.stretch=set.stretch;c.dynamics=set.dynamics;
    c.lid=set.lid;c.soundboard=set.soundboard;c.sympathetic=set.sympathetic;c.duplex=set.duplex;
    for(int m=0;m<model::micCount;++m)c.mic[m]=set.mic[m];
    c.room=set.room;c.tuning=set.tuning;c.felt=set.felt;c.mute=std::max(set.mute,wheelMute);
    piano.setControls(c);
  }
  float wheelMute=0;
  // A knock of the action on the body: on each piano between its two
  // recorded pitches' (levels mixed, phases from the nearer), between the
  // pianos by the action's build, ringing at the action's decay. It builds
  // up under the action's rise, or, `struck` with a strike, under the
  // body's as the strike's knock does.
  // A uniform draw of unit spread for a knock of the action; a measurement's
  // knocks are the recorded ones.
  double actionDraw() noexcept {
    if(steady)return 0;
    chance^=chance<<13;chance^=chance>>17;chance^=chance<<5;
    return std::sqrt(12.)*(chance*(1./4294967296.)-.5);
  }
  void actionKnock(const ActionSide (&side)[pianoCount],bool struck=false) noexcept {
    if(!(parameters.mechanics>0))return;
    const double knockDb=knockSpreadDb*actionDraw();
    const int ahead=static_cast<int>((chunk-(frame%chunk))%chunk);
    int counts[pianoCount];
    for(int p=0;p<pianoCount;++p)counts[p]=side[p].count;
    bool any=false;
    for(int k=0;k<bodyModeCount;++k){double level=0,phase=0;
      if(!betweenPianos(share.action,k,counts,[&](int p,double& l,double& ph){const auto& x=side[p];
           l=mix(x.x[k].levelDb,x.y[k].levelDb,x.t)+x.gainDb;ph=x.t<.5?x.x[k].phase:x.y[k].phase;},level,phase))continue;
      level+=knockDb+modeSpreadDb*actionDraw();phase+=modeSpreadPhase*actionDraw();
      const double amplitude=parameters.mechanics*std::pow(10.,level/20);
      const Complex g{amplitude*std::cos(phase),amplitude*std::sin(phase)};
      knock(actionRing[k/lanes],k%lanes,g,ahead);
      if(!struck)knock(actionOnset[k/lanes],k%lanes,{-g.re,-g.im},ahead);
      else{knock(onset[k/lanes],k%lanes,{struckOnset*g.re,struckOnset*g.im},ahead);
           knock(contactOnset[k/lanes],k%lanes,{struckContact*g.re,struckContact*g.im},ahead);}
      any=true;
    }
    if(any){wake();actionRinging=true;rising=rising||struck;}
    actionClick(side,knockDb);
  }
  // The click above the body modes, as a burst per noise band under the
  // action's rise, mixed as the knock's modes are: on each piano between its
  // two recorded pitches in dB (density, decay and balance), and between the
  // pianos in power by the action's build, the decays (in the log domain)
  // and the balances weighted by those powers. A band silent at one pitch
  // has no level to mix in dB: the other's fades in power towards it,
  // rather than towards -200 dB.
  void actionClick(const ActionSide (&side)[pianoCount],double knockDb) noexcept {
    Burst* burst=nullptr;double rise=actionRise;
    for(int k=0;k<noiseBands;++k){
      if(noise[k].scale==0)continue;
      double power=0,logRate=0,balance=0;
      for(int p=0;p<pianoCount;++p){const auto& x=side[p];
        if(!(x.noiseX&&share.action[p]>0))continue;
        const auto& a=x.noiseX[k];const auto& b=x.noiseY[k];
        // The table marks a silent band -200 dB.
        const bool hasA=a.densityDb>-180,hasB=b.densityDb>-180;
        if(!hasA&&!hasB)continue;
        double db,w;
        if(hasA&&hasB){db=mix(a.densityDb,b.densityDb,x.t);w=1;}
        else{db=hasA?a.densityDb:b.densityDb;w=hasA?1-x.t:x.t;}
        const double rate=hasA&&hasB?std::exp(mix(std::log(a.rate),std::log(b.rate),x.t)):hasA?a.rate:b.rate;
        const double tilt=hasA&&hasB?mix(a.balanceDb,b.balanceDb,x.t):hasA?a.balanceDb:b.balanceDb;
        w*=share.action[p]*std::pow(10.,(db+x.gainDb)/10);
        power+=w;logRate+=w*std::log(rate);balance+=w*tilt;
      }
      // Under -180 dB the band is silent, as a burst's stages end there.
      if(!(power>=1e-18))continue;
      if(!burst){burst=&claimBurst();*burst=Burst{};rise*=std::exp(clickSpreadRise*actionDraw());}
      const double rate=std::exp(logRate/power),tilt=balance/power;
      const double amplitude=parameters.mechanics*std::sqrt(power)*noise[k].scale*std::pow(10.,(knockDb+clickSpreadDb*actionDraw())/20);
      burst->knockLeft[k]=burst->riseLeft[k]=amplitude*std::pow(10.,-tilt/40);
      burst->knockRight[k]=burst->riseRight[k]=amplitude*std::pow(10.,tilt/40);
      burst->knockStep[k]=std::exp(-rate*chunk/sampleRate);
      burst->riseStep[k]=std::exp(-(rate+1/rise)*chunk/sampleRate);
    }
    if(burst){burst->active=true;burst->serial=serial;hissing=true;wake();}
  }
  // A key let go: its damper falls back onto the strings unless a pedal holds
  // it off them, and the key returns. From F6 up there is no damper to fall,
  // so the key sounds alone; the recordings of those keys are that sound.
  // Each piano's knock follows where its layers played the strike.
  void release(int note,int ch) noexcept {
    const auto& channel=channels[ch];const int key=note-21;
    if(note<89&&(channel.captured[key]||pedalLevel(parameters.sustain,channel.sustain,channel.keySwitches[2])>=pedalClear))return;
    const double held=static_cast<double>(clock-channel.struck[key])/sampleRate;
    ActionSide sides[pianoCount];
    for(int p=0;p<pianoCount;++p){const Model& m=models[p];const double v=channel.velocity[p][key];
      const int upper=upperAnchor(m,note);
      const auto& a=m.anchors[upper-1];const auto& b=m.anchors[upper];
      const auto* x=m.releaseKnocks+(upper-1)*m.bodyModeCount;
      const double t=std::max(0.,std::min(1.,static_cast<double>(note-a.note)/(b.note-a.note)));
      const double muteScale=1.-std::max(parameters.mute,channel.mute);
      const auto* click=m.releaseNoise?m.releaseNoise+(upper-1)*noiseBands:nullptr;
      sides[p]={x,x+m.bodyModeCount,t,
                m.releaseDb+20*std::log10(trackingGain(m.releaseTracking,v)/trackingGain(m.noteTracking,v))
                -m.releaseFadeDbPerSecond*held+20*std::log10(m.outputScale)+channel.releaseCapDb[p][key]
                +muteScale*mix(actionAnchorGainDb[p][upper-1],actionAnchorGainDb[p][upper],t),m.bodyModeCount,
                click,click?click+noiseBands:nullptr};
    }
    actionKnock(sides);
  }
  // Each action's recorded pedal knock, and going up its click. The grand's
  // down take also measures the strings newly freed by its dampers.
  void soundPedal(bool down) noexcept {
    ActionSide sides[pianoCount];
    for(int p=0;p<pianoCount;++p){const Model& m=models[p];const auto* k=down?m.pedalDown:m.pedalUp;
      const auto* click=down?nullptr:m.pedalUpNoise;
      if(k)sides[p]={k,k,0,(down?m.pedalDownDb:m.pedalUpDb)+20*std::log10(m.outputScale),m.bodyModeCount,click,click};}
    actionKnock(sides);
  }
  void pedalEdge(bool audible=true) noexcept {
    const float level=sharedSustain(parameters.sustain);
    const bool held=level>=pedalClear||(pedalHeld&&level>pedalRest);
    if(audible&&held!=pedalHeld)soundPedal(held);
    pedalHeld=held;
  }
  // Each recorded pitch's key return against its neighbours', as 1.0.0
  // evened them: the grand's a third of the way to the mean of the two
  // either side, within 2.5 dB; an upright's that lies more than 1.5 dB under
  // its neighbours' upper third is raised 85 % of the way there, by 16 dB at
  // most. The mute's felt takes its share of it away (release()).
  void initCalibrations() noexcept {
    for(int p=0;p<pianoCount;++p){
      const Model& m=models[p];
      const double scaleDb=20*std::log10(m.outputScale);
      std::array<double,32> rawActDb{};
      for(int a=0;a<m.anchorCount;++a){
        double sum=1e-18;
        for(int k=0;k<m.bodyModeCount;++k)
          sum+=std::pow(10.,.1*m.releaseKnocks[a*m.bodyModeCount+k].levelDb);
        rawActDb[a]=10*std::log10(sum)+m.releaseDb+scaleDb;
      }
      for(int a=0;a<m.anchorCount;++a){
        if(p==0){
          double wSum=0,vSum=0;
          for(int b=std::max(0,a-2);b<=std::min(m.anchorCount-1,a+2);++b){
            const double w=b==a?.4:1.;
            wSum+=w;vSum+=w*rawActDb[b];
          }
          const double avg=wSum>0?vSum/wSum:rawActDb[a];
          actionAnchorGainDb[p][a]=std::max(-2.5,std::min(2.5,.35*(avg-rawActDb[a])));
        }else{
          double vals[7]{};int n=0;
          for(int b=std::max(0,a-3);b<=std::min(m.anchorCount-1,a+3);++b)
            if(b!=a)vals[n++]=rawActDb[b];
          // Not std::sort: GCC 13 cannot bound n by 6 here and fails the Rack's -Werror.
          for(int i=1;i<n;++i)
            for(int j=i;j>0&&vals[j-1]>vals[j];--j)std::swap(vals[j-1],vals[j]);
          const double localRef=n>0?vals[(n*2)/3]:rawActDb[a];
          if(rawActDb[a]<localRef-1.5)
            actionAnchorGainDb[p][a]=std::max(0.,std::min(16.,.85*(localRef-rawActDb[a])));
          else
            actionAnchorGainDb[p][a]=0.;
        }
      }
    }
  }
  // N banks whose pickups hold still are N independent rotations summed into
  // the mix. Run together, their dependent chains overlap, which a lone
  // bank's cannot; each is added in order, so the mix is the same bit for
  // bit as adding them one after another.
  template<int N> void bodyRun(Body& body,const int* banks,int frames) noexcept {
    V4 re[N],im[N],c[N],s[N],l[N],rr[N],ri[N];
    for(int n=0;n<N;++n){const auto& bank=body[banks[n]];const auto& p=pickup[banks[n]];
      re[n]=bank.re;im[n]=bank.im;c[n]=bank.c;s[n]=bank.s;l[n]=p.left;rr[n]=p.rightRe;ri[n]=p.rightIm;}
    for(int i=0;i<frames;++i){
      V4 left=mixLeft[i],right=mixRight[i];
      for(int n=0;n<N;++n){
        left+=l[n]*re[n];right+=rr[n]*re[n]-ri[n]*im[n];
        const V4 next=re[n]*c[n]-im[n]*s[n];im[n]=re[n]*s[n]+im[n]*c[n];re[n]=next;
      }
      mixLeft[i]=left;mixRight[i]=right;
    }
    for(int n=0;n<N;++n){body[banks[n]].re=re[n];body[banks[n]].im=im[n];}
  }
  void ringBody(Body& body,int frames) noexcept {
    // A bank at rest stays at rest and adds nothing: every bank past the
    // built piano's last mode (the upright has 87 modes of the 92 the banks
    // hold), and a body's whole bank once it falls silent.
    int sounding[bodyBanks],count=0;
    for(int k=0;k<bodyBanks;++k){const auto& bank=body[k];
      bool rest=true;for(int j=0;j<lanes;++j)rest=rest&&lane(bank.re,j)==0&&lane(bank.im,j)==0;
      if(!rest)sounding[count++]=k;}
    const int gliding=std::min(frames,pickupGlide);
    int n=0;
    if(gliding==0){
      for(;n+4<=count;n+=4)bodyRun<4>(body,sounding+n,frames);
      if(n+2<=count){bodyRun<2>(body,sounding+n,frames);n+=2;}
    }
    for(;n<count;++n){const int k=sounding[n];auto& bank=body[k];
      V4 re=bank.re,im=bank.im,l=pickup[k].left,rr=pickup[k].rightRe,ri=pickup[k].rightIm;
      const V4 c=bank.c,s=bank.s;
      int i=0;
      for(const auto& step=pickupStep[k];i<gliding;++i){
        l+=step.left;rr+=step.rightRe;ri+=step.rightIm;
        mixLeft[i]+=l*re;mixRight[i]+=rr*re-ri*im;
        const V4 next=re*c-im*s;im=re*s+im*c;re=next;
      }
      for(;i<frames;++i){
        mixLeft[i]+=l*re;mixRight[i]+=rr*re-ri*im;
        const V4 next=re*c-im*s;im=re*s+im*c;re=next;
      }
      bank.re=re;bank.im=im;
    }
  }
  // After every body has rung `frames`: the pickups as far along their glide,
  // and at its end exactly the board's.
  void glidePickups(int frames) noexcept {
    if(pickupGlide==0)return;
    const int n=std::min(frames,pickupGlide);const V4 by=splat(static_cast<float>(n));
    for(int k=0;k<bodyBanks;++k){auto& x=pickup[k];const auto& step=pickupStep[k];
      x.left+=step.left*by;x.rightRe+=step.rightRe*by;x.rightIm+=step.rightIm*by;}
    pickupGlide-=n;
    if(pickupGlide==0)pickup=pickupTarget;
  }
  void render(float* left,float* right,int frames) noexcept {
    const V4 zero{};
    for(int i=0;i<frames;++i){mixLeft[i]=zero;mixRight[i]=zero;}
    if(rising){ringBody(onset,frames);ringBody(contactOnset,frames);}
    if(actionRinging){ringBody(actionRing,frames);ringBody(actionOnset,frames);}
    glidePickups(frames);
    const bool noisy=hissing;
    if(noisy)hiss(frames);
    // The noise source runs on the engine's clock, sounding or not, so that a
    // click's noise does not depend on how long earlier noise sounded.
    else for(int i=0;i<2*frames;++i){seed^=seed<<13;seed^=seed>>17;seed^=seed<<5;}
    // The action's room hears its rings and its noise.
    const bool roomHears=(rising||actionRinging||hissing)&&roomGain*parameters.room>0;
    for(int i=0;i<frames;++i){
      const V4 l4=mixLeft[i],r4=mixRight[i];
      double l=static_cast<double>(lane(l4,0))+lane(l4,1)+lane(l4,2)+lane(l4,3);
      double r=static_cast<double>(lane(r4,0))+lane(r4,1)+lane(r4,2)+lane(r4,3);
      if(noisy){l+=noiseLeft[i];r+=noiseRight[i];}
      dryLeft[i]=l;dryRight[i]=r;
      if(roomHears)roomInput[i]=.5*(l+r);
    }
    const bool roomPlays=roomHears||roomSounding;
    if(roomPlays){
      if(!roomHears)std::fill_n(roomInput.begin(),frames,0.);
      roomSounding=true;playRoom(frames);
    }
    piano.process(pianoLeft.data(),pianoRight.data(),frames);
    const double scale=pascalScale[static_cast<int>(set.body)];
    for(int i=0;i<frames;++i){
      width+=smooth*(parameters.width-width);
      gain+=smooth*(parameters.gain-gain);
      double l=dryLeft[i]+scale*pianoLeft[i],r=dryRight[i]+scale*pianoRight[i];
      if(roomPlays){l+=roomLeft[i];r+=roomRight[i];}
      // The pairs' own image at the default width; narrower towards mono.
      const double mid=(l+r)*.5,side=(l-r)*.5*width/.75;
      const double outL=mid+side,outR=mid-side;
      // Remove DC before measuring stereo peaks and applying the output gain.
      const double hpL=outL-previousL+highpassCoefficient*highpassL,hpR=outR-previousR+highpassCoefficient*highpassR;
      previousL=outL;previousR=outR;highpassL=hpL;highpassR=hpR;
      const auto frame=output.Process(hpL*gain,hpR*gain);
      left[i]=frame[0];right[i]=frame[1];
    }
  }
};

Engine::Engine(double sampleRate):impl(new Impl){
  auto& p=*impl;
  p.initCalibrations();
  p.assemble();
  prepare(sampleRate);
}
Engine::~Engine()=default;
void Engine::prepare(double sampleRate){
  auto& p=*impl;p.sampleRate=sampleRate==sampleRate?std::max(8000.,std::min(192000.,sampleRate)):48000.;
  p.smooth=1-std::exp(-1/(.012*p.sampleRate));
  p.highpassCoefficient=std::exp(-2*pi*10/p.sampleRate);
  p.prepareBody();
  p.prepareNoise();
  p.output.Prepare(p.sampleRate);
  p.prepareRoomLines();p.prepareRoom();
  p.piano.prepare(p.sampleRate);p.applyControls();
  reset();
}
void Engine::reset() noexcept {
  auto& p=*impl;
  for(auto& channel:p.channels)channel=Channel{};
  p.silenceBody();p.silenceNoise();p.silenceRoom();
  // A hard reset starts the current action afresh, even if a live change had
  // not finished gliding its pickups. Live changes still glide.
  p.pickup=p.pickupTarget;p.pickupStep={};p.pickupGlide=0;
  p.serial=0;p.frame=0;p.clock=0;p.touch=1;p.chance=1;p.gain=p.parameters.gain;p.width=p.parameters.width;
  p.sleeping=true;
  p.highpassL=p.highpassR=p.previousL=p.previousR=0;
  p.output.Reset();
  for(int ch=0;ch<16;++ch)p.capture(ch);
  p.pedalHeld=false;p.pedalEdge(false);
  p.piano.reset();p.wheelMute=-1;p.syncPiano();
}
void Engine::setParameters(const Parameters& input) noexcept {
  auto& p=*impl;auto& set=p.set;
  set=input;
  set.gain=bounded(input.gain,0,2);set.width=bounded(input.width);set.room=bounded(input.room);
  // Wrappers combine their 400..480 Hz user range with host master tuning.
  set.tuning=bounded(input.tuning,300,600);set.mute=bounded(input.mute);
  set.sustain=bounded(input.sustain);set.sostenuto=bounded(input.sostenuto);set.soft=bounded(input.soft);
  set.mechanics=bounded(input.mechanics,0,2);
  if(static_cast<int>(set.body)<0||static_cast<int>(set.body)>=model::bodyCount)set.body=model::Body::concertGrand;
  auto& action=p.parameters;
  action.gain=set.gain;action.width=set.width;action.mute=set.mute;
  action.sustain=set.sustain;action.sostenuto=set.sostenuto;action.soft=set.soft;action.mechanics=set.mechanics;
  // The action's room is the one its noises were recorded in: as measured at
  // the Room control's default.
  action.room=2*set.room;
  // The action whose noises play: the measured grand's under every grand,
  // the measured upright's under the upright.
  const Build build=measuredBuild(set.body==model::Body::upright?Piano::upright:Piano::grand);
  if(build.action!=action.build.action){
    action.build=build;
    p.share={sharesOf(build.soundboard),sharesOf(build.action)};
    p.assemble();p.prepareBody(p.rising||p.actionRinging);p.prepareNoise();p.prepareRoom(true);}
  for(int ch=0;ch<16;++ch)p.capture(ch);
  if(p.sleeping)p.snapNoiseMixes();
  p.applyControls();
  p.pedalEdge();
  p.syncPiano();
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
    impl->syncPiano();
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
    impl->syncPiano();
    return;
  }
  if(note<21||note>108)return;
  auto& count=impl->channels[ch].presses[note-21];
  if(count>0&&--count==0){impl->release(note,ch);impl->syncPiano();}
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
    // The strings are one piano's, whichever channel plays them.
    state.presses.fill(0);state.keySwitches.fill(0);state.captured.fill(false);p.capture(ch);p.pedalEdge(false);
    p.piano.reset();p.piano.setBend(state.bend);
    p.silenceBody();p.silenceNoise();p.silenceRoom();
    p.highpassL=p.highpassR=p.previousL=p.previousR=0;p.output.Reset();
  }else if(cc==121){
    state.sustain=state.sostenuto=state.soft=state.mute=state.bend=0;
    // Resetting MIDI CC sources is not a new edge on a held panel/switch.
    p.capture(ch);p.pedalEdge(false);
    p.piano.setBend(0);
  }
  else return;
  p.syncPiano();
}
void Engine::pitchBend(float semitones,int channel) noexcept {
  const int ch=channelIndex(channel);if(ch<0)return;
  // The strings are one piano's: the latest bend moves them all.
  impl->channels[ch].bend=bounded(semitones,-48,48);impl->piano.setBend(impl->channels[ch].bend);
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
int Engine::outputLatencySamples() const noexcept {return impl->output.DelaySamples();}
void Engine::setSteadyStrikesForMeasurement(bool enabled) noexcept {impl->steady=enabled;}
void Engine::process(float* left,float* right,int frames) noexcept {
  if(!left||!right||frames<=0)return;
  auto& p=*impl;
  p.clock+=static_cast<std::uint64_t>(frames);
  if(p.sleeping){
    std::fill_n(left,frames,0.f);std::fill_n(right,frames,0.f);
    p.gain=p.parameters.gain;p.width=p.parameters.width;p.snapNoiseMixes();
    return;
  }
  int done=0;
  while(done<frames){
    if(p.frame%chunk==0)p.boundary();
    const int n=std::min(frames-done,static_cast<int>(chunk-p.frame%chunk));
    p.render(left+done,right+done,n);
    done+=n;p.frame+=static_cast<std::uint64_t>(n);
  }
  if(!(p.rising||p.actionRinging||p.hissing||p.roomSounding||!p.piano.silent())
     &&std::abs(p.highpassL)+std::abs(p.highpassR)<1e-14){
    // Chunks restart with the next strike, so a silent engine's output does
    // not depend on how long it has been silent. The output stage restarts
    // empty too: its look-ahead holds only the last few ms, which are as
    // quiet as the residue.
    p.sleeping=true;p.frame=0;p.highpassL=p.highpassR=p.previousL=p.previousR=0;
    p.silenceNoise();
    p.output.Reset();
  }
}
}
