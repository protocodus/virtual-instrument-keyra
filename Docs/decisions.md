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

## 2026-10-28 — the treble's own unison strings play beside its partials

From C6 up the upright's unison strings sound 2 to 10 cents from their
partial, where its lanes reach about 3 (`piano_analysis.fit_partial_layers`).
The fit took any component within 15 cents of an anchor's fundamental for
its unison, which it assumed the lanes held, and left it out: the strings
beyond their reach did not sound, and G7's fundamental sat 14 to 30 dB under
the recordings from 0.25 to 1.5 s. Those components now play like any other
beside the series, each one lane at the order nearest it; one within 3.5
cents of another key's undamped string is still that string. The upright
gains 13 components from C6 to G7, the grand three, at F♯6, A6 and C7.

On the [upright's benchmark](validation/upright-unison-benchmark-2026-10-28.md)
the treble's train partials sit 4.88 to 3.88 dB from the recordings, their
decay 5.06 to 3.54 dB/s and the sustain spectrum 10.55 to 9.17 dB; at the
never-fitted E6, between the recorded pitches, 8.86 to 7.75 dB, 13.90 to
12.34 dB/s and 15.11 to 12.43 dB. G7's fundamental now sits within 0.4 to
9 dB of the recordings over those windows, except at the softest layer,
still 17 to 21 dB under. The bass and middle do not move. The new components
have no rise of their own and start under the pitch's shortest, so the onset
fit lengthens that for every partial where they are loud: D6's goes from 0.2
to 19.8 ms, and its attack spectrum moves 0.36 dB, within tolerance. C7's,
refitted with its new components, goes from 2.3–2.4 to 4.0–4.3 ms, and its
onset rise regresses on train, 0.44 to 1.82 ms from the recording. On the
[grand's](validation/grand-unison-benchmark-2026-10-28.md) the dev treble's
tuning moves 1.68 to 1.26 cents and the train treble's decay 3.90 to
3.82 dB/s; D♯7's stereo balance regresses on dev, 2.18 to 2.69 dB, as it
interpolates C7's new component. Three-note chords every 0.15 s from C6 to
C8 under the sustain pedal, 6 s of them, render 1.6 % slower on both pianos
(the median of seven paired rounds: upright 4.31 to 4.38 s, grand 5.55 to
5.64 s). Chosen on these measurements, not by ear.

## 2026-10-28 — no two strikes land alike

The owner heard Pop Upright's repeated chords as mechanical and asked for
every key press to differ a little, in velocity and perhaps in tuning. Of the
upright library's 143 second takes, 17 are new strikes rather than copies
(above); 13 are at train pitches, and twelve of those have layers whose
levels read a velocity, a slope of 0.1 dB per unit or more. Each differs from
its first take as a velocity change does: by a median 5.4 velocity units at
its layers' level slope (about 1 dB), ten of the twelve brighter where louder
over their first eight partials, and in pitch by a median 0.02 cents
(`Tools/find_repeated_takes.py`). Each strike now moves its key's velocity by
a draw of spread 5.6, the median absolute difference over 0.6745 and the
square root of two; tuning does not vary. The draw sums four uniform ones, so
it stays within 3.5 spreads, and its sequence restarts with the engine and on
a piano switch, so a render replays exactly. `keyra_render`, and so every
benchmark, strikes at the velocity exactly unless given `--vary`. Nine of the
twelve strikes are at the softest layer, and the spread plays at every
velocity and on the grand, whose library holds one take of each note.
Measured, at the owner's request; Pop Upright's before/after went to the
owner. On 2026-10-29 the owner adopted the spread under their standing rule
that a lettered candidate wins over the shipping engine unless they say
otherwise; no listening verdict was reported.

## 2026-10-28 — one velocity response for both pianos

A Recon check of the Rack device found the upright's chords growing about
12 dB from velocity 96 to 127 where the grand's grew 5. The engine followed
each library: every layer sits within 0.2 dB of its recordings (median), and
the libraries map velocity differently, the Helsinki library putting its two
loudest layers at 100–127 where Salamander spreads sixteen evenly. The owner
asked for one response for every piano, "something between linear and
sigmoid". A velocity v now asks for a level under the loudest recorded layer,
floor × (1 − (x + smoothstep(x)) / 2) with x = (v − 1) / 126, and plays the
layer coordinate where the piano's measured layer levels reach it: each
layer's early level under its pitch's loudest (both channels' RMS 50–750 ms
after the onset), the median over the pitches recorded at every layer, from
−21.2 dB for the grand and −27.2 dB for the upright. The floor is the higher
of those, so neither piano plays outside what it recorded: velocity 1 plays
the grand's softest layer, which the upright reaches between its two
softest, and velocity 127 each piano's loudest, where it used to play past
it. The strike spread moves the layer coordinate as before. The upright's
output scale goes from .502 to .642, so that its median note at velocity 127
stays as loud as the grand's.

Over every key A0–C8 (RMS 50–750 ms, no spread), the median notes now sit
within 1 dB of each other at velocities 1, 32, 64, 96 and 127, where they sat
7.0, 8.7, 9.9, 4.5 and 0 dB apart, and from velocity 64 to 127 the median key
grows 10.6 dB on the grand and 9.9 dB on the upright (8.4 and 17.4). Single
keys keep their recordings' differences: a key of the upright sits from 4 dB
under to 7 dB over the same key of the grand (the tenth to the ninetieth
percentile). The upright's softest layer no longer plays on its own. The
benchmarks strike at layer coordinates and do not move: their grand renders
are bit-identical and their upright renders scale by the new output scale
alone. The shape is the owner's choice, not a measurement. A lettered chord
ramp went to the owner on both pianos: the shipping response, this halfway
shape, a straight line and smoothstep, with the key beside them. On
2026-10-29 the owner kept the halfway shape that ships, the shape they had
asked for, under their standing rule that a candidate wins over the old
response; no listening verdict was reported.

## 2026-10-28 — a partial's lanes reach its farther unison strings

From C6 up the upright's unison strings sound 2 to 20 cents from their
partial, where a partial's lanes reached about 3 cents
(`piano_analysis.fit_partial_layers`). The strings beyond played as one-lane
components beside the series (above), and G7's fundamental fitted two lanes
at those bounds that fell 40 dB in half a second, between strings that ring
on for two. Where a fitted lane now settles within 2 % of its bound, the
partial is fitted again with lanes up to 0.6 % of its frequency out (about 10
cents), seeded also from the components its layers' envelopes resolve from
0.5 s and keeping the first fit's rise, and the fit of lower cost is kept.
A partial whose lanes reach further keeps the residual's peaks within its
furthest lane out of the components beside it. 131 of the grand's partials
and 120 of the upright's are refitted, all but six of them above 1 kHz; the
grand plays 206 components beside its series instead of 217, the upright 53
instead of 74.

On the [upright's benchmark](validation/upright-lane-reach-benchmark-2026-10-28.md)
the never-fitted E6's partials sit 7.75 to 6.83 dB from the recordings, their
decay 12.34 to 8.23 dB/s, the sustain spectrum 12.43 to 10.10 dB and the
envelope 9.04 to 6.46 dB; the train treble's decay 3.54 to 2.16 dB/s and its
sustain spectrum 9.17 to 6.93 dB, and D6's shortest onset rise returns from
19.8 ms to 0.2–4.3 ms. Its 24 regressions are listed there, among them the
stereo coherence of A♯6 and C6, the onset rise at C1, A1, A2, A♯6 and C6, E6's
stereo balance, 2.94 to 4.67 dB, and E7's level, 3.54 to 5.77 dB: from 0.05 to
0.75 s E7 sits 3 to 5 dB under its recordings, as the fit weighs its quiet
tail as much as its start. On the
[grand's](validation/grand-lane-reach-benchmark-2026-10-28.md) the
never-fitted treble's decay moves 4.48 to 3.29 dB/s, its sustain spectrum
7.30 to 7.15 dB, its stereo balance 1.93 to 1.62 dB and its tuning 1.26 to
1.86 cents; the train treble's decay 3.82 to 3.56 dB/s, its sustain spectrum
7.86 to 8.13 dB and its envelope 2.82 to 3.39 dB. Its 17 regressions are
listed there, F♯6's first: its envelope 2.16 to 5.29 dB and its sustain
spectrum 4.84 to 7.00 dB from the train recordings. Its refitted fundamental
follows the recordings' complex envelope more closely (relative error 0.24 to
0.20), but where their level holds or rises from 0.75 to 1 s it keeps
falling, and sits 6 to 8 dB under them from 1 to 1.5 s. Three-note chords
every 0.15 s from C6 to C8 under the sustain pedal, 6 s of them, render
25.5 % faster on the upright (4.28 to 3.19 s) and 6.0 % slower on the grand
(5.60 to 5.93 s), the median of seven paired rounds. Chosen on these
measurements, not by ear.

A forward weight, each frame weighed by the envelope's largest value over the
next two beats rather than around it, was tried on the upright with the wider
reach and not kept: its never-fitted partials moved 5.86 to 6.67 dB, the
sustain spectrum 7.76 to 8.56 dB and the envelope 5.00 to 5.88 dB, and only
the decay improved, 4.27 to 3.50 dB/s.

## 2026-10-28 — a blended partial keeps its two pitches' power

A key between two recorded pitches blends each partial's four lanes one by
one (`blendLane`): rate, offset and level between the two pitches', phase
from the nearer, stereo pickup between theirs. A partial's lanes beat against
each other, so the power of their sum turns on all of these together, and the
blend's combination is one neither pitch has: on the grand B4 played 3.5 to
4.4 dB under both A4 and C5 at every velocity and A♯6 up to 4.6 dB over both
A6 and C7, and on the upright B3 played 3 to 4.7 dB under both F♯3 and C4.
`blend` now computes a partial's heard power, every pair of its lanes with
their amplitudes, phases and pickups integrated in closed form against
e^(−t/0.4 s) from contact, for both pitches and for the blend, and moves the
blend's lanes together so its power sits at the two pitches' mixed in dB, as
the lanes' levels are. 0.4 s is the mean time of the 50–750 ms window the
layers' levels are measured over; the rise the lanes share is left out.
Recorded pitches play as before, to the bit.

Over every key at the layer coordinates velocities 1, 32, 64, 96 and 127 ask
for (both channels, 50–750 ms), the keys more than 1 dB outside the levels of
the two recorded pitches around them go from 8–16 of the grand's 63 to 1–4
and from 8–18 of the upright's 52 to 3–5; the furthest goes from 4.6 to
2.6 dB on the grand and from 4.7 to 2.8 dB on the upright. A new engine test
holds every such key within 3 dB of its neighbours' levels at one layer
coordinate on both pianos: 4.2 dB before, 1.7 dB now.

On the [grand's benchmark](validation/grand-between-pitches-benchmark-2026-10-28.md)
the never-fitted pitches between recorded ones, D♯1, D♯3, D♯5 and D♯7, sit
0.39, 0.80, 0.03 and 0.61 dB closer to their recordings' level; the dev cases'
level moves 1.29 to 1.10 dB and their partials 3.20 to 3.13 dB, with no
regressions. On the [upright's](validation/upright-between-pitches-benchmark-2026-10-28.md)
D♯2 sits 0.34 dB closer and G♯3, B3, C5 and E6 0.92, 0.75, 0.27 and 0.30 dB
further; the dev cases' level moves 2.25 to 2.56 dB and their partials 5.86
to 5.97 dB, and its nine regressions, at G♯3, B3 and C5, are listed there.
The upright's recorded levels are uneven from note to note: C4 sits 3 to
7.5 dB over the line through F♯3's and D4's levels at every layer, and F♯5 3
to 9 dB under E5's and A♯5's. G♯3 and B3 lie between F♯3 and C4, and there
the old blend happened to stray from the two pitches' levels the way their
recordings do, over at G♯3 and under at B3; a blend's beating says nothing
about a note's own level, so it is not kept for that.
Three-note chords every 0.15 s under the sustain pedal, 6 s of them, render
within 1.2 % of before on both pianos, from C6 to C8 and from A0 to B4 (the
grand 6.02 to 6.07 s and 27.17 to 26.88 s, the upright 3.17 to 3.21 s and 7.37
to 7.42 s), the median of seven paired rounds. Chosen on these measurements,
not by ear.

## 2026-10-28 — a strike's spread is in level

The strike spread (above) moved a strike's layer coordinate by 5.6 velocity
units, and a velocity unit is worth what the layers' level slope makes it: the
upright's levels climb about twice as steeply between its two loudest layers
as between the layers the spread was measured at, and the grand's softest
layers climb steeply too. Read on Reason's channel meter (the louder channel's
RMS over 300 ms), single notes every fourth semitone and eight chords at
velocities 50 to 127 strayed from the steady strikes' readings by an RMS 1.4
to 2.3 dB on the upright, the most at velocity 120, and by 2.2 dB on the grand
at velocity 50, where the same twelve new strikes differ from their first
takes by a median 1.04 dB in early level (`find_repeated_takes.py`'s
`touch_spread_db`). A strike now moves the level the velocity response asks
for by a draw of spread 1.085 dB and plays the layer coordinate where the
piano's measured layers reach that level, continuing the end layers' slopes
beyond them. It strays by an RMS 1.1 to 1.5 dB on the upright and 0.8 to 1.3
dB on the grand, at every velocity; the eight chords grow a median 1.9 dB on
the upright from velocity 110 to 127, where they grew 1.6 dB and one read 0.5
dB quieter. The draws are the same, so a render still replays exactly;
`keyra_render` and so every benchmark strike steadily and do not move.
Measured, not chosen by ear.

## 2026-10-28 — typical playing at −9 VU, behind the portfolio's output stage

The owner asked for every new instrument to play "just right - not too loud,
not too silent". Keyra played 11.5 dB under the portfolio's newer
instruments: typical playing on the default controls read −20.5 VU on
Reason's channel meter (the louder channel's RMS over 300 ms, 0 VU at
−12 dBFS), where Aculele and Aculyre read −9 VU, the owner's choice for them.
`Tools/KeyraLevels.cpp` now reads every factory preset on that meter: single
notes every fourth semitone and eight chords at velocities 70, 90 and 110
for typical playing, the median over them, and the chords at 127 for the
loudest. Each piano's output scale brings its default sound's typical playing
to −9 VU (the grand's .21 to .7887, the upright's .642 to 2.387, both
+11.5 dB, so the upright's median note at velocity 127 stays within 0.1 dB of
the grand's).

At that level the eight chords at velocity 127 would read up to +1.3 VU on
the grand and +5.9 VU on the upright, peaking 1.0 and 5.8 dB over full
scale, so the clip at full scale gives way to the portfolio's shared output
stage
(`Source/DSP/OutputStage.h`) with the guard the newer instruments use
(`kVuGuard`: power over the meter's 300 ms, a knee from −11 to +5 VU, 10:1),
then a look-ahead limiter at −1.5 dBFS with 2 ms of latency, which the
plug-in reports and `keyra_render` compensates. Single notes pass it
untouched, a median 0.04 dB at velocity 110. Chords lose a median 0.5 and
1.4 dB on the grand at velocities 90 and 110, 0.9 and 3.0 dB on the upright;
at 127, 2.0 dB on the grand and 4.7 dB on the upright, whose middle register,
where the chords sit, is hotter than the grand's. The loudest chords read
−0.6 VU on the grand and −0.2 VU on the upright, and a chord at velocity 127
still reads louder than at 110, by a median 0.2 dB on the grand and 0.3 dB
on the upright through the guard, where it reads 0.6 and 2.7 dB louder
without it. The presets without felt read −10.8 to −7.8 VU; the felt presets
read about 8 dB lower (Felt Nocturne −17.5 VU, Felt Upright −16.5 VU) and are
left there: the felt stops each note within a fraction of a second, so the
meter's 300 ms holds less of it, while its attacks peak as high as the
others' and raising them would press every hard note into the limiter. The
audio-tier test `Keyra.Levels` holds these readings.

The measurements render 20 dB under the default Output, where the stage
passes every strike untouched (`benchmark_recordings.MEASURE`): both
benchmarks score within 0.001 dB of before, with no regressions. The
upright's dampers leave part of each partial ringing (above), so at the new
level its released chords reach the matrix's −60 dBFS floor 2 s after the
keys go up and 3 s at full Output; `Keyra.ParameterMatrix` allows the upright
presets 3 s. The level and the stage are the portfolio's, chosen by
measurement; whether the guard's cost to the hardest chords is worth keeping
them out of the red is the owner's to hear. A lettered crescendo of chords on
both pianos went to the owner, level-matched: the shipping engine, this
stage, and the same level through the limiter alone, with the key beside
them. On 2026-10-29 the owner kept the stage that ships, guard and limiter,
under their standing rule that a candidate wins over the old output; no
listening verdict was reported.

## 2026-10-28 — a Quality choice leaves out what no band hears

The owner asked every new instrument for a quality setting ("oversample 1x
2x 4x"). Keyra plays each partial as its own oscillator and silences any
above 0.45 of the sample rate, so it has nothing to alias and oversampling
would cost CPU for nothing. On the decision card the owner chose instead a
Quality choice that sets how much of each note plays, trading detail for CPU
on slower machines, with the full sound as the default.

A strike's slots (a partial's four lanes, or four of the components beside
the partials) cost alike, and many play far under the strike's strongest:
over every key at velocities 40, 80, 110 and 127 a grand strike plays a mean
43.1 slots and an upright strike 24.2. Balanced and Light keep only the
slots that come within 60 and 50 dB of the strike's strongest, at contact
(the sum of their lanes' amplitudes) or over their whole ring with the key
held (their lanes' energy to silence), each at its brightness tint; the
second test keeps a quiet partial that rings long. The grand then plays 26.5
and 21.5 slots a strike and the upright 21.6 and 19.4. Over every third key
from A0 to C8 at those velocities, 3 s of each, no third-octave band within
40 dB of the note's strongest moves by more than 0.04 dB at Balanced (the
grand's D♯3 at velocity 80) or 0.74 dB at Light (its A6 at 127), and the
median note's largest change is under 0.001 dB at both. At 40 dB a soft bass
note's band from 1 to 4 kHz, 35 to 40 dB under its strongest, lost up to
27 dB, so no lighter setting is offered. On this development machine's
process CPU (`Docs/benchmarks/quality-cpu-2026-10-28.json`), twenty legato
chords under the pedal take 49 % of Full's at Balanced and 38 % at Light on
the grand, 95 and 87 % on the upright; fast chords under the pedal take 61
and 48 % in the grand's bass and 90 and 74 % in its treble, while the
upright's treble saves nothing. `Keyra.Engine` holds the four
keys whose bands changed the most.

Chosen by measurement. Whether Light's largest change can be heard is the
owner's to judge: a lettered passage on both pianos, the shipping Full
against Balanced and Light, went to the owner level-matched with its key. On
2026-10-29 the owner kept all three settings, Full the default, under their
standing rule that candidates win; no listening verdict was reported.

## 2026-10-29 — the noise score counts what either sound puts over the recording's floor

The benchmark scored a band's noise between the partials where the
recording's noise alone stood within 40 dB of its loudest. At a soft note that
took the recording's own hiss, level to 20 kHz, for the piano's noise, and it
left out any hiss a render added over a band the recording keeps quiet. A
band now counts as it does in the band scores: where either sound stands
within 40 dB of the recording's loudest and 10 dB above the recording's
floor. Scored again under it, the engine at 98c6740 sits 6.90 dB
from the grand's train recordings and 6.31 dB from its never-fitted ones
(5.56 and 5.62 under the old rule), and 7.08 and 7.53 dB from the upright's
(8.93 and 9.73); 0.3.0 sits 24.7 dB from the grand's never-fitted
recordings, where the frozen 0.4.0 report, under the rules of its day, scored
it 25.9. The README's comparison with 0.3.0 now comes from both versions
scored by the benchmark as it stands
(`Docs/validation/grand-recording-benchmark-2026-10-29.md`).

## 2026-10-29 — the board noise under a top note passes over other strings' tones

Through the upright's top octave each strike left a hiss ringing on for
seconds. The fit measured each noise band as the mean power of its bins
between the partials, and in the bands centred below the struck note's
fundamental, where none of its own partials lie, those bins also hold other
strings' tones: chiefly the undamped treble strings' detuned unisons, which
the engine rings at one pitch each and which a one-pitch fit leaves partly in
the residual (B6's span 1957 to 1992 Hz). The mean took them for noise
decaying at their rate: the upright's 2 kHz band after C7 fell at 2 per
second (17 dB/s), where the noise between them falls at 20 (174 dB/s). In
those bands a frame's density is now the median of the band's bin powers
over ln 2 (a noise bin's power is exponential, whose median is ln 2 times its
mean, and the median passes over the few bins a tone holds), each channel's,
then the channels' mean, so that the result does not depend on how alike the
channels are.

Only the bands below a fundamental change, from C6 up. The upright's 2 kHz
band now starts 9.7 dB louder at C7 and falls 17 dB in a tenth of a second
instead of ringing on (its decay rate 2 to 20 per second at C7, 4 to 18 at
E7, 9 to 21 at G7); the grand's bands moved by −3.4 to +1.7 dB at contact,
in the mean over the layers, and their decays by at most 4 per second. On the upright's train recordings from C6 up
the spectrum sits 0.21 dB closer to the recordings from 0.1 to 0.5 s and
0.12 dB closer from 0.5 to 3 s, at C7 1.6 and 0.9 dB closer; on the grand's
it sits 0.05 to 0.10 dB further in the attack and the early spectrum, where
its attack already sits under the recordings from 400 Hz to 3 kHz
([grand](validation/grand-treble-noise-benchmark-2026-10-29.md),
[upright](validation/upright-treble-noise-benchmark-2026-10-29.md)).

Three regressions. The grand's F♯7 onset rise moves from 3.6 to 5.7 ms from
its recordings (3.55 to 5.86 on the never-fitted takes): at its softer layers
the envelope rises through ripples within a decibel of its peak, so a
fraction of a decibel moves its first 90 % crossing by tens of milliseconds.
At velocity 14 the first ripple, at 4 ms, falls from 0.6 to 1.1 dB under the
peak, past the 90 % line, and the measured rise goes from 4.7 to 27.5 ms (the
recording's 10.8). The upright's G7 noise moves from 5.85 to 6.62 dB:
through its first 0.6 s the recording holds a tone at 3.0 kHz, where F♯7's
undamped string sounds (2989.5 Hz), 14 to 15 dB under G7's fundamental and
falling with it at about 50 dB/s. The engine plays that string more than
30 dB under, at a level measured from 1 to 2 s and brought back to contact at the
strings' median 19 dB/s; the mean had measured the tone as slow noise in the
3.2 kHz band and so stood in for the string.

Rejected: the median in every band, under which the upright's 12.7 kHz band
went silent and E3's 8 kHz band fell 16 dB further under its recording,
since above a fundamental the residue between the partials is mostly the
note's own unresolved partials, which have no other voice than the noise;
and the median everywhere but above the highest partial, under which the
bass and middle registers' noise sat up to 1.2 dB further from the train
recordings.

Chosen by measurement; the owner's standing direction is to adopt such
candidates. A short lettered passage on both pianos, the shipping engine
against this fit, went to the owner level-matched with its key. On 2026-10-29
the owner adopted the candidate under their standing rule that a lettered
candidate wins over the shipping engine unless they say otherwise; no
listening verdict was reported.

## 2026-10-29 — a strike's knock grows with the level its layer plays at

Soft notes knocked the body too loud. Each body mode's knock was a line in
velocity (dB against (v − 64)/64), weighted by each layer's power, so the
loudest layers set it; in velocity the knocks' levels curve down toward the
softest layers, and the line played the softest layer's knock a median 5.9 dB
(grand) and 5.0 dB (upright) over its recordings, summed over the modes.
Against the level the strike's layer plays at (the fit's layer levels, 0 dB
at the loudest) the knocks lie on a line, a median 0.93 dB per dB on the
grand and 0.96 on the upright: the body is knocked as hard as the strings
are struck. Each mode's level is now a line in that level, weighted by the
knock's amplitude, and the engine reads the layer level at the strike's
velocity as the strings' levels do. The softest layer's knock sits 1.1 and
0.8 dB over its recordings.

The weighting was chosen on the knocks' third-octave band levels, each layer
predicted by a line fitted without it (the median over the anchors of the
mean error over the bands within 30 dB of the loudest, averaged over the
layers between the softest and the loudest): 1.85 dB on the grand and 3.78 on
the upright for the line in velocity, 1.63 and 2.57 for a line in the layer
level weighting every layer alike, 1.41 and 2.81 weighted by amplitude.
Weighting every layer alike was tried first: it lets the soft layers pull the
loudest layer's band levels a median 2.0 dB off on both pianos (1.0 and 0.5
under the shipping line, 1.3 and 0.7 under this one), and on the benchmark it
played the louder layers' attack up to 0.6 dB further from their recordings
and moved the grand's train level from 0.54 to 0.66 dB. A quadratic in the
layer level predicted the left-out layers within 0.1 dB of the line inside
the recorded layers and far worse past them (the softest, left out: 4.4
against 3.5 dB on the grand, 11.3 against 5.9 on the upright).

On the recording benchmark against the shipping engine (39032f0) the attack
spectrum sits 0.12 dB (grand) and 0.43 dB (upright) closer to the train
recordings and 0.05 and 0.22 dB closer to the never-fitted ones; the
upright's early spectrum 0.33 and 0.23 dB closer, its noise between partials
0.22 and 0.34, and its level 0.07 dB closer on the train notes; the grand's
level 0.04 dB further
([grand](validation/grand-knock-benchmark-2026-10-29.md),
[upright](validation/upright-knock-benchmark-2026-10-29.md)).

Nineteen regressions. The grand's noise score at F♯3, A3 and C4 (8.16 to
9.63 dB, 7.44 to 8.56 and 6.03 to 6.70 on the train takes, 9.05 to 10.45,
6.62 to 7.46 and 6.15 to 6.69 on the never-fitted), up to 6 dB at the
softest layers, lies wholly in the 25 Hz band (22 to 28 Hz). The recordings
fill it 6 to 22 dB over their floor, growing more slowly than the strings,
under the lowest body mode (29.3 Hz), so the engine plays nothing
there but that mode's skirt; the louder knock had covered part of it. C8's
level moves from 3.05 to 3.88 dB: C8 already sat 2.5 to 6 dB under its
recordings from its softest layer to velocity 61, and its softest layer's
knock had covered part of that (2.5 to 7.7 dB under). The upright's
A♯6 sustain moves from 5.21 to 6.20 dB: at its two softest layers the knock
had carried up to 58 % of the render's power from 50 to 750 ms, by which the
benchmark matches the recording's level, so the strings are now scaled
3.8 dB further up. Its noise scores at A2, C3 and D3 (5.71 to 7.84, 8.24 to
9.61, 11.74 to 12.47) each rest on one or two time cells of a band near the
recording's floor, far above the knock's modes (2 kHz at C3's softest layer,
6.3 kHz at A2's third); its G♯6 and C7 interchannel coherence moves by 0.06
and 0.02. Six onset-rise scores move between two crossings of a rippling
envelope (the grand's C3 and F♯2 on the never-fitted takes, 7.27 to 10.73 ms
and 7.51 to 9.96; the upright's A1, C1, F♯2 and A♯5, 13.90 to 21.87, 13.54
to 19.67, 4.46 to 5.90 and 5.28 to 6.45).

Chosen by measurement; the owner's standing direction is to adopt such
candidates. A short lettered passage of soft strikes on both pianos, the
shipping engine against this fit, went to the owner level-matched with its
key. On 2026-10-29 the owner adopted the candidate under their standing rule
that a lettered candidate wins over the shipping engine unless they say
otherwise; no listening verdict was reported.

## 2026-10-29 — each undamped string starts with its own prompt part

The undamped strings from F6 up started at the level their fall from 1 to 2 s
brings back to contact. In the recordings they stand far over that line in
the first half second, and the strings that ring clear sat a median 8.0 dB
over the engine at 0.125 s and 4.8 dB at 0.25 s on the grand's train notes
(7.8 and 4.8 on its never-fitted ones), 5.0 and 7.8 dB on the upright's
(9.5 and 10.9), measured as `Tools/compare_ring_levels.py` measures them:
quarter-second windows where a string lies 60 Hz or more from every partial
of the struck key. A struck unison first sounds a prompt part that the bridge
drains fast, then its aftersound (Weinreich, "Coupled piano strings", 1977),
and the strings a strike sets ringing do the same. Each now starts with a
second resonator at its frequency, phase and pickup. Its level over the
string's own at contact is the string's own; its decay, 103 dB/s on the grand
and 75 dB/s on the upright, is shared, fitted on every window where a string
rings clear. A string's level is measured in the early windows of the layers
where it rings clear from 1 to 2 s, as its excess over its own line there: a
window where it rings clear measures it and one where the strike's noise
hides it bounds it from above (a censored fit), and each level is drawn
towards the strings' median by ten layers' worth of windows, as their rates
are. On the grand they run from too little to hear (nine strings at −24 dB
or less) to 25 dB (C7), on the upright from −26 dB (C7) to 17 dB (B6).

At 0.125 s the strings that ring clear now sit a median 4.0 dB under the
grand's train recordings and 2.7 dB under its never-fitted ones (mean
absolute error 7.7 to 4.7 dB and 7.4 to 4.6), and 1.8 and 6.4 dB under the
upright's (6.7 to 5.2 and 9.4 to 8.0); at 0.25 s 3.1, 2.2, 4.5 and 7.7 dB
under. The strings that ring 10 dB or more over the recordings at 0.125 s,
counted at every string the windows can see, go from 0.7 to 1.0 % on the
grand's train notes and 4.5 to 5.7 % on its never-fitted ones, 7.8 to 11.6 %
and 5.5 to 10.5 % on the upright's. Nothing changes from a second on.

Rejected, each scored the same way:

- One prompt part shared by every string, fitted on the clear windows (20 dB
  on the grand, 10 dB on the upright). It met the clear strings' median (0.1
  dB over on the grand's train notes), but those are the strings that ring
  loud early: strings the noise hides early, which come clear only later (on
  the grand B6, C♯7 and G7 among them), rang 10 dB or more over the
  recordings at 0.125 s at 8.9 % of the grand's train strings and 19.6 % of
  its never-fitted ones, 15.3 and 11.3 % of the upright's. On the benchmark
  it played the grand's never-fitted bass notes noisier (7.37 to 7.58 dB).
- Each string's own level, not drawn towards the others. Closest on the
  grand (2.8 and 1.2 dB under at 0.125 s), but the upright's strings that one
  to ten strikes measure (D7, E7, F♯7, A7) came out 21 to 24 dB, and the
  upright's never-fitted notes rang 17.2 % of their strings 10 dB over.
- Each string's level against what the engine plays at every strike, every
  layer counted. The soft layers, where one velocity slope already rings these
  strings too loud (README, Known gaps), held the prompt parts at nothing for
  17 of the grand's 20 strings, which left its never-fitted strings 5.3 dB
  under at 0.125 s.
- A free decay in the censored fit: the decay and level trade against each
  other, and the fit ran off (51 dB falling at 184/s for one shared part).

On the recording benchmark against the shipping engine (bd11277) the grand's
treble early spectrum and noise between partials sit 0.05 to 0.06 dB closer
to its train and never-fitted recordings, with no regressions
([grand](validation/grand-halo-prompt-benchmark-2026-10-29.md)). The upright
barely moves and has one regression
([upright](validation/upright-halo-prompt-benchmark-2026-10-29.md)): F♯3's
noise score on the train takes, 9.87 to 10.54 dB, at its softest layer, whose
1.6 kHz band already sat 17.6 dB over the recording, where one velocity slope
plays the strings too loud at soft strikes, and now sits 22.4 dB over for the
first 0.3 s.

`Keyra.Engine`'s check of the board noise under each recorded pitch's first
100 ms read every bin's mean, which the prompt parts' tones raise in bands
below the note's fundamental, where they lie and none of its own partials
can. It now reads those bands as the fit does, each frame's and channel's
median bin over ln 2, which passes over the tones: the check's limit is
unchanged, and the shipping engine passes it read this way too.

Chosen by measurement; the owner's standing direction is to adopt such
candidates. A short lettered passage on both pianos, the shipping engine
against this fit, went to the owner level-matched with its key. On 2026-10-29
the owner adopted the candidate under their standing rule that a lettered
candidate wins over the shipping engine unless they say otherwise; no
listening verdict was reported.

## 2026-10-29 — the undamped strings grow with the strike, fitted with hidden layers as bounds

Soft strikes rang the undamped strings from F6 up too loud. One slope in
velocity served every string, fitted on the layers where a string rings clear
from 1 to 2 s, and in soft layers only the strings that ring loudest do, so it
came out about a quarter too shallow and soft strikes rang strings the
recordings leave under the noise. Measured as `Tools/compare_ring_levels.py`
measures them, at their two softest layers the grand's never-fitted notes rang
17 and 25 % of these strings 10 dB or more over the recordings at 1 s, and the
upright's F♯3 at velocity 51 rang G♯6 27.6 dB over.

The fit now reads every layer of a pitch and string that rings clear in two or
more of them: a layer where the string rings clear measures its level, brought
back to contact at its rate, and one where the noise hides it bounds it from
above at its 1 s tone, with one spread for every layer (a censored fit). The
level grows in dB per dB of the level the strike's layer plays at, as the
knock's does, and the slope rises with the octaves the string lies over the
struck fundamental, as a harder strike is brighter: 1.48 dB per dB and 0.38
more per octave on the grand, 1.39 and 0.47 on the upright. Over those
strings' layers the censored fit's negative log-likelihood is 2478.0 (grand)
and 548.2 (upright) with velocity as the regressor, 2427.6 and 551.8 with the
layer level and 2184.1 and 518.4 with the rise, one parameter more. A string
hidden in all but one layer of a pitch sits 10 dB under its median bound,
brought to the loudest layer at that slope, but never over its tightest: the
steep slopes of the high strings bring the soft layers' bounds so far up that
the median alone played 40 % of these strings over their own recording in the
grand's three loudest layers and 45 % in the upright's.

At 1 s the strings ring 10 dB or more over the grand's never-fitted recordings
at 2.7 % of them (6.0 % before), none and 6 % at the two softest layers, and
over its train recordings at 1.5 % (2.2); the upright's at 0.7 % of its train
strings (2.5), and F♯3's G♯6 1.7 dB over. At 0.125 s, prompt parts included,
4.1 % of the grand's never-fitted strings ring 10 dB over (5.7) and 5.5 % of
the upright's (10.5). The strings that ring clear sit a median 1.2 dB over the
grand's never-fitted recordings at 1 s (1.8), mean absolute error 3.7 dB
(3.8), and 5.7 dB under the upright's (7.9), 8.7 dB (10.3). The upright's
never-fitted pitches ring 16 of their 295 strings 10 dB or more over at 1 s,
where one rang: at the two loudest layers of G♯3, B3, C5 and E6 the pitches
around them set a hidden string at its tightest bound, which those notes'
recordings hold under.

Rejected, each scored the same way:

- The censored slope in velocity (dB per 64). The soft layers came right, but
  in velocity the layers' levels curve, and the loudest layers rang 19 % of the
  grand's never-fitted strings at its loudest layer 10 dB over at 2 s (8 %
  before).
- The slope in the layer level with no rise. Soft strikes came right on both
  pianos, and on the benchmark it had no regressions, but the steeper slope
  brought hidden strings' median bounds up: at the loudest layer 11 % of the
  grand's never-fitted strings rang 10 dB over at 1 s, against 3 % before and
  with the rise.
- The rise with each hidden string 10 dB under its median bound. Over F♯3
  the upright's C8 string grows 3.5 dB per dB, which brings the soft layers'
  bounds up so far that at its loudest layer 31 % of its train strings and
  47 % of its never-fitted ones rang 10 dB over at 1 s.
- The rise with each hidden string 10 dB under its tightest bound. Nothing
  rings over, but the pitches between such a string and one ringing clear
  play it too quietly: on the upright the strings that ring clear sat a median
  11.4 dB under its never-fitted recordings at 1 s (7.9 before), half of them
  10 dB or more under, and 9.3 dB under its train recordings at 0.25 s (4.5).

On the recording benchmark against the shipping engine (badc9d7) the grand
barely moves and has no regressions; its train treble's early and sustain
spectra sit 0.08 and 0.07 dB further from the recordings
([grand](validation/grand-halo-velocity-benchmark-2026-10-29.md)). The
upright's noise between partials sits 0.09 dB closer to its train recordings
and 0.10 dB to its never-fitted ones, and F♯3's at its softest layer 11.30 dB
from the recording, where it sat 19.21
([upright](validation/upright-halo-velocity-benchmark-2026-10-29.md)). One
regression: A1's noise score on the train takes, 7.26 to 7.95 dB, from its
velocity-51 layer, where the score counts the 2.5 kHz band in four time cells
under the shipping engine and in one under this fit. The strings no longer
lift the render's band over the count's threshold in the other three, and the
one left, where the board noise sits 12.7 dB over the recording, decides it.
Below F♯3 no recorded pitch measures the strings, so a bass note's strings
take F♯3's levels and the rise runs on past the 4.5 octaves the fit saw; A1
is the only bass note the benchmark moves by more than its tolerance.

Chosen by measurement; the owner's standing direction is to adopt such
candidates. A short lettered passage of soft and hard strikes on both pianos,
the shipping engine against this fit, went to the owner level-matched with
its key. On 2026-10-29 the owner adopted the candidate under their standing
rule that a lettered candidate wins over the shipping engine unless they say
otherwise; no listening verdict was reported.

## 2026-10-29 — the board's ring under a treble fundamental falls in two stages

Asked whether the grand sounds full across the spectrum, the per-band
comparison of the train and dev renders with their recordings (gain-matched
as the benchmark does) found the bass and middle within about half a
decibel from 80 Hz up after the attack, and one large gap: under the
fundamentals from C6 up, where the board's ring sounds with none of the
note's own partials, the 1 to 1.6 kHz bands sat 4 to 52 dB under the
recordings from 0.1 to 0.8 s after contact, the gap growing with time, and
the 2 and 2.5 kHz bands 5 to 16 dB under. The recordings' ring there falls in
two stages, 100 to 170 dB/s over the first tenth of a second and then 40 to
60 dB/s, and the fit drew one line through the first 120 ms, which the engine
played on at 110 to 230 dB/s, 30 to 60 dB down by a quarter of a second.

Under the fundamental the fit now draws a second line through the frames
every 10 ms from 0.15 to 0.6 s that stand 10 dB over the floor, and refits
the first on the early density less the second's power; the second stage is
kept only where it is the slower, starts 3 dB or more under the first and
both lines have ten frames. The grand measures it from C6 to A7, at 39 to
57 dB/s starting 9 to 20 dB under the first; the upright from C6 to G7, at 18
to 58 dB/s starting 15 to 46 dB under. Each burst plays the two stages
adding in power; between a pitch that measures the second and one that
cannot, its amplitude blends linearly, so a key plays it as far as it lies
towards the pitch that measured it. Above the fundamental the late frames
mix the ring with the note's own unresolved partials (in the grand's top
bands they fall 0 to 10 dB/s), so only the first stage is fitted there.

From C6 up the 1 to 1.6 kHz bands now sit within about 4.5 dB of the
recordings from 0.1 to 0.8 s, the train and the never-fitted dev takes
alike, and the 2 and 2.5 kHz bands 0 to 5 dB under. On the recording
benchmark the grand's treble early spectrum sits 1.07 dB closer to its train
recordings and 0.91 dB to its dev ones, its sustain spectrum 0.39 and
0.27 dB, its noise between partials 0.56 and 0.50 dB; the upright's treble
moves by 0.08 dB or less. Neither piano has a regression
([grand](validation/grand-board-ring-benchmark-2026-10-29.md),
[upright](validation/upright-board-ring-benchmark-2026-10-29.md)). The
engine test's board-noise check now expects both stages' power over its
frames, where it had brought each frame back to contact at the first stage's
rate.

Still open: in their first 50 ms these notes sit 2 to 8 dB under the
recordings from 400 Hz to 2.5 kHz, and the body's 400 to 800 Hz band under
them falls 8 to 21 dB under from 0.5 to 0.8 s, as its modes' decays are
measured from 35 to 400 ms.

Chosen by measurement; the owner's standing direction is to adopt such
candidates. A short lettered treble passage on both pianos, the shipping
engine against this fit, went to the owner level-matched with its key. On
2026-10-29 the owner adopted the candidate under their standing rule that a
lettered candidate wins over the shipping engine unless they say otherwise;
no listening verdict was reported.

## 2026-10-29 — the body's modes ring in two stages

Asked for a grand that sounds full across the spectrum, the per-mode
comparison of the train and dev renders from C4 up with their recordings
(each take gained as the benchmark does, each mode's ±3 Hz envelope wherever
the recording stands 6 dB over its floor) found the body falling away after
the first 0.4 s: from 0.4 to 0.7 s the grand's regions from 25 Hz to 1 kHz
sat 5 to 13 dB under the recordings, from 0.7 to 1.5 s 17 to 35 dB under,
and the upright's 7 to 34 dB. The recordings' modes fall at 50 to 90 dB/s
over the first 0.4 s and then at 9 to 26 dB/s; the fit drew one line through
35 to 400 ms, which the engine played on at 50 to 70 dB/s. Room reverberation
is too short to hold a 9 dB/s ring; the frame and the board's low-loss modes,
which no damper touches, are a plausible source.

Each mode now has a second stage. Through the raw take's ±3 Hz envelope
every 10 ms from 0.4 to 1.5 s, the frames 6 dB over the take's quietest
second give a line; a layer counts it where 30 or more frames hold, it falls
6 dB or more across them, is slower than the first and starts 3 dB or more
under it, and the first is refitted on what the second leaves of the frames
from 35 to 400 ms. A mode takes the energy-weighted median of six or more
layers' second rates, else none. Each anchor's knock on each stage is a line
in its layers' level as before; the second stage's amplitudes are fitted on
the residual after 0.4 s, the first's on what they leave. The engine plays a
second bank on the same modes at the slower rate, knocked with the first;
the onset bank cancels both at contact, and the action's knocks ring only the
first. The grand measures a second stage on 86 of its 91 modes, a median 13
to 22 dB/s by region; the upright on 88 of 89, 10 to 30 dB/s.

Rejected on the way: a window of 0.4 to 0.95 s measured hum and rumble as
0.4 dB/s rings; one of 0.4 to 3 s left 56 of the grand's 91 modes without a
second stage; frames 10 dB over the floor left most of its modes from 200 to
400 Hz unmeasured, still 10 to 25 dB under the recordings; fitting both
stages' amplitudes jointly traded one against the other, so the grand's
400 Hz to 1 kHz rang 8 to 10 dB over the recordings from 0.4 to 1 s.

Now the grand's train takes sit 1.6 to 4.1 dB under the recordings from 0.4
to 0.7 s, 2.5 to 6.7 dB from 0.7 to 1 s and 3.7 to 11.4 dB from 1 to 1.5 s
(200 to 400 Hz the furthest), the never-fitted dev takes alike; before 0.4 s
the regions move by 1.2 dB or less. The upright's train takes are within
about 3 dB to 1.5 s, except 700 Hz to 1 kHz from 1 to 1.5 s (5.8 dB under;
dev 10.2 dB). On the recording benchmark the grand's sustain spectrum sits
0.31 dB closer to its train recordings and 0.27 dB to its dev ones (treble
0.95 and 0.84 dB), its noise between partials 0.10 and 0.05 dB, its early
spectrum 0.04 and 0.06 dB; its attack spectrum 0.06 and 0.02 dB further. The
upright's sustain spectrum sits 0.45 and 0.38 dB closer (treble 0.97 and
1.20 dB), its train noise 0.12 dB closer, its dev noise 0.26 dB further.

Regressions, all listed
([grand](validation/grand-body-tail-benchmark-2026-10-29.md),
[upright](validation/upright-body-tail-benchmark-2026-10-29.md)): on the
grand three rise times, F♯1 dev 1.8 to 5.3 ms, A4 train 3.0 to 5.6 ms and C2
train 4.3 to 5.4 ms; on the upright six rise times (A1 train 21.9 to
32.6 ms, C2 12.8 to 19.0, E5 7.6 to 11.6, G♯3 dev 14.3 to 15.8, C3 13.8 to
15.1, A♯3 4.4 to 5.7), four noise scores 0.5 to 0.8 dB (G♯3 dev, C2, A1 and
D3 train), F♯3's attack and early spectra 0.8 dB, the coherence of F♯6 and
G7 (train) and C5 (dev) by 0.02 to 0.06, and the envelopes of G7 and F♯6 by 0.5 to
0.7 dB. The rise times move in steps on single layers (the upright's C2 at
velocity 15, 15.4 to 31.2 ms; the grand's A4 from velocity 101 up, 0.5 to
8.2 ms): as the body's ripple near the onset's peak changes, the envelope's
90 % crossing jumps from one ripple to another.

Chosen by measurement; the owner's standing direction is to adopt such
candidates. A short lettered passage on both pianos, the shipping engine
against this fit, went to the owner level-matched with its key. On 2026-10-29
the owner adopted the candidate under their standing rule that a lettered
candidate wins over the shipping engine unless they say otherwise; no
listening verdict was reported.
## 2026-10-29 — a strike starts without a corner

Every strike clicked. Each partial rises as 1 − e^(−t/rise) and the body's
knock under its own rise of 0.3 ms, and each starts on a corner, a step in
slope, whose spectrum reaches to 22 kHz. In the 5 ms after the onset, from 8
to 22 kHz, each train and dev render stood a median 12 to 17 dB over its
recording in the bass and 8 to 20 dB in the middle (render less recording,
each against its 50 to 750 ms RMS, by band of 8 to 12, 12 to 16 and 16 to
22 kHz), and up to 26 dB at the tenth worst. A felt hammer's force grows
from zero slope as the felt is pressed in (a power law of its compression),
so the recordings start without one.

Every strike's rise is now smoothed by one more pole of 0.1 ms
(`contactSmoothing` in the engine): the partials' through a one-pole on
their rise, the body's by a second onset bank that cancels the first's slope
at contact. The 5 ms after the onset now sit a median 2.1, 2.5 and −3.0 dB
from the recordings in the bass and 2.6, 1.5 and 0.5 dB in the middle. In
the treble the measure barely moves (17 to 15 dB, 15 to 11, 19 to 13): there
the recordings' onset falls 2 to 4 ms before the hammer's contact, so their
first 5 ms hold less of the strike than the render's, whose onset is its
contact, and the treble's partials fill these bands themselves. At 0.05 ms
A1's click stayed 3 to 7 dB over its recording at velocity 61, and the
benchmark's bass noise 0.4 dB further from the recordings than at 0.1 ms.

On the recording benchmark the grand's noise between partials sits 1.22 dB
closer to its train recordings and 0.77 dB to its never-fitted dev ones (the
bass 3.55 and 2.34 dB, the middle 0.49 and 0.25 dB); every other measure
moves by 0.01 dB or less, and the rise times 0.01 ms (train) and 0.08 ms
(dev) closer. No case regresses ([grand](validation/grand-onset-smoothing-benchmark-2026-10-29.md)).
The upright's recordings were not in this session, so its benchmark was not
run; the engine test `a strike starts without a click` holds both pianos:
from 8 kHz up the 5 ms after contact hold no more than 3 dB over 20 to 40 ms
later, where unsmoothed they reached 14 dB.

The fits time every rise without this pole. Refitted with it in their
model, the grand's onset rises move at 14 of its 22 anchors (A0 from 2.8 to
1.7–3.8 ms over its layers, F♯5 from 5.6–7.3 to 1.0 ms; the fit keeps the
shortest of the candidates within 1 % of the best, so many are near-ties)
and its body rise from 0.31 to 0.24 ms. Played, that refit scores no closer
to the recordings: the rise times 0.07 ms (train) and 0.09 ms (dev)
further, the noise between partials 0.01 and 0.03 dB further, every other
measure within 0.01 dB. So the rises stay as fitted without the pole, and
the fit is unchanged; the upright's could not be refitted here in any case.

Rejected on the way: squaring each rise, (1 − e^(−t/rise))², which is
smooth at contact without a new time, removed the click as well (noise
5.38 dB on the train notes) but slowed every onset under rises fitted to the
unsquared shape, the train rise times 3.70 to 4.51 ms from their recordings;
it would need every rise of both pianos refitted to it.

Chosen by measurement; the owner's standing direction is to adopt such
candidates. A lettered phrase on both pianos, the shipping engine against
this one, went to the owner level-matched with its key.

## 2026-10-29 — one subtle release for both pianos, the body stopping with the strings

The owner heard the upright's release ring on far too long and asked for both
pianos to end alike, "something very subtle". A lettered set on staccato
notes and a released chord (`rel.ev`, RMS-matched) put the shipping engine
(A) against the body's ring stopping with the strings once every damper is
down, plus one shared leftover under the felt at −40 dB (B), −46 dB (C) or
none (D).

Chosen: **C**, under the owner's standing direction to adopt the candidate.
Both pianos now leave the upright's measured leftover shape and rates under
the felt at −46 dB at C4 (`leftover` in the engine), and the body's modes damp
at the felt's rate for their frequency while every key below the top damper
is muted. One second after release both pianos sit about 48 to 60 dB under
the note. The upright's release benchmark (2026-10-28) measured its leftover
at about −13 dB; that measurement still stands, and the owner's ear overrules
it here. Recorded as chosen by ear.

## 2026-10-29 — the action's key noise at −30 dB

The owner asked for key-down and key-up noise that is audible but not
overstated. Set `key.ev` (RMS-matched): A shipping (key-up only, grand about
−38 dB under the note, upright inaudible), B a key-down knock about −30 dB
and key-up about −32 dB under a velocity-80 note on both pianos, C 6 dB
louder. Chosen: **B**, as the less overstated of the two candidates. The
key-down knock is the action's measured knock on the body's modes, growing
with the strike's layer (`keyDownDb`). Chosen by ear.

## 2026-10-29 — more colour with velocity, at the same loudness

The owner asked for tone, not level, to follow velocity more. Set `col.ev`
(RMS-matched): A shipping, B and C each partial gaining 0.2 or 0.4 dB per
octave of its order (up to four octaves) for every dB the strike's layer sits
over a pivot layer. Chosen: **C**, 0.4 dB (`velocityColour`). As listened it
pivoted on velocity 64 and kept each partial's own level; that lifted the
loud chords into the output guard and broke the Levels check's
velocity-127-over-110 rule on Felt Upright. Shipped pivoting on the layer at
velocity 100, with each strike's partial energy rescaled to what the
recordings' layer plays, so loudness stays calibrated and only the balance
moves. C4's spectral centroid from velocity 20 to 120: grand 349→711 Hz
(was 419→504), upright 265→472 Hz (was 272→292). Chosen by ear; the amount
is a by-ear pinning, not a measurement.

## 2026-10-29 — the upright's faster attack waits for the owner

Asked to improve the upright's attack. Its partials swell over their fitted
rises, up to 116 ms at A2's fundamental, reaching 90 % of their early peak
14 to 50 ms after the strike. Two candidates were tried: every partial rising
with its pitch's measured whole-note onset (set `att.ev`, B), and each rise
capped at the hammer's contact time, about 2 ms at C4 halving per two octaves
up (Askenfelt and Jansson). B clicks: 8 to 10 dB of energy over 8 kHz in the
first 5 ms against 20–40 ms, where the limit is 3 dB. The cap sits at that
limit and makes Rehearsal Upright's velocity-127 chords no louder than at 110
through the output guard (HEAD's margin is 0.16 dB). Neither ships until the
owner says which check to give up or recalibrate.

## 2026-10-29 — the upright's partials rise within the hammer's contact

The owner chose, among the options above, to cap the upright's rises at the
hammer's contact time and re-trim its level. No partial of the upright now
rises slower than the hammer stays on the string: 2 ms at C4, halving every
two octaves up (about 4 ms at C2 and 0.7 ms at C7, Askenfelt and Jansson);
a partial whose fitted rise is shorter keeps it, and none rises faster than
its pitch's recorded onset. The grand's rises stay as fitted. The cap applies
the contact time itself rather than shortening each rise by its
mezzo-forte ratio, which kept C6's click measure at 3.05 dB at velocity 101;
now the highest is 2.38 dB (C4, velocity 31) under the 3 dB limit. The
upright's outputScale is re-pinned from 2.3548 to 2.2691 for −9 VU.

The level check's 110-to-127 step read −0.06 dB with the cap, and no level
trim within the target moved it: through the guard the upright's top two
velocities differ by about a tenth of a decibel, so each strike's spread
decided the sign, and the shipping upright read +0.08 dB over one round of
eight chords but −0.04 dB over five. `KeyraLevels` now plays each velocity's
chords in five rounds of their own, where the shipping upright reads +0.35 dB
and the capped one +0.24 dB. Chosen by the owner; the cap's time is a
measurement, the choice to apply it by ear.

## 2026-10-29 — the top strings keep the body ringing

The grand's Salamander benchmark of the shipping engine with the upright's
cap (`out/bench/cand-56dc43c`, 2494771 before its rebase, against
`out/bench/base-89e5eb0`, the engine before the shared release) found its
treble far from the recordings: from C6
up, the training notes' early spectrum sat 13.4 dB from them and their board
noise 13.2 dB, where 89e5eb0 had 4.3 and 5.4. The cause was the body's felt
contact: it counted only the damped strings, so a strike above F6, whose
strings have no damper, left the body falling at the felt's rate as if every
key were let go. An undamped string now keeps the body ringing as a held
key's does, and only CC1's mute damps it.

With the fix the treble's early spectrum is back to 4.6 dB and its noise to
5.6 dB (dev 4.6 and 5.5); over all training notes the early spectrum moves
from 6.9 to 4.3 dB and the noise from 8.2 to 5.8 dB. One note moves the other
way: A7's partials sit 3.7 dB from the recordings instead of 2.7 (dev 3.4
instead of 2.5), now that the body rings under them. Decided by the
measurement; no listening test.

Variants of the same run separate what else moved the grand since 89e5eb0:
the velocity colour accounts for the rest (training partials 1.7 → 4.6 dB,
attack 3.7 → 4.7, early 2.7 → 4.3, sustain 3.2 → 4.6), the key-down knock
for under 0.1 dB, and with both left out the run matches 89e5eb0 within
0.1 dB on every metric but rise time (3.6 against 3.7 ms).

## 2026-10-30 — the upright's two changes against the Helsinki recordings

The upright's benchmark (`Tools/benchmark_recordings.py --model upright`,
every train and dev note of the Helsinki split, lower is better) of the
shipping engine (0ec8037), the hammer-contact cap alone (2494771) and the cap
with the body fix (612c354):

| run | attack dB | early dB | sustain dB | noise dB | rise ms | partials dB |
|---|---|---|---|---|---|---|
| shipping, train | 5.90 | 7.54 | 6.71 | 8.65 | 9.53 | 5.87 |
| cap, train | 6.07 | 7.56 | 6.75 | 8.62 | 8.60 | 5.92 |
| cap and fix, train | 5.10 | 5.24 | 5.56 | 6.60 | 8.60 | 6.00 |
| shipping, dev | 6.66 | 7.26 | 8.78 | 6.88 | 10.14 | 8.80 |
| cap and fix, dev | 6.64 | 7.27 | 8.78 | 6.83 | 6.59 | 8.81 |

The body fix is the upright's largest move toward its recordings: from C6 up
the training notes' early spectrum moves from 14.4 to 6.0 dB, their noise from
12.8 to 6.0 dB, their sustain from 10.2 to 5.9 dB and their attack from 8.2
to 4.7 dB, and no note's attack or early spectrum moves away. Its four
regressions: E7's partials (2.8 → 5.7 dB, from its softest layer), the
interchannel coherence of C7 (0.16 → 0.20) and F#6 (0.10 → 0.12), and G7's
level difference between the channels (1.8 → 2.7 dB).

The cap brings the mean 10–90 % rise closer (train 9.5 → 8.6 ms, dev
10.1 → 6.6 ms, the training bass 26.0 → 13.0 ms), but moves more strikes'
rise away from the recordings (82 of 158) than toward them (66), and its
attack spectrum is 0.14 dB further on average. Its regressions are rises, at
C4 (9.8 → 32.0 ms), D5, G#4, D6, F#6, A2, E7, A#3, F#5, D4, C3, G#3 (dev)
and A#5, and the attack spectra of A2 (4.7 → 6.7 dB), A1 (4.4 → 5.7) and D3
(5.3 → 6.2), with A2's partials, envelope, level, sustain and early spectrum
each 0.5 to 0.7 dB further. At C4's loudest layer the recording's broadband
envelope takes 58 ms from 10 to 90 % of its peak; the fitted rises gave
57.5 ms and the cap gives 5.5 ms. The owner chose the cap by ear before these
recordings were measured; this record stands beside that choice, not in its
place.

## 2026-10-30 — grand and upright are two builds of one model

The owner asked for the grand and the upright to be two sets of parameters
of one model, with parameters to explore others. `keyra::Build` replaces the
Piano choice in the engine: four parts (strings, hammers, soundboard,
action), each from the grand's measurements at 0 to the upright's at 1, and
three modifiers (stiffness, B × 4^x; unisons, offsets × (1 + x) below 0 and
(1 + 2x) above; sustain, decay times × 2^x). At 0 and 1 every part takes its
piano's measurements exactly, so the measured builds play as the two pianos
did: a phrase of chords, pedal, mute and releases renders within −123 dB of
the shipping engine on the grand and −115 dB on the upright, where the
upright's noise draws follow a burst that ends one chunk apart. Levels moved
into output units (each piano's output scale added to its levels), so the
engine's absolute silence thresholds now read in them. Every third key at
velocities 15, 64 and 110, rendered at the benchmark's Output 0.07, differs
from the shipping engine by no more than −125 dBFS over any 100 ms on the
grand (C8 and A7 at velocity 15, a partial falling under a threshold 0.1 s
sooner) and −142 dBFS on the upright.

On the recording benchmarks the measured builds score as the shipping engine
did. All 432 Salamander train and dev notes score identically on the grand.
On the upright 156 of the 158 Helsinki notes do; the other two's noise score
moves 2.8 and 1.4 dB, and dev note 39's mean 0.7 dB, the one regression
`Tools/compare_benchmarks.py` lists. The scorer seeks a render's partials by
threshold and masks them out of the noise between them; in renders whose
difference sat 120 and 89 dB under them it found 39 partials where it had
found 40, and 22 where 19.

A strike between the pianos reads both pianos' series and sums three window
powers per partial: a ten-note chord's 64-frame callback took 1.9 ms on the
development machine at the halfway build, against 1.1 ms on either measured
build, whose strikes cost what the shipping engine's did. The demos' CPU
budget passes.

Between the builds, levels are blended on measured grounds, not by ear:

- A partial's lanes (decays, offsets, pickups, phases, shares) come from the
  strings, blended as between two recorded pitches, and its power over the
  layers' 50–750 ms window lies between the two pianos' partials' at the
  hammers' share. Lane levels mixed by the hammers put one piano's strike on
  the other's lanes, and the power from contact counted the upright's top
  notes' fastest lanes, which die within 50 ms: either put the upright's
  hammers on the grand's strings 5 to 7 dB over both pianos at E7.
- The body's modes pass between the pianos mode by mode in power, and a mode
  or partial only one piano has plays at its share in power. The two boards'
  modes of one index are not one mode, so their dB mean fell under both:
  the halfway build's soft top octave, nearly all knock, sat 4 dB under both
  pianos.
- Scanned over every key at velocities 0.25, 0.7 and 1, the halfway build
  now plays within 1.6 dB of between the two pianos' levels (was 3.9 dB);
  the engine test reads every third key.

A build change no longer silences what sounds, as the Piano switch did: the
build applies from the next strike, the sounding strings keep what they were
struck with, and the body, undamped strings and noise take the new build at
once. The body's pickups glide to the new board's over 10 ms (set at once,
they put 4 dB more over 8 kHz into the next 5 ms than the ring has), and a
mode the new board lacks fades over 5 ms.

## 2026-10-30 — the build's controls move each part toward the other piano

The front ends show the build as the chosen piano with each part moved
toward the other piano's (`keyra::buildToward`), not as four absolute
grand-to-upright positions. Every song, session and Rack patch saved before
the controls existed carries its Piano and no build, and loads the controls
at 0, so it plays the piano it chose; with absolute parts an upright saved
then would have loaded as the grand. A Rack panel cannot set four knobs from
one button either, so absolute parts would have cost Reason the one-click
choice of a measured piano. The price is that each measured piano has two
settings: the grand with every part at 100 % is the upright, which the
plug-in's processor test checks sample for sample. The plug-in shows the
parts as whose they are (Grand, 30 % upright, Upright) and the modifiers as
their factors, in a Build view beside the voicing knobs, so the editor keeps
its size and the main build's screenshot its view.

## 2026-10-30 — a strike's knock, measured from contact

For the first 20 ms after the hammer meets the strings, between the
partials, both pianos' recordings stood 5 to 16 dB over everything the engine
played there from 250 Hz to 10 kHz, while from 35 ms on the body and the
board's noise rang as recorded: the engine had no knock beyond the body's
modes, which stop at 945 Hz, and the board's noise measured 2 to 100 ms
after contact. Every strike now also starts a knock: band noise from contact
in fifteen third-octave bands from 630 Hz to 16 kHz, its own burst beside
the ring's two stages, measured per recorded pitch from 10 to 35 ms after
contact between the partials, beyond what the body and the ring play there
(`knock_bands` in `Tools/fit_realtime_modal.py` has the protocol): per band
one decay, the median of its layers' slopes, and per layer a density at
contact under it, and one left/right balance. The grand's pitches from F♯4
up find it in 27 to 123 of their 180 layer bands and play it in 3 to 12
bands, falling at a median 480 to 900 dB/s by pitch; the pitches below find
it in at most three layer bands, where their partials leave gaps to measure
at all, and play it in at most one band. The upright's plays from G♯4 up.

Rejected on the way: measured from the onset, with one fall per band shared
across the pitches, the knock took the treble's slow upper bands (about
180 dB/s at 16 kHz) where the bass's own fell at 1000 to 2700 dB/s, and the
bass's knock, which the key and action meet 9 ms before contact, sat 15 to
25 dB over its recordings through the first 0.1 s.

On the recording benchmarks against the shipping engine (4b11922), the
grand's attack spectrum moves closer on 216 of its 432 train and dev notes
and further on 20 (train 4.74 → 4.50 dB, dev 4.99 → 4.83; the treble's train
notes 5.35 → 4.73), its noise between partials closer on 232 and further on
28 (5.82 → 5.70, 5.50 → 5.41), and the onset rise 3.94 → 3.88 ms (train)
and 4.66 → 4.31 ms (dev). Its six regressions are rises at the top: F♯6, F♯7
and A7 now take 4.1 to 5.3 ms from 10 to 90 % of their peak at every layer,
where their recordings take 9.5 to 10.7 ms (F♯6), 7.4 to 10.8 (F♯7) and 6.6
to 15.0 (A7) and the shipping engine took 10 to 18, 4.6 to 9.0 and 4.6 to 8.4:
the knock now brings them to their peak sooner than the recordings' strikes,
which start 2 to 4 ms before contact
([grand](validation/grand-knock-from-contact-benchmark-2026-10-30.md)). The
upright's attack spectrum moves closer on 52 of its 158 notes and further on
13 (train 5.10 → 5.03, dev 6.64 → 6.55; the dev treble 6.85 → 6.47) and its
noise closer on 64 and further on 4, with no regression
([upright](validation/upright-knock-from-contact-benchmark-2026-10-30.md)).

Chosen by measurement; the owner's standing direction is to adopt such
candidates. A before/after phrase on both pianos went to the owner,
level-matched.

## 2026-10-30 — the open strings ring at their own partials, as the pedal-down take does

The strings whose dampers are off (all of them under the sustain pedal, and
each held key's) rang in sympathy as one resonator per key at its
equal-tempered fundamental, decaying at an invented 0.7 + 0.001 f per second,
so a struck C4 could not ring C3's second partial, and none followed the
piano's stretch. Salamander's pedal-down take shows what they do: once the
pedal's knock has passed, 122 string peaks from 60 Hz to 5 kHz ring for
seconds, their energy from 0.3 to 2.3 s 12.9 dB over the knock's in its first
0.3 s; the engine's open strings rang 32 dB under its knock.

Each damped key from A0 to E6 now rings its first eight partials under 5 kHz
at the built piano's own frequencies for them (its pitch, stiffness and
partial tunings, as a strike of that key plays them), driven by the output
at unity gain at resonance as far as its damper is off. They decay as
measured: from pedalD1 (train), each clearly falling string peak's slope over
0.5 s frames, and over 99 of them the rate's log linear in octaves, 0.319/s at
C4 (2.8 dB/s) growing ×1.334 per octave. That law sits a median 1.84 dB/s
from those peaks and 1.71 dB/s from pedalD2's 100, never fitted, where the
shipping engine's rates sat 17.5 and 19.8 dB/s from them. A key's own strikes
do not drive its own string, which is their voices: driven by its own
partials, the string's slower decay held a released C6's second partial
30 dB over its voice's after 2 s.

The pedal going down sets the strings it frees ringing, as its dampers lift:
per third-octave band from 63 Hz to 5 kHz, every free string's partial there
starts at the level that rings pedalD1's energy from 0.3 to 2.3 s through
those strings at the default Resonance and width, set against the notes at
the pedal knock's mix and at the share of the grand's action the build plays.
On `Tools/benchmark_pedal.py` the pedal-down ring over its knock now sits a
mean 2.7 dB per band from pedalD1 and 2.8 dB from pedalD2 (shipping: 55.5 and
60.2 dB), and its fall to 2.3–4.3 s 2.6 and 2.5 dB from them (8.5 and 8.7 dB)
([report](validation/grand-open-strings-benchmark-2026-10-30.md)). The
recording benchmark plays single notes without pedal, so it does not see this
change; its notes score as they did within 0.07 on every measure.

The upright has no pedal recordings: its open strings ring at the grand's
law, and its pedal lifts no strings. With every damper off the bank takes
about 3 % of one core of the development machine, and the demos' CPU budget
passes.

Chosen by measurement; the owner's standing direction is to adopt such
candidates. A before/after pedalled phrase on both pianos went to the owner,
level-matched.

## 2026-10-30 — the upright's soft pedal is a half-blow

The upright's soft pedal was the grand's una corda: it lowered the level and
the high partials and moved energy to the slowest lane, as a hammer shifted
off one string of each unison does. An upright's soft pedal moves the hammer
rail toward the strings instead (half-blow): every string is struck as
before, by a hammer that travels a shorter way and so arrives slower. At
full pedal a hammer now starts halfway to its strings; thrown as hard by the
key, accelerating over half the distance, it meets them √½ as fast (v² = 2as),
so the strike plays as that slower strike, on the layer the recordings hold
at its loudness, and changes nothing else. Between the pianos the action's
build sets the share of each mechanism. At middle C, velocity 100, full pedal
now takes 6.8 dB off the upright's first second and moves its spectral
centroid from 296 to 268 Hz, where it took 6.3 dB and moved it to 293 Hz.

No recording plays the upright's soft pedal, so neither halfway nor the
constant acceleration is measured: this is a derivation, adopted under the
owner's standing direction. A before/after phrase with the pedal held went
to the owner, level-matched.

## 2026-10-30 — full sustain pedal rings as 80 % of it did

The owner found full sustain too long and asked to calibrate it so its
maximum is 80 % of what it was. Read, and said so to the owner when the work
started, as: full pedal lifts the dampers only as far as 80 % of the pedal
did (`dampersLift`), so the felt still grazes the strings. A velocity-80
chord of C3, C4, C5 and C6 let go under full pedal now falls 60 dB in 8.7 s
on the grand and 11.2 s on the upright, where it rang on past 30 s.

Taken literally the request would also have silenced the pedal's sympathetic
wash, which the realism pass had just fitted to Salamander's pedal-down
takes: the open strings had their own partial-pedal law, openness = sustain²
and (1 − openness) × 60/s of loss, which at 80 % of the pedal took them down
at 21.6/s (188 dB/s) while the same pedal left the struck strings' felt
barely touching (a released C4 losing about 2.5 dB/s more than with the
dampers clear). One pedal lifts one rail of felts, so the open strings now
follow the struck strings' felt law (`feltContact`): at full pedal they lose
about 3 dB/s more than clear of the felt, and the wash is kept. This also
moves half pedalling: at half pedal the open strings lost 45/s and now 14/s.

On `Tools/benchmark_pedal.py` the pedal-down ring over its knock sits 1.21
and 4.74 dB per band from pedalD1 and pedalD2 (2.73 and 2.80), its fall to
2.3–4.3 s 6.10 and 6.29 dB from them (2.58 and 2.46), and the freed strings'
median decay is 9.6 dB/s against the takes' 6.8 and 7.0
([report](validation/grand-pedal-lift-benchmark-2026-10-30.md)). The
recording benchmark plays single notes without pedal: playing without pedal
renders sample for sample as before on both pianos.

Chosen by the owner, not by a measurement: the recordings' pedal lifts the
dampers clear and sustains longer.

## 2026-10-30 — a Mechanics control

The owner asked for the action's loudness to be customizable. Mechanics
scales, as an amplitude from 0 to 2, every knock of the action (the keys
landing and coming back, the dampers falling, the sustain pedal going down
and coming up) and the ring the pedal sets going down. A strike's own knock
on the body and its contact noise are the hammer's, not the action's, and do
not move. At 1 the engine plays as before, sample for sample. The plug-in's
presets leave it, as they leave Output.

## 2026-10-30 — the action's knocks ring at their own decay; a key lands with its strike

The owner asked for the tonal balance to be refined and unwanted resonance
removed. Surveyed signed per third-octave band against the recordings
(`Tools/tone_survey.py`), the treble boomed: 0.1 to 0.5 s after the strike
the grand's train notes from C6 up stood a median 5.1 dB over their
recordings at 200 Hz and 7.3 dB at 250 Hz (dev 6.9 and 9.8 dB), the
upright's 5.4 and 6.5 dB at 80 and 100 Hz and 4.3 and 5.1 dB at 250 and
315 Hz. Most of it was the key landing: a knock about 28 dB under a
velocity-80 note at C2, C4 and C6, but 4 to 10 dB under the quiet notes from
C7 up, building up over the release recordings' 54 ms rise and ringing at the
board's own rates on a body that a top note keeps free.

The release recordings' knocks fall faster than the board rings: per
third-octave band from 63 to 800 Hz the grand's train takes fall a median
1.3 to 3 times as fast as its modes ring there, the 19 takes of keys without
a damper about as fast as the 62 with one. The fit now finds one decay with
the knocks' shared rise, each mode falling that many times as fast as the
board's ring of it: 1.5 on both pianos, under a 152 ms rise on the grand
(40.3 % of the knocks' energy left unexplained, 41.4 % at the board's rates
under the 54 ms it found then) and 108 ms on the upright (58.8 %, 59.6 %).
The engine rings every knock of the action on its own bank at that decay,
whatever the dampers do, and a key landing knocks with its strike, building
up under the body's rise as the strike's knock does: the landing is an
impact, where the release recordings' slower build is the key and the damper
coming back. Rejected on the way: the measured decay with the landing still
building up over the knocks' rise, which the refit lengthens, left most of
the boom (grand treble 4.8 and 6.6 dB at 200 and 250 Hz, upright 4.5 and
5.8 dB at 80 and 100 Hz).

The owner chose the keys' loudness by ear (2026-10-29), so their levels are
re-pinned to play as before in their first 100 ms against a velocity-80
note's 50 to 750 ms, C2, C4 and C6 averaged in dB: the grand's landing and
let-go knocks −27.9 and −28.0 dB, the upright's −30.1 and −36.1 dB, each
within 0.03 dB of the shipping engine. The old felt damped the board's ring
once every damped key was down, so a key let go below F6 lost most of its
knock to it while one above, with no damper, rang on: the grand's C7 to C8
let go 1 to 7 dB over their notes and the keys below 20 to 33 dB under. Now
every key's let-go knocks as the release recordings' do, at the level the
owner chose for the keys below F6 (C8 −3.7 dB, C7 −9.9 dB). The sustain
pedal's knocks stay at the library's mix and now stand against the strings
the pedal frees as Salamander's pedal-down takes do: with the dampers clear
the energy from 0.3 to 2.3 s sits 4.1 dB over the first 0.3 s against the
takes' 4.7 and 4.4 dB (it sat 6.9 dB), so the knock sounds about 3 dB
louder, and under the owner's grazing felt −0.2 dB (2.8 dB)
([pedal](validation/grand-action-decay-pedal-benchmark-2026-10-30.md)).

Surveyed again, the treble's boom 0.1 to 0.5 s after the strike is a median
1.0 and 1.7 dB over the grand's train recordings at 200 and 250 Hz (dev 1.6
and 3.7 dB) and 0.8, 1.8, 1.3 and 1.6 dB over the upright's at 80, 100, 250
and 315 Hz; the grand's middle register, 2.2, 1.9 and 1.1 dB over from 125
to 200 Hz, is 0.5, 0.0 and −0.6 dB. On the recording benchmarks against
e9411bb, the grand's early spectrum moves closer on 175 of its 432 train and
dev notes and further on 39 (train 4.25 → 4.16 dB, dev 4.62 → 4.52; treble
4.63 → 4.41 and 4.60 → 4.28) and its noise between partials 5.70 → 5.63 and
5.41 → 5.38 dB. Its regressions: C8, which plays A7's data, now sits 5 to
7 dB under its recordings from 62 to 315 Hz in that window, where the
landing's long ring had filled them (early 6.27 → 6.94 dB train, 5.88 → 6.53
dev, its noise and dev partials 0.5 dB further); A3's onset rise
(0.94 → 2.49 ms train, 0.69 → 2.29 ms dev); and F♯1's dev noise
(3.81 → 4.70 dB) ([grand](validation/grand-action-decay-benchmark-2026-10-30.md)).
The upright's early spectrum moves closer on 70 of its 158 notes and further
on 16 (train 5.24 → 5.05, dev 7.28 → 7.31; treble 6.01 → 5.50 and
7.82 → 7.93) and its noise 6.56 → 6.42 and 6.92 → 7.01 dB, with F♯6's and
G7's train envelopes (3.50 → 4.03, 3.92 → 4.49 dB) and G♯6's train
coherence (0.32 → 0.37) its regressions
([upright](validation/upright-action-decay-benchmark-2026-10-30.md)). On the
upright's key-release takes (`Tools/benchmark_releases.py`) the partials'
release shapes sit 5.15 dB from the train takes (5.03 dB) and 6.65 dB from
the dev takes (6.74 dB): the let-go knock the felt no longer cuts short rings
on through A♯3's, F♯4's and F♯5's partials, 1.1 to 1.2 dB further from their
takes, and D6's sits 1.3 dB nearer.

The action's own bank costs CPU: on the development machine the README
demos render 5 to 13 % slower on six presets and within 3 % on Felt Upright
and Pop Upright (`RenderKeyraPresetDemos --cpu`, shipping and candidate run
twice, alternated, medians of six).

Chosen by measurement, under the owner's standing direction to adopt such
candidates; a before/after phrase of treble notes, a chord and the pedal went
to the owner for both pianos.

## 2026-10-30 — a Tube Mic: from the pair to the vintage tube

The owner asked for microphone positions to choose the sound's colour, from
vintage to close to distant to floor, and for a way to balance or mix them.
Of the recordings the owner provided, only the Helsinki library took the
same strikes with more than one microphone: the Blumlein ribbon pair in
player position that the upright is fitted from, and a mono tube condenser
(a modified CV-12) at shin height to the left. A card offered the close pair
and the vintage tube, mixable (recommended); adding a modelled distant
position chosen by ear from lettered candidates; or waiting for recordings
from further off. It is unanswered, so the recommended option is built and
the other two stay open.

The tube's colour is measured, not chosen: per third octave, the tube's
level over the ribbons' mid on the 137 train takes, fitted with two shelves
and five peaks, 1.5 dB from the 21 dev takes' medians where a flat response
sits 3.8 dB from them (`Tools/fit_mic.py`). No grand was recorded through
it, so on the grand the same response is a colour, not a measurement. Its
level is each piano's calibration on Reason's meter, so that typical playing
reads −9 VU through the tube as through the pair: ×1.588 on the grand and
×2.440 on the upright against the response's own level, between them by the
hammers' build. Through the tube a soft note loses more than a loud chord,
since its dip at 250 to 315 Hz holds much of a soft middle note, so the
loudest chords press the output stage's guard harder: they read −0.8 and
−0.3 VU (the pair's −0.9 and −0.8 VU on the default presets) and still play
0.6 and 0.3 dB louder at velocity 127 than at 110. Between 0 and 1 the two
are mixed in amplitude and the image narrows; at 1 the sound is mono and
Width does nothing. Presets leave the control, as they leave Output and
Mechanics: it says where the listener stands, not how the piano is voiced.

## 2026-10-30 — rejected: a strike's knock falling faster at first

Under the upright's treble the body still rings boxy: 0.1 to 0.5 s after the
strike the train notes from C6 up stand a median 3.4, 5.5, 6.3, 8.3 and
5.0 dB over their recordings from 400 Hz to 1 kHz. Fitted from 20 ms on with
each mode's measured rate, a knock's first stage takes up its early fall and
rings on over the recordings. Two ways of letting part of it fall 1.5 times
as fast, the action's knocks' decay, were refitted on both pianos and
benchmarked against 0.4.1 at dba37b9; neither ships.

- A free fast part took about twice the first stage's amplitude in opposite
  phase in nine modes of ten, a notch in each mode's ring. It cut the boxy
  band 4 to 6 dB toward the upright's recordings but put 2 to 4 dB more
  knock below 160 Hz into the first 0.1 s on both pianos, where the renders
  already stood over theirs; the attack score fell from 5.02 to 5.36 dB
  (train) and 6.56 to 7.05 dB (dev) on the upright and from 4.48 to 4.75 dB
  and 4.83 to 5.13 dB on the grand.
- A share of the first stage in its own phase, 0 to 1 per mode, met its
  bound of 1 in 77 to 88 % of the upright's modes: the data asks for the
  whole knock to fall faster, which, extrapolated back to contact, starts it
  3 to 4 dB louder. The upright's boxy band came 2.5 to 3 dB closer and its
  early score 5.05 to 4.91 dB (train) but 7.31 to 7.34 dB (dev); the
  grand's early score fell from 4.16 to 4.39 dB (train) and 4.52 to 4.71 dB
  (dev), its treble's band going 1 to 3 dB under its recordings, with 28
  notes and roles regressing.

With the action's knocks silenced the upright's middle register still
stands 3 dB over its recordings at 80 to 100 Hz in the first 0.1 s, so that
low thump is the strike's knock, not the keys landing. Both stay known gaps.

## 2026-10-30 — rejected: the board's ring at each pitch's own coherence

From C6 up the grand's image is narrower than Salamander's: from 800 Hz to
4 kHz its side stands a median 2.4 to 4.7 dB further under its mid than the
recordings' on the dev cases, and its channels' coherence 0.2 to 0.3 higher
(`Tools/tone_survey.py` at dba37b9's engine). The board's ring plays one
left/right coherence per band, pooled over every recorded pitch and measured
on its first stage, 2 to 100 ms after contact; the recordings of the notes
from C7 up hold a median 0.17 from 1 to 1.6 kHz over 0.05 to 1.5 s. Two
refits gave the ring its own pitch's coherence, interpolated between the
recorded pitches like its balance; both reproduce every other value of both
headers, and neither ships.

- The first stage's coherence per pitch: the treble's own is no lower than
  the pool (0.08 to 0.58 from 1 to 1.6 kHz at C6 to A7, median 0.36,
  against 0.29 to 0.38 pooled). The grand's treble dev cases moved the
  wrong way at 1.26 kHz (side 4.7 to 5.3 dB under the recordings',
  coherence 0.25 to 0.32 over) and at 2, 4, 8 and 10 kHz, 0.6 to 2.7 dB
  further under.
- Adding the second stage's own coherence, measured over the late frames it
  is fitted on (150 to 600 ms; 0.04 to 0.33 at those pitches): from 1 to
  1.6 kHz the treble's side came 0.3 to 1.2 dB closer and its coherence
  0.02 to 0.12, but at 2 and 4 kHz it fell 0.4 and 0.6 dB further under,
  at 8 and 10 kHz 1.4 and 2.7 dB, and the upright's treble train cases lost
  0.4 and 1.0 dB at 1 and 1.26 kHz.

So fitting the ring's coherence per pitch does not widen the treble. In
probe builds that silence the board's noise, C7's and F♯7's bands from 1 to
1.6 kHz fall 10 to 22 dB at velocity 80, so the noise is what those bands
hold. Heard alone, it reads a coherence of 0.45 to 0.54 there over 0.05 to
1.5 s, where those bands mix their sources at 0.29 to 0.38; silencing the
undamped strings or the open strings' resonance widens none of them. In a
probe whose noise does not decay it reads 0.38, 0.37 and 0.28 at 1, 1.26 and
1.6 kHz, the coherence it is mixed at: the engine mixes as measured, and the
higher reading is the short burst's, an estimate from few independent
samples. The recordings read 0.17 there over the same window, with their
energy in those bands within 3.5 dB of the render's in the first 0.1 s and
within 1.3 dB after it, so their sound is less coherent there than the 2 to
100 ms frames the coherence is measured on. What the noise should be mixed at
over its whole ring, not its first 0.1 s, is the open question; it stays a
known gap.

## 2026-10-30 — the body is fitted after the knock where the knock plays

The upright's treble rang boxy: 0.1 to 0.5 s after the strike its train
notes from C6 up stood a median 3.4, 5.5, 6.3 and 8.3 dB over their
recordings at 400, 500, 630 and 800 Hz (`Tools/tone_survey.py`, early
window, at 027ac85's engine). The recordings fall there at 190 to 250 dB/s
from 50 to 200 ms; the body's modes, fitted from 20 ms after contact, fall
at their own measured rates, 100 to 130 dB/s, so their fit took up the
strike's fast knock and rang it on. Where the knock's bands play it, the
modes are now fitted again from 45 ms, the end of the knock's last frame,
on what the other modes leave, and the knock is measured from 400 Hz where
it started at 630 Hz: in the treble those two bands find it falling at 170
to 400 dB/s. A first fit refits the modes in every band whose gaps between
the partials can measure the knock; the second only where that one found
it. Refitted at every pitch from 354 Hz up, the modes lost the knock
wherever no band played it: the upright's F♯3 and A♯4 and the grand's C5
and F♯5 rose 5 to 11 ms off their recordings, where they had been within
1.4 ms. Refitted in every band the knock could be measured in, the grand's
never-fitted middle notes stood 2.4 dB further under their recordings at
500 Hz in the first 0.1 s, and the upright's treble 1.5 dB at 1 kHz. The
body's rise is still timed on the first fit from 20 ms, knock and all, as
the recording builds up: on the refitted modes it fell to the grid's
0.1 ms, under the 0.2 ms the engine's onset needs.

On the upright the boxy bands now stand 2.6, 2.1, 3.9 and 4.5 dB over, and
the dev notes' 630 and 800 Hz 3.4 and 1.5 dB where they stood 5.5 and
5.3. Against 0.4.1 at 027ac85 the benchmark lists no note or role worse
than its tolerance on either piano; the upright's early score moves from
5.05 to 4.94 dB (train) and 7.31 to 7.29 (dev), its noise 6.42 to 6.31 and
7.01 to 6.98, and the grand's attack 4.48 to 4.44 and 4.83 to 4.80, its
early score 4.16 to 4.19 (train) and 4.52 (dev) unchanged
([grand](validation/grand-body-after-knock-benchmark-2026-10-30.md),
[upright](validation/upright-body-after-knock-benchmark-2026-10-30.md)).
Per band the costs are under the treble's fundamental: from 400 to 800 Hz
the side falls up to 5 dB further under the mid on both pianos (the knock
is mixed at the coherence of its first frames, 0.53 to 0.82 at 400 and
500 Hz), and the grand's 500 Hz to 1 kHz stands 0.4 to 1.2 dB further under
its recordings from 0.1 to 0.5 s. The preset demos time 0.8 % slower in
total, the two new bands, within run-to-run spread (−1.9 to +2.2 % per
preset); typical playing still reads −9 VU on both pianos.

Chosen by measurement, as the owner's standing direction asks; no one has
listened to it yet.

## 2026-10-31 — a blended partial keeps the nearer pitch's channel phase

A key between two recorded pitches takes each lane's phases from the nearer
pitch, but `blendLane` blended the channels' phase difference along the
shorter arc. The right channel's phase is the lane's turned by that
difference, so the lanes met in the right channel at phases neither pitch
gives them and cancelled there: D♯5's third partial on the grand and its
second on the upright sat 4.6 and 6 dB further to one side than either
neighbour (whole band, 0.1 to 1.1 s), and on refitted data D♯3's
fundamental sat 14.2 dB to the left, where C3 holds it 4.7 dB left and F♯3
0.2 dB right. The phase difference now comes from the nearer pitch with the
phases; the level difference is still blended in dB. Recorded pitches are
not blended; they change only by the re-pinned output scale below.

Every blended partial of every key between recorded pitches at layer
coordinate 64, its heard right-over-left balance (the lanes' beating
included, against e^(−t/0.4 s) as `heardPower` weighs it) against its two
pitches': on the grand 29 % of them sat beyond both, by up to 12.5 dB (99th
percentile 5.45 dB), now 24 %, by up to 7.7 dB (4.23); on the upright 24 %
by up to 11.7 dB (5.00), now 20 % by up to 7.2 dB (3.54). The engine test
now reads D♯3 and D♯5 on both pianos, their first four partials over each
whole band, and holds each within 3 dB of its neighbours' range; the
shipping engine fails it at D♯5 on both pianos (the grand's third partial
−10.7 dB against −6.1 and +3.0).

On the benchmark the dev notes' image (ild_db) moves 2.56 to 2.47 dB on the
grand, its four never-fitted pitches 4.97 to 4.74 dB, and 4.53 to 4.26 dB on
the upright, whose dev notes are all never fitted; the train notes score as
before. Per pitch on the grand D♯1 3.12 to 2.98, D♯5 8.30 to 6.81
and D♯7 1.62 to 1.45, but D♯3 6.84 to 7.73: the recording holds its first
eight partials between 0 and 12 dB to the right, where C3 and F♯3 hold their
second 19 to 24 and 10 to 11 dB to the left, so no blend of the two places
D♯3, and the old one happened to land nearer. The regressions
`Tools/compare_benchmarks.py` lists are that D♯3 image, D♯5's envelope on
the grand (4.61 to 5.66 dB) and on the upright E6's coherence (0.20 to 0.28)
and envelope (6.55 to 7.06 dB) and D♯2's coherence (0.20 to 0.22)
([grand](validation/grand-stereo-between-pitches-benchmark-2026-10-31.md),
[upright](validation/upright-stereo-between-pitches-benchmark-2026-10-31.md)).

Rejected: setting each blended partial's heard balance between its two
pitches' (or pianos') with a gain per channel. Where a channel cancels over
the heard window but rings on later, its gain grows without bound: at the
halfway build a soft A1's fifth partial took 19.3 dB of gain on the right.
It failed the stereo test at D♯3 (the grand's fundamental +3.9 dB against
−4.3 and +0.4) and the halfway build's level test (2.8 dB at A1), where the
nearer phase passes both (0.95 dB, was 1.22).

The meter reads the louder channel and the tube hears their sum, so the
balanced channels read a little lower on the pair and higher through the
tube: typical playing on the presets moved −0.14 to +0.15 dB, the default
sounds −0.04 (grand) and −0.05 dB (upright), and the tube alone +0.27 and
+0.31 dB. `outputScale` and `tubeScale` are re-pinned to the new readings
(`Tools/KeyraLevels.cpp`): each piano's default sound reads −9.00 and
−9.02 VU through the pair and −9.00 and −9.01 VU through the tube. Warm
Walnut then read 2.02 dB under the target, where the check allows 2, and
now plays at brightness 0.30 (was 0.28), which reads −10.94 VU. The change
takes work from a strike; the per-sample path is unchanged.

Chosen by measurement, as the owner's standing direction asks; no one has
listened to it yet. The A/B pack is in the project files
(`keyra/stereo-between-pitches-2026-10-31/`).

## 2026-10-31 — an in-between key's lanes meet by the share they carry

A key between two recorded pitches blends each partial's four lanes pair by
pair, and `blend` paired them as they are stored, fastest first. Where one
pitch's fit holds a lane the other's lacks, that order meets the lane that
carries a partial with one that carries little. A refit gave F♯3's second
partial on the grand a 228 dB/s transient ahead of the lane that carries
91 % of it: C3's carrying lane met the transient, F♯3's met a lane of C3's at
−38 dB, and D♯3's second partial sat at −6.2 dB right over left, 6.3 dB
nearer the middle than either neighbour (C3 −24.0 dB, F♯3 −12.5 dB), which
fails the stereo test. Each partial now takes, of the 24 pairings, the one
whose pairs' log decay rates differ least, each pair weighed by the share of
the partial its two lanes carry: a lane's heard power (against
e^(−t/0.4 s) as `heardPower` weighs it, its beating left out) as a share of
its partial's, averaged over the layers so that a key pairs its lanes alike
at every velocity. The blended lanes are then stored fastest first again, as
`combine` pairs the pianos' lanes. On the refit D♯3's second partial sits at
−20.8 dB, and every engine test passes on the shipping data, on the refit and
on the refit with its strings' energy restored.

On the shipping data the pairing changes 433 of the grand's 733 blended
partials and 286 of the upright's 498, most of them in the bass; in 131 and
66 of them the lanes that carry the partial now meet where they did not.
Recorded pitches play as before, and the train notes score as before. On the
grand's dev notes level moves 1.20 to 1.07 dB (middle register 1.03 to
0.76), decay 2.34 to 2.29 dB/s (treble 3.37 to 3.08), the early spectrum
4.57 to 4.52 dB, the image 2.47 to 2.44 dB (middle 3.77 to 3.65) and the
envelope 2.67 to 2.65 dB; partial levels move 5.42 to 5.44 dB, the sustain
spectrum 5.25 to 5.31 dB and the bass image 1.33 to 1.43 dB. On the
upright's 21 dev notes the envelope moves 4.95 to 4.88 dB and the early
spectrum 7.32 to 7.27 dB, decay 4.47 to 4.63 dB/s and the image 4.26 to
4.31 dB. No note moves past the tolerances `Tools/compare_benchmarks.py`
lists regressions at
([grand](validation/grand-lane-roles-benchmark-2026-10-31.md),
[upright](validation/upright-lane-roles-benchmark-2026-10-31.md)). The
levels check passes unchanged. The pairing costs a strike 24 sums of four
terms per blended partial; the per-sample path is unchanged.

Chosen by measurement and the stereo test, as the owner's standing direction
asks; no one has listened to it yet. The A/B pack is in the project files
(`keyra/lane-roles-2026-10-31/`).

## 2026-10-31 — each partial keeps the energy its strings hold

A least-squares fit keeps less of a partial than its recording holds, by what
it leaves in the residual, and where the lanes cannot follow the unison
strings' beating that is a good share of it. Over the first 0.75 s that loss
sets a recorded pitch's loudness, and so the keyboard's evenness: the grand's
F♯7 fits held 2.9 to 3.4 dB less than its recordings at every layer, the
upright's A♯6 and E7 fundamentals 2.7 to 8.4 dB, where C3's and C4's hold
within 0.3 dB, and the benchmark heard F♯7 2.3 to 3.5 dB under the median
note. `Tools/fit_realtime_modal.py` now scales each partial's lanes, layer by
layer, to the energy its strings hold from 50 to 750 ms after contact, both
measured through the analysis's window, in the frames where the recording
stands 10 dB over the partial's floor and 10 dB over its level half an order
either side, less that level; by at most 6 dB, and not where fewer than ten
frames stand that clear. Beside a bass fundamental the board rings within
5 dB of it, a sound the body plays; taken as the strings', it would have
raised the grand's A0 and A1 fundamentals by 1 to 5 dB, so the level beside
is taken out. The analysis is unchanged; both pianos are refitted from it.

On the benchmark the grand's train notes' level moves 0.69 to 0.50 dB and
their partial levels 4.62 to 4.54 dB; on its dev notes level moves 1.07 to
0.96 dB (treble 1.42 to 1.01), partial levels 5.44 to 5.39 dB and the attack
4.81 to 4.78 dB. F♯7 sits 0.82 dB from its recordings' loudness (was 1.98)
and A7 0.85 dB (1.98). Of the 17 regressions `Tools/compare_benchmarks.py`
lists, ten are C8's: the keys above A7 play A7's data, A7's fundamental now
plays 1.7 to 3.8 dB louder, and C8's spectra move 0.8 to 1.2 dB further from
its recordings (its sustain spectrum was already 16 dB off). The others are
A7's rise (dev 2.33 to 3.71 ms, train 2.96 to 4.37 ms), D♯1's dev rise
(1.83 to 7.98 ms: at three layers the 10–90 % rise jumps from about 1 ms to
24 ms while D♯1's spectra and level move under 0.1 dB, the 90 % point
passing from the strike to the swell after it), A1's train noise (6.02 to
6.75 dB) and rise (2.10 to 3.14 ms), and A6's and D♯7's dev tuning (0.12 to
0.76 and 3.48 to 4.04 cents) ([report](validation/grand-string-energy-benchmark-2026-10-31.md)).

On the upright the train notes' level moves 0.87 to 0.51 dB (treble 1.58 to
0.57) and partial levels 5.98 to 5.76 dB; on its 21 dev notes partial levels
move 8.78 to 8.39 dB, the early spectrum 7.27 to 7.14 dB, the sustain
spectrum 8.77 to 8.66 dB, decay 4.63 to 4.54 dB/s and the attack 6.47 to
6.41 dB, while noise moves 6.98 to 7.09 dB and rise 6.00 to 6.21 ms. E7 sits
1.50 dB from its recordings' loudness (was 4.52), G♯6 0.12 dB (1.89), A♯6
0.44 dB (2.08) and C6 0.45 dB (1.75). The five regressions are E7's train
sustain spectrum (6.89 to 8.06 dB), D♯2's dev noise (8.57 to 9.39 dB), A2's
train noise (4.53 to 5.13 dB), C7's train coherence (0.21 to 0.24) and B3's
dev rise (4.85 to 5.85 ms) ([report](validation/upright-string-energy-benchmark-2026-10-31.md)).

`Tools/evaluate_recordings.py`'s 24 cases of the preserved research split,
all in the live model's train role, through the product default: the twelve
in-range held-out cases' harmonic levels move 4.11 to 4.01 dB, their band
levels 5.15 to 5.13 dB, partial tuning 0.34 to 0.22 cents and rise 4.83 to
4.02 ms, envelope 1.71 dB and decay 2.27 to 2.28 dB/s; the edge cases C1v8
(band levels 2.61 to 2.63 dB, harmonic levels 3.08 to 3.18 dB) and C7v8
(band levels 6.43 to 6.83 dB, envelope 13.63 to 13.76 dB, rise 0.23 to
0.02 ms).

The refit plays louder: the upright's typical playing read 0.30 dB over
−9 VU at Mic 0 and 1.18 dB at Mic 1, the grand's 0.04 and 0.17 dB, so
`outputScale` and `tubeScale` are re-pinned (grand 0.7699 and 1.5091, were
0.7738 and 1.5312; upright 2.2040 and 2.1196, were 2.2806 and 2.3472) and
every reading is back at −9.00 VU. The refit changes levels only, no lane or
partial: the demo renderer's CPU time is 45.1 s against 45.2 s (median of
three runs each).

Chosen by measurement, as the owner's standing direction asks; no one has
listened to it yet. The A/B pack is in the project files
(`keyra/string-energy-2026-10-31/`).

## 2026-10-31 — a third piano, the grand of VCSL Keys

The owner offered more libraries to calibrate the pianos against, to blend
between or to build new pianos from, keeping one product whose model fits
them all: VCSL Keys, Pianobook's Grandmas, Yamaha C3 and Grandpas, Mum's
Upright and a Steinway grand for Decent Sampler. VCSL Keys (Versilian
Studios) is CC0, so numbers fitted from its "Grand Piano, K", a Kawai grand,
can ship without asking anyone. The Pianobook and Decent Sampler libraries
need their authors' permission to be fitted, as the Helsinki library did, and
none has been asked, so none of them is fitted. The grand is the third
measured piano, `Piano::kawai`, added after the other two so that saved songs
and patches recall them as before; the front ends call it the Hamamatsu grand
(below).

Its recordings are a stereo pair in player position, 44.1 kHz/16-bit, one
take per note at four velocity layers, the SFZ's 0–54, 55–83, 84–106 and
107–127, each played at its range's rounded midpoint (27, 69, 95 and 117
where a pitch has all four), the softest 32.8 dB under the loudest, with a
release take per recorded pitch and no pedal recordings.
`Tools/decode_vcsl.py` decodes a copy of the library without gain, trim or
resampling and verifies it against the pins in `Tools/corpus/vcsl-kawai.json`.
The lowest takes, which the SFZ maps to A♯0, sound A0 (the strongest peak by
A♯0's third partial sits 109 to 112 cents under it) and are taken as A0's.
The split (`Tools/corpus/split-vcsl-kawai-2026-10-31.json`) was written after
an inventory and before any fit: 27 pitches train (131 files); D♯1, D♯2, A♯3,
D5, A♯5, B5, F♯7 and G7 dev (31 files with their release takes; B5 and G7
hold one layer each); D3, F♯4 and F♯6 sealed (14 files), not opened.

`Tools/fit_realtime_modal.py --model kawai` fits it as it fits the other two,
624 partials at 27 recorded pitches from A0 to C8
(`Source/DSP/MeasuredKawaiData.h`), with what its recordings ask:

- An order counts where two layers find it, not three. The layers span
  33 dB, and the second softest finds C4's series to the 15th partial where
  the two loudest find it to the 29th and 38th: asked of three layers, a
  forte strike's upper partials went unplayed. On the dev notes the partial
  levels sit 9.85 dB from the recordings (three layers: 11.17 dB) and the
  rise 4.98 ms (9.55 ms), while decay sits 5.25 dB/s (5.03 dB/s).
- Every second-layer take from E3 up was recorded through a noise gate that
  cuts it to digital silence, channel by channel, 0.6 to 15 s after the
  strike. The analysis, the fit and the benchmark read a take only until it
  stops holding the piano, at its first 20 ms of exact silence in either
  channel (`piano_analysis.recorded_end`). No Salamander take holds such a
  run, and the Helsinki takes only past the fade-out every measurement
  leaves out, so the other two fits are unchanged by it.
- Its release takes scatter by up to 20 dB between neighbouring keys about a
  fall of 38 dB from A0 to C6: played take by take, a key let go at C4
  knocked 34 dB louder against its note than one at C6. Each take keeps its
  modes and plays at the keyboard's trend, a Theil–Sen line through the
  takes' levels (`release_trend`); from F6 up the library plays no release
  and those keys take D♯6's. Its SFZ brings every take to about one
  loudness, so it sets no balance between the action and the notes: a key
  let go half a second after its strike, and a key landing, play no louder
  against a velocity-80 note than the grand's do at C2, C4 or C6 (as loud at
  C2, 11 to 13 dB under at C4, 44 dB under at C6).
- Its rises are capped at the hammer's contact, as the upright's are: the
  fit times them past it too, a median 2.5 ms but 35 partials over 30 ms.

It answers velocity through the shared response. Its median note sits
0.6 dB over the grand's at velocity 127 and 1.4 dB over at velocity 30 (each
key held, both channels' RMS from 50 to 750 ms), and its softest layer,
11.6 dB further under its loudest than the grand's, never plays alone. Its
soft pedal shifts the hammers, as a grand's does. Its output scale (2.8267)
brings typical playing to −9 VU on Reason's meter, with the other two. Through
the tube alone (`tubeScale` 1.3201) typical playing reads −10.03 VU, 1.03 dB
under the pair: within 0.5 dB, where the other pianos' tubes sit, its
loudest chords through the tube reach the red (+0.07 VU at −9.73 VU), and at
−10.03 VU they read −0.004 VU. Its A2 is recorded about 4 dB over its
neighbours in its three loudest layers, the keys between them play toward
it, and the tube hears more of the bass. The owner first chose a quieter
tube over evening out the A2, 0.1 dB past the half-decibel bound; the change
to the keys between recorded pitches (below) then raised those chords, and
asked again, between the tube 1 dB quieter and the A2 brought down to its
neighbours' trend, the owner chose the quieter tube, which
`KeyraLevels --check` allows the Kawai alone (1.05 dB). Its loudest chords
through the tube clear the red by 0.004 dB and its reading the bound by
0.02 dB, so a later change that raises those chords comes back to the
owner.

On its 23 dev notes, against the grand's data played on them, the Kawai's
own data sits closer to the recordings in tuning (2.87 against 4.17 cents),
attack (8.23 and 8.82 dB), early spectrum (9.45 and 9.55 dB), noise between
partials (8.77 and 12.66 dB), rise (4.99 and 8.02 ms) and level (3.96 and
7.27 dB), and further in partial levels (9.88 and 7.74 dB), decay (5.24 and
4.90 dB/s), image (5.28 and 4.52 dB), envelope (4.91 and 4.26 dB) and the
sustain spectrum (9.51 and 9.48 dB). Of the 33 notes and measures that
regress, the largest are B5's partial levels (11.44 to 22.43 dB), early
spectrum (11.06 to 17.30 dB) and attack (7.82 to 13.75 dB), D5's image
(4.91 to 11.64 dB) and A♯3's partial levels (5.95 to 11.30 dB)
([report](validation/kawai-recording-benchmark-2026-10-31.md)). At its
never-fitted pitches, then, the Kawai's partials stand further from their
recordings' balance than the grand's data does; the pitches it is fitted
from lie two to six semitones apart, and B5 sits between G♯5 and C6.

Fitted at the owner's request and checked by measurement; no one has
listened to it yet.

## 2026-10-31 — a key between two recorded pitches meets them over the levels' window

A key between two recorded pitches sets each blended partial's power between
the two pitches' in dB, so that its lanes' beating cannot put it under or
over both. That power was weighed from contact by e^(−t/0.4 s), the mean time
of the 50–750 ms window the layers' levels and the benchmark's gain are
measured over, and so it counted a lane that dies within the first 50 ms for
its whole energy. The Kawai's A6 fundamental holds such a lane: the keys
below it took a share of a burst the window never hears, and the engine's
F♯6 played 4.3 dB over both D♯6 and A6 (renders of the three keys; F♯6's
recordings stay sealed), past `Keyra.Engine`'s 3 dB. The power is now
integrated over the window itself (`windowPower`), as a build between two
pianos already measured it.

On the dev notes, against the engine before it: the grand's partial levels
move 5.39 to 5.33 dB, its early spectrum 4.55 to 4.52 dB, its sustain
spectrum 5.35 to 5.31 dB and its rise 4.76 to 4.61 ms, while its level moves
0.94 to 1.01 dB, with no regression
([report](validation/grand-between-window-benchmark-2026-10-31.md)). The
upright's attack moves 6.41 to 6.37 dB, its early spectrum 7.14 to 7.09 dB
and its rise 6.21 to 6.01 ms, while its partial levels move 8.39 to 8.46 dB
and its level 2.41 to 2.46 dB, with no regression
([report](validation/upright-between-window-benchmark-2026-10-31.md)). The
Kawai's early spectrum moves 9.81 to 9.45 dB, its attack 8.39 to 8.23 dB and
its level 4.00 to 3.96 dB, while its partial levels move 9.85 to 9.88 dB;
its three regressions are F♯7's level (8.10 to 10.14 dB) and partial levels
(9.22 to 9.88 dB) and B5's level (7.68 to 8.31 dB)
([report](validation/kawai-between-window-benchmark-2026-10-31.md)).

It moves typical playing, so the scales are re-pinned: the grand's to
0.7680 and 1.5139 (were 0.7699 and 1.5091) and the upright's to 2.2755 and
2.1763 (were 2.2040 and 2.1196), which puts the upright's median note at
velocity 127 0.4 dB over the grand's. Chosen by measurement, as the owner's
standing direction asks; no one has listened to it yet.

## 2026-10-31 — a palette: each part mixes any of the recorded pianos

The owner asked for a palette of parameters (strings, wood, detune, mics,
stiffness, unison spread) and presets that set them to play like one
particular piano, under other names, the user free to change any of them,
where the build could only blend two pianos. It continues their earlier
asks: one product, no strip but parameters and presets, and the power to
tune those parameters into hybrids by hand.

Each part of `keyra::Build` (strings, hammers, soundboard, action) now holds
a weight from 0 to 1 for each measured piano (`keyra::Mix`), played as
shares of their sum, so any number of pianos mix in any part; a part with no
weight plays the grand's. The engine mixes the pianos' values two at a time
in `Piano`'s order, each next piano at its share of the shares so far
(`fold`), so that two pianos mix exactly as the two-piano build mixed them
and more as that rule's weighted mean: every measured piano, every
two-piano build and every demo renders sample for sample as before. A body
mode the boards share mixes their powers at their shares, with the phase of
the largest share's; one only some boards have plays from those at their
share in power, as before. A strike's partials come from each piano's two
recorded pitches around the key, merged by order across the pianos, and an
order only some pianos play plays at their share of the hammers in power.
Stiffness, Unisons and Ring stretch what the parts build, as before. Of the
owner's list, detune is Unisons, how far each partial's unison strings sit
apart, the wood is the Soundboard part and the mics are the Tube Mic
control. Halfway between the grand and the upright every third key plays
within 0.93 dB of between the two pianos' levels, and at equal thirds of the
three within 1.37 dB of between the three's, soft, middle and full
(`Keyra.Engine`, under 2 dB).

In the plug-in the weights are twelve parameters, `strings1` to `action3`,
the n-th of each part the n-th of `Piano` (`weightId`), shown as percentages
and not offered for automation: a build is chosen for a part, not played. A
piano added later adds its four without changing the others'. The Build view
lays them out as a grid, a row per part and a column per piano under its
city, beside Stiffness, Unisons and Ring. The Piano control is gone and the
preset menu takes its place. A session saved with the Piano control and the
two-piano parts opens as the same build (`buildToward(piano, partner(piano),
…)`), and a state holding both kinds of parameter is refused.

The owner chose a weight per piano for each part over one knob per part
that sweeps the pianos in a row: four knobs, but only neighbours in the row
blend, never Helsinki with Hamamatsu directly. Checked by measurement; no
one has listened to a build of three pianos yet.

## 2026-10-31 — the pianos and the presets go by cities

The owner asked for presets of particular pianos under other names than
their makers', such as the cities the makers come from: Reason's identity
rule keeps makers' names, model numbers and trademarks off panels, patches
and copy. The front ends name the pianos by `keyra::pianoCities` and
`pianoKinds`: the Salamander grand is the Kakegawa grand, the Helsinki
upright keeps its city, and the VCSL grand is the Hamamatsu grand. Both
grands' makers come from Hamamatsu, so the Salamander grand takes Kakegawa,
where its maker builds its grands.

The bank holds ten presets. Concert Grand is renamed Kakegawa Grand and
Rehearsal Upright Helsinki Upright; the other six keep their names, and all
eight their program numbers, so a session recalls the preset it chose. Two
are added: Hamamatsu Grand, the third piano as built, and Three Cities, every
part at equal thirds of the three, both at the default voicing. A preset
sets the parts' weights, the modifiers and the voicing; Output, Tuning,
Quality, Mechanics, Tube Mic and the pedals keep their values.

The owner also named a Steinway. The model plays only the pianos it
measures, and a preset only mixes them, so no preset imitates one: the
Steinway grand for Decent Sampler would need its own fit and its author's
permission.

The README keeps eight demos, each a different side of the instrument: Studio
Grand, a brighter and narrower Kakegawa Grand, and Felt Upright, the felt
Felt Nocturne already shows, leave the set, and the two new presets take
their places with phrases of their own: Hamamatsu Grand plays two voices
without the pedal, each line heard on its own, and Three Cities a chorale
whose chords sound the blend across the range. The renamed presets keep their
phrases. Each
file takes its preset's program number (`01-kakegawa-grand` to
`10-three-cities`), and `Tools/write_preset_midi.py` checks the set against
the bank.

Hamamatsu Grand fails `Keyra.Levels`. Through the output stage its chords at
velocity 127 read a median 0.04 dB under the same chords at 110, where every
other preset's read louder, as the step check asks. Before the stage they
read 1.5 to 2.9 dB louder (chord by chord, five rounds each), and the stage's
guard, which keeps its loudest chords at −1.2 VU, takes the step: lowering
the Kawai's output gives back 0.09 dB of it per dB, and the in-between
change above is not the cause (before it the step read −0.05 dB). Asked
whether its top velocities may level off there, whether the Kawai plays
1 dB quieter overall (typical playing at −10 VU, its chords at 127 then
0.05 dB over 110) or whether the preset waits, the owner chose to let them
level off. `KeyraLevels --check` now lets the chords of a preset on the
Kawai's hammers alone read up to a quarter decibel under 110, short of the
0.4 dB change listeners can just detect in a broadband sound, and holds
every preset's single notes to playing louder at 127 than at 110 (the median
over the 22 typical notes). Hamamatsu Grand's single notes read 2.28 dB
louder at 127 (21 of 22 notes), the other presets' 1.58 to 1.90 dB, and its
chords at 127 are brighter: their spectral centroid over the first 0.3 s
rises from a median 477 to 551 Hz, brighter in 38 of 40 chords, as the
Kakegawa grand's rises from 551 to 614 Hz.

## 2026-10-31 — a fourth and a fifth piano, the Hamburg and New York grands

At the owner's direction (2026-10-31), two more libraries are fitted: Jon Meyer's
"Steinway Grand" for Decent Sampler and David Hawkins's "Grandpa's Piano"
(Pianobook).

They go by the cities of their maker, as the owner chose. The 1933 Model L of
"Grandpa's Piano" was built in New York. Hamburg is the maker's other city and
claims nothing about where Jon Meyer's piano was built, which nothing says.
They are `Piano::hamburg` and `Piano::newyork`, added after the others so saved
songs and patches recall those as before; older sessions load with no weight
on them, and their presets go after Three Cities (programs 11 and 12).

**Hamburg.** Twelve pitches every seven semitones, four layers, two round
robins, a release take per pitch, 48 kHz/24-bit. Train is the first takes at ten
pitches. Dev is E3 and C♯5 (MIDI 52, 73; the library names them E2 and C♯4). The
second takes are `repeat`: same-layer pairs correlate at a median 0.94 over the
impact, and C♯5's Dyn2 RR2 and Dyn3 RR1 are one strike. **It has no sealed set**:
a third held-out pitch would leave a 21-semitone hole among twelve. The decoder
cuts each take at the preset's start point less 20 ms, because the pre-roll holds
unrelated sounds up to −39 dBFS that the onset would take for the strike. The
preset gives one take's rootNote as 37 where its zone says 101. Its undamped
strings stand too faintly for the 20 dB their shared fall asks (1 % of tones), so
it is read from 16 dB: 0.76/s, 0.77/s from 14 dB. Lowering the margin slows the
rate on New York too (2.64/s at 20 dB, 2.36 at 16), so Hamburg's may read slow.

**New York.** Five layers on 17 pitches every five semitones, seven unpitched key
noises, 44.1 kHz. Train is 13 pitches, dev MIDI 39, 64, 84 and the single FF
takes at 100 and 105, sealed MIDI 54 (not opened). The FF takes peak within
2.4 dB of full scale, which raised normalisation, but their raw levels are kept:
F to FF is the steadiest step of all (SD 1.18 dB, the others 2.79 to 3.54), which
take-by-take gain would have scattered; FF across the keyboard (SD 3.17 dB) is no
jumpier than F (3.68 dB); and the peaks, 0.765 to 0.9996, hold no one ceiling.
G5, A♯6, D♯7 and G♯7 have no mapped FF take. Carried on by slope, D♯7 rose 41 dB
from velocity 91 to 127 where F6, with its FF, rises 11 dB, and put a ten-note
chord past the engine's headroom. They now take the median recorded F to FF step
(5.96 dB), so their loudest strikes are F's tone, louder: their FF tone is not
measured. Its pedal noises are pinned and not played.

`responseFloorDb` stays over the first three pianos: Hamburg's softest layer
stands 15 dB over theirs, and raising the floor would change how they answer
velocity. Below its softest layer Hamburg continues on that layer's slope, so it
plays softer than it recorded.

The first three pianos, 13 solo, two-piano and three-piano renders and all eight
demos are sample for sample the same as before. Each piano's typical playing
reads −9 VU and its tube the pair's (`KeyraLevels --check`), at scales of 2.3152
and 1.5936, and 0.6823 and 1.7227. `Keyra.Engine`'s ring measure now renders 5 s,
as Hamburg's C4 falls 20 dB past the old 3 s at Ring 1.

On its 8 dev notes, against the Kakegawa grand's data played on them, Hamburg's
data sits closer in tuning (0.56 against 2.06 cents), attack (6.47 and 9.01 dB),
early spectrum (5.78 and 8.95 dB), sustain (7.32 and 10.92 dB), noise (5.39 and
10.13 dB), image (4.17 and 5.00 dB), envelope (4.39 and 4.82 dB), rise (3.87 and
11.97 ms) and level (1.78 and 3.71 dB), and further in partial levels (7.32 and
6.38 dB) and decay (6.14 and 3.03 dB/s), with five regressions, largest C♯5's
decay (3.93 to 8.97 dB/s)
([report](validation/hamburg-recording-benchmark-2026-10-31.md)). On its 17,
New York's sits closer in partial levels (9.94 and 12.88 dB), tuning (2.37 and
5.75 cents), attack (8.72 and 9.34 dB), early (7.88 and 8.70 dB), sustain (9.13
and 10.27 dB), noise (8.91 and 10.23 dB), image (6.25 and 7.42 dB), envelope
(3.60 and 4.55 dB), rise (8.51 and 9.99 ms) and level (2.18 and 4.59 dB), and
further in decay (7.75 and 6.78 dB/s), with 13 regressions, largest the single
FF take at 105's decay (5.54 to 29.05 dB/s)
([report](validation/newyork-recording-benchmark-2026-10-31.md)).

Fitted at the owner's request and checked by measurement; no one has listened to
them yet.

## 2026-11-01 — a sixth piano, the Belmont grand

The owner asked for Pianobook's "Mom's 1974 Baby Grand" (The Imperfect
Drummer, Brian Peat; Decent Sampler 1.5) as Belmont: a 1974 Wm. Knabe & Co.
baby grand, reconditioned with its felts sanded, recorded by one pair of sE 8
cardioids in X/Y at the hammers with the lid fully open, 48 kHz/24-bit. The
library states no licence; the owner takes its use as allowed and asked for a
credit only, given in `THIRD_PARTY_NOTICES.md` as for the other libraries, and
nothing from it is copied. It holds 30 pitches a
minor third apart from A0 to C8 in three layers (Soft 1–48, Med 49–104, Hard
105–127, one to three round robins in the first two), a key-release take per
pitch and five sustain-pedal noises each way. `Tools/decode_belmont.py` reads
the folder or the `.dslibrary` and `Tools/corpus/belmont-grand.json` pins
every take's PCM and decoded WAV by SHA256.

Before any fit, the split (`split-belmont-2026-11-01.json`) set each layer's
first take of 27 pitches, their key releases and the first pedal noises down
and up for training, D♯2, D♯4 and D♯6 for dev, and every later round robin
and pedal noise as repeats. Nothing is sealed: a fourth held-out pitch would
leave a sixth hole of six semitones, and the library holds no other session.

Every note take is peak-normalised by layer (Soft −11.9, Med −9.9, Hard
−7.9 dBFS), so the library records no level between its layers or its keys.
Asked how the layers should be levelled, the owner chose the library's own
velocity curve: Decent Sampler scales a note by velocity/127 when no group
sets `ampVelTrack`, so each layer plays at its velocity midpoint's gain
against Hard's (Soft −13.33 dB, Med −3.56 dB). At the owner's request each
note is then brought to a smooth trend over the keyboard: per layer, a
locally weighted line (tricube over ±10 semitones, two robust passes) through
the training takes' 50–750 ms levels. Key to key, the median step at velocity
80 went from 0.67 to 0.39 dB and the largest from 3.58 to 3.07 dB. Both are
choices, not measurements: the recordings cannot say how loud the piano's
layers or keys stood against each other. The key releases and pedal noises
keep their recorded levels, and the preset's own balance plays them 3.5 dB
under the notes (Key Vol 0.3 against 0.1 at +6 dB).

The fit is the fixed fitter's (2026-11-01, the soundboard kept off the
strings' leftovers): 27 anchors, 595 partials, 60 body modes, 17 noise bands,
key-release knocks, and the pedal's knocks down and up, which Belmont plays as
the Kakegawa grand plays its own. Its strings ring under the pedal at the
Kakegawa grand's rates, as every piano's do.

The other five pianos, a blend of all of them and both microphones render
sample for sample as before. Belmont's typical playing reads −9 VU at an
output scale of 1.2453.

Through the tube alone its typical playing reads the pair's −9 VU at a tube
scale of 1.7607, but its loudest chords there read +0.61 VU, in the red. Its
A2 and D♯3 to F♯3 are recorded nearly all fundamental (A2's within 0.3 to
2 dB of the whole note's level, where F♯2's and C3's sit 7 to 13 dB under),
the tube's response favours that range, and the chord of A2, E3, A3, C4 and
E4 at velocity 127 reads 1.7 dB over Belmont's next loudest through it. A
quieter tube hardly moves those chords through the output stage's
compressor: 1.1 dB under the pair they read +0.48 VU, 3 dB under +0.15 VU.
Asked between letting them read up to +0.7 VU, a tube about 5 dB quieter
and A2's fundamental drawn toward its neighbours', the owner chose the
first: `KeyraLevels --check` allows Belmont alone loudest chords under
+0.7 VU at Mic 1. Every sample still stays under the stage's −1.5 dBFS
ceiling, and Mic 0's loudest chords read −0.70 VU.

On its 9 dev notes, against the Kakegawa grand's data played on them,
Belmont's data sits closer in partial levels (7.00 against 9.68 dB), tuning
(1.56 and 3.05 cents), attack (6.81 and 9.50 dB), early spectrum (7.47 and
12.02 dB), sustain (8.43 and 11.88 dB), noise (7.75 and 14.83 dB) and level
(0.44 and 1.68 dB), and further in decay (4.77 and 4.34 dB/s), envelope (4.61
and 4.36 dB) and rise (20.54 and 10.74 ms), with seven regressions, largest
D♯2's rise (13.95 to 34.59 ms)
([report](validation/belmont-recording-benchmark-2026-11-01.md)).

Fitted at the owner's request and checked by measurement; no one has listened to
it yet.

## 2026-11-01 — Mom’s Baby Grand velocity interpolation

The owner compared the two lettered Mom’s Baby Grand clips and chose **B**:
“B sounds more even.” A is the unchanged `ba3ee99` engine; B is the guarded
whole-partial velocity interpolation, with the same poles, measured layers
and piano data. This choice supports retaining that velocity-interpolation
direction. It is a listening preference, separate from recording-error
measurements; the pitch-rate interpolation was not part of these clips.

The material is seven isolated A1/MIDI 33 notes at recording-layer coordinates
77, 85, 92, 97, 102, 109 and 116. Each file is 8.4 seconds of 48 kHz stereo
audio through the native engine in steady measurement mode, with identical
controls, events and fresh-engine seeds. A and B share one trim derived from
A; no independent file or per-note matching was applied because evenness of
dynamics was being judged. Files, the separately written key and full receipt
remain under `out/realism/listening/velocity-interpolation/`.

A WAV SHA256: `43d851e01cbf3af10447fa24f4adc890ec6075932e3658225a6ec605919cc917`.

B WAV SHA256: `8c7981564e8b8f7718e88cd4af75db52dc322cd8fc1628a715d1e75748c163d4`.

## 2026-11-01 — Mom’s Baby Grand soft-pedal interpolation

Asked which new soft-pedal clips sounded more natural and consistent, with
the option to choose differently for the upper and bass phrases, the owner
answered **“B”**. With no phrase-specific exception, this records B for both.
This is a separate decision from the earlier velocity-progression preference.

A is accepted 0.4.2; B carries each measured component’s soft-pedal bias
through interpolation instead of assigning it again after sorting decay rates.
The latter sorting could abruptly exchange biases between components. B keeps
the measured coefficients and pedal constants. The choice supports promoting
this shared change while retaining 0.4.3’s independent reset fix; combined
validation must establish fresh-playback equivalence to B. It does not establish
that every piano or every intermediate note sounds better, or supply a recorded
soft-pedal calibration target. Mixed-string continuity remains unproven.

The upper phrase uses MIDI 84–93 at velocity 120 (11.5 seconds), including the
known 86→87 and 89 level tradeoffs. The bass phrase uses MIDI 27–30 at velocity
32 (11.75 seconds), with two-second holds including the changed rise at 28.
Both use Belmont, soft pedal fully down, 48 kHz stereo, normal strike variation,
identical events and controls, and a fresh seed of 1. B is whole-file RMS matched
to A: +0.351716 dB upper, +0.294457 dB bass. Each pair then shares a trim to a
maximum peak of −3 dBFS; there is no per-note matching. Files and the frozen
pre-listening receipt/key remain under
`out/realism/soft-order-audit/listening-tradeoffs/`; their then-pending status is
historical, and this entry records the later answer.

- A source SHA256: `8afcba98abe2029b8adcff5b49e846312476b199f2e9383d8779f91957d55ee0`.
- B source SHA256: `e6e8c22f851eaf9a2c738a5607266ca6331655cee632dc32e2bf24ec492b6991`.
- Upper A WAV SHA256: `4d91acea2ce521a45f146ba952a8420f7cf4ec92e9b5ab70a5344f448eb89285`.
- Upper B WAV SHA256: `cbbc9d008b6d20388e7b574678448323d8837cefbaf9f8de37a2e1c0dd91cb1b`.
- Bass A WAV SHA256: `b005eaaa8dd7e9d731584e73f2e192008e9b706b0b46142dd4dc12d324f14e24`.
- Bass B WAV SHA256: `8c1c070b8495c40798755008c0907c83ff483ce10fa783da6357555db66916ac`.

## 2026-11-01 — quieter key-landing action in the Moonlight performance

The owner described the mechanical sound as too loud on every Moonlight note
press. After initially liking C and B and hearing the key, the owner explicitly
chose **B**: “ok then lets go with B,” requesting a Mechanics volume control
with that balance at **0.4** on the knob. This authorizes the quieter playback
default across the instrument. It is a listening preference, not a claim that
the physical action level was measured or independently preferred on all six
pianos.

Version 0.4.5 sets new instances to physical Mechanics gain **0.175**, exactly
the Moonlight B setting. The existing visible knob receives a continuous taper
with this setting at 40%, silence at 0%, and the existing maximum gain 2 at
100%. The taper is an interface choice anchored to the requested position;
it is not an acoustic fit. Raw engine values and the host parameter's linear
0–2 range remain unchanged so existing state and automation keep their sound.
Old plug-in states that omit Mechanics explicitly recover historical gain 1.
The native renderer continues to accept raw gain through `--mechanics`.

A is the current 0.4.4 engine and Moonlight demo settings, Mechanics 0.35.
B uses Mechanics 0.175, halving action excitation amplitude (−6.0206 dB).
C uses Mechanics 0. All other notes, velocities, pedals, settings and seed are
identical. All letters use the same gain, retaining the same tonal level while
judging action-to-tone balance. The 19.900049-second excerpt starts at
20.375066 seconds and is rendered with its complete preceding musical history.
The common export gain is +44.869798 dB, making A's excerpt RMS −24 dBFS.

In this pedalled Hamburg passage, Mechanics changes the added key-landing
action and its downstream sympathetic response. It does not scale the separate
hammer/body knock, modal attack or impact-noise burst. Hamburg has no active
pedal-knock recording, and the passage's note releases occur while sustain
suppresses the combined release knock. C therefore retains the piano's tonal
and hammer/body attack. The owner was told this key after answering.

The A−C causal difference is 46.345 dB below A in whole-excerpt RMS and peaks
at −49.342 dBFS at this common listening gain. B's effect is half A's within
floating-point error. These descriptive levels are not an audibility threshold
and do not override the owner's preference. The separate Helsinki controls
have not received a verdict. No physical keybed amplitude is identified by
this listening choice; the existing Mechanics control is a playback balance.

The frozen files/key/receipt are in the local review folder
`Downloads/Keyra Mechanics Listening 2026-11-01/`; the reproducer and native
controls remain under `out/realism/native-component-audit-20261101/mechanics/`.
The WAVs are review artifacts and are not committed.

- Receipt SHA256: `15f6ea5b84dbb38eb59d5093981578cd54e8d056f182ea4cfa5b6302a98010e5`.
- A WAV SHA256: `c40418816a33cd6660c70d4b2ff389d0f73dffce766fd4a6bb0b64c104c635ea`.
- B WAV SHA256: `4bb940ce17541fdc1b58cb4924e47cd440785cda8118a29daf2ef78885202654`.
- C WAV SHA256: `968b08ba5265d082737b489b839290b6cfbe26a70612d3e79d41ae1daca75204`.

## 2026-11-01 — Belmont clarity across dynamics

The owner described Belmont as very dark and chose **C** in the subsequent
three-way Moonlight comparison. A was unchanged 0.4.5 with additional velocity
colour strength 0.4; B reduced this to 0.2; C removed this additional colour.
All three retained the instrument's measured velocity layers, note envelopes,
body, noise, pedals and mechanics. The identical 19.900049-second passage was
rendered with its preceding history and controls, then matched in whole-excerpt
stereo RMS to −24 dBFS with a single scalar per letter and identical 5 ms cut
fades. There was no equalization or compression.

Version 0.4.6 adopts C for Belmont's hammer contribution only. The other five
pianos retain strength 0.4. A mixed build changes according to its Belmont
hammer share. Existing Belmont presets and saved sessions intentionally gain
this clearer voicing; control ranges and automation identifiers are unchanged.
This is an owner's voicing preference, not a new estimate of physical hammer
behaviour or a claim that every piano should have the same spectrum.

The frozen review files and separate key are in
`Downloads/Keyra Belmont Tone 2026-11-01/`; the reproducer is under
`out/realism/belmont-colour-control-20261101/listening.py`. The retained C WAV
SHA256 is `f8d0da8d6bef957482def9de751ec93178bfc55bab298cc42554722c5cb265fc`.

## 2026-11-02 — Belmont factory Brightness: C

The owner chose **C** after revisiting the piano-only clips and asking for
their key. A used the accepted Belmont voicing at Brightness 0.5; B used
0.625; C used 0.75. This is a separate audition from the 2026-11-01 C choice
above, which removed additional velocity darkening.

The initial accompanied comparison did not establish a preference: the owner
said the backing obscured the piano. The same 17.171938-second phrases were
then presented solo, and the settings were disclosed before the final C
selection. This is an informed voicing preference, not a blind listening
result or an inferred physical measurement.

Version 0.4.9 applies Brightness 0.75 when loading the **Belmont Grand** factory
preset. The knob remains fully adjustable. Other presets and the engine's
general parameter defaults remain as before; loading existing saved states
restores their explicit brightness. Changing piano-build weights alone does
not overwrite the current voicing controls. The agreed Mechanics default
remains at UI 0.4 / raw gain 0.175.

The frozen audition is in `Downloads/Keyra Belmont Mix Clarity 2026-11-02/`.
Each complete piano performance received one scalar RMS match to −25.8 dBFS
before phrase extraction, followed by a common export gain. All MIDI, seeds,
and other controls were identical. Those listening trims are not preset
output-gain changes. Solo C WAV SHA256:
`a077016ab499c334435897917f8125bf50a4a8d29db00448bd6a6e50ec664864`.

## 2026-11-02 — ship B at the usual playing level

The owner selected B in the six-piano forte comparison and asked to ship it
without lowering piano levels. Both clips played three chords at MIDI 80,
110 and 127. A used the previous factory Output of 0.70. B drove the same
instrument at 0.35 and used one level match per piano for its moderate
strikes. The same export gain was then applied to A and B within each piano.
The owner’s choice was “B is indeed better, ship it”.

0.4.11 makes the half-drive response available at factory Output 0.70 and
restores 6.02 dB after the original guard. An additional short gain curve
catches peaks above the sample ceiling. The decision favors the stronger
forte response, including chords above 0 VU on a meter with 12 dB offset.
The selected Mechanics position is 0.4 and the Belmont Grand factory
Brightness is 0.75. [Measurements](validation/forte-response-2026-11-02.md).

## 2026-11-03 — chords carry their per-key trims

Found in review, not chosen by ear. Since 0.4.13 the per-key level trim of the
keys below C7 was applied one process() call after the strike and only for a
voice no other voice shared a clock with, so a chord struck at once lost every
note's trim while the same notes a sample apart kept them; the late body
ring's crowding reduction likewise went to the first note of a chord alone,
whichever note that was. A fifteen-note chord (`Keyra.Engine`, fifteen
keys from D2 to A♯6 at velocity 80) summed to its notes struck alone to
−29 dB; with the trim applied at the strike and one crowding verdict per
chord it does to −38 dB, and the test pins it at −35 dB. The fix itself leaves
single notes byte-identical to 0.4.13; the re-pin below is what changes them.

The chords of the demos and of `KeyraLevels` now read lower: typical playing on
the default controls −0.04 dB on the grand, −0.27 on the upright and −0.48 on
the Kawai; the other pianos hold. Output scales are re-pinned as earlier
decisions did (upright 2.2755 → 2.3474, Kawai 2.8267 → 2.9873) with their tube
scales (2.1763 → 2.1097, 1.3308 → 1.3035) so that their default sound and Mic 1
return to the readings approved on 2026-11-02, and the Belmont's tube trim
is eased from 0.351552439 to 0.3216 dB for its Mic 1 (−9.52 → −9.49 VU, the
approved −9.485). Four presets' typical levels still move and their rows in
`Tests/Fixtures/dynamics/ApprovedLevels.h` are re-baselined to the two
decimals the tool prints: Studio Grand −10.006 → −10.17 VU, Open Strings
−7.985 → −8.04, Felt Upright −15.755 → −15.86 and Three Cities −10.500 →
−10.29 (its three pianos' trims largely cancel, so it gains only the
re-pinned scales). No preset's loudest chord rises over its approved level.
These are measured level shifts of 0.06 to 0.21 dB, small enough that no
listening test was run; the owner may keep the previous chord behaviour by
reverting the commits "give every note of a chord its per-key trim and
crowding verdict" and "re-pin the upright's, Kawai's and Belmont's levels".

The same release runs steady partials and body banks four at a time. The
eight factory demos are byte-identical before and after, and each takes 14 to
21 % less DSP time (paired runs, median of three, 4-thread Xeon at 2.3 GHz).

## 2026-11-04 — the Belmont grand is removed

The owner asked for it: "remove belmont piano, it sucks, keep only 5
pianos". Keyra plays five measured pianos again, the Kakegawa, Hamamatsu,
Hamburg and New York grands and the Helsinki upright, and its factory bank
twelve presets. Removed with it: its measured header, decoder, corpus and
split pins, stored-number archive, fit receipt, its factory preset and its
Build column, the tube-output trim only it used, and its credit in
`THIRD_PARTY_NOTICES.md`. `keyra::Piano` loses its last value, so the other
pianos keep theirs. A session saved with Belmont weights loads with those
weights dropped and plays the other pianos at their shares, or the Kakegawa
grand's part where Belmont was a part's only piano; a session saved on the
Belmont Grand program loads the first program. The stored-number pipeline's
tests, which ran on Belmont's archive, now run on Hamburg's
(`Tests/Fixtures/measurements/hamburg-accepted.json.gz`), and the recipe only
Belmont's authored WAVs used is gone. The other pianos' measurements, fits
and factory dynamics rows are unchanged by the removal; the velocity masks
are regenerated because they are tabulated over the pianos.

## 2026-11-04 — a key between two pitches keeps a stereo image between theirs

Reported by the owner on Pop Upright: "huge difference in tone between B2 and
A#2 (127)". Found by measurement, not chosen by ear. A key between two
recorded pitches took its partials' phases and channel phase difference from
the nearer pitch (2026-10-28, to keep a partial's lanes from cancelling in
the right channel), so every partial's whole stereo image switched at the
pitches' midpoint. On the upright A2 holds its second partial 3.5 dB more out
of phase between the microphones than in phase and C3 9.4 dB more in phase:
A♯2 played A2's image and B2 C3's, so the octave partial in the sum of the
channels jumped 7.3 dB from A♯2 to B2 at velocity 127. A Width under 75 %
mixes that sum into each channel: at Pop Upright's 50 % the left channel's
octave partial jumped 6.9 dB there. Each lane's right channel is now turned by one angle per partial so that
the partial's lag of right behind left over the 50–750 ms window moves from
one pitch's to the other's along the shorter arc as the key moves between
them. All lanes turn alike, so they sum as one pitch's do and no channel's
power changes at the default Width. Across A2 to C3 the interchannel angle
of partials 1 to 4 at the in-between keys sits within 3.2° of the straight
line between the pitches', where it missed it by 36 to 56° (`Keyra.Engine`,
held to 20°), and the octave partial in the sum of the channels steps 5.3 and
3.3 dB from A2 to A♯2 to B2 where it stepped 1.0 and 7.3 dB. Recorded pitches
are unchanged; every key between two of them changes in its stereo image
only, and in its level per channel only where Width is under 75 %. Against
the recordings' dev cases, which are all between recorded pitches, every
benchmark score but the onset rise and the level moves by 0.04 or less on
the Hamamatsu, Hamburg and upright. The level error falls or stays: upright
2.53 → 2.41 dB, Hamburg 1.89 → 1.83, Hamamatsu 4.34 unchanged, New York
5.62 → 2.25.
The onset rise error grows on three pianos (Hamamatsu 5.24 → 6.09 ms, upright
5.74 → 6.17, Hamburg 3.77 → 4.00) and falls on the New York (8.63 → 8.19):
turning the right channel moves where its first peaks fall, and at the
Hamamatsu's D♯2 the 90 % point of the summed envelope moves between two early
peaks of nearly equal height, while each channel's own rise changes by under
2 ms. A lettered listening set of the reported keys went to the
owner (`ab-2026-11-04-pop-upright-a2-c3`).

That no channel's power changes holds for one note. In a chord the notes'
coincident partials now add at other angles, and the tube hears the sum of
the channels, so `Keyra.Levels` moved. Typical playing through the tube alone
read off its approved level by −0.27 dB on the grand, −0.55 on the upright,
+0.42 on the Kawai, +0.53 on the Hamburg and −0.22 on the New York, and each
piano's `tubeScale` is re-pinned to bring it back (1.5139 → 1.5619, 2.1097 →
2.2468, 1.3035 → 1.2426, 1.5936 → 1.4988, 1.7227 → 1.7668). Six presets'
typical levels still read off theirs (Studio Grand −0.07 dB, Felt Nocturne
+0.05, Open Strings −0.09, Helsinki Upright −0.06, Pop Upright +0.20, New
York Grand −0.05), and five loudest-chord readings rise over their approved
ceilings (Kakegawa Grand +0.08 dB, Warm Walnut +0.14, Open Strings +0.01,
Hamburg Grand +0.05, the grand through the tube +0.10); no sample passes the
−1.5 dBFS ceiling. Asked whether to accept these readings, lower the grand
and the Hamburg until no loudest chord rose, or drop the fix, the owner chose
to accept them, and `Tests/Fixtures/dynamics/ApprovedLevels.h` now holds
them. `Keyra.FactoryDynamics`, the 0.4.11 chord audit's step floors and
level limits, already failed before the fix: with the Belmont removed 588 of
its 2,120 pairs sat under their floors (699 on main with six pianos). With
the fix and the re-pinned tubes 988 do, 179 of those 588 now clearing
theirs, and 11 chords pass the audit's maximum levels: the Kakegawa grand's,
its tube's and the Hamburg's loudest readings above, which the owner
accepted, and the grand's tube by up to +0.41 dB in the chords struck at 101
and 121 and by +0.10 dB in the velocity ladder. Its floors and limits are
unchanged.


## 2026-11-04 — a key between two pitches keeps each partial between theirs

Found by measurement after the A♯2/B2 fix, when the owner asked whether it
covered every note of every piano and for a more robust way to prevent such
jumps. Rendered for 1 s at the default controls, every key between two
recorded pitches on the five pianos was measured for its first eight partials
in each channel from 50 to 750 ms after the strike. At velocity 127, 66 of the
312 such keys played a partial within 20 dB of their strongest more than 3 dB
outside both neighbours in a channel, and 13 more than 6 dB outside. The worst
was the Hamamatsu's B7, whose second partial played 21.5 dB over both A7's and
C8's in the right channel. There were two causes. A lane's decay rate was
mixed in its logarithm, so a lane paired between a quiet one barely decaying
and a loud fast one started between them but decayed far more slowly than the
loud one: the Hamamatsu's A7 holds a lane of its second partial at −103 dB
decaying at 0.08/s, C8 the lane it meets at −45 dB and 36/s, and B7's decayed
at 4.8/s. And a partial's level was set so that its power over both channels
together sat between the pitches', so one channel could play far outside both
pitches' while the other made up for it: the Hamburg's E1 at 127 played its
twelfth partial's right channel 11.4 dB under both C1's and G1's.

Each lane's decay rate is now mixed in 1/s, so that with its level mixed in dB
its level at every moment is the same mix of its two pitches'. A partial's
power over the 50–750 ms window stays where it was, at its place between the
pitches' in dB, and its balance, the left channel's power over the right's, is
now set at its place between theirs in dB too, unless that would take a
channel outside both pitches': that channel then stops at the pitch's power it
would pass. Recorded pitches are unchanged byte for byte, as is every train
case's score on every piano: the per-key trims are derived from each key's
total power, which does not move.

The owner chose "Fix it, A/B the worst keys first", and a lettered set of each
piano's two worst spans went to them (`ab-2026-11-04-between-keys`): A the
shipping engine, B the decay rates mixed in 1/s, C each channel's power set
between the pitches' in dB, D both. No letter has been reported. Measured
before shipping, C failed where a partial's image swaps sides between the
pitches: set channel by channel in dB, its total fell under both pitches', the
Hamamatsu's A4 2.4 dB under both its neighbours and D's worst 5.2 dB, and the
moved totals changed the per-key trims and with them the recorded pitches. The
balance rule above replaced C; it was not itself in the set. Measured against
the recordings, the balance rule alone moves the dev cases' partial error by 0
to −0.05 dB and their channel level difference error by −0.22 to +0.07 dB,
except +0.72 dB on the Hamburg. The decay rates mixed in 1/s cost +0.03,
+0.03, +0.29, +0.57 and +0.49 dB of partial error on the Kakegawa, upright,
Hamamatsu, Hamburg and New York, and change the late decay error by −0.02,
−0.43, +0.17, −0.52 and −0.14 dB/s. Asked "Land the decay-over-time part now,
or leave it to the experiment?" with that cost, the owner chose "Land both
parts now". The choice was made on these measurements, not by ear; it licenses
this blend for keys between recorded pitches and no fit of any single key.

Every dev case, paired, from `Tools/compare_benchmarks.py` (none of these
pitches was fitted):

| Piano | partial_db | decay_db_s | sustain_db | envelope_db | ild_db |
| --- | --- | --- | --- | --- | --- |
| Kakegawa | 5.31 → 5.33 | 2.26 → 2.24 | 5.33 → 5.42 | 2.69 → 2.74 | 2.42 → 2.48 |
| Helsinki upright | 8.41 → 8.44 | 4.36 → 3.93 | 8.81 → 8.81 | 4.88 → 4.80 | 4.34 → 4.23 |
| Hamamatsu | 9.82 → 10.09 | 5.16 → 5.40 | 9.53 → 9.64 | 5.08 → 5.39 | 5.36 → 5.27 |
| Hamburg | 7.28 → 7.84 | 5.61 → 5.14 | 7.37 → 7.53 | 4.43 → 4.21 | 4.27 → 4.99 |
| New York | 10.12 → 10.56 | 7.47 → 7.29 | 9.99 → 10.48 | 4.48 → 4.94 | 6.19 → 5.97 |

It lists 20 regressions over its tolerances. On the Kakegawa, D♯7's ild_db
rises 1.31 → 2.16. On the upright, B3's sustain_db rises 6.56 → 8.53 and its
envelope_db 4.04 → 5.35. On the Hamamatsu, F♯7's ild_db rises 0.06 → 3.62, its
icc 0.56 → 0.69, its decay_db_s 9.63 → 15.42, its partial_db 9.80 → 11.12 and
its envelope_db 5.48 → 6.28; B5's ild_db rises 9.09 → 10.44, A♯3's envelope_db
6.94 → 7.64 and G7's 3.32 → 3.83. On the Hamburg, E3's ild_db rises 4.50 →
5.61 and C♯5's partial_db 5.76 → 6.82. On the New York, E7's envelope_db rises
3.21 → 5.60, its decay_db_s 3.68 → 8.19, its partial_db 8.88 → 9.96 and its
sustain_db 12.26 → 12.94; C6's envelope_db rises 5.15 → 6.28 and its
sustain_db 10.17 → 11.29, and E4's partial_db 9.44 → 10.09.

Over the same renders as the scan, keys with a partial more than 3 dB outside
both neighbours fall at velocity 127 from 11, 10, 16, 21 and 8 to 4, 8, 15, 7
and 5 on the Kakegawa, upright, Hamamatsu, Hamburg and New York. Keys more
than 6 dB outside fall from 13 to 2, the Hamburg's and the New York's, and the
worst miss falls from 21.5 to 6.7 dB, the New York's C♯7 fundamental, which
was 6.2 dB outside. At velocity 80 they fall from 35 to 23, though the
upright's rise 3 → 6 and the New York's 3 → 5, and those more than 6 dB
outside fall from 3 to 1. The partials' data now sits between the pitches'
exactly, so what remains comes from what these renders add to it, such as the
body, the per-key trims and the hammer's contact; which of them, this does not
measure. `Keyra.PitchBlend` now guards the data itself, on every piano at
every recorded layer, halfway between layers and both velocity ends: across
113,127 shared partials of 4,056 keys and velocities, each partial's power
over both channels is within 3 × 10⁻¹³ dB of its place, each channel inside
its pitches' (the shipping engine 13.0 dB outside, D's total 5.2 dB off its
place), a balance off its place only where a channel is held at a pitch's
(9,821 partials, up to 18.7 dB), and each lag on its line. `Keyra.Engine`'s
whole-note check now covers all five pianos, its worst 1.91 dB at the New
York's F2 against the 3 dB limit (shipping: 1.88). The Hamamatsu's B7 still
plays its second partial up to 7 dB over both neighbours in its left channel
from 200 to 450 ms, where the fit splits it into lanes differently at A7 and
C8 (README, Known gaps). `Keyra.Levels` moves with it, by up to 0.27 dB in
typical playing and 0.86 dB through the Hamamatsu's tube; the output and tube
scales are re-pinned after the forte-noise refit, under their own entry.

## 2026-11-04 — forte notes no longer ring a hiss over their partials

Reported by the owner: "in all pianos, there is a weird noise, example: C4 at
velocity 127 for hamamatsu". Between a note's partials the engine plays band
noise, the board's ring after the strike, measured per third-octave band from
the recordings. Above each note's fundamental a band's level was the mean
power of the bins between the partials. At a hard strike those bins also hold
tones that are not noise: the string's phantom partials at the sums of two
partials' frequencies (the Hamamatsu's C4 at 127 holds f8+f9 at 4482 Hz, 135
Hz under its 17th partial) and high partials the fit does not track. The mean
counted them, and the engine played their power as a hiss that rang for about
half a second over every forte note. On a spectrogram of the Hamamatsu's C4 it
carried a cloud of noise from 2.5 to 12 kHz dying over half a second, where
the recording of the same note shows tonal lines.

`Tools/fit_realtime_modal.py` now measures every band by the median of its
bins' powers over ln 2, the estimator it already used under the fundamental,
which passes over the few bins a tone holds. Only the five pianos' `noise` and
`noiseBands` change; partials, body, knock, action and the velocity masks are
the same numbers. Measured on 0.4.14 with and without the refit, in the first
300 ms of C4 at 127 the take's third-octave bands from 8 to 16 kHz fall by up
to 10.5 dB on the Hamamatsu, 26 dB on the upright, 8.1 dB on the New York, 7.6
dB on the Kakegawa and 1.8 dB on the Hamburg; below 5 kHz the partials
dominate every band and none moves more than 2 dB. The upright's 12.7 kHz band
falls silent after the knock, and its 8 kHz band at C4 rises 5.9 dB: with the
median only two of that note's five layers measure it, and a band measured at
fewer than three is filled from the neighbouring notes, as for every piano.
The fit's receipts now name the fitter and analysis sources as they stand;
since the Belmont's removal they had named the ones before it, so
`Tools/evaluate_recordings.py` refused to run.

A lettered set (`ab-2026-11-04-forte-noise`: A the shipping 0.4.14, B the
median) went to the owner, and no letter has been reported. The refit lands
under the owner's instruction to fix the issues already found and verified
first, on their report and these measurements, not by ear.

Against the recordings (`Tools/benchmark_recordings.py`, train and dev, the
fix of the entry above in both runs), the noise score between the partials
moves as follows, lower being closer: Kakegawa 5.68 → 5.86 (train) and 5.36 →
5.42 (dev), upright 6.48 → 7.40 and 7.21 → 7.20, Hamamatsu 8.68 → 8.33 and
9.23 → 9.01, Hamburg 6.93 → 7.12 and 6.17 → 6.74, New York 8.38 → 8.16 and
9.67 → 9.62. That score measures the recordings with the mean, so it counts
the phantom tones as noise and leans towards the old fit. Every other paired
score moves by 0.09 or less in its unit (the New York's dev attack_db 9.28 →
9.37 the most).

`Tools/compare_benchmarks.py` lists 27 regressions over its tolerances, 25 of
them in that noise score. On the Kakegawa: F♯1 4.42 → 5.34, C2 6.99 → 7.83 and
C3 6.05 → 6.68 (train), A2 6.54 → 7.19, A0 4.14 → 4.72 and C1 3.83 → 4.35
(dev). On the upright: A2 5.10 → 11.45, D3 5.97 → 12.26, C3 5.67 → 11.10, E3
12.94 → 17.81, A1 6.45 → 9.73, C1 7.65 → 9.55, F♯3 6.89 → 8.41, C2 13.34 →
14.77, A♯4 5.82 → 6.77, D♯1 9.23 → 10.08 and C4 4.78 → 5.36 (train), B3 7.50 →
9.40 (dev). On the Hamamatsu: G♯3 6.72 → 9.62 and F♯3 8.85 → 11.71 (train),
A♯3 6.11 → 8.51 (dev), and A7's early_db 11.94 → 12.78 (train). On the
Hamburg: D2 8.57 → 10.70 and A2 4.67 → 6.04 (train), E3 3.50 → 5.07 (dev). On
the New York, E7's partial_db 9.96 → 11.90 and its attack_db 13.13 → 13.78
(dev).

`Tools/evaluate_recordings.py`'s 24 Kakegawa cases, all at recorded pitches,
were scored for the shipping 0.4.14 build and for this one (the measured
attack): the twelve in-range held-out cases' broad bands 5.113 → 5.116 dB,
their harmonic levels 4.002 → 4.002 dB, envelope 1.706 → 1.706 dB, partial
decay 2.281 → 2.282 dB/s, pitch 0.190 → 0.190 cents and attack rise 4.080 →
4.080 ms; the two edge cases' broad bands 4.659 → 4.665 dB, every other figure
unchanged. No case moves by more than 0.033 dB or 0.062 ms. The in-between fix
leaves these recorded pitches unchanged, so the refit accounts for all of it.

## 2026-11-04 — the levels after the blend between pitches and the noise refit

The two entries above move `Keyra.Levels`. At the shipping output and tube
scales the five default sounds read 0.07 dB louder (Kakegawa), 0.24 (upright),
0.20 (Hamburg) and 0.36 (New York), and 0.14 dB quieter on the Hamamatsu.
Nearly all of it is the blend: with the blend alone every default sound and
every preset's typical playing reads within 0.04 dB of its reading with both.
The blend leaves every recorded pitch as it was, so its movement is in the
keys between them.

Each piano's `outputScale` and `tubeScale` are re-pinned so that its default
sound and its tube read, to the hundredth of a dB, what they read before both
changes: −9.06, −9.12, −8.99, −8.93 and −9.09 VU, and −9.07, −8.99, −9.98,
−9.17 and −9.02 VU through the tubes (.7680 → .7615 and 1.5619 → 1.5671,
2.3474 → 2.2837 and 2.2468 → 2.2864, 2.9873 → 3.0341 and 1.2426 → 1.2250,
2.3152 → 2.2622 and 1.4988 → 1.5176, .6823 → .6543 and 1.7668 → 1.8141). A
recorded pitch's partials therefore play 0.07 dB quieter on the Kakegawa
grand, 0.24 on the upright, 0.20 on the Hamburg and 0.36 on the New York, and
0.14 dB louder on the Hamamatsu; through the tube alone they move by −0.05,
−0.09, +0.01, −0.09 and −0.13 dB.

Seven presets then read off their approved levels: typical playing on Felt
Upright by +0.44 dB (−15.86 → −15.42 VU), Three Cities +0.10, Pop Upright
−0.09 and Warm Walnut −0.09, and the loudest chords rise over their approved
ceilings on Felt Nocturne by +0.05 dB, Open Strings +0.03, Warm Walnut +0.02
and the Kakegawa Grand +0.01. No sample passes the −1.5 dBFS ceiling. Felt
Upright's rise is not one key's: struck chromatically from A0 to C8 at
velocity 90 with its felt and without, the upright's keys keep the steps
between neighbours they had, over 3 dB at 12 and 5 places (11 and 6 before),
each within 1.1 dB of what it was. No Output trim brings Warm Walnut or the
Kakegawa Grand back to both of its approved readings: its loudest chords need
a larger cut than its typical playing allows. Asked whether to accept these
readings and merge, accept them and merge after listening, or drop both fixes,
the owner chose to accept them and merge, and
`Tests/Fixtures/dynamics/ApprovedLevels.h` now holds the eight readings to six
decimals. `Keyra.FactoryDynamics` still fails, as it did before both changes:
1,048 of its 2,120 pairs sit under their step floors (988 after the stereo
fix, 588 on main), and 6 chords pass its maximum levels (11 after the stereo
fix), all the Kakegawa grand's: its loudest reading above, and through its
tube the chords struck at 101 by up to +0.47 dB and its velocity ladder by
+0.07 dB. Its floors and limits are unchanged.

## 2026-11-04 — the levels after phantom partials

0.4.16 to 0.4.18 (faded partials and the felt's update, the floor following
Brightness, and phantom partials, which also render a key's strikes together)
move three presets' typical playing past `Keyra.Levels`' 0.05 dB guard: the
Kakegawa Grand from −9.016195 to −9.066835 VU, Open Strings from −8.133493 to
−8.081521 and the Hamburg Grand from −8.893996 to −8.953395. The phantom
partials' lines make −0.009, +0.010 and −0.023 dB of it: with every phantom
gain at zero, 0.4.18 reads −9.057675, −8.091657 and −8.930175 VU. Every
preset's loudest chords stay under their approved ceilings, and no sample
passes the −1.5 dBFS ceiling.

Asked whether to accept these readings and merge, to merge after listening to
the phantom partials' A/B set, or to merge 0.4.16 and 0.4.17 without them, the
owner chose to accept them and merge now. The choice came ahead of the
listening set, so no letter is recorded for the phantom partials.
`Tests/Fixtures/dynamics/ApprovedLevels.h` now holds the three typical
readings to six decimals. `Keyra.FactoryDynamics` still fails as on 0.4.17:
1,049 of its 2,120 pairs sit under their step floors (1,048 on 0.4.17), and
the same six chords pass its maximum levels. Its floors and limits are
unchanged.

## 2026-11-05 — the pitch glide, the action's click and the string beat ship unheard

Three A/B sets waited for the owner's ear, each A the shipping 0.4.18 and B a
candidate fitted from the train recordings and benchmarked on the five
pianos:

- the upright's pitch glide (`ab-2026-11-04-pitch-glide`, both upright
  presets): B is 0.4.19, a key's strings sharp in proportion to their
  partials' power, settling as they decay;
- the action's click (`ab-2026-11-05-action-click`, the Kakegawa, Hamburg and
  New York grands at Mechanics 77 % and the Kakegawa grand at its default): B
  is 0.4.20, a click above the body's modes as a key or the grand's pedal
  comes up;
- the undamped strings' beat (`ab-2026-11-05-string-beat`, the Kakegawa grand
  at Mechanics 0): B is 0.4.21, its F♯6, A♯6 and C♯7 ringing as two
  components that beat.

The owner chose B for all three without listening to the sets: "simply take
the candidate because it is better". No letter was chosen by ear, and no
listening preference is recorded. The choice licenses shipping the three as
their fits give them. It does not settle the beat's fixed timing, which Known
gaps keeps.

## 2026-11-05 — the Hamburg's keys between recorded pitches play the keyboard network

The owner asked for the keyboard network to be applied: tables at the keys
between recorded pitches, played in the engine, the fits kept at the
recorded pitches, the benchmark deciding for each piano. 0.4.22 plays the
first run's network (2026-11-04, the five Keyra pianos' train pitches alone)
at the Hamburg grand's keys between its recorded pitches, written by
`Tools/write_network_tables.py` with each partial's power moved to the fits'
at the recorded pitches around it; the other four pianos blend as before.
It was chosen on measurements. No listening test was run and no listening
preference is recorded.

The engine's score (`keyboard_network.py engine`, the rms level error at the
dev takes, dB) for the grand, the upright, the Kawai, the Hamburg and New
York: blending (0.4.21) 7.79, 9.56, 10.56, 11.04 and 11.65; the first run's
tables 7.73, 9.94, 11.13, 9.38 and 12.36; the second run's (2026-11-05, all
ten libraries) 7.80, 9.86, 12.44, 10.12 and 12.13. Every train figure stays
within 0.02 dB of blending. The first run's figures quoted earlier the same
day for the grand, the upright, the Kawai and New York (7.83, 10.01, 11.03
and 11.95) came from a writer that did not yet move the levels to the fits'
and are superseded.

The recording benchmark (`Tools/benchmark_recordings.py`, paired against
0.4.21) decided between the two pianos the first run brought closer. On the
Hamburg's eight dev takes, at E3 and C♯5, 0.4.22 stands closer on 7 of its
12 measures: envelope −1.68 dB, sustain −1.36 dB, decay −0.59 dB/s, rise
−0.33 ms, noise −0.19 dB, image −0.12 dB and early −0.07 dB; and further on
5: tuning +0.38 cents, level +0.31 dB (each run against its own median
gain), attack +0.13 dB, coherence +0.008 and partial levels +0.02 dB. Past a
tolerance: E3's partial levels 8.89 → 10.22 dB, its noise 5.01 → 5.94 dB,
its attack 6.68 → 7.32 dB and its coherence 0.19 → 0.21, and C♯5's tuning
0.90 → 1.57 cents. The train takes stay within 0.02 dB, but for the level:
the paired comparison holds 0.4.21's median gain, so the re-pin below shows
in it as 0.70 → 1.93 dB on the train takes and 1.84 → 1.38 on the dev takes,
where each run against its own median reads 0.70 → 0.69 and 1.84 → 2.15
([report](validation/hamburg-network-keys-benchmark-2026-11-05.md)). On the
grand's dev takes the first run's tables stand further on 6 measures and
closer on 5, and 8 measures at four notes pass a tolerance: D♯3's envelope
1.59 → 5.73 dB,
D♯7's tuning 3.86 → 6.12 cents, partial levels 2.78 → 4.21 dB and decay
2.81 → 4.11 dB/s, D♯1's partial levels 6.73 → 7.91 dB and sustain 4.38 →
5.44 dB, D♯5's rise 3.31 → 5.21 ms and D♯7's coherence. So the grand keeps
blending.

Written other ways, the Hamburg's first-run tables measured worse:

- at the network's own levels, 8.96 dB in the engine, but the per-key trims
  (initCalibrations) then moved the recorded pitches: the benchmark's level
  error went from 0.70 to 2.95 dB on the train takes and from 1.84 to 6.01
  on the dev takes;
- with the lanes faster than both fits kept at the fits' fastest decay
  instead of left out, 12.74 dB;
- with the decays moved towards the fits' as well, in three ways, 9.35 to
  10.61 dB, each failing `Keyra.Engine`'s Ring check on the Hamburg's C4,
  and the best of them on the benchmark the envelope 1.88 dB, sustain
  1.18 dB and partial levels 0.84 dB further from the dev takes;
- with the blend's lanes that decay faster than the network's in the places
  of the lanes left out, the network's scaled to keep each partial's power
  over 50 to 750 ms (the owner's question of a blend of both), 9.49 dB, and
  on the benchmark further than the shipped tables on 6 of the 12 measures
  (partial levels +0.26 dB against +0.02, sustain −0.93 dB against −1.36,
  decay −0.50 dB/s against −0.63, early, image) and closer on two (tuning
  +0.20 cents against +0.34, envelope −1.74 dB against −1.68). Its default
  sound read −10.33 VU where the shipped tables' read −10.83.

The second run's tables fail two of `Keyra.Engine`'s checks and
`Keyra.Glide`. The Hamburg's eight dev takes compared these 18 candidates,
and the Hamburg has no sealed takes, so its dev figures are no longer
untouched held-out evidence.

`Keyra.SoftLaneContinuity` checked that the legacy soft-pedal rank
multiplier fails at a crossing of lane rates in four grands. The Hamburg's
crossing, between D2 and A2 (the test strikes F2 at 123), lies at keys the
network now plays, where no lane rate crosses, so the legacy multiplier no longer fails there; that
case is removed with the reason beside it, and the test asks for the other
three.

The keys between strike weaker than the blend did, 2.3 dB over their first
100 ms at velocity 80, and the Hamburg's default sound read −10.83 VU and
its tube −10.49. Its `outputScale` and `tubeScale` are re-pinned, as on
2026-11-04, to what they read before: 2.2622 → 2.8070 and 1.5176 → 1.4219,
−8.95 and −9.18 VU. A recorded pitch's partials therefore play 1.87 dB
louder, and through the tube alone 1.31 dB louder. The Hamburg Grand
preset's typical playing reads −8.95 VU as approved, but its loudest chords
read 2.40 VU against an approved 1.69, and through the tube 2.20 against
1.41, with no sample past the −1.5 dBFS ceiling. Asked whether to accept
these readings and merge, to listen to a keyed A/B first, or to keep the
Hamburg blending, the owner chose to accept them and merge:
`Tests/Fixtures/dynamics/ApprovedLevels.h` now holds the two loudest
readings to six decimals, 2.404007 VU for the preset and 2.196889 VU for
the tube, and `Keyra.Levels` passes. `Keyra.FactoryDynamics`
fails as it did on 0.4.21, with 1,090 of its pairs under their step floors
(1,046 on 0.4.21: the Hamburg Grand's 102 new and 58 gone, no other
preset's moving) and 30 chords past its maximum levels (6 on 0.4.21): the
Hamburg Grand's chords struck at 110, 12 at each microphone, up to 2.40 VU
against 1.64 and 2.20 against 1.41. Its floors and limits are unchanged.
`Keyra.CpuBudget` passes, its demos playing no Hamburg; struck chromatically
at velocities 40 and 100 with the pedal down, the Hamburg renders in a
median 9.45 s of CPU where 0.4.21 took 14.34 s (seven alternating runs of
each, on the development machine).

## 2026-11-05 — a realistic piano with a recorded piano's character

The owner asked for a way to bring what the pianos recorded at many pitches
measure to the keys between a sparser piano's recorded pitches, rather than
relying on blending alone. Told that a correction learned at hidden recorded
pitches carries how pianos generally behave between two pitches, not one
piano's own quirks, the owner answered: "our goal is not to replicate an
exact piano, but create a realistic sounding piano with a character that is
similar to some exact piano - so we are fine".

This licenses playing the keys between a piano's recorded pitches with
behaviour learned from all five pianos' fits. It does not make such a key a
measurement of that piano: its recorded pitches keep their own fits, and
the recordings of the keys between, which nothing is fitted to, stay the
test of whether the keys between sound like the piano around them.

## 2026-11-05 — correct the blend at the grand's and the upright's keys between recorded pitches

The owner's answer above licenses playing the keys between a piano's
recorded pitches with behaviour learned from all five pianos' fits. 0.4.23
does so at the Kakegawa grand's and the upright's keys between two recorded
pitches above the bass break, where both pitches' strings are plain: they
blend the two pitches' fits as before and then take, for each partial, a
shift of its lanes' decay rates and a tilt of their levels between its fast
lanes and its slow, both vanishing at the recorded pitches, with each
channel's power over 50 to 750 ms held where the blend has it
(`Tools/keyboard_network.py correct`, the medium network at the knob 1000,
kept in `Docs/research/keyboard-network-correction-2026-11-05/`). Their
keys between in the wound bass, and the Kawai, the Hamburg and New York,
render as in 0.4.22, sample for sample. It was chosen on measurements. No
listening test was run and no listening preference is recorded.

A piano takes the correction where its dev takes, which no fit holds, come
closer on most of `Tools/benchmark_recordings.py`'s twelve measures, paired
against 0.4.22, with no pitch further on a measure by more than its
tolerance, and where its corrected keys come out no quieter or shorter
beside their recorded neighbours than blended. Of the grand's 156 dev takes
the correction reaches the 48 at D♯3, D♯5 and D♯7; at them 0.4.23 stands
closer on 7 measures, sustain −0.61 dB, envelope −0.45 dB, partial levels
−0.28 dB, decay −0.23 dB/s, rise −0.14 ms, image −0.022 dB and noise
−0.008 dB, and further on 5, tuning +0.061 cents, attack +0.027 dB, level
+0.010 dB, coherence +0.007 and early +0.002 dB. Of the upright's 21 it
reaches the 16 at G♯3, B3, C5 and E6; at them it stands closer on 9,
envelope −0.37 dB, sustain −0.22 dB, partial levels −0.19 dB, decay
−0.064 dB/s, rise −0.039 ms, early −0.037 dB, attack −0.007 dB, level
−0.003 dB and coherence −0.0009, and further on 3, tuning +0.060 cents,
noise +0.021 dB and image +0.006 dB. No pitch passes a tolerance on either
([grand](validation/grand-blend-correction-benchmark-2026-11-05.md),
[upright](validation/upright-blend-correction-benchmark-2026-11-05.md),
which pair all 156 and 21). Their train takes, at the recorded pitches, and
their other dev takes score as in 0.4.22 to four decimals.

The first candidate corrected every key between, as the correction was
trained (21224de on the branch). It stood closer on 8 measures of the
grand's 156 dev takes and further on 4, and on 7 of the upright's 21 and
further on 5, none past a tolerance; but below the break, on the wound
strings, it took the envelope and the sustain further from the recordings
at every pitch then scored there: the grand's D♯1 (envelope 4.38 → 4.54 dB,
sustain 4.38 → 4.67 dB), the upright's D♯2 (2.09 → 2.50 and 8.96 →
9.15 dB, and further on 9 of the 12 measures) and the grand's sealed D♯2
(1.86 → 2.38 and 5.58 → 5.67 dB, its envelope and its rise, 9.12 →
16.28 ms, past a tolerance). At all nine pitches then scored above the
break, dev and sealed, the envelope came closer. So the writer corrects
only between two plain-string pitches (`piano_corrections` in
`Tools/write_network_tables.py`). This restriction was chosen after the
grand's sealed takes had been opened for the first candidate, so the
sealed D♯2 is no longer untouched evidence for it, and the restriction is
a choice made on the dev and sealed takes together. The upright's sealed
takes, opened only after it was chosen, bear it out at F♯1: the first
candidate took its partial levels 9.73 → 10.94 dB, its decay 4.97 →
6.33 dB/s and its sustain 7.04 → 7.95 dB, all three past a tolerance,
though its envelope came closer (3.43 → 3.12 dB). So the sustain went
further at all four pitches scored below the break and came closer at nine
of the eleven above it, and the envelope went further at three of the four
and came closer at nine of the eleven.

With the correction at every key between, the Kawai's 23 dev takes stand
closer on 7 measures and further on 5, sustain +0.29 dB the most, and six
measures pass a tolerance at five pitches: F♯7's sustain 7.18 → 8.20 dB and
envelope 6.27 → 6.95 dB, A♯5's sustain 10.25 → 11.26 dB, D5's decay 6.16 →
7.40 dB/s, D♯2's envelope 2.66 → 3.43 dB and B5's 3.62 → 4.13 dB, all but
D♯2's above its bass break. New York's 17 stand closer on 6 and further on
6, decay +1.09 dB/s the most, and six pass a tolerance at C6 and E4, both
in ten-key gaps above its break: C6's decay 8.27 → 10.79 dB/s, partial
levels 10.71 → 11.29 dB and coherence 0.22 → 0.25, and E4's envelope 3.82
→ 4.70 dB, decay 5.17 → 6.41 dB/s and attack 7.86 → 8.37 dB. In place of
the Hamburg's network keys, its 8 stand closer on 4 and further on 8,
envelope +2.11 dB the most, and nine pass a tolerance at C♯5 and E3, C♯5's
envelope 3.12 → 6.35 dB and sustain 5.70 → 8.30 dB the most. So those three
play as before; each key's correction being its own, correcting the Kawai
and New York above the break alone would leave every one of those pitches
but the Kawai's D♯2 past its tolerance. These dev takes compared the
candidates below, so they are no longer untouched held-out evidence for the
correction.

Earlier forms of the correction measured worse:

- moving each partial's decay rates and each channel's power at each
  velocity layer, trained frame by frame: it played the keys between
  quieter than the blend over their first 0.75 s on every piano, by 0.25 to
  1.8 dB, where the recordings of those keys put four pianos' louder;
- the same trained on each channel's energy over 0.05 to 0.75, 0.75 to 1.5
  and 1.5 to 3.5 s, at the knob 1000: the grand's dev takes closer on 7
  measures and further on 5, with four measures past a tolerance at three
  pitches, D♯1's rise 8.65 → 16.79 ms the most, and the upright's closer on
  8 and further on 4, with seven past a tolerance at four pitches, G♯3's
  level 2.86 → 4.10 dB the most; its powers moved the train takes too, the
  grand's rise 0.06 ms and level 0.06 dB further;
- the shift and the tilt with each channel's power at each layer moved as
  well, at the knob 1000: 8.14 dB off the grand's dev takes' energies and
  8.24 off the upright's, where the blend stands 8.03 and 8.09 and the
  shipped form 7.89 and 8.03.

Struck key by key at velocity 72, each key between against the line
through its recorded neighbours' levels, the Kakegawa Grand preset's keys
between stood on average −0.02, −0.10, −0.72 and −1.11 dB under it over
0.05 to 0.30, 0.05 to 0.75, 0.75 to 1.5 and 1.5 to 3.5 s, and stand −0.04,
−0.11, −0.34 and −0.47 dB corrected; the Helsinki Upright's −0.15, −0.27,
−1.13 and −1.10, now −0.18, −0.27, −0.88 and −0.76; Pop Upright's −0.17,
−0.27, −1.23 and −1.12, now −0.20, −0.27, −0.98 and −0.78; Felt
Nocturne's −0.10, −0.10, −0.27 and −0.82, now −0.16, −0.16, −0.26 and
−0.82; and Felt Upright's −0.27, −0.27, −0.71 and −1.51, now −0.32,
−0.32, −0.68 and −1.51. So from 0.75 s the default sounds' keys between
ring on closer to their neighbours, and up to 0.75 s every preset's stand
within 0.06 dB of where the blend put them, the felt presets' that much
quieter. Over the first 50 ms, which the correction leaves free, they start
0.12 to 0.17 dB further under on average, the grand's from C6 up 0.57 dB.

The grand reads on Reason's meter (`Tools/KeyraLevels.cpp`) as in 0.4.22,
its default sound −9.066824 VU and its tube −9.072822, so its `outputScale`
and `tubeScale` stay. The upright's default sound reads −9.121526 VU against
−9.119352 before, and stays, but the reshaped decays took its tube to
−9.11 VU from −9.00, so as for the Hamburg in 0.4.22 its `tubeScale` is
re-pinned to what it read before, 2.2864 → 2.3142, which reads −9.001472 VU
against −9.002294 before and the approved −8.993037. Through the tube alone
the upright then plays 0.105 dB louder than in 0.4.22; nothing else moves.

Three presets then read past `Keyra.Levels`' guard of their approved
levels: the Kakegawa Grand's loudest chords 0.707407 VU against 0.702634
and Open Strings' 1.501300 against 1.489288, each more than 0.001 over
(0.4.22 read 0.697666 and 1.483250), and Felt Upright's typical playing
−15.665733 VU against −15.424076, more than 0.05 off (0.4.22: −15.420022).
Pop Upright's typical playing reads −9.214799 VU against −9.165020, 0.0498
off and inside the guard by 0.0002 VU (0.4.22: −9.164666); it goes to the
owner with the other three, so that a reading this close to its guard does
not rest on the last digits of a platform's arithmetic. Typical playing is
the median of ninety events' loudest 300 ms. Read event by event against
0.4.22's, the grand's presets' events moved by a median 0.000 dB and the
upright's by −0.019 to −0.032 dB, and at the upright's two the median now
falls on other events: Felt Upright's on F6 struck at velocity 110, now
0.49 dB lower over its loudest 300 ms, and A4 at 70, 0.09 dB lower; Pop
Upright's on C♯6 at 110, 0.25 dB lower. Every other preset, both pianos
and their tubes pass. These four readings went to the owner with the
version, and the owner approved them:
`Tests/Fixtures/dynamics/ApprovedLevels.h` now holds them to six decimals,
and `Keyra.Levels` passes.

`Keyra.FactoryDynamics` fails as it did on 0.4.22, with 1,098 of its pairs
under their step floors (1,090 on 0.4.22: the Kakegawa Grand's 10 new and 5
gone, the Helsinki Upright's 5 new and 2 gone, no other preset's moving) and
the same 30 chords past its maximum levels. Its floors and limits are
unchanged. The `unit` tier (37 tests, `Keyra.KeyboardNetwork` and
`Keyra.MeasuredNetworkKeys` among them), `Keyra.AudioDemos` and
`Keyra.CpuBudget` pass, and `KeyraDSPCxx17` builds. Struck chromatically
at velocities 40 and 100 with the pedal down, as 0.4.22 was measured, the
grand renders in a median 6.64 s of CPU where 0.4.22 took 6.59 s, and the
upright in 4.96 s where it took 5.11 s (seven alternating runs of each, 48 s
of audio, on the development machine), differences within the runs' spread.
`Tools/evaluate_recordings.py`'s 24 cases, the twelve in-range held-out and
both edge cases among them, are all recorded pitches, and every one scores
exactly as in 0.4.22.

The grand's sealed takes, D♯2, D♯4 and D♯6 at all sixteen layers, were
opened twice beside 0.4.22 (`Tools/corpus/sealed-openings.json`; fetched for
the runs, as the workspace held none): for the first candidate and for this
version. This version plays D♯2 as 0.4.22 does. On D♯4's and D♯6's 32
takes it stands closer on 9 of the 12 measures, partial levels −0.98 dB,
sustain −0.97 dB, decay −0.91 dB/s and envelope −0.87 dB the most, and
further on 3, rise +0.06 ms, attack +0.03 dB and image +0.02 dB, none past
a tolerance ([report](validation/grand-blend-correction-sealed-2026-11-05.md),
which pairs all 48). The upright's sealed takes, F♯1, E4 and G♯5 at all
five layers, were opened once each for 0.4.22, the first candidate and this
version (`Tools/corpus/sealed-openings-helsinki.json`; decoded for the runs
from the owner's copy of the library, each file checked against its pin).
This version plays F♯1 as 0.4.22 does. On E4's and G♯5's 10 takes, which
both candidates correct alike, it stands closer on 5 of the 12 measures,
decay −0.65 dB/s (G♯5's 5.98 → 4.63) and partial levels −0.13 dB the most,
and further on 7, envelope +0.18 dB (E4's 3.57 → 3.89) and tuning
+0.08 cents the most and the others 0.03 or less, none past a tolerance
([report](validation/upright-blend-correction-sealed-2026-11-05.md), which
pairs all 15). There the correction's gain is in the decay, not in the
envelope the upright's dev takes showed.

Asked to choose between this version and the first candidate, or to keep
both unmerged, the owner chose this version, with its four preset readings
approved, and to merge it. The choice was made on these measurements; no
listening test was run.

## 2026-11-05 — the struck key's own undamped string rings

0.4.24 sets the struck key's own undamped string ringing where the
recordings hold it and the key's partials leave its pitch apart, as
`Tools/fit_halo_own.py` measures it on each piano's train takes
(`Source/DSP/MeasuredHaloOwn.h`,
[research](research/halo-own-2026-11-05.md)). It was chosen on
measurements, under the owner's standing direction for these rounds,
"simply take the candidate because it is better": no listening test was
run and no listening preference is recorded. That direction licenses
shipping the own string as its fit gives it. It does not settle what Known
gaps keeps: one slope for every string, F♯7's string at the pitch the other
keys' strikes give rather than the octave-below string's second partial,
and the keys between recorded pitches that hold or lack a level.

The fit's choices, made on the train takes before any dev take was scored:

- A pitch's own string is read only where no lane of its fitted series lies
  within 4 Hz of the string's pitch, the main lobe of the halo fit's
  half-second Hann window, inside which that window resolves no second
  component. The engine asks the same of the series it builds for each key
  (`ownStringApart()`, `haloOwnResolvedHz`).
- A window hears the string clear where it stands 10 dB over the median 4
  to 20 Hz either side, leaving out the bins within 4 Hz of the key's own
  components, and 10 dB over what the key's lanes within 40 Hz read there
  through the same window. The second test came from the Hamamatsu's C7,
  whose string lies 4.2 Hz from its fundamental: the reading there was the
  fundamental's first sidelobe, as loud in the render, which plays no own
  string, as in the recording, and without the test C7 would have been
  given one.
- The level grows at the halo fit's one slope, fitted over the layers with
  the hidden ones as bounds. With fewer than two layers clear it sits 10 dB
  under their median bound, never over the tightest, and a layer that rings
  clear caps it.

Two readings were corrected before the candidate was frozen. The grand's C8,
which the series fit leaves uncalibrated, first held A7's level and played
11 to 20 dB over its takes; with no fitted series to tell its own components
from the string, its layers now only bound it, and it plays 5 to 14 dB under
them. The Hamburg's F7 rings clear only at its softest layer, and its loud
layers' bounds alone put it 18 dB over that layer; the clear layer now caps
it (−99.0 dB at the loudest layer against −80.7).

Read as the halo fit reads a string, from 1 to 2 s, brought back to contact
and against the take's level from 50 to 750 ms, the grand's F♯7 and A7 train
takes, which 0.4.23 left 30 to 43 and 59 to 64 dB under the recordings, stand
−1.4 to +4.4 and −1.0 to +9.9 dB from them, and their dev takes −0.6 to +4.3
and −0.1 to +2.1 dB. Of the keys no fit holds, the grand's D♯7 comes from 27
to 33 dB under to 3 to 9, the Hamamatsu's F♯7 from 42 to 43 to 17 to 24 and
the New York's A7 from 38 to 20, and the New York's E7 stays about 33 dB under, as
its keys from E7 up hold G♯7's bound.

Paired against 0.4.23 by `Tools/benchmark_recordings.py`, the grand's 156
dev takes stand closer on all 12 measures, tuning −0.083 cents, decay
−0.056 dB/s, sustain −0.041 dB, image −0.035 dB, envelope −0.024 dB and
partial levels −0.023 dB the most, and its 276 train takes closer on 7 and
further on 5, tuning +0.015 cents, decay +0.004 dB/s, level +0.004 dB,
partial levels +0.002 dB and image +0.001 dB. The Hamamatsu's 23 dev takes
stand closer on 7 and further on 4, by 0.01 or less; the Hamburg's 8, at E3
and C♯5, score as before; the New York's 17 stand closer on 8 and further on
3, decay +0.025 dB/s the most. Their train takes move by 0.021 or less. The
upright renders as before, sample for sample
([grand](validation/grand-halo-own-benchmark-2026-11-05.md),
[Hamamatsu](validation/kawai-halo-own-benchmark-2026-11-05.md),
[Hamburg](validation/hamburg-halo-own-benchmark-2026-11-05.md),
[New York](validation/newyork-halo-own-benchmark-2026-11-05.md)).

One pitch passes a tolerance: the tuning of the grand's C8 train takes, 1.01
→ 1.51 cents against the 0.5-cent tolerance (its dev takes 1.55 → 1.90,
inside it). The benchmark takes a render's first partial as the clear peak
nearest the recording's, at C8 4276.6 Hz, and in 14 of the 16 takes' renders
it now finds the own string 6 Hz over it, where 0.4.23's found one of the
render's own peaks between 4269 and 4285 Hz. Through that window, in the
five takes probed, the recordings' first partial peaks 8 to 13 dB over what
stands at the string's pitch, and the renders' own peaks stand 7 to 21 dB
under the string's. So the regression shows that C8, which is not
calibrated and plays A7's data on the stretch curve, peaks under a string
that the recordings hold, and hold louder from 1 to 2 s, where their first
partial peaks over it. The note's partials are as in 0.4.23, and the string
stays.

`Tools/evaluate_recordings.py`'s 24 cases, the twelve in-range held-out and
both edge cases among them, all lie at C7 and below, and every one scores
exactly as in 0.4.23 in its three variants. The `unit` tier (39 tests,
`Keyra.HaloOwn` and `Keyra.MeasuredHaloOwn` among them), `Keyra.Levels`,
`Keyra.AudioDemos` and `Keyra.CpuBudget` pass, and `KeyraDSPCxx17` builds.
On Reason's meter (`Tools/KeyraLevels.cpp --report`) the Hamamatsu's default
sound, tube and preset read −8.97, −9.95 and −8.97 VU against −8.99, −9.97 and
−8.99, its own strings from F6 to B7 adding to its typical playing, inside
their guards, so its scales stay; every other piano and preset reads as in
0.4.23 to the hundredth of a VU. `Keyra.FactoryDynamics` fails as it did on
0.4.23, on the same 1,128 rows under the same floors and limits; 24 of their
values, at the Hamamatsu's and the Hamburg's, move by 0.0021 dB or less.
Struck chromatically at velocities 40 and 100 with the pedal down, as 0.4.22
and 0.4.23 were measured, the grand renders in a median 6.26 s of CPU where
0.4.23 took 6.25 s, the Hamamatsu in 5.01 s against 4.93, the Hamburg in
8.59 s against 8.90 and New York in 5.04 s against 4.95 (seven alternating
runs of each, 48 s of audio, on the development machine), differences within
the runs' spread: the own string rings in the string's one resonator, and a
strike only checks the key's lanes against its pitch.

Also examined this round, none shipping:

- The undamped strings after a key is let go. In the upright's key-release
  takes where they ring clear, they ring 30 to 50 dB over the engine's after
  the key comes up, but a coupling from the released string fitted to those
  takes alone is +3 dB, and with the takes where the strings are hidden
  counted as bounds −24 dB, with a spread of 18 dB. The takes do not decide
  one coupling, and most of what rings near a covered string after a release
  is the key's own leftover, which the owner chose to keep quiet (2026-10-29,
  option C).
- The treble's low bands. Under the top notes the bands below their
  fundamentals stand further from the recordings from 0.3 to 1 s, where the
  recordings' body and room ring decays more slowly. It is not a string, and
  no candidate was formed.
- The treble's stereo coherence. Over 50 ms to 1.5 s the recordings' F♯7 and
  A7 keep 0.47 to 0.81 of their coherence between channels and the renders
  0.91 to 0.99, which the own string leaves unchanged; the rest lies in the
  unison strings tuned further off than the lanes reach.

## 2026-11-06 — the Hamamatsu's, the Hamburg's and New York's keys between recorded pitches play the retrained network

The owner asked for the keyboard network to be trained again with a cap on
how fast a lane may decay and a loss over the attack, its settings picked by
the engine's score, and for the candidate to be taken because it measures
better ("simply take the candidate because it is better"). 0.4.26 does so.
No listening test was run and no listening preference is recorded.

The third run (`Tools/keyboard_network.py grid --run capped --alone --arch
large medium small --knob 10 1000`, the five Keyra pianos alone) keeps every
lane at or under the fits' fastest decay at its key (`lane_caps`), the bound
the table writer puts on a key's lanes, and weighs each partial's energy in
each channel over its first 100 ms against the measured (`attack_weight`).
Each of its six settings' tables, written for every piano, was scored by
`Tools/benchmark_recordings.py` on every train and dev take, paired against
0.4.25, and each measure's mean change on the dev takes, in units of
`Tools/compare_benchmarks.py`'s tolerance, summed over the 12 measures
([grid](research/keyboard-network.md#the-third-run)). A piano plays the third
run's tables where they bring its dev takes closer on most of the measures
with the sum below zero, at the setting with the lowest such sum whose tables
pass the engine's tests: the Hamamatsu the medium network at knob 1000
(−3.23, 9 measures closer), the Hamburg the medium at knob 10 (−0.55, 8
closer) and New York the medium at knob 1000 (−0.57, 7 closer). The Hamburg's
lowest, the large network at knob 10 (−2.68), leaves its sustain pedal no
bloom on a held C4 (−0.02 dB, where `Keyra.Engine` asks 0.6 to 5). The
grand's and the upright's dev takes stand further at every setting (their
lowest +1.92 and +0.78), so they keep their corrections to the blend. Six
settings were tried on the same dev takes and the best kept, so their
figures flatter the choice; the sealed takes were not opened this round, and
the Hamburg has none.

The network's keys strike weaker than the blend: each key between struck
alone and held for 2 s stands a median 2.7, 2.6 and 2.4 dB under the blend
over its first 100 ms at velocity 80 on the Hamamatsu, the Hamburg and New
York, and 0.4, 0.4 and 1.4 dB over it from 100 ms on (velocity 32: 2.2, 2.4
and 2.2 under, 1.4, 0.5 and 1.1 over). Their readings on Reason's meter moved:
the Hamamatsu's default sound to −10.21 VU from −8.97 and its tube to −11.27
from −9.95, New York's to −10.94 and −9.86 from −9.09 and −9.03, and the
Hamburg's, against the first run's tables, to about −8.4 and −8.9 from −8.95
and −9.18. Each is re-pinned to the reading it had (`KeyraEngine.cpp`): the
Hamamatsu's `outputScale` 3.0341 → 3.5030 and `tubeScale` 1.2250 → 1.2364,
the Hamburg's 2.8070 → 2.6414 and 1.4219 → 1.4655, New York's .6543 → .8093
and 1.8141 → 1.6122. The recorded pitches move with them, and a recorded
pitch stands apart from the mean of its two neighbours by 4.0, 2.4 and 2.6 dB
rms over the first 100 ms (blended, 1.9, 0.9 and 0.9) and by 7.7, 4.5 and
4.5 dB rms from 0.8 to 1.6 s (blended, 4.2, 1.3 and 2.3), over velocities 80
and 32; the most, the Hamamatsu's F♯2 at velocity 32, 9.3 dB over its
neighbours and then 21.2 dB under them (blended, 1.8 and 6.1).

Paired against 0.4.25, the 12 measures' changes on the dev takes, which no fit
holds (the benchmark's level holds 0.4.25's median gain, so it carries the
re-pin):

- The Hamamatsu's 23: closer on 10, tuning −0.61 cents, rise −0.48 ms, decay
  −0.42 dB/s, level −0.41 dB, envelope −0.27 dB, partial levels −0.23 dB,
  sustain −0.19 dB, attack −0.08 dB, noise −0.01 dB and coherence −0.005, and
  further on 2, stereo balance +0.33 dB and early +0.003 dB. Its 104 train
  takes move by 0.05 or less but for the level, +0.33 dB.
- The Hamburg's 8, at E3 and C♯5: closer on 8, noise −1.35 dB, partial levels
  −0.76 dB, decay −0.72 dB/s, rise −0.68 ms, envelope −0.25 dB, early
  −0.17 dB, stereo balance −0.04 dB and coherence −0.006, and further on 4,
  tuning +1.62 cents, level +1.41 dB, attack +0.32 dB and sustain +0.21 dB.
  Its train takes move by 0.09 or less.
- New York's 17: closer on 6, tuning −0.81 cents, sustain −0.32 dB, rise
  −0.30 ms, partial levels −0.28 dB, noise −0.26 dB and decay −0.19 dB/s, and
  further on 6, level +1.63 dB, envelope +0.28 dB, early +0.28 dB, attack
  +0.23 dB, stereo balance +0.13 dB and coherence +0.031. Its train takes move
  by 0.10 or less but for the level, +1.19 dB. New York carries the treble's
  unison strings too (next entry).

Taken at each version's own gain, as the benchmark's first tables are, the
level error stands the Hamamatsu's dev and train takes 4.36 → 4.21 and 1.89 →
1.94 dB, the Hamburg's 2.15 → 3.13 and 0.69 → 0.61 and New York's 5.61 → 5.45
and 0.88 → 0.90. Past a tolerance, besides the level at 16 of the Hamamatsu's
notes and roles, 2 of the Hamburg's and 16 of New York's: the Hamamatsu's dev
B5 (envelope 3.62 → 7.38 dB, sustain 12.70 → 14.34 dB), A♯5 (stereo balance
4.41 → 7.21 dB, early 8.67 → 10.64 dB, decay 3.55 → 5.23 dB/s, partial
levels 5.72 → 6.94 dB, sustain 10.25 → 11.29 dB, noise 7.07 → 8.09 dB,
envelope 6.28 → 7.25 dB), F♯7 (envelope 6.27 → 8.01 dB, tuning 3.14 → 4.82
cents, sustain 7.18 → 8.40 dB, partial levels 11.19 → 11.87 dB), D♯2
(envelope 2.66 → 4.41 dB, sustain 9.67 → 10.57 dB) and D♯1 (rise 6.33 →
9.44 ms, sustain 8.97 → 9.50 dB), and its train C6 (early 6.41 → 7.37 dB,
noise 5.43 → 6.01 dB); the Hamburg's dev E3 (tuning 0.48 → 3.69 cents,
sustain 6.64 → 7.47 dB, attack 7.32 → 8.03 dB); New York's dev E7
(coherence 0.06 → 0.17, decay 8.18 → 10.46 dB/s), C6 (coherence 0.22 →
0.27), D♯2 (early 8.04 → 9.11 dB, envelope 3.41 → 4.20 dB), E4 (envelope
3.82 → 4.72 dB, attack 7.86 → 8.65 dB, coherence 0.19 → 0.22) and A7
(partial levels 12.04 → 12.64 dB)
([Hamamatsu](validation/kawai-network-unisons-benchmark-2026-11-06.md),
[Hamburg](validation/hamburg-network-unisons-benchmark-2026-11-06.md),
[New York](validation/newyork-network-unisons-benchmark-2026-11-06.md)).

On Reason's meter (`Tools/KeyraLevels.cpp --report`, read to six decimals)
every piano's default sound and tube read as in 0.4.25 to the hundredth of a
VU, and two readings pass their guards: the Hamamatsu's loudest chords
through the tube, 3.292226 VU against an approved 3.199726 (0.4.25: 2.59),
and Three Cities' typical playing, −10.426881 VU against −10.192568 (0.4.25:
−10.24). Asked whether to accept them and merge, to score the sealed takes
first, or to keep 0.4.26 on its branch, the owner chose to accept them and
merge: `Tests/Fixtures/dynamics/ApprovedLevels.h` now holds both to six
decimals, and `Keyra.Levels` passes. Felt Upright's typical playing, which the
upright's unison strings move (next entry), reads −15.617991 VU, 0.048 over
its approved level and inside the 0.05 guard. `Keyra.FactoryDynamics` fails as it did
on 0.4.25, on 993 rows, 968 pairs under their step floors and 25 chords past
its maximum levels, where 0.4.25 failed on 1,128 (1,098 and 30); its floors
and limits are unchanged.

The `unit` tier (40 tests), `Keyra.AudioDemos` and `Keyra.CpuBudget` pass,
`KeyraDSPCxx17` builds, and `Tests/test_keyboard_network.py` checks three
things more: that no lane decays past its cap, that the caps are the fits'
fastest lanes, and that the strike term is the log energy ratio. The 88
keys struck in turn at velocity 90, 120 ms apart with the pedal down, render
14 s of audio in a median 3.10 s of CPU on
the Hamburg where 0.4.25 took 5.63, 2.76 on the Hamamatsu against 2.72 and
3.05 on New York against 2.79 (seven alternating runs of each on the
development machine). The Hamburg plays as many partials as before (2,889),
and what makes it lighter was not traced.

## 2026-11-06 — the treble's unison strings ring on three pianos, and four own strings grow at their own slopes

The owner asked, beside the retrained network, for the treble's unison
strings with their own stereo spread, and then for the own undamped string's
pitch and its per-pitch slope to be finished, each decided on the recordings,
and for the better candidate to be taken. 0.4.26 plays the unison strings on
the Kakegawa grand, the upright and New York, grows four own strings at
their own slopes, and keeps the own string beside the unison strings. No
listening test was run and no listening preference is recorded.

From C6 up, `Tools/fit_treble_unisons.py` reads each recorded pitch's train
takes for the components within the unison reach of its first two partials
and keeps those nothing in 0.4.25 played: the key's own unison strings tuned
past its lanes and, from F7 up, the second partial of the undamped string an
octave down (the grand's 11, the upright's 10, the Hamamatsu's 1, the
Hamburg's 1 and New York's 4). It measures each through its own window, as
the analysis measures a component beside the series, with two lanes, a quick
early fall and a slow ring, and writes `Source/DSP/MeasuredTrebleUnisons.h`
([research](research/treble-unisons-2026-11-06.md)). The engine starts each
string in phase with its partial's lanes as they sum at contact and takes the
strings' power from those lanes, so that the lanes and the strings together,
every pair's beating counted, hold the power the fit gave the lanes alone
over 50 to 750 ms; where the lanes would keep less than a quarter of it the
strings give way.

Seven candidates were scored from C6 up on all five pianos, each measure's
mean change against 0.4.25 in tolerance units, summed over the eleven
measures other than level: the train and dev sums went from +2.87 and +2.05
(U2, power taken from the lanes in order of their rate) through U3 to U6 to
−0.57 and −0.98 for U7, the strings starting in phase with the partial, which
ships. Piano by piano U7 brought the grand's, the upright's and New York's
takes closer (train −1.01, −0.37 and −1.15, dev −1.04, −2.25 and −0.06) and
stood the Hamamatsu's and the Hamburg's train takes, on which their one
string each was measured, further (+0.43 and +1.74), none of their dev takes
changing. So those two are measured and not played (`PLAYED`). Over the three
that play, the dev takes from C6 up stand closer in stereo balance
(0.57 dB), tuning (0.31 cents), rise (0.17 ms), coherence (0.021) and decay
(0.06 dB/s), and further in sustain (0.41 dB), partial levels (0.29 dB),
envelope (0.27 dB), early (0.04 dB) and attack (0.02 dB). Struck at velocity
90, the grand's F♯7 keeps 0.76 of its coherence between channels where
0.4.25 kept 0.89 (its train takes 0.37 to 0.51), and its A7 0.67 where 0.4.25
kept 0.91 (0.68 to 0.77); `Keyra.Engine` checks that both stay under 0.85.

Past a tolerance, on the grand ten scores at four notes: C8's sustain (dev
16.28 → 17.61 dB, train 17.07 → 18.28), partial levels (dev 10.19 → 11.39,
train 9.69 → 10.80) and envelope (dev 2.54 → 3.63), D♯7's dev sustain (4.14 →
5.30) and envelope (3.26 → 3.79), A6's partial levels (dev 2.45 → 3.61, train
2.51 → 3.64) and F♯7's dev sustain (5.00 → 5.58); on the upright G7's train
sustain (11.71 → 12.63 dB) and coherence (0.31 → 0.34). C8 is not calibrated
and plays A7's data, its strings with it; D♯7 has no recording in the fit
and takes F♯7's ([grand](validation/grand-network-unisons-benchmark-2026-11-06.md),
[upright](validation/upright-network-unisons-benchmark-2026-11-06.md)). On
the grand's held-out evaluation (`Tools/evaluate_recordings.py`) the twelve
in-range cases move only at C6, whose string it plays: at velocity 8 the
harmonic levels 2.78 → 2.58 dB, the broad bands 7.18 → 7.13 dB, the partial
decay 14.72 → 14.62 dB/s and the rise 1.17 → 1.27 ms. Over the twelve the
means stand at 5.117 dB in bands (5.121), 3.988 dB in harmonics (4.005),
2.272 dB/s in decay (2.280) and 4.089 ms in rise (4.080), and the edge cases
C1 and C7 at velocity 8 score as before.

The own string's pitch. The grand's F♯7 now plays F♯6's second partial at
the pitch its own takes measure, as one of its strings, 2.4 Hz under its own
undamped string, which plays at the pitch the other keys' strikes measure
and at the level F♯7's strikes set where the halo fit's window hears the two
as one. Letting the own string give way wherever a string beside the series
lies within 4 Hz of it, as it gives way to a lane, silenced it at D♯7 and
F♯7 and stood the grand's treble further from its recordings: its 44 dev
takes from C6 up by +2.02 summed as above and its 84 train takes by +0.32,
D♯7's dev sustain 1.03 dB further. So both play.

The own string's slope. Where three or more of a pitch's train layers ring
its own string clear (`SLOPED`), `Tools/fit_halo_own.py` fits the pitch's
own slope with its level, between 0 and 3 dB per dB (`SLOPES`): the grand's
F♯7 1.09 and A7 1.85, the Hamburg's A♯6 2.16 and New York's F6 1.47, where
the halo fit's are 1.48, 1.48, 1.28 and 1.94. The layers' residuals fall from
2.31 to 0.71, 2.67 to 1.60, 4.53 to 2.44 and 3.77 to 1.59 dB on the train
takes, and the grand's dev layers from 2.02 to 0.92 and 1.49 to 1.37. On the
benchmark from C6 up, against the unison candidate without it (U6), the train
takes stay where they were and the dev takes stand 0.13 further, almost all
at the grand's D♯7, whose 16 dev takes hold F♯7's string and slope (+0.47:
decay 0.10 dB/s, envelope 0.09 dB and sustain 0.05 dB further); the four
measured pitches move by 0.10 or less. The slopes ship for the pitches they
were measured at, whose held-out layers they bring closer
([own slope](research/halo-own-2026-11-05.md#each-pitchs-own-slope-0426)).

The 88 keys struck in turn at velocity 90, 120 ms apart with the pedal down,
render in a median 3.57 s of CPU on the grand where 0.4.25 took 3.51
(+1.7 %), 2.50 on the upright against 2.53 (−0.8 %) and 3.05 on New York
against 2.79 (+9.5 %, with its retrained network), seven alternating runs of
each on the development machine.

## 2026-11-09 — each piano plays the room it was recorded in

The owner asked for five rounds of audible improvements from the physics and
the acoustics, each decided on the recordings with the better candidate
taken and no listening test, then for the whole keyboard to be calibrated.
This is the first round. No listening test was run and no listening
preference is recorded.

The finding. From 0.1 s after a strike the recordings' floor between the
partials falls at one rate per third octave whatever the note, and above
250 Hz the two microphones hear it uncorrelated: the recording room. 0.4.26
had only the board's modes and the noise bands there, which fall with the
strike, and by 0.45 s its floor at 1 to 4 kHz stood 5.4 dB under the
Kakegawa grand's train takes, 3.3 dB under the upright's, 13.7 dB under the
Hamamatsu's, 20.6 dB under the Hamburg's and 20.4 dB under New York's
([room](research/room-2026-11-09.md)).

What the room hears. The fitted partials are measured from the same
recordings and hold the room at their own frequencies, so a room fed the
whole output counts it twice. Scored against 0.4.26 before this round's fix
to the benchmark's bands, summed over the eleven measures other than level
in tolerance units, train and dev: a statistical room fed the whole output
stood the grand further (+3.75, +3.19) and the Hamburg (+5.12, +4.03); fed
only the strike's noise and the board's ring, with each band's level fitted
to what that band lacked, it brought all five pianos closer (the grand −2.28,
−1.75; the upright −2.71, −2.71; the Hamamatsu −0.66, −0.49; the Hamburg
−8.13, −0.25; New York −2.14, −3.65); a first build of the network fed the
same, with one gain per piano, brought all five closer by less (−0.91, −0.88;
−0.14, −0.01; −0.23, −0.82; −6.70, −0.60; −1.08, −3.32). The network ships
with one gain. A level per band would close more of each floor on the
benchmark, but outside the bands where the floor decays as a room it would
stand in for whatever else the engine leaves out there, such as the strike's
low thud, and it would no longer be a room's level.

The measurement. `Tools/fit_room.py` reads each piano's train takes only and
writes `Source/DSP/MeasuredRoom.h` and its receipt, which `Keyra.MeasuredRoom`
checks against the current modal data, split and corpus. Per band the rate is
the median over five or more takes of a line through the floor's frames 15 dB
over the take's own floor; the network's shelf is fitted to the measured
bands; the gain is the square root of the median, over those bands, of the
power that brings the engine's floor to the recordings'. The rooms' T60s run
from 0.85 to 1.07 s on the grand, 0.72 to 1.83 s on the upright, 1.20 to
1.61 s on the Hamamatsu, 2.29 to 3.66 s on the Hamburg and 1.56 to 2.17 s on
New York, the shelf within 1.8 to 5.1 dB/s rms of the measured rates and
8.7 dB/s on the upright. Three runs of the fit, on renderers built with and
without these numbers in the header, wrote the same header.

On the benchmark, against 0.4.26 on every train and dev take, the paired sums
in the same units are: the grand −1.05 and −0.88, the upright −0.29 and
−0.19, the Hamamatsu −0.31 and −0.90, the Hamburg −6.73 and −0.29 and New
York −1.65 and −3.10. Past a tolerance: the grand's dev D♯7 early (3.87 →
4.49 dB) and train C2 rise (7.26 → 8.49 ms); the Hamamatsu's dev G7 early
(18.58 → 19.89 dB, one take) and its train D♯7 tuning (0.26 → 1.43 cents),
D♯6 early (5.32 → 6.29 dB) and noise (4.86 → 5.44 dB), C6 early (6.16 →
7.08 dB) and noise (6.01 → 6.90 dB), A♯4 decay (3.10 → 4.51 dB/s) and A6
early (6.19 → 6.71 dB); the Hamburg's dev E3 coherence (0.21 → 0.25) and
noise (2.88 → 3.52 dB), its train F♯4 (0.10 → 0.14) and B3 coherence (0.09
→ 0.12) and its dev C♯5 coherence (0.18 → 0.21); New York's train F6 early
(4.32 → 5.13 dB) and dev E7 tuning (2.15 → 2.92 cents); none on the
upright. Four scores 0.4.26 could not measure are measured: the upright's
train E7 sustain (14.31 dB), the Hamamatsu's train G♯5 sustain (27.14 dB),
New York's train G♯7 sustain (12.76 dB) and the Hamburg's dev E3 noise on a
second take (7.63 dB). The Hamamatsu's treble early and noise scores are
probably its floor between 250 Hz and 1 kHz, which the room now takes over
its recordings' (5.6 dB by 0.45 s), and the Hamburg's coherence scores the
room's channels, uncorrelated under 250 Hz where its recordings' are not
(Known gaps). On the grand's held-out evaluation the twelve in-range cases'
bands stand 4.988 dB from their recordings (5.117), closer at ten, further
at C2 (3.35 → 3.37) and F♯5 (4.89 → 5.05) at velocity 8; the harmonic levels
3.990 dB (3.989), the envelope 1.707 dB (1.705), the partial decay
2.270 dB/s (2.272), the pitch 0.190 cents (0.190) and the rise 4.095 ms
(4.089), F♯4's at velocity 8 the most (3.21 → 3.37 ms). The edge cases C1 and
C7 at velocity 8 stand 4.657 dB in bands (4.660), 2.263 dB in harmonics
(2.286) and 8.032 dB in envelope (8.045).

The benchmark itself changed first (`fix(bench)`): it scores only the
third-octave bands both spectra have bins in. Its 40 ms window has none in
the 25 Hz band at 44.1 kHz and none in the 20 and 31.5 Hz bands at 48 kHz,
which read −300 dB whatever plays, so the Hamamatsu's and New York's
44.1 kHz recordings against 48 kHz renders took the 30 dB cap there in every
take. Rescored, 0.4.26's attack, early and sustain errors fall 0.82 to
1.61 dB on the Hamamatsu and 0.26 to 1.25 dB on New York, train and dev, and
the other three pianos' do not move. The five baselines above are 0.4.26
rescored; `Keyra.BenchmarkBands` checks which bands count.

Levels and tests. The room raises five loudest-chord readings over their
approved levels: the Hamamatsu's through the tube 3.297875 VU against
3.292226, Kakegawa Grand 0.709162 against 0.707407, Warm Walnut −0.120532
against −0.123667, Felt Nocturne −5.595710 against −5.597279 and Open
Strings 1.505028 against 1.501300, so `Keyra.Levels` failed on them; the
owner accepted them with 0.4.28's readings (next entry). Typical playing
moves −0.006 to +0.025 VU, inside the test's 0.05 guard, so no output or
tube scale is re-pinned.
`Keyra.FactoryDynamics` fails as it did on 0.4.26, on 992 rows (966 pairs
under their step floors and 26 chords past its maximum levels) where 0.4.26
failed on 993 (968 and 25); the one new row is the original Hamburg Grand's
microphone 1, round 3, shape 7 at velocity 110, +1.428 against +1.408. Its
floors and limits are unchanged. The `unit` tier (43 tests, `Keyra.Room`,
`Keyra.MeasuredRoom` and `Keyra.BenchmarkBands` among them), the `audio`
tier's demos and the `perf` tier pass, and `KeyraDSPCxx17` builds. One
`Keyra.Engine` check, that a top note's body rings on until CC1 mutes it,
measured the grand's free ring 16.09 dB over the muted one with the room
against its 20 dB threshold: the room rings on with what it heard of the
strike after CC1 mutes the strings and the body, as a room does, and the
check measures the body alone, so it now runs with the room off.
`Keyra.VelocityInterpolationFreshness` follows the engine source's hash, and
its receipt was regenerated by its generator; the masks did not change.

The plug-in's `Keyra.ParameterMatrix` needs a JUCE build, which was not made
for this round. A stand-in that plays the plug-in's eleven automatable
parameters, its twelve programs and its block loop over the engine, through
the shared `Tests/ParameterMatrix.h` with `Tests/ParameterMatrixTests.cpp`'s
limits, passed all 2,889 runs, its 321 cases at all nine rates and block
sizes. The room rings on after the release: of one run per case where
silence is due, the loudest tail is the Hamburg Grand's at full Output,
−71.6 dBFS 2 s after the release (−84.1 with the room off), 11.6 dB under
the matrix's −60 dBFS floor.

The 88 keys struck in turn at velocity 90, 120 ms apart with the pedal down,
render in a median 4.00 s of CPU on the grand where 0.4.26 took 3.80
(+5.2 %), 2.72 on the upright against 2.59 (+5.0 %), 2.91 on the Hamamatsu
against 2.83 (+2.8 %), 3.40 on the Hamburg against 3.44 (−1.2 %) and 3.16 on
New York against 3.14 (+0.5 %), seven alternating runs of each on the
development machine.

## 2026-11-09 — the strike knocks the board under 400 Hz

The second of the owner's five rounds of audible improvements, decided on the
recordings with the better candidate taken. No listening test was run and no
listening preference is recorded.

The finding. `fit_realtime_modal.py` measures the strike's knock from 400 Hz
up, and under 400 Hz it fits the body's modes from 20 ms after contact, so
there nothing played the blow: aligned at the strike, the train notes from
C6 up stood a median 1 to 12 dB under their recordings from 160 to 315 Hz
over their first 30 ms on every piano, at 0.4.27
([low knock](research/low-knock-2026-11-09.md)).

The first candidate let the partials of the Hamamatsu, the Hamburg and New
York rise as fitted, as the grand's do, where their rises are capped at the
hammer's contact. Against 0.4.27, summed over the eleven measures other than
level in tolerance units, it brought their train takes closer (the Hamburg
−6.10, New York −3.82, the Hamamatsu −1.55) and their dev takes further
(+6.13, +0.86, +0.11): the Hamburg's dev C♯5 rose in 15.0 ms where it took
1.0, and twelve of the Hamamatsu's rises stood further past a tolerance, its
train A♯4's 1.8 to 12.9 ms. It fitted the train takes and not the pianos, so
it was reverted.

The second candidate is the knock under 400 Hz. `Tools/fit_low_knock.py`
reads each piano's train takes only and writes `Source/DSP/MeasuredLowKnock.h`
and its receipt, which `Keyra.MeasuredLowKnock` checks against the tool, the
room, the modal data, the split and the corpus. In five third-octave bands
from 125 to 315 Hz, each take's power is compared with the engine's played
without the knock, through the engine's band filter, with a knock under one
decay and rise per piano and band and a level per recorded pitch. Its first
fit read the first 0.1 s only and left out the room, which hears the knock:
it brought four pianos closer and the Hamburg further (−0.14 and −0.17 on
the grand, train and dev, −1.33 and −1.06 on the upright, −0.37 and −0.32 on
the Hamamatsu, +0.82 and +1.78 on the Hamburg, −0.13 and −0.90 on New York),
because over 0.1 s a knock decaying at 37 to 50 dB/s fitted the Hamburg's
takes and on to 3 s it and the Hamburg's slow room stood over them. The refit
that ships reads 0.5 s, the benchmark's attack and early windows weighed
alike, and counts what the room returns of the knock, its model checked
against the engine's room on its own. The bands under 400 Hz also start in
their filters' stationary state, drawn from a fixed seed and the same after
every silence, where at rest the knock's first milliseconds would play the
filters' own build-up.

On the benchmark, against 0.4.27 on every train and dev take, the paired
sums in the same units are: the grand −0.11 and −0.14, the upright −3.04
and −2.39, the Hamamatsu −0.32 and −0.37, the Hamburg −0.17 and +1.56 and
New York −0.13 and −0.63. The Hamburg's dev takes stand further at C♯5
(+2.77, four takes), between its train F♯4 and G♯5, where 0.4.27 already
stood over the recordings from 100 to 315 Hz through the attack at the three
softest layers, by 7 to 12 dB at the softest. Past a tolerance: the
upright's dev B3 coherence (0.142 → 0.170, one take); the Hamamatsu's train
C6 attack (4.08 → 4.62 dB), E4 noise (9.47 → 10.01 dB), C4 rise (9.93 →
10.98 ms) and D♯6 early (6.29 → 6.80 dB); New York's dev E4 noise (6.26 →
6.93 dB, five takes); none on the grand or the Hamburg. One score 0.4.27
measured is not measured: New York's train G♯7 sustain at its third layer
(12.76 dB), which 0.4.27 first measured. On the grand's held-out evaluation
the twelve in-range cases' bands stand 4.968 dB from their recordings
(4.988), closer at C5 at velocities 6 and 8 (5.321 → 5.121, 4.661 → 4.475),
C6 (6.688 → 6.526) and F♯5 (5.050 → 5.046) at velocity 8, further at C4 at
velocities 6 and 8 (5.837 → 5.906, 4.460 → 4.512), F♯3 (5.409 → 5.420) and
F♯4 (4.465 → 4.651) at velocity 8, and unchanged at the other four; the
harmonic levels 3.991 dB (3.990), the envelope 1.708 dB (1.707), the partial
decay 2.270 dB/s and the pitch 0.190 cents (unchanged), and the rise
4.038 ms (4.095). The edge cases C1 and C7 at velocity 8 stand 4.589 dB in
bands (4.657), 2.259 dB in harmonics (2.263) and 8.036 dB in envelope
(8.032).

Levels and tests. On the meter, typical playing moves −0.012 to +0.030 VU
from 0.4.27's readings, and the Hamamatsu's through the tube +0.078 VU, past
the test's 0.05 guard: the knock lies under 400 Hz, which the tube's
response favours. Its tube scale is re-pinned to the −9.95 VU it read before
(1.2364 to 1.2253), as in earlier rounds. Six readings then stood past their
approved levels: the five loudest chords 0.4.27 already raised, now the
Hamamatsu's through the tube 3.301832 VU against its approved 3.292226,
Kakegawa Grand 0.719836 against 0.707407, Warm Walnut −0.104002 against
−0.123667, Felt Nocturne −5.592784 against −5.597279 and Open Strings
1.514169 against 1.501300, and Felt Upright's typical playing, −15.589097
against −15.665733, 0.077 VU louder where 0.4.27's reading stood 0.046 VU
louder. Asked whether to accept them and merge 0.4.27 and 0.4.28, the
owner chose to: `Tests/Fixtures/dynamics/ApprovedLevels.h` now holds all
six to six decimals, and `Keyra.Levels` passes.
`Keyra.FactoryDynamics` fails as it did on 0.4.27, on 1,019 rows (992 pairs
under their step floors and 27 chords past its maximum levels) where 0.4.27
failed on 992 (966 and 26). Of the 68 new rows, 67 pairs stand a median
0.020 dB under their floors (0.176 dB at most) and one chord passes its
maximum, the original Hamburg Grand's microphone 0, round 3, shape 7 at
velocity 110, +1.643 against +1.639; 41 of 0.4.27's rows are gone. Its
floors and limits are unchanged. The `unit` tier (45 tests,
`Keyra.LowKnock` and `Keyra.MeasuredLowKnock` among them), the `audio`
tier's demos and the `perf` tier pass, and `KeyraDSPCxx17` builds.
`Keyra.LowKnock` checks that a low key plays none of the knock, that a high
key's lies 99 % and more under 500 Hz, falls 10 dB and more by 0.3 s and
grows with the blow, that the bands' factor holds their filters' stationary
covariance at 44.1, 48 and 96 kHz, and that every silence and `reset()`
leave the bands in one state.
One `Keyra.Engine` check, that a top note's body rings on until CC1 mutes
it, measured the upright's free ring 3.5 dB over the muted one and the
grand's 16.9 dB against its 20 dB threshold with the knock: no string keeps
the knock up, so it rings at its own decay whatever CC1 does, as the knock
above 400 Hz and the action's do, and the check measures the body alone, so
it now runs without the knock as it already ran without the room and the
action; it then reads 44.8 and 58.2 dB, as on 0.4.27. Whether a real board's
knock stops sooner under the dampers or a mute is not measured.
`Keyra.VelocityInterpolationFreshness` follows the engine source's hash, and
its receipt was regenerated by its generator; the masks did not change.

As for 0.4.27, the plug-in's `Keyra.ParameterMatrix` needs a JUCE build,
which was not made; the stand-in described there passed all 2,889 runs, its
321 cases at all nine rates and block sizes. Of one run per case where
silence is due, the loudest tail 2 s after the release is again the Hamburg
Grand's, through the tube −68.7 dBFS where 0.4.27 read −73.3 and at full
Output −69.2 (−71.6), 8.7 dB under the matrix's −60 dBFS floor: its room
rings on with what it heard of the knock. With the room off the loudest
tails read as on 0.4.27 (−81.95 dBFS), and the knock's own decay leaves 22
more cases' tails over −180 dBFS, the loudest at −106.8.

The 88 keys struck in turn at velocity 90, 120 ms apart with the pedal down,
render in a median 3.77 s of CPU on the grand where 0.4.27 took 3.74
(+0.9 %), 2.70 on the upright against 2.63 (+2.9 %), 2.85 on the Hamamatsu
against 2.81 (+1.4 %), 3.27 on the Hamburg against 3.28 (−0.3 %) and 3.03 on
New York against 3.05 (−0.5 %), seven alternating runs of each on the
development machine.

A finding from before this round. Struck alone at velocity 127 and let go
after 0.5 s, 54 of the five pianos' keys from F6 up still sound a minute
later at the default Output, on 0.4.27 as on 0.4.28, so the engine never
comes to rest after them. On the two looked at, the Hamamatsu's and the
upright's C7, partials whose fit stopped at the fitter's slowest decay,
0.003/s, where it identified none, keep ringing: the upright's C7 plays its
6.5 kHz partial at −60 dBFS a minute on, its other keys from A♯6 to D♯7
−66 to −77 dBFS, and every other key −83 dBFS or quieter. It is left to the keyboard's
calibration, which follows the five rounds.

## 2026-11-09 — the strike's wave reaches the bridge

The third of the owner's five rounds of audible improvements, decided on the
recordings with the better candidate taken. No listening test was run and no
listening preference is recorded.

The finding. A hammer strikes its string about an eighth of the speaking
length from the near end, and the board hears the string only once the
strike's wave has run the other seven eighths to the bridge. In the
recordings of four pianos a bass key's band under 400 Hz comes in after its
band over 2 kHz by about that time, from A0 to C♯1 12.5 ms on the Kakegawa
grand, 14.0 on the upright, 11.2 on the Hamamatsu and 16.7 on the Hamburg,
where 0.4.28 brought both in 1.1 to 3.4 ms apart ([string
travel](research/string-travel-2026-11-09.md)). New York's bass takes start
too close to their sound to show it.

The candidates. Every one starts a key's partials and its knock on the
body's modes when the wave reaches the bridge, at the fundamental's group
velocity for the key's stiffness: 13.4 ms after the strike at C1, 2.0 ms at
A3, with no fitted number. The first three let each partial's oscillator run
from the strike and held its rise until the wave arrived; they differed in
what else waited (the first left the knock at the strike, the second also
held the strike's noise, whose click came 10 ms late). Their partials came
in at the phase their oscillators had run to rather than the one fitted at
contact, and the third, benchmarked, stood further on every piano's train
takes (+5.08 on the grand, in tolerance units summed over the eleven
measures other than level). The fourth plays each key as one time shift of
its fitted sound, every lane run back by the wait so it arrives at its
fitted phase; the fifth starts each partial at its own group velocity, a
stiff string's higher partials sooner. Against 0.4.28 the fifth stood
further on three pianos' dev takes (the grand +0.78, the upright +1.20, New
York +0.37) and the fourth closer on all five. 0.4.29 ships the fourth. The
hammer's noise and the key landing do not travel the string and stay at the
strike.

On the benchmark, against 0.4.28 on every train and dev take, the paired
sums are: the grand −0.04 and −0.02, the upright +0.11 and −0.19, the
Hamamatsu +0.38 and −0.55, the Hamburg −1.05 and −0.18 and New York +0.33
and −0.29. The grand's train bass, A0 to B2, stands 0.32 dB closer in the
envelope and 0.25 dB in the attack. Past a tolerance, 25 scores stand
further: 14 rises, eleven of them from C4 up, where the wave takes 1.7 ms or
less and the rise moves where the envelope stands near its 90 % line, the
grand's F♯5 the most (train 0.86 → 7.34 ms, dev 1.21 → 7.07); 8 scores of
the deepest keys, which wait 13 to 16 ms, the grand's dev A0 attack (4.27 →
5.87 dB), early and sustain, the Hamamatsu's train A0 attack (7.81 → 9.77)
and early and C1 attack, and New York's train C1 attack (7.45 → 9.81) and
envelope; the upright's train E3 and the Hamamatsu's train C2 noise (17.77 →
18.38, 4.34 → 4.85 dB); and the Hamburg's train G♯5 coherence (0.15 → 0.19).
The Hamamatsu's recordings come in 11.2 ms apart from A0 to C♯1, where the
wave takes 13.4 and 0.4.29 15.3. On the grand's held-out evaluation the
twelve in-range cases stand 4.950 dB from their recordings in bands (4.968),
3.990 dB in harmonics (3.991), 1.676 dB in envelope (1.708), 2.270 dB/s in
decay and 0.190 cents in pitch (both unchanged) and 4.090 ms in rise
(4.038): C2 at velocity 8 rises 1.19 ms from its recording's where it stood
10.83 ms off, and F♯5 8.10 where it stood 0.98, as on the benchmark. The
edge cases C1 and C7 at velocity 8 stand 4.603 dB in bands (4.589), 2.284 dB
in harmonics (2.259) and 8.275 dB in envelope (8.036), C1's envelope 2.38 →
2.86 dB.

Levels and tests. The engine stays linear, but a chord's notes now start at
their own waits, so the coincident partials of notes struck together meet at
other phases: single notes keep their level, and a chord's level moves with
its voicing. The open-fifth chord E1, B1, E2, B2, E3 through the Kakegawa
grand's tube played 5.1 dB under its notes' powers summed and plays 2.1 dB
over them, from 60 to 140 Hz 8 to 9 dB louder; through New York's tube the
same chord played 3.0 dB over them and plays 3.4 dB under. On the meter, the
presets' typical playing moves 0.09 dB at most from 0.4.28's readings and
New York's tube 0.12 dB. Of the readings past the test's 0.05 guard, the
pianos' own are re-pinned to the readings they held before, as in earlier
rounds: New York's tube (−8.90 VU) from 1.6122 to 1.5890, the Hamamatsu's
default sound (−8.92) by its output scale, from 3.5030 to 3.4816, and with
it the Hamamatsu's tube, which that took from −9.99 to −10.05 VU, from
1.2253 to 1.2391. Eleven readings then stood past their approved levels, the
loudest chords of the grand's tube 1.717973 VU against its approved
1.222194, the Hamburg's tube 2.560835 against 2.196889, Kakegawa Grand
1.408187 against 0.719836, Studio Grand 1.234696 against −0.019715, Warm
Walnut 0.620191 against −0.104002, Open Strings 1.934134 against 1.514169,
Hamburg Grand 2.474622 against 2.404007 and New York Grand 3.322501 against
3.213257, and the typical playing of Studio Grand −10.171010 against
−10.241775, Open Strings −7.970366 against −8.081521 and Pop Upright
−9.306939 against −9.214799. Asked whether to accept them and merge 0.4.29,
the owner chose to: `Tests/Fixtures/dynamics/ApprovedLevels.h` now holds all
eleven to six decimals, and `Keyra.Levels` passes. `Keyra.FactoryDynamics`
fails as it did on 0.4.28, on 1,134 rows (1,038 pairs under their step
floors and 96 chords past its maximum levels) where 0.4.28 failed on 1,019
(992 and 27). Of the 372 new rows, 289 pairs stand a median 0.095 dB under
their floors, 4.875 dB at most, the expanded panel's Hamamatsu Grand through
the tube, A1, E2, A2, C3, E3, A3 from velocity 64 to 80, whose chord at 64
plays 5.6 dB louder than on 0.4.28; 83 chords pass their maximum levels by a
median 0.43 dB (2.52 at most), 60 of them the Kakegawa Grand's; 257 of
0.4.28's rows are gone. Over the audit's 2,120 pairs the median step moves
−0.005 dB and the median chord +0.006 dB. Its floors and limits are
unchanged.

Two `Keyra.Engine` checks read chords where the change exposed their
fixtures, both corrected beside them. The check that a chord is its notes'
sum read the chord at the default Output, where the output stage now acts on
its attack (−28.6 dB against the −35 dB limit); it reads it 24 dB down, as
the headroom check reads its chords, and the chord is its notes' sum to
−129 dB. The headroom check took the emergency bound ahead of the stage as 4
(+12 dBFS) in its own units, where `ForteOutput` feeds the guard half of
what it reads and clamps it at 4, so the bound is 8 (+18 dBFS); the
upright's ten-note chord peaks at +9.3 dBFS, 8.7 dB under it.
`Keyra.VelocityInterpolationFreshness` follows the engine source's hash, and
its receipt was regenerated by its generator; the masks did not change. A
third check is new: on every piano, C1 struck alone with the action, the
room and the knock under the noise bands off plays under 400 Hz over its
first 12 ms only the hammer's noise, 51 to 70 dB under the 10 ms from
14.4 ms on, where its partials play; through `keyra_render`, 0.4.28 read 3
to 12 dB. The `unit` tier (45 tests), the `audio` tier's demos and the
`perf` tier pass, and `KeyraDSPCxx17` builds.

As for 0.4.27 and 0.4.28, the plug-in's `Keyra.ParameterMatrix` needs a JUCE
build, which was not made; the stand-in described there passed all 2,889
runs, its 321 cases at all nine rates and block sizes. Of one run per case
where silence is due, the loudest tail 2 s after the release is again the
Hamburg Grand's, through the tube −69.0 dBFS where 0.4.28 read −68.7 and at
full Output −70.9 (−69.2), 9.0 dB under the matrix's −60 dBFS floor. With
the room off the loudest tail reads as on 0.4.28, the Hamamatsu Grand's at
full Hammer brightness −81.9 dBFS (−81.95), and as many runs as on 0.4.28
leave a tail over −180 dBFS, 295 of 353.

The 88 keys struck in turn at velocity 90, 120 ms apart with the pedal down,
render in a median 3.81 s of CPU on the grand where 0.4.28 took 3.84
(−0.7 %), 2.67 on the upright against 2.67 (0.0 %), 2.90 on the Hamamatsu
against 2.84 (+2.1 %), 3.28 on the Hamburg against 3.31 (−1.0 %) and 3.19 on
New York against 3.20 (−0.3 %), seven alternating runs of each on the
development machine.

## 2026-11-09 — the orders a fit left out of a string's series

The fourth of the owner's five rounds of audible improvements, decided on
the recordings with the better candidate taken. No listening test was run
and no listening preference is recorded.

The finding. A struck string sounds every order of its series, and a fit
leaves an order out where it cannot tell the partial from what sounds beside
it; 0.4.29 played nothing there. Scored as the benchmark scores partial
levels, the orders a render lacked carried 15 % of the Hamamatsu's partial
error on its train takes and 24 % on its dev takes, 4 % or less on the other
pianos ([series orders](research/series-orders-2026-11-09.md),
`Tools/measure_absent_orders.py`). Its G♯3 holds no 12th to 20th partial
between neighbours 21 and 30 dB under its strongest. Most of the orders the
fits lack sit in a series' sparse upper tail, 60 to 100 dB under its
strongest partial.

The candidates. Both play each order a series lacks between two it holds as
a partial between two recorded pitches plays, between its neighbours in
power, balance and image, with no fitted number. The first fills every gap;
the second only where, from g orders under a gap g orders long to g over
it, the series holds at least as many orders as it lacks. Against 0.4.29,
in tolerance units summed over the eleven measures other than level, the
first stood closer on every piano's train takes and further on three
pianos' dev takes (the upright +0.38, the Hamburg +0.99, New York +0.13),
mostly in the noise between partials, the upright's D♯2 at velocity 122 from
8.13 to 10.31 dB. The second stood closer on every train take, closer on the
grand's and the Hamamatsu's dev takes, 0.05 further on the upright's and New
York's and 0.94 further on the Hamburg's, all of it one note. 0.4.30 ships
the second, as the dev takes are never fitted.

On the benchmark, against 0.4.29 on every train and dev take, the paired
sums are: the grand −0.08 and −0.04, the upright −0.15 and +0.05, the
Hamamatsu −1.34 and −0.30, the Hamburg −0.13 and +0.94 and New York −0.11
and +0.05. The Hamamatsu's train takes stand 0.46 dB closer in partial
levels (8.32 → 7.86) and its dev takes 0.14 dB (9.63 → 9.50); its G♯3 at
velocity 95 stands 4.70 dB from its recording in partials where it stood
14.04. Past a tolerance, four scores stand further: the upright's dev B3 at
velocity 122 in decay (3.32 → 6.36 dB/s), the Hamburg's dev E3 in noise
(5.51 → 6.80 dB, at velocity 80 9.1 dB over its recording at 6.35 kHz where
it stood 7.4), the Hamamatsu's train E5 in decay (5.19 → 6.42 dB/s), and the
Hamamatsu's train G♯3 at velocity 69 loses its noise score (5.47 dB). The
Hamburg's eight dev takes carry their whole move in noise on that E3. On the
grand's held-out evaluation the twelve in-range cases stand where they stood
(4.950 dB in bands, 3.990 dB in harmonics, 1.676 dB in envelope, 2.270 dB/s
in decay, 0.190 cents in pitch, 4.090 ms in rise), and the edge cases C1 and
C7 at velocity 8 stand 4.602 dB in bands (4.603), 2.284 dB in harmonics and
8.275 dB in envelope.

Levels and tests. On the meter the presets' typical playing and the pianos'
default sounds stand within the test's 0.05 guard of their approved
readings, and one reading stands past its approved level: the Hamburg's
loudest chords through the tube, 2.587909 VU against 2.560835. Asked
whether to accept it and merge 0.4.30, the owner chose to:
`Tests/Fixtures/dynamics/ApprovedLevels.h` now holds it, and `Keyra.Levels`
passes. `Keyra.FactoryDynamics` fails as it did on 0.4.29, on 1,136
rows (1,040 pairs under their step floors and 96 chords past its maximum
levels) where 0.4.29 failed on 1,134 (1,038 and 96): six pairs are new, a
median 0.02 dB under their floors and 0.11 dB at most, and four of 0.4.29's
are gone. Over the audit's 2,120 pairs the median step and the median chord
move under 0.001 dB. Its floors and limits are unchanged.

Two checks walked a blend's output beside the two recorded pitches' fitted
partials, one entry for each order either fit holds, and the fills put them
out of step; both are corrected beside them. `Keyra.PitchBlend` walks the
pitches' series as they are blended, fills included, and holds every shared
order between them. `Keyra.RateInterpolation` renders that the support
prior for an unidentified decay leaves a recorded pitch as it was; a filled
order is blended with that prior by design, so it takes the nearest pitches
whose series hold no fill. `Keyra.SoftLaneContinuity` found the Hamamatsu's
F♯2 playing a filled partial's two equal-rate lanes with each other's
una-corda bias: a filled partial's lanes take their bias by their own rank,
equal rates in lane order, and at a recorded pitch a partial paired with a
filled one plays as that pitch's series holds it.
`Keyra.VelocityInterpolationFreshness` follows the engine source's hash, and
its receipt was regenerated by its generator; the masks did not change. The
`unit` tier (45 tests), the `audio` tier's demos and the `perf` tier pass,
and `KeyraDSPCxx17` builds.

The 88 keys struck in turn at velocity 90, 120 ms apart with the pedal down,
render in a median 3.75 s of CPU on the grand where 0.4.29 took 3.73
(+0.5 %), 2.61 on the upright against 2.60 (+0.3 %), 2.89 on the Hamamatsu
against 2.80 (+3.3 %), 3.34 on the Hamburg against 3.29 (+1.6 %) and 3.19 on
New York against 3.11 (+2.5 %), seven alternating runs of each on the
development machine: a filled order is one more partial, and the Hamamatsu
fills the most.

## 2026-11-10 — the undamped strings under a soft bass note

The last of the owner's five rounds of audible improvements, decided on the
recordings with the better candidate taken. No listening test was run and no
listening preference is recorded.

The finding. Every strike sets the undamped strings from F6 up ringing, louder
as the strike plays louder, by one law `fit_realtime_modal.py` fits on the
recorded pitches from F♯3 up: a slope in dB per dB of the strike's layer that
rises or falls per octave the string lies over the key. New York's falls by
0.51 per octave from 1.95 and passes under 0 at 3.8 octaves, which bass keys
reach and the fitted takes do not, so 0.4.30 rang the strings louder the
softer a bass key was struck: the C1, F1 and A♯1 at velocity 13 stood 30 to
49 dB over their recordings from 1.6 to 4 kHz
([undamped strings](research/halo-slope-2026-11-10.md)). The other four
pianos' laws never fall under 0.

The candidates. Both hold the law where it falls under a bound, with no
fitted number: the first at 1 dB per dB, as a hammer that never grows duller
would bound it, the second at 0, as a softer blow never rings a string louder.
Against 0.4.30 on New York's takes, in tolerance units summed over the eleven
measures other than level, the first stood 3.41 closer on the train takes and
1.37 further on the dev takes, its soft D♯2 and G♯2 left under their
recordings from 2 kHz up; the second stood 4.56 closer on the train takes and
1.90 closer on the dev takes. 0.4.31 ships the second.

On the benchmark New York's train takes stand 1.52 dB closer in the noise
between partials (7.98 → 6.46) and its dev takes 0.85 dB (8.87 → 8.02). Past a
tolerance two scores stand further, both train takes in rise: F1 (24.56 →
26.46 ms) and A♯1 (5.20 → 6.33 ms). The Kakegawa grand, the upright, the
Hamamatsu and the Hamburg render byte for byte as on 0.4.30, so their
benchmarks and the grand's held-out evaluation stand where they stood.

Levels and tests. Every meter reading stands within its approved level.
`Keyra.FactoryDynamics` fails as on 0.4.30, on the same 1,136 rows; New
York's pairs move by under 0.001 dB. The `unit` tier (45 tests), the `audio`
tier's demos and the `perf` tier pass, and `KeyraDSPCxx17` builds. On the
development machine New York's 88 keys in turn with the pedal down render in
a median 2.90 s of CPU against 2.98, within the runs' spread.

## 2026-11-10 — each key's level and balance at its neighbours'

The first step of the owner's calibration of every piano across the
keyboard, decided on the measurements with the better candidate taken. No
listening test was run and no listening preference is recorded.

The finding. Struck in turn, the Hamamatsu grand's stereo balance swung by
10 to 13 dB from one key to the next between E4 and C6 and the upright's by
up to 10 dB between A♯3 and C6, and at velocity 40 the Hamamatsu's level
stood up to 8 dB off its neighbours'. The recordings swing so themselves:
each pitch was taken alone, with its own microphone image and gain
([key smoothing](research/key-balance-smoothing-2026-11-10.md)).

The owner's choice (2026-11-10, on a decision card): smooth the recordings'
own key-to-key jumps even where that departs from them, each key's balance
and loudness pulled toward its neighbours' median at every velocity, its
tone and decay kept as recorded. This licenses the train takes standing
further from their recordings in stereo balance and level; it does not
license any fitted number, and none is fitted.

The candidates. At each recorded layer each key's level and balance go to
the median of the keys around it. The median of seven alone kept the steps
of the Hamamatsu's swing (5.9 dB to one side at E5, 3.7 to the other at F5),
so the median of thirteen averaged over seven ships; both windows narrow at
the keyboard's ends, as at full width they flattened the top-note trims.
The gain on the partials alone, against the partials and the key's noise
burst together: the second stood closer on nine of the ten pianos' train and
dev sums and ships.

On the benchmark, against 0.4.31, in tolerance units over the eleven
measures other than level: New York +0.53 train and −0.32 dev, the Hamamatsu
+4.79 and −1.36, the upright +2.43 and −0.09, the Kakegawa grand +1.36 and
+0.44, the Hamburg +0.40 and −0.29. The stereo balance carries the train
takes' moves (the Hamamatsu's 1.77 to 4.49 dB); its dev takes stand 0.73 dB
closer in it, and partial levels stand closer on every piano and role but
the Hamburg's dev takes. The grand's held-out cases stand closer in bands,
harmonics and decay and further in envelope and rise (4.090 to 4.514 ms).

Levels. Each piano's output and tube scale is re-pinned to the reading it
had before. The owner approved thirteen new readings of the presets that
play a piano at another width, brightness or mute (2026-11-10: "approving
new levels - app is not released yet"), recorded to six decimals in
`Tests/Fixtures/dynamics/ApprovedLevels.h`. `Keyra.FactoryDynamics` fails
on 995 rows where 0.4.31 failed on 1,136. The `unit` tier (45 tests), the
`audio` tier and the `perf` tier pass, and `KeyraDSPCxx17` builds. The
engine's construction takes 0.28 s of CPU where it took 0.05.

## 2026-11-10 — a key struck again is not turned down

Decided on what the model can defend, with the candidate taken as the
project's rule has it, and then chosen by ear: the owner heard the listening
set (the grand and the upright, A and B matched on whole-file RMS, B trimmed
2.10 and 1.59 dB down) and chose B (2026-11-10).

The finding. Since 0.4.12 a strike on a key that still sounded was turned
down by how much of the key's earlier sound was left: its partials by up to
26 % in amplitude, its knock and noise by up to 28 %, its ring on the
undamped strings by up to 35 %, with a rise up to 20 % shorter, a colour up
to 1.08 dB an octave brighter and a pull on its partials' pitch and phase.
0.4.12's commit carried no write-up, and no recording in any of the corpora
strikes a sounding string, so every one of those numbers was drawn.

The candidates. A is 0.4.34. B plays the strike as it plays on strings at
rest and adds it to what sounds, which is what a linear string does with a
second blow: where the two waves meet in phase at a partial the strike is
louder, and where they oppose it is softer. A real hammer on a moving string
also changes its contact with the string's phase; a third candidate that
played that would need a contact law and a number no recording here gives,
so under the listening tests' limit none was built.

What it measures. Played as the plug-in plays, pedal down, the level of each
strike's first 100 ms against the first strike's, C4 six times at 0.25 s,
velocity 80:

| | 2nd | 3rd | 4th | 5th | 6th |
| --- | --- | --- | --- | --- | --- |
| grand, A | +0.4 | −2.4 | −3.8 | −3.9 | −4.6 |
| grand, B | +1.5 | −0.4 | −1.2 | −0.6 | −1.9 |
| upright, A | −3.1 | −7.8 | −5.0 | −2.2 | −6.5 |
| upright, B | −1.0 | −5.9 | −2.5 | −0.8 | −4.6 |

A C4 at velocity 110 after one at 50 stood 2.1 dB (grand) and 2.8 dB
(upright) under the same strike alone in A, and 0.3 and 1.0 dB under in B.
What is left in B is the two waves' phases at a strike interval that is a
whole number of periods apart each time, which A has as well. The same
phrases through Arturia's Piano V3, the owner's renders of three of its
pianos, stand −1.9 to +2.0 dB at C4, +0.8 to +5.6 dB at C2 and +1.1 to
+8.2 dB at C6 against their first strike, never turned down as A's are.
Piano V3 is itself a model, so it is a second opinion on the direction and
not a measurement of a piano; no audio of it is kept here.

What it licenses. Removing numbers nothing measured, not a new law: the
hammer's meeting with a moving string stays a Known gap. A phrase with the
pedal held now plays louder where keys repeat, 2.1 dB over 0.4.34 on the
grand and 1.6 dB on the upright in whole-file RMS over the listening set's
phrase (C4 six times, a chord four times, G5 ten times, C2 three times).

Levels and tests. A strike on strings at rest is unchanged: the benchmark's
single notes render byte for byte as on 0.4.34 (thirty checked, five pianos,
three keys, two velocities), so the benchmarks and the grand's held-out
evaluation stand where they stood. `KeyraLevels` reads every level within
its approval, and `Keyra.FactoryDynamics` fails as on 0.4.34 with the same
audit, byte for byte. `Keyra.Engine` holds a restrike under the pedal to the
same strike on another channel's strings, sample for sample. The `unit`
tier, the `audio` tier's demos and the `perf` tier pass, and `KeyraDSPCxx17`
builds.

## 2026-11-10 — a strike rings the open strings

Decided on a measurement, with the candidate taken as the project's rule has
it. A listening set was rendered and handed over; no listening verdict is
recorded.

The finding. Under the pedal the open strings rang only with what the notes'
partials drove at resonance, so only the strings that share a note's partials
built up, and a pedalled note stayed clean between them. The Yamaha C3's
pedal-down takes show otherwise: from 0.15 s on, the sound between a note's
partials holds 24 to 26 dB under the whole note in the middle register, 10
to 20 dB over the same key's pedal-up take, which lies on the recording's
floor there. By one protocol (`Tools/benchmark_pedal_wash.py`) the grand
stood a median 26 dB under those takes between the partials, 12.5 dB from
0.15 to 0.5 s and 42 dB from 3 to 6 s.

The candidates. A is 0.4.35. B starts every open string but the struck key's
own at the strike, each open partial at a level set by the strike's partial
nearest it in pitch. Two numbers are fitted on the grand against the takes'
17 train pitches: the level, 49 dB under the power that partial's components
start with at middle C, and its fall, 2.7 dB per octave the struck key lies
higher (Theil–Sen over the train pitches; least squares gives 3.1). Under the
strike's first partial the takes ask for 10 to 12 dB per octave more, played
as the square of the frequency ratio. Nothing else was needed: fitted so,
the octave bands from 150 Hz to 2.4 kHz, the windows from 0.15 to 3 s and
the three layers each stand within 2 dB of the train takes in their medians,
with the open strings' decay as it was. A first pass sized the level through a render that played
the ring at the notes' own level; the output stage turned that render down
and the level came out 4.5 dB high, so the figures here are from renders at
the level that ships.

What was left alone. From 3 to 6 s Keyra stands 3 to 17 dB under the takes
because full pedal leaves the felt grazing the strings, which the owner chose
on 2026-10-30; that choice stands. How a note's own partials decay under the
pedal against without it was measured on the same takes in the session: a
ratio of 0.96 in the middle register on the Yamaha and on the grand, 0.75
against 0.87 in the bass and 0.93 against 0.95 in the treble. So the pedal's
unloading of the bridge was left as it is; those figures are not tracked.

What it measures. Render minus takes, bands holding partials, median and
mean |dB|: the grand's train pitches −26.3 and 26.7 before, −1.1 and 5.7
after; its five dev pitches −22.2 and 22.6 before, +4.7 and 6.4 after. The
other four pianos, which play the same two numbers against their own
partials, move from 13.6 to 24.2 dB off to 5.9 to 8.9 dB
([report](validation/pedal-wash-benchmark-2026-11-10.md)). The Yamaha C3 is
none of Keyra's pianos, its strike force and microphone blend are unknown,
and the spread from key to key is the larger part of what is left.

What it licenses. One level and one slope, fitted on train pitches and
scored on dev pitches, for every piano. It does not license a wash per piano,
a wash over 2.4 kHz other than what the fitted law gives there, or a level
for the strings that share a note's partials, which a recording cannot tell
from the note: that stays the Resonance control's.

Levels and tests. A note alone without the pedal renders byte for byte as on
0.4.35 (ninety on the grand, thirty over the five pianos), so the benchmarks'
single notes stand where they stood. `Keyra.Engine` holds E4's string, under
a struck C4, 39 dB under C4's first partial and G3's 5 dB lower. Two of its
checks searched 6 % either side of the concert pitch for the sympathetic
bank's peak and now find the strings of the key a semitone up, which the
blow rings; they search 2.5 % either side, where a bank left at 440 Hz would
still peak. `KeyraLevels` reads every level within its approval
(`Keyra.Levels`), and `Keyra.FactoryDynamics` fails as on 0.4.35 with the
same audit, byte for byte. The `unit` tier's other 43 suites, the `audio`
tier's demos and the `perf` tier pass, and `KeyraDSPCxx17` builds. The takes'
energies in `Tools/corpus/yamaha-c3-pedal-wash.json` were measured on the
owner's copy of the library by the tool's own procedure.

The owner's renders of Arturia's Piano V3 prompted the measurement: its
pedalled notes build a wash Keyra's did not. It is a model and no audio of
it is kept here; the level comes from the Yamaha C3's takes alone.

## 2026-11-10 — the pedal's sizes from 0.4.12, measured and left

No listening test and no change to the engine. 0.4.12 gave a note struck
under the pedal a longer ring (its decay rates lower by 0.20 on the grand's
and the Hamamatsu's strings, 0.30 on the others', less up the series), a
drive of the open strings 1.65 times as hard, 12 % more of the undamped
strings' aftersound, and 0.78 of the late body ring for a note struck within
1.2 s of another. Its commit carried no write-up and none has a source.

What was measured. `Tools/benchmark_pedal_wash.py` now reports, beside the
sound between the partials, how the whole note holds up under the pedal
against the same note without it, on the Yamaha C3's pedal pairs and on the
render ([report](validation/pedalled-note-ring-2026-11-10.md)). Every
piano's train median stands within 1.6 dB of the takes from 0.5 to 6 s, and
each pair lies 2 to 3 dB from its take either way. By register the Kakegawa
grand holds up as the takes do from C1 to A2 and 3 dB short of them from C3
up at 1.5 to 3 s. The entry above read the partials' decay under the pedal
as 0.96 of that without it in the middle register on both; that was a median
over eight partials, and the first three, which carry the note, stood at 0.8
to 0.9 on the takes.

What was tried, on the grand in a scratch build. Twice the ring's share
halves the shortfall from C3 to A4 and takes the pairs' mean miss down in two
of the six train and dev windows by 0.7 and 1.1 dB, and it plays the first
half second 1.3 dB louder against the note without the pedal, where the
takes' median is 0.6 dB quieter. Four times overshoots every window. The
drive of the open strings moves the medians 1.3 dB at most from 1 to 9
times; at 21 times the median stands 2 dB over the takes to 3 s and the
pairs' mean miss before 1.5 s goes from 2.6 to 4.6 dB. The takes' rise comes
late, as a slower sound beside the note would make it, and a lower decay
rate lifts every window from the start; neither size brings the pairs
closer than the takes lie from one another.

What each is worth in a phrase. The pedal-wash listening phrase, rendered
with one size taken out at a time: without the longer ring it differs 20 dB
under the phrase's level on the grand and 17 dB on the upright, 9 dB under
in the second after the first five notes; without the harder drive 44 dB
under, 29 and 34 dB under in its worst second; without the crowding factor
56 and 47 dB under, 40 and 33 dB in its worst second; without the undamped
strings' 12 %, 90 and 75 dB under, on a phrase that plays none of their keys.

What stands. All four sizes, each now with what is known beside it in
`Source/DSP/KeyraEngine.cpp`. The crowding factor needs notes played one
after another against their MIDI, which no corpus here holds.

## 2026-11-10 — the finger's knock on the key is left out

The owner asked whether the sound of fingers or nails hitting the keys would
be audible to model, and chose to leave it out. No listening test.

What is known. Goebl, Bresin and Fujinaga (JASA 136(5), 2014, 2839–2850)
recorded middle C on a 173 cm Yamaha grand 10 cm from the strings, played by
two pianists pressed from the key's surface and struck from above, 25 hammer
velocities each from 0.37 to 4.1 m/s, and publish the 100 tones with 250 ms
kept before the hammer (16 kHz, 16 bit). Half of their 22 musicians told
struck from pressed better than chance, up to 86 % correct, and none did once
the sound before the tone was cut. They put the knock 20 ms before the tone
at very loud and 200 ms or more at pianissimo.

What was measured here, on those tones over 100 Hz. A pressed key shows
nothing over the recording's floor. A struck key's knock clears the floor
from a hammer velocity of about 0.8 m/s up: it leads the hammer by 55 ms
there and 11 to 17 ms at 4 m/s, about 45 to 65 ms·m/s over the hammer's
velocity, and its peak stands 16 to 34 dB under the tone's peak with one
pianist and 26 to 43 dB with the other. The Salamander takes start 11 to
15 ms before the tone and hold nothing earlier. The tones were fetched for
this and are not kept.

Why it is left out. The knock comes before the hammer, and a note reaches the
engine at about the hammer's moment, so playing it means delaying every note
by about 60 ms, and MIDI does not say whether a key was struck or pressed.
The owner was offered it as an option that is off by default and adds that
delay, and chose to leave it out.


## 2026-11-10 — una corda resized from concert performances

Played from the MIDI of thirty MAESTRO performances, the grands' soft pedal
took 1 to 4 dB more than the recorded pianists' from 125 Hz to 2 kHz
(`Docs/validation/played-phrases-maestro-2026-11-10.md`). Its sizes were
0.4.12's, without a source. MAESTRO is licensed CC BY-NC-SA 4.0 and Keyra is
sold, so the owner was asked whether the pedal may take its sizes from
numbers measured on those recordings, nothing of them copied, and chose to
resize it from the measurement.

What was decided by the measurement, on the train performances: the level at
0.72 under the pedal goes, the partials' fall of 1 dB each stays but stops at
the fifth above the first, the prompt lane's move to the slowest stays as it
was (`Docs/validation/una-corda-maestro-2026-11-10.md`). A second candidate
without the lane move, at 0.90 of the level, fitted the first 0.2 s of a note
as well; the performances hold too little after 0.5 s to tell the two apart,
and the first was taken because it keeps the engine's account of the pedal
and drops only the size the recordings contradict. That choice is a
judgement, not a measurement.

A lettered set went to the owner with 0.4.37: an original phrase played first
without the soft pedal and then with it, on the Kakegawa and Hamburg grands,
A 0.4.36 and B 0.4.37, not level-matched because the pedal's level is what is
judged. By the project's standing rule B stands unless the owner says
otherwise.

## 2026-11-10 — the candidates stand, and 0.4.38's level readings

With 0.4.38 three things waited on the owner: the lettered set for the open
strings under a strike (A 0.4.35, B 0.4.36), the lettered set for una corda
(A 0.4.36, B 0.4.37), and ten level readings that moved when the key
smoothing took in the strike's velocity colour and the keyboard's ends and
the Kakegawa grand's, the Hamamatsu's and the Hamburg's output and tube
scales were re-pinned to their earlier readings. The owner answered all
three with "use candidate": B stands in both sets, chosen by the owner
without a letter-by-letter account of what was heard, and the ten readings
are approved, to six decimals (`Tests/Fixtures/dynamics/ApprovedLevels.h`):
the typical playing of Studio Grand (−9.88 to −9.66 VU), Warm Walnut (−10.66
to −10.41), Felt Nocturne (−17.54 to −17.28), Open Strings (−8.17 to −7.98)
and Pop Upright (−9.71 to −9.85), and the loudest chords of the Kakegawa
Grand (1.57 to 1.70 VU), Studio Grand (1.23 to 1.29), Warm Walnut (1.01 to
1.16), Felt Nocturne (−5.32 to −5.11) and Open Strings (2.05 to 2.16)
([key smoothing](research/key-balance-smoothing-2026-11-10.md)).

## 2026-11-10 — version 1.0.0

The owner asked for Keyra to be ready for a production release and, with
0.4.38 on main, set the version to 1.0.0. It is 0.4.38's engine, unchanged.
The number is the owner's product decision, not a fidelity or acceptance
measurement: the gates the README's Known gaps and
`Docs/plans/production-readiness.md` list as unverified (the Audio Unit's
auval, Windows, manual DAW workflows, interactive Rack controls and song
recall, retail Reason, target-chip CPU) are as they were, and
`Keyra.FactoryDynamics` fails as it did on 0.4.37. Tagging and publishing
the release remain the owner's steps.


## 2026-11-11 — the piano rewritten as a physical model (2.0.0)

The owner was not happy with the engine: the mechanical part was liked, the
keys' own sound "very low-quality". The owner asked for it to be rewritten
from zero as a physical model of the piano on current research, versatile
enough to be kept as various grands and uprights, with several microphone
positions (pop, XY, live, distant) and controls for the hammers, the strings'
age, the unisons' detuning, the stretch tuning, the dynamic range, the lid
and the soundboard's, sympathetic and duplex resonance, with the samples of
the owner's training set as reference and benchmark.

2.0.0 is that: `Source/DSP/PianoModel.cpp` replaces the partials fitted from
recordings, and the action's noises, the pedals, the keyswitches and the
output stage are 1.0.0's. Its hammers, losses and frame knock are fitted to
notes of the training set's Steinway grand, the upright's hammer stiffness
to eleven notes of a recorded upright; nothing else is fitted to a recording.

What the measurement says: against the Salamander grand, which 1.0.0 was
fitted to, 2.0.0 is further off on every score of
`Tools/benchmark_recordings.py`, on the notes 1.0.0 trained on and on those
it never fitted (dev: partial levels 5.3 to 11.7 dB, tuning 0.9 to 3.1
cents, decay 2.1 to 5.5 dB/s, rise 4.5 to 15.5 ms;
[report](validation/grand-recording-benchmark-2026-11-11.md)). The upright
was not benchmarked: the Helsinki recordings were not in the session, and
the owner is to be asked for them.

What was decided by ear: two lettered sets went to the owner on 2026-11-11,
A 1.0.0 and B the model, on four phrases (the first demo, the upright demo,
the pedal wash of 2026-11-10 and the nocturne), B matched to A on whole-file
RMS (in the final set by +0.09, +0.98, +0.08 and −0.03 dB), with previews of
each control. The sets are in the project's files and not committed. In the
first set the Hammer previews ran backwards (hard for soft); the final set
replaces it. By the project's standing rule B stands unless the owner says
otherwise, and the owner had asked for the rewrite. So 2.0.0 shipped on the
owner's request and that rule, against a benchmark that favours A.

The verdict, the same day: the owner chose B by ear ("B sounds good
enough"), without a letter-by-letter account, and asked for the work to go
on: the stereo image, how the piano answers velocity, its dynamics, and the
model fitted closer to the recordings. The choice licenses the physical
model as the product; it does not say the benchmark's distance is closed.

## 2026-11-11 — the full pedal rings as long as the one chosen on 2026-10-30

Clear of the strings, the model's dampers let a chord of C3, C4, C5 and C6
ring 17.4 s to −60 dB on the concert grand and 20.5 s on the upright. On
2026-10-30 the owner had found such a ring too long and chosen a full pedal
whose felt still grazes the strings, which on 1.0.0 gave 9.5 s on the grand
and 11.3 s on the upright by the same protocol. That choice is kept, re-pinned
on the new strings: the engine stops the pedal at 0.7 of the travel the model
takes (`pedalLift`, `KeyraEngine.cpp`), which gives 9.6 s on the concert
grand, 12.3 s on the parlor grand, 9.9 s on the baby grand and 10.4 s on the
upright. The number 0.7 is pinned to that earlier choice by measurement; the
owner has not heard it against other stops.

## 2026-11-11 — pinned without the owner's ear in 2.0.0

These were set by derivation or to a recording, and the owner may want them
otherwise:

- The hammers are as hard as the Steinway notes ask, which leaves the grand
  3.5 to 14 dB under 1.0.0's from the 2 kHz octave to the 8 kHz octave on the
  first demo's phrase. Hammer is the control for it; the default was not
  chosen by ear.
- The half pedal lies between about 64 and 89 of CC64, by a law in which the
  felt's loss grows as the square of how far it is let down
  (`damperGoal()`, `PianoModel.cpp`). No recording with documented pedal
  travel is at hand to fit it to.
- The four pianos' dimensions, the microphones' positions and the room are
  typical values, not measurements of an instrument or a hall.

## 2026-11-11 — velocity, the stereo image and a closer fit (2.1.0)

After choosing the physical model the owner asked for the work to go on:
"continue in improving stereo image, behaviour based on velocity, dynamics"
and "keep improving and fitting the physical model to get more real", with a
demo of the microphone pairs, and brought the Helsinki recordings into the
session. 2.1.0 is that round. Five things changed in
`Source/DSP/PianoModel.cpp`, each set against recordings by measurement, none
by ear:

- **Velocity.** The hammer's speed is the velocity to a power, 1 at Dynamics
  0.5 (0.4 to 1.6 across the control), where 2.0.0's speeds were even in dB.
  Against the Salamander grand's sixteen layers 2.0.0's soft and medium
  notes were 2.5 dB too quiet and its hardest 4.4 dB too loud; 2.1.0's stand
  within 2 dB from velocity 31 up and 2.6 dB too quiet below it, and within
  2 dB of the MAPS Disklavier's notes. The Helsinki upright's five layers,
  which cover wide velocity ranges and whose played velocities are not
  documented, agree less well (1.5 dB over at the softest to 4.3 dB under
  at the hardest).
- **Felt.** The felt's exponent is 1 higher with the force kept at 1 mm of
  compression, fitted to the same sixteen layers. Hammer, the practice felt
  and una corda cover half as many decades again, which keeps what each did
  to middle C.
- **Stereo image.** Each soundboard mode may reach a pair's two microphones
  up to a quarter turn out of step (70° under about 220 Hz for the close
  pair), where 2.0.0 held every mode within 70°. Between 500 Hz and 2 kHz
  the Salamander's two channels are 0.05 alike on average in forte notes,
  2.0.0's 0.6 and 2.1.0's 0.4. A law with no quarter-turn bound came closer
  on single notes and was rejected by measurement: a phrase through the
  distant pair summed out of phase (correlation −0.3). On whole phrases the
  channels' correlation went from 0.49 to 0.33 (first demo) and 0.54 to 0.44
  (upright).
- **Radiation.** The board radiates fully to 6 kHz (3 kHz in 2.0.0): the
  middle of the keyboard held 5 to 9 dB less in the 4 kHz octave than the
  Salamander's forte notes.
- **Bridge.** The bridge takes 0.3 as much from the strings between D♯3 and
  D6, fitted to how the Salamander's notes die away.

Not done, by measurement: no lean of low keys to one side and high keys to
the other was added. The Salamander's notes lean left by 3 dB in the bass
and right by 6 dB around A4 to G♯5 with no steady trend, the MAPS upright's
not at all, and neither the microphones' placement nor a lower crossover
gives the model one.

What the benchmark says (`Tools/benchmark_recordings.py`, 2.0.0 to 2.1.0, on
the notes 1.0.0 never fitted). The grand against Salamander
([report](validation/grand-velocity-stereo-benchmark-2026-11-11.md)):
partial levels 11.7 to 8.2 dB, tuning 3.1 to 2.9 cents, decay 5.5 to
3.7 dB/s, attack 9.5 to 8.1 dB, first half second 10.0 to 8.9 dB, sustain
10.9 to 9.1 dB, noise 10.6 to 10.1 dB, envelope 4.8 to 4.2 dB, rise 15.5 to
14.9 ms, level 4.5 to 3.4 dB with each version's own gain. Worse: the
channels' level difference 5.4 to 5.6 dB, their correlation by 0.004, the
level by 0.1 dB when both are scored with 2.0.0's gain, on the fitted notes
the rise (16.1 to 17.3 ms), and 97 single-note scores, the furthest C3's
rise (19 to 57 ms), the levels of C7, A7 and A5 with 2.0.0's gain (4 to
7 dB), C6's first half second (12.8 to 17.2 dB) and the partials and
sustain of F♯5 and C5 (3 to 4 dB). The stereo change is therefore not one
the benchmark's stereo scores confirm.

The upright against Helsinki, benchmarked for the first time
([report](validation/upright-velocity-stereo-benchmark-2026-11-11.md)), is
mixed. Closer: partial levels 8.8 to 8.4 dB, tuning 6.1 to 4.7 cents,
envelope 5.2 to 4.7 dB, level 4.1 to 3.0 dB. Further: decay 5.3 to
5.5 dB/s, attack 7.7 to 8.5 dB, first half second 9.7 to 10.2 dB, sustain
9.9 to 10.8 dB, noise 10.4 to 11.0 dB, rise 12.2 to 12.6 ms, and on the
notes 1.0.0 fitted the attack (8.9 to 9.2 dB), the noise (11.2 to 11.8 dB)
and the channels' level difference (6.4 to 6.7 dB), with 109 single-note
scores worse, most in the bass's noise between its partials (C1 13.7 to
18.5 dB). These come mostly with the velocity law, which the Helsinki
layers fit less well than 2.0.0's; one law was kept for all four pianos
because the Salamander's sixteen layers and the MAPS Disklavier, whose
velocities are the MIDI's own, agree on it.

What is the owner's to hear: a lettered set went to the owner on 2026-11-11
(`2026-11-11-velocity-stereo-fit` in the project's files, not committed), A
2.0.0 and B 2.1.0, on the first demo, the nocturne, the upright demo and one
arpeggio at six velocities, B matched to A on whole-file RMS by −0.65,
−3.61, −1.16 and +0.91 dB, with the first demo through each microphone pair
alone. By the project's standing rule B stands unless the owner says
otherwise; no verdict has been given yet, and 2.1.0 ships on that rule and
on the grand's benchmark, with the upright's regressions as listed.


## 2026-11-11 — an even scale (2.2.0)

**The owner's verdict on 2.1.0, by ear.** After the
`2026-11-11-velocity-stereo-fit` set (A 2.0.0, B 2.1.0) and the first demo
through each microphone pair, the owner wrote on 2026-11-11: "sounds like we
are on the right track. keep improving the model further please." B stands:
2.1.0's velocity law, felt, stereo image, radiation and bridge are kept,
chosen by ear. No letter was singled out and no measurement settled it.

**What 2.2.0 changes: the keys are voiced.** Measured key by key at one
velocity, 2.1.0's keys stood 2.2 to 2.8 dB apart from one to the next and
single keys 7 to 11 dB off a smooth line through the keyboard, in every
microphone pair; the Salamander's keys stand 1.1 to 1.6 dB (standard
deviation) off a cubic through theirs, 2.1.0's 2.1 to 2.2 dB. The cause is
the board: its modes answer each partial's frequency in their own way, which
the model's transfer predicts within 1.5 to 3 dB a partial. A real piano's
keys are uneven in the same way before a technician voices the hammers, so
the model is voiced: `KeyraLevels --write-keys` measures what each key's
strings alone give each pair and every two pairs together (pairs in a mix
add as waves, so a table per pair left mixes 1.8 dB apart), and each key's
strings pull on the board by what brings the key onto a smooth line through
the keys in the mix that is set, at most 12 dB either way. Neighbours stand
0.3 to 0.4 dB apart at the default Lid and Soundboard in single pairs and
mixes, at velocities 40 to 115 and at 44.1 and 96 kHz, and 0.9 to 1.6 dB at
other Lid and Soundboard settings (2.0 to 2.8 dB in 2.1.0). `KeyraLevels
--check` fails when a key stands more than 2 dB off the line. Each piano's
output scale was re-pinned to −9 VU.

This is a measurement's decision, not one by ear: an uneven scale is a
fault a technician removes, and the numbers show it removed.

**Tried and not shipped, by measurement.** The middle of the keyboard holds
13 to 15 dB less in the 2 kHz octave than the Salamander's forte notes. A
rise in the board's radiation around 1.3 to 1.9 kHz (3 to 6 dB, Q 1 to 2.2)
was benchmarked in eleven variants, with and without the rise carried above
the modes. Every one was further from the recordings than 2.1.0 on the
notes 1.0.0 never fitted: with the rise carried, attack 8.50 to 8.76 dB
(2.1.0: 8.11), first half second 9.40 to 9.70 (8.92), sustain 9.57 to 9.83
(9.10), noise 10.70 to 11.13 (10.07), level 4.11 to 4.41 (3.39), and the
middle's partials 7.74 to 8.16 (7.49). None ships. Smoothing the partials
within a note (6 to 10 dB from their neighbours' mean where the
Salamander's stand 2.5 to 5 dB) needed the board's loss raised four to
eight times, which is not a board's; not shipped either.

**What the benchmark says** (`Tools/benchmark_recordings.py`, 2.1.0 to
2.2.0). The grand against Salamander
([report](validation/grand-even-scale-benchmark-2026-11-11.md)), on the
notes 1.0.0 never fitted: level 3.39 to 2.51 dB, noise 10.07 to 9.89 dB,
attack 8.11 to 8.07 dB, first half second 8.92 to 8.86 dB; partials,
tuning, decay, sustain, the stereo scores and the envelope within 0.02; the
rise 14.93 to 15.06 ms. On the fitted notes the partials are 0.08 dB
further off (8.86 to 8.94) and the level 3.72 to 2.68 dB. 21 single-note
scores are worse: F♯4's rise (16.4 to 21.8 ms, 18.0 to 22.9 on the fitted
layers), noise (5.7 to 7.4 dB), attack (4.9 to 5.7 dB) and first half
second (5.0 to 5.5 dB), the levels of
D♯7 (1.5 to 3.2 dB) and A5 (3.3 to 4.9 dB), A1's rise (9.6 to 12.3 ms),
C8's sustain and first half second (by 0.8 to 0.9 dB), A4's noise (6.7 to
7.6 dB), A2's rise (24.1 to 25.7 ms), A7's partials (by 0.7 dB) and A1's
level (0.5 to 1.1 dB).

The upright against Helsinki
([report](validation/upright-even-scale-benchmark-2026-11-11.md)): on the
fitted notes level 5.03 to 4.29 dB and attack 9.21 to 9.11 dB, the rise
16.0 to 16.6 ms; on the 21 notes 1.0.0 never fitted the noise 11.01 to
11.42 dB, the rise 12.6 to 13.0 ms, the level 2.78 to 2.87 dB and the
attack 8.54 to 8.61 dB are further off. 15 single-note scores are worse,
the furthest the rises of F♯4 (1.7 to 8.5 ms), D♯1 (33.1 to 37.9 ms), C1,
C2, C5 and A♯3, the levels of G7 (3.1 to 4.8 dB) and A♯3 (3.6 to 4.3 dB)
and the noise of B3, G♯3, D4, A♯3, D5, C5 and G♯4 (by 0.6 to 1.3 dB).

**Found and left for the next round.** The open strings answer a blow far
too weakly. In the Salamander's treble notes the undamped top strings ring
at their own pitches about 30 dB under the struck note's fundamental over
the first second, more the nearer the struck key, and the model's ring is
40 dB and more under that; what the recordings hold under a treble
fundamental after the blow is this ring, not a knock. Against the Yamaha
C3's pedal-down takes (`Tools/benchmark_pedal_wash.py`, parlor grand) a
struck note leaves 25 dB less between its partials in the median (19 dB in
the first half second, 38 dB after three), and gains nothing under the
pedal where the takes gain 3 to 7 dB from C3 to A4. The model moves a
string's end by the force at its own bridge point through a third of the
plate's point mobility. A first experiment, not shipped, says the bridge is
not the path that is missing: driven by the board's own motion at the
bridge, the top strings ring no more than they do now, while the blow's
lean on the iron frame moving the string ends there gives the recorded
ring's level and its fall for keys struck further down. That is the next
round's work.

**What is the owner's to hear.** A lettered set went to the owner on
2026-11-11 (`2026-11-11-even-scale` in the project's files, not committed),
A 2.1.0 and B 2.2.0: chromatic scales on the concert grand at velocity 80
(C3 to C6) and 45 (C4 to C7), one through a room mix (C2 to C5, velocity
90), one on the upright, and the first demo and the nocturne. B is matched
to A on whole-file RMS by +0.26, +0.10, +1.63, −0.27, −0.35 and +0.88 dB.
By the project's standing rule B stands unless the owner says otherwise.

## 2026-11-11 — the open strings (2.3.0)

**The owner on 2.2.0.** No verdict on the `2026-11-11-even-scale` set came
back; the owner's next messages asked for natural key noises and a closer
calibration to the recordings. By the project's standing rule B (2.2.0)
stands.

**What 2.3.0 changes: the open strings answer through the iron frame.** The
last round found the open strings 25 dB too quiet under the pedal and 40 dB
too quiet at the top, and that the bridge was not the missing path. Two
things ship.

- *The frame's give.* A blow leans on the iron frame through the string's
  near end (the lean that already knocks the board). The frame gives, and
  with it the near end of every string whose damper is off, so each such
  string is driven at that end. The give is one damped resonance: 1.2e-7 m/N
  below 500 Hz, falling above it as the iron's mass holds it still. A string
  that only follows its end pulls on nothing, so that part is taken out and
  the bridge hears what the string rings beyond it.
- *Detuned unisons load the bridge once.* The open strings are one mode a
  unison. In tune, its three strings load the bridge three times; further
  apart than the bridge couples them, each rings alone and loads it once
  (Weinreich 1977, the faster decay of a coupled pair). Loaded three times
  the top strings died at 35 to 80 dB/s; they now die at 16 to 62 dB/s (27
  to 29 in the median) where the Salamander's take 8 to 35.

Both constants of the give are fitted, and the two recordings they are
fitted to disagree by a few dB. Against the Yamaha C3's pedal-down takes
(`Tools/benchmark_pedal_wash.py`, parlor grand) the bands that hold a note's
partials stood 25.6 dB short in the median on the fitted takes and 24.6 on
the others; they stand 5.6 and 7.9 dB short (3.0 dB in the first half
second, 10.0 after three seconds). Against the Salamander's forte notes
(layer 14), the median top string under a note struck from C5 to F♯7 rings
within 3.3 dB of the recording's (it was 40 dB under). A give of 1.5e-7
closed the first to 3.8 and 6.0 dB and put the second between 2 dB under
and 4 dB over; half the shipped give rings the strings 6 dB less. The
shipped value is between what each asks.

**Forms tried and not shipped, by measurement.** The ring scaled by each
key's voicing: the string-to-string spread did not fall. The frame as a
mobility (a velocity for a force): the wrong tilt across the pedal takes'
bands. The frame as a plain spring at every frequency: in the first half
second 6.4 dB short from 150 to 300 Hz and 16.5 dB over from 1.2 to
2.4 kHz. The damped resonance at 500 Hz fits the four octave bands from
150 Hz to 2.4 kHz within 3.5 dB in the first half second at a give of
1.5e-7 (−3.5, −1.5, −1.0 and +0.9 dB).

**What it leaves wrong.** Under the pedal, a key from about C♯4 up rings the
strings below its own pitch too much: the bands under the first partial
stand 8.2 dB over the takes in the median (12.9 on the takes not fitted),
where they stood 14.9 short on the fitted takes. Under A7 and C8 the top strings ring 7 to 10 dB
too much, and under C3 and C4 10 to 13 dB above what the recording holds
there, which is near its floor. The ring still dies about twice as fast as
recorded. The note itself still gains nothing under the pedal where the
takes gain 3 to 7 dB from C3 to A4, and after three seconds the wash is
10 to 12 dB short.

**What the benchmark says** (`Tools/benchmark_recordings.py`, 2.2.0 to
2.3.0). The grand against Salamander
([report](validation/grand-open-strings-benchmark-2026-11-11.md)), on the
notes 1.0.0 never fitted: first half second 8.86 to 8.08 dB, noise between
the partials 9.89 to 9.30 dB, sustain 9.11 to 8.73 dB, attack 8.07 to
7.82 dB, tuning 2.90 to 2.81 cents; partials 8.19 to 8.23 dB and the
channels' correlation 0.214 to 0.218 are further off; decay, envelope, rise
and level within 0.01. From C6 up: first half second 15.40 to 12.65 dB,
noise 15.14 to 13.10, sustain 13.74 to 12.40, attack 12.29 to 11.39. On the
fitted notes the same: first half second 9.39 to 8.71, noise 10.23 to 9.63,
sustain 10.09 to 9.66, attack 8.39 to 8.13, partials 8.94 to 8.98. Six
single-note scores are worse: the channels' correlation at C8 (0.26 to 0.37,
0.33 to 0.44 on the fitted layers), F♯7 (0.45 to 0.51, 0.47 to 0.52) and
D♯7 (0.36 to 0.40), and F♯2's noise (11.5 to 12.7 dB).

The upright against Helsinki
([report](validation/upright-open-strings-benchmark-2026-11-11.md)): on the
fitted notes attack 9.11 to 8.89 dB, first half second 11.20 to 10.86,
noise 11.74 to 11.41, tuning 4.08 to 4.02 cents; on the 21 notes 1.0.0 never
fitted attack 8.61 to 8.52, first half second 10.25 to 10.17, noise 11.42 to
11.23 and rise 12.95 to 12.84 ms are closer, and the partials (8.46 to
8.57 dB) and the decay (5.55 to 5.72 dB/s) further off. Two single-note
scores are worse: B3's decay (6.0 to 7.6 dB/s) and D3's noise (7.0 to
7.5 dB).

The benchmarks and the listening set were rendered before a fault was found
in the tests: a pitch bend four octaves down at 192 kHz divided by zero in
the term that takes out a string following its end. That term is now taken
from each mode as it turns. On three of the set's phrases the output moved
by −142 to −163 dB against a signal at −21 to −31 dB, so the numbers stand.

**What is the owner's to hear.** A lettered set went to the owner on
2026-11-11 (`2026-11-11-open-strings` in the project's files, not
committed): A 2.2.0, B 2.3.0, C 2.3.0 with half the frame's give, since the
recordings disagree on it. Eight phrases: treble staccato and a treble
melody without the pedal, chords, a treble arpeggio and bass notes under
the pedal on the concert grand, the chords on the upright, and the first
demo and the nocturne. B and C are matched to A on whole-file RMS; every
trim is within 0.03 dB. By the project's standing rule B stands unless the
owner says otherwise.

## 2026-11-11 — the key presses (2.4.0)

**The owner on 2.3.0.** No verdict on the `2026-11-11-open-strings` set came
back. The owner's next messages: "the key presses (noises) sound too
mechanical, ensure they are realistic, natural and vary naturally", then to
calibrate further against the training material, MAPS included, and to
"research, invent, reuse any algorithm or model necessary to make the piano
sound real". By the project's standing rule B (2.3.0) stands.

**What 2.4.0 changes.**

- *The action's noises vary.* A key landing or returning, a damper and the
  pedal were one sound each, repeated. The Salamander grand's key returns,
  each key's recorded once, stand 1.5 dB from their neighbours' in level and
  are 0.56 alike at the best lag: an upper bound on how two returns of one
  key differ. Each knock now draws its level (1 dB), each body mode its
  level and phase (2 dB, 1 radian), each band of the click its level (3 dB)
  and the click its rise (a factor of e^0.3). Two returns of C3, C4 or C6
  then differ by 1.4 to 1.9 dB and are 0.60 to 0.75 alike. The pedal's two
  recorded takes are 0.52 and 0.36 alike; the engine's stay more alike than
  that, 0.89 and 0.62. The draws are the engine's own, apart from the
  strikes' and the noise's, and a measurement (`steady`) draws none.
- *Two knocks under a note.* Read on the Salamander where the fundamental
  leaves room: from 180 Hz up, what a treble note holds under its
  fundamental reaches half its peak within 5 ms of the onset at every
  layer; from 60 to 180 Hz it reaches half 14.5 ms (hardest layers) to
  22 ms (softest) after the onset. 2.3.0 had one thump, with the blow, on
  every key. Now the thump is the action catching the hammer on its way
  back (14 ms and 11 mm at the hammer's own rebound speed after it leaves
  the string), handed to the board's edge by the keybed, and the knock is
  the blow's lean on the capo d'astro bar, from A5 up and above 180 Hz. The
  catch varies from strike to strike by 2 dB and a fifth of its time: over
  a Salamander key's sixteen layers the thump stands 2.6 to 2.7 dB off a
  line in the note's level, the model's 2.2 to 2.5.
- *The top octave.* Hammers above C5 harder by up to three quarters of a
  decade at C8, the bridge's full hold from A♯6 up, more loss in the top
  strings, and three times the sideways drive at the very top.
- *The room in the close pair*, 0.45 where it was 0.03.
- *The upright's thump* is caught at once (MAPS ENSTDkCl is a Disklavier,
  and its thump comes with the blow).

**What they are set against, and how close.** All Salamander unless said,
model against recording, each against its own piano's middle notes.

- Thump timing (when 60 to 180 Hz comes within 6 dB of its peak, median
  from D♯4 to C8, seven layers from the second to the sixteenth): recorded
  21.9, 23.2, 18.9, 15.0, 14.0, 14.5 and 14.6 ms; model 21.3, 19.6, 18.2,
  16.7, 15.6, 15.1 and 14.7. The first fit, with 10 ms in place of 14, was
  2.4 to 7.3 ms early and was corrected before the benchmarks.
- Thump level by key from C4 to C8 at layers 4, 9 and 14: medians −4 to
  0 dB from 60 to 110 Hz and −1 to +2 dB from 110 to 180 Hz; single keys up
  to 14 dB off.
- Knock from A6 to C8: +2 to +3 dB in the median from 350 to 700 Hz and +2
  to +4 from 700 to 1100 Hz, single keys within 8 dB. From C6 to F♯6 it is
  2 to 12 dB short.
- Top octave: the fundamentals of C7, F♯7 and C8 fall 30, 35 and 28 dB in
  their first 300 ms (recorded 21 to 28, 22 to 24 and 30 to 36; 2.3.0 15, 8
  and 14).
- Room: from 280 to 710 Hz a treble note stands 32, 47 and 69 dB under the
  knock's peak 150, 300 and 600 ms after it (recorded 24, 36 and 47; 2.3.0
  41, 67 and 88).
- Upright against MAPS ENSTDkCl, soft, medium and loud notes from C4 to B5
  and from C6 to C8: the bands from 60 to 110, 110 to 180 and above 180 Hz
  within 3.1 dB; the thump arrives 4 to 13 ms after the onset where the
  recorded one arrives −3 to 10.

**Forms tried and not shipped, by measurement.** The blow's knock on every
key, without the high-pass: 15 to 20 ms before a bass note the recording
holds 41 to 70 dB less than the note's low band from 400 to 1200 Hz, that
form 13 to 36, and the bass's rise moved from 23 to 30 ms. A catch that
hardens with speed: it fitted the bass and broke the treble's slope across
the layers. A static correction for the modes the strings do not keep:
right in principle, ±1 dB on the knock's bands, so left out. Hammers a
decade and a half harder at C8: the softest layer fitted and the others
came out up to 8 dB loud beside the middle of the keyboard. Five times the
reduced hold at the top: C8 gained energy.

**What it leaves wrong.** The thump rings for a shorter time than recorded
(its peak 20 to 27 ms after the onset, recorded 24 to 42). From C5 to A5 the
model holds something under 180 Hz with the blow that the recording does
not. The knock is short from C6 to F♯6. Beside the middle of the keyboard
the keys from F♯6 up are 5 to 13 dB quiet at the softest layer and up to
6 dB loud at the hardest, and the keys from C1 to F♯2 1 to 8 dB quiet, as
they were in 2.3.0. The upright's notes from C6 up stand 1 to 4 dB louder
beside its middle than MAPS's. The causes named for the two knocks (the
catch, the capo d'astro bar) are what their timing and their keys suggest;
no action was measured. The literature names the key meeting the key frame
for the thump, at the hammer's contact at mezzo-forte, 12 ms after it at a
piano touch and 3 ms before it at forte (Askenfelt and Jansson 1990, as
cited by Goebl 2001); that reading is not built or compared yet
([options](plans/realism-options-2026-11-11.md)).

**What the benchmark says** (`Tools/benchmark_recordings.py`, 2.3.0 to
2.4.0). The grand against Salamander
([report](validation/grand-key-presses-benchmark-2026-11-11.md)), on the
notes 1.0.0 never fitted: attack 7.82 to 6.60 dB, first half second 8.08 to
6.96, noise between the partials 9.30 to 7.83, sustain 8.73 to 8.39, rise
15.06 to 12.98 ms, level 2.52 to 2.39 dB, the channels' correlation 0.218
to 0.203; further off: tuning 2.81 to 3.20 cents, decay 3.67 to
4.15 dB/s, envelope 4.18 to 4.55 dB, the channels' level difference 5.60 to
5.66 dB; partials 8.23 to 8.23. By register on those notes: from C6 up
partials 8.96 to 7.51, attack 11.39 to 7.81, first half second 12.65 to
9.55, sustain 12.40 to 11.07, noise 13.10 to 8.95, and decay 5.33 to 7.04,
envelope 4.62 to 5.93 and tuning 3.30 to 3.66 further off; below C3
partials 8.59 to 9.66 and tuning 3.57 to 4.05 further off, rise 28.1 to
22.8 ms closer. On the fitted notes: partials 8.98 to 8.62, attack 8.13 to
7.08, first half second 8.71 to 7.70, noise 9.63 to 8.40, rise 17.3 to
15.2 ms; tuning 2.72 to 2.81, decay 4.72 to 4.84 and envelope 4.23 to 4.40
further off. 106 single-note scores are worse, where 2.3.0 had six; the
furthest are F♯3's rise (41.0 to 50.9 ms fitted, 40.4 to 49.7 not), C8's
decay (7.8 to 15.4 dB/s; 5.4 to 12.0 fitted) and sustain (18.8 to 22.4 dB),
A3's noise (7.4 to 10.6 dB), C7's envelope (3.8 to 7.0 dB) and A7's sustain
(11.0 to 14.1 dB). The report lists every one.

With the room share back at 0.03 and all else the same, an earlier build of
this candidate scored the fitted bass's partials 8.93 dB where it scored
9.81 with 0.45, and its tuning 3.12 cents against 3.45: the room in the
close pair is what moves the bass's partials further off.

The upright against Helsinki
([report](validation/upright-key-presses-benchmark-2026-11-11.md)): on the
fitted notes attack 8.89 to 7.58 dB, first half second 10.86 to 9.70,
sustain 11.32 to 10.88, noise 11.41 to 10.23, envelope 4.42 to 4.17, rise
16.6 to 15.5 ms; tuning 4.02 to 4.25 cents and level 4.29 to 4.36 dB
further off. On the 21 notes 1.0.0 never fitted: attack 8.52 to 7.50, first
half second 10.17 to 9.12, noise 11.23 to 9.80, tuning 4.55 to 4.32, decay
5.72 to 5.51; partials 8.57 to 9.57 dB, rise 12.8 to 13.1 ms, level 2.85 to
3.04 dB and the channels' level difference 5.10 to 5.24 dB further off. 39
single-note scores are worse, the furthest D♯1's rise (37.9 to 50.2 ms),
E7's decay (3.6 to 11.6 dB/s), E6's partials (8.2 to 11.8 dB) and G♯6's
tuning (3.2 to 6.6 cents).

**Two test fixtures.** The block-size check now plays a top key too, and
found that a finished catch was put to rest when a render call ended, which
the host's blocks decide; it is put to rest at the model's own 32-sample
boundary. "All notes off leaves the pedal down" compared a note let go under
the pedal with the same note kept down, within 1 dB; the pedal holds the
dampers a little less clear than a key does (the owner's choice of
2026-10-30), which takes 0.99 dB in 2.3.0 and 1.00 dB now. It now compares
with the key let go under the pedal, within 0.1 dB, and reads 0.00.

**What is the owner's to hear.** A lettered set went to the owner on
2026-11-11 (`2026-11-11-key-presses` in the project's files, not
committed): A 2.3.0, B 2.4.0, C 2.4.0 with 2.3.0's room share in the close
pair, since the room brings the treble's tail closer and the bass's
partials further off. Eight phrases: one key pressed sixteen times, a soft
treble melody, soft bass notes, chords, treble staccato, the chords on the
upright, and the first demo and the nocturne. B and C are matched to A on
whole-file RMS; the trims are within 0.2 dB except the soft treble melody
(−1.4 and −1.6 dB) and the treble staccato (−0.6 and −0.7 dB). By the
project's standing rule B stands unless the owner says otherwise.

**The owner's verdict, 2026-11-11.** "B is ok - continue, iterate until the
piano sounds absolutely real." B (2.4.0) stands, chosen by ear on the
`2026-11-11-key-presses` set; C (without the room in the close pair) was
not taken up, so the close pair keeps its share of the room. The next
rounds follow [the ranked options](plans/realism-options-2026-11-11.md).

## 2026-11-11 — the string scale (2.5.0)

**What was looked for.** Why the partials' score had stood at 8.2 dB since
2.0.0. Each partial's signed error on every scored note of the Salamander
(the benchmark's own measure, taken apart): 7 % of the scored partials were
ones the search did not find in the render at all, each counted as 30 dB,
nearly all from the fifteenth partial up. They were there, at other pitches.

**The cause.** The inharmonicity the recordings' partials give, beside the
model's: the concert grand's plain strings were 1.1 to 1.5 times as stiff as
the Salamander's from C3 up and twice at F♯2 and A2, the upright's up to
twice the Helsinki's, and both pianos' wound strings 0.4 to 0.85 of the
recorded ones. The lengths the Salamander's stiffness implies, at the
model's wire, follow the scale's own rule (doubling 0.93 of an octave) all
the way down to the break at 1.035 of it, with no bend; the Helsinki's bend
only in the last half octave above its break. The model bent every string
from the bass up.

**What 2.5.0 changes.** C8 at 51.5 mm; the plain strings keep the rule down
to 0.87 of A0's length; the wound strings run from the lowest plain
string's length to A0's; their cores 1.035 to 1.555 mm and tensions 1000 to
1300 N. The 0.87, the cores and the tensions were fitted to the two pianos'
inharmonicity with the recorded pianos' own sizes left free; the rule's
form is the model's. The concert grand then stands within 8 % of the
Salamander from C3 to F♯6, 15 to 19 % over at F♯2 and A2 (plain in the
model, wound in the Salamander), and 14 to 53 % under in the wound strings:
the Salamander is a 2 m grand, and the parlor grand's A0 is within 3 % of
it. The upright's plain strings stand 22 % under to 38 % over the
Helsinki's, its wound strings 6 to 41 % under. Keys re-voiced, levels
re-pinned (0.1 to 0.3 dB).

**Measured.** Grand, the notes 1.0.0 never fitted, 2.4.0 to 2.5.0: partials
8.23 to 7.91 dB, tuning 3.20 to 2.10 cents, decay 4.15 to 4.17 dB/s, attack
6.60 to 6.56, early 6.96 to 6.98, sustain 8.39 to 8.35, noise 7.83 to 7.64,
envelope 4.55 to 4.55, rise 12.98 to 12.15 ms, level 2.42 to 2.50. Upright:
partials 9.57 to 8.42, tuning 4.32 to 3.17, decay 5.51 to 5.33, attack 7.50
to 7.56, early 9.12 to 9.27, noise 9.80 to 9.65. 13 single-note scores of
the grand are worse (the furthest F♯7's decay, 4.3 to 9.6 dB/s, and F♯6's
tuning, 1.7 to 3.5 cents) and 11 of the upright
(C1's rise 6.5 to 21.6 ms, F♯5's tuning 1.2 to 4.3 cents).

**Tried and dropped.** On the new scale, two searches against the
Salamander at four layers. The felt by register (exponent, stiffness,
hysteresis) brought the partials' levels averaged by register, band and
layer from 4.3 to 3.6 dB off, stopping at the edge of what it was allowed
(exponent +0.6, a factor 2 on the hysteresis), and on the benchmark took
0.2 dB off the partials while the noise between them went 1.2 dB further
off for the exponent and stiffness and 1.5 more for the hysteresis. The
strings' losses and the bridge's hold by register brought how the partials
fall after their first 200 ms from 3.5 to 3.1 dB off, and on the benchmark
took 0.3 dB off the partials, sustain and envelope while the decay went 0.3
to 0.5 dB/s and the level 0.5 dB further off. Neither is in 2.5.0. A search
on one measure moves the others; the next fit of the felt has to score the
noise between the partials with them.

**Also measured, not acted on.** The strike point: the Salamander's bass
notes fit a strike at 0.117 to 0.123 of the length (the model's 0.12), with
the eighth partial 14 dB under its neighbours where the model's is 6 to 9,
and the twenty-fifth 9 under where the model's, an exact node, is 26.
Whether the model's partials within a note are rougher than a real
piano's: through the close pair a partial stands 6 to 7 dB from its
neighbours, the same notes averaged over all four pairs 4 to 5 under 2 kHz,
so about half of it is common to every microphone.

**What is the owner's to hear.** A lettered set (`2026-11-11-string-scale`
in the project's files, not committed): A 2.4.0, B 2.5.0. Eight phrases:
long forte notes from C2 to C5, held octaves and fifths, wide chords, a
loud bass line, the chords on the upright, the octaves on the parlor grand,
and the first demo and the nocturne. B is matched to A on whole-file RMS;
the trims are within 0.25 dB. By the project's standing rule B stands
unless the owner says otherwise.

## 2026-11-11 — what rings under a treble note (2.6.0)

**What was looked for.** What stands between a note's partials, each sound
with its own stiff string's partials left out, on the Salamander at four
layers. The model held less than the recording nearly everywhere (4.4 dB
on average, signed), most from A5 up: 7 to 17 dB less from 125 Hz to 2 kHz
from 50 ms after the blow. From A4 to G♯5 it held 5 to 13 dB more in the
first 50 ms, and from A4 up a loud note 10 to 40 dB less above 5 kHz.

**The benchmark corrected.** Its noise score left out of a render only the
partials matched to the recording's, so a render's partial standing off
the recording's was scored twice, as missing and as noise. At the orders
the recording holds, the render's own partials are now left out too
(orders above them stay in for both: left out for the render alone, the
bass's bands kept only what the recording never resolved, and its noise
read 28 dB). 2.5.0 reads 7.45 dB by it where it read 7.64, the upright
9.54 where 9.65. The reports of 2.6.0 compare both versions by the
corrected score.

**The felt, again.** With the corrected score the felt refit dropped from
2.5.0 (exponent +0.6, stiffness by register) still took 0.1 dB off the
partials at four layers and put the noise 0.7 to 1.1 dB further off. By
third octaves the middle register is not short of top end as a whole: it
holds 4 to 9 dB less at 1.6 kHz and 4 to 9 dB more from 2 to 5 kHz half a
second on. A harder felt is not the remedy; not in 2.6.0.

**A correction to 2.4.0.** The close pair's share of the room was set
against what the Salamander's treble notes leave from 280 to 710 Hz, 24, 36
and 47 dB down at 150, 300 and 600 ms. From 400 ms on that recording stands
at its own floor (51 dB under the knock's peak from one second to four), so
the 600 ms figure was not the piano. The first two stand.

**What rang in the recording.** Valid to 300 ms, the recorded tail falls
15 dB in 200 ms from 100 ms on, as a space ringing 0.8 s does, from 13 dB
under the knock's peak. Three readings were built. The board at half its
loss rings as long (16, 28 and 39 dB down at 100, 200 and 300 ms against
the recording's 21, 28 and 36) and brings the treble's first half second
2.3 dB closer, but the bass and the middle then take twice as long to
reach their level (the benchmark's rise, 14 to 26 ms), and halving the
loss only above 250 to 600 Hz kept most of that cost for a seventh of the
gain. More room for everything: at the Room control's top the tail is
still 3 to 5 dB short. The case's own sound in the room: the pairs hear
the board from near it, and what the knock shakes in the frame and the
case reaches them mostly by the room.

**What 2.6.0 changes.** The knock the blow gives the board's edge (keys
from A5 up, 2.4.0) also goes to the room, 0.6 of it, in other signs than
the board's sound. From 280 to 710 Hz the tail stands 15, 21, 29, 29 and
39 dB down at 60, 100, 150, 200 and 300 ms (recorded 15, 21, 24, 28, 36;
2.5.0 19, 28, 32, 38, 47), and from 180 to 280 Hz 11, 16, 21, 27 and 34
(recorded 14, 19, 22, 27, 34). Between the partials the notes from A6 to
G♯7 now stand within 6 dB of the recording from 250 Hz to 1.6 kHz; from A5
to G♯6, where the knock itself is weak, 4 to 11 dB short. Nothing a key's
strings give the microphones moved: the voicing table is byte for byte
2.5.0's and the levels hold at −9 VU without a re-pin.

**Tried on the way.** The caught hammer's thump in the room as well, at
0.4: the treble's first half second another 0.4 to 0.6 dB closer, the
bass's partials 0.2 to 0.3 dB and its noise 0.4 to 0.6 dB further off, and from 60 to
110 Hz the thump's tail already stands within 2 dB of the recorded one to
200 ms without it; left out. The knock in the room in the same signs as
the room's output: the top keys' two channels came out 0.04 to 0.28 more
alike than the recording's; fed in other signs they are as far apart as in
2.5.0.

**Measured.** Grand, the notes 1.0.0 never fitted, 2.5.0 to 2.6.0: attack
6.56 to 6.39 dB, early 6.98 to 6.49, noise 7.45 to 7.00, partials 7.91 to
7.90, tuning 2.10 to 2.10, decay 4.17 to 4.16, sustain 8.35 to 8.33, rise
12.15 to 12.16 ms, level 2.50 to 2.49; from C6 up attack 7.75 to 7.15,
early 9.58 to 7.86, noise 9.05 to 7.53. Two single-note scores are worse:
C8's level difference between the channels, 1.2 to 1.9 dB and 1.2 to 1.7.
Upright against the Helsinki: attack 7.56 to 7.42, early 9.27 to 8.95,
noise 9.54 to 9.22, partials 8.42 to 8.55, tuning 3.17 to 3.09; one
single-note score worse (E6's partials, 10.5 to 11.0 dB). A drier recording
of an upright (MAPS, ENSTDkCl) held less from 150 ms on than the model did
with the knock and the thump in the room at 0.4 (25, 26 and 36 dB down at
150, 200 and 300 ms against its 29, 35 and 44); the shipped form was not
measured against it.

**What is the owner's to hear.** A lettered set (`2026-11-11-case-ring` in
the project's files, not committed): A 2.5.0, B 2.6.0. Seven phrases:
single notes from C6 to C8 soft then loud, the same keys staccato, a
melody in the top two octaves over a held chord, the melody on the
upright, the single notes on the parlor grand, and the first demo and the
nocturne. B is matched to A on whole-file RMS; the trims are within
0.01 dB. Keys below A5 are the same in both. By the project's standing
rule B stands unless the owner says otherwise.

## 2026-11-12 — a denser room, and a bridge with length (2.7.0)

**What the owner said.** Of 2.6.0's short demo: "sounds good. maybe too
"springy" and cheap". Then: research, reuse or invent what makes the piano
sound real, and keep on until the benchmark against the recordings is good.

**The room.** 2.6.0's eight lines under a Householder reflection took
310 ms to grow dense (normalized echo density 0.9, measured on a copy of
the network) and their spectrum from 200 Hz to 2 kHz stood 8.9 dB about its
mean where a diffuse field's stands 5.6; since 2.6.0 the case's knock goes
straight into them. Sixteen lines under a Hadamard mix take 180 ms and
stand 5.9 dB; behind three allpass sections 130 ms. With every feed through
the allpass sections the upright's bass partials stood 0.4 dB further from
the Helsinki's (11.13 against 10.73 dB), so only the knock goes through
them. The room's level is kept (sixteen lines give an impulse back 1.4 dB
louder, so 0.85 of them). Under a treble note the knock's tail from 280 to
710 Hz now stands 15, 19, 24, 27 and 37 dB under its peak at 60, 100, 150,
200 and 300 ms, where the Salamander's stands 15, 21, 24, 28 and 36 and
2.6.0's stood 15, 21, 29, 29 and 39.

**The bridge.** Partial by partial against the Salamander, single keys
stood far from their neighbours: C5's partials 2 to 4 were 10 to 15 dB
over, C6's 2 to 6 were 16 to 22 dB under. Each key drove the board at one
point, so its partials stood as the board's modes fell under that point.
A plain string's force now reaches each mode as the mean of the mode's
shape along half the bridge's bending wavelength at that frequency. On
four layers, unvoiced, half that length and twice it did less for the
partials than the length itself (7.35 and 7.17 against 7.17 dB, with a
worse level and rise at twice); voiced again, the length itself brought the
unfitted notes' partials from 7.51 to 7.25. The wound strings' short bridge
stays a point: spread along its own length the upright's bass partials
stood 0.3 dB further off. The bridge's admittance is taken the same way as
its drive; with the admittance left at a point the grand's treble partials
stood 0.7 dB further from the recording (7.88 against 7.20).

**What followed from it.** Every key voiced again; the furthest unvoiced
key now stands 14 dB under the even scale, so a key may be pulled 15 dB
(12 before). A chord let go under the full pedal rang longer (58 dB down
after 12 s where it stood 64 down), past what the owner chose on
2026-10-30, so the pedal stops at 0.695 of its travel instead of 0.7:
60 dB in 11.1 s on the concert grand and 9.2 s on the upright, where
2.6.0 took 10.7 and 10.2 by the same measure. The engine test of a
re-pedalled note had its limit 0.1 dB from the grazing pedal's own decay;
it is 4 dB now, with the reason beside it.

**Measured.** Grand, the notes 1.0.0 never fitted, 2.6.0 to 2.7.0: partials
7.90 to 7.86 dB (bass 9.50 to 9.85, middle 7.11 to 7.01, treble 7.52 to
7.20), tuning 2.10 to 2.10, decay 4.16 to 4.23, attack 6.39 to 6.28, early
6.49 to 6.27, sustain 8.33 to 8.24, noise 7.00 to 6.75, level between the
channels 5.67 to 5.30, envelope 4.54 to 4.35, rise 12.16 to 12.65 ms, level
2.49 to 2.11. On the fitted notes the partials went 8.03 to 8.11 (bass 8.78
to 9.17, treble 7.84 to 8.06). 71 single-note scores are worse. Upright
against the Helsinki, unfitted notes: partials 8.55 to 8.06 (five treble
notes carry it, 10.98 to 7.43; fitted notes 8.03 to 7.92, their bass 10.36
to 10.75), tuning 3.09 to 3.63, decay 5.33 to 5.36, attack 7.42 to 7.54,
early 8.95 to 8.77, sustain 10.42 to 10.61, noise 9.22 to 8.91, level
between the channels 5.07 to 5.65, rise 12.77 to 13.07, level 3.03 to
3.16; 29 single-note scores worse. The bass's partials are further off on
both pianos with the wound strings' bridge unchanged; what in the new room
or the new voicing costs them is not found.

**What is the owner's to hear.** A lettered set (`2026-11-12-room-and-bridge`
in the project's files, not committed): A 2.6.0, B 2.7.0. Five phrases:
short loud middle notes, the top keys staccato, the white keys from C4 to
C6 and back at one touch, the first demo, and a treble melody on the
upright. B is matched to A on whole-file RMS (trims +0.61, +1.39, +0.37,
+0.02 and +0.89 dB). By the project's standing rule B stands unless the
owner says otherwise.

## 2026-11-12 — how a grand's upper notes die away (2.8.0)

**What was looked for.** The largest scores left: the treble's sustain
(10.6 dB on the unfitted notes) and its decay (7.5 dB/s). By third octaves
the recording seemed to hold 26 to 39 dB more than the model from 100 to
160 Hz half a second after a treble note; those are steady lines at 100.0
and 144.5 Hz in every take (mains hum, level from 0.1 to 3.6 s), in a few
frames of each note, and not the piano. A room ringing longer in the bass
was tried against them and dropped. What the score does hold: from C5 up
the model's first partial stood 7 to 8 dB over the recorded one 1 to 1.5 s
after the blow.

**What holds it up.** Halving the sideways motion's share of the blow (the
aftersound) took 1.5 dB off that and put the decay score further off. The
unisons' spread decides it: at Detune 0.15 the first partial stood within
3 dB of the recorded one to 3 s, at the default 0.3 7 to 8 over, at 0.6 8
over. From C3 to B4 the spread made no such difference.

**The change.** On a grand the spread is whole up to B3 and narrows as
250/f to half from C5 up. On four layers, unfitted notes: decay 3.89 to
3.36 dB/s, sustain 7.73 to 7.41, partials 7.27 to 7.27; narrowed on to 0.3
or all the way, decay 3.52 and 3.36 with the top octaves' sustain 0.8 dB
further off (10.0 against 9.2). On the upright the same narrowing put the
fitted notes' decay from 4.54 to 4.95 dB/s and their envelope from 4.27
to 4.54 (unfitted: decay 5.36 to 4.59, sustain 10.61 to 10.33), so the
upright keeps the whole spread and is 2.7.0's sample for sample: the
Helsinki upright's unisons stand wider than a studio grand's.

**Measured.** Grand, the notes 1.0.0 never fitted, 2.7.0 to 2.8.0: decay
4.23 to 3.80 dB/s (from C6 up 7.53 to 5.80), sustain 8.24 to 7.85 dB,
envelope 4.35 to 4.18, partials 7.86 to 7.74, tuning 2.10 to 2.21 cents,
attack 6.28 to 6.26, early 6.27 to 6.29, noise 6.75 to 6.78, level 2.11 to
2.07. On the fitted notes decay 5.07 to 4.50, sustain 9.01 to 8.80, and
from C6 up the envelope 4.39 to 4.94 and the partials 8.06 to 8.27 further
off. 23 single-note scores are worse.

**What is the owner's to hear.** A lettered set (`2026-11-12-unison-spread`
in the project's files, not committed): A 2.7.0, B 2.8.0, on the concert
grand: held notes from C4 to C7, slow chords, a treble melody over a held
chord and the first demo. B is matched to A on whole-file RMS; the trims
are in its key. By the project's standing rule B stands unless the owner
says otherwise.

## 2026-11-12 — a Studio Grand, and the pedal's whisper (2.9.0)

**Asked.** The owner chose to add a fifth piano, a 2.0 m studio grand the
size of the recorded Yamaha, and asked for audible phenomena the model
lacks, those that cost little CPU first.

**The Studio Grand.** The concert grand's wound strings are 14 to 53 %
less stiff than the Salamander's, a grand 0.7 m shorter. A scan of the bass
length and the first plain-steel key against the recordings' inharmonicity
at eleven notes below C4 (one layer) stood, as the rms of log2 of the
ratio, at 0.38 for 1.55 m, 0.34 for 1.60 m, 0.32 for 1.65 m and 0.30 for
1.75 m, with plain steel from B2. 1.60 m is kept: a length a 2.0 m case
holds, where 1.75 m would be fitted past the instrument. The board, bridge,
hammers and case are typical of the size, between the concert and the
parlor grand. It is appended as the last Piano so that saved sessions keep
their piano; the Studio Grand preset moved to it from the parlor grand.

**Measured.** Against the Salamander, the notes 1.0.0 never fitted, the
Concert Grand of 2.8.0 to the Studio Grand: partials 7.74 to 7.73 dB (bass
9.84 to 9.73, middle 6.65 to 7.02, treble 7.34 to 6.82), tuning 2.21 to
2.02 cents, decay 3.80 to 3.69 dB/s, envelope 4.18 to 3.94 dB, level 2.07
to 2.06; attack 6.26 to 6.78, early 6.29 to 7.06, sustain 7.85 to 8.78,
noise 6.78 to 7.01, stereo balance 5.31 to 6.08 and rise 12.65 to 19.66 ms
(the bass 22 to 37) further off; 221 single-note scores worse. The size
alone does not bring the model nearer the recording, so the benchmark's
default piano stays the Concert Grand.

**The pedal's whisper.** The Salamander's pedal-down takes ring for more
than five seconds after the knock, on the strings; the model was silent
after one. Each damper now plucks its strings by a hair as it leaves them
(`whisper()` in `PianoModel.cpp`, where the fit is written). An impulse on
the bridge with the pedal, tried for the takes' low ring, left no ring on
the open strings and is not kept. The whisper's level was first read
against the library's notes, on the assumption that its pedal takes share
their gain: that stood 18 dB higher and 30 dB over the engine's knock at
the default Mechanics. It is set beside the engine's knock instead, which
is the project's standing reading of the same takes.

**Tried and left out.** The radiation's corner at 10 kHz for 6: on four
layers the partials moved by 0.13 dB at most either way, the bass's noise
on the fitted notes from 6.44 to 7.42 and the middle's on the others from
8.32 to 7.80. On the Studio Grand the notes A4, D♯5, A5 and A6 hold 2 to
9 dB less from 5 to 10 kHz than the recordings 10 to 30 ms after the
onset, D♯6 22 to 25, at a middle and a loud layer alike, so the shortfall
is not the felt's stiffening.

**What is the owner's to hear.** A lettered set (`2026-11-12-pedal-whisper`
in the project's files, not committed): A 2.8.0, B 2.9.0, on the concert
grand: the pedal alone (not level-matched, the whisper's level being what
is judged), soft chords with legato pedalling and staccato notes with the
pedal between them (B matched to A on whole-file RMS; the trims, under
0.02 dB, are in its key). Beside it, unlettered, the first demo's phrase
on the Concert and the Studio Grand. By the project's standing rule B
stands unless the owner says otherwise.

## 2026-11-12 — a heavier bass, from the board beside its modes (2.10.0)

**Asked.** The owner asked whether the model sounds rich enough, "heavy,
expensive wood", and whether material, weight and timing could move one
piano toward another: a grand toward an upright, one maker toward another.

**What was missing.** Against three reference grands (a commercial modelled
piano's American, German and Japanese grands at velocity 80, the owner's
renders), partial by partial from 50 to 350 ms, the concert grand's
partials from 56 to 80 Hz stood 9.5 dB under their median and from 112 to
160 Hz 3.7 dB under; the upright's bass 14 to 17 dB under. The smeared
plate has few modes there, and between two of them a partial died as fast
as its neighbours but reached the air a tenth as strong: a ribbed board
under its bridge takes more from the strings at those frequencies than the
plate's lowest modes do.

**The first candidate, rejected.** A softer board, 1.0e3 kg/s, under half a
measured board's impedance, brought the partials nearer (7.74 to 7.15 dB on
the notes 1.0.0 never fitted) but put the tuning 0.4 cents and the decay
0.2 dB/s further off and 129 single-note scores; whole notes from A1 to A3
died too fast (C3 at 12.3 dB/s; the Salamander's 7.1, the reference
grands' 6.5 to 8.2). Weighing each partial by what the board leaves out of
it was not causal: C1 sounded at -23.5 dB re the note in its first 4 ms,
before its string's wave had reached the bridge (`Keyra.PianoModel` holds
that under -50).

**Chosen.** 2.9.0's board (about 2.5e3 kg/s); 2.0, 2.5 and 3.2e3 kg/s
scored within 0.2 dB of one another on the partials of the fitted notes.
2.9.0's hold on each key's pull, a curve fitted to the Salamander's decay,
is gone: the strings meet the board through the bridge, a maple beam whose
own impedance stands in series, assumed to narrow from C5 to 0.47 of its
impedance at C8, over a board evened to 0.7 to 1.5 times an endless
plate's. What the plate's modes leave out radiates beside them, from the
bridge force through one causal filter per piano, from the board's lowest
mode to where it falls past half (50 to 508 Hz on the concert grand, 101
to 604 on the baby grand), into the direct, floor and lid taps. The
strings' sideways motion was set again against the reference grands'
fundamentals (3.9 dB from their median from A0 to B6, 2.9.0 4.1). The
bridge's pull on a partial now acts with the partial's turn in each step,
as the string's own loss does: taken before it, the pull met the string a
step late, and where a step is a quarter of the partial's period or more
the bridge's springiness came out as a gain. On four layers, voicing not
rewritten:

- the sound beside the modes, against none: on the notes 1.0.0 never
  fitted the partials 7.19 to 7.01 dB, the attack 6.52 to 6.32, the first
  half second 6.24 to 5.76, the sustain 7.42 to 7.13; on the fitted notes
  the rise 15.63 to 12.56 ms;
- no beam: the fitted notes' partials 8.86 dB and 207 single-note scores
  worse;
- no narrowing: the fitted treble's attack 7.91 against 7.61 dB and its
  level 3.35 against 2.87;
- the modes levelled to their own response, rising to the treble, instead
  of flat: the unfitted notes' attack 6.32 to 7.12 dB (halfway, 6.75);
- the ribs' stiffness above their spacing, in an earlier candidate:
  without it the unfitted notes' decay 3.64 to 3.14 and 2.99 dB/s on two
  readings;
- each key tuned by its first six partials instead of its first: the
  tuning 0.08 cents further off.

**The microphone pairs.** The sound beside the modes adds 0.2 dB to the
concert grand's close pair and up to 1.3 dB to the others, which took the
distant pair 2.6 dB over the close one in `Keyra.Engine`'s chord. An
estimate made when the piano is designed did not agree with the renders
(the close pair +0.95 dB computed, +0.15 measured), so `KeyraLevels` now
sets each pair's scale at the close pair's level without the room, on
average over the keys. One key then needed 14.1 dB (the Studio Grand's G♯3
in one mix) and the voicing's limit went from 12 to 15 dB; it is the
engine's limit, not a test tolerance.

**Makers.** Each piano's description now holds its board's mass and two
bending stiffnesses, its bridge's mass and narrowing, and its strike point,
beside the hammers, the scale and the case it held already. The five share
one board, bridge and strike point: no measurement in hand says how one
maker's board differs from another's, and the recordings are of one grand
and one upright.

**Measured** (`Docs/validation/grand-board-beside-benchmark-2026-11-12.md`,
`upright-board-beside-benchmark-2026-11-12.md`): see the 2.10.0 entry of
the README. Further off: the grand's level by register (the top octave
about 3.2 dB louder beside the middle than the recording's), the onset of
A0 to C2 by up to 60 ms at some layers, the upright's stereo balance by
0.5 to 0.6 dB; 108 and 72 single-note scores. Middle C and C5 now die at
5.6 and 6.0 dB/s from 0.4 to 2.6 s (2.9.0 6.2 and 7.2; the Salamander 9.2
and 10.5, the reference grands 6.2 to 8.6 and 7.7 to 9.1).

**What is the owner's to hear.** A lettered set (`2026-11-12-board-beside`
in the project's files, not committed): A 2.9.0, B 2.10.0, the concert
grand through the close pair: low chords, bass notes alone and left-hand
octaves under soft chords around middle C. B is matched to A on whole-file
RMS; the trims, -0.63 to -0.92 dB, are in its key. By the project's
standing rule B stands unless the owner says otherwise.

## 2026-11-12 — bass strings that beat each their own way (2.11.0)

**Asked.** The owner heard held bass chords sound "phaser like" and asked
whether the strings vibrate too much alike from note to note, and whether
something in their dispersion should vary more.

**What was found.** Within a key, yes. 2.10.0 drew a small stray from the
stiff-string series once for each key, about 0.3 cents, and shared it
between the key's strings: the strings of a unison stood one ratio apart at
every partial, so each partial beat at a rate in proportion to its
frequency, and the partials' beats swept together like a flanger. Measured
with `Tools/measure_partial_stray.py` (its protocol at its head; every
third key from A0 to B2, layers 8 and 13), the Salamander's bass partials
stray 1.54 cents (median) from their best stiff-string fit, 2.10.0's 0.40;
from C3 to B4 0.59 against 0.27. Per note the recording's stray is about
3 cents from A0 to D♯1, its single strings, and 1.0 to 1.9 from F♯1 to
D♯2.

**Chosen.** Each wound string's partials stray on their own, 1.5 cents for
one standard deviation from the second partial up, drawn when the piano is
designed; the plain strings keep the shared stray. 1.5 cents is set
against the Salamander's 1.54 from A0 to B2. The renders now stray 1.31
cents there, 1.25 to 1.55 note by note. On the partials within 20 dB of the
strongest, how far each one's beat rate lies off the line through its
neighbours' (over the median rate), median over the notes: 0.12 in 2.10.0,
0.25 in 2.11.0, 0.20 in the Salamander; how deep they swing about their
decay, 1.4, 2.7 and 2.0 dB. Over every partial kept: 0.04, 0.11 and 0.28;
3.9, 4.8 and 3.5 dB.

**A smaller stray, left out.** On a probe build with the same change, 1.5,
1.0 and 0.75 cents swing the strong partials 2.47, 2.44 and 2.27 dB: how
deep they swing is not the stray's size, and a smaller stray would only
leave the recording's measured stray further off.

**Tests.** `Keyra.PianoModel` held every key's partials within 3 cents of
the stiff-string law; C2 now strays 3.9 at worst by design, and the test
holds C2's partials within 3 cents rms, twice the design's deviation, and
the plain strings' to the law as before. Its check that nothing precedes a bass string read C1 at
-49.98 dB under the note in its first 4 ms against a limit of -50: no
knock reaches C1 (`knockArm` is nil below `capoFrom`), and what those
4 ms hold is the strings' own modes summed before their wave reaches the
bridge, -50.4 in 2.10.0 and -51.7 under another draw of the stray. The
limit is now -48 with that reason beside it; a knock stands tens of dB
higher.

**Measured** (`Docs/validation/grand-wound-stray-benchmark-2026-11-12.md`,
`upright-wound-stray-benchmark-2026-11-12.md`): see the 2.11.0 entry of the
README. Further off: the grand's bass envelope (3.26 to 3.62 dB on the
notes 1.0.0 fitted, 2.78 to 3.04 on the others), its beats now landing
where the recording's do not; 12 single-note scores at C1, A1 and C2 and 6
of the upright's at A1, A2 and C3. C1's rise on the notes 1.0.0 never
fitted, 4.1 to 12.0 ms, is the largest.

**What is the owner's to hear.** A lettered set (`2026-11-12-bass-phaser`
in the project's files, not committed): A 2.10.0, B 2.11.0, the concert
grand through the close pair: two low chords held with the pedal, four low
chords, bass notes alone, and left-hand octaves under soft chords around
middle C. B is matched to A on whole-file RMS; the trims, -0.02 to
-0.33 dB, are in its key. By the project's standing rule B stands unless
the owner says otherwise.

## 2026-11-13 — the image a spaced pair hears (2.12.0)

**Asked.** The owner asked for the pianos to be improved as whole
instruments against the recordings: how the piano works, the room and what
the microphones hear, with the recordings as benchmarks of the model and no
note fitted (`Docs/plans/whole-model-realism-2026-11-13.md`). The image was
that plan's first step: the close pair's two channels were more alike than
the recorded pair's above 250 Hz and less alike below it.

**What was found.** The model's board is one smeared plate and its modes
are exact: every second one is odd across the board's middle, so two
microphones either side of the middle hear it exactly out of phase, the
lowest modes too. Left as they fall, the close pair's channels are about
-0.6 alike from 88 to 354 Hz. The hold from 2.1.0 to 2.11.0 turned any mode
further than 70 to 90 degrees out of step back to that angle and left the
others as they fell, half of them in step. Over 150 notes
(`Tools/measure_pair_image.py`, its protocol at its head: 30 pitches from
A0 to C8 at five layers, 0.05 to 0.85 s of each) that gave 0.57, 0.30, 0.27
and 0.17 alike in the octaves at 125, 250, 500 and 1000 Hz, where the
Salamander's two channels are 0.79, -0.17, 0.05 and 0.08, each within
0.04: too loose in the bass and too tight above it. No place for a spaced
pair avoids the odd modes, and a real board, ribbed, bridged and shaped
like a wing, has none that are exact.

**Chosen.** Each microphone keeps the level it hears of each mode, and the
angle between a pair's two microphones is set, mode by mode, to the one
whose cosine the sound field at a pair gives in the mean. For the board's
own sound that is sin(kr)/(kr), r the most that the two paths from one
point of the board can differ: the cosine of the path difference averaged
over a source as wide as the board looks from the pair (the van
Cittert-Zernike theorem). For the room's share it is sin(kd)/(kd) across
the spacing d (Cook and others, JASA 27, 1955), times what the two
patterns share of a diffuse field, (3 + the cosine of the angle between
them) / 4 for cardioids. The two are weighed by how much of each the pair
hears of that mode. A mode keeps the side its own phase fell on; half a
turn is a change of sign, and what is left, a quarter turn at most, is
shared evenly between the two microphones. The pair's level is set after
the turning. The law has no constant: nothing in it is fitted, and the
Salamander's figures stand beside it as a check.

Over the same 150 notes, 2.12.0 beside the recording and 2.11.0, by
octave and over everything above 20 Hz:

| | 125 Hz | 250 Hz | 500 Hz | 1 kHz | 2 kHz | whole |
| --- | --- | --- | --- | --- | --- | --- |
| Salamander | 0.79 | -0.17 | 0.05 | 0.08 | 0.01 | 0.22 |
| Close, 2.12.0 | 0.78 | 0.01 | -0.05 | 0.08 | 0.04 | 0.15 |
| Close, 2.11.0 | 0.57 | 0.30 | 0.27 | 0.17 | 0.30 | 0.40 |
| XY, 2.12.0 | 0.91 | 0.58 | 0.46 | 0.45 | 0.69 | 0.76 |
| XY, 2.11.0 | 0.85 | 0.49 | 0.35 | 0.29 | 0.61 | 0.65 |
| Live, 2.12.0 | 0.54 | 0.14 | 0.10 | 0.06 | 0.11 | 0.33 |
| Live, 2.11.0 | 0.49 | 0.31 | 0.10 | 0.15 | 0.21 | 0.34 |
| Distant, 2.12.0 | 0.26 | 0.04 | 0.09 | -0.02 | 0.01 | 0.16 |
| Distant, 2.11.0 | 0.18 | 0.03 | 0.15 | 0.08 | 0.11 | 0.22 |

Each figure stands within 0.05 (one standard error). The recording is one
spaced pair close over the strings, so only the close pair has a recording
beside it. The octave at 250 Hz is where the two still differ: the
recorded pair is a little out of step there, and the law, which knows the
mean of a sound field and not this piano's, gives 0.

The other pianos' close pairs, 2.12.0, same notes: the studio grand 0.69,
0.21, -0.10, -0.04 and 0.01; the parlor grand 0.62, 0.36, 0.08, -0.01 and
0.04; the baby grand 0.86, 0.24, -0.09, 0.03 and 0.04; the upright 0.37,
0.42, -0.06, -0.29 and -0.07 (2.11.0: 0.25, 0.60, -0.01, 0.38 and 0.28).
The upright's octave at 1 kHz is the furthest any close pair's octave
stands under the law's mean, which is near 0 there. It is the draw of the
room's phases, which decides the side many modes fall on: with those
drawn again (a scratch build, not shipped) the upright's close pair reads
0.63, 0.26, -0.19, -0.04 and -0.17. The draw is 2.11.0's and was not
chosen for its result.

On phrases (a 15 s phrase, held chords and a bass line; whole-signal
correlation and the mono sum against the two channels' mean level), the
concert grand's close pair reads 0.14 to 0.29 and sums to mono 1.9 to
2.5 dB down (2.11.0: 0.38 to 0.49, 1.3 to 1.6), the XY pair 0.79 to 0.88
and 0.3 to 0.5 (0.65 to 0.79, 0.6 to 0.9), the live pair 0.20 to 0.56 and
1.1 to 2.2 (0.24 to 0.57, 1.1 to 2.1), the distant pair -0.04 to 0.12 and
2.5 to 3.2 (0.05 to 0.34, 1.8 to 2.8). The upright's close pair reads 0.01
to 0.17 and 2.4 to 3.0 (0.34 to 0.40, 1.6 to 1.8). 2.1.0 rejected a law
without the quarter-turn bound because a phrase through the distant pair
summed out of phase, at -0.3; under this one the distant pair's lowest
phrase reads -0.04.

**Tried and left out.**

- *The whole turn given to the right microphone*, the left keeping the
  board's own phases: 0.70, 0.15, 0.00 and -0.06 at 125 to 1000 Hz.
  Nothing makes one microphone the one that keeps the board's phases, and
  sharing the turn holds the bass together better (0.78).
- *Each mode put on whichever side took the least turning*, not its own:
  0.56, 0.10, -0.13 and -0.03. Neighbouring modes then land on opposite
  sides and take the bass apart between them.
- *The angle changed as little as would bring a third of an octave to the
  law's cosine*, instead of each mode set to it: 0.81, 0.38, -0.08 and
  0.06. The octave at 250 Hz stays as tight as 2.11.0's.

**Levels.** `KeyVoicing.h` is written again and `pascalScale` pinned to
what `KeyraLevels --report` reads (0.1840, 0.1517, 0.1128, 0.1609, 0.1703).
Bar Piano's typical playing read -11.4 VU with the new image, outside the
window about -9, so its two pairs' levels go from 0.6 and 0.8 to 0.72 and
0.96, their ratio kept; it reads -9.8. The Rack adapter's factory patches
are written from `KeyraPresets.h` and follow when its pin advances.

**Tests.** `Keyra.Engine` now holds, for each pair alone on a chord, that
its two channels are more than -0.217 alike (the least the law asks, sin
x / x at its first trough) and that the XY pair's are the most alike of
the four. No other test changed. How alike a pair's octaves are is a mean
over many notes, which `Tools/measure_pair_image.py` measures; one chord
in a test would hold a draw, not the law.

**Measured** (`Docs/validation/grand-pair-image-benchmark-2026-11-13.md`):
see the 2.12.0 entry of the README. Better: the stereo balance, 5.03 to
4.79 dB on the notes 1.0.0 fitted and 5.15 to 4.96 on the others, and the
bass's and the treble's spectral scores by 0.05 to 0.2 dB. Further off:
the middle register's partials (6.46 to 7.48 dB on the fitted notes, 6.52
to 7.05 on the others) and with them its attack, early and sustained
spectra by 0.2 to 0.7 dB; the bass's level by 0.2 to 0.3 dB and the
treble's stereo balance by 0.1 to 0.4 dB; the rise on the fitted notes
(13.3 to 14.2 ms); 89 single-note scores (rise 18, level 14, stereo balance 13, partials 10,
sustain 10, attack 7, noise 6, early 6, the other stereo score 5), the
largest C1's rise, 12.0 to 35.0 ms, then C3's, F♯4's and A3's.

**What the benchmark can and cannot say here.** A control
(`Docs/validation/grand-room-draw-control-2026-11-13.md`): 2.11.0 with
nothing changed but the draw of the room's phases, its key levels not
written again, so its level score does not compare. It moves the same
scores as far: the middle's partials on the unfitted notes 6.52 to 7.36
dB, the unfitted notes' attack and early spectra 6.32 to 6.87 and 5.98 to
6.56, the stereo balance 5.03 to 5.97 and 5.15 to 5.61, the rise 13.3 to 12.8 and
12.1 to 10.8 ms, 103 single-note scores worse. So a single note's
spectrum at one pair depends on the phases its modes arrive in by about as
much as this change moved it, and the benchmark does not tell this
change's cost in the middle register from chance. Its second stereo score
reads how strongly two channels are related and not in which sense, so it
cannot see what changed (0.20 and 0.19 to 0.20 and 0.18). Its rise is the
time from 10 to 90 % of an envelope's peak in its first 150 ms, and the
envelopes looked at (A3, C4, F♯4 and C5; A3 and F♯4 are among the notes it
calls worse) stand within 1 to 2 dB of 2.11.0's in each channel, on a
plateau from 15 to 130 ms whose highest point moves.

**Not measured.** The upright against the Helsinki recordings: they were
not in the session and the owner's machine was not reachable. By the
standing rule the change is not merged until that benchmark is run; the
owner has been asked for the recordings. Those are a coincident ribbon
pair, so they will score the upright's tone and level, not a spaced pair's
image.

**What is the owner's to hear.** A lettered set (`2026-11-13-pair-image`
in the project's files, not committed): A 2.11.0, B 2.12.0, one 15 s
phrase (four rolled low chords with the pedal, a line around C5, single
notes across the keyboard and a fortissimo chord from C1 to E5) through
four settings: the concert grand's close pair, its room pairs, all four
pairs, and the upright's close pair, each also folded to mono. B is
matched to A on whole-file RMS over both channels; the trims, -0.06 to
+0.57 dB, are in its key. The mono folds are (L+R)/2 of the matched files
and not matched again: how much each loses in mono is part of what is
judged. No verdict yet. Merged to `main` on 2026-11-13 with the verdict
open (2.13.1's entry).

## 2026-11-13 — the bass octaves, and the loops four abreast (2.13.0)

**Asked.** Before a first commercial release the owner asked for the whole
model to be read again across all five pianos: every note well tuned and
level, one character across the keyboard, the dynamics balanced, the mix
of mechanics, strings and resonances natural, every parameter used, the
CPU cost lower, then a Rack Extension built and tried in Recon with its
Shop materials.

**What was read, and stands.** On 2.12.0, the concert grand's close pair
beside the Salamander's 30 pitches and 16 layers:

- From key to key the level, the stereo balance and the brightness are as
  even as the recording's or more so.
- A held note's slow swells are the recording's size: 0.1 dB recorded and
  0.2 in the model from A0 to A2, 0.7 and 1.1 from C3 to A4, 3.9 and 3.5
  from C5 to A5, 4.8 and 2.8 from C6 to C8.
- Layer by layer, each run beside its own median, the octaves from C2 to
  B6 follow the recording's dynamics within 1 to 2 dB from the second
  layer to the fifteenth. A0 to B1 stands 3 to 4 dB low at every layer,
  C3 to B3 about 2 dB high, and C7 to C8 goes from 0.5 dB loud at the
  second layer to 5.5 at the twelfth. The softest layer (velocity 14) is
  4 to 8 dB quiet from C5 up, 14 at A6. These stay Known gaps: the top
  octave has been loud since 2.10.0's sound beside the board's modes.
- Every one of the plug-in's 24 parameters reaches the engine's field of
  its name (`Source/PluginProcessor.cpp`, read index for index), and
  `Keyra.ParameterExtremes` plays each at its ends.

The scripts behind these readings are scratch work kept with the project's
files, not committed.

**The tuner (measured, not by ear).** Through 2.12.0 the bass octaves
were 6:3 and A3's 4:2, which stepped the line a cent at every A from G♯3
down. `Tools/measure_tuner_octaves.py` applies each octave type to the
Salamander's own measured stiffness and reads the stretch it would give
beside the stretch recorded, A0 to A2: 4:2 stands 7.3 cents rms off (6.0
sharp in the mean), 6:3 4.5 (3.6 sharp, 7.6 at A0), 8:4 1.4 (0.1), 10:5
5.1 (4.3 flat). That piano's tuner set its bass 8:4. The model now passes
from 4:2 at A3 through 6:3 at A2 to 8:4 from A1 down, key by key, which
reads 2.2 cents rms there and has no step at an A. The ladder and not 8:4
from A3 down, though 8:4 reads 0.7 cents rms nearer over those eight
keys: 8:4 on the octave under an A3 tuned 4:2 would bring back the step
at G♯3.
The steps that remain are the strings' own, where wound strings give way
to plain ones (Known gaps).

**What the benchmark says of it**
(`Docs/validation/grand-tuner-ladder-benchmark-2026-11-13.md`): the tuning
score goes from 2.13 to 2.20 cents on the notes 1.0.0 fitted and 2.22 to
2.32 on the others; the bass's from 2.68 to 2.85 and 3.29 to 3.52. Four
single-note scores are worse: A0's tuning on both sets (4.87 to 5.63 and
4.91 to 5.61 cents), A1's partials on the unfitted notes (10.39 to 10.90
dB) and F♯3's rise there (3.05 to 5.44 ms). Everything else moves by 0.03
or less, and no note from C4 up moves at all. The score is a mean over a
note's first thirty partials. The concert grand's A0 to C2 are 0.47 to
0.74 as stiff as the Salamander's (Known gaps), so its upper partials
already stood under the recording's, and a fundamental 3 cents lower puts
them further under while it brings the fundamental itself nearer (A0: 6.5
cents under equal temperament before, 9.7 now, 16.5 recorded). The score
cannot be brought down by the tuner without tuning the model's bass sharp
of its own octaves. Against the shipping 2.11.0
(`grand-since-shipping-benchmark-2026-11-13.md`) 2.13.0 carries 2.12.0's
89 single-note regressions and these, 90 paired in all.

**Tried and left out: a harder felt in the middle.** The strike
measurements (the plan's first proposal) read the middle register's felt
as the recorded one played 6 to 10 dB softer. A felt up to 0.4 of a
decade stiffer, most at C4 and fading to nothing at C2 and C5, brought the partials of C3 to B3 0.4 to 0.8
dB and of C4 to B4 0.6 to 0.9 dB nearer the recording, the early spectrum
0.3 to 0.45 dB from the middle layers up, left C5 and above alone, and
put the loud noise of C3 to B3 1.1 dB and the decay 0.1 to 0.3 dB/s
further off. `Keyra.Engine` then failed three checks: the soft pedal's
darkening above 2 kHz fell to 0.31 dB (the check asks 0.5; 2.12.0 gives
0.64), the Hammer control's span from −1 to 1 to 5.3 dB (6; 6.9) and the
practice felt's cut above 1 kHz to 9.4 dB (10; 12.8). A harder felt
leaves each of those controls less to do, which is the felt's law, not
the tests' error, so the change is out and the tests are as they were.
The middle's missing upper partials stay a Known gap until the felt's law
itself (its exponent and hysteresis by register) is worked through.

**Looked at and set aside.** The board's rise above 1.1 kHz, as too small
beside the hammer's share. The keys with a hole at their fundamental (D♯5,
F♯5, A5): the board's modes and the sound beside them cancel there; 16 or
32 bridge points and a higher top mode leave it as it is.

**The loops four abreast (no listening needed).** The same compiler gives
the same bytes before and after on a dense pedalled phrase and a melody,
with GCC 13, Clang 18 and Clang built as Reason's SDK builds (no
vectoriser, no builtins), and the plain-loop fallback gives GCC's bytes
too. Cost on the development machine, 30 s renders through
`keyra_render`: 38.3 to 33.0 % and 9.0 to 8.4 % of one core with GCC,
35.7 to 32.3 % and 8.9 to 8.2 % with Clang, 72.7 to 33.4 % and 13.8 to
8.4 % the SDK's way. Not Reason's meter: no Rack Extension of the
physical model has run in Reason yet.

**The upright against the Helsinki recordings**, run on the owner's
machine the same day for 2.11.0, 2.12.0 and 2.13.0
(`Docs/validation/upright-pair-image-`, `upright-tuner-ladder-` and
`upright-since-shipping-benchmark-2026-11-13.md`; 137 fitted and 21
unfitted notes). 2.12.0: stereo balance 6.62 to 6.43 dB and 6.21 to 6.03;
attack 7.50 to 7.65 and 7.33 to 7.68, early spectrum 9.00 to 9.07 and
8.70 to 9.08, noise 9.66 to 9.80 and 8.49 to 8.66, level 4.17 to 4.23 and
3.07 to 3.15; 58 single-note scores worse, the largest D3's rise (68.4 to
79.3 ms) and the stereo balance of D7, C3 and D4 (7.2 to 12.3, 3.5 to 8.6
and 3.1 to 7.4 dB). 2.13.0 after it: tuning 3.36 to 3.43 cents and 3.41
to 3.55, the bass's 4.77 to 5.22 and 4.02 to 4.12, the bass's partials
10.62 to 10.80 and 9.98 to 10.30 dB; seven single-note scores worse, all
in the bass (C1's tuning 8.09 to 9.06 and partials 11.74 to 12.62, D♯1's
rise 10.6 to 19.4 ms, tuning 6.73 to 7.65 and decay 7.98 to 9.18, C2's
partials 11.72 to 12.50 and tuning 3.74 to 4.32). The recordings are a
coincident ribbon pair and say nothing of a spaced pair's image.

**What is the owner's to hear.** The bass tuning is audible, most on the
baby grand and the upright (A0 11 cents lower than 2.12.0's). It rests on
the measurement above, not on a listening test; the 2.12.0 image set's
verdict is still open. Merged to `main` on 2026-11-13 (2.13.1's entry).

## 2026-11-13 — the upright's bass octaves are an upright's (2.13.1)

**What was wrong.** 2.13.0 gave every piano the bass octaves read from the
Salamander grand: 4:2 at A3, 6:3 at A2, 8:4 from A1 down. Its own upright
benchmark, run after it was written, put the upright's bass tuning 0.1 to
0.45 cents further off and seven single notes worse, all at C1, D♯1 and
C2. That asked whether an upright's tuner hears its bass octaves where a
grand's does.

**Measured.** `Tools/measure_tuner_octaves.py --model upright`, on the
Helsinki upright's own stiffness with its own A4 as the reference, rule
against recording from C1 to A2 (seven pitches):

| Rule | rms, cents | mean |
| --- | --- | --- |
| 4:2 throughout | 2.39 | |
| 6:3 | 9.08 | flat |
| 8:4 | 19.56 | flat |
| 10:5 | 32.99 | flat |
| the grands' ladder | 14.87 | −12.17 (−30.1 at C1) |

The same table for the Salamander reads 7.3, 4.5, 1.4, 5.1 and 2.2 (the
2.13.0 entry above). The tool now prints what it reads straight from the
recording too. Stiffness, B × 10⁴, at C1, D♯1, A1, C2, D♯2, F♯2, A2: the
Helsinki 4.90, 3.82, 2.42, 2.37, 2.30, 2.05, 2.12; the Salamander at A0,
C1, D♯1, F♯1, A1 2.28, 1.61, 1.32, 0.88, 0.88. And each octave both of
whose notes were recorded, the upper note's partial n above the lower's
partial 2n in cents (the octave tuned stands at nothing):

| Octave | 2:1 | 4:2 | 6:3 | 8:4 | 10:5 | 12:6 |
| --- | --- | --- | --- | --- | --- | --- |
| Helsinki C1–C2 | +1.9 | −0.8 | −5.2 | −18.3 | −40.0 | −57.7 |
| D♯1–D♯2 | +9.0 | +7.5 | −1.1 | −12.0 | −21.4 | −35.6 |
| A1–A2 | +7.0 | +3.6 | +2.6 | −4.0 | −12.1 | −18.9 |
| C2–C3 | +0.1 | −2.6 | −3.0 | −9.0 | −19.8 | −25.6 |
| F♯2–F♯3 | +8.5 | +8.2 | +4.6 | +0.2 | −6.8 | −12.7 |
| C3–C4 | +3.5 | +8.5 | +2.5 | −1.6 | −8.9 | −16.2 |
| D3–D4 | −3.8 | −1.8 | −1.0 | −4.3 | −4.5 | −7.7 |
| F♯3–F♯4 | +0.5 | −2.6 | −2.3 | −7.4 | −11.6 | −15.1 |
| G♯3–G♯4 | −4.0 | −4.5 | −6.5 | −8.2 | −7.9 | −12.0 |
| Salamander A0–A1 | +16.0 | +13.8 | +11.6 | +4.1 | −4.3 | −14.5 |
| C1–C2 | +12.6 | +10.8 | +9.3 | +6.2 | −2.4 | −10.7 |
| A1–A2 | +0.9 | +4.6 | +3.2 | +2.5 | −0.8 | −2.9 |
| A3–A4 | +2.1 | +0.1 | −0.6 | −2.8 | −3.3 | −5.8 |

The grand's lowest octaves stand at nothing between 8:4 and 10:5 and its
A3–A4 at 4:2, as the rules table said. The upright's single octaves
scatter from 2:1 to 8:4 (an old instrument, each octave from one pair of
notes), its two lowest between 4:2 and 6:3; none of its bass octaves is
as wide as 8:4 but F♯2's. The chain and the single octaves agree that the
grands' ladder is not this upright's tuning; the chain says 4:2, the
lowest single octaves 4:2 to 6:3.

**Decided (measured, not by ear).** The upright's bass octaves are 4:2
all the way down (`Design::bassOctave`), the rule its recording's stretch
follows; the four grands keep the ladder and render to the byte as
2.13.0. The upright's A0 stands 8.9 cents under equal temperament (28.7
in 2.13.0, 18.1 through 2.12.0), C1 7.7, A1 5.4, A2 2.8. Its level rows
are written again and its output scale pinned to them (.1609 to .1622).

**Not measured: the baby grand.** The model's baby grand has bass strings
as stiff as its upright's (B at A0 3.35e-4 beside 3.13e-4; the Helsinki's
C1 4.9e-4, the Salamander's 1.6e-4). No small grand is in the reference
set, and no source found says at what size a tuner leaves the wide bass
octaves. It keeps the ladder (A0 29.9 cents under; 18.6 with 6:3 below
A2; 9.1 with 4:2).

**A listening set for the owner** (not committed; A is 2.13.0 as built
into the U45, one 16 s phrase of low octaves under held chords, default
controls, each letter trimmed to A's whole-file RMS: upright B −0.13 dB
and C +0.12, baby grand B −0.02 and C −0.28), on the upright and on the
baby grand: A the grands' ladder, B 4:2 throughout, C 4:2 at A3 to 6:3 at
A2 and 6:3 below. The upright stands at B by the measurement unless the
owner chooses otherwise; the baby grand at A until the owner chooses. No
verdict yet.

**What the benchmark says of it** (run on the owner's machine,
`Docs/validation/upright-bass-octaves-benchmark-2026-11-13.md` and its two
companions; 137 fitted and 21 unfitted notes). Against 2.13.0: tuning
3.43 to 3.33 cents and 3.55 to 3.39, the bass's 5.22 to 4.74 and 4.12 to
3.34; the bass's partials 10.80 to 10.07 dB and 10.30 to 9.22, its rise
8.95 to 7.42 ms on the fitted notes; no single-note score worse, nine
better (C1's partials 12.62 to 10.76 and tuning 9.06 to 8.16; D♯1's
partials 10.60 to 10.06, tuning 7.65 to 6.77 and rise 19.4 to 10.3 ms;
C2's partials 12.50 to 11.48 and tuning 4.32 to 2.81; D♯2's partials
10.30 to 9.22 and tuning 4.12 to 3.34). Against 2.12.0, whose bass was
6:3: the bass's tuning 4.77 to 4.74 and 4.02 to 3.34, its partials 10.62
to 10.07 and 9.98 to 9.22; one single-note score worse, G♯3's tuning on
the unfitted notes (0.89 to 1.41 cents; 2.12.0 tuned that key 6:3 under
an A3 tuned 4:2, the step 2.13.0 removed), eight better. Against the
shipping 2.11.0: 55 single-note scores worse, the largest D3's rise (68.4
to 79.3 ms) and the stereo balance of D7, C3 and D4, which are 2.12.0's
image and were reported with it; 60 better. The score is a mean distance
over thirty partials with no common pitch removed, and here it agrees
with the tuner's reading. The recording's own middle stands within 4
cents of A 440 (F♯4 −0.3, G♯4 −3.9, A♯4 −3.8), so its bass's 6 to 15
cents under is its tuner's stretch and not a flat piano.

**Merged.** On 2026-11-13 the owner chose "Merge all three with the
website": 2.12.0, 2.13.0 and 2.13.1 went to `main` at `7c0724c` and the
Rack device 2.13.1f1 with them. Both listening sets were still unheard:
2.12.0's image and this entry's bass tuning. What is on `main` is what
each entry says the engine does, and a verdict that goes the other way
is a new version.
