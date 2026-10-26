# Soundboard radiation reconstruction and fitting

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

One six-parameter fit uses the 32 already observed TRAIN cases other than C8.
C8 is excluded from parameter selection because its broad sustain normalization
contains substantial unassigned subfundamental content. The same six weights
apply to **all 34 cases**, including C8; every original preservation guard and
complete-window censoring rule still applies. There are no per-note output
exceptions, new gains, shifted onsets or microphone-channel-specific fits.

The objective balances early band powers, included late harmonics and late
envelopes, with fixed smoothness and gain priors. Coherent Gram matrices retain
interference between basis signals. A single bounded optimization starts at unit
weights; all final metrics use explicit float32 candidate output.

Six broad gains cannot add missing poles, move string partials, change physical
decay or create a measured microphone arrangement. An improved local TRAIN fit
would still need listening, unseen evidence and integrated network checks before
any runtime change.
