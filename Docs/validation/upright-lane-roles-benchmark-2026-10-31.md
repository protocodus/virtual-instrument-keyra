# Recording benchmark: lanes meet by role against shipping 0.4.1 (6691d3e)

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## shipping 0.4.1 (6691d3e)

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 5.98 | 0.26 | 2.38 | 5.01 | 4.94 | 5.51 | 6.31 | 2.10 | 0.13 | 2.54 | 8.46 | 0.87 |
| dev (21) | 8.78 | 1.87 | 4.47 | 6.44 | 7.32 | 8.80 | 6.98 | 4.26 | 0.21 | 4.95 | 6.02 | 2.46 |
| train / bass A0-B2 (30) | 7.06 | 0.24 | 1.84 | 5.50 | 5.07 | 5.37 | 8.39 | 1.26 | 0.09 | 2.47 | 12.92 | 0.96 |
| train / middle C3-B5 (69) | 6.76 | 0.19 | 2.62 | 5.10 | 4.76 | 5.46 | 6.11 | 1.90 | 0.10 | 2.16 | 8.71 | 0.43 |
| train / treble C6-C8 (38) | 3.72 | 0.39 | 2.39 | 4.45 | 5.18 | 5.71 | 5.25 | 3.16 | 0.24 | 3.27 | 4.49 | 1.58 |
| dev / bass A0-B2 (5) | 9.42 | 1.36 | 2.01 | 5.83 | 7.44 | 9.40 | 8.55 | 5.12 | 0.22 | 2.49 | 1.93 | 1.04 |
| dev / middle C3-B5 (11) | 8.65 | 1.13 | 3.68 | 6.76 | 6.94 | 8.16 | 6.54 | 4.16 | 0.18 | 5.11 | 9.86 | 2.80 |
| dev / treble C6-C8 (5) | 8.43 | 4.01 | 8.67 | 6.36 | 8.05 | 9.61 | 6.67 | 3.64 | 0.28 | 7.06 | 1.67 | 3.13 |

## lanes meet by role

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 5.98 | 0.26 | 2.38 | 5.01 | 4.94 | 5.51 | 6.31 | 2.10 | 0.13 | 2.54 | 8.46 | 0.87 |
| dev (21) | 8.78 | 1.87 | 4.63 | 6.47 | 7.27 | 8.77 | 6.98 | 4.31 | 0.21 | 4.88 | 6.00 | 2.46 |
| train / bass A0-B2 (30) | 7.06 | 0.24 | 1.84 | 5.50 | 5.07 | 5.37 | 8.39 | 1.26 | 0.09 | 2.47 | 12.92 | 0.96 |
| train / middle C3-B5 (69) | 6.76 | 0.19 | 2.62 | 5.10 | 4.76 | 5.46 | 6.11 | 1.90 | 0.10 | 2.16 | 8.71 | 0.44 |
| train / treble C6-C8 (38) | 3.72 | 0.39 | 2.39 | 4.45 | 5.18 | 5.71 | 5.25 | 3.16 | 0.24 | 3.27 | 4.49 | 1.58 |
| dev / bass A0-B2 (5) | 9.32 | 1.38 | 1.87 | 5.88 | 7.49 | 9.20 | 8.57 | 5.16 | 0.23 | 2.22 | 1.92 | 1.02 |
| dev / middle C3-B5 (11) | 8.67 | 1.09 | 3.74 | 6.79 | 6.87 | 8.20 | 6.55 | 4.24 | 0.17 | 5.11 | 9.83 | 2.81 |
| dev / treble C6-C8 (5) | 8.48 | 4.07 | 9.36 | 6.34 | 7.92 | 9.60 | 6.67 | 3.64 | 0.28 | 7.03 | 1.67 | 3.13 |

## Regressions

Every note and role where lanes meet by role is worse than shipping 0.4.1 (6691d3e) by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.
