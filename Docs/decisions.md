# Sound decisions

## 2026-10-26 — retain the original physical sound as the quality target

The user identified the reduced preview's attack/struck texture as the main
initial difference, then clarified that the difference remains substantial:
body is missing, stereo image is needed, and attack needs more detail. They
reported that the original demos from before the repository split sounded a
bit better.

That is listening feedback, not a controlled blind-test result. It licenses a
change in development priority: preserve the original full physical renderer's
quality while optimizing it, rather than treating lower isolated-note errors
as permission to replace its mechanics with a reduced pressure-mode renderer.
The original source/calibration and demos are preserved. A matched same-passage,
gain/room-controlled comparison is now available in `QUALITY_BASELINE.md`; no
user preference on that newly matched pair has been inferred.

The live-preview data/interpolation improvements remain useful research evidence
and playable prototypes. They do not establish that the sound is preferable to
the original. Material choices, extra presets and UI remain secondary to the
default physical model's body, attack, stereo and response.

## 2026-10-26 — optimize the original, then improve its realism

The user explicitly directed performance work toward the original model and
clarified that its sound is also imperfect. The original is a starting point
and comparison reference; acoustic recordings and musician feedback remain the
quality target. Preserving the original byte-for-byte is a contract for
performance-only changes, not a permanent restriction on acoustic development.

Maintain separate evidence for these two kinds of change. Performance-only
edits keep the full current mechanics and compare audio plus final mechanical
state. Intentional realism changes compare against recordings and the previous
physical version, with locked fitting/evaluation splits and every regression
reported. Prioritize detailed hammer/struck texture, body, stereo observation,
release/pedal and their coupled behavior before materials, presets or UI.

## 2026-10-26 — spend CPU on audible completeness

The user cites Arturia Piano V3 and Pianoteq as evidence that realtime physical
pianos are practical, and explicitly accepts reduced precision or quality when
the difference is hardly audible. Their priority is broad, integrated behavior:
an approximate key press/release sound can contribute more realism than a more
precise string calculation that omits the action entirely.

This updates the performance acceptance policy. Keep an exact full-model
comparison version, but do not require bit-identical output from every useful
optimization. Evaluate mixed precision, reordered sums, reduced models and
update rates using numerical stability, energy behavior, tuning, attack/decay,
stereo, pedal/retrigger and level-matched musical listening. Null measurements
are diagnostics, not a substitute for audibility judgment. Explicitly record
each approximation and regression.

Allocate a modest but intentional budget to finger/key/keybed/release, hammer,
strings, sympathetic behavior, body, air/lid/player loads and stereo pickup.
Approximations should respond to shared velocity, key, hammer and pedal state
and maintain their causal connection. Preserve isolated module benchmarks.
Materials, preset breadth and UI remain secondary to a convincing default.

## 2026-10-26 — benchmark the full keyboard and retain strike history

The user asks for public acoustic recordings covering C keys across octaves and
the lowest/highest keys, then model and algorithm fitting against them. The
grand benchmark now includes A0 and C1–C8 at several recorded velocity layers,
with fitting/evaluation roles fixed before acquisition. Ambiguous components,
short tails and recording floors must remain explicit; do not force a pitch or
material identity simply because a spectral component is strong.

The user also requires natural differences between successive key presses and
repetitions that respect vibrating strings and incomplete hammer return. Use
bounded excitation/mechanism variation with reproducible per-instance seeds,
retain string phase/energy on every strike, and never reset an active/contact
hammer to create a new note. A bounded repetition controller can defer or
coalesce physically impossible requests; report that policy and test partial
release, rapid repeats, pedal and long decay. Return timing remains an authored
proxy until controlled action recordings identify it.

## 2026-10-26 — investigate the original attack click

The user describes the latest musical demo as sounding quite good, with a
high-frequency ringing click that resembles a key going down too loudly or at
the wrong frequency, especially on the third note. They confirm it is present
in both comparison halves and has been audible since the beginning. The exact
note ordinal is not yet identified.

The first comparison half disables the added mechanical sources. That excludes
those new key/pedal textures as the cause of this shared artifact. Investigate
the original hammer/string/board pressure transient, its calibrated radiation
and the dry versus room path. Preserve the instrument's body and sustained
spectrum; do not mask the problem by removing mechanical behavior or applying
a blanket high-frequency cut. No click fix or listening approval has been
inferred from this feedback.

## 2026-10-27 — listen before further transient adjustment

The contact-driven, frequency-aware observation experiment reduces C3's measured
first impulse and ringing excess, but passes only 33/34 original TRAIN cases.
Hard C8 still exceeds the early-window allowance, and early/whole-note stereo
changes are not covered by sustain preservation. Keep the global failure and
default sound unchanged; see [TRANSIENT_RADIATION.md](../Experiments/docs/TRANSIENT_RADIATION.md).

Stop parameter adjustment for an explicitly experimental musical comparison.
The stricter, unrun music protocol requiring 34/34 remains preserved; a new
diagnostic protocol deliberately admits this exact failed candidate for
listening, without changing any acoustic gate. Identical original audio,
physical-state/force witnesses, a full rho=1 observer control and shared
presentation gains qualify the comparison. They do not establish listener
preference, physical-part identity, realtime cost or production readiness.

## 2026-10-27 — fit each partial's whole decay in relative terms

The four-lane fit weighed each frame by the inverse of its envelope capped
20 dB under the peak, which left the treble's slow aftersound to the noise.
Weighing each frame by the envelope's largest value within a beat plus the
partial's floor fits the whole decay in relative terms. With the board-noise
code unchanged, the dev recordings' treble decay error fell from 17.3 to
12.4 dB/s and treble partial levels from 6.6 to 4.3 dB; C3–B5 sustain went
from 3.5 to 4.6 dB, as the evenly spaced frames of a long tail, up to 20 s, now
count as much as the first seconds, and the bass's 10–90 % rise error from 3.9
to 5.1 ms. Chosen on these measurements, not by ear.

Rejected on the same dev cases: thinning the tail's weight as 1/√t, so that
each doubling of time counts alike, which brought C3–B5 sustain back to 3.6 dB
but the treble's decay back to 17.9 dB/s and the bass's rise error to 10.7 ms;
and even weights to 3.5 s with 1/√t after, a compromise whose break point is
the benchmark's window rather than anything the piano sets. The relative
weights also let many bass partials spend a lane on the recording's noise
floor; weights from the floor's variance plus the fit's own relative error
are the next candidate.

## 2026-10-27 — keep the relative fit weights

The next candidate named above, each frame weighed by the floor's variance plus
the fit's own relative error and refitted until the weights settle, was fitted
on the train recordings and scored on the never-fitted dev cases. Against the
relative weights it moved the partial levels from 3.20 to 3.33 dB, the late
decay from 4.85 to 5.13 dB/s, the broadband envelope from 2.59 to 2.84 dB and
the 10–90 % rise from 5.3 to 6.7 ms, and stayed within 0.1 dB elsewhere. The
relative weights stay. Chosen on these measurements, not by ear.

## 2026-10-28 — measure the components beside the series through their own windows

The recordings hold peaks between the partials that four or more velocity
layers share: in the bass mostly the strings' longitudinal and phantom
partials, from F6 up the undamped strings a strike sets ringing. Each is now
measured through a window just long enough to part it from its nearest
neighbour, from 30 ms to 2 s, its frames weighed against its envelope within
one window and its rise pinned at contact, and the engine plays each with one
lane. A peak from F6 up that recurs within 1.5 cents in four or more recorded
pitches is one undamped string (22 strings, where the same peaks shifted at
random form about three); it rings at one pitch whichever key sets it ringing,
as the per-pitch offsets of the fit had put one string up to 0.5 Hz apart
between keys.

Against the committed engine, on the never-fitted dev recordings from C6 up,
the sustain spectrum moved from 8.83 to 7.86 dB, the early spectrum from 6.43
to 5.17 dB, the late decay from 5.16 to 4.56 dB/s and the board noise from 5.50
to 5.09 dB; the one regression listed is F♯6's tuning on the train recordings,
from 0.97 to 1.47 cents. Chosen on these measurements, not by ear.

Rejected: weighing a component's frames over its first 0.3 s only, which left
components pinging on after the partials around them had decayed, and fitting
each component's rise, which left A7's string at 1578 Hz 20 dB under the
recording. Each undamped string keeps one decay, fitted to its first second;
the slower ring the recordings hold after it is the next candidate.

The benchmark's late decay now needs half a second of frames above the
recording's floor and scores the render with that floor added; both rules,
and the cases that called for them, are beside the code in
`Tools/benchmark_recordings.py`. Both versions were scored again under them.

## 2026-10-28 — two decays for the undamped strings, timed from their tone

With one lane, an undamped string's decay was caught between its quick early
fall and its slow ringing on: after 1.5 s the strings F♯7 and A7 set ringing
sat 20 to 40 dB under the recordings. Each is now fitted like a partial, with
two lanes from contact across the layers, and the engine plays both, the
slower at the string's pitch.

The fit measures a string through a window as wide as the gap to its
neighbours, which also holds the board's noise around a faint string, and a
free slower lane takes that noise for the string ringing on; some were left
at the slowest rate a fit allows, so their notes never ended.
`Tools/compare_ring_levels.py` measures the strings as tones instead, within
2 Hz at 1, 2 and 3 s after contact: at four layers of every train pitch that
rings them, and at every dev case with the strings the engine plays there. A
render over the recording sounds a tone the piano did not; one under it counts
only where the recording shows the string 10 dB clear of the noise around it.
Rules for the slower lane, at 1, 2 and 3 s:

| Rule | Train: over by 10 dB | Train: clear strings' error | Dev: over by 10 dB | Dev: over by 20 dB | Dev: clear strings' error |
|---|---|---|---|---|---|
| One lane (before) | 2.7, 2.2, 2.4 % | 7.5, 19.2, 31.5 dB | 9.3, 4.6, 2.6 % | 4.3, 0.2, 0.4 % | 9.6, 19.6, 35.1 dB |
| Two free lanes | 6.3, 6.3, 6.6 % | 4.2, 8.3, 11.7 dB | 10.7, 6.9, 5.5 % | 4.7, 0.6, 0.9 % | 6.3, 8.8, 15.8 dB |
| Lanes at the slowest rate moved to the string's median | 6.3, 5.8, 6.3 % | 4.4, 10.3, 14.3 dB | 10.5, 6.9, 4.8 % | 4.6, 0.6, 0.7 % | 6.8, 10.7, 17.9 dB |
| The slower lane at the string's median | 15.8, 10.2, 7.8 % | 5.9, 11.5, 17.0 dB | 18.6, 13.0, 10.7 % | 11.1, 5.8, 4.2 % | 7.9, 10.3, 17.5 dB |
| No lane slower than the string's median | 4.6, 1.7, 1.9 % | 5.4, 13.5, 21.6 dB | 8.9, 4.2, 2.7 % | 4.2, 0.3, 0.3 % | 7.7, 13.1, 23.9 dB |
| Timed from the tone | 0.5, 0.0, 1.0 % | 5.4, 6.1, 7.2 dB | 7.9, 7.0, 7.2 % | 6.1, 4.6, 3.8 % | 8.6, 7.2, 8.7 dB |

The string's median is that of its slower lanes over the recorded pitches
whose fits timed one. Timed from the tone: where the string's tone stands
clear in two or more of a layer's half-second windows from 1 to 3.5 s after
contact, a second apart in all, its decay there times the slower lane and its
level sets the lane's (67 of the 103 times a recorded pitch rings a string);
elsewhere no lane decays more slowly than the string's median; and at no
layer do the two lanes together stand over the tone. It is the closest on the
recorded pitches, and on the dev cases' clear strings after a second. Chosen
on these measurements, not by ear.

Its dev strings 20 dB over the recordings after 2 s are almost all at D♯3 and
D♯5: keys between recorded pitches that ring the strings their neighbours
list, though their own partials pass far from them. That is the next change.
