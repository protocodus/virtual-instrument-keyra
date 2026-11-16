# Recording benchmark: 2.20.0 against 2.19.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.19.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 7.89 | 2.24 | 4.00 | 6.61 | 6.54 | 8.69 | 7.37 | 5.02 | 0.20 | 4.23 | 14.25 | 2.48 |
| dev (156) | 7.35 | 2.56 | 3.41 | 6.34 | 6.03 | 7.76 | 7.05 | 5.02 | 0.18 | 3.92 | 12.23 | 2.66 |
| train / bass A0-B2 (84) | 8.77 | 2.94 | 2.68 | 5.73 | 5.41 | 6.35 | 6.52 | 4.36 | 0.20 | 3.52 | 26.52 | 1.96 |
| train / middle C3-B5 (108) | 7.26 | 1.26 | 3.89 | 6.11 | 6.28 | 7.93 | 7.23 | 6.58 | 0.20 | 3.91 | 10.36 | 2.16 |
| train / treble C6-C8 (84) | 7.83 | 2.78 | 5.56 | 8.13 | 8.01 | 11.99 | 8.37 | 3.59 | 0.19 | 5.34 | 6.98 | 3.43 |
| dev / bass A0-B2 (44) | 9.06 | 3.64 | 2.52 | 5.33 | 4.86 | 5.67 | 6.44 | 4.52 | 0.18 | 3.16 | 22.78 | 2.60 |
| dev / middle C3-B5 (68) | 6.95 | 1.20 | 3.53 | 6.21 | 5.89 | 7.20 | 6.92 | 6.77 | 0.15 | 3.70 | 10.12 | 2.18 |
| dev / treble C6-C8 (44) | 6.25 | 3.57 | 4.12 | 7.54 | 7.41 | 10.70 | 7.83 | 2.71 | 0.22 | 5.03 | 4.93 | 3.45 |

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

## Independent-sample regressions (legacy)

Every note and role where 2.20.0 is worse than 2.19.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.19.0 | 2.20.0 |
|---|---|---|---|---|
| 24 | dev | noise_db | 5.97 | 9.34 |
| 24 | train | noise_db | 6.60 | 9.51 |
| 42 | dev | noise_db | 8.02 | 10.04 |
| 21 | train | noise_db | 6.30 | 8.25 |
| 33 | dev | noise_db | 4.48 | 6.40 |
| 36 | dev | noise_db | 3.18 | 4.85 |
| 33 | train | noise_db | 5.46 | 7.04 |
| 36 | train | noise_db | 4.90 | 6.44 |
| 30 | train | noise_db | 6.24 | 7.70 |
| 42 | train | noise_db | 8.85 | 10.15 |
| 30 | dev | noise_db | 6.18 | 7.32 |
| 27 | dev | noise_db | 7.62 | 8.33 |
| 21 | dev | noise_db | 6.22 | 6.76 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.5156 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 7.3452 | 7.3187 | -0.0265 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.5566 | 2.5343 | -0.0223 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 3.4089 | 3.4197 | 0.0108 | 0 | 0 | 1 |
| dev | attack_db | 156 | 6.3377 | 6.3543 | 0.0166 | 0 | 0 | 0 |
| dev | early_db | 156 | 6.0298 | 6.0477 | 0.0179 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 7.7566 | 7.7701 | 0.0135 | 0 | 0 | 0 |
| dev | noise_db | 153 | 7.0469 | 7.3412 | 0.2942 | 0 | 0 | 3 |
| dev | ild_db | 154 | 5.0202 | 5.0191 | -0.0012 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1788 | 0.1791 | 0.0002 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 3.9212 | 3.9227 | 0.0015 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 12.2277 | 12.2396 | 0.0119 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.6569 | 2.6515 | -0.0054 | 0 | 0 | 0 |
| train | partial_db | 276 | 7.8933 | 7.8759 | -0.0174 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.2353 | 2.2356 | 0.0003 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 3.9999 | 3.9990 | -0.0009 | 0 | 0 | 5 |
| train | attack_db | 276 | 6.6071 | 6.6229 | 0.0158 | 0 | 0 | 0 |
| train | early_db | 276 | 6.5431 | 6.5617 | 0.0185 | 0 | 0 | 0 |
| train | sustain_db | 276 | 8.6864 | 8.6951 | 0.0088 | 0 | 0 | 0 |
| train | noise_db | 273 | 7.3693 | 7.8044 | 0.4351 | 0 | 0 | 3 |
| train | ild_db | 270 | 5.0250 | 5.0248 | -0.0001 | 0 | 0 | 6 |
| train | icc | 270 | 0.1962 | 0.1964 | 0.0002 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.2257 | 4.2294 | 0.0037 | 0 | 0 | 0 |
| train | rise_ms | 276 | 14.2489 | 14.1917 | -0.0572 | 0 | 0 | 0 |
| train | level_db | 276 | 2.4839 | 2.4719 | -0.0120 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 24 | dev | noise_db | 4 | 5.9684 | 9.3357 | 3.3673 |
| 24 | train | noise_db | 12 | 6.6010 | 9.5146 | 2.9136 |
| 42 | dev | noise_db | 4 | 8.0178 | 10.0397 | 2.0219 |
| 21 | train | noise_db | 12 | 6.3017 | 8.2521 | 1.9504 |
| 33 | dev | noise_db | 4 | 4.4776 | 6.4044 | 1.9267 |
| 36 | dev | noise_db | 4 | 3.1824 | 4.8534 | 1.6710 |
| 33 | train | noise_db | 12 | 5.4621 | 7.0407 | 1.5786 |
| 36 | train | noise_db | 11 | 4.8997 | 6.4392 | 1.5395 |
| 30 | train | noise_db | 12 | 6.2373 | 7.7037 | 1.4664 |
| 42 | train | noise_db | 12 | 8.8540 | 10.1498 | 1.2958 |
| 30 | dev | noise_db | 4 | 6.1777 | 7.3241 | 1.1464 |
| 27 | dev | noise_db | 16 | 7.6153 | 8.3303 | 0.7150 |
| 21 | dev | noise_db | 4 | 6.2200 | 6.7626 | 0.5426 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
