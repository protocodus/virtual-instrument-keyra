# Recording benchmark: candidate 0.4.18 against shipping 0.4.17

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## shipping 0.4.17

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.55 | 0.18 | 1.85 | 4.43 | 4.24 | 4.65 | 5.86 | 0.90 | 0.06 | 1.96 | 3.13 | 0.52 |
| dev (156) | 5.33 | 1.12 | 2.24 | 4.79 | 4.53 | 5.42 | 5.41 | 2.49 | 0.11 | 2.75 | 4.64 | 0.96 |
| train / bass A0-B2 (84) | 4.70 | 0.04 | 0.43 | 4.80 | 3.96 | 3.75 | 5.93 | 0.40 | 0.03 | 2.12 | 3.89 | 0.39 |
| train / middle C3-B5 (108) | 4.90 | 0.07 | 1.44 | 4.00 | 4.07 | 3.48 | 6.15 | 0.69 | 0.05 | 0.82 | 2.91 | 0.36 |
| train / treble C6-C8 (84) | 3.94 | 0.45 | 3.91 | 4.62 | 4.75 | 7.05 | 5.44 | 1.74 | 0.12 | 3.26 | 2.65 | 0.87 |
| dev / bass A0-B2 (44) | 5.36 | 1.23 | 1.08 | 5.17 | 4.08 | 3.90 | 5.13 | 1.35 | 0.06 | 2.97 | 5.64 | 0.99 |
| dev / middle C3-B5 (68) | 6.48 | 0.64 | 2.39 | 4.65 | 4.92 | 5.94 | 5.80 | 3.64 | 0.10 | 2.14 | 5.46 | 0.86 |
| dev / treble C6-C8 (44) | 3.54 | 1.76 | 3.21 | 4.62 | 4.38 | 6.14 | 5.09 | 1.81 | 0.18 | 3.48 | 2.37 | 1.08 |

## candidate 0.4.18

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.54 | 0.18 | 1.85 | 4.43 | 4.24 | 4.65 | 5.86 | 0.91 | 0.06 | 1.96 | 3.13 | 0.52 |
| dev (156) | 5.33 | 1.12 | 2.24 | 4.79 | 4.53 | 5.42 | 5.40 | 2.49 | 0.11 | 2.75 | 4.65 | 0.96 |
| train / bass A0-B2 (84) | 4.70 | 0.04 | 0.44 | 4.80 | 3.96 | 3.75 | 5.93 | 0.40 | 0.03 | 2.12 | 3.89 | 0.39 |
| train / middle C3-B5 (108) | 4.90 | 0.07 | 1.44 | 3.99 | 4.07 | 3.48 | 6.15 | 0.70 | 0.05 | 0.82 | 2.91 | 0.36 |
| train / treble C6-C8 (84) | 3.93 | 0.45 | 3.91 | 4.62 | 4.75 | 7.05 | 5.43 | 1.73 | 0.12 | 3.26 | 2.65 | 0.87 |
| dev / bass A0-B2 (44) | 5.36 | 1.23 | 1.08 | 5.17 | 4.08 | 3.90 | 5.13 | 1.35 | 0.06 | 2.97 | 5.63 | 0.98 |
| dev / middle C3-B5 (68) | 6.48 | 0.64 | 2.39 | 4.65 | 4.92 | 5.94 | 5.80 | 3.65 | 0.10 | 2.14 | 5.46 | 0.86 |
| dev / treble C6-C8 (44) | 3.53 | 1.76 | 3.21 | 4.62 | 4.38 | 6.14 | 5.08 | 1.80 | 0.18 | 3.48 | 2.41 | 1.08 |

## Independent-sample regressions (legacy)

Every note and role where candidate 0.4.18 is worse than shipping 0.4.17 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (25.8192 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 5.3316 | 5.3293 | -0.0023 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 1.1228 | 1.1234 | 0.0006 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 2.2445 | 2.2443 | -0.0002 | 0 | 0 | 1 |
| dev | attack_db | 156 | 4.7888 | 4.7900 | 0.0011 | 0 | 0 | 0 |
| dev | early_db | 156 | 4.5283 | 4.5286 | 0.0003 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 5.4206 | 5.4203 | -0.0002 | 0 | 0 | 0 |
| dev | noise_db | 153 | 5.4068 | 5.4042 | -0.0026 | 0 | 0 | 3 |
| dev | ild_db | 154 | 2.4857 | 2.4864 | 0.0007 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1108 | 0.1106 | -0.0002 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 2.7533 | 2.7532 | -0.0001 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 4.6373 | 4.6470 | 0.0097 | 0 | 0 | 0 |
| dev | level_db | 156 | 0.9596 | 0.9599 | 0.0003 | 0 | 0 | 0 |
| train | partial_db | 276 | 4.5463 | 4.5432 | -0.0031 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 0.1767 | 0.1768 | 0.0000 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 1.8491 | 1.8489 | -0.0002 | 0 | 0 | 5 |
| train | attack_db | 276 | 4.4314 | 4.4315 | 0.0000 | 0 | 0 | 0 |
| train | early_db | 276 | 4.2434 | 4.2436 | 0.0003 | 0 | 0 | 0 |
| train | sustain_db | 276 | 4.6509 | 4.6510 | 0.0001 | 0 | 0 | 0 |
| train | noise_db | 262 | 5.8608 | 5.8585 | -0.0023 | 0 | 0 | 14 |
| train | ild_db | 270 | 0.9040 | 0.9051 | 0.0011 | 0 | 0 | 6 |
| train | icc | 270 | 0.0647 | 0.0644 | -0.0003 | 0 | 0 | 6 |
| train | envelope_db | 276 | 1.9578 | 1.9582 | 0.0004 | 0 | 0 | 0 |
| train | rise_ms | 276 | 3.1273 | 3.1268 | -0.0005 | 0 | 0 | 0 |
| train | level_db | 276 | 0.5216 | 0.5210 | -0.0006 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
