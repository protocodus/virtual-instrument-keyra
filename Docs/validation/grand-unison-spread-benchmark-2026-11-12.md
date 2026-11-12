# Recording benchmark: 2.8.0 against 2.7.0

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## 2.7.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.11 | 2.00 | 5.07 | 6.67 | 6.77 | 9.01 | 7.34 | 5.02 | 0.20 | 4.38 | 14.98 | 2.36 |
| dev (156) | 7.86 | 2.10 | 4.23 | 6.28 | 6.27 | 8.24 | 6.75 | 5.30 | 0.19 | 4.35 | 12.65 | 2.11 |
| train / bass A0-B2 (84) | 9.17 | 2.54 | 2.66 | 6.11 | 5.77 | 7.04 | 6.78 | 4.74 | 0.20 | 3.86 | 21.35 | 2.15 |
| train / middle C3-B5 (108) | 7.34 | 1.25 | 3.98 | 6.23 | 6.66 | 8.34 | 7.31 | 7.07 | 0.20 | 4.77 | 16.34 | 2.16 |
| train / treble C6-C8 (84) | 8.06 | 2.42 | 9.12 | 7.78 | 7.91 | 11.84 | 7.93 | 2.48 | 0.18 | 4.39 | 6.87 | 2.82 |
| dev / bass A0-B2 (44) | 9.85 | 3.16 | 2.41 | 6.17 | 5.91 | 6.65 | 6.49 | 5.11 | 0.21 | 3.39 | 21.99 | 2.69 |
| dev / middle C3-B5 (68) | 7.01 | 1.13 | 3.32 | 5.96 | 6.04 | 7.75 | 6.74 | 7.33 | 0.16 | 4.36 | 11.71 | 1.87 |
| dev / treble C6-C8 (44) | 7.20 | 2.56 | 7.53 | 6.88 | 6.99 | 10.58 | 7.01 | 2.21 | 0.21 | 5.30 | 4.77 | 1.91 |

## 2.8.0

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| train (276) | 8.07 | 2.07 | 4.50 | 6.67 | 6.68 | 8.80 | 7.35 | 5.01 | 0.20 | 4.38 | 15.00 | 2.34 |
| dev (156) | 7.74 | 2.21 | 3.80 | 6.26 | 6.29 | 7.85 | 6.78 | 5.31 | 0.19 | 4.18 | 12.65 | 2.07 |
| train / bass A0-B2 (84) | 9.16 | 2.54 | 2.66 | 6.11 | 5.77 | 7.04 | 6.79 | 4.74 | 0.20 | 3.86 | 21.35 | 2.21 |
| train / middle C3-B5 (108) | 7.06 | 1.34 | 4.20 | 6.16 | 6.49 | 7.73 | 7.26 | 7.07 | 0.20 | 4.35 | 16.34 | 2.02 |
| train / treble C6-C8 (84) | 8.27 | 2.55 | 6.87 | 7.86 | 7.82 | 11.94 | 8.03 | 2.46 | 0.18 | 4.94 | 6.92 | 2.88 |
| dev / bass A0-B2 (44) | 9.84 | 3.16 | 2.42 | 6.17 | 5.91 | 6.65 | 6.62 | 5.11 | 0.21 | 3.39 | 22.00 | 2.79 |
| dev / middle C3-B5 (68) | 6.65 | 1.23 | 3.42 | 5.88 | 6.17 | 6.88 | 6.68 | 7.33 | 0.17 | 4.09 | 11.71 | 1.71 |
| dev / treble C6-C8 (44) | 7.34 | 2.77 | 5.80 | 6.94 | 6.86 | 10.54 | 7.10 | 2.25 | 0.20 | 5.12 | 4.76 | 1.91 |

## Independent-sample regressions (legacy)

Every note and role where 2.8.0 is worse than 2.7.0 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | 2.7.0 | 2.8.0 |
|---|---|---|---|---|
| 90 | dev | envelope_db | 4.51 | 9.41 |
| 93 | train | sustain_db | 5.59 | 10.36 |
| 93 | dev | sustain_db | 5.51 | 10.15 |
| 90 | train | envelope_db | 4.21 | 8.50 |
| 93 | dev | envelope_db | 3.93 | 7.87 |
| 93 | train | envelope_db | 4.17 | 8.08 |
| 90 | train | sustain_db | 7.36 | 10.48 |
| 90 | dev | sustain_db | 8.02 | 10.65 |
| 93 | dev | partial_db | 4.55 | 6.00 |
| 93 | train | partial_db | 5.77 | 7.22 |
| 102 | dev | sustain_db | 10.11 | 11.55 |
| 102 | train | sustain_db | 11.06 | 12.41 |
| 66 | dev | envelope_db | 2.51 | 3.54 |
| 90 | train | partial_db | 4.96 | 5.94 |
| 84 | dev | tuning_cents | 1.62 | 2.58 |
| 66 | train | envelope_db | 2.67 | 3.59 |
| 84 | train | tuning_cents | 1.70 | 2.61 |
| 75 | dev | early_db | 5.51 | 6.41 |
| 90 | dev | partial_db | 4.62 | 5.49 |
| 90 | dev | decay_db_s | 4.55 | 6.02 |
| 78 | dev | decay_db_s | 5.61 | 6.90 |
| 78 | train | decay_db_s | 5.54 | 6.74 |
| 108 | dev | partial_db | 9.00 | 9.56 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (24.8287 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| dev | partial_db | 156 | 7.8622 | 7.7435 | -0.1187 | 0 | 0 | 0 |
| dev | tuning_cents | 156 | 2.1031 | 2.2080 | 0.1049 | 0 | 0 | 0 |
| dev | decay_db_s | 155 | 4.2307 | 3.7974 | -0.4332 | 0 | 0 | 1 |
| dev | attack_db | 156 | 6.2784 | 6.2611 | -0.0173 | 0 | 0 | 0 |
| dev | early_db | 156 | 6.2730 | 6.2933 | 0.0204 | 0 | 0 | 0 |
| dev | sustain_db | 156 | 8.2386 | 7.8491 | -0.3895 | 0 | 0 | 0 |
| dev | noise_db | 153 | 6.7468 | 6.7823 | 0.0355 | 0 | 0 | 3 |
| dev | ild_db | 154 | 5.3025 | 5.3123 | 0.0098 | 0 | 0 | 2 |
| dev | icc | 154 | 0.1874 | 0.1876 | 0.0002 | 0 | 0 | 2 |
| dev | envelope_db | 156 | 4.3517 | 4.1825 | -0.1692 | 0 | 0 | 0 |
| dev | rise_ms | 156 | 12.6546 | 12.6532 | -0.0015 | 0 | 0 | 0 |
| dev | level_db | 156 | 2.1149 | 2.0701 | -0.0447 | 0 | 0 | 0 |
| train | partial_db | 276 | 8.1131 | 8.0669 | -0.0462 | 0 | 0 | 0 |
| train | tuning_cents | 276 | 1.9976 | 2.0742 | 0.0766 | 0 | 0 | 0 |
| train | decay_db_s | 271 | 5.0694 | 4.4968 | -0.5725 | 0 | 0 | 5 |
| train | attack_db | 276 | 6.6677 | 6.6653 | -0.0023 | 0 | 0 | 0 |
| train | early_db | 276 | 6.7706 | 6.6752 | -0.0953 | 0 | 0 | 0 |
| train | sustain_db | 276 | 9.0139 | 8.8020 | -0.2119 | 0 | 0 | 0 |
| train | noise_db | 274 | 7.3368 | 7.3506 | 0.0138 | 0 | 0 | 2 |
| train | ild_db | 270 | 5.0182 | 5.0134 | -0.0049 | 0 | 0 | 6 |
| train | icc | 270 | 0.1977 | 0.1973 | -0.0004 | 0 | 0 | 6 |
| train | envelope_db | 276 | 4.3772 | 4.3835 | 0.0063 | 0 | 0 | 0 |
| train | rise_ms | 276 | 14.9787 | 14.9971 | 0.0184 | 0 | 0 | 0 |
| train | level_db | 276 | 2.3584 | 2.3424 | -0.0160 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 90 | dev | envelope_db | 4 | 4.5096 | 9.4123 | 4.9027 |
| 93 | train | sustain_db | 12 | 5.5871 | 10.3630 | 4.7758 |
| 93 | dev | sustain_db | 4 | 5.5087 | 10.1469 | 4.6382 |
| 90 | train | envelope_db | 12 | 4.2068 | 8.5011 | 4.2943 |
| 93 | dev | envelope_db | 4 | 3.9274 | 7.8698 | 3.9424 |
| 93 | train | envelope_db | 12 | 4.1687 | 8.0802 | 3.9116 |
| 90 | train | sustain_db | 12 | 7.3554 | 10.4814 | 3.1260 |
| 90 | dev | sustain_db | 4 | 8.0231 | 10.6490 | 2.6259 |
| 93 | dev | partial_db | 4 | 4.5462 | 6.0047 | 1.4585 |
| 93 | train | partial_db | 12 | 5.7666 | 7.2238 | 1.4572 |
| 102 | dev | sustain_db | 4 | 10.1068 | 11.5473 | 1.4405 |
| 102 | train | sustain_db | 12 | 11.0626 | 12.4091 | 1.3464 |
| 66 | dev | envelope_db | 4 | 2.5051 | 3.5393 | 1.0342 |
| 90 | train | partial_db | 12 | 4.9609 | 5.9442 | 0.9833 |
| 84 | dev | tuning_cents | 4 | 1.6165 | 2.5849 | 0.9684 |
| 66 | train | envelope_db | 12 | 2.6681 | 3.5903 | 0.9222 |
| 84 | train | tuning_cents | 12 | 1.6983 | 2.6089 | 0.9107 |
| 75 | dev | early_db | 16 | 5.5083 | 6.4118 | 0.9035 |
| 90 | dev | partial_db | 4 | 4.6171 | 5.4856 | 0.8685 |
| 90 | dev | decay_db_s | 4 | 4.5471 | 6.0190 | 1.4719 |
| 78 | dev | decay_db_s | 4 | 5.6065 | 6.9036 | 1.2971 |
| 78 | train | decay_db_s | 12 | 5.5377 | 6.7368 | 1.1991 |
| 108 | dev | partial_db | 4 | 9.0005 | 9.5594 | 0.5589 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
