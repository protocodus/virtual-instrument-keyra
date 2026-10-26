# Keyra development

Keyra owns the piano model, measured numeric data, performance behavior and DAW
plug-in. The Reason Rack Extension is a thin adapter in
`reason-rack-extensions/Examples/Keyra`, consuming this canonical source.

- `Source/DSP/` is JUCE/Reason independent, C++17 compatible, with no allocation,
  I/O, blocking locks or exceptions in note/controller/render callbacks.
- `Source/Plugin*` contains DAW parameters, state and the native editor.
- `Research/GrandPianoV2/` is the preserved offline nonlinear reference. Do not
  rewrite its solver, training split or frozen benchmark results to make a new
  candidate look better.
- `Tools/` contains current measurement, render and calibration workflows.
- `Docs/research/`, `Docs/validation/`, `Docs/benchmarks/`, `Docs/guide/`,
  `Docs/plans/` and `Docs/release/` hold the corresponding evidence.

The live reduced modal model is a separate candidate. Never describe its sound,
physics or CPU as equivalent to the preserved solver without measurements.
For that retained frontend, C2–C6 at velocity layers 4/12 are training data; report all twelve in-range
held-out cases and both edge cases, including regressions. Reference audio is
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

The later full physical path lives in `src/full_instrument/`, `include/keyra/`
and `src/full_reference/`. Its locked full-range corpus is documented under
`References/GrandFullRange/`: 34 TRAIN cases at 17 anchors, with separately
identified previously observed evaluation cases. Preserve those roles and all
reported regressions. `OriginalControl` stays the default; the frozen confidence
calibration is an explicit build profile. The full Reason experiment lives in
`reason-rack-extensions/Prototypes/Keyra` and uses the same pinned instrument
checkout as the existing adapter. It is not a packaged replacement for it.

Preserve the existing `KeyraDSP`, `keyra_render` and JUCE `KEYRA_BUILD_PLUGIN`
targets when changing full-model code. The additional preview is
`keyra_preview_render`, CLAP uses `KEYRA_BUILD_CLAP`, and the complete physical
renderer is `keyra_full_render`. Follow `docs/DECISIONS.md` for the user's default
sound priorities and precision/phenomena tradeoffs. Frozen evidence can precede
later source changes; keep its original hashes and explicit scope.
