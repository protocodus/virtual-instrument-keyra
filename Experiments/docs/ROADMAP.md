# Keyra product goal and release gates

Build a realistic, expressive **Reason Rack Extension** that earns a price above US$199 through sound, playability and reliable host behavior. The user clarified Reason as the product priority and authorized the most efficient development environment. **Linux is the DSP, recording and mock-host test target.** VST3/CLAP remain optional development harnesses; Windows VST3 is secondary. A compiled harness and good aggregate recording scores are insufficient for RE release.

The latest priority is explicit: **get the default model on par with recordings before expanding material choices, presets or product UI**. The compact material evidence and connected component prototypes are retained as test infrastructure. Do not switch the default to an unvalidated physical candidate merely because it has more mechanisms.

The user subsequently reports the original pre-split demos sounded better. The
preserved full nonlinear model is therefore the sound-quality baseline; the
reduced live model's lower note errors do not override that feedback. Follow
`QUALITY_BASELINE.md` and the recorded listening direction in `Docs/decisions.md` at the repository root.

The user then explicitly chose optimizing the original model and clarified that
it also needs realism improvements. Acoustic recordings remain the target;
the original is the starting point. Exact-output parity checks the current
numerics-preserving transformations. Intentional sound changes need recording/listening evidence and may
improve on the original rather than preserve its flaws.

The user also accepts precision/quality tradeoffs when hardly audible and puts
perceptual completeness ahead of extreme precision in one subsystem. Retain an
exact comparison version while testing faster numerical and reduced models;
approve their sound through recording/listening evidence, not byte equality
alone. Give low-cost, state-linked action/release and acoustic behavior an
explicit CPU budget alongside the tonal core. See `Docs/decisions.md` at the repository root.

## Completed foundation

- Preserve the original nonlinear mechanical reference, calibration and frozen evidence without editing them.
- Separate recorded grand and upright calibration with pinned licenses/hashes and excluded cases; no runtime sample playback.
- Playable 88-key, 64-voice modal engine with fast/slow decay, detuned aftersound, partial sustain damping, note identity and bounded stealing fades.
- Four instrument voicings, three bounded material voicings, six procedural mic setups and ten stable host controls.
- VST3 and CLAP wrappers, portable state, sample-offset notes/automation, headless ABI tests and official VST3 validator.
- Regression coverage for velocity monotonicity, sample rates, block invariance, pedals, repeated notes, malformed inputs, multi-instance independence, microphone mono compatibility and C++ allocations in real-time entry points.
- Thirteen grand fitting pitches at two velocities, seven newly reserved evaluation cases, a phase-consistent decay fit and exact attack-cost reductions.
- Isolated contact/action, modal strings/bridge/wood, acoustic-load and connected-chain research tests; see `MODULES.md`. Numerical passivity does not establish calibrated realism.
- Full physical block API with persistent strings, bounded seeded excitation variation, deferred hammer-safe repetitions and connected key/pedal resonators. Virgin hammers start at their authored rest plane; native/scalar/sanitizer and original-control output parity checks pass. See `FULL_BACKEND.md` and `STRIKE_REPETITION.md`.
- Touching MIDI releases/represses finish a finite key lift and retain string/hammer state; seed and block-partition checks cover the canonical API and opt-in Reason source wrapper. The full offline renderer and matched musical clips expose this path without added sample playback.
- A bounded contact solve preserves all 16 tested float-output cases and roughly halves dense-strike peak cost. Its timing regressions remain documented. Later free/unison fusion and current pressure-readout studies reduce native cost with exact physical-state checks; fresh supported OriginalControl builds enable both after compiler checks. The pressure output has tightly bounded numerical differences, and realtime remains unresolved; see `PRESSURE_CURRENT.md`.
- An authenticated eight-recording mechanism training corpus and eight unopened reserved files, plus reciprocal full-model cavity/lid/player research integration with source/coupling ablations. Capture-state ambiguity and authored air/texture levels prevent a calibrated-realism claim.
- Public A0 and C1–C8 coverage, 34 full-model training recordings at 17 anchors, and a frozen v4 evaluation with predictions made before reserved recordings were decoded. The mixed candidate was not promoted; see `FULL_CALIBRATION.md`.
- Actual full-API 48 kHz/64-frame timing and stage measurements. The frozen pre-contact-optimization native path takes 3.31–3.47 CPU seconds/audio second in the bounded cases. Bridge/radiation dominates; see `FULL_BACKEND_BUDGET.md`. Later contact gains and regressions are reported separately; realtime remains unresolved.

## Next iterations, in order

1. **Optimize the original physical model and improve its fidelity.** First preserve the full original mechanics while measuring data-layout, redundant-work and compiler changes against exact output/state checks. Then make intentional acoustic improvements against recordings, especially struck texture, body and stereo, retaining the original and preceding physical version as listening comparisons. The reduced preview's thirteen-pitch grand fit and seven once-reserved evaluation cases remain useful diagnostic evidence; their aggregate gains do not establish a better piano. Use level-matched listening feedback and training-only diagnostics to choose the next mechanism. Report every regression and do not fit ambiguous room/body/mains content as uniquely identified piano physics. Seek controlled recordings where source conditions limit the next inference.
2. **Broaden evidence before new claims.** Add independently licensed instruments and register/dynamic coverage, lock new fitting/validation splits before fitting and report every regression. Upright ordinal layer proxies, edited source audio and unknown microphone/pedal state limit conclusions. Reserve a new instrument and new performances for release evaluation; previously observed cases are regression evidence, not a fresh blind test. Do not tune on the seven evaluated cases and call their next score a fresh result.
3. **Address expressive mechanisms.** Validate damper/re-pedal behavior against controlled release and pedal recordings. Retain the full model's reciprocal sympathetic strings through optimization and host integration; the reduced preview's feed-forward body effect is insufficient evidence for that behavior. Validate the authored repetition/return proxy and variation ranges against controlled action recordings. Investigate nonlinear hammer memory, unison structure, duplex/longitudinal components and register transitions against the preserved reference. Add soft pedal and sostenuto only with correct documented semantics and tests.
4. **Validate materials and microphones.** Obtain controlled recordings or measured geometry before calling presets calibrated wood species or specific microphone pairs. Improve lid/rim/soundboard radiation, keyboard-dependent pickup and room response. Maintain level-matched stereo/mono comparisons; avoid a disappearance of dominant notes under mono fold-down.
5. **Meet real-time deadlines under the actual Rack toolchain and host.** Test 44.1/48/88.2/96 kHz at Reason's 64-frame batch, dense sustain, repeated full chords, long tails and concurrent instances. Include events/stealing in callback timing and report p95/max/deadline misses. Host `-fno-builtin`/no-exception compatibility builds are useful approximations; they do not reproduce the SDK compiler or Reason's shared rack budget. Preserve no allocation, blocking lock or I/O in real-time methods; instrument platform allocations beyond C++ `new` before release.
6. **Complete the Reason product after fidelity evidence.** The source wrapper is staged in `reason-rack-extensions/Prototypes/Keyra`. Publish a reviewed canonical core pin before promotion into the production `Examples/` inventory. Finish master tuning/performance/CV, panels/note indicators, property/patch contracts and an understandable ten-control interface. Run genuine SDK5 `local45`/`universal45` builds and isolated authorized Reason/Recon validation; SDK-free tests cannot establish acceptance. Verify save/reload, automation, duplicate instances, bounce, sample-rate changes and stable identities. Curated presets and material UI follow the default's sound, not precede it.
7. **Release engineering and price validation.** Genuine `.u45` package, Reason acceptance/submission, matching panels/manual/Shop material, supported host matrix, compatibility/migration tests, CPU budgets, support policy and third-party notices. Run level-matched blind listening and musician beta sessions against acoustic recordings and established paid instruments. Investigate response, timbre, fatigue and mix usefulness separately; use buyer evidence to assess the intended price. VST3/CLAP tests and Linux preview archives never substitute for a Rack Extension build.

No marketing claim of production readiness, named-instrument replication, measured wood species, measured microphone emulation or perceptual parity is supported by this preview.
