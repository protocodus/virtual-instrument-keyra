# Recording benchmark: window against shipping

Every train and dev note of `Tools/corpus/split-vcsl-kawai-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## shipping

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev (23) | 9.85 | 2.88 | 5.25 | 8.39 | 9.81 | 9.57 | 8.81 | 5.29 | 0.20 | 4.97 | 4.98 | 4.00 |
| dev / bass A0-B2 (8) | 10.88 | 3.70 | 2.68 | 8.72 | 8.70 | 9.47 | 10.60 | 3.21 | 0.15 | 3.41 | 7.09 | 1.54 |
| dev / middle C3-B5 (12) | 9.26 | 2.25 | 6.26 | 8.12 | 10.06 | 10.02 | 7.68 | 7.75 | 0.17 | 6.18 | 4.16 | 4.83 |
| dev / treble C6-C8 (3) | 9.22 | 3.34 | 9.50 | 8.56 | 11.73 | 7.22 | 8.19 | 0.06 | 0.56 | 4.33 | 2.69 | 7.19 |

## window

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev (23) | 9.88 | 2.87 | 5.24 | 8.23 | 9.45 | 9.51 | 8.77 | 5.28 | 0.20 | 4.91 | 4.99 | 3.96 |
| dev / bass A0-B2 (8) | 10.87 | 3.70 | 2.68 | 8.69 | 8.62 | 9.37 | 10.76 | 3.19 | 0.14 | 3.40 | 7.15 | 1.51 |
| dev / middle C3-B5 (12) | 9.23 | 2.25 | 6.26 | 8.01 | 9.93 | 10.00 | 7.67 | 7.74 | 0.17 | 6.19 | 4.16 | 4.57 |
| dev / treble C6-C8 (3) | 9.88 | 3.32 | 9.37 | 7.88 | 9.73 | 7.11 | 7.47 | 0.08 | 0.56 | 3.82 | 2.55 | 8.10 |

## Regressions

Every note and role where window is worse than shipping by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | shipping | window |
|---|---|---|---|---|
| 102 | dev | level_db | 8.10 | 10.14 |
| 102 | dev | partial_db | 9.22 | 9.88 |
| 83 | dev | level_db | 7.68 | 8.31 |
