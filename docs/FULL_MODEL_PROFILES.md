# Full-model build profiles

`OriginalControl` remains the default. `FrozenConfidenceGrand` is an explicit
engineering build selection for reviewing the frozen confidence calibration with
the full model. It adds no runtime model loader, recording playback or user
control. It is not a default promotion, perceptual approval or realtime claim.

**Integration status:** generation, private-model parity and actual FullInstrument
integration pass. Both profiles pass native/scalar behavior tests; the candidate
also passes actual API/private-profile ASAN/UBSAN checks. SDK-free Reason wrapper
checks pass for both profiles, native/scalar cores and all four declared rates;
see [the separate receipt](../Validation/reason-full-profiles.json). None of
these tests is a Reason SDK/host or realtime qualification.

| Profile | Anchors | Strings | String modes | Board modes |
|---|---:|---:|---:|---:|
| OriginalControl | 5 | 230 | 17,778 | 475 |
| FrozenConfidenceGrand | 17 | 230 | 17,849 | 475 |

The profile files are tracked under
`src/full_instrument/profiles/confidence_grand/`. The JSON and numeric header
are exact copies of the frozen fitted candidate. Runtime uses compiled constants
and never opens their historical source paths or any reference audio.

## Reproducible source adaptation

A seventeen-anchor header cannot simply replace the five-anchor control header.
The confidence generator starts from the pinned **double** original renderer and
applies the same five guarded changes as the frozen fitter:

1. Bracket actual sorted anchor notes and semitone distances.
2. Permit the frozen ±70-cent tuning range.
3. Apply bass stiffness extrapolation only below the first anchor.
4. Apply treble late-loss extrapolation only above the final anchor.
5. Apply treble common-unison loss extrapolation only above the final anchor.

The generator hashes the fitter's `build_candidate` function and reads its five
literal replacements through Python AST parsing. It does not import or execute
the fitter, NumPy or SciPy. Each original site must occur exactly once. The
adapted double source SHA256 must be
`aeab17da971bc0136635af0d0a83134936ae23d39c5f3b3f0cdbdf0fbd7240ba`;
applying the existing hot-float transform once must reproduce the frozen source
`8d6abcd41d89a32b54366106c54ebb62a9b52de21dc21402a7c179c55af88e56`.
The existing runtime/fault/contact/pressure transforms then prepare that same
physical model. Feeding the already transformed float source back into this
workflow would apply precision conversion twice and is not supported.

Standard-library validation checks the frozen JSON/header hashes, seventeen
integer anchors, finite positive scalar parameters, four finite length-64 arrays,
positive losses and prompt loss not below late loss. A standard-library emitter
reproduces the frozen header byte for byte using the original field order and
`.17g` number formatting. Historical paths in JSON remain metadata.

```sh
python3 src/full_instrument/generate_prepared_model.py
python3 src/full_instrument/generate_prepared_model.py --profile FrozenConfidenceGrand
```

The first command writes the existing control directory; the second defaults to
the separate confidence directory. Confidence generation refuses to overwrite
the control directory. An explicit `--output-dir` supports verification in a
private build directory. The original generated model and calibration remain
byte-identical; generator provenance records the updated generator honestly.

## Build selection

CMake accepts only:

```text
KEYRA_FULL_MODEL_PROFILE=OriginalControl
KEYRA_FULL_MODEL_PROFILE=FrozenConfidenceGrand
```

Omitting the setting selects OriginalControl. `FullModelProfile.cmake` resolves
metadata and explicitly overrides inherited profile macros on supported GCC,
Clang and MSVC targets. Unknown profile names fail configuration. The private
`SelectedModel.h` chooses exactly one prepared header using numeric selector
0 or 1, rejecting other values. Public API, controls, repetition and mechanism
code are shared; no runtime switching is introduced.

FullInstrument.cpp now includes this selector. Its repetition, seeded touch
variation, key/pedal mechanisms and shared-body network remain the same code in
both profiles. The mechanism/body coefficient cache is model-independent and
does not include a second default model header.

## Phase A evidence

[Generator/private-model receipt](../Validation/full-profile-phase-a.json)
verifies both profiles reproduce their tracked model, calibration and provenance
exactly under `python -S`. Six malformed numeric profiles, ambiguous source-site
matches and a candidate attempt to overwrite the control are rejected.

The new `tests/full_profile_tests.cpp` checks complete topology, all-key anchor
bracketing, measured extreme anchors, four-rate finite excitation, allocation-free
render/reset and retained unison pointers. It is a private-model test; it does not
claim controller or Reason coverage.

The confidence prepared model matches the actual frozen hot-float CLI's
float32 output **byte for byte at 48 and 96 kHz**, with the original 24 Hz high-pass
and an irregular event/block schedule. These parity cases explicitly use the
legacy contact path and pressure SIMD disabled, separating calibration/source
identity from later numerical optimization. No recording is decoded and no new
fit is performed by these checks.

The initial preflight stopped on an incorrectly written match-count test fixture
before any C++ build or DSP render. Its source and failure receipt are preserved
under `out/full-profile-phase-a/`. The final complete study is `v3/`; it also
checks normal-render fault counters before resetting them. The earlier v2 source
inputs are retained as a historical snapshot.

## Actual API evidence

The [actual API parity receipt](../Validation/full-profile-api-parity.json)
compares the confidence FullInstrument against the actual frozen CLI at 48 and
96 kHz, with both legacy and bounded-Newton contact. All four float32 payloads
are byte-identical. These isolated comparisons disable humanization/mechanism
levels and bypass repetition so that they test the frozen calibration identity;
the mechanism cache remains enabled. They report four launches, the complete
17,849-mode topology and zero faults, unsafe launches or rejected inputs.

The [profile integration matrix](../Validation/full-profile-integration.json)
then exercises normal repetition and mechanisms in the actual API. Both
OriginalControl and confidence pass the native and scalar test suites plus
private topology/anchor tests. The candidate passes actual API and private-model
ASAN/UBSAN tests. Coverage includes touching notes, ringing-state repetition,
block partitions, seeded variation, reset/independence, runtime allocations,
four supported rates, mechanism isolation and cache reprepare/reset.

Expected topology remains explicit per build: 17,778 for the control and 17,849
for the candidate. The control header and model remain byte-identical. Its
unchanged ASAN behavior is covered by the preserved mechanism-cache matrix;
candidate dimensions receive new sanitizer coverage rather than repeating that
unchanged control run. Existing original-control CLI parity tooling is retained.

Native builds use bounded-Newton contact and the mechanism cache, with pressure
SIMD disabled. Scalar builds retain the same selected calibration/contact/cache
and disable compiler vectorization. This is behavioral and memory-safety
validation; elapsed test time is not an audio callback measurement.

## Fidelity limits

The candidate uses all TRAIN34 for fitting. The subsequent historical regression
contains previously observed recordings, including both extremes; it is not fresh
validation. A0 relative-rise timing, C2 envelope and the unresolved C8 component
remain material issues. See [confidence results](FULL_CONFIDENCE_LOSS.md) and
[attack diagnosis](FULL_ATTACK_TIMING.md). No new instrument/microphone
independence, Reason SDK/host test or callback budget is established.
