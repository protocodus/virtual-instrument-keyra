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

Progress remains active until the sound and whole-range requirements have
direct evidence for all six pianos. A prepared dataset, a favorable aggregate
score, or one improved piano is insufficient.
