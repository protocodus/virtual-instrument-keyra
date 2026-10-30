#pragma once
#include <memory>

namespace keyra {
// The two measured pianos: the grand from the Salamander Grand Piano V3
// recordings, the upright from the Helsinki 1967 Tube-Ribbon Edition's.
enum class Piano {grand,upright};
// The piano that plays, built part by part. Each part sits between the two
// measured pianos' (0 the grand's, 1 the upright's); between them it blends
// the two, a piano neither recording is. The modifiers scale what the parts
// give, 0 leaving them as built. A change applies from the next strike, and
// the soundboard's modes and the undamped strings move at once.
struct Build {
  // The strings: their stretch and stiffness, unisons, decays and pickups,
  // the undamped top strings and the components beside the series.
  float strings=0;
  // The hammers: what a strike excites, each partial's level and phase at
  // contact, the tone's change with velocity, the onset and the contact.
  float hammers=0;
  // The soundboard and case: their modes, a strike's knock on them and the
  // board's noise.
  float soundboard=0;
  // The action: the knocks of keys, dampers and pedals.
  float action=0;
  // The strings' inharmonicity, times 4^stiffness (-1 to 1: a quarter to four
  // times as built).
  float stiffness=0;
  // How far the unison strings sit apart: -1 pure, 0 as built, 1 three times
  // as far.
  float unisons=0;
  // How long the strings ring, times 2^ring (-1 to 1: half to twice).
  float ring=0;
};
// Each measured piano's build: every part its own, the modifiers at 0.
constexpr Build measuredBuild(Piano piano) noexcept {
  const float part=piano==Piano::upright?1.f:0.f;
  return {part,part,part,part,0.f,0.f,0.f};
}
// The build the front ends' controls describe: a measured piano with each
// part moved toward the other piano's by its control (0 its own, 1 the
// other's), and the modifiers. A song or patch saved before the controls
// existed has them at 0, so it plays the piano it chose.
constexpr Build buildToward(Piano piano,float strings,float hammers,float soundboard,float action,
                            float stiffness,float unisons,float ring) noexcept {
  const float own=piano==Piano::upright?1.f:0.f,way=1-2*own;
  return {own+way*strings,own+way*hammers,own+way*soundboard,own+way*action,stiffness,unisons,ring};
}
// How much of each strike plays, for CPU: every partial, or only those that
// come within 60 dB (balanced) or 50 dB (light) of the strike's strongest,
// which no third-octave band of the note misses by more than 0.04 or 0.74 dB
// (KeyraEngine.cpp, keepAudible). A change applies from the next strike.
enum class Quality {full,balanced,light};
struct Parameters {
  float gain=.7f, brightness=.5f, resonance=.25f, width=.75f, tuning=440.f;
  float mute=0.f, sustain=0.f, sostenuto=0.f, soft=0.f;
  // Where the piano is heard from: 0 the stereo pair each piano is fitted
  // from (the upright's ribbons in player position, the grand's pair over
  // the strings), 1 the upright recordings' other microphone, a mono tube
  // further off on the same strikes, by its difference from the ribbons
  // (MeasuredMicData.h); between them the two mixed. It applies at once, to
  // everything sounding.
  float mic=0.f;
  // How loud the action plays, as an amplitude: the keys landing and coming
  // back, the dampers falling, the sustain pedal's knocks and the strings its
  // lifting sets ringing. 0 silent, 1 as calibrated, 2 twice as loud.
  float mechanics=1.f;
  Build build{};
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
// plays on a measured piano before its player's spread: one response for both
// pianos.
float responseVelocity(Piano piano,float velocity) noexcept;
}
