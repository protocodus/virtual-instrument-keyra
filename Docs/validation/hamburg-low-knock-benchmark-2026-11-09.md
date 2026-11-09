# Recording benchmark: 0.4.28 against 0.4.27

Every train and dev note of `Tools/corpus/split-hamburg-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.27

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (40) | 4.44 | 0.27 | 2.29 | 6.09 | 4.42 | 4.94 | 6.60 | 1.51 | 0.11 | 3.13 | 17.10 | 0.57 |
| dev (8) | 7.11 | 2.53 | 3.68 | 7.19 | 6.19 | 6.09 | 6.00 | 4.76 | 0.23 | 2.31 | 3.01 | 3.12 |
| train / bass A0-B2 (16) | 4.66 | 0.10 | 0.99 | 6.52 | 3.74 | 3.73 | 7.95 | 0.84 | 0.07 | 2.40 | 31.40 | 0.56 |
| train / middle C3-B5 (12) | 4.63 | 0.24 | 2.10 | 6.09 | 4.44 | 4.77 | 6.13 | 1.93 | 0.14 | 1.84 | 12.40 | 0.22 |
| train / treble C6-C8 (12) | 3.97 | 0.52 | 4.22 | 5.51 | 5.30 | 6.73 | 5.62 | 1.98 | 0.15 | 5.41 | 2.73 | 0.92 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.11 | 2.53 | 3.68 | 7.19 | 6.19 | 6.09 | 6.00 | 4.76 | 0.23 | 2.31 | 3.01 | 3.12 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## 0.4.28

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (40) | 4.45 | 0.27 | 2.30 | 6.09 | 4.42 | 4.98 | 6.55 | 1.54 | 0.11 | 3.11 | 16.86 | 0.55 |
| dev (8) | 7.12 | 2.53 | 3.68 | 7.39 | 6.29 | 6.19 | 6.16 | 4.87 | 0.23 | 2.32 | 3.12 | 3.10 |
| train / bass A0-B2 (16) | 4.66 | 0.10 | 0.99 | 6.52 | 3.74 | 3.73 | 7.95 | 0.84 | 0.07 | 2.40 | 31.40 | 0.56 |
| train / middle C3-B5 (12) | 4.64 | 0.24 | 2.11 | 6.15 | 4.47 | 4.75 | 6.10 | 1.99 | 0.13 | 1.82 | 12.06 | 0.23 |
| train / treble C6-C8 (12) | 3.98 | 0.52 | 4.23 | 5.47 | 5.27 | 6.87 | 5.48 | 2.02 | 0.16 | 5.34 | 2.30 | 0.87 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.12 | 2.53 | 3.68 | 7.39 | 6.29 | 6.19 | 6.16 | 4.87 | 0.23 | 2.32 | 3.12 | 3.10 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## Independent-sample regressions (legacy)

Every note and role where 0.4.28 is worse than 0.4.27 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (15.0389 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 8 | 7.1149 | 7.1249 | 0.0100 | 0 | 0 | 0 |
| dev | tuning_cents | 8 | 2.5327 | 2.5327 | 0.0000 | 0 | 0 | 0 |
| dev | decay_db_s | 8 | 3.6773 | 3.6802 | 0.0029 | 0 | 0 | 0 |
| dev | attack_db | 8 | 7.1868 | 7.3931 | 0.2063 | 0 | 0 | 0 |
| dev | early_db | 8 | 6.1899 | 6.2870 | 0.0971 | 0 | 0 | 0 |
| dev | sustain_db | 8 | 6.0904 | 6.1865 | 0.0961 | 0 | 0 | 0 |
| dev | noise_db | 6 | 6.0014 | 6.1569 | 0.1555 | 0 | 0 | 2 |
| dev | ild_db | 8 | 4.7561 | 4.8719 | 0.1158 | 0 | 0 | 0 |
| dev | icc | 8 | 0.2270 | 0.2283 | 0.0013 | 0 | 0 | 0 |
| dev | envelope_db | 8 | 2.3067 | 2.3155 | 0.0088 | 0 | 0 | 0 |
| dev | rise_ms | 8 | 3.0078 | 3.1172 | 0.1094 | 0 | 0 | 0 |
| dev | level_db | 8 | 3.1230 | 3.0872 | -0.0358 | 0 | 0 | 0 |
| train | partial_db | 40 | 4.4433 | 4.4529 | 0.0096 | 0 | 0 | 0 |
| train | tuning_cents | 40 | 0.2658 | 0.2658 | -0.0000 | 0 | 0 | 0 |
| train | decay_db_s | 40 | 2.2946 | 2.3000 | 0.0054 | 0 | 0 | 0 |
| train | attack_db | 40 | 6.0867 | 6.0915 | 0.0048 | 0 | 0 | 0 |
| train | early_db | 40 | 4.4187 | 4.4202 | 0.0015 | 0 | 0 | 0 |
| train | sustain_db | 40 | 4.9388 | 4.9752 | 0.0364 | 0 | 0 | 0 |
| train | noise_db | 37 | 6.6044 | 6.5522 | -0.0522 | 0 | 0 | 3 |
| train | ild_db | 40 | 1.5104 | 1.5402 | 0.0299 | 0 | 0 | 0 |
| train | icc | 40 | 0.1131 | 0.1141 | 0.0010 | 0 | 0 | 0 |
| train | envelope_db | 40 | 3.1328 | 3.1072 | -0.0255 | 0 | 0 | 0 |
| train | rise_ms | 40 | 17.1005 | 16.8646 | -0.2359 | 0 | 0 | 0 |
| train | level_db | 40 | 0.5685 | 0.5546 | -0.0139 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
