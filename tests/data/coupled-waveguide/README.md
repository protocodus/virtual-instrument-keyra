# Coupled waveguide fixtures

These two numeric configurations are copied byte for byte from the frozen 32-section isolated-string study. `provenance.json` records their source and hashes, and links the preserved fit/provenance reports in `Validation/`.

They describe one polarization at 48 kHz, with the fixed hammer position `x/length=.12` and authored positive intrinsic losses. They are test fixtures for a bounded C2/C4 network proof, not an 88-key piano calibration. The coupled experiment enables an additional passive DC-preserving loss shelf; its phase and storage form part of that experiment.

The CMake test supplies this directory through `KEYRA_WAVEGUIDE_TEST_PROFILE_DIR`. A standalone test executable accepts the directory as its first argument, so it can run from another working directory without relying on ignored `out/` files.
