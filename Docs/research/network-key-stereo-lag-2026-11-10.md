# The keys between recorded pitches as wide as their neighbours

10 November 2026, Keyra 0.4.34. On the three pianos the keyboard network
plays between their recorded pitches (the Hamburg, New York and Hamamatsu
grands), each partial's right channel was turned to the lag between the two
recorded pitches' partials of its order, along the shorter arc, as the
engine's `blend()` moves it for the grand and the upright. It now takes the
lag of the nearer pitch's partial, the pitch its lanes already take their
phases from (`Tools/write_network_tables.py`, `align`). Nothing is fitted.

## Why

A partial's lag is how far its right channel trails its left. At the keys
between with recordings (their dev takes, 0.05 to 0.75 s, every partial both
pitches around the key hold up to 6 kHz), neither rule tells it from the
neighbours: the cosine of the miss averaged 0.11, 0.08 and −0.02 for the lag
between them (New York, Hamburg, Hamamatsu), 0.10, 0.07 and 0.02 for the
nearer pitch's. Weighed by power, which the few loudest low partials decide,
the lag between came to 0.44, 0.33 and −0.21 and the nearer pitch's to
0.29, −0.03 and −0.26. A delay wound through each recorded pitch's own
partials did no better.

What does follow is the spread. Between two lags the arc lands nearer
their middle, and across the partials of a key those middles fall closer to
in phase than either pitch's lags do: the keys between stood more alike in
their two channels than the recorded pitches around them. The table's own
partials over the window, the median |correlation| of the two channels at
every layer:

| piano | register | recorded pitches | keys between, 0.4.33 | keys between, 0.4.34 |
|---|---|---:|---:|---:|
| New York | below C3 | 0.61 | 0.59 | 0.55 |
| New York | C3 to B4 | 0.37 | 0.55 | 0.34 |
| New York | C5 up | 0.28 | 0.51 | 0.35 |
| Hamburg | below C3 | 0.37 | 0.49 | 0.37 |
| Hamburg | C3 to B4 | 0.41 | 0.48 | 0.39 |
| Hamburg | C5 up | 0.50 | 0.66 | 0.53 |
| Hamamatsu | below C3 | 0.73 | 0.74 | 0.72 |
| Hamamatsu | C3 to B4 | 0.49 | 0.59 | 0.52 |
| Hamamatsu | C5 up | 0.67 | 0.76 | 0.61 |

Rendered, every key at its piano's middle velocity layer, the whole output
from 0.05 to 0.75 s, New York's keys between C3 and B4 went from 0.64 to
0.35 against its recorded pitches' 0.35, from C5 up from 0.51 to 0.30
against 0.27; the Hamburg's from 0.42, 0.50 and 0.59 to 0.32, 0.42 and 0.53
against 0.32, 0.43 and 0.45.

A key takes its lag from one pitch up to the middle of the gap and from the
other past it, as its phases already did; its power in each channel still
moves between the two.

The tube (Mic 1) hears the two channels' sum, which came out less alike:
New York's read −9.21 VU on typical playing against the −9.02 it read
before, so its `tubeScale` is re-pinned from 1.7066 to 1.7443 and it reads
−9.02 again (`KeyraEngine.cpp`). The Hamburg's and the Hamamatsu's stayed
within 0.05 dB of theirs.

## On the benchmark

Against 0.4.33, the paired means summed over the eleven measures other than
level, in tolerance units (lower is closer): the train takes, the recorded
pitches, do not move.

| piano | train | dev |
|---|---:|---:|
| Hamburg | 0.00 | +0.56 |
| New York | 0.00 | −1.07 |
| Hamamatsu | 0.00 | −0.42 |

Every measure but the rise stays within a hundredth of its tolerance: the
benchmark's coherence (`icc`) is per band and blind to a lag. The rise,
which the onset's sum across the partials decides, moved 0.59 ms further on
the Hamburg's dev takes and 0.99 and 0.44 ms closer on New York's and the
Hamamatsu's. No take stands further past a tolerance on any of the three
([Hamburg](../validation/hamburg-network-key-lag-benchmark-2026-11-10.md),
[New York](../validation/newyork-network-key-lag-benchmark-2026-11-10.md),
[Hamamatsu](../validation/kawai-network-key-lag-benchmark-2026-11-10.md)).
The grand and the upright render as before, byte for byte.

## Left as it is

- **The grand's and the upright's keys between.** `blend()` moves their lag
  along the same arc, but it sums both pitches' lanes, which decorrelates
  them again: the grand's keys between rendered 0.50, 0.48 and 0.34 below
  C3, to B4 and from C5 up against its recorded pitches' 0.67, 0.46 and
  0.47, the upright's 0.19, 0.30 and 0.75 against 0.24, 0.34 and 0.63. Not
  one direction, so not this cause.
- **New York's bass** renders 0.87 at its recorded pitches below C3 against
  0.53 in its five recordings there at that velocity: a gap of the fits,
  not of the keys between.

## Tests

The `unit` tier (45 tests), `Keyra.AudioDemos`, `Keyra.Levels` on the
approved readings and the `perf` tier pass, and `KeyraDSPCxx17` builds.
`Keyra.FactoryDynamics` fails on 997 rows where 0.4.33 failed on 994.
