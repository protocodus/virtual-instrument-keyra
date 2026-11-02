# Factory forte response in Keyra 0.4.11

The owner chose B in a piano-only comparison of three chords played at MIDI
velocities 80, 110 and 127 on each of the six factory instruments. B used
Output 0.35 in 0.4.10. A constant gain after the instrument matched its
velocity-80 group to A (Output 0.70) for that piano. A common export gain
then kept both files within playback headroom. This choice and the request
to keep normal piano volume are recorded in the [listening decision](../decisions.md#2026-11-02--ship-b-at-the-usual-playing-level).

## Factory behavior

At Output 0.70, the shared guard now receives half its former input.
Restoring 6.02 dB afterward gives unity gain when protection is inactive.
On the original moderate audition chords this common makeup gives each
piano 0.20–0.57 dB more than the original per-instrument level match. The
median levels of the broader typical-playing sequences differ from the
previous factory levels by at most 0.04 dB.

Undoing the audition export attenuation produces individual peaks as high
as +3.97 dBFS in the level-matched B. On the six clips just 0.035–0.313%
of stereo frames exceed the −1.5 dBFS ceiling. The longest continuous
excursion is 0.81 ms. The release uses a second, short look-ahead stage
to reduce gain around those peaks. Between two block boundaries, the stereo
gain follows a cubic with zero end slope. Each boundary takes the lesser of
the gains permitted by its two adjacent blocks, so every sample in the block
obeys its peak bound. Blocks below the ceiling with equally safe neighbors pass the unprotected
half-drive ×2 signal unchanged.

At 48 kHz the two guard stages contribute 96 and 24 frames of latency. The
native engine reports their sum to its caller. There is one small, fixed
stereo buffer per instrument. The process function allocates no memory.
On the actual audition the stronger group ended within −0.01 to +0.39 dB
of B's restored velocity-127 group on each piano, and 2.19–3.61 dB above
the previous factory equivalent.

## Dynamics and levels

The same 48 kHz performances, touch draws, factory voicings and 300 ms
louder-channel RMS meter were used for every comparison. The original and
independent sets replay five rounds, and the expanded set includes eleven
velocity steps on twelve more voicings. Both mic endpoints are included.

| Chord panel | Pairs | Decreases in 0.4.10 | Decreases in B before final peak protection | Decreases in 0.4.11 | Median increase in 0.4.11 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Original, 110 → 127 | 480 | 104 | 0 | 0 | +1.40 dB |
| Independent, 101 → 121 | 480 | 30 | 1 | 1 | +2.38 dB |
| Expanded, 48–127 | 1,584 | 272 | 32 | 36 | +0.50 dB |

The minimum original-panel increase is +0.0055 dB. Some small increments
remain effectively level. Duration and spectrum can also affect how two
strikes sound at the same meter reading. The release checks protect individual
velocity steps and the absolute upper levels measured from the selected B
reference. Strong chords may read above 0 VU on the Reason scale, where
0 VU corresponds to −12 dBFS RMS. The separate sample peak limit stays
−1.5 dBFS. [Reproduction and regression fixtures](../../Tests/Fixtures/dynamics/README.md).

All 933 held-note recording benchmarks at their frozen Output of 0.07
produced the same WAV bytes as 0.4.10 after compensation for host latency.
Tests against the original B signal at seven sample rates exercise stereo
image, clear intervals, reset, over-ceiling attacks and published delay.
A hot synthesized bass attack can acquire additional harmonics while its
peaks are reduced. A longer recovery improved that stress signal but added
four velocity reversals on real bass chords. Across the actual isolated
fortissimo A0/A1 tests at both mic endpoints, a single Hamburg tube A0
crossed the ceiling, for 0.067% of its first 340 ms. Chords engage the
protection more often.

Five alternating timing rounds on one Mac covered all six pianos in a pedaled
phrase, repeated notes and a dense 162-strike passage. Pooled process CPU
was 0.997× the prior engine (round range 0.982–1.001×). The per-scene medians
were 1.001×, 1.003× and 0.996× respectively.

## Remaining interpolation gaps

New York D♯1 still dips at ordinary velocities 44 → 45, and Hamamatsu G♯3
at 72 → 73. A change to phase interpolation repaired Hamamatsu's onset but
made a release on another note fall 3.36 dB. For New York, a gain curve
fixed the 0.85 dB early dip on one touch and passed an initial 795 native
cases. Denser mixture coverage exposed new reversals, and a separately
optimized curve reversed 25 steps on a different touch. The existing attack
rise is essentially complete by 50 ms on both problem notes. Making it
instantaneous moved the 50–300 ms window by less than 0.00006 dB. These
experiments were held out of the release. [Earlier source and mixture
diagnosis](factory-dynamics-2026-11-02.md).
