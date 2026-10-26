#pragma once
#include <cstdint>
#include <memory>

namespace keyra {

// Controls for the complete physical instrument. Gain is applied after its
// original 24 Hz high-pass. No limiter, reverb, or automatic normalization.
struct FullInstrumentParameters {
  double gainDb=0;
  double dynamics=.5;      // .5 preserves the original velocity response
  double humanization=.65; // bounded velocity/hardness excitation variation
  double mechanicalLevel=.025; // quiet authored texture; zero disables sources
  double stereoWidth=1;    // 1 preserves the original two observations
};
struct FullInstrumentConfig {
  double sampleRate=48000;
  uint32_t seed=0x4b657972u;
  FullInstrumentParameters parameters{};
  bool repetitionController=true;
  bool mechanismBodyCoupling=true;
  bool mechanismObservation=true;
};
struct FullInstrumentDiagnostics {
  uint64_t frames=0,requests=0,launches=0,deferred=0,coalesced=0;
  uint64_t cancelled=0,expired=0,rejectedInputs=0,unsafeLaunches=0;
  uint64_t bridgeFaults=0,contactFaults=0,nonfiniteOutputFaults=0;
  uint32_t faultFlags=0; // 1 bridge, 2 contact, 4 nonfinite output
  uint32_t stringCount=0,stringModes=0,boardModes=0,activeHammers=0;
  double pedal=0,pedalTarget=0;
};

// One physical 88-key instrument, with a shared soundboard and global pedal.
// Access must be serialized by the caller. Construction and prepare may
// allocate; all other methods are bounded and allocation-free. prepare/reset
// clear sound and counters. Events apply before the next process frame.
class FullInstrument {
public:
  FullInstrument();
  ~FullInstrument();
  FullInstrument(const FullInstrument&)=delete;
  FullInstrument& operator=(const FullInstrument&)=delete;
  FullInstrument(FullInstrument&&) noexcept;
  FullInstrument& operator=(FullInstrument&&) noexcept;

  bool prepare(const FullInstrumentConfig&) noexcept;
  bool prepare(double sampleRate) noexcept;
  bool prepared() const noexcept;
  void reset() noexcept;
  void allSoundOff() noexcept;
  bool setParameters(const FullInstrumentParameters&) noexcept;
  FullInstrumentParameters parameters() const noexcept;
  bool noteOn(int midiNote,double normalizedVelocity) noexcept;
  bool noteOff(int midiNote) noexcept;
  bool sustain(double normalizedPosition) noexcept;
  // Overwrites both buffers. A null buffer rejects the entire block; neither
  // audio state nor the absolute frame clock advances. Zero frames is a no-op.
  bool process(float* left,float* right,uint32_t frames) noexcept;
  FullInstrumentDiagnostics diagnostics() const noexcept;

private:
  struct Impl;
  std::unique_ptr<Impl> impl_;
};
} // namespace keyra
