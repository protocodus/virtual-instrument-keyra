# Radiation startup research

The proposed observer/crossover is **not adopted**. The full TRAIN34 confirmation
failed: **26 cases passed and eight failed**. Current runtime, calibration,
presets and defaults are unchanged.

| Frozen experiment | Result | Meaning |
|---|---|---|
| [Stateful radiation observer](../tools/experiments/causal_radiation_pilot/README.md), C3/C4/C6 × two velocities | 4/6 pass; both C6 fail | C3 attack excess fell, but C6 lost low-frequency attack/body pressure. |
| [Fixed 400 Hz compatibility crossover](../tools/experiments/radiation_crossover/README.md), the same six cases | 6/6 pass | Post-hoc reuse of already observed TRAIN cases; no broader qualification. |
| [Full TRAIN34 confirmation](../tools/experiments/radiation_crossover_train34/README.md), six reused + 28 new cases | **26/34 pass; global fail** | One frozen batch and one scoring pass; no retuning or adoption. |

All eight failures concern the unchanged early five-band mean absolute-error
preservation guard, which permits at most +1 dB worsening in each window:

| Case | Worst window after fixed onset, ms | MAE worsening, dB |
|---|---:|---:|
| A0v4 | 0–5 | +3.093 |
| A0v12 | 0–5 | +3.186 |
| D#5v4 | 0–5 | +2.341 |
| D#5v12 | 0–5 | +2.468 |
| C7v4 | 5–20 | +1.386 |
| C7v12 | 20–50 | +1.390 |
| C8v4 | 5–20 | +1.975 |
| C8v12 | 0–5 | +1.501 |

All source-integrity, cached-baseline, late harmonic/envelope, sustain RMS,
L/R and mono preservation guards passed. These relative guards do not establish
accurate absolute attack, body or stereo sound. Passing aggregate bands can
also hide individual-band regressions; the signed errors remain archived.

The historical comparison uses the original 5-anchor model/calibration
(`PreparedModel` SHA `5c8c92f8…`, calibration `619d6bf4…`), 48 kHz stereo,
humanization/mechanisms off and repetition bypassed. It does not qualify the
optional `FrozenConfidenceGrand` profile or connected production settings.
Both the original modal projection and the proposed stateful observation are
causal. The correction drive is a virtual weighted modal signal; its observer
is not a newly identified physical piano part. The fixed construction
`new + LP400(old − new)` preserves the earlier low-frequency observation with
a complementary transition, where correlated signals can still reinforce or
cancel. It does not identify the missing physical source of the reference LF.

C8 needs particular care. The frozen old RMS-matching gains are **451.7466** and
**26.88975** for v4/v12. In the cached reference features, the 31.25–250 Hz band
contains 95.57%/86.76% of measured 31.25–22627 Hz Hann bandpower at 0.25–0.75 s.
That warns against treating the broad rectangular-RMS gain as a tonal deficit:
the window/weighting differ, and the subfundamental content's physical identity
is unassigned. The roughly 4433.89/4433.83 Hz components remain unassigned
diagnostics. Weak candidate-family H1 errors are retained even where the
original reference-prominence mask excludes them from the aggregate; v4 has
roughly −33 to −39 dB H1 errors. No component was relabeled or gate relaxed.
C8v4's short reference supports only three complete late spectral windows,
through 2.5 s, and envelope samples through 2.80 s; no padding was used.

The [compact evidence package](../tools/experiments/radiation_crossover_train34/README.md)
contains the exact protocol, sources and immutable outcomes. Its verifier reads
stored evidence only. There was no new recording acquisition, cutoff sweep,
held-out test, Reason host/SDK validation or realtime qualification. All 34 cases
were already observed TRAIN, and the six earlier outcomes were copied exactly.
