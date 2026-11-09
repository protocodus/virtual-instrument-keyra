# Recording benchmark: 0.4.30 against 0.4.29

Every train and dev note of `Tools/corpus/split-vcsl-kawai-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.29

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (104) | 8.32 | 0.54 | 3.94 | 6.49 | 7.54 | 7.89 | 8.37 | 1.76 | 0.10 | 3.51 | 7.35 | 1.93 |
| dev (23) | 9.63 | 2.41 | 5.03 | 6.90 | 8.72 | 8.39 | 9.02 | 5.60 | 0.20 | 5.08 | 4.83 | 4.23 |
| train / bass A0-B2 (27) | 9.91 | 0.41 | 1.84 | 6.77 | 7.14 | 7.54 | 9.59 | 1.42 | 0.07 | 2.91 | 14.96 | 1.49 |
| train / middle C3-B5 (52) | 8.78 | 0.52 | 4.20 | 6.35 | 7.45 | 8.53 | 8.28 | 2.12 | 0.12 | 3.78 | 5.54 | 1.96 |
| train / treble C6-C8 (25) | 5.30 | 0.78 | 6.81 | 6.48 | 8.20 | 6.40 | 7.40 | 1.04 | 0.07 | 3.61 | 2.89 | 2.34 |
| dev / bass A0-B2 (8) | 10.29 | 2.33 | 2.59 | 5.93 | 6.10 | 8.52 | 9.63 | 3.25 | 0.15 | 3.85 | 8.44 | 1.76 |
| dev / middle C3-B5 (12) | 9.15 | 2.15 | 5.99 | 7.18 | 9.36 | 8.89 | 8.59 | 7.77 | 0.16 | 5.72 | 3.00 | 4.74 |
| dev / treble C6-C8 (3) | 9.93 | 4.30 | 8.97 | 8.37 | 13.19 | 4.90 | 8.96 | 3.09 | 0.66 | 5.74 | 2.49 | 8.79 |

## 0.4.30

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (104) | 7.86 | 0.50 | 3.85 | 6.46 | 7.47 | 7.85 | 8.39 | 1.77 | 0.10 | 3.52 | 7.35 | 1.93 |
| dev (23) | 9.50 | 2.39 | 5.03 | 6.90 | 8.71 | 8.39 | 9.02 | 5.60 | 0.20 | 5.08 | 4.83 | 4.23 |
| train / bass A0-B2 (27) | 9.83 | 0.41 | 1.84 | 6.77 | 7.13 | 7.54 | 9.57 | 1.42 | 0.07 | 2.91 | 14.94 | 1.48 |
| train / middle C3-B5 (52) | 7.92 | 0.44 | 4.05 | 6.30 | 7.33 | 8.45 | 8.34 | 2.14 | 0.12 | 3.79 | 5.54 | 1.96 |
| train / treble C6-C8 (25) | 5.30 | 0.78 | 6.81 | 6.48 | 8.20 | 6.40 | 7.40 | 1.04 | 0.07 | 3.61 | 2.89 | 2.34 |
| dev / bass A0-B2 (8) | 10.22 | 2.33 | 2.59 | 5.92 | 6.05 | 8.50 | 9.65 | 3.26 | 0.15 | 3.85 | 8.44 | 1.76 |
| dev / middle C3-B5 (12) | 8.95 | 2.11 | 5.99 | 7.18 | 9.37 | 8.89 | 8.59 | 7.76 | 0.16 | 5.72 | 3.00 | 4.74 |
| dev / treble C6-C8 (3) | 9.93 | 4.30 | 8.97 | 8.37 | 13.19 | 4.90 | 8.96 | 3.09 | 0.66 | 5.74 | 2.49 | 8.79 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.30 is worse than 0.4.29 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.29 | 0.4.30 |
|---|---|---|---|---|
| 56 | train | noise_db | 9.38 | 11.40 |
| 76 | train | decay_db_s | 5.19 | 6.42 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.7297 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 22 | 9.6322 | 9.4962 | -0.1360 | 0 | 0 | 1 |
| dev | tuning_cents | 22 | 2.4076 | 2.3864 | -0.0212 | 0 | 0 | 1 |
| dev | decay_db_s | 22 | 5.0265 | 5.0258 | -0.0007 | 0 | 0 | 1 |
| dev | attack_db | 23 | 6.8985 | 6.8957 | -0.0027 | 0 | 0 | 0 |
| dev | early_db | 23 | 8.7226 | 8.7105 | -0.0121 | 0 | 0 | 0 |
| dev | sustain_db | 22 | 8.3948 | 8.3871 | -0.0077 | 0 | 0 | 1 |
| dev | noise_db | 22 | 9.0176 | 9.0224 | 0.0048 | 0 | 0 | 1 |
| dev | ild_db | 21 | 5.5988 | 5.6007 | 0.0019 | 0 | 0 | 2 |
| dev | icc | 21 | 0.2038 | 0.2046 | 0.0008 | 0 | 0 | 2 |
| dev | envelope_db | 23 | 5.0762 | 5.0763 | 0.0001 | 0 | 0 | 0 |
| dev | rise_ms | 23 | 4.8261 | 4.8270 | 0.0009 | 0 | 0 | 0 |
| dev | level_db | 23 | 4.2293 | 4.2293 | -0.0001 | 0 | 0 | 0 |
| train | partial_db | 100 | 8.3181 | 7.8573 | -0.4608 | 0 | 0 | 4 |
| train | tuning_cents | 100 | 0.5446 | 0.5036 | -0.0410 | 0 | 0 | 4 |
| train | decay_db_s | 93 | 3.9366 | 3.8522 | -0.0844 | 0 | 0 | 11 |
| train | attack_db | 104 | 6.4926 | 6.4648 | -0.0278 | 0 | 0 | 0 |
| train | early_db | 102 | 7.5391 | 7.4715 | -0.0676 | 0 | 0 | 2 |
| train | sustain_db | 95 | 7.8914 | 7.8462 | -0.0452 | 0 | 0 | 9 |
| train | noise_db | 94 | 8.3967 | 8.3892 | -0.0075 | 1 | 0 | 9 |
| train | ild_db | 90 | 1.7567 | 1.7679 | 0.0112 | 0 | 0 | 14 |
| train | icc | 90 | 0.0968 | 0.0974 | 0.0006 | 0 | 0 | 14 |
| train | envelope_db | 104 | 3.5147 | 3.5159 | 0.0012 | 0 | 0 | 0 |
| train | rise_ms | 104 | 7.3509 | 7.3457 | -0.0052 | 0 | 0 | 0 |
| train | level_db | 104 | 1.9276 | 1.9290 | 0.0015 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 76 | train | decay_db_s | 4 | 5.1931 | 6.4210 | 1.2279 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| n56v2 | 56 | train | noise_db | lost | 5.4678 | - |
