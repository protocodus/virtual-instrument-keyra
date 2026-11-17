# Recording benchmark: 2.24.0 against 2.23.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.23.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 7.79 | 2.22 | 3.96 | 6.63 | 6.59 | 8.71 | 7.95 | 5.03 | 0.20 | 4.23 | 14.04 | 2.56 |
| dev (156) | 7.26 | 2.54 | 3.42 | 6.36 | 6.08 | 7.79 | 7.56 | 5.02 | 0.18 | 3.92 | 12.25 | 2.81 |
| train / bass A0-B2 (84) | 8.72 | 2.94 | 2.66 | 5.80 | 5.47 | 6.38 | 8.33 | 4.35 | 0.20 | 3.52 | 25.81 | 2.02 |
| train / middle C3-B5 (108) | 7.13 | 1.26 | 3.90 | 6.05 | 6.23 | 7.93 | 7.22 | 6.58 | 0.20 | 3.90 | 10.44 | 2.09 |
| train / treble C6-C8 (84) | 7.69 | 2.74 | 5.44 | 8.20 | 8.17 | 12.03 | 8.50 | 3.60 | 0.19 | 5.36 | 6.88 | 3.72 |
| dev / bass A0-B2 (44) | 9.02 | 3.68 | 2.49 | 5.38 | 4.94 | 5.74 | 7.96 | 4.52 | 0.18 | 3.16 | 22.83 | 2.79 |
| dev / middle C3-B5 (68) | 6.85 | 1.19 | 3.56 | 6.16 | 5.84 | 7.21 | 7.00 | 6.77 | 0.15 | 3.69 | 10.18 | 2.16 |
| dev / treble C6-C8 (44) | 6.12 | 3.50 | 4.17 | 7.64 | 7.60 | 10.73 | 7.99 | 2.72 | 0.22 | 5.04 | 4.88 | 3.82 |

## 2.24.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 7.80 | 2.22 | 3.98 | 6.53 | 6.46 | 8.64 | 7.81 | 5.02 | 0.20 | 4.21 | 13.96 | 2.07 |
| dev (156) | 7.28 | 2.55 | 3.44 | 6.24 | 5.90 | 7.75 | 7.34 | 5.02 | 0.18 | 3.91 | 12.26 | 1.94 |
| train / bass A0-B2 (84) | 8.71 | 2.93 | 2.68 | 5.79 | 5.47 | 6.38 | 8.29 | 4.36 | 0.20 | 3.52 | 25.43 | 1.03 |
| train / middle C3-B5 (108) | 7.13 | 1.26 | 3.90 | 6.05 | 6.23 | 7.93 | 7.22 | 6.58 | 0.20 | 3.90 | 10.44 | 2.08 |
| train / treble C6-C8 (84) | 7.73 | 2.75 | 5.48 | 7.91 | 7.74 | 11.82 | 8.09 | 3.59 | 0.19 | 5.30 | 7.01 | 3.09 |
| dev / bass A0-B2 (44) | 9.12 | 3.65 | 2.52 | 5.37 | 4.94 | 5.74 | 7.80 | 4.52 | 0.18 | 3.16 | 22.82 | 0.91 |
| dev / middle C3-B5 (68) | 6.85 | 1.19 | 3.56 | 6.16 | 5.84 | 7.21 | 7.00 | 6.77 | 0.15 | 3.69 | 10.17 | 2.20 |
| dev / treble C6-C8 (44) | 6.10 | 3.55 | 4.21 | 7.24 | 6.94 | 10.61 | 7.39 | 2.72 | 0.22 | 5.00 | 4.91 | 2.56 |

## Independent-sample regressions (legacy)

Every note and role where 2.24.0 is worse than 2.23.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.3727 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 7.2568 | 7.2825 | 0.0256 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.5442 | 2.5509 | 0.0066 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 3.4231 | 3.4437 | 0.0207 | 0 | 0 | 1 |
| dev | attack_db | 156 | 6.3589 | 6.2428 | -0.1161 | 0 | 0 | 0 |
| dev | early_db | 156 | 6.0810 | 5.8954 | -0.1856 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 7.7871 | 7.7530 | -0.0341 | 0 | 0 | 0 |
| dev | noise_db | 153 | 7.5555 | 7.3371 | -0.2184 | 0 | 0 | 3 |
| dev | ild_db | 154 | 5.0217 | 5.0217 | 0.0000 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1789 | 0.1786 | -0.0003 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 3.9213 | 3.9094 | -0.0120 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 12.2525 | 12.2587 | 0.0061 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.8076 | 2.0280 | -0.7796 | 0 | 0 | 0 |
| train | partial_db | 276 | 7.7877 | 7.7953 | 0.0075 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.2212 | 2.2225 | 0.0013 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 3.9626 | 3.9831 | 0.0205 | 0 | 0 | 5 |
| train | attack_db | 276 | 6.6273 | 6.5347 | -0.0926 | 0 | 0 | 0 |
| train | early_db | 276 | 6.5893 | 6.4579 | -0.1313 | 0 | 0 | 0 |
| train | sustain_db | 276 | 8.7066 | 8.6417 | -0.0649 | 0 | 0 | 0 |
| train | noise_db | 273 | 7.9495 | 7.8094 | -0.1401 | 0 | 0 | 3 |
| train | ild_db | 270 | 5.0258 | 5.0248 | -0.0010 | 0 | 0 | 6 |
| train | icc | 270 | 0.1962 | 0.1959 | -0.0004 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.2284 | 4.2123 | -0.0161 | 0 | 0 | 0 |
| train | rise_ms | 276 | 14.0362 | 13.9580 | -0.0782 | 0 | 0 | 0 |
| train | level_db | 276 | 2.5637 | 2.1116 | -0.4521 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 78 | train | level_db | 12 | 4.0844 | 4.8320 | 0.7476 |
| 72 | train | level_db | 12 | 2.1229 | 2.8704 | 0.7475 |
| 72 | dev | level_db | 4 | 2.1671 | 2.9146 | 0.7475 |
| 33 | dev | level_db | 4 | 1.1838 | 1.9313 | 0.7475 |
| 78 | dev | level_db | 4 | 3.9973 | 4.7448 | 0.7475 |
| 75 | dev | level_db | 16 | 3.3997 | 4.1472 | 0.7475 |
| 42 | train | level_db | 12 | 1.2602 | 2.0076 | 0.7474 |
| 42 | dev | level_db | 4 | 1.4614 | 2.2087 | 0.7473 |
| 60 | dev | level_db | 4 | 0.9611 | 1.7081 | 0.7471 |
| 33 | train | level_db | 12 | 1.0362 | 1.6506 | 0.6145 |
| 60 | train | level_db | 12 | 1.2379 | 1.8519 | 0.6140 |
| 69 | train | level_db | 12 | 0.6937 | 1.2606 | 0.5669 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
