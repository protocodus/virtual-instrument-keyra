#pragma once
#include <array>
#include <cmath>
#include <cstdint>

namespace keyra::physics {

// Effective MIDI-to-action timing, not measured key geometry. Normalized
// variation affects the excitation only; a string's tuning/state is not owned
// by this controller. All render/event storage is fixed-size.
struct StrikeConfig {
  double sampleRate=48000;
  double variation=.65;
  double velocityVariation=.008;
  double hardnessVariation=.025;
  double restDepth=.012;
  double separationMargin=.0005;
  double releasedReturnSeconds=.012;
  double heldReturnSeconds=.035;
  double keyReleaseSeconds=.018;
  double keyDepressSeconds=.005;
  double minimumIntervalSeconds=.003;
  double maximumPendingSeconds=.120;
  double minimumRecovery=.06;
  double minimumKeyLift=.20;
  uint32_t seed=0x4b657972u;
};
struct HammerObservation {
  bool active=false;
  double compression=0; // hammer displacement minus contact-point displacement
  double velocity=0;
};
struct StrikeLaunch {
  bool valid=false;
  bool preserveSeparatedPosition=false;
  double velocity=0; // normalized MIDI value; adapter applies original response
  double velocityFactor=1,hardnessFactor=1,recoveryVelocityFactor=1;
  double recovery=1,keyLift=1;
  uint64_t requestId=0;
};
struct StrikeState {
  bool down=false,pending=false,hasLaunched=false,lastActive=false,releasedSinceLaunch=false;
  double recovery=1,returnDepth=.012,keyLift=1,returnVelocity=0;
  double elapsedSinceLaunch=1.e9,pendingAge=0,pendingVelocity=0,pendingLift=1;
  double pendingVelocityFactor=1,pendingHardnessFactor=1;
  double correlatedVelocity=0,correlatedHardness=0;
  uint32_t random=1;
  uint64_t requests=0,launches=0,pendingId=0;
};
struct StrikeStatistics {
  uint64_t requests=0,launches=0,deferred=0,coalesced=0,cancelled=0,expired=0;
  uint64_t retiredBeforeSeparation=0,invalidObservations=0;
};

class StrikeController {
public:
  static constexpr unsigned keyCount=88;
  StrikeController() noexcept { (void)prepare(StrikeConfig{}); }
  bool prepare(const StrikeConfig& c) noexcept {
    if (!finite(c.sampleRate)||c.sampleRate<8000||c.sampleRate>384000||
        !finite(c.variation)||c.variation<0||c.variation>1||
        !finite(c.velocityVariation)||c.velocityVariation<0||c.velocityVariation>.1||
        !finite(c.hardnessVariation)||c.hardnessVariation<0||c.hardnessVariation>.2||
        !finite(c.restDepth)||c.restDepth<.001||c.restDepth>.1||
        !finite(c.separationMargin)||c.separationMargin<=0||c.separationMargin>=c.restDepth||
        !positiveTime(c.releasedReturnSeconds)||!positiveTime(c.heldReturnSeconds)||
        !positiveTime(c.keyReleaseSeconds)||!positiveTime(c.keyDepressSeconds)||
        !positiveTime(c.minimumIntervalSeconds)||!positiveTime(c.maximumPendingSeconds)||
        c.maximumPendingSeconds<c.minimumIntervalSeconds||
        !finite(c.minimumRecovery)||c.minimumRecovery<0||c.minimumRecovery>1||
        !finite(c.minimumKeyLift)||c.minimumKeyLift<0||c.minimumKeyLift>1) return false;
    config_=c;
    releaseReturn_=1-std::exp(-1/(c.sampleRate*c.releasedReturnSeconds));
    heldReturn_=1-std::exp(-1/(c.sampleRate*c.heldReturnSeconds));
    releaseKey_=1-std::exp(-1/(c.sampleRate*c.keyReleaseSeconds));
    depressKey_=1-std::exp(-1/(c.sampleRate*c.keyDepressSeconds));
    reset(); return true;
  }
  void reset() noexcept {
    statistics_={};
    for (unsigned i=0;i<keyCount;++i) {
      auto& s=states_[i]; s={}; s.returnDepth=config_.restDepth;
      s.random=mix(config_.seed^(0x9e3779b9u*(i+1)));
      if (!s.random) s.random=1;
    }
  }
  const StrikeConfig& config() const noexcept { return config_; }
  const StrikeStatistics& statistics() const noexcept { return statistics_; }
  const StrikeState& state(int note) const noexcept {
    return states_[validNote(note)?unsigned(note-21):0];
  }
  bool requiresTick(int note) const noexcept {
    if (!validNote(note)) return false;
    const auto& s=states_[note-21];
    return s.pending||s.lastActive||s.recovery<1||(s.down?s.keyLift>0:s.keyLift<1);
  }
  bool request(int note,double velocity) noexcept {
    if (!validNote(note)||!finite(velocity)||velocity<0) return false;
    if (velocity==0) { release(note); return false; }
    auto& s=states_[note-21];
    if (s.pending) ++statistics_.coalesced;
    s.pending=true; s.down=true; s.pendingAge=0;
    s.pendingVelocity=velocity<1?velocity:1;
    // MIDI may repeat a note-on without an intervening note-off. Treat that
    // explicitly as an authored short key cycle. An explicit short release
    // instead finishes its finite lift while this request is pending.
    s.pendingLift=s.releasedSinceLaunch?s.keyLift:(s.keyLift>.35?s.keyLift:.35);
    s.pendingId=++s.requests; ++statistics_.requests;
    s.correlatedVelocity=.72*s.correlatedVelocity+.28*random(s.random);
    s.correlatedHardness=.72*s.correlatedHardness+.28*random(s.random);
    const double v=.65*s.correlatedVelocity+.35*random(s.random);
    const double h=.65*s.correlatedHardness+.35*random(s.random);
    s.pendingVelocityFactor=1+config_.variation*config_.velocityVariation*v;
    s.pendingHardnessFactor=1+config_.variation*config_.hardnessVariation*h;
    return true;
  }
  void release(int note) noexcept {
    if (!validNote(note)) return;
    auto& s=states_[note-21]; s.down=false; s.releasedSinceLaunch=true;
    if (s.pending) { s.pending=false; ++statistics_.cancelled; }
  }
  // poll(..., false) checks an event without advancing time. It never changes
  // an external hammer. The adapter may act only on a valid launch result.
  StrikeLaunch poll(int note,const HammerObservation& h,bool advance=true) noexcept {
    StrikeLaunch launch;
    if (!validNote(note)) return launch;
    if (!finite(h.compression)||std::abs(h.compression)>1||
        !finite(h.velocity)||std::abs(h.velocity)>10000) {
      ++statistics_.invalidObservations; return launch;
    }
    auto& s=states_[note-21]; const double dt=1/config_.sampleRate;
    const double depth=h.compression<0?-h.compression:0;
    if (advance) {
      s.elapsedSinceLaunch+=dt;
      // A new MIDI press requests an effective key cycle. Touching quantized
      // notes can have an explicit release too short to reset the action.
      // Finish that finite lift before depression, rather than latching its
      // initial zero lift forever or instantly moving an external hammer.
      const bool finishLift=s.pending&&s.hasLaunched&&s.pendingLift<config_.minimumKeyLift;
      const bool keyUp=!s.down||finishLift;
      s.keyLift+=(keyUp?releaseKey_:depressKey_)*((keyUp?1.:0.)-s.keyLift);
      if (keyUp?1-s.keyLift<1.e-8:s.keyLift<1.e-8) s.keyLift=keyUp?1:0;
      if (finishLift) s.pendingLift=s.keyLift;
      s.returnVelocity=0;
      if (h.active) {
        // Inbound/contact states cannot re-arm the hammer. A rebound exposes
        // actual separation, while full recovery remains a later return proxy.
        if (h.velocity<0&&depth>config_.separationMargin) {
          s.returnDepth=depth<config_.restDepth?depth:config_.restDepth;
          s.recovery=s.returnDepth/config_.restDepth;
        }
      } else if (s.hasLaunched) {
        if (s.lastActive) {
          // The legacy solver may retire at its 40ms safety timeout before
          // separation. That removes its active contact energy. Continue a
          // finite-speed return proxy from the signed depth, rather than
          // leaving this key permanently unready or teleporting a new strike.
          s.returnDepth=-h.compression;
          if (s.returnDepth>config_.restDepth) s.returnDepth=config_.restDepth;
          if (depth<config_.separationMargin) ++statistics_.retiredBeforeSeparation;
        }
        const double before=s.returnDepth;
        s.returnDepth+=(s.down?heldReturn_:releaseReturn_)*(config_.restDepth-s.returnDepth);
        if (config_.restDepth-s.returnDepth<1.e-8) s.returnDepth=config_.restDepth;
        s.returnVelocity=s.returnDepth==config_.restDepth?0:(s.returnDepth-before)*config_.sampleRate;
        s.recovery=s.returnDepth>0?s.returnDepth/config_.restDepth:0;
      }
      s.lastActive=h.active;
      if (s.pending) s.pendingAge+=dt;
    }
    if (!s.pending) return launch;
    if (s.pendingAge>config_.maximumPendingSeconds) {
      s.pending=false; ++statistics_.expired; return launch;
    }
    const bool initial=!s.hasLaunched;
    const bool separated=h.compression<=-config_.separationMargin;
    if (h.active||h.compression>0||(!initial&&!separated)||
        s.elapsedSinceLaunch<config_.minimumIntervalSeconds||
        (!initial&&(s.recovery<config_.minimumRecovery||s.pendingLift<config_.minimumKeyLift))) {
      if (!advance) ++statistics_.deferred;
      return launch;
    }
    launch.valid=true; launch.requestId=s.pendingId;
    launch.velocity=s.pendingVelocity; launch.velocityFactor=s.pendingVelocityFactor;
    launch.hardnessFactor=s.pendingHardnessFactor;
    launch.recovery=initial?1:s.recovery; launch.keyLift=s.pendingLift;
    const double effective=launch.recovery*(.35+.65*launch.keyLift);
    launch.recoveryVelocityFactor=initial?1:.30+.70*std::sqrt(effective);
    launch.preserveSeparatedPosition=!initial&&(launch.recovery<.995||launch.keyLift<.8);
    s.pending=false; s.hasLaunched=true; s.recovery=0; s.elapsedSinceLaunch=0;
    s.keyLift=0; s.releasedSinceLaunch=false;
    s.lastActive=true; ++s.launches; ++statistics_.launches;
    return launch;
  }

private:
  StrikeConfig config_{};
  std::array<StrikeState,keyCount> states_{};
  StrikeStatistics statistics_{};
  double releaseReturn_=0,heldReturn_=0,releaseKey_=0,depressKey_=0;
  static bool finite(double x) noexcept { return std::isfinite(x); }
  static bool positiveTime(double x) noexcept { return finite(x)&&x>0&&x<=10; }
  static bool validNote(int note) noexcept { return note>=21&&note<=108; }
  static uint32_t mix(uint32_t x) noexcept { x^=x>>16; x*=0x7feb352du; x^=x>>15; x*=0x846ca68bu; return x^(x>>16); }
  static double random(uint32_t& x) noexcept {
    x^=x<<13; x^=x>>17; x^=x<<5;
    return 2*(double(x)/4294967295.)-1;
  }
};
} // namespace keyra::physics
