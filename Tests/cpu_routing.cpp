// The portfolio demo budget measures stereo at 48 kHz in 256-frame blocks.
// Measure the same stress events with each physical microphone bus connected.
#include "DSP/KeyraEngine.h"
#include "DSP/OutputStage.h"
#include "../Tools/PresetDemoRenderer.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <cstdio>
#include <ctime>
#include <fstream>
#include <numeric>
#include <vector>

namespace {
constexpr int blockFrames = 64;
constexpr int channels = 12;
using Clock = std::chrono::steady_clock;

#if defined(CLOCK_THREAD_CPUTIME_ID)
double threadTime() {
    timespec time{};
    return clock_gettime(CLOCK_THREAD_CPUTIME_ID, &time) == 0
        ? static_cast<double>(time.tv_sec) + 1.0e-9 * time.tv_nsec : -1.0;
}
#endif

void dispatch(keyra::Engine& engine, const protocodus::demos::MidiEvent& event) {
    const auto& b = event.bytes;
    switch (b[0] & 0xf0) {
        case 0x80: engine.noteOff(b[1]); break;
        case 0x90: engine.noteOn(b[1], b[2] / 127.0f); break;
        case 0xb0: engine.controlChange(b[1], b[2]); break;
    }
}

bool measure(keyra::Engine& engine, int rate, bool direct, std::ostream& json) {
    const auto events = protocodus::demos::StressPhrase();
    const int total = static_cast<int>(std::llround((events.back().seconds + 1.0) * rate));
    const double deadline = static_cast<double>(blockFrames) / rate;
    std::array<std::array<float, blockFrames>, channels> samples{};
    std::array<float, channels> peaks{};
    std::vector<double> times;
    times.reserve(total / blockFrames + 1);
    engine.reset();
    std::size_t next = 0;
    bool finite = true;
    int missed = 0;
#if defined(CLOCK_THREAD_CPUTIME_ID)
    double cpuTotal = 0.0;
    int cpuSamples = 0, cpuMissed = 0;
#endif
    for (int first = 0; first < total; first += blockFrames) {
        const int count = std::min(blockFrames, total - first);
#if defined(CLOCK_THREAD_CPUTIME_ID)
        const double cpuStart = threadTime();
#endif
        const auto start = Clock::now();
        for (int offset = 0; offset < count;) {
            const int now = first + offset;
            while (next < events.size() && std::llround(events[next].seconds * rate) <= now)
                dispatch(engine, events[next++]);
            const int later = next < events.size() ? static_cast<int>(std::llround(events[next].seconds * rate)) : total;
            const int n = std::min(count - offset, later - now);
            std::array<float*, channels - 2> microphones{};
            if (direct)
                for (int c = 2; c < channels; ++c)
                    microphones[c - 2] = samples[c].data() + offset;
            engine.process(samples[0].data() + offset, samples[1].data() + offset,
                           direct ? microphones.data() : nullptr, n);
            offset += n;
        }
        const double elapsed = std::chrono::duration<double>(Clock::now() - start).count();
#if defined(CLOCK_THREAD_CPUTIME_ID)
        const double cpuEnd = threadTime();
        if (cpuStart >= 0.0 && cpuEnd >= cpuStart) {
            cpuTotal += cpuEnd - cpuStart;
            cpuMissed += cpuEnd - cpuStart > static_cast<double>(count) / rate;
            ++cpuSamples;
        }
#endif
        times.push_back(elapsed);
        missed += elapsed > static_cast<double>(count) / rate;
        for (int c = 0; c < (direct ? channels : 2); ++c)
            for (int i = 0; i < count; ++i) {
                const float value = samples[c][i];
                finite &= std::isfinite(value);
                peaks[c] = std::max(peaks[c], std::abs(value));
            }
    }
    std::sort(times.begin(), times.end());
    const double mean = std::accumulate(times.begin(), times.end(), 0.0) / times.size();
    const double p99 = times[static_cast<std::size_t>(std::ceil(0.99 * times.size())) - 1];
    const float mainPeak = std::max(peaks[0], peaks[1]);
    const float ceiling = protocodus::OutputStage<2>::kCeiling * (1.0f + 1.0e-6f);
    const bool audible = std::all_of(peaks.begin(), peaks.begin() + (direct ? channels : 2),
                                     [](float peak) { return peak > 1.0e-5f; });
    const bool valid = finite && audible && mainPeak <= ceiling && next == events.size();
    const char* route = direct ? "main_and_five_mics" : "main";
    std::printf("%s %d Hz %s, 64 frames: %.3f ms mean / %.3f ms p99 / %.3f ms max, "
                "%d/%zu over %.3f ms, main peak %.5f\n",
                !valid ? "FAIL" : missed ? "WARN" : "PASS", rate, route, 1000 * mean, 1000 * p99,
                1000 * times.back(), missed, times.size(), 1000 * deadline, mainPeak);
    json << "{\"sample_rate\":" << rate << ",\"route\":\"" << route << "\",\"block_frames\":" << blockFrames
         << ",\"blocks\":" << times.size() << ",\"wall_mean_ms\":" << 1000 * mean
         << ",\"wall_p99_ms\":" << 1000 * p99 << ",\"wall_max_ms\":" << 1000 * times.back()
         << ",\"deadline_ms\":" << 1000 * deadline << ",\"missed_deadlines\":" << missed
         << ",\"main_peak\":" << mainPeak << ",\"audio_valid\":" << (valid ? "true" : "false");
#if defined(CLOCK_THREAD_CPUTIME_ID)
    if (cpuSamples == static_cast<int>(times.size())) {
        const double cpuMean = 1000 * cpuTotal / cpuSamples;
        json << ",\"thread_cpu_mean_ms\":" << cpuMean << ",\"thread_cpu_missed_deadlines\":" << cpuMissed;
        std::printf("  calling thread %.3f ms mean, %d/%d over deadline\n", cpuMean, cpuMissed, cpuSamples);
    }
#endif
    json << "}";
    return valid;
}
}

int main(int argc, char** argv) {
    if (argc != 2) {
        std::fprintf(stderr, "usage: KeyraCpuRouting OUTPUT.json\n");
        return 2;
    }
    std::ofstream json(argv[1]);
    if (!json) return 2;
    keyra::Engine engine;
    bool valid = true;
    json << "[\n";
    for (int rate : {48000, 96000, 192000}) {
        engine.prepare(rate);
        for (bool direct : {false, true}) {
            if (rate != 48000 || direct) json << ",\n";
            valid &= measure(engine, rate, direct, json);
        }
    }
    json << "\n]\n";
    json.close();
    return valid && json ? 0 : 1;
}
