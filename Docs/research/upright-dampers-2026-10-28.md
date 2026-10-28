# What the upright's dampers leave ringing

28 October 2026. The upright's key-release takes from the Helsinki 1967
Tube-Ribbon Edition: the 22 of the train role of
`Tools/corpus/split-helsinki-2026-10-28.json` below F6 (C1 to D6) fitted by
`damper_data` in `Tools/fit_realtime_modal.py`, the four dev takes (D♯2, G♯3,
C5, E6) only scored, by `Tools/benchmark_releases.py`. The upright's header
takes four numbers from them; no take is loaded or distributed.

## The takes

The library plays a release take, one per key group, when a key is let go,
at group volume 0.2 and 3 dB quieter for each second the key was held. Each
holds its note dying under the damper from about the key-up, the way the
grand's release recordings cannot (they fade in over the damper's first tenth
of a second; [release recordings](release-recordings-2026-10-27.md)). Their
first eight partials 20 to 40 ms into the take match the first-take note
recordings of the 71–99 layer best at seven of nine train keys from C1 to E5,
and within 0.6 dB of the best at the other two, most often 1.5 to 2 s after
the strike (scratch comparison against each layer 0.25 to 4 s after its
onset). The fit takes the note under the felt to be one struck at velocity 85,
that layer's middle, and held 1.5 s; holding it 0.75 or 3 s instead moves the
fitted share by under 0.2 dB and the slow rate at middle C between 5.2 and
7.1 dB/s.

Through the felt, a take's partial first falls fast and then, tens of dB
down, only a few dB per second faster than a held note does. The engine's
felt took all of a partial at the felt loss of 24 + 1.4√f + 0.001 f per
second at full contact (about 500 dB/s on a C4; Taguti et al. measured 220 to
470 dB/s on a grand), so its releases went silent where the takes ring on.

## The law

Of a damped partial's power when the felt lands, a share
r = 10^((a + b x) / 10), at most all of it, with x = log2(f / 261.63 Hz),
falls at S = e^(c + d x) per second at full contact besides the partial's own
decay, while the felt takes the rest at the felt loss above. The fit
(`measured::Damper`): a = −12.95 dB, b = −6.92 dB per octave, S = 0.719/s at
middle C (6.2 dB/s), 1.434 times faster each octave up. At middle C the share
is 13 dB under the partial and falls 6.2 dB/s faster than it would held; an
octave up 19.9 dB under at 8.9 dB/s; two up 26.8 dB under at 12.8 dB/s. Below
71.5 Hz, the fundamentals up to C♯2, the felt holds the whole partial only
loosely, at 2 to 3 dB/s: in C1's and D♯1's takes the fundamental falls only
9 to 14 dB/s from 150 to 600 ms after its peak (through a 20 ms window).

The forward model is the engine's: the damper's position d moves toward the
strings with an 18 ms time constant and its contact is ((d − 0.08) / 0.92)^2.5, so a
partial's amplitude falls as e^(−rate·C(t)) with C the time integral of the
contact. Through the benchmark's analysis window (`piano_analysis.window_length`:
six periods of the fundamental, 4 to 250 ms, Blackman-Harris), with the take
silent before its first sample and its floor (its last half second) added in
power, it is compared every 10 ms to 3 s, or half a second before the take
ends, at each partial to the tenth that stands 25 dB over that floor in the
first 60 ms: 118 partials. Under the felt, a partial also decays as its
anchor's lanes do at velocity 85 from 1.5 s. Each take has its own key-up
time and each partial its own level, as the takes carry no level against the
notes, so only the shape of each release is fitted; soft L1 (2 dB) in dB over
the frames 6 dB over the floor. Mean |error| over the train frames: 3.90 dB.

The share and the rate are each linear in octaves; a logistic share fitted
the takes no better (3.690 against 3.689 dB in a scratch fit of the same
takes). The felt loss stays the engine's: the window, six periods long,
blurs a fall of hundreds of dB/s, and with each take's key-up free the takes
do not set it.

## What is left out

Partials within 60 cents of the first three partials of an undamped string,
F6 and up, are not fitted: the take holds that string's sympathy, which the
halo plays. That leaves out every partial above 1.35 kHz, where the law's
share is under −29 dB.

From D♯1 to F♯2 the fitted key-up lands 100 to 260 ms into the take (C1
50 ms), against −5 to 93 ms from A2 up. The engine's dampers all land alike,
so either those takes start earlier before the key-up or the bass dampers
land more slowly; the fit gives each take its own key-up and does not decide.

Where a damped partial lies on an undamped string, the take keeps that string
ringing far louder than the halo plays it. C5's third partial, 1575 Hz, lies
4 cents from the upright's G6 string (1579 Hz). Through a 50 ms window the
take holds that frequency within 8 dB of its level at the take's start for
0.6 s and 11 to 19 dB under it from 1 to 1.5 s, where a render let go at
1.5 s falls 60 dB within 0.2 s of the key-up with the felt taking all of the
partial, and 27 dB with the loosely held share. The halo's levels come from
note recordings, where a string the struck key's own partial covers takes the
level of the pitches around it, so a string driven at a coincidence plays as
one that is not. This is where the never-fitted C5 regresses on the
[release benchmark](../validation/upright-release-benchmark-2026-10-28.md).

## The engine

`setDamper()` in `Source/DSP/KeyraEngine.cpp` gives each damped partial its
share and slow rate. While the felt is on a partial that both shares still
hold, `feltChunk()` sets the next 32 samples' decay to the two shares' power
sum, each falling at its own rate, and the loosely held share becomes more of
what is left; once the other is 60 dB under it, the partial falls at the slow
rate alone. Rendered, a C4 struck at velocity 89 and let go at 1.5 s holds its
fundamental 16.7 dB under the held note's 0.5 to 0.75 s after the key-up,
where the law gives 16.6 dB, and from there falls 6.5 dB/s, the law's 6.2
and the note's own 0.3 (through 0.25 s Hann windows); `Tests/engine_tests.cpp`
checks that it still rings then and keeps falling. The grand has no
`measured::Damper`, so its felt takes all of every partial and it renders bit
for bit as before.
