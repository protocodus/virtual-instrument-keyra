# Frozen confidence-prior grand

These are the exact frozen TRAIN34 calibration numbers from the confidence-prior
study. `calibration.json` SHA256 is
`3cdd77c04d5507ff6c20e150bb8503c7accf21486c3bbead590f63dbb99fd90e`;
`PreparedCalibration.h` is
`fdeee2144dc45bd7b56078c146a6444710c038b62610e9be156adbc321908b63`.
The profile has seventeen anchors, 230 strings, 17,849 string modes and 475 board
modes. No reference waveform or recorded impulse response is included.

`profile_provenance.json` records the fitted-data roles, frozen source transforms
and limits. Absolute `out/` paths inside the original JSON are historical
metadata; generation and runtime do not follow them. The C++ model uses only
compiled constants. This is an opt-in engineering profile. OriginalControl is
still the default, and no listening approval or calibration promotion is implied.

Regenerate using standard Python only:

```sh
python3 src/full_instrument/generate_prepared_model.py --profile FrozenConfidenceGrand
```

[Profile build and validation notes](../../../../docs/FULL_MODEL_PROFILES.md)
provide the integration status. [Recording-agreement results](../../../../docs/FULL_CONFIDENCE_LOSS.md)
and [attack diagnosis](../../../../docs/FULL_ATTACK_TIMING.md) retain the remaining
A0 attack, C2 envelope and unresolved C8-component problems.

Measured recordings: Salamander Grand Piano V3 by Alexander Holm,
[CC BY 3.0 Unported](https://creativecommons.org/licenses/by/3.0/).
[Source pinned to commit3382bf9496bba2486f5ab0de55a264d1dfc38404](https://github.com/sfzinstruments/SalamanderGrandPiano/tree/3382bf9496bba2486f5ab0de55a264d1dfc38404).
