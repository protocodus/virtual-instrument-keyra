# The treble's unison strings (2026-11-06)

From C6 up a key's unison strings lie 2 to 7 cents apart, 4 to 12 Hz at its
fundamental. The series fit follows each partial through a window of six
periods of the fundamental, at least 4 ms, whose main lobe holds the whole
unison, and its lanes reach about 3 cents from the partial, or 10 where one
settles at that bound; the energy gains put what they leave into them. So the
fitted treble beat less than its recordings and sounded from one place. 0.4.26
plays the strings the lanes leave out, on the three pianos whose takes they
bring closer: the Kakegawa grand, the Helsinki upright and the New York grand.
`Tools/fit_treble_unisons.py` measures them on every piano's train takes and
writes the played pianos' into `Source/DSP/MeasuredTrebleUnisons.h`; its
receipt is [treble-unisons-2026-11-06.json](treble-unisons-2026-11-06.json).

## What the recordings hold

Read through a window of 10 ms frames at the fundamental from 50 ms to 1.5 s
after contact, the grand's 12 train takes of F♯7 keep 0.37 to 0.51 of their
coherence between channels and those of A7 0.68 to 0.77; 0.4.25's renders of
the two keys struck at velocity 90 kept 0.89 and 0.91.

Each train take of a recorded pitch from C6 up is read through a 1.45 s Hann
window from 50 ms after contact, within the unison reach of its first two
partials, for the peaks standing 10 dB over their surroundings and within
20 dB of the strongest there. A component is a peak that half the layers or
more, and at least three, hold within 0.6 Hz of one another. Most of them
something already plays: the series' own partial, one of the partial's lanes
(within 1.5 Hz and falling no faster than twice its rate), a component
beside the series that the fit measured, or an undamped string, the key's own
or another key's within 3.5 cents. Some hold too little for a lane to be
timed. The rest nothing in 0.4.25 played: the key's own unison strings tuned
past its lanes and, from F7 up, the second partial of the undamped string an
octave down, which the strike sets ringing through the bridge (the grand's
F♯7 holds one 11.0 Hz under its fundamental, at F♯6's second partial,
3001.1 Hz).

| Piano | Pitches read | Components | Series | Lanes | Beside the series | Undamped strings | Too weak to time | Nothing plays |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Kakegawa grand | 6 | 34 | 9 | 3 | 2 | 5 | 4 | 11 |
| Helsinki upright | 8 | 39 | 14 | 5 | 3 | 5 | 2 | 10 |
| Hamamatsu grand | 7 | 10 | 7 | 1 | | | 1 | 1 |
| Hamburg grand | 3 | 9 | 5 | 1 | | 1 | 1 | 1 |
| New York grand | 4 | 12 | 4 | 1 | | 1 | 2 | 4 |

The strings nothing played, each from the partial's own frequency, how far it
stands under the strongest peak within the reach (the median over the
layers), the layers that hold it and the lanes the fit times it with:

| Piano | Pitch | Partial | From the partial (Hz) | Under the strongest (dB) | Layers | Lanes |
| --- | --- | ---: | --- | --- | --- | --- |
| Kakegawa grand | C6 | 2 | −11.05 | 17.1 | 12 | 1 |
| | F♯6 | 2 | −9.22 | 14.9 | 9 | 2 |
| | A6 | 2 | −8.12 | 8.4 | 12 | 2 |
| | F♯7 | 1 | −14.29, −11.01, −5.13 | 11.5, 1.6, 2.7 | 8, 12, 8 | 2, 2, 2 |
| | A7 | 1 | −19.05, −4.19, +4.25, +14.96 | 8.0, 8.2, 0, 16.3 | 12, 12, 11, 10 | 1, 2, 2, 2 |
| Helsinki upright | F♯6 | 2 | −14.28, −11.20 | 13.2, 11.7 | 4, 4 | 1, 1 |
| | G♯6 | 1 | −4.00 | 1.8 | 5 | 1 |
| | A♯6 | 2 | −18.16, −13.74 | 3.2, 11.6 | 5, 5 | 2, 1 |
| | C7 | 2 | −14.78 | 9.9 | 4 | 2 |
| | E7 | 1 | −13.67 | 6.6 | 3 | 1 |
| | G7 | 1 | −10.31, +3.76 | 3.3, 3.1 | 4, 4 | 2, 2 |
| | G7 | 2 | +6.89 | 10.7 | 3 | 1 |
| Hamamatsu grand | D♯6 | 2 | +5.18 | 2.2 | 3 | 2 (not played) |
| Hamburg grand | D♯6 | 1 | −2.38 | 4.2 | 3 | 2 (not played) |
| New York grand | F6 | 2 | −5.82 | 3.4 | 3 | 1 |
| | A♯6 | 2 | +6.55 | 0.9 | 3 | 1 |
| | G♯7 | 2 | +10.18, +26.02 | 3.2, 0.7 | 3, 3 | 1, 2 |

The grand's A7 holds one string louder than its series' fundamental
(0 dB, the strongest within the reach), 4.25 Hz over it.

## How it is measured

Each string is read as the analysis reads a component beside the series
(`piano_analysis.analyse_anchor`): through its own Blackman-Harris window,
whose main lobe ends where the nearest other component begins, on the
recording itself, fitted across the layers and carried into the engine's
frame and the header's layers as the fit carries a component beside the
series (`fit_realtime_modal.anchor_data` and `on_grid`). It takes two lanes,
as the analysis fits a component where an undamped string may ring: the
strings' quick early fall and their slow ringing on. With one, F♯7's strings
fell at 4 to 7 per second where through their own windows they fall at 2 to 4
after the first half second. Two lanes the fit gives the same rate and pitch
are one (the grand's F♯7, its nearest string), and a lane left at the slowest
rate the fit allows was not timed and is refused: New York's G♯7 left one
there at −76 dB in its loudest layer, which would have rung on for half an
hour. Each frame is weighed against the envelope within 0.3 s of it, as a
partial's frames are. The tool's docstring gives the whole protocol, and
`Keyra.MeasuredTrebleUnisons` checks that the receipt is current and the
header is the one it gives.

The grand's F♯7 holds one more component nothing plays, at its second partial
10.1 Hz under it, 6.8 dB under the strongest there; the fit's frame leaves it
out by its rules for a component beside the series, as it would have left it
out of the fit.

## In the engine

`strike()` plays each recorded pitch's strings as it plays the components
beside the series: a key between two recorded pitches takes each one's
strings at that pitch's share in power, each string at the partial's pitch as
the key builds it moved by the string's cents from the stiff series, spread
by the unisons modifier and heard through the string's own two pickups. Two
things it does that a component beside the series does not:

- **The strings start in phase with the partial.** The hammer sets every
  string of a unison off together: each string starts in phase with the
  partial's lanes as they sum at contact in the left channel, whose pickups
  are real.
- **Their power comes out of the partial's lanes.** The fit's energy gains
  matched the lanes to the whole unison over 50 to 750 ms, so the strings
  take their power from the lanes alike. With the lanes' amplitude s and the
  strings' g, s² own + 2sg cross + g² beside = own, where own is the lanes'
  power over 50 to 750 ms, beside the strings' among themselves and cross the
  lanes' with the strings', every pair summed as `windowPower` sums a
  partial's lanes. The pairs count: the lanes beat, and the grand's F♯7
  struck hard plays two fifths of the power its lanes have one by one. Where
  the lanes would keep less than a quarter of their power (`unisonFloor`, the
  most the fit's energy gains moved a partial's lanes, 6 dB), the strings
  give way.

`Keyra.Engine` checks that the grand's F♯7 and A7, struck at velocity 90,
keep less than 0.85 of their fundamentals' coherence between channels.

The 88 keys struck in turn at velocity 90, 120 ms apart with the pedal down,
render 14 s of audio in a median 3.57 s of CPU on the grand where 0.4.25
took 3.51 (+1.7 %), 2.50 on the upright against 2.53 (−0.8 %) and 3.05 on
New York against 2.79 (+9.5 %), seven runs of each in alternating order on
a 2.1 GHz Xeon: a development machine's figure, not Reason's. They carry
0.4.26's retrained keyboard network too, which New York's keys between
recorded pitches play since.

## The candidates

Each candidate was scored by `Tools/benchmark_recordings.py` on every train
and dev take from C6 up of all five pianos, paired against 0.4.25: each
measure's mean change in `Tools/compare_benchmarks.py`'s tolerance, summed
over the eleven measures other than level, so that a lower sum is closer to
the recordings. They differ in how the strings take their power from the
lanes and in how the strings are fitted.

| Candidate | The strings | Train (176) | Dev (59) |
| --- | --- | ---: | ---: |
| U2 | power taken from the lanes in order of their rate | +2.87 | +2.05 |
| U3 | from the lane within 1.5 Hz first, then from all evenly | +1.13 | +0.41 |
| U4 | from the nearest lanes, the beats not counted | +0.88 | +0.16 |
| U5 | matched over every pair of lanes and strings, one lane a string | −0.15 | −0.64 |
| U6 | as U5, two lanes a string, frames weighed within 0.3 s | −0.09 | +0.14 |
| O6 | U6 and the own string's per-pitch slope ([halo-own](halo-own-2026-11-05.md)) | −0.09 | +0.27 |
| U7 | O6, the strings starting in phase with the partial | −0.57 | −0.98 |

A first candidate, U1, which floored the lanes and took nothing from them,
grew the treble's power, and the grand's A7 and the Hamburg's D♯6 sustained
much further from their recordings; it was set aside on the full benchmark.
U3's even share took twice its power from F♯7's nearest string, which missed
the 1.5 Hz test by 0.05 Hz, and struck it 4 dB loud over the first 100 ms; U4
gave each string the lanes nearest it.

U7 ships, but not for every piano. Piano by piano (from C6 up, against 0.4.25,
summed as above):

| Piano | Train takes | Train | Closer, further | Dev takes | Dev | Closer, further |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| Kakegawa grand | 84 | −1.01 | 6, 5 | 44 | −1.04 | 6, 5 |
| Helsinki upright | 38 | −0.37 | 6, 5 | 5 | −2.25 | 8, 3 |
| New York grand | 17 | −1.15 | 7, 4 | 7 | −0.06 | 6, 5 |
| Hamamatsu grand | 25 | +0.43 | 5, 5 | 3 | unchanged | |
| Hamburg grand | 12 | +1.74 | 3, 8 | 0 | | |

The Hamamatsu's and the Hamburg's train takes, on which their one string each
was measured, stand further from the recordings with it, and none of their
dev takes changes: the Hamburg's D♯6 moves 0.08 to 0.13 in coherence and 0.76
to 1.57 dB in stereo balance. So those two pianos are measured and not played
(`PLAYED` in the tool), and the three that play come closer by 0.88 on their
139 train takes and 1.01 on their 56 dev takes.

The grand's F♯7 now plays F♯6's second partial twice over in a way: as one
of its strings, 2.4 Hz under its own undamped string's pitch, and through
that own string, whose level its strikes set where the halo fit's window
hears the two as one. Letting the own string give way wherever a string
beside the series lies within 4 Hz of it, as it gives way to a lane, silences
it at D♯7 and F♯7, and the grand's treble stands further from its recordings:
its 44 dev takes by +2.02 and its 84 train takes by +0.32, summed as above,
D♯7's dev sustain 1.03 dB further and F♯7's 0.24 to 0.27. So both play.

## Against the recordings

Over the three pianos that play the strings, against 0.4.25 from C6 up, the
dev takes stand closer in stereo balance (0.57 dB), tuning (0.31 cents), rise
(0.17 ms), coherence (0.021) and decay (0.06 dB/s), and further in sustain
(0.41 dB), partial levels (0.29 dB), envelope (0.27 dB), early (0.04 dB) and
attack (0.02 dB). On the grand, whose 44 dev takes carry most of it, the
treble's stereo balance comes 0.71 dB closer and its coherence 0.026, and its
sustain stands 0.53 dB, partial levels 0.35 dB and envelope 0.34 dB further.
New York's train takes from C6 up decay 0.48 dB/s closer and the upright's
dev takes tune 0.99 cents closer.

Read as above, at velocity 90, the grand's F♯7 now keeps 0.76 of its
coherence, against 0.37 to 0.51 in the recordings, and its A7 0.67, against
0.68 to 0.77.

Ten of the grand's scores, at four notes, stand further by more than their
tolerance (largest first; 0.4.25 → 0.4.26): C8's sustain (dev 16.28 → 17.61 dB, train 17.07 → 18.28), its partial
levels (dev 10.19 → 11.39, train 9.69 → 10.80) and envelope (dev 2.54 →
3.63), D♯7's dev sustain (4.14 → 5.30) and envelope (3.26 → 3.79), A6's
partial levels (dev 2.45 → 3.61, train 2.51 → 3.64) and F♯7's dev sustain
(5.00 → 5.58). C8 is not calibrated and plays A7's data, its four strings
with it; D♯7 has no recording of its own in the fit and takes F♯7's. The
upright's G7 train sustain stands 11.71 → 12.63 dB. The whole benchmark of
0.4.26, which carries the retrained keyboard network too, is in each piano's
[validation report](../validation/grand-network-unisons-benchmark-2026-11-06.md).

The held-out evaluation (`Tools/evaluate_recordings.py`, the grand) moves
only at C6, whose string it plays: at velocity 8 the harmonic levels stand
2.78 → 2.58 dB, the broad bands 7.18 → 7.13 dB, the partial decay 14.72 →
14.62 dB/s and the rise 1.17 → 1.27 ms.

## What it leaves

- The strings that lie between two recorded pitches are cross-faded between
  them, as the components beside the series are: a key between plays both
  pitches' strings at their shares, not one unison of its own.
- The grand's F♯7 still keeps more coherence than its recordings (0.76
  against 0.37 to 0.51), and its strings, with A7's, sound 1 to 4 dB loud over
  the first 100 ms and fall faster late than the recordings' do through the
  same windows: the fit gives them pairs of beating lanes of like rate where
  the recordings hold a quick and a slow one.
- The treble's sustain and partial levels stand further on the grand,
  most at C8, D♯7 and A6.
- Only the first two partials are searched: the reach of the third and
  higher crosses the next partial's lanes.
- The Hamamatsu's and the Hamburg's strings are measured and not played.
