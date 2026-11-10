# How fast the undamped strings grow with the blow

10 November 2026, Keyra 0.4.31. Every strike sets the undamped strings from
F6 up ringing, and how loudly grows with the strike: `fit_realtime_modal.py`
fits one law for every string and pitch, a slope in dB per dB of the level
the strike's layer plays at that rises or falls by a fitted amount per octave
the string lies over the struck fundamental (`halo_slope_fit`). It measures
the law on the recorded pitches from F♯3 up (`HALO_LOWEST`), where the
strings lie at most about four octaves over the key; a bass key plays it up
to seven. New York's law falls by 0.51 per octave from 1.95 at the key's own
pitch, so it passes under 0 at 3.8 octaves, and 0.4.30, which held the law as
fitted at every key, rang the strings louder the softer a bass key was struck.
0.4.31 holds the slope at 0 where the law falls under it: a softer blow moves
the bridge less at every frequency, so it never rings a string louder. No
fitted number changes.

## What the recordings show

Each New York train and dev take and its render at the take's layer, as the
benchmark scores its bands: per third-octave band, the render's level less
the recording's at the benchmark's gain over 0.1 to 0.6 s, where either
stands within 50 dB of the recording's peak and 10 dB over its floor. The
bands from 1.6 to 4 kHz that stood 15 dB or more over their recordings on
0.4.30:

| take | velocity | 0.4.30, largest band over | 0.4.31 |
|---|---|---|---|
| C1 | 13 | +49 dB at 2.5 kHz | under 15 dB |
| C1 | 36 | +37 dB at 2.5 kHz | under 15 dB |
| F1 | 13 | +46 dB at 2.5 kHz | +18 dB at 2 kHz |
| F1 | 36 | +24 dB at 2.5 kHz | under 15 dB |
| A♯1 | 13 | +30 dB at 2.5 kHz | under 15 dB |
| G♯2 | 13 | +18 dB at 2.5 kHz | under 15 dB |
| D♯2 (dev) | 13 | +22 dB at 2.5 kHz | under 15 dB |

A fine spectrum of the C1 at velocity 13 from 0.15 to 1.15 s shows what
sounded there: lines at 1578, 1878, 1998, 2125, 2248, 2390 Hz and on, the
undamped strings from G6 to A♯7, the loudest of them 6 dB under the note's
strongest band, where the recording holds only its floor. The other four
pianos' laws never fall under 0 at any key: the grand's, the upright's and
the Hamamatsu's rise with the octaves, and the Hamburg's falls by 0.06 per
octave from 1.28, to 0.83 at A0's seven octaves.

## Two bounds

Both hold the law where it falls under a bound and leave it as fitted
elsewhere. The first holds it at 1 dB per dB, as a hammer that never grows
duller would bound it: the felt stiffens as it is pressed, so a harder blow is
shorter and brighter. The second holds it at 0. Against 0.4.30, the paired
means of New York's takes summed over the eleven measures other than level in
tolerance units (lower is closer):

| bound | train | dev |
|---|---|---|
| 1 dB per dB | −3.41 | +1.37 |
| 0 dB per dB | −4.56 | −1.90 |

The first stood further on the dev takes in partial levels (10.37 to 10.55 dB)
and the noise between partials (8.87 to 9.17 dB): at 1 dB per dB the strings
fall so far at velocities 13 and 36 that the soft D♯2 and G♯2 stand under
their recordings from 2 kHz up, where those takes hold more than the
render's partials there (D♯2 at velocity 36, from 30 to 150 ms: 2.5 kHz at
−104 dB on the recording, −88 on 0.4.30 and −112 at 1 dB per dB). 0.4.31 ships the second; the
Hamburg's law, which the first held from 4.5 octaves, is never under 0.

## On the benchmark

Against 0.4.30 on every New York train and dev take
([New York](../validation/newyork-halo-slope-benchmark-2026-11-10.md)), the
paired measures that move by 2 % of a tolerance or more: the train takes
stand 1.52 dB closer in the noise between partials (7.98 to 6.46), 0.38 dB in
attack, 0.29 dB early, 0.14 dB in the sustain, 0.06 dB in the envelope and
0.001 in coherence, and 0.32 ms further in rise; the dev takes 0.85 dB closer
in noise (8.87 to 8.02) and 0.20 dB in attack, 0.05 dB further in partial
levels, 0.02 cents in tuning and 0.10 ms in rise. Past a tolerance two scores stand further, both in rise on train takes:
F1 (24.56 to 26.46 ms over its five layers) and A♯1 (5.20 to 6.33 ms). The
Kakegawa grand, the upright, the Hamamatsu and the Hamburg render byte for
byte as on 0.4.30, so their benchmarks and the grand's held-out evaluation
stand where they stood.

## Levels and tests

On the meter every reading stands within its approved level (`Keyra.Levels`
passes). `Keyra.FactoryDynamics` fails as it did on 0.4.30, on the same 1,136
rows: 102 of New York's 2,120 audit pairs move, each by under 0.001 dB, and
the median step and the largest stay as they were. The `unit` tier (45
tests), the `audio` tier's demos and the `perf` tier pass, and `KeyraDSPCxx17`
builds. The 88 keys struck in turn at velocity 90, 120 ms apart with the pedal
down, render on New York in a median 2.90 s of CPU where 0.4.30 took 2.98, seven
alternating runs of each on the development machine, within the runs' spread:
the bound is one comparison per string at a strike.

## What it does not do

A slope of 0 leaves the strings at the level a bass key's loudest layer
rings them at, whatever the layer: the F1 at velocity 13 still stands 16 to
18 dB over its recording from 1.6 to 2.5 kHz. How fast the strings grow
seven octaves over a key is not measured, as no take from F♯3 up reaches
there, and the fitted law is not refitted.
