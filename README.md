# Keyra

Keyra is a sample-free piano instrument in development, targeting a **Reason Rack Extension**. Linux provides the efficient DSP/recording test environment; Reason itself and its licensed Jukebox toolchain require separate host validation. Version 0.2 adds a playable modal engine, optional VST3/CLAP development harnesses, separate grand/upright recording calibrations, four instrument voicings, three material voicings and six microphone arrangements. Production readiness and a price above US$199 remain goals, not established claims.

**Sound-quality baseline:** the preserved full nonlinear physical renderer that produced the original demos. The user reports that those demos sounded better than the newer reduced live model, especially in body, stereo and attack. The reduced renderer is a CPU/parameter research preview, not a proven quality replacement. [QUALITY_BASELINE.md](docs/QUALITY_BASELINE.md) explains the distinction and links a same-passage, RMS-matched comparison with identical room processing. Performance work must preserve that original quality rather than justify removing physical mechanisms with note scores alone.

The active direction is **optimize the original physical model and improve its realism against recordings**. The original also has audible limitations; it is a starting point. The user accepts precision/quality tradeoffs when hardly audible and prioritizes a complete, connected instrument over extreme precision in one part. Keep an exact comparison version, then evaluate approximations with explicit numerical, recording and listening evidence. Attack, body, stereo and state-linked action/release behavior come first.

`keyra_full_reference` now builds a [working full-model copy](src/full_reference/README.md) with loop fusion and a portable unison layout. Audio, stems and final mechanical state match the original in the [tested configurations](Validation/full-reference-parity.json). Initial CPU savings leave the full solver several times slower than realtime. [Feasibility and remaining performance gap](docs/REALTIME_FEASIBILITY.md) records the measured limits and next engineering steps.

The current priority is the **full physical grand against recordings**. The [locked full-range corpus](References/GrandFullRange/README.md) adds A0 and C1–C8, with 34 training recordings at 17 pitches and separate evaluation cases. The [full-model calibration work](docs/FULL_CALIBRATION.md) retains nonlinear contact and reciprocal string/body coupling; its candidate remains separate from the plugin preview. C8 has an unresolved strong recorded component whose physical identity is uncertain.

A subsequent [confidence-prior decay candidate](docs/FULL_CONFIDENCE_LOSS.md) improves mean envelope and early attack-band agreement and reverses the earlier A3 envelope regression. [Five matched recording comparisons](Audio/full-confidence-loss/README.md) retain the A0 attack, C2 envelope and C8 regressions. These previously observed historical cases are not fresh validation, and the canonical calibration remains unchanged.

The [A0 attack diagnosis](docs/FULL_ATTACK_TIMING.md) separates the large relative-rise metric change from actual hammer timing: radiation weighting changes which bass-cycle peak crosses the threshold. Early attack-band agreement improves, while excessive initial pressure remains. The next fit needs coherent pressure guards before 50 ms alongside the existing spectrum/envelope criteria.

For frozen listening exports and numerical replays, follow the [replay-environment addendum](docs/REPLAY_ENVIRONMENT.md), including `OPENBLAS_NUM_THREADS=1` before Python starts. It records a later-discovered procedural-room fingerprint requirement while preserving the original evidence and its scope.

The earlier 13-pitch **reduced preview** improved harmonic error from 5.83 to 2.97 dB and envelope error from 4.26 to 2.46 dB on seven recordings opened after that candidate froze. Its [validation report](docs/VALIDATION.md) preserves individual regressions. [A3](Audio/default-A3v8-real-before-after.mp3) and [D♯4](Audio/default-Dsharp4v8-real-before-after.mp3) play real → previous preview → current preview at 0 / 4.5 / 9 seconds. These historical preview results do not establish full-model or perceptual parity.

A separate [connected physical research path](docs/MODULES.md) provides independently testable finger/key/keybed/action, nonlinear hammer contact, persistent strings, sympathetic coupling, wood, air, lid and player-load components. It has not replaced the default sound: physical passivity, material tables and more modules do not by themselves prove recording realism. Material/preset expansion is secondary to default-model fidelity.

The [piano-parts coverage map](docs/PIANO_PARTS_COVERAGE.md) relates the supplied grand/upright schematics to the actual implementations. It distinguishes effective action textures from mechanical parts, identifies missing body-reaction paths and separates upright voicing from an upright action model.

The original full model also has a [modular key/pedal body-coupling prototype](docs/MECHANISM_NETWORK.md). Tests show mechanism impacts reaching unstruck strings and body motion reacting back on the source; intact stems and coupling/source ablations expose both effects. A separate [precision candidate](docs/PRECISION_FINDINGS.md) retains every original mode/operator and is about 1.67× faster on repeated short 48 kHz comparisons, with measured numerical loss. Both remain research candidates for listening and further validation.

A separate [full physical block API](docs/FULL_BACKEND.md) now combines that precision approach with persistent strings, bounded seeded strike variation, hammer recovery and quiet body-coupled key/pedal texture. Its [repetition controller](docs/STRIKE_REPETITION.md) defers unsafe strikes instead of overwriting an active hammer. [Shared-gain repetition clips](Audio/strike-repetition/README.md) expose the behavior. This API uses the original control calibration; the development plugin wrappers still use the reduced preview, and full-model realtime performance remains unresolved.

The [full offline renderer](docs/FULL_RENDERER.md) exercises that API with sample-timestamped scores and component switches. A [matched stereo passage](Audio/full-performance/README.md) compares the original full control and connected action version, dry and with identical room processing. A separate [air/lid/player research integration](docs/FULL_ACOUSTIC_NETWORK.md) connects the existing passive cavity to the full string/body network and exposes reciprocal transfer and source/coupling ablations; its uncalibrated parameters remain outside the default instrument.

A bounded [C2/C4 waveguide experiment](docs/COUPLED_WAVEGUIDE.md) demonstrates persistent nonlinear strikes and reciprocal transfer through the full 475-mode board with a numerical energy ledger. It is a cheaper-representation study; missing polarization, unison losses, dampers and calibrated radiation prevent replacing the full engine.

## Existing native frontend

The `Source/DSP/KeyraEngine` engine, JUCE editor, pedals and keyswitches already on `main` are retained with their existing fixes. The production-layout Reason source adapter in `reason-rack-extensions/Examples/Keyra` still consumes that engine. Its [user guide](Docs/guide/user-guide.md), [native build evidence](Docs/validation/native-wrapper-2026-10-26.md) and [editor](Docs/screenshots/keyra-editor.png) remain available. It is a reduced live model, separate from the full physical engine used in the latest comparison.

`keyra_render` retains that existing frontend's renderer. `keyra_preview_render` renders the additional ten-control development preview described below; `keyra_full_render` renders the complete physical API. The JUCE VST3/standalone build retains `-DKEYRA_BUILD_PLUGIN=ON`, optionally with `-DKEYRA_JUCE_PATH=/path/to/JUCE`. The separate CLAP harness uses `-DKEYRA_BUILD_CLAP=ON`.

## Playable engine and plugins

The live engine reduces measured partial balance, stiff-string tuning, two-stage decay and attack envelopes into up to 64 modes per voice, with 64 playing voices and bounded stealing fades. It uses numeric calibration from acoustic recordings, with no recorded waveform, sample bank or impulse response loaded at runtime. This is a distinct modal surrogate; it does not run the preserved nonlinear hammer/contact solver below.

| Choice | Available models | Evidence |
|---|---|---|
| Instrument | Concert Grand, Studio Grand, Upright, Felt Upright | Two separately calibrated recorded instruments; studio/felt are authored variants |
| Material voicing | Spruce, Cedar, Maple | Authored changes to modal dispersion, loss, spectral color and board resonances; no isolated species measurement |
| Microphones | Close AB, XY, ORTF, Mid Side, Mono, Room AB | Procedural stereo pickup approximations; no measured capsule, position or room responses |

Ten host parameters cover those three choices plus **tone, dynamics, resonance, mechanical noise, room/distance, stereo width and output**. Each has a regression check for a measurable signal change. Instrument, string material character and dynamics affect subsequent strikes; material board color, tone, microphone routing, resonance, noise, distance, width and gain also respond during playback with smoothing. Measurable change does not replace listening evaluation.

The optional VST3/CLAP adapters support sample-accurate notes/automation, per-channel sustain with partial damping, note identity, bounded polyphony and versioned project state. VST3 uses the official pinned MIT SDK; CLAP headers are vendored under MIT. Use the DAW's generic parameter editor. No custom graphical editor is included. The separate Reason wrapper is staged in `reason-rack-extensions/Prototypes/Keyra`, consuming the canonical engine directly rather than copying it. Its opt-in `KEYRA_BUILD_EXPERIMENTAL_FULL_MODEL=ON` mock-host build exercises `FullInstrument` with five controls: dynamics, humanization, mechanical level, width and gain. The full variant stays disabled by default while its CPU budget is unresolved. Both variants are source-only until a reviewed canonical pin, SDK compilation, panels and actual Reason/Recon creation are validated; promotion to the production `Examples/` inventory comes with that pin.

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
ctest --test-dir build --output-on-failure
build/keyra_full_render --help
```

The default build is offline and creates the core, renderer, reference and CLAP harness. Add `-DKEYRA_BUILD_VST3=ON` to download the pinned SDK, or also supply `-DKEYRA_VST3_SDK_DIR=/path/to/vst3sdk` with its submodules for an offline build. On Windows use an x64 Visual Studio toolchain, `cmake --build build --config Release`, and `ctest --test-dir build -C Release --output-on-failure`. The optional [Windows workflow](.github/workflows/windows-vst3.yml) is manually invoked; it must run successfully before any Windows binary can be called validated. Linux builds have been exercised locally. See [VST3](vst3/README.md) and [CLAP](plugin/README.md) for harness details. Their binaries are not Rack Extensions.

The [live validation report](docs/VALIDATION.md) separates improvements, regressions and release blockers. [Release goals](docs/ROADMAP.md) record the remaining Reason work. [Listening examples](Audio/manifest.json) include four performances and held-out real→model comparisons; recording attribution is retained in the manifest.

## Preserved mechanical reference

The offline reference models nonlinear hammer contact, dispersive two-polarization strings, detuned unisons, sympathetic coupling and a reduced soundboard. It has 88 keys, 230 strings, 17,778 string modes and 475 board modes. Numeric calibration comes from acoustic-piano measurements; no recorded waveform or impulse response is loaded by the synthesizer.

The reference renderer is expensive: the supplied 192 kHz musical renders took about 17–19 wall seconds per audio second on the development machine. This is an offline baseline; the optimized block API still needs further performance work and host integration. The benchmark below applies to this preserved renderer.

## Reference sound and evidence

[Research/GrandPianoV2](Research/GrandPianoV2/README.md) preserves the exact v2 solver and calibration, original event/MIDI scores, measurement scripts, frozen reports and numerical validation. The source import is documented in [import-provenance.json](Research/GrandPianoV2/import-provenance.json).

| Original musical example | MP3 preview |
|---|---|
| Window at Dusk | [Nocturne](Research/GrandPianoV2/renders/01_nocturne-room.mp3) |
| Two Voices in Morning Light | [Prelude](Research/GrandPianoV2/renders/02_prelude-room.mp3) |
| Sunday on the River | [Jazz waltz](Research/GrandPianoV2/renders/03_jazz_waltz-room.mp3) |
| Copper and Thunder | [Etude](Research/GrandPianoV2/renders/04_etude-room.mp3) |

The isolated-note clips play **real acoustic piano → original POC → calibrated v2**. Try [C4](Research/GrandPianoV2/listening/C4v8-real-v1-v2.mp3), [F♯3](Research/GrandPianoV2/listening/Fsharp3v8-real-v1-v2.mp3) or the [C7 extrapolation check](Research/GrandPianoV2/listening/C7v8-real-v1-v2.mp3). These are level-matched, labeled comparisons, not blind listening tests.

The reference recordings are **Salamander Grand Piano V3 by Alexander Holm**, an acoustic Yamaha C5 set under CC BY 3.0. Ten notes/velocity cases were used for fitting, twelve in-range cases were excluded from fitting and two extreme notes were tested separately. Across the twelve in-range held-out cases:

| Mean error — lower is better | Original POC | Calibrated reference |
|---|---:|---:|
| Harmonic levels | 11.03 dB | 4.96 dB |
| Broad spectral bands | 15.62 dB | 12.09 dB |
| Partial decay rate | 3.88 dB/s | 2.83 dB/s |
| Attack rise time | 8.29 ms | 19.17 ms |

Attack timing regressed. All four held-out-pitch envelope errors and several upper-register/edge cases also regressed. The [complete benchmark](Research/GrandPianoV2/BENCHMARK.md) includes every case and limitation; error reductions are not percentages of perceptual realism or a claim of Pianoteq parity.

## Build the preserved reference

The reference engine needs a C++17 compiler and CMake. It has no SDK dependency.

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
ctest --test-dir build --output-on-failure
build/keyra_reference --help
```

To regenerate the musical WAVs and MP3s:

```sh
cd Research/GrandPianoV2
python3 -m pip install -r requirements.txt
python3 tools/render.py --jobs 4
python3 tools/validate.py --audio
```

`ffmpeg` is required for MP3 encoding and reference decoding. Matplotlib is optional for regenerating figures. The [reference README](Research/GrandPianoV2/README.md) documents MIDI import, benchmark reproduction and generated assets.

## Source and licensing boundaries

- [Research/GrandPianoV2/src](Research/GrandPianoV2/src/): preserved offline solver and generated numeric calibration.
- [src](src): live modal engine and generated numeric grand/upright calibration; [include/keyra](include/keyra) exposes the shared host API and stable parameter IDs.
- [References/Upright](References/Upright/README.md): pinned VCSL CC0 Yamaha upright recordings, velocity-proxy caveats, separate training/held-out split and reproducible fetch/extraction.
- [tools](tools): live calibration, render, validation, listening exports and local preview packaging.
- The proprietary Jukebox SDK and a Rack Extension wrapper are not included in this baseline.
- Reference-audio attribution and modification details are in [ATTRIBUTION.md](Research/GrandPianoV2/reference/ATTRIBUTION.md), with the [full CC BY 3.0 license](Research/GrandPianoV2/reference/upstream/LICENSE-CC-BY-3.0.txt).

This checkout includes small MP3 examples and numerical evidence. Original reference FLACs, decoded WAVs, full-resolution demo WAVs and compiled binaries are intentionally generated or fetched instead of tracked. The source code has no additional open-source license grant in this initial repository; the audio's CC BY license does not license the implementation.
