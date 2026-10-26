# Real-recording evidence for connected mechanism texture

The new [mechanism corpus](../References/Mechanisms/README.md) provides a bounded
real-recording target for key-release, pedal and string-release behavior. It
adds evidence without changing the original full solver, current mechanism
coefficients, repetition controller or default plugin sound. Eight TRAIN files
are measured and eight disjoint files remain reserved and unopened.

These recordings are Salamander Grand Piano V3 by Alexander Holm, CC BY 3.0,
at the existing pinned source commit. Capture is described as stereo AKG C414
AB above an acoustic Yamaha C5. Individual event strength, room, microphone
spacing, held-key conditions and previous editing are unknown. Playback SFZ
volume/velocity/decay instructions are retained but not applied or treated as
physical measurements.

## Available and unavailable phenomena

| Reference family | What it can constrain | What it cannot identify alone |
|---|---|---|
| Chromatic `rel` files | Recorded key-release texture across low/middle/high keys; useful envelope/spectral/stereo ranges | Finger/keybed/hammer-strike/hammer-return separation, contact force, material or unique source/body decomposition |
| Pedal D/U variants | Distinct recorded down/up textures and broad tail behavior | Calibrated pedal speed/depth, complete continuous half-pedal law, a population of repetition variation or independent instruments |
| `harmS`, `harmL`, `harmV3` | Several source-library release-resonance families | A pure isolated source, exact preceding note duration or complete layered release without the other families and playback context |

The upstream “hammer noise” label must not be renamed to “hammer hit.” README
and control descriptions explicitly call it key-release noise. Both key-release
and string-resonance families inherit `trigger=release`; pedal files use CC64
endpoint triggers and randomized source alternatives. The V3 resonance family
can accompany the velocity-selected S/L family.

## Interpreting the measured shapes

The TRAIN key-release spectra contain substantial low-frequency energy: their
strong early components are around 174–238 Hz. Most 20 Hz–19 kHz power is below
the current free key-release source's nominal 1206/1800/3258 Hz modes. That
comparison excludes the piano body and sympathetic strings. It is evidence to
test the **whole body-coupled release network**, not a direct error score for
the free source or permission to add a large independent bass click.

The current base source nominal free amplitude T60 is about 10.6 ms for key
release and 197 ms for pedal. These are analytic descriptors of authored
three-mode templates. The recordings include shared body/string/air/room
responses and edited support; their broadband slopes and energy-percentile
times are different quantities. They cannot uniquely supply intrinsic source
loss or modal mass. `FullInstrument` additionally scales body-port resistance
and trigger strength, so the template's standalone output is not its prepared
network level.

The two TRAIN pedal directions differ markedly. D1's recorded 90%-energy time
is about 3.57 seconds; U1's is about 0.275 seconds. D1's longer file/support and
unknown capture conditions remain visible. Changes to damper/string state are
part of pedal behavior and may explain part of a difference, but the recording
does not prove that assignment. A source-only fitted oscillator or reverb would
not establish the causal pedal response requested for the instrument.

The key-release files have 21–39 ms detected leading support before the chosen
onset threshold. There is no synchronization marker establishing when the real
key moved. Do not add that amount as instrument input latency. Their common
0.45625-second crop and nonzero late power also caution against treating file
length as an identified decay time.

Some key-release envelopes build for 0.10–0.24 seconds after the detected
threshold. That is an observed recording shape, not a synchronized action-time
measurement or proof of a particular physical excitation sequence. Preserve
the envelope evidence without imposing that delay on MIDI input.

Approximately 33–38% of the two pedal files' early Hann spectral power lies
below 20 Hz. Its identity is unassigned. The full model's existing 24 Hz output
high-pass must be handled consistently in later recording/model comparisons;
do not add a subaudio body mode or gain boost simply to match this raw-file
component. Keep raw acquisition files unchanged and document any analysis-only
filtering separately.

Stereo correlation and channel balance vary by source file. The current direct
mechanism observer is mono while its coupled piano observer is stereo. Fit and
evaluate the combined observation before inferring that each individual
mechanical source needs its own arbitrary stereo delay or pan trajectory.

## Next bounded fitting experiment

Keep the present coefficients as a control and use the intact original-network
stems and source/coupling-off ablations already available in
[MECHANISM_NETWORK.md](MECHANISM_NETWORK.md). Match available recording windows,
report onsets/envelopes/spectra/stereo together and use a clearly declared gain
normalization; raw file level does not identify physical impulse work.

Any candidate should retain positive mechanical mass/loss and reciprocal body
reaction, persistent source/string state, the launch/recovery controller and
the source-work ledger. A small bounded parameter set is preferable to many
unidentified modes. Added modes or directional behavior need observable
training support and full-network checks, rather than fitting every peak as a
unique wood, felt or string mechanism.

Freeze candidate parameters, source, protocol and model predictions before the
first opening of the eight reserved files. Report every regression and keep
those files out of fitting. These are same-piano/same-library tests, not a blind
perceptual panel, a new instrument or proof of Reason realtime readiness.

No candidate fit, default change or runtime waveform embedding is part of this
data-acquisition iteration. The evidence is in
[manifest.json](../References/Mechanisms/manifest.json),
[train_features.json](../References/Mechanisms/train_features.json) and
[analysis-receipt.json](../References/Mechanisms/analysis-receipt.json).
