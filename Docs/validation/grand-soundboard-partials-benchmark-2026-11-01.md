# Recording benchmark: candidate 0.4.1 against 0.4.1 at d5e467d

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at d5e467d

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.54 | 0.25 | 1.84 | 4.44 | 4.26 | 4.66 | 5.72 | 0.92 | 0.06 | 1.96 | 3.95 | 0.50 |
| dev (156) | 5.33 | 1.15 | 2.32 | 4.79 | 4.52 | 5.31 | 5.34 | 2.44 | 0.12 | 2.65 | 4.61 | 1.03 |
| train / bass A0-B2 (84) | 4.68 | 0.04 | 0.44 | 4.75 | 3.96 | 3.76 | 5.51 | 0.42 | 0.03 | 2.12 | 5.52 | 0.40 |
| train / middle C3-B5 (108) | 4.90 | 0.07 | 1.44 | 4.02 | 4.11 | 3.49 | 6.10 | 0.70 | 0.04 | 0.83 | 3.60 | 0.28 |
| train / treble C6-C8 (84) | 3.92 | 0.69 | 3.88 | 4.68 | 4.74 | 7.07 | 5.41 | 1.76 | 0.13 | 3.27 | 2.84 | 0.90 |
| dev / bass A0-B2 (44) | 5.41 | 1.15 | 1.05 | 5.09 | 4.10 | 3.76 | 4.83 | 1.42 | 0.07 | 2.72 | 5.70 | 1.26 |
| dev / middle C3-B5 (68) | 6.42 | 0.65 | 2.60 | 4.61 | 4.88 | 5.78 | 5.82 | 3.64 | 0.12 | 2.12 | 5.36 | 0.82 |
| dev / treble C6-C8 (44) | 3.57 | 1.94 | 3.19 | 4.78 | 4.39 | 6.14 | 5.12 | 1.56 | 0.19 | 3.42 | 2.36 | 1.13 |

## candidate 0.4.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.54 | 0.25 | 1.84 | 4.42 | 4.24 | 4.65 | 5.69 | 0.90 | 0.06 | 1.96 | 3.26 | 0.50 |
| dev (156) | 5.33 | 1.16 | 2.32 | 4.80 | 4.52 | 5.31 | 5.36 | 2.44 | 0.12 | 2.65 | 3.90 | 1.03 |
| train / bass A0-B2 (84) | 4.70 | 0.04 | 0.44 | 4.79 | 3.96 | 3.75 | 5.52 | 0.40 | 0.03 | 2.12 | 4.08 | 0.40 |
| train / middle C3-B5 (108) | 4.89 | 0.07 | 1.44 | 4.01 | 4.08 | 3.48 | 6.06 | 0.70 | 0.05 | 0.82 | 3.01 | 0.27 |
| train / treble C6-C8 (84) | 3.92 | 0.70 | 3.88 | 4.57 | 4.71 | 7.06 | 5.38 | 1.73 | 0.12 | 3.27 | 2.78 | 0.90 |
| dev / bass A0-B2 (44) | 5.40 | 1.19 | 1.05 | 5.14 | 4.09 | 3.76 | 4.87 | 1.42 | 0.07 | 2.72 | 3.12 | 1.26 |
| dev / middle C3-B5 (68) | 6.42 | 0.65 | 2.60 | 4.64 | 4.89 | 5.78 | 5.83 | 3.65 | 0.12 | 2.12 | 5.38 | 0.83 |
| dev / treble C6-C8 (44) | 3.57 | 1.94 | 3.19 | 4.69 | 4.39 | 6.13 | 5.12 | 1.56 | 0.19 | 3.42 | 2.39 | 1.13 |

## Regressions

Every note and role where candidate 0.4.1 is worse than 0.4.1 at d5e467d by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.1 at d5e467d | candidate 0.4.1 |
|---|---|---|---|---|
| 54 | train | rise_ms | 0.55 | 4.70 |
| 36 | train | rise_ms | 4.41 | 8.41 |
| 54 | dev | rise_ms | 0.32 | 4.12 |
| 33 | dev | rise_ms | 2.55 | 6.05 |
| 36 | dev | rise_ms | 4.05 | 5.95 |
| 69 | dev | rise_ms | 2.37 | 3.93 |
| 45 | dev | noise_db | 5.81 | 6.54 |
| 45 | train | noise_db | 7.11 | 7.65 |
