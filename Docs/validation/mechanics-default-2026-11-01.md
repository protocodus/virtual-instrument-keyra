# Mechanics default and control — 0.4.5

The owner selected Moonlight **B**, raw Mechanics gain **0.175**, and asked for
that balance at **0.4** on the knob. New native and plug-in instances now use
that exact gain. This is half the audition's A setting (0.35), rather than half
the former factory default (1). The choice and frozen listening-file hashes
are recorded in [the decision log](../decisions.md#2026-11-01--quieter-key-landing-action-in-the-moonlight-performance).

Only the editor's travel/readout is tapered. The parameter ID, index, version,
linear raw range 0–2 and host normalization gain/2 remain unchanged. Forty
percent maps exactly to 0.175f, zero silences the action, and 100% retains the
former maximum gain 2. Double-click restores 40%. Factory piano selection
preserves the user's Mechanics setting. Valid older states lacking Mechanics
explicitly restore historical gain 1; states containing it retain their value.

`MechanicsControl.h` derives the interface taper from the chosen default and
maximum. It adds no calculation to the render callback. The engine `.cpp` and
measured data are unchanged. Mechanics still affects the existing action
excitation paths, not the separate hammer/body attack or tonal model.

## Verification

- Universal macOS Release builds: VST3, AU, CLAP, Standalone and native tools;
  the shared DSP also compiles as C++17. Tests executed on arm64.
- All 13 native unit and two audio tests pass. Tests cover finite, monotonic
  control mapping, round trips, exact default/B equality on all six pianos,
  action amplitude scaling, and no live allocations.
- Plug-in processor/state, actual editor and rotating parameter-matrix tests
  pass. The editor tests exercise 40% display/entry/travel, host updates,
  GUI writeback, double-click with one balanced host gesture and reopening
  without writing automation. Explicit old values and missing-field legacy
  states are checked independently of the fresh default.
- A complete-history 40.5-second Moonlight render with no Mechanics override
  is byte-identical to the frozen native B WAV. Explicit raw 0.35 also remains
  byte-identical to frozen A. This verifies the actual listening choice,
  rather than just its numeric setting.
- VST3 passes pluginval 1.0.4, strictness 10, seed `0x4b455952`; CLAP passes
  17 tests with zero failures and three optional skips (one validator warning).
- The native CPU budget passes: eight preset phrases, three repeats, 48 kHz,
  256-frame blocks, Apple M1 Max. Median realtime factors range from 0.0300
  to 0.1003 against a 0.6 budget. This is native timing, not Reason target CPU.
- The actual default editor screenshot was inspected at its displayed size;
  Mechanics reads 40%. The standard eight README demos were regenerated from
  their unchanged MIDI through the new default, using the normal build tools.

Build hashes, render parity, timing and log hashes are in the
[numeric receipt](mechanics-default-2026-11-01.json). Raw evidence is under
`out/mechanics-default-20261101/`, with native tier evidence under
`out/realism/native-component-audit-20261101/engine/mechanics-default-045/`.
The original A/B/C audition and complete demo-song delivery remain frozen.

The x86_64 slices were built, not executed. AUval and a fresh manual DAW session
were not run. Reason's adapter and host checks are recorded in its repository.
No upload, publication, push or merge is implied by these local checks.
The repository-standard audit retains one unrelated tag-name failure for the
existing `baseline-v2-20261026` research tag; that tag was not renamed or deleted.
