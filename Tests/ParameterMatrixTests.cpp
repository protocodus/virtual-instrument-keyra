// U4 parameter-extremes matrix over the plug-in processor, through the shared
// portfolio harness (Tests/ParameterMatrix.h is a byte-identical copy of the
// master; change it in reason-rack-extensions).
//
//   KeyraParameterMatrixTests [--jobs N] [--rotation] [--shard K/N]
//                             [--case LABEL] [--count]
//
// --rotation runs each case at one rate and block size instead of all nine,
// --shard runs every Nth case starting at K (1-based), --case runs only the
// case a FAIL line names, and --count only prints how many cases there are.
//
// The limits below follow from Source/DSP/KeyraEngine.cpp; each one names
// the mechanism it comes from.

#include "PluginProcessor.h"
#include "ParameterMatrix.h"
#include "DSP/KeyraPresets.h"
#include "DSP/OutputStage.h"

#include <algorithm>
#include <cstdio>
#include <cstdlib>
#include <map>
#include <string>

namespace
{
using protocodus::matrix::Case;
using protocodus::matrix::Limits;

class KeyraDevice final : public protocodus::matrix::JuceDevice
{
public:
    KeyraDevice() : JuceDevice (std::make_unique<KeyraAudioProcessor>())
    {
        for (auto* parameter : processor->getParameters())
            if (parameter->isAutomatable())
                if (auto* ranged = dynamic_cast<juce::RangedAudioParameter*> (parameter))
                    columns[ranged->paramID.toStdString()] = { automatable++, ranged };
    }

    Limits LimitsFor (const Case& c) const override
    {
        Limits limits;
        // The shared output stage ends process() after the output gain, so
        // no sample passes its limiter's ceiling, -1.5 dBFS, at any Output;
        // the margin is the float rounding its own test allows.
        limits.ceiling = protocodus::OutputStage<2>::kCeiling * (1.0f + 1.0e-6f);
        // Output at zero is silent by design, in whichever row has it. So are
        // held notes under the felt mute, which is what it is for: control()
        // adds 180 m^2 (0.5 + 0.00015 f) nepers per second of loss to held
        // strings, 40 dB on the chord's G4 by the held window at Felt
        // Nocturne's 0.32. Whether a muted chord is still above the -60 dBFS
        // floor then depends on its level, so the check holds only with the
        // felt off in both rows.
        limits.soundsWhileHeld = std::min (value (c.values, "gain"), value (c.base, "gain")) > 0.0
                              && std::max (value (c.values, "mute"), value (c.base, "mute")) == 0.0;
        // The ramp is back on the case's own values before note-off, so the
        // case row decides the release. Any sustain lifts the dampers part
        // way (control(): target 1 - sustain), and a sostenuto at or above
        // its 0.5 threshold catches the held chord when the ramp brings it
        // back up (capture()), so those strings ring on after the keys go up.
        if (value (c.values, "sustain") > 0.0 || value (c.values, "sostenuto") >= 0.5)
            limits.releaseSeconds = -1.0;
        // The upright's dampers hold part of each partial only loosely, as its
        // release takes show (setDamper(), measured::Damper): C4's keeps 12.9 dB
        // under the partial and falls about 6 dB a second, lower keys more of
        // it and slower. At -9 VU typical playing (Tools/KeyraLevels.cpp) the
        // chord's strings sit at the -60 dBFS floor 2 s after the release, and
        // at full Output 3 dB over it, so silence is due a second later.
        else if (c.preset >= 0 && keyra::factoryPresets[static_cast<std::size_t> (c.preset)].piano == keyra::Piano::upright)
            limits.releaseSeconds = 3.0;
        return limits;
    }

private:
    struct Column
    {
        std::size_t index;
        juce::RangedAudioParameter* parameter;
    };

    // A row's value of one parameter in its own units.
    double value (const std::vector<float>& row, const std::string& id) const
    {
        const auto& column = columns.at (id);
        return column.parameter->convertFrom0to1 (row[column.index]);
    }

    std::size_t automatable = 0;
    std::map<std::string, Column> columns;
};
} // namespace

int main (int argc, char** argv)
{
    juce::ScopedJuceInitialiser_GUI juce;
    protocodus::matrix::Options options;
    int shard = 1, shards = 1;
    bool countOnly = false;
    std::string only;
    for (int i = 1; i < argc; ++i)
    {
        const std::string arg = argv[i];
        if (arg == "--rotation") options.everyConfiguration = false;
        else if (arg == "--count") countOnly = true;
        else if (arg == "--jobs" && i + 1 < argc) options.jobs = std::atoi (argv[++i]);
        else if (arg == "--case" && i + 1 < argc) only = argv[++i];
        else if (arg == "--shard" && i + 1 < argc
                 && std::sscanf (argv[++i], "%d/%d", &shard, &shards) == 2
                 && shards >= 1 && shard >= 1 && shard <= shards) {}
        else
        {
            std::fprintf (stderr, "usage: %s [--jobs N] [--rotation] [--shard K/N] [--case LABEL] [--count]\n", argv[0]);
            return 2;
        }
    }
    const auto make = [] { return std::make_unique<KeyraDevice>(); };
    if (countOnly)
    {
        auto probe = make();
        probe->Prepare (48000.0, 512);
        std::printf ("%zu cases\n", protocodus::matrix::Cases (*probe).size());
        return 0;
    }
    options.select = [shard, shards, only] (std::size_t index, const Case& c)
    {
        return static_cast<int> (index % static_cast<std::size_t> (shards)) == shard - 1
            && (only.empty() || c.label == only);
    };
    return protocodus::matrix::Run (make, options) == 0 ? 0 : 1;
}
