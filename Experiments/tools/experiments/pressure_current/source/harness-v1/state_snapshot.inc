// Diagnostic include appended to the privately copied FullInstrument.cpp after
// Impl is defined. Copied headers expose private members without layout changes.
// No model construction, stepping, event, output mutation, or render-path I/O.
// Serialize individual arithmetic values, never structs, padding, capacities or
// raw allocation addresses. Vector lengths and pointer ownership are explicit.
// Native IEEE float/double payloads preserve signed zero and NaN payload bits;
// comparisons are scoped to the same compiler/platform used by the harness.
//
// Coverage: FullInstrument config, all Impl counters/baselines/contact planes and
// every common physical coefficient/state/cache except observer-only cachedRadiation; hammer,
// damper, force/velocity/solver counters/stems; unison topology/coefficient caches;
// Impl.previous/highpass are also excluded; complete controller configs/states/RNG/recovery/stats; all mechanism configs,
// modal state/coefficients/flags/energy ledgers; optional body cache coefficients,
// velocities and impulses. Immutable translation-unit constants and ephemeral
// stack temporaries have no instance state and remain bound by source hashes.
// Candidate-only execution-view arrays have no baseline counterpart and are
// excluded from byte equality; their ownership/coverage is checked separately
// by the candidate's prepare-time inventory and frozen source review.

#include <cstdint>
#include <cstring>
#include <fstream>
#include <limits>
#include <type_traits>

extern "C" bool keyra_pressure_snapshot(const keyra::FullInstrument* piano,
                                      const char* path) {
  static_assert(sizeof(float)==4 && sizeof(double)==8 &&
                std::numeric_limits<float>::is_iec559 &&
                std::numeric_limits<double>::is_iec559,
                "Snapshot requires the harness's IEEE float/double format");
  if (!piano || !path || !piano->impl_ || !piano->impl_->model) return false;
  const auto& impl=*piano->impl_;
  const auto& model=*impl.model;
  std::ofstream file(path,std::ios::binary|std::ios::trunc);
  if (!file) return false;
  bool pointersValid=true;
  auto scalar=[&](const auto& value) {
    using T=std::decay_t<decltype(value)>;
    static_assert(std::is_arithmetic_v<T>,"Only individual arithmetic fields");
    if constexpr(std::is_same_v<T,bool>) {
      const std::uint8_t canonical=value?1u:0u;
      file.write(reinterpret_cast<const char*>(&canonical),sizeof(canonical));
    } else {
      file.write(reinterpret_cast<const char*>(&value),sizeof(value));
    }
  };
  auto sequence=[&](const auto& values) {
    scalar(static_cast<std::uint64_t>(values.size()));
    for (const auto& value:values) scalar(value);
  };
  auto strikes=[&](const auto& s) {
    scalar(s.requests);scalar(s.launches);scalar(s.deferred);scalar(s.coalesced);
    scalar(s.cancelled);scalar(s.expired);scalar(s.retiredBeforeSeparation);
    scalar(s.invalidObservations);
  };
  // Cache aliases point only into a string's canonical modal velocity vector.
  // Encode (null/non-null, owner string, element), not process-specific pointers.
  // Integer-address comparisons avoid relational comparisons between unrelated
  // allocations, and no pointer is dereferenced during alias identification.
  auto alias=[&](const float* pointer) {
    std::uint8_t kind=pointer?1u:0u;
    std::uint64_t stringIndex=std::numeric_limits<std::uint64_t>::max();
    std::uint64_t modeIndex=std::numeric_limits<std::uint64_t>::max();
    if (pointer) {
      const auto address=reinterpret_cast<std::uintptr_t>(pointer);
      for (std::size_t i=0;i<model.strings.size();++i) {
        const auto& values=model.strings[i].m.p;
        if (values.empty()) continue;
        const auto first=reinterpret_cast<std::uintptr_t>(values.data());
        const auto bytes=values.size()*sizeof(float);
        if (address>=first && address-first<bytes && (address-first)%sizeof(float)==0) {
          stringIndex=static_cast<std::uint64_t>(i);
          modeIndex=static_cast<std::uint64_t>((address-first)/sizeof(float));
          break;
        }
      }
      if (stringIndex==std::numeric_limits<std::uint64_t>::max()) {
        kind=2u;pointersValid=false;
      }
    }
    scalar(kind);scalar(stringIndex);scalar(modeIndex);
  };

  const std::uint32_t version=1;
  const std::uint32_t marker=0x4b465331u; // KFS1; no raw struct header.
  scalar(marker);scalar(version);
  scalar(static_cast<std::uint8_t>(sizeof(int)));
  scalar(static_cast<std::uint8_t>(sizeof(unsigned)));
  scalar(impl.config.sampleRate);scalar(impl.config.seed);
  const auto& parameters=impl.config.parameters;
  scalar(parameters.gainDb);scalar(parameters.dynamics);scalar(parameters.humanization);
  scalar(parameters.mechanicalLevel);scalar(parameters.stereoWidth);
  scalar(impl.config.repetitionController);scalar(impl.config.mechanismBodyCoupling);
  scalar(impl.config.mechanismObservation);
  sequence(impl.baseHardness);sequence(impl.contactPlane);
  // Output-observer filter memory intentionally excluded.
  scalar(impl.frame);scalar(impl.rejected);scalar(impl.unsafe);
  scalar(impl.bypassRequests);scalar(impl.bypassLaunches);scalar(impl.outputFaults);
  scalar(impl.savedBridgeFaults);scalar(impl.savedContactFaults);scalar(impl.savedFaultFlags);
  strikes(impl.savedStrikes);
  scalar(impl.pole);scalar(impl.gain);scalar(impl.velocityExponent);

  scalar(model.opt.sampleRate);scalar(model.opt.bridge);scalar(model.opt.hammerLoss);
  scalar(model.opt.loss);scalar(model.opt.damper);scalar(model.opt.sympathetic);
  scalar(model.opt.calibrated);scalar(model.opt.captureStems);
  scalar(model.dt);scalar(model.pedal);scalar(model.pedalTarget);
  scalar(model.maxForce);scalar(model.contactTime);scalar(model.maxContactResidual);
  scalar(model.forceSolves);scalar(model.contactEvaluations);
  scalar(model.contactNewtonIterations);scalar(model.contactBisectionIterations);
  scalar(model.contactFallbacks);scalar(model.maximumContactNewton);scalar(model.maximumContactBisections);
  scalar(model.faultFlags);scalar(model.bridgeFaults);scalar(model.contactFaults);scalar(model.maxEnergy);
  for (const auto& row:model.boardGram) sequence(row);
  for (const auto& stem:model.lastStems) sequence(stem);

  scalar(static_cast<std::uint64_t>(model.strings.size()));
  for (const auto& string:model.strings) {
    scalar(string.note);scalar(string.unison);scalar(string.group);
    scalar(string.resistance);scalar(string.compliance);scalar(string.velocity);scalar(string.force);
    // Per-string observer cache intentionally excluded.
    const auto& m=string.m;
    sequence(m.q);sequence(m.p);sequence(m.c);sequence(m.s);sequence(m.omega);
    sequence(m.hammer);sequence(m.b);sequence(m.forceQ);sequence(m.forceP);
    sequence(m.loss);sequence(m.damper);sequence(m.damp);
    sequence(m.partial);sequence(m.polarization);
    sequence(m.radQL);sequence(m.radPL);sequence(m.radQR);sequence(m.radPR);
    sequence(m.radiationMagnitude);
    sequence(m.baseQL);sequence(m.basePL);sequence(m.baseQR);sequence(m.basePR);
    sequence(m.portOmega);sequence(m.portInverse);
  }
  scalar(static_cast<std::uint64_t>(model.keys.size()));
  for (const auto& key:model.keys) {
    sequence(key.strings);
    scalar(key.f0);scalar(key.B);scalar(key.length);scalar(key.mu);
    scalar(key.mass);scalar(key.K);scalar(key.power);
    scalar(key.hammerX);scalar(key.hammerV);scalar(key.age);scalar(key.maxForce);
    scalar(key.contactSeconds);scalar(key.contactCompliance);scalar(key.velocityExponent);
    scalar(key.down);scalar(key.hammerActive);scalar(key.everStruck);
    scalar(key.damperPosition);scalar(key.cachedContact);scalar(key.cachedLoss);
  }
  scalar(static_cast<std::uint64_t>(model.board.size()));
  for (const auto& z:model.board) {
    scalar(z.q);scalar(z.p);scalar(z.w);scalar(z.c);scalar(z.s);scalar(z.damp);
    scalar(z.sigma);scalar(z.force);sequence(z.port);sequence(z.mic);
  }
  scalar(static_cast<std::uint64_t>(model.unisonPorts.size()));
  for (const auto& port:model.unisonPorts) {
    scalar(static_cast<std::uint64_t>(port.modes.size()));
    for (const auto& mode:port.modes) {scalar(mode.first);scalar(mode.second);}
    scalar(port.coefficient);scalar(port.count);
    for (const auto* pointer:port.velocityState) alias(pointer);
    sequence(port.omega);sequence(port.inverseOmega);
  }
  scalar(static_cast<std::uint64_t>(model.unisonGroups.size()));
  for (const auto& group:model.unisonGroups) {
    scalar(group.count);
    for (const auto* pointer:group.velocity) alias(pointer);
    for (const auto& omega:group.omega) sequence(omega);
    for (const auto& inverse:group.inverse) sequence(inverse);
    sequence(group.coefficient);
  }

  const auto& controller=impl.controller;
  const auto& c=controller.config_;
  scalar(c.sampleRate);scalar(c.variation);scalar(c.velocityVariation);scalar(c.hardnessVariation);
  scalar(c.restDepth);scalar(c.separationMargin);scalar(c.releasedReturnSeconds);scalar(c.heldReturnSeconds);
  scalar(c.keyReleaseSeconds);scalar(c.keyDepressSeconds);scalar(c.minimumIntervalSeconds);
  scalar(c.maximumPendingSeconds);scalar(c.minimumRecovery);scalar(c.minimumKeyLift);scalar(c.seed);
  scalar(controller.releaseReturn_);scalar(controller.heldReturn_);
  scalar(controller.releaseKey_);scalar(controller.depressKey_);
  scalar(static_cast<std::uint64_t>(controller.states_.size()));
  for (const auto& s:controller.states_) {
    scalar(s.down);scalar(s.pending);scalar(s.hasLaunched);scalar(s.lastActive);scalar(s.releasedSinceLaunch);
    scalar(s.recovery);scalar(s.returnDepth);scalar(s.keyLift);scalar(s.returnVelocity);
    scalar(s.elapsedSinceLaunch);scalar(s.pendingAge);scalar(s.pendingVelocity);scalar(s.pendingLift);
    scalar(s.pendingVelocityFactor);scalar(s.pendingHardnessFactor);
    scalar(s.correlatedVelocity);scalar(s.correlatedHardness);scalar(s.random);
    scalar(s.requests);scalar(s.launches);scalar(s.pendingId);
  }
  strikes(controller.statistics_);

  scalar(static_cast<std::uint64_t>(impl.mechanisms.size()));
  for (const auto& mechanism:impl.mechanisms) {
    const auto& cfg=mechanism.config_;
    scalar(cfg.sampleRate);scalar(cfg.modalMassKg);scalar(cfg.frequencyHz);scalar(cfg.lossPerSecond);
    scalar(cfg.couplingResistanceKgPerSecond);scalar(cfg.triggerImpulseNs);scalar(cfg.directObservationGain);
    scalar(static_cast<std::uint64_t>(mechanism.modes_.size()));
    for (const auto& mode:mechanism.modes_) {
      scalar(mode.x);scalar(mode.v);scalar(mode.c);scalar(mode.s);scalar(mode.damp);scalar(mode.port);
    }
    const auto& ledger=mechanism.ledger_;
    scalar(ledger.externalWork);scalar(ledger.retiredEnergy);scalar(ledger.internalDissipation);
    scalar(ledger.couplingDissipation);scalar(ledger.bodyWork);scalar(ledger.maximumBalanceResidual);
    scalar(ledger.triggers);scalar(ledger.frames);scalar(ledger.invalidFrames);
    scalar(mechanism.inverseMass_);scalar(mechanism.enabled_);
    scalar(mechanism.coupling_);scalar(mechanism.observation_);
  }
#if defined(KEYRA_FULL_MECHANISM_CACHE) && KEYRA_FULL_MECHANISM_CACHE
  scalar(std::uint8_t{1});
  const auto& cache=impl.bodyCache;
  scalar(static_cast<std::uint64_t>(cache.nodes.size()));
  for (const auto& node:cache.nodes) {sequence(node.impulse);sequence(node.dampingObserver);}
  for (const auto& row:cache.gram) sequence(row);
  for (const auto& row:cache.forceObserver) sequence(row);
  sequence(cache.velocity);sequence(cache.impulse);
#else
  scalar(std::uint8_t{0});
#endif
  file.close();
  return pointersValid && bool(file);
}
