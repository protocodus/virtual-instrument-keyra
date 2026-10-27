# Recording benchmark: candidate 0.4.0 against shipping 0.3.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## shipping 0.3.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 9.13 | 7.50 | 6.23 | 16.08 | 14.08 | 10.69 | 25.43 | 5.48 | 0.26 | 5.84 | 6.61 | 4.08 |
| dev (156) | 9.57 | 6.12 | 6.39 | 15.80 | 14.20 | 10.24 | 25.87 | 5.82 | 0.25 | 5.48 | 9.19 | 4.17 |
| train / bass A0-B2 (84) | 12.14 | 6.73 | 4.90 | 8.60 | 8.40 | 9.73 | 29.18 | 4.55 | 0.29 | 4.16 | 10.76 | 4.13 |
| train / middle C3-B5 (108) | 5.48 | 1.88 | 4.22 | 14.23 | 10.25 | 7.26 | 20.34 | 4.63 | 0.24 | 4.57 | 5.94 | 1.37 |
| train / treble C6-C8 (84) | 10.81 | 15.48 | 10.16 | 25.93 | 24.67 | 16.07 | 28.24 | 7.65 | 0.25 | 9.14 | 3.33 | 7.51 |
| dev / bass A0-B2 (44) | 12.77 | 5.98 | 4.36 | 8.35 | 8.08 | 9.99 | 29.16 | 5.27 | 0.29 | 4.33 | 19.32 | 4.25 |
| dev / middle C3-B5 (68) | 6.48 | 1.86 | 5.70 | 13.76 | 10.78 | 7.37 | 22.07 | 5.41 | 0.19 | 4.40 | 6.62 | 1.45 |
| dev / treble C6-C8 (44) | 11.15 | 12.83 | 9.47 | 26.40 | 25.60 | 14.92 | 28.44 | 7.04 | 0.30 | 8.29 | 3.05 | 8.28 |

## candidate 0.4.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 2.24 | 0.65 | 4.82 | 3.80 | 3.39 | 4.05 | 5.87 | 0.91 | 0.07 | 3.72 | 3.89 | 0.55 |
| dev (156) | 3.39 | 2.33 | 5.00 | 4.22 | 4.24 | 5.19 | 5.96 | 3.34 | 0.13 | 3.47 | 5.29 | 1.23 |
| train / bass A0-B2 (84) | 0.76 | 0.06 | 0.58 | 3.45 | 1.80 | 1.44 | 6.17 | 0.42 | 0.04 | 2.22 | 4.47 | 0.15 |
| train / middle C3-B5 (108) | 1.13 | 0.16 | 2.10 | 2.97 | 2.39 | 2.04 | 5.76 | 0.74 | 0.05 | 0.67 | 4.40 | 0.19 |
| train / treble C6-C8 (84) | 5.14 | 1.88 | 12.56 | 5.24 | 6.25 | 9.26 | 5.73 | 1.67 | 0.14 | 9.16 | 2.66 | 1.43 |
| dev / bass A0-B2 (44) | 2.38 | 2.67 | 1.15 | 3.97 | 2.86 | 2.40 | 6.36 | 2.04 | 0.07 | 2.82 | 5.69 | 1.12 |
| dev / middle C3-B5 (68) | 3.59 | 0.81 | 3.10 | 3.80 | 3.71 | 4.61 | 6.01 | 4.88 | 0.13 | 1.41 | 6.14 | 1.18 |
| dev / treble C6-C8 (44) | 4.08 | 4.33 | 11.78 | 5.13 | 6.43 | 8.86 | 5.50 | 2.21 | 0.19 | 7.29 | 3.56 | 1.42 |

## Regressions

Every note and role where candidate 0.4.0 is worse than shipping 0.3.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | shipping 0.3.0 | candidate 0.4.0 |
|---|---|---|---|---|
| 108 | train | envelope_db | 15.91 | 28.28 |
| 105 | train | decay_db_s | 5.37 | 29.34 |
| 105 | dev | decay_db_s | 4.27 | 22.51 |
| 108 | dev | envelope_db | 12.78 | 21.75 |
| 105 | dev | envelope_db | 10.43 | 17.56 |
| 108 | train | decay_db_s | 12.69 | 25.13 |
| 51 | dev | ild_db | 4.70 | 10.66 |
| 105 | train | envelope_db | 11.19 | 16.08 |
| 108 | dev | decay_db_s | 15.44 | 23.94 |
| 60 | train | rise_ms | 1.53 | 8.91 |
| 27 | dev | tuning_cents | 4.24 | 7.25 |
| 51 | dev | icc | 0.14 | 0.25 |
| 66 | train | rise_ms | 2.72 | 7.78 |
| 75 | dev | sustain_db | 8.44 | 10.94 |
| 42 | train | rise_ms | 3.94 | 7.66 |
| 42 | dev | rise_ms | 3.85 | 7.56 |
| 75 | dev | icc | 0.15 | 0.22 |
| 66 | dev | rise_ms | 3.73 | 6.90 |
| 60 | dev | rise_ms | 3.32 | 6.48 |
| 99 | dev | rise_ms | 2.80 | 5.42 |
| 102 | train | rise_ms | 1.81 | 4.07 |
| 102 | dev | rise_ms | 1.39 | 3.65 |
| 99 | dev | decay_db_s | 8.25 | 10.47 |
| 75 | dev | rise_ms | 1.95 | 3.97 |
| 96 | dev | decay_db_s | 9.32 | 11.32 |
| 51 | dev | level_db | 2.15 | 3.13 |
| 90 | train | rise_ms | 3.06 | 4.84 |
| 90 | dev | rise_ms | 2.78 | 4.49 |
| 51 | dev | rise_ms | 12.15 | 13.75 |
| 75 | dev | ild_db | 7.86 | 8.60 |
| 75 | dev | partial_db | 6.87 | 7.57 |
| 30 | dev | envelope_db | 4.39 | 5.09 |
| 84 | dev | decay_db_s | 8.16 | 9.42 |
