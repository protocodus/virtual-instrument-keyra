#pragma once

#include "OutputStage.h"

namespace keyra {

// B in the forte audition drove the existing guard at half level. Doubling
// its output restores the uncompressed playing level exactly. A stereo crest
// guard catches the occasional peak this puts above the original ceiling.
class ForteOutput {
public:
    using Frame = std::array<float, 2>;
    using Stage = protocodus::OutputStage<2>;
    static constexpr int maxBlock = Stage::kMaximumDelay / 8;
    static constexpr int maxDelay = Stage::kMaximumDelay + 2 * maxBlock;

    static int DelayFor(double sampleRate) noexcept {
        const int primary = Stage::DelayFor(sampleRate);
        return primary + 2 * std::max(1, primary / 8);
    }

    void Prepare(double sampleRate) noexcept {
        primary_.Prepare(sampleRate, protocodus::kVuGuard);
        blockSize_ = std::max(1, primary_.DelaySamples() / 8);
        phaseScale_ = 1. / blockSize_;
        Reset();
    }

    int DelaySamples() const noexcept { return primary_.DelaySamples() + 2 * blockSize_; }

    void Reset() noexcept {
        primary_.Reset();
        std::fill_n(delay_.begin(), 2 * blockSize_, Frame{});
        blockGains_.fill(1.);
        sampleIndex_ = blockIndex_ = phase_ = 0;
        blockPeak_ = 0.f;
        startGain_ = endGain_ = 1.;
    }

    Frame Process(double left, double right) noexcept {
        // The historical +/-4 emergency bound applies at the guard input.
        Frame frame{input(left), input(right)};
        primary_.Process(frame);
        for (auto& sample : frame) sample *= 2.f;
        return protectCrest(frame);
    }

private:
    static float input(double value) noexcept {
        return static_cast<float>(std::clamp(.5 * value, -4., 4.));
    }

    Frame protectCrest(const Frame& inputFrame) noexcept {
        Frame result = delay_[sampleIndex_];
        delay_[sampleIndex_] = inputFrame;
        if (++sampleIndex_ == 2 * blockSize_) sampleIndex_ = 0;

        blockPeak_ = std::max({blockPeak_, std::abs(inputFrame[0]), std::abs(inputFrame[1])});
        if (phase_ == 0) {
            // Two short blocks behind the input, both neighbors are known.
            // Each boundary takes the smaller gain of its adjacent blocks.
            // The entire curve within a block therefore obeys its peak bound.
            const double center = blockGains_[(blockIndex_ + 2) % 4];
            startGain_ = std::min(center, blockGains_[(blockIndex_ + 1) % 4]);
            endGain_ = std::min(center, blockGains_[(blockIndex_ + 3) % 4]);
        }
        if (startGain_ < 1. || endGain_ < 1.) {
            const double time = phase_ * phaseScale_;
            const double curve = time * time * (3. - 2. * time);
            const double gain = startGain_ + (endGain_ - startGain_) * curve;
            for (auto& sample : result) sample = static_cast<float>(sample * gain);
        }
        if (++phase_ == blockSize_) {
            blockGains_[blockIndex_] = blockPeak_ > Stage::kCeiling
                ? static_cast<double>(Stage::kCeiling) / blockPeak_ : 1.;
            blockIndex_ = (blockIndex_ + 1) % 4;
            phase_ = 0;
            blockPeak_ = 0.f;
        }
        return result;
    }

    Stage primary_;
    std::array<Frame, 2 * maxBlock> delay_{};
    std::array<double, 4> blockGains_{};
    int blockSize_ = 1, sampleIndex_ = 0, blockIndex_ = 0, phase_ = 0;
    float blockPeak_ = 0.f;
    double phaseScale_ = 1., startGain_ = 1., endGain_ = 1.;
};

} // namespace keyra
