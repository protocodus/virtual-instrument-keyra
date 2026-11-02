`factory-0.4.10.json` records the six factory presets, both microphone endpoints,
chord voicings, rounds and paired velocities measured by `KeyraLevels` at 48 kHz
and Output 0.7. The source commit and SHA-256 identify the original CSV. The
fixture stores only its 406 negative steps: 104 of 480 original pairs, 30 of
480 independent pairs and 272 of 1,584 expanded pairs. The MIDI chord index is
zero-based and the round is one-based, matching the audit CSV.

`Keyra.FactoryDynamics` runs one fresh audit when model validation and tools are
enabled, including the primary Linux CI audio tier. It checks and retains the
resulting `factory-dynamics.csv` in the build directory. To check an existing
capture without a render:

```sh
python3 Tools/check_factory_dynamics.py --csv factory.csv
```

Every row must be present once, with the expected notes, velocities, drive and
finite paired readings. Each previously nonnegative row has a floor of 0 dB.
An existing negative row has its own measured step as the floor. The checker
allows 0.001 dB below either floor for build and reporting differences; this is
a numerical tolerance. Arm64 and x86-64 Release runs of the reference differed
by at most 0.000002 dB per step on the development Mac.

These floors prevent new regressions. The negative rows remain open defects;
recorded improvements can tighten their floors after review. Low-drive runs,
other performances and the stricter gates for choosing a replacement output
stage remain separate. The existing `Keyra.Levels` test continues to verify
absolute playing levels, median dynamics and peak limits.
