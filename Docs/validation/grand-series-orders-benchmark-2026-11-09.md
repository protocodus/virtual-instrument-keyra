# Recording benchmark: 0.4.30 against 0.4.29

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.29

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 4.62 | 0.16 | 1.85 | 4.29 | 4.02 | 4.64 | 5.64 | 0.80 | 0.06 | 1.89 | 3.61 | 0.50 |
| dev (156) | 5.35 | 0.90 | 2.10 | 4.66 | 4.42 | 5.33 | 5.27 | 2.24 | 0.10 | 2.60 | 4.71 | 0.96 |
| train / bass A0-B2 (84) | 4.69 | 0.04 | 0.43 | 4.56 | 3.86 | 3.68 | 6.00 | 0.40 | 0.03 | 1.80 | 4.03 | 0.40 |
| train / middle C3-B5 (108) | 4.90 | 0.07 | 1.44 | 3.89 | 3.90 | 3.48 | 5.81 | 0.70 | 0.05 | 0.82 | 4.13 | 0.35 |
| train / treble C6-C8 (84) | 4.20 | 0.40 | 3.92 | 4.52 | 4.33 | 7.09 | 5.11 | 1.36 | 0.09 | 3.36 | 2.53 | 0.79 |
| dev / bass A0-B2 (44) | 5.48 | 1.27 | 1.08 | 4.82 | 4.02 | 3.88 | 5.18 | 1.35 | 0.05 | 2.66 | 5.38 | 0.99 |
| dev / middle C3-B5 (68) | 6.30 | 0.64 | 2.47 | 4.51 | 4.70 | 5.60 | 5.42 | 3.63 | 0.11 | 1.88 | 6.01 | 0.87 |
| dev / treble C6-C8 (44) | 3.76 | 0.95 | 2.55 | 4.71 | 4.40 | 6.36 | 5.13 | 0.95 | 0.15 | 3.64 | 2.05 | 1.07 |

## 0.4.30

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

## Independent-sample regressions (legacy)

Every note and role where 0.4.30 is worse than 0.4.29 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (25.7989 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 5.3548 | 5.3548 | 0.0001 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 0.9047 | 0.9046 | -0.0001 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 2.0978 | 2.0981 | 0.0003 | 0 | 0 | 1 |
| dev | attack_db | 156 | 4.6565 | 4.6538 | -0.0027 | 0 | 0 | 0 |
| dev | early_db | 156 | 4.4222 | 4.4210 | -0.0012 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 5.3263 | 5.3256 | -0.0007 | 0 | 0 | 0 |
| dev | noise_db | 153 | 5.2689 | 5.2475 | -0.0214 | 0 | 0 | 3 |
| dev | ild_db | 154 | 2.2450 | 2.2450 | 0.0000 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1020 | 0.1022 | 0.0002 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 2.5959 | 2.5958 | -0.0000 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 4.7109 | 4.7106 | -0.0003 | 0 | 0 | 0 |
| dev | level_db | 156 | 0.9610 | 0.9610 | 0.0000 | 0 | 0 | 0 |
| train | partial_db | 276 | 4.6224 | 4.6223 | -0.0002 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 0.1627 | 0.1627 | 0.0000 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 1.8520 | 1.8519 | -0.0000 | 0 | 0 | 5 |
| train | attack_db | 276 | 4.2852 | 4.2822 | -0.0030 | 0 | 0 | 0 |
| train | early_db | 276 | 4.0173 | 4.0159 | -0.0014 | 0 | 0 | 0 |
| train | sustain_db | 276 | 4.6394 | 4.6384 | -0.0010 | 0 | 0 | 0 |
| train | noise_db | 263 | 5.6387 | 5.5980 | -0.0406 | 0 | 0 | 13 |
| train | ild_db | 270 | 0.7957 | 0.7960 | 0.0003 | 0 | 0 | 6 |
| train | icc | 270 | 0.0555 | 0.0557 | 0.0002 | 0 | 0 | 6 |
| train | envelope_db | 276 | 1.8906 | 1.8905 | -0.0000 | 0 | 0 | 0 |
| train | rise_ms | 276 | 3.6142 | 3.6139 | -0.0003 | 0 | 0 | 0 |
| train | level_db | 276 | 0.5003 | 0.5005 | 0.0002 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
