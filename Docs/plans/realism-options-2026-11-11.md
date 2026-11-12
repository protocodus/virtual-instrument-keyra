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

**After 2.7.0.** The room is sixteen lines under a Hadamard mix with the
knock diffused before it, and the long bridge spreads a string's force
along its length (`Docs/decisions.md`, 2026-11-12). Open: the bass's
partials stand 0.3 to 0.4 dB further off than in 2.6.0, cause not found.

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

## After 2.9.0: looked at and not built

Measured on 2026-11-12 against the Salamander; nothing here shipped.

- **The loud notes' top.** Partial by partial (50 to 750 ms, four
  layers) the model's upper partials stand from 12 dB under to 18 dB over
  the recording's from one note to the next (A3 9 under, C5 10 over, F♯5
  18 over, C6 12 under), and alike at a soft and a loud layer. It is each
  key's own response, the recorded piano's and the model's board's, not a
  mechanism the hammers or the strings lack.
- **The pedal's low ring.** The takes' ring under 150 Hz is the
  fundamentals of D2 to F2 (73, 77.5, 82 and 86.5 Hz). An impulse on the
  bridge with the pedal leaves no such ring on the model's open strings.
- **The image from key to key.** Through the close pair a note's two
  channels stand up to 12 dB apart on the Studio, Parlor and Baby Grand
  from C6 up (the Concert Grand within 3, the recording within 4 but for
  one note). Neither keeping the board's modes only up to 1.4 kHz nor
  taking the scattered arrivals out of the bridge's own radiation steadied
  it (a note still stood 13 to 15 dB to one side), and the first put the
  Concert Grand's treble balance from 2.5 to 5.0 dB off the recording's.
  The floor's and lid's reflections and the room are what is left to try.

## The Studio Grand voiced key by key: tried and dropped (2026-11-12)

The owner chose to try it and asked whether it would be 1.x's trap again.
A gain on what the strings take of the blow, for each key's first sixteen
partials, was measured on the Salamander's train notes (276 notes at 23
keys; the keys between in a straight line, within 12 dB) and scored on
four layers:

| Partials, dB | 2.9.0 | voiced |
| --- | --- | --- |
| the notes it was fitted to | 7.97 | 6.05 |
| the notes it never saw | 7.32 | 7.40 |
| of those, bass / middle / treble | 9.27 / 6.76 / 6.22 | 9.36 / 6.31 / 7.11 |

It moved what it was fitted to and nothing else, and put the unseen treble
0.9 dB further off: what it learns is each recorded note's own response,
which does not carry to the key beside it. The table and its tool are not
in the repository. (The keys' levels were not evened again for this
reading; the level score is left out.)

How even the keys are, as partials 2 to 8 against the first, each key
against the mean of the two measured keys beside it (every third key, a
middle layer, 50 to 550 ms, rms in dB):

| | bass | middle | treble |
| --- | --- | --- | --- |
| the recording | 9.3 | 11.8 | 9.9 |
| Concert Grand | 8.9 | 11.3 | 15.7 |
| Studio Grand | 12.6 | 10.0 | 18.0 |
| Baby Grand | 12.1 | 16.7 | 18.1 |

A real grand's keys are that uneven partial by partial through a close
pair, and the Concert Grand's are as even as the recording's up to B5.
From C6 up, and on the smaller pianos, the model's keys read 6 to 8 dB
rougher than the recording's.

That last reading was wrong (corrected the same day). From C6 up most of
partials 2 to 8 lie under the recording's noise floor, 90 dB under the
fundamental, where the recording reads the same on every key and the
model, which has no floor, reads whatever its skirts leave. Counting only
the partials that stand more than 60 dB over that on both, on the key and
on the two beside it:

| | bass | middle | treble (10 readings) |
| --- | --- | --- | --- |
| the recording | 9.3 | 12.0 | 9.9 |
| Concert Grand | 8.9 | 8.6 | 8.4 |
| Studio Grand | 12.5 | 8.6 | 11.4 |

And how far a key leans left or right (right over left, the first 500 ms,
C5 to C8, standard deviation in dB): the recording 4.9 to 5.0 on three
layers, with one key 13 dB to the right; Concert 4.9, Studio 5.7, Parlor
5.0, Baby 6.0, Upright 5.0, every key. Taking the board's modes only to
1.4 kHz, leaving out the scattered arrivals above them, or giving each
key one place on the bridge left that between 3.5 and 6.0.

So the model's keys are as uneven as a real grand's through a close pair
and no more, in their partials and in their place: nothing here to mend.

## After 2.10.0: open, and tried and left out

2.10.0 radiates what the smeared board's modes leave out beside them and
puts the bridge in series between the strings and the board
(`Docs/decisions.md`). Measured on 2026-11-12; open:

- **The top octave loud.** From C7 up the grand plays about 3.2 dB louder
  beside the middle than the Salamander (0.5 quieter in 2.9.0), and its
  whole notes die at 18.5 dB/s at C7 against the recording's 8.7.
- **The middle long.** Middle C and C5 die at 5.6 and 6.0 dB/s from 0.4 to
  2.6 s; the Salamander's at 9.2 and 10.5, the reference grands' at 6.2 to
  8.6 and 7.7 to 9.1.
- **40 to 56 Hz.** The concert grand's partials there stand 5.2 dB over
  the reference grands' median (0.6 in 2.9.0), where 56 to 80 Hz still
  stand 2.7 under.
- **The bass's onset.** A0 to C2 rise 25 to 60 ms later than the
  Salamander's at some layers, more than in 2.9.0.
- **The upright's image.** Its stereo balance stands 0.5 to 0.6 dB further
  from the Helsinki's than 2.9.0's; on the treble notes 1.0.0 fitted,
  7.7 dB (6.0).
- **One board for every maker.** Each piano's description holds its board,
  bridge and strike point, and the five share one set. Telling one maker's
  board from another's needs a measurement of each (a board's point
  impedance, its first modes), not a recording of the whole piano.

Tried and left out: a board of 1.0e3 kg/s (whole notes from A1 to A3 die
too fast); each partial weighted by what the board leaves out of it (not
causal); the modes levelled to a response rising to the treble; the ribs'
stiffness above their spacing; tuning a key by its first six partials. The
figures are in `Docs/decisions.md`.

## After 2.11.0: open

2.11.0 lets each wound string's partials stray from the stiff string on
their own, which ends the held bass chords' flanger (`Docs/decisions.md`).
Measured on 2026-11-12; open:

- **The stray by register.** The Salamander's stray is about 3 cents from
  A0 to D♯1, its single strings, and 1.0 to 1.9 from F♯1 to D♯2; 2.11.0
  draws one 1.5 cents for every wound string and reads 1.25 to 1.55 note
  by note. What makes the lowest strings stray more (their heavier
  winding, the bare core at their ends) is not modelled.
- **The bass's swing.** On the partials within 20 dB of the strongest the
  bass's beats swing 2.7 dB about their decay, the Salamander's 2.0; a
  smaller stray swings nearly as deep, so the depth comes from elsewhere,
  the unisons' spread or their coupling at the bridge.
- **Neighbours unlike, on the Baby Grand as on the recording.** Each key's
  whole-note level at 0.5, 1, 2 and 3 s after its onset, re its level at
  0.1 s: keys three apart differ by a median of 3.3 to 8.1 dB on the
  Salamander, 1.8 to 6.3 on the Baby Grand (adjacent keys 2.2 to 6.4) and
  2.0 to 8.0 on the concert grand. The Baby Grand's most unlike neighbours
  are E5 and F5, 18 dB apart at 1 s: E5 dips where the first decay meets
  the ring and comes back (34 dB down at 1 s, 28 at 2 s), as the
  recording's F♯5 does (31 to 35 down at 1 s, 29 to 31 at 2 s); and B6 and
  C7, 25 dB apart at 3 s, where C7 dies fast (the top octave, under 2.10.0
  above): the preset's Age of 0.15 does that, its C7 and C8 dying at 21.3
  and 28.6 dB/s, at Age 0 14.7 and 21.8, the Salamander's 13.8 and 19.4. On a probe none of these brought neighbours nearer at every
  time: unisons not narrowed from C5 up, no sideways drive, every key's
  detune scaled to one size, every unison left the same residual. Without
  the narrowing, on the concert grand on four layers, the envelope comes
  nearer (4.32 to 3.90 dB on the notes 1.0.0 fitted) and the decay goes
  further off (3.79 to 4.82 dB/s; the treble's 4.56 to 8.14). The ring
  itself is not too long: from 2 to 8 s the fundamental falls 2.0 to
  4.6 dB/s in the model from A4 to A5 and 2.4 to 4.1 in the Salamander.
  For reference, the strings' own loss at G5 is 0.26 a second, and a piano
  string clamped between two fixed ends on an aluminium plate lost 0.43 a
  second at 810 Hz, its clamps included (Ege and Chaigne, ISMA 2007).
- **The open top strings' ring under a treble note.** From 700 Hz up to the
  band under the fundamental, against the note's loudest band, on the
  Salamander's 32 notes from C6 up on layers 4, 8, 12 and 16: −52.4 dB at
  0.5 s, −60.7 at 1 s, −76.5 at 2.9 s; the model −55.4, −72.6 and −108.6.
  Under the recording's C7 the strings from F♯6 to B6 ring, each unison as
  two peaks 1.6 to 2.2 cents apart, 18 to 31 dB under the fundamental,
  dying at 10 to 15.5 dB/s. The model's open strings there die at 20 to
  74 dB/s: their own loss is 0.7 to 2.1 a second and the bridge takes 1.5 to
  2.9 from each string, up to three times that from a unison narrowed
  into step. On a probe build (2026-11-12), at 1 and 2.9 s:
  - each open string's sideways motion, driven and drained as a played
    string's is: −72.2 and −106.2;
  - Weinreich's slow mode for each open unison, at the full spread:
    −69.4 and −108.4;
  - the full spread with the sideways motion: −64.4 and −97.3, but the full
    spread takes the played treble's decay further off (above);
  - a board three times stiffer under the bridge from C5 to C8: −58.2 and
    −83.3; with the full spread and without the top keys' extra string
    loss as well, −54.4 and −74.0, within 6 dB of the recording at every
    time;
  - a board three times more mobile there instead, as measured boards are
    above about 1 kHz, at the full spread: −73.6 and −120.6.

  Only the stiffer board comes near, and the boards measured say the
  opposite: from about 1.1 kHz, where half a bending wave spans the
  space between two ribs, the board between them moves on its own and its
  mean impedance falls, from 800 kg/s to 230 at 2.5 kHz on an upright
  (Ege and Boutillon; Giordano's and Nakamura's measurements agree), and
  2.10.0 left the ribs above their spacing out because the notes' decay
  went further off with them. The recording says its top strings lose less
  to the bridge than the model's: unisons 1.6 to 2.2 cents apart are wider
  than the coupling, so each string would die at its own loss plus the
  bridge's 1.6 to 3 a second, 20 to 30 dB/s, where the recording's open
  strings take 10 to 15 and its whole notes 14 to 19 at C7 and C8. Nothing
  in the description explains a stiffer treble yet, so that probe is a fit
  and stays out.
- **The treble's place from key to key, on the smaller pianos.** Through
  the close pair alone, a key's lean (left over right, 0.1 to 1.1 s)
  moves between keys three apart by an rms of 10.4 dB from C7 to C8 on the
  Baby Grand, 8.4 on the Studio, 8.3 on the Parlor and 6.7 on the Upright;
  the Concert Grand's 3.1, the Salamander's 2.7 (from C5 to A6 the
  recording's 9.6, the model's 2.6 to 8.9). In the Baby Grand preset
  neighbours stand up to 20 dB apart (G6 and G♯6). Three things do it:
  the small boards' few modes under 2.6 kHz (76 on the Baby Grand, 158 on
  the Concert), each throwing a key to one side; a key between two of the
  bridge's eight drive points radiating from both above the modes, which
  combs; and each microphone's two scattered arrivals. The room, the lid's
  reflection and the room's first answer are not it.

  On a probe the board radiated as modes only up to 1.1 kHz and near the
  bridge above (where Ege and Boutillon measured its motion gather between
  the ribs), each key from its nearest drive point, without the scattered
  arrivals: the top's steps through one pair fell to 1.3 to 3.9 dB on
  every piano. Against the Salamander on four layers (108 notes, the
  Concert Grand, keys not levelled again) its partials came nearer (7.75
  to 7.31 dB on the train notes, 6.90 to 6.66 on dev) and the treble's
  attack (7.72 to 9.35), noise (7.99 to 9.71) and image (2.55 to 5.12)
  went further off; each part alone took the treble's image further off
  (5.51, 3.44 and 3.16). The Baby Grand preset also mixes the close and the
  XY pair, which comb against each other in the treble: with the probe its
  steps stay at 8.9 dB, 5.7 with the XY at 0.2, 4.2 with the close pair
  alone. Nothing shipped.

## Not about the sound

- The Rack Extension adapter still pins engine 1.0.0.
- CPU: the demos play at 0.07 to 0.18 times real time on the development
  machine (2.11.0). Its heaviest block is too unsteady there to compare
  builds: two readings of one build gave 40 to 94 % and 33 to 133 % of a
  block.

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
- K. Ege and X. Boutillon, "Synthetic description of the piano soundboard
  mechanical mobility" (the inter-rib fall, from 800 to 230 kg/s):
  <https://arxiv.org/abs/1210.5688>
- G. Weinreich, "Coupled piano strings", JASA 62 (1977).
- K. Ege and A. Chaigne, "End conditions of piano strings", ISMA 2007
  (Barcelona): <https://arxiv.org/abs/1101.4511>
