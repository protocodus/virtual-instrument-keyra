# Recording benchmark: 2.7.0 against 2.6.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.6.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.03 | 2.00 | 5.02 | 6.85 | 7.14 | 9.11 | 7.69 | 5.45 | 0.20 | 4.40 | 14.32 | 2.68 |
| dev (156) | 7.90 | 2.10 | 4.16 | 6.39 | 6.49 | 8.33 | 7.00 | 5.67 | 0.20 | 4.54 | 12.16 | 2.49 |
| train / bass A0-B2 (84) | 8.78 | 2.47 | 2.68 | 5.99 | 5.64 | 6.96 | 7.07 | 4.68 | 0.19 | 3.94 | 21.13 | 2.61 |
| train / middle C3-B5 (108) | 7.60 | 1.22 | 3.99 | 6.49 | 6.93 | 8.62 | 7.39 | 7.36 | 0.22 | 4.52 | 16.01 | 2.14 |
| train / treble C6-C8 (84) | 7.84 | 2.55 | 8.93 | 8.16 | 8.91 | 11.87 | 8.69 | 3.64 | 0.20 | 4.70 | 5.33 | 3.45 |
| dev / bass A0-B2 (44) | 9.50 | 3.04 | 2.42 | 6.01 | 5.77 | 6.56 | 6.96 | 5.06 | 0.21 | 3.41 | 21.64 | 3.36 |
| dev / middle C3-B5 (68) | 7.11 | 1.11 | 3.32 | 6.14 | 6.07 | 7.81 | 6.67 | 7.94 | 0.17 | 4.27 | 11.44 | 1.84 |
| dev / treble C6-C8 (44) | 7.52 | 2.70 | 7.27 | 7.15 | 7.86 | 10.89 | 7.53 | 2.65 | 0.23 | 6.09 | 3.79 | 2.63 |

## 2.7.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.11 | 2.00 | 5.07 | 6.67 | 6.77 | 9.01 | 7.34 | 5.02 | 0.20 | 4.38 | 14.98 | 2.36 |
| dev (156) | 7.86 | 2.10 | 4.23 | 6.28 | 6.27 | 8.24 | 6.75 | 5.30 | 0.19 | 4.35 | 12.65 | 2.11 |
| train / bass A0-B2 (84) | 9.17 | 2.54 | 2.66 | 6.11 | 5.77 | 7.04 | 6.78 | 4.74 | 0.20 | 3.86 | 21.35 | 2.15 |
| train / middle C3-B5 (108) | 7.34 | 1.25 | 3.98 | 6.23 | 6.66 | 8.34 | 7.31 | 7.07 | 0.20 | 4.77 | 16.34 | 2.16 |
| train / treble C6-C8 (84) | 8.06 | 2.42 | 9.12 | 7.78 | 7.91 | 11.84 | 7.93 | 2.48 | 0.18 | 4.39 | 6.87 | 2.82 |
| dev / bass A0-B2 (44) | 9.85 | 3.16 | 2.41 | 6.17 | 5.91 | 6.65 | 6.49 | 5.11 | 0.21 | 3.39 | 21.99 | 2.69 |
| dev / middle C3-B5 (68) | 7.01 | 1.13 | 3.32 | 5.96 | 6.04 | 7.75 | 6.74 | 7.33 | 0.16 | 4.36 | 11.71 | 1.87 |
| dev / treble C6-C8 (44) | 7.20 | 2.56 | 7.53 | 6.88 | 6.99 | 10.58 | 7.01 | 2.21 | 0.21 | 5.30 | 4.77 | 1.91 |

## Independent-sample regressions (legacy)

Every note and role where 2.7.0 is worse than 2.6.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.6.0 | 2.7.0 |
|---|---|---|---|---|
| 48 | train | rise_ms | 4.14 | 28.83 |
| 48 | dev | rise_ms | 3.57 | 19.42 |
| 66 | dev | rise_ms | 14.78 | 22.77 |
| 66 | train | rise_ms | 15.55 | 23.22 |
| 93 | dev | rise_ms | 4.29 | 11.06 |
| 93 | train | rise_ms | 5.11 | 11.12 |
| 36 | train | rise_ms | 8.65 | 12.91 |
| 96 | train | sustain_db | 7.32 | 9.22 |
| 96 | train | partial_db | 6.01 | 7.79 |
| 66 | dev | ild_db | 7.93 | 9.67 |
| 96 | dev | sustain_db | 6.83 | 8.49 |
| 66 | train | ild_db | 7.87 | 9.52 |
| 96 | dev | partial_db | 6.46 | 7.98 |
| 36 | dev | rise_ms | 8.37 | 11.20 |
| 45 | dev | icc | 0.09 | 0.15 |
| 45 | train | icc | 0.09 | 0.14 |
| 90 | train | rise_ms | 3.53 | 6.10 |
| 24 | train | partial_db | 9.02 | 10.24 |
| 54 | dev | rise_ms | 44.56 | 46.98 |
| 33 | train | icc | 0.24 | 0.29 |
| 60 | dev | rise_ms | 3.33 | 5.61 |
| 33 | dev | icc | 0.25 | 0.30 |
| 90 | dev | rise_ms | 3.31 | 5.52 |
| 84 | dev | envelope_db | 3.47 | 4.52 |
| 84 | train | envelope_db | 3.48 | 4.50 |
| 93 | dev | noise_db | 5.19 | 6.20 |
| 93 | train | noise_db | 5.79 | 6.80 |
| 96 | train | decay_db_s | 11.07 | 13.06 |
| 48 | train | envelope_db | 2.37 | 3.36 |
| 48 | dev | envelope_db | 2.27 | 3.26 |
| 24 | dev | partial_db | 8.97 | 9.85 |
| 96 | dev | decay_db_s | 11.26 | 13.01 |
| 84 | train | sustain_db | 14.96 | 15.82 |
| 99 | dev | ild_db | 1.16 | 1.99 |
| 69 | train | partial_db | 7.44 | 8.26 |
| 42 | train | rise_ms | 1.87 | 3.51 |
| 69 | dev | partial_db | 7.18 | 7.99 |
| 60 | train | rise_ms | 5.55 | 7.16 |
| 51 | dev | early_db | 4.44 | 5.21 |
| 84 | train | partial_db | 7.52 | 8.27 |
| 27 | dev | rise_ms | 22.78 | 24.29 |
| 84 | dev | sustain_db | 15.27 | 16.01 |
| 84 | dev | partial_db | 8.40 | 9.10 |
| 36 | train | partial_db | 9.38 | 10.08 |
| 93 | dev | attack_db | 5.24 | 5.93 |
| 42 | dev | rise_ms | 0.26 | 1.63 |
| 72 | dev | envelope_db | 7.54 | 8.22 |
| 69 | train | envelope_db | 5.63 | 6.31 |
| 93 | train | attack_db | 6.27 | 6.95 |
| 90 | train | tuning_cents | 3.38 | 4.06 |
| 69 | dev | envelope_db | 5.88 | 6.55 |
| 90 | dev | tuning_cents | 3.51 | 4.18 |
| 60 | dev | envelope_db | 6.91 | 7.56 |
| 60 | train | envelope_db | 6.50 | 7.15 |
| 105 | train | ild_db | 2.03 | 2.67 |
| 72 | train | envelope_db | 7.48 | 8.07 |
| 60 | train | noise_db | 6.05 | 6.64 |
| 84 | train | rise_ms | 10.06 | 11.24 |
| 93 | train | early_db | 7.24 | 7.82 |
| 51 | dev | partial_db | 5.95 | 6.52 |
| 60 | dev | partial_db | 6.49 | 7.06 |
| 60 | train | early_db | 5.82 | 6.38 |
| 21 | train | ild_db | 4.22 | 4.76 |
| 45 | dev | sustain_db | 7.34 | 7.88 |
| 60 | dev | early_db | 5.89 | 6.43 |
| 45 | train | sustain_db | 7.41 | 7.95 |
| 105 | train | noise_db | 7.12 | 7.66 |
| 21 | dev | ild_db | 4.09 | 4.63 |
| 93 | dev | early_db | 6.60 | 7.13 |
| 27 | dev | partial_db | 10.80 | 11.31 |
| 42 | dev | icc | 0.16 | 0.18 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.6037 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 7.9011 | 7.8622 | -0.0389 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.1036 | 2.1031 | -0.0005 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 4.1611 | 4.2307 | 0.0696 | 0 | 0 | 1 |
| dev | attack_db | 156 | 6.3850 | 6.2784 | -0.1066 | 0 | 0 | 0 |
| dev | early_db | 156 | 6.4896 | 6.2730 | -0.2166 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 8.3264 | 8.2386 | -0.0878 | 0 | 0 | 0 |
| dev | noise_db | 153 | 6.9999 | 6.7468 | -0.2530 | 0 | 0 | 3 |
| dev | ild_db | 154 | 5.6731 | 5.3025 | -0.3707 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1980 | 0.1874 | -0.0106 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 4.5400 | 4.3517 | -0.1883 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 12.1568 | 12.6546 | 0.4979 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.4945 | 2.1492 | -0.3453 | 0 | 0 | 0 |
| train | partial_db | 276 | 8.0325 | 8.1131 | 0.0806 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.0042 | 1.9976 | -0.0066 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 5.0243 | 5.0694 | 0.0451 | 0 | 0 | 5 |
| train | attack_db | 276 | 6.8469 | 6.6677 | -0.1792 | 0 | 0 | 0 |
| train | early_db | 276 | 7.1375 | 6.7706 | -0.3669 | 0 | 0 | 0 |
| train | sustain_db | 276 | 9.1054 | 9.0139 | -0.0916 | 0 | 0 | 0 |
| train | noise_db | 274 | 7.6925 | 7.3368 | -0.3557 | 0 | 0 | 2 |
| train | ild_db | 270 | 5.4531 | 5.0182 | -0.4349 | 0 | 0 | 6 |
| train | icc | 270 | 0.2049 | 0.1977 | -0.0072 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.3979 | 4.3772 | -0.0207 | 0 | 0 | 0 |
| train | rise_ms | 276 | 14.3176 | 14.9787 | 0.6612 | 0 | 0 | 0 |
| train | level_db | 276 | 2.6842 | 2.3500 | -0.3341 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 48 | train | rise_ms | 12 | 4.1372 | 28.8299 | 24.6927 |
| 48 | dev | rise_ms | 4 | 3.5729 | 19.4167 | 15.8438 |
| 66 | dev | rise_ms | 4 | 14.7760 | 22.7708 | 7.9948 |
| 66 | train | rise_ms | 12 | 15.5521 | 23.2170 | 7.6649 |
| 93 | dev | rise_ms | 4 | 4.2865 | 11.0625 | 6.7760 |
| 93 | train | rise_ms | 12 | 5.1094 | 11.1181 | 6.0087 |
| 36 | train | rise_ms | 12 | 8.6458 | 12.9080 | 4.2622 |
| 96 | train | sustain_db | 12 | 7.3174 | 9.2219 | 1.9045 |
| 96 | train | partial_db | 12 | 6.0134 | 7.7913 | 1.7779 |
| 66 | dev | ild_db | 4 | 7.9277 | 9.6721 | 1.7444 |
| 96 | dev | sustain_db | 4 | 6.8301 | 8.4853 | 1.6552 |
| 66 | train | ild_db | 12 | 7.8674 | 9.5155 | 1.6480 |
| 96 | dev | partial_db | 4 | 6.4565 | 7.9829 | 1.5264 |
| 36 | dev | rise_ms | 4 | 8.3698 | 11.1979 | 2.8281 |
| 45 | dev | icc | 4 | 0.0918 | 0.1453 | 0.0535 |
| 45 | train | icc | 12 | 0.0884 | 0.1402 | 0.0518 |
| 90 | train | rise_ms | 12 | 3.5278 | 6.0955 | 2.5677 |
| 24 | train | partial_db | 12 | 9.0235 | 10.2427 | 1.2192 |
| 54 | dev | rise_ms | 4 | 44.5625 | 46.9792 | 2.4167 |
| 33 | train | icc | 12 | 0.2439 | 0.2902 | 0.0463 |
| 60 | dev | rise_ms | 4 | 3.3333 | 5.6146 | 2.2812 |
| 33 | dev | icc | 4 | 0.2507 | 0.2960 | 0.0452 |
| 90 | dev | rise_ms | 4 | 3.3073 | 5.5208 | 2.2135 |
| 84 | dev | envelope_db | 4 | 3.4657 | 4.5191 | 1.0534 |
| 84 | train | envelope_db | 12 | 3.4849 | 4.4966 | 1.0117 |
| 93 | dev | noise_db | 4 | 5.1902 | 6.2014 | 1.0112 |
| 93 | train | noise_db | 12 | 5.7923 | 6.8031 | 1.0108 |
| 96 | train | decay_db_s | 12 | 11.0665 | 13.0567 | 1.9903 |
| 48 | train | envelope_db | 12 | 2.3653 | 3.3550 | 0.9898 |
| 48 | dev | envelope_db | 4 | 2.2685 | 3.2571 | 0.9886 |
| 24 | dev | partial_db | 4 | 8.9724 | 9.8451 | 0.8727 |
| 96 | dev | decay_db_s | 4 | 11.2615 | 13.0052 | 1.7436 |
| 84 | train | sustain_db | 12 | 14.9610 | 15.8180 | 0.8570 |
| 99 | dev | ild_db | 16 | 1.1611 | 1.9948 | 0.8337 |
| 69 | train | partial_db | 12 | 7.4409 | 8.2645 | 0.8237 |
| 42 | train | rise_ms | 12 | 1.8733 | 3.5052 | 1.6319 |
| 69 | dev | partial_db | 4 | 7.1818 | 7.9911 | 0.8094 |
| 60 | train | rise_ms | 12 | 5.5538 | 7.1632 | 1.6094 |
| 51 | dev | early_db | 16 | 4.4366 | 5.2144 | 0.7778 |
| 84 | train | partial_db | 12 | 7.5204 | 8.2745 | 0.7541 |
| 27 | dev | rise_ms | 16 | 22.7799 | 24.2865 | 1.5065 |
| 84 | dev | sustain_db | 4 | 15.2733 | 16.0149 | 0.7416 |
| 84 | dev | partial_db | 4 | 8.4028 | 9.1028 | 0.7000 |
| 36 | train | partial_db | 12 | 9.3799 | 10.0792 | 0.6992 |
| 93 | dev | attack_db | 4 | 5.2396 | 5.9339 | 0.6943 |
| 42 | dev | rise_ms | 4 | 0.2604 | 1.6302 | 1.3698 |
| 72 | dev | envelope_db | 4 | 7.5432 | 8.2228 | 0.6796 |
| 69 | train | envelope_db | 12 | 5.6275 | 6.3066 | 0.6791 |
| 93 | train | attack_db | 12 | 6.2692 | 6.9466 | 0.6774 |
| 90 | train | tuning_cents | 12 | 3.3817 | 4.0583 | 0.6766 |
| 69 | dev | envelope_db | 4 | 5.8783 | 6.5467 | 0.6684 |
| 90 | dev | tuning_cents | 4 | 3.5111 | 4.1757 | 0.6647 |
| 60 | dev | envelope_db | 4 | 6.9069 | 7.5596 | 0.6527 |
| 60 | train | envelope_db | 12 | 6.5049 | 7.1533 | 0.6484 |
| 105 | train | ild_db | 11 | 2.0339 | 2.6685 | 0.6346 |
| 72 | train | envelope_db | 12 | 7.4792 | 8.0743 | 0.5951 |
| 60 | train | noise_db | 12 | 6.0529 | 6.6420 | 0.5890 |
| 84 | train | rise_ms | 12 | 10.0642 | 11.2413 | 1.1771 |
| 93 | train | early_db | 12 | 7.2390 | 7.8151 | 0.5760 |
| 51 | dev | partial_db | 16 | 5.9480 | 6.5152 | 0.5672 |
| 60 | dev | partial_db | 4 | 6.4942 | 7.0559 | 0.5616 |
| 60 | train | early_db | 12 | 5.8153 | 6.3767 | 0.5613 |
| 21 | train | ild_db | 12 | 4.2152 | 4.7635 | 0.5483 |
| 45 | dev | sustain_db | 4 | 7.3352 | 7.8779 | 0.5428 |
| 60 | dev | early_db | 4 | 5.8935 | 6.4336 | 0.5401 |
| 45 | train | sustain_db | 12 | 7.4070 | 7.9458 | 0.5388 |
| 105 | train | noise_db | 12 | 7.1218 | 7.6578 | 0.5360 |
| 21 | dev | ild_db | 4 | 4.0930 | 4.6274 | 0.5344 |
| 93 | dev | early_db | 4 | 6.6008 | 7.1344 | 0.5336 |
| 27 | dev | partial_db | 16 | 10.8000 | 11.3120 | 0.5120 |
| 42 | dev | icc | 4 | 0.1636 | 0.1836 | 0.0200 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
