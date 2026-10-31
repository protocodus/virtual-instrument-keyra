#pragma once
#include <array>
#include <cstddef>
#include <memory>

namespace keyra {
// The measured pianos, each fitted from its own recordings: the grand from
// the Salamander Grand Piano V3's, the upright from the Helsinki 1967
// Tube-Ribbon Edition's, the Kawai grand from the VCSL Keys "Grand Piano,
// K"'s. Saved songs and patches recall a piano by its value, so pianos are
// only ever added at the end.
enum class Piano {grand,upright,kawai};
constexpr int pianoCount=3;
// How much of each measured piano a part of the build takes, by Piano:
// weights from 0 to 1, played as shares of their sum, so that any number of
// pianos mix in one part. A part with no weight plays the grand's.
using Mix=std::array<float,pianoCount>;
constexpr Mix only(Piano piano) noexcept {Mix mix{};mix[static_cast<std::size_t>(piano)]=1;return mix;}
// The piano that plays, built part by part from the measured pianos. Each
// part mixes the pianos by its Mix; between them it blends them, a piano no
// recording is. The modifiers scale what the parts give, 0 leaving them as
// built. A change applies from the next strike, and the soundboard's modes
// and the undamped strings move at once.
struct Build {
  // The strings: their stretch and stiffness, unisons, decays and pickups,
  // the undamped top strings and the components beside the series.
  Mix strings=only(Piano::grand);
  // The hammers: what a strike excites, each partial's level and phase at
  // contact, the tone's change with velocity, the onset and the contact.
  Mix hammers=only(Piano::grand);
  // The soundboard and case: their modes, a strike's knock on them and the
  // board's noise.
  Mix soundboard=only(Piano::grand);
  // The action: the knocks of keys, dampers and pedals.
  Mix action=only(Piano::grand);
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
constexpr Build measuredBuild(Piano piano) noexcept {return {only(piano),only(piano),only(piano),only(piano),0,0,0};}
// A build between two pianos, as the controls of songs and patches saved
// before the mixes describe it: each part moved from `piano`'s (0) toward
// `toward`'s (1), and the modifiers. A piano built toward itself is just
// itself.
constexpr Build buildToward(Piano piano,Piano toward,float strings,float hammers,float soundboard,float action,
                            float stiffness,float unisons,float ring) noexcept {
  const auto part=[piano,toward](float x){
    Mix mix{};mix[static_cast<std::size_t>(piano)]+=1-x;mix[static_cast<std::size_t>(toward)]+=x;return mix;};
  return {part(strings),part(hammers),part(soundboard),part(action),stiffness,unisons,ring};
}
// The piano a measured piano's parts moved toward in those songs and
// patches: the upright's for the grand, the grand's for every other.
constexpr Piano partner(Piano piano) noexcept {return piano==Piano::grand?Piano::upright:Piano::grand;}
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
// plays on a measured piano before its player's spread: one response for
// every piano.
float responseVelocity(Piano piano,float velocity) noexcept;
}
