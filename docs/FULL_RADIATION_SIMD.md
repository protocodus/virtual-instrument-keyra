# Hot-float stereo radiation SIMD experiment

The local-pointer SIMD candidate reduces measured median CPU cost by
**16.0–22.2%** across the three full-API cases, while every checked mechanical
state remains byte-identical. Its pressure observation changes slightly because
the float sum uses a different order. This original study retained a research
candidate and changed no canonical API, calibration or plugin backend. These numerical
differences do not establish inaudibility, SDK compatibility or realtime use.

A later guarded native API integration is documented in
`docs/FULL_BACKEND.md` and `Validation/full-pressure-integration.json`. That
integration checks compiler support, preserves the original fallback, and
validates the newer finite key-lift controller. Its performance option defaults
to OFF because the current measurements retain a repetition/pedal regression.
The original timing tables below
remain historical evidence for their recorded inputs; their 16–22% medians are
not a new measurement of the integrated build.

The integrated build's later three-pair countercheck preserves its mixed first
pass and reports **a 12.2% higher median CPU cost for 48 kHz repetition/pedal**.
Seven other case/rate medians improve by 10.1–24.5%; seven of 24 individual pairs
regress. Exact mechanical parity and pressure differences pass independently of
those timings. See the separate integration report for every trial, its two
coordinated quiet-window pairs, and the compiler/fallback policy. No universal
speedup, inaudibility, or supported real-time budget follows from either study.

The frozen experiments below precede the zero-gap repetition-controller fix
and canonical guarded pressure integration. Their copied headers and hashes
remain the exact measurement basis; do not apply these timings to a newer API
without remeasurement. The later integration is documented separately in
`FULL_BACKEND.md`.

This is distinct from the earlier rejected double-precision four-accumulator
and coefficient-layout studies. It uses the current hot-float `FullInstrument`,
including the corrected resting hammers, seeded strike/recovery controller,
quiet reciprocal mechanical sources and original control calibration. All
230 strings, 17,778 modes and 475 board modes remain present.

## Changes permitted by the experiment

Only `Modes::portImpulseRadiation()` and `Modes::radiation()` are transformed,
on private source copies under `out/full-radiation-simd`. The first still applies
exactly the original per-mode float impulse expression before observing that
updated mode. Port velocity, bridge/contact solves, oscillator rotations,
unison reductions and damping retain their original expressions and order.

Both arms compile with the same GCC 14.2 flags:

```text
-O3 -DNDEBUG -std=c++17 -ffp-contract=off
-fno-exceptions -fno-rtti -fno-builtin -fopenmp-simd
```

There is no global fast math, FMA, AVX-specific flag, OpenMP worker thread or
OpenMP runtime dependency. `ldd` results are retained for both executables.
The SDK compiler has not been exercised. A scalar path remains necessary even
if this observation-only change is later adopted on supporting compilers.

## Candidate 1: pragma alone — rejected

The first candidate adds `#pragma omp simd reduction(+:l,r)` before the two
existing float pressure loops. Every pressure sample, final float output and
all 45 complete mechanical checkpoint comparisons match the baseline exactly.
It is slower in all nine paired measurements; median CPU cost increases by
3.1% for music, 4.0% for repetition/pedal and 2.4% for dense strikes.

The compiler's initial “loop vectorized” message at the pragma line is
insufficient evidence that the working pressure body vectorizes. The full
diagnostic explicitly rejects the fused body at `yp[i] += ...`, and reports
vectorized reduction setup around it. The unchanged pressure samples are
consistent with no reassociated working reduction. This candidate is rejected.

## Candidate 2: local pointers and four-lane reduction — retained for research

The second candidate caches the mode count and local nonaliasing pointers for
`q`, `p`, port inverse and the four radiation coefficient arrays, then uses
`#pragma omp simd reduction(+:l,r) simdlen(4)`. The arrays are separate vector
allocations in the prepared model; the added nonaliasing assumptions match
their actual ownership. The per-mode impulse arithmetic is unchanged.

GCC now reports **16-byte vectorization at the actual body statements** of
both the fused update/pressure loop and the readonly pressure loop. The full
compiler diagnostics, generated sources and binaries are preserved. This
provides evidence of working reduction vectorization, rather than relying on
the presence of a directive.

Three paired trials run in AB, BA, AB order. Each executable runs the existing
48 kHz/64-frame music, repeated-key/pedal and dense-88/tail cases. Event dispatch
is included in callback timing. Preparation, checkpoint serialization and final
file writes are excluded from callback CPU sums. Both arms capture the same
two pre-high-pass doubles per frame for pressure analysis; that identical extra
memory work is part of their measured callback cost.

| Case | Baseline median CPU s/audio s | Candidate median | Median reduction | Individual paired speedups |
|---|---:|---:|---:|---|
| Music | 3.530 | 2.744 | 22.2% | 1.268×, 1.368×, 2.109× |
| Repetition/pedal | 3.404 | 2.769 | 18.7% | 1.218×, 1.309×, 1.577× |
| Dense 88/tail | 3.443 | 2.894 | 16.0% | 1.190×, 1.242×, 0.951× |

Eight of nine pairs improve. One dense pair regresses by 4.9%, and the third
trial contains large CPU spikes in both arms. No trial is discarded. The first
two pairs improve every case by 19–37%, which supports a useful candidate while
the larger third-pair gains do not establish a stable speedup. Shared-host
clock/cache/frequency effects are not identified by this experiment.

The median p95 callback CPU times across trials change from 5.784 to 4.042 ms
for music, 4.965 to 4.181 ms for repetitions and 4.973 to 4.102 ms for dense
strikes. These remain above the **1.333 ms** callback deadline. The raw reports
retain every callback and large outliers; neither average throughput nor these
short measurements certify a worst case or a supported Reason budget.

## Controlled pointer-only ablation — no consistent material gain

At review, a separate ablation keeps the second candidate's cached bound and
local pointers, removing only its two SIMD reduction pragmas. Both arms still
compile with the same `-fopenmp-simd` flag. This checks whether the portable
pointer changes alone explain the gain; it is not a search for another model.
The original two experiments and their freeze receipt remain preserved.

| Case | Baseline median CPU s/audio s | Pointer-only median | Median reduction | Individual paired speedups |
|---|---:|---:|---:|---|
| Music | 4.092 | 3.896 | 4.8% | 1.226×, 0.864×, 1.173× |
| Repetition/pedal | 3.497 | 3.502 | −0.14% | 1.068×, 0.985×, 0.855× |
| Dense 88/tail | 3.592 | 3.581 | 0.29% | 1.006×, 1.082×, 0.946× |

Pressure and final output bytes remain identical, as do all 45 mechanical
checkpoints. Compiler reports retain automatic loop vectorization, with the
strict summation producing the original output. Mixed paired results and the
negligible repetition/dense medians do not demonstrate a consistent material
gain. Do not integrate the pointer-only change on this evidence. The stronger
SIMD result therefore remains conditional on the local reassociated reduction
and compiler support; it is not a portable exact-output optimization result.

## Mechanical state and observation differences

Each case writes full diagnostic snapshots after frames 64, 512, 4096, 8192 and
its final frame, in all three trials. Every candidate/baseline snapshot is
compared as bytes. The 45 comparisons per candidate cover:

- Every string's modal `q`, `p`, damping values, bridge velocity and force.
- Every board mode's `q`, `p` and force.
- Every hammer's position, velocity, age, hardness, contact history and damper
  state; pedal and solver counters.
- Every key's controller/recovery/pending/RNG state and every mechanical source
  mode's position and velocity.

Fields are serialized individually, avoiding struct padding. Observer caches
and output high-pass/filter state are excluded because they are allowed to
follow the changed pressure. Copied headers expose private members solely for
this diagnostic; storage and layout are unchanged. All **135** comparisons
across the two candidates and controlled ablation pass, with no solver fault or
unsafe launch.

For the retained pointer candidate, three repeated runs reproduce each arm's
audio exactly. Its pre-high-pass float64 pressure differences are:

| Case | Null RMS relative to baseline | Maximum absolute sample difference |
|---|---:|---:|
| Music | −132.20 dB | 7.15e−7 |
| Repetition/pedal | −138.95 dB | 3.58e−7 |
| Dense 88/tail | −127.51 dB | 2.11e−6 |

Final float32 output nulls are −132.09, −138.55 and −127.44 dB respectively.
The largest measured broad-band power change is 0.00023 dB; pre-high-pass
stereo correlation changes by at most 1.19e−8 and channel balance by at most
1.09e−7 dB across the reported attack/sustain windows. These are short signal
comparisons, not perceptual thresholds. There is no listening or inaudibility
claim.

All analysis arithmetic promotes float32 output samples to float64. Original
reports are preserved alongside a receipt for that analysis correction; the
DSP outputs and timings were reused unchanged. Exact-equality cases have an
explicit equality flag; their −3000 dB metric value is a finite serialization
floor for a zero null, not a measured noise level.

## Evidence and reproduction

`Validation/full-radiation-simd.json` contains both candidate reports and the
controlled ablation, every
mechanical checkpoint hash, sound differences, timing summaries, vectorization
evidence, all regressions and the explicit decision. Raw traces, pressure/audio,
generated source/header/tool snapshots and per-trial state files are retained
under `out/full-radiation-simd`. Inputs are hashed before compilation and after
each run; any change aborts the experiment. The canonical source and preserved
`Research/` tree remain unchanged.

The original transformation expects the unguarded source hashes recorded in its
report. Reproduce it from that matching source snapshot or checkout on Linux
with GCC, NumPy and SciPy, using new output directories. Do not apply the original
pointer transformation again to the now-guarded API header:

```sh
OPENBLAS_NUM_THREADS=1 python3 tools/probe_full_radiation_simd.py \
  --candidate pragma --output out/radiation-pragma-recheck \
  --report out/radiation-pragma-recheck/report.json

OPENBLAS_NUM_THREADS=1 python3 tools/probe_full_radiation_simd.py \
  --candidate pointer --output out/radiation-pointer-recheck \
  --report out/radiation-pointer-recheck/report.json

OPENBLAS_NUM_THREADS=1 python3 tools/probe_full_radiation_simd.py \
  --candidate pointer-control --output out/radiation-pointer-control-recheck \
  --report out/radiation-pointer-control-recheck/report.json
```

The tool writes one complete candidate/control report per invocation; the
retained combined report records the subsequent review and controlled ablation.
Runtime measurements will vary. This original study changed no default backend.
The later integration adds compiler/fallback selection; its separate report
retains all current measurements and does not establish inaudibility or a
supported real-time budget.
