# Recording benchmark: candidate 0.4.23 against shipping 0.4.22

Every train and dev note of `Tools/corpus/split-2026-10-27.json` scored by `Tools/benchmark_recordings.py` (metric definitions in its docstring; lower is better). Train recordings calibrated the candidate; dev recordings were never fitted. The first tables retain each run's independently filtered means; use the paired section for changes on the same observations.

## shipping 0.4.22

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sealed (48) | 8.75 | 0.84 | 4.61 | 5.68 | 5.97 | 7.27 | 5.74 | 6.28 | 0.25 | 4.08 | 4.95 | 2.46 |
| sealed / bass A0-B2 (16) | 7.59 | 0.72 | 2.91 | 6.11 | 5.16 | 5.58 | 5.91 | 3.55 | 0.17 | 1.86 | 9.12 | 0.74 |
| sealed / middle C3-B5 (16) | 9.05 | 0.79 | 2.58 | 6.36 | 6.99 | 7.56 | 5.93 | 6.20 | 0.16 | 5.60 | 1.00 | 3.93 |
| sealed / treble C6-C8 (16) | 9.62 | 1.01 | 8.34 | 4.56 | 5.76 | 8.66 | 5.41 | 9.09 | 0.42 | 4.78 | 4.72 | 2.72 |

## candidate 0.4.23

| cases | partial_db | tuning_cents | decay_db_s | attack_db | early_db | sustain_db | noise_db | ild_db | icc | envelope_db | rise_ms | level_db |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| sealed (48) | 8.10 | 0.76 | 4.00 | 5.73 | 5.93 | 6.65 | 5.82 | 6.31 | 0.25 | 3.67 | 7.37 | 2.43 |
| sealed / bass A0-B2 (16) | 7.58 | 0.68 | 2.90 | 6.21 | 5.16 | 5.67 | 6.18 | 3.59 | 0.16 | 2.38 | 16.28 | 0.68 |
| sealed / middle C3-B5 (16) | 8.53 | 0.74 | 2.48 | 6.44 | 6.96 | 6.73 | 5.92 | 6.21 | 0.15 | 4.21 | 1.01 | 3.72 |
| sealed / treble C6-C8 (16) | 8.18 | 0.86 | 6.62 | 4.53 | 5.67 | 7.56 | 5.40 | 9.12 | 0.43 | 4.42 | 4.83 | 2.88 |

## Independent-sample regressions (legacy)

Every note and role where candidate 0.4.23 is worse than shipping 0.4.22 by more than the tolerance (partial_db 0.5, tuning_cents 0.5, decay_db_s 1, attack_db 0.5, early_db 0.5, sustain_db 0.5, noise_db 0.5, ild_db 0.5, icc 0.02, envelope_db 0.5, rise_ms 1, level_db 0.5), largest first.

| note | role | metric | shipping 0.4.22 | candidate 0.4.23 |
|---|---|---|---|---|
| 39 | sealed | rise_ms | 9.12 | 16.28 |
| 39 | sealed | envelope_db | 1.86 | 2.38 |

## Paired changes

Only observations measurable in both runs contribute to each metric. Both level errors use the baseline full-case median gain (26.9307 dB). Lower errors are better; no metric tolerance changed.

| role | metric | paired n | baseline | candidate | change | baseline only | candidate only | neither |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| sealed | partial_db | 48 | 8.7525 | 8.0992 | -0.6533 | 0 | 0 | 0 |
| sealed | tuning_cents | 48 | 0.8402 | 0.7603 | -0.0799 | 0 | 0 | 0 |
| sealed | decay_db_s | 48 | 4.6099 | 3.9976 | -0.6123 | 0 | 0 | 0 |
| sealed | attack_db | 48 | 5.6773 | 5.7277 | 0.0504 | 0 | 0 | 0 |
| sealed | early_db | 48 | 5.9702 | 5.9270 | -0.0432 | 0 | 0 | 0 |
| sealed | sustain_db | 48 | 7.2658 | 6.6500 | -0.6158 | 0 | 0 | 0 |
| sealed | noise_db | 46 | 5.7424 | 5.8187 | 0.0762 | 0 | 0 | 2 |
| sealed | ild_db | 48 | 6.2787 | 6.3085 | 0.0298 | 0 | 0 | 0 |
| sealed | icc | 48 | 0.2492 | 0.2478 | -0.0014 | 0 | 0 | 0 |
| sealed | envelope_db | 48 | 4.0783 | 3.6681 | -0.4101 | 0 | 0 | 0 |
| sealed | rise_ms | 48 | 4.9475 | 7.3724 | 2.4249 | 0 | 0 | 0 |
| sealed | level_db | 48 | 2.4638 | 2.4406 | -0.0232 | 0 | 0 | 0 |

### Paired note regressions

| note | role | metric | paired n | baseline | candidate | change |
|---|---|---|---:|---:|---:|---:|
| 39 | sealed | rise_ms | 16 | 9.1172 | 16.2786 | 7.1615 |
| 39 | sealed | envelope_db | 16 | 1.8575 | 2.3754 | 0.5179 |

### Metric availability changes

Gaining or losing a score is not an error delta. Every changed observation is listed; lost coverage is not silently treated as improvement.

None.
