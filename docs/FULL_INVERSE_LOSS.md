# Full-network loss response experiment

This bounded experiment tests the calibrated damping fields against actual
connected-model output. It changes private profiles under `out/full-inverse-loss`
and does not alter the canonical solver, prepared instrument, controller,
calibration or plugin wrappers. No recording waveform enters the synthesizer.

The frozen base is the version-4 full-model radiation candidate. That candidate
has not been promoted. This experiment uses only the locked TRAIN34 feature
export and authenticated TRAIN audio; it does not open evaluation references or
use their numerical features to select parameters.

## What the fields mean

The calibrated primary string's intrinsic amplitude-loss coefficient is
`0.82 * late`. Its bridge transformer is chosen so that an isolated string
against a fixed board has approximately `0.18 * late` additional amplitude
loss: `b² = 2 * 0.18 * late / 0.85`, with resistance `0.85`. This split is
intentional. It is not evidence of an accidental duplicate application of the
entire measured loss.

The actual moving board and reciprocal multi-string network differ from that
fixed-board approximation. The secondary polarization uses `0.60 * late` and
a weaker bridge transformer. The common-unison operator applies the
nonnegative excess `prompt - late` to the choir's in-phase motion; out-of-phase
states can survive differently. Interference and pickup therefore make a
microphone partial-band slope different from one uniquely isolated damping
coefficient.

The experiment scales `late` and the excess separately:

```text
new_late   = late_scale * old_late
new_prompt = new_late + excess_scale * (old_prompt - old_late)
```

Both operators remain dissipative and all other profile fields remain exact.
The factors apply to the seventeen profile anchors. Intervening keys retain
the existing positive log interpolation of late and prompt fields; the excess
at an interpolated key is not asserted to be exactly the same scalar multiple.
Changing late changes both intrinsic loss and bridge-transformer strength.
The analytic `radiationTransfer` response depends on the unchanged board,
frequencies and fixed bridge resistances, so its precomputed phase does not
change. Its modal pressure coefficients contain the bridge transformer and
therefore change amplitude with late. Actual coupled-state evolution can also
change the resulting waveform phase and interference. The radiation target
arrays are never refitted in this test.

## Frozen pilot

Before any new response was rendered, `freeze.json` fixed these ten TRAIN cases:

`A0v4, A0v12, C2v4, C2v12, C4v4, C4v12, D#4v4, D#4v12, C6v4, C6v12`.

Its initial SHA256 is
`ddae981acba9777d20a92d28775dbff444afdfcbb7d1b996b7e58ab045e654a9`.
It records exact source/header/binary/profile/feature/split/tool identities,
authenticated reference PCM links and the cached baseline producer/event/WAV
hashes. The base already used all TRAIN34 for earlier fitting; transfer to
the remaining TRAIN cases would be conditional confirmation, not a new blind
evaluation.

Four banks are fixed in advance:

| Bank | Late scale | Prompt-minus-late scale |
|---|---:|---:|
| late-down | 0.7 | 1 |
| late-up | 1.3 | 1 |
| excess-down | 1 | 0.5 |
| both-down | 0.7 | 0.5 |

Each bank retains all strings, polarizations, unisons, board modes, hammer
parameters, tuning, stiffness, detuning, damper behavior and radiation target
arrays. The private renderer uses the same tested hot-float arithmetic as the
base at 48 kHz. Notes begin at 0.1 seconds, remain held, and are measured over
the same support as the base in 3.8-second renders. At most two renders run
concurrently. Render wall time is not a realtime measurement.

## Acceptance and interpretation

The frozen report compares every case's full-envelope, harmonic, broadband,
partial-decay, tuning, RMS-rise and prominent 5–100 ms attack-band errors.
Unnormalized soft/hard velocity contrast and spurious model bands remain
visible. The full envelope is not filtered to hide low-frequency/body power.

A candidate must improve mean envelope error by at least 0.25 dB without a
case regression above 0.75 dB, then pass the separately frozen harmonic,
attack, decay, rise, tuning, velocity and spurious-band limits. A passing
setting can be confirmed on all TRAIN34; that confirmation does not select a
new setting and does not authorize default promotion. The complete limits and
per-case results belong to the machine-readable report.

The cached base already shows why one global decay explanation may be
insufficient. Many late envelopes contain too little normalized power, while
reliable upper-register partials can decay more slowly than their recorded
counterparts. Adding longer-lived harmonic energy might fill an envelope and
still worsen struck texture or harmonic decay. Background, room, library
editing, pedal state and unresolved body content remain acquisition confounds.
They are not relabeled as identified material damping.

## Prospective refinement and separate condition check

None of the first four banks passes every frozen pilot gate. The
common-unison-excess scale 0.5 passes fourteen gates and misses only the
C6v12 envelope limit: +0.875 dB versus the +0.75 dB cap. It improves mean
envelope error by 0.625 dB and prominent attack-band error by 0.368 dB. The
limit is not relaxed after seeing that result.

A single additional global excess scale 0.6 was registered separately before
its predictions, under `out/full-inverse-loss-refinement`. Its freeze SHA256 is
`ba1a83ec9d14ab0692e1eaa8dda64e4e828871316a6db56cbbe59c209db30083`.
It keeps every gate and every other field unchanged, pins the initial TRAIN
report, and uses no pedal-condition result. A passing refinement can reuse
its ten authenticated pilot predictions and render only the other twenty-four
TRAIN cases for confirmation.

An independent prospective pedal-condition diagnostic is registered at
`out/full-pedal-condition/freeze.json`, SHA256
`981a26a370106d184f0d50a2d6b5f46c1500397962f7b4884f1f2aecef7ee9e9`.
It compares pedal 0, 0.5 and 1 on A0/C4/D#4, both TRAIN layers, with unchanged
profile and early pedal settling. Pedal 0 reuses the cached predictions. This
tests sensitivity to unstruck-string damping and sympathetic response; it
does not identify the undocumented recording condition or propose holding the
live pedal down. It does not enter loss-bank selection.

The original four-bank driver/report are archived with their exact frozen
hashes. A versioned explanatory correction clarifies that changing late loss
does not change the analytic loaded-board `H` phase. No predictions, acoustic
scores, numerical results, gates or selections were changed by that prose
correction. The current driver contains the corrected explanation.

## Actual confirmation result

The separately registered excess scale 0.6 passes all fifteen unchanged pilot
gates. Its ten-case mean envelope error improves by 0.595 dB and attack-band
error by 0.323 dB; the worst envelope regression is +0.641 dB. It was then
confirmed on the other twenty-four TRAIN cases without choosing a new setting.
The ten pilot predictions were authenticated and copied, rather than rendered
again; the combined manifest distinguishes those sources from the new runs.

It does **not** pass the confirmation. The global correction is not promoted.

| TRAIN34 mean error | V4 base | Excess scale 0.6 |
|---|---:|---:|
| Whole envelope | 5.011 dB | 4.678 dB |
| Harmonic levels | 6.911 dB | 7.067 dB |
| Prominent attack bands | 5.361 dB | 5.048 dB |
| Partial decay slope | 3.917 dB/s | 3.812 dB/s |

The attack figure is an unweighted mean of per-case MAEs across accepted
5–100 ms bands above 250 Hz. It differs from earlier reports' flat average of
accepted band cells; the underlying feature measurements are unchanged.

C7v12's envelope regresses by 0.997 dB, exceeding the unchanged 0.75 dB cap.
The same case's harmonic regression is 1.022 dB, exceeding its 1 dB cap. The other
twenty-four cases improve mean envelope by only 0.223 dB, below the unchanged
0.25 dB minimum. Spurious-band flags remain five. Every case and every gate is
retained in `Validation/full-inverse-loss.json`; the failed four initial banks
remain alongside the refinement.

The [pilot heatmap](../Validation/full-inverse-loss-pilot.png) keeps the ten
individual cases visible alongside their mean gains. It is also available as
an SVG for export.

The response confirms that prompt/aftersound balance contributes to the missing
midrange envelope power. It does not justify one global loss correction across
registers and dynamics. No further setting is chosen from the confirmation,
and no historical evaluation file is opened or rerendered. A future inverse fit
would need to distinguish observable body/aftersound balance, recording
condition and identifiable damping while retaining the full waveform checks.

## Reproduction

Use a new output directory if any frozen input or tool changes:

```sh
OPENBLAS_NUM_THREADS=1 python3 tools/probe_full_inverse_loss.py run \
  --output out/full-inverse-loss-reproduction \
  --report out/full-inverse-loss-reproduction/report.json
```

Separate `prepare`, `pilot`, `report` and `validate-selected` stages are also
available. A failed gate is retained with its regressions. No evaluation
recording is automatically opened, and no canonical file is generated.
The separately registered refinement uses `--refine-excess` and a new output
directory; it requires the retained initial report at
`out/full-inverse-loss/report.json` as its TRAIN-only selection receipt.

The separately fitted [confidence-prior phase](FULL_CONFIDENCE_LOSS.md) retains
weak-anchor priors instead of applying a global correction. It uses all TRAIN34,
then freezes the candidate for previously observed historical regression and
matched listening. That later phase does not change the failed global result.
