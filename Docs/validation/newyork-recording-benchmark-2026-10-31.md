# Recording benchmark: the newyork piano's own data against the Kakegawa grand's data

Every train and dev note of `Tools/corpus/split-newyork-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## the Kakegawa grand's data

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev (17) | 12.88 | 5.75 | 6.78 | 9.34 | 8.70 | 10.27 | 10.23 | 7.42 | 0.21 | 4.55 | 9.99 | 4.59 |
| dev / bass A0-B2 (5) | 13.57 | 4.63 | 4.17 | 10.49 | 9.93 | 9.56 | 19.09 | 5.92 | 0.16 | 2.38 | 15.32 | 5.28 |
| dev / middle C3-B5 (5) | 11.37 | 6.88 | 5.21 | 8.81 | 6.97 | 9.46 | 6.04 | 4.67 | 0.19 | 4.05 | 8.69 | 2.86 |
| dev / treble C6-C8 (7) | 13.48 | 5.74 | 9.76 | 8.89 | 9.04 | 11.36 | 6.91 | 10.45 | 0.24 | 6.45 | 7.10 | 5.34 |

## the newyork piano's own data

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev (17) | 9.94 | 2.37 | 7.75 | 8.72 | 7.88 | 9.13 | 8.91 | 6.25 | 0.19 | 3.60 | 8.51 | 2.18 |
| dev / bass A0-B2 (5) | 10.68 | 3.74 | 3.68 | 9.38 | 8.19 | 8.32 | 12.09 | 3.79 | 0.11 | 2.37 | 7.46 | 1.36 |
| dev / middle C3-B5 (5) | 9.41 | 1.04 | 6.98 | 7.75 | 7.66 | 9.68 | 7.47 | 6.21 | 0.15 | 3.70 | 10.10 | 1.57 |
| dev / treble C6-C8 (7) | 9.79 | 2.34 | 11.21 | 8.94 | 7.80 | 9.32 | 7.66 | 8.04 | 0.27 | 4.42 | 8.13 | 3.22 |

## Regressions

Every note and role where the newyork piano's own data is worse than the Kakegawa grand's data by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | the Kakegawa grand's data | the newyork piano's own data |
|---|---|---|---|---|
| 105 | dev | decay_db_s | 5.54 | 29.05 |
| 105 | dev | tuning_cents | 0.93 | 4.03 |
| 105 | dev | icc | 0.43 | 0.52 |
| 84 | dev | noise_db | 6.10 | 8.09 |
| 64 | dev | ild_db | 4.67 | 6.21 |
| 64 | dev | noise_db | 6.04 | 7.47 |
| 100 | dev | rise_ms | 1.98 | 4.73 |
| 84 | dev | rise_ms | 7.35 | 9.95 |
| 84 | dev | attack_db | 8.33 | 9.31 |
| 64 | dev | decay_db_s | 5.21 | 6.98 |
| 84 | dev | icc | 0.20 | 0.24 |
| 64 | dev | rise_ms | 8.69 | 10.10 |
| 64 | dev | early_db | 6.97 | 7.66 |
