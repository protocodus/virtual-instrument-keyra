# Recording benchmark: 2.6.0 against 2.5.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.5.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.03 | 1.98 | 5.02 | 7.02 | 7.67 | 9.13 | 8.14 | 5.44 | 0.21 | 4.40 | 14.34 | 2.70 |
| dev (156) | 7.91 | 2.10 | 4.17 | 6.56 | 6.98 | 8.35 | 7.45 | 5.67 | 0.20 | 4.55 | 12.15 | 2.50 |
| train / bass A0-B2 (84) | 8.78 | 2.47 | 2.68 | 5.99 | 5.64 | 6.96 | 7.07 | 4.68 | 0.19 | 3.94 | 21.13 | 2.59 |
| train / middle C3-B5 (108) | 7.60 | 1.22 | 3.99 | 6.50 | 6.96 | 8.63 | 7.44 | 7.36 | 0.22 | 4.52 | 16.01 | 2.15 |
| train / treble C6-C8 (84) | 7.83 | 2.47 | 8.92 | 8.72 | 10.62 | 11.94 | 10.10 | 3.60 | 0.22 | 4.71 | 5.41 | 3.52 |
| dev / bass A0-B2 (44) | 9.50 | 3.04 | 2.42 | 6.01 | 5.77 | 6.56 | 6.96 | 5.06 | 0.21 | 3.41 | 21.64 | 3.34 |
| dev / middle C3-B5 (68) | 7.11 | 1.11 | 3.32 | 6.14 | 6.09 | 7.81 | 6.70 | 7.94 | 0.17 | 4.27 | 11.44 | 1.84 |
| dev / treble C6-C8 (44) | 7.55 | 2.69 | 7.29 | 7.75 | 9.58 | 10.97 | 9.05 | 2.63 | 0.25 | 6.12 | 3.78 | 2.67 |

## 2.6.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.03 | 2.00 | 5.02 | 6.85 | 7.14 | 9.11 | 7.69 | 5.45 | 0.20 | 4.40 | 14.32 | 2.68 |
| dev (156) | 7.90 | 2.10 | 4.16 | 6.39 | 6.49 | 8.33 | 7.00 | 5.67 | 0.20 | 4.54 | 12.16 | 2.49 |
| train / bass A0-B2 (84) | 8.78 | 2.47 | 2.68 | 5.99 | 5.64 | 6.96 | 7.07 | 4.68 | 0.19 | 3.94 | 21.13 | 2.61 |
| train / middle C3-B5 (108) | 7.60 | 1.22 | 3.99 | 6.49 | 6.93 | 8.62 | 7.39 | 7.36 | 0.22 | 4.52 | 16.01 | 2.14 |
| train / treble C6-C8 (84) | 7.84 | 2.55 | 8.93 | 8.16 | 8.91 | 11.87 | 8.69 | 3.64 | 0.20 | 4.70 | 5.33 | 3.45 |
| dev / bass A0-B2 (44) | 9.50 | 3.04 | 2.42 | 6.01 | 5.77 | 6.56 | 6.96 | 5.06 | 0.21 | 3.41 | 21.64 | 3.36 |
| dev / middle C3-B5 (68) | 7.11 | 1.11 | 3.32 | 6.14 | 6.07 | 7.81 | 6.67 | 7.94 | 0.17 | 4.27 | 11.44 | 1.84 |
| dev / treble C6-C8 (44) | 7.52 | 2.70 | 7.27 | 7.15 | 7.86 | 10.89 | 7.53 | 2.65 | 0.23 | 6.09 | 3.79 | 2.63 |

## Independent-sample regressions (legacy)

Every note and role where 2.6.0 is worse than 2.5.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.5.0 | 2.6.0 |
|---|---|---|---|---|
| 108 | dev | ild_db | 1.19 | 1.90 |
| 108 | train | ild_db | 1.19 | 1.71 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.6345 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 7.9075 | 7.9011 | -0.0064 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.0984 | 2.1036 | 0.0052 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 4.1668 | 4.1611 | -0.0057 | 0 | 0 | 1 |
| dev | attack_db | 156 | 6.5553 | 6.3850 | -0.1703 | 0 | 0 | 0 |
| dev | early_db | 156 | 6.9836 | 6.4896 | -0.4940 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 8.3486 | 8.3264 | -0.0223 | 0 | 0 | 0 |
| dev | noise_db | 153 | 7.4468 | 6.9999 | -0.4470 | 0 | 0 | 3 |
| dev | ild_db | 154 | 5.6669 | 5.6731 | 0.0062 | 0 | 0 | 2 |
| dev | icc | 154 | 0.2041 | 0.1980 | -0.0061 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 4.5464 | 4.5400 | -0.0064 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 12.1541 | 12.1568 | 0.0027 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.4956 | 2.4910 | -0.0046 | 0 | 0 | 0 |
| train | partial_db | 276 | 8.0280 | 8.0325 | 0.0045 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 1.9799 | 2.0042 | 0.0242 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 5.0224 | 5.0243 | 0.0019 | 0 | 0 | 5 |
| train | attack_db | 276 | 7.0194 | 6.8469 | -0.1725 | 0 | 0 | 0 |
| train | early_db | 276 | 7.6715 | 7.1375 | -0.5340 | 0 | 0 | 0 |
| train | sustain_db | 276 | 9.1274 | 9.1054 | -0.0220 | 0 | 0 | 0 |
| train | noise_db | 274 | 8.1428 | 7.6925 | -0.4504 | 0 | 0 | 2 |
| train | ild_db | 270 | 5.4407 | 5.4531 | 0.0124 | 0 | 0 | 6 |
| train | icc | 270 | 0.2107 | 0.2049 | -0.0059 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.4003 | 4.3979 | -0.0024 | 0 | 0 | 0 |
| train | rise_ms | 276 | 14.3433 | 14.3176 | -0.0257 | 0 | 0 | 0 |
| train | level_db | 276 | 2.7042 | 2.6862 | -0.0179 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 108 | dev | ild_db | 2 | 1.1929 | 1.8954 | 0.7025 |
| 108 | train | ild_db | 7 | 1.1929 | 1.7072 | 0.5143 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
