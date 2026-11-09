// The recording room (Tools/fit_room.py, MeasuredRoom.h; the room's network
// in KeyraEngine.cpp). Its network decays in each band at the rate its shelf
// is designed for, at every rate the engine runs at, with the same energy;
// a build plays the soundboard's room, and a mix of soundboards the rooms
// between them. Room scales the room alone; the host's blocks do not change
// it; reset() and sleep leave nothing of it behind, so that a strike after
// silence sounds the same however long the silence was.
#include <algorithm>
#include <cmath>
#include <complex>
#include <iostream>
#include <vector>
#include "DSP/KeyraEngine.cpp"

namespace keyra {
struct RoomTestObserver {
  static Engine::Impl& state(Engine& engine) noexcept {return *engine.impl;}
};
}

namespace {
int failures=0;
void check(bool condition,const char* message){if(!condition){std::cerr<<"FAIL: "<<message<<'\n';++failures;}}
const keyra::measured::Room& roomOf(keyra::Piano piano){return keyra::rooms[static_cast<int>(piano)];}
// The network's response to a unit input at sample 0, left channel then right.
std::vector<double> response(keyra::Engine& engine,double seconds,std::vector<double>* right=nullptr){
  auto& impl=keyra::RoomTestObserver::state(engine);
  impl.silenceRoom();impl.roomSounding=true;
  std::vector<double> left;
  const int frames=static_cast<int>(seconds*impl.sampleRate);
  for(int done=0;done<frames;done+=keyra::chunk){
    std::fill(impl.roomInput.begin(),impl.roomInput.end(),0.);
    if(done==0)impl.roomInput[0]=1;
    if(impl.roomSounding)impl.playRoom(keyra::chunk);
    else{std::fill(impl.roomLeft.begin(),impl.roomLeft.end(),0.);std::fill(impl.roomRight.begin(),impl.roomRight.end(),0.);}
    for(int i=0;i<keyra::chunk;++i){left.push_back(impl.roomLeft[i]);if(right)right->push_back(impl.roomRight[i]);}
  }
  return left;
}
// x's power through a second-order band-pass an octave wide around f (RBJ).
std::vector<double> bandPower(const std::vector<double>& x,double sr,double f){
  const double w=2*keyra::pi*f/sr,alpha=std::sin(w)*std::sinh(std::log(2.)/2*w/std::sin(w));
  const double a0=1+alpha,b0=alpha/a0,a1=-2*std::cos(w)/a0,a2=(1-alpha)/a0;
  std::vector<double> e(x.size());double x1=0,x2=0,y1=0,y2=0;
  for(std::size_t i=0;i<x.size();++i){const double y=b0*(x[i]-x2)-a1*y1-a2*y2;x2=x1;x1=x[i];y2=y1;y1=y;e[i]=y*y;}
  return e;
}
// The decay (dB/s) of x's energy around f: the energy left after each sample
// of its band (Schroeder's integral), and the slope of a line through it from
// 5 dB to 25 dB down.
double bandDecay(const std::vector<double>& x,double sr,double f){
  auto e=bandPower(x,sr,f);
  for(std::size_t i=x.size()-1;i-->0;)e[i]+=e[i+1];
  double st=0,sy=0,stt=0,sty=0;int n=0;
  for(std::size_t i=0;i<x.size();++i){const double db=10*std::log10(e[i]/e[0]+1e-300);
    if(db>-5||db<-25)continue;const double t=i/sr;st+=t;sy+=db;stt+=t*t;sty+=t*db;++n;}
  return -(n*sty-st*sy)/(n*stt-st*st);
}
// The rate (dB/s) the network's line of median length loses at f through its
// shelf (prepareRoom()). (A template, as the engine's state type is private
// to it.)
template<class State> double designed(const State& impl,double f){
  std::array<int,keyra::roomLines> order{};
  for(int j=0;j<keyra::roomLines;++j)order[static_cast<std::size_t>(j)]=j;
  std::sort(order.begin(),order.end(),[&](int a,int b){return impl.roomLength[static_cast<std::size_t>(a)]<impl.roomLength[static_cast<std::size_t>(b)];});
  const auto j=static_cast<std::size_t>(order[keyra::roomLines/2]);
  const auto& loss=impl.roomLoss[j];
  const std::complex<double> z=std::polar(1.,-2*keyra::pi*f/impl.sampleRate);
  return -20*std::log10(std::abs((loss.b0+loss.b1*z)/(1.+loss.a1*z)))*impl.sampleRate/impl.roomLength[j];
}
double energy(const std::vector<double>& x){double s=0;for(double v:x)s+=v*v;return s;}
std::vector<float> render(keyra::Engine& engine,int frames,int block){
  std::vector<float> out;std::vector<float> l(static_cast<std::size_t>(block)),r(static_cast<std::size_t>(block));
  for(int done=0;done<frames;done+=block){const int n=std::min(block,frames-done);
    engine.process(l.data(),r.data(),n);
    for(int i=0;i<n;++i){out.push_back(l[static_cast<std::size_t>(i)]);out.push_back(r[static_cast<std::size_t>(i)]);}}
  return out;
}
keyra::Parameters quiet(keyra::Piano piano,float room){
  // At this Output the output stage passes the strikes untouched (Tools/benchmark_recordings.py).
  keyra::Parameters p;p.build=keyra::measuredBuild(piano);p.gain=.07f;p.room=room;return p;
}
std::vector<float> strike(keyra::Piano piano,float room,int block=64){
  keyra::Engine engine(48000);engine.setParameters(quiet(piano,room));engine.setSteadyStrikesForMeasurement(true);
  engine.noteOn(48,.7f);engine.noteOn(72,.5f);
  auto out=render(engine,24000,block);engine.noteOff(48);engine.noteOff(72);
  const auto rest=render(engine,72000,block);out.insert(out.end(),rest.begin(),rest.end());
  return out;
}
}

int main(){
  using keyra::Piano;
  const Piano pianos[]{Piano::grand,Piano::upright,Piano::kawai,Piano::hamburg,Piano::newyork};
  // Each piano's room decays in each band as its shelf is designed to, at
  // the rates the engine runs at.
  for(double sr:{44100.,48000.,96000.})for(Piano piano:pianos){
    keyra::Engine engine(sr);auto& impl=keyra::RoomTestObserver::state(engine);
    engine.setParameters(quiet(piano,1));
    const auto ir=response(engine,4.);
    for(double f:{250.,1000.,4000.,12000.}){
      // A band's decay over the network's finitely many modes scatters by a
      // few per cent around its lines' (5 % at most over these cases).
      const double measured=bandDecay(ir,sr,f),want=designed(impl,f);
      if(std::abs(measured-want)>.1*want){
        std::cerr<<"rate "<<sr<<" Hz piano "<<static_cast<int>(piano)<<" band "<<f<<": "<<measured<<" dB/s, designed "<<want<<'\n';
        check(false,"the room decays at its shelf's rate in every band");
      }
    }
  }
  // The room's level in a band does not depend on the rate: its lines'
  // lengths and losses scale with it, so its energy per hertz does. (A unit
  // impulse spreads its energy over sr/2 Hz, so a band's summed energy alone
  // falls as the rate rises; times sr it is the energy per hertz.) A band's
  // energy sums the network's modes in it, about a hundred in the octave at
  // 250 Hz (0.56 modes/Hz, its lines' total length), and each rate's lines
  // are slightly different primes, so it scatters by about 1/sqrt(100),
  // 0.4 dB (0.3 dB at most over these cases).
  for(Piano piano:pianos)for(double f:{250.,2000.}){
    double db[3];int k=0;
    for(double sr:{44100.,48000.,96000.}){keyra::Engine engine(sr);engine.setParameters(quiet(piano,1));
      std::vector<double> right;const auto left=response(engine,4.,&right);
      double band=0;for(double v:bandPower(left,sr,f))band+=v;for(double v:bandPower(right,sr,f))band+=v;
      db[k++]=10*std::log10(band*sr);}
    if(std::abs(db[0]-db[1])>=.5||std::abs(db[2]-db[1])>=.5){
      std::cerr<<"piano "<<static_cast<int>(piano)<<" band "<<f<<": "<<db[0]-db[1]<<" dB at 44.1 kHz, "<<db[2]-db[1]<<" dB at 96 kHz against 48 kHz\n";
      check(false,"the room's level is the same at every rate");
    }
  }
  // The left and right outputs are uncorrelated, as the recordings' rooms
  // are above 250 Hz.
  {
    keyra::Engine engine(48000);engine.setParameters(quiet(Piano::grand,1));
    std::vector<double> right;const auto left=response(engine,2.,&right);
    double lr=0;for(std::size_t i=0;i<left.size();++i)lr+=left[i]*right[i];
    // Two independent noises' correlation over this response scatters by
    // about 0.01.
    check(std::abs(lr)/std::sqrt(energy(left)*energy(right))<.05,"the room's channels are uncorrelated");
  }
  // A measured build plays its own piano's room; a mix of soundboards the
  // rooms between them, in the log domain; the other parts choose nothing.
  {
    keyra::Engine engine(48000);auto& impl=keyra::RoomTestObserver::state(engine);
    for(Piano piano:pianos){auto p=quiet(piano,1);p.build.strings=keyra::only(Piano::grand);p.build.hammers=keyra::only(Piano::upright);
      engine.setParameters(p);const auto& want=roomOf(piano);
      check(impl.builtRoom.lowRate==want.lowRate&&impl.builtRoom.highRate==want.highRate&&impl.builtRoom.crossover==want.crossover
            &&impl.builtRoom.gain==want.gain,"a build plays its soundboard's room");}
    auto p=quiet(Piano::grand,1);p.build.soundboard=keyra::Mix{1,0,0,1,0};engine.setParameters(p);
    const auto &a=roomOf(Piano::grand),&b=roomOf(Piano::hamburg);
    const auto between=[](float x,float y){return static_cast<float>(std::sqrt(static_cast<double>(x)*y));};
    check(std::abs(impl.builtRoom.lowRate-between(a.lowRate,b.lowRate))<1e-4f*a.lowRate
          &&std::abs(impl.builtRoom.gain-between(a.gain,b.gain))<1e-4f*a.gain,"a mix of soundboards plays the rooms between them");
  }
  // Room scales the room alone: twice the room adds twice what the room adds.
  for(Piano piano:{Piano::grand,Piano::hamburg}){
    const auto none=strike(piano,0),one=strike(piano,1),two=strike(piano,2);
    double peak=0,worst=0,added=0;
    for(std::size_t i=0;i<none.size();++i){peak=std::max(peak,std::abs(static_cast<double>(none[i])));
      const double d1=static_cast<double>(one[i])-none[i],d2=static_cast<double>(two[i])-none[i];
      added=std::max(added,std::abs(d1));worst=std::max(worst,std::abs(d2-2*d1));}
    check(added>1e-4*peak,"the room adds to a strike");
    // Within the three renders' float rounding.
    check(worst<=2e-6*peak,"Room scales the room alone");
  }
  // At Room 0 nothing enters the room and it never sounds.
  {
    keyra::Engine engine(48000);auto& impl=keyra::RoomTestObserver::state(engine);engine.setParameters(quiet(Piano::hamburg,0));
    engine.noteOn(40,.9f);bool sounded=false;
    for(int k=0;k<200;++k){render(engine,480,480);sounded=sounded||impl.roomSounding;}
    check(!sounded,"at Room 0 the room stays silent");
  }
  // The host's blocks do not change it.
  for(Piano piano:{Piano::upright,Piano::newyork}){
    const auto a=strike(piano,1,1),b=strike(piano,1,37),c=strike(piano,1,512);
    check(a==b&&b==c,"the room is the same for every block size");
  }
  // A build changed while the room sounds glides its losses to the new
  // room's over 10 ms, and ends there exactly.
  {
    keyra::Engine engine(48000);auto& impl=keyra::RoomTestObserver::state(engine);engine.setParameters(quiet(Piano::grand,1));
    engine.noteOn(60,.8f);render(engine,4800,256);
    check(impl.roomSounding,"a strike sets the room sounding");
    engine.setParameters(quiet(Piano::hamburg,1));
    check(impl.roomGlide==480,"a build changed while the room sounds glides its losses");
    render(engine,960,256);
    check(impl.roomGlide==0&&impl.roomLoss[3].a1==impl.roomLossTarget[3].a1&&impl.roomLoss[3].b0==impl.roomLossTarget[3].b0,
          "the glide ends on the new room's losses exactly");
  }
  // reset() leaves nothing of the room, and once the engine falls silent the
  // room has gone quiet with it: the same strike after a second's silence
  // and after ten sounds the same.
  {
    keyra::Engine engine(48000);auto& impl=keyra::RoomTestObserver::state(engine);engine.setParameters(quiet(Piano::hamburg,1));
    engine.noteOn(36,1.f);render(engine,9600,256);engine.reset();
    bool clear=!impl.roomSounding;for(float x:impl.roomLine)clear=clear&&x==0;
    check(clear,"reset() clears the room");
    std::vector<float> after[2];
    for(int k=0;k<2;++k){
      keyra::Engine e(48000);auto& s=keyra::RoomTestObserver::state(e);e.setParameters(quiet(Piano::hamburg,1));e.setSteadyStrikesForMeasurement(true);
      e.noteOn(36,1.f);render(e,24000,256);e.noteOff(36);
      int waited=0;while(!s.sleeping&&waited<48000*120){render(e,4800,4800);waited+=4800;}
      check(s.sleeping&&!s.roomSounding,"the engine falls silent with its room");
      render(e,k==0?48000:480000,4800);
      e.noteOn(36,1.f);after[k]=render(e,24000,256);
    }
    check(after[0]==after[1],"a strike after silence does not depend on how long the silence was");
  }
  if(failures)std::cerr<<failures<<" room check(s) failed\n";else std::cout<<"room tests passed\n";
  return failures?1:0;
}
