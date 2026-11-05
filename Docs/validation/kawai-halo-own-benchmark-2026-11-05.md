# Recording benchmark: 0.4.24 against 0.4.23

Every train and dev note of `Tools/corpus/split-vcsl-kawai-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.23

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (104) | 8.39 | 0.54 | 3.84 | 8.21 | 8.84 | 8.47 | 8.33 | 1.77 | 0.10 | 3.55 | 7.46 | 1.89 |
| dev (23) | 10.12 | 2.91 | 5.48 | 8.70 | 10.15 | 9.64 | 9.06 | 5.28 | 0.21 | 5.39 | 6.08 | 4.35 |
| train / bass A0-B2 (27) | 9.97 | 0.43 | 1.78 | 9.07 | 9.53 | 8.72 | 9.44 | 1.46 | 0.07 | 2.89 | 14.96 | 1.38 |
| train / middle C3-B5 (52) | 8.80 | 0.45 | 3.96 | 7.79 | 8.34 | 8.55 | 8.19 | 2.13 | 0.12 | 3.79 | 5.71 | 1.99 |
| train / treble C6-C8 (25) | 5.48 | 0.89 | 7.15 | 8.13 | 9.16 | 7.79 | 7.63 | 1.02 | 0.07 | 3.77 | 2.99 | 2.24 |
| dev / bass A0-B2 (8) | 10.69 | 3.88 | 2.71 | 8.89 | 8.45 | 9.32 | 9.58 | 3.13 | 0.15 | 3.50 | 9.08 | 1.90 |
| dev / middle C3-B5 (12) | 9.56 | 2.23 | 5.58 | 8.09 | 9.98 | 10.27 | 8.18 | 7.14 | 0.17 | 6.64 | 4.88 | 4.88 |
| dev / treble C6-C8 (3) | 11.19 | 3.14 | 15.90 | 10.62 | 15.31 | 7.18 | 10.87 | 3.62 | 0.69 | 5.45 | 2.87 | 8.78 |

## 0.4.24

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (104) | 8.39 | 0.52 | 3.84 | 8.21 | 8.84 | 8.47 | 8.33 | 1.77 | 0.10 | 3.55 | 7.46 | 1.89 |
| dev (23) | 10.12 | 2.91 | 5.47 | 8.70 | 10.15 | 9.64 | 9.06 | 5.28 | 0.21 | 5.39 | 6.08 | 4.36 |
| train / bass A0-B2 (27) | 9.97 | 0.43 | 1.78 | 9.07 | 9.53 | 8.72 | 9.44 | 1.46 | 0.07 | 2.89 | 14.96 | 1.37 |
| train / middle C3-B5 (52) | 8.80 | 0.45 | 3.96 | 7.79 | 8.34 | 8.55 | 8.19 | 2.13 | 0.12 | 3.79 | 5.71 | 1.99 |
| train / treble C6-C8 (25) | 5.47 | 0.82 | 7.16 | 8.13 | 9.16 | 7.78 | 7.63 | 1.02 | 0.07 | 3.77 | 2.99 | 2.24 |
| dev / bass A0-B2 (8) | 10.69 | 3.88 | 2.71 | 8.89 | 8.45 | 9.32 | 9.58 | 3.13 | 0.15 | 3.50 | 9.08 | 1.90 |
| dev / middle C3-B5 (12) | 9.56 | 2.23 | 5.58 | 8.09 | 9.98 | 10.27 | 8.18 | 7.14 | 0.17 | 6.64 | 4.88 | 4.88 |
| dev / treble C6-C8 (3) | 11.19 | 3.14 | 15.80 | 10.62 | 15.31 | 7.18 | 10.87 | 3.62 | 0.69 | 5.45 | 2.87 | 8.78 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.24 is worse than 0.4.23 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (13.6244 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 22 | 10.1199 | 10.1194 | -0.0004 | 0 | 0 | 1 |
| dev | tuning_cents | 22 | 2.9132 | 2.9132 | -0.0000 | 0 | 0 | 1 |
| dev | decay_db_s | 22 | 5.4780 | 5.4696 | -0.0084 | 0 | 0 | 1 |
| dev | attack_db | 23 | 8.6974 | 8.6974 | -0.0000 | 0 | 0 | 0 |
| dev | early_db | 23 | 10.1464 | 10.1464 | -0.0000 | 0 | 0 | 0 |
| dev | sustain_db | 22 | 9.6410 | 9.6410 | 0.0001 | 0 | 0 | 1 |
| dev | noise_db | 22 | 9.0553 | 9.0553 | -0.0000 | 0 | 0 | 1 |
| dev | ild_db | 21 | 5.2767 | 5.2766 | -0.0000 | 0 | 0 | 2 |
| dev | icc | 21 | 0.2127 | 0.2127 | 0.0000 | 0 | 0 | 2 |
| dev | envelope_db | 23 | 5.3911 | 5.3911 | 0.0000 | 0 | 0 | 0 |
| dev | rise_ms | 23 | 6.0829 | 6.0829 | 0.0000 | 0 | 0 | 0 |
| dev | level_db | 23 | 4.3514 | 4.3514 | 0.0000 | 0 | 0 | 0 |
| train | partial_db | 100 | 8.3877 | 8.3869 | -0.0008 | 0 | 0 | 4 |
| train | tuning_cents | 100 | 0.5410 | 0.5244 | -0.0166 | 0 | 0 | 4 |
| train | decay_db_s | 93 | 3.8427 | 3.8445 | 0.0017 | 0 | 0 | 11 |
| train | attack_db | 104 | 8.2066 | 8.2065 | -0.0000 | 0 | 0 | 0 |
| train | early_db | 102 | 8.8430 | 8.8429 | -0.0001 | 0 | 0 | 2 |
| train | sustain_db | 94 | 8.4711 | 8.4701 | -0.0010 | 0 | 0 | 10 |
| train | noise_db | 95 | 8.3290 | 8.3289 | -0.0000 | 0 | 0 | 9 |
| train | ild_db | 90 | 1.7711 | 1.7708 | -0.0003 | 0 | 0 | 14 |
| train | icc | 90 | 0.0965 | 0.0965 | -0.0000 | 0 | 0 | 14 |
| train | envelope_db | 104 | 3.5524 | 3.5530 | 0.0006 | 0 | 0 | 0 |
| train | rise_ms | 104 | 7.4575 | 7.4573 | -0.0002 | 0 | 0 | 0 |
| train | level_db | 104 | 1.8885 | 1.8889 | 0.0004 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
