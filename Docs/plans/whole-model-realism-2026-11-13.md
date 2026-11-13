# The whole model against the recordings, and what to change

2026-11-13, on 2.11.0. The owner asked for the model to be analysed as a
piano (how the hammers, strings, board, case, room and microphones make the
sound) and improved against real recordings used as benchmarks of the whole
model, not fitted note by note. The aim: a rich, polished, smooth, expansive
grand and a felt, delicate, home-like upright, intimate when played softly
and majestic at fortissimo, at a reasonable CPU cost.

Nothing here is shipped. The gaps are measurements. The probes were scratch
builds outside the checkout. The remedies are proposals until each is built,
benchmarked and heard.

## Since it was written

- **Proposal 2, the image, is built** as 2.12.0 on the work branch
  (`Docs/decisions.md`, 2026-11-13). The law is not the one sketched
  below: the board's own sound is alike across a pair by how far the paths
  from the board to its two microphones can differ, the room's by the
  pair's spacing.
- **The unisons are not why the strike has no bite** (finding 2 and the
  first half of proposal 1). Measured afterwards from how far each
  note's partials split, the Salamander's unisons stand 0.23, 0.30 and
  0.29 cents apart from C3 to A3, C4 to A4 and C5 to C6, and the model's
  at the default 0.26, 0.24 and 0.14. The default stays, and the upper partials missing from the
  middle register are the hammer's: its felt behaves like the recorded
  one played 6 to 10 dB softer. Proposal 1 is the felt's law and the
  velocity curve alone.
- **Proposal 1, the felt, was tried once and left out** (2.13.0,
  `Docs/decisions.md`, 2026-11-13): a harder felt from C3 to C5 brought
  the middle's partials 0.4 to 0.9 dB nearer and took the soft pedal, the
  Hammer control and the practice felt under what `Keyra.Engine` asks of
  them. It needs the felt's law by register, not one stiffness.
- **The grands' bass octaves are tuned on higher partials** since 2.13.0,
  set against the Salamander's stretch (`Tools/measure_tuner_octaves.py`);
  the upright's are 4:2 throughout since 2.13.1, as the Helsinki's read.
  Not among the proposals below.
- **Proposal 3, new rooms, is dropped.** Asked how a hall and a home
  should appear in the product, the owner chose to leave the room as it
  is (2026-11-13).

## How it was measured

- **The model alone**: `build-dsp/render_model` (the piano without the
  action's noises or the output stage), Concert Grand, close pair, default
  controls, 48 kHz.
- **The recording**: the Salamander grand (a 2.0 m Yamaha C5, a close spaced
  pair), 30 pitches from A0 to C8 in minor thirds, at five of its sixteen
  layers (2, 5, 9, 13, 16: velocities 31, 45, 69, 101, 124). The physical
  model is fitted to none of them.
- **Pooled and signed**: by register (bass A0–A2, low-mid C3–A3, mid C4–A4,
  upper C5–A5, treble C6–A6, top C7–C8) and by layer, model less recording.
  No per-note score, and each number is a mean over 4 to 18 notes.
- **What was read**: each octave band's share of the note by time window;
  band levels in 100 ms windows from 0.06 to 3 s; partial levels against the
  note's first three; level by layer; how alike the two channels are by band;
  the time to fall 10, 20 and 30 dB.

Limits to keep in mind: one recorded piano, 0.7 m shorter than the Concert
Grand (the Studio Grand is its size and is not surveyed yet); the upright is
not measured, because the Helsinki recordings and the owner's reference set
are on a device that was offline; probes did not rewrite `KeyVoicing.h`,
which moves a key's level and not the balance within a note. The scripts and
their raw results are in the project's files
(`keyra/whole-model-2026-11-13/`), not committed; `Tools/tone_survey.py` is
where the layer and time axes should land (item 9).

## What the measurements say

### 1. The model does not brighten with the blow as the piano does

Share of the note above 2.8 kHz from 0.05 to 0.3 s, dB (recording / model):

| Register | L2 | L5 | L9 | L13 | L16 | L2 to L16 |
| --- | --- | --- | --- | --- | --- | --- |
| bass | −66.6 / −68.4 | −60.4 / −58.9 | −51.4 / −48.8 | −40.4 / −42.1 | −32.4 / −39.2 | 34.2 / 29.2 |
| low-mid | −57.4 / −57.9 | −47.3 / −48.9 | −36.4 / −41.6 | −29.2 / −36.8 | −24.2 / −34.8 | 33.2 / 23.1 |
| mid | −54.5 / −56.2 | −37.3 / −47.2 | −29.0 / −40.0 | −24.3 / −35.8 | −21.9 / −33.9 | 32.6 / 22.4 |
| upper | −46.5 / −39.9 | −37.6 / −31.3 | −31.9 / −24.9 | −26.7 / −20.7 | −23.0 / −19.1 | 23.6 / 20.8 |
| treble | −36.1 / −38.0 | −30.2 / −37.5 | −23.5 / −27.5 | −20.1 / −23.7 | −17.8 / −22.6 | 18.3 / 15.4 |

From C3 to A4 the softest layer matches and everything from layer 5 up is 10
to 12 dB duller than recorded. The recorded piano brightens 17 dB between
layers 2 and 5 in the middle and 15 dB over the eleven layers above; the
model brightens 9 and 13. Its levels are close (middle register, layer 2 to
16 re layer 9: −9.1 to +7.0 dB recorded, −6.9 to +5.1 modelled).

This is not the velocity curve. At Dynamics 1 the level range grows to 20 dB
and the soft notes fall 25 dB too dull, while the hardest blow stays where it
was (−34.0 against −21.9): the hardest blow the model can give is no
brighter than something between the recording's fifth and ninth layers of
sixteen.

It is not hardness alone either. Hammer at +0.5 with the unisons nearly pure
(Detune 0.1) brings the loud layers within 5 to 6 dB (−27.7 at L16) and puts
the softest 11 dB too bright (−43.5 against −54.5): stiffer felt brightens a
soft blow twice as much as a hard one. The piano's felt is softer at the
skin and harder in the core than the model's law, or stiffens with the speed
of the blow more than the model's short-memory form of Stulov's felt lets it.
This is what a technician's voicing does, and it is the measured gap that
bears most directly on "intimate when soft, majestic when loud".

### 2. The strike has no bite, and the unisons are why

Level of the 2.8 to 5.7 kHz band, middle register, layers 13 and 16, dB re
the note's own 177 to 707 Hz band at 60 ms:

| Seconds after the blow | 0.06 | 0.15 | 0.3 | 0.5 | 0.8 | 1.2 |
| --- | --- | --- | --- | --- | --- | --- |
| Recording | −22 | −24 | −32 | −39 | −43 | −51 |
| 2.11.0 | −30 | −35 | −40 | −42 | −45 | −54 |
| Hammer +0.5 | −27 | −32 | −37 | −39 | −43 | −52 |
| Hammer +0.5, Detune 0 | −26 | −28 | −32 | −38 | −47 | −56 |
| Probe: Chaigne and Askenfelt's stiffness and string loss | −27 | −34 | −42 | −49 | −57 | −72 |
| Probe: 8 dB more coupling and radiation above 2 kHz | −28 | −35 | −42 | −43 | −51 | −61 |

The recorded highs hold for the first 0.15 s, fall fast to 0.5 s and slowly
after. The model's start 8 to 11 dB lower and are already falling. Four
explanations were probed:

- **The strings' own loss** (Chaigne and Askenfelt's square-of-frequency
  term, 6.25e-9 s at C4 as I recall it and about five times the model's, to
  be checked against the paper, with their felt stiffness): refuted. The
  highs then die three times too fast after 0.3 s.
- **The high partials' coupling to the board** (more drain and more
  radiation above 2 kHz, as a board that localises between its ribs would
  give): refuted in this form. It gains 2 dB at the strike and loses it by
  0.3 s.
- **The felt's hardness**: Hammer +0.5 puts the highs from 0.5 s on within
  1 dB, and leaves the first 0.3 s 5 to 8 dB short.
- **The unisons' tuning**: with the three strings nearly pure the first
  0.3 s comes within 4 dB and the 1.4 to 2.8 kHz band lands on the recording
  from the strike to 3 s (−16, −18, −21, −25, −31, −39 against −17, −18,
  −21, −26, −34, −39).

The mechanism is physical. A unison's strings start in phase and drift apart
at the mistuning times the partial's number, so the fifteenth partial drifts
fifteen times as fast as the fundamental. At the default Detune (0.69 cents
of spread) the upper partials of a middle note are out of step within
100 ms, and three strings out of step are 4.8 dB under three in step. The
recorded piano's stay in step for 150 to 300 ms, which reads as unisons
about twice as close (inferred from the band's level, not measured string by
string). 2.8.0 found the same from the other side (the spread narrowed from
C5 up to fit the fundamentals' decay); this is the same law seen in the
upper partials of the middle of the keyboard, where it shapes the attack.

### 3. The balance within a note changes character at C5

Partial levels against the note's first three, model less recording, dB,
loud layers:

| Register | 2 | 3 | 4–5 | 6–8 | 9–12 | 13–18 | 19–27 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| bass | 3.5 | 3.8 | 2.1 | 4.8 | 2.1 | −1.3 | −3.3 |
| low-mid | 1.4 | −3.3 | −0.2 | −2.5 | −5.0 | −4.2 | −9.4 |
| mid | −4.5 | 1.5 | −5.8 | −4.2 | −6.9 | −11.4 | −17.9 |
| upper | 1.7 | 9.0 | 8.5 | 6.0 | −5.8 | −14.7 | −28.2 |
| treble | −5.5 | −1.2 | −4.5 | −8.2 | −16.3 | | |

- **C3 to A4** lack upper partials at every layer (finding 1).
- **C5 to A5** hold 6 to 9 dB too much in partials 3 to 8, which is 1.5 to
  5 kHz: the glassy edge of that octave. The same frequencies are too weak
  an octave below, so this is the strike (the felt and where it meets the
  string), not the board or the microphones. A harder hammer makes it worse
  (+10 to +12), and taking away the extra hardness that begins at C5 does
  not move it (the ramp is small there).
- **The bass** stands 10 dB over the recording at its fundamental against
  partials 2 and 3, and its soft and middle layers hold 6 to 11 dB too much
  from the 28th partial up (1.5 to 2.6 kHz). The first is partly the owner's
  heavier bass and a longer piano; the second is the same felt law as
  finding 1, seen from the soft side.

### 4. The image is narrower than a spaced pair's, and softer in the bass

How alike the close pair's channels are (1 the same, 0 unrelated), loud
single notes, mean of the six registers:

| | 250 Hz | 500 Hz | 1 kHz |
| --- | --- | --- | --- |
| Recording | −0.11 | 0.04 | 0.04 |
| 2.11.0 | 0.35 | 0.22 | 0.23 |
| Probe: hold released to the pair's spacing | 0.04 | 0.08 | −0.05 |

On a chord phrase (the recording's own notes summed, the model playing the
same):

| | 125 Hz | 250 Hz | 500 Hz | 1 kHz | Whole | Mono sum |
| --- | --- | --- | --- | --- | --- | --- |
| Recording | 0.66 | 0.13 | 0.07 | 0.25 | 0.30 | −1.9 dB |
| 2.11.0 | 0.44 | 0.49 | 0.49 | 0.53 | 0.49 | −1.3 dB |
| Probe: hold released | 0.29 | −0.26 | 0.13 | 0.11 | −0.06 | −3.3 dB |

The model holds every mode's phase between the two microphones within 70 to
90 degrees so that the pair sums to mono (`designBoard()`). That is a rule
of thumb, not what a pair hears: two microphones 0.6 m apart hear the same
below about 150 Hz and unrelated sound above about 300 Hz. The hold is at
once too tight above 250 Hz (the narrow image) and too loose below it (it
allows 70 degrees at 100 Hz, where the recording's channels move together).
Released to what the spacing allows, the model matches the recording from
250 Hz up and overshoots below: the bass comes apart, which the recording's
does not.

### 5. The middle of the keyboard dies evenly where the piano falls and then sings

Seconds to fall 10, 20 and 30 dB (layers 9 and 13, recording / model): bass
1.6 / 1.9, 3.4 / 4.7, 6.3 / more than 6.5; low-mid 0.8 / 1.1, 1.95 / 2.45,
3.7 / 4.8; mid 0.45 / 0.75, 1.15 / 1.7, 3.35 / 3.95; upper 0.35 / 0.5,
0.7 / 0.95, 2.15 / 3.0. In the middle the band of the fundamentals stands at
−18 dB 0.8 s after a recorded blow and −12 after a modelled one, then the
recording flattens (−25, −27, −32 at 1.2, 2 and 3 s against −17, −22, −25):
a quick first fall and a long aftersound, where the model's is one slope.
The README's Known gaps has this as "the middle long".

### 6. The board adds no colour of its own, by construction

A knock on the bridge reaches the close pair within ±3 dB from 50 Hz to
2 kHz, −2.4 dB at 2.5 to 5 kHz and −5.7 dB at 12.8 kHz, at ten keys. Every
mode is levelled to a flat target and every key is voiced to its neighbours
(`KeyVoicing.h`, up to ±15 dB). So what separates the model's tone from the
recording's is the strike and the strings, not the board's response, and the
model has no body resonance a listener could call wood. No recording here
holds a real board's knock, so this stays an observation.

### 7. Where the CPU goes

One core of the session's machine, 256-frame blocks at 48 kHz, denormals
flushed as a plug-in's callback does (a scratch build with a timer around
each part):

| | A gentle melody | Sixteen voices, pedal down |
| --- | --- | --- |
| Whole model | 5.3 % | 15.4 % |
| Board, microphones, room | 3.4 % | 4.0 % |
| Strings (voices) | 1.0 % | 7.4 % |
| Open strings (the sympathetic bank) | 1.1 % | 4.6 % |
| Hammer contact | 0.02 % | 0.03 % |
| A blow's setup | 12 µs each | 9 µs each |

The board costs 3.4 % whether one note sounds or sixteen; a voice costs
about 0.45 %; the pedal about 3.5 %. The worst block of the stress phrase is
28 % (eight blows landing in one block), against a mean of 15 %. A blow's
setup is not the cause of heavy blocks: it takes 10 µs. Without the flush a
block reaches 80 % in the open strings' bank as it is first driven, so a
front end that does not flush denormals pays for it; the plug-in does, and
the Rack adapter should be checked when its pin advances.

### Read in the code, not measured here

- **The room** is one size: sixteen delay lines of 0.8 s fed by the distant
  pair's signal, with the floor's and the lid's reflections. There are no
  walls, so no early reflections that say how large the space is, and
  nothing for an upright against a wall at home. The Salamander is close and
  dry and cannot benchmark this.
- **The open strings** answer with ten partials and two duplex modes a key.
  A0's strings answer up to 275 Hz and C2's to 650 Hz, where a real bass
  string holds fifty partials under 3 kHz: the pedal's wash is thin where
  the piano's is densest (Known gaps: the open strings' ring).
- **The strings' stretching** gives twice each partial's frequency for forty
  partials below C5. The sums of two partials and the strings' own
  longitudinal modes are absent (Conklin 1999; Bank and Sujbert 2005).
- **A restrike** is solved against a string at rest (`startContact()` clears
  the contact's copy of the string), and its force is added to what rings.
  The README says a restrike meets a string already moving; the hammer does
  not feel that motion.

## Proposals, ranked

Ranked by how much of the owner's aim each covers for its cost. The first
two cost no CPU.

### 1. The strike: unisons in tune, and felt with a soft skin and a hard core

**What.** Two changes, benchmarked together.

- Grand unisons about half as far apart at the default (what Detune 0.3
  means, or the default itself, the owner's choice of which). The control
  keeps its range to a bar piano.
- The felt's law re-fitted across the whole keyboard to pooled targets
  instead of note spectra averaged over 0.3 s: soft blows as dull as now,
  blows from layer 5 up 10 dB brighter from C3 to A4, C5 to A5 6 to 9 dB
  less in partials 3 to 8, soft bass blows duller from the 28th partial up.
  Two physical forms can give it: a higher exponent with the stiffness
  pinned at a smaller compression (a soft skin over a hard core), or
  Stulov's felt with its memory kept (stiffer the faster it is compressed).
  The model has the second in its short-memory limit, which the blow's speed
  hardly stiffens. Both are derivable; which fits is a measurement.

**Judged by** the tables of findings 1 to 3 (brightness by layer and
register, the band's level through the first 1.2 s, partials by number),
with `Tools/benchmark_recordings.py` as the regression gate, then a lettered
listening set.

**Cost and risk.** No CPU. It moves every preset's tone, so `KeyVoicing.h`,
`pascalScale` and the level checks follow. The earlier fits traded hardness
against the wide unisons and the short averaging window, so expect several
rounds. The owner can hear the direction today on the Concert Grand: Hammer
at +0.5 and Detune at 0, which is the fourth row of finding 2 (loud notes
only; soft notes come out too bright, which is the part the new law fixes).

### 2. The image: what a spaced pair hears

**What.** Replace the 70 to 90 degree hold by the pair's own physics: the
channels in phase where the microphones are closer than half a wavelength
and free above it (a wave from any direction arrives within 2πfd/c of a turn
apart; a diffuse field's coherence between two points is sin(kd)/kd). The
coincident XY pair then stays the mono-safe one. The bass must come out more
alike than it is now, not less; the probes do not do that yet, and the
random phase each mode's share of the room is given is the first suspect.

**Judged by** the recording's own figures: 0.66, 0.13, 0.07 and 0.25 at
125 Hz to 1 kHz and 0.30 for the whole signal on the chord phrase, a mono sum
1.9 dB under the stereo one.

**Cost and risk.** No CPU. Wider and less mono-compatible than now by design
(about 0.6 dB in the mono sum), so the listening set includes a mono fold.

### 3. The space: a hall for the grand, a home for the upright

**What.** Early reflections for each pair from the walls and ceiling of a
stated room (image sources, first order: a handful of taps on delay lines
the model already runs), a decay that is longer in the bass than the treble,
and more than one room: the studio it has now, a hall (1.6 to 2 s, the
"expansive" and "majestic" of concert recordings) and a living room for the
upright (0.3 to 0.4 s, a wall 10 cm behind the board, which lifts its bass
and combs its middle as a real one does).

**Judged by** recordings that hold a room, which the Salamander does not:
the owner's reference set once the device is reachable. Until then this is
ranked on the aim, not on a measurement.

**Cost and risk.** Under 1 % of a core for the taps by my estimate,
unmeasured. It needs the owner's
decision on the product: a Room choice on the panel and in the saved state,
or rooms baked into presets.

### 4. Fortissimo's own sounds: the strings stretching

**What.** The sum-frequency partials and the longitudinal modes a hard blow
adds in the bass and tenor (Conklin; Bank and Sujbert report the forced
response as the audible part). They grow with the square of the amplitude:
nothing at pianissimo, a metallic growl at fortissimo, which is the widening
of character with force the aim asks for. It also adds to the bass's
brightness range, 29 dB against the recording's 34.

**Judged by** what the recording holds between the partials of loud bass
notes against soft ones (the benchmark's noise score, by layer).

**Cost.** Computed only while a voice's amplitude is over a threshold, so
nothing in quiet playing; my estimate is 1 to 2 % of a core in loud bass
passages, unmeasured.

### 5. The middle's sustain: a first fall and an aftersound

**What.** Check what the middle strings meet at the bridge against published
bridge impedances (Conklin 1996, Giordano 1998, Ege and Boutillon 2013), key
by key from the model's own tables, before changing anything: the bridge as
a beam in series and the hold on the board's conductance both make the
middle a stiffer termination. And carry the second polarisation past the
first 16 partials, since it is what the aftersound is made of. Item 1's
unisons already move this (in tune, three strings pull the bridge together
and fall faster at first).

**Judged by** finding 5's table and the fundamentals' band through 3 s. The
owner may prefer the longer middle: by ear, against the recording.

**Cost.** About 0.1 % a voice for the wider second polarisation.

### 6. The pedal's wash

**What.** Give the lowest thirty keys' open strings their upper partials,
either outright (the bank grows from 4.6 to about 7 % with the pedal down)
or as a dense bed of resonators with the open strings' partial density and
decay above the tenth partial, driven by the bridge as the bank is.

**Judged by** `Tools/benchmark_pedal_wash.py` on the Yamaha C3's pedalled
takes (not in this session).

### 7. A repeated note meets a moving string

**What.** Start the contact's copy of the string from the voice's motion at
the strike point instead of from rest. A repeated note then comes out a
little louder or softer and brighter or duller each time, as on a piano,
with no random draw. A copy of at most 160 values a blow.

### 8. The upright

Not measured here. With the Helsinki recordings in the session: the same
surveys, then its own strike (finding 1's law on its hammers), the wall and
the room of item 3, and a decision on a felt-forward close position (the
front panel off, microphones at the hammers, the action audible), which is
the sound "felt, delicate, home-like" names in current records.

### 9. The benchmark itself

Add the layer axis and the time axis to `Tools/tone_survey.py` (brightness
by layer, band level by time, partials by number, the pair's coherence on
summed notes), and run it over every recorded piano of the reference set, so
that the model is tuned to what pianos share and not to one Yamaha under one
pair of microphones.

### 10. CPU

The budget above leaves room: items 1, 2 and 7 are free, 3 and 5 are under
1 %. The fixed 3.4 % of the board and microphones is the place to look
first if more is needed (the `dsp-cpu-optimization` procedure), since every
note pays it.

## Tried before and left out

From [realism-options-2026-11-11.md](realism-options-2026-11-11.md), still
standing: modes only to 1.1 kHz (better partials, worse treble attack, noise
and image); a three times stiffer treble board (a fit); per-key voicing of
partials (the 1.x trap). New here: the published string loss and a stronger
high-frequency coupling to the board, both refuted in finding 2; a harder
hammer everywhere and a wider velocity curve, both refuted in finding 1.

## Order of work

1. Item 2, the image: small, free, and independent of the rest.
2. Item 1, the strike: the largest gain and the most rounds.
3. Item 7 with item 1, since both are in the contact.
4. Items 3 and 8 once the owner has decided the room's place in the product
   and the reference recordings are in the session.
5. Items 4, 5 and 6 in that order.

Each is its own version with its benchmark movement, a lettered listening
set against 2.11.0, and its entry in `Docs/decisions.md`.
