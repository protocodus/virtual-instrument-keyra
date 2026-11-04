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
namespace keyra_test {
struct ApprovedLevel {
    const char* name;
    double typicalVu;
    double loudestVu;
};

inline constexpr std::array<ApprovedLevel, 12> approvedPreset {{
    {"Kakegawa Grand", -9.016195, 0.688266},
    {"Studio Grand", -10.241775, -0.019715},
    {"Warm Walnut", -10.865286, -0.139903},
    {"Felt Nocturne", -18.132439, -5.642349},
    {"Open Strings", -8.133493, 1.455051},
    {"Helsinki Upright", -9.122448, 4.217296},
    {"Felt Upright", -15.86, -0.127207},
    {"Pop Upright", -9.078588, 3.904373},
    {"Hamamatsu Grand", -9.012878, 4.003352},
    {"Three Cities", -10.29, 2.871424},
    {"Hamburg Grand", -8.893996, 1.688414},
    {"New York Grand", -9.092756, 3.213257},
}};

inline constexpr std::array<ApprovedLevel, 5> approvedTube {{
    {"grand", -9.068710, 1.222194},
    {"upright", -8.993037, 4.328115},
    {"kawai", -9.985854, 3.199726},
    {"hamburg", -9.172983, 1.407187},
    {"newyork", -9.020263, 2.115038},
}};
} // namespace keyra_test
