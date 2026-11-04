// Build against 0.4.10 commit 674ad1a. This uses its untouched meter, engine,
// factory programs and strike sequences. See README.md in this directory.
#include "DSP/KeyraEngine.h"
#include <cstdlib>
#include <cstring>

namespace keyra {
class RestoredBEngine : public Engine {
public:
    using Engine::Engine;
    void setParameters(Parameters p) noexcept {
        p.gain *= .5f;
        Engine::setParameters(p);
    }
    void process(float* left, float* right, int frames) noexcept {
        Engine::process(left, right, frames);
        for (int i = 0; i < frames; ++i) {
            left[i] *= 2.f;
            right[i] *= 2.f;
        }
    }
};
}

// Use the historical test's complete MIDI sequence, playing only through the
// half-drive engine and a linear monitoring gain. Both microphone paths and
// the meter see that same gain. No peak ceiling is added to the reference.
#define Engine RestoredBEngine
#define main originalKeyraLevelsMain
#include "Tools/KeyraLevels.cpp"
#undef main
#undef Engine

int main(int argc, char** argv) {
    if (argc > 1) {
        if (std::strcmp(argv[1], "--audit-dynamics") == 0)
            return originalKeyraLevelsMain(argc, argv);
        return 2;
    }
    const auto typical = typicalPlaying();
    const auto hard = chordRounds(127);
    const auto& presets = keyra::factoryPresets;
    constexpr std::size_t pianos = keyra::pianoCount;
    const char* const pianoNames[pianos] = {"grand", "upright", "kawai", "hamburg", "newyork"};
    struct Capture { double typicalVu; double hardVu; };
    std::vector<Capture> captures(presets.size() + pianos);
    parallel(captures.size(), 4, [&](std::size_t index) {
        keyra::Parameters p;
        if (index < presets.size()) {
            p = keyra::withPreset(p, presets[index]);
        } else {
            p.build = keyra::measuredBuild(static_cast<keyra::Piano>(index - presets.size()));
            p.mic = 1;
        }
        const auto loudest = play(p, hard);
        const auto normal = play(p, typical);
        if (!normal.finite || !loudest.finite) std::abort();
        captures[index] = {median(normal.events),
                           *std::max_element(loudest.events.begin(), loudest.events.end())};
    });
    std::puts("scope,name,typical_vu,maximum_fortissimo_vu");
    for (std::size_t i = 0; i < captures.size(); ++i) {
        const bool preset = i < presets.size();
        const char* name = preset ? presets[i].name : pianoNames[i - presets.size()];
        std::printf("%s,%s,%.6f,%.6f\n", preset ? "preset" : "tube", name,
                    captures[i].typicalVu, captures[i].hardVu);
    }
}
