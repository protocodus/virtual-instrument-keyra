# Recording benchmark: candidate 0.4.1 against 0.4.1 at bd11277

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at bd11277

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 1.65 | 0.26 | 1.68 | 3.68 | 3.06 | 3.65 | 6.85 | 0.90 | 0.06 | 1.88 | 3.75 | 0.58 |
| dev (156) | 3.13 | 1.10 | 2.25 | 4.14 | 3.71 | 4.57 | 6.31 | 2.56 | 0.12 | 2.52 | 4.58 | 1.12 |
| train / bass A0-B2 (84) | 0.50 | 0.04 | 0.39 | 3.21 | 1.64 | 1.31 | 8.26 | 0.35 | 0.02 | 1.95 | 4.56 | 0.15 |
| train / middle C3-B5 (108) | 1.31 | 0.07 | 1.30 | 2.87 | 2.38 | 2.06 | 6.49 | 0.70 | 0.04 | 0.68 | 4.35 | 0.19 |
| train / treble C6-C8 (84) | 3.23 | 0.72 | 3.58 | 5.18 | 5.37 | 8.03 | 5.92 | 1.77 | 0.13 | 3.37 | 2.17 | 1.53 |
| dev / bass A0-B2 (44) | 2.23 | 1.10 | 0.89 | 3.95 | 2.63 | 2.07 | 7.37 | 1.38 | 0.07 | 2.57 | 3.35 | 1.03 |
| dev / middle C3-B5 (68) | 3.38 | 0.61 | 2.43 | 3.62 | 3.43 | 4.52 | 6.02 | 3.92 | 0.12 | 1.82 | 6.23 | 0.94 |
| dev / treble C6-C8 (44) | 3.65 | 1.86 | 3.34 | 5.13 | 5.24 | 7.15 | 5.69 | 1.61 | 0.19 | 3.56 | 3.25 | 1.48 |

## candidate 0.4.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 1.65 | 0.26 | 1.68 | 3.67 | 3.05 | 3.65 | 6.81 | 0.90 | 0.06 | 1.88 | 3.76 | 0.58 |
| dev (156) | 3.13 | 1.10 | 2.25 | 4.14 | 3.70 | 4.57 | 6.30 | 2.56 | 0.12 | 2.52 | 4.57 | 1.12 |
| train / bass A0-B2 (84) | 0.50 | 0.04 | 0.39 | 3.21 | 1.64 | 1.31 | 8.22 | 0.35 | 0.02 | 1.95 | 4.56 | 0.15 |
| train / middle C3-B5 (108) | 1.31 | 0.07 | 1.30 | 2.87 | 2.38 | 2.06 | 6.49 | 0.70 | 0.04 | 0.68 | 4.35 | 0.19 |
| train / treble C6-C8 (84) | 3.23 | 0.72 | 3.58 | 5.16 | 5.31 | 8.03 | 5.86 | 1.77 | 0.13 | 3.37 | 2.18 | 1.53 |
| dev / bass A0-B2 (44) | 2.23 | 1.10 | 0.89 | 3.96 | 2.63 | 2.07 | 7.39 | 1.38 | 0.07 | 2.57 | 3.35 | 1.03 |
| dev / middle C3-B5 (68) | 3.38 | 0.61 | 2.43 | 3.62 | 3.43 | 4.52 | 6.01 | 3.92 | 0.12 | 1.82 | 6.23 | 0.94 |
| dev / treble C6-C8 (44) | 3.65 | 1.86 | 3.34 | 5.12 | 5.19 | 7.14 | 5.64 | 1.61 | 0.19 | 3.56 | 3.22 | 1.48 |

## Regressions

Every note and role where candidate 0.4.1 is worse than 0.4.1 at bd11277 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.
