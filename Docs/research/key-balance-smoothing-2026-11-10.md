# Each key's level and balance at its neighbours'

10 November 2026, Keyra 0.4.32. The libraries record a piano one pitch at a
time, each take with the microphones' image of where its strings lay and with
its own gain, and the engine played each recorded pitch as recorded, the
keys between them between their neighbours. Struck in turn, the Hamamatsu
grand's balance swung by 10 to 13 dB from one key to the next between E4 and
C6, the upright's by up to 10 dB between A♯3 and C6, and at velocity 40 the
Hamamatsu's level stood up to 8 dB off its neighbours'. No piano's strings
lie so. The owner chose to smooth the recordings' own jumps even where that
departs from them: each key's stereo balance and loudness pulled toward its
neighbours' median at every velocity, its tone and decay kept as recorded.
Nothing is fitted.

## What the keyboard shows

`Tools/survey_keyboard.py` strikes every key alone at velocities 40, 80 and
120 and measures its level and balance over 50 to 750 ms, its brightness,
decay and rise (the protocol is at the head of the tool). A key's jump is
its value less the median of its up to six neighbours within three keys; the
table gives the jumps' rms and the largest, in dB.

| piano | velocity | level, 0.4.31 | level, 0.4.32 | balance, 0.4.31 | balance, 0.4.32 |
|---|---:|---:|---:|---:|---:|
| Kakegawa grand | 40 | 0.54 / 2.3 | 0.34 / 1.3 | 1.15 / 5.2 | 0.43 / 1.7 |
| | 80 | 0.45 / 2.2 | 0.15 / 0.6 | 0.96 / 4.2 | 0.24 / 1.1 |
| | 120 | 0.37 / 1.6 | 0.17 / 0.8 | 0.79 / 2.4 | 0.49 / 2.3 |
| upright | 40 | 1.12 / 3.8 | 0.53 / 2.0 | 2.12 / 8.8 | 1.10 / 5.0 |
| | 80 | 0.79 / 2.7 | 0.22 / 0.8 | 2.22 / 10.1 | 0.71 / 3.8 |
| | 120 | 0.87 / 4.0 | 0.31 / 0.9 | 2.02 / 7.8 | 0.68 / 3.5 |
| Hamamatsu grand | 40 | 2.55 / 8.3 | 1.08 / 5.2 | 3.37 / 13.5 | 0.89 / 6.0 |
| | 80 | 0.97 / 3.0 | 0.66 / 3.3 | 3.22 / 11.9 | 0.79 / 5.7 |
| | 120 | 1.43 / 6.0 | 0.79 / 5.8 | 2.64 / 10.3 | 0.78 / 5.0 |
| Hamburg grand | 40 | 0.51 / 2.6 | 0.30 / 1.2 | 0.42 / 2.2 | 0.23 / 1.0 |
| | 80 | 0.47 / 2.4 | 0.26 / 0.9 | 0.38 / 1.3 | 0.16 / 0.6 |
| | 120 | 0.41 / 2.7 | 0.34 / 2.3 | 0.31 / 1.0 | 0.16 / 0.6 |
| New York grand | 40 | 0.62 / 3.4 | 0.40 / 3.2 | 0.95 / 7.0 | 0.26 / 1.4 |
| | 80 | 0.39 / 1.7 | 0.33 / 2.3 | 1.10 / 8.7 | 0.72 / 6.5 |
| | 120 | 0.59 / 2.5 | 0.40 / 2.0 | 0.68 / 3.2 | 0.20 / 1.0 |

Brightness, decay and rise move by at most 0.04 octaves, 0.02 and 0.04 in
rms. These figures are from the build before the output scales were
re-pinned (below), which move every key of a piano alike and leave the jumps
as they are.

## How it smooths

At each of a piano's recorded layers, `initCalibrations()` sums every key's
partials and the components beside them over 50 to 750 ms in each channel, as
the per-key level trims already measure a key, and adds those trims. Each
key's level and its balance then go to a target: the median of the thirteen
keys around it, averaged over the seven around. A median alone keeps the
steps of a swing longer than its window: the Hamamatsu's balance, pulled to
the median of seven, still stepped from 5.9 dB to one side to 3.7 dB to the
other between E5 and F5. Both windows narrow at the keyboard's ends, which
keep their own slope: held at full width they flattened the last six keys,
lifting the upright's top keys by 2.5 dB and lowering the Hamburg's A0 by
3 dB, against the top-note trims. Each key takes a gain on each channel that
brings it to both targets, the balance's at its target level, and the strike
plays it between the layers around its own, on the partials and the noise
burst alike.

Moving the burst with the partials, against moving the partials alone, stood
closer on nine of the ten pianos' train and dev sums (in tolerance units over
the eleven measures other than level): the Hamamatsu's 0.54 closer on the
train takes and 0.60 on the dev, New York's 0.65 and 0.24; the upright's dev
takes stood 0.57 further.

## On the benchmark

Against 0.4.31, the paired means summed over the eleven measures other than
level, in tolerance units (lower is closer):

| piano | train | dev | train ild (dB) | dev ild (dB) |
|---|---:|---:|---|---|
| New York | +0.53 | −0.32 | 1.74 → 2.43 | 6.09 → 6.04 |
| Hamamatsu | +4.79 | −1.36 | 1.77 → 4.49 | 5.60 → 4.87 |
| upright | +2.43 | −0.09 | 1.85 → 2.90 | 3.90 → 4.23 |
| Kakegawa | +1.36 | +0.44 | 0.80 → 1.48 | 2.25 → 2.61 |
| Hamburg | +0.40 | −0.29 | 1.59 → 1.55 | 4.93 → 4.88 |

The level difference between the channels (`ild_db`) carries the train
takes' moves: those are the recorded pitches, which now leave their
recordings' own balance, as the owner chose. The Hamamatsu's dev takes, keys
the fit never saw, stand 0.73 dB closer in it. Partial levels stand closer
on every piano and role but the Hamburg's dev takes (7.14 to 7.15 dB), the
Hamamatsu's train takes 7.86 to 7.56 dB. The train takes stand further in
level (`level_db`, the spread of a take's gain about the median), the dev
takes of New York, the upright and the Hamburg closer (5.46 to 4.87, 2.53 to
1.85 and 3.12 to 2.67 dB). Every regression past a tolerance is
listed in the five comparisons
([New York](../validation/newyork-key-smoothing-benchmark-2026-11-10.md),
[Hamamatsu](../validation/kawai-key-smoothing-benchmark-2026-11-10.md),
[upright](../validation/upright-key-smoothing-benchmark-2026-11-10.md),
[Kakegawa](../validation/grand-key-smoothing-benchmark-2026-11-10.md),
[Hamburg](../validation/hamburg-key-smoothing-benchmark-2026-11-10.md)); past
the stereo balance and level they are mostly the Hamamatsu's and the
upright's recorded treble pitches in noise, attack and early level, their
noise burst moved with their partials, and rise on the grand's dev C2
(3.88 to 8.71 ms), the upright's C4 (28.09 to 32.00 ms), the Hamburg's D2
(20.56 to 23.03 ms) and the Hamamatsu's dev A♯5 (2.38 to 4.69 ms).

On the grand's held-out evaluation (`Tools/evaluate_recordings.py`) the
twelve in-range cases stand at 4.892 dB in bands (4.950 on 0.4.31), 3.785 dB
in harmonics (3.990), 1.718 dB in envelope (1.676), 1.904 dB/s in decay
(2.270), 0.186 cents in pitch (0.190) and 4.514 ms in rise (4.090). The edge
cases C1 and C7 at velocity 8 stand 4.774 dB in bands (4.602), 2.235 dB in
harmonics (2.284), 8.135 dB in envelope (8.275) and 0.784 dB/s in decay
(0.424).

## Levels

Reason's meter reads the louder channel, so evening out a piano's balance
moves its reading: each piano's default sound moved by 0.15 to 0.67 dB and
its tube alone by up to 0.63 dB. Each output scale and tube scale is
re-pinned to the reading it had before; the Hamamatsu's default sound reads
−8.92 VU against −8.97, as a smaller output scale took its tube under its
approved reading. The presets that play a piano at another width,
brightness or mute move against its default sound, and the owner approved
thirteen new readings, to six decimals: the typical playing of Studio Grand
(−10.17 to −9.88 VU), Warm Walnut (−10.95 to −10.66), Felt Nocturne (−18.13
to −17.54), Open Strings (−7.97 to −8.17), Felt Upright (−15.59 to −16.32),
Pop Upright (−9.31 to −9.71), Hamamatsu Grand (−9.01 to −8.92) and Three
Cities (−10.43 to −10.12), and the loudest chords of the Kakegawa Grand
(1.41 to 1.57 VU), Warm Walnut (0.62 to 1.01), Felt Nocturne (−5.59 to
−5.32), Open Strings (1.93 to 2.05) and the grand's tube (1.72 to 1.77).
`Keyra.FactoryDynamics` fails on 995 rows where 0.4.31 failed on 1,136: 924
pairs under their step floors (1,040) and 71 chords past its maximum levels
(96).

## Tests and CPU

The `unit` tier (45 tests), the `audio` tier's demos, `Keyra.Levels` on the
approved readings and the `perf` tier pass, and `KeyraDSPCxx17` builds. The
smoothing is set up once, when the engine is built: a key's partials at each
of its piano's layers, 2,640 series in all, which takes the engine's
construction from 0.05 to 0.28 s of CPU on the development machine (nine
alternating runs). Each strike adds two interpolations and a gain per
channel. New York's and the Hamamatsu's 88 keys struck in turn with the
pedal down render in a median 3.35 and 3.11 s of CPU against 3.23 and 2.91,
seven alternating runs, the construction's 0.23 s included.

## What it does not do

The measure is the key's partials and burst; from F6 up the undamped
strings ring with each strike and carry their own image, so a top key's
balance on the meter is not its partials': the upright's E7 and F7 at
velocity 40 stand 3 dB further to one side than before. At the keyboard's
ends the windows narrow to nothing, so A0 and C8 keep their own level and
balance: the Hamamatsu's A0 stands 5 dB over its neighbours at velocities 40
and 120 and its C8 6 dB to one side. Between two recorded layers the gain
moves linearly, while a key's partials move between the layers' fits, so a
key can still jump at a velocity between: New York's D♯7 at velocity 80
stands 6.5 dB to one side of its neighbours, and 1 dB at velocities 40 and
120.
