# Interpolation candidate: local frontend validation — 2026-11-01

Keyra 0.4.2 builds as macOS arm64 VST3, AU, CLAP and standalone. VST3 passes
pluginval 1.0.4 at strictness 10 with seed `0x4b455952`; CLAP passes all 17
applicable clap-validator 0.3.2 tests, with no failures. Three optional
`clap.preset-discovery-factory/draft-2` tests are skipped because the wrapper
does not implement that factory. The final run retains a scan-time warning:
111 ms against the validator's 100 ms threshold. The earlier run took 704 ms;
neither warning is hidden or turned into a pass.

This is a local candidate, based on canonical commit
`60d89f00f12290d8d7ec599cf48e7905dbf01da6`, plus a small editor layout fix.
The six-column Build controls now allow JUCE's 30-pixel track reservation and
the complete 36-pixel value box, so `100%` is visible instead of an ellipsis.
The rendered Build view was visually inspected. DSP and generated numeric
data are unchanged by that fix. The [receipt](host-interpolation-2026-11-01.json)
pins the resulting source, binary, log and screenshot hashes.

## Plug-in checks

- Release build, JUCE 8.0.14, the repository-pinned CLAP wrapper, native arm64
  on an Apple M1 Max. `COPY_PLUGIN_AFTER_BUILD` remains false; the build does
  not install these bundles into user plug-in folders.
- `Keyra.PluginProcessor`, the rotating `Keyra.ParameterMatrix` run with four
  workers, and `Keyra.EditorRender` pass. After the layout fix, the processor
  and editor checks pass again, as do the two host validators above.
- The processor check covers state validation, sample-accurate pedal/MIDI and
  block invariance. The rotating parameter matrix is not the full CI matrix.
- The AU and standalone bundles are built. This iteration does not claim AU
  validation or interactive standalone/DAW acceptance. The scoped local
  validator script retains the shared script's pinned downloads, checksums
  and VST3/CLAP commands, while omitting its AU installation/registrar step;
  the shared portfolio script itself is unchanged.

The cold-scan warning prompted a separate construction-cost diagnostic.
Three runs of 50 constructor/reset/destructor cycles at 48 kHz give median
process CPU times of 2.1363 ms for baseline and 2.6157 ms for this candidate,
about 0.48 ms extra per cycle. This is initialization work, not callback cost,
and does not explain all host scanning overhead. The existing eight-demo
rendering benchmark remains within −0.33% to +0.66% of baseline on this
development machine; neither result is a Reason target-chip CPU claim.

## Rack integration

The isolated Rack branch is at
`1d0214d17e3cb5d61c7de3c7c5f68ebf711de630`, based on fetched Rack main
`ca0b1f44ef3d5b68d7d23e84c4ff94162141c809`. Its canonical submodule pins
`60d89f0` and directly compiles the same DSP. Rack version **0.4.2d1** adds the
four Belmont build weights on new stable tags 299–302 and synchronizes the
six-piano panel, Random Piano operation and fourteen factory patches.

Four native wrapper checks and the ASan/UBSan wrapper contract pass, along
with Keyra-specific ownership/freshness checks. Jukebox SDK 5 compile-only,
local45 Deployment and universal45 complete. The U45 passes ZIP integrity,
contains the fourteen patches and all four Testing/Deployment 32-/64-bit
chip inputs. Two static-analyzer nullability warnings in unchanged canonical
voice selection remain recorded; no Rack-only DSP workaround was added.

Protected Recon 14.1d48 build 20466 creates the default device and plays and
exports all fourteen factory patches. Exports are finite and audible at
44.1 kHz, with peaks from −5.585 to −1.49995 dBFS. No Keyra error or failed
script API call occurs. The protected runner preserves all 9,440 production
files, restores its scratch/log state and leaves the installed payload
unchanged. Its controlled shutdown after the completion marker is not a
timeout or crash.

The adapter receipt and complete evidence are in the isolated Rack checkout
under `Examples/Keyra/Docs/validation/interpolation-2026-11-01.{md,json}`.
The local handoff is `Examples/Keyra/Release/0.4.2d1/Keyra-0.4.2d1.u45`,
SHA256 `e80a5851de90e420db6c3b026925559c9d6d1b1fe209d983c07d1bad50ab7ab6`.
This GUI-only canonical follow-up does not change that tested Rack DSP.

## Remaining acceptance

No manual DAW session workflow, AU/auval run, Windows validation for this
candidate, interactive Rack Build/Random Piano operation, all Rack views,
RPG-8 auto-routing, song save/reload or older-song loading was performed.
Native/Lua simulations cover their stated contracts only. Target-chip CPU,
retail Reason and Reason Studios cloud acceptance remain open. No upload,
publication, push, PR or merge was performed.

The all-piano recording and keyboard results, including the New York tuning
regression and remaining keyboard outliers, remain in the
[calibration report](realism-baseline-and-trials-2026-11-01.md). Passing these
host checks does not resolve those sound-quality limitations.
