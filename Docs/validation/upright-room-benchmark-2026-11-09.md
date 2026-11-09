# Recording benchmark: 0.4.27 against 0.4.26

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.26

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 5.78 | 0.27 | 2.38 | 5.15 | 5.27 | 5.75 | 7.42 | 2.14 | 0.14 | 2.61 | 7.79 | 1.20 |
| dev (21) | 8.23 | 1.58 | 3.99 | 6.47 | 7.26 | 8.64 | 6.84 | 4.21 | 0.21 | 4.51 | 6.19 | 2.52 |
| train / bass A0-B2 (30) | 6.90 | 0.29 | 1.93 | 5.61 | 5.18 | 5.36 | 10.26 | 1.28 | 0.10 | 2.51 | 8.78 | 0.95 |
| train / middle C3-B5 (69) | 6.58 | 0.23 | 2.55 | 5.34 | 4.94 | 5.45 | 7.58 | 1.94 | 0.10 | 2.14 | 9.54 | 1.39 |
| train / treble C6-C8 (38) | 3.44 | 0.31 | 2.42 | 4.42 | 5.95 | 6.65 | 5.44 | 3.22 | 0.23 | 3.55 | 3.83 | 1.05 |
| dev / bass A0-B2 (5) | 8.81 | 1.25 | 2.08 | 5.79 | 7.48 | 8.96 | 7.09 | 5.19 | 0.20 | 2.09 | 1.42 | 1.41 |
| dev / middle C3-B5 (11) | 8.45 | 0.95 | 3.82 | 7.07 | 6.94 | 8.02 | 6.93 | 4.22 | 0.17 | 4.56 | 10.54 | 2.71 |
| dev / treble C6-C8 (5) | 7.17 | 3.30 | 6.27 | 5.85 | 7.73 | 9.70 | 6.46 | 3.24 | 0.29 | 6.83 | 1.38 | 3.21 |

## 0.4.27

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 5.77 | 0.27 | 2.41 | 5.15 | 5.26 | 5.81 | 7.39 | 2.13 | 0.13 | 2.61 | 7.75 | 1.20 |
| dev (21) | 8.23 | 1.60 | 3.99 | 6.48 | 7.25 | 8.64 | 6.85 | 4.19 | 0.20 | 4.51 | 6.19 | 2.52 |
| train / bass A0-B2 (30) | 6.87 | 0.31 | 2.05 | 5.62 | 5.17 | 5.36 | 10.13 | 1.29 | 0.10 | 2.51 | 8.78 | 0.94 |
| train / middle C3-B5 (69) | 6.58 | 0.23 | 2.55 | 5.34 | 4.94 | 5.44 | 7.56 | 1.94 | 0.10 | 2.14 | 9.46 | 1.39 |
| train / treble C6-C8 (38) | 3.44 | 0.32 | 2.42 | 4.42 | 5.91 | 6.82 | 5.43 | 3.22 | 0.22 | 3.55 | 3.83 | 1.05 |
| dev / bass A0-B2 (5) | 8.80 | 1.29 | 2.08 | 5.81 | 7.47 | 8.96 | 7.09 | 5.18 | 0.20 | 2.09 | 1.42 | 1.41 |
| dev / middle C3-B5 (11) | 8.45 | 0.97 | 3.82 | 7.07 | 6.93 | 8.01 | 6.92 | 4.21 | 0.17 | 4.56 | 10.55 | 2.71 |
| dev / treble C6-C8 (5) | 7.17 | 3.30 | 6.28 | 5.84 | 7.74 | 9.70 | 6.50 | 3.17 | 0.28 | 6.83 | 1.38 | 3.21 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.27 is worse than 0.4.26 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.26 | 0.4.27 |
|---|---|---|---|---|
| 100 | train | sustain_db | 9.47 | 10.64 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (15.9388 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 8.2322 | 8.2307 | -0.0015 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 1.5783 | 1.6010 | 0.0227 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 3.9906 | 3.9909 | 0.0003 | 0 | 0 | 0 |
| dev | attack_db | 21 | 6.4730 | 6.4796 | 0.0067 | 0 | 0 | 0 |
| dev | early_db | 21 | 7.2562 | 7.2519 | -0.0043 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 8.6443 | 8.6400 | -0.0043 | 0 | 0 | 0 |
| dev | noise_db | 20 | 6.8440 | 6.8499 | 0.0059 | 0 | 0 | 1 |
| dev | ild_db | 21 | 4.2148 | 4.1935 | -0.0213 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2063 | 0.2022 | -0.0040 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.5130 | 4.5130 | -0.0000 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 6.1875 | 6.1905 | 0.0030 | 0 | 0 | 0 |
| dev | level_db | 21 | 2.5193 | 2.5189 | -0.0004 | 0 | 0 | 0 |
| train | partial_db | 137 | 5.7778 | 5.7727 | -0.0051 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 0.2669 | 0.2727 | 0.0058 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 2.3788 | 2.4051 | 0.0264 | 0 | 0 | 2 |
| train | attack_db | 137 | 5.1478 | 5.1472 | -0.0005 | 0 | 0 | 0 |
| train | early_db | 137 | 5.2730 | 5.2572 | -0.0158 | 0 | 0 | 0 |
| train | sustain_db | 136 | 5.7539 | 5.7425 | -0.0114 | 0 | 1 | 0 |
| train | noise_db | 125 | 7.4198 | 7.3865 | -0.0333 | 0 | 0 | 12 |
| train | ild_db | 135 | 2.1382 | 2.1343 | -0.0040 | 0 | 0 | 2 |
| train | icc | 135 | 0.1352 | 0.1323 | -0.0029 | 0 | 0 | 2 |
| train | envelope_db | 137 | 2.6124 | 2.6117 | -0.0007 | 0 | 0 | 0 |
| train | rise_ms | 137 | 7.7885 | 7.7508 | -0.0377 | 0 | 0 | 0 |
| train | level_db | 137 | 1.1972 | 1.1970 | -0.0003 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| n100v1r1 | 100 | train | sustain_db | gained | - | 14.3110 |
