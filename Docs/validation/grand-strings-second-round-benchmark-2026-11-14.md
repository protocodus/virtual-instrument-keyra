# Recording benchmark: candidate 2.14.0 against shipping 2.13.1

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## shipping 2.13.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.10 | 2.20 | 3.93 | 6.70 | 6.49 | 8.72 | 7.23 | 4.79 | 0.20 | 4.33 | 14.30 | 2.47 |
| dev (156) | 7.58 | 2.32 | 3.31 | 6.34 | 6.02 | 7.90 | 6.83 | 4.95 | 0.18 | 4.02 | 12.00 | 2.62 |
| train / bass A0-B2 (84) | 9.03 | 2.85 | 2.47 | 6.07 | 5.55 | 6.66 | 6.65 | 4.25 | 0.21 | 3.55 | 24.22 | 2.25 |
| train / middle C3-B5 (108) | 7.47 | 1.41 | 3.87 | 6.30 | 6.32 | 7.77 | 7.14 | 6.77 | 0.19 | 4.25 | 12.33 | 2.03 |
| train / treble C6-C8 (84) | 7.98 | 2.57 | 5.56 | 7.83 | 7.63 | 12.00 | 7.90 | 2.61 | 0.19 | 5.21 | 6.91 | 3.26 |
| dev / bass A0-B2 (44) | 9.69 | 3.52 | 2.29 | 5.88 | 5.12 | 5.91 | 6.34 | 4.47 | 0.21 | 3.00 | 22.95 | 3.04 |
| dev / middle C3-B5 (68) | 7.04 | 1.28 | 3.44 | 6.08 | 6.00 | 7.44 | 6.87 | 6.84 | 0.15 | 4.13 | 9.49 | 1.94 |
| dev / treble C6-C8 (44) | 6.31 | 2.71 | 4.14 | 7.18 | 6.94 | 10.60 | 7.25 | 2.41 | 0.22 | 4.89 | 4.94 | 3.25 |

## candidate 2.14.0

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

## Independent-sample regressions (legacy)

Every note and role where candidate 2.14.0 is worse than shipping 2.13.1 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | shipping 2.13.1 | candidate 2.14.0 |
|---|---|---|---|---|
| 42 | dev | rise_ms | 0.27 | 12.34 |
| 42 | train | rise_ms | 5.14 | 13.74 |
| 54 | dev | rise_ms | 5.44 | 13.15 |
| 54 | train | rise_ms | 4.93 | 11.76 |
| 75 | dev | rise_ms | 2.83 | 8.52 |
| 93 | train | ild_db | 1.40 | 4.03 |
| 93 | dev | ild_db | 1.43 | 4.05 |
| 66 | dev | sustain_db | 4.55 | 7.02 |
| 66 | train | sustain_db | 4.67 | 7.11 |
| 78 | dev | ild_db | 3.00 | 4.85 |
| 78 | train | ild_db | 3.09 | 4.91 |
| 24 | train | rise_ms | 32.11 | 35.67 |
| 45 | train | envelope_db | 1.92 | 3.41 |
| 45 | dev | envelope_db | 1.87 | 3.33 |
| 72 | dev | rise_ms | 0.62 | 3.31 |
| 30 | dev | envelope_db | 3.94 | 5.23 |
| 30 | train | envelope_db | 3.99 | 5.15 |
| 66 | dev | early_db | 4.84 | 5.99 |
| 81 | dev | icc | 0.16 | 0.20 |
| 36 | dev | rise_ms | 26.21 | 28.32 |
| 66 | train | early_db | 5.04 | 6.06 |
| 33 | train | rise_ms | 5.37 | 7.41 |
| 81 | train | icc | 0.16 | 0.20 |
| 57 | dev | sustain_db | 9.32 | 10.27 |
| 36 | train | rise_ms | 25.31 | 27.18 |
| 75 | dev | ild_db | 9.62 | 10.55 |
| 54 | dev | sustain_db | 5.62 | 6.52 |
| 54 | train | sustain_db | 5.75 | 6.65 |
| 33 | dev | rise_ms | 10.82 | 12.60 |
| 57 | train | sustain_db | 9.25 | 10.12 |
| 66 | train | envelope_db | 2.02 | 2.86 |
| 72 | train | rise_ms | 0.75 | 2.41 |
| 66 | dev | envelope_db | 1.93 | 2.72 |
| 75 | dev | envelope_db | 2.18 | 2.95 |
| 45 | train | decay_db_s | 1.91 | 3.26 |
| 66 | dev | partial_db | 6.50 | 7.16 |
| 66 | train | partial_db | 6.50 | 7.14 |
| 45 | dev | decay_db_s | 1.97 | 3.26 |
| 78 | train | envelope_db | 4.83 | 5.47 |
| 57 | train | envelope_db | 3.79 | 4.43 |
| 57 | dev | envelope_db | 3.69 | 4.32 |
| 27 | dev | envelope_db | 1.95 | 2.57 |
| 48 | train | ild_db | 9.91 | 10.53 |
| 72 | dev | decay_db_s | 3.46 | 4.69 |
| 48 | dev | ild_db | 9.64 | 10.25 |
| 72 | train | decay_db_s | 3.71 | 4.88 |
| 78 | dev | envelope_db | 4.91 | 5.48 |
| 69 | train | sustain_db | 5.74 | 6.26 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.0940 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 7.5800 | 7.3176 | -0.2624 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.3183 | 2.2813 | -0.0370 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 3.3102 | 3.4035 | 0.0934 | 0 | 0 | 1 |
| dev | attack_db | 156 | 6.3368 | 6.1281 | -0.2086 | 0 | 0 | 0 |
| dev | early_db | 156 | 6.0155 | 5.8817 | -0.1338 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 7.8982 | 7.7161 | -0.1822 | 0 | 0 | 0 |
| dev | noise_db | 153 | 6.8294 | 6.7252 | -0.1042 | 0 | 0 | 3 |
| dev | ild_db | 154 | 4.9548 | 5.1055 | 0.1507 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1844 | 0.1813 | -0.0032 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 4.0239 | 3.8803 | -0.1435 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 12.0019 | 12.9840 | 0.9821 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.6197 | 2.6074 | -0.0122 | 0 | 0 | 0 |
| train | partial_db | 276 | 8.0999 | 7.9388 | -0.1611 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.2028 | 2.1864 | -0.0164 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 3.9267 | 4.0288 | 0.1021 | 0 | 0 | 5 |
| train | attack_db | 276 | 6.6962 | 6.5201 | -0.1762 | 0 | 0 | 0 |
| train | early_db | 276 | 6.4863 | 6.4361 | -0.0502 | 0 | 0 | 0 |
| train | sustain_db | 276 | 8.7205 | 8.7587 | 0.0382 | 0 | 0 | 0 |
| train | noise_db | 272 | 7.2276 | 7.0311 | -0.1965 | 0 | 1 | 3 |
| train | ild_db | 270 | 4.7852 | 4.8757 | 0.0905 | 0 | 0 | 6 |
| train | icc | 270 | 0.1973 | 0.1965 | -0.0008 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.3263 | 4.1868 | -0.1396 | 0 | 0 | 0 |
| train | rise_ms | 276 | 14.2951 | 14.0408 | -0.2544 | 0 | 0 | 0 |
| train | level_db | 276 | 2.4710 | 2.3882 | -0.0827 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 42 | dev | rise_ms | 4 | 0.2708 | 12.3385 | 12.0677 |
| 42 | train | rise_ms | 12 | 5.1406 | 13.7448 | 8.6042 |
| 54 | dev | rise_ms | 4 | 5.4427 | 13.1510 | 7.7083 |
| 54 | train | rise_ms | 12 | 4.9306 | 11.7604 | 6.8299 |
| 75 | dev | rise_ms | 16 | 2.8346 | 8.5234 | 5.6888 |
| 93 | train | ild_db | 12 | 1.3969 | 4.0334 | 2.6365 |
| 93 | dev | ild_db | 4 | 1.4259 | 4.0515 | 2.6256 |
| 66 | dev | sustain_db | 4 | 4.5477 | 7.0182 | 2.4705 |
| 66 | train | sustain_db | 12 | 4.6651 | 7.1051 | 2.4401 |
| 78 | dev | ild_db | 4 | 2.9985 | 4.8493 | 1.8508 |
| 78 | train | ild_db | 12 | 3.0866 | 4.9110 | 1.8245 |
| 24 | train | rise_ms | 12 | 32.1076 | 35.6736 | 3.5660 |
| 45 | train | envelope_db | 12 | 1.9215 | 3.4089 | 1.4874 |
| 45 | dev | envelope_db | 4 | 1.8739 | 3.3313 | 1.4574 |
| 72 | dev | rise_ms | 4 | 0.6250 | 3.3073 | 2.6823 |
| 30 | dev | envelope_db | 4 | 3.9432 | 5.2275 | 1.2844 |
| 30 | train | envelope_db | 12 | 3.9934 | 5.1533 | 1.1599 |
| 66 | dev | early_db | 4 | 4.8408 | 5.9882 | 1.1474 |
| 81 | dev | icc | 4 | 0.1588 | 0.2037 | 0.0449 |
| 36 | dev | rise_ms | 4 | 26.2135 | 28.3177 | 2.1042 |
| 66 | train | early_db | 12 | 5.0371 | 6.0571 | 1.0200 |
| 33 | train | rise_ms | 12 | 5.3733 | 7.4115 | 2.0382 |
| 81 | train | icc | 12 | 0.1601 | 0.1985 | 0.0384 |
| 57 | dev | sustain_db | 4 | 9.3248 | 10.2696 | 0.9448 |
| 36 | train | rise_ms | 12 | 25.3056 | 27.1823 | 1.8767 |
| 75 | dev | ild_db | 16 | 9.6199 | 10.5456 | 0.9257 |
| 54 | dev | sustain_db | 4 | 5.6240 | 6.5223 | 0.8983 |
| 54 | train | sustain_db | 12 | 5.7518 | 6.6456 | 0.8939 |
| 33 | dev | rise_ms | 4 | 10.8177 | 12.5990 | 1.7813 |
| 57 | train | sustain_db | 12 | 9.2464 | 10.1224 | 0.8760 |
| 66 | train | envelope_db | 12 | 2.0226 | 2.8612 | 0.8386 |
| 72 | train | rise_ms | 12 | 0.7483 | 2.4149 | 1.6667 |
| 66 | dev | envelope_db | 4 | 1.9285 | 2.7244 | 0.7959 |
| 75 | dev | envelope_db | 16 | 2.1758 | 2.9529 | 0.7771 |
| 60 | dev | level_db | 4 | 0.7385 | 1.4768 | 0.7383 |
| 78 | dev | level_db | 4 | 3.5725 | 4.3054 | 0.7329 |
| 78 | train | level_db | 12 | 3.5717 | 4.2839 | 0.7122 |
| 60 | train | level_db | 12 | 0.6996 | 1.4001 | 0.7004 |
| 45 | train | decay_db_s | 12 | 1.9058 | 3.2551 | 1.3493 |
| 72 | dev | level_db | 4 | 1.7515 | 2.4183 | 0.6667 |
| 66 | dev | partial_db | 4 | 6.4954 | 7.1589 | 0.6635 |
| 66 | train | partial_db | 12 | 6.4959 | 7.1426 | 0.6467 |
| 45 | dev | decay_db_s | 4 | 1.9698 | 3.2550 | 1.2852 |
| 78 | train | envelope_db | 12 | 4.8307 | 5.4725 | 0.6418 |
| 57 | train | envelope_db | 12 | 3.7872 | 4.4258 | 0.6386 |
| 57 | dev | envelope_db | 4 | 3.6852 | 4.3236 | 0.6384 |
| 27 | dev | envelope_db | 16 | 1.9538 | 2.5726 | 0.6188 |
| 48 | train | ild_db | 12 | 9.9139 | 10.5316 | 0.6178 |
| 72 | dev | decay_db_s | 4 | 3.4625 | 4.6884 | 1.2259 |
| 48 | dev | ild_db | 4 | 9.6429 | 10.2479 | 0.6050 |
| 72 | train | level_db | 12 | 1.7036 | 2.3006 | 0.5970 |
| 72 | train | decay_db_s | 12 | 3.7084 | 4.8761 | 1.1676 |
| 78 | dev | envelope_db | 4 | 4.9139 | 5.4847 | 0.5708 |
| 75 | dev | level_db | 16 | 2.7780 | 3.3186 | 0.5406 |
| 69 | train | sustain_db | 12 | 5.7374 | 6.2588 | 0.5214 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| F#1v5 | 30 | train | noise_db | gained | - | 4.1838 |
