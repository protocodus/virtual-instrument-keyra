# Recording benchmark: 2.5.0 against 2.4.0

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.4.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 8.63 | 4.25 | 5.05 | 7.58 | 9.70 | 10.88 | 10.26 | 6.53 | 0.25 | 4.17 | 15.50 | 4.37 |
| dev (21) | 9.57 | 4.32 | 5.51 | 7.50 | 9.12 | 10.56 | 9.80 | 5.24 | 0.26 | 4.53 | 13.10 | 3.02 |
| train / bass A0-B2 (30) | 10.53 | 5.09 | 5.28 | 7.87 | 9.65 | 10.30 | 15.63 | 6.00 | 0.22 | 3.09 | 20.61 | 3.63 |
| train / middle C3-B5 (69) | 8.55 | 3.61 | 4.53 | 7.44 | 8.59 | 8.92 | 8.90 | 6.50 | 0.20 | 3.97 | 19.04 | 4.73 |
| train / treble C6-C8 (38) | 7.28 | 4.75 | 5.88 | 7.61 | 11.74 | 14.90 | 8.40 | 7.04 | 0.38 | 5.39 | 5.06 | 4.29 |
| dev / bass A0-B2 (5) | 9.83 | 5.12 | 3.91 | 8.26 | 9.60 | 9.90 | 16.54 | 4.61 | 0.26 | 2.87 | 24.70 | 1.95 |
| dev / middle C3-B5 (11) | 8.46 | 3.97 | 5.01 | 6.80 | 7.67 | 8.76 | 7.69 | 6.65 | 0.21 | 4.22 | 11.22 | 3.48 |
| dev / treble C6-C8 (5) | 11.76 | 4.29 | 8.20 | 8.28 | 11.82 | 15.17 | 9.05 | 2.75 | 0.37 | 6.90 | 5.61 | 3.07 |

## 2.5.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 8.04 | 3.40 | 4.83 | 7.57 | 9.69 | 10.87 | 10.10 | 6.46 | 0.25 | 4.16 | 15.54 | 4.37 |
| dev (21) | 8.42 | 3.17 | 5.33 | 7.56 | 9.27 | 10.42 | 9.65 | 5.13 | 0.26 | 4.35 | 12.78 | 3.03 |
| train / bass A0-B2 (30) | 10.36 | 4.50 | 5.06 | 7.90 | 9.66 | 10.30 | 15.42 | 5.98 | 0.23 | 3.20 | 21.52 | 3.61 |
| train / middle C3-B5 (69) | 7.62 | 3.07 | 4.24 | 7.42 | 8.56 | 8.92 | 8.71 | 6.50 | 0.20 | 3.91 | 18.73 | 4.75 |
| train / treble C6-C8 (38) | 6.96 | 3.13 | 5.76 | 7.56 | 11.75 | 14.87 | 8.42 | 6.79 | 0.37 | 5.37 | 5.04 | 4.28 |
| dev / bass A0-B2 (5) | 9.87 | 4.49 | 4.06 | 8.34 | 9.86 | 9.80 | 16.10 | 4.48 | 0.27 | 2.39 | 24.50 | 1.96 |
| dev / middle C3-B5 (11) | 6.84 | 1.99 | 4.78 | 6.92 | 7.87 | 8.70 | 7.47 | 6.53 | 0.20 | 4.08 | 10.71 | 3.48 |
| dev / treble C6-C8 (5) | 10.46 | 4.43 | 7.80 | 8.21 | 11.78 | 14.84 | 9.29 | 2.70 | 0.37 | 6.91 | 5.61 | 3.12 |

## Independent-sample regressions (legacy)

Every note and role where 2.5.0 is worse than 2.4.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.4.0 | 2.5.0 |
|---|---|---|---|---|
| 24 | train | rise_ms | 6.50 | 21.63 |
| 78 | train | tuning_cents | 1.21 | 4.34 |
| 59 | dev | decay_db_s | 5.81 | 9.23 |
| 48 | train | tuning_cents | 3.00 | 4.44 |
| 86 | train | ild_db | 9.93 | 11.24 |
| 45 | train | tuning_cents | 3.25 | 4.09 |
| 59 | dev | noise_db | 7.25 | 7.99 |
| 70 | train | noise_db | 7.01 | 7.72 |
| 24 | train | partial_db | 12.44 | 13.12 |
| 27 | train | partial_db | 9.06 | 9.71 |
| 103 | train | partial_db | 4.07 | 4.60 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (11.5766 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 9.5730 | 8.4234 | -1.1495 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 4.3201 | 3.1685 | -1.1516 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 5.5072 | 5.3296 | -0.1776 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.4999 | 7.5644 | 0.0645 | 0 | 0 | 0 |
| dev | early_db | 21 | 9.1185 | 9.2725 | 0.1540 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 10.5552 | 10.4220 | -0.1332 | 0 | 0 | 0 |
| dev | noise_db | 20 | 9.7969 | 9.6507 | -0.1461 | 0 | 0 | 1 |
| dev | ild_db | 21 | 5.2364 | 5.1280 | -0.1083 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2578 | 0.2593 | 0.0016 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.5343 | 4.3506 | -0.1837 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 13.0952 | 12.7808 | -0.3145 | 0 | 0 | 0 |
| dev | level_db | 21 | 3.0210 | 3.0514 | 0.0303 | 0 | 0 | 0 |
| train | partial_db | 137 | 8.6315 | 8.0376 | -0.5940 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 4.2521 | 3.3986 | -0.8535 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 5.0543 | 4.8302 | -0.2242 | 0 | 0 | 2 |
| train | attack_db | 137 | 7.5847 | 7.5656 | -0.0191 | 0 | 0 | 0 |
| train | early_db | 137 | 9.6957 | 9.6880 | -0.0077 | 0 | 0 | 0 |
| train | sustain_db | 137 | 10.8847 | 10.8692 | -0.0155 | 0 | 0 | 0 |
| train | noise_db | 135 | 10.2570 | 10.1021 | -0.1549 | 0 | 2 | 0 |
| train | ild_db | 135 | 6.5344 | 6.4612 | -0.0732 | 0 | 0 | 2 |
| train | icc | 135 | 0.2521 | 0.2516 | -0.0005 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.1720 | 4.1589 | -0.0131 | 0 | 0 | 0 |
| train | rise_ms | 137 | 15.5038 | 15.5435 | 0.0397 | 0 | 0 | 0 |
| train | level_db | 137 | 4.3652 | 4.3694 | 0.0043 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 24 | train | rise_ms | 5 | 6.5000 | 21.6333 | 15.1333 |
| 78 | train | tuning_cents | 5 | 1.2085 | 4.3372 | 3.1286 |
| 59 | dev | decay_db_s | 1 | 5.8129 | 9.2301 | 3.4173 |
| 48 | train | tuning_cents | 5 | 2.9967 | 4.4431 | 1.4464 |
| 86 | train | ild_db | 5 | 9.9298 | 11.2396 | 1.3098 |
| 45 | train | tuning_cents | 5 | 3.2520 | 4.0924 | 0.8403 |
| 59 | dev | noise_db | 1 | 7.2498 | 7.9941 | 0.7443 |
| 70 | train | noise_db | 5 | 7.0069 | 7.7169 | 0.7100 |
| 24 | train | partial_db | 5 | 12.4438 | 13.1245 | 0.6807 |
| 27 | train | partial_db | 5 | 9.0571 | 9.7076 | 0.6505 |
| 103 | train | partial_db | 4 | 4.0683 | 4.6025 | 0.5343 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| n50v1r1 | 50 | train | noise_db | gained | - | 13.6806 |
| n50v3r1 | 50 | train | noise_db | gained | - | 6.1466 |
