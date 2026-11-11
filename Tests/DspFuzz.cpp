// U4 input fuzzing of the JUCE-free engine through the shared portfolio
// harness (Tests/FuzzHarness.h is a byte-identical copy of the master; change
// it in reason-rack-extensions). Every input starts from an engine prepared
// and reset, which plays as a fresh one (Keyra.Engine checks that), so a
// saved crash replays alone; constructing one designs every piano, too slow
// to do for each input. Commands and rendered frames are bounded whatever
// the input length.
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
    static const auto engine = std::make_unique<keyra::Engine>();
    engine->prepare (input.Rate());
    engine->reset();
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
            // Each read in its own statement: the order a call's arguments
            // are evaluated in is the compiler's, and a saved input must
            // replay the same on all of them.
            case 0: { const int note = midi() + 64; const float velocity = input.Scalar(); engine->noteOn (note, velocity, midi() / 4); break; }
            case 1: { const int note = midi() + 64; engine->noteOff (note, midi() / 4); break; }
            case 2: { const int note = any(); const float velocity = input.Scalar(); engine->noteOn (note, velocity, any()); break; }
            case 3: { const int controller = input.Byte(); const int value = any(); engine->controlChange (controller, value, input.Byte() % 18); break; }
            case 4: { const float semitones = input.Scalar() * 96.0f - 48.0f; engine->pitchBend (semitones, input.Byte() % 18); break; }
            case 5:
            {
                // One raw write, which may be any float, to any control.
                float* fields[] { &parameters.gain, &parameters.hammer, &parameters.age, &parameters.detune,
                                  &parameters.stretch, &parameters.dynamics, &parameters.lid, &parameters.soundboard,
                                  &parameters.sympathetic, &parameters.duplex, &parameters.mic[0], &parameters.mic[1],
                                  &parameters.mic[2], &parameters.mic[3], &parameters.room, &parameters.width,
                                  &parameters.tuning, &parameters.felt, &parameters.mute, &parameters.sustain,
                                  &parameters.sostenuto, &parameters.soft, &parameters.mechanics };
                float& field = *fields[input.Pick (std::size (fields))];
                field = input.Scalar();
                engine->setParameters (parameters);
                break;
            }
            case 6:
                parameters = keyra::withPreset (parameters, keyra::factoryPresets[input.Pick (keyra::factoryPresets.size())]);
                engine->setParameters (parameters);
                break;
            case 7: engine->reset(); break;
            case 8: engine->prepare (input.Rate()); break;
            // Any piano, including one that does not exist.
            default:
                parameters.body = static_cast<keyra::model::Body> (static_cast<int> (input.Byte()) - 8);
                engine->setParameters (parameters);
                break;
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
