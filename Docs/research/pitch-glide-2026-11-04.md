# Pitch glide

4 November 2026, Keyra 0.4.19. A string's mean tension rises with the square
of its slope, so a struck string plays sharp and settles as it decays
(tension modulation: T. Tolonen, V. Välimäki and M. Karjalainen, IEEE Trans.
Speech Audio Process. 8(3), 300–310, 2000). For partials of displacement
a(n) the tension grows by EA π² / (8 L²) Σ n² a(n)², and every frequency by
half that share of the tension; a partial's energy is μ L π² f1² n² a(n)², so
the glide is in proportion to the string's whole energy.

The measurement is `Tools/fit_glide.py`; its protocol is at the head of the
tool and its receipt is
[`pitch-glide-2026-11-04.json`](pitch-glide-2026-11-04.json), which
`Source/DSP/MeasuredGlide.h` is generated from. No take is loaded or
distributed.

## The model

A key plays sharp by

cents(t) = K 2^(s (key − 60) / 12) P(t),

P its partials' power, both channels' squared amplitudes summed over every
lane, in the recordings' units (1 at full scale), the key held between the
lowest and the highest pitch measured. The output's power falls with the
string's energy at each partial's own rate, so P stands for that energy as
far as the board radiates the partials alike. K and s are each piano's.

## What the takes show

Each train take's glide is the frequency of its first ten partials from
their phase's slope, both channels summed, over 0.05 to 0.35 s against over
0.6 to 1.1 s after the onset, the median over the partials; its drop is P's
mean over the first window less its mean over the second, from the table
(`MeasuredModalData.h`) at the take's layer. A piano's takes give glide =
a(pitch) + K 2^(s (key − 60) / 12) drop: the offset per pitch takes what does
not grow with the strike, as the unison's beating moves a partial's phase at
every layer. Each take weighs by its median's spread over 2000 draws of its
partials, the takes' scatter beyond that is fitted, and s is profiled from
−3 to 1 per octave. A piano shows a glide where the lowest 0.1 % of K refitted
on the draws stays above zero and the law lowers χ² by more than the highest
0.1 % of 2000 shuffles of the drops among each pitch's takes do.

| Piano | Takes (pitches) | K at C4, cents per unit power (0.1 % to 99.9 %) | Per octave up | χ² gain | Shuffles' 99.9 % | Glide |
| --- | --- | --- | --- | --- | --- | --- |
| Kakegawa grand | 228 of 264 (19) | 1.27 (−0.77 to 2.78) | ×0.93 | 6.7 | 3.6 | none |
| Helsinki upright | 114 of 137 (23) | 7.96 (0.70 to 18.96) | ×0.42 | 25.7 | 15.1 | **yes** |
| Hamamatsu grand | 89 of 104 (23) | 15.4 (−5.6 to 31.1) | ×0.79 | 6.4 | 8.7 | none |
| Hamburg grand | 40 of 40 (10) | 9.8 (−35.7 to 50.2) | ×0.84 | 0.7 | 1.9 | none |
| New York grand | 44 of 61 (9) | 4.72 (−0.08 to 9.43) | ×1.19 | 22.2 | 12.0 | none |

A take is left out where its recording ends before the late window or fewer
than five of its first ten partials are measured there. Only the upright
clears both tests. The New York grand clears the shuffles but its K's lowest
0.1 % falls just under zero; the Hamamatsu and Hamburg grands clear neither.
The upright's K grows 2.4 times per octave down: at its loudest layer
(velocity 122, which the plug-in's velocity 127 plays) the law gives 3.6 cents of glide from the early window to the
late at C1, 1.0 at F♯2, 1.7 at A2 and 0.8 at C4, and at most 0.43 cents from
F♯4 up.

**The drop is the table's power.** In the bass, measured at the partials'
frequencies, the takes hold a half to a third of the table's power (upright
C1, New York C1 and A♯1), where a partial's lanes beat against each other.
The lanes' powers add as the string's modes' energies do, and they are what
the engine sums. A first fit on the takes' own power found K two to three
times larger in the bass, and the engine glided that much over its law
there: 10.9 cents from the early window to the late at the upright's C1 at
layer 122, against the law's 3.75.

## In the engine

At each chunk boundary (32 samples) a key's glide is its law times its
partials' power over the chunk before, in the output's units: the law over
the square of the piano's output scale. A voice retunes all its partials to
its key's glide, with its channel's tuning and bend, whenever the two differ
by 0.05 cents or more (`glideStep`), so its partials stay within 0.05 cents of
it. A strike starts unglided and takes its key's glide at its second
boundary, within 1.4 ms. On a mixed build it is the pianos' laws, in the
output's units, weighted by the strings' shares. The open strings do not
glide.

The same measurement on the engine's own renders of the upright's train
takes, 0.4.19 against 0.4.18 at each take's velocity:

| Pitch | C1 | D♯1 | A1 | C2 | F♯2 | A2 | C3 | D3 | E3 | C4 | D4 | G♯4 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Engine's glide at layer 122 | 4.08 | 0.79 | 0.96 | 0.66 | 0.99 | 1.67 | 1.02 | 1.01 | 0.85 | 0.56 | 0.23 | 0.35 |
| The law's | 3.64 | 0.80 | 0.91 | 0.58 | 1.00 | 1.73 | 1.49 | 0.98 | 0.36 | 0.82 | 0.24 | 0.43 |

in cents, early window over late. From E5 up both are under 0.2 cents. At
layer 15 no take's glide reaches the step, and each measures exactly as
on 0.4.18. The five factory demos that do not play the upright (Kakegawa
Grand, Open Strings, Warm Walnut, Felt Nocturne, Hamamatsu Grand) render
byte for byte as on 0.4.18.

What the plug-in plays at a velocity, through its velocity response and
without the strike-to-strike variation, in cents sharp 50 ms and 0.35 s after
the strike, the most among each register's keys:

| Velocity (layer) | A0 to B1 | C2 to F3 | F♯3 to F4 | F♯4 to C8 |
| --- | --- | --- | --- | --- |
| 127 (122.0) | 7.88, 3.59 | 4.39, 1.83 | 1.25, 0.48 | 0.91, 0.26 |
| 100 (110.5) | 2.06, 1.24 | 1.06, 0.35 | 1.79, 0.82 | 0.42, 0.14 |
| 80 (95.9) | 1.78, 1.22 | 0.40, 0.19 | 0.16, 0.07 | 0.24, 0.07 |
| 64 (82.5) | 0.64, 0.44 | 0.25, 0.13 | 0.10, 0.07 | 0.12, 0.05 |

G3 plays sharper at velocity 100 than at 127, as its partials sound stronger
at that layer in their first 50 ms. A strike at velocity 127 plays the
loudest recorded layer, so no velocity plays its strings past the power the
loudest takes reach.

`Keyra.Glide` checks that the loudest upright C2 plays sharp (2.5 cents
21 ms after the strike, 0.07 cents 3 s later), every partial exactly tuned to
its voice's glide through a bend, that it settles as the string decays, that
a soft C2 never retunes, that the grand plays none, that reset clears it and
that the host's blocks do not change it; `Keyra.MeasuredGlide` that the
header is the one its receipt gives and the receipt the current fit's.

## On the dev takes

The upright's 21 dev takes at D♯2, G♯3, B3, C5 and E6 were never fitted.
Taking the engine's glide at each (0.4.19 against 0.4.18) as the prediction,
each recorded glide with an offset per pitch, weighed as the fit weighs them:
the law lowers χ² from 23.47 to 22.53, which 7.1 % of 2000 shuffles of the
predictions among each pitch's takes also do. Fitted freely, the law's scale
on them reads 2.2 times the shipped one, from −2.0 to 5.7 over 95 % of the
draws. The dev pitches' predicted glides reach 0.6 cents at most, under the
takes' own errors of 0.4 to 1.9 cents: they lean the law's way but cannot
confirm it, and do not reject it. E6's three loudest takes glide 3.2 to
4.6 cents flat, which no tension law makes; the law predicts none there.

## Cost

Callgrind, the whole program rendering each factory demo, GCC 13.3.0 Release,
0.4.18 (commit 062c0d1) against 0.4.19:

| Demo | 0.4.18 | 0.4.19 | Change |
| --- | --- | --- | --- |
| 01 Kakegawa Grand | 11.562 G | 11.570 G | +0.07 % |
| 03 Warm Walnut | 8.156 G | 8.163 G | +0.09 % |
| 04 Felt Nocturne | 5.666 G | 5.671 G | +0.09 % |
| 05 Open Strings | 10.668 G | 10.674 G | +0.06 % |
| 06 Helsinki Upright | 10.697 G | 10.709 G | +0.11 % |
| 08 Pop Upright | 11.803 G | 11.840 G | +0.31 % |
| 09 Hamamatsu Grand | 5.002 G | 5.008 G | +0.12 % |
| 10 Three Cities | 8.319 G | 8.326 G | +0.09 % |

A retune recomputes every lane's rotation, so its step decides the cost. Ten
fortissimo strikes on the upright's bass and middle over 10 s
(`keyra_render --model upright`) took 6.214 G instructions on 0.4.18, 6.241 G
at the 0.05-cent step (+0.43 %) and 7.770 G retuning at every chunk (+25 %).

## Against the recordings

`Tools/benchmark_recordings.py` scored every train and dev take of the locked
split on all five pianos, 0.4.18 against 0.4.19:
[upright](../validation/upright-pitch-glide-benchmark-2026-11-04.md). On the
upright no paired mean moves by more than 0.09 and no note passes a
tolerance: dev tuning error falls from 1.809 to 1.768 cents and dev decay
error from 4.13 to 4.04 dB/s, train tuning error rises from 0.276 to 0.282
cents. The other four pianos score every case exactly as on 0.4.18: their
reports differ only in the renderer's path, so no report of theirs is kept.

## Levels

`Keyra.Levels` passes, and the presets that play the upright keep their
typical levels to 0.01 VU (Pop Upright −9.17 to −9.16 VU); Helsinki
Upright's loudest chords rise from 3.31 to 3.64 VU, under their approved
4.22 VU.
`Keyra.FactoryDynamics` fails as on 0.4.18 with four steps fewer under their
floors (1,045 against 1,049), every change Helsinki Upright's, and the same
six chords over their maxima.

## Listening

`/mnt/project-files/keyra/ab-2026-11-04-pitch-glide/` holds A (0.4.18) and B
(0.4.19) on both upright presets, a phrase of fortissimo bass notes, an
octave, a C3 and a bass chord, level-matched on whole-file RMS, with its key.
The owner's verdict goes in `Docs/decisions.md`.

## Known gaps

- One law per piano, read on loud takes' first second. The upright's dev
  takes lean its way but are too few and too noisy to confirm it, and the
  other pianos' takes do not decide one: the New York grand's falls just
  short.
- The glide follows the output's power, which stands for the strings'
  energy only as far as the board radiates the partials alike, so Brightness,
  which scales the partials' levels, also scales the glide.
- The takes are measured from 50 ms after the onset. Before that the glide
  follows the partials' power by the same law, unmeasured, and is highest
  just after the strike: 9.8 cents at C1 at velocity 127, 1.3 ms in.
- A strike plays unglided for its first chunk or two, and the open strings
  do not glide.
