# Recording benchmark: 0.4.30 against 0.4.29

Every train and dev note of `Tools/corpus/split-newyork-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 0.4.29

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (61) | 7.43 | 0.53 | 3.82 | 6.40 | 6.64 | 7.13 | 8.02 | 1.75 | 0.09 | 2.62 | 11.56 | 0.90 |
| dev (17) | 10.37 | 1.85 | 7.06 | 8.26 | 8.08 | 9.43 | 8.85 | 6.09 | 0.22 | 5.10 | 7.69 | 5.46 |
| train / bass A0-B2 (20) | 8.95 | 0.39 | 1.85 | 7.69 | 7.54 | 7.29 | 12.31 | 1.43 | 0.08 | 2.46 | 12.76 | 0.90 |
| train / middle C3-B5 (24) | 8.23 | 0.30 | 4.23 | 5.64 | 6.45 | 6.93 | 5.63 | 1.54 | 0.11 | 2.58 | 15.83 | 0.25 |
| train / treble C6-C8 (17) | 4.34 | 1.05 | 6.78 | 5.93 | 5.87 | 7.22 | 6.34 | 2.90 | 0.07 | 2.87 | 4.12 | 1.84 |
| dev / bass A0-B2 (5) | 10.31 | 2.18 | 2.68 | 7.38 | 8.09 | 8.94 | 11.41 | 3.94 | 0.13 | 4.26 | 8.50 | 3.71 |
| dev / middle C3-B5 (5) | 9.77 | 1.00 | 4.29 | 7.43 | 7.34 | 9.81 | 6.51 | 5.58 | 0.21 | 4.71 | 8.33 | 4.16 |
| dev / treble C6-C8 (7) | 10.84 | 2.22 | 12.16 | 9.48 | 8.60 | 9.51 | 8.69 | 7.99 | 0.29 | 5.98 | 6.66 | 7.64 |

## 0.4.30

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (61) | 7.42 | 0.53 | 3.82 | 6.39 | 6.64 | 7.13 | 7.98 | 1.75 | 0.09 | 2.62 | 11.56 | 0.90 |
| dev (17) | 10.37 | 1.85 | 7.06 | 8.27 | 8.08 | 9.43 | 8.87 | 6.09 | 0.22 | 5.10 | 7.69 | 5.46 |
| train / bass A0-B2 (20) | 8.91 | 0.39 | 1.86 | 7.68 | 7.53 | 7.29 | 12.31 | 1.43 | 0.08 | 2.46 | 12.76 | 0.90 |
| train / middle C3-B5 (24) | 8.23 | 0.30 | 4.23 | 5.65 | 6.45 | 6.93 | 5.53 | 1.54 | 0.11 | 2.58 | 15.83 | 0.25 |
| train / treble C6-C8 (17) | 4.34 | 1.05 | 6.78 | 5.93 | 5.87 | 7.22 | 6.34 | 2.90 | 0.07 | 2.87 | 4.12 | 1.84 |
| dev / bass A0-B2 (5) | 10.31 | 2.18 | 2.68 | 7.39 | 8.09 | 8.94 | 11.48 | 3.94 | 0.13 | 4.26 | 8.50 | 3.71 |
| dev / middle C3-B5 (5) | 9.77 | 1.00 | 4.29 | 7.43 | 7.34 | 9.81 | 6.51 | 5.58 | 0.21 | 4.71 | 8.33 | 4.16 |
| dev / treble C6-C8 (7) | 10.84 | 2.22 | 12.16 | 9.48 | 8.60 | 9.51 | 8.69 | 7.99 | 0.29 | 5.98 | 6.66 | 7.64 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.30 is worse than 0.4.29 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.8189 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 17 | 10.3714 | 10.3714 | -0.0000 | 0 | 0 | 0 |
| dev | tuning_cents | 17 | 1.8501 | 1.8501 | 0.0000 | 0 | 0 | 0 |
| dev | decay_db_s | 17 | 7.0600 | 7.0600 | 0.0000 | 0 | 0 | 0 |
| dev | attack_db | 17 | 8.2620 | 8.2658 | 0.0037 | 0 | 0 | 0 |
| dev | early_db | 17 | 8.0786 | 8.0771 | -0.0015 | 0 | 0 | 0 |
| dev | sustain_db | 17 | 9.4329 | 9.4324 | -0.0005 | 0 | 0 | 0 |
| dev | noise_db | 17 | 8.8478 | 8.8707 | 0.0229 | 0 | 0 | 0 |
| dev | ild_db | 17 | 6.0890 | 6.0890 | 0.0000 | 0 | 0 | 0 |
| dev | icc | 17 | 0.2207 | 0.2207 | -0.0000 | 0 | 0 | 0 |
| dev | envelope_db | 17 | 5.1042 | 5.1042 | -0.0000 | 0 | 0 | 0 |
| dev | rise_ms | 17 | 7.6921 | 7.6921 | 0.0000 | 0 | 0 | 0 |
| dev | level_db | 17 | 5.4612 | 5.4612 | 0.0000 | 0 | 0 | 0 |
| train | partial_db | 60 | 7.4297 | 7.4187 | -0.0110 | 0 | 0 | 1 |
| train | tuning_cents | 60 | 0.5304 | 0.5304 | 0.0000 | 0 | 0 | 1 |
| train | decay_db_s | 54 | 3.8213 | 3.8236 | 0.0023 | 0 | 0 | 7 |
| train | attack_db | 61 | 6.3953 | 6.3932 | -0.0021 | 0 | 0 | 0 |
| train | early_db | 61 | 6.6435 | 6.6411 | -0.0024 | 0 | 0 | 0 |
| train | sustain_db | 59 | 7.1262 | 7.1258 | -0.0005 | 0 | 0 | 2 |
| train | noise_db | 61 | 8.0175 | 7.9813 | -0.0362 | 0 | 0 | 0 |
| train | ild_db | 54 | 1.7498 | 1.7514 | 0.0015 | 0 | 0 | 7 |
| train | icc | 54 | 0.0938 | 0.0937 | -0.0001 | 0 | 0 | 7 |
| train | envelope_db | 61 | 2.6209 | 2.6209 | 0.0000 | 0 | 0 | 0 |
| train | rise_ms | 61 | 11.5619 | 11.5606 | -0.0014 | 0 | 0 | 0 |
| train | level_db | 61 | 0.9031 | 0.9031 | 0.0000 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
