# Optimized full reference renderer

This renderer preserves the original piano model while reducing repeated modal-array scans. It is a separate executable, `keyra_full_reference`, whose source retains all 88 keys, 230 strings, 17,778 string modes, 475 soundboard modes, nonlinear hammer contact, reciprocal bridge feedback, sympathetic interaction, both string polarizations, and the original stereo radiation calibration. The frozen research model remains the starting comparison for this performance step.

The original piano is still acoustically imperfect. Exact parity is this version's performance contract and makes it a control for later experiments. Future performance versions may use separately measured precision or ordering trades when their sound changes are hardly audible against this control. Realism improvements should intentionally change its sound and be judged against real recordings and matched listening comparisons. This version's pinned generator preserves the present optimization; it does not prevent a later, explicitly reviewed model version.

`grand.cpp` reproduces the passing loop-fusion candidate and adds the reviewed portable grouped-unison layout. The original direct `unisonStep()` remains available for modular probes, while production uses `groupedUnisonStep()`. The experiment's unused GNU vector member is excluded entirely. `calibration.h` is an exact copy of `Research/GrandPianoV2/src/calibration.h`. `provenance.json` records the version, intermediate and final source hashes, and the unchanged original source hash.

Three performance changes are present:

- When a hammer is inactive, free rotation and the second damping pass share one loop. Active hammer contact keeps its original integration sequence.
- String bridge impulses and calibrated stereo radiation observations share one loop. Each string's accumulation order stays unchanged, and the final string-to-output additions retain their original order after soundboard observation. Uncalibrated and disabled-bridge paths retain the original observation path.
- Unison rows with contiguous modal storage share a setup-time group, with separate loop specializations for one, two and three participating strings. Every row and participant remains present, including changes in detuned upper-partial membership. Each row retains its original multiply/add/subtract order; the grouped loop avoids repeated pointer gathering and participant-count branches.

No modes, resonances, contact states, coupling paths, or calibration coefficients are removed. Invariant-matrix caches, the rejected key-local ordering experiment, and explicit vector-extension experiments are excluded.

## Build and render

The root CMake option `KEYRA_BUILD_FULL_REFERENCE` controls this executable. Both the baseline and optimized target require C++17 and floating-point contraction disabled for the checked configuration; neither should use fast math. The original CLI throws exceptions and uses filesystem operations, so it is not yet a Rack Extension DSP implementation.

```sh
cmake --build build --target keyra_reference keyra_full_reference
build/keyra_full_reference --events score.events --output full.wav --sample-rate 192000 --duration 3
```

The complete original CLI remains available, including `--self-test`, `--no-sympathetic`, `--uncalibrated`, `--bridge`, `--hammer-loss`, `--loss`, `--damper`, model/radiation dumps and `--stem-prefix`. Output remains float32 stereo with the original 24 Hz output high-pass. No sample-rate, gain, stereo, room, or normalization change is introduced by this executable.

An event file uses one event per line:

```text
0 pedal 0 1
0.01 on 60 93
0.50 off 60 0
0.70 pedal 0 0
```

## Reproduce and verify

```sh
python3 src/full_reference/generate.py --check
python3 tools/check_full_reference_parity.py --baseline build/keyra_reference --optimized build/keyra_full_reference --scalar-state-probes
```

The generator verifies the pinned original and calibration hashes, reproduces all three transformations, checks the loop-fusion intermediate against its validated hash, and checks the final portable source hash. It performs no writes by default. `--write` explicitly regenerates the local source, calibration and provenance; it never writes to `Research`.

The parity runner compares the actual build binaries on a mixed-velocity bass/mid/treble sequence with releases, re-strikes and pedal transitions. It covers the default renderer, 96 kHz stems, disabled sympathetic coupling, zero bridge coupling and uncalibrated settings. Separate validation copies expose canonical final mechanical state at full double precision; `--scalar-state-probes` also checks a scalar/no-builtin host compilation. Every compiler configuration requires its own verification. These checks establish equivalence on the exercised inputs, not exhaustive equivalence across all compilers and event streams.

Earlier loop-fusion measurements are recorded in `Validation/reference-optimization.md`. The grouped-layout experiment in `Validation/full-layout-optimization.json` showed about 1.05x native speed over that fused model; its separate scalar/no-builtin run showed about 1.175x. Those shared-host measurements concern the experimental grouped source; the canonical adaptation also retains the direct modular API and removes unused vector-extension code. Results depend on compiler settings and have run-to-run variation. The full solver still exceeds real-time cost on that host; this change provides a sound-preserving starting point for continued performance and acoustic work and does not establish DAW or Reason readiness.

The independent original unison/observation probe is also run against both the canonical direct API and the grouped production operator. `Validation/full-reference-unison-physics.json` records the all-key topology, random-state passivity, common/opposite velocity and observation checks; these numerical checks do not measure acoustic realism.

## Later runtime integration

The CLI remains intact rather than extracting a block API in this change. A later wrapper must preserve the absolute internal frame counter because pedal/damper updates occur every 64 samples, and must preserve the 24 Hz output high-pass that currently lives outside `Piano::step`.

Unison ports cache pointers into modal storage: a live piano must not be copied, resized or rebuilt in place. `build()` appends to storage; a fresh instance should be constructed off the audio thread when structural configuration changes. Several loss, bridge and radiation coefficients are baked during construction, so changing option fields directly is not a complete runtime parameter implementation.

Grouped rows additionally copy the setup-time unison coefficients and frequency factors. After intentional setup edits to those public port fields, call `buildUnisonGroups()` off the audio thread before using the grouped production operator. The original `unisonStep()` reads the public rows directly for isolated probes. Construction builds the groups once; normal note, pedal and damping events do not invalidate them.
