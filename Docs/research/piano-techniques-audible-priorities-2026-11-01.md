# Piano techniques ranked by expected audible impact — 1 November 2026

> Historical research baseline: this review inspected `e96ce8a8bf58`. Implementation now starts from `ba3ee9908645`, which adds Belmont and soundboard-fitting fixes. See [the refreshed baseline and trials](../validation/realism-baseline-and-trials-2026-11-01.md).

For Keyra's next sound improvements, prioritize the first 100 ms of each strike, coherent body/stereo radiation, and the evolution of ringing strings. Then transfer reduced pedal and restrike physics from the existing experiments. More detailed hammer material or a new whole-instrument solver is a lower-confidence route to immediate improvement.

This extends the [model and market review](piano-modelling-review-2026-11-01.md). The source baseline remains `e96ce8a8bf58711fbbe283733749070cf2f842ea`. This is additional literature research and comparison of existing evidence, with no new synthesis, fitting, listening trial or host benchmark. Historical experiments refer to different revisions and test sets: compare changes within a study, not absolute scores across studies.

The ranking estimates the remaining audible benefit over the current product for exposed solo-piano playing. It is not a measured percentage, a universal ordering, or a ranking of mathematical sophistication. Pedaled music moves item 4 upward; rapid repetitions move item 5 upward; sparse new piano families make item 3 especially urgent. Expected benefit and implementation effort are separate.

| Rank | Technique | Expected audible benefit | Confidence and cost |
| --- | --- | --- | --- |
| 1 | Joint causal excitation/transient fitting through the complete sound-output path | Very high: less click, better hammer/body connection, convincing soft and hard attacks | Strong problem evidence; candidate benefit unproven. Medium development, low-to-medium runtime addition |
| 2 | Shared-pole, multiple-output body/radiation model with coherent phase and delay | High: body weight and believable stereo that evolve together | Owner feedback and failed spatial fits support priority; physical identification remains uncertain. Medium-to-high development |
| 3 | Confidence-aware modal fitting across pitch, plus multiple components for upper sympathetic strings | High on exposed notes: more natural beating/tails and fewer uneven notes | Strong localized recording errors; no new perceptual result. Mostly offline cost, small selective runtime increase |
| 4 | Register-dependent damper model and reduced reciprocal sympathetic network | High during pedaling: chord bloom, clearer release, realistic residual ringing | Published pedal evidence and useful new Yamaha data; continuous trajectories remain unmeasured. Medium-to-high development |
| 5 | Persistent string state with state-dependent contact and action recovery | High during repetitions: each strike responds to the note already ringing | Physics exists in full research; incremental product benefit needs listening. High integration cost |
| 6 | Targeted bass longitudinal/nonlinear residual model | Medium overall, potentially high for exposed forte bass | Controlled perceptual evidence supports register targeting; actual source can be ambiguous. Medium cost |
| 7 | Further mechanism timing and compact felt memory | Low-to-medium incremental benefit, depending on passage and microphone | Basic mechanism sounds already ship and have owner approval. Detailed felt accuracy has weaker direct audibility evidence |

**1. Fit the strike as a causal event, not another freely cancelling resonator bank.**

The production path already includes measured onset phases, contact-relative knocks, two-stage body/noise decay, 0.1 ms smoothing and an upright contact-time rise cap. A further unrestricted fast body component previously created large opposing contributions and worsened attacks. The useful new variable is a bounded excitation with explicit timing and duration, fitted through the actual renderer while initially holding late decay and mode frequencies fixed. Treat the coherent struck component and the stochastic residual separately, then score their sum.

The full physical experiment gives a particularly clear diagnosis: changing only the pressure observer moved A0's measured 10–90% rise to about 56 ms while leaving the hammer/contact trace unchanged. The old radiation fit began at 50 ms and did not constrain the earliest pressure shape. This motivates jointly fitting 0–5, 5–30, 30–100 ms and later windows, rather than changing hammer hardness to repair an observer artifact. Those windows are proposed diagnostics, not replacements for frozen historical metrics. [Attack diagnosis](../../Experiments/docs/FULL_ATTACK_TIMING.md), [production rejected approaches](../decisions.md).

Recent sines/transient/noise neural synthesis provides a useful decomposition, but its 20-musician study still found a substantial reference gap; the authors identify attack problems without isolating them in an attack-only controlled test. Use the decomposition as an offline fitting idea, not evidence that a neural transient will automatically improve Keyra. [Simionato and Fasciani, 2025](https://www.frontiersin.org/journals/signal-processing/articles/10.3389/frsip.2024.1494864/full).

First test: a few grand/upright bass and treble training notes at several dynamics, then short staccato phrases. Preserve the later spectrum, mono energy and stereo image. Do not improve a single rise-time threshold by moving energy into the wrong part of the attack.

**2. Fit shared mechanical sources and their microphone outputs together.**

A promising representation is a compact state-space or parallel-resonator model with shared poles and distinct complex output weights for ribbon-left, ribbon-right and tube, plus supported relative delays. A shared state represents the source; each microphone observes it differently. This can preserve phase relationships across components better than independently fitting left/right amplitudes or inserting a global stereo delay. High-frequency stochastic body energy may still need a separate, transient-aware covariance model.

The existing fitter already estimates dominant stereo pickups with SVD and aligns velocity-layer phases. What is new is joint three-output fitting across component roles and pitch, and evaluating the noise covariance through the actual decaying-noise process. A prior per-pitch early/late coherence refit did not fix width; finite bursts and the measurement estimator altered the resulting coherence. Another widening table would repeat that mistake. [Current fitter](../../Tools/fit_realtime_modal.py), [coherence investigation](../decisions.md).

This differs from the failed full-model body-only replacement, which used six broad frequency gains and passed none of 34 preservation cases. It also differs from an affine microphone gain/delay field, which worsened omitted-pitch covariance in a conditional correction test; the base renderer had already fitted those training pitches. Retain both string and body contributions until a physically or empirically supported replacement accounts for them. [Body-only study](../../Experiments/docs/BODY_RADIATION.md), [microphone study](../../Experiments/docs/FULL_MIC_FINDINGS.md).

Soundboard research shows that observation position changes radiated spectra even with the same underlying harmonic decay; it does not provide a formal perceptual ranking. The AudioLabs 2023 work also demonstrates direct soundboard-to-microphone measurement on a Yamaha C3. That instrument is not established as the Yamaha C3 in Downloads. [Jenei-Kulcsár and Fiala, 2023](https://www.pp.bme.hu/eecs/article/view/21181), [AudioLabs measurement method](https://audiolabs-erlangen.de/resources/MIR/2023-ISMIR-PianoSynth/).

Use Helsinki's simultaneous microphone recordings first. They support relative observation fitting; they do not uniquely reveal bridge forces or source geometry. A causal filter fitted to acoustic output is still an empirical model unless the physical input is identified. Do not require the sound-pressure observation transfer to be positive-real: passivity belongs at the mechanical force/velocity coupling ports, while radiation filters require appropriate stability and causality.

**3. Improve pole identity and model order where current data demonstrate a failure.**

The fitter is already advanced: joint complex exponentials across velocity, variable projection with a QR amplitude solve and analytic Jacobian, regularization against cancelling lanes, noise/beat-aware weighting, multistart initialization, SVD pickup estimation, velocity smoothing and runtime lane correspondence. A generic proposal to add differentiable fitting would duplicate much of the existing capability. [Joint fitting](../../Tools/piano_analysis.py), [parameter extraction](../../Tools/fit_realtime_modal.py), [interpolation](../../Source/DSP/KeyraEngine.cpp).

Two additions are worth testing. First, infer consistent pole/component identities across adjacent pitches and partial families, with confidence-weighted regularization that retains well-supported irregularities. Second, let evidence determine when additional components are identifiable. Matrix-pencil/ESPRIT-style estimates or ESPIRA can supply alternative initial poles and order diagnostics before the existing nonlinear refinement. They are not a reason to discard the current fitter. Das and Abel demonstrate warped-axis modal estimation on coupled piano strings; ESPIRA reports robust exponential-sum recovery on its numerical cases. Neither establishes an audible Keyra improvement. [Das and Abel, 2022](https://arxiv.org/abs/2202.11192), [Derevianko, Plonka and Petz, 2021/2022](https://arxiv.org/abs/2106.15140).

Apply selective extra components to the upper sympathetic-string bank, which currently lacks the unison beating already present in struck partials. Recordings show 3–10 dB dips after 0.5 s, and some late upper-string energy is substantially under-reproduced. Fit only clearly resolved strings before expanding the bank. Woodhouse explains coupled double-decay mechanisms but explicitly notes the lack of formal psychoacoustic threshold evidence at publication; physical plausibility should not be mistaken for a quantified preference. [Current gaps](../../README.md), [Woodhouse, 2021](https://euphonics.org/wp-content/uploads/2022/03/Double_decays_JASA.pdf).

First tests: one poorly interpolated pitch interval and three or four resolved upper strings. Compare tuning, beat period, early/late decay, mono/stereo and small repeated phrases. Do not score against a training note transposed into the gap as if that were an independent acoustic recording.

**4. Let pedal state change the system's decay and coupling.**

A reduced reciprocal string/bridge network can make open receiver strings load the donor strings; a spatial damper model can apply frequency-dependent loss according to contact location and pedal position. Start with calibrated binary pedal states, then add continuous contact/motion only when observations support it. A global multiplier on all note durations cannot represent the different changes across registers.

Lehtonen and colleagues measured sustain effects on two grands and tested an approximation with six listeners. They found longer mid-register partial decay times and changed beating/residual energy, without the same decay extension in bass and treble. Their efficient sympathetic approximation used 12 string models. That supports testing compact structures, not replacing Keyra's existing richer bank with exactly 12 resonators. [Lehtonen et al., 2007](https://pubmed.ncbi.nlm.nih.gov/17927438/).

Keyra's full research already proves reciprocal interfaces; the coupled-waveguide damper proof uses the hammer location rather than the true damper location. Production already supports continuous pedal and repedaling, but its open-string decay law is shared across piano identities. Yamaha C3's separate pedal-up/down regions supply new evidence for spectral/decay differences. They are different performances, so direct subtraction is not an isolated response to the pedal. Binary endpoint recordings cannot identify lift speed, half-pedal hysteresis or repedal timing. [Coupled-waveguide limits](../../Experiments/docs/COUPLED_WAVEGUIDE.md), [library inventory](piano-modelling-review-2026-11-01.md).

Preserve the owner's preferred short release and 80% full-lift voicing. Those choices intentionally depart from the recordings. Evaluate a physically calibrated regulation as a separate comparison; longer ringing alone is not an improvement.

**5. Transfer persistent contact and restrike behavior without replacing the whole instrument.**

Use a small identified per-key/unison mechanical state that persists between strikes. During contact, hammer compression depends on current string displacement and velocity; after separation, use efficient modal evolution. Retain hammer return and partial-recovery state. This is distinct from the production engine's existing overlapping tails and deliberate random variation.

The full experimental controller already preserves string state, protects active contact and handles incomplete return; its diagnostic admitted six of seven requests, intentionally cancelling one. Those tests establish safe state behavior, not calibrated action timing or a listening preference. Transfer and reduce that implementation rather than reimplementing it from scratch. The four fitted acoustic lanes are not automatically valid physical contact coordinates. [Strike repetition](../../Experiments/docs/STRIKE_REPETITION.md).

An energy-stable contact method is useful here, but faster or more detailed contact is not itself an audible benefit. The existing full-model fast solver is already integrated. A 2024 comparison of explicit and implicit energy-quadratized collision schemes identifies possible spurious/contact-force artifacts as well as efficiency benefits. Compare a candidate against the current dissipative law and its force/energy behavior; do not assume a drop-in equivalence. [Van Walstijn et al., 2024](https://www.sciencedirect.com/science/article/pii/S0022460X23004170).

First test: quiet-after-loud and loud-after-quiet repetitions at multiple intervals on three representative keys. Use current production as A and full physical research as a diagnostic comparator. Real repeated-strike sequences remain necessary for acoustic validation; round-robin isolated notes do not capture prior vibration or action recovery.

**6. Spend nonlinear-string CPU first on the bass.**

A targeted branch can derive low-register longitudinal/phantom energy from transverse motion and feed it through identified radiation, instead of adding unrelated extra oscillators. Bank and Lehtonen's ABX study used fortissimo recordings from two grands and one upright. Longitudinal components were audible up to C5, but A3–C5 effects were subtle; they considered modeling up to roughly A3 sufficient for synthesis. This is a useful starting region, not a universal cutoff. [Bank and Lehtonen, 2010](https://pubmed.ncbi.nlm.nih.gov/20815427/).

Production already includes measured off-series components. The benefit sought is their state/velocity dependence and generalization, not the first introduction of inharmonic detail. The full experiment's passive C8-local resonator at about 4434 Hz remained 87–102 dB below the baseline RMS in its direct output, despite mechanical activity: the correct frequency alone did not solve excitation and radiation. [Local-resonance study](../../Experiments/docs/LOCAL_RESONANCE.md).

Also compare a structural nonlinear residual hypothesis. Moore and colleagues found phantom partial generation in wooden structures as well as strings, with smaller string contributions in their measurements. A strong off-series peak does not uniquely identify a longitudinal string mode. [Moore, Neldner and Rokni, 2018](https://pubmed.ncbi.nlm.nih.gov/30424657/).

First test: a few exposed forte bass notes and left-hand octaves, with source-consistent velocity scaling. Preserve the existing measured extras until the replacement improves both recordings and listening.

**7. Refine connected action cues before detailed felt or action geometry.**

Goebl and colleagues provide unusually direct perceptual evidence: listeners distinguished pressed and struck touches at matched hammer velocity, and removing finger/key noise removed that distinction. This supports correctly timed mechanical cues. It does not imply that louder generic noise or more detailed hammer geometry improves an existing implementation. [Goebl, Bresin and Fujinaga, 2014](https://pubmed.ncbi.nlm.nih.gov/25373983/).

Keyra already has owner-approved moderate mechanism sounds. Further work should address timing, spectral source and dependence on release/return state. Some acoustic action precedes string contact, while ordinary MIDI note-on does not provide that earlier gesture; any inserted delay or inferred touch state needs an explicit latency/input contract. The current note-off API also lacks release velocity.

Stulov's experiments support compact hysteretic/hereditary felt models and show that simplified models can approximate measured dynamics. They do not establish a listening advantage for detailed felt simulation. Try a small memory state only if contact-duration/velocity residuals remain after observer repair. Full flexible shanks, explicit multibody double-escapement geometry and air/lid/player geometry remain lower-confidence development priorities; compact repetition behavior belongs in item 5. [Stulov, 2003](https://www.ioc.ee/~stulov/smac03.pdf), [current action-model coverage](../../Experiments/docs/ACTION_MODEL.md).

**Grand and upright action references: preserve the event sequence with a compact state model.**

The owner supplied a grand-action diagram, a 2.4-second silent grand-action animation, and a labeled upright-action diagram. The animation was inspected as a sequence of frames; these references illustrate mechanism structure, not measured force, timing or material parameters. They reinforce items 4, 5 and 7 without establishing a new audible ranking.

For a grand, the useful sequence is key/jack drive, escapement and free hammer flight, impact, rebound/backcheck, then repetition readiness. A repetition lever permits jack reset after partial key return; the damper can remain clear through that cycle. A conventional upright has different hammer-return and jack-reset regulation. These should be instrument-specific parameters rather than a fixed maximum repetition rate. Upright designs vary: Steingraeber's SFM uses magnets to accelerate jack return and explicitly omits jack springs. [Askenfelt and Jansson's action timing](https://www.speech.kth.se/music/5_lectures/askenflt/timing.html), [Steingraeber SFM](https://www.steingraeber.de/en/innovationen/sfm-upright-piano-action/).

| Reference mechanism | Keyra already has | Useful next distinction |
| --- | --- | --- |
| Hammer escapes, flies, strikes and returns | The separate `physics::Action` experiment models jack disengagement, free hammer flight, nonlinear contact and a passive backcheck | Transfer a reduced, calibrated state model where it changes the sound; production currently has fitted strike excitation, without hammer position/velocity |
| Repetition readiness depends on recovery | `FullInstrument` has a `StrikeController` with partial-recovery and deferred-strike behavior | This is an authored proxy. The separate detailed `Action` re-engages its jack only at complete rest; neither demonstrates a calibrated grand repetition lever or upright reset mechanism |
| Key release and damper landing are separate events | Production supports continuous pedal, repedaling and sostenuto, with smoothed damper motion | Key/pedal flags currently govern damping, without a key-travel liftoff threshold. Separate virtual key motion, damper motion and hammer recovery |
| Action moves even while the pedal holds dampers up | Production has fitted mechanism sounds | Below F6, current key-up sound is suppressed while sustain/sostenuto holds the damper. Distinguish key-return/backcheck cues from damper-contact cues before adding more noise |
| Grand and upright soft pedals move different mechanisms | Production already distinguishes grand una corda and upright half-blow voicing | Refine per-string contact/voicing for grand and travel/energy/reset behavior for upright only if recordings support it; do not present basic soft-pedal differentiation as a new feature |

Code evidence: [experimental action](../../Experiments/src/physics/Action.cpp), [strike controller](../../Experiments/include/keyra/physics/StrikeController.h), [full integration](../../Experiments/src/full_instrument/FullInstrument.cpp), [production damping, soft pedal and note-off](../../Source/DSP/KeyraEngine.cpp). Yamaha confirms the physical distinction: the grand shifts its action laterally, while the upright moves its hammers closer to the strings. [Yamaha mechanism comparison](https://www.yamaha.com/en/musical_instrument_guide/piano/selection/).

The proposed compact state consists of hammer flight/contact/return, strike readiness, inferred key lift/recovery, and damper contact controlled jointly by key, sustain and sostenuto. Emit separate strike, keybed, key-return and damper-contact events. Ordinary note events do not reveal continuous key depth, finger force or partial-release trajectories; those states remain explicit approximations unless a controller supplies them. The experimental `setFingerTarget` interface can accept a kinematic trajectory, but cannot recover one from absent MIDI data. Preserve the requested strike time: starting an entire finger-travel simulation at note-on would introduce extra latency.

First action-specific comparison: quiet-after-loud and loud-after-quiet repeats, short and long release intervals, with and without sustain. Evaluate grand and upright separately. Keep the existing recovery controller as the baseline; no drawing alone justifies spring constants, reset thresholds or a slower response.

**The previous experiments rule out specific shortcuts, not whole technique families.**

| Previous Keyra experiment | Observed result | Consequence for the next candidate |
| --- | --- | --- |
| Full-model additive radiation calibration | A0 rise changed to about 56 ms with unchanged mechanics; earliest 0–50 ms was outside the radiation fit | Constrain transient pressure and coherent cross terms explicitly; isolate observation from contact |
| Contact-driven transient companion network | Early-band error improved 14.963→13.730 dB, but only 33/34 cases passed; hard C8 and stereo remained problems | Keep as diagnostic evidence; avoid another full network and require full-range/mono/stereo checks |
| Six-gain body-only observer | 0/34 preservation passes; sustain drift −8.92 to +12.72 dB | Shared poles and source/output structure are a different experiment from broad EQ |
| Two-branch stereo interpolation | Omitted-pitch covariance 0.875–0.884 versus 0.760 for its old panner, lower being better | Better anchor fits are insufficient; test interpolation and physically plausible source identities |
| Confidence-prior unison-loss fit | Historical envelope error improved 6.366→5.710 dB versus V4, with other regressions and no listening verdict | Retaining priors where parameters are poorly identified is useful; report all tradeoffs |
| Waveguide prototype | C6 fundamental still 8.36 cents wrong in the cited fit | Use modal treble initially; validate phase/dispersion before replacing strings |
| Fixed-Q compact waveguide radiation | Large waveform correction errors remained | Test shared fitted poles or physically positioned wave taps with a modal remainder |
| Modal-cap reduction | 64/24 caps gave 1.58× speed in that study; aggressive 32/16 removed much weak 4–12 kHz C2 attack energy | Mode-count reduction can damage the very detail ranked first |
| Port-velocity “reduction” | SIMD reassociated a sum, retaining all modes; dense p95 time worsened despite better median CPU | This was not physical model-order reduction and did not validate a reduced bridge |

Sources for the comparison: [transients](../../Experiments/docs/TRANSIENT_RADIATION.md), [two-branch stereo](../../Experiments/docs/STEREO_TWO_BRANCH.md), [confidence loss](../../Experiments/docs/FULL_CONFIDENCE_LOSS.md), [waveguide radiation](../../Experiments/docs/WAVEGUIDE_RADIATION.md), [resolution](../../Experiments/docs/RESOLUTION_FINDINGS.md), [port summation](../../Experiments/docs/FULL_PORT_REDUCTION.md). These are frozen numerical outcomes, not a new listening verdict. The old preview with twelve authored body resonances is not today's production engine.

**Runtime techniques should be judged by how much sound they preserve per CPU cost.**

| Technique | Assessment for Keyra |
| --- | --- |
| Passive multiport model reduction / vector fitting | Best new structural reduction to investigate. Fit a compact force-to-velocity bridge/body response with shared poles, preserve reciprocity and enforce passivity; retain a distinct microphone observer. Identify from the full model or controlled measurements, not acoustic spectra alone |
| Hybrid dispersive waveguides and modal treble | Promising enabler already partly explored. Must preserve contact/bridge behavior, unison loss and radiation; cheap delay lines alone do not recover missing body |
| Mixed precision, SIMD and block caching | Much already implemented. Aim for inaudible changes and measurable callback headroom; these do not create a new piano behavior |
| Energy quadratization / non-iterative contact | Useful if contact bursts become a measured bottleneck. A published real-time string result is not an 88-key integrated-piano budget |
| Commuting or caching linear filters | Useful for truly linear, fixed observation stages. Moving nonlinear contact or changing pedal-dependent feedback across them is not an equivalent operation |
| Neural synthesis / learned residual | Prefer offline parameter fitting or a small constrained residual trial. A full neural replacement has uncertain benefit to Keyra's controls, sample-free runtime design and interaction coverage |

The multiport proposal borrows established rational macromodeling, not a demonstrated piano-specific improvement. Stable poles alone do not ensure passive mechanical interconnection; passivity must be checked/enforced, including parameter changes. SINTEF describes that distinction, and Grivet-Talocia/Gustavsen discuss shared poles and preserving reciprocity. Do not impose those mechanical positivity constraints on arbitrary microphone-pressure transfers. [SINTEF passivity](https://www.sintef.no/en/software/vector-fitting/passivity/), [multiport vector fitting](https://onlinelibrary.wiley.com/doi/10.1002/9781119140931.ch8).

Energy-quadratized struck-string research demonstrates real-time feasibility for typical individual strings, with an explicit scalar auxiliary state. It is an implementation option to benchmark, not a proven full-instrument replacement. [Ducceschi, Bilbao and Webb, 2022](https://cris.unibo.it/handle/11585/883682). Piano-SSM's causal neural C++ implementation is also a credible research comparator, but its published speed and spectral scores establish neither Keyra host performance nor a preferred sound. [Piano-SSM, 2025](https://dafx25.dii.univpm.it/wp-content/uploads/2025/09/DAFx25_paper_57.pdf).

**Recommended experiment order differs slightly from the audible-impact ranking.** Start with item 1, then a bounded item-3 fit/halo experiment because it is relatively inexpensive and addresses known errors. In parallel, test item 2 on Helsinki's three simultaneous outputs and characterize Yamaha's pedal endpoints for item 4. Prototype a reduced bridge and persistent restrikes only after a small donor/receiver network has a credible sound and CPU budget. Test bass nonlinear detail after those paths are stable.

Use A as unchanged production; give every candidate the same event stream, seed, controls, sample rate and duration. Match whole-phrase RMS for timbre comparisons, retain mono checks, and use controlled dry presentation before adding the same room. A discrimination result establishes audibility; ask separately which version is preferred. Live playing is needed for touch response. Dynamic-range trials must retain their dynamic contrasts rather than normalize every note separately.

Preserve the owner's chosen velocity color, subtle action level, shorter tails and accepted output/headroom tradeoffs. An optional high-headroom comparison may be perceptually worthwhile because the current guard flattens some hard chord dynamics, but that is a deliberate product choice. Do not silently convert source-recording agreement into authority to reverse it. Likewise, repeated dev scoring is development evidence, not a fresh test; use the existing corpus roles and log any final evaluation opening.

The first deliverable should be a small lettered comparison focused on attack texture, followed by one on treble ringing, with complete existing metric/regression reports. That will turn this research ranking into Keyra-specific audible evidence without committing to an expensive redesign.
