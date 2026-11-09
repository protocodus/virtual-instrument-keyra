# Recording benchmark: 0.4.27 against 0.4.26

Every train and dev note of `Tools/corpus/split-newyork-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.26

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (61) | 7.67 | 0.53 | 3.89 | 6.28 | 6.72 | 7.30 | 8.14 | 1.73 | 0.09 | 2.59 | 12.06 | 0.90 |
| dev (17) | 10.35 | 1.73 | 7.07 | 8.45 | 8.64 | 9.90 | 9.34 | 6.11 | 0.23 | 5.22 | 7.99 | 5.45 |
| train / bass A0-B2 (20) | 9.04 | 0.36 | 1.84 | 7.06 | 7.46 | 7.16 | 12.40 | 1.39 | 0.08 | 2.16 | 14.39 | 0.87 |
| train / middle C3-B5 (24) | 8.25 | 0.25 | 4.35 | 5.61 | 6.42 | 6.97 | 5.57 | 1.53 | 0.11 | 2.59 | 15.86 | 0.23 |
| train / treble C6-C8 (17) | 5.10 | 1.18 | 6.90 | 6.31 | 6.27 | 8.02 | 6.77 | 2.93 | 0.07 | 3.10 | 3.94 | 1.88 |
| dev / bass A0-B2 (5) | 10.10 | 2.02 | 2.64 | 7.14 | 8.11 | 8.95 | 11.35 | 3.94 | 0.13 | 4.20 | 8.36 | 3.69 |
| dev / middle C3-B5 (5) | 9.77 | 0.99 | 4.30 | 7.48 | 7.66 | 9.83 | 6.84 | 5.62 | 0.22 | 4.72 | 9.09 | 4.18 |
| dev / treble C6-C8 (7) | 10.95 | 2.06 | 12.21 | 10.08 | 9.73 | 10.63 | 9.68 | 8.02 | 0.30 | 6.30 | 6.93 | 7.62 |

## 0.4.27

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (61) | 7.43 | 0.53 | 3.81 | 6.25 | 6.58 | 7.15 | 8.09 | 1.73 | 0.09 | 2.53 | 12.01 | 0.89 |
| dev (17) | 10.38 | 1.82 | 7.06 | 8.42 | 8.17 | 9.43 | 8.92 | 6.10 | 0.22 | 5.09 | 8.01 | 5.46 |
| train / bass A0-B2 (20) | 8.97 | 0.41 | 1.83 | 7.05 | 7.41 | 7.15 | 12.34 | 1.39 | 0.08 | 2.16 | 14.29 | 0.87 |
| train / middle C3-B5 (24) | 8.20 | 0.29 | 4.22 | 5.62 | 6.40 | 6.94 | 5.64 | 1.53 | 0.11 | 2.59 | 15.83 | 0.23 |
| train / treble C6-C8 (17) | 4.35 | 1.05 | 6.79 | 6.21 | 5.88 | 7.48 | 6.55 | 2.90 | 0.07 | 2.88 | 3.94 | 1.85 |
| dev / bass A0-B2 (5) | 10.31 | 2.18 | 2.69 | 7.14 | 8.09 | 8.94 | 11.37 | 3.93 | 0.13 | 4.20 | 8.36 | 3.69 |
| dev / middle C3-B5 (5) | 9.77 | 1.00 | 4.31 | 7.50 | 7.36 | 9.82 | 6.26 | 5.57 | 0.21 | 4.71 | 9.09 | 4.18 |
| dev / treble C6-C8 (7) | 10.85 | 2.14 | 12.15 | 9.99 | 8.82 | 9.51 | 9.06 | 8.03 | 0.29 | 6.00 | 6.99 | 7.63 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.27 is worse than 0.4.26 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.26 | 0.4.27 |
|---|---|---|---|---|
| 89 | train | early_db | 4.32 | 5.13 |
| 100 | dev | tuning_cents | 2.15 | 2.92 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.8464 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 17 | 10.3539 | 10.3754 | 0.0215 | 0 | 0 | 0 |
| dev | tuning_cents | 17 | 1.7312 | 1.8171 | 0.0859 | 0 | 0 | 0 |
| dev | decay_db_s | 17 | 7.0697 | 7.0617 | -0.0080 | 0 | 0 | 0 |
| dev | attack_db | 17 | 8.4511 | 8.4177 | -0.0334 | 0 | 0 | 0 |
| dev | early_db | 17 | 8.6433 | 8.1749 | -0.4684 | 0 | 0 | 0 |
| dev | sustain_db | 17 | 9.8992 | 9.4348 | -0.4644 | 0 | 0 | 0 |
| dev | noise_db | 17 | 9.3370 | 8.9166 | -0.4204 | 0 | 0 | 0 |
| dev | ild_db | 17 | 6.1102 | 6.0998 | -0.0104 | 0 | 0 | 0 |
| dev | icc | 17 | 0.2267 | 0.2210 | -0.0057 | 0 | 0 | 0 |
| dev | envelope_db | 17 | 5.2188 | 5.0942 | -0.1246 | 0 | 0 | 0 |
| dev | rise_ms | 17 | 7.9862 | 8.0082 | 0.0221 | 0 | 0 | 0 |
| dev | level_db | 17 | 5.4516 | 5.4570 | 0.0054 | 0 | 0 | 0 |
| train | partial_db | 60 | 7.6747 | 7.4309 | -0.2438 | 0 | 0 | 1 |
| train | tuning_cents | 60 | 0.5341 | 0.5332 | -0.0009 | 0 | 0 | 1 |
| train | decay_db_s | 54 | 3.8903 | 3.8115 | -0.0788 | 0 | 0 | 7 |
| train | attack_db | 61 | 6.2801 | 6.2508 | -0.0294 | 0 | 0 | 0 |
| train | early_db | 61 | 6.7201 | 6.5847 | -0.1354 | 0 | 0 | 0 |
| train | sustain_db | 59 | 7.2989 | 7.0575 | -0.2415 | 0 | 1 | 1 |
| train | noise_db | 61 | 8.1417 | 8.0873 | -0.0544 | 0 | 0 | 0 |
| train | ild_db | 54 | 1.7350 | 1.7315 | -0.0035 | 0 | 0 | 7 |
| train | icc | 54 | 0.0931 | 0.0934 | 0.0003 | 0 | 0 | 7 |
| train | envelope_db | 61 | 2.5877 | 2.5278 | -0.0599 | 0 | 0 | 0 |
| train | rise_ms | 61 | 12.0575 | 12.0124 | -0.0451 | 0 | 0 | 0 |
| train | level_db | 61 | 0.9012 | 0.8931 | -0.0082 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 89 | train | early_db | 5 | 4.3226 | 5.1262 | 0.8036 |
| 100 | dev | tuning_cents | 1 | 2.1509 | 2.9195 | 0.7686 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| n104v3 | 104 | train | sustain_db | gained | - | 12.7557 |
