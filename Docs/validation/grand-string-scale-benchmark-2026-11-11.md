# Recording benchmark: 2.5.0 against 2.4.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.4.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.62 | 2.81 | 4.84 | 7.08 | 7.70 | 9.24 | 8.42 | 5.56 | 0.21 | 4.40 | 15.17 | 2.65 |
| dev (156) | 8.23 | 3.20 | 4.15 | 6.60 | 6.96 | 8.39 | 7.83 | 5.66 | 0.20 | 4.55 | 12.98 | 2.42 |
| train / bass A0-B2 (84) | 9.79 | 3.38 | 2.74 | 6.01 | 5.62 | 7.03 | 8.02 | 4.67 | 0.19 | 4.00 | 21.81 | 2.42 |
| train / middle C3-B5 (108) | 8.21 | 2.41 | 4.02 | 6.57 | 7.04 | 8.69 | 7.46 | 7.37 | 0.22 | 4.56 | 17.63 | 2.12 |
| train / treble C6-C8 (84) | 7.99 | 2.78 | 8.18 | 8.81 | 10.63 | 12.16 | 10.05 | 4.00 | 0.21 | 4.59 | 5.38 | 3.55 |
| dev / bass A0-B2 (44) | 9.66 | 4.05 | 2.45 | 6.07 | 5.79 | 6.62 | 8.09 | 4.96 | 0.21 | 3.46 | 22.80 | 3.11 |
| dev / middle C3-B5 (68) | 7.78 | 2.35 | 3.42 | 6.16 | 6.04 | 7.81 | 6.90 | 7.77 | 0.17 | 4.37 | 12.55 | 1.79 |
| dev / treble C6-C8 (44) | 7.51 | 3.66 | 7.04 | 7.81 | 9.55 | 11.07 | 8.95 | 2.97 | 0.24 | 5.93 | 3.83 | 2.70 |

## 2.5.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.03 | 1.98 | 5.02 | 7.02 | 7.67 | 9.13 | 8.26 | 5.44 | 0.21 | 4.40 | 14.34 | 2.70 |
| dev (156) | 7.91 | 2.10 | 4.17 | 6.56 | 6.98 | 8.35 | 7.64 | 5.67 | 0.20 | 4.55 | 12.15 | 2.50 |
| train / bass A0-B2 (84) | 8.78 | 2.47 | 2.68 | 5.99 | 5.64 | 6.96 | 7.50 | 4.68 | 0.19 | 3.94 | 21.13 | 2.59 |
| train / middle C3-B5 (108) | 7.60 | 1.22 | 3.99 | 6.50 | 6.96 | 8.63 | 7.40 | 7.36 | 0.22 | 4.52 | 16.01 | 2.15 |
| train / treble C6-C8 (84) | 7.83 | 2.47 | 8.92 | 8.72 | 10.62 | 11.94 | 10.10 | 3.60 | 0.22 | 4.71 | 5.41 | 3.52 |
| dev / bass A0-B2 (44) | 9.50 | 3.04 | 2.42 | 6.01 | 5.77 | 6.56 | 7.60 | 5.06 | 0.21 | 3.41 | 21.64 | 3.34 |
| dev / middle C3-B5 (68) | 7.11 | 1.11 | 3.32 | 6.14 | 6.09 | 7.81 | 6.72 | 7.94 | 0.17 | 4.27 | 11.44 | 1.84 |
| dev / treble C6-C8 (44) | 7.55 | 2.69 | 7.29 | 7.75 | 9.58 | 10.97 | 9.04 | 2.63 | 0.25 | 6.12 | 3.78 | 2.67 |

## Independent-sample regressions (legacy)

Every note and role where 2.5.0 is worse than 2.4.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.4.0 | 2.5.0 |
|---|---|---|---|---|
| 102 | train | decay_db_s | 4.31 | 9.59 |
| 90 | dev | tuning_cents | 1.75 | 3.51 |
| 105 | dev | icc | 0.26 | 0.33 |
| 90 | train | tuning_cents | 1.75 | 3.28 |
| 96 | dev | tuning_cents | 3.01 | 4.21 |
| 96 | dev | partial_db | 5.35 | 6.42 |
| 27 | dev | partial_db | 9.74 | 10.80 |
| 96 | train | tuning_cents | 3.05 | 4.02 |
| 105 | train | icc | 0.24 | 0.27 |
| 75 | dev | ild_db | 10.36 | 10.94 |
| 36 | dev | partial_db | 8.94 | 9.51 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.5939 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 8.2338 | 7.9075 | -0.3262 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 3.2020 | 2.0984 | -1.1036 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 4.1497 | 4.1668 | 0.0171 | 0 | 0 | 1 |
| dev | attack_db | 156 | 6.6026 | 6.5553 | -0.0473 | 0 | 0 | 0 |
| dev | early_db | 156 | 6.9629 | 6.9836 | 0.0206 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 8.3936 | 8.3486 | -0.0450 | 0 | 0 | 0 |
| dev | noise_db | 153 | 7.8250 | 7.6358 | -0.1892 | 0 | 0 | 3 |
| dev | ild_db | 154 | 5.6568 | 5.6669 | 0.0102 | 0 | 0 | 2 |
| dev | icc | 154 | 0.2032 | 0.2041 | 0.0009 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 4.5528 | 4.5464 | -0.0064 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 12.9833 | 12.1541 | -0.8292 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.4169 | 2.5003 | 0.0834 | 0 | 0 | 0 |
| train | partial_db | 276 | 8.6230 | 8.0280 | -0.5950 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.8141 | 1.9799 | -0.8342 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 4.8364 | 5.0224 | 0.1860 | 0 | 0 | 5 |
| train | attack_db | 276 | 7.0817 | 7.0194 | -0.0623 | 0 | 0 | 0 |
| train | early_db | 276 | 7.6993 | 7.6715 | -0.0279 | 0 | 0 | 0 |
| train | sustain_db | 276 | 9.2427 | 9.1274 | -0.1153 | 0 | 0 | 0 |
| train | noise_db | 274 | 8.4243 | 8.2559 | -0.1684 | 0 | 0 | 2 |
| train | ild_db | 270 | 5.5583 | 5.4407 | -0.1177 | 0 | 0 | 6 |
| train | icc | 270 | 0.2108 | 0.2107 | -0.0000 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.3987 | 4.4003 | 0.0017 | 0 | 0 | 0 |
| train | rise_ms | 276 | 15.1738 | 14.3433 | -0.8305 | 0 | 0 | 0 |
| train | level_db | 276 | 2.6476 | 2.7018 | 0.0542 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 102 | train | decay_db_s | 12 | 4.3096 | 9.5917 | 5.2821 |
| 90 | dev | tuning_cents | 4 | 1.7489 | 3.5120 | 1.7631 |
| 105 | dev | icc | 4 | 0.2608 | 0.3286 | 0.0679 |
| 90 | train | tuning_cents | 12 | 1.7521 | 3.2801 | 1.5280 |
| 96 | dev | tuning_cents | 4 | 3.0130 | 4.2053 | 1.1923 |
| 96 | dev | partial_db | 4 | 5.3457 | 6.4246 | 1.0790 |
| 27 | dev | partial_db | 16 | 9.7410 | 10.8000 | 1.0590 |
| 96 | train | tuning_cents | 12 | 3.0475 | 4.0174 | 0.9699 |
| 105 | train | icc | 11 | 0.2396 | 0.2658 | 0.0262 |
| 75 | dev | ild_db | 16 | 10.3565 | 10.9406 | 0.5841 |
| 36 | dev | partial_db | 4 | 8.9382 | 9.5148 | 0.5766 |
| 21 | train | level_db | 12 | 4.8303 | 5.3506 | 0.5204 |
| 21 | dev | level_db | 4 | 5.0306 | 5.5491 | 0.5185 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
