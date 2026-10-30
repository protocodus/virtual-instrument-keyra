# Recording benchmark: candidate 0.4.1 against 0.4.1 at 4b11922

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at 4b11922

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.63 | 0.25 | 1.78 | 4.74 | 4.25 | 4.63 | 5.82 | 0.92 | 0.06 | 1.98 | 3.94 | 0.66 |
| dev (156) | 5.44 | 1.07 | 2.32 | 4.99 | 4.62 | 5.27 | 5.50 | 2.57 | 0.12 | 2.58 | 4.66 | 1.14 |
| train / bass A0-B2 (84) | 4.66 | 0.04 | 0.44 | 4.76 | 3.96 | 3.76 | 5.46 | 0.43 | 0.03 | 2.13 | 5.74 | 0.43 |
| train / middle C3-B5 (108) | 4.98 | 0.07 | 1.46 | 4.25 | 4.19 | 3.51 | 6.28 | 0.71 | 0.05 | 0.83 | 3.96 | 0.29 |
| train / treble C6-C8 (84) | 4.16 | 0.69 | 3.66 | 5.35 | 4.62 | 6.95 | 5.55 | 1.75 | 0.12 | 3.31 | 2.13 | 1.35 |
| dev / bass A0-B2 (44) | 5.33 | 1.11 | 0.89 | 5.06 | 4.14 | 3.75 | 4.98 | 1.38 | 0.07 | 2.82 | 4.15 | 1.22 |
| dev / middle C3-B5 (68) | 6.52 | 0.61 | 2.58 | 4.78 | 4.94 | 5.68 | 5.85 | 3.92 | 0.12 | 1.92 | 5.90 | 0.94 |
| dev / treble C6-C8 (44) | 3.87 | 1.73 | 3.36 | 5.23 | 4.60 | 6.15 | 5.46 | 1.63 | 0.18 | 3.38 | 3.25 | 1.36 |

## candidate 0.4.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.63 | 0.25 | 1.78 | 4.50 | 4.25 | 4.62 | 5.70 | 0.92 | 0.06 | 1.96 | 3.88 | 0.65 |
| dev (156) | 5.44 | 1.06 | 2.31 | 4.83 | 4.62 | 5.27 | 5.41 | 2.57 | 0.12 | 2.58 | 4.31 | 1.14 |
| train / bass A0-B2 (84) | 4.65 | 0.04 | 0.44 | 4.76 | 3.95 | 3.74 | 5.45 | 0.43 | 0.03 | 2.12 | 5.74 | 0.43 |
| train / middle C3-B5 (108) | 4.97 | 0.07 | 1.46 | 4.11 | 4.19 | 3.50 | 6.15 | 0.71 | 0.04 | 0.83 | 3.49 | 0.29 |
| train / treble C6-C8 (84) | 4.16 | 0.69 | 3.66 | 4.73 | 4.63 | 6.95 | 5.33 | 1.75 | 0.12 | 3.27 | 2.51 | 1.34 |
| dev / bass A0-B2 (44) | 5.33 | 1.11 | 0.90 | 5.06 | 4.14 | 3.74 | 4.98 | 1.38 | 0.07 | 2.81 | 4.15 | 1.22 |
| dev / middle C3-B5 (68) | 6.52 | 0.61 | 2.58 | 4.63 | 4.94 | 5.67 | 5.74 | 3.92 | 0.12 | 1.91 | 5.57 | 0.95 |
| dev / treble C6-C8 (44) | 3.87 | 1.73 | 3.36 | 4.91 | 4.60 | 6.16 | 5.32 | 1.62 | 0.18 | 3.38 | 2.53 | 1.36 |

## Regressions

Every note and role where candidate 0.4.1 is worse than 0.4.1 at 4b11922 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.1 at 4b11922 | candidate 0.4.1 |
|---|---|---|---|---|
| 102 | dev | rise_ms | 1.07 | 2.38 |
| 105 | dev | rise_ms | 1.06 | 2.33 |
| 90 | dev | rise_ms | 3.85 | 5.08 |
| 102 | train | rise_ms | 1.51 | 2.68 |
| 105 | train | rise_ms | 1.86 | 2.91 |
| 90 | train | rise_ms | 4.26 | 5.27 |
