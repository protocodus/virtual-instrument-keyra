# Fixed 400 Hz compatibility audition

[Listen: old → compatibility, room](old-then-compatibility-room.flac).
The old nine-second segment starts at **0 s**; compatibility starts at
**9.5 s**, after a half-second gap. The 18.5-second file is stereo 48 kHz PCM24.
No listening verdict is asserted.

One fixed 400 Hz observation crossover passed all six unchanged original pilot
gates on previously observed C3/C4/C6 TRAIN cases. This is **post-hoc TRAIN
reuse**; the broader 34-case set remains unvalidated. The [original unfiltered
pilot](../full-radiation-pilot/README.md) still failed both C6 early-band guards.
The [crossover evidence](../../tools/experiments/radiation_crossover/README.md)
retains the remaining C6 deficits and individual-band regressions. Neither
result changes the default or qualifies realtime or production use.

“Old” is the frozen legacy OriginalControl run, not the latest connected
default. Both source readouts are causal. Compatibility uses
`new + LP400(old − new)` with one zero-initialized stereo filter state preserved
through the entire nine seconds, including the held tail. It is an observation
operation, not another physical piano part. The source pair has identical
physical-state and force evidence; no new piano DSP render was performed.

Both versions keep the historical control room gain, procedural room at wet
0.16, 150 ms ending fade, original common gain and the previous pilot's fixed
extra safety gain **0.786203420103643**. There is no compatibility RMS match,
new normalization or limiter. The old segment is byte-identical to the prior
old-room PCM24. The fixed presentation peaks at approximately −2.38 dBFS;
finite, stereo and mono checks appear in [the manifest](manifest.json).

The first export stopped before room processing because unpinned BLAS
threading changed the procedural IR's binary64 hash. Its small receipts and
original file hashes are preserved under `evidence/`; raw audio is not
duplicated. Pinning `OPENBLAS_NUM_THREADS=1` restored the exact historical IR.
The compatibility raw PCM remained identical. See the
[environment receipt](environment-receipt.json) and
[replay-environment notes](../../docs/REPLAY_ENVIRONMENT.md).

To reproduce presentation, supply the two external raw float32 WAVs identified
by SHA-256 in `manifest.json:raw_sources`. The manifest uses stable source IDs;
put their local paths in a JSON object:

```json
{"music-old-raw": "/path/to/baseline.wav", "music-causal-raw": "/path/to/candidate.wav"}
```

Then run from the repository root, with NumPy, SciPy and FFmpeg installed:

```sh
OPENBLAS_NUM_THREADS=1 python3 Audio/full-radiation-crossover/export.py --inputs source-files.json --output /tmp/keyra-crossover-listening
```

The output directory must be new or empty. The exporter also pins the thread
setting before NumPy import, authenticates the unchanged archived crossover
and room sources, and checks the exact expected PCM24. This command reproduces
postprocessing and presentation only; the external raw WAVs and a portable
producer for this particular musical capture are not bundled. Tested numerical
versions were NumPy 2.3.5 and SciPy 1.17.0. No acoustic recording excerpt or
recorded room IR is included in this audition. Benchmark reference attribution
remains in the linked research package.

Presentation reproduction was verified from outside the repository directory:
the regenerated FLAC and decoded PCM24 both match this file exactly. The
small receipt is [preserved here](evidence/presentation-reproduction.json).
