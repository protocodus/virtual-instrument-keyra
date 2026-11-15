# Recording benchmark: 2.16.0 Room against 2.15.0 (703587a)

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.15.0 (703587a)

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.31 | 3.28 | 4.58 | 7.60 | 9.04 | 10.45 | 9.88 | 6.39 | 0.24 | 4.27 | 12.15 | 4.29 |
| dev (21) | 7.20 | 3.57 | 4.85 | 7.62 | 8.99 | 9.90 | 8.66 | 6.17 | 0.26 | 4.62 | 9.13 | 3.34 |
| train / bass A0-B2 (30) | 9.43 | 4.82 | 4.39 | 8.49 | 9.27 | 10.36 | 15.43 | 6.72 | 0.19 | 3.00 | 6.53 | 3.67 |
| train / middle C3-B5 (69) | 7.25 | 2.79 | 4.36 | 7.39 | 8.19 | 8.15 | 8.77 | 6.05 | 0.19 | 3.76 | 18.85 | 4.71 |
| train / treble C6-C8 (38) | 5.76 | 2.95 | 5.16 | 7.28 | 10.40 | 14.68 | 7.52 | 6.74 | 0.36 | 6.19 | 4.43 | 4.01 |
| dev / bass A0-B2 (5) | 9.17 | 3.50 | 2.90 | 9.08 | 9.97 | 10.38 | 12.94 | 3.98 | 0.28 | 2.07 | 2.00 | 2.41 |
| dev / middle C3-B5 (11) | 6.32 | 2.49 | 4.38 | 6.90 | 7.59 | 8.08 | 7.08 | 8.07 | 0.21 | 4.77 | 14.60 | 3.73 |
| dev / treble C6-C8 (5) | 7.18 | 6.02 | 7.81 | 7.74 | 11.09 | 13.43 | 7.85 | 4.17 | 0.35 | 6.83 | 4.23 | 3.43 |

## 2.16.0 Room

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.65 | 3.47 | 4.48 | 7.47 | 8.78 | 10.47 | 9.95 | 5.98 | 0.22 | 4.22 | 12.67 | 4.28 |
| dev (21) | 7.63 | 3.90 | 4.96 | 7.50 | 8.51 | 10.00 | 8.56 | 5.41 | 0.24 | 4.55 | 9.12 | 3.48 |
| train / bass A0-B2 (30) | 10.26 | 4.98 | 4.16 | 8.77 | 9.60 | 10.53 | 15.63 | 6.29 | 0.19 | 2.87 | 6.82 | 3.69 |
| train / middle C3-B5 (69) | 7.46 | 2.93 | 4.31 | 7.28 | 7.88 | 8.35 | 8.84 | 5.96 | 0.19 | 3.81 | 19.75 | 4.72 |
| train / treble C6-C8 (38) | 5.94 | 3.27 | 5.06 | 6.77 | 9.77 | 14.27 | 7.50 | 5.76 | 0.31 | 6.04 | 4.42 | 3.97 |
| dev / bass A0-B2 (5) | 8.86 | 3.57 | 2.91 | 9.11 | 10.27 | 10.62 | 12.92 | 3.98 | 0.30 | 1.92 | 1.98 | 2.66 |
| dev / middle C3-B5 (11) | 6.51 | 2.46 | 4.41 | 6.95 | 7.12 | 8.33 | 7.22 | 7.25 | 0.19 | 4.77 | 14.61 | 3.90 |
| dev / treble C6-C8 (5) | 8.85 | 7.40 | 8.21 | 7.09 | 9.82 | 13.06 | 7.16 | 2.78 | 0.29 | 6.67 | 4.18 | 3.39 |

## Independent-sample regressions (legacy)

Every note and role where 2.16.0 Room is worse than 2.15.0 (703587a) by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.15.0 (703587a) | 2.16.0 Room |
|---|---|---|---|---|
| 50 | train | rise_ms | 72.02 | 83.12 |
| 86 | train | tuning_cents | 2.92 | 5.99 |
| 76 | train | icc | 0.17 | 0.28 |
| 42 | train | early_db | 5.94 | 8.18 |
| 24 | train | partial_db | 9.81 | 11.95 |
| 42 | train | noise_db | 13.81 | 15.52 |
| 88 | dev | partial_db | 7.18 | 8.85 |
| 76 | train | tuning_cents | 3.56 | 5.18 |
| 42 | train | attack_db | 8.15 | 9.70 |
| 54 | train | sustain_db | 6.20 | 7.66 |
| 60 | train | icc | 0.11 | 0.17 |
| 54 | train | early_db | 5.45 | 6.88 |
| 88 | dev | tuning_cents | 6.02 | 7.40 |
| 96 | train | noise_db | 7.23 | 8.44 |
| 42 | train | partial_db | 7.88 | 9.01 |
| 96 | train | tuning_cents | 2.08 | 3.18 |
| 76 | train | noise_db | 7.40 | 8.48 |
| 76 | train | partial_db | 8.23 | 9.23 |
| 45 | train | partial_db | 9.93 | 10.92 |
| 66 | train | sustain_db | 9.18 | 10.15 |
| 27 | train | partial_db | 9.73 | 10.67 |
| 42 | train | rise_ms | 6.37 | 8.26 |
| 66 | train | partial_db | 8.62 | 9.56 |
| 42 | train | sustain_db | 5.53 | 6.46 |
| 74 | train | rise_ms | 8.27 | 10.02 |
| 27 | train | icc | 0.18 | 0.22 |
| 86 | train | partial_db | 5.97 | 6.78 |
| 103 | train | partial_db | 3.43 | 4.21 |
| 94 | train | noise_db | 7.21 | 8.00 |
| 78 | train | partial_db | 7.07 | 7.75 |
| 45 | train | noise_db | 14.80 | 15.47 |
| 82 | train | ild_db | 9.24 | 9.90 |
| 24 | train | ild_db | 7.26 | 7.89 |
| 36 | train | tuning_cents | 2.66 | 3.28 |
| 54 | train | noise_db | 11.99 | 12.60 |
| 92 | train | ild_db | 3.35 | 3.95 |
| 72 | dev | partial_db | 5.30 | 5.86 |
| 70 | train | ild_db | 4.23 | 4.77 |
| 39 | dev | icc | 0.28 | 0.30 |
| 76 | train | sustain_db | 11.26 | 11.79 |
| 72 | dev | sustain_db | 9.73 | 10.24 |
| 100 | train | level_db | 2.24 | 2.74 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.5157 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 7.2030 | 7.6277 | 0.4246 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 3.5700 | 3.9002 | 0.3302 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 4.8459 | 4.9574 | 0.1115 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.6183 | 7.4972 | -0.1211 | 0 | 0 | 0 |
| dev | early_db | 21 | 8.9903 | 8.5117 | -0.4787 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 9.9015 | 10.0028 | 0.1013 | 0 | 0 | 0 |
| dev | noise_db | 21 | 8.6569 | 8.5631 | -0.0937 | 0 | 0 | 0 |
| dev | ild_db | 21 | 6.1679 | 5.4076 | -0.7604 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2621 | 0.2430 | -0.0192 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.6185 | 4.5468 | -0.0718 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 9.1280 | 9.1171 | -0.0109 | 0 | 0 | 0 |
| dev | level_db | 21 | 3.3448 | 3.4361 | 0.0913 | 0 | 0 | 0 |
| train | partial_db | 137 | 7.3133 | 7.6526 | 0.3393 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 3.2784 | 3.4748 | 0.1964 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 4.5807 | 4.4778 | -0.1029 | 0 | 0 | 2 |
| train | attack_db | 137 | 7.6000 | 7.4673 | -0.1328 | 0 | 0 | 0 |
| train | early_db | 137 | 9.0416 | 8.7809 | -0.2607 | 0 | 0 | 0 |
| train | sustain_db | 137 | 10.4476 | 10.4679 | 0.0203 | 0 | 0 | 0 |
| train | noise_db | 137 | 9.8806 | 9.9543 | 0.0738 | 0 | 0 | 0 |
| train | ild_db | 135 | 6.3868 | 5.9824 | -0.4044 | 0 | 0 | 2 |
| train | icc | 135 | 0.2368 | 0.2207 | -0.0161 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.2680 | 4.2217 | -0.0463 | 0 | 0 | 0 |
| train | rise_ms | 137 | 12.1513 | 12.6651 | 0.5138 | 0 | 0 | 0 |
| train | level_db | 137 | 4.2902 | 4.2969 | 0.0067 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 50 | train | rise_ms | 5 | 72.0167 | 83.1208 | 11.1042 |
| 86 | train | tuning_cents | 5 | 2.9246 | 5.9859 | 3.0613 |
| 76 | train | icc | 5 | 0.1659 | 0.2767 | 0.1108 |
| 42 | train | early_db | 5 | 5.9358 | 8.1787 | 2.2429 |
| 24 | train | partial_db | 5 | 9.8114 | 11.9509 | 2.1395 |
| 42 | train | noise_db | 5 | 13.8078 | 15.5186 | 1.7108 |
| 88 | dev | partial_db | 5 | 7.1800 | 8.8504 | 1.6704 |
| 76 | train | tuning_cents | 5 | 3.5608 | 5.1834 | 1.6226 |
| 42 | train | attack_db | 5 | 8.1452 | 9.6962 | 1.5510 |
| 54 | train | sustain_db | 5 | 6.2017 | 7.6565 | 1.4548 |
| 60 | train | icc | 5 | 0.1103 | 0.1678 | 0.0575 |
| 54 | train | early_db | 5 | 5.4517 | 6.8816 | 1.4299 |
| 88 | dev | tuning_cents | 5 | 6.0194 | 7.4042 | 1.3849 |
| 96 | train | noise_db | 5 | 7.2292 | 8.4438 | 1.2146 |
| 42 | train | partial_db | 5 | 7.8755 | 9.0050 | 1.1295 |
| 96 | train | tuning_cents | 5 | 2.0762 | 3.1802 | 1.1040 |
| 76 | train | noise_db | 5 | 7.3974 | 8.4789 | 1.0815 |
| 76 | train | partial_db | 5 | 8.2300 | 9.2330 | 1.0031 |
| 45 | train | partial_db | 5 | 9.9311 | 10.9237 | 0.9926 |
| 66 | train | sustain_db | 5 | 9.1754 | 10.1471 | 0.9717 |
| 27 | train | partial_db | 5 | 9.7259 | 10.6743 | 0.9484 |
| 42 | train | rise_ms | 5 | 6.3708 | 8.2625 | 1.8917 |
| 66 | train | partial_db | 5 | 8.6220 | 9.5566 | 0.9347 |
| 42 | train | sustain_db | 5 | 5.5303 | 6.4609 | 0.9306 |
| 74 | train | rise_ms | 5 | 8.2667 | 10.0208 | 1.7542 |
| 27 | train | icc | 5 | 0.1847 | 0.2197 | 0.0350 |
| 100 | train | level_db | 4 | 2.2415 | 3.0729 | 0.8314 |
| 86 | train | partial_db | 5 | 5.9700 | 6.7815 | 0.8115 |
| 103 | train | partial_db | 4 | 3.4270 | 4.2134 | 0.7864 |
| 94 | train | noise_db | 5 | 7.2131 | 7.9970 | 0.7839 |
| 78 | train | partial_db | 5 | 7.0728 | 7.7535 | 0.6808 |
| 45 | train | noise_db | 5 | 14.8009 | 15.4747 | 0.6738 |
| 82 | train | ild_db | 5 | 9.2384 | 9.8962 | 0.6578 |
| 24 | train | ild_db | 5 | 7.2598 | 7.8902 | 0.6304 |
| 36 | train | tuning_cents | 5 | 2.6575 | 3.2822 | 0.6247 |
| 54 | train | noise_db | 5 | 11.9850 | 12.6016 | 0.6166 |
| 92 | train | ild_db | 5 | 3.3500 | 3.9540 | 0.6040 |
| 72 | dev | partial_db | 5 | 5.2961 | 5.8588 | 0.5626 |
| 70 | train | ild_db | 5 | 4.2288 | 4.7748 | 0.5460 |
| 39 | dev | icc | 5 | 0.2810 | 0.3028 | 0.0218 |
| 76 | train | sustain_db | 5 | 11.2582 | 11.7934 | 0.5351 |
| 72 | dev | sustain_db | 5 | 9.7272 | 10.2375 | 0.5103 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
