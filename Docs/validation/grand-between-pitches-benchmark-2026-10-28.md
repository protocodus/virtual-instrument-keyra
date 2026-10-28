# Recording benchmark: candidate 0.4.1 against 0.4.1 at 2e3854b

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at 2e3854b

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 1.69 | 0.26 | 1.68 | 3.78 | 3.07 | 3.68 | 5.56 | 0.91 | 0.06 | 1.89 | 3.82 | 0.54 |
| dev (156) | 3.20 | 1.11 | 2.24 | 4.22 | 3.79 | 4.65 | 5.65 | 2.55 | 0.12 | 2.55 | 4.90 | 1.29 |
| train / bass A0-B2 (84) | 0.51 | 0.04 | 0.39 | 3.37 | 1.65 | 1.31 | 5.50 | 0.36 | 0.03 | 1.95 | 4.48 | 0.15 |
| train / middle C3-B5 (108) | 1.31 | 0.07 | 1.30 | 2.97 | 2.39 | 2.06 | 5.59 | 0.70 | 0.04 | 0.69 | 4.31 | 0.19 |
| train / treble C6-C8 (84) | 3.36 | 0.72 | 3.56 | 5.23 | 5.36 | 8.13 | 5.57 | 1.78 | 0.13 | 3.39 | 2.54 | 1.38 |
| dev / bass A0-B2 (44) | 2.33 | 1.14 | 0.89 | 3.95 | 2.76 | 2.23 | 5.83 | 1.31 | 0.07 | 2.69 | 4.74 | 1.17 |
| dev / middle C3-B5 (68) | 3.54 | 0.61 | 2.44 | 3.73 | 3.55 | 4.61 | 5.79 | 3.92 | 0.12 | 1.82 | 5.92 | 1.13 |
| dev / treble C6-C8 (44) | 3.55 | 1.86 | 3.29 | 5.24 | 5.19 | 7.15 | 5.26 | 1.62 | 0.19 | 3.54 | 3.51 | 1.63 |

## candidate 0.4.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 1.69 | 0.26 | 1.68 | 3.78 | 3.07 | 3.68 | 5.56 | 0.91 | 0.06 | 1.89 | 3.82 | 0.54 |
| dev (156) | 3.13 | 1.10 | 2.25 | 4.17 | 3.68 | 4.58 | 5.62 | 2.56 | 0.12 | 2.52 | 4.54 | 1.10 |
| train / bass A0-B2 (84) | 0.51 | 0.04 | 0.39 | 3.37 | 1.65 | 1.31 | 5.50 | 0.36 | 0.03 | 1.95 | 4.48 | 0.15 |
| train / middle C3-B5 (108) | 1.31 | 0.07 | 1.30 | 2.97 | 2.39 | 2.06 | 5.59 | 0.70 | 0.04 | 0.69 | 4.31 | 0.19 |
| train / treble C6-C8 (84) | 3.36 | 0.72 | 3.56 | 5.23 | 5.36 | 8.13 | 5.57 | 1.78 | 0.13 | 3.39 | 2.54 | 1.38 |
| dev / bass A0-B2 (44) | 2.23 | 1.10 | 0.89 | 3.98 | 2.62 | 2.07 | 5.86 | 1.38 | 0.07 | 2.58 | 3.12 | 1.03 |
| dev / middle C3-B5 (68) | 3.38 | 0.61 | 2.43 | 3.64 | 3.40 | 4.52 | 5.72 | 3.92 | 0.12 | 1.82 | 6.09 | 0.95 |
| dev / treble C6-C8 (44) | 3.66 | 1.86 | 3.34 | 5.18 | 5.18 | 7.17 | 5.24 | 1.61 | 0.19 | 3.54 | 3.56 | 1.43 |

## Regressions

Every note and role where candidate 0.4.1 is worse than 0.4.1 at 2e3854b by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.
