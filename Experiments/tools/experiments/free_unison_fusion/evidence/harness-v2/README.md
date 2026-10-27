# Current full API free/unison fusion harness

Source-only preparation. `run.py prepare` freezes source identities and builds
two correctness and two timing executables. It never constructs or advances a
model. It waits for the sibling `../v2/protocol.json` freeze and copies its
baseline/candidate sources. Public/runtime/Research files are never edited.

The correctness stage uses the current OriginalControl full API defaults,
including humanization, mechanisms, shared body coupling and the repetition
controller. Four rates (44.1/48/88.2/96 kHz) run music, repeated notes/pedal,
88-note dense tails and silence/reset. Events include offsets inside nominal
64-frame callbacks. The first two cases last .64 seconds and the others .4.
Every case requires exact pre-high-pass double pressure, final float audio and
five deep snapshots. Snapshot serialization has no struct padding or raw
addresses; it includes all baseline state, coefficients, controller/RNG,
mechanism ledgers/cache and output-filter memory. Candidate-only execution
views are covered by a separate prepare-time ownership/update inventory.

No actual correctness or timing command is authorized by source preparation.
Before `run.py correctness`, root must write `correctness-authorization.json`:

```json
{"protocol":{"path":"/absolute/path/protocol.json","sha256":"FROZEN_SHA"},"actions":["correctness"]}
```

Before `run.py performance`, root must separately write
`performance-authorization.json`, adding `correctness_result` with its exact
path/SHA and `actions:["performance"]`. The result must pass all correctness
cases. Execution is once-only; started markers and all outputs remain intact.

Timing uses separate executables with the diagnostic code preprocessed out;
the build rejects capture/snapshot symbols in those binaries. It retains all
three pairs in AB/BA/AB order at 48 and 96 kHz, using the existing actual-API
budget event/frame sequences (30720/30720/15360 frames). Each callback clock
covers event dispatch and process. Prepare, inventory, snapshots, pressure
capture, output/report writes and timing-vector bookkeeping are excluded.
Every callback's CPU/wall time, p50/p95/max and deadline misses remain recorded.
No trial is discarded and no realtime/Reason claim follows from this harness.

The harness does not add allocator interposition. Existing allocation-free API
qualification remains separate. The source protocol states all flags and scope;
no recording corpus is accessed.

This v2 harness adds only `-fopenmp-simd` and `KEYRA_FULL_FREE_UNISON_SIMD=1` to both arms. Pressure SIMD remains disabled. All cases, comparisons, source snapshots, timing recipes and policies remain as declared for v1. Binding/compilation awaits the explicit final v2 source freeze.
