# Recording benchmark: candidate 0.4.1 against shipping 0.4.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## shipping 0.4.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 1.66 | 0.27 | 1.76 | 3.77 | 3.06 | 3.62 | 5.54 | 0.89 | 0.06 | 1.77 | 3.83 | 0.55 |
| dev (156) | 3.16 | 1.06 | 2.56 | 4.19 | 3.78 | 4.74 | 5.63 | 2.59 | 0.12 | 2.51 | 4.92 | 1.22 |
| train / bass A0-B2 (84) | 0.52 | 0.04 | 0.40 | 3.36 | 1.66 | 1.32 | 5.50 | 0.36 | 0.03 | 1.95 | 4.49 | 0.15 |
| train / middle C3-B5 (108) | 1.23 | 0.07 | 1.25 | 2.97 | 2.39 | 2.04 | 5.58 | 0.74 | 0.05 | 0.69 | 4.41 | 0.19 |
| train / treble C6-C8 (84) | 3.35 | 0.76 | 3.90 | 5.22 | 5.33 | 7.96 | 5.53 | 1.67 | 0.13 | 2.99 | 2.43 | 1.41 |
| dev / bass A0-B2 (44) | 2.34 | 1.14 | 0.89 | 3.95 | 2.76 | 2.23 | 5.81 | 1.31 | 0.07 | 2.69 | 4.75 | 1.17 |
| dev / middle C3-B5 (68) | 3.48 | 0.60 | 2.42 | 3.74 | 3.55 | 4.60 | 5.78 | 3.92 | 0.12 | 1.82 | 5.95 | 1.13 |
| dev / treble C6-C8 (44) | 3.49 | 1.68 | 4.51 | 5.12 | 5.16 | 7.48 | 5.22 | 1.78 | 0.18 | 3.39 | 3.51 | 1.41 |

## candidate 0.4.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 1.65 | 0.27 | 1.73 | 3.78 | 3.06 | 3.59 | 5.55 | 0.86 | 0.06 | 1.72 | 3.84 | 0.54 |
| dev (156) | 3.17 | 0.94 | 2.56 | 4.21 | 3.79 | 4.69 | 5.63 | 2.63 | 0.12 | 2.51 | 4.89 | 1.24 |
| train / bass A0-B2 (84) | 0.52 | 0.04 | 0.40 | 3.36 | 1.66 | 1.32 | 5.50 | 0.36 | 0.03 | 1.95 | 4.49 | 0.15 |
| train / middle C3-B5 (108) | 1.23 | 0.07 | 1.25 | 2.97 | 2.39 | 2.04 | 5.58 | 0.74 | 0.05 | 0.69 | 4.41 | 0.19 |
| train / treble C6-C8 (84) | 3.33 | 0.76 | 3.82 | 5.25 | 5.32 | 7.86 | 5.56 | 1.57 | 0.13 | 2.82 | 2.47 | 1.38 |
| dev / bass A0-B2 (44) | 2.34 | 1.14 | 0.89 | 3.95 | 2.76 | 2.23 | 5.81 | 1.31 | 0.07 | 2.69 | 4.75 | 1.17 |
| dev / middle C3-B5 (68) | 3.48 | 0.60 | 2.42 | 3.74 | 3.55 | 4.60 | 5.78 | 3.92 | 0.12 | 1.82 | 5.95 | 1.13 |
| dev / treble C6-C8 (44) | 3.52 | 1.26 | 4.48 | 5.20 | 5.19 | 7.30 | 5.23 | 1.93 | 0.18 | 3.42 | 3.39 | 1.47 |

## Regressions

Every note and role where candidate 0.4.1 is worse than shipping 0.4.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | shipping 0.4.0 | candidate 0.4.1 |
|---|---|---|---|---|
| 99 | dev | ild_db | 2.18 | 2.69 |
