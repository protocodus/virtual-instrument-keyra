# Recording benchmark: candidate 0.4.1 against 0.4.1 at 98c6740

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at 98c6740

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 1.69 | 0.26 | 1.68 | 3.78 | 3.07 | 3.68 | 6.90 | 0.91 | 0.06 | 1.89 | 3.82 | 0.54 |
| dev (156) | 3.13 | 1.10 | 2.25 | 4.17 | 3.68 | 4.58 | 6.31 | 2.56 | 0.12 | 2.52 | 4.54 | 1.10 |
| train / bass A0-B2 (84) | 0.51 | 0.04 | 0.39 | 3.37 | 1.65 | 1.31 | 8.73 | 0.36 | 0.03 | 1.95 | 4.48 | 0.15 |
| train / middle C3-B5 (108) | 1.31 | 0.07 | 1.30 | 2.97 | 2.39 | 2.06 | 6.25 | 0.70 | 0.04 | 0.69 | 4.31 | 0.19 |
| train / treble C6-C8 (84) | 3.36 | 0.72 | 3.56 | 5.23 | 5.36 | 8.13 | 5.92 | 1.78 | 0.13 | 3.39 | 2.54 | 1.38 |
| dev / bass A0-B2 (44) | 2.23 | 1.10 | 0.89 | 3.98 | 2.62 | 2.07 | 7.64 | 1.38 | 0.07 | 2.58 | 3.12 | 1.03 |
| dev / middle C3-B5 (68) | 3.38 | 0.61 | 2.43 | 3.64 | 3.40 | 4.52 | 5.85 | 3.92 | 0.12 | 1.82 | 6.09 | 0.95 |
| dev / treble C6-C8 (44) | 3.66 | 1.86 | 3.34 | 5.18 | 5.18 | 7.17 | 5.68 | 1.61 | 0.19 | 3.54 | 3.56 | 1.43 |

## candidate 0.4.1

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

## Regressions

Every note and role where candidate 0.4.1 is worse than 0.4.1 at 98c6740 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.1 at 98c6740 | candidate 0.4.1 |
|---|---|---|---|---|
| 102 | dev | rise_ms | 3.55 | 5.86 |
| 102 | train | rise_ms | 3.60 | 5.66 |
