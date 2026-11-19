// Late diffuse coherence of each XY pair, through the actual room and capsules.
#include "DSP/PianoModel.h"
#include <array>
#include <cmath>
#include <iostream>
#include <vector>

namespace {
using keyra::model::Body;
using keyra::model::Controls;
using keyra::model::Piano;

constexpr int rate = 48000;
using Stereo = std::array<std::vector<float>, 2>;

Stereo bridgeImpulse(Piano& piano, Controls controls, int key, bool room) {
    controls.roomHeard = room;
    piano.setControls(controls);
    piano.reset();
    piano.knockBridge(key, .005f);
    Stereo out;
    for (auto& channel : out) channel.resize(3 * rate / 5);
    piano.process(out[0].data(), out[1].data(), static_cast<int>(out[0].size()));
    return out;
}

double lateCoherence(Piano& piano, Body body) {
    Controls controls;
    controls.body = body;
    controls.soundboard = controls.sympathetic = controls.duplex = 0;
    controls.room = .85f;
    controls.mic[keyra::model::micClose] = 0;
    controls.mic[keyra::model::micXY] = 1;
    double ll = 0, rr = 0, lr = 0;
    for (int key : {27, 63}) {
        const auto dry = bridgeImpulse(piano, controls, key, false);
        const auto wet = bridgeImpulse(piano, controls, key, true);
        // Remove the direct sound and omit the first 200 ms of arrivals.
        for (std::size_t i = rate / 5; i < wet[0].size(); ++i) {
            const double l = wet[0][i] - dry[0][i], r = wet[1][i] - dry[1][i];
            ll += l * l;
            rr += r * r;
            lr += l * r;
        }
    }
    return lr / std::sqrt(ll * rr);
}
}

int main() {
    Piano piano;
    const double grand = lateCoherence(piano, Body::concertGrand);
    const double upright = lateCoherence(piano, Body::upright);
    // Coincident cardioids have coherence (3 + dot(leftAxis, rightAxis)) / 4.
    // The grand tilts down toward the strings, dot = .4202; the upright's
    // axes are perpendicular. Allow for the finite diffuse decay measured.
    std::cout << "XY tail correlation, concert grand " << grand << ", upright " << upright << '\n';
    return std::abs(grand - .855) < .025 && std::abs(upright - .75) < .025 ? 0 : 1;
}
