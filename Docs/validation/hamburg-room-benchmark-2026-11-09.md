# Recording benchmark: 0.4.27 against 0.4.26

Every train and dev note of `Tools/corpus/split-hamburg-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.26

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (40) | 4.69 | 0.26 | 3.41 | 6.18 | 5.12 | 5.66 | 7.24 | 1.53 | 0.12 | 3.32 | 17.41 | 0.61 |
| dev (8) | 7.13 | 2.64 | 3.73 | 7.27 | 6.51 | 6.39 | 5.73 | 4.82 | 0.19 | 2.29 | 3.05 | 3.13 |
| train / bass A0-B2 (16) | 4.69 | 0.09 | 0.97 | 6.54 | 3.86 | 3.73 | 8.19 | 0.89 | 0.06 | 2.39 | 32.18 | 0.57 |
| train / middle C3-B5 (12) | 4.63 | 0.23 | 2.25 | 6.17 | 5.43 | 5.62 | 7.19 | 1.93 | 0.12 | 1.94 | 12.41 | 0.22 |
| train / treble C6-C8 (12) | 4.75 | 0.51 | 7.82 | 5.71 | 6.51 | 8.28 | 6.25 | 1.97 | 0.19 | 5.92 | 2.73 | 1.06 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.13 | 2.64 | 3.73 | 7.27 | 6.51 | 6.39 | 5.73 | 4.82 | 0.19 | 2.29 | 3.05 | 3.13 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## 0.4.27

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (40) | 4.44 | 0.27 | 2.29 | 6.09 | 4.42 | 4.94 | 6.60 | 1.51 | 0.11 | 3.13 | 17.10 | 0.57 |
| dev (8) | 7.11 | 2.53 | 3.68 | 7.19 | 6.19 | 6.09 | 6.00 | 4.76 | 0.23 | 2.31 | 3.01 | 3.12 |
| train / bass A0-B2 (16) | 4.66 | 0.10 | 0.99 | 6.52 | 3.74 | 3.73 | 7.95 | 0.84 | 0.07 | 2.40 | 31.40 | 0.56 |
| train / middle C3-B5 (12) | 4.63 | 0.24 | 2.10 | 6.09 | 4.44 | 4.77 | 6.13 | 1.93 | 0.14 | 1.84 | 12.40 | 0.22 |
| train / treble C6-C8 (12) | 3.97 | 0.52 | 4.22 | 5.51 | 5.30 | 6.73 | 5.62 | 1.98 | 0.15 | 5.41 | 2.73 | 0.92 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.11 | 2.53 | 3.68 | 7.19 | 6.19 | 6.09 | 6.00 | 4.76 | 0.23 | 2.31 | 3.01 | 3.12 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## Independent-sample regressions (legacy)

Every note and role where 0.4.27 is worse than 0.4.26 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.26 | 0.4.27 |
|---|---|---|---|---|
| 52 | dev | noise_db | 2.88 | 5.57 |
| 52 | dev | icc | 0.21 | 0.25 |
| 66 | train | icc | 0.10 | 0.14 |
| 59 | train | icc | 0.09 | 0.12 |
| 73 | dev | icc | 0.18 | 0.21 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (15.0669 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 8 | 7.1295 | 7.1149 | -0.0146 | 0 | 0 | 0 |
| dev | tuning_cents | 8 | 2.6419 | 2.5327 | -0.1092 | 0 | 0 | 0 |
| dev | decay_db_s | 8 | 3.7271 | 3.6773 | -0.0498 | 0 | 0 | 0 |
| dev | attack_db | 8 | 7.2663 | 7.1868 | -0.0795 | 0 | 0 | 0 |
| dev | early_db | 8 | 6.5068 | 6.1899 | -0.3169 | 0 | 0 | 0 |
| dev | sustain_db | 8 | 6.3853 | 6.0904 | -0.2949 | 0 | 0 | 0 |
| dev | noise_db | 5 | 5.7268 | 5.6755 | -0.0513 | 0 | 1 | 2 |
| dev | ild_db | 8 | 4.8235 | 4.7561 | -0.0674 | 0 | 0 | 0 |
| dev | icc | 8 | 0.1943 | 0.2270 | 0.0327 | 0 | 0 | 0 |
| dev | envelope_db | 8 | 2.2880 | 2.3067 | 0.0187 | 0 | 0 | 0 |
| dev | rise_ms | 8 | 3.0521 | 3.0078 | -0.0443 | 0 | 0 | 0 |
| dev | level_db | 8 | 3.1326 | 3.1090 | -0.0236 | 0 | 0 | 0 |
| train | partial_db | 40 | 4.6888 | 4.4433 | -0.2454 | 0 | 0 | 0 |
| train | tuning_cents | 40 | 0.2597 | 0.2658 | 0.0061 | 0 | 0 | 0 |
| train | decay_db_s | 40 | 3.4089 | 2.2946 | -1.1142 | 0 | 0 | 0 |
| train | attack_db | 40 | 6.1796 | 6.0867 | -0.0929 | 0 | 0 | 0 |
| train | early_db | 40 | 5.1231 | 4.4187 | -0.7044 | 0 | 0 | 0 |
| train | sustain_db | 40 | 5.6609 | 4.9388 | -0.7221 | 0 | 0 | 0 |
| train | noise_db | 37 | 7.2363 | 6.6044 | -0.6319 | 0 | 0 | 3 |
| train | ild_db | 40 | 1.5258 | 1.5104 | -0.0154 | 0 | 0 | 0 |
| train | icc | 40 | 0.1157 | 0.1131 | -0.0026 | 0 | 0 | 0 |
| train | envelope_db | 40 | 3.3159 | 3.1328 | -0.1831 | 0 | 0 | 0 |
| train | rise_ms | 40 | 17.4130 | 17.1005 | -0.3125 | 0 | 0 | 0 |
| train | level_db | 40 | 0.6126 | 0.5726 | -0.0400 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 52 | dev | icc | 4 | 0.2061 | 0.2462 | 0.0401 |
| 66 | train | icc | 4 | 0.0996 | 0.1358 | 0.0362 |
| 59 | train | icc | 4 | 0.0931 | 0.1237 | 0.0306 |
| 52 | dev | noise_db | 1 | 2.8793 | 3.5178 | 0.6385 |
| 73 | dev | icc | 4 | 0.1824 | 0.2077 | 0.0253 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| n52v2r1 | 52 | dev | noise_db | gained | - | 7.6308 |
