# Recording benchmark: candidate 0.4.1 against shipping 0.4.0

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## shipping 0.4.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 3.16 | 0.36 | 2.93 | 4.17 | 4.04 | 5.65 | 8.99 | 2.30 | 0.12 | 3.01 | 6.53 | 0.80 |
| dev (21) | 6.52 | 2.14 | 5.52 | 5.64 | 6.48 | 9.04 | 9.73 | 4.32 | 0.20 | 6.29 | 10.30 | 2.30 |
| train / bass A0-B2 (30) | 2.38 | 0.24 | 1.61 | 3.14 | 2.16 | 2.40 | 12.66 | 1.18 | 0.08 | 2.05 | 12.22 | 0.23 |
| train / middle C3-B5 (69) | 2.55 | 0.22 | 2.39 | 4.02 | 3.28 | 4.44 | 9.08 | 1.99 | 0.10 | 2.30 | 5.94 | 0.29 |
| train / treble C6-C8 (38) | 4.88 | 0.73 | 5.06 | 5.27 | 6.92 | 10.55 | 5.92 | 3.84 | 0.21 | 5.06 | 3.10 | 2.18 |
| dev / bass A0-B2 (5) | 6.07 | 1.41 | 2.04 | 3.94 | 5.02 | 7.25 | 14.68 | 5.12 | 0.19 | 2.42 | 1.13 | 1.50 |
| dev / middle C3-B5 (11) | 5.66 | 1.32 | 3.29 | 5.71 | 5.67 | 7.10 | 8.44 | 4.57 | 0.15 | 5.61 | 13.51 | 2.31 |
| dev / treble C6-C8 (5) | 8.86 | 4.67 | 13.90 | 7.20 | 9.74 | 15.11 | 7.61 | 2.98 | 0.32 | 11.67 | 12.43 | 3.07 |

## candidate 0.4.1

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

## Regressions

Every note and role where candidate 0.4.1 is worse than shipping 0.4.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | shipping 0.4.0 | candidate 0.4.1 |
|---|---|---|---|---|
| 96 | train | rise_ms | 0.44 | 1.82 |
