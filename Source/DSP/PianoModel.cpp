#include "PianoModel.h"
#include "Four.h"
#include "KeyVoicing.h"
#include <algorithm>
#include <cmath>
#include <complex>
#include <cstdint>
#include <cstring>

// The model, block by block (README, How it works):
//
// Strings   Each string is the modes of a stiff, lossy string hinged at both
//           ends: partial k at k f0 sqrt(1 + B k^2) (H. Fletcher, "Normal
//           vibration frequencies of a stiff piano string", JASA 36, 1964),
//           kept as one complex number turning at that frequency. Modal
//           synthesis of the piano is B. Bank and S. Zambon's (B. Bank,
//           S. Zambon and F. Fontana, "A modal-based real-time piano
//           synthesizer", IEEE TASLP 18(4), 2010).
// Hammer    A mass on felt that stiffens as it is compressed and gives way
//           while it is held: F = F0 (x^p - e/t0 * integral of x^p
//           exp(-(t - s)/t0) ds), A. Stulov's hysteretic felt ("Hysteretic
//           model of the grand piano hammer felt", JASA 97, 1995) with his
//           measured hammers, solved against the string's own motion at the
//           strike point while they touch (A. Chaigne and A. Askenfelt,
//           "Numerical simulations of piano strings", JASA 95, 1994).
// Unisons   The strings of a key, each in two polarisations, share the
//           bridge: its admittance couples them, which gives the prompt
//           sound, the aftersound and their beating (G. Weinreich, "Coupled
//           piano strings", JASA 62, 1977).
// Board     An orthotropic plate's modes driven at the bridge, their
//           radiation to each microphone summed over the plate (Rayleigh's
//           integral) with the lid's and the floor's reflections; above the
//           modes, the board moves and radiates near the bridge only
//           (K. Ege, X. Boutillon and M. Rebillat, "Vibroacoustics of the
//           piano soundboard", J. Sound Vib. 332, 2013).
// Resonance Every string whose damper is off, and the duplex scales, are
//           driven by the bridge's motion.
namespace keyra { namespace model {
namespace {
constexpr double pi=3.14159265358979323846;
constexpr double soundSpeed=343,airDensity=1.2;
constexpr double steelYoung=2.0e11,steelDensity=7850;

constexpr int maxK=160;      // partials of a string
constexpr int maxKv=48;      // partials whose unison strings are kept apart
constexpr int maxKh=16;      // partials with a second polarisation
constexpr int maxKl=40;      // partials that drive the longitudinal force
constexpr int planeStart[6]{0,maxK,maxK+maxKv,maxK+2*maxKv,maxK+2*maxKv+maxKh,maxK+2*maxKv+2*maxKh};
constexpr int planeFloats=maxK+2*maxKv+3*maxKh;
constexpr int points=8;      // where the bridge drives the board
constexpr int maxModes=224;  // soundboard modes
constexpr int lidStops=3;
constexpr double lidAngles[lidStops]{0,14*pi/180,38*pi/180};
constexpr int bankPartials=10,duplexModes=2,bankSlots=bankPartials+duplexModes;
constexpr int chunk=32;
constexpr int maxContacts=24;
constexpr int hfTapsPerPoint=6;
constexpr int roomLines=16,roomSpreads=3;

struct Rng {
  std::uint32_t s;
  double uniform() noexcept {s=s*1664525u+1013904223u;return (s>>8)*(1./16777216.);}
  double symmetric() noexcept {return 2*uniform()-1;}
  // Four uniforms summed: unit variance, within 3.5 deviations.
  double normal() noexcept {return (uniform()+uniform()+uniform()+uniform()-2)*1.7320508;}
};
Rng seeded(int a,int b,int c=0) noexcept {
  Rng r{static_cast<std::uint32_t>(2166136261u^(a*16777619u)^(b*374761393u)^(c*668265263u))};
  for(int i=0;i<4;++i)r.uniform();
  return r;
}
double clamp(double x,double lo,double hi) noexcept {return x<lo?lo:x>hi?hi:x;}
float clampf(float x,float lo,float hi) noexcept {return x!=x?lo:x<lo?lo:x>hi?hi:x;}
double mix(double a,double b,double t) noexcept {return a+(b-a)*t;}
// A signed size turned by an angle. std::polar is undefined for a negative
// size, and libc++ (macOS) answers it with NaN.
std::complex<double> turned(double size,double angle) noexcept {return {size*std::cos(angle),size*std::sin(angle)};}
// The sum of a[k] b[k] in eight strands: summed in order, every add waits for
// the one before it, which was most of what a sounding string cost.
inline float dot(const float* a,const float* b,int n) noexcept {
  Four low=Four::all(0),high=Four::all(0);int k=0;
  for(;k+8<=n;k+=8){low+=Four::at(a+k)*Four::at(b+k);high+=Four::at(a+k+4)*Four::at(b+k+4);}
  float rest=0;
  for(;k<n;++k)rest+=a[k]*b[k];
  return ((low[0]+low[1])+(low[2]+low[3]))+((high[0]+high[1])+(high[2]+high[3]))+rest;
}
// cos and sin of an angle from 0 to pi, to 1e-7: every partial sounding is
// retuned through here while the pitch bends. Their series about pi/2, put
// back on the unit circle so that no partial gains or loses by the error.
void turnOf(double angle,float& cosine,float& sine) noexcept {
  const double y=angle-pi/2,q=y*y;
  const double s=y*(1+q*(-1/6.+q*(1/120.+q*(-1/5040.+q*(1/362880.+q*(-1/39916800.+q/6227020800.))))));
  const double c=1+q*(-1/2.+q*(1/24.+q*(-1/720.+q*(1/40320.+q*(-1/3628800.+q*(1/479001600.-q/87178291200.))))));
  const double fix=1.5-.5*(s*s+c*c);
  cosine=static_cast<float>(-s*fix);sine=static_cast<float>(c*fix);
}
// A value given at keys C2, C4 and C7 (15, 39 and 75), as Chaigne and
// Askenfelt's three hammers are, carried in straight lines beyond them.
double throughThree(int key,double c2,double c4,double c7) noexcept {
  return key<39?mix(c2,c4,(key-15)/24.):mix(c4,c7,(key-39)/36.);
}

struct Vec {double x,y,z;};
Vec operator-(Vec a,Vec b) noexcept {return {a.x-b.x,a.y-b.y,a.z-b.z};}
double dot(Vec a,Vec b) noexcept {return a.x*b.x+a.y*b.y+a.z*b.z;}
double norm(Vec a) noexcept {return std::sqrt(dot(a,a));}
Vec unit(Vec a) noexcept {const double n=norm(a);return {a.x/n,a.y/n,a.z/n};}
// A reflecting plane n.p = d, and a point's or a direction's image in it.
struct Plane {Vec n;double d;};
Vec mirror(Vec p,Plane m) noexcept {const double h=2*(dot(m.n,p)-m.d);return {p.x-h*m.n.x,p.y-h*m.n.y,p.z-h*m.n.z};}
Vec mirrorDirection(Vec a,Plane m) noexcept {const double h=2*dot(m.n,a);return {a.x-h*m.n.x,a.y-h*m.n.y,a.z-h*m.n.z};}

// A microphone pair. The board lies in z = 0, its strings on the z > 0 side
// of a grand; `side` is the face of the board the pair hears.
struct MicSpec {
  Vec position[2],axis[2];
  double cardioid;   // 0 omnidirectional, 1 cardioid
  double side;       // 1 the strings' side, -1 through the case
  double shade;      // how much a closed lid keeps from it
  double floor;      // the floor's reflection, signed
  double lid;        // the lid's reflection
  double room;       // how much of the room it hears
  double diffuse;    // the room's first answer against the board's own sound
};
// A piano as built. The dimensions are typical of each kind of piano, not
// one maker's instrument.
struct Design {
  bool upright;
  double bassLength;      // A0's speaking length, m
  int monochords;         // keys with one string
  int trichords;          // the first key with three
  int plain;              // the first key with plain steel strings
  double boardX,boardY;   // the soundboard, m
  double trebleEnd[2],bassEnd[2]; // the bridge's ends, as fractions of the board
  int undamped;           // the first key without a damper
  bool duplex;
  double hammerMass,hammerStiffness; // against the reference hammers
  double dipoleHertz;     // under it the two faces cancel
  double catchSeconds,catchRun; // the action catches the hammer catchSeconds + catchRun / its speed after the blow
  double caseArm;         // m: the moment on the board's edge for each newton of the catch
  // The soundboard as one ribbed plate smeared out: the mass per area of
  // board and ribs, kg/m^2, and the bending stiffnesses along and across
  // the grain with the ribs' counted in, N m.
  double boardMass,boardStiffX,boardStiffY;
  double bridgeMass;      // the bridge at its bass end, kg/m
  double bridgeTaper;     // its treble end's impedance against the bass end's
  double strike;          // where the hammers strike from the bass to C5, as a share of the string
  int bassOctave;         // the lower note's partial the lowest octaves are tuned on (designStrings)
};
// One board, bridge and strike point stand for all five. The plate is chosen
// so that its point impedance, 8 sqrt(D m), is about 2.5e3 kg/s and its modal
// density about 0.05 per Hz for 1.6 m^2, as measured boards' are (Ege et al.
// 2013; N. Giordano, "Mechanical impedance of a piano soundboard", JASA 103,
// 1998). The bridge is maple 33 mm high and 30 wide at the bass end; toward
// the treble it is taken as narrowing to 25 by 25 mm, an assumption, which
// leaves 0.47 of its impedance (as width times height to the 3/2). A maker's
// piano differs from another's in these numbers, and in the hammers and the
// scale above.
constexpr Design designs[bodyCount]{
  // 2.74 m concert grand
  {false,2.01,8,20,20,1.45,1.55,{.86,.10},{.22,.80},69,true,1.,1.,50,.014,.011,.25,19.5,6500,3800,.64,.47,.12,8},
  // 1.86 m parlor grand
  {false,1.40,8,26,26,1.42,1.12,{.86,.11},{.20,.82},69,true,.96,1.1,65,.014,.011,.25,19.5,6500,3800,.64,.47,.12,8},
  // 1.50 m baby grand
  {false,1.14,10,28,28,1.40,.86,{.86,.13},{.18,.84},68,true,.92,1.2,80,.014,.011,.25,19.5,6500,3800,.64,.47,.12,8},
  // 1.25 m upright. Its hammers' stiffness is fitted to eleven forte notes
  // of a recorded upright (MAPS, ENSTDkCl: a Yamaha Disklavier, close pair),
  // whose bass notes hold more above 2 kHz than softer hammers gave.
  {true,1.18,10,30,30,1.40,.95,{.84,.80},{.14,.22},66,false,.9,2.6,90,0,0,.5,19.5,6500,3800,.64,.47,.12,4},
  // 2.0 m studio grand, the size of the grand the benchmark's recordings
  // are of (Salamander: a Yamaha C5). Its bass length and the key where
  // plain steel begins are set against those recordings' inharmonicity
  // below C4, eleven notes at one layer; the rest is typical of the size.
  {false,1.60,8,26,26,1.43,1.22,{.86,.11},{.20,.82},69,true,.97,1.08,62,.014,.011,.25,19.5,6500,3800,.64,.47,.12,8},
};
// The bridge's bending waves are bridgeWave / sqrt(f) m long (maple 33 mm
// high).
constexpr double bridgeWave=16.3;
constexpr double boardLoss=.025;        // loss factor at Soundboard = .5
constexpr double boardEdge=.5;          // edges between hinged (0) and clamped (.5)
constexpr double modesTop=2600;         // Hz: no mode is kept above it
// Hz: above it the board radiates less, 6 dB an octave. At 3 kHz (2.0.0) the
// middle of the keyboard held 5 to 9 dB less in the 4 kHz octave than the
// Salamander grand's forte notes; at 12 kHz the bass held more between its
// partials than they do.
constexpr double radiationCorner=6000;
constexpr double patchRadius=.5;        // m: what radiates about the bridge above the modes
// A note holds two knocks under its fundamental, read on the Salamander
// grand where the fundamental leaves room for them.
// The thump, from 60 to about 350 Hz, is not the blow: it arrives 22 ms
// after the softest notes' onsets and 14.5 after the hardest (the median
// from C#4 to C8 of when what a note holds from 60 to 180 Hz comes within
// 6 dB of its peak), which is when the action catches the hammer coming back
// off the string, taken here as its cause: catchSeconds and catchRun metres
// at the speed the model's hammer comes back with, after it leaves (the
// model's thump then arrives within 4 ms of the recorded one, by the same
// median, at each of seven layers). The hammer's momentum then goes through the key into the keybed, and the case
// hands it, twice smoothed at caseHertz, to the edge of the board the action
// is hung along: a moment of caseArm metres for each newton, keybedShare of
// it on the whole edge alike, where it also heaves the board by rimHeave of
// each mode's mean shape for each metre of the arm, and the rest at the
// key's own place, so that no two keys thump alike. The four are fitted to
// the same notes: from C4 to C8 at three layers, what a key holds from 60 to
// 110 and from 110 to 180 Hz stands within 4 dB of the recording's in the
// median and within 14 on single keys, each against its piano's middle
// notes, and the 40 to 70 Hz the top keys ring on with for a quarter of a
// second within a few dB. (Through 2.3.0 the blow itself knocked every point
// of the bridge alike, which rang one mode, the same on every key, 13 to
// 17 dB over these notes from 110 to 180 Hz. A Steinway's notes thump 8 to
// 10 dB harder than the Salamander's: the level is one piano's.) The
// upright's are set against a recorded upright's notes from C4 up (MAPS,
// ENSTDkCl), a Disklavier, whose thump comes with the blow: caught at once,
// the model's stands within 3.1 dB of it in every band.
constexpr double caseHertz=300,keybedShare=.75,rimHeave=15;
// The knock, from 180 Hz up, comes with the blow, within 5 ms of the onset
// at every layer, and only at the top: from C6 up it is as loud as the note
// itself at a middle layer, at A5 it is not there, and under a bass note
// nothing precedes the strings (15 ms before a note from C1 to D#3 the
// recording holds 20 to 30 dB less from 400 to 1200 Hz than a knock on every
// key gave). The top strings end on the capo d'astro bar, a bar of the
// frame itself, where the others end on agraffes over the pin block: the
// blow's lean on that bar is taken as the cause. From capoFrom up (faded in
// over six keys) it reaches the board's edge at the key's place, above
// knockHertz, as a moment of knockArm metres for each newton. Fitted: from
// A6 to C8 what a key holds from 350 to 700 and from 700 to 1100 Hz stands
// 2 to 4 dB over the recording's in the median and within 8 on single keys;
// from C6 to F#6 it is 2 to 12 dB short. The strings' own pull on the bridge
// is 15 to 25 dB short of it.
constexpr double knockArm=.017,knockHertz=180;
constexpr double whisperTravel=1.9e-6;   // m: see whisper()
// The case sounds too. The pairs hear the board from near it, but what the
// blow's knock shakes in the frame and the case reaches them mostly by the
// room: caseSound of what the knock gives the board's edge goes to the room
// as well, in other signs than the board's sound, so that the two channels
// stay as far apart as they were. Fitted to what the Salamander's notes
// from C6 to C8 leave from 280 to 710 Hz after the knock: 15, 21, 24, 28
// and 36 dB under its peak 60, 100, 150, 200 and 300 ms after it (from
// 400 ms on that recording is at its own floor), where the model without it
// stood 19, 28, 32, 38 and 47 dB under and with it stands 15, 21, 29, 29
// and 39; from 180 to 280 Hz the recording's 14, 19, 22, 27 and 34 against
// 11, 16, 21, 27 and 34. The board at half its loss rang as long, but took
// the bass and the middle twice as long to reach their level (the
// benchmark's rise, 14 to 26 ms). The caught hammer's thump is left out:
// from 60 to 110 Hz the model's stands within 2 dB of the recorded one to
// 200 ms without the room, and with it in the room the bass's partials
// stood 0.2 to 0.3 dB further from the recording's.
constexpr float caseSound=.6f;
// Sixteen lines give an impulse back 1.4 dB louder than the eight of 2.6.0
// did; this keeps the room's level.
constexpr float roomLevel=.85f;
constexpr int capoFrom=60;
// One catch is not the next. Over the sixteen layers of a Salamander key the
// thump stands 2.7 dB (60 to 110 Hz) and 2.6 dB (110 to 180 Hz) off a line
// in the note's level; these spreads of its strength (dB) and of its time (a
// factor's logarithm) give 2.5 and 2.2.
constexpr double catchSpreadDb=2,catchSpreadTime=.2;
constexpr double keyboardWidth=1.23;    // m, centred on the board's edge
// A string struck at an eighth of its length leans seven eighths of the blow
// on its near end, in the iron frame. That lean moves the iron the strings
// end on, and with it the near end of every string whose damper is off:
// frameGive metres a newton, the iron
// under the string ends taken as one damped resonance at frameCorner (a
// Butterworth pair), above which its mass holds it still. Both are fitted:
// to what the Yamaha C3's pedalled takes hold between a note's partials
// from 150 Hz to 2.4 kHz (Tools/benchmark_pedal_wash.py), and to the top
// strings of the Salamander grand, the median of which rings at its own
// pitch 72 to 89 dB under the peak of a forte note struck from C6 to F#7.
// The bridge's own travel left the first 25 dB short in the median and the
// second 40. The two disagree by a few dB: at this give the first is still
// 6 to 8 dB short and the second within 3 dB.
constexpr double frameGive=1.2e-7,frameCorner=500;

// The blow: 5 m/s at full velocity, and under it the velocity to a power:
// 1 at Dynamics 0.5, where the notes' levels stand within 2 dB of the
// Salamander grand's sixteen layers from velocity 31 up and 2.6 dB under
// them below it (2.0.0's speeds, even in dB, were 2.5 dB under in the soft
// and medium layers and 4.4 dB over at the hardest) and within 2 dB of a
// Disklavier's notes (MAPS, ENSTDkCl), and 0.4 to 1.6 from Dynamics 0 to 1:
// 10, 25 and 40 dB between the softest and the hardest blow. `softest`
// keeps the lowest velocity a blow, 0.28 m/s at Dynamics 0.5.
constexpr double softest=.05;
double dynamicsPower(double dynamics) noexcept {return .4+1.2*dynamics;}
double hammerSpeed(double velocity,double dynamics) noexcept {
  return 5*std::pow((velocity+softest)/(1+softest),dynamicsPower(dynamics));
}

MicSpec micSpec(const Design& d,int mic) noexcept {
  const double X=d.boardX,Y=d.boardY;
  const auto toward=[](Vec from,Vec to,double turn){ // the axis toward `to`, turned about the vertical
    const Vec a=unit(to-from);const double c=std::cos(turn),s=std::sin(turn);
    return Vec{a.x*c-a.y*s,a.x*s+a.y*c,a.z};};
  // The close pair's share of the room is set against what the Salamander's
  // treble notes leave from 280 to 710 Hz once the knock under them is over:
  // 24 and 36 dB down 150 and 300 ms after its peak. At 0.03 (2.3.0) the
  // model's stood 41 and 67 dB down, at 0.45 it stood 32 and 47, and with
  // the case's own sound in the room (caseSound) 29 and 39. It is not free:
  // the bass partials stand 0.9 dB further from the recording's than without
  // it. (2.4.0 also read 47 dB at 600 ms, which is that recording's floor.)
  if(!d.upright)switch(mic){
    case micClose: return {{{.30*X,.22,.20},{.72*X,.20,.20}},{{0,0,-1},{0,0,-1}},0,1,0,0,.5,.45,.35};
    case micXY: {const Vec at{X+.8,.45*Y,1.3},aim{.5*X,.4*Y,0};
      return {{at,at},{toward(at,aim,-pi/4),toward(at,aim,pi/4)},1,1,.8,-.3,.6,.18,.7};}
    case micLive: return {{{X+2.3,.5*Y-.6,1.6},{X+2.3,.5*Y+.6,1.6}},{{-1,0,0},{-1,0,0}},0,1,.85,-.3,.6,.45,1.2};
    default: return {{{X+6,.5*Y-1.5,2.5},{X+6,.5*Y+1.5,2.5}},{{-1,0,0},{-1,0,0}},0,1,.9,-.3,.6,1.,2.};
  }
  // An upright: x across, y up, the open back on the z > 0 side.
  switch(mic){
    case micClose: return {{{.30*X,.55*Y,.30},{.70*X,.55*Y,.30}},{{0,0,-1},{0,0,-1}},0,1,0,.3,0,.45,.35};
    case micXY: {const Vec at{.5*X,.6*Y,1.};
      return {{at,at},{unit(Vec{-1,0,-1}),unit(Vec{1,0,-1})},1,1,0,.4,0,.18,.7};}
    case micLive: return {{{.25*X,Y+.45,-.45},{.75*X,Y+.45,-.45}},{{0,-1,0},{0,-1,0}},0,-1,.9,0,0,.4,1.};
    default: return {{{.5*X-1.5,1.3,-4.},{.5*X+1.5,1.3,-4.}},{{0,0,1},{0,0,1}},0,-1,.6,.4,0,1.,2.};
  }
}
Plane floorPlane(const Design& d) noexcept {return d.upright?Plane{{0,1,0},-.25}:Plane{{0,0,1},-.7};}
// A grand's lid, hinged along the bass side .28 m over the board.
Plane lidPlane(int stop) noexcept {
  const double a=lidAngles[stop];return {{-std::sin(a),0,std::cos(a)},.28*std::cos(a)};
}

struct KeyData {
  int strings=1,partials=1;
  bool wound=false;
  double hertz=0,length=0,tension=0,density=0,inharmonicity=0,impedance=0,strike=0;
  double hammerMass=0,hammerStiffness=0,hammerExponent=0,hammerSeconds=0;
  double stretchCents=0;
  double loss1=0,loss2=0,loss3=0; // the string's own losses: loss1 + loss2 f/kHz + loss3 w^2, 1/s
  double damper=0;             // the damper's loss on the strings, 1/s
  double bridge=0;             // where on the bridge, 0..points-1
  double young=0;              // E S of the core, N
  float ratio[maxK]{},shape[maxK]{};
  float couplingRe[maxK]{},couplingIm[maxK]{}; // 2 f0 Z0 Y(w), 1/s
  float detune[3]{},polarisation[3]{},share[3]{},across[3]{},acrossDrive[3]{};
  float stray[3][maxKv]{};     // each string's partial against the ratio, wound strings only
  float duplexRatio[duplexModes]{};
};
struct HfTap {float gain,seconds;};
struct Tables {
  Design design{};
  KeyData keys[keyCount];
  int modes=0;
  double crossover=0;          // Hz, the modes' top
  double besideGain=0,besideLow=0,besideHigh=0; // what radiates beside the modes: its level, and Hz
  double infinite=0;           // the plate's point impedance, kg/s
  float modeHertz[maxModes]{};
  float modeIn[points][maxModes]{};         // shape at the point / (modal mass w)
  float modeHeave[maxModes]{};              // mean shape / (modal mass w)
  float modeEdge[points][maxModes]{};       // slope across the action's edge at a place / (modal mass w)
  // Each mode's radiation to a microphone, as acceleration to pascals:
  // directly, by the floor and by the lid at each stop.
  float direct[micCount][2][2][maxModes]{};
  float floor[micCount][2][2][maxModes]{};
  float lid[lidStops][micCount][2][2][maxModes]{};
  float diffuse[micCount][2][2][maxModes]{};
  // Each pair's level in the mix.
  float micLevel[micCount]{};
  HfTap hfDirect[micCount][2][points]{},hfFloor[micCount][2][points]{},hfLid[lidStops][micCount][2][points]{};
  HfTap hfDiffuse[micCount][2][points][2]{};
  MicSpec mic[micCount]{};
};

// --- the scale -----------------------------------------------------------
void designStrings(Tables& t,int body) noexcept {
  const Design& d=t.design;
  // The plain strings' speaking length doubles a little less than every
  // octave down from C8's 51.5 mm, until the case's length bends it over: no
  // plain string is longer than 0.87 of A0's. The wound strings have a bridge
  // of their own: from the lowest plain string's length at the break to A0's.
  // Set against the strings' stiffness as the recorded pianos' partials give
  // it: the concert grand's inharmonicity stands within 8 % of the
  // Salamander grand's from C3 to F#6 and the upright's within 38 % of the
  // Helsinki upright's plain strings (22 % low to 38 % high). Through 2.4.0
  // the rule bent every string from the bass up, which left the plain
  // strings 10 to 100 % stiffer than the recorded ones: C4's twentieth
  // partial 18 cents and C3's thirtieth 37 cents sharp of the Salamander's.
  const auto ideal=[](int key){return .0515*std::pow(2.,(87-key)/12.*.93);};
  constexpr double bend=8;
  const double longest=.87*d.bassLength;
  const auto plainLength=[&](int key){return std::pow(std::pow(ideal(key),-bend)+std::pow(longest,-bend),-1/bend);};
  for(int i=0;i<keyCount;++i){
    KeyData& k=t.keys[i];
    k.hertz=440*std::pow(2.,(i-48)/12.);
    k.strings=i<d.monochords?1:i<d.trichords?2:3;
    k.wound=i<d.plain;
    double core;
    if(!k.wound){
      // Plain wire from 0.775 mm at the top to 1.125 mm at the break.
      core=(.775+.35*(87-i)/(87.-d.plain))*1e-3;
      k.length=plainLength(i);
      k.density=steelDensity*pi*core*core/4;
      k.tension=4*k.length*k.length*k.hertz*k.hertz*k.density;
      k.inharmonicity=pi*pi*pi*steelYoung*std::pow(core,4)/(64*k.tension*k.length*k.length);
    }else{
      // Copper-wound strings: the winding sets the mass for the tension the
      // scale asks, the steel core the stiffness. The cores and tensions
      // are set with the lengths above. The upright's wound strings stand
      // 6 to 41 % under the Helsinki's stiffness; the concert grand's 14 to
      // 53 % under the Salamander's, a grand 0.7 m shorter.
      const double deep=(d.plain-i)/static_cast<double>(d.plain),top=plainLength(d.plain);
      k.length=top*std::pow(d.bassLength/top,(d.plain-1-i)/(d.plain-1.));
      k.tension=1000+300*deep;
      k.density=k.tension/(4*k.length*k.length*k.hertz*k.hertz);
      core=(1.035+.52*deep)*1e-3;
      k.inharmonicity=pi*pi*pi*steelYoung*std::pow(core,4)/(64*k.tension*k.length*k.length);
    }
    k.young=steelYoung*pi*core*core/4;
    k.impedance=std::sqrt(k.tension*k.density);
    // The hammers are a mass on felt that stiffens as it is compressed,
    // F = K x^p, with a force against the rate of compression beside it (the
    // felt's hysteresis in the limit of a memory far shorter than the
    // contact: A. Stulov, "Hysteretic model of the grand piano hammer felt",
    // JASA 97, 1995). The masses, 4.9, 2.97 and 2.2 g at C2, C4 and C7, and
    // the exponents and stiffnesses the fit starts from (2.3, 2.5 and 3.0;
    // 4.0e8, 4.5e9 and 1.0e12 N/m^p) are the set A. Chaigne and
    // A. Askenfelt give ("Numerical simulations of piano strings II",
    // JASA 95, 1994), quoted from memory. Theirs is the hammer one string
    // meets: three times 2.97 g is a middle hammer's weight, so each string
    // of a unison is struck by that much. A third of it left the Steinway
    // notes' fundamentals 10 to 20 dB under their second partials, the
    // contact being too short. The rest is fitted to the Steinway notes of
    // Tools/compare_model_notes.py, their first 0.3 s in third octaves from
    // the fundamental to 10 kHz and the levels of their four dynamic layers:
    // felt 0.3 as stiff at middle C, softer than their line towards the
    // treble and stiffer towards the bass, the exponent 0.05 higher and
    // falling a little down the bass, and a hysteresis time of 65
    // microseconds at middle C, shorter up the scale, where a longer one
    // lets a soft blow's felt lie on the string and damp it. A fit to the
    // first twenty partials alone left the loud bass 15 to 25 dB short above
    // 2 kHz.
    // Stulov's own measured hammers, as published, left the soft layers'
    // upper partials 20 dB above the recordings'.
    // The felt stiffens faster than that fit's as it is compressed: the
    // exponent is `steeper` higher with the force at `kept` of compression
    // unchanged, fitted to the Salamander grand's sixteen layers under the
    // blow's speeds above (hammerSpeed). With the first fit's exponent its
    // soft layers were brighter than the recordings and its loud ones
    // duller; keeping the force at 0.4 mm instead left the soft bass with
    // more between its partials than the recordings hold.
    constexpr double steeper=1,kept=1e-3;
    const double fromMiddle=i-39;
    k.hammerExponent=throughThree(i,2.3,2.5,3.0)+.047-.0033*std::max(0.,-fromMiddle)+steeper;
    k.hammerMass=d.hammerMass*1e-3*throughThree(i,4.9,2.97,2.2);
    k.hammerStiffness=d.hammerStiffness*.305*std::exp(throughThree(i,std::log(4.0e8),std::log(4.5e9),std::log(1.0e12))
      +2.302585*(fromMiddle>0?-.0092:-.0079)*fromMiddle)*std::pow(kept,-steeper)
      // Above C5 the felt is harder still, by three quarters of a decade at
      // C8: with the slope above, the Salamander's soft notes from A6 up
      // stood 15 to 40 dB under their middle layer at the fundamental where
      // the recording's stand 12 to 25, and the softest were near silent.
      // Set against how loud its keys from F#6 up are beside its middle
      // ones, layer by layer (rms from 50 to 750 ms): within 2 dB at a
      // middle layer, up to 6 loud at the hardest and up to 10 quiet at a
      // soft one (5 to 13 at the softest). Twice as many decades fitted the
      // softest notes and left the others up to 8 dB loud.
      *std::pow(10.,.75*clamp((i-51)/36.,0,1));
    k.hammerSeconds=65e-6*std::exp((fromMiddle>0?-.066:-.0141)*fromMiddle);
    k.strike=clamp(throughThree(i,d.strike,d.strike,.0625),.05,.125);
    // The string's own losses, without the bridge's: the fundamental's,
    // slow at the bottom and faster up the keyboard; what each kHz above the
    // fundamental adds, hardly anything in the long bass strings; and a
    // term with the square of frequency, which only the top partials feel.
    // The first two were fitted, with the bridge as it was to 2.9.0, to how
    // twelve Steinway notes die away over six seconds, whole and at their
    // fundamental (Tools/compare_model_notes.py).
    // The top strings lose more: 0.75 a second more from D7 up, faded in
    // from E6, fitted on that bridge to how the Salamander's C7, F#7 and C8
    // fall in their first second and a half. Neither is fitted again to the
    // bridge and board below.
    k.loss1=.12*std::exp(.013*i)+.75*clamp((i-65)/10.,0,1);
    k.loss2=.72*(.05+.45*clamp((i-12)/40.,0,1));
    k.loss3=1.2e-9;
    // The top keys have no dampers: theirs is what Mute's felt takes.
    k.damper=mix(22,150,std::min(1.,i/static_cast<double>(d.undamped)));
    k.bridge=(87-i)/87.*(points-1);
    Rng r=seeded(body,i,1);
    for(int j=0;j<3;++j){
      k.detune[j]=static_cast<float>(r.normal());
      k.polarisation[j]=static_cast<float>(.6+.8*r.uniform())*(r.uniform()<.5?-1.f:1.f);
      k.share[j]=static_cast<float>(1+.04*r.symmetric());
      // A string also moves sideways, along the soundboard, which the
      // bridge hardly follows: that motion takes a share of the blow, loses
      // little to the board and is the aftersound left once the first, loud
      // decay is over (Weinreich, JASA 62, 1977). Set against how the
      // fundamentals of three reference grands fall in their first 2.7 s,
      // key by key (a commercial modelled piano's American, German and
      // Japanese grands at velocity 80, the owner's renders), on a softer
      // board than this one, and kept on this board, where 2.9.0's sideways
      // motion put the Salamander's notes further off on four layers. From
      // A0 to B6, octave by octave over 0.03 to 2.7 s, the model's
      // fundamentals stand 3.9 dB from the median of the three on average
      // (2.9.0: 4.1). The top octave does not: its fundamentals hold up 14 dB
      // more than theirs.
      k.across[j]=static_cast<float>(.25+.22*r.uniform());
      k.acrossDrive[j]=static_cast<float>(.58*(.5+.5*r.uniform())*(r.uniform()<.5?-1:1));
    }
    // A unison's strings sit about its pitch.
    if(k.strings>1){float mean=0;for(int j=0;j<k.strings;++j)mean+=k.detune[j];
      for(int j=0;j<k.strings;++j)k.detune[j]-=mean/k.strings;}
    else k.detune[0]=0;
    // The length behind the bridge, tuned near the octave and the twelfth.
    k.duplexRatio[0]=static_cast<float>(2*(1+.012*r.symmetric()));
    k.duplexRatio[1]=static_cast<float>(3*(1+.012*r.symmetric()));
    int count=0;
    for(int n=1;n<=maxK;++n){
      const double ratio=n*std::sqrt(1+k.inharmonicity*n*n);
      if(k.hertz*ratio>15000)break;
      // A plain string strays a little from the ideal stiff string, the
      // same for its unison; a wound one strays on its own, below.
      const double shared=r.symmetric();
      k.ratio[count]=static_cast<float>(ratio*(1+(k.wound?0:2e-4)*shared*std::min(1.,n/8.)));
      k.shape[count]=static_cast<float>(std::sin(n*pi*k.strike));
      ++count;
    }
    k.partials=count;
    // A wound string's winding is not even along its length, so each
    // string's partials stray from the ideal stiff string's n sqrt(1 + B n^2)
    // its own way: 1.5 cents for one deviation, from the second partial up.
    // Shared by a unison's strings, as through 2.10.0, a stray left them one
    // ratio apart at every partial, each partial beat at a rate in proportion
    // to its frequency, and a held bass chord swept like a flanger. Set
    // against the Salamander grand's stray from A0 to B2, a median of 1.54
    // cents, where 2.10.0's stood at 0.40 (Tools/measure_partial_stray.py).
    for(int j=0;j<3;++j){Rng q=seeded(body,i,57+j);
      k.stray[j][0]=1;
      for(int n=2;n<=maxKv;++n)k.stray[j][n-1]=static_cast<float>(k.wound?std::pow(2.,1.5*q.normal()/1200):1.);}
  }
  // The tuner's stretch: A4 at pitch, the octave under it and every octave
  // above tuned 4:2 (the upper note's second partial on the lower's fourth),
  // each on the strings' own partials (O. L. Railsback, "Scale temperament as
  // applied to piano tuning", JASA 9, 1938). Down a grand's bass the octave
  // is heard on higher partials, as its tuner hears it: 6:3 at A2 and 8:4
  // from A1 down, passing from one to the next key by key. On the Salamander
  // grand's own stiffness, 8:4 leaves its stretch from A0 to A2 within 1.4
  // cents rms and this ladder within 2.2, where 6:3 throughout, as through
  // 2.12.0, stood 3.6 cents sharp of it (7.6 at A0) and stepped a cent at
  // every A, G#3 being tuned 6:3 beside an A3 tuned 4:2; its octave A0-A1
  // stands 4 cents wide at 8:4 and 4 narrow at 10:5.
  // The upright's bass is tuned 4:2 throughout (Design::bassOctave). The Helsinki
  // upright, whose bass strings are three times as stiff as that grand's, reads
  // so: 4:2 leaves its stretch from C1 to A2 within 2.4 cents rms, 6:3
  // within 9.1 and the grands' ladder, which 2.13.0 gave every piano, 14.9
  // flat of it (30 at C1); its octave C1-C2 stands 0.8 cents narrow at 4:2
  // and 18 at 8:4. No small grand is among the recordings: the baby grand,
  // whose bass strings are as stiff as the upright's here, keeps the
  // grands' ladder until one is heard (README, Known gaps).
  // (Tools/measure_tuner_octaves.py, with --model upright.)
  // A pitch here is the ideal string's, which its stiffness raises to its
  // first partial: that partial is what is tuned.
  double pitch[keyCount];
  const auto partial=[&](int key,int n){return n*std::sqrt(1+t.keys[key].inharmonicity*n*n);};
  const auto octaveUnder=[&](int key,int n){return pitch[key+12]*partial(key+12,n/2)/partial(key,n);};
  pitch[48]=440/partial(48,1);
  pitch[36]=pitch[48]*partial(48,2)/partial(36,4);
  for(int i=37;i<48;++i)pitch[i]=pitch[36]*std::pow(pitch[48]/pitch[36],(i-36)/12.);
  for(int i=49;i<keyCount;++i)pitch[i]=pitch[i-12]*partial(i-12,4)/partial(i,2);
  for(int i=35;i>=0;--i){
    const double steps=std::min((t.design.bassOctave-4)/2.,(36-i)/12.); // octave types past 4:2
    const int lower=4+2*static_cast<int>(steps);
    pitch[i]=steps>=2?octaveUnder(i,8):octaveUnder(i,lower)*std::pow(octaveUnder(i,lower+2)/octaveUnder(i,lower),steps-std::floor(steps));
  }
  for(int i=0;i<keyCount;++i)t.keys[i].stretchCents=1200*std::log2(pitch[i]*partial(i,1)/t.keys[i].hertz);
}

// --- the soundboard --------------------------------------------------------
struct BoardMode {double hertz;int m,n;};
double shapeAt(const Design& d,const BoardMode& mode,double x,double y) noexcept {
  return std::sin(mode.m*pi*x/d.boardX)*std::sin(mode.n*pi*y/d.boardY);
}
void bridgePoint(const Design& d,double at,double& x,double& y) noexcept {
  const double s=at/(points-1);
  x=d.boardX*mix(d.trebleEnd[0],d.bassEnd[0],s);y=d.boardY*mix(d.trebleEnd[1],d.bassEnd[1],std::pow(s,.85));
}
double shade(double amount,double hertz) noexcept {
  return 1-amount+.7*amount/std::sqrt(1+hertz*hertz/(500.*500.));
}
// A bridge is a beam, not a point: it hands a string's force to the board
// along its own length, so a mode takes the mean of its shape there, over half
// the bridge's bending wavelength at the mode's frequency (16.3/sqrt(f) m, a
// maple beam some 33 mm high). Driven at a point, a key's partials stood as the
// board's modes happened to fall under it, 10 to 20 dB apart from the
// recorded key's on single notes (C5, C6 on Salamander). On the four-layer
// benchmark the spread, each key voiced again, brought the unfitted notes'
// partials from 7.51 to 7.25 dB, the level between the channels from 5.93
// to 5.35 and the top octaves' partials from 7.12 to 6.45; half the length
// and twice it both did less (unvoiced, 7.35 and 7.17 against 7.17).
double bridgeShape(const Design& d,const BoardMode& mode,double at) noexcept {
  double x,y,x0,y0,x1,y1;bridgePoint(d,0,x0,y0);bridgePoint(d,points-1,x1,y1);
  const double spacing=std::hypot(x1-x0,y1-y0)/(points-1);
  const double half=.25*bridgeWave/std::sqrt(mode.hertz)/spacing;
  // The wound strings stand on a short bridge of their own, taken as a
  // point: spread along its length it put the upright's bass partials 0.3 dB
  // further from the recorded ones (11.39 against 11.13 dB).
  const double split=(87.5-d.plain)/87*(points-1);
  if(at>split){bridgePoint(d,at,x,y);return shapeAt(d,mode,x,y);}
  double sum=0,weight=0;
  for(int j=-4;j<=4;++j){const double w=.5+.5*std::cos(pi*j/5.);
    bridgePoint(d,clamp(at+half*j/4.,0,split),x,y);sum+=w*shapeAt(d,mode,x,y);weight+=w;}
  return sum/weight;
}
void designBoard(Tables& t,int body){
  const Design& d=t.design;
  BoardMode all[40*40];int found=0;
  Rng r=seeded(body,777);
  for(int m=1;m<=40;++m)for(int n=1;n<=40;++n){
    const double a=(m+boardEdge)/d.boardX,b=(n+boardEdge)/d.boardY;
    const double hertz=pi/2*std::sqrt((d.boardStiffX*a*a*a*a+2*std::sqrt(d.boardStiffX*d.boardStiffY)*a*a*b*b+d.boardStiffY*b*b*b*b)/d.boardMass)
                       *(1+.03*r.symmetric());
    if(hertz<modesTop)all[found++]={hertz,m,n};
  }
  std::sort(all,all+found,[](const BoardMode& a,const BoardMode& b){return a.hertz<b.hertz;});
  t.modes=std::min(found,maxModes);
  t.crossover=t.modes<found?all[t.modes].hertz:modesTop;
  t.infinite=8*std::sqrt(std::sqrt(d.boardStiffX*d.boardStiffY)*d.boardMass);
  const double modalMass=d.boardMass*d.boardX*d.boardY/4;
  for(int k=0;k<t.modes;++k){
    t.modeHertz[k]=static_cast<float>(all[k].hertz);
    for(int p=0;p<points;++p)t.modeIn[p][k]=static_cast<float>(bridgeShape(d,all[k],p)/(modalMass*2*pi*all[k].hertz));
    // The action hangs along the edge by the tuning pins, the bridge's
    // treble end's: eight places under the keyboard, the bass first.
    t.modeHeave[k]=static_cast<float>(((all[k].m&1)&&(all[k].n&1)?4/(pi*pi*all[k].m*all[k].n):0)/(modalMass*2*pi*all[k].hertz));
    const bool far=d.trebleEnd[1]>.5;
    const double slope=(far&&(all[k].n&1)?-1:1)*all[k].n*pi/d.boardY,margin=(1-keyboardWidth/d.boardX)/2;
    for(int p=0;p<points;++p)
      t.modeEdge[p][k]=static_cast<float>(slope*std::sin(all[k].m*pi*mix(margin,1-margin,p/(points-1.)))/(modalMass*2*pi*all[k].hertz));
  }
  // The bridge's admittance at each key, which loads its strings:
  // Y(w) = sum of i w shape^2 / (M (wm^2 - w^2 + 2 i sm w)) over the modes,
  // and the plate's own 1 / (8 sqrt(D m)) above them. The strings' decay is
  // 2 f0 Z0 Re Y each (Weinreich 1977). A mode right under a partial would
  // drain it at once and a node would never: both are held within what a
  // bridge, which spreads the string's force along its length, allows.
  // What the strings meet of an admittance Y at `hertz`, and what the plate's
  // own modes would take of them, both as 2 f0 Z0 Y, 1/s.
  struct Met {std::complex<double> plate,met;};
  const auto meets=[&](int i,const KeyData& key,double hertz,std::complex<double> Y){
    const double above=hertz*hertz/(hertz*hertz+t.crossover*t.crossover);
    Y+=above/t.infinite;
    const double unit=2*key.hertz*key.impedance/t.infinite;
    const std::complex<double> c=2*key.hertz*key.impedance*Y;
    // The plate's single modes would let one key die four times as fast as
    // its neighbour; a bridge and its ribs even that out, so a key keeps
    // within about a third of the infinite plate's value. Under the board's
    // lowest mode there is nothing to even out: the board is a spring there,
    // the bridge moves with it as one, and a string keeps what it has.
    const bool under=hertz<all[0].hertz;
    const std::complex<double> board(clamp(c.real(),under?0:.7*unit,1.5*unit),clamp(c.imag(),-unit,unit));
    // The bridge is a beam between the strings and the board, and a beam's
    // own point impedance, 2 m' c (1 + i) with c its bending waves' speed,
    // stands in the strings' way before the board's does: they meet
    // 1 / (1 / Y + Z beam). It narrows from C5 to the top.
    const double beam=under?0:mix(1,d.bridgeTaper,clamp((i-51)/36.,0,1))*2*d.bridgeMass*bridgeWave*std::sqrt(hertz)/(2*key.hertz*key.impedance);
    return Met{c,board/(1.+board*std::complex<double>(beam,beam))};
  };
  // What the strings lose to the bridge is what the board is given, and the
  // plate's own modes take less than the evened board: between two of the
  // lowest a partial dies as fast as its neighbours and reaches the air a
  // tenth as strong. The rest goes to the board the smeared plate leaves out,
  // which answers at once and about the bridge: it radiates as the bridge's
  // own sound does above the modes (`beside`). restSteps a twelfth of an
  // octave apart from 20 Hz hold that rest for each key, against the
  // infinite plate's share.
  constexpr int restSteps=97;
  const auto restHertz=[](int step){return 20*std::pow(2.,step/12.);};
  const std::unique_ptr<std::complex<double>[][maxModes]> mobility(new std::complex<double>[restSteps][maxModes]);
  for(int step=0;step<restSteps;++step){const double w=2*pi*restHertz(step);
    for(int k=0;k<t.modes;++k){const double wm=2*pi*all[k].hertz,sm=pi*all[k].hertz*boardLoss;
      mobility[step][k]=std::complex<double>(0,w)/(modalMass*std::complex<double>(wm*wm-w*w,2*sm*w));}}
  const std::unique_ptr<double[][restSteps]> rest(new double[keyCount][restSteps]);
  for(int i=0;i<keyCount;++i){KeyData& key=t.keys[i];
    double shape2[maxModes];
    for(int k=0;k<t.modes;++k){const double shape=bridgeShape(d,all[k],key.bridge);shape2[k]=shape*shape;}
    for(int n=0;n<key.partials;++n){
      const double hertz=key.hertz*key.ratio[n],w=2*pi*hertz;
      std::complex<double> Y=0;
      for(int k=0;k<t.modes;++k){const double wm=2*pi*all[k].hertz,sm=pi*all[k].hertz*boardLoss;
        Y+=std::complex<double>(0,w)*shape2[k]/(modalMass*std::complex<double>(wm*wm-w*w,2*sm*w));}
      const Met m=meets(i,key,hertz,Y);
      key.couplingRe[n]=static_cast<float>(m.met.real());key.couplingIm[n]=static_cast<float>(m.met.imag());
    }
    const double unit=2*key.hertz*key.impedance/t.infinite;
    for(int step=0;step<restSteps;++step){const double hertz=restHertz(step);
      std::complex<double> Y=0;
      for(int k=0;k<t.modes;++k)Y+=shape2[k]*mobility[step][k];
      const Met m=meets(i,key,hertz,Y);
      const double below=t.crossover*t.crossover/(hertz*hertz+t.crossover*t.crossover);
      rest[i][step]=below*below*std::max(0.,m.met.real()-m.plate.real())/unit;}
  }
  // Each mode's radiation: Rayleigh's integral p = rho / (2 pi) * integral of
  // the plate's acceleration, delayed by R / c, over R, summed on a grid of
  // three points to the wavelength, with each pair's nearest path taken out
  // of the delay. Under dipoleHertz the board's two faces cancel.
  const Plane ground=floorPlane(d);
  double sx[64],sy[64];
  for(int mic=0;mic<micCount;++mic){
    const MicSpec spec=micSpec(d,mic);t.mic[mic]=spec;
    double nearest=1e9;
    for(int p=0;p<points;++p){double x,y;bridgePoint(d,p,x,y);
      for(int ch=0;ch<2;++ch)nearest=std::min(nearest,norm(spec.position[ch]-Vec{x,y,0}));}
    // The receivers: the microphone, and its images in the floor and the lid.
    struct Receiver {Vec at,axis;bool on;};
    Receiver receivers[2][2+lidStops];
    for(int ch=0;ch<2;++ch){
      receivers[ch][0]={spec.position[ch],spec.axis[ch],true};
      receivers[ch][1]={mirror(spec.position[ch],ground),mirrorDirection(spec.axis[ch],ground),spec.floor!=0};
      for(int stop=0;stop<lidStops;++stop){const Plane lid=lidPlane(stop);
        // Only what is under the lid hears its reflection.
        const bool under=!d.upright&&spec.lid!=0&&dot(lid.n,spec.position[ch])<lid.d;
        receivers[ch][2+stop]={mirror(spec.position[ch],lid),mirrorDirection(spec.axis[ch],lid),under};}
    }
    for(int k=0;k<t.modes;++k){const BoardMode& mode=all[k];
      const int nx=std::min(64,3*mode.m/2+2),ny=std::min(64,3*mode.n/2+2);
      for(int a=0;a<nx;++a)sx[a]=std::sin(mode.m*pi*(a+.5)/nx);
      for(int b=0;b<ny;++b)sy[b]=std::sin(mode.n*pi*(b+.5)/ny);
      const double wave=2*pi*mode.hertz/soundSpeed;
      const double cell=d.boardX*d.boardY/(nx*ny);
      const double w=2*pi*mode.hertz;
      const double scale=-airDensity*w*w*cell/(2*pi)*mode.hertz/std::sqrt(mode.hertz*mode.hertz+d.dipoleHertz*d.dipoleHertz)*spec.side;
      for(int ch=0;ch<2;++ch)for(int image=0;image<2+lidStops;++image){
        const Receiver& rec=receivers[ch][image];
        std::complex<double> sum=0;
        if(rec.on)for(int a=0;a<nx;++a)for(int b=0;b<ny;++b){
          const Vec source{d.boardX*(a+.5)/nx,d.boardY*(b+.5)/ny,0};
          const Vec path=source-rec.at;const double R=norm(path);
          const double heard=1-spec.cardioid+spec.cardioid*.5*(1+dot(path,rec.axis)/R);
          sum+=turned(sx[a]*sy[b]*heard/R,-wave*(R-nearest));
        }
        // p = scale * Im(z C): on Re z its imaginary part, on Im z its real.
        float* out=image==0?t.direct[mic][ch][0]:image==1?t.floor[mic][ch][0]:t.lid[image-2][mic][ch][0];
        out[k]=static_cast<float>(scale*sum.imag());out[maxModes+k]=static_cast<float>(scale*sum.real());
      }
    }
    Rng taps=seeded(body,mic,31);
    for(int ch=0;ch<2;++ch)for(int p=0;p<points;++p){double x,y;bridgePoint(d,p,x,y);
      const Vec source{x,y,0};
      const auto tap=[&](const Receiver& rec)->HfTap{
        if(!rec.on)return {0,0};
        const Vec path=source-rec.at;const double R=norm(path);
        const double heard=1-spec.cardioid+spec.cardioid*.5*(1+dot(path,rec.axis)/R);
        // The patch is not a point: about patchRadius of board radiates.
        return {static_cast<float>(spec.side*heard/std::hypot(R,patchRadius)),static_cast<float>(std::max(0.,R-nearest)/soundSpeed)};};
      t.hfDirect[mic][ch][p]=tap(receivers[ch][0]);
      t.hfFloor[mic][ch][p]=tap(receivers[ch][1]);
      for(int stop=0;stop<lidStops;++stop)t.hfLid[stop][mic][ch][p]=tap(receivers[ch][2+stop]);
      // The ribs and the case scatter what the patch radiates: two later,
      // weaker arrivals, each microphone its own.
      for(int e=0;e<2;++e){const HfTap first=t.hfDirect[mic][ch][p];
        t.hfDiffuse[mic][ch][p][e]={first.gain*static_cast<float>((e?.3:.45)*(taps.uniform()<.5?-1:1)),
                                    first.seconds+static_cast<float>(.0004+.0035*taps.uniform())};}
    }
  }
  // The smeared plate radiates too well where its bending waves pass the
  // speed of sound, which a ribbed board's do not do together, and its few
  // lowest modes stand far out of the rest. Measured boards radiate evenly
  // from their lowest modes to a few kHz (H. Suzuki, "Vibration and sound
  // radiation of a piano soundboard", JASA 80, 1986), so each mode is set
  // against its neighbourhood's level: what an impulse on the bridge puts in
  // each pair, smoothed over a third of an octave, is levelled to `radiated`,
  // which keeps each mode's own strength and what the lid then changes.
    const auto radiated=[&](double hertz){
    return hertz*hertz/(hertz*hertz+d.dipoleHertz*d.dipoleHertz)/(1+hertz*hertz/(radiationCorner*radiationCorner));};
  constexpr int bins=360,octave=48;      // from 20 Hz
  // Each bin's frequency and the smoothing's weights, taken once. `response`
  // asked pow and exp for them 130 000 times a call, half of the half
  // second the five pianos take to design here, and more where the library's
  // pow and exp are slower, as the Rack's are. The same expressions as
  // before, so the same bits.
  double hertzAt[bins],smoothing[bins];
  for(int bin=0;bin<bins;++bin){
    hertzAt[bin]=20*std::pow(2.,bin/static_cast<double>(octave));
    const double octaves=bin/static_cast<double>(octave);smoothing[bin]=std::exp(-octaves*octaves/(2*.3*.3));}
  const auto binHertz=[&](int bin){return hertzAt[bin];};
  double anchor[micCount]{};
  // On the heap, and each call's own: pianos are prepared on any thread.
  const std::unique_ptr<std::complex<double>[][maxModes]> answer(new std::complex<double>[bins][maxModes]);
  for(int bin=0;bin<bins;++bin)for(int k=0;k<t.modes;++k){
    const double wk=2*pi*all[k].hertz;const std::complex<double> s(pi*all[k].hertz*boardLoss,2*pi*binHertz(bin));
    answer[bin][k]=1./(s*s+wk*wk);}
  // What an impulse on the bridge puts in a pair whose share of each mode is
  // c, smoothed over a third of an octave; returns its level from 200 to
  // 800 Hz against `radiated`.
  const auto response=[&](const double (*c)[2][maxModes],double* level){
    double raw[bins]{};
    for(int bin=0;bin<bins&&binHertz(bin)<1.1*t.crossover;++bin){const double w=2*pi*binHertz(bin);
      for(int ch=0;ch<2;++ch){std::complex<double> H[points]{};
        for(int k=0;k<t.modes;++k){const double wk=2*pi*all[k].hertz;
          const std::complex<double> heard=(c[ch][0][k]*std::complex<double>(pi*all[k].hertz*boardLoss,w)+c[ch][1][k]*wk)*answer[bin][k];
          for(int p=0;p<points;++p)H[p]+=static_cast<double>(t.modeIn[p][k])*heard;}
        for(int p=0;p<points;++p)raw[bin]+=std::norm(H[p])/(2*points);}
    }
    double sum=0;int count=0;
    for(int bin=0;bin<bins;++bin){double total=0,weight=0;
      for(int other=0;other<bins&&binHertz(other)<.9*t.crossover;++other){
        const double w=smoothing[other>bin?other-bin:bin-other];total+=w*raw[other];weight+=w;}
      level[bin]=total/std::max(weight,1e-9);
      if(binHertz(bin)>200&&binHertz(bin)<800){sum+=std::log(level[bin]/radiated(binHertz(bin)));++count;}}
    return std::exp(sum/count);
  };
  // What each mode radiates in all: its far field's mean square over the
  // half space, the plate's two directions apart.
  double power[maxModes];
  for(int k=0;k<t.modes;++k){const BoardMode& mode=all[k];
    const int nx=std::min(64,3*mode.m/2+2),ny=std::min(64,3*mode.n/2+2);
    const double wave=2*pi*mode.hertz/soundSpeed;
    for(int a=0;a<nx;++a)sx[a]=std::sin(mode.m*pi*(a+.5)/nx);
    for(int b=0;b<ny;++b)sy[b]=std::sin(mode.n*pi*(b+.5)/ny);
    double total=0;
    constexpr int directions=48;
    for(int i=0;i<directions;++i){
      const double z=(i+.5)/directions,rho=std::sqrt(1-z*z),turn=i*2.39996323;
      const double ux=wave*rho*std::cos(turn),uy=wave*rho*std::sin(turn);
      std::complex<double> across=0,along=0;
      for(int a=0;a<nx;++a)across+=turned(sx[a],ux*d.boardX*(a+.5)/nx);
      for(int b=0;b<ny;++b)along+=turned(sy[b],uy*d.boardY*(b+.5)/ny);
      total+=std::norm(across*along)/directions;}
    const double w=2*pi*mode.hertz;
    power[k]=total*std::pow(w*w*d.boardX*d.boardY/(nx*ny)*mode.hertz,2)/(mode.hertz*mode.hertz+d.dipoleHertz*d.dipoleHertz);
  }
  // What each pair hears of the patch, over the bridge's points.
  double patchMean[micCount]{};
  for(int mic=0;mic<micCount;++mic){const MicSpec& spec=t.mic[mic];
    for(int p=0;p<points;++p)for(int ch=0;ch<2;++ch){
      const auto add=[&](HfTap tap,double g){patchMean[mic]+=g*g*tap.gain*tap.gain/(2*points);};
      add(t.hfDirect[mic][ch][p],1);add(t.hfFloor[mic][ch][p],spec.floor);add(t.hfLid[lidStops-1][mic][ch][p],spec.lid);
      for(int e=0;e<2;++e)add(t.hfDiffuse[mic][ch][p][e],1);}
  }
  double heard[2][2][maxModes]{},direct[2][2][maxModes]{},level[bins]{};
  for(int mic=0;mic<micCount;++mic){const MicSpec& spec=t.mic[mic];
    // The pair hears the board itself, and the room's first answer to all
    // it radiates: every mode by its power, in a phase of the room's.
    Rng room=seeded(body,mic,53);
    for(int ch=0;ch<2;++ch)for(int k=0;k<t.modes;++k){
      for(int part=0;part<2;++part)direct[ch][part][k]=t.direct[mic][ch][part][k]+spec.floor*t.floor[mic][ch][part][k]
                                                       +spec.lid*t.lid[lidStops-1][mic][ch][part][k];
      const double phase=2*pi*room.uniform(),size=std::sqrt(power[k]);
      heard[ch][0][k]=size*std::cos(phase);heard[ch][1][k]=size*std::sin(phase);}
    anchor[mic]=response(direct,level);
    const double diffuse=spec.diffuse*std::sqrt(anchor[mic]/response(heard,level));
    for(int ch=0;ch<2;++ch)for(int part=0;part<2;++part)for(int k=0;k<t.modes;++k){
      t.diffuse[mic][ch][part][k]=static_cast<float>(diffuse*heard[ch][part][k]);
      heard[ch][part][k]=direct[ch][part][k]+t.diffuse[mic][ch][part][k];}
    anchor[mic]*=1+spec.diffuse*spec.diffuse;
    // The smeared plate's modes are exact: every second one is odd across the
    // board's middle and reaches two microphones either side of it exactly
    // out of phase, in the bass too, and no place for a spaced pair avoids
    // them. A real board, ribbed, bridged and shaped like a wing, has no such
    // mode. So each microphone keeps the level it hears of a mode, and the
    // phase between the two is set to what the sound field at a pair gives in
    // the mean, on the side the mode's own fell.
    // The board's own sound reaches the pair from every direction the board
    // subtends: its paths to the two microphones differ by up to `reach`,
    // evenly, and the mean of the cosine over that span is
    // sin(k reach) / (k reach), a wide source's coherence (the van
    // Cittert-Zernike theorem). The room's first answer is a diffuse field,
    // sin(kd) / (kd) between two points d apart (R. K. Cook and others,
    // "Measurement of correlation coefficients in reverberant sound fields",
    // JASA 27, 1072-1077, 1955), times what two patterns share of
    // it, (3 + cos of their angle) / 4 for cardioids. A mode is turned to the
    // angle whose cosine is the two, weighed by what the pair hears of each.
    // So the bass is in phase, a spaced pair opens to a quarter turn where
    // its spacing is half a wavelength (280 Hz for a grand's close pair) and
    // a coincident one stays nearly together.
    // Nothing in it is fitted. Over 150 of the Salamander's notes
    // (Tools/measure_pair_image.py, its protocol at its head) the two
    // channels are 0.79, -0.17, 0.05 and 0.08 alike in the octaves at 125,
    // 250, 500 and 1000 Hz, each within 0.04. The close pair gives 0.78,
    // 0.01, -0.05 and 0.08; the hold to 2.11.0 (no mode more than 70 to 90
    // degrees out of step, the others left as they fell) gave 0.57, 0.30,
    // 0.27 and 0.17.
    const double spacing=norm(spec.position[0]-spec.position[1]);
    double reach=0;
    for(int a=0;a<=16;++a)for(int b=0;b<=16;++b){const Vec source{d.boardX*a/16,d.boardY*b/16,0};
      reach=std::max(reach,std::abs(norm(source-spec.position[0])-norm(source-spec.position[1])));}
    const double omni=1-spec.cardioid/2,figure=spec.cardioid/2;
    const double shared=(omni*omni+figure*figure*dot(spec.axis[0],spec.axis[1])/3)/(omni*omni+figure*figure/3);
    const auto alike=[](double turns){return turns>1e-6?std::sin(turns)/turns:1.;};
    for(int k=0;k<t.modes;++k){
      const double wave=2*pi*all[k].hertz/soundSpeed;
      double own=1,rooms=1;
      for(int ch=0;ch<2;++ch){const auto& room=t.diffuse[mic][ch];
        own*=std::hypot(heard[ch][0][k]-room[0][k],heard[ch][1][k]-room[1][k]);rooms*=std::hypot(room[0][k],room[1][k]);}
      const double cosine=(own*alike(wave*reach)+rooms*shared*alike(wave*spacing))/std::max(own+rooms,1e-300);
      const std::complex<double> l(heard[0][0][k],-heard[0][1][k]),r(heard[1][0][k],-heard[1][1][k]);
      const double apart=std::arg(r*std::conj(l)),held=std::acos(clamp(cosine,-1,1));
      // Half a turn is a change of sign. What is left to turn, a quarter turn
      // at most, is shared evenly between the two microphones: neither is the
      // one that keeps the board's own phases, and no mode is turned more than
      // an eighth of a turn in either.
      const double whole=(apart<0?-held:held)-apart,halves=std::round(whole/pi),least=whole-pi*halves;
      for(int ch=0;ch<2;++ch){
        const double turn=ch?least/2+pi*halves:-least/2,c=std::cos(turn),sn=std::sin(turn);
        const auto rotate=[&](float (*gain)[maxModes]){const float a=gain[0][k],b=gain[1][k];
          gain[0][k]=static_cast<float>(a*c+b*sn);gain[1][k]=static_cast<float>(b*c-a*sn);};
        rotate(t.direct[mic][ch]);rotate(t.floor[mic][ch]);rotate(t.diffuse[mic][ch]);
        for(int stop=0;stop<lidStops;++stop)rotate(t.lid[stop][mic][ch]);
      }
    }
    // The pair's level is set on what it hears with the modes so turned.
    for(int ch=0;ch<2;++ch)for(int part=0;part<2;++part)for(int k=0;k<t.modes;++k)
      heard[ch][part][k]=t.direct[mic][ch][part][k]+spec.floor*t.floor[mic][ch][part][k]
                         +spec.lid*t.lid[lidStops-1][mic][ch][part][k]+t.diffuse[mic][ch][part][k];
    float trim[maxModes];
    for(int k=0;k<t.modes;++k)trim[k]=1;
    for(int pass=0;pass<3;++pass){
      response(heard,level);
      for(int k=0;k<t.modes;++k){
        const double at=clamp(octave*std::log2(all[k].hertz/20),0,bins-1.001);const int bin=static_cast<int>(at);
        const double excess=mix(std::log(level[bin]),std::log(level[bin+1]),at-bin)-std::log(anchor[mic]);
        const double step=clamp(std::sqrt(radiated(all[k].hertz)/std::exp(excess)),.1/trim[k],10/trim[k]);
        trim[k]*=static_cast<float>(step);
        for(int ch=0;ch<2;++ch)for(int part=0;part<2;++part)heard[ch][part][k]*=step;
      }
    }
    for(int k=0;k<t.modes;++k)for(int ch=0;ch<2;++ch)for(int part=0;part<2;++part){
      t.direct[mic][ch][part][k]*=trim[k];t.floor[mic][ch][part][k]*=trim[k];t.diffuse[mic][ch][part][k]*=trim[k];
      for(int stop=0;stop<lidStops;++stop)t.lid[stop][mic][ch][part][k]*=trim[k];}
    t.micLevel[mic]=static_cast<float>(anchor[mic]);
  }
  // Above the modes the board moves and radiates near the bridge only, and
  // the ribs and the case scatter it: each pair hears that at the level its
  // modes leave off.
  for(int mic=0;mic<micCount;++mic){
    const float join=static_cast<float>(std::sqrt(anchor[mic]/patchMean[mic]));
    for(int ch=0;ch<2;++ch)for(int p=0;p<points;++p){
      t.hfDirect[mic][ch][p].gain*=join;t.hfFloor[mic][ch][p].gain*=join;
      for(int stop=0;stop<lidStops;++stop)t.hfLid[stop][mic][ch][p].gain*=join;
      for(int e=0;e<2;++e)t.hfDiffuse[mic][ch][p][e].gain*=join;}
  }
  // Beside the modes the bridge's force radiates through one filter, which
  // waits as a board does: nothing under the lowest mode, then the root of
  // that rest, the keys' mean taken over a third of an octave, times how
  // much louder the pairs hear the modes there than at their top, where the
  // bridge's own sound is joined; and falling from where that is past half
  // its most. (Each partial weighed by its own rest filled the same holes
  // and answered before it was asked: C1 sounded 13 ms before its string's
  // wave had reached the bridge, 35 dB up.)
  {
    double shaped[restSteps],most=0;int last=0;
    constexpr double wide=.33;
    for(int step=0;step<restSteps;++step){double total=0,sum=0;
      for(int other=0;other<restSteps;++other){const double octaves=(other-step)/12.,w=std::exp(-octaves*octaves/(2*wide*wide));
        double mean=0;for(int i=0;i<keyCount;++i)mean+=rest[i][other]/keyCount;
        total+=w*mean;sum+=w;}
      shaped[step]=total/sum*radiated(restHertz(step));most=std::max(most,shaped[step]);}
    for(int step=0;step<restSteps;++step)if(shaped[step]>=.5*most)last=step;
    t.besideLow=all[0].hertz;t.besideHigh=restHertz(last);
    // The two slopes take a little off the most between them.
    double passed=0;
    for(int step=0;step<restSteps;++step){const double low=std::pow(restHertz(step)/t.besideLow,4),high=std::pow(restHertz(step)/t.besideHigh,2);
      passed=std::max(passed,low/(1+low)/(1+high));}
    t.besideGain=std::sqrt(most/passed);
  }
}

// --- what sounds -----------------------------------------------------------
// A key's strings. Plane 0 is the first string's vertical polarisation and,
// for the partials above maxKv, all the strings' moving together; planes 1
// and 2 the other strings' vertical motion, 3 to 5 each string's motion
// along the bridge. Every mode is a complex number z turning by its
// frequency and loss each sample; the string's displacement is Im z.
struct Voice {
  bool active=false,forcing=false;
  int strings=1,partials=0,sounding=0,apart=0,across=0,longitudinal=0;
  int point=0;float pointMix=0;
  float damper=0;            // 0 off the strings, 1 on them
  float appliedDamper=-1;
  float u[6]{};              // each plane's hold on the bridge
  float re[planeFloats]{},im[planeFloats]{};
  float turnRe[planeFloats]{},turnIm[planeFloats]{}; // the step: rotation times loss
  float cosine[planeFloats]{},sine[planeFloats]{};
  float drive[planeFloats]{};   // displacement per newton of hammer force, per sample
  float couplingRe[maxK]{},couplingIm[maxK]{}; // per sample
  float bridge[maxK]{};         // newtons on the bridge per metre
  float open[maxK]{},damped[maxK]{}; // the loss per sample, damper off and on
  float tension[maxK]{};        // the longitudinal force's share
  float force[chunk]{};
  float floor2=0;            // the squared bridge force under which a partial is let go
};
// A hammer against its string, from contact until it has left.
struct Contact {
  bool active=false;
  int key=0,partials=0,age=0;
  double position=0,velocity=0,mass=0,relaxed=0,prompt=0,exponent=0,previous=0,deepest=0;
  double give=0;             // the string's yielding at the hammer within a step, m/N
  double late=1,strength=1;  // this blow's catch against the middle one's: its time and its push
  float re[maxK]{},im[maxK]{},turnRe[maxK]{},turnIm[maxK]{},drive[maxK]{},shape[maxK]{};
};
struct Biquad {
  double b0=1,b1=0,b2=0,a1=0,a2=0,z1=0,z2=0;
  double run(double x) noexcept {const double y=b0*x+z1;z1=b1*x-a1*y+z2;z2=b2*x-a2*y;return y;}
};
}

struct Piano::Impl {
  double sampleRate=48000;
  std::unique_ptr<Tables[]> tables;
  Controls controls{};
  const Tables* table=nullptr;
  float pedal=0,bend=0;
  bool held[keyCount]{};
  bool quiet=true;
  int quietChunks=0;
  int phase=0;               // samples into the chunk
  float loud=0;              // the chunk's peak
  bool retune=false;         // the pitch moved since the last boundary
  float knocks[points]{};    // impulses waiting for the bridge, newton-samples

  Voice voices[keyCount];
  Contact contacts[maxContacts];
  int substeps=2;

  // The open strings and duplex scales: bankSlots modes a key.
  float bankRe[keyCount*bankSlots]{},bankIm[keyCount*bankSlots]{};
  float bankTurnRe[keyCount*bankSlots]{},bankTurnIm[keyCount*bankSlots]{};
  float bankCos[keyCount*bankSlots]{},bankSin[keyCount*bankSlots]{};
  float bankIn[keyCount*bankSlots]{},bankOut[keyCount*bankSlots]{};
  float bankOpen[keyCount*bankSlots]{},bankDamped[keyCount*bankSlots]{};
  float bankEnd[keyCount*bankSlots]{}; // a mode's drive from its string's near end
  float bankFollow[keyCount]{};                    // the pull of a string that only follows that end
  float bankDamper[keyCount]{},bankApplied[keyCount]{};
  float damperOn[keyCount]{};   // each damper's own weight on its strings, 0 off to 1
  bool bankAwake[keyCount]{};float bankEnergy[keyCount]{};
  bool pedalKnown=false;     // setPedal() has said where the pedal stands since reset()
  std::uint32_t lifts=0;     // dampers lifted since silence, which draws each whisper
  int bankPoint[keyCount]{};float bankMix[keyCount]{};
  double travel[points]{};   // the bridge's displacement at each point
  double travelLeak=1,mobility=0;

  // The soundboard.
  int modes=0;
  float boardRe[maxModes]{},boardIm[maxModes]{},boardTurnRe[maxModes]{},boardTurnIm[maxModes]{};
  float boardIn[points][maxModes]{};
  float outNow[4][2][maxModes]{},outGoal[4][2][maxModes]{}; // left, right, room left, room right
  bool outMoving=false;
  // Above the modes: each point's force, high-passed, delayed to each
  // microphone.
  struct Tap {int point,delay;float gain;};
  Biquad highpass[points][3];   // two high-pass stages and the radiation's fall
  static constexpr int lineSize=8192;
  float line[points][lineSize]{};
  int lineAt=0;
  Tap taps[4][points*hfTapsPerPoint*micCount]{};int tapCount[4]{};
  // Beside the modes: each point's force through the board's filter, to
  // each microphone by the direct path, the floor and the lid.
  Biquad besideFilter[points][2];
  float lineBeside[points][lineSize]{};
  Tap tapsBeside[4][points*4*micCount]{};int tapBesideCount[4]{};
  float roomSend=0;
  float voicing[keyCount]{};   // each key's pull on the board, evened for the mix
  float pull[keyCount];        // a tool's own pull in its place; negative, none

  // The room: a feedback delay network (J.-M. Jot and A. Chaigne, "Digital
  // delay networks for designing artificial reverberators", AES 90th
  // Convention, 1991) of sixteen lines mixed by a Hadamard matrix. Eight
  // lines under a Householder reflection, as 2.6.0 had, took 310 ms to grow
  // dense (normalized echo density 0.9, Abel and Huang 2006) and a knock rang
  // in them as in a spring; sixteen take 180 ms, and 130 behind three allpass
  // sections (M. R. Schroeder, "Natural sounding artificial reverberation",
  // JAES 10, 1962). Only the case's knock goes through those: with the board
  // through them too, the upright's bass partials stood 0.4 dB further from
  // the recorded ones (11.13 against 10.73 dB).
  static constexpr int roomSize=32768,spreadSize=4096;
  float roomLine[roomLines][roomSize]{};
  int roomDelay[roomLines]{},roomAt=0;
  float roomGain[roomLines]{},roomDamp[roomLines]{},roomState[roomLines]{};
  float spreadLine[roomSpreads][spreadSize]{};
  int spreadDelay[roomSpreads]{};
  double dcL=0,dcR=0,dcInL=0,dcInR=0,dcPole=0;
  float boardRim[points+1][maxModes]{}; // the edge's places, and last all of them alike
  int catchIn[keyCount]{},catches=0;  // samples until a key's hammer is caught (-1: none), and how many wait
  float catchPush[keyCount]{};        // newtons for one sample
  double catchAt[keyCount][2]{};      // each catch's push, twice smoothed, newtons
  double casePole=0;
  bool frameRings=false;              // through this chunk: decided at its boundary, or by a blow in it
  Biquad frameTravel;            // the blow to the string ends' travel on the frame, metres
  Biquad frameKnock[points][2];  // the blow's lean on the capo bar to the edge's places, above knockHertz

  // The ideal string's pitch against the key's in equal temperament: the
  // string's stiffness raises its first partial, which is the one tuned.
  // A bend or a sample rate that would put a key's first partial past what
  // the rate can carry holds it there: a string turning more than half a
  // circle a step has no stable contact with its hammer.
  double tuningRatio(const KeyData& key,double bend) const noexcept {
    const double ratio=controls.tuning/440.*std::pow(2.,(controls.stretch*key.stretchCents/1200.)+bend/12.)/std::sqrt(1+key.inharmonicity);
    return std::min(ratio,.45*sampleRate/(key.hertz*key.ratio[0]));
  }
  double tuningRatio(const KeyData& key) const noexcept {return tuningRatio(key,bend);}
  // How far a unison's strings stand apart, in cents for one deviation: at
  // Detune 1, 6 cents up to B3, narrowing to half that from C5 up. A tuner
  // sets a unison by its beats, which the same cents make faster up the
  // keyboard. With the full spread everywhere the Salamander grand's first
  // partials from C5 up stood 7 to 8 dB over the recorded ones 1 to 1.5 s
  // after the blow (1.0 and 1.4 with this), and on four layers its partials'
  // decay stood 3.89 dB/s from the recorded on the unfitted notes, 3.36 with
  // this; narrowed on to 0.3 or all the way as 250/f, 3.52 and 3.36 with the
  // top octaves' sustain 0.8 dB further off. The upright keeps the full
  // spread: narrowed like the grand's, the decay of the notes it is fitted
  // on stood 4.95 dB/s from the Helsinki upright's where it stands 4.54.
  double unisonSpread(const KeyData& key) const noexcept {
    return (6*controls.detune*controls.detune+.15)*(table->design.upright?1:clamp(250/key.hertz,.5,1));
  }
  // The strings' own loss for a partial at w rad/s, 1/s. Old strings lose
  // their upper partials, wound ones most.
  double stringLoss(const KeyData& key,double w) const noexcept {
    const double age=controls.age;
    const double over=std::max(0.,w/(2000*pi)-key.hertz/1000);
    return key.loss1*(1+.8*age)+(key.loss2*over+key.loss3*w*w)*(1+(key.wound?10:5)*age);
  }
  static int planeLength(const Voice& v,int plane) noexcept {
    if(plane==0)return v.sounding;
    if(plane<3)return plane<v.strings?std::min(v.sounding,v.apart):0;
    return plane-3<v.strings?std::min(v.sounding,v.across):0;
  }
  void applyDamper(Voice& v) noexcept {
    const float d=v.damper;
    for(int plane=0;plane<6;++plane){const int n=planeLength(v,plane),o=planeStart[plane];
      // Across the bridge a string meets u^2 of the admittance it meets
      // down into it, and meets it alone.
      const float own=plane<3?0:v.u[plane]*v.u[plane];
      for(int k=0;k<n;++k){const float g=v.open[k]+(v.damped[k]-v.open[k])*d;
        v.turnRe[o+k]=v.cosine[o+k]*g-own*v.couplingRe[k];v.turnIm[o+k]=v.sine[o+k]*g-own*v.couplingIm[k];}}
    v.appliedDamper=d;
  }
  // A voice's partials and their frequencies from its key as the controls
  // and the bend stand.
  void tune(Voice& v,int index) noexcept {
    const KeyData& key=table->keys[index];
    // The bridge gives under the strings and so moves their pitch where a
    // mode of the board lies near (each step turns a partial by its angle
    // and by the unison's coupling, renderChunk). A tuner tunes what sounds:
    // the key's first partial is set where it is heard.
    const double ideal=key.hertz*tuningRatio(key);
    const double f0=ideal/(1-key.strings*key.couplingIm[0]/(2*pi*ideal*key.ratio[0]));
    v.strings=key.strings;
    int count=key.partials;
    while(count>1&&f0*key.ratio[count-1]>.45*sampleRate)--count;
    v.partials=count;
    v.apart=key.strings>1?std::min(count,maxKv):0;
    v.across=std::min(count,maxKh);
    v.longitudinal=index<52?std::min(count,maxKl):0;
    v.point=std::min(points-2,static_cast<int>(key.bridge));v.pointMix=static_cast<float>(key.bridge-v.point);
    // False beats grow with the strings' age.
    const double spread=unisonSpread(key),split=1e-4*(1+7*controls.age);
    for(int plane=0;plane<6;++plane){
      const int string=plane%3;const bool isAcross=plane>=3;
      const int n=plane==0?count:isAcross?(string<v.strings?v.across:0):(string<v.strings?v.apart:0);
      const double cents=spread*key.detune[string];
      const double apart=std::pow(2.,cents/1200.)*(isAcross?1+split*key.polarisation[string]:1);
      v.u[plane]=isAcross?key.across[string]:1;
      const int o=planeStart[plane];
      for(int k=0;k<n;++k){
        // The partials the strings play together sit at the unison's pitch.
        const double tuned=plane==0&&k>=v.apart&&v.strings>1?1:apart*(k<maxKv?key.stray[string][k]:1);
        turnOf(2*pi*f0*key.ratio[k]*tuned/sampleRate,v.cosine[o+k],v.sine[o+k]);
      }
    }
    for(int k=0;k<count;++k){
      // Above `apart` plane 0 is the strings' sum: together they load the
      // bridge once each.
      const double together=k>=v.apart&&v.strings>1?v.strings:1;
      // The coupling acts with the partial's turn, as the string's own loss
      // does. Taken before the turn it met the string a step late, and
      // where a step is a quarter of the partial's period or more the
      // bridge's springiness came out as a gain.
      const double re=key.couplingRe[k]*together/sampleRate,im=key.couplingIm[k]*together/sampleRate;
      v.couplingRe[k]=static_cast<float>(re*v.cosine[k]-im*v.sine[k]);
      v.couplingIm[k]=static_cast<float>(re*v.sine[k]+im*v.cosine[k]);
    }
  }
  // A voice's losses, coupling and pull on the bridge from its key as the
  // controls stand.
  void build(Voice& v,int index) noexcept {
    const KeyData& key=table->keys[index];
    const double f0=key.hertz*tuningRatio(key);
    tune(v,index);
    const int count=v.partials;
    for(int k=0;k<count;++k){
      const double w=2*pi*f0*key.ratio[k];
      const double loss=stringLoss(key,w);
      // Dampers hold a partial the less the nearer one of its nodes lies to
      // the felt, and the bass's lowest partials least.
      const double felt=.2+.8*std::pow(std::sin((k+1)*pi*.115),2);
      v.open[k]=static_cast<float>(std::exp(-loss/sampleRate));
      v.damped[k]=static_cast<float>(std::exp(-(loss+key.damper*felt)/sampleRate));
      // The string's pull on the bridge is its tension times its slope
      // there: T k pi / L per metre of mode k, alternating.
      v.bridge[k]=static_cast<float>(key.tension*(k+1)*pi/key.length*((k&1)?-1:1));
      // The longitudinal force: stretching raises the tension by
      // E S pi^2 / (4 L^2) * sum of k^2 y_k^2, whose part at twice each
      // partial pulls the bridge along the string (H. A. Conklin, "Generation
      // of partials due to nonlinear mixing in a stringed instrument", JASA
      // 105, 1999). About a fifth of it bends the board, by the bridge's
      // height over it.
      v.tension[k]=k<v.longitudinal?static_cast<float>(-.2*key.strings*key.young*pi*pi/(8*key.length*key.length)*(k+1)*(k+1)):0;
    }
    v.floor2=static_cast<float>(3e-6*3e-6);
    v.appliedDamper=-1;
  }
  void setDrive(Voice& v,int index,float soft) noexcept {
    const KeyData& key=table->keys[index];
    const double f0=key.hertz*tuningRatio(key);
    // Una corda: a grand's hammers shift off each unison's last string.
    const double shifted=table->design.upright?0:soft;
    for(int plane=0;plane<6;++plane){
      const int string=plane%3;const bool isAcross=plane>=3;
      const int n=plane==0?v.partials:isAcross?(string<v.strings?v.across:0):(string<v.strings?v.apart:0);
      const bool last=v.strings>1&&string==v.strings-1;
      const double share=key.share[string]*(last?1-.92*shifted:1)*(isAcross?key.acrossDrive[string]:1);
      const int o=planeStart[plane];
      for(int k=0;k<n;++k){
        const double w=2*pi*f0*key.ratio[k];
        double together=1;
        if(plane==0&&k>=v.apart&&v.strings>1)together=v.strings-.92*shifted;
        // A string's mode k takes 2 / (mu L w) sin(k pi x0 / L) metres per
        // newton-second of the hammer's force.
        v.drive[o+k]=static_cast<float>(share*together*2*key.shape[k]/(key.density*key.length*w)/sampleRate);
      }
    }
  }
  Contact& claimContact() noexcept {
    Contact* oldest=&contacts[0];
    for(auto& c:contacts){if(!c.active)return c;if(c.age>oldest->age)oldest=&c;}
    return *oldest;
  }
  void startContact(int index,float velocity,float soft,double late,double strength) noexcept {
    const KeyData& key=table->keys[index];
    Contact& c=claimContact();
    const Voice& v=voices[index];
    const double f0=key.hertz*tuningRatio(key),rate=sampleRate*substeps;
    c.active=true;c.key=index;c.age=0;c.partials=v.partials;c.give=0;c.late=late;c.strength=strength;
    for(int k=0;k<c.partials;++k){
      const double w=2*pi*f0*key.ratio[k],loss=std::exp(-stringLoss(key,w)/rate);
      c.turnRe[k]=static_cast<float>(std::cos(w/rate)*loss);c.turnIm[k]=static_cast<float>(std::sin(w/rate)*loss);
      c.shape[k]=key.shape[k];
      c.drive[k]=static_cast<float>(2*key.shape[k]/(key.density*key.length*w)/rate);
      c.re[k]=c.im[k]=0;
      c.give+=static_cast<double>(c.shape[k])*c.turnIm[k]*c.drive[k];
    }
    const bool upright=table->design.upright;
    // An upright's soft pedal halves the hammers' run, so they arrive
    // sqrt(1/2) as fast.
    c.velocity=hammerSpeed(velocity,controls.dynamics)*(upright?std::sqrt(1-.5*soft):1);
    c.position=0;c.previous=0;c.deepest=0;
    c.mass=key.hammerMass;
    // Hammer: a decade and a half of stiffness between soft and hard felt.
    // The felt strip softens the blow by up to three decades; shifted, a
    // grand's hammer strikes with felt the strings have not packed. The
    // exponent stays the key's: the stiffness is in newtons per metre to
    // that power, so a change of exponent is a far larger change of
    // stiffness the other way at the few tenths of a millimetre a blow
    // compresses the felt. Under the steeper felt a factor on the stiffness
    // moves the tone less, so these are half as many decades again as
    // 2.0.0's, which keeps what each does to middle C: Hammer -1 takes
    // 8 dB from what it holds above 2 kHz, and the strip 8 dB from its
    // level and 30 dB from what it holds above 1 kHz.
    const double stiffness=key.hammerStiffness*std::pow(10.,.75*controls.hammer-3*controls.felt-(upright?0:.3*soft));
    c.exponent=key.hammerExponent;
    c.relaxed=stiffness;
    c.prompt=stiffness*key.hammerSeconds*sampleRate*substeps;
  }
  // One step of hammer and string together. The felt is far stiffer than the
  // string is heavy, so the force is solved with the string's and the
  // hammer's answer to it inside the step: the string's modes turn by one
  // step, the hammer moves on, and the compression x that the felt's law and
  // their yielding (`give` metres per newton) agree on is found by Newton's
  // method on x + give F(x) = x unloaded, which rises with x throughout.
  // `previous` is the last step's x^p.
  void runContact(Contact& c,int frames) noexcept {
    Voice& v=voices[c.key];
    const double dt=1/(sampleRate*substeps);
    const int n=c.partials;
    const double give=dt*dt/c.mass+c.give;
    for(int s=0;s<frames;++s){
      double total=0;
      for(int sub=0;sub<substeps;++sub){
        float y=0;
        for(int k=0;k<n;++k){
          const float re=c.turnRe[k]*c.re[k]-c.turnIm[k]*c.im[k];
          c.im[k]=c.turnIm[k]*c.re[k]+c.turnRe[k]*c.im[k];c.re[k]=re;
          y+=c.shape[k]*c.im[k];
        }
        const double unloaded=c.position+c.velocity*dt-y;
        double force=0,x=std::max(unloaded,0.),felt=0;
        if(unloaded>0){
          // F(x) = relaxed x^p + prompt (x^p - last step's), never a pull.
          for(int i=0;i<8;++i){
            const double power=std::pow(x,c.exponent-1);
            const double law=(c.relaxed+c.prompt)*power*x-c.prompt*c.previous;
            const double step=(x+give*law-unloaded)/(1+give*(c.relaxed+c.prompt)*c.exponent*power);
            x=std::max(x-step,0.);
            if(std::abs(step)<1e-12)break;
          }
          felt=std::pow(x,c.exponent);
          force=(c.relaxed+c.prompt)*felt-c.prompt*c.previous;
          // The felt cannot pull: it leaves the string while still pressed.
          if(force<0){force=0;x=unloaded;felt=std::pow(x,c.exponent);}
          c.deepest=std::max(c.deepest,x);
        }
        c.previous=felt;
        c.velocity-=force/c.mass*dt;c.position+=c.velocity*dt;
        const float f=static_cast<float>(force);
        if(f>0)for(int k=0;k<n;++k){c.re[k]+=c.turnRe[k]*c.drive[k]*f;c.im[k]+=c.turnIm[k]*c.drive[k]*f;}
        total+=force;
      }
      v.force[s]+=static_cast<float>(total/substeps);
      ++c.age;
      // The hammer has left once it is falling back clear of the string.
      if((c.velocity<0&&c.position<-2*c.deepest-1e-5)||c.age>sampleRate*.08){c.active=false;
        // The action catches the hammer with the momentum it comes back with.
        if(c.velocity<0){const Design& d=table->design;const double back=-c.velocity;
          if(catchIn[c.key]<0&&catchAt[c.key][0]==0&&catchAt[c.key][1]==0)++catches;
          catchIn[c.key]=s+static_cast<int>(sampleRate*(d.catchSeconds+d.catchRun/back)*c.late);
          catchPush[c.key]=static_cast<float>(c.mass*back*c.strength*sampleRate);}
        break;}
    }
  }
  // Four partials at a time (Four.h), the last one to three singly: a lane
  // past a plane's length would wake a partial that was let go.
  void play(Voice& v,float* out,int frames) noexcept {
    float sumRe[maxK],sumIm[maxK],stretch[maxKl];
    const int n=v.sounding;
    const int lengths[6]{planeLength(v,0),planeLength(v,1),planeLength(v,2),planeLength(v,3),planeLength(v,4),planeLength(v,5)};
    for(int s=0;s<frames;++s){
      const float force=v.forcing?v.force[s]:0;
      int k=0;
      for(;k+4<=n;k+=4){Four::at(v.re+k).to(sumRe+k);Four::at(v.im+k).to(sumIm+k);}
      for(;k<n;++k){sumRe[k]=v.re[k];sumIm[k]=v.im[k];}
      for(int plane=1;plane<3;++plane){const int len=lengths[plane],o=planeStart[plane];
        for(k=0;k+4<=len;k+=4){(Four::at(sumRe+k)+Four::at(v.re+o+k)).to(sumRe+k);(Four::at(sumIm+k)+Four::at(v.im+o+k)).to(sumIm+k);}
        for(;k<len;++k){sumRe[k]+=v.re[o+k];sumIm[k]+=v.im[o+k];}}
      float pull=dot(v.bridge,sumIm,n);
      for(int plane=3;plane<6;++plane)pull+=v.u[plane]*dot(v.bridge,v.im+planeStart[plane],lengths[plane]);
      const int longitudinal=std::min(n,v.longitudinal);
      for(k=0;k+4<=longitudinal;k+=4){const Four re=Four::at(v.re+k),im=Four::at(v.im+k);(re*re-im*im).to(stretch+k);}
      for(;k<longitudinal;++k)stretch[k]=v.re[k]*v.re[k]-v.im[k]*v.im[k];
      out[s]=pull+dot(v.tension,stretch,longitudinal);
      // The bridge gives under the strings' sum and takes from each.
      for(k=0;k+4<=n;k+=4){
        const Four cRe=Four::at(v.couplingRe+k),cIm=Four::at(v.couplingIm+k),re=Four::at(sumRe+k),im=Four::at(sumIm+k);
        (cRe*re-cIm*im).to(sumRe+k);(cRe*im+cIm*re).to(sumIm+k);
      }
      for(;k<n;++k){
        const float cr=v.couplingRe[k]*sumRe[k]-v.couplingIm[k]*sumIm[k];
        sumIm[k]=v.couplingRe[k]*sumIm[k]+v.couplingIm[k]*sumRe[k];sumRe[k]=cr;
      }
      const Four forced=Four::all(force);
      for(int plane=0;plane<6;++plane){const int len=lengths[plane],o=planeStart[plane];const float u=plane<3?1.f:0.f;
        float* re=v.re+o;float* im=v.im+o;const float* tr=v.turnRe+o;const float* ti=v.turnIm+o;const float* drive=v.drive+o;
        const Four held=Four::all(u);
        for(k=0;k+4<=len;k+=4){
          const Four r=Four::at(re+k),i=Four::at(im+k),turnRe=Four::at(tr+k),turnIm=Four::at(ti+k);
          (turnRe*r-turnIm*i-held*Four::at(sumRe+k)+Four::at(drive+k)*forced).to(re+k);
          (turnIm*r+turnRe*i-held*Four::at(sumIm+k)).to(im+k);
        }
        for(;k<len;++k){
          const float r=tr[k]*re[k]-ti[k]*im[k]-u*sumRe[k]+drive[k]*force;
          im[k]=ti[k]*re[k]+tr[k]*im[k]-u*sumIm[k];re[k]=r;
        }
      }
    }
  }
  // Lets go of the highest partials once the bridge no longer feels them.
  void prune(Voice& v) noexcept {
    for(int tries=0;tries<6&&v.sounding>0;++tries){
      const int k=v.sounding-1;
      float energy=0;
      for(int plane=0;plane<6;++plane){if(k>=planeLength(v,plane))continue;const int o=planeStart[plane];
        energy+=v.re[o+k]*v.re[o+k]+v.im[o+k]*v.im[o+k];}
      if(energy*v.bridge[k]*v.bridge[k]>v.floor2)break;
      for(int plane=0;plane<6;++plane){if(k>=planeLength(v,plane))continue;const int o=planeStart[plane];v.re[o+k]=v.im[o+k]=0;}
      --v.sounding;
    }
    if(v.sounding==0)v.active=false;
  }
  // Mute lays felt on every string, held or not, lightly at first.
  float muted() const noexcept {return controls.mute*controls.mute;}
  float damperGoal(int index,bool withMute=true) const noexcept {
    const float felt=withMute?muted():0;
    if(index>=table->design.undamped||held[index])return felt;
    // The dampers start to clear the strings a fifth of the way down and
    // are off them at three quarters. Felt presses harder the further it is
    // let down, so its loss grows as the square of the way: the last third
    // of the lift is the half pedal, where the strings ring on, shortened.
    const double on=1-clamp((pedal-.2)/.55,0,1);
    return std::max(felt,static_cast<float>(on*on));
  }
  // A damper's felt, pressed into its strings, lets them go as it lifts: each
  // string is left a hair off its rest and rings, so that the pedal alone
  // sets the whole piano whispering. A pluck of `whisperTravel` metres where
  // the damper sat, less for a pedal let down slowly (`speed`, 1 for a lift
  // as fast as the dampers move), its size and sign the felt's chance.
  // whisperTravel is fitted to the Salamander's two pedal-down takes, beside
  // the engine's pedal knock at a Mechanics gain of 1: from 0.5 to 2.5 s
  // after the knock the takes hold, under its peak, 46, 47 and 51 dB and
  // 40, 38 and 45 dB from 300 to 450 Hz, to 700 Hz and to 1 kHz; the
  // concert grand's whisper 44, 42 and 47. Under 150 Hz the takes ring 25
  // to 35 dB more than that, on the strings from D2 to F2, which this does
  // not give.
  void whisper(int i,float speed) noexcept {
    const float size=static_cast<float>(whisperTravel*controls.sympathetic*2*speed);
    if(size==0)return;
    Rng r=seeded(i,static_cast<int>(lifts++),91);
    const float pluck=size*static_cast<float>(r.normal());
    for(int k=0;k<bankPartials;++k){const int at=i*bankSlots+k;
      if(bankOut[at]==0)continue;
      bankIm[at]+=pluck*static_cast<float>(std::sin((k+1)*pi*.115)/((k+1)*(k+1)));}
  }
  // The open strings' and duplex scales' modes for the controls as they are;
  // under a bend (`pitchOnly`) their frequencies alone.
  void tuneBank(bool pitchOnly=false) noexcept {
    for(int i=0;i<keyCount;++i){const KeyData& key=table->keys[i];
      const double f0=key.hertz*tuningRatio(key);
      bankApplied[i]=-1;
      if(pitchOnly){
        for(int slot=0;slot<bankSlots;++slot){const int at=i*bankSlots+slot;
          if(bankOut[at]==0)continue;
          const double hertz=f0*(slot<bankPartials?key.ratio[slot]:key.duplexRatio[slot-bankPartials]);
          turnOf(2*pi*std::min(hertz,.45*sampleRate)/sampleRate,bankCos[at],bankSin[at]);}
        continue;
      }
      // What a string is, it is unbent: a bend moves its pitch alone, so
      // that it comes back from one as it was.
      const double still=key.hertz*tuningRatio(key,0),bent=f0/still;
      bankPoint[i]=std::min(points-2,static_cast<int>(key.bridge));bankMix[i]=static_cast<float>(key.bridge-bankPoint[i]);
      // How far the unison's strings stand apart, as tune() sets them.
      double apart=0;for(int j=0;j<key.strings;++j)apart+=key.detune[j]*key.detune[j];
      apart=std::pow(2.,unisonSpread(key)*std::sqrt(apart/key.strings)/1200)-1;
      for(int slot=0;slot<bankSlots;++slot){const int at=i*bankSlots+slot;
        bankEnd[at]=0;
        const bool isDuplex=slot>=bankPartials;
        double hertz,loss,damper,drive,pull;
        if(!isDuplex){
          if(slot>=key.partials||still*key.ratio[slot]>.45*sampleRate){bankIn[at]=bankOut[at]=0;bankCos[at]=1;bankSin[at]=0;bankOpen[at]=bankDamped[at]=0;continue;}
          hertz=still*key.ratio[slot];const double w=2*pi*hertz;
          // One mode for the unison, set going with its strings in step.
          // In tune they stay so and load the bridge once each; further
          // apart than the bridge couples them (the loss it gives one
          // string, in rad/s) each rings on alone and loads it once in all:
          // the faster of a coupled pair's two decays (G. Weinreich,
          // "Coupled piano strings", JASA 62, 1977), taken for three too.
          // Loaded three times, the Salamander's top strings died at 35 to
          // 80 dB/s under a treble note where the recording's take 8 to 35.
          const double split=apart*w/std::max(1e-9,static_cast<double>(key.couplingRe[slot]));
          loss=stringLoss(key,w)+(1+(key.strings-1)*std::sqrt(std::max(0.,1-split*split)))*key.couplingRe[slot];
          damper=key.damper*(.2+.8*std::pow(std::sin((slot+1)*pi*.115),2));
          pull=key.tension*(slot+1)*pi/key.length*((slot&1)?-1:1);
          drive=2/(key.density*key.length*w)*pull;
          pull*=key.strings;
        }else{
          // The length behind the bridge as a short string of its own.
          const double ratio=key.duplexRatio[slot-bankPartials];
          hertz=still*ratio;
          if(!table->design.duplex||i<51||hertz>.45*sampleRate){bankIn[at]=bankOut[at]=0;bankCos[at]=1;bankSin[at]=0;bankOpen[at]=bankDamped[at]=0;continue;}
          const double w=2*pi*hertz,length=key.length/ratio;
          loss=5+stringLoss(key,w);damper=0;
          pull=key.tension*pi/length;
          drive=2/(key.density*length*w)*pull;
          pull*=key.strings;
        }
        turnOf(2*pi*std::min(hertz*bent,.45*sampleRate)/sampleRate,bankCos[at],bankSin[at]);
        bankOpen[at]=static_cast<float>(std::exp(-loss/sampleRate));
        bankDamped[at]=static_cast<float>(std::exp(-(loss+damper)/sampleRate));
        const double amount=isDuplex?2*controls.duplex:2*controls.sympathetic;
        bankIn[at]=static_cast<float>(amount*drive/sampleRate);bankOut[at]=static_cast<float>(pull);
        // The near end moves every mode the same way, where the bridge
        // moves them by turns; the duplex lengths lie beyond the bridge.
        if(!isDuplex)bankEnd[at]=std::abs(bankIn[at]);
      }
    }
  }
  void tuneBoard() noexcept {
    const Tables& t=*table;modes=t.modes;
    const double loss=boardLoss*std::pow(2.,1-2*controls.soundboard);
    for(int k=0;k<modes;++k){const double hertz=t.modeHertz[k],w=2*pi*hertz/sampleRate,g=std::exp(-pi*hertz*loss/sampleRate);
      boardTurnRe[k]=static_cast<float>(std::cos(w)*g);boardTurnIm[k]=static_cast<float>(std::sin(w)*g);
      for(int p=0;p<points;++p){boardIn[p][k]=static_cast<float>(t.modeIn[p][k]/sampleRate);
        boardRim[p][k]=static_cast<float>(t.modeEdge[p][k]/sampleRate);}
      double all=0;
      for(int p=0;p<points;++p)all+=t.modeEdge[p][k];
      boardRim[points][k]=static_cast<float>((all/points+rimHeave*t.modeHeave[k])/sampleRate);}
    for(int p=0;p<points;++p){for(int stage=0;stage<2;++stage){
      // A fourth-order high-pass at the modes' top.
      const double q=stage?1.3066:.5412,w0=2*pi*t.crossover/sampleRate,alpha=std::sin(w0)/(2*q),c=std::cos(w0),a0=1+alpha;
      Biquad& b=highpass[p][stage];
      b.b0=(1+c)/2/a0;b.b1=-(1+c)/a0;b.b2=(1+c)/2/a0;b.a1=-2*c/a0;b.a2=(1-alpha)/a0;
    }
      const double pole=std::exp(-2*pi*std::min(.45*sampleRate,radiationCorner)/sampleRate);
      Biquad& fall=highpass[p][2];fall.b0=1-pole;fall.b1=fall.b2=fall.a2=0;fall.a1=-pole;
      // Beside the modes: a second-order high-pass at the board's lowest
      // mode, and one pole above.
      {const double w0=2*pi*t.besideLow/sampleRate,alpha=std::sin(w0)/std::sqrt(2.),c=std::cos(w0),a0=1+alpha;
        Biquad& low=besideFilter[p][0];low.b0=(1+c)/2/a0;low.b1=-(1+c)/a0;low.b2=(1+c)/2/a0;low.a1=-2*c/a0;low.a2=(1-alpha)/a0;
        const double top=std::exp(-2*pi*std::min(.45*sampleRate,t.besideHigh)/sampleRate);
        Biquad& high=besideFilter[p][1];high.b0=t.besideGain*(1-top);high.b1=high.b2=high.a2=0;high.a1=-top;}}
  }
  // Each microphone's share of every mode and of the bridge's direct sound,
  // for the lid and the levels as they are.
  void mixMics() noexcept {
    const Tables& t=*table;
    const double lid=clamp(controls.lid,0,1);
    const double at=lid*(lidStops-1);const int stop=std::min(lidStops-2,static_cast<int>(at));const double between=at-stop;
    for(int out=0;out<4;++out){std::memset(outGoal[out],0,sizeof(outGoal[out]));tapCount[out]=tapBesideCount[out]=0;}
    double send=0;
    for(int mic=0;mic<micCount;++mic){
      const MicSpec& spec=t.mic[mic];
      // Every pair hears the piano as loud as the close one at the same
      // level: a fader is a balance, and the distance is in the sound
      // already. The room each pair sends to comes on top of that.
      const double level=clamp(controls.mic[mic],0,2)*std::sqrt(t.micLevel[micClose]/t.micLevel[mic]);
      const double shut=spec.shade*std::pow(1-lid,1.5);
      send+=level*spec.room;
      // The room hears the piano as the distant pair does.
      for(int feed=0;feed<2;++feed){
        if(feed==0&&level==0)continue;
        if(feed==1&&mic!=micDistant)continue;
        const double gain=feed?1:level;
        for(int ch=0;ch<2;++ch){const int out=2*feed+ch;
          for(int part=0;part<2;++part){
            const float* direct=t.direct[mic][ch][part];const float* floor=t.floor[mic][ch][part];const float* diffuse=t.diffuse[mic][ch][part];
            const float* lidA=t.lid[stop][mic][ch][part];const float* lidB=t.lid[stop+1][mic][ch][part];
            float* goal=outGoal[out][part];
            for(int k=0;k<t.modes;++k)
              goal[k]+=static_cast<float>(gain*(shade(shut,t.modeHertz[k])*(direct[k]+diffuse[k])+spec.floor*floor[k]
                                                +spec.lid*(lidA[k]+(lidB[k]-lidA[k])*between)));
          }
          for(int p=0;p<points;++p){
            const auto add=[&](HfTap tap,double g,bool beside){
              if(tap.gain==0||g==0)return;
              const int delay=std::min(lineSize-1,static_cast<int>(tap.seconds*sampleRate+.5));
              taps[out][tapCount[out]++]={p,delay,static_cast<float>(g*tap.gain)};
              if(beside)tapsBeside[out][tapBesideCount[out]++]={p,delay,static_cast<float>(g*tap.gain)};};
            add(t.hfDirect[mic][ch][p],gain*(1-.85*shut),true);
            add(t.hfFloor[mic][ch][p],gain*spec.floor,true);
            add(t.hfLid[stop][mic][ch][p],gain*spec.lid*(1-between),true);
            add(t.hfLid[stop+1][mic][ch][p],gain*spec.lid*between,true);
            // The two scattered arrivals stay above the modes: lower, where
            // they come within a wave of the first, they would only tilt a
            // channel's level.
            for(int e=0;e<2;++e)add(t.hfDiffuse[mic][ch][p][e],gain*(1-.85*shut),false);
          }
        }
      }
    }
    roomSend=static_cast<float>(send*2*clamp(controls.room,0,1));
    // A board answers each frequency in its own way, so a key comes out of
    // the microphones stronger or weaker than its neighbours, as a piano's
    // keys do before it is voiced. KeyVoicing.h holds what each key's strings
    // alone give every pair, and every two pairs together, since pairs in a
    // mix add as waves, against the even scale through the keys: each key
    // pulls on the board by what brings it there in this mix, no more than
    // 15 dB either way. Each pair's scale is set at the close pair's level
    // without the room, which also keeps the balance above where the modes
    // alone do not.
    const int body=static_cast<int>(controls.body);
    for(int i=0;i<keyCount;++i){double got=0,even=0;
      const float* heard=keyHeard[body][i];
      for(int a=0;a<micCount;++a){const double level=clamp(controls.mic[a],0,2);
        even+=level*level*keyEven[body][i][a];
        for(int b=a;b<micCount;++b)got+=(a==b?1:2)*level*clamp(controls.mic[b],0,2)**heard++;}
      // A key is pulled at most 15 dB: the furthest unvoiced key stands 14 dB
      // under the even scale (the baby grand's G#5 through the close pair),
      // and one 14 dB over it (the studio grand's G#3 in the four pairs
      // Keyra.Levels mixes).
      voicing[i]=even>0?static_cast<float>(clamp(std::sqrt(even/std::max(got,even/32)),1/5.6,5.6)):1;}
    // What sounds glides to the new mix; silence takes it at once.
    outMoving=!quiet;
    if(quiet)for(int out=0;out<4;++out)std::memcpy(outNow[out],outGoal[out],sizeof(outNow[out]));
  }
  void prepareRoom() noexcept {
    // Line lengths spread over 23 to 97 ms; the room falls 60 dB in 0.8 s,
    // its top in half that.
    constexpr double seconds[roomLines]{.0229,.0267,.0311,.0353,.0397,.0441,.0487,.0533,
                                        .0581,.0631,.0683,.0737,.0793,.0851,.0911,.0973};
    constexpr double spreads[roomSpreads]{.0047,.0073,.0113};
    for(int k=0;k<roomSpreads;++k)spreadDelay[k]=std::min(spreadSize-1,static_cast<int>(spreads[k]*sampleRate)|1);
    for(int k=0;k<roomLines;++k){
      roomDelay[k]=std::min(roomSize-1,static_cast<int>(seconds[k]*sampleRate)|1);
      roomGain[k]=static_cast<float>(std::pow(10.,-3*seconds[k]/.8));
      roomDamp[k]=static_cast<float>(1-std::exp(-2*pi*5200/sampleRate));
    }
  }
  void silence() noexcept {
    for(auto& v:voices){v.active=false;v.forcing=false;v.sounding=0;v.damper=0;v.appliedDamper=-1;
      std::memset(v.re,0,sizeof(v.re));std::memset(v.im,0,sizeof(v.im));std::memset(v.force,0,sizeof(v.force));}
    for(auto& c:contacts)c.active=false;
    std::memset(bankRe,0,sizeof(bankRe));std::memset(bankIm,0,sizeof(bankIm));
    std::memset(boardRe,0,sizeof(boardRe));std::memset(boardIm,0,sizeof(boardIm));
    std::memset(line,0,sizeof(line));std::memset(roomLine,0,sizeof(roomLine));std::memset(roomState,0,sizeof(roomState));std::memset(spreadLine,0,sizeof(spreadLine));
    for(auto& point:highpass)for(auto& stage:point)stage.z1=stage.z2=0;
    for(auto& point:besideFilter)for(auto& stage:point)stage.z1=stage.z2=0;
    std::memset(lineBeside,0,sizeof(lineBeside));
    for(double& x:travel)x=0;
    for(float& x:knocks)x=0;
    for(auto& state:catchAt)state[0]=state[1]=0;
    for(int& in:catchIn)in=-1;
    catches=0;
    frameRings=false;frameTravel.z1=frameTravel.z2=0;
    for(auto& place:frameKnock)for(auto& f:place)f.z1=f.z2=0;
    for(int i=0;i<keyCount;++i){bankAwake[i]=false;bankEnergy[i]=0;}
    lifts=0;
    // Silence takes the microphones' mix at once.
    for(int out=0;out<4;++out)std::memcpy(outNow[out],outGoal[out],sizeof(outNow[out]));
    outMoving=false;
    dcL=dcR=dcInL=dcInR=0;rest();
  }
  void select() noexcept {
    table=&tables[static_cast<int>(controls.body)];
    // The bridge moves at about a third of the plate's point mobility where
    // another key's strings cross it.
    mobility=.3/table->infinite;
    tuneBoard();tuneBank();mixMics();
    for(int out=0;out<4;++out)std::memcpy(outNow[out],outGoal[out],sizeof(outNow[out]));
    outMoving=false;
  }

  // Asleep: nothing sounds and nothing is computed until wake().
  void rest() noexcept {quiet=true;quietChunks=0;phase=0;loud=0;retune=false;}
  // What moved while it slept is where it now stands.
  void wake() noexcept {
    quietChunks=0;
    if(!quiet)return;
    quiet=false;
    for(int i=0;i<keyCount;++i){bankDamper[i]=damperGoal(i);damperOn[i]=damperGoal(i,false);bankApplied[i]=-1;}
  }
  // Every `chunk` samples, the same samples however the host cuts its blocks:
  // the bend is taken up, the dampers and the mix move on, and what has
  // decayed away is put to rest.
  void boundary() noexcept {
    if(retune){
      for(int i=0;i<keyCount;++i){Voice& v=voices[i];if(!v.active)continue;
        const int sounding=v.sounding;tune(v,i);v.sounding=std::min(sounding,v.partials);v.appliedDamper=-1;}
      tuneBank(true);retune=false;
    }
    // The dampers fall and lift over about 15 ms.
    const float damperStep=static_cast<float>(std::min(1.,chunk/(.015*sampleRate)));
    // Whatever has decayed this far is put to rest, before the processor
    // slows over numbers too small for it.
    constexpr float still=1e-18f;
    bool sounding=false;
    for(int i=0;i<keyCount;++i){
      const float goal=damperGoal(i);
      Voice& v=voices[i];
      if(v.active){
        if(v.damper!=goal){v.damper+=(goal-v.damper)*damperStep;if(std::abs(v.damper-goal)<.002f)v.damper=goal;}
        if(v.damper!=v.appliedDamper)applyDamper(v);
        if(!v.forcing)prune(v);
        sounding=sounding||v.active;
      }
      if(bankDamper[i]!=goal){bankDamper[i]+=(goal-bankDamper[i])*damperStep;if(std::abs(bankDamper[i]-goal)<.002f)bankDamper[i]=goal;}
      // The damper alone, without Mute's felt, which lets go of no string
      // at once. No two dampers leave their strings at the same height.
      const float lifted=damperGoal(i,false);
      if(damperOn[i]!=lifted){const float before=damperOn[i];
        damperOn[i]+=(lifted-before)*damperStep;if(std::abs(damperOn[i]-lifted)<.002f)damperOn[i]=lifted;
        const float leaves=.2f+.6f*static_cast<float>(seeded(i,17).uniform());
        if(before>=leaves&&damperOn[i]<leaves&&muted()<leaves&&!v.active)whisper(i,std::min(1.f,(before-lifted)/leaves));}
      const bool was=bankAwake[i];
      bankAwake[i]=bankEnergy[i]>chunk*1e-14f;bankEnergy[i]=0;
      if(was&&!bankAwake[i]&&bankDamper[i]>=1)for(int k=0;k<bankSlots;++k)bankRe[i*bankSlots+k]=bankIm[i*bankSlots+k]=0;
    }
    for(const auto& c:contacts)sounding=sounding||c.active;
    // A catch is over once the case has handed all of it on. Counted here,
    // at the chunk's boundary, so that the host's blocks do not decide when.
    if(catches>0){catches=0;
      for(int i=0;i<keyCount;++i){double* state=catchAt[i];
        if(catchIn[i]<0&&std::abs(state[0])+std::abs(state[1])<=1e-9*catchPush[i])state[0]=state[1]=0;
        if(catchIn[i]>=0||state[0]!=0||state[1]!=0)++catches;}}
    sounding=sounding||catches>0;
    frameRings=std::abs(frameTravel.z1)+std::abs(frameTravel.z2)>still;
    for(const auto& place:frameKnock)for(const auto& f:place)frameRings=frameRings||std::abs(f.z1)+std::abs(f.z2)>still;
    if(outMoving){float furthest=0;
      for(int out=0;out<4;++out)for(int part=0;part<2;++part)for(int k=0;k<modes;++k){
        float& now=outNow[out][part][k];const float step=(outGoal[out][part][k]-now)*.25f;now+=step;furthest=std::max(furthest,std::abs(step));}
      if(furthest<1e-9f){for(int out=0;out<4;++out)std::memcpy(outNow[out],outGoal[out],sizeof(outNow[out]));outMoving=false;}}
    for(double& x:travel)if(std::abs(x)<still)x=0;
    for(int k=0;k<modes;++k)if(std::abs(boardRe[k])+std::abs(boardIm[k])<still)boardRe[k]=boardIm[k]=0;
    for(auto& point:highpass)for(auto& stage:point){if(std::abs(stage.z1)<still)stage.z1=0;if(std::abs(stage.z2)<still)stage.z2=0;}
    for(auto& point:besideFilter)for(auto& stage:point){if(std::abs(stage.z1)<still)stage.z1=0;if(std::abs(stage.z2)<still)stage.z2=0;}
    for(float& x:roomState)if(std::abs(x)<still)x=0;
    quietChunks=sounding||loud>1e-9f?0:quietChunks+1;loud=0;
    // Two seconds of nothing: everything left is put to rest.
    if(quietChunks*chunk>2*sampleRate){
      std::memset(boardRe,0,sizeof(boardRe));std::memset(boardIm,0,sizeof(boardIm));
      std::memset(bankRe,0,sizeof(bankRe));std::memset(bankIm,0,sizeof(bankIm));
      std::memset(line,0,sizeof(line));std::memset(roomLine,0,sizeof(roomLine));std::memset(roomState,0,sizeof(roomState));std::memset(spreadLine,0,sizeof(spreadLine));
      for(double& x:travel)x=0;
      for(auto& point:highpass)for(auto& stage:point)stage.z1=stage.z2=0;
      for(auto& point:besideFilter)for(auto& stage:point)stage.z1=stage.z2=0;
      std::memset(lineBeside,0,sizeof(lineBeside));
      for(int i=0;i<keyCount;++i){bankAwake[i]=false;bankEnergy[i]=0;}
      dcL=dcR=dcInL=dcInR=0;rest();}
  }
  void renderChunk(float* left,float* right,int frames) noexcept {
    alignas(32) float struck[points][chunk],answered[points][chunk],each[chunk];
    std::memset(struck,0,sizeof(struck));std::memset(answered,0,sizeof(answered));
    for(auto& c:contacts)if(c.active)runContact(c,frames);
    for(int p=0;p<points;++p){struck[p][0]=knocks[p];knocks[p]=0;}
    alignas(32) float blow[chunk]{};
    // What reaches the board's edge at each of its places, and last at all
    // of them alike: the blows' lean on the capo bar and the caught hammers.
    alignas(32) float rim[points+1][chunk],leans[points][chunk];
    bool rimmed=false,leaned=false;
    const auto placeOf=[](int key,int& place,float& share){const double at=key/(keyCount-1.)*(points-1);
      place=std::min(points-2,static_cast<int>(at));share=static_cast<float>(at-place);};
    for(int i=0;i<keyCount;++i){Voice& v=voices[i];
      if(!v.active)continue;
      if(v.forcing){const float near=static_cast<float>((1-table->keys[i].strike)*v.strings);
        if(!leaned){std::memset(leans,0,sizeof(leans));leaned=true;}
        int place;float share;placeOf(i,place,share);
        const float arm=static_cast<float>(knockArm*clamp((i-capoFrom+3)/6.,0,1));
        for(int s=0;s<frames;++s){const float lean=near*v.force[s];blow[s]+=lean;
          leans[place][s]+=arm*(1-share)*lean;leans[place+1][s]+=arm*share*lean;}
        frameRings=true;}
      play(v,each,frames);
      const float pulled=pull[i]<0?voicing[i]:pull[i],b=v.pointMix*pulled,a=pulled-b;
      for(int s=0;s<frames;++s){struck[v.point][s]+=a*each[s];struck[v.point+1][s]+=b*each[s];}
      if(v.forcing){bool still=false;for(const auto& c:contacts)still=still||(c.active&&c.key==i);
        std::memset(v.force,0,sizeof(v.force));v.forcing=still;}
    }
    if(frameRings){std::memset(rim,0,sizeof(rim));rimmed=true;
      if(!leaned)std::memset(leans,0,sizeof(leans));
      for(int p=0;p<points;++p)for(int s=0;s<frames;++s)rim[p][s]=static_cast<float>(frameKnock[p][1].run(frameKnock[p][0].run(leans[p][s])));}
    else for(auto& place:frameKnock)for(auto& f:place)f.z1=f.z2=0;
    // What the case gives the room of the knock.
    alignas(32) float cased[chunk]{};
    if(rimmed)for(int p=0;p<points;++p)for(int s=0;s<frames;++s)cased[s]+=caseSound*rim[p][s];
    // The hammers the action catches in this chunk, and what the case hands
    // on of them.
    if(catches>0){
      if(!rimmed){std::memset(rim,0,sizeof(rim));rimmed=true;}
      for(int i=0;i<keyCount;++i){double* state=catchAt[i];
        int lands=frames;
        if(catchIn[i]>=frames)catchIn[i]-=frames;
        else if(catchIn[i]>=0){lands=catchIn[i];catchIn[i]=-1;}
        if(lands==frames&&state[0]==0&&state[1]==0)continue;
        const double pole=casePole;int place;float share;placeOf(i,place,share);
        const float whole=static_cast<float>(keybedShare*table->design.caseArm),own=static_cast<float>(table->design.caseArm)-whole;
        const float b=share*own,a=own-b;
        for(int s=0;s<frames;++s){
          state[0]+=pole*((s==lands?catchPush[i]:0)-state[0]);state[1]+=pole*(state[0]-state[1]);
          const float push=static_cast<float>(state[1]);
          rim[points][s]+=whole*push;rim[place][s]+=a*push;rim[place+1][s]+=b*push;}}}
    // The string ends' travel on the frame under the blow.
    alignas(32) float pushed[chunk]{};
    if(frameRings)for(int s=0;s<frames;++s)pushed[s]=static_cast<float>(frameTravel.run(frameGive*blow[s]));
    else frameTravel.z1=frameTravel.z2=0;
    // The bridge's displacement under what was struck, which drives every
    // string whose damper is off it.
    alignas(32) float moved[points][chunk];
    for(int p=0;p<points;++p){double x=travel[p];
      for(int s=0;s<frames;++s){x=x*travelLeak+mobility*struck[p][s]/sampleRate;moved[p][s]=static_cast<float>(x);}
      travel[p]=x;}
    for(int i=0;i<keyCount;++i){
      const int o=i*bankSlots;
      const bool open=bankDamper[i]<1;
      if(!open&&!bankAwake[i])continue;
      if(bankDamper[i]!=bankApplied[i]){const float d=bankDamper[i];
        for(int k=0;k<bankSlots;++k){const float g=k<bankPartials?bankOpen[o+k]+(bankDamped[o+k]-bankOpen[o+k])*d:bankOpen[o+k];
          bankTurnRe[o+k]=bankCos[o+k]*g;bankTurnIm[o+k]=bankSin[o+k]*g;}
        // What the string pulls with while it only follows its end: each
        // mode's answer to an end that stands still, as it turns now.
        double follow=0;
        for(int k=0;k<bankPartials;++k){const double re=1-bankTurnRe[o+k],im=bankTurnIm[o+k];
          follow+=bankOut[o+k]*bankEnd[o+k]*im/std::max(1e-30,re*re+im*im);}
        bankFollow[i]=static_cast<float>(follow);
        bankApplied[i]=d;}
      // A sounding key's own strings are its voice's.
      const bool own=voices[i].active;
      const int p=bankPoint[i];const float b=bankMix[i],a=1-b;
      float energy=0;
      // The key's modes in three vectors for the chunk. The pull is dot()'s
      // sum of out[k] im[k] over the twelve: eight strands from nothing, then
      // the last four in order.
      static_assert(bankSlots==12,"the open strings' modes fill three vectors");
      Four re[3],im[3];const Four none=Four::all(0);
      const float* tr=bankTurnRe+o;const float* ti=bankTurnIm+o;const float* in=bankIn+o;const float* end=bankEnd+o;const float* out=bankOut+o;
      for(int j=0;j<3;++j){re[j]=Four::at(bankRe+o+4*j);im[j]=Four::at(bankIm+o+4*j);}
      const float follow=bankFollow[i];
      for(int s=0;s<frames;++s){
        const float x=own?0:a*moved[p][s]+b*moved[p+1][s],y=own?0:pushed[s];
        const Four moving=Four::all(x),pushing=Four::all(y);
        Four product[3];
        // The SDK's compiler keeps the vectors in registers only when told
        // the loop is three steps long.
#if defined(__clang__)
#pragma unroll
#endif
        for(int j=0;j<3;++j){
          const Four turnRe=Four::at(tr+4*j),turnIm=Four::at(ti+4*j);
          const Four r=turnRe*re[j]-turnIm*im[j]+Four::at(in+4*j)*moving+Four::at(end+4*j)*pushing;
          im[j]=turnIm*re[j]+turnRe*im[j];re[j]=r;
          product[j]=Four::at(out+4*j)*im[j];
        }
        // A string that only follows its end leans on the frame and the
        // bridge as it stands between them; what it rings beyond that is
        // what the bridge hears.
        const Four low=none+product[0],high=none+product[1];
        const float rest=(((0.f+product[2][0])+product[2][1])+product[2][2])+product[2][3];
        const float pull=((low[0]+low[1])+(low[2]+low[3]))+((high[0]+high[1])+(high[2]+high[3]))+rest-follow*y;
        answered[p][s]+=a*pull;answered[p+1][s]+=b*pull;energy+=pull*pull;
      }
      for(int j=0;j<3;++j){re[j].to(bankRe+o+4*j);im[j].to(bankIm+o+4*j);}
      bankEnergy[i]+=energy;
    }
    // The board, and above its modes the bridge's own radiation.
    const int mask=lineSize-1,roomMask=roomSize-1;
    for(int s=0;s<frames;++s){
      // What pushes the board in this sample: each bridge point's force and
      // each place of the edge, those at rest left out.
      const float* pushing[2*points+1];float pushes[2*points+1];int pushCount=0;
      for(int p=0;p<points;++p){
        const float force=struck[p][s]+answered[p][s];
        line[p][lineAt]=static_cast<float>(highpass[p][2].run(highpass[p][1].run(highpass[p][0].run(force))));
        lineBeside[p][lineAt]=static_cast<float>(besideFilter[p][1].run(besideFilter[p][0].run(force)));
        if(force==0)continue;
        pushing[pushCount]=boardIn[p];pushes[pushCount++]=force;
      }
      if(rimmed)for(int p=0;p<=points;++p){
        const float push=rim[p][s];
        if(push==0)continue;
        pushing[pushCount]=boardRim[p];pushes[pushCount++]=push;
      }
      int k=0;
      for(;k+4<=modes;k+=4){
        Four in=Four::all(0);
        for(int j=0;j<pushCount;++j)in+=Four::at(pushing[j]+k)*Four::all(pushes[j]);
        const Four re=Four::at(boardRe+k),im=Four::at(boardIm+k),turnRe=Four::at(boardTurnRe+k),turnIm=Four::at(boardTurnIm+k);
        (turnRe*re-turnIm*im+in).to(boardRe+k);(turnIm*re+turnRe*im).to(boardIm+k);
      }
      for(;k<modes;++k){
        float in=0;
        for(int j=0;j<pushCount;++j)in+=pushing[j][k]*pushes[j];
        const float re=boardTurnRe[k]*boardRe[k]-boardTurnIm[k]*boardIm[k]+in;
        boardIm[k]=boardTurnIm[k]*boardRe[k]+boardTurnRe[k]*boardIm[k];boardRe[k]=re;
      }
      float o[4];
      for(int out=0;out<4;++out){const Tap* tap=taps[out];
        float sum=dot(outNow[out][0],boardRe,modes)+dot(outNow[out][1],boardIm,modes);
        for(int k=0;k<tapCount[out];++k)sum+=tap[k].gain*line[tap[k].point][(lineAt-tap[k].delay)&mask];
        const Tap* beside=tapsBeside[out];
        for(int k=0;k<tapBesideCount[out];++k)sum+=beside[k].gain*lineBeside[beside[k].point][(lineAt-beside[k].delay)&mask];
        o[out]=sum;}
      lineAt=(lineAt+1)&mask;
      // The room.
      float knock=cased[s];
      for(int k=0;k<roomSpreads;++k){
        float* held=spreadLine[k];
        const float old=held[(roomAt-spreadDelay[k])&(spreadSize-1)],in=knock+.6f*old;
        held[roomAt&(spreadSize-1)]=in;knock=old-.6f*in;}
      float back[roomLines],roomL=0,roomR=0;
      for(int k=0;k<roomLines;++k){
        const float x=roomLine[k][(roomAt-roomDelay[k])&roomMask];
        roomState[k]+=roomDamp[k]*(x-roomState[k]);back[k]=roomState[k]*roomGain[k];
        if(k&1)roomR+=(k&4)?-back[k]:back[k];else roomL+=(k&4)?-back[k]:back[k];}
      for(int span=1;span<roomLines;span*=2)for(int k=0;k<roomLines;k+=2*span)for(int j=k;j<k+span;++j){
        const float a=back[j],b=back[j+span];back[j]=a+b;back[j+span]=a-b;}
      for(int k=0;k<roomLines;++k)
        roomLine[k][roomAt]=.25f*back[k]+((k&1)?o[3]:o[2])*((k&2)?-.5f:.5f)+knock*(((k^(k>>1))&2)?-.5f:.5f);
      roomAt=(roomAt+1)&roomMask;
      roomL*=roomLevel;roomR*=roomLevel;
      const double l=o[0]+roomSend*roomL,r=o[1]+roomSend*roomR;
      // Nothing under 10 Hz is sound.
      dcL=dcPole*(dcL+l-dcInL);dcInL=l;dcR=dcPole*(dcR+r-dcInR);dcInR=r;
      left[s]=static_cast<float>(dcL);right[s]=static_cast<float>(dcR);
      loud=std::max(loud,std::max(std::abs(left[s]),std::abs(right[s])));
    }
  }
};

float touched(float velocity,float decibels,float dynamics) noexcept {
  return static_cast<float>((velocity+softest)*std::pow(10.,decibels/(20*dynamicsPower(dynamics)))-softest);
}

Piano::Piano():impl(new Impl){for(float& gain:impl->pull)gain=-1;for(int& in:impl->catchIn)in=-1;prepare(48000);}
Piano::~Piano()=default;
void Piano::prepare(double sampleRate){
  auto& p=*impl;
  p.sampleRate=sampleRate==sampleRate?std::max(8000.,std::min(192000.,sampleRate)):48000.;
  if(!p.tables){
    p.tables.reset(new Tables[bodyCount]);
    for(int b=0;b<bodyCount;++b){Tables& t=p.tables[b];t.design=designs[b];designStrings(t,b);designBoard(t,b);}
  }
  p.substeps=p.sampleRate<70000?2:1;
  p.travelLeak=std::exp(-2*pi*8/p.sampleRate);
  p.dcPole=std::exp(-2*pi*10/p.sampleRate);
  {const double w=2*pi*frameCorner/p.sampleRate,alpha=std::sin(w)/std::sqrt(2.),c=std::cos(w),a0=1+alpha;
    Biquad& f=p.frameTravel;f.b0=f.b2=(1-c)/2/a0;f.b1=(1-c)/a0;f.a1=-2*c/a0;f.a2=(1-alpha)/a0;}
  p.casePole=1-std::exp(-2*pi*caseHertz/p.sampleRate);
  // A fourth-order high-pass.
  for(auto& place:p.frameKnock)for(int stage=0;stage<2;++stage){Biquad& f=place[stage];
    const double w=2*pi*knockHertz/p.sampleRate,alpha=std::sin(w)/(2*(stage?1.3066:.5412)),c=std::cos(w),a0=1+alpha;
    f.b0=f.b2=(1+c)/2/a0;f.b1=-(1+c)/a0;f.a1=-2*c/a0;f.a2=(1-alpha)/a0;}
  p.prepareRoom();
  p.select();
  reset();
}
void Piano::reset() noexcept {
  auto& p=*impl;p.pedal=0;p.pedalKnown=false;for(bool& h:p.held)h=false;p.silence();
  // The sympathetic strings come back from a bend with it.
  if(p.bend!=0){p.bend=0;p.tuneBank(true);}
}
void Piano::setControls(const Controls& input) noexcept {
  auto& p=*impl;const Controls old=p.controls;Controls c=input;
  if(static_cast<int>(c.body)<0||static_cast<int>(c.body)>=bodyCount)c.body=Body::concertGrand;
  c.hammer=clampf(c.hammer,-1,1);c.age=clampf(c.age,0,1);c.detune=clampf(c.detune,0,1);c.stretch=clampf(c.stretch,0,2);
  c.dynamics=clampf(c.dynamics,0,1);c.lid=clampf(c.lid,0,1);c.soundboard=clampf(c.soundboard,0,1);
  c.sympathetic=clampf(c.sympathetic,0,1);c.duplex=clampf(c.duplex,0,1);c.room=clampf(c.room,0,1);
  c.tuning=clampf(c.tuning,300,600);c.felt=clampf(c.felt,0,1);c.mute=clampf(c.mute,0,1);
  for(float& level:c.mic)level=clampf(level,0,2);
  p.controls=c;
  if(c.body!=old.body){p.select();p.silence();return;}
  if(c.soundboard!=old.soundboard)p.tuneBoard();
  if(c.tuning!=old.tuning||c.stretch!=old.stretch||c.age!=old.age||c.detune!=old.detune||c.sympathetic!=old.sympathetic||c.duplex!=old.duplex)p.tuneBank();
  // What sounds follows the tuner at the next boundary.
  if(c.tuning!=old.tuning||c.stretch!=old.stretch||c.detune!=old.detune)p.retune=!p.quiet;
  bool mics=c.lid!=old.lid||c.room!=old.room;
  for(int m=0;m<micCount;++m)mics=mics||c.mic[m]!=old.mic[m];
  if(mics)p.mixMics();
}
void Piano::strike(int key,float velocity,float soft,std::uint32_t chance) noexcept {
  if(key<0||key>=keyCount||!(velocity>0))return;
  auto& p=*impl;Voice& v=p.voices[key];
  p.wake();
  // What still rings keeps ringing; the blow adds to it.
  p.build(v,key);
  v.sounding=v.partials;v.active=true;v.forcing=true;
  // The key lifts its damper before the hammer arrives.
  v.damper=p.bankDamper[key]=p.muted();
  p.applyDamper(v);
  p.setDrive(v,key,clampf(soft,0,1));
  // The action catches the hammer a little sooner or later and harder or
  // softer than the last time.
  double late=1,strength=1;
  if(chance){
    chance=chance*747796405u+2891336453u;if(!chance)chance=1;
    const auto draw=[&chance]{ // near enough normal: four uniform draws summed, within 3.5 spreads
      double sum=0;
      for(int k=0;k<4;++k){chance^=chance<<13;chance^=chance>>17;chance^=chance<<5;sum+=chance*(1./4294967296.)-.5;}
      return std::sqrt(3.)*sum;};
    late=std::exp(catchSpreadTime*draw());strength=std::pow(10.,catchSpreadDb*draw()/20);}
  p.startContact(key,clampf(velocity,0,1),clampf(soft,0,1),late,strength);
}
void Piano::holdDamper(int key,bool held) noexcept {if(key>=0&&key<keyCount)impl->held[key]=held;}
void Piano::setPedal(float travel) noexcept {
  auto& p=*impl;travel=clampf(travel,0,1);
  // A pedal going down wakes a silent piano: its strings whisper.
  // The first travel after reset() is where the pedal stands, not a press.
  if(p.quiet&&p.pedalKnown&&travel>p.pedal&&p.controls.sympathetic>0)p.wake();
  p.pedal=travel;p.pedalKnown=true;
}
void Piano::setBend(float semitones) noexcept {
  auto& p=*impl;const float bend=clampf(semitones,-48,48);
  if(bend==p.bend)return;
  p.bend=bend;
  if(p.quiet)p.tuneBank(true);else p.retune=true;
}
void Piano::process(float* left,float* right,int frames) noexcept {
  if(!left||!right||frames<=0)return;
  auto& p=*impl;
  for(int done=0;done<frames;){
    if(p.phase==0&&!p.quiet)p.boundary();
    if(p.quiet){std::fill_n(left+done,frames-done,0.f);std::fill_n(right+done,frames-done,0.f);return;}
    const int n=std::min(chunk-p.phase,frames-done);
    p.renderChunk(left+done,right+done,n);
    done+=n;p.phase=(p.phase+n)%chunk;
  }
}
bool Piano::silent() const noexcept {return impl->quiet;}
void Piano::knockBridge(int key,float newtonSeconds) noexcept {
  if(key<0||key>=keyCount)return;
  auto& p=*impl;const double at=p.table->keys[key].bridge;const int point=std::min(points-2,static_cast<int>(at));
  const float impulse=static_cast<float>(newtonSeconds*p.sampleRate),b=static_cast<float>(at-point);
  p.knocks[point]+=(1-b)*impulse;p.knocks[point+1]+=b*impulse;p.wake();
}
void Piano::pullKey(int key,float gain) noexcept {if(key>=0&&key<keyCount)impl->pull[key]=gain;}
Piano::KeyReport Piano::report(Body body,int key) const noexcept {
  const KeyData& k=impl->tables[static_cast<int>(body)].keys[std::max(0,std::min(keyCount-1,key))];
  return {k.strings,k.partials,k.hertz,k.length,k.tension,k.inharmonicity,k.stretchCents,k.hammerMass};
}
}}
