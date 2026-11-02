# Factory chord response

`Keyra.Levels` checks ordinary playing levels, fortissimo levels and the stereo sample ceiling. `Keyra.FactoryDynamics` checks the change in loudness for 2,544 individual chord pairs across the six named pianos at both microphone endpoints. Both tests use the louder channel's sliding 300 ms RMS at 48 kHz, with 0 VU at −12 dBFS RMS. They compensate the engine's reported latency. Each velocity replays the full MIDI sequence from reset, including the same sequence of strike variations.

The approved B reference is the 0.4.10 engine at commit `674ad1a985142472b062b47063a54b194f0bbec2`. It receives half of the factory Output, and a linear factor of two restores level after its output stage. That restores the factory calibration and preserves the velocity progression heard in B. The original listening clips used a different constant per piano to align their first passages. Such a constant cancels from every velocity difference. This unprotected reference can exceed full scale.

`ApprovedLevels.h` records B's typical level and maximum fortissimo level for each of the 13 factory programs and the six measured builds at Mic 1. `Keyra.Levels` requires normal playing within 0.05 dB of its own reference, a fortissimo maximum no higher than that reference plus 0.001 dB, and an output sample peak of at most −1.5 dBFS with 0.00001 dB of floating-point tolerance. Typical levels use the median over 90 events, including single notes and chords at velocities 70, 90 and 110. The fortissimo measure uses the loudest of 40 chord strikes at 127.

`factory-0.4.11.json` holds the maximum unprotected B reading for each panel, named preset and microphone. These bounds also cover Belmont's named bright preset at Mic 1. They are rounded up to the next thousandth of a VU. The per-pair step floors come from the actual factory output with its final peak protection active. Each `minimum_step_millidb` list covers one microphone, in round, chord and velocity-interval order, with the velocity interval varying fastest. Each step is rounded down to the next thousandth of a dB. The checker allows a further 0.001 dB for compiler and meter variation and requires all 480 original steps to be positive.

| Panel | Pairs | Unprotected B median step | Factory median step | Decreasing pairs, B / factory |
| --- | ---: | ---: | ---: | ---: |
| Original, 110 → 127 | 480 | 1.675 dB | 1.398 dB | 0 / 0 |
| Independent, 101 → 121 | 480 | 2.480 dB | 2.380 dB | 1 / 1 |
| Expanded, 11 velocity intervals | 1,584 | 0.546 dB | 0.502 dB | 32 / 36 |

The protection reduces some hard peaks and their 300 ms readings. The finer panel also contains chords whose underlying unison and octave contributions interfere. The individual floors retain those measured differences so a change at one chord cannot hide another chord getting quieter.

To rerun the release gate from a build containing `KeyraLevels`:

```sh
python3 Tools/check_factory_dynamics.py --renderer build/KeyraLevels --output build/factory-dynamics.csv
build/KeyraLevels --check --jobs 4
```

To reproduce the independent B limits on a machine with a C++17 compiler, run from the repository root:

```sh
capture_dir=$(mktemp -d)
git archive 674ad1a985142472b062b47063a54b194f0bbec2 Source/DSP Tools/KeyraLevels.cpp | tar -x -C "$capture_dir"
c++ -O3 -DNDEBUG -pthread -std=c++17 -I"$capture_dir" -I"$capture_dir/Source" \
    Tests/Fixtures/dynamics/measure_approved_levels.cpp "$capture_dir/Source/DSP/KeyraEngine.cpp" \
    -o "$capture_dir/approved-b"
"$capture_dir/approved-b" > "$capture_dir/levels.csv"
"$capture_dir/approved-b" --audit-dynamics --jobs 4 > "$capture_dir/chords.csv"
```

The first CSV gives the values in `ApprovedLevels.h`. For each panel, piano and microphone in the second CSV, take the largest of both `vu_low` and `vu_high` across all its chords and round upward to obtain `approved_max_vu`. The previous `factory-0.4.10.json` records the older output stage for historical comparison.
