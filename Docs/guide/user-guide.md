# Keyra development candidate

Keyra generates an 88-key piano from three measured pianos, the Kakegawa and
Hamamatsu grands and the Helsinki upright, mixed part by part, using a
real-time reduced modal engine and numerical measurements of acoustic
recordings. The preserved nonlinear
research renderer remains available separately. This candidate is for
development and evaluation; host acceptance and commercial release are pending.

## Playing and controls

Send MIDI notes A0–C8 (21–108). MIDI velocity changes spectral balance and
excitation level continuously, along one curve on every piano: halfway
between a straight line and an S-curve in level, from the grand's softest
recorded strike at velocity 1 to each piano's loudest at 127. Each strike
lands a little harder or softer than its velocity, as a player's do. MIDI
note-on with velocity zero releases a key.
Each MIDI channel owns its key and controller state.

| Control | Behavior |
| --- | --- |
| Strings, Hammers, Soundboard, Action | In the Build view: a row per part, with a weight from 0 to 100% for each measured piano (Kakegawa, Helsinki, Hamamatsu). The part mixes the pianos at their shares of its row, so 100% Kakegawa and 50% Helsinki plays two thirds of the one and a third of the other, and a row of zeros plays the Kakegawa grand's. Strings set the tuning stretch, stiffness, unisons and how the partials ring; Hammers how hard each partial is struck, how fast it rises and how the tone follows velocity; Soundboard the body's modes, the strike's knock and the board's noise; Action the knocks of keys, dampers and pedals and how the soft pedal works. A change applies from the next note: what sounds rings on, and held keys and pedals keep their state; the soundboard's modes move at once |
| Stiffness, Unisons, Ring | In the Build view: the strings' inharmonicity from ×0.25 to ×4, how far each note's unison strings sit apart from ×0 (one pitch) to ×3, and how long the strings ring from ×0.5 to ×2, each ×1.00 as built. A change applies from the next note |
| Quality | How much of each note plays, for CPU on slower machines. Full, the default, plays all of it; Balanced and Light leave out the partials 60 and 50 dB under the note's strongest, which changes no third of an octave of its spectrum by more than 0.04 and 0.74 dB. A change applies from the next note |
| Output | Master output level, smoothed during playback. At its default, typical playing reads about −9 VU on Reason's channel meter; the output stage keeps every sample under −1.5 dBFS and delays the sound by 2 ms, which the plug-in reports to the host |
| Brightness | Changes partial balance; the neutral setting is 50% |
| Resonance | Amount of the reduced sympathetic response |
| Width | Stereo spread, from centered to wide |
| Tube Mic | Where the piano is heard from: at 0% the stereo pair the piano was recorded with, close over the strings (Kakegawa grand), at the player's position by the hammers (Helsinki upright) or at the player's position (Hamamatsu grand); at 100% a vintage tube microphone at shin height, mono, with more deep bass and top and less low midrange, measured on the upright's recordings. Between, the two are mixed and the image narrows. Typical playing reads the same on the meter at 0% and 100%, and about half a decibel less mixed halfway |
| Mechanics | How loud the action plays: the keys landing and coming back, the dampers falling, the sustain pedal's knocks and the strings it sets ringing going down. From silent at 0% to twice as loud at 200%; 100% is as calibrated |
| Tuning | Concert A frequency; the DAW interface shows hertz |
| Felt mute | Adds damping to sounding modes, including physically held notes |
| Sustain | Continuous damper lifting; intermediate positions produce half-pedal damping. Full pedal lifts the dampers 80% of the way clear, so the felt still grazes the strings: a chord let go under it falls 60 dB in about 9 s on the Kakegawa grand and 11 s on the Helsinki upright |
| Sostenuto | Captures only keys held when the pedal crosses 50% upward; later notes release normally |
| Soft | Changes the level, high-partial excitation and unison balance of subsequent strikes |

The ten factory presets set the build, Brightness, Resonance, Width and
Felt mute; Output, Tuning, Quality, Tube Mic, Mechanics and the pedals keep
their settings. Five play the Kakegawa grand and three the Helsinki upright,
Hamamatsu Grand plays the Hamamatsu grand, and Three Cities plays every part
at equal thirds of the three. The DAW interface's on-screen keyboard
is playable. Three brass pedal controls
show the effective soft, sostenuto and sustain positions, in the physical
piano's left-to-right order. Hold a pedal to press it and release to lift it;
the continuous travel controls remain available for half pedalling. The
display also follows MIDI pedals and keyswitches. The Rack Extension has
host pitch and modulation wheels; pitch bend spans two semitones each way.
Reason's master tuning is included by the adapter.

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

## Pedals and modulation

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
already lost to damping. The highest twenty keys have no ordinary key damper;
the felt mute can damp them as well.

## Save and recall

DAW state stores the 27 saved parameters. Transient held notes and MIDI
controller positions are performance state. Malformed, incomplete or unsupported
state is rejected; a session saved before the build existed opens with the
grand it was made with, and one saved with the Piano control as the build it
chose. The build and Quality are not offered for automation. The Rack Extension uses Reason patches for its panel state
and native host performance properties for pitch, mod and sustain.

## Scope of the sound model

The live core plays each partial as four measured decay lanes, with the
beating and left/right balance of its unison strings, over a bank of measured
soundboard and case modes and the board's band noise, which every strike
excites; the open-string bank adds a reduced sympathetic response. The strings
from F6 up have no dampers: every strike sets them ringing, whatever the
Resonance control, and they ring on after the key is let go. The felt
mute damps the strings, not the board's ring, which dies within a second. The
core does not reproduce the reference solver's nonlinear hammer contact or
full reciprocal soundboard network. Detailed key/damper noises and
recording-room acoustics are not calibrated.
The current isolated-note library cannot establish pedal realism because the
recording pedal positions and timings are undocumented.

The upright is measured the same way from another library's recordings, which
hold no pedal recordings: its sustain pedal makes no sound of its own, and its
soft pedal brings the hammers closer to the strings, as an upright's does
(half-blow), by a derivation no recording measures. The Hamamatsu grand is
measured from a third library's recordings, which hold no pedal recordings
either: its sustain pedal makes no sound of its own, its strings ring under
it at the Kakegawa grand's rates, and its soft pedal shifts the hammers, as a
grand's does.
