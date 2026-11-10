# Recording benchmark: 0.4.32 against 0.4.31

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.31

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 5.75 | 0.26 | 2.38 | 4.99 | 4.95 | 5.66 | 7.21 | 1.85 | 0.12 | 2.58 | 7.79 | 1.20 |
| dev (21) | 8.23 | 1.62 | 4.08 | 6.29 | 7.00 | 8.52 | 6.73 | 3.90 | 0.19 | 4.53 | 5.86 | 2.53 |
| train / bass A0-B2 (30) | 6.76 | 0.26 | 1.97 | 5.53 | 5.12 | 5.32 | 10.31 | 1.29 | 0.10 | 2.37 | 8.96 | 0.92 |
| train / middle C3-B5 (69) | 6.58 | 0.23 | 2.54 | 5.19 | 4.83 | 5.40 | 7.42 | 1.84 | 0.09 | 2.15 | 9.56 | 1.40 |
| train / treble C6-C8 (38) | 3.45 | 0.31 | 2.43 | 4.20 | 5.03 | 6.38 | 4.99 | 2.34 | 0.18 | 3.52 | 3.66 | 1.04 |
| dev / bass A0-B2 (5) | 8.81 | 1.28 | 2.08 | 5.69 | 7.45 | 8.95 | 7.08 | 5.20 | 0.20 | 2.13 | 1.07 | 1.44 |
| dev / middle C3-B5 (11) | 8.43 | 1.02 | 4.00 | 6.96 | 6.77 | 7.93 | 6.98 | 3.95 | 0.17 | 4.57 | 10.01 | 2.71 |
| dev / treble C6-C8 (5) | 7.19 | 3.30 | 6.28 | 5.40 | 7.04 | 9.37 | 5.91 | 2.48 | 0.25 | 6.84 | 1.54 | 3.21 |

## 0.4.32

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 5.65 | 0.27 | 2.38 | 5.08 | 5.02 | 5.61 | 7.30 | 2.90 | 0.11 | 2.63 | 7.75 | 2.27 |
| dev (21) | 8.17 | 1.55 | 4.11 | 6.15 | 6.93 | 8.63 | 6.51 | 4.23 | 0.19 | 4.64 | 5.83 | 1.73 |
| train / bass A0-B2 (30) | 6.72 | 0.27 | 1.93 | 5.54 | 5.10 | 5.30 | 10.22 | 1.87 | 0.10 | 2.39 | 8.15 | 1.25 |
| train / middle C3-B5 (69) | 6.48 | 0.24 | 2.54 | 5.27 | 4.91 | 5.38 | 7.48 | 2.69 | 0.09 | 2.15 | 9.84 | 2.71 |
| train / treble C6-C8 (38) | 3.30 | 0.33 | 2.43 | 4.36 | 5.16 | 6.28 | 5.21 | 4.15 | 0.18 | 3.67 | 3.63 | 2.29 |
| dev / bass A0-B2 (5) | 8.83 | 1.30 | 2.08 | 5.67 | 7.45 | 8.96 | 7.08 | 5.19 | 0.20 | 2.13 | 1.04 | 1.39 |
| dev / middle C3-B5 (11) | 8.44 | 1.02 | 4.01 | 6.84 | 6.70 | 7.95 | 6.65 | 4.29 | 0.16 | 4.55 | 9.96 | 1.74 |
| dev / treble C6-C8 (5) | 6.89 | 2.98 | 6.36 | 5.13 | 6.89 | 9.79 | 5.73 | 3.13 | 0.25 | 7.32 | 1.53 | 2.06 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.32 is worse than 0.4.31 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.31 | 0.4.32 |
|---|---|---|---|---|
| 86 | train | ild_db | 1.90 | 7.77 |
| 60 | train | ild_db | 2.09 | 6.02 |
| 84 | train | ild_db | 3.98 | 7.89 |
| 54 | train | level_db | 1.47 | 5.15 |
| 58 | train | ild_db | 1.34 | 4.33 |
| 60 | train | level_db | 1.89 | 4.52 |
| 96 | train | level_db | 0.65 | 2.97 |
| 94 | train | level_db | 0.28 | 2.46 |
| 66 | train | level_db | 0.91 | 3.00 |
| 45 | train | ild_db | 1.08 | 3.06 |
| 60 | train | rise_ms | 28.09 | 32.00 |
| 90 | train | level_db | 1.18 | 2.90 |
| 78 | train | level_db | 3.73 | 5.26 |
| 94 | train | ild_db | 0.98 | 2.48 |
| 86 | train | envelope_db | 2.02 | 3.44 |
| 48 | train | level_db | 1.46 | 2.71 |
| 92 | train | level_db | 0.69 | 1.94 |
| 96 | train | ild_db | 2.34 | 3.57 |
| 76 | train | level_db | 2.06 | 3.27 |
| 68 | train | ild_db | 1.27 | 2.46 |
| 27 | train | ild_db | 1.14 | 2.28 |
| 74 | train | level_db | 2.89 | 4.02 |
| 84 | train | level_db | 0.95 | 2.01 |
| 58 | train | level_db | 0.39 | 1.39 |
| 100 | train | ild_db | 2.37 | 3.32 |
| 54 | train | ild_db | 2.70 | 3.61 |
| 86 | train | sustain_db | 3.93 | 4.83 |
| 52 | train | level_db | 0.54 | 1.38 |
| 70 | train | level_db | 0.55 | 1.36 |
| 50 | train | level_db | 0.79 | 1.57 |
| 68 | train | level_db | 1.25 | 2.00 |
| 50 | train | ild_db | 1.27 | 1.99 |
| 84 | train | noise_db | 4.93 | 5.63 |
| 27 | train | level_db | 1.31 | 2.00 |
| 76 | train | ild_db | 1.34 | 2.02 |
| 60 | train | early_db | 5.20 | 5.87 |
| 88 | dev | ild_db | 2.48 | 3.13 |
| 62 | train | level_db | 0.23 | 0.88 |
| 60 | train | attack_db | 5.68 | 6.32 |
| 76 | train | rise_ms | 7.14 | 8.42 |
| 33 | train | level_db | 0.88 | 1.46 |
| 94 | train | noise_db | 4.27 | 4.84 |
| 48 | train | ild_db | 1.41 | 1.97 |
| 59 | dev | ild_db | 3.10 | 3.66 |
| 100 | train | level_db | 1.11 | 1.65 |
| 78 | train | ild_db | 1.46 | 2.01 |
| 86 | train | attack_db | 3.82 | 4.36 |
| 76 | train | noise_db | 5.95 | 6.49 |
| 76 | train | early_db | 5.11 | 5.64 |
| 94 | train | early_db | 4.18 | 4.71 |
| 58 | train | noise_db | 6.63 | 7.14 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (15.8807 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 8.2263 | 8.1668 | -0.0595 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 1.6233 | 1.5508 | -0.0725 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 4.0846 | 4.1099 | 0.0253 | 0 | 0 | 0 |
| dev | attack_db | 21 | 6.2895 | 6.1533 | -0.1361 | 0 | 0 | 0 |
| dev | early_db | 21 | 6.9967 | 6.9250 | -0.0717 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 8.5181 | 8.6280 | 0.1099 | 0 | 0 | 0 |
| dev | noise_db | 20 | 6.7315 | 6.5055 | -0.2260 | 0 | 0 | 1 |
| dev | ild_db | 21 | 3.8969 | 4.2254 | 0.3286 | 0 | 0 | 0 |
| dev | icc | 21 | 0.1942 | 0.1934 | -0.0009 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.5278 | 4.6367 | 0.1089 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 5.8631 | 5.8274 | -0.0357 | 0 | 0 | 0 |
| dev | level_db | 21 | 2.5273 | 1.8481 | -0.6793 | 0 | 0 | 0 |
| train | partial_db | 137 | 5.7506 | 5.6500 | -0.1006 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 0.2614 | 0.2720 | 0.0106 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 2.3817 | 2.3762 | -0.0055 | 0 | 0 | 2 |
| train | attack_db | 137 | 4.9905 | 5.0762 | 0.0857 | 0 | 0 | 0 |
| train | early_db | 137 | 4.9465 | 5.0208 | 0.0743 | 0 | 0 | 0 |
| train | sustain_db | 136 | 5.5939 | 5.6100 | 0.0160 | 1 | 0 | 0 |
| train | noise_db | 125 | 7.2115 | 7.3142 | 0.1027 | 0 | 1 | 11 |
| train | ild_db | 135 | 1.8503 | 2.8958 | 1.0454 | 0 | 0 | 2 |
| train | icc | 135 | 0.1161 | 0.1145 | -0.0016 | 0 | 0 | 2 |
| train | envelope_db | 137 | 2.5787 | 2.6252 | 0.0465 | 0 | 0 | 0 |
| train | rise_ms | 137 | 7.7918 | 7.7502 | -0.0417 | 0 | 0 | 0 |
| train | level_db | 137 | 1.1960 | 2.3150 | 1.1190 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 86 | train | ild_db | 5 | 1.8956 | 7.7691 | 5.8734 |
| 60 | train | ild_db | 5 | 2.0926 | 6.0244 | 3.9318 |
| 84 | train | ild_db | 5 | 3.9760 | 7.8889 | 3.9128 |
| 60 | train | level_db | 5 | 1.8929 | 5.1132 | 3.2203 |
| 54 | train | level_db | 5 | 1.4672 | 4.5580 | 3.0907 |
| 58 | train | ild_db | 4 | 1.3447 | 4.3313 | 2.9865 |
| 96 | train | level_db | 5 | 0.6491 | 3.5587 | 2.9096 |
| 94 | train | level_db | 5 | 0.2818 | 2.7320 | 2.4502 |
| 45 | train | ild_db | 5 | 1.0829 | 3.0620 | 1.9792 |
| 60 | train | rise_ms | 5 | 28.0917 | 32.0000 | 3.9083 |
| 48 | train | level_db | 5 | 1.4564 | 3.3006 | 1.8443 |
| 76 | train | level_db | 5 | 2.0574 | 3.8612 | 1.8038 |
| 74 | train | level_db | 5 | 2.8870 | 4.6131 | 1.7261 |
| 90 | train | level_db | 5 | 1.1820 | 2.7852 | 1.6033 |
| 66 | train | level_db | 5 | 0.9085 | 2.4103 | 1.5019 |
| 94 | train | ild_db | 5 | 0.9793 | 2.4806 | 1.5013 |
| 86 | train | envelope_db | 5 | 2.0217 | 3.4399 | 1.4182 |
| 27 | train | level_db | 5 | 1.3120 | 2.5935 | 1.2816 |
| 84 | train | level_db | 5 | 0.9461 | 2.2078 | 1.2617 |
| 96 | train | ild_db | 5 | 2.3432 | 3.5660 | 1.2228 |
| 68 | train | ild_db | 5 | 1.2655 | 2.4645 | 1.1990 |
| 27 | train | ild_db | 5 | 1.1432 | 2.2789 | 1.1357 |
| 68 | train | level_db | 5 | 1.2459 | 2.3508 | 1.1050 |
| 58 | train | level_db | 4 | 0.3872 | 1.3937 | 1.0065 |
| 100 | train | ild_db | 3 | 2.3654 | 3.3230 | 0.9576 |
| 78 | train | level_db | 5 | 3.7312 | 4.6673 | 0.9360 |
| 54 | train | ild_db | 5 | 2.7043 | 3.6114 | 0.9071 |
| 86 | train | sustain_db | 5 | 3.9306 | 4.8321 | 0.9015 |
| 62 | train | level_db | 5 | 0.2307 | 1.0637 | 0.8331 |
| 50 | train | ild_db | 5 | 1.2723 | 1.9896 | 0.7173 |
| 70 | train | level_db | 5 | 0.5453 | 1.2464 | 0.7011 |
| 84 | train | noise_db | 5 | 4.9333 | 5.6327 | 0.6994 |
| 76 | train | ild_db | 5 | 1.3367 | 2.0151 | 0.6784 |
| 50 | train | level_db | 5 | 0.7887 | 1.4563 | 0.6676 |
| 60 | train | early_db | 5 | 5.2048 | 5.8678 | 0.6629 |
| 92 | train | level_db | 5 | 0.6896 | 1.3474 | 0.6578 |
| 88 | dev | ild_db | 5 | 2.4769 | 3.1302 | 0.6533 |
| 60 | train | attack_db | 5 | 5.6799 | 6.3188 | 0.6389 |
| 76 | train | rise_ms | 5 | 7.1417 | 8.4167 | 1.2750 |
| 94 | train | noise_db | 5 | 4.2744 | 4.8404 | 0.5660 |
| 48 | train | ild_db | 5 | 1.4051 | 1.9692 | 0.5641 |
| 59 | dev | ild_db | 1 | 3.0994 | 3.6625 | 0.5631 |
| 78 | train | ild_db | 5 | 1.4609 | 2.0068 | 0.5459 |
| 86 | train | attack_db | 5 | 3.8198 | 4.3583 | 0.5385 |
| 76 | train | noise_db | 5 | 5.9529 | 6.4902 | 0.5374 |
| 76 | train | early_db | 5 | 5.1091 | 5.6445 | 0.5354 |
| 94 | train | early_db | 5 | 4.1751 | 4.7104 | 0.5353 |
| 58 | train | noise_db | 4 | 6.6265 | 7.1395 | 0.5130 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| n100v1r1 | 100 | train | sustain_db | lost | 14.2445 | - |
| n48v1r1 | 48 | train | noise_db | gained | - | 4.9706 |
