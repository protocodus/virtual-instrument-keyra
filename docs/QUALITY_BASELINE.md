# Original physical renderer is the sound-quality baseline

The repository split did not change the preserved original engine. Its solver
and calibration remain byte-identical to the imported study, and its original
musical MP3s remain under `Research/GrandPianoV2/renders/`.

The original is a starting point for further development. The user explicitly
expects its realism to improve; acoustic recordings and listening feedback
remain the target. An exact full-model version provides a comparison control.
The user accepts precision/quality tradeoffs when hardly audible: numerical
approximations need quantified errors, stability checks and musical listening.
Intentional acoustic improvements need separate evidence against recordings
and the previous physical version. Broad, connected behavior takes priority
over extreme precision in one subsystem.

The live-preview work introduced a **different synthesizer**. Agreement with
isolated harmonic powers does not preserve the original's nonlinear excitation,
mechanical phase or spatial response. These structural differences are plausible
contributors to the listening feedback; their individual perceptual effects have
not been isolated. Promoting the preview on CPU and note-error results before a
matched quality comparison was a regression in the development process.

| Quality baseline | Reduced live preview |
|---|---|
| Nonlinear hammer/string contact | Shared exponential attack on fitted pressure modes |
| 230 strings, two polarizations, detuned unisons | Fast/late fitted components per voice |
| Reciprocal string/bridge/soundboard dynamics | Feed-forward authored resonance effect |
| 475 board modes, approximately 75–12992 Hz | Twelve authored body resonances |
| Complex loaded-board radiation phase and transient | Scalar voice observation/panning |
| Original musical exports at 192 kHz internal rate | 48 kHz preview/comparison renders |

The original musical examples also use a procedural room. Consequently comparing
an original room performance against a dry isolated preview mixes algorithm,
material and presentation differences. Room is one factor; it is not the sole
explanation for the missing body and spatial behavior.

## Matched comparison

`tools/compare_quality_baseline.py` renders the same first six seconds of the
original nocturne events, followed by three seconds of tail/held behavior:

- [Original, dry](../Audio/quality-baseline/original-dry.mp3)
- [Reduced preview, dry](../Audio/quality-baseline/reduced-dry.mp3)
- [Original, same room](../Audio/quality-baseline/original-room.mp3)
- [Reduced preview, same room](../Audio/quality-baseline/reduced-room.mp3)
- [Original → reduced, dry](../Audio/quality-baseline/original-then-reduced-dry.mp3)
  (segments begin at 0 and 9.5 seconds)

The reduced preview retains its default body/resonance (0.3), mechanical noise
(0.1), mic and width settings. Only its room/distance control is zero, allowing
the same external room processing for both engines. The first comparison also
bypassed its body/noise effects; that ablation is archived separately in
`Audio/quality-baseline/body-off-ablation/` and must not represent the full live
default.

All export at 48 kHz. Whole-file stereo RMS is matched separately per engine and
presentation before the same 150 ms end fade; one final true-peak gain applies to
all files. Both room versions use the identical preserved procedural room,
wet=.16. No added room appears in either dry file. The reference's 192 kHz native
output is FIR-downsampled; the live model synthesizes at 48 kHz. Native output
high-pass differences are retained and documented; no further EQ is applied.
The [manifest](../Audio/quality-baseline/manifest.json) records hashes, gains,
commands, source identities and limitations. This is a labeled comparison, not a
fabricated blind-listening verdict.

For this passage, dry channel correlation is 0.147 in the original and 0.925 in the
reduced model. Correlation is not a realism score, but it demonstrates a large
spatial difference even without added room. Their RMS levels match within 0.001 dB.

## Runtime constraint and next work

On this Linux machine, the preserved full model's one-second C4 render at 48 kHz
took 6.16 wall seconds. The nine-second 192 kHz passage took 256 wall seconds. These
shared-host diagnostic timings are not a real-time performance guarantee and
must not be compared as if the workloads/rates were identical.

The full mechanical reference therefore remains an offline quality baseline.
Its performance must improve substantially for a Rack Extension. First work on
sound-preserving loop/caching changes against the exact source; use byte/null
checks, physical tests and the same musical material. Any mode/model reduction
needs explicit body, attack, stereo and listening evidence against the original.
Do not silently substitute a faster engine because a subset of note metrics
improves.

The connected `PhysicalPiano` research candidate is also a reduction, not an
automatic recovery of original quality. Its initial 48-mode board covered only
72–491 Hz and cannot reproduce the reference's high-frequency body phase. The
new full-board experiment restores all 475 reference poles and uses a nonlinear
hammer and two mechanical polarizations, but retains aggregate choirs and
empirical observation/loss priors. See the separately labeled
[physical audition](PHYSICAL_AUDITION.md). It has not replaced the live preview.
Material and preset expansion stay secondary.

[Exact-output optimization experiments](../Validation/reference-optimization.md)
retain the complete original topology. Passing candidates preserve float audio
and final double state for the tested cases; measured CPU differences depend on
compiler settings and do not establish real-time performance in Reason.

The frozen source itself is never edited during optimization. Reproduce the
reference passage using:

```sh
python3 tools/compare_quality_baseline.py --render-reference
```

Omit `--render-reference` to reuse the original WAV only when every input/output
hash matches its synthesis receipt. A cached file is never associated with the
current source merely because it exists. The first receipt was assembled after
the recorded successful render; regenerated receipts hash inputs before and
after execution. The common event file is the exact first six-second prefix
of the preserved nocturne; the final note/pedal remain held during the tail.

