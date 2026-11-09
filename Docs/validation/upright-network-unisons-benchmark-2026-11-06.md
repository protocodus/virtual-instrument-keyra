# Recording benchmark: 0.4.26 against 0.4.25

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.25

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 5.76 | 0.28 | 2.38 | 5.15 | 5.28 | 5.73 | 7.42 | 2.13 | 0.14 | 2.62 | 7.80 | 1.19 |
| dev (21) | 8.23 | 1.81 | 3.99 | 6.46 | 7.26 | 8.64 | 6.85 | 4.22 | 0.21 | 4.51 | 6.19 | 2.52 |
| train / bass A0-B2 (30) | 6.90 | 0.29 | 1.93 | 5.61 | 5.18 | 5.36 | 10.26 | 1.28 | 0.10 | 2.51 | 8.78 | 0.95 |
| train / middle C3-B5 (69) | 6.58 | 0.23 | 2.55 | 5.34 | 4.94 | 5.45 | 7.58 | 1.94 | 0.10 | 2.14 | 9.54 | 1.39 |
| train / treble C6-C8 (38) | 3.37 | 0.36 | 2.42 | 4.43 | 5.97 | 6.56 | 5.44 | 3.20 | 0.24 | 3.59 | 3.87 | 1.03 |
| dev / bass A0-B2 (5) | 8.81 | 1.25 | 2.08 | 5.79 | 7.48 | 8.96 | 7.09 | 5.19 | 0.20 | 2.09 | 1.42 | 1.41 |
| dev / middle C3-B5 (11) | 8.45 | 0.95 | 3.82 | 7.07 | 6.94 | 8.02 | 6.93 | 4.22 | 0.17 | 4.56 | 10.54 | 2.71 |
| dev / treble C6-C8 (5) | 7.17 | 4.28 | 6.27 | 5.81 | 7.73 | 9.69 | 6.46 | 3.28 | 0.29 | 6.84 | 1.40 | 3.20 |

## 0.4.26

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 5.78 | 0.27 | 2.38 | 5.15 | 5.27 | 5.75 | 7.42 | 2.14 | 0.14 | 2.61 | 7.79 | 1.20 |
| dev (21) | 8.23 | 1.58 | 3.99 | 6.47 | 7.26 | 8.64 | 6.84 | 4.21 | 0.21 | 4.51 | 6.19 | 2.52 |
| train / bass A0-B2 (30) | 6.90 | 0.29 | 1.93 | 5.61 | 5.18 | 5.36 | 10.26 | 1.28 | 0.10 | 2.51 | 8.78 | 0.95 |
| train / middle C3-B5 (69) | 6.58 | 0.23 | 2.55 | 5.34 | 4.94 | 5.45 | 7.58 | 1.94 | 0.10 | 2.14 | 9.54 | 1.39 |
| train / treble C6-C8 (38) | 3.44 | 0.31 | 2.42 | 4.42 | 5.95 | 6.65 | 5.44 | 3.22 | 0.23 | 3.55 | 3.83 | 1.05 |
| dev / bass A0-B2 (5) | 8.81 | 1.25 | 2.08 | 5.79 | 7.48 | 8.96 | 7.09 | 5.19 | 0.20 | 2.09 | 1.42 | 1.41 |
| dev / middle C3-B5 (11) | 8.45 | 0.95 | 3.82 | 7.07 | 6.94 | 8.02 | 6.93 | 4.22 | 0.17 | 4.56 | 10.54 | 2.71 |
| dev / treble C6-C8 (5) | 7.17 | 3.30 | 6.27 | 5.85 | 7.73 | 9.70 | 6.46 | 3.24 | 0.29 | 6.83 | 1.38 | 3.21 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.26 is worse than 0.4.25 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.25 | 0.4.26 |
|---|---|---|---|---|
| 103 | train | sustain_db | 11.71 | 12.63 |
| 103 | train | icc | 0.31 | 0.34 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (15.9384 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 8.2323 | 8.2322 | -0.0002 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 1.8131 | 1.5783 | -0.2349 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 3.9889 | 3.9906 | 0.0018 | 0 | 0 | 0 |
| dev | attack_db | 21 | 6.4633 | 6.4730 | 0.0096 | 0 | 0 | 0 |
| dev | early_db | 21 | 7.2564 | 7.2562 | -0.0002 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 8.6418 | 8.6443 | 0.0025 | 0 | 0 | 0 |
| dev | noise_db | 20 | 6.8453 | 6.8440 | -0.0013 | 0 | 0 | 1 |
| dev | ild_db | 21 | 4.2246 | 4.2148 | -0.0098 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2076 | 0.2063 | -0.0013 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.5137 | 4.5130 | -0.0007 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 6.1915 | 6.1875 | -0.0040 | 0 | 0 | 0 |
| dev | level_db | 21 | 2.5181 | 2.5194 | 0.0013 | 0 | 0 | 0 |
| train | partial_db | 137 | 5.7572 | 5.7778 | 0.0206 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 0.2816 | 0.2669 | -0.0147 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 2.3784 | 2.3788 | 0.0004 | 0 | 0 | 2 |
| train | attack_db | 137 | 5.1500 | 5.1478 | -0.0023 | 0 | 0 | 0 |
| train | early_db | 137 | 5.2798 | 5.2730 | -0.0068 | 0 | 0 | 0 |
| train | sustain_db | 136 | 5.7287 | 5.7539 | 0.0252 | 0 | 0 | 1 |
| train | noise_db | 125 | 7.4192 | 7.4198 | 0.0006 | 0 | 0 | 12 |
| train | ild_db | 135 | 2.1318 | 2.1382 | 0.0064 | 0 | 0 | 2 |
| train | icc | 135 | 0.1377 | 0.1352 | -0.0025 | 0 | 0 | 2 |
| train | envelope_db | 137 | 2.6223 | 2.6124 | -0.0099 | 0 | 0 | 0 |
| train | rise_ms | 137 | 7.8000 | 7.7885 | -0.0116 | 0 | 0 | 0 |
| train | level_db | 137 | 1.1923 | 1.1972 | 0.0049 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 103 | train | sustain_db | 4 | 11.7142 | 12.6276 | 0.9135 |
| 103 | train | icc | 3 | 0.3127 | 0.3409 | 0.0282 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
