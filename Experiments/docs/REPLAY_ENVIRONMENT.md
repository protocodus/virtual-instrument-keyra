# Replay environment for frozen listening and numerical evidence

Set **`OPENBLAS_NUM_THREADS=1` before Python starts** when reproducing the
historical presentation exports or NumPy-based numerical studies below. This
addendum supplies a later-discovered environment requirement; the original
pilot package, exporter, hashes and receipts remain byte for byte unchanged.

The preserved procedural room generator normalizes its diffuse tail with
`np.linalg.norm`. In the observed NumPy 2.3.5 environment, changing the OpenBLAS
reduction thread count changed the final binary64 IR bytes. The default eight
threads produced `b033d343963462d49247dade80a831015e5a3c04534160fc2f303d55d7806657`;
one thread reproduced the exact historical fingerprint:

`38dd2ac037e8fb2cb47f3ec561c37eab0478cef092b7ded9b617b92d6458b374`

This was an exact-reproduction failure, not evidence of an audible difference.
The historical source, random seed, filter, gains and room recipe did not
change. The first compatibility-presentation attempt stopped at the IR hash
assertion before room processing/export and was preserved. An explicit
environment-only retry reproduced the historical IR, retained identical raw
crossover PCM and matched the old presented segment's PCM24. The separate
presentation evidence records the failed attempt and retry; it does not revise
the original six-case failed pilot or establish a listener preference.

The [IR-only receipt](../Audio/full-radiation-crossover/environment-receipt.json)
records a maximum IR difference of `1.1102230246251565e-16` and 139,793 differing
binary64 elements between one and eight threads. It opened no piano PCM. The
[first-attempt receipt](../Audio/full-radiation-crossover/evidence/first-attempt-receipt.json)
and [exact presentation reproduction](../Audio/full-radiation-crossover/evidence/presentation-reproduction.json)
retain the failure and corrected-environment evidence. The newer exporter's
thread pin is set before NumPy import; the old frozen exporter requires the
explicit prefix below.

Use the corrected invocation for the **old failed-pilot** exporter:

```sh
OPENBLAS_NUM_THREADS=1 python3 Audio/full-radiation-pilot/export.py --inputs source-files.json --output /tmp/keyra-radiation-listening
```

The input map, original fingerprint-matched files, NumPy/SciPy and FFmpeg are
still required as described in its unchanged
[README](../Audio/full-radiation-pilot/README.md). Choose a new or empty output
directory. This command performs presentation processing, not instrument
synthesis or a model-quality evaluation.

Use the same explicit setting for numerical replay, preserving exact captured
inputs and writing a new receipt:

```sh
OPENBLAS_NUM_THREADS=1 python3 tools/check_causal_radiation_review.py --recompute --capture-root /path/to/archive --output /tmp/keyra-radiation-numeric-review.json
```

In the original populated study workspace, the known-answer fixture command is:

```sh
OPENBLAS_NUM_THREADS=1 python3 tools/check_causal_radiation_metrics.py --output /tmp/keyra-radiation-fixture-review.json
```

Numerical metric replay already records narrowly bounded binary64 differences
with exact structural/metadata checks. That comparison does not permit changing
a waveform or IR hash, gain, onset, formula or acceptance threshold. Setting the
thread count supports deterministic reduction; it does not promise identical
results across untested library versions, CPUs or compilers. Keep the actual
runtime versions and all remaining fingerprint checks visible.

The new crossover package's source/JSON verifier needs only Python's standard
library and has no BLAS dependency:

```sh
python3 tools/experiments/radiation_crossover/check.py
```

Its [research documentation](../tools/experiments/radiation_crossover/README.md)
separates six post-hoc TRAIN passes, individual C6 regressions, archived
chronology, inherited physical proofs and unqualified listening/default status.
