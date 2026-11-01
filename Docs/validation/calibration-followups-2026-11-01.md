# Calibration follow-ups and runtime diagnosis — 2026-11-01

The calibration and pitch-transport experiments below remain rejected or
bounded diagnostics. The separate soft-pedal candidate passes its recorded
gates but awaits listening; it is not adopted. The
[compact evidence](calibration-followups-2026-11-01.json) retains paired
recording summaries, every tolerance regression, velocity-pilot aggregates,
invariants and hashes of the complete local reports.

These experiments use the accepted 0.4.2 source as their frozen reference.
The independent hard-reset correction is accepted locally as 0.4.3 after the
separate checks below. It does not adopt any of the sound candidates.

## Hard reset after changing piano — accepted locally in 0.4.3

Changing the piano while its body rings starts a 10 ms pickup transition.
Previously, an immediate hard reset cleared the resonators but retained the
previous pickups and unfinished transition. The next strike therefore depended
on the previous piano. For Grand→Upright, waveform error against a fresh engine
was 11.389% of fresh-output RMS over the first 50 ms. This is waveform error,
not a loudness increase.

Reset now snaps the pickups to the current build's target, clears their steps
and cancels the transition. Live build changes keep their existing smoothing.
The permanent public-API regression covers all 30 different-model transitions,
six same-model controls and a mixed build. The old source fails 31 of these
37 cases; the correction passes all 37 with exact fresh-engine stereo output.
The existing completed-transition and live-click tests remain unchanged.

The complete 933-case TRAIN/DEV recording comparison has zero regressions or
metric-availability changes. Of those score rows, 930 are exact; the remaining
three differ by at most 1.78e−15 and have byte-identical 4.6-second audio.
Thirty additional fresh-start playback controls are exact, covering all six
pianos, soft pedal, both velocity paths and mixed/nondefault builds. No new
reference extraction, fitting or sealed-data access occurred.

The universal macOS Release build and C++17 compilation pass. All 12 unit and
two audio tests pass, including callback-allocation checks. The eight-demo CPU
gate passes at real-time factors 0.0301–0.0998 against the unchanged 0.6 budget,
at 48 kHz/256-frame blocks, three repeats on an Apple M1 Max. These are native
development-machine timings, not Reason target-chip measurements. Regenerating
the velocity guard reproduces its numeric header exactly; only source-hash
provenance changes.

Universal VST3, AU, CLAP and standalone bundles build as 0.4.3 without user
plug-in installation. The processor and final rotating parameter-matrix checks
pass. VST3 passes pluginval 1.0.4, strictness 10, seed `0x4b455952`; CLAP passes
17 applicable tests with zero failures, three optional preset-discovery skips
and a 117 ms scan warning against 100 ms. The matrix's final run follows
completed linking; the earlier potentially stale run is retained but not used
as its acceptance evidence. AU/auval, manual DAW workflows and Windows remain
unverified.

Rack 0.4.3d1 now pins the accepted canonical revision `ae731673760f486ab762cd021e3b2b7a4a757bbd`,
with adapter commit `7654ca3f737af0d200c0fa398b9cac00010bb9ce`. Its four native
tests, sanitizer contract, SDK 5 compile/local45/universal45 and archive checks
pass. Protected fresh Recon 14.1d48 build 20466 creates and exports all fourteen
patches, preserving all 9,440 production files and restoring scratch/log state.
Two denied graphics-cache writes are recorded separately from loading/playback
errors. Interactive host GUI, song recall and target-chip CPU remain unverified.
The adapter receipt is `Examples/Keyra/Docs/validation/reset-pickup-2026-11-01.json`;
U45 SHA256 is `4ecbe1205407ebcaccfa678ceccb27ea06b611d594852097dcc39eb29dd878b8`.
No wrapper behavior, patch values or demo audio changed in this sync.

The linked compact receipt retains source, build, test, benchmark and binary
hashes. Full causal and validation evidence is under
`out/realism/reset-body-audit/`. No push, upload or merge is part of this change.

## Retaining quiet observations in truncated recordings

The candidate retains quiet held frames from recordings cut off before the
tone has decayed, preserving the original floor estimator and weighting
formula. Its 27 Kawai training anchors contain 18 affected anchors and 207
flagged partial/layer observations. Unflagged partials remain identical to
the paired refit. Synthetic controls improve, and the original noise floors
are unchanged, but this does not establish an improvement after export and
native playback.

All 933 train/dev recordings and 1,584 normal-playing keyboard cases were
evaluated. Compared with accepted 0.4.2, Kawai has **23 paired note/metric
regressions** beyond the existing tolerances. Against the regenerated paired
baseline it has **21**. An additional apparent sustain regression in the
legacy averages is a coverage change: `n80v2` becomes measurable where it
previously had no sustain score. The [common-support correction](benchmark-common-support-2026-11-01.md)
separates that event; the real regressions still reject the candidate.

For `n80v2`, envelope agreement improves by about 8.56 dB while attack, early
spectrum, noise and rise metrics worsen. Its anomalously loud modeled sustain
is reduced, bringing its required level-match gain closer to the other
recorded layers. That mixed outcome needs a fit-to-runtime stage diagnosis,
not another gain adjustment or a favorable aggregate claim.

Kawai's 78→79 early-level gap at velocity 32 improves from −8.237 to −3.270 dB,
but a +8.210 dB gap remains at 83→84. All 1,320 keyboard waveforms from the
other five pianos are bit-identical. Their recording scores also remain
unchanged apart from four grand metrics differing by at most 1.25e−14.
All keyboard cases retain exact gain-halving behavior and deterministic
repeat checks. The isolated candidate therefore neither solves Kawai's
whole-range consistency nor supplies an all-piano sound improvement.

Reproducibility is a separate limitation. Regenerating the baseline with the
historically recorded package versions does not recreate its shipping header.
Those versions identify the generation environment; the old raw-fit cache
does not pin its NumPy/SciPy/BLAS environment. The bounded native probe finds
material baseline drift at notes 64 and 96, reaching −3.382 dB in one late
window. The paired candidate comparison isolates the observation change,
while actual shipping remains the acceptance baseline. No package search or
development-set tuning was used to select a favorable reconstruction.

Complete fits, synthetic controls, source snapshots, three-way recording
comparisons and keyboard reports remain under
`out/realism/censor-observations/`. The candidate stays out of production.

## Transferring velocity curvature between pianos

The [Steinway reference](../research/bitklavier-house-ortf-2026-11-01.md) enabled
a dense, fixed training pilot at MIDI 36/69/96: 12 permitted Salamander layers
and 16 bitKlavier layers per pitch. Salamander's permanent dev layers remain
excluded. Source pins were frozen before extraction; the reduced measurement
operator reproduces an existing Salamander cache exactly. No dev or sealed
recordings were opened.

The candidate transfers only the other piano's normalized spectral-shape
curvature. It preserves target endpoints exactly and the target-local baseline
level curve within 1.42e−14 dB. Despite those constraints, shape error worsens
in all eight instrument/gap/window groups, including energy-weighted scoring.
It worsens 187 of 276 case-window predictions and 21 of 24 note/group means.
The worst case grows from 1.125 to 4.220 dB shape error, with energy-weighted
error also worsening from 0.583 to 1.970 dB.

No target-specific strength or selective note gate was fitted afterwards.
Target-local log-power interpolation remains the baseline. A predeclared
power-linear control also worsens the primary shape metric in all eight
groups, although some Salamander level/energy-weighted metrics improve; those
tradeoffs remain in the numeric report. Three pitches cannot establish a
universal interpolation law. Complete predictions and exposure masks are
under `out/realism/masked-velocity/`.

## Donor uncertainty for unobserved tails

Masked training tails from Yamaha, Helsinki and Mom's test donor residual
distributions while excluding the complete target instrument. A short local
trend predicts coherent beating poorly. Broader-prefix donor corrections help
some targets but worsen Kawai and New York; a proposed upper quantile fails
on fundamentals even when its aggregate coverage looks adequate.

These quantiles are conditioned on the future still being measurable, and
the available cache windows end by 3.5 seconds. They cannot justify an
automatic clamp or a universal prediction for a genuinely truncated future.
No such rule is adopted. The complete assessment and all predictions remain
under `out/realism/tail-prior/`.

## Yamaha pedal observations: complementary evidence, not a new rate law

A frozen panel reads 24 existing TRAIN feature caches: notes 24/48/69/96,
three source velocity bins, pedal up/down. No source waveform or new model
fit is used. The pairs are separate performances; their early levels differ
by −4.87 to +6.97 dB. Every pair's supported broad-band late/early median is
larger with pedal down, but only 98 of 122 supported band cells have that
sign. At note 48, matched-order late-slope medians reverse sign in two of
three layers. Note 96 has only two to four supported late bands and one
supported late partial per layer.

These temporal contrasts remove a constant level factor, not differences in
strike, beating, release timing or room response. The caches describe struck
orders and broad bands; they do not identify individual sympathetic receivers
or a coupling gain. All six models currently inherit the receiver rate law
from Salamander's pedal-alone recording, a different excitation condition.
Yamaha can add a useful note-driven diagnostic but cannot replace that law
from this panel. The owner's existing pedal-clearance preference is retained.
The full findings and playback-metadata limits are frozen under
`out/realism/yamaha-pedal-diagnostic/`. A separately pinned TRAIN repeatability
intake is the next evidence step; distinct sample regions are not automatically
independent strikes or calibrated equal velocities.

## Fit, export and runtime diagnosis

The following bounded diagnoses retain the accepted DSP and numeric tables.
They identify different errors; combining their changes would obscure their
causes. Better raw fitting alone does not qualify a candidate for the model.

### Stereo compression and the played energy denominator

On fifteen Helsinki TRAIN layers at notes 82/84/86, the existing per-lane SVD
minimizes coefficient error rather than error through the nonorthogonal
runtime basis. A fixed-pole alternating least-squares diagnostic reduces that
objective, but its exported native sound has mixed attack and tail results.
In particular, one optimized basis replaces a slow component with a prompt
component and loses the quiet tail. No additional pole was introduced.

A separate correction changes only the fundamental's energy-gain denominator
to include the actual contact cap, onset floor and discrete smoothing. Its
independent sampled-wave check agrees within 3.19e−6 dB, and all 30 legacy
native controls are bit-identical. At note 86, original-pole ALS mean errors
improve from 2.037→1.706 dB early, 0.602→0.309 dB middle, 1.188→1.019 dB in
the first late window, and 0.936→0.858 dB in the second. Notes 82/84 barely
change. The correction accounts for only 0.28–0.41 dB of the earlier energy
gain; the remaining 2.26–3.96 dB compensates fit residual energy.

Against shipping, this corrected candidate still worsens 26 of 60 isolated
case/window errors; its worst first-late-window regression adds 1.048 dB
absolute error at 86/v51, with every scored frame clearly above the floor.
These are isolated fundamental results, not full-piano recording scores.
No all-piano refit follows. Complete results, unchanged-field controls and
regressions are in `out/realism/runtime-fit-review/runtime-energy/`.

The proposed remedy of fixing the slowest original pole does not protect the
lost note-86 tail: the optimized basis already retains that pole, at about
0.494/s and +2.79 Hz. It drops the **second slowest**, at 0.522190/s and
+2.087026 Hz. The quiet layer has 521 late observations above the existing
floor plus 10 dB, spanning 3.500–6.215 s. Omitting that second component with
the other old-basis coefficients fixed raises relative complex tail error
from 0.46546 to 0.58642. That is conditional model sensitivity, not proof of
a uniquely identified physical pole.

Note 82 already retains its slowest component; note 84 replaces its slowest
while improving native late errors on average. There is no common evidence
for locking exactly one minimum-rate point estimate. A pinned pole can also
receive zero excitation or be coherently cancelled. Any future search needs
a predeclared retention check on the full observed late response across all
15 layers and the complete export/native roundtrip, without coefficient floors
or per-case winners. No new fit ran for this review; source-pinned evidence is
under `out/realism/runtime-fit-review/slow-pole-design/`.

The subsequent frozen design proposes a final-excitation feasibility trial
with published poles and pickups fixed. It constrains each layer's supported
late response relative to shipping, using both coherent residual and power
error; a scalar-only control separates pattern changes from gain changes.
Exact lower-power bounds are nonconvex. The first trial uses a sufficient
baseline-directed affine lower bound, with convex upper-power and residual
bounds. Shipping is feasible by construction on each separately computed mask.
A failure to find improvement in that conservative subset is not proof that
the complete representation cannot improve.

The current all-frame tail scores cannot be relabeled as supported-only:
10,250 of 11,847 late2 frames meet the existing floor criterion. The design
requires exact identity serialization/native controls before fitting and
actual native retention afterward. It holds later SVD, gain compensation and
velocity smoothing out of this representation question; a successful trial
would still need an export-aware production recipe. No fit was run in the
design checkpoint, frozen under
`out/realism/runtime-fit-review/late-retention-design/`.

### A loud-layer regression contaminates quiet body excitation

Tracing Kawai TRAIN note 80 establishes that the quiet-frame candidate's
fundamental correction survives export and native rendering. The new problem
is not simply a correction being lost later: reducing the previously excessive
fundamental exposes an already excessive low-frequency body component.

The body's amplitude-weighted line lets loud layers dominate quiet layers.
For the 206.681 Hz mode, projected levels at layer coordinates 27/69/95/117 are
approximately −91.77/−87.21/−44.79/−54.20 dB, while the exported line gives
−49.68/−48.65/−47.61/−47.31 dB. Shipping and regenerated line slopes are very
close, so this is a pre-existing representation error rather than merely
refit drift. The fixed-basis conditioning is benign; removing the existing
ridge changes the mode's raw amplitude by only 0.04–0.11 dB.

Two bounded alternatives affect only the five exactly reconstructed
150–250 Hz modes. A constrained line cannot retain all four observed layer
levels. Its constraint uses total observed band power as a conditional bound,
not an identified body-only target or statistical confidence bound. Per-layer
projected magnitudes remove the large quiet excess and
improve the v95 body band, but lose another 2.39 dB at v117. Neither is a
complete accepted correction. The unchanged full-engine scorer also reports
mixed rise and early-spectrum results even where soft-layer noise and
envelope errors improve substantially. No dev-derived gain enters fitting.

The loud-layer loss has an upstream cause. In the regenerated-baseline trace,
150–250 Hz over 50–300 ms after contact, all in source units, the v117 recorded
band is −54.925 dB; the independent fixed-pole fit yields −59.246 dB, shared-pickup
compression −61.942 dB, and common phase −61.773 dB. Waveform variance
explained falls from 38.60% to 12.93% to 9.97%. Fundamental leakage is
negligible. Some residual energy near 165 Hz has no corresponding pole;
it is unassigned recorded energy, not a proven missing body resonance that
a gain should fill.

Mode 206's v117 stereo projection alone loses 7.20 dB of coefficient power.
Per-layer scalar complex excitation can preserve the projected endpoints
with the existing state count. Restoring arbitrary independent stereo
coefficients would require an additional complex state per body pole, even
if the resonant frequencies stay the same. Evidence and the explicitly
superseded wider-mode diagnostic remain under
`out/realism/censor-observations/body-trace/`.

A broader bounded survey covers **65 TRAIN layers at 12 anchors**, selecting
each piano's training pitch nearest MIDI 72 and 84, with lower-pitch ties.
Native struck-body power minus recorded total power in 150–250 Hz over
50–300 ms ranges from −8.540 to +2.297 dB; the softest 12 layers range from
−8.540 to +1.073 dB. The Kawai80 quiet excess does not recur at comparable
magnitude in this panel, so it does not support a global body gain repair.

The comparison reverses only known gain and output scale; it does not undo
the output signal path or identify an isolated recorded body stem. Its
quietest complete one-second tail window is a selection-biased observational
proxy, with no noise subtraction or confidence claim. Kawai72/84's softest
recorded bands are only 9.14/6.04 dB above that proxy. Twelve half-gain controls
and six official-renderer controls are exact. No dev/sealed reads or fits ran;
the panel and full measurements remain under `out/realism/body-layer-survey/`.

### Colour normalization reintroduces pitch-boundary level steps

The existing pitch interpolation normalizes coherent four-lane energy over
50–750 ms. A later colour normalizer instead counts each lane independently
to infinity. When the selected phase/pickup pattern changes at an interval's
midpoint, that second calculation can change the whole note's gain despite
unchanged coherent energy before normalization.

The fixed-carrier diagnostic isolates steps as large as +7.008 dB for Kawai,
−6.134 dB for New York and +3.659 dB for Belmont. These are model-coordinate
switches, not claimed audible jumps of that size between actual played keys.
Separate integer-key measurements retain legitimate anchor variation.

A finite-window coherent normalizer removes the isolated gain steps in nine
preselected examples, with exact neutral-colour controls. However, it changes
some existing anchor levels by about 2.2 dB, worsens some actual key gaps and
does not repair phase, stereo, attack or tail discontinuities. Its initial
analytic implementation also costs about five to seven times as much at
note setup. It is not adopted. A second candidate interpolates the existing
anchor gain residual in dB and preserves all 39 native anchor, edge and
neutral-colour controls exactly. It also removes the isolated normalization
step, but still worsens some actual gaps and tails: Kawai 38→39's late step
changes from +0.012 to −4.628 dB. Preserving endpoints does not repair the
underlying phase-pattern switch. Mixed builds and realtime endpoint
preparation remain unresolved. Complete evidence is under
`out/realism/pitch-pattern-continuity/`.

### Smooth whole-pattern pitch transport still distorts tails and stereo

A four-lane stereo interpolation using a real-Hilbert spherical path removes
the sampled midpoint switches in the same nine selected intervals. All 12
disabled-hook and 30 enabled anchor/edge waveform controls match, and sampled
midpoint power/ILD steps fall below 4.86e−7/6.61e−7 dB. However, the one-window
50–750 ms construction is **rejected**: Upright53/layer15 late power exceeds
the louder unchanged endpoint by 9.060 dB and its original value by 10.114 dB.
Its normalization-window ILD changes by +7.503 dB. This occurs with positive
overlap and modest residues, so a near-antipodal guard would not solve it.
These are slot-summed model diagnostics; later windows omit cross-slot
interference, body/noise and output processing.

An existing-output eligibility study checks channel power, total power and ILD
in four windows against the endpoint range expanded only to include baseline.
Of 313 matched partials, 250 have complete native coverage; missing coverage is
not a pass. Even an optimistic allowance for an arbitrary common gain leaves
only 20 possible partials. Belmont retains 2.163% of its normalization power;
every other selected case retains at most 0.00988%. This overestimates usable
coverage because it permits a different hypothetical gain for each partial;
a real note has one shared colour gain. No multiplier or mask was implemented.

The nine difficult intervals and one selected layer per interval do not certify
all velocities, unsampled pitches or the whole keyboard. Endpoint containment
is an artifact guard, not an acoustic law, and weak tails lack independent
noise/uncertainty qualification. Exact zero-channel representation is valid in
the pure diagnostic but unsafe through current mixed-piano metadata; soft-rank
behavior and mixed builds remain outside scope. No broad recording or listening
test followed. The rejection and eligibility limits are frozen under
`out/realism/pitch-pattern-continuity/transport-candidate/` and
`out/realism/pitch-pattern-continuity/transport-eligibility/`.

### Soft-pedal lane transport: validated candidate, pending listening

The soft-pedal multiplier currently follows sorted decay rank. A rate crossing
can therefore abruptly exchange its unchanged −0.28/0/0/+0.08 biases. The
candidate assigns canonical measured-anchor biases and carries them along the
existing paired lanes. It changes no measured coefficients, poles or soft
constants. Six selected crossing tests contract toward continuity; the same
assertion rejects all five legacy grand mutations, while upright is the
negative control. These are numerical continuity checks, not audibility limits.

All **933 frozen TRAIN/DEV default-soft recordings** have zero paired tolerance
regressions and zero availability changes. Three score rows differ by at most
1.78e−15; their full 4.6-second waveforms are bit-identical. The two complete
soft-on keyboard grids each cover **1,584 cases**. All are finite and retain
exact half-gain behavior; each build's first case passes its fresh-engine repeat
check. All 465 measured-anchor
and edge cases match, as do all 264 upright cases; 920 interpolated cases change.

Those changes are not uniformly small: Belmont89/v120 middle power falls
2.398 dB, Kawai35/v120 early power rises 1.518 dB, and NewYork101/v80 early
side fraction falls 0.10147. Some adjacent-key differences grow, including
Belmont86→87/v32 middle magnitude by 1.286 dB. The largest rise changes are
NewYork32/v80 +38.083 ms, Belmont28/v32 +31.938 ms and Kawai25/v80 −28.083 ms.
All three keep the same event onset. New York and Kawai chiefly move the 90%
crossing between peaks; Belmont also changes its early RMS shape materially.
These are sound changes against baseline, not soft-pedal recording errors.

Native engine/headroom, parameter extremes, 300 seeded fuzz iterations and
preset-demo checks pass. The staged regression adds 2,214 anchor/edge state
checks, 2,904 all-key soft-off state checks and 12 short waveform controls.
Eight serial native CPU demos, three repeats each, change median real-time
factor by −4.17% to +3.65%; the candidate maximum is 0.113. This is development
machine evidence, not a host or deadline guarantee. Mixed-string rank pairing
still limits the continuity claim. **Listening remains pending; the candidate
is not adopted.** Complete per-model, gap, edge and window results, excursions,
commands and source hashes are under `out/realism/soft-order-audit/`.

### Noise covariance disagrees with its density calibration

`prepareNoise()` normalizes a sum of band-response powers, while `hiss()`
feeds the same two random signals through every band. The actual response
contains cross-band terms. Native-filter analysis across all six builds and
32/44.1/48/96 kHz finds centre-frequency density deficits up to 3.11 dB for
a flat stationary target. This is distinct from the Kawai low-frequency body
problem; the noise bank starts near 397 Hz.

An isolated candidate gives each active frequency band its own random draws.
All-six-build stationary native tests at 48 kHz, plus grand tests at the other
three rates, agree with the intended independent-band response within 0.443 dB
over two fixed seeds. Synthetic finite-burst tests over 64 fixed seeds match
their predicted window powers within 0.141 dB. These are finite stochastic
diagnostics, not perceptual scores or statistical confidence bounds.

The candidate nevertheless fails the existing loud-chord headroom test:
the upright's ten-note fortissimo peak before the output stage changes from
7.960 to 9.810 dBFS, above the unchanged 9.041 dBFS margin. All other engine
assertions pass, including zero callback allocations; both baseline and
candidate parameter-extremes tests pass. No gain or threshold is adjusted.

A separate polyphony diagnostic shows that the current noise system sums
amplitudes across strikes, giving identical simultaneous bursts +6.021 dB
for two and +12.041 dB for four. Under an explicit independent-strike
assumption, summing powers gives +3.010/+6.021 dB and preserves a single
burst exactly. That second candidate reduces the upright chord peak to
9.183 dBFS but still fails the margin. Moreover, separate left/right power
sums with fixed band coherence do not generally preserve stereo covariance
when simultaneous strikes have different left/right ratios. Correct marginal
powers alone do not close the polyphonic model. A shared filtered carrier
scaled by aggregate power also differs in temporal covariance from separately
filtered strikes whose envelopes are not proportional. Full stereo covariance
factoring can repair the instantaneous matrix; it cannot establish temporal
equivalence by itself. No polyphonic recording claim follows from the synthetic
simultaneous-burst control.

The unchanged baseline also fails the same headroom margin at predeclared
seed 3: 9.576 dBFS for the upright ten-note chord, versus 7.960 dBFS at its
usual seed 1. With noise muted the peak is 8.427 dBFS. Over eight fixed seeds
and 18 unchanged chords, each of the three variants has one failing run,
always that upright chord. This bounded diagnostic is not a failure-rate
estimate, does not select a replacement seed and does not excuse the
candidate's failure.

The independent-band candidate's complete 933-recording evaluation has 19
paired note/role/metric regressions and 179 individual case/metric regressions,
with no metric availability changes. Dev noise-error changes are −0.082 dB
grand, +0.041 upright, −0.174 Kawai, −0.199 Hamburg, −0.031 New York and +0.156
Belmont. All 1,584 keyboard cases are finite and retain exact half-gain
linearity; the repeated first case is identical. Those low-gain checks do not
override the chord failure. Keyboard rise changes include −27 ms at Belmont
45/v32 and +9.417 ms at upright 79/v120; these are descriptive changes, not
errors against recordings.

A 32-render, eight-seed audit of those two keyboard cases reproduces all four
seed-1 controls exactly. The large rise changes come from the 90% threshold
selecting different peaks, not a shifted event or signal onset. Paired rise
changes span −27.000…+26.979 ms for Belmont and −0.583…+9.417 ms for upright;
their medians are −0.031 and +0.031 ms. The 10% crossing changes by at most
0.042 ms, and the first nonzero sample is unchanged. This does not erase the
frozen score differences or establish perceptual equivalence; it identifies
finite-realization sensitivity in those particular rise metrics.

An activation control also finds that interleaving draws from one PRNG across
active bands changes an already-playing band's realization when another band
starts. Distinct persistent per-band streams could preserve deterministic
isolation, but have not been substituted or selected to pass the headroom
test. Neither noise candidate is adopted. Frozen evaluations,
all regressions, controls and headroom evidence live under
`out/realism/noise-covariance/`.
