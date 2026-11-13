# Recording benchmark: 2.13.0 against 2.12.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.12.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.07 | 2.13 | 3.92 | 6.70 | 6.49 | 8.72 | 7.21 | 4.79 | 0.20 | 4.33 | 14.23 | 2.50 |
| dev (156) | 7.57 | 2.22 | 3.31 | 6.34 | 6.01 | 7.89 | 6.84 | 4.96 | 0.18 | 4.03 | 11.94 | 2.65 |
| train / bass A0-B2 (84) | 8.93 | 2.68 | 2.46 | 6.07 | 5.55 | 6.65 | 6.57 | 4.24 | 0.21 | 3.58 | 24.14 | 2.34 |
| train / middle C3-B5 (108) | 7.48 | 1.36 | 3.87 | 6.30 | 6.33 | 7.77 | 7.17 | 6.78 | 0.19 | 4.24 | 12.23 | 2.03 |
| train / treble C6-C8 (84) | 7.98 | 2.57 | 5.56 | 7.83 | 7.63 | 12.00 | 7.90 | 2.61 | 0.19 | 5.21 | 6.91 | 3.26 |
| dev / bass A0-B2 (44) | 9.65 | 3.29 | 2.29 | 5.87 | 5.10 | 5.89 | 6.37 | 4.47 | 0.21 | 3.00 | 22.94 | 3.13 |
| dev / middle C3-B5 (68) | 7.05 | 1.21 | 3.44 | 6.09 | 6.01 | 7.44 | 6.88 | 6.85 | 0.15 | 4.13 | 9.35 | 1.94 |
| dev / treble C6-C8 (44) | 6.31 | 2.71 | 4.14 | 7.18 | 6.94 | 10.60 | 7.25 | 2.41 | 0.22 | 4.89 | 4.94 | 3.25 |

## 2.13.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.10 | 2.20 | 3.93 | 6.70 | 6.49 | 8.72 | 7.23 | 4.79 | 0.20 | 4.33 | 14.30 | 2.47 |
| dev (156) | 7.58 | 2.32 | 3.31 | 6.34 | 6.02 | 7.90 | 6.83 | 4.95 | 0.18 | 4.02 | 12.00 | 2.62 |
| train / bass A0-B2 (84) | 9.03 | 2.85 | 2.47 | 6.07 | 5.55 | 6.66 | 6.65 | 4.25 | 0.21 | 3.55 | 24.22 | 2.25 |
| train / middle C3-B5 (108) | 7.47 | 1.41 | 3.87 | 6.30 | 6.32 | 7.77 | 7.14 | 6.77 | 0.19 | 4.25 | 12.33 | 2.03 |
| train / treble C6-C8 (84) | 7.98 | 2.57 | 5.56 | 7.83 | 7.63 | 12.00 | 7.90 | 2.61 | 0.19 | 5.21 | 6.91 | 3.26 |
| dev / bass A0-B2 (44) | 9.69 | 3.52 | 2.29 | 5.88 | 5.12 | 5.91 | 6.34 | 4.47 | 0.21 | 3.00 | 22.95 | 3.04 |
| dev / middle C3-B5 (68) | 7.04 | 1.28 | 3.44 | 6.08 | 6.00 | 7.44 | 6.87 | 6.84 | 0.15 | 4.13 | 9.49 | 1.94 |
| dev / treble C6-C8 (44) | 6.31 | 2.71 | 4.14 | 7.18 | 6.94 | 10.60 | 7.25 | 2.41 | 0.22 | 4.89 | 4.94 | 3.25 |

## Independent-sample regressions (legacy)

Every note and role where 2.13.0 is worse than 2.12.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.12.0 | 2.13.0 |
|---|---|---|---|---|
| 54 | dev | rise_ms | 3.05 | 5.44 |
| 21 | train | tuning_cents | 4.87 | 5.63 |
| 21 | dev | tuning_cents | 4.91 | 5.61 |
| 33 | dev | partial_db | 10.39 | 10.90 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.1037 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 7.5743 | 7.5800 | 0.0057 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.2208 | 2.3183 | 0.0975 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 3.3104 | 3.3102 | -0.0002 | 0 | 0 | 1 |
| dev | attack_db | 156 | 6.3353 | 6.3368 | 0.0015 | 0 | 0 | 0 |
| dev | early_db | 156 | 6.0124 | 6.0155 | 0.0031 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 7.8925 | 7.8982 | 0.0057 | 0 | 0 | 0 |
| dev | noise_db | 153 | 6.8389 | 6.8294 | -0.0095 | 0 | 0 | 3 |
| dev | ild_db | 154 | 4.9586 | 4.9548 | -0.0038 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1833 | 0.1844 | 0.0012 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 4.0252 | 4.0239 | -0.0013 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 11.9374 | 12.0019 | 0.0645 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.6475 | 2.6187 | -0.0288 | 0 | 0 | 0 |
| train | partial_db | 276 | 8.0744 | 8.0999 | 0.0255 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.1282 | 2.2028 | 0.0747 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 3.9245 | 3.9267 | 0.0022 | 0 | 0 | 5 |
| train | attack_db | 276 | 6.6988 | 6.6962 | -0.0026 | 0 | 0 | 0 |
| train | early_db | 276 | 6.4896 | 6.4863 | -0.0033 | 0 | 0 | 0 |
| train | sustain_db | 276 | 8.7177 | 8.7205 | 0.0027 | 0 | 0 | 0 |
| train | noise_db | 272 | 7.2141 | 7.2276 | 0.0135 | 0 | 0 | 4 |
| train | ild_db | 270 | 4.7876 | 4.7852 | -0.0024 | 0 | 0 | 6 |
| train | icc | 270 | 0.1970 | 0.1973 | 0.0004 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.3335 | 4.3263 | -0.0072 | 0 | 0 | 0 |
| train | rise_ms | 276 | 14.2329 | 14.2951 | 0.0622 | 0 | 0 | 0 |
| train | level_db | 276 | 2.4999 | 2.4715 | -0.0284 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 54 | dev | rise_ms | 4 | 3.0521 | 5.4427 | 2.3906 |
| 21 | train | tuning_cents | 12 | 4.8740 | 5.6313 | 0.7573 |
| 21 | dev | tuning_cents | 4 | 4.9124 | 5.6133 | 0.7009 |
| 33 | dev | partial_db | 4 | 10.3868 | 10.8953 | 0.5084 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
