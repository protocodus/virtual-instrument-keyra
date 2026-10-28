# Keyra

Keyra is a sample-free grand piano: a real-time modal engine whose strings,
soundboard ring and stereo image are fitted from numerical measurements of
acoustic piano recordings, with three visible pedals, momentary pedal
keyswitches and felt muting from the modulation wheel. It builds as VST3 and
CLAP plug-ins, an Audio Unit on macOS and a standalone application, and the
Reason Rack Extension adapter plays the same engine. It is a development
candidate: host acceptance and a commercial release are still to come.

![Keyra](Docs/screenshots/keyra.png)

## Audio demos

One phrase per factory preset, written for what that preset is for and
rendered from `Docs/audio/midi/` through the shipping engine.

<!-- audio-demos-begin -->

| # | Preset | Demo | Length | Peak |
| --- | --- | --- | --- | --- |
| 1 | Concert Grand | [01-concert-grand.wav](Docs/audio/01-concert-grand.wav) | 11.2 s | -8.6 dBFS |
| 2 | Studio Grand | [02-studio-grand.wav](Docs/audio/02-studio-grand.wav) | 11.6 s | -8.9 dBFS |
| 3 | Warm Walnut | [03-warm-walnut.wav](Docs/audio/03-warm-walnut.wav) | 11.1 s | -19.8 dBFS |
| 4 | Felt Nocturne | [04-felt-nocturne.wav](Docs/audio/04-felt-nocturne.wav) | 10.7 s | -17.8 dBFS |
| 5 | Open Strings | [05-open-strings.wav](Docs/audio/05-open-strings.wav) | 11.7 s | -12.6 dBFS |

<!-- audio-demos-end -->

### Listening against the recordings

The [recording comparisons](Docs/audio/recording-comparisons/2026-10-26/README.md)
play a real Salamander Grand note, the first fit and the current fit in turn,
level-matched. The [live renders](Docs/audio/live/manifest.json) are earlier
musical passages through the same engine. Both are frozen evidence from
0.2.0's review.

## Version history

### Unreleased — 0.4.0 — measured strings, body and board noise

- Recalibrated from 264 recordings (every A, C and F♯ from A0 to A7 at twelve
  velocities) instead of ten. Each partial has four measured decay lanes with
  their own beating and left/right balance, starts from the phase pattern the
  recordings show at string contact and rises no faster than its pitch's
  recorded onset.
- Every strike knocks a body of 91 measured soundboard and case modes and
  starts a burst of board noise in 13 bands, measured for its pitch, so
  repeated notes differ as real strikes do. The felt mute damps the strings,
  not this ring, which dies within a second.
- Beside its partials, a strike plays the components the recordings hold
  between them, 51 at A0 and a few or none from C4 up, and sets ringing the
  undamped strings from F6 up that its pitch is heard to excite (22 strings):
  each falls fast at first and then rings on more slowly, and goes on ringing
  after the key is let go.
- Existing sessions sound different; the median note keeps 0.3.0's level. On
  the 156 never-fitted cases of the [recording benchmark](Docs/validation/recording-benchmark-split-2026-10-27.md),
  partial levels sit 3.1 dB from the recordings (0.3.0: 9.3 dB), the attack
  spectrum 4.2 dB (15.8 dB), the sustain spectrum 4.9 dB (10.2 dB) and the
  noise between partials 5.8 dB (25.9 dB); its regressions, C4's onset rise
  and D♯1's tuning first, are listed there.
- Adds the CLAP plug-in on every platform beside VST3, the standalone
  application and, on macOS, the Audio Unit.
- The repository root is the product only. The full physical piano research
  moved to [`Experiments/`](Experiments/README.md), its own CMake project that
  the product build does not build.

### 0.2.0 — 2026-10-26 — native instrument

- The real-time modal piano with five presets, three visible pedals,
  momentary pedal keyswitches on MIDI 12–14, continuous pedal depth and
  modulation-wheel felt muting, as a VST3 plug-in and a standalone
  application. Details are in the
  [native wrapper validation](Docs/validation/native-wrapper-2026-10-26.md).

## Downloads

<!-- build-download-begin -->
**[Download main build 3](https://github.com/protocodus/virtual-instrument-keyra/actions/runs/40471972512/artifacts/12722636207)**, built from [`3beb98d283cd`](https://github.com/protocodus/virtual-instrument-keyra/commit/3beb98d283cd346890a8b52f0ca297da40a7c49c). It holds the macOS, Windows and Linux packages, `SHA256SUMS` and `BUILD.txt`.
<!-- build-download-end -->

---

## How it works

### The modal engine

`Source/DSP/KeyraEngine` is front-end-neutral C++17 with no allocation, I/O or
locks in its event and render calls; the plug-in and the Rack adapter both
compile it. Each struck key becomes one voice of up to 128 stiff-string
partials (128 voices; when they run out, a released tail goes before the
oldest held note). Every partial has four lanes, each a decaying rotation with
its own rate, small frequency offset and stereo pickup: together they make a
note's prompt fall, the beating of its unison strings, its slow aftersound and
the way its balance moves between the microphones. A partial starts from the
phase the recordings show at string contact and rises from zero, never faster
than its pitch's recorded onset builds up. The lanes run four to a 128-bit
vector in single precision, restarted every 32 samples from a double-precision
state, so long notes keep their exact decay.

Beside its series, a strike plays the components the recordings hold between
the partials, each one lane placed by the series and damped with it, and sets
ringing the undamped strings from F6 up that its pitch is heard to excite.
Those ring at their own pitches whichever key struck them, and on after the
key is let go, each with two lanes: a fast first fall and a slower ring. All
start at contact under the pitch's onset rise and share vectors four lanes to
a slot, so a component costs a quarter of a partial and a string half of one.

Every strike also knocks the body: a bank of 91 soundboard and case modes from
29 to 945 Hz, shared by every key, which rings for half a second to a second,
with the level, phase and velocity response measured for each recorded pitch.
Above the modes, the board's dense ring is band noise in 13 third-octave bands
from 1 to 16 kHz, each a sixth-order band-pass so that the quiet top octaves
keep their measured level: each strike starts its own burst with the density,
decay and left/right balance measured for its pitch. A shared bank of 88 open-string
resonators supplies the sympathetic response the Resonance control sets.

### Calibration from recordings

`Source/DSP/MeasuredModalData.h` is generated by `Tools/fit_realtime_modal.py`
from the train role of a locked split of the Salamander Grand Piano V3
(`Tools/corpus/split-2026-10-27.json`, fetched and verified by
`Tools/fetch_salamander.py`): every A, C and F♯ from A0 to A7 at twelve
velocity layers, 264 recordings. Each partial is fitted jointly across its
pitch's layers (`Tools/piano_analysis.py`), the lanes' rates shared and their
levels and phases per layer, every moment of its decay weighed relative to its
level down to the recording's floor; the layers' contact times are aligned so
that the phases form one pattern across the partials. Beside the series, the
residual's peaks that four or more layers share are measured each through a
window just long enough to part it from its nearest neighbour, from 30 ms to
2 s, and fitted with one lane from contact. A peak from F6 up that recurs
within 1.5 cents across four or more recorded pitches is an undamped string
ringing (22 such strings, where the same peaks shifted at random form about
three), fitted with two lanes. Its window also holds the board's noise around
a faint string, which a slower lane can take for the string ringing on, so the
string's tone (its largest amplitude within 2 Hz through half-second windows
from 1 to 3.5 s) times and levels the slower lane where it stands 10 dB clear
of the noise either side, as it does at 67 of the 103 recorded pitches that
ring a string; elsewhere no lane decays more slowly than the string's median,
and the two lanes never stand over the tone. The body modes are found below the treble's fundamentals, where no
string sounds; the board noise is
measured in the gaps between the partials the recordings show and, above the
highest of them, across whole bands, as the benchmark measures it. A strike
interpolates between the recorded pitches by partial order and between the
layers by velocity, taking phases from the nearer pitch; a partial's stereo
pickup moves between the two pitches' channel level and phase differences. C8 is left out: its
strongest components sit 90–100 cents above the stretch that F♯7 and A7 set
and no partial series explains the recording, so the keys above A7 play A7's
data on the stretch curve. Only fitted numbers enter the header; no recorded
waveform or impulse response is loaded.

`Tools/benchmark_recordings.py` scores a renderer against every train and dev
recording. The dev recordings, D♯1, D♯3, D♯5 and D♯7 at every layer and four
other layers of every calibrated pitch, are never fitted; D♯2, D♯4 and D♯6
stay sealed until a candidate goes to the owner. `Tools/compare_benchmarks.py`
lists every note where a candidate is worse than the shipping engine. The [current report](Docs/validation/recording-benchmark-split-2026-10-27.md)
compares this engine with 0.3.0.

### Pedals and keyswitches

Sustain lifts the dampers continuously, so half pedalling damps part way.
Sostenuto captures the keys held as it crosses halfway down and holds only
those. Soft lowers the level and the high-partial excitation of later strikes.
Each pedal takes the largest of its panel control, its MIDI controller (CC64,
CC66, CC67) and its momentary keyswitch (MIDI 14, 13, 12, below the piano's
A0). The top twenty keys have no dampers, as on a grand. The felt mute (CC1
or its control) adds damping to sounding notes, held ones included.

### Controls, presets and MIDI

Output, Brightness, Resonance, Width, Tuning, Felt mute and the three pedals
are the nine saved parameters. The five factory presets in
`Source/DSP/KeyraPresets.h` set Brightness, Resonance, Width and Felt mute and
leave the rest alone. Notes, pedals and pitch bend (two semitones each way)
are dispatched at their sample positions; each MIDI channel owns its keys and
pedals, and CC120, CC121 and CC123 are honoured per channel. The
[user guide](Docs/guide/user-guide.md) describes every control.

### The full physical research

[`Experiments/`](Experiments/README.md) holds the preserved nonlinear
reference solver, the full physical block API, its calibration against the
full-range corpus and the module research behind them. It is the direction the
product's sound is meant to move towards, and none of it is in the plug-in.

## Known gaps

- The modal engine does not model nonlinear hammer contact or a reciprocal
  soundboard; the full physical model in `Experiments/` does, but it is several
  times slower than real time.
- Pedal behaviour is not validated against recordings: the training recordings
  do not document pedal positions or timings. Key and damper noises and the
  room are not calibrated ([release recordings](Docs/research/release-recordings-2026-10-27.md)),
  and the key and action noise the recordings carry 1 to 28 ms before string
  contact is not played: a note sounds from contact.
- Between the recorded pitches, partials, phases and stereo pickups are
  interpolated by partial order. The microphones' left/right balance changes
  sharply with frequency, so at D♯3 the image is still further from the
  recording than 0.3.0's fixed panning was (6.9 dB against 4.7 dB).
- From C6 up, the partials' decay after half a second is 4.6 dB/s from the
  recordings' on the dev cases (0.3.0: 6.7 dB/s), but at A7 it is 1 to 2 dB/s
  further than 0.3.0's. Between the recorded pitches a key rings the undamped
  strings either neighbour lists, faded towards the other; where its own
  partials pass far from them, as at D♯3 and D♯5, they stand 20 dB or more
  over the recordings after 2 s (4.6 % of the strings the dev cases ring).
  From F♯3 to F♯5 the first seconds of the sustain sit up to 1 dB further from
  the recordings (4 dB at D♯5) than under a fit weighted towards them, as a
  long note's tail now counts as much.
- C8 is not calibrated (above). Below A3 the partials leave too few gaps to
  measure the board noise in six to ten of the thirteen bands; those bands are
  interpolated between the nearest pitches that measured them.
- Every recording is from one piano and one session, so the holdout does not
  establish how the fit generalises to another instrument.
- Only Linux VST3 and standalone builds have been validated
  ([pluginval](Docs/validation/pluginval-2026-10-26.txt)); CLAP, the Audio Unit,
  macOS, Windows and Reason are built by CI but not yet accepted in a host.
- The [production target](Docs/plans/production-readiness.md) lists the
  evidence a commercial release still needs.

## Build

The JUCE-free engine, tests and demo renderer (`build-dsp`):

```bash
cmake -S . -B build-dsp -DCMAKE_BUILD_TYPE=Release -DKEYRA_BUILD_PLUGIN=OFF -DBUILD_TESTING=ON
cmake --build build-dsp --parallel && ctest --test-dir build-dsp --output-on-failure
./build-dsp/RenderKeyraPresetDemos Docs/audio/midi build-dsp/demos   # WAVs + demos.json
```

The full plug-in (`build-plugin`). JUCE 8.0.14 and clap-juce-extensions are
fetched pinned at configure time; pass `-DKEYRA_JUCE_PATH=/path/to/JUCE` or
`-DKEYRA_CLAP_JUCE_EXTENSIONS_PATH=/path/to/clap-juce-extensions` to use local
checkouts, or `-DKEYRA_BUILD_CLAP=OFF` to skip CLAP:

```bash
cmake -S . -B build-plugin -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=ON
cmake --build build-plugin --parallel && ctest --test-dir build-plugin --output-on-failure
```

Every test carries one tier label, so `ctest -L unit`, `-L audio`, `-L render`
or `-L fuzz` selects a tier. `KeyraDSPCxx17` compiles the engine as C++17,
the Rack Extension toolchain's standard. `-DKEYRA_ENABLE_SANITIZERS=ON` builds
everything under ASan and UBSan, and `-DKEYRA_BUILD_LIBFUZZER=ON` (Clang) makes
`KeyraDspFuzz` a libFuzzer target.

On macOS, `./scripts/build-macos.sh` drives the same build through Xcode as a
universal binary and `./scripts/sign-and-package-macos.sh` packages it. On
Linux and Windows, `scripts/package-linux.py` and `scripts/package-windows.py`
package a `build-plugin` tree.

Three workflows run in CI: `ci.yml` on every push to any branch (tiers per
platform, sanitizers and the experiments), `main-build.yml` on every push to
`main` and nightly (pluginval and auval, the collected download, and the
committed screenshot, demos and README blocks), and `release.yml` on `v*` tags.

The research in `Experiments/` is configured on its own:
`cmake -S Experiments -B Experiments/build`.

## Licensing

Keyra's source is available under the [PolyForm Noncommercial License
1.0.0](LICENSE), with an additional permission to use official builds for any
purpose, commercial music included. The reference recordings are Salamander
Grand Piano V3 by Alexander Holm under CC BY 3.0; JUCE, CLAP and the other
dependencies keep their own licences. [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)
lists them, with the licence texts in `ThirdParty/`. The licensed Reason
Jukebox SDK is not part of this repository.
