#include "keyra/FullInstrument.h"
#include "keyra/physics/MechanismExciter.h"
#include "keyra/physics/StrikeController.h"
#include "SelectedModel.h"
#include "MechanismBodyCache.h"
#include <array>
#include <cmath>
#include <limits>
#include <new>
#include <utility>

namespace keyra {
namespace {
constexpr std::array<unsigned,4> bodyGroups{{1,1,1,0}};
bool validNote(int note) noexcept { return note>=21&&note<=108; }
bool unit(double value) noexcept { return std::isfinite(value)&&value>=0&&value<=1; }
bool validParameters(const FullInstrumentParameters& p) noexcept {
  return std::isfinite(p.gainDb)&&p.gainDb>=-60&&p.gainDb<=12&&
    unit(p.dynamics)&&unit(p.humanization)&&unit(p.mechanicalLevel)&&
    std::isfinite(p.stereoWidth)&&p.stereoWidth>=0&&p.stereoWidth<=2;
}
grand::Options options(double rate) noexcept {
  grand::Options result; result.sampleRate=static_cast<int>(rate); return result;
}
}

struct FullInstrument::Impl {
  std::unique_ptr<grand::Piano> model;
  FullInstrumentConfig config{};
  physics::StrikeController controller;
  std::array<physics::MechanismExciter,4> mechanisms{};
  std::array<double,88> baseHardness{},contactPlane{};
  std::array<double,2> previous{},highpass{};
  uint64_t frame=0,rejected=0,unsafe=0,bypassRequests=0,bypassLaunches=0,outputFaults=0;
  uint64_t savedBridgeFaults=0,savedContactFaults=0;
  uint32_t savedFaultFlags=0;
  physics::StrikeStatistics savedStrikes{};
  double pole=0,gain=1,velocityExponent=1;
#if defined(KEYRA_FULL_MECHANISM_CACHE) && KEYRA_FULL_MECHANISM_CACHE
  detail::MechanismBodyCache bodyCache;
#endif

  void parameters(const FullInstrumentParameters& value) noexcept {
    config.parameters=value;
    gain=value.gainDb==0?1:std::pow(10.,value.gainDb/20.);
    velocityExponent=value.dynamics==.5?1:std::exp2(2*(value.dynamics-.5));
    for (auto& source:mechanisms) source.setEnabled(value.mechanicalLevel>0);
  }
  void clearSound() noexcept {
    model->resetState();
    controller.reset();
    for (unsigned i=0;i<88;++i) {
      auto& key=model->keys[i];key.K=baseHardness[i];
      // Virgin inactive hammers begin at the controller's authored rest plane.
      // The original zero coordinate can imply contact when a vibrating string
      // passes below zero, spuriously delaying a key's first strike.
      key.hammerX=-controller.config().restDepth;
    }
    for (auto& source:mechanisms) source.reset();
#if defined(KEYRA_FULL_MECHANISM_CACHE) && KEYRA_FULL_MECHANISM_CACHE
    bodyCache.reset();
#endif
    contactPlane={}; previous={}; highpass={};
  }
  void reset() noexcept {
    clearSound(); frame=rejected=unsafe=bypassRequests=bypassLaunches=outputFaults=0;
    savedBridgeFaults=savedContactFaults=0;savedFaultFlags=0;savedStrikes={};
  }
  void retireNonfinite() noexcept {
    ++outputFaults;
    savedFaultFlags|=model->faultFlags|4u;
    savedBridgeFaults+=model->bridgeFaults;savedContactFaults+=model->contactFaults;
    const auto& s=controller.statistics();
    savedStrikes.requests+=s.requests;savedStrikes.launches+=s.launches;
    savedStrikes.deferred+=s.deferred;savedStrikes.coalesced+=s.coalesced;
    savedStrikes.cancelled+=s.cancelled;savedStrikes.expired+=s.expired;
    clearSound();
  }
  physics::HammerObservation observation(int note,bool refresh) noexcept {
    const unsigned index=static_cast<unsigned>(note-21);
    const auto& key=model->keys[index];
    if (refresh) {
      double y=0;for (int string:key.strings) y+=model->strings[string].m.displacement();
      contactPlane[index]=y;
    }
    return {key.hammerActive,key.hammerX-contactPlane[index],key.hammerV};
  }
  void liftDamper(int note) noexcept {
    auto& key=model->keys[note-21];
    key.down=true;key.damperPosition=0;key.cachedContact=0;key.cachedLoss=model->opt.loss;
    for (int index:key.strings) {
      auto& m=model->strings[index].m;
      for (size_t i=0;i<m.size();++i) m.damp[i]=std::exp(-model->opt.loss*m.loss[i]*model->dt);
    }
  }
  void trigger(unsigned index,double strength) noexcept {
    if (config.parameters.mechanicalLevel>0)
      (void)mechanisms[index].trigger(strength*config.parameters.mechanicalLevel);
  }
  bool apply(int note,const physics::StrikeLaunch& launch) noexcept {
    auto& key=model->keys[note-21];
    const auto h=observation(note,true);
    if (key.hammerActive || (controller.state(note).launches>1&&
        h.compression>-controller.config().separationMargin)) { ++unsafe;return false; }
    const double oldX=key.hammerX;
    const double human=config.parameters.humanization;
    const double velocityFactor=1+human*(launch.velocityFactor-1);
    const double hardnessFactor=1+human*(launch.hardnessFactor-1);
    key.K=baseHardness[note-21]*hardnessFactor;
    model->noteOn(note,launch.velocity*127.);
    if (launch.preserveSeparatedPosition) key.hammerX=oldX;
    key.hammerV*=velocityFactor*launch.recoveryVelocityFactor;
    trigger(1,.95*launch.velocity*launch.recoveryVelocityFactor*hardnessFactor);
    return true;
  }
  bool on(int note,double velocity) noexcept {
    if (velocity==0) return off(note);
    if (velocityExponent!=1) velocity=std::pow(velocity,velocityExponent);
    if (!config.repetitionController) {
      ++bypassRequests;
      // The bypass supports legacy comparison, but never overwrites an active
      // hammer. The normal controller queues a new request until separation.
      if (model->keys[note-21].hammerActive) { ++unsafe;return false; }
      model->keys[note-21].K=baseHardness[note-21];
      model->noteOn(note,velocity*127.);++bypassLaunches;
      trigger(0,.95*velocity);trigger(1,.95*velocity);return true;
    }
    if (!controller.request(note,velocity)) return false;
    liftDamper(note);
    const double factor=1+config.parameters.humanization*
      (controller.state(note).pendingVelocityFactor-1);
    trigger(0,.95*velocity*factor);
    const auto launch=controller.poll(note,observation(note,true),false);
    if (launch.valid) (void)apply(note,launch);
    return true;
  }
  bool off(int note) noexcept {
    const bool wasDown=model->keys[note-21].down;
    controller.release(note);model->noteOff(note);
    if (wasDown) trigger(2,.4);
    return true;
  }
  physics::MechanismBodyPort bodyPort(unsigned group) const noexcept {
    physics::MechanismBodyPort port;
    for (const auto& z:model->board) {
      port.velocity+=z.port[group]*z.w*z.p;
      port.inverseMass+=z.port[group]*z.port[group];
    }
    return port;
  }
  void bodyImpulse(unsigned group,double impulse) noexcept {
    for (auto& z:model->board) z.p+=z.port[group]*impulse/z.w;
  }
  std::array<double,2> boardObservation(const std::array<double,3>& force={}) const noexcept {
    std::array<double,2> out{};
    for (const auto& z:model->board) {
      double f=z.force;
      for (unsigned g=0;g<3;++g) f+=z.port[g]*force[g];
      const double acc=-z.w*z.w*z.q-2*z.sigma*z.w*z.p+f;
      for (unsigned ch=0;ch<2;++ch) out[ch]+=acc*z.mic[ch];
    }
    return out;
  }
  std::array<double,2> step() noexcept {
    if (config.repetitionController) {
      for (int note=21;note<=108;++note) if (controller.requiresTick(note)) {
        auto& key=model->keys[note-21];
        const auto launch=controller.poll(note,
          observation(note,key.hammerActive||controller.state(note).pending));
        if (launch.valid) (void)apply(note,launch);
        else if (!key.hammerActive&&controller.state(note).hasLaunched) {
          const auto& state=controller.state(note);
          key.hammerX=contactPlane[note-21]-state.returnDepth;
          key.hammerV=-state.returnVelocity;
        }
      }
    }
    auto out=model->step(frame);
    if (config.parameters.mechanicalLevel<=0) return out;
    // Passive reciprocal impulses are applied after the original network.
    // J/dt is added once to its acceleration observer. Sources see the body
    // state after earlier sources, including the equal/opposite reaction.
#if defined(KEYRA_FULL_MECHANISM_CACHE) && KEYRA_FULL_MECHANISM_CACHE
    bodyCache.begin(*model);
    double direct=0;bool applied=false;
    for(unsigned i=0;i<4;++i){
      const auto result=mechanisms[i].step(bodyCache.port(bodyGroups[i]));
      if(result.bodyImpulse!=0){bodyCache.add(bodyGroups[i],result.bodyImpulse);applied=true;}
      direct+=mechanisms[i].directObservation();
    }
    if(applied){const auto delta=bodyCache.finish(*model);for(unsigned ch=0;ch<2;++ch)out[ch]+=delta[ch];}
    if(direct!=0)for(auto& value:out)value+=direct;
    return out;
#else
    const auto original=boardObservation();
    std::array<double,3> force{};double direct=0;bool applied=false;
    for (unsigned i=0;i<4;++i) {
      const auto result=mechanisms[i].step(bodyPort(bodyGroups[i]));
      if (result.bodyImpulse!=0) {
        bodyImpulse(bodyGroups[i],result.bodyImpulse);
        force[bodyGroups[i]]+=result.bodyImpulse/model->dt;applied=true;
      }
      direct+=mechanisms[i].directObservation();
    }
    if (applied) {
      const auto observed=boardObservation(force);
      for (unsigned ch=0;ch<2;++ch) out[ch]+=observed[ch]-original[ch];
    }
    if (direct!=0) for (auto& value:out) value+=direct;
    return out;
#endif
  }
};

FullInstrument::FullInstrument():impl_(new Impl) {}
FullInstrument::~FullInstrument()=default;
FullInstrument::FullInstrument(FullInstrument&&) noexcept=default;
FullInstrument& FullInstrument::operator=(FullInstrument&&) noexcept=default;
bool FullInstrument::prepare(double rate) noexcept {
  auto c=impl_?impl_->config:FullInstrumentConfig{};c.sampleRate=rate;return prepare(c);
}
bool FullInstrument::prepare(const FullInstrumentConfig& c) noexcept {
  if (!std::isfinite(c.sampleRate)||c.sampleRate<44100||c.sampleRate>96000||
      std::floor(c.sampleRate)!=c.sampleRate||!validParameters(c.parameters)) return false;
  if (!impl_) impl_.reset(new (std::nothrow) Impl);
  if (!impl_) return false;
  std::unique_ptr<grand::Piano> model(new (std::nothrow) grand::Piano(options(c.sampleRate)));
  if (!model) return false;
  impl_->model=std::move(model);impl_->config=c;
  physics::StrikeConfig strike;
  strike.sampleRate=c.sampleRate;strike.variation=1;strike.seed=c.seed;
  if (!impl_->controller.prepare(strike)) return false;
  for (unsigned i=0;i<4;++i) {
    auto& source=impl_->mechanisms[i];
    auto mechanism=physics::mechanismPreset(static_cast<physics::MechanismKind>(i),c.sampleRate);
    // Conservative authored loading, independent of trigger level. Full
    // research-port resistance audibly damps the core even between triggers.
    mechanism.couplingResistanceKgPerSecond*=.025;
    if (!source.prepare(mechanism)) return false;
    source.setCouplingEnabled(c.mechanismBodyCoupling);
    source.setObservationEnabled(c.mechanismObservation);
  }
  for (unsigned i=0;i<88;++i) impl_->baseHardness[i]=impl_->model->keys[i].K;
#if defined(KEYRA_FULL_MECHANISM_CACHE) && KEYRA_FULL_MECHANISM_CACHE
  impl_->bodyCache.prepare(*impl_->model);
#endif
  impl_->pole=std::exp(-2*grand::pi*24/c.sampleRate);
  impl_->parameters(c.parameters);impl_->reset();return true;
}
bool FullInstrument::prepared() const noexcept { return impl_&&bool(impl_->model); }
void FullInstrument::reset() noexcept { if (prepared()) impl_->reset(); }
void FullInstrument::allSoundOff() noexcept { reset(); }
bool FullInstrument::setParameters(const FullInstrumentParameters& p) noexcept {
  if (!impl_||!validParameters(p)) { if (impl_) ++impl_->rejected;return false; }
  impl_->parameters(p);return true;
}
FullInstrumentParameters FullInstrument::parameters() const noexcept {
  return impl_?impl_->config.parameters:FullInstrumentParameters{};
}
bool FullInstrument::noteOn(int note,double velocity) noexcept {
  if (!prepared()||!validNote(note)||!unit(velocity)) { if (impl_) ++impl_->rejected;return false; }
  return impl_->on(note,velocity);
}
bool FullInstrument::noteOff(int note) noexcept {
  if (!prepared()||!validNote(note)) { if (impl_) ++impl_->rejected;return false; }
  return impl_->off(note);
}
bool FullInstrument::sustain(double value) noexcept {
  if (!prepared()||!unit(value)) { if (impl_) ++impl_->rejected;return false; }
  impl_->trigger(3,std::abs(value-impl_->model->pedalTarget));impl_->model->pedalTarget=value;return true;
}
bool FullInstrument::process(float* left,float* right,uint32_t frames) noexcept {
  if (!frames) return true;
  if (!prepared()||!left||!right||left==right) { if (impl_) ++impl_->rejected;return false; }
  for (uint32_t i=0;i<frames;++i) {
    auto x=impl_->step();
    if (impl_->config.parameters.stereoWidth!=1) {
      const double mid=.5*(x[0]+x[1]),side=.5*(x[0]-x[1])*impl_->config.parameters.stereoWidth;
      x={mid+side,mid-side};
    }
    std::array<double,2> output{};
    bool valid=true;
    for (unsigned ch=0;ch<2;++ch) {
      impl_->highpass[ch]=impl_->pole*(impl_->highpass[ch]+x[ch]-impl_->previous[ch]);
      impl_->previous[ch]=x[ch];output[ch]=impl_->highpass[ch]*impl_->gain;
      valid=valid&&std::isfinite(output[ch])&&std::abs(output[ch])<=std::numeric_limits<float>::max();
    }
    if (!valid) { impl_->retireNonfinite();output={}; }
    left[i]=static_cast<float>(output[0]);right[i]=static_cast<float>(output[1]);++impl_->frame;
  }
  return true;
}
FullInstrumentDiagnostics FullInstrument::diagnostics() const noexcept {
  FullInstrumentDiagnostics d;
  if (!impl_) return d;
  d.frames=impl_->frame;d.rejectedInputs=impl_->rejected;d.unsafeLaunches=impl_->unsafe;
  d.nonfiniteOutputFaults=impl_->outputFaults;
  const auto& s=impl_->controller.statistics();
  d.requests=s.requests+impl_->savedStrikes.requests+impl_->bypassRequests;
  d.launches=s.launches+impl_->savedStrikes.launches+impl_->bypassLaunches;
  d.deferred=s.deferred+impl_->savedStrikes.deferred;d.coalesced=s.coalesced+impl_->savedStrikes.coalesced;
  d.cancelled=s.cancelled+impl_->savedStrikes.cancelled;d.expired=s.expired+impl_->savedStrikes.expired;
  if (!impl_->model) return d;
  const auto& model=*impl_->model;
  d.bridgeFaults=model.bridgeFaults+impl_->savedBridgeFaults;
  d.contactFaults=model.contactFaults+impl_->savedContactFaults;
  d.faultFlags=model.faultFlags|impl_->savedFaultFlags;
  d.stringCount=static_cast<uint32_t>(model.strings.size());d.stringModes=static_cast<uint32_t>(model.modeCount());
  d.boardModes=static_cast<uint32_t>(model.board.size());
  for (const auto& key:model.keys) if (key.hammerActive) ++d.activeHammers;
  d.pedal=model.pedal;d.pedalTarget=model.pedalTarget;return d;
}
} // namespace keyra
