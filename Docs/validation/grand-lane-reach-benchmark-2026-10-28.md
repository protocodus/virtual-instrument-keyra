# Recording benchmark: candidate 0.4.1 against 0.4.1 at 3c65822

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at 3c65822

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

## candidate 0.4.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 1.69 | 0.26 | 1.68 | 3.78 | 3.07 | 3.68 | 5.56 | 0.91 | 0.06 | 1.89 | 3.82 | 0.54 |
| dev (156) | 3.20 | 1.11 | 2.24 | 4.22 | 3.79 | 4.65 | 5.65 | 2.55 | 0.12 | 2.55 | 4.90 | 1.29 |
| train / bass A0-B2 (84) | 0.51 | 0.04 | 0.39 | 3.37 | 1.65 | 1.31 | 5.50 | 0.36 | 0.03 | 1.95 | 4.48 | 0.15 |
| train / middle C3-B5 (108) | 1.31 | 0.07 | 1.30 | 2.97 | 2.39 | 2.06 | 5.59 | 0.70 | 0.04 | 0.69 | 4.31 | 0.19 |
| train / treble C6-C8 (84) | 3.36 | 0.72 | 3.56 | 5.23 | 5.36 | 8.13 | 5.57 | 1.78 | 0.13 | 3.39 | 2.54 | 1.38 |
| dev / bass A0-B2 (44) | 2.33 | 1.14 | 0.89 | 3.95 | 2.76 | 2.23 | 5.83 | 1.31 | 0.07 | 2.69 | 4.74 | 1.17 |
| dev / middle C3-B5 (68) | 3.54 | 0.61 | 2.44 | 3.73 | 3.55 | 4.61 | 5.79 | 3.92 | 0.12 | 1.82 | 5.92 | 1.13 |
| dev / treble C6-C8 (44) | 3.55 | 1.86 | 3.29 | 5.24 | 5.19 | 7.15 | 5.26 | 1.62 | 0.19 | 3.54 | 3.51 | 1.63 |

## Regressions

Every note and role where candidate 0.4.1 is worse than 0.4.1 at 3c65822 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.1 at 3c65822 | candidate 0.4.1 |
|---|---|---|---|---|
| 90 | dev | envelope_db | 2.24 | 5.71 |
| 90 | train | envelope_db | 2.16 | 5.29 |
| 90 | dev | sustain_db | 5.35 | 7.54 |
| 90 | train | sustain_db | 4.84 | 7.00 |
| 99 | dev | tuning_cents | 2.19 | 3.92 |
| 96 | dev | level_db | 0.81 | 1.65 |
| 84 | dev | rise_ms | 3.36 | 5.02 |
| 96 | train | ild_db | 0.31 | 1.09 |
| 81 | train | partial_db | 2.03 | 2.80 |
| 96 | dev | ild_db | 0.27 | 1.00 |
| 90 | dev | partial_db | 1.38 | 2.08 |
| 96 | train | envelope_db | 1.64 | 2.27 |
| 90 | train | partial_db | 1.75 | 2.37 |
| 81 | dev | partial_db | 2.44 | 3.04 |
| 96 | dev | envelope_db | 1.74 | 2.27 |
| 99 | dev | icc | 0.26 | 0.28 |
| 102 | train | rise_ms | 2.59 | 3.60 |
