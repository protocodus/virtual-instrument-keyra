# Full TRAIN34 radiation confirmation — failed

**26/34 passed; eight early-attack preservation failures. No adoption.** This
package preserves one fixed 400 Hz confirmation using six unchanged previous
outcomes and 28 newly rendered original/causal pairs. All 34 are already observed
TRAIN. It is neither a held-out study nor a production/default change.
See [the result and limitations](../../../docs/RADIATION_STARTUP.md).

The eight failures are A0v4, A0v12, D#5v4, D#5v12, C7v4, C7v12, C8v4 and C8v12.
Each fails only the original +1 dB early five-band MAE preservation limit.
The original source, baseline, late/sustain, L/R and mono guards pass. Signed
band errors, weak H1 measurements and the unassigned C8 components remain in
the records; no gain, onset, reference mask or threshold was changed afterward.

## What is archived

`index.json` maps original absolute paths and SHA-256 identities to this
checkout. Large immutable JSON is gzip-compressed with timestamp zero; both
stored and uncompressed hashes are recorded. Decompression recovers the exact
original bytes. Old `private`/`published:false` labels describe collection time;
this later package publication does not alter those receipts.

The package adds only four changed producer source files, the new measurement
and consumer sources, and selected contract/result receipts. All unchanged
headers, observer, driver and fixed operator are reused by hash from the
[original pilot](../causal_radiation_pilot/README.md) and
[six-case crossover](../radiation_crossover/README.md). Historical fixtures are
not production headers. The changed `FullInstrument.cpp` disables stem-only
scans, stem readout and stem-file writes in the already validated music producer;
mechanics and original/candidate observation remain unchanged.

| Immutable item | SHA-256 |
|---|---|
| Final protocol | `4d88205cd74ff1e05aa5082619d187435983e0c233b135100ff5bc906cb87cb6` |
| Reference/control features | `e3ad140a8052c2e81acdc0a281a4e658a2df7f796029572d562634c8adf375fe` |
| Producer plan | `c703d4062f276d68f1cbc61ad06a1cbebb7face8e1f68b37002909b5918d31c2` |
| Pre-render producer freeze | `ab3352f721dc3041e9a8bf4a3731eca25e827e251d5045528976ec4a808d9486` |
| Compiled producer, external binary | `c4768f6b4a2e52412d80047aad386a9f6c37ee56815330f7b18203de5b776757` |
| Producer receipt | `22c02d6344bf0676f4901a2ba838bb5a2ed8956c50bdb372ae5aaa025d3b0774` |
| Full result | `5895dc53be8bf77398327c4b1f0c3057abadbb5cfe5904f957a9bde97cab49fe` |
| Stored summary | `af2136bbd8b2fbbe8aae5fa908b18c36487b7df2271e18f311a1a457a5706b49` |

The original 413-file manifest identifies 1.075 GB of private capture material.
Audio, binary/object files, raw traces and raw parity arrays are omitted; inline
per-case receipt fields are retained without duplicating 28 separate receipts.
No reference audio or recorded IR is added to this package.

## Verify without audio or synthesis

From the repository root:

```sh
python3 tools/experiments/radiation_crossover_train34/check.py
```

This standard-library reader checks hashes/decompression, all 27 producer input
bindings, protocol/source/render/scoring chronology, exact operator function
source, the six unchanged outcomes, all 34 stored decisions and the 26/8 counts.
It runs no compiler, DSP, filter, feature extraction or scorer. The source/force
and partition checks are authenticated **collection-time claims**; verifying
those raw bytes again requires the omitted capture bundle. A successful package
check is evidence consistency, not a new acoustic or perceptual pass.
`--output /path/to/new-review.json` writes a fresh verifier receipt.

To inspect compressed evidence directly, for example:

```sh
python3 -m gzip -dc tools/experiments/radiation_crossover_train34/evidence/result.json.gz
```

## Source reconstruction and external replay requirements

The optional assembly command copies source and metadata only to a new directory
outside this checkout; it never compiles or renders:

```sh
python3 tools/experiments/radiation_crossover_train34/check.py \
  --assemble /tmp/keyra-train34-source
```

`compile-commands.json` then contains the three original GNU/Clang-style C++17
compile/link commands with the source/output directory remapped. The flags,
prepared model, calibration and observer bytes stay fixed. Compilation was not
repeated for package publication. The historical binary identity depends on
the original compiler, platform and paths; different toolchains may differ.

For an independent new model capture, execute the assembled compile commands,
create a fresh case directory, and call `producer CASE_DIR MIDI VELOCITY` using
the immutable plan's event inventory. The producer is fixed to 182400 frames,
48 kHz stereo, note-on at frame 4800, held to the end, seed 123456,
humanization/mechanisms off, repetition bypassed, gain 0 dB and width 1. It emits
raw float32 baseline/causal pairs plus diagnostics/proof arrays. The archived
`compat400.py` contains the exact four functions from the frozen operator;
`process(old, causal, [64])` begins with zero state. Emit float32 and check output
and final-state bytes against `[1,3,17,64,129,7]`. This is a new capture, not the
historical confirmation. Neither archived orchestration nor scoring scripts
are portable launchers: they deliberately retain the historical absolute paths
and once-only guards. Do not point them at old evidence or treat a manual rerun
as another unchanged result.

To reproduce the reference comparison, additionally supply the authenticated
34 reference recordings and cached old model-control WAVs/events/metadata in
the protocol, all 28 baseline/causal/fixed400 WAVs and raw proof rows, the original
six outputs/proofs, and the SHA-bound external binaries when asserting binary
identity. The compressed original manifest and protocol list original paths,
hashes and omitted-file sizes. Reconstruct a separate workspace/path mapping;
preserve the protocol and six reused outcomes rather than rescoring them.
NumPy/SciPy are required for waveform workflows. Set `OPENBLAS_NUM_THREADS=1`
before Python starts; see [the environment addendum](../../../docs/REPLAY_ENVIRONMENT.md).
No waveform replay was performed while packaging this result.

At collection time every new baseline's entire float32 payload matched its old
cache. The observer pre/post FNV checks matched at 714 physical-state checkpoints
and all 182400 contact/bridge-force frames per case, with zero physical/API and
observer faults. This is one physical trajectory with a read-only observer,
not a second independent mechanics run. The sampled field list and FNV collision
limitation remain explicit. Actual fixed400 output and filter-state bytes
matched both partition schedules and were finite. The two-worker batch took
396.55 s wall and 759.73 s child CPU including diagnostic work; this is not a
realtime benchmark or Reason host qualification.

Source retains the repository's existing ownership terms; this archive adds no
license grant. Reference measurements use Alexander Holm's Salamander Grand
Piano V3 under [CC BY 3.0](../../../References/GrandFullRange/upstream/LICENSE-CC-BY-3.0.txt),
with [attribution and acquisition limits](../../../References/GrandFullRange/README.md).
