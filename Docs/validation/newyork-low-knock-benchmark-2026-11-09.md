# Recording benchmark: 0.4.28 against 0.4.27

Every train and dev note of `Tools/corpus/split-newyork-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

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

## 0.4.28

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (61) | 7.43 | 0.53 | 3.81 | 6.17 | 6.60 | 7.08 | 8.05 | 1.73 | 0.09 | 2.52 | 12.05 | 0.89 |
| dev (17) | 10.38 | 1.82 | 7.06 | 8.27 | 8.08 | 9.43 | 8.96 | 6.10 | 0.22 | 5.08 | 7.82 | 5.46 |
| train / bass A0-B2 (20) | 8.97 | 0.41 | 1.83 | 7.05 | 7.41 | 7.15 | 12.34 | 1.39 | 0.08 | 2.16 | 14.29 | 0.87 |
| train / middle C3-B5 (24) | 8.20 | 0.29 | 4.22 | 5.61 | 6.45 | 6.94 | 5.68 | 1.54 | 0.11 | 2.59 | 15.79 | 0.23 |
| train / treble C6-C8 (17) | 4.34 | 1.05 | 6.78 | 5.93 | 5.87 | 7.22 | 6.34 | 2.90 | 0.07 | 2.87 | 4.12 | 1.84 |
| dev / bass A0-B2 (5) | 10.31 | 2.18 | 2.69 | 7.14 | 8.09 | 8.94 | 11.37 | 3.93 | 0.13 | 4.20 | 8.36 | 3.69 |
| dev / middle C3-B5 (5) | 9.77 | 1.00 | 4.31 | 7.73 | 7.35 | 9.82 | 6.93 | 5.57 | 0.21 | 4.71 | 8.82 | 4.18 |
| dev / treble C6-C8 (7) | 10.86 | 2.14 | 12.15 | 9.47 | 8.59 | 9.50 | 8.68 | 8.03 | 0.29 | 5.98 | 6.73 | 7.64 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.28 is worse than 0.4.27 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.27 | 0.4.28 |
|---|---|---|---|---|
| 64 | dev | noise_db | 6.26 | 6.93 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.8471 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 17 | 10.3754 | 10.3770 | 0.0016 | 0 | 0 | 0 |
| dev | tuning_cents | 17 | 1.8171 | 1.8171 | -0.0000 | 0 | 0 | 0 |
| dev | decay_db_s | 17 | 7.0617 | 7.0618 | 0.0001 | 0 | 0 | 0 |
| dev | attack_db | 17 | 8.4177 | 8.2709 | -0.1467 | 0 | 0 | 0 |
| dev | early_db | 17 | 8.1749 | 8.0773 | -0.0976 | 0 | 0 | 0 |
| dev | sustain_db | 17 | 9.4348 | 9.4304 | -0.0043 | 0 | 0 | 0 |
| dev | noise_db | 17 | 8.9166 | 8.9576 | 0.0410 | 0 | 0 | 0 |
| dev | ild_db | 17 | 6.0998 | 6.0979 | -0.0018 | 0 | 0 | 0 |
| dev | icc | 17 | 0.2210 | 0.2209 | -0.0002 | 0 | 0 | 0 |
| dev | envelope_db | 17 | 5.0942 | 5.0842 | -0.0101 | 0 | 0 | 0 |
| dev | rise_ms | 17 | 8.0082 | 7.8207 | -0.1875 | 0 | 0 | 0 |
| dev | level_db | 17 | 5.4576 | 5.4613 | 0.0036 | 0 | 0 | 0 |
| train | partial_db | 60 | 7.4309 | 7.4287 | -0.0021 | 0 | 0 | 1 |
| train | tuning_cents | 60 | 0.5332 | 0.5332 | -0.0000 | 0 | 0 | 1 |
| train | decay_db_s | 54 | 3.8115 | 3.8114 | -0.0002 | 0 | 0 | 7 |
| train | attack_db | 61 | 6.2508 | 6.1730 | -0.0777 | 0 | 0 | 0 |
| train | early_db | 61 | 6.5847 | 6.6038 | 0.0191 | 0 | 0 | 0 |
| train | sustain_db | 59 | 7.0575 | 7.0797 | 0.0222 | 1 | 0 | 1 |
| train | noise_db | 61 | 8.0873 | 8.0463 | -0.0410 | 0 | 0 | 0 |
| train | ild_db | 54 | 1.7315 | 1.7328 | 0.0014 | 0 | 0 | 7 |
| train | icc | 54 | 0.0934 | 0.0934 | 0.0001 | 0 | 0 | 7 |
| train | envelope_db | 61 | 2.5278 | 2.5236 | -0.0041 | 0 | 0 | 0 |
| train | rise_ms | 61 | 12.0124 | 12.0452 | 0.0328 | 0 | 0 | 0 |
| train | level_db | 61 | 0.8929 | 0.8878 | -0.0050 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 64 | dev | noise_db | 5 | 6.2568 | 6.9333 | 0.6765 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| n104v3 | 104 | train | sustain_db | lost | 12.7557 | - |
