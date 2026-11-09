# Recording benchmark: 0.4.27 against 0.4.26

Every train and dev note of `Tools/corpus/split-vcsl-kawai-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.26

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (104) | 8.37 | 0.52 | 3.84 | 6.58 | 7.50 | 7.66 | 8.33 | 1.78 | 0.10 | 3.55 | 7.46 | 1.94 |
| dev (23) | 9.89 | 2.30 | 5.05 | 7.11 | 8.68 | 8.41 | 9.05 | 5.61 | 0.21 | 5.12 | 5.60 | 4.21 |
| train / bass A0-B2 (27) | 9.95 | 0.42 | 1.80 | 6.52 | 7.11 | 7.45 | 9.43 | 1.46 | 0.07 | 2.89 | 14.96 | 1.50 |
| train / middle C3-B5 (52) | 8.80 | 0.46 | 3.95 | 6.41 | 7.38 | 8.16 | 8.22 | 2.14 | 0.12 | 3.79 | 5.73 | 1.95 |
| train / treble C6-C8 (25) | 5.47 | 0.81 | 7.15 | 7.00 | 8.22 | 6.40 | 7.60 | 1.02 | 0.07 | 3.76 | 2.98 | 2.37 |
| dev / bass A0-B2 (8) | 10.45 | 2.09 | 2.58 | 6.08 | 6.17 | 8.53 | 9.56 | 3.27 | 0.15 | 3.83 | 9.17 | 1.73 |
| dev / middle C3-B5 (12) | 9.19 | 2.03 | 6.00 | 7.15 | 9.17 | 8.89 | 8.28 | 7.77 | 0.17 | 5.74 | 4.00 | 4.72 |
| dev / treble C6-C8 (3) | 11.87 | 4.82 | 9.20 | 9.70 | 13.47 | 4.99 | 10.46 | 3.09 | 0.66 | 6.08 | 2.48 | 8.79 |

## 0.4.27

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (104) | 8.31 | 0.54 | 3.91 | 6.56 | 7.48 | 7.86 | 8.30 | 1.76 | 0.10 | 3.53 | 7.45 | 1.93 |
| dev (23) | 9.64 | 2.39 | 5.04 | 7.09 | 8.64 | 8.39 | 9.04 | 5.59 | 0.20 | 5.08 | 5.45 | 4.21 |
| train / bass A0-B2 (27) | 9.92 | 0.44 | 1.86 | 6.51 | 7.07 | 7.44 | 9.42 | 1.43 | 0.07 | 2.89 | 14.97 | 1.50 |
| train / middle C3-B5 (52) | 8.75 | 0.51 | 4.15 | 6.41 | 7.39 | 8.52 | 8.14 | 2.13 | 0.11 | 3.79 | 5.69 | 1.96 |
| train / treble C6-C8 (25) | 5.29 | 0.76 | 6.80 | 6.94 | 8.16 | 6.40 | 7.64 | 1.02 | 0.07 | 3.66 | 2.99 | 2.35 |
| dev / bass A0-B2 (8) | 10.30 | 2.28 | 2.59 | 6.08 | 6.14 | 8.53 | 9.56 | 3.24 | 0.15 | 3.83 | 9.17 | 1.73 |
| dev / middle C3-B5 (12) | 9.15 | 2.14 | 6.01 | 7.15 | 9.20 | 8.89 | 8.42 | 7.76 | 0.16 | 5.73 | 3.72 | 4.72 |
| dev / treble C6-C8 (3) | 9.92 | 4.30 | 8.97 | 9.59 | 13.06 | 4.89 | 9.96 | 3.08 | 0.66 | 5.80 | 2.48 | 8.78 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.27 is worse than 0.4.26 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.26 | 0.4.27 |
|---|---|---|---|---|
| 80 | train | sustain_db | 5.87 | 11.20 |
| 103 | dev | early_db | 18.58 | 19.89 |
| 99 | train | tuning_cents | 0.26 | 1.43 |
| 87 | train | early_db | 5.32 | 6.29 |
| 84 | train | early_db | 6.16 | 7.08 |
| 84 | train | noise_db | 6.01 | 6.90 |
| 70 | train | decay_db_s | 3.10 | 4.51 |
| 87 | train | noise_db | 4.86 | 5.44 |
| 93 | train | early_db | 6.19 | 6.71 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.7441 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 22 | 9.8920 | 9.6370 | -0.2550 | 0 | 0 | 1 |
| dev | tuning_cents | 22 | 2.3044 | 2.3894 | 0.0850 | 0 | 0 | 1 |
| dev | decay_db_s | 22 | 5.0496 | 5.0367 | -0.0130 | 0 | 0 | 1 |
| dev | attack_db | 23 | 7.1081 | 7.0935 | -0.0146 | 0 | 0 | 0 |
| dev | early_db | 23 | 8.6849 | 8.6411 | -0.0438 | 0 | 0 | 0 |
| dev | sustain_db | 22 | 8.4083 | 8.3938 | -0.0145 | 0 | 0 | 1 |
| dev | noise_db | 22 | 9.0454 | 9.0413 | -0.0041 | 0 | 0 | 1 |
| dev | ild_db | 21 | 5.6064 | 5.5934 | -0.0130 | 0 | 0 | 2 |
| dev | icc | 21 | 0.2074 | 0.2045 | -0.0029 | 0 | 0 | 2 |
| dev | envelope_db | 23 | 5.1181 | 5.0817 | -0.0364 | 0 | 0 | 0 |
| dev | rise_ms | 23 | 5.6005 | 5.4533 | -0.1471 | 0 | 0 | 0 |
| dev | level_db | 23 | 4.2110 | 4.2094 | -0.0016 | 0 | 0 | 0 |
| train | partial_db | 100 | 8.3733 | 8.3070 | -0.0663 | 0 | 0 | 4 |
| train | tuning_cents | 100 | 0.5235 | 0.5439 | 0.0204 | 0 | 0 | 4 |
| train | decay_db_s | 93 | 3.8433 | 3.9123 | 0.0690 | 0 | 0 | 11 |
| train | attack_db | 104 | 6.5794 | 6.5634 | -0.0160 | 0 | 0 | 0 |
| train | early_db | 102 | 7.4992 | 7.4770 | -0.0222 | 0 | 0 | 2 |
| train | sustain_db | 94 | 7.6571 | 7.6524 | -0.0047 | 0 | 1 | 9 |
| train | noise_db | 95 | 8.3349 | 8.3049 | -0.0300 | 0 | 0 | 9 |
| train | ild_db | 90 | 1.7761 | 1.7569 | -0.0192 | 0 | 0 | 14 |
| train | icc | 90 | 0.0969 | 0.0962 | -0.0007 | 0 | 0 | 14 |
| train | envelope_db | 104 | 3.5509 | 3.5268 | -0.0241 | 0 | 0 | 0 |
| train | rise_ms | 104 | 7.4643 | 7.4491 | -0.0152 | 0 | 0 | 0 |
| train | level_db | 104 | 1.9366 | 1.9337 | -0.0029 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 103 | dev | early_db | 1 | 18.5809 | 19.8904 | 1.3095 |
| 99 | train | tuning_cents | 3 | 0.2572 | 1.4304 | 1.1732 |
| 87 | train | early_db | 3 | 5.3221 | 6.2870 | 0.9649 |
| 84 | train | early_db | 4 | 6.1638 | 7.0841 | 0.9202 |
| 84 | train | noise_db | 4 | 6.0102 | 6.8955 | 0.8853 |
| 70 | train | decay_db_s | 4 | 3.1005 | 4.5086 | 1.4080 |
| 87 | train | noise_db | 3 | 4.8597 | 5.4368 | 0.5772 |
| 93 | train | early_db | 3 | 6.1892 | 6.7078 | 0.5187 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| n80v2 | 80 | train | sustain_db | gained | - | 27.1435 |
