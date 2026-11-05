// The undamped strings' beat (Tools/fit_halo_beats.py, MeasuredHaloBeats.h;
// assemble() and strike() in KeyraEngine.cpp). Where a piano's takes decide a
// string's beat, a strike sets its aftersound ringing as two components: the
// first at the level its beat gives against the one the halo fit gives, the
// second at its level and phase against the first and its offset above it,
// both falling at the string's rate times the beat's rate scale. A string
// whose takes decide none rings as one component at the string's own rate.
// Between pianos the second fades in power by the strings' build; a build
// whose strings stop beating lets it ring out; the unisons modifier spreads
// its offset; reset silences it; the host's blocks do not change it.
#include <cmath>
#include <complex>
#include <iostream>
#include <vector>
#include "DSP/KeyraEngine.cpp"

namespace keyra {
struct HaloBeatTestObserver {
  static Engine::Impl& state(Engine& engine) noexcept {return *engine.impl;}
};
}

namespace {
int failures=0;
void check(bool condition,const char* message){if(!condition){std::cerr<<"FAIL: "<<message<<'\n';++failures;}}
std::vector<float> render(keyra::Engine& engine,int frames,int block){
  std::vector<float> out;std::vector<float> l(static_cast<std::size_t>(block)),r(static_cast<std::size_t>(block));
  for(int done=0;done<frames;done+=block){const int n=std::min(block,frames-done);
    engine.process(l.data(),r.data(),n);
    for(int i=0;i<n;++i){out.push_back(l[static_cast<std::size_t>(i)]);out.push_back(r[static_cast<std::size_t>(i)]);}}
  return out;
}
keyra::Parameters build(keyra::Piano piano){keyra::Parameters p;p.build=keyra::measuredBuild(piano);return p;}
const keyra::Model& model(keyra::Piano piano){return keyra::models[static_cast<int>(piano)];}
bool beats(const keyra::measured::HaloBeat& b){return b.secondDb>-200;}
std::complex<double> state(const keyra::Resonator& x){return {x.q,x.p};}
bool close(double x,double y,double tolerance){return std::abs(x-y)<=tolerance*std::max(std::abs(x),std::abs(y));}
// The offset (Hz) between two resonators' rotations at 48 kHz.
double offset(const keyra::Resonator& a,const keyra::Resonator& b){
  return (std::atan2(a.s,a.c)-std::atan2(b.s,b.c))*48000/(2*keyra::pi);
}
// A key below the undamped strings, whose recorded pitches around it hold
// their levels as fitted, so that its strike sets each string's aftersound
// and prompt part ringing from one level (strike()).
constexpr int note=72;
}

int main(){
  using keyra::Piano;
  {
    // Each measured piano: a strike plays each string's beat as its table
    // gives it, and every other string as one component.
    int beating=0;
    for(const Piano piano:{Piano::grand,Piano::upright,Piano::kawai,Piano::hamburg,Piano::newyork}){
      const auto& m=model(piano);
      keyra::Engine engine(48000);engine.setParameters(build(piano));
      auto& impl=keyra::HaloBeatTestObserver::state(engine);
      engine.noteOn(note,.6f);
      bool first=true,second=true,alone=true,rates=true;
      for(int j=0;j<keyra::halo;++j){
        const auto& b=m.haloBeats[j];const auto& s=m.haloStrings[j];
        const auto ring=state(impl.haloRing[j]),prompt=state(impl.haloPrompt[j]),beat=state(impl.haloBeat[j]);
        // The prompt part takes the level the halo fit gives one component,
        // so the first stands firstDb from it as the prompt stands promptDb.
        first=first&&ring!=0.&&close(std::abs(ring/prompt),std::pow(10.,(static_cast<double>(b.firstDb)-s.promptDb)/20),1e-12)
                   &&std::abs(std::arg(ring/prompt))<1e-12;
        // The built rate is a float.
        rates=rates&&close(impl.haloString[j].rate,static_cast<double>(s.rate)*b.rateScale,1e-6)
                   &&impl.haloRing[j].decay==std::exp(-static_cast<double>(impl.haloString[j].rate)/48000)
                   &&impl.haloBeat[j].decay==impl.haloRing[j].decay;
        if(!beats(b)){alone=alone&&beat==0.&&b.rateScale==1&&b.firstDb==0;continue;}
        ++beating;
        // In the bank's turning a component's state is the conjugate of its
        // analytic amplitude, so the second over the first is conj(rho).
        const auto rho=std::polar(std::pow(10.,static_cast<double>(b.secondDb)/20),static_cast<double>(b.phase));
        second=second&&std::abs(beat/ring-std::conj(rho))<=1e-12*std::abs(rho)
                     &&std::abs(offset(impl.haloBeat[j],impl.haloRing[j])-b.splitHz)<1e-3;
        std::cout<<"piano="<<static_cast<int>(piano)<<" key="<<keyra::firstHalo+j<<" split="<<b.splitHz
                 <<" second_db="<<b.secondDb<<" rate_scale="<<b.rateScale<<'\n';
      }
      check(first,"a strike sets each undamped string's first component at its beat's level");
      check(second,"a beating string's second component plays at its level, phase and offset");
      check(alone,"a string whose takes decide no beat rings as one component");
      check(rates,"both components fall at the string's rate times the beat's scale");
    }
    check(beating>0,"some piano's strings beat");
  }
  {
    // Between the grand and the Kawai, whose strings do not beat, the second
    // component fades in power by the strings' build, at the grand's offset
    // and phase; the first's level and the rate mix as the string's do.
    const auto& grand=model(Piano::grand);const auto& kawai=model(Piano::kawai);
    auto parameters=build(Piano::grand);parameters.build.strings={.5f,0.f,.5f,0.f,0.f};
    keyra::Engine engine(48000);engine.setParameters(parameters);
    auto& impl=keyra::HaloBeatTestObserver::state(engine);
    bool mixed=true;
    for(int j=0;j<keyra::halo;++j){
      const auto& b=grand.haloBeats[j];
      const double rate=std::exp(.5*(std::log(static_cast<double>(grand.haloStrings[j].rate)*b.rateScale)
                                     +std::log(static_cast<double>(kawai.haloStrings[j].rate))));
      mixed=mixed&&close(impl.haloFirst[j],std::pow(10.,.5*b.firstDb/20),1e-12)
                 &&close(impl.haloString[j].rate,rate,1e-6);
      const std::complex<double> second{impl.haloSecond[j].re,impl.haloSecond[j].im};
      if(!beats(b)){mixed=mixed&&second==0.;continue;}
      mixed=mixed&&close(std::abs(second)/impl.haloFirst[j],std::sqrt(.5)*std::pow(10.,static_cast<double>(b.secondDb)/20),1e-12)
                 &&std::abs(std::remainder(std::arg(second)-b.phase,2*keyra::pi))<1e-12
                 &&close(impl.haloSplit[j],b.splitHz,1e-12);
    }
    check(mixed,"between pianos the second component fades in power by the strings' build");
  }
  {
    // The unisons modifier spreads the offset as it spreads a strike's: none
    // at -1, three times as far at 1.
    const auto& grand=model(Piano::grand);
    bool spread=true;
    for(const float unisons:{-1.f,1.f}){
      auto parameters=build(Piano::grand);parameters.build.unisons=unisons;
      keyra::Engine engine(48000);engine.setParameters(parameters);
      auto& impl=keyra::HaloBeatTestObserver::state(engine);
      for(int j=0;j<keyra::halo;++j)if(beats(grand.haloBeats[j]))
        spread=spread&&std::abs(offset(impl.haloBeat[j],impl.haloRing[j])-(unisons<0?0:3)*grand.haloBeats[j].splitHz)<1e-3;
    }
    check(spread,"the unisons modifier spreads a string's beat");
  }
  {
    // A build whose strings no longer beat lets a ringing second component
    // ring out at the string's rate rather than stop it.
    auto parameters=build(Piano::grand);
    keyra::Engine engine(48000);engine.setParameters(parameters);
    auto& impl=keyra::HaloBeatTestObserver::state(engine);
    engine.noteOn(note,.6f);render(engine,4800,256);
    parameters.build.strings=keyra::only(Piano::kawai);engine.setParameters(parameters);
    bool out=false;
    for(int j=0;j<keyra::halo;++j){
      const double before=std::abs(state(impl.haloBeat[j]));
      if(before==0)continue;
      render(engine,4800,256);
      out=std::abs(std::abs(state(impl.haloBeat[j]))/before-std::pow(impl.haloBeat[j].decay,4800))<1e-9;
      break;
    }
    check(out,"a second component rings out when the build's strings stop beating");
  }
  {
    // Reset silences the second components with the rest of the strings.
    keyra::Engine engine(48000);engine.setParameters(build(Piano::grand));
    auto& impl=keyra::HaloBeatTestObserver::state(engine);
    engine.noteOn(note,.6f);render(engine,4800,256);
    bool rang=false;for(const auto& x:impl.haloBeat)rang=rang||state(x)!=0.;
    engine.reset();
    bool silent=true;for(const auto& x:impl.haloBeat)silent=silent&&state(x)==0.;
    check(rang&&silent,"reset silences the strings' second components");
  }
  {
    // The host's blocks do not change a beating string.
    std::vector<float> renders[2];int k=0;
    for(const int block:{64,1000}){
      keyra::Engine engine(48000);engine.setParameters(build(Piano::grand));
      engine.noteOn(note,.6f);renders[k++]=render(engine,48000,block);
    }
    check(renders[0]==renders[1],"the host's blocks do not change the beat");
  }
  if(failures)return 1;
  std::cout<<"halo beat tests passed\n";
  return 0;
}
