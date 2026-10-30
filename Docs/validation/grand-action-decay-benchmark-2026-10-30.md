# Recording benchmark: candidate 0.4.1 against 0.4.1 at e9411bb

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at e9411bb

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.63 | 0.25 | 1.78 | 4.50 | 4.25 | 4.62 | 5.70 | 0.92 | 0.06 | 1.96 | 3.88 | 0.65 |
| dev (156) | 5.44 | 1.06 | 2.31 | 4.83 | 4.62 | 5.27 | 5.41 | 2.57 | 0.12 | 2.58 | 4.31 | 1.14 |
| train / bass A0-B2 (84) | 4.65 | 0.04 | 0.44 | 4.76 | 3.95 | 3.74 | 5.45 | 0.43 | 0.03 | 2.12 | 5.74 | 0.43 |
| train / middle C3-B5 (108) | 4.97 | 0.07 | 1.46 | 4.11 | 4.19 | 3.50 | 6.15 | 0.71 | 0.04 | 0.83 | 3.49 | 0.29 |
| train / treble C6-C8 (84) | 4.16 | 0.69 | 3.66 | 4.73 | 4.63 | 6.95 | 5.33 | 1.75 | 0.12 | 3.27 | 2.51 | 1.34 |
| dev / bass A0-B2 (44) | 5.33 | 1.11 | 0.90 | 5.06 | 4.14 | 3.74 | 4.98 | 1.38 | 0.07 | 2.81 | 4.15 | 1.22 |
| dev / middle C3-B5 (68) | 6.52 | 0.61 | 2.58 | 4.63 | 4.94 | 5.67 | 5.74 | 3.92 | 0.12 | 1.91 | 5.57 | 0.95 |
| dev / treble C6-C8 (44) | 3.87 | 1.73 | 3.36 | 4.91 | 4.60 | 6.16 | 5.32 | 1.62 | 0.18 | 3.38 | 2.53 | 1.36 |

## candidate 0.4.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.62 | 0.25 | 1.79 | 4.48 | 4.16 | 4.60 | 5.63 | 0.92 | 0.06 | 1.95 | 3.84 | 0.69 |
| dev (156) | 5.44 | 1.07 | 2.31 | 4.83 | 4.52 | 5.26 | 5.38 | 2.56 | 0.12 | 2.57 | 4.33 | 1.16 |
| train / bass A0-B2 (84) | 4.65 | 0.04 | 0.44 | 4.76 | 3.96 | 3.74 | 5.47 | 0.43 | 0.03 | 2.12 | 5.55 | 0.43 |
| train / middle C3-B5 (108) | 4.97 | 0.07 | 1.46 | 4.06 | 4.12 | 3.50 | 6.09 | 0.71 | 0.04 | 0.83 | 3.56 | 0.29 |
| train / treble C6-C8 (84) | 4.14 | 0.69 | 3.68 | 4.74 | 4.41 | 6.88 | 5.19 | 1.74 | 0.12 | 3.24 | 2.50 | 1.46 |
| dev / bass A0-B2 (44) | 5.33 | 1.11 | 0.90 | 5.06 | 4.14 | 3.74 | 5.07 | 1.38 | 0.07 | 2.81 | 4.14 | 1.22 |
| dev / middle C3-B5 (68) | 6.52 | 0.61 | 2.58 | 4.64 | 4.93 | 5.68 | 5.78 | 3.92 | 0.12 | 1.91 | 5.63 | 0.95 |
| dev / treble C6-C8 (44) | 3.87 | 1.73 | 3.36 | 4.89 | 4.28 | 6.13 | 5.07 | 1.60 | 0.18 | 3.37 | 2.53 | 1.42 |

## Regressions

Every note and role where candidate 0.4.1 is worse than 0.4.1 at e9411bb by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.1 at e9411bb | candidate 0.4.1 |
|---|---|---|---|---|
| 30 | dev | noise_db | 3.81 | 4.70 |
| 57 | dev | rise_ms | 0.69 | 2.29 |
| 57 | train | rise_ms | 0.94 | 2.49 |
| 108 | train | early_db | 6.27 | 6.94 |
| 108 | dev | early_db | 5.88 | 6.53 |
| 108 | train | noise_db | 7.87 | 8.46 |
| 108 | dev | noise_db | 7.49 | 8.02 |
| 108 | dev | partial_db | 9.54 | 10.05 |
