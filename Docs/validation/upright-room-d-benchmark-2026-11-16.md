# Recording benchmark: 2.17.0 room against 2.16.2

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.16.2

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.66 | 3.48 | 4.48 | 7.47 | 8.78 | 10.47 | 9.98 | 5.98 | 0.22 | 4.22 | 12.66 | 4.28 |
| dev (21) | 7.63 | 3.90 | 4.96 | 7.50 | 8.51 | 10.00 | 8.54 | 5.41 | 0.24 | 4.55 | 9.10 | 3.48 |
| train / bass A0-B2 (30) | 10.25 | 4.97 | 4.16 | 8.77 | 9.59 | 10.52 | 15.74 | 6.29 | 0.19 | 2.87 | 6.83 | 3.69 |
| train / middle C3-B5 (69) | 7.47 | 2.94 | 4.31 | 7.29 | 7.88 | 8.35 | 8.83 | 5.96 | 0.19 | 3.81 | 19.74 | 4.72 |
| train / treble C6-C8 (38) | 5.94 | 3.27 | 5.06 | 6.77 | 9.77 | 14.27 | 7.50 | 5.76 | 0.31 | 6.04 | 4.42 | 3.97 |
| dev / bass A0-B2 (5) | 8.87 | 3.58 | 2.92 | 9.11 | 10.26 | 10.62 | 12.82 | 3.98 | 0.30 | 1.92 | 1.98 | 2.66 |
| dev / middle C3-B5 (11) | 6.51 | 2.46 | 4.41 | 6.95 | 7.12 | 8.33 | 7.22 | 7.25 | 0.19 | 4.77 | 14.57 | 3.90 |
| dev / treble C6-C8 (5) | 8.85 | 7.40 | 8.21 | 7.09 | 9.82 | 13.06 | 7.16 | 2.78 | 0.29 | 6.67 | 4.18 | 3.39 |

## 2.17.0 room

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

## Independent-sample regressions (legacy)

Every note and role where 2.17.0 room is worse than 2.16.2 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.16.2 | 2.17.0 room |
|---|---|---|---|---|
| 92 | train | tuning_cents | 3.43 | 6.56 |
| 88 | dev | ild_db | 2.78 | 5.82 |
| 96 | train | ild_db | 7.67 | 10.23 |
| 27 | train | rise_ms | 6.02 | 10.72 |
| 86 | train | ild_db | 9.81 | 11.80 |
| 94 | train | ild_db | 5.31 | 7.08 |
| 100 | train | icc | 0.20 | 0.26 |
| 78 | train | icc | 0.14 | 0.20 |
| 76 | train | ild_db | 2.38 | 3.58 |
| 50 | train | icc | 0.14 | 0.18 |
| 72 | dev | icc | 0.21 | 0.26 |
| 54 | train | icc | 0.21 | 0.25 |
| 100 | train | ild_db | 4.64 | 5.69 |
| 33 | train | ild_db | 7.44 | 8.47 |
| 54 | train | ild_db | 4.88 | 5.90 |
| 70 | train | icc | 0.15 | 0.19 |
| 90 | train | ild_db | 2.71 | 3.71 |
| 92 | train | icc | 0.38 | 0.42 |
| 90 | train | early_db | 9.38 | 10.32 |
| 72 | dev | ild_db | 7.34 | 8.27 |
| 88 | dev | icc | 0.29 | 0.33 |
| 42 | train | ild_db | 4.50 | 5.37 |
| 42 | train | envelope_db | 3.15 | 4.01 |
| 36 | train | ild_db | 6.33 | 7.18 |
| 103 | train | ild_db | 5.35 | 6.12 |
| 70 | train | early_db | 7.75 | 8.53 |
| 70 | train | sustain_db | 7.26 | 8.00 |
| 70 | train | partial_db | 5.70 | 6.43 |
| 78 | train | noise_db | 9.62 | 10.33 |
| 59 | dev | ild_db | 5.93 | 6.62 |
| 59 | dev | icc | 0.15 | 0.18 |
| 78 | train | early_db | 10.86 | 11.54 |
| 96 | train | tuning_cents | 3.18 | 3.85 |
| 39 | dev | ild_db | 3.98 | 4.65 |
| 59 | dev | noise_db | 8.48 | 9.15 |
| 66 | train | icc | 0.22 | 0.24 |
| 82 | train | early_db | 7.24 | 7.88 |
| 45 | train | icc | 0.15 | 0.17 |
| 103 | train | decay_db_s | 4.30 | 5.54 |
| 68 | train | partial_db | 6.12 | 6.72 |
| 90 | train | attack_db | 7.48 | 8.06 |
| 62 | train | icc | 0.14 | 0.16 |
| 84 | train | early_db | 8.42 | 8.97 |
| 58 | train | early_db | 5.03 | 5.58 |
| 66 | train | tuning_cents | 3.06 | 3.58 |
| 88 | dev | early_db | 9.82 | 10.34 |
| 94 | train | icc | 0.47 | 0.49 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.1844 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 7.6292 | 7.1014 | -0.5278 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 3.9028 | 3.6623 | -0.2405 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 4.9579 | 4.8877 | -0.0702 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.4954 | 7.4022 | -0.0932 | 0 | 0 | 0 |
| dev | early_db | 21 | 8.5112 | 8.7069 | 0.1957 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 10.0029 | 9.8281 | -0.1748 | 0 | 0 | 0 |
| dev | noise_db | 21 | 8.5416 | 8.5084 | -0.0332 | 0 | 0 | 0 |
| dev | ild_db | 21 | 5.4074 | 6.6569 | 1.2495 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2430 | 0.2548 | 0.0118 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.5472 | 4.6032 | 0.0560 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 9.0992 | 9.0873 | -0.0119 | 0 | 0 | 0 |
| dev | level_db | 21 | 3.4834 | 3.4363 | -0.0470 | 0 | 0 | 0 |
| train | partial_db | 137 | 7.6556 | 7.3611 | -0.2945 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 3.4797 | 3.5605 | 0.0808 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 4.4768 | 4.5079 | 0.0311 | 0 | 0 | 2 |
| train | attack_db | 137 | 7.4663 | 7.3721 | -0.0942 | 0 | 0 | 0 |
| train | early_db | 137 | 8.7794 | 8.7814 | 0.0020 | 0 | 0 | 0 |
| train | sustain_db | 137 | 10.4674 | 10.3436 | -0.1238 | 0 | 0 | 0 |
| train | noise_db | 137 | 9.9755 | 9.8051 | -0.1704 | 0 | 0 | 0 |
| train | ild_db | 135 | 5.9823 | 6.2159 | 0.2335 | 0 | 0 | 2 |
| train | icc | 135 | 0.2207 | 0.2266 | 0.0059 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.2218 | 4.2618 | 0.0399 | 0 | 0 | 0 |
| train | rise_ms | 137 | 12.6639 | 12.4842 | -0.1797 | 0 | 0 | 0 |
| train | level_db | 137 | 4.2844 | 4.2458 | -0.0386 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 92 | train | tuning_cents | 5 | 3.4261 | 6.5611 | 3.1350 |
| 88 | dev | ild_db | 5 | 2.7798 | 5.8163 | 3.0366 |
| 96 | train | ild_db | 5 | 7.6656 | 10.2297 | 2.5641 |
| 27 | train | rise_ms | 5 | 6.0208 | 10.7167 | 4.6958 |
| 86 | train | ild_db | 5 | 9.8119 | 11.8017 | 1.9898 |
| 94 | train | ild_db | 5 | 5.3104 | 7.0774 | 1.7670 |
| 100 | train | icc | 3 | 0.1950 | 0.2558 | 0.0608 |
| 78 | train | icc | 5 | 0.1393 | 0.1999 | 0.0606 |
| 76 | train | ild_db | 5 | 2.3809 | 3.5773 | 1.1964 |
| 50 | train | icc | 5 | 0.1401 | 0.1843 | 0.0442 |
| 72 | dev | icc | 5 | 0.2146 | 0.2579 | 0.0433 |
| 54 | train | icc | 5 | 0.2102 | 0.2529 | 0.0428 |
| 100 | train | ild_db | 3 | 4.6423 | 5.6859 | 1.0436 |
| 33 | train | ild_db | 5 | 7.4410 | 8.4651 | 1.0241 |
| 54 | train | ild_db | 5 | 4.8817 | 5.9036 | 1.0219 |
| 70 | train | icc | 5 | 0.1455 | 0.1860 | 0.0404 |
| 90 | train | ild_db | 5 | 2.7090 | 3.7073 | 0.9984 |
| 92 | train | icc | 5 | 0.3789 | 0.4171 | 0.0382 |
| 90 | train | early_db | 5 | 9.3777 | 10.3171 | 0.9393 |
| 72 | dev | ild_db | 5 | 7.3442 | 8.2704 | 0.9262 |
| 88 | dev | icc | 5 | 0.2932 | 0.3287 | 0.0355 |
| 42 | train | ild_db | 5 | 4.4979 | 5.3737 | 0.8759 |
| 42 | train | envelope_db | 5 | 3.1508 | 4.0146 | 0.8637 |
| 36 | train | ild_db | 5 | 6.3253 | 7.1797 | 0.8544 |
| 103 | train | ild_db | 3 | 5.3459 | 6.1250 | 0.7791 |
| 70 | train | early_db | 5 | 7.7504 | 8.5267 | 0.7763 |
| 70 | train | sustain_db | 5 | 7.2572 | 7.9958 | 0.7386 |
| 70 | train | partial_db | 5 | 5.6987 | 6.4284 | 0.7298 |
| 78 | train | noise_db | 5 | 9.6198 | 10.3318 | 0.7120 |
| 59 | dev | ild_db | 1 | 5.9290 | 6.6247 | 0.6957 |
| 59 | dev | icc | 1 | 0.1523 | 0.1796 | 0.0273 |
| 78 | train | early_db | 5 | 10.8578 | 11.5364 | 0.6786 |
| 96 | train | tuning_cents | 5 | 3.1802 | 3.8510 | 0.6708 |
| 39 | dev | ild_db | 5 | 3.9806 | 4.6501 | 0.6695 |
| 59 | dev | noise_db | 1 | 8.4817 | 9.1510 | 0.6694 |
| 66 | train | icc | 5 | 0.2155 | 0.2414 | 0.0258 |
| 82 | train | early_db | 5 | 7.2419 | 7.8804 | 0.6385 |
| 45 | train | icc | 5 | 0.1497 | 0.1746 | 0.0249 |
| 103 | train | decay_db_s | 3 | 4.3025 | 5.5359 | 1.2334 |
| 68 | train | partial_db | 5 | 6.1224 | 6.7178 | 0.5955 |
| 90 | train | attack_db | 5 | 7.4780 | 8.0638 | 0.5858 |
| 62 | train | icc | 5 | 0.1367 | 0.1600 | 0.0233 |
| 84 | train | early_db | 5 | 8.4202 | 8.9736 | 0.5534 |
| 58 | train | early_db | 4 | 5.0261 | 5.5787 | 0.5526 |
| 66 | train | tuning_cents | 5 | 3.0560 | 3.5818 | 0.5258 |
| 88 | dev | early_db | 5 | 9.8164 | 10.3403 | 0.5239 |
| 94 | train | icc | 5 | 0.4715 | 0.4924 | 0.0209 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
