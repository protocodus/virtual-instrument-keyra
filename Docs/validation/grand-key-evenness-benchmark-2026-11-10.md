# Recording benchmark: 0.4.38 against 0.4.37

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.37

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.51 | 0.17 | 1.85 | 4.30 | 4.02 | 4.61 | 5.62 | 1.48 | 0.06 | 1.94 | 3.60 | 1.10 |
| dev (156) | 5.28 | 0.91 | 2.09 | 4.66 | 4.42 | 5.32 | 5.26 | 2.61 | 0.10 | 2.62 | 4.51 | 1.11 |
| train / bass A0-B2 (84) | 4.72 | 0.04 | 0.43 | 4.56 | 3.86 | 3.70 | 5.83 | 0.74 | 0.03 | 1.80 | 3.98 | 0.99 |
| train / middle C3-B5 (108) | 4.73 | 0.08 | 1.47 | 3.90 | 3.88 | 3.48 | 5.86 | 2.11 | 0.05 | 0.97 | 4.13 | 1.06 |
| train / treble C6-C8 (84) | 4.03 | 0.41 | 3.89 | 4.55 | 4.36 | 6.98 | 5.14 | 1.42 | 0.09 | 3.32 | 2.54 | 1.25 |
| dev / bass A0-B2 (44) | 5.48 | 1.26 | 1.09 | 4.82 | 4.02 | 3.87 | 5.11 | 1.51 | 0.05 | 2.65 | 4.65 | 1.03 |
| dev / middle C3-B5 (68) | 6.20 | 0.65 | 2.49 | 4.51 | 4.67 | 5.60 | 5.42 | 4.28 | 0.11 | 1.95 | 6.03 | 1.13 |
| dev / treble C6-C8 (44) | 3.66 | 0.95 | 2.49 | 4.72 | 4.43 | 6.32 | 5.16 | 1.04 | 0.15 | 3.63 | 2.01 | 1.15 |

## 0.4.38

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.50 | 0.17 | 1.85 | 4.29 | 4.01 | 4.60 | 5.65 | 1.54 | 0.06 | 1.94 | 3.67 | 1.05 |
| dev (156) | 5.28 | 0.91 | 2.09 | 4.65 | 4.41 | 5.31 | 5.27 | 2.64 | 0.10 | 2.63 | 4.50 | 1.11 |
| train / bass A0-B2 (84) | 4.74 | 0.04 | 0.44 | 4.56 | 3.87 | 3.70 | 5.91 | 0.76 | 0.03 | 1.80 | 4.11 | 0.89 |
| train / middle C3-B5 (108) | 4.68 | 0.08 | 1.47 | 3.87 | 3.84 | 3.46 | 5.88 | 2.28 | 0.05 | 0.97 | 4.21 | 1.03 |
| train / treble C6-C8 (84) | 4.03 | 0.41 | 3.88 | 4.55 | 4.36 | 6.98 | 5.14 | 1.38 | 0.10 | 3.32 | 2.52 | 1.25 |
| dev / bass A0-B2 (44) | 5.49 | 1.26 | 1.09 | 4.82 | 4.02 | 3.88 | 5.13 | 1.53 | 0.05 | 2.65 | 4.67 | 1.02 |
| dev / middle C3-B5 (68) | 6.19 | 0.65 | 2.49 | 4.50 | 4.66 | 5.59 | 5.43 | 4.37 | 0.11 | 1.96 | 6.01 | 1.15 |
| dev / treble C6-C8 (44) | 3.66 | 0.95 | 2.49 | 4.72 | 4.43 | 6.32 | 5.16 | 1.02 | 0.15 | 3.63 | 2.01 | 1.15 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.38 is worse than 0.4.37 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.37 | 0.4.38 |
|---|---|---|---|---|
| 60 | train | ild_db | 1.76 | 2.63 |
| 21 | dev | ild_db | 0.35 | 1.12 |
| 60 | dev | ild_db | 1.47 | 2.21 |
| 21 | train | ild_db | 0.33 | 1.03 |
| 21 | dev | level_db | 0.20 | 0.81 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (25.6625 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 5.2840 | 5.2793 | -0.0047 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 0.9053 | 0.9073 | 0.0020 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 2.0891 | 2.0898 | 0.0007 | 0 | 0 | 1 |
| dev | attack_db | 156 | 4.6574 | 4.6518 | -0.0055 | 0 | 0 | 0 |
| dev | early_db | 156 | 4.4185 | 4.4112 | -0.0073 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 5.3161 | 5.3141 | -0.0020 | 0 | 0 | 0 |
| dev | noise_db | 153 | 5.2609 | 5.2698 | 0.0089 | 0 | 0 | 3 |
| dev | ild_db | 154 | 2.6084 | 2.6444 | 0.0360 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1022 | 0.1024 | 0.0002 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 2.6225 | 2.6256 | 0.0031 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 4.5051 | 4.5040 | -0.0011 | 0 | 0 | 0 |
| dev | level_db | 156 | 1.1072 | 1.1158 | 0.0086 | 0 | 0 | 0 |
| train | partial_db | 276 | 4.5122 | 4.5021 | -0.0101 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 0.1685 | 0.1689 | 0.0004 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 1.8534 | 1.8530 | -0.0004 | 0 | 0 | 5 |
| train | attack_db | 276 | 4.3003 | 4.2885 | -0.0118 | 0 | 0 | 0 |
| train | early_db | 276 | 4.0204 | 4.0107 | -0.0097 | 0 | 0 | 0 |
| train | sustain_db | 276 | 4.6108 | 4.6038 | -0.0070 | 0 | 0 | 0 |
| train | noise_db | 262 | 5.6220 | 5.6292 | 0.0072 | 0 | 1 | 13 |
| train | ild_db | 270 | 1.4849 | 1.5448 | 0.0599 | 0 | 0 | 6 |
| train | icc | 270 | 0.0562 | 0.0564 | 0.0002 | 0 | 0 | 6 |
| train | envelope_db | 276 | 1.9382 | 1.9386 | 0.0005 | 0 | 0 | 0 |
| train | rise_ms | 276 | 3.5984 | 3.6678 | 0.0694 | 0 | 0 | 0 |
| train | level_db | 276 | 1.0951 | 1.0530 | -0.0420 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 60 | train | ild_db | 12 | 1.7643 | 2.6269 | 0.8625 |
| 21 | dev | ild_db | 4 | 0.3489 | 1.1157 | 0.7668 |
| 60 | dev | ild_db | 4 | 1.4702 | 2.2129 | 0.7427 |
| 21 | train | ild_db | 12 | 0.3282 | 1.0294 | 0.7011 |
| 21 | dev | level_db | 4 | 0.2011 | 0.8216 | 0.6205 |
| 21 | train | level_db | 12 | 0.2485 | 0.7525 | 0.5040 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| A1v1 | 33 | train | noise_db | gained | - | 11.4844 |
