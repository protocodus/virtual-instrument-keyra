# Recording benchmark: 2.3.0 against 2.2.0

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.2.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 8.65 | 4.08 | 5.10 | 9.11 | 11.20 | 11.36 | 11.74 | 6.69 | 0.25 | 4.42 | 16.57 | 4.29 |
| dev (21) | 8.46 | 4.63 | 5.55 | 8.61 | 10.25 | 10.76 | 11.42 | 5.10 | 0.26 | 4.73 | 12.95 | 2.85 |
| train / bass A0-B2 (30) | 9.32 | 4.92 | 5.17 | 7.75 | 9.62 | 10.28 | 15.18 | 5.94 | 0.22 | 3.08 | 23.31 | 3.62 |
| train / middle C3-B5 (69) | 8.44 | 3.72 | 4.41 | 8.21 | 9.38 | 8.91 | 9.77 | 6.65 | 0.20 | 3.96 | 19.41 | 4.67 |
| train / treble C6-C8 (38) | 8.48 | 4.09 | 6.38 | 11.82 | 15.74 | 16.67 | 12.59 | 7.39 | 0.39 | 6.33 | 6.09 | 4.12 |
| dev / bass A0-B2 (5) | 8.44 | 4.82 | 3.84 | 7.80 | 9.51 | 9.77 | 16.38 | 4.51 | 0.27 | 2.94 | 24.97 | 1.93 |
| dev / middle C3-B5 (11) | 8.58 | 4.29 | 4.90 | 7.74 | 8.92 | 8.89 | 9.62 | 6.42 | 0.20 | 4.26 | 11.25 | 3.51 |
| dev / treble C6-C8 (5) | 8.21 | 5.18 | 8.69 | 11.32 | 13.92 | 15.85 | 11.41 | 2.79 | 0.37 | 7.55 | 4.67 | 2.31 |

## 2.3.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 8.66 | 4.02 | 5.12 | 8.89 | 10.86 | 11.32 | 11.41 | 6.68 | 0.25 | 4.42 | 16.57 | 4.29 |
| dev (21) | 8.57 | 4.55 | 5.72 | 8.52 | 10.17 | 10.76 | 11.23 | 5.10 | 0.26 | 4.73 | 12.84 | 2.85 |
| train / bass A0-B2 (30) | 9.30 | 4.94 | 5.11 | 7.75 | 9.62 | 10.28 | 15.25 | 5.94 | 0.22 | 3.08 | 23.31 | 3.62 |
| train / middle C3-B5 (69) | 8.46 | 3.64 | 4.49 | 8.19 | 9.38 | 8.92 | 9.77 | 6.65 | 0.20 | 3.96 | 19.41 | 4.67 |
| train / treble C6-C8 (38) | 8.50 | 3.99 | 6.33 | 11.04 | 14.52 | 16.50 | 11.38 | 7.38 | 0.39 | 6.32 | 6.08 | 4.12 |
| dev / bass A0-B2 (5) | 8.73 | 4.72 | 3.83 | 7.81 | 9.51 | 9.77 | 16.36 | 4.51 | 0.27 | 2.94 | 24.97 | 1.93 |
| dev / middle C3-B5 (11) | 8.66 | 4.19 | 5.18 | 7.74 | 8.91 | 8.89 | 9.53 | 6.42 | 0.20 | 4.26 | 11.25 | 3.51 |
| dev / treble C6-C8 (5) | 8.22 | 5.18 | 8.81 | 10.95 | 13.61 | 15.85 | 10.86 | 2.78 | 0.37 | 7.55 | 4.22 | 2.31 |

## Independent-sample regressions (legacy)

Every note and role where 2.3.0 is worse than 2.2.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.2.0 | 2.3.0 |
|---|---|---|---|---|
| 59 | dev | decay_db_s | 6.00 | 7.59 |
| 50 | train | noise_db | 7.02 | 7.55 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (11.4717 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 8.4573 | 8.5721 | 0.1148 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 4.6307 | 4.5539 | -0.0768 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 5.5515 | 5.7242 | 0.1727 | 0 | 0 | 0 |
| dev | attack_db | 21 | 8.6084 | 8.5201 | -0.0882 | 0 | 0 | 0 |
| dev | early_db | 21 | 10.2486 | 10.1736 | -0.0751 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 10.7551 | 10.7551 | 0.0001 | 0 | 0 | 0 |
| dev | noise_db | 20 | 11.4166 | 11.2311 | -0.1855 | 0 | 0 | 1 |
| dev | ild_db | 21 | 5.0983 | 5.0982 | -0.0001 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2588 | 0.2588 | -0.0000 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.7290 | 4.7289 | -0.0001 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 12.9504 | 12.8442 | -0.1062 | 0 | 0 | 0 |
| dev | level_db | 21 | 2.8479 | 2.8480 | 0.0001 | 0 | 0 | 0 |
| train | partial_db | 137 | 8.6457 | 8.6553 | 0.0096 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 4.0827 | 4.0195 | -0.0632 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 5.1041 | 5.1182 | 0.0141 | 0 | 0 | 2 |
| train | attack_db | 137 | 9.1115 | 8.8863 | -0.2253 | 0 | 0 | 0 |
| train | early_db | 137 | 11.1990 | 10.8594 | -0.3396 | 0 | 0 | 0 |
| train | sustain_db | 137 | 11.3650 | 11.3197 | -0.0453 | 0 | 0 | 0 |
| train | noise_db | 134 | 11.7384 | 11.4122 | -0.3262 | 0 | 0 | 3 |
| train | ild_db | 135 | 6.6880 | 6.6850 | -0.0031 | 0 | 0 | 2 |
| train | icc | 135 | 0.2525 | 0.2523 | -0.0002 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.4221 | 4.4192 | -0.0029 | 0 | 0 | 0 |
| train | rise_ms | 137 | 16.5698 | 16.5690 | -0.0008 | 0 | 0 | 0 |
| train | level_db | 137 | 4.2875 | 4.2874 | -0.0001 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 59 | dev | decay_db_s | 1 | 6.0012 | 7.5863 | 1.5851 |
| 50 | train | noise_db | 3 | 7.0152 | 7.5466 | 0.5314 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
