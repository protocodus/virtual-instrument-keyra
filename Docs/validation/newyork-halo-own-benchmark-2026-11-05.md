# Recording benchmark: 0.4.24 against 0.4.23

Every train and dev note of `Tools/corpus/split-newyork-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.23

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (61) | 7.73 | 0.59 | 3.99 | 7.53 | 7.41 | 7.87 | 8.13 | 1.74 | 0.09 | 2.59 | 12.06 | 0.88 |
| dev (17) | 10.63 | 2.54 | 7.23 | 9.36 | 8.77 | 10.48 | 9.60 | 5.98 | 0.20 | 4.94 | 8.28 | 5.61 |
| train / bass A0-B2 (20) | 9.04 | 0.41 | 1.85 | 9.40 | 9.28 | 8.15 | 12.39 | 1.39 | 0.08 | 2.15 | 14.39 | 0.85 |
| train / middle C3-B5 (24) | 8.26 | 0.25 | 4.35 | 6.40 | 6.54 | 7.15 | 5.53 | 1.53 | 0.11 | 2.59 | 15.86 | 0.23 |
| train / treble C6-C8 (17) | 5.29 | 1.31 | 7.38 | 6.94 | 6.44 | 8.63 | 6.80 | 2.92 | 0.07 | 3.12 | 3.97 | 1.83 |
| dev / bass A0-B2 (5) | 10.57 | 4.22 | 3.50 | 8.85 | 8.04 | 8.63 | 11.37 | 3.62 | 0.13 | 3.41 | 8.04 | 4.09 |
| dev / middle C3-B5 (5) | 10.08 | 1.08 | 5.17 | 7.86 | 7.80 | 10.02 | 7.01 | 5.49 | 0.19 | 3.82 | 9.84 | 3.40 |
| dev / treble C6-C8 (7) | 11.07 | 2.39 | 11.38 | 10.79 | 9.98 | 12.14 | 10.18 | 8.01 | 0.25 | 6.82 | 7.35 | 8.26 |

## 0.4.24

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

## Independent-sample regressions (legacy)

Every note and role where 0.4.24 is worse than 0.4.23 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (26.6328 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 17 | 10.6314 | 10.6314 | 0.0001 | 0 | 0 | 0 |
| dev | tuning_cents | 17 | 2.5445 | 2.5445 | -0.0000 | 0 | 0 | 0 |
| dev | decay_db_s | 17 | 7.2338 | 7.2586 | 0.0248 | 0 | 0 | 0 |
| dev | attack_db | 17 | 9.3585 | 9.3585 | -0.0000 | 0 | 0 | 0 |
| dev | early_db | 17 | 8.7665 | 8.7664 | -0.0001 | 0 | 0 | 0 |
| dev | sustain_db | 17 | 10.4828 | 10.4825 | -0.0003 | 0 | 0 | 0 |
| dev | noise_db | 17 | 9.5995 | 9.5995 | -0.0000 | 0 | 0 | 0 |
| dev | ild_db | 17 | 5.9768 | 5.9768 | 0.0001 | 0 | 0 | 0 |
| dev | icc | 17 | 0.1957 | 0.1957 | -0.0000 | 0 | 0 | 0 |
| dev | envelope_db | 17 | 4.9362 | 4.9361 | -0.0001 | 0 | 0 | 0 |
| dev | rise_ms | 17 | 8.2845 | 8.2845 | 0.0000 | 0 | 0 | 0 |
| dev | level_db | 17 | 5.6056 | 5.6056 | -0.0000 | 0 | 0 | 0 |
| train | partial_db | 60 | 7.7301 | 7.7300 | -0.0001 | 0 | 0 | 1 |
| train | tuning_cents | 60 | 0.5860 | 0.5863 | 0.0003 | 0 | 0 | 1 |
| train | decay_db_s | 54 | 3.9858 | 3.9863 | 0.0005 | 0 | 0 | 7 |
| train | attack_db | 61 | 7.5337 | 7.5336 | -0.0002 | 0 | 0 | 0 |
| train | early_db | 61 | 7.4105 | 7.4106 | 0.0001 | 0 | 0 | 0 |
| train | sustain_db | 59 | 7.8678 | 7.8677 | -0.0001 | 0 | 0 | 2 |
| train | noise_db | 61 | 8.1336 | 8.1335 | -0.0002 | 0 | 0 | 0 |
| train | ild_db | 54 | 1.7350 | 1.7350 | 0.0000 | 0 | 0 | 7 |
| train | icc | 54 | 0.0930 | 0.0930 | -0.0000 | 0 | 0 | 7 |
| train | envelope_db | 61 | 2.5928 | 2.5925 | -0.0003 | 0 | 0 | 0 |
| train | rise_ms | 61 | 12.0630 | 12.0654 | 0.0024 | 0 | 0 | 0 |
| train | level_db | 61 | 0.8761 | 0.8764 | 0.0004 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
