# Recording benchmark: 2.10.0 against 2.9.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.9.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.07 | 2.07 | 4.50 | 6.67 | 6.68 | 8.80 | 7.35 | 5.01 | 0.20 | 4.38 | 15.00 | 2.34 |
| dev (156) | 7.74 | 2.21 | 3.80 | 6.26 | 6.29 | 7.85 | 6.78 | 5.31 | 0.19 | 4.18 | 12.65 | 2.07 |
| train / bass A0-B2 (84) | 9.16 | 2.54 | 2.66 | 6.11 | 5.77 | 7.04 | 6.79 | 4.74 | 0.20 | 3.86 | 21.35 | 2.21 |
| train / middle C3-B5 (108) | 7.06 | 1.34 | 4.20 | 6.16 | 6.49 | 7.73 | 7.26 | 7.07 | 0.20 | 4.35 | 16.34 | 2.02 |
| train / treble C6-C8 (84) | 8.27 | 2.55 | 6.87 | 7.86 | 7.82 | 11.94 | 8.03 | 2.46 | 0.18 | 4.94 | 6.92 | 2.88 |
| dev / bass A0-B2 (44) | 9.84 | 3.16 | 2.42 | 6.17 | 5.91 | 6.65 | 6.62 | 5.11 | 0.21 | 3.39 | 22.00 | 2.79 |
| dev / middle C3-B5 (68) | 6.65 | 1.23 | 3.42 | 5.88 | 6.17 | 6.88 | 6.68 | 7.33 | 0.17 | 4.09 | 11.71 | 1.71 |
| dev / treble C6-C8 (44) | 7.34 | 2.77 | 5.80 | 6.94 | 6.86 | 10.54 | 7.10 | 2.25 | 0.20 | 5.12 | 4.76 | 1.91 |

## 2.10.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 7.69 | 2.15 | 3.97 | 6.59 | 6.42 | 8.49 | 7.08 | 5.03 | 0.20 | 4.21 | 13.23 | 2.41 |
| dev (156) | 7.38 | 2.19 | 3.32 | 6.32 | 5.99 | 7.76 | 6.81 | 5.15 | 0.19 | 3.93 | 11.92 | 2.62 |
| train / bass A0-B2 (84) | 8.90 | 2.75 | 2.66 | 6.26 | 5.79 | 6.64 | 6.51 | 4.47 | 0.22 | 3.26 | 23.63 | 2.18 |
| train / middle C3-B5 (108) | 6.46 | 1.36 | 3.81 | 5.79 | 5.86 | 7.10 | 6.79 | 7.29 | 0.20 | 4.16 | 10.20 | 1.78 |
| train / treble C6-C8 (84) | 8.07 | 2.57 | 5.57 | 7.94 | 7.75 | 12.14 | 7.99 | 2.49 | 0.18 | 5.22 | 6.71 | 3.46 |
| dev / bass A0-B2 (44) | 9.71 | 3.20 | 2.42 | 6.01 | 5.29 | 5.98 | 6.44 | 4.72 | 0.23 | 2.78 | 21.99 | 2.84 |
| dev / middle C3-B5 (68) | 6.52 | 1.21 | 3.41 | 5.88 | 5.73 | 6.96 | 6.67 | 7.37 | 0.16 | 4.04 | 10.09 | 1.88 |
| dev / treble C6-C8 (44) | 6.36 | 2.71 | 4.12 | 7.30 | 7.08 | 10.76 | 7.37 | 2.00 | 0.21 | 4.90 | 4.69 | 3.55 |

## Independent-sample regressions (legacy)

Every note and role where 2.10.0 is worse than 2.9.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.9.0 | 2.10.0 |
|---|---|---|---|---|
| 33 | train | rise_ms | 9.05 | 39.28 |
| 21 | dev | rise_ms | 37.83 | 65.82 |
| 33 | dev | rise_ms | 7.26 | 30.04 |
| 21 | train | rise_ms | 36.28 | 58.83 |
| 36 | dev | rise_ms | 11.21 | 21.09 |
| 105 | dev | level_db | 1.23 | 4.86 |
| 36 | train | rise_ms | 12.92 | 19.92 |
| 99 | dev | level_db | 1.19 | 4.48 |
| 57 | dev | rise_ms | 22.45 | 28.72 |
| 105 | train | level_db | 1.69 | 4.39 |
| 102 | dev | envelope_db | 3.93 | 6.61 |
| 75 | dev | rise_ms | 3.51 | 8.61 |
| 96 | dev | level_db | 1.96 | 4.49 |
| 60 | train | rise_ms | 7.16 | 12.22 |
| 60 | dev | rise_ms | 5.61 | 10.45 |
| 96 | train | level_db | 2.51 | 4.82 |
| 45 | dev | rise_ms | 19.70 | 24.21 |
| 105 | dev | envelope_db | 4.78 | 7.01 |
| 78 | dev | level_db | 1.29 | 3.50 |
| 78 | train | level_db | 1.32 | 3.45 |
| 102 | train | envelope_db | 3.06 | 5.18 |
| 78 | dev | ild_db | 6.28 | 8.36 |
| 45 | train | rise_ms | 20.76 | 24.88 |
| 102 | dev | noise_db | 8.11 | 10.16 |
| 78 | train | ild_db | 6.36 | 8.41 |
| 102 | train | noise_db | 8.05 | 10.08 |
| 102 | dev | attack_db | 8.08 | 10.10 |
| 93 | dev | ild_db | 0.78 | 2.79 |
| 60 | dev | ild_db | 8.44 | 10.44 |
| 102 | train | attack_db | 8.01 | 9.98 |
| 93 | train | ild_db | 0.81 | 2.76 |
| 60 | train | ild_db | 8.35 | 10.29 |
| 105 | train | envelope_db | 3.79 | 5.71 |
| 102 | dev | early_db | 8.15 | 10.01 |
| 102 | dev | level_db | 2.37 | 4.11 |
| 57 | train | rise_ms | 24.82 | 28.30 |
| 24 | train | icc | 0.14 | 0.21 |
| 102 | train | level_db | 2.80 | 4.50 |
| 24 | train | rise_ms | 2.88 | 6.27 |
| 102 | train | early_db | 8.04 | 9.74 |
| 24 | dev | icc | 0.14 | 0.21 |
| 102 | dev | sustain_db | 11.55 | 13.16 |
| 84 | train | sustain_db | 11.03 | 12.61 |
| 75 | dev | sustain_db | 5.68 | 7.14 |
| 84 | dev | envelope_db | 3.44 | 4.90 |
| 102 | train | sustain_db | 12.41 | 13.87 |
| 105 | train | sustain_db | 14.13 | 15.56 |
| 36 | dev | early_db | 5.41 | 6.76 |
| 36 | train | early_db | 5.67 | 7.00 |
| 84 | dev | sustain_db | 11.83 | 13.13 |
| 75 | dev | attack_db | 6.25 | 7.49 |
| 42 | dev | ild_db | 3.96 | 5.18 |
| 69 | dev | envelope_db | 4.19 | 5.36 |
| 42 | train | ild_db | 4.05 | 5.23 |
| 69 | train | envelope_db | 4.08 | 5.22 |
| 72 | dev | ild_db | 6.96 | 8.07 |
| 30 | dev | envelope_db | 3.02 | 4.12 |
| 30 | train | envelope_db | 2.88 | 3.97 |
| 72 | train | ild_db | 6.77 | 7.87 |
| 105 | dev | icc | 0.21 | 0.25 |
| 36 | train | icc | 0.26 | 0.30 |
| 42 | dev | noise_db | 8.59 | 9.56 |
| 36 | dev | icc | 0.25 | 0.29 |
| 84 | train | envelope_db | 3.47 | 4.40 |
| 81 | train | envelope_db | 2.18 | 3.10 |
| 75 | dev | level_db | 1.83 | 2.74 |
| 72 | train | envelope_db | 6.69 | 7.59 |
| 54 | train | ild_db | 4.04 | 4.93 |
| 72 | dev | envelope_db | 6.90 | 7.79 |
| 54 | dev | ild_db | 4.03 | 4.91 |
| 48 | dev | noise_db | 6.36 | 7.23 |
| 81 | dev | envelope_db | 2.33 | 3.18 |
| 105 | dev | sustain_db | 12.48 | 13.31 |
| 102 | train | partial_db | 7.95 | 8.76 |
| 99 | dev | attack_db | 5.58 | 6.38 |
| 102 | dev | partial_db | 6.99 | 7.78 |
| 57 | train | sustain_db | 7.07 | 7.86 |
| 69 | dev | ild_db | 5.18 | 5.97 |
| 57 | dev | sustain_db | 7.09 | 7.88 |
| 60 | dev | level_db | 0.85 | 1.61 |
| 48 | train | noise_db | 5.27 | 6.00 |
| 75 | dev | partial_db | 5.71 | 6.43 |
| 99 | dev | noise_db | 5.74 | 6.45 |
| 75 | dev | noise_db | 5.71 | 6.42 |
| 60 | train | level_db | 0.79 | 1.50 |
| 69 | train | ild_db | 5.10 | 5.76 |
| 81 | dev | sustain_db | 5.38 | 6.02 |
| 24 | dev | rise_ms | 2.87 | 4.11 |
| 42 | train | attack_db | 5.88 | 6.49 |
| 105 | dev | early_db | 7.56 | 8.17 |
| 42 | train | early_db | 4.89 | 5.50 |
| 24 | dev | attack_db | 6.50 | 7.08 |
| 99 | dev | early_db | 5.60 | 6.16 |
| 42 | train | noise_db | 9.26 | 9.82 |
| 36 | train | ild_db | 5.34 | 5.90 |
| 57 | dev | partial_db | 7.53 | 8.09 |
| 42 | dev | early_db | 4.36 | 4.92 |
| 84 | train | partial_db | 7.47 | 8.01 |
| 105 | train | icc | 0.21 | 0.23 |
| 36 | dev | partial_db | 9.99 | 10.52 |
| 42 | dev | attack_db | 5.42 | 5.94 |
| 102 | train | decay_db_s | 7.39 | 8.43 |
| 57 | train | partial_db | 7.35 | 7.87 |
| 84 | dev | partial_db | 8.26 | 8.77 |
| 81 | train | sustain_db | 6.09 | 6.59 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.7883 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 7.7435 | 7.3761 | -0.3674 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.2080 | 2.1942 | -0.0138 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 3.7974 | 3.3240 | -0.4734 | 0 | 0 | 1 |
| dev | attack_db | 156 | 6.2611 | 6.3169 | 0.0558 | 0 | 0 | 0 |
| dev | early_db | 156 | 6.2933 | 5.9880 | -0.3053 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 7.8491 | 7.7551 | -0.0940 | 0 | 0 | 0 |
| dev | noise_db | 153 | 6.7823 | 6.8066 | 0.0243 | 0 | 0 | 3 |
| dev | ild_db | 154 | 5.3123 | 5.1461 | -0.1661 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1876 | 0.1940 | 0.0064 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 4.1825 | 3.9286 | -0.2539 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 12.6532 | 11.9223 | -0.7309 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.0748 | 2.5713 | 0.4965 | 0 | 0 | 0 |
| train | partial_db | 276 | 8.0669 | 7.6929 | -0.3739 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.0742 | 2.1504 | 0.0762 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 4.4968 | 3.9658 | -0.5310 | 0 | 0 | 5 |
| train | attack_db | 276 | 6.6653 | 6.5852 | -0.0802 | 0 | 0 | 0 |
| train | early_db | 276 | 6.6752 | 6.4164 | -0.2588 | 0 | 0 | 0 |
| train | sustain_db | 276 | 8.8020 | 8.4927 | -0.3093 | 0 | 0 | 0 |
| train | noise_db | 274 | 7.3506 | 7.0750 | -0.2755 | 0 | 0 | 2 |
| train | ild_db | 270 | 5.0134 | 5.0256 | 0.0122 | 0 | 0 | 6 |
| train | icc | 270 | 0.1973 | 0.2021 | 0.0048 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.3835 | 4.2076 | -0.1759 | 0 | 0 | 0 |
| train | rise_ms | 276 | 14.9971 | 13.2274 | -1.7698 | 0 | 0 | 0 |
| train | level_db | 276 | 2.3395 | 2.6053 | 0.2658 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 33 | train | rise_ms | 12 | 9.0451 | 39.2760 | 30.2309 |
| 21 | dev | rise_ms | 4 | 37.8333 | 65.8229 | 27.9896 |
| 33 | dev | rise_ms | 4 | 7.2552 | 30.0365 | 22.7812 |
| 21 | train | rise_ms | 12 | 36.2830 | 58.8264 | 22.5434 |
| 36 | dev | rise_ms | 4 | 11.2135 | 21.0885 | 9.8750 |
| 105 | dev | level_db | 4 | 1.2315 | 5.8445 | 4.6130 |
| 99 | dev | level_db | 16 | 1.1895 | 5.3376 | 4.1481 |
| 105 | train | level_db | 12 | 1.6947 | 5.3715 | 3.6768 |
| 96 | dev | level_db | 4 | 1.9562 | 5.4705 | 3.5143 |
| 36 | train | rise_ms | 12 | 12.9184 | 19.9184 | 7.0000 |
| 57 | dev | rise_ms | 4 | 22.4479 | 28.7188 | 6.2708 |
| 96 | train | level_db | 12 | 2.5059 | 5.6370 | 3.1310 |
| 102 | dev | envelope_db | 4 | 3.9294 | 6.6110 | 2.6816 |
| 75 | dev | rise_ms | 16 | 3.5052 | 8.6107 | 5.1055 |
| 60 | train | rise_ms | 12 | 7.1632 | 12.2188 | 5.0556 |
| 60 | dev | rise_ms | 4 | 5.6146 | 10.4531 | 4.8385 |
| 102 | train | level_db | 12 | 2.8033 | 5.1572 | 2.3539 |
| 45 | dev | rise_ms | 4 | 19.7031 | 24.2135 | 4.5104 |
| 102 | dev | level_db | 4 | 2.3721 | 4.6023 | 2.2302 |
| 105 | dev | envelope_db | 4 | 4.7832 | 7.0062 | 2.2230 |
| 102 | train | envelope_db | 12 | 3.0559 | 5.1843 | 2.1284 |
| 78 | dev | ild_db | 4 | 6.2781 | 8.3556 | 2.0774 |
| 45 | train | rise_ms | 12 | 20.7604 | 24.8767 | 4.1163 |
| 102 | dev | noise_db | 4 | 8.1124 | 10.1629 | 2.0505 |
| 78 | train | ild_db | 12 | 6.3649 | 8.4052 | 2.0403 |
| 102 | train | noise_db | 12 | 8.0523 | 10.0787 | 2.0264 |
| 102 | dev | attack_db | 4 | 8.0784 | 10.1014 | 2.0230 |
| 93 | dev | ild_db | 4 | 0.7801 | 2.7936 | 2.0135 |
| 60 | dev | ild_db | 4 | 8.4426 | 10.4366 | 1.9940 |
| 102 | train | attack_db | 12 | 8.0084 | 9.9760 | 1.9676 |
| 93 | train | ild_db | 12 | 0.8077 | 2.7650 | 1.9573 |
| 60 | train | ild_db | 12 | 8.3470 | 10.2875 | 1.9405 |
| 105 | train | envelope_db | 12 | 3.7890 | 5.7061 | 1.9170 |
| 102 | dev | early_db | 4 | 8.1505 | 10.0138 | 1.8634 |
| 57 | train | rise_ms | 12 | 24.8247 | 28.2969 | 3.4722 |
| 24 | train | icc | 12 | 0.1417 | 0.2109 | 0.0692 |
| 24 | train | rise_ms | 12 | 2.8802 | 6.2743 | 3.3941 |
| 102 | train | early_db | 12 | 8.0406 | 9.7367 | 1.6961 |
| 24 | dev | icc | 4 | 0.1420 | 0.2084 | 0.0664 |
| 102 | dev | sustain_db | 4 | 11.5473 | 13.1579 | 1.6105 |
| 84 | train | sustain_db | 12 | 11.0255 | 12.6074 | 1.5819 |
| 75 | dev | sustain_db | 16 | 5.6793 | 7.1425 | 1.4632 |
| 84 | dev | envelope_db | 4 | 3.4375 | 4.9004 | 1.4629 |
| 102 | train | sustain_db | 12 | 12.4091 | 13.8719 | 1.4628 |
| 105 | train | sustain_db | 12 | 14.1272 | 15.5617 | 1.4345 |
| 36 | dev | early_db | 4 | 5.4103 | 6.7636 | 1.3534 |
| 36 | train | early_db | 12 | 5.6663 | 7.0050 | 1.3387 |
| 84 | dev | sustain_db | 4 | 11.8265 | 13.1254 | 1.2989 |
| 75 | dev | attack_db | 16 | 6.2472 | 7.4900 | 1.2427 |
| 78 | dev | level_db | 4 | 1.2886 | 2.5136 | 1.2250 |
| 42 | dev | ild_db | 4 | 3.9571 | 5.1807 | 1.2237 |
| 69 | dev | envelope_db | 4 | 4.1856 | 5.3635 | 1.1779 |
| 42 | train | ild_db | 12 | 4.0539 | 5.2250 | 1.1711 |
| 78 | train | level_db | 12 | 1.3230 | 2.4694 | 1.1465 |
| 69 | train | envelope_db | 12 | 4.0798 | 5.2250 | 1.1452 |
| 72 | dev | ild_db | 4 | 6.9626 | 8.0678 | 1.1052 |
| 30 | dev | envelope_db | 4 | 3.0201 | 4.1212 | 1.1011 |
| 30 | train | envelope_db | 12 | 2.8758 | 3.9719 | 1.0961 |
| 72 | train | ild_db | 12 | 6.7750 | 7.8697 | 1.0947 |
| 36 | dev | level_db | 4 | 0.4627 | 1.5224 | 1.0596 |
| 36 | train | level_db | 12 | 0.9603 | 1.9867 | 1.0264 |
| 105 | dev | icc | 4 | 0.2100 | 0.2501 | 0.0401 |
| 36 | train | icc | 12 | 0.2581 | 0.2979 | 0.0398 |
| 42 | dev | noise_db | 4 | 8.5920 | 9.5552 | 0.9633 |
| 36 | dev | icc | 4 | 0.2488 | 0.2863 | 0.0375 |
| 84 | train | envelope_db | 12 | 3.4674 | 4.4004 | 0.9329 |
| 81 | train | envelope_db | 12 | 2.1825 | 3.1031 | 0.9206 |
| 72 | train | envelope_db | 12 | 6.6896 | 7.5883 | 0.8987 |
| 54 | train | ild_db | 12 | 4.0356 | 4.9264 | 0.8908 |
| 72 | dev | envelope_db | 4 | 6.9038 | 7.7896 | 0.8858 |
| 54 | dev | ild_db | 4 | 4.0251 | 4.9093 | 0.8842 |
| 48 | dev | noise_db | 4 | 6.3624 | 7.2282 | 0.8658 |
| 81 | dev | envelope_db | 4 | 2.3293 | 3.1798 | 0.8505 |
| 105 | dev | sustain_db | 4 | 12.4828 | 13.3131 | 0.8303 |
| 102 | train | partial_db | 12 | 7.9539 | 8.7563 | 0.8024 |
| 99 | dev | attack_db | 16 | 5.5828 | 6.3844 | 0.8016 |
| 45 | dev | level_db | 4 | 0.7770 | 1.5716 | 0.7946 |
| 102 | dev | partial_db | 4 | 6.9857 | 7.7781 | 0.7925 |
| 57 | train | sustain_db | 12 | 7.0671 | 7.8563 | 0.7893 |
| 69 | dev | ild_db | 4 | 5.1839 | 5.9726 | 0.7887 |
| 57 | dev | sustain_db | 4 | 7.0942 | 7.8823 | 0.7881 |
| 45 | train | level_db | 12 | 1.0558 | 1.7996 | 0.7438 |
| 48 | train | noise_db | 11 | 5.2664 | 6.0006 | 0.7341 |
| 75 | dev | partial_db | 16 | 5.7085 | 6.4329 | 0.7244 |
| 99 | dev | noise_db | 16 | 5.7350 | 6.4539 | 0.7189 |
| 75 | dev | noise_db | 16 | 5.7118 | 6.4223 | 0.7104 |
| 69 | train | ild_db | 12 | 5.0980 | 5.7563 | 0.6583 |
| 48 | train | level_db | 12 | 1.6602 | 2.3012 | 0.6410 |
| 81 | dev | sustain_db | 4 | 5.3819 | 6.0221 | 0.6402 |
| 48 | dev | level_db | 4 | 1.6715 | 2.3024 | 0.6309 |
| 24 | dev | rise_ms | 4 | 2.8698 | 4.1094 | 1.2396 |
| 42 | train | attack_db | 12 | 5.8831 | 6.4927 | 0.6096 |
| 105 | dev | early_db | 4 | 7.5613 | 8.1671 | 0.6058 |
| 42 | train | early_db | 12 | 4.8922 | 5.4954 | 0.6031 |
| 24 | dev | attack_db | 4 | 6.5014 | 7.0750 | 0.5736 |
| 99 | dev | early_db | 16 | 5.5989 | 6.1631 | 0.5643 |
| 42 | train | noise_db | 12 | 9.2611 | 9.8231 | 0.5621 |
| 36 | train | ild_db | 12 | 5.3409 | 5.9003 | 0.5594 |
| 57 | dev | partial_db | 4 | 7.5327 | 8.0906 | 0.5579 |
| 42 | dev | early_db | 4 | 4.3589 | 4.9168 | 0.5578 |
| 84 | train | partial_db | 12 | 7.4662 | 8.0147 | 0.5485 |
| 105 | train | icc | 11 | 0.2120 | 0.2336 | 0.0216 |
| 36 | dev | partial_db | 4 | 9.9884 | 10.5217 | 0.5333 |
| 42 | dev | attack_db | 4 | 5.4170 | 5.9425 | 0.5255 |
| 102 | train | decay_db_s | 12 | 7.3939 | 8.4258 | 1.0320 |
| 57 | train | partial_db | 12 | 7.3524 | 7.8672 | 0.5148 |
| 84 | dev | partial_db | 4 | 8.2632 | 8.7675 | 0.5043 |
| 81 | train | sustain_db | 12 | 6.0864 | 6.5873 | 0.5010 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
