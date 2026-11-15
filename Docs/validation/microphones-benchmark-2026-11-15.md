# Recording benchmark: candidate 2.15.0 against shipping 2.14.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## shipping 2.14.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 7.94 | 2.19 | 4.03 | 6.52 | 6.44 | 8.76 | 7.02 | 4.88 | 0.20 | 4.19 | 14.04 | 2.40 |
| dev (156) | 7.32 | 2.28 | 3.40 | 6.13 | 5.88 | 7.72 | 6.73 | 5.11 | 0.18 | 3.88 | 12.98 | 2.56 |
| train / bass A0-B2 (84) | 8.63 | 2.97 | 2.64 | 5.83 | 5.50 | 6.38 | 6.50 | 4.30 | 0.21 | 3.38 | 25.19 | 2.01 |
| train / middle C3-B5 (108) | 7.39 | 1.26 | 3.90 | 6.11 | 6.33 | 8.06 | 6.82 | 6.74 | 0.19 | 3.96 | 10.88 | 2.03 |
| train / treble C6-C8 (84) | 7.95 | 2.59 | 5.68 | 7.74 | 7.51 | 12.03 | 7.78 | 2.92 | 0.19 | 5.29 | 6.95 | 3.25 |
| dev / bass A0-B2 (44) | 9.17 | 3.63 | 2.47 | 5.44 | 4.99 | 5.70 | 6.40 | 4.50 | 0.20 | 3.08 | 24.41 | 2.68 |
| dev / middle C3-B5 (68) | 6.82 | 1.13 | 3.51 | 5.94 | 5.86 | 7.10 | 6.66 | 7.05 | 0.15 | 3.67 | 10.78 | 2.02 |
| dev / treble C6-C8 (44) | 6.23 | 2.71 | 4.19 | 7.11 | 6.81 | 10.68 | 7.14 | 2.58 | 0.21 | 5.00 | 4.96 | 3.27 |

## candidate 2.15.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 7.95 | 2.19 | 4.03 | 6.50 | 6.43 | 8.76 | 7.03 | 4.88 | 0.20 | 4.19 | 13.85 | 2.39 |
| dev (156) | 7.31 | 2.28 | 3.41 | 6.11 | 5.88 | 7.72 | 6.72 | 5.11 | 0.18 | 3.88 | 12.75 | 2.56 |
| train / bass A0-B2 (84) | 8.65 | 2.98 | 2.65 | 5.80 | 5.49 | 6.38 | 6.51 | 4.30 | 0.21 | 3.37 | 25.01 | 2.01 |
| train / middle C3-B5 (108) | 7.40 | 1.26 | 3.90 | 6.09 | 6.33 | 8.06 | 6.85 | 6.74 | 0.19 | 3.96 | 10.54 | 2.03 |
| train / treble C6-C8 (84) | 7.95 | 2.60 | 5.68 | 7.72 | 7.51 | 12.03 | 7.77 | 2.92 | 0.19 | 5.31 | 6.94 | 3.24 |
| dev / bass A0-B2 (44) | 9.15 | 3.63 | 2.48 | 5.42 | 4.98 | 5.70 | 6.36 | 4.50 | 0.20 | 3.07 | 23.50 | 2.68 |
| dev / middle C3-B5 (68) | 6.83 | 1.13 | 3.51 | 5.93 | 5.86 | 7.10 | 6.68 | 7.05 | 0.15 | 3.67 | 10.84 | 2.02 |
| dev / treble C6-C8 (44) | 6.23 | 2.71 | 4.19 | 7.08 | 6.80 | 10.68 | 7.13 | 2.58 | 0.21 | 5.01 | 4.96 | 3.27 |

## Independent-sample regressions (legacy)

Every note and role where candidate 2.15.0 is worse than shipping 2.14.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | shipping 2.14.0 | candidate 2.15.0 |
|---|---|---|---|---|
| 33 | train | rise_ms | 7.41 | 9.93 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.3973 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 7.3176 | 7.3134 | -0.0042 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.2813 | 2.2806 | -0.0007 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 3.4035 | 3.4068 | 0.0033 | 0 | 0 | 1 |
| dev | attack_db | 156 | 6.1281 | 6.1102 | -0.0179 | 0 | 0 | 0 |
| dev | early_db | 156 | 5.8817 | 5.8794 | -0.0022 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 7.7161 | 7.7156 | -0.0005 | 0 | 0 | 0 |
| dev | noise_db | 153 | 6.7252 | 6.7213 | -0.0039 | 0 | 0 | 3 |
| dev | ild_db | 154 | 5.1055 | 5.1053 | -0.0002 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1813 | 0.1813 | -0.0000 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 3.8803 | 3.8818 | 0.0015 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 12.9840 | 12.7519 | -0.2321 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.5603 | 2.5589 | -0.0015 | 0 | 0 | 0 |
| train | partial_db | 276 | 7.9388 | 7.9456 | 0.0068 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.1864 | 2.1894 | 0.0030 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 4.0288 | 4.0311 | 0.0023 | 0 | 0 | 5 |
| train | attack_db | 276 | 6.5201 | 6.4989 | -0.0212 | 0 | 0 | 0 |
| train | early_db | 276 | 6.4361 | 6.4338 | -0.0023 | 0 | 0 | 0 |
| train | sustain_db | 276 | 8.7587 | 8.7579 | -0.0008 | 0 | 0 | 0 |
| train | noise_db | 273 | 7.0207 | 7.0310 | 0.0104 | 0 | 0 | 3 |
| train | ild_db | 270 | 4.8757 | 4.8751 | -0.0006 | 0 | 0 | 6 |
| train | icc | 270 | 0.1965 | 0.1965 | -0.0000 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.1868 | 4.1917 | 0.0049 | 0 | 0 | 0 |
| train | rise_ms | 276 | 14.0408 | 13.8492 | -0.1916 | 0 | 0 | 0 |
| train | level_db | 276 | 2.3954 | 2.3944 | -0.0009 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 33 | train | rise_ms | 12 | 7.4115 | 9.9253 | 2.5139 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
