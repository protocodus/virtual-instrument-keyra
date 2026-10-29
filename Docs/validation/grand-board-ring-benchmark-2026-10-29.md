# Recording benchmark: candidate 0.4.1 against 0.4.1 at f043882

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at f043882

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 1.65 | 0.26 | 1.71 | 3.67 | 3.07 | 3.67 | 6.84 | 0.90 | 0.06 | 1.88 | 3.76 | 0.58 |
| dev (156) | 3.14 | 1.10 | 2.26 | 4.14 | 3.70 | 4.59 | 6.30 | 2.56 | 0.12 | 2.52 | 4.57 | 1.12 |
| train / bass A0-B2 (84) | 0.50 | 0.04 | 0.39 | 3.21 | 1.64 | 1.31 | 8.27 | 0.35 | 0.02 | 1.95 | 4.57 | 0.15 |
| train / middle C3-B5 (108) | 1.31 | 0.07 | 1.31 | 2.87 | 2.38 | 2.06 | 6.49 | 0.70 | 0.04 | 0.68 | 4.35 | 0.19 |
| train / treble C6-C8 (84) | 3.25 | 0.72 | 3.66 | 5.17 | 5.39 | 8.10 | 5.88 | 1.77 | 0.13 | 3.36 | 2.18 | 1.53 |
| dev / bass A0-B2 (44) | 2.24 | 1.10 | 0.89 | 3.95 | 2.63 | 2.07 | 7.40 | 1.38 | 0.07 | 2.57 | 3.35 | 1.03 |
| dev / middle C3-B5 (68) | 3.38 | 0.61 | 2.43 | 3.62 | 3.43 | 4.52 | 6.01 | 3.92 | 0.12 | 1.82 | 6.23 | 0.94 |
| dev / treble C6-C8 (44) | 3.67 | 1.86 | 3.40 | 5.13 | 5.20 | 7.20 | 5.63 | 1.60 | 0.19 | 3.56 | 3.23 | 1.48 |

## candidate 0.4.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 1.65 | 0.26 | 1.71 | 3.65 | 2.74 | 3.55 | 6.66 | 0.89 | 0.06 | 1.88 | 3.74 | 0.58 |
| dev (156) | 3.14 | 1.06 | 2.26 | 4.12 | 3.45 | 4.51 | 6.16 | 2.56 | 0.12 | 2.51 | 4.59 | 1.11 |
| train / bass A0-B2 (84) | 0.50 | 0.04 | 0.39 | 3.21 | 1.64 | 1.31 | 8.27 | 0.35 | 0.02 | 1.95 | 4.57 | 0.14 |
| train / middle C3-B5 (108) | 1.31 | 0.07 | 1.31 | 2.87 | 2.38 | 2.06 | 6.49 | 0.70 | 0.04 | 0.68 | 4.35 | 0.19 |
| train / treble C6-C8 (84) | 3.25 | 0.71 | 3.66 | 5.10 | 4.32 | 7.71 | 5.32 | 1.75 | 0.13 | 3.34 | 2.12 | 1.51 |
| dev / bass A0-B2 (44) | 2.24 | 1.10 | 0.89 | 3.95 | 2.63 | 2.07 | 7.40 | 1.38 | 0.07 | 2.57 | 3.35 | 1.03 |
| dev / middle C3-B5 (68) | 3.38 | 0.61 | 2.43 | 3.62 | 3.43 | 4.52 | 6.01 | 3.92 | 0.12 | 1.82 | 6.23 | 0.94 |
| dev / treble C6-C8 (44) | 3.68 | 1.73 | 3.40 | 5.06 | 4.29 | 6.93 | 5.13 | 1.60 | 0.18 | 3.53 | 3.30 | 1.45 |

## Regressions

Every note and role where candidate 0.4.1 is worse than 0.4.1 at f043882 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.
