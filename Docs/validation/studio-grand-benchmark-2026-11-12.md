# Recording benchmark: 2.9.0 Studio Grand against 2.8.0 Concert Grand

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.8.0 Concert Grand

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

## 2.9.0 Studio Grand

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.05 | 2.23 | 4.46 | 7.11 | 7.42 | 9.68 | 7.20 | 6.05 | 0.19 | 4.24 | 11.45 | 2.24 |
| dev (156) | 7.73 | 2.02 | 3.69 | 6.78 | 7.06 | 8.78 | 7.01 | 6.08 | 0.18 | 3.94 | 19.66 | 2.06 |
| train / bass A0-B2 (84) | 9.84 | 2.99 | 2.87 | 7.41 | 7.49 | 8.51 | 6.47 | 5.93 | 0.21 | 3.55 | 15.68 | 2.02 |
| train / middle C3-B5 (108) | 6.49 | 1.45 | 3.75 | 6.16 | 6.88 | 7.94 | 7.36 | 5.29 | 0.19 | 4.29 | 12.98 | 1.64 |
| train / treble C6-C8 (84) | 8.24 | 2.47 | 7.13 | 8.04 | 8.05 | 13.08 | 7.73 | 7.23 | 0.16 | 4.86 | 5.25 | 3.25 |
| dev / bass A0-B2 (44) | 9.73 | 2.52 | 2.46 | 7.17 | 6.99 | 7.99 | 6.88 | 5.85 | 0.22 | 3.06 | 36.98 | 2.34 |
| dev / middle C3-B5 (68) | 7.02 | 1.39 | 3.45 | 6.26 | 7.12 | 7.42 | 7.25 | 5.89 | 0.18 | 3.97 | 18.62 | 1.42 |
| dev / treble C6-C8 (44) | 6.82 | 2.49 | 5.34 | 7.20 | 7.03 | 11.68 | 6.79 | 6.65 | 0.15 | 4.76 | 3.93 | 2.77 |

## Independent-sample regressions (legacy)

Every note and role where 2.9.0 Studio Grand is worse than 2.8.0 Concert Grand by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.8.0 Concert Grand | 2.9.0 Studio Grand |
|---|---|---|---|---|
| 27 | dev | rise_ms | 24.29 | 73.94 |
| 24 | dev | rise_ms | 2.87 | 33.69 |
| 24 | train | rise_ms | 2.88 | 33.70 |
| 90 | dev | ild_db | 3.12 | 14.89 |
| 90 | train | ild_db | 3.17 | 14.86 |
| 75 | dev | rise_ms | 3.51 | 22.65 |
| 36 | dev | rise_ms | 11.21 | 28.40 |
| 51 | dev | rise_ms | 12.28 | 27.15 |
| 81 | train | rise_ms | 1.72 | 16.36 |
| 36 | train | rise_ms | 12.92 | 26.94 |
| 81 | dev | rise_ms | 2.13 | 15.07 |
| 105 | train | ild_db | 2.68 | 8.84 |
| 72 | dev | rise_ms | 0.87 | 13.20 |
| 96 | dev | sustain_db | 4.91 | 11.02 |
| 72 | train | rise_ms | 1.15 | 12.83 |
| 84 | train | sustain_db | 11.03 | 16.50 |
| 93 | dev | ild_db | 0.78 | 6.00 |
| 93 | train | ild_db | 0.81 | 6.03 |
| 84 | dev | sustain_db | 11.83 | 16.69 |
| 30 | dev | partial_db | 7.93 | 12.45 |
| 96 | train | sustain_db | 5.92 | 10.41 |
| 105 | dev | ild_db | 1.82 | 6.26 |
| 96 | train | ild_db | 2.29 | 6.57 |
| 51 | dev | early_db | 5.21 | 9.39 |
| 99 | dev | ild_db | 2.13 | 6.23 |
| 96 | dev | ild_db | 2.39 | 6.46 |
| 21 | train | early_db | 4.71 | 8.53 |
| 30 | train | partial_db | 8.14 | 11.87 |
| 42 | train | ild_db | 4.05 | 7.73 |
| 21 | dev | early_db | 4.52 | 8.20 |
| 36 | dev | sustain_db | 7.18 | 10.85 |
| 30 | dev | tuning_cents | 1.33 | 4.99 |
| 21 | train | sustain_db | 7.38 | 10.98 |
| 42 | dev | ild_db | 3.96 | 7.55 |
| 21 | dev | sustain_db | 7.25 | 10.79 |
| 30 | train | tuning_cents | 1.40 | 4.93 |
| 51 | dev | noise_db | 6.28 | 9.79 |
| 42 | dev | early_db | 4.36 | 7.84 |
| 36 | train | sustain_db | 7.52 | 10.98 |
| 45 | train | ild_db | 5.27 | 8.69 |
| 30 | dev | sustain_db | 5.53 | 8.92 |
| 45 | dev | ild_db | 5.22 | 8.45 |
| 30 | train | sustain_db | 5.96 | 9.16 |
| 42 | train | early_db | 4.89 | 8.08 |
| 21 | train | attack_db | 5.27 | 8.46 |
| 51 | dev | attack_db | 5.03 | 8.20 |
| 30 | dev | attack_db | 5.71 | 8.85 |
| 54 | dev | early_db | 5.53 | 8.67 |
| 33 | dev | rise_ms | 7.26 | 13.44 |
| 21 | dev | attack_db | 4.60 | 7.68 |
| 51 | dev | partial_db | 6.52 | 9.59 |
| 48 | train | sustain_db | 7.93 | 10.92 |
| 30 | train | early_db | 5.55 | 8.54 |
| 30 | train | attack_db | 6.10 | 9.09 |
| 54 | train | early_db | 5.44 | 8.40 |
| 69 | train | rise_ms | 3.64 | 9.55 |
| 48 | train | early_db | 4.66 | 7.61 |
| 48 | dev | early_db | 4.46 | 7.39 |
| 30 | dev | early_db | 5.25 | 8.18 |
| 81 | dev | envelope_db | 2.33 | 5.23 |
| 21 | dev | icc | 0.20 | 0.32 |
| 108 | dev | sustain_db | 19.40 | 22.28 |
| 81 | train | envelope_db | 2.18 | 5.07 |
| 48 | dev | sustain_db | 7.81 | 10.70 |
| 21 | train | icc | 0.21 | 0.32 |
| 54 | dev | partial_db | 6.15 | 8.99 |
| 54 | train | partial_db | 6.07 | 8.81 |
| 84 | train | ild_db | 3.43 | 6.09 |
| 105 | train | decay_db_s | 6.20 | 11.50 |
| 96 | dev | envelope_db | 4.64 | 7.16 |
| 81 | dev | sustain_db | 5.38 | 7.87 |
| 24 | train | sustain_db | 6.25 | 8.67 |
| 81 | train | sustain_db | 6.09 | 8.46 |
| 33 | train | rise_ms | 9.05 | 13.77 |
| 84 | dev | ild_db | 3.13 | 5.47 |
| 60 | train | level_db | 0.79 | 3.12 |
| 24 | dev | sustain_db | 6.38 | 8.70 |
| 36 | train | early_db | 5.67 | 7.99 |
| 60 | dev | level_db | 0.85 | 3.14 |
| 54 | dev | noise_db | 10.25 | 12.51 |
| 36 | dev | early_db | 5.41 | 7.67 |
| 108 | dev | partial_db | 9.56 | 11.81 |
| 96 | train | envelope_db | 4.49 | 6.73 |
| 51 | dev | icc | 0.10 | 0.19 |
| 90 | dev | level_db | 0.66 | 2.80 |
| 90 | dev | attack_db | 5.74 | 7.87 |
| 54 | dev | attack_db | 5.70 | 7.79 |
| 108 | train | sustain_db | 19.23 | 21.28 |
| 54 | train | noise_db | 9.79 | 11.83 |
| 90 | train | attack_db | 5.92 | 7.96 |
| 60 | dev | rise_ms | 5.61 | 9.64 |
| 69 | dev | rise_ms | 3.96 | 7.98 |
| 108 | train | partial_db | 10.27 | 12.28 |
| 24 | train | early_db | 5.21 | 7.18 |
| 90 | train | early_db | 5.52 | 7.47 |
| 51 | dev | sustain_db | 6.24 | 8.11 |
| 54 | train | attack_db | 5.72 | 7.59 |
| 90 | dev | early_db | 5.37 | 7.23 |
| 24 | dev | early_db | 5.26 | 7.11 |
| 105 | dev | decay_db_s | 7.51 | 11.20 |
| 96 | dev | early_db | 4.92 | 6.75 |
| 42 | train | attack_db | 5.88 | 7.68 |
| 90 | dev | noise_db | 6.12 | 7.87 |
| 33 | dev | partial_db | 9.91 | 11.65 |
| 42 | dev | attack_db | 5.42 | 7.14 |
| 84 | dev | envelope_db | 3.44 | 5.12 |
| 108 | dev | decay_db_s | 10.58 | 13.92 |
| 96 | dev | level_db | 1.96 | 3.63 |
| 96 | train | early_db | 5.53 | 7.18 |
| 90 | train | level_db | 1.16 | 2.81 |
| 33 | train | tuning_cents | 2.42 | 4.05 |
| 102 | dev | partial_db | 6.99 | 8.61 |
| 84 | train | envelope_db | 3.47 | 5.08 |
| 54 | dev | tuning_cents | 0.86 | 2.47 |
| 54 | train | tuning_cents | 0.89 | 2.45 |
| 54 | dev | envelope_db | 2.03 | 3.59 |
| 81 | dev | early_db | 6.37 | 7.90 |
| 48 | train | partial_db | 5.99 | 7.52 |
| 42 | dev | sustain_db | 6.25 | 7.78 |
| 81 | train | early_db | 6.44 | 7.96 |
| 96 | train | level_db | 2.51 | 4.01 |
| 90 | train | noise_db | 6.21 | 7.70 |
| 96 | train | partial_db | 7.58 | 9.05 |
| 54 | dev | ild_db | 4.03 | 5.49 |
| 42 | train | sustain_db | 6.55 | 8.01 |
| 48 | dev | partial_db | 5.79 | 7.25 |
| 48 | dev | tuning_cents | 1.50 | 2.94 |
| 102 | train | partial_db | 7.95 | 9.38 |
| 99 | dev | level_db | 1.19 | 2.59 |
| 21 | train | noise_db | 6.22 | 7.60 |
| 54 | train | ild_db | 4.04 | 5.41 |
| 102 | dev | ild_db | 3.34 | 4.72 |
| 30 | train | ild_db | 4.20 | 5.57 |
| 30 | dev | ild_db | 4.16 | 5.53 |
| 81 | dev | attack_db | 5.26 | 6.62 |
| 33 | dev | tuning_cents | 2.72 | 4.01 |
| 54 | train | envelope_db | 2.21 | 3.49 |
| 33 | train | partial_db | 10.35 | 11.63 |
| 108 | dev | icc | 0.08 | 0.13 |
| 48 | train | tuning_cents | 1.56 | 2.80 |
| 33 | train | ild_db | 3.97 | 5.19 |
| 81 | train | partial_db | 4.36 | 5.58 |
| 21 | train | partial_db | 12.12 | 13.30 |
| 36 | dev | noise_db | 3.15 | 4.33 |
| 33 | dev | ild_db | 3.91 | 5.08 |
| 84 | dev | decay_db_s | 5.41 | 7.74 |
| 93 | dev | level_db | 1.10 | 2.24 |
| 84 | train | decay_db_s | 5.27 | 7.54 |
| 108 | dev | ild_db | 1.02 | 2.14 |
| 102 | dev | tuning_cents | 2.78 | 3.88 |
| 27 | dev | sustain_db | 6.27 | 7.36 |
| 108 | train | decay_db_s | 8.80 | 10.97 |
| 36 | train | envelope_db | 6.32 | 7.40 |
| 81 | train | attack_db | 5.65 | 6.71 |
| 36 | dev | envelope_db | 6.44 | 7.49 |
| 24 | dev | noise_db | 6.16 | 7.21 |
| 102 | train | tuning_cents | 2.91 | 3.94 |
| 21 | dev | partial_db | 12.44 | 13.45 |
| 36 | train | decay_db_s | 2.04 | 4.02 |
| 48 | dev | envelope_db | 3.26 | 4.25 |
| 81 | dev | partial_db | 4.50 | 5.48 |
| 48 | train | envelope_db | 3.36 | 4.34 |
| 102 | train | ild_db | 3.29 | 4.26 |
| 24 | dev | icc | 0.14 | 0.18 |
| 57 | train | noise_db | 12.03 | 12.99 |
| 108 | train | ild_db | 0.95 | 1.90 |
| 36 | dev | decay_db_s | 2.02 | 3.91 |
| 24 | train | icc | 0.14 | 0.18 |
| 90 | train | partial_db | 5.94 | 6.84 |
| 45 | train | attack_db | 6.31 | 7.19 |
| 42 | dev | partial_db | 6.06 | 6.91 |
| 69 | dev | early_db | 5.18 | 6.02 |
| 60 | train | noise_db | 6.66 | 7.48 |
| 36 | train | partial_db | 10.07 | 10.89 |
| 54 | dev | sustain_db | 5.86 | 6.68 |
| 66 | dev | sustain_db | 4.38 | 5.18 |
| 36 | dev | partial_db | 9.99 | 10.78 |
| 54 | train | sustain_db | 6.06 | 6.85 |
| 81 | dev | noise_db | 6.77 | 7.55 |
| 51 | dev | tuning_cents | 0.67 | 1.45 |
| 36 | train | tuning_cents | 3.33 | 4.09 |
| 36 | dev | level_db | 0.46 | 1.20 |
| 27 | dev | icc | 0.21 | 0.24 |
| 81 | train | noise_db | 7.40 | 8.13 |
| 45 | dev | attack_db | 6.03 | 6.76 |
| 36 | train | level_db | 0.96 | 1.68 |
| 45 | dev | noise_db | 6.33 | 7.05 |
| 45 | train | icc | 0.14 | 0.17 |
| 21 | dev | noise_db | 5.39 | 6.10 |
| 90 | dev | sustain_db | 10.65 | 11.36 |
| 45 | train | decay_db_s | 1.90 | 3.31 |
| 48 | dev | attack_db | 5.95 | 6.63 |
| 24 | train | attack_db | 7.08 | 7.75 |
| 30 | train | icc | 0.19 | 0.21 |
| 69 | dev | sustain_db | 5.73 | 6.40 |
| 24 | dev | attack_db | 6.50 | 7.16 |
| 36 | dev | tuning_cents | 3.55 | 4.20 |
| 96 | dev | attack_db | 5.36 | 6.01 |
| 45 | dev | decay_db_s | 1.96 | 3.24 |
| 66 | dev | attack_db | 4.14 | 4.77 |
| 66 | dev | icc | 0.12 | 0.15 |
| 27 | dev | noise_db | 7.51 | 8.14 |
| 66 | dev | early_db | 4.59 | 5.21 |
| 66 | train | sustain_db | 4.57 | 5.18 |
| 60 | train | ild_db | 8.35 | 8.96 |
| 69 | train | early_db | 5.43 | 6.04 |
| 42 | dev | tuning_cents | 0.99 | 1.59 |
| 45 | dev | icc | 0.15 | 0.17 |
| 42 | train | tuning_cents | 0.96 | 1.55 |
| 66 | train | icc | 0.12 | 0.15 |
| 105 | dev | sustain_db | 12.48 | 13.06 |
| 60 | dev | ild_db | 8.44 | 9.00 |
| 96 | train | attack_db | 5.63 | 6.19 |
| 54 | dev | icc | 0.21 | 0.23 |
| 99 | dev | sustain_db | 8.74 | 9.29 |
| 36 | train | noise_db | 4.90 | 5.43 |
| 66 | train | early_db | 4.75 | 5.28 |
| 108 | train | icc | 0.24 | 0.26 |
| 90 | train | sustain_db | 10.48 | 10.99 |
| 66 | train | attack_db | 4.30 | 4.81 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.7883 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 7.7435 | 7.7286 | -0.0150 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.2080 | 2.0167 | -0.1913 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 3.7974 | 3.6940 | -0.1034 | 0 | 0 | 1 |
| dev | attack_db | 156 | 6.2611 | 6.7836 | 0.5225 | 0 | 0 | 0 |
| dev | early_db | 156 | 6.2933 | 7.0585 | 0.7652 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 7.8491 | 8.7818 | 0.9327 | 0 | 0 | 0 |
| dev | noise_db | 151 | 6.7377 | 7.0049 | 0.2672 | 2 | 1 | 2 |
| dev | ild_db | 154 | 5.3123 | 6.0840 | 0.7717 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1876 | 0.1843 | -0.0034 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 4.1825 | 3.9365 | -0.2459 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 12.6532 | 19.6553 | 7.0021 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.0748 | 2.1072 | 0.0324 | 0 | 0 | 0 |
| train | partial_db | 276 | 8.0669 | 8.0455 | -0.0214 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.0742 | 2.2252 | 0.1510 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 4.4968 | 4.4622 | -0.0346 | 0 | 0 | 5 |
| train | attack_db | 276 | 6.6653 | 7.1109 | 0.4455 | 0 | 0 | 0 |
| train | early_db | 276 | 6.6752 | 7.4245 | 0.7492 | 0 | 0 | 0 |
| train | sustain_db | 276 | 8.8020 | 9.6808 | 0.8788 | 0 | 0 | 0 |
| train | noise_db | 273 | 7.3528 | 7.2175 | -0.1353 | 1 | 2 | 0 |
| train | ild_db | 270 | 5.0134 | 6.0475 | 1.0341 | 0 | 0 | 6 |
| train | icc | 270 | 0.1973 | 0.1888 | -0.0085 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.3835 | 4.2363 | -0.1472 | 0 | 0 | 0 |
| train | rise_ms | 276 | 14.9971 | 11.4520 | -3.5451 | 0 | 0 | 0 |
| train | level_db | 276 | 2.3395 | 2.3304 | -0.0091 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 27 | dev | rise_ms | 16 | 24.2865 | 73.9388 | 49.6523 |
| 24 | dev | rise_ms | 4 | 2.8698 | 33.6927 | 30.8229 |
| 24 | train | rise_ms | 12 | 2.8802 | 33.7014 | 30.8212 |
| 90 | dev | ild_db | 4 | 3.1216 | 14.8873 | 11.7657 |
| 90 | train | ild_db | 12 | 3.1677 | 14.8558 | 11.6881 |
| 75 | dev | rise_ms | 16 | 3.5052 | 22.6523 | 19.1471 |
| 36 | dev | rise_ms | 4 | 11.2135 | 28.3958 | 17.1823 |
| 51 | dev | rise_ms | 16 | 12.2812 | 27.1536 | 14.8724 |
| 81 | train | rise_ms | 12 | 1.7205 | 16.3646 | 14.6441 |
| 36 | train | rise_ms | 12 | 12.9184 | 26.9358 | 14.0174 |
| 81 | dev | rise_ms | 4 | 2.1302 | 15.0677 | 12.9375 |
| 105 | train | ild_db | 11 | 2.6757 | 8.8410 | 6.1653 |
| 72 | dev | rise_ms | 4 | 0.8750 | 13.2031 | 12.3281 |
| 96 | dev | sustain_db | 4 | 4.9146 | 11.0226 | 6.1080 |
| 72 | train | rise_ms | 12 | 1.1493 | 12.8316 | 11.6823 |
| 84 | train | sustain_db | 12 | 11.0255 | 16.4977 | 5.4722 |
| 93 | dev | ild_db | 4 | 0.7801 | 6.0037 | 5.2236 |
| 93 | train | ild_db | 12 | 0.8077 | 6.0269 | 5.2192 |
| 84 | dev | sustain_db | 4 | 11.8265 | 16.6878 | 4.8613 |
| 30 | dev | partial_db | 4 | 7.9331 | 12.4538 | 4.5207 |
| 96 | train | sustain_db | 12 | 5.9205 | 10.4056 | 4.4850 |
| 105 | dev | ild_db | 4 | 1.8220 | 6.2568 | 4.4348 |
| 96 | train | ild_db | 12 | 2.2858 | 6.5671 | 4.2813 |
| 51 | dev | early_db | 16 | 5.2147 | 9.3925 | 4.1778 |
| 99 | dev | ild_db | 16 | 2.1309 | 6.2324 | 4.1015 |
| 96 | dev | ild_db | 4 | 2.3906 | 6.4599 | 4.0693 |
| 51 | dev | noise_db | 13 | 5.8596 | 9.7912 | 3.9316 |
| 21 | train | early_db | 12 | 4.7058 | 8.5279 | 3.8221 |
| 30 | train | partial_db | 12 | 8.1392 | 11.8694 | 3.7302 |
| 42 | train | ild_db | 12 | 4.0539 | 7.7312 | 3.6772 |
| 21 | dev | early_db | 4 | 4.5205 | 8.1959 | 3.6753 |
| 36 | dev | sustain_db | 4 | 7.1755 | 10.8486 | 3.6731 |
| 30 | dev | tuning_cents | 4 | 1.3295 | 4.9912 | 3.6617 |
| 21 | train | sustain_db | 12 | 7.3755 | 10.9762 | 3.6007 |
| 42 | dev | ild_db | 4 | 3.9571 | 7.5450 | 3.5880 |
| 21 | dev | sustain_db | 4 | 7.2521 | 10.7912 | 3.5391 |
| 30 | train | tuning_cents | 12 | 1.3972 | 4.9344 | 3.5371 |
| 42 | dev | early_db | 4 | 4.3589 | 7.8385 | 3.4795 |
| 36 | train | sustain_db | 12 | 7.5173 | 10.9849 | 3.4676 |
| 45 | train | ild_db | 12 | 5.2687 | 8.6932 | 3.4245 |
| 30 | dev | sustain_db | 4 | 5.5308 | 8.9161 | 3.3852 |
| 45 | dev | ild_db | 4 | 5.2182 | 8.4487 | 3.2306 |
| 30 | train | sustain_db | 12 | 5.9565 | 9.1640 | 3.2076 |
| 42 | train | early_db | 12 | 4.8922 | 8.0841 | 3.1919 |
| 21 | train | attack_db | 12 | 5.2746 | 8.4574 | 3.1828 |
| 51 | dev | attack_db | 16 | 5.0262 | 8.2013 | 3.1751 |
| 30 | dev | attack_db | 4 | 5.7067 | 8.8541 | 3.1475 |
| 54 | dev | early_db | 4 | 5.5306 | 8.6725 | 3.1419 |
| 33 | dev | rise_ms | 4 | 7.2552 | 13.4427 | 6.1875 |
| 21 | dev | attack_db | 4 | 4.5992 | 7.6770 | 3.0778 |
| 51 | dev | partial_db | 16 | 6.5155 | 9.5905 | 3.0750 |
| 48 | train | sustain_db | 12 | 7.9271 | 10.9234 | 2.9963 |
| 30 | train | early_db | 12 | 5.5456 | 8.5393 | 2.9937 |
| 30 | train | attack_db | 12 | 6.1015 | 9.0889 | 2.9874 |
| 54 | train | early_db | 12 | 5.4444 | 8.4023 | 2.9579 |
| 69 | train | rise_ms | 12 | 3.6389 | 9.5538 | 5.9149 |
| 48 | train | early_db | 12 | 4.6616 | 7.6084 | 2.9468 |
| 48 | dev | early_db | 4 | 4.4611 | 7.3921 | 2.9310 |
| 30 | dev | early_db | 4 | 5.2529 | 8.1797 | 2.9268 |
| 81 | dev | envelope_db | 4 | 2.3293 | 5.2282 | 2.8988 |
| 21 | dev | icc | 4 | 0.2031 | 0.3188 | 0.1157 |
| 108 | dev | sustain_db | 4 | 19.3958 | 22.2814 | 2.8856 |
| 81 | train | envelope_db | 12 | 2.1825 | 5.0659 | 2.8834 |
| 48 | dev | sustain_db | 4 | 7.8130 | 10.6955 | 2.8825 |
| 21 | train | icc | 12 | 0.2075 | 0.3214 | 0.1139 |
| 54 | dev | partial_db | 4 | 6.1452 | 8.9879 | 2.8427 |
| 54 | train | partial_db | 12 | 6.0650 | 8.8106 | 2.7456 |
| 90 | dev | level_db | 4 | 0.6647 | 3.3970 | 2.7323 |
| 84 | train | ild_db | 12 | 3.4280 | 6.0870 | 2.6590 |
| 105 | train | decay_db_s | 11 | 6.2046 | 11.4960 | 5.2914 |
| 96 | dev | envelope_db | 4 | 4.6379 | 7.1611 | 2.5232 |
| 81 | dev | sustain_db | 4 | 5.3819 | 7.8675 | 2.4856 |
| 24 | train | sustain_db | 12 | 6.2545 | 8.6711 | 2.4165 |
| 81 | train | sustain_db | 12 | 6.0864 | 8.4551 | 2.3687 |
| 33 | train | rise_ms | 12 | 9.0451 | 13.7656 | 4.7205 |
| 84 | dev | ild_db | 4 | 3.1268 | 5.4722 | 2.3453 |
| 24 | dev | sustain_db | 4 | 6.3801 | 8.7034 | 2.3234 |
| 36 | train | early_db | 12 | 5.6663 | 7.9861 | 2.3199 |
| 96 | dev | level_db | 4 | 1.9562 | 4.2267 | 2.2705 |
| 54 | dev | noise_db | 4 | 10.2465 | 12.5145 | 2.2680 |
| 36 | dev | early_db | 4 | 5.4103 | 7.6680 | 2.2577 |
| 108 | dev | partial_db | 4 | 9.5594 | 11.8112 | 2.2518 |
| 96 | train | envelope_db | 12 | 4.4939 | 6.7264 | 2.2325 |
| 51 | dev | icc | 16 | 0.1004 | 0.1880 | 0.0877 |
| 90 | train | level_db | 12 | 1.1638 | 3.3061 | 2.1422 |
| 90 | dev | attack_db | 4 | 5.7442 | 7.8704 | 2.1262 |
| 54 | dev | attack_db | 4 | 5.7023 | 7.7868 | 2.0845 |
| 108 | train | sustain_db | 12 | 19.2296 | 21.2814 | 2.0518 |
| 54 | train | noise_db | 12 | 9.7911 | 11.8296 | 2.0385 |
| 90 | train | attack_db | 12 | 5.9204 | 7.9566 | 2.0362 |
| 60 | dev | rise_ms | 4 | 5.6146 | 9.6354 | 4.0208 |
| 69 | dev | rise_ms | 4 | 3.9583 | 7.9792 | 4.0208 |
| 108 | train | partial_db | 12 | 10.2723 | 12.2760 | 2.0037 |
| 96 | train | level_db | 12 | 2.5059 | 4.5074 | 2.0015 |
| 24 | train | early_db | 12 | 5.2067 | 7.1767 | 1.9701 |
| 90 | train | early_db | 12 | 5.5163 | 7.4672 | 1.9509 |
| 99 | dev | level_db | 16 | 1.1895 | 3.1214 | 1.9319 |
| 51 | dev | sustain_db | 16 | 6.2415 | 8.1130 | 1.8715 |
| 54 | train | attack_db | 12 | 5.7168 | 7.5880 | 1.8712 |
| 90 | dev | early_db | 4 | 5.3667 | 7.2346 | 1.8679 |
| 24 | dev | early_db | 4 | 5.2560 | 7.1071 | 1.8511 |
| 105 | dev | decay_db_s | 4 | 7.5065 | 11.1996 | 3.6931 |
| 96 | dev | early_db | 4 | 4.9174 | 6.7528 | 1.8353 |
| 42 | train | attack_db | 12 | 5.8831 | 7.6820 | 1.7989 |
| 90 | dev | noise_db | 4 | 6.1203 | 7.8709 | 1.7506 |
| 33 | dev | partial_db | 4 | 9.9074 | 11.6533 | 1.7459 |
| 93 | dev | level_db | 4 | 1.0955 | 2.8411 | 1.7455 |
| 60 | train | level_db | 12 | 0.7917 | 2.5227 | 1.7310 |
| 42 | dev | attack_db | 4 | 5.4170 | 7.1431 | 1.7261 |
| 60 | dev | level_db | 4 | 0.8530 | 2.5439 | 1.6909 |
| 84 | dev | envelope_db | 4 | 3.4375 | 5.1186 | 1.6811 |
| 108 | dev | decay_db_s | 3 | 10.5778 | 13.9229 | 3.3451 |
| 96 | train | early_db | 12 | 5.5338 | 7.1778 | 1.6440 |
| 33 | train | tuning_cents | 12 | 2.4169 | 4.0453 | 1.6285 |
| 102 | dev | partial_db | 4 | 6.9857 | 8.6108 | 1.6251 |
| 84 | train | envelope_db | 12 | 3.4674 | 5.0812 | 1.6138 |
| 54 | dev | tuning_cents | 4 | 0.8587 | 2.4722 | 1.6135 |
| 54 | train | tuning_cents | 12 | 0.8868 | 2.4511 | 1.5643 |
| 54 | dev | envelope_db | 4 | 2.0256 | 3.5896 | 1.5640 |
| 81 | dev | early_db | 4 | 6.3676 | 7.9018 | 1.5342 |
| 48 | train | partial_db | 12 | 5.9897 | 7.5234 | 1.5337 |
| 42 | dev | sustain_db | 4 | 6.2491 | 7.7778 | 1.5287 |
| 81 | train | early_db | 12 | 6.4355 | 7.9606 | 1.5251 |
| 90 | train | noise_db | 12 | 6.2084 | 7.7047 | 1.4963 |
| 96 | train | partial_db | 12 | 7.5759 | 9.0484 | 1.4725 |
| 54 | dev | ild_db | 4 | 4.0251 | 5.4942 | 1.4690 |
| 42 | train | sustain_db | 12 | 6.5505 | 8.0114 | 1.4609 |
| 48 | dev | partial_db | 4 | 5.7946 | 7.2457 | 1.4512 |
| 48 | dev | tuning_cents | 4 | 1.5015 | 2.9365 | 1.4349 |
| 102 | train | partial_db | 12 | 7.9539 | 9.3831 | 1.4293 |
| 21 | train | noise_db | 12 | 6.2167 | 7.6031 | 1.3864 |
| 54 | train | ild_db | 12 | 4.0356 | 5.4137 | 1.3781 |
| 102 | dev | ild_db | 4 | 3.3442 | 4.7174 | 1.3732 |
| 30 | train | ild_db | 12 | 4.2044 | 5.5729 | 1.3685 |
| 30 | dev | ild_db | 4 | 4.1611 | 5.5274 | 1.3663 |
| 81 | dev | attack_db | 4 | 5.2595 | 6.6213 | 1.3618 |
| 36 | dev | level_db | 4 | 0.4627 | 1.8023 | 1.3396 |
| 36 | train | level_db | 12 | 0.9603 | 2.2820 | 1.3216 |
| 33 | dev | tuning_cents | 4 | 2.7198 | 4.0084 | 1.2885 |
| 54 | train | envelope_db | 12 | 2.2123 | 3.4917 | 1.2794 |
| 33 | train | partial_db | 12 | 10.3463 | 11.6252 | 1.2789 |
| 108 | dev | icc | 2 | 0.0771 | 0.1275 | 0.0504 |
| 48 | train | tuning_cents | 12 | 1.5612 | 2.8044 | 1.2432 |
| 33 | train | ild_db | 12 | 3.9656 | 5.1943 | 1.2287 |
| 81 | train | partial_db | 12 | 4.3629 | 5.5827 | 1.2199 |
| 21 | train | partial_db | 12 | 12.1161 | 13.3013 | 1.1852 |
| 36 | dev | noise_db | 4 | 3.1490 | 4.3297 | 1.1807 |
| 33 | dev | ild_db | 4 | 3.9134 | 5.0790 | 1.1656 |
| 84 | dev | decay_db_s | 4 | 5.4072 | 7.7374 | 2.3301 |
| 84 | train | decay_db_s | 12 | 5.2701 | 7.5357 | 2.2656 |
| 108 | dev | ild_db | 2 | 1.0212 | 2.1398 | 1.1186 |
| 102 | dev | tuning_cents | 4 | 2.7770 | 3.8757 | 1.0987 |
| 27 | dev | sustain_db | 16 | 6.2746 | 7.3633 | 1.0887 |
| 108 | train | decay_db_s | 8 | 8.7967 | 10.9689 | 2.1722 |
| 36 | train | envelope_db | 12 | 6.3172 | 7.4017 | 1.0845 |
| 81 | train | attack_db | 12 | 5.6455 | 6.7139 | 1.0684 |
| 36 | dev | envelope_db | 4 | 6.4354 | 7.4902 | 1.0548 |
| 24 | dev | noise_db | 4 | 6.1620 | 7.2128 | 1.0509 |
| 102 | train | tuning_cents | 12 | 2.9149 | 3.9392 | 1.0243 |
| 21 | dev | partial_db | 4 | 12.4398 | 13.4536 | 1.0138 |
| 36 | train | decay_db_s | 12 | 2.0423 | 4.0220 | 1.9797 |
| 48 | dev | envelope_db | 4 | 3.2571 | 4.2453 | 0.9882 |
| 81 | dev | partial_db | 4 | 4.4963 | 5.4816 | 0.9853 |
| 48 | train | envelope_db | 12 | 3.3550 | 4.3356 | 0.9806 |
| 102 | train | ild_db | 12 | 3.2906 | 4.2644 | 0.9738 |
| 24 | dev | icc | 4 | 0.1420 | 0.1804 | 0.0384 |
| 57 | train | noise_db | 12 | 12.0332 | 12.9919 | 0.9586 |
| 108 | train | ild_db | 7 | 0.9493 | 1.8995 | 0.9502 |
| 36 | dev | decay_db_s | 4 | 2.0212 | 3.9099 | 1.8887 |
| 24 | train | icc | 12 | 0.1417 | 0.1793 | 0.0376 |
| 90 | train | partial_db | 12 | 5.9442 | 6.8450 | 0.9008 |
| 45 | train | attack_db | 12 | 6.3072 | 7.1913 | 0.8840 |
| 42 | dev | partial_db | 4 | 6.0578 | 6.9129 | 0.8551 |
| 69 | dev | early_db | 4 | 5.1753 | 6.0195 | 0.8442 |
| 60 | train | noise_db | 12 | 6.6577 | 7.4788 | 0.8210 |
| 36 | train | partial_db | 12 | 10.0748 | 10.8937 | 0.8189 |
| 54 | dev | sustain_db | 4 | 5.8636 | 6.6767 | 0.8131 |
| 66 | dev | sustain_db | 4 | 4.3793 | 5.1792 | 0.7999 |
| 36 | dev | partial_db | 4 | 9.9884 | 10.7849 | 0.7965 |
| 54 | train | sustain_db | 12 | 6.0579 | 6.8488 | 0.7909 |
| 81 | dev | noise_db | 4 | 6.7657 | 7.5537 | 0.7880 |
| 51 | dev | tuning_cents | 16 | 0.6729 | 1.4496 | 0.7767 |
| 93 | train | level_db | 12 | 2.4799 | 3.2485 | 0.7686 |
| 36 | train | tuning_cents | 12 | 3.3309 | 4.0894 | 0.7585 |
| 27 | dev | icc | 16 | 0.2146 | 0.2438 | 0.0292 |
| 81 | train | noise_db | 12 | 7.3972 | 8.1262 | 0.7290 |
| 45 | dev | attack_db | 4 | 6.0300 | 6.7587 | 0.7287 |
| 45 | train | icc | 12 | 0.1402 | 0.1687 | 0.0285 |
| 21 | dev | noise_db | 4 | 5.3858 | 6.0964 | 0.7107 |
| 90 | dev | sustain_db | 4 | 10.6490 | 11.3580 | 0.7090 |
| 45 | train | decay_db_s | 12 | 1.8975 | 3.3073 | 1.4098 |
| 36 | train | noise_db | 11 | 4.7363 | 5.4337 | 0.6974 |
| 48 | dev | attack_db | 4 | 5.9519 | 6.6287 | 0.6768 |
| 24 | train | attack_db | 12 | 7.0841 | 7.7509 | 0.6668 |
| 30 | train | icc | 12 | 0.1881 | 0.2146 | 0.0266 |
| 69 | dev | sustain_db | 4 | 5.7338 | 6.3970 | 0.6632 |
| 24 | dev | attack_db | 4 | 6.5014 | 7.1632 | 0.6618 |
| 30 | dev | noise_db | 3 | 5.6965 | 6.3486 | 0.6520 |
| 36 | dev | tuning_cents | 4 | 3.5512 | 4.1987 | 0.6475 |
| 96 | dev | attack_db | 4 | 5.3638 | 6.0099 | 0.6460 |
| 45 | dev | decay_db_s | 4 | 1.9562 | 3.2408 | 1.2846 |
| 66 | dev | attack_db | 4 | 4.1407 | 4.7735 | 0.6328 |
| 66 | dev | icc | 4 | 0.1201 | 0.1452 | 0.0251 |
| 27 | dev | noise_db | 16 | 7.5078 | 8.1351 | 0.6272 |
| 66 | dev | early_db | 4 | 4.5890 | 5.2099 | 0.6209 |
| 66 | train | sustain_db | 12 | 4.5680 | 5.1840 | 0.6159 |
| 60 | train | ild_db | 12 | 8.3470 | 8.9628 | 0.6158 |
| 69 | train | early_db | 12 | 5.4316 | 6.0395 | 0.6079 |
| 42 | dev | tuning_cents | 4 | 0.9865 | 1.5907 | 0.6042 |
| 45 | dev | icc | 4 | 0.1453 | 0.1694 | 0.0241 |
| 42 | train | tuning_cents | 12 | 0.9554 | 1.5475 | 0.5921 |
| 66 | train | icc | 12 | 0.1218 | 0.1454 | 0.0237 |
| 105 | dev | sustain_db | 4 | 12.4828 | 13.0606 | 0.5777 |
| 60 | dev | ild_db | 4 | 8.4426 | 9.0022 | 0.5596 |
| 96 | train | attack_db | 12 | 5.6311 | 6.1906 | 0.5594 |
| 54 | dev | icc | 4 | 0.2051 | 0.2269 | 0.0218 |
| 99 | dev | sustain_db | 16 | 8.7424 | 9.2854 | 0.5430 |
| 66 | train | early_db | 12 | 4.7529 | 5.2772 | 0.5243 |
| 108 | train | icc | 7 | 0.2431 | 0.2640 | 0.0209 |
| 90 | train | sustain_db | 12 | 10.4814 | 10.9887 | 0.5074 |
| 66 | train | attack_db | 12 | 4.3040 | 4.8081 | 0.5042 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| A2v1 | 45 | train | noise_db | gained | - | 9.0321 |
| A2v3 | 45 | dev | noise_db | gained | - | 7.8767 |
| C2v2 | 36 | train | noise_db | lost | 6.7507 | - |
| C3v1 | 48 | train | noise_db | gained | - | 1.6169 |
| D#3v5 | 51 | dev | noise_db | lost | 11.7982 | - |
| F#1v3 | 30 | dev | noise_db | lost | 8.5079 | - |
