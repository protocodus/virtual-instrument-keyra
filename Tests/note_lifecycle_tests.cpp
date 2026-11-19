// The contact allocator and a string's modal state across repeat strikes.
#include "DSP/PianoModel.h"
#include <algorithm>
#include <cmath>
#include <iostream>
#include <numeric>
#include <vector>

namespace {
using keyra::model::Controls;
using keyra::model::keyCount;
using keyra::model::Piano;

struct Stereo {
    std::vector<float> left, right;
    explicit Stereo(int length) : left(length), right(length) {}
    void render(Piano& piano) {
        piano.process(left.data(), right.data(), static_cast<int>(left.size()));
    }
    bool operator==(const Stereo& other) const {
        return left == other.left && right == other.right;
    }
};

Controls dry() {
    Controls controls;
    controls.sympathetic = controls.duplex = 0;
    controls.roomHeard = false;
    return controls;
}

Stereo chord(Piano& piano, const std::vector<int>& keys) {
    piano.reset();
    for (int key : keys) {
        piano.holdDamper(key, true);
        piano.strike(key, .7f);
    }
    Stereo take(2048);
    take.render(piano);
    return take;
}

bool allHammersSound(Piano& piano) {
    piano.setControls(dry());
    std::vector<int> keys(keyCount);
    std::iota(keys.begin(), keys.end(), 0);
    const auto all = chord(piano, keys);
    std::reverse(keys.begin(), keys.end());
    if (!(chord(piano, keys) == all)) return false;

    // When every hammer is already claimed, another strike of the last
    // key can replace its own unstarted blow without stealing a neighbor.
    keys.push_back(keys.back());
    if (!(chord(piano, keys) == all)) return false;

    // A still-missing key may reclaim a duplicate from a different key.
    std::iota(keys.begin(), keys.begin() + keyCount, 0);
    keys[keyCount - 1] = keys.front();
    keys.back() = keyCount - 1;
    if (!(chord(piano, keys) == all)) return false;

    // The first blow in a same-frame cluster must actually reach its string.
    keys.resize(25);
    const auto cluster = chord(piano, keys);
    keys.erase(keys.begin());
    return !(cluster == chord(piano, keys));
}

bool stalledHammerRests(Piano& piano) {
    constexpr int rate = 48000;
    piano.prepare(rate);
    auto controls = dry();
    controls.hammer = -1;
    controls.dynamics = controls.felt = controls.mute = 1;
    piano.setControls(controls);
    // With the soft pedal down, these A0 blows time out while still near
    // the string. Dividing the catch distance by their tiny rebound speeds
    // formerly scheduled one over a minute later and overflowed an int for the other.
    for (float velocity : {.0131f, .0130248852f}) {
        piano.reset();
        piano.strike(0, velocity, 1);
        Stereo tail(256);
        for (int i = 0; i < 8 * rate / 256 && !piano.silent(); ++i) tail.render(piano);
        if (!piano.silent()) return false;
    }
    return true;
}

bool retiredModesStaySilent(Piano& piano) {
    constexpr int rate = 22050, key = 96 - 21;
    piano.prepare(rate);
    auto controls = dry();
    piano.setControls(controls);
    piano.holdDamper(key, true);
    piano.strike(key, 1.f);
    Stereo advance(224);
    advance.render(piano);
    // The wheel takes the loud fourth partial past the Nyquist guard.
    piano.setBend(2);
    Stereo step(32);
    step.render(piano);
    piano.holdDamper(key, false);
    controls.mute = 1;
    piano.setControls(controls);
    Stereo tail(256);
    for (int i = 0; i < 12 * rate / 256 && !piano.silent(); ++i) tail.render(piano);
    if (!piano.silent()) return false;

    controls.mute = 0;
    piano.setControls(controls);
    piano.setBend(0);
    const auto repeat = [&] {
        piano.holdDamper(key, true);
        piano.strike(key, .2f);
        Stereo result(2240);
        result.render(piano);
        return result;
    };
    const auto afterBend = repeat();
    piano.reset();
    const auto fresh = repeat();
    double delta = 0, energy = 0;
    for (std::size_t i = 0; i < fresh.left.size(); ++i) {
        const double l = fresh.left[i], r = fresh.right[i];
        const double dl = afterBend.left[i] - l, dr = afterBend.right[i] - r;
        delta += dl * dl + dr * dr;
        energy += l * l + r * r;
    }
    std::cout << "Relative RMS after quiet repeat at 22.05 kHz: "
              << std::sqrt(delta / energy) << '\n';
    return energy > 0 && delta < 1e-10 * energy;
}
}

int main() {
    Piano piano;
    const bool contacts = allHammersSound(piano);
    const bool modes = retiredModesStaySilent(piano);
    const bool catchRests = stalledHammerRests(piano);
    if (!contacts) std::cerr << "A dense chord lost a hammer or depended on note order\n";
    if (!modes) std::cerr << "A frequency removed by the bend returned on a quiet strike\n";
    if (!catchRests) std::cerr << "An unreturned hammer scheduled a catch after the piano fell silent\n";
    return contacts && modes && catchRests ? 0 : 1;
}
