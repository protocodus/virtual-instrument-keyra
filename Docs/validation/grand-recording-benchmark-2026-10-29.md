# Recording benchmark: 0.4.1 at 98c6740 against shipping 0.3.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## shipping 0.3.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 9.39 | 2.64 | 4.09 | 16.08 | 14.08 | 10.69 | 24.71 | 5.48 | 0.26 | 5.16 | 6.61 | 4.08 |
| dev (156) | 9.78 | 2.27 | 4.68 | 15.80 | 14.20 | 10.24 | 24.68 | 5.82 | 0.25 | 5.25 | 9.19 | 4.17 |
| train / bass A0-B2 (84) | 12.59 | 2.59 | 3.44 | 8.60 | 8.40 | 9.73 | 27.65 | 4.55 | 0.29 | 4.24 | 10.76 | 4.13 |
| train / middle C3-B5 (108) | 5.49 | 1.06 | 3.42 | 14.23 | 10.25 | 7.26 | 20.20 | 4.63 | 0.24 | 4.90 | 5.94 | 1.37 |
| train / treble C6-C8 (84) | 11.19 | 4.71 | 5.71 | 25.93 | 24.67 | 16.07 | 27.86 | 7.65 | 0.25 | 6.41 | 3.33 | 7.51 |
| dev / bass A0-B2 (44) | 13.14 | 2.74 | 3.33 | 8.35 | 8.08 | 9.99 | 27.38 | 5.27 | 0.29 | 4.40 | 19.32 | 4.25 |
| dev / middle C3-B5 (68) | 6.36 | 1.02 | 4.38 | 13.76 | 10.78 | 7.37 | 20.66 | 5.41 | 0.19 | 5.14 | 6.62 | 1.45 |
| dev / treble C6-C8 (44) | 11.69 | 3.72 | 6.54 | 26.40 | 25.60 | 14.92 | 28.12 | 7.04 | 0.30 | 6.28 | 3.05 | 8.28 |

## 0.4.1 at 98c6740

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 1.69 | 0.26 | 1.68 | 3.78 | 3.07 | 3.68 | 6.90 | 0.91 | 0.06 | 1.89 | 3.82 | 0.54 |
| dev (156) | 3.13 | 1.10 | 2.25 | 4.17 | 3.68 | 4.58 | 6.31 | 2.56 | 0.12 | 2.52 | 4.54 | 1.10 |
| train / bass A0-B2 (84) | 0.51 | 0.04 | 0.39 | 3.37 | 1.65 | 1.31 | 8.73 | 0.36 | 0.03 | 1.95 | 4.48 | 0.15 |
| train / middle C3-B5 (108) | 1.31 | 0.07 | 1.30 | 2.97 | 2.39 | 2.06 | 6.25 | 0.70 | 0.04 | 0.69 | 4.31 | 0.19 |
| train / treble C6-C8 (84) | 3.36 | 0.72 | 3.56 | 5.23 | 5.36 | 8.13 | 5.92 | 1.78 | 0.13 | 3.39 | 2.54 | 1.38 |
| dev / bass A0-B2 (44) | 2.23 | 1.10 | 0.89 | 3.98 | 2.62 | 2.07 | 7.64 | 1.38 | 0.07 | 2.58 | 3.12 | 1.03 |
| dev / middle C3-B5 (68) | 3.38 | 0.61 | 2.43 | 3.64 | 3.40 | 4.52 | 5.85 | 3.92 | 0.12 | 1.82 | 6.09 | 0.95 |
| dev / treble C6-C8 (44) | 3.66 | 1.86 | 3.34 | 5.18 | 5.18 | 7.17 | 5.68 | 1.61 | 0.19 | 3.54 | 3.56 | 1.43 |

## Regressions

Every note and role where 0.4.1 at 98c6740 is worse than shipping 0.3.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | shipping 0.3.0 | 0.4.1 at 98c6740 |
|---|---|---|---|---|
| 60 | train | rise_ms | 1.53 | 8.95 |
| 66 | train | rise_ms | 2.72 | 7.91 |
| 51 | dev | ild_db | 4.70 | 6.87 |
| 51 | dev | icc | 0.14 | 0.22 |
| 75 | dev | sustain_db | 8.44 | 10.31 |
| 42 | train | rise_ms | 3.94 | 7.61 |
| 42 | dev | rise_ms | 3.85 | 7.51 |
| 99 | dev | tuning_cents | 2.28 | 3.93 |
| 60 | dev | rise_ms | 3.32 | 6.52 |
| 66 | dev | rise_ms | 3.73 | 6.90 |
| 99 | dev | rise_ms | 2.80 | 5.26 |
| 75 | dev | icc | 0.15 | 0.19 |
| 102 | dev | rise_ms | 1.39 | 3.55 |
| 75 | dev | rise_ms | 1.95 | 3.93 |
| 84 | dev | rise_ms | 3.21 | 5.02 |
| 102 | train | rise_ms | 1.81 | 3.60 |
| 105 | train | decay_db_s | 0.75 | 2.38 |
| 90 | dev | rise_ms | 2.78 | 4.30 |
| 51 | dev | rise_ms | 12.15 | 13.66 |
| 90 | train | rise_ms | 3.06 | 4.53 |
| 84 | train | rise_ms | 2.14 | 3.36 |
