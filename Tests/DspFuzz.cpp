// U4 input fuzzing of the JUCE-free engine through the shared portfolio
// harness (Tests/FuzzHarness.h is a byte-identical copy of the master; change
// it in reason-rack-extensions). Every input starts from a fresh engine, so a
// saved crash replays alone; commands and rendered frames are bounded
// whatever the input length.
#include "DSP/KeyraEngine.h"
#include "DSP/KeyraPresets.h"
#include "FuzzHarness.h"

#include <cmath>
#include <iterator>
#include <memory>

extern "C" int LLVMFuzzerTestOneInput (const std::uint8_t* data, std::size_t size)
{
    using namespace protocodus::fuzz;
    Input input { data, size };

    // prepare() clamps any rate, including the nonsense ones Rate() returns.
    auto engine = std::make_unique<keyra::Engine> (input.Rate());
    keyra::Parameters parameters = keyra::withPreset ({}, keyra::factoryPresets[input.Pick (keyra::factoryPresets.size())]);
    engine->setParameters (parameters);

    constexpr std::size_t maxFrames = 512;
    Sentinels<maxFrames> block;
    // Notes, channels and controllers come as any int, not only MIDI's range.
    const auto any = [&input] { return static_cast<int> (input.Word()); };
    const auto midi = [&input] { return static_cast<int> (input.Byte()) - 64; };

    for (int command = 0; command < 64 && ! input.Empty(); ++command)
    {
        switch (input.Pick (10))
        {
            case 0: engine->noteOn (midi() + 64, input.Scalar(), midi() / 4); break;
            case 1: engine->noteOff (midi() + 64, midi() / 4); break;
            case 2: engine->noteOn (any(), input.Scalar(), any()); break;
            case 3: engine->controlChange (input.Byte(), any(), input.Byte() % 18); break;
            case 4: engine->pitchBend (input.Scalar() * 96.0f - 48.0f, input.Byte() % 18); break;
            case 5:
            {
                // One raw write, which may be any float, to any control,
                // the build's included.
                float* fields[] { &parameters.gain, &parameters.brightness, &parameters.resonance,
                                  &parameters.width, &parameters.tuning, &parameters.mute,
                                  &parameters.sustain, &parameters.sostenuto, &parameters.soft,
                                  &parameters.build.strings, &parameters.build.hammers,
                                  &parameters.build.soundboard, &parameters.build.action,
                                  &parameters.build.stiffness, &parameters.build.unisons,
                                  &parameters.build.ring };
                *fields[input.Pick (std::size(fields))] = input.Scalar();
                engine->setParameters (parameters);
                break;
            }
            case 6:
                parameters = keyra::withPreset (parameters, keyra::factoryPresets[input.Pick (keyra::factoryPresets.size())]);
                engine->setParameters (parameters);
                break;
            case 7: engine->reset(); break;
            case 8: engine->prepare (input.Rate()); break;
            default: engine->setLegacyAttackForComparison (input.Byte() & 1); break;
        }
        const auto frames = 1 + input.Word() % maxFrames;
        block.Arm();
        engine->process (block.Left(), block.Right(), static_cast<int> (frames));
        block.Check (frames);
        // The engine's last stage bounds every sample to full scale.
        for (std::size_t i = 0; i < frames; ++i)
            Require (std::fabs (block.Left()[i]) <= 1.0f && std::fabs (block.Right()[i]) <= 1.0f);
        const auto pedals = engine->pedalState (static_cast<int> (input.Byte() % 18) - 1);
        Require (std::isfinite (pedals.sustain) && std::isfinite (pedals.sostenuto) && std::isfinite (pedals.soft));
    }
    return 0;
}
