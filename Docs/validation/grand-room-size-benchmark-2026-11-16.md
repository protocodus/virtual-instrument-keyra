# Recording benchmark: 2.18.0 against 2.17.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.17.0

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

## 2.18.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 7.89 | 2.23 | 4.00 | 6.61 | 6.54 | 8.69 | 7.37 | 5.02 | 0.20 | 4.23 | 14.25 | 2.48 |
| dev (156) | 7.35 | 2.55 | 3.41 | 6.34 | 6.03 | 7.76 | 7.03 | 5.02 | 0.18 | 3.92 | 12.23 | 2.66 |
| train / bass A0-B2 (84) | 8.76 | 2.94 | 2.67 | 5.73 | 5.41 | 6.35 | 6.52 | 4.36 | 0.20 | 3.52 | 26.52 | 1.96 |
| train / middle C3-B5 (108) | 7.26 | 1.26 | 3.89 | 6.11 | 6.28 | 7.94 | 7.23 | 6.58 | 0.20 | 3.92 | 10.36 | 2.16 |
| train / treble C6-C8 (84) | 7.83 | 2.78 | 5.56 | 8.13 | 8.01 | 12.00 | 8.37 | 3.59 | 0.19 | 5.34 | 6.98 | 3.43 |
| dev / bass A0-B2 (44) | 9.06 | 3.64 | 2.51 | 5.33 | 4.86 | 5.67 | 6.39 | 4.52 | 0.18 | 3.16 | 22.78 | 2.60 |
| dev / middle C3-B5 (68) | 6.95 | 1.20 | 3.54 | 6.21 | 5.89 | 7.21 | 6.92 | 6.77 | 0.15 | 3.70 | 10.12 | 2.18 |
| dev / treble C6-C8 (44) | 6.25 | 3.55 | 4.12 | 7.54 | 7.41 | 10.70 | 7.83 | 2.71 | 0.22 | 5.04 | 4.93 | 3.45 |

## Independent-sample regressions (legacy)

Every note and role where 2.18.0 is worse than 2.17.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.17.0 | 2.18.0 |
|---|---|---|---|---|
| 33 | train | rise_ms | 12.19 | 30.72 |
| 96 | dev | ild_db | 0.96 | 3.66 |
| 96 | train | ild_db | 1.06 | 3.55 |
| 33 | dev | rise_ms | 19.32 | 24.20 |
| 21 | train | rise_ms | 38.63 | 42.67 |
| 102 | dev | noise_db | 9.09 | 10.95 |
| 84 | dev | early_db | 8.06 | 9.88 |
| 84 | train | early_db | 7.97 | 9.77 |
| 84 | train | noise_db | 8.29 | 10.08 |
| 84 | dev | noise_db | 8.21 | 9.99 |
| 102 | train | noise_db | 9.06 | 10.77 |
| 54 | dev | noise_db | 10.02 | 11.67 |
| 90 | dev | rise_ms | 3.98 | 7.28 |
| 54 | dev | ild_db | 5.00 | 6.62 |
| 54 | train | ild_db | 4.99 | 6.59 |
| 57 | dev | noise_db | 10.59 | 12.15 |
| 90 | train | rise_ms | 4.66 | 7.71 |
| 57 | train | noise_db | 11.63 | 13.14 |
| 54 | train | noise_db | 9.62 | 11.06 |
| 105 | train | ild_db | 1.55 | 2.98 |
| 102 | dev | early_db | 8.99 | 10.35 |
| 102 | train | early_db | 8.76 | 10.04 |
| 102 | dev | ild_db | 3.40 | 4.67 |
| 45 | dev | rise_ms | 25.56 | 27.91 |
| 108 | train | tuning_cents | 2.94 | 4.11 |
| 108 | dev | tuning_cents | 2.78 | 3.95 |
| 105 | dev | icc | 0.24 | 0.29 |
| 102 | dev | tuning_cents | 2.87 | 3.97 |
| 102 | train | ild_db | 3.24 | 4.33 |
| 42 | dev | rise_ms | 5.39 | 7.52 |
| 102 | dev | attack_db | 9.34 | 10.40 |
| 93 | dev | partial_db | 4.97 | 6.01 |
| 102 | train | attack_db | 9.22 | 10.24 |
| 81 | dev | tuning_cents | 1.62 | 2.61 |
| 108 | dev | partial_db | 9.16 | 10.15 |
| 90 | dev | noise_db | 5.28 | 6.26 |
| 108 | dev | level_db | 4.00 | 4.88 |
| 108 | train | level_db | 4.02 | 4.90 |
| 96 | dev | tuning_cents | 0.98 | 1.84 |
| 42 | train | ild_db | 5.94 | 6.78 |
| 81 | train | tuning_cents | 1.69 | 2.52 |
| 105 | dev | ild_db | 1.32 | 2.15 |
| 90 | train | noise_db | 5.42 | 6.24 |
| 60 | dev | noise_db | 6.00 | 6.81 |
| 42 | dev | ild_db | 5.85 | 6.66 |
| 96 | train | tuning_cents | 1.01 | 1.81 |
| 102 | train | tuning_cents | 2.96 | 3.75 |
| 81 | train | icc | 0.18 | 0.21 |
| 81 | dev | icc | 0.19 | 0.22 |
| 96 | dev | noise_db | 5.76 | 6.53 |
| 45 | train | rise_ms | 25.86 | 27.39 |
| 108 | dev | early_db | 9.39 | 10.15 |
| 84 | dev | attack_db | 8.18 | 8.92 |
| 96 | train | icc | 0.06 | 0.09 |
| 96 | dev | icc | 0.05 | 0.08 |
| 108 | dev | noise_db | 10.37 | 11.10 |
| 93 | dev | sustain_db | 9.32 | 10.05 |
| 66 | dev | rise_ms | 17.97 | 19.44 |
| 54 | train | rise_ms | 11.80 | 13.26 |
| 60 | train | noise_db | 5.88 | 6.59 |
| 90 | dev | tuning_cents | 3.31 | 4.02 |
| 93 | train | partial_db | 6.30 | 6.99 |
| 81 | train | early_db | 5.69 | 6.38 |
| 66 | train | rise_ms | 17.97 | 19.32 |
| 84 | train | attack_db | 7.88 | 8.55 |
| 99 | dev | noise_db | 6.27 | 6.93 |
| 21 | dev | rise_ms | 32.12 | 33.43 |
| 60 | train | icc | 0.24 | 0.26 |
| 57 | dev | early_db | 8.65 | 9.28 |
| 57 | train | early_db | 8.67 | 9.30 |
| 60 | dev | icc | 0.24 | 0.27 |
| 93 | train | sustain_db | 9.73 | 10.34 |
| 96 | train | noise_db | 6.02 | 6.63 |
| 81 | train | noise_db | 5.47 | 6.05 |
| 54 | dev | attack_db | 4.61 | 5.19 |
| 54 | train | attack_db | 4.63 | 5.21 |
| 108 | train | early_db | 9.39 | 9.95 |
| 90 | dev | decay_db_s | 3.84 | 4.93 |
| 81 | dev | noise_db | 4.80 | 5.34 |
| 57 | train | sustain_db | 9.36 | 9.89 |
| 57 | dev | sustain_db | 9.48 | 10.01 |
| 96 | dev | early_db | 5.25 | 5.78 |
| 108 | train | noise_db | 10.37 | 10.89 |
| 81 | dev | early_db | 5.63 | 6.15 |
| 66 | dev | partial_db | 6.57 | 7.08 |
| 90 | train | tuning_cents | 3.42 | 3.94 |
| 108 | dev | attack_db | 9.88 | 10.40 |
| 57 | train | rise_ms | 18.83 | 19.86 |
| 90 | train | early_db | 4.99 | 5.50 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.6633 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 7.5509 | 7.3454 | -0.2055 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.4696 | 2.5545 | 0.0849 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 3.3717 | 3.4066 | 0.0350 | 0 | 0 | 1 |
| dev | attack_db | 156 | 6.2797 | 6.3377 | 0.0579 | 0 | 0 | 0 |
| dev | early_db | 156 | 6.0558 | 6.0298 | -0.0260 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 7.8593 | 7.7587 | -0.1005 | 0 | 0 | 0 |
| dev | noise_db | 153 | 6.8568 | 7.0337 | 0.1768 | 0 | 0 | 3 |
| dev | ild_db | 154 | 5.2093 | 5.0202 | -0.1891 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1858 | 0.1788 | -0.0070 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 3.8591 | 3.9238 | 0.0647 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 12.0620 | 12.2277 | 0.1657 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.7223 | 2.6447 | -0.0776 | 0 | 0 | 0 |
| train | partial_db | 276 | 8.0681 | 7.8921 | -0.1759 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.0604 | 2.2336 | 0.1732 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 3.9952 | 3.9995 | 0.0043 | 0 | 0 | 5 |
| train | attack_db | 276 | 6.4917 | 6.6071 | 0.1154 | 0 | 0 | 0 |
| train | early_db | 276 | 6.4142 | 6.5431 | 0.1290 | 0 | 0 | 0 |
| train | sustain_db | 276 | 8.7460 | 8.6887 | -0.0573 | 0 | 0 | 0 |
| train | noise_db | 272 | 7.0507 | 7.3506 | 0.3000 | 0 | 1 | 3 |
| train | ild_db | 270 | 5.1345 | 5.0250 | -0.1095 | 0 | 0 | 6 |
| train | icc | 270 | 0.2030 | 0.1962 | -0.0069 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.2250 | 4.2293 | 0.0044 | 0 | 0 | 0 |
| train | rise_ms | 276 | 12.9373 | 14.2489 | 1.3116 | 0 | 0 | 0 |
| train | level_db | 276 | 2.4849 | 2.4963 | 0.0114 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 33 | train | rise_ms | 12 | 12.1910 | 30.7153 | 18.5243 |
| 96 | dev | ild_db | 4 | 0.9632 | 3.6647 | 2.7015 |
| 96 | train | ild_db | 12 | 1.0594 | 3.5549 | 2.4955 |
| 33 | dev | rise_ms | 4 | 19.3229 | 24.2031 | 4.8802 |
| 21 | train | rise_ms | 12 | 38.6302 | 42.6684 | 4.0382 |
| 102 | dev | noise_db | 4 | 9.0898 | 10.9455 | 1.8557 |
| 84 | dev | early_db | 4 | 8.0643 | 9.8816 | 1.8173 |
| 84 | train | early_db | 12 | 7.9679 | 9.7734 | 1.8055 |
| 84 | train | noise_db | 12 | 8.2923 | 10.0845 | 1.7922 |
| 84 | dev | noise_db | 4 | 8.2143 | 9.9880 | 1.7736 |
| 102 | train | noise_db | 12 | 9.0633 | 10.7738 | 1.7105 |
| 54 | dev | noise_db | 4 | 10.0216 | 11.6748 | 1.6532 |
| 90 | dev | rise_ms | 4 | 3.9844 | 7.2812 | 3.2969 |
| 54 | dev | ild_db | 4 | 4.9951 | 6.6224 | 1.6273 |
| 54 | train | ild_db | 12 | 4.9919 | 6.5945 | 1.6025 |
| 57 | dev | noise_db | 4 | 10.5912 | 12.1474 | 1.5562 |
| 90 | train | rise_ms | 12 | 4.6580 | 7.7101 | 3.0521 |
| 57 | train | noise_db | 12 | 11.6338 | 13.1350 | 1.5012 |
| 54 | train | noise_db | 12 | 9.6163 | 11.0595 | 1.4432 |
| 105 | train | ild_db | 11 | 1.5493 | 2.9848 | 1.4355 |
| 102 | dev | early_db | 4 | 8.9925 | 10.3536 | 1.3611 |
| 102 | train | early_db | 12 | 8.7557 | 10.0446 | 1.2889 |
| 102 | dev | ild_db | 4 | 3.3950 | 4.6688 | 1.2738 |
| 45 | dev | rise_ms | 4 | 25.5625 | 27.9062 | 2.3438 |
| 108 | train | tuning_cents | 12 | 2.9368 | 4.1083 | 1.1715 |
| 108 | dev | tuning_cents | 4 | 2.7835 | 3.9469 | 1.1634 |
| 105 | dev | icc | 4 | 0.2402 | 0.2864 | 0.0462 |
| 102 | dev | tuning_cents | 4 | 2.8687 | 3.9719 | 1.1031 |
| 102 | train | ild_db | 12 | 3.2431 | 4.3330 | 1.0898 |
| 42 | dev | rise_ms | 4 | 5.3854 | 7.5208 | 2.1354 |
| 102 | dev | attack_db | 4 | 9.3375 | 10.3964 | 1.0589 |
| 93 | dev | partial_db | 4 | 4.9674 | 6.0148 | 1.0474 |
| 102 | train | attack_db | 12 | 9.2244 | 10.2437 | 1.0193 |
| 81 | dev | tuning_cents | 4 | 1.6185 | 2.6122 | 0.9937 |
| 108 | dev | partial_db | 4 | 9.1600 | 10.1451 | 0.9851 |
| 90 | dev | noise_db | 4 | 5.2786 | 6.2569 | 0.9783 |
| 108 | dev | level_db | 4 | 3.9978 | 4.8842 | 0.8864 |
| 108 | train | level_db | 12 | 4.0179 | 4.8981 | 0.8803 |
| 96 | dev | tuning_cents | 4 | 0.9827 | 1.8367 | 0.8540 |
| 42 | train | ild_db | 12 | 5.9378 | 6.7767 | 0.8389 |
| 81 | train | tuning_cents | 12 | 1.6892 | 2.5228 | 0.8336 |
| 105 | dev | ild_db | 4 | 1.3202 | 2.1516 | 0.8314 |
| 90 | train | noise_db | 12 | 5.4191 | 6.2415 | 0.8224 |
| 60 | dev | noise_db | 4 | 5.9956 | 6.8064 | 0.8107 |
| 42 | dev | ild_db | 4 | 5.8521 | 6.6607 | 0.8086 |
| 96 | train | tuning_cents | 12 | 1.0101 | 1.8102 | 0.8001 |
| 102 | train | tuning_cents | 12 | 2.9574 | 3.7532 | 0.7959 |
| 81 | train | icc | 12 | 0.1801 | 0.2117 | 0.0316 |
| 81 | dev | icc | 4 | 0.1890 | 0.2205 | 0.0315 |
| 96 | dev | noise_db | 4 | 5.7597 | 6.5323 | 0.7726 |
| 45 | train | rise_ms | 12 | 25.8646 | 27.3941 | 1.5295 |
| 108 | dev | early_db | 4 | 9.3948 | 10.1541 | 0.7592 |
| 84 | dev | attack_db | 4 | 8.1764 | 8.9248 | 0.7484 |
| 96 | train | icc | 12 | 0.0589 | 0.0884 | 0.0295 |
| 96 | dev | icc | 4 | 0.0535 | 0.0830 | 0.0294 |
| 108 | dev | noise_db | 4 | 10.3687 | 11.1040 | 0.7353 |
| 93 | dev | sustain_db | 4 | 9.3182 | 10.0523 | 0.7342 |
| 66 | dev | rise_ms | 4 | 17.9740 | 19.4375 | 1.4635 |
| 54 | train | rise_ms | 12 | 11.7969 | 13.2587 | 1.4618 |
| 60 | train | noise_db | 12 | 5.8807 | 6.5915 | 0.7108 |
| 90 | dev | tuning_cents | 4 | 3.3133 | 4.0239 | 0.7106 |
| 93 | train | partial_db | 12 | 6.2977 | 6.9944 | 0.6967 |
| 81 | train | early_db | 12 | 5.6928 | 6.3839 | 0.6910 |
| 66 | train | rise_ms | 12 | 17.9705 | 19.3160 | 1.3455 |
| 84 | train | attack_db | 12 | 7.8812 | 8.5532 | 0.6719 |
| 99 | dev | noise_db | 16 | 6.2701 | 6.9254 | 0.6553 |
| 21 | dev | rise_ms | 4 | 32.1250 | 33.4271 | 1.3021 |
| 60 | train | icc | 12 | 0.2383 | 0.2642 | 0.0259 |
| 57 | dev | early_db | 4 | 8.6459 | 9.2814 | 0.6355 |
| 57 | train | early_db | 12 | 8.6712 | 9.2959 | 0.6247 |
| 60 | dev | icc | 4 | 0.2405 | 0.2653 | 0.0249 |
| 93 | train | sustain_db | 12 | 9.7260 | 10.3420 | 0.6160 |
| 96 | train | noise_db | 12 | 6.0168 | 6.6288 | 0.6120 |
| 81 | train | noise_db | 12 | 5.4701 | 6.0526 | 0.5826 |
| 54 | dev | attack_db | 4 | 4.6062 | 5.1876 | 0.5815 |
| 54 | train | attack_db | 12 | 4.6339 | 5.2122 | 0.5783 |
| 108 | train | early_db | 12 | 9.3866 | 9.9451 | 0.5585 |
| 90 | dev | decay_db_s | 4 | 3.8418 | 4.9316 | 1.0898 |
| 81 | dev | noise_db | 4 | 4.8040 | 5.3434 | 0.5394 |
| 57 | train | sustain_db | 12 | 9.3580 | 9.8920 | 0.5340 |
| 57 | dev | sustain_db | 4 | 9.4801 | 10.0125 | 0.5324 |
| 96 | dev | early_db | 4 | 5.2496 | 5.7762 | 0.5266 |
| 108 | train | noise_db | 12 | 10.3694 | 10.8933 | 0.5239 |
| 81 | dev | early_db | 4 | 5.6287 | 6.1470 | 0.5183 |
| 66 | dev | partial_db | 4 | 6.5655 | 7.0825 | 0.5170 |
| 90 | train | tuning_cents | 12 | 3.4218 | 3.9388 | 0.5169 |
| 108 | dev | attack_db | 4 | 9.8831 | 10.3976 | 0.5145 |
| 57 | train | rise_ms | 12 | 18.8333 | 19.8611 | 1.0278 |
| 90 | train | early_db | 12 | 4.9872 | 5.4988 | 0.5116 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| C3v2 | 48 | train | noise_db | gained | - | 12.1541 |
