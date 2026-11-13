# Recording benchmark: candidate 2.13.1 against 2.13.0

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.13.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.70 | 3.43 | 4.41 | 7.64 | 9.06 | 10.52 | 9.81 | 6.46 | 0.24 | 4.23 | 13.14 | 4.23 |
| dev (21) | 7.55 | 3.55 | 4.65 | 7.67 | 9.07 | 9.87 | 8.67 | 5.99 | 0.26 | 4.12 | 9.07 | 3.15 |
| train / bass A0-B2 (30) | 10.80 | 5.22 | 4.28 | 8.36 | 9.21 | 10.35 | 15.10 | 6.98 | 0.20 | 2.75 | 8.95 | 3.60 |
| train / middle C3-B5 (69) | 7.40 | 2.85 | 3.98 | 7.47 | 8.26 | 8.31 | 8.79 | 6.05 | 0.20 | 3.83 | 19.78 | 4.65 |
| train / treble C6-C8 (38) | 5.80 | 3.07 | 5.33 | 7.37 | 10.39 | 14.66 | 7.50 | 6.80 | 0.36 | 6.14 | 4.41 | 3.94 |
| dev / bass A0-B2 (5) | 10.30 | 4.12 | 2.23 | 8.70 | 9.76 | 10.59 | 13.43 | 4.01 | 0.28 | 2.02 | 1.74 | 2.06 |
| dev / middle C3-B5 (11) | 6.34 | 2.29 | 4.39 | 7.11 | 7.93 | 7.83 | 7.35 | 8.01 | 0.22 | 3.79 | 14.75 | 3.62 |
| dev / treble C6-C8 (5) | 7.47 | 5.74 | 7.65 | 7.88 | 10.89 | 13.64 | 7.77 | 3.54 | 0.35 | 6.94 | 3.90 | 3.21 |

## candidate 2.13.1

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.54 | 3.33 | 4.37 | 7.65 | 9.09 | 10.54 | 9.82 | 6.40 | 0.24 | 4.24 | 12.81 | 4.24 |
| dev (21) | 7.27 | 3.39 | 4.65 | 7.71 | 9.10 | 9.88 | 8.75 | 5.94 | 0.27 | 4.13 | 9.15 | 3.19 |
| train / bass A0-B2 (30) | 10.07 | 4.74 | 4.11 | 8.43 | 9.34 | 10.44 | 15.24 | 6.72 | 0.20 | 2.80 | 7.42 | 3.63 |
| train / middle C3-B5 (69) | 7.39 | 2.87 | 3.99 | 7.47 | 8.26 | 8.32 | 8.75 | 6.04 | 0.20 | 3.83 | 19.78 | 4.66 |
| train / treble C6-C8 (38) | 5.80 | 3.07 | 5.33 | 7.37 | 10.39 | 14.66 | 7.50 | 6.80 | 0.36 | 6.14 | 4.41 | 3.95 |
| dev / bass A0-B2 (5) | 9.22 | 3.34 | 2.27 | 8.88 | 9.86 | 10.62 | 12.82 | 3.80 | 0.29 | 2.09 | 2.07 | 2.23 |
| dev / middle C3-B5 (11) | 6.29 | 2.34 | 4.37 | 7.11 | 7.93 | 7.83 | 7.35 | 8.01 | 0.22 | 3.79 | 14.75 | 3.60 |
| dev / treble C6-C8 (5) | 7.47 | 5.74 | 7.65 | 7.88 | 10.89 | 13.64 | 7.77 | 3.54 | 0.35 | 6.94 | 3.90 | 3.22 |

## Independent-sample regressions (legacy)

Every note and role where candidate 2.13.1 is worse than 2.13.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (12.3758 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 7.5504 | 7.2686 | -0.2818 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 3.5456 | 3.3869 | -0.1587 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 4.6505 | 4.6477 | -0.0027 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.6700 | 7.7115 | 0.0415 | 0 | 0 | 0 |
| dev | early_db | 21 | 9.0705 | 9.0951 | 0.0246 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 9.8720 | 9.8773 | 0.0053 | 0 | 0 | 0 |
| dev | noise_db | 20 | 8.6723 | 8.6555 | -0.0167 | 0 | 1 | 0 |
| dev | ild_db | 21 | 5.9939 | 5.9421 | -0.0518 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2632 | 0.2660 | 0.0028 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.1157 | 4.1321 | 0.0164 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 9.0694 | 9.1488 | 0.0794 | 0 | 0 | 0 |
| dev | level_db | 21 | 3.1512 | 3.1837 | 0.0325 | 0 | 0 | 0 |
| train | partial_db | 137 | 7.7032 | 7.5369 | -0.1662 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 3.4330 | 3.3346 | -0.0984 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 4.4075 | 4.3713 | -0.0363 | 0 | 0 | 2 |
| train | attack_db | 137 | 7.6394 | 7.6533 | 0.0140 | 0 | 0 | 0 |
| train | early_db | 137 | 9.0596 | 9.0879 | 0.0283 | 0 | 0 | 0 |
| train | sustain_db | 137 | 10.5186 | 10.5409 | 0.0222 | 0 | 0 | 0 |
| train | noise_db | 137 | 9.8120 | 9.8228 | 0.0108 | 0 | 0 | 0 |
| train | ild_db | 135 | 6.4559 | 6.3964 | -0.0595 | 0 | 0 | 2 |
| train | icc | 135 | 0.2424 | 0.2423 | -0.0001 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.2322 | 4.2440 | 0.0118 | 0 | 0 | 0 |
| train | rise_ms | 137 | 13.1429 | 12.8104 | -0.3326 | 0 | 0 | 0 |
| train | level_db | 137 | 4.2250 | 4.2372 | 0.0122 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

| case | note | role | metric | change | baseline | candidate |
|---|---|---|---|---|---:|---:|
| n39v1r1 | 39 | dev | noise_db | gained | - | 10.7280 |
