# Recording benchmark: candidate 0.4.1 against 0.4.1 at bd11277

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at bd11277

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 2.41 | 0.26 | 1.97 | 3.69 | 3.50 | 4.43 | 6.86 | 2.12 | 0.13 | 2.25 | 7.11 | 0.61 |
| dev (21) | 5.95 | 1.89 | 4.24 | 5.51 | 6.06 | 7.99 | 7.19 | 4.72 | 0.17 | 5.14 | 9.58 | 2.55 |
| train / bass A0-B2 (30) | 2.33 | 0.24 | 1.65 | 2.90 | 2.09 | 2.34 | 8.03 | 1.16 | 0.08 | 2.05 | 15.51 | 0.22 |
| train / middle C3-B5 (69) | 2.26 | 0.19 | 2.05 | 3.56 | 2.95 | 4.02 | 6.95 | 1.93 | 0.09 | 1.91 | 5.08 | 0.26 |
| train / treble C6-C8 (38) | 2.74 | 0.39 | 2.10 | 4.55 | 5.62 | 6.88 | 5.83 | 3.27 | 0.23 | 3.01 | 4.15 | 1.56 |
| dev / bass A0-B2 (5) | 5.50 | 1.19 | 1.94 | 3.67 | 4.81 | 7.16 | 9.52 | 4.99 | 0.19 | 2.49 | 0.96 | 1.34 |
| dev / middle C3-B5 (11) | 5.75 | 1.11 | 3.47 | 5.67 | 5.63 | 7.30 | 6.30 | 4.63 | 0.14 | 5.75 | 12.09 | 2.83 |
| dev / treble C6-C8 (5) | 6.85 | 4.33 | 8.20 | 6.99 | 8.26 | 10.31 | 7.28 | 4.63 | 0.21 | 6.45 | 12.69 | 3.13 |

## candidate 0.4.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 2.41 | 0.26 | 1.97 | 3.71 | 3.50 | 4.43 | 6.93 | 2.11 | 0.13 | 2.25 | 7.11 | 0.61 |
| dev (21) | 5.95 | 1.89 | 4.23 | 5.51 | 6.05 | 7.99 | 7.26 | 4.72 | 0.17 | 5.14 | 9.59 | 2.55 |
| train / bass A0-B2 (30) | 2.33 | 0.24 | 1.65 | 2.95 | 2.12 | 2.34 | 8.25 | 1.16 | 0.08 | 2.05 | 15.51 | 0.22 |
| train / middle C3-B5 (69) | 2.26 | 0.19 | 2.05 | 3.57 | 2.95 | 4.02 | 7.03 | 1.93 | 0.09 | 1.91 | 5.08 | 0.26 |
| train / treble C6-C8 (38) | 2.73 | 0.39 | 2.10 | 4.55 | 5.60 | 6.88 | 5.79 | 3.27 | 0.23 | 3.01 | 4.18 | 1.56 |
| dev / bass A0-B2 (5) | 5.50 | 1.19 | 1.94 | 3.71 | 4.82 | 7.16 | 9.95 | 5.00 | 0.19 | 2.49 | 0.96 | 1.34 |
| dev / middle C3-B5 (11) | 5.74 | 1.11 | 3.47 | 5.66 | 5.63 | 7.30 | 6.30 | 4.63 | 0.14 | 5.75 | 12.09 | 2.83 |
| dev / treble C6-C8 (5) | 6.85 | 4.33 | 8.20 | 6.99 | 8.20 | 10.32 | 7.24 | 4.63 | 0.21 | 6.45 | 12.71 | 3.13 |

## Regressions

Every note and role where candidate 0.4.1 is worse than 0.4.1 at bd11277 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.1 at bd11277 | candidate 0.4.1 |
|---|---|---|---|---|
| 54 | train | noise_db | 9.87 | 10.54 |
