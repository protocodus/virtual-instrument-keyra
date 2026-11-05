# Recording benchmark: candidate 0.4.22 against shipping 0.4.21

Every train and dev note of `Tools/corpus/split-hamburg-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## shipping 0.4.21

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (40) | 4.69 | 0.26 | 3.42 | 6.14 | 5.07 | 5.62 | 7.16 | 1.53 | 0.12 | 3.30 | 17.42 | 0.70 |
| dev (8) | 7.87 | 0.65 | 5.04 | 6.82 | 6.75 | 7.53 | 6.71 | 4.98 | 0.19 | 4.21 | 4.07 | 1.84 |
| train / bass A0-B2 (16) | 4.69 | 0.09 | 0.97 | 6.53 | 3.86 | 3.73 | 8.13 | 0.89 | 0.06 | 2.39 | 32.18 | 0.56 |
| train / middle C3-B5 (12) | 4.63 | 0.24 | 2.25 | 6.21 | 5.48 | 5.67 | 7.24 | 1.93 | 0.12 | 1.95 | 12.41 | 0.27 |
| train / treble C6-C8 (12) | 4.75 | 0.51 | 7.84 | 5.54 | 6.27 | 8.10 | 6.04 | 1.97 | 0.19 | 5.87 | 2.74 | 1.32 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.87 | 0.65 | 5.04 | 6.82 | 6.75 | 7.53 | 6.71 | 4.98 | 0.19 | 4.21 | 4.07 | 1.84 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## candidate 0.4.22

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (40) | 4.69 | 0.26 | 3.41 | 6.13 | 5.06 | 5.61 | 7.14 | 1.53 | 0.12 | 3.30 | 17.42 | 0.69 |
| dev (8) | 7.88 | 1.02 | 4.45 | 6.94 | 6.68 | 6.17 | 6.52 | 4.86 | 0.20 | 2.54 | 3.74 | 2.15 |
| train / bass A0-B2 (16) | 4.69 | 0.09 | 0.97 | 6.53 | 3.86 | 3.73 | 8.10 | 0.89 | 0.06 | 2.39 | 32.19 | 0.60 |
| train / middle C3-B5 (12) | 4.63 | 0.23 | 2.24 | 6.19 | 5.43 | 5.62 | 7.19 | 1.93 | 0.12 | 1.94 | 12.41 | 0.27 |
| train / treble C6-C8 (12) | 4.75 | 0.51 | 7.81 | 5.55 | 6.28 | 8.11 | 6.05 | 1.97 | 0.19 | 5.87 | 2.74 | 1.24 |
| dev / bass A0-B2 (0) | - | - | - | - | - | - | - | - | - | - | - | - |
| dev / middle C3-B5 (8) | 7.88 | 1.02 | 4.45 | 6.94 | 6.68 | 6.17 | 6.52 | 4.86 | 0.20 | 2.54 | 3.74 | 2.15 |
| dev / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## Independent-sample regressions (legacy)

Every note and role where candidate 0.4.22 is worse than shipping 0.4.21 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | shipping 0.4.21 | candidate 0.4.22 |
|---|---|---|---|---|
| 52 | dev | partial_db | 8.89 | 10.22 |
| 52 | dev | noise_db | 5.01 | 5.94 |
| 73 | dev | tuning_cents | 0.90 | 1.57 |
| 52 | dev | attack_db | 6.68 | 7.32 |
| 52 | dev | icc | 0.19 | 0.21 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (16.3580 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 8 | 7.8676 | 7.8846 | 0.0170 | 0 | 0 | 0 |
| dev | tuning_cents | 8 | 0.6487 | 1.0239 | 0.3752 | 0 | 0 | 0 |
| dev | decay_db_s | 8 | 5.0405 | 4.4461 | -0.5944 | 0 | 0 | 0 |
| dev | attack_db | 8 | 6.8163 | 6.9444 | 0.1281 | 0 | 0 | 0 |
| dev | early_db | 8 | 6.7477 | 6.6789 | -0.0687 | 0 | 0 | 0 |
| dev | sustain_db | 8 | 7.5310 | 6.1727 | -1.3582 | 0 | 0 | 0 |
| dev | noise_db | 6 | 6.7072 | 6.5164 | -0.1908 | 0 | 0 | 2 |
| dev | ild_db | 8 | 4.9821 | 4.8605 | -0.1216 | 0 | 0 | 0 |
| dev | icc | 8 | 0.1915 | 0.1999 | 0.0083 | 0 | 0 | 0 |
| dev | envelope_db | 8 | 4.2126 | 2.5367 | -1.6759 | 0 | 0 | 0 |
| dev | rise_ms | 8 | 4.0703 | 3.7370 | -0.3333 | 0 | 0 | 0 |
| dev | level_db | 8 | 1.8434 | 1.3750 | -0.4684 | 0 | 0 | 0 |
| train | partial_db | 40 | 4.6901 | 4.6906 | 0.0006 | 0 | 0 | 0 |
| train | tuning_cents | 40 | 0.2602 | 0.2594 | -0.0008 | 0 | 0 | 0 |
| train | decay_db_s | 40 | 3.4165 | 3.4052 | -0.0114 | 0 | 0 | 0 |
| train | attack_db | 40 | 6.1373 | 6.1338 | -0.0035 | 0 | 0 | 0 |
| train | early_db | 40 | 5.0692 | 5.0574 | -0.0118 | 0 | 0 | 0 |
| train | sustain_db | 40 | 5.6238 | 5.6130 | -0.0108 | 0 | 0 | 0 |
| train | noise_db | 37 | 7.1640 | 7.1439 | -0.0201 | 0 | 0 | 3 |
| train | ild_db | 40 | 1.5251 | 1.5255 | 0.0004 | 0 | 0 | 0 |
| train | icc | 40 | 0.1157 | 0.1157 | 0.0000 | 0 | 0 | 0 |
| train | envelope_db | 40 | 3.3029 | 3.3023 | -0.0006 | 0 | 0 | 0 |
| train | rise_ms | 40 | 17.4177 | 17.4214 | 0.0036 | 0 | 0 | 0 |
| train | level_db | 40 | 0.6965 | 1.9310 | 1.2345 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 45 | train | level_db | 4 | 0.4256 | 2.2998 | 1.8742 |
| 38 | train | level_db | 4 | 0.3383 | 2.1886 | 1.8503 |
| 24 | train | level_db | 4 | 0.5263 | 2.3211 | 1.7948 |
| 59 | train | level_db | 4 | 0.1623 | 1.9339 | 1.7716 |
| 80 | train | level_db | 4 | 0.4410 | 1.9420 | 1.5010 |
| 66 | train | level_db | 4 | 0.1935 | 1.6567 | 1.4632 |
| 31 | train | level_db | 4 | 0.9300 | 2.2658 | 1.3357 |
| 52 | dev | partial_db | 4 | 8.8886 | 10.2184 | 1.3298 |
| 52 | dev | noise_db | 2 | 5.0136 | 5.9392 | 0.9255 |
| 94 | train | level_db | 4 | 1.1794 | 2.0870 | 0.9076 |
| 73 | dev | tuning_cents | 4 | 0.8979 | 1.5701 | 0.6723 |
| 52 | dev | attack_db | 4 | 6.6849 | 7.3222 | 0.6373 |
| 52 | dev | icc | 4 | 0.1919 | 0.2144 | 0.0224 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
