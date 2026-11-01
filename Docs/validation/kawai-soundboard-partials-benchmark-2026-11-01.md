# Recording benchmark: candidate 0.4.1 against 0.4.1 at d5e467d

Every train and dev note of `Tools/corpus/split-vcsl-kawai-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at d5e467d

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (104) | 9.60 | 2.19 | 3.94 | 8.44 | 9.57 | 9.28 | 8.85 | 2.60 | 0.11 | 3.77 | 7.98 | 1.85 |
| dev (23) | 12.74 | 4.86 | 5.07 | 8.74 | 9.75 | 9.95 | 9.96 | 5.82 | 0.18 | 5.12 | 7.14 | 5.86 |
| train / bass A0-B2 (27) | 10.88 | 1.07 | 2.19 | 9.63 | 10.08 | 9.07 | 11.91 | 1.79 | 0.08 | 3.30 | 15.91 | 2.00 |
| train / middle C3-B5 (52) | 9.58 | 1.11 | 3.83 | 7.81 | 8.63 | 8.72 | 8.17 | 2.26 | 0.13 | 3.80 | 6.47 | 1.00 |
| train / treble C6-C8 (25) | 8.08 | 6.08 | 7.45 | 8.48 | 10.97 | 11.27 | 7.44 | 5.56 | 0.14 | 4.22 | 2.54 | 3.47 |
| dev / bass A0-B2 (8) | 12.34 | 3.91 | 3.01 | 10.03 | 9.64 | 10.20 | 13.67 | 4.11 | 0.12 | 4.11 | 7.56 | 4.33 |
| dev / middle C3-B5 (12) | 13.49 | 5.76 | 5.72 | 8.10 | 9.82 | 10.26 | 7.93 | 8.10 | 0.16 | 6.11 | 8.01 | 6.14 |
| dev / treble C6-C8 (3) | 9.88 | 3.32 | 9.37 | 7.88 | 9.73 | 7.11 | 7.47 | 0.08 | 0.56 | 3.82 | 2.55 | 8.86 |

## candidate 0.4.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (104) | 9.57 | 2.20 | 3.93 | 8.35 | 9.52 | 9.28 | 8.88 | 2.71 | 0.11 | 3.77 | 8.59 | 1.87 |
| dev (23) | 12.69 | 4.94 | 5.07 | 8.69 | 9.67 | 9.96 | 9.95 | 5.86 | 0.19 | 5.11 | 7.36 | 5.86 |
| train / bass A0-B2 (27) | 10.63 | 1.10 | 2.17 | 9.37 | 9.89 | 9.05 | 12.22 | 2.05 | 0.08 | 3.31 | 18.03 | 2.00 |
| train / middle C3-B5 (52) | 9.65 | 1.11 | 3.83 | 7.75 | 8.61 | 8.73 | 8.06 | 2.31 | 0.12 | 3.79 | 6.59 | 1.02 |
| train / treble C6-C8 (25) | 8.08 | 6.08 | 7.45 | 8.48 | 11.01 | 11.27 | 7.48 | 5.59 | 0.14 | 4.22 | 2.55 | 3.48 |
| dev / bass A0-B2 (8) | 12.21 | 4.08 | 3.01 | 9.87 | 9.45 | 10.20 | 13.67 | 4.19 | 0.12 | 4.11 | 7.57 | 4.33 |
| dev / middle C3-B5 (12) | 13.48 | 5.78 | 5.72 | 8.10 | 9.78 | 10.28 | 7.91 | 8.12 | 0.16 | 6.11 | 8.42 | 6.13 |
| dev / treble C6-C8 (3) | 9.88 | 3.32 | 9.37 | 7.89 | 9.82 | 7.11 | 7.51 | 0.08 | 0.56 | 3.81 | 2.56 | 8.85 |

## Regressions

Every note and role where candidate 0.4.1 is worse than 0.4.1 at d5e467d by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.1 at d5e467d | candidate 0.4.1 |
|---|---|---|---|---|
| 30 | train | rise_ms | 25.67 | 34.85 |
| 33 | train | noise_db | 11.35 | 13.34 |
| 60 | train | rise_ms | 4.70 | 8.56 |
| 36 | train | rise_ms | 3.83 | 7.42 |
| 42 | train | rise_ms | 28.90 | 30.98 |
| 58 | dev | rise_ms | 3.03 | 4.55 |
| 54 | train | noise_db | 8.09 | 8.76 |
| 82 | dev | icc | 0.28 | 0.31 |
