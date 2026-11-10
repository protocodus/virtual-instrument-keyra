# How a note holds up under the pedal: 0.4.36 against the Yamaha C3's pedal pairs

Keyra plays a note struck under the pedal with a longer ring (its partials'
decay rates fall by 0.20 on the grand's and the Hamamatsu's strings and 0.30
on the others', less up the series) and drives the open strings 1.65 times as
hard as without it. Both sizes came with 0.4.12 and have no source. This
measures them; the engine is unchanged.

`Tools/benchmark_pedal_wash.py` reports it beside the sound between the
partials, by the same protocol and from the same tracked numbers
(`Tools/corpus/yamaha-c3-pedal-wash.json`): the whole note's energy from
150 Hz to 6 kHz, pedal down less pedal up, in the windows 0.5–1.5, 1.5–3 and
3–6 s after the onset, less the same in 0.15–0.5 s, so that neither take's
strike nor its scale counts. Pitches C1 to D♯6 in minor thirds, three layers
(66 pairs: 51 on the 17 train pitches, 15 on the 5 dev pitches), each
piano at its default controls.

## The note under the pedal less without, dB, median (0.5–1.5 / 1.5–3 / 3–6 s)

| | C1–A2 | C3–A4 | C5–D♯6 |
|---|---|---|---|
| the Yamaha C3's takes | +0.3 / +0.7 / +1.6 | +3.1 / +5.2 / +6.7 | +1.3 / +3.9 / +3.6 |
| Kakegawa grand | +0.5 / +1.0 / +1.3 | +1.2 / +2.1 / +2.6 | +1.7 / +1.2 / +1.0 |
| Helsinki upright | +0.9 / +1.8 / +2.5 | +1.9 / +1.9 / +2.2 | +1.2 / +1.8 / +3.5 |
| Hamamatsu grand | +0.6 / +1.2 / +1.9 | +0.9 / +2.5 / +3.6 | +1.4 / +3.5 / +6.4 |
| Hamburg grand | +0.7 / +2.0 / +3.8 | +1.6 / +4.4 / +4.1 | +1.3 / +2.1 / +4.6 |
| New York grand | +0.6 / +1.7 / +3.5 | +1.0 / +2.7 / +5.4 | +1.7 / +4.7 / +7.7 |

## Render minus the takes, pair by pair

| piano | train median | train mean \|dB\| | dev median | dev mean \|dB\| |
|---|---|---|---|---|
| Kakegawa grand | +0.2 / −1.2 / −1.4 | 2.2 / 3.1 / 3.0 | −2.1 / −3.6 / −0.7 | 3.7 / 3.6 / 2.5 |
| Helsinki upright | +0.2 / −0.3 / −1.6 | 2.3 / 2.8 / 3.2 | −1.4 / −2.9 / +1.3 | 3.2 / 4.5 / 3.0 |
| Hamamatsu grand | +0.3 / −0.1 / −0.9 | 2.5 / 2.3 / 2.8 | −1.6 / −1.3 / +2.3 | 3.2 / 2.6 / 8.1 |
| Hamburg grand | −0.1 / −0.4 / +0.4 | 2.3 / 2.6 / 3.2 | −1.4 / −2.4 / +1.8 | 3.0 / 3.1 / 3.2 |
| New York grand | +0.5 / +0.7 / +0.9 | 2.3 / 2.5 / 2.8 | −1.7 / −1.3 / +4.0 | 3.0 / 2.6 / 4.7 |

## Other sizes on the grand, C2 to D♯6 (42 train pairs, 12 dev)

A scratch build with the two sizes switchable, the pedalled ring's share of
the decay rate and the drive of the open strings under the pedal; not kept.

| the grand with | train median | train mean \|dB\| | dev median | dev mean \|dB\| |
|---|---|---|---|---|
| 0.4.36 as it ships | +0.4 / −2.1 / −2.0 | 2.6 / 3.5 / 3.5 | −3.4 / −4.0 / +0.2 | 4.6 / 4.3 / 2.9 |
| the pedalled ring's share doubled (0.40) | +0.9 / −1.0 / −0.3 | 2.6 / 3.6 / 2.8 | −2.6 / −3.2 / +2.0 | 4.3 / 3.2 / 2.8 |
| the share at 0.80 | +1.9 / +1.3 / +2.0 | 3.5 / 4.1 / 3.5 | −0.9 / −1.1 / +4.9 | 3.8 / 2.1 / 4.3 |
| the share at 0.80, the same up the series | +2.0 / +1.9 / +2.7 | 3.8 / 4.3 / 3.6 | −0.6 / −0.2 / +5.3 | 3.8 / 2.0 / 5.1 |
| the bridge drive at 1 | +0.4 / −2.1 / −1.9 | 2.5 / 3.5 / 3.5 | −3.3 / −4.0 / +0.2 | 4.6 / 4.3 / 2.9 |
| at 4 | +0.5 / −1.9 / −2.4 | 2.7 / 3.4 / 3.7 | −3.4 / −3.9 / +0.4 | 4.6 / 4.3 / 2.8 |
| at 9 | +1.0 / −0.8 / −2.4 | 3.1 / 3.2 / 3.9 | −3.3 / −3.6 / +0.6 | 4.7 / 4.1 / 2.6 |
| at 21 | +2.1 / +2.1 / −2.3 | 4.6 / 3.5 / 3.8 | −2.8 / −2.3 / +0.9 | 5.0 / 3.4 / 2.4 |
| at 41 | +4.3 / +6.2 / −0.1 | 6.3 / 6.1 / 3.5 | −2.5 / −1.1 / +1.8 | 6.2 / 3.0 / 2.7 |

## Reading

- Every piano's train median stands within 1.6 dB of the takes in every
  window, and each pair lies 2 to 3 dB from its take either way: the takes
  differ from key to key by more than the pianos differ from them.
- By register the grand holds up as the takes do from C1 to A2 and 3 dB
  short of them from C3 up at 1.5 to 3 s. The other pianos stand 1 to 3.5 dB
  short there from C3 to A4 and within 2 dB from C5 up, and from C1 to A2
  they hold up as much as 2 dB longer than the takes.
- Twice the grand's share halves its shortfall from C3 to A4 and takes the
  train pairs' mean miss at 3 to 6 s from 3.5 to 2.8 dB and the dev pairs' at
  1.5 to 3 s from 4.3 to 3.2 dB. It also plays the first half second 1.3 dB
  louder against the note without the pedal (+2.1 dB for +0.8), where the
  takes' median is 0.6 dB quieter; the window is this measure's reference, so
  the tables do not show it. Four times the share overshoots every window.
- The drive of the open strings moves the train medians 1.3 dB at most from
  1 to 9 times. At 21 times the median stands 2 dB over the takes to 3 s and
  still 2 dB under them after, and the pairs' mean miss from 0.5 to 1.5 s
  rises from 2.6 to 4.6 dB: the strings it builds are not the ones the
  Yamaha's keys build.
- The takes' rise comes late, +1.3 to +3.1 dB by 0.5 to 1.5 s and +3.9 to
  +5.2 dB after it from C3 up, as a slower sound beside the note would make
  it. A lower decay rate lifts every window from the start. Neither size
  was changed.

The Yamaha C3 is one piano and none of Keyra's five; the capture's strike
force is unknown and its two pedal states are separate strikes.
