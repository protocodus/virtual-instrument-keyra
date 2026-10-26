# Merge-review native validation — 2026-10-26

The Linux x86-64 VST3 and standalone candidate were rebuilt after the two
review fixes: channel-1 CC120/123 now cancels stale GUI ownership bookkeeping,
and the shared sympathetic bank follows concert tuning without clearing its
existing resonator state. The editor and its artwork are unchanged.

The build began from Git revision
`1800837710ec5a3154f9180144d9f79b0746de0b` plus the pending review fixes.
Exact source hashes below identify the tested implementation independently of
the subsequent review commit. Toolchain: GNU C++ 14.2.0, CMake 3.31.6, JUCE
8.0.14 (`2cdfca8feb300fb424002ba2c2751569e5bacb64`).

## Results

All `build-plugin` targets rebuilt successfully. The complete native CTest
suite passed **5/5**, exit 0, in 9.30 seconds:

| Test | Result |
| --- | --- |
| `realtime_engine_contract` | Passed |
| `realtime_parameter_extremes` | Passed |
| `plugin_state_and_midi` | Passed |
| `reference_self_test` | Passed |
| `reference_passivity_and_radiation` | Passed |

The wrapper harness includes 16 ownership regressions: CC120 and CC123,
piano note 60 and pedal keyswitches 12/13/14, with releases on channel 1 and
channel 2. After a channel-1 release, a late GUI mouse-up leaves a fresh
host-owned press intact; a channel-2 release preserves the GUI channel-1
ledger. The piano renders match their corresponding control renders exactly,
and the pedal snapshots reach the expected held/released states. The new
regression failed against the preceding wrapper before its fix.

`pluginval` **1.0.4, strictness 5**, passed with exit 0 and seed 20261026.
The actual rebuilt VST3 passed its default 44.1/48/96 kHz ×
64/128/256/512/1024-sample matrix, sub-block/non-realtime processing, programs,
GUI creation during processing, editor automation and bus tests. GUI tests ran
under Xvfb on display `:99`. A separate Steinberg validator was not configured;
pluginval reports that optional test skipped.

The complete run logs accompany the refreshed local package as
`Docs/validation/merge-review-native-ctest-2026-10-26.txt` and
`Docs/validation/merge-review-pluginval-2026-10-26.txt`. Earlier measurement,
rendering and validation reports remain frozen. This run does not establish
macOS, Windows, commercial DAW or Reason acceptance.

## Tested hashes

| File | SHA-256 |
| --- | --- |
| `Source/PluginProcessor.cpp` | `f5416f89cd48b2b467ec68c4fb633ad67352e5cd2efd44d9190627c898d4ae81` |
| `Source/DSP/KeyraEngine.cpp` | `3d6d2dcad4f024376814ca3011080345e96cb5b7def65787fa6c51d3569215ec` |
| `Keyra.vst3/Contents/x86_64-linux/Keyra.so` | `870872a718d60c201cfecf29dd587e8ad398994fe549e8206a6fb959c94e76bd` |
| `Standalone/Keyra` | `2c6470fbd7403161662f41776868a6f4b359ca899ef88d504f5fe3475f616473` |

The refreshed ignored bundle is
`deliverables/Keyra-0.2.0-linux-x86_64/`. Its current manifest records the new
source/binary hashes, while retaining the original candidate's build manifest
under `build-history/initial-build-manifest.json`. `SHA256SUMS` covers both the
current payload and that historical provenance.
