# Offline full-instrument renderer

`keyra_full_render` renders the complete `FullInstrument` API, including its
persistent strings, seeded strike variation, finite hammer/key recovery and
quiet connected key/pedal sources. The original control calibration is used.
`keyra_preview_render` renders the additional ten-control development preview.
`keyra_render` retains the existing `Source/DSP/KeyraEngine` renderer from main.

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --target keyra_full_render -j2
build/keyra_full_render --output /tmp/keyra-full.wav --seconds 4.5 \
  --note 60 --velocity 80 --seed 123456 --param gain=-6 \
  --report /tmp/keyra-full.json
```

The output is stereo float32 WAV at the requested integer sample rate within
44.1–96 kHz. There is no normalization, limiter, room effect or sample playback.
Output gain is in dB; width is 0–2 with a default of 1. Dynamics, humanization and
mechanical level are 0–1. Invalid controls/rates/scores are rejected. Rendering
is offline; its wall/process timing includes dispatch and audio collection and
does not qualify callbacks or Reason performance.

## Event scores and repetitions

`--events` accepts the original text score format, with one event per line:

```text
0.00 pedal 0 1
0.00 on 60 90
0.10 off 60 0
0.10 on 60 90
0.20 off 60 0
0.20 on 60 90
0.28 on 60 0
```

The fields are seconds, event kind, MIDI note and value. Notes use velocity
0–127; note-on velocity zero releases. Pedal uses normalized position 0–1 and
ignores the note field. Comments start with `#`. Events are stably ordered by
their rounded sample frame; events sharing a frame retain file order. The
renderer splits blocks at events and retains the API's absolute frame clock.
Events beyond the output duration are counted without being applied.

The instrument represents one physical keyboard and global pedal. Note-ons can
queue until the existing hammer and finite key-lift proxy are ready; they are
accepted requests rather than promises of immediate audible contact. One
pending slot per key coalesces requests. The report includes admitted launches,
deferred/coalesced/cancelled/expired requests and faults. Return geometry/timing
and variation ranges are authored approximations; see `STRIKE_REPETITION.md`.

## Component comparisons

The following switches support controlled experiments:

- `--param humanization=0`: disable excitation variation while retaining
  existing string/body state and recovery.
- `--param mechanicalLevel=0`: disable mechanical source excitation and loading.
- `--mechanism-body 0`: disable source/body coupling while retaining direct
  source observation.
- `--mechanism-direct 0`: mute direct source observation while retaining its
  effect on the body/string network.
- `--repetition 0`: use the safe comparison bypass. It rejects requests during
  active hammer motion; it does not overwrite an active hammer.

These are offline investigation switches, not additional product controls.
Source-isolation stems and stronger diagnostic levels remain available through
the dedicated mechanism/strike probes. Keep gains and processing identical
when comparing versions. The JSON records the actual controls and selected
pressure/contact build paths. A seeded performance and reset are reproducible.

`Validation/full-renderer.json` retains the initial smoke check and exact source
snapshot: touching notes admit all three strikes; block sizes 17 and 64 produce
identical WAV bytes; disabling variation or mechanisms changes the signal;
velocity zero releases silently; invalid arguments are rejected. This check
does not establish acoustic realism or actual Reason validation.

`Validation/full-renderer-current.json` separately pins the earlier fast-contact
build, with pressure SIMD disabled. Its touching-note renders at block
sizes 17 and 64 are identical and retain the initial control's WAV bytes. The
initial source/binary snapshot remains preserved for the
[matched musical comparison](../Audio/full-performance/README.md).

`Validation/full-renderer-profiles.json` pins the later default mechanism-cache
build for both `OriginalControl` and `FrozenConfidenceGrand`. Each admits all
three touching notes and produces identical output at block sizes 17 and 64.
Its JSON records the selected profile, numeric calibration-header hash and
actual contact/cache/pressure flags.

## Recording-calibration candidate

Use a separate build directory to review the frozen candidate with the full
repetition and mechanism network:

```sh
cmake -S . -B build-confidence -DCMAKE_BUILD_TYPE=Release \
  -DKEYRA_FULL_MODEL_PROFILE=FrozenConfidenceGrand
cmake --build build-confidence --target keyra_full_render -j2
build-confidence/keyra_full_render --output /tmp/keyra-confidence.wav \
  --note 60 --velocity 80 --seed 123456 --param gain=-6
```

`OriginalControl` remains the default. Profile selection introduces no additional
playing controls or runtime data loading. See [FULL_MODEL_PROFILES.md](FULL_MODEL_PROFILES.md)
for numeric provenance and known recording regressions. These builds remain
offline development tools; this is not a genuine Rack Extension package.
