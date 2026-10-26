# Mechanical port-velocity reduction study

Retain this as a research candidate. It reduces measured median CPU cost by
**5.6–13.2%** relative to the explicitly pressure-enabled control and passes the
predefined energy/stability gates. However, dense-playing p95 callback CPU time
regresses at both sample rates. No canonical change, deadline improvement,
inaudibility or SDK/Reason qualification is established.

Both arms enable the experimental pressure SIMD option. The product's pressure
default is **off**. These results describe an additional change in that selected
experimental chain; they must not be added to the earlier pressure percentages
or presented as a comparison with the current default backend.

## Exact scope and frozen basis

Only the candidate's `Modes::portVelocity()` changes. It caches the mode count
and nonaliasing pointers to the existing float `portOmega` and `p` arrays, then
uses a four-lane SIMD reduction. The sum supplies a mechanical bridge velocity,
so reassociation can change subsequent forces, string/board states and contact.
Unlike pressure-only SIMD, mechanical byte parity is neither expected nor used
as a conservation argument.

The pressure observation, hammer displacement/contact law, oscillator updates,
unison network, three-port bridge solve, damping and controller remain the same
between arms. All 230 strings, 17,778 modes and 475 board modes are retained,
including unstruck sympathetic strings. The canonical API is not edited.

The control uses the guarded pressure integration and finite key-lift controller
from the source snapshot whose prepared-model SHA256 is
`5c8c92f8a761b46a66f3823765f6348ab0c08b74457d7efc062f0941ab07faf8`.
All ten original inputs are preserved under
`out/full-port-reduction/input-snapshot/`, with a final live-input guard and
receipt in `source-freeze.json`. Later contact/API changes have a different
basis and are not covered by these timings.

Both arms compile with GCC 14.2, strict floating-point contraction disabled,
no exceptions/RTTI/builtins, `-fopenmp-simd`, and
`KEYRA_FULL_PRESSURE_SIMD=1`. The candidate alone enables the copied
`KEYRA_FULL_PORT_SIMD` branch. That branch has a compiler/macro guard and the
original scalar expression as fallback. Global fast math and FMA are disabled;
no OpenMP runtime or worker thread is linked. SDK/compiler/fallback behavior is
not validated by this Linux experiment.

GCC reports 16-byte vectorization at the actual candidate velocity-reduction
body, separately from reduction setup. The full vectorization diagnostics and
all generated sources/binaries are retained. All 90 candidate/control
mechanical snapshots differ, confirming that this is a changed mechanical
computation rather than an observation-only edit.

## Independent energy and stability checks

The energy audit promotes every stored value to double **before** any product,
including modal squares and physical hammer displacement. It independently
sums string/board modal energy and active hammer kinetic/contact energy. It
does not call the model's float reductions or infer conservation from output
hashes. Physical bridge velocities use double products of the stored `b`,
`omega` and `p`, independent of both tested float sums.

| Audit per arm | Coverage | Predefined gate |
|---|---|---|
| Bridge-only stress | 36 cases: 48/96 kHz, resistance scale 0.01/1/100, three amplitude scales, random/cancelling port states; 500 steps each | Step increase ≤5e−7 of initial energy; total growth ≤5e−6 |
| Isolated contact | A0/C2/C4/C6/C8, velocities 40/127, 48/96 kHz | Relative energy error ≤5e−5; contact residual <1e−8 |
| Isolated free oscillators | Five frequencies from 27.5 to 12,500 Hz, position/velocity starts, 48/96 kHz; ten seconds | Growth ≤5e−6 |
| Whole coupled unforced network | All strings, unisons and board, 48/96 kHz; eight seconds | Growth ≤1e−4; finite pressure each frame and nonnegative finite energy at 64-frame checks |

All gates pass for both arms. The candidate's largest bridge-only positive
energy step is 4.74e−11 of initial energy. Its maximum overall bridge energy
ratio is 1.000000000047; the control reaches 1.000000000441. These tiny positive
changes are visible and are **not exact passivity**.

The independent bridge work ledger compares the energy change with positive
resistance times squared midpoint relative port velocity. Its largest residual
is 2.31e−9 of initial energy for the candidate, versus 2.29e−9 for the control.
Stored float coefficients, nonreciprocal rounding of coefficient products and
rounded state updates already limit the exact-arithmetic midpoint proof.
This is a bounded empirical near-passivity/stability result, not a new formal
conservation proof.

The maximum port-sum error divided by the sum of absolute physical products is
1.81e−7 for the candidate and 3.16e−7 for the control across those stress cases.
That normalization keeps cancelling ports visible without dividing by an
almost-zero net velocity. It does not uniquely identify which float summation
is most accurate for every piano state.

The isolated-contact results match between arms because that audit disables
the bridge: maximum relative energy drift is 3.57e−5 and maximum contact
residual is 9.07e−13. It checks that the local compiler change has not altered
the isolated contact path. In the actual coupled API performances, the largest
contact residual is 1.45e−11; no solver fault or unsafe launch occurs.

Ten-second free tests reach at most 1.000000316 times their initial energy.
The eight-second unforced coupled network never exceeds its initial energy at
the sampled checks. Candidate final ratios are 0.26925589 at 48 kHz and
0.26285341 at 96 kHz, versus 0.26925584 and 0.26285350 for the control. Intrinsic
string/damper loss is disabled in this audit; positive unison/body/bridge and
numerical losses remain. No MIDI launch, mechanism trigger or other external
work is added during the decay.

## Actual API callbacks and regressions

The existing deterministic music, repeated-key/pedal and dense-88/tail cases
run in AB, BA, AB order at both rates. Callback timing includes events and
processing with identical pressure capture, and excludes preparation,
checkpoint serialization and final file writes. Every trial is retained.

| Rate | Case | Control median CPU s/audio s | Candidate median | Median CPU reduction |
|---|---|---:|---:|---:|
| 48 kHz | Music | 2.993 | 2.599 | 13.2% |
| 48 kHz | Repetition/pedal | 2.939 | 2.589 | 11.9% |
| 48 kHz | Dense 88/tail | 2.888 | 2.725 | 5.6% |
| 96 kHz | Music | 5.643 | 5.119 | 9.3% |
| 96 kHz | Repetition/pedal | 5.603 | 5.035 | 10.1% |
| 96 kHz | Dense 88/tail | 5.935 | 5.297 | 10.7% |

Fifteen of eighteen pairs improve. The losing pairs are 48 kHz music trial 1,
96 kHz repetition trial 0 and 96 kHz dense trial 1. Their candidate CPU costs
increase by approximately 10.5%, 8.7% and 8.0% respectively. They are not
discarded or assigned an unproven cause.

Dense-case median p95 callback CPU **regresses** from 4.252 to 4.730 ms at
48 kHz and from 4.711 to 5.019 ms at 96 kHz. Larger isolated maxima are also
retained in the raw traces. These remain far above the 64-frame deadlines of
1.333 and 0.667 ms. The candidate provides useful throughput evidence; it does
not demonstrate safer callback deadlines. A workspace quiet window reduces
our own concurrent work, but does not identify every shared-host timing effect.

The controller admits the same 5, 10 and 88 strikes in every arm/rate/trial.
Each arm reproduces its own pressure and output bytes across its three runs,
despite differing from the other arm. Seeded repetition and mechanical state
remain deterministic within the measured configuration.

## Sound and tuning comparisons

| Rate | Case | Pre-high-pass pressure null RMS relative to control |
|---|---|---:|
| 48 kHz | Music | −117.70 dB |
| 48 kHz | Repetition/pedal | −110.64 dB |
| 48 kHz | Dense 88/tail | −113.38 dB |
| 96 kHz | Music | −114.54 dB |
| 96 kHz | Repetition/pedal | −109.27 dB |
| 96 kHz | Dense 88/tail | −110.50 dB |

Maximum pressure-sample difference is 1.34e−5. The largest measured broad-band
power change is 0.00157 dB, attack/sustain stereo correlation changes by at most
3.43e−7, and channel balance changes by at most 2.43e−6 dB. The causal 5 ms RMS
10–90% attack-rise diagnostic is unchanged in all six comparisons. This is
neither a full attack-structure score nor a listening/inaudibility result.

The strongest baseline-resolved spectral peaks are tracked to their nearest
candidate local maxima using an eightfold FFT grid and interpolation. All 120
peaks match; maximum measured shift is 7.3e−5 cents. Chord and dense peaks are
not uniquely assigned string fundamentals. The free string coefficients are
unchanged, while the observed coupled spectrum is measured rather than assumed
unchanged.

The original peak matcher incorrectly chose a stronger neighboring bin even
for identical inputs. Its results are explicitly invalidated and preserved in
the report. The corrected analysis passes identity checks on all six actual
signals, and recovers a synthetic +1 cent shift as 1.00035 cents. A separate
receipt records the analysis correction; no DSP output or timing was rerun.

## Remaining bridge cost

A short control-only stage profile preserves every pressure/output byte and
every mechanical checkpoint relative to the uninstrumented control. With
pressure SIMD enabled, approximately 41–44% of measured bridge time is board
velocity plus string-port/force assembly, 50–54% is impulse plus fused pressure,
less than 1% is the three-dimensional junction solve, and 4.0–4.3% is board
impulse update. These are clock-instrumented stage shares, not zero-overhead
whole-instrument percentages. The actual working port loop is a useful target,
but it is only part of the remaining bridge cost.

The separate pressure integration's 48 kHz repetition regression remains
unresolved. This study does not infer a denormal or host-noise cause from
output/state classification. Counting actual SIMD partial accumulators needs a
separate validated instrumentation path; no FTZ/DAZ or flush policy is adopted.

## Evidence and reproduction

`Validation/full-port-reduction.json` contains the complete reviewed result,
physics reports, every paired regression, sound/tuning diagnostics, compiled
source/binary hashes and the source-freeze receipt. Raw callback traces,
pressure/output files, state checkpoints, generated physics harnesses and
compiler diagnostics remain under `out/full-port-reduction`.

The original input snapshot reproduces this basis after the live API changes.
From the repository root on Linux with GCC, NumPy and SciPy:

```sh
OPENBLAS_NUM_THREADS=1 python3 tools/probe_full_port_reduction.py \
  --input-root out/full-port-reduction/input-snapshot \
  --output out/full-port-reduction-recheck \
  --report out/full-port-reduction-recheck/report.json
```

Use an empty output directory. `--prepare-only`, then `--run-prepared
--physics-only`, and finally `--run-prepared --reuse-physics` can separate
compilation, long numerical checks and a quiet timing window. Use the same
input-root selection at every stage. Inputs are rehashed throughout; changed
source or driver versions abort reuse. The preserved `Research/` tree is
unchanged, and no recording or evaluation file is opened by this study.
