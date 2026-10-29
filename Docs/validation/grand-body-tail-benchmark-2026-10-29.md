# Recording benchmark: candidate 0.4.1 against 0.4.1 at f02e4d5

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at f02e4d5

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 1.65 | 0.26 | 1.71 | 3.65 | 2.74 | 3.55 | 6.66 | 0.89 | 0.06 | 1.88 | 3.74 | 0.58 |
| dev (156) | 3.14 | 1.06 | 2.26 | 4.12 | 3.45 | 4.51 | 6.16 | 2.56 | 0.12 | 2.51 | 4.59 | 1.11 |
| train / bass A0-B2 (84) | 0.50 | 0.04 | 0.39 | 3.21 | 1.64 | 1.31 | 8.27 | 0.35 | 0.02 | 1.95 | 4.57 | 0.14 |
| train / middle C3-B5 (108) | 1.31 | 0.07 | 1.31 | 2.87 | 2.38 | 2.06 | 6.49 | 0.70 | 0.04 | 0.68 | 4.35 | 0.19 |
| train / treble C6-C8 (84) | 3.25 | 0.71 | 3.66 | 5.10 | 4.32 | 7.71 | 5.32 | 1.75 | 0.13 | 3.34 | 2.12 | 1.51 |
| dev / bass A0-B2 (44) | 2.24 | 1.10 | 0.89 | 3.95 | 2.63 | 2.07 | 7.40 | 1.38 | 0.07 | 2.57 | 3.35 | 1.03 |
| dev / middle C3-B5 (68) | 3.38 | 0.61 | 2.43 | 3.62 | 3.43 | 4.52 | 6.01 | 3.92 | 0.12 | 1.82 | 6.23 | 0.94 |
| dev / treble C6-C8 (44) | 3.68 | 1.73 | 3.40 | 5.06 | 4.29 | 6.93 | 5.13 | 1.60 | 0.18 | 3.53 | 3.30 | 1.45 |

## candidate 0.4.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 1.66 | 0.26 | 1.71 | 3.71 | 2.70 | 3.24 | 6.56 | 0.89 | 0.06 | 1.85 | 3.70 | 0.57 |
| dev (156) | 3.14 | 1.05 | 2.26 | 4.14 | 3.39 | 4.24 | 6.11 | 2.56 | 0.12 | 2.46 | 4.45 | 1.11 |
| train / bass A0-B2 (84) | 0.50 | 0.04 | 0.39 | 3.24 | 1.63 | 1.31 | 7.98 | 0.35 | 0.02 | 1.95 | 4.67 | 0.15 |
| train / middle C3-B5 (108) | 1.31 | 0.07 | 1.31 | 2.92 | 2.33 | 2.00 | 6.42 | 0.70 | 0.04 | 0.68 | 4.17 | 0.19 |
| train / treble C6-C8 (84) | 3.26 | 0.71 | 3.65 | 5.21 | 4.26 | 6.76 | 5.39 | 1.74 | 0.12 | 3.25 | 2.14 | 1.50 |
| dev / bass A0-B2 (44) | 2.25 | 1.06 | 0.89 | 3.96 | 2.62 | 2.07 | 7.25 | 1.38 | 0.07 | 2.57 | 3.36 | 1.02 |
| dev / middle C3-B5 (68) | 3.38 | 0.61 | 2.43 | 3.59 | 3.35 | 4.45 | 5.96 | 3.92 | 0.12 | 1.82 | 5.94 | 0.94 |
| dev / treble C6-C8 (44) | 3.67 | 1.73 | 3.40 | 5.17 | 4.21 | 6.09 | 5.20 | 1.60 | 0.18 | 3.35 | 3.24 | 1.45 |

## Regressions

Every note and role where candidate 0.4.1 is worse than 0.4.1 at f02e4d5 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.1 at f02e4d5 | candidate 0.4.1 |
|---|---|---|---|---|
| 30 | dev | rise_ms | 1.81 | 5.30 |
| 69 | train | rise_ms | 3.00 | 5.55 |
| 36 | train | rise_ms | 4.31 | 5.39 |
