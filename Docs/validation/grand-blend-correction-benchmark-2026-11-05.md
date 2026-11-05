# Recording benchmark: candidate 0.4.23 against shipping 0.4.22

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## shipping 0.4.22

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.54 | 0.18 | 1.85 | 4.43 | 4.25 | 4.66 | 5.86 | 0.91 | 0.06 | 1.96 | 3.13 | 0.52 |
| dev (156) | 5.33 | 1.12 | 2.24 | 4.79 | 4.53 | 5.43 | 5.41 | 2.49 | 0.11 | 2.75 | 4.65 | 0.96 |
| train / bass A0-B2 (84) | 4.70 | 0.04 | 0.44 | 4.80 | 3.96 | 3.75 | 5.93 | 0.40 | 0.03 | 2.12 | 3.89 | 0.39 |
| train / middle C3-B5 (108) | 4.90 | 0.07 | 1.44 | 3.99 | 4.07 | 3.48 | 6.15 | 0.70 | 0.05 | 0.82 | 2.91 | 0.36 |
| train / treble C6-C8 (84) | 3.93 | 0.45 | 3.91 | 4.62 | 4.76 | 7.07 | 5.44 | 1.73 | 0.12 | 3.26 | 2.65 | 0.87 |
| dev / bass A0-B2 (44) | 5.36 | 1.23 | 1.08 | 5.17 | 4.08 | 3.90 | 5.13 | 1.34 | 0.06 | 2.97 | 5.63 | 0.98 |
| dev / middle C3-B5 (68) | 6.48 | 0.64 | 2.39 | 4.65 | 4.92 | 5.94 | 5.80 | 3.65 | 0.10 | 2.14 | 5.46 | 0.86 |
| dev / treble C6-C8 (44) | 3.53 | 1.76 | 3.21 | 4.62 | 4.38 | 6.17 | 5.09 | 1.81 | 0.18 | 3.48 | 2.41 | 1.09 |

## candidate 0.4.23

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

## Independent-sample regressions (legacy)

Every note and role where candidate 0.4.23 is worse than shipping 0.4.22 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (25.8221 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 5.3291 | 5.2435 | -0.0856 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 1.1234 | 1.1422 | 0.0188 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 2.2448 | 2.1733 | -0.0715 | 0 | 0 | 1 |
| dev | attack_db | 156 | 4.7902 | 4.7984 | 0.0082 | 0 | 0 | 0 |
| dev | early_db | 156 | 4.5294 | 4.5300 | 0.0006 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 5.4299 | 5.2414 | -0.1884 | 0 | 0 | 0 |
| dev | noise_db | 153 | 5.4051 | 5.4026 | -0.0025 | 0 | 0 | 3 |
| dev | ild_db | 154 | 2.4865 | 2.4796 | -0.0069 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1106 | 0.1128 | 0.0022 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 2.7516 | 2.6129 | -0.1387 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 4.6473 | 4.6056 | -0.0417 | 0 | 0 | 0 |
| dev | level_db | 156 | 0.9593 | 0.9623 | 0.0030 | 0 | 0 | 0 |
| train | partial_db | 276 | 4.5432 | 4.5432 | 0.0000 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 0.1768 | 0.1768 | 0.0000 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 1.8490 | 1.8490 | 0.0000 | 0 | 0 | 5 |
| train | attack_db | 276 | 4.4318 | 4.4318 | 0.0000 | 0 | 0 | 0 |
| train | early_db | 276 | 4.2492 | 4.2492 | 0.0000 | 0 | 0 | 0 |
| train | sustain_db | 276 | 4.6577 | 4.6577 | 0.0000 | 0 | 0 | 0 |
| train | noise_db | 262 | 5.8606 | 5.8606 | 0.0000 | 0 | 0 | 14 |
| train | ild_db | 270 | 0.9052 | 0.9052 | 0.0000 | 0 | 0 | 6 |
| train | icc | 270 | 0.0644 | 0.0644 | 0.0000 | 0 | 0 | 6 |
| train | envelope_db | 276 | 1.9581 | 1.9581 | 0.0000 | 0 | 0 | 0 |
| train | rise_ms | 276 | 3.1270 | 3.1270 | 0.0000 | 0 | 0 | 0 |
| train | level_db | 276 | 0.5214 | 0.5214 | 0.0000 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
