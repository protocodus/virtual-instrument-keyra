# Recording benchmark: 0.4.33 against 0.4.32

Every train and dev note of `Tools/corpus/split-hamburg-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.32

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (40) | 4.38 | 0.29 | 2.34 | 5.90 | 4.43 | 4.98 | 6.47 | 1.55 | 0.12 | 2.94 | 16.79 | 1.04 |
| dev (8) | 7.15 | 2.58 | 3.63 | 7.36 | 6.25 | 6.13 | 6.43 | 4.94 | 0.23 | 2.33 | 2.79 | 2.60 |
| train / bass A0-B2 (16) | 4.65 | 0.10 | 0.99 | 6.07 | 3.62 | 3.59 | 7.70 | 0.92 | 0.07 | 2.09 | 31.92 | 0.66 |
| train / middle C3-B5 (12) | 4.60 | 0.23 | 2.13 | 5.99 | 4.36 | 4.73 | 5.99 | 2.25 | 0.15 | 1.91 | 11.43 | 0.81 |
| train / treble C6-C8 (12) | 3.80 | 0.61 | 4.35 | 5.58 | 5.59 | 7.10 | 5.62 | 1.70 | 0.15 | 5.12 | 2.00 | 1.79 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.15 | 2.58 | 3.63 | 7.36 | 6.25 | 6.13 | 6.43 | 4.94 | 0.23 | 2.33 | 2.79 | 2.60 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## 0.4.33

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (40) | 4.38 | 0.29 | 2.34 | 5.90 | 4.43 | 4.98 | 6.47 | 1.55 | 0.12 | 2.94 | 16.79 | 1.04 |
| dev (8) | 7.16 | 2.58 | 3.63 | 7.04 | 5.92 | 6.02 | 5.66 | 4.93 | 0.23 | 2.32 | 2.79 | 2.60 |
| train / bass A0-B2 (16) | 4.65 | 0.10 | 0.99 | 6.07 | 3.62 | 3.59 | 7.70 | 0.92 | 0.07 | 2.09 | 31.92 | 0.66 |
| train / middle C3-B5 (12) | 4.60 | 0.23 | 2.13 | 5.99 | 4.36 | 4.73 | 5.99 | 2.25 | 0.15 | 1.91 | 11.43 | 0.81 |
| train / treble C6-C8 (12) | 3.80 | 0.61 | 4.35 | 5.58 | 5.59 | 7.10 | 5.62 | 1.70 | 0.15 | 5.12 | 2.00 | 1.79 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.16 | 2.58 | 3.63 | 7.04 | 5.92 | 6.02 | 5.66 | 4.93 | 0.23 | 2.32 | 2.79 | 2.60 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## Independent-sample regressions (legacy)

Every note and role where 0.4.33 is worse than 0.4.32 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (15.0842 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 8 | 7.1521 | 7.1618 | 0.0096 | 0 | 0 | 0 |
| dev | tuning_cents | 8 | 2.5758 | 2.5758 | 0.0000 | 0 | 0 | 0 |
| dev | decay_db_s | 8 | 3.6319 | 3.6318 | -0.0001 | 0 | 0 | 0 |
| dev | attack_db | 8 | 7.3590 | 7.0427 | -0.3163 | 0 | 0 | 0 |
| dev | early_db | 8 | 6.2538 | 5.9218 | -0.3319 | 0 | 0 | 0 |
| dev | sustain_db | 8 | 6.1267 | 6.0242 | -0.1026 | 0 | 0 | 0 |
| dev | noise_db | 6 | 6.4331 | 5.6621 | -0.7710 | 0 | 0 | 2 |
| dev | ild_db | 8 | 4.9351 | 4.9329 | -0.0021 | 0 | 0 | 0 |
| dev | icc | 8 | 0.2335 | 0.2337 | 0.0002 | 0 | 0 | 0 |
| dev | envelope_db | 8 | 2.3254 | 2.3236 | -0.0018 | 0 | 0 | 0 |
| dev | rise_ms | 8 | 2.7917 | 2.7917 | 0.0000 | 0 | 0 | 0 |
| dev | level_db | 8 | 2.5970 | 2.5957 | -0.0013 | 0 | 0 | 0 |
| train | partial_db | 40 | 4.3806 | 4.3806 | -0.0000 | 0 | 0 | 0 |
| train | tuning_cents | 40 | 0.2937 | 0.2937 | -0.0000 | 0 | 0 | 0 |
| train | decay_db_s | 40 | 2.3383 | 2.3383 | -0.0000 | 0 | 0 | 0 |
| train | attack_db | 40 | 5.9022 | 5.9022 | -0.0000 | 0 | 0 | 0 |
| train | early_db | 40 | 4.4316 | 4.4316 | -0.0000 | 0 | 0 | 0 |
| train | sustain_db | 40 | 4.9848 | 4.9848 | -0.0000 | 0 | 0 | 0 |
| train | noise_db | 37 | 6.4698 | 6.4698 | -0.0000 | 0 | 0 | 3 |
| train | ild_db | 40 | 1.5512 | 1.5512 | 0.0000 | 0 | 0 | 0 |
| train | icc | 40 | 0.1171 | 0.1171 | -0.0000 | 0 | 0 | 0 |
| train | envelope_db | 40 | 2.9442 | 2.9442 | 0.0000 | 0 | 0 | 0 |
| train | rise_ms | 40 | 16.7927 | 16.7927 | 0.0000 | 0 | 0 | 0 |
| train | level_db | 40 | 1.0432 | 1.0432 | -0.0000 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
