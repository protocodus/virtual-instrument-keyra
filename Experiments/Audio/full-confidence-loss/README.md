# Matched full-model calibration comparisons

Each 14.75-second file plays **real → original full control → V4 candidate →
confidence-prior candidate**. Sections start at **0, 3.75, 7.5 and 11.25 seconds**.
Each contains 3.5 seconds of actual post-onset support, with 0.25-second gaps.

| File | Data role | Review target |
|---|---|---|
| [A3v8](A3v8-real-original-v4-confidence.flac) | Previously observed historical | Body/aftersound; the confidence fit reverses the earlier A3 envelope regression. |
| [C4v12](C4v12-real-original-v4-confidence.flac) | TRAIN | Midrange attack and body. |
| [A0v8](A0v8-real-original-v4-confidence.flac) | Previously observed historical | Persistent attack rise-time regression. |
| [C2v8](C2v8-real-original-v4-confidence.flac) | Previously observed historical | Envelope regression versus the original. |
| [C8v8](C8v8-real-original-v4-confidence.flac) | Previously observed historical | Unresolved strong component near 4433.8 Hz. |

Models use exactly their scored early-RMS gains, fixed over the whole note.
One additional peak gain of 0.5078143556842272 applies to all twenty sections.
There is no independent peak normalization, added room, EQ, resampling, pitch
shift, time stretch or onset fade. Every section has the same 20 ms end fade.
Each source uses its frozen benchmark onset. The original capture room remains
in the real recordings. Files are 48 kHz stereo PCM24 FLAC; each decoded file is
verified against the PCM24 conversion of its processed float source.

The [manifest](manifest.json) pins 157 inputs, exact producer source/header/binary
identities, the confidence and V4 profiles, reference identities, gains, support,
onsets and output PCM. The exporter creates no synthesis and performs no fitting.

C4v12 influenced fitting. All four historical cases were observed previously,
including both extremes; this is **not fresh validation**. Recording-agreement
metrics are not a listening verdict. The calibration candidates remain private
and have not changed the canonical model. These held-note renders do not use the
separate repeated-strike, action-noise or cavity research adapters.

Recordings: **Salamander Grand Piano V3, Alexander Holm**, distributed under
[Creative Commons Attribution 3.0 Unported](https://creativecommons.org/licenses/by/3.0/).
[Pinned source](https://github.com/sfzinstruments/SalamanderGrandPiano/tree/3382bf9496bba2486f5ab0de55a264d1dfc38404)
· [Original distribution](https://archive.org/details/SalamanderGrandPianoV3).
Modifications are onset trimming, 3.5-second cropping, a 20 ms end fade, common
scaling, concatenation with modeled comparisons and silence, and PCM24 conversion.
