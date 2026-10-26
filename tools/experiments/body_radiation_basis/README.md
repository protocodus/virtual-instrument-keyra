This package preserves a **34/34 passing reconstruction check**, not a new piano sound. Replaying the original 475 soundboard modes from previously captured bridge forces reproduced all 12,403,200 raw stereo pressure samples bit for bit. Six smooth frequency bases reconstruct that pressure within floating point summation error. No recording was fitted, no coefficients were selected and no runtime/default changed.

The six bases use raised-cosine crossfades on log frequency, centered at 55, 140, 350, 900, 2,400 and 6,500 Hz, with constant endpoint tails. They weight each mode's **complete acceleration**, including its instantaneous bridge force, and preserve the original signed left/right microphone coefficients. Positive scalar weights could later be folded into those coefficients without additional runtime states. This establishes a usable representation; it does not establish a sonic improvement.

The representation spans raw body pressure only. Existing empirical string-radiation correction depends nonlinearly on the microphone coefficients. Recomputing that correction after a change is outside this six-basis identity. Any later fit must define whether it replaces the correction or freezes it. These bases cannot create missing resonances, change their decay or add an independent stereo phase.

Run the source-only consistency check with Python's standard library:

```sh
python3 tools/experiments/body_radiation_basis/check.py
```

It checks the archived source, protocol, results, pre-opening failures, all 34 stored case statistics, six chunk comparisons and twelve coherent Gram checks. It does not decode PCM, run a simulation or measure a new candidate. `index.json` pins decoded and compressed bytes; existing public producer sources and metadata are reused rather than copied.

Raw capture files and compiled binaries are deliberately external. A capture archive must retain these original paths below its root:

```text
out/full-causal-radiation/v1/pilot/{C3,C4,C6}v{4,12}/{trace.f64le,force-proof.u64le}
out/full-radiation-crossover/train34/producer/renders/CASE/{trace.f64le,force-proof.u64le}
```

There are 17 TRAIN keys at layers 4 and 12: A0, C1, A1, C2, D#2, A2, C3, D#3, C4, D#4, A4, C5, D#5, A5, C6, C7 and C8. These recordings were already observed during previous work; this study creates no fresh validation set. Input bindings use 30 historical trace hashes and four explicitly fresh pre-opening hashes. Every trace's 88 hammer forces and three bridge forces are authenticated against historically pinned before/after FNV proof rows. FNV is not collision resistant; the proof files also have pinned SHA-256 hashes.

With the external archive present, this portable launcher uses the frozen C++ source and losslessly encoded static coefficients:

```sh
python3 tools/experiments/body_radiation_basis/replay.py replay \
  --capture-root /path/to/capture-archive --output /tmp/keyra-body-replay
```

G++ is required. `--ids C3v4 C3v12` selects a smaller reconstruction check. New output directories are required and failures are retained. The launcher checks the board recurrence, force proofs, partition sum, fixed positive recombination, 24 Hz high-pass sum and witness chunk invariance. It does not recompute the coherent Gram matrices; the original frozen NumPy runner and their stored results are archived. All 34 raw outputs occupy 694,579,200 bytes (about 662 MiB). The original offline replay took 56.3 seconds including six alternate chunk runs; that is **not a full-piano realtime benchmark**.

Optionally rebuild the static coefficients directly from the already archived original model constructor:

```sh
python3 tools/experiments/body_radiation_basis/replay.py export-static \
  --output /tmp/keyra-board-coefficients
```

This constructs the model but processes no audio frame. It compares the exported coefficient bytes with the frozen hash and retains any platform difference. The supplied JSON encodes the exact original float64 values and reconstructs the original coefficient file without platform math dependencies.

The first unrun protocol used numeric equality where bit identity was intended. The independent audit rejected it before pressure access. The second attempt failed while serializing a NumPy Boolean in the synthetic Gram preflight, before any trace was opened. Both freezes, source versions and failure records remain in `evidence/study/pre-access-v1` and `pre-access-v2`; the successful third freeze changed no basis or acoustic gate. Independent source and post-run reviews are included in `evidence/independent`.

The package contains no listening candidate and makes no production-readiness or default-adoption claim. The high click and full-range sound mismatch remain unresolved.
