#include "DSP/KeyraEngine.h"
#include <algorithm>
#include <array>
#include <cmath>
#include <iostream>
#include <limits>
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
struct Control { const char* name; float keyra::Parameters::*field; float low, mid, high; };
const Control controls[] {
    {"gain", &keyra::Parameters::gain, 0, .5f, 1},
    {"brightness", &keyra::Parameters::brightness, 0, .5f, 1},
    {"resonance", &keyra::Parameters::resonance, 0, .5f, 1},
    {"width", &keyra::Parameters::width, 0, .5f, 1},
    {"tuning", &keyra::Parameters::tuning, 400, 440, 480},
    {"mute", &keyra::Parameters::mute, 0, .5f, 1},
    {"sustain", &keyra::Parameters::sustain, 0, .5f, 1},
    {"sostenuto", &keyra::Parameters::sostenuto, 0, .5f, 1},
    {"soft", &keyra::Parameters::soft, 0, .5f, 1}
};

Audio exercise(const Control& control, float value, double rate, bool automate, keyra::Piano piano) {
    auto engine = std::make_unique<keyra::Engine>(rate);
    keyra::Parameters parameters;
    parameters.piano = piano;
    // Sostenuto needs keys present at its rising edge. Pressing it before all
    // notes correctly captures nothing, so that sequence cannot witness its
    // signal path (the engine contract separately checks that behavior).
    if (!automate && control.field != &keyra::Parameters::sostenuto)
        parameters.*(control.field) = value;
    engine->setParameters(parameters);
    engine->noteOn(48, .8f); engine->noteOn(60, .7f);
    play(*engine, 4096);
    parameters.*(control.field) = value;
    engine->setParameters(parameters);
    // A later strike witnesses Soft, and released notes witness both pedals.
    engine->noteOn(72, .75f);
    play(*engine, 2048);
    engine->noteOff(48); engine->noteOff(60); engine->noteOff(72);
    return play(*engine, 16384);
}
}

int main() {
    unsigned cases = 0;
    for (const auto piano : {keyra::Piano::grand, keyra::Piano::upright}) {
        for (const double rate : {44100., 48000., 96000.}) {
            for (const auto& control : controls) {
                for (const bool automate : {false, true}) {
                    const auto low = exercise(control, control.low, rate, automate, piano);
                    const auto middle = exercise(control, control.mid, rate, automate, piano);
                    const auto high = exercise(control, control.high, rate, automate, piano);
                    for (const auto* audio : {&low, &middle, &high}) {
                        const bool safe = std::all_of(audio->begin(), audio->end(), [](float x) {
                            return std::isfinite(x) && x >= -1 && x <= 1;
                        });
                        check(safe, "parameter endpoint/midpoint emitted unsafe audio");
                        ++cases;
                    }
                    if (difference(low, high) <= 1e-14) {
                        std::cerr << "Unwitnessed control: " << control.name << '\n';
                        check(false, "control endpoints have no audible-path activation witness");
                    }
                }
            }
        }
    }
    {
        keyra::Engine engine;
        std::array<float, 4> left{{1, 2, 3, 4}}, right{{5, 6, 7, 8}};
        engine.process(left.data(), right.data(), 0);
        engine.process(left.data(), right.data(), -1);
        engine.process(nullptr, right.data(), 4);
        engine.process(left.data(), nullptr, 4);
        check(left[0] == 1 && right[3] == 8, "invalid render span changed output memory");
    }
    std::cout << "parameter_cases=" << cases << " failures=" << failures << '\n';
    return failures ? 1 : 0;
}
