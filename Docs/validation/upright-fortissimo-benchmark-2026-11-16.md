# Recording benchmark: 2.21.0 against 2.20.0

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.20.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.30 | 3.23 | 4.60 | 7.78 | 9.25 | 10.46 | 10.68 | 6.55 | 0.24 | 4.25 | 11.80 | 4.31 |
| dev (21) | 7.19 | 3.67 | 5.05 | 7.61 | 8.99 | 9.90 | 9.35 | 6.49 | 0.27 | 4.64 | 9.10 | 3.25 |
| train / bass A0-B2 (30) | 9.71 | 4.86 | 4.35 | 8.97 | 9.90 | 10.41 | 17.55 | 6.48 | 0.19 | 2.88 | 6.79 | 3.64 |
| train / middle C3-B5 (69) | 7.04 | 2.75 | 4.44 | 7.43 | 8.22 | 8.20 | 9.18 | 6.29 | 0.20 | 3.77 | 18.02 | 4.72 |
| train / treble C6-C8 (38) | 5.88 | 2.82 | 5.12 | 7.47 | 10.60 | 14.60 | 7.98 | 7.13 | 0.37 | 6.20 | 4.45 | 4.09 |
| dev / bass A0-B2 (5) | 9.52 | 3.42 | 3.04 | 9.42 | 10.21 | 10.44 | 14.96 | 4.56 | 0.30 | 2.11 | 2.01 | 2.41 |
| dev / middle C3-B5 (11) | 6.23 | 2.40 | 4.63 | 6.77 | 7.39 | 8.04 | 7.25 | 7.63 | 0.22 | 4.77 | 14.54 | 3.63 |
| dev / treble C6-C8 (5) | 6.96 | 6.71 | 8.01 | 7.66 | 11.29 | 13.44 | 8.34 | 5.90 | 0.35 | 6.89 | 4.25 | 3.27 |

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

## Independent-sample regressions (legacy)

Every note and role where 2.21.0 is worse than 2.20.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.20.0 | 2.21.0 |
|---|---|---|---|---|
| 36 | train | noise_db | 12.87 | 14.86 |
| 45 | train | noise_db | 16.56 | 18.26 |
| 52 | train | noise_db | 9.80 | 11.44 |
| 33 | train | noise_db | 17.62 | 19.24 |
| 42 | train | noise_db | 17.05 | 18.66 |
| 48 | train | noise_db | 16.86 | 18.46 |
| 39 | dev | noise_db | 14.96 | 16.51 |
| 50 | train | noise_db | 8.66 | 9.71 |
| 88 | dev | partial_db | 6.96 | 8.00 |
| 54 | train | noise_db | 13.23 | 13.98 |
| 56 | dev | noise_db | 7.73 | 8.44 |
| 60 | train | noise_db | 7.00 | 7.61 |
| 27 | train | noise_db | 21.30 | 21.86 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.7506 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 7.1855 | 7.3603 | 0.1747 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 3.6680 | 3.6314 | -0.0366 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 5.0538 | 5.0123 | -0.0415 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.6132 | 7.6754 | 0.0623 | 0 | 0 | 0 |
| dev | early_db | 21 | 8.9921 | 9.0082 | 0.0161 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 9.8984 | 9.8809 | -0.0175 | 0 | 0 | 0 |
| dev | noise_db | 21 | 9.3480 | 9.8399 | 0.4919 | 0 | 0 | 0 |
| dev | ild_db | 21 | 6.4872 | 6.4929 | 0.0056 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2730 | 0.2727 | -0.0003 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.6388 | 4.6384 | -0.0004 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 9.1042 | 9.0784 | -0.0258 | 0 | 0 | 0 |
| dev | level_db | 21 | 3.2520 | 2.7364 | -0.5155 | 0 | 0 | 0 |
| train | partial_db | 137 | 7.3048 | 7.2749 | -0.0299 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 3.2326 | 3.1971 | -0.0355 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 4.5994 | 4.5840 | -0.0155 | 0 | 0 | 2 |
| train | attack_db | 137 | 7.7789 | 7.8461 | 0.0672 | 0 | 0 | 0 |
| train | early_db | 137 | 9.2499 | 9.3263 | 0.0764 | 0 | 0 | 0 |
| train | sustain_db | 137 | 10.4552 | 10.4813 | 0.0262 | 0 | 0 | 0 |
| train | noise_db | 137 | 10.6786 | 11.1965 | 0.5178 | 0 | 0 | 0 |
| train | ild_db | 135 | 6.5543 | 6.5534 | -0.0008 | 0 | 0 | 2 |
| train | icc | 135 | 0.2422 | 0.2420 | -0.0002 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.2478 | 4.2445 | -0.0033 | 0 | 0 | 0 |
| train | rise_ms | 137 | 11.8000 | 11.7666 | -0.0335 | 0 | 0 | 0 |
| train | level_db | 137 | 4.3080 | 3.9323 | -0.3757 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 36 | train | noise_db | 5 | 12.8699 | 14.8617 | 1.9918 |
| 45 | train | noise_db | 5 | 16.5621 | 18.2645 | 1.7024 |
| 52 | train | noise_db | 5 | 9.7992 | 11.4405 | 1.6414 |
| 33 | train | noise_db | 5 | 17.6240 | 19.2384 | 1.6145 |
| 42 | train | noise_db | 5 | 17.0502 | 18.6555 | 1.6054 |
| 48 | train | noise_db | 5 | 16.8617 | 18.4615 | 1.5998 |
| 39 | dev | noise_db | 5 | 14.9580 | 16.5101 | 1.5522 |
| 50 | train | noise_db | 5 | 8.6586 | 9.7126 | 1.0540 |
| 88 | dev | partial_db | 5 | 6.9572 | 8.0009 | 1.0437 |
| 54 | train | noise_db | 5 | 13.2309 | 13.9821 | 0.7512 |
| 56 | dev | noise_db | 5 | 7.7254 | 8.4412 | 0.7158 |
| 60 | train | noise_db | 5 | 7.0003 | 7.6065 | 0.6063 |
| 27 | train | noise_db | 5 | 21.2964 | 21.8637 | 0.5673 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
