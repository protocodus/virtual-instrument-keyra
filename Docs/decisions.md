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
