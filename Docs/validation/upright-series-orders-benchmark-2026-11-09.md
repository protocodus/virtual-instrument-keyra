# Recording benchmark: 0.4.30 against 0.4.29

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.29

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 5.77 | 0.28 | 2.41 | 4.99 | 4.95 | 5.67 | 7.22 | 1.85 | 0.12 | 2.58 | 7.79 | 1.20 |
| dev (21) | 8.24 | 1.60 | 3.99 | 6.29 | 7.01 | 8.53 | 6.73 | 3.89 | 0.19 | 4.53 | 5.86 | 2.53 |
| train / bass A0-B2 (30) | 6.85 | 0.31 | 2.04 | 5.56 | 5.15 | 5.36 | 10.32 | 1.29 | 0.10 | 2.37 | 8.95 | 0.92 |
| train / middle C3-B5 (69) | 6.59 | 0.24 | 2.56 | 5.19 | 4.82 | 5.40 | 7.43 | 1.84 | 0.09 | 2.15 | 9.56 | 1.40 |
| train / treble C6-C8 (38) | 3.45 | 0.31 | 2.43 | 4.20 | 5.03 | 6.38 | 4.99 | 2.34 | 0.18 | 3.52 | 3.66 | 1.04 |
| dev / bass A0-B2 (5) | 8.81 | 1.28 | 2.08 | 5.69 | 7.45 | 8.95 | 7.08 | 5.20 | 0.20 | 2.13 | 1.07 | 1.44 |
| dev / middle C3-B5 (11) | 8.46 | 0.98 | 3.82 | 6.97 | 6.79 | 7.96 | 6.98 | 3.95 | 0.17 | 4.57 | 10.00 | 2.71 |
| dev / treble C6-C8 (5) | 7.19 | 3.30 | 6.28 | 5.40 | 7.04 | 9.37 | 5.91 | 2.48 | 0.25 | 6.84 | 1.54 | 3.21 |

## 0.4.30

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 5.75 | 0.26 | 2.38 | 4.99 | 4.95 | 5.66 | 7.21 | 1.85 | 0.12 | 2.58 | 7.79 | 1.20 |
| dev (21) | 8.23 | 1.62 | 4.08 | 6.29 | 7.00 | 8.52 | 6.73 | 3.90 | 0.19 | 4.53 | 5.86 | 2.53 |
| train / bass A0-B2 (30) | 6.76 | 0.26 | 1.97 | 5.53 | 5.12 | 5.32 | 10.31 | 1.29 | 0.10 | 2.37 | 8.96 | 0.92 |
| train / middle C3-B5 (69) | 6.58 | 0.23 | 2.54 | 5.19 | 4.83 | 5.40 | 7.42 | 1.84 | 0.09 | 2.15 | 9.56 | 1.40 |
| train / treble C6-C8 (38) | 3.45 | 0.31 | 2.43 | 4.20 | 5.03 | 6.38 | 4.99 | 2.34 | 0.18 | 3.52 | 3.66 | 1.04 |
| dev / bass A0-B2 (5) | 8.81 | 1.28 | 2.08 | 5.69 | 7.45 | 8.95 | 7.08 | 5.20 | 0.20 | 2.13 | 1.07 | 1.44 |
| dev / middle C3-B5 (11) | 8.43 | 1.02 | 4.00 | 6.96 | 6.77 | 7.93 | 6.98 | 3.95 | 0.17 | 4.57 | 10.01 | 2.71 |
| dev / treble C6-C8 (5) | 7.19 | 3.30 | 6.28 | 5.40 | 7.04 | 9.37 | 5.91 | 2.48 | 0.25 | 6.84 | 1.54 | 3.21 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.30 is worse than 0.4.29 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.29 | 0.4.30 |
|---|---|---|---|---|
| 59 | dev | decay_db_s | 3.32 | 6.36 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (15.8807 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 8.2419 | 8.2263 | -0.0156 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 1.6021 | 1.6233 | 0.0212 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 3.9920 | 4.0846 | 0.0926 | 0 | 0 | 0 |
| dev | attack_db | 21 | 6.2898 | 6.2895 | -0.0004 | 0 | 0 | 0 |
| dev | early_db | 21 | 7.0081 | 6.9967 | -0.0113 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 8.5332 | 8.5181 | -0.0150 | 0 | 0 | 0 |
| dev | noise_db | 20 | 6.7336 | 6.7315 | -0.0020 | 0 | 0 | 1 |
| dev | ild_db | 21 | 3.8946 | 3.8969 | 0.0023 | 0 | 0 | 0 |
| dev | icc | 21 | 0.1945 | 0.1942 | -0.0002 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.5277 | 4.5278 | 0.0001 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 5.8591 | 5.8631 | 0.0040 | 0 | 0 | 0 |
| dev | level_db | 21 | 2.5274 | 2.5273 | -0.0000 | 0 | 0 | 0 |
| train | partial_db | 137 | 5.7734 | 5.7506 | -0.0229 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 0.2777 | 0.2614 | -0.0162 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 2.4102 | 2.3817 | -0.0285 | 0 | 0 | 2 |
| train | attack_db | 137 | 4.9945 | 4.9905 | -0.0040 | 0 | 0 | 0 |
| train | early_db | 137 | 4.9512 | 4.9465 | -0.0047 | 0 | 0 | 0 |
| train | sustain_db | 137 | 5.6656 | 5.6571 | -0.0085 | 0 | 0 | 0 |
| train | noise_db | 125 | 7.2168 | 7.2115 | -0.0054 | 0 | 0 | 12 |
| train | ild_db | 135 | 1.8505 | 1.8503 | -0.0002 | 0 | 0 | 2 |
| train | icc | 135 | 0.1160 | 0.1161 | 0.0001 | 0 | 0 | 2 |
| train | envelope_db | 137 | 2.5787 | 2.5787 | 0.0000 | 0 | 0 | 0 |
| train | rise_ms | 137 | 7.7909 | 7.7918 | 0.0009 | 0 | 0 | 0 |
| train | level_db | 137 | 1.1960 | 1.1960 | -0.0000 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 59 | dev | decay_db_s | 1 | 3.3158 | 6.3598 | 3.0440 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
