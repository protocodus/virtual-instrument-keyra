# Recording benchmark: 2.7.0 against 2.6.0

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.6.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 8.03 | 3.41 | 4.83 | 7.44 | 9.39 | 10.84 | 9.86 | 6.39 | 0.25 | 4.16 | 15.55 | 4.36 |
| dev (21) | 8.55 | 3.09 | 5.33 | 7.42 | 8.95 | 10.42 | 9.22 | 5.07 | 0.26 | 4.35 | 12.77 | 3.03 |
| train / bass A0-B2 (30) | 10.36 | 4.50 | 5.06 | 7.90 | 9.66 | 10.30 | 15.42 | 5.98 | 0.23 | 3.20 | 21.52 | 3.61 |
| train / middle C3-B5 (69) | 7.62 | 3.07 | 4.24 | 7.42 | 8.54 | 8.92 | 8.70 | 6.49 | 0.20 | 3.91 | 18.73 | 4.75 |
| train / treble C6-C8 (38) | 6.93 | 3.16 | 5.76 | 7.12 | 10.73 | 14.77 | 7.57 | 6.52 | 0.36 | 5.37 | 5.05 | 4.25 |
| dev / bass A0-B2 (5) | 9.87 | 4.49 | 4.06 | 8.34 | 9.86 | 9.80 | 15.71 | 4.48 | 0.27 | 2.39 | 24.50 | 1.96 |
| dev / middle C3-B5 (11) | 6.84 | 1.99 | 4.78 | 6.92 | 7.87 | 8.70 | 7.51 | 6.53 | 0.20 | 4.08 | 10.71 | 3.48 |
| dev / treble C6-C8 (5) | 10.98 | 4.10 | 7.80 | 7.61 | 10.44 | 14.81 | 7.77 | 2.48 | 0.36 | 6.91 | 5.59 | 3.12 |

## 2.7.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.92 | 3.25 | 4.54 | 7.34 | 9.13 | 10.67 | 9.50 | 6.14 | 0.25 | 4.27 | 15.34 | 4.23 |
| dev (21) | 8.06 | 3.63 | 5.36 | 7.54 | 8.77 | 10.61 | 8.91 | 5.65 | 0.25 | 4.40 | 13.07 | 3.16 |
| train / bass A0-B2 (30) | 10.75 | 4.76 | 4.70 | 7.91 | 9.57 | 10.21 | 15.09 | 5.93 | 0.23 | 3.25 | 22.35 | 3.52 |
| train / middle C3-B5 (69) | 7.64 | 2.96 | 4.05 | 7.36 | 8.40 | 8.74 | 8.40 | 6.33 | 0.20 | 4.00 | 18.13 | 4.69 |
| train / treble C6-C8 (38) | 6.20 | 2.58 | 5.33 | 6.85 | 10.11 | 14.55 | 7.10 | 5.95 | 0.38 | 5.55 | 4.75 | 3.95 |
| dev / bass A0-B2 (5) | 10.65 | 4.98 | 4.06 | 8.24 | 9.87 | 9.56 | 15.03 | 4.38 | 0.26 | 2.33 | 21.99 | 1.83 |
| dev / middle C3-B5 (11) | 7.18 | 2.05 | 4.49 | 7.13 | 7.81 | 9.14 | 7.38 | 7.67 | 0.21 | 4.17 | 13.38 | 3.79 |
| dev / treble C6-C8 (5) | 7.43 | 5.76 | 8.58 | 7.72 | 9.81 | 14.89 | 7.38 | 2.48 | 0.35 | 6.98 | 3.48 | 3.12 |

## Independent-sample regressions (legacy)

Every note and role where 2.7.0 is worse than 2.6.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.6.0 | 2.7.0 |
|---|---|---|---|---|
| 96 | train | ild_db | 6.08 | 10.28 |
| 56 | dev | rise_ms | 11.06 | 16.88 |
| 72 | dev | ild_db | 5.37 | 8.26 |
| 48 | train | partial_db | 9.32 | 11.61 |
| 27 | train | rise_ms | 40.82 | 45.23 |
| 27 | train | partial_db | 9.71 | 11.74 |
| 88 | dev | tuning_cents | 4.10 | 5.76 |
| 96 | train | icc | 0.27 | 0.34 |
| 58 | train | ild_db | 4.68 | 6.03 |
| 82 | train | ild_db | 5.94 | 7.27 |
| 24 | train | tuning_cents | 6.66 | 7.96 |
| 72 | dev | partial_db | 6.71 | 7.78 |
| 66 | train | tuning_cents | 2.72 | 3.77 |
| 94 | train | sustain_db | 17.42 | 18.46 |
| 100 | train | envelope_db | 4.26 | 5.05 |
| 39 | dev | partial_db | 9.87 | 10.65 |
| 68 | train | ild_db | 5.82 | 6.57 |
| 100 | train | tuning_cents | 2.06 | 2.81 |
| 103 | train | partial_db | 4.48 | 5.23 |
| 72 | dev | sustain_db | 10.40 | 11.14 |
| 76 | train | level_db | 3.75 | 4.41 |
| 36 | train | partial_db | 11.33 | 11.97 |
| 86 | train | icc | 0.33 | 0.36 |
| 59 | dev | level_db | 5.98 | 6.56 |
| 74 | train | level_db | 6.44 | 7.03 |
| 72 | dev | attack_db | 6.83 | 7.41 |
| 72 | dev | level_db | 3.35 | 3.92 |
| 74 | train | tuning_cents | 2.81 | 3.38 |
| 96 | train | decay_db_s | 5.45 | 6.59 |
| 103 | train | envelope_db | 5.45 | 6.02 |
| 45 | train | icc | 0.20 | 0.22 |
| 70 | train | partial_db | 5.31 | 5.84 |
| 96 | train | envelope_db | 3.49 | 4.00 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (11.7179 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 8.5470 | 8.0645 | -0.4824 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 3.0889 | 3.6311 | 0.5422 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 5.3296 | 5.3611 | 0.0315 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.4227 | 7.5355 | 0.1127 | 0 | 0 | 0 |
| dev | early_db | 21 | 8.9549 | 8.7747 | -0.1802 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 10.4154 | 10.6079 | 0.1925 | 0 | 0 | 0 |
| dev | noise_db | 20 | 9.2198 | 8.9111 | -0.3086 | 0 | 0 | 1 |
| dev | ild_db | 21 | 5.0746 | 5.6491 | 0.5744 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2567 | 0.2527 | -0.0040 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.3508 | 4.4044 | 0.0536 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 12.7748 | 13.0734 | 0.2986 | 0 | 0 | 0 |
| dev | level_db | 21 | 3.0316 | 3.1446 | 0.1130 | 0 | 0 | 0 |
| train | partial_db | 137 | 8.0298 | 7.9236 | -0.1061 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 3.4069 | 3.2476 | -0.1593 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 4.8299 | 4.5373 | -0.2926 | 0 | 0 | 2 |
| train | attack_db | 137 | 7.4402 | 7.3402 | -0.0999 | 0 | 0 | 0 |
| train | early_db | 137 | 9.3924 | 9.1280 | -0.2644 | 0 | 0 | 0 |
| train | sustain_db | 137 | 10.8416 | 10.6718 | -0.1698 | 0 | 0 | 0 |
| train | noise_db | 137 | 9.8582 | 9.5029 | -0.3553 | 0 | 0 | 0 |
| train | ild_db | 135 | 6.3871 | 6.1401 | -0.2470 | 0 | 0 | 2 |
| train | icc | 135 | 0.2488 | 0.2518 | 0.0030 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.1594 | 4.2660 | 0.1066 | 0 | 0 | 0 |
| train | rise_ms | 137 | 15.5471 | 15.3417 | -0.2054 | 0 | 0 | 0 |
| train | level_db | 137 | 4.3637 | 4.2377 | -0.1260 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 96 | train | ild_db | 5 | 6.0841 | 10.2774 | 4.1933 |
| 56 | dev | rise_ms | 5 | 11.0583 | 16.8792 | 5.8208 |
| 72 | dev | ild_db | 5 | 5.3699 | 8.2625 | 2.8926 |
| 48 | train | partial_db | 5 | 9.3223 | 11.6052 | 2.2830 |
| 27 | train | rise_ms | 5 | 40.8167 | 45.2292 | 4.4125 |
| 27 | train | partial_db | 5 | 9.7076 | 11.7359 | 2.0283 |
| 88 | dev | tuning_cents | 5 | 4.0952 | 5.7641 | 1.6689 |
| 96 | train | icc | 5 | 0.2744 | 0.3356 | 0.0612 |
| 58 | train | ild_db | 4 | 4.6830 | 6.0327 | 1.3496 |
| 82 | train | ild_db | 5 | 5.9396 | 7.2728 | 1.3332 |
| 24 | train | tuning_cents | 5 | 6.6600 | 7.9557 | 1.2957 |
| 72 | dev | partial_db | 5 | 6.7061 | 7.7766 | 1.0706 |
| 66 | train | tuning_cents | 5 | 2.7215 | 3.7674 | 1.0459 |
| 94 | train | sustain_db | 5 | 17.4176 | 18.4563 | 1.0387 |
| 100 | train | envelope_db | 4 | 4.2629 | 5.0536 | 0.7908 |
| 39 | dev | partial_db | 5 | 9.8749 | 10.6524 | 0.7775 |
| 68 | train | ild_db | 5 | 5.8163 | 6.5706 | 0.7543 |
| 100 | train | tuning_cents | 4 | 2.0571 | 2.8087 | 0.7516 |
| 103 | train | partial_db | 4 | 4.4840 | 5.2306 | 0.7466 |
| 72 | dev | sustain_db | 5 | 10.4040 | 11.1444 | 0.7403 |
| 36 | train | partial_db | 5 | 11.3328 | 11.9671 | 0.6343 |
| 86 | train | icc | 5 | 0.3323 | 0.3566 | 0.0243 |
| 72 | dev | attack_db | 5 | 6.8250 | 7.4067 | 0.5817 |
| 74 | train | tuning_cents | 5 | 2.8136 | 3.3831 | 0.5695 |
| 96 | train | decay_db_s | 5 | 5.4543 | 6.5924 | 1.1381 |
| 103 | train | envelope_db | 4 | 5.4511 | 6.0197 | 0.5686 |
| 45 | train | icc | 5 | 0.2005 | 0.2228 | 0.0223 |
| 70 | train | partial_db | 5 | 5.3074 | 5.8416 | 0.5342 |
| 96 | train | envelope_db | 5 | 3.4937 | 3.9973 | 0.5037 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
