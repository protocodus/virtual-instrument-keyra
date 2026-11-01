# Calibration follow-ups and runtime diagnosis — 2026-11-01

Three additional experiments produced useful negative results. None changes
the accepted 0.4.2 DSP or its measured numeric tables. The
[compact evidence](calibration-followups-2026-11-01.json) retains paired
recording summaries, every tolerance regression, velocity-pilot aggregates,
invariants and hashes of the complete local reports.

## Retaining quiet observations in truncated recordings

The candidate retains quiet held frames from recordings cut off before the
tone has decayed, preserving the original floor estimator and weighting
formula. Its 27 Kawai training anchors contain 18 affected anchors and 207
flagged partial/layer observations. Unflagged partials remain identical to
the paired refit. Synthetic controls improve, and the original noise floors
are unchanged, but this does not establish an improvement after export and
native playback.

All 933 train/dev recordings and 1,584 normal-playing keyboard cases were
evaluated. Compared with accepted 0.4.2, Kawai has **23 paired note/metric
regressions** beyond the existing tolerances. Against the regenerated paired
baseline it has **21**. An additional apparent sustain regression in the
legacy averages is a coverage change: `n80v2` becomes measurable where it
previously had no sustain score. The [common-support correction](benchmark-common-support-2026-11-01.md)
separates that event; the real regressions still reject the candidate.

For `n80v2`, envelope agreement improves by about 8.56 dB while attack, early
spectrum, noise and rise metrics worsen. Its anomalously loud modeled sustain
is reduced, bringing its required level-match gain closer to the other
recorded layers. That mixed outcome needs a fit-to-runtime stage diagnosis,
not another gain adjustment or a favorable aggregate claim.

Kawai's 78→79 early-level gap at velocity 32 improves from −8.237 to −3.270 dB,
but a +8.210 dB gap remains at 83→84. All 1,320 keyboard waveforms from the
other five pianos are bit-identical. Their recording scores also remain
unchanged apart from four grand metrics differing by at most 1.25e−14.
All keyboard cases retain exact gain-halving behavior and deterministic
repeat checks. The isolated candidate therefore neither solves Kawai's
whole-range consistency nor supplies an all-piano sound improvement.

Reproducibility is a separate limitation. Regenerating the baseline with the
historically recorded package versions does not recreate its shipping header.
Those versions identify the generation environment; the old raw-fit cache
does not pin its NumPy/SciPy/BLAS environment. The bounded native probe finds
material baseline drift at notes 64 and 96, reaching −3.382 dB in one late
window. The paired candidate comparison isolates the observation change,
while actual shipping remains the acceptance baseline. No package search or
development-set tuning was used to select a favorable reconstruction.

Complete fits, synthetic controls, source snapshots, three-way recording
comparisons and keyboard reports remain under
`out/realism/censor-observations/`. The candidate stays out of production.

## Transferring velocity curvature between pianos

The [Steinway reference](../research/bitklavier-house-ortf-2026-11-01.md) enabled
a dense, fixed training pilot at MIDI 36/69/96: 12 permitted Salamander layers
and 16 bitKlavier layers per pitch. Salamander's permanent dev layers remain
excluded. Source pins were frozen before extraction; the reduced measurement
operator reproduces an existing Salamander cache exactly. No dev or sealed
recordings were opened.

The candidate transfers only the other piano's normalized spectral-shape
curvature. It preserves target endpoints exactly and the target-local baseline
level curve within 1.42e−14 dB. Despite those constraints, shape error worsens
in all eight instrument/gap/window groups, including energy-weighted scoring.
It worsens 187 of 276 case-window predictions and 21 of 24 note/group means.
The worst case grows from 1.125 to 4.220 dB shape error, with energy-weighted
error also worsening from 0.583 to 1.970 dB.

No target-specific strength or selective note gate was fitted afterwards.
Target-local log-power interpolation remains the baseline. A predeclared
power-linear control also worsens the primary shape metric in all eight
groups, although some Salamander level/energy-weighted metrics improve; those
tradeoffs remain in the numeric report. Three pitches cannot establish a
universal interpolation law. Complete predictions and exposure masks are
under `out/realism/masked-velocity/`.

## Donor uncertainty for unobserved tails

Masked training tails from Yamaha, Helsinki and Mom's test donor residual
distributions while excluding the complete target instrument. A short local
trend predicts coherent beating poorly. Broader-prefix donor corrections help
some targets but worsen Kawai and New York; a proposed upper quantile fails
on fundamentals even when its aggregate coverage looks adequate.

These quantiles are conditioned on the future still being measurable, and
the available cache windows end by 3.5 seconds. They cannot justify an
automatic clamp or a universal prediction for a genuinely truncated future.
No such rule is adopted. The complete assessment and all predictions remain
under `out/realism/tail-prior/`.

## Fit, export and runtime diagnosis

The following bounded diagnoses retain the accepted DSP and numeric tables.
They identify different errors; combining their changes would obscure their
causes. Better raw fitting alone does not qualify a candidate for the model.

### Stereo compression and the played energy denominator

On fifteen Helsinki TRAIN layers at notes 82/84/86, the existing per-lane SVD
minimizes coefficient error rather than error through the nonorthogonal
runtime basis. A fixed-pole alternating least-squares diagnostic reduces that
objective, but its exported native sound has mixed attack and tail results.
In particular, one optimized basis replaces a slow component with a prompt
component and loses the quiet tail. No additional pole was introduced.

A separate correction changes only the fundamental's energy-gain denominator
to include the actual contact cap, onset floor and discrete smoothing. Its
independent sampled-wave check agrees within 3.19e−6 dB, and all 30 legacy
native controls are bit-identical. At note 86, original-pole ALS mean errors
improve from 2.037→1.706 dB early, 0.602→0.309 dB middle, 1.188→1.019 dB in
the first late window, and 0.936→0.858 dB in the second. Notes 82/84 barely
change. The correction accounts for only 0.28–0.41 dB of the earlier energy
gain; the remaining 2.26–3.96 dB compensates fit residual energy.

Against shipping, this corrected candidate still worsens 26 of 60 isolated
case/window errors; its worst first-late-window regression adds 1.048 dB
absolute error at 86/v51, with every scored frame clearly above the floor.
These are isolated fundamental results, not full-piano recording scores.
No all-piano refit follows. Complete results, unchanged-field controls and
regressions are in `out/realism/runtime-fit-review/runtime-energy/`.

### A loud-layer regression contaminates quiet body excitation

Tracing Kawai TRAIN note 80 establishes that the quiet-frame candidate's
fundamental correction survives export and native rendering. The new problem
is not simply a correction being lost later: reducing the previously excessive
fundamental exposes an already excessive low-frequency body component.

The body's amplitude-weighted line lets loud layers dominate quiet layers.
For the 206.681 Hz mode, projected levels at layer coordinates 27/69/95/117 are
approximately −91.77/−87.21/−44.79/−54.20 dB, while the exported line gives
−49.68/−48.65/−47.61/−47.31 dB. Shipping and regenerated line slopes are very
close, so this is a pre-existing representation error rather than merely
refit drift. The fixed-basis conditioning is benign; removing the existing
ridge changes the mode's raw amplitude by only 0.04–0.11 dB.

Two bounded alternatives affect only the five exactly reconstructed
150–250 Hz modes. A constrained line cannot retain all four observed layer
levels. Its constraint uses total observed band power as a conditional bound,
not an identified body-only target or statistical confidence bound. Per-layer
projected magnitudes remove the large quiet excess and
improve the v95 body band, but lose another 2.39 dB at v117. Neither is a
complete accepted correction. The unchanged full-engine scorer also reports
mixed rise and early-spectrum results even where soft-layer noise and
envelope errors improve substantially. No dev-derived gain enters fitting.

The loud-layer loss has an upstream cause. In the regenerated-baseline trace,
150–250 Hz over 50–300 ms after contact, all in source units, the v117 recorded
band is −54.925 dB; the independent fixed-pole fit yields −59.246 dB, shared-pickup
compression −61.942 dB, and common phase −61.773 dB. Waveform variance
explained falls from 38.60% to 12.93% to 9.97%. Fundamental leakage is
negligible. Some residual energy near 165 Hz has no corresponding pole;
it is unassigned recorded energy, not a proven missing body resonance that
a gain should fill.

Mode 206's v117 stereo projection alone loses 7.20 dB of coefficient power.
Per-layer scalar complex excitation can preserve the projected endpoints
with the existing state count. Restoring arbitrary independent stereo
coefficients would require an additional complex state per body pole, even
if the resonant frequencies stay the same. Evidence and the explicitly
superseded wider-mode diagnostic remain under
`out/realism/censor-observations/body-trace/`.

### Colour normalization reintroduces pitch-boundary level steps

The existing pitch interpolation normalizes coherent four-lane energy over
50–750 ms. A later colour normalizer instead counts each lane independently
to infinity. When the selected phase/pickup pattern changes at an interval's
midpoint, that second calculation can change the whole note's gain despite
unchanged coherent energy before normalization.

The fixed-carrier diagnostic isolates steps as large as +7.008 dB for Kawai,
−6.134 dB for New York and +3.659 dB for Belmont. These are model-coordinate
switches, not claimed audible jumps of that size between actual played keys.
Separate integer-key measurements retain legitimate anchor variation.

A finite-window coherent normalizer removes the isolated gain steps in nine
preselected examples, with exact neutral-colour controls. However, it changes
some existing anchor levels by about 2.2 dB, worsens some actual key gaps and
does not repair phase, stereo, attack or tail discontinuities. Its initial
analytic implementation also costs about five to seven times as much at
note setup. It is not adopted. A second candidate interpolates the existing
anchor gain residual in dB and preserves all 39 native anchor, edge and
neutral-colour controls exactly. It also removes the isolated normalization
step, but still worsens some actual gaps and tails: Kawai 38→39's late step
changes from +0.012 to −4.628 dB. Preserving endpoints does not repair the
underlying phase-pattern switch. Mixed builds and realtime endpoint
preparation remain unresolved. Complete evidence is under
`out/realism/pitch-pattern-continuity/`.

### Noise covariance disagrees with its density calibration

`prepareNoise()` normalizes a sum of band-response powers, while `hiss()`
feeds the same two random signals through every band. The actual response
contains cross-band terms. Native-filter analysis across all six builds and
32/44.1/48/96 kHz finds centre-frequency density deficits up to 3.11 dB for
a flat stationary target. This is distinct from the Kawai low-frequency body
problem; the noise bank starts near 397 Hz.

An isolated candidate gives each active frequency band its own random draws.
All-six-build stationary native tests at 48 kHz, plus grand tests at the other
three rates, agree with the intended independent-band response within 0.443 dB
over two fixed seeds. Synthetic finite-burst tests over 64 fixed seeds match
their predicted window powers within 0.141 dB. These are finite stochastic
diagnostics, not perceptual scores or statistical confidence bounds.

The candidate nevertheless fails the existing loud-chord headroom test:
the upright's ten-note fortissimo peak before the output stage changes from
7.960 to 9.810 dBFS, above the unchanged 9.041 dBFS margin. All other engine
assertions pass, including zero callback allocations; both baseline and
candidate parameter-extremes tests pass. No gain or threshold is adjusted.

A separate polyphony diagnostic shows that the current noise system sums
amplitudes across strikes, giving identical simultaneous bursts +6.021 dB
for two and +12.041 dB for four. Under an explicit independent-strike
assumption, summing powers gives +3.010/+6.021 dB and preserves a single
burst exactly. That second candidate reduces the upright chord peak to
9.183 dBFS but still fails the margin. Moreover, separate left/right power
sums with fixed band coherence do not generally preserve stereo covariance
when simultaneous strikes have different left/right ratios. Correct marginal
powers alone do not close the polyphonic model. A shared filtered carrier
scaled by aggregate power also differs in temporal covariance from separately
filtered strikes whose envelopes are not proportional. Full stereo covariance
factoring can repair the instantaneous matrix; it cannot establish temporal
equivalence by itself. No polyphonic recording claim follows from the synthetic
simultaneous-burst control.

The unchanged baseline also fails the same headroom margin at predeclared
seed 3: 9.576 dBFS for the upright ten-note chord, versus 7.960 dBFS at its
usual seed 1. With noise muted the peak is 8.427 dBFS. Over eight fixed seeds
and 18 unchanged chords, each of the three variants has one failing run,
always that upright chord. This bounded diagnostic is not a failure-rate
estimate, does not select a replacement seed and does not excuse the
candidate's failure.

The independent-band candidate's complete 933-recording evaluation has 19
paired note/role/metric regressions and 179 individual case/metric regressions,
with no metric availability changes. Dev noise-error changes are −0.082 dB
grand, +0.041 upright, −0.174 Kawai, −0.199 Hamburg, −0.031 New York and +0.156
Belmont. All 1,584 keyboard cases are finite and retain exact half-gain
linearity; the repeated first case is identical. Those low-gain checks do not
override the chord failure. Keyboard rise changes include −27 ms at Belmont
45/v32 and +9.417 ms at upright 79/v120; these are descriptive changes, not
errors against recordings.

A 32-render, eight-seed audit of those two keyboard cases reproduces all four
seed-1 controls exactly. The large rise changes come from the 90% threshold
selecting different peaks, not a shifted event or signal onset. Paired rise
changes span −27.000…+26.979 ms for Belmont and −0.583…+9.417 ms for upright;
their medians are −0.031 and +0.031 ms. The 10% crossing changes by at most
0.042 ms, and the first nonzero sample is unchanged. This does not erase the
frozen score differences or establish perceptual equivalence; it identifies
finite-realization sensitivity in those particular rise metrics.

An activation control also finds that interleaving draws from one PRNG across
active bands changes an already-playing band's realization when another band
starts. Distinct persistent per-band streams could preserve deterministic
isolation, but have not been substituted or selected to pass the headroom
test. Neither noise candidate is adopted. Frozen evaluations,
all regressions, controls and headroom evidence live under
`out/realism/noise-covariance/`.
