# Recording benchmark: 0.4.28 against 0.4.27

Every train and dev note of `Tools/corpus/split-vcsl-kawai-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.27

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (104) | 8.31 | 0.54 | 3.91 | 6.56 | 7.48 | 7.86 | 8.30 | 1.76 | 0.10 | 3.53 | 7.45 | 1.93 |
| dev (23) | 9.64 | 2.39 | 5.04 | 7.09 | 8.64 | 8.39 | 9.04 | 5.59 | 0.20 | 5.08 | 5.45 | 4.21 |
| train / bass A0-B2 (27) | 9.92 | 0.44 | 1.86 | 6.51 | 7.07 | 7.44 | 9.42 | 1.43 | 0.07 | 2.89 | 14.97 | 1.50 |
| train / middle C3-B5 (52) | 8.75 | 0.51 | 4.15 | 6.41 | 7.39 | 8.52 | 8.14 | 2.13 | 0.11 | 3.79 | 5.69 | 1.96 |
| train / treble C6-C8 (25) | 5.29 | 0.76 | 6.80 | 6.94 | 8.16 | 6.40 | 7.64 | 1.02 | 0.07 | 3.66 | 2.99 | 2.35 |
| dev / bass A0-B2 (8) | 10.30 | 2.28 | 2.59 | 6.08 | 6.14 | 8.53 | 9.56 | 3.24 | 0.15 | 3.83 | 9.17 | 1.73 |
| dev / middle C3-B5 (12) | 9.15 | 2.14 | 6.01 | 7.15 | 9.20 | 8.89 | 8.42 | 7.76 | 0.16 | 5.73 | 3.72 | 4.72 |
| dev / treble C6-C8 (3) | 9.92 | 4.30 | 8.97 | 9.59 | 13.06 | 4.89 | 9.96 | 3.08 | 0.66 | 5.80 | 2.48 | 8.78 |

## 0.4.28

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (104) | 8.31 | 0.55 | 3.94 | 6.44 | 7.51 | 7.86 | 8.28 | 1.76 | 0.10 | 3.51 | 7.34 | 1.93 |
| dev (23) | 9.64 | 2.39 | 5.04 | 6.95 | 8.71 | 8.40 | 8.94 | 5.59 | 0.20 | 5.07 | 5.46 | 4.21 |
| train / bass A0-B2 (27) | 9.92 | 0.44 | 1.86 | 6.51 | 7.07 | 7.44 | 9.42 | 1.43 | 0.07 | 2.89 | 14.97 | 1.50 |
| train / middle C3-B5 (52) | 8.75 | 0.51 | 4.21 | 6.38 | 7.44 | 8.52 | 8.24 | 2.13 | 0.12 | 3.79 | 5.47 | 1.96 |
| train / treble C6-C8 (25) | 5.29 | 0.76 | 6.80 | 6.47 | 8.17 | 6.40 | 7.36 | 1.02 | 0.07 | 3.61 | 2.99 | 2.34 |
| dev / bass A0-B2 (8) | 10.30 | 2.28 | 2.59 | 6.08 | 6.14 | 8.53 | 9.56 | 3.24 | 0.15 | 3.83 | 9.17 | 1.73 |
| dev / middle C3-B5 (12) | 9.15 | 2.14 | 6.01 | 7.17 | 9.30 | 8.89 | 8.49 | 7.76 | 0.16 | 5.73 | 3.72 | 4.72 |
| dev / treble C6-C8 (3) | 9.93 | 4.30 | 8.97 | 8.37 | 13.19 | 4.90 | 8.96 | 3.09 | 0.66 | 5.74 | 2.49 | 8.77 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.28 is worse than 0.4.27 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.27 | 0.4.28 |
|---|---|---|---|---|
| 84 | train | attack_db | 4.08 | 4.62 |
| 64 | train | noise_db | 9.47 | 10.01 |
| 60 | train | rise_ms | 9.93 | 10.98 |
| 87 | train | early_db | 6.29 | 6.80 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.7486 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 22 | 9.6370 | 9.6377 | 0.0006 | 0 | 0 | 1 |
| dev | tuning_cents | 22 | 2.3894 | 2.3894 | 0.0000 | 0 | 0 | 1 |
| dev | decay_db_s | 22 | 5.0367 | 5.0376 | 0.0009 | 0 | 0 | 1 |
| dev | attack_db | 23 | 7.0935 | 6.9463 | -0.1472 | 0 | 0 | 0 |
| dev | early_db | 23 | 8.6411 | 8.7093 | 0.0682 | 0 | 0 | 0 |
| dev | sustain_db | 22 | 8.3938 | 8.3951 | 0.0013 | 0 | 0 | 1 |
| dev | noise_db | 22 | 9.0413 | 8.9414 | -0.0999 | 0 | 0 | 1 |
| dev | ild_db | 21 | 5.5934 | 5.5916 | -0.0018 | 0 | 0 | 2 |
| dev | icc | 21 | 0.2045 | 0.2046 | 0.0001 | 0 | 0 | 2 |
| dev | envelope_db | 23 | 5.0817 | 5.0729 | -0.0089 | 0 | 0 | 0 |
| dev | rise_ms | 23 | 5.4533 | 5.4561 | 0.0027 | 0 | 0 | 0 |
| dev | level_db | 23 | 4.2073 | 4.2061 | -0.0013 | 0 | 0 | 0 |
| train | partial_db | 100 | 8.3070 | 8.3053 | -0.0017 | 0 | 0 | 4 |
| train | tuning_cents | 100 | 0.5439 | 0.5471 | 0.0032 | 0 | 0 | 4 |
| train | decay_db_s | 93 | 3.9123 | 3.9447 | 0.0324 | 0 | 0 | 11 |
| train | attack_db | 104 | 6.5634 | 6.4390 | -0.1244 | 0 | 0 | 0 |
| train | early_db | 102 | 7.4770 | 7.5052 | 0.0282 | 0 | 0 | 2 |
| train | sustain_db | 95 | 7.8575 | 7.8568 | -0.0007 | 0 | 0 | 9 |
| train | noise_db | 95 | 8.3049 | 8.2824 | -0.0225 | 0 | 0 | 9 |
| train | ild_db | 90 | 1.7569 | 1.7579 | 0.0010 | 0 | 0 | 14 |
| train | icc | 90 | 0.0962 | 0.0965 | 0.0003 | 0 | 0 | 14 |
| train | envelope_db | 104 | 3.5268 | 3.5130 | -0.0139 | 0 | 0 | 0 |
| train | rise_ms | 104 | 7.4491 | 7.3415 | -0.1076 | 0 | 0 | 0 |
| train | level_db | 104 | 1.9341 | 1.9307 | -0.0034 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 84 | train | attack_db | 4 | 4.0770 | 4.6153 | 0.5383 |
| 64 | train | noise_db | 4 | 9.4748 | 10.0072 | 0.5324 |
| 60 | train | rise_ms | 4 | 9.9273 | 10.9793 | 1.0521 |
| 87 | train | early_db | 3 | 6.2870 | 6.8015 | 0.5145 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
