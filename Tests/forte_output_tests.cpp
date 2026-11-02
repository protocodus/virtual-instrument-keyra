// Compare the public output stage with the approved half-drive audition signal.
// This reference has no final peak protection, so its over-ceiling frames
// also prove that the safety path actually engaged.
#include "DSP/ForteOutput.h"
#include <cmath>
#include <cstdlib>
#include <iostream>
#include <stdexcept>
#include <vector>

using Frame = keyra::ForteOutput::Frame;
using Stage = keyra::ForteOutput::Stage;

static void require(bool pass, const char* message) {
    if (!pass) throw std::runtime_error(message);
}

static double peak(const Frame& frame) {
    return std::max(std::abs(frame[0]), std::abs(frame[1]));
}

static void verify(double rate) {
    keyra::ForteOutput piano;
    piano.Prepare(rate);
    Stage audition;
    audition.Prepare(rate, protocodus::kVuGuard);
    const int window = std::max(1, audition.DelaySamples() / 8);
    const int extra = 2 * window;
    const int latency = audition.DelaySamples() + extra;
    require(piano.DelaySamples() == latency && keyra::ForteOutput::DelayFor(rate) == latency,
            "reported delay disagrees with the two look-ahead stages");

    for (int i = 0; i <= latency; ++i) {
        const Frame frame = piano.Process(i == 0 ? .125 : 0., 0.);
        require(frame[0] == (i == latency ? .125f : 0.f) && frame[1] == 0.f,
                "quiet impulse did not emerge unchanged at the declared frame");
    }
    piano.Reset();
    const int total = static_cast<int>(rate / 2);
    std::vector<Frame> target(total), actual(total);
    std::vector<double> blockPeak((total + window - 1) / window);
    for (int i = 0; i < total; ++i) {
        const double t = i / rate;
        // Isolated peaks on either side of block boundaries, a bass onset,
        // different stereo phases and a quiet tail.
        double left = .08 * std::sin(2. * 3.141592653589793 * 220. * t);
        double right = -.6 * left;
        if (i % (7 * window) == window - 1 && t < .1) left += 2.1;
        if (i % (11 * window) == 0 && t < .1) right -= 2.8;
        if (t >= .1 && t < .22) {
            left += 2. * std::sin(2. * 3.141592653589793 * 27.5 * t);
            right += 1.8 * std::cos(2. * 3.141592653589793 * 55. * t);
        }
        actual[i] = piano.Process(left, right);
        Frame reference{static_cast<float>(.5 * left), static_cast<float>(.5 * right)};
        audition.Process(reference);
        for (auto& sample : reference) sample *= 2.f;
        target[i] = reference;
        blockPeak[i / window] = std::max(blockPeak[i / window], peak(reference));
    }
    int over = 0, exact = 0;
    for (int i = 0; i < total; ++i) {
        const auto& out = actual[i];
        require(std::isfinite(out[0]) && std::isfinite(out[1]) && peak(out) <= Stage::kCeiling,
                "nonfinite sample or breached stereo ceiling");
        if (i < extra) continue;
        const int source = i - extra;
        const auto& reference = target[source];
        const int block = source / window;
        if (block > 0 && block + 1 < static_cast<int>(blockPeak.size()) &&
            std::max({blockPeak[block - 1], blockPeak[block], blockPeak[block + 1]}) <= Stage::kCeiling) {
            require(out == reference, "safe audition audio was altered beyond the crest");
            ++exact;
        }
        if (peak(reference) > Stage::kCeiling) ++over;
        require(peak(out) <= peak(reference), "crest guard increased a sample");
        const double stereoError = double(out[0]) * reference[1] - double(out[1]) * reference[0];
        require(std::abs(stereoError) < 2.e-7, "crest guard changed the stereo image");
    }
    require(over > 0 && exact > total / 2, "probe did not exercise both protection and clear audio");
    piano.Process(3., -2.);
    piano.Reset();
    for (int i = 0; i < latency + window; ++i)
        require(piano.Process(0., 0.) == Frame{}, "reset retained previous audio");
}

int main() {
    try {
        for (double r : {8000., 22050., 44100., 48000., 88200., 96000., 192000.}) verify(r);
        std::cout << "Approved B level, stereo, ceiling, latency and reset passed at seven rates\n";
        return EXIT_SUCCESS;
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return EXIT_FAILURE;
    }
}
