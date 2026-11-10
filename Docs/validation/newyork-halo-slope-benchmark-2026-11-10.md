# Recording benchmark: 0.4.31 against 0.4.30

Every train and dev note of `Tools/corpus/split-newyork-2026-10-31.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

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

## 0.4.31

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (61) | 7.41 | 0.53 | 3.82 | 6.01 | 6.35 | 6.99 | 6.46 | 1.74 | 0.09 | 2.56 | 11.88 | 0.90 |
| dev (17) | 10.42 | 1.87 | 7.08 | 8.07 | 8.05 | 9.46 | 8.02 | 6.09 | 0.22 | 5.08 | 7.79 | 5.46 |
| train / bass A0-B2 (20) | 8.89 | 0.39 | 1.83 | 6.52 | 6.63 | 6.90 | 7.61 | 1.42 | 0.08 | 2.29 | 13.73 | 0.88 |
| train / middle C3-B5 (24) | 8.23 | 0.30 | 4.23 | 5.64 | 6.45 | 6.93 | 5.58 | 1.54 | 0.11 | 2.57 | 15.83 | 0.25 |
| train / treble C6-C8 (17) | 4.34 | 1.05 | 6.78 | 5.93 | 5.87 | 7.22 | 6.34 | 2.90 | 0.07 | 2.87 | 4.12 | 1.84 |
| dev / bass A0-B2 (5) | 10.47 | 2.25 | 2.73 | 6.72 | 7.99 | 9.03 | 8.58 | 3.93 | 0.13 | 4.19 | 8.82 | 3.70 |
| dev / middle C3-B5 (5) | 9.77 | 1.00 | 4.29 | 7.43 | 7.34 | 9.81 | 6.51 | 5.58 | 0.21 | 4.71 | 8.33 | 4.16 |
| dev / treble C6-C8 (7) | 10.84 | 2.22 | 12.16 | 9.48 | 8.60 | 9.51 | 8.69 | 7.99 | 0.29 | 5.98 | 6.66 | 7.64 |

## Independent-sample regressions (legacy)

Every note and role where 0.4.31 is worse than 0.4.30 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 0.4.30 | 0.4.31 |
|---|---|---|---|---|
| 29 | train | rise_ms | 24.56 | 26.46 |
| 34 | train | rise_ms | 5.20 | 6.33 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.8189 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 17 | 10.3714 | 10.4187 | 0.0474 | 0 | 0 | 0 |
| dev | tuning_cents | 17 | 1.8501 | 1.8689 | 0.0188 | 0 | 0 | 0 |
| dev | decay_db_s | 17 | 7.0600 | 7.0763 | 0.0164 | 0 | 0 | 0 |
| dev | attack_db | 17 | 8.2658 | 8.0681 | -0.1977 | 0 | 0 | 0 |
| dev | early_db | 17 | 8.0771 | 8.0498 | -0.0273 | 0 | 0 | 0 |
| dev | sustain_db | 17 | 9.4324 | 9.4604 | 0.0279 | 0 | 0 | 0 |
| dev | noise_db | 17 | 8.8707 | 8.0177 | -0.8530 | 0 | 0 | 0 |
| dev | ild_db | 17 | 6.0890 | 6.0863 | -0.0027 | 0 | 0 | 0 |
| dev | icc | 17 | 0.2207 | 0.2208 | 0.0001 | 0 | 0 | 0 |
| dev | envelope_db | 17 | 5.1042 | 5.0818 | -0.0225 | 0 | 0 | 0 |
| dev | rise_ms | 17 | 7.6921 | 7.7852 | 0.0931 | 0 | 0 | 0 |
| dev | level_db | 17 | 5.4612 | 5.4594 | -0.0018 | 0 | 0 | 0 |
| train | partial_db | 60 | 7.4187 | 7.4137 | -0.0050 | 0 | 0 | 1 |
| train | tuning_cents | 60 | 0.5304 | 0.5303 | -0.0001 | 0 | 0 | 1 |
| train | decay_db_s | 54 | 3.8236 | 3.8153 | -0.0083 | 0 | 0 | 7 |
| train | attack_db | 61 | 6.3932 | 6.0096 | -0.3836 | 0 | 0 | 0 |
| train | early_db | 61 | 6.6411 | 6.3472 | -0.2939 | 0 | 0 | 0 |
| train | sustain_db | 59 | 7.1258 | 6.9928 | -0.1329 | 0 | 0 | 2 |
| train | noise_db | 61 | 7.9813 | 6.4567 | -1.5245 | 0 | 0 | 0 |
| train | ild_db | 54 | 1.7514 | 1.7445 | -0.0069 | 0 | 0 | 7 |
| train | icc | 54 | 0.0937 | 0.0926 | -0.0011 | 0 | 0 | 7 |
| train | envelope_db | 61 | 2.6209 | 2.5613 | -0.0596 | 0 | 0 | 0 |
| train | rise_ms | 61 | 11.5606 | 11.8809 | 0.3204 | 0 | 0 | 0 |
| train | level_db | 61 | 0.9031 | 0.8987 | -0.0044 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 29 | train | rise_ms | 5 | 24.5557 | 26.4557 | 1.9000 |
| 34 | train | rise_ms | 5 | 5.2046 | 6.3338 | 1.1292 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
