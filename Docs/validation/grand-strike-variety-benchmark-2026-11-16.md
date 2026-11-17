# Recording benchmark: 2.23.0 against 2.22.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.22.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 7.79 | 2.22 | 3.96 | 6.63 | 6.59 | 8.71 | 7.95 | 5.03 | 0.20 | 4.23 | 14.04 | 2.56 |
| dev (156) | 7.26 | 2.54 | 3.42 | 6.36 | 6.08 | 7.79 | 7.56 | 5.02 | 0.18 | 3.92 | 12.25 | 2.81 |
| train / bass A0-B2 (84) | 8.72 | 2.94 | 2.66 | 5.80 | 5.47 | 6.38 | 8.33 | 4.35 | 0.20 | 3.52 | 25.81 | 2.02 |
| train / middle C3-B5 (108) | 7.13 | 1.26 | 3.90 | 6.05 | 6.23 | 7.93 | 7.22 | 6.58 | 0.20 | 3.90 | 10.44 | 2.09 |
| train / treble C6-C8 (84) | 7.69 | 2.74 | 5.44 | 8.20 | 8.17 | 12.03 | 8.50 | 3.59 | 0.19 | 5.36 | 6.88 | 3.72 |
| dev / bass A0-B2 (44) | 9.02 | 3.68 | 2.50 | 5.37 | 4.94 | 5.74 | 7.96 | 4.52 | 0.18 | 3.16 | 22.83 | 2.79 |
| dev / middle C3-B5 (68) | 6.85 | 1.19 | 3.56 | 6.16 | 5.84 | 7.21 | 7.00 | 6.77 | 0.15 | 3.69 | 10.18 | 2.16 |
| dev / treble C6-C8 (44) | 6.12 | 3.50 | 4.17 | 7.64 | 7.59 | 10.73 | 7.99 | 2.72 | 0.22 | 5.04 | 4.88 | 3.82 |

## 2.23.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 7.79 | 2.22 | 3.96 | 6.63 | 6.59 | 8.71 | 7.95 | 5.03 | 0.20 | 4.23 | 14.04 | 2.56 |
| dev (156) | 7.26 | 2.54 | 3.42 | 6.36 | 6.08 | 7.79 | 7.56 | 5.02 | 0.18 | 3.92 | 12.25 | 2.81 |
| train / bass A0-B2 (84) | 8.72 | 2.94 | 2.66 | 5.80 | 5.47 | 6.38 | 8.33 | 4.35 | 0.20 | 3.52 | 25.81 | 2.02 |
| train / middle C3-B5 (108) | 7.13 | 1.26 | 3.90 | 6.05 | 6.23 | 7.93 | 7.22 | 6.58 | 0.20 | 3.90 | 10.44 | 2.09 |
| train / treble C6-C8 (84) | 7.69 | 2.74 | 5.44 | 8.20 | 8.17 | 12.03 | 8.50 | 3.60 | 0.19 | 5.36 | 6.88 | 3.72 |
| dev / bass A0-B2 (44) | 9.02 | 3.68 | 2.49 | 5.38 | 4.94 | 5.74 | 7.96 | 4.52 | 0.18 | 3.16 | 22.83 | 2.79 |
| dev / middle C3-B5 (68) | 6.85 | 1.19 | 3.56 | 6.16 | 5.84 | 7.21 | 7.00 | 6.77 | 0.15 | 3.69 | 10.18 | 2.16 |
| dev / treble C6-C8 (44) | 6.12 | 3.50 | 4.17 | 7.64 | 7.60 | 10.73 | 7.99 | 2.72 | 0.22 | 5.04 | 4.88 | 3.82 |

## Independent-sample regressions (legacy)

Every note and role where 2.23.0 is worse than 2.22.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.8010 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 7.2567 | 7.2568 | 0.0001 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.5442 | 2.5442 | 0.0000 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 3.4238 | 3.4231 | -0.0007 | 0 | 0 | 1 |
| dev | attack_db | 156 | 6.3565 | 6.3589 | 0.0025 | 0 | 0 | 0 |
| dev | early_db | 156 | 6.0806 | 6.0810 | 0.0004 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 7.7872 | 7.7871 | -0.0000 | 0 | 0 | 0 |
| dev | noise_db | 153 | 7.5560 | 7.5555 | -0.0005 | 0 | 0 | 3 |
| dev | ild_db | 154 | 5.0217 | 5.0217 | 0.0000 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1789 | 0.1789 | -0.0000 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 3.9218 | 3.9213 | -0.0004 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 12.2525 | 12.2525 | 0.0000 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.8077 | 2.7808 | -0.0268 | 0 | 0 | 0 |
| train | partial_db | 276 | 7.7877 | 7.7877 | 0.0000 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.2211 | 2.2212 | 0.0000 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 3.9626 | 3.9626 | 0.0000 | 0 | 0 | 5 |
| train | attack_db | 276 | 6.6265 | 6.6273 | 0.0008 | 0 | 0 | 0 |
| train | early_db | 276 | 6.5891 | 6.5893 | 0.0002 | 0 | 0 | 0 |
| train | sustain_db | 276 | 8.7066 | 8.7066 | 0.0000 | 0 | 0 | 0 |
| train | noise_db | 273 | 7.9470 | 7.9495 | 0.0024 | 0 | 0 | 3 |
| train | ild_db | 270 | 5.0257 | 5.0258 | 0.0001 | 0 | 0 | 6 |
| train | icc | 270 | 0.1962 | 0.1962 | 0.0000 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.2285 | 4.2284 | -0.0001 | 0 | 0 | 0 |
| train | rise_ms | 276 | 14.0365 | 14.0362 | -0.0003 | 0 | 0 | 0 |
| train | level_db | 276 | 2.5637 | 2.6058 | 0.0421 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
