# Full-range grand recording benchmark

This corpus supplies public **real acoustic piano recordings** for every C key
from C1 through C8, plus A0, the lowest key on an 88-key piano. C8 is the highest
key. Scientific pitch notation is used: C4 is MIDI 60.

The recordings are **Salamander Grand Piano V3 by Alexander Holm**, an acoustic
Yamaha C5, distributed under **CC BY 3.0**. This expands the existing pinned
corpus rather than introducing another recording chain or a synthesized target.

- [Pinned source repository](https://github.com/sfzinstruments/SalamanderGrandPiano/tree/3382bf9496bba2486f5ab0de55a264d1dfc38404)
- [Original distribution](https://archive.org/details/SalamanderGrandPianoV3)
- [License](https://creativecommons.org/licenses/by/3.0/)
- [Local license copy](upstream/LICENSE-CC-BY-3.0.txt)
- [Pinned recording description](upstream/README.md)

Upstream describes 48 kHz/24-bit stereo recordings, 16 velocity layers and two
AKG C414 microphones in AB configuration approximately 12 cm above the strings.
Kinwie / sfzinstruments maintains the SFZ mapping and FLAC distribution. Actual
hammer speed, room, acquisition pedal position, key-release time and previous
editing/denoising are unknown. Separate source-library pedal, hammer-release and
string-resonance layers are not mixed into these main note files.

## Coverage and locked roles

The [split](split.json) and [lock receipt](split-lock.json) were written before
the eight new training recordings were downloaded or decoded. The split SHA256 is
`a00135a26fb0e9a95e1245d1f29d55c57da332d42510f1efb9adcbca36fd0428`.

| Key | MIDI | Training layers | Layer 8 evaluation status |
|---|---:|---|---|
| A0 | 21 | 4, 12 | Fresh reserved; not downloaded or decoded |
| C1 | 24 | 4, 12 | Previously observed edge regression |
| C2 | 36 | 4, 12 | Previously observed velocity regression |
| C3 | 48 | 4, 12 | Previously observed velocity regression |
| C4 | 60 | 4, 12 | Previously observed velocity regression |
| C5 | 72 | 4, 12 | Previously observed velocity regression |
| C6 | 84 | 4, 12 | Previously observed velocity regression |
| C7 | 96 | 4, 12 | Previously observed edge regression |
| C8 | 108 | 4, 12 | Fresh reserved; not downloaded or decoded |

The 27-case inventory therefore has **18 fitting cases, seven known regression
cases and two fresh reserved cases**. Ten C2–C6 training recordings and the seven
known evaluation files are reused with exact source identities. A0, C1, C7 and
C8 at layers 4/12 add eight new training recordings. Combining them with the
existing GrandExpanded TRAIN26 produces **TRAIN34 at 17 pitches**. None of the
evaluation files enters training or method selection.

Layers 4/8/12 map to model velocities **40/61/93**, the rounded midpoints of the
upstream SFZ playback bins 37–43, 57–64 and 89–96. These are playback proxies,
not known recording MIDI values or calibrated hammer speeds. No SFZ tuning,
optional sample offset, playback velocity scaling, room or release layer is
applied during acquisition.

## Identity, decoding and features

[upstream-file-identities.json](upstream-file-identities.json) records the pinned
Git blob SHA1 and size for all 27 source files. [manifest.json](manifest.json)
additionally pins the acquired 25 FLAC SHA256 hashes and signed PCM24 identities.
The two fresh layer-8 extremes retain metadata/Git-blob pins only. They stay
unopened until an explicit model freeze and subsequent evaluation.

Original FLACs remain byte-identical. WAVs are lossless PCM24 decodes at 48 kHz
stereo, without gain, trim, retuning, resampling, denoising, EQ, looping or padding.
The local `recordings/` and `downloads/` directories are ignored. No recorded
waveform is embedded in the synthesizer.

- [train_features.json](train_features.json): the 18 full-range fitting cases.
- [combined_train_features.json](combined_train_features.json): all 34 fitting
  cases, preserving the existing TRAIN26 rows and adding eight extremes.
- [training-quality.json](training-quality.json): training-only acquisition and
  spectral-support diagnostics.
- [verification.json](verification.json): acquisition/PCM verification receipt.

Existing TRAIN10 numerical measurements are reused unchanged. New rows use the
preserved benchmark's onset, stereo-power, pitch/partial, decay and attack
formulas. C1/C7 layers 4/12 explicitly receive their new locked training roles;
the old frozen split and its layer-8 edge roles remain unchanged.

## Extreme-register limits

All acquired source files are 48 kHz/24-bit stereo. The new training files span
**2.811–25.692 seconds**. C8v4 is only 2.810833 seconds long; after measured onset,
its final feature window is **1.5–2.808083 seconds**, and its envelope stops at
2.8 seconds. It is marked `right_censored`. Its recorded tail is never padded or
extended. Comparisons must respect each row's `analysis_windows_seconds` and
`envelope_times_seconds`, including when measuring the synthesized counterpart.
The extraction helper accepts explicit matching windows, envelope times and
maximum support for that purpose.

The frozen broadband bins start at 31.25 Hz and therefore omit A0's approximately
27.10 Hz fundamental. The separate training diagnostics include 20–31.25 Hz and
other low-frequency bands. A0 has an identifiable joint partial tuning fit, but
its fundamental band is weak relative to neighboring bands. Do not interpret
all low-frequency power as string/body vibration or blindly boost that partial.
The 48–52 Hz diagnostic can overlap piano energy and is not a measured hum level.

The frozen C7 pitch fit reports its fundamental but cannot identify B; its
placeholder B=0.0001 is **not a measurement**. C8 fits only three peaks and has
limited, inconsistent B estimates across the two velocities. Preserve these
confidence flags instead of forcing an inharmonicity fit. Its measured f1 is
approximately 4276.7 Hz, about +37 cents relative to equal-tempered C8; the source
is naturally stretched, not automatically an A440 equal-tempered tuning target.

Late treble windows can include body/room/background content after rapid string
decay. Neighbor-band prominence and final-half-second power are useful warnings,
not calibrated SNR or noise-floor measurements. The fixed first-150-ms attack
search can also limit slow-bass interpretation. These are recording-agreement
features, not perceptual scores or uniquely identified material parameters.

## Reproduce

From the repository root:

```sh
python3 tools/fetch_full_range_grand.py
python3 tools/fetch_full_range_grand.py --verify-only
OPENBLAS_NUM_THREADS=1 python3 tools/extract_full_range_grand.py
```

The committed initial SHA/PCM pins are enforced during ordinary fetching.
`--acquire` performs initial pinning only after the immutable Git blobs match.
`--include-reserved-bytes` can fetch the two reserved FLAC files for byte/hash
verification, but there is deliberately no reserved decode/extraction option.
None of these commands modifies Research, GrandExpanded or existing calibration.
