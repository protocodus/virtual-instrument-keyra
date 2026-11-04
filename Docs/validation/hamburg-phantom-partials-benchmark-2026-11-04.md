# Recording benchmark: candidate 0.4.18 against shipping 0.4.17

Every train and dev note of `Tools/corpus/split-hamburg-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## shipping 0.4.17

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (40) | 4.69 | 0.26 | 3.42 | 6.14 | 5.07 | 5.62 | 7.18 | 1.53 | 0.12 | 3.30 | 17.42 | 0.70 |
| dev (8) | 7.87 | 0.65 | 5.04 | 6.80 | 6.75 | 7.53 | 6.72 | 4.99 | 0.19 | 4.21 | 4.04 | 1.84 |
| train / bass A0-B2 (16) | 4.69 | 0.09 | 0.97 | 6.53 | 3.86 | 3.73 | 8.13 | 0.89 | 0.06 | 2.39 | 32.18 | 0.56 |
| train / middle C3-B5 (12) | 4.63 | 0.24 | 2.25 | 6.21 | 5.48 | 5.67 | 7.27 | 1.93 | 0.12 | 1.95 | 12.40 | 0.27 |
| train / treble C6-C8 (12) | 4.75 | 0.51 | 7.84 | 5.54 | 6.27 | 8.10 | 6.04 | 1.97 | 0.19 | 5.87 | 2.74 | 1.32 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.87 | 0.65 | 5.04 | 6.80 | 6.75 | 7.53 | 6.72 | 4.99 | 0.19 | 4.21 | 4.04 | 1.84 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## candidate 0.4.18

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (40) | 4.69 | 0.26 | 3.42 | 6.14 | 5.07 | 5.62 | 7.16 | 1.53 | 0.12 | 3.30 | 17.42 | 0.70 |
| dev (8) | 7.87 | 0.65 | 5.04 | 6.82 | 6.75 | 7.53 | 6.71 | 4.98 | 0.19 | 4.21 | 4.07 | 1.84 |
| train / bass A0-B2 (16) | 4.69 | 0.09 | 0.97 | 6.53 | 3.86 | 3.73 | 8.13 | 0.89 | 0.06 | 2.39 | 32.18 | 0.56 |
| train / middle C3-B5 (12) | 4.63 | 0.24 | 2.25 | 6.21 | 5.48 | 5.67 | 7.24 | 1.93 | 0.12 | 1.95 | 12.41 | 0.27 |
| train / treble C6-C8 (12) | 4.75 | 0.51 | 7.84 | 5.54 | 6.27 | 8.10 | 6.04 | 1.97 | 0.19 | 5.87 | 2.74 | 1.32 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.87 | 0.65 | 5.04 | 6.82 | 6.75 | 7.53 | 6.71 | 4.98 | 0.19 | 4.21 | 4.07 | 1.84 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## Independent-sample regressions (legacy)

Every note and role where candidate 0.4.18 is worse than shipping 0.4.17 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (16.3605 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 8 | 7.8675 | 7.8676 | 0.0001 | 0 | 0 | 0 |
| dev | tuning_cents | 8 | 0.6486 | 0.6487 | 0.0001 | 0 | 0 | 0 |
| dev | decay_db_s | 8 | 5.0398 | 5.0405 | 0.0007 | 0 | 0 | 0 |
| dev | attack_db | 8 | 6.8017 | 6.8163 | 0.0146 | 0 | 0 | 0 |
| dev | early_db | 8 | 6.7478 | 6.7477 | -0.0001 | 0 | 0 | 0 |
| dev | sustain_db | 8 | 7.5310 | 7.5310 | -0.0000 | 0 | 0 | 0 |
| dev | noise_db | 6 | 6.7175 | 6.7072 | -0.0103 | 0 | 0 | 2 |
| dev | ild_db | 8 | 4.9858 | 4.9821 | -0.0037 | 0 | 0 | 0 |
| dev | icc | 8 | 0.1915 | 0.1915 | 0.0001 | 0 | 0 | 0 |
| dev | envelope_db | 8 | 4.2111 | 4.2126 | 0.0015 | 0 | 0 | 0 |
| dev | rise_ms | 8 | 4.0391 | 4.0703 | 0.0312 | 0 | 0 | 0 |
| dev | level_db | 8 | 1.8408 | 1.8428 | 0.0019 | 0 | 0 | 0 |
| train | partial_db | 40 | 4.6896 | 4.6901 | 0.0005 | 0 | 0 | 0 |
| train | tuning_cents | 40 | 0.2629 | 0.2602 | -0.0027 | 0 | 0 | 0 |
| train | decay_db_s | 40 | 3.4171 | 3.4165 | -0.0006 | 0 | 0 | 0 |
| train | attack_db | 40 | 6.1388 | 6.1373 | -0.0015 | 0 | 0 | 0 |
| train | early_db | 40 | 5.0688 | 5.0692 | 0.0004 | 0 | 0 | 0 |
| train | sustain_db | 40 | 5.6241 | 5.6238 | -0.0003 | 0 | 0 | 0 |
| train | noise_db | 37 | 7.1750 | 7.1640 | -0.0111 | 0 | 0 | 3 |
| train | ild_db | 40 | 1.5267 | 1.5251 | -0.0016 | 0 | 0 | 0 |
| train | icc | 40 | 0.1157 | 0.1157 | 0.0000 | 0 | 0 | 0 |
| train | envelope_db | 40 | 3.3033 | 3.3029 | -0.0003 | 0 | 0 | 0 |
| train | rise_ms | 40 | 17.4161 | 17.4177 | 0.0016 | 0 | 0 | 0 |
| train | level_db | 40 | 0.6979 | 0.6967 | -0.0012 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
