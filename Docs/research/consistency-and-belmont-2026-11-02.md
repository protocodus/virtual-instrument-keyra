# Consistency repairs and Belmont mix presence

Working research record for the owner's eight-hour improvement window, ending
2026-11-02 at 07:40 UTC. This is not a release certificate. The accepted comparison
baseline is source `a734d0fe3ad9116937de8c693826c58c6d371308b7a74f5502c5665fb7b56ed8`,
with the accepted Belmont C voicing and Mechanics at UI 0.4 / raw 0.175.

## What the comparison supports

Piano V3 remains the stronger provisional production-readiness benchmark because
Keyra has demonstrated keyboard/velocity consistency defects. This is not a
blind listening ranking, nor a claim that Piano V3 passed the same exhaustive
keyboard audit. The common Bugatti Step performance and whole-performance level
matching isolate many performance differences, but factory voicing, dynamics and
microphone choices still differ. Do not turn a spectral statistic into a claim
that somebody listened and preferred one engine.

The owner's current priority for Belmont is **generic, versatile** mix presence.
Its earlier C choice removed extra velocity darkening; that correction is already
present in the compared engine. More work therefore must start from that accepted
sound, not from the superseded dark version.

## Belmont: source character, mapping, and a real omission

The complete musical signal is predominantly modal: the signed contribution of
modal strings is 96.17% over 20 Hz–20 kHz and 91.27% over 4–8 kHz. Noise contributes 8.71%
in the high band; body and action are negligible there. These are component
contributions including cross terms, not independently summed stem powers. The
passive observer reproduces the delivered WAV exactly; reconstruction closure is
1.35e−15 relative L2.

The simple existing Brightness control has a modest effect here. Increasing it
from 0.5 to 0.75 raises whole-piece 4–8 kHz share from 0.004264% to 0.005764% in
a fixed Welch measurement; centroid moves 649.96 → 658.03 Hz. The control
applies a tilt by harmonic order, and most high-frequency energy in this
performance is at low harmonic orders. This experiment does not show that
increasing a knob by a given amount produces the same audible brightness change
in every piano.

The source recordings themselves are dark at soft and middle dynamics. At six
tested middle/upper TRAIN anchors, the hard-layer early 4–8 kHz native power is
within 0.44 dB of the cached recording measurement after the established level
alignment. A universal missing-high-frequency-content explanation is therefore
unsupported.

There is a specific omission at MIDI 99. The old detector reports peaks at
5152.231 Hz and 7992.919 Hz, but the header contains only the fundamental. The first
admission gate requires an order to be detected in two recorded layers. Rejected
detected harmonics are also excluded from residual-noise estimation, so the noise
path does not provide a fallback. This is a genuine local reconstruction defect;
only 9 of 2,819 Bugatti attacks are MIDI 99, so fixing it cannot explain or close the
entire musical high-band difference.

An isolated union-of-detected-orders trial at MIDI 99 retains the later quality
gates: at least two usable layers in the joint fit and three usable layers for
export. Partial orders 2–4 survive all three TRAIN layers without relaxing those
gates. That trial estimated stiffness B≈0.00982245 instead of the
single-fundamental fallback of 0.0001, but subsequent original-waveform checks
undermine the frequency estimates. MIDI 99's reported third partial lies only
0.430 Hz below its search boundary; the 50–150 ms recording peak at 8031.74 Hz
is 28.42 dB stronger. MIDI 108's reported second partial lies 1.927 Hz below its
search boundary, below stronger early components at 8933–8962 Hz. Neither merely
admitting those old detections nor exporting their inferred stiffness is
defensible yet.

The controlled incremental generator reproduces the accepted numeric tables,
preserves unrelated measurements, rebases halo cents without moving physical
frequencies, and regenerates the normal velocity guards. Its 7,156 paired native
cases are finite, repeat, and preserve all 240 other-piano waveforms exactly.
Those implementation checks do not validate the input measurements. A variant
retaining 108's old amplitude model while updating only stiffness likewise
remains unvalidated. Both are frozen outside the product. No unused round-robin
take exists for 99 or 108, so independent-take validation cannot be claimed.

The next acquisition discovers competing peaks before assigning harmonic order,
checks multiple time windows and unison clusters, then tests a common stiffness
family. Two frequencies determine a stiffness value but cannot independently
validate that family. In 108's hard recording, strong components near twice the
fundamental and a sharper early family make this distinction consequential.

The performance response also matters. Across the actual 2,819 note events and
their ongoing random-touch sequence, Belmont's native layer coordinate has
median 80.95, between recorded layers 77 and 116. Only 0.39% of attacks reach 116;
the mean fraction through that upper interval is 0.215. Reusing the first reset
random draw for every note would misrepresent this distribution. A separate
out-only control tested direct MIDI timbre coordinates with level compensation,
while leaving body, noise, action and release tracking alone.
Neither mapping is a measured hammer-speed law: the library is peak-normalized
and supplies three named dynamic regions, not calibrated impact velocities.

The full-performance result does not support adopting that remap as a strong
brightness repair. Despite large high-band changes in some freshly reset single
notes, Bugatti's whole-piece 4–8 kHz share increases only 0.37 dB; the theme and
dolce excerpts decrease by 0.09 and 0.44 dB. Whole-piece RMS changes by −0.010 dB.
Capping the timbre coordinate at the hardest recorded layer affects only three
attacks and gives almost the same result. Individual decay windows also change
materially. Small spectral differences do not mean the waveforms are identical
or that a listener could not hear a difference. The experiment remains out of
the product; its frozen report is `belmont-timbre-coordinate/report.md`.

## Why the obvious consistency patches have not been adopted

| Candidate | Benefit | Reason it remains out of the product |
|---|---|---|
| Enable every velocity interval passing endpoint-power bounds | Repairs the original New York 27 / Hamamatsu 56 reversals | Full 67,056-note grid introduces a 1.6 dB onset reversal and changes some measured early/middle envelopes by 5–7 dB |
| Shortest-arc lane phases | Removes near-antipodal phase-speed singularities | New actual-key velocity reversals reach 2.88 dB; exact-anchor failures also remain |
| Coherent colour energy | Repairs the New York 27 early reversal | Does not fix phase-envelope failures; fails unchanged Hamamatsu Tube playing-level limits |
| Reference-window mono alignment | Recovers severe early mono cancellation in all six witness pianos | Full 6,864-case grid exposes Hamburg held/release losses of 5.78/11.51 dB |
| Multiwindow no-loss mono phase constraints | Removes those selected late losses | Adjacent floating-point build settings cause a large native waveform jump; RMS alone nearly hides it |

All of these trials are retained with input/source hashes, numeric observations,
negative results and reproducing code under `out/consistency-repair-20261101/`.
The temporarily integrated mono change was explicitly restored to the accepted
source after its wider failures. No rejected candidate should be described as a
completed repair merely because it passes finite-output or targeted tests.

## Interpolation representation under investigation

The existing four exponential lanes are an ill-conditioned interpolation chart
for some measured patterns. Exact repeated poles occur in 648 of 3,382 partials;
plain Gram whitening is consequently not a general replacement. An input-normal
four-state lattice reconstructs the endpoint patterns, including duplicate poles,
without a matrix inverse or extra oscillators. It is a numerical representation,
not an improved piano by itself.

On 84 independent central-velocity pitch points across six frozen intervals,
fitting stereo covariance in seven native windows reduces mean absolute power
error from 2.138 to 0.776 dB with fixed geometric endpoint energy. Allowing
energy within the endpoint interval reduces it to 0.460 dB. Worst errors remain
5.72 and 4.64 dB, and two/three optimizer runs respectively reach their declared
limits. Independent point fits are unsuitable as runtime tables: a shared
continuous pitch/velocity field, mixed-build semantics, held-note control
behavior and native CPU costs remain required. The eight-state union-pole
control improves mean absolute error to 0.473 dB, but 48 of 84 optimizations
reach their limit. Its 30.34 dB worst relative error occurs against a −269.99 dB
analytic tail target, and therefore is not evidence of an audible defect. The
target-normalized quadratic objective is badly scaled there. A separate
log-power/normalized-covariance objective was tested with the same points,
targets, energy and optimizer policy. Mean error improves only from 0.473 to
0.450 dB, 158 of 588 windows regress, and 50 of 84 runs reach their limits.
Hamamatsu mean error rises from 1.136 to 1.355 dB. Neither formulation is an
accepted interpolation replacement.

A separate velocity-field experiment preserves measured poles and microphone
pickups, including exactly redundant pole directions. It fits one polynomial
excitation path per recorded velocity interval, retaining the endpoints and
geometric complex-envelope energy. Across 28 intervals at four New York and
Hamamatsu anchors, mean absolute seven-window target error improves from 0.653
to 0.165 dB. That average conceals a 10.46 dB onset overshoot at a withheld
velocity coordinate; four optimizer runs also reach their declared limit.
An exact rational certificate proves the ideal rounded polynomials never have
zero normalization, but one passes close enough to zero to change direction
rapidly. Thus continuity alone does not establish a good interpolation. The
analytic operator agrees with independent quadrature for 784 fitted controls to
4.77e−15 relative covariance error; this verifies the calculation, not acoustic
quality.

A bounded Bezier curve removes that near-zero normalization geometry and reduces
the analytic maximum error to 3.982 dB (mean 0.170 dB). Independent native
coefficient readback agrees to 5.54e−15 relative error. Nevertheless, the
4,788-case full-engine panel reveals material new pitch-coupled changes:
Hamamatsu note 79, velocity 65, onset −8.58 dB; note 77, velocity 64, late
−18.80 dB; and note 79, velocity 77, release +27.42 dB. The candidate remains
rejected. Optimizing recorded-pitch velocity curves separately does not solve
the joint pitch/velocity field. Exact internal endpoints pass; public float MIDI
endpoints differ at up to −132.55 dB relative waveform level. The originally
failed exact-PCM contract remains recorded, with that numerical diagnosis
alongside it.

## Belmont stereo reconstruction

Across 27 TRAIN note/layer cases, the source and native 50–750 ms, 1–4 kHz
mono-versus-stereo medians are −4.91 and −4.52 dB. Strong cancellation is
substantially present in the recordings, so removing all cancellation would
change their microphone character. The reconstruction still exaggerates it at
some notes: at note 72, velocity 77, source −11.49 dB becomes native −18.28 dB
despite only +.033 dB stereo band-level error. At note 72, velocity 25, the
model instead reduces cancellation. A universal polarity or phase correction is
not supported.

The second-partial region carries 99.65% of the source 1–4 kHz energy at note
72, velocity 77. Its complex-envelope mono loss progresses from −11.44 dB in the
source to −25.40 dB in the raw joint fit, −18.37 dB in the shared-pickup
approximation and −18.40 dB in the accepted runtime-like model. The original
complex fit already misses the stereo relationship; phase data are present, and
export is not the main cause. Two fitted poles coincide exactly. The actual
spectral peaks are inside the allowed search, unlike 99/108. An additional
measured-spectrum starting point finds a lower original fitting objective
without selecting by desired mono gain. The existing fitter tried these
frequency seeds only after a bound-hitting retry; this fit was poorly resolved
while remaining inside its bounds. Trying the same seeds independently of that
retry reduces the original objective by 26.35%. The other two frozen control
notes keep their original winners.

The conditional export preserves the accepted onset clock and floor, fundamental,
stiffness, cents, all other partials, global parameters, and the original 405
velocity guards. Three TRAIN layers improve their native 1–4 kHz mono/stereo
ratio error, while stereo power stays within 0.08 dB of the source. Medium and
hard 0.75–1.5 s level errors improve from about −10.4/−12.3 dB to −0.28/−0.33 dB.
Soft 3.5–8 s sustain becomes 3.84 dB weaker, and the later hard tail is still
under-represented. Those are retained regressions, not omitted quiet windows.

Four repeat-role takes, excluded from this fit, all improve partial-level MAE
(1.159 → 0.633, 4.607 → 4.365, 3.590 → 2.632 and 3.652 → 2.694 dB). Soft repeat
decay errors worsen by 0.185–0.370 dB/s and medium early errors by 0.250–0.284
dB. These are independent takes for this fit, not newly sealed recordings or a
listening verdict. No hard-layer repeat is available.

The 10,668-case native panel covers notes 69–75 at all 127 velocities and four
static profiles, against unchanged and locally remeasured residual-noise
variants. All numerical/output checks pass; both unchanged neighbouring anchors
remain byte exact across every velocity/profile. There is a real local balance
tradeoff: ordinary C5/v94 late pitch curvature changes −0.924 → +2.947 dB as the
missing sustain returns. Some tiny late/release reversals also appear; the worst
new whole-stereo step is −0.0845 dB in Soft = 1 release at −93.07 dBFS. The
unchanged playing-level suite passes. This supports a local reconstruction
repair, not a claim that the whole keyboard is now uniform.

The complete Bugatti performance barely changes: raw RMS −0.019 dB and
full-piece 1–4 kHz mono power +0.011 dB. The soft phrase's mono loss changes
−8.894 → −8.660 dB. C5 repair alone therefore does not solve Belmont's overall
mix presence.

## Narrow velocity correction and wider guard

An isolated ablation identifies two causes: Hamamatsu note 56 partial 2 and New
York note 29 partial 14, each in one recorded-layer interval. Enabling the existing
bounded whole-partial interpolation on those intervals repairs the original
native witnesses. Enabling New York 24 partial 14 alone barely helps and is not
part of the two-interval candidate. No modal coefficient or runtime formula was
changed in this causal experiment.

Across 6,096 paired ordinary-play cases (Hamamatsu 53–61, New York 21–35, all
velocities), the two-interval candidate introduces no new velocity reversal and
worsens no existing negative step in any of five windows, either channel, stereo
or mono. Hamamatsu's worst attack step improves −0.791 → +0.020 dB; New York's
worst early step improves −0.850 → −0.102 dB. Existing problems elsewhere in
those spans remain. Pitch balance changes: the largest additional Hamamatsu late
curvature is 2.08 dB, and New York early curvature increases by 0.83 dB at one
note.

The completed control follow-up adds 22,860 paired cases covering Soft = 1, mono
width, Tube microphone and both Brightness endpoints. Across all five windows
and L/R/stereo/mono, it introduces no new velocity reversal, worsens no existing
negative step and never increases per-note excess variation. Endpoint audio and
reset repeats remain exact. A general selector is being evaluated through the
actual pitch interpolation and whole-note colour gain. Selecting by a partial's
anchor energy alone cannot detect the demonstrated interactions. The two
hand-selected bits are diagnostic evidence, not an undocumented production
exception.

The frozen generic all-channel rule independently selects Hamamatsu 56/p2, but
rejects New York 29/p14. The latter improves whole-modal excess variation yet
worsens p14 itself in a longer 1.5–3.5 s left-channel window. That partial is
24–31 dB below the whole-modal channel at the interval endpoints. This does not
contradict the short full-wave test; it is a distinct, conservative constraint.
The original criterion is retained without a note-specific exception. A bounded
raw-fit check of New York 24/p14 and 29/p14 also yields no replacement: 24's extra
start is worse, and 29 has only one resolved component so the start is skipped.
All ten TRAIN source/PCM identities pass; no new fit is exported.

## Broader fitting panel

A frozen eight-partial TRAIN panel tests the same additional start. Four produce
substantial objective reductions: New York 74/p1 (27.57%), New York 49/p2 (73.09%),
Belmont 81/p1 (38.81%) and Belmont 96/p1 (14.10%). Hamburg 87/p1 improves the
objective only 0.17% while worsening a supported loud tail by 9.48 dB; it is held.
Two other changes are numerical-scale and Hamburg 80 keeps its original winner.

The four isolated exports preserve all unrelated measurements and stock guards.
They still have supported-window tradeoffs: New York 74's hard late2 level error
worsens about 2.09 dB, New York 49's hard late2 by 0.45 dB, Belmont 81's hard middle
by 0.73 dB and Belmont 96's hard middle by 1.68 dB. The completed native source
panel and compact neighbourhood checks distinguish these outcomes:

| Candidate | Native recording result | Status before final dense checks |
|---|---|---|
| New York 74/p1 | Mean envelope error +0.384 dB; all five layers worsen sustain score | Held |
| New York 49/p2 | Mean envelope error −0.570 dB; partial error −0.022 dB | Held after dense ordinary playback introduces new late/release velocity reversals |
| Belmont 81/p1 | Mean envelope error −14.206 dB and sustain error −15.623 dB; soft stereo balance worsens 1.032 dB | Supported local repair after all four dense profiles; final combined validation pending |
| Belmont 96/p1 | Mean envelope error −1.255 dB; hard sustain error +0.764 dB | Held: ordinary dense playback introduces additional middle/late/release reversals |

Belmont 81 also improves all four available soft/medium repeat takes without
retuning. Their envelope errors change 17.575 → 4.031, 17.364 → 3.961, 20.635 →
2.875 and 21.987 → 3.174 dB. These are repeat-role observations, not a newly
opened sealed test; no hard repeat exists. The soft stereo-balance tradeoff
remains. In New York's ordinary dense grid, note 49 around velocities 103–106
acquires roughly −0.04 to −0.05 dB late steps around −59 dBFS, and late excess
variation increases from zero to 0.795 dB. A modest fit improvement does not
justify ignoring that.

Each candidate was also rendered through the entire fixed Bugatti performance.
Whole-piece RMS changes are under 0.002 dB and matched 1–4 kHz stereo/mono changes
under 0.009 dB. These are local repairs, not evidence of a broad musical voicing
improvement. Fresh-compiler baseline WAVs differ from the delivered versions only
by about 1.7e−7 relative L2; they are compared as fresh paired renders, not claimed
byte-identical to delivery.

A second frozen panel recovered the original Grand 93, Helsinki 103 and
Hamamatsu 78 TRAIN anchors from 20 exact-PCM-verified sources. Grand and
Helsinki retain the original winner. Hamamatsu's p1 objective improves 11.537%,
but the loud layer's middle-window stereo error worsens +0.025 → +4.492 dB with
strong source support. That candidate is held without export. A lower complex
fitting objective is useful evidence, not automatic release approval or proof
that every envelope sounds better.

Belmont 81's completed dense panel contains 3,556 paired cases: notes 78–84, all
127 velocities, ordinary controls, Soft = 1, mono width and Tube microphone. All
samples are finite, reset repeats are exact, and both unchanged neighboring
anchors remain byte-identical. There is no new whole-stereo velocity reversal in
the first 750 ms in any profile. Small channel-only exceptions remain, including
a −0.0125 dB new early left-channel step and a −0.0213 dB new middle
right-channel step with Soft = 1.

The most material tradeoff is neighboring-note balance. At note 83/velocity 93,
onset level drops 1.759 dB in mono and 1.735 dB with Tube. At note 82/velocity
66, middle pitch curvature changes −0.228 → −4.846 dB in mono, at −77.40 dBFS;
Tube changes −0.174 → −4.770 dB at −75.42 dBFS. New late mono/Tube steps reach
about −0.126 dB near note 83/velocity 63, at −80.38/−78.93 dBFS. The
repeat-supported recovery of missing sustain supports this local repair, while
those observations rule out calling it a universal keyboard or mono improvement.

## Reproducible measurement updates

The new fitter option is disabled by default. It retains the original objective,
bounds and search budget, reports both candidates, and only replaces the original
winner when its objective is lower. Default-path and skipped-start contracts are
checked without assuming that independently repeated nonlinear fits return the
same ordering of indistinguishable lanes. The old fitter itself fails that
assumption on the repository's NumPy/SciPy versions; the failed test and diagnosis
are retained, and no solver tolerance was changed.

A conditional generator reproduces both C5 headers byte for byte from immutable
accepted numeric measurements plus hash-pinned TRAIN sources and raw fits. It
independently reconstructs the original residual and the declared partial delta,
fixes the accepted clock before phase smoothing, and checks that all unrelated
numeric domains stay exact. Public numeric snapshots contain no audio or raw-fit
pickle. Stored-number regeneration and source recalibration are separate claims.

The integrated tooling passes 68 focused contracts. Independent review caught
and repaired output aliases that could overwrite an input archive, a metadata
check that ignored its requested file, and an unverified manifest reread during
snapshot creation. Integration review additionally fixes an importer that could
be shadowed by a historical operator directory, portable LF byte writing, and a
source-record loop that polluted the target receipt. Resolved paths and hard
links are checked before publication; snapshot creation rechecks every input
pin and loads the specifically pinned importer. Both original and repaired stored
numbers regenerate without NumPy/SciPy or licensed recordings. Source re-fitting
still requires the original private sources and its pinned analysis environment.
An additional non-ASCII path/attribution test verifies UTF-8 manifests under a
simulated non-UTF-8 default locale. Explicit decoder paths work with an empty
`PATH`, including exact executable identity, probing and decoding.


## Research informing the next work

- A modal piano can retain physically meaningful string parameters and a
  separate excitation/radiation path while running in real time. This supports
  improving the reduced representation rather than assuming that a complete
  finite-difference instrument is the only route forward.
  [Bank, Zambon and Fontana, 2010](https://home.mit.bme.hu/~bank/publist/taslp10.pdf).
- Piano excitation models separate dynamic gain from spectral change and discuss
  loudness/brightness controls. That motivates a controlled timbre-coordinate
  experiment; it does not establish which MIDI mapping fits this uncalibrated
  three-layer library.
  [Bensa et al., Hybrid Resynthesis of Piano Tones, 2004](https://citeseerx.ist.psu.edu/document?doi=7abae085a6b4753ff97553198d3aad1db1004a03&repid=rep1&type=pdf).
- Commuted-piano synthesis explicitly identifies phase cancellation as a problem
  when interpolating excitation tables. Keyra's modal endpoint cancellation is
  analogous, but a sample-table fix is not a drop-in solution for its coherent
  decay modes.
  [Smith, Piano Synthesis](https://www.dsprelated.com/freebooks/pasp/Piano_Synthesis.html).
- Sparse peak selection can undercount weak modes. A 2026 plate-model estimation
  study separates modal-count estimation from parameter refinement. Its relevance
  here is the admission-versus-fitting distinction, not evidence that its learned
  plate method has solved piano calibration.
  [Lu and Reiss, 2026](https://arxiv.org/abs/2608.00667).

The newer learning literature strengthens the case for improving the offline
calibration first. **Piano-SSM** provides actual C++17, whole-keyboard mono runtime
evidence: its largest model reports real-time factor 0.44 at 44.1 kHz on an
i7-12700. That deserves credit, but is not six-piano stereo/host validation; its
repository is noncommercially licensed. **Neural Sample-based Piano Synthesis**
models velocity response from one retained recording per key. It motivates
separate pitch and velocity tests, while remaining a sample-based architecture.
[Piano-SSM paper](https://dafx25.dii.univpm.it/wp-content/uploads/2025/07/DAFx25_paper_57.pdf),
[repository licence](https://github.com/domdal/piano-ssm/blob/main/LICENSE),
[Neural Sample-based Piano paper](https://dafx25.dii.univpm.it/wp-content/uploads/2025/07/DAFx25_paper_32.pdf).

For subsequent experiments, the practical order is: validate the exported sound
with separate magnitude, stereo and envelope diagnostics; improve frequency-family
acquisition with leakage/ambiguity controls; then fit source-grounded velocity
responses separately for each instrument. Differentiable physical modal fitting
shows promising parameter recovery but remains sensitive to initialization.
Stable neural modal coupling is a later option: its published state-supervised
synthetic-string proof does not establish coupling identification from these
microphone recordings. Neither result warrants replacing the current runtime
without causal evidence of a missing nonlinear effect.
[Fast Differentiable Modal Simulation](https://arxiv.org/abs/2505.05940),
[Stable Differentiable Modal Synthesis](https://arxiv.org/abs/2601.10453).

## Review evidence

The private `Downloads/Keyra Belmont Mix Clarity 2026-11-02` listening folder
contains shipping A and two existing-Brightness controls B/C, solo and with the
same authored synthetic bass/drums/pad bed at three relative levels. Piano stems
are matched by one scalar over the full performance before extracting phrases;
the mixed files share one export gain. This is a repeatable context test, not a
claim that a synthetic backing represents every mix. The separate key is intended
to be read after the listening choice. No verdict has been inferred.

Detailed current evidence: `belmont-audit/report.md`,
`velocity/rejected-broad-summary.md`, `velocity/shortarc-exact/report.md`,
`colour-normalization/report.md`, `mono/broad/report.md`,
`mono/candidate-v5/report.md`, and `lattice-field/summary.json`, all beneath the
dated working evidence directory above. Publication and release validation
remain separate steps.
