#pragma once
#include <memory>

namespace keyra {
// The piano that plays: the grand measured from the Salamander Grand Piano V3
// recordings, or the upright measured from the Helsinki 1967 Tube-Ribbon
// Edition's. Switching silences what sounds.
enum class Piano {grand,upright};
// How much of each strike plays, for CPU: every partial, or only those that
// come within 60 dB (balanced) or 50 dB (light) of the strike's strongest,
// which no third-octave band of the note misses by more than 0.04 or 0.74 dB
// (KeyraEngine.cpp, keepAudible). A change applies from the next strike.
enum class Quality {full,balanced,light};
struct Parameters {
  float gain=.7f, brightness=.5f, resonance=.25f, width=.75f, tuning=440.f;
  float mute=0.f, sustain=0.f, sostenuto=0.f, soft=0.f;
  Piano piano=Piano::grand;
  Quality quality=Quality::full;
};
struct PedalState {float sustain=0,sostenuto=0,soft=0;};

// Front-end-neutral reduced modal piano. Construct/prepare outside the callback.
// All event and render methods are bounded, allocation-free and C++17 compatible.
class Engine {
public:
  explicit Engine(double sampleRate=48000);
  ~Engine();
  Engine(const Engine&)=delete;
  Engine& operator=(const Engine&)=delete;
  void prepare(double sampleRate);
  void reset() noexcept;
  void setParameters(const Parameters&) noexcept;
  // MIDI12/13/14 are counted momentary soft/sostenuto/sustain switches.
  // Piano notes are21..108; other note numbers are ignored.
  void noteOn(int note,float velocity01,int channel=1) noexcept;
  void noteOff(int note,int channel=1) noexcept;
  void controlChange(int cc,int value,int channel=1) noexcept;
  void pitchBend(float semitones,int channel=1) noexcept;
  // Audio-thread query for front ends to publish through their own UI bridge.
  // Channel0 returns maxima across all channels;1..16 return one channel.
  PedalState pedalState(int channel=0) const noexcept;
  void process(float* left,float* right,int frames) noexcept;
  // How late the output is: the shared output stage's look-ahead
  // (Source/DSP/OutputStage.h), 2 ms at the prepared rate. Front ends report
  // it to the host.
  int outputLatencySamples() const noexcept;
  // Offline diagnostic: fixed 2ms rise versus training-recording rise. This
  // changes only future strikes; it is deliberately absent from product UIs.
  void setLegacyAttackForComparison(bool enabled) noexcept;
  // Offline measurement: every strike at exactly the recorded layers'
  // velocity it is given, where strikes otherwise go through the shared
  // velocity response and vary as a player's do. Also absent from product UIs.
  void setSteadyStrikesForMeasurement(bool enabled) noexcept;
private:
  struct Impl;
  std::unique_ptr<Impl> impl;
};
// The recorded layers' velocity (1..127) a strike at MIDI `velocity` (0..1)
// plays on `piano` before its player's spread: one response for both pianos.
float responseVelocity(Piano piano,float velocity) noexcept;
}
