# Recording benchmark: 2.24.0 against 2.23.0

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.23.0

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

## 2.24.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.28 | 3.20 | 4.61 | 7.77 | 9.27 | 10.46 | 10.96 | 6.55 | 0.24 | 4.24 | 11.78 | 3.90 |
| dev (21) | 7.36 | 3.63 | 5.03 | 7.64 | 8.99 | 9.88 | 9.65 | 6.49 | 0.27 | 4.64 | 9.09 | 2.86 |
| train / bass A0-B2 (30) | 9.64 | 4.86 | 4.48 | 9.00 | 9.98 | 10.43 | 18.12 | 6.48 | 0.19 | 2.87 | 6.84 | 3.32 |
| train / middle C3-B5 (69) | 7.03 | 2.71 | 4.40 | 7.42 | 8.22 | 8.21 | 9.51 | 6.28 | 0.20 | 3.77 | 17.95 | 4.32 |
| train / treble C6-C8 (38) | 5.88 | 2.79 | 5.09 | 7.44 | 10.61 | 14.58 | 7.94 | 7.11 | 0.37 | 6.19 | 4.46 | 3.59 |
| dev / bass A0-B2 (5) | 9.43 | 3.52 | 3.03 | 9.58 | 10.27 | 10.44 | 15.77 | 4.55 | 0.30 | 2.11 | 1.97 | 2.49 |
| dev / middle C3-B5 (11) | 6.13 | 2.32 | 4.55 | 6.76 | 7.39 | 8.03 | 7.43 | 7.64 | 0.22 | 4.76 | 14.51 | 3.11 |
| dev / treble C6-C8 (5) | 8.00 | 6.61 | 8.06 | 7.64 | 11.21 | 13.41 | 8.39 | 5.92 | 0.35 | 6.89 | 4.31 | 2.69 |

## Independent-sample regressions (legacy)

Every note and role where 2.24.0 is worse than 2.23.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.23.0 | 2.24.0 |
|---|---|---|---|---|
| 24 | train | level_db | 3.24 | 3.95 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.1109 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 7.3627 | 7.3627 | 0.0000 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 3.6271 | 3.6271 | 0.0000 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 5.0268 | 5.0268 | 0.0000 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.6381 | 7.6379 | -0.0002 | 0 | 0 | 0 |
| dev | early_db | 21 | 8.9865 | 8.9865 | -0.0000 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 9.8821 | 9.8820 | -0.0000 | 0 | 0 | 0 |
| dev | noise_db | 21 | 9.6463 | 9.6462 | -0.0001 | 0 | 0 | 0 |
| dev | ild_db | 21 | 6.4933 | 6.4930 | -0.0002 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2729 | 0.2729 | -0.0000 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.6382 | 4.6382 | 0.0000 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 9.0933 | 9.0933 | 0.0000 | 0 | 0 | 0 |
| dev | level_db | 21 | 2.8826 | 2.9944 | 0.1118 | 0 | 0 | 0 |
| train | partial_db | 137 | 7.2981 | 7.2804 | -0.0176 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 3.2036 | 3.2042 | 0.0006 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 4.5758 | 4.6056 | 0.0298 | 0 | 0 | 2 |
| train | attack_db | 137 | 7.8152 | 7.7742 | -0.0410 | 0 | 0 | 0 |
| train | early_db | 137 | 9.2941 | 9.2680 | -0.0261 | 0 | 0 | 0 |
| train | sustain_db | 137 | 10.4689 | 10.4612 | -0.0077 | 0 | 0 | 0 |
| train | noise_db | 137 | 10.9954 | 10.9585 | -0.0369 | 0 | 0 | 0 |
| train | ild_db | 135 | 6.5539 | 6.5493 | -0.0046 | 0 | 0 | 2 |
| train | icc | 135 | 0.2420 | 0.2416 | -0.0004 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.2456 | 4.2428 | -0.0028 | 0 | 0 | 0 |
| train | rise_ms | 137 | 11.7673 | 11.7768 | 0.0094 | 0 | 0 | 0 |
| train | level_db | 137 | 4.0101 | 3.9008 | -0.1093 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 24 | train | level_db | 5 | 3.2359 | 3.8586 | 0.6228 |
| 96 | train | level_db | 5 | 3.8152 | 4.3433 | 0.5281 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
