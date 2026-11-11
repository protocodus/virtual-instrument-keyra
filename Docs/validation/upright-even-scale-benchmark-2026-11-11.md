# Recording benchmark: 2.2.0 against 2.1.0

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.1.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 8.69 | 4.09 | 5.11 | 9.21 | 11.24 | 11.37 | 11.81 | 6.66 | 0.25 | 4.43 | 16.04 | 5.03 |
| dev (21) | 8.39 | 4.66 | 5.55 | 8.54 | 10.20 | 10.77 | 11.01 | 5.02 | 0.26 | 4.73 | 12.63 | 2.78 |
| train / bass A0-B2 (30) | 9.25 | 4.90 | 5.13 | 7.76 | 9.62 | 10.28 | 15.22 | 5.94 | 0.22 | 3.08 | 21.93 | 3.85 |
| train / middle C3-B5 (69) | 8.45 | 3.73 | 4.43 | 8.18 | 9.31 | 8.92 | 9.65 | 6.59 | 0.20 | 3.96 | 18.97 | 5.24 |
| train / treble C6-C8 (38) | 8.69 | 4.09 | 6.39 | 12.20 | 16.03 | 16.67 | 13.01 | 7.38 | 0.38 | 6.36 | 6.07 | 5.60 |
| dev / bass A0-B2 (5) | 8.20 | 4.99 | 3.83 | 7.82 | 9.51 | 9.77 | 16.35 | 4.51 | 0.27 | 2.94 | 24.68 | 2.03 |
| dev / middle C3-B5 (11) | 8.56 | 4.29 | 4.91 | 7.45 | 8.71 | 8.90 | 8.77 | 6.28 | 0.21 | 4.26 | 10.60 | 3.44 |
| dev / treble C6-C8 (5) | 8.21 | 5.16 | 8.69 | 11.66 | 14.18 | 15.90 | 11.67 | 2.78 | 0.37 | 7.53 | 5.06 | 2.11 |

## 2.2.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 8.65 | 4.08 | 5.10 | 9.11 | 11.20 | 11.36 | 11.74 | 6.69 | 0.25 | 4.42 | 16.57 | 4.29 |
| dev (21) | 8.46 | 4.63 | 5.55 | 8.61 | 10.25 | 10.76 | 11.42 | 5.10 | 0.26 | 4.73 | 12.95 | 2.85 |
| train / bass A0-B2 (30) | 9.32 | 4.92 | 5.17 | 7.75 | 9.62 | 10.28 | 15.18 | 5.94 | 0.22 | 3.08 | 23.31 | 3.62 |
| train / middle C3-B5 (69) | 8.44 | 3.72 | 4.41 | 8.21 | 9.38 | 8.91 | 9.77 | 6.65 | 0.20 | 3.96 | 19.41 | 4.67 |
| train / treble C6-C8 (38) | 8.48 | 4.09 | 6.38 | 11.82 | 15.74 | 16.67 | 12.59 | 7.39 | 0.39 | 6.33 | 6.09 | 4.12 |
| dev / bass A0-B2 (5) | 8.44 | 4.82 | 3.84 | 7.80 | 9.51 | 9.77 | 16.38 | 4.51 | 0.27 | 2.94 | 24.97 | 1.93 |
| dev / middle C3-B5 (11) | 8.58 | 4.29 | 4.90 | 7.74 | 8.92 | 8.89 | 9.62 | 6.42 | 0.20 | 4.26 | 11.25 | 3.51 |
| dev / treble C6-C8 (5) | 8.21 | 5.18 | 8.69 | 11.32 | 13.92 | 15.85 | 11.41 | 2.79 | 0.37 | 7.55 | 4.67 | 2.31 |

## Independent-sample regressions (legacy)

Every note and role where 2.2.0 is worse than 2.1.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.1.0 | 2.2.0 |
|---|---|---|---|---|
| 66 | train | rise_ms | 1.69 | 8.53 |
| 27 | train | rise_ms | 33.08 | 37.91 |
| 103 | train | level_db | 3.14 | 4.90 |
| 59 | dev | noise_db | 7.52 | 8.85 |
| 24 | train | rise_ms | 32.06 | 34.52 |
| 36 | train | rise_ms | 10.66 | 12.93 |
| 56 | dev | noise_db | 10.08 | 11.10 |
| 62 | train | noise_db | 7.57 | 8.53 |
| 58 | train | level_db | 3.60 | 4.40 |
| 58 | train | noise_db | 8.35 | 9.05 |
| 72 | dev | rise_ms | 10.08 | 11.45 |
| 74 | train | noise_db | 8.00 | 8.66 |
| 72 | dev | noise_db | 7.71 | 8.29 |
| 68 | train | noise_db | 9.74 | 10.30 |
| 58 | train | rise_ms | 40.37 | 41.44 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (11.2654 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 8.3899 | 8.4573 | 0.0674 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 4.6628 | 4.6307 | -0.0321 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 5.5495 | 5.5515 | 0.0021 | 0 | 0 | 0 |
| dev | attack_db | 21 | 8.5424 | 8.6084 | 0.0659 | 0 | 0 | 0 |
| dev | early_db | 21 | 10.2033 | 10.2486 | 0.0454 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 10.7721 | 10.7551 | -0.0170 | 0 | 0 | 0 |
| dev | noise_db | 20 | 11.0123 | 11.4166 | 0.4043 | 0 | 0 | 1 |
| dev | ild_db | 21 | 5.0243 | 5.0983 | 0.0740 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2621 | 0.2588 | -0.0032 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.7261 | 4.7290 | 0.0029 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 12.6310 | 12.9504 | 0.3194 | 0 | 0 | 0 |
| dev | level_db | 21 | 2.7839 | 2.8723 | 0.0884 | 0 | 0 | 0 |
| train | partial_db | 137 | 8.6944 | 8.6457 | -0.0487 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 4.0853 | 4.0827 | -0.0026 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 5.1091 | 5.1041 | -0.0049 | 0 | 0 | 2 |
| train | attack_db | 137 | 9.2052 | 9.1115 | -0.0937 | 0 | 0 | 0 |
| train | early_db | 137 | 11.2434 | 11.1990 | -0.0443 | 0 | 0 | 0 |
| train | sustain_db | 137 | 11.3676 | 11.3650 | -0.0026 | 0 | 0 | 0 |
| train | noise_db | 134 | 11.8088 | 11.7384 | -0.0704 | 0 | 0 | 3 |
| train | ild_db | 135 | 6.6572 | 6.6880 | 0.0308 | 0 | 0 | 2 |
| train | icc | 135 | 0.2522 | 0.2525 | 0.0003 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.4313 | 4.4221 | -0.0092 | 0 | 0 | 0 |
| train | rise_ms | 137 | 16.0376 | 16.5698 | 0.5322 | 0 | 0 | 0 |
| train | level_db | 137 | 5.0332 | 4.2860 | -0.7473 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 66 | train | rise_ms | 5 | 1.6917 | 8.5292 | 6.8375 |
| 27 | train | rise_ms | 5 | 33.0792 | 37.9083 | 4.8292 |
| 103 | train | level_db | 4 | 3.1392 | 4.7928 | 1.6536 |
| 59 | dev | noise_db | 1 | 7.5236 | 8.8453 | 1.3218 |
| 24 | train | rise_ms | 5 | 32.0583 | 34.5167 | 2.4583 |
| 36 | train | rise_ms | 5 | 10.6625 | 12.9292 | 2.2667 |
| 56 | dev | noise_db | 5 | 10.0820 | 11.0989 | 1.0168 |
| 62 | train | noise_db | 5 | 7.5693 | 8.5338 | 0.9645 |
| 58 | train | noise_db | 4 | 8.3485 | 9.0516 | 0.7031 |
| 58 | train | level_db | 4 | 3.5963 | 4.2947 | 0.6984 |
| 72 | dev | rise_ms | 5 | 10.0792 | 11.4542 | 1.3750 |
| 74 | train | noise_db | 5 | 7.9998 | 8.6594 | 0.6596 |
| 72 | dev | noise_db | 5 | 7.7092 | 8.2909 | 0.5817 |
| 68 | train | noise_db | 5 | 9.7389 | 10.3013 | 0.5625 |
| 58 | train | rise_ms | 4 | 40.3698 | 41.4375 | 1.0677 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
