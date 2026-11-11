#pragma once
#include <memory>

// Keyra's physical piano: hammers thrown at stiff strings, the strings of a
// unison coupled at the bridge in two polarisations, a soundboard of modes
// radiating to microphones, and the open strings and duplex scales ringing
// with them. Nothing here is fitted to a recording note by note; a piano is
// a description (PianoModel.cpp, Design) and the controls below.
namespace keyra { namespace model {
constexpr int keyCount=88;   // A0 (key 0) to C8 (key 87)
// The pianos designed at prepare(): each a string scale, hammers, soundboard
// and case of its size.
enum class Body {concertGrand,parlorGrand,babyGrand,upright};
constexpr int bodyCount=4;
// The microphone pairs, each mixed at its own level:
// close    a spaced pair inside, over the hammers (behind an upright's board)
// xy       a coincident cardioid pair at the open lid, a metre off
// live     a spaced pair in the room at 2.5 m, the player's side of an upright
// distant  a wide pair across the room
enum Mic {micClose,micXY,micLive,micDistant};
constexpr int micCount=4;

struct Controls {
  Body body=Body::concertGrand;
  // The hammers' felt, from soft and worn-in (-1) to hard and bright (1).
  float hammer=0;
  // The strings' age: 0 new, 1 old strings that have lost their upper
  // partials' sustain and beat against themselves.
  float age=0;
  // How far apart the strings of a unison are tuned: 0 pure, 1 a bar piano.
  float detune=.3f;
  // The tuner's stretch: 0 equal temperament, 1 octaves tuned to the
  // strings' own inharmonic partials, 2 twice that.
  float stretch=1;
  // How far apart the softest and the hardest blow are: 0 a narrow, even
  // touch, 1 the widest.
  float dynamics=.5f;
  // The lid (an upright's top): 0 closed, .5 the short stick, 1 open.
  float lid=1;
  // How long the soundboard rings: 0 heavily damped, 1 lively.
  float soundboard=.5f;
  // How strongly the open strings and the duplex scales answer.
  float sympathetic=.5f,duplex=.5f;
  // Each microphone pair's level as an amplitude, by Mic.
  float mic[micCount]{1,0,0,0};
  // The room's reverberation in the pairs that hear it: 0 none, 1 twice.
  float room=.5f;
  // A4 in Hz.
  float tuning=440;
  // A practice felt between hammers and strings, 0 off to 1 down.
  float felt=0;
  // Felt laid on every string, held or not: 0 off, 1 as a damper rests.
  float mute=0;
};

// Allocation-free, bounded and C++17 after prepare().
class Piano {
public:
  Piano();
  ~Piano();
  Piano(const Piano&)=delete;
  Piano& operator=(const Piano&)=delete;
  // Designs every body; not real-time.
  void prepare(double sampleRate);
  void reset() noexcept;
  // Applies at once to what sounds, except what only a strike can set (the
  // hammer, the felt, the dynamics and the strings' age), which the next
  // strike takes.
  void setControls(const Controls&) noexcept;
  // The hammer of `key` thrown at `velocity` (0..1); `soft` is the soft
  // pedal's travel (una corda on a grand, half-blow on an upright).
  void strike(int key,float velocity,float soft=0) noexcept;
  // Whether a key or the sostenuto holds this key's damper off its strings.
  void holdDamper(int key,bool held) noexcept;
  // The sustain pedal's travel, 0 up to 1 down.
  void setPedal(float travel) noexcept;
  // Pitch bend of everything sounding, in semitones.
  void setBend(float semitones) noexcept;
  // Writes the microphones' mix, in pascals.
  void process(float* left,float* right,int frames) noexcept;
  bool silent() const noexcept;
  // Offline diagnostics for Tools/: an impulse on the bridge where `key`'s
  // strings cross it, and what a key is built as.
  void knockBridge(int key,float newtonSeconds) noexcept;
  struct KeyReport {int strings,partials;double hertz,length,tension,inharmonicity,stretchCents,hammerMass;};
  KeyReport report(Body body,int key) const noexcept;
private:
  struct Impl;
  std::unique_ptr<Impl> impl;
};
}}
