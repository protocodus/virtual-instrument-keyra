#pragma once
#include "Parameters.h"
#include <cstddef>
#include <cstdint>
#include <memory>

namespace keyra {
// Sample-free, recording-calibrated modal performance engine. This is a reduced
// model, not the preserved research renderer's nonlinear hammer solver.
// All methods except prepare/construction/destruction are allocation-free.
// The caller serializes these methods on the audio thread; host UI/state code
// must transfer parameter changes to that thread rather than call concurrently.
class Piano {
public:
  static constexpr std::size_t maxVoices=64;
  static constexpr std::size_t partialCount=64;
  Piano();
  ~Piano();
  Piano(const Piano&)=delete;
  Piano& operator=(const Piano&)=delete;
  Piano(Piano&&)=delete;
  Piano& operator=(Piano&&)=delete;
  // Valid sample rates: 8–384 kHz. Success rebuilds coefficients, clears playing
  // state, and preserves parameter values. Unsupported/nonfinite rates return
  // false without changing the current engine. No exceptions are required.
  bool prepare(double sampleRate) noexcept;
  // Clears voices, pedals and effects, retaining parameter values.
  void reset() noexcept;
  // Instrument, material's string voicing and dynamics affect new strikes.
  // Tone also supplies a live shelf. Material board color, microphones, tone,
  // resonance, noise, distance, width and gain are smoothed in running audio.
  void setParameter(ParamId,double) noexcept;
  double parameter(ParamId) const noexcept;
  void noteOn(int note,double velocity,int channel=0,int32_t noteId=-1) noexcept;
  // -1 is a wildcard for note, channel, or noteId. Repeated same-key notes with
  // different host note IDs can therefore be released independently.
  void noteOff(int note,int channel=0,int32_t noteId=-1) noexcept;
  void noteChoke(int note=-1,int channel=-1,int32_t noteId=-1) noexcept;
  bool noteActive(int note,int channel,int32_t noteId=-1) const noexcept;
  void sustain(double position,int channel=0) noexcept;
  void allNotesOff(int channel=-1) noexcept;
  void allSoundOff(int channel=-1) noexcept;
  // Replaces output samples. Events/parameters can be applied between calls at
  // exact sample boundaries; output does not depend on host block partitioning.
  void process(float* left,float* right,uint32_t frames) noexcept;
  std::size_t activeVoices() const noexcept;
private:
  struct Impl;
  std::unique_ptr<Impl> impl_;
};
} // namespace keyra
