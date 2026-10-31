# Recording benchmark: window against shipping

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## shipping

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev (156) | 5.39 | 1.15 | 2.32 | 4.78 | 4.55 | 5.35 | 5.33 | 2.44 | 0.12 | 2.66 | 4.76 | 0.94 |
| dev / bass A0-B2 (44) | 5.44 | 1.16 | 1.05 | 5.07 | 4.13 | 3.80 | 4.83 | 1.43 | 0.07 | 2.72 | 6.13 | 1.15 |
| dev / middle C3-B5 (68) | 6.46 | 0.65 | 2.58 | 4.63 | 4.93 | 5.83 | 5.81 | 3.65 | 0.12 | 2.13 | 5.37 | 0.78 |
| dev / treble C6-C8 (44) | 3.70 | 1.94 | 3.21 | 4.73 | 4.38 | 6.15 | 5.09 | 1.55 | 0.19 | 3.43 | 2.43 | 0.99 |

## window

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| dev (156) | 5.33 | 1.15 | 2.32 | 4.79 | 4.52 | 5.31 | 5.34 | 2.44 | 0.12 | 2.65 | 4.61 | 1.01 |
| dev / bass A0-B2 (44) | 5.41 | 1.15 | 1.05 | 5.09 | 4.10 | 3.76 | 4.83 | 1.42 | 0.07 | 2.72 | 5.70 | 1.18 |
| dev / middle C3-B5 (68) | 6.42 | 0.65 | 2.60 | 4.61 | 4.88 | 5.78 | 5.82 | 3.64 | 0.12 | 2.12 | 5.36 | 0.85 |
| dev / treble C6-C8 (44) | 3.57 | 1.94 | 3.19 | 4.78 | 4.39 | 6.14 | 5.12 | 1.56 | 0.19 | 3.42 | 2.36 | 1.07 |

## Regressions

Every note and role where window is worse than shipping by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.
