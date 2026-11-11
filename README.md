# Keyra

Keyra is a physically modelled piano that plays no samples: felt hammers
thrown at stiff strings, the strings of each unison coupled at the bridge, a
soundboard of plate modes radiating to four microphone pairs, and the open
strings and duplex scales ringing with them. Four pianos are designed, a
concert grand, a parlor grand, a baby grand and an upright, and each is kept
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
| 3 | Warm Walnut | [03-warm-walnut.wav](Docs/audio/03-warm-walnut.wav) | 11.1 s | -7.3 dBFS |
| 4 | Felt Nocturne | [04-felt-nocturne.wav](Docs/audio/04-felt-nocturne.wav) | 10.7 s | -10.9 dBFS |
| 5 | Open Strings | [05-open-strings.wav](Docs/audio/05-open-strings.wav) | 11.7 s | -2.4 dBFS |
| 6 | Upright | [06-upright.wav](Docs/audio/06-upright.wav) | 11.6 s | -3.3 dBFS |
| 8 | Pop Upright | [08-pop-upright.wav](Docs/audio/08-pop-upright.wav) | 11.6 s | -1.5 dBFS |
| 9 | Baby Grand | [09-baby-grand.wav](Docs/audio/09-baby-grand.wav) | 9.7 s | -7.6 dBFS |
| 10 | Distant Hall | [10-distant-hall.wav](Docs/audio/10-distant-hall.wav) | 10.8 s | -4.1 dBFS |

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
**[Download main build 110](https://github.com/protocodus/virtual-instrument-keyra/actions/runs/43007331777/artifacts/13853086060)**, built from [`34a319c8140f`](https://github.com/protocodus/virtual-instrument-keyra/commit/34a319c8140fb4b2baad570397748e5a5d4ad7a3). It holds the macOS, Windows and Linux packages, `SHA256SUMS` and `BUILD.txt`.
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
lengths that double a little less than every octave down from C8's 50 mm
until the case bends them over, plain steel wire from 0.775 mm at the top to
1.125 mm at the break, copper-wound strings below it, one string a key at
the bottom, then two, then three. Tension, mass and inharmonicity follow from
those (B is 0.00035 at the concert grand's middle C and 0.00049 at the baby
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
depends on where it crosses the bridge. Above the modes the board moves and
radiates near the bridge only. A blow also leans on the iron frame, which
knocks the board: the thump under a note's fundamental, fitted to the same
Steinway notes.

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
half velocity; the frame's knock is not voiced.

**Sympathetic strings and duplex scales.** Every string whose damper is
lifted, by its key, the sostenuto or the pedal, is driven by the
bridge's motion, ten partials and two duplex-scale modes a key. The top
keys have no dampers (from F♯6 on the concert grand) and always answer. The
upright has no duplex scales.

### Four pianos

| Piano | A0's speaking length | Soundboard | First plain-steel key | First key without a damper |
| --- | --- | --- | --- | --- |
| Concert Grand, 2.74 m | 2.01 m | 1.45 × 1.55 m | F2 | F♯6 |
| Parlor Grand, 1.86 m | 1.40 m | 1.42 × 1.12 m | B2 | F♯6 |
| Baby Grand, 1.50 m | 1.14 m | 1.40 × 0.86 m | C♯3 | F6 |
| Upright, 1.25 m | 1.18 m | 1.40 × 0.95 m | D♯3 | D♯6 |

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
feedback delay network of eight lines (Jot and Chaigne 1991) ringing 0.8 s,
which hears the piano as the distant pair does and which each pair hears by
its distance; Room sets how much. Width at 0.75 is the pairs' own image and
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
| Piano | four | The piano that plays (above) |
| Hammer | −1 to 1 | The felt's stiffness, a decade and a half from soft and worn-in to hard: ×10^(0.75 Hammer) |
| String age | 0 to 1 | Old strings lose their upper partials' sustain, wound ones most, and beat against themselves |
| Detune | 0 to 1 | How far apart a unison's strings are tuned: pure at 0, 6 cents of spread at 1, a bar piano. 0.3 by default |
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
their level. They play beside the model and do not drive its strings.

### Pedals and keyswitches

Sustain lifts the dampers continuously, and the half pedal lies between
about 64 and 89 of CC64: two seconds after a chord of C3, C4, C5 and C6 is
let go it stands 87 dB under where it was at 64, 47 dB at 76, 22 dB at 86
and 18 dB from 89 up, against 95 dB with the pedal up. At the owner's
choice a full pedal stops
short of lifting the felt clear, so that it still grazes the strings: a
chord of C3, C4, C5 and C6 let go under it falls 60 dB in 9.6 s on the
concert grand, 12.3 s on the parlor grand, 9.9 s on the baby grand and
10.4 s on the upright, where clear of the strings the concert grand takes
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
  notes 1.0.0 never fitted, the partials' levels differ by 8.2 dB where
  1.0.0's differed by 5.3, the tuning by 2.9 cents against 0.9, the decay by
  3.7 dB/s against 2.1 and the rise by 15 ms against 4.5
  ([2.0.0 against 1.0.0](Docs/validation/grand-recording-benchmark-2026-11-11.md),
  [2.1.0 against 2.0.0](Docs/validation/grand-velocity-stereo-benchmark-2026-11-11.md),
  [2.2.0 against 2.1.0](Docs/validation/grand-even-scale-benchmark-2026-11-11.md)).
  The furthest are the treble's first half second (15 dB off in third
  octaves) and the bass's rise (28 ms on average). Whether it sounds better
  is the owner's verdict by ear (`Docs/decisions.md`, 2026-11-11), not a
  measurement.
- **The upright against its recordings.** Against the Helsinki upright the
  partials' levels differ by 8.5 dB, the tuning by 4.6 cents, the decay by
  5.5 dB/s and the rise by 13 ms on the notes 1.0.0 never fitted; 2.1.0
  moved its attack, sustain and noise further off than 2.0.0's, and 2.2.0
  its noise a little further
  ([2.1.0](Docs/validation/upright-velocity-stereo-benchmark-2026-11-11.md),
  [2.2.0](Docs/validation/upright-even-scale-benchmark-2026-11-11.md)).
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
- **The open strings answer too weakly.** A struck treble note sets the top
  strings, which have no dampers, ringing: in the Salamander grand's notes
  each stands about 30 dB under the struck note's fundamental over the
  first second, and the model's stand 40 dB and more under that. This ring,
  not a knock, is what the recordings hold under a treble fundamental after
  the blow, and most of why the treble's first half second is the
  benchmark's furthest score. Under the pedal it is the same: a struck note leaves 19
  to 38 dB less between its partials than the Yamaha C3's pedal-down takes
  (25 dB in the median, `Tools/benchmark_pedal_wash.py` on the parlor
  grand), and the note does not gain under the pedal where the takes gain 3
  to 7 dB between C3 and A4.
- **The thump under the fundamental** is up to 12 dB stronger than the
  Salamander's from C4 to F♯5 and 2 to 10 dB weaker from A5 to F♯6.
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
  beside the model: a pedal going down does not set the freed strings
  whispering, and a key's knock does not reach the soundboard's model.
- **Changing the piano cuts what sounds.** A new body starts silent.
- **CPU.** The eight demos take 5 to 11 % of one core on the CI runner
  (main build 105), and their heaviest 256-frame blocks 12 to 29 % of the
  block's time; on a development machine (an Intel Xeon at 2.1 GHz, GCC 13)
  6 to 13 % and 20 to 54 %. There is no Quality setting to lighten it.
- **Typical dimensions.** The four pianos are typical of their kinds, not
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
