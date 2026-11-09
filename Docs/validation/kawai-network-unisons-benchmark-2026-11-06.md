# Recording benchmark: 0.4.26 against 0.4.25

Every train and dev note of `Tools/corpus/split-vcsl-kawai-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.25

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (104) | 8.39 | 0.52 | 3.84 | 8.21 | 8.84 | 8.47 | 8.33 | 1.77 | 0.10 | 3.55 | 7.46 | 1.89 |
| dev (23) | 10.12 | 2.91 | 5.47 | 8.70 | 10.15 | 9.64 | 9.06 | 5.28 | 0.21 | 5.39 | 6.08 | 4.36 |
| train / bass A0-B2 (27) | 9.97 | 0.43 | 1.78 | 9.07 | 9.53 | 8.72 | 9.44 | 1.46 | 0.07 | 2.89 | 14.96 | 1.37 |
| train / middle C3-B5 (52) | 8.80 | 0.45 | 3.96 | 7.79 | 8.34 | 8.55 | 8.19 | 2.13 | 0.12 | 3.79 | 5.71 | 1.99 |
| train / treble C6-C8 (25) | 5.47 | 0.82 | 7.16 | 8.13 | 9.16 | 7.78 | 7.63 | 1.02 | 0.07 | 3.77 | 2.99 | 2.24 |
| dev / bass A0-B2 (8) | 10.69 | 3.88 | 2.71 | 8.89 | 8.45 | 9.32 | 9.58 | 3.13 | 0.15 | 3.50 | 9.08 | 1.90 |
| dev / middle C3-B5 (12) | 9.56 | 2.23 | 5.58 | 8.09 | 9.98 | 10.27 | 8.18 | 7.14 | 0.17 | 6.64 | 4.88 | 4.88 |
| dev / treble C6-C8 (3) | 11.19 | 3.14 | 15.80 | 10.62 | 15.31 | 7.18 | 10.87 | 3.62 | 0.69 | 5.45 | 2.87 | 8.78 |

## 0.4.26

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (104) | 8.37 | 0.52 | 3.84 | 8.19 | 8.89 | 8.47 | 8.33 | 1.78 | 0.10 | 3.55 | 7.46 | 1.94 |
| dev (23) | 9.89 | 2.30 | 5.05 | 8.62 | 10.15 | 9.46 | 9.05 | 5.61 | 0.21 | 5.12 | 5.60 | 4.21 |
| train / bass A0-B2 (27) | 9.95 | 0.42 | 1.80 | 9.08 | 9.53 | 8.72 | 9.43 | 1.46 | 0.07 | 2.89 | 14.96 | 1.50 |
| train / middle C3-B5 (52) | 8.80 | 0.46 | 3.95 | 7.78 | 8.39 | 8.56 | 8.22 | 2.14 | 0.12 | 3.79 | 5.73 | 1.95 |
| train / treble C6-C8 (25) | 5.47 | 0.81 | 7.15 | 8.08 | 9.26 | 7.78 | 7.60 | 1.02 | 0.07 | 3.76 | 2.98 | 2.37 |
| dev / bass A0-B2 (8) | 10.45 | 2.09 | 2.58 | 8.64 | 8.53 | 10.04 | 9.56 | 3.27 | 0.15 | 3.83 | 9.17 | 1.73 |
| dev / middle C3-B5 (12) | 9.19 | 2.03 | 6.00 | 8.13 | 10.08 | 9.24 | 8.28 | 7.77 | 0.17 | 5.74 | 4.00 | 4.72 |
| dev / treble C6-C8 (3) | 11.87 | 4.82 | 9.20 | 10.49 | 14.73 | 8.40 | 10.46 | 3.09 | 0.66 | 6.08 | 2.48 | 8.79 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.26 is worse than 0.4.25 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.25 | 0.4.26 |
|---|---|---|---|---|
| 83 | dev | envelope_db | 3.62 | 7.38 |
| 82 | dev | ild_db | 4.41 | 7.21 |
| 82 | dev | early_db | 8.67 | 10.64 |
| 39 | dev | envelope_db | 2.66 | 4.41 |
| 102 | dev | envelope_db | 6.27 | 8.01 |
| 102 | dev | tuning_cents | 3.14 | 4.82 |
| 83 | dev | sustain_db | 12.70 | 14.34 |
| 27 | dev | rise_ms | 6.33 | 9.44 |
| 83 | dev | level_db | 11.67 | 12.93 |
| 82 | dev | partial_db | 5.72 | 6.94 |
| 102 | dev | sustain_db | 7.18 | 8.40 |
| 82 | dev | sustain_db | 10.25 | 11.29 |
| 82 | dev | noise_db | 7.07 | 8.09 |
| 82 | dev | envelope_db | 6.28 | 7.25 |
| 84 | train | early_db | 6.41 | 7.37 |
| 39 | dev | sustain_db | 9.67 | 10.57 |
| 82 | dev | decay_db_s | 3.55 | 5.23 |
| 102 | dev | partial_db | 11.19 | 11.87 |
| 84 | train | level_db | 2.13 | 2.80 |
| 84 | train | noise_db | 5.43 | 6.01 |
| 27 | dev | sustain_db | 8.97 | 9.50 |
| 39 | dev | level_db | 1.39 | 1.89 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (13.6146 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 22 | 10.1194 | 9.8920 | -0.2274 | 0 | 0 | 1 |
| dev | tuning_cents | 22 | 2.9132 | 2.3044 | -0.6089 | 0 | 0 | 1 |
| dev | decay_db_s | 22 | 5.4696 | 5.0496 | -0.4200 | 0 | 0 | 1 |
| dev | attack_db | 23 | 8.6974 | 8.6162 | -0.0813 | 0 | 0 | 0 |
| dev | early_db | 23 | 10.1464 | 10.1490 | 0.0026 | 0 | 0 | 0 |
| dev | sustain_db | 22 | 9.6410 | 9.4559 | -0.1852 | 0 | 0 | 1 |
| dev | noise_db | 22 | 9.0553 | 9.0454 | -0.0100 | 0 | 0 | 1 |
| dev | ild_db | 21 | 5.2766 | 5.6064 | 0.3298 | 0 | 0 | 2 |
| dev | icc | 21 | 0.2127 | 0.2074 | -0.0053 | 0 | 0 | 2 |
| dev | envelope_db | 23 | 5.3911 | 5.1181 | -0.2730 | 0 | 0 | 0 |
| dev | rise_ms | 23 | 6.0829 | 5.6005 | -0.4824 | 0 | 0 | 0 |
| dev | level_db | 23 | 4.3552 | 3.9424 | -0.4128 | 0 | 0 | 0 |
| train | partial_db | 100 | 8.3869 | 8.3733 | -0.0136 | 0 | 0 | 4 |
| train | tuning_cents | 100 | 0.5244 | 0.5235 | -0.0009 | 0 | 0 | 4 |
| train | decay_db_s | 93 | 3.8445 | 3.8433 | -0.0011 | 0 | 0 | 11 |
| train | attack_db | 104 | 8.2065 | 8.1894 | -0.0171 | 0 | 0 | 0 |
| train | early_db | 102 | 8.8429 | 8.8906 | 0.0477 | 0 | 0 | 2 |
| train | sustain_db | 94 | 8.4701 | 8.4749 | 0.0047 | 0 | 0 | 10 |
| train | noise_db | 95 | 8.3289 | 8.3349 | 0.0060 | 0 | 0 | 9 |
| train | ild_db | 90 | 1.7708 | 1.7761 | 0.0053 | 0 | 0 | 14 |
| train | icc | 90 | 0.0965 | 0.0969 | 0.0003 | 0 | 0 | 14 |
| train | envelope_db | 104 | 3.5530 | 3.5509 | -0.0021 | 0 | 0 | 0 |
| train | rise_ms | 104 | 7.4573 | 7.4643 | 0.0070 | 0 | 0 | 0 |
| train | level_db | 104 | 1.8880 | 2.2202 | 0.3323 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 83 | dev | envelope_db | 1 | 3.6178 | 7.3784 | 3.7606 |
| 82 | dev | ild_db | 2 | 4.4053 | 7.2072 | 2.8019 |
| 82 | dev | early_db | 3 | 8.6708 | 10.6416 | 1.9708 |
| 39 | dev | envelope_db | 4 | 2.6617 | 4.4096 | 1.7479 |
| 102 | dev | envelope_db | 2 | 6.2666 | 8.0108 | 1.7442 |
| 102 | dev | tuning_cents | 2 | 3.1386 | 4.8241 | 1.6855 |
| 83 | dev | sustain_db | 1 | 12.7008 | 14.3357 | 1.6349 |
| 27 | dev | rise_ms | 4 | 6.3281 | 9.4375 | 3.1094 |
| 93 | train | level_db | 3 | 0.1968 | 1.4425 | 1.2458 |
| 82 | dev | partial_db | 3 | 5.7232 | 6.9400 | 1.2168 |
| 102 | dev | sustain_db | 2 | 7.1845 | 8.3960 | 1.2115 |
| 82 | dev | sustain_db | 3 | 10.2497 | 11.2907 | 1.0410 |
| 56 | train | level_db | 4 | 3.8538 | 4.8862 | 1.0324 |
| 82 | dev | noise_db | 3 | 7.0658 | 8.0900 | 1.0241 |
| 87 | train | level_db | 3 | 0.6569 | 1.6715 | 1.0146 |
| 36 | train | level_db | 4 | 1.1261 | 2.1194 | 0.9933 |
| 82 | dev | envelope_db | 3 | 6.2802 | 7.2453 | 0.9651 |
| 84 | train | early_db | 4 | 6.4081 | 7.3729 | 0.9648 |
| 33 | train | level_db | 4 | 0.4402 | 1.3920 | 0.9518 |
| 48 | train | level_db | 4 | 0.1687 | 1.1103 | 0.9417 |
| 108 | train | level_db | 4 | 5.8258 | 6.7594 | 0.9336 |
| 39 | dev | sustain_db | 4 | 9.6696 | 10.5709 | 0.9013 |
| 62 | train | level_db | 4 | 2.5888 | 3.4729 | 0.8841 |
| 78 | train | level_db | 4 | 3.7700 | 4.6116 | 0.8416 |
| 82 | dev | decay_db_s | 3 | 3.5485 | 5.2254 | 1.6770 |
| 103 | dev | level_db | 1 | 3.1166 | 3.9502 | 0.8336 |
| 45 | train | level_db | 4 | 0.7071 | 1.5357 | 0.8286 |
| 30 | train | level_db | 4 | 0.7416 | 1.4727 | 0.7311 |
| 102 | dev | partial_db | 2 | 11.1854 | 11.8696 | 0.6842 |
| 70 | train | level_db | 4 | 2.5463 | 3.2048 | 0.6585 |
| 24 | train | level_db | 4 | 2.8005 | 3.4080 | 0.6075 |
| 84 | train | noise_db | 4 | 5.4331 | 6.0102 | 0.5771 |
| 42 | train | level_db | 4 | 1.2169 | 1.7540 | 0.5371 |
| 27 | dev | sustain_db | 4 | 8.9675 | 9.5042 | 0.5367 |
| 80 | train | level_db | 4 | 4.2631 | 4.7900 | 0.5269 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
