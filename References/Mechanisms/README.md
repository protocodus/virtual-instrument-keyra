# Public piano mechanism recording evidence

This small corpus adds real **key-release noise, pedal action and string-release
resonance** evidence to the sample-free piano work. It contains 16 distinct
source files: eight TRAIN files are acquired and measured; eight reserved files
remain **undownloaded, undecoded and unanalyzed**. No default DSP parameter was
fitted or adopted from this corpus.

Recordings are **Salamander Grand Piano V3 by Alexander Holm**, an acoustic
Yamaha C5, under [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/).
The [pinned distribution](https://github.com/sfzinstruments/SalamanderGrandPiano/tree/3382bf9496bba2486f5ab0de55a264d1dfc38404)
is maintained by kinwie / sfzinstruments; the
[original distribution](https://archive.org/details/SalamanderGrandPianoV3)
and [local license](upstream/LICENSE-CC-BY-3.0.txt) retain attribution.
Upstream describes 48 kHz/24-bit stereo recording with two AKG C414 microphones
in AB configuration about 12 cm above the strings. Microphone spacing, room,
physical event strength, held notes, exact capture timing and editing history
are not documented for these individual files.

## Locked selection and source meaning

[split.json](split.json) and [split-lock.json](split-lock.json) were written
before audio acquisition. The split hash is
`71455bf0383f58563527520a14a5a9456169820dbee04fa20c4411943ae0895c`.
The [metadata inventory](upstream-inventory.json) contains Git blob identities
and sizes for all 161 available mechanism files; only the selected TRAIN eight
were fetched. TRAIN and reserved selections share no source blob.

| Family | TRAIN files | Reserved files | Meaning from source text |
|---|---|---|---|
| Key release | `rel1`, `rel40`, `rel88` — A0/C4/C8 | `rel4`, `rel28`, `rel64` — C1/C3/C6 | Upstream calls these “hammer noise” but explicitly describes **key-release noise**; chromatic mapping is MIDI = file index + 20 |
| Pedal down/up | `pedalD1`, `pedalU1` | `pedalD2`, `pedalU2` | Two randomized variants per direction, triggered at CC64 endpoints 127 and 0 |
| String release | `harmSC2`, `harmLC4`, `harmV3C6` | `harmSC4`, `harmLC6`, `harmV3C2` | Release-triggered resonance families with overlapping playback roles |

`harmS` is selected for playback velocities up to 44 and `harmL` from 45;
`harmV3` is an additional layer across velocities. A release can therefore mix
S or L **with V3**. These are source playback mappings, not measured acquisition
MIDI values or calibrated physical velocities. The diagonal family/register
selection describes several kinds of release without opening their reserved
counterparts; it does not reconstruct a complete same-key layered release.

The raw files do not have the SFZ playback volume, velocity tracking,
`rt_decay`, endpoint random selection or group choking applied. For example,
the key-release group uses −37 dB playback volume, velocity tracking 82 and
`rt_decay=2`; the pedal groups use −20/−19 dB. Such instructions are not physical
capture-level or damping measurements. No loop or start-offset opcode appears
in the three mechanism include files. Parent/global instructions and the
complete pinned SFZ are retained under [upstream](upstream).

There is **no isolated finger-contact, keybed-impact, hammer-strike or
hammer-return recording** here. The source labels do not separate those parts
from piano body, strings, air, room or acquisition artifacts.

## Authentication and measurements

[manifest.json](manifest.json) binds the selected source paths, immutable Git
blob SHA1/byte counts, acquired TRAIN SHA256 hashes, original format and decoded
PCM identities. Each source FLAC is independently decoded to signed PCM24 and
its sample hash is matched to the WAV used for analysis. Container headers may
differ across decoder versions; exact source bytes and decoded samples govern
identity. Original files are 48 kHz, stereo and 24 bit.

There is no gain, trim, retune, resample, denoise, EQ, loop or time padding in
acquisition. Local FLAC/WAV files are ignored by Git. No recorded waveform,
sample bank or impulse response is embedded in the instrument.

- [verification.json](verification.json): TRAIN source/format/PCM verification.
- [train_features.json](train_features.json): eight recording descriptors and
  current authored free-source preset values.
- [analysis-receipt.json](analysis-receipt.json): exact input/output hashes and
  explicit exclusion of reserved audio.
- [Guard-check receipt](../../Validation/mechanism-reference-guards.json): ten
  synthetic/metadata checks, including source PCM mismatch and measurement-read
  replacement rejection, without opening real or reserved audio.
- [Training figure](figures/training-summary.svg): relative envelopes and
  stereo-power spectra, with each recording's actual available support.

Onsets use a 1 ms RMS threshold and are recording coordinates, not physical
MIDI-to-contact times. Spectra use mean stereo power, preserving energy when
the channels have opposite phase. FFT padding interpolates frequency bins;
the native window resolution remains explicit. Time windows and envelopes stop
at actual source support, including partial final windows. Tails are never
extended with invented silence.

Power, envelope decay slopes, local spectral prominence, tail level and stereo
correlation are descriptive features. They do not uniquely identify source
mass, wood, friction, source/body loss, microphone response or an acoustic
background level. Below-20-Hz energy and the final 100 ms can contain a mixture
of event, body, room, background and editing contributions.

The two measured pedal files put approximately 33–38% of their early Hann
spectral power below 20 Hz. That component remains unassigned. The current full
instrument has a 24 Hz output high-pass; later reference/model comparisons must
declare matching observation/filtering, while preserving these unmodified
source files. Do not interpret an unmatched sub-20-Hz component as a new piano
mode or compensate for it with source gain.

## What the first TRAIN measurements show

Key-release early spectra are dominated near 174–238 Hz. About 98.8–99.9% of
their measured 20 Hz–19 kHz early power lies below the current free key-release
exciter's lowest nominal 1206 Hz mode. This makes the **connected body path**
important to evaluate. It does not prove the free source preset is wrong:
soundboard and sympathetic-string output are deliberately absent from that
free-source frequency-coverage calculation.

Pedal-down TRAIN D1 lasts 6.378 seconds and reaches 90% of its recorded energy
at 3.569 seconds after onset. Pedal-up U1 lasts 0.699 seconds and reaches 90% at
0.275 seconds. The unknown event strength/capture state and different editing
support prevent a unique physical decay or directional pedal model from these
two files. The three key-release files all stop at 0.45625 seconds, with useful
late power in some files; their ends cannot be assumed to mark complete decay.

The free preset values are authored effective coefficients. `FullInstrument`
also scales mechanism coupling and trigger strength, then observes its shared
soundboard/string network. Compare these references with the **whole connected
response and intact stems**, plus source/coupling ablations, before changing
exciter frequency, loss or gain. Raw broadband slopes must not be assigned
directly to intrinsic source damping. See
[MECHANISM_REFERENCES.md](../../docs/MECHANISM_REFERENCES.md) for the implications.

## Reproduce without opening reserved cases

```sh
python3 tools/fetch_mechanism_references.py
python3 tools/fetch_mechanism_references.py --verify-only
OPENBLAS_NUM_THREADS=1 python3 tools/analyze_mechanism_references.py
python3 tools/check_mechanism_reference_guards.py
```

The initial acquisition used `--acquire` to pin SHA256/PCM only after Git blob
authentication; subsequent runs enforce the pins. The fetch and analysis tools
offer no evaluation-audio option and reject reserved files in their canonical
recording paths. First evaluation requires a separate candidate/protocol and
prediction freeze, followed by a separate evaluator. After that first opening,
those cases become observed regression evidence.
