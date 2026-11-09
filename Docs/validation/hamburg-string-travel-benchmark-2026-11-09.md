# Recording benchmark: 0.4.29 against 0.4.28

Every train and dev note of `Tools/corpus/split-hamburg-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.28

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (40) | 4.45 | 0.27 | 2.30 | 6.09 | 4.42 | 4.98 | 6.55 | 1.54 | 0.11 | 3.11 | 16.86 | 0.55 |
| dev (8) | 7.12 | 2.53 | 3.68 | 7.39 | 6.29 | 6.19 | 6.16 | 4.87 | 0.23 | 2.32 | 3.12 | 3.10 |
| train / bass A0-B2 (16) | 4.66 | 0.10 | 0.99 | 6.52 | 3.74 | 3.73 | 7.95 | 0.84 | 0.07 | 2.40 | 31.40 | 0.56 |
| train / middle C3-B5 (12) | 4.64 | 0.24 | 2.11 | 6.15 | 4.47 | 4.75 | 6.10 | 1.99 | 0.13 | 1.82 | 12.06 | 0.23 |
| train / treble C6-C8 (12) | 3.98 | 0.52 | 4.23 | 5.47 | 5.27 | 6.87 | 5.48 | 2.02 | 0.16 | 5.34 | 2.30 | 0.87 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.12 | 2.53 | 3.68 | 7.39 | 6.29 | 6.19 | 6.16 | 4.87 | 0.23 | 2.32 | 3.12 | 3.10 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## 0.4.29

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (40) | 4.45 | 0.27 | 2.30 | 5.86 | 4.35 | 4.92 | 6.49 | 1.59 | 0.12 | 2.99 | 16.60 | 0.55 |
| dev (8) | 7.14 | 2.59 | 3.66 | 7.36 | 6.25 | 6.13 | 6.05 | 4.93 | 0.23 | 2.33 | 2.88 | 3.12 |
| train / bass A0-B2 (16) | 4.66 | 0.10 | 0.99 | 6.05 | 3.62 | 3.58 | 7.84 | 0.84 | 0.07 | 2.09 | 31.31 | 0.55 |
| train / middle C3-B5 (12) | 4.64 | 0.23 | 2.09 | 5.99 | 4.41 | 4.72 | 6.06 | 2.16 | 0.15 | 1.83 | 11.41 | 0.22 |
| train / treble C6-C8 (12) | 3.99 | 0.51 | 4.26 | 5.48 | 5.27 | 6.88 | 5.47 | 2.02 | 0.16 | 5.35 | 2.17 | 0.86 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.14 | 2.59 | 3.66 | 7.36 | 6.25 | 6.13 | 6.05 | 4.93 | 0.23 | 2.33 | 2.88 | 3.12 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## Independent-sample regressions (legacy)

Every note and role where 0.4.29 is worse than 0.4.28 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.28 | 0.4.29 |
|---|---|---|---|---|
| 80 | train | icc | 0.15 | 0.19 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (15.0229 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 8 | 7.1249 | 7.1446 | 0.0197 | 0 | 0 | 0 |
| dev | tuning_cents | 8 | 2.5327 | 2.5889 | 0.0562 | 0 | 0 | 0 |
| dev | decay_db_s | 8 | 3.6802 | 3.6551 | -0.0251 | 0 | 0 | 0 |
| dev | attack_db | 8 | 7.3931 | 7.3607 | -0.0324 | 0 | 0 | 0 |
| dev | early_db | 8 | 6.2870 | 6.2543 | -0.0327 | 0 | 0 | 0 |
| dev | sustain_db | 8 | 6.1865 | 6.1346 | -0.0519 | 0 | 0 | 0 |
| dev | noise_db | 6 | 6.1569 | 6.0459 | -0.1110 | 0 | 0 | 2 |
| dev | ild_db | 8 | 4.8719 | 4.9259 | 0.0540 | 0 | 0 | 0 |
| dev | icc | 8 | 0.2283 | 0.2333 | 0.0050 | 0 | 0 | 0 |
| dev | envelope_db | 8 | 2.3155 | 2.3312 | 0.0157 | 0 | 0 | 0 |
| dev | rise_ms | 8 | 3.1172 | 2.8828 | -0.2344 | 0 | 0 | 0 |
| dev | level_db | 8 | 3.0952 | 3.0856 | -0.0096 | 0 | 0 | 0 |
| train | partial_db | 40 | 4.4529 | 4.4547 | 0.0018 | 0 | 0 | 0 |
| train | tuning_cents | 40 | 0.2658 | 0.2657 | -0.0002 | 0 | 0 | 0 |
| train | decay_db_s | 40 | 2.3000 | 2.3025 | 0.0025 | 0 | 0 | 0 |
| train | attack_db | 40 | 6.0915 | 5.8631 | -0.2283 | 0 | 0 | 0 |
| train | early_db | 40 | 4.4202 | 4.3531 | -0.0671 | 0 | 0 | 0 |
| train | sustain_db | 40 | 4.9752 | 4.9150 | -0.0602 | 0 | 0 | 0 |
| train | noise_db | 37 | 6.5522 | 6.4941 | -0.0581 | 0 | 0 | 3 |
| train | ild_db | 40 | 1.5402 | 1.5905 | 0.0503 | 0 | 0 | 0 |
| train | icc | 40 | 0.1141 | 0.1177 | 0.0035 | 0 | 0 | 0 |
| train | envelope_db | 40 | 3.1072 | 2.9882 | -0.1190 | 0 | 0 | 0 |
| train | rise_ms | 40 | 16.8646 | 16.5964 | -0.2682 | 0 | 0 | 0 |
| train | level_db | 40 | 0.5528 | 0.5587 | 0.0059 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 80 | train | icc | 4 | 0.1541 | 0.1891 | 0.0350 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
