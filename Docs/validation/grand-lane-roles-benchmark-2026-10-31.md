# Recording benchmark: lanes meet by role against shipping 0.4.1 (6691d3e)

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## shipping 0.4.1 (6691d3e)

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.62 | 0.25 | 1.79 | 4.44 | 4.19 | 4.60 | 5.62 | 0.92 | 0.06 | 1.95 | 3.87 | 0.69 |
| dev (156) | 5.42 | 1.07 | 2.34 | 4.81 | 4.57 | 5.25 | 5.36 | 2.47 | 0.12 | 2.67 | 4.19 | 1.20 |
| train / bass A0-B2 (84) | 4.65 | 0.04 | 0.44 | 4.76 | 3.96 | 3.74 | 5.43 | 0.42 | 0.03 | 2.12 | 5.53 | 0.43 |
| train / middle C3-B5 (108) | 4.97 | 0.07 | 1.46 | 4.02 | 4.13 | 3.50 | 6.08 | 0.71 | 0.04 | 0.83 | 3.69 | 0.29 |
| train / treble C6-C8 (84) | 4.14 | 0.69 | 3.68 | 4.65 | 4.49 | 6.88 | 5.20 | 1.75 | 0.12 | 3.24 | 2.45 | 1.46 |
| dev / bass A0-B2 (44) | 5.40 | 1.09 | 0.96 | 5.08 | 4.14 | 3.76 | 5.05 | 1.33 | 0.06 | 2.73 | 4.08 | 1.24 |
| dev / middle C3-B5 (68) | 6.48 | 0.65 | 2.57 | 4.63 | 5.05 | 5.72 | 5.80 | 3.77 | 0.12 | 2.18 | 5.41 | 1.03 |
| dev / treble C6-C8 (44) | 3.79 | 1.70 | 3.37 | 4.80 | 4.26 | 6.02 | 5.02 | 1.54 | 0.19 | 3.37 | 2.42 | 1.42 |

## lanes meet by role

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.62 | 0.25 | 1.79 | 4.44 | 4.19 | 4.60 | 5.62 | 0.92 | 0.06 | 1.95 | 3.87 | 0.69 |
| dev (156) | 5.44 | 1.09 | 2.29 | 4.81 | 4.52 | 5.31 | 5.36 | 2.44 | 0.12 | 2.65 | 4.22 | 1.07 |
| train / bass A0-B2 (84) | 4.65 | 0.04 | 0.44 | 4.76 | 3.96 | 3.74 | 5.43 | 0.42 | 0.03 | 2.12 | 5.53 | 0.43 |
| train / middle C3-B5 (108) | 4.97 | 0.07 | 1.46 | 4.02 | 4.13 | 3.50 | 6.08 | 0.71 | 0.04 | 0.83 | 3.69 | 0.29 |
| train / treble C6-C8 (84) | 4.14 | 0.69 | 3.68 | 4.65 | 4.49 | 6.88 | 5.20 | 1.75 | 0.12 | 3.24 | 2.45 | 1.46 |
| dev / bass A0-B2 (44) | 5.42 | 1.16 | 1.05 | 5.07 | 4.12 | 3.79 | 5.06 | 1.43 | 0.07 | 2.74 | 4.15 | 1.20 |
| dev / middle C3-B5 (68) | 6.54 | 0.65 | 2.60 | 4.64 | 4.96 | 5.83 | 5.79 | 3.65 | 0.12 | 2.13 | 5.40 | 0.76 |
| dev / treble C6-C8 (44) | 3.75 | 1.69 | 3.08 | 4.80 | 4.26 | 6.02 | 5.02 | 1.54 | 0.19 | 3.37 | 2.46 | 1.42 |

## Regressions

Every note and role where lanes meet by role is worse than shipping 0.4.1 (6691d3e) by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.
