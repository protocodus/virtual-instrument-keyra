# Recording benchmark: candidate 0.4.0 against shipping 0.3.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## shipping 0.3.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.80 | 7.37 | 6.94 | 16.08 | 14.08 | 10.69 | 25.43 | 5.48 | 0.26 | 5.16 | 6.61 | 4.08 |
| dev (156) | 9.30 | 6.13 | 6.15 | 15.80 | 14.20 | 10.24 | 25.87 | 5.82 | 0.25 | 5.25 | 9.19 | 4.17 |
| train / bass A0-B2 (84) | 11.71 | 6.60 | 3.20 | 8.60 | 8.40 | 9.73 | 29.18 | 4.55 | 0.29 | 4.24 | 10.76 | 4.13 |
| train / middle C3-B5 (108) | 5.45 | 1.88 | 3.58 | 14.23 | 10.25 | 7.26 | 20.34 | 4.63 | 0.24 | 4.90 | 5.94 | 1.37 |
| train / treble C6-C8 (84) | 10.22 | 15.21 | 15.01 | 25.93 | 24.67 | 16.07 | 28.24 | 7.65 | 0.25 | 6.41 | 3.33 | 7.51 |
| dev / bass A0-B2 (44) | 12.27 | 6.01 | 3.08 | 8.35 | 8.08 | 9.99 | 29.16 | 5.27 | 0.29 | 4.40 | 19.32 | 4.25 |
| dev / middle C3-B5 (68) | 6.33 | 1.87 | 4.11 | 13.76 | 10.78 | 7.37 | 22.07 | 5.41 | 0.19 | 5.14 | 6.62 | 1.45 |
| dev / treble C6-C8 (44) | 10.93 | 12.83 | 12.39 | 26.40 | 25.60 | 14.92 | 28.44 | 7.04 | 0.30 | 6.28 | 3.05 | 8.28 |

## candidate 0.4.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 1.91 | 0.65 | 4.47 | 3.80 | 3.39 | 4.05 | 5.87 | 0.91 | 0.07 | 1.80 | 3.89 | 0.55 |
| dev (156) | 3.16 | 2.35 | 4.87 | 4.20 | 4.17 | 5.17 | 5.95 | 2.61 | 0.13 | 2.54 | 4.93 | 1.22 |
| train / bass A0-B2 (84) | 0.73 | 0.06 | 0.46 | 3.45 | 1.80 | 1.44 | 6.17 | 0.42 | 0.04 | 1.95 | 4.47 | 0.15 |
| train / middle C3-B5 (108) | 1.24 | 0.16 | 1.40 | 2.97 | 2.39 | 2.04 | 5.76 | 0.74 | 0.05 | 0.69 | 4.40 | 0.19 |
| train / treble C6-C8 (84) | 3.97 | 1.88 | 12.42 | 5.24 | 6.25 | 9.26 | 5.73 | 1.67 | 0.14 | 3.06 | 2.66 | 1.42 |
| dev / bass A0-B2 (44) | 2.20 | 2.78 | 0.95 | 3.98 | 2.88 | 2.38 | 6.35 | 1.37 | 0.07 | 2.69 | 4.70 | 1.17 |
| dev / middle C3-B5 (68) | 3.48 | 0.80 | 2.49 | 3.73 | 3.55 | 4.60 | 5.98 | 3.92 | 0.12 | 1.82 | 5.95 | 1.13 |
| dev / treble C6-C8 (44) | 3.63 | 4.33 | 12.46 | 5.12 | 6.43 | 8.83 | 5.50 | 1.79 | 0.19 | 3.51 | 3.58 | 1.42 |

## Regressions

Every note and role where candidate 0.4.0 is worse than shipping 0.3.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | shipping 0.3.0 | candidate 0.4.0 |
|---|---|---|---|---|
| 60 | train | rise_ms | 1.53 | 8.91 |
| 27 | dev | tuning_cents | 4.53 | 7.53 |
| 102 | train | decay_db_s | 19.96 | 25.55 |
| 102 | dev | decay_db_s | 9.23 | 14.50 |
| 66 | train | rise_ms | 2.72 | 7.78 |
| 99 | dev | decay_db_s | 9.70 | 14.55 |
| 75 | dev | sustain_db | 8.44 | 10.74 |
| 51 | dev | ild_db | 4.70 | 6.88 |
| 51 | dev | icc | 0.14 | 0.23 |
| 96 | train | decay_db_s | 9.03 | 13.28 |
| 96 | dev | decay_db_s | 11.44 | 15.22 |
| 42 | train | rise_ms | 3.94 | 7.66 |
| 42 | dev | rise_ms | 3.85 | 7.56 |
| 66 | dev | rise_ms | 3.73 | 6.90 |
| 60 | dev | rise_ms | 3.32 | 6.48 |
| 99 | dev | rise_ms | 2.80 | 5.45 |
| 75 | dev | icc | 0.15 | 0.19 |
| 102 | train | rise_ms | 1.81 | 4.07 |
| 102 | dev | rise_ms | 1.39 | 3.65 |
| 75 | dev | rise_ms | 1.95 | 3.93 |
| 108 | train | decay_db_s | 6.51 | 8.32 |
| 90 | train | rise_ms | 3.06 | 4.84 |
| 51 | dev | level_db | 2.15 | 3.04 |
| 90 | dev | rise_ms | 2.78 | 4.49 |
