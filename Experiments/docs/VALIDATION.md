# Live model validation — 0.2 development preview

The product target is a Reason Rack Extension. These are Linux engine and
headless-adapter results. They do not establish Reason/Recon behavior, a usable
`.u45`, production readiness, or the intended price.

## Recording agreement

The original Salamander grand split, source and evidence remain unchanged. The
current grand adds a separately locked expansion: **26 fitting cases at 13
pitches**, with **seven new recordings reserved until candidate freeze**.
[GrandExpanded](../References/GrandExpanded/README.md) records the source identity,
roles and evaluation receipt. The upright retains its independent ten fitting
cases and seven excluded cases. Pitch-analysis fallback values are excluded; the
unidentifiable C6 soft upright shape borrows the same-note loud training shape
with measured RMS scaling, recorded explicitly as a prior.

On the **seven newly reserved grand cases**, versus the five-anchor phase-aware
model, lower error is better:

| Metric | Five anchors | Current thirteen anchors |
|---|---:|---:|
| Harmonic levels | 5.83 dB | 2.97 dB |
| Broad spectral bands | 14.17 dB | 12.48 dB |
| Partial decay slopes | 3.17 dB/s | 2.45 dB/s |
| Attack rise time | 5.26 ms | 4.26 ms |
| Envelope | 4.26 dB | 2.46 dB |

Every case improves in harmonic levels. This is not uniform improvement: A3v12
attack error increases by 3.38 ms; A4v8 attack increases by 2.13 ms and decay by
0.31 dB/s. The three A3 velocity cases at one completely excluded pitch still average
4.97 dB harmonic and 4.11 dB envelope error. Candidate selection was made from
the predetermined coverage, training-only fits and passing tests before opening
these recordings. Full results and immutable freeze hashes are in
[fresh-grand.json](../Validation/fresh-grand.json). These seven cases are now
regression evidence; they cannot be reused as a fresh model-selection test.

Across the **twelve original in-range excluded cases**, which are historical
regression evidence for this iteration:

| Metric | Preserved mechanical v2 | Live modal engine |
|---|---:|---:|
| Harmonic levels | 4.96 dB | 3.13 dB |
| Broad spectral bands | 12.09 dB | 11.54 dB |
| Partial decay slopes | 2.83 dB/s | 2.15 dB/s |
| Attack rise time | 19.17 ms | 9.81 ms |
| Envelope | 4.30 dB | 2.54 dB |

The current model improves the aggregate errors above. It is a different reduced model, not an
optimization preserving the mechanical solver's behavior. In particular, C6v8
regresses in spectrum, attack and envelope; F#5v8 regresses in harmonic
levels; several pitch-interpolation cases regress in decay. Every case and
baseline delta, including the edge notes, is retained in
[live-grand.json](../Validation/live-grand.json).

The **seven excluded upright cases** average **5.84 dB harmonic**, **8.25 dB
broad-band**, **6.70 dB/s decay**, **8.63 ms attack** and **3.04 dB envelope**
error. There was no prior upright candidate, so no improvement claim is made.
These errors still leave substantial work, especially in decay and spectral
generalization. See [live-upright.json](../Validation/live-upright.json).

All comparisons reuse the preserved onset alignment and stereo-power feature
extractor. One early RMS gain per comparison is fixed through the decay. This
helps assess timbre but does not validate absolute loudness or dynamics. Separate
velocity tests detect inverted dynamics. The upright source layers are ordinal;
40/61/93 MIDI values are documented input proxies, not measured hammer velocities.
Both corpora are narrow and contain microphone/room/editing confounds. These
metrics are not perceptual scores, blind-test results or a percentage of realism.

## Default-model corrections and unresolved errors

The positive two-stage fit now includes the live grand's known 0.23-cent
difference-frequency cross term. A known-signal check across 27 cases/four
windows agrees with sampled Hann band powers within 0.00270 dB; the previous
coherent assumption can miss by 5.55 dB. This is a model-consistency correction,
not identification of true unison geometry. The original coherent header can
still be reproduced with `--legacy-coherent`.

Positive component amplitudes interpolate linearly across pitches, preventing
nearly zero fast/late components from erasing each other between fitted notes.
Training-only cross-validation and the component-swap diagnostic are in
[interpolation-cv.json](../Validation/interpolation-cv.json). Variable-size anchor
lookup preserves the original five-anchor audio byte for byte. Cached source
logarithms reduce measured attack callback cost by about 17–20% with byte-identical
output for the stated four-rate event stream; see
[attack-optimization.json](../Validation/attack-optimization.json).

The default still has substantial gaps. In C6 training tails, much of the
recorded late energy is below the played fundamental, including subsonic and
50 Hz-related content with weak soft/loud scaling. Its origin cannot be uniquely
classified as body/room response or acquisition noise. The original full-envelope
metric is retained; no hum/noise was fitted to hide it. See
[default-training-audit.json](../Validation/default-training-audit.json).

Stereo also needs work: the first C4v12 window has recorded left/right
correlation 0.54 versus approximately 1.00 in the current default. The measured
power agreement does not establish a matched microphone image. The
[stereo audit](../Validation/default-stereo-audit.json) keeps that discrepancy
visible instead of treating it as a new realism score. A training-only complex
observation study is retained separately; static phase/gain interpolation is not
promoted when its pitch cross-validation worsens.

Broad attack-ramp fitting was rejected. Matching one rise metric required
150–156 ms bass ramps and worsened several early-envelope/energy witnesses.
Native candidates and regressions remain in
[attack-proposal.json](../Validation/attack-proposal.json); default attacks were
not changed to chase that metric. These gaps, plus the remaining A3 mismatch, mean
recording parity has not been established.

## Controls and reliability

Twelve engine test groups cover invalid-rate rejection without state changes,
44.1/48/88.2/96 kHz/full keyboard/malformed inputs, block partitions, note IDs,
channel isolation, polyphony, partial sustain/re-pedal, parameter bounds and
signal influence, mic mono compatibility, velocity sweeps and anchor continuity,
automation, reset/independence, tuning, and C++ allocation traps. The same tests
also pass with a host approximation of Rack flags: no exceptions, no RTTI,
`-fno-builtin`, no automatic vectorization and no FP contraction.

The tests found and fixed two important defects: per-component velocity
extrapolation could make pianissimo louder than forte; long-held notes could
enter subnormal arithmetic and slow processing by about five times. The engine
now uses bounded full-note velocity scaling/energy normalization and removes
inaudible modal pairs. `prepare()` returns false for invalid rates while
preserving playing state, allowing exception-free wrappers.

The separate physical research path also passes contact/action, persistent
strings/bridge/wood, acoustic-load and complete-chain tests. Its 18 isolated and
connected benchmark scenarios have finite-output and activation witnesses;
components sharing a solver are labeled accordingly. [MODULES.md](MODULES.md)
documents the port graph, energy balances and approximations. This candidate
has not replaced the default: action latency, CPU cost and unmeasured component
parameters still require recording and host validation.

The Linux CLAP harness passes state/partial-stream, sample-offset, malformed
event, note-lifetime and concurrent-state tests. The VST3 harness passes the
official SDK validator (**47 tests, zero failures**) and direct-core event/state
parity tests. ASan/UBSan engine and CLAP tests also pass. The optional Windows
workflow has **not** run natively. Its presence is not a Windows validation result.

The staged Reason adapter has its own mocked motherboard/event contract tests;
see `reason-rack-extensions/Prototypes/Keyra/README.md`. Mock Jukebox declarations
are authored test facsimiles, never SDK build inputs. No Jukebox SDK is available
in this workspace. Thus no SDK compile, Reason device creation, GUI or `.u45`
acceptance is claimed. Master tuning, performance expression, CV, panels and a
published canonical source pin remain explicit adapter blockers.

[checks.json](../Validation/checks.json) records the executed checks and limits.
The portfolio-wide source inventory check is blocked by the preexisting,
uninitialized Acustra submodule; the Keyra prototype is outside that production
inventory. The repository's no-SDK-tracked check passes.

## CPU evidence and reproduction

[Native timing](../Validation/performance.json),
[Rack-flag host approximation](../Validation/sdk-approx-performance.json) and
[long-tail diagnostic](../Validation/tail-performance.json) identify the CPU,
compiler, source hash, mean/p95/max timings and deadline exceedances. The
64-voice/48 kHz test includes recurring strikes and stealing. The ten-second
tail test disables FTZ/DAZ on x86 and restores the caller's flags. Shared-host
outliers remain; average throughput cannot prove glitch-free audio. Independent
attack-burst probes also exceeded 96 kHz/64-frame deadlines for 64 simultaneous
strikes. Actual Rack budget is shared across the whole rack, and the SDK compiler
differs from host GCC. Performance remains a release gate.

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
ctest --test-dir build --output-on-failure
python3 Research/GrandPianoV2/reference/fetch_reference.py
python3 References/Upright/fetch_reference.py
python3 References/GrandExpanded/fetch_reference.py
python3 References/GrandExpanded/extract_training.py
python3 tools/fit_live_calibration.py
python3 tools/fit_live_calibration.py --upright
python3 tools/validate_live.py
python3 tools/validate_live.py --upright --output Validation/live-upright.json
python3 tools/make_live_listening.py
python3 tools/make_default_comparisons.py
build/keyra_performance
build/keyra_sdk_performance
build/keyra_tail_performance
build/keyra_benchmark_modules
```

Refit only from the locked training subset. New evaluation-driven iterations
need new reserved recordings before making fresh generalization claims. The
[listening manifest](../Audio/manifest.json) identifies real→model segment times,
gains, hashes and attribution. Four performances share one export gain. These
are labeled listening aids; no human listening verdict has been fabricated.
