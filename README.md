# Keyra

Keyra is a physically modelled piano that plays no samples: felt hammers
thrown at stiff strings, the strings of each unison coupled at the bridge, a
soundboard of plate modes radiating to four microphone pairs, and the open
strings and duplex scales ringing with them. Five pianos are designed, a
concert grand, a studio grand, a parlor grand, a baby grand and an upright,
and each is kept
as you like it: the hammers' felt, the strings' age, the unisons' tuning, the
tuner's stretch, the dynamic range, the lid, and how the soundboard, the
sympathetic strings and the duplex scales ring. Beside the model plays the
action measured from recordings for 1.x: the keys, the dampers and the
pedals' knocks. It builds as VST3 and CLAP plug-ins, an Audio Unit on macOS
and a standalone application. Version 2.0.0 replaces 1.x's partials fitted
from recordings with this model; what is not yet verified for it is listed
under Known gaps.

![Keyra](Docs/screenshots/keyra.png)

## Audio demos

One phrase per factory preset, written for what that preset is for and
rendered from `Docs/audio/midi/` through the shipping engine.

<!-- audio-demos-begin -->

| # | Preset | Demo | Length | Peak |
| --- | --- | --- | --- | --- |
| 1 | Concert Grand | [01-concert-grand.wav](Docs/audio/01-concert-grand.wav) | 11.2 s | -1.5 dBFS |
| 3 | Warm Walnut | [03-warm-walnut.wav](Docs/audio/03-warm-walnut.wav) | 11.1 s | -6.6 dBFS |
| 4 | Felt Nocturne | [04-felt-nocturne.wav](Docs/audio/04-felt-nocturne.wav) | 10.7 s | -12.3 dBFS |
| 5 | Open Strings | [05-open-strings.wav](Docs/audio/05-open-strings.wav) | 11.7 s | -3.7 dBFS |
| 6 | Upright | [06-upright.wav](Docs/audio/06-upright.wav) | 11.6 s | -3.7 dBFS |
| 8 | Pop Upright | [08-pop-upright.wav](Docs/audio/08-pop-upright.wav) | 11.6 s | -1.6 dBFS |
| 9 | Baby Grand | [09-baby-grand.wav](Docs/audio/09-baby-grand.wav) | 9.7 s | -7.6 dBFS |
| 10 | Distant Hall | [10-distant-hall.wav](Docs/audio/10-distant-hall.wav) | 10.8 s | -5.3 dBFS |

<!-- audio-demos-end -->

### Listening against the recordings

The physical model is fitted to no recording note by note, and against the
Salamander grand that 1.0.0 was fitted to it stands further off than 1.0.0 on
every score of `Tools/benchmark_recordings.py`
([report](Docs/validation/grand-recording-benchmark-2026-11-11.md), and Known
gaps). The owner judges it by ear against 1.0.0 in A/B sets, which are not
committed; `Docs/decisions.md` records the verdicts. The
[live renders](Docs/audio/live/manifest.json) are musical passages through
0.2.0's engine, frozen evidence from that version's review.

## Version history

### 2.9.0 — 2026-11-12 — a Studio Grand, and the pedal's whisper

A fifth piano, and the strings answer the pedal itself. The saved state is
2.8.0's with one more choice of Piano; a 2.8.0 session opens as saved, and
the four older pianos' notes are 2.8.0's sample for sample until the pedal
goes down.

- **Studio Grand**, 2.0 m: the size of the grand the benchmark's recordings
  are of. Its bass strings' length (1.60 m at A0) and the key where plain
  steel begins (B2) are set against those recordings' inharmonicity below
  C4, which the model's then stands within a factor of 0.75 to 1.54 of,
  note by note; the rest is typical of the size. It is the last choice of
  Piano, and the Studio Grand preset, which played the parlor grand, plays
  it. Against the recordings it is no nearer than the Concert Grand
  overall: on the notes 1.0.0 never fitted its partials stand as far
  (7.7 dB), its tuning, decay and envelope a little nearer (2.0 cents,
  3.7 dB/s, 3.9 dB against 2.2, 3.8 and 4.2), and its attack, sustain,
  stereo balance and rise further (the rise 20 ms against 13), with 221
  single-note scores worse
  ([benchmark](Docs/validation/studio-grand-benchmark-2026-11-12.md)).
- **The pedal's whisper.** A damper's felt lets its strings go as it
  lifts, and they ring: the sustain pedal alone now sets the open strings
  whispering, less for a pedal let down slowly, scaled by Sympathetic and
  silent at 0. It is set beside the engine's pedal knock as the
  Salamander's two pedal-down takes hold it from 300 Hz to 1 kHz; the
  takes' low ring, 25 to 35 dB stronger under 150 Hz, is not there. It
  costs nothing while notes sound; pressed on a silent piano the pedal
  wakes the model until the whisper has died.
- **Tried and left out.** A brighter radiation above 6 kHz, for the top
  end loud notes lack: on four layers the partials moved by 0.13 dB at
  most either way, the bass's noise on the fitted notes 1.0 dB further off
  and the middle's on the others 0.5 dB nearer.

### 2.8.0 — 2026-11-12 — how a grand's upper notes die away

On the three grands a note from middle C up falls away as the recorded
grand's does, where it held on too loud after its first second. The panel
and the saved state are 2.7.0's; a 2.7.0 session opens as saved and the
grands' notes from C4 up ring differently. The upright is 2.7.0's, sample
for sample.

- **The unisons** of a grand stand closer together up the keyboard: the
  spread Detune sets is whole up to B3 and narrows to half from C5 up. A
  tuner sets a unison by its beats, which the same cents make faster the
  higher the note. With the whole spread everywhere the first partial of
  the Salamander grand's notes from C5 up stood 7 to 8 dB over the
  recorded one 1 to 1.5 s after the blow; it stands 1.0 to 1.4 dB over.
  The upright keeps the whole spread: narrowed, its decay stood further
  from the Helsinki upright's.
- **Against the recordings**
  ([grand](Docs/validation/grand-unison-spread-benchmark-2026-11-12.md)):
  on the notes 1.0.0 never fitted, the grand's decay stands 3.8 dB/s from
  the Salamander's (4.2 in 2.7.0), its sustain 7.9 dB (8.2), its envelope
  4.2 (4.4) and its partials 7.7 (7.9); its tuning is 2.2 cents off (2.1).
  The other scores moved by less than 0.05. 23 single-note scores are
  worse, listed in the report.

### 2.7.0 — 2026-11-12 — a denser room, and a bridge with length

The room no longer rings like a spring after a short note, and a key's
colour stands closer to its neighbours'. The panel and the saved state are
2.6.0's; a 2.6.0 session opens as saved and every key sounds a little
different.

- **The room** is sixteen delay lines mixed by a Hadamard matrix where it
  was eight under a Householder reflection, and the case's knock passes
  three allpass sections before it enters. Its echoes grow dense in 130 to
  180 ms where they took 310, and its level is kept. Under a treble note
  the knock's tail from 280 to 710 Hz stands 19, 24 and 37 dB under its
  peak 100, 150 and 300 ms on, where the recording's stands 21, 24 and 36
  and 2.6.0's stood 21, 29 and 39.
- **The bridge** hands a plain string's force to the soundboard along its
  own length, half its bending wavelength at each board mode, where every
  string drove the board at a point. Every key is voiced again for it, and
  a key may now be pulled 15 dB onto the even scale (12 before).
- **The sustain pedal** stops a little higher (0.695 of its travel, was
  0.7): with the new bridge a chord let go under it rang longer than the
  owner chose, and this brings it back (60 dB in 11.1 s on the concert
  grand and 9.2 s on the upright, where 2.6.0 took 10.7 and 10.2).
- **Against the recordings**
  ([grand](Docs/validation/grand-room-bridge-benchmark-2026-11-12.md),
  [upright](Docs/validation/upright-room-bridge-benchmark-2026-11-12.md)):
  on the notes 1.0.0 never fitted, the grand's level difference between
  the channels stands 5.3 dB from the Salamander's (5.7 in 2.6.0), its
  level 2.1 (2.5), its first half second 6.3 (6.5), its noise 6.7 (7.0),
  its attack 6.3 (6.4) and its partials 7.9 (7.9): 7.0 (7.1) in the middle
  and 7.2 (7.5) from C6 up, but 9.9 (9.5) in the bass. Its rise is 12.7 ms
  off (12.2). The upright's partials stand 8.1 dB off (8.6) and its noise
  8.9 (9.2); its tuning 3.6 cents (3.1), its level difference between the
  channels 5.7 dB (5.1) and its sustain 10.6 (10.4) are further off. 71
  single-note scores of the grand and 29 of the upright are worse, listed
  in the reports.

### 2.6.0 — 2026-11-11 — what rings under a treble note

From A5 up something rings on under a note after the blow, as it does on the
recorded grand. The panel and the saved state are 2.5.0's; a 2.5.0 session
opens as saved and its top two and a half octaves sound different.

- **The case in the room**: the knock the blow gives the frame and the case
  (2.4.0) reached the microphones only through the board, and died away
  under a treble note twice as fast as on the Salamander grand. The room
  now hears it as well: from 280 to 710 Hz it stands 21 and 39 dB under its
  peak 100 and 300 ms on, where the recording's stands 21 and 36 and
  2.5.0's stood 28 and 47. Keys below A5 are as they were.
- **Against the recordings**
  ([grand](Docs/validation/grand-case-ring-benchmark-2026-11-11.md),
  [upright](Docs/validation/upright-case-ring-benchmark-2026-11-11.md)):
  on the notes 1.0.0 never fitted, the grand's first half second stands
  6.5 dB from the Salamander's in third octaves (7.0 in 2.5.0), its attack
  6.4 (6.6) and the noise between its partials 7.0 (7.5); from C6 up 7.9
  (9.6), 7.2 (7.8) and 7.5 (9.1). The upright's stand 9.0 (9.3), 7.4 (7.6)
  and 9.2 (9.5). The other scores moved by 0.1 or less. Two single-note
  scores of the grand and one of the upright are worse, listed in the
  reports.
- **The benchmark's noise score** counted a render's partial that stood off
  the recording's twice, as a missing partial and as noise; it is now left
  out of the noise. 2.5.0's noise reads 7.5 dB by it (7.6 before) and the
  upright's 9.5 (9.7).

### 2.5.0 — 2026-11-11 — the string scale

The strings are as stiff as the recorded pianos' are, so a note's upper
partials sit where a real piano's do. The panel and the saved state are
2.4.0's; a 2.4.0 session opens as saved and sounds different.

- **Strings of the measured stiffness**: the plain strings were 10 to 100 %
  stiffer than the Salamander grand's and the Helsinki upright's, which put
  middle C's twentieth partial 18 cents sharp of the recorded note's and
  C3's thirtieth 37 cents. The plain strings now keep their length down to
  the break and the wound strings have their own run to A0; the concert
  grand's inharmonicity stands within 8 % of the Salamander's from C3 to
  F♯6. The tuner's stretch follows the new partials.
- **Against the recordings**
  ([grand](Docs/validation/grand-string-scale-benchmark-2026-11-11.md),
  [upright](Docs/validation/upright-string-scale-benchmark-2026-11-11.md)):
  on the notes 1.0.0 never fitted, the grand's partials stand 7.9 dB from
  the Salamander's (8.2 in 2.4.0, their first move since 2.0.0) and its
  tuning 2.1 cents (3.2); the upright's 8.4 dB (9.6) and 3.2 cents (4.3).
  The other scores moved by 0.2 or less. 13 single-note scores of the grand
  and 11 of the upright are worse, all listed in the reports.
- Keys re-voiced and each piano's typical playing re-pinned to −9 VU.

### 2.4.0 — 2026-11-11 — the key presses

No two presses of a key sound alike, the thump under a note is the action
catching the hammer, and the top octave is set against the recordings. The
panel and the saved state are 2.3.0's; a 2.3.0 session opens as saved and
sounds different.

- **Key noises that vary**: a key landing or coming back, a damper and the
  pedal were the same sound every time. Each knock now draws its own level,
  each of its body modes a level and a phase, and its click a rise and a
  level in each band: two returns of one key differ by 1.4 to 1.9 dB and
  are 0.60 to 0.75 alike, where the Salamander grand's neighbouring keys
  differ by 1.5 dB and are 0.56 alike.
- **Two knocks under a note**, where one thump came with the blow. Recorded
  notes hold a thump under 180 Hz that comes 14.5 to 22 ms after the onset,
  later the softer the note: the action catching the hammer on its way
  back. The model's arrives within 4 ms of the Salamander's at seven
  velocity layers and stands within 4 dB of it in the median from C4 to C8
  (single keys up to 14 dB off), and no two catches are alike. Above 180 Hz
  a knock comes with the blow, from A5 up only, where the strings end on the
  frame's capo d'astro bar: 2 to 4 dB over the recording's from A6 to C8.
  Nothing precedes a bass note any more.
- **The top octave**: the hammers above C5 are harder (by three quarters of
  a decade at C8), the bridge holds the top strings in full, and they lose
  more on their own. The fundamentals of C7, F♯7 and C8 fall 28 to 35 dB in
  their first 300 ms, where the Salamander's fall 21 to 36 and 2.3.0's fell
  8 to 15; a soft note's stands 9 to 17 dB under a mezzo-forte one's, where
  the Salamander's stands 8 and 2.3.0's stood 12 to 20.
- **The room in the close pair**: what a treble note leaves from 280 to
  710 Hz, 300 ms after the knock under it, stood 67 dB down; it stands 47,
  the Salamander's 36. Room still sets how much.
- **The upright's thump** is set against a recorded upright (MAPS,
  ENSTDkCl): within 3.1 dB of it in three bands at three velocities.
- **Level**: each piano's typical playing stays at −9 VU.
- **Against the recordings**: on the Salamander grand's notes 1.0.0 never
  fitted, the attack is closer (7.8 to 6.6 dB), the first half second (8.1
  to 7.0), the noise between the partials (9.3 to 7.8), the sustain (8.7 to
  8.4) and the rise (15 to 13 ms); from C6 up the first half second moves
  from 12.7 to 9.6 dB and the partials from 9.0 to 7.5. Further off: the
  tuning (2.8 to 3.2 cents), the decay (3.7 to 4.1 dB/s; from C6 up 5.3 to
  7.0), the envelope (4.2 to 4.6 dB) and the bass's partials (8.6 to
  9.7 dB), the price of the room in the close pair. 106 single-note scores
  are worse, where 2.3.0 had six: the furthest F♯3's rise (41 to 51 ms),
  C8's decay (7.8 to 15.4 dB/s) and sustain (18.8 to 22.4 dB) and A3's
  noise (7.4 to 10.6 dB)
  ([report](Docs/validation/grand-key-presses-benchmark-2026-11-11.md)). On
  the Helsinki upright's the attack (8.5 to 7.5 dB), the first half second
  (10.2 to 9.1) and the noise (11.2 to 9.8) are closer and the partials
  further off (8.6 to 9.6 dB); 39 single-note scores are worse, the furthest
  D♯1's rise (38 to 50 ms) and E7's decay (3.6 to 11.6 dB/s)
  ([report](Docs/validation/upright-key-presses-benchmark-2026-11-11.md)).

### 2.3.0 — 2026-11-11 — the open strings

The strings whose dampers are off answer a blow as recorded pianos' do. The
panel and the saved state are 2.2.0's; a 2.2.0 session opens as saved and
sounds different.

- **Under the pedal**: a blow now moves the iron frame the strings end on,
  and that sets every open string ringing. Between a note's partials the
  parlor grand held 25 dB less than the Yamaha C3's pedal-down takes; it
  holds 6 to 8 dB less.
- **The top strings**, which have no dampers, ring under every note: 40 dB
  too quietly before, within 3 dB of the Salamander grand's under a forte
  note from C5 to F♯7. They ring longer too (about 28 dB/s where they died
  at 35 to 80; the recording's take 8 to 35), since a unison out of tune
  loads the bridge once, not once a string.
- **Level**: each piano's typical playing stays at −9 VU.
- **Against the recordings**: on the Salamander grand's notes 1.0.0 never
  fitted, the first half second is closer (8.9 to 8.1 dB, from C6 up 15.4 to
  12.7), the noise between the partials (9.9 to 9.3), the sustain (9.1 to
  8.7) and the attack (8.1 to 7.8); the partials are 0.04 dB further off.
  Six single-note scores are worse, five of them the channels' likeness at
  C8, F♯7 and D♯7
  ([report](Docs/validation/grand-open-strings-benchmark-2026-11-11.md)). On
  the Helsinki upright the attack, the first half second and the noise are
  closer by 0.1 to 0.3 dB; on the notes 1.0.0 never fitted the partials (8.5
  to 8.6 dB) and the decay (5.6 to 5.7 dB/s) are further off, and two
  single-note scores are worse
  ([report](Docs/validation/upright-open-strings-benchmark-2026-11-11.md)).

### 2.2.0 — 2026-11-11 — an even scale

The keys are voiced. The panel and the saved state are 2.1.0's; a 2.1.0
session opens as saved and sounds different.

- **Even keys**: a board answers each frequency in its own way, so 2.1.0's
  keys came out of the microphones 2.2 to 2.8 dB apart from one to the next
  on average, single keys 7 to 11 dB off the line through the keyboard. Each
  key's strings now pull on the board by what puts the key on that line in
  the microphone mix that is set: neighbours stand 0.3 to 0.4 dB apart at
  the default Lid and Soundboard, in single pairs and in mixes, and 0.9 to
  1.6 dB at other Lid and Soundboard settings (2.0 to 2.8 dB before).
- **Level**: each piano's typical playing is pinned to −9 VU again.
- **Against the recordings**: the loudness error across the Salamander
  grand's notes falls from 3.4 to 2.5 dB on the notes 1.0.0 never fitted
  (3.7 to 2.7 dB on the fitted ones) and the noise between the partials from
  10.1 to 9.9 dB; no other score moves by more than 0.2. 21 single-note
  scores are worse, the furthest F♯4's rise (16 to 22 ms) and noise (5.7 to
  7.4 dB) and the levels of D♯7 and A5 (by 1.6 to 1.7 dB)
  ([report](Docs/validation/grand-even-scale-benchmark-2026-11-11.md)). On
  the Helsinki upright the level error falls from 5.0 to 4.3 dB on the
  fitted notes; on the 21 notes 1.0.0 never fitted the noise is further off
  (11.0 to 11.4 dB) and the rise (12.6 to 13.0 ms), and 15 single-note
  scores are worse, the furthest F♯4's rise (1.7 to 8.5 ms)
  ([report](Docs/validation/upright-even-scale-benchmark-2026-11-11.md)).

### 2.1.0 — 2026-11-11 — velocity, the stereo image and a closer fit

The physical model fitted closer to the recordings. The panel and the saved
state are 2.0.0's; a 2.0.0 session opens as saved and sounds different.

- **Velocity**: the hammer's speed now follows the velocity, so that at
  Dynamics 0.5 the notes' levels stand within 2 dB of the Salamander grand's
  sixteen layers from velocity 31 up and 2.6 dB under them below it.
  2.0.0's speeds were even in dB, which left its soft and medium notes
  2.5 dB too quiet and its hardest 4.5 dB too loud against those layers.
  Dynamics spans 10 dB at 0, 25 dB at 0.5 and 40 dB at 1.
- **Felt**: the felt stiffens more steeply under a harder blow, fitted to
  the same layers, so soft notes are darker and hard ones brighter. Hammer
  and the practice felt cover half as many decades again, which keeps what
  each did to the tone.
- **Stereo image**: wider. A microphone pair's channels may now be up to a
  quarter turn out of step at each mode of the board, where 2.0.0 held them
  within 70°: on the first demo's phrase the channels' correlation is 0.33
  where it was 0.49, and each pair still sums to mono (Close 0.33, XY 0.67,
  Live 0.31, Distant 0.06).
- **Top end**: the board radiates fully up to 6 kHz, where 2.0.0's began to
  fall at 3 kHz. On the first demo's phrase the concert grand holds 3.6 dB
  more in the 2 kHz octave, 3.7 dB at 4 kHz and 7.1 dB at 8 kHz.
- **Treble sustain**: the bridge takes less from the strings between D♯3 and
  D6, so the upper keys ring longer.
- **Level**: each piano's typical playing is pinned to −9 VU again.
- **Against the recordings**: closer to the Salamander grand than 2.0.0 on
  ten of the benchmark's twelve scores, on the notes 1.0.0 never fitted
  (partial levels 11.7 to 8.2 dB, decay 5.5 to 3.7 dB/s, sustain 10.9 to
  9.1 dB). Its two stereo scores did not improve (the channels' level
  difference 5.4 to 5.6 dB, their correlation 0.21 as before), and 97
  single-note scores are worse, C3's rise the furthest (19 to 57 ms)
  ([report](Docs/validation/grand-velocity-stereo-benchmark-2026-11-11.md)).
  The upright is benchmarked against the Helsinki recordings for the first
  time, and there the change is mixed: on the notes 1.0.0 never fitted the
  partials (8.8 to 8.4 dB), the tuning (6.1 to 4.7 cents) and the envelope
  are closer, and the attack (7.7 to 8.5 dB), the first half second, the
  sustain (9.9 to 10.8 dB), the decay, the noise between the partials and
  the rise are further off
  ([report](Docs/validation/upright-velocity-stereo-benchmark-2026-11-11.md)).

### 2.0.0 — 2026-11-11 — a physical piano

The strings, hammers, soundboard and microphones are a new engine, written
from nothing: a physical model in place of 1.x's partials fitted from
recordings of five pianos. The action's noises, the pedals, the keyswitches
and the output stage are 1.0.0's.

- **Four pianos**: Concert Grand (2.74 m), Parlor Grand (1.86 m), Baby Grand
  (1.50 m) and Upright (1.25 m), each a string scale, hammers, soundboard and
  case of its size. The five measured pianos and their part-by-part builds
  are gone.
- **The piano's controls**: Hammer (soft to hard felt), String age, Detune
  (the unisons), Stretch (the tuner's), Dynamics (the span from the softest
  to the hardest blow), Lid, Soundboard, Sympathetic, Duplex and a Practice
  felt. Brightness, Resonance, Stiffness, Unisons, Ring, Quality and Tube Mic
  are gone.
- **Four microphone pairs**, each with its own level: Close (over the
  hammers), XY (at the lid), Live (in the room) and Distant (across it), and
  a Room control for the pairs that hear the room.
- **Twelve factory presets** for the new pianos in the old ones' program
  slots, six under the names they had; four demo phrases are renamed for
  them.
- **A full sustain pedal** rings about as long as the one chosen by ear on
  2026-10-30: a chord let go under it falls 60 dB in 9.6 s on the concert
  grand and 10.4 s on the upright.
- **Sessions**: a 1.x session opens with its Output, Width, Tuning, Felt
  mute, Mechanics and pedals as saved, its Brightness as Hammer and its
  Resonance as Sympathetic, on the Concert Grand (the Upright where its
  strings were mostly the Helsinki upright's) with the other new controls at
  their defaults. It does not sound as it did. The plug-in's identifiers are
  unchanged.
- **CPU**: the eight demos take 6 to 13 % of one core on a development
  machine; there is no Quality setting.
- **Against the recordings**: further from the Salamander grand than 1.0.0 on
  every score, since 1.0.0 was fitted to it and 2.0.0 is fitted to no one
  recording ([report](Docs/validation/grand-recording-benchmark-2026-11-11.md)).
  The upright is not yet benchmarked against its recordings.

### 1.0.0 — 2026-11-10 — the first release, and the last of the modal engine

0.4.38's engine, unchanged: partials fitted from recordings of five pianos.
Its forty versions from 0.2.0 are in the
[release history of 1.x](Docs/release/release-history-1.x.md), and
[how that engine worked](Docs/research/modal-engine-1.0.0.md) is kept beside
it.

## Downloads

<!-- build-download-begin -->
**[Download main build 124](https://github.com/protocodus/virtual-instrument-keyra/actions/runs/43200941050/artifacts/13943032727)**, built from [`8c0744366e04`](https://github.com/protocodus/virtual-instrument-keyra/commit/8c0744366e04ca2f9665bc797b71c21106dd86fa). It holds the macOS, Windows and Linux packages, `SHA256SUMS` and `BUILD.txt`.
<!-- build-download-end -->

---

## How it works

### The piano model

`Source/DSP/PianoModel.cpp` is the piano. Nothing in it is a recording or a
table fitted note by note: a piano is a description (its `Design`, a string
scale and the constants beside it) and the controls. The papers each part
follows are cited beside the code.

**Strings.** Each string is the modes of a stiff, lossy string hinged at both
ends, partial k at k f0 √(1 + B k²) (Fletcher 1964), up to 160 partials in
the bass and three at C8. The scale is built from each piano's size: speaking
lengths that double a little less than every octave down from C8's 51.5 mm,
no plain string longer than 0.87 of A0's, the wound strings running from
there to A0's length on a bridge of their own (set against the
inharmonicity the Salamander grand's and the Helsinki upright's partials
give), plain steel wire from 0.775 mm at the top to
1.125 mm at the break, copper-wound strings below it, one string a key at
the bottom, then two, then three. Tension, mass and inharmonicity follow from
those (B is 0.00028 at the concert grand's middle C and 0.00031 at the baby
grand's). Every partial loses by the string's own damping, which rises with
frequency, and by what the bridge takes from it.

**Hammers.** A hammer is a mass on felt that stiffens as it is compressed and
gives way while it is held: Stulov's hysteretic felt with his measured
hammers, given at C2, C4 and C7 as Chaigne and Askenfelt's three hammers are
and carried across the keys. The blow is solved against the string's own
motion at the strike point, twice a sample at 44.1 and 48 kHz, for as long
as they touch, so a hard blow is brighter because the felt is stiffer under
it and a restrike meets a string already moving. The hammers' stiffness and
the strings' losses are fitted to notes of one recorded grand (Jon Meyer's
"Steinway Grand" for Decent Sampler, from the owner's reference set); the
upright's stiffness to eleven forte notes of a recorded upright (MAPS,
ENSTDkCl). How steeply the felt stiffens is fitted to the Salamander grand's
sixteen velocity layers, with the force kept where the felt is 1 mm in.

**Velocity.** Full velocity is a blow of 5 m/s, and under it the hammer's
speed is the velocity to a power that Dynamics sets: 1 at 0.5, where the
notes' levels stand within 2 dB of the Salamander's layers from velocity 31
up (2.6 dB under them below it) and within 2 dB of a Disklavier's notes
(MAPS, ENSTDkCl). The softest key still strikes, at 0.28 m/s.

**Unisons.** The strings of a key, each in two polarisations, share the
bridge, whose admittance couples them (Weinreich 1977): that gives the
prompt sound, the slower aftersound and their beating. The first 48 partials
of each string are kept apart, the first 16 also across the bridge; above
them the strings move together. From C5 down the strings' stretching as
they swing pulls the bridge at twice each partial's frequency (Conklin
1999), the phantom partials of a bass note.

**Soundboard.** The bridge drives the modes of a ribbed plate smeared into
one orthotropic plate, up to 224 of them under 2.6 kHz, with a point
impedance of about 2500 kg/s and a modal density of about 0.05 per Hz, as
measured boards have (Ege, Boutillon and Rebillat 2013; Giordano 1998). The
bridge's admittance at each key comes from those modes, so a string's decay
depends on where it crosses the bridge. The long bridge is a beam: a plain
string's force reaches each mode as the mean of the mode's shape along half
the bridge's bending wavelength at that frequency; the wound strings' short
bridge drives the board at a point. Above the modes the board moves and
radiates near the bridge only.

**The knocks under a note.** Recorded notes hold two knocks under their
fundamental, and so does the model. The thump, under about 350 Hz, is the
action catching the hammer as it comes back off the string: 14 ms and the
time the hammer takes over 11 mm at the speed it rebounds with, so later
after a soft blow, and at once on the upright. Its momentum goes through the
key into the keybed, and the case hands it to the board's edge, three
quarters of it along the whole edge and the rest at the key's own place. The
knock, above 180 Hz, comes with the blow and only from A5 up, where the
strings end on the frame's capo d'astro bar instead of on agraffes: the
blow's lean on that bar reaches the board's edge at the key's place. Both
are fitted to the Salamander grand's notes, the upright's thump to a
recorded upright's (MAPS, ENSTDkCl); no catch is like the last, by 2 dB and
a fifth of its time.

**Voicing.** A board answers each frequency in its own way, so a key comes
out of the microphones stronger or weaker than its neighbours, as a piano's
keys do before a technician voices them: unvoiced, the model's neighbours
stand 3.7 to 4.5 dB apart and single keys up to 12 dB off.
`KeyraLevels --write-keys` measures what each key's strings alone give each
microphone pair, and every two pairs together, since pairs in a mix add as
waves, against a smooth line through the keys, and writes
`Source/DSP/KeyVoicing.h`. Each key's strings pull on the board by what
brings the key onto that line in the mix that is set, by no more than 12 dB
either way. The table is measured at the default Lid and Soundboard and at
half velocity; the knocks under a note are not voiced.

**Sympathetic strings and duplex scales.** Every string whose damper is
lifted, by its key, the sostenuto or the pedal, answers what is played, ten
partials and two duplex-scale modes a key. Two things drive it: the
bridge's motion, and the iron frame, which gives under a blow's lean and
moves the string's near end (1.2e-7 m/N below 500 Hz, less above, fitted to
the Yamaha C3's pedal-down takes and the Salamander grand's top strings). A
unison rings as one mode: in tune its strings load the bridge once each,
and further apart than the bridge couples them, once in all (Weinreich
1977). The top keys have no dampers (from F♯6 on the concert grand) and
always answer. The upright has no duplex scales.

### Five pianos

| Piano | A0's speaking length | Soundboard | First plain-steel key | First key without a damper |
| --- | --- | --- | --- | --- |
| Concert Grand, 2.74 m | 2.01 m | 1.45 × 1.55 m | F2 | F♯6 |
| Parlor Grand, 1.86 m | 1.40 m | 1.42 × 1.12 m | B2 | F♯6 |
| Baby Grand, 1.50 m | 1.14 m | 1.40 × 0.86 m | C♯3 | F6 |
| Upright, 1.25 m | 1.18 m | 1.40 × 0.95 m | D♯3 | D♯6 |
| Studio Grand, 2.0 m | 1.60 m | 1.43 × 1.22 m | B2 | F♯6 |

The dimensions are typical of each kind of piano, not one maker's
instrument. The smaller pianos have shorter, stiffer bass strings (more
inharmonic, so tuned with more stretch), lighter and harder hammers and a
smaller board. Changing the piano stops what sounds.

### Microphones and the room

Each mode's radiation to each microphone is Rayleigh's integral over the
plate, with the floor's reflection and, on a grand, the lid's at three
positions (closed, the short stick at 14°, open at 38°). Four pairs hear the
piano, each with its own level:

- **Close**: a spaced pair inside, 20 cm over the strings by the hammers
  (behind an upright's board). The pop sound.
- **XY**: a coincident cardioid pair at the open lid, about a metre off
  (behind an upright).
- **Live**: a spaced pair in the room, 2.3 m from a grand's side; over the
  player's head at an upright.
- **Distant**: a wide pair across the room, 4 to 6 m off.

At the same level every pair plays the piano as loud as the close pair: a
level is a balance, and the distance is in the sound already. The room is a
feedback delay network of sixteen lines under a Hadamard mix (Jot and
Chaigne 1991) ringing 0.8 s,
which hears the piano as the distant pair does and which each pair hears by
its distance, the close pair too (set against what the Salamander grand's
treble notes leave after the knock under them); Room sets how much. The
room also hears the case: the knock the blow gives the frame under the top
strings goes to it directly, through three allpass sections (Schroeder
1962), as well as through the board. Width at 0.75 is the pairs' own image and
0 is mono.

A pair is placed so that it sums to mono: no mode of the board reaches one
microphone more than 70° out of step with the other, or half the pair's
spacing in wavelengths where that is more, up to a quarter turn. A spaced
pair so opens from 70° to 90° (between 220 and 280 Hz for a grand's close
pair) and the coincident pair is held at 70°. The quarter turn is as far as
a phrase through the distant pair allows before it sums out of phase; the
Salamander grand's two channels are less alike still (Known gaps). The
recordings at hand show no steady lean of low keys to one side and high
keys to the other, so the model adds none: where a key sits in the image is
what the board and the microphones give it.

### Controls

| Control | Range | What it changes |
| --- | --- | --- |
| Piano | five | The piano that plays (above) |
| Hammer | −1 to 1 | The felt's stiffness, a decade and a half from soft and worn-in to hard: ×10^(0.75 Hammer) |
| String age | 0 to 1 | Old strings lose their upper partials' sustain, wound ones most, and beat against themselves |
| Detune | 0 to 1 | How far apart a unison's strings are tuned: pure at 0, 6 cents of spread at 1, a bar piano (on a grand, half that from C5 up). 0.3 by default |
| Stretch | 0 to 2 | The tuner's stretch. At 1, octaves are tuned on the strings' own partials (4:2 in the treble, 6:3 in the bass, Railsback's curve); 0 is equal temperament |
| Dynamics | 0 to 1 | The span of hammer speeds from the softest to the hardest blow under 5 m/s at full velocity: 10 dB at 0, 25 dB at 0.5, where the speed follows the velocity, and 40 dB at 1 |
| Lid | 0 to 1 | Closed, the short stick at 0.5, open; an upright's top |
| Soundboard | 0 to 1 | How long the board rings: its loss halves from 0.5 to 1 and doubles to 0 |
| Sympathetic, Duplex | 0 to 1 | How strongly the open strings and the duplex scales answer |
| Close, XY, Live, Distant | 0 to 1 | Each microphone pair's level |
| Room | 0 to 1 | The room in the pairs that hear it |
| Width | 0 to 1 | The stereo image |
| Practice felt | 0 to 1 | A felt strip between hammers and strings: up to three decades softer |
| Felt mute | 0 to 1 | Felt laid on every sounding string, held or not (the mod wheel) |
| A4 tuning | 415 to 466 Hz | Concert pitch |
| Mechanics | 0 to 2 | How loud the action plays |
| Output | 0 to 1 | The output level |

The hammer, the practice felt, the dynamics and the strings' age are taken
by the next strike; everything else applies to what sounds.

### The action

The keys landing and coming back, the dampers falling and the sustain
pedal's knocks are 1.0.0's, unchanged: knocks on measured body modes and
bursts of band noise, fitted as numbers from the Salamander grand's
recordings under the three grands and from the Helsinki upright's under the
upright, in the room those were recorded in. No recorded waveform plays.
They follow the velocity of the strike they belong to, and Mechanics sets
their level. No two are alike: each knock draws its level (1 dB), each body
mode its level and phase (2 dB, a radian), and the click its rise and each
band's level (3 dB), set against how far the Salamander's keys stand from
their neighbours. They play beside the model and do not drive its strings.

### Pedals and keyswitches

Sustain lifts the dampers continuously, and the half pedal lies between
about 64 and 89 of CC64: two seconds after a chord of C3, C4, C5 and C6 is
let go it stands 87 dB under where it was at 64, 47 dB at 76, 22 dB at 86
and 18 dB from 89 up, against 95 dB with the pedal up. At the owner's
choice a full pedal stops
short of lifting the felt clear, so that it still grazes the strings: a
chord of C3, C4, C5 and C6 let go under it falls 60 dB in 11.1 s on the
concert grand, 8.6 s on the studio grand, 10.6 s on the parlor grand, 9.0 s
on the baby grand and 9.2 s on the upright (2.9.0, in 0.1 s windows), where clear of the strings the concert grand takes
17.4 s. Sostenuto captures the keys held as it crosses halfway down. Soft is
una corda on a grand: the hammers shift off each unison's last string and
strike with softer felt. On the upright it halves the hammers' run, so they
arrive √½ as fast. Each pedal takes the largest of its panel control, its
MIDI controller (CC64, CC66, CC67) and its momentary keyswitch (MIDI 14, 13,
12, below the piano's A0). The sustain pedal knocks within 0.08 of either
end of its travel, once each way.

### Presets, MIDI and saved state

The twelve factory presets in `Source/DSP/KeyraPresets.h` set the piano, its
controls from Hammer to Duplex, the four microphone levels, Room, Width and
the practice felt;
Output, Tuning, Mechanics, the mod wheel's mute and the pedals keep their
values. Notes, pedals and pitch bend (two semitones each way) are dispatched
at their sample positions; each MIDI channel owns its keys and pedals, CC1
is the felt mute, and CC120, CC121 and CC123 are honoured per channel. Every
strike lands a little harder or softer than its velocity, as a player's do.
The plug-in saves 24 parameters; the piano is not offered for automation. A
1.x session loads as the Version history describes. The
[user guide](Docs/guide/user-guide.md) describes every control.

### Playing level

`Tools/KeyraLevels.cpp` reads every piano and preset on Reason's channel
meter (the louder channel's RMS over 300 ms, 0 VU at −12 dBFS), playing
single notes every fourth semitone and eight chords at velocities 70, 90 and
110 for typical playing. Each piano's output scale puts its default sound's
typical playing at −9 VU at the default Output; a preset has no level of its
own, and its microphone levels keep it within 2 dB of that (they read −10.0
to −7.9 VU). The output stage after it is the portfolio's compressor and
peak limiter with 1.0.0's half-drive response: nothing passes −1.5 dBFS, and
its 2.5 ms look-ahead is reported to the host.

### The full physical research

[`Experiments/`](Experiments/README.md) holds the earlier offline research:
a nonlinear reference solver and a full physical block API calibrated
against a full-range corpus. None of it is in the plug-in, and 2.0.0's model
is written independently of it.

## Known gaps

- **Not fitted note by note.** The model is a description of a piano with a
  few constants set against recordings, and note by note it stands further
  from the Salamander grand than 1.0.0, which was fitted to those
  recordings, on every score of `Tools/benchmark_recordings.py`: on the
  notes 1.0.0 never fitted, the partials' levels differ by 7.7 dB where
  1.0.0's differed by 5.3, the tuning by 2.2 cents against 0.9, the decay by
  3.8 dB/s against 2.1 and the rise by 13 ms against 4.5
  ([2.0.0 against 1.0.0](Docs/validation/grand-recording-benchmark-2026-11-11.md),
  [2.1.0 against 2.0.0](Docs/validation/grand-velocity-stereo-benchmark-2026-11-11.md),
  [2.2.0 against 2.1.0](Docs/validation/grand-even-scale-benchmark-2026-11-11.md),
  [2.3.0 against 2.2.0](Docs/validation/grand-open-strings-benchmark-2026-11-11.md),
  [2.4.0 against 2.3.0](Docs/validation/grand-key-presses-benchmark-2026-11-11.md),
  [2.5.0 against 2.4.0](Docs/validation/grand-string-scale-benchmark-2026-11-11.md),
  [2.6.0 against 2.5.0](Docs/validation/grand-case-ring-benchmark-2026-11-11.md),
  [2.7.0 against 2.6.0](Docs/validation/grand-room-bridge-benchmark-2026-11-12.md),
  [2.8.0 against 2.7.0](Docs/validation/grand-unison-spread-benchmark-2026-11-12.md)).
  2.7.0 put the bass's partials 0.3 to 0.4 dB and the rise 0.5 ms further
  off, and 71 single-note scores.
  The furthest are the treble's sustain (11 dB off in third octaves) and
  the bass's rise (23 ms on average). 2.4.0 moved the tuning, the decay and
  the bass's partials further off, and 106 single-note scores; 2.5.0 brought
  the tuning and the partials closer and left 13 single-note scores worse. Whether each sounds better
  is the owner's verdict by ear (`Docs/decisions.md`, 2026-11-11), not a
  measurement.
- **The upright against its recordings.** Against the Helsinki upright the
  partials' levels differ by 8.1 dB, the tuning by 3.6 cents, the decay by
  5.4 dB/s and the rise by 13 ms on the notes 1.0.0 never fitted; 2.1.0
  moved its attack, sustain and noise further off than 2.0.0's, 2.2.0 its
  noise a little further, 2.3.0 its partials and decay, and 2.4.0 its
  partials by another 1.0 dB
  ([2.1.0](Docs/validation/upright-velocity-stereo-benchmark-2026-11-11.md),
  [2.2.0](Docs/validation/upright-even-scale-benchmark-2026-11-11.md),
  [2.3.0](Docs/validation/upright-open-strings-benchmark-2026-11-11.md),
  [2.4.0](Docs/validation/upright-key-presses-benchmark-2026-11-11.md));
  2.5.0 took 1.2 dB off its partials and 1.1 cents off its tuning
  ([2.5.0](Docs/validation/upright-string-scale-benchmark-2026-11-11.md));
  2.6.0 its first half second by 0.3 dB and put its partials 0.1 dB further
  ([2.6.0](Docs/validation/upright-case-ring-benchmark-2026-11-11.md));
  2.7.0 took 0.5 dB off its partials there (five treble notes carry it; on
  the notes 1.0.0 fitted 0.1) and put its tuning 0.5 cents, its sustain
  0.2 dB and its bass's partials 0.4 dB further off
  ([2.7.0](Docs/validation/upright-room-bridge-benchmark-2026-11-12.md)).
- **The bass strings' stiffness.** The concert grand's wound strings are 14
  to 53 % less stiff than the Salamander's, a grand 0.7 m shorter, so in
  the bass the benchmark still looks for upper partials where the model
  does not put them; the upright's are 6 to 41 % under the Helsinki's. No
  recorded concert grand's bass is in the reference set to say what the
  model's should be.
  Against a second recorded upright (MAPS, ENSTDkCl) the notes from C6 up
  stand 1 to 4 dB louder beside the middle ones than recorded, and the
  thump arrives up to 10 ms later.
  That library's five layers cover wide velocity ranges; the velocity each
  was played at is not documented.
- **A narrower image than the recordings.** Between 500 Hz and 2 kHz the
  two channels of a forte note are 0.4 alike on average where the
  Salamander grand's are 0.05, and the benchmark's two stereo scores stand
  where 2.0.0's did.
- **Less top end than 1.0.0.** On the first demo's phrase the concert grand
  holds 2 dB less in the 4 kHz octave and 7 dB less at 8 kHz than 1.0.0's
  grand; Hammer at +0.6 holds 4, 7 and 18 dB more in the 2, 4 and 8 kHz
  octaves than at −0.6. Against the Salamander's single notes, a note's
  share above its sixth partial is 4 to 8 dB less at every velocity, and the
  middle of the keyboard holds 13 to 15 dB less in the 2 kHz octave from
  mezzo-forte up.
- **The open strings, where they are still off.** Under the pedal a note
  leaves 6 to 8 dB less between its partials than the Yamaha C3's
  pedal-down takes (`Tools/benchmark_pedal_wash.py` on the parlor grand), 10
  to 12 dB less after three seconds, and a key from about C♯4 up rings the
  strings below its own pitch 8 to 13 dB too much. The top strings ring 7 to
  10 dB too much under A7 and C8 and die about twice as fast as the
  Salamander's. The note itself does not gain under the pedal where the
  takes gain 3 to 7 dB between C3 and A4. The frame's give is fitted to two
  recordings that disagree by a few dB.
- **The knocks under a note.** Key by key the thump stands up to 14 dB
  from the Salamander's (within 4 dB in the median), and it rings on for a
  shorter time: the recording's peaks 24 to 42 ms after the onset, the
  model's 20 to 27. The knock with the blow is 2 to 12 dB weak from C6 to
  F♯6, and from C5 to A5 the model holds something under 180 Hz with the
  blow that the recording does not. That the catch and the capo d'astro bar
  are their causes is the reading the timing and the keys suggest, not a
  measurement of a piano's action; the literature names the key meeting
  the key frame for the thump (Askenfelt and Jansson), which is not built
  or compared yet ([options](Docs/plans/realism-options-2026-11-11.md)). A Steinway's notes thump 8 to 10 dB
  harder than the Salamander's; the grands share one level.
- **The room against the recordings.** With the room in the close pair the
  bass's partials stand 1 dB further from the recordings than without it.
  What a treble note leaves under it now falls as the Salamander's does for
  300 ms (39 dB down against 36); after 400 ms that recording is at its own
  floor and says nothing (2.4.0 read its 47 dB at 600 ms as the piano).
  Between its partials a note from A5 to G♯6, where the knock itself is
  weak, still holds 4 to 11 dB less than the recording from 125 Hz to 2 kHz
  after its first 50 ms; the softest notes from A7 up hold 3 to 7 dB more
  from 250 Hz to 2.5 kHz; and from A4 up a loud note holds 10 to 40 dB less
  above 5 kHz.
- **The softest treble and the bass's level.** At the softest layer the
  keys from F♯6 up stand 5 to 13 dB quiet beside the middle of the keyboard
  against the Salamander's, and at the hardest up to 6 dB loud; the keys
  from C1 to F♯2 stand 1 to 8 dB quiet from a soft layer up, as in 2.3.0.
- **Rough partials.** Within a note a partial stands 6 to 10 dB from the
  mean of its neighbours where the Salamander's stand 2.5 to 5 dB: the
  model's board answers single frequencies more unevenly than a real one.
  The voicing evens the keys, not the partials within a key.
- **Evenness away from the default panel.** The voicing is measured at the
  default Lid and Soundboard, so at other settings neighbouring keys stand
  0.9 to 1.6 dB apart, and with the unisons' Detune at 1, 0.7 dB. One key
  (the concert grand's F♯5) needs more than the 12 dB the voicing allows
  and stays 1.5 dB off in one mix, and in the top treble, where the frame's
  knock is part of the sound, keys stand up to 1.3 dB off.
- **Slow bass onsets.** The lowest octaves take longer to rise than recorded
  grands do.
- **Uneven keys on the close pair.** Two keys lean to one side of the image
  on the Close pair.
- **The action does not ring the strings.** The recorded action noises play
  beside the model: a key's or the pedal's knock does not reach the
  soundboard's model. The pedal's whisper is the felt letting the strings
  go and holds, under 150 Hz, 25 to 35 dB less than the Salamander's
  pedal-down takes ring there; its level against the notes rests on the
  engine's pedal knock, 2.8.0's, not on a measurement of its own.
- **The Studio Grand is not fitted further.** Only its bass scale is set
  against the recordings; its microphones, hammers and voicing are the
  other grands' ways at its size, and the benchmark still scores the
  Concert Grand by default (`-- --body studio` scores this one).
- **Changing the piano cuts what sounds.** A new body starts silent.
- **CPU.** On a development machine (an Intel Xeon at 2.1 GHz, GCC 13) the
  eight demos take 6 to 14 % of one core and their heaviest 256-frame
  blocks 35 to 62 % of the block's time. 2.3.0 read 6 to 13 % and 20 to
  54 % there, and 5 to 11 % and 12 to 29 % on the CI runner (main build
  105). There is no Quality setting to lighten it.
- **Typical dimensions.** The five pianos are typical of their kinds, not
  one maker's instruments, and their soundboards are a smeared plate, not a
  ribbed board with its bridges.
- **The room** is a small feedback delay network, not a measured hall.
- **1.x sessions do not sound as they did.** They load mapped to the nearest
  piano (Version history).
- **Host acceptance.** pluginval, clap-validator, auval, Windows, manual DAW
  workflows and Reason are unverified for 2.0.0; the Rack Extension adapter
  still pins 1.0.0.

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
`-L fuzz` or `-L perf` selects a tier. `unit` holds `Keyra.PianoModel` (the
model's tuning, partials, hammer, decay, coupling and controls),
`Keyra.Engine` (MIDI, pedals, the action, block invariance) and
`Keyra.DspFuzzReplay`, the fuzz harness replaying `Tests/Fixtures/fuzz/` and
seeded inputs; `audio` is `Keyra.AudioDemos` and `Keyra.Levels`; and `perf`
is `Keyra.CpuBudget`, the demos timed in a Release build, which fails above
0.33 of real time, three times the slowest demo's median on the CI runner.
`KeyraDSPCxx17` compiles the engine as C++17, the Rack Extension toolchain's
standard. `-DKEYRA_ENABLE_SANITIZERS=ON` builds everything under ASan and
UBSan, and `-DKEYRA_BUILD_FUZZER=ON` (Clang) makes `KeyraDspFuzz` a libFuzzer
target. `scripts/validate-plugins.sh build-plugin Keyra aumu Kyra Ptoc
0x4b455952` runs pluginval, clap-validator and, on macOS, auval on a plug-in
build.

`build-dsp/keyra_render --events score.events --output out.wav` plays an
event score through the engine with any control set from the command line,
and `render_model --report --body upright` prints what each key of a piano
is built as: its strings, partials, length, tension, inharmonicity, stretch
and hammer.

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
purpose, commercial music included. The piano model holds no recording and no
table fitted from one note by note; its hammers and losses were set against
notes of Jon Meyer's "Steinway Grand" for Decent Sampler and of the MAPS
database's ENSTDkCl upright. The action's noises are numbers fitted from
Salamander Grand Piano V3 by Alexander Holm under CC BY 3.0 and from the
Helsinki 1967 Tube-Ribbon Edition by Mikko Patama, whose author permits
fitting numbers from them provided the recordings are not distributed. JUCE,
CLAP and the other dependencies keep their own licences.
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) lists them, with the licence
texts in `ThirdParty/`. The licensed Reason Jukebox SDK is not part of this
repository.
