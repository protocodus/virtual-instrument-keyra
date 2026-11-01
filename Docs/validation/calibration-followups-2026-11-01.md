# Calibration follow-ups: rejected candidates — 2026-11-01

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

The next bounded work examines information lost during stereo compression
and later fit/export transformations, plus phase-pattern changes between
recorded pitches. It preserves the owner's contact cap and the current
oscillator count. Better raw fitting alone will not qualify a candidate for
the model: its exported native sound must improve the recording comparison.
