# Whole-keyboard quality and Belmont clarity

The owner's priority is a common playing-quality standard across all six
pianos, preserving each instrument's character. Recordings now serve as sanity
checks rather than targets for making every piano resemble one recording.

## Current consolidation baseline

The consolidation baseline freezes main `69b87ce` and the accepted 0.4.6
Belmont C sound. Its DSP SHA-256 is
`d584ab20776cc4b3994dcdf07e27f561b5e4e60eb6ff02661990f35dc5a6becb`.
`Tools/quality_audit.py` and `Tools/quality_probe.cpp` provide a reproducible
public-engine audit, including source/observer hashes and resumable receipts.
Independent synthetic-signal tests verify stereo power, cross-power, Hann
spectra and Parseval normalization against NumPy, as well as coverage,
unavailable measurements and rejection of incomplete or mismatched runs.

The completed baseline includes 67,056 two-second strikes (six models,
88 keys, all 127 velocities), 2,586 supplementary scenes and 324 separate
Brightness/quality interaction scenes. The main grid measures onset,
50–300 ms, 300–750 ms, 750–1,500 ms and release through two seconds. Additional
panels cover 16-second tails, three qualities, rates, MIDI channels, live
controls, interacting control corners and all 1,296 categorical four-part
builds at one common note. All declared finite-output, ceiling, coverage,
nonzero-primary-note, selected-repeat and zero-gain contracts pass.

This is exhaustive only over the declared default-control integer key/velocity
grid at 48 kHz. It uses the same normal first strike draw after reset, not
independent randomized seeds. The other panels sample rates, controls, mixes
and histories; passing them does not prove absence of every audible artifact.
Raw window powers and absolute levels accompany relative diagnostics so a
very quiet tail or frequency band is not mistaken for a loud defect.

The main remaining findings are pitch-dependent phase/pickup changes,
different soft-to-loud response across registers, and reduced-quality partials
that cannot return after Brightness increases. For example, the soft upper
registers differ much more than the loud ones: octave/register median spreads
reach roughly 13–19 dB at velocity 32. Removing the extra velocity colour
changes those soft treble levels by at most 0.067 dB in a separate causal
panel. The response mapping, rather than a global colour adjustment, therefore
needs calibration. This does not prescribe identical spectra for all pianos.

The frozen baseline receipt is
`out/consolidation-20261101/quality/baseline-final-receipt.json`
(SHA-256 `fb89d5264da85cf469c3afb5217526a44fbd7d08d0468f4374bf20a78f82e017`).
Its component receipts, complete numeric observations and plots are retained
beside it. They predate the live-control fixes described below.

## Earlier coverage and limits

The unchanged 0.4.5 native engine rendered **67,056 isolated strikes**: six
pianos, every MIDI key 21–108 and every velocity 1–127. Every strike uses the
normal playing response and the same first touch draw after a hard reset.
The first 300 ms is measured at every velocity. Thirteen velocities per key
continue through a 1.5-second hold and 0.5-second release. Output latency is
removed before measurement. Controls are Full quality, 48 kHz, gain 0.07,
brightness 0.5, resonance 0.25, Mechanics 0.175, width 0.75, Mic/soft/pedals/mute 0.

All strikes are finite and non-silent in the first 300 ms. This does **not**
certify absence of audible artifacts, every possible controller history, or
all decay windows at all velocities. Adjacent level changes are diagnostic
flags; normal piano irregularity is not automatically a defect.

A separate structural sweep covered the same 67,056 setups with no invalid
states or unstable poles. The action panel adds 48 paired scenes across all
six models, four registers and two velocities: short/long releases, sustain
release and repedalling, and repeated strikes. Its 96 renders were finite.

## Findings that remain actionable

The pitch interpolation still switches the nearest phase/pickup pattern at
some anchor midpoints. Kawai MIDI 79, velocity 18 is a concrete example:
its first 50–300 ms stereo level is 8.663 dB below the mean of its neighbouring
keys. A fixed-carrier modal probe crossing the actual midpoint changes the
fundamental's early power by 6.619 dB while redistributing energy into later
windows. This is a pattern-transfer discontinuity, not excess Mechanics or
an unstable decay. The four-lane interpolation has not been replaced; previous
single-window smoothing trials produced other tail regressions.

Selected largest successive-velocity decreases in the 50–300 ms window:

| Piano | Key | Velocity transition | Level change |
| --- | ---: | ---: | ---: |
| Kakegawa | 34 | 56 → 57 | −0.588 dB |
| Helsinki | 25 | 57 → 58 | −0.269 dB |
| Hamamatsu | 56 | 72 → 73 | −0.541 dB |
| Hamburg | 99 | 125 → 126 | −0.193 dB |
| New York | 27 | 44 → 45 | −0.850 dB |
| Belmont, before C | 63 | 63 → 64 | −0.163 dB |

These are deterministic finite-window energy changes, not estimates of
perceived loudness. New York and Kawai merit targeted interpolation work;
one global equalizer or gain curve cannot repair the underlying envelopes.

Hamburg's reported Moonlight attack remains with Mechanics muted. The explicit
control's causal contribution is 52.37 dB below the remaining theme in RMS,
comparable to Kakegawa and Helsinki. In onset windows, modal strings dominate;
the coherent body group is the largest secondary transient. Reducing the
action constant would therefore leave most of that attack intact.

A distinct release imbalance appears in Hamburg's quiet high notes: at C7,
velocity 32, the short-release contribution is 22.15 dB below the initial
note, versus 49.01 dB at velocity 112. Its inherited release mapping makes the
absolute release amplitude nearly independent of strike velocity. Note-on
velocity alone does not specify key-return speed, so no new velocity law was
invented from this measurement.

## Accepted Belmont change

The owner chose C: remove only Belmont's additional velocity colour, preserving
the measured layer timbre. All 20 control renders for the other five pianos
remain byte-identical; four Belmont controls exactly match the audition's
neutral-colour renderer. Mixed builds change by their Belmont hammer share.

The adopted model was rendered across all 11,176 key/velocity combinations
with the same protocol. No invalid samples occurred. In the 50–300 ms window,
its worst successive-velocity decrease improves from −0.163 to −0.027 dB;
no decreases exceed 0.1 dB in either of the first two measured windows.
This choice does not repair the independent pitch-envelope boundaries.

## Tube output calibration

Removing Belmont's extra colour changed its loud tube-mic chord reading from
the previously accepted region to +1.036856902 VU. Its typical tube reading
was −9.133752024 VU. Reducing the existing pre-guard tube scale to the exact
−9.5 VU typical boundary left the loud chord at +1.0272 VU: compression largely
cancelled that attenuation. This candidate was rejected.

The existing typical lower limit (−9.5 VU) and owner-approved Belmont tube
chord upper limit (+0.7 VU) allow a **post-guard** attenuation greater than
0.336856902 dB and no greater than 0.366247976 dB. Version 0.4.6 uses the
interval midpoint, **0.351552439 dB**. This is a measured monitoring-level
calibration, not a string/body coefficient or an acoustic fit. Neither test
limit was relaxed.

The full-tube readings become −9.485304275 VU typical and +0.685304650 VU for
the loudest chord; strong-to-hard velocity growth remains +0.927416593 dB.
The sample peak becomes −1.85155 dBFS. The default stereo-pair sound is exactly
unchanged, including the accepted C audition and the Bugatti Step renders.

At intermediate Mic settings the calibration scales the complete blended
output, according to Mic and the Belmont hammer share; it does not claim to
isolate a tube component after nonlinear processing. Hammer-share changes
smooth over the existing 12 ms time constant, and a fixed gain FIFO follows
the shared guard's exact look-ahead. No latency, control, automation identifier,
shared portfolio output-stage code, or allocation in callbacks was added.
Static other-piano/Mic0 paths retain exact output; a live transition away from
Belmont intentionally fades the prior calibration.

The focused native regression covers 55 static controls at 44.1, 48 and 192 kHz,
an independent delayed-gain oracle at two block partitions, reset, idle control
changes, CC120, prepare, and allocation checks. It retains the unchanged guard's
existing one-ULP sample-ceiling roundoff, and separately requires that no
candidate sample exceed its untrimmed control. Existing body-glide partition
roundoff is measured against the unchanged control rather than attributed to
the new gain path.

## Consolidation: live-control continuity

The subsequent consolidation starts from main `69b87ce` (unchanged 0.4.6
DSP). A frozen same-history native probe found that moving Resonance changed
the receiver's output gain immediately, and moving Brightness changed every
held partial's gain at the next 32-frame boundary. Gain, Width and Mic already
used a 12 ms glide. The discontinuities appeared across all six models in
single-note and chord scenes, both on and between chunk boundaries.

Resonance now uses the same 12 ms per-sample one-pole convention. Brightness
sets each held partial's amplitude target at the existing boundary, then
glides that amplitude every sample while retaining its stereo pickup. The
stable rendering path is unchanged. Both trajectories remain between their
old and new gains; neither changes oscillator poles or output latency. Silent
Resonance changes start at the requested value, and reset/voice reuse discard
old glide state.

The independent regression covers all six models at 44.1, 48 and 192 kHz,
closed-form state trajectories, an audio reference forced through the stable
instantaneous-gain path, interrupted/reversed automation, chunk partitions,
settling, reset/reuse and callback allocation. Both deliberate mutations that
disconnect a glide from the audible output fail the same audio oracle.
All 162 static endpoint renders match the frozen baseline byte-for-byte.
Across 24 same-history witnesses per control at 48 kHz, the first changed
sample's difference is reduced by 55.216 dB for Resonance and
55.211–55.234 dB for Brightness. This is a first-step measurement, not a claim
that every possible automation artifact is reduced by that amount.

The initial moving-gain loop cost 2.46–2.75 times the baseline's CPU during
continuous automation. Keeping its state local and separating rising from
settled partial loops reduces that to 1.59–1.71 times while preserving the
independent audio oracle exactly. With 16 held notes, Full quality, 48 kHz and
128-frame blocks, the optimized moving cases use 12.2–18.6% of one CPU deadline
on average; static cases remain within 1.8% of baseline cost. Three paired
rounds per model/mode record zero CPU or wall deadline exceedances. The native
instance grows by 262,160 bytes. These are bounded native measurements under
concurrent audit load, not Rack timing or a maximum-polyphony/rate guarantee.

The initial registered unit/audio tiers passed 17/17 checks. Quality-mode
repair, cross-model calibration and native/Rack performance remain separate
consolidation gates. The diagnostic dual-template pitch crossfade
was rejected after 3,168 cases per path: it removes phase switches but worsens
early note-to-note level curvature in all six models. It is not in production.

The next change applies the same 12 ms one-pole to the hammers' tube gain.
Soundboard changes rotate each live noise band's stereo mixing direction over
12 ms, preserving unit power instead of independently fading its components.
An interrupted rotation starts from the current direction; silent/reset or
inactive bands snap to the target. Filter memories, burst amplitudes and RNG
state are retained. No per-sample trigonometry or callback allocation is added.

The new build-control regression covers all six models at 44.1, 48 and 192 kHz,
independent closed-form/angle trajectories, audible-path mutations, partitions,
reset, silence and interrupted automation. All 108 static pure/mixed/Mic
renders match the preceding frozen source exactly. In the original causal
scenes, first-step differences fall by about 55.2 dB for tube gain and
52.5–56.5 dB for noise coherence. These measurements isolate the respective
control changes; they are not whole-note noise-reduction claims. The additional
state costs 688 bytes per instance, bringing the total increase over the
0.4.6 baseline to 262,848 bytes.

The combined source (`94891ed…`) passes all 20 registered checks, including
the native CPU budget (179.12 seconds total). A separate paired timing panel
uses the same 16-note/48 kHz/128-frame workload described above and adds
continuous hammer/soundboard changes at Mic 1. Static mean CPU is within 3.7%
of baseline; build automation is within 2.5%. Brightness/Resonance automation
costs 1.68–1.81 times baseline and averages 14.2–21.9% of a block deadline.
Across the 54 candidate runs there are zero thread-CPU deadline exceedances
and four wall-time exceedances under concurrent work. Both timings are kept;
this panel is not evidence of zero wall overruns or Rack performance. It does
not repeatedly retrigger noise during measurement. The full timing rows and
source/binary hashes are in `live-controls/performance-final-summary.json`.

Evidence: `out/consolidation-20261101/interaction-audit/`,
`out/consolidation-20261101/live-controls/` and
`out/consolidation-20261101/pitch-candidate/`.

## Consolidation: retain partials needed by Brightness

Reduced quality previously deleted partials using only the Brightness value
at the strike. Raising Brightness later could not recover them. In a native
Helsinki C4/velocity-100 Light case, a supported band near 6.35 kHz lost
68.81 dB relative to Full after brightening; a Hamamatsu C4/velocity-40
Balanced case lost 34.87 dB near 2 kHz. Absolute levels and the complete
spectral panel are retained beside these relative diagnostics.

The selected change retains a partial when either existing peak/held-energy
criterion can include it anywhere in Brightness 0–1. Log ratios are affine
in Brightness, so intersecting their linear inequalities covers the complete
interval. Merely combining masks at the two endpoints would miss partials
that qualify only in the middle. A few float epsilon units cover gain
representation roundoff; this allowance changes no mask in the 60-strike
analytic test panel. It is not a new acoustic threshold.

The measured losses above become effectively zero with the current smooth
Brightness path. All 180 Full static/interrupted/reversed histories match
the frozen preceding source byte-for-byte; 1,080 comparison renders are
finite. Independent breakpoint and dense float-tint oracles, an interior-only
fixture, a deliberately restored legacy implementation, allocation and block
partition checks verify the selected mechanism. Quality still applies to
future strikes, with no new live Quality switching behavior.

Alternating-order timing retains 9.27% Balanced and 14.98% Light callback CPU
savings versus Full in the declared panel; it costs 11.06%/15.29% more than
the former reduced modes. Persistent instance/voice/partial storage is
unchanged, with 1 KiB more temporary strike storage and no heap allocation.
The largest median 16-note strike is 0.850 ms in this native panel. Full CPU
differs by 0.74% between equivalent binaries. Concurrent work remains a timing
limitation; these are not Rack host measurements.

Whole-three-second supported-band errors in the measured dark-to-bright
panel remain 0.061 dB Balanced and 0.923 dB Light. These are observations,
not a guarantee for every band or instant: a very quiet late band can have a
large relative error (one Light example is −16.96 dB against a Full band at
−108.51 dBFS, gain 0.07). The header now states the proxy's scope explicitly.
The more complex dormant-state alternative is retained as an unselected
experiment; it recovered the same witnesses with less CPU saving.

Evidence: `out/consolidation-20261101/quality/pruning-recovery/` and
`out/consolidation-20261101/quality/pruning-integration/`.

## Consolidation: quiet-strike release balance

The inherited sampler ratios made several pianos' key-return amplitudes
nearly independent of strike velocity. The selected performance policy caps
a quiet strike's return against the same model's nominal MIDI-80 return,
scaled by the requested strike level. It only attenuates below that reference;
at or above it the existing balance remains unchanged. This is a product
balance rule, not a claim that note-on velocity measures key-return speed.

Let `d` include the existing touch variation and half-blow hammer reduction,
`d80` be the nominal zero-draw MIDI-80 reference, and `r` the existing
release/note tracking ratio. The captured cap in dB is
`min(0, d - d80 + 20 log10(r80/r))` for `d < d80`, otherwise zero.
It is stored per model/key at the latest strike, so later action-build changes
and overlapping presses use the correct strike history. Held-time decay,
damper/pedal eligibility and channel ownership retain their existing rules.
Raw native-layer measurement captures a zero cap and remains unaffected by
later changes to that diagnostic mode.

Key-landing sounds, pedal-only events and the Mechanics default are unchanged.
If response calibration subsequently adds a strike gain, the cap helper also
accepts the reference-minus-actual correction; the release must apply the
corresponding stored actual correction. This prevents a quiet-note boost from
defeating the intended relative balance. That calibration is still experimental.

The causal prototype covers 426 histories across all six models, four
registers, six velocities, two hold durations, action changes, soft pedal,
repeated presses, channels, sustain/sostenuto and steady diagnostic seeds.
All pre-release prefixes and all release-suppressed candidate/control renders
are exact. No callback allocations, nonfinite samples or guard activity occur
at the declared gain 0.07. For key 100/velocity 8 after a short hold, Hamburg's
release contribution falls from −21.60 to −37.25 dB relative to the played
note; New York's falls from −17.19 to −32.85 dB. This is a signed full-engine
causal difference, not an independently recorded noise stem.

The focused regression adds an independent gain-bound calculation, three
sample rates, partition checks, stored-history ownership and an audible-path
mutation. A coherent total waveform can increase slightly when one component
is attenuated: the prototype's largest full post-release increase is 0.528 dB
in a Kawai soft-pedal tail at approximately −117 dBFS. The component cap and
the finite native panel do not promise that every total sample decreases.

Evidence: `out/consolidation-20261101/interaction-audit/release-cap-prototype/`.

The integrated retention/release source (`a734d0fe…`) passes all 22 registered
checks, including the existing native CPU budget, in 223.66 seconds. Its
velocity-interpolation generated data are unchanged; provenance now identifies
the new source. The source changes above are accepted consolidation milestones.
Cross-piano response calibration and phase/interpolation experiments remain
separate and are not certified by this test result.

## Earlier reproduction records

Local working evidence is retained under:

- `out/realism/whole-keyboard-quality-20261101/`: public-engine sweep source,
  protocol, all numeric rows, per-model receipts, summary, and adopted Belmont
  comparison. An end-of-run source-tree equality assertion caught the authorized
  Belmont edit while the final baseline jobs ran. The statically linked baseline
  executable retained its frozen hash throughout; the amendment records this
  explicitly. Candidate data use a separate executable and filenames.
- `out/realism/full-range-structure-20261101/`: structural sweep and Kawai 79
  causal midpoint probe.
- `out/realism/six-piano-mechanics-balance-20261101/`: Moonlight ablation,
  component closure and action panel.
- `out/realism/belmont-colour-adoption-046/`: exact other-piano and audition
  parity, plus adopted structural sweep.

The complete Bugatti Step comparison uses the supplied modern score's full
154-bar form, including both repeat endings and D.S./coda, independently
checked against the 1931 edition. All six use the same 2,819 attacks and
152.256-second performance. Listening copies receive one whole-file RMS trim
each, with no equalization or compression; raw common-gain renders are retained.
The source score, MIDI, generator, edition differences and receipts remain in
the dated Downloads delivery rather than the public repository.
