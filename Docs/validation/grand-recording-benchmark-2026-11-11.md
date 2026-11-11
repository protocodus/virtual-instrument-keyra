# Recording benchmark: physical model 2.0.0 against shipping 1.0.0

> Added by hand, 2026-11-11: the roles are 1.0.0's. Its modal engine was fitted to the train recordings; the physical model of 2.0.0 is fitted to neither role, so both of its rows are held-out scores. The decision this report belongs to is in [`decisions.md`](../decisions.md), 2026-11-11.

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## shipping 1.0.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.50 | 0.17 | 1.85 | 4.29 | 4.01 | 4.60 | 5.65 | 1.54 | 0.06 | 1.94 | 3.67 | 1.05 |
| dev (156) | 5.28 | 0.91 | 2.09 | 4.65 | 4.41 | 5.31 | 5.27 | 2.64 | 0.10 | 2.63 | 4.50 | 1.11 |
| train / bass A0-B2 (84) | 4.74 | 0.04 | 0.44 | 4.56 | 3.87 | 3.70 | 5.91 | 0.76 | 0.03 | 1.80 | 4.11 | 0.89 |
| train / middle C3-B5 (108) | 4.68 | 0.08 | 1.47 | 3.87 | 3.84 | 3.46 | 5.87 | 2.28 | 0.05 | 0.97 | 4.21 | 1.03 |
| train / treble C6-C8 (84) | 4.03 | 0.41 | 3.88 | 4.55 | 4.36 | 6.98 | 5.14 | 1.38 | 0.10 | 3.32 | 2.52 | 1.25 |
| dev / bass A0-B2 (44) | 5.49 | 1.26 | 1.09 | 4.82 | 4.02 | 3.88 | 5.11 | 1.53 | 0.05 | 2.65 | 4.67 | 1.02 |
| dev / middle C3-B5 (68) | 6.19 | 0.65 | 2.49 | 4.50 | 4.66 | 5.59 | 5.44 | 4.37 | 0.11 | 1.96 | 6.01 | 1.15 |
| dev / treble C6-C8 (44) | 3.66 | 0.95 | 2.48 | 4.72 | 4.43 | 6.32 | 5.16 | 1.02 | 0.15 | 3.63 | 2.01 | 1.15 |

## physical model 2.0.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 12.02 | 2.85 | 6.65 | 9.39 | 10.18 | 11.46 | 10.95 | 5.69 | 0.22 | 4.89 | 16.10 | 4.91 |
| dev (156) | 11.70 | 3.09 | 5.48 | 9.50 | 10.04 | 10.87 | 10.62 | 5.42 | 0.21 | 4.81 | 15.47 | 4.47 |
| train / bass A0-B2 (84) | 10.58 | 3.06 | 2.68 | 5.84 | 5.86 | 6.93 | 7.98 | 4.49 | 0.19 | 3.95 | 25.01 | 3.49 |
| train / middle C3-B5 (108) | 9.73 | 2.65 | 4.07 | 8.67 | 8.92 | 8.96 | 9.20 | 7.64 | 0.24 | 4.45 | 17.71 | 5.81 |
| train / treble C6-C8 (84) | 16.41 | 2.90 | 14.41 | 13.88 | 16.13 | 19.19 | 15.95 | 4.27 | 0.22 | 6.39 | 5.11 | 5.18 |
| dev / bass A0-B2 (44) | 11.03 | 3.57 | 2.44 | 6.50 | 6.50 | 6.83 | 7.48 | 4.75 | 0.21 | 3.49 | 31.65 | 3.36 |
| dev / middle C3-B5 (68) | 9.25 | 2.39 | 3.36 | 8.44 | 8.37 | 8.17 | 8.79 | 7.42 | 0.19 | 4.78 | 12.65 | 4.91 |
| dev / treble C6-C8 (44) | 16.14 | 3.68 | 11.95 | 14.14 | 16.18 | 19.09 | 16.42 | 2.89 | 0.25 | 6.16 | 3.66 | 4.90 |

## Independent-sample regressions (legacy)

Every note and role where physical model 2.0.0 is worse than shipping 1.0.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | shipping 1.0.0 | physical model 2.0.0 |
|---|---|---|---|---|
| 30 | dev | rise_ms | 1.78 | 69.97 |
| 30 | train | rise_ms | 2.28 | 69.63 |
| 21 | dev | rise_ms | 2.05 | 48.21 |
| 21 | train | rise_ms | 1.94 | 46.74 |
| 105 | dev | partial_db | 3.45 | 25.42 |
| 105 | train | partial_db | 3.16 | 24.91 |
| 54 | train | rise_ms | 4.26 | 45.94 |
| 54 | dev | rise_ms | 4.69 | 45.60 |
| 102 | train | partial_db | 1.96 | 21.57 |
| 27 | dev | rise_ms | 5.59 | 43.71 |
| 102 | dev | partial_db | 1.95 | 20.31 |
| 102 | train | sustain_db | 6.36 | 22.57 |
| 96 | train | sustain_db | 2.63 | 18.49 |
| 96 | dev | sustain_db | 2.70 | 18.35 |
| 102 | dev | sustain_db | 5.47 | 20.95 |
| 102 | train | early_db | 3.31 | 18.56 |
| 105 | dev | sustain_db | 6.68 | 21.33 |
| 99 | dev | partial_db | 2.80 | 17.19 |
| 105 | train | sustain_db | 6.95 | 21.14 |
| 102 | dev | early_db | 3.40 | 17.59 |
| 99 | dev | sustain_db | 5.39 | 19.46 |
| 105 | train | early_db | 3.97 | 17.74 |
| 105 | dev | early_db | 4.10 | 17.32 |
| 105 | train | noise_db | 4.55 | 17.61 |
| 96 | train | partial_db | 1.92 | 14.65 |
| 99 | dev | early_db | 4.61 | 17.30 |
| 102 | train | noise_db | 4.39 | 16.92 |
| 105 | dev | noise_db | 4.77 | 17.28 |
| 102 | dev | noise_db | 4.49 | 16.94 |
| 93 | train | noise_db | 4.47 | 16.85 |
| 93 | dev | noise_db | 4.25 | 16.60 |
| 99 | dev | noise_db | 5.26 | 17.58 |
| 57 | dev | rise_ms | 1.98 | 26.49 |
| 57 | train | rise_ms | 2.41 | 26.60 |
| 96 | dev | partial_db | 1.94 | 14.02 |
| 96 | train | noise_db | 4.35 | 16.43 |
| 108 | train | partial_db | 10.61 | 22.40 |
| 84 | dev | sustain_db | 4.05 | 15.78 |
| 108 | dev | early_db | 6.94 | 18.62 |
| 84 | train | sustain_db | 3.59 | 15.24 |
| 108 | train | early_db | 7.25 | 18.87 |
| 105 | train | decay_db_s | 1.12 | 24.30 |
| 105 | train | attack_db | 4.46 | 16.04 |
| 96 | dev | noise_db | 4.27 | 15.82 |
| 105 | dev | attack_db | 4.53 | 15.95 |
| 102 | train | attack_db | 3.96 | 15.26 |
| 96 | train | early_db | 4.19 | 15.22 |
| 102 | dev | attack_db | 4.29 | 15.22 |
| 90 | train | early_db | 3.71 | 14.59 |
| 93 | train | early_db | 4.29 | 15.09 |
| 93 | train | sustain_db | 5.06 | 15.70 |
| 90 | dev | noise_db | 4.51 | 15.04 |
| 90 | train | noise_db | 4.44 | 14.93 |
| 90 | dev | early_db | 3.84 | 14.18 |
| 108 | dev | partial_db | 11.13 | 21.38 |
| 108 | dev | sustain_db | 16.93 | 27.18 |
| 93 | train | attack_db | 3.81 | 14.05 |
| 105 | dev | decay_db_s | 1.66 | 22.07 |
| 72 | train | attack_db | 4.17 | 14.32 |
| 93 | dev | early_db | 4.19 | 14.32 |
| 96 | dev | early_db | 4.01 | 14.05 |
| 78 | train | attack_db | 3.24 | 13.26 |
| 99 | dev | attack_db | 5.05 | 15.08 |
| 78 | dev | early_db | 3.43 | 13.45 |
| 78 | dev | attack_db | 3.35 | 13.33 |
| 72 | dev | attack_db | 4.21 | 14.10 |
| 93 | dev | attack_db | 3.52 | 13.29 |
| 78 | train | early_db | 3.38 | 13.06 |
| 96 | train | attack_db | 3.76 | 13.28 |
| 93 | dev | sustain_db | 4.85 | 14.35 |
| 72 | train | noise_db | 4.71 | 14.07 |
| 72 | dev | noise_db | 4.59 | 13.76 |
| 96 | dev | attack_db | 3.85 | 12.96 |
| 21 | dev | partial_db | 3.37 | 12.42 |
| 66 | train | rise_ms | 6.88 | 24.96 |
| 84 | train | early_db | 3.81 | 12.83 |
| 108 | train | sustain_db | 17.70 | 26.69 |
| 93 | train | ild_db | 0.69 | 9.68 |
| 93 | dev | ild_db | 0.67 | 9.65 |
| 78 | train | noise_db | 3.95 | 12.86 |
| 84 | dev | early_db | 3.79 | 12.69 |
| 90 | train | attack_db | 3.39 | 12.25 |
| 66 | dev | rise_ms | 5.79 | 23.47 |
| 69 | dev | partial_db | 3.72 | 12.56 |
| 108 | dev | decay_db_s | 5.64 | 23.29 |
| 78 | dev | noise_db | 3.98 | 12.75 |
| 69 | train | partial_db | 4.14 | 12.85 |
| 21 | train | partial_db | 3.69 | 12.37 |
| 90 | dev | attack_db | 3.28 | 11.95 |
| 72 | dev | rise_ms | 1.21 | 18.08 |
| 93 | train | partial_db | 3.75 | 12.15 |
| 72 | train | rise_ms | 1.02 | 17.76 |
| 24 | dev | partial_db | 3.15 | 11.51 |
| 72 | train | early_db | 3.84 | 12.18 |
| 108 | dev | noise_db | 8.51 | 16.72 |
| 54 | dev | level_db | 0.78 | 8.96 |
| 45 | train | rise_ms | 7.89 | 24.18 |
| 45 | dev | rise_ms | 7.77 | 23.87 |
| 54 | train | level_db | 0.92 | 8.96 |
| 54 | dev | partial_db | 5.08 | 13.10 |
| 108 | train | noise_db | 8.81 | 16.78 |
| 90 | train | sustain_db | 6.55 | 14.50 |
| 72 | dev | sustain_db | 3.29 | 11.18 |
| 66 | train | ild_db | 4.53 | 12.38 |
| 72 | dev | early_db | 4.28 | 12.09 |
| 24 | train | partial_db | 3.50 | 11.30 |
| 72 | train | sustain_db | 3.27 | 11.06 |
| 66 | dev | ild_db | 4.54 | 12.28 |
| 57 | dev | partial_db | 4.83 | 12.47 |
| 78 | dev | sustain_db | 2.11 | 9.61 |
| 60 | dev | ild_db | 2.21 | 9.63 |
| 108 | train | decay_db_s | 5.10 | 19.90 |
| 90 | train | partial_db | 3.06 | 10.36 |
| 78 | train | ild_db | 0.50 | 7.78 |
| 108 | train | attack_db | 8.13 | 15.38 |
| 54 | train | partial_db | 5.37 | 12.59 |
| 90 | dev | level_db | 0.53 | 7.74 |
| 84 | train | noise_db | 4.98 | 12.17 |
| 42 | train | noise_db | 4.25 | 11.44 |
| 108 | dev | attack_db | 7.75 | 14.92 |
| 90 | train | level_db | 0.51 | 7.65 |
| 48 | dev | rise_ms | 5.51 | 19.69 |
| 78 | dev | ild_db | 0.62 | 7.71 |
| 72 | train | level_db | 0.24 | 7.32 |
| 84 | dev | noise_db | 4.96 | 11.93 |
| 60 | train | ild_db | 2.63 | 9.56 |
| 90 | dev | sustain_db | 7.27 | 14.17 |
| 66 | dev | icc | 0.03 | 0.30 |
| 42 | dev | noise_db | 5.20 | 11.98 |
| 57 | train | partial_db | 4.78 | 11.55 |
| 69 | dev | sustain_db | 2.05 | 8.82 |
| 78 | train | icc | 0.04 | 0.31 |
| 78 | dev | icc | 0.03 | 0.30 |
| 66 | train | icc | 0.03 | 0.30 |
| 78 | train | sustain_db | 2.23 | 8.92 |
| 96 | dev | decay_db_s | 2.53 | 15.91 |
| 96 | train | decay_db_s | 2.19 | 15.52 |
| 69 | train | sustain_db | 2.15 | 8.82 |
| 93 | train | level_db | 1.17 | 7.81 |
| 72 | dev | level_db | 0.32 | 6.96 |
| 48 | train | rise_ms | 5.99 | 19.18 |
| 93 | dev | partial_db | 3.70 | 10.29 |
| 84 | train | attack_db | 4.36 | 10.93 |
| 36 | dev | partial_db | 4.61 | 11.06 |
| 84 | dev | attack_db | 4.53 | 10.93 |
| 90 | dev | envelope_db | 5.67 | 12.05 |
| 60 | dev | partial_db | 4.20 | 10.48 |
| 93 | dev | level_db | 0.87 | 7.09 |
| 75 | dev | noise_db | 4.70 | 10.86 |
| 30 | train | partial_db | 4.66 | 10.76 |
| 78 | dev | envelope_db | 0.46 | 6.49 |
| 36 | train | partial_db | 4.72 | 10.72 |
| 90 | dev | partial_db | 2.84 | 8.80 |
| 30 | dev | partial_db | 4.56 | 10.50 |
| 72 | dev | ild_db | 0.50 | 6.41 |
| 78 | train | envelope_db | 0.51 | 6.42 |
| 81 | dev | icc | 0.01 | 0.25 |
| 33 | dev | icc | 0.03 | 0.26 |
| 60 | train | partial_db | 4.24 | 10.10 |
| 33 | train | partial_db | 4.80 | 10.60 |
| 57 | dev | sustain_db | 3.16 | 8.93 |
| 48 | dev | level_db | 0.48 | 6.25 |
| 33 | dev | noise_db | 4.98 | 10.70 |
| 93 | train | envelope_db | 4.24 | 9.96 |
| 90 | train | envelope_db | 5.22 | 10.94 |
| 33 | dev | partial_db | 4.68 | 10.39 |
| 75 | dev | attack_db | 5.09 | 10.79 |
| 81 | dev | ild_db | 3.10 | 8.78 |
| 60 | dev | icc | 0.06 | 0.29 |
| 48 | train | level_db | 0.48 | 6.12 |
| 72 | train | ild_db | 0.56 | 6.15 |
| 60 | train | icc | 0.07 | 0.29 |
| 93 | dev | envelope_db | 4.11 | 9.69 |
| 81 | train | icc | 0.03 | 0.25 |
| 33 | train | icc | 0.03 | 0.25 |
| 57 | train | sustain_db | 3.30 | 8.75 |
| 54 | dev | early_db | 3.93 | 9.34 |
| 108 | train | tuning_cents | 0.80 | 6.20 |
| 81 | dev | early_db | 3.55 | 8.90 |
| 48 | train | ild_db | 2.83 | 8.17 |
| 78 | train | level_db | 1.21 | 6.54 |
| 57 | dev | level_db | 1.53 | 6.83 |
| 54 | dev | sustain_db | 3.47 | 8.77 |
| 36 | train | envelope_db | 1.38 | 6.67 |
| 36 | train | sustain_db | 3.43 | 8.71 |
| 36 | dev | sustain_db | 3.38 | 8.65 |
| 60 | dev | sustain_db | 4.58 | 9.83 |
| 69 | train | early_db | 3.64 | 8.87 |
| 36 | dev | envelope_db | 1.51 | 6.73 |
| 102 | train | decay_db_s | 6.95 | 17.35 |
| 48 | dev | ild_db | 2.83 | 8.01 |
| 54 | train | early_db | 3.96 | 9.11 |
| 60 | dev | envelope_db | 1.13 | 6.26 |
| 54 | train | sustain_db | 3.85 | 8.98 |
| 69 | dev | early_db | 3.45 | 8.57 |
| 81 | train | early_db | 3.91 | 9.02 |
| 81 | dev | noise_db | 3.96 | 9.07 |
| 84 | train | partial_db | 3.76 | 8.87 |
| 57 | train | level_db | 1.94 | 7.00 |
| 36 | train | icc | 0.04 | 0.24 |
| 48 | dev | sustain_db | 3.77 | 8.78 |
| 81 | train | noise_db | 4.86 | 9.88 |
| 54 | dev | attack_db | 3.88 | 8.87 |
| 36 | dev | icc | 0.04 | 0.24 |
| 66 | train | partial_db | 5.01 | 9.96 |
| 78 | dev | level_db | 1.40 | 6.33 |
| 48 | train | sustain_db | 3.95 | 8.88 |
| 60 | train | envelope_db | 1.10 | 6.01 |
| 66 | dev | partial_db | 4.91 | 9.82 |
| 108 | dev | tuning_cents | 0.86 | 5.77 |
| 57 | dev | early_db | 4.01 | 8.91 |
| 81 | train | ild_db | 3.37 | 8.27 |
| 69 | dev | level_db | 0.78 | 5.67 |
| 66 | dev | level_db | 0.29 | 5.15 |
| 60 | train | sustain_db | 4.76 | 9.60 |
| 57 | dev | ild_db | 1.65 | 6.46 |
| 24 | train | ild_db | 0.50 | 5.29 |
| 45 | dev | partial_db | 5.82 | 10.58 |
| 24 | dev | ild_db | 0.50 | 5.26 |
| 69 | train | level_db | 0.62 | 5.37 |
| 105 | dev | icc | 0.15 | 0.33 |
| 57 | train | ild_db | 1.60 | 6.32 |
| 66 | train | sustain_db | 3.73 | 8.40 |
| 66 | train | level_db | 0.60 | 5.24 |
| 54 | train | attack_db | 4.20 | 8.81 |
| 45 | dev | level_db | 0.25 | 4.84 |
| 21 | dev | tuning_cents | 0.04 | 4.63 |
| 90 | train | icc | 0.08 | 0.26 |
| 21 | train | tuning_cents | 0.05 | 4.63 |
| 27 | dev | partial_db | 7.04 | 11.61 |
| 66 | dev | sustain_db | 3.64 | 8.17 |
| 84 | dev | partial_db | 4.07 | 8.61 |
| 72 | dev | envelope_db | 0.88 | 5.39 |
| 96 | dev | envelope_db | 2.23 | 6.73 |
| 24 | dev | icc | 0.02 | 0.20 |
| 57 | train | early_db | 4.10 | 8.58 |
| 84 | dev | level_db | 0.66 | 5.11 |
| 24 | train | icc | 0.02 | 0.20 |
| 60 | dev | early_db | 3.36 | 7.80 |
| 93 | dev | rise_ms | 0.61 | 9.44 |
| 45 | train | level_db | 0.51 | 4.92 |
| 48 | dev | tuning_cents | 0.07 | 4.48 |
| 90 | dev | icc | 0.07 | 0.25 |
| 72 | train | envelope_db | 0.94 | 5.32 |
| 60 | train | early_db | 3.44 | 7.80 |
| 36 | train | ild_db | 0.67 | 5.02 |
| 24 | train | rise_ms | 1.72 | 10.37 |
| 57 | train | icc | 0.06 | 0.23 |
| 69 | train | attack_db | 3.55 | 7.85 |
| 45 | dev | sustain_db | 3.80 | 8.08 |
| 45 | train | sustain_db | 3.76 | 8.03 |
| 24 | dev | noise_db | 4.22 | 8.48 |
| 45 | train | partial_db | 5.84 | 10.10 |
| 30 | dev | icc | 0.03 | 0.20 |
| 69 | dev | icc | 0.03 | 0.20 |
| 93 | train | rise_ms | 0.73 | 9.24 |
| 78 | dev | partial_db | 3.61 | 7.86 |
| 102 | train | icc | 0.24 | 0.41 |
| 24 | dev | tuning_cents | 0.06 | 4.30 |
| 48 | train | tuning_cents | 0.09 | 4.32 |
| 24 | train | tuning_cents | 0.07 | 4.30 |
| 24 | dev | rise_ms | 1.80 | 10.24 |
| 96 | train | envelope_db | 2.24 | 6.45 |
| 102 | dev | icc | 0.23 | 0.40 |
| 36 | dev | ild_db | 0.72 | 4.89 |
| 66 | dev | tuning_cents | 0.09 | 4.24 |
| 30 | dev | noise_db | 3.30 | 7.45 |
| 42 | dev | envelope_db | 0.88 | 5.03 |
| 54 | dev | ild_db | 0.84 | 4.99 |
| 42 | dev | rise_ms | 0.84 | 9.08 |
| 84 | train | level_db | 0.86 | 4.97 |
| 69 | train | icc | 0.03 | 0.20 |
| 30 | train | icc | 0.04 | 0.20 |
| 54 | train | ild_db | 0.94 | 5.00 |
| 42 | train | envelope_db | 0.96 | 5.02 |
| 102 | dev | level_db | 1.01 | 5.07 |
| 69 | dev | attack_db | 3.45 | 7.49 |
| 66 | train | tuning_cents | 0.11 | 4.15 |
| 105 | train | icc | 0.12 | 0.28 |
| 21 | dev | icc | 0.03 | 0.19 |
| 72 | train | partial_db | 4.82 | 8.83 |
| 21 | train | icc | 0.03 | 0.19 |
| 57 | dev | icc | 0.06 | 0.22 |
| 57 | dev | attack_db | 3.86 | 7.82 |
| 99 | dev | decay_db_s | 1.26 | 9.13 |
| 42 | dev | ild_db | 0.38 | 4.30 |
| 42 | train | ild_db | 0.46 | 4.37 |
| 84 | dev | icc | 0.03 | 0.19 |
| 72 | dev | partial_db | 4.99 | 8.85 |
| 54 | train | icc | 0.08 | 0.24 |
| 48 | dev | icc | 0.06 | 0.21 |
| 81 | train | attack_db | 3.93 | 7.74 |
| 102 | dev | decay_db_s | 2.55 | 10.18 |
| 24 | train | noise_db | 4.23 | 8.04 |
| 81 | dev | attack_db | 3.41 | 7.20 |
| 51 | dev | envelope_db | 1.52 | 5.27 |
| 42 | train | rise_ms | 2.50 | 9.92 |
| 57 | dev | envelope_db | 0.50 | 4.21 |
| 30 | train | sustain_db | 3.48 | 7.11 |
| 108 | train | icc | 0.18 | 0.32 |
| 57 | train | envelope_db | 0.50 | 4.14 |
| 84 | train | icc | 0.04 | 0.18 |
| 54 | dev | icc | 0.08 | 0.23 |
| 36 | train | level_db | 0.77 | 4.37 |
| 108 | dev | icc | 0.10 | 0.25 |
| 102 | train | level_db | 0.98 | 4.54 |
| 33 | train | level_db | 0.65 | 4.20 |
| 27 | dev | early_db | 4.29 | 7.84 |
| 48 | dev | partial_db | 5.42 | 8.96 |
| 36 | dev | level_db | 0.53 | 3.99 |
| 42 | dev | icc | 0.02 | 0.16 |
| 48 | train | icc | 0.06 | 0.20 |
| 96 | dev | level_db | 1.14 | 4.57 |
| 81 | dev | sustain_db | 3.02 | 6.42 |
| 75 | dev | early_db | 5.82 | 9.22 |
| 45 | dev | ild_db | 1.39 | 4.77 |
| 81 | train | sustain_db | 3.87 | 7.24 |
| 84 | dev | decay_db_s | 3.28 | 10.03 |
| 42 | dev | tuning_cents | 0.02 | 3.40 |
| 30 | dev | sustain_db | 3.49 | 6.86 |
| 54 | dev | tuning_cents | 0.05 | 3.40 |
| 36 | train | early_db | 3.30 | 6.65 |
| 33 | dev | level_db | 0.69 | 4.04 |
| 45 | train | ild_db | 1.47 | 4.82 |
| 54 | train | tuning_cents | 0.05 | 3.39 |
| 72 | train | icc | 0.03 | 0.16 |
| 57 | train | attack_db | 4.35 | 7.66 |
| 21 | train | ild_db | 1.03 | 4.33 |
| 36 | dev | early_db | 3.35 | 6.64 |
| 42 | train | icc | 0.03 | 0.16 |
| 30 | train | ild_db | 0.70 | 3.97 |
| 45 | dev | tuning_cents | 0.03 | 3.26 |
| 30 | dev | ild_db | 0.69 | 3.92 |
| 96 | dev | ild_db | 0.53 | 3.76 |
| 90 | dev | decay_db_s | 2.66 | 9.10 |
| 99 | dev | level_db | 1.19 | 4.40 |
| 33 | train | ild_db | 0.45 | 3.64 |
| 33 | dev | ild_db | 0.40 | 3.58 |
| 66 | train | envelope_db | 0.76 | 3.93 |
| 78 | train | partial_db | 3.72 | 6.89 |
| 33 | train | sustain_db | 4.47 | 7.61 |
| 33 | dev | early_db | 4.23 | 7.36 |
| 33 | dev | sustain_db | 4.34 | 7.46 |
| 96 | train | ild_db | 0.54 | 3.66 |
| 99 | dev | tuning_cents | 1.83 | 4.94 |
| 27 | dev | icc | 0.10 | 0.23 |
| 33 | train | early_db | 4.31 | 7.39 |
| 21 | dev | ild_db | 1.12 | 4.20 |
| 66 | dev | envelope_db | 0.73 | 3.82 |
| 75 | dev | level_db | 1.15 | 4.21 |
| 60 | dev | tuning_cents | 0.04 | 3.09 |
| 42 | train | tuning_cents | 0.03 | 3.06 |
| 45 | train | tuning_cents | 0.03 | 3.05 |
| 54 | train | noise_db | 8.77 | 11.77 |
| 51 | dev | partial_db | 8.01 | 11.02 |
| 72 | dev | icc | 0.03 | 0.15 |
| 66 | dev | early_db | 4.40 | 7.37 |
| 57 | dev | tuning_cents | 0.05 | 3.01 |
| 69 | dev | envelope_db | 1.04 | 4.01 |
| 57 | train | tuning_cents | 0.04 | 3.00 |
| 84 | train | decay_db_s | 3.41 | 9.26 |
| 66 | train | early_db | 4.44 | 7.36 |
| 48 | train | partial_db | 5.78 | 8.67 |
| 45 | dev | early_db | 4.12 | 6.99 |
| 90 | train | decay_db_s | 2.75 | 8.48 |
| 27 | dev | attack_db | 5.26 | 8.08 |
| 21 | train | noise_db | 4.70 | 7.52 |
| 54 | train | envelope_db | 0.46 | 3.27 |
| 90 | train | ild_db | 0.88 | 3.66 |
| 81 | train | envelope_db | 1.39 | 4.17 |
| 69 | train | envelope_db | 1.07 | 3.84 |
| 105 | dev | tuning_cents | 0.25 | 3.01 |
| 45 | train | early_db | 4.16 | 6.91 |
| 66 | train | attack_db | 3.90 | 6.64 |
| 90 | dev | ild_db | 0.88 | 3.62 |
| 45 | dev | icc | 0.02 | 0.13 |
| 60 | train | tuning_cents | 0.05 | 2.75 |
| 42 | dev | sustain_db | 3.69 | 6.38 |
| 54 | dev | envelope_db | 0.39 | 3.07 |
| 42 | train | sustain_db | 3.82 | 6.49 |
| 66 | dev | attack_db | 4.11 | 6.77 |
| 78 | train | rise_ms | 7.23 | 12.55 |
| 81 | dev | envelope_db | 1.48 | 4.14 |
| 69 | train | noise_db | 4.96 | 7.62 |
| 30 | train | early_db | 3.50 | 6.15 |
| 96 | train | level_db | 1.28 | 3.91 |
| 60 | train | attack_db | 3.62 | 6.25 |
| 69 | dev | noise_db | 4.95 | 7.53 |
| 78 | dev | rise_ms | 7.06 | 12.19 |
| 60 | dev | attack_db | 3.63 | 6.20 |
| 30 | train | attack_db | 4.37 | 6.89 |
| 33 | train | noise_db | 7.10 | 9.61 |
| 27 | dev | sustain_db | 4.31 | 6.81 |
| 96 | dev | rise_ms | 0.70 | 5.70 |
| 27 | dev | ild_db | 2.90 | 5.34 |
| 24 | dev | level_db | 0.62 | 3.06 |
| 102 | dev | envelope_db | 4.03 | 6.46 |
| 75 | dev | ild_db | 7.07 | 9.49 |
| 30 | train | level_db | 0.91 | 3.33 |
| 96 | train | rise_ms | 1.02 | 5.84 |
| 45 | train | icc | 0.03 | 0.12 |
| 42 | dev | partial_db | 6.09 | 8.48 |
| 54 | dev | noise_db | 9.58 | 11.96 |
| 24 | train | level_db | 0.76 | 3.13 |
| 105 | train | tuning_cents | 0.24 | 2.59 |
| 96 | train | tuning_cents | 0.31 | 2.64 |
| 102 | dev | tuning_cents | 0.41 | 2.70 |
| 33 | dev | tuning_cents | 0.05 | 2.31 |
| 42 | train | partial_db | 5.96 | 8.21 |
| 105 | train | ild_db | 0.66 | 2.90 |
| 36 | dev | tuning_cents | 0.03 | 2.25 |
| 84 | dev | rise_ms | 3.45 | 7.86 |
| 30 | dev | level_db | 0.93 | 3.13 |
| 81 | dev | level_db | 1.59 | 3.79 |
| 66 | dev | noise_db | 4.78 | 6.98 |
| 33 | train | tuning_cents | 0.05 | 2.24 |
| 105 | train | level_db | 0.99 | 3.16 |
| 36 | train | tuning_cents | 0.04 | 2.21 |
| 51 | dev | level_db | 1.46 | 3.61 |
| 30 | dev | early_db | 3.56 | 5.70 |
| 96 | dev | tuning_cents | 0.42 | 2.55 |
| 30 | dev | attack_db | 4.38 | 6.49 |
| 36 | train | attack_db | 3.85 | 5.97 |
| 90 | dev | tuning_cents | 0.16 | 2.26 |
| 93 | train | tuning_cents | 0.48 | 2.55 |
| 84 | train | envelope_db | 1.25 | 3.30 |
| 84 | dev | envelope_db | 0.85 | 2.90 |
| 69 | dev | ild_db | 3.31 | 5.33 |
| 30 | dev | tuning_cents | 0.02 | 2.03 |
| 78 | dev | decay_db_s | 1.50 | 5.51 |
| 78 | train | decay_db_s | 1.31 | 5.29 |
| 33 | train | rise_ms | 3.23 | 7.20 |
| 81 | train | level_db | 1.47 | 3.44 |
| 45 | train | envelope_db | 1.03 | 2.99 |
| 90 | train | tuning_cents | 0.26 | 2.21 |
| 24 | dev | sustain_db | 3.20 | 5.14 |
| 105 | train | envelope_db | 3.15 | 5.08 |
| 30 | train | tuning_cents | 0.02 | 1.94 |
| 66 | train | noise_db | 4.73 | 6.64 |
| 21 | train | sustain_db | 3.56 | 5.44 |
| 81 | train | partial_db | 4.29 | 6.16 |
| 21 | dev | level_db | 0.81 | 2.69 |
| 27 | dev | level_db | 1.34 | 3.20 |
| 69 | dev | decay_db_s | 1.60 | 5.31 |
| 36 | dev | attack_db | 3.96 | 5.80 |
| 45 | dev | envelope_db | 1.05 | 2.89 |
| 102 | train | tuning_cents | 0.39 | 2.23 |
| 99 | dev | icc | 0.24 | 0.31 |
| 78 | dev | tuning_cents | 0.11 | 1.92 |
| 21 | dev | sustain_db | 3.54 | 5.34 |
| 93 | dev | tuning_cents | 0.77 | 2.56 |
| 105 | dev | envelope_db | 4.42 | 6.20 |
| 45 | train | attack_db | 4.42 | 6.19 |
| 33 | train | attack_db | 4.09 | 5.85 |
| 60 | train | rise_ms | 3.49 | 7.00 |
| 78 | train | tuning_cents | 0.10 | 1.84 |
| 45 | dev | attack_db | 4.39 | 6.13 |
| 51 | dev | sustain_db | 5.65 | 7.36 |
| 105 | dev | level_db | 0.96 | 2.66 |
| 24 | train | sustain_db | 3.41 | 5.10 |
| 24 | dev | envelope_db | 2.20 | 3.89 |
| 96 | train | icc | 0.02 | 0.09 |
| 21 | dev | noise_db | 4.62 | 6.30 |
| 33 | train | envelope_db | 2.02 | 3.69 |
| 48 | dev | noise_db | 4.25 | 5.92 |
| 102 | train | envelope_db | 3.10 | 4.74 |
| 33 | dev | attack_db | 3.92 | 5.54 |
| 69 | train | decay_db_s | 1.75 | 4.98 |
| 84 | dev | tuning_cents | 0.25 | 1.85 |
| 69 | train | ild_db | 3.54 | 5.13 |
| 48 | dev | attack_db | 3.77 | 5.35 |
| 48 | train | attack_db | 3.88 | 5.46 |
| 60 | dev | decay_db_s | 1.09 | 4.26 |
| 42 | dev | decay_db_s | 0.42 | 3.58 |
| 30 | dev | decay_db_s | 0.20 | 3.32 |
| 81 | train | tuning_cents | 0.17 | 1.73 |
| 30 | train | decay_db_s | 0.22 | 3.30 |
| 21 | train | level_db | 0.74 | 2.27 |
| 84 | train | ild_db | 2.90 | 4.41 |
| 42 | train | decay_db_s | 0.48 | 3.50 |
| 51 | dev | tuning_cents | 1.37 | 2.88 |
| 69 | dev | tuning_cents | 0.08 | 1.54 |
| 84 | train | tuning_cents | 0.39 | 1.86 |
| 93 | train | decay_db_s | 5.82 | 8.73 |
| 84 | train | rise_ms | 2.82 | 5.69 |
| 96 | dev | icc | 0.03 | 0.08 |
| 21 | dev | decay_db_s | 0.27 | 3.09 |
| 105 | dev | ild_db | 0.72 | 2.12 |
| 69 | train | tuning_cents | 0.07 | 1.46 |
| 60 | train | decay_db_s | 1.22 | 3.97 |
| 21 | train | decay_db_s | 0.25 | 2.98 |
| 81 | dev | tuning_cents | 0.18 | 1.53 |
| 81 | train | decay_db_s | 2.33 | 5.02 |
| 24 | dev | early_db | 3.89 | 5.23 |
| 108 | dev | level_db | 2.74 | 4.07 |
| 99 | dev | envelope_db | 3.76 | 5.10 |
| 108 | train | level_db | 2.94 | 4.20 |
| 54 | dev | decay_db_s | 1.21 | 3.68 |
| 24 | train | envelope_db | 2.64 | 3.86 |
| 21 | train | early_db | 3.98 | 5.19 |
| 72 | dev | decay_db_s | 1.62 | 4.01 |
| 93 | dev | decay_db_s | 4.75 | 7.13 |
| 72 | dev | tuning_cents | 0.04 | 1.22 |
| 48 | train | decay_db_s | 1.16 | 3.52 |
| 54 | train | decay_db_s | 1.28 | 3.62 |
| 72 | train | decay_db_s | 1.78 | 4.12 |
| 48 | dev | decay_db_s | 1.09 | 3.42 |
| 72 | train | tuning_cents | 0.04 | 1.18 |
| 45 | dev | noise_db | 6.27 | 7.41 |
| 24 | train | early_db | 4.06 | 5.19 |
| 57 | dev | decay_db_s | 0.87 | 3.11 |
| 33 | dev | envelope_db | 2.54 | 3.66 |
| 48 | dev | envelope_db | 1.78 | 2.88 |
| 24 | dev | attack_db | 5.09 | 6.16 |
| 24 | dev | decay_db_s | 0.41 | 2.51 |
| 21 | dev | early_db | 4.05 | 5.10 |
| 24 | train | decay_db_s | 0.38 | 2.46 |
| 57 | train | decay_db_s | 0.92 | 3.00 |
| 81 | dev | decay_db_s | 2.47 | 4.53 |
| 48 | train | envelope_db | 2.02 | 2.96 |
| 60 | dev | rise_ms | 2.95 | 4.83 |
| 84 | dev | ild_db | 3.05 | 3.97 |
| 33 | train | decay_db_s | 0.76 | 2.59 |
| 33 | dev | decay_db_s | 0.71 | 2.53 |
| 81 | dev | partial_db | 4.26 | 5.13 |
| 27 | dev | tuning_cents | 3.41 | 4.27 |
| 21 | train | envelope_db | 2.47 | 3.32 |
| 66 | train | decay_db_s | 1.49 | 3.13 |
| 36 | train | decay_db_s | 0.41 | 2.01 |
| 66 | dev | decay_db_s | 1.46 | 3.06 |
| 27 | dev | noise_db | 5.27 | 6.04 |
| 24 | train | attack_db | 5.54 | 6.31 |
| 36 | dev | decay_db_s | 0.41 | 1.91 |
| 51 | dev | early_db | 5.45 | 6.19 |
| 21 | dev | envelope_db | 2.61 | 3.33 |
| 45 | dev | decay_db_s | 0.49 | 1.89 |
| 45 | train | decay_db_s | 0.54 | 1.90 |
| 102 | dev | rise_ms | 2.45 | 3.68 |
| 102 | dev | ild_db | 2.39 | 3.00 |
| 102 | train | rise_ms | 2.84 | 3.97 |
| 102 | train | ild_db | 2.18 | 2.74 |
| 30 | train | noise_db | 5.70 | 6.22 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (25.4583 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 5.2791 | 11.6964 | 6.4174 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 0.9074 | 3.0864 | 2.1790 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 2.0900 | 5.4786 | 3.3885 | 0 | 0 | 1 |
| dev | attack_db | 156 | 4.6518 | 9.5013 | 4.8495 | 0 | 0 | 0 |
| dev | early_db | 156 | 4.4112 | 10.0422 | 5.6311 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 5.3141 | 10.8728 | 5.5587 | 0 | 0 | 0 |
| dev | noise_db | 153 | 5.2681 | 10.6177 | 5.3496 | 0 | 0 | 3 |
| dev | ild_db | 154 | 2.6444 | 5.4224 | 2.7780 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1024 | 0.2105 | 0.1080 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 2.6256 | 4.8061 | 2.1805 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 4.5040 | 15.4748 | 10.9708 | 0 | 0 | 0 |
| dev | level_db | 156 | 1.1130 | 6.0968 | 4.9838 | 0 | 0 | 0 |
| train | partial_db | 276 | 4.5018 | 12.0238 | 7.5220 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 0.1689 | 2.8484 | 2.6795 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 1.8523 | 6.6544 | 4.8021 | 0 | 0 | 5 |
| train | attack_db | 276 | 4.2885 | 9.3942 | 5.1057 | 0 | 0 | 0 |
| train | early_db | 276 | 4.0107 | 10.1826 | 6.1719 | 0 | 0 | 0 |
| train | sustain_db | 276 | 4.6038 | 11.4566 | 6.8528 | 0 | 0 | 0 |
| train | noise_db | 263 | 5.6516 | 11.0441 | 5.3925 | 0 | 7 | 6 |
| train | ild_db | 270 | 1.5448 | 5.6865 | 4.1417 | 0 | 0 | 6 |
| train | icc | 270 | 0.0564 | 0.2210 | 0.1646 | 0 | 0 | 6 |
| train | envelope_db | 276 | 1.9386 | 4.8882 | 2.9495 | 0 | 0 | 0 |
| train | rise_ms | 276 | 3.6678 | 16.0952 | 12.4274 | 0 | 0 | 0 |
| train | level_db | 276 | 1.0545 | 5.7237 | 4.6692 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 30 | dev | rise_ms | 4 | 1.7760 | 69.9740 | 68.1979 |
| 30 | train | rise_ms | 12 | 2.2760 | 69.6302 | 67.3542 |
| 21 | dev | rise_ms | 4 | 2.0521 | 48.2135 | 46.1615 |
| 21 | train | rise_ms | 12 | 1.9444 | 46.7448 | 44.8003 |
| 105 | dev | partial_db | 4 | 3.4512 | 25.4201 | 21.9689 |
| 105 | train | partial_db | 12 | 3.1564 | 24.9075 | 21.7511 |
| 54 | train | rise_ms | 12 | 4.2587 | 45.9375 | 41.6788 |
| 54 | dev | rise_ms | 4 | 4.6875 | 45.6042 | 40.9167 |
| 102 | train | partial_db | 12 | 1.9643 | 21.5654 | 19.6011 |
| 27 | dev | rise_ms | 16 | 5.5937 | 43.7057 | 38.1120 |
| 102 | dev | partial_db | 4 | 1.9485 | 20.3095 | 18.3610 |
| 102 | train | sustain_db | 12 | 6.3568 | 22.5749 | 16.2181 |
| 96 | train | sustain_db | 12 | 2.6345 | 18.4887 | 15.8542 |
| 96 | dev | sustain_db | 4 | 2.6965 | 18.3501 | 15.6536 |
| 102 | dev | sustain_db | 4 | 5.4749 | 20.9490 | 15.4741 |
| 102 | train | early_db | 12 | 3.3135 | 18.5573 | 15.2438 |
| 105 | dev | sustain_db | 4 | 6.6773 | 21.3254 | 14.6481 |
| 99 | dev | partial_db | 16 | 2.7975 | 17.1912 | 14.3937 |
| 105 | train | sustain_db | 12 | 6.9493 | 21.1448 | 14.1954 |
| 102 | dev | early_db | 4 | 3.4004 | 17.5923 | 14.1918 |
| 99 | dev | sustain_db | 16 | 5.3915 | 19.4589 | 14.0674 |
| 105 | train | early_db | 12 | 3.9747 | 17.7364 | 13.7617 |
| 105 | dev | early_db | 4 | 4.0958 | 17.3186 | 13.2228 |
| 105 | train | noise_db | 12 | 4.5545 | 17.6069 | 13.0524 |
| 96 | train | partial_db | 12 | 1.9224 | 14.6537 | 12.7313 |
| 99 | dev | early_db | 16 | 4.6088 | 17.2985 | 12.6897 |
| 102 | train | noise_db | 12 | 4.3913 | 16.9180 | 12.5267 |
| 105 | dev | noise_db | 4 | 4.7727 | 17.2793 | 12.5066 |
| 102 | dev | noise_db | 4 | 4.4906 | 16.9449 | 12.4543 |
| 93 | train | noise_db | 12 | 4.4667 | 16.8463 | 12.3796 |
| 93 | dev | noise_db | 4 | 4.2535 | 16.6037 | 12.3501 |
| 99 | dev | noise_db | 16 | 5.2590 | 17.5843 | 12.3253 |
| 57 | dev | rise_ms | 4 | 1.9792 | 26.4896 | 24.5104 |
| 57 | train | rise_ms | 12 | 2.4063 | 26.6007 | 24.1944 |
| 96 | dev | partial_db | 4 | 1.9410 | 14.0218 | 12.0808 |
| 96 | train | noise_db | 12 | 4.3540 | 16.4280 | 12.0740 |
| 108 | train | partial_db | 12 | 10.6054 | 22.3994 | 11.7940 |
| 84 | dev | sustain_db | 4 | 4.0531 | 15.7769 | 11.7238 |
| 108 | dev | early_db | 4 | 6.9387 | 18.6243 | 11.6856 |
| 84 | train | sustain_db | 12 | 3.5922 | 15.2389 | 11.6467 |
| 108 | train | early_db | 12 | 7.2477 | 18.8682 | 11.6204 |
| 90 | dev | level_db | 4 | 0.5323 | 12.1478 | 11.6156 |
| 105 | train | decay_db_s | 11 | 1.1175 | 24.2986 | 23.1811 |
| 105 | train | attack_db | 12 | 4.4559 | 16.0431 | 11.5872 |
| 96 | dev | noise_db | 4 | 4.2699 | 15.8155 | 11.5456 |
| 90 | train | level_db | 12 | 0.5134 | 12.0347 | 11.5213 |
| 72 | train | level_db | 12 | 0.2435 | 11.7042 | 11.4607 |
| 105 | dev | attack_db | 4 | 4.5274 | 15.9454 | 11.4180 |
| 102 | train | attack_db | 12 | 3.9619 | 15.2626 | 11.3008 |
| 93 | train | level_db | 12 | 1.1687 | 12.2451 | 11.0764 |
| 72 | dev | level_db | 4 | 0.3248 | 11.3956 | 11.0708 |
| 96 | train | early_db | 12 | 4.1934 | 15.2159 | 11.0226 |
| 102 | dev | attack_db | 4 | 4.2907 | 15.2190 | 10.9283 |
| 90 | train | early_db | 12 | 3.7116 | 14.5882 | 10.8766 |
| 93 | train | early_db | 12 | 4.2948 | 15.0870 | 10.7922 |
| 93 | dev | level_db | 4 | 0.8706 | 11.5176 | 10.6470 |
| 93 | train | sustain_db | 12 | 5.0608 | 15.7007 | 10.6399 |
| 90 | dev | noise_db | 4 | 4.5104 | 15.0403 | 10.5299 |
| 90 | train | noise_db | 12 | 4.4422 | 14.9279 | 10.4858 |
| 90 | dev | early_db | 4 | 3.8370 | 14.1849 | 10.3479 |
| 108 | dev | partial_db | 4 | 11.1333 | 21.3824 | 10.2491 |
| 108 | dev | sustain_db | 4 | 16.9346 | 27.1803 | 10.2457 |
| 93 | train | attack_db | 12 | 3.8066 | 14.0460 | 10.2394 |
| 105 | dev | decay_db_s | 4 | 1.6645 | 22.0669 | 20.4024 |
| 72 | train | attack_db | 12 | 4.1652 | 14.3163 | 10.1511 |
| 93 | dev | early_db | 4 | 4.1881 | 14.3176 | 10.1296 |
| 96 | dev | early_db | 4 | 4.0102 | 14.0491 | 10.0389 |
| 78 | train | attack_db | 12 | 3.2375 | 13.2649 | 10.0274 |
| 99 | dev | attack_db | 16 | 5.0541 | 15.0803 | 10.0263 |
| 78 | dev | early_db | 4 | 3.4332 | 13.4535 | 10.0203 |
| 78 | dev | attack_db | 4 | 3.3539 | 13.3298 | 9.9759 |
| 72 | dev | attack_db | 4 | 4.2114 | 14.0957 | 9.8843 |
| 78 | train | level_db | 12 | 1.2054 | 10.9764 | 9.7710 |
| 93 | dev | attack_db | 4 | 3.5245 | 13.2943 | 9.7698 |
| 78 | train | early_db | 12 | 3.3832 | 13.0578 | 9.6746 |
| 96 | train | attack_db | 12 | 3.7553 | 13.2791 | 9.5238 |
| 93 | dev | sustain_db | 4 | 4.8498 | 14.3514 | 9.5016 |
| 78 | dev | level_db | 4 | 1.3970 | 10.7619 | 9.3648 |
| 72 | train | noise_db | 12 | 4.7080 | 14.0653 | 9.3574 |
| 72 | dev | noise_db | 4 | 4.5898 | 13.7650 | 9.1752 |
| 96 | dev | attack_db | 4 | 3.8485 | 12.9633 | 9.1147 |
| 42 | train | noise_db | 7 | 4.2543 | 13.3190 | 9.0646 |
| 21 | dev | partial_db | 4 | 3.3683 | 12.4187 | 9.0504 |
| 66 | train | rise_ms | 12 | 6.8802 | 24.9583 | 18.0781 |
| 84 | train | early_db | 12 | 3.8067 | 12.8348 | 9.0281 |
| 108 | train | sustain_db | 12 | 17.6996 | 26.6927 | 8.9932 |
| 93 | train | ild_db | 12 | 0.6887 | 9.6758 | 8.9871 |
| 93 | dev | ild_db | 4 | 0.6671 | 9.6507 | 8.9836 |
| 78 | train | noise_db | 12 | 3.9549 | 12.8648 | 8.9099 |
| 84 | dev | early_db | 4 | 3.7882 | 12.6884 | 8.9002 |
| 90 | train | attack_db | 12 | 3.3894 | 12.2502 | 8.8608 |
| 66 | dev | rise_ms | 4 | 5.7865 | 23.4688 | 17.6823 |
| 69 | dev | partial_db | 4 | 3.7153 | 12.5563 | 8.8410 |
| 108 | dev | decay_db_s | 3 | 5.6362 | 23.2910 | 17.6548 |
| 78 | dev | noise_db | 4 | 3.9813 | 12.7513 | 8.7700 |
| 69 | train | partial_db | 12 | 4.1351 | 12.8543 | 8.7192 |
| 21 | train | partial_db | 12 | 3.6908 | 12.3652 | 8.6744 |
| 90 | dev | attack_db | 4 | 3.2787 | 11.9474 | 8.6687 |
| 72 | dev | rise_ms | 4 | 1.2083 | 18.0781 | 16.8698 |
| 93 | train | partial_db | 12 | 3.7458 | 12.1455 | 8.3997 |
| 72 | train | rise_ms | 12 | 1.0226 | 17.7639 | 16.7413 |
| 24 | dev | partial_db | 4 | 3.1489 | 11.5080 | 8.3591 |
| 72 | train | early_db | 12 | 3.8370 | 12.1837 | 8.3467 |
| 108 | dev | noise_db | 4 | 8.5127 | 16.7198 | 8.2071 |
| 45 | train | rise_ms | 12 | 7.8941 | 24.1788 | 16.2847 |
| 45 | dev | rise_ms | 4 | 7.7656 | 23.8698 | 16.1042 |
| 54 | dev | partial_db | 4 | 5.0811 | 13.1013 | 8.0202 |
| 108 | train | noise_db | 12 | 8.8070 | 16.7822 | 7.9752 |
| 90 | train | sustain_db | 12 | 6.5477 | 14.5003 | 7.9527 |
| 72 | dev | sustain_db | 4 | 3.2880 | 11.1783 | 7.8903 |
| 66 | train | ild_db | 12 | 4.5349 | 12.3828 | 7.8479 |
| 72 | dev | early_db | 4 | 4.2791 | 12.0861 | 7.8070 |
| 24 | train | partial_db | 12 | 3.5031 | 11.3028 | 7.7998 |
| 72 | train | sustain_db | 12 | 3.2718 | 11.0601 | 7.7883 |
| 66 | dev | ild_db | 4 | 4.5406 | 12.2828 | 7.7423 |
| 57 | dev | partial_db | 4 | 4.8320 | 12.4687 | 7.6366 |
| 78 | dev | sustain_db | 4 | 2.1141 | 9.6082 | 7.4941 |
| 75 | dev | level_db | 16 | 1.1549 | 8.6383 | 7.4834 |
| 60 | dev | ild_db | 4 | 2.2129 | 9.6311 | 7.4182 |
| 108 | train | decay_db_s | 8 | 5.0975 | 19.8997 | 14.8022 |
| 90 | train | partial_db | 12 | 3.0608 | 10.3594 | 7.2985 |
| 78 | train | ild_db | 12 | 0.4994 | 7.7811 | 7.2817 |
| 102 | train | level_db | 12 | 0.9845 | 8.2575 | 7.2729 |
| 108 | train | attack_db | 12 | 8.1348 | 15.3753 | 7.2404 |
| 54 | train | partial_db | 12 | 5.3732 | 12.5870 | 7.2138 |
| 102 | dev | level_db | 4 | 1.0135 | 8.2052 | 7.1917 |
| 84 | train | noise_db | 12 | 4.9781 | 12.1683 | 7.1902 |
| 108 | dev | attack_db | 4 | 7.7463 | 14.9197 | 7.1734 |
| 99 | dev | level_db | 16 | 1.1876 | 8.3196 | 7.1320 |
| 48 | dev | rise_ms | 4 | 5.5052 | 19.6875 | 14.1823 |
| 78 | dev | ild_db | 4 | 0.6237 | 7.7059 | 7.0822 |
| 84 | dev | noise_db | 4 | 4.9617 | 11.9342 | 6.9725 |
| 60 | train | ild_db | 12 | 2.6269 | 9.5601 | 6.9332 |
| 90 | dev | sustain_db | 4 | 7.2722 | 14.1691 | 6.8969 |
| 66 | dev | icc | 4 | 0.0307 | 0.3033 | 0.2726 |
| 42 | dev | noise_db | 4 | 5.2040 | 11.9834 | 6.7795 |
| 57 | train | partial_db | 12 | 4.7793 | 11.5543 | 6.7750 |
| 69 | dev | sustain_db | 4 | 2.0532 | 8.8248 | 6.7716 |
| 78 | train | icc | 12 | 0.0364 | 0.3071 | 0.2707 |
| 84 | train | level_db | 12 | 0.8596 | 7.6028 | 6.7432 |
| 78 | dev | icc | 4 | 0.0316 | 0.3010 | 0.2694 |
| 84 | dev | level_db | 4 | 0.6551 | 7.3813 | 6.7261 |
| 66 | train | icc | 12 | 0.0335 | 0.3025 | 0.2689 |
| 78 | train | sustain_db | 12 | 2.2277 | 8.9248 | 6.6971 |
| 96 | dev | decay_db_s | 4 | 2.5310 | 15.9149 | 13.3839 |
| 96 | train | decay_db_s | 12 | 2.1859 | 15.5237 | 13.3378 |
| 69 | train | sustain_db | 12 | 2.1525 | 8.8212 | 6.6687 |
| 48 | train | rise_ms | 12 | 5.9896 | 19.1771 | 13.1875 |
| 93 | dev | partial_db | 4 | 3.7043 | 10.2889 | 6.5846 |
| 84 | train | attack_db | 12 | 4.3650 | 10.9294 | 6.5645 |
| 36 | dev | partial_db | 4 | 4.6060 | 11.0571 | 6.4510 |
| 84 | dev | attack_db | 4 | 4.5251 | 10.9279 | 6.4028 |
| 90 | dev | envelope_db | 4 | 5.6676 | 12.0513 | 6.3837 |
| 60 | dev | partial_db | 4 | 4.1975 | 10.4807 | 6.2832 |
| 75 | dev | noise_db | 16 | 4.7031 | 10.8556 | 6.1525 |
| 30 | train | partial_db | 12 | 4.6610 | 10.7560 | 6.0950 |
| 78 | dev | envelope_db | 4 | 0.4617 | 6.4852 | 6.0235 |
| 36 | train | partial_db | 12 | 4.7230 | 10.7190 | 5.9960 |
| 90 | dev | partial_db | 4 | 2.8353 | 8.7961 | 5.9609 |
| 30 | dev | partial_db | 4 | 4.5627 | 10.5032 | 5.9405 |
| 72 | dev | ild_db | 4 | 0.4953 | 6.4111 | 5.9157 |
| 78 | train | envelope_db | 12 | 0.5085 | 6.4196 | 5.9111 |
| 81 | dev | icc | 4 | 0.0150 | 0.2497 | 0.2348 |
| 33 | dev | icc | 4 | 0.0254 | 0.2598 | 0.2344 |
| 60 | train | partial_db | 12 | 4.2445 | 10.0984 | 5.8538 |
| 96 | train | level_db | 12 | 1.2832 | 7.0869 | 5.8037 |
| 33 | train | partial_db | 12 | 4.8020 | 10.5961 | 5.7941 |
| 27 | dev | level_db | 16 | 1.3414 | 7.1170 | 5.7756 |
| 57 | dev | sustain_db | 4 | 3.1631 | 8.9346 | 5.7715 |
| 108 | dev | level_db | 4 | 2.7391 | 8.5042 | 5.7651 |
| 33 | dev | noise_db | 4 | 4.9755 | 10.7028 | 5.7273 |
| 93 | train | envelope_db | 12 | 4.2431 | 9.9618 | 5.7187 |
| 90 | train | envelope_db | 12 | 5.2240 | 10.9412 | 5.7172 |
| 33 | dev | partial_db | 4 | 4.6804 | 10.3878 | 5.7073 |
| 75 | dev | attack_db | 16 | 5.0895 | 10.7939 | 5.7044 |
| 108 | train | level_db | 12 | 2.9431 | 8.6310 | 5.6879 |
| 81 | dev | ild_db | 4 | 3.0971 | 8.7781 | 5.6810 |
| 60 | dev | icc | 4 | 0.0619 | 0.2884 | 0.2265 |
| 96 | dev | level_db | 4 | 1.1397 | 6.7849 | 5.6451 |
| 72 | train | ild_db | 12 | 0.5618 | 6.1525 | 5.5907 |
| 60 | train | icc | 12 | 0.0695 | 0.2932 | 0.2236 |
| 93 | dev | envelope_db | 4 | 4.1123 | 9.6890 | 5.5766 |
| 81 | train | icc | 12 | 0.0265 | 0.2485 | 0.2221 |
| 33 | train | icc | 12 | 0.0328 | 0.2507 | 0.2179 |
| 57 | train | sustain_db | 12 | 3.3042 | 8.7513 | 5.4471 |
| 54 | dev | early_db | 4 | 3.9344 | 9.3378 | 5.4033 |
| 108 | train | tuning_cents | 12 | 0.7998 | 6.2026 | 5.4028 |
| 21 | dev | level_db | 4 | 0.8124 | 6.1933 | 5.3809 |
| 24 | train | level_db | 12 | 0.7628 | 6.1285 | 5.3656 |
| 81 | dev | early_db | 4 | 3.5498 | 8.9031 | 5.3533 |
| 21 | train | level_db | 12 | 0.7402 | 6.0826 | 5.3423 |
| 48 | train | ild_db | 12 | 2.8283 | 8.1679 | 5.3396 |
| 54 | dev | sustain_db | 4 | 3.4701 | 8.7678 | 5.2977 |
| 36 | train | envelope_db | 12 | 1.3782 | 6.6696 | 5.2914 |
| 36 | train | sustain_db | 12 | 3.4308 | 8.7129 | 5.2821 |
| 36 | dev | sustain_db | 4 | 3.3781 | 8.6507 | 5.2726 |
| 60 | dev | sustain_db | 4 | 4.5848 | 9.8349 | 5.2501 |
| 69 | train | early_db | 12 | 3.6388 | 8.8695 | 5.2307 |
| 36 | dev | envelope_db | 4 | 1.5058 | 6.7317 | 5.2259 |
| 102 | train | decay_db_s | 12 | 6.9478 | 17.3460 | 10.3983 |
| 48 | dev | ild_db | 4 | 2.8345 | 8.0090 | 5.1745 |
| 54 | train | early_db | 12 | 3.9551 | 9.1135 | 5.1585 |
| 24 | dev | level_db | 4 | 0.6192 | 5.7659 | 5.1467 |
| 60 | dev | envelope_db | 4 | 1.1310 | 6.2646 | 5.1337 |
| 54 | train | sustain_db | 12 | 3.8525 | 8.9800 | 5.1275 |
| 69 | dev | early_db | 4 | 3.4539 | 8.5749 | 5.1210 |
| 81 | train | early_db | 12 | 3.9105 | 9.0167 | 5.1062 |
| 81 | dev | noise_db | 4 | 3.9643 | 9.0701 | 5.1058 |
| 84 | train | partial_db | 12 | 3.7643 | 8.8682 | 5.1038 |
| 105 | train | level_db | 12 | 0.9905 | 6.0246 | 5.0341 |
| 36 | train | icc | 12 | 0.0406 | 0.2414 | 0.2008 |
| 48 | dev | sustain_db | 4 | 3.7670 | 8.7834 | 5.0164 |
| 81 | train | noise_db | 12 | 4.8631 | 9.8788 | 5.0156 |
| 54 | dev | attack_db | 4 | 3.8839 | 8.8735 | 4.9896 |
| 36 | dev | icc | 4 | 0.0374 | 0.2357 | 0.1983 |
| 66 | train | partial_db | 12 | 5.0057 | 9.9599 | 4.9543 |
| 48 | train | sustain_db | 12 | 3.9514 | 8.8791 | 4.9277 |
| 60 | train | envelope_db | 12 | 1.0965 | 6.0080 | 4.9115 |
| 66 | dev | partial_db | 4 | 4.9063 | 9.8166 | 4.9102 |
| 108 | dev | tuning_cents | 4 | 0.8644 | 5.7676 | 4.9032 |
| 57 | dev | early_db | 4 | 4.0089 | 8.9101 | 4.9012 |
| 81 | train | ild_db | 12 | 3.3702 | 8.2658 | 4.8956 |
| 60 | train | sustain_db | 12 | 4.7593 | 9.5969 | 4.8377 |
| 57 | dev | ild_db | 4 | 1.6516 | 6.4639 | 4.8124 |
| 24 | train | ild_db | 12 | 0.4986 | 5.2894 | 4.7908 |
| 45 | dev | partial_db | 4 | 5.8187 | 10.5823 | 4.7636 |
| 24 | dev | ild_db | 4 | 0.5007 | 5.2567 | 4.7559 |
| 105 | dev | icc | 4 | 0.1451 | 0.3344 | 0.1894 |
| 57 | train | ild_db | 12 | 1.5996 | 6.3177 | 4.7181 |
| 66 | train | sustain_db | 12 | 3.7274 | 8.4026 | 4.6751 |
| 54 | train | attack_db | 12 | 4.2009 | 8.8084 | 4.6075 |
| 21 | dev | tuning_cents | 4 | 0.0403 | 4.6273 | 4.5869 |
| 90 | train | icc | 12 | 0.0767 | 0.2599 | 0.1832 |
| 21 | train | tuning_cents | 12 | 0.0520 | 4.6258 | 4.5738 |
| 27 | dev | partial_db | 16 | 7.0378 | 11.6095 | 4.5717 |
| 66 | dev | sustain_db | 4 | 3.6356 | 8.1711 | 4.5354 |
| 84 | dev | partial_db | 4 | 4.0722 | 8.6058 | 4.5336 |
| 72 | dev | envelope_db | 4 | 0.8787 | 5.3899 | 4.5111 |
| 96 | dev | envelope_db | 4 | 2.2295 | 6.7309 | 4.5013 |
| 24 | dev | icc | 4 | 0.0208 | 0.2005 | 0.1797 |
| 57 | train | early_db | 12 | 4.0954 | 8.5826 | 4.4872 |
| 24 | train | icc | 12 | 0.0210 | 0.1987 | 0.1777 |
| 60 | dev | early_db | 4 | 3.3566 | 7.7951 | 4.4385 |
| 93 | dev | rise_ms | 4 | 0.6094 | 9.4375 | 8.8281 |
| 48 | dev | tuning_cents | 4 | 0.0741 | 4.4826 | 4.4085 |
| 90 | dev | icc | 4 | 0.0736 | 0.2487 | 0.1751 |
| 72 | train | envelope_db | 12 | 0.9450 | 5.3230 | 4.3781 |
| 105 | dev | level_db | 4 | 0.9565 | 5.3248 | 4.3683 |
| 60 | train | early_db | 12 | 3.4359 | 7.8039 | 4.3680 |
| 36 | train | ild_db | 12 | 0.6738 | 5.0181 | 4.3442 |
| 24 | train | rise_ms | 12 | 1.7153 | 10.3715 | 8.6562 |
| 57 | train | icc | 12 | 0.0618 | 0.2341 | 0.1723 |
| 69 | train | attack_db | 12 | 3.5537 | 7.8532 | 4.2995 |
| 45 | dev | sustain_db | 4 | 3.7985 | 8.0828 | 4.2844 |
| 45 | train | sustain_db | 12 | 3.7627 | 8.0288 | 4.2661 |
| 24 | dev | noise_db | 4 | 4.2178 | 8.4817 | 4.2640 |
| 45 | train | partial_db | 12 | 5.8358 | 10.0979 | 4.2621 |
| 30 | dev | icc | 4 | 0.0290 | 0.1995 | 0.1704 |
| 69 | dev | icc | 4 | 0.0302 | 0.2005 | 0.1703 |
| 93 | train | rise_ms | 12 | 0.7309 | 9.2431 | 8.5122 |
| 78 | dev | partial_db | 4 | 3.6103 | 7.8576 | 4.2473 |
| 102 | train | icc | 12 | 0.2408 | 0.4106 | 0.1699 |
| 24 | dev | tuning_cents | 4 | 0.0557 | 4.2977 | 4.2420 |
| 48 | train | tuning_cents | 12 | 0.0853 | 4.3196 | 4.2344 |
| 24 | train | tuning_cents | 12 | 0.0691 | 4.2977 | 4.2286 |
| 24 | dev | rise_ms | 4 | 1.7969 | 10.2448 | 8.4479 |
| 96 | train | envelope_db | 12 | 2.2443 | 6.4457 | 4.2014 |
| 102 | dev | icc | 4 | 0.2312 | 0.3979 | 0.1667 |
| 36 | dev | ild_db | 4 | 0.7227 | 4.8867 | 4.1639 |
| 66 | dev | tuning_cents | 4 | 0.0916 | 4.2414 | 4.1498 |
| 30 | dev | noise_db | 4 | 3.3016 | 7.4511 | 4.1495 |
| 42 | dev | envelope_db | 4 | 0.8811 | 5.0294 | 4.1483 |
| 54 | dev | ild_db | 4 | 0.8412 | 4.9856 | 4.1444 |
| 42 | dev | rise_ms | 4 | 0.8438 | 9.0833 | 8.2396 |
| 69 | train | icc | 12 | 0.0334 | 0.1980 | 0.1646 |
| 30 | train | icc | 12 | 0.0361 | 0.1988 | 0.1627 |
| 54 | train | ild_db | 12 | 0.9388 | 5.0031 | 4.0643 |
| 42 | train | envelope_db | 12 | 0.9622 | 5.0229 | 4.0607 |
| 69 | dev | attack_db | 4 | 3.4490 | 7.4914 | 4.0423 |
| 66 | train | tuning_cents | 12 | 0.1133 | 4.1455 | 4.0322 |
| 105 | train | icc | 11 | 0.1185 | 0.2791 | 0.1605 |
| 21 | dev | icc | 4 | 0.0279 | 0.1881 | 0.1602 |
| 72 | train | partial_db | 12 | 4.8248 | 8.8261 | 4.0013 |
| 21 | train | icc | 12 | 0.0299 | 0.1899 | 0.1600 |
| 57 | dev | icc | 4 | 0.0637 | 0.2233 | 0.1596 |
| 57 | dev | attack_db | 4 | 3.8649 | 7.8213 | 3.9564 |
| 99 | dev | decay_db_s | 16 | 1.2605 | 9.1318 | 7.8712 |
| 42 | dev | ild_db | 4 | 0.3791 | 4.3013 | 3.9222 |
| 42 | train | ild_db | 12 | 0.4636 | 4.3702 | 3.9066 |
| 84 | dev | icc | 4 | 0.0310 | 0.1872 | 0.1562 |
| 72 | dev | partial_db | 4 | 4.9941 | 8.8507 | 3.8567 |
| 54 | train | icc | 12 | 0.0843 | 0.2382 | 0.1538 |
| 48 | dev | icc | 4 | 0.0597 | 0.2126 | 0.1528 |
| 81 | train | attack_db | 12 | 3.9259 | 7.7431 | 3.8172 |
| 102 | dev | decay_db_s | 4 | 2.5548 | 10.1820 | 7.6272 |
| 24 | train | noise_db | 12 | 4.2311 | 8.0422 | 3.8110 |
| 81 | dev | attack_db | 4 | 3.4066 | 7.2036 | 3.7969 |
| 51 | dev | envelope_db | 16 | 1.5203 | 5.2720 | 3.7517 |
| 54 | dev | level_db | 4 | 0.7826 | 4.5302 | 3.7476 |
| 42 | train | rise_ms | 12 | 2.4983 | 9.9201 | 7.4219 |
| 57 | dev | envelope_db | 4 | 0.5036 | 4.2110 | 3.7075 |
| 30 | train | sustain_db | 12 | 3.4762 | 7.1146 | 3.6384 |
| 108 | train | icc | 7 | 0.1779 | 0.3235 | 0.1455 |
| 57 | train | envelope_db | 12 | 0.4976 | 4.1358 | 3.6381 |
| 84 | train | icc | 12 | 0.0352 | 0.1805 | 0.1453 |
| 54 | dev | icc | 4 | 0.0845 | 0.2294 | 0.1449 |
| 54 | train | level_db | 12 | 0.9202 | 4.5244 | 3.6041 |
| 108 | dev | icc | 2 | 0.1026 | 0.2459 | 0.1433 |
| 27 | dev | early_db | 16 | 4.2911 | 7.8355 | 3.5444 |
| 48 | dev | partial_db | 4 | 5.4199 | 8.9629 | 3.5430 |
| 42 | dev | icc | 4 | 0.0237 | 0.1620 | 0.1383 |
| 48 | train | icc | 12 | 0.0628 | 0.2007 | 0.1379 |
| 81 | dev | sustain_db | 4 | 3.0192 | 6.4222 | 3.4030 |
| 75 | dev | early_db | 16 | 5.8216 | 9.2220 | 3.4005 |
| 45 | dev | ild_db | 4 | 1.3857 | 4.7732 | 3.3875 |
| 81 | train | sustain_db | 12 | 3.8681 | 7.2432 | 3.3751 |
| 84 | dev | decay_db_s | 4 | 3.2794 | 10.0260 | 6.7466 |
| 42 | dev | tuning_cents | 4 | 0.0242 | 3.3964 | 3.3723 |
| 30 | dev | sustain_db | 4 | 3.4944 | 6.8576 | 3.3632 |
| 54 | dev | tuning_cents | 4 | 0.0459 | 3.4006 | 3.3546 |
| 36 | train | early_db | 12 | 3.2999 | 6.6537 | 3.3539 |
| 45 | train | ild_db | 12 | 1.4739 | 4.8201 | 3.3462 |
| 54 | train | tuning_cents | 12 | 0.0516 | 3.3885 | 3.3370 |
| 72 | train | icc | 12 | 0.0273 | 0.1602 | 0.1329 |
| 57 | train | attack_db | 12 | 4.3452 | 7.6629 | 3.3178 |
| 21 | train | ild_db | 12 | 1.0294 | 4.3331 | 3.3037 |
| 36 | dev | early_db | 4 | 3.3528 | 6.6390 | 3.2862 |
| 42 | train | icc | 12 | 0.0283 | 0.1594 | 0.1310 |
| 30 | train | ild_db | 12 | 0.6970 | 3.9658 | 3.2688 |
| 45 | dev | tuning_cents | 4 | 0.0258 | 3.2614 | 3.2356 |
| 60 | train | level_db | 12 | 1.8140 | 5.0486 | 3.2346 |
| 30 | dev | ild_db | 4 | 0.6889 | 3.9180 | 3.2291 |
| 96 | dev | ild_db | 4 | 0.5341 | 3.7614 | 3.2274 |
| 90 | dev | decay_db_s | 4 | 2.6622 | 9.0968 | 6.4346 |
| 81 | train | level_db | 12 | 1.4715 | 4.6769 | 3.2054 |
| 33 | train | ild_db | 12 | 0.4516 | 3.6397 | 3.1881 |
| 33 | dev | ild_db | 4 | 0.4039 | 3.5808 | 3.1769 |
| 66 | train | envelope_db | 12 | 0.7594 | 3.9320 | 3.1726 |
| 78 | train | partial_db | 12 | 3.7173 | 6.8860 | 3.1686 |
| 33 | train | sustain_db | 12 | 4.4742 | 7.6107 | 3.1365 |
| 33 | dev | early_db | 4 | 4.2338 | 7.3624 | 3.1286 |
| 33 | dev | sustain_db | 4 | 4.3389 | 7.4593 | 3.1204 |
| 96 | train | ild_db | 12 | 0.5386 | 3.6587 | 3.1201 |
| 99 | dev | tuning_cents | 16 | 1.8302 | 4.9368 | 3.1066 |
| 27 | dev | icc | 16 | 0.1048 | 0.2288 | 0.1240 |
| 33 | train | early_db | 12 | 4.3061 | 7.3946 | 3.0885 |
| 21 | dev | ild_db | 4 | 1.1157 | 4.2011 | 3.0855 |
| 66 | dev | envelope_db | 4 | 0.7297 | 3.8151 | 3.0855 |
| 60 | dev | tuning_cents | 4 | 0.0397 | 3.0894 | 3.0497 |
| 42 | train | tuning_cents | 12 | 0.0279 | 3.0643 | 3.0364 |
| 45 | train | tuning_cents | 12 | 0.0298 | 3.0467 | 3.0169 |
| 54 | train | noise_db | 12 | 8.7670 | 11.7748 | 3.0078 |
| 51 | dev | partial_db | 16 | 8.0123 | 11.0151 | 3.0028 |
| 72 | dev | icc | 4 | 0.0292 | 0.1488 | 0.1196 |
| 66 | dev | early_db | 4 | 4.3951 | 7.3739 | 2.9788 |
| 57 | dev | tuning_cents | 4 | 0.0456 | 3.0133 | 2.9677 |
| 69 | dev | envelope_db | 4 | 1.0393 | 4.0056 | 2.9663 |
| 57 | train | tuning_cents | 12 | 0.0437 | 2.9951 | 2.9514 |
| 84 | train | decay_db_s | 12 | 3.4077 | 9.2562 | 5.8485 |
| 66 | train | early_db | 12 | 4.4397 | 7.3604 | 2.9207 |
| 48 | train | partial_db | 12 | 5.7836 | 8.6737 | 2.8901 |
| 60 | dev | level_db | 4 | 1.9064 | 4.7880 | 2.8815 |
| 81 | dev | level_db | 4 | 1.5948 | 4.4717 | 2.8769 |
| 45 | dev | early_db | 4 | 4.1166 | 6.9932 | 2.8766 |
| 90 | train | decay_db_s | 12 | 2.7548 | 8.4776 | 5.7228 |
| 27 | dev | attack_db | 16 | 5.2584 | 8.0753 | 2.8170 |
| 21 | train | noise_db | 12 | 4.7002 | 7.5152 | 2.8150 |
| 54 | train | envelope_db | 12 | 0.4593 | 3.2680 | 2.8087 |
| 90 | train | ild_db | 12 | 0.8805 | 3.6638 | 2.7833 |
| 81 | train | envelope_db | 12 | 1.3902 | 4.1653 | 2.7751 |
| 69 | train | envelope_db | 12 | 1.0678 | 3.8425 | 2.7747 |
| 105 | dev | tuning_cents | 4 | 0.2524 | 3.0091 | 2.7567 |
| 45 | train | early_db | 12 | 4.1572 | 6.9120 | 2.7548 |
| 66 | train | attack_db | 12 | 3.8956 | 6.6420 | 2.7464 |
| 90 | dev | ild_db | 4 | 0.8838 | 3.6187 | 2.7349 |
| 45 | dev | icc | 4 | 0.0197 | 0.1285 | 0.1088 |
| 60 | train | tuning_cents | 12 | 0.0472 | 2.7485 | 2.7012 |
| 42 | dev | sustain_db | 4 | 3.6944 | 6.3810 | 2.6866 |
| 54 | dev | envelope_db | 4 | 0.3870 | 3.0707 | 2.6838 |
| 42 | train | sustain_db | 12 | 3.8166 | 6.4929 | 2.6763 |
| 66 | dev | attack_db | 4 | 4.1076 | 6.7725 | 2.6649 |
| 78 | train | rise_ms | 12 | 7.2309 | 12.5521 | 5.3212 |
| 81 | dev | envelope_db | 4 | 1.4782 | 4.1375 | 2.6593 |
| 69 | train | noise_db | 12 | 4.9614 | 7.6167 | 2.6554 |
| 30 | train | early_db | 12 | 3.4995 | 6.1518 | 2.6523 |
| 60 | train | attack_db | 12 | 3.6247 | 6.2477 | 2.6230 |
| 69 | dev | noise_db | 4 | 4.9536 | 7.5342 | 2.5805 |
| 78 | dev | rise_ms | 4 | 7.0573 | 12.1875 | 5.1302 |
| 60 | dev | attack_db | 4 | 3.6332 | 6.1970 | 2.5638 |
| 30 | train | attack_db | 12 | 4.3742 | 6.8925 | 2.5183 |
| 27 | dev | sustain_db | 16 | 4.3058 | 6.8071 | 2.5014 |
| 96 | dev | rise_ms | 4 | 0.7031 | 5.6979 | 4.9948 |
| 27 | dev | ild_db | 16 | 2.8971 | 5.3378 | 2.4407 |
| 102 | dev | envelope_db | 4 | 4.0268 | 6.4591 | 2.4323 |
| 33 | train | noise_db | 11 | 7.0990 | 9.5186 | 2.4196 |
| 75 | dev | ild_db | 16 | 7.0715 | 9.4908 | 2.4193 |
| 96 | train | rise_ms | 12 | 1.0208 | 5.8351 | 4.8142 |
| 45 | train | icc | 12 | 0.0269 | 0.1227 | 0.0958 |
| 42 | dev | partial_db | 4 | 6.0894 | 8.4784 | 2.3890 |
| 54 | dev | noise_db | 4 | 9.5789 | 11.9647 | 2.3857 |
| 105 | train | tuning_cents | 12 | 0.2400 | 2.5872 | 2.3472 |
| 96 | train | tuning_cents | 12 | 0.3068 | 2.6389 | 2.3321 |
| 102 | dev | tuning_cents | 4 | 0.4109 | 2.6951 | 2.2841 |
| 33 | dev | tuning_cents | 4 | 0.0493 | 2.3088 | 2.2595 |
| 42 | train | partial_db | 12 | 5.9562 | 8.2089 | 2.2526 |
| 105 | train | ild_db | 11 | 0.6558 | 2.9019 | 2.2461 |
| 36 | dev | tuning_cents | 4 | 0.0324 | 2.2537 | 2.2213 |
| 84 | dev | rise_ms | 4 | 3.4479 | 7.8594 | 4.4115 |
| 66 | dev | noise_db | 4 | 4.7818 | 6.9779 | 2.1962 |
| 33 | train | tuning_cents | 12 | 0.0481 | 2.2371 | 2.1890 |
| 36 | train | tuning_cents | 12 | 0.0397 | 2.2089 | 2.1692 |
| 30 | dev | early_db | 4 | 3.5558 | 5.6988 | 2.1430 |
| 96 | dev | tuning_cents | 4 | 0.4198 | 2.5480 | 2.1282 |
| 30 | dev | attack_db | 4 | 4.3760 | 6.4926 | 2.1165 |
| 36 | train | attack_db | 12 | 3.8517 | 5.9677 | 2.1160 |
| 90 | dev | tuning_cents | 4 | 0.1623 | 2.2555 | 2.0932 |
| 93 | train | tuning_cents | 12 | 0.4806 | 2.5550 | 2.0744 |
| 84 | train | envelope_db | 12 | 1.2492 | 3.3017 | 2.0525 |
| 84 | dev | envelope_db | 4 | 0.8544 | 2.9028 | 2.0484 |
| 45 | dev | level_db | 4 | 0.2460 | 2.2710 | 2.0250 |
| 69 | dev | ild_db | 4 | 3.3092 | 5.3296 | 2.0204 |
| 30 | dev | tuning_cents | 4 | 0.0188 | 2.0315 | 2.0127 |
| 78 | dev | decay_db_s | 4 | 1.5001 | 5.5097 | 4.0096 |
| 78 | train | decay_db_s | 12 | 1.3113 | 5.2928 | 3.9815 |
| 33 | train | rise_ms | 12 | 3.2326 | 7.1997 | 3.9670 |
| 48 | dev | level_db | 4 | 0.4811 | 2.4638 | 1.9827 |
| 33 | dev | level_db | 4 | 0.6898 | 2.6441 | 1.9543 |
| 45 | train | envelope_db | 12 | 1.0336 | 2.9877 | 1.9540 |
| 90 | train | tuning_cents | 12 | 0.2639 | 2.2063 | 1.9424 |
| 24 | dev | sustain_db | 4 | 3.2016 | 5.1412 | 1.9396 |
| 105 | train | envelope_db | 12 | 3.1509 | 5.0837 | 1.9328 |
| 30 | train | tuning_cents | 12 | 0.0220 | 1.9432 | 1.9212 |
| 66 | train | noise_db | 12 | 4.7258 | 6.6447 | 1.9189 |
| 21 | train | sustain_db | 12 | 3.5642 | 5.4427 | 1.8785 |
| 81 | train | partial_db | 12 | 4.2872 | 6.1625 | 1.8753 |
| 69 | dev | decay_db_s | 4 | 1.6025 | 5.3058 | 3.7033 |
| 36 | dev | attack_db | 4 | 3.9558 | 5.8044 | 1.8486 |
| 45 | dev | envelope_db | 4 | 1.0477 | 2.8874 | 1.8397 |
| 102 | train | tuning_cents | 12 | 0.3916 | 2.2261 | 1.8345 |
| 99 | dev | icc | 16 | 0.2396 | 0.3120 | 0.0724 |
| 78 | dev | tuning_cents | 4 | 0.1091 | 1.9174 | 1.8083 |
| 21 | dev | sustain_db | 4 | 3.5394 | 5.3350 | 1.7956 |
| 93 | dev | tuning_cents | 4 | 0.7651 | 2.5564 | 1.7913 |
| 105 | dev | envelope_db | 4 | 4.4225 | 6.2014 | 1.7788 |
| 45 | train | attack_db | 12 | 4.4222 | 6.1878 | 1.7656 |
| 33 | train | attack_db | 12 | 4.0909 | 5.8536 | 1.7627 |
| 48 | train | level_db | 12 | 0.4845 | 2.2422 | 1.7578 |
| 60 | train | rise_ms | 12 | 3.4913 | 7.0035 | 3.5122 |
| 78 | train | tuning_cents | 12 | 0.0981 | 1.8449 | 1.7469 |
| 45 | dev | attack_db | 4 | 4.3885 | 6.1341 | 1.7456 |
| 33 | train | level_db | 12 | 0.6516 | 2.3906 | 1.7390 |
| 51 | dev | sustain_db | 16 | 5.6499 | 7.3649 | 1.7150 |
| 36 | dev | level_db | 4 | 0.5313 | 2.2325 | 1.7012 |
| 24 | train | sustain_db | 12 | 3.4070 | 5.0987 | 1.6917 |
| 24 | dev | envelope_db | 4 | 2.2019 | 3.8925 | 1.6906 |
| 96 | train | icc | 12 | 0.0217 | 0.0890 | 0.0673 |
| 21 | dev | noise_db | 4 | 4.6167 | 6.2963 | 1.6796 |
| 33 | train | envelope_db | 12 | 2.0161 | 3.6928 | 1.6767 |
| 48 | dev | noise_db | 4 | 4.2493 | 5.9184 | 1.6690 |
| 102 | train | envelope_db | 12 | 3.0951 | 4.7354 | 1.6403 |
| 66 | dev | level_db | 4 | 0.2895 | 1.9295 | 1.6400 |
| 33 | dev | attack_db | 4 | 3.9185 | 5.5384 | 1.6199 |
| 69 | train | decay_db_s | 12 | 1.7528 | 4.9796 | 3.2268 |
| 30 | dev | level_db | 4 | 0.9294 | 2.5330 | 1.6037 |
| 84 | dev | tuning_cents | 4 | 0.2496 | 1.8494 | 1.5998 |
| 30 | train | level_db | 12 | 0.9147 | 2.5095 | 1.5948 |
| 69 | train | ild_db | 12 | 3.5416 | 5.1323 | 1.5907 |
| 48 | dev | attack_db | 4 | 3.7651 | 5.3485 | 1.5834 |
| 48 | train | attack_db | 12 | 3.8795 | 5.4629 | 1.5834 |
| 60 | dev | decay_db_s | 4 | 1.0946 | 4.2575 | 3.1628 |
| 42 | dev | decay_db_s | 4 | 0.4240 | 3.5819 | 3.1579 |
| 30 | dev | decay_db_s | 4 | 0.2001 | 3.3250 | 3.1249 |
| 81 | train | tuning_cents | 12 | 0.1693 | 1.7272 | 1.5578 |
| 30 | train | decay_db_s | 12 | 0.2218 | 3.2997 | 3.0779 |
| 51 | dev | level_db | 16 | 1.4569 | 2.9842 | 1.5273 |
| 84 | train | ild_db | 12 | 2.8952 | 4.4115 | 1.5163 |
| 42 | train | decay_db_s | 12 | 0.4818 | 3.5038 | 3.0220 |
| 51 | dev | tuning_cents | 16 | 1.3721 | 2.8793 | 1.5072 |
| 69 | dev | tuning_cents | 4 | 0.0754 | 1.5433 | 1.4679 |
| 84 | train | tuning_cents | 12 | 0.3948 | 1.8580 | 1.4632 |
| 93 | train | decay_db_s | 12 | 5.8159 | 8.7280 | 2.9120 |
| 84 | train | rise_ms | 12 | 2.8247 | 5.6875 | 2.8628 |
| 96 | dev | icc | 4 | 0.0272 | 0.0838 | 0.0566 |
| 36 | train | level_db | 12 | 0.7654 | 2.1752 | 1.4098 |
| 21 | dev | decay_db_s | 4 | 0.2701 | 3.0891 | 2.8190 |
| 105 | dev | ild_db | 4 | 0.7163 | 2.1234 | 1.4071 |
| 69 | train | tuning_cents | 12 | 0.0679 | 1.4640 | 1.3961 |
| 60 | train | decay_db_s | 12 | 1.2183 | 3.9730 | 2.7546 |
| 21 | train | decay_db_s | 12 | 0.2502 | 2.9837 | 2.7334 |
| 45 | train | level_db | 12 | 0.5120 | 1.8741 | 1.3621 |
| 81 | dev | tuning_cents | 4 | 0.1831 | 1.5338 | 1.3507 |
| 81 | train | decay_db_s | 12 | 2.3336 | 5.0198 | 2.6862 |
| 24 | dev | early_db | 4 | 3.8914 | 5.2306 | 1.3391 |
| 99 | dev | envelope_db | 16 | 3.7643 | 5.0963 | 1.3320 |
| 69 | train | level_db | 12 | 0.6201 | 1.9042 | 1.2841 |
| 42 | dev | level_db | 4 | 2.0238 | 3.2781 | 1.2543 |
| 54 | dev | decay_db_s | 4 | 1.2056 | 3.6839 | 2.4783 |
| 69 | dev | level_db | 4 | 0.7765 | 2.0154 | 1.2389 |
| 24 | train | envelope_db | 12 | 2.6442 | 3.8611 | 1.2169 |
| 21 | train | early_db | 12 | 3.9825 | 5.1868 | 1.2043 |
| 66 | train | level_db | 12 | 0.5978 | 1.7963 | 1.1985 |
| 72 | dev | decay_db_s | 4 | 1.6167 | 4.0062 | 2.3895 |
| 93 | dev | decay_db_s | 4 | 4.7506 | 7.1336 | 2.3830 |
| 72 | dev | tuning_cents | 4 | 0.0359 | 1.2218 | 1.1859 |
| 48 | train | decay_db_s | 12 | 1.1574 | 3.5233 | 2.3659 |
| 54 | train | decay_db_s | 12 | 1.2803 | 3.6170 | 2.3367 |
| 72 | train | decay_db_s | 12 | 1.7845 | 4.1183 | 2.3338 |
| 48 | dev | decay_db_s | 4 | 1.0946 | 3.4230 | 2.3284 |
| 72 | train | tuning_cents | 12 | 0.0414 | 1.1815 | 1.1401 |
| 45 | dev | noise_db | 3 | 6.2689 | 7.4085 | 1.1396 |
| 24 | train | early_db | 12 | 4.0558 | 5.1927 | 1.1369 |
| 42 | train | level_db | 12 | 1.8658 | 2.9923 | 1.1265 |
| 57 | dev | decay_db_s | 4 | 0.8695 | 3.1078 | 2.2383 |
| 33 | dev | envelope_db | 4 | 2.5393 | 3.6581 | 1.1188 |
| 48 | dev | envelope_db | 4 | 1.7774 | 2.8843 | 1.1068 |
| 24 | dev | attack_db | 4 | 5.0895 | 6.1585 | 1.0690 |
| 24 | dev | decay_db_s | 4 | 0.4125 | 2.5068 | 2.0943 |
| 21 | dev | early_db | 4 | 4.0545 | 5.1002 | 1.0457 |
| 24 | train | decay_db_s | 12 | 0.3765 | 2.4573 | 2.0808 |
| 57 | train | decay_db_s | 12 | 0.9221 | 3.0020 | 2.0800 |
| 30 | train | noise_db | 9 | 5.7026 | 6.7417 | 1.0390 |
| 81 | dev | decay_db_s | 4 | 2.4668 | 4.5316 | 2.0648 |
| 48 | train | envelope_db | 12 | 2.0222 | 2.9628 | 0.9405 |
| 60 | dev | rise_ms | 4 | 2.9531 | 4.8281 | 1.8750 |
| 84 | dev | ild_db | 4 | 3.0548 | 3.9692 | 0.9144 |
| 33 | train | decay_db_s | 12 | 0.7641 | 2.5927 | 1.8286 |
| 33 | dev | decay_db_s | 4 | 0.7066 | 2.5344 | 1.8277 |
| 81 | dev | partial_db | 4 | 4.2571 | 5.1342 | 0.8771 |
| 57 | dev | level_db | 4 | 1.5318 | 2.3984 | 0.8666 |
| 27 | dev | tuning_cents | 16 | 3.4097 | 4.2689 | 0.8593 |
| 21 | train | envelope_db | 12 | 2.4734 | 3.3192 | 0.8459 |
| 66 | train | decay_db_s | 12 | 1.4890 | 3.1349 | 1.6458 |
| 36 | train | decay_db_s | 12 | 0.4144 | 2.0112 | 1.5968 |
| 66 | dev | decay_db_s | 4 | 1.4596 | 3.0559 | 1.5963 |
| 57 | train | level_db | 12 | 1.9411 | 2.7374 | 0.7964 |
| 27 | dev | noise_db | 16 | 5.2682 | 6.0397 | 0.7715 |
| 24 | train | attack_db | 12 | 5.5375 | 6.3087 | 0.7712 |
| 36 | dev | decay_db_s | 4 | 0.4060 | 1.9059 | 1.5000 |
| 51 | dev | early_db | 16 | 5.4516 | 6.1935 | 0.7419 |
| 21 | dev | envelope_db | 4 | 2.6132 | 3.3296 | 0.7165 |
| 45 | dev | decay_db_s | 4 | 0.4935 | 1.8936 | 1.4001 |
| 45 | train | decay_db_s | 12 | 0.5377 | 1.8979 | 1.3602 |
| 102 | dev | rise_ms | 4 | 2.4531 | 3.6771 | 1.2240 |
| 102 | dev | ild_db | 4 | 2.3908 | 3.0024 | 0.6116 |
| 102 | train | rise_ms | 12 | 2.8403 | 3.9653 | 1.1250 |
| 102 | train | ild_db | 12 | 2.1800 | 2.7363 | 0.5563 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| A1v2 | 33 | train | noise_db | gained | - | 10.6267 |
| F#1v5 | 30 | train | noise_db | gained | - | 3.9152 |
| F#1v6 | 30 | train | noise_db | gained | - | 3.8347 |
| F#2v10 | 42 | train | noise_db | gained | - | 9.6084 |
| F#2v2 | 42 | train | noise_db | gained | - | 3.3427 |
| F#2v4 | 42 | train | noise_db | gained | - | 8.4082 |
| F#2v6 | 42 | train | noise_db | gained | - | 11.2185 |
