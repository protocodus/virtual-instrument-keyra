# Extended full-solver denormal diagnosis

No late denormal slowdown was reproduced in this bounded test. The pinned
extended-calibration float solver produced no sampled float subnormals during an
8.35-second C8 note/release render. Enabling FTZ/DAZ produced identical pressure
samples and sampled mechanical energy, without a CPU improvement. No portable
floor was run or added to a model, and no production FP-environment assumption
was introduced.

## Exact scope

The source is
`out/full-calibration/v2/mechanics/float-solver/grand.cpp`, SHA-256
`8d6abcd41d89a32b54366106c54ebb62a9b52de21dc21402a7c179c55af88e56`.
Its adjacent calibration header has SHA-256
`45935c2fbe67e1916ba1bf6eeb22f676f04639e70f5aa1e53e3bd5196c01a529`.
Copies and generated harness inputs are preserved under
`out/full-denormal-study/`. The source/header remain unchanged.

This is one synthetic C8/MIDI 108 note at velocity 93: note-on at 0.1 s, note-off
at 4.15 s, no pedal, 48 kHz, 8.35 seconds total. The exact 4.35 s CPU checkpoint covers
the acquisition-style duration; the same render continues through a longer
release tail. No real recording or reference feature file was opened, including
fresh A0/C8v8 cases. All 88 keys, 230 strings, 17,849 string modes and 475 board modes
remain. The extended tuning changes the mode count from the earlier 17,778 model.

Both runs use the same g++ binary and flags
`-O3 -DNDEBUG -std=c++17 -ffp-contract=off`, with no fast math. Solver CPU/wall
timing is collected in 0.25 s windows; diagnostic scans and file I/O are excluded.

## Results

| Measurement | Baseline | FTZ/DAZ diagnostic |
|---|---:|---:|
| CPU to 4.35 s audio | 14.273 s | 15.863 s |
| CPU for 8.35 s audio | 27.203 s | 32.736 s |
| Early CPU seconds/audio second (0.25–1.25s) | 3.204 | 3.092 |
| Late CPU seconds/audio second (5–8.35s) | 3.255 | 4.443 |
| Maximum sampled subnormal count, every category | 0 | 0 |
| Maximum absolute float64 pressure difference | — | 0 |
| Maximum sampled mechanical-energy difference | — | 0 J |

The baseline's late cost is within 1.6% of its early cost. The diagnostic FTZ/DAZ
run is slower overall, so these measurements do not justify using FTZ as a speed
fix. A single sequential pair does not establish that FTZ itself causes the
timing difference. Shared-host load, CPU frequency and other run-to-run effects
remain possible. The earlier 25 s versus 13 s wall-time observation remains
unexplained by this test; contention is plausible, not proven.

Classification uses IEEE 754 binary32 exponent/mantissa bits, equivalent to
`FP_SUBNORMAL`, so DAZ cannot make classification falsely report zero. Merely
converting a float subnormal to double would classify it as a normal double.
The 13 sampled categories cover string/board q/p, float port velocity, force and
impulse casts, port/radiation/rotation products, unison sum/impulse/update, and
radiation reduction intermediates.

On this x86 host, the caller's full MXCSR value was 0x1fa0. The diagnostic enabled
FTZ+DAZ as 0x9fe0 only inside a guarded standalone execution scope, then restored
0x1fa0. Both runs recorded successful restoration. This is a diagnostic, not a
proposal to change a DAW's floating-point environment.

## Limits and portable-fix decision

Quarter-second scans are snapshots, not an instruction-level trace. Brief
intermediate underflows between scans are not completely excluded. However,
identical full pressure output, a flat baseline late CPU cost and no FTZ speed
gain provide no evidence that denormals dominate this workload. Other rates,
velocities, pedals and longer tails are untested.

The tool contains an explicitly optional, **unexecuted** portable-floor trial
for a future reproduced case. It flushes tiny q/p state after updates, tests
incoming double force/impulse before float conversion, and computes tiny unison
impulses in double. A 1e-33 state floor has an instantaneous direct-observation
bound of approximately 1.62e-22 pressure for this prepared model. That bound is
not a proof about subsequent coupled trajectories. Any future trial must measure
the complete pressure null, finite behavior and energy change; this report does
not certify that trial or recommend promoting it.

Reproduce the bounded diagnosis:

```sh
python3 tools/probe_full_denormals.py
```

The report at `out/full-denormal-study/report.json` preserves every CPU window,
count, source/header/compiler identity, pressure/WAV hash, FP-control value and
comparison. Float64 pressure files retain differences below WAV quantization.
