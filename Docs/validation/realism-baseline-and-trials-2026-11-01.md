# Recording baseline and first interpolation trials — 1 November 2026

The implementation baseline is `ba3ee990864577464f9cf449b2c335c6788a465b`. Native arm64 Release DSP and C++17 compilation passed; the unchanged unit tier passed 5/5. The six recording suites scored 933 train/dev cases. No sealed cases were opened. Scores below measure recording agreement, not listening preference.

| Piano | Train/dev | Partial error dB | Attack error dB | Envelope error dB | Rise error ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| grand | 276/156 | 5.327 | 4.796 | 2.655 | 3.899 |
| upright | 137/21 | 8.470 | 6.423 | 4.845 | 5.743 |
| kawai | 104/23 | 9.809 | 8.277 | 4.911 | 5.226 |
| hamburg | 40/8 | 7.278 | 6.818 | 4.436 | 3.768 |
| newyork | 61/17 | 9.980 | 8.604 | 3.937 | 8.625 |
| belmont | 81/9 | 6.999 | 6.807 | 4.611 | 20.537 |

## Acoustic references and reproducibility

The unchanged renderer is frozen under `out/realism/baseline/keyra_render`, SHA256 `239dea11fbd9ccd421c569657e4984625116f7cd9f37c69f1186aea921a90f6d`. Tool sources and corpus metadata are frozen under `out/realism/baseline-source/`; each model has its own reference cache. Full report locations and SHA256 values are in `out/realism/baseline-summary.json`. Source-file hashes and native test logs are in the adjacent receipts. These ignored working artifacts retain the full per-case evidence; recordings are not committed.

A reference-cache defect was found before comparisons: different libraries reuse case names, and the old cache key identified only the name and analysis version. The new key includes actual WAV bytes, interpreted MIDI note and both analysis implementations. Atomic publication also prevents a concurrent reader seeing a partly written archive. Two regression tests cover cross-piano ID collisions, same-size/same-timestamp source replacement and pitch changes.

Yamaha C3 now has a pinned, deduplicated corpus and whole-pitch train/dev split; see [its protocol](../research/yamaha-c3-corpus-2026-11-01.md). It supplies additional evidence for shared behavior. Each existing piano retains its own recording benchmark.

## Trial: power fade for unmatched partial orders

An order found at just one adjacent anchor currently fades in amplitude; the trial faded it in power, matching how off-series components are mixed. The trial preserved recorded endpoints, and used the unchanged scorer and the same dev recordings. Level metrics were recomputed over identical case sets.

| Piano | Change in partial error dB | Change in attack error dB | Change in residual-noise error dB |
| --- | ---: | ---: | ---: |
| grand | -0.0000 | +0.0016 | +0.0684 |
| upright | -0.0090 | +0.0268 | +0.2310 |
| kawai | -0.1049 | +0.0105 | +0.0162 |
| hamburg | +0.0389 | +0.1474 | +0.0182 |
| newyork | -0.0975 | +0.0341 | +0.2235 |
| belmont | -0.0000 | +0.0347 | +0.0449 |

Negative changes are better. The small mixed spectral gains do not justify adoption: attack and residual-noise errors worsened in every model. The change was reverted. Its immutable renderer, source snapshot, per-case reports and every numerical regression remain under `out/realism/power-interpolation/`. This is evidence against an unconditional power fade, not evidence that missing partials should always be treated as known silence.

## Trial: borrow interpolation curvature from other pianos

A numerical pilot masked internal training anchors in the published modal tables, interpolated between the remaining endpoints and added the median curvature of other pianos. The correction strength for a target piano was learned only from the other five. This retained target endpoints and avoided directly copying their levels. It improved some sparse-piano power predictions by roughly 0.1–0.16 dB but worsened the grand; decay changes were mixed. These are fitted-parameter predictions, not recording or listening scores. The unconditional correction was not adopted. Full protocol, predictions and per-model results are in `out/realism/curvature-pilot.json`; its source and numeric endpoint export are retained alongside it.

## Mom’s Baby Grand reference

The owner’s `Moms 1974 Baby Grand Decent Sampler 1.5` library is the existing Belmont source. All 90 train/dev recordings were decoded from that exact local `.dslibrary`; source PCM and processed WAV hashes match the pinned corpus. The library is useful for timbre, envelopes, decay and stereo. Its samples were peak normalized, so absolute key/velocity loudness is not an independent acoustic measurement. Existing pinned calibration gains were used; no sealed recordings were decoded to recompute them.

## Trial: guarded velocity interpolation

The current source candidate blends each partial’s four complex excitation lanes together, preserving their relative pattern. It aligns whole-pattern phase, interpolates normalized patterns, then restores endpoint phase and log-linear 50–750 ms power. This avoids treating mutually cancelling fitted lanes as independent amplitudes. Exact recorded-layer endpoints and extrapolation retain the old path. Only complete velocity intervals passing an early-window and three later-window power guard are enabled; unsupported intervals stay unchanged. The generator and its metadata record the scope and numerical limits of this guard.

There are 405 enabled partial/layer intervals across all six models: grand 110, upright 79, Kawai 47, Hamburg 68, New York 57, Belmont 44. Native tests checked 20,583 measured partial/layer endpoints, continuity and bounded normalization. Extra cache storage is 118,912 bytes, with no additional rendering oscillators.

All 933 train/dev recording cases were rerun through the frozen scorer. No per-note metric exceeded the existing regression tolerances. Most recordings sit exactly on measured velocity layers, so this is chiefly a preservation check, not proof of improvement between layers. The largest mean dev movement was Kawai decay error +0.0151 dB/s; its partial error changed +0.0036 dB. Other models’ dev changes were negligible.

An analytic sweep over every integer velocity at all recorded pitches found changes in 3,308 of 16,129 note/velocity cases. This sums coherent lane power within each partial, then adds partial powers, over 50–750 ms; it excludes onset, body, noise and output. Kawai A1 at coordinate 107 recovers 4.769 dB of missing total modal power. The largest total-power changes for the other models are grand +0.109 dB, upright −2.404 dB, Hamburg −0.011 dB, New York +0.482 dB and Belmont +1.605 dB. These signed changes repair both dips and overshoots; they are not a loudness target.

The full renderer also completed all 1,584 A0–C8 cases at MIDI velocities 32/80/120 using normal playing response. Every case remained exactly proportional when gain was halved; repeated first cases were bit-identical. 1,049 baseline/candidate files were bit-identical. This repair does not eliminate the existing pitch-gap defects: the largest Kawai early adjacent jump grows from 7.964 to 8.237 dB, while other models’ largest early jumps are unchanged. Mean adjacent level differences are mixed, so no whole-keyboard consistency victory is claimed. Reports and renderer hashes are retained under `out/realism/velocity-interpolation/` and `out/realism/keyboard/`.

## Trial: measured cross-piano stiffness curvature

Yamaha C3 and Helsinki training observations supplied a robust spline of log inharmonicity. Its curvature was added to each target’s own endpoint interpolation, leaving measured anchors unchanged. The upright’s curve and selection folds excluded Helsinki; correction strength was selected on other pianos’ masked training anchors. Parameter and observed-partial-frequency predictions improved in aggregate, but actual dev renders did not improve consistently.

| Piano | Change in partial error dB | Change in tuning error cents |
| --- | ---: | ---: |
| grand | +0.0839 | +0.0199 |
| upright | +0.0713 | +0.0197 |
| kawai | −0.0704 | −0.0826 |
| hamburg | −0.0062 | +0.5006 |
| newyork | +0.0034 | −0.0788 |
| belmont | +0.0612 | +0.0203 |

Every tolerance-exceeding regression: grand MIDI 27 partial error 6.8374→7.6565 dB (+0.8191); Hamburg MIDI 52 tuning error 0.3644→1.2091 cents (+0.8447). Six selected measured-anchor waveforms were bit-identical. The correction is not adopted, and is not being tuned against these dev results. Full evidence is in `out/realism/stiffness-prior/`; feature-level diagnostics remain under `out/realism/yamaha-c3/`.

## Trial: continuous treatment of unidentified decay rates

The fitter’s 0.003/s lower bound means a lane was not timed by the observation. Interpolating that bound as though it were a measured decay can release cancellation between lanes and create long false tails. A hard carry from the identified endpoint improved all models’ mean decay errors but caused an endpoint discontinuity, so it was rejected.

The continuous candidate uses a quadratic Bézier curve in log rate. If exactly one endpoint is identified, that endpoint also supplies the middle control value. Equivalently, the interpolation coordinate is `t + t*(1-t)*(identified_right-identified_left)`. It has no fitted strength or per-model exception, remains between endpoint rates and converges to both endpoints. Both-identified and both-unidentified lanes retain the old interpolation. Only within-piano pitch interpolation changes; the cross-piano control retains its old rule. This is an explicit assumption about uncertain parameters, not a measured law of piano scaling.

| Piano | Change in dev decay error dB/s | Change in dev partial error dB |
| --- | ---: | ---: |
| grand | −0.0611 | −0.0168 |
| upright | −0.1535 | −0.0591 |
| kawai | −0.1145 | −0.0196 |
| hamburg | −0.5217 | +0.0087 |
| newyork | −0.3578 | −0.0086 |
| belmont | −0.0445 | −0.0226 |

Every tolerance-exceeding regression: New York MIDI 100 tuning error 2.9563→4.1858 cents (+1.2295). Pole frequencies are unchanged, but different modal decay changes the dominant measured frequency. This remains a regression, not an excluded case. Other changes and gains are fully retained in `out/realism/rate-confidence-quadratic/comparison.json`.

The 1,584-case renderer sweep preserves all 381 measured-anchor and 84 edge waveforms exactly and has exact half-gain proportionality. Independent near-endpoint checks agree to 0.0000021 dB at a coordinate distance of 1e-9. Belmont MIDI 83 at MIDI velocity 120 loses 4.916 dB of its excess late tail, and 7.018 dB at velocity 32. Mean adjacent late-level differences improve for four models but rise slightly for grand (+0.0020 dB) and upright (+0.0050 dB). Some gaps worsen: Belmont 83→84 at velocity 80 grows by 2.615 dB because the corrected 83 falls below 84. Faster lane decay can also reduce destructive interference and make a note louder; grand 27 at velocity 32 rises 1.029 dB early. These observations limit the claim: better mean decay agreement does not guarantee smoother every-note envelopes.

The candidate is being combined with the velocity repair for a fresh all-model comparison. No source adoption or complete realism claim follows from these isolated trials alone.

## Measurement diagnosis: a truncated tone mistaken for noise

A train-only investigation separated the raw fit, four-lane projection, smoothing and runtime onset processing at Kawai MIDI 80 and upright 82/84/86. The Kawai layer at coordinate 69 ends before its sustained tone decays into noise. The existing stationary-tail rule assigns the tone itself as the fundamental’s noise floor (−63.435 dB), leaving too little of its envelope eligible for fitting. This is not primarily a smoothing defect: the observed early/middle ratio is +9.764 dB and the reconstructed baseline observation −3.805 dB, while observation-window blur accounts for only about 0.105 dB.

An experimental off-partial threshold changes the Kawai ratio to +8.972 dB with the same four poles and fitting objective. On a common full grid, clear-envelope error falls from 10.484 to 1.807 dB. However, independent review found that the short observation window leaks the sustained tone into those side probes: a noiseless control reproduces nearly the same −99 dB estimate. Colored in-band noise is a decisive counterexample: eight of twelve synthetic seeds pass the trigger while the side observations underestimate actual in-band noise by 32–35 dB. The experiment establishes a causal measurement failure; its replacement is not a validated noise estimator or a general upper bound and is not adopted.

The prospective inventory surveyed 843 train recordings: all 699 train notes from the six model corpora plus the 144 currently decoded Yamaha train selections. The remaining 114 unique Yamaha train note regions were listed as unavailable, not silently decoded. Only Kawai triggered: 18 censored cases at 18 pitches and 207 stationary-tail partials. A general replacement must distinguish missing observations from noise and reject leakage and colored-noise counterexamples. Whole train/dev roles and production analysis/data remain unchanged. Scripts, frozen receipts and synthetic counterexamples are retained under `out/realism/jump-diagnosis/`.

The upright investigation found a separate capacity limit at MIDI 84. For one layer the existing four-pole basis cannot exceed an early/middle ratio of 12.558 dB under its exact envelope and pickups, whereas the recording requires 13.264 dB. Adding poles helps this case but did not solve Kawai’s measurement defect. Neither indiscriminate extra modes nor time-window reweighting is adopted.

## Combined native candidate: 0.4.2

The guarded velocity morph and continuous rate-confidence rule are implemented together. The full unchanged scorer reran all 933 train/dev recordings, and the normal-playing renderer reran all 1,584 keyboard cases. The frozen combined renderer SHA256 is `248bc8b3568d9f2b85bd2ee5cc44bf8206915c52f8f7fe6284e5b0f79e6519a3`; its complete source snapshot and raw reports are under `out/realism/combined-interpolation/`. The earlier velocity-only source was reconstructed and checked against every retained source hash. No sealed recordings were opened.

| Piano | Change in dev decay error dB/s | Change in dev partial error dB | Change in dev envelope error dB |
| --- | ---: | ---: | ---: |
| grand | −0.0612 | −0.0171 | +0.0038 |
| upright | −0.1535 | −0.0591 | +0.0345 |
| kawai | −0.0994 | −0.0156 | +0.0310 |
| hamburg | −0.5217 | +0.0087 | −0.0008 |
| newyork | −0.3578 | −0.0086 | +0.0103 |
| belmont | −0.0445 | −0.0226 | −0.1087 |

Lower errors are better. The only per-note tolerance-exceeding recording regression, across both train and dev, is still New York MIDI 100 tuning error +1.2295 cents (2.9563→4.1858). The compact [machine-readable evidence](interpolation-2026-11-01.json) retains every metric mean, regression and significant improvement, source/report hashes, keyboard summaries and CPU measurements.

On the keyboard sweep, 451 files are bit-identical to baseline; every case remains exactly proportional at half gain, with no missing metric changes. Mean adjacent late-level differences improve for Kawai, Hamburg, New York and Belmont, and grow slightly for grand (+0.0020 dB) and upright (+0.0262 dB). The largest early Kawai gap remains worse by 0.2734 dB. Belmont’s largest middle-window adjacent gap grows 3.7224→3.8671 dB even though its mean middle-window difference falls. This is a measured improvement in selected interpolation failures and average recording agreement, not a guarantee that every neighbouring key is more even.

Native Release checks passed: all 11 unit tests, both audio-tier checks (demo determinism/levels and playing-level bounds), the performance tier and C++17 compilation. Focused tests cover exact recorded endpoints, bounded continuous interpolation, live allocation traps, actual interior-key integration, source freshness and generator bootstrap without an existing mask header. Independent review added mutation checks that fail if pitch correction is disconnected or velocity interpolation loses rate support. The Yamaha importer also passed concurrent-publication regression tests after its temporary files were made unique.

On an Apple M1 Max, the eight curated demos’ median realtime factors range from 0.0297 to 0.0984 against the existing 0.6 budget. Changes against baseline range from −0.33% to +0.66%, within the variation of this development-machine measurement. This is not a Reason or DAW CPU claim and does not expand the demo set to every piano.

The model/data anchors, output scales, contact-time cap and sample-rate rendering loop remain unchanged. The extra fixed working storage is approximately 164 KiB per engine (velocity cache plus rate-support scratch); no new rendering oscillators or callback allocations are introduced. Version 0.4.2 identifies this development candidate. The local Rack 0.4.2d1 now pins canonical commit `60d89f0`; macOS arm64 VST3/CLAP validators and protected Recon playback of all fourteen patches pass. The [host validation record](host-interpolation-2026-11-01.md) distinguishes these completed checks from manual, AU, retail and target-chip acceptance still outstanding. Nothing has been merged or released.

## Continuing iterations

The all-piano interpolation candidate now has native and recording evidence. Full-keyboard consistency still has unresolved attack and pitch-gap outliers. Cross-piano stiffness corrections remain rejected; no unsupported claim is made that Yamaha measurements have already improved every model’s gap prediction.

The next calibration experiment retains quiet held observations from prematurely truncated recordings while preserving the existing noise floors and weights. It must pass synthetic tone/noise controls and affected-anchor training refits before any generated data changes. A separate upright capacity study examines whether existing fast residual components can represent the missing early energy without increasing ordinary partials’ runtime cost. Both remain out-only research.

The opt-in onset-envelope experiment and its native parity tests are preserved under `out/realism/onset-candidate/`; the production fitter remains unchanged. The owner’s previously chosen contact-time cap remains in place. Listening files are under `out/realism/listening/velocity-interpolation/`, with the key separate. The owner chose B for a more even Mom’s Baby Grand velocity progression; the exact scope is recorded in `Docs/decisions.md`. This report does not claim the iterative realism goal is complete.
