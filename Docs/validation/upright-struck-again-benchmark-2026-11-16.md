# Recording benchmark: 2.19.0 against 2.18.1

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.18.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.29 | 3.22 | 4.62 | 7.69 | 9.13 | 10.44 | 10.15 | 6.56 | 0.24 | 4.25 | 11.83 | 4.31 |
| dev (21) | 7.24 | 3.71 | 5.00 | 7.52 | 8.95 | 9.89 | 8.73 | 6.49 | 0.27 | 4.64 | 9.11 | 3.26 |
| train / bass A0-B2 (30) | 9.57 | 4.85 | 4.45 | 8.60 | 9.37 | 10.34 | 15.58 | 6.48 | 0.19 | 2.89 | 6.82 | 3.67 |
| train / middle C3-B5 (69) | 7.07 | 2.73 | 4.44 | 7.42 | 8.22 | 8.20 | 8.99 | 6.29 | 0.20 | 3.77 | 18.08 | 4.72 |
| train / treble C6-C8 (38) | 5.87 | 2.83 | 5.11 | 7.46 | 10.59 | 14.60 | 7.98 | 7.13 | 0.37 | 6.20 | 4.45 | 4.08 |
| dev / bass A0-B2 (5) | 9.66 | 3.40 | 2.93 | 8.97 | 10.01 | 10.42 | 12.68 | 4.56 | 0.30 | 2.10 | 1.99 | 2.43 |
| dev / middle C3-B5 (11) | 6.26 | 2.38 | 4.63 | 6.78 | 7.38 | 8.04 | 7.08 | 7.64 | 0.22 | 4.76 | 14.56 | 3.62 |
| dev / treble C6-C8 (5) | 6.98 | 6.94 | 7.89 | 7.72 | 11.33 | 13.44 | 8.39 | 5.90 | 0.35 | 6.89 | 4.22 | 3.27 |

## 2.19.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.28 | 3.22 | 4.62 | 7.69 | 9.13 | 10.44 | 10.15 | 6.56 | 0.24 | 4.25 | 11.83 | 4.31 |
| dev (21) | 7.24 | 3.71 | 5.00 | 7.52 | 8.95 | 9.89 | 8.73 | 6.49 | 0.27 | 4.64 | 9.11 | 3.26 |
| train / bass A0-B2 (30) | 9.57 | 4.85 | 4.45 | 8.60 | 9.37 | 10.34 | 15.58 | 6.48 | 0.19 | 2.89 | 6.82 | 3.67 |
| train / middle C3-B5 (69) | 7.07 | 2.73 | 4.44 | 7.42 | 8.22 | 8.20 | 8.99 | 6.29 | 0.20 | 3.77 | 18.08 | 4.72 |
| train / treble C6-C8 (38) | 5.87 | 2.83 | 5.11 | 7.46 | 10.59 | 14.60 | 7.98 | 7.13 | 0.37 | 6.20 | 4.45 | 4.08 |
| dev / bass A0-B2 (5) | 9.66 | 3.40 | 2.93 | 8.97 | 10.01 | 10.42 | 12.68 | 4.56 | 0.30 | 2.10 | 1.99 | 2.43 |
| dev / middle C3-B5 (11) | 6.26 | 2.38 | 4.63 | 6.78 | 7.38 | 8.04 | 7.08 | 7.64 | 0.22 | 4.76 | 14.56 | 3.62 |
| dev / treble C6-C8 (5) | 6.98 | 6.94 | 7.89 | 7.72 | 11.33 | 13.44 | 8.39 | 5.90 | 0.35 | 6.89 | 4.22 | 3.27 |

## Independent-sample regressions (legacy)

Every note and role where 2.19.0 is worse than 2.18.1 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.7492 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 7.2422 | 7.2422 | 0.0000 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 3.7067 | 3.7067 | 0.0000 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 5.0003 | 5.0003 | 0.0000 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.5244 | 7.5244 | -0.0000 | 0 | 0 | 0 |
| dev | early_db | 21 | 8.9479 | 8.9479 | -0.0000 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 9.8940 | 9.8940 | 0.0000 | 0 | 0 | 0 |
| dev | noise_db | 21 | 8.7274 | 8.7274 | 0.0000 | 0 | 0 | 0 |
| dev | ild_db | 21 | 6.4889 | 6.4889 | 0.0000 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2731 | 0.2731 | 0.0000 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.6365 | 4.6365 | 0.0000 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 9.1071 | 9.1071 | 0.0000 | 0 | 0 | 0 |
| dev | level_db | 21 | 3.2578 | 3.2578 | -0.0000 | 0 | 0 | 0 |
| train | partial_db | 137 | 7.2855 | 7.2847 | -0.0008 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 3.2199 | 3.2197 | -0.0002 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 4.6226 | 4.6223 | -0.0003 | 0 | 0 | 2 |
| train | attack_db | 137 | 7.6861 | 7.6861 | 0.0000 | 0 | 0 | 0 |
| train | early_db | 137 | 9.1282 | 9.1282 | 0.0000 | 0 | 0 | 0 |
| train | sustain_db | 137 | 10.4434 | 10.4434 | 0.0000 | 0 | 0 | 0 |
| train | noise_db | 137 | 10.1537 | 10.1537 | -0.0000 | 0 | 0 | 0 |
| train | ild_db | 135 | 6.5574 | 6.5574 | 0.0000 | 0 | 0 | 2 |
| train | icc | 135 | 0.2424 | 0.2424 | -0.0000 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.2511 | 4.2511 | 0.0000 | 0 | 0 | 0 |
| train | rise_ms | 137 | 11.8324 | 11.8324 | 0.0000 | 0 | 0 | 0 |
| train | level_db | 137 | 4.3138 | 4.3138 | 0.0000 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
