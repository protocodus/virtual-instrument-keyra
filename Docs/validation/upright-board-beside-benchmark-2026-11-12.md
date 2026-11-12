# Recording benchmark: 2.10.0 against 2.9.0

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.9.0

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

## 2.10.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.66 | 3.38 | 4.39 | 7.49 | 9.04 | 10.48 | 9.58 | 6.62 | 0.25 | 4.24 | 13.28 | 4.16 |
| dev (21) | 7.62 | 3.67 | 5.24 | 7.35 | 8.83 | 9.98 | 8.47 | 6.22 | 0.25 | 4.19 | 9.13 | 3.10 |
| train / bass A0-B2 (30) | 10.55 | 4.97 | 4.25 | 7.98 | 9.07 | 10.15 | 14.89 | 6.10 | 0.20 | 2.90 | 10.70 | 3.52 |
| train / middle C3-B5 (69) | 7.69 | 2.89 | 4.02 | 7.52 | 8.48 | 8.42 | 8.58 | 6.30 | 0.20 | 3.78 | 19.19 | 4.56 |
| train / treble C6-C8 (38) | 5.35 | 3.03 | 5.22 | 7.05 | 10.04 | 14.48 | 7.20 | 7.67 | 0.37 | 6.15 | 4.58 | 3.94 |
| dev / bass A0-B2 (5) | 9.95 | 4.95 | 4.55 | 7.65 | 9.23 | 10.23 | 12.89 | 4.35 | 0.24 | 2.37 | 3.39 | 2.00 |
| dev / middle C3-B5 (11) | 6.55 | 2.08 | 4.40 | 7.30 | 8.06 | 8.01 | 7.54 | 7.61 | 0.21 | 3.75 | 13.83 | 3.63 |
| dev / treble C6-C8 (5) | 7.64 | 5.88 | 7.76 | 7.17 | 10.12 | 14.07 | 6.97 | 5.04 | 0.35 | 6.97 | 4.56 | 3.03 |

## Independent-sample regressions (legacy)

Every note and role where 2.10.0 is worse than 2.9.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.9.0 | 2.10.0 |
|---|---|---|---|---|
| 48 | train | rise_ms | 23.18 | 35.93 |
| 59 | dev | rise_ms | 3.87 | 14.33 |
| 84 | train | ild_db | 6.96 | 11.88 |
| 82 | train | ild_db | 7.27 | 11.69 |
| 58 | train | rise_ms | 36.89 | 44.23 |
| 96 | train | ild_db | 10.28 | 13.69 |
| 84 | train | envelope_db | 4.33 | 7.55 |
| 84 | train | sustain_db | 9.83 | 12.51 |
| 88 | dev | ild_db | 2.48 | 5.04 |
| 45 | train | ild_db | 5.27 | 7.80 |
| 36 | train | sustain_db | 8.07 | 10.58 |
| 54 | train | rise_ms | 4.03 | 8.89 |
| 94 | train | ild_db | 4.89 | 7.20 |
| 68 | train | partial_db | 7.91 | 10.04 |
| 103 | train | decay_db_s | 0.85 | 5.06 |
| 68 | train | attack_db | 8.60 | 10.57 |
| 103 | train | tuning_cents | 1.90 | 3.77 |
| 103 | train | level_db | 3.31 | 5.18 |
| 90 | train | ild_db | 3.89 | 5.75 |
| 52 | train | rise_ms | 4.13 | 7.69 |
| 68 | train | sustain_db | 9.55 | 11.27 |
| 24 | train | ild_db | 4.56 | 6.28 |
| 52 | train | icc | 0.17 | 0.24 |
| 100 | train | tuning_cents | 2.81 | 4.38 |
| 68 | train | early_db | 9.31 | 10.65 |
| 58 | train | envelope_db | 3.67 | 5.01 |
| 103 | train | attack_db | 7.89 | 9.22 |
| 56 | dev | early_db | 6.59 | 7.90 |
| 96 | train | envelope_db | 4.00 | 5.28 |
| 76 | train | ild_db | 5.14 | 6.35 |
| 103 | train | noise_db | 8.77 | 9.98 |
| 100 | train | envelope_db | 5.05 | 6.23 |
| 74 | train | ild_db | 7.34 | 8.49 |
| 56 | dev | attack_db | 6.66 | 7.80 |
| 68 | train | noise_db | 8.58 | 9.69 |
| 70 | train | partial_db | 5.84 | 6.94 |
| 48 | train | early_db | 10.51 | 11.53 |
| 100 | train | level_db | 1.10 | 2.11 |
| 48 | train | sustain_db | 7.98 | 8.98 |
| 100 | train | ild_db | 3.62 | 4.62 |
| 90 | train | envelope_db | 5.17 | 6.16 |
| 74 | train | early_db | 8.61 | 9.58 |
| 84 | train | partial_db | 5.55 | 6.51 |
| 59 | dev | partial_db | 8.40 | 9.31 |
| 52 | train | ild_db | 5.22 | 6.08 |
| 58 | train | ild_db | 6.03 | 6.90 |
| 70 | train | sustain_db | 7.94 | 8.79 |
| 59 | dev | attack_db | 8.10 | 8.94 |
| 54 | train | noise_db | 10.46 | 11.29 |
| 36 | train | attack_db | 8.01 | 8.81 |
| 52 | train | envelope_db | 2.46 | 3.23 |
| 68 | train | icc | 0.13 | 0.16 |
| 59 | dev | icc | 0.14 | 0.17 |
| 36 | train | early_db | 10.79 | 11.50 |
| 60 | train | envelope_db | 2.11 | 2.80 |
| 39 | dev | sustain_db | 9.56 | 10.23 |
| 33 | train | ild_db | 6.29 | 6.95 |
| 36 | train | envelope_db | 2.73 | 3.39 |
| 78 | train | level_db | 5.68 | 6.33 |
| 100 | train | sustain_db | 17.88 | 18.51 |
| 56 | dev | noise_db | 8.06 | 8.68 |
| 33 | train | sustain_db | 10.64 | 11.26 |
| 56 | dev | partial_db | 6.33 | 6.93 |
| 59 | dev | level_db | 6.56 | 7.12 |
| 50 | train | sustain_db | 6.47 | 7.01 |
| 88 | dev | rise_ms | 3.48 | 4.56 |
| 33 | train | attack_db | 9.50 | 10.04 |
| 78 | train | decay_db_s | 5.15 | 6.21 |
| 27 | train | ild_db | 4.39 | 4.92 |
| 94 | train | envelope_db | 7.29 | 7.80 |
| 96 | train | sustain_db | 13.58 | 14.08 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (11.3665 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 8.0645 | 7.6207 | -0.4439 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 3.6311 | 3.6657 | 0.0347 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 5.3611 | 5.2383 | -0.1228 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.5355 | 7.3546 | -0.1808 | 0 | 0 | 0 |
| dev | early_db | 21 | 8.7747 | 8.8307 | 0.0560 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 10.6079 | 9.9799 | -0.6280 | 0 | 0 | 0 |
| dev | noise_db | 20 | 8.9111 | 8.4684 | -0.4427 | 0 | 0 | 1 |
| dev | ild_db | 21 | 5.6491 | 6.2212 | 0.5722 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2527 | 0.2482 | -0.0044 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.4044 | 4.1899 | -0.2145 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 13.0734 | 9.1339 | -3.9395 | 0 | 0 | 0 |
| dev | level_db | 21 | 3.1614 | 3.2303 | 0.0689 | 0 | 0 | 0 |
| train | partial_db | 137 | 7.9236 | 7.6647 | -0.2590 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 3.2476 | 3.3815 | 0.1339 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 4.5373 | 4.3903 | -0.1470 | 0 | 0 | 2 |
| train | attack_db | 137 | 7.3402 | 7.4920 | 0.1518 | 0 | 0 | 0 |
| train | early_db | 137 | 9.1280 | 9.0401 | -0.0878 | 0 | 0 | 0 |
| train | sustain_db | 137 | 10.6718 | 10.4798 | -0.1920 | 0 | 0 | 0 |
| train | noise_db | 137 | 9.5029 | 9.5819 | 0.0790 | 0 | 0 | 0 |
| train | ild_db | 135 | 6.1401 | 6.6237 | 0.4836 | 0 | 0 | 2 |
| train | icc | 135 | 0.2518 | 0.2467 | -0.0051 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.2660 | 4.2434 | -0.0226 | 0 | 0 | 0 |
| train | rise_ms | 137 | 15.3417 | 13.2803 | -2.0614 | 0 | 0 | 0 |
| train | level_db | 137 | 4.2303 | 4.1624 | -0.0679 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 48 | train | rise_ms | 5 | 23.1833 | 35.9333 | 12.7500 |
| 59 | dev | rise_ms | 1 | 3.8750 | 14.3333 | 10.4583 |
| 84 | train | ild_db | 5 | 6.9556 | 11.8850 | 4.9294 |
| 82 | train | ild_db | 5 | 7.2728 | 11.6899 | 4.4172 |
| 58 | train | rise_ms | 4 | 36.8906 | 44.2344 | 7.3438 |
| 96 | train | ild_db | 5 | 10.2774 | 13.6940 | 3.4166 |
| 84 | train | envelope_db | 5 | 4.3293 | 7.5528 | 3.2235 |
| 84 | train | sustain_db | 5 | 9.8270 | 12.5087 | 2.6817 |
| 88 | dev | ild_db | 5 | 2.4776 | 5.0372 | 2.5596 |
| 45 | train | ild_db | 5 | 5.2744 | 7.7994 | 2.5249 |
| 36 | train | sustain_db | 5 | 8.0748 | 10.5757 | 2.5009 |
| 54 | train | rise_ms | 5 | 4.0292 | 8.8917 | 4.8625 |
| 94 | train | ild_db | 5 | 4.8857 | 7.2025 | 2.3168 |
| 68 | train | partial_db | 5 | 7.9134 | 10.0377 | 2.1243 |
| 103 | train | decay_db_s | 3 | 0.8544 | 5.0604 | 4.2059 |
| 68 | train | attack_db | 5 | 8.6011 | 10.5716 | 1.9705 |
| 103 | train | tuning_cents | 4 | 1.9021 | 3.7713 | 1.8692 |
| 90 | train | ild_db | 5 | 3.8914 | 5.7520 | 1.8606 |
| 52 | train | rise_ms | 5 | 4.1333 | 7.6917 | 3.5583 |
| 68 | train | sustain_db | 5 | 9.5542 | 11.2734 | 1.7193 |
| 24 | train | ild_db | 5 | 4.5625 | 6.2799 | 1.7174 |
| 52 | train | icc | 5 | 0.1724 | 0.2398 | 0.0673 |
| 103 | train | level_db | 4 | 3.3139 | 4.9383 | 1.6244 |
| 100 | train | tuning_cents | 4 | 2.8087 | 4.3806 | 1.5720 |
| 68 | train | early_db | 5 | 9.3096 | 10.6509 | 1.3412 |
| 58 | train | envelope_db | 4 | 3.6721 | 5.0053 | 1.3333 |
| 103 | train | attack_db | 4 | 7.8921 | 9.2183 | 1.3262 |
| 56 | dev | early_db | 5 | 6.5896 | 7.9011 | 1.3114 |
| 96 | train | envelope_db | 5 | 3.9973 | 5.2841 | 1.2867 |
| 76 | train | ild_db | 5 | 5.1400 | 6.3512 | 1.2113 |
| 103 | train | noise_db | 4 | 8.7719 | 9.9752 | 1.2033 |
| 100 | train | envelope_db | 4 | 5.0536 | 6.2277 | 1.1740 |
| 74 | train | ild_db | 5 | 7.3442 | 8.4901 | 1.1459 |
| 56 | dev | attack_db | 5 | 6.6561 | 7.8002 | 1.1441 |
| 68 | train | noise_db | 5 | 8.5837 | 9.6885 | 1.1048 |
| 70 | train | partial_db | 5 | 5.8416 | 6.9443 | 1.1027 |
| 59 | dev | level_db | 1 | 6.5616 | 7.6062 | 1.0446 |
| 48 | train | early_db | 5 | 10.5068 | 11.5343 | 1.0275 |
| 48 | train | sustain_db | 5 | 7.9839 | 8.9828 | 0.9989 |
| 100 | train | ild_db | 3 | 3.6215 | 4.6164 | 0.9948 |
| 90 | train | envelope_db | 5 | 5.1682 | 6.1563 | 0.9881 |
| 74 | train | early_db | 5 | 8.6111 | 9.5771 | 0.9660 |
| 84 | train | partial_db | 5 | 5.5508 | 6.5135 | 0.9626 |
| 59 | dev | partial_db | 1 | 8.3954 | 9.3133 | 0.9179 |
| 52 | train | ild_db | 5 | 5.2158 | 6.0843 | 0.8685 |
| 58 | train | ild_db | 4 | 6.0327 | 6.8997 | 0.8670 |
| 70 | train | sustain_db | 5 | 7.9376 | 8.7872 | 0.8495 |
| 59 | dev | attack_db | 1 | 8.1014 | 8.9358 | 0.8345 |
| 54 | train | noise_db | 5 | 10.4592 | 11.2880 | 0.8288 |
| 36 | train | attack_db | 5 | 8.0072 | 8.8112 | 0.8040 |
| 52 | train | envelope_db | 5 | 2.4596 | 3.2253 | 0.7658 |
| 68 | train | icc | 5 | 0.1315 | 0.1618 | 0.0303 |
| 59 | dev | icc | 1 | 0.1397 | 0.1692 | 0.0296 |
| 36 | train | early_db | 5 | 10.7946 | 11.5006 | 0.7060 |
| 48 | train | level_db | 5 | 3.8686 | 4.5729 | 0.7044 |
| 60 | train | envelope_db | 5 | 2.1064 | 2.8048 | 0.6984 |
| 39 | dev | sustain_db | 5 | 9.5614 | 10.2282 | 0.6668 |
| 33 | train | ild_db | 5 | 6.2900 | 6.9533 | 0.6633 |
| 36 | train | envelope_db | 5 | 2.7318 | 3.3877 | 0.6560 |
| 100 | train | sustain_db | 4 | 17.8815 | 18.5094 | 0.6279 |
| 56 | dev | noise_db | 5 | 8.0584 | 8.6757 | 0.6173 |
| 33 | train | sustain_db | 5 | 10.6395 | 11.2555 | 0.6160 |
| 56 | dev | partial_db | 5 | 6.3311 | 6.9289 | 0.5979 |
| 50 | train | sustain_db | 5 | 6.4673 | 7.0093 | 0.5420 |
| 88 | dev | rise_ms | 5 | 3.4750 | 4.5583 | 1.0833 |
| 33 | train | attack_db | 5 | 9.5026 | 10.0423 | 0.5396 |
| 78 | train | decay_db_s | 5 | 5.1497 | 6.2103 | 1.0607 |
| 27 | train | ild_db | 5 | 4.3900 | 4.9184 | 0.5284 |
| 100 | train | level_db | 4 | 1.0990 | 1.6180 | 0.5190 |
| 94 | train | envelope_db | 5 | 7.2872 | 7.7954 | 0.5081 |
| 96 | train | sustain_db | 5 | 13.5809 | 14.0829 | 0.5020 |
| 60 | train | level_db | 5 | 4.1339 | 4.6342 | 0.5003 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
