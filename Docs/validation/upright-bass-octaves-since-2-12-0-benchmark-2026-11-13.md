# Recording benchmark: candidate 2.13.1 against 2.12.0

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

## candidate 2.13.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.54 | 3.33 | 4.37 | 7.65 | 9.09 | 10.54 | 9.82 | 6.40 | 0.24 | 4.24 | 12.81 | 4.24 |
| dev (21) | 7.27 | 3.39 | 4.65 | 7.71 | 9.10 | 9.88 | 8.75 | 5.94 | 0.27 | 4.13 | 9.15 | 3.19 |
| train / bass A0-B2 (30) | 10.07 | 4.74 | 4.11 | 8.43 | 9.34 | 10.44 | 15.24 | 6.72 | 0.20 | 2.80 | 7.42 | 3.63 |
| train / middle C3-B5 (69) | 7.39 | 2.87 | 3.99 | 7.47 | 8.26 | 8.32 | 8.75 | 6.04 | 0.20 | 3.83 | 19.78 | 4.66 |
| train / treble C6-C8 (38) | 5.80 | 3.07 | 5.33 | 7.37 | 10.39 | 14.66 | 7.50 | 6.80 | 0.36 | 6.14 | 4.41 | 3.95 |
| dev / bass A0-B2 (5) | 9.22 | 3.34 | 2.27 | 8.88 | 9.86 | 10.62 | 12.82 | 3.80 | 0.29 | 2.09 | 2.07 | 2.23 |
| dev / middle C3-B5 (11) | 6.29 | 2.34 | 4.37 | 7.11 | 7.93 | 7.83 | 7.35 | 8.01 | 0.22 | 3.79 | 14.75 | 3.60 |
| dev / treble C6-C8 (5) | 7.47 | 5.74 | 7.65 | 7.88 | 10.89 | 13.64 | 7.77 | 3.54 | 0.35 | 6.94 | 3.90 | 3.22 |

## Independent-sample regressions (legacy)

Every note and role where candidate 2.13.1 is worse than 2.12.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.12.0 | candidate 2.13.1 |
|---|---|---|---|---|
| 56 | dev | tuning_cents | 0.89 | 1.41 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.4053 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 7.4740 | 7.2686 | -0.2053 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 3.4107 | 3.3869 | -0.0238 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 4.6598 | 4.6477 | -0.0121 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.6762 | 7.7115 | 0.0353 | 0 | 0 | 0 |
| dev | early_db | 21 | 9.0798 | 9.0951 | 0.0153 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 9.8687 | 9.8773 | 0.0086 | 0 | 0 | 0 |
| dev | noise_db | 20 | 8.6585 | 8.6555 | -0.0030 | 0 | 1 | 0 |
| dev | ild_db | 21 | 6.0296 | 5.9421 | -0.0875 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2626 | 0.2660 | 0.0034 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.1182 | 4.1321 | 0.0138 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 9.0764 | 9.1488 | 0.0724 | 0 | 0 | 0 |
| dev | level_db | 21 | 3.1523 | 3.1767 | 0.0244 | 0 | 0 | 0 |
| train | partial_db | 137 | 7.6849 | 7.5369 | -0.1480 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 3.3647 | 3.3346 | -0.0301 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 4.3938 | 4.3713 | -0.0225 | 0 | 0 | 2 |
| train | attack_db | 137 | 7.6455 | 7.6533 | 0.0078 | 0 | 0 | 0 |
| train | early_db | 137 | 9.0702 | 9.0879 | 0.0177 | 0 | 0 | 0 |
| train | sustain_db | 137 | 10.5245 | 10.5409 | 0.0164 | 0 | 0 | 0 |
| train | noise_db | 137 | 9.7997 | 9.8228 | 0.0231 | 0 | 0 | 0 |
| train | ild_db | 135 | 6.4346 | 6.3964 | -0.0381 | 0 | 0 | 2 |
| train | icc | 135 | 0.2414 | 0.2423 | 0.0010 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.2465 | 4.2440 | -0.0025 | 0 | 0 | 0 |
| train | rise_ms | 137 | 13.1934 | 12.8104 | -0.3831 | 0 | 0 | 0 |
| train | level_db | 137 | 4.2294 | 4.2383 | 0.0089 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 56 | dev | tuning_cents | 5 | 0.8946 | 1.4077 | 0.5131 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| n39v1r1 | 39 | dev | noise_db | gained | - | 10.7280 |
