# Windows x64 VST3

Reason Rack Extension is the primary product target. This optional VST3 build
is a secondary integration harness and does not validate Rack Extension behavior.

The Windows workflow builds with Visual Studio 2022 on a native Windows runner,
downloads the pinned MIT SDK, then runs the core DSP tests, official VST3 SDK
validator and dynamic host state/event tests. A successful run uploads
`Keyra-Windows-x64-VST3` with the complete `Keyra.vst3` folder, SDK license,
documentation and checksums. It does not publish a release or install a plugin.

The workflow has been added but has not been run from this Linux development
session. Linux results do not establish Windows compatibility. Treat a native
Windows test run and an actual DAW session as required before shipping.

To build locally, install Visual Studio 2022 with Desktop development with C++,
CMake 3.25 or newer and Git, then run from a developer PowerShell:

```powershell
cmake -S . -B build-windows -G "Visual Studio 17 2022" -A x64 -DBUILD_TESTING=ON -DKEYRA_BUILD_REFERENCE=OFF -DKEYRA_BUILD_CLAP=OFF -DKEYRA_BUILD_VST3=ON
cmake --build build-windows --config Release --target keyra_vst3 keyra_piano_tests keyra_vst3_host validator --parallel 2
ctest --test-dir build-windows -C Release --output-on-failure -R '^(live_piano|vst3_sdk_validator|vst3_host_state_and_events)$'
```

For an offline build, supply `-DKEYRA_VST3_SDK_DIR=C:/path/to/vst3sdk` during
configuration. Prepare that checkout at commit
`3cdf9ca5d1f5b1b21e0a86832aa4abe55607bd96` with its `base`, `cmake`,
`pluginterfaces` and `public.sdk` submodules already present; the SDK path then
avoids CMake's download step. Keep `vst3/SDK-LICENSE.txt` with distributed builds.

After all tests pass, the bundle is at
`build-windows/VST3/Release/Keyra.vst3`. To try it locally, copy the entire
`Keyra.vst3` folder into `%LOCALAPPDATA%\Programs\Common\VST3` if supported by
the DAW, or into `C:\Program Files\Common Files\VST3` with the appropriate
filesystem permission. Rescan VST3 plugins in the DAW and use its generic
parameter controls. The build has no custom editor, installer or signing.
