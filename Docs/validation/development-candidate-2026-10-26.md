# Keyra 0.2.0 development candidate

This candidate adds a playable reduced modal piano, native DAW wrapper, common
pedals, below-piano keyswitches and a thin Reason adapter. It preserves the
offline research tree unchanged. It is not a commercial release.

## Completed evidence

- The SDK-free release build passed **4/4 CTest tests**: live-engine contracts,
  162 parameter endpoint/midpoint cases with activation witnesses across three
  sample rates, and both preserved reference checks.
- The live-engine ASan/UBSan build passed **2/2 tests**, including the same
  parameter cases. Live event/render/reset allocation probes report zero.
- Independent review reproduced and verified fixes for channel-local muting,
  sostenuto/controller reset, ordinary forte-chord headroom, GUI note ownership
  and malformed state. The added MIDI 12/13/14 switches have independent source
  composition, channel ownership, momentary release, panic/reset and edge tests.
- The [native wrapper receipt](native-wrapper-2026-10-26.md) records actual Linux
  VST3/standalone builds, processor state/MIDI tests, rendered editor inspection
  and strictness-5 pluginval results. Pluginval loads the actual VST3; its
  default matrix includes three rates and five block sizes.
  Its full native configuration passed **5/5 CTest tests**.
- The [recording benchmark](recording-benchmark-2026-10-26.md) includes all ten
  fitting cases, twelve development-validation cases and two edges, with every
  regression. The [fresh eight-note report](recording-benchmark-fresh-2026-10-26.md)
  was locked before its recordings were downloaded. Neither uses another piano
  or recording session.
- [Final recording parity](final-recording-parity-2026-10-26.json) replays all
  **96** live variant renders from both recording reports with the final
  keyswitch implementation. Every WAV is byte-identical to its frozen score
  input. Adding pedal control and display did not change those piano tones.
- The Rack adapter's native and sanitizer suites each passed **2/2**, with
  executed Lua/art/patch checks, exact event-order comparisons against the
  canonical engine and independent tuning-frequency measurements. These are
  authored host-mock checks, not proprietary SDK or Reason-host results.

## Material gaps

The [native CPU receipt](../benchmarks/realtime-cpu-2026-10-26.json) shows that
the 128-strike workload still exceeds real time on this machine. Ordinary
musical examples run faster, but average render time does not establish every
audio deadline or whole-rack headroom. A scratch mode-retirement optimization
was not adopted: its dense workload remained over budget and one sparse
diagnostic became slower.

The [production plan](../plans/production-readiness.md) retains the remaining
gates: independent piano/pedal captures and listening, sustained-polyphony
performance, representative commercial DAW sessions, macOS/Windows artifacts,
licensed Jukebox SDK compilation, U45/cloud build and actual Reason acceptance.
The present evidence does not establish pedal calibration or justify a retail
price above USD 199. No public product release or website availability claim
has been made.

The full portfolio-standard audit is not green. This initial research repository
still needs the portfolio's CI/release, CLAP, test-tier and shared-tool adoption,
and its preserved `Research/` layout differs from that checker's expected root
layout. Some build-wiring checks also inspect only root CMake text, whereas the
working JUCE configuration lives in `cmake/Plugin.cmake`. These are additional
release-engineering gaps, not passing checks. The Rack repository's 64 general
and 61 portfolio unit tests passed; its whole-repository style audit also has
pre-existing failures in unrelated devices.
