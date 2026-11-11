#pragma once
#include "MechanicsControl.h"
#include "PianoModel.h"
#include <memory>

namespace keyra {
// The piano that plays and where it is heard from. Every control but the
// body is continuous; PianoModel.h says what each one is in the instrument.
struct Parameters {
  float gain=.7f;
  model::Body body=model::Body::concertGrand;
  // The hammers' felt, -1 soft to 1 hard; the strings' age, 0 new to 1 old;
  // the unisons' spread, 0 pure to 1 a bar piano; the tuner's stretch, 0
  // equal temperament, 1 the strings' own, 2 twice that; the span between
  // the softest and the hardest blow, 0 narrow to 1 wide.
  float hammer=0.f, age=0.f, detune=.3f, stretch=1.f, dynamics=.5f;
  // The lid, 0 closed, .5 the short stick, 1 open; how long the soundboard
  // rings; how strongly the open strings and the duplex scales answer.
  float lid=1.f, soundboard=.5f, sympathetic=.5f, duplex=.5f;
  // Each microphone pair's level as an amplitude, by model::Mic: the close
  // pair over the hammers (the pop sound), the XY pair at the lid, the live
  // pair in the room and the distant pair across it. Each plays as loud as
  // the close pair at the same level.
  float mic[model::micCount]{1.f,0.f,0.f,0.f};
  // The room in the pairs that hear it, and in the action's sound: 0 none.
  float room=.5f;
  // The stereo image: .75 as the pairs hear it, 0 mono.
  float width=.75f;
  float tuning=440.f;
  // A practice felt between hammers and strings, from the next strike; felt
  // on the sounding strings themselves, at once (the mod wheel's).
  float felt=0.f, mute=0.f;
  float sustain=0.f, sostenuto=0.f, soft=0.f;
  // How loud the action plays, as an amplitude: the keys landing and coming
  // back, the dampers falling and the sustain pedal's knocks. 0 silent, 1 as
  // recorded, 2 twice as loud. New instruments use the owner's quieter
  // choice; the knob's display taper lives in MechanicsControl.h.
  float mechanics=defaultMechanicsGain;
};
struct PedalState {float sustain=0,sostenuto=0,soft=0;};

// Front-end-neutral piano: the physical model (PianoModel.h) under the keys,
// pedals and controllers, with the action's recorded noises beside it.
// Construct/prepare outside the callback. All event and render methods are
// bounded, allocation-free and C++17 compatible.
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
  // Total look-ahead of the piano output stage at the prepared rate.
  // Front ends report this frame count to the host.
  int outputLatencySamples() const noexcept;
  // Offline measurement: every strike at exactly the velocity it is given,
  // where strikes otherwise vary a little as a player's do. Absent from
  // product UIs.
  void setSteadyStrikesForMeasurement(bool enabled) noexcept;
private:
  struct Impl;
  std::unique_ptr<Impl> impl;
};
}
