# Recording benchmark: 0.4.24 against 0.4.23

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.23

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.54 | 0.18 | 1.85 | 4.43 | 4.25 | 4.66 | 5.86 | 0.91 | 0.06 | 1.96 | 3.13 | 0.52 |
| dev (156) | 5.24 | 1.14 | 2.17 | 4.80 | 4.53 | 5.24 | 5.40 | 2.48 | 0.11 | 2.61 | 4.61 | 0.96 |
| train / bass A0-B2 (84) | 4.70 | 0.04 | 0.44 | 4.80 | 3.96 | 3.75 | 5.93 | 0.40 | 0.03 | 2.12 | 3.89 | 0.39 |
| train / middle C3-B5 (108) | 4.90 | 0.07 | 1.44 | 3.99 | 4.07 | 3.48 | 6.15 | 0.70 | 0.05 | 0.82 | 2.91 | 0.36 |
| train / treble C6-C8 (84) | 3.93 | 0.45 | 3.91 | 4.62 | 4.76 | 7.07 | 5.44 | 1.73 | 0.12 | 3.26 | 2.65 | 0.87 |
| dev / bass A0-B2 (44) | 5.36 | 1.23 | 1.08 | 5.17 | 4.08 | 3.90 | 5.13 | 1.34 | 0.06 | 2.97 | 5.63 | 0.98 |
| dev / middle C3-B5 (68) | 6.30 | 0.65 | 2.47 | 4.68 | 4.92 | 5.60 | 5.79 | 3.63 | 0.10 | 1.87 | 5.45 | 0.87 |
| dev / treble C6-C8 (44) | 3.49 | 1.82 | 2.82 | 4.61 | 4.39 | 6.03 | 5.09 | 1.81 | 0.19 | 3.40 | 2.27 | 1.09 |

## 0.4.24

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.55 | 0.19 | 1.85 | 4.43 | 4.25 | 4.66 | 5.86 | 0.91 | 0.06 | 1.95 | 3.12 | 0.53 |
| dev (156) | 5.22 | 1.06 | 2.12 | 4.80 | 4.53 | 5.20 | 5.40 | 2.44 | 0.11 | 2.59 | 4.61 | 0.96 |
| train / bass A0-B2 (84) | 4.70 | 0.04 | 0.44 | 4.80 | 3.96 | 3.75 | 5.93 | 0.40 | 0.03 | 2.12 | 3.89 | 0.39 |
| train / middle C3-B5 (108) | 4.90 | 0.07 | 1.44 | 3.99 | 4.07 | 3.48 | 6.15 | 0.70 | 0.05 | 0.82 | 2.91 | 0.36 |
| train / treble C6-C8 (84) | 3.94 | 0.50 | 3.92 | 4.62 | 4.75 | 7.07 | 5.44 | 1.74 | 0.12 | 3.25 | 2.63 | 0.88 |
| dev / bass A0-B2 (44) | 5.36 | 1.23 | 1.08 | 5.17 | 4.08 | 3.90 | 5.13 | 1.34 | 0.06 | 2.97 | 5.63 | 0.98 |
| dev / middle C3-B5 (68) | 6.30 | 0.65 | 2.47 | 4.68 | 4.92 | 5.60 | 5.79 | 3.63 | 0.10 | 1.87 | 5.45 | 0.87 |
| dev / treble C6-C8 (44) | 3.41 | 1.53 | 2.62 | 4.61 | 4.38 | 5.88 | 5.08 | 1.69 | 0.18 | 3.31 | 2.27 | 1.09 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.24 is worse than 0.4.23 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.23 | 0.4.24 |
|---|---|---|---|---|
| 108 | train | tuning_cents | 1.01 | 1.51 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (25.8221 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 5.2435 | 5.2204 | -0.0231 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 1.1422 | 1.0595 | -0.0827 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 2.1733 | 2.1170 | -0.0563 | 0 | 0 | 1 |
| dev | attack_db | 156 | 4.7984 | 4.7959 | -0.0025 | 0 | 0 | 0 |
| dev | early_db | 156 | 4.5300 | 4.5275 | -0.0024 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 5.2414 | 5.2005 | -0.0409 | 0 | 0 | 0 |
| dev | noise_db | 153 | 5.4026 | 5.4002 | -0.0024 | 0 | 0 | 3 |
| dev | ild_db | 154 | 2.4796 | 2.4449 | -0.0347 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1128 | 0.1114 | -0.0014 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 2.6129 | 2.5894 | -0.0235 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 4.6056 | 4.6055 | -0.0001 | 0 | 0 | 0 |
| dev | level_db | 156 | 0.9623 | 0.9617 | -0.0007 | 0 | 0 | 0 |
| train | partial_db | 276 | 4.5432 | 4.5456 | 0.0024 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 0.1768 | 0.1916 | 0.0149 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 1.8490 | 1.8531 | 0.0040 | 0 | 0 | 5 |
| train | attack_db | 276 | 4.4318 | 4.4313 | -0.0005 | 0 | 0 | 0 |
| train | early_db | 276 | 4.2492 | 4.2455 | -0.0037 | 0 | 0 | 0 |
| train | sustain_db | 276 | 4.6577 | 4.6575 | -0.0001 | 0 | 0 | 0 |
| train | noise_db | 262 | 5.8606 | 5.8603 | -0.0003 | 0 | 0 | 14 |
| train | ild_db | 270 | 0.9052 | 0.9066 | 0.0014 | 0 | 0 | 6 |
| train | icc | 270 | 0.0644 | 0.0642 | -0.0002 | 0 | 0 | 6 |
| train | envelope_db | 276 | 1.9581 | 1.9546 | -0.0035 | 0 | 0 | 0 |
| train | rise_ms | 276 | 3.1270 | 3.1221 | -0.0048 | 0 | 0 | 0 |
| train | level_db | 276 | 0.5214 | 0.5252 | 0.0038 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 108 | train | tuning_cents | 12 | 1.0059 | 1.5086 | 0.5027 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
