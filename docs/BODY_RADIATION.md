# Soundboard radiation reconstruction and fitting

**The six-weight body-only replacement is rejected: 0/34 cases passed all
unchanged preservation guards. Runtime sound and defaults are unchanged.**

The latest experiment asks whether a shared, bounded observation of the actual
soundboard can replace the original empirical string-state radiation correction.
It changes observation only. It does not add a structural part, change the
hammer/string/bridge mechanics, or establish recording fidelity or realtime
performance.

## Verified reconstruction

The frozen original-control captures contain the model's three solved bridge
forces at every frame. These are saved **simulation forces**, not forces measured
on the recorded piano. Replaying those forces through the existing 475 board
modes reproduces all 34 raw body outputs: **12,403,200 double samples match bit
for bit**. Every force frame also matches the archived before/after FNV checksum;
FNV is not a collision-free cryptographic proof.

Six smooth, nonnegative frequency weights partition the board modes. They share
the existing signed stereo microphone geometry and weight each mode's complete
acceleration, including restoring, damping and instantaneous force terms. Their
sum reproduces the raw board pressure within double-precision rounding. Chunk,
high-pass and coherent-energy checks passed; independent review verified the
source, input identities and recorded outcomes.

The 34 cases and six additional chunk checks took 56.3 seconds in this offline
board-only implementation. This is a workflow timing, not a plugin callback
benchmark. It avoids rerunning the much larger string/contact simulation during
observation fitting. The [reconstruction package](../tools/experiments/body_radiation_basis/README.md)
preserves source, checks, input identities and the pre-opening implementation
failures; raw captures remain external.

## Bounded fit

The proposed body-only output is

```text
Y = HP24(sum_b alpha_b * body_basis_b), alpha_b > 0.
```

It removes the empirical string correction. Setting every alpha to one gives
the uncalibrated raw body, **not** the original final sound. Multipliers can fold
into existing board microphone coefficients, requiring no new runtime states.
Rebuilding the old empirical correction after changing those coefficients would
be a different, nonlinear operator and is outside this experiment.

One six-parameter fit used the 32 already observed TRAIN cases other than C8.
C8 is excluded from parameter selection because its broad sustain normalization
contains substantial unassigned subfundamental content. The same six weights
apply to **all 34 cases**, including C8; every original preservation guard and
complete-window censoring rule still applies. There are no per-note output
exceptions, new gains, shifted onsets or microphone-channel-specific fits.

The objective balanced early band powers, included late harmonics and late
envelopes, with fixed smoothness and gain priors. Coherent Gram matrices retain
interference between basis signals. A single bounded optimization starts at unit
weights; all final metrics use explicit float32 candidate output.

Six broad gains cannot add missing poles, move string partials, change physical
decay or create a measured microphone arrangement. An improved local TRAIN fit
would still need listening, unseen evidence and integrated network checks before
any runtime change.

## Result and limits

The single bounded optimization converged in 13 iterations / 14 evaluations.
The complete numerical fitting/scoring run took 19.0 seconds, with no new
physical render or reference PCM access. All 34 explicit final outputs passed
the numerical forecast checks. This verifies the calculation, not the sound.

The paired errors below use this experiment's frozen scoring convention and
the 32 fit cases. They compare the **original final sound** with the fitted
body-only replacement, rather than comparing against its uncalibrated start.

| Mean absolute error, dB; lower is better | Original final sound | Body-only fit |
|---|---:|---:|
| Early five-band levels | 14.434 | 11.490 |
| Included late harmonics | 11.385 | 12.874 |
| Late envelope | 5.445 | 6.809 |

The optimized objective improved from 105.45 to 95.16 relative to the **raw
body-only start**. That is not an improvement over the original instrument.
Across all 34 cases, every sustain RMS preservation guard failed; drift ranged
from -8.92 to +12.72 dB. L/R failed in 25 cases and mono energy in 31. A shared
output gain would not resolve those opposing level changes.

C3's first-5ms excess fell by 20.24 / 19.22 dB, but its 5-20ms ringing excess
increased by 0.90 / 1.02 dB. Neither layer passed the original click criteria.
No failed case was omitted, including C8, and no alternate coefficient set was
selected. The [fit evidence](../tools/experiments/body_radiation_fit/README.md)
retains the exact objective, one optimizer trace and all 34 outcomes.

The first attempt stopped before optimization because the running envelope
average and reassociated Gram calculation exceeded a relative-only numerical
consistency threshold. That failure remains archived. The second attempt used
direct 240-sample positive-semidefinite Grams and an independently derived
absolute rounding bound for the existing SciPy running average. Targets,
parameter bounds, initialization and all acoustic gates stayed unchanged;
there was only one optimization.

This rejects this small local fit as a replacement. It does not prove that
every possible body observation is infeasible, identify a missing physical part,
or establish a better stereo geometry. Further work needs better constrained
radiation and mechanical evidence rather than promoting this result or adding
per-note exceptions.
