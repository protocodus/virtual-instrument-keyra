# Recording benchmark: candidate 2.1.0 against shipping 2.0.0

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## shipping 2.0.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 9.81 | 4.37 | 5.78 | 8.86 | 11.13 | 11.36 | 11.23 | 6.43 | 0.25 | 4.95 | 16.45 | 5.14 |
| dev (21) | 8.81 | 6.12 | 5.34 | 7.73 | 9.70 | 9.87 | 10.38 | 5.00 | 0.26 | 5.21 | 12.22 | 4.06 |
| train / bass A0-B2 (30) | 9.08 | 4.90 | 5.12 | 6.70 | 8.35 | 9.44 | 12.22 | 5.83 | 0.22 | 3.12 | 24.09 | 2.92 |
| train / middle C3-B5 (69) | 8.97 | 4.02 | 4.37 | 8.13 | 9.51 | 9.27 | 9.36 | 6.64 | 0.19 | 4.31 | 19.42 | 4.48 |
| train / treble C6-C8 (38) | 11.90 | 4.61 | 9.03 | 11.90 | 16.28 | 16.67 | 13.71 | 6.53 | 0.39 | 7.54 | 5.00 | 8.09 |
| dev / bass A0-B2 (5) | 8.71 | 5.17 | 3.82 | 6.23 | 8.08 | 9.83 | 12.19 | 4.55 | 0.25 | 3.02 | 24.65 | 4.70 |
| dev / middle C3-B5 (11) | 8.42 | 5.11 | 5.36 | 7.14 | 8.21 | 8.84 | 8.71 | 6.17 | 0.21 | 5.30 | 10.60 | 1.90 |
| dev / treble C6-C8 (5) | 9.78 | 9.31 | 6.81 | 10.53 | 14.59 | 12.14 | 12.62 | 2.89 | 0.38 | 7.20 | 3.35 | 8.14 |

## candidate 2.1.0

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

## Independent-sample regressions (legacy)

Every note and role where candidate 2.1.0 is worse than shipping 2.0.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | shipping 2.0.0 | candidate 2.1.0 |
|---|---|---|---|---|
| 59 | dev | level_db | 0.08 | 5.87 |
| 24 | train | noise_db | 13.73 | 18.47 |
| 39 | dev | noise_db | 12.19 | 16.35 |
| 88 | dev | sustain_db | 12.14 | 15.90 |
| 27 | train | noise_db | 16.43 | 19.85 |
| 100 | train | sustain_db | 16.59 | 19.84 |
| 94 | train | rise_ms | 0.83 | 7.28 |
| 86 | train | sustain_db | 10.50 | 13.66 |
| 27 | train | level_db | 1.80 | 4.81 |
| 82 | train | level_db | 1.87 | 4.74 |
| 84 | train | level_db | 2.56 | 5.43 |
| 33 | train | noise_db | 13.39 | 16.21 |
| 48 | train | level_db | 3.63 | 6.26 |
| 45 | train | noise_db | 11.40 | 13.84 |
| 86 | train | level_db | 2.15 | 4.50 |
| 96 | train | ild_db | 5.16 | 7.50 |
| 45 | train | level_db | 1.75 | 4.09 |
| 48 | train | noise_db | 12.42 | 14.70 |
| 36 | train | noise_db | 8.47 | 10.74 |
| 68 | train | level_db | 3.53 | 5.73 |
| 84 | train | ild_db | 5.78 | 7.93 |
| 78 | train | noise_db | 11.25 | 13.33 |
| 74 | train | envelope_db | 5.70 | 7.68 |
| 86 | train | attack_db | 8.79 | 10.76 |
| 72 | dev | level_db | 1.38 | 3.25 |
| 24 | train | early_db | 8.83 | 10.63 |
| 52 | train | noise_db | 7.27 | 9.06 |
| 24 | train | level_db | 1.58 | 3.27 |
| 84 | train | attack_db | 9.55 | 11.21 |
| 60 | train | level_db | 4.11 | 5.77 |
| 92 | train | sustain_db | 14.12 | 15.77 |
| 45 | train | attack_db | 8.00 | 9.63 |
| 39 | dev | attack_db | 6.23 | 7.82 |
| 42 | train | attack_db | 5.44 | 6.95 |
| 84 | train | noise_db | 11.15 | 12.63 |
| 86 | train | noise_db | 9.95 | 11.43 |
| 74 | train | rise_ms | 8.35 | 11.29 |
| 39 | dev | early_db | 8.08 | 9.51 |
| 90 | train | tuning_cents | 3.96 | 5.38 |
| 86 | train | envelope_db | 6.62 | 8.03 |
| 76 | train | sustain_db | 10.96 | 12.36 |
| 100 | train | envelope_db | 5.58 | 6.98 |
| 27 | train | early_db | 9.41 | 10.81 |
| 54 | train | noise_db | 7.99 | 9.39 |
| 33 | train | sustain_db | 9.36 | 10.72 |
| 42 | train | noise_db | 9.92 | 11.28 |
| 45 | train | early_db | 8.86 | 10.22 |
| 33 | train | attack_db | 7.76 | 9.11 |
| 48 | train | early_db | 8.79 | 10.13 |
| 94 | train | attack_db | 12.50 | 13.82 |
| 82 | train | attack_db | 6.88 | 8.19 |
| 48 | train | attack_db | 8.19 | 9.50 |
| 33 | train | early_db | 8.73 | 10.00 |
| 62 | train | level_db | 3.04 | 4.29 |
| 50 | train | noise_db | 6.00 | 7.24 |
| 78 | train | attack_db | 10.74 | 11.98 |
| 92 | train | attack_db | 12.02 | 13.25 |
| 50 | train | level_db | 1.65 | 2.86 |
| 103 | train | attack_db | 15.84 | 17.03 |
| 45 | train | partial_db | 7.96 | 9.15 |
| 68 | train | partial_db | 7.11 | 8.29 |
| 74 | train | sustain_db | 9.48 | 10.63 |
| 33 | train | rise_ms | 9.32 | 11.58 |
| 88 | dev | attack_db | 10.53 | 11.66 |
| 60 | train | icc | 0.13 | 0.17 |
| 92 | train | early_db | 16.67 | 17.76 |
| 90 | train | ild_db | 5.15 | 6.24 |
| 60 | train | partial_db | 9.49 | 10.55 |
| 56 | dev | attack_db | 6.47 | 7.51 |
| 82 | train | noise_db | 8.51 | 9.54 |
| 48 | train | partial_db | 7.91 | 8.93 |
| 24 | train | sustain_db | 13.54 | 14.55 |
| 76 | train | partial_db | 7.29 | 8.30 |
| 100 | train | ild_db | 4.32 | 5.32 |
| 86 | train | decay_db_s | 2.07 | 4.06 |
| 66 | train | level_db | 4.49 | 5.49 |
| 92 | train | rise_ms | 2.57 | 4.53 |
| 42 | train | early_db | 4.36 | 5.31 |
| 60 | train | ild_db | 7.04 | 7.98 |
| 88 | dev | decay_db_s | 6.81 | 8.69 |
| 70 | train | level_db | 2.23 | 3.15 |
| 78 | train | level_db | 7.72 | 8.64 |
| 45 | train | sustain_db | 7.46 | 8.37 |
| 56 | dev | noise_db | 9.17 | 10.08 |
| 36 | train | early_db | 9.91 | 10.79 |
| 103 | train | early_db | 19.81 | 20.69 |
| 58 | train | envelope_db | 3.18 | 4.05 |
| 88 | dev | rise_ms | 3.35 | 5.06 |
| 100 | train | tuning_cents | 3.71 | 4.55 |
| 60 | train | sustain_db | 8.54 | 9.37 |
| 56 | dev | early_db | 6.65 | 7.45 |
| 76 | train | icc | 0.16 | 0.19 |
| 84 | train | tuning_cents | 3.36 | 4.13 |
| 86 | train | early_db | 12.76 | 13.53 |
| 78 | train | ild_db | 12.24 | 13.00 |
| 103 | train | noise_db | 16.22 | 16.95 |
| 74 | train | decay_db_s | 4.17 | 5.62 |
| 27 | train | sustain_db | 13.20 | 13.90 |
| 36 | train | attack_db | 6.90 | 7.59 |
| 27 | train | attack_db | 5.86 | 6.53 |
| 42 | train | sustain_db | 5.38 | 6.02 |
| 48 | train | sustain_db | 7.55 | 8.16 |
| 58 | train | level_db | 3.01 | 3.60 |
| 56 | dev | ild_db | 7.02 | 7.60 |
| 48 | train | ild_db | 4.90 | 5.44 |
| 42 | train | level_db | 3.07 | 3.60 |
| 60 | train | attack_db | 9.60 | 10.13 |
| 24 | train | attack_db | 6.23 | 6.75 |
| 68 | train | tuning_cents | 5.22 | 5.72 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.6337 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 8.8098 | 8.3899 | -0.4199 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 6.1240 | 4.6628 | -1.4612 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 5.3375 | 5.5495 | 0.2119 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.7316 | 8.5424 | 0.8108 | 0 | 0 | 0 |
| dev | early_db | 21 | 9.7000 | 10.2033 | 0.5033 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 9.8656 | 10.7721 | 0.9065 | 0 | 0 | 0 |
| dev | noise_db | 20 | 10.3837 | 11.0123 | 0.6287 | 0 | 0 | 1 |
| dev | ild_db | 21 | 5.0024 | 5.0243 | 0.0219 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2608 | 0.2621 | 0.0013 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 5.2096 | 4.7261 | -0.4834 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 12.2222 | 12.6310 | 0.4087 | 0 | 0 | 0 |
| dev | level_db | 21 | 4.0563 | 3.0498 | -1.0065 | 0 | 0 | 0 |
| train | partial_db | 137 | 9.8067 | 8.6944 | -1.1123 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 4.3720 | 4.0853 | -0.2867 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 5.7781 | 5.1091 | -0.6691 | 0 | 0 | 2 |
| train | attack_db | 137 | 8.8594 | 9.2052 | 0.3458 | 0 | 0 | 0 |
| train | early_db | 137 | 11.1315 | 11.2434 | 0.1119 | 0 | 0 | 0 |
| train | sustain_db | 137 | 11.3619 | 11.3676 | 0.0056 | 0 | 0 | 0 |
| train | noise_db | 133 | 11.2259 | 11.8145 | 0.5886 | 1 | 1 | 2 |
| train | ild_db | 135 | 6.4281 | 6.6572 | 0.2291 | 0 | 0 | 2 |
| train | icc | 135 | 0.2511 | 0.2522 | 0.0011 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.9452 | 4.4313 | -0.5139 | 0 | 0 | 0 |
| train | rise_ms | 137 | 16.4451 | 16.0376 | -0.4075 | 0 | 0 | 0 |
| train | level_db | 137 | 5.1427 | 5.1376 | -0.0051 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 24 | train | noise_db | 5 | 13.7279 | 18.4686 | 4.7407 |
| 59 | dev | level_db | 1 | 0.0752 | 4.4998 | 4.4246 |
| 82 | train | level_db | 5 | 1.8701 | 6.1045 | 4.2344 |
| 39 | dev | noise_db | 4 | 12.1874 | 16.3496 | 4.1622 |
| 88 | dev | sustain_db | 5 | 12.1419 | 15.8990 | 3.7571 |
| 86 | train | level_db | 5 | 2.1510 | 5.8696 | 3.7186 |
| 84 | train | level_db | 5 | 2.5644 | 6.2499 | 3.6855 |
| 27 | train | noise_db | 5 | 16.4303 | 19.8528 | 3.4225 |
| 100 | train | sustain_db | 4 | 16.5883 | 19.8407 | 3.2524 |
| 36 | train | noise_db | 4 | 7.5121 | 10.7449 | 3.2328 |
| 94 | train | rise_ms | 5 | 0.8333 | 7.2833 | 6.4500 |
| 86 | train | sustain_db | 5 | 10.4972 | 13.6622 | 3.1651 |
| 33 | train | noise_db | 5 | 13.3895 | 16.2116 | 2.8221 |
| 45 | train | noise_db | 5 | 11.3970 | 13.8427 | 2.4457 |
| 96 | train | ild_db | 5 | 5.1607 | 7.4986 | 2.3379 |
| 78 | train | level_db | 5 | 7.7158 | 10.0082 | 2.2924 |
| 48 | train | noise_db | 5 | 12.4173 | 14.6979 | 2.2806 |
| 68 | train | level_db | 5 | 3.5280 | 5.7567 | 2.2288 |
| 27 | train | level_db | 5 | 1.8035 | 3.9883 | 2.1848 |
| 84 | train | ild_db | 5 | 5.7819 | 7.9322 | 2.1502 |
| 78 | train | noise_db | 5 | 11.2503 | 13.3270 | 2.0767 |
| 45 | train | level_db | 5 | 1.7503 | 3.8124 | 2.0621 |
| 74 | train | envelope_db | 5 | 5.6998 | 7.6849 | 1.9851 |
| 86 | train | attack_db | 5 | 8.7853 | 10.7574 | 1.9720 |
| 24 | train | level_db | 5 | 1.5768 | 3.4006 | 1.8239 |
| 24 | train | early_db | 5 | 8.8308 | 10.6256 | 1.7948 |
| 52 | train | noise_db | 5 | 7.2743 | 9.0589 | 1.7846 |
| 84 | train | attack_db | 5 | 9.5522 | 11.2132 | 1.6610 |
| 92 | train | sustain_db | 5 | 14.1159 | 15.7721 | 1.6562 |
| 45 | train | attack_db | 5 | 7.9980 | 9.6309 | 1.6329 |
| 72 | dev | level_db | 5 | 1.3778 | 2.9783 | 1.6005 |
| 39 | dev | attack_db | 5 | 6.2289 | 7.8195 | 1.5907 |
| 62 | train | level_db | 5 | 3.0416 | 4.5632 | 1.5216 |
| 42 | train | attack_db | 5 | 5.4390 | 6.9461 | 1.5071 |
| 84 | train | noise_db | 5 | 11.1544 | 12.6327 | 1.4782 |
| 86 | train | noise_db | 5 | 9.9504 | 11.4281 | 1.4777 |
| 74 | train | rise_ms | 5 | 8.3500 | 11.2917 | 2.9417 |
| 39 | dev | early_db | 5 | 8.0785 | 9.5050 | 1.4265 |
| 50 | train | level_db | 5 | 1.6462 | 3.0710 | 1.4247 |
| 66 | train | level_db | 5 | 4.4904 | 5.9133 | 1.4229 |
| 90 | train | tuning_cents | 5 | 3.9644 | 5.3791 | 1.4147 |
| 86 | train | envelope_db | 5 | 6.6237 | 8.0334 | 1.4097 |
| 76 | train | sustain_db | 5 | 10.9579 | 12.3640 | 1.4061 |
| 100 | train | envelope_db | 4 | 5.5826 | 6.9814 | 1.3988 |
| 27 | train | early_db | 5 | 9.4078 | 10.8062 | 1.3984 |
| 54 | train | noise_db | 5 | 7.9949 | 9.3855 | 1.3906 |
| 33 | train | sustain_db | 5 | 9.3618 | 10.7247 | 1.3629 |
| 42 | train | noise_db | 5 | 9.9154 | 11.2759 | 1.3605 |
| 45 | train | early_db | 5 | 8.8578 | 10.2170 | 1.3592 |
| 33 | train | attack_db | 5 | 7.7558 | 9.1100 | 1.3542 |
| 48 | train | early_db | 5 | 8.7901 | 10.1320 | 1.3419 |
| 94 | train | attack_db | 5 | 12.5022 | 13.8248 | 1.3226 |
| 82 | train | attack_db | 5 | 6.8791 | 8.1892 | 1.3102 |
| 48 | train | attack_db | 5 | 8.1883 | 9.4961 | 1.3077 |
| 92 | train | level_db | 5 | 4.4717 | 5.7667 | 1.2950 |
| 58 | train | level_db | 4 | 3.0095 | 4.2804 | 1.2708 |
| 48 | train | level_db | 5 | 3.6251 | 4.8896 | 1.2645 |
| 33 | train | early_db | 5 | 8.7311 | 9.9951 | 1.2640 |
| 78 | train | attack_db | 5 | 10.7431 | 11.9770 | 1.2339 |
| 92 | train | attack_db | 5 | 12.0245 | 13.2529 | 1.2285 |
| 103 | train | attack_db | 4 | 15.8384 | 17.0267 | 1.1883 |
| 45 | train | partial_db | 5 | 7.9584 | 9.1454 | 1.1870 |
| 68 | train | partial_db | 5 | 7.1078 | 8.2901 | 1.1823 |
| 74 | train | sustain_db | 5 | 9.4787 | 10.6349 | 1.1562 |
| 33 | train | rise_ms | 5 | 9.3250 | 11.5833 | 2.2583 |
| 88 | dev | attack_db | 5 | 10.5331 | 11.6581 | 1.1250 |
| 60 | train | icc | 5 | 0.1271 | 0.1714 | 0.0444 |
| 92 | train | early_db | 5 | 16.6730 | 17.7607 | 1.0877 |
| 90 | train | ild_db | 5 | 5.1532 | 6.2381 | 1.0848 |
| 60 | train | partial_db | 5 | 9.4889 | 10.5525 | 1.0635 |
| 56 | dev | attack_db | 5 | 6.4683 | 7.5117 | 1.0433 |
| 82 | train | noise_db | 5 | 8.5128 | 9.5360 | 1.0232 |
| 70 | train | level_db | 5 | 2.2281 | 3.2492 | 1.0211 |
| 48 | train | partial_db | 5 | 7.9116 | 8.9294 | 1.0177 |
| 24 | train | sustain_db | 5 | 13.5407 | 14.5510 | 1.0104 |
| 76 | train | partial_db | 5 | 7.2911 | 8.3008 | 1.0097 |
| 100 | train | ild_db | 3 | 4.3227 | 5.3223 | 0.9996 |
| 86 | train | decay_db_s | 5 | 2.0677 | 4.0636 | 1.9958 |
| 92 | train | rise_ms | 5 | 2.5708 | 4.5292 | 1.9583 |
| 42 | train | early_db | 5 | 4.3555 | 5.3063 | 0.9508 |
| 60 | train | ild_db | 5 | 7.0383 | 7.9801 | 0.9418 |
| 88 | dev | decay_db_s | 5 | 6.8095 | 8.6852 | 1.8757 |
| 45 | train | sustain_db | 5 | 7.4560 | 8.3706 | 0.9146 |
| 56 | dev | noise_db | 5 | 9.1743 | 10.0820 | 0.9078 |
| 36 | train | early_db | 5 | 9.9072 | 10.7890 | 0.8818 |
| 103 | train | early_db | 4 | 19.8091 | 20.6877 | 0.8786 |
| 58 | train | envelope_db | 4 | 3.1799 | 4.0506 | 0.8708 |
| 88 | dev | rise_ms | 5 | 3.3542 | 5.0583 | 1.7042 |
| 100 | train | tuning_cents | 4 | 3.7123 | 4.5535 | 0.8412 |
| 60 | train | sustain_db | 5 | 8.5425 | 9.3672 | 0.8247 |
| 42 | train | level_db | 5 | 3.0661 | 3.8726 | 0.8065 |
| 56 | dev | early_db | 5 | 6.6542 | 7.4485 | 0.7944 |
| 76 | train | icc | 5 | 0.1594 | 0.1905 | 0.0312 |
| 84 | train | tuning_cents | 5 | 3.3595 | 4.1334 | 0.7739 |
| 86 | train | early_db | 5 | 12.7634 | 13.5265 | 0.7631 |
| 78 | train | ild_db | 5 | 12.2418 | 13.0010 | 0.7593 |
| 103 | train | noise_db | 4 | 16.2178 | 16.9511 | 0.7333 |
| 74 | train | decay_db_s | 5 | 4.1734 | 5.6212 | 1.4479 |
| 27 | train | sustain_db | 5 | 13.1980 | 13.8999 | 0.7019 |
| 36 | train | attack_db | 5 | 6.9037 | 7.5912 | 0.6875 |
| 27 | train | attack_db | 5 | 5.8585 | 6.5263 | 0.6678 |
| 42 | train | sustain_db | 5 | 5.3792 | 6.0234 | 0.6442 |
| 48 | train | sustain_db | 5 | 7.5461 | 8.1602 | 0.6140 |
| 56 | dev | level_db | 5 | 2.7977 | 3.4069 | 0.6092 |
| 56 | dev | ild_db | 5 | 7.0167 | 7.5969 | 0.5802 |
| 48 | train | ild_db | 5 | 4.9030 | 5.4434 | 0.5405 |
| 60 | train | attack_db | 5 | 9.6044 | 10.1346 | 0.5302 |
| 24 | train | attack_db | 5 | 6.2283 | 6.7532 | 0.5249 |
| 68 | train | tuning_cents | 5 | 5.2203 | 5.7209 | 0.5005 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| n36v1r1 | 36 | train | noise_db | lost | 12.3228 | - |
| n50v2r1 | 50 | train | noise_db | gained | - | 11.0494 |
