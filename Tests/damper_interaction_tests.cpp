// Exercise the public event/render path. Read the struck voice and the receiving
// bank in this test's single translation unit so their physical behavior can be
// compared independently of the microphone mix. Never modify engine state here.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <iostream>
#include <limits>
#include <memory>
#include <stdexcept>
#include <vector>
#include "DSP/KeyraEngine.cpp"

namespace keyra {
struct DamperTestObserver {
    static const auto& state(const Engine& engine) noexcept { return *engine.impl; }
};
}

namespace {
const auto& state(const keyra::Engine& e) { return keyra::DamperTestObserver::state(e); }

using Audio = std::vector<float>;
constexpr int receiver = 48; // C3's second partial is driven by the C4 strike.

void require(bool ok, const char* message) {
    if (!ok) throw std::runtime_error(message);
}

keyra::Parameters controls(keyra::Piano piano, float resonance = 1.f) {
    keyra::Parameters p;
    p.build = keyra::measuredBuild(piano);
    p.resonance = resonance;
    p.mechanics = 0;
    p.gain = .05f;
    return p;
}

Audio render(keyra::Engine& e, int frames, int block) {
    Audio out(static_cast<std::size_t>(2 * frames));
    std::array<float, 257> left{}, right{};
    for (int at = 0; at < frames;) {
        const int count = std::min(block, frames - at);
        e.process(left.data(), right.data(), count);
        for (int i = 0; i < count; ++i) {
            out[2 * (at + i)] = left[i];
            out[2 * (at + i) + 1] = right[i];
        }
        at += count;
    }
    return out;
}

const keyra::Voice& voice(const keyra::Engine& e, int key, int channel) {
    for (const auto& v : state(e).voices)
        if (v.active && v.note == key && v.channel == channel - 1) return v;
    throw std::runtime_error("expected a sounding voice");
}

// One felt damps a key's direct and sympathetic vibration. The independently
// advanced direct voice provides the reference throughout a rapid repedal.
void sharedFelt(keyra::Piano piano) {
    keyra::Engine e;
    e.setParameters(controls(piano));
    e.reset();
    e.noteOn(receiver, .6f);
    render(e, 3072, 127);
    e.noteOff(receiver);
    const auto advance = [&](int chunks) {
        for (int i = 0; i < chunks; ++i) {
            render(e, keyra::chunk, 13);
            const double free = 1.0 - voice(e, receiver, 1).contact;
            const auto& bank = state(e).open[(receiver - 21) * keyra::openPartials / keyra::lanes];
            const float fullDrive = static_cast<float>(1.0 - bank.decay[0]);
            const float expected = static_cast<float>((1.0 - bank.decay[0]) * free);
            require(std::abs(keyra::lane(bank.drive, 0) - expected)
                        <= 4 * std::numeric_limits<float>::epsilon() * fullDrive,
                    "the receiver drive and direct string disagree about felt contact");
        }
        return state(e).openness[receiver - 21];
    };
    const double falling = advance(16);
    require(falling > 0 && falling < 1, "a released damper has no intermediate travel");
    e.controlChange(64, 127);
    const double caught = advance(5);
    require(caught > falling && caught < 1, "repedaling did not catch the moving receiver damper");
    e.controlChange(64, 32);
    require(advance(5) < caught, "the damper did not reverse toward partial contact");
}

void restrikeOwnership(keyra::Piano piano) {
    keyra::Engine e;
    e.setParameters(controls(piano));
    e.reset();
    e.noteOn(receiver, .7f, 1);
    render(e, 3072, 127);
    e.noteOff(receiver, 1);
    render(e, 515, 127); // The next events fall inside an engine chunk.
    const auto& original = voice(e, receiver, 1);
    const double down = original.damper;
    require(down > 0 && original.contact > 0, "restrike control has no engaged felt");
    e.noteOn(receiver, .3f, 2);
    require(original.damper == down, "a foreign-channel strike lifted a direct voice's damper");
    render(e, 32, 13);
    require(state(e).openness[receiver - 21] == 1 && original.contact > 0,
            "shared receiver and channel-owned struck voice must have distinct key ownership");
    e.controlChange(66, 127, 2);
    e.noteOff(receiver, 2);
    render(e, 160, 13);
    require(state(e).openness[receiver - 21] == 1 && original.contact > 0,
            "sostenuto capture lost its shared receiver or lifted another channel's direct voice");
    e.controlChange(66, 0, 2);
    render(e, 256, 13);
    require(state(e).openness[receiver - 21] < 1, "released capture left the receiver fully open");
    const auto prior = original.partials[0].exact[0];
    const auto serial = original.serial;
    const double slowShare = original.partials[0].slowShare;
    e.noteOn(receiver, .4f, 1);
    require(original.damper == 0 && original.serial == serial && original.active,
            "same-channel restrike did not lift the felt off the earlier voice");
    const auto after = original.partials[0].exact[0];
    require(prior.re == after.re && prior.im == after.im && original.partials[0].slowShare == slowShare,
            "reopening the damper restarted an earlier vibration");
    render(e, 32, 7);
    require(original.contact == 0, "reopened direct voice retains felt after the next boundary");
    e.noteOn(89, .5f, 1);
    render(e, 1024, 127);
    e.noteOff(89, 1);
    render(e, 1024, 127);
    require(voice(e, 89, 1).contact == 0, "key release applied a damper to F6");
}

// Two public render pairs isolate sympathetic radiation. A nearly silent held
// C3 receives energy from C4. CC120 on C4's channel removes the driver while
// C3 keeps the bank alive. Release C3 in one pair. At 48 kHz the existing
// 18 ms travel takes more than two 32-sample chunks to reach first contact
// (8% of travel). A receiver that jumps closed differs immediately instead.
Audio receiverTail(keyra::Piano piano, bool release, float resonance, int block) {
    keyra::Engine e;
    e.setParameters(controls(piano, resonance));
    e.reset();
    e.noteOn(receiver, .00001f, 2);
    render(e, 2048, block);
    e.noteOn(60, .8f, 1);
    render(e, 8192, block);
    e.controlChange(120, 0, 1);
    render(e, 512, block);
    if (release) e.noteOff(receiver, 2);
    return render(e, 4800, block);
}

void audibleTravel(keyra::Piano piano) {
    const auto wetHeld = receiverTail(piano, false, 1, 127);
    const auto dryHeld = receiverTail(piano, false, 0, 127);
    const auto wetFall = receiverTail(piano, true, 1, 127);
    const auto dryFall = receiverTail(piano, true, 0, 127);
    const int earlySamples = 2 * (keyra::ForteOutput::DelayFor(48000) + 2 * keyra::chunk);
    double earlyEnergy = 0, lateDifference = 0;
    for (std::size_t i = 0; i < wetHeld.size(); ++i) {
        const double held = double(wetHeld[i]) - dryHeld[i];
        const double fall = double(wetFall[i]) - dryFall[i];
        if (i < static_cast<std::size_t>(earlySamples)) {
            require(held == fall, "receiver radiation changes before the falling felt can reach the string");
            earlyEnergy += held * held;
        } else lateDifference += (held - fall) * (held - fall);
    }
    require(earlyEnergy > 0 && lateDifference > 0, "receiver tail is absent or unaffected by damper travel");
}

void resetAndPartition(keyra::Piano piano) {
    keyra::Engine history, fresh;
    const auto p = controls(piano);
    history.setParameters(p);
    history.noteOn(receiver, .8f);
    render(history, 2048, 127);
    history.noteOff(receiver);
    history.controlChange(64, 70);
    render(history, 515, 127);
    history.reset();
    fresh.setParameters(p);
    fresh.reset();
    const auto play = [](keyra::Engine& e, int block) {
        Audio result;
        const auto advance = [&](int frames) {
            const auto part = render(e, frames, block);
            result.insert(result.end(), part.begin(), part.end());
        };
        e.noteOn(receiver, .6f); advance(1003);
        e.noteOff(receiver); advance(341);
        e.controlChange(64, 100); advance(257);
        e.noteOn(receiver, .3f); advance(371);
        e.controlChange(64, 0); e.noteOff(receiver); advance(2048);
        return result;
    };
    const auto replay = play(history, 7);
    require(replay == play(fresh, 7), "hard reset retained a previous damper or receiver state");
    fresh.reset();
    const auto partitioned = play(fresh, 257);
    double peak = 0, error = 0;
    for (std::size_t i = 0; i < replay.size(); ++i) {
        peak = std::max(peak, std::abs(double(replay[i])));
        error = std::max(error, std::abs(double(replay[i]) - partitioned[i]));
    }
    require(peak > 0 && error <= 8 * std::numeric_limits<float>::epsilon() * peak,
            "host blocks changed damper travel or restrike timing");
}
// Silent blocks do not run the oscillator banks, but the physical pedal must
// have traveled for the elapsed time before the next attack wakes them.
void pedalFromSilence(keyra::Piano piano) {
    for (const int lead : {0, 480, 48000}) {
        keyra::Engine e(48000);
        e.setParameters(controls(piano));
        e.reset();
        render(e, 4800, 127);
        e.controlChange(64, 127);
        if (lead) render(e, lead, 257);
        e.noteOn(72, .8f);
        render(e, keyra::chunk, 13);
        const double target = 1 - keyra::dampersLift;
        const double expected = target + (1 - target) * std::exp(-(lead + keyra::chunk) / (48000. * keyra::damperTravelSeconds));
        require(std::abs(state(e).receiverDamper[60-21] - expected) < 1e-8,
                "a silent pedal change lost its elapsed travel before the attack");
        e.controlChange(64, 0);
        render(e, 48000, 257);
        require(state(e).openness[60-21] == 0 && !state(e).open[(60-21)*keyra::openPartials/keyra::lanes].active,
                "a closed, silent receiver failed to retire");
    }
}

void silentPanelHandoff(keyra::Piano piano) {
    const auto target = [](float sustain) { return 1. - keyra::dampersLift * sustain; };
    const auto after = [](double start, double end, int frames) {
        return end + (start - end) * std::exp(-frames / (48000. * keyra::damperTravelSeconds));
    };
    const auto felt = [](const keyra::Engine& e) { return state(e).receiverDamper[receiver - 21]; };
    const auto wakeAndCheck = [&](keyra::Engine& e, double expected) {
        e.noteOn(72, .8f);
        render(e, keyra::chunk, 13);
        require(std::abs(felt(e) - expected) < 1e-8, "silent panel edit teleported a moving receiver");
    };
    // Neither the empty sostenuto capture nor the lower panel sustain can
    // change the MIDI pedal's target. Its original travel must continue.
    for (bool changeSostenuto : {false, true}) {
        keyra::Engine e(48000);
        auto p = controls(piano);
        e.setParameters(p); e.reset();
        e.controlChange(64, 127, 2);
        render(e, 480, 127);
        if (changeSostenuto) p.sostenuto = 1; else p.sustain = .4f;
        e.setParameters(p);
        wakeAndCheck(e, after(1, target(1), 480 + keyra::chunk));
    }
    // The original panel setting is already in position before the first
    // note. Lowering it hands the felt to the CC on a different channel.
    keyra::Engine e(48000);
    auto p = controls(piano);
    p.sustain = 1; e.setParameters(p);
    require(felt(e) == target(1), "an initial panel sustain setting must start settled");
    const float midi = 64 / 127.f;
    e.controlChange(64, 64, 2);
    render(e, 480, 127);
    p.sustain = 0; e.setParameters(p);
    render(e, 240, 127);
    wakeAndCheck(e, after(target(1), target(midi), 240 + keyra::chunk));

    // Reversing towards a new panel target after MIDI release starts at
    // the current felt position, even though no CC is now held.
    e.reset(); e.controlChange(64, 127, 2); render(e, 480, 127);
    e.controlChange(64, 0, 2); render(e, 240, 127);
    const double turning = after(after(1, target(1), 480), 1, 240);
    p.sustain = .75f; e.setParameters(p);
    wakeAndCheck(e, after(turning, target(.75f), keyra::chunk));

    e.noteOn(receiver, .6f, 2); render(e, 32, 13);
    p.sostenuto = 1; e.setParameters(p); e.noteOff(receiver, 2);
    render(e, 64, 13);
    require(felt(e) == 0, "a captured key must stay clear of the felt");
    e.reset();
    require(felt(e) == target(.75f), "reset must clear the capture and restore the panel position");
}

// Independently integrate the actual contact loss while the felt travels.
// Only the excitation fitted from the late pedal ring needs this correction.
void measuredLift() {
    for (const double pedal : {.92, .97, 1.}) {
        const double target = 1. - keyra::dampersLift * pedal;
        for (const double start : {0., .07, .08, .2, .5, 1.}) {
            constexpr int steps = 16000;
            const double dt = 24 * keyra::damperTravelSeconds / steps;
            double loss = 0.;
            for (int i = 0; i < steps; ++i) {
                const double t = (i + .5) * dt;
                const double distance = target + (start - target) * std::exp(-t / keyra::damperTravelSeconds);
                loss += (keyra::feltContact(distance) - keyra::feltContact(target)) * dt;
            }
            const double residual = std::log(keyra::liftImpulseGain(start, target)) - keyra::receiverFeltRate * loss;
            require(std::abs(residual) < 5e-7, "pedal excitation double-counts the changing felt loss");
        }
    }
}
} // namespace

int main() {
    int failures = 0;
    try { measuredLift(); }
    catch (const std::exception& error) { std::cerr << error.what() << '\n'; ++failures; }
    for (int i = 0; i < keyra::pianoCount; ++i) {
        for (const auto test : {sharedFelt, restrikeOwnership, audibleTravel, resetAndPartition, pedalFromSilence, silentPanelHandoff}) {
            try { test(static_cast<keyra::Piano>(i)); }
            catch (const std::exception& error) {
                std::cerr << "model " << i << ": " << error.what() << '\n';
                ++failures;
            }
        }
    }
    if (!failures) std::cout << "Six pianos passed receiver travel, restrike ownership, acoustic tail, reset and partition checks\n";
    return failures ? 1 : 0;
}
