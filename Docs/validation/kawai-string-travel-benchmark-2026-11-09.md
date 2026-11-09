# Recording benchmark: 0.4.29 against 0.4.28

Every train and dev note of `Tools/corpus/split-vcsl-kawai-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.28

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (104) | 8.31 | 0.55 | 3.94 | 6.44 | 7.51 | 7.86 | 8.28 | 1.76 | 0.10 | 3.51 | 7.34 | 1.93 |
| dev (23) | 9.64 | 2.39 | 5.04 | 6.95 | 8.71 | 8.40 | 8.94 | 5.59 | 0.20 | 5.07 | 5.46 | 4.21 |
| train / bass A0-B2 (27) | 9.92 | 0.44 | 1.86 | 6.51 | 7.07 | 7.44 | 9.42 | 1.43 | 0.07 | 2.89 | 14.97 | 1.50 |
| train / middle C3-B5 (52) | 8.75 | 0.51 | 4.21 | 6.38 | 7.44 | 8.52 | 8.24 | 2.13 | 0.12 | 3.79 | 5.47 | 1.96 |
| train / treble C6-C8 (25) | 5.29 | 0.76 | 6.80 | 6.47 | 8.17 | 6.40 | 7.36 | 1.02 | 0.07 | 3.61 | 2.99 | 2.34 |
| dev / bass A0-B2 (8) | 10.30 | 2.28 | 2.59 | 6.08 | 6.14 | 8.53 | 9.56 | 3.24 | 0.15 | 3.83 | 9.17 | 1.73 |
| dev / middle C3-B5 (12) | 9.15 | 2.14 | 6.01 | 7.17 | 9.30 | 8.89 | 8.49 | 7.76 | 0.16 | 5.73 | 3.72 | 4.72 |
| dev / treble C6-C8 (3) | 9.93 | 4.30 | 8.97 | 8.37 | 13.19 | 4.90 | 8.96 | 3.09 | 0.66 | 5.74 | 2.49 | 8.77 |

## 0.4.29

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (104) | 8.32 | 0.54 | 3.94 | 6.49 | 7.54 | 7.89 | 8.37 | 1.76 | 0.10 | 3.51 | 7.35 | 1.93 |
| dev (23) | 9.63 | 2.41 | 5.03 | 6.90 | 8.72 | 8.39 | 9.02 | 5.60 | 0.20 | 5.08 | 4.83 | 4.23 |
| train / bass A0-B2 (27) | 9.91 | 0.41 | 1.84 | 6.77 | 7.14 | 7.54 | 9.59 | 1.42 | 0.07 | 2.91 | 14.96 | 1.49 |
| train / middle C3-B5 (52) | 8.78 | 0.52 | 4.20 | 6.35 | 7.45 | 8.53 | 8.28 | 2.12 | 0.12 | 3.78 | 5.54 | 1.96 |
| train / treble C6-C8 (25) | 5.30 | 0.78 | 6.81 | 6.48 | 8.20 | 6.40 | 7.40 | 1.04 | 0.07 | 3.61 | 2.89 | 2.34 |
| dev / bass A0-B2 (8) | 10.29 | 2.33 | 2.59 | 5.93 | 6.10 | 8.52 | 9.63 | 3.25 | 0.15 | 3.85 | 8.44 | 1.76 |
| dev / middle C3-B5 (12) | 9.15 | 2.15 | 5.99 | 7.18 | 9.36 | 8.89 | 8.59 | 7.77 | 0.16 | 5.72 | 3.00 | 4.74 |
| dev / treble C6-C8 (3) | 9.93 | 4.30 | 8.97 | 8.37 | 13.19 | 4.90 | 8.96 | 3.09 | 0.66 | 5.74 | 2.49 | 8.79 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.29 is worse than 0.4.28 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.28 | 0.4.29 |
|---|---|---|---|---|
| 21 | train | attack_db | 7.81 | 9.77 |
| 68 | train | rise_ms | 7.84 | 10.11 |
| 80 | train | rise_ms | 2.42 | 4.32 |
| 24 | train | attack_db | 6.53 | 7.45 |
| 82 | dev | rise_ms | 0.78 | 2.38 |
| 21 | train | early_db | 7.78 | 8.47 |
| 36 | train | noise_db | 4.34 | 4.85 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.7486 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 22 | 9.6377 | 9.6322 | -0.0054 | 0 | 0 | 1 |
| dev | tuning_cents | 22 | 2.3894 | 2.4076 | 0.0182 | 0 | 0 | 1 |
| dev | decay_db_s | 22 | 5.0376 | 5.0265 | -0.0111 | 0 | 0 | 1 |
| dev | attack_db | 23 | 6.9463 | 6.8985 | -0.0478 | 0 | 0 | 0 |
| dev | early_db | 23 | 8.7093 | 8.7226 | 0.0134 | 0 | 0 | 0 |
| dev | sustain_db | 22 | 8.3951 | 8.3948 | -0.0003 | 0 | 0 | 1 |
| dev | noise_db | 22 | 8.9414 | 9.0176 | 0.0762 | 0 | 0 | 1 |
| dev | ild_db | 21 | 5.5916 | 5.5988 | 0.0072 | 0 | 0 | 2 |
| dev | icc | 21 | 0.2046 | 0.2038 | -0.0009 | 0 | 0 | 2 |
| dev | envelope_db | 23 | 5.0729 | 5.0762 | 0.0034 | 0 | 0 | 0 |
| dev | rise_ms | 23 | 5.4561 | 4.8261 | -0.6300 | 0 | 0 | 0 |
| dev | level_db | 23 | 4.2061 | 4.2203 | 0.0142 | 0 | 0 | 0 |
| train | partial_db | 100 | 8.3053 | 8.3181 | 0.0128 | 0 | 0 | 4 |
| train | tuning_cents | 100 | 0.5471 | 0.5446 | -0.0025 | 0 | 0 | 4 |
| train | decay_db_s | 93 | 3.9447 | 3.9366 | -0.0081 | 0 | 0 | 11 |
| train | attack_db | 104 | 6.4390 | 6.4926 | 0.0536 | 0 | 0 | 0 |
| train | early_db | 102 | 7.5052 | 7.5391 | 0.0339 | 0 | 0 | 2 |
| train | sustain_db | 95 | 7.8568 | 7.8914 | 0.0345 | 0 | 0 | 9 |
| train | noise_db | 94 | 8.3023 | 8.3508 | 0.0485 | 1 | 1 | 8 |
| train | ild_db | 90 | 1.7579 | 1.7567 | -0.0012 | 0 | 0 | 14 |
| train | icc | 90 | 0.0965 | 0.0968 | 0.0003 | 0 | 0 | 14 |
| train | envelope_db | 104 | 3.5130 | 3.5147 | 0.0017 | 0 | 0 | 0 |
| train | rise_ms | 104 | 7.3415 | 7.3509 | 0.0094 | 0 | 0 | 0 |
| train | level_db | 104 | 1.9307 | 1.9297 | -0.0009 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 21 | train | attack_db | 3 | 7.8096 | 9.7679 | 1.9584 |
| 68 | train | rise_ms | 4 | 7.8425 | 10.1082 | 2.2656 |
| 80 | train | rise_ms | 4 | 2.4212 | 4.3244 | 1.9032 |
| 24 | train | attack_db | 4 | 6.5276 | 7.4537 | 0.9261 |
| 82 | dev | rise_ms | 3 | 0.7801 | 2.3798 | 1.5997 |
| 21 | train | early_db | 3 | 7.7842 | 8.4650 | 0.6808 |
| 36 | train | noise_db | 3 | 4.3394 | 4.8476 | 0.5083 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| n30v1 | 30 | train | noise_db | gained | - | 9.7809 |
| n52v2 | 52 | train | noise_db | lost | 6.4125 | - |
