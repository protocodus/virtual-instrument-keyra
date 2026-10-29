# Recording benchmark: candidate 0.4.1 against 0.4.1 at f02e4d5

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at f02e4d5

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 2.42 | 0.26 | 1.98 | 3.67 | 3.48 | 4.44 | 6.83 | 2.12 | 0.13 | 2.25 | 7.02 | 0.61 |
| dev (21) | 5.95 | 1.88 | 4.24 | 5.50 | 6.05 | 7.99 | 7.16 | 4.71 | 0.17 | 5.14 | 9.60 | 2.55 |
| train / bass A0-B2 (30) | 2.33 | 0.24 | 1.66 | 2.87 | 2.04 | 2.35 | 8.10 | 1.16 | 0.08 | 2.05 | 15.51 | 0.22 |
| train / middle C3-B5 (69) | 2.27 | 0.19 | 2.05 | 3.56 | 2.94 | 4.02 | 6.89 | 1.93 | 0.09 | 1.91 | 5.08 | 0.26 |
| train / treble C6-C8 (38) | 2.76 | 0.39 | 2.11 | 4.51 | 5.60 | 6.91 | 5.77 | 3.27 | 0.23 | 3.00 | 3.83 | 1.55 |
| dev / bass A0-B2 (5) | 5.49 | 1.19 | 1.94 | 3.66 | 4.81 | 7.16 | 9.47 | 4.99 | 0.19 | 2.49 | 0.95 | 1.34 |
| dev / middle C3-B5 (11) | 5.76 | 1.11 | 3.48 | 5.67 | 5.63 | 7.30 | 6.29 | 4.62 | 0.14 | 5.75 | 12.09 | 2.83 |
| dev / treble C6-C8 (5) | 6.85 | 4.25 | 8.22 | 6.96 | 8.20 | 10.31 | 7.21 | 4.63 | 0.21 | 6.45 | 12.75 | 3.13 |

## candidate 0.4.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 2.42 | 0.26 | 1.97 | 3.70 | 3.34 | 3.99 | 6.71 | 2.07 | 0.13 | 2.31 | 7.23 | 0.62 |
| dev (21) | 5.95 | 1.88 | 4.25 | 5.52 | 6.00 | 7.61 | 7.42 | 4.61 | 0.17 | 5.15 | 10.26 | 2.55 |
| train / bass A0-B2 (30) | 2.31 | 0.24 | 1.62 | 2.88 | 2.00 | 2.34 | 8.12 | 1.17 | 0.08 | 2.06 | 15.63 | 0.23 |
| train / middle C3-B5 (69) | 2.27 | 0.19 | 2.05 | 3.63 | 2.82 | 3.67 | 6.69 | 1.90 | 0.09 | 1.92 | 5.50 | 0.26 |
| train / treble C6-C8 (38) | 2.79 | 0.39 | 2.11 | 4.48 | 5.35 | 5.94 | 5.69 | 3.15 | 0.24 | 3.23 | 3.74 | 1.58 |
| dev / bass A0-B2 (5) | 5.48 | 1.21 | 1.94 | 3.74 | 4.76 | 7.16 | 9.83 | 5.00 | 0.19 | 2.49 | 1.36 | 1.34 |
| dev / middle C3-B5 (11) | 5.76 | 1.11 | 3.48 | 5.75 | 5.82 | 7.13 | 6.68 | 4.45 | 0.15 | 5.75 | 13.17 | 2.83 |
| dev / treble C6-C8 (5) | 6.85 | 4.25 | 8.22 | 6.78 | 7.65 | 9.11 | 7.12 | 4.58 | 0.20 | 6.51 | 12.77 | 3.13 |

## Regressions

Every note and role where candidate 0.4.1 is worse than 0.4.1 at f02e4d5 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.1 at f02e4d5 | candidate 0.4.1 |
|---|---|---|---|---|
| 33 | train | rise_ms | 21.88 | 32.61 |
| 36 | train | rise_ms | 12.80 | 19.02 |
| 76 | train | rise_ms | 7.62 | 11.60 |
| 90 | train | icc | 0.09 | 0.15 |
| 103 | train | icc | 0.26 | 0.29 |
| 56 | dev | noise_db | 5.98 | 6.75 |
| 54 | train | attack_db | 3.32 | 4.08 |
| 54 | train | early_db | 2.76 | 3.50 |
| 56 | dev | rise_ms | 14.27 | 15.75 |
| 48 | train | rise_ms | 13.75 | 15.13 |
| 103 | train | envelope_db | 3.95 | 4.61 |
| 36 | train | noise_db | 12.34 | 12.98 |
| 58 | train | rise_ms | 4.42 | 5.69 |
| 33 | train | noise_db | 7.95 | 8.57 |
| 72 | dev | icc | 0.17 | 0.19 |
| 50 | train | noise_db | 12.48 | 13.01 |
| 90 | train | envelope_db | 3.38 | 3.91 |
