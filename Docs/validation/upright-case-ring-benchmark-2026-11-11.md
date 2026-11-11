# Recording benchmark: 2.6.0 against 2.5.0

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.5.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 8.04 | 3.40 | 4.83 | 7.57 | 9.69 | 10.87 | 10.10 | 6.46 | 0.25 | 4.16 | 15.54 | 4.37 |
| dev (21) | 8.42 | 3.17 | 5.33 | 7.56 | 9.27 | 10.42 | 9.54 | 5.13 | 0.26 | 4.35 | 12.78 | 3.03 |
| train / bass A0-B2 (30) | 10.36 | 4.50 | 5.06 | 7.90 | 9.66 | 10.30 | 15.42 | 5.98 | 0.23 | 3.20 | 21.52 | 3.61 |
| train / middle C3-B5 (69) | 7.62 | 3.07 | 4.24 | 7.42 | 8.56 | 8.92 | 8.73 | 6.50 | 0.20 | 3.91 | 18.73 | 4.75 |
| train / treble C6-C8 (38) | 6.96 | 3.13 | 5.76 | 7.56 | 11.75 | 14.87 | 8.40 | 6.79 | 0.37 | 5.37 | 5.04 | 4.28 |
| dev / bass A0-B2 (5) | 9.87 | 4.49 | 4.06 | 8.34 | 9.86 | 9.80 | 15.71 | 4.48 | 0.27 | 2.39 | 24.50 | 1.96 |
| dev / middle C3-B5 (11) | 6.84 | 1.99 | 4.78 | 6.92 | 7.87 | 8.70 | 7.51 | 6.53 | 0.20 | 4.08 | 10.71 | 3.48 |
| dev / treble C6-C8 (5) | 10.46 | 4.43 | 7.80 | 8.21 | 11.78 | 14.84 | 9.06 | 2.70 | 0.37 | 6.91 | 5.61 | 3.12 |

## 2.6.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 8.03 | 3.41 | 4.83 | 7.44 | 9.39 | 10.84 | 9.86 | 6.39 | 0.25 | 4.16 | 15.55 | 4.36 |
| dev (21) | 8.55 | 3.09 | 5.33 | 7.42 | 8.95 | 10.42 | 9.22 | 5.07 | 0.26 | 4.35 | 12.77 | 3.03 |
| train / bass A0-B2 (30) | 10.36 | 4.50 | 5.06 | 7.90 | 9.66 | 10.30 | 15.42 | 5.98 | 0.23 | 3.20 | 21.52 | 3.61 |
| train / middle C3-B5 (69) | 7.62 | 3.07 | 4.24 | 7.42 | 8.54 | 8.92 | 8.70 | 6.49 | 0.20 | 3.91 | 18.73 | 4.75 |
| train / treble C6-C8 (38) | 6.93 | 3.16 | 5.76 | 7.12 | 10.73 | 14.77 | 7.57 | 6.52 | 0.36 | 5.37 | 5.05 | 4.25 |
| dev / bass A0-B2 (5) | 9.87 | 4.49 | 4.06 | 8.34 | 9.86 | 9.80 | 15.71 | 4.48 | 0.27 | 2.39 | 24.50 | 1.96 |
| dev / middle C3-B5 (11) | 6.84 | 1.99 | 4.78 | 6.92 | 7.87 | 8.70 | 7.51 | 6.53 | 0.20 | 4.08 | 10.71 | 3.48 |
| dev / treble C6-C8 (5) | 10.98 | 4.10 | 7.80 | 7.61 | 10.44 | 14.81 | 7.77 | 2.48 | 0.36 | 6.91 | 5.59 | 3.12 |

## Independent-sample regressions (legacy)

Every note and role where 2.6.0 is worse than 2.5.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.5.0 | 2.6.0 |
|---|---|---|---|---|
| 88 | dev | partial_db | 10.46 | 10.98 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (11.7179 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 8.4234 | 8.5470 | 0.1235 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 3.1685 | 3.0889 | -0.0796 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 5.3296 | 5.3296 | 0.0000 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.5644 | 7.4227 | -0.1417 | 0 | 0 | 0 |
| dev | early_db | 21 | 9.2725 | 8.9549 | -0.3176 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 10.4220 | 10.4154 | -0.0066 | 0 | 0 | 0 |
| dev | noise_db | 20 | 9.5423 | 9.2198 | -0.3226 | 0 | 0 | 1 |
| dev | ild_db | 21 | 5.1280 | 5.0746 | -0.0534 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2593 | 0.2567 | -0.0026 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.3506 | 4.3508 | 0.0002 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 12.7808 | 12.7748 | -0.0060 | 0 | 0 | 0 |
| dev | level_db | 21 | 3.0312 | 3.0316 | 0.0004 | 0 | 0 | 0 |
| train | partial_db | 137 | 8.0376 | 8.0298 | -0.0078 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 3.3986 | 3.4069 | 0.0084 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 4.8302 | 4.8299 | -0.0002 | 0 | 0 | 2 |
| train | attack_db | 137 | 7.5656 | 7.4402 | -0.1254 | 0 | 0 | 0 |
| train | early_db | 137 | 9.6880 | 9.3924 | -0.2956 | 0 | 0 | 0 |
| train | sustain_db | 137 | 10.8692 | 10.8416 | -0.0276 | 0 | 0 | 0 |
| train | noise_db | 137 | 10.1039 | 9.8582 | -0.2457 | 0 | 0 | 0 |
| train | ild_db | 135 | 6.4612 | 6.3871 | -0.0742 | 0 | 0 | 2 |
| train | icc | 135 | 0.2516 | 0.2488 | -0.0028 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.1589 | 4.1594 | 0.0005 | 0 | 0 | 0 |
| train | rise_ms | 137 | 15.5435 | 15.5471 | 0.0036 | 0 | 0 | 0 |
| train | level_db | 137 | 4.3710 | 4.3637 | -0.0073 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 88 | dev | partial_db | 5 | 10.4613 | 10.9801 | 0.5188 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
