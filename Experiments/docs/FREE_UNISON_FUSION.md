# Free oscillator / unison fusion

**The guarded SIMD candidate passes the native optimization policy with the
same tested sound and state. It is still slower than realtime.** The preceding
scalar fused candidate failed and remains archived. The native optimization is
integrated behind a compiler/profile guard; integration checks are recorded
separately from these frozen experiments.

This work reduces computation in the existing complete piano. It does not
change the hammer, strings, board, damping, calibration, mode counts or controls,
and it is not a recording-fit or realism benchmark. The fixtures exercise the
current full API with humanization, repetition control, mechanical textures and
body coupling enabled.

## Change and measured decision

The original scheduler advances free strings and then visits grouped unison
couplings. The candidate combines those operations for independent rows owned
by one inactive key. Active-hammer keys keep their original contact path;
uncovered modes keep their original free update. Coupling stays after the
relevant free updates and before the shared bridge solve. Arithmetic and
within-row operation order remain unchanged.

Prepared views reuse the original unison coefficients and modal storage. The
inventory verifies all 88 keys and 230 strings, **12,507 fused plus 5,271 fallback
modes = 17,778**, every original **6,168** row exactly once, and 89 groups. The
reported extra view storage is **42,328 bytes**, including vector capacities but
excluding allocator overhead and process RSS.

The scalar fused implementation (`v1`) was 18.1–30.9% slower by median callback
CPU across the six rate/case groups. Five groups also failed the p95 guard.
GCC did not vectorize its fused row loops. This candidate is rejected; one
faster individual outlier is retained alongside all slower trials.

The next implementation (`v2`) adds a guarded `omp simd` directive across
independent rows. There is no cross-row reduction, fast math, FMA, OpenMP worker
runtime or pressure-reduction change. Both comparison arms use the same added
compiler flag. GCC 14's actual API compilation vectorizes all three row-count
templates; manufactured state fixtures report zero bit mismatches before any
model execution. The two baseline binaries remain identical to `v1`.

| v2 rate / case | Median CPU seconds per audio second, old → new | CPU reduction | Median p95 callback CPU, ms, old → new |
|---|---:|---:|---:|
| 48 kHz music | 3.184 → 2.813 | 11.66% | 4.600 → 4.225 |
| 48 kHz repeated notes / pedal | 3.153 → 2.859 | 9.30% | 4.541 → 4.173 |
| 48 kHz dense 88-key tail | 3.198 → 2.943 | 7.95% | 4.791 → 4.562 |
| 96 kHz music | 6.205 → 5.615 | 9.51% | 4.451 → 4.149 |
| 96 kHz repeated notes / pedal | 6.228 → 5.700 | 8.47% | 4.581 → 4.105 |
| 96 kHz dense 88-key tail | 6.432 → 5.979 | 7.04% | 4.820 → 4.384 |

The policy was declared before timing: at least 5% lower median CPU in **every**
group, with no group exceeding a 5% increase in the median of three p95 callback
CPU values. `v2` passes all six throughput and all six p95 guards; all 18 paired
trials are faster. Each study retains every AB/BA/AB trial, all 14,400 callback
CPU/wall measurements, maxima, deadline misses and output identities. No warmup
trial or outlier is discarded.

Every measured callback in both studies misses its wall deadline. The new
48 kHz workload still requires 2.81–2.94 CPU seconds per audio second on this
shared Linux host. Short native timings do not certify worst-case behavior,
Reason SDK performance or realtime operation.

## Exactness and scope

Each candidate first passes the same 16 correctness rate/case groups:
44.1/48/88.2/96 kHz crossed with music, repeated notes/pedal, dense 88-key tails
and silence/reset. Events include offsets inside nominal 64-frame callbacks.
The first two cases last .64 seconds, the others .4 seconds. Each arm advances
574,704 frames across the matrix.

All **1,149,408** paired pre-high-pass float64 pressure values and final float32
output values are byte-identical. Five deep checkpoints per case give **80
paired snapshots**, for **112 paired file comparisons** including audio and
pressure. Snapshots include all common physical state and coefficients,
controller/RNG, full mechanism ledgers/cache and output-filter memory, without
struct padding or raw pointer addresses. Candidate-only execution views are
checked through the separate prepare inventory. This is not a claim about
every internal state at every frame. Output scans are finite and final
diagnostics report zero faults and unsafe launches; reset restarts counters as
the API specifies.

All 18 paired performance audio files also match exactly. Correctness capture
and snapshots are absent from the separate timed binaries. Callback clocks
cover event dispatch plus process, excluding prepare, inventory, file writes,
report generation and timing-vector bookkeeping.

The frozen configuration uses OriginalControl profile 0, pressure SIMD **off**,
fast contact **on**, mechanism cache **on**, seed `0x4b657972` and current API
defaults. There is no new recording access, gain matching, spectral tolerance,
partial removal or perceptual approximation. It does not qualify other piano
profiles, new parts/materials/microphones, the transient click candidate,
Reason/Recon/U45, production readiness or the price-value goal.

Canonical integration defaults `KEYRA_FULL_FREE_UNISON_SIMD` on only for a
supported native compiler and OriginalControl profile 0. Opt-out, unsupported,
profile 1 and scalar/SDK builds retain the original scheduling and storage path,
with target-local macro overrides. Guarding only the pragma would expose the
rejected scalar fused path.

Generated-source reproduction and enabled/disabled source equivalence passed.
Native API/profile/scalar-portability tests passed (3), sanitizer API/profile
tests passed (2), and Reason native/scalar mock-host and contract checks passed
(12). Four configure-only build-policy cases verify eight effective target
macros. A native renderer smoke check reports fusion on, pressure SIMD off,
contact/cache on and no faults. These are host approximations; no actual Reason
SDK or Recon execution occurred.

The original integration tests bind header `31ceb1…`. A later cleanup splits
four cold setup statement pairs across lines without changing C++ tokens or the
hot helper, yielding final header `325a6e…`. Both source versions and the addendum
are retained. All four native and three Reason mock executables rebuild to the
same hashes as the already-tested binaries, with no warnings. The sanitizer
result remains the original pre-cleanup run, linked through token identity;
there is no claim of another sanitizer or timing matrix.

## Evidence

The [compact archive](../tools/experiments/free_unison_fusion/README.md) preserves
both candidates, source-only preparation history, freezes, authorizations,
quality results, every timing trial and independent/root reviews. Its standard
library checker recomputes stored decisions and timing summaries from the raw
callback lists. It does not synthesize, decode omitted binary state/audio or
rerun a benchmark. The [validation summary](../Validation/full-free-unison-fusion.json)
links the exact study identities and separately recorded integration status.
