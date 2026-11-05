# Recording benchmark: candidate 0.4.19 against shipping 0.4.18

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## shipping 0.4.18

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 5.76 | 0.28 | 2.37 | 5.15 | 5.28 | 5.73 | 7.42 | 2.13 | 0.14 | 2.62 | 7.80 | 1.19 |
| dev (21) | 8.38 | 1.81 | 4.13 | 6.47 | 7.28 | 8.81 | 6.83 | 4.22 | 0.21 | 4.80 | 6.22 | 2.52 |
| train / bass A0-B2 (30) | 6.90 | 0.26 | 1.91 | 5.62 | 5.17 | 5.35 | 10.26 | 1.28 | 0.10 | 2.49 | 8.78 | 0.94 |
| train / middle C3-B5 (69) | 6.58 | 0.24 | 2.55 | 5.34 | 4.94 | 5.45 | 7.58 | 1.94 | 0.10 | 2.14 | 9.55 | 1.39 |
| train / treble C6-C8 (38) | 3.36 | 0.36 | 2.42 | 4.43 | 5.97 | 6.56 | 5.43 | 3.20 | 0.24 | 3.59 | 3.87 | 1.03 |
| dev / bass A0-B2 (5) | 8.78 | 1.22 | 2.07 | 5.79 | 7.48 | 8.96 | 7.09 | 5.19 | 0.20 | 2.09 | 1.41 | 1.41 |
| dev / middle C3-B5 (11) | 8.55 | 1.08 | 3.98 | 7.08 | 6.96 | 8.14 | 6.90 | 4.21 | 0.17 | 4.86 | 10.55 | 2.71 |
| dev / treble C6-C8 (5) | 7.60 | 4.00 | 6.50 | 5.82 | 7.81 | 10.12 | 6.46 | 3.27 | 0.29 | 7.37 | 1.51 | 3.20 |

## candidate 0.4.19

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 5.76 | 0.28 | 2.38 | 5.15 | 5.28 | 5.73 | 7.42 | 2.13 | 0.14 | 2.62 | 7.80 | 1.19 |
| dev (21) | 8.38 | 1.77 | 4.04 | 6.47 | 7.28 | 8.81 | 6.83 | 4.22 | 0.21 | 4.80 | 6.22 | 2.52 |
| train / bass A0-B2 (30) | 6.90 | 0.29 | 1.93 | 5.61 | 5.18 | 5.36 | 10.26 | 1.28 | 0.10 | 2.51 | 8.78 | 0.95 |
| train / middle C3-B5 (69) | 6.58 | 0.23 | 2.55 | 5.34 | 4.94 | 5.45 | 7.58 | 1.94 | 0.10 | 2.14 | 9.54 | 1.39 |
| train / treble C6-C8 (38) | 3.37 | 0.36 | 2.42 | 4.43 | 5.97 | 6.56 | 5.43 | 3.20 | 0.24 | 3.59 | 3.87 | 1.03 |
| dev / bass A0-B2 (5) | 8.81 | 1.25 | 2.08 | 5.79 | 7.48 | 8.96 | 7.09 | 5.19 | 0.20 | 2.09 | 1.42 | 1.41 |
| dev / middle C3-B5 (11) | 8.54 | 0.99 | 3.81 | 7.07 | 6.96 | 8.14 | 6.90 | 4.21 | 0.17 | 4.86 | 10.55 | 2.71 |
| dev / treble C6-C8 (5) | 7.60 | 4.00 | 6.50 | 5.82 | 7.81 | 10.12 | 6.46 | 3.27 | 0.29 | 7.37 | 1.51 | 3.20 |

## Independent-sample regressions (legacy)

Every note and role where candidate 0.4.19 is worse than shipping 0.4.18 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (15.9384 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 8.3752 | 8.3806 | 0.0053 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 1.8091 | 1.7676 | -0.0415 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 4.1272 | 4.0379 | -0.0893 | 0 | 0 | 0 |
| dev | attack_db | 21 | 6.4690 | 6.4688 | -0.0002 | 0 | 0 | 0 |
| dev | early_db | 21 | 7.2849 | 7.2839 | -0.0010 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 8.8076 | 8.8073 | -0.0003 | 0 | 0 | 0 |
| dev | noise_db | 20 | 6.8276 | 6.8267 | -0.0009 | 0 | 0 | 1 |
| dev | ild_db | 21 | 4.2198 | 4.2201 | 0.0003 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2082 | 0.2082 | 0.0000 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.7974 | 4.7971 | -0.0003 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 6.2192 | 6.2212 | 0.0020 | 0 | 0 | 0 |
| dev | level_db | 21 | 2.5198 | 2.5202 | 0.0004 | 0 | 0 | 0 |
| train | partial_db | 137 | 5.7573 | 5.7572 | -0.0001 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 0.2759 | 0.2816 | 0.0057 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 2.3737 | 2.3784 | 0.0048 | 0 | 0 | 2 |
| train | attack_db | 137 | 5.1504 | 5.1500 | -0.0004 | 0 | 0 | 0 |
| train | early_db | 137 | 5.2767 | 5.2785 | 0.0018 | 0 | 0 | 0 |
| train | sustain_db | 136 | 5.7265 | 5.7290 | 0.0025 | 0 | 0 | 1 |
| train | noise_db | 125 | 7.4180 | 7.4177 | -0.0003 | 0 | 0 | 12 |
| train | ild_db | 135 | 2.1316 | 2.1318 | 0.0002 | 0 | 0 | 2 |
| train | icc | 135 | 0.1378 | 0.1377 | -0.0001 | 0 | 0 | 2 |
| train | envelope_db | 137 | 2.6177 | 2.6223 | 0.0046 | 0 | 0 | 0 |
| train | rise_ms | 137 | 7.8047 | 7.8002 | -0.0046 | 0 | 0 | 0 |
| train | level_db | 137 | 1.1923 | 1.1923 | 0.0000 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
