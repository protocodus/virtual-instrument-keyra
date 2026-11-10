# Recording benchmark: 0.4.33 against 0.4.32

Every train and dev note of `Tools/corpus/split-newyork-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.32

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (61) | 7.36 | 0.46 | 3.70 | 5.87 | 6.32 | 6.98 | 6.45 | 2.43 | 0.09 | 2.55 | 11.76 | 1.45 |
| dev (17) | 10.40 | 1.84 | 7.09 | 8.02 | 8.03 | 9.40 | 8.07 | 6.04 | 0.22 | 5.07 | 7.84 | 5.51 |
| train / bass A0-B2 (20) | 8.97 | 0.36 | 1.84 | 6.41 | 6.62 | 6.92 | 7.50 | 1.63 | 0.08 | 2.30 | 13.71 | 1.33 |
| train / middle C3-B5 (24) | 8.03 | 0.26 | 4.14 | 5.55 | 6.40 | 6.80 | 5.73 | 2.57 | 0.11 | 2.60 | 15.74 | 1.10 |
| train / treble C6-C8 (17) | 4.36 | 0.89 | 6.36 | 5.70 | 5.87 | 7.34 | 6.24 | 3.70 | 0.07 | 2.78 | 3.86 | 2.09 |
| dev / bass A0-B2 (5) | 10.57 | 2.18 | 2.73 | 6.69 | 7.96 | 9.02 | 8.67 | 3.93 | 0.13 | 4.19 | 8.81 | 3.85 |
| dev / middle C3-B5 (5) | 9.54 | 0.98 | 4.25 | 7.19 | 7.20 | 9.62 | 6.51 | 5.23 | 0.21 | 4.71 | 8.55 | 3.93 |
| dev / treble C6-C8 (7) | 10.90 | 2.21 | 12.23 | 9.57 | 8.67 | 9.51 | 8.77 | 8.12 | 0.29 | 5.96 | 6.63 | 7.82 |

## 0.4.33

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (61) | 7.36 | 0.46 | 3.70 | 5.87 | 6.32 | 6.98 | 6.45 | 2.43 | 0.09 | 2.55 | 11.76 | 1.45 |
| dev (17) | 10.47 | 1.81 | 7.09 | 8.00 | 8.00 | 9.40 | 7.95 | 6.04 | 0.22 | 5.07 | 7.84 | 5.51 |
| train / bass A0-B2 (20) | 8.97 | 0.36 | 1.84 | 6.41 | 6.62 | 6.92 | 7.50 | 1.63 | 0.08 | 2.30 | 13.71 | 1.33 |
| train / middle C3-B5 (24) | 8.03 | 0.26 | 4.14 | 5.55 | 6.40 | 6.80 | 5.73 | 2.57 | 0.11 | 2.60 | 15.74 | 1.10 |
| train / treble C6-C8 (17) | 4.36 | 0.89 | 6.36 | 5.70 | 5.87 | 7.34 | 6.24 | 3.70 | 0.07 | 2.78 | 3.86 | 2.09 |
| dev / bass A0-B2 (5) | 10.56 | 2.18 | 2.73 | 6.63 | 7.92 | 9.02 | 8.74 | 3.93 | 0.13 | 4.19 | 8.81 | 3.85 |
| dev / middle C3-B5 (5) | 9.54 | 0.98 | 4.25 | 7.16 | 7.14 | 9.62 | 6.00 | 5.23 | 0.21 | 4.71 | 8.55 | 3.93 |
| dev / treble C6-C8 (7) | 11.08 | 2.14 | 12.23 | 9.57 | 8.67 | 9.51 | 8.77 | 8.12 | 0.29 | 5.96 | 6.63 | 7.82 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.33 is worse than 0.4.32 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (25.4567 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 17 | 10.4045 | 10.4716 | 0.0671 | 0 | 0 | 0 |
| dev | tuning_cents | 17 | 1.8392 | 1.8125 | -0.0267 | 0 | 0 | 0 |
| dev | decay_db_s | 17 | 7.0893 | 7.0893 | 0.0000 | 0 | 0 | 0 |
| dev | attack_db | 17 | 8.0231 | 7.9978 | -0.0253 | 0 | 0 | 0 |
| dev | early_db | 17 | 8.0272 | 7.9996 | -0.0276 | 0 | 0 | 0 |
| dev | sustain_db | 17 | 9.3996 | 9.4006 | 0.0010 | 0 | 0 | 0 |
| dev | noise_db | 17 | 8.0750 | 7.9481 | -0.1268 | 0 | 0 | 0 |
| dev | ild_db | 17 | 6.0378 | 6.0379 | 0.0001 | 0 | 0 | 0 |
| dev | icc | 17 | 0.2201 | 0.2200 | -0.0001 | 0 | 0 | 0 |
| dev | envelope_db | 17 | 5.0723 | 5.0724 | 0.0001 | 0 | 0 | 0 |
| dev | rise_ms | 17 | 7.8354 | 7.8354 | 0.0000 | 0 | 0 | 0 |
| dev | level_db | 17 | 5.5077 | 5.5076 | -0.0001 | 0 | 0 | 0 |
| train | partial_db | 60 | 7.3640 | 7.3639 | -0.0000 | 0 | 0 | 1 |
| train | tuning_cents | 60 | 0.4608 | 0.4608 | -0.0000 | 0 | 0 | 1 |
| train | decay_db_s | 54 | 3.6999 | 3.6999 | 0.0000 | 0 | 0 | 7 |
| train | attack_db | 61 | 5.8719 | 5.8719 | -0.0000 | 0 | 0 | 0 |
| train | early_db | 61 | 6.3243 | 6.3243 | -0.0000 | 0 | 0 | 0 |
| train | sustain_db | 60 | 6.9810 | 6.9810 | -0.0000 | 0 | 0 | 1 |
| train | noise_db | 61 | 6.4531 | 6.4531 | -0.0000 | 0 | 0 | 0 |
| train | ild_db | 54 | 2.4283 | 2.4283 | 0.0000 | 0 | 0 | 7 |
| train | icc | 54 | 0.0930 | 0.0930 | -0.0000 | 0 | 0 | 7 |
| train | envelope_db | 61 | 2.5544 | 2.5544 | 0.0000 | 0 | 0 | 0 |
| train | rise_ms | 61 | 11.7631 | 11.7631 | 0.0000 | 0 | 0 | 0 |
| train | level_db | 61 | 1.4481 | 1.4481 | 0.0001 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
