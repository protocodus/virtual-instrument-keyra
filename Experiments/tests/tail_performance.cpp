#include "keyra/Piano.h"
#include "keyra/Parameters.h"

#include <algorithm>
#include <array>
#include <chrono>
#include <cmath>
#include <iomanip>
#include <iostream>

#if defined(__SSE__) || defined(_M_X64) || (defined(_M_IX86_FP) && _M_IX86_FP >= 1)
#include <xmmintrin.h>
#define KEYRA_CAN_CONTROL_DENORMAL_FLAGS 1
#else
#define KEYRA_CAN_CONTROL_DENORMAL_FLAGS 0
#endif

namespace {
// Exercise modal decay without relying on the DAW to flush denormals. Restore
// the calling thread's complete original floating-point flags on every exit.
class DenormalFlags {
public:
  DenormalFlags() noexcept {
#if KEYRA_CAN_CONTROL_DENORMAL_FLAGS
    original_ = _mm_getcsr();
    _mm_setcsr(original_ & ~0x8040u); // FTZ (bit15), DAZ (bit6).
    controlled_ = (_mm_getcsr() & 0x8040u) == 0;
#endif
  }
  ~DenormalFlags() {
#if KEYRA_CAN_CONTROL_DENORMAL_FLAGS
    _mm_setcsr(original_);
#endif
  }
  DenormalFlags(const DenormalFlags&) = delete;
  DenormalFlags& operator=(const DenormalFlags&) = delete;
  bool controlled() const noexcept { return controlled_; }
private:
#if KEYRA_CAN_CONTROL_DENORMAL_FLAGS
  unsigned original_ = 0;
#endif
  bool controlled_ = false;
};

struct Second {
  double wallSeconds = 0;
  double callbackMeanMs = 0, callbackP95Ms = 0, callbackMaxMs = 0;
  double energy = 0, peak = 0;
  unsigned activeVoices = 0;
  bool finite = true;
};
} // namespace

// A diagnostic, not a timing test gate. Scheduling and CPU performance vary;
// retaining per-second timings exposes growth hidden by a short mean benchmark.
int main() {
  constexpr unsigned sampleRate = 48000, block = 64, audioSeconds = 10;
  constexpr unsigned callbacksPerSecond = sampleRate / block;
  constexpr double deadlineMs = 1000. * block / sampleRate;
  using Clock = std::chrono::steady_clock;

  DenormalFlags denormalFlags;
  keyra::Piano piano;
  piano.prepare(sampleRate);
  piano.setParameter(keyra::ParamId::Noise, 0);
  piano.setParameter(keyra::ParamId::Resonance, 0);
  piano.setParameter(keyra::ParamId::Distance, 0);
  piano.reset();
  for (int note = 60; note < 68; ++note) piano.noteOn(note, .8);

  std::array<float, block> left{}, right{};
  std::array<double, callbacksPerSecond> callbackTimes{};
  std::array<Second, audioSeconds> results{};
  bool allFinite = true;
  double totalWallSeconds = 0;
  for (unsigned second = 0; second < audioSeconds; ++second) {
    auto& result = results[second];
    const auto wallStart = Clock::now();
    for (unsigned callback = 0; callback < callbacksPerSecond; ++callback) {
      const auto start = Clock::now();
      piano.process(left.data(), right.data(), block);
      const auto end = Clock::now();
      callbackTimes[callback] = std::chrono::duration<double, std::milli>(end - start).count();
      for (unsigned frame = 0; frame < block; ++frame) {
        const double l = left[frame], r = right[frame];
        if (!std::isfinite(l) || !std::isfinite(r)) {
          result.finite = false;
          continue;
        }
        result.energy += l * l + r * r;
        result.peak = std::max({result.peak, std::abs(l), std::abs(r)});
      }
    }
    result.wallSeconds = std::chrono::duration<double>(Clock::now() - wallStart).count();
    totalWallSeconds += result.wallSeconds;
    result.activeVoices = static_cast<unsigned>(piano.activeVoices());
    result.finite = result.finite && std::isfinite(result.energy);
    allFinite = allFinite && result.finite;
    for (double elapsed : callbackTimes)
      result.callbackMeanMs += elapsed / callbackTimes.size();
    std::sort(callbackTimes.begin(), callbackTimes.end());
    constexpr auto p95Index = static_cast<std::size_t>((95 * callbacksPerSecond + 99) / 100 - 1);
    result.callbackP95Ms = callbackTimes[p95Index];
    result.callbackMaxMs = callbackTimes.back();
  }

  std::cout << std::setprecision(10)
            << "{\n  \"schema_version\": 1,\n"
            << "  \"scenario\": \"Eight held notes MIDI60-67, ten seconds of decay, no new strikes\",\n"
            << "  \"sample_rate\": " << sampleRate << ",\n"
            << "  \"frames_per_callback\": " << block << ",\n"
            << "  \"callback_deadline_ms\": " << deadlineMs << ",\n"
            << "  \"callbacks_per_audio_second\": " << callbacksPerSecond << ",\n"
            << "  \"measured_audio_seconds\": " << audioSeconds << ",\n"
            << "  \"ftz_daz_controlled\": " << (denormalFlags.controlled() ? "true" : "false") << ",\n"
            << "  \"denormal_mode\": \""
            << (denormalFlags.controlled() ? "FTZ and DAZ disabled for this thread; original flags restored on exit"
                                           : "Floating-point denormal flags not controlled on this architecture") << "\",\n"
            << "  \"all_audio_and_energy_finite\": " << (allFinite ? "true" : "false") << ",\n"
            << "  \"timing_is_diagnostic_not_a_test_gate\": true,\n"
            << "  \"wall_seconds\": " << totalWallSeconds << ",\n"
            << "  \"wall_seconds_per_audio_second\": " << totalWallSeconds / audioSeconds << ",\n"
            << "  \"per_audio_second\": [\n";
  for (unsigned second = 0; second < audioSeconds; ++second) {
    const auto& result = results[second];
    std::cout << "    {\"audio_second_start\": " << second
              << ", \"wall_seconds\": " << result.wallSeconds
              << ", \"callback_mean_ms\": " << result.callbackMeanMs
              << ", \"callback_p95_ms\": " << result.callbackP95Ms
              << ", \"callback_max_ms\": " << result.callbackMaxMs
              << ", \"callback_mean_deadline_fraction\": " << result.callbackMeanMs / deadlineMs
              << ", \"callback_mean_cpu_percent\": " << 100 * result.callbackMeanMs / deadlineMs
              << ", \"active_voices\": " << result.activeVoices
              << ", \"energy\": " << result.energy
              << ", \"peak_amplitude\": " << result.peak
              << ", \"audio_and_energy_finite\": " << (result.finite ? "true" : "false")
              << '}' << (second + 1 < audioSeconds ? "," : "") << '\n';
  }
  std::cout << "  ]\n}\n";
  return allFinite ? 0 : 1;
}
