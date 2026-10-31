# Recording benchmark: the hamburg piano's own data against the Kakegawa grand's data

Every train and dev note of `Tools/corpus/split-hamburg-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## the Kakegawa grand's data

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev (8) | 6.38 | 2.06 | 3.03 | 9.01 | 8.95 | 10.92 | 10.13 | 5.00 | 0.19 | 4.82 | 11.97 | 3.71 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 6.38 | 2.06 | 3.03 | 9.01 | 8.95 | 10.92 | 10.13 | 5.00 | 0.19 | 4.82 | 11.97 | 3.71 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## the hamburg piano's own data

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev (8) | 7.32 | 0.56 | 6.14 | 6.47 | 5.78 | 7.32 | 5.39 | 4.17 | 0.21 | 4.39 | 3.87 | 1.78 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.32 | 0.56 | 6.14 | 6.47 | 5.78 | 7.32 | 5.39 | 4.17 | 0.21 | 4.39 | 3.87 | 1.78 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## Regressions

Every note and role where the hamburg piano's own data is worse than the Kakegawa grand's data by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | the Kakegawa grand's data | the hamburg piano's own data |
|---|---|---|---|---|
| 73 | dev | decay_db_s | 3.93 | 8.97 |
| 52 | dev | partial_db | 7.19 | 8.79 |
| 73 | dev | icc | 0.16 | 0.20 |
| 52 | dev | rise_ms | 4.68 | 6.46 |
| 52 | dev | decay_db_s | 2.12 | 3.31 |
