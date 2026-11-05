# Recording benchmark: candidate 0.4.23 against shipping 0.4.22

Every train and dev note of `Tools/corpus/split-helsinki-2026-10-28.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## shipping 0.4.22

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sealed (15) | 8.71 | 1.79 | 5.85 | 7.37 | 7.45 | 7.14 | 8.13 | 5.94 | 0.18 | 3.71 | 11.43 | 1.16 |
| sealed / bass A0-B2 (5) | 9.73 | 2.68 | 4.97 | 10.14 | 7.74 | 7.04 | 12.86 | 3.54 | 0.20 | 3.43 | 14.83 | 0.99 |
| sealed / middle C3-B5 (10) | 8.20 | 1.35 | 6.29 | 5.99 | 7.30 | 7.19 | 5.76 | 7.14 | 0.17 | 3.85 | 9.74 | 1.24 |
| sealed / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## candidate 0.4.23

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sealed (15) | 8.63 | 1.85 | 5.41 | 7.39 | 7.46 | 7.15 | 8.13 | 5.93 | 0.18 | 3.83 | 11.43 | 1.16 |
| sealed / bass A0-B2 (5) | 9.73 | 2.68 | 4.97 | 10.14 | 7.74 | 7.04 | 12.86 | 3.54 | 0.20 | 3.43 | 14.83 | 0.99 |
| sealed / middle C3-B5 (10) | 8.07 | 1.43 | 5.63 | 6.02 | 7.33 | 7.20 | 5.76 | 7.13 | 0.18 | 4.03 | 9.74 | 1.24 |
| sealed / treble C6-C8 (0) | - | - | - | - | - | - | - | - | - | - | - | - |

## Independent-sample regressions (legacy)

Every note and role where candidate 0.4.23 is worse than shipping 0.4.22 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

None.

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (19.7569 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| sealed | partial_db | 15 | 8.7093 | 8.6253 | -0.0840 | 0 | 0 | 0 |
| sealed | tuning_cents | 15 | 1.7949 | 1.8492 | 0.0542 | 0 | 0 | 0 |
| sealed | decay_db_s | 15 | 5.8480 | 5.4147 | -0.4334 | 0 | 0 | 0 |
| sealed | attack_db | 15 | 7.3729 | 7.3904 | 0.0175 | 0 | 0 | 0 |
| sealed | early_db | 15 | 7.4483 | 7.4642 | 0.0160 | 0 | 0 | 0 |
| sealed | sustain_db | 15 | 7.1372 | 7.1468 | 0.0096 | 0 | 0 | 0 |
| sealed | noise_db | 15 | 8.1275 | 8.1265 | -0.0009 | 0 | 0 | 0 |
| sealed | ild_db | 15 | 5.9364 | 5.9303 | -0.0061 | 0 | 0 | 0 |
| sealed | icc | 15 | 0.1820 | 0.1839 | 0.0019 | 0 | 0 | 0 |
| sealed | envelope_db | 15 | 3.7068 | 3.8294 | 0.1226 | 0 | 0 | 0 |
| sealed | rise_ms | 15 | 11.4319 | 11.4333 | 0.0014 | 0 | 0 | 0 |
| sealed | level_db | 15 | 1.1589 | 1.1589 | -0.0000 | 0 | 0 | 0 |

### Paired note regressions

None.

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
