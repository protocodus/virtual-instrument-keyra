# Keyra CLAP adapter

`Keyra.clap` is an instrument with one stereo float32 output and one note input.
It accepts MIDI 1.0 notes/CC64/CC120/CC121/CC123 and native CLAP note events,
including channel/note-ID targeting and choke. Events and automation are applied
at their sample offsets. Native note lifetimes are reported with `NOTE_END`.
Per-note modulation, MIDI 2.0, MPE expression and a custom graphical editor are
not implemented. Use the DAW's generic parameter editor.

Build from the repository root with `KEYRA_BUILD_CLAP=ON` (the default). The
headless `clap_host_integration` CTest loads the actual shared plugin and exercises
the ABI, state and event handling. This is not certification by a commercial DAW.

On Linux, copy `build/plugin/Keyra.clap` into `~/.clap/`, then rescan CLAP plugins
in the DAW. Hosts must support CLAP; this binary is not a VST3 or Audio Unit.
Windows and macOS builds use the same adapter but require native build and host
validation before distribution. The build does not install the plugin into a
user's DAW directory automatically.

The host exposes ten stable parameter IDs:

| ID | Control | Plain values |
|---|---|---|
| 0 | Instrument | Concert Grand, Studio Grand, Upright, Felt Upright |
| 1 | Material voicing | Spruce, Cedar, Maple |
| 2 | Microphones | Close AB, XY, ORTF, Mid Side, Mono, Room AB |
| 3 | Tone | 0–100% |
| 4 | Dynamics | 0–100% |
| 5 | Resonance | 0–100% |
| 6 | Mechanical noise | 0–100% |
| 7 | Room / distance | 0–100% |
| 8 | Stereo width | 0–100% |
| 9 | Output | −48 to +6 dB |

Parameters are exposed through the shared engine metadata. The instrument and
material names describe authored model voicings, not verified replicas of named
commercial instruments or isolated measurements of wood species. Microphones
are procedural pickup arrangements, not recorded microphone responses.

State format `KEYRACL1`, version 1, stores parameter IDs and IEEE-754 binary64
values in little-endian order. Loading state validates the entire stream before
publishing parameter changes; partial reads/writes are supported. Main-thread
state changes reach the audio thread through lock-free atomics. The audio
callback never waits for a state load. Only float32 buffers are advertised.
