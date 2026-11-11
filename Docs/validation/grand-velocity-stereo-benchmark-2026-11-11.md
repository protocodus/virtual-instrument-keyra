# Recording benchmark: candidate 2.1.0 against shipping 2.0.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## shipping 2.0.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 12.02 | 2.85 | 6.65 | 9.39 | 10.18 | 11.46 | 10.95 | 5.69 | 0.22 | 4.89 | 16.10 | 4.91 |
| dev (156) | 11.70 | 3.09 | 5.48 | 9.50 | 10.04 | 10.87 | 10.62 | 5.42 | 0.21 | 4.81 | 15.47 | 4.47 |
| train / bass A0-B2 (84) | 10.58 | 3.06 | 2.68 | 5.84 | 5.86 | 6.93 | 7.98 | 4.49 | 0.19 | 3.95 | 25.01 | 3.49 |
| train / middle C3-B5 (108) | 9.73 | 2.65 | 4.07 | 8.67 | 8.92 | 8.96 | 9.20 | 7.64 | 0.24 | 4.45 | 17.71 | 5.81 |
| train / treble C6-C8 (84) | 16.41 | 2.90 | 14.41 | 13.88 | 16.13 | 19.19 | 15.95 | 4.27 | 0.22 | 6.39 | 5.11 | 5.18 |
| dev / bass A0-B2 (44) | 11.03 | 3.57 | 2.44 | 6.50 | 6.50 | 6.83 | 7.48 | 4.75 | 0.21 | 3.49 | 31.65 | 3.36 |
| dev / middle C3-B5 (68) | 9.25 | 2.39 | 3.36 | 8.44 | 8.37 | 8.17 | 8.79 | 7.42 | 0.19 | 4.78 | 12.65 | 4.91 |
| dev / treble C6-C8 (44) | 16.14 | 3.68 | 11.95 | 14.14 | 16.18 | 19.09 | 16.42 | 2.89 | 0.25 | 6.16 | 3.66 | 4.90 |

## candidate 2.1.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.86 | 2.81 | 4.72 | 8.49 | 9.57 | 10.06 | 10.55 | 5.48 | 0.21 | 4.23 | 17.26 | 3.72 |
| dev (156) | 8.19 | 2.91 | 3.67 | 8.11 | 8.92 | 9.10 | 10.07 | 5.60 | 0.21 | 4.18 | 14.93 | 3.39 |
| train / bass A0-B2 (84) | 8.64 | 3.09 | 2.69 | 5.68 | 5.58 | 7.05 | 8.07 | 4.68 | 0.19 | 3.95 | 25.43 | 2.67 |
| train / middle C3-B5 (108) | 7.87 | 2.56 | 3.94 | 7.21 | 7.47 | 8.57 | 8.43 | 7.48 | 0.22 | 4.52 | 21.11 | 4.00 |
| train / treble C6-C8 (84) | 10.36 | 2.86 | 7.97 | 12.95 | 16.27 | 14.98 | 15.53 | 3.56 | 0.23 | 4.15 | 4.14 | 4.40 |
| dev / bass A0-B2 (44) | 8.52 | 3.55 | 2.45 | 5.87 | 5.85 | 6.69 | 8.06 | 4.87 | 0.22 | 3.47 | 27.58 | 4.15 |
| dev / middle C3-B5 (68) | 7.49 | 2.24 | 3.42 | 6.74 | 6.48 | 7.68 | 7.82 | 7.78 | 0.17 | 4.35 | 14.32 | 3.13 |
| dev / treble C6-C8 (44) | 8.96 | 3.31 | 5.34 | 12.49 | 15.76 | 13.71 | 15.40 | 2.82 | 0.28 | 4.62 | 3.23 | 3.03 |

## Independent-sample regressions (legacy)

Every note and role where candidate 2.1.0 is worse than shipping 2.0.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | shipping 2.0.0 | candidate 2.1.0 |
|---|---|---|---|---|
| 48 | train | rise_ms | 19.18 | 57.30 |
| 48 | dev | rise_ms | 19.69 | 57.79 |
| 84 | train | early_db | 12.83 | 17.16 |
| 78 | train | partial_db | 6.89 | 11.12 |
| 78 | train | sustain_db | 8.92 | 13.13 |
| 84 | dev | early_db | 12.69 | 16.86 |
| 78 | dev | sustain_db | 9.61 | 13.73 |
| 27 | dev | level_db | 3.20 | 7.05 |
| 78 | dev | partial_db | 7.86 | 11.68 |
| 72 | dev | sustain_db | 11.18 | 14.85 |
| 21 | train | level_db | 2.27 | 5.88 |
| 72 | train | sustain_db | 11.06 | 14.61 |
| 21 | dev | level_db | 2.69 | 6.08 |
| 72 | dev | partial_db | 8.85 | 12.23 |
| 84 | dev | noise_db | 11.93 | 15.25 |
| 84 | train | noise_db | 12.17 | 15.45 |
| 72 | train | partial_db | 8.83 | 12.11 |
| 96 | train | level_db | 3.91 | 7.05 |
| 84 | train | attack_db | 10.93 | 13.96 |
| 84 | dev | attack_db | 10.93 | 13.92 |
| 102 | dev | early_db | 17.59 | 20.18 |
| 24 | train | level_db | 3.13 | 5.63 |
| 96 | dev | level_db | 4.57 | 6.94 |
| 102 | train | early_db | 18.56 | 20.90 |
| 24 | dev | level_db | 3.06 | 5.34 |
| 33 | dev | rise_ms | 5.18 | 9.59 |
| 21 | dev | sustain_db | 5.34 | 7.51 |
| 21 | train | sustain_db | 5.44 | 7.59 |
| 69 | dev | envelope_db | 4.01 | 6.08 |
| 27 | dev | noise_db | 6.04 | 8.11 |
| 69 | train | envelope_db | 3.84 | 5.83 |
| 72 | train | envelope_db | 5.32 | 7.27 |
| 72 | dev | envelope_db | 5.39 | 7.33 |
| 45 | train | noise_db | 5.76 | 7.70 |
| 45 | dev | noise_db | 7.41 | 8.99 |
| 57 | train | noise_db | 9.62 | 11.20 |
| 57 | dev | noise_db | 8.28 | 9.84 |
| 105 | dev | level_db | 2.66 | 4.18 |
| 81 | dev | ild_db | 8.78 | 10.23 |
| 105 | train | tuning_cents | 2.59 | 4.04 |
| 81 | train | ild_db | 8.27 | 9.72 |
| 48 | dev | noise_db | 5.92 | 7.33 |
| 105 | train | level_db | 3.16 | 4.57 |
| 33 | train | rise_ms | 7.20 | 9.98 |
| 102 | train | icc | 0.41 | 0.46 |
| 84 | train | rise_ms | 5.69 | 8.36 |
| 24 | dev | sustain_db | 5.14 | 6.46 |
| 42 | train | attack_db | 4.29 | 5.57 |
| 24 | train | sustain_db | 5.10 | 6.33 |
| 102 | dev | noise_db | 16.94 | 18.18 |
| 102 | train | noise_db | 16.92 | 18.15 |
| 102 | dev | icc | 0.40 | 0.45 |
| 99 | dev | icc | 0.31 | 0.36 |
| 42 | train | noise_db | 11.44 | 12.61 |
| 48 | train | noise_db | 4.78 | 5.94 |
| 108 | dev | icc | 0.25 | 0.29 |
| 42 | dev | attack_db | 3.97 | 5.08 |
| 75 | dev | ild_db | 9.49 | 10.49 |
| 108 | train | icc | 0.32 | 0.36 |
| 99 | dev | ild_db | 0.94 | 1.87 |
| 51 | dev | noise_db | 5.78 | 6.71 |
| 51 | dev | ild_db | 4.64 | 5.54 |
| 60 | dev | envelope_db | 6.26 | 7.05 |
| 42 | train | early_db | 3.50 | 4.24 |
| 78 | dev | envelope_db | 6.49 | 7.22 |
| 84 | dev | rise_ms | 7.86 | 9.30 |
| 102 | dev | attack_db | 15.22 | 15.92 |
| 84 | dev | envelope_db | 2.90 | 3.60 |
| 78 | train | envelope_db | 6.42 | 7.11 |
| 108 | train | level_db | 4.20 | 4.88 |
| 60 | train | envelope_db | 6.01 | 6.67 |
| 60 | dev | level_db | 2.30 | 2.94 |
| 102 | train | attack_db | 15.26 | 15.90 |
| 60 | train | level_db | 2.26 | 2.87 |
| 42 | dev | early_db | 3.09 | 3.69 |
| 27 | dev | icc | 0.23 | 0.25 |
| 57 | train | ild_db | 6.32 | 6.90 |
| 54 | train | noise_db | 11.77 | 12.34 |
| 33 | train | icc | 0.25 | 0.27 |
| 102 | train | level_db | 4.54 | 5.09 |
| 57 | dev | ild_db | 6.46 | 6.99 |
| 54 | dev | noise_db | 11.96 | 12.49 |
| 42 | dev | noise_db | 11.98 | 12.51 |
| 108 | dev | envelope_db | 3.34 | 3.86 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (29.8905 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 11.6964 | 8.1924 | -3.5040 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 3.0864 | 2.9129 | -0.1735 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 5.4786 | 3.6741 | -1.8044 | 0 | 0 | 1 |
| dev | attack_db | 156 | 9.5013 | 8.1148 | -1.3865 | 0 | 0 | 0 |
| dev | early_db | 156 | 10.0422 | 8.9192 | -1.1230 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 10.8728 | 9.1030 | -1.7698 | 0 | 0 | 0 |
| dev | noise_db | 153 | 10.6177 | 10.0668 | -0.5509 | 0 | 0 | 3 |
| dev | ild_db | 154 | 5.4224 | 5.5967 | 0.1743 | 0 | 0 | 2 |
| dev | icc | 154 | 0.2105 | 0.2140 | 0.0036 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 4.8061 | 4.1774 | -0.6287 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 15.4748 | 14.9335 | -0.5413 | 0 | 0 | 0 |
| dev | level_db | 156 | 4.4695 | 4.6132 | 0.1437 | 0 | 0 | 0 |
| train | partial_db | 276 | 12.0238 | 8.8626 | -3.1612 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.8484 | 2.8127 | -0.0357 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 6.6544 | 4.7235 | -1.9309 | 0 | 0 | 5 |
| train | attack_db | 276 | 9.3942 | 8.4934 | -0.9008 | 0 | 0 | 0 |
| train | early_db | 276 | 10.1826 | 9.5749 | -0.6076 | 0 | 0 | 0 |
| train | sustain_db | 276 | 11.4566 | 10.0594 | -1.3972 | 0 | 0 | 0 |
| train | noise_db | 268 | 10.9980 | 10.5517 | -0.4462 | 2 | 0 | 6 |
| train | ild_db | 270 | 5.6865 | 5.4759 | -0.2106 | 0 | 0 | 6 |
| train | icc | 270 | 0.2210 | 0.2136 | -0.0074 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.8882 | 4.2340 | -0.6541 | 0 | 0 | 0 |
| train | rise_ms | 276 | 16.0952 | 17.2584 | 1.1632 | 0 | 0 | 0 |
| train | level_db | 276 | 4.9117 | 5.4566 | 0.5449 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 48 | train | rise_ms | 12 | 19.1771 | 57.2951 | 38.1181 |
| 48 | dev | rise_ms | 4 | 19.6875 | 57.7865 | 38.0990 |
| 96 | dev | level_db | 4 | 4.5688 | 11.6433 | 7.0745 |
| 96 | train | level_db | 12 | 3.9069 | 10.9714 | 7.0644 |
| 105 | dev | level_db | 4 | 2.6618 | 8.7005 | 6.0387 |
| 105 | train | level_db | 12 | 3.1647 | 8.3647 | 5.2000 |
| 84 | train | early_db | 12 | 12.8348 | 17.1592 | 4.3244 |
| 81 | dev | level_db | 4 | 3.7911 | 8.0427 | 4.2516 |
| 78 | train | partial_db | 12 | 6.8860 | 11.1200 | 4.2340 |
| 78 | train | sustain_db | 12 | 8.9248 | 13.1345 | 4.2097 |
| 81 | train | level_db | 12 | 3.4426 | 7.6207 | 4.1782 |
| 84 | dev | early_db | 4 | 12.6884 | 16.8636 | 4.1752 |
| 78 | dev | sustain_db | 4 | 9.6082 | 13.7319 | 4.1237 |
| 78 | dev | partial_db | 4 | 7.8576 | 11.6837 | 3.8261 |
| 84 | train | level_db | 12 | 4.9743 | 8.6999 | 3.7256 |
| 84 | dev | level_db | 4 | 5.1076 | 8.7819 | 3.6742 |
| 72 | dev | sustain_db | 4 | 11.1783 | 14.8462 | 3.6680 |
| 72 | train | sustain_db | 12 | 11.0601 | 14.6072 | 3.5471 |
| 72 | dev | partial_db | 4 | 8.8507 | 12.2338 | 3.3831 |
| 84 | dev | noise_db | 4 | 11.9342 | 15.2491 | 3.3149 |
| 84 | train | noise_db | 12 | 12.1683 | 15.4481 | 3.2798 |
| 72 | train | partial_db | 12 | 8.8261 | 12.1059 | 3.2797 |
| 69 | train | level_db | 12 | 5.3688 | 8.5170 | 3.1482 |
| 84 | train | attack_db | 12 | 10.9294 | 13.9603 | 3.0309 |
| 69 | dev | level_db | 4 | 5.6677 | 8.6646 | 2.9969 |
| 84 | dev | attack_db | 4 | 10.9279 | 13.9202 | 2.9923 |
| 102 | dev | early_db | 4 | 17.5923 | 20.1762 | 2.5840 |
| 66 | train | level_db | 12 | 5.2444 | 7.7498 | 2.5054 |
| 66 | dev | level_db | 4 | 5.1541 | 7.5406 | 2.3865 |
| 102 | train | early_db | 12 | 18.5573 | 20.9013 | 2.3440 |
| 33 | dev | rise_ms | 4 | 5.1771 | 9.5885 | 4.4115 |
| 21 | dev | sustain_db | 4 | 5.3350 | 7.5058 | 2.1708 |
| 21 | train | sustain_db | 12 | 5.4427 | 7.5882 | 2.1455 |
| 69 | dev | envelope_db | 4 | 4.0056 | 6.0828 | 2.0772 |
| 27 | dev | noise_db | 16 | 6.0397 | 8.1052 | 2.0654 |
| 69 | train | envelope_db | 12 | 3.8425 | 5.8348 | 1.9924 |
| 72 | train | envelope_db | 12 | 5.3230 | 7.2688 | 1.9457 |
| 72 | dev | envelope_db | 4 | 5.3899 | 7.3342 | 1.9443 |
| 45 | train | noise_db | 11 | 5.7592 | 7.6990 | 1.9397 |
| 57 | train | level_db | 12 | 7.0022 | 8.9363 | 1.9341 |
| 102 | train | level_db | 12 | 4.5379 | 6.4093 | 1.8714 |
| 57 | dev | level_db | 4 | 6.8307 | 8.6373 | 1.8066 |
| 102 | dev | level_db | 4 | 5.0726 | 6.8714 | 1.7987 |
| 45 | dev | noise_db | 3 | 7.4085 | 8.9924 | 1.5839 |
| 57 | train | noise_db | 12 | 9.6238 | 11.2003 | 1.5765 |
| 57 | dev | noise_db | 4 | 8.2812 | 9.8432 | 1.5620 |
| 81 | dev | ild_db | 4 | 8.7781 | 10.2314 | 1.4533 |
| 105 | train | tuning_cents | 12 | 2.5872 | 4.0398 | 1.4526 |
| 81 | train | ild_db | 12 | 8.2658 | 9.7163 | 1.4506 |
| 48 | dev | noise_db | 4 | 5.9184 | 7.3320 | 1.4136 |
| 33 | train | rise_ms | 12 | 7.1997 | 9.9826 | 2.7830 |
| 102 | train | icc | 12 | 0.4106 | 0.4648 | 0.0541 |
| 84 | train | rise_ms | 12 | 5.6875 | 8.3594 | 2.6719 |
| 24 | dev | sustain_db | 4 | 5.1412 | 6.4608 | 1.3196 |
| 42 | train | attack_db | 12 | 4.2930 | 5.5684 | 1.2754 |
| 24 | train | sustain_db | 12 | 5.0987 | 6.3345 | 1.2358 |
| 102 | dev | noise_db | 4 | 16.9449 | 18.1772 | 1.2323 |
| 102 | train | noise_db | 12 | 16.9180 | 18.1480 | 1.2299 |
| 102 | dev | icc | 4 | 0.3979 | 0.4464 | 0.0485 |
| 99 | dev | icc | 16 | 0.3120 | 0.3592 | 0.0472 |
| 48 | train | noise_db | 11 | 4.7778 | 5.9363 | 1.1586 |
| 108 | dev | icc | 2 | 0.2459 | 0.2907 | 0.0448 |
| 42 | dev | attack_db | 4 | 3.9659 | 5.0822 | 1.1162 |
| 45 | train | level_db | 12 | 4.9209 | 6.0078 | 1.0869 |
| 48 | train | level_db | 12 | 6.1220 | 7.1926 | 1.0706 |
| 75 | dev | ild_db | 16 | 9.4908 | 10.4942 | 1.0034 |
| 45 | dev | level_db | 4 | 4.8351 | 5.8278 | 0.9928 |
| 33 | train | level_db | 12 | 4.1997 | 5.1900 | 0.9903 |
| 108 | train | icc | 7 | 0.3235 | 0.3627 | 0.0392 |
| 48 | dev | level_db | 4 | 6.2470 | 7.2168 | 0.9698 |
| 51 | dev | level_db | 16 | 3.6061 | 4.5682 | 0.9621 |
| 99 | dev | ild_db | 16 | 0.9375 | 1.8734 | 0.9359 |
| 51 | dev | noise_db | 14 | 5.7781 | 6.7105 | 0.9324 |
| 33 | dev | level_db | 4 | 4.0402 | 4.9591 | 0.9189 |
| 51 | dev | ild_db | 16 | 4.6393 | 5.5420 | 0.9027 |
| 60 | dev | envelope_db | 4 | 6.2646 | 7.0497 | 0.7851 |
| 54 | train | level_db | 12 | 8.9566 | 9.7413 | 0.7847 |
| 42 | train | early_db | 12 | 3.4954 | 4.2392 | 0.7438 |
| 36 | train | level_db | 12 | 4.3677 | 5.1020 | 0.7343 |
| 78 | dev | envelope_db | 4 | 6.4852 | 7.2166 | 0.7313 |
| 84 | dev | rise_ms | 4 | 7.8594 | 9.2969 | 1.4375 |
| 102 | dev | attack_db | 4 | 15.2190 | 15.9200 | 0.7010 |
| 84 | dev | envelope_db | 4 | 2.9028 | 3.6015 | 0.6987 |
| 54 | dev | level_db | 4 | 8.9625 | 9.6573 | 0.6948 |
| 78 | train | envelope_db | 12 | 6.4196 | 7.1128 | 0.6932 |
| 60 | train | envelope_db | 12 | 6.0080 | 6.6723 | 0.6643 |
| 36 | dev | level_db | 4 | 3.9925 | 4.6414 | 0.6489 |
| 102 | train | attack_db | 12 | 15.2626 | 15.9007 | 0.6380 |
| 42 | dev | early_db | 4 | 3.0907 | 3.6889 | 0.5982 |
| 27 | dev | icc | 16 | 0.2288 | 0.2521 | 0.0232 |
| 57 | train | ild_db | 12 | 6.3177 | 6.8961 | 0.5785 |
| 54 | train | noise_db | 12 | 11.7748 | 12.3397 | 0.5649 |
| 33 | train | icc | 12 | 0.2507 | 0.2727 | 0.0220 |
| 57 | dev | ild_db | 4 | 6.4639 | 6.9897 | 0.5258 |
| 54 | dev | noise_db | 4 | 11.9647 | 12.4876 | 0.5229 |
| 42 | dev | noise_db | 4 | 11.9834 | 12.5062 | 0.5228 |
| 108 | dev | envelope_db | 4 | 3.3378 | 3.8552 | 0.5175 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| A1v1 | 33 | train | noise_db | lost | 4.7534 | - |
| F#2v2 | 42 | train | noise_db | lost | 3.3427 | - |
