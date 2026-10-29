# Recording benchmark: candidate 0.4.1 against 0.4.1 at 8836965

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at 8836965

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 1.66 | 0.26 | 1.71 | 3.71 | 2.70 | 3.24 | 6.56 | 0.89 | 0.06 | 1.85 | 3.70 | 0.57 |
| dev (156) | 3.14 | 1.05 | 2.26 | 4.14 | 3.39 | 4.24 | 6.11 | 2.56 | 0.12 | 2.46 | 4.45 | 1.11 |
| train / bass A0-B2 (84) | 0.50 | 0.04 | 0.39 | 3.24 | 1.63 | 1.31 | 7.98 | 0.35 | 0.02 | 1.95 | 4.67 | 0.15 |
| train / middle C3-B5 (108) | 1.31 | 0.07 | 1.31 | 2.92 | 2.33 | 2.00 | 6.42 | 0.70 | 0.04 | 0.68 | 4.17 | 0.19 |
| train / treble C6-C8 (84) | 3.26 | 0.71 | 3.65 | 5.21 | 4.26 | 6.76 | 5.39 | 1.74 | 0.12 | 3.25 | 2.14 | 1.50 |
| dev / bass A0-B2 (44) | 2.25 | 1.06 | 0.89 | 3.96 | 2.62 | 2.07 | 7.25 | 1.38 | 0.07 | 2.57 | 3.36 | 1.02 |
| dev / middle C3-B5 (68) | 3.38 | 0.61 | 2.43 | 3.59 | 3.35 | 4.45 | 5.96 | 3.92 | 0.12 | 1.82 | 5.94 | 0.94 |
| dev / treble C6-C8 (44) | 3.67 | 1.73 | 3.40 | 5.17 | 4.21 | 6.09 | 5.20 | 1.60 | 0.18 | 3.35 | 3.24 | 1.45 |

## candidate 0.4.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 1.66 | 0.26 | 1.71 | 3.72 | 2.70 | 3.24 | 5.34 | 0.89 | 0.06 | 1.85 | 3.69 | 0.57 |
| dev (156) | 3.14 | 1.05 | 2.26 | 4.15 | 3.39 | 4.24 | 5.34 | 2.56 | 0.12 | 2.46 | 4.37 | 1.11 |
| train / bass A0-B2 (84) | 0.50 | 0.04 | 0.39 | 3.25 | 1.64 | 1.31 | 4.43 | 0.35 | 0.02 | 1.95 | 4.71 | 0.15 |
| train / middle C3-B5 (108) | 1.31 | 0.07 | 1.31 | 2.92 | 2.33 | 2.00 | 5.93 | 0.70 | 0.04 | 0.68 | 4.12 | 0.19 |
| train / treble C6-C8 (84) | 3.26 | 0.71 | 3.65 | 5.21 | 4.26 | 6.76 | 5.38 | 1.74 | 0.12 | 3.25 | 2.14 | 1.50 |
| dev / bass A0-B2 (44) | 2.25 | 1.06 | 0.89 | 3.96 | 2.62 | 2.07 | 4.91 | 1.38 | 0.07 | 2.58 | 3.06 | 1.02 |
| dev / middle C3-B5 (68) | 3.38 | 0.61 | 2.43 | 3.60 | 3.35 | 4.45 | 5.71 | 3.92 | 0.12 | 1.82 | 5.94 | 0.94 |
| dev / treble C6-C8 (44) | 3.67 | 1.73 | 3.40 | 5.17 | 4.21 | 6.08 | 5.20 | 1.60 | 0.18 | 3.35 | 3.26 | 1.45 |

## Regressions

Every note and role where candidate 0.4.1 is worse than 0.4.1 at 8836965 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.
