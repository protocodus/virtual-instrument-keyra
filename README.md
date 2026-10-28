# Keyra

Keyra is a sample-free piano, a grand or an upright: a real-time modal engine
whose strings, soundboard ring and stereo image are fitted from numerical
measurements of acoustic piano recordings, with three visible pedals,
momentary pedal keyswitches and felt muting from the modulation wheel. It
builds as VST3 and CLAP plug-ins, an Audio Unit on macOS and a standalone
application, and the Reason Rack Extension adapter plays the same engine's
grand. It is a development candidate: host acceptance and a commercial release
are still to come.

![Keyra](Docs/screenshots/keyra.png)

## Audio demos

One phrase per factory preset, written for what that preset is for and
rendered from `Docs/audio/midi/` through the shipping engine.

<!-- audio-demos-begin -->

| # | Preset | Demo | Length | Peak |
| --- | --- | --- | --- | --- |
| 1 | Concert Grand | [01-concert-grand.wav](Docs/audio/01-concert-grand.wav) | 11.2 s | -11.6 dBFS |
| 2 | Studio Grand | [02-studio-grand.wav](Docs/audio/02-studio-grand.wav) | 11.6 s | -16.0 dBFS |
| 3 | Warm Walnut | [03-warm-walnut.wav](Docs/audio/03-warm-walnut.wav) | 11.1 s | -21.7 dBFS |
| 4 | Felt Nocturne | [04-felt-nocturne.wav](Docs/audio/04-felt-nocturne.wav) | 10.7 s | -22.9 dBFS |
| 5 | Open Strings | [05-open-strings.wav](Docs/audio/05-open-strings.wav) | 11.7 s | -13.3 dBFS |
| 6 | Rehearsal Upright | [06-rehearsal-upright.wav](Docs/audio/06-rehearsal-upright.wav) | 11.6 s | -20.7 dBFS |
| 7 | Felt Upright | [07-felt-upright.wav](Docs/audio/07-felt-upright.wav) | 10.4 s | -32.0 dBFS |
| 8 | Pop Upright | [08-pop-upright.wav](Docs/audio/08-pop-upright.wav) | 11.6 s | -18.1 dBFS |

<!-- audio-demos-end -->

### Listening against the recordings

The [recording comparisons](Docs/audio/recording-comparisons/2026-10-26/README.md)
play a real Salamander Grand note, the first fit and the current fit in turn,
level-matched. The [live renders](Docs/audio/live/manifest.json) are earlier
musical passages through the same engine. Both are frozen evidence from
0.2.0's review.

## Version history

### Unreleased — 0.4.1 — measured strings, body and board noise

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
  between them, 48 at A0 and a few or none from C4 up, and sets ringing every
  undamped string from F6 up but its own key's, each at its own measured
  pitch, decay and stereo position, at the level the recorded pitches around
  the key set it. They ring on after the key is let go.
- Letting a key go knocks the body as its damper lands, and the sustain pedal
  knocks it going down and coming up, synthesized on the body's modes: each
  mode's level and phase is measured from the library's release and pedal
  recordings, and the knocks sit against the notes as the library's SFZ mixes
  them, since the recordings carry no level of their own.
- Existing sessions sound different; the median note keeps 0.3.0's level. On
  the 156 never-fitted cases of the [recording benchmark](Docs/validation/recording-benchmark-split-2026-10-27.md),
  partial levels sit 3.1 dB from the recordings (0.3.0: 9.3 dB), the attack
  spectrum 4.2 dB (15.8 dB), the sustain spectrum 4.7 dB (10.2 dB) and the
  noise between partials 5.8 dB (25.9 dB); its regressions, C4's onset rise
  and D♯1's tuning first, are listed there.
- Adds an upright beside the grand, chosen with the new Piano control and
  three presets (Rehearsal Upright, Felt Upright, Pop Upright): a 1967
  upright with worn hammers in a dry room, measured the grand's way from 137
  recordings of the Helsinki 1967 Tube-Ribbon Edition (Mikko Patama, with his
  permission; none of its recordings is distributed). Switching silences what
  sounds; sessions saved before keep the grand. On the
  [upright's benchmark](Docs/validation/upright-recording-benchmark-2026-10-28.md)
  its attack, tuning and level sit closer to its never-fitted recordings than
  the grand's data does; its treble does not yet (Known gaps). From C6 up it
  now plays the unison strings that sound further from their partial than its
  lanes reach: its first fit took them for the partial's own and left them
  out, so its treble tails fell too fast. On the never-fitted E6 the partials
  sit 7.7 dB from the recordings instead of 8.9 and the sustain spectrum
  12.4 dB instead of 15.1
  ([unisons](Docs/validation/upright-unison-benchmark-2026-10-28.md)); the
  grand gains such a string at F♯6, A6 and C7. Its dampers
  leave ringing what the library's key-release takes show, a share of each
  partial that fades over seconds once the felt lands, 13 dB down at middle
  C and less higher up: on the never-fitted takes its releases sit 6.3 dB
  from the recordings, where the grand's felt left them 8.4 dB
  ([release benchmark](Docs/validation/upright-release-benchmark-2026-10-28.md)).
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
**[Download main build 7](https://github.com/protocodus/virtual-instrument-keyra/actions/runs/40710782336/artifacts/12827605353)**, built from [`a96097a8d466`](https://github.com/protocodus/virtual-instrument-keyra/commit/a96097a8d46690f5616da03545a2422c629b8d0e). It holds the macOS, Windows and Linux packages, `SHA256SUMS` and `BUILD.txt`.
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
the partials, each one lane placed by the series and damped with it; in the
treble they include the unison strings that sound further from their partial
than its lanes reach. They
start at contact under the pitch's onset rise and share vectors four lanes to
a slot, so a component costs a quarter of a partial.

Every strike also knocks the body: a bank of 91 soundboard and case modes from
29 to 945 Hz, shared by every key, which rings for half a second to a second,
with the level, phase and velocity response measured for each recorded pitch.
Above the modes, the board's dense ring is band noise in 13 third-octave bands
from 1 to 16 kHz, each a sixth-order band-pass so that the quiet top octaves
keep their measured level: each strike starts its own burst with the density,
decay and left/right balance measured for its pitch. A shared bank of 88 open-string
resonators supplies the sympathetic response the Resonance control sets. Its
top twenty are the undamped strings from F6 up, which every strike sets
ringing whatever that control: each but the struck key's own, at the level the
recorded pitches around the key set it, and each at its own measured pitch,
decay and stereo pickup whichever key struck it. They ring on after the key is
let go; the felt mute damps them.

The action knocks the same modes. A key let go knocks them as its damper lands,
building up over the 54 ms the release recordings show rather than clicking,
and quieter the longer the key was held; under the sustain pedal or sostenuto
no damper falls and the key-up is silent, while from F6 up, where there is
no damper, the key's own return knocks them whatever the pedals do. The
sustain pedal knocks them going down and coming up.

### Calibration from recordings

`Source/DSP/MeasuredModalData.h` is generated by `Tools/fit_realtime_modal.py`
from the train role of a locked split of the Salamander Grand Piano V3
(`Tools/corpus/split-2026-10-27.json`, fetched and verified by
`Tools/fetch_salamander.py`): every A, C and F♯ from A0 to A7 at twelve
velocity layers, 264 recordings. Each partial is fitted jointly across its
pitch's layers (`Tools/piano_analysis.py`), the lanes' rates shared and their
levels and phases per layer, every moment of its decay weighed relative to its
level down to the recording's floor; in a layer where it does not stand clear
of that floor, it is no louder than its recorded peak there. The layers'
contact times are aligned so that the phases form one pattern across the
partials, and a pitch's onset rise follows one line over velocity, held within
the range its layers measure. Beside the series, the
residual's peaks that four or more layers share are measured each through a
window just long enough to part it from its nearest neighbour, from 30 ms to 2
s, and fitted with one lane from contact; one within 3.5 cents of another
key's undamped string is that string. The undamped strings are measured as
tones from F♯3 up, below which the struck key's series covers their pitches:
through half-second windows from 1 to 2 s after contact, both channels' power
at the strongest bin within 1 Hz of a string's pitch, where it stands 10 dB
over the median 4–20 Hz either side and 10 Hz from every partial of the
struck key.
A string's pitch is the median of its strongest peak in the recordings from C6
up; its stereo pickup the median level difference and mean phase between the
channels; its decay its fall from 1 to 2 s, drawn towards the strings' median;
its level at a recorded pitch the mean over the layers where it rings clear,
brought back to contact, or 10 dB under the tone where the noise hides it, with
one velocity slope for every string. The body modes are found below the
treble's fundamentals, where no string sounds; the board noise is measured in
the gaps between the partials the recordings show and, above the highest of
them, across whole bands, as the benchmark measures it. The action's knocks are
measured from each recorded pitch's key-release take and the sustain pedal's
two: a level and phase per mode at the knock's onset, fitted on the same modes
under one rise they share; the recordings were gained up as a set, so their
level against the notes is the library's SFZ mix (a release at −37 dB tracking
velocity and 2 dB quieter for each second held, the pedal at −20 dB down and
−19 dB up), not a measurement. A strike interpolates between the recorded
pitches by partial order and between the layers by velocity, taking phases from
the nearer pitch; a partial's stereo pickup moves between the two pitches'
channel level and phase differences. C8 is left out: its strongest components
sit 90–100 cents above the stretch that F♯7 and A7 set and no partial series
explains the recording, so the keys above A7 play A7's data on the stretch
curve. Only fitted numbers enter the header; no recorded waveform or impulse
response is loaded.

The upright's `Source/DSP/MeasuredUprightData.h` comes from the same tool
(`--model upright`) and the train role of
`Tools/corpus/split-helsinki-2026-10-28.json`: 28 pitches from C1 to G7 at the
library's five velocity layers (four at A♯3, E7 and G7), one take each, and the
hammer noise the library plays as each of those keys is let go
(`Tools/decode_helsinki.py` verifies a copy of the library against its pins).
Each layer is measured at the middle of its velocity range. The takes are cut
at the strike, so a band's noise floor is read at a take's end, and the frames
that would start before a take are left out. The library mixes the hammer
noises at a fixed −14 dB against the notes, whatever the velocity or how long
the key was held, and so do the upright's release knocks. Its key-release
takes, each a note dying under its damper from about the key-up, set what the
dampers leave ringing: below F6, each train take's partials to the tenth that
stand clear of its floor and of the undamped strings' partials, fitted under
the engine's own damper as a share the felt takes at its loss and a share it
holds loosely, each linear in octaves, with a key-up per take and a level per
partial, as the takes carry no level against the notes
([dampers](Docs/research/upright-dampers-2026-10-28.md)). It has no pedal
recordings, so the upright's pedals make no sound of their own; no take shows
the 16 kHz band's noise in three layers, so that band is silent. Its 21 dev
recordings, never fitted, are the first takes of D♯2, G♯3, C5 and E6 and B3's
one take; F♯1, E4 and G♯5 stay sealed. The library's second take of a note
repeats its first: 126 of the 143 share its hammer noise, nine in ten of those
within 0.15 cents of it (`Tools/find_repeated_takes.py`), so no second take is
fitted or scored.

`Tools/benchmark_recordings.py` scores a renderer against every train and dev
recording. The dev recordings, D♯1, D♯3, D♯5 and D♯7 at every layer and four
other layers of every calibrated pitch, are never fitted; D♯2, D♯4 and D♯6
stay sealed until a candidate goes to the owner. `Tools/compare_benchmarks.py`
lists every note where a candidate is worse than the shipping engine. The [current report](Docs/validation/recording-benchmark-split-2026-10-27.md)
compares this engine with 0.3.0; the [upright's](Docs/validation/upright-recording-benchmark-2026-10-28.md)
scores the upright on its own recordings against the grand's data played on
them. `Tools/benchmark_releases.py` scores the upright's key releases against
its train and dev key-release takes ([report](Docs/validation/upright-release-benchmark-2026-10-28.md)).

### Pedals and keyswitches

Sustain lifts the dampers continuously, so half pedalling damps part way.
Sostenuto captures the keys held as it crosses halfway down and holds only
those. Soft lowers the level and the high-partial excitation of later strikes.
Each pedal takes the largest of its panel control, its MIDI controller (CC64,
CC66, CC67) and its momentary keyswitch (MIDI 14, 13, 12, below the piano's
A0). The top twenty keys have no dampers, as on a grand. A damper's felt
takes a partial down faster the higher it sounds, a released C4 at about
500 dB/s. The upright's holds a share of each partial only loosely, as its
release recordings show, so a released note fades over seconds: 13 dB under
the partial at middle C, less higher up, and all of the fundamentals up to
C♯2. The felt mute (CC1
or its control) adds damping to sounding notes, held ones included. The
sustain pedal sounds within 0.08 of either end of its travel, once each way,
from whichever of its sources moves it; half pedalling between is silent, and
a reset of the controllers lifts it without a sound.

### Controls, presets and MIDI

Piano, Output, Brightness, Resonance, Width, Tuning, Felt mute and the three
pedals are the ten saved parameters; Piano is not offered for automation, as
switching silences what sounds, and a session saved before it existed plays
the grand. The eight factory presets in `Source/DSP/KeyraPresets.h`, five on
the grand and three on the upright, set the piano, Brightness, Resonance,
Width and Felt mute and leave the rest alone. Notes, pedals and pitch bend
(two semitones each way) are dispatched at their sample positions; each MIDI
channel owns its keys and pedals, and CC120, CC121 and CC123 are honoured per
channel. The [user guide](Docs/guide/user-guide.md) describes every control.

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
  do not document pedal positions or timings. The release and pedal knocks
  play at the library's mix, not a measured level, and only as far as the
  body's modes hold them: 26 to 67 % of each recorded knock below 1 kHz, and
  all of it above, is left out, so a released C4 knocks 4 to 5 dB under the
  library's balance ([release recordings](Docs/research/release-recordings-2026-10-27.md)).
  The room is not calibrated, and the key noise the recordings carry 1 to
  28 ms before string contact is not played: a note sounds from contact.
- Between the recorded pitches, partials, phases and stereo pickups are
  interpolated by partial order. The microphones' left/right balance changes
  sharply with frequency, so at D♯3 the image is still further from the
  recording than 0.3.0's fixed panning was (6.9 dB against 4.7 dB).
- From C6 up, the partials' decay after half a second is 4.5 dB/s from the
  recordings' on the dev cases (0.3.0: 6.7 dB/s), but at A7 it is 1 to 2 dB/s
  further than 0.3.0's. Each undamped key rings as one string at one pitch,
  without its unison's beating, and falls at its rate from 1 to 2 s
  throughout, where the real strings fall faster at first and more slowly
  later: on the dev cases the strings that ring clear sit a median 1.6 dB
  over the recordings at 1 s and 1.5 dB under at 3 s, when 9 % of them are
  10 dB or more under. Where a recorded pitch's own partials cover a string,
  its level there is interpolated from the pitches around it; below F♯3 each
  string keeps the level of the lowest pitch that measured it.
  From F♯3 to F♯5 the first seconds of the sustain sit up to 1 dB further from
  the recordings (4 dB at D♯5) than under a fit weighted towards them, as a
  long note's tail now counts as much.
- C8 is not calibrated (above). Below A3 the partials leave too few gaps to
  measure the board noise in six to ten of the thirteen bands; those bands are
  interpolated between the nearest pitches that measured them.
- Every recording of each piano is from one instrument and one session, so
  the holdout does not establish how the fit generalises to another
  instrument.
- The upright's soft pedal is the grand's: it lowers the level and the high
  partials and moves energy to the slowest lane as an una corda does, where an
  upright's moves the hammers closer to the strings. Its pedals are silent
  (above). Its dampers all land alike, where from C1 to F♯2 the felt reaches
  the strings 0.1 to 0.3 s later into the release takes than elsewhere,
  whether those takes start earlier or those dampers land more slowly. Where a
  damped partial lies on an undamped string, the takes hold that string
  ringing far louder than the halo plays it, its level being interpolated
  there (above): the never-fitted C5's third partial, 4 cents from G6's
  string, now releases 6.6 dB from its take, where it was 3.5 dB with the
  felt taking all of it ([dampers](Docs/research/upright-dampers-2026-10-28.md)).
- The upright's treble is fitted worse than its middle. From C6 up its unison
  strings sound 6 to 20 cents apart (the grand's top octave up to 12). A
  partial's lanes hold those within about 3 cents of it; each one further out
  plays as a component beside it, which has no rise of its own and takes the
  pitch's shortest, so the fit lengthens that for every partial: D6's is now
  20 ms, where it was 0.2 ms
  ([unisons](Docs/validation/upright-unison-benchmark-2026-10-28.md)).
  At the never-fitted E6, between the recorded pitches, the partials sit
  7.7 dB from the recording and their decay 12.3 dB/s from its, where the
  middle register's sit 5.7 dB and 3.3 dB/s. Its noise between partials
  scores 9 to 10 dB, most of it above 6 kHz the recordings' own steady floor,
  which that score does not part from the piano's noise.
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
purpose, commercial music included. The grand's reference recordings are
Salamander Grand Piano V3 by Alexander Holm under CC BY 3.0; the upright's are
the Helsinki 1967 Tube-Ribbon Edition by Mikko Patama, whose author permits
fitting numbers from them provided the recordings are not distributed. JUCE,
CLAP and the other dependencies keep their own licences.
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) lists them, with the licence
texts in `ThirdParty/`. The licensed Reason Jukebox SDK is not part of this
repository.
