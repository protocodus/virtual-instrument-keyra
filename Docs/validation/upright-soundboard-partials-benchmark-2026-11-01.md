# Recording benchmark: candidate 0.4.1 against 0.4.1 at d5e467d

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at d5e467d

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 6.70 | 0.79 | 2.73 | 5.49 | 5.57 | 6.25 | 7.00 | 2.91 | 0.15 | 2.92 | 9.40 | 1.54 |
| dev (21) | 8.46 | 1.88 | 4.52 | 6.37 | 7.09 | 8.63 | 7.06 | 4.29 | 0.21 | 4.83 | 6.01 | 2.58 |
| train / bass A0-B2 (30) | 9.18 | 1.66 | 2.45 | 6.15 | 5.44 | 6.54 | 9.78 | 3.00 | 0.13 | 2.94 | 15.23 | 2.37 |
| train / middle C3-B5 (69) | 7.12 | 0.54 | 2.72 | 5.50 | 5.27 | 5.70 | 6.39 | 2.40 | 0.11 | 2.31 | 9.85 | 1.39 |
| train / treble C6-C8 (38) | 3.98 | 0.57 | 2.98 | 4.94 | 6.22 | 7.04 | 5.98 | 3.79 | 0.24 | 4.01 | 3.99 | 1.16 |
| dev / bass A0-B2 (5) | 9.00 | 1.40 | 1.87 | 6.14 | 7.49 | 9.08 | 9.59 | 5.06 | 0.22 | 2.19 | 1.93 | 1.42 |
| dev / middle C3-B5 (11) | 8.57 | 1.09 | 3.74 | 6.81 | 6.84 | 8.17 | 6.59 | 4.23 | 0.17 | 5.15 | 9.86 | 2.82 |
| dev / treble C6-C8 (5) | 7.68 | 4.07 | 8.88 | 5.64 | 7.23 | 9.19 | 6.07 | 3.64 | 0.28 | 6.75 | 1.63 | 3.21 |

## candidate 0.4.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 6.70 | 0.81 | 2.73 | 5.49 | 5.82 | 6.45 | 7.06 | 2.97 | 0.15 | 2.97 | 9.64 | 1.52 |
| dev (21) | 8.47 | 1.88 | 4.52 | 6.42 | 7.25 | 8.80 | 7.04 | 4.35 | 0.21 | 4.84 | 5.74 | 2.58 |
| train / bass A0-B2 (30) | 9.18 | 1.74 | 2.45 | 6.12 | 5.47 | 6.55 | 9.81 | 3.00 | 0.13 | 2.94 | 13.89 | 2.37 |
| train / middle C3-B5 (69) | 7.13 | 0.54 | 2.72 | 5.52 | 5.36 | 5.74 | 6.46 | 2.42 | 0.11 | 2.30 | 10.97 | 1.38 |
| train / treble C6-C8 (38) | 3.95 | 0.57 | 2.98 | 4.95 | 6.92 | 7.70 | 6.19 | 3.97 | 0.24 | 4.21 | 3.87 | 1.11 |
| dev / bass A0-B2 (5) | 9.02 | 1.43 | 1.86 | 5.89 | 7.50 | 9.09 | 9.39 | 5.14 | 0.22 | 2.20 | 1.87 | 1.42 |
| dev / middle C3-B5 (11) | 8.58 | 1.09 | 3.74 | 7.03 | 6.96 | 8.27 | 6.58 | 4.22 | 0.16 | 5.16 | 9.38 | 2.83 |
| dev / treble C6-C8 (5) | 7.68 | 4.07 | 8.88 | 5.62 | 7.65 | 9.67 | 6.18 | 3.84 | 0.29 | 6.80 | 1.62 | 3.20 |

## Regressions

Every note and role where candidate 0.4.1 is worse than 0.4.1 at d5e467d by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.1 at d5e467d | candidate 0.4.1 |
|---|---|---|---|---|
| 62 | train | rise_ms | 4.02 | 23.56 |
| 54 | train | rise_ms | 0.59 | 10.04 |
| 58 | train | rise_ms | 6.24 | 10.34 |
| 103 | train | sustain_db | 8.19 | 10.15 |
| 100 | train | sustain_db | 8.06 | 9.74 |
| 33 | train | rise_ms | 4.86 | 8.17 |
| 45 | train | rise_ms | 11.97 | 15.21 |
| 74 | train | rise_ms | 11.51 | 14.50 |
| 96 | train | early_db | 4.86 | 6.30 |
| 103 | train | envelope_db | 4.71 | 6.12 |
| 36 | train | noise_db | 11.88 | 13.18 |
| 103 | train | early_db | 4.97 | 6.14 |
| 48 | train | noise_db | 5.49 | 6.58 |
| 103 | train | ild_db | 2.76 | 3.81 |
| 96 | train | sustain_db | 4.90 | 5.90 |
| 84 | train | icc | 0.23 | 0.27 |
| 96 | train | ild_db | 3.69 | 4.51 |
| 100 | train | early_db | 5.68 | 6.42 |
| 78 | train | noise_db | 4.84 | 5.56 |
| 103 | train | icc | 0.33 | 0.35 |
| 82 | train | icc | 0.15 | 0.18 |
| 84 | train | early_db | 5.12 | 5.80 |
| 94 | train | sustain_db | 15.01 | 15.66 |
| 92 | train | early_db | 4.77 | 5.37 |
| 94 | train | ild_db | 5.66 | 6.24 |
| 94 | train | early_db | 13.87 | 14.45 |
| 78 | train | early_db | 4.68 | 5.25 |
| 86 | train | icc | 0.08 | 0.10 |
| 59 | dev | rise_ms | 4.85 | 5.88 |
| 24 | train | tuning_cents | 5.45 | 5.96 |
