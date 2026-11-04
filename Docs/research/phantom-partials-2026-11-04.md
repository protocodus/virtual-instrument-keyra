# Phantom partials

4 November 2026, Keyra 0.4.18. A struck string's tension grows with the
square of its displacement, so besides its series it sounds lines at the sums
f(m) + f(n) of two of its partials' frequencies, a few hertz under the
series' own partial near them since the series is stretched, and at their
differences f(n) − f(m), as far over it (phantom partials: H. A. Conklin,
JASA 105(1), 536–545, 1999). Bank and Lehtonen's ABX study of fortissimo
grand and upright recordings heard the longitudinal components up to C5, and
only subtly from A3 (JASA 128(3), EL117–EL123, 2010). Moore, Neldner and
Rokni found the string's share of the lines much smaller than the rest of the
piano's (JASA 144(3), 1564, 2018): a line in a recording does not say where it
was made, and the engine's square stands for wherever that is.

The measurement is `Tools/fit_phantoms.py`; its protocol is at the head of
the tool and its receipt is
[`phantom-partials-2026-11-04.json`](phantom-partials-2026-11-04.json), which
`Source/DSP/MeasuredPhantoms.h` is generated from. No take is loaded or
distributed.

## The model

The engine adds gain x² to each channel, x the sum of a key's partials in
that channel, through the output's DC high-pass (first order, 10 Hz), so that
the square's constant, the partials' power, does not play. For partials of
amplitudes a(m) and a(n) that is a line of a(m) a(n) at f(m) + f(n) and at
f(n) − f(m), and of a(m)²/2 at 2 f(m). The prediction the fit regresses on is
the same square of the take itself, so a partial's own decay and beating
carry into its lines in both.

A first version played the sums alone, as the square of the partials'
analytic signal, since the takes seemed to show no line between a note's
partials. Fitted apart, each family's windows and the bins their floor is
read on kept 4.5 Hz clear of every line of the other, the takes show both: of
the 46 pitches where that version found its lines, the sums stand clear at
18 and the differences at 22, both at 8, where the differences read 0.78 to
10.6 times the sums' gain² (median 3.1). Part of what the first version read
as sums was difference lines in its windows or under its floor. The square
plays both families at one gain, fitted on both families' windows together.

## What the takes show

On every piano's train takes, the fit finds the lines at 38 of the 100
recorded pitches (it needs 30 windows clear of every lane to decide), and
fills 13 more between two that show them:

| Piano | Pitches | Show phantom partials | Filled between them | Gain |
| --- | --- | --- | --- | --- |
| Kakegawa grand | 22 | 11, F♯2 to A6 | 3 | 0.012 to 0.26 |
| Helsinki upright | 28 | 11, C2 to E5 | 4 | 0.033 to 0.081 |
| Hamamatsu grand | 27 | 9, F♯2 to C5 | 3 | 0.032 to 0.20 |
| Hamburg grand | 10 | 2, A2 and F♯4 | 1 | 0.074 to 0.15 |
| New York grand | 13 | 5, A♭2 to F6 | 2 | 0.016 to 0.054 |

The gains are in the recordings' units (1 at full scale). Beyond those
pitches the gain is 0:

- **In the bass** each partial has a sum line just under it and a difference
  line just over it from every pair of partials whose orders add or subtract
  to its own, and they crowd every gap the lanes leave: at the grand's C2,
  198 windows stay clear where the sums alone left 1205, and the null there
  stands clear of zero. Below the lowest pitch each piano shows (C2 on the
  upright, F♯2 on the Kakegawa and Hamamatsu grands, A♭2 on the New York and
  A2 on the Hamburg) the takes do not decide.
- **In the treble** the windows clear of every lane get few again. The fit
  decides only the grand's F♯6 and A6 and the New York's F6, on 87, 61 and 40
  windows. The grand's read 0.26 and 0.23, against 0.012 to 0.038 from F♯2 to
  A5, and at F♯6 the null reads half the line, though its spread holds zero:
  they are the least certain gains the fit finds. The grand's C6 fills to
  0.11 between A5 and F♯6, the most its own takes allow.

Three findings bear on what one gain per pitch can play:

- **The lines' gain depends on where they lie.** At the grand's F♯3, C4 and
  F♯4 the lines from 1.6 to 3.2 kHz read 8 to 10 dB over those from 3.2 to
  6.4 kHz and 6 to 8.5 dB over the pitch's pooled gain, while the null beside
  them reads 15 to 30 dB under them (at C5 the null reads nearly as much as
  the lines). A longitudinal resonance of the strings would lift the lines
  near it so (B. Bank and L. Sujbert, JASA 117(4), 2268–2278, 2005). One gain
  per pitch, pooled by the windows' inverse variance, plays the lines from
  1.6 to 3.2 kHz that much too soft and those from 3.2 to 6.4 kHz 1 to 3 dB
  too loud.
- **Soft strikes read higher.** On the grand, the takes at velocity 64 or
  under read 3.8 to 15 times the gain² of those at 96 or over (F♯2, F♯3, C4
  and C5, the medians of the takes); the pooled gain lies within 0.94 to 1.17
  times the loud takes' median at all four, as the loud takes' lines are the
  clearest. A part of the soft takes' lines may grow only as fast as the
  partials, as a longitudinal mode the hammer drives would, which a square
  cannot play. The engine plays the loud takes' gain, where the lines can be
  heard.
- **Some measured components sit on sum lines.** At the grand's C2 and F♯3
  some of the components the engine already plays beside the series (the
  extras) lie on sums of two partials and stand well over what the square
  makes there: at F♯3, 12 dB or more over the line it plays. They keep
  playing as measured, and the square adds its line under them.

## In the engine

A key's strikes share its strings, so all of a key's sounding strikes are
summed and squared together, each channel apart; a restrike carries on the
square of the strike it joins. A strike takes its key's gain from the strings
as built, between the recorded pitches around it as the fit fills a pitch,
over the scale that brings the recordings' levels to the output's; a build
changed while a key sounds keeps the gain its strike set until the key is
struck again. The square plays while its lines can reach the floor a partial
is dropped under (10⁻¹² in the output's units): for gain g and the key's
partials' power e, the lines' power in both channels is at most (g e)² where
no two of them fall together, and lines that do beat about the sum of theirs.
When it plays again it starts from silence.

The DC high-pass takes out the square's constant but not all of its
envelope: as a strike's partials rise, their power's rise passes through it
as a pulse under 120 Hz. In a C3 to E5 chord at velocity 127 that pulse peaks
at −48 dBFS on the Kakegawa grand and −41 dBFS on the upright and the
Hamamatsu grand, 7 to 16 ms after the strike, and over the first 250 ms its
RMS lies 42 to 50 dB under the chord's. Nothing in the takes measures it: the
fit's band starts at 200 Hz.

A rendered Hamamatsu E4 at velocity 110 differs from 0.4.17's render by what
the square of that render predicts, to 0.05 dB in power from 400 Hz to
8 kHz. Over 0.05 to 1.05 s after a strike, the lines lie 36 to 56 dB under
the note at velocity 100, and 48 to 77 dB under at velocity 40:

| Piano | Keys (velocity 40 / 100, dB under the note) |
| --- | --- |
| Kakegawa grand | F♯2 −57/−49, C3 −58/−52, C4 −60/−51, C5 −56/−47, F♯6 −48/−36 |
| Helsinki upright | C2 −63/−51, C3 −67/−56, C4 −63/−49, D4 −66/−50, C5 −71/−54 |
| Hamamatsu grand | F♯2 −67/−48, C3 −69/−45, C4 −77/−50, E4 −72/−40, C5 −75/−47 |
| Hamburg grand | A2 −57/−53, E3 −58/−51, B3 −57/−46, D4 −59/−46, F♯4 −59/−45 |
| New York grand | A♭2 −67/−53, C♯3 −62/−47, B3 −62/−43, A4 −57/−41, F6 −67/−45 |

The square doubles the partials' highest frequency, but at velocity 100 its
lines over 16 kHz lie 92 dB or more under the whole of them, so little lies
near the Nyquist frequency to fold back.

## Cost

Callgrind, the engine's `process()` rendering each factory demo, GCC 13.3.0
Release, 0.4.17 (commit 450187e) against 0.4.18:

| Demo | 0.4.17 | 0.4.18 | Change |
| --- | --- | --- | --- |
| 01 Kakegawa Grand | 10.60 G | 10.63 G | +0.3 % |
| 03 Warm Walnut | 7.20 G | 7.25 G | +0.7 % |
| 04 Felt Nocturne | 4.72 G | 4.78 G | +1.2 % |
| 05 Open Strings | 9.68 G | 9.78 G | +1.0 % |
| 06 Helsinki Upright | 9.81 G | 9.79 G | −0.2 % |
| 08 Pop Upright | 11.06 G | 10.78 G | −2.6 % |
| 09 Hamamatsu Grand | 4.09 G | 4.14 G | +1.2 % |
| 10 Three Cities | 7.28 G | 7.33 G | +0.8 % |

A key whose lines can reach the floor takes, at each sample, the sum of its
partials' lanes in each channel, its square and the high-pass. The render now
sums a key's strikes before squaring them, so a key held down, whose strikes
also drive its open strings, takes that drive once where it took it once for
each strike: Pop Upright's pumping chords, each key struck while its last
strike still sounds, save more there than their squares cost.

`RenderKeyraPresetDemos --cpu --repeats 3`, one thread, 48 kHz in 256-frame
blocks, DSP seconds per audio second; 0.4.17 and 0.4.18 run alternately,
twice each, the mean of the two medians. Development machine (Intel Xeon at
2.1 GHz, 4 hardware threads) while a four-worker training run held every
core: two runs of one build differ by up to 22 %, more than the two builds
do, so the instruction counts above measure the change. These are
development-machine figures, never Reason or DAW CPU.

| Demo | 0.4.17 | 0.4.18 |
| --- | --- | --- |
| 01 Kakegawa Grand | 0.0852x | 0.0835x |
| 03 Warm Walnut | 0.0594x | 0.0619x |
| 04 Felt Nocturne | 0.0436x | 0.0425x |
| 05 Open Strings | 0.0763x | 0.0761x |
| 06 Helsinki Upright | 0.0767x | 0.0797x |
| 08 Pop Upright | 0.0851x | 0.0851x |
| 09 Hamamatsu Grand | 0.0401x | 0.0400x |
| 10 Three Cities | 0.0630x | 0.0581x |

## Against the recordings

`Tools/benchmark_recordings.py` scored every train and dev take of the
locked split on all five pianos, 0.4.17 against 0.4.18:
[grand](../validation/grand-phantom-partials-benchmark-2026-11-04.md),
[upright](../validation/upright-phantom-partials-benchmark-2026-11-04.md),
[Hamamatsu](../validation/kawai-phantom-partials-benchmark-2026-11-04.md),
[Hamburg](../validation/hamburg-phantom-partials-benchmark-2026-11-04.md)
and [New York](../validation/newyork-phantom-partials-benchmark-2026-11-04.md).
No paired mean on the three other grands moves by 0.02. On the upright the
dev takes' decay error moves from 3.93 to 4.13 dB/s and their partial levels'
from 8.44 to 8.38 dB, and on the Hamamatsu grand the train takes' tuning error
from 0.50 to 0.54 cents and their decay error from 3.80 to 3.84 dB/s.

Four notes regress past the tolerances, each at its takes at velocity 95 or
over:

| Piano | Note | Role | Metric | 0.4.17 | 0.4.18 |
| --- | --- | --- | --- | --- | --- |
| Helsinki upright | B3 | dev | decay | 1.91 dB/s | 5.16 dB/s |
| Helsinki upright | D4 | train | decay | 3.25 dB/s | 4.70 dB/s |
| Helsinki upright | D3 | train | noise | 12.26 dB | 13.32 dB |
| Hamamatsu grand | A♭3 | train | tuning | 0.17 cents | 1.12 cents |

None of them changes a partial the engine played before: in those takes no
partial the scorer found in 0.4.17's render moves by 1 cent or its decay by
1 dB/s. The scorer looks for each recorded partial at the render's peak
nearest it, and 0.4.17's renders hold none at some of these pitches' upper
partials: the A♭3's 12, 13, 20 and 22, the B3's 24 and 29 to 31, the D4's 16,
21 to 26 and 28 to 30 and the D3's 35 and 44 to 50. The lines now give it a
peak there: at the A♭3, 8 to 11 cents from the recorded partial; at the B3
and the D4, one that stays at the recording's floor and so decays flat
against the recorded 18 to 51 dB/s; at the D3, peaks from 5.5 to 8.3 kHz
that the noise measure then leaves out as partials, which takes the render's
8 kHz band from 13.3 to 15.6 dB under the recording's at velocity 108.

## Levels

`Keyra.Levels` holds each preset's typical playing on Reason's meter within
0.05 dB of the reading the owner approved. 0.4.17 reads the Kakegawa Grand
at −9.057675 VU, Open Strings at −8.091657 and the Hamburg Grand at
−8.930175, 0.036 to 0.042 dB off their approved −9.016195, −8.133493 and
−8.893996. The lines move them by −0.009, +0.010 and −0.023 dB, to
−9.066835, −8.081521 and −8.953395, past that margin. No other preset moves
by more than 0.004 dB, no loudest chord rises over its approved ceiling, no
sample passes −1.5 dBFS, and each piano's default sound and tube move by
0.025 dB or less. The three readings wait for the owner's approval.
`Keyra.FactoryDynamics` fails on 0.4.17 with 1,048 steps between factory
levels under their floors and 6 chords over their maxima, and on 0.4.18 with
1,049 and the same 6: 13 steps fall under their floors and 12 rise over
them, each within 0.025 dB of it, and no step moves by more than 0.07 dB.

## Known gaps

- **One gain per pitch.** Every line of a pitch plays at one gain, sums and
  differences alike, where the takes show the lines from 1.6 to 3.2 kHz 6 to
  8.5 dB over it at the grand's F♯3, C4 and F♯4, and the differences 0.78 to
  10.6 times the sums' gain² where both stand clear. A longitudinal resonance
  for each string would place that lift; none is modelled.
- **No bass, an uncertain treble.** The bass plays no lines, where the takes
  do not decide, and the grand's F♯6 and A6 rest on 87 and 61 windows.
- **Lines beside partials are counted twice.** A line within a few hertz of a
  measured partial or extra adds to what the modal fit already put there from
  the same takes.
- **Soft strikes** play the loud takes' gain, under what their takes read.
- **The envelope's pulse** under 120 Hz plays, unmeasured.
- **Lines between keys.** Each key is squared alone, so the lines between two
  keys' partials, which a nonlinearity in the piano's structure would make,
  are not played.
