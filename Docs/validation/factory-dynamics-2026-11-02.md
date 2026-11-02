# Factory piano dynamics at playing level

Keyra's six pianos keep their individual level and timbre calibrations. Those
calibrations do not ensure that every chord grows louder when struck harder.
The existing level test checks the median of several repetitions. An individual
reversal can hide behind a passing median. This audit keeps the individual
strikes and compares exactly the same touch draws at both velocities.

## Reproduce the measurements

Build `KeyraLevels` from the product repository. Run each command from a DSP
build directory:

```sh
./KeyraLevels --check --jobs 4
./KeyraLevels --audit-dynamics --jobs 4 > factory.csv
./KeyraLevels --audit-dynamics --low-drive --jobs 4 > low-drive.csv
```

Each CSV has 2,544 paired readings, with the named factory preset, mic setting,
actual MIDI notes, velocities and round. The first command retains the existing
peak, median and VU limits. The other two are diagnostics and return the
observations without treating a median as a pass for every chord. Output gain
is 0.7 at factory and 0.07 at low drive. No post-render normalization is
applied. Both use the production plug-in's DSP, at 48 kHz; low drive is not a
software bypass. Belmont uses its chosen Brightness of 0.75 in both runs.

The meter measures maximum RMS within a 300 ms sliding window on the louder
channel. These are meter comparisons, not listener preference or acoustic
ground truth. Each panel covers all six instruments and both mic endpoints:

| Panel | Pairs | Quieter at higher velocity, factory | Quieter at higher velocity, low drive | Worst step at factory |
| --- | ---: | ---: | ---: | ---: |
| Eight calibration chords, five rounds, 110 → 127 | 480 | 104 | 0 | −0.632 dB |
| Eight different voicings, five rounds, 101 → 121 | 480 | 30 | 1 | −1.246 dB |
| Twelve more voicings, eleven steps between 48 and 127 | 1,584 | 272 | 19 | −1.504 dB |

These results were reproduced on the 0.4.10 engine. The counts also match its
0.4.9 predecessor. The largest change in an individual factory velocity step
between the two is less than 0.0001 dB. The [damper and repeated-note
correction](damper-travel-2026-11-02.md) is independent of this fault.

## Protection-stage experiments

In isolated 0.4.9 trials, a straight bypass of the output protection also had
19 negative steps on the expanded panel. It is not appropriate to attribute
every decrease to the output compressor. Simply bypassing protection can also
exceed the plug-in's sample ceiling and level limits.

For example, the Kakegawa bass chord A1–E2–A2–C3–E3–A3 (MIDI 116 → 120)
fell **3.15 dB before protection** on the tube mic. Each of the six struck
notes grew on its own. Their independent powers and the remaining shared
sound grew 0.19 dB, evaluated in the actual winning meter windows. The A1
second partial and A2 fundamental overlapped around 110 Hz; their relative
phase changed so the sum cancelled more strongly at the higher velocity.
That pair accounted for about 94% of the decrease in the cross terms. The
close mic also showed the effect, but less strongly. Raising the overall
gain of A1 or A2 to compensate would change notes that already grew. No
recorded chord establishes how much cancellation this piano should have.
The A1 layer endpoints differ by about 178° under the fitter's contact
alignment. Interpolating their normalized complex vectors concentrates the
rotation near the halfway point: A1 rotated about 166° across these two
strikes while A2 moved less than a degree. The library contains separate
single notes, with no shared hammer timing to resolve the absolute phase
between the keys at the intervening velocities.

A trial rotated each partial's lanes together, taking its strongest measured
carrier through that angle at a constant rate. This preserved every tested
layer endpoint and the individual partial envelopes to floating-point
precision. It cut the example's tube drop from 3.15 to 0.23 dB. But the same
chord at 124 → 127 changed from a 0.015 dB rise to a 0.76 dB fall. The
expanded panel went from 19 to 28 decreases before output protection. Smoothing
the rotation moved interference to other velocities. That trial was rejected.

The most promising alternative kept the shared peak limiter and credited the
attenuation that it had already supplied. A stereo detector compared aligned
input power and peak-limited power; the slower level control applied just the
remaining reduction. A common 3:1 ratio met the existing peak/VU limits,
raised **all 480** original chord pairs, and left just one decreasing pair on
the 480 independent comparisons. That pair also decreased before the guard.
On the expanded panel, however, **three** chords which rose before protection
fell after it, by up to **0.052 dB**. One already-small negative step got worse
than the current product's. No measured perceptibility is implied.

This is a time-domain effect. The input increment in those three cases was
only 0.054–0.062 dB; a static 3:1 curve would leave about 0.02 dB. The gain
applied earlier in the meter window differed between the two strikes by more
than that margin. Replacing the exponential detector by the meter's exact
rectangular window introduced two new failures on the independent set. The
least-compressive common exponential ratio satisfying the original level
limits (2.33:1; Helsinki failed at 2.32:1) still reversed the same three
source-positive comparisons. Moving a raw power guard upstream of the peak
limiter also passed the published level limits, yet five of the six pianos
still had reversals on the original chord test.

Feeding back the *actually delivered* power reduced the expanded reversal
count to 18, but three raw-positive steps still went negative. More decisively,
the candidates added distortion to the low register. A settled 27.5 Hz sine
through the guard, with input peak 1.8, came out at almost the same RMS with
feedback as with stock (−13.30 vs −13.32 dBFS). Non-fundamental energy was
−26.78 dBc with feedback and −27.06 dBc with 3:1 feedforward, compared to
−84.92 dBc with stock. The feedback version also added a third harmonic at
input peak 0.5, below the limiter's ceiling. These are isolated guard tests,
not measurements of a piano recording.

Putting a 3:1 compressor *before* the unchanged limiter, with the original
power, attack and release times, kept the hot A0 clean (−87.53 dBc).
However, hard-chord minima remained negative at the close mic on all six
pianos, and New York failed even the existing median check at both mic
settings. No controller or model parameters were changed to pass the tests.

These alternatives did not meet the criteria for changing factory output.
For a player wanting more headroom today, reducing Keyra's Output *before*
the guard preserves more of the difference between hard strikes. Lowering
only the DAW fader cannot recover a difference already compressed in Keyra.

## What is separate from output protection

- **New York, MIDI 27 (D♯1):** the ordinary-play 44 → 45 step fell about
  0.85 dB in the 50–300 ms window. Changing partial 14 at the neighboring
  recorded key 29 fixed that example but increased excess variation at other
  pitches, by as much as 2.12 dB. Key 27 itself has no recording in this
  library.
- **Hamamatsu, MIDI 56 (G♯3):** the 72 → 73 onset step fell about 0.79 dB.
  Replacing one interpolation interval repaired it, but the whole-note gain
  adjustment affected the fourth partial at key 55. Holding that gain fixed
  isolated the cause and passed all 1,728 analytic observations. On 1,344
  native cases it still worsened two release steps in a mix with Kakegawa.
  A source-only refit using the existing four-lane format reduced the fitting
  objective by 47%, chiefly by improving the tail after 3.5 s. It more than
  doubled the objective below 750 ms; nine native comparisons worsened,
  including six new reversals. The
  current interval table and source fit are retained.
  Neither experiment justifies modifying the measured data of the other five
  pianos. See the [earlier interpolation trials](../research/consistency-and-belmont-2026-11-02.md).

Keep per-note checks, paired chord checks at the actual output setting and
separate recording validation. Each identifies a different failure. None
establishes that the others passed.
