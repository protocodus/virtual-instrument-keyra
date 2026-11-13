# Recording benchmark: candidate 2.13.1 against shipping 2.11.0

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

## candidate 2.13.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.54 | 3.33 | 4.37 | 7.65 | 9.09 | 10.54 | 9.82 | 6.40 | 0.24 | 4.24 | 12.81 | 4.24 |
| dev (21) | 7.27 | 3.39 | 4.65 | 7.71 | 9.10 | 9.88 | 8.75 | 5.94 | 0.27 | 4.13 | 9.15 | 3.19 |
| train / bass A0-B2 (30) | 10.07 | 4.74 | 4.11 | 8.43 | 9.34 | 10.44 | 15.24 | 6.72 | 0.20 | 2.80 | 7.42 | 3.63 |
| train / middle C3-B5 (69) | 7.39 | 2.87 | 3.99 | 7.47 | 8.26 | 8.32 | 8.75 | 6.04 | 0.20 | 3.83 | 19.78 | 4.66 |
| train / treble C6-C8 (38) | 5.80 | 3.07 | 5.33 | 7.37 | 10.39 | 14.66 | 7.50 | 6.80 | 0.36 | 6.14 | 4.41 | 3.95 |
| dev / bass A0-B2 (5) | 9.22 | 3.34 | 2.27 | 8.88 | 9.86 | 10.62 | 12.82 | 3.80 | 0.29 | 2.09 | 2.07 | 2.23 |
| dev / middle C3-B5 (11) | 6.29 | 2.34 | 4.37 | 7.11 | 7.93 | 7.83 | 7.35 | 8.01 | 0.22 | 3.79 | 14.75 | 3.60 |
| dev / treble C6-C8 (5) | 7.47 | 5.74 | 7.65 | 7.88 | 10.89 | 13.64 | 7.77 | 3.54 | 0.35 | 6.94 | 3.90 | 3.22 |

## Independent-sample regressions (legacy)

Every note and role where candidate 2.13.1 is worse than shipping 2.11.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | shipping 2.11.0 | candidate 2.13.1 |
|---|---|---|---|---|
| 50 | train | rise_ms | 68.41 | 79.30 |
| 86 | train | ild_db | 7.22 | 12.29 |
| 48 | train | ild_db | 3.53 | 8.51 |
| 62 | train | ild_db | 3.12 | 7.41 |
| 68 | train | rise_ms | 13.33 | 18.83 |
| 48 | train | icc | 0.15 | 0.25 |
| 59 | dev | ild_db | 4.08 | 6.41 |
| 56 | dev | rise_ms | 17.84 | 22.05 |
| 36 | train | ild_db | 5.08 | 6.98 |
| 60 | train | ild_db | 6.17 | 7.82 |
| 70 | train | rise_ms | 5.11 | 8.33 |
| 94 | train | rise_ms | 1.29 | 4.43 |
| 54 | train | icc | 0.16 | 0.22 |
| 66 | train | attack_db | 6.58 | 7.90 |
| 39 | dev | attack_db | 7.56 | 8.88 |
| 54 | train | noise_db | 11.29 | 12.54 |
| 39 | dev | icc | 0.24 | 0.29 |
| 86 | train | partial_db | 4.83 | 6.07 |
| 56 | dev | ild_db | 7.42 | 8.63 |
| 39 | dev | early_db | 8.66 | 9.86 |
| 36 | train | icc | 0.21 | 0.26 |
| 78 | train | ild_db | 7.83 | 8.95 |
| 54 | train | ild_db | 4.04 | 5.07 |
| 76 | train | level_db | 3.89 | 4.86 |
| 33 | train | ild_db | 6.95 | 7.92 |
| 66 | train | early_db | 8.40 | 9.35 |
| 66 | train | noise_db | 5.87 | 6.81 |
| 86 | train | early_db | 8.28 | 9.22 |
| 90 | train | attack_db | 7.16 | 8.04 |
| 76 | train | rise_ms | 1.15 | 2.87 |
| 66 | train | sustain_db | 8.28 | 9.11 |
| 90 | train | noise_db | 6.98 | 7.79 |
| 88 | dev | noise_db | 6.97 | 7.77 |
| 24 | train | ild_db | 6.39 | 7.18 |
| 74 | train | level_db | 6.50 | 7.27 |
| 88 | dev | early_db | 10.12 | 10.89 |
| 96 | train | partial_db | 6.20 | 6.94 |
| 88 | dev | attack_db | 7.17 | 7.88 |
| 76 | train | attack_db | 7.59 | 8.27 |
| 45 | train | early_db | 8.87 | 9.54 |
| 92 | train | rise_ms | 1.68 | 3.02 |
| 66 | train | partial_db | 7.81 | 8.47 |
| 100 | train | partial_db | 4.90 | 5.54 |
| 48 | train | rise_ms | 36.60 | 37.84 |
| 84 | train | partial_db | 6.52 | 7.13 |
| 39 | dev | sustain_db | 10.02 | 10.62 |
| 36 | train | attack_db | 9.13 | 9.68 |
| 96 | train | tuning_cents | 1.52 | 2.06 |
| 56 | dev | icc | 0.16 | 0.19 |
| 74 | train | attack_db | 6.72 | 7.24 |
| 56 | dev | tuning_cents | 0.89 | 1.41 |
| 82 | train | rise_ms | 6.20 | 7.22 |
| 84 | train | early_db | 9.26 | 9.77 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.0155 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 7.5388 | 7.2686 | -0.2701 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 3.4374 | 3.3869 | -0.0505 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 4.6931 | 4.6477 | -0.0454 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.3318 | 7.7115 | 0.3797 | 0 | 0 | 0 |
| dev | early_db | 21 | 8.6961 | 9.0951 | 0.3990 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 9.9304 | 9.8773 | -0.0531 | 0 | 0 | 0 |
| dev | noise_db | 20 | 8.4884 | 8.6555 | 0.1672 | 0 | 1 | 0 |
| dev | ild_db | 21 | 6.2127 | 5.9421 | -0.2706 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2499 | 0.2660 | 0.0160 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.1183 | 4.1321 | 0.0137 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 9.1062 | 9.1488 | 0.0427 | 0 | 0 | 0 |
| dev | level_db | 21 | 3.0742 | 3.2952 | 0.2210 | 0 | 0 | 0 |
| train | partial_db | 137 | 7.6565 | 7.5369 | -0.1196 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 3.3510 | 3.3346 | -0.0164 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 4.3342 | 4.3713 | 0.0371 | 0 | 0 | 2 |
| train | attack_db | 137 | 7.5009 | 7.6533 | 0.1525 | 0 | 0 | 0 |
| train | early_db | 137 | 8.9997 | 9.0879 | 0.0882 | 0 | 0 | 0 |
| train | sustain_db | 137 | 10.5183 | 10.5409 | 0.0226 | 0 | 0 | 0 |
| train | noise_db | 137 | 9.6567 | 9.8228 | 0.1661 | 0 | 0 | 0 |
| train | ild_db | 135 | 6.6217 | 6.3964 | -0.2253 | 0 | 0 | 2 |
| train | icc | 135 | 0.2470 | 0.2423 | -0.0047 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.2210 | 4.2440 | 0.0230 | 0 | 0 | 0 |
| train | rise_ms | 137 | 13.1620 | 12.8104 | -0.3516 | 0 | 0 | 0 |
| train | level_db | 137 | 4.1732 | 4.2299 | 0.0567 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 50 | train | rise_ms | 5 | 68.4125 | 79.3042 | 10.8917 |
| 86 | train | ild_db | 5 | 7.2214 | 12.2867 | 5.0652 |
| 48 | train | ild_db | 5 | 3.5307 | 8.5108 | 4.9802 |
| 62 | train | ild_db | 5 | 3.1151 | 7.4061 | 4.2910 |
| 68 | train | rise_ms | 5 | 13.3333 | 18.8292 | 5.4958 |
| 48 | train | icc | 5 | 0.1494 | 0.2548 | 0.1054 |
| 59 | dev | ild_db | 1 | 4.0769 | 6.4097 | 2.3328 |
| 56 | dev | rise_ms | 5 | 17.8417 | 22.0500 | 4.2083 |
| 36 | train | ild_db | 5 | 5.0754 | 6.9809 | 1.9055 |
| 60 | train | ild_db | 5 | 6.1747 | 7.8213 | 1.6467 |
| 70 | train | rise_ms | 5 | 5.1125 | 8.3292 | 3.2167 |
| 94 | train | rise_ms | 5 | 1.2917 | 4.4333 | 3.1417 |
| 54 | train | icc | 5 | 0.1644 | 0.2208 | 0.0564 |
| 66 | train | attack_db | 5 | 6.5820 | 7.9048 | 1.3227 |
| 39 | dev | attack_db | 5 | 7.5561 | 8.8751 | 1.3190 |
| 54 | train | noise_db | 5 | 11.2858 | 12.5380 | 1.2522 |
| 39 | dev | icc | 5 | 0.2443 | 0.2942 | 0.0499 |
| 86 | train | partial_db | 5 | 4.8296 | 6.0700 | 1.2404 |
| 56 | dev | ild_db | 5 | 7.4170 | 8.6288 | 1.2118 |
| 39 | dev | early_db | 5 | 8.6631 | 9.8596 | 1.1965 |
| 76 | train | level_db | 5 | 3.8853 | 5.0677 | 1.1824 |
| 36 | train | icc | 5 | 0.2105 | 0.2555 | 0.0450 |
| 78 | train | ild_db | 5 | 7.8340 | 8.9489 | 1.1150 |
| 54 | train | ild_db | 5 | 4.0431 | 5.0714 | 1.0283 |
| 74 | train | level_db | 5 | 6.4959 | 7.4804 | 0.9845 |
| 33 | train | ild_db | 5 | 6.9471 | 7.9182 | 0.9711 |
| 66 | train | early_db | 5 | 8.4012 | 9.3524 | 0.9512 |
| 66 | train | noise_db | 5 | 5.8724 | 6.8095 | 0.9372 |
| 86 | train | early_db | 5 | 8.2845 | 9.2156 | 0.9312 |
| 90 | train | attack_db | 5 | 7.1585 | 8.0432 | 0.8847 |
| 76 | train | rise_ms | 5 | 1.1500 | 2.8667 | 1.7167 |
| 66 | train | sustain_db | 5 | 8.2795 | 9.1144 | 0.8348 |
| 90 | train | noise_db | 5 | 6.9789 | 7.7912 | 0.8123 |
| 88 | dev | noise_db | 5 | 6.9715 | 7.7741 | 0.8026 |
| 24 | train | ild_db | 5 | 6.3886 | 7.1797 | 0.7911 |
| 88 | dev | early_db | 5 | 10.1228 | 10.8881 | 0.7653 |
| 96 | train | partial_db | 5 | 6.1971 | 6.9397 | 0.7426 |
| 88 | dev | attack_db | 5 | 7.1718 | 7.8759 | 0.7042 |
| 76 | train | attack_db | 5 | 7.5868 | 8.2665 | 0.6797 |
| 45 | train | early_db | 5 | 8.8660 | 9.5449 | 0.6790 |
| 92 | train | rise_ms | 5 | 1.6750 | 3.0167 | 1.3417 |
| 66 | train | partial_db | 5 | 7.8105 | 8.4661 | 0.6555 |
| 100 | train | partial_db | 4 | 4.8997 | 5.5444 | 0.6447 |
| 48 | train | rise_ms | 5 | 36.5958 | 37.8417 | 1.2458 |
| 84 | train | partial_db | 5 | 6.5162 | 7.1293 | 0.6131 |
| 39 | dev | sustain_db | 5 | 10.0211 | 10.6154 | 0.5943 |
| 48 | train | level_db | 5 | 4.2101 | 4.7683 | 0.5582 |
| 36 | train | attack_db | 5 | 9.1255 | 9.6752 | 0.5498 |
| 27 | train | level_db | 5 | 3.4108 | 3.9527 | 0.5419 |
| 96 | train | tuning_cents | 5 | 1.5240 | 2.0646 | 0.5406 |
| 56 | dev | icc | 5 | 0.1648 | 0.1863 | 0.0215 |
| 74 | train | attack_db | 5 | 6.7232 | 7.2444 | 0.5211 |
| 56 | dev | tuning_cents | 5 | 0.8935 | 1.4077 | 0.5142 |
| 82 | train | rise_ms | 5 | 6.2042 | 7.2250 | 1.0208 |
| 84 | train | early_db | 5 | 9.2613 | 9.7716 | 0.5103 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| n39v1r1 | 39 | dev | noise_db | gained | - | 10.7280 |
