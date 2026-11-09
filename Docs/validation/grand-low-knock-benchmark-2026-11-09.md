# Recording benchmark: 0.4.28 against 0.4.27

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.27

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.62 | 0.16 | 1.85 | 4.42 | 4.05 | 4.66 | 5.63 | 0.79 | 0.06 | 1.99 | 3.16 | 0.52 |
| dev (156) | 5.34 | 0.91 | 2.10 | 4.82 | 4.44 | 5.33 | 5.27 | 2.24 | 0.10 | 2.68 | 4.36 | 0.96 |
| train / bass A0-B2 (84) | 4.70 | 0.04 | 0.44 | 4.81 | 3.93 | 3.75 | 5.89 | 0.40 | 0.03 | 2.12 | 4.06 | 0.39 |
| train / middle C3-B5 (108) | 4.90 | 0.07 | 1.44 | 3.96 | 3.90 | 3.48 | 5.84 | 0.70 | 0.05 | 0.82 | 2.95 | 0.36 |
| train / treble C6-C8 (84) | 4.18 | 0.40 | 3.91 | 4.61 | 4.36 | 7.09 | 5.15 | 1.34 | 0.10 | 3.36 | 2.55 | 0.85 |
| dev / bass A0-B2 (44) | 5.43 | 1.27 | 1.08 | 5.18 | 4.05 | 3.90 | 5.11 | 1.34 | 0.05 | 2.97 | 5.03 | 0.98 |
| dev / middle C3-B5 (68) | 6.30 | 0.64 | 2.47 | 4.65 | 4.72 | 5.60 | 5.50 | 3.62 | 0.10 | 1.87 | 5.44 | 0.87 |
| dev / treble C6-C8 (44) | 3.75 | 0.95 | 2.55 | 4.71 | 4.38 | 6.34 | 5.08 | 0.96 | 0.15 | 3.63 | 2.04 | 1.09 |

## 0.4.28

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.63 | 0.16 | 1.85 | 4.38 | 4.05 | 4.66 | 5.62 | 0.79 | 0.06 | 1.99 | 3.12 | 0.50 |
| dev (156) | 5.34 | 0.91 | 2.10 | 4.78 | 4.44 | 5.33 | 5.27 | 2.24 | 0.10 | 2.68 | 4.28 | 0.96 |
| train / bass A0-B2 (84) | 4.70 | 0.04 | 0.44 | 4.81 | 3.93 | 3.75 | 5.89 | 0.40 | 0.03 | 2.12 | 4.06 | 0.39 |
| train / middle C3-B5 (108) | 4.90 | 0.07 | 1.44 | 3.94 | 3.90 | 3.48 | 5.85 | 0.70 | 0.05 | 0.83 | 2.87 | 0.35 |
| train / treble C6-C8 (84) | 4.20 | 0.41 | 3.92 | 4.52 | 4.35 | 7.10 | 5.11 | 1.35 | 0.10 | 3.35 | 2.51 | 0.79 |
| dev / bass A0-B2 (44) | 5.43 | 1.27 | 1.08 | 5.18 | 4.05 | 3.90 | 5.11 | 1.34 | 0.05 | 2.97 | 5.03 | 0.99 |
| dev / middle C3-B5 (68) | 6.30 | 0.64 | 2.47 | 4.57 | 4.71 | 5.60 | 5.47 | 3.62 | 0.10 | 1.87 | 5.25 | 0.87 |
| dev / treble C6-C8 (44) | 3.76 | 0.95 | 2.55 | 4.71 | 4.42 | 6.36 | 5.13 | 0.94 | 0.15 | 3.64 | 2.03 | 1.07 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.28 is worse than 0.4.27 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (25.8246 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 5.3377 | 5.3408 | 0.0030 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 0.9078 | 0.9078 | 0.0000 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 2.0963 | 2.0971 | 0.0008 | 0 | 0 | 1 |
| dev | attack_db | 156 | 4.8184 | 4.7809 | -0.0375 | 0 | 0 | 0 |
| dev | early_db | 156 | 4.4357 | 4.4439 | 0.0082 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 5.3283 | 5.3338 | 0.0055 | 0 | 0 | 0 |
| dev | noise_db | 153 | 5.2707 | 5.2710 | 0.0003 | 0 | 0 | 3 |
| dev | ild_db | 154 | 2.2446 | 2.2422 | -0.0024 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1022 | 0.1020 | -0.0002 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 2.6806 | 2.6812 | 0.0006 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 4.3632 | 4.2810 | -0.0823 | 0 | 0 | 0 |
| dev | level_db | 156 | 0.9647 | 0.9568 | -0.0079 | 0 | 0 | 0 |
| train | partial_db | 276 | 4.6195 | 4.6252 | 0.0056 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 0.1625 | 0.1640 | 0.0015 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 1.8492 | 1.8514 | 0.0022 | 0 | 0 | 5 |
| train | attack_db | 276 | 4.4175 | 4.3796 | -0.0379 | 0 | 0 | 0 |
| train | early_db | 276 | 4.0504 | 4.0492 | -0.0012 | 0 | 0 | 0 |
| train | sustain_db | 276 | 4.6597 | 4.6620 | 0.0023 | 0 | 0 | 0 |
| train | noise_db | 262 | 5.6318 | 5.6247 | -0.0071 | 0 | 0 | 14 |
| train | ild_db | 270 | 0.7889 | 0.7940 | 0.0051 | 0 | 0 | 6 |
| train | icc | 270 | 0.0559 | 0.0558 | -0.0001 | 0 | 0 | 6 |
| train | envelope_db | 276 | 1.9899 | 1.9883 | -0.0017 | 0 | 0 | 0 |
| train | rise_ms | 276 | 3.1646 | 3.1218 | -0.0428 | 0 | 0 | 0 |
| train | level_db | 276 | 0.5175 | 0.4992 | -0.0183 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
