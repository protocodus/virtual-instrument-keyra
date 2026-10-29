# Recording benchmark: candidate 0.4.1 against 0.4.1 at 98c6740

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at 98c6740

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 2.54 | 0.25 | 1.99 | 4.13 | 3.89 | 4.46 | 7.08 | 2.13 | 0.13 | 2.28 | 7.11 | 0.67 |
| dev (21) | 5.97 | 1.90 | 4.24 | 5.73 | 6.29 | 7.94 | 7.53 | 4.71 | 0.17 | 5.15 | 9.93 | 2.56 |
| train / bass A0-B2 (30) | 2.33 | 0.24 | 1.65 | 3.14 | 2.11 | 2.34 | 7.97 | 1.17 | 0.08 | 2.05 | 13.71 | 0.22 |
| train / middle C3-B5 (69) | 2.30 | 0.19 | 2.05 | 4.00 | 3.23 | 4.05 | 7.02 | 1.94 | 0.10 | 1.95 | 5.92 | 0.29 |
| train / treble C6-C8 (38) | 3.13 | 0.36 | 2.16 | 5.14 | 6.49 | 6.93 | 6.56 | 3.28 | 0.22 | 3.04 | 4.04 | 1.74 |
| dev / bass A0-B2 (5) | 5.51 | 1.21 | 1.94 | 3.69 | 4.82 | 7.16 | 9.44 | 4.99 | 0.19 | 2.49 | 1.00 | 1.35 |
| dev / middle C3-B5 (11) | 5.75 | 1.11 | 3.47 | 5.99 | 5.74 | 7.28 | 6.66 | 4.60 | 0.15 | 5.75 | 12.84 | 2.83 |
| dev / treble C6-C8 (5) | 6.93 | 4.33 | 8.21 | 7.21 | 8.96 | 10.16 | 7.92 | 4.67 | 0.22 | 6.50 | 12.47 | 3.19 |

## candidate 0.4.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 2.54 | 0.26 | 1.98 | 4.12 | 3.83 | 4.43 | 7.08 | 2.13 | 0.13 | 2.28 | 7.12 | 0.68 |
| dev (21) | 5.97 | 1.90 | 4.24 | 5.73 | 6.29 | 7.94 | 7.53 | 4.71 | 0.17 | 5.15 | 9.98 | 2.56 |
| train / bass A0-B2 (30) | 2.33 | 0.24 | 1.65 | 3.14 | 2.11 | 2.34 | 7.97 | 1.17 | 0.08 | 2.05 | 13.71 | 0.22 |
| train / middle C3-B5 (69) | 2.30 | 0.19 | 2.05 | 4.00 | 3.23 | 4.05 | 7.02 | 1.94 | 0.10 | 1.95 | 5.92 | 0.29 |
| train / treble C6-C8 (38) | 3.13 | 0.39 | 2.14 | 5.11 | 6.28 | 6.81 | 6.54 | 3.28 | 0.22 | 3.06 | 4.08 | 1.75 |
| dev / bass A0-B2 (5) | 5.51 | 1.21 | 1.94 | 3.69 | 4.82 | 7.16 | 9.44 | 4.99 | 0.19 | 2.49 | 1.00 | 1.35 |
| dev / middle C3-B5 (11) | 5.75 | 1.11 | 3.47 | 5.99 | 5.74 | 7.28 | 6.66 | 4.60 | 0.15 | 5.75 | 12.84 | 2.83 |
| dev / treble C6-C8 (5) | 6.93 | 4.33 | 8.21 | 7.19 | 8.95 | 10.17 | 7.91 | 4.67 | 0.22 | 6.50 | 12.67 | 3.19 |

## Regressions

Every note and role where candidate 0.4.1 is worse than 0.4.1 at 98c6740 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.1 at 98c6740 | candidate 0.4.1 |
|---|---|---|---|---|
| 103 | train | noise_db | 5.85 | 6.62 |
