# Reciprocal mechanism/body cache study

This is a research transformation of snapshotted `FullInstrument.cpp`, with
pressure SIMD off and bounded contact on. Canonical sources and defaults are
unchanged. The study keeps the four sources, their order (body ports 1, 1, 1,
0), reverse body loading, source direct observation and the bridge force.

## Design before measurement

For board mode `j`, let `b[j,g]` be its port shape, `w[j]` its angular frequency,
and `p[j]` its velocity coordinate. Physical port velocity and Gram matrix are

```
v[g] = sum_j b[j,g] * w[j] * p[j]
G[g,h] = sum_j b[j,g] * b[j,h]
```

`Piano` already computes constant `G` at preparation. After the original network
step, gather fresh `v[0]` and `v[1]` once. A mechanism consumes its current
`v[g]` and `G[g,g]`, returns signed impulse `J`, and receives its reciprocal
reaction. Then update every observed port by `v[h] += G[h,g] * J` before the
next mechanism. Accumulate impulses by port and write board modes once after
all four sources. This is the same sequential coupling in real arithmetic;
it does not apply four sources against the same stale body velocity.

Board observation is linear in velocity and force. Preserve the existing
bridge force and add the mechanism force `sum_g b[j,g]*J[g]/dt` once. Compute
its stereo observer using preparation-time force weights. In the one board
write, also accumulate `-2*sigma[j]*w[j]*(p_after-p_before)*mic[j,ch]` using the
**actual rounded float state change**. Position is unchanged during coupling.
No subtraction of two complete board observations is needed.

The existing API rounds board `p` to float after each source. The candidate
rounds once, so mechanical states need not be bit identical. Gram updates also
omit intermediate float-rounding perturbations. Work checks therefore compare
actual board energy change against the sum of each sequential source's body
work, in addition to each source's own ledger. The observer algebra can change
double reduction roundoff. Neither difference is labeled inaudible in advance.

Preparation rebuilds all coefficient and observer caches for the new board and
sample rate. Render-time port velocities and impulse accumulators are reset
at every post-network coupling stage, including after sound resets. No stale
velocity crosses `model->step`. The board and coefficient arrays have separate
storage; no restrictive alias assertion, source removal, global fast math,
OpenMP runtime, new randomness, or render allocation is introduced.

## Required guards

Before timing, require the copied baseline to retain canonical arithmetic;
exercise actual 475-mode board coupling with source and reverse-transfer
energy/work ledgers; retain zero-source/coupling-off ablations; and compare
bounded C4, music and repeat renders at 48/96 kHz. Log mechanical, hammer,
controller, raw stereo pressure and API output changes separately. Rendering
uses nonzero sources. Numerical checks precede any performance decision.

Initial engineering tolerances: isolated coupling step energy rise at most
`5e-7` of initial energy and work mismatch at most `1e-6` of initial/external
energy scale; no new solver fault or change to strike admission. These allow
float arithmetic error and do not constitute an exact passivity proof.

Timing remains pending until the other heavy jobs are quiet. Any gain must be
reported together with regressions; no default adoption is implied.

## Frozen results

The 24 isolated cases per variant cover both rates, three board-energy scales,
triggered and untriggered reciprocal transfer, and nominal/1000× coupling
resistance. The cached variant has no positive energy step in this audit;
maximum actual board-work mismatch is `1.42e-8` of the energy scale, versus
`3.01e-8` for the original four-write stage. Each source ledger residual stays
below `3.63e-19` nominal joules. These results satisfy the unchanged float
engineering guards; they do not establish exact arithmetic passivity.

Fourteen complete .35-second renders cover C4, music, repeats and four
ablations at 48/96 kHz. All seven sampled discrete controller fields and reported strike diagnostics
match. Source-off, coupling-off and silent outputs/states are byte identical.
The copied macro-zero C4 baseline also matches the independent actual full API
renderer byte for byte. Intact output nulls range from −117.12 to −109.49 dB
relative RMS; the largest float sample difference is `4.80e-6` (−106.38 dB
relative to sample magnitude one). Mono-fold nulls are also retained. These
are normalized model samples, not acoustic pressure or an audibility verdict.

The largest observed return-depth difference is `2.06e-10` nominal metres;
normalized recovery differs by `1.72e-8`, consistent with recovery being depth
divided by the authored .012-metre rest depth. This geometry is a playing proxy.
The first analysis mistakenly demanded byte identity from continuous controller
state; a later unit-mixed `1e-10` check also fails at three checkpoints. Both
failed expectations and tool revisions are retained. Discrete admissions remain
exact, and the original physics/audio guards were not loosened. Continuous
state differences are reported without claiming a universal propagation bound.

A separate cache contract passes ASAN/UBSAN: preparation at 48→96→48 kHz, nine
zero/nonzero observer cases, preserved board position/bridge force, fresh
accumulators, and zero ordinary C++ render allocations. Its observer identity
residual is at most `1.42e-15` after scaling. Direct malloc/aligned APIs are not
intercepted. Timing binaries omit diagnostic pressure/state capture.

Three preregistered AB/BA/AB pairs use the same CPU 0 for both variants. Each
pair renders music/repeats at 48/96 kHz: 24 case cells, **12 paired comparisons**.
Preparation, compilation, event dispatch and file I/O are excluded. Every timed
output matches its corresponding correctness binary. No extra pairs were run.

| Rate/case | Original median CPU/audio | Cached median CPU/audio | Reduction |
| --- | ---: | ---: | ---: |
| 48 kHz music | 4.2276 | 3.4585 | 18.19% |
| 48 kHz repeats | 3.6963 | 3.4433 | 6.84% |
| 96 kHz music | 7.3902 | 6.8879 | 6.80% |
| 96 kHz repeats | 8.1499 | 6.8441 | 16.02% |

All 12 average CPU/wall and p95 pairs improve. Four CPU/wall peak pairs regress,
including a 66.86% CPU-peak increase in the third 48-kHz music pair. All raw
traces, pairs, p95/max values and variation are retained. Affinity does not
isolate the host or establish certified worst-case behavior. The full core
continues to miss realtime deadlines.

Root authorized integration with the original cache-OFF path retained. This
receipt is the frozen pre-integration study; subsequent canonical/Reason checks
must carry their own source hashes. Canonical calibration, precision, topology
and defaults were unchanged during these measurements. The local equations
use nominal mass-normalized SI work, while source modes and gains remain
authored proxies rather than measured key/pedal mechanisms.

Evidence: [full-mechanism-cache.json](../Validation/full-mechanism-cache.json).

The independent review scoped the discrete-state claim: sampled fields are
`down`, `pending`, `hasLaunched`, RNG state, request count, launch count and
pending request ID. Internal `lastActive`/`releasedSinceLaunch` and the
`retiredBeforeSeparation`/`invalidObservations` statistics were not serialized.
The original v1 report is preserved, and the current report carries this prose
erratum without changing any numeric evidence or timing pair.
