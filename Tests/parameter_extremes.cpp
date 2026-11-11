// Every control at its ends and its middle, set before the notes and while
// they sound, on every piano at three sample rates: the output stays finite
// and under full scale, and the two ends differ, so no control is dead.
#include "DSP/KeyraEngine.h"
#include "DSP/KeyraPresets.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <cstring>
#include <iostream>
#include <memory>
#include <vector>

namespace {
using Audio = std::vector<float>;
int failures = 0;
void check(bool ok, const char* message) {
    if (!ok) { ++failures; std::cerr << "FAIL: " << message << '\n'; }
}
Audio play(keyra::Engine& engine, int count) {
    std::array<float, 64> left{}, right{};
    Audio result(static_cast<std::size_t>(count) * 2);
    for (int offset = 0; offset < count; offset += 64) {
        const int n = std::min(64, count - offset);
        engine.process(left.data(), right.data(), n);
        for (int i = 0; i < n; ++i) {
            result[2 * (offset + i)] = left[i];
            result[2 * (offset + i) + 1] = right[i];
        }
    }
    return result;
}
double difference(const Audio& a, const Audio& b) {
    double sum = 0;
    for (std::size_t i = 0; i < a.size(); ++i) {
        const double d = a[i] - b[i]; sum += d * d;
    }
    return sum / a.size();
}
using Field = float& (*)(keyra::Parameters&);
struct Control { const char* name; Field field; float low, mid, high; };
const Control controls[] {
    {"gain", [](keyra::Parameters& p) -> float& { return p.gain; }, 0, .7f, 2},
    {"hammer", [](keyra::Parameters& p) -> float& { return p.hammer; }, -1, 0, 1},
    {"age", [](keyra::Parameters& p) -> float& { return p.age; }, 0, .5f, 1},
    {"detune", [](keyra::Parameters& p) -> float& { return p.detune; }, 0, .5f, 1},
    {"stretch", [](keyra::Parameters& p) -> float& { return p.stretch; }, 0, 1, 2},
    {"dynamics", [](keyra::Parameters& p) -> float& { return p.dynamics; }, 0, .5f, 1},
    {"lid", [](keyra::Parameters& p) -> float& { return p.lid; }, 0, .5f, 1},
    {"soundboard", [](keyra::Parameters& p) -> float& { return p.soundboard; }, 0, .5f, 1},
    {"sympathetic", [](keyra::Parameters& p) -> float& { return p.sympathetic; }, 0, .5f, 1},
    {"duplex", [](keyra::Parameters& p) -> float& { return p.duplex; }, 0, .5f, 1},
    {"mic close", [](keyra::Parameters& p) -> float& { return p.mic[keyra::model::micClose]; }, 0, 1, 2},
    {"mic xy", [](keyra::Parameters& p) -> float& { return p.mic[keyra::model::micXY]; }, 0, 1, 2},
    {"mic live", [](keyra::Parameters& p) -> float& { return p.mic[keyra::model::micLive]; }, 0, 1, 2},
    {"mic distant", [](keyra::Parameters& p) -> float& { return p.mic[keyra::model::micDistant]; }, 0, 1, 2},
    {"room", [](keyra::Parameters& p) -> float& { return p.room; }, 0, .5f, 1},
    {"width", [](keyra::Parameters& p) -> float& { return p.width; }, 0, .5f, 1},
    {"tuning", [](keyra::Parameters& p) -> float& { return p.tuning; }, 400, 440, 480},
    {"felt", [](keyra::Parameters& p) -> float& { return p.felt; }, 0, .5f, 1},
    {"mute", [](keyra::Parameters& p) -> float& { return p.mute; }, 0, .5f, 1},
    {"sustain", [](keyra::Parameters& p) -> float& { return p.sustain; }, 0, .5f, 1},
    {"sostenuto", [](keyra::Parameters& p) -> float& { return p.sostenuto; }, 0, .5f, 1},
    {"soft", [](keyra::Parameters& p) -> float& { return p.soft; }, 0, .5f, 1},
    {"mechanics", [](keyra::Parameters& p) -> float& { return p.mechanics; }, 0, 1, 2}
};

Audio exercise(keyra::Engine& engine, const Control& control, float value, bool automate, keyra::model::Body body) {
    keyra::Parameters parameters;
    parameters.body = body;
    // Sostenuto needs keys present at its rising edge. Pressing it before all
    // notes correctly captures nothing, so that sequence cannot witness its
    // signal path (the engine contract separately checks that behavior).
    if (!automate && std::strcmp(control.name, "sostenuto") != 0)
        control.field(parameters) = value;
    engine.setParameters(parameters);
    engine.reset();
    engine.noteOn(48, .8f); engine.noteOn(60, .7f);
    play(engine, 4096);
    control.field(parameters) = value;
    engine.setParameters(parameters);
    // A later strike witnesses what only a strike takes (the hammer, the
    // felt, the dynamics, the strings' age and Soft), and released notes
    // witness both pedals.
    engine.noteOn(84, .75f);
    play(engine, 2048);
    engine.noteOff(48); engine.noteOff(60); engine.noteOff(84);
    return play(engine, 12288);
}
}

int main() {
    unsigned cases = 0;
    // One engine: constructing it designs every piano, a change of rate does not.
    auto engine = std::make_unique<keyra::Engine>(48000);
    for (const double rate : {44100., 48000., 96000.}) {
        engine->prepare(rate);
        for (int body = 0; body < keyra::model::bodyCount; ++body) {
            for (const auto& control : controls) {
                for (const bool automate : {false, true}) {
                    const auto piano = static_cast<keyra::model::Body>(body);
                    const auto low = exercise(*engine, control, control.low, automate, piano);
                    const auto middle = exercise(*engine, control, control.mid, automate, piano);
                    const auto high = exercise(*engine, control, control.high, automate, piano);
                    for (const auto* audio : {&low, &middle, &high}) {
                        const bool safe = std::all_of(audio->begin(), audio->end(), [](float x) {
                            return std::isfinite(x) && x >= -1 && x <= 1;
                        });
                        check(safe, "parameter endpoint/midpoint emitted unsafe audio");
                        ++cases;
                    }
                    // An upright has no duplex scale, so the control is silent there.
                    const bool silentByDesign = piano == keyra::model::Body::upright && std::strcmp(control.name, "duplex") == 0;
                    if ((difference(low, high) <= 1e-14) != silentByDesign) {
                        std::cerr << "Unwitnessed control: " << control.name << " on " << keyra::bodyNames[static_cast<std::size_t>(body)] << '\n';
                        check(false, "control endpoints have no audible-path activation witness");
                    }
                }
            }
        }
    }
    std::cout << "parameter_cases=" << cases << " failures=" << failures << '\n';
    return failures ? 1 : 0;
}
