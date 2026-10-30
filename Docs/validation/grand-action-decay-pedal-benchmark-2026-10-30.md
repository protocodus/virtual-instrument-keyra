# Pedal-down benchmark: the action's knocks at their own decay against 0.4.1 at e9411bb

The grand's sustain pedal going down, alone, scored by `Tools/benchmark_pedal.py`
against Salamander's two pedal-down takes, pedalD1 (train) and pedalD2 (dev),
as in the [pedal-lift report](grand-pedal-lift-benchmark-2026-10-30.md): the
pedal down at 50 ms at the default controls; per third-octave band from 63 Hz
to 5 kHz the ring (0.3 to 2.3 s) against the knock (the first 0.3 s), and the
fall from that ring to 2.3–4.3 s; errors are the mean |dB| difference from a
take over the bands, lower is better. Machine-readable in
[the JSON](grand-action-decay-pedal-benchmark-2026-10-30.json).

The candidate rings the action's knocks at the decay and rise refitted with
them, each body mode 1.5 times as fast as the board's own ring of it, with a
152 ms rise (54 ms at the board's rates); the pedal's knocks stay at the
library's mix. Since the owner's 80 % pedal (2026-10-30) the felt grazes the
strings the pedal frees, which the takes' pedal does not, so each engine was
also built with the dampers lifted clear (`dampersLift` 1) as a probe, which
does not ship.

| run | whole ring over knock dB | string peaks | median decay dB/s | ring error, pedalD1 / pedalD2 dB | fall error, pedalD1 / pedalD2 dB |
|---|---|---|---|---|---|
| pedalD1 (train) | 12.9 | 122 | −6.78 | | |
| pedalD2 (dev) | 12.2 | 118 | −6.97 | | |
| 0.4.1 at e9411bb | 10.6 | 124 | −9.59 | 1.21 / 4.74 | 6.10 / 6.29 |
| candidate 0.4.1 | 7.8 | 124 | −9.59 | 2.88 / 7.56 | 6.10 / 6.29 |
| 0.4.1 at e9411bb, dampers clear (probe) | 14.8 | 147 | −6.50 | 2.73 / 2.80 | 2.58 / 2.46 |
| candidate 0.4.1, dampers clear (probe) | 12.2 | 147 | −6.50 | 0.69 / 4.73 | 2.58 / 2.46 |

The candidate's knock is 2.6 to 2.9 dB louder in its first 0.3 s in every
band; the strings ring as before. With the dampers clear, as in the takes,
its ring over the knock sits within 1 dB of pedalD1's in most bands, 0.69 dB
over all of them where 0.4.1 sat 2.73 dB over, and its whole ring over knock
is 12.2 dB against the takes' 12.9 and 12.2 (14.8): the knock that rang at
the board's rates was too quiet against its own take. pedalD2, never fitted,
rings louder against its knock than pedalD1 from 200 Hz up, so it moves away
(2.80 → 4.73 dB). Under the owner's grazing felt the ring falls faster than
the takes', and the louder knock now shows it: 2.88 and 7.56 dB from the
takes, from 1.21 and 4.74. In the engine test's broadband measure, the energy
from 0.3 to 2.3 s over the first 0.3 s: takes 4.7 and 4.4 dB, 0.4.1 2.8 dB,
the candidate −0.2 dB; dampers clear, 6.9 and 4.1 dB.

## Ring over knock per band (dB)

| band Hz | pedalD1 (train) | pedalD2 (dev) | 0.4.1 at e9411bb | candidate 0.4.1 | 0.4.1, dampers clear | candidate, dampers clear |
|---|---|---|---|---|---|---|
| 62.5 | −1.4 | −0.6 | −2.8 | −5.6 | 1.4 | −1.3 |
| 78.7 | 11.9 | 10.6 | 9.5 | 6.7 | 13.9 | 11.3 |
| 99.2 | 1.8 | 2.4 | −1.3 | −4.1 | 2.5 | −0.2 |
| 125 | 0.7 | −1.0 | −1.3 | −4.1 | 2.1 | −0.5 |
| 157.5 | −3.6 | −1.2 | −5.1 | −7.8 | −1.6 | −4.2 |
| 198.4 | −10.0 | −6.3 | −9.7 | −12.6 | −7.2 | −9.8 |
| 250 | −11.6 | −5.9 | −11.4 | −14.3 | −8.6 | −11.2 |
| 315 | −17.9 | −12.7 | −18.7 | −21.6 | −15.8 | −18.5 |
| 396.9 | −18.6 | −10.6 | −18.4 | −21.3 | −15.8 | −18.5 |
| 500 | −18.4 | −10.0 | −19.5 | −22.4 | −16.6 | −19.3 |
| 630 | −16.3 | −11.1 | −15.1 | −17.9 | −12.8 | −15.5 |
| 793.7 | −22.5 | −15.7 | −20.4 | −23.2 | −18.0 | −20.7 |
| 1000 | −21.6 | −16.4 | −20.5 | −23.3 | −18.1 | −20.8 |
| 1259.9 | −25.0 | −19.6 | −25.4 | −28.3 | −22.8 | −25.5 |
| 1587.4 | −25.6 | −17.6 | −25.4 | −28.2 | −22.9 | −25.5 |
| 2000 | −25.0 | −19.4 | −22.6 | −25.4 | −20.7 | −23.4 |
| 2519.8 | −29.8 | −23.5 | −28.5 | −31.4 | −26.5 | −29.1 |
| 3174.8 | −33.2 | −26.5 | −32.4 | −35.2 | −30.3 | −33.0 |
| 4000 | −35.1 | −28.3 | −34.4 | −37.2 | −32.3 | −35.0 |
| 5039.7 | −40.8 | −34.9 | −39.7 | −42.5 | −37.3 | −40.1 |
