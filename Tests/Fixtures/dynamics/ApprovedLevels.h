#pragma once

#include <array>

// 0.4.10 engine at half drive, with a factor of two after its output stage.
// Reproduce these 48 kHz readings with measure_approved_levels.cpp.
// Four presets' typical levels were re-baselined for 0.4.14, to the two
// decimals KeyraLevels prints, when the chords of the grand and the upright
// gained their per-key trims and their output scales were re-pinned
// (Docs/decisions.md, 2026-11-03); the other rows are the 0.4.10 readings.
// The Belmont baby grand's rows were removed with that piano on 2026-11-04.
// The same day the owner approved the readings of KeyraLevels after the
// stereo image between recorded pitches changed how a chord's notes add:
// six presets' typical levels, four presets' and the grand tube's loudest
// chords, re-baselined to six decimals (Docs/decisions.md, 2026-11-04).
// Later that day the blend between recorded pitches and the noise refit
// moved seven presets, with each piano's default sound and tube re-pinned
// to its earlier reading, and the owner approved the new readings: four
// presets' typical levels and four presets' loudest chords, to six decimals
// (Docs/decisions.md, 2026-11-04). Then 0.4.16 to 0.4.18, with the phantom
// partials, moved three presets' typical playing past the guard, and the
// owner approved those three readings, to six decimals (Docs/decisions.md,
// 2026-11-04). In 0.4.22 the Hamburg's keys between recorded pitches play the
// keyboard network, its output and tube re-pinned to their earlier
// readings, and the owner approved its loudest chords' new readings, the
// Hamburg Grand preset's and its tube's, to six decimals (Docs/decisions.md,
// 2026-11-05). In 0.4.23 the Kakegawa grand's and the upright's keys between
// recorded pitches above the bass break take the keyboard network's
// correction to the blend, the upright's tube re-pinned to its earlier
// reading, and the owner approved four presets' new readings, the Kakegawa
// Grand's and Open Strings' loudest chords and Felt Upright's and Pop
// Upright's typical playing, to six decimals (Docs/decisions.md, 2026-11-05).
// In 0.4.26 the Hamamatsu's, the Hamburg's and New York's keys between
// recorded pitches play the retrained keyboard network, their output and
// tube levels re-pinned to their earlier readings, and the treble's unison
// strings ring on three pianos; the owner approved two new readings, Three
// Cities' typical playing and the Hamamatsu tube's loudest chords, to six
// decimals (Docs/decisions.md, 2026-11-06).
// In 0.4.27 each piano plays the room it was recorded in, and in 0.4.28 the
// strike knocks the board under 400 Hz, the Hamamatsu's tube re-pinned to its
// earlier reading; the owner approved six new readings, the loudest chords of
// the Hamamatsu's tube, the Kakegawa Grand, Warm Walnut, Felt Nocturne and
// Open Strings and Felt Upright's typical playing, to six decimals
// (Docs/decisions.md, 2026-11-09).
namespace keyra_test {
struct ApprovedLevel {
    const char* name;
    double typicalVu;
    double loudestVu;
};

inline constexpr std::array<ApprovedLevel, 12> approvedPreset {{
    {"Kakegawa Grand", -9.066835, 0.719836},
    {"Studio Grand", -10.241775, -0.019715},
    {"Warm Walnut", -10.950910, -0.104002},
    {"Felt Nocturne", -18.132439, -5.592784},
    {"Open Strings", -8.081521, 1.514169},
    {"Helsinki Upright", -9.122448, 4.217296},
    {"Felt Upright", -15.589097, -0.127207},
    {"Pop Upright", -9.214799, 3.904373},
    {"Hamamatsu Grand", -9.012878, 4.003352},
    {"Three Cities", -10.426881, 2.871424},
    {"Hamburg Grand", -8.953395, 2.404007},
    {"New York Grand", -9.092756, 3.213257},
}};

inline constexpr std::array<ApprovedLevel, 5> approvedTube {{
    {"grand", -9.068710, 1.222194},
    {"upright", -8.993037, 4.328115},
    {"kawai", -9.985854, 3.301832},
    {"hamburg", -9.172983, 2.196889},
    {"newyork", -9.020263, 2.115038},
}};
} // namespace keyra_test
