# Recording benchmark: 2.11.0 against 2.10.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.10.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 7.69 | 2.15 | 3.97 | 6.59 | 6.42 | 8.49 | 7.08 | 5.03 | 0.20 | 4.21 | 13.23 | 2.41 |
| dev (156) | 7.38 | 2.19 | 3.32 | 6.32 | 5.99 | 7.76 | 6.81 | 5.15 | 0.19 | 3.93 | 11.92 | 2.62 |
| train / bass A0-B2 (84) | 8.90 | 2.75 | 2.66 | 6.26 | 5.79 | 6.64 | 6.51 | 4.47 | 0.22 | 3.26 | 23.63 | 2.18 |
| train / middle C3-B5 (108) | 6.46 | 1.36 | 3.81 | 5.79 | 5.86 | 7.10 | 6.79 | 7.29 | 0.20 | 4.16 | 10.20 | 1.78 |
| train / treble C6-C8 (84) | 8.07 | 2.57 | 5.57 | 7.94 | 7.75 | 12.14 | 7.99 | 2.49 | 0.18 | 5.22 | 6.71 | 3.46 |
| dev / bass A0-B2 (44) | 9.71 | 3.20 | 2.42 | 6.01 | 5.29 | 5.98 | 6.44 | 4.72 | 0.23 | 2.78 | 21.99 | 2.84 |
| dev / middle C3-B5 (68) | 6.52 | 1.21 | 3.41 | 5.88 | 5.73 | 6.96 | 6.67 | 7.37 | 0.16 | 4.04 | 10.09 | 1.88 |
| dev / treble C6-C8 (44) | 6.36 | 2.71 | 4.12 | 7.30 | 7.08 | 10.76 | 7.37 | 2.00 | 0.21 | 4.90 | 4.69 | 3.55 |

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

## Independent-sample regressions (legacy)

Every note and role where 2.11.0 is worse than 2.10.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.10.0 | 2.11.0 |
|---|---|---|---|---|
| 24 | dev | rise_ms | 4.11 | 12.04 |
| 24 | train | rise_ms | 6.27 | 11.94 |
| 36 | dev | envelope_db | 5.55 | 7.75 |
| 36 | train | envelope_db | 5.51 | 7.54 |
| 36 | train | sustain_db | 7.64 | 8.53 |
| 36 | dev | sustain_db | 7.44 | 8.26 |
| 33 | dev | partial_db | 9.86 | 10.59 |
| 33 | dev | envelope_db | 2.78 | 3.44 |
| 33 | train | envelope_db | 2.81 | 3.43 |
| 33 | train | partial_db | 10.09 | 10.69 |
| 24 | train | tuning_cents | 3.96 | 4.47 |
| 33 | train | sustain_db | 7.73 | 8.24 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (23.8050 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 7.3761 | 7.4093 | 0.0332 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.1942 | 2.2106 | 0.0165 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 3.3240 | 3.2854 | -0.0386 | 0 | 0 | 1 |
| dev | attack_db | 156 | 6.3169 | 6.3201 | 0.0032 | 0 | 0 | 0 |
| dev | early_db | 156 | 5.9880 | 5.9753 | -0.0127 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 7.7551 | 7.7820 | 0.0269 | 0 | 0 | 0 |
| dev | noise_db | 153 | 6.8066 | 6.8383 | 0.0318 | 0 | 0 | 3 |
| dev | ild_db | 154 | 5.1461 | 5.1540 | 0.0079 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1940 | 0.1942 | 0.0002 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 3.9286 | 4.0017 | 0.0731 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 11.9223 | 12.0743 | 0.1520 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.6231 | 2.6149 | -0.0082 | 0 | 0 | 0 |
| train | partial_db | 276 | 7.6929 | 7.7162 | 0.0232 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.1504 | 2.1169 | -0.0336 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 3.9658 | 3.9040 | -0.0618 | 0 | 0 | 5 |
| train | attack_db | 276 | 6.5852 | 6.5974 | 0.0123 | 0 | 0 | 0 |
| train | early_db | 276 | 6.4164 | 6.3990 | -0.0174 | 0 | 0 | 0 |
| train | sustain_db | 276 | 8.4927 | 8.5506 | 0.0579 | 0 | 0 | 0 |
| train | noise_db | 274 | 7.0750 | 7.1186 | 0.0435 | 0 | 0 | 2 |
| train | ild_db | 270 | 5.0256 | 5.0267 | 0.0012 | 0 | 0 | 6 |
| train | icc | 270 | 0.2021 | 0.2026 | 0.0005 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.2076 | 4.3162 | 0.1086 | 0 | 0 | 0 |
| train | rise_ms | 276 | 13.2274 | 13.3022 | 0.0749 | 0 | 0 | 0 |
| train | level_db | 276 | 2.4110 | 2.4489 | 0.0379 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 24 | dev | rise_ms | 4 | 4.1094 | 12.0417 | 7.9323 |
| 24 | train | rise_ms | 12 | 6.2743 | 11.9392 | 5.6649 |
| 36 | dev | envelope_db | 4 | 5.5496 | 7.7508 | 2.2012 |
| 36 | train | envelope_db | 12 | 5.5133 | 7.5404 | 2.0271 |
| 36 | train | sustain_db | 12 | 7.6415 | 8.5307 | 0.8892 |
| 36 | dev | sustain_db | 4 | 7.4439 | 8.2555 | 0.8116 |
| 33 | dev | partial_db | 4 | 9.8551 | 10.5913 | 0.7362 |
| 33 | dev | envelope_db | 4 | 2.7847 | 3.4440 | 0.6593 |
| 33 | train | envelope_db | 12 | 2.8083 | 3.4269 | 0.6186 |
| 33 | train | partial_db | 12 | 10.0870 | 10.6918 | 0.6048 |
| 24 | train | tuning_cents | 12 | 3.9569 | 4.4702 | 0.5132 |
| 33 | train | sustain_db | 12 | 7.7293 | 8.2364 | 0.5071 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
