# bitKlavier Steinway D: calibration reference — 2026-11-01

The owner's `Downloads/bitKlavierGrand_HouseORTF_44k16b` is inventoried as an
additional calibration reference. Its dense velocity layers can test recovery
of missing dynamics while preserving each piano's measured tone. No production
instrument or numeric DSP data has been fitted from it yet.

The [publisher](https://bitklavier.com/the-bitklavier-grand/) identifies a
Steinway D recorded at Princeton's Taplin Auditorium in January 2021. Andrés
Villalta recorded it, Matt Wang played, and Dan Trueman produced the library,
licensed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
The [House ORTF distribution](https://archive.org/details/bitKlavierGrand_HouseORTF_44k16b)
uses Schoeps cmc64 microphones in an audience perspective, including hall
sound. All nine microphone perspectives and all resolutions belong to one
recording family and must share evaluation roles.

The local README's heading says “Piano Bar,” but its methodology says House
ORTF, agreeing with the folder and publisher download label. A copied heading
is the likely explanation, not a verified archive identity. The README
describes 96 kHz acquisition; all 21 opened files are 44.1 kHz, 16-bit stereo.
Unopened WAV headers have not been verified.

## Coverage and frozen roles

The filename inventory contains 662 WAVs:

| Kind | Coverage | Count |
| --- | --- | ---: |
| Main notes | A0–C8, MIDI 21–108 every three semitones, 16 layers each | 480 |
| Release resonance (`harm`) | Same 30 pitches, three layers each | 90 |
| Hammer sounds (`rel`) | 88 key-indexed files | 88 |
| Pedal sounds | Down/up, two action-speed categories | 4 |

The [split](bitklavier-house-ortf-2026-11-01/split.json) was frozen from pitch
order before opening WAV headers, hashing contents or measuring audio.
There are 24 training pitches. MIDI **30, 60 and 90** are development-only;
**42, 72 and 102** remain sealed. Every main and resonance-release layer of a
pitch shares its role. Hammer/pedal files remain unopened and unassigned;
their mapping must be verified before use. Sibling microphone recordings,
sample-rate editions and derived copies inherit this family split.

The [inventory](bitklavier-house-ortf-2026-11-01/inventory.json),
[numeric survey](bitklavier-house-ortf-2026-11-01/survey.json) and
[receipt](bitklavier-house-ortf-2026-11-01/receipt.json) are exact copies of
the frozen intake artifacts. Split SHA256:
`1452c65b60f8d633cd21c9db05e9ccb79f1f0feb5ef12ba1c1e866093bc12db8`.
The receipt pins the local research scripts and full report under
`out/realism/bitklavier-house-ortf/`; no audio is copied or committed.

## Initial measurements and interpretation

Only 21 predeclared training files were opened: A0/C8 layers 1/8/16 and
C2/A4/C7 layers 1/4/8/12/16. Lengths range from 4.35 to 74.30 seconds and
peaks from −38.71 to −2.96 dBFS. None contains a full-scale sample value or
a 20 ms exact-zero run after the first 50 ms. This does not exclude earlier
analog clipping, fades or nonzero/dithered recording truncation.

Sampled layers increase monotonically in stereo RMS over 5–500 ms from the
edited file start. Soft-to-loud spans are 22.09–30.60 dB across the five
surveyed pitches. This establishes ordered layers in that subset, not
identical curves across the keyboard or a physical hammer-velocity law.

The user-supplied README documents RMS-based layer selection and gain balancing,
usually below 2 dB, RX8 denoising/repair, onset trimming, 5 ms attack fades and
100 ms end fades. Resonance-release clips have their attacks removed and
100 ms fades. Late measured power mixes room sound, instrument decay,
processing and quantization; it is not a calibrated noise floor or isolated
mechanical decay. Layer indices are ordinal loudness categories, not known
MIDI velocities or measured hammer speeds.

The existing [Hamburg source](https://www.pianobook.co.uk/packs/steinway-grand/)
and [New York source](https://www.pianobook.co.uk/packs/grandpas-piano/) document
different instruments and sessions. No exact full-file hash match was found
for the 21 opened files against their corpus metadata. This supports separate
provenance but is not an exhaustive independence test: resampling, trimming
and re-encoding defeat a byte comparison.

## Next interpolation experiment

Hide layers at training pitches, retain sparse target anchors, and compare
predicted levels, spectral shape and envelopes with the withheld recordings.
Start with target-local interpolation; test donor corrections only after
normalization and with the entire target recording family excluded from its
donors. Corrections must vanish at retained target anchors. Independent strikes
make raw waveform/phase error an unsuitable reference objective.

Keep sparse three-anchor trials separate from smaller gaps. Retain actual
available layer coordinates: Salamander has 16 source layers but only 12
training layers; its held-out layers 3/7/11/15 must not become training truth.
Relative layer rank across edited libraries is an explicit comparison
convention, not a common physical input measurement. Measure spectral-shape
improvement separately from gain balancing. Open dev only to score a frozen
candidate; sealed evaluation remains unopened.
