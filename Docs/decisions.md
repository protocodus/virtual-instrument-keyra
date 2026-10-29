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
levels read a velocity, a slope of 0.1 dB per unit or more. Each differs
from its first take as a velocity change does: by a median 5.4 velocity
units at its layers' level slope (about 1 dB), ten of the twelve brighter
where louder over their first eight partials, and in pitch by a median
0.02 cents (`Tools/find_repeated_takes.py`). Each strike now moves its key's
velocity by a draw of spread 5.6, the median absolute difference over 0.6745
and the square root of two; tuning does not vary. The draw sums four uniform
ones, so it stays within 3.5 spreads, and its sequence restarts with the
engine and on a piano switch, so a render replays exactly. `keyra_render`,
and so every benchmark, strikes at the velocity exactly unless given
`--vary`. Nine of the twelve strikes are at the softest layer, and the
spread plays at every velocity and on the grand, whose library holds one
take of each note. Measured, at the owner's request; Pop Upright's
before/after went to the owner, with no listening verdict yet.

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
within 1 dB of each other at velocities 1, 32, 64, 96 and 127, where they
sat 7.0, 8.7, 9.9, 4.5 and 0 dB apart, and from velocity 64 to 127 the
median key grows 10.6 dB on the grand and 9.9 dB on the upright (8.4 and
17.4). Single keys keep their recordings' differences: a key of the upright
sits from 4 dB under to 7 dB over the same key of the grand (the tenth to the
ninetieth percentile). The upright's softest layer no longer plays on its
own. The benchmarks strike at layer coordinates and do not move: their grand
renders are bit-identical and their upright renders scale by the new output
scale alone. The shape is the owner's choice, not a measurement. A lettered
chord ramp went to the owner on both pianos: the shipping response, this
halfway shape, a straight line and smoothstep, with the key beside them, and
no verdict yet.

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
benchmarks score within 0.001 dB of before, with no regressions. The upright's
dampers leave part of each partial ringing (above), so at the new level its
released chords reach the matrix's −60 dBFS floor 2 s after the keys go up
and 3 s at full Output; `Keyra.ParameterMatrix` allows the upright presets 3 s.
The level and the stage are the portfolio's, chosen by measurement; whether
the guard's cost to the hardest chords is worth keeping them out of the red is
the owner's to hear. A lettered crescendo of chords on both pianos went to
the owner, level-matched: the shipping engine, this stage, and the same level
through the limiter alone, with the key beside them, and no verdict yet.

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
against Balanced and Light, went to the owner level-matched with its key,
and no verdict yet.

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
against this fit, went to the owner level-matched with its key, and no
verdict yet.

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
key, and no verdict yet.

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
against this fit, went to the owner level-matched with its key, and no
verdict yet.
