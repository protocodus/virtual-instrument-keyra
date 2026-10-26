# Expanded grand calibration recordings

This is a new, pre-locked expansion of the **Salamander Grand Piano V3**
recordings by **Alexander Holm**, using the same acoustic Yamaha C5 and pinned
upstream commit as the preserved study:
`3382bf9496bba2486f5ab0de55a264d1dfc38404`.

- [Pinned upstream](https://github.com/sfzinstruments/SalamanderGrandPiano/tree/3382bf9496bba2486f5ab0de55a264d1dfc38404)
- [Original distribution](https://archive.org/details/SalamanderGrandPianoV3)
- [Attribution license, CC BY 3.0](https://creativecommons.org/licenses/by/3.0/)
- [Local license](upstream/LICENSE-CC-BY-3.0.txt)

Alexander Holm is the recording author. Kinwie / sfzinstruments maintains the
SFZ remapping and distribution. Upstream describes 48 kHz/24-bit stereo samples,
16 ordinal velocity layers, minor-third sampling, and two AKG C414 microphones
in AB configuration approximately 12 cm above the strings. Room, acquisition
pedal state, physical hammer speed, exact release time and earlier library
editing/noise-reduction history remain unknown.

No new features were extracted from reserved recordings until the expanded model
and its training-based choices were frozen. A pinned source and more calibration
notes do not themselves establish sound quality or generalization to other
pianos or microphone arrangements.

## Locked roles

`split.json` was written **before any new audio download or feature extraction**.
Its SHA256 is
`35fc73788b8e27e6762a1e9664992c6bbc4702858e2b7bb5185885974dac0061`.

| Role | Cases | Notes/layers |
|---|---:|---|
| Fitting | 26 | A1, C2, D#2, A2, C3, D#3, C4, D#4, A4, C5, D#5, A5, C6; each layer 4 and 12 |
| Fresh pitch validation | 3 | A3 at layers 4, 8 and 12; no A3 recording is used for fitting |
| Fresh velocity validation | 4 | D#3v8, D#4v8, A4v8, D#5v8 |
| Historical regression | 14 | Original nontraining cases, including old held-out and edge cases |

The 26 fitting cases retain the original ten C2–C6 anchors and add sixteen
recordings. A1 was selected from the existing upstream SFZ inventory before
extraction, to extend the fitting range into the bass. The original frozen
research split, source and reports are unchanged. Its previously observed
held-out cases are regression evidence, not fresh tests for this iteration.

Layer 4/8/12 model inputs remain **40/61/93 MIDI velocity**, the rounded
midpoints of the SFZ playback bins 37–43, 57–64 and 89–96. They are not known
recording MIDI values or measured hammer speeds. No SFZ tuning, offset,
velocity tracking, release envelope, resonance, hammer or pedal layers are
applied to these source recordings.

## Identity and extraction

`upstream-file-identities.json` retains the selected Git blob SHA1 and byte count
from the pinned commit tree. `manifest.json` additionally pins each new FLAC's
SHA256 and decoded PCM24 identity. The 23 newly acquired files comprise sixteen
fitting and seven reserved cases. During acquisition the reserved recordings only
underwent byte/hash and PCM-format verification; no feature extraction, waveform
plots, listening, spectrum or quality measurements were used in choosing this split.

The seven reserved cases were subsequently evaluated **after** training-only
candidate selection and freeze. [evaluation-receipt.json](evaluation-receipt.json)
records that transition and the immutable split/freeze/result hashes. Results are
in [fresh-grand.json](../../Validation/fresh-grand.json). These cases are now
regression evidence; later reuse must not be presented as another fresh test.

FLAC downloads are unchanged. WAV files are lossless signed-PCM24 decodes made
with ffmpeg at the original rate and channel count. No local gain, trimming,
normalization, EQ, denoising, retuning, resampling or padding is applied.
The local `recordings/` directory and transient download logs are ignored.
No waveform is embedded in the piano engine or plugin.

`train_features.json` uses the unchanged preserved benchmark's onset alignment,
stereo power combination, fixed windows and pitch/partial/decay/attack extraction.
For the original ten training cases it reuses the exact frozen numerical
measurements; new rows carry the same schema and an explicit training role.
`extract_training.py` has no validation-extraction mode and refuses reserved
roles. It verifies both the locked split and input PCM identities.

From the repository root:

```sh
python3 References/GrandExpanded/fetch_reference.py
python3 References/GrandExpanded/fetch_reference.py --verify-only
python3 References/GrandExpanded/extract_training.py
```

The committed manifest already contains the initial authenticated SHA256/PCM
pins. `--acquire` is the explicit initial-pin operation; ordinary fetching and
verification enforce the pins. The extraction scripts never modify the
preserved study's source, features, split or reports.
