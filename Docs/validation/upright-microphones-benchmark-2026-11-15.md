# Recording benchmark: candidate 2.15.0 against shipping 2.14.0

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## shipping 2.14.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.32 | 3.31 | 4.56 | 7.67 | 9.05 | 10.45 | 9.86 | 6.39 | 0.24 | 4.27 | 12.05 | 4.29 |
| dev (21) | 7.18 | 3.57 | 4.81 | 7.71 | 9.00 | 9.90 | 8.68 | 6.17 | 0.26 | 4.62 | 9.14 | 3.35 |
| train / bass A0-B2 (30) | 9.53 | 4.92 | 4.33 | 8.52 | 9.27 | 10.36 | 15.28 | 6.72 | 0.19 | 3.01 | 6.53 | 3.67 |
| train / middle C3-B5 (69) | 7.22 | 2.81 | 4.34 | 7.47 | 8.19 | 8.15 | 8.79 | 6.05 | 0.19 | 3.76 | 18.65 | 4.71 |
| train / treble C6-C8 (38) | 5.77 | 2.95 | 5.16 | 7.37 | 10.41 | 14.68 | 7.53 | 6.74 | 0.36 | 6.19 | 4.43 | 4.02 |
| dev / bass A0-B2 (5) | 9.08 | 3.49 | 2.76 | 9.09 | 9.97 | 10.38 | 12.92 | 3.98 | 0.28 | 2.09 | 2.08 | 2.41 |
| dev / middle C3-B5 (11) | 6.32 | 2.50 | 4.38 | 7.00 | 7.60 | 8.08 | 7.12 | 8.07 | 0.21 | 4.77 | 14.59 | 3.73 |
| dev / treble C6-C8 (5) | 7.18 | 6.02 | 7.81 | 7.89 | 11.09 | 13.43 | 7.87 | 4.17 | 0.35 | 6.83 | 4.23 | 3.43 |

## candidate 2.15.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.31 | 3.28 | 4.58 | 7.60 | 9.04 | 10.45 | 9.88 | 6.39 | 0.24 | 4.27 | 12.15 | 4.29 |
| dev (21) | 7.20 | 3.57 | 4.85 | 7.62 | 8.99 | 9.90 | 8.66 | 6.17 | 0.26 | 4.62 | 9.13 | 3.34 |
| train / bass A0-B2 (30) | 9.43 | 4.82 | 4.39 | 8.49 | 9.27 | 10.36 | 15.43 | 6.72 | 0.19 | 3.00 | 6.53 | 3.67 |
| train / middle C3-B5 (69) | 7.25 | 2.79 | 4.36 | 7.39 | 8.19 | 8.15 | 8.77 | 6.05 | 0.19 | 3.76 | 18.85 | 4.71 |
| train / treble C6-C8 (38) | 5.76 | 2.95 | 5.16 | 7.28 | 10.40 | 14.68 | 7.52 | 6.74 | 0.36 | 6.19 | 4.43 | 4.01 |
| dev / bass A0-B2 (5) | 9.17 | 3.50 | 2.90 | 9.08 | 9.97 | 10.38 | 12.94 | 3.98 | 0.28 | 2.07 | 2.00 | 2.41 |
| dev / middle C3-B5 (11) | 6.32 | 2.49 | 4.38 | 6.90 | 7.59 | 8.08 | 7.08 | 8.07 | 0.21 | 4.77 | 14.60 | 3.73 |
| dev / treble C6-C8 (5) | 7.18 | 6.02 | 7.81 | 7.74 | 11.09 | 13.43 | 7.85 | 4.17 | 0.35 | 6.83 | 4.23 | 3.43 |

## Independent-sample regressions (legacy)

Every note and role where candidate 2.15.0 is worse than shipping 2.14.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | shipping 2.14.0 | candidate 2.15.0 |
|---|---|---|---|---|
| 50 | train | rise_ms | 68.80 | 72.02 |
| 36 | train | noise_db | 10.65 | 11.54 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.5167 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 7.1832 | 7.2030 | 0.0199 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 3.5723 | 3.5700 | -0.0023 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 4.8084 | 4.8459 | 0.0375 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.7081 | 7.6183 | -0.0898 | 0 | 0 | 0 |
| dev | early_db | 21 | 8.9973 | 8.9903 | -0.0070 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 9.9014 | 9.9015 | 0.0001 | 0 | 0 | 0 |
| dev | noise_db | 21 | 8.6826 | 8.6569 | -0.0257 | 0 | 0 | 0 |
| dev | ild_db | 21 | 6.1680 | 6.1679 | -0.0001 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2621 | 0.2621 | 0.0000 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.6219 | 4.6185 | -0.0034 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 9.1448 | 9.1280 | -0.0169 | 0 | 0 | 0 |
| dev | level_db | 21 | 3.3452 | 3.3447 | -0.0005 | 0 | 0 | 0 |
| train | partial_db | 137 | 7.3239 | 7.3133 | -0.0105 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 3.3086 | 3.2784 | -0.0302 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 4.5577 | 4.5807 | 0.0230 | 0 | 0 | 2 |
| train | attack_db | 137 | 7.6714 | 7.6000 | -0.0713 | 0 | 0 | 0 |
| train | early_db | 137 | 9.0456 | 9.0416 | -0.0040 | 0 | 0 | 0 |
| train | sustain_db | 137 | 10.4484 | 10.4476 | -0.0008 | 0 | 0 | 0 |
| train | noise_db | 137 | 9.8623 | 9.8806 | 0.0183 | 0 | 0 | 0 |
| train | ild_db | 135 | 6.3870 | 6.3868 | -0.0002 | 0 | 0 | 2 |
| train | icc | 135 | 0.2368 | 0.2368 | -0.0001 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.2689 | 4.2680 | -0.0009 | 0 | 0 | 0 |
| train | rise_ms | 137 | 12.0534 | 12.1513 | 0.0979 | 0 | 0 | 0 |
| train | level_db | 137 | 4.2905 | 4.2902 | -0.0003 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 50 | train | rise_ms | 5 | 68.7958 | 72.0167 | 3.2208 |
| 36 | train | noise_db | 5 | 10.6459 | 11.5413 | 0.8954 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
