# Recording benchmark: candidate 2.13.0 against 2.12.0

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.12.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.68 | 3.36 | 4.39 | 7.65 | 9.07 | 10.52 | 9.80 | 6.43 | 0.24 | 4.25 | 13.19 | 4.23 |
| dev (21) | 7.47 | 3.41 | 4.66 | 7.68 | 9.08 | 9.87 | 8.66 | 6.03 | 0.26 | 4.12 | 9.08 | 3.15 |
| train / bass A0-B2 (30) | 10.62 | 4.77 | 4.17 | 8.38 | 9.27 | 10.38 | 15.16 | 6.86 | 0.20 | 2.81 | 9.17 | 3.60 |
| train / middle C3-B5 (69) | 7.45 | 2.91 | 4.00 | 7.48 | 8.26 | 8.31 | 8.74 | 6.06 | 0.20 | 3.83 | 19.78 | 4.66 |
| train / treble C6-C8 (38) | 5.80 | 3.07 | 5.33 | 7.37 | 10.39 | 14.66 | 7.50 | 6.80 | 0.36 | 6.14 | 4.41 | 3.95 |
| dev / bass A0-B2 (5) | 9.98 | 4.02 | 2.25 | 8.72 | 9.76 | 10.60 | 13.43 | 3.99 | 0.28 | 2.02 | 1.78 | 2.08 |
| dev / middle C3-B5 (11) | 6.34 | 2.08 | 4.40 | 7.11 | 7.95 | 7.83 | 7.33 | 8.09 | 0.22 | 3.79 | 14.74 | 3.61 |
| dev / treble C6-C8 (5) | 7.47 | 5.74 | 7.65 | 7.88 | 10.89 | 13.64 | 7.77 | 3.54 | 0.35 | 6.94 | 3.90 | 3.22 |

## candidate 2.13.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.70 | 3.43 | 4.41 | 7.64 | 9.06 | 10.52 | 9.81 | 6.46 | 0.24 | 4.23 | 13.14 | 4.23 |
| dev (21) | 7.55 | 3.55 | 4.65 | 7.67 | 9.07 | 9.87 | 8.67 | 5.99 | 0.26 | 4.12 | 9.07 | 3.15 |
| train / bass A0-B2 (30) | 10.80 | 5.22 | 4.28 | 8.36 | 9.21 | 10.35 | 15.10 | 6.98 | 0.20 | 2.75 | 8.95 | 3.60 |
| train / middle C3-B5 (69) | 7.40 | 2.85 | 3.98 | 7.47 | 8.26 | 8.31 | 8.79 | 6.05 | 0.20 | 3.83 | 19.78 | 4.65 |
| train / treble C6-C8 (38) | 5.80 | 3.07 | 5.33 | 7.37 | 10.39 | 14.66 | 7.50 | 6.80 | 0.36 | 6.14 | 4.41 | 3.94 |
| dev / bass A0-B2 (5) | 10.30 | 4.12 | 2.23 | 8.70 | 9.76 | 10.59 | 13.43 | 4.01 | 0.28 | 2.02 | 1.74 | 2.06 |
| dev / middle C3-B5 (11) | 6.34 | 2.29 | 4.39 | 7.11 | 7.93 | 7.83 | 7.35 | 8.01 | 0.22 | 3.79 | 14.75 | 3.62 |
| dev / treble C6-C8 (5) | 7.47 | 5.74 | 7.65 | 7.88 | 10.89 | 13.64 | 7.77 | 3.54 | 0.35 | 6.94 | 3.90 | 3.21 |

## Independent-sample regressions (legacy)

Every note and role where candidate 2.13.0 is worse than 2.12.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.12.0 | candidate 2.13.0 |
|---|---|---|---|---|
| 27 | train | rise_ms | 10.56 | 19.38 |
| 24 | train | tuning_cents | 8.09 | 9.06 |
| 27 | train | tuning_cents | 6.73 | 7.65 |
| 24 | train | partial_db | 11.74 | 12.62 |
| 36 | train | partial_db | 11.72 | 12.50 |
| 27 | train | decay_db_s | 7.98 | 9.18 |
| 36 | train | tuning_cents | 3.74 | 4.32 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.4053 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 7.4740 | 7.5504 | 0.0764 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 3.4107 | 3.5456 | 0.1349 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 4.6598 | 4.6505 | -0.0094 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.6762 | 7.6700 | -0.0062 | 0 | 0 | 0 |
| dev | early_db | 21 | 9.0798 | 9.0705 | -0.0093 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 9.8687 | 9.8720 | 0.0033 | 0 | 0 | 0 |
| dev | noise_db | 20 | 8.6585 | 8.6723 | 0.0138 | 0 | 0 | 1 |
| dev | ild_db | 21 | 6.0296 | 5.9939 | -0.0357 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2626 | 0.2632 | 0.0006 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.1182 | 4.1157 | -0.0025 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 9.0764 | 9.0694 | -0.0069 | 0 | 0 | 0 |
| dev | level_db | 21 | 3.1523 | 3.1442 | -0.0081 | 0 | 0 | 0 |
| train | partial_db | 137 | 7.6849 | 7.7032 | 0.0182 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 3.3647 | 3.4330 | 0.0683 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 4.3938 | 4.4075 | 0.0137 | 0 | 0 | 2 |
| train | attack_db | 137 | 7.6455 | 7.6394 | -0.0062 | 0 | 0 | 0 |
| train | early_db | 137 | 9.0702 | 9.0596 | -0.0106 | 0 | 0 | 0 |
| train | sustain_db | 137 | 10.5245 | 10.5186 | -0.0058 | 0 | 0 | 0 |
| train | noise_db | 137 | 9.7997 | 9.8120 | 0.0123 | 0 | 0 | 0 |
| train | ild_db | 135 | 6.4346 | 6.4559 | 0.0214 | 0 | 0 | 2 |
| train | icc | 135 | 0.2414 | 0.2424 | 0.0011 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.2465 | 4.2322 | -0.0143 | 0 | 0 | 0 |
| train | rise_ms | 137 | 13.1934 | 13.1429 | -0.0505 | 0 | 0 | 0 |
| train | level_db | 137 | 4.2294 | 4.2261 | -0.0033 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 27 | train | rise_ms | 5 | 10.5583 | 19.3792 | 8.8208 |
| 24 | train | tuning_cents | 5 | 8.0900 | 9.0604 | 0.9705 |
| 27 | train | tuning_cents | 5 | 6.7329 | 7.6506 | 0.9177 |
| 24 | train | partial_db | 5 | 11.7398 | 12.6235 | 0.8838 |
| 36 | train | partial_db | 5 | 11.7185 | 12.4988 | 0.7803 |
| 27 | train | decay_db_s | 5 | 7.9820 | 9.1795 | 1.1974 |
| 36 | train | tuning_cents | 5 | 3.7439 | 4.3164 | 0.5724 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
