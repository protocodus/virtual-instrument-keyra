# Pitch-wheel reset A/B

After a reset, a new note should sound as it would on a fresh piano. In 2.24.3, returning the pitch wheel to centre just before a reset could leave the sympathetic strings tuned to the previous bend.

| Recording | Concert Grand at 48 kHz |
| --- | --- |
| A | [2.24.3 after wheel return and reset](../audio/pitch-wheel-reset/before.wav) |
| B | [2.24.4 after the same events](../audio/pitch-wheel-reset/after.wav) |

The pitch wheel rose five semitones. A note sounded for 64 frames, then the wheel returned to centre immediately before reset. A bridge impulse of 0.004 N·s at C♯4 excited the undamped strings. The two seconds in each recording begin at that impulse. Both stereo PCM24 files use the same playback gain of 0.1871666077 full scale per pascal.

A second instrument received the impulse immediately after preparation at concert pitch. In the first 250 ms the RMS difference between A and this control was −33.38 dB relative to the control. B matched it on all 192,000 floating-point channel samples over two seconds. The regression runs in `Keyra.PianoModel` and also checks the previously bent key on a subsequent strike.
