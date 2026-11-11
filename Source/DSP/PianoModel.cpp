#include "PianoModel.h"
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
constexpr int roomLines=8;

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
  float strand[8]{};int k=0;
  for(;k+8<=n;k+=8)for(int j=0;j<8;++j)strand[j]+=a[k+j]*b[k+j];
  float rest=0;
  for(;k<n;++k)rest+=a[k]*b[k];
  return ((strand[0]+strand[1])+(strand[2]+strand[3]))+((strand[4]+strand[5])+(strand[6]+strand[7]))+rest;
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
};
constexpr Design designs[bodyCount]{
  // 2.74 m concert grand
  {false,2.01,8,20,20,1.45,1.55,{.86,.10},{.22,.80},69,true,1.,1.,50},
  // 1.86 m parlor grand
  {false,1.40,8,26,26,1.42,1.12,{.86,.11},{.20,.82},69,true,.96,1.1,65},
  // 1.50 m baby grand
  {false,1.14,10,28,28,1.40,.86,{.86,.13},{.18,.84},68,true,.92,1.2,80},
  // 1.25 m upright. Its hammers' stiffness is fitted to eleven forte notes
  // of a recorded upright (MAPS, ENSTDkCl: a Yamaha Disklavier, close pair),
  // whose bass notes hold more above 2 kHz than softer hammers gave.
  {true,1.18,10,30,30,1.40,.95,{.84,.80},{.14,.22},66,false,.9,2.6,90},
};
// The soundboard as one ribbed plate smeared out: bending stiffnesses along
// and across the grain with the ribs' counted in, and the mass per area of
// board, ribs and bridges. Chosen so that the plate's point impedance,
// 8 sqrt(D m), is about 2.5e3 kg/s and its modal density about 0.05 per Hz
// for 1.6 m^2, as measured boards' are (Ege et al. 2013; N. Giordano,
// "Mechanical impedance of a piano soundboard", JASA 103, 1998).
constexpr double boardMass=19.5,boardStiffX=6500,boardStiffY=3800;
constexpr double boardLoss=.025;        // loss factor at Soundboard = .5
constexpr double boardEdge=.5;          // edges between hinged (0) and clamped (.5)
constexpr double modesTop=2600;         // Hz: no mode is kept above it
// Hz: above it the board radiates less, 6 dB an octave. At 3 kHz (2.0.0) the
// middle of the keyboard held 5 to 9 dB less in the 4 kHz octave than the
// Salamander grand's forte notes; at 12 kHz the bass held more between its
// partials than they do.
constexpr double radiationCorner=6000;
constexpr double patchRadius=.5;        // m: what radiates about the bridge above the modes
// The blow's thump. A string struck at an eighth of its length leans seven
// eighths of the blow on its near end, the agraffe in the iron frame, and the
// frame knocks the board it is bolted over: what comes of it about
// frameHertz, frameShare times as strong, spread along the bridge. Both are
// fitted to what the Steinway notes hold under their fundamentals in their
// first 150 ms (12 to 18 dB under the note, most of it from 60 to 240 Hz,
// swelling for 20 ms and gone in 150); the strings' own pull on the bridge
// is 20 dB short of it.
constexpr double frameShare=2,frameHertz=160;

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
  if(!d.upright)switch(mic){
    case micClose: return {{{.30*X,.22,.20},{.72*X,.20,.20}},{{0,0,-1},{0,0,-1}},0,1,0,0,.5,.03,.35};
    case micXY: {const Vec at{X+.8,.45*Y,1.3},aim{.5*X,.4*Y,0};
      return {{at,at},{toward(at,aim,-pi/4),toward(at,aim,pi/4)},1,1,.8,-.3,.6,.18,.7};}
    case micLive: return {{{X+2.3,.5*Y-.6,1.6},{X+2.3,.5*Y+.6,1.6}},{{-1,0,0},{-1,0,0}},0,1,.85,-.3,.6,.45,1.2};
    default: return {{{X+6,.5*Y-1.5,2.5},{X+6,.5*Y+1.5,2.5}},{{-1,0,0},{-1,0,0}},0,1,.9,-.3,.6,1.,2.};
  }
  // An upright: x across, y up, the open back on the z > 0 side.
  switch(mic){
    case micClose: return {{{.30*X,.55*Y,.30},{.70*X,.55*Y,.30}},{{0,0,-1},{0,0,-1}},0,1,0,.3,0,.04,.35};
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
  float duplexRatio[duplexModes]{};
};
struct HfTap {float gain,seconds;};
struct Tables {
  Design design{};
  KeyData keys[keyCount];
  int modes=0;
  double crossover=0;          // Hz, the modes' top
  double infinite=0;           // the plate's point impedance, kg/s
  float modeHertz[maxModes]{};
  float modeIn[points][maxModes]{};         // shape at the point / (modal mass w)
  // Each mode's radiation to a microphone, as acceleration to pascals:
  // directly, by the floor and by the lid at each stop.
  float direct[micCount][2][2][maxModes]{};
  float floor[micCount][2][2][maxModes]{};
  float lid[lidStops][micCount][2][2][maxModes]{};
  float diffuse[micCount][2][2][maxModes]{};
  // Each pair's level, and each key's against the scale's in each pair.
  float micLevel[micCount]{},keyLevel[micCount][keyCount]{};
  HfTap hfDirect[micCount][2][points]{},hfFloor[micCount][2][points]{},hfLid[lidStops][micCount][2][points]{};
  HfTap hfDiffuse[micCount][2][points][2]{};
  MicSpec mic[micCount]{};
};

// --- the scale -----------------------------------------------------------
void designStrings(Tables& t,int body) noexcept {
  const Design& d=t.design;
  // The speaking length doubles a little less than every octave down from
  // C8's 50 mm, until the case's length bends it over.
  const auto ideal=[](int key){return .050*std::pow(2.,(87-key)/12.*.93);};
  constexpr double bend=2.5;
  const double longest=std::pow(std::pow(d.bassLength,-bend)-std::pow(ideal(0),-bend),-1/bend);
  for(int i=0;i<keyCount;++i){
    KeyData& k=t.keys[i];
    k.hertz=440*std::pow(2.,(i-48)/12.);
    k.strings=i<d.monochords?1:i<d.trichords?2:3;
    k.length=std::pow(std::pow(ideal(i),-bend)+std::pow(longest,-bend),-1/bend);
    k.wound=i<d.plain;
    double core;
    if(!k.wound){
      // Plain wire from 0.775 mm at the top to 1.125 mm at the break.
      core=(.775+.35*(87-i)/(87.-d.plain))*1e-3;
      k.density=steelDensity*pi*core*core/4;
      k.tension=4*k.length*k.length*k.hertz*k.hertz*k.density;
      k.inharmonicity=pi*pi*pi*steelYoung*std::pow(core,4)/(64*k.tension*k.length*k.length);
    }else{
      // Copper-wound strings: the winding sets the mass for the tension the
      // scale asks, the steel core the stiffness.
      const double deep=(d.plain-i)/static_cast<double>(d.plain);
      k.tension=850+550*deep;
      k.density=k.tension/(4*k.length*k.length*k.hertz*k.hertz);
      core=(1.05+.45*deep)*1e-3;
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
      +2.302585*(fromMiddle>0?-.0092:-.0079)*fromMiddle)*std::pow(kept,-steeper);
    k.hammerSeconds=65e-6*std::exp((fromMiddle>0?-.066:-.0141)*fromMiddle);
    k.strike=clamp(throughThree(i,.12,.12,.0625),.05,.125);
    // The string's own losses, without the bridge's: the fundamental's,
    // slow at the bottom and faster up the keyboard; what each kHz above the
    // fundamental adds, hardly anything in the long bass strings; and a
    // term with the square of frequency, which only the top partials feel.
    // The first two are fitted, with the bridge's hold on the strings and
    // the sideways motion below, to how twelve Steinway notes die away over
    // six seconds, whole and at their fundamental
    // (Tools/compare_model_notes.py).
    k.loss1=.12*std::exp(.013*i);
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
      // decay is over (Weinreich, JASA 62, 1977). Fitted with the losses.
      k.across[j]=static_cast<float>(.97*(.16+.14*r.uniform()));
      k.acrossDrive[j]=static_cast<float>(.36*(.5+.5*r.uniform())*(r.uniform()<.5?-1:1));
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
      k.ratio[count]=static_cast<float>(ratio*(1+2e-4*r.symmetric()*std::min(1.,n/8.)));
      k.shape[count]=static_cast<float>(std::sin(n*pi*k.strike));
      ++count;
    }
    k.partials=count;
  }
  // The tuner's stretch: A4 at pitch, the octave under it and every octave
  // above tuned 4:2 (the upper note's second partial on the lower's fourth),
  // the bass 6:3, each on the strings' own partials (O. L. Railsback,
  // "Scale temperament as applied to piano tuning", JASA 9, 1938).
  // A pitch here is the ideal string's, which its stiffness raises to its
  // first partial: that partial is what is tuned.
  double pitch[keyCount];
  const auto partial=[&](int key,int n){return n*std::sqrt(1+t.keys[key].inharmonicity*n*n);};
  pitch[48]=440/partial(48,1);
  pitch[36]=pitch[48]*partial(48,2)/partial(36,4);
  for(int i=37;i<48;++i)pitch[i]=pitch[36]*std::pow(pitch[48]/pitch[36],(i-36)/12.);
  for(int i=49;i<keyCount;++i)pitch[i]=pitch[i-12]*partial(i-12,4)/partial(i,2);
  for(int i=35;i>=0;--i)pitch[i]=pitch[i+12]*partial(i+12,3)/partial(i,6);
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
void designBoard(Tables& t,int body){
  const Design& d=t.design;
  BoardMode all[40*40];int found=0;
  Rng r=seeded(body,777);
  for(int m=1;m<=40;++m)for(int n=1;n<=40;++n){
    const double a=(m+boardEdge)/d.boardX,b=(n+boardEdge)/d.boardY;
    const double hertz=pi/2*std::sqrt((boardStiffX*a*a*a*a+2*std::sqrt(boardStiffX*boardStiffY)*a*a*b*b+boardStiffY*b*b*b*b)/boardMass)
                       *(1+.03*r.symmetric());
    if(hertz<modesTop)all[found++]={hertz,m,n};
  }
  std::sort(all,all+found,[](const BoardMode& a,const BoardMode& b){return a.hertz<b.hertz;});
  t.modes=std::min(found,maxModes);
  t.crossover=t.modes<found?all[t.modes].hertz:modesTop;
  t.infinite=8*std::sqrt(std::sqrt(boardStiffX*boardStiffY)*boardMass);
  const double modalMass=boardMass*d.boardX*d.boardY/4;
  for(int k=0;k<t.modes;++k){
    t.modeHertz[k]=static_cast<float>(all[k].hertz);
    for(int p=0;p<points;++p){double x,y;bridgePoint(d,p,x,y);
      t.modeIn[p][k]=static_cast<float>(shapeAt(d,all[k],x,y)/(modalMass*2*pi*all[k].hertz));}
  }
  // The bridge's admittance at each key, which loads its strings:
  // Y(w) = sum of i w shape^2 / (M (wm^2 - w^2 + 2 i sm w)) over the modes,
  // and the plate's own 1 / (8 sqrt(D m)) above them. The strings' decay is
  // 2 f0 Z0 Re Y each (Weinreich 1977). A mode right under a partial would
  // drain it at once and a node would never: both are held within what a
  // bridge, which spreads the string's force along its length, allows.
  for(int i=0;i<keyCount;++i){KeyData& key=t.keys[i];
    double x,y;bridgePoint(d,key.bridge,x,y);
    for(int n=0;n<key.partials;++n){
      const double hertz=key.hertz*key.ratio[n],w=2*pi*hertz;
      std::complex<double> Y=0;
      for(int k=0;k<t.modes;++k){const double wm=2*pi*all[k].hertz,sm=pi*all[k].hertz*boardLoss;
        const double s=shapeAt(d,all[k],x,y);
        Y+=std::complex<double>(0,w)*s*s/(modalMass*std::complex<double>(wm*wm-w*w,2*sm*w));}
      const double above=hertz*hertz/(hertz*hertz+t.crossover*t.crossover);
      Y+=above/t.infinite;
      const double unit=2*key.hertz*key.impedance/t.infinite;
      const std::complex<double> c=2*key.hertz*key.impedance*Y;
      // How firmly the bridge holds the strings against the plate's own
      // admittance: more up the keyboard, fitted with the losses, and from
      // D#3 to D6 down to 0.3 of that, fitted to how the Salamander grand's
      // notes die away (its treble's partials fell 10 dB/s out of step with
      // the full hold, 6 with this; a hold of 0.15 or 0.5 was further off).
      const double stiff=1.12*std::exp((i-44)/44.)/(1+.095*std::pow(i/87.,3))*(1-.7*clamp((i-30)/35.,0,1));
      // The plate's single modes would let one key die four times as fast as
      // its neighbour; a bridge and its ribs even that out, so a key keeps
      // within about a third of the infinite plate's value.
      key.couplingRe[n]=static_cast<float>(stiff*clamp(c.real(),.7*unit,1.5*unit));
      key.couplingIm[n]=static_cast<float>(stiff*clamp(c.imag(),-unit,unit));
    }
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
  const auto binHertz=[](int bin){return 20*std::pow(2.,bin/static_cast<double>(octave));};
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
        const double octaves=(other-bin)/static_cast<double>(octave),w=std::exp(-octaves*octaves/(2*.3*.3));total+=w*raw[other];weight+=w;}
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
    double total=0;
    constexpr int directions=48;
    for(int i=0;i<directions;++i){
      const double z=(i+.5)/directions,rho=std::sqrt(1-z*z),turn=i*2.39996323;
      const double ux=wave*rho*std::cos(turn),uy=wave*rho*std::sin(turn);
      std::complex<double> across=0,along=0;
      for(int a=0;a<nx;++a)across+=turned(std::sin(mode.m*pi*(a+.5)/nx),ux*d.boardX*(a+.5)/nx);
      for(int b=0;b<ny;++b)along+=turned(std::sin(mode.n*pi*(b+.5)/ny),uy*d.boardY*(b+.5)/ny);
      total+=std::norm(across*along)/directions;}
    const double w=2*pi*mode.hertz;
    power[k]=total*std::pow(w*w*d.boardX*d.boardY/(nx*ny)*mode.hertz,2)/(mode.hertz*mode.hertz+d.dipoleHertz*d.dipoleHertz);
  }
  // What each pair hears of the patch at each point of the bridge, against
  // the points' mean.
  double patch[micCount][points],patchMean[micCount];
  for(int mic=0;mic<micCount;++mic){const MicSpec& spec=t.mic[mic];
    patchMean[mic]=0;
    for(int p=0;p<points;++p){patch[mic][p]=0;
      for(int ch=0;ch<2;++ch){
        const auto add=[&](HfTap tap,double g){patch[mic][p]+=g*g*tap.gain*tap.gain/2;};
        add(t.hfDirect[mic][ch][p],1);add(t.hfFloor[mic][ch][p],spec.floor);add(t.hfLid[lidStops-1][mic][ch][p],spec.lid);
        for(int e=0;e<2;++e)add(t.hfDiffuse[mic][ch][p][e],1);}
      patchMean[mic]+=patch[mic][p]/points;}
    for(int p=0;p<points;++p)patch[mic][p]/=patchMean[mic];
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
    // An engineer moves a pair until it sums to mono: no mode reaches the
    // right microphone more than 70 degrees out of step with the left, or
    // than half the pair's spacing in wavelengths where that is more, up to
    // the quarter turn past which a mode starts to cancel in the sum. So a
    // spaced pair opens from 70 to 90 degrees (between 220 and 280 Hz for a
    // grand's close pair) and a coincident one is held at 70 throughout.
    // Set against how alike the Salamander grand's two channels are in
    // forte notes from 500 Hz to 2 kHz: 0.05 on average over the keyboard,
    // where 70 degrees at every frequency (2.0.0) left 0.6 and this leaves
    // 0.4. Without the quarter turn the notes came closer still, and a
    // phrase through the distant pair summed out of phase (-0.3).
    const double spacing=norm(spec.position[0]-spec.position[1]);
    for(int k=0;k<t.modes;++k){
      const double pairTurn=std::min(pi/2,std::max(70*pi/180,pi*all[k].hertz*spacing/soundSpeed));
      const std::complex<double> l(heard[0][0][k],-heard[0][1][k]),r(heard[1][0][k],-heard[1][1][k]);
      const double apart=std::arg(r*std::conj(l));
      if(std::abs(apart)<=pairTurn)continue;
      const double turn=(apart>0?pairTurn:-pairTurn)-apart,c=std::cos(turn),sn=std::sin(turn);
      const auto rotate=[&](float (*gain)[maxModes]){const float a=gain[0][k],b=gain[1][k];
        gain[0][k]=static_cast<float>(a*c+b*sn);gain[1][k]=static_cast<float>(b*c-a*sn);};
      rotate(t.direct[mic][1]);rotate(t.floor[mic][1]);rotate(t.diffuse[mic][1]);
      for(int stop=0;stop<lidStops;++stop)rotate(t.lid[stop][mic][1]);
      const double a=heard[1][0][k],b=heard[1][1][k];heard[1][0][k]=a*c+b*sn;heard[1][1][k]=b*c-a*sn;
    }
    // A board answers each frequency in its own way, so one key's partials
    // come out stronger than its neighbour's: each key's level in this pair
    // against what the even board would give it, from its lowest partials
    // weighed as a blow drives them. The mix sets each key's pull by it.
    t.micLevel[mic]=static_cast<float>(anchor[mic]);
    for(int i=0;i<keyCount;++i){const KeyData& key=t.keys[i];
      const int p=std::min(points-2,static_cast<int>(key.bridge));const double b=key.bridge-p;
      double got=0,even=0;
      for(int n=0;n<std::min(key.partials,24);++n){
        const double hertz=key.hertz*key.ratio[n],w=2*pi*hertz;
        // A blow's force on the bridge falls about 12 dB an octave over
        // 330 Hz (this model's hammers at mezzo forte, C2 to C6).
        const double weight=key.shape[n]*key.shape[n]/(1+std::pow(hertz/330,4));
        even+=weight*radiated(hertz);
        if(hertz>.9*t.crossover){got+=weight*radiated(hertz)*mix(patch[mic][p],patch[mic][p+1],b);continue;}
        double norm=0;
        for(int ch=0;ch<2;++ch){std::complex<double> H=0;
          for(int k=0;k<t.modes;++k){const double wk=2*pi*all[k].hertz;const std::complex<double> s(pi*all[k].hertz*boardLoss,w);
            H+=mix(t.modeIn[p][k],t.modeIn[p+1][k],b)*(heard[ch][0][k]*s+heard[ch][1][k]*wk)/(s*s+wk*wk);}
          norm+=std::norm(H)/2;}
        got+=weight*norm/anchor[mic];
      }
      t.keyLevel[mic][i]=static_cast<float>(got/even);
    }
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
  alignas(32) float re[planeFloats]{},im[planeFloats]{};
  alignas(32) float turnRe[planeFloats]{},turnIm[planeFloats]{}; // the step: rotation times loss
  alignas(32) float cosine[planeFloats]{},sine[planeFloats]{};
  alignas(32) float drive[planeFloats]{};   // displacement per newton of hammer force, per sample
  alignas(32) float couplingRe[maxK]{},couplingIm[maxK]{}; // per sample
  alignas(32) float bridge[maxK]{};         // newtons on the bridge per metre
  alignas(32) float open[maxK]{},damped[maxK]{}; // the loss per sample, damper off and on
  alignas(32) float tension[maxK]{};        // the longitudinal force's share
  alignas(32) float force[chunk]{};
  float floor2=0;            // the squared bridge force under which a partial is let go
};
// A hammer against its string, from contact until it has left.
struct Contact {
  bool active=false;
  int key=0,partials=0,age=0;
  double position=0,velocity=0,mass=0,relaxed=0,prompt=0,exponent=0,previous=0,deepest=0;
  double give=0;             // the string's yielding at the hammer within a step, m/N
  alignas(32) float re[maxK]{},im[maxK]{},turnRe[maxK]{},turnIm[maxK]{},drive[maxK]{},shape[maxK]{};
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
  alignas(32) float bankRe[keyCount*bankSlots]{},bankIm[keyCount*bankSlots]{};
  alignas(32) float bankTurnRe[keyCount*bankSlots]{},bankTurnIm[keyCount*bankSlots]{};
  alignas(32) float bankCos[keyCount*bankSlots]{},bankSin[keyCount*bankSlots]{};
  alignas(32) float bankIn[keyCount*bankSlots]{},bankOut[keyCount*bankSlots]{};
  alignas(32) float bankOpen[keyCount*bankSlots]{},bankDamped[keyCount*bankSlots]{};
  float bankDamper[keyCount]{},bankApplied[keyCount]{};
  bool bankAwake[keyCount]{};float bankEnergy[keyCount]{};
  int bankPoint[keyCount]{};float bankMix[keyCount]{};
  double travel[points]{};   // the bridge's displacement at each point
  double travelLeak=1,mobility=0;

  // The soundboard.
  int modes=0;
  alignas(32) float boardRe[maxModes]{},boardIm[maxModes]{},boardTurnRe[maxModes]{},boardTurnIm[maxModes]{};
  alignas(32) float boardIn[points][maxModes]{};
  alignas(32) float outNow[4][2][maxModes]{},outGoal[4][2][maxModes]{}; // left, right, room left, room right
  bool outMoving=false;
  // Above the modes: each point's force, high-passed, delayed to each
  // microphone.
  struct Tap {int point,delay;float gain;};
  Biquad highpass[points][3];   // two high-pass stages and the radiation's fall
  static constexpr int lineSize=8192;
  float line[points][lineSize]{};
  int lineAt=0;
  Tap taps[4][points*hfTapsPerPoint*micCount]{};int tapCount[4]{};
  float roomSend=0;
  float voicing[keyCount]{};   // each key's pull on the board, evened for the mix

  // The room: a feedback delay network (J.-M. Jot and A. Chaigne, "Digital
  // delay networks for designing artificial reverberators", AES 90th
  // Convention, 1991) of eight lines under a Householder reflection.
  static constexpr int roomSize=16384;
  float roomLine[roomLines][roomSize]{};
  int roomDelay[roomLines]{},roomAt=0;
  float roomGain[roomLines]{},roomDamp[roomLines]{},roomState[roomLines]{};
  double dcL=0,dcR=0,dcInL=0,dcInR=0,dcPole=0;
  double frame[2]{},framePole=0; // the frame's knock, twice smoothed, newtons
  bool frameRings=false;         // through this chunk: decided at its boundary, or by a blow in it

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
    // The bridge gives under the strings and so moves their pitch, by up to
    // 2.4 cents where a mode of the board lies near (each step turns a
    // partial by its angle less the unison's coupling, renderChunk). A tuner
    // tunes what sounds: the key's first partial is set where it is heard.
    const double ideal=key.hertz*tuningRatio(key),angle=2*pi*ideal*key.ratio[0]/sampleRate;
    const double pulled=-key.strings*(key.couplingIm[0]*std::cos(angle)-key.couplingRe[0]*std::sin(angle))/sampleRate;
    const double f0=ideal*angle/(angle+pulled);
    v.strings=key.strings;
    int count=key.partials;
    while(count>1&&f0*key.ratio[count-1]>.45*sampleRate)--count;
    v.partials=count;
    v.apart=key.strings>1?std::min(count,maxKv):0;
    v.across=std::min(count,maxKh);
    v.longitudinal=index<52?std::min(count,maxKl):0;
    v.point=std::min(points-2,static_cast<int>(key.bridge));v.pointMix=static_cast<float>(key.bridge-v.point);
    // Unison spread: at Detune 1 a deviation of 6 cents; false beats grow
    // with the strings' age.
    const double spread=6*controls.detune*controls.detune+.15,split=1e-4*(1+7*controls.age);
    for(int plane=0;plane<6;++plane){
      const int string=plane%3;const bool isAcross=plane>=3;
      const int n=plane==0?count:isAcross?(string<v.strings?v.across:0):(string<v.strings?v.apart:0);
      const double cents=spread*key.detune[string];
      const double apart=std::pow(2.,cents/1200.)*(isAcross?1+split*key.polarisation[string]:1);
      v.u[plane]=isAcross?key.across[string]:1;
      const int o=planeStart[plane];
      for(int k=0;k<n;++k){
        // The partials the strings play together sit at the unison's pitch.
        const double tuned=plane==0&&k>=v.apart&&v.strings>1?1:apart;
        turnOf(2*pi*f0*key.ratio[k]*tuned/sampleRate,v.cosine[o+k],v.sine[o+k]);
      }
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
      // Above `apart` plane 0 is the strings' sum: together they load the
      // bridge once each.
      const double together=k>=v.apart&&v.strings>1?v.strings:1;
      v.couplingRe[k]=static_cast<float>(key.couplingRe[k]*together/sampleRate);
      v.couplingIm[k]=static_cast<float>(key.couplingIm[k]*together/sampleRate);
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
  void startContact(int index,float velocity,float soft) noexcept {
    const KeyData& key=table->keys[index];
    Contact& c=claimContact();
    const Voice& v=voices[index];
    const double f0=key.hertz*tuningRatio(key),rate=sampleRate*substeps;
    c.active=true;c.key=index;c.age=0;c.partials=v.partials;c.give=0;
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
      if((c.velocity<0&&c.position<-2*c.deepest-1e-5)||c.age>sampleRate*.08){c.active=false;break;}
    }
  }
  void play(Voice& v,float* out,int frames) noexcept {
    alignas(32) float sumRe[maxK],sumIm[maxK],stretch[maxKl];
    const int n=v.sounding;
    const int lengths[6]{planeLength(v,0),planeLength(v,1),planeLength(v,2),planeLength(v,3),planeLength(v,4),planeLength(v,5)};
    for(int s=0;s<frames;++s){
      const float force=v.forcing?v.force[s]:0;
      for(int k=0;k<n;++k){sumRe[k]=v.re[k];sumIm[k]=v.im[k];}
      for(int plane=1;plane<3;++plane){const int len=lengths[plane],o=planeStart[plane];
        for(int k=0;k<len;++k){sumRe[k]+=v.re[o+k];sumIm[k]+=v.im[o+k];}}
      float pull=dot(v.bridge,sumIm,n);
      for(int plane=3;plane<6;++plane)pull+=v.u[plane]*dot(v.bridge,v.im+planeStart[plane],lengths[plane]);
      const int longitudinal=std::min(n,v.longitudinal);
      for(int k=0;k<longitudinal;++k)stretch[k]=v.re[k]*v.re[k]-v.im[k]*v.im[k];
      out[s]=pull+dot(v.tension,stretch,longitudinal);
      // The bridge gives under the strings' sum and takes from each.
      for(int k=0;k<n;++k){
        const float cr=v.couplingRe[k]*sumRe[k]-v.couplingIm[k]*sumIm[k];
        sumIm[k]=v.couplingRe[k]*sumIm[k]+v.couplingIm[k]*sumRe[k];sumRe[k]=cr;
      }
      for(int plane=0;plane<6;++plane){const int len=lengths[plane],o=planeStart[plane];const float u=plane<3?1.f:0.f;
        float* re=v.re+o;float* im=v.im+o;const float* tr=v.turnRe+o;const float* ti=v.turnIm+o;const float* drive=v.drive+o;
        for(int k=0;k<len;++k){
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
  float damperGoal(int index) const noexcept {
    if(index>=table->design.undamped||held[index])return muted();
    // The dampers start to clear the strings a fifth of the way down and
    // are off them at three quarters. Felt presses harder the further it is
    // let down, so its loss grows as the square of the way: the last third
    // of the lift is the half pedal, where the strings ring on, shortened.
    const double on=1-clamp((pedal-.2)/.55,0,1);
    return std::max(muted(),static_cast<float>(on*on));
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
      for(int slot=0;slot<bankSlots;++slot){const int at=i*bankSlots+slot;
        const bool isDuplex=slot>=bankPartials;
        double hertz,loss,damper,drive,pull;
        if(!isDuplex){
          if(slot>=key.partials||still*key.ratio[slot]>.45*sampleRate){bankIn[at]=bankOut[at]=0;bankCos[at]=1;bankSin[at]=0;bankOpen[at]=bankDamped[at]=0;continue;}
          hertz=still*key.ratio[slot];const double w=2*pi*hertz;
          // The strings of the unison move together here: one mode for all,
          // loading the bridge once each.
          loss=stringLoss(key,w)+key.strings*key.couplingRe[slot];
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
      }
    }
  }
  void tuneBoard() noexcept {
    const Tables& t=*table;modes=t.modes;
    const double loss=boardLoss*std::pow(2.,1-2*controls.soundboard);
    for(int k=0;k<modes;++k){const double hertz=t.modeHertz[k],w=2*pi*hertz/sampleRate,g=std::exp(-pi*hertz*loss/sampleRate);
      boardTurnRe[k]=static_cast<float>(std::cos(w)*g);boardTurnIm[k]=static_cast<float>(std::sin(w)*g);
      for(int p=0;p<points;++p)boardIn[p][k]=static_cast<float>(t.modeIn[p][k]/sampleRate);}
    for(int p=0;p<points;++p){for(int stage=0;stage<2;++stage){
      // A fourth-order high-pass at the modes' top.
      const double q=stage?1.3066:.5412,w0=2*pi*t.crossover/sampleRate,alpha=std::sin(w0)/(2*q),c=std::cos(w0),a0=1+alpha;
      Biquad& b=highpass[p][stage];
      b.b0=(1+c)/2/a0;b.b1=-(1+c)/a0;b.b2=(1+c)/2/a0;b.a1=-2*c/a0;b.a2=(1-alpha)/a0;
    }
      const double pole=std::exp(-2*pi*std::min(.45*sampleRate,radiationCorner)/sampleRate);
      Biquad& fall=highpass[p][2];fall.b0=1-pole;fall.b1=fall.b2=fall.a2=0;fall.a1=-pole;}
  }
  // Each microphone's share of every mode and of the bridge's direct sound,
  // for the lid and the levels as they are.
  void mixMics() noexcept {
    const Tables& t=*table;
    const double lid=clamp(controls.lid,0,1);
    const double at=lid*(lidStops-1);const int stop=std::min(lidStops-2,static_cast<int>(at));const double between=at-stop;
    for(int out=0;out<4;++out){std::memset(outGoal[out],0,sizeof(outGoal[out]));tapCount[out]=0;}
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
            const auto add=[&](HfTap tap,double g){
              if(tap.gain==0||g==0)return;
              const int delay=std::min(lineSize-1,static_cast<int>(tap.seconds*sampleRate+.5));
              taps[out][tapCount[out]++]={p,delay,static_cast<float>(g*tap.gain)};};
            add(t.hfDirect[mic][ch][p],gain*(1-.85*shut));
            add(t.hfFloor[mic][ch][p],gain*spec.floor);
            add(t.hfLid[stop][mic][ch][p],gain*spec.lid*(1-between));
            add(t.hfLid[stop+1][mic][ch][p],gain*spec.lid*between);
            for(int e=0;e<2;++e)add(t.hfDiffuse[mic][ch][p][e],gain*(1-.85*shut));
          }
        }
      }
    }
    roomSend=static_cast<float>(send*2*clamp(controls.room,0,1));
    // The scale is voiced for what is heard: no key more than 6 dB.
    for(int i=0;i<keyCount;++i){double got=0,even=0;
      for(int mic=0;mic<micCount;++mic){const double power=controls.mic[mic]*controls.mic[mic];
        got+=power*t.keyLevel[mic][i];even+=power;}
      voicing[i]=even>0?static_cast<float>(clamp(std::sqrt(even/got),.5,2)):1;}
    // What sounds glides to the new mix; silence takes it at once.
    outMoving=!quiet;
    if(quiet)for(int out=0;out<4;++out)std::memcpy(outNow[out],outGoal[out],sizeof(outNow[out]));
  }
  void prepareRoom() noexcept {
    // Line lengths spread over 21 to 66 ms; the room falls 60 dB in 0.8 s,
    // its top in half that.
    constexpr double seconds[roomLines]{.0211,.0253,.0309,.0361,.0425,.0495,.0573,.0663};
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
    std::memset(line,0,sizeof(line));std::memset(roomLine,0,sizeof(roomLine));std::memset(roomState,0,sizeof(roomState));
    for(auto& point:highpass)for(auto& stage:point)stage.z1=stage.z2=0;
    for(double& x:travel)x=0;
    for(float& x:knocks)x=0;
    frame[0]=frame[1]=0;frameRings=false;
    for(int i=0;i<keyCount;++i){bankAwake[i]=false;bankEnergy[i]=0;}
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
    for(int i=0;i<keyCount;++i){bankDamper[i]=damperGoal(i);bankApplied[i]=-1;}
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
      const bool was=bankAwake[i];
      bankAwake[i]=bankEnergy[i]>chunk*1e-14f;bankEnergy[i]=0;
      if(was&&!bankAwake[i]&&bankDamper[i]>=1)for(int k=0;k<bankSlots;++k)bankRe[i*bankSlots+k]=bankIm[i*bankSlots+k]=0;
    }
    for(const auto& c:contacts)sounding=sounding||c.active;
    frameRings=frame[0]*frame[0]+frame[1]*frame[1]>1e-12;
    if(outMoving){float furthest=0;
      for(int out=0;out<4;++out)for(int part=0;part<2;++part)for(int k=0;k<modes;++k){
        float& now=outNow[out][part][k];const float step=(outGoal[out][part][k]-now)*.25f;now+=step;furthest=std::max(furthest,std::abs(step));}
      if(furthest<1e-9f){for(int out=0;out<4;++out)std::memcpy(outNow[out],outGoal[out],sizeof(outNow[out]));outMoving=false;}}
    for(double& x:travel)if(std::abs(x)<still)x=0;
    for(int k=0;k<modes;++k)if(std::abs(boardRe[k])+std::abs(boardIm[k])<still)boardRe[k]=boardIm[k]=0;
    for(auto& point:highpass)for(auto& stage:point){if(std::abs(stage.z1)<still)stage.z1=0;if(std::abs(stage.z2)<still)stage.z2=0;}
    for(float& x:roomState)if(std::abs(x)<still)x=0;
    quietChunks=sounding||loud>1e-9f?0:quietChunks+1;loud=0;
    // Two seconds of nothing: everything left is put to rest.
    if(quietChunks*chunk>2*sampleRate){
      std::memset(boardRe,0,sizeof(boardRe));std::memset(boardIm,0,sizeof(boardIm));
      std::memset(bankRe,0,sizeof(bankRe));std::memset(bankIm,0,sizeof(bankIm));
      std::memset(line,0,sizeof(line));std::memset(roomLine,0,sizeof(roomLine));std::memset(roomState,0,sizeof(roomState));
      for(double& x:travel)x=0;
      for(auto& point:highpass)for(auto& stage:point)stage.z1=stage.z2=0;
      for(int i=0;i<keyCount;++i){bankAwake[i]=false;bankEnergy[i]=0;}
      dcL=dcR=dcInL=dcInR=0;rest();}
  }
  void renderChunk(float* left,float* right,int frames) noexcept {
    alignas(32) float struck[points][chunk],answered[points][chunk],each[chunk];
    std::memset(struck,0,sizeof(struck));std::memset(answered,0,sizeof(answered));
    for(auto& c:contacts)if(c.active)runContact(c,frames);
    for(int p=0;p<points;++p){struck[p][0]=knocks[p];knocks[p]=0;}
    alignas(32) float blow[chunk]{};
    for(int i=0;i<keyCount;++i){Voice& v=voices[i];
      if(!v.active)continue;
      if(v.forcing){const float near=static_cast<float>((1-table->keys[i].strike)*v.strings);
        for(int s=0;s<frames;++s)blow[s]+=near*v.force[s];
        frameRings=true;}
      play(v,each,frames);
      const float b=v.pointMix*voicing[i],a=voicing[i]-b;
      for(int s=0;s<frames;++s){struck[v.point][s]+=a*each[s];struck[v.point+1][s]+=b*each[s];}
      if(v.forcing){bool still=false;for(const auto& c:contacts)still=still||(c.active&&c.key==i);
        std::memset(v.force,0,sizeof(v.force));v.forcing=still;}
    }
    if(frameRings)for(int s=0;s<frames;++s){
      frame[0]+=framePole*(blow[s]-frame[0]);frame[1]+=framePole*(frame[0]-frame[1]);
      const float knock=static_cast<float>(frameShare/points*(frame[0]-frame[1]));
      for(int p=0;p<points;++p)struck[p][s]+=knock;}
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
        bankApplied[i]=d;}
      // A sounding key's own strings are its voice's.
      const bool own=voices[i].active;
      const int p=bankPoint[i];const float b=bankMix[i],a=1-b;
      float energy=0;
      // The key's modes out of the arrays for the chunk, where the compiler
      // can keep them in registers and take them four at a time.
      alignas(16) float re[bankSlots],im[bankSlots],turnRe[bankSlots],turnIm[bankSlots],in[bankSlots],out[bankSlots];
      for(int k=0;k<bankSlots;++k){re[k]=bankRe[o+k];im[k]=bankIm[o+k];turnRe[k]=bankTurnRe[o+k];turnIm[k]=bankTurnIm[o+k];
        in[k]=bankIn[o+k];out[k]=bankOut[o+k];}
      for(int s=0;s<frames;++s){
        const float x=own?0:a*moved[p][s]+b*moved[p+1][s];
        for(int k=0;k<bankSlots;++k){
          const float r=turnRe[k]*re[k]-turnIm[k]*im[k]+in[k]*x;
          im[k]=turnIm[k]*re[k]+turnRe[k]*im[k];re[k]=r;
        }
        const float pull=dot(out,im,bankSlots);
        answered[p][s]+=a*pull;answered[p+1][s]+=b*pull;energy+=pull*pull;
      }
      for(int k=0;k<bankSlots;++k){bankRe[o+k]=re[k];bankIm[o+k]=im[k];}
      bankEnergy[i]+=energy;
    }
    // The board, and above its modes the bridge's own radiation.
    alignas(32) float in[maxModes];
    const int mask=lineSize-1,roomMask=roomSize-1;
    for(int s=0;s<frames;++s){
      for(int k=0;k<modes;++k)in[k]=0;
      for(int p=0;p<points;++p){
        const float force=struck[p][s]+answered[p][s];
        line[p][lineAt]=static_cast<float>(highpass[p][2].run(highpass[p][1].run(highpass[p][0].run(force))));
        if(force==0)continue;
        const float* gain=boardIn[p];
        for(int k=0;k<modes;++k)in[k]+=gain[k]*force;
      }
      for(int k=0;k<modes;++k){
        const float re=boardTurnRe[k]*boardRe[k]-boardTurnIm[k]*boardIm[k]+in[k];
        boardIm[k]=boardTurnIm[k]*boardRe[k]+boardTurnRe[k]*boardIm[k];boardRe[k]=re;
      }
      float o[4];
      for(int out=0;out<4;++out){const Tap* tap=taps[out];
        float sum=dot(outNow[out][0],boardRe,modes)+dot(outNow[out][1],boardIm,modes);
        for(int k=0;k<tapCount[out];++k)sum+=tap[k].gain*line[tap[k].point][(lineAt-tap[k].delay)&mask];
        o[out]=sum;}
      lineAt=(lineAt+1)&mask;
      // The room.
      float back[roomLines],total=0;
      for(int k=0;k<roomLines;++k){
        const float x=roomLine[k][(roomAt-roomDelay[k])&roomMask];
        roomState[k]+=roomDamp[k]*(x-roomState[k]);back[k]=roomState[k]*roomGain[k];total+=back[k];}
      total*=2.f/roomLines;
      float roomL=0,roomR=0;
      for(int k=0;k<roomLines;++k){
        roomLine[k][roomAt]=back[k]-total+((k&1)?o[3]:o[2])*((k&2)?-.5f:.5f);
        if(k&1)roomR+=(k&4)?-back[k]:back[k];else roomL+=(k&4)?-back[k]:back[k];}
      roomAt=(roomAt+1)&roomMask;
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

Piano::Piano():impl(new Impl){prepare(48000);}
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
  p.framePole=1-std::exp(-2*pi*frameHertz/p.sampleRate);
  p.prepareRoom();
  p.select();
  reset();
}
void Piano::reset() noexcept {
  auto& p=*impl;p.pedal=0;for(bool& h:p.held)h=false;p.silence();
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
  if(c.tuning!=old.tuning||c.stretch!=old.stretch||c.age!=old.age||c.sympathetic!=old.sympathetic||c.duplex!=old.duplex)p.tuneBank();
  // What sounds follows the tuner at the next boundary.
  if(c.tuning!=old.tuning||c.stretch!=old.stretch||c.detune!=old.detune)p.retune=!p.quiet;
  bool mics=c.lid!=old.lid||c.room!=old.room;
  for(int m=0;m<micCount;++m)mics=mics||c.mic[m]!=old.mic[m];
  if(mics)p.mixMics();
}
void Piano::strike(int key,float velocity,float soft) noexcept {
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
  p.startContact(key,clampf(velocity,0,1),clampf(soft,0,1));
}
void Piano::holdDamper(int key,bool held) noexcept {if(key>=0&&key<keyCount)impl->held[key]=held;}
void Piano::setPedal(float travel) noexcept {impl->pedal=clampf(travel,0,1);}
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
Piano::KeyReport Piano::report(Body body,int key) const noexcept {
  const KeyData& k=impl->tables[static_cast<int>(body)].keys[std::max(0,std::min(keyCount-1,key))];
  return {k.strings,k.partials,k.hertz,k.length,k.tension,k.inharmonicity,k.stretchCents,k.hammerMass};
}
}}
