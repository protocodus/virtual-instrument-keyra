# Recording benchmark: candidate 0.4.1 against 0.4.1 at d5e467d

Every train and dev note of `Tools/corpus/split-newyork-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at d5e467d

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (61) | 7.81 | 0.46 | 4.06 | 7.07 | 6.93 | 7.52 | 7.77 | 1.69 | 0.09 | 2.34 | 11.99 | 0.62 |
| dev (17) | 9.94 | 2.37 | 7.75 | 8.72 | 7.88 | 9.13 | 8.91 | 6.25 | 0.19 | 3.60 | 8.51 | 4.91 |
| train / bass A0-B2 (20) | 9.24 | 0.23 | 1.77 | 9.49 | 9.25 | 8.22 | 12.82 | 1.33 | 0.08 | 2.16 | 13.86 | 1.04 |
| train / middle C3-B5 (24) | 8.08 | 0.24 | 4.24 | 6.42 | 6.45 | 7.17 | 5.64 | 1.49 | 0.11 | 2.59 | 16.35 | 0.18 |
| train / treble C6-C8 (17) | 5.62 | 1.09 | 8.21 | 5.14 | 4.75 | 7.12 | 4.83 | 2.90 | 0.07 | 2.20 | 3.66 | 0.74 |
| dev / bass A0-B2 (5) | 10.68 | 3.74 | 3.68 | 9.38 | 8.19 | 8.32 | 12.09 | 3.79 | 0.11 | 2.37 | 7.46 | 3.14 |
| dev / middle C3-B5 (5) | 9.41 | 1.04 | 6.98 | 7.75 | 7.66 | 9.68 | 7.47 | 6.21 | 0.15 | 3.70 | 10.10 | 3.47 |
| dev / treble C6-C8 (7) | 9.79 | 2.34 | 11.21 | 8.94 | 7.80 | 9.32 | 7.66 | 8.04 | 0.27 | 4.42 | 8.13 | 7.21 |

## candidate 0.4.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (61) | 7.78 | 0.47 | 4.09 | 6.99 | 7.36 | 7.51 | 7.77 | 1.73 | 0.09 | 2.34 | 11.96 | 0.59 |
| dev (17) | 9.98 | 2.37 | 7.77 | 8.60 | 7.90 | 9.21 | 8.77 | 6.21 | 0.20 | 3.94 | 8.63 | 5.15 |
| train / bass A0-B2 (20) | 9.11 | 0.25 | 1.78 | 9.32 | 9.26 | 8.22 | 12.80 | 1.38 | 0.08 | 2.15 | 14.38 | 1.03 |
| train / middle C3-B5 (24) | 8.12 | 0.24 | 4.30 | 6.39 | 6.53 | 7.15 | 5.65 | 1.52 | 0.11 | 2.59 | 15.89 | 0.13 |
| train / treble C6-C8 (17) | 5.62 | 1.09 | 8.21 | 5.11 | 6.30 | 7.13 | 4.86 | 2.92 | 0.07 | 2.20 | 3.57 | 0.73 |
| dev / bass A0-B2 (5) | 10.82 | 3.73 | 3.84 | 8.89 | 8.10 | 8.53 | 11.73 | 3.82 | 0.11 | 3.49 | 8.36 | 3.94 |
| dev / middle C3-B5 (5) | 9.42 | 1.05 | 6.87 | 7.93 | 7.65 | 9.73 | 7.35 | 6.03 | 0.18 | 3.70 | 9.53 | 3.48 |
| dev / treble C6-C8 (7) | 9.79 | 2.34 | 11.21 | 8.88 | 7.93 | 9.34 | 7.68 | 8.04 | 0.27 | 4.43 | 8.17 | 7.21 |

## Regressions

Every note and role where candidate 0.4.1 is worse than 0.4.1 at d5e467d by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.1 at d5e467d | candidate 0.4.1 |
|---|---|---|---|---|
| 104 | train | early_db | 5.21 | 11.42 |
| 34 | train | rise_ms | 3.71 | 6.38 |
| 39 | dev | envelope_db | 2.37 | 3.49 |
| 44 | train | rise_ms | 8.68 | 10.73 |
| 69 | train | rise_ms | 4.64 | 6.41 |
| 64 | dev | icc | 0.15 | 0.18 |
| 39 | dev | level_db | 3.14 | 3.94 |
| 24 | train | rise_ms | 12.69 | 13.72 |
