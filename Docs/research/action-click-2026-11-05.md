# The action's click

5 November 2026, Keyra 0.4.20. A key let go brings its damper's felt down on
the strings and its parts back onto their rails, and the grand's pedal coming
up drops every raised damper at once. The engine plays these knocks on the
body's fitted modes, 25 Hz to 1 kHz. The release takes
hold more above them: a click, the felt and the wood meeting their stops
within a few milliseconds and setting ringing the board's dense upper modes,
which no mode the engine fits resolves. 0.4.20 plays it as noise in the
engine's noise bands.

The measurement is `Tools/fit_action_noise.py`; its protocol is at the head
of the tool and its receipt is
[`action-noise-2026-11-05.json`](action-noise-2026-11-05.json), which
`Source/DSP/MeasuredActionNoise.h` is generated from. It reads the train
takes of each piano's locked split only. No take is loaded or distributed.

## The model

In each noise band k from the first whose lower edge lies at 1 kHz or above
(centres 1.26 to 16 kHz), a knock of the action plays the burst

a_k (e^(−r_k t) − e^(−(r_k + 1/τ) t))

under τ, the action's rise, which the knock's modes build up under: one
stroke of the action drives both (152 ms on the Kakegawa grand, 91 ms on the
upright, 77 ms on the Hamburg grand and 5 ms on the New York grand). Per
recorded pitch and band the table holds a_k² as a density in the take's own
scale, as the knocks' levels are, its decay r_k, and its balance, right over
left. A band the take does not sound is silent.

## What the takes show

Each train release take (and the Kakegawa grand's pedal coming up), from the
knock's onset over its first second: per band the density as the median of
the band's bin powers over ln 2, so that the tones of strings a take holds
count for nothing, less the take's floor; a band clicks where it stands 10 dB
over its floor somewhere. The click against its knock is A-weighted, both as
the engine plays them.

| Piano | Takes | Bands that click | Click under its knock (median) | Decay, per second (median) |
| --- | --- | --- | --- | --- |
| Kakegawa grand | 22 keys, pedal up | all twelve, every pitch | 3.7 to 18.8 dB (9.8); pedal up 0.7 | 5.8 to 33.1 (15.3) |
| Helsinki upright | 28 keys | 1.26 kHz on 13 pitches, 1.6 and 2 kHz on 3 and 2 | 7.8 to 34.6 dB (31.1) | 0.3 to 99.8 (5.4) |
| Hamburg grand | 10 keys | 1.26 kHz up to 6.3 to 10 kHz | 3.6 to 18.9 dB (10.7) | 2.1 to 103.4 (14.1) |
| New York grand | 13 keys | 1.26 kHz up to 3.2 to 5 kHz | 22.3 under to 1.1 over (8.1 under) | 17.5 to 80.3 (37.2) |

The Hamamatsu grand plays none. Its release takes are let go from sounding
notes: over their first 0.3 s the key's partials stand 32 to 62 dB over the
median of their 0.9 to 6 kHz spectrum, and above the modes those partials'
sidelobes and their fall under the damper fill the bands. Measured so, D♯6's
take would click 24 dB over its knock, where the Kakegawa grand's keys click
4 to 19 dB under theirs. The engine plays those strings through its dampers.

The pedal going down has no click of its own to measure: from 1.26 to
12.7 kHz the Kakegawa grand's pedal-down take climbs 20 to 30 dB over its
first 100 ms and then falls only 3 to 21 dB/s, the strings its dampers free
ringing on, which the engine plays as its open strings. Only the Kakegawa
grand has pedal takes.

## In the engine

A release's knock carries its click as one burst of the engine's noise (and
the Kakegawa grand's pedal coming up one more), claimed as a strike's is. Per
band, on each piano between its two recorded pitches the densities mix in dB,
the decays in the log domain and the balances in dB, by where the key lies
between them, as the knock's modes do; a band one pitch leaves silent fades
in power towards it. Between the pianos the bands mix in power by the
action's build, so a build with the Hamamatsu grand in its action plays the
others' clicks at their shares. The click takes the knock's gain: its piano's
release level and tracking at the key's velocity, the fade the longer the key
was held, the mute, and Mechanics, which scales it with every knock. A key
whose damper the sustain pedal or sostenuto holds knocks and clicks nothing;
from F6 up, where there is no damper, the key's return clicks whatever the
pedals do. The burst starts and falls at chunk boundaries, so the host's
blocks do not change it.

The engine's noise is one xorshift source the bursts share. It used to run
only while a burst sounded, so a strike's noise depended on how long earlier
noise had sounded; a click sounds for a second or two after a key-up, and
every later strike then drew other noise. `Keyra.Levels` read Felt Upright's
typical playing 0.11 dB lower for it (−15.53 against 0.4.19's −15.42 VU),
outside the 0.05 dB its approved level allows, all of it the strikes' draws.
The source now runs on the engine's clock while the engine is awake, sounding
or not; asleep it rests as before, so a note from silence draws the same
noise as on 0.4.19. A band's filter still runs only while the band sounds,
so a strike that follows a click starts its noise in those bands from
another filter state: a different draw of the same noise over its first 10
to 15 ms.

`Keyra.ActionClick` checks that a key let go on a recorded pitch plays its
row exactly (each band's level against the others', its balance, its decay
and its rise), that a key between two recorded pitches mixes their rows in
dB, and on the Hamburg grand fades a band one of them leaves silent in power,
that a strike, the pedal going down, a key let go under the pedal and
Mechanics at 0 click nothing, that the Hamamatsu grand knocks without a
click, that the pedal coming up plays its row, and that the host's blocks do
not change the click; `Keyra.MeasuredActionNoise` that the header is the one
its receipt gives and the receipt the current fit's.

## Against the recordings

`Tools/benchmark_action.py` scores the click on every release take of the
locked split, train and dev, and the Kakegawa grand's pedal coming up: each
key struck at velocity 85, held 1.5 s and let go (the pedal held 3 s), at the
default Mechanics and at 0, their difference the action alone; per band from
1.26 kHz its density against the take's, the render set to the take's knock
on the header's modes, where the take stands 6 dB over its floor. Lower is
better. 0.4.18 against 0.4.20, mean |dB| per take
([benchmark](../validation/action-click-benchmark-2026-11-05.md)):

| Piano | Takes | 0.4.18 | 0.4.20 |
| --- | --- | --- | --- |
| Kakegawa grand, fitted (22 keys, pedal up) | 23 | 17.83 | 0.42 |
| Kakegawa grand, other train keys | 59 | 17.94 | 2.46 |
| Kakegawa grand, dev (4 keys, pedal up) | 5 | 20.13 | 3.53 |
| Helsinki upright, fitted | 4 | 17.82 | 0.63 |
| Hamburg grand, fitted | 10 | 25.80 | 0.74 |
| Hamburg grand, dev | 2 | 23.58 | 3.57 |
| New York grand, fitted | 13 | 12.05 | 1.31 |
| New York grand, dev | 5 | 11.12 | 3.21 |

No take scores worse; the least gain on any take is 4.7 dB. The upright's
other 28 takes, and its dev takes, stand nowhere 6 dB over their floors above
1 kHz, and are not scored. The Kakegawa grand's other train keys lie between
the recorded pitches, which the fit never reads, so they score the mixing.

`Tools/benchmark_releases.py`, the shape of each partial's release on the
upright's release takes, 0.4.18 against 0.4.20: train 5.94 to 5.82 dB, dev
7.20 to 7.01 dB. Ten takes score worse, by 0.54 dB at rel70 (train), 0.13 at
rel82, 0.12 at rel84, 0.07 at rel72 (dev) and under 0.03 elsewhere.

`Tools/benchmark_recordings.py` renders one note from silence and never lets
it go. On all five pianos 0.4.20 renders such notes byte for byte as 0.4.19
(40 of 40 compared: eight keys from A0 to G7 at velocities 30 to 127 on
each), and its reports equal 0.4.19's case for case: 843 of 843 (432 on the
Kakegawa grand, 158 on the upright, 127 on the Hamamatsu, 48 on the Hamburg
and 78 on the New York grand)
([upright](../validation/upright-pitch-glide-benchmark-2026-11-04.md); the
other four pianos score as on 0.4.18).

## Against the playing

A phrase of three chords let go after a third of a second, four short treble
notes, two held notes and a four-note chord let go under the pedal, then the
pedal coming up, rendered by 0.4.18 and 0.4.20 at Mechanics 0 and at raw gain
1, the level the recordings show (77% on the knob). The click alone is the
difference of the two differences. Over the 150 ms after each of the nine
key-ups that click (the chord let go under the pedal does not), A-weighted,
it sits under what is still sounding by

| Piano | Raw gain 1 (median) | Default, raw gain 0.175 (median) |
| --- | --- | --- |
| Kakegawa grand | 31 to 45 dB (37); pedal up 25 | 46 to 60 dB (52); pedal up 40 |
| Hamburg grand | 35 to 49 dB (44) | 50 to 64 dB (59) |
| New York grand | 31 to 57 dB (40) | 47 to 72 dB (55) |

At the default Mechanics,
which the owner chose by ear for the knocks (2026-11-01), the click is hard
to hear at all; it is heard where Mechanics is turned up.

## Cost

Callgrind, the whole program rendering each factory demo, GCC 13.3.0
Release, 0.4.19 (commit 2886afc) against 0.4.20:

| Demo | 0.4.19 | 0.4.20 | Change |
| --- | --- | --- | --- |
| 01 Kakegawa Grand | 11.570 G | 11.653 G | +0.72 % |
| 03 Warm Walnut | 8.163 G | 8.219 G | +0.69 % |
| 04 Felt Nocturne | 5.671 G | 5.752 G | +1.42 % |
| 05 Open Strings | 10.674 G | 10.746 G | +0.67 % |
| 06 Helsinki Upright | 10.709 G | 10.725 G | +0.16 % |
| 08 Pop Upright | 11.840 G | 12.039 G | +1.68 % |
| 09 Hamamatsu Grand | 5.008 G | 5.045 G | +0.75 % |
| 10 Three Cities | 8.326 G | 8.384 G | +0.69 % |

Every burst now also carries the click's rise, which costs the Hamamatsu
Grand demo, which clicks nothing, 43 M instructions in the noise's chunk
update. Pop Upright plays the most key-ups; a few of the upright's bands
decay at under 3 per second, so their bursts sound for many seconds.

`Keyra.CpuBudget` passes. In wall-clock time, the two builds' demo
renderers run alternately three times each (each run the median of three
renders), 0.4.20 moves −5.6 to +8.2 % per demo against 0.4.19, inside the up
to 16 % that either build's own runs spread over on this machine; the
instruction counts above are the measure. The heaviest demo in these runs,
Pop Upright, renders at 0.092x realtime (0.4.19: 0.088x).

## Listening

`/mnt/project-files/keyra/ab-2026-11-05-action-click/` holds A (0.4.18) and
B (0.4.20) on the Kakegawa, Hamburg and New York grands at raw gain 1, and
the Kakegawa grand at the default Mechanics, the phrase above, level-matched
on whole-file RMS (every trim 0.0000 dB), with its key. The owner's verdict
goes in `Docs/decisions.md`.

## Known gaps

- One take per recorded pitch, at velocity 85 after 1.5 s held; at other
  velocities and holds the click follows the knock's tracking and fade,
  unmeasured.
- The upright's click is mostly a single band at 1.26 kHz near its floor. Its
  slowest bands decay at the fit's bound of 0.3 per second, which no stop's
  impact makes; they stand only 10 to 15 dB over their floors.
- Only the Kakegawa grand has pedal takes, and the pedal going down has no
  click to measure. The Hamamatsu grand's click is unmeasured.
- A strike after a click starts its upper bands' noise from another filter
  state than it would have.
