# Pressure SIMD on the current fused backend

**The current pressure observer passes numerical and native timing guards,
reducing median CPU by 21.96–25.05% against the current fused baseline.** The
register checks also pass. The fresh supported-native OriginalControl default
is now ON, with separately recorded integration and production-render checks.

This changes the order of existing float L/R pressure reductions. Both arms
keep free/unison SIMD, fast contact and mechanism cache enabled, using the
current OriginalControl profile 0. Source, coefficients, controls, event timing
and physical update expressions are unchanged. Output samples intentionally
differ slightly. Numerical agreement does not establish inaudibility, pitch
accuracy or recording realism.

## Physical and output checks

The fixed correctness matrix covers 44.1/48/88.2/96 kHz with music, repeated
notes/pedal, dense 88-key tails and silence/reset. Each arm advances 574,704
frames. All **80 deep physical/coefficient snapshot pairs** are exact. Only
three observer memories are excluded: `String.cachedRadiation`, `Impl.previous`
and `Impl.highpass`. All string/board coordinates, damping, forces/velocities,
hammers, controller/RNG, mechanisms/ledgers, body cache and `lastStems` remain
exact requirements. These are checkpoints, not every internal state at every
frame.

All 32 raw-float64/final-float32 payload comparisons pass bounds frozen before
model execution. The comparator uses whole signals and fixed 0–50 ms,
50–200 ms and 200 ms–end windows, with no level, delay or onset matching:

- Relative null RMS at most −110 dB where the baseline window is powered;
  maximum absolute error at most `1e-4 * (1 + baseline peak)`.
- L/R and powered mono-energy shifts at most .001 dB; nondegenerate Pearson
  correlation shift at most `1e-5`.
- Seven symmetric-Hann spectral bands cover DC through Nyquist at every rate.
  Band-level shift is at most .01 dB where baseline band power reaches
  `1e-10` of its total spectrum. No mean removal or detrending occurs.

Masks depend only on the OFF baseline. Weak and degenerate observations retain
their powers, absolute errors, nulls, masks and statuses; undefined ratios are
not assigned fake finite dB values. Eleven manufactured metric checks precede
the model matrix.

The worst core window null is **−126.327 dB**, maximum absolute sample error
`2.511e-6`, and maximum powered-band shift **.000535 dB**. There are 200 powered
band gates and 24 retained weak-band diagnostics. The largest defined weak-band
shift is −.116531 dB in the 19–48 kHz band below the frozen power floor.

Ten additional one-second 48 kHz model diagnostics cover A0/C2/C4/C6/C8 at
MIDI velocities 14 and 124, with humanization .65, mechanisms off, pedal .75,
note-on .05 s and note-off .65 s. All ten final physical-state pairs and twenty
observer comparisons pass the same unchanged recipe. Worst window null is
**−121.967 dB** and powered-band shift **.001718 dB**. All 28 weak bands remain
visible, including a −3.877 dB diagnostic whose baseline power is −146.099 dB
relative to total. These fixtures do not decode recordings or establish unseen
piano generalization.

## Paired native timing

One quiet-window matrix retains three pairs in AB/BA/AB order at 48 and 96 kHz,
using the same actual API event/frame schedules as the fused-backend study.
Separate timed executables contain no pressure capture or snapshots. Callback
CPU covers dispatch plus process; prepare, file writes and reporting are
excluded. No trial or outlier is discarded.

| Rate / case | Median CPU/audio, OFF → ON | CPU reduction | Median p95 CPU, ms, OFF → ON |
|---|---:|---:|---:|
| 48 kHz music | 2.874 → 2.154 | 25.05% | 4.177 → 3.444 |
| 48 kHz repeated notes / pedal | 2.857 → 2.172 | 23.95% | 4.242 → 3.376 |
| 48 kHz dense 88-key tail | 2.947 → 2.292 | 22.24% | 4.498 → 3.645 |
| 96 kHz music | 5.664 → 4.413 | 22.09% | 4.224 → 3.394 |
| 96 kHz repeated notes / pedal | 5.838 → 4.537 | 22.30% | 4.462 → 3.414 |
| 96 kHz dense 88-key tail | 5.993 → 4.677 | 21.96% | 4.659 → 3.767 |

The unchanged policy requires at least 5% lower median CPU in every group and
no more than 5% increase in any median-of-three p95. All six groups pass both
requirements, and all 18 paired trials are faster. The same frozen numerical
recipe also passes on all 18 performance float32 output pairs, with worst
window null −126.885 dB. Three empty late windows from the short 96 kHz dense
fixture remain explicitly empty; no tail is fabricated.

All 14,400 callback records, maxima and misses remain available. Every callback
still misses its wall deadline; the candidate includes a retained 49.76 ms
maximum CPU outlier. A median/p95 pass does not certify worst-case or realtime
behavior. The new 48 kHz medians still exceed two CPU seconds per audio second
on this shared Linux host. Do not multiply these gains by the earlier
free/unison percentage as if a combined improvement had been measured in one
paired experiment.

## Prior result and integration scope

The earlier integrated pressure study remains negative evidence: its 48 kHz
repetition/pedal median regresses **12.16%**, with seven regressive individual
pairs among 24. That pre-fusion result motivated the former default OFF and is
preserved in `Validation/full-pressure-integration.json`. It is not replaced by
this current baseline or relabeled as fresh validation.

The pre-study baseline uses pressure OFF. Fresh supported-native
OriginalControl builds now default ON; existing cached OFF values remain OFF.
Pressure opt-out, scalar/SDK and unsupported builds use scalar pressure.
Fresh confidence-profile builds default OFF, with explicit ON retained as an
experimental opt-in outside this study's qualification. Free/unison opt-out is
independent of pressure opt-out; the measured gains here use free/unison ON.

Canonical native tests passed (3), sanitizer tests passed (2), and Reason
mock-host/contract tests passed (12). Seven configure-only cases verify fourteen
effective pressure/free target settings, including cache reuse and conflicting
parent macros. An actual CMake production CLI then renders the same ten register
fixtures: every float32 payload matches its qualified ON output, and the same
frozen numerical recipe passes against OFF. The archive retains the native
comparison, actual interleaved payload hashes and separately encoded planar
reference-file identities. This adds production-path coverage to the same
fixtures rather than new recording evidence.

The repository subsequently moved research under `Experiments/`. The
[layout integration receipt](../Validation/full-pressure-layout.json) verifies
all ten runtime inputs against the measured source and repeats the three native
and twelve Reason mock tests through the new paths. All seven rebuilt native
and Reason executables, including the qualified production renderer, are
byte-identical to their pre-move builds. Sanitizers and performance measurements
were not repeated for this directory move. The product build is separate.

Actual Reason SDK/Recon, production readiness and the price-value goal remain
unqualified.

The [validation summary](../Validation/full-pressure-current.json) records the
current integration status. The [compact archive](../tools/experiments/pressure_current/README.md)
retains frozen source, numerical metrics, every timing trial, register checks,
authorizations and reviews. Its standard-library checker recomputes stored
gate and timing arithmetic without decoding omitted payloads or running models.
