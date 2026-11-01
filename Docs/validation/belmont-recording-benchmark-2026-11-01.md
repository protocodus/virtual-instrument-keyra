# Recording benchmark: the belmont piano's own data against the Kakegawa grand's data

Every train and dev note of `Tools/corpus/split-belmont-2026-11-01.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## the Kakegawa grand's data

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev (9) | 9.68 | 3.05 | 4.34 | 9.50 | 12.02 | 11.88 | 14.83 | 3.72 | 0.07 | 4.36 | 10.74 | 1.68 |
| dev / bass A0-B2 (3) | 12.07 | 4.86 | 2.86 | 10.30 | 12.72 | 14.47 | 24.68 | 3.43 | 0.15 | 4.44 | 13.95 | 1.37 |
| dev / middle C3-B5 (3) | 6.64 | 1.61 | 4.40 | 9.00 | 9.49 | 7.65 | 9.15 | 4.89 | 0.06 | 2.79 | 15.89 | 0.77 |
| dev / treble C6-C8 (3) | 10.33 | 2.68 | 5.77 | 9.20 | 13.87 | 13.51 | 10.65 | 2.83 | 0.01 | 5.86 | 2.39 | 2.89 |

## the belmont piano's own data

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev (9) | 7.00 | 1.56 | 4.77 | 6.81 | 7.47 | 8.43 | 7.75 | 3.77 | 0.08 | 4.61 | 20.54 | 0.44 |
| dev / bass A0-B2 (3) | 9.86 | 2.56 | 3.75 | 7.44 | 9.92 | 10.72 | 9.25 | 4.25 | 0.15 | 4.72 | 34.59 | 0.16 |
| dev / middle C3-B5 (3) | 6.05 | 1.17 | 4.21 | 6.85 | 7.45 | 8.34 | 8.01 | 3.25 | 0.07 | 3.51 | 21.97 | 0.78 |
| dev / treble C6-C8 (3) | 5.09 | 0.96 | 6.36 | 6.13 | 5.04 | 6.24 | 5.99 | 3.81 | 0.02 | 5.60 | 5.06 | 0.40 |

## Regressions

Every note and role where the belmont piano's own data is worse than the Kakegawa grand's data by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | the Kakegawa grand's data | the belmont piano's own data |
|---|---|---|---|---|
| 39 | dev | rise_ms | 13.95 | 34.59 |
| 63 | dev | rise_ms | 15.89 | 21.97 |
| 87 | dev | rise_ms | 2.39 | 5.06 |
| 87 | dev | ild_db | 2.83 | 3.81 |
| 39 | dev | ild_db | 3.43 | 4.25 |
| 63 | dev | envelope_db | 2.79 | 3.51 |
| 63 | dev | sustain_db | 7.65 | 8.34 |
