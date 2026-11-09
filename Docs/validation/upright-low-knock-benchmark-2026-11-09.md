# Recording benchmark: 0.4.28 against 0.4.27

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.27

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 5.77 | 0.27 | 2.41 | 5.15 | 5.26 | 5.81 | 7.39 | 2.13 | 0.13 | 2.61 | 7.75 | 1.20 |
| dev (21) | 8.23 | 1.60 | 3.99 | 6.48 | 7.25 | 8.64 | 6.85 | 4.19 | 0.20 | 4.51 | 6.19 | 2.52 |
| train / bass A0-B2 (30) | 6.87 | 0.31 | 2.05 | 5.62 | 5.17 | 5.36 | 10.13 | 1.29 | 0.10 | 2.51 | 8.78 | 0.94 |
| train / middle C3-B5 (69) | 6.58 | 0.23 | 2.55 | 5.34 | 4.94 | 5.44 | 7.56 | 1.94 | 0.10 | 2.14 | 9.46 | 1.39 |
| train / treble C6-C8 (38) | 3.44 | 0.32 | 2.42 | 4.42 | 5.91 | 6.82 | 5.43 | 3.22 | 0.22 | 3.55 | 3.83 | 1.05 |
| dev / bass A0-B2 (5) | 8.80 | 1.29 | 2.08 | 5.81 | 7.47 | 8.96 | 7.09 | 5.18 | 0.20 | 2.09 | 1.42 | 1.41 |
| dev / middle C3-B5 (11) | 8.45 | 0.97 | 3.82 | 7.07 | 6.93 | 8.01 | 6.92 | 4.21 | 0.17 | 4.56 | 10.55 | 2.71 |
| dev / treble C6-C8 (5) | 7.17 | 3.30 | 6.28 | 5.84 | 7.74 | 9.70 | 6.50 | 3.17 | 0.28 | 6.83 | 1.38 | 3.21 |

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

## Independent-sample regressions (legacy)

Every note and role where 0.4.28 is worse than 0.4.27 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.27 | 0.4.28 |
|---|---|---|---|---|
| 59 | dev | icc | 0.14 | 0.17 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (15.9394 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 8.2307 | 8.2342 | 0.0035 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 1.6010 | 1.6010 | 0.0000 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 3.9909 | 3.9919 | 0.0010 | 0 | 0 | 0 |
| dev | attack_db | 21 | 6.4796 | 6.3204 | -0.1593 | 0 | 0 | 0 |
| dev | early_db | 21 | 7.2519 | 7.0058 | -0.2461 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 8.6400 | 8.5373 | -0.1027 | 0 | 0 | 0 |
| dev | noise_db | 20 | 6.8499 | 6.6313 | -0.2186 | 0 | 0 | 1 |
| dev | ild_db | 21 | 4.1935 | 3.9065 | -0.2871 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2022 | 0.1939 | -0.0084 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.5130 | 4.5146 | 0.0016 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 6.1905 | 6.2361 | 0.0456 | 0 | 0 | 0 |
| dev | level_db | 21 | 2.5189 | 2.5159 | -0.0029 | 0 | 0 | 0 |
| train | partial_db | 137 | 5.7727 | 5.7758 | 0.0030 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 0.2727 | 0.2727 | -0.0000 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 2.4051 | 2.4068 | 0.0017 | 0 | 0 | 2 |
| train | attack_db | 137 | 5.1472 | 5.0003 | -0.1469 | 0 | 0 | 0 |
| train | early_db | 137 | 5.2572 | 4.9414 | -0.3158 | 0 | 0 | 0 |
| train | sustain_db | 137 | 5.8051 | 5.6645 | -0.1406 | 0 | 0 | 0 |
| train | noise_db | 125 | 7.3865 | 7.1327 | -0.2538 | 0 | 0 | 12 |
| train | ild_db | 135 | 2.1343 | 1.8532 | -0.2810 | 0 | 0 | 2 |
| train | icc | 135 | 0.1323 | 0.1177 | -0.0146 | 0 | 0 | 2 |
| train | envelope_db | 137 | 2.6117 | 2.6020 | -0.0097 | 0 | 0 | 0 |
| train | rise_ms | 137 | 7.7508 | 7.7313 | -0.0195 | 0 | 0 | 0 |
| train | level_db | 137 | 1.1970 | 1.2015 | 0.0045 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 59 | dev | icc | 1 | 0.1424 | 0.1700 | 0.0276 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
