# Recording benchmark: candidate 0.4.0 against shipping 0.3.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## shipping 0.3.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 10.08 | 7.79 | 5.57 | 16.21 | 15.18 | 14.05 | 25.33 | 5.44 | 0.27 | 8.65 | 6.72 | 3.99 |
| dev (156) | 10.75 | 6.98 | 6.75 | 15.94 | 15.12 | 13.32 | 25.80 | 5.88 | 0.25 | 8.25 | 8.96 | 4.11 |
| train / bass A0-B2 (84) | 12.31 | 6.77 | 5.19 | 8.41 | 8.40 | 9.88 | 29.18 | 4.42 | 0.29 | 4.26 | 11.12 | 4.12 |
| train / middle C3-B5 (108) | 5.56 | 1.89 | 3.71 | 14.40 | 12.22 | 10.26 | 20.34 | 4.13 | 0.26 | 5.41 | 5.87 | 1.36 |
| train / treble C6-C8 (84) | 13.65 | 16.38 | 8.33 | 26.33 | 25.77 | 23.09 | 27.91 | 8.14 | 0.27 | 17.21 | 3.42 | 7.26 |
| dev / bass A0-B2 (44) | 13.43 | 6.42 | 7.64 | 8.31 | 8.17 | 10.16 | 29.16 | 5.17 | 0.29 | 4.42 | 19.26 | 4.24 |
| dev / middle C3-B5 (68) | 6.56 | 1.87 | 4.68 | 13.89 | 12.30 | 9.72 | 22.06 | 4.88 | 0.20 | 5.34 | 6.12 | 1.45 |
| dev / treble C6-C8 (44) | 14.55 | 15.45 | 9.06 | 26.73 | 26.43 | 22.04 | 28.21 | 8.12 | 0.28 | 16.58 | 3.06 | 8.10 |

## candidate 0.4.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 2.86 | 0.58 | 6.42 | 5.71 | 4.03 | 8.69 | 10.00 | 1.26 | 0.09 | 3.43 | 4.71 | 0.47 |
| dev (156) | 3.91 | 2.23 | 6.55 | 6.38 | 4.70 | 8.88 | 11.29 | 3.14 | 0.12 | 3.02 | 5.27 | 1.66 |
| train / bass A0-B2 (84) | 0.71 | 0.07 | 0.62 | 5.27 | 2.17 | 2.16 | 18.23 | 0.70 | 0.06 | 2.26 | 5.48 | 0.14 |
| train / middle C3-B5 (108) | 1.09 | 0.12 | 3.07 | 3.69 | 3.10 | 5.54 | 6.98 | 1.13 | 0.08 | 0.69 | 4.65 | 0.18 |
| train / treble C6-C8 (84) | 7.28 | 1.75 | 17.16 | 8.76 | 7.10 | 19.28 | 5.64 | 1.99 | 0.15 | 8.13 | 4.04 | 1.16 |
| dev / bass A0-B2 (44) | 2.49 | 2.70 | 1.24 | 6.71 | 3.25 | 2.72 | 19.32 | 1.91 | 0.09 | 2.31 | 3.89 | 2.08 |
| dev / middle C3-B5 (68) | 3.12 | 0.81 | 3.18 | 4.48 | 3.82 | 6.16 | 9.77 | 4.08 | 0.11 | 0.88 | 6.38 | 1.33 |
| dev / treble C6-C8 (44) | 6.56 | 4.00 | 17.33 | 8.97 | 7.51 | 19.22 | 5.63 | 2.90 | 0.17 | 7.04 | 4.93 | 1.74 |

## Regressions

Every note and role where candidate 0.4.0 is worse than shipping 0.3.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | shipping 0.3.0 | candidate 0.4.0 |
|---|---|---|---|---|
| 105 | train | decay_db_s | 3.96 | 23.33 |
| 105 | dev | decay_db_s | 4.19 | 23.08 |
| 84 | dev | decay_db_s | 4.17 | 19.16 |
| 84 | train | decay_db_s | 4.13 | 18.29 |
| 96 | train | decay_db_s | 7.73 | 20.88 |
| 96 | dev | decay_db_s | 7.13 | 18.96 |
| 102 | dev | decay_db_s | 9.40 | 17.59 |
| 102 | train | decay_db_s | 9.64 | 17.59 |
| 60 | train | rise_ms | 1.64 | 9.13 |
| 51 | dev | ild_db | 3.94 | 7.65 |
| 99 | dev | decay_db_s | 10.57 | 17.67 |
| 51 | dev | rise_ms | 10.50 | 17.39 |
| 108 | dev | decay_db_s | 13.39 | 18.93 |
| 60 | dev | rise_ms | 1.34 | 6.44 |
| 81 | train | decay_db_s | 3.69 | 8.42 |
| 81 | dev | decay_db_s | 3.58 | 7.95 |
| 99 | dev | rise_ms | 2.80 | 7.09 |
| 27 | dev | tuning_cents | 5.33 | 7.31 |
| 102 | dev | rise_ms | 1.40 | 5.23 |
| 90 | train | decay_db_s | 8.89 | 12.18 |
| 102 | train | rise_ms | 2.06 | 5.26 |
| 75 | dev | level_db | 1.31 | 2.89 |
| 90 | dev | rise_ms | 2.78 | 5.75 |
| 90 | train | rise_ms | 3.06 | 5.72 |
| 108 | train | envelope_db | 18.93 | 20.18 |
| 108 | dev | rise_ms | 2.47 | 4.96 |
| 72 | train | decay_db_s | 1.85 | 4.22 |
| 72 | dev | decay_db_s | 1.71 | 3.97 |
| 93 | dev | decay_db_s | 9.96 | 12.14 |
| 108 | train | rise_ms | 2.70 | 4.86 |
| 27 | dev | attack_db | 8.27 | 9.34 |
| 51 | dev | icc | 0.15 | 0.19 |
| 108 | train | decay_db_s | 14.03 | 15.77 |
| 66 | train | rise_ms | 2.70 | 4.42 |
| 93 | train | decay_db_s | 9.93 | 11.50 |
| 78 | dev | decay_db_s | 3.39 | 4.93 |
| 105 | dev | rise_ms | 1.69 | 3.11 |
| 90 | dev | decay_db_s | 9.11 | 10.44 |
| 105 | train | rise_ms | 2.73 | 3.82 |
| 84 | train | rise_ms | 2.11 | 3.14 |
