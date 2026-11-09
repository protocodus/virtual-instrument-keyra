# Recording benchmark: 0.4.26 against 0.4.25

Every train and dev note of `Tools/corpus/split-hamburg-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.25

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (40) | 4.67 | 0.26 | 3.43 | 6.13 | 5.06 | 5.60 | 7.14 | 1.53 | 0.12 | 3.29 | 17.42 | 0.69 |
| dev (8) | 7.88 | 1.02 | 4.45 | 6.94 | 6.68 | 6.17 | 6.52 | 4.86 | 0.20 | 2.54 | 3.74 | 2.15 |
| train / bass A0-B2 (16) | 4.69 | 0.09 | 0.97 | 6.53 | 3.86 | 3.73 | 8.10 | 0.89 | 0.06 | 2.39 | 32.19 | 0.60 |
| train / middle C3-B5 (12) | 4.63 | 0.23 | 2.24 | 6.19 | 5.43 | 5.62 | 7.19 | 1.93 | 0.12 | 1.94 | 12.41 | 0.27 |
| train / treble C6-C8 (12) | 4.69 | 0.51 | 7.88 | 5.55 | 6.28 | 8.08 | 6.05 | 1.97 | 0.19 | 5.83 | 2.74 | 1.24 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.88 | 1.02 | 4.45 | 6.94 | 6.68 | 6.17 | 6.52 | 4.86 | 0.20 | 2.54 | 3.74 | 2.15 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

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

## Independent-sample regressions (legacy)

Every note and role where 0.4.26 is worse than 0.4.25 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.25 | 0.4.26 |
|---|---|---|---|---|
| 52 | dev | tuning_cents | 0.48 | 3.69 |
| 73 | dev | level_db | 2.51 | 3.60 |
| 52 | dev | level_db | 1.78 | 2.67 |
| 52 | dev | sustain_db | 6.64 | 7.47 |
| 52 | dev | attack_db | 7.32 | 8.03 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (14.5631 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 8 | 7.8846 | 7.1295 | -0.7551 | 0 | 0 | 0 |
| dev | tuning_cents | 8 | 1.0239 | 2.6419 | 1.6180 | 0 | 0 | 0 |
| dev | decay_db_s | 8 | 4.4461 | 3.7271 | -0.7190 | 0 | 0 | 0 |
| dev | attack_db | 8 | 6.9444 | 7.2663 | 0.3219 | 0 | 0 | 0 |
| dev | early_db | 8 | 6.6789 | 6.5068 | -0.1721 | 0 | 0 | 0 |
| dev | sustain_db | 8 | 6.1727 | 6.3853 | 0.2126 | 0 | 0 | 0 |
| dev | noise_db | 5 | 7.0747 | 5.7268 | -1.3478 | 1 | 0 | 2 |
| dev | ild_db | 8 | 4.8605 | 4.8235 | -0.0370 | 0 | 0 | 0 |
| dev | icc | 8 | 0.1999 | 0.1943 | -0.0056 | 0 | 0 | 0 |
| dev | envelope_db | 8 | 2.5367 | 2.2880 | -0.2487 | 0 | 0 | 0 |
| dev | rise_ms | 8 | 3.7370 | 3.0521 | -0.6849 | 0 | 0 | 0 |
| dev | level_db | 8 | 2.1456 | 3.5555 | 1.4100 | 0 | 0 | 0 |
| train | partial_db | 40 | 4.6717 | 4.6888 | 0.0171 | 0 | 0 | 0 |
| train | tuning_cents | 40 | 0.2594 | 0.2597 | 0.0003 | 0 | 0 | 0 |
| train | decay_db_s | 40 | 3.4259 | 3.4089 | -0.0170 | 0 | 0 | 0 |
| train | attack_db | 40 | 6.1338 | 6.1796 | 0.0459 | 0 | 0 | 0 |
| train | early_db | 40 | 5.0571 | 5.1231 | 0.0659 | 0 | 0 | 0 |
| train | sustain_db | 40 | 5.6031 | 5.6609 | 0.0578 | 0 | 0 | 0 |
| train | noise_db | 37 | 7.1438 | 7.2363 | 0.0925 | 0 | 0 | 3 |
| train | ild_db | 40 | 1.5252 | 1.5258 | 0.0006 | 0 | 0 | 0 |
| train | icc | 40 | 0.1157 | 0.1157 | 0.0000 | 0 | 0 | 0 |
| train | envelope_db | 40 | 3.2889 | 3.3159 | 0.0270 | 0 | 0 | 0 |
| train | rise_ms | 40 | 17.4208 | 17.4130 | -0.0078 | 0 | 0 | 0 |
| train | level_db | 40 | 0.6923 | 0.7302 | 0.0379 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 52 | dev | tuning_cents | 4 | 0.4776 | 3.6901 | 3.2125 |
| 73 | dev | level_db | 4 | 2.5105 | 4.0083 | 1.4978 |
| 52 | dev | level_db | 4 | 1.7807 | 3.1028 | 1.3221 |
| 52 | dev | sustain_db | 4 | 6.6438 | 7.4735 | 0.8296 |
| 52 | dev | attack_db | 4 | 7.3222 | 8.0306 | 0.7084 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| n52v2r1 | 52 | dev | noise_db | lost | 3.7250 | - |
