# Recording benchmark: 0.4.24 against 0.4.23

Every train and dev note of `Tools/corpus/split-hamburg-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.23

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (40) | 4.69 | 0.26 | 3.41 | 6.13 | 5.06 | 5.61 | 7.14 | 1.53 | 0.12 | 3.30 | 17.42 | 0.69 |
| dev (8) | 7.88 | 1.02 | 4.45 | 6.94 | 6.68 | 6.17 | 6.52 | 4.86 | 0.20 | 2.54 | 3.74 | 2.15 |
| train / bass A0-B2 (16) | 4.69 | 0.09 | 0.97 | 6.53 | 3.86 | 3.73 | 8.10 | 0.89 | 0.06 | 2.39 | 32.19 | 0.60 |
| train / middle C3-B5 (12) | 4.63 | 0.23 | 2.24 | 6.19 | 5.43 | 5.62 | 7.19 | 1.93 | 0.12 | 1.94 | 12.41 | 0.27 |
| train / treble C6-C8 (12) | 4.75 | 0.51 | 7.81 | 5.55 | 6.28 | 8.11 | 6.05 | 1.97 | 0.19 | 5.87 | 2.74 | 1.24 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.88 | 1.02 | 4.45 | 6.94 | 6.68 | 6.17 | 6.52 | 4.86 | 0.20 | 2.54 | 3.74 | 2.15 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## 0.4.24

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (40) | 4.67 | 0.26 | 3.43 | 6.13 | 5.06 | 5.60 | 7.14 | 1.53 | 0.12 | 3.29 | 17.42 | 0.69 |
| dev (8) | 7.88 | 1.02 | 4.45 | 6.94 | 6.68 | 6.17 | 6.52 | 4.86 | 0.20 | 2.54 | 3.74 | 2.15 |
| train / bass A0-B2 (16) | 4.69 | 0.09 | 0.97 | 6.53 | 3.86 | 3.73 | 8.10 | 0.89 | 0.06 | 2.39 | 32.19 | 0.60 |
| train / middle C3-B5 (12) | 4.63 | 0.23 | 2.24 | 6.19 | 5.43 | 5.62 | 7.19 | 1.93 | 0.12 | 1.94 | 12.41 | 0.27 |
| train / treble C6-C8 (12) | 4.69 | 0.51 | 7.88 | 5.55 | 6.28 | 8.08 | 6.05 | 1.97 | 0.19 | 5.83 | 2.74 | 1.24 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.88 | 1.02 | 4.45 | 6.94 | 6.68 | 6.17 | 6.52 | 4.86 | 0.20 | 2.54 | 3.74 | 2.15 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## Independent-sample regressions (legacy)

Every note and role where 0.4.24 is worse than 0.4.23 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (14.5631 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 8 | 7.8846 | 7.8846 | 0.0000 | 0 | 0 | 0 |
| dev | tuning_cents | 8 | 1.0239 | 1.0239 | 0.0000 | 0 | 0 | 0 |
| dev | decay_db_s | 8 | 4.4461 | 4.4461 | 0.0000 | 0 | 0 | 0 |
| dev | attack_db | 8 | 6.9444 | 6.9444 | 0.0000 | 0 | 0 | 0 |
| dev | early_db | 8 | 6.6789 | 6.6789 | 0.0000 | 0 | 0 | 0 |
| dev | sustain_db | 8 | 6.1727 | 6.1727 | 0.0000 | 0 | 0 | 0 |
| dev | noise_db | 6 | 6.5164 | 6.5164 | 0.0000 | 0 | 0 | 2 |
| dev | ild_db | 8 | 4.8605 | 4.8605 | 0.0000 | 0 | 0 | 0 |
| dev | icc | 8 | 0.1999 | 0.1999 | 0.0000 | 0 | 0 | 0 |
| dev | envelope_db | 8 | 2.5367 | 2.5367 | 0.0000 | 0 | 0 | 0 |
| dev | rise_ms | 8 | 3.7370 | 3.7370 | 0.0000 | 0 | 0 | 0 |
| dev | level_db | 8 | 2.1456 | 2.1456 | 0.0000 | 0 | 0 | 0 |
| train | partial_db | 40 | 4.6906 | 4.6717 | -0.0189 | 0 | 0 | 0 |
| train | tuning_cents | 40 | 0.2594 | 0.2594 | -0.0000 | 0 | 0 | 0 |
| train | decay_db_s | 40 | 3.4052 | 3.4259 | 0.0207 | 0 | 0 | 0 |
| train | attack_db | 40 | 6.1338 | 6.1338 | -0.0000 | 0 | 0 | 0 |
| train | early_db | 40 | 5.0574 | 5.0571 | -0.0003 | 0 | 0 | 0 |
| train | sustain_db | 40 | 5.6130 | 5.6031 | -0.0099 | 0 | 0 | 0 |
| train | noise_db | 37 | 7.1439 | 7.1438 | -0.0001 | 0 | 0 | 3 |
| train | ild_db | 40 | 1.5255 | 1.5252 | -0.0003 | 0 | 0 | 0 |
| train | icc | 40 | 0.1157 | 0.1157 | -0.0000 | 0 | 0 | 0 |
| train | envelope_db | 40 | 3.3023 | 3.2889 | -0.0134 | 0 | 0 | 0 |
| train | rise_ms | 40 | 17.4214 | 17.4208 | -0.0005 | 0 | 0 | 0 |
| train | level_db | 40 | 0.6924 | 0.6923 | -0.0001 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
