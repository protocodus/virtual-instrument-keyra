# Recording benchmark: 0.4.26 against 0.4.25

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.25

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.55 | 0.19 | 1.85 | 4.43 | 4.25 | 4.66 | 5.86 | 0.91 | 0.06 | 1.95 | 3.12 | 0.53 |
| dev (156) | 5.22 | 1.06 | 2.12 | 4.80 | 4.53 | 5.20 | 5.40 | 2.44 | 0.11 | 2.59 | 4.61 | 0.96 |
| train / bass A0-B2 (84) | 4.70 | 0.04 | 0.44 | 4.80 | 3.96 | 3.75 | 5.93 | 0.40 | 0.03 | 2.12 | 3.89 | 0.39 |
| train / middle C3-B5 (108) | 4.90 | 0.07 | 1.44 | 3.99 | 4.07 | 3.48 | 6.15 | 0.70 | 0.05 | 0.82 | 2.91 | 0.36 |
| train / treble C6-C8 (84) | 3.94 | 0.50 | 3.92 | 4.62 | 4.75 | 7.07 | 5.44 | 1.74 | 0.12 | 3.25 | 2.63 | 0.88 |
| dev / bass A0-B2 (44) | 5.36 | 1.23 | 1.08 | 5.17 | 4.08 | 3.90 | 5.13 | 1.34 | 0.06 | 2.97 | 5.63 | 0.98 |
| dev / middle C3-B5 (68) | 6.30 | 0.65 | 2.47 | 4.68 | 4.92 | 5.60 | 5.79 | 3.63 | 0.10 | 1.87 | 5.45 | 0.87 |
| dev / treble C6-C8 (44) | 3.41 | 1.53 | 2.62 | 4.61 | 4.38 | 5.88 | 5.08 | 1.69 | 0.18 | 3.31 | 2.27 | 1.09 |

## 0.4.26

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.64 | 0.16 | 1.85 | 4.44 | 4.27 | 4.70 | 5.86 | 0.80 | 0.06 | 1.99 | 3.10 | 0.53 |
| dev (156) | 5.32 | 0.98 | 2.10 | 4.80 | 4.54 | 5.35 | 5.40 | 2.25 | 0.10 | 2.68 | 4.54 | 0.97 |
| train / bass A0-B2 (84) | 4.70 | 0.04 | 0.44 | 4.80 | 3.96 | 3.75 | 5.93 | 0.40 | 0.03 | 2.12 | 3.89 | 0.39 |
| train / middle C3-B5 (108) | 4.90 | 0.07 | 1.44 | 3.99 | 4.07 | 3.48 | 6.15 | 0.70 | 0.05 | 0.82 | 2.91 | 0.36 |
| train / treble C6-C8 (84) | 4.23 | 0.38 | 3.91 | 4.64 | 4.82 | 7.20 | 5.42 | 1.37 | 0.10 | 3.35 | 2.57 | 0.90 |
| dev / bass A0-B2 (44) | 5.36 | 1.23 | 1.08 | 5.17 | 4.08 | 3.90 | 5.13 | 1.34 | 0.06 | 2.97 | 5.63 | 0.98 |
| dev / middle C3-B5 (68) | 6.30 | 0.65 | 2.47 | 4.68 | 4.92 | 5.60 | 5.79 | 3.63 | 0.10 | 1.87 | 5.45 | 0.87 |
| dev / treble C6-C8 (44) | 3.76 | 1.24 | 2.55 | 4.63 | 4.43 | 6.41 | 5.07 | 0.97 | 0.15 | 3.65 | 2.06 | 1.12 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.26 is worse than 0.4.25 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.25 | 0.4.26 |
|---|---|---|---|---|
| 108 | dev | sustain_db | 16.28 | 17.61 |
| 108 | train | sustain_db | 17.07 | 18.28 |
| 108 | dev | partial_db | 10.19 | 11.39 |
| 99 | dev | sustain_db | 4.14 | 5.30 |
| 93 | dev | partial_db | 2.45 | 3.61 |
| 93 | train | partial_db | 2.51 | 3.64 |
| 108 | train | partial_db | 9.69 | 10.80 |
| 108 | dev | envelope_db | 2.54 | 3.63 |
| 102 | dev | sustain_db | 5.00 | 5.58 |
| 99 | dev | envelope_db | 3.26 | 3.79 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (25.8248 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 5.2204 | 5.3198 | 0.0994 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 1.0595 | 0.9789 | -0.0805 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 2.1170 | 2.0967 | -0.0203 | 0 | 0 | 1 |
| dev | attack_db | 156 | 4.7959 | 4.8019 | 0.0060 | 0 | 0 | 0 |
| dev | early_db | 156 | 4.5275 | 4.5417 | 0.0141 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 5.2005 | 5.3485 | 0.1480 | 0 | 0 | 0 |
| dev | noise_db | 153 | 5.4002 | 5.3986 | -0.0016 | 0 | 0 | 3 |
| dev | ild_db | 154 | 2.4449 | 2.2507 | -0.1942 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1114 | 0.1042 | -0.0072 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 2.5894 | 2.6846 | 0.0953 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 4.6055 | 4.5442 | -0.0613 | 0 | 0 | 0 |
| dev | level_db | 156 | 0.9611 | 0.9697 | 0.0086 | 0 | 0 | 0 |
| train | partial_db | 276 | 4.5456 | 4.6357 | 0.0901 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 0.1916 | 0.1552 | -0.0364 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 1.8531 | 1.8495 | -0.0036 | 0 | 0 | 5 |
| train | attack_db | 276 | 4.4313 | 4.4364 | 0.0051 | 0 | 0 | 0 |
| train | early_db | 276 | 4.2455 | 4.2652 | 0.0197 | 0 | 0 | 0 |
| train | sustain_db | 276 | 4.6575 | 4.6971 | 0.0395 | 0 | 0 | 0 |
| train | noise_db | 262 | 5.8603 | 5.8553 | -0.0050 | 0 | 0 | 14 |
| train | ild_db | 270 | 0.9066 | 0.8008 | -0.1058 | 0 | 0 | 6 |
| train | icc | 270 | 0.0642 | 0.0575 | -0.0067 | 0 | 0 | 6 |
| train | envelope_db | 276 | 1.9546 | 1.9864 | 0.0318 | 0 | 0 | 0 |
| train | rise_ms | 276 | 3.1221 | 3.1032 | -0.0189 | 0 | 0 | 0 |
| train | level_db | 276 | 0.5256 | 0.5308 | 0.0052 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 108 | dev | sustain_db | 4 | 16.2777 | 17.6075 | 1.3298 |
| 108 | train | sustain_db | 12 | 17.0707 | 18.2776 | 1.2068 |
| 108 | dev | partial_db | 4 | 10.1901 | 11.3877 | 1.1976 |
| 99 | dev | sustain_db | 16 | 4.1394 | 5.3005 | 1.1611 |
| 93 | dev | partial_db | 4 | 2.4520 | 3.6083 | 1.1563 |
| 93 | train | partial_db | 12 | 2.5145 | 3.6438 | 1.1293 |
| 108 | train | partial_db | 12 | 9.6863 | 10.7983 | 1.1120 |
| 108 | dev | envelope_db | 4 | 2.5372 | 3.6303 | 1.0931 |
| 102 | dev | sustain_db | 4 | 5.0003 | 5.5799 | 0.5796 |
| 99 | dev | envelope_db | 16 | 3.2558 | 3.7868 | 0.5310 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
