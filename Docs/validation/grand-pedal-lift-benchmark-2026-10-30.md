# Pedal-down benchmark: full pedal at 80 % of the lift against 0.4.1 at 266104c

The grand's sustain pedal going down, alone, scored by `Tools/benchmark_pedal.py`
against Salamander's two pedal-down takes, pedalD1 (train) and pedalD2 (dev),
as in the [realism pass's report](grand-open-strings-benchmark-2026-10-30.md):
the pedal down at 50 ms at the default controls; per third-octave band from
63 Hz to 5 kHz the ring (0.3 to 2.3 s) against the knock (the first 0.3 s),
and the fall from that ring to 2.3–4.3 s; errors are the mean |dB| difference
from a take over the bands, lower is better. Machine-readable in
[the JSON](grand-pedal-lift-benchmark-2026-10-30.json).

At the owner's request (2026-10-30) full pedal lifts the dampers only as far
as 80 % of the pedal did, so the felt still grazes the strings, the ones the
pedal frees with the rest. 0.4.1 at `266104c` is the shipping engine; its
pedal renders as the realism pass's candidate did.

| run | whole ring over knock dB | string peaks | median decay dB/s | ring error, pedalD1 / pedalD2 dB | fall error, pedalD1 / pedalD2 dB |
|---|---|---|---|---|---|
| pedalD1 (train) | 12.9 | 122 | −6.78 | | |
| pedalD2 (dev) | 12.2 | 118 | −6.97 | | |
| 0.4.1 at 266104c | 14.8 | 147 | −6.50 | 2.73 / 2.80 | 2.58 / 2.46 |
| full pedal at 80 % | 10.6 | 124 | −9.59 | 1.21 / 4.74 | 6.10 / 6.29 |

The pedal's knock is unchanged and the freed strings start ringing as
before, then fall faster: their median decay steepens from 6.5 to 9.6 dB/s against the takes' 6.8 and
7.0, so the fall from the ring sits 6.1 and 6.3 dB from the takes' where it
sat 2.6 and 2.5. The ring over the knock moves to 1.2 dB from the train take
and 4.7 dB from the dev take, from 2.7 and 2.8: it was 1.9 to 2.6 dB over
both, and the faster fall takes it under the dev take's. This is the owner's
calibration, not a fit: the recordings' pedal lifts the dampers clear.

## Ring over knock per band (dB)

| band Hz | pedalD1 (train) | pedalD2 (dev) | 0.4.1 at 266104c | full pedal at 80 % |
|---|---|---|---|---|
| 62.5 | −1.4 | −0.6 | 1.4 | −2.8 |
| 78.7 | 11.9 | 10.6 | 13.9 | 9.5 |
| 99.2 | 1.8 | 2.4 | 2.5 | −1.3 |
| 125 | 0.7 | −1.0 | 2.1 | −1.3 |
| 157.5 | −3.6 | −1.2 | −1.6 | −5.1 |
| 198.4 | −10.0 | −6.3 | −7.2 | −9.7 |
| 250 | −11.6 | −5.9 | −8.6 | −11.4 |
| 315 | −17.9 | −12.7 | −15.8 | −18.7 |
| 396.9 | −18.6 | −10.6 | −15.8 | −18.4 |
| 500 | −18.4 | −10.0 | −16.6 | −19.5 |
| 630 | −16.3 | −11.1 | −12.8 | −15.1 |
| 793.7 | −22.5 | −15.7 | −18.0 | −20.4 |
| 1000 | −21.6 | −16.4 | −18.1 | −20.5 |
| 1259.9 | −25.0 | −19.6 | −22.8 | −25.4 |
| 1587.4 | −25.6 | −17.6 | −22.9 | −25.4 |
| 2000 | −25.0 | −19.4 | −20.7 | −22.6 |
| 2519.8 | −29.8 | −23.5 | −26.5 | −28.5 |
| 3174.8 | −33.2 | −26.5 | −30.3 | −32.4 |
| 4000 | −35.1 | −28.3 | −32.3 | −34.4 |
| 5039.7 | −40.8 | −34.9 | −37.3 | −39.7 |

## Fall from the ring to 2.3–4.3 s per band (dB)

| band Hz | pedalD1 (train) | pedalD2 (dev) | 0.4.1 at 266104c | full pedal at 80 % |
|---|---|---|---|---|
| 62.5 | −2.1 | −1.2 | −3.2 | −9.3 |
| 78.7 | −6.9 | −6.5 | −3.3 | −8.2 |
| 99.2 | −2.3 | −4.1 | −1.6 | −7.5 |
| 125 | −6.9 | −4.8 | −1.8 | −7.4 |
| 157.5 | −3.9 | −1.5 | −3.9 | −9.6 |
| 198.4 | −4.5 | −2.4 | −4.7 | −11.3 |
| 250 | −1.8 | −2.5 | −6.9 | −13.1 |
| 315 | −2.4 | −2.0 | −4.0 | −10.1 |
| 396.9 | −2.2 | −3.7 | −5.8 | −11.6 |
| 500 | −2.9 | −4.5 | −5.1 | −11.0 |
| 630 | −6.1 | −4.6 | −9.4 | −15.9 |
| 793.7 | −3.6 | −4.5 | −8.9 | −14.4 |
| 1000 | −6.5 | −4.9 | −9.3 | −14.9 |
| 1259.9 | −6.9 | −6.3 | −8.0 | −12.8 |
| 1587.4 | −8.8 | −10.2 | −10.2 | −15.1 |
| 2000 | −9.6 | −10.0 | −13.6 | −19.0 |
| 2519.8 | −11.0 | −10.9 | −11.0 | −15.2 |
| 3174.8 | −11.6 | −11.0 | −9.4 | −13.1 |
| 4000 | −12.0 | −11.0 | −9.0 | −12.4 |
| 5039.7 | −10.6 | −7.5 | −5.4 | −8.3 |

The upright has no pedal recordings and is not scored here.
