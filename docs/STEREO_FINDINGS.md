# Default grand stereo-observation feasibility

The current dry close-AB source observation differs substantially from the
recorded stereo image. This training-only investigation asks whether adding one
complex left/right coefficient pair per partial would be a defensible default
correction. **The default was left unchanged.** The simple patch does not
reliably predict spatial behavior at excluded training pitches.

## Data and estimator

`tools/audit_stereo_observation.py` opens only the 26 designated fitting cases in
`References/GrandExpanded/train_features.json`. It never opens the seven reserved
recordings or the historical held-out cases. Input, script, engine and individual
training-WAV hashes are recorded in
[stereo-observation-feasibility.json](../Validation/stereo-observation-feasibility.json).

For each partial, the estimator integrates a two-channel Hann FFT covariance
over the same leakage/unison band and time windows as the preserved benchmark.
Prominent partials exceed −40 dB relative to the recording's early mean stereo
power. The first two windows, 0.05–0.25 and 0.25–0.75 seconds after onset, supply
stability and cross-validation measurements. The later windows are retained as
diagnostics. The baseline is the current dry close-AB panner at 70% width;
authored room, noise and resonance are excluded.

With `C = sum(Z_L conjugate(Z_R))`, the proposed coefficient convention is a
real nonnegative `c_L` and `arg(c_R) = -arg(C)`. Normalizing
`(|c_L|² + |c_R|²)/2 = 1` preserves the carrier-averaged stereo power of one
partial. A synthetic known-phase signal verifies the sign convention to
approximately 4×10⁻¹³ radians. That normalization does **not** prove unchanged
attack waveform, finite-window power, cross-partial interference or envelope.

## Findings

Soft/loud radiation observations are reasonably consistent: across 293 prominent
partial/window pairs, median phase difference is 3.18°, and 93.9% have both
phase difference at most 30° and channel-balance difference at most 3 dB.

Temporal behavior is less consistent. Across 295 prominent early/sustain pairs,
median phase difference is 18.1°, the 90th percentile is 78.2°, and only 50.5%
meet the joint 30°/3 dB limits. A coefficient shared by both fast and late branches
cannot generally reproduce that changing stereo relationship.

This is not solely weak cross-power: requiring coherence-squared at least 0.5
and at least 1% of partial power in each channel leaves 265 pairs. Their median
phase change is 15.8°, the 90th percentile is 59.0°, and only 55.5% meet the same
joint limits.

Holding out **both velocities of each interior training pitch together** gives
507 prominent partial/window predictions. Lower normalized covariance error is
better, but these values are diagnostics rather than realism scores:

| Observation prediction | Power-weighted covariance error | Channel-balance error |
|---|---:|---:|
| Existing dry panner | 0.760 | 6.65 dB |
| Linear complex coefficient, rank one | 0.879 | 9.67 dB |
| Interpolated covariance phase, rank one | 0.765 | 7.02 dB |
| Shortest phase arc / log amplitude ratio | 0.748 | 7.36 dB |
| Positive covariance interpolation, rank two | 0.649 | 7.02 dB |

The best scalar phase heuristic barely improves aggregate covariance and worsens
channel balance. Direct complex interpolation is worse than the simple baseline.
The rank-two covariance result is a useful clue, but it also regresses at several
middle and upper pitches; it is not an accepted model or an audio result.

## Interpretation and limits

One coefficient pair implies a rank-one stereo covariance, with
`|C_model|² = P_L P_R`. It cannot reproduce lower coherence from multiple sources.
The smaller covariance eigenvalue has median 0.24% and 95th percentile 6.39% of
trace across prominent early/sustain observations; the treble has larger residuals
than the lower registers. Individual windows are often nearly rank one, while
their relative phase changes with time. Different unison/polarization/board
contributions are plausible explanations requiring a richer source/observation
model.

Band-integrated spectral similarity from one tapered window is **not** a
multi-realization statistical coherence estimate with known confidence. High
coherence can arise from an unresolved single sinusoid. Shortest-arc interpolation
across pitches is also not a propagation-delay or causal microphone model.

The observations do not uniquely identify individual choirs, polarizations,
bridge/soundboard response, capsule geometry, room reflections or acquisition
processing. They support a bounded future study of richer radiation/source
states, with separate mono, temporal and recording checks. Controlled captures
would help distinguish those mechanisms. They do not justify inventing a fixed
microphone geometry or changing the default solely to lower one pooled score.

Reproduce without fitting or changing any model:

```sh
python3 tools/audit_stereo_observation.py
```
