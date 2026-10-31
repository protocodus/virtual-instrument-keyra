# Recording benchmark: kawai-fit against grand-data

Every train and dev note of `Tools/corpus/split-vcsl-kawai-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## grand-data

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev (23) | 7.74 | 4.17 | 4.90 | 8.82 | 9.55 | 9.48 | 12.66 | 4.52 | 0.19 | 4.26 | 8.02 | 7.27 |
| dev / bass A0-B2 (8) | 8.08 | 2.74 | 2.68 | 9.03 | 7.89 | 7.56 | 14.92 | 2.85 | 0.12 | 2.96 | 12.93 | 6.63 |
| dev / middle C3-B5 (12) | 7.03 | 3.90 | 5.10 | 8.19 | 9.03 | 9.61 | 11.58 | 5.79 | 0.15 | 4.96 | 6.53 | 7.37 |
| dev / treble C6-C8 (3) | 10.67 | 11.49 | 12.55 | 10.76 | 16.03 | 16.44 | 10.63 | 4.17 | 0.69 | 4.93 | 0.87 | 8.60 |

## kawai-fit

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev (23) | 9.88 | 2.87 | 5.24 | 8.23 | 9.45 | 9.51 | 8.77 | 5.28 | 0.20 | 4.91 | 4.99 | 3.96 |
| dev / bass A0-B2 (8) | 10.87 | 3.70 | 2.68 | 8.69 | 8.62 | 9.37 | 10.76 | 3.19 | 0.14 | 3.40 | 7.15 | 1.51 |
| dev / middle C3-B5 (12) | 9.23 | 2.25 | 6.26 | 8.01 | 9.93 | 10.00 | 7.67 | 7.74 | 0.17 | 6.19 | 4.16 | 4.57 |
| dev / treble C6-C8 (3) | 9.88 | 3.32 | 9.37 | 7.88 | 9.73 | 7.11 | 7.47 | 0.08 | 0.56 | 3.82 | 2.55 | 8.10 |

## Regressions

Every note and role where kawai-fit is worse than grand-data by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | grand-data | kawai-fit |
|---|---|---|---|---|
| 83 | dev | partial_db | 11.44 | 22.43 |
| 74 | dev | ild_db | 4.91 | 11.64 |
| 83 | dev | early_db | 11.06 | 17.30 |
| 83 | dev | attack_db | 7.82 | 13.75 |
| 58 | dev | partial_db | 5.95 | 11.30 |
| 83 | dev | decay_db_s | 9.15 | 16.34 |
| 82 | dev | icc | 0.15 | 0.28 |
| 27 | dev | partial_db | 8.23 | 11.52 |
| 27 | dev | tuning_cents | 2.94 | 5.83 |
| 39 | dev | sustain_db | 7.10 | 9.92 |
| 74 | dev | partial_db | 4.26 | 6.77 |
| 39 | dev | partial_db | 7.93 | 10.23 |
| 83 | dev | noise_db | 7.90 | 10.19 |
| 83 | dev | sustain_db | 10.49 | 12.75 |
| 74 | dev | early_db | 8.25 | 10.49 |
| 58 | dev | early_db | 6.37 | 8.50 |
| 58 | dev | envelope_db | 5.04 | 6.94 |
| 74 | dev | envelope_db | 4.40 | 6.14 |
| 58 | dev | sustain_db | 8.59 | 10.06 |
| 83 | dev | icc | 0.12 | 0.18 |
| 83 | dev | level_db | 6.96 | 8.31 |
| 39 | dev | icc | 0.11 | 0.16 |
| 103 | dev | envelope_db | 0.89 | 2.01 |
| 82 | dev | decay_db_s | 3.08 | 5.30 |
| 103 | dev | level_db | 2.89 | 4.00 |
| 39 | dev | early_db | 7.50 | 8.55 |
| 103 | dev | rise_ms | 1.37 | 3.27 |
| 74 | dev | noise_db | 7.74 | 8.58 |
| 27 | dev | envelope_db | 3.27 | 4.10 |
| 82 | dev | ild_db | 6.67 | 7.50 |
| 27 | dev | sustain_db | 8.02 | 8.82 |
| 102 | dev | rise_ms | 0.62 | 2.19 |
| 83 | dev | rise_ms | 4.73 | 5.95 |
