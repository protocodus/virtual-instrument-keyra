# Experimental contact-driven attack comparison

**This is a listening diagnostic, not a promoted piano model.** The candidate
passes 33/34 original recording guards; hard C8 still fails an early-window
limit. Runtime and plugin defaults are unchanged. No listener preference or
complete click fix has been established.

- [Same room, original then candidate](old-then-modal-room.flac)
- [Dry, original then candidate](old-then-modal-dry.flac)

Both files last 18.5 seconds: **original at 0 s; candidate at 9.5 s**, with a
half-second silent gap. They play the same nine-second synthesized performance,
including its held three-second tail. These clips contain no acoustic reference
recording. The third key event is MIDI48 at about 1.148 s / 10.648 s; the third
melody event is MIDI77 at about 2.160 s / 11.660 s. The user's original note
ordinal remains ambiguous.

The candidate subtracts a short-memory, contact-driven observation of the same
coupled model. It changes no hammer, string, bridge or pedal trajectory. A
separate unity-memory observer reproduces the entire original raw pressure and
all 1,689 physical checkpoints exactly; the original float32 audio matches the
historical control. All 432,000 before/after force-hash pairs match. This checks
the comparison, not how convincing the piano sounds.

Each version uses identical fixed gain, final 150 ms fade and shared safety
factor. The room version uses the same procedural stereo room at wet 0.16.
There is **no independent candidate RMS matching**, limiting or candidate-only
gain. Exports are lossless 48 kHz, stereo, 24-bit FLAC with decoded-PCM checks
and a −2 dBFS four-times-oversampled peak guard. The manifest preserves measured
levels and stereo differences.

This is the historical original-control grand at 48 kHz, with humanization and
mechanical textures off and repetition control bypassed. It isolates the
original attack complaint; it does not qualify the current connected defaults.
The extra complete observer is an expensive offline experiment, with realtime
realization and Reason/Recon validation outstanding.

See [construction and all 34 outcomes](../../docs/TRANSIENT_RADIATION.md),
[frozen numerical evidence](../../tools/experiments/transient_completion/README.md)
and [presentation manifest](manifest.json). The known C8 regression and changes
in early/whole-note stereo remain part of the result. Sustain preservation does
not mean that attack stereo is unchanged.
