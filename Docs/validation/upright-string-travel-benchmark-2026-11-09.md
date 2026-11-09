# Recording benchmark: 0.4.29 against 0.4.28

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.28

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 5.78 | 0.27 | 2.41 | 5.00 | 4.94 | 5.66 | 7.13 | 1.85 | 0.12 | 2.60 | 7.73 | 1.20 |
| dev (21) | 8.23 | 1.60 | 3.99 | 6.32 | 7.01 | 8.54 | 6.63 | 3.91 | 0.19 | 4.51 | 6.24 | 2.52 |
| train / bass A0-B2 (30) | 6.87 | 0.31 | 2.05 | 5.62 | 5.17 | 5.36 | 10.13 | 1.29 | 0.10 | 2.51 | 8.78 | 0.94 |
| train / middle C3-B5 (69) | 6.58 | 0.23 | 2.55 | 5.19 | 4.80 | 5.40 | 7.34 | 1.84 | 0.09 | 2.14 | 9.38 | 1.39 |
| train / treble C6-C8 (38) | 3.45 | 0.32 | 2.42 | 4.17 | 5.02 | 6.38 | 4.96 | 2.34 | 0.18 | 3.51 | 3.90 | 1.06 |
| dev / bass A0-B2 (5) | 8.80 | 1.29 | 2.08 | 5.81 | 7.47 | 8.96 | 7.09 | 5.18 | 0.20 | 2.09 | 1.42 | 1.41 |
| dev / middle C3-B5 (11) | 8.45 | 0.97 | 3.82 | 6.97 | 6.78 | 7.97 | 6.79 | 3.98 | 0.16 | 4.56 | 10.56 | 2.71 |
| dev / treble C6-C8 (5) | 7.19 | 3.30 | 6.28 | 5.40 | 7.04 | 9.37 | 5.91 | 2.48 | 0.25 | 6.84 | 1.54 | 3.20 |

## 0.4.29

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 5.77 | 0.28 | 2.41 | 4.99 | 4.95 | 5.67 | 7.22 | 1.85 | 0.12 | 2.58 | 7.79 | 1.20 |
| dev (21) | 8.24 | 1.60 | 3.99 | 6.29 | 7.01 | 8.53 | 6.73 | 3.89 | 0.19 | 4.53 | 5.86 | 2.53 |
| train / bass A0-B2 (30) | 6.85 | 0.31 | 2.04 | 5.56 | 5.15 | 5.36 | 10.32 | 1.29 | 0.10 | 2.37 | 8.95 | 0.92 |
| train / middle C3-B5 (69) | 6.59 | 0.24 | 2.56 | 5.19 | 4.82 | 5.40 | 7.43 | 1.84 | 0.09 | 2.15 | 9.56 | 1.40 |
| train / treble C6-C8 (38) | 3.45 | 0.31 | 2.43 | 4.20 | 5.03 | 6.38 | 4.99 | 2.34 | 0.18 | 3.52 | 3.66 | 1.04 |
| dev / bass A0-B2 (5) | 8.81 | 1.28 | 2.08 | 5.69 | 7.45 | 8.95 | 7.08 | 5.20 | 0.20 | 2.13 | 1.07 | 1.44 |
| dev / middle C3-B5 (11) | 8.46 | 0.98 | 3.82 | 6.97 | 6.79 | 7.96 | 6.98 | 3.95 | 0.17 | 4.57 | 10.00 | 2.71 |
| dev / treble C6-C8 (5) | 7.19 | 3.30 | 6.28 | 5.40 | 7.04 | 9.37 | 5.91 | 2.48 | 0.25 | 6.84 | 1.54 | 3.21 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.29 is worse than 0.4.28 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.28 | 0.4.29 |
|---|---|---|---|---|
| 48 | train | rise_ms | 13.81 | 16.68 |
| 52 | train | noise_db | 17.77 | 18.38 |
| 54 | train | rise_ms | 9.70 | 10.76 |
| 76 | train | rise_ms | 6.13 | 7.14 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (15.9383 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 8.2342 | 8.2419 | 0.0077 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 1.6010 | 1.6021 | 0.0011 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 3.9919 | 3.9920 | 0.0001 | 0 | 0 | 0 |
| dev | attack_db | 21 | 6.3204 | 6.2898 | -0.0305 | 0 | 0 | 0 |
| dev | early_db | 21 | 7.0058 | 7.0081 | 0.0023 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 8.5373 | 8.5332 | -0.0042 | 0 | 0 | 0 |
| dev | noise_db | 20 | 6.6313 | 6.7336 | 0.1023 | 0 | 0 | 1 |
| dev | ild_db | 21 | 3.9065 | 3.8946 | -0.0119 | 0 | 0 | 0 |
| dev | icc | 21 | 0.1939 | 0.1945 | 0.0006 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.5146 | 4.5277 | 0.0131 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 6.2361 | 5.8591 | -0.3770 | 0 | 0 | 0 |
| dev | level_db | 21 | 2.5161 | 2.5191 | 0.0031 | 0 | 0 | 0 |
| train | partial_db | 137 | 5.7758 | 5.7734 | -0.0023 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 0.2727 | 0.2777 | 0.0050 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 2.4068 | 2.4102 | 0.0033 | 0 | 0 | 2 |
| train | attack_db | 137 | 5.0003 | 4.9945 | -0.0058 | 0 | 0 | 0 |
| train | early_db | 137 | 4.9414 | 4.9512 | 0.0098 | 0 | 0 | 0 |
| train | sustain_db | 137 | 5.6645 | 5.6656 | 0.0011 | 0 | 0 | 0 |
| train | noise_db | 125 | 7.1327 | 7.2168 | 0.0841 | 0 | 0 | 12 |
| train | ild_db | 135 | 1.8532 | 1.8505 | -0.0027 | 0 | 0 | 2 |
| train | icc | 135 | 0.1177 | 0.1160 | -0.0017 | 0 | 0 | 2 |
| train | envelope_db | 137 | 2.6020 | 2.5787 | -0.0233 | 0 | 0 | 0 |
| train | rise_ms | 137 | 7.7313 | 7.7909 | 0.0596 | 0 | 0 | 0 |
| train | level_db | 137 | 1.2015 | 1.1991 | -0.0024 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 48 | train | rise_ms | 5 | 13.8125 | 16.6833 | 2.8708 |
| 52 | train | noise_db | 5 | 17.7706 | 18.3837 | 0.6131 |
| 54 | train | rise_ms | 5 | 9.7000 | 10.7583 | 1.0583 |
| 76 | train | rise_ms | 5 | 6.1292 | 7.1417 | 1.0125 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
