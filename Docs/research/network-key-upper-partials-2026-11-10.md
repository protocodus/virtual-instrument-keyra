# The keys between recorded pitches no brighter than their neighbours

10 November 2026, Keyra 0.4.33. On the three pianos the keyboard network
plays between their recorded pitches (the Hamburg, New York and Hamamatsu
grands), a key's partials are the orders either recorded pitch around it
holds (`Tools/write_network_tables.py`). An order only one of the two holds
kept, by number, the level that one pitch gives it, moved by the network's
error there. At the key between, that order sounds at a higher frequency
than at the pitch that holds it: the Hamburg's A2 holds its 35th partial at
3.9 kHz, and at E3, where B3 holds no 35th, it sounds at 6.3 kHz, 41 dB over
A2's partials at 6.3 kHz and 32 dB over B3's. The wider the gap between two
recorded pitches, the further such an order moves, which is why the Hamburg
(seven and fourteen semitones between its middle pitches) and New York (ten)
showed it and the Hamamatsu (two to four) hardly did.

Such an order is now held, at every layer, no louder than the louder of the
two recorded pitches at its frequency: the line through each one's partials
in log Hz, held flat past its first and last. Orders both pitches hold, and
the recorded pitches themselves, are as they were. Nothing is fitted.

## What the keyboard shows

Each key struck alone at its piano's loudest layer, its third octaves from 2
to 16 kHz over 0.15 to 0.6 s after onset (both channels' mean) against the dB
line between the recorded pitches around it; the most any band of a key
stands over:

| piano | keys | 0.4.32 | 0.4.33 |
|---|---|---:|---:|
| Hamburg (velocity 123) | E3 to A♯3 | 34 to 42 dB | 16 to 22 dB |
| Hamburg | C3 to D♯3 | 23 to 26 dB | 13 to 17 dB |
| Hamburg | F2 to G♯2 | 18 to 22 dB | 8 to 11 dB |
| New York (velocity 117) | G3 to A♯3, C♯4 to G♯4 | 13 to 21 dB | 6 to 10 dB |
| Hamamatsu (velocity 117) | B2 to D♯3 | 12 to 18 dB | 6 to 8 dB |

The Hamburg's E3 at velocity 123 held 6.3 and 8 kHz 35 and 40 dB over its
recording from 0.15 to 0.6 s; it stands 17 and 19 dB over. At the layers
below, the Hamburg's at velocity 80 and New York's at 61, no key stood so
far over its neighbours. From A4 up a third octave holds one or two partials, and this
measure says little there.

Silencing such an order past both pitches' last partials, where neither fit
holds any, took the Hamburg's E3 to A♯3 to 4 to 15 dB, but it took from New
York's C6 at velocity 117 the partials its recording holds from 8 kHz up,
which neither F6's fit nor G5's reaches (partial levels 6.11 to 8.50 dB off
it). The three pianos' dev takes stood 3.37 closer in sum that way and 3.35
held flat, the latter with no regression past a tolerance, so it ships.

## On the benchmark

Against 0.4.32, the paired means summed over the eleven measures other than
level, in tolerance units (lower is closer): the train takes, the recorded
pitches, do not move.

| piano | train | dev |
|---|---:|---:|
| Hamburg | 0.00 | −3.02 |
| New York | 0.00 | −0.28 |
| Hamamatsu | 0.00 | −0.04 |

The Hamburg's dev takes stand closer in noise (6.43 to 5.66 dB), attack
(7.36 to 7.04) and early level (6.25 to 5.92): its E3 at velocities 80, 108
and 123 by 12.8, 3.2 and 8.9, its E3 at velocity 31 3.7 further, in noise
(4.47 to 6.31 dB). New York's dev takes stand closer in noise (8.08 to 7.95)
and 0.07 dB further in partial levels. No take stands further past a
tolerance on any of the three
([Hamburg](../validation/hamburg-network-high-partials-benchmark-2026-11-10.md),
[New York](../validation/newyork-network-high-partials-benchmark-2026-11-10.md),
[Hamamatsu](../validation/kawai-network-high-partials-benchmark-2026-11-10.md)).
The grand and the upright blend their recorded pitches and render as before,
byte for byte, so their benchmarks and the grand's held-out evaluation stand
as in 0.4.32.

## The other outliers of the keyboard survey

- **The grand's soft A1.** Its fundamental stands 20 dB over its recording at
  velocity 14 and 10 dB at 124. Every piano's wound bass does the same at
  its softest layer, its fundamental 10 to 25 dB over the recordings and 2 to
  9 dB under at the loudest: that is the strike's colour
  (`additionalVelocityColour`, chosen by ear), which tilts a strike's
  partials with its velocity and keeps its energy. A1 stands about 12 dB over
  its neighbours on top of it at every layer: its fit holds its fundamental
  that much over the recording (13 dB at velocity 31, 11 at 124), three of
  its four lanes 2.5 Hz under it. That is the fit's, and only a new fit
  changes it.
- **The upright's soft C5 to F♯5.** The bands that stood over are between
  the partials: over the first 50 ms the render holds there what the
  recordings hold, and from then on it falls more slowly. From 0.05 to
  0.75 s the D5's components between its partials stand 27 to 43 dB under
  its fundamental, the 1967 recording's 47 to 60. Left as it is.

## Tests

The `unit` tier (45 tests), `Keyra.AudioDemos`, `Keyra.Levels` on the
approved readings and the `perf` tier pass, and `KeyraDSPCxx17` builds.
`Keyra.FactoryDynamics` fails on 994 rows where 0.4.32 failed on 995.
