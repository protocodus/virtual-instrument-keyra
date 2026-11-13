# Recording benchmark: candidate 2.13.0 against shipping 2.11.0

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## shipping 2.11.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.66 | 3.35 | 4.33 | 7.50 | 9.00 | 10.52 | 9.66 | 6.62 | 0.25 | 4.22 | 13.16 | 4.17 |
| dev (21) | 7.54 | 3.44 | 4.69 | 7.33 | 8.70 | 9.93 | 8.49 | 6.21 | 0.25 | 4.12 | 9.11 | 3.07 |
| train / bass A0-B2 (30) | 10.47 | 4.79 | 4.12 | 8.04 | 9.09 | 10.24 | 15.22 | 6.12 | 0.20 | 2.75 | 10.74 | 3.52 |
| train / middle C3-B5 (69) | 7.70 | 2.90 | 3.97 | 7.51 | 8.39 | 8.45 | 8.59 | 6.29 | 0.20 | 3.80 | 18.94 | 4.58 |
| train / treble C6-C8 (38) | 5.35 | 3.03 | 5.22 | 7.05 | 10.04 | 14.48 | 7.20 | 7.67 | 0.37 | 6.16 | 4.58 | 3.96 |
| dev / bass A0-B2 (5) | 9.61 | 4.00 | 2.26 | 7.56 | 8.66 | 10.02 | 12.99 | 4.32 | 0.24 | 2.08 | 3.27 | 2.01 |
| dev / middle C3-B5 (11) | 6.55 | 2.07 | 4.40 | 7.30 | 8.06 | 8.01 | 7.54 | 7.61 | 0.21 | 3.75 | 13.83 | 3.56 |
| dev / treble C6-C8 (5) | 7.64 | 5.88 | 7.77 | 7.17 | 10.12 | 14.06 | 6.97 | 5.04 | 0.35 | 6.97 | 4.56 | 3.06 |

## candidate 2.13.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.70 | 3.43 | 4.41 | 7.64 | 9.06 | 10.52 | 9.81 | 6.46 | 0.24 | 4.23 | 13.14 | 4.23 |
| dev (21) | 7.55 | 3.55 | 4.65 | 7.67 | 9.07 | 9.87 | 8.67 | 5.99 | 0.26 | 4.12 | 9.07 | 3.15 |
| train / bass A0-B2 (30) | 10.80 | 5.22 | 4.28 | 8.36 | 9.21 | 10.35 | 15.10 | 6.98 | 0.20 | 2.75 | 8.95 | 3.60 |
| train / middle C3-B5 (69) | 7.40 | 2.85 | 3.98 | 7.47 | 8.26 | 8.31 | 8.79 | 6.05 | 0.20 | 3.83 | 19.78 | 4.65 |
| train / treble C6-C8 (38) | 5.80 | 3.07 | 5.33 | 7.37 | 10.39 | 14.66 | 7.50 | 6.80 | 0.36 | 6.14 | 4.41 | 3.94 |
| dev / bass A0-B2 (5) | 10.30 | 4.12 | 2.23 | 8.70 | 9.76 | 10.59 | 13.43 | 4.01 | 0.28 | 2.02 | 1.74 | 2.06 |
| dev / middle C3-B5 (11) | 6.34 | 2.29 | 4.39 | 7.11 | 7.93 | 7.83 | 7.35 | 8.01 | 0.22 | 3.79 | 14.75 | 3.62 |
| dev / treble C6-C8 (5) | 7.47 | 5.74 | 7.65 | 7.88 | 10.89 | 13.64 | 7.77 | 3.54 | 0.35 | 6.94 | 3.90 | 3.21 |

## Independent-sample regressions (legacy)

Every note and role where candidate 2.13.0 is worse than shipping 2.11.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | shipping 2.11.0 | candidate 2.13.0 |
|---|---|---|---|---|
| 50 | train | rise_ms | 68.41 | 79.30 |
| 86 | train | ild_db | 7.22 | 12.29 |
| 48 | train | ild_db | 3.53 | 8.56 |
| 62 | train | ild_db | 3.12 | 7.41 |
| 68 | train | rise_ms | 13.33 | 18.83 |
| 48 | train | icc | 0.15 | 0.25 |
| 36 | train | ild_db | 5.08 | 7.48 |
| 59 | dev | ild_db | 4.08 | 6.41 |
| 56 | dev | rise_ms | 17.84 | 22.05 |
| 60 | train | ild_db | 6.17 | 7.82 |
| 70 | train | rise_ms | 5.11 | 8.33 |
| 94 | train | rise_ms | 1.29 | 4.43 |
| 54 | train | icc | 0.16 | 0.22 |
| 66 | train | attack_db | 6.58 | 7.91 |
| 86 | train | partial_db | 4.83 | 6.07 |
| 33 | train | ild_db | 6.95 | 8.18 |
| 54 | train | noise_db | 11.29 | 12.51 |
| 56 | dev | ild_db | 7.42 | 8.64 |
| 24 | train | ild_db | 6.39 | 7.57 |
| 39 | dev | attack_db | 7.56 | 8.70 |
| 27 | train | tuning_cents | 6.51 | 7.65 |
| 78 | train | ild_db | 7.83 | 8.95 |
| 39 | dev | early_db | 8.66 | 9.76 |
| 54 | train | ild_db | 4.04 | 5.09 |
| 24 | train | partial_db | 11.61 | 12.62 |
| 76 | train | level_db | 3.89 | 4.89 |
| 36 | train | icc | 0.21 | 0.25 |
| 39 | dev | icc | 0.24 | 0.28 |
| 66 | train | early_db | 8.40 | 9.35 |
| 66 | train | noise_db | 5.87 | 6.81 |
| 86 | train | early_db | 8.28 | 9.22 |
| 90 | train | attack_db | 7.16 | 8.04 |
| 76 | train | rise_ms | 1.15 | 2.87 |
| 66 | train | sustain_db | 8.28 | 9.11 |
| 90 | train | noise_db | 6.98 | 7.79 |
| 74 | train | level_db | 6.50 | 7.31 |
| 88 | dev | noise_db | 6.97 | 7.77 |
| 88 | dev | early_db | 10.12 | 10.89 |
| 24 | train | tuning_cents | 8.31 | 9.06 |
| 36 | train | partial_db | 11.75 | 12.50 |
| 96 | train | partial_db | 6.20 | 6.94 |
| 88 | dev | attack_db | 7.17 | 7.88 |
| 39 | dev | partial_db | 9.61 | 10.30 |
| 45 | train | early_db | 8.87 | 9.56 |
| 76 | train | attack_db | 7.59 | 8.27 |
| 92 | train | rise_ms | 1.68 | 3.02 |
| 66 | train | partial_db | 7.81 | 8.47 |
| 100 | train | partial_db | 4.90 | 5.54 |
| 27 | train | decay_db_s | 7.89 | 9.18 |
| 48 | train | rise_ms | 36.60 | 37.85 |
| 84 | train | partial_db | 6.52 | 7.13 |
| 39 | dev | sustain_db | 10.02 | 10.59 |
| 59 | dev | partial_db | 9.31 | 9.87 |
| 96 | train | tuning_cents | 1.52 | 2.06 |
| 56 | dev | icc | 0.16 | 0.19 |
| 45 | train | partial_db | 10.30 | 10.83 |
| 50 | train | icc | 0.15 | 0.17 |
| 74 | train | attack_db | 6.72 | 7.24 |
| 82 | train | rise_ms | 6.20 | 7.22 |
| 84 | train | early_db | 9.26 | 9.77 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.0155 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 7.5388 | 7.5504 | 0.0116 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 3.4374 | 3.5456 | 0.1082 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 4.6931 | 4.6505 | -0.0426 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.3318 | 7.6700 | 0.3382 | 0 | 0 | 0 |
| dev | early_db | 21 | 8.6961 | 9.0705 | 0.3744 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 9.9304 | 9.8720 | -0.0584 | 0 | 0 | 0 |
| dev | noise_db | 20 | 8.4884 | 8.6723 | 0.1839 | 0 | 0 | 1 |
| dev | ild_db | 21 | 6.2127 | 5.9939 | -0.2188 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2499 | 0.2632 | 0.0132 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.1183 | 4.1157 | -0.0026 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 9.1062 | 9.0694 | -0.0367 | 0 | 0 | 0 |
| dev | level_db | 21 | 3.0742 | 3.2677 | 0.1935 | 0 | 0 | 0 |
| train | partial_db | 137 | 7.6565 | 7.7032 | 0.0466 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 3.3510 | 3.4330 | 0.0821 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 4.3342 | 4.4075 | 0.0734 | 0 | 0 | 2 |
| train | attack_db | 137 | 7.5009 | 7.6394 | 0.1385 | 0 | 0 | 0 |
| train | early_db | 137 | 8.9997 | 9.0596 | 0.0599 | 0 | 0 | 0 |
| train | sustain_db | 137 | 10.5183 | 10.5186 | 0.0004 | 0 | 0 | 0 |
| train | noise_db | 137 | 9.6567 | 9.8120 | 0.1553 | 0 | 0 | 0 |
| train | ild_db | 135 | 6.6217 | 6.4559 | -0.1658 | 0 | 0 | 2 |
| train | icc | 135 | 0.2470 | 0.2424 | -0.0046 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.2210 | 4.2322 | 0.0112 | 0 | 0 | 0 |
| train | rise_ms | 137 | 13.1620 | 13.1429 | -0.0190 | 0 | 0 | 0 |
| train | level_db | 137 | 4.1732 | 4.2190 | 0.0458 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 50 | train | rise_ms | 5 | 68.4125 | 79.3042 | 10.8917 |
| 86 | train | ild_db | 5 | 7.2214 | 12.2867 | 5.0652 |
| 48 | train | ild_db | 5 | 3.5307 | 8.5562 | 5.0255 |
| 62 | train | ild_db | 5 | 3.1151 | 7.4061 | 4.2910 |
| 68 | train | rise_ms | 5 | 13.3333 | 18.8292 | 5.4958 |
| 48 | train | icc | 5 | 0.1494 | 0.2547 | 0.1053 |
| 36 | train | ild_db | 5 | 5.0754 | 7.4809 | 2.4055 |
| 59 | dev | ild_db | 1 | 4.0769 | 6.4098 | 2.3329 |
| 56 | dev | rise_ms | 5 | 17.8417 | 22.0500 | 4.2083 |
| 60 | train | ild_db | 5 | 6.1747 | 7.8213 | 1.6466 |
| 70 | train | rise_ms | 5 | 5.1125 | 8.3292 | 3.2167 |
| 94 | train | rise_ms | 5 | 1.2917 | 4.4333 | 3.1417 |
| 54 | train | icc | 5 | 0.1644 | 0.2180 | 0.0536 |
| 66 | train | attack_db | 5 | 6.5820 | 7.9051 | 1.3231 |
| 86 | train | partial_db | 5 | 4.8296 | 6.0700 | 1.2404 |
| 33 | train | ild_db | 5 | 6.9471 | 8.1822 | 1.2351 |
| 54 | train | noise_db | 5 | 11.2858 | 12.5120 | 1.2262 |
| 56 | dev | ild_db | 5 | 7.4170 | 8.6416 | 1.2246 |
| 76 | train | level_db | 5 | 3.8853 | 5.1096 | 1.2243 |
| 24 | train | ild_db | 5 | 6.3886 | 7.5662 | 1.1776 |
| 39 | dev | attack_db | 5 | 7.5561 | 8.7007 | 1.1446 |
| 27 | train | tuning_cents | 5 | 6.5122 | 7.6506 | 1.1383 |
| 78 | train | ild_db | 5 | 7.8340 | 8.9489 | 1.1149 |
| 39 | dev | early_db | 5 | 8.6631 | 9.7570 | 1.0938 |
| 54 | train | ild_db | 5 | 4.0431 | 5.0904 | 1.0474 |
| 74 | train | level_db | 5 | 6.4959 | 7.5223 | 1.0264 |
| 24 | train | partial_db | 5 | 11.6148 | 12.6235 | 1.0088 |
| 36 | train | icc | 5 | 0.2105 | 0.2508 | 0.0402 |
| 39 | dev | icc | 5 | 0.2443 | 0.2827 | 0.0384 |
| 66 | train | early_db | 5 | 8.4012 | 9.3527 | 0.9515 |
| 66 | train | noise_db | 5 | 5.8724 | 6.8107 | 0.9383 |
| 86 | train | early_db | 5 | 8.2845 | 9.2156 | 0.9312 |
| 90 | train | attack_db | 5 | 7.1585 | 8.0432 | 0.8847 |
| 76 | train | rise_ms | 5 | 1.1500 | 2.8667 | 1.7167 |
| 66 | train | sustain_db | 5 | 8.2795 | 9.1144 | 0.8348 |
| 90 | train | noise_db | 5 | 6.9789 | 7.7912 | 0.8123 |
| 88 | dev | noise_db | 5 | 6.9715 | 7.7741 | 0.8026 |
| 88 | dev | early_db | 5 | 10.1228 | 10.8881 | 0.7653 |
| 24 | train | tuning_cents | 5 | 8.3098 | 9.0604 | 0.7506 |
| 36 | train | partial_db | 5 | 11.7549 | 12.4988 | 0.7439 |
| 96 | train | partial_db | 5 | 6.1971 | 6.9397 | 0.7426 |
| 88 | dev | attack_db | 5 | 7.1718 | 7.8760 | 0.7042 |
| 39 | dev | partial_db | 5 | 9.6091 | 10.3026 | 0.6935 |
| 45 | train | early_db | 5 | 8.8660 | 9.5555 | 0.6896 |
| 76 | train | attack_db | 5 | 7.5868 | 8.2665 | 0.6798 |
| 92 | train | rise_ms | 5 | 1.6750 | 3.0167 | 1.3417 |
| 66 | train | partial_db | 5 | 7.8105 | 8.4671 | 0.6566 |
| 100 | train | partial_db | 4 | 4.8997 | 5.5444 | 0.6447 |
| 27 | train | decay_db_s | 5 | 7.8928 | 9.1795 | 1.2867 |
| 48 | train | rise_ms | 5 | 36.5958 | 37.8458 | 1.2500 |
| 84 | train | partial_db | 5 | 6.5162 | 7.1293 | 0.6131 |
| 39 | dev | sustain_db | 5 | 10.0211 | 10.5940 | 0.5730 |
| 59 | dev | partial_db | 1 | 9.3131 | 9.8737 | 0.5607 |
| 96 | train | tuning_cents | 5 | 1.5240 | 2.0646 | 0.5406 |
| 48 | train | level_db | 5 | 4.2101 | 4.7467 | 0.5367 |
| 56 | dev | icc | 5 | 0.1648 | 0.1861 | 0.0214 |
| 45 | train | partial_db | 5 | 10.3011 | 10.8279 | 0.5268 |
| 50 | train | icc | 5 | 0.1489 | 0.1698 | 0.0209 |
| 74 | train | attack_db | 5 | 6.7232 | 7.2444 | 0.5211 |
| 72 | dev | level_db | 5 | 3.4464 | 3.9637 | 0.5174 |
| 82 | train | rise_ms | 5 | 6.2042 | 7.2250 | 1.0208 |
| 84 | train | early_db | 5 | 9.2613 | 9.7714 | 0.5101 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
