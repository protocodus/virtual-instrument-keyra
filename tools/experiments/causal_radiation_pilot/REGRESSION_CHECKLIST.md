# Targeted frozen-pilot regression checklist

Run from the repository root. Keep new review receipts outside the frozen
archive. These checks preserve a **failed** experiment; none is a sound-quality
acceptance or a fresh holdout evaluation.

1. Check published source/evidence without recordings or ignored output:

   ```sh
   python3 tools/check_causal_radiation_review.py
   ```

   Expected: review consistency passes, pilot remains `false`, C3/C4 pass,
   C6v4/C6v12 each fail only `each_early_window_band_MAE`. Original protocol,
   metric, result, producer source and adapter scope retain their hashes.

2. Check CLI inspection is read-only:

   ```sh
   python3 tools/check_causal_radiation_metrics.py --help
   python3 tools/check_causal_radiation_review.py --help
   ```

   Expected: help exits without running acoustic checks or writing receipts.

3. With the original captured input bundle, verify byte identities and physical
   parity rows before trusting numerical replay:

   ```sh
   python3 tools/check_causal_radiation_review.py --verify-captures --capture-root /path/to/archive
   ```

   Expected: every required artifact SHA matches; each state/force row compares
   equal before/after observer calls, with 714 checkpoints and 182400 force rows.
   These finite-width hashes supplement source review and do not prove absence
   of all possible collisions or physical realism.

4. With NumPy/SciPy, replay the six fixed numerical observations:

   ```sh
   python3 tools/check_causal_radiation_review.py --recompute --capture-root /path/to/archive
   ```

   Expected: baseline float32 payload is exact to each cached control; numerical
   features agree within the explicitly recorded binary64 replay comparison.
   Old gains/onsets remain fixed and the frozen failed result stays unchanged.

5. In the original populated study workspace only, exercise known-answer metric
   fixtures and nine invalid producer/capture guards:

   ```sh
   python3 tools/check_causal_radiation_metrics.py --output out/full-causal-radiation-metrics/v1/new-fixture-review.json
   ```

   Expected: two cached TRAIN identities, gain ×2 giving +6.0206 dB, LR common-gain
   invariance, correct mono energy, a 48-frame delay detected without retiming,
   tiny-power/type/metadata/nonfinite comparator negatives, and nine rejected
   provenance/schema mutations. This checker requires the archived `out/`
   layout; portable source/evidence review is step 1. Its synthetic metadata
   fixture is not physical-state validation.

6. Confirm the result and scope before review: C6 first-window improvement does
   not erase the +8.227/+8.872 dB 5–20 ms band-MAE regressions; post-hoc finer
   bands, prominence and transient ×0.5 observations do not rescore the pilot.
   `OriginalControl`, all canonical calibrations and sound-validation status
   remain unchanged. No full-core test matrix is required unless runtime source
   is changed in a separate task.
