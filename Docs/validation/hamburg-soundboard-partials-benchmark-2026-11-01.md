# Recording benchmark: candidate 0.4.1 against 0.4.1 at d5e467d

Every train and dev note of `Tools/corpus/split-hamburg-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at d5e467d

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (40) | 4.60 | 0.28 | 3.30 | 5.83 | 3.95 | 5.33 | 6.05 | 1.37 | 0.11 | 2.97 | 17.17 | 0.61 |
| dev (8) | 7.32 | 0.56 | 6.14 | 6.47 | 5.78 | 7.32 | 5.39 | 4.17 | 0.21 | 4.39 | 3.87 | 1.88 |
| train / bass A0-B2 (16) | 4.72 | 0.09 | 0.97 | 6.65 | 3.76 | 3.71 | 7.69 | 0.76 | 0.06 | 2.41 | 32.40 | 0.60 |
| train / middle C3-B5 (12) | 4.63 | 0.24 | 2.20 | 5.96 | 4.14 | 5.37 | 5.68 | 1.79 | 0.13 | 1.89 | 11.68 | 0.20 |
| train / treble C6-C8 (12) | 4.39 | 0.59 | 7.50 | 4.62 | 4.03 | 7.46 | 4.64 | 1.74 | 0.18 | 4.81 | 2.36 | 1.03 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.32 | 0.56 | 6.14 | 6.47 | 5.78 | 7.32 | 5.39 | 4.17 | 0.21 | 4.39 | 3.87 | 1.88 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## candidate 0.4.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (40) | 4.58 | 0.28 | 3.30 | 6.00 | 4.77 | 5.25 | 6.76 | 1.54 | 0.12 | 3.17 | 17.34 | 0.64 |
| dev (8) | 7.28 | 0.62 | 6.13 | 6.82 | 6.64 | 7.36 | 6.12 | 4.24 | 0.21 | 4.44 | 3.77 | 1.88 |
| train / bass A0-B2 (16) | 4.69 | 0.09 | 0.97 | 6.57 | 3.85 | 3.73 | 7.71 | 0.89 | 0.06 | 2.39 | 32.18 | 0.59 |
| train / middle C3-B5 (12) | 4.63 | 0.24 | 2.20 | 6.33 | 5.51 | 5.65 | 7.39 | 1.92 | 0.12 | 1.94 | 12.44 | 0.22 |
| train / treble C6-C8 (12) | 4.37 | 0.59 | 7.50 | 4.92 | 5.27 | 6.87 | 5.10 | 2.02 | 0.18 | 5.44 | 2.44 | 1.13 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.28 | 0.62 | 6.13 | 6.82 | 6.64 | 7.36 | 6.12 | 4.24 | 0.21 | 4.44 | 3.77 | 1.88 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## Regressions

Every note and role where candidate 0.4.1 is worse than 0.4.1 at d5e467d by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.1 at d5e467d | candidate 0.4.1 |
|---|---|---|---|---|
| 59 | train | noise_db | 5.58 | 8.64 |
| 59 | train | early_db | 3.72 | 5.44 |
| 66 | train | early_db | 4.17 | 5.54 |
| 94 | train | early_db | 4.07 | 5.43 |
| 87 | train | early_db | 4.22 | 5.55 |
| 66 | train | noise_db | 6.17 | 7.49 |
| 52 | dev | early_db | 5.91 | 7.04 |
| 73 | dev | noise_db | 6.29 | 7.40 |
| 101 | train | early_db | 3.79 | 4.82 |
| 80 | train | early_db | 4.54 | 5.54 |
| 94 | train | envelope_db | 4.35 | 5.22 |
| 59 | train | rise_ms | 2.03 | 3.76 |
| 101 | train | envelope_db | 3.49 | 4.31 |
| 101 | train | icc | 0.22 | 0.25 |
| 59 | train | attack_db | 5.47 | 6.23 |
| 80 | train | noise_db | 5.29 | 6.03 |
| 87 | train | noise_db | 4.97 | 5.58 |
| 73 | dev | early_db | 5.65 | 6.25 |
| 52 | dev | attack_db | 6.13 | 6.71 |
| 101 | train | attack_db | 4.38 | 4.94 |
