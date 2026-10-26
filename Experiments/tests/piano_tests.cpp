#include "keyra/Piano.h"
#include "keyra/Parameters.h"

#include <algorithm>
#include <array>
#include <atomic>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <exception>
#include <iostream>
#include <limits>
#include <new>
#include <stdexcept>
#include <string>
#include <type_traits>
#include <utility>
#include <vector>

// Catch C++ heap allocations in the real-time entry points. This deliberately
// does not claim to catch direct malloc, aligned new, or DAW adapter allocations.
namespace {
std::atomic<bool> countAllocations{false};
std::atomic<std::size_t> allocationCount{0};
// Keep GCC's allocation/deallocation family warning from looking through this
// intentional replacement delete and diagnosing free as a caller-side mismatch.
#if defined(__GNUC__) || defined(__clang__)
__attribute__((noinline))
#endif
void releaseAllocation(void* p) noexcept { std::free(p); }
}

void* operator new(std::size_t bytes) {
  if (countAllocations.load(std::memory_order_relaxed))
    allocationCount.fetch_add(1, std::memory_order_relaxed);
  if (void* p = std::malloc(bytes ? bytes : 1)) return p;
  throw std::bad_alloc();
}
void* operator new[](std::size_t bytes) { return ::operator new(bytes); }
void operator delete(void* p) noexcept { releaseAllocation(p); }
void operator delete[](void* p) noexcept { releaseAllocation(p); }
void operator delete(void* p, std::size_t) noexcept { releaseAllocation(p); }
void operator delete[](void* p, std::size_t) noexcept { releaseAllocation(p); }

namespace {
using keyra::ParamId;
constexpr double pi = 3.1415926535897932384626433832795;
static_assert(noexcept(std::declval<keyra::Piano&>().prepare(48000.)),
              "prepare must be safe to call across a no-exceptions SDK boundary");
static_assert(std::is_same_v<decltype(std::declval<keyra::Piano&>().prepare(48000.)), bool>,
              "prepare must report unsupported sample rates without throwing");

void require(bool condition, const std::string& reason) {
  if (!condition) throw std::runtime_error(reason);
}

struct Audio {
  std::vector<float> l, r;
  explicit Audio(std::size_t size) : l(size), r(size) {}
};

void process(keyra::Piano& piano, Audio& out, std::size_t block = 257) {
  for (std::size_t offset = 0; offset < out.l.size(); offset += block) {
    const auto count = static_cast<uint32_t>(std::min(block, out.l.size() - offset));
    piano.process(out.l.data() + offset, out.r.data() + offset, count);
  }
}

double energy(const Audio& audio, std::size_t start = 0) {
  double e = 0;
  for (std::size_t i = start; i < audio.l.size(); ++i)
    e += double(audio.l[i]) * audio.l[i] + double(audio.r[i]) * audio.r[i];
  return e;
}

double maxDifference(const Audio& a, const Audio& b) {
  require(a.l.size() == b.l.size(), "comparison size mismatch");
  double result = 0;
  for (std::size_t i = 0; i < a.l.size(); ++i) {
    result = std::max(result, std::abs(double(a.l[i]) - b.l[i]));
    result = std::max(result, std::abs(double(a.r[i]) - b.r[i]));
  }
  return result;
}

void finite(const Audio& audio, const char* context) {
  for (std::size_t i = 0; i < audio.l.size(); ++i) {
    if (!std::isfinite(audio.l[i]) || !std::isfinite(audio.r[i]) ||
        std::abs(audio.l[i]) > 100 || std::abs(audio.r[i]) > 100)
      throw std::runtime_error(std::string(context) + ": invalid or unbounded output");
  }
}

void dry(keyra::Piano& piano) {
  piano.setParameter(ParamId::Noise, 0);
  piano.setParameter(ParamId::Resonance, 0);
  piano.setParameter(ParamId::Distance, 0);
}

Audio note(ParamId param, double value, std::size_t samples = 24000) {
  keyra::Piano piano;
  piano.prepare(48000);
  piano.setParameter(param, value);
  piano.reset();
  piano.noteOn(60, .7);
  Audio out(samples);
  process(piano, out);
  finite(out, "parameter render");
  return out;
}

void ratesAndKeyboard() {
  for (double rate : {44100., 48000., 88200., 96000.}) {
    keyra::Piano piano;
    require(piano.prepare(rate), "supported sample rate was rejected");
    Audio out(257);
    double total = 0;
    for (int n = 21; n <= 108; ++n) {
      piano.noteOn(n, n % 2 ? .05 : 1.0);
      process(piano, out, n % 2 ? 17 : 257);
      finite(out, "keyboard/sample rate");
      total += energy(out);
      piano.allSoundOff();
    }
    require(total > 1e-6, "keyboard is silent");
    piano.noteOn(-1, .7);
    piano.noteOn(128, .7);
    piano.noteOn(60, std::numeric_limits<double>::quiet_NaN());
    piano.noteOn(60, std::numeric_limits<double>::infinity());
    piano.noteOff(-100);
    piano.sustain(std::numeric_limits<double>::quiet_NaN());
    process(piano, out, 1);
    finite(out, "malformed note/control input");
  }
}

void sampleRateValidation() {
  keyra::Piano piano, control;
  require(piano.prepare(48000) && control.prepare(48000), "48 kHz prepare failed");
  for (auto* instance : {&piano, &control}) {
    instance->setParameter(ParamId::Gain, -8.5);
    instance->setParameter(ParamId::Mic, 2);
    instance->reset();
    instance->noteOn(48, .7, 3, 7);
  }
  Audio actual(1024), expected(1024);
  process(piano, actual);
  process(control, expected);
  const double invalidRates[] = {
      -1, 0, 7999, 384001,
      std::numeric_limits<double>::quiet_NaN(),
      std::numeric_limits<double>::infinity(),
      -std::numeric_limits<double>::infinity(),
  };
  for (double rate : invalidRates) {
    const auto voices = piano.activeVoices();
    std::array<double, 10> parameters{};
    for (std::size_t i = 0; i < parameters.size(); ++i)
      parameters[i] = piano.parameter(static_cast<ParamId>(i));
    require(!piano.prepare(rate), "invalid sample rate was accepted");
    require(piano.activeVoices() == voices, "failed prepare changed active voices");
    for (std::size_t i = 0; i < parameters.size(); ++i)
      require(piano.parameter(static_cast<ParamId>(i)) == parameters[i],
              "failed prepare changed a parameter");
    process(piano, actual);
    process(control, expected);
    require(maxDifference(actual, expected) < 2e-6,
            "failed prepare changed the previously prepared audio state");
  }
  for (double rate : {8000., 384000.}) {
    require(piano.prepare(rate), "documented sample-rate boundary was rejected");
    piano.noteOn(60, .8);
    process(piano, actual);
    finite(actual, "sample-rate boundary");
  }
}

Audio partitioned(std::size_t block) {
  keyra::Piano piano;
  piano.prepare(48000);
  Audio result(24000);
  piano.noteOn(48, .75, 1, 20);
  piano.noteOn(64, .6, 2, 21);
  // Events occur at exact sample boundaries, independently of the caller's
  // blocks. The odd boundary lengths exercise internal chunk handling.
  std::size_t offset = 0;
  const auto segment = [&](std::size_t length) {
    for (std::size_t i = 0; i < length; i += block) {
      const auto frames = static_cast<uint32_t>(std::min(block, length - i));
      piano.process(result.l.data() + offset + i, result.r.data() + offset + i, frames);
    }
    offset += length;
  };
  segment(5003);
  piano.sustain(.65, 1);
  piano.noteOff(48, 1, 20);
  segment(4001);
  piano.setParameter(ParamId::Width, .2);
  piano.noteOn(72, .9, 2, 22);
  segment(3007);
  piano.sustain(0, 1);
  piano.noteOff(64, 2, 21);
  segment(result.l.size() - offset);
  return result;
}

void blockInvariance() {
  const Audio reference = partitioned(1);
  finite(reference, "single-sample blocks");
  for (auto block : {17u, 32u, 64u, 257u, 1024u}) {
    const auto candidate = partitioned(block);
    require(maxDifference(reference, candidate) < 2e-6,
            "audio or event timing depends on process block size");
  }
}

void noteIdentityAndPolyphony() {
  keyra::Piano piano;
  piano.prepare(48000);
  dry(piano);
  piano.noteOn(60, .7, 1, 10);
  piano.noteOn(60, .7, 2, 11);
  require(piano.activeVoices() == 2, "overlapping note IDs must have independent voices");
  piano.allSoundOff(1);
  require(piano.activeVoices() == 1, "channel all-sound-off killed the other channel");
  piano.allSoundOff(2);
  require(piano.activeVoices() == 0, "channel all-sound-off left a voice active");

  // A mismatched note ID/channel must leave precisely the same audio as no
  // note-off. This detects premature releases without guessing tail duration.
  keyra::Piano control;
  control.prepare(48000);
  dry(control);
  control.reset();
  piano.reset();
  piano.noteOn(60, .7, 1, 10);
  control.noteOn(60, .7, 1, 10);
  piano.noteOff(60, 2, 10);
  piano.noteOff(60, 1, 99);
  piano.noteOff(-100, 1, 10);
  piano.noteOff(60, -2, 10);
  piano.noteOff(60, 1, -2);
  Audio a(4096), b(4096);
  process(piano, a);
  process(control, b);
  require(maxDifference(a, b) < 2e-6, "note-off did not respect channel/note ID");
  piano.noteOff(60, 1, 10);
  Audio released(24000), held(24000);
  process(piano, released);
  process(control, held);
  require(energy(released, 12000) < .5 * energy(held, 12000),
          "a matching explicit note ID did not release its voice");

  piano.reset();
  for (int i = 0; i < 160; ++i) {
    piano.noteOn(21 + i % 88, .8, i % 16, i);
    require(piano.activeVoices() <= 64, "polyphony exceeded its fixed voice pool");
    piano.process(a.l.data(), a.r.data(), 17);
  }
  process(piano, a);
  finite(a, "voice stealing");
  piano.allNotesOff();
  piano.allSoundOff();
  require(piano.activeVoices() == 0, "all-sound-off did not release all voices");
}

void microphoneMonoCompatibility() {
  for (int mic = 0; mic < 6; ++mic) {
    for (int noteNumber : {36, 60, 84}) {
      keyra::Piano piano;
      piano.prepare(48000);
      dry(piano);
      piano.setParameter(ParamId::Mic, mic);
      piano.reset();
      piano.noteOn(noteNumber, .8);
      Audio out(12000);
      process(piano, out);
      double monoEnergy = 0;
      for (std::size_t i = 0; i < out.l.size(); ++i) {
        const double mono = .5 * (out.l[i] + out.r[i]);
        monoEnergy += mono * mono;
      }
      require(monoEnergy > .01 * energy(out),
              "a microphone setup cancels a dominant register when summed to mono");
    }
  }
}

double velocityEnergy(keyra::Piano& piano, int noteNumber, int velocity, Audio& audio) {
  piano.reset();
  piano.noteOn(noteNumber, velocity / 127.);
  process(piano, audio);
  double e = 0;
  for (std::size_t i = 2400; i < 36000; ++i)
    e += double(audio.l[i]) * audio.l[i] + double(audio.r[i]) * audio.r[i];
  require(std::isfinite(e) && e > 0, "velocity produced nonfinite or silent early energy");
  return e;
}

void velocityDynamics() {
  keyra::Piano piano;
  piano.prepare(48000);
  dry(piano);
  Audio audio(48000);
  for (int instrument : {0, 2}) {
    piano.setParameter(ParamId::Instrument, instrument);
    for (double dynamics : {0., .5, 1.}) {
      piano.setParameter(ParamId::Dynamics, dynamics);
      for (int noteNumber : {36, 48, 60, 72, 84}) {
        if (dynamics != .5 && noteNumber != 36 && noteNumber != 60 && noteNumber != 84) continue;
        double previous = 0, softest = 0, anchor = 0;
        for (int velocity : {1, 2, 4, 8, 16, 24, 40, 61, 93, 112, 127}) {
          const double current = velocityEnergy(piano, noteNumber, velocity, audio);
          // Allow under half a dB for interference changes in the finite window;
          // inverted soft/loud response is a playability failure, regardless of
          // how closely either fitted anchor matches an isolated recording.
          require(current >= previous * .9,
                  "inverted velocity dynamics for instrument " + std::to_string(instrument) +
                  ", MIDI " + std::to_string(noteNumber) +
                  ", velocity " + std::to_string(velocity) +
                  ", dynamics " + std::to_string(dynamics));
          if (velocity == 1) softest = current;
          if (velocity == 40) anchor = current;
          previous = current;
        }
        require(softest < .25 * anchor,
                "minimum velocity is not substantially quieter than the soft fitted anchor");
      }
    }
    piano.setParameter(ParamId::Dynamics, .5);
    for (int center : {40, 93}) {
      const double below = velocityEnergy(piano, 60, center - 1, audio);
      const double at = velocityEnergy(piano, 60, center, audio);
      const double above = velocityEnergy(piano, 60, center + 1, audio);
      require(std::abs(10 * std::log10(at / below)) < 3 &&
              std::abs(10 * std::log10(above / at)) < 3,
              "velocity response has an abrupt level step near a measured anchor");
    }
  }
}

Audio pedalTail(bool sustainPedal, bool repedal = false) {
  keyra::Piano piano;
  piano.prepare(48000);
  dry(piano);
  Audio first(4800), tail(24000);
  if (sustainPedal) piano.sustain(1);
  piano.noteOn(60, .8);
  process(piano, first);
  piano.noteOff(60);
  if (repedal) {
    Audio catchWindow(960);
    process(piano, catchWindow);
    piano.sustain(1);
  }
  process(piano, tail);
  return tail;
}

void pedals() {
  const auto held = pedalTail(true);
  const auto released = pedalTail(false);
  const auto caught = pedalTail(false, true);
  require(energy(held, 12000) > 2 * energy(released, 12000),
          "sustain did not preserve released-note decay");
  require(energy(caught, 12000) > 1.2 * energy(released, 12000),
          "repedal failed to catch a still-vibrating released note");

  keyra::Piano piano;
  piano.prepare(48000);
  Audio out(1024);
  for (int i = 0; i < 64; ++i) {
    piano.sustain((i % 9) / 8.0, i % 4);
    piano.noteOn(36 + i % 48, .7, i % 4, i);
    piano.noteOff(36 + i % 48, i % 4, i);
    process(piano, out);
    finite(out, "continuous pedal/repetition");
  }
  piano.sustain(0, 0);
  piano.sustain(0, 1);
  piano.sustain(0, 2);
  piano.sustain(0, 3);
  piano.allSoundOff();
  require(piano.activeVoices() == 0, "pedal stress left active voices after panic");
}

void parameterBoundsAndAudibility() {
  keyra::Piano piano;
  piano.prepare(48000);
  for (const auto& info : keyra::kParameters) {
    piano.setParameter(info.id, info.min - 1000);
    require(piano.parameter(info.id) >= info.min, "parameter accepted a value below its range");
    piano.setParameter(info.id, info.max + 1000);
    require(piano.parameter(info.id) <= info.max, "parameter accepted a value above its range");
    piano.setParameter(info.id, std::numeric_limits<double>::quiet_NaN());
    require(std::isfinite(piano.parameter(info.id)), "NaN contaminated parameter state");
    piano.setParameter(info.id, std::numeric_limits<double>::infinity());
    require(std::isfinite(piano.parameter(info.id)), "infinity contaminated parameter state");
  }
  piano.setParameter(static_cast<ParamId>(1000), 1);

  // These are regression tests of implemented influence, not a listening test
  // or a claim that waveform differences prove perceptual usefulness.
  for (const auto& info : keyra::kParameters) {
    const auto low = note(info.id, info.min);
    const auto high = note(info.id, info.max);
    double difference = 0;
    for (std::size_t i = 0; i < low.l.size(); ++i) {
      const double dl = double(low.l[i]) - high.l[i];
      const double dr = double(low.r[i]) - high.r[i];
      difference += dl * dl + dr * dr;
    }
    require(difference > std::max(energy(low), energy(high)) * 1e-7,
            std::string(info.name) + " has no measurable effect on the fixed C4 strike");
  }
}

void gainSmoothingAndAutomation() {
  keyra::Piano moved, fixed;
  moved.prepare(48000);
  fixed.prepare(48000);
  dry(moved);
  dry(fixed);
  moved.noteOn(60, .8);
  fixed.noteOn(60, .8);
  Audio warmA(12000), warmB(12000);
  process(moved, warmA);
  process(fixed, warmB);
  moved.setParameter(ParamId::Gain, -48);
  Audio a(32), b(32);
  process(moved, a);
  process(fixed, b);
  double maximum = 0;
  for (float x : b.l) maximum = std::max(maximum, std::abs(double(x)));
  for (float x : b.r) maximum = std::max(maximum, std::abs(double(x)));
  require(maxDifference(a, b) < maximum * .35 + 1e-7,
          "gain automation jumped abruptly at a block boundary");

  Audio out(257);
  for (int i = 0; i < 160; ++i) {
    for (const auto& info : keyra::kParameters)
      moved.setParameter(info.id, info.min + (info.max - info.min) * ((i * 13) % 101) / 100.);
    if (i % 4 == 0) moved.noteOn(36 + i % 60, .8);
    if (i % 7 == 0) moved.noteOff(36 + i % 60);
    process(moved, out, 17);
    finite(out, "parameter automation");
  }
}

void resetAndInstanceIsolation() {
  keyra::Piano piano, other;
  piano.prepare(48000);
  other.prepare(48000);
  piano.noteOn(60, .8);
  Audio sound(4096), silence(4096);
  process(piano, sound);
  process(other, silence);
  require(energy(sound) > 1e-7, "test note is silent");
  require(energy(silence) == 0, "instances share active audio state");
  piano.reset();
  process(piano, silence);
  require(energy(silence) == 0, "reset left a voice or effect tail audible");
  require(piano.activeVoices() == 0, "reset left active voice bookkeeping");
  piano.noteOn(60, .8);
  other.noteOn(60, .8);
  process(piano, sound);
  process(other, silence);
  require(maxDifference(sound, silence) < 2e-6, "reset did not restore deterministic synthesis state");
  piano.prepare(96000);
  process(piano, silence);
  require(energy(silence) == 0, "sample-rate reinitialization retained stale audio");
}

void middleAPitch() {
  keyra::Piano piano;
  piano.prepare(48000);
  dry(piano);
  piano.noteOn(69, .7);
  Audio audio(24000);
  process(piano, audio);
  // Measure the strongest sinusoid within a wide A4 neighborhood. Recurrence
  // avoids a dependency on an FFT library and uses a Hann analysis window.
  constexpr std::size_t start = 4800, count = 16384;
  double bestPower = 0, bestFrequency = 0;
  for (double hz = 420; hz <= 460; hz += .25) {
    const double angle = 2 * pi * hz / 48000;
    const double cs = std::cos(angle), sn = std::sin(angle);
    double c = 1, s = 0, re = 0, im = 0;
    for (std::size_t i = 0; i < count; ++i) {
      const double value = .5 * (audio.l[start + i] + audio.r[start + i]) *
                           (.5 - .5 * std::cos(2 * pi * i / (count - 1)));
      re += value * c;
      im += value * s;
      const double nextC = c * cs - s * sn;
      s = s * cs + c * sn;
      c = nextC;
    }
    const double power = re * re + im * im;
    if (power > bestPower) { bestPower = power; bestFrequency = hz; }
  }
  require(bestPower > 1e-8, "A4 fundamental was absent");
  require(std::abs(1200 * std::log2(bestFrequency / 440)) < 30,
          "A4 tuning or sample-rate conversion is incorrect");
}

void realtimeAllocation() {
  keyra::Piano piano;
  piano.prepare(48000);
  std::array<float, 257> l{}, r{};
  allocationCount.store(0, std::memory_order_relaxed);
  countAllocations.store(true, std::memory_order_relaxed);
  for (int i = 0; i < 96; ++i) {
    piano.setParameter(ParamId::Instrument, i % 4);
    piano.setParameter(ParamId::Material, i % 3);
    piano.setParameter(ParamId::Mic, i % 6);
    piano.setParameter(ParamId::Tone, (i % 11) / 10.);
    piano.noteOn(21 + i % 88, .8, i % 16, i);
    piano.sustain((i % 7) / 6., i % 16);
    piano.process(l.data(), r.data(), 257);
    piano.noteOff(21 + i % 88, i % 16, i);
  }
  piano.allNotesOff();
  piano.allSoundOff();
  piano.reset();
  countAllocations.store(false, std::memory_order_relaxed);
  require(allocationCount.load(std::memory_order_relaxed) == 0,
          "real-time control/event/process path performed a C++ heap allocation");
}
}

int main() {
  struct Test { const char* name; void (*run)(); };
  const Test tests[] = {
      {"sample rates, keyboard and malformed inputs", ratesAndKeyboard},
      {"sample-rate rejection preserves the running state", sampleRateValidation},
      {"block-size and event-timing invariance", blockInvariance},
      {"note identity, channel isolation and bounded polyphony", noteIdentityAndPolyphony},
      {"sustain, repedal and repeated half-pedal changes", pedals},
      {"parameter bounds and implemented sonic influence", parameterBoundsAndAudibility},
      {"microphone mono compatibility across registers", microphoneMonoCompatibility},
      {"velocity dynamics and fitted-anchor continuity", velocityDynamics},
      {"gain smoothing and automation stability", gainSmoothingAndAutomation},
      {"reset, sample-rate changes and instance isolation", resetAndInstanceIsolation},
      {"A4 fundamental tuning", middleAPitch},
      {"real-time C++ allocation instrumentation", realtimeAllocation},
  };
  unsigned failures = 0;
  for (const auto& test : tests) {
    try {
      test.run();
      std::cout << "PASS " << test.name << '\n';
    } catch (const std::exception& error) {
      countAllocations.store(false, std::memory_order_relaxed);
      ++failures;
      std::cerr << "FAIL " << test.name << ": " << error.what() << '\n';
    }
  }
  std::cout << (std::size(tests) - failures) << '/' << std::size(tests) << " tests passed\n";
  return failures ? 1 : 0;
}
