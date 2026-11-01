# Compare the same measured observations — 2026-11-01

The quiet-observation calibration experiment exposed a reporting ambiguity:
Kawai `n80v2` has no baseline sustain score but becomes measurable in the
candidate. Averaging each run's available layers independently reports a
+4.929 dB note-80 sustain change. That is a change in aggregate membership,
not an error increase measured on the same take.

`Tools/compare_benchmarks.py` now adds paired summaries and note regressions,
using each metric's common case set. Every gained/lost score is listed
separately, with paired, baseline-only, candidate-only and neither counts.
Missing values remain missing. Both level errors use the full baseline's
median gain so candidate recentering cannot hide changed loudness. Duplicate
cases, changed note identities, mismatched splits and non-finite observations
fail validation. Reports retain the old independently filtered summaries and
regression list, explicitly labelled legacy, alongside the new comparison.
No scorer, fit, recording, metric tolerance or production DSP changes.

The actual paired regenerated Kawai baseline versus quiet-frame experiment
has **21 paired note/metric regressions, one availability change and 22 legacy
independent-sample regressions**. The availability change is `n80v2` sustain.
Removing the misleading aggregate comparison does not make this candidate
acceptable; it remains research only. The newly generated report is under
`out/realism/censor-observations/evaluation/common-support-paired-kawai`.
Earlier frozen reports are preserved.

Rechecking all 933 frozen original-baseline and accepted 0.4.2 observations
with the paired method finds **no availability changes in any piano**.
The previous dev decay improvements remain unchanged: grand −0.0612,
upright −0.1535, Kawai −0.0994, Hamburg −0.5217, New York −0.3578 and Belmont
−0.0445 dB/s. The sole tolerance-exceeding paired note regression remains
New York MIDI 100 tuning. This check reads numeric reports only; it does not
rerender or rescore audio. Full hashes and paired results are under
`out/realism/common-support/accepted-interpolation.json`.

Validation: four regression tests cover gained coverage, lost/all-absent
coverage with a real paired regression, shared loudness reference, malformed
identity and non-finite scores. `Keyra.BenchmarkComparison` passes through
CTest in the existing Release configuration. The real Kawai command also
generates both JSON and Markdown with the counts above. The existing
`cell_means()` API remains unchanged for frozen research callers.
