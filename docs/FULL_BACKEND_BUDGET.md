# Full physical API callback budget

This report measures the frozen API **before the zero-gap repetition fix and
guarded pressure-SIMD integration**. Its source/header hashes and actual input
copies are under `out/full-backend-budget/{native,scalar,profile}`; there is no
`snapshots/` subdirectory. These timings are historical evidence for that
version, not a timing result for the subsequently changed API.

The measured complete API remains slower than realtime on this Linux host.
At 48 kHz, a 64-frame callback has **1.333 ms** available. The measured native
build consumes 3.31–3.47 CPU seconds per audio second, and all 1,200 measured
native callbacks exceed that deadline. This is an actual `FullInstrument`
measurement with its default strike controller, variation and connected
mechanical sources, rather than a string-only workload or a CLI estimate.

The original control calibration, 230 strings, 17,778 modes and 475 board modes
remain present. The initial-hammer rest-position fix is included. No samples,
recordings, feature exports, mode cuts, altered floating-point environment or
new calibration are involved.

## Budget and workload

`Validation/full-backend-budget.json` retains every callback CPU/wall duration,
event count, exact event schedule, source/binary/audio hashes and diagnostic
counters. `tools/probe_full_backend_budget.py` snapshots the API, prepared model,
calibration and headers under `out/full-backend-budget` before compiling.

The three deterministic cases last 0.64, 0.64 and 0.32 seconds. Every event is
at a real 64-frame callback boundary. They cover a short chord/melody with
pedal transitions, rapid same-key requests followed by released repetitions,
and an 88-key strike/release with a sustained and damped tail. The controller
admits 5, 10 and 88 strikes respectively; no solver fault or unsafe launch is
reported. These cases do not establish long-tail, multi-instance or musical
release coverage.

| Native case | CPU s/audio s | Callback CPU p50 | CPU p95 | CPU maximum |
|---|---:|---:|---:|---:|
| Music | 3.308 | 4.358 ms | 4.752 ms | 7.881 ms |
| Repeats/pedal | 3.417 | 4.394 ms | 5.203 ms | 28.265 ms |
| Dense 88/tail | 3.469 | 4.426 ms | 5.434 ms | 19.694 ms |

Callback timing includes event dispatch and processing. Preparation, report
generation and final audio writes are excluded. The total process-CPU window
also includes the benchmark's clock and preallocated result-vector bookkeeping.
The dense case's first callback contains 89 events and is its measured maximum.
The large repeat maximum occurs in a callback with no event; its cause and
repeatability are not established by this bounded run.

The scalar SDK approximation uses the same strict flags plus
`-fno-tree-vectorize`. It consumes 5.762, 4.825 and 5.321 CPU s/audio s in the
three cases. Its p95 callback CPU times are 11.096, 8.789 and 8.850 ms. The report
also retains isolated maxima of 199.618 and 143.826 ms. They are observed
thread-CPU spikes, with no established hardware, denormal, scheduler or model
cause. All scalar callbacks also miss the deadline. Native and scalar audio
bytes match in all three cases.

The compiler is GCC 14.2 with `-O3 -DNDEBUG -std=c++17 -ffp-contract=off
-fno-exceptions -fno-rtti -fno-builtin`; the native build allows automatic
vectorization. This is a host approximation, not the Jukebox compiler or a
Reason callback test. CPU and wall timing are both retained: wall times include
descheduling on the shared host, while callback CPU clocks measure the current
thread. Short-run maxima are neither a certified worst case nor grounds to
discard an outlier.

## Where the native full model spends time

A second copied-source build places thread-CPU timers around stage boundaries.
All three of its audio outputs match the uninstrumented native outputs byte
for byte. The original API and model sources are never edited.

| Stage | Share of measured exclusive stage time across cases |
|---|---:|
| Reciprocal bridge plus fused string radiation | 53.1–55.3% |
| String/board oscillators, including hammer contact | 18.6–20.8% |
| Grouped common-unison coupling | 12.4–12.8% |
| Coupled mechanical sources and their body observations/reactions | 9.0–9.2% |
| Damping/pedal controls | 1.6–2.1% |
| Final board/string observation | 1.6–1.7% |
| Strike/recovery controller | 0.5–1.5% |

Contact alone is **inside** the oscillator stage: about 0.05% of exclusive stage
time for music, 0.13% for repetitions and 1.79% for the dense case. It must not be
added a second time. This average does not establish its share of the most
expensive individual callback; a faster contact solve may still improve a dense
attack peak.

The instrumented runs consume 5.3–7.8% more process CPU than the preceding
native runs. That difference includes timer/code-layout effects and run
variation. An empty timer pair costs approximately 0.339 microseconds on this
run. Timer reads/accumulations therefore make these approximate stage shares,
especially for the smaller stages. They are sufficient to identify the dominant
throughput cost, without treating the profile as zero-overhead timing.

## Actionable next work

The largest target is the bridge/radiation path. Every frame reduces all string
port velocities, solves the reciprocal three-port board junction, then applies
every string impulse while reducing its stereo radiation. Sparse playing still
advances the unstruck strings because they participate in sympathetic
resonance. A future layout/reduction or accuracy tradeoff should be evaluated
against those coupled ports and actual acoustic energy, preserving the full
control for comparison. A string-only waveguide speedup cannot be applied
directly to this whole-instrument budget.

The mechanical path is a useful smaller target. It currently observes the
475-mode board before and after source coupling, recomputes body-port reductions
for four sources and may write board impulses separately. A cached three-port
board velocity/Gram representation plus accumulated reaction and an analytic
observer correction may reduce repeated work. It needs a simultaneous energy
and observation derivation: simply removing reverse reaction would change the
connected model. No such optimization is adopted by this study.

The controller's small measured share supports keeping stateful hammer recovery
and per-key variation. Removing those mechanisms would not resolve the current
deadline gap. Neither the new API nor this report establishes Reason production
readiness or realtime feasibility on supported user machines.

## Reproduction

From the repository root on Linux with GCC and NumPy:

```sh
OPENBLAS_NUM_THREADS=1 python3 tools/probe_full_backend_budget.py \
  --output out/full-backend-budget-recheck \
  --report out/full-backend-budget-recheck/report.json
```

The output directory must be empty. Inputs are rehashed before compilation and
after every variant; changes abort the run. The profile's sound must remain
byte-identical to the native copy. The recorded source hashes bind the results
to the specific full API version and control calibration, and all output audio
is raw float32 planar stereo with no normalizing, limiting or added room.
