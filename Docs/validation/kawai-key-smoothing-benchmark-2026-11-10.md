# Recording benchmark: 0.4.32 against 0.4.31

Every train and dev note of `Tools/corpus/split-vcsl-kawai-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.31

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (104) | 7.86 | 0.50 | 3.85 | 6.46 | 7.47 | 7.85 | 8.39 | 1.77 | 0.10 | 3.52 | 7.35 | 1.93 |
| dev (23) | 9.50 | 2.39 | 5.03 | 6.90 | 8.71 | 8.39 | 9.02 | 5.60 | 0.20 | 5.08 | 4.83 | 4.23 |
| train / bass A0-B2 (27) | 9.83 | 0.41 | 1.84 | 6.77 | 7.13 | 7.54 | 9.57 | 1.42 | 0.07 | 2.91 | 14.94 | 1.48 |
| train / middle C3-B5 (52) | 7.92 | 0.44 | 4.05 | 6.30 | 7.33 | 8.45 | 8.34 | 2.14 | 0.12 | 3.79 | 5.54 | 1.96 |
| train / treble C6-C8 (25) | 5.30 | 0.78 | 6.81 | 6.48 | 8.20 | 6.40 | 7.40 | 1.04 | 0.07 | 3.61 | 2.89 | 2.34 |
| dev / bass A0-B2 (8) | 10.22 | 2.33 | 2.59 | 5.92 | 6.05 | 8.50 | 9.65 | 3.26 | 0.15 | 3.85 | 8.44 | 1.76 |
| dev / middle C3-B5 (12) | 8.95 | 2.11 | 5.99 | 7.18 | 9.37 | 8.89 | 8.59 | 7.76 | 0.16 | 5.72 | 3.00 | 4.74 |
| dev / treble C6-C8 (3) | 9.93 | 4.30 | 8.97 | 8.37 | 13.19 | 4.90 | 8.96 | 3.09 | 0.66 | 5.74 | 2.49 | 8.79 |

## 0.4.32

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (104) | 7.56 | 0.54 | 3.90 | 6.54 | 7.61 | 7.54 | 8.52 | 4.49 | 0.10 | 3.42 | 6.80 | 2.78 |
| dev (23) | 9.40 | 2.38 | 4.99 | 6.91 | 8.77 | 8.34 | 8.98 | 4.87 | 0.20 | 5.03 | 5.32 | 4.20 |
| train / bass A0-B2 (27) | 9.78 | 0.42 | 1.83 | 6.70 | 7.05 | 7.50 | 9.64 | 1.67 | 0.07 | 2.89 | 12.81 | 2.36 |
| train / middle C3-B5 (52) | 7.50 | 0.49 | 4.12 | 6.28 | 7.33 | 7.87 | 8.24 | 5.51 | 0.12 | 3.62 | 5.60 | 2.67 |
| train / treble C6-C8 (25) | 4.99 | 0.78 | 6.88 | 6.92 | 8.91 | 6.55 | 7.99 | 6.44 | 0.07 | 3.59 | 2.81 | 3.46 |
| dev / bass A0-B2 (8) | 10.29 | 2.30 | 2.60 | 5.91 | 6.12 | 8.51 | 9.60 | 3.33 | 0.15 | 3.86 | 8.50 | 1.31 |
| dev / middle C3-B5 (12) | 8.73 | 2.11 | 5.92 | 7.17 | 9.38 | 8.81 | 8.53 | 6.27 | 0.16 | 5.64 | 3.91 | 5.04 |
| dev / treble C6-C8 (3) | 9.91 | 4.30 | 8.95 | 8.56 | 13.38 | 4.87 | 9.00 | 3.38 | 0.66 | 5.75 | 2.49 | 8.57 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.32 is worse than 0.4.31 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.31 | 0.4.32 |
|---|---|---|---|---|
| 84 | train | ild_db | 0.83 | 14.49 |
| 80 | train | ild_db | 3.03 | 12.31 |
| 70 | train | ild_db | 3.03 | 10.77 |
| 78 | train | ild_db | 3.10 | 10.73 |
| 64 | train | ild_db | 2.09 | 8.93 |
| 68 | train | ild_db | 2.92 | 8.47 |
| 96 | train | ild_db | 0.26 | 4.85 |
| 84 | train | early_db | 7.56 | 10.53 |
| 80 | train | level_db | 3.95 | 6.84 |
| 84 | train | noise_db | 7.53 | 10.34 |
| 60 | train | ild_db | 2.89 | 5.67 |
| 76 | train | ild_db | 0.91 | 3.30 |
| 84 | train | attack_db | 4.66 | 7.02 |
| 99 | train | level_db | 0.47 | 2.73 |
| 96 | train | level_db | 2.14 | 4.30 |
| 68 | train | level_db | 0.27 | 2.38 |
| 33 | train | level_db | 0.64 | 2.72 |
| 45 | train | level_db | 0.86 | 2.75 |
| 72 | train | ild_db | 2.21 | 4.09 |
| 72 | train | level_db | 2.27 | 3.91 |
| 87 | train | ild_db | 1.30 | 2.86 |
| 105 | train | level_db | 2.50 | 4.01 |
| 36 | train | level_db | 1.21 | 2.64 |
| 99 | train | early_db | 5.63 | 6.96 |
| 56 | train | level_db | 4.03 | 5.21 |
| 82 | dev | rise_ms | 2.38 | 4.69 |
| 70 | train | envelope_db | 5.38 | 6.52 |
| 52 | train | level_db | 2.00 | 3.13 |
| 72 | train | noise_db | 7.90 | 8.95 |
| 62 | train | ild_db | 1.36 | 2.40 |
| 72 | train | early_db | 7.07 | 8.01 |
| 52 | train | ild_db | 1.51 | 2.43 |
| 105 | train | ild_db | 0.77 | 1.68 |
| 74 | dev | level_db | 4.97 | 5.88 |
| 60 | train | level_db | 1.29 | 2.06 |
| 93 | train | level_db | 0.50 | 1.27 |
| 74 | dev | early_db | 9.10 | 9.87 |
| 84 | train | level_db | 2.84 | 3.61 |
| 87 | train | level_db | 0.77 | 1.54 |
| 30 | train | level_db | 0.85 | 1.61 |
| 54 | train | level_db | 0.55 | 1.30 |
| 84 | train | sustain_db | 3.55 | 4.30 |
| 70 | train | partial_db | 8.13 | 8.81 |
| 78 | train | rise_ms | 2.83 | 4.11 |
| 74 | dev | noise_db | 8.44 | 9.08 |
| 74 | dev | rise_ms | 4.60 | 5.84 |
| 72 | train | attack_db | 6.20 | 6.81 |
| 60 | train | noise_db | 8.20 | 8.79 |
| 45 | train | ild_db | 1.43 | 2.01 |
| 68 | train | noise_db | 7.13 | 7.67 |
| 82 | dev | ild_db | 7.15 | 7.68 |
| 36 | train | ild_db | 1.96 | 2.48 |
| 62 | train | level_db | 2.57 | 3.09 |
| 42 | train | ild_db | 1.43 | 1.94 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.7275 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 22 | 9.4962 | 9.4022 | -0.0940 | 0 | 0 | 1 |
| dev | tuning_cents | 22 | 2.3864 | 2.3760 | -0.0103 | 0 | 0 | 1 |
| dev | decay_db_s | 22 | 5.0258 | 4.9877 | -0.0381 | 0 | 0 | 1 |
| dev | attack_db | 23 | 6.8957 | 6.9117 | 0.0160 | 0 | 0 | 0 |
| dev | early_db | 23 | 8.7105 | 8.7689 | 0.0583 | 0 | 0 | 0 |
| dev | sustain_db | 22 | 8.3871 | 8.3436 | -0.0435 | 0 | 0 | 1 |
| dev | noise_db | 22 | 9.0224 | 8.9846 | -0.0378 | 0 | 0 | 1 |
| dev | ild_db | 21 | 5.6007 | 4.8749 | -0.7258 | 0 | 0 | 2 |
| dev | icc | 21 | 0.2046 | 0.2035 | -0.0011 | 0 | 0 | 2 |
| dev | envelope_db | 23 | 5.0763 | 5.0345 | -0.0417 | 0 | 0 | 0 |
| dev | rise_ms | 23 | 4.8270 | 5.3226 | 0.4956 | 0 | 0 | 0 |
| dev | level_db | 23 | 4.2303 | 4.2030 | -0.0273 | 0 | 0 | 0 |
| train | partial_db | 100 | 7.8573 | 7.5633 | -0.2941 | 0 | 0 | 4 |
| train | tuning_cents | 100 | 0.5036 | 0.5385 | 0.0349 | 0 | 0 | 4 |
| train | decay_db_s | 93 | 3.8522 | 3.9032 | 0.0510 | 0 | 0 | 11 |
| train | attack_db | 104 | 6.4648 | 6.5424 | 0.0777 | 0 | 0 | 0 |
| train | early_db | 102 | 7.4715 | 7.6116 | 0.1401 | 0 | 0 | 2 |
| train | sustain_db | 94 | 7.6398 | 7.5413 | -0.0984 | 1 | 0 | 9 |
| train | noise_db | 94 | 8.3892 | 8.5433 | 0.1542 | 0 | 1 | 9 |
| train | ild_db | 90 | 1.7679 | 4.4939 | 2.7260 | 0 | 0 | 14 |
| train | icc | 90 | 0.0974 | 0.0972 | -0.0002 | 0 | 0 | 14 |
| train | envelope_db | 104 | 3.5159 | 3.4221 | -0.0938 | 0 | 0 | 0 |
| train | rise_ms | 104 | 7.3457 | 6.8010 | -0.5447 | 0 | 0 | 0 |
| train | level_db | 104 | 1.9288 | 2.7813 | 0.8526 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 84 | train | ild_db | 4 | 0.8265 | 14.4932 | 13.6667 |
| 80 | train | ild_db | 3 | 3.0280 | 12.3108 | 9.2827 |
| 70 | train | ild_db | 4 | 3.0274 | 10.7721 | 7.7447 |
| 78 | train | ild_db | 3 | 3.1019 | 10.7343 | 7.6324 |
| 64 | train | ild_db | 4 | 2.0907 | 8.9306 | 6.8399 |
| 68 | train | ild_db | 4 | 2.9213 | 8.4750 | 5.5537 |
| 96 | train | ild_db | 2 | 0.2645 | 4.8513 | 4.5868 |
| 84 | train | early_db | 4 | 7.5592 | 10.5323 | 2.9731 |
| 80 | train | level_db | 4 | 3.9476 | 6.7969 | 2.8494 |
| 84 | train | noise_db | 4 | 7.5251 | 10.3442 | 2.8191 |
| 60 | train | ild_db | 4 | 2.8924 | 5.6707 | 2.7783 |
| 76 | train | ild_db | 4 | 0.9095 | 3.3036 | 2.3942 |
| 84 | train | attack_db | 4 | 4.6552 | 7.0212 | 2.3660 |
| 99 | train | level_db | 3 | 0.4750 | 2.7100 | 2.2350 |
| 96 | train | level_db | 4 | 2.1422 | 4.3268 | 2.1846 |
| 68 | train | level_db | 4 | 0.2747 | 2.4281 | 2.1535 |
| 33 | train | level_db | 4 | 0.6440 | 2.7643 | 2.1202 |
| 45 | train | level_db | 4 | 0.8572 | 2.7701 | 1.9129 |
| 72 | train | ild_db | 4 | 2.2056 | 4.0897 | 1.8841 |
| 72 | train | level_db | 4 | 2.2664 | 3.9573 | 1.6909 |
| 87 | train | ild_db | 3 | 1.2983 | 2.8623 | 1.5639 |
| 105 | train | level_db | 4 | 2.4961 | 3.9594 | 1.4633 |
| 36 | train | level_db | 4 | 1.2075 | 2.6163 | 1.4088 |
| 99 | train | early_db | 3 | 5.6339 | 6.9581 | 1.3242 |
| 52 | train | level_db | 4 | 2.0004 | 3.1714 | 1.1710 |
| 82 | dev | rise_ms | 3 | 2.3798 | 4.6921 | 2.3123 |
| 70 | train | envelope_db | 4 | 5.3758 | 6.5221 | 1.1462 |
| 56 | train | level_db | 4 | 4.0306 | 5.1600 | 1.1294 |
| 72 | train | noise_db | 4 | 7.8979 | 8.9518 | 1.0539 |
| 62 | train | ild_db | 4 | 1.3576 | 2.3975 | 1.0399 |
| 72 | train | early_db | 4 | 7.0698 | 8.0074 | 0.9376 |
| 74 | dev | level_db | 4 | 4.9723 | 5.9038 | 0.9314 |
| 52 | train | ild_db | 4 | 1.5099 | 2.4334 | 0.9235 |
| 105 | train | ild_db | 1 | 0.7650 | 1.6843 | 0.9192 |
| 84 | train | level_db | 4 | 2.8380 | 3.6537 | 0.8157 |
| 60 | train | level_db | 4 | 1.2864 | 2.0855 | 0.7991 |
| 74 | dev | early_db | 4 | 9.1001 | 9.8720 | 0.7720 |
| 30 | train | level_db | 4 | 0.8452 | 1.6082 | 0.7630 |
| 93 | train | level_db | 3 | 0.4962 | 1.2536 | 0.7574 |
| 54 | train | level_db | 4 | 0.5458 | 1.3023 | 0.7565 |
| 87 | train | level_db | 3 | 0.7732 | 1.5236 | 0.7504 |
| 84 | train | sustain_db | 4 | 3.5495 | 4.2980 | 0.7485 |
| 70 | train | partial_db | 4 | 8.1312 | 8.8063 | 0.6750 |
| 78 | train | rise_ms | 4 | 2.8284 | 4.1149 | 1.2865 |
| 74 | dev | noise_db | 4 | 8.4400 | 9.0759 | 0.6360 |
| 74 | dev | rise_ms | 4 | 4.6028 | 5.8372 | 1.2344 |
| 72 | train | attack_db | 4 | 6.1972 | 6.8111 | 0.6139 |
| 60 | train | noise_db | 4 | 8.1964 | 8.7913 | 0.5949 |
| 45 | train | ild_db | 4 | 1.4282 | 2.0137 | 0.5854 |
| 68 | train | noise_db | 4 | 7.1329 | 7.6745 | 0.5416 |
| 82 | dev | ild_db | 2 | 7.1460 | 7.6824 | 0.5364 |
| 36 | train | ild_db | 4 | 1.9570 | 2.4803 | 0.5233 |
| 42 | train | ild_db | 4 | 1.4301 | 1.9428 | 0.5127 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| n52v2 | 52 | train | noise_db | gained | - | 5.8831 |
| n80v2 | 80 | train | sustain_db | lost | 27.2522 | - |
