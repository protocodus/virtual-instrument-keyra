# Confidence-prior full-network loss candidate

This candidate improves the full model's prompt/aftersound balance against the
locked recordings. It remains a private calibration under `out/`; the canonical
model and plugin defaults are unchanged.

The preceding [global loss experiment](FULL_INVERSE_LOSS.md) failed its remaining
TRAIN confirmation. This phase uses **all 34 TRAIN cases for fitting**, including
its confidence-rule design. It is not a second independent confirmation of the
global experiment. The fitted candidate was then frozen before testing sixteen
previously observed historical cases. Neither formerly fresh extreme is fresh
again.

## Fitted change

At fifteen anchors, only the nonnegative common-unison excess loss changes:

```text
new_prompt = old_late + 0.6 * (old_prompt - old_late)
```

The scale is the already selected TRAIN refinement. Support requires both TRAIN
layers to have good, identifiable pitch with at least four fitted peaks and no
pitch-identity ambiguity. Their union must contain at least four distinct early
decay partial orders with relative level at least −45 dB, slope below −0.3 dB/s,
and fit R² at least 0.15. The rule uses existing TRAIN metadata. It retains the
prior at C7 and C8, whose pooled supported early-decay order counts are one each.

Supported MIDI anchors are 21, 24, 33, 36, 39, 45, 48, 51, 60, 63, 69, 72, 75,
81 and 84. The C7/C8 prompt arrays remain exact; all other physical key fields,
including intrinsic late loss, hammer, tuning, stiffness, detuning, radiation
and board parameters, remain exact everywhere. Existing positive interpolation
between anchors remains in use. This is a conservative regularization choice,
not a unique identification of a piano's physical damping.

## Recording agreement

Errors are lower when the model agrees better with the reference. These are
recording-agreement measures, not perceptual scores. Attack is the unweighted
mean of each case's accepted 5–100 ms band MAEs above 250 Hz. The historical
report also retains the earlier flat band-cell average for comparison.

| Data and error | Original full control | V4 candidate | Confidence candidate |
|---|---:|---:|---:|
| TRAIN34 envelope, dB | 6.101 | 5.011 | 4.628 |
| TRAIN34 harmonic, dB | 7.852 | 6.911 | 6.987 |
| TRAIN34 attack, dB | 6.901 | 5.361 | 5.022 |
| Historical16 envelope, dB | 6.637 | 6.366 | 5.710 |
| Historical16 harmonic, dB | 8.043 | 7.380 | 7.426 |
| Historical16 attack, dB | 5.695 | 4.613 | 4.213 |

All fifteen previously fixed TRAIN gates pass versus V4, including the individual
regression limits. Historical envelope improves in twelve of sixteen cases
versus either baseline. Harmonic error improves in eight cases versus the
original and seven versus V4; the small mean harmonic regression versus V4 is
retained.

The earlier A3 envelope regression is reversed. At A3 layers 4/8/12, envelope
error falls by 2.261/2.147/2.052 dB versus V4 and by 1.167/1.131/1.133 dB versus
the original control. Absolute candidate envelope errors remain large:
9.419/8.491/7.488 dB.

Material remaining problems include:

- A0v8 attack rise-time error is 38.146 ms, versus 1.438 ms for the original.
  The new loss adjustment barely changes that existing V4 regression.
- C2v8 envelope error is 3.589 dB, versus 2.775 dB for the original.
- C8v8 harmonic error is 37.671 dB, versus 36.887 dB for the original.
  The unassigned 4433.8 Hz component remains about 83 dB too weak in its two
  prominent reference windows. Its physical identity remains unknown.
- TRAIN A4v12 and D#5v12 envelope errors regress by 1.052 and 1.631 dB versus
  the original despite better aggregate agreement.

These problems prevent a claim of recording parity or complete calibration.
The candidate is ready for matched listening; it has not been promoted.

## Frozen provenance and recovery

The candidate profile/header/binary and all TRAIN predictions were frozen at
17:46:57 UTC on 2026-10-26. The historical protocol was frozen at 17:49:23 UTC.
The interrupted batch had eleven completed predictions. A separately identified
recovery runner authenticated and preserved those eleven sidecars and rendered
only the remaining five, finishing all predictions at 18:00:00 UTC. Historical
scoring started at 18:00:08 UTC. No new acquisition, fitting or default change
occurred during recovery.

The completing-agent audit recomputes the TRAIN support mask, checks every
changed/nonchanged field, reproduces the generated candidate header exactly,
verifies all 129 historical frozen input identities and the six-stage chronology,
and confirms that the original calibration and `Research/` remain unchanged.
It is a numerical/data-provenance audit, not an independent listening review.

Receipts:

- [TRAIN result](../Validation/full-confidence-loss.json)
- [Historical result with every case and regression](../Validation/full-confidence-loss-historical.json)
- [Provenance review](../Validation/full-confidence-loss-review.json)
- [Matched listening files and processing notes](../Audio/full-confidence-loss/README.md)

The piano and recording chain are the same Salamander instrument throughout.
Hammer speeds, capture pedal state, room and editing are not fully known. MIDI
velocities remain SFZ-bin proxies. No new instrument/microphone generalization,
realtime budget, Reason host validation or perceptual parity is established.

## Reproduction

The original TRAIN candidate workflow remains:

```sh
OPENBLAS_NUM_THREADS=1 python3 tools/probe_full_confidence_loss.py run \
  --output out/full-confidence-loss-reproduction \
  --report out/full-confidence-loss-reproduction/report.json
```

The historical runner is specific to the existing frozen interrupted batch. Use
`python3 tools/evaluate_full_confidence_loss.py verify` to authenticate it. Its
`predictions` stage reuses authenticated completed results and never overwrites
unreceipted audio. Its `score` stage refuses to overwrite a completed score or
silently restart interrupted scoring. The exporter runs no synthesis or fitting:

```sh
OPENBLAS_NUM_THREADS=1 python3 tools/export_full_confidence_listening.py
```
