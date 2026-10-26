#include "keyra/Piano.h"
#include "keyra/Parameters.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <vector>

// Diagnostic, not a timing-based test: scheduling and CI hosts vary. The JSON
// records actual callback deadline misses so a fast average cannot hide them.
int main() {
  constexpr unsigned sampleRate = 48000, block = 64;
  constexpr unsigned warmupCallbacks = sampleRate / block;
  constexpr unsigned measuredCallbacks = 3 * sampleRate / block;
  constexpr double deadlineMs = 1000. * block / sampleRate;
  keyra::Piano piano;
  if (!piano.prepare(sampleRate)) {
    std::cerr << "Benchmark sample-rate preparation failed\n";
    return 1;
  }
  piano.setParameter(keyra::ParamId::Resonance, 1);
  piano.setParameter(keyra::ParamId::Distance, .4);
  piano.sustain(1);
  for (int i = 0; i < 64; ++i)
    piano.noteOn(21 + i, .55 + .35 * (i % 7) / 6., 0, i);

  std::array<float, block> l{}, r{};
  std::vector<double> times(measuredCallbacks);
  double checksum = 0, peak = 0;
  unsigned minimumVoices = 64, maximumVoices = 0;
  int nextId = 64;
  const auto renderCallback = [&](unsigned index) {
    // Keep the dense pedal-held texture populated throughout the benchmark,
    // including bounded voice stealing in the measured callback workload.
    if (index % 37 == 0) {
      piano.noteOn(36 + (nextId * 7) % 49, .8, 0, nextId);
      ++nextId;
    }
    piano.process(l.data(), r.data(), block);
  };
  for (unsigned i = 0; i < warmupCallbacks; ++i) renderCallback(i);

  using Clock = std::chrono::steady_clock;
  const auto wallStart = Clock::now();
  for (unsigned i = 0; i < measuredCallbacks; ++i) {
    const auto start = Clock::now();
    renderCallback(i + warmupCallbacks);
    const auto stop = Clock::now();
    times[i] = std::chrono::duration<double, std::milli>(stop - start).count();
    const auto active = static_cast<unsigned>(piano.activeVoices());
    minimumVoices = std::min(minimumVoices, active);
    maximumVoices = std::max(maximumVoices, active);
    for (unsigned j = 0; j < block; ++j) {
      if (!std::isfinite(l[j]) || !std::isfinite(r[j])) {
        std::cerr << "Nonfinite benchmark audio\n";
        return 1;
      }
      checksum += (double(l[j]) + r[j]) * (1 + (j % 11));
      peak = std::max({peak, std::abs(double(l[j])), std::abs(double(r[j]))});
    }
  }
  const double wallSeconds = std::chrono::duration<double>(Clock::now() - wallStart).count();
  double mean = 0;
  unsigned misses = 0;
  for (double elapsed : times) {
    mean += elapsed / times.size();
    if (elapsed > deadlineMs) ++misses;
  }
  std::sort(times.begin(), times.end());
  const double audioSeconds = double(block) * measuredCallbacks / sampleRate;
  const auto p95Index = static_cast<std::size_t>(std::ceil(.95 * times.size())) - 1;
  std::cout << std::setprecision(10)
            << "{\n  \"schema_version\": 1,\n"
            << "  \"scenario\": \"64-voice pedal-held piano, recurring new strikes and voice stealing\",\n"
            << "  \"sample_rate\": " << sampleRate << ",\n"
            << "  \"frames_per_callback\": " << block << ",\n"
            << "  \"callback_deadline_ms\": " << deadlineMs << ",\n"
            << "  \"warmup_audio_seconds\": " << double(block) * warmupCallbacks / sampleRate << ",\n"
            << "  \"measured_audio_seconds\": " << audioSeconds << ",\n"
            << "  \"callbacks\": " << measuredCallbacks << ",\n"
            << "  \"minimum_active_voices\": " << minimumVoices << ",\n"
            << "  \"maximum_active_voices\": " << maximumVoices << ",\n"
            << "  \"callback_mean_ms\": " << mean << ",\n"
            << "  \"callback_p95_ms\": " << times[p95Index] << ",\n"
            << "  \"callback_max_ms\": " << times.back() << ",\n"
            << "  \"callback_deadline_exceedances\": " << misses << ",\n"
            << "  \"wall_seconds\": " << wallSeconds << ",\n"
            << "  \"wall_seconds_per_audio_second\": " << wallSeconds / audioSeconds << ",\n"
            << "  \"output_checksum\": " << checksum << ",\n"
            << "  \"peak_amplitude\": " << peak << ",\n"
            << "  \"timing_is_diagnostic_not_a_test_gate\": true\n}\n";
  return 0;
}
