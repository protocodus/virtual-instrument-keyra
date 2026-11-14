# Recording benchmark: candidate 2.14.0 against shipping 2.13.1

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## shipping 2.13.1

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

## candidate 2.14.0

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

## Independent-sample regressions (legacy)

Every note and role where candidate 2.14.0 is worse than shipping 2.13.1 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | shipping 2.13.1 | candidate 2.14.0 |
|---|---|---|---|---|
| 59 | dev | envelope_db | 2.25 | 4.62 |
| 72 | dev | envelope_db | 4.07 | 5.78 |
| 74 | train | sustain_db | 6.56 | 8.12 |
| 59 | dev | sustain_db | 5.72 | 7.18 |
| 100 | train | ild_db | 5.00 | 6.25 |
| 50 | train | envelope_db | 3.38 | 4.58 |
| 42 | train | envelope_db | 2.85 | 4.05 |
| 76 | train | early_db | 9.16 | 10.24 |
| 70 | train | envelope_db | 3.09 | 4.09 |
| 72 | dev | ild_db | 7.71 | 8.68 |
| 59 | dev | partial_db | 9.39 | 10.31 |
| 84 | train | envelope_db | 7.41 | 8.24 |
| 24 | train | tuning_cents | 8.16 | 8.97 |
| 33 | train | tuning_cents | 2.34 | 3.15 |
| 94 | train | ild_db | 5.31 | 6.07 |
| 68 | train | ild_db | 4.32 | 5.06 |
| 68 | train | envelope_db | 4.46 | 5.20 |
| 84 | train | sustain_db | 12.92 | 13.61 |
| 72 | dev | sustain_db | 9.04 | 9.73 |
| 48 | train | rise_ms | 37.84 | 39.20 |
| 74 | train | partial_db | 5.90 | 6.57 |
| 76 | train | attack_db | 8.27 | 8.91 |
| 42 | train | attack_db | 7.54 | 8.17 |
| 88 | dev | ild_db | 3.54 | 4.17 |
| 60 | train | noise_db | 6.58 | 7.19 |
| 76 | train | noise_db | 6.84 | 7.38 |
| 72 | dev | tuning_cents | 2.97 | 3.49 |
| 42 | train | noise_db | 13.31 | 13.82 |
| 42 | train | decay_db_s | 2.72 | 3.73 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.3653 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 7.2686 | 7.1832 | -0.0855 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 3.3869 | 3.5723 | 0.1854 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 4.6477 | 4.8084 | 0.1606 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.7115 | 7.7081 | -0.0035 | 0 | 0 | 0 |
| dev | early_db | 21 | 9.0951 | 8.9973 | -0.0978 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 9.8773 | 9.9014 | 0.0241 | 0 | 0 | 0 |
| dev | noise_db | 21 | 8.7542 | 8.6826 | -0.0716 | 0 | 0 | 0 |
| dev | ild_db | 21 | 5.9421 | 6.1680 | 0.2259 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2660 | 0.2621 | -0.0038 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.1321 | 4.6219 | 0.4899 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 9.1488 | 9.1448 | -0.0040 | 0 | 0 | 0 |
| dev | level_db | 21 | 3.1862 | 3.3751 | 0.1889 | 0 | 0 | 0 |
| train | partial_db | 137 | 7.5369 | 7.3239 | -0.2131 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 3.3346 | 3.3086 | -0.0260 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 4.3713 | 4.5577 | 0.1864 | 0 | 0 | 2 |
| train | attack_db | 137 | 7.6533 | 7.6714 | 0.0180 | 0 | 0 | 0 |
| train | early_db | 137 | 9.0879 | 9.0456 | -0.0423 | 0 | 0 | 0 |
| train | sustain_db | 137 | 10.5409 | 10.4484 | -0.0924 | 0 | 0 | 0 |
| train | noise_db | 137 | 9.8228 | 9.8623 | 0.0395 | 0 | 0 | 0 |
| train | ild_db | 135 | 6.3964 | 6.3870 | -0.0095 | 0 | 0 | 2 |
| train | icc | 135 | 0.2423 | 0.2368 | -0.0055 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.2440 | 4.2689 | 0.0249 | 0 | 0 | 0 |
| train | rise_ms | 137 | 12.8104 | 12.0534 | -0.7570 | 0 | 0 | 0 |
| train | level_db | 137 | 4.2369 | 4.2882 | 0.0513 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 59 | dev | envelope_db | 1 | 2.2459 | 4.6151 | 2.3691 |
| 72 | dev | envelope_db | 5 | 4.0698 | 5.7848 | 1.7150 |
| 74 | train | sustain_db | 5 | 6.5618 | 8.1224 | 1.5606 |
| 59 | dev | sustain_db | 1 | 5.7170 | 7.1762 | 1.4592 |
| 100 | train | ild_db | 3 | 5.0033 | 6.2466 | 1.2433 |
| 50 | train | envelope_db | 5 | 3.3827 | 4.5832 | 1.2005 |
| 42 | train | envelope_db | 5 | 2.8537 | 4.0503 | 1.1966 |
| 76 | train | early_db | 5 | 9.1562 | 10.2422 | 1.0859 |
| 70 | train | envelope_db | 5 | 3.0856 | 4.0929 | 1.0073 |
| 72 | dev | ild_db | 5 | 7.7078 | 8.6815 | 0.9737 |
| 59 | dev | partial_db | 1 | 9.3886 | 10.3071 | 0.9185 |
| 84 | train | envelope_db | 5 | 7.4139 | 8.2427 | 0.8288 |
| 24 | train | tuning_cents | 5 | 8.1574 | 8.9662 | 0.8088 |
| 33 | train | tuning_cents | 5 | 2.3407 | 3.1464 | 0.8057 |
| 94 | train | ild_db | 5 | 5.3106 | 6.0708 | 0.7602 |
| 68 | train | ild_db | 5 | 4.3177 | 5.0636 | 0.7460 |
| 68 | train | envelope_db | 5 | 4.4585 | 5.2039 | 0.7453 |
| 84 | train | sustain_db | 5 | 12.9171 | 13.6117 | 0.6946 |
| 72 | dev | sustain_db | 5 | 9.0426 | 9.7266 | 0.6840 |
| 48 | train | rise_ms | 5 | 37.8417 | 39.1958 | 1.3542 |
| 74 | train | partial_db | 5 | 5.9042 | 6.5687 | 0.6645 |
| 76 | train | attack_db | 5 | 8.2665 | 8.9147 | 0.6482 |
| 42 | train | attack_db | 5 | 7.5361 | 8.1715 | 0.6354 |
| 88 | dev | ild_db | 5 | 3.5363 | 4.1700 | 0.6337 |
| 60 | train | noise_db | 5 | 6.5845 | 7.1916 | 0.6071 |
| 76 | train | noise_db | 5 | 6.8401 | 7.3842 | 0.5441 |
| 72 | dev | tuning_cents | 5 | 2.9737 | 3.4874 | 0.5137 |
| 42 | train | noise_db | 5 | 13.3057 | 13.8158 | 0.5101 |
| 42 | train | decay_db_s | 5 | 2.7152 | 3.7252 | 1.0099 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
