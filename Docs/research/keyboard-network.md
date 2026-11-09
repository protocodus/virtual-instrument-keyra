# The keyboard network

Today every recorded pitch of a piano is fitted on its own
(`Tools/fit_realtime_modal.py`) and the engine blends between the recorded
pitches. The keyboard network fits a piano's whole keyboard at once: one small
network gives, for any piano, key, velocity layer and partial, the figures the
engine plays. It learns what pianos share from every library in its settings,
and what makes each piano itself from a short code per piano. It runs offline
only. The recordings are the benchmark: the network is fitted to all of them as
a whole and never to one note.

Since 0.4.26 the Kawai, the Hamburg and New York play the third run's
partials at their keys between recorded pitches, each at its own setting,
written by `Tools/write_network_tables.py` (The third run and In the engine,
below); from 0.4.22 the Hamburg played the first run's. Since 0.4.23 the
grand and the upright blend theirs and then reshape how each partial decays
by a correction learned at recorded pitches it hid (A correction to the
blend, below), and every recorded pitch plays its own fit. The first run's
cross-validation, backtest and weights are kept (The first run, below), the
second run's cross-validation and backtest (The second run), and the third
run's grid and the weights that ship (The third run).

`Tools/keyboard_network.py` does the work. Its head states the protocol: the
loss, what is left free to each recording, and how cross-validation chooses.
`Tools/keyboard_network.json` holds its settings. This page is the how-to.

## What it learns from

| Library | Piano | Recordings | Decoder | Manifest |
| --- | --- | --- | --- | --- |
| `grand` | Keyra's grand | Salamander Grand Piano V3 | `fetch_salamander.py` | `Tools/corpus/salamander-v3.json` |
| `upright` | Keyra's upright | Helsinki 1967 Tube-Ribbon Edition | `decode_helsinki.py` | `Tools/corpus/helsinki-1967.json` |
| `kawai` | Keyra's Hamamatsu grand | VCSL Keys "Grand Piano, K" | `decode_vcsl.py` | `Tools/corpus/vcsl-kawai.json` |
| `hamburg` | Keyra's Hamburg grand | Decent Sampler "Steinway Grand" | `decode_hamburg.py` | `Tools/corpus/hamburg-grand.json` |
| `newyork` | Keyra's New York grand | Pianobook "Grandpa's Piano" | `decode_newyork.py` | `Tools/corpus/newyork-grand.json` |
| `vcsl-kawai-legacy` | the Hamamatsu grand again | VCSL Keys "Grand Piano, K - Legacy" | `decode_base_library.py` | `Tools/corpus/vcsl-kawai-legacy.json` |
| `bitklavier` | a Steinway D | bitKlavier House ORTF | `decode_base_library.py` | `Tools/corpus/bitklavier.json` |
| `vcsl-steinway-b` | a Steinway B of 1895 | VCSL Keys "Grand Piano, S Model B 1895" | `decode_base_library.py` | `Tools/corpus/vcsl-steinway-b.json` |
| `vcsl-knight` | a Knight upright | VCSL Keys "Upright Piano, Knight" | `decode_base_library.py` | `Tools/corpus/vcsl-knight.json` |
| `vcsl-upright-y` | an upright, maker not given | VCSL Keys "Upright Piano, Y" | `decode_base_library.py` | `Tools/corpus/vcsl-upright-y.json` |

The five Keyra pianos contribute only the train pitches of their locked
splits (`split` in each piano's entry in `fit_realtime_modal.MODELS`); their
dev and sealed pitches are never measured. A second capture of a Keyra piano
(`capture_of` in its manifest, as `vcsl-kawai-legacy` has) leaves out the
pitches that piano's split holds back, so that no held-out recording is
learned through other microphones. The other libraries are measured whole.
No library is played, shipped or committed; each is measured into `out/`,
which Git ignores.

## Running it

Run everything from the repository root. The network needs Python 3 with
NumPy, SciPy and PyTorch (CPU is enough); `check` and `engine` also need
`build-dsp/keyra_render` (the `keyra_render` target of the DSP build), built
from the engine being judged.

First bring the audio in with each library's decoder (table above), which
verifies every file against its manifest's SHA256 pins. A base library can
come over in parts; `--pin` pins takes not pinned yet. Then one command does
the rest, unattended:

```sh
python3 Tools/keyboard_network.py all --run <run> --alone --workers 4
```

`--alone` learns from the five Keyra pianos only; without it every library in
the settings is used. `--workers` sets how many processes measure, render or
train at once (one PyTorch thread each by default, `--threads`). Every step
keeps what it has finished, so the same command resumes a run that stopped
and redoes only what changed. It ends with `out/network/<run>/report.md`
(and `report.json`): today's tables and engine, every cross-validation entry
and the dev backtest of the chosen fits. On four cores a `--alone` run takes
most of a day.

The steps `all` runs, each of which can be run on its own:

1. **Self-test:** `python3 Tests/test_keyboard_network.py` checks the training
   model's arithmetic without any recording (see Checks below). `all` stops
   if it fails.
2. **Measure:** `python3 Tools/keyboard_network.py measure` measures every
   recorded pitch whose audio is present into `out/keyboard/<library>/<pitch>.pkl`,
   and each Keyra piano's dev takes into `out/keyboard-dev/`: each partial's
   envelope in each channel and the frames and weights the fitter weighs them
   by. A pitch is cached by its inputs (the takes' pins, the analysis options
   and the code of `piano_analysis.py` and `keyboard_measurements.py`), so the
   step redoes only what is missing or stale. Once a base library is measured
   its audio can be deleted (`out/base/<library>/wav`): training reads only the
   measurements, and with no audio left the step says so and keeps them as
   they are, whatever analysis code made them; decode the library again to
   measure it anew.
3. **Check the training model against the engine:**
   `python3 Tools/keyboard_network.py check` plays today's tables through
   `keyra_render` at each Keyra piano's lowest, middle and highest train
   pitches, measures the renders as recordings are measured, and compares them
   with the closed form the network is trained through, with the engine's
   velocity colour applied as the engine applies it. It passes when, at each
   pitch's loudest layer, the median partial's relative error is under 0.05
   and the first eight partials stay, at the median, within 1 dB of the
   layer's gain; `all` stops if it fails. (One by one they would not: the
   lowest keys' weak fundamental shares its band with one of the body's
   modes, which the closed form does not hold. The partial straying
   furthest is printed.) Each layer's gain is printed: it stays within a few
   tenths of a dB across a pitch's layers, and differs from key to key by the
   engine's per-key loudness trims. Run it after any engine change to how
   partials are played.
4. **Score today's tables:** `python3 Tools/keyboard_network.py baseline`
   scores today's tables in closed form under the same loss at their own train
   pitches, each channel's level first set where it fits best (the network
   learns its own). There the tables hold each key's own fit.
5. **Score today's engine:** `python3 Tools/keyboard_network.py engine`
   renders every train and dev take's key at its velocity through
   `keyra_render` and scores the render as a network is scored (What today's
   engine scores, below). The renders are cached in
   `out/keyboard-engine/<library>.npz` by the renderer's bytes and the takes,
   so a new engine build renders again and a scoring change does not.
6. **Cross-validate:** `python3 Tools/keyboard_network.py cv --run <run>`
   (add `--alone` as above). For every architecture and knob asked for, it
   trains once without each fold of the Keyra pianos' train pitches and scores
   that fold, as trained and after fine-tuning each piano (its code alone, and
   its code with the network's last layers). `--arch`, `--knob` and `--folds`
   narrow it. `all` first runs every architecture at the smallest knob, then
   every knob at the architecture that predicted the held-out pitches best.
   Results go to `out/network/<run>/cv.json` and each entry's training log to
   `logs/`; a finished entry is kept while its settings, the script and the
   measurements are unchanged.
7. **Fit and backtest:** `python3 Tools/keyboard_network.py fit --run <run>`
   (`--arch` to choose another than the best) trains on every train pitch at
   both settings cross-validation chose, "character" (the knob whose held-out
   error is lowest) and "smooth" (the largest knob within one standard error of
   it), fine-tunes each piano at the depth cross-validation chose for it,
   scores each piano at its train and dev takes, and writes `receipt.json` and
   the weights, `<setting>-shared.npz` and `<setting>-<piano>.npz`, to
   `out/network/<run>/`.
8. **Report:** `python3 Tools/keyboard_network.py report --run <run>` prints
   the cross-validation summary and writes `report.md` and `report.json` again.
9. **Correct the blend:** `python3 Tools/keyboard_network.py correct --run
   <run> --arch medium --knob 10 100 1000` trains, at each knob, a correction
   to the engine's blend between recorded pitches (A correction to the blend,
   below) on the Keyra pianos' train pitches, and scores it beside the blend
   alone at those pitches and at the dev takes: `correction.json` and
   `correction-<arch>-<knob>.npz` in `out/network/<run>/`. `all` does not run
   it.

`Tools/write_network_tables.py` then writes a fit's partials at every key
between two recorded pitches into the engine's tables (In the engine, below),
or a correction's figures at the keys of the pianos it names (`--corrections`
and `--corrected`).
Still to come: the keyed A/B between the blend and the network at the
Hamburg's keys between recorded pitches.

## What the loss compares

The loss compares what is heard. For every partial, in each channel, frame by
frame, it takes the network's power through the window the fitter measures
with, in log, against the measured power. A frame counts against the
envelope's largest value within 0.3 s of it, as the fitter weighs it, and a
beat's nulls count down to 20 dB below that value. Each partial's frequency
is fitted to the measured one in cents: the power-weighted centre of its
lanes, where the engine plays them. The figure reported is the rms level
error in dB.

The fitter's own misfit, which compares the complex envelopes, is reported
beside it but is not trained on. It also compares the lanes' frequencies to
a few hundredths of a hertz over seconds, and a unison's beat rate changes
at random from one key to the next. No model that follows the keyboard
smoothly can match that. Lanes off by 0.05 Hz take today's tables' misfit at
their own pitches from 0.20 to 0.57 on the grand; at 0.3 Hz it reaches 0.98,
and silence scores 1. The power loss only moves from 0.71 to 1.01. Trained
on the misfit, the network made every partial silent.

Phases are not compared. The soundboard, the room and the microphones'
places turn every partial by their own response at its frequency, and no key
tells its neighbour's. The lanes' phases against each other set the beating,
and those the network learns. The table writer will take each partial's
phases from the nearest recorded pitch, as the engine takes them from the
nearer anchor today.

Two things belong to a recording rather than to the piano, and the loss
leaves them free:

- **The level of each take** where a library normalised its takes
  (`normalised` in its manifest). Such a library's layer levels are learned
  instead of measured.
- **Each library's recording term:** a level and a tone curve over octaves per
  microphone.

## What today's engine scores

`engine` plays every train and dev take's key at its velocity through
`keyra_render`, as the instrument ships, measures the render as a recording is
measured and scores it under the same loss. Each channel's level is set where
the train takes fit best and kept for the dev takes, as a network's recording
term is.

Beside its tables the engine plays its own voicing: the additional velocity
colour, which gives the partials 10 to 12 dB more range across the layers
than the recordings have; per-key loudness trims of up to several dB; and
the strike's noise, the body's knocks and the undamped strings. A network's
closed form holds none of these, so a network's figures and the engine's do
not compare. Compare a network's train figures in closed form with today's
tables in closed form (`baseline`), and each with its own dev figures; written
into tables, a network plays in the engine and scores there as today's tables
do (In the engine, below).

Dividing the colour back out of a render is no shortcut: it divides it out of
the noise too, which the colour never touched. Where the colour cuts deepest,
the soft layers' upper partials, the noise then stands 20 to 35 dB over the
take, and the New York grand scored worse without its colour than with it.

On 2026-11-04, with `keyra_render` built from commit 6ebafe2 (rms level error
in dB):

| Piano | Tables, closed form, train | Engine, train | Engine, dev |
| --- | --- | --- | --- |
| grand | 3.55 | 5.59 | 7.68 |
| upright | 4.60 | 7.04 | 9.54 |
| kawai | 6.84 | 8.87 | 10.53 |
| hamburg | 6.63 | 7.56 | 10.90 |
| newyork | 6.14 | 9.37 | 11.42 |

The grand's dev takes include 88 at its own recorded pitches; every other
dev take lies between a piano's recorded pitches, where the engine blends
its two neighbours.

## The first run

On 2026-11-04, `all --run alone --alone --workers 4` with the engine figures
above. Its receipt, report, cross-validation results and weights are kept in
[keyboard-network-2026-11-04/](keyboard-network-2026-11-04/), without the
training logs.

Cross-validation chose architecture medium. Held out, it scored 9.89 dB at
knob 1000 against 10.18 dB for small and 10.26 dB for large (each at knob 0).
Both settings chose knob 1000, so the `character-` and `smooth-` files hold
the same arrays and differ only in their `meta`. Knob 1000 is the largest the
settings try, and every medium knob from 0 to 1000 scores within 0.11 dB of
it, under one standard error: the held-out pitches do not decide the knob at
this size.

Backtest, rms level error in dB; the network in closed form, fitted on every
train pitch and fine-tuned to each piano at the depth in brackets:

| Piano | Network, train | Network, dev | Engine, train | Engine, dev |
| --- | --- | --- | --- | --- |
| grand | 8.05 (none) | 9.06 | 5.59 | 7.68 |
| upright | 8.04 (last) | 7.84 | 7.04 | 9.54 |
| kawai | 8.36 (last) | 8.94 | 8.87 | 10.53 |
| hamburg | 7.31 (last) | 9.54 | 7.56 | 10.90 |
| newyork | 7.50 (last) | 7.64 | 9.37 | 11.42 |

The two do not compare across (What today's engine scores, above), but each
compares with itself. From the train takes to the dev takes the network
moves by −0.2 to +2.2 dB and today's engine, blending its recorded pitches,
by +1.7 to +3.3 dB. At the train pitches the network is far from today's
tables, which hold each key's own fit (3.55 to 6.84 dB in closed form).
Whether its tables play better than today's is for the table writer, the
recording benchmarks and the keyed A/B to show.

## The second run

On 2026-11-05, `cv --run full --arch medium --knob 1000 --workers 3`, then
`fit` and `report`: every library in the settings, the five base libraries
beside the five Keyra pianos' train pitches, at the architecture and knob the
first run chose. Its report, receipt and cross-validation results are kept in
[keyboard-network-2026-11-05/](keyboard-network-2026-11-05/); its weights
are not, as no table written from them ships.

Held out, it scored 10.24 dB, where the first run scored 9.89 at the same
setting: the grand 10.12 (9.55), the upright 9.39 (9.35), the Kawai 10.94
(9.20), the Hamburg 10.90 (11.34) and New York 9.73 (9.85).

Backtest in closed form, rms level error in dB, the first run's in brackets:

| Piano | Network, train | Network, dev |
| --- | --- | --- |
| grand | 8.24 (8.05) | 8.94 (9.06) |
| upright | 8.20 (8.04) | 7.54 (7.84) |
| kawai | 11.11 (8.36) | 11.25 (8.94) |
| hamburg | 7.57 (7.31) | 7.69 (9.54) |
| newyork | 7.94 (7.50) | 7.60 (7.64) |

In closed form the base libraries bring four pianos' dev figures down, the
Hamburg's by 1.85 dB, and the Kawai's up by 2.31 dB. Played in the engine,
its tables score worse than the first run's (In the engine, below).

## The third run

On 2026-11-06, `grid --run capped --alone --arch large medium small --knob
10 1000`, the five Keyra pianos alone with the settings' `cap` and
`attack_weight` on (the tool's head gives both): no lane decays faster than
the fits' fastest at its key, the bound the table writer puts on a key's
lanes, and each partial's energy in each channel over its first 100 ms is
weighed against the measured. The first run decayed 31 to 54 % of its lanes
faster than that bound, which the writer then left out, and struck 1.4 to
2.8 dB quiet over the first 100 ms at the train takes before any lane was
left out. `grid` makes the final fits, fine-tuned to each piano, at each
architecture and knob, without cross-validation: the first run's held-out
pitches did not decide the knob, so each piano's setting is the one its
tables played in the engine score best at. Its grid report, receipt and the
weights of the three settings that ship are kept in
[keyboard-network-2026-11-06/](keyboard-network-2026-11-06/).

In closed form, its train takes' strike over the first 100 ms stands 0.44 to
2.77 dB under the measured, from 0.44 to 0.68 at the large network and knob
10 to 1.59 to 2.77 at the small and knob 1000; their level errors are 7.29 to
11.24 dB, where the first run's were 7.31 to 8.36.

Each setting's tables, written for every piano and played by
`keyra_render`, were scored by `Tools/benchmark_recordings.py` on every train
and dev take against 0.4.25 (the first run's tables on the Hamburg, the
corrections on the grand and the upright, blending on the Kawai and New
York). Each measure's mean change on the dev takes, in units of
`Tools/compare_benchmarks.py`'s tolerance, summed over the 12 measures, and
how many of them stand closer and how many further:

| Setting | grand | upright | kawai | hamburg | newyork |
| --- | --- | --- | --- | --- | --- |
| large, knob 10 | +4.89 (2, 10) | +0.78 (4, 8) | +2.05 (4, 8) | −2.68 (7, 5) | +6.32 (3, 9) |
| large, knob 1000 | +2.78 (3, 9) | +2.23 (4, 8) | −3.18 (8, 4) | +10.00 (2, 10) | +3.67 (4, 8) |
| medium, knob 10 | +1.92 (4, 8) | +2.02 (4, 8) | −0.50 (8, 4) | **−0.55 (8, 4)** | +3.32 (7, 5) |
| medium, knob 1000 | +4.51 (2, 10) | +5.83 (5, 7) | **−3.23 (9, 3)** | +18.30 (1, 11) | **−0.57 (7, 5)** |
| small, knob 10 | +8.24 (0, 12) | +8.18 (2, 10) | +3.07 (4, 8) | +5.23 (5, 7) | +7.24 (4, 8) |
| small, knob 1000 | +5.91 (3, 9) | +3.44 (3, 9) | −2.47 (8, 4) | +5.01 (7, 5) | +7.93 (1, 11) |

A piano plays the third run's tables where they bring its dev takes closer on
most of the 12 measures with the sum below zero, at the setting with the
lowest such sum whose tables pass the engine's tests; the train takes move by
0.38 or less at every setting. The Hamburg's lowest, the large network at
knob 10, leaves its sustain pedal no bloom on a held C4 (−0.02 dB, where
`Keyra.Engine` asks 0.6 to 5), so it takes the medium at knob 10. The
grand's and the upright's stand further at every setting, and they keep their
corrections (A correction to the blend, below). In bold, what ships
(`SETTING` in the writer):

- **The Kawai**, medium at knob 1000: its 23 dev takes stand closer in
  tuning (0.61 cents), rise (0.48 ms), decay (0.41 dB/s), envelope (0.27 dB),
  partial levels (0.22 dB), sustain (0.18 dB), attack, noise and coherence,
  and further in stereo balance (0.33 dB), level (0.05 dB) and early
  (0.003 dB).
- **The Hamburg**, medium at knob 10: its 8 closer in noise (1.35 dB),
  partial levels (0.76 dB), decay (0.72 dB/s), rise (0.69 ms), envelope,
  early, stereo balance and coherence, and further in tuning (1.62 cents),
  level (0.98 dB), attack (0.32 dB) and sustain (0.21 dB).
- **New York**, medium at knob 1000: its 17 closer in tuning (0.82 cents),
  rise (0.37 ms), sustain (0.30 dB), noise (0.26 dB), level (0.22 dB),
  partial levels (0.18 dB) and decay (0.16 dB/s), and further in early
  (0.29 dB), envelope (0.28 dB), attack (0.23 dB), stereo balance (0.14 dB)
  and coherence (0.033).

Six settings were tried on the dev takes and the best of them kept, so those
figures flatter the choice; the sealed takes were not opened this round.

With these tables the Kawai's and New York's keys between recorded pitches
play quieter than they blended, and their readings on Reason's meter fell:
the Kawai's to −10.21 VU from −8.97 and New York's to −10.94 from −9.09. The
Hamburg's play louder than the first run's tables did, and its reading rose
to about −8.4 from −8.95 (through the tube to about −8.9 from −9.18). Each
output and tube level is re-pinned to the reading it had
(`KeyraEngine.cpp`), which moves every take of the piano, recorded pitches
too. The benchmark's level error, which holds 0.4.25's gain, then stands
the Kawai's dev takes 0.41 dB closer and its train takes 0.33 further, the
Hamburg's 1.41 and 0.04 further and New York's 1.63 and 1.19 further; taken
at each version's own gain, as its first tables are, the Kawai's stand 4.36
→ 4.21 and 1.89 → 1.94 dB, the Hamburg's 2.15 → 3.13 and 0.69 → 0.61 and New
York's 5.61 → 5.45 and 0.88 → 0.90. The whole benchmark of 0.4.26, which
carries the treble's unison strings on the grand, the upright and New York
too, is in each piano's report
([grand](../validation/grand-network-unisons-benchmark-2026-11-06.md),
[upright](../validation/upright-network-unisons-benchmark-2026-11-06.md),
[Kawai](../validation/kawai-network-unisons-benchmark-2026-11-06.md),
[Hamburg](../validation/hamburg-network-unisons-benchmark-2026-11-06.md),
[New York](../validation/newyork-network-unisons-benchmark-2026-11-06.md)).

The 88 keys struck in turn at velocity 90, 120 ms apart with the pedal down,
render 14 s of audio in a median 3.10 s of CPU on the Hamburg where 0.4.25
took 5.63 (−45 %), 2.76 on the Kawai against 2.72 (+1.6 %) and 3.05 on New
York against 2.79 (+9.5 %, which carries its unison strings too), seven runs
of each in alternating order on a 2.1 GHz Xeon: a development machine's
figure, not Reason's.

## In the engine

`Tools/write_network_tables.py` evaluates a fit at every key strictly between
two recorded pitches and writes its partials in the engine's format into
`Source/DSP/MeasuredNetworkKeys.h`; its head gives the reason for each step:

- the orders either pitch holds, each lane's decay, offset, pickup and level
  per layer from the network, in the fits' units;
- no lane that decays faster than both fits beside the key: unlike the
  fitter, the network pays nothing for a lane's amplitude, and played, those
  lanes clicked;
- each partial's power in each channel over 50 to 750 ms moved by what the
  fit at each of the two pitches holds over the network there, blended
  between the two in dB, so that the engine's per-key trims, which pull every
  key towards its neighbours' level, leave the recorded pitches where they
  were;
- tuning and rise from the blend, and the right channel's lag and the phases
  as the blend gives them.

`KeyraEngine.cpp` plays a key the table holds from its partials (`series()`)
and every other key as before. `python3 -I Tools/write_network_tables.py`
writes the table that ships, and `Keyra.MeasuredNetworkKeys` checks that the
header is what it writes.

The `engine` stage scored each piano's dev takes with its keys between
played from each run's tables (rms level error, dB; the train takes, at the
recorded pitches, stay within 0.02 dB of blending):

| Piano | Blending, 0.4.21 | First run | Second run |
| --- | --- | --- | --- |
| grand | 7.79 | 7.73 | 7.80 |
| upright | 9.56 | 9.94 | 9.86 |
| kawai | 10.56 | 11.13 | 12.44 |
| hamburg | 11.04 | 9.38 | 10.12 |
| newyork | 11.65 | 12.36 | 12.13 |

The recording benchmark (`Tools/benchmark_recordings.py`) decided between
the two pianos the first run brought closer. On the Hamburg's eight dev
takes its keys stand closer to the recordings on 7 of the benchmark's 12
measures (envelope 1.68 dB, sustain 1.36 dB, decay 0.59 dB/s, rise 0.33 ms,
noise 0.19 dB, image 0.12 dB, early 0.07 dB) and further on 5 (tuning 0.38
cents, level 0.31 dB, attack 0.13 dB, coherence 0.008, partial levels
0.02 dB; [report](../validation/hamburg-network-keys-benchmark-2026-11-05.md)). On the grand's they stand further on 6 (envelope 0.31 dB, tuning
0.24 cents, decay 0.17 dB/s, level and partial levels 0.04 dB, image
0.03 dB) and closer on 5 (rise 0.56 ms, sustain 0.47 dB, early and noise
0.05 dB, attack 0.01 dB), and 8 measures at four of its notes pass a
tolerance, D♯3's envelope from 1.59 to 5.73 dB. So the Hamburg played the first run's tables and the
other four blended (Docs/decisions.md, 2026-11-05), until 0.4.26 gave the
Hamburg, the Kawai and New York the third run's (The third run, above).

Written other ways, the Hamburg's first-run tables scored worse:

- at the network's own levels, 8.96 dB on the dev takes, but the per-key
  trims then moved the recorded pitches: the benchmark's level error went
  from 0.70 to 2.95 dB on the train takes and from 1.84 to 6.01 on the dev
  takes;
- with the fastest lanes kept at the fits' fastest decay rather than left
  out, 12.74 dB;
- with each partial's decays moved towards the fits' as its levels are,
  9.35 to 10.61 dB, failing `Keyra.Engine`'s Ring check on the Hamburg's
  C4, and on the benchmark the envelope 1.88 dB further from the dev takes;
- with the blend's lanes faster than the network's in the places of the
  lanes left out, the network's lanes scaled to keep each partial's power
  over 50 to 750 ms, 9.49 dB, and further than the shipped tables on 6 of the
  benchmark's 12 measures, the partial levels 0.26 dB further and the
  sustain 0.93 dB closer where the shipped tables' are 1.36 closer.

The second run's tables fail two of `Keyra.Engine`'s checks and
`Keyra.Glide`. The first run's tables strike weaker than the blend, 2.3 dB over
the first 100 ms at velocity 80, and ring 1.0 to 1.7 dB louder from 100 ms
on, so the Hamburg's output and tube are re-pinned to the readings they had
(Docs/decisions.md, 2026-11-05). The third run's strike weaker too: each key
between struck alone and held for 2 s stands a median 2.7, 2.6 and 2.4 dB
under the blend over its first 100 ms at velocity 80 on the Kawai, the
Hamburg and New York, and 0.4, 0.4 and 1.4 dB over it from 100 ms on
(README, Known gaps). They cost less to
play: struck chromatically at velocities 40 and 100 with the pedal down, the
Hamburg renders in a median 9.45 s of CPU where 0.4.21 took 14.34 s (seven
runs of each in alternating order, 48 s of audio, on a 2.1 GHz Xeon; a
development machine's figure, not Reason's).

## A correction to the blend

Since 0.4.23 the grand's and the upright's keys between two recorded pitches
above the bass break, where both pitches' strings are plain, blend the two
pitches' fits as before and then reshape how each partial decays, by a
correction learned at recorded pitches it hid (step 9 above). Its weights
and its scores at the three knobs it was trained at are kept in
[keyboard-network-correction-2026-11-05](keyboard-network-correction-2026-11-05/);
the head of the correction's section in `Tools/keyboard_network.py` gives
the reasons for its form, and Docs/decisions.md (2026-11-05) the owner's
answer that licenses it: the keys between are to sound like a realistic
piano with that piano's character, not to be measurements of it.

For any piano, key and partial, the gap the key lies in and its place `t`
there, a small network gives two figures, each times 4t(1 − t) so that both
vanish at the recorded pitches: a shift of the partial's decay rates in log,
at most a factor of e, and a tilt of its lanes' levels, at most 6 dB.
`correct()` in `KeyraEngine.cpp` applies them to the blend as the training
model does: every lane's decay rate times e to the shift, each lane's level
moved by the tilt times the tanh of its log rate's distance from the lanes'
mean, weighed by their power, and then each channel's power over 50 to
750 ms put back where the blend has it. So the per-key trims play every key
as they played the blend, and each lane's tuning and rise and the channel
balance stay the blend's; the first 50 ms, which the window leaves out, are
not held (below). Played through the engine at every key of the five
pianos, the 32,745 corrected partials match the training model's to float
rounding: each lane's share of its partial within a relative 6.5e-7, every
decay rate exactly, and each channel's window power within a relative 2e-6.

It learns by hiding each recorded pitch of the five pianos with up to two
of its neighbours in a row, across no more than 21 keys, and comparing the
blend of the pitches around them with the hidden pitch's own fit, by each
channel's energy over 0.05 to 0.75, 0.75 to 1.5 and 1.5 to 3.5 s. Trained
at the knobs 10, 100 and 1000 (about 26 minutes each on one thread), the one
at 1000 ships. Its rms error in those energies, in dB, against the hidden
pitches' fits (train) and the dev takes' recordings, corrected at every key
between as it was trained:

| Piano | Train, blend | Train, corrected | Dev, blend | Dev, corrected |
| --- | --- | --- | --- | --- |
| grand | 10.05 | 9.79 | 8.03 | 7.89 |
| upright | 10.42 | 9.93 | 8.09 | 8.03 |
| kawai | 11.10 | 10.99 | 10.80 | 10.76 |
| hamburg | 13.33 | 11.74 | 10.79 | 12.42 |
| newyork | 12.20 | 11.42 | 9.67 | 10.07 |

The blend leaves the keys between short. At the grand's dev takes the
correction touches, D♯3, D♯5 and D♯7, partials 1 to 15 stand 3.1 and 3.5 dB
under their recordings over 0.75 to 1.5 and 1.5 to 3.5 s blended and 2.2 and
2.5 dB under corrected, partials 16 to 39 4.6 and 4.8 dB under and 3.2 and
2.5 corrected, and partials from the 40th 1.3 and 7.5 dB under and 1.0 and
6.1 corrected. At the upright's, G♯3, B3, C5 and E6, partials 1 to 15 stand
1.2 and 2.9 dB under, corrected 1.0 and 2.5, and partials 16 to 39 5.9 and
6.6, corrected 5.4 and 5.0. So the corrected keys ring on longer than
blended, toward how the recordings ring.

The window leaves each key's first 50 ms free. Struck alone at velocity 72,
each key between against the line through its recorded neighbours' levels,
the grand's keys between from C6 up start over their first 50 ms on average
0.69 dB under that line blended and 1.26 dB under corrected, and those from
C3 to B5 0.10 and 0.04 dB over it; below C3 they blend as before. The
upright's move by 0.22 dB or less in each register.

The recording benchmark (`Tools/benchmark_recordings.py`) decided for each
piano, against 0.4.22 on the dev takes, which no fit holds. The grand's and
the upright's rows are the version that ships, corrected above the bass
break; the other three pianos' are the correction at every key between:

| Piano | Dev takes | Measures closer | Further | A pitch's measures past a tolerance |
| --- | --- | --- | --- | --- |
| grand | 156, 48 of them corrected | 7 of 12 | 5, by 0.019 or less | none |
| upright | 21, 16 of them corrected | 9 of 12 | 3, by 0.046 or less | none |
| kawai | 23 | 7 of 12 | 5, sustain 0.29 dB | 6, at 5 pitches |
| hamburg | 8 | 4 of 12 | 8, envelope 2.11 dB | 9, at 2 pitches |
| newyork | 17 | 6 of 12 | 6, decay 1.09 dB/s | 6, at 2 pitches |

At the 48 takes it corrects, the grand's come closer in sustain (0.61 dB),
envelope (0.45 dB), partial levels (0.28 dB), decay (0.23 dB/s) and rise
(0.14 ms), and further in tuning (0.06 cents) and four measures by 0.03 or
less; at the 16, the upright's come closer in envelope (0.37 dB), sustain
(0.22 dB), partial levels (0.19 dB) and six measures more, and further in
tuning (0.06 cents), noise (0.02 dB) and image (0.006 dB)
([grand](../validation/grand-blend-correction-benchmark-2026-11-05.md),
[upright](../validation/upright-blend-correction-benchmark-2026-11-05.md)).
Their train takes, at the recorded pitches, score as in 0.4.22 on every
measure to four decimals.

Corrected at every key between, as trained, the grand's 156 stood closer on
8 measures and further on 4, and the upright's 21 closer on 7 and further on
5, again none past a tolerance. But below the break it took the envelope
and the sustain further from the recordings at every pitch then scored
there: the grand's D♯1 (envelope 4.38 to 4.54 dB, sustain 4.38 to 4.67 dB),
the upright's D♯2 (2.09 to 2.50 and 8.96 to 9.15 dB, and further on 9 of the
12 measures) and the grand's sealed D♯2 (1.86 to 2.38 and 5.58 to 5.67 dB,
its envelope and its rise, 9.12 to 16.28 ms, past a tolerance), where at all
nine pitches then scored above it the envelope came closer. So the writer
corrects only between two plain-string pitches. That restriction was chosen
after the grand's sealed takes had been opened for the correction at every
key between, so D♯2 no longer stands as untouched evidence for it. The
upright's sealed F♯1, opened after it was chosen, bears it out: corrected,
its partial levels went 9.73 to 10.94 dB, its decay 4.97 to 6.33 dB/s and
its sustain 7.04 to 7.95 dB, all three past a tolerance, though its
envelope came closer (3.43 to 3.12 dB).

The Kawai's take six measures past a tolerance at five pitches, F♯7's
sustain 7.18 to 8.20 dB the most, five of them above its bass break, and
New York's at E4 and C6, both in ten-key gaps above its break, C6's decay
8.27 to 10.79 dB/s. The Hamburg's keys play the network's partials, which
stand closer. So the grand and the upright take the correction
(`CORRECTION` and `CORRECTED` in the writer). The engine stage's frame score
(What today's engine scores), which counts each frame's level and so the
beats the correction does not place, has the grand's dev takes 7.78 dB off
against 7.79 blended and the upright's 9.58 against 9.56.

The grand's sealed takes, D♯2, D♯4 and D♯6 at every layer, were opened
twice, for the correction at every key between and for this version, which
plays D♯2 as 0.4.22 does. At D♯4 and D♯6, 32 takes, it stands closer on 9
of the 12 measures (partial levels 0.98 dB, sustain 0.97 dB, decay
0.91 dB/s, envelope 0.87 dB) and further on 3 (rise 0.06 ms, attack
0.03 dB, image 0.02 dB), and no pitch passes a tolerance
([report](../validation/grand-blend-correction-sealed-2026-11-05.md)). The
upright's, F♯1, E4 and G♯5 at every layer, were opened once for each
candidate and for 0.4.22. This version plays F♯1 as 0.4.22 does. At E4 and
G♯5, 10 takes, it stands closer on 5 of the 12 measures (decay 0.65 dB/s,
partial levels 0.13 dB) and further on 7 (envelope 0.18 dB, tuning
0.08 cents, the others 0.03 or less), and no pitch passes a tolerance
([report](../validation/upright-blend-correction-sealed-2026-11-05.md)).
There its gain is in the decay, not in the envelope its dev takes showed.

The correction is figured once per strike, as the blend is, and costs no CPU
the measurement can tell: struck chromatically at velocities 40 and 100 with
the pedal down, the grand renders in a median 6.64 s of CPU where 0.4.22
took 6.59 s, and the upright in 4.96 s where it took 5.11 s (seven runs of
each in alternating order, 48 s of audio, on a 2.1 GHz Xeon; a development
machine's figure, not Reason's), each within the runs' spread.

## Checks

`Tests/test_keyboard_network.py` checks the training model on synthetic
pitches whose figures are known, without any recording:

- the closed form measures a lane as the fitter's window does, and a strike
  synthesised sample by sample and measured as a recording is gives the
  closed form's envelopes;
- the figures that made the envelopes score nothing, and the loss grows away
  from them;
- what the loss leaves free stays free: each partial's phase, a normalised
  library's take levels, each channel's level;
- the knob's penalty ignores the bass break and partials above the engine's
  highest;
- the strike's term scores nothing at the figures that made the envelopes
  and the squared log of the energy ratio away from them, and nothing for a
  library that normalised its takes; with the caps no lane decays past its
  key's, a lane well under its cap keeps its rate, and the caps are the fits'
  fastest lanes, between two pitches the faster of theirs;
- the blend plays each recorded pitch's fit at its pitch and a power between
  the two pitches' between them, and a correction vanishes at the recorded
  pitches; it speeds every lane's decay by its shift and tilts the lanes'
  levels by theirs, and each channel's power over 50 to 750 ms stays the
  blend's; its window energies leave a partial's beats alone, and a short
  run learns a synthetic correction;
- a network starts the same whatever trained before it in the process, and a
  short run learns a synthetic keyboard;
- the settings name every piano and library, and the train and dev takes keep
  their roles in each locked split, with no sealed take read.

It takes about ten seconds. `all` runs it first. CTest runs it as
`Keyra.KeyboardNetwork` (label `unit`) in a build configured with
`-DKEYRA_ENABLE_NETWORK_TESTS=ON`, which needs NumPy, SciPy and PyTorch; CI
does not install PyTorch, so the option is off by default. The same option
registers `Keyra.MeasuredNetworkKeys`, which writes the table again from the
kept weights (about sixteen seconds) and checks that the header is the same. `check` (step 3
above) is the other half: the same closed form against the engine itself.

## The settings

`Tools/keyboard_network.json`:

- `libraries`: each library the network learns from. `piano` names the piano
  it records (two captures of one piano share it, and with it a code), and
  `keyra: true` marks a piano Keyra plays: its train pitches are the ones
  cross-validation holds out and scores.
- `pianos`: each piano's `tenor`, its first plain-string key. The knob never
  smooths across it, and the network sees which side of it a key is on.
  `tenor_source` says how the key was found: the step in inharmonicity
  between two recorded pitches, or "uncertain" where the recordings show no
  clear step.
- `architectures`: the network sizes cross-validation chooses between. `code`
  is the length of each piano's code, `width` and `depth` the string trunk's
  size, and `fourier` the number of sine and cosine pairs of the key the
  network sees, which sets how sharply it can follow the keyboard.
- `training`: the steps, the units (one layer of one pitch each) drawn per
  library per step, the learning rate, the weight of the tuning term, the
  ridge on the tone curves, and fine-tuning's steps and rate.
- `knobs`: the smoothness values tried, the penalty on the second difference
  of every figure from key to key.
- `folds` and `seed`.

## Recipes

**Use the kept fit instead of retraining.** Copy
[keyboard-network-2026-11-04/](keyboard-network-2026-11-04/) to
`out/network/alone/`. `report` then writes its report again, and the weights
load with NumPy alone: each `.npz` holds the network's arrays and a `meta`
naming its pianos, architecture and knob. `cv` and `fit` keep its entries
while the settings, the script's bytes and the measurements' file names and
sizes are those it was made with, and train again after any change to them.

**Retrain after a change to the network, its settings or the measurements.**
Run `all` under a new run name. Under an existing name, entries whose
settings changed are redone and the others kept; the script's own bytes are
among those settings, so do not edit it while a run is under way.

**After a change to the engine.** Rebuild `keyra_render`, then run `check`
and `engine`: `check` confirms the closed form still plays as the engine
does, and `engine` renders the takes again (its cache follows the renderer's
bytes) and scores the new engine. A network's figures do not change.

**More recordings of a library already here.**

- A base library: copy the new takes into its folder, pin and decode them
  (`decode_base_library.py <library> --library <folder> --pin`), then run
  `all` without `--alone`, which leaves the base libraries out.
- A Keyra piano: new takes need roles in its split first (train, dev or
  sealed), and the split is locked, so that is the owner's call. Then pin and
  decode them with the piano's decoder and run `all`. Train takes are
  measured for training and dev takes for the backtest; sealed takes never.

**A new base library.** Add it to `LIBRARIES` in `decode_base_library.py`:
its title, author, licence, capture, whether its takes were normalised, and
how its notes are found (an SFZ's regions or a file naming scheme). Then pin
and decode it, add it to `libraries` in the settings with its `piano`, and
add that piano's `tenor` to `pianos` (find the step in inharmonicity, B,
between its recorded pitches). Then run `all` without `--alone`. A second
capture of a Keyra piano also takes `capture_of`, so that the piano's
held-out pitches stay out.

**A new piano for Keyra.** It needs what each Keyra piano has: a decoder
that pins its files, a corpus manifest, a locked split, and an entry in
`fit_realtime_modal.MODELS` with its header. Then add it to `libraries` with
`keyra: true` and to `pianos` with its `tenor`, and run `all`.

## Cost

The measurements of all ten libraries take about 230 MB in `out/keyboard`.
A training step takes about 0.2 s on four threads for the five Keyra pianos
alone. The first run's 35 cross-validation entries took 34 to 68 minutes
each on one thread, and its two final fits about 27 minutes each: 7 h 35 min
on four workers, its measurements and renders already cached. Its weights
take 7.3 MB. The second run, on all ten libraries, took 93 to 123 minutes
for each of its five cross-validation entries on three workers, about five
and a half hours with its two final fits. The correction trained for 26
minutes at each knob on one thread, and its weights take 0.28 MB. The
third run's six final fits took 36 to 44 minutes each, three at a time:
about an hour and a half. The three of its weights that ship take 1.9 MB.
Writing the table, the Kawai's, the Hamburg's and New York's partials and
the grand's and the upright's corrections, takes about sixteen seconds, and
the table takes 4.7 MB of source.
