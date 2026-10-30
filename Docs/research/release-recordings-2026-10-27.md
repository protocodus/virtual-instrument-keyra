# What the Salamander release recordings can and cannot set

27 October 2026. Train-role files only (A, C and F# pitches, `rel` keys off
D#, `pedalD1`, `pedalU1`), read with the scratch scripts summarised here; no
model was fitted to them.

## The string-resonance releases (`harmL*`, `harmS*`)

These are the tails Salamander's SFZ plays after a key-up ("string resonance
releases", `Data/str_res.txt`). Every file starts with a fade-in: a linear
gain ramp times one exponential decay fits the first 0.4 s of each to 1.2–3.8 dB
RMS, with ramps of 23–188 ms (median 95 ms loud, 58 ms soft). After the ramp
the tails fall at 45–80 dB/s in every band from 70 Hz to 4.5 kHz (loud layer
medians 55–79 dB/s, soft 44–60), slower in the extreme registers (F#5 and A5
16–31 dB/s, as the undamped strings above F6 keep ringing), and slow to
10–50 dB/s after 0.3 s.

A rate that does not depend on frequency is the room's, not the felt's, so
these files show the recording room's reverberant tail and the strings the
dampers leave ringing. Its level relative to the note before the key-up is not
in the files: the fade-in hides the first tenth of a second, where a damper
does most of its work, and the files carry no common reference to the note
recordings (their noise floor sits 10 dB below the notes').

## The damper itself

Taguti, Ohtsuki, Yamasaki, Kuwano and Namba, "Quality of piano tones under
different tone stoppings", *Acoust. Sci. & Tech.* 23(5), 244–251 (2002),
Table 6, measured the termination of C4–C5 on a Yamaha C7 in a 61 m³ room
(0.3 s at 500 Hz): 220–470 dB/s over the first 35 dB after a quick key release,
130–200 dB/s over the first 20 dB after the slowest smooth release.

Keyra's damper (`partial.damperScale` in `Source/DSP/KeyraEngine.cpp`) takes a
released C4 down at about 500 dB/s and A2 at about 330 dB/s once the felt has
landed, so it sits at the fast end of that range. The engine was left as it is:
the release recordings above cannot correct it, and the measured range does
not single out a better value.

## Key-release and pedal noise

The 88 `rel` files ("hammer noise releases", one layer) are low-frequency
thumps: at C4 the energy is in the body modes near 96, 170 and 228 Hz, peaking
100–250 ms into the file and falling about 100 dB/s. Their spectra and their
variation across the keyboard are measurable. Their level relative to the notes
is not: the files peak within 5 dB of full scale, so they were gained up as a
set, and the only level the distribution gives is the SFZ's playback trim
(`volume=-37`, `Data/hammer.txt`; pedal noises `-20` and `-19`,
`Data/pedal.txt`), a mixing choice rather than a measurement.

## What the engine takes from them (28 October)

The engine now synthesizes the knocks these files record on its own body
modes, from their spectra, not their level; no waveform is played.
`Tools/fit_realtime_modal.py` fits each recorded pitch's own `rel` take and
`pedalD1`/`pedalU1` as knocks on the 91 body modes every strike rings, the
modes' frequencies, rates and pickups fixed: per mode a complex level at the
knock's onset (where its power over 5 ms first comes within 30 dB of its
peak), 25 Hz to 1 kHz, under one rise 1 − e^(−t/τ) that every knock shares.
τ = 54.5 ms leaves the least energy unexplained across them (5–300 ms
searched); a strike's knock rises in a fraction of a millisecond. The modes
leave 26–67 % of a knock's energy unexplained (median 38 %), most at A0's
release and the pedal's, whose energy spreads beyond the modes; the 1–3 kHz
part, 20 dB under the rest, is left out. A decay shared by every knock on top
of the modes' own improved the mean only from 42 % to 40 % (a 200 ms decay
under a 120 ms rise), so the knocks ring with the modes' own decays.
(Superseded on 2026-10-30: the knocks now fall 1.5 times as fast as the modes
ring, which their bands' decays show; see `Docs/decisions.md`.)

The engine sets them against the notes as the SFZ does: a release at −37 dB
with 82 % velocity tracking where the notes track 73 % (the notes play at the
recordings' own levels, so a release takes the ratio of the two), 2 dB
quieter for each second since its strike (`rt_decay`); the pedal at −20 dB
going down and −19 dB coming up, sounding within 0.08 of either end of its
travel. With the modes leaving part of each knock out, a C4 at velocity 70
let go after 0.18 s knocks 39 dB under its note's peak, where the SFZ's
balance puts it 34 dB under (strongest 300 ms in 25 Hz–1 kHz: 40 against
36 dB). A key-up knocks only where a damper falls: not under the sustain
pedal or a sostenuto capture, while from F6 up, where there is no damper,
the key's own return knocks whatever the pedals do, as its recording is that
sound alone.

## What would settle it

One continuous capture per note of a strike, a hold and a key-up, with the
microphones and gain of the note recordings, would give the damper rate, the
room tail's level and the release noise's level together.
