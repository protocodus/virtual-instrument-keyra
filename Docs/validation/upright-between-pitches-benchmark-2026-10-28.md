# Recording benchmark: candidate 0.4.1 against 0.4.1 at 2e3854b

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at 2e3854b

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

## candidate 0.4.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 2.54 | 0.25 | 1.99 | 4.13 | 3.89 | 4.46 | 8.93 | 2.13 | 0.13 | 2.28 | 7.11 | 0.67 |
| dev (21) | 5.97 | 1.90 | 4.24 | 5.73 | 6.29 | 7.94 | 9.73 | 4.71 | 0.17 | 5.15 | 9.93 | 2.56 |
| train / bass A0-B2 (30) | 2.33 | 0.24 | 1.65 | 3.14 | 2.11 | 2.34 | 12.61 | 1.17 | 0.08 | 2.05 | 13.71 | 0.22 |
| train / middle C3-B5 (69) | 2.30 | 0.19 | 2.05 | 4.00 | 3.23 | 4.05 | 9.07 | 1.94 | 0.10 | 1.95 | 5.92 | 0.29 |
| train / treble C6-C8 (38) | 3.13 | 0.36 | 2.16 | 5.14 | 6.49 | 6.93 | 5.78 | 3.28 | 0.22 | 3.04 | 4.04 | 1.74 |
| dev / bass A0-B2 (5) | 5.51 | 1.21 | 1.94 | 3.69 | 4.82 | 7.16 | 14.85 | 4.99 | 0.19 | 2.49 | 1.00 | 1.35 |
| dev / middle C3-B5 (11) | 5.75 | 1.11 | 3.47 | 5.99 | 5.74 | 7.28 | 8.39 | 4.60 | 0.15 | 5.75 | 12.84 | 2.83 |
| dev / treble C6-C8 (5) | 6.93 | 4.33 | 8.21 | 7.21 | 8.96 | 10.16 | 7.56 | 4.67 | 0.22 | 6.50 | 12.47 | 3.19 |

## Regressions

Every note and role where candidate 0.4.1 is worse than 0.4.1 at 2e3854b by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.1 at 2e3854b | candidate 0.4.1 |
|---|---|---|---|---|
| 59 | dev | attack_db | 6.16 | 7.56 |
| 56 | dev | level_db | 1.97 | 2.89 |
| 59 | dev | noise_db | 6.34 | 7.23 |
| 72 | dev | partial_db | 4.08 | 4.90 |
| 59 | dev | level_db | 0.92 | 1.67 |
| 59 | dev | partial_db | 9.26 | 9.82 |
| 59 | dev | sustain_db | 5.58 | 6.11 |
| 56 | dev | envelope_db | 3.63 | 4.14 |
| 72 | dev | sustain_db | 7.09 | 7.60 |
