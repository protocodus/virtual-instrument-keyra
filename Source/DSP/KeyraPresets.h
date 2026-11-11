#pragma once
#include "KeyraEngine.h"
#include <array>

namespace keyra {
// The pianos as the front ends name them, by model::Body.
inline constexpr std::array<const char*, model::bodyCount> bodyNames {{ "Concert Grand", "Parlor Grand", "Baby Grand", "Upright" }};
// The microphone pairs as the front ends name them, by model::Mic.
inline constexpr std::array<const char*, model::micCount> micNames {{ "Close", "XY", "Live", "Distant" }};
// The factory bank: the plug-in's programs and the README demos. A preset is
// a piano, how it is kept and where it is heard from; output, tuning,
// mechanics, the mod wheel's mute and the pedals keep their values. New
// presets go at the end, so a host's program numbers keep theirs.
struct Preset {
  const char* name;
  model::Body body;
  float hammer, age, detune, stretch, dynamics;
  float lid, soundboard, sympathetic, duplex;
  float mic[model::micCount];
  float room, width, felt;
};
inline constexpr std::array<Preset, 12> factoryPresets {{
    { "Concert Grand", model::Body::concertGrand, 0.f, 0.f, .3f, 1.f, .5f, 1.f, .5f, .5f, .5f, { 1.f, 0.f, 0.f, 0.f }, .5f, .75f, 0.f },
    { "Studio Grand", model::Body::parlorGrand, .3f, 0.f, .25f, 1.f, .45f, 1.f, .4f, .35f, .5f, { 1.f, .5f, 0.f, 0.f }, .3f, .6f, 0.f },
    { "Warm Walnut", model::Body::parlorGrand, -.5f, .25f, .35f, 1.f, .5f, .5f, .6f, .6f, .4f, { .7f, .7f, .3f, 0.f }, .5f, .7f, 0.f },
    { "Felt Nocturne", model::Body::concertGrand, -.3f, .1f, .3f, 1.f, .4f, .5f, .55f, .5f, .3f, { 1.f, .4f, 0.f, 0.f }, .5f, .65f, .6f },
    { "Open Strings", model::Body::concertGrand, 0.f, 0.f, .35f, 1.f, .55f, 1.f, .7f, 1.f, 1.f, { .5f, .5f, .8f, 0.f }, .6f, .9f, 0.f },
    { "Upright", model::Body::upright, 0.f, .2f, .4f, 1.f, .5f, 1.f, .5f, .5f, 0.f, { 1.f, 0.f, 0.f, 0.f }, .5f, .75f, 0.f },
    { "Felt Upright", model::Body::upright, -.4f, .3f, .4f, 1.f, .4f, .5f, .5f, .4f, 0.f, { 1.f, 0.f, .3f, 0.f }, .4f, .6f, .7f },
    { "Pop Upright", model::Body::upright, .6f, .1f, .3f, 1.f, .4f, 1.f, .4f, .3f, 0.f, { 1.f, .4f, 0.f, 0.f }, .25f, .55f, 0.f },
    { "Baby Grand", model::Body::babyGrand, .1f, .15f, .35f, 1.f, .5f, 1.f, .5f, .5f, .5f, { .8f, .6f, 0.f, 0.f }, .4f, .75f, 0.f },
    { "Distant Hall", model::Body::concertGrand, -.1f, 0.f, .3f, 1.f, .55f, 1.f, .6f, .6f, .5f, { 0.f, .3f, .7f, 1.f }, .8f, .9f, 0.f },
    { "Old Parlor", model::Body::parlorGrand, -.2f, .8f, .6f, .8f, .5f, .5f, .5f, .6f, .6f, { .6f, 0.f, .8f, 0.f }, .5f, .7f, 0.f },
    { "Bar Piano", model::Body::upright, .5f, .7f, 1.f, .6f, .45f, 1.f, .5f, .5f, 0.f, { .6f, 0.f, .8f, 0.f }, .5f, .7f, 0.f }
}};

inline Parameters withPreset(Parameters parameters, const Preset& preset) noexcept {
  parameters.body = preset.body;
  parameters.hammer = preset.hammer;
  parameters.age = preset.age;
  parameters.detune = preset.detune;
  parameters.stretch = preset.stretch;
  parameters.dynamics = preset.dynamics;
  parameters.lid = preset.lid;
  parameters.soundboard = preset.soundboard;
  parameters.sympathetic = preset.sympathetic;
  parameters.duplex = preset.duplex;
  for (int i = 0; i < model::micCount; ++i) parameters.mic[i] = preset.mic[i];
  parameters.room = preset.room;
  parameters.width = preset.width;
  parameters.felt = preset.felt;
  return parameters;
}
}
