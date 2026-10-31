#pragma once
#include "KeyraEngine.h"
#include <array>

namespace keyra {
// The measured pianos as the front ends name them, by Piano: each by a city
// its kind of piano comes from, and whether it is a grand or an upright.
// Reason's identity rule keeps their makers' names off the panels and out of
// the presets; the grand's and the Kawai's makers both come from Hamamatsu,
// so the grand goes by Kakegawa, where its maker builds its grands.
inline constexpr std::array<const char*, pianoCount> pianoCities {{ "Kakegawa", "Helsinki", "Hamamatsu" }};
inline constexpr std::array<const char*, pianoCount> pianoKinds {{ "grand", "upright", "grand" }};
// The factory bank: the plug-in's programs and the README demos. A preset sets
// the build, every part's mix and the modifiers, and the voicing controls;
// output, tuning, mechanics, the mic and the pedals keep their values. A
// recorded piano's presets play it as built; Three Cities plays every part
// at equal thirds of the three.
struct Preset { const char* name; Build build; float brightness, resonance, width, mute; };
inline constexpr Build kakegawa = measuredBuild(Piano::grand), helsinki = measuredBuild(Piano::upright),
                       hamamatsu = measuredBuild(Piano::kawai), thirds { {1, 1, 1}, {1, 1, 1}, {1, 1, 1}, {1, 1, 1}, 0, 0, 0 };
inline constexpr std::array<Preset, 10> factoryPresets {{
    { "Kakegawa Grand", kakegawa, .5f, .25f, .75f, 0.f },
    { "Studio Grand", kakegawa, .62f, .12f, .48f, 0.f },
    { "Warm Walnut", kakegawa, .3f, .31f, .64f, 0.f },
    { "Felt Nocturne", kakegawa, .35f, .17f, .58f, .32f },
    { "Open Strings", kakegawa, .52f, .62f, .95f, 0.f },
    { "Helsinki Upright", helsinki, .5f, .25f, .75f, 0.f },
    { "Felt Upright", helsinki, .32f, .18f, .6f, .3f },
    { "Pop Upright", helsinki, .64f, .14f, .5f, 0.f },
    { "Hamamatsu Grand", hamamatsu, .5f, .25f, .75f, 0.f },
    { "Three Cities", thirds, .5f, .25f, .75f, 0.f }
}};

inline Parameters withPreset(Parameters parameters, const Preset& preset) noexcept {
  parameters.build = preset.build;
  parameters.brightness = preset.brightness;
  parameters.resonance = preset.resonance;
  parameters.width = preset.width;
  parameters.mute = preset.mute;
  return parameters;
}
}
