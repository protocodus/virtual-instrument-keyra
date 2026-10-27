# Realtime feasibility of the original physical model

Realtime is a reasonable development target for a model built from the original.
The unchanged full solver reaching it through ordinary code cleanup remains
unproven. Current measurements require substantial algorithmic and implementation
work; they do not justify a release date or a claim of Reason readiness.

The user explicitly allows precision/quality reductions when hardly audible.
That broadens the feasible design space beyond exact-output optimization.
Commercial physical piano instruments demonstrate the practicality of the
general goal; the timings below describe this implementation. Prioritize the
whole instrument's audible behaviors, including inexpensive state-linked action
and release sounds, over extreme numerical precision in an isolated subsystem.

## Measured gap

The full model retains 88 keys, 230 strings, 17,778 string modes, 475 board modes,
nonlinear hammer contact and reciprocal coupling. The interleaved native probe
renders 0.35 seconds at 48 kHz. Its baseline median is 2.100 process CPU seconds;
the passing loop-fusion version takes 2.003 seconds. This is approximately
6.00 and 5.72 CPU seconds per second of audio respectively. Preparation is outside
that timed region. Shared-host variability and the short workload limit how
precisely these figures predict sustained performance.

At 48 kHz, a 64-frame callback has 1.333 ms available. The optimized work rate
corresponds to roughly 7.63 ms per callback **on average**, before adapter overhead.
This conversion is not a measured callback maximum. Breaking even requires about
5.7 times further speedup. A provisional 25% single-core budget would require
about 23 times further speedup; that budget is an engineering assumption for
headroom, not a user requirement or established Reason limit.

The scalar/no-builtin approximation is slower: its passing loop-fusion median
is 2.403 CPU seconds for the same 0.35 seconds of audio, or 6.86 times realtime.
Compiler settings change the results substantially. A native SIMD result cannot
be presented as Jukebox compiler performance.

Source, flags, per-run ranges and limitations are in
[reference-optimization.md](../Validation/reference-optimization.md). The
[working full renderer](../src/full_reference/README.md) passes exact audio,
stem and final-double-state checks for the exercised native/scalar cases.

## Subsequent measured progress

The portable grouped-unison layout adds modest native gains and larger scalar
gains while preserving the exact tested sound/state. In the separate AVX2
experiment, grouping is 1.41 times as fast as that run's original, still costing
about 4.58 CPU seconds per audio second. SIMD support in Reason remains untested.

The [full float-kernel candidate](PRECISION_FINDINGS.md) is 1.67 times as fast as
the grouped double control on repeated 48 kHz C4/music comparisons. All physical
operators and modes remain, with measured rounding and extra numerical loss.
Its music case costs about 3.33 CPU seconds per audio second. It is retained for
listening and further validation; it is neither realtime nor an established
inaudible substitution. Do not multiply these speedups across different builds
and workloads. Two partial float conversions and two radiation-layout/sum
experiments failed to provide useful speed gains and were rejected.

The [mechanism/body prototype](MECHANISM_NETWORK.md) illustrates a separate
budget: one three-mode key/pedal component plus a minimal dummy body takes
about 0.0039 CPU seconds for three audio seconds here (roughly 0.13% of one core).
This does not include original-piano or full-adapter cost. Broad behavior can
be inexpensive; the dense tonal network remains the present bottleneck.

## Engineering judgment and priorities

The [free/unison row-fusion study](FREE_UNISON_FUSION.md) measured the
full API with pressure SIMD off, fast contact and mechanism cache on.
Its guarded row-vectorized implementation reduces median CPU by 7.04–11.66%
across all six 48/96 kHz workload groups, with exact pressure, output and common
state comparisons. Every paired timing trial improves. At 48 kHz the measured
candidate still costs 2.81–2.94 CPU seconds per audio second and every measured
callback misses its wall deadline. This is incremental progress, not realtime.
The scalar fused version was slower and is rejected; unsupported/scalar builds
retain the original complete schedule. Do not multiply these gains with the
earlier studies' percentages or apply them to the SDK compiler.

The subsequent [current pressure study](PRESSURE_CURRENT.md) measures a further
21.96–25.05% reduction against that fused backend, with improved p95s in all six
groups. Physical snapshots remain exact; pressure/output differ within fixed
numerical limits, including ten isolated soft/hard register cases. The measured
48 kHz path costs 2.15–2.29 CPU seconds per audio second and still misses every
measured deadline. It supplies no new SDK performance evidence. Its current
source and complete paired results must be used rather than multiplying prior
speedup percentages.

The first layout experiments preserve the entire physical model. They target
repeated modal scans, unison pointer traffic and radiation observation. Useful
gains are worth retaining, but a few percent does not close the measured gap.
Do not add percentage savings from different compilers or compare different
sample rates as if they were one optimization result.

Larger gains may require a different numerical implementation of the same
physical interactions: more efficient modal/coupling kernels, suitable block
methods, or passive reduced representations of weakly observable states.
These are hypotheses to test. Any approximation needs transfer, energy,
attack/decay, pedal, stereo and musical listening evidence against the full
physical version and recordings. A missing interaction cannot be justified by
an isolated-note power score.

Several independent voices are not a substitute for the coupled instrument:
unstruck strings participate in sympathetic behavior. Sleeping or reducing those
states requires a measured error policy. Audio callbacks also cannot rely on
unbounded worker synchronization or all CPU cores being available to one device.
GPU, SIMD and multicore support must be established for the actual target before
they enter the performance budget.

Keep acoustic development open. The original already has attack/envelope and
other recording mismatches; it is the starting point, not the acoustic endpoint.
Retain exact-output controls for reference comparisons. Precision and numerical
approximations use explicit error/stability measurements and musical listening;
they need not preserve bytes. Intentional realism changes are evaluated against
recordings and listening feedback. A deep audio null alone does not establish
perceptual parity across all playing conditions.

Before treating realtime as demonstrated, run sustained callback workloads with
dense pedal, retriggers, release tails and multiple instances; report p95,
maximum and misses as well as mean cost. Then repeat under the licensed Jukebox
toolchain and actual Reason host. Neither is available in this Linux workspace.

## Published scope and current representation studies

[Van Walstijn, Bhanuprakash and Chatziioannou, DAFx23](https://www.dafx.de/paper-archive/2023/DAFx23_paper_18.pdf)
demonstrate a non-iterative energy-quadratized hammer/string scheme with
time-varying parameters. Their Figure 8 reports a realtime factor below 0.75
for at least 32-frame blocks and up to 1,000 string modes in MATLAB on an
i7-6700. That is a single hammer/string experiment. Its timing is useful
context for efficient physical synthesis, but does not cover Keyra's complete
sympathetic network, stereo radiation, action sources or host callback budget.
Keyra's present discrete-gradient contact solver uses a different method.

The [coupled C2/C4 waveguide study](COUPLED_WAVEGUIDE.md) provides a second
implementation of persistent nonlinear contact and reciprocal soundboard
transfer, including an optional positive damper load. Its energy checks do not
establish equivalent sound. Efficient calibrated string radiation, polarization,
unison structure, high-register dispersion and a full-keyboard workload still
need evidence before it can replace the complete modal instrument.

The [radiation readout study](WAVEGUIDE_RADIATION.md) tests compact causal filters
without inserting new acoustic recordings or altering mechanics. Its tested
filters leave substantial stereo-observation error even after separating small
pole-frequency shifts from phase decorrelation. That result rejects those
bounded observers as sound-equivalent replacements; it neither rejects all
waveguide methods nor establishes an audibility threshold. Spatial wavefield
readouts remain a separate hypothesis.
