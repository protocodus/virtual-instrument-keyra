#pragma once

#include <array>
#include <cmath>
#include <complex>
#include <cstddef>

namespace keyra { namespace physics {

// Isolated 48 kHz feasibility model. Not the piano's default string solver.
// All traveling-wave samples have velocity units m/s; Z is kg/s. One rail
// sample stores h*Z*u^2 joules. The left path folds the outward/return rails
// at a fixed end; the other two paths reach and return from the bridge.
class WaveguideString {
public:
  static constexpr std::size_t delayCapacity=4096;
  static constexpr std::size_t allpassCapacity=16;
  static constexpr double sampleRate=48000.;
  static constexpr double stepSeconds=1./sampleRate;

  struct PathConfig {
    unsigned delaySamples=1;
    unsigned allpassCount=0;
    std::array<double,allpassCapacity> allpass{};
    // Contractive two-tap FIR g*((1-alpha)+alpha*z^-1).
    double lossGain=1,lossMix=0;
    // Optional passive shelf preserves unity DC transmission. Without it,
    // scalar lossGain<1 gives nonzero DC contact mobility and displacement
    // creep. The default retains the original isolated-study arithmetic.
    bool dcPreservingLoss=false;
    double dcLossPole=.9997;
  };
  struct Config {
    double impedance=1;
    PathConfig left{},toBridge{},fromBridge{};
  };
  struct Result {
    bool valid=false;
    double contactVelocity=0,bridgeVelocity=0;
    // Force exerted by the prescribed bridge motion ON the string.
    // The equal/opposite force on a board is -bridgeForce.
    double bridgeForce=0;
    double portWork=0,dissipated=0;
  };
  struct Ports {
    bool valid=false;
    double contactVelocityFree=0;
    double bridgeIncomingVelocity=0;
    double contactForceMobility=0;
  };

  bool prepare(const Config& candidate) noexcept {
    if(!std::isfinite(candidate.impedance)||candidate.impedance<=0||
       !valid(candidate.left)||!valid(candidate.toBridge)||!valid(candidate.fromBridge)||
       !same(candidate.toBridge,candidate.fromBridge))return false;
    config_=candidate;left_.prepare(candidate.left);toBridge_.prepare(candidate.toBridge);
    fromBridge_.prepare(candidate.fromBridge);prepared_=true;
    accumulatedWork_=accumulatedLoss_=contactDisplacement_=bridgeDisplacement_=0;
    return true;
  }
  const Config& config() const noexcept {return config_;}

  // Current incoming waves after every configured path filter, without
  // advancing delay/allpass/FIR/shelf state or their loss/work ledgers.
  // The integer delay on every path makes these independent of the current
  // contact force and bridge velocity. A caller must still step exactly once.
  Ports ports() const noexcept {
    Ports result;
    if(!prepared_)return result;
    result.contactVelocityFree=-left_.peek()+fromBridge_.peek();
    result.bridgeIncomingVelocity=toBridge_.peek();
    result.contactForceMobility=1/(2*config_.impedance);
    result.valid=std::isfinite(result.contactVelocityFree)&&
      std::isfinite(result.bridgeIncomingVelocity)&&std::isfinite(result.contactForceMobility);
    return result;
  }

  // Forces persistently advance existing state. A repeated strike must supply
  // another force sequence, never prepare()/clear() an already vibrating string.
  // Contact F is prescribed; bridge velocity is prescribed. Their simultaneous
  // connection to nonlinear hammers/modal boards remains a separate task.
  Result step(double contactForce=0,double bridgeVelocity=0) noexcept {
    Result result;
    if(!prepared_||!std::isfinite(contactForce)||!std::isfinite(bridgeVelocity))return result;
    double loss=0;
    const double aLeft=-left_.take(loss);
    const double aRight=fromBridge_.take(loss);
    const double aBridge=toBridge_.take(loss);
    const double halfForce=contactForce/(2*config_.impedance);
    result.contactVelocity=aLeft+aRight+halfForce;
    result.bridgeVelocity=bridgeVelocity;
    result.bridgeForce=config_.impedance*(bridgeVelocity-2*aBridge);
    // Equal-Z interior force junction: bL=aR+F/(2Z), bR=aL+F/(2Z).
    left_.put(aRight+halfForce);
    toBridge_.put(aLeft+halfForce);
    fromBridge_.put(bridgeVelocity-aBridge);
    result.portWork=stepSeconds*(contactForce*result.contactVelocity+
                                result.bridgeForce*bridgeVelocity);
    result.dissipated=stepSeconds*config_.impedance*loss;
    accumulatedWork_+=result.portWork;accumulatedLoss_+=result.dissipated;
    contactDisplacement_+=stepSeconds*result.contactVelocity;
    bridgeDisplacement_+=stepSeconds*bridgeVelocity;
    result.valid=true;return result;
  }

  // Diagnostics only: O(delay length), intentionally absent from step().
  double energy() const noexcept {
    return stepSeconds*config_.impedance*(left_.energy()+toBridge_.energy()+fromBridge_.energy());
  }
  double accumulatedWork() const noexcept {return accumulatedWork_;}
  double accumulatedLoss() const noexcept {return accumulatedLoss_;}
  double balanceResidual() const noexcept {return energy()+accumulatedLoss_-accumulatedWork_;}
  double contactDisplacement() const noexcept {return contactDisplacement_;}
  double bridgeDisplacement() const noexcept {return bridgeDisplacement_;}

  // Offline transfer helper; never called by step(). Uses z (not z^-1).
  static std::complex<double> transfer(const PathConfig& path,std::complex<double> z) noexcept {
    const auto zi=1./z;
    auto h=std::pow(zi,int(path.delaySamples));
    for(unsigned i=0;i<path.allpassCount;++i)h*=(path.allpass[i]+zi)/(1.+path.allpass[i]*zi);
    if(path.dcPreservingLoss){
      const auto shelf=path.lossGain+(1-path.lossGain)*(1-path.dcLossPole)/(1.-path.dcLossPole*zi);
      return h*((1-path.lossMix)+path.lossMix*zi)*shelf;
    }
    return h*path.lossGain*((1-path.lossMix)+path.lossMix*zi);
  }

private:
  static bool same(const PathConfig& a,const PathConfig& b) noexcept {
    if(a.delaySamples!=b.delaySamples||a.allpassCount!=b.allpassCount||
       a.lossGain!=b.lossGain||a.lossMix!=b.lossMix||
       a.dcPreservingLoss!=b.dcPreservingLoss||a.dcLossPole!=b.dcLossPole)return false;
    for(unsigned i=0;i<a.allpassCount;++i)if(a.allpass[i]!=b.allpass[i])return false;
    return true;
  }
  static bool valid(const PathConfig& path) noexcept {
    if(path.delaySamples==0||path.delaySamples>delayCapacity||path.allpassCount>allpassCapacity||
       !std::isfinite(path.lossGain)||path.lossGain<0||path.lossGain>1||
       !std::isfinite(path.lossMix)||path.lossMix<0||path.lossMix>.5||
       !std::isfinite(path.dcLossPole)||path.dcLossPole<0||path.dcLossPole>=1)return false;
    for(unsigned i=0;i<path.allpassCount;++i)
      if(!std::isfinite(path.allpass[i])||std::abs(path.allpass[i])>=1)return false;
    return true;
  }
  struct Path {
    PathConfig config{};
    std::array<double,delayCapacity> delay{};
    std::array<double,allpassCapacity> state{},sine{};
    unsigned index=0;
    double previous=0,dcState=0;
    void prepare(const PathConfig& c) noexcept {
      config=c;delay.fill(0);state.fill(0);index=0;previous=0;dcState=0;
      for(unsigned i=0;i<c.allpassCount;++i)sine[i]=std::sqrt(1-c.allpass[i]*c.allpass[i]);
    }
    double peek() const noexcept {
      double x=delay[index];
      for(unsigned i=0;i<config.allpassCount;++i)
        x=config.allpass[i]*x+sine[i]*state[i];
      const double beforeGain=(1-config.lossMix)*x+config.lossMix*previous;
      if(config.dcPreservingLoss){
        const double updated=config.dcLossPole*dcState+(1-config.dcLossPole)*beforeGain;
        return config.lossGain*beforeGain+(1-config.lossGain)*updated;
      }
      return config.lossGain*beforeGain;
    }
    double take(double& loss) noexcept {
      double x=delay[index];
      // Orthogonal scattering allpass: x²+q²=y²+q'², including its storage.
      // H(z)=(c+z^-1)/(1+c*z^-1). No interpolator passivity assumption.
      for(unsigned i=0;i<config.allpassCount;++i){
        const double old=state[i],c=config.allpass[i],s=sine[i];
        state[i]=s*x-c*old;x=c*x+s*old;
      }
      const double alpha=config.lossMix;
      const double beforeGain=(1-alpha)*x+alpha*previous;
      const double difference=x-previous;
      if(config.dcPreservingLoss){
        const double pole=config.dcLossPole,gain=config.lossGain;
        const double old=dcState;
        const double updated=pole*old+(1-pole)*beforeGain;
        const double inputDifference=beforeGain-old;
        const double outputDifference=beforeGain-updated;
        loss+=alpha*(1-alpha)*difference*difference+
          (1-gain)*pole*inputDifference*inputDifference+
          gain*(1-gain)*outputDifference*outputDifference;
        dcState=updated;previous=x;
        return gain*beforeGain+(1-gain)*updated;
      }
      loss+=alpha*(1-alpha)*difference*difference+
            (1-config.lossGain*config.lossGain)*beforeGain*beforeGain;
      previous=x;return config.lossGain*beforeGain;
    }
    void put(double x) noexcept {delay[index]=x;if(++index==config.delaySamples)index=0;}
    double energy() const noexcept {
      double e=config.lossMix*previous*previous;
      for(unsigned i=0;i<config.delaySamples;++i)e+=delay[i]*delay[i];
      for(unsigned i=0;i<config.allpassCount;++i)e+=state[i]*state[i];
      if(config.dcPreservingLoss)
        e+=(1-config.lossGain)*config.dcLossPole/(1-config.dcLossPole)*dcState*dcState;
      return e;
    }
  };
  Config config_{};
  Path left_{},toBridge_{},fromBridge_{};
  bool prepared_=false;
  double accumulatedWork_=0,accumulatedLoss_=0;
  double contactDisplacement_=0,bridgeDisplacement_=0;
};

}} // namespace keyra::physics
