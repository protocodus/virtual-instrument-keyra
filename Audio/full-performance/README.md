# Full physical performance comparison

The clips compare the original full model's control calibration with the same
model plus stateful action recovery, bounded strike variation and quiet
body-coupled key/pedal texture. Both retain all 230 strings, 17,778 string modes,
475 board modes and the original stereo radiation observations.

Listen to [dry](control-then-connected-dry.flac) or
[with the same room](control-then-connected-room.flac): control starts at 0 s;
the connected version starts at 9.5 s. The four individual versions are also
included. The room version uses the original procedural presentation at the
same 0.16 wet setting for both engines. Dry versions have no added room.

Both play the exact first six seconds of the original *Window at Dusk* event
score, followed by three seconds of held/tail behavior. The final key and pedal
remain held as in that event prefix; no release is invented. All requested
strikes launch, with no unsafe launch or numerical fault. The connected version
uses humanization 0.65, mechanical level 0.025 and seed 123456. The control
disables these excitations and uses the safe repetition bypass.

Each nine-second engine/presentation is matched to 0.08 stereo RMS before an
identical 150 ms ending fade. One common true-peak gain is then applied across
all four versions. This makes the comparison easier to hear while preserving
the within-performance dynamics. It is not a source-level calibration test.

The [manifest](manifest.json) pins the exact renderer binary, source snapshot,
events, parameters, presentation code and export gains. Each FLAC is a verified
lossless copy of the corresponding PCM24 conversion. Run
`python3 tools/compare_full_performance.py` to verify and re-export the frozen
renders; `--render` repeats synthesis with that same authenticated producer.

This snapshot uses the original control calibration and hot-float full API,
with the legacy contact implementation and pressure SIMD disabled. Subsequent
contact optimization, calibration candidates and the separate air/lid research
adapter are excluded. Return timing, variation and texture strengths are
authored approximations. The comparison establishes no listening preference,
recording parity, realtime budget or Reason host qualification.
