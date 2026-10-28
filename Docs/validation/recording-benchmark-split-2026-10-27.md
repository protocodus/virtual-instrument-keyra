# Recording benchmark: candidate 0.4.0 against shipping 0.3.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## shipping 0.3.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.80 | 7.37 | 4.43 | 16.08 | 14.08 | 10.69 | 25.43 | 5.48 | 0.26 | 5.16 | 6.61 | 4.08 |
| dev (156) | 9.30 | 6.13 | 4.72 | 15.80 | 14.20 | 10.24 | 25.87 | 5.82 | 0.25 | 5.25 | 9.19 | 4.17 |
| train / bass A0-B2 (84) | 11.71 | 6.60 | 3.42 | 8.60 | 8.40 | 9.73 | 29.18 | 4.55 | 0.29 | 4.24 | 10.76 | 4.13 |
| train / middle C3-B5 (108) | 5.45 | 1.88 | 3.58 | 14.23 | 10.25 | 7.26 | 20.34 | 4.63 | 0.24 | 4.90 | 5.94 | 1.37 |
| train / treble C6-C8 (84) | 10.22 | 15.21 | 6.65 | 25.93 | 24.67 | 16.07 | 28.24 | 7.65 | 0.25 | 6.41 | 3.33 | 7.51 |
| dev / bass A0-B2 (44) | 12.27 | 6.01 | 3.21 | 8.35 | 8.08 | 9.99 | 29.16 | 5.27 | 0.29 | 4.40 | 19.32 | 4.25 |
| dev / middle C3-B5 (68) | 6.33 | 1.87 | 4.48 | 13.76 | 10.78 | 7.37 | 22.07 | 5.41 | 0.19 | 5.14 | 6.62 | 1.45 |
| dev / treble C6-C8 (44) | 10.93 | 12.83 | 6.66 | 26.40 | 25.60 | 14.92 | 28.44 | 7.04 | 0.30 | 6.28 | 3.05 | 8.28 |

## candidate 0.4.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 1.73 | 0.68 | 1.75 | 3.78 | 3.18 | 3.84 | 5.79 | 0.88 | 0.06 | 1.79 | 3.81 | 0.55 |
| dev (156) | 3.13 | 2.37 | 2.59 | 4.18 | 3.91 | 4.93 | 5.83 | 2.59 | 0.12 | 2.53 | 4.77 | 1.22 |
| train / bass A0-B2 (84) | 0.75 | 0.07 | 0.40 | 3.37 | 1.69 | 1.36 | 6.03 | 0.36 | 0.03 | 1.95 | 4.49 | 0.15 |
| train / middle C3-B5 (108) | 1.23 | 0.16 | 1.26 | 2.97 | 2.40 | 2.04 | 5.75 | 0.74 | 0.05 | 0.69 | 4.41 | 0.19 |
| train / treble C6-C8 (84) | 3.34 | 1.96 | 3.85 | 5.22 | 5.67 | 8.61 | 5.59 | 1.65 | 0.13 | 3.04 | 2.37 | 1.41 |
| dev / bass A0-B2 (44) | 2.19 | 2.78 | 0.93 | 3.94 | 2.76 | 2.23 | 6.14 | 1.31 | 0.07 | 2.69 | 4.21 | 1.17 |
| dev / middle C3-B5 (68) | 3.48 | 0.81 | 2.42 | 3.73 | 3.55 | 4.60 | 5.98 | 3.92 | 0.12 | 1.82 | 5.95 | 1.13 |
| dev / treble C6-C8 (44) | 3.52 | 4.36 | 4.55 | 5.12 | 5.62 | 8.15 | 5.28 | 1.76 | 0.18 | 3.47 | 3.51 | 1.41 |

## Regressions

Every note and role where candidate 0.4.0 is worse than shipping 0.3.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | shipping 0.3.0 | candidate 0.4.0 |
|---|---|---|---|---|
| 60 | train | rise_ms | 1.53 | 8.96 |
| 27 | dev | tuning_cents | 4.53 | 7.53 |
| 66 | train | rise_ms | 2.72 | 7.78 |
| 75 | dev | sustain_db | 8.44 | 10.74 |
| 51 | dev | ild_db | 4.70 | 6.88 |
| 51 | dev | icc | 0.14 | 0.23 |
| 42 | train | rise_ms | 3.94 | 7.66 |
| 42 | dev | rise_ms | 3.85 | 7.56 |
| 60 | dev | rise_ms | 3.32 | 6.53 |
| 66 | dev | rise_ms | 3.73 | 6.90 |
| 99 | dev | rise_ms | 2.80 | 5.35 |
| 75 | dev | icc | 0.15 | 0.19 |
| 75 | dev | rise_ms | 1.95 | 3.93 |
| 102 | dev | rise_ms | 1.39 | 3.33 |
| 51 | dev | level_db | 2.15 | 3.04 |
| 90 | train | rise_ms | 3.06 | 4.84 |
| 90 | dev | rise_ms | 2.78 | 4.50 |
| 105 | train | decay_db_s | 0.75 | 2.37 |
| 105 | dev | decay_db_s | 2.04 | 3.33 |
