# Preserved full-model optimization probe

The original mechanical model remains immutable. These experiments keep all 88 keys, 230 strings, 17,778 string modes, 475 soundboard modes, nonlinear hammer contact, reciprocal bridge coupling, and the complete calibrated radiation map. No candidate is adopted into the production engine.

The native loop fusion delivered about 4.6% lower median process CPU time in this run. Its advantage is small compared with the run-to-run spread. Compiler settings materially changed the result: the scalar/no-builtin build penalized damping fusion alone and benefited from fusing string impulse application with radiation observation. These are measured host medians, not validated speedups on Reason's DSP compiler.

Each timed render is 0.35 seconds at 48 kHz, with a mixed bass/mid/treble event stream, three velocities, pedal changes, note releases, and a repeated middle note. Variants are interleaved for three repeats. Process CPU timing excludes other processes' direct CPU time, but shared-host frequency, cache and scheduling effects remain. The preserved baseline still takes roughly six CPU seconds per audio second in the native build; this is an offline quality reference, not a real-time plugin result.

| Candidate | Native process CPU; change from baseline | Scalar/no-builtin process CPU; change from baseline |
| --- | --- | --- |
| baseline | 2.0999 s (-0.0%; range 2.059–2.134) | 2.9307 s (-0.0%; range 2.586–3.093) |
| free_damping_fusion | 2.0032 s (-4.6%; range 1.953–2.253) | 3.7651 s (+28.5%; range 3.575–3.927) |
| invariant_cache | 2.0912 s (-0.4%; range 2.037–2.093) | not run |
| combined | 2.0537 s (-2.2%; range 2.026–2.135) | 2.5729 s (-12.2%; range 2.560–4.548) |
| hot_key | 2.0525 s (-2.3%; range 2.037–3.048) | not run |
| impulse_radiation | 2.0027 s (-4.6%; range 1.978–2.098) | 2.4026 s (-18.0%; range 2.362–2.478) |

Native flags are `-O3 -DNDEBUG -std=c++17 -ffp-contract=off`. The scalar approximation additionally uses `-fno-builtin -fno-tree-vectorize`. Neither enables fast math or FMA contraction. Both use the same compiler and source/calibration hashes recorded in their JSON reports. This is a host approximation of restricted DSP compilation, not the Jukebox toolchain, and it does not establish Reason compatibility.

## Exactness checks

All timed default runs produced identical float32 stereo WAV bytes **and identical canonical final runtime-state bytes**. The state snapshot includes string q/p/damping arrays, string port velocities and forces, hammer and key state, pedal state, soundboard q/p/force, output filter state, and final stem observations. Optimization caches are excluded. Final-state equality checks full double precision, which float32 output equality alone would not establish. This verifies these event streams and compiler configurations; it is not an exhaustive proof for every possible parameter or event sequence.

The native build additionally checks the same complete 0.35-second sequence with 96 kHz primary/secondary/transient stereo stems, sympathetic coupling disabled, bridge coupling zero, and uncalibrated settings. Every candidate's audio and stem files match the original exactly. Damping fusion, invariant caching, combined caching/fusion, and impulse/radiation fusion also preserve final double state in every extra case.

The experimental `hot_key` candidate fails the bridge-zero state check: it updates the stored string port velocity even though the original bridge-zero path leaves it untouched. The resulting audio is identical, but this candidate is rejected for full state parity. The native report deliberately records the failure and the profiling command exits with status 1. This result does not affect the frozen original or the passing candidates.

Every candidate passes the original conservative hammer-contact and passive reciprocal-bridge self-tests. The independent preserved v2 physics probe also passes for the baseline, damping fusion, invariant caching and hot-key experiment: all 17,778 projection modes and 88 keys are checked; the maximum analytic board-transfer relative error is 4.94e-16 and stored projection coefficient error is zero. These are numerical contracts, not comparisons against piano recordings.

## What was changed in the copies

- `free_damping_fusion` combines the two damping passes with free rotation only for keys whose hammer is inactive. Active contact retains the original integration sequence and arithmetic order.
- `invariant_cache` caches fixed board products, string bridge denominators, and 3x3 bridge elimination factors without changing physical topology. Extra bookkeeping and changed code generation can outweigh the saved arithmetic.
- `combined` uses both of the preceding changes.
- `hot_key` additionally moves independent key-local unison/port-velocity work next to its modal updates. Its bridge-zero final-state mismatch disqualifies the tested version.
- `impulse_radiation` combines the passing damping fusion with one loop applying string port impulses and calculating the unchanged per-string radiation sums. Later additions to the soundboard output remain in the original string order, so their floating-point accumulation order is preserved. Disabled-bridge and uncalibrated branches keep their original path.

The instrumented native baseline attributes approximately 29% of render time to modal rotations/contact, 20% to unison contraction, 21% to the reciprocal bridge solve and modal port scans, and 29% to radiation observation. Controls are about 1%. These are diagnostic wall-clock stage fractions, and instrumentation itself has overhead. No single scalar setup calculation dominates the total.

## Reproduce and inspect

`python3 tools/profile_reference.py` reconstructs the frozen baseline, the reproducible damping-fusion candidate and an instrumented baseline from the preserved source. Add `--scalar` for the restricted host approximation and `--extra-parity-cases` for the option/stem comparisons. The report records tool/source/compiler hashes and full source diffs for every external candidate. Exact command arguments and compiled source snapshots used for the other candidates remain under `out/reference-optimization/`.

- `Validation/reference-optimization.json`: native interleaved timings, source diffs, physical self-tests, full-state hashes, extra option/stem checks, and the deliberately rejected hot-key state result.
- `Validation/reference-optimization-scalar.json`: separate scalar/no-builtin interleaved timings and exact default audio/state checks.
- `Validation/reference-optimization-physics.json`: independent original v2 numerical probe results.
- `out/reference-optimization/profile-run/` and `scalar-run/`: binaries, input and instrumented source snapshots, WAV and raw state artifacts.

The original `Research/GrandPianoV2/src/grand.cpp` and `calibration.h` were not edited. Approximating or removing mechanical states requires a separate matched listening comparison against this preserved model; these experiments do not authorize such a change.
