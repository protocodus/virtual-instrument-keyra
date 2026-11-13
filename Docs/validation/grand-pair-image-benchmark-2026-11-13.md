# Recording benchmark: 2.12.0 against 2.11.0

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

## 2.12.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.07 | 2.13 | 3.92 | 6.70 | 6.49 | 8.72 | 7.21 | 4.79 | 0.20 | 4.33 | 14.23 | 2.50 |
| dev (156) | 7.57 | 2.22 | 3.31 | 6.34 | 6.01 | 7.89 | 6.84 | 4.96 | 0.18 | 4.03 | 11.94 | 2.65 |
| train / bass A0-B2 (84) | 8.93 | 2.68 | 2.46 | 6.07 | 5.55 | 6.65 | 6.57 | 4.24 | 0.21 | 3.58 | 24.14 | 2.34 |
| train / middle C3-B5 (108) | 7.48 | 1.36 | 3.87 | 6.30 | 6.33 | 7.77 | 7.17 | 6.78 | 0.19 | 4.24 | 12.23 | 2.03 |
| train / treble C6-C8 (84) | 7.98 | 2.57 | 5.56 | 7.83 | 7.63 | 12.00 | 7.90 | 2.61 | 0.19 | 5.21 | 6.91 | 3.26 |
| dev / bass A0-B2 (44) | 9.65 | 3.29 | 2.29 | 5.87 | 5.10 | 5.89 | 6.37 | 4.47 | 0.21 | 3.00 | 22.94 | 3.13 |
| dev / middle C3-B5 (68) | 7.05 | 1.21 | 3.44 | 6.09 | 6.01 | 7.44 | 6.88 | 6.85 | 0.15 | 4.13 | 9.35 | 1.94 |
| dev / treble C6-C8 (44) | 6.31 | 2.71 | 4.14 | 7.18 | 6.94 | 10.60 | 7.25 | 2.41 | 0.22 | 4.89 | 4.94 | 3.25 |

## Independent-sample regressions (legacy)

Every note and role where 2.12.0 is worse than 2.11.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.11.0 | 2.12.0 |
|---|---|---|---|---|
| 24 | dev | rise_ms | 12.04 | 34.96 |
| 24 | train | rise_ms | 11.94 | 32.12 |
| 48 | train | rise_ms | 6.54 | 17.84 |
| 66 | train | rise_ms | 13.38 | 22.77 |
| 57 | train | rise_ms | 28.29 | 37.65 |
| 57 | dev | rise_ms | 28.71 | 35.49 |
| 96 | dev | ild_db | 0.51 | 3.74 |
| 96 | train | ild_db | 0.52 | 3.63 |
| 30 | dev | rise_ms | 11.27 | 17.45 |
| 36 | train | rise_ms | 19.98 | 25.31 |
| 78 | dev | partial_db | 10.18 | 12.76 |
| 36 | dev | rise_ms | 21.15 | 26.23 |
| 66 | dev | rise_ms | 16.28 | 21.30 |
| 78 | train | partial_db | 9.59 | 12.09 |
| 30 | train | rise_ms | 12.03 | 16.89 |
| 48 | train | ild_db | 7.50 | 9.90 |
| 81 | dev | partial_db | 4.70 | 7.08 |
| 81 | train | partial_db | 4.49 | 6.83 |
| 48 | dev | ild_db | 7.36 | 9.63 |
| 78 | train | sustain_db | 10.10 | 12.17 |
| 78 | dev | sustain_db | 10.73 | 12.80 |
| 78 | dev | attack_db | 8.52 | 10.44 |
| 78 | train | attack_db | 8.46 | 10.37 |
| 54 | dev | noise_db | 8.91 | 10.65 |
| 78 | dev | early_db | 10.07 | 11.79 |
| 57 | dev | partial_db | 8.09 | 9.81 |
| 48 | dev | rise_ms | 6.74 | 10.09 |
| 57 | dev | attack_db | 7.14 | 8.76 |
| 57 | dev | early_db | 8.07 | 9.69 |
| 78 | train | early_db | 9.76 | 11.33 |
| 57 | dev | noise_db | 9.93 | 11.50 |
| 57 | train | partial_db | 7.87 | 9.42 |
| 54 | train | noise_db | 8.54 | 10.08 |
| 57 | train | early_db | 8.17 | 9.65 |
| 57 | train | attack_db | 7.22 | 8.70 |
| 90 | dev | rise_ms | 4.42 | 7.35 |
| 57 | dev | sustain_db | 7.88 | 9.32 |
| 72 | train | ild_db | 7.87 | 9.27 |
| 57 | train | noise_db | 11.03 | 12.43 |
| 57 | train | sustain_db | 7.86 | 9.25 |
| 54 | dev | partial_db | 4.79 | 6.13 |
| 72 | dev | ild_db | 8.07 | 9.41 |
| 78 | dev | noise_db | 6.27 | 7.61 |
| 78 | train | noise_db | 6.28 | 7.60 |
| 66 | dev | partial_db | 5.21 | 6.50 |
| 54 | train | partial_db | 4.72 | 5.97 |
| 57 | dev | level_db | 1.98 | 3.24 |
| 57 | train | level_db | 2.25 | 3.49 |
| 54 | dev | ild_db | 4.91 | 6.15 |
| 108 | train | icc | 0.25 | 0.30 |
| 54 | train | ild_db | 4.93 | 6.14 |
| 81 | train | ild_db | 7.34 | 8.52 |
| 54 | dev | level_db | 1.30 | 2.47 |
| 66 | train | partial_db | 5.35 | 6.50 |
| 90 | train | rise_ms | 5.08 | 7.35 |
| 54 | dev | sustain_db | 4.52 | 5.65 |
| 54 | train | sustain_db | 4.65 | 5.78 |
| 81 | dev | attack_db | 4.91 | 6.02 |
| 54 | dev | early_db | 3.95 | 4.95 |
| 81 | dev | sustain_db | 6.02 | 7.01 |
| 66 | dev | sustain_db | 3.56 | 4.55 |
| 81 | train | attack_db | 5.55 | 6.53 |
| 54 | train | early_db | 3.85 | 4.82 |
| 54 | train | level_db | 1.62 | 2.58 |
| 81 | dev | ild_db | 7.90 | 8.86 |
| 42 | train | rise_ms | 3.27 | 5.13 |
| 93 | train | rise_ms | 10.67 | 12.52 |
| 66 | train | sustain_db | 3.75 | 4.67 |
| 93 | dev | rise_ms | 10.74 | 12.48 |
| 81 | train | sustain_db | 6.59 | 7.43 |
| 99 | dev | ild_db | 1.40 | 2.17 |
| 24 | train | icc | 0.22 | 0.25 |
| 24 | dev | icc | 0.21 | 0.24 |
| 45 | dev | icc | 0.16 | 0.19 |
| 42 | train | ild_db | 5.22 | 5.88 |
| 42 | dev | ild_db | 5.18 | 5.79 |
| 45 | dev | rise_ms | 24.21 | 25.41 |
| 48 | train | level_db | 1.44 | 2.01 |
| 48 | dev | level_db | 1.44 | 2.01 |
| 54 | dev | attack_db | 4.74 | 5.27 |
| 45 | train | icc | 0.16 | 0.18 |
| 24 | dev | level_db | 4.02 | 4.52 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (23.6952 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 7.4093 | 7.5743 | 0.1650 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.2106 | 2.2208 | 0.0102 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 3.2854 | 3.3104 | 0.0249 | 0 | 0 | 1 |
| dev | attack_db | 156 | 6.3201 | 6.3353 | 0.0152 | 0 | 0 | 0 |
| dev | early_db | 156 | 5.9753 | 6.0124 | 0.0371 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 7.7820 | 7.8925 | 0.1105 | 0 | 0 | 0 |
| dev | noise_db | 153 | 6.8383 | 6.8389 | 0.0006 | 0 | 0 | 3 |
| dev | ild_db | 154 | 5.1540 | 4.9586 | -0.1954 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1942 | 0.1833 | -0.0109 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 4.0017 | 4.0252 | 0.0235 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 12.0743 | 11.9374 | -0.1369 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.6324 | 2.7027 | 0.0703 | 0 | 0 | 0 |
| train | partial_db | 276 | 7.7162 | 8.0744 | 0.3582 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.1169 | 2.1282 | 0.0113 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 3.9040 | 3.9245 | 0.0205 | 0 | 0 | 5 |
| train | attack_db | 276 | 6.5974 | 6.6988 | 0.1014 | 0 | 0 | 0 |
| train | early_db | 276 | 6.3990 | 6.4896 | 0.0905 | 0 | 0 | 0 |
| train | sustain_db | 276 | 8.5506 | 8.7177 | 0.1672 | 0 | 0 | 0 |
| train | noise_db | 272 | 7.1358 | 7.2141 | 0.0782 | 2 | 0 | 2 |
| train | ild_db | 270 | 5.0267 | 4.7876 | -0.2391 | 0 | 0 | 6 |
| train | icc | 270 | 0.2026 | 0.1970 | -0.0056 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.3162 | 4.3335 | 0.0173 | 0 | 0 | 0 |
| train | rise_ms | 276 | 13.3022 | 14.2329 | 0.9307 | 0 | 0 | 0 |
| train | level_db | 276 | 2.4373 | 2.4990 | 0.0618 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 24 | dev | rise_ms | 4 | 12.0417 | 34.9583 | 22.9167 |
| 24 | train | rise_ms | 12 | 11.9392 | 32.1215 | 20.1823 |
| 48 | train | rise_ms | 12 | 6.5417 | 17.8385 | 11.2969 |
| 66 | train | rise_ms | 12 | 13.3785 | 22.7691 | 9.3906 |
| 57 | train | rise_ms | 12 | 28.2934 | 37.6458 | 9.3524 |
| 57 | dev | rise_ms | 4 | 28.7135 | 35.4948 | 6.7812 |
| 96 | dev | ild_db | 4 | 0.5133 | 3.7370 | 3.2237 |
| 96 | train | ild_db | 12 | 0.5185 | 3.6305 | 3.1120 |
| 30 | dev | rise_ms | 4 | 11.2708 | 17.4479 | 6.1771 |
| 36 | train | rise_ms | 12 | 19.9774 | 25.3056 | 5.3281 |
| 78 | dev | partial_db | 4 | 10.1768 | 12.7621 | 2.5853 |
| 36 | dev | rise_ms | 4 | 21.1510 | 26.2292 | 5.0781 |
| 66 | dev | rise_ms | 4 | 16.2760 | 21.2969 | 5.0208 |
| 78 | train | partial_db | 12 | 9.5922 | 12.0896 | 2.4974 |
| 30 | train | rise_ms | 12 | 12.0295 | 16.8941 | 4.8646 |
| 48 | train | ild_db | 12 | 7.5049 | 9.8983 | 2.3934 |
| 81 | dev | partial_db | 4 | 4.6978 | 7.0839 | 2.3861 |
| 81 | train | partial_db | 12 | 4.4865 | 6.8275 | 2.3410 |
| 48 | dev | ild_db | 4 | 7.3647 | 9.6282 | 2.2634 |
| 78 | train | sustain_db | 12 | 10.0954 | 12.1702 | 2.0748 |
| 78 | dev | sustain_db | 4 | 10.7335 | 12.8031 | 2.0696 |
| 78 | dev | attack_db | 4 | 8.5231 | 10.4425 | 1.9194 |
| 78 | train | attack_db | 12 | 8.4632 | 10.3677 | 1.9045 |
| 54 | dev | noise_db | 4 | 8.9107 | 10.6482 | 1.7375 |
| 78 | dev | early_db | 4 | 10.0661 | 11.7850 | 1.7189 |
| 57 | dev | partial_db | 4 | 8.0906 | 9.8064 | 1.7157 |
| 48 | dev | rise_ms | 4 | 6.7396 | 10.0937 | 3.3542 |
| 57 | dev | attack_db | 4 | 7.1354 | 8.7633 | 1.6279 |
| 57 | dev | early_db | 4 | 8.0698 | 9.6851 | 1.6153 |
| 78 | train | early_db | 12 | 9.7556 | 11.3281 | 1.5726 |
| 57 | dev | noise_db | 4 | 9.9289 | 11.4996 | 1.5707 |
| 57 | train | partial_db | 12 | 7.8672 | 9.4215 | 1.5544 |
| 54 | train | noise_db | 12 | 8.5387 | 10.0811 | 1.5424 |
| 57 | train | early_db | 12 | 8.1674 | 9.6487 | 1.4812 |
| 57 | train | attack_db | 12 | 7.2243 | 8.7037 | 1.4795 |
| 90 | dev | rise_ms | 4 | 4.4167 | 7.3542 | 2.9375 |
| 57 | dev | sustain_db | 4 | 7.8823 | 9.3248 | 1.4424 |
| 72 | train | ild_db | 12 | 7.8697 | 9.2705 | 1.4008 |
| 57 | train | noise_db | 12 | 11.0298 | 12.4276 | 1.3978 |
| 57 | train | sustain_db | 12 | 7.8563 | 9.2464 | 1.3901 |
| 54 | dev | partial_db | 4 | 4.7867 | 6.1305 | 1.3439 |
| 72 | dev | ild_db | 4 | 8.0678 | 9.4059 | 1.3381 |
| 78 | dev | noise_db | 4 | 6.2740 | 7.6076 | 1.3336 |
| 78 | train | noise_db | 12 | 6.2844 | 7.5990 | 1.3146 |
| 66 | dev | partial_db | 4 | 5.2050 | 6.4954 | 1.2903 |
| 54 | train | partial_db | 12 | 4.7174 | 5.9724 | 1.2551 |
| 54 | dev | ild_db | 4 | 4.9094 | 6.1456 | 1.2363 |
| 108 | train | icc | 7 | 0.2536 | 0.3022 | 0.0486 |
| 54 | train | ild_db | 12 | 4.9265 | 6.1412 | 1.2147 |
| 81 | train | ild_db | 12 | 7.3360 | 8.5178 | 1.1818 |
| 66 | train | partial_db | 12 | 5.3492 | 6.4959 | 1.1467 |
| 90 | train | rise_ms | 12 | 5.0833 | 7.3542 | 2.2708 |
| 54 | dev | sustain_db | 4 | 4.5218 | 5.6472 | 1.1254 |
| 54 | train | sustain_db | 12 | 4.6498 | 5.7751 | 1.1254 |
| 81 | dev | attack_db | 4 | 4.9136 | 6.0194 | 1.1057 |
| 54 | dev | early_db | 4 | 3.9532 | 4.9490 | 0.9957 |
| 81 | dev | sustain_db | 4 | 6.0221 | 7.0111 | 0.9890 |
| 66 | dev | sustain_db | 4 | 3.5645 | 4.5477 | 0.9832 |
| 81 | train | attack_db | 12 | 5.5453 | 6.5283 | 0.9830 |
| 54 | train | early_db | 12 | 3.8472 | 4.8201 | 0.9729 |
| 81 | dev | ild_db | 4 | 7.9047 | 8.8553 | 0.9505 |
| 42 | train | rise_ms | 12 | 3.2691 | 5.1319 | 1.8628 |
| 93 | train | rise_ms | 12 | 10.6701 | 12.5243 | 1.8542 |
| 24 | dev | level_db | 4 | 4.0188 | 4.9325 | 0.9137 |
| 66 | train | sustain_db | 12 | 3.7531 | 4.6651 | 0.9120 |
| 24 | train | level_db | 12 | 4.3215 | 5.2181 | 0.8966 |
| 27 | dev | level_db | 16 | 4.1466 | 5.0388 | 0.8923 |
| 93 | dev | rise_ms | 4 | 10.7448 | 12.4792 | 1.7344 |
| 57 | dev | level_db | 4 | 1.9813 | 2.8270 | 0.8456 |
| 81 | train | sustain_db | 12 | 6.5874 | 7.4281 | 0.8407 |
| 57 | train | level_db | 12 | 2.2524 | 3.0864 | 0.8340 |
| 99 | dev | ild_db | 16 | 1.3955 | 2.1653 | 0.7698 |
| 54 | dev | level_db | 4 | 1.2972 | 2.0609 | 0.7637 |
| 24 | train | icc | 12 | 0.2158 | 0.2451 | 0.0293 |
| 24 | dev | icc | 4 | 0.2128 | 0.2411 | 0.0283 |
| 45 | dev | icc | 4 | 0.1603 | 0.1873 | 0.0269 |
| 30 | dev | level_db | 4 | 2.2112 | 2.8701 | 0.6589 |
| 21 | dev | level_db | 4 | 4.1456 | 4.8014 | 0.6558 |
| 78 | train | level_db | 12 | 3.3149 | 3.9705 | 0.6557 |
| 21 | train | level_db | 12 | 3.9488 | 4.6004 | 0.6516 |
| 42 | train | ild_db | 12 | 5.2248 | 5.8754 | 0.6505 |
| 54 | train | level_db | 12 | 1.6169 | 2.2349 | 0.6180 |
| 78 | dev | level_db | 4 | 3.3590 | 3.9713 | 0.6123 |
| 42 | dev | ild_db | 4 | 5.1804 | 5.7868 | 0.6065 |
| 45 | dev | rise_ms | 4 | 24.2135 | 25.4115 | 1.1979 |
| 30 | train | level_db | 12 | 2.2939 | 2.8737 | 0.5797 |
| 75 | dev | level_db | 16 | 2.6050 | 3.1768 | 0.5717 |
| 54 | dev | attack_db | 4 | 4.7422 | 5.2704 | 0.5282 |
| 45 | train | icc | 12 | 0.1582 | 0.1786 | 0.0204 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| C2v2 | 36 | train | noise_db | lost | 6.9328 | - |
| F#1v5 | 30 | train | noise_db | lost | 2.6099 | - |
