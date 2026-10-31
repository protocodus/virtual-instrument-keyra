# Recording benchmark: channel phase from the nearer pitch against 0.4.1 at 39d485a

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at 39d485a

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 5.98 | 0.26 | 2.38 | 5.01 | 4.94 | 5.51 | 6.31 | 2.10 | 0.13 | 2.54 | 8.46 | 0.87 |
| dev (21) | 8.81 | 1.92 | 4.35 | 6.55 | 7.29 | 8.78 | 6.98 | 4.53 | 0.18 | 5.07 | 6.42 | 2.46 |
| train / bass A0-B2 (30) | 7.06 | 0.24 | 1.84 | 5.50 | 5.07 | 5.37 | 8.39 | 1.26 | 0.09 | 2.47 | 12.92 | 0.96 |
| train / middle C3-B5 (69) | 6.76 | 0.19 | 2.62 | 5.10 | 4.76 | 5.46 | 6.11 | 1.90 | 0.10 | 2.16 | 8.71 | 0.44 |
| train / treble C6-C8 (38) | 3.72 | 0.39 | 2.39 | 4.45 | 5.18 | 5.71 | 5.25 | 3.16 | 0.24 | 3.27 | 4.49 | 1.58 |
| dev / bass A0-B2 (5) | 9.37 | 1.33 | 2.02 | 6.22 | 7.38 | 9.31 | 8.52 | 5.00 | 0.20 | 2.48 | 1.51 | 1.10 |
| dev / middle C3-B5 (11) | 8.76 | 1.12 | 3.63 | 6.74 | 7.00 | 8.29 | 6.53 | 4.33 | 0.17 | 5.58 | 10.79 | 2.77 |
| dev / treble C6-C8 (5) | 8.37 | 4.24 | 8.25 | 6.46 | 7.82 | 9.31 | 6.74 | 4.53 | 0.20 | 6.55 | 1.71 | 3.14 |

## channel phase from the nearer pitch

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 5.98 | 0.26 | 2.38 | 5.01 | 4.94 | 5.51 | 6.31 | 2.10 | 0.13 | 2.54 | 8.46 | 0.87 |
| dev (21) | 8.78 | 1.87 | 4.47 | 6.44 | 7.32 | 8.80 | 6.98 | 4.26 | 0.21 | 4.95 | 6.02 | 2.46 |
| train / bass A0-B2 (30) | 7.06 | 0.24 | 1.84 | 5.50 | 5.07 | 5.37 | 8.39 | 1.26 | 0.09 | 2.47 | 12.92 | 0.96 |
| train / middle C3-B5 (69) | 6.76 | 0.19 | 2.62 | 5.10 | 4.76 | 5.46 | 6.11 | 1.90 | 0.10 | 2.16 | 8.71 | 0.43 |
| train / treble C6-C8 (38) | 3.72 | 0.39 | 2.39 | 4.45 | 5.18 | 5.71 | 5.25 | 3.16 | 0.24 | 3.27 | 4.49 | 1.58 |
| dev / bass A0-B2 (5) | 9.42 | 1.36 | 2.01 | 5.83 | 7.44 | 9.40 | 8.55 | 5.12 | 0.22 | 2.49 | 1.93 | 1.04 |
| dev / middle C3-B5 (11) | 8.65 | 1.13 | 3.68 | 6.76 | 6.94 | 8.16 | 6.54 | 4.16 | 0.18 | 5.11 | 9.86 | 2.80 |
| dev / treble C6-C8 (5) | 8.43 | 4.01 | 8.67 | 6.36 | 8.05 | 9.61 | 6.67 | 3.64 | 0.28 | 7.06 | 1.67 | 3.13 |

## Regressions

Every note and role where channel phase from the nearer pitch is worse than 0.4.1 at 39d485a by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.1 at 39d485a | channel phase from the nearer pitch |
|---|---|---|---|---|
| 88 | dev | icc | 0.20 | 0.28 |
| 39 | dev | icc | 0.20 | 0.22 |
| 88 | dev | envelope_db | 6.55 | 7.06 |
