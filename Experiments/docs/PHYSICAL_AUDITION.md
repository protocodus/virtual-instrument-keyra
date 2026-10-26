# Experimental physical-kernel audition

This candidate tests nonlinear hammer/string excitation, two persistent
mechanical polarizations, reciprocal sympathetic coupling, all 475 original
soundboard poles and complex loaded-board radiation. It is a separate research
kernel, with aggregate choirs and empirical loss/observation priors. It has not
replaced the reduced live preview and has not established parity with the
original model or acoustic recordings.

The same nine-second passage is exported in three forms, at matched whole-file
RMS and with the same end fade. All dry files have no added room. All room files
use the same preserved procedural room at wet=0.16. The live preview retains its
default body/noise controls, with only internal room bypassed. Native filter and
internal-rate differences remain documented in the manifest.

- [Original full physical model, dry](../Audio/physical-candidate/original-dry.mp3)
- [Experimental physical kernel, dry](../Audio/physical-candidate/physical-dry.mp3)
- [Reduced live preview, dry](../Audio/physical-candidate/reduced-dry.mp3)
- [Original → experimental physical → reduced, dry](../Audio/physical-candidate/original-physical-reduced-dry.mp3)
  (starts at 0 / 9.5 / 19 seconds)
- [Experimental physical kernel, same room](../Audio/physical-candidate/physical-room.mp3)

The candidate retains 4,607 modes in this 48 kHz configuration, including 475
board modes. The original retains 17,778 string modes plus 475 board modes.
Restoring board poles does not recover missing relative unison motion, all
upper partials, the original hammer law/geometry or calibrated radiation.
Channel correlation alone is not a quality score: the observer can produce a
different stereo image without reproducing the recorded instrument.

The render checks finite output, nonlinear-contact residuals and reconstruction
of primary/secondary/board stems from the same complete simulation. These are
numerical checks, not listener approval. The candidate remains slower than
real time in this shared Linux environment; its timing is not SDK/Reason
qualification. Finger/key/action and air/lid/player modules are independently
tested elsewhere; this direct at-string-hammer audition does not include their
complete chain or its authored MIDI-to-finger latency.

Reproduce after building `keyra_physical_render` and the quality comparison:

```sh
python3 tools/compare_physical_candidate.py --render-candidate
```

Omit `--render-candidate` to reuse only hash-verified synthesis outputs. The
[manifest](../Audio/physical-candidate/manifest.json) and
[report](../Validation/physical-candidate-comparison.json) identify commands,
inputs, binaries, raw audio, stems, gains and limitations. No recording fitting
or automatic perceptual decision occurs in these export scripts.
