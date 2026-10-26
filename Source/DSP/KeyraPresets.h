#pragma once
#include "KeyraEngine.h"
#include <array>

namespace keyra {
// The factory bank: the plug-in's programs and the README demos. A preset sets
// the voicing controls only; output, tuning and the pedals keep their values.
struct Preset { const char* name; float brightness, resonance, width, mute; };
inline constexpr std::array<Preset, 5> factoryPresets {{
    { "Concert Grand", .5f, .25f, .75f, 0.f },
    { "Studio Grand", .62f, .12f, .48f, 0.f },
    { "Warm Walnut", .28f, .31f, .64f, 0.f },
    { "Felt Nocturne", .35f, .17f, .58f, .32f },
    { "Open Strings", .52f, .62f, .95f, 0.f }
}};

inline Parameters withPreset(Parameters parameters, const Preset& preset) noexcept {
  parameters.brightness = preset.brightness;
  parameters.resonance = preset.resonance;
  parameters.width = preset.width;
  parameters.mute = preset.mute;
  return parameters;
}
}
