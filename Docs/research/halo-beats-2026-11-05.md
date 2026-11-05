# The undamped strings' beat

5 November 2026, Keyra 0.4.21. The strings from F6 up have no dampers, so
every strike sets them ringing through the bridge, and the engine played each
as one tone at its pitch: a prompt part the bridge drains within a few tenths
of a second, then its aftersound. A unison's strings, a little mistuned and
coupled through the bridge, ring as two components a few tenths of a hertz to
a few hertz apart, which beat (G. Weinreich, "Coupled piano strings", JASA 62,
1977), and so do the undamped strings the bridge sets ringing. Where a
piano's takes decide a string's beat, 0.4.21 plays its aftersound as two
components.

The measurement is `Tools/fit_halo_beats.py`; its protocol is at the head of
the tool and its receipt is
[`halo-beats-2026-11-05.json`](halo-beats-2026-11-05.json), which
`Source/DSP/MeasuredHaloBeats.h` is generated from. It reads the train takes
of each piano's locked split; the dev takes score each decided beat and are
never fitted. No take is loaded or distributed.

## The model

A strike that sets string j ringing at amplitude a, with the fixed phase φ its
key gives that string, starts its aftersound as

a g e^(iφ) e^(−r s t) e^(2πi f t) (1 + ρ e^(2πi Δf t))

at the string's pitch f and its rate r. Where the string does not beat, ρ is
0, the scale s is 1 and the level g is 1, and the string rings as in 0.4.20.
Where it beats, the second component stands Δf above the first at
ρ = 10^(L/20) e^(iθ) against it: L its level and θ its phase at contact. The
prompt part is unchanged.

The halo fit read each string's rate and level as one tone: its rate from
the fall between half-second windows at 1 and 2 s after contact, its level
from those windows brought back to contact. Read so, a beat changes the fall,
so the rate the fit gave a beating string holds the beat's share. s and g are
therefore no new fit: they are the scale and the level at which the two
components, read through the same windows, fall as the fit fitted the string
and stand at the level it fitted.

## What the takes show

Each train take of a pitch from F♯3 up, at every undamped string but the
struck key's own, where no partial of the struck key lies within 10 Hz of it
and the string's tone at 1 s stands 20 dB over its surroundings: the take
demodulated at the string's pitch as the engine plays it, both channels,
low-passed at 4 Hz, read 100 times a second from 0.3 to 3 s after contact. Its
two components by ESPRIT, the poles both channels share: the second's offset
above the first, its level against the first and its phase at contact. A
string's beat is the median offset and level over its envelopes and the
circular mean of their phases.

The takes decide a string's beat where it carries over between the struck
pitches: each train pitch's envelopes are scored at the beat the string's
other train pitches give, as the energy two components at that beat leave
unexplained against one, with the same freedom (each channel's amplitude, the
rate and the offset fitted), and so many pitches score better with it that
tossed coins would show as many in 5 % of draws or fewer (the one-sided sign
test).

| Piano | Train envelopes (strings) | Dev envelopes | Strings that beat |
| --- | --- | --- | --- |
| Kakegawa grand | 566 (18) | 413 | F♯6, A♯6, C♯7 |
| Helsinki upright | 141 (12) | 18 | C7 |
| Hamamatsu grand | 35 (11) | 5 | none |
| Hamburg grand | none | none | none |
| New York grand | 32 (9) | 22 | none |

| String | Pitches better | Sign test | Offset | Second against first | Phase concentration | Dev envelopes: energy left, better |
| --- | --- | --- | --- | --- | --- | --- |
| Kakegawa F♯6 | 10 of 10 | 0.001 | 0.889 Hz | −5.2 dB | 0.81 | 47: 0.73, 98 % |
| Kakegawa A♯6 | 9 of 11 | 0.033 | 1.616 Hz | −10.9 dB | 0.71 | 44: 0.84, 98 % |
| Kakegawa C♯7 | 8 of 9 | 0.020 | 0.834 Hz | −1.1 dB | 0.84 | 48: 0.53, 88 % |
| Helsinki C7 | 8 of 8 | 0.004 | 0.992 Hz | −5.2 dB | 0.76 | 3: 0.78, 100 % |

"Energy left" is the geometric mean, over the dev envelopes, of the energy
the beat leaves unexplained against one component's; "better" the share of
them it explains better. Every other string's envelopes resolve two
components too, a median 0.3 to 7.4 Hz apart, but the beat of a string's
other pitches explains a pitch's envelopes no better than one component
does. Nearest to deciding are the Kakegawa grand's B7 (4 of 4 pitches,
0.063), the upright's F6 (7 of 9, 0.090) and F♯6 (3 of 3, 0.125), the
Hamamatsu's F7 (2 of 2, 0.25) and the New York grand's E7 (2 of 3, 0.5).

No string on any of the Hamburg grand's train takes stands 20 dB over its
surroundings at 1 s: at most 19.3 dB, a median 7.8 dB. Its strings keep one
component.

## The decay under the beat

Each train envelope's own two components, read through the halo fit's
windows at the string's fitted rate, fall faster than one component would:

| String | Each envelope's beat reads the fall faster by (quartiles) | The median beat | Rate scale s | First's level g |
| --- | --- | --- | --- | --- |
| Kakegawa F♯6 | 0.38, 1.82, 4.14 dB | 1.90 dB | 0.843 | −3.14 dB |
| Kakegawa A♯6 | 0.45, 1.52, 1.84 dB | 1.24 dB | 0.884 | −1.95 dB |
| Kakegawa C♯7 | 0.66, 1.63, 4.44 dB | 2.46 dB | 0.825 | −4.20 dB |
| Helsinki C7 | −0.61, 0.06, 0.52 dB | −0.20 dB | 1.008 | +0.12 dB |

So the grand's three strings fall 12 to 18 % slower under the beat than the
halo fit's rate, which read the beat's dip from 1 to 2 s as decay, and their
first components stand 2 to 4 dB under the level it fitted, which the second
adds back to the windows' reading. The upright's beat reads about as one tone
does.

## In the engine

Each undamped string has a third resonator beside its aftersound and its
prompt part: the second component, at the string's pitch plus its offset,
falling at the string's rate. A strike adds to it the strike's amplitude at
ρ against the first, in the same phase the key gives the string, so the beat
starts at contact. Only the strings whose second components ring are turned
each sample: those that beat on the built piano, and any still ringing from
an earlier build.

Between the pianos the first component's level mixes in dB by the strings'
build, the rate in the log domain, and the second's power in power, so a
piano whose string does not beat fades it; its offset mixes in the log domain
and its phase along the shorter arc among the pianos whose strings beat. The
unisons modifier spreads the offset as it spreads a strike's: none at −1,
three times as far at 1. Ring scales both components' rate, the felt mute
damps both, and a build whose strings stop beating lets a ringing second
component ring out at the string's own pitch and the new build's rate. Reset
silences it.

`Keyra.HaloBeat` checks that a strike on each piano sets every undamped
string's first component at its level against the prompt part, and each
beating string's second at its level, phase and offset (to 1e-12, and 1 mHz
for the offset the sine table turns), with both at the string's rate times
its scale; that a string whose takes decide no beat rings as one component;
that between the Kakegawa and Hamamatsu grands the second fades in power by
the strings' build at the grand's offset and phase; that the unisons modifier
spreads the offset; that a build whose strings stop beating lets the second
ring out; that reset silences it; and that the host's blocks do not change
it. `Keyra.MeasuredHaloBeats` checks that the header is the one its receipt
gives and the receipt the current fit's.

## Against the recordings

`Tools/benchmark_recordings.py`, every train and dev note of each piano's
locked split, 0.4.20 against 0.4.21
([Kakegawa grand](../validation/grand-halo-beat-benchmark-2026-11-05.md),
[upright](../validation/upright-halo-beat-benchmark-2026-11-05.md)): no note
regresses past a tolerance on either piano, and no paired mean moves by as
much as 0.01 dB (the most, the grand's sustain spectrum: dev 5.420 to
5.430 dB, train 4.651 to 4.658). The Hamamatsu, Hamburg and New York grands'
reports equal 0.4.20's case for case (127, 48 and 78 cases).

`Tools/compare_ring_levels.py` measures the undamped strings a held note sets
ringing as the halo fit measures them, against the recordings: their prompt
parts at 0.125 to 0.5 s and their tones at 1, 2 and 3 s, on the grand's train
notes at layers 5, 9, 13 and 16 and the upright's at every layer, and on
both pianos' dev notes. Every string that does not beat scores as on 0.4.20.
The four that beat, mean |dB| where the recording rings clear, 0.4.20 →
0.4.21 (blank: fewer than three strikes ring the string clear there):

| String, role | 0.125 s | 0.25 s | 0.375 s | 0.5 s | 1 s | 2 s | 3 s |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Kakegawa F♯6, train |  |  |  | 5.8 → 2.4 | 2.6 → 3.5 | 1.9 → 2.9 | 2.1 → 1.9 |
| Kakegawa A♯6, train | 2.0 → 2.6 | 2.6 → 4.7 | 4.9 → 6.0 | 6.3 → 5.7 | 2.1 → 2.1 | 1.7 → 1.5 | 3.2 → 2.7 |
| Kakegawa C♯7, train | 1.0 → 1.3 | 3.2 → 2.9 | 2.9 → 7.8 | 5.5 → 8.5 | 1.9 → 2.7 | 3.0 → 4.2 | 1.8 → 2.8 |
| Kakegawa F♯6, dev |  |  |  | 6.1 → 3.0 | 2.8 → 3.7 | 3.0 → 3.9 | 2.1 → 2.0 |
| Kakegawa A♯6, dev | 2.1 → 2.3 | 2.0 → 4.0 | 4.6 → 5.8 | 5.7 → 5.0 | 2.2 → 2.2 | 2.4 → 2.2 | 2.3 → 3.3 |
| Kakegawa C♯7, dev | 1.6 → 1.7 | 3.3 → 1.9 | 4.3 → 6.6 | 7.6 → 6.4 | 2.3 → 3.8 | 2.7 → 4.4 | 3.2 → 3.1 |
| Helsinki C7, train | 5.7 → 6.5 | 5.9 → 8.3 | 9.6 → 10.3 | 11.2 → 10.1 | 11.7 → 11.7 |  |  |
| Helsinki C7, dev |  | 6.3 → 8.1 | 5.0 → 5.9 | 8.3 → 7.2 | 16.3 → 16.1 |  |  |

The beat brings F♯6 at half a second from 6.2 dB over the recordings to
0.2 dB under (median, train), where its median beat dips as the recordings'
strings do. But at 1 and 2 s, the windows the halo fit reads, F♯6 and C♯7
sit 0.8 to 1.7 dB further from the recordings on average than one tone did,
and C♯7's dip reads 8.6 and 8.4 dB under them at 0.375 and 0.5 s (median,
train), where one tone read 0.2 and 5.0 dB over. The engine plays each
string's median beat whichever key strikes it, so its peaks and dips fall at
the same times after every strike, while each recording's fall at its own:
the offset and phase vary with the struck key (phase concentration 0.71 to
0.84), and so do the peaks' times, more with every second. Measured at fixed
times, one tone sits between a recording's peaks and dips and scores better
than a beat that peaks where the recording dips. The fit scores each
envelope whole, by the energy left unexplained, which the loud first second
weighs most; scored so, the beat explains 88 to 98 % of the dev envelopes
better than one tone.

Over all the strings, on the grand's never-fitted notes the strings that ring
clear sit a median 0.9 dB over the recordings at 1 s and 1.1 dB under at 3 s
(0.4.20: 0.6 over and 1.6 under), 3.7 and 5.1 dB from them on average (3.6
and 4.9), and 10.8 % of them 10 dB or more under at 3 s (10.4 %). On its
train notes they sit 2.5, 2.6 and 3.9 dB from the recordings on average at
1, 2 and 3 s (2.3, 2.4 and 3.9). Of the grand's dev strings that ring clear
at 0.375 and 0.5 s, 3.8 and 3.7 % play 10 dB or more over the recordings (6.0
and 6.6 %). On the upright every pooled reading from 0.5 s on moves by
0.1 dB at most.

The renderers are the two builds' `keyra_render` (sha256 of 0.4.21's:
72df738c…), at sympathetic resonance 0:

    python3 Tools/compare_ring_levels.py --renderer v0420=<0.4.20> --renderer v0421=<0.4.21> --out <dir>/rings-grand.json
    python3 Tools/compare_ring_levels.py --model upright --renderer v0420=<0.4.20> --renderer v0421=<0.4.21> --out <dir>/rings-upright.json

## Against the playing

A C major chord let go after 0.3 s, a D5 after a quarter of a second and a
low four-note chord after 0.3 s, each left to ring, rendered by 0.4.20 and
0.4.21 at Mechanics 0. Over the 0.5 to 2.5 s after each key-up, the
difference, the beat alone, sits under what still sounds by

| Piano | After the C major chord | After the D5 | After the low chord |
| --- | --- | --- | --- |
| Kakegawa grand | 15 to 18 dB | 7 to 10 dB | 32 to 36 dB |
| Helsinki upright | 42 to 58 dB | 37 to 45 dB | 44 to 54 dB |

## Cost

Callgrind, the whole program rendering each factory demo, GCC 13.3.0
Release, 0.4.20 (commit b78fd06) against 0.4.21:

| Demo | 0.4.20 | 0.4.21 | Change |
| --- | --- | --- | --- |
| 01 Kakegawa Grand | 11.653 G | 11.704 G | +0.43 % |
| 03 Warm Walnut | 8.219 G | 8.269 G | +0.61 % |
| 04 Felt Nocturne | 5.752 G | 5.799 G | +0.83 % |
| 05 Open Strings | 10.746 G | 10.798 G | +0.48 % |
| 06 Helsinki Upright | 10.725 G | 10.715 G | −0.10 % |
| 08 Pop Upright | 12.039 G | 12.029 G | −0.08 % |
| 09 Hamamatsu Grand | 5.045 G | 5.007 G | −0.75 % |
| 10 Three Cities | 8.384 G | 8.461 G | +0.92 % |

The Hamamatsu Grand demo, whose strings beat nowhere, renders byte for byte
as on 0.4.20. A first version that tested every string's second component
each sample cost the Kakegawa Grand demo 1.23 %; turning only the strings
that beat brought it to 0.43 %.

`Keyra.CpuBudget` passes. In wall-clock time, the two builds' demo
renderers run alternately twice each (each run the median of three renders),
0.4.21 moves −9.0 to +9.7 % per demo against 0.4.20 (the Kakegawa Grand
demo −9.0 %, Three Cities +9.7 %), inside the up to 13 % that either build's
own runs spread over on this machine; the instruction counts above are the
measure. The machine this session ran on renders the demos about half again
as slowly as the one earlier rounds measured: the Kakegawa Grand demo at 0.12
to 0.14x realtime on both builds, where 0.4.19 measured 0.088x.

## Listening

`/mnt/project-files/keyra/ab-2026-11-05-string-beat/` holds A (0.4.18) and
B (0.4.21) on the Kakegawa grand at Mechanics 0, the phrase above,
level-matched on whole-file RMS (the trim 0.0000 dB), with its key. On the
grand at Mechanics 0, 0.4.20 renders the phrase byte for byte as 0.4.18. The
owner's verdict goes in `Docs/decisions.md`.

## Known gaps

- Seventeen of the Kakegawa grand's twenty undamped strings, nineteen of the
  upright's and all of the other pianos' ring as one component: their takes
  do not decide a beat that carries over between pitches, and the Hamburg
  grand's hold none 20 dB clear at 1 s.
- One beat per string, whichever key strikes it: the median offset and level
  and the mean phase. The takes' phases scatter (concentration 0.71 to 0.84),
  and on the dev takes the median beat leaves 0.53 to 0.84 of the energy one
  component leaves unexplained, not none.
- Both components fall at one rate. In Weinreich's model the two modes of a
  coupled unison decay at their own rates, which the envelopes from 0.3 to
  3 s, and the halo fit's fall from 1 to 2 s, do not part from the beat.
- Measured at fixed times, the beating strings sit further from the
  recordings than one tone did: at 1 and 2 s F♯6 and C♯7 by 0.8 to 1.7 dB on
  average, and C♯7 a median 6 to 9 dB under them at 0.375 and 0.5 s, where
  its median beat dips. The engine's beat peaks and dips at the same times
  after every strike, each recording's at its own.
- The prompt part keeps one component.
