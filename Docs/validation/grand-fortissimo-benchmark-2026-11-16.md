# Recording benchmark: 2.21.0 against 2.20.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.20.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 7.88 | 2.24 | 4.00 | 6.62 | 6.56 | 8.70 | 7.80 | 5.02 | 0.20 | 4.23 | 14.19 | 2.47 |
| dev (156) | 7.32 | 2.53 | 3.42 | 6.35 | 6.05 | 7.77 | 7.34 | 5.02 | 0.18 | 3.92 | 12.24 | 2.65 |
| train / bass A0-B2 (84) | 8.75 | 2.95 | 2.66 | 5.79 | 5.47 | 6.39 | 8.04 | 4.35 | 0.20 | 3.51 | 26.25 | 1.92 |
| train / middle C3-B5 (108) | 7.22 | 1.26 | 3.91 | 6.09 | 6.26 | 7.93 | 7.16 | 6.58 | 0.20 | 3.91 | 10.44 | 2.16 |
| train / treble C6-C8 (84) | 7.85 | 2.77 | 5.55 | 8.13 | 8.03 | 11.98 | 8.39 | 3.59 | 0.19 | 5.36 | 6.96 | 3.43 |
| dev / bass A0-B2 (44) | 9.04 | 3.64 | 2.50 | 5.38 | 4.94 | 5.74 | 7.73 | 4.52 | 0.18 | 3.16 | 22.82 | 2.56 |
| dev / middle C3-B5 (68) | 6.91 | 1.20 | 3.55 | 6.21 | 5.87 | 7.19 | 6.75 | 6.77 | 0.15 | 3.70 | 10.12 | 2.18 |
| dev / treble C6-C8 (44) | 6.23 | 3.49 | 4.15 | 7.56 | 7.43 | 10.69 | 7.85 | 2.71 | 0.22 | 5.04 | 4.93 | 3.46 |

## 2.21.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 7.77 | 2.22 | 3.96 | 6.64 | 6.60 | 8.71 | 8.17 | 5.03 | 0.20 | 4.23 | 13.97 | 2.54 |
| dev (156) | 7.23 | 2.55 | 3.43 | 6.37 | 6.09 | 7.79 | 7.82 | 5.02 | 0.18 | 3.92 | 12.12 | 2.77 |
| train / bass A0-B2 (84) | 8.66 | 2.94 | 2.66 | 5.84 | 5.51 | 6.40 | 9.01 | 4.35 | 0.20 | 3.51 | 25.50 | 1.91 |
| train / middle C3-B5 (108) | 7.13 | 1.26 | 3.90 | 6.04 | 6.23 | 7.93 | 7.25 | 6.58 | 0.20 | 3.90 | 10.52 | 2.11 |
| train / treble C6-C8 (84) | 7.69 | 2.74 | 5.44 | 8.20 | 8.17 | 12.03 | 8.50 | 3.59 | 0.19 | 5.36 | 6.88 | 3.72 |
| dev / bass A0-B2 (44) | 8.95 | 3.71 | 2.51 | 5.43 | 4.99 | 5.77 | 8.82 | 4.52 | 0.18 | 3.16 | 22.35 | 2.60 |
| dev / middle C3-B5 (68) | 6.84 | 1.19 | 3.56 | 6.16 | 5.84 | 7.21 | 7.06 | 6.77 | 0.15 | 3.69 | 10.18 | 2.20 |
| dev / treble C6-C8 (44) | 6.12 | 3.50 | 4.17 | 7.64 | 7.59 | 10.73 | 7.99 | 2.72 | 0.22 | 5.04 | 4.88 | 3.81 |

## Independent-sample regressions (legacy)

Every note and role where 2.21.0 is worse than 2.20.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.20.0 | 2.21.0 |
|---|---|---|---|---|
| 45 | dev | noise_db | 6.74 | 8.32 |
| 51 | dev | noise_db | 5.85 | 7.09 |
| 30 | dev | noise_db | 7.32 | 8.54 |
| 36 | dev | noise_db | 4.85 | 5.99 |
| 36 | train | noise_db | 6.44 | 7.57 |
| 45 | train | noise_db | 6.98 | 8.10 |
| 33 | dev | noise_db | 6.40 | 7.52 |
| 48 | dev | noise_db | 5.72 | 6.82 |
| 21 | dev | noise_db | 6.76 | 7.86 |
| 24 | dev | noise_db | 9.34 | 10.39 |
| 48 | train | noise_db | 4.96 | 6.00 |
| 30 | train | noise_db | 7.70 | 8.73 |
| 42 | dev | noise_db | 10.04 | 11.05 |
| 27 | dev | noise_db | 8.33 | 9.30 |
| 21 | train | noise_db | 8.25 | 9.20 |
| 42 | train | noise_db | 10.15 | 11.09 |
| 108 | dev | level_db | 4.88 | 5.74 |
| 24 | train | noise_db | 9.51 | 10.37 |
| 33 | train | noise_db | 7.04 | 7.84 |
| 108 | train | level_db | 4.90 | 5.60 |
| 93 | dev | level_db | 0.94 | 1.55 |
| 69 | dev | rise_ms | 3.07 | 4.10 |
| 102 | dev | level_db | 3.92 | 4.43 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.5474 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 7.3187 | 7.2314 | -0.0873 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.5343 | 2.5522 | 0.0179 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 3.4197 | 3.4281 | 0.0084 | 0 | 0 | 1 |
| dev | attack_db | 156 | 6.3543 | 6.3708 | 0.0166 | 0 | 0 | 0 |
| dev | early_db | 156 | 6.0477 | 6.0924 | 0.0447 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 7.7701 | 7.7946 | 0.0245 | 0 | 0 | 0 |
| dev | noise_db | 153 | 7.3412 | 7.8218 | 0.4806 | 0 | 0 | 3 |
| dev | ild_db | 154 | 5.0191 | 5.0221 | 0.0030 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1791 | 0.1789 | -0.0002 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 3.9227 | 3.9211 | -0.0016 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 12.2396 | 12.1185 | -0.1211 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.6483 | 2.8039 | 0.1556 | 0 | 0 | 0 |
| train | partial_db | 276 | 7.8759 | 7.7681 | -0.1079 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.2356 | 2.2208 | -0.0147 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 3.9990 | 3.9627 | -0.0363 | 0 | 0 | 5 |
| train | attack_db | 276 | 6.6229 | 6.6381 | 0.0152 | 0 | 0 | 0 |
| train | early_db | 276 | 6.5617 | 6.5988 | 0.0371 | 0 | 0 | 0 |
| train | sustain_db | 276 | 8.6951 | 8.7107 | 0.0155 | 0 | 0 | 0 |
| train | noise_db | 273 | 7.8044 | 8.1653 | 0.3609 | 0 | 0 | 3 |
| train | ild_db | 270 | 5.0248 | 5.0257 | 0.0009 | 0 | 0 | 6 |
| train | icc | 270 | 0.1964 | 0.1962 | -0.0001 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.2294 | 4.2281 | -0.0013 | 0 | 0 | 0 |
| train | rise_ms | 276 | 14.1917 | 13.9697 | -0.2220 | 0 | 0 | 0 |
| train | level_db | 276 | 2.4733 | 2.5340 | 0.0606 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 45 | dev | noise_db | 3 | 6.7365 | 8.3193 | 1.5828 |
| 51 | dev | noise_db | 14 | 5.8486 | 7.0905 | 1.2418 |
| 30 | dev | noise_db | 4 | 7.3241 | 8.5446 | 1.2205 |
| 36 | dev | noise_db | 4 | 4.8534 | 5.9872 | 1.1338 |
| 36 | train | noise_db | 11 | 6.4392 | 7.5678 | 1.1286 |
| 45 | train | noise_db | 11 | 6.9837 | 8.0993 | 1.1155 |
| 33 | dev | noise_db | 4 | 6.4044 | 7.5191 | 1.1147 |
| 48 | dev | noise_db | 4 | 5.7215 | 6.8211 | 1.0996 |
| 21 | dev | noise_db | 4 | 6.7626 | 7.8553 | 1.0928 |
| 24 | dev | noise_db | 4 | 9.3357 | 10.3860 | 1.0503 |
| 48 | train | noise_db | 11 | 4.9637 | 6.0005 | 1.0369 |
| 30 | train | noise_db | 12 | 7.7037 | 8.7272 | 1.0235 |
| 42 | dev | noise_db | 4 | 10.0397 | 11.0540 | 1.0143 |
| 27 | dev | noise_db | 16 | 8.3303 | 9.3037 | 0.9734 |
| 21 | train | noise_db | 12 | 8.2521 | 9.1959 | 0.9438 |
| 42 | train | noise_db | 12 | 10.1498 | 11.0866 | 0.9368 |
| 108 | dev | level_db | 4 | 4.8765 | 5.7363 | 0.8599 |
| 24 | train | noise_db | 12 | 9.5146 | 10.3678 | 0.8532 |
| 33 | train | noise_db | 12 | 7.0407 | 7.8392 | 0.7985 |
| 108 | train | level_db | 12 | 4.8951 | 5.6447 | 0.7496 |
| 93 | dev | level_db | 4 | 0.9393 | 1.5527 | 0.6133 |
| 60 | train | level_db | 12 | 1.0144 | 1.5338 | 0.5194 |
| 69 | dev | rise_ms | 4 | 3.0677 | 4.0990 | 1.0312 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
