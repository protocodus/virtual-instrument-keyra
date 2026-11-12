# Recording benchmark: 2.11.0 against 2.10.0

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.10.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.66 | 3.38 | 4.39 | 7.49 | 9.04 | 10.48 | 9.58 | 6.62 | 0.25 | 4.24 | 13.28 | 4.16 |
| dev (21) | 7.62 | 3.67 | 5.24 | 7.35 | 8.83 | 9.98 | 8.47 | 6.22 | 0.25 | 4.19 | 9.13 | 3.10 |
| train / bass A0-B2 (30) | 10.55 | 4.97 | 4.25 | 7.98 | 9.07 | 10.15 | 14.89 | 6.10 | 0.20 | 2.90 | 10.70 | 3.52 |
| train / middle C3-B5 (69) | 7.69 | 2.89 | 4.02 | 7.52 | 8.48 | 8.42 | 8.58 | 6.30 | 0.20 | 3.78 | 19.19 | 4.56 |
| train / treble C6-C8 (38) | 5.35 | 3.03 | 5.22 | 7.05 | 10.04 | 14.48 | 7.20 | 7.67 | 0.37 | 6.15 | 4.58 | 3.94 |
| dev / bass A0-B2 (5) | 9.95 | 4.95 | 4.55 | 7.65 | 9.23 | 10.23 | 12.89 | 4.35 | 0.24 | 2.37 | 3.39 | 2.00 |
| dev / middle C3-B5 (11) | 6.55 | 2.08 | 4.40 | 7.30 | 8.06 | 8.01 | 7.54 | 7.61 | 0.21 | 3.75 | 13.83 | 3.63 |
| dev / treble C6-C8 (5) | 7.64 | 5.88 | 7.76 | 7.17 | 10.12 | 14.07 | 6.97 | 5.04 | 0.35 | 6.97 | 4.56 | 3.03 |

## 2.11.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (137) | 7.66 | 3.35 | 4.34 | 7.50 | 9.00 | 10.52 | 9.66 | 6.62 | 0.25 | 4.22 | 13.16 | 4.17 |
| dev (21) | 7.53 | 3.44 | 4.70 | 7.33 | 8.70 | 9.93 | 8.47 | 6.21 | 0.25 | 4.12 | 9.11 | 3.07 |
| train / bass A0-B2 (30) | 10.47 | 4.79 | 4.13 | 8.04 | 9.09 | 10.24 | 15.22 | 6.12 | 0.20 | 2.75 | 10.74 | 3.52 |
| train / middle C3-B5 (69) | 7.70 | 2.90 | 3.97 | 7.51 | 8.39 | 8.46 | 8.59 | 6.29 | 0.20 | 3.79 | 18.94 | 4.58 |
| train / treble C6-C8 (38) | 5.35 | 3.03 | 5.22 | 7.05 | 10.04 | 14.48 | 7.20 | 7.67 | 0.37 | 6.15 | 4.58 | 3.96 |
| dev / bass A0-B2 (5) | 9.59 | 4.00 | 2.29 | 7.56 | 8.66 | 10.02 | 12.92 | 4.32 | 0.24 | 2.08 | 3.27 | 2.01 |
| dev / middle C3-B5 (11) | 6.55 | 2.07 | 4.40 | 7.30 | 8.06 | 8.01 | 7.54 | 7.61 | 0.21 | 3.75 | 13.83 | 3.56 |
| dev / treble C6-C8 (5) | 7.64 | 5.88 | 7.76 | 7.17 | 10.12 | 14.07 | 6.97 | 5.04 | 0.35 | 6.97 | 4.56 | 3.06 |

## Independent-sample regressions (legacy)

Every note and role where 2.11.0 is worse than 2.10.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.10.0 | 2.11.0 |
|---|---|---|---|---|
| 45 | train | envelope_db | 2.15 | 3.20 |
| 45 | train | noise_db | 13.64 | 14.66 |
| 48 | train | sustain_db | 8.98 | 9.95 |
| 45 | train | sustain_db | 7.98 | 8.86 |
| 33 | train | noise_db | 15.68 | 16.22 |
| 48 | train | envelope_db | 4.21 | 4.74 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (11.8555 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 21 | 7.6207 | 7.5333 | -0.0873 | 0 | 0 | 0 |
| dev | tuning_cents | 21 | 3.6657 | 3.4373 | -0.2284 | 0 | 0 | 0 |
| dev | decay_db_s | 21 | 5.2383 | 4.7002 | -0.5382 | 0 | 0 | 0 |
| dev | attack_db | 21 | 7.3546 | 7.3319 | -0.0228 | 0 | 0 | 0 |
| dev | early_db | 21 | 8.8307 | 8.6961 | -0.1346 | 0 | 0 | 0 |
| dev | sustain_db | 21 | 9.9799 | 9.9307 | -0.0493 | 0 | 0 | 0 |
| dev | noise_db | 20 | 8.4684 | 8.4741 | 0.0057 | 0 | 0 | 1 |
| dev | ild_db | 21 | 6.2212 | 6.2127 | -0.0085 | 0 | 0 | 0 |
| dev | icc | 21 | 0.2482 | 0.2499 | 0.0017 | 0 | 0 | 0 |
| dev | envelope_db | 21 | 4.1899 | 4.1186 | -0.0712 | 0 | 0 | 0 |
| dev | rise_ms | 21 | 9.1339 | 9.1062 | -0.0278 | 0 | 0 | 0 |
| dev | level_db | 21 | 3.1014 | 3.1004 | -0.0010 | 0 | 0 | 0 |
| train | partial_db | 137 | 7.6647 | 7.6561 | -0.0086 | 0 | 0 | 0 |
| train | tuning_cents | 137 | 3.3815 | 3.3477 | -0.0338 | 0 | 0 | 0 |
| train | decay_db_s | 135 | 4.3903 | 4.3381 | -0.0522 | 0 | 0 | 2 |
| train | attack_db | 137 | 7.4920 | 7.5008 | 0.0088 | 0 | 0 | 0 |
| train | early_db | 137 | 9.0401 | 8.9997 | -0.0404 | 0 | 0 | 0 |
| train | sustain_db | 137 | 10.4798 | 10.5176 | 0.0378 | 0 | 0 | 0 |
| train | noise_db | 137 | 9.5819 | 9.6576 | 0.0758 | 0 | 0 | 0 |
| train | ild_db | 135 | 6.6237 | 6.6217 | -0.0020 | 0 | 0 | 2 |
| train | icc | 135 | 0.2467 | 0.2470 | 0.0003 | 0 | 0 | 2 |
| train | envelope_db | 137 | 4.2434 | 4.2198 | -0.0236 | 0 | 0 | 0 |
| train | rise_ms | 137 | 13.2803 | 13.1620 | -0.1183 | 0 | 0 | 0 |
| train | level_db | 137 | 4.1591 | 4.1721 | 0.0131 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 45 | train | envelope_db | 5 | 2.1516 | 3.1966 | 1.0450 |
| 45 | train | noise_db | 5 | 13.6391 | 14.6561 | 1.0170 |
| 48 | train | sustain_db | 5 | 8.9828 | 9.9501 | 0.9672 |
| 45 | train | sustain_db | 5 | 7.9827 | 8.8641 | 0.8814 |
| 33 | train | noise_db | 5 | 15.6829 | 16.2224 | 0.5395 |
| 48 | train | envelope_db | 5 | 4.2102 | 4.7444 | 0.5342 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
