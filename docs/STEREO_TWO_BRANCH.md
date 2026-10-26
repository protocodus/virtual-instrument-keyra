# Two-branch stereo projection: rejected feasibility candidate

Giving the existing fast and late decay branches independent complex left/right
coefficients does not generalize across the training pitches. The bounded
candidate is rejected. No native audio, default calibration, synthesis source,
plugin parameter or header was changed by this study.

## Scope and method

[The reproducible diagnostic](../tools/probe_two_branch_stereo.py) uses only the
26 designated training cases, their saved four-window stereo covariances and
their fitted amplitude/decay envelopes. It never opens A3, the seven reserved
recordings or historical held-out audio/features. Both velocities of each
interior training pitch are excluded together in cross-validation. Their
frequencies, dispersion, envelopes and observations are predicted from retained
anchors. Target covariance enters only the evaluation masks, weights and errors.

For the two branch signals, define a positive source covariance

```
Q = 0.5 [[A, D], [conjugate(D), B]]
A = weighted mean(F² exp(-2 sf t))
B = weighted mean(L² exp(-2 sl t))
D = weighted mean(F L exp(-(sf + sl)t) exp(-i delta t))
S = T Q conjugate_transpose(T)
```

`T` has independent complex L/R columns for the fast and late branch; the fast
left coefficient is real and positive to fix the common phase gauge. The source
detuning remains the existing 0.23 cents. Fits share `T` across the two velocities
and all four windows (0.05–0.25, 0.25–0.75, 0.75–1.5 and 1.5–3.5 seconds).
Bounded coefficients, trace-scaled residuals and three predefined regularization
strengths constrain the fit. Predictions remain positive semidefinite.

The principal interpolation normalizes each column to squared norm two and
absorbs its original norm into its branch amplitude before interpolation. Direct
complex interpolation is retained as a second check. Six predefined RBF ridge
fields also test smoother dependence on frequency and pitch, with Cartesian and
polar coefficient encodings. These are a bounded exploration, not an exhaustive
search over radiation models.

## Results

Lower errors are better. The early-window comparison uses the same 492 prominent
partial/windows in each local interpolation method, with power weighting.

| Prediction | Normalized covariance error | Absolute channel-balance error |
|---|---:|---:|
| Existing dry panner | 0.760 | 6.65 dB |
| Shared static complex coefficient | 0.880 | 9.67 dB |
| Independent columns, normalized interpolation (three regularizers) | 0.875–0.884 | 9.81–10.44 dB |
| Independent columns, direct interpolation | 0.885–0.892 | 10.05–10.68 dB |
| Best of six frequency/pitch fields | 0.779 | 7.07 dB |

All 193 local node optimizations converge at each regularization strength.
Known-pitch fitting has much smaller early covariance error (0.125 at strength
0.1, against 0.787 for the panner), but does not beat the shared static early
fit (0.121) or predict omitted pitches. The normalized interpolation also has
about 2.50 dB mean absolute raw-power error on excluded pitches. A good local fit
is insufficient evidence for changing the default instrument.

This is not universal local rank deficiency: the conditional data Jacobian has
full seven-parameter rank at 190 of 193 fitted nodes. At strength 0.1 its median
smallest/largest singular-value ratio is 0.050; the tenth percentile is 0.0025.
This conditioning is conditional on the assumed decay envelopes, detuning and
gauge. It does not establish stable physical source identities across pitches.

## Interpretation and remaining limits

The earlier [rank-two covariance clue](STEREO_FINDINGS.md) allows each measured
window a general positive covariance. It does not imply that two fixed radiation
vectors multiplying the current fitted fast/late decay basis can explain every
window and interpolate to other notes. Those decay components can trade relative
weight or become negligible across pitches; they have not been identified as
consistent physical string or board sources. This is a plausible source of the
failure, not a uniquely established cause.

Separate unit-normalized branch vectors change coherent interference. Their
mean stereo power is `0.5(A+B) + 0.5 real(D b†a)` rather than the existing
`0.5(A+B) + real(D)`. Normalizing columns and rescaling branch amplitudes preserves
the new prediction, but does not preserve the previous fit or live early-energy
normalization. A future native candidate requires observation-aware amplitude
calibration and velocity, attack, mono and dynamics checks.

The analysis checks positive covariance, the analytical gradient against finite
differences, explicit complex time signals, and column-normalization invariance.
It does not test native audio or realism. Windows starting at 50 ms leave the
initial attack and common cross-harmonic onset phases unresolved. No claim about
physical choir, polarization, bridge/soundboard or microphone geometry follows
from these covariances. A richer source basis should preserve physical source
identity and independent displacement/velocity observations; controlled captures
and listening can then test its predictions. This rejection does not rule out
all two-source physical models.

The [compact report](../Validation/two-branch-stereo-feasibility.json) records
input/source SHA-256 hashes, self-check errors, pitchwise results and hashes of
raw fitted coefficients in the ignored `out/stereo-candidate/` directory.

```sh
OPENBLAS_NUM_THREADS=1 python3 tools/probe_two_branch_stereo.py
```
