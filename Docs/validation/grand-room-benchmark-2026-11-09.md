# Recording benchmark: 0.4.27 against 0.4.26

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.26

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.64 | 0.16 | 1.85 | 4.44 | 4.27 | 4.70 | 5.86 | 0.80 | 0.06 | 1.99 | 3.10 | 0.53 |
| dev (156) | 5.32 | 0.98 | 2.10 | 4.80 | 4.54 | 5.35 | 5.40 | 2.25 | 0.10 | 2.68 | 4.54 | 0.97 |
| train / bass A0-B2 (84) | 4.70 | 0.04 | 0.44 | 4.80 | 3.96 | 3.75 | 5.93 | 0.40 | 0.03 | 2.12 | 3.89 | 0.39 |
| train / middle C3-B5 (108) | 4.90 | 0.07 | 1.44 | 3.99 | 4.07 | 3.48 | 6.15 | 0.70 | 0.05 | 0.82 | 2.91 | 0.36 |
| train / treble C6-C8 (84) | 4.23 | 0.38 | 3.91 | 4.64 | 4.82 | 7.20 | 5.42 | 1.37 | 0.10 | 3.35 | 2.57 | 0.90 |
| dev / bass A0-B2 (44) | 5.36 | 1.23 | 1.08 | 5.17 | 4.08 | 3.90 | 5.13 | 1.34 | 0.06 | 2.97 | 5.63 | 0.98 |
| dev / middle C3-B5 (68) | 6.30 | 0.65 | 2.47 | 4.68 | 4.92 | 5.60 | 5.79 | 3.63 | 0.10 | 1.87 | 5.45 | 0.87 |
| dev / treble C6-C8 (44) | 3.76 | 1.24 | 2.55 | 4.63 | 4.43 | 6.41 | 5.07 | 0.97 | 0.15 | 3.65 | 2.06 | 1.12 |

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

## Independent-sample regressions (legacy)

Every note and role where 0.4.27 is worse than 0.4.26 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.26 | 0.4.27 |
|---|---|---|---|---|
| 99 | dev | early_db | 3.87 | 4.49 |
| 36 | train | rise_ms | 7.26 | 8.49 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (25.8258 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 5.3198 | 5.3377 | 0.0179 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 0.9789 | 0.9078 | -0.0712 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 2.0967 | 2.0963 | -0.0004 | 0 | 0 | 1 |
| dev | attack_db | 156 | 4.8019 | 4.8184 | 0.0165 | 0 | 0 | 0 |
| dev | early_db | 156 | 4.5417 | 4.4357 | -0.1060 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 5.3485 | 5.3283 | -0.0202 | 0 | 0 | 0 |
| dev | noise_db | 153 | 5.3986 | 5.2707 | -0.1279 | 0 | 0 | 3 |
| dev | ild_db | 154 | 2.2507 | 2.2446 | -0.0061 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1042 | 0.1022 | -0.0020 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 2.6846 | 2.6806 | -0.0041 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 4.5442 | 4.3632 | -0.1810 | 0 | 0 | 0 |
| dev | level_db | 156 | 0.9695 | 0.9644 | -0.0051 | 0 | 0 | 0 |
| train | partial_db | 276 | 4.6357 | 4.6195 | -0.0161 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 0.1552 | 0.1625 | 0.0073 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 1.8495 | 1.8492 | -0.0003 | 0 | 0 | 5 |
| train | attack_db | 276 | 4.4364 | 4.4175 | -0.0189 | 0 | 0 | 0 |
| train | early_db | 276 | 4.2652 | 4.0504 | -0.2148 | 0 | 0 | 0 |
| train | sustain_db | 276 | 4.6971 | 4.6597 | -0.0374 | 0 | 0 | 0 |
| train | noise_db | 262 | 5.8553 | 5.6318 | -0.2235 | 0 | 0 | 14 |
| train | ild_db | 270 | 0.8008 | 0.7889 | -0.0120 | 0 | 0 | 6 |
| train | icc | 270 | 0.0575 | 0.0559 | -0.0017 | 0 | 0 | 6 |
| train | envelope_db | 276 | 1.9864 | 1.9899 | 0.0035 | 0 | 0 | 0 |
| train | rise_ms | 276 | 3.1032 | 3.1646 | 0.0614 | 0 | 0 | 0 |
| train | level_db | 276 | 0.5309 | 0.5176 | -0.0133 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 99 | dev | early_db | 16 | 3.8699 | 4.4898 | 0.6199 |
| 36 | train | rise_ms | 12 | 7.2587 | 8.4913 | 1.2326 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
