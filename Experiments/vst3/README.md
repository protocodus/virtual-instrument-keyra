# Optional VST3 adapter

Reason Rack Extension is the primary product target. VST3 provides an optional
DAW integration harness alongside the Linux DSP validation tools.

Enable with `-DKEYRA_BUILD_VST3=ON`. This uses the official Steinberg SDK,
MIT licensed at pinned commit `3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96`.
CMake downloads the SDK when `KEYRA_VST3_SDK_DIR` is empty. An existing checkout
with its `base`, `cmake`, `pluginterfaces` and `public.sdk` submodules can be
selected instead. The default build does not download this dependency.

The adapter exports a stereo instrument and a host generic parameter editor.
It supports sample accurate notes and automation, per-channel CC64 sustain,
CC123 all notes off and CC120 all sound off. It advertises 32-bit processing.
Instrument, material and dynamics preserve the engine's documented behavior
for newly struck notes. State is a versioned little-endian numeric encoding;
partial stream reads and writes are handled and malformed states are rejected.

No graphical editor, installer, signing, notarization or commercial DAW
compatibility certification is provided by this prototype. The SDK validator
is available in the build and can be run against the generated `Keyra.vst3`
bundle. Distribute its MIT license with binaries; see `SDK-LICENSE.txt`.

[Windows x64 build and workflow](WINDOWS.md) describes the target platform,
offline SDK setup and the native tests required before shipping.
