# Whole-keyboard quality and Belmont clarity

The owner's priority is a common playing-quality standard across all six
pianos, preserving each instrument's character. Recordings now serve as sanity
checks rather than targets for making every piano resemble one recording.

## Coverage and limits

The unchanged 0.4.5 native engine rendered **67,056 isolated strikes**: six
pianos, every MIDI key 21–108 and every velocity 1–127. Every strike uses the
normal playing response and the same first touch draw after a hard reset.
The first 300 ms is measured at every velocity. Thirteen velocities per key
continue through a 1.5-second hold and 0.5-second release. Output latency is
removed before measurement. Controls are Full quality, 48 kHz, gain 0.07,
brightness 0.5, resonance 0.25, Mechanics 0.175, width 0.75, Mic/soft/pedals/mute 0.

All strikes are finite and non-silent in the first 300 ms. This does **not**
certify absence of audible artifacts, every possible controller history, or
all decay windows at all velocities. Adjacent level changes are diagnostic
flags; normal piano irregularity is not automatically a defect.

A separate structural sweep covered the same 67,056 setups with no invalid
states or unstable poles. The action panel adds 48 paired scenes across all
six models, four registers and two velocities: short/long releases, sustain
release and repedalling, and repeated strikes. Its 96 renders were finite.

## Findings that remain actionable

The pitch interpolation still switches the nearest phase/pickup pattern at
some anchor midpoints. Kawai MIDI 79, velocity 18 is a concrete example:
its first 50–300 ms stereo level is 8.663 dB below the mean of its neighbouring
keys. A fixed-carrier modal probe crossing the actual midpoint changes the
fundamental's early power by 6.619 dB while redistributing energy into later
windows. This is a pattern-transfer discontinuity, not excess Mechanics or
an unstable decay. The four-lane interpolation has not been replaced; previous
single-window smoothing trials produced other tail regressions.

Selected largest successive-velocity decreases in the 50–300 ms window:

| Piano | Key | Velocity transition | Level change |
| --- | ---: | ---: | ---: |
| Kakegawa | 34 | 56 → 57 | −0.588 dB |
| Helsinki | 25 | 57 → 58 | −0.269 dB |
| Hamamatsu | 56 | 72 → 73 | −0.541 dB |
| Hamburg | 99 | 125 → 126 | −0.193 dB |
| New York | 27 | 44 → 45 | −0.850 dB |
| Belmont, before C | 63 | 63 → 64 | −0.163 dB |

These are deterministic finite-window energy changes, not estimates of
perceived loudness. New York and Kawai merit targeted interpolation work;
one global equalizer or gain curve cannot repair the underlying envelopes.

Hamburg's reported Moonlight attack remains with Mechanics muted. The explicit
control's causal contribution is 52.37 dB below the remaining theme in RMS,
comparable to Kakegawa and Helsinki. In onset windows, modal strings dominate;
the coherent body group is the largest secondary transient. Reducing the
action constant would therefore leave most of that attack intact.

A distinct release imbalance appears in Hamburg's quiet high notes: at C7,
velocity 32, the short-release contribution is 22.15 dB below the initial
note, versus 49.01 dB at velocity 112. Its inherited release mapping makes the
absolute release amplitude nearly independent of strike velocity. Note-on
velocity alone does not specify key-return speed, so no new velocity law was
invented from this measurement.

## Accepted Belmont change

The owner chose C: remove only Belmont's additional velocity colour, preserving
the measured layer timbre. All 20 control renders for the other five pianos
remain byte-identical; four Belmont controls exactly match the audition's
neutral-colour renderer. Mixed builds change by their Belmont hammer share.

The adopted model was rendered across all 11,176 key/velocity combinations
with the same protocol. No invalid samples occurred. In the 50–300 ms window,
its worst successive-velocity decrease improves from −0.163 to −0.027 dB;
no decreases exceed 0.1 dB in either of the first two measured windows.
This choice does not repair the independent pitch-envelope boundaries.

## Tube output calibration

Removing Belmont's extra colour changed its loud tube-mic chord reading from
the previously accepted region to +1.036856902 VU. Its typical tube reading
was −9.133752024 VU. Reducing the existing pre-guard tube scale to the exact
−9.5 VU typical boundary left the loud chord at +1.0272 VU: compression largely
cancelled that attenuation. This candidate was rejected.

The existing typical lower limit (−9.5 VU) and owner-approved Belmont tube
chord upper limit (+0.7 VU) allow a **post-guard** attenuation greater than
0.336856902 dB and no greater than 0.366247976 dB. Version 0.4.6 uses the
interval midpoint, **0.351552439 dB**. This is a measured monitoring-level
calibration, not a string/body coefficient or an acoustic fit. Neither test
limit was relaxed.

The full-tube readings become −9.485304275 VU typical and +0.685304650 VU for
the loudest chord; strong-to-hard velocity growth remains +0.927416593 dB.
The sample peak becomes −1.85155 dBFS. The default stereo-pair sound is exactly
unchanged, including the accepted C audition and the Bugatti Step renders.

At intermediate Mic settings the calibration scales the complete blended
output, according to Mic and the Belmont hammer share; it does not claim to
isolate a tube component after nonlinear processing. Hammer-share changes
smooth over the existing 12 ms time constant, and a fixed gain FIFO follows
the shared guard's exact look-ahead. No latency, control, automation identifier,
shared portfolio output-stage code, or allocation in callbacks was added.
Static other-piano/Mic0 paths retain exact output; a live transition away from
Belmont intentionally fades the prior calibration.

The focused native regression covers 55 static controls at 44.1, 48 and 192 kHz,
an independent delayed-gain oracle at two block partitions, reset, idle control
changes, CC120, prepare, and allocation checks. It retains the unchanged guard's
existing one-ULP sample-ceiling roundoff, and separately requires that no
candidate sample exceed its untrimmed control. Existing body-glide partition
roundoff is measured against the unchanged control rather than attributed to
the new gain path.

## Reproduction

Local working evidence is retained under:

- `out/realism/whole-keyboard-quality-20261101/`: public-engine sweep source,
  protocol, all numeric rows, per-model receipts, summary, and adopted Belmont
  comparison. An end-of-run source-tree equality assertion caught the authorized
  Belmont edit while the final baseline jobs ran. The statically linked baseline
  executable retained its frozen hash throughout; the amendment records this
  explicitly. Candidate data use a separate executable and filenames.
- `out/realism/full-range-structure-20261101/`: structural sweep and Kawai 79
  causal midpoint probe.
- `out/realism/six-piano-mechanics-balance-20261101/`: Moonlight ablation,
  component closure and action panel.
- `out/realism/belmont-colour-adoption-046/`: exact other-piano and audition
  parity, plus adopted structural sweep.

The complete Bugatti Step comparison uses the supplied modern score's full
154-bar form, including both repeat endings and D.S./coda, independently
checked against the 1931 edition. All six use the same 2,819 attacks and
152.256-second performance. Listening copies receive one whole-file RMS trim
each, with no equalization or compression; raw common-gain renders are retained.
The source score, MIDI, generator, edition differences and receipts remain in
the dated Downloads delivery rather than the public repository.
