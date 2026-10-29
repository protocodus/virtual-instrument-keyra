// Renders one README demo per factory preset (README G3) from the committed
// phrases in Docs/audio/midi, through the same JUCE-free engine the plug-in
// runs. The contract and the fixed rate, block size and seed live in the
// shared PresetDemoRenderer.h.

#include "DSP/KeyraEngine.h"
#include "DSP/KeyraPresets.h"
#include "DSP/OutputStage.h"
#include "PresetDemoRenderer.h"

#include <memory>
#include <stdexcept>
#include <string>

namespace
{
class KeyraVoice final : public protocodus::demos::Voice
{
public:
    KeyraVoice (const keyra::Preset& preset, double sampleRate)
        : engine (std::make_unique<keyra::Engine> (sampleRate))
    {
        engine->setParameters (keyra::withPreset ({}, preset));
    }

    // The messages the processor dispatches, mapped the way it maps them.
    // Anything else in a phrase is an error, not a silently dropped event.
    void Midi (const std::uint8_t* bytes, int size) override
    {
        const int kind = bytes[0] & 0xf0, channel = (bytes[0] & 0x0f) + 1;
        const int data1 = size > 1 ? bytes[1] : 0, data2 = size > 2 ? bytes[2] : 0;
        if (kind == 0x80 || (kind == 0x90 && data2 == 0)) engine->noteOff (data1, channel);
        else if (kind == 0x90) engine->noteOn (data1, data2 / 127.0f, channel);
        else if (kind == 0xb0) engine->controlChange (data1, data2, channel);
        else if (kind == 0xe0)
        {
            const int wheel = (data2 << 7) | data1;
            engine->pitchBend (2.0f * (wheel - 8192) / (wheel < 8192 ? 8192.0f : 8191.0f), channel);
        }
        else throw std::runtime_error ("unsupported MIDI message " + std::to_string (bytes[0]));
    }

    void Render (float* left, float* right, int frames) override
    {
        engine->process (left, right, frames);
    }

private:
    std::unique_ptr<keyra::Engine> engine;
};
} // namespace

int main (int argc, char** argv)
{
    protocodus::demos::Instrument instrument;
    instrument.name = "Keyra";
    // The engine ends in the shared output stage, whose limiter holds every
    // sample at -1.5 dBFS; the margin is the float rounding its own test allows.
    instrument.ceiling = protocodus::OutputStage<2>::kCeiling * (1.0f + 1.0e-6f);
    for (const auto& preset : keyra::factoryPresets)
        instrument.presets.push_back (preset.name);
    // U7 perf budget: about 3x the slowest demo's median realtime factor on
    // the CI runner, 0.203 (08-pop-upright) in ci.yml run 58 (ubuntu-24.04,
    // Intel Xeon Platinum 8573C, three repeats), 2026-10-29.
    instrument.cpuBudget = 0.6;
    instrument.open = [] (std::size_t preset, double sampleRate, int, std::uint32_t)
    {
        // The engine has no random source, so it takes no seed.
        return std::make_unique<KeyraVoice> (keyra::factoryPresets[preset], sampleRate);
    };
    return protocodus::demos::Main (argc, argv, instrument);
}
