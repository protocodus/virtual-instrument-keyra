# Pedal-condition sensitivity of the full-model benchmark

Changing the assumed pedal condition does not explain the large missing
body/envelope power in the six tested held notes. This is a result for the
current model/configuration, not a finding about the undocumented source
recording's pedal state or a validation of real-piano sympathetic strength.

The separate prospective protocol compares the unchanged version-4 physical
profile at pedal 0, 0.5 and 1 for A0/C4/D#4, both TRAIN layers 4/12. These are
authenticated Salamander Grand training recordings. No evaluation reference or
feature is opened.

The freeze receipt is `out/full-pedal-condition/freeze.json`, SHA256
`981a26a370106d184f0d50a2d6b5f46c1500397962f7b4884f1f2aecef7ee9e9`.
It precedes new predictions and pins source, header, executable, features,
split, tools and cached baseline. Pedal 0 reuses six authenticated predictions;
twelve new predictions cover the other conditions. Each uses 48 kHz,
3.8 seconds, a pedal event at zero and a held strike at 0.1 seconds. At most
two render processes run concurrently.

The pedal settles before the strike and changes passive damper/sympathetic
response. This offline solver excludes the separate pedal-noise adapter, so
no new noise source is added. All profile fields remain identical. The full
topology retains 230 strings and 475 board modes.

## Actual response

| Six-case mean error | Pedal 0 | Pedal 0.5 | Pedal 1 |
|---|---:|---:|---:|
| Whole envelope | 5.4163 dB | 5.4163 dB | 5.4151 dB |
| Harmonic levels | 4.9335 dB | 4.9335 dB | 4.9331 dB |
| Partial decay slope | 3.3694 dB/s | 3.3693 dB/s | 3.3677 dB/s |

The largest individual envelope improvement is about 0.004 dB. Late-window
stereo correlation changes by at most about 0.00016. All per-case spectral,
attack, rise, velocity, spurious-band and stereo results remain in
`Validation/full-pedal-condition.json`. These are not perceptual scores.

A separate coherent comparison uses the unchanged sample clock and raw float
outputs, with no alignment, gain matching or resampling. Both arms retain the
original 24 Hz output high-pass. Full-file null RMS is roughly 78–87 dB below
baseline for half pedal and 69–76 dB below it for full pedal. In the late
1.6–3.6-second absolute window, full-pedal nulls are about 57–67 dB below
baseline. No inaudibility threshold is inferred. Whole-network final energies
and waveform hashes remain in `Validation/full-pedal-pressure-delta.json`;
they are not isolated sympathetic energies.

## Inference limits

Loss selection and full-TRAIN confirmation finished before these condition
results were inspected. No condition data enter loss selection. No profile,
live pedal behavior, canonical model or plugin is changed. The diagnostic
does not identify acquisition state or justify holding the live pedal down.

The small modeled response rules out this simple condition switch as an
explanation of the current large recording disagreement. It does not rule out
stronger/different sympathetic behavior in a real instrument, room/body
content, unison/aftersound balance or other poorly calibrated phenomena.
Controlled pedal/release recordings remain needed for those claims.

## Reproduction

Use a new directory so frozen predictions are not overwritten:

```sh
OPENBLAS_NUM_THREADS=1 python3 tools/probe_full_pedal_condition.py run \
  --output out/full-pedal-condition-reproduction \
  --report out/full-pedal-condition-reproduction/report.json
```

The retained raw-null analysis driver is
`out/full-pedal-condition/analyze_pressure_delta.py`. Source, event, WAV and
acoustic-score identities bind both reports. No runtime waveform/IR is added.
