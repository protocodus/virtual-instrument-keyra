# Recording benchmark: 2.18.1 against 2.18.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.18.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 7.89 | 2.23 | 4.00 | 6.61 | 6.54 | 8.69 | 7.37 | 5.02 | 0.20 | 4.23 | 14.25 | 2.48 |
| dev (156) | 7.35 | 2.56 | 3.41 | 6.34 | 6.03 | 7.76 | 7.05 | 5.02 | 0.18 | 3.92 | 12.23 | 2.66 |
| train / bass A0-B2 (84) | 8.76 | 2.94 | 2.67 | 5.73 | 5.41 | 6.35 | 6.52 | 4.36 | 0.20 | 3.52 | 26.52 | 1.96 |
| train / middle C3-B5 (108) | 7.26 | 1.26 | 3.89 | 6.11 | 6.28 | 7.93 | 7.23 | 6.58 | 0.20 | 3.91 | 10.36 | 2.16 |
| train / treble C6-C8 (84) | 7.83 | 2.78 | 5.56 | 8.13 | 8.01 | 11.99 | 8.37 | 3.59 | 0.19 | 5.34 | 6.98 | 3.43 |
| dev / bass A0-B2 (44) | 9.06 | 3.64 | 2.52 | 5.33 | 4.86 | 5.67 | 6.44 | 4.52 | 0.18 | 3.16 | 22.78 | 2.60 |
| dev / middle C3-B5 (68) | 6.95 | 1.20 | 3.53 | 6.21 | 5.89 | 7.20 | 6.92 | 6.77 | 0.15 | 3.70 | 10.12 | 2.18 |
| dev / treble C6-C8 (44) | 6.25 | 3.57 | 4.12 | 7.54 | 7.41 | 10.70 | 7.83 | 2.71 | 0.22 | 5.03 | 4.93 | 3.45 |

## 2.18.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 7.89 | 2.23 | 4.00 | 6.61 | 6.54 | 8.69 | 7.37 | 5.02 | 0.20 | 4.23 | 14.25 | 2.48 |
| dev (156) | 7.35 | 2.56 | 3.41 | 6.34 | 6.03 | 7.76 | 7.05 | 5.02 | 0.18 | 3.92 | 12.23 | 2.66 |
| train / bass A0-B2 (84) | 8.76 | 2.94 | 2.67 | 5.73 | 5.41 | 6.35 | 6.52 | 4.36 | 0.20 | 3.52 | 26.52 | 1.96 |
| train / middle C3-B5 (108) | 7.26 | 1.26 | 3.89 | 6.11 | 6.28 | 7.93 | 7.23 | 6.58 | 0.20 | 3.91 | 10.36 | 2.16 |
| train / treble C6-C8 (84) | 7.83 | 2.78 | 5.56 | 8.13 | 8.01 | 11.99 | 8.37 | 3.59 | 0.19 | 5.34 | 6.98 | 3.43 |
| dev / bass A0-B2 (44) | 9.06 | 3.64 | 2.52 | 5.33 | 4.86 | 5.67 | 6.44 | 4.52 | 0.18 | 3.16 | 22.78 | 2.60 |
| dev / middle C3-B5 (68) | 6.95 | 1.20 | 3.53 | 6.21 | 5.89 | 7.20 | 6.92 | 6.77 | 0.15 | 3.70 | 10.12 | 2.18 |
| dev / treble C6-C8 (44) | 6.25 | 3.57 | 4.12 | 7.54 | 7.41 | 10.70 | 7.83 | 2.71 | 0.22 | 5.03 | 4.93 | 3.45 |

## Independent-sample regressions (legacy)

Every note and role where 2.18.1 is worse than 2.18.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.5156 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 7.3458 | 7.3458 | -0.0000 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.5577 | 2.5577 | -0.0000 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 3.4084 | 3.4085 | 0.0000 | 0 | 0 | 1 |
| dev | attack_db | 156 | 6.3377 | 6.3377 | 0.0000 | 0 | 0 | 0 |
| dev | early_db | 156 | 6.0298 | 6.0298 | -0.0000 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 7.7566 | 7.7566 | -0.0000 | 0 | 0 | 0 |
| dev | noise_db | 153 | 7.0463 | 7.0467 | 0.0004 | 0 | 0 | 3 |
| dev | ild_db | 154 | 5.0202 | 5.0202 | 0.0000 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1788 | 0.1788 | -0.0000 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 3.9212 | 3.9212 | -0.0000 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 12.2277 | 12.2277 | 0.0000 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.6569 | 2.6569 | 0.0000 | 0 | 0 | 0 |
| train | partial_db | 276 | 7.8908 | 7.8909 | 0.0001 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.2348 | 2.2348 | 0.0000 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 3.9990 | 3.9990 | -0.0000 | 0 | 0 | 5 |
| train | attack_db | 276 | 6.6071 | 6.6071 | -0.0000 | 0 | 0 | 0 |
| train | early_db | 276 | 6.5431 | 6.5431 | -0.0000 | 0 | 0 | 0 |
| train | sustain_db | 276 | 8.6864 | 8.6864 | -0.0000 | 0 | 0 | 0 |
| train | noise_db | 273 | 7.3682 | 7.3696 | 0.0014 | 0 | 0 | 3 |
| train | ild_db | 270 | 5.0250 | 5.0250 | 0.0000 | 0 | 0 | 6 |
| train | icc | 270 | 0.1962 | 0.1962 | -0.0000 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.2257 | 4.2257 | -0.0000 | 0 | 0 | 0 |
| train | rise_ms | 276 | 14.2489 | 14.2489 | 0.0000 | 0 | 0 | 0 |
| train | level_db | 276 | 2.4838 | 2.4839 | 0.0000 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
