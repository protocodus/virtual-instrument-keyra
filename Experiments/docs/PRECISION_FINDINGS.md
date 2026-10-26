# Full-solver precision experiment

The true-float hot-kernel candidate is retained for listening. It is not promoted
to the default. All 88 keys, 230 strings, 17,778 string modes, 475 board modes,
hammer contact, reciprocal bridge, unison and sympathetic interactions remain.
Neither the canonical working source nor frozen Research source was changed.

## Performance and short-audio evidence

All versions use the same g++ compiler and `-O3 -DNDEBUG -std=c++17
-ffp-contract=off`, without global fast math. Process CPU timing excludes model
construction. These shared-host measurements do not establish a plugin deadline.

| Profile | Music CPU speedup | Numerical result |
|---|---:|---|
| Float q/p, double coefficients/arithmetic | 0.855x | Passes declared experimental contact/bridge/free checks; slower |
| Float string coefficients/free arithmetic, double reductions | 0.987x | Rounded rotation injects energy in some lossless cases; no useful speed gain |
| Float hot kernels/reductions, rotation norm biased <=1 | 1.676x | Clear performance gain with deliberate added numerical loss |

The retained candidate casts force/impulse once per string and uses float
free/force/port/unison/radiation kernels and per-string reductions. Hammer
mechanics, nonlinear contact and the 3x3 bridge solve remain double. C4 and music
have two paired runs with the order reversed; ratios of median CPU times are
1.666x and 1.676x. Single additional pairs give 1.654x for C2 soft, 1.521x for C6
hard, and 1.331x for the 0.35-second mixed event case at 192 kHz.

For the three 1.2-second note/release cases, the retained candidate has:

- Raw waveform null RMS 66–69 dB below baseline RMS.
- Dominant-fundamental peak differences below 0.00064 cents using the same short
  window estimator. This is relative agreement, not tuning accuracy against a
  real piano; unresolved unison and window bias remain.
- Whole-file level changes below 0.0026 dB and short held-energy slope changes
  below 0.0191 dB/s.
- Attack-window energy changes below 0.00085 dB; early/sustain channel-balance
  changes below 0.00186 dB and correlation changes below 0.000135.

These numbers do not prove inaudibility. The short cases do not cover long pedal
tails, repeated chords across the full keyboard, or all dynamics.

## Numerical tradeoff

Contact energy error is 1.18e-5 (declared tolerance 5e-5); contact solve residual
is 2.64e-13 (tolerance 1e-8). The seeded bridge test has no measured positive
energy step and remains finite. Full renderer outputs remain finite in all five
exercised cases. These are bounded tests, not a proof of complete coupled-system
passivity.

Each rounded float rotation has squared norm <=1 after moving its larger
component toward zero as needed. The supplemental free test records maximum
energy throughout every step, not just final energy. Maximum positive energy
excursions are 3.17e-7 at 48 kHz and 6.05e-10 at 192 kHz, below the declared
5e-6 growth tolerance.

The experimental free-oscillator **1e-3 conservation-drift check still fails** because
the candidate adds loss. Across six tested oscillator states over ten seconds,
maximum extra loss is 0.178 dB at 48 kHz and 0.219 dB at 192 kHz. Across every
prepared string mode, the rotation-only added amplitude-decay rate has median /
95th percentile / maximum 0.00127 / 0.00254 / 0.00286 per second at 48 kHz and
0.00549 / 0.01054 / 0.01144 per second at 192 kHz. Those setup figures are not a
full coupled-note decay prediction; intrinsic damping and output weighting vary.

A possible future correction is `d_eff=min(1,d_original/R)` for rotation radius
`R<=1`, at every damping update. It was **not applied**. Zero-loss modes would
still have a numerical decay floor, and a correction requires separate tests.

## Audition and reproduction

[Double control](../Audio/precision-comparison/double-control.flac) and
[float candidate](../Audio/precision-comparison/float-candidate.flac) are lossless
24-bit FLAC exports of dry 48 kHz outputs, complete-file RMS
matched with one shared sample-peak gain. Starts: C2 soft at 0 s, C4 hard at
1.4 s, C6 hard at 2.8 s, original musical prefix at 4.2 s. No blind listening
verdict is claimed.

The [combined listening file](../Audio/precision-comparison/double-then-float.flac)
plays double control then float candidate, with a 0.5-second gap. No extra gain
is applied by the lossless export. Its [manifest](../Audio/precision-comparison/manifest.json)
records the exact source and gains.

[Initial profiles](../Validation/full-precision-profiles.json) preserve the first
two failures; the [candidate report](../Validation/full-precision-candidate.json)
contains broader cases and matched audio; the [energy/radius audit](../Validation/full-precision-free-rates.json)
records the supplemental stability results. Raw study outputs remain under
`out/full-precision-optimization/`.
The artifact manifest and four analysis-stage tool snapshots preserve provenance.

```sh
python3 tools/probe_full_precision.py
python3 tools/probe_full_precision.py --hot-kernel-only
python3 tools/probe_full_precision.py --broaden-hot
python3 tools/probe_full_precision.py --audit-hot-free-rates
```
