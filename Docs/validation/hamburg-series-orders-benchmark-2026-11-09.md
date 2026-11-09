# Recording benchmark: 0.4.30 against 0.4.29

Every train and dev note of `Tools/corpus/split-hamburg-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.29

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (40) | 4.45 | 0.27 | 2.30 | 5.86 | 4.35 | 4.92 | 6.49 | 1.59 | 0.12 | 2.99 | 16.60 | 0.55 |
| dev (8) | 7.14 | 2.59 | 3.66 | 7.36 | 6.25 | 6.13 | 6.05 | 4.93 | 0.23 | 2.33 | 2.88 | 3.12 |
| train / bass A0-B2 (16) | 4.66 | 0.10 | 0.99 | 6.05 | 3.62 | 3.58 | 7.84 | 0.84 | 0.07 | 2.09 | 31.31 | 0.55 |
| train / middle C3-B5 (12) | 4.64 | 0.23 | 2.09 | 5.99 | 4.41 | 4.72 | 6.06 | 2.16 | 0.15 | 1.83 | 11.41 | 0.22 |
| train / treble C6-C8 (12) | 3.99 | 0.51 | 4.26 | 5.48 | 5.27 | 6.88 | 5.47 | 2.02 | 0.16 | 5.35 | 2.17 | 0.86 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.14 | 2.59 | 3.66 | 7.36 | 6.25 | 6.13 | 6.05 | 4.93 | 0.23 | 2.33 | 2.88 | 3.12 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## 0.4.30

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (40) | 4.45 | 0.27 | 2.30 | 5.87 | 4.35 | 4.92 | 6.43 | 1.59 | 0.12 | 2.99 | 16.60 | 0.55 |
| dev (8) | 7.14 | 2.59 | 3.66 | 7.38 | 6.27 | 6.14 | 6.48 | 4.93 | 0.23 | 2.33 | 2.88 | 3.12 |
| train / bass A0-B2 (16) | 4.64 | 0.10 | 0.98 | 6.07 | 3.62 | 3.58 | 7.66 | 0.84 | 0.07 | 2.09 | 31.31 | 0.55 |
| train / middle C3-B5 (12) | 4.64 | 0.23 | 2.09 | 5.99 | 4.41 | 4.72 | 6.06 | 2.16 | 0.15 | 1.83 | 11.41 | 0.22 |
| train / treble C6-C8 (12) | 3.99 | 0.51 | 4.26 | 5.48 | 5.27 | 6.88 | 5.47 | 2.02 | 0.16 | 5.35 | 2.17 | 0.86 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.14 | 2.59 | 3.66 | 7.38 | 6.27 | 6.14 | 6.48 | 4.93 | 0.23 | 2.33 | 2.88 | 3.12 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## Independent-sample regressions (legacy)

Every note and role where 0.4.30 is worse than 0.4.29 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.29 | 0.4.30 |
|---|---|---|---|---|
| 52 | dev | noise_db | 5.51 | 6.80 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (14.9476 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 8 | 7.1446 | 7.1446 | -0.0000 | 0 | 0 | 0 |
| dev | tuning_cents | 8 | 2.5889 | 2.5889 | -0.0000 | 0 | 0 | 0 |
| dev | decay_db_s | 8 | 3.6551 | 3.6551 | 0.0000 | 0 | 0 | 0 |
| dev | attack_db | 8 | 7.3607 | 7.3820 | 0.0214 | 0 | 0 | 0 |
| dev | early_db | 8 | 6.2543 | 6.2707 | 0.0164 | 0 | 0 | 0 |
| dev | sustain_db | 8 | 6.1346 | 6.1365 | 0.0019 | 0 | 0 | 0 |
| dev | noise_db | 6 | 6.0459 | 6.4750 | 0.4291 | 0 | 0 | 2 |
| dev | ild_db | 8 | 4.9259 | 4.9259 | 0.0000 | 0 | 0 | 0 |
| dev | icc | 8 | 0.2333 | 0.2333 | -0.0000 | 0 | 0 | 0 |
| dev | envelope_db | 8 | 2.3312 | 2.3316 | 0.0004 | 0 | 0 | 0 |
| dev | rise_ms | 8 | 2.8828 | 2.8828 | 0.0000 | 0 | 0 | 0 |
| dev | level_db | 8 | 3.1233 | 3.1236 | 0.0003 | 0 | 0 | 0 |
| train | partial_db | 40 | 4.4547 | 4.4463 | -0.0084 | 0 | 0 | 0 |
| train | tuning_cents | 40 | 0.2657 | 0.2657 | 0.0000 | 0 | 0 | 0 |
| train | decay_db_s | 40 | 2.3025 | 2.2989 | -0.0036 | 0 | 0 | 0 |
| train | attack_db | 40 | 5.8631 | 5.8713 | 0.0082 | 0 | 0 | 0 |
| train | early_db | 40 | 4.3531 | 4.3536 | 0.0005 | 0 | 0 | 0 |
| train | sustain_db | 40 | 4.9150 | 4.9150 | 0.0000 | 0 | 0 | 0 |
| train | noise_db | 37 | 6.4941 | 6.4314 | -0.0627 | 0 | 0 | 3 |
| train | ild_db | 40 | 1.5905 | 1.5896 | -0.0009 | 0 | 0 | 0 |
| train | icc | 40 | 0.1177 | 0.1176 | -0.0000 | 0 | 0 | 0 |
| train | envelope_db | 40 | 2.9882 | 2.9882 | 0.0000 | 0 | 0 | 0 |
| train | rise_ms | 40 | 16.5964 | 16.5958 | -0.0005 | 0 | 0 | 0 |
| train | level_db | 40 | 0.5466 | 0.5466 | 0.0000 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 52 | dev | noise_db | 2 | 5.5082 | 6.7955 | 1.2872 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
