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

## What would settle it

One continuous capture per note of a strike, a hold and a key-up, with the
microphones and gain of the note recordings, would give the damper rate, the
room tail's level and the release noise's level together.
