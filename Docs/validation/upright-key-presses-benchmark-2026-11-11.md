# Recording benchmark: 2.4.0 against 2.3.0

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.3.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 8.66 | 4.02 | 5.12 | 8.89 | 10.86 | 11.32 | 11.41 | 6.68 | 0.25 | 4.42 | 16.57 | 4.29 |
| dev (21) | 8.57 | 4.55 | 5.72 | 8.52 | 10.17 | 10.76 | 11.23 | 5.10 | 0.26 | 4.73 | 12.84 | 2.85 |
| train / bass A0-B2 (30) | 9.30 | 4.94 | 5.11 | 7.75 | 9.62 | 10.28 | 15.25 | 5.94 | 0.22 | 3.08 | 23.31 | 3.62 |
| train / middle C3-B5 (69) | 8.46 | 3.64 | 4.49 | 8.19 | 9.38 | 8.92 | 9.77 | 6.65 | 0.20 | 3.96 | 19.41 | 4.67 |
| train / treble C6-C8 (38) | 8.50 | 3.99 | 6.33 | 11.04 | 14.52 | 16.50 | 11.38 | 7.38 | 0.39 | 6.32 | 6.08 | 4.12 |
| dev / bass A0-B2 (5) | 8.73 | 4.72 | 3.83 | 7.81 | 9.51 | 9.77 | 16.36 | 4.51 | 0.27 | 2.94 | 24.97 | 1.93 |
| dev / middle C3-B5 (11) | 8.66 | 4.19 | 5.18 | 7.74 | 8.91 | 8.89 | 9.53 | 6.42 | 0.20 | 4.26 | 11.25 | 3.51 |
| dev / treble C6-C8 (5) | 8.22 | 5.18 | 8.81 | 10.95 | 13.61 | 15.85 | 10.86 | 2.78 | 0.37 | 7.55 | 4.22 | 2.31 |

## 2.4.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 8.63 | 4.25 | 5.05 | 7.58 | 9.70 | 10.88 | 10.26 | 6.53 | 0.25 | 4.17 | 15.50 | 4.37 |
| dev (21) | 9.57 | 4.32 | 5.51 | 7.50 | 9.12 | 10.56 | 9.80 | 5.24 | 0.26 | 4.53 | 13.10 | 3.02 |
| train / bass A0-B2 (30) | 10.53 | 5.09 | 5.28 | 7.87 | 9.65 | 10.30 | 15.63 | 6.00 | 0.22 | 3.09 | 20.61 | 3.63 |
| train / middle C3-B5 (69) | 8.55 | 3.61 | 4.53 | 7.44 | 8.59 | 8.92 | 8.90 | 6.50 | 0.20 | 3.97 | 19.04 | 4.73 |
| train / treble C6-C8 (38) | 7.28 | 4.75 | 5.88 | 7.61 | 11.74 | 14.90 | 8.40 | 7.04 | 0.38 | 5.39 | 5.06 | 4.29 |
| dev / bass A0-B2 (5) | 9.83 | 5.12 | 3.91 | 8.26 | 9.60 | 9.90 | 16.54 | 4.61 | 0.26 | 2.87 | 24.70 | 1.95 |
| dev / middle C3-B5 (11) | 8.46 | 3.97 | 5.01 | 6.80 | 7.67 | 8.76 | 7.69 | 6.65 | 0.21 | 4.22 | 11.22 | 3.48 |
| dev / treble C6-C8 (5) | 11.76 | 4.29 | 8.20 | 8.28 | 11.82 | 15.17 | 9.05 | 2.75 | 0.37 | 6.90 | 5.61 | 3.07 |

## Independent-sample regressions (legacy)

Every note and role where 2.4.0 is worse than 2.3.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.3.0 | 2.4.0 |
|---|---|---|---|---|
| 27 | train | rise_ms | 37.92 | 50.22 |
| 100 | train | decay_db_s | 3.56 | 11.56 |
| 88 | dev | partial_db | 8.22 | 11.76 |
| 92 | train | tuning_cents | 3.17 | 6.55 |
| 24 | train | partial_db | 10.39 | 12.44 |
| 78 | train | noise_db | 11.14 | 13.03 |
| 36 | train | partial_db | 9.37 | 11.23 |
| 96 | train | level_db | 4.07 | 5.86 |
| 96 | train | partial_db | 8.74 | 10.44 |
| 42 | train | noise_db | 11.54 | 13.22 |
| 42 | train | partial_db | 7.30 | 8.93 |
| 96 | train | tuning_cents | 3.44 | 5.03 |
| 90 | train | tuning_cents | 5.36 | 6.53 |
| 52 | train | partial_db | 8.05 | 9.19 |
| 54 | train | noise_db | 9.70 | 10.81 |
| 39 | dev | partial_db | 8.73 | 9.83 |
| 45 | train | partial_db | 9.18 | 10.23 |
| 94 | train | ild_db | 6.76 | 7.77 |
| 33 | train | partial_db | 10.31 | 11.26 |
| 66 | train | icc | 0.21 | 0.25 |
| 68 | train | partial_db | 8.29 | 9.14 |
| 84 | train | level_db | 4.35 | 5.16 |
| 33 | train | rise_ms | 9.97 | 11.55 |
| 86 | train | tuning_cents | 3.95 | 4.73 |
| 36 | train | noise_db | 10.72 | 11.48 |
| 88 | dev | level_db | 2.31 | 3.07 |
| 88 | dev | rise_ms | 4.22 | 5.61 |
| 82 | train | level_db | 3.90 | 4.57 |
| 50 | train | partial_db | 9.66 | 10.31 |
| 103 | train | envelope_db | 4.65 | 5.30 |
| 86 | train | level_db | 2.82 | 3.47 |
| 90 | train | icc | 0.17 | 0.20 |
| 82 | train | partial_db | 4.09 | 4.67 |
| 78 | train | rise_ms | 14.21 | 15.35 |
| 94 | train | level_db | 4.15 | 4.71 |
| 24 | train | attack_db | 6.66 | 7.21 |
| 78 | train | level_db | 5.91 | 6.46 |
| 48 | train | rise_ms | 22.22 | 23.29 |
| 90 | train | rise_ms | 5.94 | 7.00 |
| 66 | train | tuning_cents | 3.11 | 3.63 |
| 62 | train | partial_db | 9.10 | 9.60 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (11.4704 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 8.5721 | 9.5730 | 1.0009 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 4.5539 | 4.3201 | -0.2338 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 5.7242 | 5.5072 | -0.2170 | 0 | 0 | 0 |
| dev | attack_db | 21 | 8.5201 | 7.4999 | -1.0202 | 0 | 0 | 0 |
| dev | early_db | 21 | 10.1736 | 9.1185 | -1.0550 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 10.7551 | 10.5552 | -0.1999 | 0 | 0 | 0 |
| dev | noise_db | 20 | 11.2311 | 9.7969 | -1.4342 | 0 | 0 | 1 |
| dev | ild_db | 21 | 5.0982 | 5.2364 | 0.1382 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2588 | 0.2578 | -0.0010 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.7289 | 4.5343 | -0.1946 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 12.8442 | 13.0952 | 0.2510 | 0 | 0 | 0 |
| dev | level_db | 21 | 2.8481 | 3.0362 | 0.1881 | 0 | 0 | 0 |
| train | partial_db | 137 | 8.6553 | 8.6315 | -0.0238 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 4.0195 | 4.2521 | 0.2326 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 5.1182 | 5.0543 | -0.0639 | 0 | 0 | 2 |
| train | attack_db | 137 | 8.8863 | 7.5847 | -1.3015 | 0 | 0 | 0 |
| train | early_db | 137 | 10.8594 | 9.6957 | -1.1637 | 0 | 0 | 0 |
| train | sustain_db | 137 | 11.3197 | 10.8847 | -0.4351 | 0 | 0 | 0 |
| train | noise_db | 134 | 11.4122 | 10.2256 | -1.1866 | 0 | 1 | 2 |
| train | ild_db | 135 | 6.6850 | 6.5344 | -0.1506 | 0 | 0 | 2 |
| train | icc | 135 | 0.2523 | 0.2521 | -0.0002 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.4192 | 4.1720 | -0.2473 | 0 | 0 | 0 |
| train | rise_ms | 137 | 16.5690 | 15.5038 | -1.0652 | 0 | 0 | 0 |
| train | level_db | 137 | 4.2874 | 4.3641 | 0.0767 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 27 | train | rise_ms | 5 | 37.9208 | 50.2208 | 12.3000 |
| 100 | train | decay_db_s | 3 | 3.5645 | 11.5603 | 7.9958 |
| 88 | dev | partial_db | 5 | 8.2248 | 11.7627 | 3.5379 |
| 92 | train | tuning_cents | 5 | 3.1742 | 6.5532 | 3.3789 |
| 24 | train | partial_db | 5 | 10.3890 | 12.4438 | 2.0548 |
| 96 | train | level_db | 5 | 4.0680 | 5.9626 | 1.8946 |
| 78 | train | noise_db | 5 | 11.1400 | 13.0253 | 1.8853 |
| 36 | train | partial_db | 5 | 9.3744 | 11.2261 | 1.8517 |
| 96 | train | partial_db | 5 | 8.7364 | 10.4448 | 1.7084 |
| 42 | train | noise_db | 5 | 11.5431 | 13.2177 | 1.6746 |
| 42 | train | partial_db | 5 | 7.3044 | 8.9329 | 1.6285 |
| 96 | train | tuning_cents | 5 | 3.4419 | 5.0268 | 1.5849 |
| 90 | train | tuning_cents | 5 | 5.3552 | 6.5293 | 1.1741 |
| 52 | train | partial_db | 5 | 8.0518 | 9.1884 | 1.1366 |
| 54 | train | noise_db | 5 | 9.7036 | 10.8051 | 1.1015 |
| 39 | dev | partial_db | 5 | 8.7325 | 9.8306 | 1.0980 |
| 45 | train | partial_db | 5 | 9.1843 | 10.2259 | 1.0416 |
| 94 | train | ild_db | 5 | 6.7617 | 7.7687 | 1.0070 |
| 33 | train | partial_db | 5 | 10.3079 | 11.2649 | 0.9570 |
| 66 | train | icc | 5 | 0.2106 | 0.2452 | 0.0346 |
| 68 | train | partial_db | 5 | 8.2887 | 9.1438 | 0.8552 |
| 33 | train | rise_ms | 5 | 9.9750 | 11.5500 | 1.5750 |
| 86 | train | tuning_cents | 5 | 3.9493 | 4.7329 | 0.7836 |
| 84 | train | level_db | 5 | 4.3519 | 5.0978 | 0.7459 |
| 88 | dev | level_db | 5 | 2.3072 | 3.0468 | 0.7396 |
| 88 | dev | rise_ms | 5 | 4.2208 | 5.6083 | 1.3875 |
| 94 | train | level_db | 5 | 4.1498 | 4.8203 | 0.6705 |
| 50 | train | partial_db | 5 | 9.6582 | 10.3114 | 0.6532 |
| 103 | train | envelope_db | 4 | 4.6546 | 5.3030 | 0.6484 |
| 90 | train | icc | 5 | 0.1749 | 0.2004 | 0.0255 |
| 86 | train | level_db | 5 | 2.8240 | 3.4389 | 0.6149 |
| 82 | train | level_db | 5 | 3.9032 | 4.5074 | 0.6042 |
| 82 | train | partial_db | 5 | 4.0868 | 4.6736 | 0.5868 |
| 78 | train | rise_ms | 5 | 14.2125 | 15.3500 | 1.1375 |
| 24 | train | attack_db | 5 | 6.6630 | 7.2133 | 0.5503 |
| 48 | train | rise_ms | 5 | 22.2208 | 23.2875 | 1.0667 |
| 90 | train | rise_ms | 5 | 5.9417 | 7.0042 | 1.0625 |
| 66 | train | tuning_cents | 5 | 3.1081 | 3.6290 | 0.5209 |
| 62 | train | partial_db | 5 | 9.0993 | 9.6029 | 0.5036 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| n36v1r1 | 36 | train | noise_db | gained | - | 14.4647 |
