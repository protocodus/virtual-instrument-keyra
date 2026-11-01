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
| 1 | Continuous whole-pattern pitch interpolation: remove abrupt changes in note body, stereo image and tail between anchors. | Native diagnosis finds energetic gain steps of several dB. Coherent colour normalization removes that gain discontinuity, but both its original and anchor-preserving forms leave phase/stereo/tail switches. Exact endpoint preservation alone is insufficient. Derive and test complete four-lane stereo transport before a broad benchmark. |
| 2 | Layer-resolved body excitation and better stereo representation: prevent quiet notes inheriting loud-layer body energy. | Kawai TRAIN80 proves that the current weighted line can greatly overstate a soft body component. Per-layer magnitudes repair that excess but expose upstream fixed-pole and pickup losses at the loudest layer. Keep the genuine fundamental correction separate from this body error; avoid a scalar compensation or invented resonance. |
| 3 | Fit against the actual played observation model, including stereo compression, contact cap and smoothing. | Fixed-pole ALS improves its waveform objective, and correcting the energy denominator helps one Helsinki note. Exported attack/tail tradeoffs remain. Do not substitute raw fit quality for native recording agreement or discard a measured slow component to improve the attack. |
| 4 | Consistent stochastic noise covariance across bands and simultaneous strikes. | Independent bands repair a proven density-calibration mismatch. The 933-case recording comparison is mixed, with dev noise-error changes around −0.20 to +0.16 dB. Chord headroom and stereo covariance across strikes remain unresolved. Retain this as a separate shared-engine correction, not evidence of a large overall realism gain. |
| 5 | Donor-informed uncertainty or structural priors for genuinely missing measurements. | The dense Steinway masked-layer pilot rejects direct transfer of another piano's velocity curvature in every primary aggregate. The tail prior also lacks reliable coverage. Keep target anchors and voicing; a useful donor method must win masked-target prediction before filling production gaps. |

The [follow-up evidence](../validation/calibration-followups-2026-11-01.md)
records negative results, native controls and remaining limits. None of these
follow-up candidates has replaced accepted 0.4.2. No fixed seed, favorable
window or single piano may be selected afterwards to conceal a regression.

Progress remains active until the sound and whole-range requirements have
direct evidence for all six pianos. A prepared dataset, a favorable aggregate
score, or one improved piano is insufficient.
