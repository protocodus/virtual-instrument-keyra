# Realism and whole-keyboard interpolation

The owner requests improved realism for every Keyra piano, using recordings as
benchmarks, primarily Yamaha C3, Belmont (Mom’s Baby Grand) and Helsinki upright. Every model must remain
consistent over A0–C8 and velocity while keeping its own character. Measurements
from other pianos should constrain gaps rather than replace the target piano's
measured voicing.

The implementation baseline is `ba3ee9908645`, including the latest soundboard
refits and Belmont. Work is isolated on `codex/keyra-realism-20261101`. Earlier
research at `e96ce8a8bf58` remains historical evidence, not this baseline.

The owner later supplied [bitKlavier's House ORTF Steinway D](../research/bitklavier-house-ortf-2026-11-01.md).
Its 30 recorded pitches and 16 layers add a dense velocity-interpolation
reference. Its source family and whole-pitch roles are frozen; an initial
21-file training survey is complete. Test masked training layers before using
it to fill another piano's gaps. Preserve its documented gain balancing,
fades and room perspective as observation limits, and retain each target
piano's own measured level and spectral anchors.

## Required evidence

- Unchanged native baseline renderer, source hashes and train/dev recording
  scores for grand, upright, Kawai, Hamburg, New York and Belmont. Keep each
  library's source identity in every feature cache. Preserve existing splits
  and sealed evaluation rules.
- Yamaha C3 import with exact sample boundaries, hashes, deduplicated mapping,
  velocity and pedal metadata, and a whole-pitch train/dev split. Yamaha is an
  additional acoustic reference; its measurements do not make every model a
  Yamaha. Helsinki's paired microphones and real repeat recordings retain their
  existing data roles.
- Cross-piano interpolation candidates selected by masked training pitches,
  then checked on existing dev pitches. Assess wide gaps and edge extrapolation
  separately. Preserve reliable anchor measurements and instrument-specific
  voicing, pickup relationships and velocity behavior. Report unsupported
  parameters and all per-model regressions.
- Dense A0–C8 checks at multiple dynamics: energy/envelope, spectral balance,
  pitch/inharmonicity, decay, stereo, note release and pedal behavior. Adjacent
  notes need continuity without forcing acoustic irregularities to disappear.
- Recording-guided improvements to the shared strike/body and interaction
  model, following the ranked research; do not treat cache fixes or corpus
  preparation alone as completion of the sound goal.
- Candidate native C++17, affected suites and unit/audio/perf tiers; separate
  source benchmarks from listening preference and host performance. Prepare
  short lettered comparisons for audible choices the recordings cannot settle.
- Version/provenance/documentation updates for accepted DSP behavior, followed
  by the corresponding adapter integration and validation when ready. No PR
  merge without the owner's explicit request.

## First experiments

1. Repair reference-cache identity and import the primary recording libraries.
2. Reconcile the onset fitter with the runtime's contact cap and smoothing in
   an opt-in candidate; the previous smoothing-only refit did not improve the
   benchmark, so parity alone is not grounds to adopt a refit.
3. Evaluate cross-piano structural priors as corrections to each instrument's
   own interpolation. Learn regularization from masked training anchors;
   preserve anchor endpoints and measure gains on gaps/edges independently.
4. Use those results to select and implement shared engine/data changes, then
   run all-model acoustic and controller regressions and listening comparisons.

## Current priority by likely audible impact

This ranking is an engineering judgment from the bounded native measurements,
not a listening-test result or an estimate of every piano's error. The accepted
velocity-pattern interpolation and pitch-rate confidence change remain in
0.4.2; the owner preferred B for the Belmont velocity progression. That verdict
does not select the subsequent candidates below.

| Priority | Mechanism and likely effect | Comparison with the experiments so far |
| --- | --- | --- |
| 1 | Continuous whole-pattern pitch interpolation: remove abrupt changes in note body, stereo image and tail between anchors. | Coherent colour normalization leaves phase/stereo/tail switches. The subsequent one-window spherical transport removes sampled switches but creates a 9.060 dB late-energy excursion above Upright53's anchors. Reject it. Optimistic multi-window eligibility leaves only small possible contributions in nine selected intervals, without full-velocity certification or common-gain closure. A different multi-window/stereo formulation is needed before a broad benchmark. |
| 2 | Layer-resolved body excitation and better stereo representation: prevent quiet notes inheriting loud-layer body energy. | Kawai TRAIN80 proves a weighted-line error, but the completed 65-layer/12-anchor TRAIN panel does not show comparable quiet excess across all six pianos. Its softest-layer body-minus-recorded-total range is −8.540 to +1.073 dB, with no identified body-only target. Keep any repair specific to measured export-stage evidence; do not add a global body gain or invented resonance. |
| 3 | Fit against the actual played observation model, including stereo compression, contact cap and smoothing. | The completed 15-layer final-excitation retention trial is rejected: four solver failures, seven tail case/window violations, and worse middle-window mean error at all three notes. Success-status cases still regress in full late tails and middle energy. Fixing one slow pole is insufficient, and an aggregate fit gain does not license a refit. Diagnose numerical conditioning and the mismatch between the objective and audible-window behavior before further fitting; this failure is not a capacity proof. |
| 4 | Consistent stochastic noise covariance across bands and simultaneous strikes. | Independent bands repair a proven density-calibration mismatch. The 933-case recording comparison is mixed, with dev noise-error changes around −0.20 to +0.16 dB. Chord headroom and stereo covariance across strikes remain unresolved. Retain this as a separate shared-engine correction, not evidence of a large overall realism gain. |
| 5 | Donor-informed uncertainty or structural priors for genuinely missing measurements. | The dense Steinway masked-layer pilot rejects direct transfer of another piano's velocity curvature in every primary aggregate. The tail prior also lacks reliable coverage. Keep target anchors and voicing; a useful donor method must win masked-target prediction before filling production gaps. |

The [follow-up evidence](../validation/calibration-followups-2026-11-01.md)
records negative results, native controls and remaining limits. None of the
rejected calibration candidates has replaced the accepted data. No fixed seed, favorable
window or single piano may be selected afterwards to conceal a regression.

The separate soft-pedal lane-bias change is accepted locally in 0.4.4 after the
owner chose B for the new upper and bass Belmont phrases, which include known
tradeoffs. Combined validation preserves the 933-case default-soft benchmark
against 0.4.3 and matches B exactly across all 1,584 soft-on keyboard cases and
both selected phrases. Native unit/audio/performance and VST3/CLAP checks pass.
Transporting existing biases removes selected rank-crossing discontinuities;
920 interpolated waveforms still change against the older soft-on control,
including −2.398 dB middle level at Belmont89/v120 and larger adjacent gaps
elsewhere. The choice supports this direction without claiming uniform audible
improvement, a measured soft-pedal acoustic target or mixed-string continuity.
Rack integration follows canonical acceptance.

The independent reset fix is accepted locally as 0.4.3: all 37 reset-history
cases match a fresh engine, the 933-case recording comparison has no regressions,
and native unit/audio/performance and VST3/CLAP validation pass. Rack 0.4.3d1
pins that exact revision and passes native/sanitizer, SDK/package and protected
fresh Recon playback checks. The reset fix remains in 0.4.4; the rejected
calibration candidates remain out of production.

The bounded late-retention trial is complete and rejected. Identity/export
preflight passes, but four solver failures and actual native tail/middle
regressions prevent adoption. Its conservative convex subset contains shipping;
this result cannot prove the full representation impossible. No new fit or
broader calibration follows from the checkpoint.

Yamaha's repeatability intake is also complete: sixteen new TRAIN regions plus
eight existing controls at MIDI 48/69, P/MF and pedal up/down. The descriptive
mapped-state tail contrast strengthens at MIDI 69 and remains mixed at MIDI 48.
The tested exact-copy explanations are excluded, but independent strikes and
equal physical velocity remain unproven. Retain all within-state variation;
do not assign independent-replicate weights or infer a shared coupling gain,
receiver identity or decay law. The existing 80% pedal lift remains unchanged.

Progress remains active until the sound and whole-range requirements have
direct evidence for all six pianos. A prepared dataset, a favorable aggregate
score, or one improved piano is insufficient.
