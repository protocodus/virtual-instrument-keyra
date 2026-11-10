# Recording benchmark: 0.4.32 against 0.4.31

Every train and dev note of `Tools/corpus/split-hamburg-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.31

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (40) | 4.45 | 0.27 | 2.30 | 5.87 | 4.35 | 4.92 | 6.43 | 1.59 | 0.12 | 2.99 | 16.60 | 0.55 |
| dev (8) | 7.14 | 2.59 | 3.66 | 7.38 | 6.27 | 6.14 | 6.48 | 4.93 | 0.23 | 2.33 | 2.88 | 3.12 |
| train / bass A0-B2 (16) | 4.64 | 0.10 | 0.98 | 6.07 | 3.62 | 3.58 | 7.66 | 0.84 | 0.07 | 2.09 | 31.31 | 0.55 |
| train / middle C3-B5 (12) | 4.64 | 0.23 | 2.09 | 5.99 | 4.41 | 4.72 | 6.06 | 2.16 | 0.15 | 1.83 | 11.41 | 0.22 |
| train / treble C6-C8 (12) | 3.99 | 0.51 | 4.26 | 5.48 | 5.27 | 6.88 | 5.47 | 2.02 | 0.16 | 5.35 | 2.17 | 0.86 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.14 | 2.59 | 3.66 | 7.38 | 6.27 | 6.14 | 6.48 | 4.93 | 0.23 | 2.33 | 2.88 | 3.12 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## 0.4.32

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (40) | 4.38 | 0.29 | 2.34 | 5.90 | 4.43 | 4.98 | 6.47 | 1.55 | 0.12 | 2.94 | 16.79 | 1.04 |
| dev (8) | 7.15 | 2.58 | 3.63 | 7.36 | 6.25 | 6.13 | 6.43 | 4.94 | 0.23 | 2.33 | 2.79 | 2.60 |
| train / bass A0-B2 (16) | 4.65 | 0.10 | 0.99 | 6.07 | 3.62 | 3.59 | 7.70 | 0.92 | 0.07 | 2.09 | 31.92 | 0.66 |
| train / middle C3-B5 (12) | 4.60 | 0.23 | 2.13 | 5.99 | 4.36 | 4.73 | 5.99 | 2.25 | 0.15 | 1.91 | 11.43 | 0.81 |
| train / treble C6-C8 (12) | 3.80 | 0.61 | 4.35 | 5.58 | 5.59 | 7.10 | 5.62 | 1.70 | 0.15 | 5.12 | 2.00 | 1.79 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.15 | 2.58 | 3.63 | 7.36 | 6.25 | 6.13 | 6.43 | 4.94 | 0.23 | 2.33 | 2.79 | 2.60 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## Independent-sample regressions (legacy)

Every note and role where 0.4.32 is worse than 0.4.31 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.31 | 0.4.32 |
|---|---|---|---|---|
| 87 | train | level_db | 0.25 | 2.81 |
| 80 | train | level_db | 0.30 | 1.64 |
| 38 | train | rise_ms | 20.56 | 23.03 |
| 87 | train | sustain_db | 7.57 | 8.27 |
| 94 | train | early_db | 5.35 | 5.88 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (14.9476 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 8 | 7.1446 | 7.1521 | 0.0075 | 0 | 0 | 0 |
| dev | tuning_cents | 8 | 2.5889 | 2.5758 | -0.0131 | 0 | 0 | 0 |
| dev | decay_db_s | 8 | 3.6551 | 3.6319 | -0.0232 | 0 | 0 | 0 |
| dev | attack_db | 8 | 7.3820 | 7.3590 | -0.0231 | 0 | 0 | 0 |
| dev | early_db | 8 | 6.2707 | 6.2538 | -0.0169 | 0 | 0 | 0 |
| dev | sustain_db | 8 | 6.1365 | 6.1267 | -0.0097 | 0 | 0 | 0 |
| dev | noise_db | 6 | 6.4750 | 6.4331 | -0.0419 | 0 | 0 | 2 |
| dev | ild_db | 8 | 4.9259 | 4.9351 | 0.0092 | 0 | 0 | 0 |
| dev | icc | 8 | 0.2333 | 0.2335 | 0.0002 | 0 | 0 | 0 |
| dev | envelope_db | 8 | 2.3316 | 2.3254 | -0.0062 | 0 | 0 | 0 |
| dev | rise_ms | 8 | 2.8828 | 2.7917 | -0.0911 | 0 | 0 | 0 |
| dev | level_db | 8 | 3.1236 | 2.6653 | -0.4583 | 0 | 0 | 0 |
| train | partial_db | 40 | 4.4463 | 4.3806 | -0.0657 | 0 | 0 | 0 |
| train | tuning_cents | 40 | 0.2657 | 0.2937 | 0.0281 | 0 | 0 | 0 |
| train | decay_db_s | 40 | 2.2989 | 2.3383 | 0.0394 | 0 | 0 | 0 |
| train | attack_db | 40 | 5.8713 | 5.9022 | 0.0309 | 0 | 0 | 0 |
| train | early_db | 40 | 4.3536 | 4.4316 | 0.0781 | 0 | 0 | 0 |
| train | sustain_db | 40 | 4.9150 | 4.9848 | 0.0697 | 0 | 0 | 0 |
| train | noise_db | 37 | 6.4314 | 6.4698 | 0.0384 | 0 | 0 | 3 |
| train | ild_db | 40 | 1.5896 | 1.5512 | -0.0384 | 0 | 0 | 0 |
| train | icc | 40 | 0.1176 | 0.1171 | -0.0006 | 0 | 0 | 0 |
| train | envelope_db | 40 | 2.9882 | 2.9442 | -0.0440 | 0 | 0 | 0 |
| train | rise_ms | 40 | 16.5958 | 16.7927 | 0.1969 | 0 | 0 | 0 |
| train | level_db | 40 | 0.5466 | 1.0434 | 0.4967 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 87 | train | level_db | 4 | 0.2509 | 2.8810 | 2.6300 |
| 38 | train | rise_ms | 4 | 20.5625 | 23.0260 | 2.4635 |
| 80 | train | level_db | 4 | 0.2972 | 1.5077 | 1.2105 |
| 87 | train | sustain_db | 4 | 7.5747 | 8.2703 | 0.6956 |
| 94 | train | early_db | 4 | 5.3510 | 5.8827 | 0.5316 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
