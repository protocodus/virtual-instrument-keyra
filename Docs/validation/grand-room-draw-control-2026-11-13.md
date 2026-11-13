# Recording benchmark: 2.11.0, the room's phases drawn again against 2.11.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.11.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 7.72 | 2.12 | 3.90 | 6.60 | 6.40 | 8.55 | 7.12 | 5.03 | 0.20 | 4.32 | 13.30 | 2.44 |
| dev (156) | 7.41 | 2.21 | 3.29 | 6.32 | 5.98 | 7.78 | 6.84 | 5.15 | 0.19 | 4.00 | 12.07 | 2.63 |
| train / bass A0-B2 (84) | 8.98 | 2.64 | 2.46 | 6.30 | 5.74 | 6.83 | 6.65 | 4.47 | 0.23 | 3.62 | 23.88 | 2.16 |
| train / middle C3-B5 (108) | 6.46 | 1.36 | 3.81 | 5.79 | 5.86 | 7.10 | 6.79 | 7.29 | 0.20 | 4.16 | 10.20 | 1.80 |
| train / treble C6-C8 (84) | 8.07 | 2.57 | 5.57 | 7.94 | 7.75 | 12.14 | 7.99 | 2.49 | 0.18 | 5.22 | 6.71 | 3.53 |
| dev / bass A0-B2 (44) | 9.83 | 3.25 | 2.28 | 6.03 | 5.24 | 6.07 | 6.55 | 4.75 | 0.23 | 3.04 | 22.39 | 2.85 |
| dev / middle C3-B5 (68) | 6.52 | 1.21 | 3.41 | 5.88 | 5.73 | 6.96 | 6.67 | 7.37 | 0.16 | 4.04 | 10.18 | 1.84 |
| dev / treble C6-C8 (44) | 6.36 | 2.71 | 4.12 | 7.30 | 7.08 | 10.76 | 7.37 | 2.00 | 0.21 | 4.90 | 4.69 | 3.64 |

## 2.11.0, the room's phases drawn again

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 7.64 | 2.16 | 3.91 | 6.59 | 6.41 | 8.45 | 7.26 | 5.97 | 0.20 | 4.35 | 12.82 | 2.84 |
| dev (156) | 7.72 | 2.22 | 3.27 | 6.87 | 6.56 | 7.95 | 7.43 | 5.61 | 0.19 | 4.05 | 10.82 | 3.58 |
| train / bass A0-B2 (84) | 8.94 | 2.70 | 2.46 | 6.35 | 5.71 | 6.84 | 6.86 | 5.06 | 0.21 | 3.74 | 21.14 | 1.87 |
| train / middle C3-B5 (108) | 6.37 | 1.36 | 3.81 | 5.86 | 5.82 | 7.16 | 7.02 | 8.10 | 0.20 | 4.13 | 11.36 | 2.47 |
| train / treble C6-C8 (84) | 7.96 | 2.67 | 5.61 | 7.78 | 7.87 | 11.73 | 7.96 | 4.01 | 0.19 | 5.23 | 6.39 | 4.27 |
| dev / bass A0-B2 (44) | 9.62 | 3.31 | 2.30 | 6.12 | 5.34 | 6.17 | 6.69 | 4.95 | 0.21 | 3.20 | 20.76 | 2.83 |
| dev / middle C3-B5 (68) | 7.36 | 1.21 | 3.42 | 6.75 | 6.44 | 7.49 | 7.48 | 7.54 | 0.17 | 4.03 | 8.38 | 2.87 |
| dev / treble C6-C8 (44) | 6.38 | 2.70 | 4.02 | 7.80 | 7.96 | 10.47 | 8.07 | 3.20 | 0.22 | 4.94 | 4.64 | 5.44 |

## Independent-sample regressions (legacy)

Every note and role where 2.11.0, the room's phases drawn again is worse than 2.11.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.11.0 | 2.11.0, the room's phases drawn again |
|---|---|---|---|---|
| 24 | train | rise_ms | 11.94 | 36.46 |
| 24 | dev | rise_ms | 12.04 | 33.79 |
| 93 | train | ild_db | 2.76 | 12.08 |
| 93 | dev | ild_db | 2.79 | 12.06 |
| 42 | dev | rise_ms | 0.79 | 10.97 |
| 69 | dev | ild_db | 5.97 | 10.88 |
| 69 | train | ild_db | 5.76 | 10.67 |
| 69 | train | rise_ms | 3.36 | 12.48 |
| 72 | dev | rise_ms | 0.46 | 9.15 |
| 93 | dev | level_db | 0.73 | 4.72 |
| 69 | dev | rise_ms | 3.46 | 11.39 |
| 36 | dev | rise_ms | 21.15 | 28.73 |
| 36 | train | rise_ms | 19.98 | 27.35 |
| 72 | train | rise_ms | 0.66 | 7.56 |
| 99 | dev | level_db | 4.60 | 7.96 |
| 75 | dev | level_db | 2.61 | 5.71 |
| 96 | dev | level_db | 4.63 | 7.60 |
| 93 | train | level_db | 2.12 | 5.00 |
| 75 | dev | attack_db | 7.49 | 10.31 |
| 75 | dev | partial_db | 6.43 | 9.25 |
| 81 | train | level_db | 2.53 | 5.31 |
| 81 | dev | level_db | 2.86 | 5.64 |
| 96 | train | level_db | 4.93 | 7.58 |
| 54 | dev | ild_db | 4.91 | 7.54 |
| 69 | train | level_db | 0.75 | 3.37 |
| 42 | train | rise_ms | 3.27 | 8.41 |
| 54 | train | ild_db | 4.93 | 7.45 |
| 78 | dev | partial_db | 10.18 | 12.66 |
| 78 | train | partial_db | 9.59 | 12.04 |
| 30 | dev | rise_ms | 11.27 | 15.89 |
| 75 | dev | early_db | 6.64 | 8.86 |
| 69 | dev | level_db | 1.01 | 3.18 |
| 78 | dev | sustain_db | 10.73 | 12.90 |
| 78 | train | sustain_db | 10.10 | 12.22 |
| 99 | dev | early_db | 6.16 | 8.21 |
| 75 | dev | noise_db | 6.42 | 8.46 |
| 75 | dev | sustain_db | 7.14 | 9.11 |
| 99 | dev | noise_db | 6.45 | 8.34 |
| 54 | dev | level_db | 1.30 | 3.17 |
| 54 | dev | noise_db | 8.91 | 10.74 |
| 72 | train | ild_db | 7.87 | 9.70 |
| 45 | train | ild_db | 4.14 | 5.96 |
| 78 | train | attack_db | 8.46 | 10.27 |
| 78 | dev | attack_db | 8.52 | 10.26 |
| 30 | train | rise_ms | 12.03 | 15.46 |
| 45 | dev | ild_db | 4.15 | 5.85 |
| 96 | dev | early_db | 5.22 | 6.90 |
| 99 | dev | attack_db | 6.38 | 7.99 |
| 54 | train | level_db | 1.62 | 3.19 |
| 96 | dev | noise_db | 6.00 | 7.53 |
| 54 | train | rise_ms | 14.20 | 17.18 |
| 48 | train | rise_ms | 6.54 | 9.47 |
| 81 | train | noise_db | 6.14 | 7.56 |
| 54 | train | noise_db | 8.54 | 9.92 |
| 96 | train | early_db | 5.69 | 7.06 |
| 81 | dev | noise_db | 5.47 | 6.83 |
| 78 | train | early_db | 9.76 | 11.11 |
| 72 | dev | ild_db | 8.07 | 9.40 |
| 78 | dev | early_db | 10.07 | 11.38 |
| 57 | train | ild_db | 4.93 | 6.24 |
| 96 | train | noise_db | 6.24 | 7.52 |
| 96 | dev | attack_db | 5.75 | 6.91 |
| 30 | train | ild_db | 3.47 | 4.62 |
| 30 | dev | ild_db | 3.36 | 4.48 |
| 81 | train | early_db | 5.59 | 6.66 |
| 57 | dev | ild_db | 5.26 | 6.29 |
| 96 | train | attack_db | 5.95 | 6.98 |
| 60 | train | level_db | 1.39 | 2.41 |
| 81 | dev | early_db | 5.52 | 6.54 |
| 96 | dev | ild_db | 0.51 | 1.53 |
| 78 | dev | noise_db | 6.27 | 7.27 |
| 78 | train | noise_db | 6.28 | 7.27 |
| 60 | dev | level_db | 1.47 | 2.44 |
| 36 | dev | noise_db | 3.14 | 4.10 |
| 78 | train | level_db | 3.31 | 4.24 |
| 51 | dev | noise_db | 6.72 | 7.63 |
| 96 | train | ild_db | 0.52 | 1.43 |
| 78 | dev | level_db | 3.36 | 4.24 |
| 51 | dev | partial_db | 6.58 | 7.46 |
| 51 | dev | early_db | 4.58 | 5.45 |
| 51 | dev | icc | 0.09 | 0.13 |
| 69 | dev | sustain_db | 6.09 | 6.92 |
| 36 | train | noise_db | 4.96 | 5.71 |
| 69 | dev | attack_db | 4.87 | 5.62 |
| 51 | dev | attack_db | 4.83 | 5.54 |
| 69 | train | attack_db | 4.96 | 5.67 |
| 45 | dev | icc | 0.16 | 0.19 |
| 108 | train | ild_db | 1.00 | 1.70 |
| 108 | train | icc | 0.25 | 0.28 |
| 99 | dev | ild_db | 1.40 | 2.07 |
| 45 | train | sustain_db | 6.17 | 6.82 |
| 30 | dev | noise_db | 6.46 | 7.10 |
| 81 | dev | rise_ms | 2.54 | 3.81 |
| 45 | train | icc | 0.16 | 0.18 |
| 27 | dev | level_db | 4.15 | 4.75 |
| 45 | dev | sustain_db | 6.07 | 6.66 |
| 69 | train | sustain_db | 6.06 | 6.64 |
| 81 | train | rise_ms | 2.23 | 3.38 |
| 105 | dev | tuning_cents | 0.63 | 1.15 |
| 105 | train | ild_db | 2.79 | 3.31 |
| 108 | dev | ild_db | 1.06 | 1.57 |
| 105 | dev | ild_db | 1.96 | 2.47 |
| 84 | dev | rise_ms | 11.26 | 12.27 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (23.6952 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 7.4093 | 7.7178 | 0.3085 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.2106 | 2.2232 | 0.0125 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 3.2854 | 3.2676 | -0.0179 | 0 | 0 | 1 |
| dev | attack_db | 156 | 6.3201 | 6.8682 | 0.5480 | 0 | 0 | 0 |
| dev | early_db | 156 | 5.9753 | 6.5591 | 0.5838 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 7.7820 | 7.9545 | 0.1725 | 0 | 0 | 0 |
| dev | noise_db | 153 | 6.8383 | 7.4295 | 0.5912 | 0 | 0 | 3 |
| dev | ild_db | 154 | 5.1540 | 5.6128 | 0.4587 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1942 | 0.1938 | -0.0004 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 4.0017 | 4.0523 | 0.0505 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 12.0743 | 10.8156 | -1.2587 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.6324 | 3.6172 | 0.9848 | 0 | 0 | 0 |
| train | partial_db | 276 | 7.7162 | 7.6380 | -0.0782 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.1169 | 2.1633 | 0.0464 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 3.9040 | 3.9132 | 0.0092 | 0 | 0 | 5 |
| train | attack_db | 276 | 6.5974 | 6.5933 | -0.0041 | 0 | 0 | 0 |
| train | early_db | 276 | 6.3990 | 6.4121 | 0.0131 | 0 | 0 | 0 |
| train | sustain_db | 276 | 8.5506 | 8.4516 | -0.0990 | 0 | 0 | 0 |
| train | noise_db | 274 | 7.1186 | 7.2602 | 0.1417 | 0 | 0 | 2 |
| train | ild_db | 270 | 5.0267 | 5.9705 | 0.9437 | 0 | 0 | 6 |
| train | icc | 270 | 0.2026 | 0.1992 | -0.0034 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.3162 | 4.3483 | 0.0321 | 0 | 0 | 0 |
| train | rise_ms | 276 | 13.3022 | 12.8235 | -0.4787 | 0 | 0 | 0 |
| train | level_db | 276 | 2.4373 | 2.8377 | 0.4004 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 24 | train | rise_ms | 12 | 11.9392 | 36.4566 | 24.5174 |
| 24 | dev | rise_ms | 4 | 12.0417 | 33.7917 | 21.7500 |
| 93 | train | ild_db | 12 | 2.7650 | 12.0840 | 9.3190 |
| 93 | dev | ild_db | 4 | 2.7936 | 12.0636 | 9.2700 |
| 42 | dev | rise_ms | 4 | 0.7865 | 10.9688 | 10.1823 |
| 69 | dev | ild_db | 4 | 5.9726 | 10.8837 | 4.9111 |
| 69 | train | ild_db | 12 | 5.7563 | 10.6674 | 4.9111 |
| 69 | train | rise_ms | 12 | 3.3611 | 12.4757 | 9.1146 |
| 72 | dev | rise_ms | 4 | 0.4635 | 9.1458 | 8.6823 |
| 69 | dev | rise_ms | 4 | 3.4583 | 11.3906 | 7.9323 |
| 36 | dev | rise_ms | 4 | 21.1510 | 28.7292 | 7.5781 |
| 36 | train | rise_ms | 12 | 19.9774 | 27.3524 | 7.3750 |
| 93 | dev | level_db | 4 | 0.7303 | 4.4030 | 3.6727 |
| 72 | train | rise_ms | 12 | 0.6649 | 7.5608 | 6.8958 |
| 75 | dev | level_db | 16 | 2.6050 | 6.0245 | 3.4195 |
| 99 | dev | level_db | 16 | 4.5979 | 7.6862 | 3.0883 |
| 69 | train | level_db | 12 | 0.7514 | 3.6827 | 2.9313 |
| 75 | dev | attack_db | 16 | 7.4899 | 10.3070 | 2.8171 |
| 75 | dev | partial_db | 16 | 6.4329 | 9.2474 | 2.8145 |
| 96 | dev | level_db | 4 | 4.6251 | 7.2849 | 2.6598 |
| 54 | dev | ild_db | 4 | 4.9094 | 7.5394 | 2.6301 |
| 93 | train | level_db | 12 | 2.1240 | 4.7348 | 2.6108 |
| 42 | train | rise_ms | 12 | 3.2691 | 8.4080 | 5.1389 |
| 54 | train | ild_db | 12 | 4.9265 | 7.4499 | 2.5234 |
| 69 | dev | level_db | 4 | 1.0053 | 3.4924 | 2.4872 |
| 78 | dev | partial_db | 4 | 10.1768 | 12.6566 | 2.4798 |
| 81 | train | level_db | 12 | 2.5311 | 4.9968 | 2.4657 |
| 81 | dev | level_db | 4 | 2.8557 | 5.3204 | 2.4648 |
| 78 | train | partial_db | 12 | 9.5922 | 12.0391 | 2.4468 |
| 96 | train | level_db | 12 | 4.9324 | 7.3143 | 2.3819 |
| 30 | dev | rise_ms | 4 | 11.2708 | 15.8854 | 4.6146 |
| 75 | dev | early_db | 16 | 6.6381 | 8.8633 | 2.2252 |
| 78 | dev | sustain_db | 4 | 10.7335 | 12.9012 | 2.1678 |
| 78 | train | sustain_db | 12 | 10.0954 | 12.2172 | 2.1218 |
| 99 | dev | early_db | 16 | 6.1632 | 8.2125 | 2.0493 |
| 75 | dev | noise_db | 16 | 6.4223 | 8.4575 | 2.0353 |
| 75 | dev | sustain_db | 16 | 7.1425 | 9.1097 | 1.9672 |
| 99 | dev | noise_db | 16 | 6.4539 | 8.3440 | 1.8901 |
| 54 | dev | noise_db | 4 | 8.9107 | 10.7392 | 1.8285 |
| 72 | train | ild_db | 12 | 7.8697 | 9.6953 | 1.8255 |
| 45 | train | ild_db | 12 | 4.1371 | 5.9551 | 1.8180 |
| 78 | train | attack_db | 12 | 8.4632 | 10.2728 | 1.8096 |
| 78 | dev | attack_db | 4 | 8.5231 | 10.2560 | 1.7329 |
| 30 | train | rise_ms | 12 | 12.0295 | 15.4601 | 3.4306 |
| 45 | dev | ild_db | 4 | 4.1489 | 5.8509 | 1.7020 |
| 96 | dev | early_db | 4 | 5.2166 | 6.9028 | 1.6862 |
| 99 | dev | attack_db | 16 | 6.3844 | 7.9868 | 1.6024 |
| 54 | dev | level_db | 4 | 1.2972 | 2.8600 | 1.5628 |
| 96 | dev | noise_db | 4 | 6.0044 | 7.5263 | 1.5220 |
| 54 | train | rise_ms | 12 | 14.2014 | 17.1840 | 2.9826 |
| 48 | train | rise_ms | 12 | 6.5417 | 9.4688 | 2.9271 |
| 81 | train | noise_db | 12 | 6.1394 | 7.5554 | 1.4160 |
| 54 | train | noise_db | 12 | 8.5387 | 9.9198 | 1.3811 |
| 96 | train | early_db | 12 | 5.6888 | 7.0636 | 1.3748 |
| 81 | dev | noise_db | 4 | 5.4679 | 6.8280 | 1.3601 |
| 78 | train | early_db | 12 | 9.7556 | 11.1057 | 1.3501 |
| 60 | train | level_db | 12 | 1.3863 | 2.7230 | 1.3367 |
| 72 | dev | ild_db | 4 | 8.0678 | 9.3973 | 1.3295 |
| 78 | dev | early_db | 4 | 10.0661 | 11.3835 | 1.3173 |
| 57 | train | ild_db | 12 | 4.9275 | 6.2426 | 1.3151 |
| 60 | dev | level_db | 4 | 1.4745 | 2.7593 | 1.2848 |
| 96 | train | noise_db | 12 | 6.2419 | 7.5206 | 1.2788 |
| 54 | train | level_db | 12 | 1.6169 | 2.8778 | 1.2608 |
| 78 | train | level_db | 12 | 3.3149 | 4.5595 | 1.2447 |
| 78 | dev | level_db | 4 | 3.3590 | 4.5591 | 1.2001 |
| 96 | dev | attack_db | 4 | 5.7491 | 6.9107 | 1.1616 |
| 30 | train | ild_db | 12 | 3.4699 | 4.6186 | 1.1487 |
| 30 | dev | ild_db | 4 | 3.3584 | 4.4833 | 1.1249 |
| 81 | train | early_db | 12 | 5.5875 | 6.6571 | 1.0696 |
| 57 | dev | ild_db | 4 | 5.2622 | 6.2939 | 1.0318 |
| 96 | train | attack_db | 12 | 5.9496 | 6.9813 | 1.0317 |
| 81 | dev | early_db | 4 | 5.5178 | 6.5364 | 1.0187 |
| 96 | dev | ild_db | 4 | 0.5133 | 1.5296 | 1.0163 |
| 78 | dev | noise_db | 4 | 6.2740 | 7.2717 | 0.9977 |
| 78 | train | noise_db | 12 | 6.2844 | 7.2720 | 0.9877 |
| 36 | dev | noise_db | 4 | 3.1394 | 4.0956 | 0.9562 |
| 27 | dev | level_db | 16 | 4.1466 | 5.0652 | 0.9186 |
| 51 | dev | noise_db | 14 | 6.7206 | 7.6303 | 0.9097 |
| 96 | train | ild_db | 12 | 0.5185 | 1.4264 | 0.9079 |
| 51 | dev | partial_db | 16 | 6.5833 | 7.4591 | 0.8758 |
| 51 | dev | early_db | 16 | 4.5836 | 5.4538 | 0.8703 |
| 51 | dev | icc | 16 | 0.0933 | 0.1268 | 0.0336 |
| 69 | dev | sustain_db | 4 | 6.0857 | 6.9221 | 0.8364 |
| 36 | train | noise_db | 12 | 4.9581 | 5.7112 | 0.7531 |
| 69 | dev | attack_db | 4 | 4.8652 | 5.6156 | 0.7504 |
| 51 | dev | attack_db | 16 | 4.8283 | 5.5433 | 0.7150 |
| 69 | train | attack_db | 12 | 4.9606 | 5.6744 | 0.7138 |
| 45 | dev | icc | 4 | 0.1603 | 0.1887 | 0.0284 |
| 108 | train | ild_db | 7 | 0.9970 | 1.7018 | 0.7048 |
| 108 | train | icc | 7 | 0.2536 | 0.2811 | 0.0275 |
| 99 | dev | ild_db | 16 | 1.3955 | 2.0746 | 0.6791 |
| 45 | train | sustain_db | 12 | 6.1739 | 6.8248 | 0.6509 |
| 30 | dev | noise_db | 4 | 6.4637 | 7.1042 | 0.6404 |
| 81 | dev | rise_ms | 4 | 2.5365 | 3.8073 | 1.2708 |
| 45 | train | icc | 12 | 0.1582 | 0.1833 | 0.0251 |
| 45 | dev | sustain_db | 4 | 6.0673 | 6.6576 | 0.5903 |
| 69 | train | sustain_db | 12 | 6.0552 | 6.6364 | 0.5812 |
| 81 | train | rise_ms | 12 | 2.2344 | 3.3837 | 1.1493 |
| 105 | dev | tuning_cents | 4 | 0.6256 | 1.1488 | 0.5231 |
| 105 | train | ild_db | 11 | 2.7945 | 3.3105 | 0.5161 |
| 108 | dev | ild_db | 2 | 1.0563 | 1.5716 | 0.5154 |
| 105 | dev | ild_db | 4 | 1.9585 | 2.4737 | 0.5152 |
| 84 | dev | rise_ms | 4 | 11.2604 | 12.2708 | 1.0104 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
