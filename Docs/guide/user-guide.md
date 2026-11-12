# Keyra

Keyra is an 88-key piano made by a physical model: hammers, strings, a
soundboard and microphones are computed as you play, and no samples are
loaded. You choose one of five pianos, keep it as you like it and place the
microphones. The keys', dampers' and pedals' own noises play beside it. What
is not yet verified for version 2.0.0 is listed in the README's Known gaps.

## Playing

Send MIDI notes A0–C8 (21–108). Velocity sets how fast the hammer is thrown:
a faster hammer is louder and, because its felt stiffens under the blow,
brighter. Each strike lands a little harder or softer than its velocity, as a
player's do. A note-on with velocity zero releases a key. Each MIDI channel
owns its keys and pedals; the strings are one piano's, so all channels play
the same strings.

The panel has three views, Piano, Body and Mics, and the tables below follow
them.

## The piano

| Control | Behavior |
| --- | --- |
| Piano | Concert Grand (2.74 m), Parlor Grand (1.86 m), Baby Grand (1.50 m), Upright (1.25 m) or Studio Grand (2.0 m). Smaller pianos have shorter bass strings, a smaller soundboard and lighter, harder hammers. Changing the piano stops what sounds. Not offered for automation |
| Hammer | The felt, from soft and worn-in at −1 to hard and bright at +1; 0 is the piano as built. Applies from the next strike |
| String age | 0 is new strings. Towards 1 the strings lose their upper partials' sustain, the wound bass strings most, and beat against themselves. Applies from the next strike |
| Detune | How far apart the two or three strings of a note are tuned: pure at 0, a well-kept piano at the default 0.3, a bar piano at 1 |
| Stretch | The tuner's stretch. At 1 the octaves are tuned to the strings' own slightly sharp overtones, as a tuner does; 0 is equal temperament, 2 twice the stretch |
| Dynamics | How far apart the softest and the hardest blow are, in loudness and in tone: a narrow, even touch at 0, the widest at 1. Applies from the next strike |
| Practice felt | A felt strip between hammers and strings: a soft, muffled attack. Applies from the next strike |
| Felt mute | Felt laid on the sounding strings, held notes included. The mod wheel moves it |

## The body

| Control | Behavior |
| --- | --- |
| Lid | Closed at 0, the short stick at 0.5, open at 1 (an upright's top). A closed lid keeps the high frequencies from the microphones outside the piano |
| Soundboard | How long the soundboard rings: heavily damped at 0, lively at 1 |
| Sympathetic | How strongly the strings whose dampers are off answer the notes you play: held keys, everything under the sustain pedal, and the top keys, which have no dampers. It also sets how loud the strings whisper when the pedal lifts their dampers |
| Duplex | How strongly the short lengths of string beyond the bridge ring. The upright has none |
| Mechanics | How loud the action plays: the keys landing and coming back, the dampers falling and the sustain pedal's knocks. Silent at 0%; the default is 40%. Double-click to reset |
| Output | Master output level. At its default, typical playing reads about −9 VU on Reason's channel meter; the output stage keeps every sample under −1.5 dBFS and delays the sound by 2.5 ms, which the plug-in reports to the host |

## The microphones

Four pairs hear the piano, each with its own level. At the same level each
plays the piano as loud as the close pair, so the levels are a balance.

| Control | Behavior |
| --- | --- |
| Close | A spaced pair inside the piano over the strings by the hammers (behind an upright's soundboard): the direct, percussive pop sound |
| XY | A coincident pair at the open lid, about a metre off: a focused, natural image |
| Live | A spaced pair in the room beside a grand, or over the player's head at an upright: the piano with some of its room |
| Distant | A wide pair across the room: mostly room |
| Room | How much of the room's reverberation the pairs that hear it take; none at 0 |
| Width | The stereo image: the microphones' own at 0.75, mono at 0 |

Tuning, in the header of every view, sets concert A from 415 to 466 Hz.

## Pedals

| Control | Behavior |
| --- | --- |
| Sustain | Lifts the dampers continuously. The half pedal is the upper middle of the travel, about 64 to 89 on CC64: the strings ring on, shortened. A full pedal leaves the felt grazing the strings, so a chord let go under it falls 60 dB in about 10 s rather than ringing on for 20 |
| Sostenuto | Holds only the keys that are down when the pedal crosses halfway; later notes release normally |
| Soft | On a grand, una corda: the hammers shift off one string of each note and strike with softer felt. On the upright the hammers start closer to the strings and arrive slower |

Three brass pedal controls show the effective soft, sostenuto and sustain
positions, in the piano's left-to-right order. Hold a pedal to press it and
release to lift it; the continuous travel controls remain available for half
pedalling. The display also follows MIDI pedals and keyswitches. The on-screen
keyboard is playable. Pitch bend spans two semitones each way.

## Presets

The twelve factory presets set the piano, its controls, the microphones, Room,
Width and the practice felt; Output, Tuning, Mechanics, the felt mute and the
pedals keep their settings. Every preset plays at about the same level.

| Preset | What it is |
| --- | --- |
| Concert Grand | The concert grand as built, close pair, lid open |
| Studio Grand | The studio grand with harder hammers, close and XY, a drier room |
| Warm Walnut | The parlor grand with soft hammers on the short stick, three pairs |
| Felt Nocturne | The concert grand under the practice felt |
| Open Strings | The concert grand with the soundboard, sympathetic strings and duplex scales turned up, mostly from the room |
| Upright | The upright as kept at home: slightly aged strings, a little more detune |
| Felt Upright | The upright under the practice felt, top half open |
| Pop Upright | The upright with hard hammers, close and dry |
| Baby Grand | The baby grand, close and XY |
| Distant Hall | The concert grand from across the room |
| Old Parlor | The parlor grand with old strings and wide unisons |
| Bar Piano | The upright with old strings, hard hammers and unisons far apart |

## Pedal keyswitches

These three MIDI notes sit below the lowest playable piano key, A0 (MIDI 21).
They operate pedals without sounding a string:

| MIDI note | Name when middle C is C4 | Pedal |
| --- | --- | --- |
| 12 | C0 | Soft / left |
| 13 | C♯0 | Sostenuto / middle |
| 14 | D0 | Sustain / right |

Hold the keyswitch to press the pedal; note-off or zero-velocity note-on lifts
that keyswitch. They are momentary, not toggles. DAWs differ in octave naming,
so use MIDI note numbers when assigning them. Send a sostenuto keyswitch after
the notes to capture them; sending it first captures no later notes.

Keyswitches, hardware controller travel and saved panel travel are independent
sources combined by their maximum. Releasing a keyswitch therefore leaves a
hardware or panel pedal engaged. Each MIDI channel owns its switches. All Notes
Off releases held keys and switches while other pedal sources continue to
apply; resetting MIDI controllers does not synthesize a new sostenuto press.

## Pedals and modulation by MIDI

| MIDI controller | Meaning |
| --- | --- |
| CC1 | Smooth felt muting |
| CC64 | Sustain / damper pedal, continuous 0–127 |
| CC66 | Sostenuto, captured on the upward midpoint crossing |
| CC67 | Soft pedal, continuous 0–127 |
| CC120 | All Sound Off on that channel |
| CC121 | Reset channel controllers |
| CC123 | Release channel keys; active pedals still apply |

A physical controller and its corresponding panel control combine by maximum
travel. A panel pedal left raised can therefore keep the pedal active after a
hardware pedal is released. Return the panel control to zero when using only
the physical controller. Repeated sostenuto messages above its midpoint do
not capture new notes; release and press it again to capture a new set.

Sustain can catch a still-decaying released note. It cannot restore energy
already lost to damping. The top keys have no dampers (from F♯6 on the
concert grand, D♯6 on the upright); the felt mute damps them as well.

## Save and recall

The host's state stores the 24 saved parameters. Held notes and MIDI
controller positions are performance state. Malformed, incomplete or
unsupported state is rejected.

A session saved with Keyra 1.x opens, but does not sound as it did: that
version played pianos fitted from recordings, which 2.0.0 does not have. It
keeps its Output, Width, Tuning, Felt mute, Mechanics and pedals, its
Brightness becomes Hammer and its Resonance becomes Sympathetic, and it loads
the Concert Grand, or the Upright where its strings were mostly the Helsinki
upright's. In the host's generic parameter view Mechanics uses a raw 0–2
scale; the panel shows a tapered 0–100% knob.

## Scope of the sound model

The strings, hammers, soundboard and microphones are computed from a
description of each piano; none of it is fitted to a recording note by note,
and the five pianos are typical of their kinds, not one maker's instruments.
The keys', dampers' and pedals' noises are numbers fitted from recordings of
a grand and an upright and play beside the model: the pedal going down does
not set the strings whispering. The room is a small reverberator, not a
measured hall. The README's How it works and Known gaps say more.
