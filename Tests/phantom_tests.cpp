// Phantom partials (Tools/fit_phantoms.py; square() in KeyraEngine.cpp).
// The square of a channel's partials holds a line at the sum and at the
// difference of every two of them and at the double of each, at the gains
// the fit measures, and after its high-pass no constant. A strike sets its
// key's gain from the strings as built; its phantom partials play while
// their power can reach the floor partials are dropped under, carry on
// through a restrike, and stop with the strings' state.
#include <array>
#include <cmath>
#include <complex>
#include <iostream>
#include <vector>
#include "DSP/KeyraEngine.cpp"

namespace keyra {
struct PhantomTestObserver {
  static Engine::Impl& state(Engine& engine) noexcept {return *engine.impl;}
};
}

namespace {
int failures=0;
void check(bool condition,const char* message){if(!condition){std::cerr<<"FAIL: "<<message<<'\n';++failures;}}
constexpr double rate=48000,twoPi=6.283185307179586;
// A line's amplitude at f in x, over a Hann window of whole cycles of f.
double amplitude(const std::vector<double>& x,double f){
  std::complex<double> sum{};double weight=0;const double n=static_cast<double>(x.size());
  for(std::size_t i=0;i<x.size();++i){const double w=.5-.5*std::cos(twoPi*(static_cast<double>(i)+.5)/n);
    sum+=w*x[i]*std::polar(1.,-twoPi*f*static_cast<double>(i)/rate);weight+=w;}
  return 2*std::abs(sum)/weight;
}
float sum(const keyra::V4& v){return keyra::lane(v,0)+keyra::lane(v,1)+keyra::lane(v,2)+keyra::lane(v,3);}
void render(keyra::Engine& engine,int frames){
  std::array<float,256> l{},r{};
  for(int done=0;done<frames;done+=256)engine.process(l.data(),r.data(),std::min(256,frames-done));
}
}

int main(){
  {
    // Two partials in the left channel, in different lanes, and a third
    // alone in the right, a chunk at a time; the phantom partials are what
    // square() adds, measured over the second half second, the high-pass
    // (the output's, 10 Hz) long settled. All lines lie on the window's 2 Hz
    // bins.
    const double a1=.3,f1=440,a2=.2,f2=1000,a3=.25,f3=700;const float gain=.1f;
    const float pole=static_cast<float>(std::exp(-twoPi*10/rate));
    keyra::Square q;
    std::array<keyra::V4,keyra::chunk> l{},r{};
    std::vector<double> left,right;
    for(int start=0;start<static_cast<int>(rate);start+=keyra::chunk){
      std::array<float,keyra::chunk> inLeft{},inRight{};
      for(int i=0;i<keyra::chunk;++i){const double t=(start+i)/rate;
        l[i]=keyra::splat(0);r[i]=keyra::splat(0);
        keyra::setLane(l[i],1,static_cast<float>(a1*std::cos(twoPi*f1*t)));
        keyra::setLane(l[i],3,static_cast<float>(a2*std::cos(twoPi*f2*t+1)));
        keyra::setLane(r[i],2,static_cast<float>(a3*std::cos(twoPi*f3*t+2)));
        inLeft[i]=sum(l[i]);inRight[i]=sum(r[i]);}
      keyra::square(q,gain,pole,l.data(),r.data(),keyra::chunk);
      if(start>=static_cast<int>(rate/2))for(int i=0;i<keyra::chunk;++i){
        left.push_back(static_cast<double>(sum(l[i]))-inLeft[i]);right.push_back(static_cast<double>(sum(r[i]))-inRight[i]);}
    }
    // The high-pass's gain at these lines is within 0.07 % of 1.
    const auto near=[](double x,double expected){return std::abs(x/expected-1)<.01;};
    check(near(amplitude(left,f1+f2),gain*a1*a2),"two partials' sum line has gain a(m) a(n)");
    check(near(amplitude(left,f2-f1),gain*a1*a2),"two partials' difference line has gain a(m) a(n)");
    check(near(amplitude(left,2*f1),gain*a1*a1/2)&&near(amplitude(left,2*f2),gain*a2*a2/2),
          "a partial's double has gain a(m)^2 / 2");
    check(near(amplitude(right,2*f3),gain*a3*a3/2),"the right channel's partial is squared in the right");
    check(amplitude(left,0)<1e-5&&amplitude(right,0)<1e-5,"the square's constant is not played");
    check(amplitude(left,f1)<1e-5&&amplitude(left,f2)<1e-5,"nothing at the partials themselves");
    check(amplitude(left,f1+f3)<1e-5&&amplitude(left,f3-f1)<1e-5&&amplitude(right,f1+f3)<1e-5
          &&amplitude(right,f1+f2)<1e-5&&amplitude(right,f2-f1)<1e-5,"the channels are squared apart");
    std::cout<<"sum_line_error="<<amplitude(left,f1+f2)/(gain*a1*a2)-1
             <<" difference_line_error="<<amplitude(left,f2-f1)/(gain*a1*a2)-1<<'\n';
  }
  {
    keyra::Engine engine(48000);
    keyra::Parameters p;p.build=keyra::measuredBuild(keyra::Piano::grand);p.mechanics=0;engine.setParameters(p);
    auto& impl=keyra::PhantomTestObserver::state(engine);
    constexpr int c5=72-21,a0=21-21;
    // A strike sets its key's gain from the strings as built, in the
    // output's units.
    engine.noteOn(72,.8f);engine.noteOn(21,.8f);
    render(engine,256);
    const double expected=keyra::keyPhantom(keyra::models[0],72)/keyra::models[0].outputScale;
    check(expected>0&&std::abs(impl.phantomGain[c5]/expected-1)<1e-6,"a strike takes its key's phantom gain from the built strings");
    check(impl.phantomOn[c5]&&impl.phantom[c5].warm,"a loud C5 on the grand plays phantom partials");
    check(impl.phantomGain[a0]==0&&!impl.phantomOn[a0]&&!impl.phantom[a0].warm,"the grand's A0 plays none");
    // A restrike carries the key's square on from where it was.
    engine.noteOn(72,.6f);
    render(engine,256);
    int voices=0;for(const auto& voice:impl.voices)voices+=voice.active&&voice.note==72;
    check(voices==2&&impl.phantomOn[c5]&&impl.phantom[c5].warm,"a restrike squares on with the strike it joins");
    // Let go, the felt damps the strings: their phantom partials stop while
    // the strings still sound, as their power falls under the floor.
    engine.noteOff(72);engine.noteOff(72);
    bool stoppedWhileSounding=false;
    for(int i=0;i<400&&!stoppedWhileSounding;++i){
      render(engine,256);
      bool sounding=false;for(const auto& voice:impl.voices)sounding=sounding||(voice.active&&voice.note==72);
      stoppedWhileSounding=sounding&&!impl.phantomOn[c5];
    }
    check(stoppedWhileSounding,"a damped key's phantom partials stop before its partials");
    engine.noteOn(72,.8f);render(engine,256);
    engine.reset();
    check(!impl.phantomOn[c5]&&!impl.phantom[c5].warm,"reset silences the phantom partials");
  }
  std::cout<<"phantom_failures="<<failures<<'\n';
  return failures?1:0;
}
