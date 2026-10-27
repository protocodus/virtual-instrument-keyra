# Working conventions

## Architecture

This is Keyra's canonical repository: it owns the real-time modal piano in
`Source/DSP/`, its measured numeric data and the JUCE plug-in (VST3, AU, CLAP,
Standalone) that wraps it. The Reason Rack Extension in the private
`protocodus/reason-rack-extensions` repository is a thin adapter that mounts
this repository as the pinned submodule `Examples/Keyra/Instrument` and
compiles `Source/DSP/KeyraEngine.cpp` directly. DSP and playing-model changes
land here first; the Rack pin then advances. Reason property mapping, MIDI/CV,
routing, host latency, patches and panels stay in the adapter.

Repository layout, naming, CI, versions and the `Docs/` taxonomy follow the
Protocodus portfolio standard kept in the project, not in this repository.

- The DSP version is the product version: `project(Keyra VERSION X.Y.Z)` in
  `CMakeLists.txt`. Any DSP or behaviour change bumps it, and versions only go
  up; the Rack device's `version_number` takes the same `X.Y.Z` plus its own
  stage suffix.
- `Source/DSP/` is JUCE-free and C++17 (the Rack toolchain); the
  `KeyraDSPCxx17` target proves it. No allocation, file I/O, blocking locks or
  exceptions in note, controller or render callbacks.
- `Source/DSP/KeyraPresets.h` is the factory bank every front end and the demo
  renderer read. `PLUGIN_MANUFACTURER_CODE Ptoc` / `PLUGIN_CODE Kyra`,
  `BUNDLE_ID` and the CLAP id `cz.protocodus.keyra` never change: hosts recall
  sessions by them.
- `Experiments/` is the full physical piano research, a separate CMake project
  (`cmake -S Experiments -B Experiments/build`) that the product build does not
  build. It keeps its own layout, so its receipts and tools still resolve; its
  documents and evidence stay inside it.
- This repository is public. Never add Reason/Jukebox SDK material, secrets or
  unreleased commercial material.

## Documentation layout

`README.md` is the single product document. It opens with the heading and a
one-paragraph intro, the editor screenshot, **Audio demos**, a concise
**Version history** ledger and **Downloads**; after a `---` separator come
**How it works**, **Known gaps**, **Build** and **Licensing**. Long per-version
narratives go to `Docs/release/` and are linked.

Everything else in `Docs/` has one home, and nothing sits loose there except
`decisions.md`, the by-ear decision log described below:

| Folder | Holds |
| --- | --- |
| `audio/` | rendered demos, per-fix previews, committed listening tests |
| `screenshots/` | editor images |
| `guide/` | user, install and preset guides, parameter meaning |
| `research/` | modelling research, references, design notes, experiments |
| `validation/` | audits, test results, host validation |
| `benchmarks/` | CPU and performance measurements |
| `plans/` | improvement plans, requirements, open work |
| `release/` | release checklists, readiness, release notes, asset provenance |

Name documents in lowercase kebab-case, `<topic>-YYYY-MM-DD.md` for dated
work. Moving a document is a rename only: keep its content and date, and update
every link to it in the same commit. Legal files (`LICENSE`,
`THIRD_PARTY_NOTICES.md`, `PRIVACY.md`) stay at the root; upstream licence
texts live in `ThirdParty/`.

Research the code depends on — a specific value, a manual page, a measurement,
a derivation — belongs in a comment **beside the code that uses it**, not only
in a document that drifts away from it. A measurement protocol belongs at the
head of the tool that enforces it.

These README parts are written by the build, never by hand:

- The demo table between `<!-- audio-demos-begin -->` and
  `<!-- audio-demos-end -->`, rendered from one
  `Docs/audio/midi/<NN>-<preset-slug>.mid` per curated preset demo (at most 8,
  each preset showing a different side of the instrument, or every preset of a
  bank of 8 or fewer; change a source only on purpose, in its own commit) and
  committed by the main build as `Docs/audio/<NN>-<preset-slug>.wav`, 8–12 s
  of 48 kHz 24-bit audio.
- The block between `<!-- build-download-begin -->` and
  `<!-- build-download-end -->`, rewritten by the main build, which also
  commits the README screenshot under `Docs/screenshots/`.

Version history is a ledger of what changed about the product — what it
sounds like, what it exposes, what a session must know. Pure refactors,
deduplications and test-coverage additions belong in git history, not in it.

Per-fix audio previews are **one-time review evidence**: render them while the
change is under review, then leave them frozen. Do not re-render them when
later engine changes make them stale.

## A–Z listening tests

This is a physical model with no owned calibration captures, so there are
decisions the measurements cannot close. When a change is audible and the
physics admits more than one defensible option, **render the options as WAVs,
letter them, and let the user decide the direction by ear.** A listening test is
a legitimate way to choose between candidates. It is not a way to fit a number —
see the limit below.

**When to run one.** Whenever any of these is true:

- two or more formulations are each derivable and the model cannot say which
  describes the instrument (which radiation law a body obeys, which of two
  reference geometries a term should be measured against);
- a change is audible and the open question is whether it is an improvement
  rather than whether it is correct;
- a calibrated constant has to be re-pinned and more than one pinning is
  defensible;
- the user asks for one.

Do not run one to decide something a measurement already decides. If a number
settles it, quote the number.

**How to build one.**

- **A is always the shipping engine**, unchanged. B, C, … Z are the candidates.
  So "A against B" is always "what it does now against what it would do".
- **Letters only in the filenames.** `A.wav`, `B.wav`, … carry no hint of the
  mechanism, so the listener is not primed by the label. Write the key down at
  the same time, in a separate `key.md` the user can read after deciding, and
  say in the handover that the key exists and is unread-by-design.
- **Change one thing.** Identical MIDI, seed, sample rate, block size, length
  and controls across every letter; only the mechanism under test differs.
- **Level-match, and say how.** Match on whole-file RMS unless level is itself
  what is being judged, and state the measure and the trims applied. Louder
  reads as better, and an unmatched set tests loudness.
- **Give the same material to every letter**, and pick material that exposes the
  thing under test — a stroke that drives the mechanism hard, not a general
  demo. Keep it short enough to A/B repeatedly.
- Render through the shipping signal path, never through an offline
  approximation of it.

**Where they live.** Listening tests are decision artefacts, not review
evidence. Render them to a working directory and send them to the user; do not
commit them by default — a 26-file set per decision would bloat the repository.
Commit a set only when the user asks, under
`Docs/audio/listening-tests/<date>-<topic>/` with its `key.md`, and freeze it
on merge exactly like the per-fix previews above.

**What gets committed is the verdict.** Record in `Docs/decisions.md` what was
being decided, what each letter was, which letter the user chose, and what that
choice licensed. A direction chosen by ear is recorded as chosen by ear — never
written up as though a measurement had settled it.

**The limit.** A listening test chooses between candidates that are each already
defensible on their own physics. It does not license drawing a constant, fitting
a curve, or keeping a formulation the measurements reject. If every candidate
needs an invented number, the answer is still that none of them ships.

## Shared portfolio tools

`Tools/PresetDemoRenderer.h`, `Tools/update_readme_blocks.py`,
`Tests/ParameterMatrix.h` and `Tests/FuzzHarness.h`, and the Documentation
layout and A–Z listening tests sections above, are byte-identical copies of
the portfolio masters in `reason-rack-extensions/Tools/portfolio/`. Change
them there, never here. Keyra's own parts are `Tools/RenderPresetDemos.cpp`
(the demo voice), `Tools/write_preset_midi.py` (the phrases in
`Docs/audio/midi/`) and `Tests/ParameterMatrixTests.cpp` (the limits Keyra's
design implies).

## Build and verify

```sh
cmake -S . -B build-dsp -DCMAKE_BUILD_TYPE=Release -DKEYRA_BUILD_PLUGIN=OFF -DBUILD_TESTING=ON
cmake --build build-dsp --parallel 2
ctest --test-dir build-dsp -L unit --output-on-failure
```

Use a separate `build-plugin` directory (`-DKEYRA_BUILD_PLUGIN=ON`, the
default) for the processor, editor and packaging. Every test is
`Keyra.<Suite>` with one tier label: `unit`, `audio` (`Keyra.AudioDemos`,
every preset demo rendered twice), `render` (`Keyra.EditorRender`, the editor
screenshot) or `fuzz` (`Keyra.DspFuzz`; `Keyra.ParameterMatrix` in the plug-in
build). Select the suites that cover a change with `-R`, then run the full
suite before a substantive DSP change is called done. A change under
`Experiments/` runs that project's own suite.

A test is never skipped, disabled or loosened to get green. Diagnose a failed
contract against the baseline before changing a fixture, and document why an
assumption was stale.

## Keyra specifics

- `Experiments/Research/GrandPianoV2/` is the preserved offline nonlinear
  reference. Do not rewrite its solver, training split or frozen benchmark
  results to make a new candidate look better.
- `Tools/` holds the current measurement, render and calibration workflows for
  the modal engine; `Source/DSP/MeasuredModalData.h` comes from
  `Tools/fit_realtime_modal.py` and changes only through it.

The live reduced modal model is a separate candidate. Never describe its sound,
physics or CPU as equivalent to the preserved solver without measurements.
For that retained frontend, the locked split `Tools/corpus/split-2026-10-27.json` decides the
training data: its train role is fitted, dev is scored and never fitted, and the sealed pitches are
opened only for a candidate the owner is asked to approve. Report every regression
`Tools/compare_benchmarks.py` lists, and all twelve in-range held-out cases and both edge cases of
`Tools/evaluate_recordings.py`. Reference audio is
Salamander Grand Piano V3, Alexander Holm, CC BY 3.0; retain attribution and
hashes. No recorded waveform or impulse response is loaded by the instrument.

Pedal tests must cover continuous sustain and repedaling, sostenuto's rising
edge capture, soft pedal excitation, channel ownership and reset. Mod wheel
adds smooth damping to sounding strings, including held keys. Common-controller
behavior belongs in the engine and must agree between front ends.

A price target is a product goal, not a fidelity measurement. Source builds,
native tests, isolated-note agreement, host acceptance and listening judgment
are separate evidence. Record unverified release gates explicitly. Keep the
licensed Jukebox SDK out of Git; never label a source-only wrapper a built U45.

The later full physical path lives in `Experiments/src/full_instrument/`,
`Experiments/include/keyra/` and `Experiments/src/full_reference/`. Its locked
full-range corpus is documented under `Experiments/References/GrandFullRange/`:
34 TRAIN cases at 17 anchors, with separately identified previously observed
evaluation cases. Preserve those roles and all reported regressions.
`OriginalControl` stays the default; the frozen confidence calibration is an
explicit build profile. The full Reason experiment lives in
`reason-rack-extensions/Prototypes/Keyra` and uses the same pinned instrument
checkout as the existing adapter. It is not a packaged replacement for it.

The product targets are `KeyraDSP`, `keyra_render` and the JUCE plug-in at the
root. In `Experiments/`, the ten-control preview is `keyra_preview_render`, its
CLAP harness uses `KEYRA_BUILD_CLAP`, and the complete physical renderer is
`keyra_full_render`; preserve them when changing full-model code. Follow
`Docs/decisions.md` for the user's default sound priorities and
precision/phenomena tradeoffs. Frozen evidence can precede later source
changes; keep its original hashes and explicit scope.
