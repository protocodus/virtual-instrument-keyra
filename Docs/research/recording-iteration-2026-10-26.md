# First real-time recording iteration — 26 October 2026

Keyra's preserved offline solver is an expensive reference, with nonlinear
hammer contact and reciprocal string/board coupling. The new live engine uses
a reduced modal radiation model so a DAW can play it. These are separate
implementations with different physical scope. The live engine does not inherit
the reference renderer's numerical passivity proof or its fidelity scores.

## Source and immutable split

The measurements use Alexander Holm's Salamander Grand Piano V3 recordings,
distributed under CC BY 3.0 at upstream commit
`3382bf9496bba2486f5ab0de55a264d1dfc38404`. The original reference
[attribution](../../Experiments/Research/GrandPianoV2/reference/ATTRIBUTION.md) describes the
piano, microphone configuration and acquisition limits.

All 24 source FLAC hashes and losslessly decoded PCM identities were verified
against the pinned manifest. The current ffmpeg writes different WAV container
headers; the sample rate, channel count, 24-bit precision, frame count and every
decoded sample match the preserved identities.

The existing split is unchanged:

| Purpose | Cases |
|---|---|
| Training | C2–C6 at velocity layers 4 and 12: 10 |
| Held-out velocity | C2–C6 at layer 8, C3–C5 at layer 6: 8 |
| Held-out pitch | F♯2–F♯5 at layer 8: 4 |
| Edge extrapolation | C1 and C7 at layer 8: 2 |

The layer midpoints, 40, 49, 61 and 93, are MIDI benchmark inputs. They do not
measure physical hammer velocity. Held-out cases are never opened by the
calibration generator. Subsequent changes selected after inspecting these
held-out results will need fresh validation captures; repeatedly tuning to this
same set would make it development data.

## Compact numerical calibration

`Tools/fit_realtime_modal.py` reads only the ten training WAVs and the existing
training-derived pitch/loss estimates. It measures 64 stiff-string partial bands
in the same four onset-aligned windows as the frozen benchmark. The original
feature file stopped at 48 partials; the additional low-register bands are
measured from training audio alone.

Each retained mode has two nonnegative amplitude components and positive decay
rates. The fit minimizes Hann-weighted window-power error, regularized toward
the robust training-derived prompt/late slope estimates. The prompt rate remains
larger than the late rate. Weak bands below a relative power floor and modes
above 17 kHz become silent. The generated C++ header contains numbers, with no
recorded waveform, phase trajectory, impulse response or runtime audio loading.

The first iteration assumed incoherent unison power. Its small training fit
residual did not predict the emitted engine: deterministic phases and detuning
produce coherent beating. The emitted training harmonic error was 5.59 dB and
the envelope error was 7.53 dB. Iteration two fits the same ten training notes
against the engine's authored phase, detune, stereo-pan and unison-normalization
laws. It integrates the cross-unison difference-frequency terms explicitly;
recorded phases remain unused. On actual emitted training audio, harmonic error
falls to 2.18 dB, envelope error to 5.27 dB, and decay-slope error from 3.10 to
2.10 dB/s. The first-iteration reports and fit metadata are retained separately.

The remaining training envelope error is concentrated in C6: 18.74 dB for the
lower layer and 13.91 dB for the upper layer in the isolated source probe.
The other eight training cases range from 1.86 to 3.10 dB. Missing room,
broadband/late recorded energy and compact modal decay remain material gaps.

This decomposition is not uniquely identified by four power windows. It models
the recorded output compactly; it does not establish a unique mechanical hammer,
string or soundboard. Its reported training window residual is a fit diagnostic,
not an audio fidelity score.

The attack iteration compares a fixed 2 ms radiation rise with an anchor-specific
exponential rise, whose time constant is the training recording's 10–90% rise
divided by `log(9)`. Both use the same live renderer, note events, sample rate,
deterministic phases and controls. These coefficients were finalized before
evaluating the held-out live-engine renders. A measured 5 ms RMS rise includes
beating and microphone/room effects; it is not hammer contact duration.

The generated [fit provenance](realtime-modal-fit-2026-10-26.json) records all ten
WAV hashes, immutable split, frozen features, prior calibration, measurement
source, generator source, generated-header hash and NumPy/SciPy versions. `--check` regenerates and
compares the header and metadata exactly in that environment.

## Reproduce

From the canonical repository root:

```sh
python3 Experiments/Research/GrandPianoV2/reference/fetch_reference.py --jobs 4
python3 Tools/fit_realtime_modal.py --check
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --target keyra_render -j 2
python3 Tools/evaluate_recordings.py --self-test
python3 Tools/evaluate_recordings.py --renderer build/keyra_render
python3 Tools/evaluate_fresh_recordings.py --fetch-only
python3 Tools/evaluate_fresh_recordings.py --renderer build/keyra_render
```

The live evaluation imports the preserved measurement functions without
rewriting the research split or reports. It adds a missing-partial penalty:
prominent recorded partials absent from the model receive the same fixed noise
floor, instead of disappearing from the harmonic average. The historical v2
features are scored by that same rule for context.

The evaluation saves both attack variants and the product-default variant WAVs
under `build/recording-benchmark/` and
writes a JSON report, CSV and readable tables under `Docs/validation/`. Reports
include all 24 per-case metrics, split means, the combined twelve-case held-out
mean, source/binary hashes, render commands and attack-iteration deltas. The
attack comparison sets the exposed resonance control to zero; the additional
product-default run uses 0.25. Other controls stay at their defaults.

## Fresh same-piano validation

The original held-out set was examined before the coherent-choir correction,
so its subsequent results are development validation. The correction used only
training observations, but a repeatedly inspected holdout is no longer pristine
evidence for selecting an architecture.

Before downloading any further recordings, the eight-note list D♯2–D♯5 and
A2–A5 at layer 8 was declared in a
[separate manifest](fresh-recording-holdout-2026-10-26.json), together with the
final iteration-two header hash and fit metadata hash. These are unused pitches
from the same pinned Salamander source. Their FLAC hashes and decoded PCM
identities were then pinned without extracting features. The model coefficients
remained fixed before the first fresh score. No further fitting follows that
score in this iteration.

`Tools/evaluate_fresh_recordings.py` refuses a changed model-header hash. It
retains all eight per-case errors and scores fixed attack, measured attack and
product defaults using the same renderer. This tests fresh notes within the
same piano and microphone setup, rather than generalization to another acoustic
piano, recording session or player. The
[fresh results](../validation/recording-benchmark-fresh-2026-10-26.md) preserve
the limits and the full JSON/CSV evidence.

## Evidence still needed for a premium release

These isolated held notes cannot calibrate sustain travel, half-pedal contact,
repedaling, sostenuto capture, una corda mechanics, repetition, pedal noise or
release noise. The acquisition pedal state and release times are unknown. The
new controller behavior needs musical host testing and synchronized owned
captures: controller values, MIDI note timing and unprocessed stereo audio
recorded together. Include pedal sweeps during held notes, partial releases,
repedaling around contact, selective sostenuto, repeated strikes, soft-pedal
velocity ladders and cross-register chords.

Commercial readiness also needs fresh-piano blind listening, stable host state
and automation, sustained polyphony measurements, cross-platform installer and
host validation, and Reason Studios' SDK/acceptance process. The present
measurements support model iteration; they do not substantiate a price above
USD 199 or equivalence to an established premium piano product.
