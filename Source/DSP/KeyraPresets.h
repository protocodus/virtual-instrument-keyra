#pragma once
#include "KeyraEngine.h"
#include <array>

namespace keyra {
// The factory bank: the plug-in's programs and the README demos. A preset sets
// the piano, its build controls to 0 and the voicing controls; output, tuning,
// mechanics and the pedals keep their values.
struct Preset { const char* name; Piano piano; float brightness, resonance, width, mute; };
inline constexpr std::array<Preset, 8> factoryPresets {{
    { "Concert Grand", Piano::grand, .5f, .25f, .75f, 0.f },
    { "Studio Grand", Piano::grand, .62f, .12f, .48f, 0.f },
    { "Warm Walnut", Piano::grand, .28f, .31f, .64f, 0.f },
    { "Felt Nocturne", Piano::grand, .35f, .17f, .58f, .32f },
    { "Open Strings", Piano::grand, .52f, .62f, .95f, 0.f },
    { "Rehearsal Upright", Piano::upright, .5f, .25f, .75f, 0.f },
    { "Felt Upright", Piano::upright, .32f, .18f, .6f, .3f },
    { "Pop Upright", Piano::upright, .64f, .14f, .5f, 0.f }
}};

inline Parameters withPreset(Parameters parameters, const Preset& preset) noexcept {
  parameters.build = measuredBuild(preset.piano);
  parameters.brightness = preset.brightness;
  parameters.resonance = preset.resonance;
  parameters.width = preset.width;
  parameters.mute = preset.mute;
  return parameters;
}
}
