# Recording benchmark: 2.20.0 against 2.19.0

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.19.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.28 | 3.22 | 4.62 | 7.69 | 9.13 | 10.44 | 10.15 | 6.56 | 0.24 | 4.25 | 11.83 | 4.31 |
| dev (21) | 7.24 | 3.71 | 5.00 | 7.52 | 8.95 | 9.89 | 8.73 | 6.49 | 0.27 | 4.64 | 9.11 | 3.26 |
| train / bass A0-B2 (30) | 9.57 | 4.85 | 4.45 | 8.60 | 9.37 | 10.34 | 15.58 | 6.48 | 0.19 | 2.89 | 6.82 | 3.67 |
| train / middle C3-B5 (69) | 7.07 | 2.73 | 4.44 | 7.42 | 8.22 | 8.20 | 8.99 | 6.29 | 0.20 | 3.77 | 18.08 | 4.72 |
| train / treble C6-C8 (38) | 5.87 | 2.83 | 5.11 | 7.46 | 10.59 | 14.60 | 7.98 | 7.13 | 0.37 | 6.20 | 4.45 | 4.08 |
| dev / bass A0-B2 (5) | 9.66 | 3.40 | 2.93 | 8.97 | 10.01 | 10.42 | 12.68 | 4.56 | 0.30 | 2.10 | 1.99 | 2.43 |
| dev / middle C3-B5 (11) | 6.26 | 2.38 | 4.63 | 6.78 | 7.38 | 8.04 | 7.08 | 7.64 | 0.22 | 4.76 | 14.56 | 3.62 |
| dev / treble C6-C8 (5) | 6.98 | 6.94 | 7.89 | 7.72 | 11.33 | 13.44 | 8.39 | 5.90 | 0.35 | 6.89 | 4.22 | 3.27 |

## 2.20.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.30 | 3.23 | 4.60 | 7.78 | 9.25 | 10.46 | 10.68 | 6.55 | 0.24 | 4.25 | 11.80 | 4.31 |
| dev (21) | 7.19 | 3.67 | 5.05 | 7.61 | 8.99 | 9.90 | 9.35 | 6.49 | 0.27 | 4.64 | 9.10 | 3.25 |
| train / bass A0-B2 (30) | 9.71 | 4.86 | 4.35 | 8.97 | 9.90 | 10.41 | 17.55 | 6.48 | 0.19 | 2.88 | 6.79 | 3.64 |
| train / middle C3-B5 (69) | 7.04 | 2.75 | 4.44 | 7.43 | 8.22 | 8.20 | 9.18 | 6.29 | 0.20 | 3.77 | 18.02 | 4.72 |
| train / treble C6-C8 (38) | 5.88 | 2.82 | 5.12 | 7.47 | 10.60 | 14.60 | 7.98 | 7.13 | 0.37 | 6.20 | 4.45 | 4.09 |
| dev / bass A0-B2 (5) | 9.52 | 3.42 | 3.04 | 9.42 | 10.21 | 10.44 | 14.96 | 4.56 | 0.30 | 2.11 | 2.01 | 2.41 |
| dev / middle C3-B5 (11) | 6.23 | 2.40 | 4.63 | 6.77 | 7.39 | 8.04 | 7.25 | 7.63 | 0.22 | 4.77 | 14.54 | 3.63 |
| dev / treble C6-C8 (5) | 6.96 | 6.71 | 8.01 | 7.66 | 11.29 | 13.44 | 8.34 | 5.90 | 0.35 | 6.89 | 4.25 | 3.27 |

## Independent-sample regressions (legacy)

Every note and role where 2.20.0 is worse than 2.19.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.19.0 | 2.20.0 |
|---|---|---|---|---|
| 42 | train | noise_db | 14.71 | 17.05 |
| 24 | train | noise_db | 17.63 | 19.91 |
| 39 | dev | noise_db | 12.68 | 14.96 |
| 33 | train | noise_db | 15.37 | 17.62 |
| 27 | train | noise_db | 19.30 | 21.30 |
| 45 | train | noise_db | 14.82 | 16.56 |
| 48 | train | noise_db | 15.62 | 16.86 |
| 36 | train | noise_db | 11.63 | 12.87 |
| 24 | train | early_db | 8.89 | 9.86 |
| 27 | train | early_db | 9.84 | 10.69 |
| 27 | train | attack_db | 6.68 | 7.37 |
| 52 | train | noise_db | 9.15 | 9.80 |
| 33 | train | early_db | 10.17 | 10.75 |
| 33 | train | attack_db | 10.20 | 10.75 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.7491 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 7.2422 | 7.1855 | -0.0567 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 3.7067 | 3.6680 | -0.0387 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 5.0003 | 5.0538 | 0.0535 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.5244 | 7.6132 | 0.0887 | 0 | 0 | 0 |
| dev | early_db | 21 | 8.9479 | 8.9921 | 0.0442 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 9.8940 | 9.8984 | 0.0044 | 0 | 0 | 0 |
| dev | noise_db | 21 | 8.7274 | 9.3480 | 0.6207 | 0 | 0 | 0 |
| dev | ild_db | 21 | 6.4889 | 6.4872 | -0.0017 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2731 | 0.2730 | -0.0001 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.6365 | 4.6388 | 0.0024 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 9.1071 | 9.1042 | -0.0030 | 0 | 0 | 0 |
| dev | level_db | 21 | 3.2578 | 3.2523 | -0.0054 | 0 | 0 | 0 |
| train | partial_db | 137 | 7.2847 | 7.3048 | 0.0201 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 3.2197 | 3.2326 | 0.0129 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 4.6223 | 4.5994 | -0.0229 | 0 | 0 | 2 |
| train | attack_db | 137 | 7.6861 | 7.7789 | 0.0928 | 0 | 0 | 0 |
| train | early_db | 137 | 9.1282 | 9.2499 | 0.1217 | 0 | 0 | 0 |
| train | sustain_db | 137 | 10.4434 | 10.4552 | 0.0118 | 0 | 0 | 0 |
| train | noise_db | 137 | 10.1537 | 10.6786 | 0.5250 | 0 | 0 | 0 |
| train | ild_db | 135 | 6.5574 | 6.5543 | -0.0031 | 0 | 0 | 2 |
| train | icc | 135 | 0.2424 | 0.2422 | -0.0002 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.2511 | 4.2478 | -0.0034 | 0 | 0 | 0 |
| train | rise_ms | 137 | 11.8324 | 11.8000 | -0.0324 | 0 | 0 | 0 |
| train | level_db | 137 | 4.3138 | 4.3079 | -0.0059 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 42 | train | noise_db | 5 | 14.7054 | 17.0502 | 2.3447 |
| 24 | train | noise_db | 5 | 17.6331 | 19.9111 | 2.2780 |
| 39 | dev | noise_db | 5 | 12.6847 | 14.9580 | 2.2733 |
| 33 | train | noise_db | 5 | 15.3727 | 17.6240 | 2.2513 |
| 27 | train | noise_db | 5 | 19.2974 | 21.2964 | 1.9989 |
| 45 | train | noise_db | 5 | 14.8158 | 16.5621 | 1.7463 |
| 48 | train | noise_db | 5 | 15.6244 | 16.8617 | 1.2373 |
| 36 | train | noise_db | 5 | 11.6336 | 12.8699 | 1.2363 |
| 24 | train | early_db | 5 | 8.8876 | 9.8642 | 0.9766 |
| 27 | train | early_db | 5 | 9.8386 | 10.6902 | 0.8516 |
| 27 | train | attack_db | 5 | 6.6771 | 7.3699 | 0.6928 |
| 52 | train | noise_db | 5 | 9.1478 | 9.7992 | 0.6514 |
| 33 | train | early_db | 5 | 10.1732 | 10.7467 | 0.5735 |
| 33 | train | attack_db | 5 | 10.2014 | 10.7455 | 0.5441 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
