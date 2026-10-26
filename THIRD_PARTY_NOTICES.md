# Third-party notices

## Acoustic reference and numerical calibration

Salamander Grand Piano V3 recordings are by **Alexander Holm**, licensed under
[Creative Commons Attribution 3.0 Unported](https://creativecommons.org/licenses/by/3.0/).
The pinned upstream source, original metadata, license and modification record
are retained under `Research/GrandPianoV2/reference/`. See
[ATTRIBUTION.md](Research/GrandPianoV2/reference/ATTRIBUTION.md) and
[LICENSE-CC-BY-3.0.txt](Research/GrandPianoV2/reference/upstream/LICENSE-CC-BY-3.0.txt).

Keyra measures these recordings and derives numerical spectral, attack, decay
and tuning parameters. The synthesizer generates sound from those parameters;
it does not load recorded note waveforms or impulse responses. This attribution
does not imply endorsement by the recording author or instrument maker.

## Optional DAW wrapper

The optional DAW plug-in and standalone application use JUCE. Its retained
license is in `ThirdParty/JUCE-LICENSE.md`; JUCE's applicable distribution terms
are separate from the acoustic recordings' license. The SDK-free DSP and
offline renderer do not require JUCE.

The native editor's material and control artwork is authored vector code.
`Assets/Brand/` retains the official Protocodus logo from the portfolio's brand
assets. `Assets/Fonts/LiberationSans-Bold.ttf` is Liberation Sans 2.1.5, used
to rasterize the Shop thumbnail; its SIL Open Font License 1.1 is retained in
`Assets/Fonts/OFL-Liberation-Sans.txt`. This font is not embedded in the audio
engine or DAW plug-in; the editor uses JUCE's system font facilities.

## Reason wrapper

The Rack Extension adapter is maintained in the separate
`protocodus/reason-rack-extensions` repository. The licensed Reason Studios
Jukebox SDK is a developer-supplied build dependency and is not redistributed
with Keyra source.
