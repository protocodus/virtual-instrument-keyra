# Rejected radiation-observer pilot

This is an **unpromoted diagnostic experiment**. Four of six fixed TRAIN note cases passed; both C6 layers failed. Their 5–20 ms five-band errors worsened by 8.23 and 8.87 dB. The default model is unchanged, and these clips make no sound-improvement, production, price or realtime claim.

- [Music with procedural room](old-then-new-room.flac): 18.5 seconds; old starts at 0, new at 9.5, with a half-second gap.
- [Dry music](old-then-new-dry.flac): the same order and timing.
- [C6 recording → old → new](C6-v4-v12-real-old-new.flac): 10.5 seconds. Layer 4 starts at 0; layer 12 at 5.5. Within each group, real/old/new start at offsets 0/1.75/3.5 seconds.

The music uses one frozen **old OriginalControl** trajectory with legacy contact and humanization/mechanical sources/repetition controller disabled. It is not the latest connected default. Only the radiation correction changes; original physical states and contact/bridge forces match. Both observation methods are causal. Added observer states do not represent new physical piano parts. Some overlapping musical attack windows decrease while others increase, so the passage does not isolate individual key attacks.

Both music versions use the original control’s fixed presentation gains, the same procedural room at wet 0.16, and the same 150 ms ending fade. One additional **−2.0893 dB** safety gain applies to all four music versions; there is no candidate RMS matching. C6 uses the frozen protocol onsets, reference unity, the same fixed baseline gain on old/new, one shared safety factor across both layers, and 20 ms ending fades. Exact values and PCM fingerprints are in [manifest.json](manifest.json).

The real excerpts are from **Salamander Grand Piano V3 by Alexander Holm**, a Yamaha C5 recording, distributed by kinwie / sfzinstruments under [CC BY 3.0](https://creativecommons.org/licenses/by/3.0/). Sources: [C6v4](https://raw.githubusercontent.com/sfzinstruments/SalamanderGrandPiano/3382bf9496bba2486f5ab0de55a264d1dfc38404/Samples/C6v4.flac), [C6v12](https://raw.githubusercontent.com/sfzinstruments/SalamanderGrandPiano/3382bf9496bba2486f5ab0de55a264d1dfc38404/Samples/C6v12.flac), and [original distribution](https://archive.org/details/SalamanderGrandPianoV3). Changes: onset cropping, 1.5-second excerpts, shared level adjustment, ending fade, PCM24 conversion and concatenation beside synthesized notes. No denoising, EQ, time stretching or room was added to C6. See the [license](LICENSE-CC-BY-3.0.txt); no author endorsement is implied.

[export.py](export.py) reproduces presentation from the eight fingerprint-matched raw inputs listed in the manifest. Supply a JSON map from source IDs to local files, then run:

```sh
python3 Audio/full-radiation-pilot/export.py --inputs source-files.json --output /tmp/keyra-radiation-listening
```

Relative input paths resolve beside that JSON file. Python, NumPy, SciPy and FFmpeg are required. The private prototype producer/raw model renders are not included here; this exporter performs no DSP synthesis and current main does not recreate this exact historical experiment by default.
