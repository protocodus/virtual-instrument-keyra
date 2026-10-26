# Frozen radiation-startup pilot: failed research candidate

This package preserves one **failed six-TRAIN experiment**, its exact source,
pre-audio protocol, measurements and later diagnosis. It changes no production
source, calibration, build default or public control. `OriginalControl` remains
the default. Four cases pass; **C6v4 and C6v12 fail**, so this readout is not
approved as a click fix or a sound-quality improvement.

The reference is Alexander Holm's Salamander Grand Piano V3 (Yamaha C5),
[CC BY 3.0](../../../References/GrandFullRange/upstream/LICENSE-CC-BY-3.0.txt).
See the [corpus description](../../../References/GrandFullRange/README.md)
for attribution, original capture information and unknown recording conditions.
No recording is embedded in the instrument or in this source package.

## Scope and result

The six cases are C3/C4/C6 at layers 4 and 12, all existing members of the locked
TRAIN34 inventory. They are not fresh holdouts. This experiment uses the frozen
five-anchor OriginalControl demo, not the seventeen-anchor confidence profile
or the later optimized canonical runtime. Layer velocities 40/93 are SFZ-bin
proxies, not measured recording hammer speeds.

One physical run per case emits both old and proposed observations: 48 kHz
stereo float32, 3.8 seconds, note on at frame 4800, held note, initial pedal zero,
humanization/mechanical texture zero, repetition controller bypassed, gain zero,
width one and the same 24 Hz high-pass. A separate 475-mode observation state
reads the physical trajectory without feedback. Its final endpoint has a
DC-stationary correction derived from the stored damped-rotation determinant.
The archived prototype and binary were frozen before the pressure files were
opened for scoring.

Both observation methods are mathematically causal: the old method reads
current modal state; it does not read future inputs. This study tests a proposed
dynamic radiation-startup construction. Its name is not proof that the prior
DSP is noncausal, that this construction is the unique physical solution, or
that all piano clicks have one cause.

| Case | All case gates | C3 first 5 ms / ring excess reduction, dB | Largest early five-band MAE worsening, dB |
|---|---|---:|---:|
| C3v4 | Pass | 16.215 / 9.921 | −0.246 |
| C3v12 | Pass | 15.943 / 9.758 | −0.240 |
| C4v4 | Pass | — | +0.175 |
| C4v12 | Pass | — | +0.177 |
| C6v4 | **Fail** | — | **+8.227** |
| C6v12 | **Fail** | — | **+8.872** |

The frozen limit is +1 dB for **each** C4/C6 early-window five-band MAE.
Every case passes the late harmonic/envelope, sustain RMS, LR balance and mono
energy gates, as well as exact baseline payload and producer state/force/fault
guards. All gates are required; their thresholds remain unchanged.

The later C6 diagnosis finds strong suppression below 500 Hz, while upper-band
changes are small. For example, C6v4's 5–20 ms 31.25–250 Hz signed error changes
from +2.147 to −42.481 dB. C6's measured H1 is about 1050.35 Hz. The pressure
cross terms describe cancellation of old low-frequency output; they are not a
mechanical-energy ledger. Recorded low-frequency content is real in the
reference PCM, but these recordings cannot assign it uniquely to action, body,
air or acquisition processing. Short-window leakage also matters. True SNR is
unavailable because the edited lead-ins provide insufficient separate noise.
Adjacent-band H1 prominence is only a contrast proxy, and reference-equivalent
dBFS is not calibrated acoustic SPL. The preregistered transient ×0.5 mixture
also fails both C6 cases when the same numerical gates are applied post hoc.
Neither diagnosis changes the frozen result. The separately published
[listening diagnostics](../../../Audio/full-radiation-pilot/README.md) retain
the same failure status; their manifest is pinned by the review index.

## Evidence and identities

`review-index.json` maps original absolute paths and hashes to published files.
Archived JSON is copied byte for byte; its original paths and chronology are
not rewritten to look like new measurements. `producer/source-index.json`
maps the exact frozen producer sources. The original compiled executable and
large captures are not Git payloads.

Later C6 source-path notes and music diagnostics under `producer/evidence/`
are labeled supplements. Their full trace/music captures remain external; the
default review checks these files' identities, not all their numerical claims.
The captured-input inventory and numerical replay below cover the original
six-case pilot. See each supplement's own input records for optional replay.

| Item | SHA-256 |
|---|---|
| Protocol | `5ec7ace5cffb6655fb017430d328dc784762beb9ff5460eb5c63a07e606b96fa` |
| Frozen metric implementation | `14fc804b80f3742ee6c95cc3908c498459a77e61c90a1bdfe4b6c23c8580c1cd` |
| Candidate source/binary/readout freeze | `e69b90e55119da36668feba4048eace7230f92c362fdfce93c38c9c69adea8ea` |
| Original compiled producer | `19cddb44e6b12328f74680ea4fdebd99bfae6378108822237cdd7d8c39f128f4` |
| Original producer receipt | `c18f0a3fbcec5fb85a21e1b33b95863aacb4a64b064bddd5e93056f8ae8d60ae` |
| Original capture manifest | `ade69db0219029b19c15cc727c1a72194fd1c59a0eb72bde6ed445518ff78166` |
| Frozen failed result | `ddbfffa64b0b792b61dbf71bfd3ecb8f659cb5f33a21e1ce16ffb84097e0f36c` |
| Post-hoc C6 diagnosis | `2f7966b9fddda5678024cacb22d701e9a7715b0b4b28858c079f0812187169a6` |

The old baseline source identities are model `5c8c92f8…`, calibration
`619d6bf4…` and facade `6b4bc94b…`. The actual instrumented producer files have
their own hashes and are retained separately; instrumentation is not passed
off as those original source bytes.

The first consumer attempt stopped at a metadata guard before opening pressure
audio: the producer supplied separate state/force parity flags but omitted the
consumer's combined flag. `evidence/metadata-preflight-1/` preserves that failed
attempt. The new metadata adapter adds only their logical AND. Original capture,
producer receipt, source, binary, audio, metric code and gates stay intact.

The original pre-audio fixture checker used exact dictionary equality against
stored binary64 results. A later replay exposed 1–2 ULP differences in late
partial powers and at most 3.553e−15 dB in log results. The mutable checker now
compares exact structure/nonfloating metadata and bounds floating roundoff by
16 machine epsilons relative, with an additional 16 epsilons absolute **only
for dB fields**, including arrays. Power has no absolute tolerance. Every
nonidentical scalar is recorded; tiny-power, type, metadata and nonfinite
negative tests prevent broad equality. A near-zero dB result can differ by many
ULPs after log cancellation despite its tiny absolute error. This is a replay
comparison, not a gate tolerance. Original checker/receipt and the first replay
remain archived; frozen metrics and scores are unchanged.

## Reproduce or review

From the repository root, the source/evidence review uses only Python's standard
library and published files. It checks source hashes, archived bindings,
chronology, adapter scope, stored gate arithmetic, four passes/two C6 failures
and the separate diagnostic labels. It opens no external pressure audio:

```sh
python3 tools/check_causal_radiation_review.py
```

For the standalone targeted checks, use the
[regression checklist](REGRESSION_CHECKLIST.md). All output options refuse to
overwrite a prior receipt. A review-command pass means this failed experiment
is internally preserved, not that piano sound validation passed.

Full original-artifact verification requires an external bundle rooted like
the original checkout (or the existing local checkout). Supply it explicitly:

```sh
python3 tools/check_causal_radiation_review.py --verify-captures --capture-root /path/to/archive
python3 tools/check_causal_radiation_review.py --recompute --capture-root /path/to/archive
```

The latter additionally requires NumPy and SciPy and calls the unchanged metric
functions with the exact reference PCM, old gain and old onset. It performs no
synthesis, alignment optimization, fitting or acquisition. The complete missing
artifact inventory is `review-index.json:external_input_artifacts`. It includes
the six authenticated TRAIN WAVs, old cached controls and event/JSON receipts,
six pilot baseline/candidate WAV pairs, intact stems, per-frame force and
checkpoint state proofs, the original producer/math-probe executables, frozen
board/mode binary tables, and the legacy cached-control executable used by the
known-answer metadata fixture. These local captured files
are required beyond downloadable TRAIN recordings for **original-artifact**
verification. Do not substitute a newly generated WAV or executable under an
old hash or silently normalize a recording whose WAV-container bytes differ.

For a new derivative render, the
[portable producer](producer/README.md) builds only its retained frozen source
copies and does not need old ignored `out/` source. It writes a separate output.
A compiler/toolchain change can produce a different binary and rounding; a
new render must keep its own receipt and be compared with the old payloads.
It cannot recreate the original first-use chronology. Do not run the archived
`render_pilot.py` directly: its original paths and orchestration are retained
for provenance, not as a portable interface.

No production runtime changed, so this package requires the targeted metric and
source checks, not another full-core test matrix. Independent listening,
controlled action/body/air recordings, broader TRAIN confirmation and any
production integration remain separate decisions. The failed pilot does not
justify default promotion or a claim of production sound readiness.
