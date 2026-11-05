// The struck key's own undamped string (Tools/fit_halo_own.py,
// MeasuredHaloOwn.h; strike() and ownStringApart() in KeyraEngine.cpp).
// Where a piano's own strikes ring a key's undamped string apart from the
// key's series, the key's strike sets that string's aftersound ringing at the
// level its table gives, growing with the strike's layer at the undamped
// strings' slope, with no prompt part. Where the table gives none, or where
// the key's own series plays the string, the strike leaves it silent. Between
// two pianos of which one rings it, it plays at that piano's share of the
// hammers in power. The host's blocks do not change it.
#include <cmath>
#include <complex>
#include <iostream>
#include <vector>
#include "DSP/KeyraEngine.cpp"

namespace keyra {
struct HaloOwnTestObserver {
  static Engine::Impl& state(Engine& engine) noexcept {return *engine.impl;}
};
}

namespace {
int failures=0;
void check(bool condition,const char* message){if(!condition){std::cerr<<"FAIL: "<<message<<'\n';++failures;}}
keyra::Parameters build(keyra::Piano piano){keyra::Parameters p;p.build=keyra::measuredBuild(piano);return p;}
const keyra::Model& model(keyra::Piano piano){return keyra::models[static_cast<int>(piano)];}
double ring(const keyra::Resonator& x){return std::abs(std::complex<double>{x.q,x.p});}
bool close(double x,double y,double tolerance){return std::abs(x-y)<=tolerance*std::max(std::abs(x),std::abs(y));}
std::vector<float> render(keyra::Engine& engine,int frames,int block){
  std::vector<float> out;std::vector<float> l(static_cast<std::size_t>(block)),r(static_cast<std::size_t>(block));
  for(int done=0;done<frames;done+=block){const int n=std::min(block,frames-done);
    engine.process(l.data(),r.data(),n);
    for(int i=0;i<n;++i){out.push_back(l[static_cast<std::size_t>(i)]);out.push_back(r[static_cast<std::size_t>(i)]);}}
  return out;
}
// The aftersound a first, steady strike of `key` at layer velocity `v` sets
// its own string ringing at on piano `m`, with the pedals up.
// (A template, as the engine's state type is private to it.)
template<class State> double expected(State& impl,const keyra::Model& m,int key,double v){
  const int j=key-keyra::firstHalo;
  const double order=std::max(1.,impl.haloHz[j]/impl.builtPitch(key));
  const double layerDb=keyra::levelAt(m,m.layerLevelDb,v);
  const double db=m.haloOwnDb[j]+(m.haloSlopeDb+m.haloSlopeRiseDb*std::log2(order))*layerDb+20*std::log10(m.outputScale);
  return std::pow(10.,db/20)*impl.haloFirst[j];
}
// A fresh engine's own string of `key` after one steady strike at `velocity`.
struct Struck {double ring,prompt,expected;};
Struck strike(const keyra::Parameters& parameters,keyra::Piano piano,int key,float velocity){
  keyra::Engine engine(48000);engine.setParameters(parameters);engine.setSteadyStrikesForMeasurement(true);
  auto& impl=keyra::HaloOwnTestObserver::state(engine);
  engine.noteOn(key,velocity);
  const int j=key-keyra::firstHalo;
  return {ring(impl.haloRing[j]),ring(impl.haloPrompt[j]),expected(impl,model(piano),key,127.*velocity)};
}
}

int main(){
  using keyra::Piano;
  {
    // The grand's F#7 and A7 ring their own strings at their tables' levels,
    // at full velocity and at half, with no prompt part.
    bool level=true,prompt=true;
    for(const int key:{102,105})for(const float velocity:{1.f,.5f}){
      const auto s=strike(build(Piano::grand),Piano::grand,key,velocity);
      level=level&&s.ring>0&&close(s.ring,s.expected,1e-9);prompt=prompt&&s.prompt==0;
      std::cout<<"key="<<key<<" velocity="<<velocity<<" own="<<20*std::log10(s.ring)<<" dB expected="<<20*std::log10(s.expected)<<" dB\n";
    }
    check(level,"a key's strike rings its own string at the level its table gives");
    check(prompt,"a key's own string has no prompt part");
  }
  {
    // F#6, whose own series plays its string (the table gives none), and E7,
    // whose table holds F#7's level but whose string's pitch lies on its own
    // fundamental, leave their own strings silent.
    check(strike(build(Piano::grand),Piano::grand,90,1.f).ring==0,"a key whose table gives no own string leaves it silent");
    check(strike(build(Piano::grand),Piano::grand,100,1.f).ring==0,"a key whose own series plays its string leaves it silent");
    check(model(Piano::grand).haloOwnDb[100-keyra::firstHalo]>-200,"E7's table holds a level, which its own series overrides");
  }
  {
    // Every piano: a key whose table gives none leaves its own string
    // silent, and none sets a prompt part on it.
    bool silent=true,prompt=true;int ringing=0;
    for(const Piano piano:{Piano::grand,Piano::upright,Piano::kawai,Piano::hamburg,Piano::newyork})
      for(int key=keyra::firstHalo;key<keyra::firstHalo+keyra::halo;++key){
        const auto s=strike(build(piano),piano,key,1.f);
        if(!(model(piano).haloOwnDb[key-keyra::firstHalo]>-200))silent=silent&&s.ring==0;
        else if(s.ring>0){++ringing;silent=silent&&close(s.ring,s.expected,1e-9);}
        prompt=prompt&&s.prompt==0;
      }
    check(silent,"each piano rings a key's own string only at its table's level");
    check(prompt,"no key sets a prompt part on its own string");
    check(ringing>0,"some keys ring their own strings");
  }
  {
    // Between the grand and the upright, whose takes ring no own string, F#7
    // rings its own at the grand's level, at the grand's share of the
    // hammers in power.
    auto parameters=build(Piano::grand);parameters.build.hammers={.5f,.5f,0.f,0.f,0.f};
    const auto s=strike(parameters,Piano::grand,102,1.f);
    check(close(s.ring,s.expected*std::sqrt(.5),1e-9),"between pianos the own string plays at the share of those that ring it");
  }
  {
    // The host's blocks do not change a key's own string.
    std::vector<float> renders[2];int k=0;
    for(const int block:{64,1000}){
      keyra::Engine engine(48000);engine.setParameters(build(Piano::grand));
      engine.noteOn(102,.6f);renders[k++]=render(engine,48000,block);
    }
    check(renders[0]==renders[1],"the host's blocks do not change a key's own string");
  }
  if(failures)return 1;
  std::cout<<"halo own tests passed\n";
  return 0;
}
