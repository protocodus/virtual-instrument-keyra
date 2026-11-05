// Pitch glide (Tools/fit_glide.py; keyGlide and the chunk boundary in
// KeyraEngine.cpp). A key's strings play sharp by its piano's law times its
// partials' power: a loud bass strike on the upright starts sharp and
// settles as it decays, every partial retuned to the key's glide whenever it
// has moved by glideStep, through bends and whatever the host's blocks; a
// soft strike stays under the step and never retunes; a piano whose takes
// show no glide plays none; and reset clears it.
#include <array>
#include <cmath>
#include <iostream>
#include <vector>
#include "DSP/KeyraEngine.cpp"

namespace keyra {
struct GlideTestObserver {
  static Engine::Impl& state(Engine& engine) noexcept {return *engine.impl;}
};
}

namespace {
int failures=0;
void check(bool condition,const char* message){if(!condition){std::cerr<<"FAIL: "<<message<<'\n';++failures;}}
std::vector<float> render(keyra::Engine& engine,int frames,int block=256){
  std::vector<float> out;std::vector<float> l(static_cast<std::size_t>(block)),r(static_cast<std::size_t>(block));
  for(int done=0;done<frames;done+=block){const int n=std::min(block,frames-done);
    engine.process(l.data(),r.data(),n);
    for(int i=0;i<n;++i){out.push_back(l[static_cast<std::size_t>(i)]);out.push_back(r[static_cast<std::size_t>(i)]);}}
  return out;
}
// Impl is the engine's private state, named only through the observer.
template<class Impl> const keyra::Voice* voiceOn(const Impl& impl,int note){
  for(const auto& voice:impl.voices)if(voice.active&&voice.note==note)return &voice;
  return nullptr;
}
// Every partial of the voice turns, each sample, at its lane's frequency
// times the channel's tuning and the voice's glide, exactly as tunePartial
// sets it.
template<class Impl> bool tunedToGlide(const Impl& impl,const keyra::Voice& voice){
  const double ratio=impl.tuningRatio(voice.channel)*std::exp2(voice.glide/1200);
  for(int k=0;k<voice.count;++k){const auto& partial=voice.partials[k];
    for(int j=0;j<keyra::lanes;++j){const keyra::Complex r=impl.rotation(partial.hz[j]*ratio);
      if(partial.natural[j].re!=r.re*partial.decay[j]||partial.natural[j].im!=r.im*partial.decay[j])return false;}}
  return voice.count>0;
}
keyra::Parameters build(keyra::Piano piano){
  keyra::Parameters p;p.build=keyra::measuredBuild(piano);p.mechanics=0;return p;
}
}

int main(){
  constexpr int c2=36,key=c2-21;
  const auto& upright=keyra::models[static_cast<int>(keyra::Piano::upright)];
  check(upright.glide.cents>0,"the upright's takes show a glide (MeasuredGlide.h)");
  // A steady strike plays the layer it is given; the plug-in's hardest plays
  // the upright's loudest recorded layer.
  const float loudest=keyra::responseVelocity(keyra::Piano::upright,1.f)/127;
  {
    keyra::Engine engine(48000);engine.setParameters(build(keyra::Piano::upright));engine.setSteadyStrikesForMeasurement(true);
    auto& impl=keyra::GlideTestObserver::state(engine);
    // The strings as built take the law in the output's units: the
    // recordings' power is the output's over the square of its scale.
    const double law=keyra::keyGlide(upright,c2)/(upright.outputScale*upright.outputScale);
    check(std::abs(impl.builtGlide[key]/law-1)<1e-12,"the built upright's glide is its law in the output's units");
    engine.noteOn(c2,loudest);
    render(engine,1024);
    const keyra::Voice* voice=voiceOn(impl,c2);
    check(voice!=nullptr,"a loud C2 sounds");
    if(voice){
      const double early=voice->glide;
      check(early>=keyra::glideStep,"a loud C2 on the upright plays sharp");
      check(std::abs(impl.glideCents[key]-early)<keyra::glideStep,"its voice is within a step of its key's glide");
      check(tunedToGlide(impl,*voice),"every partial of a gliding voice is tuned to its glide");
      // A bend retunes the partials to the channel's tuning and the glide
      // together.
      engine.pitchBend(2.f);render(engine,256);
      check(tunedToGlide(impl,*voice),"a bend while gliding keeps the glide");
      engine.pitchBend(0.f);
      render(engine,3*48000);
      check(voice->active&&voice->glide<early/2,"the glide settles as the string decays");
      check(std::abs(impl.glideCents[key]-voice->glide)<keyra::glideStep&&tunedToGlide(impl,*voice),
            "a settling voice follows its key's glide");
      std::cout<<"upright_c2_glide_cents_early="<<early<<" after_3s="<<voice->glide<<'\n';
    }
    // Reset clears the glide with the strings.
    engine.reset();
    bool clear=true;for(double cents:impl.glideCents)clear=clear&&cents==0;
    check(clear,"reset clears every key's glide");
    // A soft strike stays under a step: its voice never retunes.
    engine.noteOn(c2,.1f);
    bool steady=true;
    for(int i=0;i<200;++i){render(engine,256);const keyra::Voice* soft=voiceOn(impl,c2);
      steady=steady&&soft&&soft->glide==0&&tunedToGlide(impl,*soft);}
    check(steady,"a soft C2 plays no glide");
  }
  {
    // A piano whose takes show no glide plays none, however loud.
    keyra::Engine engine(48000);engine.setParameters(build(keyra::Piano::grand));engine.setSteadyStrikesForMeasurement(true);
    auto& impl=keyra::GlideTestObserver::state(engine);
    engine.noteOn(24,1.f);engine.noteOn(c2,1.f);
    bool none=true;
    for(int i=0;i<40;++i){render(engine,256);
      for(const auto& voice:impl.voices)none=none&&(!voice.active||voice.glide==0);
      for(double cents:impl.glideCents)none=none&&cents==0;}
    check(keyra::models[static_cast<int>(keyra::Piano::grand)].glide.cents==0&&none,"the grand plays no glide");
  }
  {
    // The glide moves at chunk boundaries, so the host's blocks do not
    // change it: a loud bass chord, a bend and a restrike.
    keyra::Engine a(48000),b(48000);
    for(auto* engine:{&a,&b}){engine->setParameters(build(keyra::Piano::upright));engine->noteOn(24,1.f);engine->noteOn(c2,.9f);}
    auto outA=render(a,9600,17),outB=render(b,9600,256);
    a.pitchBend(-1.f);b.pitchBend(-1.f);a.noteOn(c2,1.f);b.noteOn(c2,1.f);
    auto tailA=render(a,24000,19),tailB=render(b,24000,128);
    check(outA==outB&&tailA==tailB,"the glide is invariant to audio block partitioning");
  }
  std::cout<<"glide_failures="<<failures<<'\n';
  return failures?1:0;
}
