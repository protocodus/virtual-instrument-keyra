# Keyra release history, 0.2.0 to 1.0.0

The Version history the README carried up to 1.0.0, moved here unchanged when
2.0.0 replaced the modal engine these entries describe with the physical
piano. Sources, tools and tests they name are those of revision `dbc5692`;
many were retired with that engine.

### 1.0.0 — 2026-11-10 — the first release

The owner numbered Keyra's first release. The engine is 0.4.38's and plays
as it did: nothing in the sound, the controls or the saved state changes,
and sessions and presets from 0.4 load as before. The host acceptance that
is not yet verified for it is listed under Known gaps
([decision](../decisions.md)).

### 0.4.38 — 2026-11-10 — no key stands off its neighbours

Struck one by one, some keys still stood off the keys beside them. The key
smoothing of 0.4.32 summed a key's partials as recorded, without the velocity
colour a strike adds, and the gain that colour takes is each key's own: at
velocity 40 the Hamamatsu grand's C1 played 4.8 dB under its neighbours. It
kept the lowest and highest keys as they were, the Hamamatsu's A0 5 dB over
its neighbours and its C8 6 dB to their right, and it set its gains at the
recorded layers only, so New York's D♯7 stood 6.5 dB to one side at velocity
80. The smoothing now counts the colour, carries the six lowest keys along
the bass's own slope, holds the six highest keys' balance at the top
thirteen's median and, on the pianos of six layers or fewer, also sets gains
halfway between the layers. Across the four grands the largest jump from a
key to its neighbours falls from 5.8 to 2.6 dB in level and from 6.5 to
2.3 dB in balance, and the upright's from 2.0 to 1.2 dB in level; every
key's tone, decay and rise stay as they were
([key smoothing](../research/key-balance-smoothing-2026-11-10.md)). The
upright's balance from G6 up, which its undamped strings carry, is unchanged
(Known gaps). On the grand's recordings no benchmark mean moves by more than
0.07; the other pianos' recordings were not at hand and their benchmarks
were not run. The Kakegawa grand's, the Hamamatsu's and the Hamburg's
default sounds are re-pinned to the level they read before, and the grand's
other four presets read 0.19 to 0.26 dB higher on the meter.

### 0.4.37 — 2026-11-10 — the grands' soft pedal as concert pianists' sounds

The grands' una corda took too much. Played from the MIDI of thirty concert
performances on Disklavier grands (MAESTRO), the four grands stood 1 to 4 dB
under the recordings from 125 Hz to 2 kHz wherever the pianist's soft pedal
was down, and three of them 5 to 9 dB under from 4 kHz. Its sizes had no
source; they now stand on that measurement. The pedal no longer turns
everything down to 0.72: it softens the felt, 1 dB a partial up to the fifth
above the first and no further, and moves a share of the prompt sound to the
slowest lane, as before. Over the four grands' bands from 62 Hz to 8 kHz the
distance from the recordings goes from 2.8 to 0.8 dB on the train
performances and from 3.4 to 0.9 dB on the dev performances
([report](../validation/una-corda-maestro-2026-11-10.md),
[decision](../decisions.md)). A session that plays the soft pedal on a
grand sounds 2 to 3 dB louder under it and less dull; the upright's
half-blow and everything without the soft pedal render byte for byte as
before.

### 0.4.36 — 2026-11-10 — a strike rings the open strings

Under the pedal a note sounded too clean. The open strings took up only what
the notes' partials drove, the strings that share them, and between a note's
partials the grand stood a median 26 dB under the Yamaha C3's pedal-down
takes, 42 dB by 3 to 6 s. A strike's blow now sets every string whose damper
is off ringing at once, under the pedal or under held keys, at a level and a
fall toward the treble fitted on those takes' train pitches (How it works).
Scored by `Tools/benchmark_pedal_wash.py`, the grand stands a median 1.1 dB
under the train pitches and 4.7 dB over the five dev pitches, 5.7 and 6.4 dB
from them in mean |dB| where it stood 26.7 and 22.6, and the other four
pianos move from 13.6 to 24.2 dB off to 5.9 to 8.9 dB
([report](../validation/pedal-wash-benchmark-2026-11-10.md),
[decision](../decisions.md)). Resonance scales it with the rest of the open
strings' sound. A note alone without the pedal renders byte for byte as
before.

### 0.4.35 — 2026-11-10 — a key struck again is not turned down

Since 0.4.12 a key struck while it still sounded played up to 2.6 dB quieter
in its partials, with up to 28 % less knock and noise, up to 35 % less ring
on the undamped strings, a shorter rise, a brighter colour and a small pull
on its partials' pitch and phase, none of it measured: no recording here
strikes a sounding string. Under the pedal the grand's C4 struck six times at
0.25 s stood 4.6 dB under its first strike by the sixth and the upright's up
to 7.8 dB. The strike now plays as it does on strings at rest and adds to
what sounds; the grand's sixth stands 1.9 dB under and the upright's lowest
5.9 dB, where the two waves' phases still part
([decision](../decisions.md)). Without the pedal, and on the benchmark's
single notes, every piano renders byte for byte as before.

### 0.4.34 — 2026-11-10 — the keys between recorded pitches as wide as their neighbours

On the Hamburg, New York and Hamamatsu grands a key between two recorded
pitches turned each partial's right channel to the lag between theirs,
which no recording follows and which pulls the partials towards in phase:
those keys sounded narrower than the recorded pitches around them, New
York's between C3 and C5 at a median correlation of 0.64 between the two
channels against 0.35. They take the nearer pitch's lag now, as their
phases already did, and stand at 0.35
([stereo lag](../research/network-key-stereo-lag-2026-11-10.md)). The
recorded pitches play as before; over the eleven measures other than level
New York's dev takes stand 1.07 tolerance units closer to their recordings,
the Hamamatsu's 0.42 and the Hamburg's 0.56 further, all in the rise
([New York](../validation/newyork-network-key-lag-benchmark-2026-11-10.md)).
New York's tube, which hears the two channels' sum, is re-pinned to the
level it read before. The grand and the upright are unchanged.

### 0.4.33 — 2026-11-10 — the keys between recorded pitches no brighter than their neighbours

On the Hamburg, New York and Hamamatsu grands a key between two recorded
pitches took a partial only one of them holds at that pitch's level by
number, though at the key it sounds higher: struck hard, the Hamburg's E3 to
A♯3 stood 34 to 42 dB over their recorded neighbours somewhere from 2 to
16 kHz, New York's G3 to G♯4 13 to 21 dB. Each such partial now sounds no
louder than the louder neighbour at its frequency, and they stand 16 to 22
and 6 to 10 dB over
([upper partials](../research/network-key-upper-partials-2026-11-10.md)).
The recorded pitches play as before; the Hamburg's dev takes, keys the fit
never saw, stand 3.02 tolerance units closer to their recordings over the
eleven measures other than level, New York's 0.28 and the Hamamatsu's 0.04
([Hamburg](../validation/hamburg-network-high-partials-benchmark-2026-11-10.md)).
The grand and the upright are unchanged.

### 0.4.32 — 2026-11-10 — each key's level and balance at its neighbours'

The libraries record a piano one pitch at a time, each with its own
microphone image and gain, and the engine played each pitch so: struck in
turn, the Hamamatsu grand's stereo balance swung by 10 to 13 dB from one key
to the next between E4 and C6, the upright's by up to 10 dB. At every
velocity each key's level and balance now go to its neighbours' median, its
tone and decay as recorded, which the owner chose even where it departs from
the recordings ([key smoothing](../research/key-balance-smoothing-2026-11-10.md)).
The balance's key-to-key jumps fall by a third to three quarters in rms on
every piano and velocity (the Hamamatsu's from 3.2 to 0.8 dB at velocity 80)
and the level's by up to two thirds. The recorded pitches' train takes stand
further from their recordings in balance and level, as chosen; partial
levels stand closer on every piano and role but the Hamburg's dev takes, and
the Hamamatsu's dev takes stand 1.36 tolerance units closer over the eleven
measures other than level
([Hamamatsu](../validation/kawai-key-smoothing-benchmark-2026-11-10.md)).
Each piano's default sound and tube keep their level; thirteen preset
readings moved, which the owner approved. The engine takes 0.28 s to build
where it took 0.05.

### 0.4.31 — 2026-11-10 — the undamped strings under a soft bass note

Every strike sets the undamped strings from F6 up ringing, louder as the
strike plays louder, by a law fitted on the recorded pitches from F♯3 up that
rises or falls with how many octaves a string lies over the key. Far over a
bass key New York's law fell under 0, so 0.4.30 rang those strings louder the
softer the key was struck: its C1, F1 and A♯1 at velocity 13 stood 30 to
49 dB over their recordings from 1.6 to 4 kHz, a bright cluster where the
recordings hold only their floor. A softer blow never rings a string louder,
and 0.4.31 holds the law at 0 where it falls under it
([undamped strings](../research/halo-slope-2026-11-10.md)). On New York's
train takes the paired means summed over the eleven measures other than
level, in tolerance units, stand 4.56 closer and on its dev takes 1.90
closer, 1.52 dB closer in the noise between partials on the train takes and
0.85 dB on the dev takes; F1 and A♯1 stand further in rise by more than a
tolerance ([New York](../validation/newyork-halo-slope-benchmark-2026-11-10.md)).
Holding the law at 1 dB per dB instead stood 1.37 further on the dev takes.
The other four pianos' laws never fall under 0, and they play as before.
Every level stays within its approved reading.

### 0.4.30 — 2026-11-09 — the orders a fit left out of a string's series

A struck string sounds every order of its series, and a fit leaves an order
out where it cannot tell the partial from what sounds beside it; 0.4.29
played nothing there. Each order a series lacks between two it holds now
plays between those two, where the series holds at least as many orders
around the gap as it lacks (How it works). On the Hamamatsu grand, whose fit
lacks the most, the orders a render lacked carried 15 % of its train takes'
error in partial levels and 24 % of its dev takes'; its G♯3 lacked its 12th
to 20th partial ([series orders](../research/series-orders-2026-11-09.md)).
Against 0.4.29 on every train and dev take, the paired means summed over the
eleven measures other than level, in tolerance units, stand closer on every
piano's train takes: the Hamamatsu by 1.34, the upright by 0.15, the Hamburg
by 0.13, New York by 0.11 and the Kakegawa grand by 0.08. On the dev takes
the Hamamatsu stands 0.30 closer and the grand 0.04, the upright and New York
0.05 further and the Hamburg 0.94, all of it one note's noise between
partials. The Hamamatsu's train takes stand 0.46 dB closer in partial levels,
and its G♯3 at velocity 95 4.70 dB from its recording where it stood 14.04.
Four scores stand further by more than a tolerance: the upright's B3 and the
Hamamatsu's E5 in decay, the Hamburg's E3 in noise, and the Hamamatsu's G♯3
at velocity 69 loses its noise score
([Kakegawa grand](../validation/grand-series-orders-benchmark-2026-11-09.md),
[upright](../validation/upright-series-orders-benchmark-2026-11-09.md),
[Hamamatsu](../validation/kawai-series-orders-benchmark-2026-11-09.md),
[Hamburg](../validation/hamburg-series-orders-benchmark-2026-11-09.md),
[New York](../validation/newyork-series-orders-benchmark-2026-11-09.md)).
The grand's held-out evaluation stands where it stood. Filling every gap
instead stood further on three pianos' dev takes, in the sparse upper tails
of their series.

Single notes and chords keep their level, within 0.001 dB in the median of
the factory audit. The 88 keys struck in turn with the pedal down render in
0.5 % more CPU on the grand, 0.3 % more on the upright, 3.3 % more on the
Hamamatsu, 1.6 % more on the Hamburg and 2.5 % more on New York, on the
development machine. One reading then passed its approved level, and the
owner accepted it: the Hamburg's loudest chords through the tube, by 0.03 VU.

### 0.4.29 — 2026-11-09 — the strike's wave reaches the bridge

A key's partials and its knock on the body start when the strike's wave
reaches the bridge, as each piano's recordings show (How it works). The
hammer strikes about an eighth of the string from its near end, and the board
hears the string once the wave has run the other seven eighths: 13.4 ms after
the strike at C1, 2.0 ms at A3. 0.4.28 played the tone at the strike, so from
A0 to C♯1 its band under 400 Hz came in 1 to 3 ms after its band over 2 kHz,
where four pianos' recordings bring it in 11 to 17 ms after; 0.4.29 brings it
in 13 to 15 ms after
([string travel](../research/string-travel-2026-11-09.md)). Against 0.4.28
on every train and dev take, the paired means summed over the eleven measures
other than level, in tolerance units, stand closer on every piano's dev
takes: the Hamamatsu by 0.55, New York by 0.29, the upright by 0.19, the
Hamburg by 0.18 and the Kakegawa grand by 0.02. On the train takes the
Hamburg stands 1.05 closer and the grand 0.04, the upright 0.11 further, New
York 0.33 and the Hamamatsu 0.38. The grand's train bass, A0 to B2, stands
0.32 dB closer in the envelope and 0.25 dB in the attack. Twenty-five scores
stand further by more than a tolerance: fourteen rises, eleven of them from
C4 up, where the wave takes under 2 ms and the envelope stands near the
rise's 90 % line, the grand's F♯5 the most (0.86 to 7.34 ms); eight scores of
the deepest keys, which wait 13 to 16 ms, New York's train C1 attack the most
(7.45 to 9.81 dB); two noises and one coherence
([Kakegawa grand](../validation/grand-string-travel-benchmark-2026-11-09.md),
[upright](../validation/upright-string-travel-benchmark-2026-11-09.md),
[Hamamatsu](../validation/kawai-string-travel-benchmark-2026-11-09.md),
[Hamburg](../validation/hamburg-string-travel-benchmark-2026-11-09.md),
[New York](../validation/newyork-string-travel-benchmark-2026-11-09.md)).
On the grand's held-out evaluation the twelve in-range cases stand 4.950 dB
from their recordings in bands (4.968), 1.676 dB in envelope (1.708) and
4.090 ms in rise (4.038). The hammer's noise and the key landing stay at the
strike.

Chords line up as struck strings do: a chord's notes start at their own waits,
so their coincident partials meet at other phases than before. Single notes
keep their level, and a chord's level moves with its voicing, by up to 8 dB
through the tube for the open fifths E1, B1, E2, B2, E3, and 0.006 dB in the
median of the factory audit's chords. The 88 keys struck in turn with the
pedal down render in 0.7 % less CPU on the grand, the same on the upright,
2.1 % more on the Hamamatsu, 1.0 % less on the Hamburg and 0.3 % less on New
York, on the development machine. The Hamamatsu's output and tube and New
York's tube are re-pinned to what they read on Reason's meter before. Eleven
readings then passed their approved levels, and the owner accepted them: eight
loudest chords by 0.07 to 1.25 VU, and three presets' typical playing by 0.07
to 0.11 VU.

### 0.4.28 — 2026-11-09 — the strike's knock under 400 Hz

The hammer's blow knocks the board and case under 400 Hz as each piano's
recordings do (How it works). The knock was measured from 400 Hz up, so
under it nothing played the blow: aligned at the strike, the train notes from
C6 up stood a median 1 to 12 dB under their recordings from 160 to 315 Hz
over their first 30 ms on every piano, and now stand from 6.0 dB under to
2.5 dB over ([low knock](../research/low-knock-2026-11-09.md)). Against
0.4.27 on every train and dev take, the paired means summed over the eleven
measures other than level, in tolerance units, stand closer on every
piano's train takes and on four pianos' dev takes: the upright by 3.04 and
2.39, New York by 0.13 and 0.63, the Hamamatsu by 0.32 and 0.37, the
Kakegawa grand by 0.11 and 0.14 and the Hamburg's train takes by 0.17. The
upright's 137 train takes stand 0.32 dB closer early, 0.28 dB in stereo
balance and 0.25 dB in the noise. The Hamburg's 8 dev takes stand 1.56
further, 0.21 dB in the attack the most, above all at C♯5, where 0.4.27
already stood over its recordings from 100 to 315 Hz at the softest layers.
Six scores stand further by more than a tolerance: the upright's dev B3
coherence (0.142 to 0.170, one take), four of the Hamamatsu's train scores,
C6's attack the most (4.08 to 4.62 dB), and New York's dev E4 noise (6.26 to
6.93 dB, five takes); New York's train G♯7 sustain at its third layer, which
0.4.27 first measured, is not measured
([Kakegawa grand](../validation/grand-low-knock-benchmark-2026-11-09.md),
[upright](../validation/upright-low-knock-benchmark-2026-11-09.md),
[Hamamatsu](../validation/kawai-low-knock-benchmark-2026-11-09.md),
[Hamburg](../validation/hamburg-low-knock-benchmark-2026-11-09.md),
[New York](../validation/newyork-low-knock-benchmark-2026-11-09.md)). On
the grand's held-out evaluation the twelve in-range cases' bands stand
4.968 dB from their recordings (4.988), closer at four and further at four,
and the other measures move by 0.06 or less in their own units. The bands
under 400 Hz start in their filters' stationary state, so the knock comes up
at its measured rise and not at the filters' build-up, and a mute or a key
let go leaves it ringing at its own decay.

The 88 keys struck in turn with the pedal down render in 0.9 % more CPU on
the grand, 2.9 % more on the upright, 1.4 % more on the Hamamatsu, 0.3 % less
on the Hamburg and 0.5 % less on New York, on the development machine. The
Hamamatsu's tube, which the knock took 0.08 VU louder, is re-pinned to what
it read on Reason's meter before. Six readings then passed their approved
levels, and the owner accepted them: five loudest chords by 0.004 to
0.020 VU, and Felt Upright's typical playing by 0.077 VU.

### 0.4.27 — 2026-11-09 — the recording room

Each piano plays the room it was recorded in (How it works, The room).
Between a strike's partials its recordings hold that room's reverberation,
which 0.4.26 left out: 0.45 s after the strike its floor at 1 to 4 kHz stood
20.6 dB under the Hamburg's train takes and 20.4 dB under New York's, and now
stands 0.5 and 4.8 dB under. Against 0.4.26 on every train and dev take, the
paired means summed over the eleven measures other than level, in tolerance
units, stand closer on all five pianos, train and dev: the Kakegawa grand by
1.05 and 0.88, the upright by 0.29 and 0.19, the Hamamatsu by 0.31 and 0.90,
the Hamburg by 6.73 and 0.29 and New York by 1.65 and 3.10. New York's 17 dev
takes stand 0.47 dB closer early, 0.46 dB in the sustain and 0.42 dB in the
noise; the Hamburg's 40 train takes 1.11 dB/s closer in decay, 0.72 dB in the
sustain and 0.70 dB early. Seventeen scores stand further by more than a
tolerance: the grand's dev D♯7 early (3.87 to 4.49 dB) and train C2 rise
(7.26 to 8.49 ms), eight of the Hamamatsu's, its dev G7 early the most (18.58
to 19.89 dB, one take), five of the Hamburg's coherence and noise scores, and
New York's train F6 early (4.32 to 5.13 dB) and dev E7 tuning (2.15 to
2.92 cents). Four scores 0.4.26 could not measure are measured: three
sustains and the Hamburg's dev E3 noise
([Kakegawa grand](../validation/grand-room-benchmark-2026-11-09.md),
[upright](../validation/upright-room-benchmark-2026-11-09.md),
[Hamamatsu](../validation/kawai-room-benchmark-2026-11-09.md),
[Hamburg](../validation/hamburg-room-benchmark-2026-11-09.md),
[New York](../validation/newyork-room-benchmark-2026-11-09.md)). On the
grand's held-out evaluation the twelve in-range cases' bands stand 4.988 dB
from their recordings (5.117), closer at ten of them, and the harmonic
levels, envelope, decay, pitch and rise move by 0.006 or less in their own
units.

The benchmark now scores only the third-octave bands both spectra have bins
in. Its 40 ms window has none in the 25 Hz band at 44.1 kHz and none in the
20 and 31.5 Hz bands at 48 kHz, which then read −300 dB whatever plays, so
the Hamamatsu's and New York's 44.1 kHz recordings, scored against 48 kHz
renders, took the 30 dB cap there in every take: on 0.4.26 their attack,
early and sustain errors read 0.8 to 1.6 dB and 0.3 to 1.2 dB lower, and the
other pianos' scores do not change. Every comparison above is scored the new
way.

The 88 keys struck in turn with the pedal down render in 5.2 % more CPU on
the grand, 5.0 % more on the upright, 2.8 % more on the Hamamatsu, 1.2 % less
on the Hamburg and 0.5 % more on New York, on the development machine. Five
loudest-chord readings passed their approved levels by 0.002 to 0.006 VU, and
the owner accepted them with 0.4.28's.

### 0.4.26 — 2026-11-09 — the keyboard network retrained, and the treble's unison strings

The keyboard network is trained again with no lane decaying faster than the
fits' fastest at its key and each partial's first 100 ms weighed against the
recordings, and the Hamamatsu's, the Hamburg's and New York's keys between
recorded pitches play it, each piano at the network size and smoothness
whose tables scored best on its never-fitted takes and passed the engine's
tests; the Kakegawa grand and the upright keep their corrections to the
blend, which no setting bettered. Against 0.4.25 on the benchmark's 12
measures, the Hamamatsu's 23 never-fitted takes stand closer on 10, the tuning by 0.61 cents, the rise by 0.48 ms, the decay by
0.42 dB/s, the level by 0.41 dB and the envelope by 0.27 dB, and further on
stereo balance by 0.33 dB and early by 0.003 dB; the Hamburg's 8 closer on 8,
the noise by 1.35 dB, the partial levels by 0.76 dB, the decay by 0.72 dB/s
and the rise by 0.68 ms, and further on 4, the tuning by 1.62 cents (E3's
0.48 to 3.69), the level by 1.41 dB, the attack by 0.32 dB and the sustain by
0.21 dB; New York's 17 closer on 6, the tuning by 0.81 cents, the sustain by
0.32 dB and the partial levels by 0.28 dB, and further on 6, the level by
1.63 dB, the early and the envelope by 0.28 dB and the attack by 0.23 dB
([Hamamatsu](../validation/kawai-network-unisons-benchmark-2026-11-06.md),
[Hamburg](../validation/hamburg-network-unisons-benchmark-2026-11-06.md),
[New York](../validation/newyork-network-unisons-benchmark-2026-11-06.md)).
The network's keys strike about 2.5 dB weaker than the blend over their first
100 ms and ring up to 1.4 dB louder after, and the three pianos' output and
tube levels are re-pinned to what they read on Reason's meter before; that
moves their recorded pitches too, which shows in the level measure, and the
recorded pitches stand further apart from their neighbours (Known gaps). Six
settings were tried on those never-fitted takes, so the figures flatter the
choice; the sealed takes were not opened
([keyboard network](../research/keyboard-network.md#the-third-run)).

From C6 up, the Kakegawa grand, the upright and New York play the unison
strings their partials' lanes leave out, measured on their recordings: each
starts in phase with its partial, sounds through its own two pickups and
takes its power from the partial's lanes. Struck at velocity 90, the grand's
F♯7 keeps 0.76 of its coherence between channels where 0.4.25 kept 0.89 (its
recordings 0.37 to 0.51), and its A7 0.67 where 0.4.25 kept 0.91 (0.68 to
0.77). On the three pianos' never-fitted takes from C6 up the stereo balance
stands 0.57 dB closer, the tuning 0.31 cents and the coherence 0.021, and the
sustain 0.41 dB, the partial levels 0.29 dB and the envelope 0.27 dB further;
ten of the grand's scores at C8, D♯7, A6 and F♯7 stand further by more than a
tolerance, C8's never-fitted sustain the most (16.28 to 17.61 dB)
([unison strings](../research/treble-unisons-2026-11-06.md)). The
Hamamatsu's and the Hamburg's strings, which took their recorded pitches
further from their recordings, are measured and not played. Four undamped
own strings grow with the strike at the slope their own recordings measure:
the grand's F♯7 and A7, the Hamburg's A♯6 and New York's F6
([own string](../research/halo-own-2026-11-05.md#each-pitchs-own-slope-0426)).
On the grand's held-out evaluation only C6 moves, its harmonic levels at
velocity 8 from 2.78 to 2.58 dB.

The 88 keys struck in turn with the pedal down render in 1.7 % more CPU on the
grand, 0.8 % less on the upright, 1.6 % more on the Hamamatsu, 45 % less on
the Hamburg and 9.5 % more on New York, on the development machine. Two
readings passed their approved levels, and the owner accepted them: the
Hamamatsu's loudest chords through the tube, 3.29 VU against 3.20, and Three
Cities' typical playing, −10.43 VU against −10.19.

### 0.4.25 — 2026-11-05 — a fifth less CPU, and lighter chords

The demos take 14 to 33 % less CPU, and the block a chord is struck in up to
a third less: Three Cities' seven-note chord fell from 9.6 to 6.3 ms on the
development machine. Four of the five changes leave every sample as it was;
the felt's damping, now taken by square roots, moves a few thousand samples
of the demos by one 24-bit step (−138.5 dBFS)
([benchmark](../benchmarks/cpu-five-steps-2026-11-05.md)).

### 0.4.24 — 2026-11-05 — the struck key's own undamped string

The strings from F6 up have no dampers, and every strike sets them ringing,
each but the struck key's own, which was left to the key's partials. Where
none of the key's partials lies within 4 Hz of that string's pitch, the
recordings hold a tone there that the engine left out: from F7 up the string
an octave below, undamped too, ringing at its second partial, and below F7 a
string of the key's own unison tuned further off than its partials reach. A
key's strike now rings its own string there, at the level the key's recorded
strikes set and growing with the strike as the other undamped strings do: on
the Kakegawa grand at D♯7, F7 and from F♯7 up, the Hamamatsu at ten keys from
F6 to B7, the Hamburg at thirteen from F♯6 to A♯7 and New York at F6, G♯6 and
from E7 up. The grand's F♯7 and A7 held it 30 to 64 dB under their
recordings and now hold it within −1 to +10 dB of them, their never-fitted
takes within −0.6 to +4.3 dB, and the never-fitted D♯7 3 to 9 dB under, where
0.4.23 left it 27 to 33 dB under. On the grand's never-fitted takes the
benchmark stands closer on all 12 measures, the tuning by 0.08 cents and the
decay by 0.06 dB/s the most; the other pianos move by 0.025 or less, and the
upright, whose partials play all its strings, renders as before, sample for
sample ([grand](../validation/grand-halo-own-benchmark-2026-11-05.md),
[Hamamatsu](../validation/kawai-halo-own-benchmark-2026-11-05.md),
[Hamburg](../validation/hamburg-halo-own-benchmark-2026-11-05.md),
[New York](../validation/newyork-halo-own-benchmark-2026-11-05.md)). The
grand's C8 stands 0.50 cents further in tuning on its train takes, just past
the tolerance: the measure now finds the new string 6 Hz over C8's first
partial, which peaks under the string through the measure's window where
the recordings' peaks over it, as C8 is not calibrated. The Hamamatsu
reads 0.02 VU louder on Reason's meter and every other piano and preset as
before, and the CPU is unchanged within the runs' spread, as the string
rings in the resonator it already had
([own string](../research/halo-own-2026-11-05.md)).

### 0.4.23 — 2026-11-05 — the grand's and the upright's keys between recorded pitches ring on as recorded keys do

The Kakegawa grand's and the upright's keys between two recorded pitches
above the bass break, where both pitches' strings are plain, still blend the
two pitches' fits, and now reshape how each partial decays by a correction
the keyboard network learned from the five pianos' recorded pitches, hiding
them one to three at a time and comparing the blend around them with their
fits. It speeds or slows each partial's decay and moves its level between
its quickly and slowly decaying parts, and keeps each channel's power from
50 to 750 ms where the blend put it; the recorded pitches play their fits as
before. On the never-fitted recordings of the keys it corrects, the grand's
48 takes at D♯3, D♯5 and D♯7 stand closer on 7 of the benchmark's 12
measures, the tone from half a second to three seconds by 0.61 dB, the
envelope by 0.45 dB, the partial levels by 0.28 dB, the decay by 0.23 dB/s
and the rise by 0.14 ms, and further on 5, the tuning by 0.06 cents and the
others by 0.03 or less; the upright's 16 at G♯3, B3, C5 and E6 closer on 9,
the envelope by 0.37 dB, that tone by 0.22 dB and the partial levels by
0.19 dB, and further on 3, by 0.06 or less. No pitch stands further on any
measure by more than its tolerance
([grand](../validation/grand-blend-correction-benchmark-2026-11-05.md),
[upright](../validation/upright-blend-correction-benchmark-2026-11-05.md)).
The grand's sealed takes at D♯4 and D♯6, opened for this version, stand
closer on 9, the partial levels by 0.98 dB, that tone by 0.97 dB, the decay
by 0.91 dB/s and the envelope by 0.87 dB
([sealed](../validation/grand-blend-correction-sealed-2026-11-05.md)); the
upright's at E4 and G♯5 closer on 5, the decay by 0.65 dB/s and the partial
levels by 0.13 dB, and further on 7, the envelope by 0.18 dB and the others
by 0.08 or less, none past a tolerance
([sealed](../validation/upright-blend-correction-sealed-2026-11-05.md)).
Below the break, on the wound strings, the correction took that tone further
from the recordings at all four pitches scored there (the grand's D♯1 and
sealed D♯2, the upright's D♯2 and sealed F♯1), the sealed D♯2's rise and
envelope and F♯1's partial levels, decay and that tone past a tolerance, so
the keys between there blend as before.
The grand reads on Reason's meter as in 0.4.22, and the upright's tube,
which the correction took 0.10 VU quieter, is re-pinned to what it read
before. Three presets then read past their approved levels, the Kakegawa
Grand's and Open Strings' loudest chords by +0.005 and +0.012 VU and Felt
Upright's typical playing by −0.24 VU, and Pop Upright's typical playing,
−0.05 VU off, sits at the edge of its guard; the owner accepted the four as
their approved levels. Typical playing is a median over ninety events: Felt
Upright's moved because F6 struck at velocity 110 now reads 0.49 dB lower
over its loudest 300 ms and sits at the median, where event by event the
upright's presets moved by a median of 0.02 to 0.03 dB.
The Hamamatsu and New York grands, whose keys between it took past a
tolerance at some pitches, blend as before, and the Hamburg keeps the
network's partials ([keyboard network](../research/keyboard-network.md#a-correction-to-the-blend)).

### 0.4.22 — 2026-11-05 — the Hamburg's keys between recorded pitches from the keyboard network

The Hamburg grand's keys between its ten recorded pitches now play the
partials the keyboard network gives them, in place of blending the two
pitches' fits; the recorded pitches play their fits as before. The network
is its first run's, fitted on the train recordings of the five pianos. Each
partial keeps the blend's tuning and rise, its power is moved by what the
fits hold over the network at the pitches around it, and the lanes the
network decays faster than both fits are left out. On the Hamburg's
never-fitted recordings, eight takes of E3 and C♯5, the envelope stands
1.68 dB closer to them, the tone from half a second to three seconds
1.36 dB closer and the decay 0.59 dB/s closer; the tuning stands 0.38 cents
further, the tone of the first 100 ms 0.13 dB and the level 0.31 dB
([benchmark](../validation/hamburg-network-keys-benchmark-2026-11-05.md)).
These keys strike weaker over their first 100 ms than the blend did, 2.3 dB
at velocity 80, so the Hamburg's output is re-pinned 1.9 dB up to the
−8.95 VU it read before, and its loudest chords read 0.9 dB higher, which
the owner accepted as their approved level. On the
other four pianos the network did not bring the never-fitted recordings
closer, and they play as before, sample for sample
([keyboard network](../research/keyboard-network.md#in-the-engine)).

### 0.4.21 — 2026-11-05 — beating in the undamped strings

A unison's strings, a little mistuned and coupled through the bridge, ring as
two components that beat, and so do the undamped strings from F6 up that
every strike sets ringing. Where the recordings decide it, on the Kakegawa
grand's F♯6, A♯6 and C♯7 and the upright's C7, a string's aftersound now
plays as two components 0.83 to 1.62 Hz apart, at the level and phase the
recordings show the second against the first. Under the beat the grand's
three fall 12 to 18 % slower, so that, read as the fit reads a string, they
keep the decay and level it measured. In a phrase let go and left to ring,
the beat changes the sound 7 to 36 dB under what still sounds on the grand
and 37 to 58 dB under on the upright. Every other string, and every string of
the other three pianos, rings as one tone as before
([string beat](../research/halo-beats-2026-11-05.md)).

### 0.4.20 — 2026-11-05 — the action's click

A key let go and the grand's pedal coming up now also click above the body's
modes, as each piano's release recordings show: in each noise band from 1.26
to 16 kHz a burst that builds up with the knock and dies away, at the level,
balance and decay the recordings show at the pitch. On the Kakegawa and
Hamburg grands a key's click stands 4 to 19 dB under its knock, A-weighted,
on the New York grand from 22 dB under to 1 dB over, and the Kakegawa
grand's pedal clicks 1 dB under its knock coming up. The Helsinki upright
clicks in at most three bands, a median 31 dB under its knock; the Hamamatsu
grand, whose release takes hold sounding strings, plays none.
Mechanics scales it with the knocks: at its default the click sits 46 to
72 dB under what still sounds after a key-up, A-weighted
([action click](../research/action-click-2026-11-05.md)).

### 0.4.19 — 2026-11-04 — the upright's pitch glide

A struck string's tension rises with its energy, so it starts sharp and
settles as it decays. The upright's recordings show it, and a key on the
upright now plays sharp in proportion to its partials' power: at velocity
127, 50 ms after the strike, up to 8 cents from A0 to B1, 4.4 from C2 to F3
and under 1.3 from F♯3 up, and at velocity 64 under a cent anywhere. The
other four pianos' recordings do not show one, so they play none
([pitch glide](../research/pitch-glide-2026-11-04.md)).

### 0.4.18 — 2026-11-04 — phantom partials

A key's partials now also sound the lines their square makes, at the sums
and differences of every two of them and the double of each, at the gain
each piano's recordings show at the pitch: 36 to 56 dB under a note at
velocity 100 and 48 to 77 dB under at velocity 40, strongest in forte
attacks. The bass, where the recordings do not decide them, plays none
([phantom partials](../research/phantom-partials-2026-11-04.md)).

### 0.4.17 — 2026-11-04 — the partial floor follows a Brightness move

While Brightness glides, a partial now meets the 120 dB floor on the gain
its chunk plays rather than the one the chunk before ended on, so a move
stops a quiet partial when the setting it passes through would. The demos,
which hold Brightness still, render the same samples as 0.4.16's.

### 0.4.16 — 2026-11-04 — a quarter less CPU on the heaviest demos

A partial now stops once it falls 120 dB under full scale, where it stopped
at 150 dB, and a damper's felt reuses its update while it rests on the
strings. The four heaviest demos execute 22 to 28 % fewer instructions. The
change to their sound stays under −112 dBFS in every 100 ms, and 27 dB under
the music in every third-octave band where the music reaches −90 dBFS
([benchmark](../benchmarks/cpu-trims-2026-11-04.md)).

### 0.4.15 — 2026-11-04 — five pianos, no jump between recorded pitches, no hiss at forte

The Belmont grand is removed at the owner's request, with its preset and its
Build column: Keyra plays the Kakegawa, Hamamatsu, Hamburg and New York grands
and the Helsinki upright, and the factory bank holds twelve presets. A session
saved with Belmont weights loads with them dropped, or with the Kakegawa
grand's part where the Belmont was a part's only piano. A key between two
recorded pitches no longer takes its stereo image from the nearer one, which
switched the image at the midpoint: on the upright the octave partial in the
sum of the channels jumped 7.3 dB from A♯2 to B2, a change of tone at a
Width under 75 %. The image now moves between the two pitches' images, and
recorded pitches sound as before ([decisions](../decisions.md), 2026-11-04).
Each partial of such a key also keeps its power in each channel between the
two pitches' from 50 to 750 ms, and its components decay at rates between
theirs: the Hamamatsu's A♯7 and B7 no longer ring their second partial 20 dB
or more over A7 and C8. Against the recordings, the keys between recorded
pitches sit 0.02 to 0.56 dB further from them in partial level, and closer in
late decay on four pianos, by up to 0.48 dB/s, but 0.24 dB/s further on the
Hamamatsu ([decisions](../decisions.md), 2026-11-04).
Forte notes no longer ring a hiss over their partials for half a second, the
fault reported at the Hamamatsu's C4 struck at 127. The noise between the
partials is now measured from the recordings by the median in every band, as
it already was under the fundamental, and so passes over the phantom partials
a hard strike adds there ([decisions](../decisions.md), 2026-11-04).
A chord's notes now add at other angles and the keys between recorded
pitches read differently on Reason's meter, so each piano's output and tube
are re-pinned to keep its default sound and its tube at their earlier
readings: a recorded pitch's partials play 0.07 dB quieter on the Kakegawa
grand, 0.24 on the upright, 0.20 on the Hamburg and 0.36 on the New York, and
0.14 dB louder on the Hamamatsu, and one note through the tube alone moves
+0.23, +0.46, −0.40, −0.63 and +0.09 dB. Against 0.4.14's approved levels,
Felt Upright's typical playing is 0.44 dB louder, every other preset's within
0.12 dB, and four presets' loudest chords up to 0.16 dB higher, which the
owner accepted as the new approved levels.

### 0.4.14 — 2026-11-03 — chords sound as their notes do

Notes struck in the same instant now keep the per-key level trim that evens
out the keyboard (below C7 it was skipped for them, so a chord lost the trims
of every note while the same notes a sample apart kept them), and a chord
shares one verdict for the late body ring's reduction in quick passages
instead of giving it to the first note alone. A fifteen-note chord struck at
once now sums to its notes struck alone to −38 dB, where it was −29 dB;
the fix itself leaves single notes unchanged byte for byte. Because the
levels contract plays chords, the upright's and the Kawai's output scales are
re-pinned by +0.27 and +0.48 dB (a single note of either is that much louder)
and the Belmont's tube trim eased by 0.03 dB, to keep their default sound and
tube at the approved readings; Studio Grand, Open Strings and Felt Upright read 0.06 to 0.16 dB
lower and Three Cities 0.21 dB higher
([decisions](../decisions.md), 2026-11-03). Steady partials and the body's
banks are summed four at a time, which makes the engine 14 to 22 % cheaper
per second of audio on the factory demos with identical output.

### 0.4.13 — 2026-11-03 — 88-key tonal balance

Recorded here from its commit, which carried no write-up. Keys whose level sits
off the trend of their neighbours get a small per-key trim; the top octaves'
body and noise follow gentler slopes per piano; the undamped strings' levels
are capped against their median on the five pianos other than the grand; the
action's level is eased between anchors; the strings the sustain pedal sets
ringing play at a new scale.

### 0.4.12 — 2026-11-03 — restrikes and sympathetic resonance

Recorded here from its commit, which carried no write-up. A key struck again
while it still sounds plays with less body ring and colour, so the second
strike stays clear; a note struck soon after another rings less late on the
body; sympathetic resonance and the receivers' dampers were reworked, and the
engine's CPU use reduced.

### 0.4.11 — 2026-11-02 — more contrast on hard chords

All six pianos use the approved B response at the usual Output setting of 0.70.
Typical playing keeps its level. In the 480-pair factory chord test, striking
at velocity 127 after 110 now gives a median 1.40 dB rise, up from 0.29 dB.
The stereo peak ceiling is −1.5 dBFS and the plug-in reports 120 frames of
latency at 48 kHz. [Listening choice and measurements](../validation/forte-response-2026-11-02.md).

### 0.4.10 — 2026-11-02 — damper motion on all six pianos

When the player releases a key or moves the sustain pedal, strings ringing in
sympathy now follow the same felt travel as struck strings. Repeating a note
lifts the damper off its remaining vibration by the time the hammer strikes
again. Each piano keeps its measured tuning, voicing and decay. See the
[all-six comparison and recording checks](../validation/damper-travel-2026-11-02.md).

### 0.4.9 — 2026-11-02 — brighter Belmont factory preset

The Belmont Grand preset now starts with Brightness at 75%, following the
owner's C audition choice. Existing saved settings retain their brightness.

### 0.4.8 — 2026-11-02 — local Belmont reconstruction repairs

Belmont recovers missing sustain around C5 and A5 from its source measurements,
while retaining the accepted voicing and Mechanics default. These are local
repairs with documented neighboring-note and quiet-tail tradeoffs, not a new
global brightness setting. See the [measurement evidence](../research/belmont-conditional-update-2026-11-02.md).

### 0.4.7 — 2026-11-01 — smoother controls and quieter soft releases

Live Brightness, Resonance and piano-build changes now transition smoothly.
Balanced and Light quality retain harmonics that can become audible when
Brightness increases after a strike. Quiet key releases follow the played-note
level more closely, while the Mechanics default remains at 40% and all six
piano voicings retain their character. Saved sounds receive these behavior
fixes; parameter identities and ranges are unchanged.
[Validation and remaining limits](../validation/whole-keyboard-quality-2026-11-01.md).

### 0.4.6 — 2026-11-01 — clearer Belmont dynamics

Belmont now retains its measured soft-strike tone without the additional
velocity darkening, following the owner's C listening choice. Its recorded
velocity layers remain expressive, and the other five measured pianos keep
their voicing. Saved Belmont sounds also receive this change; parameter IDs
and ranges are unchanged.
Its tube-mic monitoring level is trimmed by 0.352 dB after the output guard
to retain the existing level limits; the stereo-pair output is unchanged.

### 0.4.5 — 2026-11-01 — quieter, adjustable mechanics

New instruments use the quieter B action balance chosen in the Moonlight
listening test. The Mechanics knob places that setting at **40%**, with finer
travel at quiet levels, silence at 0% and the existing maximum at 100%.
Saved settings and host automation keep their previous sound. The piano's
hammer/body attack and measured character are unchanged
([listening decision](../decisions.md#2026-11-01--quieter-key-landing-action-in-the-moonlight-performance)).
Universal macOS builds, control/state tests, exact B render parity and VST3/CLAP
validation pass ([validation record](../validation/mechanics-default-2026-11-01.md)).

### 0.4.4 — 2026-11-01 — development snapshot: consistent soft-pedal interpolation

A grand’s soft-pedal weighting now follows the fitted components between
measured notes and dynamics. Crossing decay rates no longer abruptly exchange
those weights. The owner preferred this change in Belmont’s upper and bass
phrases ([listening decision](../decisions.md#2026-11-01--moms-baby-grand-soft-pedal-interpolation)).
Measured endpoints, soft-pedal-off playback and the upright’s half-blow action
are preserved. Some intermediate notes change level or rise time; this does
not claim uniform improvement or continuity for every mixed piano. The 0.4.3
reset fix is retained.

The combined build passes native unit/audio/performance and VST3/CLAP checks;
the [validation record](../validation/calibration-followups-2026-11-01.md#soft-pedal-interpolation--accepted-locally-in-044)
documents keyboard parity, remaining tradeoffs and host coverage.

### 0.4.3 — 2026-11-01 — development snapshot: clean reset after changing piano

A hard reset immediately after changing piano now starts with the selected
soundboard's pickups. It no longer carries the previous piano's unfinished
pickup transition into the next note. Live piano changes retain their smooth
transition; the measured sound and interpolation are unchanged
([validation](../validation/calibration-followups-2026-11-01.md#hard-reset-after-changing-piano--accepted-locally-in-043)).

### 0.4.2 — 2026-11-01 — development snapshot: interpolation between recorded notes and dynamics

- Repairs selected cancellation dips and overshoots between velocity layers,
  while preserving the recorded layers. Between keys, unidentified decay rates
  have less influence without introducing an endpoint discontinuity. All six
  pianos have lower mean held-out decay error; individual regressions and
  remaining uneven notes are documented in the
  [recording and keyboard validation](../validation/realism-baseline-and-trials-2026-11-01.md).

### 0.4.1 — 2026-11-01 — development snapshot: measured strings, body and board noise

- Recalibrated from 264 recordings (every A, C and F♯ from A0 to A7 at twelve
  velocities) instead of ten. Each partial has four measured decay lanes with
  their own beating and left/right balance, starts from the phase pattern the
  recordings show at string contact and rises no faster than its pitch's
  recorded onset.
- Every strike knocks a body of 91 measured soundboard and case modes and
  starts a burst of board noise in 13 bands, measured for its pitch, so
  repeated notes differ as real strikes do. The felt mute damps the strings,
  and the ring stops with them once every sounding string is damped; the top
  strings, which have no dampers, keep it ringing. The knock grows about decibel
  for decibel with the level the strike's layer plays at, as the
  recordings' does: soft notes knocked the body 5 to 6 dB louder than
  theirs, and now about 1 dB, which brings the attack spectrum 0.1 dB
  (grand) and 0.4 dB (upright) closer to the calibration notes
  ([grand](../validation/grand-knock-benchmark-2026-10-29.md),
  [upright](../validation/upright-knock-benchmark-2026-10-29.md)). Under a
  top note's fundamental the noise is measured past the other strings' tones
  there, which it used to take for noise ringing on, so the upright's top
  octave no longer leaves a hiss ringing for seconds
  ([grand](../validation/grand-treble-noise-benchmark-2026-10-29.md),
  [upright](../validation/upright-treble-noise-benchmark-2026-10-29.md)).
  There the ring falls in two stages, as the recordings' does: a fast one
  over the first tenth of a second, then on the grand one of 40 to 57 dB/s,
  so from C6 up the 1 to 2.5 kHz region under the fundamental no longer
  drops 4 to 52 dB under the recordings within 0.8 s but stays within about
  5 dB of them
  ([grand](../validation/grand-board-ring-benchmark-2026-10-29.md),
  [upright](../validation/upright-board-ring-benchmark-2026-10-29.md)).
  The body's modes fall in two stages too: from 0.4 s after the strike each
  rings on at its own slower rate, on the grand a median 13 to 22 dB/s by
  region where one rate measured over the first 0.4 s played it at 70 to
  100 dB/s. Under the notes from C4 up the body from 25 Hz to 1 kHz no
  longer falls 5 to 35 dB under the recordings between 0.4 and 1.5 s but
  stays within 2 to 11 dB of them, and the grand's sustain spectrum sits
  0.3 dB closer to them (treble 0.9 dB)
  ([grand](../validation/grand-body-tail-benchmark-2026-10-29.md),
  [upright](../validation/upright-body-tail-benchmark-2026-10-29.md)).
- From F♯4 up (G♯4 on the upright) a strike knocks from the moment the hammer
  meets the strings: band noise in up to 17 third-octave bands from 400 Hz to
  16 kHz, at the level and decay measured for its pitch, layer and band over
  the first 35 ms after contact, falling at a median 480 to 900 dB/s by pitch,
  where the recordings stood 5 to 16 dB over everything the engine played
  between the partials. Below, the fit finds too little of it in the gaps
  between the partials to play. The grand's attack spectrum sits 0.24 dB
  closer to its calibration notes and 0.16 dB to the never-fitted ones (its
  treble 0.62 and 0.32 dB), its noise between partials 0.12 and 0.09 dB, and
  the upright's attack 0.07 and 0.09 dB. F♯6, F♯7 and A7 now reach their peak
  in about 5 ms, sooner than their recordings' 6.6 to 10.8 ms
  ([grand](../validation/grand-knock-from-contact-benchmark-2026-10-30.md),
  [upright](../validation/upright-knock-from-contact-benchmark-2026-10-30.md)).
- A strike no longer clicks. Each rise started on a corner that put 8 to
  20 dB more than the recordings from 8 to 22 kHz into the first 5 ms of the
  grand's bass and middle notes; smoothed over 0.1 ms, as a felt hammer
  presses in, it sits within 3 dB of them, and the grand's noise between
  partials sits 1.2 dB closer to its calibration notes and 0.8 dB to the
  never-fitted ones
  ([grand](../validation/grand-onset-smoothing-benchmark-2026-10-29.md)).
- Both pianos answer velocity alike, at the owner's request: a velocity asks
  for a level under the loudest recorded layer, halfway between a straight
  line and an S-curve, and plays the layer coordinate where that piano's
  recordings reach it, so its tone is the one recorded at that loudness.
  Velocity 127 plays each piano's loudest layer, which it used to play past,
  and velocity 1 the grand's softest, 21 dB under it. The two pianos' median
  notes now sit within 1 dB of each other at every velocity, where the
  upright's sat up to 10 dB under the grand's, and from velocity 64 to 127
  the median key grows 10.6 dB on the grand and 9.9 dB on the upright (it
  grew 8.4 and 17.4). The upright's softest layer, 6 dB further under its
  loudest than the grand's, no longer plays on its own.
- No two strikes land alike: each plays a little harder or softer than its
  velocity, as a player's do, by the spread the upright library's new
  second strikes measure, 1.085 dB of level on every key, the harder one
  the brighter. Repeated chords change level and colour from strike to
  strike; tuning does not, as those strikes keep their pitch within
  0.02 cents.
- Both pianos play 11.5 dB louder, at the level of the portfolio's newer
  instruments: typical playing on the default controls reads −9 VU on
  Reason's channel meter at the default Output. The portfolio's shared output
  stage replaces the clip at full scale: its guard keeps the loudest chords
  out of the red and its look-ahead limiter every sample under −1.5 dBFS,
  for 2 ms of latency, which the plug-in reports. Single notes pass it
  untouched; it takes a median 1.3 dB from the grand's chords at velocity
  110 and 3.5 dB from the upright's. The felt presets read 7 to 9 dB lower
  (below).
- A Quality choice trades detail for CPU on slower machines, at the owner's
  request. Full, the default, plays every partial; Balanced and Light leave
  out a strike's partials and components 60 and 50 dB under its strongest,
  which moves no third-octave band of a note by more than 0.04 and 0.74 dB.
  Legato chords under the pedal take 49 and 38 % of Full's CPU on the
  grand; the upright, which plays fewer partials, saves up to 13 %. Quality
  stays with the session, not the preset.
- Beside its partials, a strike plays the components the recordings hold
  between them, 48 at A0 and a few or none from C4 up, and sets ringing every
  undamped string from F6 up but its own key's, each at its own measured
  pitch, decay and stereo position, at the level the recorded pitches around
  the key set it. They ring on after the key is let go. Each starts with its
  own prompt part, which a struck unison sounds before its aftersound and the
  bridge drains within a few tenths of a second: in their first quarter
  second the strings that ring clear sit a median 2 to 4 dB under the grand's
  recordings, where they sat 5 to 8 dB under, and 2 to 8 dB under the
  upright's, where they sat 5 to 11 dB under.
- The undamped strings grow with the strike as the recordings' do. Fitted only
  where they ring clear, which in soft layers only the loudest strings do,
  they grew too slowly, so soft strikes rang strings the recordings leave
  under the noise: at the two softest layers of the grand's never-fitted
  notes 17 and 25 % of them rang 10 dB or more over the recordings a second
  after the strike, and the upright's F♯3 at velocity 51 rang G♯6 27.6 dB
  over. The fit now takes a hidden string's tone as a bound, and the strings
  grow faster than the level the strike's layer plays at, the faster the
  further they lie over the struck note: those shares are now none and 6 %,
  2.7 % of the grand's never-fitted strings at every layer (6.0 %), and G♯6
  rings 1.7 dB over
  ([grand](../validation/grand-halo-velocity-benchmark-2026-10-29.md),
  [upright](../validation/upright-halo-velocity-benchmark-2026-10-29.md)).
- The strings whose dampers are off ring in sympathy at their own partials:
  each key from A0 to E6 rings its first eight where its strike plays them,
  so a C4 under the pedal sets C3's second partial and F2's third ringing,
  and they decay as Salamander's pedal-down recording measures, 2.8 dB/s at
  middle C and a third faster per octave up, where one resonator per key at
  its fundamental decayed three times as fast at middle C. Pressing the pedal
  sets the freed strings ringing as the dampers lift, as the recording does:
  the ring against the pedal's knock sits 2.7 dB per band from the train take
  and 2.8 dB from the never-fitted one, where it sat 55 and 60 dB from them
  ([pedal benchmark](../validation/grand-open-strings-benchmark-2026-10-30.md)).
  The upright has no pedal recordings: its strings ring at the grand's rates
  and its pedal lifts none.
- A key between two recorded pitches plays about as loud as they do. Its
  partials' lanes were blended one by one and, with offsets, phases and
  stereo pickups neither pitch has, beat and cancelled where neither pitch's
  do: the grand's B4 sat about 4 dB under both its neighbours and the
  upright's B3 3 to 4.7 dB. Each blended partial's power over its first second
  now sits between the two pitches' in dB. At five velocities no key plays
  more than 2.8 dB outside the levels of the recorded pitches around it, and
  at most 4 of the grand's 63 such keys and 5 of the upright's 52 more than
  1 dB, where up to 16 and 18 did. The grand's never-fitted D♯ pitches sit up
  to 0.8 dB closer to their recordings' level; the upright's recordings are
  less even from note to note, and four of its five never-fitted pitches sit
  0.3 to 0.9 dB further from theirs
  ([grand](../validation/grand-between-pitches-benchmark-2026-10-28.md),
  [upright](../validation/upright-between-pitches-benchmark-2026-10-28.md)).
- A key between two recorded pitches keeps its partials between theirs in
  the stereo image. Their channels' phase difference was blended while their
  phases came from the nearer pitch, so the lanes met in the right channel at
  phases neither pitch has and cancelled there: D♯5's third partial on the
  grand and its second on the upright sat 4.6 and 6 dB further to one side
  than either neighbour. The phase difference now comes from the nearer
  pitch with the phases. At velocity 64 the share of blended partials beyond
  both pitches' balance falls from 29 to 24 % on the grand and 24 to 20 % on
  the upright, the furthest from 12.5 to 7.7 dB and 11.7 to 7.2 dB. The
  never-fitted pitches' image moves 4.97 to 4.74 dB from their recordings on
  the grand and 4.53 to 4.26 dB on the upright; the grand's D♯3 moves 6.84 to
  7.73 dB
  ([grand](../validation/grand-stereo-between-pitches-benchmark-2026-10-31.md),
  [upright](../validation/upright-stereo-between-pitches-benchmark-2026-10-31.md)).
  Warm Walnut plays a touch brighter (0.30, was 0.28) to stay within 2 dB of
  typical playing's −9 VU.
- A key between two recorded pitches pairs each partial's lanes by the share
  of the partial they carry, where it paired them fastest first. Where one
  pitch's fit holds a lane the other's lacks, that order met the lane that
  carries a partial with one that carries little, and the key between them
  rang the partial with a decay and a stereo position neither neighbour has:
  on a refit D♯3's second partial sat 6.3 dB nearer the middle than either.
  The pairing changes 433 of the grand's 733 blended partials and 286 of the
  upright's 498, most in the bass. On the grand's never-fitted pitches level
  sits 1.07 dB from the recordings (was 1.20) and the treble's decay
  3.08 dB/s (3.37); the sustain spectrum moves 5.25 to 5.31 dB
  ([grand](../validation/grand-lane-roles-benchmark-2026-10-31.md),
  [upright](../validation/upright-lane-roles-benchmark-2026-10-31.md)).
- Each recorded pitch keeps the energy its strings hold in the recordings.
  The fit left part of a partial in its residual where its lanes cannot
  follow the unison strings' beating, so some keys played quieter than their
  recordings: the grand's F♯7 by about 3 dB, the upright's A♯6 and E7
  fundamentals by 3 to 8 dB. Each partial's lanes are now scaled to the
  energy its strings hold over the first 0.75 s. On the recordings it is
  fitted from, the grand's notes sit 0.50 dB from their loudness (was 0.69)
  and the upright's 0.51 dB (0.87), on the grand's never-fitted ones 0.96 dB
  (1.07); the upright's E7 moves from 4.5 to 1.5 dB off and the grand's F♯7
  from 2.0 to 0.8 dB. C8 and the keys up to it play A7's louder
  fundamental, a step further from C8's recordings
  ([grand](../validation/grand-string-energy-benchmark-2026-10-31.md),
  [upright](../validation/upright-string-energy-benchmark-2026-10-31.md)).
- A key between two recorded pitches meets their levels over the 50 to
  750 ms its levels are measured over, where it met them over its power from
  contact, which counted a burst dying within 50 ms for its whole energy and
  put the Hamamatsu grand's F♯6 4.3 dB over both its neighbours. On the
  never-fitted recordings the Kakegawa grand's partial levels sit 5.33 dB
  from them (was 5.39) and its level 1.01 dB (0.94), and no note of it or of
  the Helsinki upright moves past the benchmark's tolerance, while the
  Hamamatsu grand's F♯7 and B5 sit 2.0 and 0.6 dB further from their
  recordings' level
  ([Kakegawa](../validation/grand-between-window-benchmark-2026-10-31.md),
  [Helsinki](../validation/upright-between-window-benchmark-2026-10-31.md),
  [Hamamatsu](../validation/kawai-between-window-benchmark-2026-10-31.md)).
- Letting a key go knocks the body as its damper lands, and the sustain pedal
  knocks it going down and coming up, synthesized on the body's modes: each
  mode's level and phase is measured from the library's release and pedal
  recordings, and the knocks sit against the notes as the library's SFZ mixes
  them, since the recordings carry no level of their own.
- A Mechanics control sets how loud the action plays, from silent to twice as
  loud: the keys landing and coming back, the dampers falling, the sustain
  pedal's knocks and the strings its going down sets ringing.
- A Tube Mic control moves the listener from each piano's stereo pair to a
  vintage tube microphone at shin height, mono, its colour measured from the
  Helsinki library's tube and ribbon takes of the same strikes: against its
  midrange it hears more deep bass and top and less of 250 to 315 Hz and
  1.3 kHz. Between, the two are mixed. Through it typical playing reads
  −9 VU on both pianos, as through the pair.
- The action's knocks ring as the release recordings' do, each body mode
  falling 1.5 times as fast as the board's own ring of it whatever the
  dampers do, and a key lands with its strike, as an impact. Ringing on the
  board's own ring, the landing boomed under the treble: 0.1 to 0.5 s after
  the strike the grand's notes from C6 up stood a median 5 to 7 dB over their
  recordings at 200 and 250 Hz and the upright's 5 to 6 dB at 80 and 100 Hz,
  now 1 to 2 dB. The keys play as loud as before in their first 100 ms,
  except that a key let go from F6 up, which has no damper, no longer rings
  on where the felt cut the knock below it: up to 11 dB quieter. The sustain
  pedal's knock now stands against the strings it frees as Salamander's
  pedal-down takes' does, about 3 dB louder than before ([grand](../validation/grand-action-decay-benchmark-2026-10-30.md),
  [upright](../validation/upright-action-decay-benchmark-2026-10-30.md),
  [pedal](../validation/grand-action-decay-pedal-benchmark-2026-10-30.md)).
- The body no longer rings a strike's knock on as its own. Fitted from 20 ms
  after contact, the soundboard's modes took up the knock, which falls far
  faster than they do, and kept ringing it: the upright's treble sounded
  boxy, its notes from C6 up standing a median 3.4 to 8.3 dB over their
  recordings from 400 Hz to 800 Hz 0.1 to 0.5 s after the strike. Where the
  knock is measured, the modes are now fitted after it, from 45 ms, and the
  knock plays from 400 Hz up where it started at 630 Hz: those bands stand
  2.1 to 4.5 dB over, and the attack spectrum moves closer on both pianos
  with no note further from its recordings than the benchmark's tolerance
  ([grand](../validation/grand-body-after-knock-benchmark-2026-10-30.md),
  [upright](../validation/upright-body-after-knock-benchmark-2026-10-30.md)).
  The cost is under the treble's fundamental: from 400 to 800 Hz its image
  narrows, its side up to 5 dB further under its mid, and the grand's 500 Hz
  to 1 kHz sits 0.4 to 1.2 dB further under its recordings from 0.1 to
  0.5 s.
- Full sustain pedal rings as 80 % of the pedal did, at the owner's request:
  the dampers stop short of clearing the strings, so the felt grazes them,
  and a chord of C3, C4, C5 and C6 let go under it falls 60 dB in 8.7 s on the
  grand and 11.2 s on the upright, where it rang on past 30 s. The strings
  the pedal frees are grazed by the same felt, so the ring it sets going down
  falls 9.6 dB/s where Salamander's pedal-down takes fall 6.8 and 7.0
  ([pedal benchmark](../validation/grand-pedal-lift-benchmark-2026-10-30.md)),
  and half pedalling lets them ring as far as it lets the struck strings,
  where it all but silenced them.
- The upright's soft pedal works as an upright's does (half-blow): it brings
  the hammers halfway to the strings, so a strike plays as one √½ as fast,
  quieter and darker, on every string of its unison. At middle C, velocity
  100, it takes 6.8 dB off and moves the spectral centroid from 296 to
  268 Hz, where the grand's una corda it played before moved it to 293 Hz.
- Existing sessions sound different. On the 156 never-fitted cases of the
  [recording benchmark](../validation/grand-recording-benchmark-2026-10-29.md),
  partial levels sit 3.1 dB from the recordings (0.3.0: 9.8 dB), the attack
  spectrum 4.2 dB (15.8 dB), the sustain spectrum 4.6 dB (10.2 dB) and the
  noise between partials 6.3 dB (24.7 dB); its regressions, C4's and F♯4's
  onset rise first, are listed there.
- Adds an upright beside the grand, with three presets (Helsinki Upright,
  Felt Upright, Pop Upright): a 1967
  upright with worn hammers in a dry room, measured the grand's way from 137
  recordings of the Helsinki 1967 Tube-Ribbon Edition (Mikko Patama, with his
  permission; none of its recordings is distributed). Sessions saved before
  keep the grand. On the [upright's benchmark](../validation/upright-recording-benchmark-2026-10-28.md)
  its attack, tuning and level sit closer to its never-fitted recordings than
  the grand's data does; its treble does not yet (Known gaps). From C6 up its
  unison strings sound up to 20 cents from their partial: its first fit took
  those beyond the partial's lanes, which reached about 3 cents, for the
  partial's own and left them out, so its treble tails fell too fast. The
  lanes now reach about 10 cents where the recordings hold strings that far
  out, and the strings beyond them play beside the partials. On the
  never-fitted E6 the partials sit 6.8 dB from the recordings instead of 8.9,
  their decay 8.2 dB/s instead of 13.9 and the sustain spectrum 10.1 dB
  instead of 15.1 ([unisons](../validation/upright-unison-benchmark-2026-10-28.md),
  [reach](../validation/upright-lane-reach-benchmark-2026-10-28.md)). The
  grand's lanes reach as far: its never-fitted treble's decay sits 3.3 dB/s
  from the recordings instead of 4.5, and F♯6's envelope 5.3 dB instead of
  2.2 ([grand](../validation/grand-lane-reach-benchmark-2026-10-28.md)).
- Notes end alike on both pianos, at the owner's ear: under the felt a
  small leftover of each partial at −46 dB at middle C, and the body's ring
  stops with the strings once the dampers are down (the top strings, which
  have none, keep it ringing), so one second after release both sit about 48
  to 60 dB under the note. The upright no longer rings on for seconds.
- The upright speaks sooner: none of its partials rises slower than the
  hammer stays on the string, 2 ms at middle C and shorter higher up, where
  they had swelled over up to 116 ms.
- The keys are heard: a key going down knocks the body about 30 dB under a
  velocity-80 note and a key coming up about 32 dB under it, on both pianos.
- Velocity changes the tone more than the recordings' layers alone: softer
  strikes are darker and the hardest keep their brightness, at the same
  loudness. Middle C's spectral centroid from velocity 20 to 120 now spans
  349 to 711 Hz on the grand and 265 to 472 Hz on the upright.
- Adds a third piano, a second grand, measured the same way from 131
  recordings of VCSL Keys' Grand Piano K (Versilian Studios, CC0): a stereo
  pair in player position at four velocity layers. On its never-fitted
  recordings its tuning, attack, noise between partials, rise and level sit
  closer to them than the first grand's data does, and its partial levels,
  decay, image and envelope further (Known gaps)
- Adds two more grands, each with a preset after Three Cities: Hamburg Grand
  (program 11), from the Decent Sampler "Steinway Grand" by Jon Meyer, and New
  York Grand (program 12), from Pianobook's "Grandpa's Piano" by David Hawkins.
  The first three pianos, their blends and
  every demo render sample for sample as before. Hamburg's data sits closer to
  its never-fitted recordings than the first grand's in tuning, attack, noise,
  rise and level and further in partial levels and decay, New York's closer but
  for decay
  ([Hamburg](../validation/hamburg-recording-benchmark-2026-10-31.md),
  [New York](../validation/newyork-recording-benchmark-2026-10-31.md))
  ([benchmark](../validation/kawai-recording-benchmark-2026-10-31.md)).
- Adds a sixth piano, Belmont Grand (program 13), from Pianobook's "Mom's 1974
  Baby Grand" by The Imperfect Drummer (Brian Peat), a 1974 Knabe baby grand,
  with its keys let go and its sustain pedal going down and coming up. Its
  library normalises every take, so its three layers are levelled by Decent
  Sampler's own velocity curve and each note by a smooth trend over the
  keyboard: a choice, not a measurement. The other pianos, their blends and
  every demo render sample for sample as before. On its never-fitted
  recordings its data sits closer to them than the first grand's in partial
  levels, tuning, attack, spectra, noise and level and further in decay,
  envelope and rise
  ([benchmark](../validation/belmont-recording-benchmark-2026-11-01.md)).
- The soundboard no longer rings the strings' leftovers. Fitted with only the
  modes within 4 Hz of a recorded pitch's partials left out, the modes 4 to
  30 Hz from them took up what the partials' fit left of the strings, 10 to
  18 dB over their knock elsewhere, and rang it a few hertz off the note: a
  rough, noisy haze around each recorded pitch, worst in the middle register,
  that stacked into fixed tones under chords. A pitch now leaves out the modes
  within a semitone of its partials and takes their knock from its measured
  neighbours, one rule over the keyboard: the body's share of Hamamatsu's C4
  falls from −19 to −30 dB under the partials, and the key-to-key steps over
  3 dB in it go from 2 to none on Kakegawa, 5 to 1 on Hamamatsu, 1 to none
  on New York and 11 to 4 on Helsinki. Lines that hardly fall are no longer
  taken for modes: New York's at 704 Hz, which every strike set ringing for
  14 s, Hamburg's at C♯2, D♯2 and D3, and Helsinki's at 147 Hz (7.4 s) and
  198 Hz (4 s), which beat against its D3 and G3. The body's onset rise is
  matched on shape, so it no longer makes up for the partials' leftovers
  (Kakegawa 0.31 to 0.83 ms, Hamamatsu 0.38 to 1.24, New York 0.38 to 0.43,
  Hamburg 1.43 to 1.86, Helsinki 0.29 to 0.49). On their recordings Kakegawa,
  Hamamatsu, New York and Helsinki's dev notes hold; Hamburg's early spectrum
  moves 0.8 dB and its noise between partials 0.7 dB further off, since its
  recordings hold the three lines, and Helsinki's train treble 0.7 dB in its
  early and sustained spectra. Helsinki's D4 now starts sharper than its
  recording (onset rise 4 to 24 ms off): the modes beside its partials had
  cancelled part of the partials' too-fast attack
  ([Kakegawa](../validation/grand-soundboard-partials-benchmark-2026-11-01.md),
  [Hamamatsu](../validation/kawai-soundboard-partials-benchmark-2026-11-01.md),
  [New York](../validation/newyork-soundboard-partials-benchmark-2026-11-01.md),
  [Hamburg](../validation/hamburg-soundboard-partials-benchmark-2026-11-01.md),
  [Helsinki](../validation/upright-soundboard-partials-benchmark-2026-11-01.md)).
- The pianos are builds of one model, at the owner's request. A Build view
  beside the voicing knobs mixes the measured pianos part by part: the
  strings, hammers, soundboard and action each take a share of every piano,
  so the first grand with the upright's hammers, a piano halfway between or
  one with something of all three plays. Halfway between the first grand and
  the upright each key sits within 0.9 dB of between their levels, and at
  equal thirds of the three within 1.4 dB of between the three's. Stiffness,
  Unisons and Ring scale the strings' inharmonicity, unison spread and decay.
  The measured pianos play as before, and a build plays from the next note
  while what sounds rings on. The voicing knob that read Hammer reads
  Brightness, beside the build's Hammers. A Strings setting between pianos
  keeps their stereo image, between theirs; at first every one of them played
  in mono.
- The pianos go by cities, at the owner's request, and so do their presets:
  the first grand is the Kakegawa grand, the upright the Helsinki upright and
  the new grand the Hamamatsu grand. Concert Grand is now Kakegawa Grand and
  Rehearsal Upright Helsinki Upright, at their program numbers; Hamamatsu
  Grand plays the new grand and Three Cities every part at equal thirds of
  the three. A preset sets the build and the voicing, and the Piano control
  is gone: a session saved with it opens as the build it chose.
- Adds the CLAP plug-in on every platform beside VST3, the standalone
  application and, on macOS, the Audio Unit.
- The repository root is the product only. The full physical piano research
  moved to [`Experiments/`](../../Experiments/README.md), its own CMake project that
  the product build does not build.

### 0.2.0 — 2026-10-26 — native instrument

- The real-time modal piano with five presets, three visible pedals,
  momentary pedal keyswitches on MIDI 12–14, continuous pedal depth and
  modulation-wheel felt muting, as a VST3 plug-in and a standalone
  application. Details are in the
  [native wrapper validation](../validation/native-wrapper-2026-10-26.md).
