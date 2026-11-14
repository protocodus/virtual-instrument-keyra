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
| train (276) | 7.90 | 2.26 | 4.04 | 6.52 | 6.37 | 8.62 | 7.14 | 4.92 | 0.20 | 4.30 | 14.07 | 2.42 |
| dev (156) | 7.22 | 2.37 | 3.43 | 6.12 | 5.82 | 7.70 | 6.71 | 5.15 | 0.18 | 3.96 | 13.02 | 2.59 |
| train / bass A0-B2 (84) | 8.56 | 3.15 | 2.57 | 5.87 | 5.52 | 6.31 | 6.59 | 4.37 | 0.21 | 3.32 | 25.31 | 2.09 |
| train / middle C3-B5 (108) | 7.37 | 1.34 | 4.06 | 6.05 | 6.13 | 7.81 | 7.03 | 6.75 | 0.19 | 4.35 | 10.86 | 2.00 |
| train / treble C6-C8 (84) | 7.92 | 2.56 | 5.59 | 7.77 | 7.52 | 11.95 | 7.80 | 2.99 | 0.19 | 5.20 | 6.94 | 3.28 |
| dev / bass A0-B2 (44) | 8.95 | 3.83 | 2.40 | 5.46 | 5.00 | 5.68 | 6.37 | 4.54 | 0.20 | 3.01 | 24.57 | 2.82 |
| dev / middle C3-B5 (68) | 6.74 | 1.21 | 3.65 | 5.87 | 5.68 | 7.14 | 6.61 | 7.11 | 0.15 | 3.96 | 10.79 | 1.97 |
| dev / treble C6-C8 (44) | 6.25 | 2.71 | 4.14 | 7.15 | 6.84 | 10.56 | 7.17 | 2.64 | 0.21 | 4.89 | 4.93 | 3.33 |

## Independent-sample regressions (legacy)

Every note and role where candidate 2.14.0 is worse than shipping 2.13.1 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | shipping 2.13.1 | candidate 2.14.0 |
|---|---|---|---|---|
| 42 | dev | rise_ms | 0.27 | 12.31 |
| 54 | dev | rise_ms | 5.44 | 13.17 |
| 42 | train | rise_ms | 5.14 | 12.60 |
| 54 | train | rise_ms | 4.93 | 11.78 |
| 93 | dev | ild_db | 1.43 | 4.47 |
| 93 | train | ild_db | 1.40 | 4.44 |
| 75 | dev | rise_ms | 2.83 | 8.55 |
| 48 | train | noise_db | 5.77 | 8.23 |
| 57 | dev | envelope_db | 3.69 | 5.80 |
| 57 | train | envelope_db | 3.79 | 5.90 |
| 78 | dev | ild_db | 3.00 | 5.03 |
| 78 | train | ild_db | 3.09 | 5.09 |
| 24 | train | rise_ms | 32.11 | 35.77 |
| 72 | dev | rise_ms | 0.62 | 3.30 |
| 30 | dev | envelope_db | 3.94 | 5.27 |
| 30 | train | envelope_db | 3.99 | 5.25 |
| 66 | dev | sustain_db | 4.55 | 5.79 |
| 66 | train | sustain_db | 4.67 | 5.91 |
| 45 | dev | rise_ms | 25.41 | 27.83 |
| 81 | dev | icc | 0.16 | 0.21 |
| 75 | dev | ild_db | 9.62 | 10.80 |
| 78 | train | envelope_db | 4.83 | 5.97 |
| 36 | dev | rise_ms | 26.21 | 28.42 |
| 78 | dev | envelope_db | 4.91 | 5.99 |
| 81 | train | icc | 0.16 | 0.20 |
| 36 | train | rise_ms | 25.31 | 27.20 |
| 33 | dev | rise_ms | 10.82 | 12.66 |
| 45 | train | envelope_db | 1.92 | 2.80 |
| 54 | dev | sustain_db | 5.62 | 6.50 |
| 54 | train | sustain_db | 5.75 | 6.62 |
| 72 | train | rise_ms | 0.75 | 2.41 |
| 45 | dev | envelope_db | 1.87 | 2.69 |
| 75 | dev | envelope_db | 2.18 | 2.83 |
| 66 | train | ild_db | 7.23 | 7.86 |
| 66 | dev | ild_db | 7.48 | 8.10 |
| 66 | dev | partial_db | 6.50 | 7.12 |
| 57 | dev | sustain_db | 9.32 | 9.94 |
| 57 | train | sustain_db | 9.25 | 9.86 |
| 66 | train | partial_db | 6.50 | 7.11 |
| 27 | dev | envelope_db | 1.95 | 2.51 |
| 96 | dev | level_db | 3.75 | 4.28 |
| 30 | train | tuning_cents | 1.20 | 1.72 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.0940 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 7.5800 | 7.2244 | -0.3555 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.3183 | 2.3732 | 0.0548 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 3.3102 | 3.4327 | 0.1226 | 0 | 0 | 1 |
| dev | attack_db | 156 | 6.3368 | 6.1175 | -0.2193 | 0 | 0 | 0 |
| dev | early_db | 156 | 6.0155 | 5.8151 | -0.2004 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 7.8982 | 7.6963 | -0.2019 | 0 | 0 | 0 |
| dev | noise_db | 153 | 6.8294 | 6.7052 | -0.1242 | 0 | 0 | 3 |
| dev | ild_db | 154 | 4.9548 | 5.1550 | 0.2002 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1844 | 0.1821 | -0.0023 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 4.0239 | 3.9557 | -0.0682 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 12.0019 | 13.0215 | 1.0196 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.6197 | 2.6298 | 0.0102 | 0 | 0 | 0 |
| train | partial_db | 276 | 8.0999 | 7.9010 | -0.1989 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.2028 | 2.2642 | 0.0614 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 3.9267 | 4.0434 | 0.1167 | 0 | 0 | 5 |
| train | attack_db | 276 | 6.6962 | 6.5164 | -0.1798 | 0 | 0 | 0 |
| train | early_db | 276 | 6.4863 | 6.3706 | -0.1157 | 0 | 0 | 0 |
| train | sustain_db | 276 | 8.7205 | 8.6153 | -0.1052 | 0 | 0 | 0 |
| train | noise_db | 271 | 7.2143 | 7.1444 | -0.0698 | 1 | 1 | 3 |
| train | ild_db | 270 | 4.7852 | 4.9227 | 0.1375 | 0 | 0 | 6 |
| train | icc | 270 | 0.1973 | 0.1976 | 0.0003 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.3263 | 4.2967 | -0.0297 | 0 | 0 | 0 |
| train | rise_ms | 276 | 14.2951 | 14.0670 | -0.2282 | 0 | 0 | 0 |
| train | level_db | 276 | 2.4710 | 2.4085 | -0.0625 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 42 | dev | rise_ms | 4 | 0.2708 | 12.3073 | 12.0365 |
| 54 | dev | rise_ms | 4 | 5.4427 | 13.1667 | 7.7240 |
| 42 | train | rise_ms | 12 | 5.1406 | 12.6024 | 7.4618 |
| 54 | train | rise_ms | 12 | 4.9306 | 11.7778 | 6.8472 |
| 93 | dev | ild_db | 4 | 1.4259 | 4.4726 | 3.0467 |
| 93 | train | ild_db | 12 | 1.3969 | 4.4407 | 3.0438 |
| 75 | dev | rise_ms | 16 | 2.8346 | 8.5456 | 5.7109 |
| 48 | train | noise_db | 11 | 5.7734 | 8.2316 | 2.4582 |
| 57 | dev | envelope_db | 4 | 3.6852 | 5.7979 | 2.1127 |
| 57 | train | envelope_db | 12 | 3.7872 | 5.8982 | 2.1110 |
| 78 | dev | ild_db | 4 | 2.9985 | 5.0297 | 2.0311 |
| 78 | train | ild_db | 12 | 3.0866 | 5.0919 | 2.0053 |
| 24 | train | rise_ms | 12 | 32.1076 | 35.7743 | 3.6667 |
| 72 | dev | rise_ms | 4 | 0.6250 | 3.3021 | 2.6771 |
| 30 | dev | envelope_db | 4 | 3.9432 | 5.2742 | 1.3311 |
| 30 | train | envelope_db | 12 | 3.9934 | 5.2472 | 1.2538 |
| 66 | dev | sustain_db | 4 | 4.5477 | 5.7908 | 1.2430 |
| 66 | train | sustain_db | 12 | 4.6651 | 5.9076 | 1.2425 |
| 45 | dev | rise_ms | 4 | 25.4115 | 27.8333 | 2.4219 |
| 81 | dev | icc | 4 | 0.1588 | 0.2065 | 0.0477 |
| 75 | dev | ild_db | 16 | 9.6199 | 10.7954 | 1.1755 |
| 78 | train | envelope_db | 12 | 4.8307 | 5.9662 | 1.1354 |
| 36 | dev | rise_ms | 4 | 26.2135 | 28.4219 | 2.2083 |
| 78 | dev | envelope_db | 4 | 4.9139 | 5.9913 | 1.0774 |
| 81 | train | icc | 12 | 0.1601 | 0.2006 | 0.0405 |
| 36 | train | rise_ms | 12 | 25.3056 | 27.1997 | 1.8941 |
| 33 | dev | rise_ms | 4 | 10.8177 | 12.6562 | 1.8385 |
| 45 | train | envelope_db | 12 | 1.9215 | 2.7971 | 0.8756 |
| 54 | dev | sustain_db | 4 | 5.6240 | 6.4957 | 0.8716 |
| 54 | train | sustain_db | 12 | 5.7518 | 6.6210 | 0.8692 |
| 72 | train | rise_ms | 12 | 0.7483 | 2.4132 | 1.6649 |
| 45 | dev | envelope_db | 4 | 1.8739 | 2.6912 | 0.8173 |
| 60 | dev | level_db | 4 | 0.7385 | 1.4565 | 0.7180 |
| 60 | train | level_db | 12 | 0.6996 | 1.3797 | 0.6801 |
| 75 | dev | envelope_db | 16 | 2.1758 | 2.8267 | 0.6509 |
| 66 | train | ild_db | 12 | 7.2275 | 7.8630 | 0.6355 |
| 66 | dev | ild_db | 4 | 7.4772 | 8.1003 | 0.6231 |
| 66 | dev | partial_db | 4 | 6.4954 | 7.1161 | 0.6208 |
| 57 | dev | sustain_db | 4 | 9.3248 | 9.9425 | 0.6177 |
| 57 | train | sustain_db | 12 | 9.2464 | 9.8635 | 0.6171 |
| 66 | train | partial_db | 12 | 6.4959 | 7.1129 | 0.6170 |
| 78 | dev | level_db | 4 | 3.5725 | 4.1883 | 0.6158 |
| 78 | train | level_db | 12 | 3.5717 | 4.1664 | 0.5946 |
| 27 | dev | envelope_db | 16 | 1.9538 | 2.5082 | 0.5544 |
| 30 | train | tuning_cents | 12 | 1.1966 | 1.7220 | 0.5254 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| A2v2 | 45 | train | noise_db | lost | 10.8395 | - |
| F#1v5 | 30 | train | noise_db | gained | - | 5.4960 |
