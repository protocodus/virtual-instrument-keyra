# Recording benchmark: string energy against round 7 (8a530bf)

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## round 7 (8a530bf)

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 5.98 | 0.26 | 2.38 | 5.01 | 4.94 | 5.51 | 6.31 | 2.10 | 0.13 | 2.54 | 8.46 | 0.87 |
| dev (21) | 8.78 | 1.87 | 4.63 | 6.47 | 7.27 | 8.77 | 6.98 | 4.31 | 0.21 | 4.88 | 6.00 | 2.46 |
| train / bass A0-B2 (30) | 7.06 | 0.24 | 1.84 | 5.50 | 5.07 | 5.37 | 8.39 | 1.26 | 0.09 | 2.47 | 12.92 | 0.96 |
| train / middle C3-B5 (69) | 6.76 | 0.19 | 2.62 | 5.10 | 4.76 | 5.46 | 6.11 | 1.90 | 0.10 | 2.16 | 8.71 | 0.44 |
| train / treble C6-C8 (38) | 3.72 | 0.39 | 2.39 | 4.45 | 5.18 | 5.71 | 5.25 | 3.16 | 0.24 | 3.27 | 4.49 | 1.58 |
| dev / bass A0-B2 (5) | 9.32 | 1.38 | 1.87 | 5.88 | 7.49 | 9.20 | 8.57 | 5.16 | 0.23 | 2.22 | 1.92 | 1.02 |
| dev / middle C3-B5 (11) | 8.67 | 1.09 | 3.74 | 6.79 | 6.87 | 8.20 | 6.55 | 4.24 | 0.17 | 5.11 | 9.83 | 2.81 |
| dev / treble C6-C8 (5) | 8.48 | 4.07 | 9.36 | 6.34 | 7.92 | 9.60 | 6.67 | 3.64 | 0.28 | 7.03 | 1.67 | 3.13 |

## string energy

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 5.76 | 0.26 | 2.34 | 4.92 | 4.87 | 5.47 | 6.24 | 2.09 | 0.13 | 2.55 | 7.77 | 0.51 |
| dev (21) | 8.39 | 1.88 | 4.54 | 6.41 | 7.14 | 8.66 | 7.09 | 4.31 | 0.21 | 4.86 | 6.21 | 2.44 |
| train / bass A0-B2 (30) | 6.90 | 0.24 | 1.78 | 5.55 | 5.07 | 5.34 | 8.61 | 1.26 | 0.09 | 2.49 | 10.76 | 0.83 |
| train / middle C3-B5 (69) | 6.60 | 0.19 | 2.53 | 5.11 | 4.72 | 5.41 | 6.09 | 1.91 | 0.10 | 2.16 | 8.52 | 0.34 |
| train / treble C6-C8 (38) | 3.33 | 0.39 | 2.45 | 4.10 | 4.98 | 5.70 | 4.95 | 3.14 | 0.24 | 3.33 | 4.04 | 0.57 |
| dev / bass A0-B2 (5) | 9.02 | 1.40 | 1.88 | 6.03 | 7.50 | 9.07 | 9.39 | 5.14 | 0.22 | 2.25 | 1.96 | 1.27 |
| dev / middle C3-B5 (11) | 8.40 | 1.09 | 3.71 | 6.73 | 6.77 | 8.09 | 6.50 | 4.24 | 0.17 | 5.11 | 10.19 | 2.68 |
| dev / treble C6-C8 (5) | 7.75 | 4.07 | 9.03 | 6.09 | 7.59 | 9.52 | 6.53 | 3.64 | 0.28 | 6.92 | 1.68 | 3.07 |

## Regressions

Every note and role where string energy is worse than round 7 (8a530bf) by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | round 7 (8a530bf) | string energy |
|---|---|---|---|---|
| 100 | train | sustain_db | 6.89 | 8.06 |
| 39 | dev | noise_db | 8.57 | 9.39 |
| 96 | train | icc | 0.21 | 0.24 |
| 45 | train | noise_db | 4.53 | 5.13 |
| 59 | dev | rise_ms | 4.85 | 5.85 |
