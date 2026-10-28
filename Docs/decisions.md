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

## 2026-10-28 — ring the undamped strings as near as the struck key's partials come

Between two recorded pitches a key rang every string either lists, faded
towards the one that does not. But a string rings through the strike's
partial nearest it, as a resonator driven off its pitch, and a key whose
partials pass far from a string its neighbour had a partial on hardly sets it
ringing. Each listed string is now scaled by the strike's decay (the string's
faster lane) over its distance from the key's nearest partial, against the
recorded pitch's distance, and never rung louder than the recorded pitch rang
it; the recorded pitches are unchanged.

On the dev cases, against the strings timed from their tone alone: strings
10 dB over the recordings at 1, 2 and 3 s 2.9, 2.1 and 2.3 % (7.9, 7.0, 7.2 %;
one lane 9.3, 4.6, 2.6 %), 20 dB over 1.3, 0.2 and 0.3 % (6.1, 4.6, 3.8 %; one
lane 4.3, 0.2, 0.4 %), and the clear strings' error 7.9, 7.4 and 8.9 dB (8.6,
7.2, 8.7 dB). Chosen on these measurements, not by ear.

At 1 s it leaves 30 % of the dev cases' clear strings 10 dB or more under the
recordings (the tone alone 21 %, one lane 25 %): strings the strike's knock
sets ringing through the body, which no partial need come near, such as
D♯5's at 2174 Hz, 295 Hz from its nearest partial, and D♯7's below its
fundamental. That second drive is not modelled.

## 2026-10-28 — play the action's knocks

The listening test `2026-10-28-action-sounds` asked whether Keyra should play
the action's own noises: a damper landing as a key is let go, and the sustain
pedal going down and coming up. A was the engine at `1d61623`; B was A plus
those knocks, synthesized on the 91 body modes every strike rings, each
knock's level and phase per mode measured from the library's release and pedal
recordings and set against the notes at the library's SFZ mix. One 12.5 s
phrase of staccato chords, soft treble notes and pedal moves, with identical
events and controls, level-matched on whole-file RMS (B trimmed by
-0.001 dB). The owner chose B. Chosen by ear: it licenses playing the knocks
at the SFZ's balance, a mixing choice rather than a measured level; no
recorded waveform is played.

## 2026-10-28 — every strike rings the undamped strings, each at its own pitch

The strings from F6 up have no dampers, and a strike sets them ringing through
the bridge, not only those its partials come near. The fit had found them as
peaks of a pitch's residual that recur across the recorded pitches, in a mono
sum, and listed 22; the engine rang each only through the struck key's
nearest partial. Measured instead as tones at each string's own pitch, in
both channels' mean power (a string ringing in anti-phase between the
channels read 16 to 26 dB low in the sum), every recorded pitch from F♯3 up
rings 5 to 19 of the twenty strings clear of the noise around them between 1
and 2 s after contact, 70 % of the times measured.

Each string now has one pitch, the median of its strongest peak in the
recordings from C6 up; one decay, its fall from 1 to 2 s drawn towards the
strings' median; one stereo pickup; and a level per recorded pitch at
velocity 64, with one velocity slope for every string (13.5 dB per 64). Every
strike rings all twenty but its own key's, in the shared bank's top twenty
slots and whatever the Resonance control; they ring on after the key is let
go, and the felt mute damps them. A component the fit finds within 3.5 cents
of a string's pitch is that string and is not played as a component: 95 % of
the peaks taken for a string lie that close to it, while within 15 cents a
fifth of the bass's components fell near some string by chance.

`Tools/compare_ring_levels.py` now measures every string the fit's way, at 1,
2 and 3 s after onset, each sound scaled as the benchmark scales a case. On the
dev cases, the strings that ring clear sit a median 1.6, 0.6 and −1.5 dB from
the recordings (c23b45d: 60.7, 66.3 and 57.0 dB under, most of them never
played), 3.7, 3.5 and 4.5 dB from them on average; 1.7, 2.9 and 8.6 % of them
sit 10 dB or more under (c23b45d: 86.5, 74.2 and 64.9 %), and 5.4, 1.9 and
0.6 % of all the strings measured 10 dB or more over (0.7, 0.3 and 0.1 %).

On the recording benchmark against c23b45d, the treble's sustain spectrum
moves from 8.61 to 7.96 dB on train and from 8.15 to 7.48 dB on dev, its early
spectrum from 5.67 to 5.33 and 5.62 to 5.16 dB, and the bass's partial levels
from 0.75 to 0.64 and 2.19 to 2.11 dB. One note regresses: D♯1's dev onset
rise, 4.68 to 6.03 ms, all from layer 14 (2.67 to 24.48 ms), whose 90 % point
moved from the first peak to a later swell, as at layers 15 and 16; its attack
spectrum is unchanged (5.53 to 5.52 dB). The paired CPU rounds show no change
beyond their spread (`Docs/benchmarks/realtime-cpu-2026-10-27.json`). Chosen
on these measurements, which decide it, not by ear.

## 2026-10-28 — add an upright, fitted from the Helsinki 1967 recordings

The owner asked for an upright beside the grand, chosen with a model switch,
each fitted from the library that records it: the grand from Salamander, the
upright from Mikko Patama's Helsinki 1967 Tube-Ribbon Edition, which the owner
supplied and whose author permits fitting numbers from it provided its
recordings are not distributed. A second library the owner supplied stays a
private check: no number of it is published or fitted. The upright is
measured with the grand's tool from its train recordings
(`Tools/corpus/split-helsinki-2026-10-28.json`) and played by the same
engine; the Piano control and three presets choose it. Switching silences
what sounds, as both pianos' strings, body and noise differ, so Piano is not
offered for automation, and a session saved before it existed keeps the
grand.

Its recordings carry their own levels. One scale sets the upright's median
note at velocity 127 as loud as the grand's, so both pianos' fortissimo
leaves the output the same headroom (the headroom tests play both); below
it the upright keeps the wider span its recordings have, and at velocity 85
its median note is 6 dB under the grand's. A mixing choice, not a
measurement.

The upright plays fewer fitted partials per note than the grand (23 against
34 at middle C, 50 against 76 at C2), and on the engine tests' timing case it
costs about half the grand's CPU: a second of 128 held notes takes 0.86 s of
process CPU against the grand's 1.69 s, and 32 notes 0.26 s against 0.56 s
(`Docs/benchmarks/realtime-cpu-2026-10-28.json`).

## 2026-10-28 — the upright's second takes repeat its first

The upright's split made every second take dev. But 126 of the library's 143
second takes share their first take's hammer impact noise (correlation 0.8
or more from 2 to 12 kHz over the first 30 ms, which differs from strike to
strike), and nine in ten of those sit under 0.15 cents from it over their
first six partials: the first take played back a fraction of a cent off, a
few samples later (`Tools/find_repeated_takes.py`). All but F♯1's softest correlate with
their first take at 0.96 or more over the first half second. A second take
cannot hold out the first take the fit used, so every second take is now
`repeat`, neither fitted nor scored, and the dev role keeps the first takes
of the pitches never fitted: D♯2, G♯3, C5, E6 and B3's one take, 21 cases.
Train is unchanged. Decided on these measurements, after the first fit's
benchmark had scored the second takes.

## 2026-10-28 — a layer that does not hear a component bounds it

A partial or component a velocity layer could not measure, as it did not
stand clear of the recording's floor there, kept the level of the nearest
layer that did. At the upright's softest layer that held C2's partials above
2.4 kHz 30 to 45 dB over a recording that holds none of them, and the line
each pitch's onset rise follows over velocity ran past every layer at its
ends: at A♯6, 8.2 ms at the softest layer, where no layer measured over
3.7 ms, and up to 190 ms in the upright's bass. In such a layer a component
is now no louder than its recorded peak there, carried into the lanes' scale
by the median difference over the layers that measured it, and the onset
line is held within the range the layers measure. Both pianos are refitted.

On the upright's benchmark against its first fit, the onset rise is 9.04 to
6.53 ms from the recordings on train (bass 21.47 to 12.22 ms) and 10.27 to
10.30 ms on dev, the attack spectrum 4.57 to 4.17 dB on train and 6.09 to
5.64 dB on dev, and the early spectrum 4.40 to 4.04 and 6.89 to 6.48 dB. Two
notes regress, both in the rise: C3 on train (10.84 to 13.55 ms) and G♯3 on
dev (12.25 to 14.50 ms), where the recording's envelope reaches 90 % of its
first-150-ms peak on a slow swell 25 to 55 ms after the strike and the
render's now reaches it 12 to 39 ms after. The grand's benchmark moves by at
most 0.05 dB or ms in any register mean, and none of its notes regresses.
Chosen on these measurements, not by ear.

## 2026-10-28 — the upright's felt leaves a share of each partial ringing

The upright's dampers took the grand's felt loss, which takes all of a
partial at hundreds of dB/s, while the library's key-release takes keep part
of each partial ringing after the felt lands. A damped partial now keeps a
share the felt holds only loosely, 10^((a + b x) / 10) of its power with x its
octaves from middle C, falling at e^(c + d x) per second besides its own
decay, and the felt takes the rest as before. Fitted on the 22 train takes
below F6 (`damper_data`, [research note](research/upright-dampers-2026-10-28.md)):
at middle C 13 dB under the partial and falling 6.2 dB/s, each octave up
6.9 dB smaller and 1.43 times faster, and below 71.5 Hz all of the partial.

On the new [release benchmark](validation/upright-release-benchmark-2026-10-28.md)
the releases sit 8.64 to 4.42 dB from the train takes and 8.41 to 6.29 dB
from the four dev takes, never fitted: D♯2 9.85 to 5.03 and G♯3 9.39 to
4.91. Two dev takes regress: C5, 5.81 to 6.61 dB, on partials that lie on
undamped strings, which its take holds far louder than the halo plays them,
and E6, 8.58 to 8.62 dB. Held notes render bit for bit as before, so the
recording benchmark does not move. Released upright passages cost 0.11 to
0.12 of real time where they cost 0.06 to 0.07, as their tails now ring,
against 0.42 for the same chords under the sustain pedal. The grand has no
`measured::Damper`: its release recordings fade in over the damper's first
tenth of a second, so it renders bit for bit as before. Chosen on these
measurements, not by ear.
