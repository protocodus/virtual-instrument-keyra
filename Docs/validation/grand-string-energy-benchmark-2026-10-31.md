# Recording benchmark: string energy against round 7 (8a530bf)

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## round 7 (8a530bf)

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.62 | 0.25 | 1.79 | 4.44 | 4.19 | 4.60 | 5.62 | 0.92 | 0.06 | 1.95 | 3.87 | 0.69 |
| dev (156) | 5.44 | 1.09 | 2.29 | 4.81 | 4.52 | 5.31 | 5.36 | 2.44 | 0.12 | 2.65 | 4.22 | 1.07 |
| train / bass A0-B2 (84) | 4.65 | 0.04 | 0.44 | 4.76 | 3.96 | 3.74 | 5.43 | 0.42 | 0.03 | 2.12 | 5.53 | 0.43 |
| train / middle C3-B5 (108) | 4.97 | 0.07 | 1.46 | 4.02 | 4.13 | 3.50 | 6.08 | 0.71 | 0.04 | 0.83 | 3.69 | 0.29 |
| train / treble C6-C8 (84) | 4.14 | 0.69 | 3.68 | 4.65 | 4.49 | 6.88 | 5.20 | 1.75 | 0.12 | 3.24 | 2.45 | 1.46 |
| dev / bass A0-B2 (44) | 5.42 | 1.16 | 1.05 | 5.07 | 4.12 | 3.79 | 5.06 | 1.43 | 0.07 | 2.74 | 4.15 | 1.20 |
| dev / middle C3-B5 (68) | 6.54 | 0.65 | 2.60 | 4.64 | 4.96 | 5.83 | 5.79 | 3.65 | 0.12 | 2.13 | 5.40 | 0.76 |
| dev / treble C6-C8 (44) | 3.75 | 1.69 | 3.08 | 4.80 | 4.26 | 6.02 | 5.02 | 1.54 | 0.19 | 3.37 | 2.46 | 1.42 |

## string energy

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.54 | 0.25 | 1.84 | 4.44 | 4.26 | 4.66 | 5.72 | 0.92 | 0.06 | 1.96 | 3.95 | 0.50 |
| dev (156) | 5.39 | 1.15 | 2.32 | 4.78 | 4.55 | 5.35 | 5.33 | 2.44 | 0.12 | 2.66 | 4.76 | 0.96 |
| train / bass A0-B2 (84) | 4.68 | 0.04 | 0.44 | 4.75 | 3.96 | 3.76 | 5.51 | 0.42 | 0.03 | 2.12 | 5.52 | 0.40 |
| train / middle C3-B5 (108) | 4.90 | 0.07 | 1.44 | 4.02 | 4.11 | 3.49 | 6.10 | 0.70 | 0.04 | 0.83 | 3.60 | 0.27 |
| train / treble C6-C8 (84) | 3.92 | 0.69 | 3.88 | 4.68 | 4.74 | 7.07 | 5.41 | 1.76 | 0.13 | 3.27 | 2.84 | 0.90 |
| dev / bass A0-B2 (44) | 5.44 | 1.16 | 1.05 | 5.07 | 4.13 | 3.80 | 4.83 | 1.43 | 0.07 | 2.72 | 6.13 | 1.22 |
| dev / middle C3-B5 (68) | 6.46 | 0.65 | 2.58 | 4.63 | 4.93 | 5.83 | 5.81 | 3.65 | 0.12 | 2.13 | 5.37 | 0.76 |
| dev / treble C6-C8 (44) | 3.70 | 1.94 | 3.21 | 4.73 | 4.38 | 6.15 | 5.09 | 1.55 | 0.19 | 3.43 | 2.43 | 1.01 |

## Regressions

Every note and role where string energy is worse than round 7 (8a530bf) by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | round 7 (8a530bf) | string energy |
|---|---|---|---|---|
| 27 | dev | rise_ms | 1.83 | 7.98 |
| 108 | dev | early_db | 6.87 | 8.15 |
| 108 | train | early_db | 7.28 | 8.45 |
| 108 | dev | noise_db | 8.22 | 9.38 |
| 108 | train | noise_db | 8.66 | 9.72 |
| 108 | dev | sustain_db | 15.27 | 16.21 |
| 108 | train | sustain_db | 16.18 | 17.01 |
| 108 | dev | attack_db | 6.92 | 7.75 |
| 33 | train | noise_db | 6.02 | 6.75 |
| 108 | train | attack_db | 7.47 | 8.18 |
| 105 | train | rise_ms | 2.96 | 4.37 |
| 105 | dev | rise_ms | 2.33 | 3.71 |
| 108 | train | rise_ms | 1.55 | 2.85 |
| 108 | dev | rise_ms | 1.29 | 2.58 |
| 93 | dev | tuning_cents | 0.12 | 0.76 |
| 99 | dev | tuning_cents | 3.48 | 4.04 |
| 33 | train | rise_ms | 2.10 | 3.14 |
