# Full-model calibration comparisons

Each clip plays **real recording → original full-model control → v4 full-model
candidate**, with 3.5 seconds per version and 0.25-second gaps. The cases are
A0v4 (lowest key, soft layer), C4v12 (middle C, hard layer) and C8v12 (highest
key, hard layer). All three are training cases.

The candidate is **not promoted**. Historical A3 envelope behavior regresses,
and C8 still lacks a strong component heard in the recording. These clips make
the remaining differences audible; they do not establish recording parity.
The control retains the original physical model and calibration using the
tested hot-float implementation. Both models retain the full string/body
network, rather than the reduced plugin preview. These isolated-note renders
do not include the separate repetition or key/pedal mechanism adapters.

Sources are aligned at the same benchmark onset definition. Model levels use
exactly the early gain recorded in their frozen scores, followed by one common
peak gain across all nine sections. There is no independent peak normalization,
EQ, resampling or added reverb. Every section has the same 20 ms ending fade;
attacks are unfaded. The real recordings retain their acquisition acoustics.
The files are 48 kHz stereo, lossless FLAC of the final 24-bit PCM conversion.

Recordings: **Salamander Grand Piano V3 by Alexander Holm**, distributed under
[Creative Commons Attribution 3.0 Unported](https://creativecommons.org/licenses/by/3.0/).
Source: [pinned Salamander repository](https://github.com/sfzinstruments/SalamanderGrandPiano/tree/3382bf9496bba2486f5ab0de55a264d1dfc38404)
and [original distribution](https://archive.org/details/SalamanderGrandPianoV3).
Modifications: onset trimming, 3.5-second cropping, identical ending fades,
common gain, concatenation with model comparisons and silence, and PCM24 FLAC
conversion. The recording credit applies to the real sections.

`manifest.json` records input/output hashes, source and synthesis identities,
onsets, exact model gains, section timing and decoded-PCM checks. Reproduce with
`python3 tools/export_full_calibration_listening.py`; it reads only the three
named TRAIN recordings and existing renders, with frozen hash/PCM guards.
