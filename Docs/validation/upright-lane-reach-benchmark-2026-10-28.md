# Recording benchmark: candidate 0.4.1 against 0.4.1 at 3c65822

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at 3c65822

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 2.88 | 0.30 | 2.52 | 4.13 | 3.92 | 5.28 | 8.94 | 2.09 | 0.11 | 2.74 | 6.58 | 0.65 |
| dev (21) | 6.26 | 1.90 | 5.15 | 5.62 | 6.40 | 8.40 | 9.70 | 4.31 | 0.18 | 5.67 | 10.14 | 2.31 |
| train / bass A0-B2 (30) | 2.38 | 0.24 | 1.61 | 3.14 | 2.16 | 2.40 | 12.66 | 1.18 | 0.08 | 2.05 | 12.22 | 0.22 |
| train / middle C3-B5 (69) | 2.55 | 0.22 | 2.39 | 4.02 | 3.28 | 4.44 | 9.08 | 1.99 | 0.10 | 2.30 | 5.94 | 0.29 |
| train / treble C6-C8 (38) | 3.88 | 0.49 | 3.54 | 5.13 | 6.47 | 9.17 | 5.73 | 3.06 | 0.17 | 4.08 | 3.29 | 1.66 |
| dev / bass A0-B2 (5) | 6.07 | 1.41 | 2.04 | 3.94 | 5.02 | 7.25 | 14.68 | 5.12 | 0.19 | 2.42 | 1.13 | 1.51 |
| dev / middle C3-B5 (11) | 5.66 | 1.32 | 3.29 | 5.71 | 5.67 | 7.10 | 8.44 | 4.57 | 0.15 | 5.61 | 13.51 | 2.31 |
| dev / treble C6-C8 (5) | 7.75 | 3.67 | 12.34 | 7.09 | 9.39 | 12.43 | 7.50 | 2.94 | 0.26 | 9.04 | 11.75 | 3.11 |

## candidate 0.4.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 2.54 | 0.25 | 1.99 | 4.13 | 3.89 | 4.46 | 8.93 | 2.13 | 0.13 | 2.28 | 7.11 | 0.67 |
| dev (21) | 5.86 | 1.90 | 4.27 | 5.67 | 6.22 | 7.76 | 9.68 | 4.78 | 0.18 | 5.00 | 10.28 | 2.25 |
| train / bass A0-B2 (30) | 2.33 | 0.24 | 1.65 | 3.14 | 2.11 | 2.34 | 12.61 | 1.17 | 0.08 | 2.05 | 13.71 | 0.22 |
| train / middle C3-B5 (69) | 2.30 | 0.19 | 2.05 | 4.00 | 3.23 | 4.05 | 9.07 | 1.94 | 0.10 | 1.95 | 5.92 | 0.29 |
| train / treble C6-C8 (38) | 3.13 | 0.36 | 2.16 | 5.14 | 6.49 | 6.93 | 5.78 | 3.28 | 0.22 | 3.04 | 4.04 | 1.74 |
| dev / bass A0-B2 (5) | 5.91 | 1.22 | 1.95 | 3.95 | 4.95 | 7.11 | 14.70 | 5.14 | 0.19 | 2.42 | 1.10 | 1.51 |
| dev / middle C3-B5 (11) | 5.40 | 1.11 | 3.52 | 5.86 | 5.62 | 7.00 | 8.45 | 4.66 | 0.15 | 5.50 | 13.43 | 2.27 |
| dev / treble C6-C8 (5) | 6.83 | 4.33 | 8.23 | 6.97 | 8.81 | 10.10 | 7.34 | 4.67 | 0.22 | 6.46 | 12.53 | 2.94 |

## Regressions

Every note and role where candidate 0.4.1 is worse than 0.4.1 at 3c65822 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.1 at 3c65822 | candidate 0.4.1 |
|---|---|---|---|---|
| 94 | train | icc | 0.18 | 0.34 |
| 84 | train | icc | 0.13 | 0.26 |
| 24 | train | rise_ms | 8.17 | 13.54 |
| 100 | train | level_db | 3.54 | 5.77 |
| 33 | train | rise_ms | 10.36 | 13.90 |
| 88 | dev | ild_db | 2.94 | 4.67 |
| 92 | train | icc | 0.23 | 0.30 |
| 100 | train | early_db | 6.42 | 7.80 |
| 84 | train | ild_db | 3.48 | 4.85 |
| 103 | train | rise_ms | 5.74 | 8.46 |
| 100 | train | partial_db | 5.91 | 7.12 |
| 74 | train | icc | 0.07 | 0.12 |
| 100 | train | attack_db | 5.93 | 7.03 |
| 100 | train | icc | 0.20 | 0.24 |
| 100 | train | noise_db | 5.26 | 6.20 |
| 103 | train | envelope_db | 3.23 | 4.13 |
| 45 | train | rise_ms | 7.42 | 9.13 |
| 94 | train | rise_ms | 1.23 | 2.90 |
| 84 | train | rise_ms | 3.08 | 4.68 |
| 84 | train | level_db | 0.94 | 1.67 |
| 88 | dev | tuning_cents | 3.67 | 4.33 |
| 90 | train | icc | 0.12 | 0.14 |
| 103 | train | decay_db_s | 1.46 | 2.68 |
| 100 | train | envelope_db | 3.73 | 4.25 |
