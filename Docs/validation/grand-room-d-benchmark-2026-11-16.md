# Recording benchmark: 2.17.0 room against 2.16.2

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.16.2

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.08 | 2.14 | 4.07 | 6.53 | 6.48 | 8.73 | 7.11 | 4.94 | 0.20 | 4.23 | 13.72 | 2.42 |
| dev (156) | 7.43 | 2.45 | 3.43 | 6.24 | 6.03 | 7.74 | 6.95 | 4.81 | 0.18 | 3.88 | 12.57 | 2.72 |
| train / bass A0-B2 (84) | 8.71 | 3.09 | 2.66 | 5.68 | 5.35 | 6.32 | 6.49 | 4.67 | 0.21 | 3.45 | 24.45 | 2.05 |
| train / middle C3-B5 (108) | 7.65 | 1.25 | 3.91 | 6.40 | 6.48 | 8.03 | 7.06 | 6.56 | 0.20 | 3.92 | 10.62 | 2.07 |
| train / treble C6-C8 (84) | 8.01 | 2.33 | 5.78 | 7.56 | 7.62 | 12.05 | 7.79 | 3.00 | 0.20 | 5.42 | 6.98 | 3.23 |
| dev / bass A0-B2 (44) | 8.97 | 3.83 | 2.50 | 5.30 | 4.82 | 5.66 | 6.46 | 4.52 | 0.18 | 3.13 | 22.70 | 2.75 |
| dev / middle C3-B5 (68) | 7.20 | 1.16 | 3.55 | 6.42 | 6.21 | 7.22 | 7.12 | 6.67 | 0.15 | 3.60 | 10.98 | 2.22 |
| dev / treble C6-C8 (44) | 6.25 | 3.05 | 4.19 | 6.91 | 6.95 | 10.63 | 7.16 | 2.12 | 0.22 | 5.05 | 4.88 | 3.45 |

## 2.17.0 room

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.07 | 2.06 | 4.00 | 6.49 | 6.41 | 8.75 | 7.05 | 5.13 | 0.20 | 4.22 | 12.94 | 2.48 |
| dev (156) | 7.55 | 2.47 | 3.37 | 6.28 | 6.06 | 7.86 | 6.86 | 5.21 | 0.19 | 3.86 | 12.06 | 2.72 |
| train / bass A0-B2 (84) | 8.94 | 2.98 | 2.66 | 5.88 | 5.64 | 6.48 | 6.65 | 4.36 | 0.20 | 3.43 | 23.23 | 1.97 |
| train / middle C3-B5 (108) | 7.21 | 1.20 | 3.90 | 6.05 | 6.18 | 7.94 | 6.84 | 7.13 | 0.19 | 3.96 | 9.93 | 2.16 |
| train / treble C6-C8 (84) | 8.30 | 2.26 | 5.56 | 7.66 | 7.49 | 12.04 | 7.71 | 3.21 | 0.23 | 5.36 | 6.52 | 3.42 |
| dev / bass A0-B2 (44) | 9.26 | 3.76 | 2.47 | 5.48 | 5.04 | 5.74 | 6.42 | 4.52 | 0.19 | 3.02 | 21.81 | 2.59 |
| dev / middle C3-B5 (68) | 7.14 | 1.17 | 3.54 | 6.30 | 6.19 | 7.40 | 6.98 | 7.13 | 0.15 | 3.61 | 10.59 | 2.20 |
| dev / treble C6-C8 (44) | 6.48 | 3.18 | 4.02 | 7.04 | 6.86 | 10.69 | 7.10 | 2.82 | 0.24 | 5.07 | 4.59 | 3.66 |

## Independent-sample regressions (legacy)

Every note and role where 2.17.0 room is worse than 2.16.2 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.16.2 | 2.17.0 room |
|---|---|---|---|---|
| 93 | dev | ild_db | 3.38 | 7.43 |
| 93 | train | ild_db | 3.37 | 7.38 |
| 90 | train | partial_db | 5.51 | 8.85 |
| 90 | dev | partial_db | 4.91 | 8.24 |
| 93 | dev | icc | 0.11 | 0.23 |
| 93 | train | icc | 0.11 | 0.23 |
| 57 | dev | rise_ms | 19.30 | 23.56 |
| 57 | dev | ild_db | 4.31 | 5.95 |
| 99 | dev | ild_db | 0.55 | 2.17 |
| 78 | dev | ild_db | 4.15 | 5.76 |
| 78 | train | ild_db | 4.23 | 5.84 |
| 57 | train | ild_db | 3.94 | 5.54 |
| 90 | dev | icc | 0.22 | 0.28 |
| 90 | train | icc | 0.23 | 0.29 |
| 90 | dev | sustain_db | 9.65 | 10.93 |
| 75 | dev | icc | 0.10 | 0.15 |
| 48 | train | ild_db | 9.74 | 10.97 |
| 57 | train | rise_ms | 16.61 | 18.83 |
| 48 | dev | ild_db | 9.55 | 10.65 |
| 66 | train | ild_db | 5.76 | 6.84 |
| 30 | dev | rise_ms | 15.35 | 17.40 |
| 90 | train | sustain_db | 9.64 | 10.66 |
| 66 | dev | ild_db | 6.00 | 6.99 |
| 81 | dev | level_db | 1.45 | 2.45 |
| 102 | train | icc | 0.31 | 0.35 |
| 102 | dev | early_db | 8.08 | 8.99 |
| 81 | train | level_db | 1.27 | 2.16 |
| 102 | dev | noise_db | 8.21 | 9.09 |
| 102 | train | early_db | 7.89 | 8.76 |
| 84 | dev | noise_db | 7.36 | 8.21 |
| 81 | dev | envelope_db | 2.44 | 3.29 |
| 84 | train | noise_db | 7.45 | 8.29 |
| 102 | train | noise_db | 8.23 | 9.06 |
| 84 | train | early_db | 7.14 | 7.97 |
| 30 | train | rise_ms | 15.25 | 16.90 |
| 90 | train | envelope_db | 7.49 | 8.31 |
| 84 | dev | early_db | 7.27 | 8.06 |
| 81 | train | envelope_db | 2.46 | 3.25 |
| 108 | dev | tuning_cents | 2.00 | 2.78 |
| 90 | dev | envelope_db | 8.20 | 8.93 |
| 81 | train | ild_db | 7.57 | 8.28 |
| 108 | train | tuning_cents | 2.28 | 2.94 |
| 57 | dev | noise_db | 9.94 | 10.59 |
| 57 | train | noise_db | 10.99 | 11.63 |
| 27 | dev | icc | 0.15 | 0.17 |
| 108 | dev | sustain_db | 17.57 | 18.18 |
| 108 | train | level_db | 3.40 | 4.02 |
| 108 | dev | level_db | 3.39 | 4.00 |
| 90 | dev | level_db | 0.40 | 1.01 |
| 54 | train | noise_db | 9.01 | 9.62 |
| 21 | train | partial_db | 10.71 | 11.29 |
| 102 | dev | icc | 0.35 | 0.37 |
| 27 | dev | ild_db | 4.37 | 4.93 |
| 108 | train | ild_db | 1.41 | 1.94 |
| 51 | dev | sustain_db | 5.26 | 5.79 |
| 33 | train | sustain_db | 6.56 | 7.09 |
| 33 | train | early_db | 6.32 | 6.84 |
| 75 | dev | sustain_db | 7.23 | 7.75 |
| 33 | dev | early_db | 6.34 | 6.86 |
| 33 | dev | sustain_db | 6.46 | 6.98 |
| 51 | dev | early_db | 4.69 | 5.20 |
| 108 | dev | ild_db | 1.44 | 1.94 |
| 48 | train | icc | 0.17 | 0.19 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.2795 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 7.4291 | 7.5509 | 0.1218 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.4471 | 2.4696 | 0.0225 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 3.4265 | 3.3717 | -0.0548 | 0 | 0 | 1 |
| dev | attack_db | 156 | 6.2436 | 6.2797 | 0.0362 | 0 | 0 | 0 |
| dev | early_db | 156 | 6.0281 | 6.0558 | 0.0277 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 7.7406 | 7.8593 | 0.1187 | 0 | 0 | 0 |
| dev | noise_db | 153 | 6.9463 | 6.8568 | -0.0895 | 0 | 0 | 3 |
| dev | ild_db | 154 | 4.8142 | 5.2093 | 0.3951 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1778 | 0.1858 | 0.0080 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 3.8766 | 3.8591 | -0.0175 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 12.5652 | 12.0620 | -0.5032 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.7178 | 2.7721 | 0.0542 | 0 | 0 | 0 |
| train | partial_db | 276 | 8.0827 | 8.0681 | -0.0147 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.1407 | 2.0604 | -0.0803 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 4.0654 | 3.9952 | -0.0703 | 0 | 0 | 5 |
| train | attack_db | 276 | 6.5332 | 6.4917 | -0.0415 | 0 | 0 | 0 |
| train | early_db | 276 | 6.4805 | 6.4142 | -0.0663 | 0 | 0 | 0 |
| train | sustain_db | 276 | 8.7338 | 8.7460 | 0.0122 | 0 | 0 | 0 |
| train | noise_db | 272 | 7.0920 | 7.0507 | -0.0413 | 1 | 0 | 3 |
| train | ild_db | 270 | 4.9400 | 5.1345 | 0.1945 | 0 | 0 | 6 |
| train | icc | 270 | 0.2027 | 0.2030 | 0.0003 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.2304 | 4.2250 | -0.0055 | 0 | 0 | 0 |
| train | rise_ms | 276 | 13.7194 | 12.9373 | -0.7820 | 0 | 0 | 0 |
| train | level_db | 276 | 2.4170 | 2.4848 | 0.0678 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 93 | dev | ild_db | 4 | 3.3753 | 7.4324 | 4.0572 |
| 93 | train | ild_db | 12 | 3.3697 | 7.3784 | 4.0087 |
| 90 | train | partial_db | 12 | 5.5054 | 8.8547 | 3.3492 |
| 90 | dev | partial_db | 4 | 4.9109 | 8.2404 | 3.3296 |
| 93 | dev | icc | 4 | 0.1134 | 0.2252 | 0.1119 |
| 93 | train | icc | 12 | 0.1146 | 0.2263 | 0.1117 |
| 57 | dev | rise_ms | 4 | 19.3021 | 23.5625 | 4.2604 |
| 57 | dev | ild_db | 4 | 4.3084 | 5.9454 | 1.6370 |
| 99 | dev | ild_db | 16 | 0.5461 | 2.1687 | 1.6226 |
| 78 | dev | ild_db | 4 | 4.1472 | 5.7572 | 1.6100 |
| 78 | train | ild_db | 12 | 4.2304 | 5.8404 | 1.6100 |
| 57 | train | ild_db | 12 | 3.9382 | 5.5431 | 1.6049 |
| 90 | dev | icc | 4 | 0.2186 | 0.2813 | 0.0627 |
| 90 | train | icc | 12 | 0.2296 | 0.2922 | 0.0626 |
| 90 | dev | sustain_db | 4 | 9.6467 | 10.9345 | 1.2878 |
| 75 | dev | icc | 16 | 0.0961 | 0.1466 | 0.0505 |
| 48 | train | ild_db | 12 | 9.7408 | 10.9729 | 1.2321 |
| 57 | train | rise_ms | 12 | 16.6076 | 18.8333 | 2.2257 |
| 48 | dev | ild_db | 4 | 9.5539 | 10.6544 | 1.1005 |
| 66 | train | ild_db | 12 | 5.7647 | 6.8391 | 1.0744 |
| 30 | dev | rise_ms | 4 | 15.3490 | 17.4010 | 2.0521 |
| 90 | train | sustain_db | 12 | 9.6399 | 10.6608 | 1.0210 |
| 66 | dev | ild_db | 4 | 5.9954 | 6.9902 | 0.9949 |
| 90 | dev | level_db | 4 | 0.4021 | 1.3838 | 0.9817 |
| 102 | train | icc | 12 | 0.3099 | 0.3467 | 0.0368 |
| 102 | dev | early_db | 4 | 8.0766 | 8.9925 | 0.9160 |
| 102 | dev | noise_db | 4 | 8.2137 | 9.0898 | 0.8761 |
| 102 | train | early_db | 12 | 7.8869 | 8.7557 | 0.8688 |
| 84 | dev | noise_db | 4 | 7.3599 | 8.2143 | 0.8544 |
| 81 | dev | envelope_db | 4 | 2.4356 | 3.2879 | 0.8523 |
| 84 | train | noise_db | 12 | 7.4488 | 8.2923 | 0.8435 |
| 102 | train | noise_db | 12 | 8.2315 | 9.0633 | 0.8319 |
| 84 | train | early_db | 12 | 7.1402 | 7.9679 | 0.8278 |
| 30 | train | rise_ms | 12 | 15.2535 | 16.8958 | 1.6424 |
| 90 | train | envelope_db | 12 | 7.4887 | 8.3064 | 0.8177 |
| 84 | dev | early_db | 4 | 7.2701 | 8.0643 | 0.7942 |
| 81 | train | envelope_db | 12 | 2.4643 | 3.2544 | 0.7901 |
| 108 | dev | tuning_cents | 4 | 1.9968 | 2.7835 | 0.7866 |
| 90 | train | level_db | 12 | 1.0027 | 1.7293 | 0.7266 |
| 90 | dev | envelope_db | 4 | 8.2001 | 8.9259 | 0.7258 |
| 81 | train | ild_db | 12 | 7.5655 | 8.2751 | 0.7095 |
| 108 | train | tuning_cents | 12 | 2.2799 | 2.9368 | 0.6569 |
| 57 | dev | noise_db | 4 | 9.9449 | 10.5912 | 0.6463 |
| 57 | train | noise_db | 12 | 10.9878 | 11.6338 | 0.6461 |
| 27 | dev | icc | 16 | 0.1493 | 0.1749 | 0.0256 |
| 108 | dev | sustain_db | 4 | 17.5658 | 18.1798 | 0.6140 |
| 108 | train | level_db | 12 | 3.4038 | 4.0179 | 0.6140 |
| 108 | dev | level_db | 4 | 3.3857 | 3.9978 | 0.6121 |
| 81 | dev | level_db | 4 | 1.4540 | 2.0613 | 0.6073 |
| 54 | train | noise_db | 12 | 9.0135 | 9.6163 | 0.6028 |
| 21 | train | partial_db | 12 | 10.7101 | 11.2925 | 0.5824 |
| 102 | dev | icc | 4 | 0.3461 | 0.3689 | 0.0228 |
| 81 | train | level_db | 12 | 1.2705 | 1.8371 | 0.5665 |
| 27 | dev | ild_db | 16 | 4.3719 | 4.9277 | 0.5558 |
| 108 | train | ild_db | 7 | 1.4114 | 1.9402 | 0.5288 |
| 51 | dev | sustain_db | 16 | 5.2585 | 5.7867 | 0.5282 |
| 33 | train | sustain_db | 12 | 6.5642 | 7.0888 | 0.5246 |
| 33 | train | early_db | 12 | 6.3161 | 6.8390 | 0.5229 |
| 75 | dev | sustain_db | 16 | 7.2281 | 7.7509 | 0.5228 |
| 33 | dev | early_db | 4 | 6.3378 | 6.8575 | 0.5198 |
| 33 | dev | sustain_db | 4 | 6.4572 | 6.9768 | 0.5196 |
| 51 | dev | early_db | 16 | 4.6949 | 5.2006 | 0.5057 |
| 108 | dev | ild_db | 2 | 1.4367 | 1.9408 | 0.5041 |
| 48 | train | icc | 12 | 0.1748 | 0.1948 | 0.0200 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| C3v2 | 48 | train | noise_db | lost | 13.0277 | - |
