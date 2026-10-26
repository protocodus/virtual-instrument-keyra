# Upright recording evidence

These isolated acoustic upright recordings come from the **Versilian Community
Sample Library (VCSL)**, `Chordophones/Zithers/Upright Piano, Yamaha`, pinned at
commit `c1ea7bcc3c7309650ab0da9d15c9cd1fbc4a4c7e`. The repository identifies the
collection as a Versilian Studios LLC project and explicitly releases it under
**CC0 1.0 Universal**. This attribution identifies the collection publisher;
it does not infer an individual recording performer or engineer.

- [Pinned upstream repository](https://github.com/sgossner/VCSL/tree/c1ea7bcc3c7309650ab0da9d15c9cd1fbc4a4c7e)
- [Pinned CC0 license](https://github.com/sgossner/VCSL/blob/c1ea7bcc3c7309650ab0da9d15c9cd1fbc4a4c7e/LICENSE)
- [Pinned instrument note](https://github.com/sgossner/VCSL/blob/c1ea7bcc3c7309650ab0da9d15c9cd1fbc4a4c7e/Chordophones/Zithers/Upright%20Piano%2C%20Yamaha/Note.txt)

The upstream instrument note describes a cleaned, recut and remastered version
of Upright No. 1 / VSCO 2 CE recordings. The exact piano model, microphones,
room, processing, physical hammer velocities and pedal state are not established
by that note. Source audio is retained unchanged for research evaluation and
fitting of numeric model parameters; it is not bundled into the plugin runtime.
The local `recordings/` directory is ignored by Git. `upstream/` preserves the
license, repository README and instrument note verbatim.

`manifest.json` pins each WAV's URL, byte count, Git blob SHA1 and SHA256. It
locks ten fitting anchors at scientific C2–C6, soft/loud ordinal source layers,
and seven excluded cases: C3/C4/C5 middle layers, G2/G3/G4 middle layers and a
C4 repeated take. Source round robin 1 is used except the C6 soft fitting anchor,
whose round robin 1 is shorter than the fixed analysis horizon; round robin 2
was chosen before feature extraction. This is a narrow single-upright corpus,
not evidence of general performance across upright instruments.

Upstream labels middle C as **C3**; the scientific-pitch alias is **C4 / MIDI60**.
Both labels are retained. `analysis_layer_proxy` 4/8/12 and
`render_velocity_proxy` 40/61/93 are explicit compatibility inputs for the grand
benchmark, not upstream MIDI velocity bins or measured hammer velocities.
Feature rows preserve original layer, round robin and note labels and mark the
velocity as a proxy. Treat velocity agreement as conditional on this choice.

From the repository root:

```sh
python References/Upright/fetch_reference.py
python References/Upright/fetch_reference.py --verify-only
python References/Upright/extract_features.py --train-only
python References/Upright/extract_features.py
```

Extraction imports the existing grand benchmark without changing its fixed
windows, stereo power combination or onset/pitch/decay algorithms. No trimming,
padding, normalization, EQ or resampling is applied. `train_features.json`
contains only the ten fitting anchors; `reference_features.json` also contains
the excluded cases and must not be used for fitting. Recording agreement is not
a perceptual quality score, and these processed library recordings do not
establish the physical properties of the instrument in isolation.
