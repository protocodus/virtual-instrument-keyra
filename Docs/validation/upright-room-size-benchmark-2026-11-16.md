# Recording benchmark: 2.18.0 against 2.17.0

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.17.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.36 | 3.56 | 4.51 | 7.37 | 8.78 | 10.34 | 9.81 | 6.22 | 0.23 | 4.26 | 12.48 | 4.25 |
| dev (21) | 7.10 | 3.66 | 4.89 | 7.40 | 8.71 | 9.83 | 8.51 | 6.66 | 0.25 | 4.60 | 9.09 | 3.39 |
| train / bass A0-B2 (30) | 9.71 | 4.94 | 4.31 | 8.36 | 9.09 | 10.30 | 15.33 | 6.62 | 0.19 | 2.99 | 7.28 | 3.70 |
| train / middle C3-B5 (69) | 7.26 | 2.85 | 4.31 | 7.21 | 8.02 | 8.11 | 8.72 | 5.73 | 0.20 | 3.80 | 19.16 | 4.69 |
| train / treble C6-C8 (38) | 5.69 | 3.75 | 5.05 | 6.89 | 9.93 | 14.44 | 7.42 | 6.82 | 0.32 | 6.11 | 4.47 | 3.89 |
| dev / bass A0-B2 (5) | 9.35 | 3.56 | 2.89 | 9.08 | 10.03 | 10.45 | 12.62 | 4.65 | 0.27 | 2.00 | 1.89 | 2.59 |
| dev / middle C3-B5 (11) | 6.14 | 2.52 | 4.45 | 6.80 | 7.36 | 7.97 | 7.18 | 7.95 | 0.21 | 4.75 | 14.57 | 3.80 |
| dev / treble C6-C8 (5) | 6.97 | 6.28 | 7.83 | 7.05 | 10.34 | 13.29 | 7.32 | 5.82 | 0.33 | 6.88 | 4.22 | 3.28 |

## 2.18.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.29 | 3.22 | 4.62 | 7.69 | 9.13 | 10.44 | 10.15 | 6.56 | 0.24 | 4.25 | 11.83 | 4.31 |
| dev (21) | 7.24 | 3.71 | 5.00 | 7.52 | 8.95 | 9.89 | 8.73 | 6.49 | 0.27 | 4.64 | 9.11 | 3.26 |
| train / bass A0-B2 (30) | 9.57 | 4.85 | 4.45 | 8.60 | 9.37 | 10.34 | 15.58 | 6.48 | 0.19 | 2.89 | 6.82 | 3.67 |
| train / middle C3-B5 (69) | 7.07 | 2.73 | 4.44 | 7.42 | 8.22 | 8.20 | 8.99 | 6.29 | 0.20 | 3.77 | 18.08 | 4.72 |
| train / treble C6-C8 (38) | 5.87 | 2.83 | 5.11 | 7.46 | 10.59 | 14.60 | 7.98 | 7.13 | 0.37 | 6.20 | 4.45 | 4.08 |
| dev / bass A0-B2 (5) | 9.66 | 3.40 | 2.93 | 8.97 | 10.01 | 10.42 | 12.68 | 4.56 | 0.30 | 2.10 | 1.99 | 2.43 |
| dev / middle C3-B5 (11) | 6.26 | 2.38 | 4.63 | 6.78 | 7.38 | 8.04 | 7.08 | 7.64 | 0.22 | 4.76 | 14.56 | 3.62 |
| dev / treble C6-C8 (5) | 6.98 | 6.94 | 7.89 | 7.72 | 11.33 | 13.44 | 8.39 | 5.90 | 0.35 | 6.89 | 4.22 | 3.27 |

## Independent-sample regressions (legacy)

Every note and role where 2.18.0 is worse than 2.17.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.17.0 | 2.18.0 |
|---|---|---|---|---|
| 100 | train | ild_db | 5.69 | 10.44 |
| 103 | train | icc | 0.33 | 0.50 |
| 76 | train | ild_db | 3.58 | 6.30 |
| 96 | train | icc | 0.23 | 0.33 |
| 90 | train | icc | 0.12 | 0.19 |
| 48 | train | ild_db | 5.89 | 7.48 |
| 92 | train | icc | 0.42 | 0.48 |
| 103 | train | noise_db | 9.25 | 10.72 |
| 76 | train | partial_db | 7.76 | 9.21 |
| 84 | train | noise_db | 6.97 | 8.38 |
| 103 | train | attack_db | 7.95 | 9.26 |
| 82 | train | noise_db | 6.50 | 7.77 |
| 76 | train | sustain_db | 10.77 | 12.00 |
| 59 | dev | decay_db_s | 7.54 | 9.98 |
| 84 | train | early_db | 8.97 | 10.16 |
| 42 | train | early_db | 5.73 | 6.89 |
| 62 | train | ild_db | 7.79 | 8.94 |
| 78 | train | noise_db | 10.33 | 11.41 |
| 88 | dev | noise_db | 7.32 | 8.39 |
| 82 | train | ild_db | 7.61 | 8.65 |
| 90 | train | noise_db | 7.92 | 8.94 |
| 90 | train | early_db | 10.32 | 11.34 |
| 94 | train | ild_db | 7.08 | 8.09 |
| 88 | dev | early_db | 10.34 | 11.33 |
| 82 | train | early_db | 7.88 | 8.83 |
| 92 | train | early_db | 9.61 | 10.55 |
| 42 | train | rise_ms | 6.37 | 8.26 |
| 100 | train | icc | 0.26 | 0.29 |
| 76 | train | attack_db | 8.63 | 9.54 |
| 62 | train | rise_ms | 11.02 | 12.85 |
| 54 | train | noise_db | 12.09 | 13.00 |
| 78 | train | ild_db | 8.20 | 9.09 |
| 42 | train | noise_db | 13.82 | 14.71 |
| 42 | train | attack_db | 8.05 | 8.94 |
| 39 | dev | icc | 0.27 | 0.30 |
| 103 | train | early_db | 10.37 | 11.22 |
| 103 | train | level_db | 4.36 | 5.20 |
| 48 | train | icc | 0.12 | 0.15 |
| 86 | train | early_db | 8.68 | 9.52 |
| 76 | train | icc | 0.19 | 0.22 |
| 84 | train | attack_db | 6.74 | 7.50 |
| 86 | train | noise_db | 6.21 | 6.91 |
| 92 | train | noise_db | 6.74 | 7.43 |
| 78 | train | tuning_cents | 3.16 | 3.84 |
| 88 | dev | attack_db | 7.05 | 7.72 |
| 100 | train | partial_db | 4.93 | 5.59 |
| 88 | dev | tuning_cents | 6.28 | 6.94 |
| 86 | train | attack_db | 5.74 | 6.37 |
| 96 | train | partial_db | 5.94 | 6.56 |
| 88 | dev | icc | 0.33 | 0.35 |
| 78 | train | attack_db | 7.93 | 8.53 |
| 59 | dev | partial_db | 9.96 | 10.55 |
| 90 | train | attack_db | 8.06 | 8.63 |
| 76 | train | early_db | 10.02 | 10.58 |
| 50 | train | ild_db | 3.84 | 4.40 |
| 56 | dev | icc | 0.18 | 0.20 |
| 92 | train | attack_db | 6.88 | 7.42 |
| 96 | train | sustain_db | 13.06 | 13.59 |
| 82 | train | attack_db | 5.88 | 6.40 |
| 36 | train | icc | 0.22 | 0.24 |
| 48 | train | attack_db | 8.87 | 9.39 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.3213 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 7.1014 | 7.2422 | 0.1408 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 3.6623 | 3.7067 | 0.0444 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 4.8877 | 5.0003 | 0.1127 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.4022 | 7.5245 | 0.1223 | 0 | 0 | 0 |
| dev | early_db | 21 | 8.7069 | 8.9479 | 0.2410 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 9.8281 | 9.8940 | 0.0659 | 0 | 0 | 0 |
| dev | noise_db | 21 | 8.5084 | 8.7274 | 0.2190 | 0 | 0 | 0 |
| dev | ild_db | 21 | 6.6569 | 6.4889 | -0.1680 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2548 | 0.2731 | 0.0183 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.6032 | 4.6365 | 0.0333 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 9.0873 | 9.1071 | 0.0198 | 0 | 0 | 0 |
| dev | level_db | 21 | 3.3907 | 3.3659 | -0.0248 | 0 | 0 | 0 |
| train | partial_db | 137 | 7.3611 | 7.2855 | -0.0756 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 3.5605 | 3.2199 | -0.3406 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 4.5079 | 4.6226 | 0.1147 | 0 | 0 | 2 |
| train | attack_db | 137 | 7.3721 | 7.6862 | 0.3140 | 0 | 0 | 0 |
| train | early_db | 137 | 8.7814 | 9.1282 | 0.3468 | 0 | 0 | 0 |
| train | sustain_db | 137 | 10.3436 | 10.4434 | 0.0998 | 0 | 0 | 0 |
| train | noise_db | 137 | 9.8051 | 10.1538 | 0.3487 | 0 | 0 | 0 |
| train | ild_db | 135 | 6.2159 | 6.5574 | 0.3415 | 0 | 0 | 2 |
| train | icc | 135 | 0.2266 | 0.2424 | 0.0158 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.2618 | 4.2511 | -0.0106 | 0 | 0 | 0 |
| train | rise_ms | 137 | 12.4842 | 11.8324 | -0.6518 | 0 | 0 | 0 |
| train | level_db | 137 | 4.2510 | 4.3051 | 0.0542 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 100 | train | ild_db | 3 | 5.6859 | 10.4375 | 4.7516 |
| 103 | train | icc | 3 | 0.3251 | 0.4997 | 0.1746 |
| 76 | train | ild_db | 5 | 3.5773 | 6.2951 | 2.7177 |
| 96 | train | icc | 5 | 0.2263 | 0.3317 | 0.1054 |
| 90 | train | icc | 5 | 0.1224 | 0.1874 | 0.0650 |
| 48 | train | ild_db | 5 | 5.8949 | 7.4789 | 1.5840 |
| 92 | train | icc | 5 | 0.4171 | 0.4778 | 0.0607 |
| 103 | train | noise_db | 4 | 9.2513 | 10.7177 | 1.4665 |
| 76 | train | partial_db | 5 | 7.7561 | 9.2108 | 1.4547 |
| 84 | train | noise_db | 5 | 6.9678 | 8.3778 | 1.4100 |
| 103 | train | attack_db | 4 | 7.9507 | 9.2588 | 1.3081 |
| 82 | train | noise_db | 5 | 6.5027 | 7.7694 | 1.2666 |
| 76 | train | sustain_db | 5 | 10.7679 | 11.9977 | 1.2298 |
| 59 | dev | decay_db_s | 1 | 7.5376 | 9.9766 | 2.4391 |
| 84 | train | early_db | 5 | 8.9736 | 10.1588 | 1.1852 |
| 42 | train | early_db | 5 | 5.7259 | 6.8928 | 1.1669 |
| 62 | train | ild_db | 5 | 7.7895 | 8.9390 | 1.1495 |
| 78 | train | noise_db | 5 | 10.3318 | 11.4133 | 1.0815 |
| 88 | dev | noise_db | 5 | 7.3209 | 8.3926 | 1.0717 |
| 82 | train | ild_db | 5 | 7.6136 | 8.6530 | 1.0395 |
| 90 | train | noise_db | 5 | 7.9194 | 8.9399 | 1.0205 |
| 90 | train | early_db | 5 | 10.3171 | 11.3365 | 1.0195 |
| 94 | train | ild_db | 5 | 7.0774 | 8.0859 | 1.0086 |
| 88 | dev | early_db | 5 | 10.3403 | 11.3260 | 0.9857 |
| 82 | train | early_db | 5 | 7.8804 | 8.8274 | 0.9470 |
| 92 | train | early_db | 5 | 9.6088 | 10.5547 | 0.9459 |
| 42 | train | rise_ms | 5 | 6.3750 | 8.2583 | 1.8833 |
| 96 | train | level_db | 5 | 3.4261 | 4.3528 | 0.9267 |
| 100 | train | icc | 3 | 0.2558 | 0.2925 | 0.0368 |
| 76 | train | attack_db | 5 | 8.6263 | 9.5442 | 0.9179 |
| 62 | train | rise_ms | 5 | 11.0208 | 12.8542 | 1.8333 |
| 54 | train | noise_db | 5 | 12.0925 | 12.9982 | 0.9057 |
| 78 | train | ild_db | 5 | 8.1990 | 9.0938 | 0.8948 |
| 42 | train | noise_db | 5 | 13.8190 | 14.7054 | 0.8865 |
| 42 | train | attack_db | 5 | 8.0547 | 8.9400 | 0.8852 |
| 39 | dev | icc | 5 | 0.2688 | 0.3034 | 0.0345 |
| 103 | train | early_db | 4 | 10.3748 | 11.2219 | 0.8471 |
| 48 | train | icc | 5 | 0.1197 | 0.1534 | 0.0337 |
| 86 | train | early_db | 5 | 8.6831 | 9.5224 | 0.8393 |
| 76 | train | icc | 5 | 0.1910 | 0.2233 | 0.0323 |
| 84 | train | attack_db | 5 | 6.7403 | 7.5028 | 0.7625 |
| 86 | train | noise_db | 5 | 6.2113 | 6.9104 | 0.6991 |
| 92 | train | noise_db | 5 | 6.7402 | 7.4349 | 0.6947 |
| 78 | train | tuning_cents | 5 | 3.1566 | 3.8448 | 0.6881 |
| 88 | dev | attack_db | 5 | 7.0528 | 7.7243 | 0.6715 |
| 100 | train | partial_db | 4 | 4.9332 | 5.5875 | 0.6544 |
| 88 | dev | tuning_cents | 5 | 6.2823 | 6.9364 | 0.6542 |
| 103 | train | level_db | 4 | 4.3576 | 4.9884 | 0.6308 |
| 86 | train | attack_db | 5 | 5.7450 | 6.3662 | 0.6212 |
| 96 | train | partial_db | 5 | 5.9440 | 6.5552 | 0.6112 |
| 88 | dev | icc | 5 | 0.3287 | 0.3527 | 0.0241 |
| 78 | train | attack_db | 5 | 7.9289 | 8.5298 | 0.6009 |
| 59 | dev | partial_db | 1 | 9.9592 | 10.5499 | 0.5907 |
| 90 | train | attack_db | 5 | 8.0638 | 8.6295 | 0.5657 |
| 76 | train | early_db | 5 | 10.0157 | 10.5792 | 0.5635 |
| 50 | train | ild_db | 5 | 3.8421 | 4.4003 | 0.5581 |
| 56 | dev | icc | 5 | 0.1788 | 0.2006 | 0.0218 |
| 92 | train | attack_db | 5 | 6.8802 | 7.4212 | 0.5410 |
| 96 | train | sustain_db | 5 | 13.0623 | 13.5880 | 0.5257 |
| 82 | train | attack_db | 5 | 5.8817 | 6.4018 | 0.5201 |
| 36 | train | icc | 5 | 0.2153 | 0.2359 | 0.0206 |
| 48 | train | attack_db | 5 | 8.8741 | 9.3852 | 0.5111 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
