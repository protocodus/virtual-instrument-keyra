# Merge review fixes — 26 October 2026

The automated review of native PR 1 found three issues. Each has a targeted
regression check and is fixed before integration into `main`.

- [GUI ownership after MIDI panic](https://github.com/protocodus/virtual-instrument-keyra/pull/1#discussion_r4375247651): channel-1 CC120/123 now clear the GUI ownership ledger when releasing engine keys. A later mouse release cannot consume a fresh host note or pedal press. Sixteen paired-render scenarios cover both controllers, piano note 60, the three pedal keyswitches and channel isolation; the old code failed the new check.
- [Portable benchmark replay](https://github.com/protocodus/virtual-instrument-keyra/pull/1#discussion_r4375247660): original event files resolve against the current checkout, and fresh scores are reconstructed from their locked manifest in a temporary directory. Two tests cover relocation without ignored build files and rejection of an unlocked fresh manifest. Reference audio is not needed to replay the MIDI scores.
- [Sympathetic concert tuning](https://github.com/protocodus/virtual-instrument-keyra/pull/1#discussion_r4375247664): shared resonators now follow concert tuning during preparation and tuning changes. Independent wet-minus-dry frequency scans measure the requested 300/600 Hz after both paths; the old implementation failed all four cases. A 440→415→440 round trip preserves ringing audio exactly, and tuning changes allocate no memory.

The final SDK-free CTest configuration passed **4/4**, the live-engine
ASan/UBSan configuration passed **2/2**, and the portable replay tests passed
**2/2**. [Actual replay of all 96 frozen renders](merge-review-parity-2026-10-26.json)
is byte-identical at the default 440 Hz tuning. Measured calibration and the
preserved research tree are unchanged.

The rebuilt [native plug-in receipt](merge-review-native-2026-10-26.md) records
**5/5** tests and a passing pluginval strictness-5 pass. This is development
validation; the existing performance, recording, commercial host and Reason
acceptance gaps remain open.
