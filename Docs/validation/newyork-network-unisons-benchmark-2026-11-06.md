# Recording benchmark: 0.4.26 against 0.4.25

Every train and dev note of `Tools/corpus/split-newyork-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.25

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (61) | 7.73 | 0.59 | 3.99 | 7.53 | 7.41 | 7.87 | 8.13 | 1.74 | 0.09 | 2.59 | 12.07 | 0.88 |
| dev (17) | 10.63 | 2.54 | 7.26 | 9.36 | 8.77 | 10.48 | 9.60 | 5.98 | 0.20 | 4.94 | 8.28 | 5.61 |
| train / bass A0-B2 (20) | 9.04 | 0.41 | 1.85 | 9.40 | 9.28 | 8.15 | 12.39 | 1.39 | 0.08 | 2.15 | 14.39 | 0.85 |
| train / middle C3-B5 (24) | 8.26 | 0.25 | 4.35 | 6.40 | 6.54 | 7.15 | 5.53 | 1.53 | 0.11 | 2.59 | 15.86 | 0.23 |
| train / treble C6-C8 (17) | 5.29 | 1.31 | 7.38 | 6.94 | 6.44 | 8.63 | 6.80 | 2.92 | 0.07 | 3.12 | 3.97 | 1.83 |
| dev / bass A0-B2 (5) | 10.57 | 4.22 | 3.50 | 8.85 | 8.04 | 8.63 | 11.37 | 3.62 | 0.13 | 3.41 | 8.04 | 4.09 |
| dev / middle C3-B5 (5) | 10.08 | 1.08 | 5.17 | 7.86 | 7.80 | 10.02 | 7.01 | 5.49 | 0.19 | 3.82 | 9.84 | 3.40 |
| dev / treble C6-C8 (7) | 11.07 | 2.39 | 11.44 | 10.79 | 9.98 | 12.14 | 10.18 | 8.01 | 0.25 | 6.82 | 7.35 | 8.26 |

## 0.4.26

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (61) | 7.67 | 0.53 | 3.89 | 7.53 | 7.40 | 7.87 | 8.14 | 1.73 | 0.09 | 2.59 | 12.06 | 0.90 |
| dev (17) | 10.35 | 1.73 | 7.07 | 9.59 | 9.05 | 10.16 | 9.34 | 6.11 | 0.23 | 5.22 | 7.99 | 5.45 |
| train / bass A0-B2 (20) | 9.04 | 0.36 | 1.84 | 9.40 | 9.28 | 8.16 | 12.40 | 1.39 | 0.08 | 2.16 | 14.39 | 0.87 |
| train / middle C3-B5 (24) | 8.25 | 0.25 | 4.35 | 6.39 | 6.55 | 7.15 | 5.57 | 1.53 | 0.11 | 2.59 | 15.86 | 0.23 |
| train / treble C6-C8 (17) | 5.10 | 1.18 | 6.90 | 6.93 | 6.39 | 8.65 | 6.77 | 2.93 | 0.07 | 3.10 | 3.94 | 1.88 |
| dev / bass A0-B2 (5) | 10.10 | 2.02 | 2.64 | 9.21 | 9.11 | 9.09 | 11.35 | 3.94 | 0.13 | 4.20 | 8.36 | 3.69 |
| dev / middle C3-B5 (5) | 9.77 | 0.99 | 4.30 | 8.65 | 8.01 | 10.08 | 6.84 | 5.62 | 0.22 | 4.72 | 9.09 | 4.18 |
| dev / treble C6-C8 (7) | 10.95 | 2.06 | 12.21 | 10.53 | 9.74 | 10.98 | 9.68 | 8.02 | 0.30 | 6.30 | 6.93 | 7.62 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.26 is worse than 0.4.25 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.25 | 0.4.26 |
|---|---|---|---|---|
| 100 | dev | icc | 0.06 | 0.17 |
| 84 | dev | icc | 0.22 | 0.27 |
| 100 | dev | decay_db_s | 8.18 | 10.46 |
| 39 | dev | early_db | 8.04 | 9.11 |
| 64 | dev | envelope_db | 3.82 | 4.72 |
| 64 | dev | icc | 0.19 | 0.22 |
| 39 | dev | envelope_db | 3.41 | 4.20 |
| 64 | dev | attack_db | 7.86 | 8.65 |
| 64 | dev | level_db | 3.40 | 4.18 |
| 105 | dev | partial_db | 12.04 | 12.64 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (26.6328 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 17 | 10.6314 | 10.3539 | -0.2775 | 0 | 0 | 0 |
| dev | tuning_cents | 17 | 2.5445 | 1.7312 | -0.8133 | 0 | 0 | 0 |
| dev | decay_db_s | 17 | 7.2586 | 7.0697 | -0.1889 | 0 | 0 | 0 |
| dev | attack_db | 17 | 9.3585 | 9.5881 | 0.2296 | 0 | 0 | 0 |
| dev | early_db | 17 | 8.7664 | 9.0485 | 0.2820 | 0 | 0 | 0 |
| dev | sustain_db | 17 | 10.4825 | 10.1596 | -0.3229 | 0 | 0 | 0 |
| dev | noise_db | 17 | 9.5995 | 9.3370 | -0.2625 | 0 | 0 | 0 |
| dev | ild_db | 17 | 5.9768 | 6.1102 | 0.1334 | 0 | 0 | 0 |
| dev | icc | 17 | 0.1957 | 0.2267 | 0.0310 | 0 | 0 | 0 |
| dev | envelope_db | 17 | 4.9361 | 5.2188 | 0.2827 | 0 | 0 | 0 |
| dev | rise_ms | 17 | 8.2845 | 7.9862 | -0.2983 | 0 | 0 | 0 |
| dev | level_db | 17 | 5.6056 | 7.2380 | 1.6324 | 0 | 0 | 0 |
| train | partial_db | 60 | 7.7300 | 7.6747 | -0.0553 | 0 | 0 | 1 |
| train | tuning_cents | 60 | 0.5863 | 0.5341 | -0.0521 | 0 | 0 | 1 |
| train | decay_db_s | 54 | 3.9863 | 3.8903 | -0.0960 | 0 | 0 | 7 |
| train | attack_db | 61 | 7.5336 | 7.5280 | -0.0056 | 0 | 0 | 0 |
| train | early_db | 61 | 7.4106 | 7.4002 | -0.0104 | 0 | 0 | 0 |
| train | sustain_db | 59 | 7.8677 | 7.8725 | 0.0048 | 0 | 0 | 2 |
| train | noise_db | 61 | 8.1335 | 8.1417 | 0.0082 | 0 | 0 | 0 |
| train | ild_db | 54 | 1.7350 | 1.7350 | -0.0001 | 0 | 0 | 7 |
| train | icc | 54 | 0.0930 | 0.0931 | 0.0000 | 0 | 0 | 7 |
| train | envelope_db | 61 | 2.5925 | 2.5877 | -0.0048 | 0 | 0 | 0 |
| train | rise_ms | 61 | 12.0654 | 12.0575 | -0.0079 | 0 | 0 | 0 |
| train | level_db | 61 | 0.8764 | 2.0636 | 1.1872 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 100 | dev | icc | 1 | 0.0596 | 0.1663 | 0.1067 |
| 64 | dev | level_db | 5 | 3.4041 | 5.9633 | 2.5592 |
| 94 | train | level_db | 4 | 0.4504 | 2.5489 | 2.0985 |
| 105 | dev | level_db | 1 | 8.0612 | 9.7745 | 1.7133 |
| 29 | train | level_db | 5 | 0.2263 | 1.7980 | 1.5718 |
| 79 | train | level_db | 4 | 0.0848 | 1.6463 | 1.5614 |
| 74 | train | level_db | 5 | 0.1552 | 1.6915 | 1.5363 |
| 89 | train | level_db | 5 | 0.1737 | 1.6696 | 1.4960 |
| 69 | train | level_db | 5 | 0.2106 | 1.6361 | 1.4255 |
| 39 | dev | level_db | 5 | 4.0858 | 5.4767 | 1.3909 |
| 84 | dev | icc | 5 | 0.2156 | 0.2650 | 0.0495 |
| 49 | train | level_db | 5 | 0.3193 | 1.5273 | 1.2080 |
| 100 | dev | level_db | 1 | 7.1620 | 8.3248 | 1.1628 |
| 100 | dev | decay_db_s | 1 | 8.1758 | 10.4630 | 2.2873 |
| 44 | train | level_db | 5 | 1.4870 | 2.5656 | 1.0786 |
| 39 | dev | early_db | 5 | 8.0403 | 9.1147 | 1.0744 |
| 84 | dev | level_db | 5 | 8.5245 | 9.5494 | 1.0249 |
| 34 | train | level_db | 5 | 0.5322 | 1.5326 | 1.0004 |
| 59 | train | level_db | 5 | 0.3296 | 1.3100 | 0.9804 |
| 64 | dev | envelope_db | 5 | 3.8239 | 4.7156 | 0.8916 |
| 64 | dev | icc | 5 | 0.1899 | 0.2233 | 0.0334 |
| 99 | train | level_db | 4 | 3.6174 | 4.4469 | 0.8295 |
| 39 | dev | envelope_db | 5 | 3.4064 | 4.2027 | 0.7963 |
| 64 | dev | attack_db | 5 | 7.8618 | 8.6510 | 0.7892 |
| 105 | dev | partial_db | 1 | 12.0389 | 12.6392 | 0.6003 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
