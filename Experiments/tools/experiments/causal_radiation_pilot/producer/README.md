# Frozen producer and portable replay

This is a review package for one **failed research pilot**. Four of six TRAIN
cases passed; both C6 cases failed the early spectral-band guards. The current
piano implementation and default are unaffected. The observer is a virtual
radiation correction, not another physical piano part. Both the earlier modal
projection and this stateful filter are causal.

`source-index.json` maps every original absolute path to its repository-relative
archive and SHA-256. All 22 frozen producer inputs retain their exact bytes,
including the old 5-anchor model/calibration, original API facade, instrumented
copies, observer and orchestration. `original_core/` and `instrumented_core/`
are historical fixtures. Production code remains under the repository's normal
`src/` and `include/` paths. Do not edit a fixture to change the instrument.

`frozen_driver/` preserves the original orchestration scripts, including their
historical workspace paths. Use the new portable launcher instead:

```sh
python3 tools/experiments/causal_radiation_pilot/producer/replay.py --phase verify
python3 tools/experiments/causal_radiation_pilot/producer/replay.py --phase math \
  --output /tmp/keyra-causal-math
python3 tools/experiments/causal_radiation_pilot/producer/replay.py --phase synth \
  --case C3v4 --output /tmp/keyra-causal-C3
```

Omit `--case` to synthesize all six fixed cases. `--jobs` accepts 1 or 2. Each
case holds its note from 0.1 seconds to the 3.8-second end; controls and velocity
are fixed by `cases.json`. Every non-verify phase requires a fresh, empty output directory outside source,
reference and audio trees; existing evidence is never overwritten.
Preparation/compilation, diagnostic capture and rendering can take minutes;
this is not a realtime host benchmark.

Requirements are a C++17 GNU/Clang-style compiler (override with `--cxx`), Python,
NumPy and SciPy. No acoustic recordings or ignored `out/` source files are needed
to build the model, run its math checks, or generate old/new model audio. Frozen
source copies are compiled directly; the launcher does not regenerate or rewrite
DSP. Original WAVs, raw proof rows and compiled binaries are omitted. Historical
payload hashes allow comparison on the original compiler/architecture; a fresh
build elsewhere can differ in floating-point details.

Math replay regenerates all 475 board and 17,778 modal coefficients, tests
unforced storage, constant-force zero pressure, compiled frequency responses and
reset/partition continuity. Synthesis emits baseline/candidate/stem WAVs, the
virtual driver, diagnostic traces and physical-state/force checkpoint proofs.
Only observation changes; the original mechanics run once per case.

The recorded TRAIN comparison additionally needs the authenticated Salamander
Grand Piano V3 reference files and the frozen metric workflow described in the
[parent review documentation](../README.md). Do not treat regenerated model audio
alone as new reference validation. No new fit, parameter search or acquisition
is performed by this producer.

The source has the repository's existing ownership terms; this archive adds no
license grant. The separate Salamander recordings are Alexander Holm's work
under CC BY 3.0, with attribution and source identities in
[the full-range reference documentation](../../../../References/GrandFullRange/README.md).
No recording, recorded impulse response or playback sample is bundled here.
