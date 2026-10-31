# Recording benchmark: window against shipping

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## shipping

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev (21) | 8.39 | 1.88 | 4.54 | 6.41 | 7.14 | 8.66 | 7.09 | 4.31 | 0.21 | 4.86 | 6.21 | 2.41 |
| dev / bass A0-B2 (5) | 9.02 | 1.40 | 1.88 | 6.03 | 7.50 | 9.07 | 9.39 | 5.14 | 0.22 | 2.25 | 1.96 | 1.20 |
| dev / middle C3-B5 (11) | 8.40 | 1.09 | 3.71 | 6.73 | 6.77 | 8.09 | 6.50 | 4.24 | 0.17 | 5.11 | 10.19 | 2.63 |
| dev / treble C6-C8 (5) | 7.75 | 4.07 | 9.03 | 6.09 | 7.59 | 9.52 | 6.53 | 3.64 | 0.28 | 6.92 | 1.68 | 3.14 |

## window

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev (21) | 8.46 | 1.88 | 4.52 | 6.37 | 7.09 | 8.63 | 7.06 | 4.29 | 0.21 | 4.83 | 6.01 | 2.46 |
| dev / bass A0-B2 (5) | 9.00 | 1.40 | 1.87 | 6.14 | 7.49 | 9.08 | 9.59 | 5.06 | 0.22 | 2.19 | 1.93 | 1.29 |
| dev / middle C3-B5 (11) | 8.57 | 1.09 | 3.74 | 6.81 | 6.84 | 8.17 | 6.59 | 4.23 | 0.17 | 5.15 | 9.86 | 2.74 |
| dev / treble C6-C8 (5) | 7.68 | 4.07 | 8.88 | 5.64 | 7.23 | 9.19 | 6.07 | 3.64 | 0.28 | 6.75 | 1.63 | 3.02 |

## Regressions

Every note and role where window is worse than shipping by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.
