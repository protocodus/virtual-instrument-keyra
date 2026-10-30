# Recording benchmark: body after the knock against 0.4.1 at 027ac85

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at 027ac85

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 5.98 | 0.26 | 2.38 | 5.02 | 5.05 | 5.50 | 6.42 | 2.09 | 0.13 | 2.53 | 8.48 | 0.88 |
| dev (21) | 8.81 | 1.92 | 4.35 | 6.56 | 7.31 | 8.78 | 7.01 | 4.53 | 0.18 | 5.07 | 6.44 | 2.46 |
| train / bass A0-B2 (30) | 7.06 | 0.24 | 1.84 | 5.50 | 5.07 | 5.37 | 8.36 | 1.26 | 0.09 | 2.47 | 12.92 | 0.96 |
| train / middle C3-B5 (69) | 6.76 | 0.19 | 2.62 | 5.11 | 4.79 | 5.46 | 6.16 | 1.90 | 0.10 | 2.16 | 8.80 | 0.44 |
| train / treble C6-C8 (38) | 3.72 | 0.39 | 2.39 | 4.48 | 5.50 | 5.69 | 5.54 | 3.16 | 0.24 | 3.26 | 4.41 | 1.61 |
| dev / bass A0-B2 (5) | 9.37 | 1.33 | 2.02 | 6.21 | 7.38 | 9.31 | 8.50 | 5.00 | 0.20 | 2.48 | 1.51 | 1.10 |
| dev / middle C3-B5 (11) | 8.76 | 1.12 | 3.63 | 6.75 | 7.00 | 8.29 | 6.52 | 4.32 | 0.17 | 5.58 | 10.80 | 2.77 |
| dev / treble C6-C8 (5) | 8.37 | 4.24 | 8.25 | 6.49 | 7.93 | 9.31 | 6.89 | 4.53 | 0.20 | 6.55 | 1.79 | 3.14 |

## body after the knock

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 5.98 | 0.26 | 2.38 | 5.01 | 4.94 | 5.51 | 6.31 | 2.10 | 0.13 | 2.54 | 8.46 | 0.87 |
| dev (21) | 8.81 | 1.92 | 4.35 | 6.55 | 7.29 | 8.78 | 6.98 | 4.53 | 0.18 | 5.07 | 6.42 | 2.46 |
| train / bass A0-B2 (30) | 7.06 | 0.24 | 1.84 | 5.50 | 5.07 | 5.37 | 8.39 | 1.26 | 0.09 | 2.47 | 12.92 | 0.96 |
| train / middle C3-B5 (69) | 6.76 | 0.19 | 2.62 | 5.10 | 4.76 | 5.46 | 6.11 | 1.90 | 0.10 | 2.16 | 8.71 | 0.44 |
| train / treble C6-C8 (38) | 3.72 | 0.39 | 2.39 | 4.45 | 5.18 | 5.71 | 5.25 | 3.16 | 0.24 | 3.27 | 4.49 | 1.58 |
| dev / bass A0-B2 (5) | 9.37 | 1.33 | 2.02 | 6.22 | 7.38 | 9.31 | 8.52 | 5.00 | 0.20 | 2.48 | 1.51 | 1.10 |
| dev / middle C3-B5 (11) | 8.76 | 1.12 | 3.63 | 6.74 | 7.00 | 8.29 | 6.53 | 4.33 | 0.17 | 5.58 | 10.79 | 2.77 |
| dev / treble C6-C8 (5) | 8.37 | 4.24 | 8.25 | 6.46 | 7.82 | 9.31 | 6.74 | 4.53 | 0.20 | 6.55 | 1.71 | 3.14 |

## Regressions

Every note and role where body after the knock is worse than 0.4.1 at 027ac85 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.
