# Yamaha C3 acoustic reference corpus

This corpus supplies acoustic evidence for behavior shared by Keyra's pianos. It
does not add a Yamaha model to the instrument. The source is the user's local
`YamahaC3.dslibrary` download of
[wesleywilson29's Yamaha C3 on Pianobook](https://www.pianobook.co.uk/packs/yamaha-c3/).
Only numeric metadata and hashes enter the repository. Source and decoded audio
stay under the ignored `out/yamaha-c3/` directory; no recordings are redistributed.
The archive contains no licence file, and these metadata do not establish rights
to redistribute it.

## Capture and interpretation

The creator describes recording a Yamaha C3 in a converted garage with acoustic
treatment, condenser microphones near the piano holes and another microphone
underneath. The preset labels its groups `MIC1`; the monolith's exact microphone
blend, processing, absolute gain and hammer velocities are unknown. Measurements
therefore describe this capture, including room and microphone effects. They are
not calibrated measurements of a bare soundboard or a known strike force.

There are 30 recorded root pitches, MIDI 21 through 108 in steps of three. The
three playback velocity bins are P: 1–95, MF: 96–109, F: 110–127. These broad,
unequal bins do not establish the original player's MIDI or hammer velocity.
The two note groups select pedal-up at CC64 0–63 and pedal-down at 64–127. They
provide endpoint references, not measurements of intermediate pedal position or
pedal motion. The release group has no CC64 gate; its recorded pedal state is
unknown.

## Import protocol

`Tools/decode_yamaha_c3.py` uses only the Python standard library. It reads the
original ZIP and streams the native stereo PCM24, 48 kHz monolith forward. No
copy of the 1.56 GB monolith is needed. It applies no gain, resampling, channel
mixing, onset alignment, filtering or silence removal.

The preset calls its region coordinates `start` and `end`. Both are zero-based
and inclusive: the
[DecentSampler sample-attribute documentation](https://decentsampler-developers-guide.readthedocs.io/en/latest/the-groups-element.html)
defines the default `end` as the file length minus one. A region therefore has
`end - start + 1` frames. The original coordinates and every original group/sample
mapping remain in the manifest. The emitted WAV container is new; its PCM bytes
are identical to that region of the monolith.

The 570 mappings refer to 354 unique coordinate regions: 324 notes and 30
releases. Identical regions become one observation with multiple mapping aliases.
The declared `seqPosition` labels are preserved. The preset does not specify
`seqMode`, so these labels alone do not establish actual playback sequencing or
independent performances. Separate SHA256 pins cover the archive, XML preset,
complete monolith bytes, each region's PCM and its deterministic WAV container.
Exact PCM identity is also checked for leakage between split roles.
Two pairs of distinct coordinate regions contain identical PCM:
`n54v1r3pup` duplicates `n54v1r1pup`, and `n93v2r3pdown` duplicates
`n93v2r1pdown`. These remain in the manifest for traceability, marked
`duplicate_pcm_of`; the split also lists them in `duplicate_cases`. Exclude these
two aliases from fitting weights and independent observation counts. There are
**352 unique PCM recordings**.

## Split and bounded decoding

The split is fixed from root-pitch numbers before acoustic feature extraction or
listening selection. Sort the pitches; indices congruent to 2 modulo 5 go to dev:
MIDI **27, 42, 57, 72, 87, 102**. The other 24 pitches go to train. Every velocity,
pedal state, sequence position and release of the same pitch stays in that role.
This yields **284 train and 70 dev regions**. There is no sealed evaluation set.
After excluding the two additional exact PCM aliases, this is **282 train and
70 dev unique observations**.
The importer refuses to publish a split if exact PCM duplicates cross roles.

```sh
# Create numeric pins and the pitch split; retain no waveforms by default.
python3 Tools/decode_yamaha_c3.py --library '/path/YamahaC3.dslibrary' --pin

# Verify every source region and the stored numeric metadata.
python3 Tools/decode_yamaha_c3.py --library '/path/YamahaC3.dslibrary'

# Keep only a small requested selection for analysis; all source regions are hashed.
python3 Tools/decode_yamaha_c3.py --library '/path/YamahaC3.dslibrary' \
  --cases n60v1r1pup n60v1r1pdown rel60

python3 -m unittest discover -s Tests -p test_yamaha_c3_import.py -v
```

Use `--role train`, `--role dev` or `--all` to retain larger selections. The
default cache limit is 256 MiB; exceeding it fails before decoding. An explicitly
larger `--cache-limit-mib` permits larger batches. Existing files are compared
byte-for-byte with source PCM, including the final frame. The tool never evicts
files automatically. Analysis jobs can delete only the task-owned WAVs they have
finished measuring and retain their numeric feature cache, keeping disk use
bounded. Source hashes remain independent of which files are retained.

The manifest is `Tools/corpus/yamaha-c3.json`; split cases and the exact policy are
in `Tools/corpus/split-yamaha-c3-2026-11-01.json`. IDs encode root pitch, playback
layer, the minimum declared sequence position and pedal endpoint, for example
`n60v1r1pdown`. `rel60` names that pitch's ungated release recording. Consumers
must count canonical files, not their repeated mapping aliases, as observations.
