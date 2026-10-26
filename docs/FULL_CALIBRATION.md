# Calibrating the original full piano

> Version4 uses the corrected TRAIN measurements and the selected physical strike proposal. C8retains an ambiguous4276Hz key-family carrier and separately reports a strong unassigned component near4434Hz. Dominance does not establish string fundamental identity. The weaker family agrees more closely with the vendor's tuning metadata; no forcedwhole-key retune is applied. The oldv2 drafts and derived C8stiffness/velocity scores are preserved as historical results with invalidated confidence, not accepted calibration. The separate component remains a large model limitation.


`tools/fit_full_calibration.py` extends the preserved full-model workflow to the locked TRAIN34 recordings. It generates candidate JSON profiles, 64-partial calibration headers, and candidate solver copies under `out/`. It does not write to `Research/`, `References/`, or the canonical solver in `src/`.

The model remains a nonlinear hammer driving 230 strings in two polarizations, passive common-unison loss ports, a reciprocal three-port bridge, and 475 soundboard modes. The complex loaded-board radiation phase remains in the solver. The calibration contains positive losses, scalar hammer controls, tuning, and smooth observation magnitudes; it contains no recorded waveform, impulse response, or substitute pressure generator.

## Data and identification limits

The current analytic candidate is `out/full-calibration/v4/analytic`, generated from the frozen physical strike proposal at `out/full-strike-bank/proposed-profile/calibration.json`. The explicit final radiation mask fits32 unambiguous training recordings; all34 are rendered/scored. C8prior observation fields are copied unchanged, with its missing component still reported.

The default inputs are `References/GrandFullRange/combined_train_features.json` and its locked `split.json`. They contain 34 source-layer4/12 cases at 17 MIDI anchors:

`21, 24, 33, 36, 39, 45, 48, 51, 60, 63, 69, 72, 75, 81, 84, 96, 108`.

The tool first validates the complete inventory, unique identities, MIDI/layer consistency, split hash, training roles, and unopened-reserved-data flags. All layer6/8 references are rejected. Reused original TRAIN10 numerical features keep historical WAVcontainer hashes; when a reconstructed container differs, audio resolution requires the historical feature-to-manifest link, identical authenticated FLAC and decoded-PCM receipts across manifests, the current WAVcontainer hash, and actual decoded-PCM equality. Both historical and actual identities are reported. A filename match is insufficient. The new A0v8 and C8v8 audio is reserved for evaluation after freezing the candidate. Previously observed evaluation notes also stay out of fitting and method selection.

C8v4 ends about 2.80808 seconds after onset. Its last window is `[1.5, 2.80808]`, and envelope samples end at 2.8 seconds. Both model measurements and stem integration use that same support. There is no zero padding, extrapolated tail, or comparison to a longer model window.

The microphone recording does not uniquely identify a physical hammer, string material, or board. SFZ-bin MIDI velocities are control representatives, not measured hammer velocities. Pedal, room, microphone and editing conditions remain uncertain. Full-envelope and spectral metrics must remain visible even when unreliable individual observations are excluded from fitting.

## Parameter order

1. **Fundamental and stiffness.** Good, identifiable fits with at least four peaks constrain `f1` and `B`. A detected fundamental can constrain pitch when stiffness is not identifiable. The no-peak nominal placeholder does not count as a measurement. Candidate-only tuning bounds are widened to `[-70,+70]` cents, matching the frozen pitch extractor search bounds; measured A0 and C8 tuning then survives without clipping. C7 retains an inherited positive stiffness prior because no upper-partial fit was identified. C8upper peaks are too weak and inconsistent to identify stiffness. A wider scan finds a much stronger early component near4434Hz, while the vendor-consistent candidate family remains near4276Hz; neither is promoted to a unique physical string identity. The normal candidate keeps that carrier with an ambiguity flag and the original positive bounded stiffness prior.
2. **Late and prompt loss.** Reliable partial-band amplitude slopes supply positive log-smoothed losses. Weak, irregular or absent measurements borrow the inherited full-model field. The late-fit gate also requires useful recorded power in both late windows. `prompt >= 1.1 * late` retains a nonnegative common-unison dissipation rate. These are initial effective loss estimates: coupled-state renders, not a single isolated exponential, determine the final behavior.
3. **Hammer and velocity.** The original fitter sets `hardness=1` and supplies authored velocity exponents; it does not identify them from microphone attack rise. `strike-bank` creates five bounded physical probes: baseline, hardness ×0.8, hardness ×1.25, and velocity-exponent offsets ±0.08. The actual nonlinear solver must render each probe. Compare transient bands, crest, centroid, full body/envelope and soft/hard amplitude contrast before choosing. One scalar RMS rise is not a hammer-contact measurement. Leave detuning unchanged until resolved beats provide evidence; a weak late spectral peak is insufficient to infer individual unison tuning.
4. **Radiation magnitude.** Render the selected mechanics/strike profile once with fitted observation magnitudes disabled. Fit primary and secondary positive magnitudes jointly using the actual three-component stem Gram matrices over four windows and two velocities. This preserves phase interference, the nonlinear strike, the residual board transient and all mechanical interactions. `radiation_after_db` is the secondary-polarization observation field, not a time-varying fade. Values are absolute `20 log10(|H|)` targets, not correction dB. Existing gain bounds `[0.025,40]` and the analytic return above partial64 remain intact.

Do not fit radiation first and then interpret the resulting compensation curve as hammer hardness or a material property. Misplaced harmonics require tuning/stiffness changes; an output gain cannot move them.

## Candidate-only source integration

The old `Cal` assumes five octave-spaced anchors. A larger header alone would silently select the wrong fields. The `build` stage makes five exact, checked replacements in an explicit source copy:

- Bracket the sorted measured anchor notes using their actual semitone spacing.
- Retain measured pitch within `[-70,+70]` cents.
- Apply bass stiffness extrapolation only below the first measured anchor.
- Apply intrinsic treble loss extrapolation only above the last measured anchor.
- Apply prompt/common-unison treble loss extrapolation only above the last measured anchor.

The source builder does not change MIDI/control behavior, hammer/contact equations, bridge coupling, mode caps, polarizations, board geometry, complex radiation phase, or arithmetic precision. String-mode counts may change when measured tuning/stiffness moves a mode across the existing frequency cutoff. The canonical source and the preserved original remain unchanged. Any separately approved hot-loop/precision transform is a later step with its own provenance and numerical checks.

## Reproduction commands

Run from the repository root with Python, NumPy and SciPy available. `OPENBLAS_NUM_THREADS=1` keeps this small offline fit from competing with parallel full-solver renders.

```sh
OPENBLAS_NUM_THREADS=1 python3 tools/fit_full_calibration.py mechanics \
  --output out/full-calibration/reproduced/mechanics

python3 tools/fit_full_calibration.py build \
  --profile out/full-calibration/reproduced/mechanics/calibration.json \
  --source src/full_reference/grand.cpp \
  --output out/full-calibration/reproduced/mechanics/solver

c++ -O3 -DNDEBUG -std=c++17 -ffp-contract=off \
  out/full-calibration/reproduced/mechanics/solver/grand.cpp \
  -o out/full-calibration/reproduced/mechanics/solver/grand

out/full-calibration/reproduced/mechanics/solver/grand --self-test
```

The source profile, generated header, source hash and every targeted replacement are recorded in the output. Version3 mechanics/analytic headers are generated from the corrected TRAIN34 export. Version2 historical header reproduction is retained in the design report; it is a software reproducibility check, not evidence for the old C8pitch interpretation. Reproducing a JSON report after a tool change updates its provenance hash even when every numerical header value is identical.

The historical v2 C8joint stiffness proposal used the old three-peak estimate, which the wider audit rejected as identifiable stiffness. It is preserved under `out/full-calibration/v2/c8-joint` for traceability. Current C8measurements set `B_identifiable=false`, clear those unreliable peak IDs, and retain the original bounded positive stiffness prior. The optional `stiffness-proposal` command requires actual three-order observations at both velocities; it should reject the corrected C8export rather than manufacture stiffness from the unassigned component.

Once the mechanics/strike choice is made, create the analytic observation render:

```sh
python3 tools/fit_full_calibration.py analytic \
  --profile out/full-calibration/reproduced/mechanics/calibration.json \
  --output out/full-calibration/reproduced/analytic

python3 tools/fit_full_calibration.py build \
  --profile out/full-calibration/reproduced/analytic/calibration.json \
  --output out/full-calibration/reproduced/analytic/solver

c++ -O3 -DNDEBUG -std=c++17 -ffp-contract=off \
  out/full-calibration/reproduced/analytic/solver/grand.cpp \
  -o out/full-calibration/reproduced/analytic/solver/grand

python3 tools/render_full_training.py \
  --renderer out/full-calibration/reproduced/analytic/solver/grand \
  --source out/full-calibration/reproduced/analytic/solver/grand.cpp \
  --calibration out/full-calibration/reproduced/analytic/solver/calibration.h \
  --stems --rate 48000 --jobs 2 \
  --output out/full-calibration/reproduced/analytic/renders
```

The render CLI's `--dump-radiation FILE` option produces the analytic basis. Supply a normal training event/output/duration command along with that option. The dump must come from the exact selected mechanics solver, since its partial frequencies and loaded bridge response depend on that profile.

Measure the actual full renders and fit:

```sh
OPENBLAS_NUM_THREADS=1 python3 tools/fit_full_calibration.py score \
  --renders out/full-calibration/reproduced/analytic/renders \
  --output out/full-calibration/reproduced/analytic/measurement

OPENBLAS_NUM_THREADS=1 python3 tools/fit_full_calibration.py radiation \
  --profile out/full-calibration/reproduced/analytic/calibration.json \
  --exclude-ambiguous-anchors \
  --model-features out/full-calibration/reproduced/analytic/measurement/model-features.json \
  --basis out/full-calibration/reproduced/analytic/radiation-basis.json \
  --stems-dir out/full-calibration/reproduced/analytic/renders \
  --render-manifest out/full-calibration/reproduced/analytic/renders/render-manifest.json \
  --output out/full-calibration/reproduced/radiation
```

Radiation fitting validates the manifest against the actual source, binary, both analytic header copies, reference-feature export, locked split and frozen guard. Every full/primary/secondary/transient WAVhash and held-note event file must match its per-render receipt. The batch must be complete, finite, and retain230strings/475board modes. Full-render feature hashes, stem shapes/rates, and reconstruction within0.5% RMSare checked again during Gram integration. Input/output identities are rechecked after fitting. Never use already corrected stems as an analytic basis: fitting their gains relative to analytic `|H|` would apply the correction twice.

The current renderer records the fitter's training-guard hash and rejects tool/input changes during a batch. Freeze the fitter before a render. Keep separate candidate version directories; do not rewrite a running batch's source or calibration.

## Quality gates and evaluation

The radiation stage measures edge-fundamental prominence per actual reference window, using the same Hann spectrum and target band as the power fit. Two adjacent bands have the same combined width as the target. A window below6dB target/neighbor power is excluded individually and fully recorded. This is a conservative reliability rule, not a measured SNR or identified ambient-noise spectrum. It excludes11 of24 edge-H1 windows on TRAIN34, while retaining C8's clearer0.25–1.5-second body windows and the clear late A0hard fundamental. It does not fit subfundamental hum or an added noise source.

With `--exclude-ambiguous-anchors`, C8 is removed from global gain estimation, observations and field smoothing. Its two supplied prior observation arrays remain exactly unchanged through profile/header serialization. Its total waveform can still change through the fitted observation of other sympathetically coupled strings; field preservation is not an audio-byte-parity claim.

The corrected C8rows include `unassigned_components`, with fixed reference centers, four-window powers, channel powers, bandwidths and decay diagnostics. Model measurement uses those exact reference centers even if no model peak is detected there; it never moves the measurement to a different model peak. Separate component errors remain outside the two-polarization radiation objective. The existing observation magnitudes cannot create a distinct frequency absent from the mechanical response.

The bounded audit at `out/full-calibration/c8-component-audit/report.json` found no prominent shared4434Hz line in ten other training keys. C8's first50–250ms band is about−8.0/−3.7dB relative to its early RMSpower, compared with−66.4/−57.6dB forC7 and still lower levels forC6/C5. Its early fixed-band decay is approximately−49/−51dB/s. This supports a key/register-localized component within this corpus; it does not identify duplex, string, body or frame uniquely. The prior full-model renders underpredict that component by about85–88dB in the first two prominent windows after common early-gain alignment. This is an explicit missing-component limitation, not a target for broadband or radiation-gain compensation.

The `score` stage retains the original whole-envelope, four-window band, harmonic, decay and tuning metrics. It adds0–5/5–20/20–50/50–100ms band power,250–19000Hz centroid, crest, peak-frequency residuals and a separate unnormalized soft/hard amplitude contrast. A separate `spurious_prominent_model_bands` diagnostic flags a window/band when normalized model power exceeds−30dB but observed power is below−50dB. It does not alter the preserved reference-masked primary metrics. This exposes loud invented model bands that the reference prominence mask would otherwise omit. The first5ms and short-window sub250Hz content remain diagnostics because onset editing and unresolved bass modes are ambiguous. The full envelope is never filtered to hide low-frequency recording disagreement. A focused comparison may pass `score --ids C8v4 C8v12`; IDs are still validated against the full locked training set.

The frozen version4 fit is at `out/full-calibration/v4/radiation`. All136 full/stem WAVhashes and34 held-note event files, plus actual source/binary/header/split/reference/guard identities, passed before fitting and were rechecked afterwards. It makes254 partial fits across32 cases/16anchors and preserves both C8prior fields exactly. Its median per-partial weighted TRAIN RMSE improves from5.48 to3.33dB after regularization;42 raw partial fits reach a gain bound. This is a fitting diagnostic, not the legacy acoustic MAE or a listening score. The joint optimizer reaches its existing350-iteration cap (`converged=false`, objective10216→8725), which remains an explicit numerical limitation.

After generating the final radiation header, build and render it again: the fitting report is not the final synthesized sound. Run physical self-tests, finite/energy/passivity checks, mode/topology checks, onset/struck-texture comparisons, body/late regressions and audible musical examples. Freeze source/header/binary hashes before a separate evaluation. Training gains and known historical regressions are not proof of generalization, and no price/product-readiness claim follows from these metrics alone.

## Version 4 actual synthesis and frozen evaluation

The final candidate was rendered again for all 34 training cases at 48 kHz,
using the full topology and the bounded hot-float precision candidate. These
are actual synthesized-waveform results, separate from the radiation objective:

| TRAIN34 mean error | Original-calibration control | Final candidate |
|---|---:|---:|
| Harmonic levels | 7.852 dB | 6.911 dB |
| Envelope | 6.101 dB | 5.011 dB |
| Broad spectral bands | 14.388 dB | 13.692 dB |
| Partial tuning | 4.162 cents | 0.705 cents |
| 5–100 ms prominent attack bands above 250 Hz | 6.766 dB | 5.552 dB |

Harmonic error improves in 24 of 34 cases and envelope error in 19. The worst
harmonic regression is C8v4, +0.92 dB; the worst envelope regression is D#4v12,
+1.34 dB. The separate spurious-band diagnostic drops from nine to five flagged
window/band pairs. The C8 component remains missing. These training results
justify evaluating this research candidate, but do not establish a better
default by listening or authorize promotion. The full per-case comparison is
in `Validation/full-calibration-v4-training.json`.

`tools/evaluate_full_candidate.py` keeps evaluation outside the fitter's locked
TRAIN-only interface. Its stages are `freeze`, `predictions`, `acquire`, `score`
and `verify`. The immutable freeze receipt is
`Validation/full-calibration-v4-freeze.json`, SHA256
`100cf59663e203c58acfaa88c220d6cc270ee777437b5a7f5c974c205c24c105`.
It pins the exact control/candidate source, header, binary, extraction methods,
training evidence and evaluation protocol before first fresh acquisition.
All 32 synthesized predictions for two fresh extreme notes and 14 historical
regressions must be complete before reference opening. An opening marker also
prevents a rerender after an interrupted first decode.

The forecasts expect A0v8 to improve but explicitly expect C8v8 to retain its
missing-component failure. Each fresh extreme is reported individually;
seven full-range and seven interpolation regressions are historical evidence.
Every regression remains visible, with harmonic/envelope increases above 2 dB
flagged. The evaluator never adjusts the model after evaluation, preserves the
reference's short-tail support, and measures unassigned components at reference
frequencies. Fresh acquisition receipts and decoded files are kept in the
evaluation directory; the immutable fitting manifests/features are unchanged.

The frozen evaluation is complete. Two genuinely fresh extreme recordings were
decoded only after every prediction was rendered. Fourteen historical cases
were kept separate. The stored acoustic measurements were audited without
repeating the acoustic scoring pass.

| Evaluation case/group | Harmonic error, control → candidate | Envelope error, control → candidate | 5–100 ms attack-band error, control → candidate |
|---|---:|---:|---:|
| Fresh A0v8 | 10.417 → 5.209 dB | 7.780 → 3.215 dB | Individual windows in report |
| Fresh C8v8 | 36.887 → 37.671 dB | 15.527 → 14.883 dB | Individual windows in report |
| Historical C1–C7 layer 8, seven cases | 6.012 → 5.519 dB | 4.668 → 4.291 dB | 6.561 → 6.159 dB |
| Historical interpolation, seven cases | 5.614 → 5.225 dB | 7.171 → 7.674 dB | 3.136 → 2.518 dB |

The A0 harmonic/envelope forecast passed, but its scalar 10–90% RMS-rise error
regressed from 1.44 to 38.13 ms, and its decay-slope error increased from 4.765
to 5.327 dB/s. Better attack-band texture does not establish a better attack
shape. C8's observed unassigned component is 4433.804 Hz; the candidate is about
83 dB too weak in its first two prominent windows after early-gain alignment.
C8 also needs approximately 40 dB of per-case early-gain normalization, making
its raw level another unresolved limitation. Its ambiguous candidate family is
4276.516 Hz, with unidentifiable stiffness. Neither family is reinterpreted to
hide the failure.

All A3 velocities regress in envelope error by approximately 0.92–1.09 dB.
The interpolation envelope mean therefore fails the frozen historical
generalization expectation. No individual harmonic/envelope regression exceeds
the predeclared 2 dB reporting threshold, but smaller regressions remain visible.
The separate spurious-band diagnostic improves from five to two flagged
window/band pairs across all evaluation cases.

The candidate remains an experiment and **is not promoted to the default**.
No tuning follows this evaluation; A0v8 and C8v8 are now observed regression
evidence for any future method, never fresh cases again. The complete source
quality flags, per-case metrics, early gains, fixed-frequency component errors,
and every regression are in `Validation/full-calibration-v4-evaluation.json`.
`Validation/full-calibration-v4-acquisition.json` supplies authenticated FLAC,
decoded PCM and license provenance. These results cover one acoustic piano and
recording setup, not a listening panel, another piano or a Reason host.
