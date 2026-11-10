# Recording benchmark: 0.4.33 against 0.4.32

Every train and dev note of `Tools/corpus/split-vcsl-kawai-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.32

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (104) | 7.56 | 0.54 | 3.90 | 6.54 | 7.61 | 7.54 | 8.52 | 4.49 | 0.10 | 3.42 | 6.80 | 2.78 |
| dev (23) | 9.40 | 2.38 | 4.99 | 6.91 | 8.77 | 8.34 | 8.98 | 4.87 | 0.20 | 5.03 | 5.32 | 4.20 |
| train / bass A0-B2 (27) | 9.78 | 0.42 | 1.83 | 6.70 | 7.05 | 7.50 | 9.64 | 1.67 | 0.07 | 2.89 | 12.81 | 2.36 |
| train / middle C3-B5 (52) | 7.50 | 0.49 | 4.12 | 6.28 | 7.33 | 7.87 | 8.24 | 5.51 | 0.12 | 3.62 | 5.60 | 2.67 |
| train / treble C6-C8 (25) | 4.99 | 0.78 | 6.88 | 6.92 | 8.91 | 6.55 | 7.99 | 6.44 | 0.07 | 3.59 | 2.81 | 3.46 |
| dev / bass A0-B2 (8) | 10.29 | 2.30 | 2.60 | 5.91 | 6.12 | 8.51 | 9.60 | 3.33 | 0.15 | 3.86 | 8.50 | 1.31 |
| dev / middle C3-B5 (12) | 8.73 | 2.11 | 5.92 | 7.17 | 9.38 | 8.81 | 8.53 | 6.27 | 0.16 | 5.64 | 3.91 | 5.04 |
| dev / treble C6-C8 (3) | 9.91 | 4.30 | 8.95 | 8.56 | 13.38 | 4.87 | 9.00 | 3.38 | 0.66 | 5.75 | 2.49 | 8.57 |

## 0.4.33

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (104) | 7.56 | 0.54 | 3.90 | 6.54 | 7.61 | 7.54 | 8.52 | 4.49 | 0.10 | 3.42 | 6.80 | 2.78 |
| dev (23) | 9.38 | 2.38 | 4.99 | 6.90 | 8.78 | 8.37 | 8.99 | 4.89 | 0.20 | 5.03 | 5.32 | 4.20 |
| train / bass A0-B2 (27) | 9.78 | 0.42 | 1.83 | 6.70 | 7.05 | 7.50 | 9.64 | 1.67 | 0.07 | 2.89 | 12.81 | 2.37 |
| train / middle C3-B5 (52) | 7.50 | 0.49 | 4.12 | 6.28 | 7.33 | 7.87 | 8.24 | 5.51 | 0.12 | 3.62 | 5.60 | 2.67 |
| train / treble C6-C8 (25) | 4.99 | 0.78 | 6.88 | 6.92 | 8.91 | 6.55 | 7.99 | 6.44 | 0.07 | 3.59 | 2.81 | 3.46 |
| dev / bass A0-B2 (8) | 10.28 | 2.30 | 2.61 | 5.93 | 6.20 | 8.60 | 9.57 | 3.34 | 0.15 | 3.86 | 8.50 | 1.31 |
| dev / middle C3-B5 (12) | 8.68 | 2.11 | 5.92 | 7.14 | 9.36 | 8.81 | 8.57 | 6.29 | 0.16 | 5.64 | 3.91 | 5.04 |
| dev / treble C6-C8 (3) | 9.91 | 4.30 | 8.95 | 8.56 | 13.38 | 4.87 | 9.00 | 3.38 | 0.66 | 5.75 | 2.49 | 8.57 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.33 is worse than 0.4.32 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.7734 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 22 | 9.4022 | 9.3773 | -0.0248 | 0 | 0 | 1 |
| dev | tuning_cents | 22 | 2.3760 | 2.3760 | -0.0000 | 0 | 0 | 1 |
| dev | decay_db_s | 22 | 4.9877 | 4.9891 | 0.0014 | 0 | 0 | 1 |
| dev | attack_db | 23 | 6.9117 | 6.9026 | -0.0091 | 0 | 0 | 0 |
| dev | early_db | 23 | 8.7689 | 8.7842 | 0.0153 | 0 | 0 | 0 |
| dev | sustain_db | 22 | 8.3436 | 8.3721 | 0.0285 | 0 | 0 | 1 |
| dev | noise_db | 22 | 8.9846 | 8.9910 | 0.0064 | 0 | 0 | 1 |
| dev | ild_db | 21 | 4.8749 | 4.8873 | 0.0124 | 0 | 0 | 2 |
| dev | icc | 21 | 0.2035 | 0.2016 | -0.0019 | 0 | 0 | 2 |
| dev | envelope_db | 23 | 5.0345 | 5.0319 | -0.0026 | 0 | 0 | 0 |
| dev | rise_ms | 23 | 5.3226 | 5.3217 | -0.0009 | 0 | 0 | 0 |
| dev | level_db | 23 | 4.2010 | 4.2014 | 0.0004 | 0 | 0 | 0 |
| train | partial_db | 100 | 7.5633 | 7.5633 | 0.0000 | 0 | 0 | 4 |
| train | tuning_cents | 100 | 0.5385 | 0.5385 | 0.0000 | 0 | 0 | 4 |
| train | decay_db_s | 93 | 3.9032 | 3.9032 | 0.0000 | 0 | 0 | 11 |
| train | attack_db | 104 | 6.5424 | 6.5424 | -0.0000 | 0 | 0 | 0 |
| train | early_db | 102 | 7.6116 | 7.6116 | -0.0000 | 0 | 0 | 2 |
| train | sustain_db | 94 | 7.5413 | 7.5413 | -0.0000 | 0 | 0 | 10 |
| train | noise_db | 95 | 8.5153 | 8.5154 | 0.0001 | 0 | 0 | 9 |
| train | ild_db | 90 | 4.4939 | 4.4942 | 0.0003 | 0 | 0 | 14 |
| train | icc | 90 | 0.0972 | 0.0972 | -0.0000 | 0 | 0 | 14 |
| train | envelope_db | 104 | 3.4221 | 3.4221 | -0.0000 | 0 | 0 | 0 |
| train | rise_ms | 104 | 6.8010 | 6.8010 | 0.0000 | 0 | 0 | 0 |
| train | level_db | 104 | 2.7813 | 2.7816 | 0.0003 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
