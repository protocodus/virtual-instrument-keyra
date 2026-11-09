# Recording benchmark: 0.4.29 against 0.4.28

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.28

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.63 | 0.16 | 1.85 | 4.38 | 4.05 | 4.66 | 5.62 | 0.79 | 0.06 | 1.99 | 3.12 | 0.50 |
| dev (156) | 5.34 | 0.91 | 2.10 | 4.78 | 4.44 | 5.33 | 5.27 | 2.24 | 0.10 | 2.68 | 4.28 | 0.96 |
| train / bass A0-B2 (84) | 4.70 | 0.04 | 0.44 | 4.81 | 3.93 | 3.75 | 5.89 | 0.40 | 0.03 | 2.12 | 4.06 | 0.39 |
| train / middle C3-B5 (108) | 4.90 | 0.07 | 1.44 | 3.94 | 3.90 | 3.48 | 5.85 | 0.70 | 0.05 | 0.83 | 2.87 | 0.35 |
| train / treble C6-C8 (84) | 4.20 | 0.41 | 3.92 | 4.52 | 4.35 | 7.10 | 5.11 | 1.35 | 0.10 | 3.35 | 2.51 | 0.79 |
| dev / bass A0-B2 (44) | 5.43 | 1.27 | 1.08 | 5.18 | 4.05 | 3.90 | 5.11 | 1.34 | 0.05 | 2.97 | 5.03 | 0.99 |
| dev / middle C3-B5 (68) | 6.30 | 0.64 | 2.47 | 4.57 | 4.71 | 5.60 | 5.47 | 3.62 | 0.10 | 1.87 | 5.25 | 0.87 |
| dev / treble C6-C8 (44) | 3.76 | 0.95 | 2.55 | 4.71 | 4.42 | 6.36 | 5.13 | 0.94 | 0.15 | 3.64 | 2.03 | 1.07 |

## 0.4.29

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.62 | 0.16 | 1.85 | 4.29 | 4.02 | 4.64 | 5.64 | 0.80 | 0.06 | 1.89 | 3.61 | 0.50 |
| dev (156) | 5.35 | 0.90 | 2.10 | 4.66 | 4.42 | 5.33 | 5.27 | 2.24 | 0.10 | 2.60 | 4.71 | 0.96 |
| train / bass A0-B2 (84) | 4.69 | 0.04 | 0.43 | 4.56 | 3.86 | 3.68 | 6.00 | 0.40 | 0.03 | 1.80 | 4.03 | 0.40 |
| train / middle C3-B5 (108) | 4.90 | 0.07 | 1.44 | 3.89 | 3.90 | 3.48 | 5.81 | 0.70 | 0.05 | 0.82 | 4.13 | 0.35 |
| train / treble C6-C8 (84) | 4.20 | 0.40 | 3.92 | 4.52 | 4.33 | 7.09 | 5.11 | 1.36 | 0.09 | 3.36 | 2.53 | 0.79 |
| dev / bass A0-B2 (44) | 5.48 | 1.27 | 1.08 | 4.82 | 4.02 | 3.88 | 5.18 | 1.35 | 0.05 | 2.66 | 5.38 | 0.99 |
| dev / middle C3-B5 (68) | 6.30 | 0.64 | 2.47 | 4.51 | 4.70 | 5.60 | 5.42 | 3.63 | 0.11 | 1.88 | 6.01 | 0.87 |
| dev / treble C6-C8 (44) | 3.76 | 0.95 | 2.55 | 4.71 | 4.40 | 6.36 | 5.13 | 0.95 | 0.15 | 3.64 | 2.05 | 1.07 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.29 is worse than 0.4.28 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.28 | 0.4.29 |
|---|---|---|---|---|
| 78 | train | rise_ms | 0.86 | 7.34 |
| 78 | dev | rise_ms | 1.21 | 7.07 |
| 21 | dev | attack_db | 4.27 | 5.87 |
| 81 | dev | rise_ms | 0.45 | 3.58 |
| 27 | dev | rise_ms | 7.10 | 8.67 |
| 66 | train | rise_ms | 4.35 | 5.88 |
| 81 | train | rise_ms | 2.22 | 3.61 |
| 60 | train | rise_ms | 2.15 | 3.40 |
| 21 | dev | early_db | 3.43 | 4.05 |
| 21 | dev | sustain_db | 2.93 | 3.53 |
| 66 | dev | rise_ms | 4.30 | 5.43 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (25.8061 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 5.3408 | 5.3548 | 0.0140 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 0.9078 | 0.9047 | -0.0030 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 2.0971 | 2.0978 | 0.0007 | 0 | 0 | 1 |
| dev | attack_db | 156 | 4.7809 | 4.6565 | -0.1244 | 0 | 0 | 0 |
| dev | early_db | 156 | 4.4439 | 4.4222 | -0.0217 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 5.3338 | 5.3263 | -0.0075 | 0 | 0 | 0 |
| dev | noise_db | 153 | 5.2710 | 5.2689 | -0.0021 | 0 | 0 | 3 |
| dev | ild_db | 154 | 2.2422 | 2.2450 | 0.0028 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1020 | 0.1020 | 0.0001 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 2.6812 | 2.5959 | -0.0853 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 4.2810 | 4.7109 | 0.4299 | 0 | 0 | 0 |
| dev | level_db | 156 | 0.9609 | 0.9594 | -0.0015 | 0 | 0 | 0 |
| train | partial_db | 276 | 4.6252 | 4.6224 | -0.0027 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 0.1640 | 0.1627 | -0.0013 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 1.8514 | 1.8520 | 0.0005 | 0 | 0 | 5 |
| train | attack_db | 276 | 4.3796 | 4.2852 | -0.0944 | 0 | 0 | 0 |
| train | early_db | 276 | 4.0492 | 4.0173 | -0.0318 | 0 | 0 | 0 |
| train | sustain_db | 276 | 4.6620 | 4.6394 | -0.0226 | 0 | 0 | 0 |
| train | noise_db | 262 | 5.6247 | 5.6156 | -0.0091 | 0 | 1 | 13 |
| train | ild_db | 270 | 0.7940 | 0.7957 | 0.0017 | 0 | 0 | 6 |
| train | icc | 270 | 0.0558 | 0.0555 | -0.0003 | 0 | 0 | 6 |
| train | envelope_db | 276 | 1.9883 | 1.8906 | -0.0977 | 0 | 0 | 0 |
| train | rise_ms | 276 | 3.1218 | 3.6142 | 0.4925 | 0 | 0 | 0 |
| train | level_db | 276 | 0.4962 | 0.5013 | 0.0051 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 78 | train | rise_ms | 12 | 0.8628 | 7.3420 | 6.4792 |
| 78 | dev | rise_ms | 4 | 1.2083 | 7.0677 | 5.8594 |
| 21 | dev | attack_db | 4 | 4.2739 | 5.8708 | 1.5969 |
| 81 | dev | rise_ms | 4 | 0.4531 | 3.5833 | 3.1302 |
| 27 | dev | rise_ms | 16 | 7.0977 | 8.6667 | 1.5690 |
| 66 | train | rise_ms | 12 | 4.3542 | 5.8767 | 1.5226 |
| 81 | train | rise_ms | 12 | 2.2153 | 3.6111 | 1.3958 |
| 60 | train | rise_ms | 12 | 2.1476 | 3.3993 | 1.2517 |
| 21 | dev | early_db | 4 | 3.4316 | 4.0513 | 0.6197 |
| 21 | dev | sustain_db | 4 | 2.9282 | 3.5255 | 0.5973 |
| 66 | dev | rise_ms | 4 | 4.2969 | 5.4271 | 1.1302 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| A1v1 | 33 | train | noise_db | gained | - | 11.6854 |
