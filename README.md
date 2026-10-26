# Keyra

Keyra is a sample-free grand-piano DSP project. This initial baseline contains the preserved physical-model research renderer, its real-recording benchmark and listening examples.

The offline reference models nonlinear hammer contact, dispersive two-polarization strings, detuned unisons, sympathetic coupling and a reduced soundboard. It has 88 keys, 230 strings, 17,778 string modes and 475 board modes. Numeric calibration comes from acoustic-piano measurements; no recorded waveform or impulse response is loaded by the synthesizer.

The reference renderer is expensive: the supplied 192 kHz musical renders took about 17–19 wall seconds per audio second on the development machine. This is an offline baseline; optimization and a live wrapper are later work. The benchmark below applies to this preserved renderer.

## Reference sound and evidence

[Research/GrandPianoV2](Research/GrandPianoV2/README.md) preserves the exact v2 solver and calibration, original event/MIDI scores, measurement scripts, frozen reports and numerical validation. The source import is documented in [import-provenance.json](Research/GrandPianoV2/import-provenance.json).

| Original musical example | MP3 preview |
|---|---|
| Window at Dusk | [Nocturne](Research/GrandPianoV2/renders/01_nocturne-room.mp3) |
| Two Voices in Morning Light | [Prelude](Research/GrandPianoV2/renders/02_prelude-room.mp3) |
| Sunday on the River | [Jazz waltz](Research/GrandPianoV2/renders/03_jazz_waltz-room.mp3) |
| Copper and Thunder | [Etude](Research/GrandPianoV2/renders/04_etude-room.mp3) |

The isolated-note clips play **real acoustic piano → original POC → calibrated v2**. Try [C4](Research/GrandPianoV2/listening/C4v8-real-v1-v2.mp3), [F♯3](Research/GrandPianoV2/listening/Fsharp3v8-real-v1-v2.mp3) or the [C7 extrapolation check](Research/GrandPianoV2/listening/C7v8-real-v1-v2.mp3). These are level-matched, labeled comparisons, not blind listening tests.

The reference recordings are **Salamander Grand Piano V3 by Alexander Holm**, an acoustic Yamaha C5 set under CC BY 3.0. Ten notes/velocity cases were used for fitting, twelve in-range cases were excluded from fitting and two extreme notes were tested separately. Across the twelve in-range held-out cases:

| Mean error — lower is better | Original POC | Calibrated reference |
|---|---:|---:|
| Harmonic levels | 11.03 dB | 4.96 dB |
| Broad spectral bands | 15.62 dB | 12.09 dB |
| Partial decay rate | 3.88 dB/s | 2.83 dB/s |
| Attack rise time | 8.29 ms | 19.17 ms |

Attack timing regressed. All four held-out-pitch envelope errors and several upper-register/edge cases also regressed. The [complete benchmark](Research/GrandPianoV2/BENCHMARK.md) includes every case and limitation; error reductions are not percentages of perceptual realism or a claim of Pianoteq parity.

## Build the preserved reference

The reference engine needs a C++17 compiler and CMake. It has no SDK dependency.

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build -j
ctest --test-dir build --output-on-failure
build/keyra_reference --help
```

To regenerate the musical WAVs and MP3s:

```sh
cd Research/GrandPianoV2
python3 -m pip install -r requirements.txt
python3 tools/render.py --jobs 4
python3 tools/validate.py --audio
```

`ffmpeg` is required for MP3 encoding and reference decoding. Matplotlib is optional for regenerating figures. The [reference README](Research/GrandPianoV2/README.md) documents MIDI import, benchmark reproduction and generated assets.

## Source and licensing boundaries

- [Research/GrandPianoV2/src](Research/GrandPianoV2/src/): preserved offline solver and generated numeric calibration.
- The proprietary Jukebox SDK and a Rack Extension wrapper are not included in this baseline.
- Reference-audio attribution and modification details are in [ATTRIBUTION.md](Research/GrandPianoV2/reference/ATTRIBUTION.md), with the [full CC BY 3.0 license](Research/GrandPianoV2/reference/upstream/LICENSE-CC-BY-3.0.txt).

This checkout includes small MP3 examples and numerical evidence. Original reference FLACs, decoded WAVs, full-resolution demo WAVs and compiled binaries are intentionally generated or fetched instead of tracked. The source code has no additional open-source license grant in this initial repository; the audio's CC BY license does not license the implementation.
