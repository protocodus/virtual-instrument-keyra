# Pedal-down benchmark: candidate 0.4.1 against 0.4.1 at 4b11922

The grand's sustain pedal going down, alone, scored by `Tools/benchmark_pedal.py`
against Salamander's two pedal-down takes: pedalD1 (train), which the open
strings' decay law and their lift levels are fitted on, and pedalD2 (dev),
never fitted. Each render plays the pedal down at 50 ms at the default
controls. Per third-octave band from 63 Hz to 5 kHz, from the onset: the ring
(the energy from 0.3 to 2.3 s) against the knock (the whole energy of the
first 0.3 s), and the fall from that ring to the energy from 2.3 to 4.3 s,
both in dB, so neither depends on a file's scale. The errors are the mean
|dB| difference from a take over the bands; lower is better. Machine-readable
in [the JSON](grand-open-strings-benchmark-2026-10-30.json).

| run | whole ring over knock dB | string peaks | median decay dB/s | ring error, pedalD1 / pedalD2 dB | fall error, pedalD1 / pedalD2 dB |
|---|---|---|---|---|---|
| pedalD1 (train) | 12.9 | 122 | −6.78 | | |
| pedalD2 (dev) | 12.2 | 118 | −6.97 | | |
| 0.4.1 at 4b11922 | −32.3 | 44 | −9.39 | 55.54 / 60.22 | 8.54 / 8.66 |
| candidate 0.4.1 | 14.8 | 147 | −6.50 | 2.73 / 2.80 | 2.58 / 2.46 |

The shipping engine's open strings rang only through the body's knock, 40 to
45 dB under the takes' ring, one resonator per key at its fundamental. The
candidate's ring stands 1.9 to 2.6 dB more over its knock than the takes'
does, as the body's modes hold only part of the recorded knock below 1 kHz and
none of it above (README, Known gaps); its strings' levels are fitted in the
take's own scale at the pedal's mix.

## Ring over knock per band (dB)

| band Hz | pedalD1 (train) | pedalD2 (dev) | 0.4.1 at 4b11922 | candidate 0.4.1 |
|---|---|---|---|---|
| 62.5 | -1.4 | -0.6 | -50.3 | 1.4 |
| 78.7 | 11.9 | 10.6 | -32.8 | 13.9 |
| 99.2 | 1.8 | 2.4 | -45.0 | 2.5 |
| 125 | 0.7 | -1.0 | -46.3 | 2.1 |
| 157.5 | -3.6 | -1.2 | -56.0 | -1.6 |
| 198.4 | -10.0 | -6.3 | -65.7 | -7.2 |
| 250 | -11.6 | -5.9 | -66.9 | -8.6 |
| 315 | -17.9 | -12.7 | -70.6 | -15.8 |
| 396.9 | -18.6 | -10.6 | -64.1 | -15.8 |
| 500 | -18.4 | -10.0 | -75.9 | -16.6 |
| 630 | -16.3 | -11.1 | -65.9 | -12.8 |
| 793.7 | -22.5 | -15.7 | -75.9 | -18.0 |
| 1000 | -21.6 | -16.4 | -84.4 | -18.1 |
| 1259.9 | -25.0 | -19.6 | -90.2 | -22.8 |
| 1587.4 | -25.6 | -17.6 | -91.3 | -22.9 |
| 2000 | -25.0 | -19.4 | -92.3 | -20.7 |
| 2519.8 | -29.8 | -23.5 | -93.3 | -26.5 |
| 3174.8 | -33.2 | -26.5 | -94.3 | -30.3 |
| 4000 | -35.1 | -28.3 | -95.2 | -32.3 |
| 5039.7 | -40.8 | -34.9 | -96.2 | -37.3 |

## Fall from the ring to 2.3–4.3 s per band (dB)

| band Hz | pedalD1 (train) | pedalD2 (dev) | 0.4.1 at 4b11922 | candidate 0.4.1 |
|---|---|---|---|---|
| 62.5 | -2.1 | -1.2 | -13.2 | -3.2 |
| 78.7 | -6.9 | -6.5 | -13.3 | -3.3 |
| 99.2 | -2.3 | -4.1 | -12.6 | -1.6 |
| 125 | -6.9 | -4.8 | -14.4 | -1.8 |
| 157.5 | -3.9 | -1.5 | -15.1 | -3.9 |
| 198.4 | -4.5 | -2.4 | -15.0 | -4.7 |
| 250 | -1.8 | -2.5 | -16.3 | -6.9 |
| 315 | -2.4 | -2.0 | -15.1 | -4.0 |
| 396.9 | -2.2 | -3.7 | -18.9 | -5.8 |
| 500 | -2.9 | -4.5 | -16.5 | -5.1 |
| 630 | -6.1 | -4.6 | -21.2 | -9.4 |
| 793.7 | -3.6 | -4.5 | -18.9 | -8.9 |
| 1000 | -6.5 | -4.9 | -12.0 | -9.3 |
| 1259.9 | -6.9 | -6.3 | -7.3 | -8.0 |
| 1587.4 | -8.8 | -10.2 | -7.3 | -10.2 |
| 2000 | -9.6 | -10.0 | -7.3 | -13.6 |
| 2519.8 | -11.0 | -10.9 | -7.3 | -11.0 |
| 3174.8 | -11.6 | -11.0 | -7.3 | -9.4 |
| 4000 | -12.0 | -11.0 | -7.3 | -9.0 |
| 5039.7 | -10.6 | -7.5 | -7.3 | -5.4 |

From 250 Hz to 1 kHz the candidate falls 2 to 5 dB further than the takes
over those two seconds, and from 3 to 5 kHz 2 to 5 dB less: one decay law
across the strings, linear in log rate over octaves. Against the string
peaks that fall clearly (`fit_realtime_modal.open_ring_peaks`), it sits a
median 1.84 dB/s from pedalD1's 99, which it is fitted on, and 1.71 dB/s from
pedalD2's 100, never fitted; the shipping engine's rates sat 17.5 and
19.8 dB/s from them.

The upright has no pedal recordings and is not scored here.
