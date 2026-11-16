# Recording benchmark: 2.16.1 against 2.16.0 (1bc8982)

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.16.0 (1bc8982)

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.65 | 3.47 | 4.48 | 7.47 | 8.78 | 10.47 | 9.95 | 5.98 | 0.22 | 4.22 | 12.67 | 4.28 |
| dev (21) | 7.63 | 3.90 | 4.96 | 7.50 | 8.51 | 10.00 | 8.56 | 5.41 | 0.24 | 4.55 | 9.12 | 3.48 |
| train / bass A0-B2 (30) | 10.26 | 4.98 | 4.16 | 8.77 | 9.60 | 10.53 | 15.63 | 6.29 | 0.19 | 2.87 | 6.82 | 3.69 |
| train / middle C3-B5 (69) | 7.46 | 2.93 | 4.31 | 7.28 | 7.88 | 8.35 | 8.84 | 5.96 | 0.19 | 3.81 | 19.75 | 4.72 |
| train / treble C6-C8 (38) | 5.94 | 3.27 | 5.06 | 6.77 | 9.77 | 14.27 | 7.50 | 5.76 | 0.31 | 6.04 | 4.42 | 3.97 |
| dev / bass A0-B2 (5) | 8.86 | 3.57 | 2.91 | 9.11 | 10.27 | 10.62 | 12.92 | 3.98 | 0.30 | 1.92 | 1.98 | 2.66 |
| dev / middle C3-B5 (11) | 6.51 | 2.46 | 4.41 | 6.95 | 7.12 | 8.33 | 7.22 | 7.25 | 0.19 | 4.77 | 14.61 | 3.90 |
| dev / treble C6-C8 (5) | 8.85 | 7.40 | 8.21 | 7.09 | 9.82 | 13.06 | 7.16 | 2.78 | 0.29 | 6.67 | 4.18 | 3.39 |

## 2.16.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.66 | 3.47 | 4.48 | 7.47 | 8.78 | 10.47 | 9.94 | 5.98 | 0.22 | 4.22 | 12.67 | 4.28 |
| dev (21) | 7.63 | 3.90 | 4.96 | 7.50 | 8.51 | 10.00 | 8.54 | 5.41 | 0.24 | 4.55 | 9.12 | 3.48 |
| train / bass A0-B2 (30) | 10.26 | 4.98 | 4.16 | 8.77 | 9.59 | 10.52 | 15.59 | 6.29 | 0.19 | 2.87 | 6.82 | 3.69 |
| train / middle C3-B5 (69) | 7.47 | 2.93 | 4.31 | 7.28 | 7.88 | 8.35 | 8.83 | 5.96 | 0.19 | 3.81 | 19.75 | 4.72 |
| train / treble C6-C8 (38) | 5.94 | 3.27 | 5.06 | 6.77 | 9.77 | 14.27 | 7.50 | 5.76 | 0.31 | 6.04 | 4.42 | 3.97 |
| dev / bass A0-B2 (5) | 8.86 | 3.58 | 2.91 | 9.11 | 10.27 | 10.62 | 12.82 | 3.98 | 0.30 | 1.92 | 1.98 | 2.66 |
| dev / middle C3-B5 (11) | 6.51 | 2.46 | 4.41 | 6.95 | 7.12 | 8.33 | 7.22 | 7.25 | 0.19 | 4.77 | 14.61 | 3.90 |
| dev / treble C6-C8 (5) | 8.85 | 7.40 | 8.21 | 7.09 | 9.82 | 13.06 | 7.16 | 2.78 | 0.29 | 6.67 | 4.18 | 3.39 |

## Independent-sample regressions (legacy)

Every note and role where 2.16.1 is worse than 2.16.0 (1bc8982) by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.1845 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 7.6277 | 7.6258 | -0.0019 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 3.9002 | 3.9025 | 0.0023 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 4.9574 | 4.9575 | 0.0001 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.4972 | 7.4968 | -0.0004 | 0 | 0 | 0 |
| dev | early_db | 21 | 8.5117 | 8.5115 | -0.0001 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 10.0028 | 10.0029 | 0.0001 | 0 | 0 | 0 |
| dev | noise_db | 21 | 8.5631 | 8.5395 | -0.0237 | 0 | 0 | 0 |
| dev | ild_db | 21 | 5.4076 | 5.4076 | 0.0000 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2430 | 0.2430 | -0.0000 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.5468 | 4.5468 | -0.0000 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 9.1171 | 9.1171 | 0.0000 | 0 | 0 | 0 |
| dev | level_db | 21 | 3.4834 | 3.4834 | 0.0000 | 0 | 0 | 0 |
| train | partial_db | 137 | 7.6526 | 7.6574 | 0.0048 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 3.4748 | 3.4749 | 0.0001 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 4.4778 | 4.4771 | -0.0007 | 0 | 0 | 2 |
| train | attack_db | 137 | 7.4673 | 7.4659 | -0.0014 | 0 | 0 | 0 |
| train | early_db | 137 | 8.7809 | 8.7793 | -0.0016 | 0 | 0 | 0 |
| train | sustain_db | 137 | 10.4679 | 10.4672 | -0.0006 | 0 | 0 | 0 |
| train | noise_db | 137 | 9.9543 | 9.9410 | -0.0134 | 0 | 0 | 0 |
| train | ild_db | 135 | 5.9824 | 5.9823 | -0.0001 | 0 | 0 | 2 |
| train | icc | 135 | 0.2207 | 0.2207 | -0.0000 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.2217 | 4.2217 | 0.0000 | 0 | 0 | 0 |
| train | rise_ms | 137 | 12.6651 | 12.6655 | 0.0003 | 0 | 0 | 0 |
| train | level_db | 137 | 4.2846 | 4.2846 | 0.0000 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
