# Third-party notices

## Acoustic reference and numerical calibration

Salamander Grand Piano V3 recordings are by **Alexander Holm**, licensed under
[Creative Commons Attribution 3.0 Unported](https://creativecommons.org/licenses/by/3.0/).
The pinned upstream source, original metadata, license and modification record
are retained under `Experiments/Research/GrandPianoV2/reference/`. See
[ATTRIBUTION.md](Experiments/Research/GrandPianoV2/reference/ATTRIBUTION.md) and
[LICENSE-CC-BY-3.0.txt](Experiments/Research/GrandPianoV2/reference/upstream/LICENSE-CC-BY-3.0.txt).

Keyra measures these recordings and derives numerical spectral, attack, decay
and tuning parameters. The synthesizer generates sound from those parameters;
it does not load recorded note waveforms or impulse responses. This attribution
does not imply endorsement by the recording author or instrument maker.

## JUCE 8.0.14

The DAW plug-in and standalone application use JUCE, Copyright (c) Raw
Material Software Limited, pinned to
<https://github.com/juce-framework/JUCE/tree/8.0.14>. Its licence is retained
in [`ThirdParty/JUCE-LICENSE.md`](ThirdParty/JUCE-LICENSE.md); JUCE's
distribution terms are separate from the acoustic recordings' licence. JUCE
modules are dual-licensed under the AGPLv3 and the commercial JUCE licence, so
distributing a build requires either AGPLv3 compliance for the combined work or
a commercial JUCE licence. Protocodus's official builds use JUCE under a
commercial JUCE 8 Starter licence. The SDK-free DSP and offline renderer do not
require JUCE.

The licence texts of the components JUCE bundles are collected in
[`ThirdParty/JUCE-DEPENDENCY-NOTICES.txt`](ThirdParty/JUCE-DEPENDENCY-NOTICES.txt),
with upstream paths and hashes, regenerated from the pinned checkout by
`Tools/collect_juce_notices.py`. Apple's Audio Unit frameworks are supplied by
the macOS SDK and remain subject to Apple's terms.

## CLAP support

The CLAP plug-in uses the MIT-licensed `clap-juce-extensions` wrapper, pinned
to commit `c1a5ad025f95d01e03267857fa8276ebeed16500`:
<https://github.com/free-audio/clap-juce-extensions/tree/c1a5ad025f95d01e03267857fa8276ebeed16500>.
It is Copyright 2019-2020, Paul Walker. The complete upstream licence is
included in [`ThirdParty/CLAP-JUCE-EXTENSIONS-LICENSE.md`](ThirdParty/CLAP-JUCE-EXTENSIONS-LICENSE.md).

The wrapper brings in two dependencies at the revisions recorded by its
submodules:

- CLAP 1.2.7, commit `29ffcc273be7c7c651f6c9953b99e69700e2387a`:
  <https://github.com/free-audio/clap/tree/29ffcc273be7c7c651f6c9953b99e69700e2387a>.
  Its MIT licence is included in [`ThirdParty/CLAP-LICENSE.md`](ThirdParty/CLAP-LICENSE.md).
- CLAP helpers, commit `a61bcdf0ecc2c8db1e80bfe8bf9cb7e8d9fd2bbc`:
  <https://github.com/free-audio/clap-helpers/tree/a61bcdf0ecc2c8db1e80bfe8bf9cb7e8d9fd2bbc>.
  Its MIT licence is included in [`ThirdParty/CLAP-HELPERS-LICENSE.md`](ThirdParty/CLAP-HELPERS-LICENSE.md).

Both dependencies are Copyright (c) 2021 Alexandre BIQUE.

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
