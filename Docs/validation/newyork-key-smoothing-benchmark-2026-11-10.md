# Recording benchmark: 0.4.32 against 0.4.31

Every train and dev note of `Tools/corpus/split-newyork-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.31

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (61) | 7.41 | 0.53 | 3.82 | 6.01 | 6.35 | 6.99 | 6.46 | 1.74 | 0.09 | 2.56 | 11.88 | 0.90 |
| dev (17) | 10.42 | 1.87 | 7.08 | 8.07 | 8.05 | 9.46 | 8.02 | 6.09 | 0.22 | 5.08 | 7.79 | 5.46 |
| train / bass A0-B2 (20) | 8.89 | 0.39 | 1.83 | 6.52 | 6.63 | 6.90 | 7.61 | 1.42 | 0.08 | 2.29 | 13.73 | 0.88 |
| train / middle C3-B5 (24) | 8.23 | 0.30 | 4.23 | 5.64 | 6.45 | 6.93 | 5.58 | 1.54 | 0.11 | 2.57 | 15.83 | 0.25 |
| train / treble C6-C8 (17) | 4.34 | 1.05 | 6.78 | 5.93 | 5.87 | 7.22 | 6.34 | 2.90 | 0.07 | 2.87 | 4.12 | 1.84 |
| dev / bass A0-B2 (5) | 10.47 | 2.25 | 2.73 | 6.72 | 7.99 | 9.03 | 8.58 | 3.93 | 0.13 | 4.19 | 8.82 | 3.70 |
| dev / middle C3-B5 (5) | 9.77 | 1.00 | 4.29 | 7.43 | 7.34 | 9.81 | 6.51 | 5.58 | 0.21 | 4.71 | 8.33 | 4.16 |
| dev / treble C6-C8 (7) | 10.84 | 2.22 | 12.16 | 9.48 | 8.60 | 9.51 | 8.69 | 7.99 | 0.29 | 5.98 | 6.66 | 7.64 |

## 0.4.32

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (61) | 7.36 | 0.46 | 3.70 | 5.87 | 6.32 | 6.98 | 6.45 | 2.43 | 0.09 | 2.55 | 11.76 | 1.45 |
| dev (17) | 10.40 | 1.84 | 7.09 | 8.02 | 8.03 | 9.40 | 8.07 | 6.04 | 0.22 | 5.07 | 7.84 | 5.51 |
| train / bass A0-B2 (20) | 8.97 | 0.36 | 1.84 | 6.41 | 6.62 | 6.92 | 7.50 | 1.63 | 0.08 | 2.30 | 13.71 | 1.33 |
| train / middle C3-B5 (24) | 8.03 | 0.26 | 4.14 | 5.55 | 6.40 | 6.80 | 5.73 | 2.57 | 0.11 | 2.60 | 15.74 | 1.10 |
| train / treble C6-C8 (17) | 4.36 | 0.89 | 6.36 | 5.70 | 5.87 | 7.34 | 6.24 | 3.70 | 0.07 | 2.78 | 3.86 | 2.09 |
| dev / bass A0-B2 (5) | 10.57 | 2.18 | 2.73 | 6.69 | 7.96 | 9.02 | 8.67 | 3.93 | 0.13 | 4.19 | 8.81 | 3.85 |
| dev / middle C3-B5 (5) | 9.54 | 0.98 | 4.25 | 7.19 | 7.20 | 9.62 | 6.51 | 5.23 | 0.21 | 4.71 | 8.55 | 3.93 |
| dev / treble C6-C8 (7) | 10.90 | 2.21 | 12.23 | 9.57 | 8.67 | 9.51 | 8.77 | 8.12 | 0.29 | 5.96 | 6.63 | 7.82 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.32 is worse than 0.4.31 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.31 | 0.4.32 |
|---|---|---|---|---|
| 99 | train | ild_db | 2.55 | 5.30 |
| 74 | train | ild_db | 1.44 | 3.73 |
| 69 | train | level_db | 0.18 | 2.12 |
| 79 | train | ild_db | 1.04 | 2.49 |
| 89 | train | level_db | 0.13 | 1.40 |
| 49 | train | level_db | 0.28 | 1.53 |
| 100 | dev | ild_db | 1.02 | 2.00 |
| 34 | train | level_db | 0.54 | 1.50 |
| 99 | train | sustain_db | 7.49 | 8.37 |
| 29 | train | level_db | 0.53 | 1.35 |
| 49 | train | ild_db | 0.99 | 1.78 |
| 94 | train | ild_db | 5.47 | 6.13 |
| 69 | train | ild_db | 1.32 | 1.97 |
| 74 | train | level_db | 0.12 | 0.63 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.8189 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 17 | 10.4187 | 10.4045 | -0.0142 | 0 | 0 | 0 |
| dev | tuning_cents | 17 | 1.8689 | 1.8392 | -0.0297 | 0 | 0 | 0 |
| dev | decay_db_s | 17 | 7.0763 | 7.0893 | 0.0129 | 0 | 0 | 0 |
| dev | attack_db | 17 | 8.0681 | 8.0231 | -0.0450 | 0 | 0 | 0 |
| dev | early_db | 17 | 8.0498 | 8.0272 | -0.0227 | 0 | 0 | 0 |
| dev | sustain_db | 17 | 9.4604 | 9.3996 | -0.0607 | 0 | 0 | 0 |
| dev | noise_db | 17 | 8.0177 | 8.0750 | 0.0573 | 0 | 0 | 0 |
| dev | ild_db | 17 | 6.0863 | 6.0378 | -0.0485 | 0 | 0 | 0 |
| dev | icc | 17 | 0.2208 | 0.2201 | -0.0007 | 0 | 0 | 0 |
| dev | envelope_db | 17 | 5.0818 | 5.0723 | -0.0094 | 0 | 0 | 0 |
| dev | rise_ms | 17 | 7.7852 | 7.8354 | 0.0502 | 0 | 0 | 0 |
| dev | level_db | 17 | 5.4594 | 4.8699 | -0.5895 | 0 | 0 | 0 |
| train | partial_db | 60 | 7.4137 | 7.3640 | -0.0497 | 0 | 0 | 1 |
| train | tuning_cents | 60 | 0.5303 | 0.4608 | -0.0695 | 0 | 0 | 1 |
| train | decay_db_s | 54 | 3.8153 | 3.6999 | -0.1154 | 0 | 0 | 7 |
| train | attack_db | 61 | 6.0096 | 5.8719 | -0.1377 | 0 | 0 | 0 |
| train | early_db | 61 | 6.3472 | 6.3243 | -0.0228 | 0 | 0 | 0 |
| train | sustain_db | 59 | 6.9928 | 6.9737 | -0.0191 | 0 | 1 | 1 |
| train | noise_db | 61 | 6.4567 | 6.4531 | -0.0036 | 0 | 0 | 0 |
| train | ild_db | 54 | 1.7445 | 2.4283 | 0.6838 | 0 | 0 | 7 |
| train | icc | 54 | 0.0926 | 0.0930 | 0.0004 | 0 | 0 | 7 |
| train | envelope_db | 61 | 2.5613 | 2.5544 | -0.0068 | 0 | 0 | 0 |
| train | rise_ms | 61 | 11.8809 | 11.7631 | -0.1178 | 0 | 0 | 0 |
| train | level_db | 61 | 0.8987 | 1.7417 | 0.8431 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 99 | train | ild_db | 2 | 2.5517 | 5.2975 | 2.7457 |
| 69 | train | level_db | 5 | 0.1750 | 2.7622 | 2.5872 |
| 74 | train | ild_db | 5 | 1.4434 | 3.7299 | 2.2865 |
| 89 | train | level_db | 5 | 0.1293 | 2.0299 | 1.9006 |
| 49 | train | level_db | 5 | 0.2750 | 2.1723 | 1.8973 |
| 34 | train | level_db | 5 | 0.5395 | 2.1385 | 1.5990 |
| 79 | train | ild_db | 4 | 1.0394 | 2.4922 | 1.4528 |
| 74 | train | level_db | 5 | 0.1187 | 1.2575 | 1.1387 |
| 100 | dev | ild_db | 1 | 1.0198 | 1.9961 | 0.9763 |
| 99 | train | sustain_db | 4 | 7.4920 | 8.3705 | 0.8785 |
| 49 | train | ild_db | 5 | 0.9856 | 1.7843 | 0.7987 |
| 94 | train | ild_db | 3 | 5.4721 | 6.1316 | 0.6595 |
| 69 | train | ild_db | 5 | 1.3191 | 1.9690 | 0.6499 |
| 29 | train | level_db | 5 | 0.5285 | 1.0758 | 0.5474 |
| 24 | train | level_db | 5 | 0.9425 | 1.4778 | 0.5353 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| n104v3 | 104 | train | sustain_db | gained | - | 7.4085 |
