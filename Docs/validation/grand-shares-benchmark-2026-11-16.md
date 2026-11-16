# Recording benchmark: 2.16.1 against 2.16.0 (1bc8982)

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.16.0 (1bc8982)

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.09 | 2.14 | 4.06 | 6.54 | 6.48 | 8.73 | 7.11 | 4.94 | 0.20 | 4.23 | 13.76 | 2.42 |
| dev (156) | 7.43 | 2.45 | 3.43 | 6.24 | 6.03 | 7.74 | 6.94 | 4.81 | 0.18 | 3.87 | 12.57 | 2.72 |
| train / bass A0-B2 (84) | 8.73 | 3.08 | 2.66 | 5.69 | 5.35 | 6.32 | 6.46 | 4.67 | 0.21 | 3.45 | 24.58 | 2.05 |
| train / middle C3-B5 (108) | 7.65 | 1.25 | 3.91 | 6.40 | 6.48 | 8.03 | 7.06 | 6.56 | 0.20 | 3.92 | 10.62 | 2.07 |
| train / treble C6-C8 (84) | 8.01 | 2.33 | 5.78 | 7.56 | 7.62 | 12.05 | 7.79 | 3.00 | 0.20 | 5.42 | 6.98 | 3.23 |
| dev / bass A0-B2 (44) | 8.98 | 3.84 | 2.50 | 5.30 | 4.82 | 5.67 | 6.42 | 4.52 | 0.18 | 3.12 | 22.70 | 2.75 |
| dev / middle C3-B5 (68) | 7.20 | 1.16 | 3.55 | 6.42 | 6.21 | 7.22 | 7.12 | 6.67 | 0.15 | 3.60 | 10.98 | 2.22 |
| dev / treble C6-C8 (44) | 6.25 | 3.05 | 4.19 | 6.91 | 6.95 | 10.63 | 7.16 | 2.12 | 0.22 | 5.05 | 4.88 | 3.45 |

## 2.16.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.09 | 2.14 | 4.07 | 6.54 | 6.48 | 8.73 | 7.11 | 4.94 | 0.20 | 4.23 | 13.76 | 2.42 |
| dev (156) | 7.43 | 2.45 | 3.43 | 6.24 | 6.03 | 7.74 | 6.95 | 4.81 | 0.18 | 3.87 | 12.57 | 2.72 |
| train / bass A0-B2 (84) | 8.72 | 3.08 | 2.66 | 5.69 | 5.35 | 6.32 | 6.48 | 4.67 | 0.21 | 3.45 | 24.58 | 2.05 |
| train / middle C3-B5 (108) | 7.65 | 1.25 | 3.91 | 6.40 | 6.48 | 8.03 | 7.06 | 6.56 | 0.20 | 3.92 | 10.62 | 2.07 |
| train / treble C6-C8 (84) | 8.01 | 2.33 | 5.78 | 7.56 | 7.62 | 12.05 | 7.79 | 3.00 | 0.20 | 5.42 | 6.98 | 3.23 |
| dev / bass A0-B2 (44) | 8.97 | 3.84 | 2.50 | 5.30 | 4.82 | 5.66 | 6.45 | 4.52 | 0.18 | 3.12 | 22.70 | 2.75 |
| dev / middle C3-B5 (68) | 7.20 | 1.16 | 3.55 | 6.42 | 6.21 | 7.22 | 7.12 | 6.67 | 0.15 | 3.60 | 10.98 | 2.22 |
| dev / treble C6-C8 (44) | 6.25 | 3.05 | 4.19 | 6.91 | 6.95 | 10.63 | 7.16 | 2.12 | 0.22 | 5.05 | 4.88 | 3.45 |

## Independent-sample regressions (legacy)

Every note and role where 2.16.1 is worse than 2.16.0 (1bc8982) by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.2795 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 7.4323 | 7.4313 | -0.0010 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.4490 | 2.4492 | 0.0002 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 3.4269 | 3.4266 | -0.0003 | 0 | 0 | 1 |
| dev | attack_db | 156 | 6.2427 | 6.2417 | -0.0010 | 0 | 0 | 0 |
| dev | early_db | 156 | 6.0284 | 6.0282 | -0.0002 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 7.7408 | 7.7406 | -0.0002 | 0 | 0 | 0 |
| dev | noise_db | 153 | 6.9369 | 6.9458 | 0.0090 | 0 | 0 | 3 |
| dev | ild_db | 154 | 4.8148 | 4.8144 | -0.0004 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1778 | 0.1778 | 0.0000 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 3.8741 | 3.8741 | -0.0000 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 12.5664 | 12.5664 | 0.0000 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.7174 | 2.7174 | -0.0000 | 0 | 0 | 0 |
| train | partial_db | 276 | 8.0882 | 8.0866 | -0.0016 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 2.1387 | 2.1402 | 0.0015 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 4.0648 | 4.0651 | 0.0003 | 0 | 0 | 5 |
| train | attack_db | 276 | 6.5378 | 6.5364 | -0.0014 | 0 | 0 | 0 |
| train | early_db | 276 | 6.4812 | 6.4804 | -0.0008 | 0 | 0 | 0 |
| train | sustain_db | 276 | 8.7344 | 8.7341 | -0.0003 | 0 | 0 | 0 |
| train | noise_db | 273 | 7.1058 | 7.1130 | 0.0072 | 0 | 0 | 3 |
| train | ild_db | 270 | 4.9411 | 4.9404 | -0.0007 | 0 | 0 | 6 |
| train | icc | 270 | 0.2027 | 0.2027 | 0.0000 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.2294 | 4.2295 | 0.0000 | 0 | 0 | 0 |
| train | rise_ms | 276 | 13.7607 | 13.7608 | 0.0001 | 0 | 0 | 0 |
| train | level_db | 276 | 2.4167 | 2.4167 | 0.0000 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
