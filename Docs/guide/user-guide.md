# Keyra development candidate

Keyra generates an 88-key piano, a grand or an upright, using a real-time
reduced modal engine and numerical measurements of acoustic recordings. The preserved nonlinear
research renderer remains available separately. This candidate is for
development and evaluation; host acceptance and commercial release are pending.

## Playing and controls

Send MIDI notes A0–C8 (21–108). MIDI velocity changes spectral balance and
excitation level continuously, along one curve on both pianos: halfway
between a straight line and an S-curve in level, from the grand's softest
recorded strike at velocity 1 to each piano's loudest at 127. Each strike
lands a little harder or softer than its velocity, as a player's do. MIDI
note-on with velocity zero releases a key.
Each MIDI channel owns its key and controller state.

| Control | Behavior |
| --- | --- |
| Piano | The grand or the upright. A switch plays from the next note: what sounds rings on, and held keys and pedals keep their state |
| Quality | How much of each note plays, for CPU on slower machines. Full, the default, plays all of it; Balanced and Light leave out the partials 60 and 50 dB under the note's strongest, which changes no third of an octave of its spectrum by more than 0.04 and 0.74 dB. A change applies from the next note |
| Output | Master output level, smoothed during playback. At its default, typical playing reads about −9 VU on Reason's channel meter; the output stage keeps every sample under −1.5 dBFS and delays the sound by 2 ms, which the plug-in reports to the host |
| Hammer / Brightness | Changes partial balance; the neutral setting is 50% |
| Resonance | Amount of the reduced sympathetic response |
| Width | Stereo spread, from centered to wide |
| Tuning | Concert A frequency; the DAW interface shows hertz |
| Felt mute | Adds damping to sounding modes, including physically held notes |
| Sustain | Continuous damper lifting; intermediate positions produce half-pedal damping |
| Sostenuto | Captures only keys held when the pedal crosses 50% upward; later notes release normally |
| Soft | Changes the level, high-partial excitation and unison balance of subsequent strikes |

The factory presets choose the piano and set Hammer, Resonance, Width and
Felt mute; Output, Tuning, Quality and the pedals keep their settings. Five
play the grand and three the upright. The DAW interface's on-screen keyboard
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

DAW state stores the ten panel parameters. Transient held notes and MIDI
controller positions are performance state. Malformed, incomplete or unsupported
state is rejected; a session saved before the Piano control existed opens with
the grand it was made with. Piano is not offered for automation. The Rack Extension uses Reason patches for its panel state
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
soft pedal works as the grand's does rather than moving the hammers closer to
the strings, as an upright's does.
