# Bounded pickup-field feasibility: rejected

A small relative gain and differential-delay field did not predict the recorded
stereo behavior reliably across omitted training pitches. The tested fitting
procedure is rejected. No model source, calibration, dynamics, recording, plugin control or
default changed, and no candidate audition was exported.

The study uses the unpromoted v4 full-physical candidate in
`out/full-calibration/v4/final-renders/`. Its underlying radiation calibration
still requires the separate full-quality evaluation. These results do not select
a new default or establish a listening verdict.

## Scope and model

The strict training guard validates all 34 frozen training identities, then an
explicit whitelist permits only the 32 unambiguous cases. Both C8 velocities are
excluded from opening audio, fitting, scoring and selection. Fresh A0/C8v8 and
historical test recordings/features are never opened. Reference WAVs pass the
existing exact-container or authenticated decoded-PCM resolver; model WAVs,
source, header and binary are checked against their render identities.

The four parameters are two affine endpoint values for relative R/L gain and two
for differential R-minus-L delay, over MIDI 21–108. Endpoint constraints bound
the complete keyboard field to ±6 dB and ±2 ms. One field is shared by every
velocity, harmonic and time window. No per-key or per-recording parameter is
fitted. A two-parameter gain-only field is a predefined simpler comparison.

Known capture information is AKG C414 AB, approximately 12 cm above the strings;
spacing, orientation and room are unknown. This is an **effective observation
fit**, not recovered microphone geometry or evidence about actual AB spacing.

The complex cross spectrum is `C = Z_L conjugate(Z_R)`. A positive right-channel
delay multiplies C by `exp(+i 2π f tau)`. Delay is applied to every model frequency
bin before harmonic-band integration. Relative channel gains have geometric
mean one; they can change mean stereo power when input channel powers differ.
That power change is reported, without fitting a nuisance gain per recording.

## Estimation and validation

The estimator uses the four frozen onset-relative Hann windows. Each file gets
one common L/R onset index. Independent channel onset alignment and ref/model
carrier phase are never used as phase targets. The relevant phase is measured
within each stereo recording.

Only resolved harmonic bands with useful power in both files/channels survive:
at least −40 dB relative power, 10 dB above neighboring local spectral density,
band coherence squared at least 0.5, and at least 2% of band power in each
channel. Adjacent-band resolution is checked. The resulting 1,067 observations
cover every permitted case. Band coherence here describes integrated spectral
concentration; it is not a statistical coherence estimate with independent
realizations and a confidence interval.

Weights give equal totals to pitches, velocities and available windows, with
capped partial-power weights inside each window. Both velocities and all windows
of each target pitch are omitted together. Fitting closures contain only the
retained-pitch arrays; target features supply evaluation masks and errors only.
Because the fixed base renderer was already calibrated on the complete training
set, this is **conditional cross-validation of the correction**, not unseen-pitch
validation of the entire piano model.

Gain endpoints are fitted to weighted channel-balance error first and then held
fixed while delay minimizes covariance error. This procedure does not establish
a joint optimum over all four parameters. Bounded circular optimization uses global and multiple local starts, without
phase unwrapping. Near-tied minima and boundary hits remain in the report. A
spectral-moment approximation accelerates fitting; every fold is scored using
the exact per-bin projection. Its worst Taylor remainder bound over the complete
gain/delay box, including gain-dependent trace normalization, is below 4e-13.

## Results

Lower errors are better. These are spectral diagnostics, not realism scores.

| Conditional prediction | Covariance error | Balance error | Cross-phase error | Band-coherence error |
|---|---:|---:|---:|---:|
| Actual full-model stereo | 0.7884 | 5.262 dB | 72.81° | 0.05447 |
| Diagnostic rank-one keyboard panner | 0.7458 | 5.434 dB | 71.30° | 0.05594 |
| Gain-only field | 0.7868 | 5.199 dB | 72.81° | 0.05447 |
| Gain-and-delay field | 0.8105 | 5.199 dB | 74.58° | 0.05429 |

Gain alone improves covariance by only about 0.2% and balance by 0.064 dB. Adding
delay worsens covariance and phase, with covariance wins at only 8 of 16 omitted
pitches. The field's mean absolute projected-power change is 0.215 dB. The
rank-one panner trades a smaller covariance error for worse channel balance and
coherence; it is not an accepted replacement for physical radiation.

The full-training delay fit looks better on known observations, but hits the
upper delay limit. Seven cross-validation folds hit a field boundary. The upper
endpoint varies from −0.747 to +2.000 ms between folds, indicating unstable
prediction rather than a defensible recovered geometry.

Neither candidate meets the predefined research gate: at least 2% covariance
improvement, 0.25 dB balance improvement, 10/16 pitch wins and no material
band-coherence regression. This gate is a model-development screen, not an
audibility threshold.

Known-signal checks recover relative gain within 1e-7 dB and delay within 1e-5 ms
(actual errors are much smaller), verify the delay sign and common-channel shift
invariance, and check endpoint bounds. Replacing every omitted-pitch target with
contradictory values changes the fitted parameters by exactly zero. Those checks
support the implementation; they do not turn the rejected field into an acoustic
improvement.

The result rejects this tested balance-first affine gain/delay procedure for this candidate.
It does not rule out measured microphone directivity, richer physical radiation
or other controlled pickup arrangements. Initial attack, releases, musical
phrases and other microphone combinations remain outside this study.

Reproduce:

```sh
python3 tools/probe_full_mic_field.py
```

`out/full-mic-study/report.json` contains the source/PCM receipts, every fold,
window/velocity slices and rejected observations. `observations.npz` preserves
exact per-bin inputs, and `measurements.json` supplies readable band records.
