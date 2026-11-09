# Keyra

Keyra is a sample-free piano: a real-time modal engine whose strings,
soundboard ring and stereo image are fitted from numerical measurements of
acoustic piano recordings, with three visible pedals, momentary pedal
keyswitches and felt muting from the modulation wheel. Five pianos are
measured, four grands and an upright, and their strings, hammers, soundboard
and action mix part by part into pianos none of them is. It builds as VST3
and CLAP plug-ins, an Audio Unit on macOS and a standalone application, and
the Reason Rack Extension adapter plays the same engine. It is a development
candidate: host acceptance and a commercial release are still to come.

![Keyra](Docs/screenshots/keyra.png)

## Audio demos

One phrase per factory preset, written for what that preset is for and
rendered from `Docs/audio/midi/` through the shipping engine.

<!-- audio-demos-begin -->

| # | Preset | Demo | Length | Peak |
| --- | --- | --- | --- | --- |
| 1 | Kakegawa Grand | [01-kakegawa-grand.wav](Docs/audio/01-kakegawa-grand.wav) | 11.2 s | -1.5 dBFS |
| 3 | Warm Walnut | [03-warm-walnut.wav](Docs/audio/03-warm-walnut.wav) | 11.1 s | -12.1 dBFS |
| 4 | Felt Nocturne | [04-felt-nocturne.wav](Docs/audio/04-felt-nocturne.wav) | 10.7 s | -15.5 dBFS |
| 5 | Open Strings | [05-open-strings.wav](Docs/audio/05-open-strings.wav) | 11.7 s | -1.5 dBFS |
| 6 | Helsinki Upright | [06-helsinki-upright.wav](Docs/audio/06-helsinki-upright.wav) | 11.6 s | -1.5 dBFS |
| 8 | Pop Upright | [08-pop-upright.wav](Docs/audio/08-pop-upright.wav) | 11.6 s | -1.5 dBFS |
| 9 | Hamamatsu Grand | [09-hamamatsu-grand.wav](Docs/audio/09-hamamatsu-grand.wav) | 9.7 s | -3.8 dBFS |
| 10 | Three Cities | [10-three-cities.wav](Docs/audio/10-three-cities.wav) | 10.8 s | -1.5 dBFS |

<!-- audio-demos-end -->

### Listening against the recordings

The [live renders](Docs/audio/live/manifest.json) are earlier musical passages
through the same engine, frozen evidence from 0.2.0's review. The recording
comparisons that set Salamander notes beside the fits were removed on
2026-10-31 so the repository holds no recordings;
`Tools/make_recording_comparisons.py --output-dir <dir>` rebuilds them outside
the checkout from a fetched copy of the library.

## Version history

### 0.4.28 — 2026-11-09 — the strike's knock under 400 Hz

The hammer's blow knocks the board and case under 400 Hz as each piano's
recordings do (How it works). The knock was measured from 400 Hz up, so
under it nothing played the blow: aligned at the strike, the train notes from
C6 up stood a median 1 to 12 dB under their recordings from 160 to 315 Hz
over their first 30 ms on every piano, and now stand from 6.0 dB under to
2.5 dB over ([low knock](Docs/research/low-knock-2026-11-09.md)). Against
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
([Kakegawa grand](Docs/validation/grand-low-knock-benchmark-2026-11-09.md),
[upright](Docs/validation/upright-low-knock-benchmark-2026-11-09.md),
[Hamamatsu](Docs/validation/kawai-low-knock-benchmark-2026-11-09.md),
[Hamburg](Docs/validation/hamburg-low-knock-benchmark-2026-11-09.md),
[New York](Docs/validation/newyork-low-knock-benchmark-2026-11-09.md)). On
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
([Kakegawa grand](Docs/validation/grand-room-benchmark-2026-11-09.md),
[upright](Docs/validation/upright-room-benchmark-2026-11-09.md),
[Hamamatsu](Docs/validation/kawai-room-benchmark-2026-11-09.md),
[Hamburg](Docs/validation/hamburg-room-benchmark-2026-11-09.md),
[New York](Docs/validation/newyork-room-benchmark-2026-11-09.md)). On the
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
([Hamamatsu](Docs/validation/kawai-network-unisons-benchmark-2026-11-06.md),
[Hamburg](Docs/validation/hamburg-network-unisons-benchmark-2026-11-06.md),
[New York](Docs/validation/newyork-network-unisons-benchmark-2026-11-06.md)).
The network's keys strike about 2.5 dB weaker than the blend over their first
100 ms and ring up to 1.4 dB louder after, and the three pianos' output and
tube levels are re-pinned to what they read on Reason's meter before; that
moves their recorded pitches too, which shows in the level measure, and the
recorded pitches stand further apart from their neighbours (Known gaps). Six
settings were tried on those never-fitted takes, so the figures flatter the
choice; the sealed takes were not opened
([keyboard network](Docs/research/keyboard-network.md#the-third-run)).

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
([unison strings](Docs/research/treble-unisons-2026-11-06.md)). The
Hamamatsu's and the Hamburg's strings, which took their recorded pitches
further from their recordings, are measured and not played. Four undamped
own strings grow with the strike at the slope their own recordings measure:
the grand's F♯7 and A7, the Hamburg's A♯6 and New York's F6
([own string](Docs/research/halo-own-2026-11-05.md#each-pitchs-own-slope-0426)).
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
([benchmark](Docs/benchmarks/cpu-five-steps-2026-11-05.md)).

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
sample ([grand](Docs/validation/grand-halo-own-benchmark-2026-11-05.md),
[Hamamatsu](Docs/validation/kawai-halo-own-benchmark-2026-11-05.md),
[Hamburg](Docs/validation/hamburg-halo-own-benchmark-2026-11-05.md),
[New York](Docs/validation/newyork-halo-own-benchmark-2026-11-05.md)). The
grand's C8 stands 0.50 cents further in tuning on its train takes, just past
the tolerance: the measure now finds the new string 6 Hz over C8's first
partial, which peaks under the string through the measure's window where
the recordings' peaks over it, as C8 is not calibrated. The Hamamatsu
reads 0.02 VU louder on Reason's meter and every other piano and preset as
before, and the CPU is unchanged within the runs' spread, as the string
rings in the resonator it already had
([own string](Docs/research/halo-own-2026-11-05.md)).

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
([grand](Docs/validation/grand-blend-correction-benchmark-2026-11-05.md),
[upright](Docs/validation/upright-blend-correction-benchmark-2026-11-05.md)).
The grand's sealed takes at D♯4 and D♯6, opened for this version, stand
closer on 9, the partial levels by 0.98 dB, that tone by 0.97 dB, the decay
by 0.91 dB/s and the envelope by 0.87 dB
([sealed](Docs/validation/grand-blend-correction-sealed-2026-11-05.md)); the
upright's at E4 and G♯5 closer on 5, the decay by 0.65 dB/s and the partial
levels by 0.13 dB, and further on 7, the envelope by 0.18 dB and the others
by 0.08 or less, none past a tolerance
([sealed](Docs/validation/upright-blend-correction-sealed-2026-11-05.md)).
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
network's partials ([keyboard network](Docs/research/keyboard-network.md#a-correction-to-the-blend)).

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
([benchmark](Docs/validation/hamburg-network-keys-benchmark-2026-11-05.md)).
These keys strike weaker over their first 100 ms than the blend did, 2.3 dB
at velocity 80, so the Hamburg's output is re-pinned 1.9 dB up to the
−8.95 VU it read before, and its loudest chords read 0.9 dB higher, which
the owner accepted as their approved level. On the
other four pianos the network did not bring the never-fitted recordings
closer, and they play as before, sample for sample
([keyboard network](Docs/research/keyboard-network.md#in-the-engine)).

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
([string beat](Docs/research/halo-beats-2026-11-05.md)).

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
([action click](Docs/research/action-click-2026-11-05.md)).

### 0.4.19 — 2026-11-04 — the upright's pitch glide

A struck string's tension rises with its energy, so it starts sharp and
settles as it decays. The upright's recordings show it, and a key on the
upright now plays sharp in proportion to its partials' power: at velocity
127, 50 ms after the strike, up to 8 cents from A0 to B1, 4.4 from C2 to F3
and under 1.3 from F♯3 up, and at velocity 64 under a cent anywhere. The
other four pianos' recordings do not show one, so they play none
([pitch glide](Docs/research/pitch-glide-2026-11-04.md)).

### 0.4.18 — 2026-11-04 — phantom partials

A key's partials now also sound the lines their square makes, at the sums
and differences of every two of them and the double of each, at the gain
each piano's recordings show at the pitch: 36 to 56 dB under a note at
velocity 100 and 48 to 77 dB under at velocity 40, strongest in forte
attacks. The bass, where the recordings do not decide them, plays none
([phantom partials](Docs/research/phantom-partials-2026-11-04.md)).

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
([benchmark](Docs/benchmarks/cpu-trims-2026-11-04.md)).

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
recorded pitches sound as before ([decisions](Docs/decisions.md), 2026-11-04).
Each partial of such a key also keeps its power in each channel between the
two pitches' from 50 to 750 ms, and its components decay at rates between
theirs: the Hamamatsu's A♯7 and B7 no longer ring their second partial 20 dB
or more over A7 and C8. Against the recordings, the keys between recorded
pitches sit 0.02 to 0.56 dB further from them in partial level, and closer in
late decay on four pianos, by up to 0.48 dB/s, but 0.24 dB/s further on the
Hamamatsu ([decisions](Docs/decisions.md), 2026-11-04).
Forte notes no longer ring a hiss over their partials for half a second, the
fault reported at the Hamamatsu's C4 struck at 127. The noise between the
partials is now measured from the recordings by the median in every band, as
it already was under the fundamental, and so passes over the phantom partials
a hard strike adds there ([decisions](Docs/decisions.md), 2026-11-04).
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
([decisions](Docs/decisions.md), 2026-11-03). Steady partials and the body's
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
latency at 48 kHz. [Listening choice and measurements](Docs/validation/forte-response-2026-11-02.md).

### 0.4.10 — 2026-11-02 — damper motion on all six pianos

When the player releases a key or moves the sustain pedal, strings ringing in
sympathy now follow the same felt travel as struck strings. Repeating a note
lifts the damper off its remaining vibration by the time the hammer strikes
again. Each piano keeps its measured tuning, voicing and decay. See the
[all-six comparison and recording checks](Docs/validation/damper-travel-2026-11-02.md).

### 0.4.9 — 2026-11-02 — brighter Belmont factory preset

The Belmont Grand preset now starts with Brightness at 75%, following the
owner's C audition choice. Existing saved settings retain their brightness.

### 0.4.8 — 2026-11-02 — local Belmont reconstruction repairs

Belmont recovers missing sustain around C5 and A5 from its source measurements,
while retaining the accepted voicing and Mechanics default. These are local
repairs with documented neighboring-note and quiet-tail tradeoffs, not a new
global brightness setting. See the [measurement evidence](Docs/research/belmont-conditional-update-2026-11-02.md).

### 0.4.7 — 2026-11-01 — smoother controls and quieter soft releases

Live Brightness, Resonance and piano-build changes now transition smoothly.
Balanced and Light quality retain harmonics that can become audible when
Brightness increases after a strike. Quiet key releases follow the played-note
level more closely, while the Mechanics default remains at 40% and all six
piano voicings retain their character. Saved sounds receive these behavior
fixes; parameter identities and ranges are unchanged.
[Validation and remaining limits](Docs/validation/whole-keyboard-quality-2026-11-01.md).

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
([listening decision](Docs/decisions.md#2026-11-01--quieter-key-landing-action-in-the-moonlight-performance)).
Universal macOS builds, control/state tests, exact B render parity and VST3/CLAP
validation pass ([validation record](Docs/validation/mechanics-default-2026-11-01.md)).

### 0.4.4 — 2026-11-01 — development snapshot: consistent soft-pedal interpolation

A grand’s soft-pedal weighting now follows the fitted components between
measured notes and dynamics. Crossing decay rates no longer abruptly exchange
those weights. The owner preferred this change in Belmont’s upper and bass
phrases ([listening decision](Docs/decisions.md#2026-11-01--moms-baby-grand-soft-pedal-interpolation)).
Measured endpoints, soft-pedal-off playback and the upright’s half-blow action
are preserved. Some intermediate notes change level or rise time; this does
not claim uniform improvement or continuity for every mixed piano. The 0.4.3
reset fix is retained.

The combined build passes native unit/audio/performance and VST3/CLAP checks;
the [validation record](Docs/validation/calibration-followups-2026-11-01.md#soft-pedal-interpolation--accepted-locally-in-044)
documents keyboard parity, remaining tradeoffs and host coverage.

### 0.4.3 — 2026-11-01 — development snapshot: clean reset after changing piano

A hard reset immediately after changing piano now starts with the selected
soundboard's pickups. It no longer carries the previous piano's unfinished
pickup transition into the next note. Live piano changes retain their smooth
transition; the measured sound and interpolation are unchanged
([validation](Docs/validation/calibration-followups-2026-11-01.md#hard-reset-after-changing-piano--accepted-locally-in-043)).

### 0.4.2 — 2026-11-01 — development snapshot: interpolation between recorded notes and dynamics

- Repairs selected cancellation dips and overshoots between velocity layers,
  while preserving the recorded layers. Between keys, unidentified decay rates
  have less influence without introducing an endpoint discontinuity. All six
  pianos have lower mean held-out decay error; individual regressions and
  remaining uneven notes are documented in the
  [recording and keyboard validation](Docs/validation/realism-baseline-and-trials-2026-11-01.md).

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
  ([grand](Docs/validation/grand-knock-benchmark-2026-10-29.md),
  [upright](Docs/validation/upright-knock-benchmark-2026-10-29.md)). Under a
  top note's fundamental the noise is measured past the other strings' tones
  there, which it used to take for noise ringing on, so the upright's top
  octave no longer leaves a hiss ringing for seconds
  ([grand](Docs/validation/grand-treble-noise-benchmark-2026-10-29.md),
  [upright](Docs/validation/upright-treble-noise-benchmark-2026-10-29.md)).
  There the ring falls in two stages, as the recordings' does: a fast one
  over the first tenth of a second, then on the grand one of 40 to 57 dB/s,
  so from C6 up the 1 to 2.5 kHz region under the fundamental no longer
  drops 4 to 52 dB under the recordings within 0.8 s but stays within about
  5 dB of them
  ([grand](Docs/validation/grand-board-ring-benchmark-2026-10-29.md),
  [upright](Docs/validation/upright-board-ring-benchmark-2026-10-29.md)).
  The body's modes fall in two stages too: from 0.4 s after the strike each
  rings on at its own slower rate, on the grand a median 13 to 22 dB/s by
  region where one rate measured over the first 0.4 s played it at 70 to
  100 dB/s. Under the notes from C4 up the body from 25 Hz to 1 kHz no
  longer falls 5 to 35 dB under the recordings between 0.4 and 1.5 s but
  stays within 2 to 11 dB of them, and the grand's sustain spectrum sits
  0.3 dB closer to them (treble 0.9 dB)
  ([grand](Docs/validation/grand-body-tail-benchmark-2026-10-29.md),
  [upright](Docs/validation/upright-body-tail-benchmark-2026-10-29.md)).
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
  ([grand](Docs/validation/grand-knock-from-contact-benchmark-2026-10-30.md),
  [upright](Docs/validation/upright-knock-from-contact-benchmark-2026-10-30.md)).
- A strike no longer clicks. Each rise started on a corner that put 8 to
  20 dB more than the recordings from 8 to 22 kHz into the first 5 ms of the
  grand's bass and middle notes; smoothed over 0.1 ms, as a felt hammer
  presses in, it sits within 3 dB of them, and the grand's noise between
  partials sits 1.2 dB closer to its calibration notes and 0.8 dB to the
  never-fitted ones
  ([grand](Docs/validation/grand-onset-smoothing-benchmark-2026-10-29.md)).
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
  ([grand](Docs/validation/grand-halo-velocity-benchmark-2026-10-29.md),
  [upright](Docs/validation/upright-halo-velocity-benchmark-2026-10-29.md)).
- The strings whose dampers are off ring in sympathy at their own partials:
  each key from A0 to E6 rings its first eight where its strike plays them,
  so a C4 under the pedal sets C3's second partial and F2's third ringing,
  and they decay as Salamander's pedal-down recording measures, 2.8 dB/s at
  middle C and a third faster per octave up, where one resonator per key at
  its fundamental decayed three times as fast at middle C. Pressing the pedal
  sets the freed strings ringing as the dampers lift, as the recording does:
  the ring against the pedal's knock sits 2.7 dB per band from the train take
  and 2.8 dB from the never-fitted one, where it sat 55 and 60 dB from them
  ([pedal benchmark](Docs/validation/grand-open-strings-benchmark-2026-10-30.md)).
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
  ([grand](Docs/validation/grand-between-pitches-benchmark-2026-10-28.md),
  [upright](Docs/validation/upright-between-pitches-benchmark-2026-10-28.md)).
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
  ([grand](Docs/validation/grand-stereo-between-pitches-benchmark-2026-10-31.md),
  [upright](Docs/validation/upright-stereo-between-pitches-benchmark-2026-10-31.md)).
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
  ([grand](Docs/validation/grand-lane-roles-benchmark-2026-10-31.md),
  [upright](Docs/validation/upright-lane-roles-benchmark-2026-10-31.md)).
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
  ([grand](Docs/validation/grand-string-energy-benchmark-2026-10-31.md),
  [upright](Docs/validation/upright-string-energy-benchmark-2026-10-31.md)).
- A key between two recorded pitches meets their levels over the 50 to
  750 ms its levels are measured over, where it met them over its power from
  contact, which counted a burst dying within 50 ms for its whole energy and
  put the Hamamatsu grand's F♯6 4.3 dB over both its neighbours. On the
  never-fitted recordings the Kakegawa grand's partial levels sit 5.33 dB
  from them (was 5.39) and its level 1.01 dB (0.94), and no note of it or of
  the Helsinki upright moves past the benchmark's tolerance, while the
  Hamamatsu grand's F♯7 and B5 sit 2.0 and 0.6 dB further from their
  recordings' level
  ([Kakegawa](Docs/validation/grand-between-window-benchmark-2026-10-31.md),
  [Helsinki](Docs/validation/upright-between-window-benchmark-2026-10-31.md),
  [Hamamatsu](Docs/validation/kawai-between-window-benchmark-2026-10-31.md)).
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
  pedal-down takes' does, about 3 dB louder than before ([grand](Docs/validation/grand-action-decay-benchmark-2026-10-30.md),
  [upright](Docs/validation/upright-action-decay-benchmark-2026-10-30.md),
  [pedal](Docs/validation/grand-action-decay-pedal-benchmark-2026-10-30.md)).
- The body no longer rings a strike's knock on as its own. Fitted from 20 ms
  after contact, the soundboard's modes took up the knock, which falls far
  faster than they do, and kept ringing it: the upright's treble sounded
  boxy, its notes from C6 up standing a median 3.4 to 8.3 dB over their
  recordings from 400 Hz to 800 Hz 0.1 to 0.5 s after the strike. Where the
  knock is measured, the modes are now fitted after it, from 45 ms, and the
  knock plays from 400 Hz up where it started at 630 Hz: those bands stand
  2.1 to 4.5 dB over, and the attack spectrum moves closer on both pianos
  with no note further from its recordings than the benchmark's tolerance
  ([grand](Docs/validation/grand-body-after-knock-benchmark-2026-10-30.md),
  [upright](Docs/validation/upright-body-after-knock-benchmark-2026-10-30.md)).
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
  ([pedal benchmark](Docs/validation/grand-pedal-lift-benchmark-2026-10-30.md)),
  and half pedalling lets them ring as far as it lets the struck strings,
  where it all but silenced them.
- The upright's soft pedal works as an upright's does (half-blow): it brings
  the hammers halfway to the strings, so a strike plays as one √½ as fast,
  quieter and darker, on every string of its unison. At middle C, velocity
  100, it takes 6.8 dB off and moves the spectral centroid from 296 to
  268 Hz, where the grand's una corda it played before moved it to 293 Hz.
- Existing sessions sound different. On the 156 never-fitted cases of the
  [recording benchmark](Docs/validation/grand-recording-benchmark-2026-10-29.md),
  partial levels sit 3.1 dB from the recordings (0.3.0: 9.8 dB), the attack
  spectrum 4.2 dB (15.8 dB), the sustain spectrum 4.6 dB (10.2 dB) and the
  noise between partials 6.3 dB (24.7 dB); its regressions, C4's and F♯4's
  onset rise first, are listed there.
- Adds an upright beside the grand, with three presets (Helsinki Upright,
  Felt Upright, Pop Upright): a 1967
  upright with worn hammers in a dry room, measured the grand's way from 137
  recordings of the Helsinki 1967 Tube-Ribbon Edition (Mikko Patama, with his
  permission; none of its recordings is distributed). Sessions saved before
  keep the grand. On the [upright's benchmark](Docs/validation/upright-recording-benchmark-2026-10-28.md)
  its attack, tuning and level sit closer to its never-fitted recordings than
  the grand's data does; its treble does not yet (Known gaps). From C6 up its
  unison strings sound up to 20 cents from their partial: its first fit took
  those beyond the partial's lanes, which reached about 3 cents, for the
  partial's own and left them out, so its treble tails fell too fast. The
  lanes now reach about 10 cents where the recordings hold strings that far
  out, and the strings beyond them play beside the partials. On the
  never-fitted E6 the partials sit 6.8 dB from the recordings instead of 8.9,
  their decay 8.2 dB/s instead of 13.9 and the sustain spectrum 10.1 dB
  instead of 15.1 ([unisons](Docs/validation/upright-unison-benchmark-2026-10-28.md),
  [reach](Docs/validation/upright-lane-reach-benchmark-2026-10-28.md)). The
  grand's lanes reach as far: its never-fitted treble's decay sits 3.3 dB/s
  from the recordings instead of 4.5, and F♯6's envelope 5.3 dB instead of
  2.2 ([grand](Docs/validation/grand-lane-reach-benchmark-2026-10-28.md)).
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
  ([Hamburg](Docs/validation/hamburg-recording-benchmark-2026-10-31.md),
  [New York](Docs/validation/newyork-recording-benchmark-2026-10-31.md))
  ([benchmark](Docs/validation/kawai-recording-benchmark-2026-10-31.md)).
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
  ([benchmark](Docs/validation/belmont-recording-benchmark-2026-11-01.md)).
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
  ([Kakegawa](Docs/validation/grand-soundboard-partials-benchmark-2026-11-01.md),
  [Hamamatsu](Docs/validation/kawai-soundboard-partials-benchmark-2026-11-01.md),
  [New York](Docs/validation/newyork-soundboard-partials-benchmark-2026-11-01.md),
  [Hamburg](Docs/validation/hamburg-soundboard-partials-benchmark-2026-11-01.md),
  [Helsinki](Docs/validation/upright-soundboard-partials-benchmark-2026-11-01.md)).
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
  moved to [`Experiments/`](Experiments/README.md), its own CMake project that
  the product build does not build.

### 0.2.0 — 2026-10-26 — native instrument

- The real-time modal piano with five presets, three visible pedals,
  momentary pedal keyswitches on MIDI 12–14, continuous pedal depth and
  modulation-wheel felt muting, as a VST3 plug-in and a standalone
  application. Details are in the
  [native wrapper validation](Docs/validation/native-wrapper-2026-10-26.md).

## Downloads

<!-- build-download-begin -->
**[Download main build 87](https://github.com/protocodus/virtual-instrument-keyra/actions/runs/42624775200/artifacts/13678433728)**, built from [`8f008da3f9f7`](https://github.com/protocodus/virtual-instrument-keyra/commit/8f008da3f9f7884997aa37c18f224487bca96344). It holds the macOS, Windows and Linux packages, `SHA256SUMS` and `BUILD.txt`.
<!-- build-download-end -->

---

## How it works

### The modal engine

`Source/DSP/KeyraEngine` is front-end-neutral C++17 with no allocation, I/O or
locks in its event and render calls; the plug-in and the Rack adapter both
compile it. Each struck key becomes one voice of up to 128 stiff-string
partials (128 voices; when they run out, a released tail goes before the
oldest held note). Every partial has four lanes, each a decaying rotation with
its own rate, small frequency offset and stereo pickup: together they make a
note's prompt fall, the beating of its unison strings, its slow aftersound and
the way its balance moves between the microphones. A partial starts from the
phase the recordings show at string contact and rises from zero, never faster
than its pitch's recorded onset builds up and, on the upright, never slower
than the hammer stays on the string (2 ms at middle C, halving every two
octaves up), and like the body's knock without a corner: every rise is smoothed over 0.1 ms, as a felt hammer presses in. The lanes run four to a 128-bit
vector in single precision, restarted every 32 samples from a double-precision
state, so long notes keep their exact decay.

Every piano answers velocity alike. A strike plays at a coordinate between
its piano's recorded layers, each layer at the velocity its library maps to
it: a velocity asks for a level under the loudest layer, halfway between a
straight line and smoothstep from velocity 1 to 127, and the strike plays
where the piano's layers reach that level, so its tone is the one recorded
at that loudness. A layer's level is its early level under the same pitch's
loudest layer (both channels' RMS from 50 to 750 ms after the onset), the
median over the pitches recorded at every layer. Velocity 127 plays each
piano's loudest layer, and velocity 1 the grand's softest, 21.2 dB under it,
which the upright and the Hamamatsu grand reach between their two softest
layers. Single keys keep their recordings' differences: at one velocity a
key of the upright sits from 4 dB under to 7 dB over the same key of the
grand (the tenth to the ninetieth percentile), where the median notes of the
two sit within 0.4 dB of each other at velocities 30, 64, 100 and 127, and
the Hamamatsu grand's within 0.6 dB of the grand's, but 1.4 dB over it at
velocity 30.

No two strikes land alike. Each plays a little harder or softer than its
velocity asks: its level moves by a random amount with a spread of 1.085 dB,
which the upright library's new second strikes measure (below), and it plays
the layer coordinate at that level, so a repeated chord changes level and
colour from strike to strike, and keeps its tuning. A spread in velocity
units instead would follow each layer's level slope, which at the upright's
loudest layers is twice the measured layers', and so double it there. The
draws restart with the engine, so a render replays exactly.

Beside its series, a strike plays the components the recordings hold between
the partials, each one lane placed by the series and damped with it; in the
treble they include the unison strings that sound further from their partial
than its lanes reach. They
start at contact under the pitch's onset rise and share vectors four lanes to
a slot, so a component costs a quarter of a partial.

From C6 up, the Kakegawa grand, the upright and New York also play the
unison strings that their recorded pitches' lanes leave out and that no
component beside the series holds, measured on their train takes by
`Tools/fit_treble_unisons.py` into `Source/DSP/MeasuredTrebleUnisons.h`
([notes](Docs/research/treble-unisons-2026-11-06.md)): each string two lanes
at its own distance from its partial, a quick early fall and a slow ring,
heard through its own two pickups and spread by the unisons modifier. The
hammer sets a unison's strings off together, so each starts in phase with
its partial's lanes as they sum at contact, and the strings take their power
from those lanes: over 50 to 750 ms the lanes and the strings together, the
beating between every two of them counted, hold the power the fit gave the
lanes alone. A key between two recorded pitches plays both pitches' strings
at their shares. The Hamamatsu's and the Hamburg's strings are measured and
not played, as their recorded pitches stood further from their recordings
with them.

A string's tension grows with the square of its displacement, so its
partials also sound lines at the sums and the differences of every two of
their frequencies and at the double of each (phantom partials). The engine
adds, in each channel, the square of a key's partials there, all its
sounding strikes together, through the output's DC high-pass. The lines grow
with the square of a strike's amplitude, so they are strongest in forte
attacks and fade about twice as fast as the partials. Their gain is each
piano's at the pitch, measured on its train takes and played between the
recorded pitches around a key: it puts them 36 to 56 dB under a note at
velocity 100 and 48 to 77 dB under at velocity 40. The takes decide it from
F♯2 (C2 on the upright, A♭2 on the New York grand, A2 on the Hamburg) up to
A6 on the grand, E5 on the upright, C5 on the Hamamatsu, F♯4 on the Hamburg
and F6 on the New York; beyond them it fades to none
([phantom partials](Docs/research/phantom-partials-2026-11-04.md)).

A string's mean tension rises with the square of its slope, so a struck
string plays sharp and settles as it decays (pitch glide). The upright's
train takes show it: from 50 ms to a second after the onset, a loud take
glides in proportion to how much its partials' power falls, by a law that
grows 2.4 times per octave down. A key on the upright plays sharp by that law
times its partials' power, and its voices retune whenever the key's glide
has moved by 0.05 cents; at velocity 127 a C1 is 7.9 cents sharp 50 ms after
the strike and 3.2 cents at 0.35 s. The other four pianos' takes do not
decide a glide, so they play none, and the open strings do not glide
([pitch glide](Docs/research/pitch-glide-2026-11-04.md)).

Every strike also knocks the body: a bank of 91 soundboard and case modes from
29 to 945 Hz, shared by every key, each ringing in two stages that add, a fast
one over the first 0.4 s and then one about a fifth as fast, so the body
lasts a second or two, with each stage's level and phase measured for each
recorded pitch; the knock grows about decibel for decibel with the level the
strike's layer plays at.
Above the modes, the board's dense ring is band noise in 13 third-octave bands
from 1 to 16 kHz, each a sixth-order band-pass so that the quiet top octaves
keep their measured level: each strike starts its own burst with the density,
decay and left/right balance measured for its pitch. Under a treble note's
fundamental the burst falls in two stages that add in power, the second
slower and quieter. From F♯4 up (G♯4 on the upright) the same burst carries
the strike's knock, in up to 17 bands from 400 Hz to 16 kHz: from contact, at
the density, decay and balance measured for its pitch and layer, falling
faster than the ring, mostly within a few tens of milliseconds. Under 400 Hz
the burst carries the knock in five more bands, 125 to 315 Hz, on the keys
whose recorded pitches lie a third of an octave and more over a band, where
none of their partials sounds: the board's and case's answer to the blow,
which the body's modes, fitted after it, leave out. Each band rises and
decays as measured for its piano, at a level measured for each recorded
pitch and layer, and starts in its filters' stationary state, as a band-pass
long fed by its noise stands, so that the knock comes up at its own rise and
not at the filters'. No string keeps it up, so a mute or a key let go leaves
it ringing at its own decay, as the knock above 400 Hz does: from 0.2 to
0.7 s after a staccato C5 is let go, it and the room's echo of it stand 44 to
68 dB under the note.

The undamped strings from F6 up ring with every strike, whatever the
Resonance control: each but the struck key's own, at the level the recorded
pitches around the key set it, and each at its own measured pitch, decay and
stereo pickup whichever key struck it. The struck key's own string rings too
where none of the key's partials lies within 4 Hz of its pitch: from F7 up,
where the string an octave below is undamped too, that string's second
partial, which the strike sets ringing through the bridge, and below F7 a
string of the key's own unison tuned further off than its lanes reach. It
rings at the level the key's own recorded strikes set, with no prompt part,
and between pianos at the share of the hammers of those whose takes ring it.
It grows with the strike as the other undamped strings do, but where three
or more of a pitch's recorded layers ring it clear of its partials it grows
at the slope those layers measure: on the Kakegawa grand's F♯7 and A7, the
Hamburg's A♯6 and New York's F6
([own string](Docs/research/halo-own-2026-11-05.md#each-pitchs-own-slope-0426)).
Each of the others starts with its own prompt part,
as a struck unison does, that is gone within a few tenths of a second: at
contact from too little to hear up to 25 dB over the string's own on the
grand and up to 17 dB on the upright, falling at 103 and 75 dB/s. Where a
piano's recordings decide it, a string's aftersound is two components a
little apart, which beat, as a coupled unison's strings do: on the Kakegawa
grand's F♯6, A♯6 and C♯7, 0.89, 1.62 and 0.83 Hz apart, the second 5.2,
10.9 and 1.1 dB under the first, and on the upright's C7, 0.99 Hz apart and
5.2 dB under, each at the phase the recordings show at contact. Both fall at
one rate, at which, read through the fit's windows from 1 to 2 s, they fall
as the fit measured the string: on the grand 12 to 18 % slower than the rate
it gave the string as one tone. The unisons modifier spreads a string's beat
as it spreads a strike's. They ring on after the key is let go; the felt mute
damps them. The damped strings, A0 to E6, ring in sympathy as far as their
dampers are off, under the sustain pedal or a held key, at the level the
Resonance control sets: each key's first eight partials under 5 kHz, at the
frequencies a strike of that key plays them, driven by the piano's output at
unity gain at resonance and heard at the key's place in the image. A key's own
strikes do not drive its string: they are its sound. They decay at the rate
the grand's pedal-down recording measures for their frequency, 0.32/s at
middle C (2.8 dB/s) and a third faster per octave up, and the pedal going down
sets the strings it frees ringing, at the level per third-octave band that
recording rings them with; under full pedal's grazing felt
(**Pedals and keyswitches**) they fall faster than its strings do.

A strike's tone moves with velocity beyond its layer: each partial gains
0.4 dB per octave of its order (up to four) for every decibel its layer plays
over the layer at velocity 100, and loses as much below it, and the strike's
partials are then rescaled to the energy the layer plays, so velocity moves
the colour without moving the level.

Once a key is let go, the felt leaves the same small share on every piano,
the upright's measured leftover shape at −46 dB at middle C, and while every
damped key is down the body's modes damp at the felt's rate for their
frequency, so the board stops with the strings.

The action knocks the same modes, each falling 1.5 times as fast as the
board's own ring of it whatever the dampers do, as the release recordings'
knocks fall. A key going down knocks them with its strike, about 28 dB under a
velocity-80 note at C2, C4 and C6 (30 dB on the upright), growing with the
strike's layer. A key let go knocks them as its damper lands, building up over
the 152 ms the release recordings show (91 ms on the upright) rather than
at once, and quieter the longer the key was held; under the sustain pedal or
sostenuto no damper falls and the key-up is silent, while from F6 up, where
there is no damper, the key's own return knocks them whatever the pedals do.
The sustain pedal knocks them going down and coming up. Above the modes, from
1.26 to 16 kHz, a key let go and the Kakegawa grand's pedal coming up also
click: in each noise band, the burst the piano's release takes hold at the
pitch, building up under the knock's rise and mixed between the recorded
pitches as the knock's modes are. The Hamamatsu grand plays none, as its
release takes hold sounding strings. The Mechanics control
scales every knock and click of the action, and the ring the pedal sets going
down, from silent at 0% to raw gain 2 at 100%. The quieter default, raw gain 0.175, sits at
40% on a continuous tapered knob. The action levels above describe raw gain 1;
the separate hammer/body attack is not scaled by Mechanics.

### Five pianos, one model

The pianos are builds of one model (`keyra::Build`): the Kakegawa grand
(Salamander's), the Helsinki upright, the Hamamatsu grand (VCSL Keys'),
and the Hamburg and New York grands, each fitted from its own recordings. Elsewhere in this document the grand is
the Kakegawa grand and the upright the Helsinki upright. Each of the model's
four parts mixes the measured pianos by a weight from 0 to 1 for each of
them (`keyra::Mix`), played as shares of their sum: the **strings** (their
stretch and stiffness, unison offsets, decays and pickups, the undamped top
strings and the components beside the series), the **hammers** (how hard
each partial is struck and how fast it rises, the components' levels, the
tone's change with velocity), the **soundboard** (the body's modes, a
strike's knock on them and the board's noise) and the **action** (the knocks
of keys, dampers and pedals). A part with no weight plays the Kakegawa
grand's. Three modifiers stretch what the parts build: stiffness scales every
key's inharmonicity B by 4^stiffness, unisons sets how far each partial's
unison strings sit apart (−1 one pitch, 0 as built, 1 three times as far)
and ring scales every string's decay time by 2^ring. A part with one piano's
weight alone plays that piano's measurements exactly, so
`measuredBuild(Piano::grand)`, `measuredBuild(Piano::upright)` and
`measuredBuild(Piano::kawai)` are the three measured pianos.

The engine mixes the pianos' values two at a time in `keyra::Piano`'s order,
each next piano at its share of the shares so far, so two pianos mix as a
pair does and more as the pair rule's weighted mean. A built partial rings
as the strings have it and is struck as the hammers have it: its lanes blend
as between two recorded pitches, and its power over the window the layers'
levels are measured over (50 to 750 ms) lies between the pianos' in dB, at
the hammers' shares; a partial only some pianos play plays at their share in
power. The body's modes pass between the pianos mode by mode in power, with
the phase of the largest share's, since the boards' modes of one index are
not one mode. So halfway between the grand and the upright each key plays
within 0.9 dB of between their levels at soft, middle and full velocity, and
with every part at equal thirds of the three pianos within 1.4 dB of between
the three's. A build changes from the next strike: what sounds rings on, the
strings as they were struck and the body as the new board has it, its
pickups gliding to the new board's over 10 ms.

The plug-in's Build view is a grid of the weights, a row per part and a
column per piano under its city, beside Stiffness, Unisons and Ring, which
show their factors, ×1.00 as built. A piano's presets set its column to
100 % and the others to 0; the weights of a part are shares of their sum, so
Strings at 50 % Kakegawa and 50 % Helsinki plays as Strings at 100 % of each.
Every song saved before the weights existed opens as the build it chose,
`keyra::buildToward` turning its Piano and its parts toward the other piano
into weights. `keyra_render --strings kawai=1,grand=1` and the other parts'
options play any build.

### Microphones

Each piano is heard from the stereo pair its recordings were taken with: the
grand from Salamander's two AKG C414 in AB about 12 cm over the strings, the
upright from the Helsinki library's Blumlein ribbon pair in player position,
close to the hammers, and the Hamamatsu grand from VCSL's pair in player
position. A build between pianos hears each partial and mode through a
pickup between theirs, by the strings' and the soundboard's shares. The Tube
Mic control (`keyra::Parameters::mic`) moves
toward the Helsinki library's other microphone, a modified CV-12 tube
condenser at shin height to the left, which took every strike at the same
time as the ribbons: its onsets sit a median 0.26 ms from theirs, and where
a note's two round robins differ in level both microphones show the same
difference (correlation 0.98). So the difference between their takes is the
microphone and its place, not the playing. `Tools/fit_mic.py` measures it
per third octave from 39 Hz to 8 kHz as the tube's level over the ribbons'
mid from 50 ms to 1 s after onset, the median over the 137 train takes, and
fits it with a low and a high shelf and five peaks
(`Source/DSP/MeasuredMicData.h`), 1.5 dB from the 21 never-fitted takes'
medians per band, where a flat response sits 3.8 dB from them. Against its
midrange (500 to 800 Hz) the tube hears 6 to 8 dB more of the deep bass
(60 to 125 Hz) and 3 to 4 dB more from 2.5 kHz up, and 5 dB less at 250 to
315 Hz and 3 dB less at 1.3 kHz. One response describes it: from the first
second to the next two its ratio moves a median 0.3 dB, and register and
velocity move it little against the bands' spread.

The tube is one microphone, so at 100 % both channels play the pair's mid
through its response, and between 0 and 100 % the two are mixed, the image
narrowing as the tube comes in. The control applies at once to everything
sounding; at 0 the tube is silent and the engine plays as before, sample for
sample. Its level is each piano's own calibration on Reason's meter (see
Playing level), between them by the hammers' build, which mixes the
partials' levels. Neither grand was recorded through the tube: each plays
the upright's measured response, a vintage colour on a grand rather than a
measurement of it.

### The room

Every recording was taken in a room, and between a strike's partials each
holds its reverberation: from 0.1 s after the strike the floor between the
partials falls at one rate per third octave whatever the note, and above
250 Hz the two microphones hear it uncorrelated. The fitted partials hold the
room at their own frequencies already, so the room hears only what they
leave out, the strike's noise bands and the board's ring. It plays as a
feedback delay network (J.-M. Jot and A. Chaigne, AES 90th Convention, 1991):
sixteen lines of 11.3 to 67.5 ms, each a prime number of samples long, mixed
by a 16-point Hadamard matrix, each losing the room's decay through a
first-order shelf, and two of the matrix's rows as the left and right
channels, whose correlation is 0.013. `Tools/fit_room.py` measures each
piano's room from its train takes: per band the rate the recordings' floor
falls at, the shelf fitted to those rates, and one gain that brings the
engine's floor to the recordings' (`Source/DSP/MeasuredRoom.h`, checked by
`Keyra.MeasuredRoom`). The Kakegawa grand's room rings for 0.85 to 1.07 s
(T60, from its highest bands to its lowest), the upright's 0.72 to 1.83 s,
the Hamamatsu's 1.20 to 1.61 s, New York's 1.56 to 2.17 s and the Hamburg's
2.29 to 3.66 s. At 1 to 4 kHz, 0.45 s after the strike, the engine's floor
stood 5.4 dB under the grand's train takes, 3.3 dB under the upright's,
13.7 dB under the Hamamatsu's, 20.6 dB under the Hamburg's and 20.4 dB
under New York's without it, and stands 2.0 dB under, 1.5 dB over, 0.7,
0.5 and 4.8 dB under with it. A build between pianos plays a room between
theirs by the soundboard's shares. `keyra::Parameters::room` scales what
enters it from 0 to 2; no control exposes it, and the plug-in plays it as
measured ([room](Docs/research/room-2026-11-09.md)).

### Calibration from recordings

The calibration tool requires an explicit operation. `--analyse` measures the
TRAIN recordings into raw anchor caches; `--recalibrate` exports from those
caches and can replace a conditional repair. `--measurements <snapshot.json.gz>`
regenerates an exported numeric snapshot without opening recordings or raw fit
caches. Add `--check` to compare the generated header and, if explicitly supplied,
its regeneration receipt. Stored-number regeneration is not a new source fit.

For a local calibration correction, `Tools/update_modal_measurements.py` accepts
an immutable accepted snapshot and a manifest pinning the TRAIN sources,
historical and candidate fits, selection evidence, and execution operators.
It supports existing partials at their accepted carrier frequencies, fixes the
accepted layer clocks, and preserves undeclared measurements. Public snapshots
contain exported numbers and provenance, never waveform data or raw-fit pickles.
The optional component-based fitting start is disabled by default; a lower fit
objective still needs source, stereo, keyboard and native validation before use.

`Source/DSP/MeasuredModalData.h` is generated by `Tools/fit_realtime_modal.py`
from the train role of a locked split of the Salamander Grand Piano V3
(`Tools/corpus/split-2026-10-27.json`, fetched and verified by
`Tools/fetch_salamander.py`): every A, C and F♯ from A0 to A7 at twelve
velocity layers, 264 recordings. Each partial is fitted jointly across its
pitch's layers (`Tools/piano_analysis.py`), the lanes' rates shared and their
levels and phases per layer, every moment of its decay weighed relative to its
level down to the recording's floor; in a layer where it does not stand clear
of that floor, it is no louder than its recorded peak there. The layers'
contact times are aligned so that the phases form one pattern across the
partials, and a pitch's onset rise follows one line over velocity, held within
the range its layers measure. A partial's lanes sit within about 3 cents of it;
where one settles at that bound, the partial is fitted again with lanes up to
about 10 cents out, seeded from the components its envelopes resolve and
keeping the first fit's rise, and the closer of the two fits is kept. A fit
leaves part of a partial in its residual where its lanes cannot follow the
unison strings' beating, so each partial's lanes are then scaled, layer by
layer and by at most 6 dB, to the energy its strings hold from 50 to 750 ms
after contact, where the recording stands 10 dB over the partial's floor and
over the levels half an order either side, less those levels. Beside
the series, the residual's peaks that four or more layers share are measured
each through a window just long enough to part it from its nearest neighbour,
from 30 ms to 2 s, and fitted with one lane from contact; one within 3.5 cents
of another key's undamped string is that string. The undamped strings are
measured as tones from F♯3 up, below which the struck key's series covers their
pitches: through half-second windows from 1 to 2 s after contact, both
channels' power at the strongest bin within 1 Hz of a string's pitch, where it
stands 10 dB over the median 4–20 Hz either side and 10 Hz from every partial
of the struck key. A string's pitch is the median of its strongest peak in the
recordings from C6 up; its stereo pickup the median level difference and mean
phase between the channels; its decay its fall from 1 to 2 s, drawn towards the
strings' median. Its level at a recorded pitch is fitted over every layer where
it rings clear in two or more: a layer where it rings clear measures it,
brought back to contact, and one where the noise hides it bounds it from above
at that tone (a censored fit, one spread for every layer); elsewhere it sits 10
dB under the median bound but never over the tightest. One slope serves every
string and pitch, in dB per dB of the level the strike's layer plays at, as the
knock's does, and rises with the octaves the string lies over the struck
fundamental, as a harder strike is brighter: 1.48 dB per dB and 0.38 more per
octave on the grand, 1.39 and 0.47 on the upright. A key's own string is
read the same way on its own key's train takes (`Tools/fit_halo_own.py`),
where no lane of the key's partials lies within 4 Hz of it, the half-second
window's main lobe: a window hears it where it stands 10 dB over the median
4–20 Hz either side, leaving out what lies within 4 Hz of the key's own
components, and 10 dB over what those components alone read there through
the same window, each lane within 40 Hz at the take's layer and falling at
its own rate. Its level at a pitch is fitted at the strings' slope as above,
a layer that rings clear capping it where fewer than two do, and a pitch the
series fit leaves uncalibrated, the grand's C8, only bounds it. Between the
recorded pitches each key interpolates their levels by key and holds the
nearest beyond them, and has none between two pitches whose partials play
their strings. The strings' prompt parts are
measured the same way through quarter-second windows at 0.125, 0.25, 0.375 and
0.5 s, where a string stands 60 Hz from every partial of the struck key and
rings clear 10 dB over the median 16–60 Hz either side: each window's excess
over the string's own line. One decay serves every string, fitted where they
ring clear; each string's level counts the windows where the noise hides it as
upper bounds and is drawn towards the strings' median by ten layers' worth of
windows. A string's beat is read on each train take where its tone stands 20
dB clear at 1 s (`Tools/fit_halo_beats.py`): its envelope from 0.3 to 3 s,
demodulated at its pitch, gives two components, and the string beats where the
median beat its other recorded pitches give explains a pitch's envelopes
better than one component on so many pitches that tossed coins would do as
well in 5 % of draws or fewer. The body modes are found below the treble's
fundamentals, where no string sounds. Each mode's second stage is a line
through its ±3 Hz envelope every 10 ms from 0.4 to 1.5 s after contact, in the
frames that stand 6 dB over the take's quietest second; a layer counts where
that line falls 6 dB or more, is the slower and starts 3 dB or more under the
first, which is then refitted on what the second leaves of the frames from 35
to 400 ms, and a mode takes the energy-weighted median of six or more layers'
rates; a line whose first stage falls less than 6 dB over those frames stands
as a string does and is no mode. A pitch's knock
on each stage is a line in the level of the layer that struck it, weighted by
the knock's amplitude: the second stage's is fitted after 0.4 s first, the
first's on what it leaves from 20 ms on, and again from 45 ms for the modes
in the bands where the pitch's knock is found (by a first such fit in every
band it can be measured in), which the knock's bands then play. A pitch leaves
out the modes within a semitone of its partials, where what the partials leave
of the strings would pass for their knock, and takes their knock from the
nearest pitches that measure them, by note. The body's onset rise is the one
under which the modes build up below 0.8 of the treble's fundamentals as the
recordings do, matched on shape, not level. The board
noise is measured
in the gaps between the partials the recordings show and, above the highest of
them, across whole bands, as the benchmark measures it. A gap's level is the
median of its bins, which passes over the tones a gap holds: below a note's
fundamental other strings', above it the phantom partials a hard strike adds
at the sums of two partials' frequencies (until 0.4.15 the mean measured the
bands above the fundamental, and the engine played those tones as a hiss over
every forte note). Below the fundamental the ring falls in two stages: a second, slower line is fitted through the
frames from 0.15 to 0.6 s after contact that stand 10 dB over the floor, and
the first is refitted on what the second leaves of the early frames. Above
the fundamental the late frames mix the ring with the note's own unresolved
partials, so only the first is fitted there. The strike's knock is measured
from contact, in third-octave bands from 400 Hz to 16 kHz: through 20 ms
frames centred 10 to 35 ms after contact, between the partials, what the
residual holds beyond the body's modes and the ring, where it stands over the
ring in four frames or more and falls faster; per pitch and band one decay,
the median of its layers' slopes, and per layer its density at contact under
it. Under 400 Hz the knock is fitted in five third-octave bands from 125 to
315 Hz, on the train takes whose fundamental lies a third of an octave and
more over a band, against the engine played without it at each take's layer
and scaled to the take as the benchmark scales it: through the engine's band
filter, in 5 ms frames from the strike to 0.5 s, the benchmark's attack and
early windows weighed alike, the recording's power against the render's plus
a knock's expected power, worked out exactly through the filters, and what
the room returns of it; per piano and band one decay, rise and balance, and
per recorded pitch a level at the loudest layer and its slope with the
layer's ([low knock](Docs/research/low-knock-2026-11-09.md)). The
action's knocks are measured from each recorded pitch's key-release take and
the sustain pedal's two: a level and phase per mode at the knock's onset,
fitted on the same modes under one rise and one decay they share; the
recordings were gained up as a set, so their level against the notes is the
library's SFZ mix (a release at −37 dB tracking velocity and 2 dB quieter for
each second held, the pedal at −20 dB down and −19 dB up), not a measurement.
The open strings' decay comes from the train pedal-down take, which rings them
for seconds once the pedal's knock has passed: each string peak from 60 Hz to
5 kHz that stands 6 dB over its floor for 0.8 s or more and clearly falls, 99
of them, its slope over 0.5 s frames, and over them the rate's log linear in
octaves. Per third-octave band from 63 Hz to 5 kHz, the level every freed
partial starts at as the dampers lift is the one that rings the take's energy
there from 0.3 to 2.3 s, in the take's own scale. A strike interpolates
between the recorded pitches by partial order and between the layers by
velocity, taking phases from the nearer pitch. A partial's lanes are paired by
the share of the partial they carry, each pair as alike in decay as the
pairing allows; each lane's decay rate moves between the pair's in 1/s, so
that with its level moving in dB its level at every moment moves between
theirs; a partial's stereo pickup moves
between the two pitches' channel level differences in dB and takes its
channel phase difference from the nearer pitch with its phases, so its lanes
sum as one pitch's do; its right channel is then turned as a whole so that
its lag behind the left over the first second or so moves between the two
pitches' along the shorter arc. Its level is set so that its power over the
same window, its lanes' beating included, sits between the two pitches' in
dB, and so does its balance, the left channel's power over the right's,
unless that would take a channel outside both pitches': that channel then
stops at the pitch's power it would pass. C8 is left out: its strongest
components sit 90–100 cents above the stretch that F♯7 and A7 set and no
partial series explains the recording, so the keys above A7 play A7's data on
the stretch curve. Only fitted numbers enter the header; no recorded waveform
or impulse response is loaded.

The Hamamatsu's, the Hamburg's and New York's keys between their recorded
pitches play the keyboard network's partials instead
([notes](Docs/research/keyboard-network.md)). The network
(`Tools/keyboard_network.py`) fits a whole keyboard at once from the train
recordings of the five pianos, no lane decaying faster than the fits' fastest
at its key and each partial's first 100 ms weighed, and
`Tools/write_network_tables.py` writes what it gives each such key, at each
piano's own setting of its size and smoothness, into
`Source/DSP/MeasuredNetworkKeys.h`:
each partial's decays, unison offsets, pickups and levels per layer from the
network, its tuning and rise from the blend, and its power in each channel
over 50 to 750 ms moved by what the fits hold over the network at the two
pitches around it, so that the per-key trims leave the recorded pitches where
they were. Its phases come from the nearer pitch, its right channel's lag
moves between the two pitches' as the blend's does, and a lane the network
decays faster than both fits around the key is left out: it clicked.

The Kakegawa grand's and the upright's keys between two recorded pitches
above the bass break blend them and then take a correction the same tool
learns (`correct`): it hides the five pianos' recorded pitches one to three
in a row and compares the blend of the pitches around them with their own
fits, by each channel's energy over 0.05 to 0.75, 0.75 to 1.5 and 1.5 to
3.5 s. For each partial it gives a shift of its lanes' decay rates and a
tilt of their levels between its fast lanes and its slow, both vanishing at
the recorded pitches; the engine applies them to the blend and then puts
each channel's power over 50 to 750 ms back where the blend has it, so the
per-key trims, the tuning and the channel balance stay the blend's.
`Tools/write_network_tables.py` writes its figures into the same header.
Their keys between in the wound bass, where a pitch around them is below the
break, blend as before.

The upright's `Source/DSP/MeasuredUprightData.h` comes from the same tool
(`--model upright`) and the train role of
`Tools/corpus/split-helsinki-2026-10-28.json`: 28 pitches from C1 to G7 at the
library's five velocity layers (four at A♯3, E7 and G7), one take each, and the
hammer noise the library plays as each of those keys is let go
(`Tools/decode_helsinki.py` verifies a copy of the library against its pins).
Each layer is measured at the middle of its velocity range. The takes are cut
at the strike, so a band's noise floor is read at a take's end, and the frames
that would start before a take are left out. The library mixes the hammer
noises at a fixed −14 dB against the notes, whatever the velocity or how long
the key was held, and so do the upright's release knocks. Its key-release
takes, each a note dying under its damper from about the key-up, set what the
dampers leave ringing: below F6, each train take's partials to the tenth that
stand clear of its floor and of the undamped strings' partials, fitted under
the engine's own damper as a share the felt takes at its loss and a share it
holds loosely, each linear in octaves, with a key-up per take and a level per
partial, as the takes carry no level against the notes
([dampers](Docs/research/upright-dampers-2026-10-28.md)). It has no pedal
recordings, so the upright's pedals make no sound of their own; no take shows
the 16 kHz band's noise in three layers, so that band is silent. Its 21 dev
recordings, never fitted, are the first takes of D♯2, G♯3, C5 and E6 and B3's
one take; F♯1, E4 and G♯5 stay sealed. The library's second take of a note
repeats its first: 126 of the 143 share its hammer noise, nine in ten of those
within 0.15 cents of it (`Tools/find_repeated_takes.py`), so no second take is
fitted or scored. The other 17 are new strikes. Twelve of them, at train
pitches, set how far the engine's strikes spread: each differs from its first
as a velocity change does, ten of them brighter where louder, by a median
1.04 dB in early level, which is a spread of 1.085 dB for one strike, and in
pitch by a median 0.02 cents.

The Hamamatsu grand's `Source/DSP/MeasuredKawaiData.h` comes from the same
tool (`--model kawai`) and the train role of
`Tools/corpus/split-vcsl-kawai-2026-10-31.json`: 27 pitches from A0 to C8 at
the library's four velocity layers (fewer at a few pitches), one take each,
each layer measured at the middle of its velocity range, and the release
take the library plays as each of those keys is let go
(`Tools/decode_vcsl.py` decodes and verifies a copy of the library). The
library's lowest takes, which it maps to A♯0, sound A0 and are taken as A0's.
Its layers span 33 dB, so a partial counts where two of them find it rather
than three, or a forte strike's upper partials would go unplayed. Every
second-layer take from E3 up was recorded through a noise gate that cuts it
to digital silence 0.6 to 15 s after the strike, so the analysis, the fit and
the benchmark read a take only until its first 20 ms of exact silence
(`piano_analysis.recorded_end`), which no take of the other two libraries
holds before its fade-out. Its release takes scatter by up to 20 dB between
neighbouring keys about a 38 dB fall from A0 to C6; each keeps its modes and
plays at that fall's line through them. The library sets no level between
the action and the notes, so its knocks play no louder against a note than
the grand's do at C2, C4 or C6. Its rises are capped at the hammer's contact,
as the upright's are. It has no pedal recordings: its pedals make no sound of
their own and its strings ring under the pedal at the grand's rates. Its 23
dev recordings, never fitted, are every layer of D♯1, D♯2, A♯3, D5, A♯5,
B5, F♯7 and G7; D3, F♯4 and F♯6 stay sealed.

`Tools/benchmark_recordings.py` scores a renderer against every train and dev
recording, through `keyra_render`, which strikes every note at exactly its
recorded layer's velocity unless given `--vary`, which plays it as the
plug-in does. The dev recordings, D♯1, D♯3, D♯5 and D♯7 at
every layer and four other layers of every calibrated pitch, are never fitted;
D♯2, D♯4 and D♯6 stay sealed until a candidate goes to the owner. `Tools/compare_benchmarks.py`
lists every note where a candidate is worse than the shipping engine. The [current report](Docs/validation/recording-benchmark-split-2026-10-27.md)
compares this engine with 0.3.0; the [upright's](Docs/validation/upright-recording-benchmark-2026-10-28.md)
scores the upright on its own recordings against the grand's data played on
them, and the [Hamamatsu grand's](Docs/validation/kawai-recording-benchmark-2026-10-31.md)
likewise; [another](Docs/validation/hamburg-network-keys-benchmark-2026-11-05.md)
scores the Hamburg's keys between recorded pitches, the keyboard network's
partials against the blend. `Tools/benchmark_releases.py` scores the upright's key releases against
its train and dev key-release takes ([report](Docs/validation/upright-release-benchmark-2026-10-28.md)),
and `Tools/benchmark_pedal.py` the grand's sustain pedal going down against
its train and dev pedal-down takes, band by band, the strings' ring against
the knock and its fall ([report](Docs/validation/grand-open-strings-benchmark-2026-10-30.md)).
`Tools/tone_survey.py` measures the benchmark's cases signed, per
third-octave band: where each register's tone and stereo image stand over or
under the recordings, in the attack, early and sustain windows.

### Pedals and keyswitches

Sustain lifts the dampers continuously, so half pedalling damps part way.
On a moving pedal or a released key, the damped sympathetic strings follow
the same 18 ms travel model as the struck strings. When the key is struck
again, its damper is clear for both the new strike and the vibration still
ringing from earlier strikes on that MIDI channel.
At the owner's request full pedal lifts them only 80 % of the way that clears
the strings, so the felt still grazes every string, those ringing in sympathy
with the rest: a chord of C3, C4, C5 and C6 let go under it falls 60 dB in
8.7 s on the grand and 11.2 s on the upright, where clear of the strings it
rang on past 30 s. Going down the pedal sets the strings it frees ringing
(**The modal engine**).
Sostenuto captures the keys held as it crosses halfway down and holds only
those. Soft acts on later strikes as each piano's action does: a grand's
shifts the hammers to fewer strings (una corda), lowering the level and the
high partials and moving energy to the slowest lane, and the upright's brings
them halfway to the strings (half-blow), so that a strike plays as one √½ as
fast, as a hammer thrown as hard over half the distance arrives. A build's
soft pedal does each as far as its action is a grand's or the upright's.
Each pedal takes the largest of its panel control, its MIDI controller (CC64,
CC66, CC67) and its momentary keyswitch (MIDI 14, 13, 12, below the piano's
A0). The top twenty keys have no dampers, as on a grand. A damper's felt
takes a partial down faster the higher it sounds, a released C4 at about
500 dB/s, and on every piano leaves the small share described under
**The modal engine**. The upright's release recordings hold more, 13 dB under the
partial at middle C ([release benchmark](Docs/validation/upright-release-benchmark-2026-10-28.md));
the owner chose the subtler ending by ear. The felt mute (CC1
or its control) adds damping to sounding notes, held ones included. The
sustain pedal sounds within 0.08 of either end of its travel, once each way,
from whichever of its sources moves it; half pedalling between is silent, and
a reset of the controllers lifts it without a sound.

### Controls, presets and MIDI

The build's twenty-four weights (`strings1` to `action6`, a part's n-th weight
for the n-th of `keyra::Piano`) and its three modifiers, Quality, Output,
Brightness, Resonance, Width, Tube Mic, Mechanics, Tuning, Felt mute and the
three pedals are the 39 saved parameters. The build and Quality are not
offered for automation: the piano is built for a part, not played, and
Quality is a setting for the machine, not the music. A session saved before
the build existed plays the grand as built at full quality, one saved with
the Piano control the build it chose, one saved before Mechanics its action
as calibrated, and one saved before Tube Mic hears the pair. Mechanics retains
its raw 0–2 host parameter range for saved automation; only the custom knob's
travel and percentage readout use the new taper. The twelve factory
presets in `Source/DSP/KeyraPresets.h` — five on the Kakegawa grand, three on
the Helsinki upright, Hamamatsu Grand, Three Cities, Hamburg Grand and New
York Grand — set the build,
Brightness, Resonance, Width and Felt mute and leave the rest alone. Notes, pedals and pitch bend (two semitones each way) are dispatched at
their sample positions; each MIDI channel owns its keys and pedals, and CC120,
CC121 and CC123 are honoured per channel. The
[user guide](Docs/guide/user-guide.md) describes every control.

### Quality

Quality sets how much of each strike plays. Full, the default, plays all of
it, each partial until it falls 120 dB under full scale. Balanced and Light keep a strike's partials, and the components beside
them, only where they come within 60 and 50 dB of its strongest: at contact,
the sum of their lanes' amplitudes, or over their ring with the key held,
their lanes' energy to silence, each at the strike's brightness. Over every
third key from A0 to C8 at velocities 40 to 127, no third-octave band within
40 dB of a note's strongest moves by more than 0.04 dB at Balanced or 0.74 dB
at Light, while a grand strike plays 39 and 50 % fewer of them and an upright
strike, whose partials sit closer to its strongest, 11 and 20 % fewer. Timed
on a development machine, not in Reason or a DAW, legato chords under the
pedal take 49 % of Full's process CPU at Balanced and 38 % at Light on the
grand, and 95 and 87 % on the upright
([receipt](Docs/benchmarks/quality-cpu-2026-10-28.json)). At 40 dB a soft bass
note lost up to 27 dB in a band 35 to 40 dB under its strongest, so there is
no lighter setting. A change applies from the next strike.

### Playing level

`Tools/KeyraLevels.cpp` reads the factory presets on Reason's channel meter
(the louder channel's RMS over 300 ms, 0 VU at −12 dBFS), playing single
notes every fourth semitone and eight chords at velocities 70, 90 and 110
for typical playing, and the chords at 127 for the loudest. Each piano's
output scale brings its default sound's typical playing to −9 VU at the
default Output, where the portfolio's newer instruments play; the other
presets without felt read from −11.0 to −8.1 VU, Three Cities −10.2 VU. The
half-drive response chosen for 0.4.11 applies at factory Output. The level
before the portfolio guard is halved and the level after it doubled. A short
stereo gain curve protects the restored signal when an attack crosses the
−1.5 dBFS sample ceiling. On a 48 kHz host this adds 24 frames to the
portfolio stage's 96-frame look-ahead. The host receives the total delay.

On the six named pianos of 0.4.11 the 110 → 127 comparison increased on every one of
480 paired strikes across the close and tube mics. Typical preset levels
stay within 0.04 dB of 0.4.10. A forte chord can now cross 0 VU on Reason's
meter, which corresponds to −12 dBFS RMS. The per-preset level tests use
the chosen listening response as their upper bound and test the sample
ceiling separately. [Factory results and reproduction instructions](Docs/validation/forte-response-2026-11-02.md).

### The full physical research

[`Experiments/`](Experiments/README.md) holds the preserved nonlinear
reference solver, the full physical block API, its calibration against the
full-range corpus and the module research behind them. It is the direction the
product's sound is meant to move towards, and none of it is in the plug-in.

## Known gaps

- The modal engine does not model nonlinear hammer contact or a reciprocal
  soundboard; the full physical model in `Experiments/` does, but it is several
  times slower than real time.
- Phantom partials play one gain per pitch, where the takes show the lines
  from 1.6 to 3.2 kHz 6 to 8.5 dB over it at the grand's F♯3, C4 and F♯4, as
  a longitudinal resonance of the strings, which the engine does not model,
  would lift them, and the difference lines 0.8 to 11 times the sums' power
  where both stand clear. The bass plays none, where the takes do not
  decide; the grand's F♯6 and A6 rest on few lines. A line within a few
  hertz of a measured partial adds to what the modal fit already put there,
  soft strikes play the loud takes' gain, under what their own takes read,
  and each key is squared alone, so no lines sound between two keys'
  partials. The square's rise at a strike passes the DC high-pass as a pulse
  under 120 Hz, 42 to 50 dB under a forte chord, which no take measures
  ([phantom partials](Docs/research/phantom-partials-2026-11-04.md)).
- The pitch glide is one law per piano, read on the upright's loud takes from
  50 ms to a second after the onset: its dev takes lean the law's way but are
  too few and too noisy to confirm it, and before 50 ms it plays the law
  unmeasured. It follows the output's power, which stands for the strings'
  energy only as far as the board radiates the partials alike, so Brightness
  also scales it. The other pianos' takes do not decide one, the New York
  grand's falling just short
  ([pitch glide](Docs/research/pitch-glide-2026-11-04.md)).
- The unison's coupled modes, and with them a restrike's or una corda's new
  balance between its strings, the duplex segments and the damper's contact
  position are not modelled: the takes' lanes read as coupled strings little
  more often than random phases make them, a new strike moves the strings'
  balance less than the two microphones disagree, no release take holds a
  line a duplex segment would add, and the best contact laws improve the
  release fits by about 1 %, nearly as much as shuffled controls do
  ([realism candidates](Docs/research/realism-candidates-2026-11-04.md)).
- Of the pedals only the grand's sustain pedal going down, alone, is scored
  against recordings, its strings' ring and fall (above). The recordings do
  not document pedal positions or timings, so half pedalling, repedalling and
  the pedal coming up are not validated, and the strings sound alike however
  fast the pedal goes down. No recording plays notes under the pedal, so how
  loud the open strings ring in sympathy with what is played is the Resonance
  control's, not a measurement, and how they ring on from 1 to 4 s is fitted
  on one decay law, which full pedal's grazing felt steepens at the owner's
  request: over those seconds they fall 1.5 to 11 dB further than the
  pedal-down takes from 63 Hz to 2.5 kHz and within 2 dB of them from 3 to
  5 kHz, a median 9.6 dB/s where the takes' strings fall 6.8 and 7.0. The
  pedal knocks play at the
  library's mix and the key knocks at a level the owner chose by ear, not a
  measured level, and only as far as the
  body's modes hold them: 24 to 70 % of each of the grand's recorded knocks
  below 1 kHz (the upright's 38 to 86 %) is left out, so a released C4
  knocks 4 to 5 dB under the library's balance, measured before 0.4.20
  played the click above 1 kHz
  ([release recordings](Docs/research/release-recordings-2026-10-27.md)).
  The click is fitted on one take per recorded pitch, let go at velocity 85
  after 1.5 s held, and follows the knock's tracking elsewhere, unmeasured;
  the upright's mostly sounds one band near its takes' floor, and the
  Hamamatsu grand's, which its takes do not hold apart from their strings,
  is not played ([action click](Docs/research/action-click-2026-11-05.md)).
  The key noise the recordings carry 1 to 28 ms before string contact is not
  played: a note sounds from contact.
  Under the lowest body mode (29 Hz) the middle register's recordings hold a
  low thud in their first 0.3 s, 6 to 22 dB over the room's floor and growing
  more slowly than the strings, which the engine does not play: the grand's
  noise score at F♯3, A3 and C4 sits up to 6 dB from it at the softest layers
  ([knock benchmark](Docs/validation/grand-knock-benchmark-2026-10-29.md)).
- Only the upright was recorded through the tube: the grands heard through it
  play the upright's measured response. The tube hears the pair's mid
  through one response, without the 0.26 ms its strikes arrive after the
  ribbons', so mixing the two sounds no comb between them, as two real
  microphones apart would. No recording takes either piano from further
  off, so there is no distant perspective.
- The room has one gain per piano. The board's modes and the noise bands
  were measured from recordings whose floor holds the room's first part, so
  between 250 Hz and 1 kHz the room takes the engine's floor over the
  recordings' by 0.45 s after the strike: the Hamamatsu's by 5.6 dB and New
  York's by 7.2 dB on their train takes, the grand's by 1.0 dB. Under 250 Hz
  the grands' recordings hear their floor correlated between the
  microphones (+0.77 to +0.93), and the room's channels are uncorrelated at
  every frequency, which takes the grand's low correlation to 0.71 against
  its recordings' 0.89 and the Hamburg's to 0.37 against 0.77. The network
  starts diffuse, with no early reflection, its rates are measured from 0.1
  to 0.6 s after the strike only, and its shelf follows the upright's rates
  (29 to 86 dB/s) within 8.7 dB/s rms
  ([room](Docs/research/room-2026-11-09.md#what-the-room-does-not-do)).
- Between the recorded pitches, partials, phases and stereo pickups are
  interpolated by partial order. The microphones' left/right balance changes
  sharply with frequency, so at D♯3 the image is still further from the
  recording than 0.3.0's fixed panning was (7.7 dB against 4.7 dB): the
  recording holds its first eight partials up to 12 dB to the right, where
  C3 and F♯3 hold their second 19 to 24 and 10 to 11 dB to the left. From C6
  up the grand's image is narrower than its recordings': from 800 Hz to
  4 kHz its side stands a median 2.4 to 4.7 dB further under its mid on the
  dev cases, and its channels' coherence 0.2 to 0.3 higher
  (`Tools/tone_survey.py`). Giving the board's ring each pitch's own
  left/right coherence, for its first stage and its second, does not close
  it ([decisions](Docs/decisions.md)). A key
  between two recorded pitches follows one that is louder or quieter than
  its neighbours, where its own recording may not: the upright's C4 sits 3
  to 7.5 dB over the line through F♯3's and D4's levels at every layer, and
  the never-fitted B3 beside it plays 1.7 dB louder against its recording
  than the median note does.
- A key between two recorded pitches holds each partial's power and each
  of its channels over 50 to 750 ms between theirs, but not the partial's
  shape inside that window where the fit splits it into lanes differently at
  the two pitches: struck at 127, the Hamamatsu's B7 plays its second partial
  up to 7 dB over both A7's and C8's in its left channel from 200 to 450 ms,
  and 6 dB over in its first 50 ms, where 0.4.14 played it 24 dB over from
  200 to 450 ms ([decisions](Docs/decisions.md), 2026-11-04).
- The Hamamatsu's, the Hamburg's and New York's keys between recorded
  pitches, which play the keyboard network's partials, strike weaker than the
  fits at their recorded pitches and ring on louder: struck alone and held,
  at velocity 80 they stand a median 2.7, 2.6 and 2.4 dB under the blend over
  their first 100 ms and 0.4, 0.4 and 1.4 dB over it from 100 ms on (at
  velocity 32, 2.2, 2.4 and 2.2 dB under and 1.4, 0.5 and 1.1 dB over). A
  recorded pitch therefore stands apart from the mean of its two neighbours
  by 4.0, 2.4 and 2.6 dB rms over the first 100 ms (blended, 1.9, 0.9 and
  0.9) and by 7.7, 4.5 and 4.5 dB rms from 0.8 to 1.6 s (blended, 4.2, 1.3 and
  2.3): at velocity 32 the Hamamatsu's F♯2 stands 9.3 dB over its neighbours
  over its first 100 ms and 21.2 dB under them from 0.8 s (blended, 1.8 and
  6.1), and the Hamburg's G♯5 11.1 dB under them there. Against 0.4.25 some
  never-fitted takes stand further from their recordings by more than a
  tolerance: the Hamamatsu's B5 envelope (3.62 to 7.38 dB) and A♯5's stereo
  balance (4.41 to 7.21 dB), the Hamburg's E3 tuning (0.48 to 3.69 cents) and
  New York's E7 decay (8.18 to 10.46 dB/s) and coherence. Those takes chose
  among six settings, and the Hamburg has no sealed recordings, so they are
  no longer untouched held-out evidence
  ([keyboard network](Docs/research/keyboard-network.md#the-third-run)).
- The correction at the Kakegawa grand's and the upright's keys between
  recorded pitches is how five pianos' recorded pitches depart from the
  blend of their neighbours, learned from their fits: a realistic character
  for those keys, not a measurement of them. It moves only how each partial
  decays, so the blend's tuning and stereo balance stay, and the blend's
  beats, which fall elsewhere than a recorded key's, stay too. It holds each
  channel's power from 50 ms, not before: struck alone at velocity 72, the
  grand's keys between from C6 up start 0.57 dB further under their
  recorded neighbours over their first 50 ms than blended. At the grand's
  never-fitted takes it corrects, its partials from the 1st to the 15th
  still ring 2.2 dB under their recordings from 0.75 to 1.5 s and 2.5 dB
  under from 1.5 to 3.5 s (blended, 3.1 and 3.5). It leaves the keys
  between in the wound bass blended, which it took further from their
  recordings, and it is not applied to the Hamamatsu's and New York's, which
  it took past a tolerance at some pitches (New York's C6 decay 8.27 to
  10.79 dB/s from its recording) and which play the network since 0.4.26
  ([keyboard network](Docs/research/keyboard-network.md#a-correction-to-the-blend)).
- From C6 up, the partials' decay after half a second is 3.3 dB/s from the
  recordings' on the dev cases (0.3.0: 6.5 dB/s), but at A7 it is 1 to 2 dB/s
  further than 0.3.0's. All but four undamped keys ring as one string at one
  pitch, without their unison's beating, which dips the recordings' strings 3
  to 10 dB from half a second on. The four that beat, the Kakegawa grand's
  F♯6, A♯6 and C♯7 and the upright's C7, play one median beat whichever key
  strikes them, where each recording's beat peaks and dips at its own times:
  measured at 1 and 2 s, the grand's F♯6 and C♯7 sit 0.8 to 1.7 dB further
  from the recordings than one tone did, and C♯7 reads a median 6 to 9 dB
  under them at 0.375 and 0.5 s
  ([string beat](Docs/research/halo-beats-2026-11-05.md)). Past
  its prompt part a string falls at its rate from 1 to 2 s, where the real
  strings fall more slowly later: the strings that ring clear sit a median
  0.9 dB over the grand's never-fitted recordings at 1 s and 1.1 dB under at
  3 s, when 11 % of them are 10 dB or more under, and 4.3 and 15.2 dB under
  the upright's train recordings (0.4.20 measures all of these within 0.5 dB;
  the 0.7 and 9 dB this item gave for the upright were measured on 0.4.11 or
  earlier). The prompt parts share one
  decay, and a string that few strikes measure takes much of the strings'
  median level: at 0.125 s 4 % of the strings ring 10 dB or more over the
  grand's never-fitted recordings and 6 % over the upright's. The upright's G7
  recording at velocity 51 holds F♯7's string 30 to 35 dB under the
  fundamental in its first half second, where the engine plays it 3 to 10 dB
  further under. Where a recorded pitch's own partials cover a string, its
  level there is interpolated from the pitches around it; below F♯3 each
  string keeps the level of the lowest pitch that measured it, and the slope
  by which they grow with the strike, which the fit sees rise over 4.5 octaves
  of the struck note, rises on past them under the bass notes. Where the noise
  hides a string in all but one of a recorded pitch's layers, the recordings
  only bound it: the string sits 10 dB under its median bound, never over its
  tightest, and at their two loudest layers the upright's never-fitted G♯3,
  B3, C5 and E6 ring 16 of their 295 strings 10 dB or more over their
  recordings at 1 s, where the pitches around them set such a string at that
  bound. In their first 0.3 s soft bass strikes still ring the upright's band
  around 1.6 kHz off its recordings: F♯3's softest layer 9 dB over (22 dB
  before this fit) and D♯1's two softest 6 to 13 dB under (8 to 9 dB over).
  From F♯3 to F♯5 the first seconds of the sustain sit up to 1 dB further from
  the recordings (4 dB at D♯5) than under a fit weighted towards them, as a
  long note's tail now counts as much.
- A key's own undamped string grows with the strike at the one slope every
  undamped string takes unless three or more of its pitch's layers ring it
  clear: the Hamamatsu's two pitches that ring it ring it clear in two layers
  each, and a key between takes the slopes of the pitches around it, so the
  grand's never-fitted D♯7, which holds F♯7's string and slope, decays
  0.10 dB/s further from its recordings than at the shared slope
  ([own slope](Docs/research/halo-own-2026-11-05.md#each-pitchs-own-slope-0426)).
  It plays at the pitch the other keys' strikes measure for the string,
  which at F♯7 lies 2.4 Hz over the octave-below string's second partial that
  F♯7's strikes ring. Since 0.4.26 F♯7 also plays that partial at its own
  pitch, as one of its unison strings, beside the own string: letting the
  own string give way there stood the grand's treble further from its
  recordings
  ([unison strings](Docs/research/treble-unisons-2026-11-06.md#the-candidates)).
  Keys between recorded pitches take the
  levels around them: the New York grand's A♯6 to D♯7 have none, and its
  never-fitted E7 and A7 sit 32 and 20 dB under their recordings there, the
  Hamamatsu's F♯7 17 to 24 dB under, and the grand's C8, which only bounds it,
  5 to 14 dB under ([own string](Docs/research/halo-own-2026-11-05.md)).
- Under the notes from C4 up the body's modes still ring short of the
  recordings late: from 0.7 to 1.5 s the grand's 200 to 400 Hz modes sit 7 to
  11 dB under its train takes, and its other regions from 25 Hz to 1 kHz 4 to
  9 dB under from 1 to 1.5 s; the upright's 700 Hz to 1 kHz sit 6 and 10 dB
  under its train and dev takes there. Earlier they ring over them: from
  0.1 to 0.5 s after the strike the upright's notes from C6 up stand 2 to
  4.5 dB over their recordings from 400 Hz to 800 Hz, and in the first 0.1 s
  its middle register's knock stands 3 dB over at 80 to 100 Hz. Letting
  the knock fall faster at first trades one for the other
  ([decisions](Docs/decisions.md)). Under the treble's fundamental, from 400
  to 800 Hz, the side stands up to 6 dB further under the mid than the
  recordings' over their first 1.5 s: the knock that plays there is mixed at
  the coherence of its first frames, centred 10 to 17.5 ms after contact.
  The body rings on after key-up; whether a real one stops sooner when the
  dampers land is not measured. In their first 50 ms the notes from C6 up sit
  2 to 8 dB under the recordings from 400 Hz to 2.5 kHz. At the top the knock
  brings a strike to its peak sooner than the recordings: F♯6, F♯7 and A7
  rise from 10 to 90 % of it in 4 to 5 ms at every layer, where the grand's
  recordings take 6.6 to 10.8 ms (A7's softest 15 ms)
  ([benchmark](Docs/validation/grand-knock-from-contact-benchmark-2026-10-30.md)).
- The knock from 400 Hz up has no rise and starts from rest after a silence,
  so through the first 30 ms the treble still stands under its recordings
  there: at 400 Hz by 3.8 dB on the Kakegawa grand, 6.6 on the Hamamatsu,
  5.1 on the Hamburg and 9.1 on New York. Under 125 Hz no knock plays: 30 to
  60 ms in, the Hamburg's treble stands 8 to 10 dB under its recordings from
  50 to 80 Hz. Between sparse recorded pitches the knock under 400 Hz is a mix
  of theirs (the Hamburg's split measures four to six pitches per band), and
  where the engine already stood over a recording there it adds to the
  excess, as at the Hamburg's never-fitted C♯5 from 100 to 315 Hz through the
  attack. Whether a real board's knock stops sooner under the dampers or a
  mute is not measured ([low knock](Docs/research/low-knock-2026-11-09.md)).
- C8 is not calibrated (above). Below A3 the partials leave too few gaps to
  measure the board noise in six to ten of the thirteen bands; those bands are
  interpolated between the nearest pitches that measured them.
- Struck alone at velocity 127 and let go after 0.5 s, 54 of the five pianos'
  keys from F6 up still sound a minute later at the default Output, so the
  engine does not come to rest after them. Partials whose fit stopped at the
  fitter's slowest decay, 0.003/s, where it identified none, ring on: the
  upright's C7 plays its 6.5 kHz partial at −60 dBFS a minute on, its other
  keys from A♯6 to D♯7 play at −66 to −77 dBFS, and every other key reads
  −83 dBFS or quieter. Their decays are left to the calibration across the
  keyboard.
- Every recording of each piano is from one instrument and one session, so
  the holdout does not establish how the fit generalises to another
  instrument.
- How far strikes spread is measured from twelve of the upright's strikes,
  nine of them at its softest layer, and plays at every velocity on every
  piano: the grands' libraries hold one take of each note, so their own
  spread is unmeasured.
- The felt presets read 6 to 9 dB under the others on the meter (Felt
  Nocturne −18.2 VU, Felt Upright −15.4 VU): the felt stops each note within
  a fraction of a second, so the meter's 300 ms holds less of it, while its
  attack peaks as high as the others'. Raising them to −9 VU would press
  every hard note into the limiter. The 0.4.11 factory response restores the hard-chord
contrast. Smaller velocity increments on some voicings can still fall,
particularly when bass partials cancel in the tube mic. See the
[paired measurements](Docs/validation/forte-response-2026-11-02.md).
- No recording plays the upright's soft pedal: its half-blow assumes the rail
  brings the hammers halfway to the strings and that the key accelerates
  them evenly. It has no pedal recordings at all, so its pedals make no sound
  of their own (above) and its open strings ring at the grand's rates. Its
  dampers all land alike, where from C1 to F♯2 the felt reaches
  the strings 0.1 to 0.3 s later into the release takes than elsewhere,
  whether those takes start earlier or those dampers land more slowly. Where a
  damped partial lies on an undamped string, the takes hold that string
  ringing far louder than the halo plays it, its level being interpolated
  there (above): the never-fitted C5's third partial, 4 cents from G6's
  string, now releases 6.6 dB from its take, where it was 3.5 dB with the
  felt taking all of it ([dampers](Docs/research/upright-dampers-2026-10-28.md)).
- The upright's treble is fitted worse than its middle. From C6 up its unison
  strings sound 6 to 20 cents apart (the grand's top octave up to 12). A
  partial's four lanes reach those within about 10 cents of it (above); each
  one further out plays as a component beside it, which has no rise of its
  own. Around G7's fundamental the recordings hold about six components and
  its lanes play four, without the 6 Hz beat two of them make. From 0.05 to
  0.75 s E7 sits 3 to 5 dB under its recordings, as the fit weighs its quiet
  tail as much as its start
  ([reach](Docs/validation/upright-lane-reach-benchmark-2026-10-28.md)).
  At the never-fitted E6, between the recorded pitches, the partials sit
  6.8 dB from the recording and their decay 8.2 dB/s from its, where the
  middle register's sit 5.4 dB and 3.5 dB/s. Its noise between partials
  scores 7.5 to 8.4 dB: at its softest layer the board below 200 Hz sounds up
  to 19 dB louder than the recording's, and at its loudest the residue
  between the partials from 1.6 to 8 kHz sits 6 to 13 dB under the
  recording's.
- The Hamamatsu grand is fitted from four velocity layers 33 dB apart, one
  take each, at pitches two to six semitones apart. At its never-fitted
  pitches its partials' balance, decay, image and envelope sit further from
  their recordings than the Kakegawa grand's data played there does: its
  partial levels 9.9 dB from them against 7.7 dB, worst at B5 (22.4 dB),
  between G♯5 and C6, and D5's image 11.6 dB from its recording's
  ([benchmark](Docs/validation/kawai-recording-benchmark-2026-10-31.md)). Its
  A2 is recorded about 4 dB over its neighbours in its three loudest layers,
  and the keys between them play toward it. Its tube's typical level is about 1 dB below the
  other pianos. Its hard chords now grow at the factory Output. It has no
  pedal recordings: its pedals make no sound of their own and its strings
  ring under the pedal at the Kakegawa grand's rates. Its second layer's
  takes from E3 up stop at a noise gate 0.6 to 15 s after the strike, and the
  fit reads them no further.
- Five pianos are measured separately. Yamaha C3 supplies additional calibration
  measurements. Predictions between recorded pitches remain approximate;
  the [interpolation validation](Docs/validation/realism-baseline-and-trials-2026-11-01.md)
  records the remaining pitch-gap and attack-fit limitations.
- Linux VST3 and standalone have earlier validation
  ([pluginval](Docs/validation/pluginval-2026-10-26.txt)). The local 0.4.4 macOS
  VST3 and CLAP pass automated host validators on arm64. Its 0.4.4d1 Rack
  package passes local build checks; fresh Recon validation is pending while
  another session is active. The earlier 0.4.3d1 fourteen-patch protected Recon
  result remains historical evidence
  ([validation](Docs/validation/calibration-followups-2026-11-01.md)). The Audio
  Unit is built but has not passed auval in this iteration. Windows, manual
  DAW workflows, interactive Rack controls/song recall, retail Reason and
  target-chip CPU acceptance remain unverified for this candidate.
- The [production target](Docs/plans/production-readiness.md) lists the
  evidence a commercial release still needs.

## Build

The JUCE-free engine, tests and demo renderer (`build-dsp`):

```bash
cmake -S . -B build-dsp -DCMAKE_BUILD_TYPE=Release -DKEYRA_BUILD_PLUGIN=OFF -DBUILD_TESTING=ON
cmake --build build-dsp --parallel && ctest --test-dir build-dsp --output-on-failure
./build-dsp/RenderKeyraPresetDemos Docs/audio/midi build-dsp/demos   # WAVs + demos.json
```

The full plug-in (`build-plugin`). JUCE 8.0.14 and clap-juce-extensions are
fetched pinned at configure time; pass `-DKEYRA_JUCE_PATH=/path/to/JUCE` or
`-DKEYRA_CLAP_JUCE_EXTENSIONS_PATH=/path/to/clap-juce-extensions` to use local
checkouts, or `-DKEYRA_BUILD_CLAP=OFF` to skip CLAP:

```bash
cmake -S . -B build-plugin -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build build-plugin --parallel && ctest --test-dir build-plugin --output-on-failure
```

Every test carries one tier label, so `ctest -L unit`, `-L audio`, `-L render`,
`-L fuzz` or `-L perf` selects a tier. `unit` includes `Keyra.DspFuzzReplay`,
the fuzz harness replaying `Tests/Fixtures/fuzz/` and seeded inputs, and `perf`
is `Keyra.CpuBudget`, the demos timed in a Release build; it fails only above a
budget, which is unset until the CI runner's median is known.
`KeyraDSPCxx17` compiles the engine as C++17, the Rack Extension toolchain's
standard. `-DKEYRA_ENABLE_SANITIZERS=ON` builds everything under ASan and
UBSan, and `-DKEYRA_BUILD_FUZZER=ON` (Clang) makes `KeyraDspFuzz` a libFuzzer
target. `scripts/validate-plugins.sh build-plugin Keyra aumu Kyra Ptoc
0x4b455952` runs pluginval, clap-validator and, on macOS, auval on a plug-in
build.

On macOS, `./scripts/build-macos.sh` drives the same build through Xcode as a
universal binary and `./scripts/sign-and-package-macos.sh` packages it. On
Linux and Windows, `scripts/package-linux.py` and `scripts/package-windows.py`
package a `build-plugin` tree.

Three workflows run in CI: `ci.yml` on every push to any branch (tiers per
platform, sanitizers and the experiments), `main-build.yml` on every push to
`main` and nightly (pluginval, clap-validator and auval, the collected
download, and the committed screenshot, demos and README blocks), and
`release.yml` on `v*` tags.

The research in `Experiments/` is configured on its own:
`cmake -S Experiments -B Experiments/build`.

## Licensing

Keyra's source is available under the [PolyForm Noncommercial License
1.0.0](LICENSE), with an additional permission to use official builds for any
purpose, commercial music included. The grand's reference recordings are
Salamander Grand Piano V3 by Alexander Holm under CC BY 3.0; the upright's are
the Helsinki 1967 Tube-Ribbon Edition by Mikko Patama, whose author permits
fitting numbers from them provided the recordings are not distributed; the
Hamamatsu grand's are VCSL Keys' Grand Piano K by Versilian Studios, dedicated
to the public domain under CC0 1.0. JUCE,
CLAP and the other dependencies keep their own licences.
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) lists them, with the licence
texts in `ThirdParty/`. The licensed Reason Jukebox SDK is not part of this
repository.
