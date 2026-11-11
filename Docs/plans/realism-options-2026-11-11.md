# Options to increase realism after 2.4.0

2026-11-11. What still separates the model from the recordings, as measured
on 2.4.0, and what could close each gap. The gaps are measurements (the
README's Known gaps and `Docs/decisions.md` name the tools and the notes);
the remedies are proposals, and what each would gain is not measured until
it is built. Ranked by how much of the remaining distance each is likely to
cover for its cost.

## Where 2.4.0 stands

On the Salamander grand's notes 1.0.0 never fitted
([report](../validation/grand-key-presses-benchmark-2026-11-11.md)):

| Score | 1.0.0 (fitted engine) | 2.3.0 | 2.4.0 |
| --- | --- | --- | --- |
| Partials' levels, dB | 5.3 | 8.2 | 8.2 |
| Tuning, cents | 0.9 | 2.8 | 3.2 |
| Decay, dB/s | 2.1 | 3.7 | 4.1 |
| Attack, dB | | 7.8 | 6.6 |
| First half second, dB | | 8.1 | 7.0 |
| Noise between the partials, dB | | 9.3 | 7.8 |
| Rise, ms | 4.5 | 15 | 13 |

## Ranked options

### 1. An even board within a note

**Gap.** Within a note a partial stands 6 to 10 dB from the mean of its
neighbours where the Salamander's stand 2.5 to 5, and the partials' score
has not moved since 2.0.0 (8.2 dB against the fitted engine's 5.3). This is
the largest standing distance and the one most likely heard as a synthetic
colour on single notes.

**Options.** (a) Drive the board along a length of bridge instead of at a
point: a real bridge is a stiff beam that averages the plate's response
over many rib bays, which is why measured point mobilities are smoother than
a bare plate's (Ege, Boutillon and Rébillat 2013 give the measured board;
Chabassier, Chaigne and Joly 2013 model the bridge as part of the plate).
The model has eight bridge points; each string could spread over three or
four with the bridge's own bending stiffness. (b) Raise the modal overlap
where the model's is too low: more modes under 2.6 kHz or a higher loss
factor in the 300 Hz to 1.5 kHz range, checked against Soundboard's range.
(c) Voice partial groups, not only keys: a filter per key from the model's
own measurement, as `KeyVoicing.h` does for level. (c) is a correction, not
a cause, and should come last.

**Cost.** (a) is a change to the tables, not to the per-sample loop.
Moderate.

**After 2.5.0.** Part of this distance was not the board. The strings were
10 to 100 % stiffer than the recorded ones, so the benchmark looked for the
upper partials where the model did not have them; with the scale rebuilt the
score is 7.9 dB. Of what is left (measured over all four windows of the
score), the larger part is each partial against its neighbours and the
rest a tilt by register and loudness: loud notes from A3 to G♯4 hold 7 to
8 dB too little from 1.2 to 4.8 kHz, notes from A4 to G♯5 6 dB too much from 1.2 to
2.4 kHz. Along the keyboard the recorded grand's first four partials stand
6 to 8 dB off their neighbours a minor third away, the model's 4 to 11, so
the recorded piano is not even either.

### 2. The action through the model

**Gap.** The owner's complaint was the key presses. 2.4.0 makes the recorded
action noises vary and gives the model its own thump and knock, but the two
still play side by side: a key's landing, its return, a damper falling and
the pedal are 1.0.0's fitted knocks beside the model, they do not ring the
strings or the board, and a pedal going down does not set the freed strings
whispering.

**Options.** (a) Send the action's knocks through the path 2.4.0 built for
the catch (the keybed onto the board's edge), so the board and the open
strings answer them as they answer the hammer's catch, and drop the part of
the fitted knocks the model then produces itself. (b) Give the dampers a
small pluck on leaving the strings, which is what the pedal's whisper is.
(c) Settle what the thump is. 2.4.0 takes it as the action catching the
hammer; the literature names the key meeting the key frame (Askenfelt and
Jansson's KTH lecture), and puts key bottom at the hammer's contact at mezzo-forte, 12 ms after it
at a piano touch and 3 ms before it at forte (Askenfelt and Jansson 1990, as
cited by Goebl 2001). The recordings' thump comes later than that and later
when soft, which both readings share; a key-bottom impulse at those times
through a keybed that rings would also explain why the recorded thump peaks
later and longer (24 to 42 ms) than the model's (20 to 27). Build both and
compare on the Salamander's sixteen layers and on MAPS, whose Disklavier
plays without a finger.

**Cost.** (a) and (b) small, on top of 2.4.0. (c) one round of measurement.

### 3. The top end from mezzo-forte up

**Gap.** A note's share above its sixth partial is 4 to 8 dB less than the
Salamander's at every velocity, and the middle of the keyboard holds 13 to
15 dB less in the 2 kHz octave from mezzo-forte up.

**Options.** (a) Longitudinal string motion: its forced partials sit
between and above the transverse ones and grow with the square of the
amplitude, so they brighten loud notes only (Bank and Sujbert 2005; the
model has Conklin's phantoms from C5 down only). (b) The board's radiation
above the kept modes (2.6 kHz) is one patch by the bridge; fit its level
and corner per register instead of once. (c) Refit the felt's law where it
is hardest, per register, against the Salamander's upper layers and MAPS.

**Cost.** (a) moderate CPU, a few forced partials a string. (b), (c) small.

### 4. The stereo image

**Gap.** Between 500 Hz and 2 kHz the two channels of a forte note are 0.4
alike where the Salamander's are 0.05. The pairs are held to sum to mono
(no mode more than 70° to 90° out of step between the channels).

**Options.** Free the Live and Distant pairs from that limit, where real
spaced pairs are decorrelated, and keep it on Close and XY; or make the
limit a control (Width above 0.75). The mono sum of the far pairs then
thins, as a real spaced pair's does.

**Cost.** Small; needs the owner's ear on the mono sum.

### 5. Decay by register, two-stage

**Gap.** The decay score is the one that has moved away in two versions
(3.7 to 4.1 dB/s; from C6 up 5.3 to 7.0). C8's fundamental falls 2 to 8 dB
short of the recording's in its first 300 ms and about 30 dB short after a
second; C7's and F♯7's fall 2 to 13 dB too far in the first 300 ms.

**Options.** Fit the strings' two loss terms and the bridge's hold per
register against first and second decay rates measured the same way on the
Salamander, MAPS (two uprights and, once extracted, its grands) and the
Steinway, instead of one hold curve; the unisons' polarisation coupling sets
the second rate (Weinreich 1977).

**Cost.** Measurement, then constants. Small in code.

### 6. The bass: level and onset

**Gap.** Beside the middle of the keyboard the keys from C1 to F♯2 stand 1
to 8 dB quiet at every layer but the softest, and the bass's low band
reaches half its level later than recorded (rise 23 ms off on average).

**Options.** Set the voicing's line through the keys against the recorded
pianos' own level by key, instead of a smooth line through the model's;
look at the wound strings' contact time and at the board's lowest modes'
build-up, which is where the rise is made.

**Cost.** Small for the level, unknown for the rise.

### 7. The room

**Gap.** With the room in the close pair a treble note's tail stands 69 dB
down after 600 ms against the Salamander's 47, and the bass's partials
moved 1 dB further from the recording. One eight-line network rings 0.8 s
for every pair.

**Options.** A room size or a second, longer network for a hall; early
reflections by image sources per pair in place of the network's first
answer; less low end in what the close pair hears of the room.

**Cost.** Moderate. The listening set's C (no added room) decides first
whether the close pair should hear it at all.

**After 2.6.0.** The 600 ms figure above was the recording's own floor.
To 300 ms the treble's tail now falls as recorded, by the case's knock in
the room; the board at half its loss did as much and slowed the bass.

### 8. Each piano against its own recordings

**Gap.** The three grands share constants set on the Salamander (a Yamaha
C5) and one Steinway; the upright's are set on MAPS and scored on Helsinki,
where its partials moved 1.0 dB further off in 2.4.0. The Parlor has the
Yamaha C3 and a Model L in the reference set, the Baby a 1974 baby grand,
the Concert MAPS's grands, a Bechstein and a Bösendorfer.

**Options.** A benchmark split per piano and a pass over the constants that
are a piano's own (hammers, thump level, room, strings' losses), with the
rest shared.

**Cost.** Mostly measurement. MAPS's grands are staged, not yet extracted.

### 9. The knocks' remaining misfits

**Gap.** Single keys' thump up to 14 dB off; the knock 2 to 12 dB weak from
C6 to F♯6; something under 180 Hz with the blow from C5 to A5 that the
recording does not hold; the softest treble layer 5 to 13 dB quiet.

**Options.** Follow from 2(c) and 6; a felt law with a floor at light
compression for the softest blows.

## Not about the sound

- The Rack Extension adapter still pins engine 1.0.0.
- CPU: the heaviest blocks take 35 to 62 % of a block on the development
  machine (20 to 54 % in 2.3.0).

## Sources

- A. Askenfelt and E. Jansson, "From touch to string vibrations", in Five
  Lectures on the Acoustics of the Piano (KTH, 1990), on the key bottom:
  <https://www.speech.kth.se/music/5_lectures/askenflt/keybott.html>
- A. Askenfelt and E. Jansson, "From touch to string vibrations. I: Timing
  in the grand piano action", JASA 88 (1990); figures as cited in W. Goebl,
  "Melody lead in piano performance", JASA 110 (2001):
  <https://iwk.mdw.ac.at/goebl/papers/Goebl_JASA2001_melodyLead.pdf>
- W. Goebl, R. Bresin and A. Galembo, "Touch and temporal behavior of grand
  piano actions", JASA 118 (2005), not read for its figures.
- B. Bank and L. Sujbert, "Generation of longitudinal vibrations in piano
  strings: from physics to sound synthesis", JASA 117 (2005).
- J. Chabassier, A. Chaigne and P. Joly, "Modeling and simulation of a grand
  piano", JASA 134 (2013).
- K. Ege, X. Boutillon and M. Rébillat, "Vibroacoustics of the piano
  soundboard", JSV 332 (2013).
- G. Weinreich, "Coupled piano strings", JASA 62 (1977).
