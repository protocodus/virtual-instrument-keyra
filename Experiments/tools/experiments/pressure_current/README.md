# Current pressure observer SIMD evidence

The current fused backend passes the frozen physical/numerical and timing
guards: **21.96–25.05% lower median CPU** against its pressure-OFF baseline.
All 80 core physical snapshot pairs are exact; 32 core and 18 performance
observer comparisons pass numerical limits. Ten register pairs add ten exact
final physical states and twenty numerical comparisons. These bounds do not
prove inaudibility or recording realism.

The prior 12.16% repetition/pedal regression remains archived as historical
negative evidence. Every current timing trial, maximum, miss and weak-band
diagnostic is retained. Every measured callback still misses its deadline.
Fresh supported-native OriginalControl builds now default ON; cached OFF and
scalar/SDK fallbacks remain available. Integration is tracked in the
[summary](../../../Validation/full-pressure-current.json), with
[design and limits](../../../docs/PRESSURE_CURRENT.md).

From the repository root:

```sh
python3 tools/experiments/pressure_current/check.py
```

The standard-library verifier checks identities, source/flag bindings, stored
physical equality metadata, every numerical gate and raw callback timing
arithmetic. It does not calculate new FFTs, decode PCM/state, compile, execute
model code or repeat measurements. The old historical timing rows are retained
for context; their earlier documentation/dependency graph is not replayed.

JSON is losslessly gzip-compressed with timestamp zero. `index.json` maps
historical paths and decoded SHA256 identities onto this checkout. Immutable
source is preserved verbatim, with `.gitattributes` disabling source whitespace
checks. Prior archive content is reused by hash. Raw audio, pressure,
physical-state binaries, executables and large compiler reports remain external
identities.

Native tests (3), sanitizer tests (2), Reason mock/contract tests (12) and seven
build-policy configurations pass. The actual CMake CLI also reproduces the same
ten qualified ON register outputs; layout-aware native comparison is retained
alongside interleaved payload and planar reference hashes. These are separate
encodings, not falsely identical digest strings. Actual SDK/Recon is untested.

Archived runners retain absolute paths and once-only guards; they are review
sources rather than portable launchers. A separate declared reproduction must
map those paths, restore bound inputs, preserve flags/recipes and use a new
output directory. Publication reruns no experiment and changes no runtime code.
