# Recording benchmark: 2.4.0 against 2.3.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.3.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.98 | 2.72 | 4.72 | 8.13 | 8.71 | 9.66 | 9.63 | 5.47 | 0.22 | 4.23 | 17.27 | 2.65 |
| dev (156) | 8.23 | 2.81 | 3.67 | 7.82 | 8.08 | 8.73 | 9.30 | 5.60 | 0.22 | 4.18 | 15.06 | 2.52 |
| train / bass A0-B2 (84) | 8.74 | 3.08 | 2.67 | 5.66 | 5.57 | 7.05 | 8.02 | 4.68 | 0.19 | 3.94 | 25.71 | 2.27 |
| train / middle C3-B5 (108) | 7.91 | 2.32 | 3.93 | 7.16 | 7.44 | 8.57 | 7.84 | 7.46 | 0.21 | 4.53 | 20.75 | 2.19 |
| train / treble C6-C8 (84) | 10.59 | 2.87 | 7.98 | 11.85 | 13.49 | 13.67 | 13.38 | 3.57 | 0.24 | 4.14 | 4.36 | 3.63 |
| dev / bass A0-B2 (44) | 8.59 | 3.57 | 2.45 | 5.86 | 5.85 | 6.69 | 8.01 | 4.87 | 0.22 | 3.47 | 28.12 | 2.89 |
| dev / middle C3-B5 (68) | 7.52 | 2.00 | 3.41 | 6.77 | 6.57 | 7.68 | 7.61 | 7.77 | 0.17 | 4.35 | 14.15 | 1.84 |
| dev / treble C6-C8 (44) | 8.96 | 3.30 | 5.33 | 11.39 | 12.65 | 12.40 | 13.10 | 2.84 | 0.30 | 4.62 | 3.41 | 3.21 |

## 2.4.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.62 | 2.81 | 4.84 | 7.08 | 7.70 | 9.24 | 8.42 | 5.56 | 0.21 | 4.40 | 15.17 | 2.65 |
| dev (156) | 8.23 | 3.20 | 4.15 | 6.60 | 6.96 | 8.39 | 7.83 | 5.66 | 0.20 | 4.55 | 12.98 | 2.42 |
| train / bass A0-B2 (84) | 9.79 | 3.38 | 2.74 | 6.01 | 5.62 | 7.03 | 8.02 | 4.67 | 0.19 | 4.00 | 21.81 | 2.42 |
| train / middle C3-B5 (108) | 8.21 | 2.41 | 4.02 | 6.57 | 7.04 | 8.69 | 7.46 | 7.37 | 0.22 | 4.56 | 17.63 | 2.12 |
| train / treble C6-C8 (84) | 7.99 | 2.78 | 8.18 | 8.81 | 10.63 | 12.16 | 10.05 | 4.00 | 0.21 | 4.59 | 5.38 | 3.55 |
| dev / bass A0-B2 (44) | 9.66 | 4.05 | 2.45 | 6.07 | 5.79 | 6.62 | 8.09 | 4.96 | 0.21 | 3.46 | 22.80 | 3.11 |
| dev / middle C3-B5 (68) | 7.78 | 2.35 | 3.42 | 6.16 | 6.04 | 7.81 | 6.90 | 7.77 | 0.17 | 4.37 | 12.55 | 1.79 |
| dev / treble C6-C8 (44) | 7.51 | 3.66 | 7.04 | 7.81 | 9.55 | 11.07 | 8.95 | 2.97 | 0.24 | 5.93 | 3.83 | 2.70 |

## Independent-sample regressions (legacy)

Every note and role where 2.4.0 is worse than 2.3.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.3.0 | 2.4.0 |
|---|---|---|---|---|
| 54 | train | rise_ms | 41.02 | 50.87 |
| 54 | dev | rise_ms | 40.43 | 49.68 |
| 108 | dev | decay_db_s | 7.84 | 15.45 |
| 108 | dev | sustain_db | 18.80 | 22.36 |
| 108 | train | decay_db_s | 5.44 | 11.98 |
| 57 | dev | noise_db | 7.44 | 10.65 |
| 96 | dev | envelope_db | 3.79 | 6.98 |
| 105 | dev | sustain_db | 11.02 | 14.12 |
| 33 | train | rise_ms | 8.28 | 14.23 |
| 57 | train | noise_db | 8.77 | 11.68 |
| 96 | train | envelope_db | 3.85 | 6.61 |
| 57 | train | rise_ms | 26.87 | 32.26 |
| 99 | dev | envelope_db | 5.23 | 7.76 |
| 72 | train | icc | 0.18 | 0.28 |
| 72 | dev | icc | 0.17 | 0.26 |
| 105 | train | decay_db_s | 10.90 | 15.31 |
| 108 | train | sustain_db | 20.11 | 21.95 |
| 33 | train | partial_db | 8.92 | 10.63 |
| 81 | dev | partial_db | 3.94 | 5.61 |
| 105 | train | sustain_db | 12.72 | 14.35 |
| 30 | dev | noise_db | 6.58 | 8.17 |
| 42 | dev | partial_db | 6.81 | 8.39 |
| 48 | dev | tuning_cents | 3.71 | 5.29 |
| 33 | dev | partial_db | 8.67 | 10.22 |
| 30 | train | noise_db | 6.28 | 7.80 |
| 60 | dev | noise_db | 4.68 | 6.19 |
| 105 | dev | decay_db_s | 9.18 | 12.19 |
| 57 | dev | rise_ms | 26.78 | 29.77 |
| 54 | dev | noise_db | 8.49 | 9.96 |
| 108 | train | level_db | 4.31 | 5.72 |
| 42 | train | partial_db | 7.11 | 8.51 |
| 30 | train | partial_db | 7.91 | 9.22 |
| 57 | dev | attack_db | 6.77 | 8.03 |
| 54 | train | noise_db | 8.27 | 9.48 |
| 27 | dev | partial_db | 8.54 | 9.74 |
| 99 | dev | decay_db_s | 2.93 | 5.30 |
| 48 | train | tuning_cents | 3.81 | 4.97 |
| 33 | dev | rise_ms | 12.34 | 14.67 |
| 57 | train | attack_db | 6.71 | 7.87 |
| 51 | dev | tuning_cents | 2.07 | 3.21 |
| 108 | dev | level_db | 4.41 | 5.56 |
| 81 | dev | ild_db | 10.23 | 11.37 |
| 60 | train | noise_db | 4.71 | 5.85 |
| 90 | dev | envelope_db | 4.64 | 5.73 |
| 30 | dev | partial_db | 7.41 | 8.48 |
| 81 | train | ild_db | 9.71 | 10.77 |
| 48 | train | partial_db | 7.53 | 8.58 |
| 78 | dev | partial_db | 11.69 | 12.72 |
| 21 | train | partial_db | 10.93 | 11.95 |
| 99 | dev | tuning_cents | 4.24 | 5.25 |
| 48 | dev | partial_db | 7.83 | 8.79 |
| 21 | dev | partial_db | 10.91 | 11.86 |
| 36 | train | rise_ms | 6.74 | 8.63 |
| 24 | train | attack_db | 6.27 | 7.20 |
| 105 | dev | envelope_db | 4.60 | 5.53 |
| 78 | train | partial_db | 11.12 | 12.02 |
| 96 | train | rise_ms | 5.42 | 7.19 |
| 105 | train | envelope_db | 3.55 | 4.43 |
| 30 | dev | envelope_db | 2.21 | 3.08 |
| 21 | train | tuning_cents | 4.68 | 5.55 |
| 84 | train | rise_ms | 8.33 | 10.04 |
| 96 | dev | decay_db_s | 9.32 | 11.00 |
| 84 | dev | noise_db | 13.81 | 14.63 |
| 27 | dev | tuning_cents | 4.13 | 4.94 |
| 84 | dev | level_db | 4.27 | 5.05 |
| 21 | dev | tuning_cents | 4.69 | 5.47 |
| 96 | dev | rise_ms | 5.30 | 6.83 |
| 30 | train | envelope_db | 2.09 | 2.86 |
| 81 | dev | sustain_db | 5.62 | 6.38 |
| 24 | dev | partial_db | 10.05 | 10.80 |
| 57 | dev | early_db | 7.26 | 8.01 |
| 57 | train | early_db | 7.21 | 7.94 |
| 90 | train | rise_ms | 2.19 | 3.64 |
| 60 | dev | partial_db | 7.04 | 7.75 |
| 66 | dev | icc | 0.11 | 0.14 |
| 45 | train | partial_db | 7.95 | 8.65 |
| 90 | train | envelope_db | 4.52 | 5.22 |
| 66 | train | icc | 0.11 | 0.14 |
| 96 | dev | tuning_cents | 2.33 | 3.01 |
| 96 | dev | ild_db | 1.93 | 2.61 |
| 96 | train | ild_db | 1.82 | 2.50 |
| 90 | dev | rise_ms | 2.01 | 3.35 |
| 105 | train | ild_db | 2.83 | 3.49 |
| 84 | dev | partial_db | 8.63 | 9.29 |
| 78 | train | sustain_db | 13.15 | 13.80 |
| 78 | dev | sustain_db | 13.74 | 14.39 |
| 36 | train | partial_db | 8.58 | 9.20 |
| 36 | dev | rise_ms | 6.85 | 8.07 |
| 60 | train | partial_db | 6.88 | 7.46 |
| 81 | train | level_db | 4.25 | 4.84 |
| 24 | train | partial_db | 9.76 | 10.35 |
| 84 | train | noise_db | 14.04 | 14.62 |
| 93 | dev | ild_db | 7.76 | 8.33 |
| 81 | train | sustain_db | 6.30 | 6.88 |
| 93 | train | ild_db | 7.78 | 8.35 |
| 24 | dev | attack_db | 6.06 | 6.62 |
| 36 | train | tuning_cents | 2.13 | 2.68 |
| 93 | train | rise_ms | 4.72 | 5.81 |
| 108 | dev | ild_db | 0.68 | 1.21 |
| 45 | dev | partial_db | 8.02 | 8.56 |
| 36 | dev | tuning_cents | 2.21 | 2.72 |
| 36 | dev | partial_db | 8.43 | 8.94 |
| 21 | train | attack_db | 4.75 | 5.25 |
| 84 | dev | rise_ms | 9.42 | 10.44 |
| 81 | dev | level_db | 4.67 | 5.17 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.9145 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 8.2264 | 8.2338 | 0.0074 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.8070 | 3.2020 | 0.3949 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 3.6677 | 4.1497 | 0.4820 | 0 | 0 | 1 |
| dev | attack_db | 156 | 7.8155 | 6.6026 | -1.2128 | 0 | 0 | 0 |
| dev | early_db | 156 | 8.0816 | 6.9629 | -1.1187 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 8.7317 | 8.3936 | -0.3380 | 0 | 0 | 0 |
| dev | noise_db | 153 | 9.3001 | 7.8250 | -1.4751 | 0 | 0 | 3 |
| dev | ild_db | 154 | 5.5962 | 5.6568 | 0.0606 | 0 | 0 | 2 |
| dev | icc | 154 | 0.2184 | 0.2032 | -0.0153 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 4.1785 | 4.5528 | 0.3743 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 15.0634 | 12.9833 | -2.0801 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.5237 | 2.3892 | -0.1344 | 0 | 0 | 0 |
| train | partial_db | 276 | 8.9780 | 8.6230 | -0.3549 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.7218 | 2.8141 | 0.0923 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 4.7181 | 4.8364 | 0.1183 | 0 | 0 | 5 |
| train | attack_db | 276 | 8.1316 | 7.0817 | -1.0499 | 0 | 0 | 0 |
| train | early_db | 276 | 8.7105 | 7.6993 | -1.0111 | 0 | 0 | 0 |
| train | sustain_db | 276 | 9.6605 | 9.2427 | -0.4178 | 0 | 0 | 0 |
| train | noise_db | 268 | 9.6292 | 8.3967 | -1.2326 | 0 | 6 | 2 |
| train | ild_db | 270 | 5.4717 | 5.5583 | 0.0866 | 0 | 0 | 6 |
| train | icc | 270 | 0.2164 | 0.2108 | -0.0057 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.2315 | 4.3987 | 0.1672 | 0 | 0 | 0 |
| train | rise_ms | 276 | 17.2686 | 15.1738 | -2.0948 | 0 | 0 | 0 |
| train | level_db | 276 | 2.6518 | 2.6788 | 0.0269 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 54 | train | rise_ms | 12 | 41.0174 | 50.8663 | 9.8490 |
| 54 | dev | rise_ms | 4 | 40.4323 | 49.6771 | 9.2448 |
| 108 | dev | decay_db_s | 3 | 7.8420 | 15.4473 | 7.6053 |
| 108 | dev | sustain_db | 4 | 18.7969 | 22.3585 | 3.5615 |
| 108 | train | decay_db_s | 8 | 5.4429 | 11.9795 | 6.5366 |
| 57 | dev | noise_db | 4 | 7.4378 | 10.6491 | 3.2113 |
| 96 | dev | envelope_db | 4 | 3.7862 | 6.9754 | 3.1891 |
| 105 | dev | sustain_db | 4 | 11.0244 | 14.1154 | 3.0909 |
| 33 | train | rise_ms | 12 | 8.2812 | 14.2309 | 5.9497 |
| 57 | train | noise_db | 12 | 8.7712 | 11.6754 | 2.9042 |
| 96 | train | envelope_db | 12 | 3.8500 | 6.6083 | 2.7583 |
| 57 | train | rise_ms | 12 | 26.8733 | 32.2622 | 5.3889 |
| 99 | dev | envelope_db | 16 | 5.2314 | 7.7634 | 2.5320 |
| 72 | train | icc | 12 | 0.1783 | 0.2768 | 0.0986 |
| 72 | dev | icc | 4 | 0.1670 | 0.2631 | 0.0961 |
| 105 | train | decay_db_s | 11 | 10.8962 | 15.3052 | 4.4090 |
| 108 | train | sustain_db | 12 | 20.1094 | 21.9451 | 1.8358 |
| 33 | train | partial_db | 12 | 8.9186 | 10.6333 | 1.7146 |
| 81 | dev | partial_db | 4 | 3.9371 | 5.6061 | 1.6690 |
| 105 | train | sustain_db | 12 | 12.7246 | 14.3493 | 1.6248 |
| 30 | dev | noise_db | 4 | 6.5838 | 8.1686 | 1.5849 |
| 42 | dev | partial_db | 4 | 6.8077 | 8.3885 | 1.5807 |
| 48 | dev | tuning_cents | 4 | 3.7149 | 5.2888 | 1.5739 |
| 33 | dev | partial_db | 4 | 8.6697 | 10.2222 | 1.5525 |
| 60 | dev | noise_db | 4 | 4.6757 | 6.1941 | 1.5183 |
| 105 | dev | decay_db_s | 4 | 9.1755 | 12.1856 | 3.0101 |
| 57 | dev | rise_ms | 4 | 26.7760 | 29.7656 | 2.9896 |
| 54 | dev | noise_db | 4 | 8.4948 | 9.9566 | 1.4618 |
| 108 | train | level_db | 12 | 4.3053 | 5.7217 | 1.4164 |
| 42 | train | partial_db | 12 | 7.1086 | 8.5060 | 1.3974 |
| 30 | train | partial_db | 12 | 7.9089 | 9.2165 | 1.3075 |
| 57 | dev | attack_db | 4 | 6.7723 | 8.0344 | 1.2621 |
| 54 | train | noise_db | 12 | 8.2712 | 9.4817 | 1.2105 |
| 27 | dev | partial_db | 16 | 8.5434 | 9.7410 | 1.1976 |
| 99 | dev | decay_db_s | 16 | 2.9275 | 5.3044 | 2.3769 |
| 48 | train | tuning_cents | 12 | 3.8057 | 4.9717 | 1.1660 |
| 33 | dev | rise_ms | 4 | 12.3385 | 14.6667 | 2.3281 |
| 57 | train | attack_db | 12 | 6.7052 | 7.8677 | 1.1624 |
| 51 | dev | tuning_cents | 16 | 2.0678 | 3.2143 | 1.1465 |
| 108 | dev | level_db | 4 | 4.4132 | 5.5584 | 1.1452 |
| 81 | dev | ild_db | 4 | 10.2255 | 11.3696 | 1.1440 |
| 60 | train | noise_db | 12 | 4.7140 | 5.8485 | 1.1345 |
| 84 | dev | level_db | 4 | 4.2699 | 5.3692 | 1.0993 |
| 90 | dev | envelope_db | 4 | 4.6420 | 5.7259 | 1.0839 |
| 30 | dev | partial_db | 4 | 7.4082 | 8.4786 | 1.0704 |
| 81 | train | ild_db | 12 | 9.7117 | 10.7660 | 1.0542 |
| 48 | train | partial_db | 12 | 7.5325 | 8.5813 | 1.0487 |
| 78 | dev | partial_db | 4 | 11.6906 | 12.7190 | 1.0284 |
| 21 | train | partial_db | 12 | 10.9277 | 11.9508 | 1.0231 |
| 99 | dev | tuning_cents | 16 | 4.2438 | 5.2546 | 1.0108 |
| 48 | dev | partial_db | 4 | 7.8295 | 8.7946 | 0.9651 |
| 21 | dev | partial_db | 4 | 10.9051 | 11.8574 | 0.9524 |
| 36 | train | rise_ms | 12 | 6.7413 | 8.6319 | 1.8906 |
| 24 | train | attack_db | 12 | 6.2652 | 7.2020 | 0.9368 |
| 105 | dev | envelope_db | 4 | 4.5978 | 5.5255 | 0.9277 |
| 81 | train | level_db | 12 | 4.2506 | 5.1559 | 0.9053 |
| 78 | train | partial_db | 12 | 11.1247 | 12.0176 | 0.8929 |
| 96 | train | rise_ms | 12 | 5.4219 | 7.1944 | 1.7726 |
| 105 | train | envelope_db | 12 | 3.5514 | 4.4325 | 0.8811 |
| 30 | dev | envelope_db | 4 | 2.2087 | 3.0836 | 0.8749 |
| 21 | train | tuning_cents | 12 | 4.6804 | 5.5539 | 0.8735 |
| 84 | train | rise_ms | 12 | 8.3299 | 10.0365 | 1.7066 |
| 96 | dev | decay_db_s | 4 | 9.3155 | 11.0025 | 1.6870 |
| 81 | dev | level_db | 4 | 4.6697 | 5.4927 | 0.8230 |
| 84 | dev | noise_db | 4 | 13.8097 | 14.6268 | 0.8170 |
| 27 | dev | tuning_cents | 16 | 4.1283 | 4.9416 | 0.8133 |
| 21 | dev | tuning_cents | 4 | 4.6913 | 5.4652 | 0.7739 |
| 96 | dev | rise_ms | 4 | 5.2969 | 6.8333 | 1.5365 |
| 30 | train | envelope_db | 12 | 2.0901 | 2.8583 | 0.7682 |
| 81 | dev | sustain_db | 4 | 5.6195 | 6.3757 | 0.7563 |
| 24 | dev | partial_db | 4 | 10.0493 | 10.8011 | 0.7518 |
| 84 | train | level_db | 12 | 4.9039 | 5.6555 | 0.7516 |
| 30 | train | noise_db | 11 | 6.2766 | 7.0266 | 0.7500 |
| 57 | dev | early_db | 4 | 7.2604 | 8.0059 | 0.7455 |
| 57 | train | early_db | 12 | 7.2082 | 7.9360 | 0.7278 |
| 90 | train | rise_ms | 12 | 2.1944 | 3.6424 | 1.4479 |
| 60 | dev | partial_db | 4 | 7.0443 | 7.7535 | 0.7092 |
| 66 | dev | icc | 4 | 0.1100 | 0.1382 | 0.0283 |
| 45 | train | partial_db | 12 | 7.9452 | 8.6503 | 0.7051 |
| 90 | train | envelope_db | 12 | 4.5190 | 5.2152 | 0.6961 |
| 66 | train | icc | 12 | 0.1094 | 0.1370 | 0.0276 |
| 96 | dev | tuning_cents | 4 | 2.3286 | 3.0130 | 0.6844 |
| 96 | dev | ild_db | 4 | 1.9294 | 2.6091 | 0.6797 |
| 96 | train | ild_db | 12 | 1.8239 | 2.4989 | 0.6750 |
| 90 | dev | rise_ms | 4 | 2.0104 | 3.3490 | 1.3385 |
| 105 | train | ild_db | 11 | 2.8267 | 3.4917 | 0.6651 |
| 84 | dev | partial_db | 4 | 8.6306 | 9.2901 | 0.6596 |
| 78 | train | sustain_db | 12 | 13.1526 | 13.8025 | 0.6500 |
| 78 | dev | sustain_db | 4 | 13.7391 | 14.3890 | 0.6499 |
| 36 | train | partial_db | 12 | 8.5808 | 9.1968 | 0.6160 |
| 36 | dev | rise_ms | 4 | 6.8542 | 8.0729 | 1.2188 |
| 60 | train | partial_db | 12 | 6.8788 | 7.4647 | 0.5859 |
| 24 | train | partial_db | 12 | 9.7627 | 10.3459 | 0.5832 |
| 84 | train | noise_db | 12 | 14.0373 | 14.6169 | 0.5796 |
| 93 | dev | ild_db | 4 | 7.7589 | 8.3339 | 0.5750 |
| 81 | train | sustain_db | 12 | 6.3048 | 6.8751 | 0.5704 |
| 93 | train | ild_db | 12 | 7.7815 | 8.3514 | 0.5699 |
| 24 | dev | attack_db | 4 | 6.0586 | 6.6229 | 0.5643 |
| 36 | train | tuning_cents | 12 | 2.1273 | 2.6781 | 0.5508 |
| 93 | train | rise_ms | 12 | 4.7170 | 5.8108 | 1.0938 |
| 108 | dev | ild_db | 2 | 0.6765 | 1.2113 | 0.5348 |
| 45 | dev | partial_db | 4 | 8.0226 | 8.5570 | 0.5344 |
| 36 | dev | tuning_cents | 4 | 2.2107 | 2.7213 | 0.5106 |
| 36 | dev | partial_db | 4 | 8.4295 | 8.9382 | 0.5087 |
| 21 | train | attack_db | 12 | 4.7455 | 5.2539 | 0.5084 |
| 84 | dev | rise_ms | 4 | 9.4219 | 10.4375 | 1.0156 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| A1v1 | 33 | train | noise_db | gained | - | 11.8816 |
| C2v1 | 36 | train | noise_db | gained | - | 8.1647 |
| C2v2 | 36 | train | noise_db | gained | - | 7.1760 |
| F#1v1 | 30 | train | noise_db | gained | - | 16.3140 |
| F#2v1 | 42 | train | noise_db | gained | - | 8.4473 |
| F#2v2 | 42 | train | noise_db | gained | - | 5.9653 |
