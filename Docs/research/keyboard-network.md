# The keyboard network

Today every recorded pitch of a piano is fitted on its own
(`Tools/fit_realtime_modal.py`) and the engine blends between the recorded
pitches. The keyboard network fits a piano's whole keyboard at once: one small
network gives, for any piano, key, velocity layer and partial, the figures the
engine plays. It learns what pianos share from every library in its settings,
and what makes each piano itself from a short code per piano. It runs offline
only. The recordings are the benchmark: the network is fitted to all of them as
a whole and never to one note.

This is an experiment. The engine still plays today's tables. Writing tables
from the network, and the engine change to 88 recorded pitches that they need,
come after the cross-validation below; nothing here changes the instrument.

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

Steps still to come: the table writer, which turns a fit's weights into the
engine's tables at all 88 keys; the engine change to 88 recorded pitches; the
neighbour check, the recording benchmarks and the held-out cases; and the
keyed A/B between today's tables and both settings.

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
not compare. Until the table writer turns a fit into tables the engine plays,
compare a network's train figures with today's tables in closed form
(`baseline`), and each with its own dev figures.

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
- a network starts the same whatever trained before it in the process, and a
  short run learns a synthetic keyboard;
- the settings name every piano and library, and the train and dev takes keep
  their roles in each locked split, with no sealed take read.

It takes about ten seconds. `all` runs it first. CTest runs it as
`Keyra.KeyboardNetwork` (label `unit`) in a build configured with
`-DKEYRA_ENABLE_NETWORK_TESTS=ON`, which needs NumPy, SciPy and PyTorch; CI
does not install PyTorch, so the option is off by default. `check` (step 3
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
alone.
