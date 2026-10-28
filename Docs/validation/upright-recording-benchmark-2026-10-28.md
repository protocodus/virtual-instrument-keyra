# Recording benchmark: the upright against the grand's data

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## the grand's data

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 6.42 | 14.25 | 5.24 | 7.70 | 7.82 | 10.05 | 12.49 | 6.20 | 0.22 | 5.28 | 10.39 | 4.09 |
| dev (21) | 5.81 | 13.53 | 4.59 | 7.95 | 8.51 | 9.54 | 12.36 | 5.76 | 0.19 | 5.33 | 14.90 | 3.22 |
| train / bass A0-B2 (30) | 7.39 | 37.71 | 5.68 | 7.88 | 6.90 | 9.38 | 19.71 | 7.46 | 0.19 | 3.66 | 17.33 | 3.80 |
| train / middle C3-B5 (69) | 6.87 | 7.52 | 5.23 | 7.41 | 7.25 | 8.71 | 12.42 | 6.67 | 0.20 | 4.72 | 10.11 | 4.19 |
| train / treble C6-C8 (38) | 4.85 | 7.96 | 4.91 | 8.08 | 9.57 | 13.00 | 6.91 | 4.26 | 0.29 | 7.57 | 5.43 | 4.13 |
| dev / bass A0-B2 (5) | 6.68 | 29.42 | 2.52 | 8.42 | 9.37 | 10.70 | 19.11 | 5.61 | 0.27 | 2.58 | 36.29 | 2.22 |
| dev / middle C3-B5 (11) | 6.46 | 5.12 | 4.92 | 7.91 | 7.88 | 8.93 | 11.73 | 7.15 | 0.15 | 6.96 | 9.67 | 3.41 |
| dev / treble C6-C8 (5) | 3.50 | 16.15 | 5.94 | 7.54 | 9.04 | 9.74 | 7.01 | 2.84 | 0.20 | 4.50 | 5.00 | 3.82 |

## the upright

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 3.18 | 0.78 | 2.92 | 4.17 | 4.04 | 5.65 | 9.81 | 2.30 | 0.12 | 3.01 | 6.53 | 0.80 |
| dev (21) | 6.40 | 3.72 | 5.54 | 5.64 | 6.48 | 9.04 | 10.51 | 4.32 | 0.20 | 6.29 | 10.30 | 2.30 |
| train / bass A0-B2 (30) | 2.49 | 0.48 | 1.56 | 3.14 | 2.16 | 2.40 | 14.28 | 1.18 | 0.08 | 2.05 | 12.22 | 0.23 |
| train / middle C3-B5 (69) | 2.55 | 0.48 | 2.39 | 4.02 | 3.28 | 4.44 | 10.01 | 1.99 | 0.10 | 2.30 | 5.94 | 0.29 |
| train / treble C6-C8 (38) | 4.88 | 1.56 | 5.07 | 5.27 | 6.92 | 10.55 | 5.93 | 3.84 | 0.21 | 5.06 | 3.10 | 2.18 |
| dev / bass A0-B2 (5) | 5.56 | 3.03 | 2.15 | 3.94 | 5.02 | 7.25 | 16.06 | 5.12 | 0.19 | 2.42 | 1.13 | 1.50 |
| dev / middle C3-B5 (11) | 5.66 | 2.48 | 3.29 | 5.71 | 5.67 | 7.10 | 9.31 | 4.57 | 0.15 | 5.61 | 13.51 | 2.31 |
| dev / treble C6-C8 (5) | 8.86 | 7.13 | 13.90 | 7.20 | 9.74 | 15.11 | 7.61 | 2.98 | 0.32 | 11.67 | 12.43 | 3.07 |

## Regressions

Every note and role where the upright is worse than the grand's data by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | the grand's data | the upright |
|---|---|---|---|---|
| 27 | train | rise_ms | 9.92 | 28.70 |
| 103 | train | partial_db | 4.40 | 12.80 |
| 103 | train | decay_db_s | 1.97 | 17.49 |
| 88 | dev | envelope_db | 4.50 | 11.67 |
| 59 | dev | rise_ms | 1.52 | 14.04 |
| 88 | dev | sustain_db | 9.74 | 15.11 |
| 88 | dev | partial_db | 3.50 | 8.86 |
| 56 | dev | rise_ms | 5.84 | 14.50 |
| 82 | train | envelope_db | 3.73 | 7.98 |
| 88 | dev | decay_db_s | 5.94 | 13.90 |
| 76 | train | rise_ms | 10.75 | 18.42 |
| 100 | train | partial_db | 2.40 | 6.15 |
| 88 | dev | rise_ms | 5.00 | 12.43 |
| 96 | train | icc | 0.15 | 0.28 |
| 88 | dev | icc | 0.20 | 0.32 |
| 94 | train | level_db | 1.29 | 4.22 |
| 59 | dev | partial_db | 6.88 | 9.22 |
| 90 | train | ild_db | 3.00 | 5.34 |
| 82 | train | sustain_db | 6.46 | 8.14 |
| 45 | train | rise_ms | 4.36 | 7.42 |
| 94 | train | ild_db | 2.65 | 4.16 |
| 33 | train | rise_ms | 7.65 | 10.36 |
| 92 | train | sustain_db | 11.60 | 12.71 |
| 66 | train | envelope_db | 2.36 | 3.27 |
| 92 | train | ild_db | 3.04 | 3.87 |
| 92 | train | partial_db | 4.32 | 5.06 |
| 72 | dev | icc | 0.14 | 0.17 |
| 90 | train | sustain_db | 10.04 | 10.75 |
| 88 | dev | early_db | 9.04 | 9.74 |
| 88 | dev | noise_db | 7.01 | 7.61 |
| 103 | train | level_db | 3.87 | 4.47 |
| 50 | train | rise_ms | 2.93 | 4.08 |
| 100 | train | rise_ms | 0.59 | 1.73 |
| 86 | train | decay_db_s | 4.14 | 5.22 |
