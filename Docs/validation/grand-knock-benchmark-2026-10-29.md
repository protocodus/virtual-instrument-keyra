# Recording benchmark: candidate 0.4.1 against 0.4.1 at 39032f0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at 39032f0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 1.69 | 0.26 | 1.68 | 3.80 | 3.10 | 3.68 | 6.92 | 0.91 | 0.06 | 1.90 | 3.91 | 0.54 |
| dev (156) | 3.13 | 1.10 | 2.25 | 4.19 | 3.71 | 4.57 | 6.33 | 2.56 | 0.12 | 2.52 | 4.58 | 1.11 |
| train / bass A0-B2 (84) | 0.51 | 0.04 | 0.39 | 3.37 | 1.65 | 1.31 | 8.73 | 0.36 | 0.03 | 1.95 | 4.48 | 0.15 |
| train / middle C3-B5 (108) | 1.31 | 0.07 | 1.30 | 2.97 | 2.39 | 2.06 | 6.25 | 0.70 | 0.04 | 0.69 | 4.31 | 0.19 |
| train / treble C6-C8 (84) | 3.35 | 0.72 | 3.56 | 5.29 | 5.45 | 8.13 | 6.00 | 1.79 | 0.13 | 3.40 | 2.83 | 1.38 |
| dev / bass A0-B2 (44) | 2.23 | 1.10 | 0.89 | 3.98 | 2.62 | 2.07 | 7.64 | 1.38 | 0.07 | 2.58 | 3.12 | 1.03 |
| dev / middle C3-B5 (68) | 3.38 | 0.61 | 2.43 | 3.64 | 3.40 | 4.52 | 5.85 | 3.92 | 0.12 | 1.82 | 6.09 | 0.95 |
| dev / treble C6-C8 (44) | 3.66 | 1.86 | 3.33 | 5.23 | 5.28 | 7.16 | 5.77 | 1.62 | 0.19 | 3.53 | 3.69 | 1.43 |

## candidate 0.4.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 1.65 | 0.26 | 1.68 | 3.68 | 3.06 | 3.65 | 6.85 | 0.90 | 0.06 | 1.88 | 3.75 | 0.58 |
| dev (156) | 3.13 | 1.10 | 2.25 | 4.14 | 3.71 | 4.57 | 6.31 | 2.56 | 0.12 | 2.52 | 4.58 | 1.12 |
| train / bass A0-B2 (84) | 0.50 | 0.04 | 0.39 | 3.21 | 1.64 | 1.31 | 8.26 | 0.35 | 0.02 | 1.95 | 4.56 | 0.15 |
| train / middle C3-B5 (108) | 1.31 | 0.07 | 1.30 | 2.87 | 2.38 | 2.06 | 6.49 | 0.70 | 0.04 | 0.68 | 4.35 | 0.19 |
| train / treble C6-C8 (84) | 3.23 | 0.72 | 3.58 | 5.18 | 5.37 | 8.03 | 5.92 | 1.77 | 0.13 | 3.37 | 2.17 | 1.53 |
| dev / bass A0-B2 (44) | 2.23 | 1.10 | 0.89 | 3.95 | 2.63 | 2.07 | 7.37 | 1.38 | 0.07 | 2.57 | 3.35 | 1.03 |
| dev / middle C3-B5 (68) | 3.38 | 0.61 | 2.43 | 3.62 | 3.43 | 4.52 | 6.02 | 3.92 | 0.12 | 1.82 | 6.23 | 0.94 |
| dev / treble C6-C8 (44) | 3.65 | 1.86 | 3.34 | 5.13 | 5.24 | 7.15 | 5.69 | 1.61 | 0.19 | 3.56 | 3.25 | 1.48 |

## Regressions

Every note and role where candidate 0.4.1 is worse than 0.4.1 at 39032f0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.1 at 39032f0 | candidate 0.4.1 |
|---|---|---|---|---|
| 48 | dev | rise_ms | 7.27 | 10.73 |
| 54 | train | noise_db | 8.16 | 9.63 |
| 54 | dev | noise_db | 9.05 | 10.45 |
| 42 | dev | rise_ms | 7.51 | 9.96 |
| 57 | train | noise_db | 7.44 | 8.56 |
| 57 | dev | noise_db | 6.62 | 7.46 |
| 108 | train | level_db | 3.05 | 3.88 |
| 60 | train | noise_db | 6.03 | 6.70 |
| 60 | dev | noise_db | 6.15 | 6.69 |
