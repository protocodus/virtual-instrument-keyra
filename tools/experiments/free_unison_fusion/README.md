# Free oscillator / unison fusion evidence

**Scalar `v1` is rejected; guarded SIMD `v2` passes the same native policy.**
The tested float64 pressure, float32 audio and common state checkpoints remain
exact. The guarded native optimization is integrated, with original scheduling
for scalar/SDK, unsupported, opt-out and profile 1 builds. The model remains
slower than realtime and actual Reason SDK/Recon is untested.

`v1` regresses median CPU by 18–31%. `v2` reduces it by 7.04–11.66% across all six
48/96 kHz case groups, and every median p95 improves. The predeclared policy
requires at least 5% lower CPU in every group and at most 5% p95 regression.
All trials, including outliers, remain present. Every measured callback misses
its wall deadline.

Each study first checks four rates and four current full-API fixtures:
574,704 frames per arm, 112 paired files and 80 paired deep snapshots. All
17,778 modes and 6,168 unison rows are inventoried. These are authored simulation
fixtures, not recording comparisons or new realism evidence. See the
[design, results and limits](../../../docs/FREE_UNISON_FUSION.md) and
[validation summary](../../../Validation/full-free-unison-fusion.json).

From the repository root:

```sh
python3 tools/experiments/free_unison_fusion/check.py
```

The standard-library checker verifies archived identities, source/control
bindings, stored exactness metadata, all raw callback lists and the unchanged
policy arithmetic. It does not run model code, decode omitted PCM/state,
rebuild binaries or repeat timings. Source-only manufactured fixtures and
compiler vectorization receipts are distinct from actual model validation.

JSON is losslessly gzip-compressed with timestamp zero. `index.json` maps
historical absolute paths and decoded hashes onto this checkout; repeated
sources and earlier immutable archive artifacts are reused by hash. Source
remains verbatim. Preparation history retains the unrun freezes and subsequent
source-only refinements. Audio, pressure/deep-state binary captures, compiled
binaries/objects and large compiler reports remain external identities.

Separate integration receipts retain native tests (3), sanitizer tests (2),
Reason mock/contract tests (12), generator/source equivalence and four build
policy configurations. The final four-newline cleanup is linked to the original
tested source through token identity and seven unchanged executable hashes;
the original test freezes are not rewritten and sanitizer tests were not rerun.

The frozen runners retain original absolute paths and once-only authorization
guards. They are review sources, not portable launchers. A separate declared
reproduction must map those paths, restore bound inputs, retain source/flags,
use the original event and timing recipes, and preserve its own new output
directory. The archive is assembled without rerunning an experiment. Existing
source ownership and provenance remain unchanged.
