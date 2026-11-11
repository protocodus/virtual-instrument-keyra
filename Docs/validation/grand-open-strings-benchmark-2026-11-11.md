# Recording benchmark: 2.3.0 against 2.2.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

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

## 2.3.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.98 | 2.72 | 4.72 | 8.13 | 8.71 | 9.66 | 9.63 | 5.47 | 0.22 | 4.23 | 17.27 | 2.65 |
| dev (156) | 8.23 | 2.81 | 3.67 | 7.82 | 8.08 | 8.73 | 9.30 | 5.60 | 0.22 | 4.18 | 15.06 | 2.52 |
| train / bass A0-B2 (84) | 8.74 | 3.08 | 2.67 | 5.66 | 5.57 | 7.05 | 8.02 | 4.68 | 0.19 | 3.94 | 25.71 | 2.27 |
| train / middle C3-B5 (108) | 7.91 | 2.32 | 3.93 | 7.16 | 7.44 | 8.57 | 7.84 | 7.46 | 0.21 | 4.53 | 20.75 | 2.19 |
| train / treble C6-C8 (84) | 10.59 | 2.87 | 7.98 | 11.85 | 13.49 | 13.67 | 13.38 | 3.57 | 0.24 | 4.14 | 4.36 | 3.63 |
| dev / bass A0-B2 (44) | 8.59 | 3.57 | 2.45 | 5.86 | 5.85 | 6.69 | 8.01 | 4.87 | 0.22 | 3.47 | 28.12 | 2.89 |
| dev / middle C3-B5 (68) | 7.52 | 2.00 | 3.41 | 6.77 | 6.57 | 7.68 | 7.61 | 7.77 | 0.17 | 4.35 | 14.15 | 1.84 |
| dev / treble C6-C8 (44) | 8.96 | 3.30 | 5.33 | 11.39 | 12.65 | 12.40 | 13.10 | 2.84 | 0.30 | 4.62 | 3.41 | 3.21 |

## Independent-sample regressions (legacy)

Every note and role where 2.3.0 is worse than 2.2.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.2.0 | 2.3.0 |
|---|---|---|---|---|
| 108 | dev | icc | 0.26 | 0.37 |
| 108 | train | icc | 0.33 | 0.44 |
| 102 | dev | icc | 0.45 | 0.51 |
| 102 | train | icc | 0.47 | 0.52 |
| 42 | dev | noise_db | 11.52 | 12.66 |
| 99 | dev | icc | 0.36 | 0.40 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.9145 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 8.1915 | 8.2264 | 0.0349 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.8971 | 2.8070 | -0.0901 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 3.6761 | 3.6677 | -0.0084 | 0 | 0 | 1 |
| dev | attack_db | 156 | 8.0689 | 7.8155 | -0.2535 | 0 | 0 | 0 |
| dev | early_db | 156 | 8.8584 | 8.0816 | -0.7768 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 9.1106 | 8.7317 | -0.3789 | 0 | 0 | 0 |
| dev | noise_db | 153 | 9.8863 | 9.3001 | -0.5861 | 0 | 0 | 3 |
| dev | ild_db | 154 | 5.5873 | 5.5962 | 0.0089 | 0 | 0 | 2 |
| dev | icc | 154 | 0.2137 | 0.2184 | 0.0048 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 4.1817 | 4.1785 | -0.0032 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 15.0601 | 15.0634 | 0.0033 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.5238 | 2.5237 | -0.0001 | 0 | 0 | 0 |
| train | partial_db | 276 | 8.9418 | 8.9780 | 0.0361 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.7928 | 2.7218 | -0.0710 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 4.7472 | 4.7181 | -0.0292 | 0 | 0 | 5 |
| train | attack_db | 276 | 8.3878 | 8.1316 | -0.2562 | 0 | 0 | 0 |
| train | early_db | 276 | 9.3864 | 8.7105 | -0.6759 | 0 | 0 | 0 |
| train | sustain_db | 276 | 10.0943 | 9.6605 | -0.4339 | 0 | 0 | 0 |
| train | noise_db | 268 | 10.2308 | 9.6292 | -0.6016 | 0 | 0 | 8 |
| train | ild_db | 270 | 5.4667 | 5.4717 | 0.0051 | 0 | 0 | 6 |
| train | icc | 270 | 0.2127 | 0.2164 | 0.0037 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.2366 | 4.2315 | -0.0051 | 0 | 0 | 0 |
| train | rise_ms | 276 | 17.2643 | 17.2686 | 0.0043 | 0 | 0 | 0 |
| train | level_db | 276 | 2.6530 | 2.6518 | -0.0012 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 108 | dev | icc | 2 | 0.2551 | 0.3705 | 0.1155 |
| 108 | train | icc | 7 | 0.3258 | 0.4360 | 0.1102 |
| 102 | dev | icc | 4 | 0.4478 | 0.5136 | 0.0658 |
| 102 | train | icc | 12 | 0.4663 | 0.5240 | 0.0577 |
| 42 | dev | noise_db | 4 | 11.5162 | 12.6595 | 1.1433 |
| 99 | dev | icc | 16 | 0.3588 | 0.3967 | 0.0379 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
