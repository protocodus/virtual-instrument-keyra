# Recording benchmark: 2.22.0 against 2.21.0

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.21.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.27 | 3.20 | 4.58 | 7.85 | 9.33 | 10.48 | 11.20 | 6.55 | 0.24 | 4.24 | 11.77 | 3.92 |
| dev (21) | 7.36 | 3.63 | 5.01 | 7.68 | 9.01 | 9.88 | 9.84 | 6.49 | 0.27 | 4.64 | 9.08 | 2.81 |
| train / bass A0-B2 (30) | 9.60 | 4.85 | 4.39 | 9.19 | 10.13 | 10.49 | 18.87 | 6.48 | 0.19 | 2.87 | 6.79 | 3.17 |
| train / middle C3-B5 (69) | 7.02 | 2.71 | 4.40 | 7.42 | 8.22 | 8.21 | 9.59 | 6.28 | 0.20 | 3.77 | 17.95 | 4.29 |
| train / treble C6-C8 (38) | 5.91 | 2.78 | 5.10 | 7.55 | 10.70 | 14.61 | 8.06 | 7.13 | 0.37 | 6.20 | 4.47 | 3.82 |
| dev / bass A0-B2 (5) | 9.42 | 3.54 | 2.98 | 9.73 | 10.36 | 10.44 | 16.51 | 4.55 | 0.30 | 2.11 | 1.91 | 2.26 |
| dev / middle C3-B5 (11) | 6.14 | 2.32 | 4.55 | 6.76 | 7.39 | 8.02 | 7.47 | 7.64 | 0.22 | 4.76 | 14.51 | 3.15 |
| dev / treble C6-C8 (5) | 8.00 | 6.61 | 8.06 | 7.64 | 11.21 | 13.41 | 8.39 | 5.92 | 0.35 | 6.89 | 4.31 | 2.60 |

## 2.22.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.30 | 3.20 | 4.58 | 7.82 | 9.29 | 10.47 | 11.00 | 6.55 | 0.24 | 4.25 | 11.77 | 4.01 |
| dev (21) | 7.36 | 3.63 | 5.03 | 7.64 | 8.99 | 9.88 | 9.65 | 6.49 | 0.27 | 4.64 | 9.09 | 2.88 |
| train / bass A0-B2 (30) | 9.69 | 4.88 | 4.34 | 9.05 | 9.98 | 10.44 | 18.14 | 6.48 | 0.19 | 2.87 | 6.79 | 3.52 |
| train / middle C3-B5 (69) | 7.03 | 2.71 | 4.40 | 7.42 | 8.22 | 8.21 | 9.51 | 6.28 | 0.20 | 3.77 | 17.95 | 4.32 |
| train / treble C6-C8 (38) | 5.91 | 2.78 | 5.10 | 7.55 | 10.71 | 14.61 | 8.06 | 7.13 | 0.37 | 6.20 | 4.47 | 3.84 |
| dev / bass A0-B2 (5) | 9.43 | 3.52 | 3.03 | 9.58 | 10.27 | 10.44 | 15.77 | 4.55 | 0.30 | 2.11 | 1.97 | 2.53 |
| dev / middle C3-B5 (11) | 6.13 | 2.32 | 4.55 | 6.76 | 7.39 | 8.03 | 7.43 | 7.64 | 0.22 | 4.76 | 14.51 | 3.15 |
| dev / treble C6-C8 (5) | 8.00 | 6.61 | 8.06 | 7.64 | 11.22 | 13.41 | 8.39 | 5.92 | 0.35 | 6.89 | 4.31 | 2.64 |

## Independent-sample regressions (legacy)

Every note and role where 2.22.0 is worse than 2.21.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.4467 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 7.3603 | 7.3627 | 0.0025 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 3.6314 | 3.6271 | -0.0043 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 5.0123 | 5.0268 | 0.0145 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.6754 | 7.6380 | -0.0374 | 0 | 0 | 0 |
| dev | early_db | 21 | 9.0082 | 8.9865 | -0.0217 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 9.8809 | 9.8821 | 0.0012 | 0 | 0 | 0 |
| dev | noise_db | 21 | 9.8399 | 9.6463 | -0.1936 | 0 | 0 | 0 |
| dev | ild_db | 21 | 6.4929 | 6.4932 | 0.0003 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2727 | 0.2729 | 0.0001 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.6384 | 4.6382 | -0.0002 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 9.0784 | 9.0933 | 0.0149 | 0 | 0 | 0 |
| dev | level_db | 21 | 2.8088 | 2.8275 | 0.0187 | 0 | 0 | 0 |
| train | partial_db | 137 | 7.2749 | 7.2981 | 0.0232 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 3.1971 | 3.2036 | 0.0065 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 4.5840 | 4.5757 | -0.0082 | 0 | 0 | 2 |
| train | attack_db | 137 | 7.8461 | 7.8152 | -0.0309 | 0 | 0 | 0 |
| train | early_db | 137 | 9.3263 | 9.2940 | -0.0323 | 0 | 0 | 0 |
| train | sustain_db | 137 | 10.4813 | 10.4689 | -0.0124 | 0 | 0 | 0 |
| train | noise_db | 137 | 11.1965 | 10.9953 | -0.2012 | 0 | 0 | 0 |
| train | ild_db | 135 | 6.5534 | 6.5537 | 0.0003 | 0 | 0 | 2 |
| train | icc | 135 | 0.2420 | 0.2420 | 0.0001 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.2445 | 4.2456 | 0.0011 | 0 | 0 | 0 |
| train | rise_ms | 137 | 11.7666 | 11.7675 | 0.0009 | 0 | 0 | 0 |
| train | level_db | 137 | 3.9162 | 4.0230 | 0.1068 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 24 | train | level_db | 5 | 2.7382 | 3.2821 | 0.5439 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
