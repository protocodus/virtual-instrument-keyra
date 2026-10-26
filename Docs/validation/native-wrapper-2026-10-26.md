# Keyra 0.2.0 native wrapper validation

This is development evidence for the Linux x86-64 VST3 and standalone
candidate, built with GNU C++ 14.2.0, CMake 3.31.6 and JUCE 8.0.14
(`2cdfca8feb300fb424002ba2c2751569e5bacb64`). It does not establish macOS,
Windows, AU, commercial DAW or Reason acceptance.

The JUCE front end links the canonical `KeyraDSP` target. It presents stereo
output, no audio input, nine persistent parameters and five authored timbre
presets. Programs preserve output level, concert tuning and the three pedal
settings. MIDI note, pedal and pitch events are dispatched at their sample
positions in source order, with no MIDI output. The editable keyboard shares
channel 1 performance controls with MIDI input. Its fixed queue balances only
GUI-owned key presses if overloaded and discards queued gestures on reset.
The three physical pedal buttons are momentary performance controls: soft uses
MIDI 12, sostenuto 13 and sustain 14, below the playable 21–108 piano range.
Existing continuous pedal sliders retain the same persistent parameter IDs and
defaults. External CC/keyswitch travel reaches the UI through audio-thread
snapshots; the GUI never reads mutable engine state.

## Checks performed

- `keyra_plugin_tests`: passed. Covers parameter state serialization,
  complete states with NaN/out-of-range/unparseable numeric
  corruption, sample-accurate note onset and pedal changes, exact render parity
  between 97- and 8192-sample host blocks, finite audible output, keyboard queue
  reset/overflow recovery including an already sounding note, and C++ allocation
  probes during rendering and ignored 4096-byte SysEx handling. The final pass
  additionally checks keyswitch silence, independent CC/keyswitch composition,
  published pedal levels, momentary GUI-pedal press/release delivery and
  same-sample sostenuto event ordering that determines which notes are captured.
- Complete native CTest suite: **5/5 passed**. This includes real-time core
  contracts, parameter extremes, the wrapper harness and both preserved
  reference tests. [Execution log](native-ctest-2026-10-26.txt).
- `pluginval` 1.0.4: passed, exit 0, strictness 5 with seed 20261026. Its default
  rate/block matrix covers 44.1, 48 and 96 kHz at 64, 128, 256, 512 and 1024
  samples, plus non-realtime/sub-block processing, actual VST3 loading, program
  enumeration, GUI creation while processing, editor automation and buses. The
  [complete log](pluginval-2026-10-26.txt) records the executed tests. A separate
  Steinberg validator was not configured; pluginval reports that test skipped.
- The native editor was rendered through the actual JUCE component and visually
  inspected. [Screenshot](../screenshots/keyra-editor.png): 980 × 560 pixels.
  Ivory controls and walnut surround are authored vector artwork. Parameter
  readouts use dark ink, percentages and one decimal place for tuning.
  [All pedals down](../screenshots/keyra-editor-pedals-down.png) and
  [half sustain](../screenshots/keyra-editor-half-sustain.png) were driven by
  actual processor MIDI after editor creation, followed by its GUI timer loop.
  Pixel differences occur only within the physical pedal region: all three
  move for keyswitches 12/13/14; only sustain moves for CC64=64. Persistent
  slider positions remain independent of those performance gestures.

The standalone executable was built. Physical MIDI hardware, audio-device
latency, commercial DAW transport/session behavior, accessibility and long
performance sessions still require host acceptance. These checks do not grade
piano realism or the commercial value of the model.

## Reproduction

With the platform's normal JUCE dependencies installed:

```sh
cmake -S . -B build-plugin -DCMAKE_BUILD_TYPE=Release \
  -DKEYRA_BUILD_PLUGIN=ON -DKEYRA_JUCE_PATH=/path/to/JUCE-8.0.14
cmake --build build-plugin -j3
ctest --test-dir build-plugin --output-on-failure
pluginval --strictness-level 5 --random-seed 20261026 --timeout-ms 60000 \
  --validate "$PWD/build-plugin/Keyra_artefacts/Release/VST3/Keyra.vst3"
build-plugin/keyra_editor_preview_artefacts/Release/keyra_editor_preview \
  "$PWD/Docs/screenshots/keyra-editor.png"
build-plugin/keyra_editor_preview_artefacts/Release/keyra_editor_preview \
  "$PWD/Docs/screenshots/keyra-editor-pedals-down.png" --pedals-down
build-plugin/keyra_editor_preview_artefacts/Release/keyra_editor_preview \
  "$PWD/Docs/screenshots/keyra-editor-half-sustain.png" --half-sustain
python3 Tools/build_shop.py
python3 Tools/build_shop.py --check
```

This managed Linux workspace had no privileged package installation. Development
packages were downloaded from the configured Debian snapshot and extracted into
`/tmp/keyra-deps/root`; no system package database was changed. The build used
that prefix for headers, pkg-config metadata and CMake. Xvfb on display `:99`
provided GUI support. These temporary paths are session setup, not repository
or product dependencies.

## Artifact hashes

| Artifact | SHA-256 |
| --- | --- |
| `Keyra.vst3/Contents/x86_64-linux/Keyra.so` | `3cef374a59c56c8cf2f99cf4e5fd5d5b3e1ad805497cc4e38767285e43afa26f` |
| `Standalone/Keyra` | `a86eff9dc4287e74006df43344d152729e68c7a7b691c8d7a79cacee87b8b552` |
| `Docs/screenshots/keyra-editor.png` | `72f5a67b42a81a6047aa5a0a1be11544341ad29cdfbe4880752d33631eb804fa` |
| `Docs/screenshots/keyra-editor-pedals-down.png` | `a315dcd5c0fc95065c114566ab9b762ab76996a05b25fa869fa893026fb9414a` |
| `Docs/screenshots/keyra-editor-half-sustain.png` | `6c4276168334d55071f45d8a1f2e89f166bf75c18613863fb99c31999f38aeab` |
