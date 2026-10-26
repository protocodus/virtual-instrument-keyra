# Full-model modal resolution experiment

The 64/24 cap is worth retaining as an experiment: it achieved about 1.58x speed over the same full float control across four short workloads, with smaller measured differences than the aggressive 32/16 cap. No cap is adopted. The current priority remains fitting the default model to full-range real recordings; this experiment read no recordings or held-out data.

Only the maximum primary/secondary partial counts changed. Every case retains all 88 keys, 230 strings, both string polarizations, 475 soundboard modes, nonlinear hammer contact, reciprocal bridge feedback, sympathetic interaction, and calibrated stereo observation. The existing 19 kHz/9 kHz frequency cutoffs remain. Preparation recomputes actual string and hammer compliance, unison membership/groups and radiation from the retained modes. No static correction, energy replacement or parameter fitting is applied.

| Primary/secondary cap | Primary + secondary modes | Speed over full float | Matched null, C2 soft / music | Assessment |
| --- | --- | --- | --- | --- |
| 320/48 control | 12,507 + 5,271 = 17,778 | 1.00x | — | Frozen same-float control |
| 128/32 | 11,359 + 4,153 = 15,512 | 0.98x | −54.5 / −46.7 dB | Reject for efficiency in this run |
| 64/24 | 8,033 + 3,447 = 11,480 | 1.58x | −40.7 / −37.9 dB | Promising; full-range and listening checks remain |
| 32/16 | 5,110 + 2,597 = 7,707 | 2.21x | −30.7 / −24.6 dB | Reject as the default at this stage; retain comparison |

Speed is the geometric mean of four ratios of median process CPU time. Each case ran twice with reversed traversal on the second repeat. The 1-second music prefix took 3.149 seconds of CPU for the control, 3.617 for 128/32, 2.044 for 64/24, and 1.504 for 32/16. Even the aggressive cap did not reach real time in that workload. These are shared-host measurements, not a Reason deadline result; fewer modes did not guarantee faster execution.

## Measured sound changes

The workload consists of 1.2-second C2-soft, C4-hard and C6-hard notes at MIDI velocities 40/93/93, including release at 0.65 seconds, plus the first second of the existing authored nocturne score. All renders use 48 kHz, the same frozen biased-float source and unchanged calibration. The cap source diffs contain one changed expression.

For 64/24, the largest resolved C2 harmonic change among bands above −40 dB of total spectral energy was 0.81 dB. Its largest short attack-window energy change was 0.017 dB; early/sustain stereo balance changed by at most 0.016 dB. Short held-note and release energy slopes changed by up to 0.006 and 0.043 dB/s respectively. C4/C6 differences were smaller: their matched nulls were approximately −58.7/−90.0 dB.

For 32/16, a resolved C2 harmonic changed by 2.88 dB. C2's largest short attack-window energy change was 0.071 dB, while its short release-energy slope changed by 0.181 dB/s. The music prefix had a −24.6 dB matched residual and up to 0.124 dB stereo-balance change. This is the strongest speed result, but it has the largest measured changes and has not established the requested hardly-audible default behavior.

Aggregate attack energy hides lost high partials: 32/16 removes most of C2's 4–12 kHz attack-band energy. That band is already weak in this frozen control, approximately −52 to −47 dB of attack energy; its removal still limits later attack calibration. The 64/24 cap changes that band by approximately −1.3 to −0.8 dB. Both smaller caps also remove much of C2's extremely weak 12–20 kHz band, which starts around −71 to −82 dB. A future recording fit may change the importance of these bands, so this experiment cannot establish a permanent resolution limit.

The automated triage screens did not reject these short examples. The assessments above also consider efficiency and unresolved listening/full-range requirements. Nulls can reflect phase differences and do not prove audibility; small aggregate values cannot prove inaudibility. Harmonic measurements use inharmonic band centers from the unchanged key parameters, not fitted recordings. Short decay slopes are whole-signal diagnostics, not independently fitted modal decay times.

## Mechanical and numerical checks

All four versions pass the independent resolution-aware topology audit: all strings have both polarizations, every retained primary mode belongs to its original unison row, grouped caches cover all rows, and coefficient fields remain finite. Expected mode counts are independently recomputed. Recomputed string and hammer compliance errors are exactly zero.

All versions also pass the existing float contact and passive-bridge allowances. Conservative contact energy error is approximately 1.18e−5 against a 5e−5 allowance; nonlinear residuals remain below 1e−8. The random-state bridge probe has zero measured positive energy increment and decays to approximately 0.9965 of its initial energy after 200 steps.

Strict free-oscillator conservation remains **false for every version**, including the full float control. Its biased float rotation produces up to 4.01% energy loss over ten seconds at 48 kHz. The separate engineering screen explicitly permits at most 5% numerical loss over that period and at most 5e−6 relative energy injection; the measured peak ratio is 1.000000316. All three cap versions have exactly the same standalone float-loss results as the control. Passing this bounded-loss screen is not a claim of conservation or validated long-tail realism.

## Listening artifacts and reproduction

The following lossless float32 stereo WAVs contain C2, C4, C6 and music at 0, 1.4, 2.8 and 4.2 seconds. Each whole file is RMS matched, with one shared sample-peak ceiling. No EQ, room, per-note gain or time alignment is applied. Raw unmatched renders are retained too.

- [Full float control](../out/full-resolution-optimization/listening-full_f32.wav)
- [128/32](../out/full-resolution-optimization/listening-cap128_32.wav)
- [64/24](../out/full-resolution-optimization/listening-cap64_24.wav)
- [32/16](../out/full-resolution-optimization/listening-cap32_16.wav)
- [Full then 64/24](../out/full-resolution-optimization/full-then-cap64_24.wav)
- [Full then 32/16](../out/full-resolution-optimization/full-then-cap32_16.wav)

```sh
python3 tools/probe_full_resolution.py --repeats 2
```

The tool pins the frozen float source and calibration hashes, compiles matching C++17/O3 configurations with floating-point contraction disabled, retains source diffs and every CPU sample, and writes `Validation/full-resolution.json`. `Validation/full-resolution-findings.json` records the engineering assessments. The full artifact hashes are frozen in `out/full-resolution-optimization/frozen-manifest.json`.

A0/C1 and the rest of the keyboard extremes are not evaluated here, nor are long pedal tails, blind listening or DAW behavior. Reduced bass resolution needs those checks before a default change. No additional caps were explored, and neither canonical source nor `Research` was edited.
