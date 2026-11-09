# The orders a fit left out of a string's series

9 November 2026, Keyra 0.4.30. A struck string sounds every order of its
series, and from one order to the next the hammer's spectrum and the
string's losses change smoothly. A fit leaves an order out where it cannot
tell the partial from what sounds beside it, and 0.4.29 played nothing
there: the Hamamatsu grand's G♯3 holds no 12th to 20th partial, nor 22nd to
25th. 0.4.30 plays each order a series lacks between two it holds, where the
fit holds at least as many orders around the gap as it lacks. Nothing is
fitted: a filled order plays between its two neighbours as a partial between
two recorded pitches does.

The measurement is `Tools/measure_absent_orders.py`; its protocol is at the
head of the tool. It reads the train and dev takes of each piano's locked
split; no sealed take is read, and no number is fitted from it.

## What the recordings show

Each train and dev take and its render at the take's layer, scored as the
benchmark's partial measure scores them: every order the recording holds, in
each of the measure's four windows, where it stands 10 dB over its floor and
within 50 dB of the strongest partial, is a cell, its error the render's
level there less the recording's at the benchmark's gain, at most 30 dB. A
cell whose order the render does not play scores 30 dB. The table gives the
share of cells whose order the render lacks and the share of the error they
carry.

| piano | role | takes | cells | 0.4.29 mean dB | lacked | their error | 0.4.30 mean dB | lacked | their error |
|---|---|---|---|---|---|---|---|---|---|
| Kakegawa grand | train | 276 | 17874 | 3.92 | 0.0 % | 0 % | 3.92 | 0.0 % | 0 % |
|  | dev | 156 | 10698 | 5.26 | 0.2 % | 1 % | 5.26 | 0.2 % | 1 % |
| upright | train | 137 | 7061 | 5.74 | 0.7 % | 4 % | 5.69 | 0.7 % | 4 % |
|  | dev | 21 | 1194 | 7.45 | 0.6 % | 2 % | 7.42 | 0.3 % | 1 % |
| Hamamatsu grand | train | 104 | 5638 | 7.49 | 3.8 % | 15 % | 6.87 | 2.3 % | 10 % |
|  | dev | 23 | 1328 | 9.31 | 7.5 % | 24 % | 9.09 | 6.6 % | 22 % |
| Hamburg grand | train | 40 | 2876 | 4.15 | 0.0 % | 0 % | 4.13 | 0.0 % | 0 % |
|  | dev | 8 | 386 | 7.52 | 0.0 % | 0 % | 7.52 | 0.0 % | 0 % |
| New York grand | train | 61 | 3758 | 7.10 | 0.5 % | 2 % | 7.08 | 0.4 % | 2 % |
|  | dev | 17 | 862 | 8.74 | 0.7 % | 2 % | 8.74 | 0.7 % | 2 % |

On the Hamamatsu, whose fit holds the fewest of its orders, the orders a
render lacked carried 15 % of the partial error on the train takes and 24 %
on the dev takes; on the other pianos 4 % or less. The orders the fits leave
out between a series' first and last order:

| piano | recorded pitches | partials held | orders lacked | filled | in gaps | network keys | partials held | orders lacked | filled | in gaps |
|---|---|---|---|---|---|---|---|---|---|---|
| Kakegawa grand | 22 | 839 | 55 | 28 | 21 | – | | | | |
| upright | 28 | 573 | 33 | 14 | 11 | – | | | | |
| Hamamatsu grand | 27 | 624 | 122 | 60 | 34 | 61 | 1656 | 184 | 89 | 63 |
| Hamburg grand | 10 | 386 | 79 | 22 | 11 | 68 | 2889 | 713 | 205 | 99 |
| New York grand | 13 | 365 | 56 | 21 | 11 | 68 | 2328 | 279 | 120 | 72 |

Most of the orders lacked sit in a series' sparse upper tail, where the
partials the fit held stand 60 to 100 dB under the strongest. The gaps that
matter have strong neighbours: the Hamamatsu's G♯3 lacks its 12th to 20th
partial between neighbours 21 and 30 dB under its strongest, and its F♯1 its
39th to 41st between neighbours 9 and 29 dB under it.

## The mechanism

`fillGap()` in `KeyraEngine.cpp` plays each order a series lacks between two
it holds as `blend()` sets a partial between two recorded pitches: its power
over the window the layers' levels are measured over, its balance and its
stereo image between its neighbours' at its place between their orders,
their lanes paired fastest with fastest, each lane's decay rate mixed in 1/s.
It runs on each recorded pitch's series (`anchorSeries()`), before the two
pitches either side of a key are blended, and on the keyboard network's
series at the keys it holds. Nothing is added below a series' first order or
over its last.

`denseGap()` fills a gap g orders long only where, from g orders under it to
g over it, the series holds at least as many orders as it lacks. A sparse
tail fails it; the Hamamatsu's G♯3, whose window from the 2nd to the 30th
order holds 15 of 29, passes; the 22nd to 25th, four orders on, fail. A
filled partial's lanes take their una-corda bias by their own rank, fastest
first, as a recorded pitch's do; no fit chose one for it.

## Two builds

Both fill between two orders a series holds; the first fills every gap, the
second only where `denseGap()` passes. Against 0.4.29, the paired means of
every train and dev take, summed over the eleven measures other than level
in tolerance units (lower is closer):

| piano | every gap, train | dev | dense stretches, train | dev |
|---|---|---|---|---|
| Kakegawa grand | −0.31 | −0.05 | −0.08 | −0.04 |
| upright | −0.57 | +0.38 | −0.15 | +0.05 |
| Hamamatsu grand | −1.93 | −0.59 | −1.34 | −0.30 |
| Hamburg grand | −0.17 | +0.99 | −0.13 | +0.94 |
| New York grand | −0.17 | +0.13 | −0.11 | +0.05 |

The first stands closer on every piano's train takes and further on three
pianos' dev takes, mostly in the noise between partials: filled orders in a
sparse tail put sound where the recordings hold only what sounds between
their partials, the upright's D♯2 at velocity 122 from 8.13 dB to 10.31. The
second keeps most of the first's gain on the train takes and stands further
on the dev takes by 0.05 or less except the Hamburg's, which both builds take
further on one note. 0.4.30 ships the second, as the dev takes are never
fitted.

## On the benchmark

Against 0.4.29 on every train and dev take
([Kakegawa grand](../validation/grand-series-orders-benchmark-2026-11-09.md),
[upright](../validation/upright-series-orders-benchmark-2026-11-09.md),
[Hamamatsu](../validation/kawai-series-orders-benchmark-2026-11-09.md),
[Hamburg](../validation/hamburg-series-orders-benchmark-2026-11-09.md),
[New York](../validation/newyork-series-orders-benchmark-2026-11-09.md)),
the paired measures that move by 2 % of a tolerance or more:

- The Hamamatsu's train takes stand 0.46 dB closer in partial levels (8.32 to
  7.86), 0.04 cents in tuning, 0.08 dB/s in decay, 0.07 dB early and 0.05 dB
  in the sustain; its dev takes 0.14 dB closer in partial levels (9.63 to
  9.50). Its G♯3 at velocity 95 stands 4.70 dB from its recording in partial
  levels where it stood 14.04, and at velocity 117 6.84 where it stood 14.72.
- The upright's train takes stand 0.02 dB closer in partial levels and
  0.03 dB/s in decay; its dev takes 0.09 dB/s further in decay and 0.02 cents
  in tuning, 0.02 dB closer in partial levels and the sustain.
- The Kakegawa grand's noise stands 0.04 dB closer on its train takes and
  0.02 on its dev takes; the Hamburg's 0.06 closer on its train takes and
  0.43 further on its dev takes; New York's 0.04 closer on its train takes
  and 0.02 further on its dev takes.

Past a tolerance, four scores stand further: the upright's dev B3 at velocity
122 in decay (3.32 to 6.36 dB/s), the Hamburg's dev E3 in noise (5.51 to
6.80 dB, its take at velocity 80 9.1 dB over its recording at 6.35 kHz where
it stood 7.4, the one band the measure scores there), the Hamamatsu's train
E5 in decay (5.19 to 6.42 dB/s), and the Hamamatsu's train G♯3 at velocity 69
loses its noise score, 5.47 dB on 0.4.29. The Hamburg's dev takes are eight,
all from C3 to B5, and its E3 carries their whole move in noise.

On the grand's held-out evaluation (`Tools/evaluate_recordings.py`) the
twelve in-range cases stand where they stood on 0.4.29: 4.950 dB in bands,
3.990 dB in harmonics, 1.676 dB in envelope, 2.270 dB/s in decay, 0.190
cents in pitch and 4.090 ms in rise. The edge cases C1 and C7 at velocity 8
stand 4.602 dB in bands (4.603), 2.284 dB in harmonics and 8.275 dB in
envelope.

## Levels

Filled orders add sound only between two partials a key already plays, so its
level moves little. On the meter the presets' typical playing and the pianos'
default sounds stand within the test's 0.05 VU guard of their approved
readings, and one reading passes its approved level: the Hamburg's loudest
chords through the tube, 2.587909 VU against 2.560835.
`Keyra.FactoryDynamics` fails as it did on 0.4.29, on 1,136 rows (1,040 pairs
under their step floors and 96 chords past its maximum levels) where 0.4.29
failed on 1,134 (1,038 and 96): six pairs are new, a median 0.02 dB under
their floors and 0.11 dB at most, and four of 0.4.29's are gone. Over the
audit's 2,120 pairs the median step and the median chord move under 0.001 dB,
the largest step 0.25 dB.

## The tests

Two checks walked a blend's output alongside the two recorded pitches' fitted
partials and assumed one entry for each order either fit holds. The fills
put them out of step, and both are corrected beside them:
`Keyra.PitchBlend` walks the pitches' series as they are blended, fills
included, and holds every shared order's power, channels, balance and lag at
its place between them, 6,349 of its 119,476 with a filled side.
`Keyra.RateInterpolation` renders, at the lowest, middle and highest recorded
pitches, that the support prior for an unidentified decay leaves a recorded
pitch's sound as it was; a filled order is blended between two orders with
that prior, by design, so the check now takes the nearest pitches whose
series hold no fill. `Keyra.SoftLaneContinuity` found the Hamamatsu's F♯2
playing a filled partial's two equal-rate lanes with each other's una-corda
bias: at a recorded pitch a partial paired with a filled one now plays as
that pitch's series holds it, and a filled partial's equal rates keep their
lane order. The `unit` tier (45 tests) passes.

## What it does not do

It adds no order under a series' first or over its last, and none in a
sparse stretch, where most of the orders lacked sit: the Hamamatsu's dev
takes still lack 6.6 % of their scored cells, 22 % of their partial error.
A filled order plays between its neighbours, which is not the string's own
level there: the hammer's position leaves near-zeros in a struck string's
series, and a fill cannot know one.
