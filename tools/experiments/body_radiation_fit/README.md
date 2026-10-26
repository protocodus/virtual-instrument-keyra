# Six-weight body radiation fit — rejected

**0/34 original preservation cases pass. The candidate is not adopted.** One
bounded fit of six shared positive soundboard observation weights converged,
but it could not replace the original empirical string radiation readout while
preserving body, sustain and stereo behavior. Runtime and defaults are unchanged.

| Fixed metric, dB MAE; lower is better | Original final, fit32 | Body-only, fit32 | Original final, all 34 | Body-only, all 34 |
|---|---:|---:|---:|---:|
| Early five-band | 14.434 | 11.490 | 14.963 | 11.977 |
| Late harmonic | 11.385 | 12.874 | 13.217 | 14.524 |
| Late envelope | 5.445 | 6.809 | 5.965 | 8.079 |

These paired figures use this experiment's frozen windows and masks; they must
not be compared with another study's differently defined aggregates. The
optimizer's objective fell from 105.45 to 95.16 relative to **uncalibrated raw
body at alpha=1**, not relative to the original final sound.

All 34 sustain RMS guards fail, with drift from −8.92 to +12.72 dB. Other overlapping
failure counts are mono 31, L/R 25, harmonic 24, early-window 22 and envelope 17.
Both C3 layers reduce first 5 ms positive excess by 20.24/19.22 dB, but their 5–20 ms
ring excess worsens by 0.904/1.025 dB and fails the unchanged 3 dB reduction target.
Thus improving the first impulse does not resolve the reported ringing click.
This experiment does not identify that sound as a particular mechanical part.

## Fixed construction and scope

The earlier [body reconstruction](../body_radiation_basis/README.md) reproduces
all 475 original body modes from authenticated saved model bridge forces. Six
smooth nonnegative frequency bases, centered at 55/140/350/900/2400/6500 Hz,
partition the existing signed stereo microphone weights. Each basis weights
the complete acceleration, including restoring, damping and instantaneous
force terms. For this candidate:

    rawBody(alpha) = sum_b alpha_b * basis_b
    output = originalHP24(rawBody(alpha))

The empirical string correction is removed. No new poles, modes, decay states,
physical parts or microphone propagation are added. Rebuilding the old
nonlinear target/abs(H) correction after changing mic weights would be a
different operator and is not represented by these six captures.

One L-BFGS-B solve starts at six 0 dB coefficients, within amplitude bounds
.025–40. Its fixed objective equally averages early, late-harmonic and
late-envelope Huber losses per case, plus magnitude and smoothness penalties.
It converges in 13 iterations / 14 evaluations. The six amplitudes are
3.3404, 3.2668, .8038, .6394, .7126, .2924; none reaches a bound. The total
precomputation, solve, emission and scoring takes 19.01 s, without a physical
piano rerender. This is not a realtime benchmark.

The fit uses 32 previously observed TRAIN cases. C8v4/v12 are excluded from
fitting because unassigned subfundamental content dominates their broad
normalization; the same six coefficients are nevertheless applied to **all 34**
and every original C8 metric and preservation guard remains. Fixed old gains,
onsets, reference masks and complete-window support never change. C8v4 has
three complete late spectral windows through 2.5 s and envelope samples through
2.80s, with no padding. Its weak family and unassigned 4434 Hz components remain
diagnostics, not newly identified string/frame/duplex parts.

Captures use the historical original 5-anchor model/calibration at 48 kHz stereo,
mechanisms/humanization off and repetition bypassed. This does not qualify the
optional confidence profile, connected runtime settings or a Reason build.
A local six-weight fit failure does not prove all body-only observations or
all positive coefficients globally infeasible. No listening preference,
generalization or production-readiness claim is made.

## Numerical checks and preserved failure

`v1` stopped before optimization at C6v4: independently evaluated rolling
envelopes differed by about 1.92e-9 relative, exceeding its relative-only numeric
bound. Its source, freeze, preflight and failure are preserved. No coefficients
or final candidate existed in that attempt.

`v2` changes numerical infrastructure only: direct 240-sample positive
semidefinite Gram matrices replace a second rolling accumulation. The absolute
comparison bound is derived from SciPy 1.17.0's exact `NI_UniformFilter1D`
recurrence, nearest padding, input energy, dot-product rounding and stable HP
rounding. It is not scaled to the observed failure. The included third-party
C source retains its copyright/license header. Objective, coefficient bounds,
start, cases and acoustic gates are unchanged.

All 34 fixed-test-alpha coherent spectral/envelope checks pass before fitting.
After fitting, all 34 double and float32 forecasts agree with explicit output
within their numerical bounds. Original gates use the actual float32 output
and the immutable scorer, rather than Gram forecasts. Historical state/force
proofs are reused as collection-time evidence; no new mechanical trajectory
or host validation was performed.

The original manifest records a 1920-byte run-log prefix. The final JSON summary
was printed after that manifest and extends the log to 3083 bytes. An append-only
completion receipt and independent addendum bind both identities; the original
source, results and manifest are not rewritten.

## Inspect the evidence

From the repository root:

```sh
python3 tools/experiments/body_radiation_fit/check.py
```

The standard-library verifier checks 154 published/reused records, all 34 stored
original gate decisions, the full 14-evaluation trace, numerical predicates,
moment-file identities/headers and the journal completion exception. It does
not decode PCM, compute features, rebuild DSP or run an optimizer. Optional
`--output /new/path.json` writes a fresh verifier receipt.

`index.json` maps historical absolute paths and uncompressed hashes onto this
checkout. JSON is losslessly gzip-compressed with timestamp zero. The archive
includes the failed preflight, frozen sources/protocols, all 34 outcomes,
optimizer trace, independent audits and 34 derived moment NPZ files totaling
4,814,760 bytes. Their numeric arrays contain Gram statistics and existing
reference targets, not audio. Existing basis/TRAIN34 sources and reference
features are reused by hash.

The historical `frozen_fit.py` files deliberately retain their original paths
and once-only guards; they are review sources, not portable launchers. The
moments permit a separately declared numerical reproduction with NumPy/SciPy
without recordings or a 17,778-mode simulation. Recreating candidate WAVs needs
the omitted 694.6 MB body-basis capture (or its authenticated force inputs and
the published board replay), plus a fresh workspace/path mapping. Audio,
compiled binaries and Python caches are omitted and listed as external
identities. Set `OPENBLAS_NUM_THREADS=1` before NumPy starts when reproducing
waveform calculations. No experiment was rerun for publication.

Reference targets derive from Alexander Holm's Salamander Grand Piano V3,
[CC BY 3.0](../../../References/GrandFullRange/upstream/LICENSE-CC-BY-3.0.txt),
with [attribution and recording limits](../../../References/GrandFullRange/README.md).
Other source retains its existing ownership terms; this archive adds no license
grant. The current result is also summarized in
[Validation/full-body-radiation-fit.json](../../../Validation/full-body-radiation-fit.json).
