# Recording benchmark: 2.2.0 against 2.1.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.1.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.86 | 2.81 | 4.72 | 8.49 | 9.57 | 10.06 | 10.55 | 5.48 | 0.21 | 4.23 | 17.26 | 3.72 |
| dev (156) | 8.19 | 2.91 | 3.67 | 8.11 | 8.92 | 9.10 | 10.07 | 5.60 | 0.21 | 4.18 | 14.93 | 3.39 |
| train / bass A0-B2 (84) | 8.64 | 3.09 | 2.69 | 5.68 | 5.58 | 7.05 | 8.07 | 4.68 | 0.19 | 3.95 | 25.43 | 2.67 |
| train / middle C3-B5 (108) | 7.87 | 2.56 | 3.94 | 7.21 | 7.47 | 8.57 | 8.43 | 7.48 | 0.22 | 4.52 | 21.11 | 4.00 |
| train / treble C6-C8 (84) | 10.36 | 2.86 | 7.97 | 12.95 | 16.27 | 14.98 | 15.53 | 3.56 | 0.23 | 4.15 | 4.14 | 4.40 |
| dev / bass A0-B2 (44) | 8.52 | 3.55 | 2.45 | 5.87 | 5.85 | 6.69 | 8.06 | 4.87 | 0.22 | 3.47 | 27.58 | 4.15 |
| dev / middle C3-B5 (68) | 7.49 | 2.24 | 3.42 | 6.74 | 6.48 | 7.68 | 7.82 | 7.78 | 0.17 | 4.35 | 14.32 | 3.13 |
| dev / treble C6-C8 (44) | 8.96 | 3.31 | 5.34 | 12.49 | 15.76 | 13.71 | 15.40 | 2.82 | 0.28 | 4.62 | 3.23 | 3.03 |

## 2.2.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.94 | 2.79 | 4.75 | 8.39 | 9.39 | 10.09 | 10.23 | 5.47 | 0.21 | 4.24 | 17.26 | 2.65 |
| dev (156) | 8.19 | 2.90 | 3.68 | 8.07 | 8.86 | 9.11 | 9.89 | 5.59 | 0.21 | 4.18 | 15.06 | 2.52 |
| train / bass A0-B2 (84) | 8.65 | 3.08 | 2.68 | 5.66 | 5.57 | 7.05 | 8.12 | 4.68 | 0.19 | 3.94 | 25.70 | 2.27 |
| train / middle C3-B5 (108) | 7.87 | 2.52 | 3.94 | 7.16 | 7.44 | 8.57 | 7.89 | 7.46 | 0.22 | 4.53 | 20.75 | 2.19 |
| train / treble C6-C8 (84) | 10.61 | 2.85 | 8.05 | 12.69 | 15.71 | 15.10 | 15.15 | 3.55 | 0.23 | 4.16 | 4.35 | 3.63 |
| dev / bass A0-B2 (44) | 8.53 | 3.54 | 2.45 | 5.86 | 5.85 | 6.69 | 7.96 | 4.87 | 0.22 | 3.47 | 28.12 | 2.89 |
| dev / middle C3-B5 (68) | 7.45 | 2.22 | 3.41 | 6.77 | 6.57 | 7.68 | 7.64 | 7.77 | 0.17 | 4.35 | 14.15 | 1.84 |
| dev / treble C6-C8 (44) | 9.00 | 3.30 | 5.35 | 12.29 | 15.40 | 13.74 | 15.14 | 2.81 | 0.28 | 4.64 | 3.41 | 3.21 |

## Independent-sample regressions (legacy)

Every note and role where 2.2.0 is worse than 2.1.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.1.0 | 2.2.0 |
|---|---|---|---|---|
| 66 | dev | rise_ms | 16.40 | 21.78 |
| 66 | train | rise_ms | 18.01 | 22.94 |
| 66 | dev | noise_db | 5.68 | 7.37 |
| 66 | train | noise_db | 5.44 | 7.02 |
| 99 | dev | level_db | 1.50 | 2.96 |
| 33 | dev | rise_ms | 9.59 | 12.33 |
| 81 | train | level_db | 2.92 | 4.25 |
| 81 | dev | level_db | 3.34 | 4.67 |
| 108 | dev | sustain_db | 22.34 | 23.29 |
| 69 | train | noise_db | 6.67 | 7.58 |
| 45 | dev | rise_ms | 24.06 | 25.66 |
| 45 | train | rise_ms | 24.37 | 25.96 |
| 108 | dev | early_db | 18.84 | 19.62 |
| 33 | dev | level_db | 0.53 | 1.29 |
| 105 | train | partial_db | 13.28 | 14.04 |
| 66 | dev | attack_db | 4.91 | 5.67 |
| 108 | train | early_db | 19.20 | 19.93 |
| 69 | dev | noise_db | 6.72 | 7.44 |
| 30 | dev | level_db | 1.51 | 2.22 |
| 66 | train | attack_db | 4.96 | 5.66 |
| 105 | dev | partial_db | 12.13 | 12.83 |
| 66 | dev | early_db | 4.96 | 5.53 |
| 30 | train | level_db | 1.77 | 2.31 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (25.1887 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 8.1924 | 8.1915 | -0.0010 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.9129 | 2.8971 | -0.0158 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 3.6741 | 3.6761 | 0.0020 | 0 | 0 | 1 |
| dev | attack_db | 156 | 8.1148 | 8.0689 | -0.0459 | 0 | 0 | 0 |
| dev | early_db | 156 | 8.9192 | 8.8584 | -0.0608 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 9.1030 | 9.1106 | 0.0076 | 0 | 0 | 0 |
| dev | noise_db | 153 | 10.0668 | 9.8863 | -0.1805 | 0 | 0 | 3 |
| dev | ild_db | 154 | 5.5967 | 5.5873 | -0.0094 | 0 | 0 | 2 |
| dev | icc | 154 | 0.2140 | 0.2137 | -0.0004 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 4.1774 | 4.1817 | 0.0043 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 14.9335 | 15.0601 | 0.1266 | 0 | 0 | 0 |
| dev | level_db | 156 | 3.3886 | 2.5069 | -0.8817 | 0 | 0 | 0 |
| train | partial_db | 276 | 8.8626 | 8.9418 | 0.0792 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.8127 | 2.7928 | -0.0199 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 4.7235 | 4.7472 | 0.0237 | 0 | 0 | 5 |
| train | attack_db | 276 | 8.4934 | 8.3878 | -0.1057 | 0 | 0 | 0 |
| train | early_db | 276 | 9.5749 | 9.3864 | -0.1886 | 0 | 0 | 0 |
| train | sustain_db | 276 | 10.0594 | 10.0943 | 0.0350 | 0 | 0 | 0 |
| train | noise_db | 268 | 10.5517 | 10.2308 | -0.3209 | 0 | 0 | 8 |
| train | ild_db | 270 | 5.4759 | 5.4667 | -0.0093 | 0 | 0 | 6 |
| train | icc | 270 | 0.2136 | 0.2127 | -0.0009 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.2340 | 4.2366 | 0.0025 | 0 | 0 | 0 |
| train | rise_ms | 276 | 17.2584 | 17.2643 | 0.0059 | 0 | 0 | 0 |
| train | level_db | 276 | 3.7167 | 2.6823 | -1.0344 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 66 | dev | rise_ms | 4 | 16.4010 | 21.7812 | 5.3802 |
| 66 | train | rise_ms | 12 | 18.0069 | 22.9427 | 4.9358 |
| 99 | dev | level_db | 16 | 1.4971 | 3.1992 | 1.7021 |
| 66 | dev | noise_db | 4 | 5.6753 | 7.3682 | 1.6929 |
| 81 | train | level_db | 12 | 2.9189 | 4.5245 | 1.6056 |
| 81 | dev | level_db | 4 | 3.3409 | 4.9435 | 1.6026 |
| 66 | train | noise_db | 12 | 5.4446 | 7.0215 | 1.5768 |
| 33 | dev | rise_ms | 4 | 9.5885 | 12.3281 | 2.7396 |
| 108 | dev | sustain_db | 4 | 22.3425 | 23.2906 | 0.9480 |
| 69 | train | noise_db | 12 | 6.6737 | 7.5783 | 0.9045 |
| 45 | dev | rise_ms | 4 | 24.0573 | 25.6562 | 1.5990 |
| 45 | train | rise_ms | 12 | 24.3698 | 25.9618 | 1.5920 |
| 108 | dev | early_db | 4 | 18.8418 | 19.6235 | 0.7817 |
| 105 | train | partial_db | 12 | 13.2843 | 14.0434 | 0.7591 |
| 66 | dev | attack_db | 4 | 4.9083 | 5.6657 | 0.7574 |
| 108 | train | early_db | 12 | 19.1992 | 19.9349 | 0.7357 |
| 69 | dev | noise_db | 4 | 6.7163 | 7.4375 | 0.7213 |
| 66 | train | attack_db | 12 | 4.9579 | 5.6611 | 0.7033 |
| 105 | dev | partial_db | 4 | 12.1332 | 12.8313 | 0.6982 |
| 66 | dev | early_db | 4 | 4.9563 | 5.5348 | 0.5784 |
| 33 | dev | level_db | 4 | 0.5293 | 1.0558 | 0.5265 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
