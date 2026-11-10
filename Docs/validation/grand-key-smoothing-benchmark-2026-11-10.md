# Recording benchmark: 0.4.32 against 0.4.31

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.31

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.62 | 0.16 | 1.85 | 4.28 | 4.02 | 4.64 | 5.60 | 0.80 | 0.06 | 1.89 | 3.61 | 0.50 |
| dev (156) | 5.35 | 0.90 | 2.10 | 4.65 | 4.42 | 5.33 | 5.25 | 2.25 | 0.10 | 2.60 | 4.71 | 0.96 |
| train / bass A0-B2 (84) | 4.69 | 0.04 | 0.43 | 4.55 | 3.85 | 3.68 | 5.89 | 0.40 | 0.03 | 1.80 | 4.03 | 0.40 |
| train / middle C3-B5 (108) | 4.90 | 0.07 | 1.44 | 3.89 | 3.90 | 3.48 | 5.79 | 0.70 | 0.05 | 0.82 | 4.13 | 0.35 |
| train / treble C6-C8 (84) | 4.20 | 0.40 | 3.92 | 4.52 | 4.33 | 7.09 | 5.11 | 1.36 | 0.09 | 3.36 | 2.53 | 0.79 |
| dev / bass A0-B2 (44) | 5.48 | 1.27 | 1.09 | 4.81 | 4.01 | 3.87 | 5.11 | 1.35 | 0.05 | 2.66 | 5.37 | 0.99 |
| dev / middle C3-B5 (68) | 6.30 | 0.64 | 2.47 | 4.51 | 4.70 | 5.60 | 5.41 | 3.63 | 0.11 | 1.88 | 6.01 | 0.87 |
| dev / treble C6-C8 (44) | 3.76 | 0.95 | 2.55 | 4.71 | 4.40 | 6.36 | 5.13 | 0.95 | 0.15 | 3.64 | 2.05 | 1.07 |

## 0.4.32

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.51 | 0.17 | 1.85 | 4.30 | 4.02 | 4.61 | 5.62 | 1.48 | 0.06 | 1.94 | 3.60 | 1.10 |
| dev (156) | 5.28 | 0.91 | 2.09 | 4.66 | 4.42 | 5.32 | 5.26 | 2.61 | 0.10 | 2.62 | 4.51 | 1.11 |
| train / bass A0-B2 (84) | 4.72 | 0.04 | 0.43 | 4.56 | 3.86 | 3.70 | 5.83 | 0.74 | 0.03 | 1.80 | 3.98 | 0.99 |
| train / middle C3-B5 (108) | 4.73 | 0.08 | 1.47 | 3.90 | 3.88 | 3.48 | 5.86 | 2.11 | 0.05 | 0.97 | 4.13 | 1.06 |
| train / treble C6-C8 (84) | 4.03 | 0.41 | 3.89 | 4.55 | 4.36 | 6.98 | 5.14 | 1.42 | 0.09 | 3.32 | 2.54 | 1.25 |
| dev / bass A0-B2 (44) | 5.48 | 1.26 | 1.09 | 4.82 | 4.02 | 3.87 | 5.11 | 1.51 | 0.05 | 2.65 | 4.65 | 1.03 |
| dev / middle C3-B5 (68) | 6.20 | 0.65 | 2.49 | 4.51 | 4.67 | 5.60 | 5.42 | 4.28 | 0.11 | 1.95 | 6.03 | 1.13 |
| dev / treble C6-C8 (44) | 3.66 | 0.95 | 2.49 | 4.72 | 4.43 | 6.32 | 5.16 | 1.04 | 0.15 | 3.63 | 2.01 | 1.15 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.32 is worse than 0.4.31 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.31 | 0.4.32 |
|---|---|---|---|---|
| 66 | dev | ild_db | 0.43 | 4.24 |
| 66 | train | ild_db | 0.48 | 4.20 |
| 69 | train | ild_db | 0.48 | 3.32 |
| 81 | train | ild_db | 0.58 | 3.35 |
| 69 | dev | ild_db | 0.48 | 3.12 |
| 81 | dev | ild_db | 0.49 | 3.10 |
| 48 | dev | ild_db | 0.63 | 3.10 |
| 36 | dev | rise_ms | 3.88 | 8.71 |
| 48 | train | ild_db | 0.74 | 3.09 |
| 60 | train | level_db | 0.49 | 2.14 |
| 45 | dev | ild_db | 0.29 | 1.83 |
| 45 | train | ild_db | 0.38 | 1.92 |
| 84 | dev | ild_db | 1.58 | 3.07 |
| 60 | dev | level_db | 0.58 | 2.07 |
| 57 | train | level_db | 0.74 | 2.22 |
| 42 | dev | level_db | 0.52 | 1.99 |
| 42 | train | level_db | 0.33 | 1.80 |
| 57 | dev | level_db | 0.58 | 1.79 |
| 81 | train | level_db | 0.29 | 1.44 |
| 78 | dev | level_db | 0.39 | 1.42 |
| 78 | train | level_db | 0.20 | 1.23 |
| 57 | train | noise_db | 8.61 | 9.63 |
| 81 | dev | level_db | 0.64 | 1.59 |
| 93 | train | level_db | 0.24 | 1.19 |
| 84 | train | ild_db | 1.98 | 2.85 |
| 96 | train | level_db | 0.46 | 1.26 |
| 30 | train | level_db | 0.13 | 0.90 |
| 57 | dev | noise_db | 7.26 | 7.99 |
| 60 | train | ild_db | 1.04 | 1.76 |
| 102 | dev | ild_db | 1.64 | 2.30 |
| 30 | dev | level_db | 0.25 | 0.84 |
| 60 | dev | ild_db | 0.91 | 1.47 |
| 24 | train | level_db | 0.73 | 1.29 |
| 102 | train | ild_db | 1.52 | 2.07 |
| 66 | train | rise_ms | 5.88 | 6.96 |
| 102 | train | level_db | 0.45 | 0.99 |
| 33 | train | level_db | 0.83 | 1.36 |
| 36 | train | level_db | 0.31 | 0.83 |
| 24 | dev | ild_db | 0.32 | 0.82 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (25.7989 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 5.3548 | 5.2840 | -0.0709 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 0.9046 | 0.9053 | 0.0007 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 2.0981 | 2.0891 | -0.0090 | 0 | 0 | 1 |
| dev | attack_db | 156 | 4.6538 | 4.6574 | 0.0036 | 0 | 0 | 0 |
| dev | early_db | 156 | 4.4210 | 4.4185 | -0.0025 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 5.3256 | 5.3161 | -0.0095 | 0 | 0 | 0 |
| dev | noise_db | 153 | 5.2475 | 5.2609 | 0.0134 | 0 | 0 | 3 |
| dev | ild_db | 154 | 2.2450 | 2.6084 | 0.3634 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1022 | 0.1022 | 0.0000 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 2.5958 | 2.6225 | 0.0266 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 4.7106 | 4.5051 | -0.2055 | 0 | 0 | 0 |
| dev | level_db | 156 | 0.9610 | 1.0837 | 0.1227 | 0 | 0 | 0 |
| train | partial_db | 276 | 4.6223 | 4.5122 | -0.1100 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 0.1627 | 0.1685 | 0.0058 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 1.8519 | 1.8534 | 0.0015 | 0 | 0 | 5 |
| train | attack_db | 276 | 4.2822 | 4.3003 | 0.0182 | 0 | 0 | 0 |
| train | early_db | 276 | 4.0159 | 4.0204 | 0.0045 | 0 | 0 | 0 |
| train | sustain_db | 276 | 4.6384 | 4.6108 | -0.0276 | 0 | 0 | 0 |
| train | noise_db | 262 | 5.5748 | 5.6220 | 0.0472 | 1 | 0 | 13 |
| train | ild_db | 270 | 0.7960 | 1.4849 | 0.6890 | 0 | 0 | 6 |
| train | icc | 270 | 0.0557 | 0.0562 | 0.0005 | 0 | 0 | 6 |
| train | envelope_db | 276 | 1.8905 | 1.9382 | 0.0476 | 0 | 0 | 0 |
| train | rise_ms | 276 | 3.6139 | 3.5984 | -0.0155 | 0 | 0 | 0 |
| train | level_db | 276 | 0.5005 | 1.1137 | 0.6132 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 66 | dev | ild_db | 4 | 0.4296 | 4.2350 | 3.8055 |
| 66 | train | ild_db | 12 | 0.4781 | 4.2006 | 3.7225 |
| 69 | train | ild_db | 12 | 0.4838 | 3.3198 | 2.8360 |
| 81 | train | ild_db | 12 | 0.5844 | 3.3501 | 2.7658 |
| 69 | dev | ild_db | 4 | 0.4792 | 3.1162 | 2.6370 |
| 81 | dev | ild_db | 4 | 0.4896 | 3.0976 | 2.6080 |
| 48 | dev | ild_db | 4 | 0.6298 | 3.1034 | 2.4736 |
| 36 | dev | rise_ms | 4 | 3.8802 | 8.7135 | 4.8333 |
| 48 | train | ild_db | 12 | 0.7388 | 3.0897 | 2.3509 |
| 57 | train | level_db | 12 | 0.7432 | 2.3574 | 1.6142 |
| 45 | dev | ild_db | 4 | 0.2907 | 1.8267 | 1.5359 |
| 60 | train | level_db | 12 | 0.4862 | 2.0221 | 1.5359 |
| 45 | train | ild_db | 12 | 0.3840 | 1.9197 | 1.5357 |
| 84 | dev | ild_db | 4 | 1.5839 | 3.0674 | 1.4835 |
| 60 | dev | level_db | 4 | 0.5843 | 1.9289 | 1.3445 |
| 57 | dev | level_db | 4 | 0.5843 | 1.9262 | 1.3419 |
| 42 | dev | level_db | 4 | 0.5167 | 1.8575 | 1.3408 |
| 42 | train | level_db | 12 | 0.3285 | 1.6643 | 1.3359 |
| 81 | train | level_db | 12 | 0.2863 | 1.5803 | 1.2940 |
| 57 | train | noise_db | 12 | 8.6088 | 9.6324 | 1.0236 |
| 81 | dev | level_db | 4 | 0.6371 | 1.6566 | 1.0195 |
| 96 | train | level_db | 12 | 0.4557 | 1.4009 | 0.9452 |
| 78 | dev | level_db | 4 | 0.3850 | 1.2848 | 0.8998 |
| 78 | train | level_db | 12 | 0.1994 | 1.0909 | 0.8915 |
| 84 | train | ild_db | 12 | 1.9792 | 2.8530 | 0.8737 |
| 93 | train | level_db | 12 | 0.2422 | 1.0528 | 0.8106 |
| 57 | dev | noise_db | 4 | 7.2577 | 7.9926 | 0.7349 |
| 60 | train | ild_db | 12 | 1.0436 | 1.7643 | 0.7208 |
| 30 | train | level_db | 12 | 0.1294 | 0.7904 | 0.6610 |
| 102 | dev | ild_db | 4 | 1.6443 | 2.3041 | 0.6598 |
| 36 | train | level_db | 12 | 0.3119 | 0.9636 | 0.6517 |
| 60 | dev | ild_db | 4 | 0.9068 | 1.4702 | 0.5634 |
| 102 | train | ild_db | 12 | 1.5203 | 2.0747 | 0.5544 |
| 66 | train | rise_ms | 12 | 5.8767 | 6.9618 | 1.0851 |
| 24 | train | level_db | 12 | 0.7276 | 1.2683 | 0.5407 |
| 54 | train | level_db | 12 | 0.2071 | 0.7406 | 0.5335 |
| 36 | dev | level_db | 4 | 0.1728 | 0.7055 | 0.5328 |
| 96 | dev | level_db | 4 | 0.7487 | 1.2567 | 0.5080 |
| 24 | dev | ild_db | 4 | 0.3184 | 0.8245 | 0.5061 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| A1v1 | 33 | train | noise_db | lost | 11.6854 | - |
