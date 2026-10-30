# Recording benchmark: candidate 0.4.1 against 0.4.1 at 4b11922

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. Means per role and register.

## 0.4.1 at 4b11922

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 6.00 | 0.26 | 2.39 | 5.10 | 5.24 | 5.56 | 6.61 | 2.11 | 0.13 | 2.49 | 8.60 | 0.88 |
| dev (21) | 8.81 | 1.92 | 4.35 | 6.64 | 7.27 | 8.78 | 6.97 | 4.54 | 0.18 | 5.07 | 6.59 | 2.46 |
| train / bass A0-B2 (30) | 7.06 | 0.24 | 1.84 | 5.50 | 5.06 | 5.37 | 8.35 | 1.28 | 0.09 | 2.47 | 13.01 | 0.96 |
| train / middle C3-B5 (69) | 6.76 | 0.19 | 2.62 | 5.16 | 4.90 | 5.47 | 6.28 | 1.90 | 0.10 | 2.16 | 8.88 | 0.44 |
| train / treble C6-C8 (38) | 3.78 | 0.39 | 2.41 | 4.66 | 6.00 | 5.87 | 5.97 | 3.21 | 0.23 | 3.12 | 4.59 | 1.61 |
| dev / bass A0-B2 (5) | 9.37 | 1.33 | 2.02 | 6.21 | 7.38 | 9.32 | 8.50 | 4.99 | 0.20 | 2.48 | 1.63 | 1.10 |
| dev / middle C3-B5 (11) | 8.76 | 1.12 | 3.63 | 6.74 | 6.98 | 8.30 | 6.44 | 4.31 | 0.16 | 5.58 | 11.02 | 2.77 |
| dev / treble C6-C8 (5) | 8.36 | 4.25 | 8.25 | 6.85 | 7.79 | 9.32 | 6.91 | 4.58 | 0.20 | 6.55 | 1.82 | 3.13 |

## candidate 0.4.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 6.00 | 0.26 | 2.39 | 5.03 | 5.24 | 5.56 | 6.56 | 2.11 | 0.13 | 2.49 | 8.52 | 0.87 |
| dev (21) | 8.81 | 1.92 | 4.35 | 6.55 | 7.28 | 8.79 | 6.92 | 4.52 | 0.18 | 5.08 | 6.59 | 2.46 |
| train / bass A0-B2 (30) | 7.06 | 0.24 | 1.84 | 5.50 | 5.06 | 5.37 | 8.35 | 1.28 | 0.09 | 2.47 | 13.01 | 0.96 |
| train / middle C3-B5 (69) | 6.76 | 0.19 | 2.62 | 5.13 | 4.90 | 5.47 | 6.23 | 1.90 | 0.10 | 2.16 | 8.84 | 0.44 |
| train / treble C6-C8 (38) | 3.79 | 0.39 | 2.40 | 4.49 | 6.01 | 5.87 | 5.89 | 3.20 | 0.23 | 3.12 | 4.40 | 1.60 |
| dev / bass A0-B2 (5) | 9.37 | 1.33 | 2.02 | 6.21 | 7.37 | 9.31 | 8.50 | 4.99 | 0.20 | 2.48 | 1.63 | 1.10 |
| dev / middle C3-B5 (11) | 8.76 | 1.12 | 3.63 | 6.74 | 6.98 | 8.30 | 6.44 | 4.31 | 0.16 | 5.58 | 11.02 | 2.77 |
| dev / treble C6-C8 (5) | 8.37 | 4.24 | 8.25 | 6.47 | 7.82 | 9.35 | 6.72 | 4.52 | 0.20 | 6.57 | 1.79 | 3.14 |

## Regressions

Every note and role where candidate 0.4.1 is worse than 0.4.1 at 4b11922 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.
