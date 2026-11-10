# Pedal wash benchmark: candidate 0.4.36 against 0.4.35 at 8d3652c

The sound a pedalled note leaves between its partials, the open strings its
strike sets ringing, scored by `Tools/benchmark_pedal_wash.py` against the
Yamaha C3's pedal-down takes (pitches C1 to D♯6 in minor thirds, three
layers; 17 train pitches the candidate's level and its fall toward the treble
are fitted on, 5 dev pitches never fitted). The Yamaha C3 is the corpus kept
as acoustic evidence for behaviour the pianos share; it is none of Keyra's
five, so a piano is scored on how its own notes stand against their wash,
never on its tone. No audio of the library is kept: its takes' band energies
are tracked as numbers in `Tools/corpus/yamaha-c3-pedal-wash.json`.

Each render plays one key under the pedal at the default controls. From the
onset, in the windows 0.15–0.5, 0.5–1.5, 1.5–3 and 3–6 s and per octave band
from 150 Hz to 2.4 kHz: the energy between the key's partials over the band's
whole energy in the first window where the band holds partials, and over the
whole note's where it lies under the first partial. Both are ratios within
one file. A row is scored where the pedal-down take stands 6 dB over the
pedal-up take; the figures are the render's ratio minus the takes', in dB,
as a median and as the mean |dB| over the rows. Machine-readable in
[the JSON](pedal-wash-benchmark-2026-11-10.json).

## Bands holding partials

| piano | run | train median | train mean \|dB\| | dev median | dev mean \|dB\| |
|---|---|---|---|---|---|
| Kakegawa grand | 0.4.35 | −26.3 | 26.7 | −22.2 | 22.6 |
| Kakegawa grand | candidate | −1.1 | 5.7 | +4.7 | 6.4 |
| Helsinki upright | 0.4.35 | −20.4 | 22.7 | −18.2 | 20.1 |
| Helsinki upright | candidate | −0.2 | 8.0 | +1.3 | 7.5 |
| Hamamatsu grand | 0.4.35 | −21.7 | 24.2 | −22.9 | 24.0 |
| Hamamatsu grand | candidate | −0.4 | 6.6 | +1.4 | 7.6 |
| Hamburg grand | 0.4.35 | −13.2 | 15.5 | −11.2 | 13.6 |
| Hamburg grand | candidate | +1.7 | 5.9 | +4.5 | 7.4 |
| New York grand | 0.4.35 | −17.8 | 19.8 | −13.5 | 15.8 |
| New York grand | candidate | −5.3 | 8.9 | −3.0 | 7.6 |

Train rows 484 and dev rows 129 per run.

## Per window, median dB (train / dev)

| piano | run | 0.15–0.5 s | 0.5–1.5 s | 1.5–3 s | 3–6 s |
|---|---|---|---|---|---|
| Kakegawa grand | 0.4.35 | −12.5 / −9.5 | −23.0 / −18.7 | −31.6 / −28.4 | −42.0 / −38.1 |
| Kakegawa grand | candidate | −0.3 / +5.8 | +1.6 / +6.2 | −1.1 / +4.7 | −8.0 / −4.7 |
| Helsinki upright | 0.4.35 | −6.9 / −5.4 | −16.1 / −12.1 | −28.4 / −22.1 | −39.7 / −33.7 |
| Helsinki upright | candidate | +3.8 / +3.2 | +3.0 / +5.9 | −2.0 / +0.1 | −11.5 / −9.0 |
| Hamamatsu grand | 0.4.35 | −12.4 / −14.8 | −19.0 / −21.8 | −28.6 / −25.5 | −37.2 / −36.9 |
| Hamamatsu grand | candidate | +1.8 / +2.5 | +3.3 / +4.1 | −0.9 / +1.5 | −9.7 / −6.2 |
| Hamburg grand | 0.4.35 | −4.1 / +0.9 | −9.7 / −6.0 | −20.4 / −15.5 | −30.4 / −25.0 |
| Hamburg grand | candidate | +2.3 / +5.4 | +5.0 / +7.3 | +2.3 / +4.2 | −5.0 / −3.3 |
| New York grand | 0.4.35 | −6.5 / −2.5 | −12.6 / −6.4 | −24.2 / −16.3 | −35.8 / −27.4 |
| New York grand | candidate | −1.1 / +1.1 | −1.1 / +2.3 | −6.8 / −4.5 | −17.1 / −14.1 |

## Per register of the struck key, median dB (train / dev)

| piano | run | C1–A2 | C3–A4 | C5–D♯6 |
|---|---|---|---|---|
| Kakegawa grand | 0.4.35 | −24.8 / −21.1 | −26.7 / −28.0 | −28.1 / −15.4 |
| Kakegawa grand | candidate | −1.7 / +4.3 | −1.1 / −1.8 | −1.0 / +9.7 |
| Helsinki upright | 0.4.35 | −12.0 / −10.3 | −23.7 / −22.8 | −28.5 / −21.9 |
| Helsinki upright | candidate | −1.1 / +2.2 | +0.4 / −6.3 | −1.2 / +8.7 |
| Hamamatsu grand | 0.4.35 | −18.1 / −19.1 | −24.2 / −29.2 | −30.0 / −23.2 |
| Hamamatsu grand | candidate | −0.7 / +2.7 | −1.4 / −7.5 | +4.5 / +7.6 |
| Hamburg grand | 0.4.35 | −10.7 / −3.8 | −14.8 / −17.8 | −14.4 / −9.0 |
| Hamburg grand | candidate | +2.4 / +6.3 | +1.4 / −1.7 | +2.0 / +8.5 |
| New York grand | 0.4.35 | −10.4 / −4.5 | −20.0 / −22.5 | −28.2 / −16.3 |
| New York grand | candidate | −3.8 / −0.4 | −5.7 / −8.0 | −7.9 / +1.1 |

## Bands under the first partial, median and mean |dB| (train / dev)

| piano | run | median | mean \|dB\| |
|---|---|---|---|
| Kakegawa grand | 0.4.35 | −19.9 / −10.5 | 21.2 / 15.1 |
| Kakegawa grand | candidate | −2.7 / −1.2 | 7.4 / 8.3 |
| Helsinki upright | 0.4.35 | −7.8 / −9.3 | 15.6 / 17.3 |
| Helsinki upright | candidate | +4.9 / +0.7 | 9.6 / 10.5 |
| Hamamatsu grand | 0.4.35 | −20.4 / −23.8 | 21.3 / 27.2 |
| Hamamatsu grand | candidate | +3.5 / +0.9 | 6.8 / 9.6 |
| Hamburg grand | 0.4.35 | −3.3 / −2.1 | 12.2 / 11.4 |
| Hamburg grand | candidate | +5.2 / +5.9 | 9.0 / 8.6 |
| New York grand | 0.4.35 | −14.4 / −18.4 | 17.6 / 22.7 |
| New York grand | candidate | −5.0 / −10.8 | 9.3 / 12.7 |

## Reading

0.4.35 rings the open strings only through the notes' drive, which builds the
strings that share a note's partials: between the partials every piano stood
11 to 26 dB under the takes, further the later the window. The candidate
starts every open string at the strike, sized on the grand against the train
pitches; the same two numbers play on all five pianos, each against its own
partials.

- The level is fitted on the grand's train rows and stands within 1.6 dB of
  them from 0.15 to 3 s; its dev pitches, five keys, stand 4.7 dB over. The
  other pianos' dev medians lie 1.5 to 2.8 dB over their train medians. The
  spread from key to key is the larger part of every mean |dB| here.
- From 3 to 6 s every piano falls 3 to 17 dB under the takes. Full pedal
  leaves the felt grazing the strings at the owner's request (`dampersLift`),
  so Keyra's open strings die away faster than a grand's with its dampers
  clear; that choice stands.
- The fall toward the treble (2.7 dB per octave of the struck key) is fitted
  on the grand. The upright, the Hamamatsu and the Hamburg follow it within
  5 dB by register on train; New York stands 4 to 8 dB under throughout.
- The layers are the preset's playback bins, scored at velocities 60, 100
  and 120: the capture's strike force is unknown, and the three layers'
  medians agree within 1 dB on the grand.
- Over 2.4 kHz the pedal-down takes do not clear the pedal-up takes, so
  nothing is scored there; the candidate's level there follows the law the
  lower bands fit.
